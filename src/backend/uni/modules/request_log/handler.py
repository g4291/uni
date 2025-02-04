#!/usr/bin/env python3

"""
uni.modules.request_log.handler

request log handler
"""

from __future__ import annotations
from typing import List

from ...database.base import DbParams
from ...handler import PrivateHandler, Depends, db_params, verify_token
from ...logger import core_logger

from .model import RequestLog, db_RequestLog


logger = core_logger().getChild("request_log")

class GetRequestLogHandler(PrivateHandler):
    """get request log """
    def request(self, params: DbParams) -> List[RequestLog]:
        """ request handler """
        # only root should have access
        self.root_check()

        return self.apply_db_params(
            self.database.find({}, db_RequestLog),
            params
        ).fetch()


    @classmethod
    def handler(cls, params = Depends(db_params), auth = Depends(verify_token)):
        handler = cls.new(auth)
        return handler.request(params)

    
if __name__ == "__main__": exit()