#!/usr/bin/env python3

"""
uni.handler.base

application base handler
"""

from __future__ import annotations
from typing import Any, Iterable, Mapping, Optional, Tuple
from fastapi import Request, params
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from ..with_request import UniWithRequest
from ..services import permission
from ..database import Database, DbParams, DbResult, database_factory
from ..default import UniDefault
from ..exceptions import BaseHTTPException, ForbiddenError, NotFoundError, UnauthorizedError
from ..logger import core_logger
from ..services.auth import AuthToken, auth_dependency, is_system_token
from ..services.request_log import log_private_request
from ..utils import timestamp_factory
from ..modules.user.model import db_User

from .model import StreamChunk, StreamError


logger = core_logger().getChild("handler")


class Handler(UniWithRequest):
    """ Base Handler class"""
    # _database: Database
    # _config: Config

    def __init__(self) -> None:
        # database init
        self._database = database_factory()        

    @property
    def database(self) -> Database:
        return self._database

    def apply_db_params(self, result: DbResult, params: DbParams) -> DbResult:
        return params.apply(result)
    
    def stream_response(self, stream: Iterable[Any], status_code: int = 200, headers: Optional[Mapping[str, str]] = None, media_type: Optional[str] = None) -> StreamingResponse:
        """
        Streams a response from an iterable source.
        Args:
            stream (Iterable[Any]): The source of the data to stream.
            status_code (int, optional): The HTTP status code for the response. Defaults to 200.
            headers (Optional[Mapping[str, str]], optional): Additional headers to include in the response. Defaults to None.
            media_type (Optional[str], optional): The media type of the response. Defaults to None.
        Yields:
            StreamChunk: Chunks of data or error information to be streamed.
        Returns:
            StreamingResponse: A response object that streams the data.
        """
        # wrapper function to handle exceptions
        def wrapper():
            try:
                for chunk in stream:
                    self.thread_wait()
                    yield StreamChunk(data=chunk).json()

            except BaseHTTPException as e:
                err = StreamError(
                    status=e.status_code,
                    text=e.name,
                    detail=e.detail
                )
                yield StreamChunk(error=err, data=None).json()

            except Exception as e:
                err = StreamError(
                    status_code==500,
                    text="Internal Server Error",
                    detail=str(e)
                )
                yield StreamChunk(error=err).json()

        return StreamingResponse(wrapper(), status_code=status_code, headers=headers, media_type=media_type)

class PublicHandler(Handler):
    """ Public handler """
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def new(cls):
        """ creates new handler"""
        return cls()
    
    @classmethod
    def dependency(cls):
        """
        Creates a dependency injection for the class method `new`.

        This method returns a dependency object that can be used to inject
        the `new` method of the class into other parts of the application.

        Returns:
            params.Depends: A dependency object configured to use the `new`
            method of the class without caching.
        """
        return params.Depends(dependency=cls.new, use_cache=False)

class PrivateHandler(Handler):
    """ Private handler """

    def __init__(
            self,
            auth: Tuple[AuthToken, Request],
            log_request: bool = True
        ) -> None:

        super().__init__()

        # process auth token
        self._process_token(auth)

        # log http request
        if log_request:
            self._log_request()
    
    def permission_filter(self, entities: DbResult, write: bool = False) -> DbResult:
        if self.user.root:
            return entities
        
        entities = entities.filter(
            permission.permission_db_filter(user=self.user, write=write)
        )
        return entities

    @property
    def user(self) -> db_User:
        if not self._user:
            raise UnauthorizedError("user not logged in")

        return self._user

    def root_check(self) -> None:
        """ check if user is root, raise error if not"""
        if not self.user.root:
            raise ForbiddenError("only for root user")


    # DEPRECATED use self.user
    def get_user(self) -> db_User:
        """ get logged user """
        return self.user        

    def _log_request(self):
        """ log http request """
        log_private_request(self._user)

    def _process_token(self, auth: Tuple[AuthToken, Request]) -> None:
        """ process auth token, get authorized user """
        self._auth = auth
        token, request = auth
        user = self.database.get_one(token._user_id, db_User)
        if user:
            #update user last login
            user.last_login = timestamp_factory()
            self.database.update(user)

            user.request = request
            self._user = user
            return
        
        if is_system_token(token):
            self._user = db_User(
                id=token._user_id,
                email="system@uni.local",
                root=True
            )
            return
        else:
            raise NotFoundError("user not found")
        
    @property
    def auth(self) -> Tuple[AuthToken, Request]:
        return self._auth

    @classmethod
    def new(cls, auth: Tuple[AuthToken, Request], log_request: bool = True):
        """ creates new handler"""
        return cls(auth=auth, log_request=log_request)
    
    @classmethod
    def dependency(cls, log_request: bool = True):
        """
        A class method that creates a dependency for FastAPI's dependency injection system.
        Args:
            log_request (bool): A flag indicating whether to log the request. Defaults to True. 
        Returns:
            Callable: A FastAPI dependency that provides an instance of the class with the given authentication and logging settings.
        """
        def wrapper(auth: Tuple[AuthToken, Request] = auth_dependency()):
            return cls.new(auth, log_request)
        return params.Depends(dependency=wrapper, use_cache=False)
    
    
def redirect_handler(url: str):
    """ redirect handler """
    def handler():
        return RedirectResponse(url)
    return handler
    
def static_handler(dir: str, html: bool = True):
    """ server static files """
    def handler():
        return StaticFiles(directory=dir, html=html)
    return handler


if __name__ == "__main__": exit()    