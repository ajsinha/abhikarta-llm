"""
ActorSystem Module - Main entry point for the actor runtime

The ActorSystem is the container for actors and manages their lifecycle,
dispatchers, mailboxes, and supervision hierarchies.

Key Responsibilities:
- Actor creation and lookup
- Dispatcher management
- Dead letter handling
- System-wide configuration
- Graceful shutdown

Acknowledgement:
This implementation is inspired by Apache Pekko (incubating).

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

Version: 1.2.3
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Set
from concurrent.futures import Future, ThreadPoolExecutor
import threading
import time
import uuid
import logging
import atexit
import weakref

from .actor import (
    Actor, ActorRef, ActorContext, ActorLifecycle,
    Envelope, PoisonPill, Kill, Terminated, DeadLetter,
    Identify, ActorIdentity, ReceiveTimeout
)
from .mailbox import Mailbox, MailboxFactory, MailboxConfig, DeadLetterMailbox
from .dispatcher import Dispatcher, DispatcherFactory, DispatcherConfig
from .supervision import SupervisorStrategy, OneForOneStrategy, Directive, ChildFailure
from .props import Props
from .scheduler import Scheduler

logger = logging.getLogger(__name__)


@dataclass
class ActorSystemConfig:
    """Configuration for the ActorSystem."""
    name: str = "abhikarta-actors"
    default_dispatcher: DispatcherConfig = field(default_factory=DispatcherConfig)
    default_mailbox: MailboxConfig = field(default_factory=MailboxConfig)
    dead_letter_capacity: int = 10000
    ask_timeout: float = 5.0
    shutdown_timeout: float = 30.0
    log_dead_letters: bool = True
    log_dead_letters_during_shutdown: bool = False


class ActorCell:
    """
    Internal container for an actor and its runtime state.
    
    ActorCell manages the actor's mailbox processing, supervision,
    and lifecycle events.
    """
    
    def __init__(self, 
                 actor: Actor,
                 props: Props,
                 ref: ActorRef,
                 context: ActorContext,
                 mailbox: Mailbox,
                 dispatcher: Dispatcher,
                 system: 'ActorSystem'):
        self.actor = actor
        self.props = props
        self.ref = ref
        self.context = context
        self.mailbox = mailbox
        self.dispatcher = dispatcher
        self.system = system
        self.lifecycle = ActorLifecycle.CREATED
        self.processing = threading.Event()
        self._lock = threading.Lock()
        self._current_message: Optional[Any] = None
        self._watchers: Set[ActorRef] = set()
    
    def start(self) -> None:
        """Start the actor."""
        with self._lock:
            if self.lifecycle != ActorLifecycle.CREATED:
                return
            self.lifecycle = ActorLifecycle.STARTING
        
        try:
            self.actor.pre_start()
            with self._lock:
                self.lifecycle = ActorLifecycle.RUNNING
            self._schedule_mailbox_processing()
            logger.debug(f"Actor started: {self.ref.path}")
        except Exception as e:
            logger.error(f"Error in pre_start for {self.ref.path}: {e}")
            self._handle_failure(e, None)
    
    def stop(self) -> None:
        """Stop the actor."""
        with self._lock:
            if self.lifecycle in (ActorLifecycle.STOPPING, ActorLifecycle.STOPPED):
                return
            self.lifecycle = ActorLifecycle.STOPPING
        
        # Stop children first
        for child_ref in list(self.context.children.values()):
            self.system._stop_actor(child_ref)
        
        # Clear mailbox
        remaining = self.mailbox.clear()
        if remaining:
            logger.debug(f"Discarded {len(remaining)} messages from {self.ref.path}")
        
        try:
            self.actor.post_stop()
        except Exception as e:
            logger.error(f"Error in post_stop for {self.ref.path}: {e}")
        
        with self._lock:
            self.lifecycle = ActorLifecycle.STOPPED
        
        # Notify watchers
        for watcher in self._watchers:
            watcher.tell(Terminated(self.ref))
        
        self.mailbox.close()
        logger.debug(f"Actor stopped: {self.ref.path}")
    
    def restart(self, reason: Exception) -> None:
        """Restart the actor."""
        with self._lock:
            if self.lifecycle == ActorLifecycle.STOPPED:
                return
            self.lifecycle = ActorLifecycle.RESTARTING
        
        try:
            self.actor.pre_restart(reason, self._current_message)
        except Exception as e:
            logger.error(f"Error in pre_restart: {e}")
        
        # Create new actor instance
        new_actor = self.props.create_actor()
        new_actor._set_context(self.context)
        self.actor = new_actor
        self.context._actor = new_actor
        
        try:
            self.actor.post_restart(reason)
        except Exception as e:
            logger.error(f"Error in post_restart: {e}")
            self._handle_failure(e, None)
            return
        
        with self._lock:
            self.lifecycle = ActorLifecycle.RUNNING
        
        logger.debug(f"Actor restarted: {self.ref.path}")
    
    def _schedule_mailbox_processing(self) -> None:
        """Schedule mailbox processing on dispatcher."""
        if self.lifecycle not in (ActorLifecycle.RUNNING, ActorLifecycle.STARTING):
            return
        
        if self.mailbox.is_empty():
            return
        
        if self.processing.is_set():
            return
        
        self.processing.set()
        self.dispatcher.execute(self._process_mailbox)
    
    def _process_mailbox(self) -> None:
        """Process messages from mailbox."""
        try:
            messages_processed = 0
            max_messages = 5  # Throughput limit per dispatch
            
            while messages_processed < max_messages:
                if self.lifecycle != ActorLifecycle.RUNNING:
                    break
                
                envelope = self.mailbox.dequeue(timeout=0.001)
                if envelope is None:
                    break
                
                self._current_message = envelope.message
                
                try:
                    # Handle system messages
                    if isinstance(envelope.message, PoisonPill):
                        self.stop()
                        return
                    elif isinstance(envelope.message, Kill):
                        self.stop()
                        return
                    elif isinstance(envelope.message, Identify):
                        if envelope.sender:
                            envelope.sender.tell(
                                ActorIdentity(self.ref, envelope.message.message_id)
                            )
                    else:
                        # Regular message processing
                        self.actor._process_message(envelope)
                
                except Exception as e:
                    self._handle_failure(e, envelope.message)
                
                finally:
                    self._current_message = None
                
                messages_processed += 1
        
        finally:
            self.processing.clear()
            
            # Reschedule if more messages
            if not self.mailbox.is_empty() and self.lifecycle == ActorLifecycle.RUNNING:
                self._schedule_mailbox_processing()
    
    def _handle_failure(self, exception: Exception, message: Any) -> None:
        """Handle actor failure with supervision."""
        logger.error(f"Actor failure in {self.ref.path}: {exception}")
        
        # Get supervision strategy
        strategy = self.props.supervisor_strategy
        if strategy is None:
            strategy = OneForOneStrategy()
        
        failure = ChildFailure(self.ref, exception, message)
        directive = strategy.handle_failure(failure)
        
        if directive == Directive.RESUME:
            pass  # Continue processing
        elif directive == Directive.RESTART:
            self.restart(exception)
        elif directive == Directive.STOP:
            self.stop()
        elif directive == Directive.ESCALATE:
            if self.context.parent:
                self.context.parent.tell(failure)
            else:
                self.stop()
    
    def add_watcher(self, watcher: ActorRef) -> None:
        """Add a watcher for termination notifications."""
        with self._lock:
            self._watchers.add(watcher)
            if self.lifecycle == ActorLifecycle.STOPPED:
                watcher.tell(Terminated(self.ref))
    
    def remove_watcher(self, watcher: ActorRef) -> None:
        """Remove a watcher."""
        with self._lock:
            self._watchers.discard(watcher)


class ActorSystem:
    """
    The ActorSystem is the entry point for creating and managing actors.
    
    It provides:
    - Actor creation via actor_of()
    - Actor lookup via actor_selection()
    - System-wide configuration
    - Dispatcher management
    - Dead letter handling
    - Graceful shutdown
    
    Example:
        # Create system
        system = ActorSystem("my-system")
        
        # Create actors
        greeter = system.actor_of(Props(GreeterActor), "greeter")
        
        # Send messages
        greeter.tell("Hello!")
        
        # Shutdown
        system.terminate()
    """
    
    _instances: Dict[str, 'ActorSystem'] = {}
    _lock = threading.Lock()
    
    def __init__(self, config: Optional[ActorSystemConfig] = None):
        """
        Create a new ActorSystem.
        
        Args:
            config: Optional system configuration
        """
        self._config = config or ActorSystemConfig()
        self._name = self._config.name
        
        # Register instance
        with ActorSystem._lock:
            if self._name in ActorSystem._instances:
                raise ValueError(f"ActorSystem '{self._name}' already exists")
            ActorSystem._instances[self._name] = self
        
        # Core components
        self._actors: Dict[str, ActorCell] = {}
        self._actors_lock = threading.RLock()
        self._terminated = threading.Event()
        
        # Dispatchers
        self._default_dispatcher = DispatcherFactory.create(self._config.default_dispatcher)
        self._dispatchers: Dict[str, Dispatcher] = {
            "default": self._default_dispatcher
        }
        
        # Dead letters
        self._dead_letters = DeadLetterMailbox(self._config.dead_letter_capacity)
        self._dead_letter_listeners: List[Callable[[DeadLetter], None]] = []
        
        # Scheduler
        self._scheduler = Scheduler()
        self._scheduler.start()
        
        # Ask pattern support
        self._ask_counter = 0
        self._ask_lock = threading.Lock()
        self._pending_asks: Dict[str, Future] = {}
        
        # Register shutdown hook
        atexit.register(self._shutdown_hook)
        
        logger.info(f"ActorSystem '{self._name}' started")
    
    @property
    def name(self) -> str:
        """System name."""
        return self._name
    
    @property
    def scheduler(self) -> Scheduler:
        """System scheduler."""
        return self._scheduler
    
    @property
    def is_terminated(self) -> bool:
        """Check if system is terminated."""
        return self._terminated.is_set()
    
    def actor_of(self, props: Props, name: Optional[str] = None) -> ActorRef:
        """
        Create a top-level actor.
        
        Args:
            props: Actor properties
            name: Optional actor name
            
        Returns:
            ActorRef to the new actor
        """
        if self._terminated.is_set():
            raise RuntimeError("ActorSystem is terminated")
        
        if name is None:
            name = f"actor-{uuid.uuid4().hex[:8]}"
        
        path = f"/{self._name}/user/{name}"
        return self._create_actor(props, path, None)
    
    def _create_actor(self, props: Props, path: str, 
                     parent: Optional[ActorRef]) -> ActorRef:
        """Internal: Create an actor at the given path."""
        with self._actors_lock:
            if path in self._actors:
                raise ValueError(f"Actor already exists at {path}")
            
            # Create mailbox
            mailbox_config = props.mailbox_config or self._config.default_mailbox
            mailbox = MailboxFactory.create(mailbox_config)
            
            # Get dispatcher
            dispatcher = self._get_dispatcher(props.dispatcher_config)
            
            # Create actor instance
            actor = props.create_actor()
            
            # Create reference and context
            uid = str(uuid.uuid4())
            ref = ActorRef(path, uid, self, mailbox)
            context = ActorContext(actor, ref, self, parent)
            actor._set_context(context)
            
            # Create cell
            cell = ActorCell(actor, props, ref, context, mailbox, dispatcher, self)
            self._actors[path] = cell
            
            # Start the actor
            cell.start()
            
            return ref
    
    def _get_dispatcher(self, config: Optional[DispatcherConfig]) -> Dispatcher:
        """Get or create a dispatcher."""
        if config is None:
            return self._default_dispatcher
        
        # For simplicity, create new dispatcher
        # In production, would cache based on config
        return DispatcherFactory.create(config)
    
    def _stop_actor(self, ref: ActorRef) -> None:
        """Internal: Stop an actor."""
        with self._actors_lock:
            cell = self._actors.get(ref.path)
            if cell:
                cell.stop()
                del self._actors[ref.path]
    
    def _register_watcher(self, watched: ActorRef, watcher: ActorRef) -> None:
        """Register death watch."""
        with self._actors_lock:
            cell = self._actors.get(watched.path)
            if cell:
                cell.add_watcher(watcher)
            else:
                # Actor already dead
                watcher.tell(Terminated(watched, existence_confirmed=False))
    
    def _unregister_watcher(self, watched: ActorRef, watcher: ActorRef) -> None:
        """Unregister death watch."""
        with self._actors_lock:
            cell = self._actors.get(watched.path)
            if cell:
                cell.remove_watcher(watcher)
    
    def _publish_dead_letter(self, dead_letter: DeadLetter) -> None:
        """Handle undeliverable message."""
        if self._config.log_dead_letters:
            if not self._terminated.is_set() or self._config.log_dead_letters_during_shutdown:
                logger.warning(
                    f"Dead letter: {type(dead_letter.message).__name__} "
                    f"from {dead_letter.sender} to {dead_letter.recipient}"
                )
        
        self._dead_letters.enqueue(Envelope(dead_letter))
        
        for listener in self._dead_letter_listeners:
            try:
                listener(dead_letter)
            except Exception as e:
                logger.error(f"Dead letter listener error: {e}")
    
    def subscribe_dead_letters(self, listener: Callable[[DeadLetter], None]) -> None:
        """Subscribe to dead letter notifications."""
        self._dead_letter_listeners.append(listener)
    
    def _ask(self, target: ActorRef, message: Any, timeout: float) -> Future:
        """Internal: Implement ask pattern."""
        future: Future = Future()
        
        with self._ask_lock:
            self._ask_counter += 1
            ask_id = f"ask-{self._ask_counter}"
            self._pending_asks[ask_id] = future
        
        # Create temporary actor for response
        class AskActor(Actor):
            def __init__(self, ask_id: str, future: Future, system: ActorSystem):
                super().__init__()
                self._ask_id = ask_id
                self._future = future
                self._system = system
            
            def receive(self, message):
                if not self._future.done():
                    self._future.set_result(message)
                self.context.stop(self.self)
                with self._system._ask_lock:
                    self._system._pending_asks.pop(self._ask_id, None)
        
        ask_actor_ref = self.actor_of(
            Props(AskActor, args=(ask_id, future, self)),
            f"ask-{ask_id}"
        )
        
        # Send message with ask actor as sender
        target.tell(message, ask_actor_ref)
        
        # Schedule timeout
        def timeout_handler():
            if not future.done():
                future.set_exception(TimeoutError(f"Ask timed out after {timeout}s"))
                with self._ask_lock:
                    self._pending_asks.pop(ask_id, None)
        
        self._scheduler.schedule_once(timeout, ask_actor_ref, PoisonPill())
        
        return future
    
    def actor_selection(self, path: str) -> Optional[ActorRef]:
        """
        Look up an actor by path.
        
        Args:
            path: Actor path
            
        Returns:
            ActorRef if found, None otherwise
        """
        with self._actors_lock:
            cell = self._actors.get(path)
            return cell.ref if cell else None
    
    def terminate(self) -> None:
        """
        Terminate the actor system gracefully.
        
        Stops all actors and shuts down dispatchers.
        """
        if self._terminated.is_set():
            return
        
        logger.info(f"Terminating ActorSystem '{self._name}'...")
        self._terminated.set()
        
        # Stop all actors
        with self._actors_lock:
            for cell in list(self._actors.values()):
                try:
                    cell.stop()
                except Exception as e:
                    logger.error(f"Error stopping actor: {e}")
            self._actors.clear()
        
        # Stop scheduler
        self._scheduler.stop()
        
        # Shutdown dispatchers
        self._default_dispatcher.shutdown(wait=True)
        for dispatcher in self._dispatchers.values():
            if dispatcher != self._default_dispatcher:
                dispatcher.shutdown(wait=True)
        
        # Unregister
        with ActorSystem._lock:
            ActorSystem._instances.pop(self._name, None)
        
        logger.info(f"ActorSystem '{self._name}' terminated")
    
    def _shutdown_hook(self) -> None:
        """Atexit hook for graceful shutdown."""
        if not self._terminated.is_set():
            self.terminate()
    
    def get_actor_count(self) -> int:
        """Get number of active actors."""
        with self._actors_lock:
            return len(self._actors)
    
    def get_dead_letter_count(self) -> int:
        """Get number of dead letters."""
        return self._dead_letters.size()
    
    @classmethod
    def get(cls, name: str) -> Optional['ActorSystem']:
        """Get an existing ActorSystem by name."""
        with cls._lock:
            return cls._instances.get(name)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - terminate system."""
        self.terminate()
        return False


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def create_actor_system(name: str = "abhikarta", 
                       **config_kwargs) -> ActorSystem:
    """
    Create a new ActorSystem with optional configuration.
    
    Args:
        name: System name
        **config_kwargs: Additional configuration options
        
    Returns:
        New ActorSystem instance
    """
    config = ActorSystemConfig(name=name, **config_kwargs)
    return ActorSystem(config)


def get_actor_system(name: str = "abhikarta") -> Optional[ActorSystem]:
    """Get an existing ActorSystem by name."""
    return ActorSystem.get(name)
