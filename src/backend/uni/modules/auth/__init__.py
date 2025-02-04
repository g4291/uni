#!/usr/bin/env python3

"""
uni.modules.auth

auth module
"""

from __future__ import annotations

from ...router import register_router
from .router import ModuleRouter


def init() -> None:
    register_router(ModuleRouter)
    

if __name__ == "__main__": exit()
