#!/usr/bin/env python3

"""
uni.modules.auth.model

auth model
"""

from __future__ import annotations
import uuid
from pydantic import BaseModel


class AuthWithRootRequest(BaseModel):
    user_id: uuid.UUID
    
    
if __name__ == "__main__": exit()