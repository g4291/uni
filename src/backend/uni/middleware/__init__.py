#!/usr/bin/env python3

"""
uni.middleware

middlewares
"""

from __future__ import annotations
from typing import List

from ..exceptions import ServerError
from .base import BaseMiddleware


__middlewares: List[BaseMiddleware] = [

]

def middleware_factory() -> List[BaseMiddleware]:
    """ return middlewares list """
    return __middlewares

def register_middleware(mw: BaseMiddleware) -> None:
    """ register middleware """
    # check middleware
    if not isinstance(mw, BaseMiddleware):
        raise ServerError(f"Object {mw} is not instance of BaseMiddleware")

    # register
    if mw not in __middlewares:
        __middlewares.append(mw)


if __name__ == '__main__': exit()