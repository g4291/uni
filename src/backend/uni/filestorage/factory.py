#!/usr/bin/env python3

"""
uni.filestorage.factory

File storage factory
"""

from typing import Dict, Optional, Type, Union

from ..config import get_config
from ..default import UniDefault
from ..exceptions import ValidationError
from .protocol import UniFileStorage
from .filesystem import UniFileSystemStorage
from .s3 import UniS3Storage


class UniFileStorageFactory():
    storages: Dict[str, Union[Type[UniFileStorage], Type[UniDefault]]] = {
        "filesystem": UniFileSystemStorage,
        "s3": UniS3Storage
    }

    @staticmethod
    def get(storage_type: Optional[str] = None, cached: bool = True) -> UniFileStorage:
        """
        Retrieve an instance of UniFileStorage based on the configuration.
        Args:
            cached (bool): If True, returns a cached instance of the storage. Defaults to True.
        Returns:
            UniFileStorage: An instance of the configured storage type.
        Raises:
            ValidationError: If the storage type specified in the configuration is invalid.
        """
        # get the storage type from the configuration if not provided
        if not storage_type:
            storage_type = get_config().storage_type

        # get the storage class
        _storage = UniFileStorageFactory.storages.get(storage_type, None)
        if not _storage:
            raise ValidationError(f"invalid storage type: {storage_type}")
        
        # return the storage instance
        if cached:
            return _storage.cached()
        
        return _storage()


if __name__ == "__main__": exit()