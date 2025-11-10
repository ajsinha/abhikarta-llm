from abc import ABC, abstractmethod

class AbstractRoutes(ABC):

    def __init__(self, app):
        self.app = app
        self.user_manager = None
        self.role_manager = None
        self.resource_manager = None

    def set_user_manager(self, user_manager):
        self.user_manager = user_manager

    def set_role_manager(self,role_manager):
        self.role_manager = role_manager

    def set_resource_manager(self, resource_manager):
        self.resource_manager = resource_manager

    @abstractmethod
    def register_routes(self):
        pass