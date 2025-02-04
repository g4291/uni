#!/usr/bin/env python3

"""
uni.modules.google_auth.handler

google authentication handler
"""

from __future__ import annotations
from typing import Any
import requests

from ...database import database_factory
from ...logger import core_logger
from ...exceptions import InvalidCredentialsError, NotFoundError, ServerError, BaseHTTPException
from ...services.auth import AuthToken, db_User, get_auth_token
from ..user import db_User

from .model import GoogleAuthRequest


logger = core_logger().getChild("google_auth")

GOOGLE_VERIFY_URL = "https://www.googleapis.com/oauth2/v3/userinfo?access_token=%s"
    
def google_oauth_handler(auth: GoogleAuthRequest) -> AuthToken:
    """ authentication handler used in Route"""
    try:        
        r = requests.get(GOOGLE_VERIFY_URL % auth.token)
        if not r.ok:
            raise InvalidCredentialsError("invalid google token")
        
        idinfo = r.json()
        
        email = idinfo["email"]       
        first_name = idinfo.get("given_name", "") 
        last_name = idinfo.get("family_name", "") 
        avatar = idinfo.get("picture", "") 
        
        # get token and user        
        token = get_auth_token(email, "", False)
        user = database_factory().get_one(token._user_id, db_User)
        if not user: raise NotFoundError("user not found")
        
        # update user info
        if user.first_name == "": user.first_name = first_name
        if user.last_name == "": user.last_name = last_name
        user.avatar = avatar
        database_factory().update(user)
        
        return token
    except ValueError:
        raise InvalidCredentialsError("invalid google token")
    except BaseHTTPException:
        raise
    except Exception as e:
        raise ServerError(str(e))
    
    
if __name__ == "__main__": exit()

