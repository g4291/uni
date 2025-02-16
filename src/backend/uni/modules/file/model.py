#!/usr/bin/env python3

"""
uni.modules.user.model
"""

from __future__ import annotations
import base64
import io
import os
from typing import BinaryIO, Optional
import uuid
from pydantic import BaseModel, Field

from ...filestorage import UniFileStorageFactory
from ...config import get_config
from ...version import API_PREFIX
from ...exceptions import NotFoundError, ServerError
from ...utils import random_secret
from ...database.model import DatabaseModel


class BaseFile(BaseModel):
    """ base file model, email validation"""
    filename: str
    original_name: str
    public_link: str = ""
    secret: str = Field(default_factory=random_secret)
    size: int
    content_type: str
    
    def get_full_public_link(self) -> str:
        """ returns full public link"""
        if not self.public_link:
            return ""
        
        return f"{get_config().server_url}{API_PREFIX}{self.public_link}"
    
    def b64_encoded(self) -> str:
        """ returns base64 encoded string"""
        fs = UniFileStorageFactory.get()
        # Read the contents of the file
        file_contents = fs.get(self.filename)
        # Encode the file contents to a base64 string
        return base64.b64encode(file_contents).decode("utf-8")

class File(DatabaseModel, BaseFile):
    """ base file db model"""

class db_File(File):
    """ Internal, stored in db"""
    
class UniUploadFile():  
    def __init__(self, filename: str, orig_name: str,  content_type: str = ""):
        if not os.path.exists(filename):
            raise NotFoundError(f"file not found: {filename}")
    
        self._filename = filename
        self._orig_name = orig_name
        self._content_type = content_type
        
    @property
    def filename(self) -> str:
        return self._orig_name
    
    @property
    def content_type(self) -> str:
        return self._content_type
        
    @property
    def file(self) -> BinaryIO:
        try:
            return open(self._filename, "rb")
        except Exception as e:
            raise ServerError(str(e))
        
class BaseFTPRequest(BaseModel):
    host: str
    user: str
    password: str
    root_dir: str = "~/"
        
class FTPListRequest(BaseFTPRequest):
    """ ftp list request"""
    path: str = "/"


class FTPUploadRequest(BaseFTPRequest):
    path: str
    filename: str
    file_id: uuid.UUID
    
class FTPDownloadRequest(BaseFTPRequest):
    path: str
    filename: str

class FTPDeleteRequest(BaseFTPRequest):
    path: str
    filename: str

class FTPCreateFolderRequest(BaseFTPRequest):
    path: str
    folder_name: str

class FTPListItem(BaseModel):
    path: str
    name: str
    is_directory: bool
    size: int

class UniB64EncodedFile(BaseModel):
    id: uuid.UUID
    filename: str
    size: int
    data: str
    mime_type: str
    path: Optional[str] = None
    
    @property
    def extension(self) -> str:
        return os.path.splitext(self.filename)[1]
    
    def decode_str(self) -> str:
        return base64.b64decode(self.data.split(",")[1]).decode("utf-8")
    
    def b64_data(self) -> str:
        return self.data.split(",")[1]
    
    def as_stream(self) -> io.BytesIO:
        data = base64.b64decode(self.data.split(",")[1])
        return io.BytesIO(data)


if __name__ == "__main__": exit()