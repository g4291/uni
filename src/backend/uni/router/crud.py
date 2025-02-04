#!/usr/bin/env python3

"""
uni.router.crud

This module provides a set of functions to generate CRUD routes for a given database model.
"""

from __future__ import annotations
from typing import Callable, List, Optional, Type
import uuid

from ..database.base import T_DatabaseModel
from ..limiter import ApiLimiter
from ..services.permission import Permissions
from ..logger import core_logger
from ..handler.crud import private, public

from .base import Route, RouteMethod


logger = core_logger().getChild("router")


def private_crud_routes(
        routes: List[Route],
        base_model: Type[T_DatabaseModel],
        database_model: Type[T_DatabaseModel],
        create_model: Type[T_DatabaseModel],
        update_model: Type[T_DatabaseModel],
        base_path: str,
        tag: str,
        *,
        root_only: bool = False,
        default_permissions: Optional[Permissions] = None,
        find_fetch_dict_disabled: bool = False,
        create: bool = True, 
        update: bool = True, 
        update_many: bool = True,
        delete: bool = True, 
        get: bool = True, 
        find: bool = True,
        count: bool = True,
        count_many = True,
        limiter_factory: Optional[Callable[[], List[ApiLimiter]]] = None
) -> List[Route]:
    if create:
        routes.append(
            Route(
                path=f"{base_path}/create",
                method=RouteMethod.POST,
                tag=tag,
                handler=private.create_handler_factory(create_model, database_model, root_only=root_only, default_permissions=default_permissions),
                response_model=base_model,
                limits=limiter_factory() if limiter_factory else None
            )
        )

    if update:
        routes.append(
            Route(
                path=f"{base_path}/update",
                method=RouteMethod.POST,
                tag=tag,
                handler=private.update_handler_factory(update_model, database_model, root_only=root_only),
                response_model=base_model,
                limits=limiter_factory() if limiter_factory else None
            )
        )

    if update_many:
        routes.append(
            Route(
                path=f"{base_path}/update_many",
                method=RouteMethod.POST,
                tag=tag,
                handler=private.update_many_handler_factory(update_model, database_model, root_only=root_only),
                response_model=List[base_model],
                limits=limiter_factory() if limiter_factory else None
            )
        )

    if delete:
        routes.append(
            Route(
                path=f"{base_path}/delete",
                method=RouteMethod.POST,
                tag=tag,
                handler=private.delete_handler_factory(database_model, root_only=root_only),
                response_model=uuid.UUID,
                limits=limiter_factory() if limiter_factory else None
            )
        )

    if get:
        routes.append(
            Route(
                path=f"{base_path}/get",
                method=RouteMethod.POST,
                tag=tag,
                handler=private.get_handler_factory(database_model, root_only=root_only),
                response_model=base_model,
                limits=limiter_factory() if limiter_factory else None
            )
        )

    if find:
        routes.append(
            Route(
                path=f"{base_path}/find",
                method=RouteMethod.POST,
                tag=tag,
                handler=private.find_handler_factory(database_model, root_only=root_only, fetch_dict_disabled=find_fetch_dict_disabled),
                response_model=List[base_model],
                limits=limiter_factory() if limiter_factory else None
            )
        )

    if count:
        routes.append(
            Route(
                path=f"{base_path}/count",
                method=RouteMethod.POST,
                tag=tag,
                handler=private.count_handler_factory(database_model, root_only=root_only),
                response_model=int,
                limits=limiter_factory() if limiter_factory else None
            )
        )

    if count_many:
        routes.append(
            Route(
                path=f"{base_path}/count_many",
                method=RouteMethod.POST,
                tag=tag,
                handler=private.count_multiple_handler_factory(database_model, root_only=root_only),
                response_model=List[int],
                limits=limiter_factory() if limiter_factory else None
            )
        )

    return routes

def public_crud_routes(
        routes: List[Route],
        base_model: Type[T_DatabaseModel],
        database_model: Type[T_DatabaseModel],
        create_model: Type[T_DatabaseModel],
        update_model: Type[T_DatabaseModel],
        base_path: str,
        tag: str,
        *,
        create: bool = True, 
        update: bool = True, 
        update_many: bool = True,
        delete: bool = True, 
        get: bool = True, 
        find: bool = True,
        count: bool = True,
        limiter_factory: Optional[Callable[[], List[ApiLimiter]]] = None
) -> List[Route]:
    if create:
        routes.append(
            Route(
                path=f"{base_path}/create",
                method=RouteMethod.POST,
                tag=tag,
                handler=public.create_handler_factory(create_model, database_model),
                response_model=base_model,
                limits=limiter_factory() if limiter_factory else None
            )
        )

    if update:
        routes.append(
            Route(
                path=f"{base_path}/update",
                method=RouteMethod.POST,
                tag=tag,
                handler=public.update_handler_factory(update_model, database_model),
                response_model=base_model,
                limits=limiter_factory() if limiter_factory else None
            )
        )

    if update_many:
        routes.append(
            Route(
                path=f"{base_path}/update_many",
                method=RouteMethod.POST,
                tag=tag,
                handler=public.update_many_handler_factory(update_model, database_model),
                response_model=List[base_model],
                limits=limiter_factory() if limiter_factory else None
            )
        )

    if delete:
        routes.append(
            Route(
                path=f"{base_path}/delete",
                method=RouteMethod.POST,
                tag=tag,
                handler=public.delete_handler_factory(database_model),
                response_model=uuid.UUID,
                limits=limiter_factory() if limiter_factory else None
            )
        )

    if get:
        routes.append(
            Route(
                path=f"{base_path}/get",
                method=RouteMethod.POST,
                tag=tag,
                handler=public.get_handler_factory(database_model),
                response_model=base_model,
                limits=limiter_factory() if limiter_factory else None
            )
        )

    if find:
        routes.append(
            Route(
                path=f"{base_path}/find",
                method=RouteMethod.POST,
                tag=tag,
                handler=public.find_handler_factory(database_model),
                response_model=List[base_model],
                limits=limiter_factory() if limiter_factory else None
            )
        )

    if count:
        routes.append(
            Route(
                path=f"{base_path}/count",
                method=RouteMethod.POST,
                tag=tag,
                handler=public.count_handler_factory(database_model),
                response_model=int,
                limits=limiter_factory() if limiter_factory else None
            )
        )

    return routes


if __name__ == "__main__": exit()
