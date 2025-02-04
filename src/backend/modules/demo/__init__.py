#!/usr/bin/env python3

"""
modules.demo
"""

from __future__ import annotations
import uni

from .router import ModuleRouter


def init() -> None:
    uni.register_router(ModuleRouter)