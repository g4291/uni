#!/usr/bin/env python3

"""
uni.router

application router
"""

from __future__ import annotations
from typing import List, Type

from .base import Router, Route, RouteMethod

__all__ = [
    'Router',
    'Route',
    'RouteMethod'
]

class NotRouterError(Exception):
    """ object is not subclass of router exception."""

__routers: List[Type[Router]] = []

def router_factory() -> List[Type[Router]]:
    """ return routers list """
    return __routers

def register_router(router: Type[Router]) -> None:
    """ register router """
    # check router
    if not issubclass(router, Router):
        raise NotRouterError(f"Object {router} is not subclass of Router")

    # register
    if router not in __routers:
        __routers.append(router)


if __name__ == "__main__": exit()    