#!/usr/bin/env python3
"""
uni.cmd.config

Configuration commands
"""
from __future__ import annotations
import argparse

from ..utils import rich_print

from ..config import config_factory
from ..logger import core_logger, set_logging_production

logger = core_logger().getChild("cmd.config")


def __cmd_show_default() -> int:
    logger.info("Show default configuration")
    raise NotImplementedError()
    return 0

def __cmd_show(path: str) -> int:
    """
    Display the configuration from the specified path.
    Args:
        path (str): The file path to the configuration file.
    Returns:
        int: Status code, 0 for success.
    """
    logger.info(f"Show configuration from {path}")
    
    cfg = config_factory(path)
    rich_print(cfg)
    
    return 0

def __main() -> int:
    """
    Main function for handling configuration commands.
    This function sets up an argument parser to handle configuration-related commands.
    It supports the following command-line arguments:
    - --show-default: If specified, the function will call `cmd_show_default()` to show the default configuration.
    Returns:
        int: The exit status code. Returns 0 if no arguments are provided or if help is displayed.
    """
    set_logging_production()

    parser = argparse.ArgumentParser(description='Configuration commands')
    parser.add_argument("--show", action="store_true", help="Show configuration")
    parser.add_argument("--path", default="config.json", help="Path to configuration file, default is config.json")
    parser.add_argument("--show-default", action="store_true", help="Show default configuration")

    args = parser.parse_args()

    if args.show_default:
        return __cmd_show_default()
    elif args.show:
        return __cmd_show(args.path)

    parser.print_help()
    return 0


if __name__ == "__main__":
    exit(__main())
