#!/usr/bin/env python3

"""
uni.module.version.router

version router
"""

from __future__ import annotations
from typing import List

from ...router import RouteMethod, Router, Route
from .handler import version_handler
from .model import Version

class ModuleRouter(Router):
    """ Version router"""
    def create_routes(self) -> List[Route]:
        """ creates /version route"""
        return [
            Route(
                path="/version",
                method=RouteMethod.GET,
                tag="version",
                handler=version_handler,
                response_model=Version
            )
        ]

    
if __name__ == "__main__": exit()