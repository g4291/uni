#!/usr/bin/env python3

"""
uni.services.auth

authentication service
"""

from __future__ import annotations
from copy import copy
import time
from fastapi import Header, Request, params
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple
import uuid
from pydantic import BaseModel, Field, PrivateAttr

from ..exceptions import InvalidCredentialsError, UnauthorizedError
from ..logger import color_red, core_logger
from ..utils import timestamp_factory, password_hash
from ..config import get_config
from ..database import database_factory
from ..database.model import DatabaseModel


MSG_INVALID_CREDENTIALS = "invalid credentials"
MSG_TOKEN_NOT_FOUND = "token not found"
MSG_TOKEN_NOT_PROVIDED = "token not provided"
MSG_USERNAME_NOT_PROVIDED = "username not provided"
MSG_PASSWORD_NOT_PROVIDED = "password not provided"
MSG_TOKEN_INVALID = "invalid token"
MSG_TOKEN_EXPIRED = "token expired"

logger = core_logger().getChild("auth")

class AuthToken(BaseModel):
    """ AuthToken class"""

    _user_id: uuid.UUID = PrivateAttr()
    token: str
    expires: int
    valid: bool
    
    
__SYSTEM_TOKEN = AuthToken(
        token="internal_"+str(uuid.uuid4()),
        expires=0,
        valid=True
    )
__SYSTEM_TOKEN._user_id = uuid.UUID("74a53a57-1752-4451-abb2-34e335b607d4")

# duplicated definition, preventing circular dependency
class db_User(DatabaseModel):
    email: str
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    avatar: str = ""
    user_permissions: List[str] = Field(default_factory=list)
    last_login: int = 0
    root: bool = False
    password_hash: str = ""

# tokens storge
__tokens: Dict[str, AuthToken] = {
    __SYSTEM_TOKEN.token: __SYSTEM_TOKEN
}

def remove_user_tokens(user_id: uuid.UUID) -> None:
    """ Remove user tokens from register"""
    for t in copy(__tokens):
        if __tokens[t]._user_id == user_id:
            logger.info(f"User token removed, token_id: {t}, user_id: {user_id}")
            del __tokens[t]

def get_auth_token(username: str, password: str, password_required: bool = True) -> AuthToken:
    """ Get auth token if user is valid """
    config = get_config()

    if not username:
        logger.error(color_red(MSG_USERNAME_NOT_PROVIDED))
        raise InvalidCredentialsError(MSG_USERNAME_NOT_PROVIDED)

    if password_required and not password:
        logger.error(color_red(MSG_PASSWORD_NOT_PROVIDED))
        raise InvalidCredentialsError(MSG_PASSWORD_NOT_PROVIDED)

    # find user
    database = database_factory()
    r = database.find(
        {}, db_User
    ).filter(["email", "==", username]).fetch()

    # password hash
    hash = ""
    if password_required: hash= password_hash(password, salt = config.security_password_salt)

    for user in r:
        if user.email == username:
            if password_required and hash != user.password_hash:
                # security delay
                time.sleep(config.security_delay_seconds)

                logger.error(color_red(MSG_INVALID_CREDENTIALS))
                raise InvalidCredentialsError(MSG_INVALID_CREDENTIALS)
            
            if not user.enabled:
                remove_user_tokens(user.id)
                logger.error(color_red(MSG_INVALID_CREDENTIALS))
                raise InvalidCredentialsError(MSG_INVALID_CREDENTIALS)
            
            token = AuthToken(
                token=str(uuid.uuid4()),
                expires=timestamp_factory(
                    from_now=timedelta(
                        minutes=config.security_token_expires_minutes
                    )
                ),
                valid=True
            )
            # never expires?
            if config.security_token_expires_minutes == 0:
                token.expires = 0  

            token._user_id=user.id

            if not config.security_multiple_tokens:
                # find user tokens
                remove_user_tokens(user.id)
                
            __tokens[token.token] = token

            return token
    
    # security delay
    time.sleep(config.security_delay_seconds)

    # user not found
    logger.error(color_red(MSG_INVALID_CREDENTIALS))
    raise InvalidCredentialsError(MSG_INVALID_CREDENTIALS)

def check_auth_token(request: Request, token: str, silent: bool = False) -> Optional[Tuple[AuthToken, Request]]:
    """ Check token validity """
    config = get_config()
    
    # empty token
    if not token:
        if silent:
            return None
        
        # security delay
        time.sleep(config.security_delay_seconds)

        logger.error(color_red(MSG_TOKEN_NOT_PROVIDED))
        raise UnauthorizedError(MSG_TOKEN_NOT_PROVIDED)

    # not found
    if token not in __tokens:
        if silent:
            return None
        
        # security delay
        time.sleep(config.security_delay_seconds)

        logger.error(color_red(MSG_TOKEN_NOT_FOUND))
        raise UnauthorizedError(MSG_TOKEN_NOT_FOUND)

    # not valid
    if not __tokens[token].valid:
        if silent:
            return None
        
        # security delay
        time.sleep(config.security_delay_seconds)
        
        logger.error(color_red(MSG_TOKEN_INVALID))
        raise UnauthorizedError(MSG_TOKEN_INVALID)
    
    # expires
    if __tokens[token].expires and __tokens[token].expires < timestamp_factory():
        # remove token
        del __tokens[token]
        
        if silent:
            return None
        
        # security delay
        time.sleep(config.security_delay_seconds)

        logger.error(color_red(MSG_TOKEN_EXPIRED))
        raise UnauthorizedError(MSG_TOKEN_EXPIRED)

    # valid token
    return __tokens[token].copy(deep=True), request
    
def verify_token(request: Request, token: str = Header()) -> Tuple[AuthToken, Request]:
    """ token verification, dependency injection """
    r = check_auth_token(request, token)
    if not r: raise UnauthorizedError("invalid token")
    return r

def system_auth() -> Tuple[AuthToken, Request]:
    """ auth as system user """
    r = check_auth_token(None, __SYSTEM_TOKEN.token)
    if not r: raise UnauthorizedError("invalid token")
    return r

def auth_dependency() -> Any:
    """ auth fastapi dependency """
    return params.Depends(dependency=verify_token, use_cache=True)

def is_system_token(token: AuthToken) -> bool:
    """ check if token is system token """
    return token.token == __SYSTEM_TOKEN.token
