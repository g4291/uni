#!/usr/bin/env python3

"""
uni.modules.version.handler

version handler
"""

from __future__ import annotations
import os
from typing import Dict

from ...logger import core_logger
from ...version import RUN_ID, VERSION

from .model import Version


logger = core_logger().getChild("version")

_cache: Dict[str, Version] = {}

def version_handler():
    """
    Handles the retrieval and caching of the application version information.
    This function checks if the version information is already cached. If not, it reads the version
    from a file named "VERSION" in the current directory. If the file does not exist, it logs a warning.
    The version information is then stored in the cache.
    Returns:
        Version: An instance of the Version class containing the version, run_id, and app_version.
    """
    
    if not "version" in _cache:
        app_version = ""
        if os.path.exists("VERSION"):
            with open("VERSION", "r") as f:
                app_version = f.read().strip()
        else:
            logger.warning("VERSION file not found")
        _cache["version"] = Version(version=VERSION, run_id=RUN_ID, app_version=app_version)
    return _cache["version"]
    

if __name__ == "__main__": exit()