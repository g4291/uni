#!/usr/bin/env python3

"""
notification module router
"""

from __future__ import annotations
from typing import List

from ...router import Router, Route
from ...router.crud import private_crud_routes

from .model import CreateNotification, Notification, UpdateNotification, db_Notification


class ModuleRouter(Router):
    def create_routes(self) -> List[Route]:
        """ create module routes """
        return private_crud_routes(
            [],
            base_model=Notification,
            database_model=db_Notification,
            create_model=CreateNotification,
            update_model=UpdateNotification,
            base_path="/notification",
            tag="notification",
            root_only=False,
            count_many=False,
        )

    
if __name__ == "__main__": exit()