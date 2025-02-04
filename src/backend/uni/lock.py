#!/usr/bin/env python3

"""
uni.lock

Lock module
"""

from __future__ import annotations
import time
from typing import Optional
import uuid
import os

from .default import UniDefault
from .logger import color_red, core_logger
from .exceptions import ServerError


logger = core_logger().getChild("lock")


class UniLock(UniDefault):
    """
    UniLock class provides a mechanism to create and manage a lock file to ensure that only one instance of a process can access a resource at a time.
    Attributes:
        filename (str): The name of the lock file.
        id (uuid.UUID): A unique identifier for the lock instance.
    Methods:
        __init__(filename: str = "UniLock.lock", directory: Optional[str] = None):
            Initializes the UniLock instance with a specified filename and directory.
        __enter__() -> None:
            Acquires the lock when entering a context.
        __exit__(*args, **kwargs) -> None:
            Releases the lock when exiting a context.
        _create_dir(directory) -> None:
            Creates the directory for the lock file if it does not exist.
        _locked() -> Optional[uuid.UUID]:
            Checks if the lock file exists and returns the process ID if it does.
        _lock() -> None:
            Creates the lock file and writes the process ID to it.
        _release() -> None:
            Deletes the lock file.
        lock():
            Waits until the lock is available and then acquires it.
        release():
            Releases the lock if the current process holds it.
    """
    def __init__(self, filename: str = "UniLock.lock", directory: Optional[str] = None):
        if not directory:
            directory = self.config.tmp_directory
        self.filename = f"{directory}/{filename}"
        self.id = uuid.uuid4()
        os.makedirs(directory, exist_ok=True)

    def __enter__(self) -> None:
        self.lock()

    def __exit__(self, *args, **kwargs) -> None:
        self.release()        

    def _locked(self) -> Optional[uuid.UUID]:
        """
        Checks if the lock file exists and reads the process ID from it.
        Returns:
            Optional[uuid.UUID]: The UUID of the process if the lock file exists and contains a valid UUID, 
                                 otherwise None.
        Raises:
            ServerError: If the lock file contains an invalid UUID.
        """
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                process_id = f.read()
                try:
                    return uuid.UUID(process_id)
                except Exception as e:
                    msg = f"UniLock exception: {e}"
                    logger.error(color_red(msg))
                    raise ServerError(msg)

    def _lock(self) -> None:
        """
        Acquires a lock by creating a file with the specified filename.
        
        This method attempts to create a file with the given filename in exclusive mode.
        If the file already exists, an exception will be raised. The file is then written
        with the ID of the lock holder and closed.

        Raises:
            OSError: If the file already exists or cannot be created.
        """
        f =  os.open(self.filename, os.O_CREAT|os.O_EXCL|os.O_WRONLY) 
        os.write(f, str(self.id).encode())
        os.close(f)

    def _release(self) -> None:
        """
        Deletes the lock file to release the lock.
        This method removes the file specified by `self.filename` to release the lock.
        """
        os.remove(self.filename)

    def lock(self):
        """
        Acquires the lock for the current instance.
        This method will block execution until the lock is available. It repeatedly
        checks if the lock is currently held by another process and waits for a short
        period before checking again. Once the lock is available, it acquires the lock.
        Note:
            This method assumes that the `_locked` and `_lock` methods are implemented
            elsewhere in the class to check the lock status and to acquire the lock,
            respectively.
        """
        # wait
        while self._locked():
            time.sleep(0.01)
        
        # lock
        self._lock()

    def release(self):
        """
        Releases the lock if the current process holds it.
        This method checks if the lock is currently held by the process with the
        given ID. If so, it releases the lock.
        Returns:
            None
        """
        # get process id
        process_id = self._locked()

        if process_id and process_id == self.id:
            self._release()


if __name__ == "__main__": exit()