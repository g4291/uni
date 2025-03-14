#!/usr/bin/env python3
"""
uni.cmd.user

User commands
"""
from __future__ import annotations
import argparse
import getpass
import json

from uni.events.crud import EventPostCreate, EventPostDelete

from ..utils import password_hash, rich_print
from ..config import ApplicationConfig, get_config
from ..database import database_factory
from ..logger import color_blue, color_red, core_logger, set_logging_dev, set_logging_production
from ..modules.user.model import db_User


logger = core_logger().getChild("cmd.user")


def __cmd_add(email: str, root: bool) -> int:
    """
    Add a user to the database.
    Args:
        email (str): The email address of the user.
        root (bool): Whether the user is a root user.
    Returns:
        int: Status code, 0 for success.
    """
    logger.info(f"Add user {email} to database")
    while True:
        password = getpass.getpass(color_blue("Enter password: ")).strip()
        if len(password) < get_config().security_min_password_length:
            logger.error(color_red("Password is too short"))
            continue
        password_check = getpass.getpass(color_blue("Enter password again: ")).strip()
        if password != password_check:
            logger.error(color_red("Passwords do not match"))
            continue
        break
    try:
        u = db_User(
                email=email,
                password_hash=password_hash(password),
                salt=get_config().security_password_salt,
                root=root
            )
        r = database_factory().create(u)
        if not r: raise Exception("Failed to create user")
        EventPostCreate(u).publish()
    except Exception as e:
        logger.error(f"Error creating user {email} \n{e}")
        return 1

    return 0

def __cmd_delete(email: str) -> int:
    """
    Delete a user from the database.
    Args:
        email (str): The email address of the user.
    Returns:
        int: Status code, 0 for success.
    """
    logger.info(f"Delete user {email} from database")
    user = database_factory().find({}, db_User).filter(["email", "==", email]).fetch_one()
    if not user:
        logger.error(f"User {email} not found")
        return 1
    
    while True:
        confirm = input(color_red(f"Are you sure you want to delete user {email}? (yes/no): ")).strip().lower()
        if confirm == "yes": break
        else: 
            logger.info("User deletion cancelled")
            return 0

    try:
        r = database_factory().delete(user)
        if not r: raise Exception("Failed to delete user")
        EventPostDelete(user).publish()
    except Exception as e:
        logger.error(f"Error deleting user {email} \n{e}")
        return 1

    return 0

def __cmd_show(email: str) -> int:
    """
    Show user information based on the provided email.
    Args:
        email (str): The email address of the user to be shown.
    Returns:
        int: Returns 0 if the user is found and displayed, otherwise returns 1 if the user is not found.
    """
    logger.info(f"Show user {email}")
    user = database_factory().find({}, db_User).filter(["email", "==", email]).fetch_one()
    if not user:
        logger.error(f"User {email} not found")
        return 1
    
    rich_print(user)
    return 0

def __cmd_permissions(email: str, permissions_file: str, root: bool) -> int:
    """
    Set user permissions based on the provided email.
    Args:
        email (str): The email address of the user to set permissions for.
    Returns:
        int: Returns 0 if the user is found and permissions are set, otherwise returns 1 if the user is not found.
    """

    user = database_factory().find({}, db_User).filter(["email", "==", email]).fetch_one()
    if not user:
        logger.error(f"User {email} not found")
        return 1
    
    # load permissions file (JSON array)
    if permissions_file != "-":
        logger.info(f"Loading permissions from file {permissions_file}")
        try:
            with open(permissions_file, "r") as f:
                permissions = json.load(f)
                logger.info(f"Permissions: \n{"\n".join(permissions)}")
        except Exception as e:
            logger.error(f"Error loading permissions file {permissions_file} \n{e}")
            return 1
        user.user_permissions = permissions
    
    else:
        logger.info(f"Setting root status for user {email}, root: {root}")
        user.root = root

    r = database_factory().update(user)
    if not r:
        logger.error(f"Error setting permissions for user {email}")
        return 1  

    return 0   

def __cmd_all(permissions_file: str, root: bool) -> int:
    """
    Set permissions for all users.
    Args:
        permissions_file (str): The path to the permissions file.
        root (bool): Whether the user is a root user.
    Returns:
        int: Returns 0 if the permissions are set for all users, otherwise returns 1 if there is an error.
    """

    users = database_factory().find({}, db_User).fetch()

    for u in users:
        email = u.email
        r = __cmd_permissions(email, permissions_file, root) 
        if r: return r


def __main() -> int:
    parser = argparse.ArgumentParser(description='User commands')   
    parser.add_argument("--cfg", default="config.json", help="Path to configuration file, default is config.json")
    parser.add_argument("--email", help="Email address of the user", default="")
    parser.add_argument("--add", action="store_true", help="Add user")
    parser.add_argument("--delete", action="store_true", help="Delete user")
    parser.add_argument("--root", action="store_true", help="User is root")    
    parser.add_argument("--show", action="store_true", help="Show user")

    parser.add_argument("--all", action="store_true", help="Set for all users")
    parser.add_argument("--permissions", default="", help="Path to permissions file or - if you want to change root status")
    args = parser.parse_args()

    # load configuration
    cfg = ApplicationConfig.from_json(args.cfg)
    if cfg.production: set_logging_production()
    else: set_logging_dev()

    # handle commands
    if args.add:
        if args.email == "":
            logger.error("Email address is required")
            return 1
        return __cmd_add(args.email, args.root)
    
    elif args.delete:
        if args.email == "":
            logger.error("Email address is required")
            return
        return __cmd_delete(args.email)
    
    elif args.show:
        if args.email == "":
            logger.error("Email address is required")
            return 1
        return __cmd_show(args.email)
    
    elif args.permissions != "":
        if args.all:
            return __cmd_all(args.permissions, args.root)
        
        if args.email == "":
            logger.error("Email address is required, or use --all to set for all users")
            return 1
        return __cmd_permissions(args.email, args.permissions, args.root)


    # print help
    parser.print_help()
    return 0


if __name__ == "__main__":
    exit(__main())