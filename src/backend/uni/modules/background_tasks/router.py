#!/usr/bin/env python3

"""
uni.modules.background_tasks.router

maintenance router
"""

from __future__ import annotations
from typing import List

from ...background_task import BackgroundTaskInfo
from ...router import RouteMethod, Router, Route
from .handler import BackgroundTasksHandler


class ModuleRouter(Router):
    """ File module router"""
    def create_routes(self) -> List[Route]:
        """ create module routes """
        return[
            Route(
                path="/background_tasks/get",
                method=RouteMethod.POST,
                tag="tasks",
                handler=BackgroundTasksHandler.get,
                response_model=BackgroundTaskInfo
            ),      
            Route(
                path="/background_tasks/get_all",
                method=RouteMethod.POST,
                tag="tasks",
                handler=BackgroundTasksHandler.get_all,
                response_model=List[BackgroundTaskInfo]
            ),       
            Route(
                path="/background_tasks/count",
                method=RouteMethod.POST,
                tag="tasks",
                handler=BackgroundTasksHandler.count,
                response_model=int
            )       
        ]

    
if __name__ == "__main__": exit()