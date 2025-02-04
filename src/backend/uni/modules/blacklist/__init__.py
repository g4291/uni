#!/usr/bin/env python3

"""
uni.modules.blacklist
"""

from __future__ import annotations

from ...middleware import register_middleware
from .middleware import BlackListMiddleware


def init():
    register_middleware(BlackListMiddleware())