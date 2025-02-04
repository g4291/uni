#!/usr/bin/env python3

"""
security.event_subscribers
"""
from __future__ import annotations
from typing import Callable, Union

from ..database import database_factory
from ..database.model import DatabaseModel
from ..database.base import DbParams
from ..exceptions import NotFoundError, ForbiddenError
from ..events.crud import EventCount, EventFind, EventPostGetOne, EventPreDelete, EventPreUpdate
from ..logger import color_yellow, core_logger
from ..modules.user.model import db_User

logger = core_logger().getChild("security")

def check_user_id(model_name: str, root_check: bool = False) -> Callable[[Union[EventPostGetOne, EventPreDelete, EventPreUpdate]], None]:
    def wrapper(event: Union[EventPostGetOne, EventPreDelete, EventPreUpdate]) -> None:
        """ event listener, check file user_id """
        if (event.model_name != model_name): return None
        
        logger.info(color_yellow(f"check_user_on_get_one: Event: {event}, model: {event.data_model}"))
        entity: DatabaseModel = event.data
        
        if not entity.created.user_id or not event.user_id: return None
        
        # user ok
        if entity.created.user_id == event.user_id: return None
        
        # check if user is root
        user = database_factory().get_one(event.user_id, db_User)
        if not user:  raise ForbiddenError("user not found")

        # user is root, ok
        if root_check and user.root: return None
        
        raise NotFoundError("entity not found")
    return wrapper

def inject_user_id_filter(model_name: str, root_check: bool = False) -> Callable[[Union[EventFind, EventCount]], None]:
    def wrapper(event: Union[EventFind, EventCount]) -> None:
        """ event listener, inject user_id filter """
        if (event.model_name != model_name): return None
        
        logger.info(color_yellow(f"inject_user_id_filter: Event: {event}, model: {event.data_model}, model_name: {model_name}, user_id: {event.user_id}"))
        
        if not event.user_id: return None
        
        user = database_factory().get_one(event.user_id, db_User)
        if not user:  raise ForbiddenError("user not found")
        
        # root, nothing to do
        if root_check and user.root: 
            logger.info(color_yellow("inject_user_id_filter: root user, no filter injected"))
            return None
        
        # inject filters
        if isinstance(event.data, DbParams):
            if not event.data.filters: event.data.filters = []
            event.data.filters.append(
                ["created.user_id", "==", event.user_id]
            )
        logger.info(color_yellow("inject_user_id_filter: filter injected"))
    return wrapper

if __name__ == "__main__": exit()