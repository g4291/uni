#!/usr/bin/env python3

"""
uni.modules.request_log

request log module
"""

from __future__ import annotations

from ...services.request_log import db_RequestLog
from ...database import register_db_model
from ...router import register_router
from ...middleware import register_middleware

from .router import ModuleRouter
from .middleware import RequestLogMiddleware

def init() -> None:
    register_db_model(db_RequestLog)
    register_router(ModuleRouter)
    register_middleware(RequestLogMiddleware())