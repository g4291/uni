#!/usr/bin/env python3

"""
uni.database.database

database module

"""

from __future__ import annotations
from typing import Callable, Optional, List, Tuple, Type, TypeVar, Any
from pydantic import BaseModel, PrivateAttr

from uni.utils import timestamp_factory

from ..default import UniDefault
from ..database import database_factory, register_db_model
from ..database.model import DatabaseModel
from ..logger import color_yellow, core_logger


logger = core_logger().getChild("cache.dbcache")

T_BaseModel = TypeVar('T_BaseModel', bound='BaseModel')
F_Cache = TypeVar('F_Cache', bound=Callable[..., Tuple[T_BaseModel, bool]])

PREFIX = "cache_"
SUFFIX = ""

class CacheInDatabase(UniDefault):
    """
    CacheInDatabase is a class that provides caching functionality using a database as the storage backend. 
    It allows for creating, retrieving, and managing cache entries for entities that inherit from T_BaseModel.
    Attributes:
        _cache_model (Type[DatabaseModel]): The internal model used for caching, which combines DatabaseModel and the provided model.
        _model (Type[T_BaseModel]): The original model class representing the entity to be cached.
    Methods:
        __init__(self, model: Type[T_BaseModel]):
            Initializes the CacheInDatabase instance with the provided model.
        _create(self, id: str, entity: T_BaseModel) -> bool:
        _get_from_cache(self, id: str) -> Optional[T_BaseModel]:
            Retrieves an entity from the cache by its ID.
        _get_id(self, **kwargs) -> Optional[str]:
            Retrieves the 'id' from the provided keyword arguments and formats it for cache usage.
        cache(cls: Type[CacheInDatabase], model: Type[T_BaseModel]) -> Callable[[F_Cache], Tuple[T_BaseModel, bool]]:
    """
    def __init__(self, model: Type[T_BaseModel], ttl_seconds: int = 0):
        super().__init__()

        # define cache model
        class _Model(DatabaseModel, model):
            expires: int = 0  # 0 = never expires
            cache_id: str
            _unique: List[str] = PrivateAttr(default=["cache_id"])
        
        self._cache_model = _Model
        # model rename
        self._cache_model.__name__ = f"{PREFIX}{model.__name__}{SUFFIX}"
        

        # register cache model
        register_db_model(self._cache_model)
        self._model = model

        self._ttl_seconds = ttl_seconds
        self._check_expired()

    @UniDefault.thread
    def _check_expired(self) -> None:
        """
        Checks for expired cache entries and deletes them from the database.
        This method checks if the cache entries have expired based on the TTL (time-to-live) value.
        If the TTL is not set, the method returns immediately. Otherwise, it retrieves the current
        timestamp and queries the database for entries that have an expiration time less than the
        current timestamp. Any expired entries found are deleted from the database.
        Returns:
            None
        """
        if not self._ttl_seconds: return None
        logger.debug(f"Checking for expired cache entries, model:{self._cache_model.__name__}")

        now_ts = timestamp_factory()
        expired = database_factory().find({}, self._cache_model).filter(["expires", "!=", 0]).filter(["expires", "<", now_ts]).fetch()

        for e in expired:
            self.thread_wait()
            logger.debug(f"Cache expired, deleting: {e}")
            database_factory().delete(e)
        
    def _create(self, id: str, entity: T_BaseModel) -> bool:
        """
        Creates a new cache entry with the given ID and entity.

        Args:
            id (str): The unique identifier for the cache entry.
            entity (T_BaseModel): The entity to be cached, which must be an instance of T_BaseModel.

        Returns:
            bool: True if the cache entry was successfully created, False otherwise.
        """
        # ttl
        self._check_expired()
        expires = 0
        if self._ttl_seconds:
            expires = timestamp_factory() + (self._ttl_seconds * 1000)

        try:
            if database_factory().create(self._cache_model(cache_id=id, **entity.dict(), expires=expires)): 
                return True
        except Exception as e:
            return False
        return False
        
    def _get_from_cache(self, id: str) -> Optional[T_BaseModel]:
        """
        Retrieve an entity from the cache by its ID.
        Args:
            id (str): The ID of the entity to retrieve.
        Returns:
            Optional[T_BaseModel]: The retrieved entity if found, otherwise None.
        Logs:
            Logs a warning if the provided ID is empty.
        """
        if not id: 
            logger.warning(color_yellow("unable to find id, can not use cache"))
            return None
        
        self._check_expired()
        e = database_factory().find({}, self._cache_model).filter(["cache_id", "==", id]).fetch_one()
        if not e:
            return None
        
        return self._model(**e.dict())
    
    def _get_id(self, **kwargs) -> Optional[str]:
        """
        Retrieve the 'id' from the provided keyword arguments and format it for cache usage.

        Args:
            kwargs (dict): A dictionary of keyword arguments.

        Returns:
            str: A formatted string with the 'id' prefixed by 'uc-', or an None if 'id' is not present in kwargs.
        """
        _id = kwargs.get("id", None)
        if not _id: 
            logger.warning(color_yellow("`id` not in kwargs, can not use cache"))
            return None
        return f"uc-{str(_id)}"        
      
    @classmethod
    def cache(cls: Type[CacheInDatabase], model: Type[T_BaseModel], ttl_seconds: int = 0) -> Callable[[F_Cache], Tuple[T_BaseModel, bool]]:
        """
        A decorator to cache the result of a function in a database.
        Args:
            cls (Type[CacheInDatabase]): The class responsible for handling the cache.
            model (Type[T_BaseModel]): The model type to be cached.
            ttl_seconds (int, optional): Time-to-live for the cache in seconds. Defaults to 0 never expires.
        Returns:
            Callable[[F_Cache], Tuple[T_BaseModel, bool]]: A decorator that wraps the function to cache its result.
        The decorator checks if the result of the function is already cached. If it is, it returns the cached result.
        If not, it calls the function, caches the result, and then returns it.
        """

        DbCache = cls(model, ttl_seconds=ttl_seconds)
                
        def decorator(fn: F_Cache) -> F_Cache:
            def wrapper(*args: Any, **kwargs: Any) -> Tuple[T_BaseModel, bool]:
                _id = DbCache._get_id(**kwargs)
                
                # try to find entity
                _cached =  DbCache._get_from_cache(_id)
                if _cached:
                    logger.debug(f"Entity found in cache, using cached value, id: {_id}")
                    return _cached, True
                        
                entity = fn(*args, **kwargs)
                if entity and _id:
                    DbCache._create(_id, entity)
                    
                return entity, False
            return wrapper
        return decorator


if __name__ == "__main__": exit()
