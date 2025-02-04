#!/usr/bin/env python3

"""
uni.modules.user.handler

user handler
"""

from __future__ import annotations
import time
from typing import  Optional

from ...exceptions import NotFoundError, ServerError, ValidationError
from ...services.auth import auth_dependency, remove_user_tokens
from ...handler import PrivateHandler
from ...logger import core_logger

from .model import ChangePasswordModel, ChangeUserRootSettingModel, User, db_User


logger = core_logger().getChild("user")


class GetLoggedUser(PrivateHandler):
    """ Get logged user hander """
    def request(self) -> Optional[User]:
        """ request handler"""
        user = User.from_model(
            self.user
        )

        return user

    @classmethod
    def handler(cls, auth = auth_dependency()):
        handler = cls.new(auth)
        return handler.request()
    
    
class ChangePassword(PrivateHandler):
    """ change user password """
    def request(self, rq: ChangePasswordModel):
        _password = rq.password.get_secret_value()
        if len(_password) < self.config.security_min_password_length:
            raise ValidationError(f"password is too short, min password length is: {self.config.security_min_password_length}")

        # changing own password
        if not rq.user_id:
            
            self.user.change_password(_password)
            self.user.request = None
            if not self.database.update(self.user):
                raise ServerError("unable to change password")
            
            # logout
            remove_user_tokens(self.user.id)
            return "ok"
        
        # only root can change other user's password
        self.root_check()
        # get user
        user = self.database.get_one(rq.user_id, db_User)
        if not user:
            raise NotFoundError("user not found")
        
        user.change_password(_password)
        user.request = None
        if not self.database.update(user):
            raise ServerError("unable to change password")

        remove_user_tokens(user.id)
        return "ok"        
    
    @classmethod
    def handler(cls, rq: ChangePasswordModel, auth = auth_dependency()):
        handler = cls.new(auth)
        return handler.request(rq)
    
    
class ChangeUserRootSetting(PrivateHandler):
    """ change user password """
    def request(self, rq: ChangeUserRootSettingModel):
        # only root can change root settings
        self.root_check()
        
        user = self.database.get_one(rq.user_id, db_User)
        if not user:
            raise NotFoundError("user not found")
        user.root = rq.root
        self.database.update(user)
        
        return "ok"
        
    
    @classmethod
    def handler(cls, rq: ChangeUserRootSettingModel, auth = auth_dependency()):
        handler = cls.new(auth)
        return handler.request(rq)

    
if __name__ == "__main__": exit()