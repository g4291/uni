#!/usr/bin/env python3

"""
uni.logger

application logger
"""

from __future__ import annotations
import functools
import inspect
import logging
import time
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar
import colorama

from .config import get_config


def disable_logger(name: str) -> None:
    """ disable logger by name"""
    logging.getLogger(name).disabled = True

def disable_uvicorn_logger() -> None:
    """ disable uvicor logger """
    disable_logger("uvicorn.error")
    disable_logger("uvicorn.access")
    
def set_logging_dev(debug: bool = True) -> None:
    """ Set debug logging """
    _format = color_cyan('[%(asctime)s]\t[%(levelname)s]\t[%(name)s]\t[%(pathname)s:%(lineno)s]:')
    
    _end = color_cyan("----------------------------------------------------------------------")
    logging.basicConfig(
        format=_format + "\n\t%(message)s\n" + _end,
        level=logging.DEBUG if debug else logging.INFO
    )

def set_logging_production() -> None:
    """ Set debug logging """
    _format = color_cyan('[%(asctime)s]\t[%(levelname)s]\t[%(name)s]\t[%(pathname)s:%(lineno)s]:')
    
    _end = color_cyan("----------------------------------------------------------------------")
    logging.basicConfig(
        format=_format + "\n\t%(message)s\n" + _end,
        level=logging.INFO
    )

def logger_factory(name: str = "uni") -> logging.Logger:
    """ Retrurns application logger object """

    return logging.getLogger(name)

def core_logger() -> logging.Logger:
    """ Returns application core logger """
    return logger_factory("uni.core")

def exception_logger() -> logging.Logger:
    """ Returns application core logger """
    return logger_factory("uni.exceptions")

def color_red(input: str) -> str:
    return colorama.Fore.RED + input + colorama.Style.RESET_ALL

def color_blue(input: str) -> str:
    return colorama.Fore.BLUE + input + colorama.Style.RESET_ALL

def color_green(input: str) -> str:
    return colorama.Fore.GREEN + input + colorama.Style.RESET_ALL

def color_yellow(input: str) -> str:
    return colorama.Fore.YELLOW + input + colorama.Style.RESET_ALL

def color_cyan(input: str) -> str:
    return colorama.Fore.LIGHTCYAN_EX + input + colorama.Style.RESET_ALL

def color_grey(input: str) -> str:
    return colorama.Fore.LIGHTBLACK_EX + input + colorama.Style.RESET_ALL

def color_magenta(input: str) -> str:  
    return colorama.Fore.MAGENTA + input + colorama.Style.RESET_ALL

# Create a type variable that can be any type of Callable
F = TypeVar('F', bound=Callable[..., Any])

def log_call(logger: Optional[logging.Logger] = None, info: bool = False, args_values: bool = True, return_value: bool = True) -> Callable[[F], F]:
    """
    A decorator to log function calls, their arguments, return values, and execution time.
    Parameters:
        logger (Optional[logging.Logger]): The logger instance to use for logging. If not provided, the core logger is used.
        info (bool): If True, logs at the info level; otherwise, logs at the debug level.
    Returns:
        Callable[[F], F]: A decorator that logs the function call details.
    The decorator logs the following details:
        - Function name (including class name if it's a method)
        - File name and line number where the function is called
        - Arguments and their types
        - Keyword arguments and their types
        - Execution duration
        - Return value and its type
    Example usage:
        @log_call(logger=my_logger, info=True)
        def my_function(arg1, arg2):
            pass
    """

    # set logger to core logger if not provided
    if not logger: logger = core_logger()
    # set logging level
    _logger = logger.info if info else logger.debug

    # Create a decorator that logs function calls
    def decorator(func: F) -> F:
        
        @functools.wraps(func)
        def wrapper(*args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> Any:
            if func.__name__ == "__init__": raise RuntimeError("Cannot log __init__ method")
            cfg = get_config()
            if not cfg.log_fn_call: return func(*args, **kwargs)

            # Get the current frame and associated information
            current_frame = inspect.currentframe()
            call_frame = inspect.getouterframes(current_frame, 2)
            file_name = call_frame[1].filename
            line_number = call_frame[1].lineno
            
            # Determine class name if available (for method)
            if len(args) > 0 and hasattr(args[0], '__class__') and hasattr(args[0], func.__name__):
                class_name = args[0].__class__.__name__
            else:
                class_name = None
            name = f"{class_name}.{func.__name__}" if class_name else func.__name__

            # Construct logging message based on the level
            args_types = ", ".join(f"{arg if args_values else "..."}: {type(arg).__name__}" for arg in args)
            kwargs_types = ", ".join(f"{k}={v if args_values else "..."}: {type(v).__name__}" for k, v in kwargs.items())
            log_msg = f"Calling: {name} [{file_name}:{line_number}]\n\t\targs: ({args_types}), \n\t\tkwargs: {{{kwargs_types}}}"
            _logger(color_grey(log_msg))

            # Call the actual function
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time

            # Log the return value and its type
            log_msg = f"Done: {name} [{file_name}:{line_number}]\n\t\tduration: {duration:.6f}s\n\t\treturned: {result if return_value else "..."} \n\t\ttype: {type(result).__name__}"
            _logger(color_grey(log_msg))

            return result
        return wrapper
    return decorator

if __name__ == '__main__': exit()