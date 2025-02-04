#!/usr/bin/env python3

"""
notification module event handler
"""
from __future__ import annotations
from typing import Union

from ...default import UniDefault
from ...database.base import DbParams
from ...exceptions import NotFoundError
from ...events.crud import EventCount, EventFind, EventPostCreate, EventPostGetOne, EventPreDelete, EventPreUpdate
from ...logger import color_red, core_logger

from .model import db_Notification


logger = core_logger().getChild("notification")

def notification_check_user_id(event: Union[EventPostGetOne, EventPreDelete, EventPreUpdate]) -> None:
    """ event listener, check notification user_id """
    if (event.data_model != db_Notification): return None
    
    logger.debug(f"notification_check_user_id: Event: {event}, model: {event.data_model}")
    entity: db_Notification = event.data
    if not entity.user_id: return None
    
    # user ok
    if entity.user_id == event.user_id : return None
    
    raise NotFoundError("entity not found")

def notification_inject_user_id_filter(event: Union[EventFind, EventCount]) -> None:
    """ event listener, inject user_id filter """
    if (event.model_name != db_Notification.__name__): return None
    
    logger.debug(f"notification_inject_user_id_filterr: Event: {event}, model: {event.data_model}")
    
    # should not happen
    if not event.user_id: return None
    
    # inject filters
    if isinstance(event.data, DbParams):
        if not event.data.filters: event.data.filters = []
        event.data.filters.append(
            ["user_id", "==", event.user_id]
        )
        
@UniDefault.thread
def notification_send_to_mail(event: EventPostCreate) -> None:
    """ event listener, send notification to mail """
    if (event.data_model != db_Notification): return None
    
    logger.debug(f"notification_send_to_mail: Event: {event}, model: {event.data_model}")
    entity: db_Notification = event.data
    
    # send mail
    try: entity.send_to_mail()
    except Exception as e: logger.error(color_red(f"notification_send_to_mail: error: {e}"))
    

if __name__ == "__main__": exit()