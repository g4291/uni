#!/usr/bin/env python3

"""
uni.with_request

Uni-backend class with UniRequest object
"""

from __future__ import annotations
from typing import Optional


from .default import UniDefault
from .exceptions import ServerError
from .unirequest import UniRequest
from .request_context import get_current_request

from .logger import core_logger


logger = core_logger().getChild("with_request")

class UniWithRequest(UniDefault):
    @property
    def request(self) -> UniRequest:
        """
        Retrieves the current request.

        This method fetches the current request using the `get_current_request` function.
        If no request is found, it raises a `ServerError`.

        Returns:
            UniRequest: The current request object.

        Raises:
            ServerError: If no request is found.
        """
        r = get_current_request()
        if not r:
            raise ServerError("No request found")
        return r
    
    @property
    def optional_request(self) -> Optional[UniRequest]:
        """
        Retrieves the current request if available.
        Returns:
            Optional[UniRequest]: The current request object if it exists, otherwise None.
        """
        return get_current_request()
    

if __name__ == '__main__': exit()