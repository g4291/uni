#!/usr/bin/env python3

"""
uni.modules.user.router
"""

from __future__ import annotations
from typing import List
import uuid

from ...handler.crud.private import delete_handler_factory, find_handler_factory, get_handler_factory, count_handler_factory

from ...router import RouteMethod, Router, Route
from .handler import PrivateFileHandler, PublicFileHandler
from .model import FTPListItem, File, db_File


class ModuleRouter(Router):
    """ File module router"""
    def create_routes(self) -> List[Route]:
        """ create module routes """
        r = [
            Route(
                path="/file/create",
                method=RouteMethod.POST,
                tag="file",
                handler=PrivateFileHandler.create,
                response_model=File
            ),
            Route(
                path="/file/create_b64",
                method=RouteMethod.POST,
                tag="file",
                handler=PrivateFileHandler.create_b64,
                response_model=File
            ),
            Route(
                path="/file/delete",
                method=RouteMethod.POST,
                tag="file",
                handler=delete_handler_factory(db_File),
                response_model=uuid.UUID
            ),
            Route(
                path="/file/get",
                method=RouteMethod.POST,
                tag="file",
                handler=get_handler_factory(db_File),
                response_model=File
            ),
            Route(
                path="/file/find",
                method=RouteMethod.POST,
                tag="file",
                handler=find_handler_factory(db_File),
                response_model=List[File]
            ),
            Route(
                path="/file/count",
                method=RouteMethod.POST,
                tag="file",
                handler=count_handler_factory(db_File),
                response_model=List[File]
            ),
            Route(
                path="/file/read",
                method=RouteMethod.GET,
                tag="file",
                handler=PrivateFileHandler.read
            ),
            Route(
                path=self.config.files_read_endpoint,
                method=RouteMethod.GET,
                tag="file",
                handler=PublicFileHandler.read
            )
        ]

        if self.config.module_ftp_enabled:
            r += [
                Route(
                    path="/file/ftp/list",
                    method=RouteMethod.POST,
                    tag="ftp",
                    handler=PrivateFileHandler.ftp_list,
                    response_model=List[FTPListItem]
                ),
                Route(
                    path="/file/ftp/upload",
                    method=RouteMethod.POST,
                    tag="ftp",
                    handler=PrivateFileHandler.ftp_upload
                ),
                Route(
                    path="/file/ftp/download",
                    method=RouteMethod.POST,
                    tag="ftp",
                    handler=PrivateFileHandler.ftp_download
                ),
                Route(
                    path="/file/ftp/delete",
                    method=RouteMethod.POST,
                    tag="ftp",
                    handler=PrivateFileHandler.ftp_delete
                ),
                Route(
                    path="/file/ftp/folder/create",
                    method=RouteMethod.POST,
                    tag="ftp",
                    handler=PrivateFileHandler.ftp_create_folder
                )
            ]

        return r

    
if __name__ == "__main__": exit()