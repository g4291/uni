#!/usr/bin/env python3

"""
uni.modules.background_tasks.handler

maintenance handler
"""

from __future__ import annotations
from typing import List

from ...exceptions import NotFoundError
from ...background_task import BackgroundTaskInfo, BackgroundTask
from ...services.auth import auth_dependency
from ...handler import PrivateHandler
from ...logger import core_logger


logger = core_logger().getChild("background_tasks")

class BackgroundTasksHandler(PrivateHandler):
    def _get(self, id: str) -> BackgroundTaskInfo:
        # root only
        self.root_check()
        
        bg = BackgroundTask.get_background_task_by_id(id)
        if not bg:
            raise NotFoundError("task not found")
        
        return bg.info
        
    def _get_all(self) -> List[BackgroundTaskInfo]:
        # root only
        self.root_check()
        r = []
        
        for v in BackgroundTask.get_all_background_tasks().values():
            r.append(v.info)
        return r

    def _count(self) -> int:
        # root only
        self.root_check()
        return len(BackgroundTask.get_all_background_tasks())    
    
    @classmethod
    def get(cls, auth = auth_dependency()) -> BackgroundTaskInfo:
        handler = cls.new(auth)
        return handler._get()
    
    @classmethod
    def get_all(cls, auth = auth_dependency()) -> List[BackgroundTaskInfo]:
        handler = cls.new(auth)
        return handler._get_all()
    
    @classmethod
    def count(cls, auth = auth_dependency()) -> int:
        handler = cls.new(auth)
        return handler._count()
    
    
if __name__ == "__main__": exit()