#!/usr/bin/env python3

"""
uni.events.crud

crud events
"""

from __future__ import annotations
from .base import Event


class EventPreCreate(Event):
    """event fired before entity is created"""

class EventPostCreate(Event):
    """event fired after entity is created"""

class EventPreUpdate(Event):
    """event fired before entity is updated"""

class EventPostUpdate(Event):
    """event fired after entity is updated"""

class EventPreDelete(Event):
    """event fired before entity is created"""

class EventPostDelete(Event):
    """event fired after entity is deleted"""

class EventPreGetOne(Event):
    """event fired on crud get_one"""

class EventPostGetOne(Event):
    """event fired on crud get_one"""

class EventFind(Event):
    """event fired on crud find"""

class EventCount(Event):
    """event fired on crud count"""


if __name__ == "__main__": exit()
