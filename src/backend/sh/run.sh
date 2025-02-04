#!/bin/bash

export UNI_CONFIG="config.json"
export UNI_PORT=8080

uvicorn app:APP --host 0.0.0.0 --port $UNI_PORT --reload --proxy-headers