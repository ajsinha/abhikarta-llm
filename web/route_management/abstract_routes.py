from abc import ABC, abstractmethod
from functools import wraps
from flask import render_template, request, redirect, url_for, session, flash
import logging
from tool_management.mcp_server_manager import MCPServerManager
from model_management.model_registry import ModelRegistry
from llm_provider.llm_facade_factory import LLMFacadeFactory
from llm_provider.facade_cache_manager import FacadeCacheManager

logger = logging.getLogger(__name__)

class AbstractRoutes(ABC):

    def __init__(self, app, db_connection_pool_name: str):
        self.app = app
        self.db_connection_pool_name = db_connection_pool_name
        self.user_manager = None
        self.role_manager = None
        self.resource_manager = None
        self.llm_facade_factory: LLMFacadeFactory = None
        self.model_provider_registry: ModelRegistry = None

        # Initialize facade cache manager
        self.facade_cache = FacadeCacheManager(default_ttl_minutes=60)

        # Initialize MCP Server Manager
        self.mcp_server_manager = MCPServerManager()

    def set_facade_cache(self, facade_cache: FacadeCacheManager):
        """
        Set the facade cache manager.

        Args:
            facade_cache: FacadeCacheManager instance
        """
        self.facade_cache = facade_cache
        logger.info("Facade cache set from external source")

    def generate_interaction_session_id(self) -> str:
        import uuid, time
        """
        Generate a unique chat session ID.

        Returns:
            Unique session identifier
        """
        return f"chat_{uuid.uuid4().hex[:16]}_{int(time.time())}"

    def set_user_manager(self, user_manager):
        self.user_manager = user_manager

    def set_role_manager(self,role_manager):
        self.role_manager = role_manager

    def set_resource_manager(self, resource_manager):
        self.resource_manager = resource_manager

    def set_model_registry(self, model_provider_registry: ModelRegistry):
        self.model_provider_registry = model_provider_registry

    def set_llm_facade_factory(self, llm_facade_factory: LLMFacadeFactory):
        self.llm_facade_factory = llm_facade_factory

    @abstractmethod
    def register_routes(self):
        pass


def login_required(f):
    """
    Decorator to require login for a route.

    Args:
        f: Function to wrap

    Returns:
        Wrapped function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'userid' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator to require admin role for a route.

    Args:
        f: Function to wrap

    Returns:
        Wrapped function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'userid' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))

        if not session.get('is_admin', False):
            flash('You do not have permission to access this page', 'error')
            logger.warning(f"User {session.get('userid')} attempted to access admin page without permission")
            return redirect(url_for('user_dashboard'))

        return f(*args, **kwargs)

    return decorated_function
