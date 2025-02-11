#!/usr/bin/env python3

"""
uni.filestorage.s3_test

module test
"""

from ..testing import AppTesting
from ..logger import core_logger

from .s3 import UniS3Storage


logger = core_logger().getChild("filestorage")


if __name__ == '__main__': 
    cfg = AppTesting.basic("s3 storage")
    
    if cfg.aws_key == "":
        logger.info("AWS credentials not configured, skipping tests")
        exit()

    fs = UniS3Storage()
    test_content = "This is a test file.".encode("utf-8")

    # Test put
    fs.put("test.txt", test_content)
    assert fs.exists("test.txt")

    # Test get
    content = fs.get("test.txt")
    assert content == test_content

    # Test delete
    fs.delete("test.txt")
    assert not fs.exists("test.txt")

    logger.info("uni.filestorage.s3_test tests passed")
