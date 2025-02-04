#!/usr/bin/env python3

"""
uni.request_context

request context
"""

from contextvars import ContextVar
from typing import Optional

from .unirequest import UniRequest
from .logger import core_logger


logger = core_logger().getChild("request_context")

_context: ContextVar[UniRequest] = ContextVar("uni_requests", default=None)

def get_current_request() -> Optional[UniRequest]:
    """
    Retrieve the current request from the context.
    Returns:
        Optional[UniRequest]: The current request if available, otherwise None.
    """
    return _context.get()

def get_context() -> ContextVar:
    """
    internal use only  !!!

    Retrieve the current context variable.
    Returns:
        ContextVar: The current context variable.
    """

    return _context


if __name__ == "__main__": exit()