#!/usr/bin/env python3

"""
uni.application

Uni-backend main Application
"""

from __future__ import annotations
import os
from typing import Any, Callable, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .middleware import middleware_factory
from .default import UniDefault
from .version import RUN_ID, VERSION
from .config import ApplicationConfig, Config
from .logger import color_blue, core_logger, disable_logger
from .database import database_factory
# imports, depends on ApplicationConfig.config
from .modules import modules_init as core_modules_init
from modules import modules_init as user_modules_init
from .router import router_factory, Router
from .eventsourcing import init as es_init

from init import init



logger = core_logger().getChild("application")


class UniBackend(UniDefault):
    """
    UniBackend is a singleton class that initializes and manages the backend of the Uni application.
    It extends the UniDefault class and provides methods to set up configurations, directories,
    logging, FastAPI application, core and user modules, routes, middlewares, and database connections.

    Attributes:
        __instance_cache (list): A cache to store the singleton instance of UniBackend.
    
    Methods:
        get_instance() -> UniBackend:
        __init__(config: Config) -> None:
            Initialize the UniBackend instance with the provided configuration.
        _directories_init() -> None:
            Initialize the necessary directories for the application.
        _db_test() -> None:
            Test the database connection.
        _fast_api_init() -> None:
            Initialize the FastAPI application instance with the specified configuration.
        _init_cors() -> None:
            Initialize CORS middleware for the FastAPI application.
        _generate_routes() -> None:
        internal_get_handler(endpoint: str) -> Optional[Callable[..., Any]]:
        _add_middlewares() -> None:
            Add all middlewares to the FastAPI application.
        __call__(scope, receive, send) -> None:
        fastapi() -> FastAPI:
            Return the FastAPI object.
    """
    __instance_cache = []

    @staticmethod
    def get_instance() -> UniBackend:
        """
        Retrieve the singleton instance of UniBackend.

        Returns:
            UniBackend: The singleton instance of the UniBackend class.
        """
        return UniBackend.__instance_cache[0]

    def __init__(self, config: Config) -> None:

        # config init
        ApplicationConfig.config = config

        self._run_id = RUN_ID
        
        # directories
        self._directories_init()

        # uni log
        if not self.config.log_uni_core:
            disable_logger("uni.core")

        # Fast API init
        self._fast_api_init()

        # init core modules
        core_modules_init()

        # init user modules
        user_modules_init()

        # Routes
        self._routers = router_factory()
        self._router_instances: List[Router] = []
        self._generate_routes()
        
        # middlewares
        self._middlewares = middleware_factory()
        self._add_middlewares()
        self._init_cors()
        
        # inti es
        es_init()


        # database test
        self._db_test()
        
        # user init
        logger.info(color_blue(f"Calling user init.init() function"))
        init()

        # Done
        logger.info(color_blue(f"{self.__class__.__name__} init done, version: {VERSION}"))
        if len(UniBackend.__instance_cache) != 0:
            logger.critical("UniBackend instance already exists")
        UniBackend.__instance_cache.append(self)
        
    def _directories_init(self) -> None:
        """
        Initializes the necessary directories for the application.
        This method creates the directories specified in the configuration
        for database exports and temporary files if they do not already exist.

        Raises:
            OSError: If the directories cannot be created.
        """
        os.makedirs(self.config.database_export_directory, exist_ok=True)
        os.makedirs(self.config.tmp_directory, exist_ok=True)

    def _db_test(self) -> None:
        """
        Tests the database connection by invoking the database factory function.
        This method is intended to ensure that the database connection can be
        established successfully. It does not return any value.
        """
        database_factory()

    def _fast_api_init(self) -> None:
        """
        Initializes the FastAPI application instance with the specified configuration.
        This method sets up the FastAPI instance with the following parameters:
        - `redoc_url`: Disabled by setting it to None.
        - `docs_url`: URL for the API documentation, as specified in the configuration.
        - `debug`: Debug mode is enabled if the application is not in production.
        - `version`: The version of the application.
        - `title`: The name of the application.
        - `description`: The description of the application.
        """
        self._fastapi = FastAPI(
            redoc_url=None,
            docs_url=self.config.doc_url,
            debug=(not self.config.production),
            version=VERSION,
            title=self.config.app_name,
            description=self.config.description
        )

    def _init_cors(self) -> None:
        """
        Initialize CORS (Cross-Origin Resource Sharing) middleware for the FastAPI application.

        This method configures the CORS settings for the FastAPI application by adding the
        CORSMiddleware with the specified origins, credentials, methods, and headers.

        The CORS settings are retrieved from the application's configuration.

        Returns:
            None
        """
        self._fastapi.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.security_cors_origins,
            allow_credentials=True,
            allow_methods=self.config.security_cors_methods,
            allow_headers=["*"],
        )

    def _generate_routes(self) -> None: 
        """
        Generate API routes by iterating over the list of routers.

        This method creates instances of each router, generates their routes,
        and appends the instances to the list of router instances. It also logs
        the registration of each router.

        Returns:
            None
        """
        for router in self._routers:
            # create router
            logger.info(color_blue(f"Router registered: {router.__module__}.{router.__name__}"))
            _r = router(self._fastapi)
            _r.generate_routes()
            self._router_instances.append(_r)

    def internal_get_handler(self, endpoint: str)-> Optional[Callable[..., Any]]:
        """
        Retrieve the handler function for a given endpoint.
        This method iterates through the router instances to find a handler
        function that matches the specified endpoint. If a handler is found,
        it is returned; otherwise, None is returned.

        Args:
            endpoint (str): The endpoint for which to retrieve the handler.

        Returns:
            Optional[Callable[..., Any]]: The handler function if found, otherwise None.
        """
        for router in self._router_instances:
            handler = router.get_handler(endpoint)
            if handler: return handler      
        return None 
            
    def _add_middlewares(self) -> None:
        """
        Adds all middlewares to the FastAPI application.
        This method iterates over the list of middlewares and adds each one to the FastAPI application instance.
        It also logs the addition of each middleware with its corresponding path.
        
        Returns:
            None
        """
        for mw in self._middlewares:
            logger.info(color_blue(f"Adding middleware: {mw}, path: {mw.path}"))
            mw.add(self.fastapi)

    async def __call__(self, scope, receive, send) -> None:
        """
        Asynchronous callable method to handle ASGI requests.
        This method allows the instance to be called as an ASGI application.
        It delegates the handling of the request to the FastAPI application.

        Args:
            scope (dict): The scope of the ASGI connection, containing details 
                          about the request such as type, path, headers, etc.
            receive (callable): An awaitable callable that will yield events 
                                related to the request.
            send (callable): An awaitable callable that will be used to send 
                             events related to the response.

        Returns:
            None
        """
        await self.fastapi(scope, receive, send)

    @property
    def fastapi(self) -> FastAPI:
        """ Returns FastAPI object """
        return self._fastapi
    
# disable 3rd party loggers
disable_logger("botocore.parsers")
disable_logger("botocore.hooks")
disable_logger("botocore.retryhandler")
disable_logger("botocore.auth")
disable_logger("botocore.utils")
disable_logger("botocore.client")
disable_logger("botocore.configprovider")
disable_logger("botocore.loaders")
disable_logger("botocore.endpoint")
disable_logger("botocore.regions")
disable_logger("botocore.httpsession")
disable_logger("botocore.handlers")
disable_logger("botocore.awsrequest")
disable_logger("boto3.s3.transfer")
disable_logger("s3transfer.utils")
disable_logger("s3transfer.futures")
disable_logger("s3transfer.tasks")
disable_logger("urllib3.util.retry")
disable_logger("urllib3.connectionpool")
disable_logger("multipart.multipart")
disable_logger("httpx")
disable_logger("httpcore.connection")
disable_logger("httpcore.http11")
disable_logger("PIL.TiffImagePlugin")
disable_logger("PIL.PngImagePlugin")
disable_logger("asyncio")
        

if __name__ == '__main__': exit()