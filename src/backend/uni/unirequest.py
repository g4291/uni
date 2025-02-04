#!/usr/bin/env python3

"""
uni.default

Uni-backend default class
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from fastapi import Request, WebSocket

from .utils import timestamp_factory
from .database import database_factory
from .services.auth import AuthToken, check_auth_token, db_User
from .default import UniDefault

class UniRequest(UniDefault):    
    def  __init__(self, request: Request):
        self._request = request
        self._auth = None
        self._user = self._get_user()
        self._start_at = timestamp_factory()
        self._ctx: Dict[str, Any] = {}
    
    def _get_token(self) -> Optional[str]:
        """
        Retrieves the token from the request headers.
        This method iterates through the headers of the request to find a header
        with the key 'token'. If found, it decodes and returns the token value.
        If the token is not found or an error occurs, it returns None.
        Returns:
            Optional[str]: The decoded token if found, otherwise None.
        """
        headers = self.request.get("headers")       
        try:
            for h in headers:
                if h[0] == b'token':
                    return h[1].decode()
        except:
            return None
        return None
    
    def done(self) -> int:
        """
        Calculate the elapsed time since the request started.
        Returns:
            int: The difference between the current timestamp and the start timestamp.
        """
        return timestamp_factory() - self._start_at
        
    def _get_user(self) -> Optional[db_User]:
        """
        Retrieves the user associated with the current request.
        This method first obtains an authentication token from the request. If the token is not present or invalid, 
        it returns None. If the token is valid, it retrieves the user ID from the token and fetches the corresponding 
        user from the database.
        Returns:
            Optional[db_User]: The user object if the token is valid, otherwise None.
        """
        self._token = self._get_token()
        if not self._token: return None
        
        self._auth = check_auth_token(self.request, self._token, silent=True)
        if not self._auth: return None
        return database_factory().get_one(self._auth[0]._user_id, db_User)
    
    @property
    def auth(self) -> Optional[Tuple[AuthToken, Request]]:
        """ returns tuple of AuthToken, Request"""
        return self._auth
        
    @property
    def request(self) -> Request:
        return self._request
        
    @property
    def client(self) -> Optional[Tuple[str, int]]:
        """
        Retrieves the client information from the request.
        Returns:
            Optional[Tuple[str, int]]: A tuple containing the client information 
            (client name and client ID) if available, otherwise None.
        """
        c = self.request.get("client")
        if c: return c[0], c[1]
        return None
        
    @property
    def server(self) -> Optional[Tuple[str, int]]:
        """
        Retrieves the server information from the request.
        Returns:
            Optional[Tuple[str, int]]: A tuple containing the server address and port if available,
            otherwise None.
        """
        s = self.request.get("server")
        if s:
            return s[0], s[1]
        return None

    @property
    def path(self) -> str:
        """
        Retrieve the 'path' value from the request.
        Returns:
            str: The 'path' value if it exists in the request, otherwise an empty string.
        """
        path = self.request.get("path")
        if path: return path
        return ""
    
    @property
    def user(self) -> Optional[db_User]:
        """
        Retrieve the user associated with the request.
        Returns:
            Optional[db_User]: The user object if available, otherwise None.
        """
        return self._user
    
    def set_context(self, key: str, value: Any):
        """
        Sets a value in the context dictionary for a given key.
        Args:
            key (str): The key for the context dictionary.
            value (Any): The value to be set for the given key.
        """
        self._ctx[key] = value

    def get_context(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieve a value from the context dictionary using the provided key.
        Args:
            key (str): The key to look up in the context dictionary.
            default (Optional[Any], optional): The value to return if the key is not found. Defaults to None.
        Returns:
            Any: The value associated with the key if it exists, otherwise the default value.
        """
        return self._ctx.get(key, default=default)
    
    def has_context(self, key: str) -> bool:
        """
        Check if a given key exists in the context.
        Args:
            key (str): The key to check in the context.
        Returns:
            bool: True if the key exists in the context, False otherwise.
        """
        return key in self._ctx
    
    def __str__(self) -> str:
        s = ""
        s += f"{self.__class__.__name__}\n"
        s += f"\tclient: {self.client}\n"
        s += f"\tserver: {self.server}\n"
        s += f"\tpath: {self.path}\n"
        if self.user:
            s += f"\tuser: {self.user.email}"

        return s
    
    def __repr__(self) -> str:
        return self.__str__()
    

class UniWebSocketRequest(UniRequest):
    def __init__(self, ws: WebSocket, token: Optional[str] = None):
        self._ws = ws
        self._ws_token = token
        self._request = ws
        self._user = self._get_user()
        self._start_at = timestamp_factory()
        self._ctx: Dict[str, Any] = {}

    def _get_token(self):
        """
        Retrieve the WebSocket token.
        Returns:
            str: The WebSocket token.
        """
        return self._ws_token
    
    # TODO: implement
    @property
    def server(self) -> Optional[Tuple[str, int]]:
        return None
    
    @property
    def client(self) -> Optional[Tuple[str, int]]:
        """
        Retrieve the client's host and port information.
        Returns:
            Optional[Tuple[str, int]]: A tuple containing the client's host and port if available, 
            otherwise None.
        """
        if self._ws.client:
            return self._ws.client.host, self._ws.client.port
        return None
        
    @property
    def path(self) -> str:
        """
        Returns the path component of the WebSocket URL.
        Returns:
            str: The path component of the WebSocket URL.
        """
        return self._ws.url.path
    

if __name__ == '__main__': exit()




{"token": "68d6788c-b2ef-48df-aa92-deae169063fe", "text": "ahoj"}