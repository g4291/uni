#!/usr/bin/env python3

"""
uni.modules.version.model

version model
"""

from __future__ import annotations
from pydantic import BaseModel

class Version(BaseModel):
    """ Version response model"""
    version: str
    run_id: str
    app_version: str = ""