#!/usr/bin/env python3

"""
notificaion module
"""

from __future__ import annotations


from ...config import get_config
from ...events import register_event_subscriber
from ...modules.notification.event_handler import notification_check_user_id, notification_inject_user_id_filter, notification_send_to_mail
from ...events.crud import EventCount, EventFind, EventPostCreate, EventPostGetOne, EventPreDelete, EventPreUpdate
from ...router import register_router
from ...database import register_db_model

from .router import ModuleRouter
from .model import db_Notification


def init() -> None:
    """ module init, called from Uni application """
    cfg = get_config()
    register_db_model(db_Notification)
    register_router(ModuleRouter)
    register_event_subscriber(EventPostGetOne, notification_check_user_id)
    register_event_subscriber(EventPreUpdate, notification_check_user_id)
    register_event_subscriber(EventPreDelete, notification_check_user_id)
    register_event_subscriber(EventFind, notification_inject_user_id_filter)
    register_event_subscriber(EventCount, notification_inject_user_id_filter)
    if cfg.notifications_send_mail:
        register_event_subscriber(EventPostCreate, notification_send_to_mail)
