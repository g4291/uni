#!/usr/bin/env python3

"""
security.restrict
"""
from __future__ import annotations

from ..events import register_event_subscriber
from ..events.crud import EventCount, EventFind, EventPostGetOne, EventPreDelete, EventPreUpdate
from ..logger import core_logger

from .event_subscribers import check_user_id, inject_user_id_filter


logger = core_logger().getChild("security")

def user_entities(model_name: str, root_check: bool = False) -> None:
    """
    Registers event subscribers for model that restricts access to the user's own entities only.

    Args:
        model_name (str): The name of the model.
        root_check (bool): If True, root users can access all entities. Default is False.

    Returns:
        None
    """
    register_event_subscriber(EventPostGetOne, check_user_id(model_name, root_check))
    register_event_subscriber(EventPreUpdate, check_user_id(model_name, root_check))
    register_event_subscriber(EventPreDelete, check_user_id(model_name, root_check))
    register_event_subscriber(EventFind, inject_user_id_filter(model_name, root_check))
    register_event_subscriber(EventCount, inject_user_id_filter(model_name, root_check))


if __name__ == "__main__": exit()