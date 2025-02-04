#!/usr/bin/env python3

"""
uni.filestorage.protocol

File storage protocol
"""

import io
from typing import Protocol


class UniFileStorage(Protocol):
    """
    UniFileStorage is a protocol that defines the interface for file storage operations.
    Methods:
        get_file(filename: str) -> bytes:
            Retrieve the contents of a file as bytes.
        put_file(filename: str, file: bytes) -> None:
            Store the given bytes as a file with the specified filename.
        delete_file(filename: str) -> None:
            Delete the file with the specified filename.
        reader(filename: str) -> BufferedReader:
            Return a BufferedReader for reading the file with the specified filename.
        writer(filename: str) -> BufferedWriter:
            Return a BufferedWriter for writing to the file with the specified filename.
    """

    def get(self, filename: str) -> bytes:
        """
        Retrieve the contents of a file as bytes.
        Args:
            filename (str): The name of the file to retrieve.
        Returns:
            bytes: The contents of the file.
        """
        ...

    def put(self, filename: str, file: bytes) -> None:
        """
        Stores a file in the file storage system.
        Args:
            filename (str): The name of the file to be stored.
            file (bytes): The content of the file to be stored.
        Returns:
            None
        """
        ...

    def delete(self, filename: str) -> None:
        """
        Deletes a file with the given filename from the storage.
        Args:
            filename (str): The name of the file to be deleted.
        Returns:
            None
        """
        ...

    def reader(self, filename: str) -> io.BytesIO:
        """
        Reads the content of the specified file and returns it as a BytesIO object.
        Args:
            filename (str): The name of the file to be read.
        Returns:
            io.BytesIO: A BytesIO object containing the file's content.
        """
        ...

    def exists(self, filename: str) -> bool:
        """
        Checks if a file with the given filename exists in the storage.
        Args:
            filename (str): The name of the file to check.
        Returns:
            bool: True if the file exists, False otherwise.
        """
        ...

if __name__ == "__main__": exit()