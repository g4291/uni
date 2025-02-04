#!/usr/bin/env python3

"""
uni.router

application base router
"""

from __future__ import annotations
from enum import IntEnum, auto
from typing import Any, Callable, List, Optional
from fastapi import FastAPI, Request, Request, Depends, WebSocket
from fastapi.responses import ORJSONResponse

from ..default import UniDefault
from ..handler.base import PublicHandler
from ..logger import color_blue, core_logger
from ..services.request_log import log_public_request
from ..version import API_PREFIX
from ..limiter import ApiLimiter


logger = core_logger().getChild("router")


def rename(name: str):
    """ rename function decorator, used to rename routes """
    def fn(f):
        f.__name__ = name
        return f
    return fn

class RouteMethod(IntEnum):
    GET = auto()
    POST = auto()
    STATIC = auto()

class Route():
    """ Route class"""
    def __init__(
        self, 
        path: str,
        method: RouteMethod,
        handler: Callable[..., Any],
        response_model: Optional[Any] = None,
        response_class: Optional[Any] = ORJSONResponse,
        include_in_schema: bool = True,
        tag: str = "default",
        prefix: str = API_PREFIX,
        limits: Optional[List[ApiLimiter]] = None
    ):
        self.path = path
        self.method = method
        self.handler = handler
        self.path = prefix+path
        self.response_model = response_model
        self.response_class = response_class
        self.include_in_schema = include_in_schema
        self.tag = tag
        self.limits = limits
        self.prefix = prefix

class WebsocketRoute():
    """ Websocket Route class """
    def __init__(
        self,
        path: str,
        handler: Callable[..., Any],
        name: str,
        prefix: str = API_PREFIX,
        limits: Optional[List[ApiLimiter]] = None
    ):
        self.path = path
        self.handler = handler
        self.path = prefix+path
        self.name = name
        self.limits = limits
        self.prefix = prefix

class Router(UniDefault):
    """ Abstract Router class """        
    def __init__(self, fastapi: FastAPI) -> None:
        self._fastapi = fastapi
        self._routes: List[Route] = []

    @property
    def fastapi(self) -> FastAPI:
        return self._fastapi

    @property
    def routes(self) -> List[Route]:
        return self._routes
    
    def get_handler(self, path: str) -> Optional[Callable[..., Any]]:
        """
        Retrieve the handler function for a given path.
        Args:
            path (str): The path to match against the registered routes.
        Returns:
            Optional[Callable[..., Any]]: The handler function if a matching route is found, 
            otherwise None.
        """
        for r in self._routes:
            if r.path == r.prefix+path:
                return r.handler
        return None
    
    def _get_handler_name(self, handler: Any) -> str:
        """ get handler name """
        try:
            handler_name = handler.__self__.__name__
        except AttributeError:
            handler_name = handler.__name__
        except Exception:
            handler_name = "Handler"

        return handler_name

    def _log_request(self, r: Route, request: Request) -> None:
        """ log public request """    
        if hasattr(r.handler, "__self__"):  # type: ignore
            if issubclass(r.handler.__self__, PublicHandler):  # type: ignore
                log_public_request(request)
        else:
            log_public_request(request)

    def _get(self, r: Route) -> None:
        """ creates GET route """
        @self.fastapi.get(
            r.path, 
            response_model=r.response_model, 
            response_class=r.response_class, 
            include_in_schema=r.include_in_schema, 
            tags=[r.tag]
        )
        @rename(self._get_handler_name(r.handler))
        async def route(request: Request, respond: Any = Depends(r.handler)):
            self._log_request(r, request)
            if r.response_class == ORJSONResponse:
                try: return ORJSONResponse(content=respond)
                except: pass
            return respond

        logger.info(color_blue(f"GET route registered: {r.path}"))

    def _post(self, r: Route) -> None:
        """ creates POST route """
        @self.fastapi.post(
            r.path, 
            response_model=r.response_model, 
            response_class=r.response_class, 
            include_in_schema=r.include_in_schema, 
            tags=[r.tag]
        )
        @rename(self._get_handler_name(r.handler))
        async def route(request: Request, respond: Any = Depends(r.handler)):
            self._log_request(r, request)
            if r.response_class == ORJSONResponse:
                try: return ORJSONResponse(content=respond)
                except: pass
            return respond

        logger.info(color_blue(f"POST route registered: {r.path}"))

    def _websocket(self, r: WebsocketRoute) -> None:
        """ creates WEBSOCKET route """
        @self.fastapi.websocket(
                r.path, 
                name=r.name
            )
        @rename(self._get_handler_name(r.handler))
        async def route(websocket: WebSocket):
            logger.debug(f"WEBSOCKET connection: {r.path}")
            await r.handler(websocket)

        logger.info(color_blue(f"WEBSOCKET route registered: {r.path}"))

    def _static(self, r: Route) -> None:
        """ creates STATIC route"""
        self.fastapi.mount(r.path, r.handler(), name=r.path)
        logger.info(color_blue(f"STATIC route registered: {r.path}"))

    def _generate_routes(self) -> list[Route]:
        """ Generate routes"""
        self._routes = sorted(
            self.create_routes(),
            key=lambda x: (x.path, x.method.value)
        )

        static_routes = []

        for route in self._routes:
            if route.method == RouteMethod.GET:
                self._get(route)
            elif route.method == RouteMethod.POST:
                self._post(route)
            elif route.method == RouteMethod.STATIC:
                static_routes.append(route)
            else:
                raise NotImplementedError()
            
            # register API limiters
            if route.limits:
                for l in route.limits:
                    l.register(route.path)

        # static routes must be registered last
        for route in static_routes:
            self._static(route)

    def _generate_ws_routes(self) -> None:
        """ Generate websocket routes """
        ws_routes = self.create_ws_routes()

        for route in ws_routes:
            self._websocket(route)

            # register API limiters
            if route.limits:
                for l in route.limits:
                    l.register(route.path)

    def generate_routes(self) -> None:
        """ Generate routes """
        self._generate_routes()
        self._generate_ws_routes()

    def create_routes(self) -> List[Route]:
        """ Create routes. """
        return []
    
    def create_ws_routes(self) -> List[WebsocketRoute]:
        """ Create websocket routes. """
        return []


if __name__ == "__main__": exit()
