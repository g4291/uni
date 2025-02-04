#!/usr/bin/env python3

"""
uni.eventsourcing.handler.private

eventsourcing private handler
"""

from typing import Type

from ...database.base import T_DatabaseModel
from ...logger import core_logger

from ..model import es_Model
from ..base import PREFIX, SUFFIX


logger = core_logger().getChild("eventsourcing")

def es_model_factory(database_model: Type[T_DatabaseModel]):
    class _Model(es_Model):
        entity_data: database_model
    _Model.__name__ = PREFIX + database_model.__name__ + SUFFIX

    return _Model