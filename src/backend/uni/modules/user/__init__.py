#!/usr/bin/env python3

"""
uni.modules.user

user module
"""

from __future__ import annotations

from ...database import register_db_model
from ...router import register_router
from ...events import register_event_subscriber
from ...events.crud import EventPostDelete, EventPostUpdate
from .router import ModuleRouter
from .model import db_User
from .event_handler import remove_illegal_tokens


def init() -> None:
    register_db_model(db_User)
    register_router(ModuleRouter)
    register_event_subscriber(EventPostUpdate, remove_illegal_tokens)
    register_event_subscriber(EventPostDelete, remove_illegal_tokens)