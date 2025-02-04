#!/usr/bin/env python3

"""
uni.eventsourcing

eventsourcing module
"""
from __future__ import annotations

from .base import es_event_subscriber
from ..events import register_event_subscriber
from ..events import crud


def init():
    """ init, called once from uni application at app init """
    # NOTE: not sure if we should not use EventPre... or direct db events
    register_event_subscriber(crud.EventPostCreate, es_event_subscriber)
    register_event_subscriber(crud.EventPostUpdate, es_event_subscriber)
    register_event_subscriber(crud.EventPostDelete, es_event_subscriber)


if __name__ == "__main__": exit