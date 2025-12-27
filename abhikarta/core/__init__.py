"""
Core Module - Core utilities and patterns.

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Legal Notice:
This software and associated documentation are proprietary and confidential.
Unauthorized copying, distribution, modification, or use is strictly prohibited.

Patent Pending: Certain architectural patterns and implementations described in this
software may be subject to patent applications.
"""

import threading


class SingletonMeta(type):
    """
    Thread-safe Singleton metaclass.
    
    Use this metaclass to create singleton classes:
    
    class MyClass(metaclass=SingletonMeta):
        pass
    """
    _instances = {}
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]
    
    @classmethod
    def reset_instance(mcs, cls):
        """Reset the singleton instance (useful for testing)."""
        with mcs._lock:
            if cls in mcs._instances:
                del mcs._instances[cls]


__all__ = ['SingletonMeta']
