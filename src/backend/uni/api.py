#!/usr/bin/env python3

"""
uni.api

api helpret functions
"""

from __future__ import annotations
from typing import Any, Callable

from .application import UniBackend
from .request_context import get_current_request
from .exceptions import BaseHTTPException, NotFoundError, ServerError

from .logger import core_logger, log_call


logger = core_logger().getChild("api")


@log_call(logger)
def get_api_handler(endpoint: str, private: bool = False, raises: bool = False) -> Callable[..., Any]:
    """
    Retrieves the API handler for a given endpoint and wraps it with additional functionality.
    Args:
        endpoint (str): The API endpoint to retrieve the handler for.
        private (bool, optional): If True, the handler requires authentication. Defaults to False.
        raises (bool, optional): If True, exceptions raised by the handler will be propagated. Defaults to False.
    Returns:
        Callable[..., Any]: A wrapped handler function.
    Raises:
        NotFoundError: If the handler for the given endpoint is not found.
        ServerError: If an unexpected error occurs within the handler.
    """
    app = UniBackend.get_instance()
    handler = app.internal_get_handler(endpoint)

    if not handler:
        raise NotFoundError(f"Handler not found")
    
    rq = get_current_request()
    if not rq:
        raise ServerError("No request context found")

    def wrapper(*args, **kwargs) -> Any:
        if private:
            try:
                return handler(*args, auth=rq.auth, **kwargs)
            except BaseHTTPException as e:
                if raises:
                    raise e
                return None
            except Exception as e:
                logger.error(f"Error in handler: {e}")
                raise ServerError("error in handler") from None
        else:
            try:
                return handler(*args, **kwargs)
            except BaseHTTPException as e:
                if raises:
                    raise e
                return None
            except Exception as e:
                logger.error(f"Error in handler: {e}")
                raise ServerError("error in handler") from None
            
    return wrapper

if __name__ == '__main__':
    exit()
