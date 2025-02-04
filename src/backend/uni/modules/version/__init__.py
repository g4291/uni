#!/usr/bin/env python3

"""
uni.modules.version

version module
"""

from __future__ import annotations

from ...middleware import register_middleware
from ...router import register_router

from .middleware import VersionMiddleware
from .router import ModuleRouter

def init() -> None:
    register_router(ModuleRouter)
    register_middleware(VersionMiddleware())