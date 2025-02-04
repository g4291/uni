#!/usr/bin/env python3

import threading
import time
import ctypes
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Type
import time

from .exceptions import ServerError
from .logger import core_logger


logger = core_logger().getChild("context")

_ctx_subscribers = dict()


# Custom context exceptions
class ContextCancelledError(ServerError):
    """ cancel exception """
class ContextTimeoutError(ServerError):
    """ timeout exception """
class SubscriberNotUnique(ServerError):
    """ subscriber id not unique exception """


def _subscribe_context_cancel(id: str, handler: callable):
    """
    Subscribes a handler to a context cancellation event.

    Args:
        id (str): The unique identifier for the subscriber.
        handler (callable): The function to be called when the context is cancelled.

    Raises:
        SubscriberNotUnique: If a subscriber with the given id already exists.

    Logs:
        Debug: Logs the addition of a new `cancel` subscriber with its id and handler.
    """
    if _ctx_subscribers.get(id, None): raise SubscriberNotUnique(f"subscriber no unique, id: {id}")
    _ctx_subscribers[id] = handler
    logger.debug(f"`cancel` subscriber added: {id}, {handler}")

def _unsubscribe_context_cancel(id: str):
    """
    Unsubscribes and removes a context subscriber by its ID.
    Args:
        id (str): The unique identifier of the context subscriber to be removed.
    Returns:
        None
    """
    if not _ctx_subscribers.get(id, None): return
    del _ctx_subscribers[id]
    logger.debug(f"`cancel` subscriber removed: {id}")

def cancel_context(id: str):
    """
    Cancels the context associated with the given ID by invoking the corresponding handler.
    Args:
        id (str): The unique identifier for the context to be canceled.
    Returns:
        None
    """
    handler = _ctx_subscribers.get(id, None)
    if handler: handler()


class AbstractContext(ABC):
    """
    Abstract base class for context management with thread termination capabilities.
    Attributes:
        _thread_id (int): Identifier of the thread associated with this instance.
        _suppress (bool): Flag indicating whether to suppress exceptions.
    Methods:
        __enter__():
            Abstract method to be implemented by subclasses for entering the context.
        __exit__(exc_type, exc_val, traceback):
            Abstract method to be implemented by subclasses for exiting the context.
        _kill(error: Type):
    """
    def __init__(self, suppress: bool = False):
        self._thread_id = threading.current_thread().ident
        self._suppress = bool(suppress)

    def _kill(self, error: Type):
        """
        Terminates the thread associated with this instance by raising the specified exception.
        Args:
            error (Type): The exception type to be raised in the thread.
        Raises:
            RuntimeError: If the thread could not be terminated.
        """
        logger.debug(f"killing thread: {self._thread_id}")
        r = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self._thread_id), ctypes.py_object(error))
        if r != 1:
            logger.error(f"error killing thread, {self._thread_id}")

    @abstractmethod
    def __enter__(self):
        """ abstract """

    @abstractmethod
    def __exit__(self, exc_type, exc_val, traceback):
        """ abstract """
        
class ContextWithCancel(AbstractContext):
    """
    A context manager class that provides a mechanism to cancel the context and handle exceptions.
    Attributes:
        _id (str): The unique identifier for the context.
        _suppress (bool): A flag to suppress the ContextCancelledError.
    Methods:
        __init__(id: str, suppress: bool = False):
            Initializes the context with a unique identifier and an optional suppress flag.
        cancel():
            Cancels the context by raising a ContextCancelledError.
        __enter__():
            Enters the runtime context and subscribes to the context cancel event.
        __exit__(exc_type, exc_val, traceback):
            Exits the runtime context, unsubscribes from the context cancel event, and handles exceptions.
    """
    def __init__(self, id: str, supress: bool = False):
        super().__init__(suppress=supress)
        self._id = id

    def cancel(self):
        """
        Cancels the current context by raising a ContextCancelledError.
        This method is used to terminate the current context and signal that
        it has been cancelled. It raises a ContextCancelledError to indicate
        the cancellation.
        """
        self._kill(ContextCancelledError)

    def __enter__(self):
        """
        Enter the runtime context related to this object.
        This method is called when the execution flow enters the context of the 
        `with` statement. It subscribes the context cancel function to the 
        context manager's ID.
        Returns:
            self: The context manager instance.
        """
        _subscribe_context_cancel(self._id, self.cancel)
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        """
        Exit the runtime context related to this object.
        Parameters:
        exc_type (type): The exception type, if an exception was raised.
        exc_val (Exception): The exception instance, if an exception was raised.
        traceback (traceback): The traceback object, if an exception was raised.
        Returns:
        bool: True if the exception is suppressed, False otherwise.
        """
        _unsubscribe_context_cancel(self._id)

        # suppress
        if self._suppress and exc_type == ContextCancelledError:
            logger.info("context cancelled")
            return True

        # log exception
        if exc_type:
            logger.error(f"context exception, {exc_type}, {exc_val}")


class ContextWithTimeout(AbstractContext):
    """
    Context manager that enforces a timeout for a block of code.
    Attributes:
        _timeout (float): The duration in seconds after which the context should timeout.
        _ts (float): The timestamp when the context was entered.
        _running (bool): A flag indicating whether the context is currently running.
        _timeout_thread (threading.Thread): The thread responsible for monitoring the timeout.
        _suppress_exceptions (Optional[List[Any]]): A list of exception types to suppress.
        timeout (float): The duration in seconds after which the context should timeout.
        suppress (bool): Whether to suppress exceptions specified in `suppress_exceptions`.
        suppress_exceptions (Optional[List[Any]]): A list of exception types to suppress.
    Methods:
        _timer(timeout: float): Starts a timer thread that monitors the elapsed time and triggers a timeout action.
        __enter__(): Enters the runtime context and starts the timer if a timeout is specified.
        __exit__(exc_type, exc_val, traceback): Exits the runtime context, stops the timer, and handles exceptions.
    """
    def __init__(self, timeout: float, suppress: bool = False, suppress_exceptions: Optional[List[Any]] = None):
        super().__init__(suppress)
        self._timeout = float(timeout)
        self._ts = time.time()
        self._running = True
        self._timeout_thread = None
        
        self._suppress_exceptions = suppress_exceptions
        if not self._suppress_exceptions:
            self._suppress_exceptions = []

    def _timer(self, timeout: float):
        """
        Starts a timer thread that monitors the elapsed time and triggers a timeout action.
        Args:
            timeout (float): The duration in seconds after which the timer should trigger the timeout action.
        The timer function runs in a separate thread and continuously checks if the specified timeout
        duration has passed. If the timeout duration is exceeded, it calls the `_kill` method with
        `ContextTimeoutError` to handle the timeout event.
        """
        def timer():
            while self._running:
                if time.time() > (self._ts + timeout):
                    self._kill(ContextTimeoutError)
                    break

        self._timeout_thread = threading.Thread(target=timer)
        self._timeout_thread.start()

    def __enter__(self):
        """
        Enter the runtime context related to this object.
        If a timeout is set (greater than 0), a timer is started with the specified timeout value.
        Returns:
            self: The context manager instance.
        """
        if self._timeout > 0:
            self._timer(self._timeout)
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        """
        Handles the exit of the context manager.
        This method is called when the context manager is exited. It performs
        cleanup operations, such as stopping the timeout thread and handling
        exceptions.
        Parameters:
        exc_type (type): The exception type, if an exception was raised.
        exc_val (Exception): The exception instance, if an exception was raised.
        traceback (traceback): The traceback object, if an exception was raised.
        Returns:
        bool: True if the exception should be suppressed, False otherwise.
        """
        self._running = False
        if self._timeout_thread: self._timeout_thread.join()

        # suppress        
        _suppress_types = [ContextTimeoutError]
        for e in self._suppress_exceptions:
            _suppress_types.append(e)

        if self._suppress and exc_type in _suppress_types:
            logger.info("context timeout")
            return True

        # log exception
        if exc_type:
            logger.error(f"context exception, {exc_type}, {exc_val}")


if __name__ == "__main__": exit()    