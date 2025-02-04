#!/usr/bin/env python3

"""
uni.exceptions
"""

from __future__ import annotations
from typing import Optional
from fastapi import HTTPException
import traceback
import colorama  # type: ignore

from .logger import exception_logger


logger = exception_logger()


class BaseHTTPException(HTTPException):
    """ Base ApplicationException """

    def __init__(self, detail: str, status_code: int) -> None:
        # get call stack
        stack = "\n ==============================================================\n"
        for i in list(traceback.format_stack())[:-2]:
            stack += f"{i}"
        stack += " =============================================================="
        logger.error(f"{colorama.Fore.RED}EXCEPTION: {self.__class__.__name__}, code: {status_code}, detail: {detail}, stack: {colorama.Fore.BLUE}{stack}{colorama.Style.RESET_ALL}")
        
        super().__init__(
            status_code=status_code,
            detail=detail
        )

    @property
    def name(self) -> str:
        if hasattr(self, "_name"):
            return self._name
        else:
            return self.__class__.__name__
        
class UnauthorizedError(BaseHTTPException):
    """ Unauthorized exception"""
    def __init__(self, msg: str, status_code: int = 401) -> None:
        self._name = "Unauthorized"
        super().__init__(
            status_code=status_code,
            detail=msg
        )

class InvalidCredentialsError(UnauthorizedError):
    """ Invalid user exception"""
    def __init__(self, msg: Optional[str] = None) -> None:
        self._name = "Invalid credentials"
        if not msg:
            msg = "provided credentials are not valid"
        super().__init__(msg)

class ForbiddenError(BaseHTTPException):
    """ Forbidden exception"""
    def __init__(self, msg: str, status_code: int = 403) -> None:
        self._name = "Forbidden"
        super().__init__(
            status_code=status_code,
            detail=msg
        )

class NotFoundError(BaseHTTPException):
    """ Internal server exception """
    def __init__(self, msg: str, status_code: int = 404) -> None:
        self._name = "Not found"
        super().__init__(
            status_code=status_code,
            detail=msg
        )

class ServerError(BaseHTTPException):
    """ Internal server exception """
    def __init__(self, msg: str, status_code: int = 500) -> None:
        self._name = "Internal server error"
        super().__init__(
            status_code=status_code,
            detail=msg
        )

class ValidationError(BaseHTTPException):
    """ validation exception """
    def __init__(self, msg: str, status_code: int = 422) -> None:
        self._name = "Validation error"
        super().__init__(
            status_code=status_code,
            detail=msg
        )

class TooManyRequests(BaseHTTPException):
    """ too many requests exception """
    def __init__(self, msg: str, status_code: int = 429) -> None:
        self._name = "Too many requests"
        super().__init__(
            status_code=status_code,
            detail=msg
        )

class TestError(BaseHTTPException):
    """ Test error """
    def __init__(self, msg: str, status_code: int = 500) -> None:
        self._name = "Test error"
        super().__init__(
            status_code=status_code,
            detail=msg
        )


if __name__ == '__main__': exit()