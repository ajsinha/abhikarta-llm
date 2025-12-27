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


def run_webserver(prop_conf, user_facade, db_facade):
    """
    Initialize and run the web server.
    
    Args:
        prop_conf: PropertiesConfigurator instance
        user_facade: UserFacade instance
        db_facade: DatabaseFacade instance
    """
    from abhikarta.web import AbhikartaLLMWeb
    
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


def print_banner(prop_conf):
    """Print application startup banner."""
    version = prop_conf.get('app.version', '1.0.0')
    host = prop_conf.get('server.host', '0.0.0.0')
    port = prop_conf.get_int('server.port', 5000)
    db_type = prop_conf.get('database.type', 'sqlite')
    debug = prop_conf.get_bool('app.debug', False)
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   █████╗ ██████╗ ██╗  ██╗██╗██╗  ██╗ █████╗ ██████╗ ████████╗   ║
║  ██╔══██╗██╔══██╗██║  ██║██║██║ ██╔╝██╔══██╗██╔══██╗╚══██╔══╝   ║
║  ███████║██████╔╝███████║██║█████╔╝ ███████║██████╔╝   ██║      ║
║  ██╔══██║██╔══██╗██╔══██║██║██╔═██╗ ██╔══██║██╔══██╗   ██║      ║
║  ██║  ██║██████╔╝██║  ██║██║██║  ██╗██║  ██║██║  ██║   ██║      ║
║  ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝      ║
║                          LLM                                     ║
║            AI Agent Design & Orchestration Platform              ║
║                        Version {version}                           ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  Copyright © 2025-2030 Ashutosh Sinha. All Rights Reserved.      ║
╚══════════════════════════════════════════════════════════════════╝

  Starting server...
  Host: {host}
  Port: {port}
  Debug: {debug}
  Database: {db_type}
  
  Access the application at: http://{host}:{port}
  
  Default credentials:
    Admin: admin / admin123
    Domain Admin: domain_admin / domain123
    Developer: developer / dev123
    User: user / user123
    
  Press Ctrl+C to stop the server.
""")


def main():
    """Main entry point for running the Abhikarta-LLM server."""
    logger = logging.getLogger(__name__)
    
    try:
        # 1. Initialize properties configuration
        prop_conf = prepare_prop_conf()
        
        # 2. Setup logging
        setup_logging(prop_conf)
        logger.info("Properties configuration initialized")
        
        # 3. Initialize database
        db_facade = prepare_database(prop_conf)
        logger.info(f"Database initialized: {prop_conf.get('database.type', 'sqlite')}")
        
        # 4. Initialize user facade
        user_facade = prepare_user_facade(prop_conf)
        logger.info("User management initialized")
        
        # 5. Print startup banner
        print_banner(prop_conf)
        
        # 6. Run web server
        run_webserver(prop_conf, user_facade, db_facade)
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        print("\n\nShutting down Abhikarta-LLM server...")
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if 'db_facade' in locals():
            db_facade.disconnect()
            logger.info("Database connection closed")
        
        if 'prop_conf' in locals():
            prop_conf.stop_reload()
            logger.info("Properties auto-reload stopped")
        
        print("Goodbye!")


if __name__ == '__main__':
    main()
