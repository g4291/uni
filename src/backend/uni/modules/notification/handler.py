#!/usr/bin/env python3

"""
notification module handler
"""

from ...handler.crud import private
from ...logger import  logger_factory

from .model import db_Notification, CreateNotification


logger = logger_factory()

def create():
    return  private.create_handler_factory(CreateNotification, database_model=db_Notification)

    
if __name__ == "__main__": exit()