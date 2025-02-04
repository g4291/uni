#!/usr/bin/env python3

"""
uni.modules.blacklist.middleware

blacklist middleware
"""

from typing import Any, Optional

from ...unirequest import UniRequest
from ...middleware.base import BaseMiddleware


class BlackListMiddleware(BaseMiddleware):
    
    def pre(self, request: UniRequest) -> Optional[Any]:
        # TODO: implement, check ip blacklist
        return None