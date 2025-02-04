#!/usr/bin/env python3

"""
uni.services.eventsourcing

eventsourcing service
"""


from typing import Dict, Type

from ..lock import UniLock
from ..database import database_factory, register_db_model
from ..database.base import T_DatabaseModel
from ..database.model import DatabaseModel
from ..events.base import Event
from ..logger import color_blue, color_red, color_yellow, core_logger
from ..exceptions import ServerError
from ..eventsourcing.model import es_Model

from . import messages

PREFIX = "es_"
SUFFIX = ""

logger = core_logger().getChild("eventsourcing")

_registered: Dict[Type[T_DatabaseModel], Type[es_Model]] = dict()


def es_event_subscriber(event: Event) -> None:
    """ eventsource event subscriber """
    model = event.data_model
    if not model in _registered.keys():
        return
    
    db = database_factory()
    
    es_model = _registered[model]
    
    logger.debug(color_blue(f"event source event: {event}, model: {model}"))
    with UniLock(f"es_lock_entity_{event.data.id}"):
        version = len(db.find({}, es_model).filter(["entity_id", "==", event.data.id])) + 1

        entity = es_model(
            entity_id=event.data.id, 
            entity_data=event.data, 
            event=event.name,
            version=version
        )
        entity.created.user_id = event.user_id
        # entity.deleted = True if event.__class__ == EventPostDelete else False
        
        if not db.create(entity):
            logger.error()    

def register_es_model(model: Type[T_DatabaseModel]) -> None:
    """ db_Model eventsource registration"""
    if not issubclass(model, DatabaseModel):
        logger.error(color_red(messages.MSG_BAD_MODEL))
        raise ServerError(messages.MSG_BAD_MODEL)
    
    if model in _registered.keys():
        logger.warning(color_yellow(messages.MSG_WARN_REGISTERED % model.__name__))
        return None
    
    # create es model
    class _Model(es_Model):
        entity_data: T_DatabaseModel
    _Model.__name__ = PREFIX + model.__name__ + SUFFIX
    _registered[model] = _Model
    
    # register es model in database
    register_db_model(_Model)
    


if __name__ == "__main__": exit()

