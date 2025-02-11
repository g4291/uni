#!/bin/bash
set -e
trap 'echo "tests failed"; exit 1' ERR

# remove test.db
rm ./test.db

# uni.cache
python3 -m uni.cache.dbcache_test

# uni.filestorage
python3 -m uni.filestorage.factory_test
python3 -m uni.filestorage.s3_test
python3 -m uni.filestorage.filesystem_test


echo "all tests passed"