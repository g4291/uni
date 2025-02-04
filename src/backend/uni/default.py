#!/usr/bin/env python3

"""
uni.default

Uni-backend default class
"""

from __future__ import annotations
import threading
import time
from typing import Dict, Type, TypeVar

from .logger import core_logger
from .config import Config, CustomConfig, get_config, get_custom_config


logger = core_logger()
_cache: Dict[str, UniDefault] = {}


T_UniDefault = TypeVar("T", bound="UniDefault")

class UniDefault():
    """
    Default uni class

    """

    def thread_wait(self) -> None:
        thread_wait()

    @property
    def config(self) -> Config:
        """
        Retrieves the configuration settings.
        Returns:
            Config: The configuration settings.
        """
        return get_config()
    
    @property
    def custom_config(self) -> CustomConfig:
        """
        Retrieve the custom configuration.
        Returns:
            CustomConfig: The custom configuration object.
        """
        return get_custom_config()

    @staticmethod
    def thread(fn):
        """
        TODO: MOVE TO UTILS
        A decorator to run a function in a separate thread.
        Args:
            fn (callable): The function to be executed in a new thread.
        Returns:
            callable: A wrapper function that starts the given function in a new thread.
        """
        def wrapper(*args, **kwargs):
            t = threading.Thread(target=fn, args=args, kwargs=kwargs)
            t.start()
            
        return wrapper
    
    @classmethod
    def is_cachable(cls) -> bool:
        """
        Determine if the class is cachable.
        Returns:
            bool: Always returns True, indicating the class is cachable.
        """
        return True
    
    @classmethod
    def cached(cls: Type[T_UniDefault], *args, **kwargs) -> T_UniDefault:
        """
        Creates and returns a cached instance of the class if it is cachable.
        If the class is not cachable, a new instance is created and returned.
        If the class is cachable and an instance is already cached, the cached instance is returned.
        Otherwise, a new instance is created, cached, and returned.
        Args:
            cls (Type[T_UniDefault]): The class to be instantiated and cached.
            *args: Variable length argument list for the class constructor.
            **kwargs: Arbitrary keyword arguments for the class constructor.
        Returns:
            T_UniDefault: An instance of the class, either newly created or retrieved from the cache.
        """

        if not cls.is_cachable():
            logger.debug(f"Class {cls.__name__} is not cachable")
            return cls(*args, **kwargs)
        
        key = cls.__name__
        if key not in _cache:
            logger.debug(f"Creating new object in cache, {key}")
            _cache[key] = cls(*args, **kwargs)
            
        return _cache[key]
    

def thread_wait() -> None:
    """
    Sleep for a short period of time.
    """
    time.sleep(0)
    
if __name__ == '__main__': exit()