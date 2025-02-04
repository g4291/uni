#!/usr/bin/env python3

"""
modules.client.router

client router
"""

from __future__ import annotations
from typing import List

from uni.router import RouteMethod, Router, Route
from uni.handler.base import redirect_handler, static_handler


class ModuleRouter(Router):
    """ Facebook module router"""

    def create_routes(self) -> List[Route]:
        """ create module routes """

        return [
            Route(
                path="/",
                method=RouteMethod.GET,
                handler=redirect_handler("/webclient"),
                prefix=""
            ),
            Route(
                path="/webclient",
                method=RouteMethod.STATIC, 
                handler=static_handler("./client"), 
                prefix=""
            )
        ]

    
if __name__ == "__main__": exit()