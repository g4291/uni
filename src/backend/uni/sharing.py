#!/usr/bin/env python3

"""
uni.sharing
"""

from __future__ import annotations
from typing import List, Optional 
import uuid

from pydantic import BaseModel, Field, validator

from .database.model import DatabaseUpdateModel
from .modules.user.model import db_User
from .utils import validate_email

from .exceptions import ForbiddenError
from .logger import core_logger


logger = core_logger().getChild("sharing")


class SharingMeta(BaseModel):
    """
    SharingMeta is a Pydantic model that represents the metadata for sharing permissions.
    Attributes:
        write (bool): Indicates whether the user has write permissions.
        user_email (uuid.UUID): The unique identifier of the user.
    """
    write: bool
    user_email: str

    @validator('user_email')
    @classmethod
    def email_validator(cls, field):
        return validate_email(field)

class ModelWithSharing(BaseModel):
    """
    ModelWithSharing is a model that includes sharing functionality.
    Attributes:
        sharing (List[SharingMeta]): A list of SharingMeta objects that represent the sharing metadata.
    Methods:
        shared_with(user_email: uuid.UUID, write: bool = False, raises: bool = False) -> bool:
            Checks if the assistant is shared with a specific user.
            Args:
                user_email (uuid.UUID): The UUID of the user to check.
                write (bool, optional): If True, checks if the user has write access. Defaults to False.
                raises (bool, optional): If True, raises a ForbiddenError if the assistant is not shared with the user. Defaults to False.
            Returns:
                bool: True if the assistant is shared with the user (and has write access if specified), False otherwise.
            Raises:
                ForbiddenError: If raises is True and the assistant is not shared with the user.
    """
    sharing: List[SharingMeta] = Field(default_factory=list)

    def shared_with(self, user: db_User, write: bool = False, raises: bool = False) -> bool:
        """
        Check if the current object is shared with a given user.
        Args:
            user (db_User): The user to check sharing status for.
            write (bool, optional): If True, check if the user has write permissions. Defaults to False.
            raises (bool, optional): If True, raise a ForbiddenError if the object is not shared with the user. Defaults to False.
        Returns:
            bool: True if the object is shared with the user (and has write permissions if specified), False otherwise.
        Raises:
            ForbiddenError: If raises is True and the object is not shared with the user.
        """

        for s in self.sharing:
            if s.user_email and s.user_email == user.email:
                if write:
                    return s.write
                return True
            
        if raises:
            raise ForbiddenError("not shared with user")
        return False
    
class DatabaseUpdateModelWithSharing(DatabaseUpdateModel):
    """
    DatabaseUpdateModelWithSharing extends the DatabaseUpdateModel to include sharing metadata.
    Attributes:
        sharing (Optional[List[SharingMeta]]): A list of sharing metadata objects, or None if no sharing metadata is provided.
    """
    sharing: Optional[List[SharingMeta]] = None
    

if __name__ == '__main__': exit()