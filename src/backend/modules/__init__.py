#!/usr/bin/env python3

"""
user modules
"""

from __future__ import annotations
from importlib import import_module

from uni.config import get_config

def modules_init() -> None:
    for m in get_config().modules:
        _m = import_module('modules.'+m)
        _m.init()
