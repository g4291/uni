#!/usr/bin/env python3

"""
uni.encoders

"""

from __future__ import annotations

import uuid
import json
from pydantic import BaseModel


# JSON encoder with uuid and pydentic encoding
class UniJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, BaseModel):
            return obj.dict()
        return json.JSONEncoder.default(self, obj)

# JSON Decoder with uuid decoding
class UniJsonDecoder(json.JSONDecoder):
    def decode(self, s: str):
        try:
            return uuid.UUID(s)
        except:
            return json.JSONDecoder.decode(self, s)
        

if __name__ == '__main__': exit()