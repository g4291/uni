#!/usr/bin/env python3

"""
uni.middleware.base

base middleware class
"""

from __future__ import annotations
from typing import Any, Optional
from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse, StreamingResponse

from ..unirequest import UniRequest
from ..database import database_factory
from ..database.base import Database
from ..default import UniDefault
from ..exceptions import BaseHTTPException

class BaseMiddleware(UniDefault):
    """
    BaseMiddleware class

    """
    
    def __init__(self, path: Optional[str] = None) -> None:
        self._path = path
        
    @property
    def path(self) -> Optional[str]:
        return self._path
    
    @property
    def database(self) -> Database:
        return database_factory()
    
    def pre(self, request: UniRequest) -> Optional[Any]:
        """ pre: runs this method before request, if method returns anything request is stopped and value is returned to client """
        return None
    
    def post(self, response: StreamingResponse, request: UniRequest) -> Any:
        return response
    
    def on_http_error(self, status_code: int, request: UniRequest ) -> None:
        """ on_http_error: runs this method on http error, status code >= 400 """
        return None
    
    def on_exception(self, e: Exception, request: UniRequest ) -> None:
        """ on_exception: runs this method on exception """
        return None
    
    async def _default(self, request: Request, call_next) -> StreamingResponse:
        """ runs request without middleware used """
        return await call_next(request)
    
    async def _handler(self, request: Request, call_next) -> Any:
        """ runs requests with middleware used """
        # pre, create json response from return value if any
        uni_request = UniRequest(request)
        try:
            mw_r = self.pre(uni_request)
        except BaseHTTPException as e:
            return(ORJSONResponse(status_code=e.status_code, content={"reason": e.detail}))
        
        if mw_r: 
            return ORJSONResponse(content=mw_r)
        
        # do request, handle no respond on canceled requests
        try:
            r: StreamingResponse = await call_next(request)
        except RuntimeError as e:
            self.on_exception(e, uni_request)
            if str(e) == 'No response returned.' and await request.is_disconnected():
                return Response(status_code=204)
            raise
        except Exception as e:
            self.on_exception(e, uni_request)
            raise e

        # check if response is valid        
        if r.status_code >= 400:
            self.on_http_error(r.status_code, uni_request)
            return r
        
        r = self.post(r, uni_request)
        return r
    
    def add(self, fastapi: FastAPI) -> None:
        """ add middleware to application """
        @fastapi.middleware("http")    
        async def _middleware(request: Request, call_next):
            _path = request.get("path")
            
            # with middleware
            if not self.path or (_path and _path == self.path):
                return await self._handler(request, call_next)
            
            # without middleware
            return await self._default(request, call_next)
        
        

if __name__ == '__main__': exit()