#!/usr/bin/env python3

"""
uni.modules.request_log.router

request log router
"""

from __future__ import annotations
from typing import List

from ...router import RouteMethod, Router, Route

from .handler import GetRequestLogHandler
from .model import RequestLog


class ModuleRouter(Router):
    """ Request log module router"""
    def create_routes(self) -> List[Route]:
        """ create module routes """
        return [
            Route(
                path="/request_log/get/",
                method=RouteMethod.POST,
                tag="log",
                handler=GetRequestLogHandler.handler,
                response_model=List[RequestLog]
            )
        ]

    
if __name__ == "__main__": exit()