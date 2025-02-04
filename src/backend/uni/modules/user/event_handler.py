#!/usr/bin/env python3

"""
poin module event handler
"""
from __future__ import annotations
from typing import Union

from ...services.auth import remove_user_tokens

from ...events.crud import EventPostDelete, EventPostUpdate
from ...logger import logger_factory


from .model import db_User


logger = logger_factory()

def remove_illegal_tokens(event: Union[EventPostUpdate, EventPostDelete]) -> None:
    """ event listener, remove tokens of disabled or deleted users """
    if (event.data_model != db_User): return None
    
    logger.info(f"remove_disabled_users_tokens: Event: {event}, model: {event.data_model}")
    entity: db_User = event.data

    # nothing to do
    if isinstance(event, EventPostUpdate) and entity.enabled: return

    # remove tokens
    remove_user_tokens(entity.id)

    
if __name__ == "__main__": exit()