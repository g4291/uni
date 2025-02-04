#!/usr/bin/env python3

"""
uni.services.request_log

authentication service
"""

from __future__ import annotations
from typing import Optional
from starlette.requests import Request
from starlette.datastructures import Address

from ..logger import color_red, core_logger
from ..modules.user.model import  db_User
from ..config import get_config
from ..database import  database_factory
from ..database import DatabaseModel


logger = core_logger().getChild("request_log")

class db_RequestLog(DatabaseModel):
    """ RequestLog database model"""

    method: str
    url: str
    client: Optional[Address]
    headers: dict

def log_private_request(user: db_User) -> None:
    """ log private http request"""
    config = get_config()

    if not config.security_log_private_requests:
        return None

    request = user.request
    if not request: return

    data = db_RequestLog(
        method=request.method,
        url=str(request.url),
        client=request.client,
        headers=dict(request.headers)
    )
    data.created.user_id = user.id

    try:
        db = database_factory()
        db.create(data)
    except Exception as e:
        logger.error(color_red(f"log_private_request: {e}"))

def log_public_request(request: Request) -> None:
    """ log public http request"""
    config = get_config()
    
    if not config.security_log_public_requests:
        return None

    data = db_RequestLog(
        method=request.method,
        url=str(request.url),
        client=request.client,
        headers=dict(request.headers)
    )

    try:
        db = database_factory()
        db.create(data)
    except Exception as e:
        logger.error(color_red(f"log_public_request: {e}"))

