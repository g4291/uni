#!/usr/bin/env python3

"""
uni.config

"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
import json

from config import CustomConfig


def _default_cors_origins_factory() -> List[str]:
    return ["*"]

def _default_cors_methods_factory() -> List[str]:
    return ["*"]

class ConfigMail(BaseModel):
    """ ConfigMail Dataclass """
    smtp_server_address: str = Field(default="", description="SMTP server address")
    smtp_server_port: int = Field(default=587, description="SMTP server port")
    tls: bool = Field(default=True, description="TLS")
    ssl: bool = Field(default=False, description="SSL")
    username: str = Field(default="", description="SMTP username")
    password: str = Field(default="", description="SMTP password")
    sender: str = Field(default="", description="Email sender address")
    debug: bool = Field(default=False, description="Debug mode (if true, just print email, do not send)")


class Config(BaseModel):
    """ Config Dataclass """
    # general
    app_name: str = Field(default="uni", description="Application name")
    description: str = Field(default="", description="Application description")
    production: bool = Field(default=False, description="Production mode")
    doc_url: Optional[str] = Field(default="/docs", description="Documentation URL")
    server_url: str = Field(default="http://localhost:8080", description="Server URL")
    log_uni_core: bool = Field(default=True, description="Log uni core")
    log_uvicorn: bool = Field(default=True, description="Log uvicorn")
    log_debug: bool = Field(default=True, description="Log debug")
    log_fn_call: bool = Field(default=True, description="Log function calls")

    # custom config
    custom: CustomConfig = Field(default_factory=CustomConfig, description="Custom configuration")

    # mail:
    mail: ConfigMail = Field(default_factory=ConfigMail, description="Mail configuration")

    # database
    database_string: str = Field(default="sqlite://uni.db", description="Database connection string")
    database_export_directory: str = Field(default="./dumps", description="Database export directory")

    mongo_cache_enabled: bool = Field(default=False, description="Enable MongoDB cache")
    mongo_cache_size: int = Field(default=1000, description="MongoDB cache size")

    # security
    security_password_salt: str = Field(default="", description="Security password salt")
    security_min_password_length: int = Field(default=6, description="Minimum password length")
    security_cors_origins: List[str] = Field(default_factory=_default_cors_origins_factory, description="CORS allowed origins")
    security_cors_methods: List[str] = Field(default_factory=_default_cors_methods_factory, description="CORS allowed methods")
    security_delay_seconds: int = Field(default=1, description="Security delay in seconds")
    security_token_expires_minutes: int = Field(default=0, description="Token expiration time in minutes (0 means never expires)")
    security_multiple_tokens: bool = Field(default=True, description="Allow multiple tokens")
    security_file_restrict_users: bool = Field(default=True, description="Restrict file access to users")
    security_enable_login_with_root: bool = Field(default=False, description="Enable login with root")

    # request logging
    security_log_public_requests: bool = Field(default=False, description="Log public requests (DEPRECATED)")
    security_log_private_requests: bool = Field(default=False, description="Log private requests (DEPRECATED)")

    # google auth
    security_google_oauth_client_id: str = Field(default="", description="Google OAuth client ID")
    security_google_oauth_client_secret: str = Field(default="", description="Google OAuth client secret")

    # performance
    performance_default_fetch_dict: bool = Field(default=False, description="Default fetch dictionary")
    multiple_count_use_threads: bool = Field(default=True, description="Use threads for multiple count")

    # modules
    module_auth_enabled: bool = Field(default=True, description="Enable auth module")
    module_user_enabled: bool = Field(default=True, description="Enable user module")
    module_google_auth_enabled: bool = Field(default=False, description="Enable Google auth module")
    module_ftp_enabled: bool = Field(default=False, description="Enable FTP module")
    module_files_enabled: bool = Field(default=True, description="Enable files module")
    module_blacklist_enabled: bool = Field(default=False, description="Enable blacklist module")
    module_maintenance_enabled: bool = Field(default=False, description="Enable maintenance module")
    module_notification_enabled: bool = Field(default=False, description="Enable notification module")
    module_kvstore_enabled: bool = Field(default=False, description="Enable key-value store module")
    module_limiter_enabled: bool = Field(default=True, description="Enable limiter module")
    modules: List[str] = Field(default_factory=list, description="List of enabled modules")

    # sending notifications to email
    notifications_send_mail: bool = Field(default=False, description="Send notifications to email")

    # files and directories
    tmp_directory: str = Field(default="./tmp", description="Temporary directory")
    files_directory: str = Field(default="./files", description="Files directory")
    files_read_endpoint: str = Field(default="/public/file/read", description="Files read endpoint")
    storage_type: str = Field(default="filesystem", description="Storage type (filesystem, s3)")

    aws_key: str = Field(default="", description="AWS key")
    aws_secret: str = Field(default="", description="AWS secret")
    aws_region: str = Field(default="", description="AWS region")


class ApplicationConfig():
    """
    ApplicationConfig class

    holds application config object
    """
    # static
    config: Config

    @classmethod
    def set_config(cls, config: Config) -> None:
        """ set config """
        cls.config = config

    @classmethod
    def from_json(cls, json_filename: str) -> Config:
        """ from json """
        cls.config = config_factory(json_filename)
        return cls.config


def get_config() -> Config:
    """
    Retrieve the current application configuration.
    Returns:
        Config: The current application configuration instance.
    """
    return ApplicationConfig.config


def get_custom_config() -> CustomConfig:
    """
    Retrieve the custom configuration from the application configuration.

    Returns:
        CustomConfig: The custom configuration object.
    """
    return ApplicationConfig.config.custom


def config_factory(json_filename: str) -> Config:
    """
    Creates a Config object from a JSON file.
    Args:
        json_filename (str): The path to the JSON file containing the configuration.
    Returns:
        Config: An instance of the Config class populated with the data from the JSON file.
    """
    with open(json_filename, "r") as config_fd:
        return Config(
            **json.loads(
                config_fd.read()
            )
        )


if __name__ == '__main__':
    exit()
