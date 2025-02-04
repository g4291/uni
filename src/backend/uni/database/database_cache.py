#!/usr/bin/env python3

"""
uni.database.mongo

mongo database cache module

TODO: refactor - use redis or other cache
"""

from __future__ import annotations
import threading
from typing import Any, Dict, List, Tuple

from ..default import UniDefault
from ..logger import core_logger


logger = core_logger().getChild("database_cache")

class DatabaseCache(UniDefault):
    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = dict()
        self._meta: Dict[str, List[str]] = dict()
        self._lock = threading.Lock()
        
    @property   
    def enabled(self) -> bool:
        """ get cfg, is caching enabled """
        return self.config.mongo_cache_enabled

    @property
    def max_size(self) -> int:
        """ get cfg, maximum cache size per collection"""
        return self.config.mongo_cache_size
    
    def _encode(self, data: Any) -> Any:
        return data
    
    def _decode(self, data: Any) -> Any:
        return data
        
    def get(self, collection: str, key: str) -> Tuple[Any, bool]:
        if not self.enabled: return None, False
        
        with self._lock:
            if collection in self._data and key in self._data[collection]:
                logger.debug(f"MongoCache: key({key}) found, using cache, collection: {collection}")
                return self._decode( self._data[collection][key]), True
        
        return None, False
    
    @UniDefault.thread
    def set(self, collection: str, key: str, data: Any) -> None:
        """ set cache for key in collection"""
        if not self.enabled: return None
        
        with self._lock:
            logger.debug(f"MongoCache: setting cache for key: {key}, collection: {collection}")
            if not collection in self._data:
                self._data[collection] = dict()
                self._meta[collection] = []
                
            while len(self._meta[collection]) >= self.max_size:
                logger.debug(f"MongoCache: cache too big, removing oldest records, collection: {collection}")
                first = self._meta[collection][0]
                try:
                    del self._data[collection][first]
                except KeyError as e:
                    logger.warning("key not in found in cache, removing from meta")
                    
                self._meta[collection].pop(0)
                
            self._data[collection][key] = self._encode(data)
            self._meta[collection].append(key)

    @UniDefault.thread
    def delete(self, collection: str, key: str) -> None:
        """ set cache for key in collection"""
        if not self.enabled: return None
        
        with self._lock:
            if not collection in self._data:
                return None
                
            if key in self._data[collection]:
                logger.debug(f"MongoCache: deleting cache for key: {key}, collection: {collection}")
                del self._data[collection][key]
                self._meta[collection].remove(key)
                
    
    @UniDefault.thread
    def clear(self, collection: str) -> None:
        """ clear cache for given collection"""
        if not self.enabled: return None
        
        with self._lock:
            if collection in self._data:
                logger.debug(f"MongoCache: clearing cache for collection: {collection}")
                del self._data[collection]
                del self._meta[collection]
    

if __name__ == "__main__":
    exit()