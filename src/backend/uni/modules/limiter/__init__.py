#!/usr/bin/env python3

"""
uni.modules.limiter

API limiter module
"""

from __future__ import annotations

from ...middleware import register_middleware

from .middleware import LimiterMiddleware


def init() -> None:
    register_middleware(LimiterMiddleware())