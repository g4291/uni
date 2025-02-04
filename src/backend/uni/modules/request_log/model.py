#!/usr/bin/env python3

"""
uni.modules.request_log.model

request log database model
"""

from __future__ import annotations

from ...services.request_log import db_RequestLog


__all__ = [
    'db_RequestLog'
]

class RequestLog(db_RequestLog):
    """ RequestLog response model"""

if __name__ == "__main__": exit()