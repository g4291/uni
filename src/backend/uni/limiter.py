#!/usr/bin/env python3
"""
ApiLimiter 
"""
from __future__ import annotations
from enum import Enum
import time
from typing import Dict, List
import limits
from limits.strategies import MovingWindowRateLimiter

from .config import get_config

from .logger import core_logger
from .default import UniDefault
from .exceptions import ServerError, TooManyRequests


# logger
logger = core_logger().getChild("limiter")


_cache: Dict[str, List[ApiLimiter]] = dict()

class ApiLimiterType(str, Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
        
class ApiLimiter(UniDefault):
    class ApiLimiter:
        """
        A class that represents an API limiter.
        Attributes:
            _limit_value (int): The limit value for the limiter.
            _type (ApiLimiterType): The type of the limiter.
            _count (int): The count of requests made.
            _limiter (MovingWindowRateLimiter): The rate limiter object.
        Methods:
            __init__(limit: int, type: ApiLimiterType): Initializes the ApiLimiter object.
            register(id: str) -> None: Registers the limiter with the given ID.
            hit(key: str) -> None: Hits the limiter with the given key.
            get_limiters(id: str) -> List[ApiLimiter]: Returns a list of ApiLimiter objects for the given ID.
            default_limits() -> List[ApiLimiter]: Returns a list of default ApiLimiter objects.
            low_limits() -> List[ApiLimiter]: Returns a list of low ApiLimiter objects.
            high_limits() -> List[ApiLimiter]: Returns a list of high ApiLimiter objects.
        """
    
    def __init__(self, limit: int, type: ApiLimiterType):
        """
        Initializes a Limiter object with the given limit and type.
        Args:
            limit (int): The limit value for the limiter.
            type (ApiLimiterType): The type of the limiter.
        Raises:
            ServerError: If an invalid limiter type is provided.
        """
        self._limit_value = limit
        self._type = type
        self._count = 0
        self._limiter = MovingWindowRateLimiter(limits.storage.MemoryStorage())
        
        if (type == ApiLimiterType.MINUTE):
            self._limit = limits.RateLimitItemPerMinute(limit)
        elif (type == ApiLimiterType.HOUR):
            self._limit = limits.RateLimitItemPerHour(limit)
        elif (type == ApiLimiterType.DAY):
            self._limit = limits.RateLimitItemPerDay(limit)
        else:
            raise ServerError("Invalid LimiterType")
        
    def register(self, id: str) -> None:
        """
        Register the object with the given ID in the cache.
        Parameters:
            id (str): The ID of the object to be registered.
        Returns:
            None
        """
        if not id in _cache:
            _cache[id] = []
            
        _cache[id].append(self)
        
    # hit limiter
    def hit(self, key: str) -> None:
        """
        Hits the limiter with the given key.
        Args:
            key (str): The key to hit the limiter with.
        Raises:
            TooManyRequests: If there are too many requests and the limit has been reached.
        """
        if not self._limiter.hit(self._limit, key):
            time.sleep(get_config().security_delay_seconds)
            raise TooManyRequests("Too many requests")    
        
    @staticmethod
    def get_limiters(id: str) -> List[ApiLimiter]:
        """
        Retrieves the limiters for the given ID.
        Args:
            id (str): The ID to retrieve the limiters for.
        Returns:
            List[ApiLimiter]: A list of ApiLimiter objects representing the limiters for the given ID.
        """

        return _cache.get(id, [])
    
    
    @staticmethod
    def default_limits():
        """
        Returns the default limits for the API.
        Returns:
            List[ApiLimiter]: A list of ApiLimiter objects.
        """
        return [
            ApiLimiter(60, ApiLimiterType.MINUTE),
            ApiLimiter(2000, ApiLimiterType.HOUR),
            ApiLimiter(20000, ApiLimiterType.DAY)
        ]
    
    @staticmethod
    def low_limits():
        """
        Returns a list of ApiLimiter objects representing the low limits for API calls.
        Returns:
            List[ApiLimiter]: A list of ApiLimiter objects.
        """
        return [
            ApiLimiter(10, ApiLimiterType.MINUTE),
            ApiLimiter(100, ApiLimiterType.HOUR),
            ApiLimiter(1000, ApiLimiterType.DAY)
        ]
    
    @staticmethod
    def high_limits():
        """
        Returns a list of ApiLimiter objects representing the high limits for API calls.
        Returns:
            List[ApiLimiter]: A list of ApiLimiter objects.
        """
        return [
            ApiLimiter(120, ApiLimiterType.MINUTE),
            ApiLimiter(4000, ApiLimiterType.HOUR),
            ApiLimiter(40000, ApiLimiterType.DAY)
        ]
    
        


if __name__ == "__main__": exit()
