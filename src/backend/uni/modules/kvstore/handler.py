#!/usr/bin/env python3

"""
uni.modules.kvstore.router

KVStore handler
"""

from __future__ import annotations
import uuid

from ...utils import timestamp_factory
from ...exceptions import ForbiddenError, ServerError, ValidationError
from ...handler.base import PrivateHandler
from ...services.auth import  auth_dependency
from ...logger import core_logger 

from .model import SetKVStore, db_KVStore


logger = core_logger().getChild("kvstore")

class KVStoreHandler(PrivateHandler):
    def _set(self, kv: SetKVStore) -> uuid.UUID:
        """ set KV store"""
        logger.info(f"set KV store: {kv.key}")
        flt = ["key", "==", kv.key]
        cur = self.database.find({}, db_KVStore).filter(flt)

        # update
        if len(cur) > 0:
            entity = list(cur.fetch())[0]
            
            # check user
            if self.user.root or entity.created.user_id == self.user.id:
                entity.value = kv.value
                entity.updated.user_id = self.user.id
                entity.updated.timestamp = timestamp_factory()
                if not self.database.update(entity):
                    raise ServerError("Cannot update KV store")

                return entity.id

            else:
                raise ForbiddenError("Forbidden")
            
        # create
        entity = db_KVStore(
            key=kv.key,
            value=kv.value,
            created=dict(
                timestamp=timestamp_factory(),
                user_id=self.user.id
            )
        )

        if not self.database.create(entity):
            raise ServerError("Cannot create in KV store")
        
        return entity.id
        
    def _get(self, key: str) -> db_KVStore:
        """ get KV store"""
        logger.info(f"get KV store: {key}")
        if not key:
            raise ValidationError("Key cannot be empty")

        flt = ["key", "==", str(key)]
        cur = self.database.find({}, db_KVStore).filter(flt)
        if len(cur) == 0:
            return db_KVStore(key=str(key), value=None)
        
        for i in cur.fetch():
            return i

    def _delete(self, key: str) -> None:
        """ delete KV store"""
        logger.info(f"delete KV store: {key}")
        if not key:
            raise ValidationError("Key cannot be empty")

        flt = ["key", "==", key]
        cur = self.database.find({}, db_KVStore).filter(flt)
        if len(cur) == 0:
            return
        
        entity = list(cur.fetch())[0]
        
        # check user
        if self.user.root or entity.created.user_id == self.user.id:
            if not self.database.delete(entity):
                raise ServerError("Cannot delete KV store")
            return
        
        raise ForbiddenError("Forbidden")
    
    @classmethod
    def set(cls, kv: SetKVStore, auth=auth_dependency()) -> uuid.UUID:
        """ set KV store"""
        return cls.new(auth=auth)._set(kv)
    
    @classmethod
    def get(cls, key: str, auth=auth_dependency()) -> db_KVStore:
        """ set KV store"""
        return cls.new(auth=auth)._get(key)
    
    @classmethod
    def delete(cls, key: str, auth=auth_dependency()) -> None:
        """ set KV store"""
        return cls.new(auth=auth)._delete(key)

if __name__ == "__main__": exit()