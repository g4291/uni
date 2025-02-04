#!/usr/bin/env python3

"""
uni.database

database module
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Type
from fastapi import params

from ..exceptions import ServerError


from .base import Database, DbOrder, DbParams, DbResult
from .mongo import MongoDatabase
from .sqlite import SQLiteDatabase
from .model import DatabaseModel
from ..logger import core_logger
from ..config import Config, get_config


logger = core_logger().getChild("database")


__all__ = [
    'Database',
    'DbOrder',
    'DbParams',
    'DbResult',
    'DatabaseModel'
]

__databases: Dict[str, Type[Database]] = {
    "mongodb": MongoDatabase,
    "mongodb+srv": MongoDatabase,
    "sqlite": SQLiteDatabase
}

def database_factory(config: Optional[Config] = None) -> Database:
    """ Database factory returns database object"""
    if not config: config = get_config()
    
    dbtype = config.database_string.split("://")[0]
    if dbtype not in __databases: raise ServerError(f"unknown database type: {dbtype}")
    
    return __databases[dbtype].cached()

def database_dependency() -> Any:
    """ Database fastapi dependency"""
    def f():
        return database_factory()
    return params.Depends(dependency=f, use_cache=False)

def register_db_model(model: Type[DatabaseModel]) -> None:
    db = database_factory()
    db.create_table(model.__name__, model)



if __name__ == "__main__": exit()