#!/usr/bin/env python3

"""
uni.modules.kvstore

KVStore
"""

from __future__ import annotations

from ...database import register_db_model
from ...router import register_router

from .router import ModuleRouter
from .model import db_KVStore


def init() -> None:
    register_db_model(db_KVStore)
    register_router(ModuleRouter)
