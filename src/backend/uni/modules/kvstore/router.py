#!/usr/bin/env python3

"""
uni.modules.kvstore.router

KVStore router
"""

from __future__ import annotations
from typing import List
import uuid

from ...router import RouteMethod, Router, Route
from .handler import KVStoreHandler
from .model import KVStore


class ModuleRouter(Router):
    """ KVStore module router"""
    def create_routes(self) -> List[Route]:
        """ create module routes """
        return[
            Route(
                path="/kvstore/get",
                method=RouteMethod.POST,
                tag="kvstore",
                handler=KVStoreHandler.get,
                response_model=KVStore
            ),
            Route(
                path="/kvstore/set",
                method=RouteMethod.POST,
                tag="kvstore",
                handler=KVStoreHandler.set,
                response_model=uuid.UUID
            ),
            Route(
                path="/kvstore/delete",
                method=RouteMethod.POST,
                tag="kvstore",
                handler=KVStoreHandler.delete,
            ),
        ]

    
if __name__ == "__main__": exit()