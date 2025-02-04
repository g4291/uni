#!/usr/bin/env python3

"""
uni.database.model

base database model
"""

from pydantic import BaseModel, Field, PrivateAttr
import uuid
from typing import Any, List, Optional, Dict

from ..logger import core_logger
from ..utils import id_factory, timestamp_factory
from ..services.permission import ModelMeta, Permissions


logger = core_logger().getChild("database")


DB_UPDATE_EXCLUDE={'created', 'updated', 'accessed', 'permissions'}

class DatabaseModel(BaseModel):
    """ Base model """
    id: uuid.UUID = Field(default_factory=id_factory)
    owner: Optional[uuid.UUID] = None
    parent: Optional[uuid.UUID] = None
    seq: int = 0
    enabled: bool = True
    note: str = ""

    # meta
    created: ModelMeta = Field(default_factory=ModelMeta.default_create)
    updated: ModelMeta = Field(default_factory=ModelMeta.default)
    accessed: ModelMeta = Field(default_factory=ModelMeta.default)
    permissions: Permissions = Field(default_factory=Permissions.default)

    # index, private, not stored in db
    _unique: List[str] = PrivateAttr(default_factory=list)
    _index: List[str] = PrivateAttr(default_factory=list)
    _compound_index: List[List[str]] = PrivateAttr(default_factory=list)

    # event, private, not stored in db
    _event: bool = PrivateAttr(default=True)

    # field to store joined records from DbResult.join
    joined_collections: Optional[Any] = None

    def __init__(self, **data: dict):
        # joined collections handling
        joined_collections = data.get("joined_collections", None)
        if joined_collections:
            updated_joined_collections: Dict[str, List[Any]] = {}
            for j in joined_collections:
                # list instance, OK
                if isinstance(joined_collections[j], list): updated_joined_collections[j] = joined_collections[j]
                # not list, need to create list a push value
                else: updated_joined_collections[j] = [joined_collections[j]]

                # cleaning, remove empty data(no id)
                for i in updated_joined_collections[j]:
                    if not i.get("id", None):
                        updated_joined_collections[j].remove(i)

            data['joined_collections'] = updated_joined_collections
        
        super().__init__(**data)

    def update(self, data: BaseModel, user_id: Optional[uuid.UUID] = None):
        updated = data.dict(exclude_unset=True, exclude=DB_UPDATE_EXCLUDE)
        entity = self.copy(update=updated)
        entity.updated.timestamp = timestamp_factory()
        entity.updated.user_id = user_id

        return entity
    
    @property
    def lock_key(self) -> str:
        return f"{self.__class__.__name__}_{self.id}.lock"

    @classmethod
    def from_model(cls, m: BaseModel):
        return cls(
            **(m.dict())
        )

class DatabaseUpdateModel(BaseModel):
    """ Base model for update"""
    id: uuid.UUID

    owner: Optional[uuid.UUID] = None
    parent: Optional[uuid.UUID] = None
    note: Optional[str] = None
    enabled: Optional[bool] = None


if __name__ == "__main__": exit()