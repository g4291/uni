#!/usr/bin/env python3

"""
uni.modules.request_log.middleware

request log middleware
"""

from typing import Any, Dict, Optional
from http.client import responses

from fastapi.responses import StreamingResponse


from ...unirequest import UniRequest
from ...middleware.base import BaseMiddleware
from ...logger import color_green, color_red, core_logger
from ...request_context import get_context


logger = core_logger().getChild("request_log")

class RequestLogMiddleware(BaseMiddleware):
    def __init__(self, path: Optional[str] = None) -> None:
        super().__init__(path)
        self._ctx_tokens: Dict[UniRequest, Any] = {}

    def _set_context(self, request: UniRequest) -> None:
        """
        Sets the context for the given request.
        This method associates the provided `request` with a context token 
        and stores it in the `_ctx_tokens` dictionary.
        Args:
            request (UniRequest): The request object for which the context is to be set.
        """
        self._ctx_tokens[request] = get_context().set(request)

    def _reset_context(self, request: UniRequest) -> None:
        """
        Resets the context for the given request.
        This method attempts to pop the context token associated with the provided
        request from the internal context tokens dictionary. If a token is found,
        it resets the context using that token. If no token is found, it logs an
        error message indicating the failure to reset the context.
        Args:
            request (UniRequest): The request for which the context needs to be reset.
        """
        token = self._ctx_tokens.pop(request, None)
        if token:
            get_context().reset(token)
            return
        
        logger.error(color_red(f"Failed to reset context for request: {request}"))
    
    def pre(self, request: UniRequest) -> Optional[Any]:
        logger.info(color_green(str(request)))
        self._set_context(request)
        return None
    
    def post(self, response: StreamingResponse, request: UniRequest) -> Any:
        logger.info(color_green(f"Request took {request.done()}ms, path: {request.path}"))
        self._reset_context(request)
        return response
    
    def on_http_error(self, status_code: int, request: UniRequest ) -> None:
        reason = responses.get(status_code, "")
        logger.error(color_red(f"Error processing request, status code: {status_code}, reason: {reason}"))
        self._reset_context(request)
        return None
    
    def on_exception(self, e: Exception, request: UniRequest) -> None:
        self._reset_context(request)
        return None

    

if __name__ == "__main__": exit()