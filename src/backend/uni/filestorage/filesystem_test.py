#!/usr/bin/env python3

"""
uni.filestorage.filesystem_test

module test
"""

from ..testing import AppTesting
from ..logger import core_logger

from .filesystem import UniFileSystemStorage


logger = core_logger().getChild("filestorage")


if __name__ == '__main__': 
    AppTesting.basic("filesystem storage")

    fs = UniFileSystemStorage()
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

    logger.info("uni.filestorage.filesystem_test tests passed")
