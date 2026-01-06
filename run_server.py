#!/usr/bin/env python3
"""
Abhikarta-LLM - Application Entry Point (run_server.py)

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Patent Pending: Certain architectural patterns and implementations described in this
software may be subject to patent applications.

Usage:
    python run_server.py [--server.port=PORT] [--app.debug=true]
    
    Command line arguments use --key=value format and override properties files.
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add new module paths for src/ layout packages
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'abhikarta-main', 'src'))      # Main abhikarta module
sys.path.insert(0, os.path.join(project_root, 'abhikarta-web', 'src'))       # Web UI module
sys.path.insert(0, os.path.join(project_root, 'abhikarta-sdk-client', 'src'))    # SDK Client
sys.path.insert(0, os.path.join(project_root, 'abhikarta-sdk-embedded', 'src'))  # SDK Embedded


def prepare_prop_conf():
    """
    Initialize the PropertiesConfigurator with property files.
    
    Returns:
        PropertiesConfigurator instance
    """
    from abhikarta.core.config import PropertiesConfigurator
    
    prop_files = [
        'config/application.properties'
    ]
    
    # Filter to only existing files
    existing_files = [f for f in prop_files if os.path.exists(f)]
    
    prop_conf = PropertiesConfigurator(properties_files=existing_files)
    return prop_conf


def setup_logging(prop_conf):
    """
    Setup logging based on properties configuration.
    
    Args:
        prop_conf: PropertiesConfigurator instance
    """
    log_level = prop_conf.get('logging.level', 'INFO')
    log_format = prop_conf.get(
        'logging.format', 
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    log_file = prop_conf.get('logging.file', './logs/abhikarta.log')
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        handlers=handlers
    )
    
    # Reduce noise from third-party loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def setup_prometheus_metrics(prop_conf):
    """
    Initialize Prometheus metrics.
    
    Args:
        prop_conf: PropertiesConfigurator instance
    """
    logger = logging.getLogger(__name__)
    
    # Check if Prometheus is enabled
    if not prop_conf.get_bool('monitoring.prometheus.enabled', True):
        logger.info("Prometheus metrics disabled in configuration")
        return
    
    try:
        from abhikarta.monitoring import (
            init_app_info,
            set_start_time,
            PROMETHEUS_AVAILABLE,
        )
        
        if PROMETHEUS_AVAILABLE:
            # Initialize application info
            environment = prop_conf.get('app.environment', 'production')
            init_app_info(version='1.5.2', environment=environment)
            
            # Set system start time
            set_start_time()
            
            logger.info("Prometheus metrics initialized successfully")
            logger.info(f"Metrics endpoint: {prop_conf.get('monitoring.metrics.path', '/metrics')}")
        else:
            logger.warning("prometheus_client not installed - metrics will be disabled")
    except ImportError as e:
        logger.warning(f"Could not initialize Prometheus metrics: {e}")


def prepare_database(prop_conf):
    """
    Initialize database facade based on configuration.
    
    Args:
        prop_conf: PropertiesConfigurator instance
        
    Returns:
        DatabaseFacade instance
    """
    from abhikarta.database import DatabaseFacade
    from abhikarta.config import Settings
    
    # Create settings from properties
    settings = Settings()
    settings.database.type = prop_conf.get('database.type', 'sqlite')
    settings.database.sqlite_path = prop_conf.get('database.sqlite.path', './data/abhikarta.db')
    settings.database.pg_host = prop_conf.get('database.postgresql.host', 'localhost')
    settings.database.pg_port = prop_conf.get_int('database.postgresql.port', 5432)
    settings.database.pg_database = prop_conf.get('database.postgresql.database', 'abhikarta')
    settings.database.pg_user = prop_conf.get('database.postgresql.user', 'abhikarta_user')
    settings.database.pg_password = prop_conf.get('database.postgresql.password', '')
    
    # Create and initialize database facade
    db_facade = DatabaseFacade(settings)
    db_facade.connect()
    db_facade.init_schema()
    
    return db_facade


def prepare_execution_logger(prop_conf):
    """
    Initialize the execution logger for detailed execution tracing.
    
    Args:
        prop_conf: PropertiesConfigurator instance
        
    Returns:
        ExecutionLogger instance
    """
    from abhikarta.services.execution_logger import init_execution_logger_from_properties
    
    logger = logging.getLogger(__name__)
    
    try:
        exec_logger = init_execution_logger_from_properties(prop_conf)
        
        enabled = prop_conf.get('execution.log.enabled', 'true').lower() == 'true'
        log_path = prop_conf.get('execution.log.path', 'executionlog')
        
        if enabled:
            logger.info(f"Execution logger initialized: path={log_path}")
        else:
            logger.info("Execution logging disabled")
        
        return exec_logger
    except Exception as e:
        logger.warning(f"Failed to initialize execution logger: {e}")
        return None


def start_execution_log_cleanup_scheduler(prop_conf, db_facade):
    """
    Start a background thread for periodic execution log cleanup.
    
    Args:
        prop_conf: PropertiesConfigurator instance
        db_facade: Database facade for DB log cleanup
    """
    import threading
    import time
    
    logger = logging.getLogger(__name__)
    
    try:
        from abhikarta.services.execution_logger import get_execution_logger
        
        exec_logger = get_execution_logger()
        if not exec_logger or not exec_logger.config.enabled:
            return
        
        interval_hours = exec_logger.config.cleanup_interval_hours
        interval_seconds = interval_hours * 3600
        
        file_retention = exec_logger.config.file_retention_days
        db_retention = exec_logger.config.db_retention_days
        
        def cleanup_task():
            """Periodic cleanup task."""
            logger.info(f"Execution log cleanup scheduler started (interval: {interval_hours}h)")
            
            # Run initial cleanup on startup
            time.sleep(60)  # Wait 1 minute after startup
            
            while True:
                try:
                    exec_logger.cleanup_old_logs(db_facade)
                    logger.debug(f"Execution log cleanup completed")
                except Exception as e:
                    logger.error(f"Error during execution log cleanup: {e}")
                
                time.sleep(interval_seconds)
        
        # Start background thread
        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True, name="exec-log-cleanup")
        cleanup_thread.start()
        
        logger.info(f"Execution log cleanup scheduler started: "
                   f"file retention={file_retention}d, db retention={db_retention}d, "
                   f"interval={interval_hours}h")
        
    except Exception as e:
        logger.warning(f"Failed to start execution log cleanup scheduler: {e}")


def prepare_user_facade(prop_conf):
    """
    Initialize user management facade.
    
    Args:
        prop_conf: PropertiesConfigurator instance
        
    Returns:
        UserFacade instance
    """
    from abhikarta.user_management import UserFacade
    
    users_file = prop_conf.get('users.file', './data/users.json')
    user_facade = UserFacade(users_file)
    
    return user_facade


def prepare_tools_registry(prop_conf, db_facade):
    """
    Initialize the tools registry with pre-built tools.
    
    Args:
        prop_conf: PropertiesConfigurator instance
        db_facade: DatabaseFacade instance
        
    Returns:
        ToolsRegistry instance
    """
    from abhikarta.tools import get_tools_registry
    from abhikarta.tools.prebuilt import register_all_prebuilt_tools
    
    logger = logging.getLogger(__name__)
    
    # Get singleton registry
    registry = get_tools_registry()
    registry.set_db_facade(db_facade)
    
    # Register pre-built tools
    prebuilt_count = register_all_prebuilt_tools(registry)
    logger.info(f"Registered {prebuilt_count} pre-built tools")
    
    # Register code fragment tools from database
    code_fragment_count = registry.register_from_code_fragments()
    logger.info(f"Registered {code_fragment_count} code fragment tools")
    
    return registry


def prepare_mcp_manager(prop_conf, db_facade, tools_registry):
    """
    Initialize MCP server manager and connect to configured servers.
    
    Args:
        prop_conf: PropertiesConfigurator instance
        db_facade: DatabaseFacade instance
        tools_registry: ToolsRegistry instance
        
    Returns:
        MCPServerManager instance
    """
    from abhikarta.mcp import get_mcp_manager
    
    logger = logging.getLogger(__name__)
    
    # Get singleton manager
    manager = get_mcp_manager()
    manager.set_db_facade(db_facade)
    manager.set_tools_registry(tools_registry)
    
    # Load servers from database
    server_count = manager.load_from_database()
    logger.info(f"Loaded {server_count} MCP servers from database")
    
    # Connect to auto-connect servers
    connect_results = manager.connect_all()
    connected = sum(1 for v in connect_results.values() if v)
    logger.info(f"Connected to {connected} MCP servers")
    
    # Start health monitor
    health_interval = prop_conf.get_int('mcp.health.interval.seconds', 30)
    manager.start_health_monitor(health_interval)
    logger.info(f"MCP health monitor started (interval: {health_interval}s)")
    
    return manager


def prepare_actor_system(prop_conf):
    """
    Initialize the Actor System for running agents and workflows concurrently.
    
    The Actor System provides:
    - Lightweight actor-based concurrency for millions of agents
    - Message-driven communication between components
    - Supervision hierarchies for fault tolerance
    - Thread-safe execution without locks
    
    Args:
        prop_conf: PropertiesConfigurator instance
        
    Returns:
        ActorSystem instance (also accessible via get_actor_system())
    """
    from abhikarta.actor import (
        ActorSystem,
        ActorSystemConfig,
        OneForOneStrategy,
        Directive,
    )
    from abhikarta.actor.dispatcher import DispatcherConfig
    
    logger = logging.getLogger(__name__)
    
    # Get configuration from properties
    system_name = prop_conf.get('actor.system.name', 'abhikarta-actors')
    default_dispatcher_threads = prop_conf.get_int('actor.dispatcher.default.threads', 8)
    io_dispatcher_threads = prop_conf.get_int('actor.dispatcher.io.threads', 16)
    dead_letter_logging = prop_conf.get_bool('actor.deadletter.logging', True)
    
    # Create dispatcher configuration
    dispatcher_config = DispatcherConfig(
        thread_pool_size=default_dispatcher_threads,
        throughput=5
    )
    
    # Create system configuration
    config = ActorSystemConfig(
        name=system_name,
        default_dispatcher=dispatcher_config,
        log_dead_letters=dead_letter_logging,
    )
    
    # Create the actor system directly with config
    actor_system = ActorSystem(config)
    
    logger.info(f"Actor system '{system_name}' started")
    logger.info(f"  Default dispatcher threads: {default_dispatcher_threads}")
    logger.info(f"  I/O dispatcher threads: {io_dispatcher_threads}")
    logger.info(f"  Dead letter logging: {dead_letter_logging}")
    
    return actor_system


def run_webserver(prop_conf, user_facade, db_facade, tools_registry, mcp_manager):
    """
    Initialize and run the web server.
    
    Args:
        prop_conf: PropertiesConfigurator instance
        user_facade: UserFacade instance
        db_facade: DatabaseFacade instance
        tools_registry: ToolsRegistry instance
        mcp_manager: MCPServerManager instance
    """
    from abhikarta_web import AbhikartaLLMWeb
    
    # Get secret key from properties or generate
    secret_key = prop_conf.get('app.secret.key', os.urandom(24).hex())
    
    # Create web application
    aweb = AbhikartaLLMWeb(secret_key=secret_key)
    
    # Set facades
    aweb.set_user_facade(user_facade)
    aweb.set_db_facade(db_facade)
    
    # Prepare routes
    aweb.prepare_routes()
    
    # Get server configuration
    host = prop_conf.get('server.host', '0.0.0.0')
    port = prop_conf.get_int('server.port', 5000)
    debug = prop_conf.get_bool('app.debug', False)
    
    # Run the application
    aweb.run(host=host, port=port, debug=debug)


def print_banner(prop_conf, tools_count=0, mcp_count=0, actor_system_name=''):
    """Print application startup banner."""
    version = prop_conf.get('app.version', '1.0.0')
    host = prop_conf.get('server.host', '0.0.0.0')
    port = prop_conf.get_int('server.port', 5000)
    db_type = prop_conf.get('database.type', 'sqlite')
    debug = prop_conf.get_bool('app.debug', False)
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║    █████╗ ██████╗ ██╗  ██╗██╗██╗  ██╗ █████╗ ██████╗ ████████╗ █████╗    ║
║   ██╔══██╗██╔══██╗██║  ██║██║██║ ██╔╝██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗   ║
║   ███████║██████╔╝███████║██║█████╔╝ ███████║██████╔╝   ██║   ███████║   ║
║   ██╔══██║██╔══██╗██╔══██║██║██╔═██╗ ██╔══██║██╔══██╗   ██║   ██╔══██║   ║
║   ██║  ██║██████╔╝██║  ██║██║██║  ██╗██║  ██║██║  ██║   ██║   ██║  ██║   ║
║   ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ║
║                                                                           ║
║                    ██╗     ██╗     ███╗   ███╗                            ║
║                    ██║     ██║     ████╗ ████║                            ║
║                    ██║     ██║     ██╔████╔██║                            ║
║                    ██║     ██║     ██║╚██╔╝██║                            ║
║                    ███████╗███████╗██║ ╚═╝ ██║                            ║
║                    ╚══════╝╚══════╝╚═╝     ╚═╝                            ║
║                                                                           ║
║               AI Agent Design & Orchestration Platform                    ║
║                           Version {version}                                  ║
║                                                                           ║
╠═══════════════════════════════════════════════════════════════════════════╣
║   Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.              ║
╚═══════════════════════════════════════════════════════════════════════════╝

  Starting server...
  Host: {host}
  Port: {port}
  Debug: {debug}
  Database: {db_type}
  Actor System: {actor_system_name}
  Tools Loaded: {tools_count}
  MCP Servers: {mcp_count}
  
  Access the application at: http://{host}:{port}
    
  Press Ctrl+C to stop the server.
""")


def print_step(step_num, total_steps, description, status='starting'):
    """Print an eye-catching step indicator."""
    # Colors for terminal
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    # Status indicators
    if status == 'starting':
        icon = f'{YELLOW}⏳{RESET}'
        status_text = f'{YELLOW}STARTING{RESET}'
    elif status == 'done':
        icon = f'{GREEN}✅{RESET}'
        status_text = f'{GREEN}DONE{RESET}'
    elif status == 'error':
        icon = f'\033[91m❌{RESET}'
        status_text = f'\033[91mERROR{RESET}'
    else:
        icon = f'{BLUE}🔄{RESET}'
        status_text = f'{BLUE}RUNNING{RESET}'
    
    # Progress bar
    progress = int((step_num / total_steps) * 20)
    bar = f'{GREEN}{"█" * progress}{RESET}{"░" * (20 - progress)}'
    
    print(f'''
{BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║  {icon} STEP {step_num}/{total_steps}: {description:<50} [{status_text}]
║  [{bar}] {int((step_num/total_steps)*100):3d}%
╚══════════════════════════════════════════════════════════════════════════════╝{RESET}''')


def print_shutdown_step(step_num, total_steps, description, status='stopping'):
    """Print an eye-catching shutdown step indicator."""
    # Colors for terminal
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    # Status indicators
    if status == 'stopping':
        icon = f'{YELLOW}🛑{RESET}'
        status_text = f'{YELLOW}STOPPING{RESET}'
    elif status == 'done':
        icon = f'{GREEN}✅{RESET}'
        status_text = f'{GREEN}STOPPED{RESET}'
    elif status == 'error':
        icon = f'{RED}⚠️{RESET}'
        status_text = f'{RED}WARNING{RESET}'
    else:
        icon = f'{MAGENTA}🔄{RESET}'
        status_text = f'{MAGENTA}RUNNING{RESET}'
    
    # Progress bar (reverse for shutdown)
    remaining = total_steps - step_num + 1
    progress = int((step_num / total_steps) * 20)
    bar = f'{RED}{"█" * progress}{RESET}{"░" * (20 - progress)}'
    
    print(f'''
{BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║  {icon} SHUTDOWN {step_num}/{total_steps}: {description:<46} [{status_text}]
║  [{bar}] {int((step_num/total_steps)*100):3d}%
╚══════════════════════════════════════════════════════════════════════════════╝{RESET}''')


def main():
    """Main entry point for running the Abhikarta-LLM server."""
    logger = logging.getLogger(__name__)
    
    tools_registry = None
    mcp_manager = None
    actor_system = None
    
    TOTAL_STARTUP_STEPS = 9
    
    try:
        # Print startup header
        print('''
\033[96m\033[1m
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     🚀  ABHIKARTA-LLM SERVER INITIALIZATION SEQUENCE STARTING  🚀           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
\033[0m''')
        
        # 1. Initialize properties configuration
        print_step(1, TOTAL_STARTUP_STEPS, "Loading Configuration Properties", 'starting')
        prop_conf = prepare_prop_conf()
        print_step(1, TOTAL_STARTUP_STEPS, "Loading Configuration Properties", 'done')
        
        # 2. Setup logging
        print_step(2, TOTAL_STARTUP_STEPS, "Initializing Logging System", 'starting')
        setup_logging(prop_conf)
        logger.info("Properties configuration initialized")
        print_step(2, TOTAL_STARTUP_STEPS, "Initializing Logging System", 'done')
        
        # 2.5 Initialize Prometheus metrics
        setup_prometheus_metrics(prop_conf)
        
        # 3. Initialize database
        print_step(3, TOTAL_STARTUP_STEPS, f"Connecting to Database ({prop_conf.get('database.type', 'sqlite')})", 'starting')
        db_facade = prepare_database(prop_conf)
        logger.info(f"Database initialized: {prop_conf.get('database.type', 'sqlite')}")
        print_step(3, TOTAL_STARTUP_STEPS, f"Connecting to Database ({prop_conf.get('database.type', 'sqlite')})", 'done')
        
        # 3.5 Initialize execution logger (for detailed execution debugging)
        exec_logger = prepare_execution_logger(prop_conf)
        if exec_logger:
            logger.info(f"Execution logger ready: {exec_logger.config.base_path}")
            # Start background cleanup scheduler
            start_execution_log_cleanup_scheduler(prop_conf, db_facade)
        
        # 3.6 Initialize LLM Config Resolver (for admin defaults)
        try:
            from abhikarta.services.llm_config_resolver import init_llm_config_resolver
            llm_resolver = init_llm_config_resolver(db_facade)
            admin_defaults = llm_resolver.get_admin_defaults()
            logger.info(f"LLM Config Resolver ready: default provider={admin_defaults.get('provider')}, model={admin_defaults.get('model')}")
        except Exception as e:
            logger.warning(f"LLM Config Resolver not initialized: {e}")
        
        # 4. Initialize user facade
        print_step(4, TOTAL_STARTUP_STEPS, "Loading User Management System", 'starting')
        user_facade = prepare_user_facade(prop_conf)
        logger.info("User management initialized")
        print_step(4, TOTAL_STARTUP_STEPS, "Loading User Management System", 'done')
        
        # 5. Initialize tools registry with pre-built tools
        print_step(5, TOTAL_STARTUP_STEPS, "Registering Pre-built Tools", 'starting')
        tools_registry = prepare_tools_registry(prop_conf, db_facade)
        tools_count = len(tools_registry.list_tools())
        logger.info(f"Tools registry initialized with {tools_count} tools")
        print_step(5, TOTAL_STARTUP_STEPS, f"Registered {tools_count} Tools", 'done')
        
        # 6. Initialize MCP manager and connect to servers
        print_step(6, TOTAL_STARTUP_STEPS, "Connecting to MCP Servers", 'starting')
        mcp_manager = prepare_mcp_manager(prop_conf, db_facade, tools_registry)
        mcp_count = len(mcp_manager.list_servers())
        logger.info(f"MCP manager initialized with {mcp_count} servers")
        print_step(6, TOTAL_STARTUP_STEPS, f"Connected to {mcp_count} MCP Servers", 'done')
        
        # 7. Initialize Actor System (BEFORE Flask for concurrent agent/workflow execution)
        print_step(7, TOTAL_STARTUP_STEPS, "Starting Actor System (Pekko-Inspired)", 'starting')
        actor_system = prepare_actor_system(prop_conf)
        actor_system_name = prop_conf.get('actor.system.name', 'abhikarta-actors')
        logger.info(f"Actor system '{actor_system_name}' ready for concurrent execution")
        print_step(7, TOTAL_STARTUP_STEPS, f"Actor System '{actor_system_name}' Ready", 'done')
        
        # 8. Print startup banner
        print_step(8, TOTAL_STARTUP_STEPS, "Loading Template Libraries", 'starting')
        print_step(8, TOTAL_STARTUP_STEPS, "36 Agent + 33 Workflow Templates Loaded", 'done')
        
        # 9. Final step - starting web server
        print_step(9, TOTAL_STARTUP_STEPS, "Starting Flask Web Server", 'starting')
        print_banner(prop_conf, tools_count, mcp_count, actor_system_name)
        print_step(9, TOTAL_STARTUP_STEPS, "Web Server Running", 'done')
        
        # Print success message
        host = prop_conf.get('server.host', '0.0.0.0')
        port = prop_conf.get_int('server.port', 5000)
        print(f'''
\033[92m\033[1m
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ✅  ABHIKARTA-LLM SERVER IS NOW RUNNING!                                 ║
║                                                                              ║
║     🌐  URL: http://{host}:{port:<5}                                          ║
║     📊  Tools: {tools_count:<4} | MCP Servers: {mcp_count:<3} | Templates: 69                  ║
║                                                                              ║
║     Press Ctrl+C to stop the server                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
\033[0m''')
        
        # Run web server (blocking call)
        run_webserver(prop_conf, user_facade, db_facade, tools_registry, mcp_manager)
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        print('''
\033[93m\033[1m
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ⚠️   SHUTDOWN SIGNAL RECEIVED (Ctrl+C)                                   ║
║                                                                              ║
║     🛑  BEGINNING GRACEFUL SHUTDOWN SEQUENCE...                              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
\033[0m''')
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        print(f'''
\033[91m\033[1m
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ❌  STARTUP ERROR OCCURRED                                               ║
║                                                                              ║
║     Error: {str(e)[:60]:<60}
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
\033[0m''')
        sys.exit(1)
    finally:
        # Cleanup in reverse order of initialization
        TOTAL_SHUTDOWN_STEPS = 4
        
        # Shutdown actor system first (allows actors to complete gracefully)
        if actor_system:
            try:
                print_shutdown_step(1, TOTAL_SHUTDOWN_STEPS, "Terminating Actor System", 'stopping')
                logger.info("Terminating actor system...")
                actor_system.terminate(timeout=5.0)
                logger.info("Actor system terminated")
                print_shutdown_step(1, TOTAL_SHUTDOWN_STEPS, "Actor System Terminated", 'done')
            except Exception as e:
                logger.warning(f"Error terminating actor system: {e}")
                print_shutdown_step(1, TOTAL_SHUTDOWN_STEPS, f"Actor System: {str(e)[:30]}", 'error')
        
        # Shutdown MCP manager
        if mcp_manager:
            print_shutdown_step(2, TOTAL_SHUTDOWN_STEPS, "Disconnecting MCP Servers", 'stopping')
            mcp_manager.shutdown()
            logger.info("MCP manager shutdown")
            print_shutdown_step(2, TOTAL_SHUTDOWN_STEPS, "MCP Servers Disconnected", 'done')
        
        # Close database connection
        if 'db_facade' in locals():
            print_shutdown_step(3, TOTAL_SHUTDOWN_STEPS, "Closing Database Connection", 'stopping')
            db_facade.disconnect()
            logger.info("Database connection closed")
            print_shutdown_step(3, TOTAL_SHUTDOWN_STEPS, "Database Connection Closed", 'done')
        
        # Stop properties auto-reload
        if 'prop_conf' in locals():
            print_shutdown_step(4, TOTAL_SHUTDOWN_STEPS, "Stopping Configuration Watcher", 'stopping')
            prop_conf.stop_reload()
            logger.info("Properties auto-reload stopped")
            print_shutdown_step(4, TOTAL_SHUTDOWN_STEPS, "Configuration Watcher Stopped", 'done')
        
        # Final goodbye message
        print('''
\033[92m\033[1m
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ✅  ABHIKARTA-LLM SERVER SHUTDOWN COMPLETE                               ║
║                                                                              ║
║     All resources have been released gracefully.                             ║
║                                                                              ║
║     👋  Goodbye! Thank you for using Abhikarta-LLM v1.5.2                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
\033[0m''')


if __name__ == '__main__':
    main()
