#!/usr/bin/env python3

"""
uni.events

application events
"""

from __future__ import annotations
from typing import Callable, Type

from ..logger import color_blue, core_logger
from ..events import base


logger = core_logger().getChild("events")


def register_event_subscriber(event_type: Type[base.Event], callback: Callable, sync: bool =True) -> None:
    """Register callback to subscribers."""

    # event not exist in subscribers register
    if not event_type.__name__ in base._subscribers:
        base._subscribers[event_type.__name__] = []

    # register subscriber callback
    logger.info(color_blue(f"Subscribe: Event: {event_type.__name__}, Callback: {callback}"))
    base._subscribers[event_type.__name__].append(callback)

def remove_event_subscriber(event_type: Type[base.Event], callback: Callable) -> None:
    """Remove callback from subscribers."""

    # nothing to do
    if not event_type.__name__ in base._subscribers:
        return None

    # nothing to do
    if not callback in base._subscribers[event_type.__name__]:
        return None

    # remove
    logger.info(color_blue(f"Unsubscribe: {event_type.__name__}, Callback: {callback}"))
    base._subscribers[event_type.__name__].remove(callback)

if __name__ == "__main__": exit()