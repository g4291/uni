#!/usr/bin/env python3

"""
uni.modules.file.event_handler
"""
from __future__ import annotations

from ...filestorage import UniFileStorageFactory

from ...events.base import EventDeleted
from ...logger import color_red, color_yellow, core_logger

from .model import db_File


logger = core_logger().getChild("file")

def delete_file(event: EventDeleted) -> None:
    """ event listener, delete file """
    if (event.data_model != db_File): return None
    
    logger.debug(f"delete_file: Event: {event}, model: {event.data_model}")
    entity_data: db_File = event.data
    
    fs = UniFileStorageFactory.get()
    if fs.exists(entity_data.filename):
        logger.info(color_yellow(f"deleting file: {entity_data.filename}, user_id: {event.user_id}"))
        try: 
            fs.delete(entity_data.filename)
        except Exception as e: logger.error(color_red(f"Exception whe deleting file: {str(e)}"))  


if __name__ == "__main__": exit()