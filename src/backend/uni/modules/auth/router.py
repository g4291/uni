#!/usr/bin/env python3

"""
uni.modules.auth.router

authentication router
"""

from __future__ import annotations
from typing import List

from ...config import get_config
from ...router import RouteMethod, Router, Route
from ...services.auth import AuthToken

from .handler import auth_handler, LoginUserWithRoot


class ModuleRouter(Router):
    """ ModuleRouter class """
    def create_routes(self) -> List[Route]:
        """ creates auth routes"""
        r = [
            Route(
                path="/auth",
                method=RouteMethod.GET,
                tag="auth",
                handler=auth_handler,
                response_model=AuthToken
            ),
        ]
        if get_config().security_enable_login_with_root:
            r.append(    
                Route(
                    path="/auth_with_root",
                    method=RouteMethod.POST,
                    tag="auth",
                    handler=LoginUserWithRoot.handler,
                    response_model=AuthToken
                )
            )

        return r

if __name__ == "__main__": exit()