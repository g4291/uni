#!/usr/bin/env python3

"""
uni.modules.version.middleware

version middleware
"""

from typing import Any
from fastapi.responses import StreamingResponse

from ...unirequest import UniRequest
from ...middleware.base import BaseMiddleware
from ...version import RUN_ID, VERSION


class VersionMiddleware(BaseMiddleware):
    """ injects uni headers """
    def post(self, response: StreamingResponse, request: UniRequest) -> Any:
        # bad type?
        if not isinstance(response, StreamingResponse):
            return response
        
        response.headers["server"] = "uni"
        response.headers["uni-version"] = VERSION
        response.headers["uni-run-id"] = RUN_ID
        return response