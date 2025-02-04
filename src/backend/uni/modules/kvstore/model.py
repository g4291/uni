#!/usr/bin/env python3

"""
uni.modules.kvstore.router

KVStore model
"""

from __future__ import annotations
from typing import Any, List
from pydantic import BaseModel, PrivateAttr, validator

from ...exceptions import ValidationError
from ...database.model import DatabaseModel


class BaseFile(BaseModel):
    """ base file model, email validation"""
    key: str
    value: Any

class KVStore(DatabaseModel, BaseFile):
    """ base file db model"""
    _unique: List[str] = PrivateAttr(default=["key"])

class db_KVStore(KVStore):
    """ Internal, stored in db"""

class SetKVStore(BaseModel):
    """ Set KV store model"""
    key: str
    value: Any

    @validator("key")
    @classmethod
    def validate_key(cls, key: str) -> str:
        """ validate key"""
        if not key:
            raise ValidationError("Key cannot be empty")
        return key
    


if __name__ == "__main__": exit()