#!/usr/bin/env python3

"""
uni.eventsourcing.model

eventsourcing model
"""


from typing import List
import uuid
from pydantic import PrivateAttr

from ..database.model import DatabaseModel
from ..database.base import T_DatabaseModel


class es_Model(DatabaseModel):
    """ Eventsourcing default model"""

    entity_id: uuid.UUID
    entity_data: T_DatabaseModel
    version: int
    event: str
    deleted: bool = False
    
    _index: List[str] = PrivateAttr(default=["entity_id"])


if __name__ == "__main__": exit()