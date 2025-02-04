#!/usr/bin/env python3

"""
uni.eventsourcing.handler.private

eventsourcing private handler
"""

from typing import Any, Callable, List, Type
import uuid
from fastapi import Depends

from ...database.base import DbParams, T_DatabaseModel
from ...exceptions import ForbiddenError
from ...handler.base import PrivateHandler
from ...logger import core_logger
from ...services.auth import verify_token
from ...services import permission
from ...handler import messages
from ...handler.crud.private import count_handler_factory, find_handler_factory

from ..model import es_Model
from . import es_model_factory


logger = core_logger().getChild("eventsourcing")


def es_get_handler_factory( database_model: Type[T_DatabaseModel], root_only: bool = False) -> Callable[[Any], List[es_Model]]:
    """ es handler factory: private - get """
    class Handler(PrivateHandler):
        def request(self, entity_id: uuid.UUID) -> List[es_Model]:
            """ request handler"""
            # root check
            if root_only: self.root_check()
            
            # es model
            _Model = es_model_factory(database_model)

            # model permissions
            group_name = _Model.__name__
            if not permission.group_permission(group_name, self.user, False):
                raise ForbiddenError(messages.MSG_PERM_DENIED)

            entities = self.database.find({}, _Model)
            entities = self.permission_filter(entities)
            params = DbParams(
                filters=[
                    ["entity_id", "==", entity_id]
                ]
            )
            return list(self.apply_db_params(entities, params).fetch_dict())

    def get_eventsourced_entities(entity_id: uuid.UUID, auth=Depends(verify_token)) -> List[es_Model]:  # type: ignore
        handler = Handler.new(auth)
        return handler.request(entity_id=entity_id)

    return get_eventsourced_entities

def es_find_handler_factory(database_model: Type[T_DatabaseModel], root_only: bool = False, fetch_dict_disabled: bool = False) -> Callable[[Any], List[es_Model]]:
    """ es handler factory: private - find """
    _Model = es_model_factory(database_model)
    return find_handler_factory(_Model, root_only, fetch_dict_disabled)

def es_count_handler_factory(database_model: Type[T_DatabaseModel], root_only: bool = False) -> Callable[[Any], int]:
    """ es handler factory: private - count """
    _Model = es_model_factory(database_model)
    return count_handler_factory(_Model, root_only)


if __name__ == "__main__": exit()