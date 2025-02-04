#!/usr/bin/env python3

"""
uni.modules.limiter.middleware

API limiter middleware
"""

from typing import Any, Optional

from ...unirequest import UniRequest
from ...middleware.base import BaseMiddleware
from ...logger import color_green, color_cyan, core_logger

from ...limiter import ApiLimiter


logger = core_logger().getChild("limiter")

class LimiterMiddleware(BaseMiddleware):
    """API Limiter Middleware"""    

    def pre(self, request: UniRequest) -> Optional[Any]:
        """
        Perform pre-processing tasks before handling the request.
        Args:
            request (UniRequest): The request object.
        Returns:
            Optional[Any]: None.
        """
        limiter_id = f"{request.client[0]}"
        for l in ApiLimiter.get_limiters(request.path):
            l.hit(limiter_id)

        return None

    

if __name__ == "__main__": exit()