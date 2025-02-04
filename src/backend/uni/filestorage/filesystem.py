#!/usr/bin/env python3

"""
uni.filestorage.filesystem

File storage implementation for the file system.
"""

from io import BytesIO
import os

from ..default import UniDefault
from ..exceptions import NotFoundError, ServerError
from ..logger import core_logger


logger = core_logger().getChild("filestorage.filesystem")


class UniFileSystemStorage(UniDefault):
    """
    UniFileSystemStorage class provides methods to interact with the file system for storing, retrieving, and deleting files.
    Methods:
        get_file(filename: str) -> bytes:
            Reads and returns the content of the specified file as bytes.
            Raises NotFoundError if the file does not exist or cannot be read.
        put_file(filename: str, file: bytes) -> None:
            Writes the given bytes to the specified file.
            Raises ServerError if the file cannot be written.
        delete_file(filename: str) -> None:
            Deletes the specified file if it exists.
            Raises ServerError if the file cannot be deleted.
        reader(filename: str) -> BytesIO:
            Opens the specified file in binary read mode and returns a BytesIO object.
            Raises NotFoundError if the file does not exist or cannot be read.
    """
    def __init__(self):
        super().__init__()
        os.makedirs(self.config.files_directory, exist_ok=True)

    @property
    def root(self) -> str:
        return self.config.files_directory

    def get(self, filename: str) -> bytes:
        """
        Retrieve the contents of a file as bytes.
        Args:
            filename (str): The name of the file to be read.
        Returns:
            bytes: The contents of the file.
        Raises:
            NotFoundError: If the file cannot be found or read.
        """
        logger.debug(f"Reading file {filename}")
        filename = os.path.join(self.root, filename)
        try:
            with open(filename, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {filename}: {e}")
            raise NotFoundError(f"file not found")

    def put(self, filename: str, file: bytes) -> None:
        """
        Save a file to the filesystem.
        Args:
            filename (str): The name of the file to be saved.
            file (bytes): The content of the file in bytes.
        Raises:
            ServerError: If there is an error writing the file.
        """
        logger.debug(f"Writing file {filename}")
        filename = os.path.join(self.root, filename)
        try:
            with open(filename, 'wb') as f:
                f.write(file)
        except Exception as e:
            logger.error(f"Error writing file {filename}: {e}")
            raise ServerError("error writing file")

    def delete(self, filename: str) -> None:
        """
        Deletes a file from the filesystem.
        Args:
            filename (str): The name of the file to be deleted.
        Raises:
            ServerError: If there is an error deleting the file.
        """
        logger.debug(f"Deleting file {filename}")
        filename = os.path.join(self.root, filename)
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception as e:
                logger.error(f"Error deleting file {filename}: {e}")
                raise ServerError("error deleting file")

    def reader(self, filename: str) -> BytesIO:
        """
        Opens a file in binary read mode and returns a BytesIO object.
        Args:
            filename (str): The path to the file to be opened.
        Returns:
            BytesIO: A buffered reader object for the file.
        Raises:
            NotFoundError: If the file cannot be found or opened.
        """
        logger.debug(f"Reading file {filename}")
        filename = os.path.join(self.root, filename)
        try:
            with open(filename, 'rb') as f:
                content = f.read()

            return BytesIO(content)
        except Exception as e:
            logger.error(f"Error reading file {filename}: {e}")
            raise NotFoundError(f"file not found")    
        
    def exists(self, filename: str) -> bool:
        """
        Checks if a file with the given filename exists in the storage.
        Args:
            filename (str): The name of the file to check.
        Returns:
            bool: True if the file exists, False otherwise.
        """
        return os.path.exists(os.path.join(self.root, filename))
    

if __name__ == '__main__': exit()