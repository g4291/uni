#!/usr/bin/env python3

"""
uni.modules.file.handler

TODO: split ftp methods into separate handler
"""

from __future__ import annotations
import base64
import io
import os
import uuid
from typing import List, Optional, Tuple, Union
from fastapi import Request, Response, UploadFile
from PIL import Image
from ftplib import FTP

from ...exceptions import ForbiddenError, NotFoundError, ServerError, BaseHTTPException
from ...filestorage import UniFileStorageFactory
from ...handler.base import PublicHandler
from ...services import permission
from ...services.auth import AuthToken, auth_dependency
from ...handler import PrivateHandler
from ...logger import color_red, core_logger
from ...utils import random_secret

from .model import FTPCreateFolderRequest, FTPDeleteRequest, FTPDownloadRequest, FTPUploadRequest, File, FTPListRequest, FTPListItem, UniB64EncodedFile, UniUploadFile, db_File


logger = core_logger().getChild("file")


class FileHandler():
    def _exists(self, filename) -> bool:
        fs = UniFileStorageFactory.get()
        return fs.exists(filename)
    
    def _respond(self, f: db_File) -> Response:
        if self._exists(f.filename):
            fs = UniFileStorageFactory.get()
            return Response(fs.get(f.filename), headers={'Content-Disposition': 'attachment; filename="%s"' % f.original_name})
        raise NotFoundError("file not found")
    
    def _ftp_is_directory(self, ftp: FTP, name):
        current = ftp.pwd()
        try:
            ftp.cwd(name)
            ftp.cwd(current)
            return True
        except Exception:
            return False
        
    def _ftp_get_size(self, ftp: FTP, name):
        size = 0
        try:
            size = ftp.size(name)
        except Exception:
            pass
        return size
    
    def _ftp_delete_directory_contents(self, ftp: FTP, path):
        # Change to the specified directory
        ftp.cwd(path)
        current = ftp.pwd()
        
        # Retrieve the list of files and directories
        items = ftp.nlst()
        
        for item in items:
            if self._ftp_is_directory(ftp, item):
                self._ftp_delete_directory_contents(ftp, item)
                ftp.cwd(current)
                ftp.rmd(item)
            else:
                ftp.delete(item)
    
    def _ftp_connect(self, host: str, user: str, password: str, **kwargs) -> FTP:
        ftp = FTP(host)
        ftp.login(user, password)
        return ftp
    
class PrivateFileHandler(PrivateHandler, FileHandler):
    def _create_b64(self, f: UniB64EncodedFile) -> File:
        # permissions
        group_name = db_File.__name__
        if not permission.group_permission(group_name, self.user, True):
            raise ForbiddenError("permission denied")
        
        fs = UniFileStorageFactory.get()

        # write file
        _id = f.id
        secret = random_secret()
        filename = f"{_id}_{f.filename}"

        try:
            b64_data = f.data.split(",")[1]
        except Exception as e:
            raise ServerError("invalid base64 data")

        content = base64.b64decode(b64_data)
        size = len(content)
        fs.put(filename, content)

        # store in db
        entity = db_File(
            id=_id, 
            secret=secret,
            filename=filename, 
            original_name=f.filename,
            public_link=f"{self.config.files_read_endpoint}?id={_id}&secret={secret}",
            size=size, 
            content_type=f.mime_type
        )
        entity.created.user_id = self.user.id
        r = self.database.create(entity)

        # server error
        if not r:
            # remove file
            fs.delete(filename)

            msg = "can not create entity"
            logger.error(color_red(msg))
            raise ServerError(msg)

        return File.from_model(entity)
    def _create(self, f: Union[UploadFile, UniUploadFile]) -> File:
        # permissions
        group_name = db_File.__name__
        if not permission.group_permission(group_name, self.user, True):
            raise ForbiddenError("permission denied")
        
        fs = UniFileStorageFactory.get()

        # write file
        _id = uuid.uuid4()
        secret = random_secret()
        filename = f"{_id}_{f.filename}"

        content = f.file.read()
        size = len(content)
        fs.put(filename, content)

        # store in db
        entity = db_File(
            id=_id, 
            secret=secret,
            filename=filename, 
            original_name=f.filename,
            public_link=f"{self.config.files_read_endpoint}?id={_id}&secret={secret}",
            size=size, 
            content_type=f.content_type
        )
        entity.created.user_id = self.user.id
        r = self.database.create(entity)

        # server error
        if not r:
            # remove file
            fs.delete(filename)

            msg = "can not create entity"
            logger.error(color_red(msg))
            raise ServerError(msg)

        return File.from_model(entity)

    def _read(self, id: uuid.UUID) -> Response:

        # permissions
        group_name = db_File.__name__
        if not permission.group_permission(group_name, self.user, False):
            raise ForbiddenError("permission denied")

        entity = self.database.get_one(id, db_File)
        if not entity:
            raise NotFoundError("file not found")

        return self._respond(entity)
    
    def _ftp_list(self, rq: FTPListRequest) -> List[str]:
        # permissions
        group_name = db_File.__name__
        if not permission.group_permission(group_name, self.user, False):
            raise ForbiddenError("permission denied")
        
        ftp = None
        try:
            ftp = self._ftp_connect(**rq.dict())
        except Exception as e:
            raise ServerError(f"unable to connect to FTP server, {str(e)}")

        try:
            ftp.cwd(rq.root_dir+rq.path)
        except Exception as e:
            raise ServerError(f"unable to change directory on FTP server, {str(e)}")
            
        # Retrieve the list of files and directories
        items = ftp.nlst()
        
        result = []
        for item in items:
            path = rq.path+"/"+item
            if self._ftp_is_directory(ftp, item):
                size = 0  # Size for directories is generally not meaningful
                result.append(FTPListItem(name=item, is_directory=True, size=size, path=path))
            else:
                size = self._ftp_get_size(ftp, item)
                result.append(FTPListItem(name=item, is_directory=False, size=size, path=path))
        
        # Close the connection
        ftp.quit()
        return result
    
    def _ftp_upload(self, rq: FTPUploadRequest) -> None:
        # permissions
        group_name = db_File.__name__
        if not permission.group_permission(group_name, self.user, False):
            raise ForbiddenError("permission denied")
        
        ftp = None
        try:
            ftp = self._ftp_connect(**rq.dict())
        except Exception as e:
            raise ServerError(f"unable to connect to FTP server, {str(e)}")
        
        # change directory
        try:
            ftp.cwd(rq.root_dir+rq.path)
        except Exception as e:
            raise ServerError(f"unable to change directory on FTP server, {str(e)}")
        
        # get file from database
        uni_f = self.database.get_one(rq.file_id, db_File)
        if not uni_f:
            raise NotFoundError("file not found")
        
        if not self._exists(uni_f.filename):
            raise NotFoundError("file not found")
        
        # upload file
        try:
            fs = UniFileStorageFactory.get()
            reader = fs.reader(uni_f.filename)
            ftp.storbinary(f"STOR {rq.filename}", reader)
        except Exception as e:
            raise ServerError(f"unable to upload file to FTP server, {str(e)}")
        finally:
            ftp.quit()
            
    def _ftp_download(self, rq: FTPDownloadRequest) -> None:
        # permissions
        group_name = db_File.__name__
        if not permission.group_permission(group_name, self.user, False):
            raise ForbiddenError("permission denied")
        
        ftp = None
        try:
            ftp = self._ftp_connect(**rq.dict())
        except Exception as e:
            raise ServerError(f"unable to connect to FTP server, {str(e)}")
        
        # change directory
        try:
            ftp.cwd(rq.root_dir+rq.path)
        except Exception as e:
            raise ServerError(f"unable to change directory on FTP server, {str(e)}")
        
        # download file
        try:
            filename = self.config.tmp_directory+"/"+str(uuid.uuid4())+"_"+rq.filename
            with open(filename, "wb") as f:
                ftp.retrbinary(f"RETR {rq.filename}", f.write)
            
            uni_file = UniUploadFile(filename, rq.filename, "application/octet-stream")
            self._create(uni_file)
            os.remove(filename)
        except BaseHTTPException as e:
            raise
        except Exception as e:
            raise ServerError(f"unable to download file from FTP server, {str(e)}")
        finally:
            ftp.quit()

    def _ftp_delete(self, rq: FTPDeleteRequest) -> None:
        """
        Delete a file from an FTP server.

        Args:
            rq (FTPDeleteRequest): The request object containing the file to delete.
        """
        # permissions
        group_name = db_File.__name__
        if not permission.group_permission(group_name, self.user, False):
            raise ForbiddenError("permission denied")
        
        ftp = None
        try:
            ftp = self._ftp_connect(**rq.dict())
        except Exception as e:
            raise ServerError(f"unable to connect to FTP server, {str(e)}")
        
        # change directory
        try:
            ftp.cwd(rq.root_dir+rq.path)
        except Exception as e:
            raise ServerError(f"unable to change directory on FTP server, {str(e)}")

        # direcotry
        if self._ftp_is_directory(ftp, rq.filename):
            try:
                self._ftp_delete_directory_contents(ftp, rq.filename)
            except Exception as e:
                raise ServerError(f"unable to delete folder contents on FTP server, {str(e)}")
            try:
                ftp.cwd(rq.root_dir+rq.path)
                ftp.rmd(rq.filename)
            except Exception as e:
                raise ServerError(f"unable to delete folder on FTP server, {str(e)}")
            finally:
                ftp.quit()
            return

        
        # delete file
        try:
            ftp.delete(rq.filename)
        except Exception as e:
            raise ServerError(f"unable to delete file on FTP server, {str(e)}")
        finally:
            ftp.quit()

    def _ftp_create_folder(self, rq: FTPCreateFolderRequest) -> None:
        """
        Create a folder on an FTP server.

        Args:
            rq (FTPCreateFolderRequest): The request object containing the folder to create.
        """
        # permissions
        group_name = db_File.__name__
        if not permission.group_permission(group_name, self.user, False):
            raise ForbiddenError("permission denied")
        
        ftp = None
        try:
            ftp = self._ftp_connect(**rq.dict())
        except Exception as e:
            raise ServerError(f"unable to connect to FTP server, {str(e)}")
        
        # change directory
        try:
            ftp.cwd(rq.root_dir+rq.path)
        except Exception as e:
            raise ServerError(f"unable to change directory on FTP server, {str(e)}")
        
        # create folder
        try:
            ftp.mkd(rq.folder_name)
        except Exception as e:
            raise ServerError(f"unable to create folder on FTP server, {str(e)}")
        finally:
            ftp.quit()

    @classmethod
    def create_b64(cls, f: UniB64EncodedFile, auth=auth_dependency()):
        """
        Creates a new file from b64 encoded data.
        Args:
            f (UniB64EncodedFile): The file to be created.
            auth (AuthDependency, optional): The authentication dependency. Defaults to auth_dependency().
        Returns:
            The created file.
        """
        return cls.new(auth)._create_b64(f)

    @classmethod
    def create(cls, f: UploadFile, auth=auth_dependency()):
        """
        Create a new file.

        Args:
            f (UploadFile): The file to be created.
            auth (AuthDependency, optional): The authentication dependency. Defaults to auth_dependency().

        Returns:
            The created file.
        """
        return cls.new(auth)._create(f)

    @classmethod
    def create_from_filename(cls, f: UniUploadFile, auth: Tuple[AuthToken, Optional[Request]]):
        """
        Create a new file from a given filename.

        Args:
            f (UniUploadFile): The file to be created.
            auth (Tuple[AuthToken, Optional[Request]]): Authentication information.

        Returns:
            The newly created file.
        """
        return cls.new(auth)._create(f)

    @classmethod
    def read(cls, id: uuid.UUID, auth = auth_dependency()):
        """
        Read a file with the given ID.

        Args:
            id (uuid.UUID): The ID of the file to read.
            auth: The authentication dependency.

        Returns:
            The result of reading the file.
        """
        return cls.new(auth)._read(id)
    
    
    @classmethod
    def ftp_list(cls, rq: FTPListRequest, auth = auth_dependency()):
        """
        Retrieve a list of files from the FTP server.

        Args:
            rq (FTPListRequest): The request object containing the FTP server details.
            auth (AuthDependency): The authentication dependency.

        Returns:
            List[str]: A list of file names retrieved from the FTP server.
        """
        return cls.new(auth)._ftp_list(rq)
    
    @classmethod
    def ftp_upload(cls, rq: FTPUploadRequest, auth = auth_dependency()):
        """
        Uploads a file using FTP.

        Args:
            rq (FTPUploadRequest): The request object containing the file to upload.
            auth: The authentication dependency.

        Returns:
            The result of the FTP upload.
        """
        return cls.new(auth)._ftp_upload(rq)
    
    @classmethod
    def ftp_download(cls, rq: FTPDownloadRequest, auth = auth_dependency()):
        """
        Downloads a file from the FTP server.

        Args:
            rq (FTPDownloadRequest): The request object containing the file information.
            auth (AuthDependency): The authentication dependency.

        Returns:
            The result of the FTP download operation.
        """
        return cls.new(auth)._ftp_download(rq)
    
    @classmethod
    def ftp_delete(cls, rq: FTPDeleteRequest, auth = auth_dependency()):
        """
        Deletes a file from the FTP server.

        Args:
            rq (FTPDeleteRequest): The request object containing the file information.
            auth (AuthDependency): The authentication dependency.

        Returns:
            The result of the FTP upload operation.
        """
        return cls.new(auth)._ftp_delete(rq)
    
    @classmethod
    def ftp_create_folder(cls, rq: FTPCreateFolderRequest, auth = auth_dependency()):
        """
        Creates a new folder in the FTP server.

        Args:
            rq (FTPDeleteRequest): The request object containing the necessary information.
            auth (AuthDependency): The authentication dependency.

        Returns:
            The result of the _ftp_create_folder method.
        """
        return cls.new(auth)._ftp_create_folder(rq)



class PublicFileHandler(PublicHandler, FileHandler):    
    def image_resize(self, entity: db_File, w: Optional[int] = None, h: Optional[int] = None) -> Response:
        if w is not None and w < 0:
            raise ServerError("width must be greater than 0")
        if h is not None and h < 0:
            raise ServerError("height must be greater than 0")

        _name, _ext = os.path.splitext(entity.filename)
        filename = f"{_name}_w{w}_h{h}_{_ext}"
        
        fs = UniFileStorageFactory.get()
        if self._exists(filename):
            return Response(fs.get(filename), headers={'Content-Disposition': 'attachment; filename="%s"' % filename})
        
        format = "JPEG" if _ext.lower() in [".jpg", ".jpeg"] else "PNG"

        try:
            image = Image.open(fs.reader(entity.filename))
            aspect = image.height / image.width
            if w is None and h is None:
                raise ServerError("width or height must be provided")
            if w is None:
                w = int(h / aspect)
            if h is None:
                h = int(w * aspect)

            resized = image.resize((w, h))
            if format == "JPEG":
                resized = resized.convert("RGB")
            stream = io.BytesIO()
            resized.save(stream, format=format)
            fs.put(filename, stream.getvalue())
        except Exception as e:
            raise ServerError(str(e))

        return Response(fs.get(filename), headers={'Content-Disposition': 'attachment; filename="%s"' % filename})

    def _read(self, id: uuid.UUID, secret: str, w: Optional[int] = None, h: Optional[int] = None) -> Response:

        entity = self.database.get_one(id, db_File)
        if not entity:
            raise NotFoundError("file not found")

        if not secret:
            raise NotFoundError("file not found")

        if entity.secret != secret:
            raise NotFoundError("file not found")

        # image resize?
        if w is not None or h is not None:
            return self.image_resize(entity, w, h)

        return self._respond(entity)


    @classmethod
    def read(cls, id: uuid.UUID, secret: str, w: Optional[int] = None, h: Optional[int] = None):
        """
        Read a file with the given ID and secret.

        Args:
            id (uuid.UUID): The ID of the file to read.
            secret (str): The secret key for accessing the file.
            w (Optional[int]): Optional width of the file to read.
            h (Optional[int]): Optional height of the file to read.

        Returns:
            The content of the file.
        """
        return cls.new()._read(id, secret, w=w, h=h)



if __name__ == "__main__": exit()