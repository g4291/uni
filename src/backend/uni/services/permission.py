#!/usr/bin/env python3

"""
uni.services.permission

permission service
"""

from __future__ import annotations
from typing import Any, Optional, Protocol, Tuple
import uuid
from pydantic import BaseModel
from typing import List

from ..exceptions import ForbiddenError
from ..utils import convert_permission, timestamp_factory
from ..logger import color_red, core_logger


logger = core_logger().getChild("permission")


MSG_PERM_DENIED = "permission denied"

class ModelMeta(BaseModel):
    """ Database model meta """
    timestamp: int = 0
    user_id: Optional[uuid.UUID] = None

    @classmethod
    def default(cls):
        """ creates defaul ModelMeta"""
        return cls()

    @classmethod
    def default_create(cls):
        """ creates defaul ModelMeta with current timestamp"""
        return cls(timestamp=timestamp_factory())


class Permission(BaseModel):
    """ permission """
    read: bool
    write: bool


class Permissions(BaseModel):
    """ Database model owner meta """
    group: Permission
    all: Permission
    other: Permission

    @classmethod
    def default(cls):
        """ creates defaul PermissionMeta"""

        return cls(
            group=Permission(read=True, write=True),
            all=Permission(read=False, write=False),
            other=Permission(read=False, write=False),
        )

    @classmethod
    def new(cls, permissions: str = "600"):

        try:
            p = cls.default()
            p.group.read, p.group.write = convert_permission(permissions[0])
            p.all.read, p.all.write = convert_permission(permissions[1])
            p.other.read, p.other.write = convert_permission(permissions[2])
            return p
        except Exception as e:
            logger.error(color_red(str(e)))
            raise

class User(Protocol):
    id: uuid.UUID
    root: bool
    user_permissions: List[str]

class Entity(Protocol):
    permissions: Permissions
    created: ModelMeta

def _check(p: Permission, permission_needed: Permission) -> bool:
    """ basic permission check"""
    if permission_needed.write:
        if p.write:
            return True
    if permission_needed.read:
        if p.read:
            return True
    return False

def _check_owner(user_id: uuid.UUID, owner_id: uuid.UUID) -> bool:
    """ check user permission """
    if owner_id == user_id:
        return True
    return False

def _check_group(entity_permissions: Permissions, permission_needed: Permission) -> bool:
    """ check group permission"""
    p = entity_permissions.group
    return _check(p, permission_needed)

def _check_all(entity_permissions: Permissions, permission_needed: Permission) -> bool:
    """ check other users permission """
    p = entity_permissions.all
    return _check(p, permission_needed)

def _check_other(entity_permissions: Permissions, permission_needed: Permission) -> bool:
    """ check anonymous permission """
    p = entity_permissions.other
    return _check(p, permission_needed)

def entity_permission(entity: Entity, user: Optional[User], write: bool, raises: bool = False) -> bool:
    """
    Determine if a user has the necessary permissions for a given entity.
    Args:
        entity (Entity): The entity for which permissions are being checked.
        user (Optional[User]): The user whose permissions are being checked. Can be None for anonymous users.
        write (bool): A flag indicating if write permissions are needed.
        raises (bool, optional): If True, raise ForbiddenError if permission is denied. Defaults to False.
    Returns:
        bool: True if the user has the required permissions, False otherwise.
    Permission checks are performed in the following order:
    1. Other (anonymous) permissions
    2. Anonymous user check
    3. Root user check
    4. All users permissions
    5. Group permissions
    6. Owner permissions
    """
    
    permission_needed = Permission(
        read=True,
        write=bool(write)
    )

    entity_permissions = entity.permissions
    owner = entity.created.user_id

    # other, anonymous
    if _check_other(entity_permissions, permission_needed):
        logger.info("PERMISSIONS other granted")
        return True

    # anonymous
    if not user:
        return False

    # Authenticated user only
    # root
    if user.root:
        return True

    # all users
    if _check_all(entity_permissions, permission_needed):
        logger.info("PERMISSIONS all granted")
        return True

    # group
    if _check_group(entity_permissions, permission_needed):
        logger.info("PERMISSIONS group granted")
        return True

    # owner
    if owner and _check_owner(user.id, owner):
        logger.info("PERMISSIONS user granted")
        return True

    if raises:
        raise ForbiddenError(MSG_PERM_DENIED)
    return False

def group_permission(group_name: str, user: User, write: bool = False, raises = False):
    """
    Check if a user has the specified group permission.
    Args:
        group_name (str): The name of the group.
        user (User): The user object.
        write (bool, optional): If True, check for write permission. Defaults to False.
        raises (bool, optional): If True, raise ForbiddenError if permission is denied. Defaults to False.
    Returns:
        bool: True if the user has the specified permission, False otherwise.
    Raises:
        ForbiddenError: If raises is True and the user does not have the required permission.
    """
    # root
    if user.root:
        return True

    permission_name = group_name
    if write:
        permission_name += ".write"
    else:
        permission_name += ".read"

    if permission_name in user.user_permissions:
        return True

    if raises:
        raise ForbiddenError(MSG_PERM_DENIED)
    return False

def owner_permission(entity: Entity, user: User, raises: bool = False):
    """
    Check if a user is the owner of the entity.
    Args:
        entity (Entity): The entity for which the ownership is being checked.
        user (User): The user object.
        raises (bool, optional): If True, raise ForbiddenError if the user is not the owner. Defaults to False.
    Returns:
        bool: True if the user is the owner of the entity, False otherwise.
    Raises:
        ForbiddenError: If raises is True and the user is not the owner of the entity.
    """
    owner = entity.created.user_id
    if owner == user.id:
        return True

    if raises:
        raise ForbiddenError(MSG_PERM_DENIED)
    return False

def permission_db_filter(user: Optional[User], write: bool = False):
    """
    Generate a database filter based on user permissions.
    Args:
        user (Optional[User]): The user for whom the permissions are being checked. If None, only group, other, and all permissions are considered.
        write (bool): If True, checks for write permissions. If False, checks for read permissions. Default is False.
    Returns:
        dict: A dictionary representing the OR conditions for the database filter based on the user's permissions.
    """
    conditions: List[Tuple[str, str, Any]] = []

    # permission type
    _type = "read"
    if write:
        _type = "write"

    # user? check owner id
    if user:
        conditions.append(
            ("created.user_id", "==", user.id)
        )

    conditions += [
        (f"permissions.group.{_type}", "==", True),
        (f"permissions.other.{_type}", "==", True),
        (f"permissions.all.{_type}", "==", True)
    ]

    return {"OR": conditions}

def owner_db_filter(user: User) -> Tuple[str, str, Any]:
    """
    Generates a database filter condition to check if the given user is the owner.
    Args:
        user (User): The user object containing user details.
    Returns:
        Tuple[str, str, Any]: A tuple representing the filter condition in the format 
                              ("field_name", "operator", value), where "field_name" is 
                              the field to be checked, "operator" is the comparison 
                              operator, and value is the user's ID.
    """
    return ("created.user_id", "==", user.id)
        

if __name__ == '__main__': exit()