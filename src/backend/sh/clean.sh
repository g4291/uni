#!/bin/bash

# delete pycache 
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf

# delete mypy and pytest cache
rm -rf .mypy_cache
rm -rf .pytest_cache