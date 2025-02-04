#!/usr/bin/env python3

"""
uni.eventsourcing.handler.public

eventsourcing public handler
"""
from typing import Any, Callable, List, Type
import uuid

from ...database.base import DbParams, T_DatabaseModel
from ...handler.base import PublicHandler
from ...logger import core_logger
from ...handler.crud.public import count_handler_factory, find_handler_factory

from ..model import es_Model
from . import es_model_factory


logger = core_logger().getChild("eventsourcing")

def es_get_handler_factory(database_model: Type[T_DatabaseModel]) -> Callable[[Any], List[es_Model]]:
    """ handler factory: public - get """
    class Handler(PublicHandler):
        def request(self, entity_id: uuid.UUID) -> List[es_Model]:
            """ request handler"""
            # es model
            _Model = es_model_factory(database_model)

            entities = self.database.find({}, _Model)
            params = DbParams(
                filters=[
                    ["entity_id", "==", entity_id]
                ]
            )
            return self.apply_db_params(entities, params).fetch()

    def get_entities(entity_id: uuid.UUID) -> List[es_Model]:  # type: ignore
        handler = Handler.new()
        return handler.request(entity_id=entity_id)

    return get_entities

def es_find_handler_factory(database_model: Type[T_DatabaseModel], fetch_dict_disabled: bool = False) -> Callable[[Any], List[es_Model]]:
    """ es handler factory: private - find """
    _Model = es_model_factory(database_model)
    return find_handler_factory(_Model, fetch_dict_disabled)

def es_count_handler_factory(database_model: Type[T_DatabaseModel]) -> Callable[[Any], int]:
    """ es handler factory: private - count """
    _Model = es_model_factory(database_model)
    return count_handler_factory(_Model)

if __name__ == "__main__": exit()