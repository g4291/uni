#!/usr/bin/env python
"""
uni package
"""

from .version import (
    VERSION,
    API_PREFIX,
    RUN_ID
)
from .config import (
    ApplicationConfig,
    get_config,
    get_custom_config
)
from .exceptions import (
    BaseHTTPException,
    ServerError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    TooManyRequests,
    InvalidCredentialsError,
    ValidationError,
    TestError
)
from .default import UniDefault
from .default import thread_wait
from .unirequest import (
    UniRequest,
    UniWebSocketRequest
)
from .with_request import UniWithRequest
from .request_context import (
    get_current_request
)
from .logger import (
    core_logger,
    logger_factory,
    log_call,
    disable_logger,
    color_blue,
    color_green,
    color_red,
    color_yellow,
    color_cyan,
    color_grey
)
from .encoders import (
    UniJsonDecoder,
    UniJsonEncoder
)
from .lock import UniLock
from .testing import AppTesting
from .sharing import ModelWithSharing
from .database import (
    database_factory,
    database_dependency,
    register_db_model,
    Database,
    DbParams,
    DbResult,
    DbOrder
)
from .database.model import (
    DatabaseModel,
    DatabaseUpdateModel
)
from .cache import CacheInDatabase
from .services import (
    permission,
    auth,
    mail,
)
from uni.services.auth import (
    auth_dependency,
    AuthToken,
    system_auth,
)
from .background_task import (
    BackgroundTask,
    BackgroundTaskInfo
)
from .router import (
    Router,
    Route,
    RouteMethod,
    register_router
)
from .router.crud import (
    private_crud_routes,
    public_crud_routes
)
from .events import (
    register_event_subscriber,
    remove_event_subscriber
)
from .events.base import (
    Event,
    EventAPIRequest,
    EventSuccessLogin,
    EventBadLogin,
    EventCreated,
    EventDeleted,
    EventUpdated,
)
from .events.crud import (
    EventPreCreate,
    EventPostCreate,
    EventPreUpdate,
    EventPostUpdate,
    EventPreDelete,
    EventPostDelete,
    EventPreGetOne,
    EventPostGetOne,
    EventFind, 
    EventCount
)

from .eventsourcing.base import register_es_model
from .filestorage import UniFileStorageFactory

from .handler import (
    PublicHandler,
    PrivateHandler,
)
from .handler.crud import (
    private as private_crud_handler,
    public as public_crud_handler
)
from .handler.websocket import (
    WebSocketPrivateHandler,
    WebSocketPublicHandler
)
from .handler.base import (
    static_handler,
    redirect_handler
)
from .limiter import (
    ApiLimiter,
    ApiLimiterType
)
from .application import UniBackend
from .api import get_api_handler
from .modules.file.model import (
    File,
    db_File,
    UniUploadFile
)
from .modules.file.handler import (
    PrivateFileHandler,
    PublicFileHandler
)
from .modules.user.model import (
    User, db_User
)
from .modules.notification.model import (
    Notification,
    db_Notification
)
from . import utils

__all__ = [
    "VERSION",
    "API_PREFIX",
    "RUN_ID",
    "ApplicationConfig",
    "get_config",
    "get_custom_config",
    "BaseHTTPException",
    "ServerError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "TooManyRequests",
    "InvalidCredentialsError",
    "ValidationError",
    "TestError",
    "UniDefault",
    "thread_wait",
    "UniRequest",
    "UniWebSocketRequest",
    "UniWithRequest",
    "get_current_request",
    "core_logger",
    "logger_factory",
    "log_call",
    "disable_logger",
    "color_blue",
    "color_green",
    "color_red",
    "color_yellow",
    "color_cyan",
    "color_grey",
    "UniJsonDecoder",
    "UniJsonEncoder",
    "UniLock",
    "AppTesting",
    "ModelWithSharing",
    "database_factory",
    "database_dependency",
    "register_db_model",
    "Database",
    "DbParams",
    "DbResult",
    "DbOrder",
    "DatabaseModel",
    "DatabaseUpdateModel",
    "CacheInDatabase",
    "permission",
    "auth",
    "mail",
    "auth_dependency",
    "AuthToken",
    "system_auth",
    "BackgroundTask",
    "BackgroundTaskInfo",
    "Router",
    "Route",
    "RouteMethod",
    "register_router",
    "private_crud_routes",
    "public_crud_routes",
    "register_event_subscriber",
    "remove_event_subscriber",
    "Event",
    "EventAPIRequest",
    "EventSuccessLogin",
    "EventBadLogin",
    "EventCreated",
    "EventDeleted",
    "EventUpdated",
    "EventPreCreate",
    "EventPostCreate",
    "EventPreUpdate",
    "EventPostUpdate",
    "EventPreDelete",
    "EventPostDelete",
    "EventPreGetOne",
    "EventPostGetOne",
    "EventFind",
    "EventCount",
    "register_es_model",
    "UniFileStorageFactory",
    "PublicHandler",
    "PrivateHandler",
    "private_crud_handler",
    "public_crud_handler",
    "WebSocketPrivateHandler",
    "WebSocketPublicHandler",
    "static_handler",
    "redirect_handler",
    "ApiLimiter",
    "ApiLimiterType",
    "UniBackend",
    "get_api_handler",
    "File",
    "db_File",
    "UniUploadFile",
    "PrivateFileHandler",
    "PublicFileHandler",
    "User",
    "db_User",
    "Notification",
    "db_Notification",
    "utils"
]