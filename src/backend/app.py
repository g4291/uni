#!/usr/bin/env python3

"""
Uni-backend main file
"""

from __future__ import annotations
import os

from uni.config import config_factory
from uni.application import UniBackend
from uni.logger import disable_uvicorn_logger, set_logging_dev, set_logging_production


# main function
def main() -> UniBackend:
    """
    Main function
    
    creates config, set logging, runs tests
    returns FastAPI application object
    """
    # get config
    config = config_factory(
        os.getenv("UNI_CONFIG", "")
    )

    # logging
    if config.production: set_logging_production()
    else: set_logging_dev()
    if not config.log_uvicorn: disable_uvicorn_logger()

    # create application
    return UniBackend(config=config)

# direct run, do nothing
if __name__ == "__main__":
    print("Run application with uvicorn (see sh/run.sh)")
    exit()    

# run application
APP = main()