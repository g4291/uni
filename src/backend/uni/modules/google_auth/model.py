#!/usr/bin/env python3

"""
uni.modules.google_auth.model

google auth model
"""

from __future__ import annotations
from pydantic import BaseModel


class GoogleAuthRequest(BaseModel):
    token: str

    
if __name__ == "__main__": exit()