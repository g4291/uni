#!/usr/bin/env python3

"""
uni.modules.user.router

user router
"""

from __future__ import annotations
from typing import List
import uuid

from ...handler.crud.private import count_handler_factory, create_handler_factory, delete_handler_factory, find_handler_factory, get_handler_factory, update_handler_factory
from ...router import RouteMethod, Router, Route
from .handler import ChangePassword, ChangeUserRootSetting, GetLoggedUser
from .model import CreateUser, UpdateUser, User, db_User

class ModuleRouter(Router):

    def create_routes(self) -> List[Route]:
        """ create module routes """
        return[
            # current user get
            Route(
                path="/user/get_self",
                method=RouteMethod.GET,
                tag="user",
                handler=GetLoggedUser.handler,
                response_model=User
            ),
            Route(
                path="/user/create",
                method=RouteMethod.POST,
                tag="user",
                handler=create_handler_factory(CreateUser, database_model=db_User),
                response_model=User
            ),
            Route(
                path="/user/update",
                method=RouteMethod.POST,
                tag="user",
                handler=update_handler_factory(UpdateUser, database_model=db_User),
                response_model=User
            ),
            Route(
                path="/user/delete",
                method=RouteMethod.POST,
                tag="user",
                handler=delete_handler_factory(db_User),
                response_model=uuid.UUID
            ),
            Route(
                path="/user/find",
                method=RouteMethod.POST,
                tag="user",
                handler=find_handler_factory(db_User, fetch_dict_disabled=True),
                response_model=List[User]
            ),
            Route(
                path="/user/count",
                method=RouteMethod.POST,
                tag="user",
                handler=count_handler_factory(db_User),
                response_model=int
            ),
            Route(
                path="/user/get",
                method=RouteMethod.POST,
                tag="user",
                handler=get_handler_factory(db_User),
                response_model=User
            ),
            Route(
                path="/user/password/change",
                method=RouteMethod.POST,
                tag="user",
                handler=ChangePassword.handler,
                response_model=str
            ),
            Route(
                path="/user/root/change",
                method=RouteMethod.POST,
                tag="user",
                handler=ChangeUserRootSetting.handler,
                response_model=str
            )
            
        ]

    
if __name__ == "__main__": exit()