#!/usr/bin/env python3

"""
uni.handler.websocket

application websocket handler
"""

from __future__ import annotations
import asyncio
import json
from typing import Any, Dict, Optional, Tuple, get_type_hints
from fastapi import Request, WebSocket, WebSocketDisconnect, WebSocketException
from pydantic import BaseModel
import pydantic

from ..request_context import get_context
from ..unirequest import UniWebSocketRequest
from ..services.auth import AuthToken, verify_token
from ..utils import timestamp_factory
from ..database import database_factory
from ..default import UniDefault
from ..exceptions import BaseHTTPException, NotFoundError, ServerError, UnauthorizedError, ValidationError
from ..logger import color_green, color_red, core_logger
from ..modules.user.model import db_User


logger = core_logger().getChild("websocket")

# base WebSocket Handler
class WebSocketHandler(UniDefault):
    """
    WebSocketHandler class for managing WebSocket connections and handling messages.
    Attributes:
        _ws (Optional[WebSocket]): The WebSocket connection instance.
        _database: The database instance created by the database factory.
        _running (bool): A flag indicating whether the WebSocket handler is running.
    Methods:
        ws: Property to get the WebSocket connection instance.
        database: Property to get the database instance.
        _on_message(message: str): Abstract method to handle incoming messages. Needs to be overridden.
        _on_connect(ws: WebSocket): Handles WebSocket connection acceptance.
        _on_disconnect(): Handles WebSocket disconnection.
        _on_error(error): Handles errors during WebSocket communication.
        _handler(ws: WebSocket): Main handler for managing WebSocket connection and message processing.
        handler(cls, ws: WebSocket): Class method to create an instance and start the WebSocket handler.
    """
    def __init__(self):
        self._ws: Optional[WebSocket] = None
        self._database = database_factory()
        self._running = True
        self._request: Optional[UniWebSocketRequest] = None
        self._ctx_tokens: Dict[UniWebSocketRequest, Any] = {}

    def _set_context(self, request: UniWebSocketRequest) -> None:
        """
        Sets the context for the given request.
        This method associates the provided `request` with a context token 
        and stores it in the `_ctx_tokens` dictionary.
        Args:
            request (UniRequest): The request object for which the context is to be set.
        """
        self._ctx_tokens[request] = get_context().set(request)

    def _reset_context(self, request: UniWebSocketRequest) -> None:
        """
        Resets the context for the given request.
        This method attempts to pop the context token associated with the provided
        request from the internal context tokens dictionary. If a token is found,
        it resets the context using that token. If no token is found, it logs an
        error message indicating the failure to reset the context.
        Args:
            request (UniWebSocketRequest): The request for which the context needs to be reset.
        """
        token = self._ctx_tokens.pop(request, None)
        if token:
            get_context().reset(token)
            return
        
        logger.error(color_red(f"Failed to reset context for request: {request}"))

    @property
    def ws(self):
        return self._ws
    
    @property
    def database(self):
        return self._database
    
    @property
    def message_model(self) -> BaseModel:
        cls =  get_type_hints(self.on_message).get("message", None)
        if not cls:
            raise ValidationError("on_message method must have a message argument")
        return cls
    
    def on_message(self, message: BaseModel) -> None:
        """
        Handle incoming WebSocket messages.
        This method should be overridden by subclasses to define custom behavior
        for processing incoming WebSocket messages.
        Args:
            message (BaseModel): The incoming WebSocket message.
        Raises:
            NotImplementedError: If the method is not overridden by a subclass.
        """
        raise NotImplementedError("on_message not implemented, needs to be overridden")
    
    def on_error(self, error: BaseHTTPException) -> None:
        """
        Handles errors that occur during WebSocket communication.
        Args:
            error (BaseHTTPException): The exception that was raised.
        Returns:
            None
        """
        return None
    
    def on_disconnect(self) -> None:
        """
        Handle the disconnection event for the websocket.
        This method is called when the websocket connection is closed.
        It performs any necessary cleanup or state updates related to the disconnection.
        Returns:
            None
        """
        return None
    
    def send(self, message: BaseModel):
        """
        Sends a message through the websocket connection.

        Args:
            message (BaseModel): The message to be sent. Must be an instance of BaseModel.

        Raises:
            ValidationError: If the message is not an instance of BaseModel.
            ServerError: If the websocket is not connected.
        """
        if not isinstance(message, BaseModel):
            raise ValidationError("message must be an instance of BaseModel")
        if not self._ws:
            raise ServerError("websocket not connected")
        asyncio.run(self._ws.send_text(json.dumps(message.dict())))
    
    async def _on_message(self, message: str):
        """
        Handle incoming WebSocket messages.
        This method should be overridden by subclasses to define custom behavior
        when a message is received.
        Args:
            message (str): The message received from the WebSocket connection.
        Raises:
            NotImplementedError: If the method is not overridden by a subclass.
        """
        raise NotImplementedError("on_message not implemented, needs to be overridden")

    async def _on_connect(self, ws: WebSocket):
        """
        Handles the WebSocket connection event.
        This method is called when a new WebSocket connection is established.
        It accepts the WebSocket connection and logs a debug message indicating
        that the connection has been established.
        Args:
            ws (WebSocket): The WebSocket connection instance.
        """
        await ws.accept()
        self._ws = ws

    async def _ws_error(self, err: BaseHTTPException):
        """
        Handles errors that occur during the WebSocket connection.
        Args:
            err (BaseHTTPException): The error that occurred.
        Raises:
            WebSocketException: If the error is an instance of BaseHTTPException.
        """
        if self.ws:
            await asyncio.to_thread(self.on_error, err)
            raise WebSocketException(code=4000+err.status_code, reason=err.detail) from None
        else: raise err

    async def _on_disconnect(self):
        """
        Handles the disconnection of the websocket.
        This method is called when the websocket is disconnected. It logs the disconnection event
        and sets the running flag to False to indicate that the websocket is no longer active.
        """
        logger.debug("websocket disconnected")
        await asyncio.to_thread(self.on_disconnect)
        if self._request:
            self._request.done()
            logger.info(color_green(f"WebSocket connection took {self._request.done()}ms, path: {self._request.path}"))

            self._reset_context(self._request)
        self._running = False

    async def _on_error(self, error):
        """
        Handles errors that occur during the websocket connection.
        Args:
            error (Exception): The error that occurred.
        Raises:
            BaseHTTPException: If the error is an instance of BaseHTTPException.
            ServerError: If any other error occurs.
        """
        self._running = False
        if isinstance(error, BaseHTTPException):
            await self._ws_error(error)

        # websocket disconnect, nothing to do
        if isinstance(error, WebSocketDisconnect):
            return 
        
        # pydantic validation errors
        if isinstance(error, pydantic.ValidationError):
            for e in error.errors():
                # private message, missing token
                if "token" in e["loc"] and "value_error.missing" in e["type"]:
                    await self._ws_error(
                        UnauthorizedError("invalid token")
                    )
                logger.error(f"validation error: {e}")
            
            await self._ws_error(
                ValidationError("invalid message")
            )
                
        # other errors
        logger.error(f"websocket error: {error}, {error.__class__.__name__}")
        await self._ws_error(
            ServerError("websocket error")
        )

    async def _handler(self, ws: WebSocket):
        """
        Handles the WebSocket connection.
        This coroutine manages the lifecycle of a WebSocket connection. It first
        calls the `_on_connect` method when a connection is established. Then, it
        enters a loop where it continuously receives messages from the WebSocket
        and processes them using the `_on_message` method. If an exception occurs,
        it calls the `_on_error` method. Finally, it ensures that the `_on_disconnect`
        method is called when the connection is closed.
        Args:
            ws (WebSocket): The WebSocket connection instance.
        Raises:
            Exception: If an error occurs during message processing.
        """
        await self._on_connect(ws)
        try:
            while self._running:
                data = await ws.receive_text()
                await self._on_message(data)
        except Exception as e:
            await self._on_error(e)
        finally:
            await self._on_disconnect()

    @classmethod
    async def handler(cls, ws: WebSocket):
        """
        Asynchronous handler for WebSocket connections.
        Args:
            ws (WebSocket): The WebSocket connection instance.
        Returns:
            The result of the internal _handler method.
        """
        return await cls()._handler(ws)
    

# Public WebSocket Handler
class WebSocketPublicHandler(WebSocketHandler):
    """
    WebSocketPublicHandler is a handler for managing WebSocket connections and processing
    public messages received over the WebSocket.
    Methods:
        __init__(): Initializes the WebSocketPublicHandler instance.
        _on_message(message: str): Asynchronously processes incoming WebSocket messages.
        on_message(message: WebSocketPublicMessage): Abstract method to handle parsed WebSocket messages.
    """
    def __init__(self):
        super().__init__()

    async def _on_message(self, message: str):
        """
        Handles incoming WebSocket messages.
        Args:
            message (str): The incoming message as a JSON-encoded string.
        Raises:
            ValidationError: If the incoming message is not valid JSON.
        Logs:
            Logs the received message and any JSON decoding errors.
        """
        logger.info(f"message received: {message}")
        try:
            _json = json.loads(message)
        except json.JSONDecodeError as e:
            logger.error(f"json decode error: {e}")
            raise ValidationError("invalid json")
        ws_msg = self.message_model(**_json)

        if not self._request:
            self._request = UniWebSocketRequest(self._ws, None)
            logger.info(color_green(str(self._request)))
            self._set_context(self._request)
        
        await asyncio.to_thread(self.on_message, ws_msg)

# Private WebSocket Handler
class WebSocketPrivateHandler(WebSocketHandler):
    """
    WebSocketPrivateHandler is a handler for managing private WebSocket connections.
    Attributes:
        _user (Optional[db_User]): The authenticated user associated with the WebSocket connection.
        _initialized (bool): Indicates whether the WebSocket connection has been initialized.
    Methods:
        initialized: Returns whether the WebSocket connection has been initialized.
        user: Returns the authenticated user associated with the WebSocket connection.
        _process_token(auth: Tuple[AuthToken, Request]) -> None: Processes the authentication token and retrieves the authorized user.
        _on_message(message: str): Handles incoming WebSocket messages.
        on_message(message: WebSocketPrivateMessage): Abstract method to be overridden for handling WebSocket messages.
    """
    def __init__(self):
        super().__init__()
        self._user: Optional[db_User] = None
        self._initialized = False

    @property
    def initialized(self):
        return self._initialized

    @property
    def user(self):
        if not self._user:
            raise UnauthorizedError("user not logged in")
        return self._user
    
    async def _process_token(self, auth: Tuple[AuthToken, Request]) -> None:
        """
        Process the authentication token and update the user's last login timestamp.
        Args:
            auth (Tuple[AuthToken, Request]): A tuple containing the authentication token and the request.
        Raises:
            NotFoundError: If the user associated with the token is not found in the database.
        Side Effects:
            Updates the user's last login timestamp in the database.
            Sets the user and request attributes for the instance.
        """        
        self._auth = auth
        token, request = auth

        user = self.database.get_one(token._user_id, db_User)
        if not user:
            raise NotFoundError("user not found")

        #update user last login
        user.last_login = timestamp_factory()
        self.database.update(user)

        user.request = request
        self._user = user

    async def _on_message(self, message: str):
        """
        Handles incoming WebSocket messages.
        Args:
            message (str): The message received from the WebSocket connection.
        Raises:
            ValidationError: If the message is not a valid JSON.
        Logs:
            Logs the received message and any JSON decoding errors.
        Workflow:
            1. Logs the received message.
            2. Attempts to decode the message as JSON.
            3. If decoding fails, logs the error and raises a ValidationError.
            4. Converts the JSON message to a message_model instance.
            5. If the connection is not initialized, verifies the token and processes it.
            6. Marks the connection as initialized.
            7. Processes the message in a separate thread.
        """
        logger.info(f"message received: {message}")
        try:
            _json = json.loads(message)
        except json.JSONDecodeError as e:
            logger.error(f"json decode error: {e}")
            raise ValidationError("invalid json")
        
        try:
            token: str = _json["token"]
            if not token:
                raise UnauthorizedError("token not provided")
        except Exception:
            raise UnauthorizedError("token not provided")
        
        ws_msg = self.message_model(**_json)

        # initialize request
        if not self._request:
            self._request = UniWebSocketRequest(self.ws, token)
            logger.info(color_green(str(self._request)))
            self._set_context(self._request)

        if not self._initialized:
            auth = verify_token(self.ws, token)
            await self._process_token(auth)
            self._initialized = True

        await asyncio.to_thread(self.on_message, ws_msg)


if __name__ == "__main__": exit()    