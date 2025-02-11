#!/usr/bin/env python3

"""
uni.filestorage.factory_test

module test
"""

from ..testing import AppTesting
from ..logger import core_logger
from ..exceptions import ValidationError

from .factory import UniFileStorageFactory
from .filesystem import UniFileSystemStorage
from .s3 import UniS3Storage


logger = core_logger().getChild("filestorage")


if __name__ == '__main__': 
    cfg = AppTesting.basic("filestorage factory")

    # test get filesystem storage
    fs = UniFileStorageFactory.get("filesystem")
    assert isinstance(fs, UniFileSystemStorage)

    # test get s3 storage
    if cfg.aws_key != "":
        fs = UniFileStorageFactory.get("s3")
        assert isinstance(fs, UniS3Storage)

    # test get invalid storage
    try:
        fs = UniFileStorageFactory.get("invalid")
    except ValidationError:
        logger.info("ValidationError raised, OK")
    except Exception:
        raise AssertionError("ValidationError not raised")
    else:
        raise AssertionError("ValidationError not raised")
    
    logger.info("uni.filestorage.factory_test tests passed")
