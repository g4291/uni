#!/usr/bin/env python3

"""
uni.modules.maintenance.router

maintenance router
"""

from __future__ import annotations
from typing import List

from ...background_task import BackgroundTaskInfo
from ...router import RouteMethod, Router, Route
from .handler import MaintenanceDbHandler


class ModuleRouter(Router):
    """ File module router"""
    def create_routes(self) -> List[Route]:
        """ create module routes """
        return[
            Route(
                path="/maintenance/export_db",
                method=RouteMethod.POST,
                tag="maintenance",
                handler=MaintenanceDbHandler.db_export,
                response_model=BackgroundTaskInfo
            ),      
            Route(
                path="/maintenance/import_db",
                method=RouteMethod.POST,
                tag="maintenance",
                handler=MaintenanceDbHandler.db_import,
                response_model=BackgroundTaskInfo
            )       
        ]

    
if __name__ == "__main__": exit()