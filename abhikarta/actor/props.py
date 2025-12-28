"""
Props Module - Actor configuration and factory

Props (properties) encapsulates the configuration needed to create
an actor. It provides immutable actor configuration that can be
safely shared and used to create multiple actor instances.

Acknowledgement:
This implementation is inspired by Apache Pekko (incubating).

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha - ajsinha@gmail.com

Version: 1.2.3
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, Tuple
import copy
import logging

from .actor import Actor
from .mailbox import MailboxConfig
from .dispatcher import DispatcherConfig
from .supervision import SupervisorStrategy, OneForOneStrategy

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Props:
    """
    Immutable configuration for actor creation.
    
    Props encapsulates:
    - Actor class to instantiate
    - Constructor arguments
    - Dispatcher configuration
    - Mailbox configuration
    - Supervision strategy
    
    Props is immutable to ensure thread safety when creating
    actors from multiple threads.
    
    Example:
        # Simple props
        props = Props(MyActor)
        
        # Props with arguments
        props = Props(MyActor, args=("arg1", "arg2"), kwargs={"key": "value"})
        
        # Props with custom dispatcher
        props = Props(
            MyActor,
            dispatcher_config=DispatcherConfig(dispatcher_type="pinned")
        )
    """
    
    actor_class: Type[Actor]
    args: Tuple[Any, ...] = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    dispatcher_config: Optional[DispatcherConfig] = None
    mailbox_config: Optional[MailboxConfig] = None
    supervisor_strategy: Optional[SupervisorStrategy] = None
    deploy_config: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate configuration."""
        if not issubclass(self.actor_class, Actor):
            raise TypeError(f"{self.actor_class} must be a subclass of Actor")
    
    def create_actor(self) -> Actor:
        """
        Create a new actor instance.
        
        Returns:
            New actor instance
        """
        return self.actor_class(*self.args, **self.kwargs)
    
    def with_dispatcher(self, config: DispatcherConfig) -> 'Props':
        """
        Create new Props with different dispatcher.
        
        Args:
            config: New dispatcher configuration
            
        Returns:
            New Props instance
        """
        return Props(
            actor_class=self.actor_class,
            args=self.args,
            kwargs=dict(self.kwargs),
            dispatcher_config=config,
            mailbox_config=self.mailbox_config,
            supervisor_strategy=self.supervisor_strategy,
            deploy_config=self.deploy_config
        )
    
    def with_mailbox(self, config: MailboxConfig) -> 'Props':
        """
        Create new Props with different mailbox.
        
        Args:
            config: New mailbox configuration
            
        Returns:
            New Props instance
        """
        return Props(
            actor_class=self.actor_class,
            args=self.args,
            kwargs=dict(self.kwargs),
            dispatcher_config=self.dispatcher_config,
            mailbox_config=config,
            supervisor_strategy=self.supervisor_strategy,
            deploy_config=self.deploy_config
        )
    
    def with_supervisor(self, strategy: SupervisorStrategy) -> 'Props':
        """
        Create new Props with different supervisor strategy.
        
        Args:
            strategy: New supervision strategy
            
        Returns:
            New Props instance
        """
        return Props(
            actor_class=self.actor_class,
            args=self.args,
            kwargs=dict(self.kwargs),
            dispatcher_config=self.dispatcher_config,
            mailbox_config=self.mailbox_config,
            supervisor_strategy=strategy,
            deploy_config=self.deploy_config
        )
    
    def with_deploy(self, config: Dict[str, Any]) -> 'Props':
        """
        Create new Props with deployment configuration.
        
        Args:
            config: Deployment configuration
            
        Returns:
            New Props instance
        """
        return Props(
            actor_class=self.actor_class,
            args=self.args,
            kwargs=dict(self.kwargs),
            dispatcher_config=self.dispatcher_config,
            mailbox_config=self.mailbox_config,
            supervisor_strategy=self.supervisor_strategy,
            deploy_config=config
        )
    
    @staticmethod
    def create(actor_class: Type[Actor], *args, **kwargs) -> 'Props':
        """
        Convenience factory method.
        
        Args:
            actor_class: Actor class to instantiate
            *args: Constructor arguments
            **kwargs: Constructor keyword arguments
            
        Returns:
            New Props instance
        """
        return Props(actor_class=actor_class, args=args, kwargs=kwargs)


class PropsBuilder:
    """
    Fluent builder for Props.
    
    Provides a chainable API for building Props configuration.
    
    Example:
        props = (PropsBuilder(MyActor)
            .with_args("arg1", "arg2")
            .with_kwargs(key="value")
            .with_pinned_dispatcher()
            .with_bounded_mailbox(1000)
            .build())
    """
    
    def __init__(self, actor_class: Type[Actor]):
        self._actor_class = actor_class
        self._args: List[Any] = []
        self._kwargs: Dict[str, Any] = {}
        self._dispatcher_config: Optional[DispatcherConfig] = None
        self._mailbox_config: Optional[MailboxConfig] = None
        self._supervisor_strategy: Optional[SupervisorStrategy] = None
        self._deploy_config: Optional[Dict[str, Any]] = None
    
    def with_args(self, *args) -> 'PropsBuilder':
        """Add constructor arguments."""
        self._args.extend(args)
        return self
    
    def with_kwargs(self, **kwargs) -> 'PropsBuilder':
        """Add constructor keyword arguments."""
        self._kwargs.update(kwargs)
        return self
    
    def with_dispatcher(self, config: DispatcherConfig) -> 'PropsBuilder':
        """Set dispatcher configuration."""
        self._dispatcher_config = config
        return self
    
    def with_default_dispatcher(self, pool_size: Optional[int] = None) -> 'PropsBuilder':
        """Use default dispatcher with optional pool size."""
        self._dispatcher_config = DispatcherConfig(
            dispatcher_type="default",
            thread_pool_size=pool_size or 0
        )
        return self
    
    def with_pinned_dispatcher(self) -> 'PropsBuilder':
        """Use pinned (dedicated thread) dispatcher."""
        self._dispatcher_config = DispatcherConfig(dispatcher_type="pinned")
        return self
    
    def with_fork_join_dispatcher(self, parallelism: Optional[int] = None) -> 'PropsBuilder':
        """Use fork-join dispatcher."""
        self._dispatcher_config = DispatcherConfig(
            dispatcher_type="fork-join",
            thread_pool_size=parallelism or 0
        )
        return self
    
    def with_mailbox(self, config: MailboxConfig) -> 'PropsBuilder':
        """Set mailbox configuration."""
        self._mailbox_config = config
        return self
    
    def with_unbounded_mailbox(self) -> 'PropsBuilder':
        """Use unbounded mailbox."""
        self._mailbox_config = MailboxConfig(mailbox_type="unbounded")
        return self
    
    def with_bounded_mailbox(self, capacity: int, 
                            timeout: Optional[float] = None) -> 'PropsBuilder':
        """Use bounded mailbox with capacity."""
        self._mailbox_config = MailboxConfig(
            mailbox_type="bounded",
            capacity=capacity,
            push_timeout=timeout
        )
        return self
    
    def with_priority_mailbox(self) -> 'PropsBuilder':
        """Use priority mailbox."""
        self._mailbox_config = MailboxConfig(mailbox_type="priority")
        return self
    
    def with_supervisor(self, strategy: SupervisorStrategy) -> 'PropsBuilder':
        """Set supervision strategy."""
        self._supervisor_strategy = strategy
        return self
    
    def with_one_for_one_supervision(self, max_restarts: int = 10,
                                     within_time: float = 60.0) -> 'PropsBuilder':
        """Use one-for-one supervision."""
        self._supervisor_strategy = OneForOneStrategy(
            max_restarts=max_restarts,
            within_time=within_time
        )
        return self
    
    def with_deploy(self, config: Dict[str, Any]) -> 'PropsBuilder':
        """Set deployment configuration."""
        self._deploy_config = config
        return self
    
    def build(self) -> Props:
        """Build the Props instance."""
        return Props(
            actor_class=self._actor_class,
            args=tuple(self._args),
            kwargs=self._kwargs,
            dispatcher_config=self._dispatcher_config,
            mailbox_config=self._mailbox_config,
            supervisor_strategy=self._supervisor_strategy,
            deploy_config=self._deploy_config
        )


# ============================================
# COMMON PROPS FACTORIES
# ============================================

class CommonProps:
    """Factory methods for common Props configurations."""
    
    @staticmethod
    def simple(actor_class: Type[Actor], *args, **kwargs) -> Props:
        """Create simple Props with default configuration."""
        return Props.create(actor_class, *args, **kwargs)
    
    @staticmethod
    def io_bound(actor_class: Type[Actor], *args, **kwargs) -> Props:
        """
        Create Props for I/O-bound actors.
        
        Uses pinned dispatcher for blocking I/O operations.
        """
        return (PropsBuilder(actor_class)
                .with_args(*args)
                .with_kwargs(**kwargs)
                .with_pinned_dispatcher()
                .build())
    
    @staticmethod
    def cpu_bound(actor_class: Type[Actor], *args, 
                  parallelism: Optional[int] = None, **kwargs) -> Props:
        """
        Create Props for CPU-bound actors.
        
        Uses fork-join dispatcher for compute-intensive operations.
        """
        return (PropsBuilder(actor_class)
                .with_args(*args)
                .with_kwargs(**kwargs)
                .with_fork_join_dispatcher(parallelism)
                .build())
    
    @staticmethod
    def high_priority(actor_class: Type[Actor], *args, **kwargs) -> Props:
        """
        Create Props for high-priority actors.
        
        Uses priority mailbox to ensure important messages processed first.
        """
        return (PropsBuilder(actor_class)
                .with_args(*args)
                .with_kwargs(**kwargs)
                .with_priority_mailbox()
                .build())
    
    @staticmethod
    def rate_limited(actor_class: Type[Actor], capacity: int,
                    *args, **kwargs) -> Props:
        """
        Create Props for rate-limited actors.
        
        Uses bounded mailbox for backpressure.
        """
        return (PropsBuilder(actor_class)
                .with_args(*args)
                .with_kwargs(**kwargs)
                .with_bounded_mailbox(capacity)
                .build())
