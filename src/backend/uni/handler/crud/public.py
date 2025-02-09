#!/usr/bin/env python3

"""
uni.handler.crud.public

application crud public handler
"""

# from __future__ import annotations  # can not be used here, (pydantic throws error)

from typing import Callable, List, NewType, Optional, Type, Any
import uuid
from fastapi import Body, Depends

from ...logger import color_red, core_logger
from ...database.base import DbParams, T_DatabaseModel
from ...database.model import DB_UPDATE_EXCLUDE
from ...exceptions import NotFoundError, ServerError
from ...utils import timestamp_factory
from ...events.crud import EventCount, EventFind, EventPostGetOne, EventPreGetOne, EventPostCreate, EventPostDelete, EventPostUpdate, EventPreCreate, EventPreDelete, EventPreUpdate

from .. import db_params
from .. import messages
from ..base import PublicHandler


logger = core_logger().getChild("handler")


def create_handler_factory(
        model: Type[T_DatabaseModel], 
        database_model: Optional[Type[T_DatabaseModel]] = None
    ) -> Callable[[Any], T_DatabaseModel]:
    """ handler factory: public - create """
    # type for fastapi
    ModelType = NewType('Model', model)  # type: ignore

    class Handler(PublicHandler):
        """ create entity handler class"""
        def request(self, entity: T_DatabaseModel) -> T_DatabaseModel:
            """ request handler"""
            # create entity, store it in database
            if database_model: _model = database_model
            else: _model = model            

            _entity = _model(**entity.dict(exclude=DB_UPDATE_EXCLUDE))
            _entity.created.timestamp = timestamp_factory()
            _entity.updated.timestamp = 0
            
            EventPreCreate(_entity).publish()
            r = self.database.create(_entity)
            if not r:
                logger.error(color_red(messages.MSG_CREATE_ERROR))
                raise ServerError(messages.MSG_CREATE_ERROR)
            EventPostCreate(_entity).publish()

            # return entity
            return self.database.get_one(r, _model)

    def create_entity(entity: ModelType = Body()):  # type: ignore
        handler = Handler.new()
        return handler.request(entity=entity)

    return create_entity

def update_handler_factory(
        model: Type[T_DatabaseModel], 
        database_model: Optional[Type[T_DatabaseModel]] = None
    ) -> Callable[[Any], T_DatabaseModel]:
    """ handler factory: public - update """
    # type for fastapi
    ModelType = NewType('Model', model)  # type: ignore

    class Handler(PublicHandler):
        """ update entity handler class"""
        def request(self, entity: T_DatabaseModel) -> T_DatabaseModel:
            """ request handler"""
            # db model select
            if database_model:
                _model = database_model
            else:
                _model = model

            # find entity
            stored_entity = self.database.get_one(entity.id, _model)
            if not stored_entity:
                msg = f"{messages.MSG_NOT_FOUND}, id: {entity.id}"
                logger.error(color_red(msg))
                raise NotFoundError(msg)

            # update entity
            updated_data = entity.dict(exclude_unset=True)
            _entity = stored_entity.copy(update=updated_data)
            _entity = _entity.parse_obj(_entity)
            _entity.updated.timestamp = timestamp_factory()

            EventPreUpdate(_entity).publish()
            r = self.database.update(_entity)
            if not r:
                logger.error(color_red(messages.MSG_UPDATE_ERROR))
                raise ServerError(messages.MSG_UPDATE_ERROR)
            EventPostUpdate(_entity).publish()

            # return entity
            return _entity

    def update_entity(entity: ModelType = Body()):  # type: ignore
        handler = Handler.new()
        return handler.request(entity=entity)

    return update_entity

def update_many_handler_factory(
        model: Type[T_DatabaseModel], 
        database_model: Optional[Type[T_DatabaseModel]] = None, 
        root_only: bool = False
    ) -> Callable[[Any], T_DatabaseModel]:
    """ handler factory: public - update many """
    # type for fastapi
    ModelType = NewType('Model', model)  # type: ignore

    def update_many(entity_list: List[ModelType]) -> List[T_DatabaseModel]:  # type: ignore
        update_handler = update_handler_factory(model, database_model)
        r = []
        
        for e in entity_list:
            r.append(update_handler(e))
            
        return r

    return update_many

def delete_handler_factory(database_model: Type[T_DatabaseModel]) -> Callable[[Any], uuid.UUID]:
    """ handler factory: public - delete """
    class Handler(PublicHandler):
        """ delete entity handler class"""
        def request(self, entity_id: uuid.UUID) -> uuid.UUID:
            """ request handler"""
            # find entity
            _entity = self.database.get_one(entity_id, database_model)
            if not _entity:
                msg = f"{messages.MSG_NOT_FOUND}, id: {entity_id}"
                logger.error(color_red(msg))
                raise NotFoundError(msg)

            # delete entity
            EventPreDelete(_entity).publish()
            r = self.database.delete(_entity)
            if not r:
                logger.error(color_red(messages.MSG_DELETE_ERROR))
                raise ServerError(messages.MSG_DELETE_ERROR)
            EventPostDelete(_entity).publish

            # return id
            return entity_id

    def delete_entity(entity_id: uuid.UUID):  # type: ignore
        handler = Handler.new()
        return handler.request(entity_id=entity_id)

    return delete_entity

def get_handler_factory(database_model: Type[T_DatabaseModel]) -> Callable[[Any], T_DatabaseModel]:
    """ handler factory: public - get """
    class Handler(PublicHandler):
        def request(self, entity_id: uuid.UUID) -> T_DatabaseModel:
            """ request handler"""
            # find entity
            EventPreGetOne(entity_id).publish()
            _entity = self.database.get_one(entity_id, database_model)
            if not _entity:
                msg = f"{messages.MSG_NOT_FOUND}, id: {entity_id}"
                logger.error(color_red(msg))
                raise NotFoundError(msg)
            
            EventPostGetOne(_entity).publish()

            # update accesed meta
            # _entity.accessed.user_id = None
            # _entity.accessed.timestamp = timestamp_factory()
            # self.database.update(_entity)

            # return entity
            return _entity

    def get_entity(entity_id: uuid.UUID):  # type: ignore
        handler = Handler.new()
        return handler.request(entity_id=entity_id)

    return get_entity

def find_handler_factory(database_model: Type[T_DatabaseModel]) -> Callable[[Any], List[T_DatabaseModel]]:
    """ handler factory: public - find """
    class Handler(PublicHandler):
        """ find entity handler class"""
        def request(self, params: DbParams) -> Optional[List[T_DatabaseModel]]:
            """ request handler"""
            
            EventFind(params, model_name=database_model.__name__).publish()
            entities = self.database.find({}, database_model)
            
            if params.fetch_dict:
                # fetching dict for faster respond serialization
                return list(self.apply_db_params(entities, params).fetch_dict())
            else:
                return list(self.apply_db_params(entities, params).fetch())

    def find_entities(params: DbParams = Depends(db_params)):  # type: ignore
        handler = Handler.new()
        return handler.request(params)

    return find_entities

def count_handler_factory(database_model: Type[T_DatabaseModel]) -> Callable[[Any], List[T_DatabaseModel]]:
    """ handler factory: public - find """
    class Handler(PublicHandler):
        """ count entity handler class"""
        def request(self, params: DbParams) -> int:
            """ request handler"""
            
            EventCount(params, model_name=database_model.__name__).publish()
            entities = self.database.find({}, database_model)
            return len(
                self.apply_db_params(entities, params)
            )

    def count_entities(params: DbParams = Depends(db_params)):  # type: ignore
        handler = Handler.new()
        return handler.request(params)

    return count_entities


if __name__ == "__main__": exit()