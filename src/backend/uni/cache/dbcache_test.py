#!/usr/bin/env python3

"""
uni.cache.dbcache_test

module test
"""

from pydantic import BaseModel

from uni.database import database_factory

from ..testing import AppTesting
from ..logger import core_logger

from .dbcache import CacheInDatabase


logger = core_logger().getChild("cache.dbcache")


if __name__ == '__main__': 
    AppTesting.basic("in-database cache test")

    class TestDbCacheModel(BaseModel):
        foo: str
        bar: int


    @CacheInDatabase.cache(TestDbCacheModel, ttl_seconds=1)
    def test_getter(foo: str, **kwargs) -> TestDbCacheModel:
        return TestDbCacheModel(foo=foo, bar=42)

    database_factory()    

    # Test cache
    test_id = "some test id"
    test_foo = "test_foo"
    t1, cached = test_getter(test_foo, id=test_id)
    assert not cached

    t2, cached = test_getter(test_foo, id=test_id)
    assert t1 == t2
    assert cached


    logger.info("uni.cache.dbcache_test tests passed")
