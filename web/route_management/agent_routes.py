from flask import render_template, request, jsonify, session, redirect, url_for, flash
import logging
from datetime import datetime

from web.route_management.abstract_routes import AbstractRoutes

class AgentRoutes(AbstractRoutes):

    def __init__(self, app, db_connection_pool_name: str):
        """
        Initialize workflow routes.

        Args:
            app: Flask application instance
            db_connection_pool_name: Database connection pool name
        """
        super().__init__(app, db_connection_pool_name)

    def register_routes(self):
        pass
