#!/usr/bin/env python3

"""
uni.modules.file
"""

from __future__ import annotations

from ...security import restrict
from ...config import get_config
from ...events.base import EventDeleted
from ...events import register_event_subscriber
from ...database import register_db_model
from ...router import register_router

from .router import ModuleRouter
from .model import db_File
from .event_handler import delete_file

__model_name = db_File.__name__

def init() -> None:
    cfg = get_config()

    register_db_model(db_File)
    register_router(ModuleRouter)
    register_event_subscriber(EventDeleted, delete_file)

    if cfg.security_file_restrict_users:
        restrict.user_entities(__model_name)