#!/usr/bin/env python3

"""
uni.modules.auth.router

authentication router
"""

from __future__ import annotations
from typing import List

from ...router import RouteMethod, Router, Route
from .handler import google_oauth_handler
from ...services.auth import AuthToken


class ModuleRouter(Router):
    """ ModuleRouter class """
    def create_routes(self) -> List[Route]:
        """ creates auth routes"""
        return [
            Route(
                path="/google_oauth",
                method=RouteMethod.POST,
                tag="auth",
                handler=google_oauth_handler,
                response_model=AuthToken
            )
        ]
    

if __name__ == "__main__": exit()