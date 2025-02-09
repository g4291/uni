#!/usr/bin/env python3

"""
uni.handler.crud.private

application crud private handler
"""

# from __future__ import annotations  # can not be used here, (pydantic throws error)

from typing import Any, Callable, List, NewType, Optional, Type
import uuid
from fastapi import Body, Depends
import threading

from ...database.base import Database, DbParams, T_DatabaseModel
from ...database.model import DB_UPDATE_EXCLUDE
from ...exceptions import ForbiddenError, NotFoundError, ServerError
from ...logger import color_red, core_logger
from ...services.auth import verify_token
from ...utils import timestamp_factory
from ...services import permission
from ...events.crud import EventCount, EventFind, EventPostGetOne, EventPreGetOne, EventPostCreate, EventPostDelete, EventPostUpdate, EventPreCreate, EventPreDelete, EventPreUpdate

from .. import db_params
from ..base import PrivateHandler
from .. import messages


logger = core_logger().getChild("handler")

T_LOCK = threading.Lock()

def create_handler_factory(
        model: Type[T_DatabaseModel],
        database_model: Optional[Type[T_DatabaseModel]] = None,
        root_only: bool = False,
        default_permissions: Optional[permission.Permissions] = None
    ) -> Callable[[Any], T_DatabaseModel]:
    """ handler factory: private - create """
    # type for fastapi
    ModelType = NewType('Model', model)  # type: ignore

    class Handler(PrivateHandler):
        """ create entity handler class"""
        def request(self, entity: T_DatabaseModel) -> Optional[T_DatabaseModel]:
            """ request handler"""
            # root check
            if root_only: self.root_check()

            # create entity, store it in database
            if database_model:
                _model = database_model
            else:
                _model = model

            # permissions
            group_name = _model.__name__
            if not permission.group_permission(group_name, self.user, True):
                raise ForbiddenError(messages.MSG_PERM_DENIED)

            _entity = _model(**entity.dict(exclude=DB_UPDATE_EXCLUDE))
            _entity.created.timestamp = timestamp_factory()
            _entity.created.user_id = self.user.id
            _entity.updated.timestamp = 0
            if default_permissions:
                _entity.permissions = default_permissions

            EventPreCreate(_entity, user_id=self.user.id).publish()
            r = self.database.create(_entity)
            if not r:
                logger.error(color_red(messages.MSG_CREATE_ERROR))
                raise ServerError(messages.MSG_CREATE_ERROR)
            EventPostCreate(_entity, user_id=self.user.id).publish()

            # return entity
            return self.database.get_one(r, _model)

    def create_entity(entity: ModelType = Body(), auth=Depends(verify_token)):  # type: ignore
        handler = Handler.new(auth)
        return handler.request(entity=entity)

    return create_entity

def update_handler_factory(
        model: Type[T_DatabaseModel], 
        database_model: Optional[Type[T_DatabaseModel]] = None, 
        root_only: bool = False
    ) -> Callable[[Any], T_DatabaseModel]:
    """ handler factory: private - update """
    # type for fastapi
    ModelType = NewType('Model', model)  # type: ignore

    class Handler(PrivateHandler):
        """ update entity handler class"""
        def request(self, entity: T_DatabaseModel) -> T_DatabaseModel:
            """ request handler"""
            # root check
            if root_only: self.root_check()

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

            # model permissions
            group_name = _model.__name__
            if not permission.group_permission(group_name, self.user, True):
                raise ForbiddenError(messages.MSG_PERM_DENIED)

            # entity permissions
            if not permission.entity_permission(stored_entity, self.user, True):
                raise ForbiddenError(messages.MSG_PERM_DENIED)

            # update entity
            updated_data = entity.dict(exclude_unset=True)
            _entity = stored_entity.copy(update=updated_data)
            _entity = _entity.parse_obj(_entity)
            _entity.updated.timestamp = timestamp_factory()
            _entity.updated.user_id = self.user.id

            EventPreUpdate(_entity, user_id=self.user.id).publish()
            r = self.database.update(_entity)
            if not r:
                logger.error(color_red(messages.MSG_UPDATE_ERROR))
                raise ServerError(messages.MSG_UPDATE_ERROR)
            EventPostUpdate(_entity, user_id=self.user.id).publish()

            # return entity
            return _entity

    def update_entity(entity: ModelType = Body(), auth=Depends(verify_token)):  # type: ignore
        handler = Handler.new(auth)
        return handler.request(entity=entity)

    return update_entity

def update_many_handler_factory(
        model: Type[T_DatabaseModel], 
        database_model: Optional[Type[T_DatabaseModel]] = None, 
        root_only: bool = False
    ) -> Callable[[Any], T_DatabaseModel]:
    """ handler factory: private - update many """
    # type for fastapi
    ModelType = NewType('Model', model)  # type: ignore

    def update_many(entity_list: List[ModelType], auth=Depends(verify_token)) -> List[T_DatabaseModel]:  # type: ignore
        update_handler = update_handler_factory(model, database_model, root_only)
        r = []
        
        for e in entity_list:
            r.append(update_handler(e, auth=auth))
            
        return r

    return update_many

def delete_handler_factory(
        database_model: Type[T_DatabaseModel], 
        root_only: bool = False
    ) -> Callable[[Any], uuid.UUID]:
    """ handler factory: private - delete """
    class Handler(PrivateHandler):
        """ delete entity handler class"""
        def request(self, entity_id: uuid.UUID) -> uuid.UUID:
            """ request handler"""
            # root check
            if root_only: self.root_check()

            # model permissions
            group_name = database_model.__name__
            if not permission.group_permission(group_name, self.user, True):
                raise ForbiddenError(messages.MSG_PERM_DENIED)

            # find entity
            stored_entity = self.database.get_one(entity_id, database_model)
            if not stored_entity:
                msg = f"{messages.MSG_NOT_FOUND}, id: {entity_id}"
                logger.error(color_red(msg))
                raise NotFoundError(msg)

            # entity permissions
            if not permission.entity_permission(stored_entity, self.user, True):
                raise ForbiddenError(messages.MSG_PERM_DENIED)

            # delete entity
            EventPreDelete(stored_entity, user_id=self.user.id).publish()
            r = self.database.delete(stored_entity)
            EventPostDelete(stored_entity, user_id=self.user.id).publish()

            # server error
            if not r:
                logger.error(color_red(messages.MSG_DELETE_ERROR))
                raise ServerError(messages.MSG_DELETE_ERROR)

            # return id
            return entity_id

    def delete_entity(entity_id: uuid.UUID, auth=Depends(verify_token)):  # type: ignore
        handler = Handler.new(auth)
        return handler.request(entity_id=entity_id)

    return delete_entity

def get_handler_factory(
        database_model: Type[T_DatabaseModel], 
        root_only: bool = False
    ) -> Callable[[Any], T_DatabaseModel]:
    """ handler factory: private - get """
    class Handler(PrivateHandler):
        def request(self, entity_id: uuid.UUID) -> T_DatabaseModel:
            """ request handler"""
            # root check
            if root_only: self.root_check()

            # model permissions
            group_name = database_model.__name__
            if not permission.group_permission(group_name, self.user, False):
                raise ForbiddenError(messages.MSG_PERM_DENIED)

            EventPreGetOne(entity_id, user_id = self.user.id).publish()

            # find entity
            stored_entity = self.database.get_one(entity_id, database_model)
            if not stored_entity:
                msg = f"{messages.MSG_NOT_FOUND}, id: {entity_id}"
                logger.error(color_red(msg))
                raise NotFoundError(msg)

            # permissions
            if not permission.entity_permission(stored_entity, self.user, False):
                raise ForbiddenError(messages.MSG_PERM_DENIED)
            
            EventPostGetOne(stored_entity, user_id = self.user.id).publish()

            # TODO: configurable
            # update accesed meta
            # stored_entity.accessed.user_id = self.user.id
            # stored_entity.accessed.timestamp = timestamp_factory()
            # self.database.update(stored_entity)

            # return entity
            return stored_entity

    def get_entity(entity_id: uuid.UUID, auth=Depends(verify_token)):  # type: ignore
        handler = Handler.new(auth)
        return handler.request(entity_id=entity_id)

    return get_entity

def find_handler_factory(
        database_model: Type[T_DatabaseModel],
        root_only: bool = False,
        fetch_dict_disabled: bool = False,
    ) -> Callable[[Any], List[T_DatabaseModel]]:
    """ handler factory: private - find """
    class Handler(PrivateHandler):
        """ find entity handler class"""
        def request(self, params: DbParams) -> Optional[List[T_DatabaseModel]]:
            """ request handler"""
            # root check
            if root_only: self.root_check()

            # model permissions
            group_name = database_model.__name__
            if not permission.group_permission(group_name, self.user, False):
                raise ForbiddenError(messages.MSG_PERM_DENIED)

            entities = self.database.find({}, database_model)
            entities = self.permission_filter(entities)

            EventFind(params, user_id = self.user.id, model_name=database_model.__name__).publish()

            if params.fetch_dict and not fetch_dict_disabled:
                # fetching dict for faster respond serialization
                # needs to be disabled for users!!
                return list(self.apply_db_params(entities, params).fetch_dict())
            else:
                return list(self.apply_db_params(entities, params).fetch())

    def find_entities(params: DbParams = Depends(db_params), auth=Depends(verify_token)):  # type: ignore
        handler = Handler.new(auth)
        return handler.request(params)

    return find_entities

def count_handler_factory(
        database_model: Type[T_DatabaseModel],
        root_only: bool = False
    ) -> Callable[[Any], int]:
    """ handler factory: private - find """
    class Handler(PrivateHandler):
        """ find entity handler class"""
        def request(self, params: DbParams) -> int:
            """ request handler"""
            # root check
            if root_only: self.root_check()

            # model permissions
            group_name = database_model.__name__
            if not permission.group_permission(group_name, self.user, False):
                raise ForbiddenError(messages.MSG_PERM_DENIED)

            entities = self.database.find({}, database_model)
            entities = self.permission_filter(entities)

            EventCount(params, user_id = self.user.id, model_name=database_model.__name__).publish()

            return len(
                self.apply_db_params(entities, params)
            )

    def count_entities(params: DbParams = Depends(db_params), auth=Depends(verify_token)):  # type: ignore
        handler = Handler.new(auth)
        return handler.request(params)

    return count_entities

def count_multiple_handler_factory(
        database_model: Type[T_DatabaseModel],
        root_only: bool = False
    ) -> Callable[[Any], List[int]]:
    """ handler factory: private - count multiple """
    class Handler(PrivateHandler):
        """ count multiple entities handler class"""
        def request(self, params: List[DbParams]) -> List[int]:
            """ request handler"""
            # root check
            if root_only: self.root_check()

            # model permissions
            group_name = database_model.__name__
            if not permission.group_permission(group_name, self.user, False):
                raise ForbiddenError(messages.MSG_PERM_DENIED)

            # count worker
            def count_worker(p: DbParams, database: Database, res: List[int], idx: int):
                with T_LOCK:
                    EventCount(p, user_id = self.user.id, model_name=database_model.__name__).publish()
                entities = database.find({}, database_model)
                entities = self.permission_filter(entities)
                res_item = len(self.apply_db_params(entities, p))
                with T_LOCK:
                    res[idx] = res_item
            
            db = self.database
            r = []
            workers: List[threading.Thread] = []
            idx = 0
            for p in params:
                r.append(0)
                if self.config.multiple_count_use_threads:
                    workers.append(threading.Thread(target=count_worker, args=(p, db, r, idx)))
                    workers[-1].start()
                else:
                    count_worker(p, db, r, idx)
                idx += 1
          
            for t in workers: t.join()
                
            return r

    def count_multiple_entities(params: List[DbParams], auth=Depends(verify_token)):  # type: ignore
        handler = Handler.new(auth)
        return handler.request(params)

    return count_multiple_entities

if __name__ == "__main__": exit()