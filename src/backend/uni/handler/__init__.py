#!/usr/bin/env python3

"""
uni.handler

application base handler
"""
from __future__ import annotations
from typing import Any, Optional
from fastapi import Depends, File, Path, Query, Header

from .base import PublicHandler, PrivateHandler
from ..services.auth import AuthToken, verify_token
from ..database import DbOrder, DbParams

__all__ = [

    # FastApi imports
    'Depends',
    'File',
    'Path',
    'Query',
    'Header',

    # handlers
    'PublicHandler',
    'PrivateHandler',

    # auth
    'AuthToken',
    'verify_token',

]

# for post: DEFAULT
def db_params(params: DbParams) -> DbParams:
    return params

# for get method
def db_params_get(
        sort_key: Optional[str] = None,
        sort_order: Optional[DbOrder] = None,
        limit_from: Optional[int] = 0,
        limit_to: Optional[int] = 100,
        filters: Optional[Any] = None
    ) -> DbParams:
    """ database params dependency """
    return DbParams(
        sort_key=sort_key,
        sort_order=sort_order,
        limit_from=limit_from,
        limit_to=limit_to,
        filters=filters
    )