#!/usr/bin/env python3

"""
uni.modules.background_tasks

maintenance module
"""

from __future__ import annotations

from ...router import register_router
from .router import ModuleRouter


def init() -> None:
    register_router(ModuleRouter)
