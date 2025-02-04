#!/usr/bin/env python3

"""
uni.services.aws

AWS service module
"""

from typing import Any
import boto3

from ..config import get_config 
from ..logger import core_logger


logger = core_logger().getChild("aws")


def aws_client_factory(resource_name: str) -> Any:
    """
    Creates and returns a boto3 client for the specified AWS resource.
    Args:
        resource_name (str): The name of the AWS resource for which the client is to be created.
    Returns:
        boto3.client: A boto3 client configured with the specified resource name and credentials.
    Raises:
        botocore.exceptions.BotoCoreError: If there is an error creating the boto3 client.
        botocore.exceptions.ClientError: If there is an error with the AWS credentials or configuration.
    Example:
        client = aws_client_factory('s3')
    """
    logger.debug(f"Creating AWS client for resource: {resource_name}")
    cfg = get_config()
    return boto3.client(
        resource_name, 
        region_name=cfg.aws_region, 
        aws_access_key_id=cfg.aws_key, 
        aws_secret_access_key=cfg.aws_secret
    )
    

if __name__ == '__main__': exit()