#!/usr/bin/env python3

"""
uni.kvstore_utils
"""

from __future__ import annotations
from typing import Any, Optional

from .logger import core_logger
from .api import get_api_handler
from .modules.kvstore.model import db_KVStore, SetKVStore


logger = core_logger()


def kvstore_get(key: str, default: Any = None) -> Any:
    """
    Retrieve a value from the KVStore.
    
    Args:
        key (str): The key to look up in the KVStore.
        default (Any, optional): The default value to return if the key is not found. Defaults to None.
    
    Returns:
        Any: The value associated with the key if found, otherwise the default value.
    """
    handler = get_api_handler("/kvstore/get", private=True)
    if not handler:
        logger.warning("KVStore API handler not found, using default value")
        return default
    
    response: Optional[db_KVStore] = handler(key=key)
    if response:
        return response.value
    
    logger.warning(f"KVStore key {key} not found, using default value")
    return default


def kvstore_set(key: str, value: Any) -> bool:
    """
    Set a key-value pair in the KVStore.
    
    Args:
        key (str): The key to set in the KVStore.
        value (Any): The value to associate with the key.

    Returns:
        bool: True if the key-value pair was successfully set, False otherwise.
    """
    handler = get_api_handler("/kvstore/set", private=True)
    if not handler:
        logger.warning("KVStore API handler not found, cannot set value")
        return False
    
    rq = SetKVStore(key=key, value=value)
    response = handler(rq)
    
    if response:
        return True
    
    logger.warning(f"KVStore key {key} not set")
    return False
    

if __name__ == '__main__': exit()