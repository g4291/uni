#!/usr/bin/env python3

"""
uni.modules.maintenance.handler

maintenance handler
"""

from __future__ import annotations
import os
import uuid
from fastapi import UploadFile

from ...background_task import BackgroundTask, BackgroundTaskInfo
from ...modules.file.handler import PrivateFileHandler
from ...modules.file.model import UniUploadFile
from ...modules.notification.model import db_Notification
from ...modules.notification.handler import create as create_notification
from ...services.auth import auth_dependency
from ...handler import PrivateHandler
from ...logger import core_logger


logger = core_logger().getChild("maintenance")

class MaintenanceDbHandler(PrivateHandler):
    def _db_export(self) -> BackgroundTaskInfo:
        # root only
        self.root_check()
        
        def task(self: MaintenanceDbHandler):
            _exception = ""
            try:
                export_file = self.database.export_database()
                filename = export_file.split("/")[-1]
                
                uni_file = UniUploadFile(export_file, filename, "application/zip")
                file_entity = PrivateFileHandler.create_from_filename(uni_file, auth=self._auth)
                os.remove(export_file)
            except Exception as e:
                _exception = str(e)
                
            # create notification
            notification = db_Notification(
                user_id=self.user.id,
                name="Maintenance: database export",
                text=f"export successfully completed, filename: {filename}",
                detail=None,
                files=[file_entity]
                
            )
            
            if _exception:
                notification.text = "ERROR: " + _exception
            create_notification()(notification, auth=self._auth)
            
        return BackgroundTask("mongo_export", task, self).run()
        
    def _db_import(self, f: UploadFile, drop: bool) -> BackgroundTaskInfo:
        # root only
        self.root_check()
        
        buff = f.file.read()
        buff_fn = f.filename
        
        def task(self: MaintenanceDbHandler):
            _exception = ""
            try:
                filename = self.config.tmp_directory+"/mongo_import"+str(uuid.uuid4())+".zip"
                with open(filename, "wb") as buffer: buffer.write(buff)
                self.database.import_database(filename, drop)
                os.remove(filename)
            except Exception as e:
                _exception = str(e)
            
            # create notification
            notification = db_Notification(
                user_id=self.user.id,
                name="Maintenance: database import",
                text=f"import successfully completed, filename: {buff_fn}",
                detail=None,
                files=[]
                
            )
            
            if _exception:
                notification.text = "ERROR: " + _exception
            create_notification()(notification, auth=self._auth)
            
        return BackgroundTask("mongo_import", task, self).run()

    @classmethod
    def db_export(cls, auth = auth_dependency()) -> BackgroundTaskInfo:
        handler = cls.new(auth)
        return handler._db_export()
    
    @classmethod
    def db_import(cls, f: UploadFile, drop: bool = False, auth = auth_dependency()) -> BackgroundTaskInfo:
        handler = cls.new(auth)
        return handler._db_import(f, drop)
    
    
if __name__ == "__main__": exit()