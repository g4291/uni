#!/usr/bin/env python3

"""
uni.modules.user.model

user database model
"""

from __future__ import annotations
from typing import List, Optional
import uuid
from pydantic import BaseModel, PrivateAttr, SecretStr, validator, Field
from fastapi import Request

from ...config import get_config
from ...database.model import DatabaseModel, DatabaseUpdateModel
from ...utils import password_hash, validate_email

class BaseUser(BaseModel):
    """ base user model, email validation"""
    email: str
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    avatar: str = ""
    user_permissions: List[str] = Field(default_factory=list)

    # email validation
    @validator('email')
    @classmethod
    def email_validator(cls, field):
        return validate_email(field)

class User(DatabaseModel, BaseUser):
    """ base user db model"""
    last_login: int = 0
    root: bool = False

    _unique: List[str] = PrivateAttr(default=['email'])

class db_User(User):
    """ Internal, stored in db"""
    password_hash: str = ""
    request: Optional[Request] = None

    # password hash
    def __init__(self, **data):

        if "password" in data and data['password'] != "":
            data['password_hash'] = password_hash(data['password'], salt=get_config().security_password_salt)

        super().__init__(**data)
        
    def change_password(self, password: str):
        self.password_hash = password_hash(password, salt=get_config().security_password_salt)

    class Config:
        arbitrary_types_allowed = True

class CreateUser(BaseUser):
    """ CreateUser model used in create user handler """
    password: str
    enabled: bool = True

class UpdateUser(DatabaseUpdateModel):
    """ UpdateUser model"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    avatar: Optional[str] = None
    user_permissions: Optional[List[str]] = None
    root: Optional[bool] = None
    
class ChangePasswordModel(BaseModel):
    user_id: Optional[uuid.UUID]
    password: SecretStr
    
class ChangeUserRootSettingModel(BaseModel):
    user_id: uuid.UUID
    root: bool


if __name__ == "__main__": exit()