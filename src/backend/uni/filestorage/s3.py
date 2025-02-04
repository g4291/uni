#!/usr/bin/env python3

"""
uni.filestorage.s3

File storage implementation for the amazon S3 service.
TODO: caching files locally
"""

import io
import os
from botocore.exceptions import ClientError

from ..services.aws import aws_client_factory 
from ..default import UniDefault
from ..exceptions import NotFoundError, ServerError
from ..logger import core_logger


logger = core_logger().getChild("filestorage.s3")


class UniS3Storage(UniDefault):

    def __init__(self):
        super().__init__()
        self._client = aws_client_factory("s3")

        # create bucket if not exists
        self._create_bucket()

        # create cache folder
        self._cache_directory = os.path.join(self.config.tmp_directory, "s3_cache")
        os.makedirs(self._cache_directory, exist_ok=True)

    def _create_bucket(self):
        """
        Creates an S3 bucket using the AWS SDK.
        This method attempts to create an S3 bucket with the specified configuration.
        If the bucket already exists and is owned by the user, it logs a debug message
        and returns without raising an exception. If any other error occurs during the
        bucket creation process, it logs an error message and raises a ServerError.
        Raises:
            ServerError: If there is an error creating the bucket that is not related
                         to the bucket already existing and being owned by the user.
        """
        try:
            self._client.create_bucket(
                CreateBucketConfiguration={
                    'LocationConstraint': self.config.aws_region
                },
                Bucket=self.bucket_name
            )

        except ClientError as e:
            if e.__class__.__name__ == "BucketAlreadyOwnedByYou":
                logger.debug(f"Bucket {self.bucket_name} already exists.")
                return

            logger.error(f"Error creating bucket {self.bucket_name}: {e}")
            raise ServerError(f"Error creating bucket {self.bucket_name}")

    @property
    def bucket_name(self) -> str:
        return self.config.app_name

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
        logger.debug(f"Downloading file {filename} from S3")
        try:
            obj = self._client.get_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            return obj['Body'].read()
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
        logger.debug(f"Uploading file {filename} to S3")
        f = io.BytesIO(file)
        try:
            self._client.upload_fileobj(
                f,
                self.bucket_name,
                filename
            )
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
        logger.debug(f"Deleting file {filename} from S3")
        try:
            self._client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            raise ServerError("error deleting file")

    def reader(self, filename: str) -> io.BytesIO:
        """
        Reads the content of a file from S3 storage and returns it as a BytesIO object.

        Args:
            filename (str): The name of the file to read from S3 storage.

        Returns:
            io.BytesIO: A BytesIO object containing the file's content.
        """

        logger.debug(f"Opening file {filename} for reading")
        return io.BytesIO(self.get(filename))
    
    def exists(self, filename: str) -> bool:
        """
        Checks if a file with the given filename exists in the storage.

        Args:
            filename (str): The name of the file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        try:
            self._client.head_object(Bucket=self.bucket_name, Key=filename)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise e
    

if __name__ == '__main__': exit()