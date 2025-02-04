#!/usr/bin/env python3

"""
uni.modules.auth.handler

authentication handler
"""

from __future__ import annotations
import uuid
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from ...handler.base import PrivateHandler
from ...database import database_factory
from ...logger import core_logger
from ...exceptions import NotFoundError
from ...services.auth import AuthToken, auth_dependency, db_User, get_auth_token
from ..user import db_User

from .model import AuthWithRootRequest


logger = core_logger().getChild("auth")

def auth_handler(credentials: HTTPBasicCredentials = Depends(HTTPBasic())) -> AuthToken:
    """ authentication handler used in Route"""
    return get_auth_token(credentials.username, credentials.password)
class LoginUserWithRoot(PrivateHandler):
    def request(self, user_id: uuid.UUID) -> AuthToken:
        self.root_check()

        user = database_factory().get_one(user_id, db_User)
        if not user:
            raise NotFoundError(f"user not found, id: {user_id}")
        
        return get_auth_token(user.email, "", False)

    @classmethod
    def handler(cls, params: AuthWithRootRequest, auth = auth_dependency()) -> AuthToken:
        h = cls.new(auth)
        return h.request(params.user_id)
    
    
if __name__ == "__main__": exit()

