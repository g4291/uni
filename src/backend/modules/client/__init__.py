#!/usr/bin/env python3

"""
modules.client

client module
"""

from __future__ import annotations

from uni.router import register_router

from .router import ModuleRouter


def init() -> None:
    register_router(ModuleRouter)