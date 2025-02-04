#!/usr/bin/env python3

"""
uni.testing

"""
from __future__ import annotations
from typing import Any, Tuple, Dict

from fastapi import Response
from fastapi.testclient import TestClient
from init import init
from uni.default import UniDefault
from uni.utils import password_hash
from uni.version import API_PREFIX
from .application import UniBackend
from .database import database_factory
from .exceptions import TestError
from .modules.user.model import db_User
from .config import ApplicationConfig
from .logger import color_green, core_logger, set_logging_dev, set_logging_production
from .config import Config


logger = core_logger().getChild("testing")

_TEST_USER_EMAIL = "test@test.com"
_TEST_USER_PASSWORD = "test1234"


class AppTesting(UniDefault):
    def __init__(self, app: UniBackend):
        logger.info("Initializing AppTesting")
        self._db = database_factory()
        self._app = app
        logger.info("Creating test user")
        self._client = TestClient(self._app.fastapi)
        self._token = ""
        self._user = None
        self._create_test_user()
        self._auth()

    def __enter__(self) -> AppTesting:
        """
        Method that is called when entering a context block.
        Returns:
            AppTesting: The AppTesting instance.
        """
        return self
    
    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """
        Method that is called when exiting a context block.
        Deletes the test user from the database.
        """
        self._delete_test_user()
        self._client.close()

    def _create_test_user(self) -> None:
        """
        Creates a test user in the database with predefined credentials.
        This method initializes a test user with a specific email, password hash, 
        and security salt, and sets the user as a root user. It then attempts to 
        create the user in the database. If the creation fails, a TestError is raised.
        Raises:
            TestError: If the test user cannot be created in the database.
        """
        self._user = db_User(
            email=_TEST_USER_EMAIL,
            password_hash=password_hash(_TEST_USER_PASSWORD),
            salt=self._app.config.security_password_salt,
            root=True
        )
        r = self._db.create(self._user)
        if not r:
            raise TestError("Failed to create test user")

    def _delete_test_user(self) -> None:
        """
        Deletes the test user from the database.
        This method checks if a test user exists and attempts to delete it from the database.
        If the deletion fails, a TestError is raised. Upon successful deletion, the user ID is set to None.
        Raises:
            TestError: If the test user could not be deleted.
        """

        if not self._user:
            return
        r = self._db.delete(self._user)

        if not r:
            raise TestError("Failed to delete test user")
        self._user_id = None

    def _auth(self) -> None:
        """
        Authenticates the client using predefined test user credentials.
        Sends a GET request to the authentication endpoint and checks if the 
        response status code is 200. If authentication is successful, stores 
        the received token. Raises a TestError if authentication fails.
        Raises:
            TestError: If the authentication request fails (status code is not 200).
        """

        r = self._client.get(
            "/api/v1/auth", auth=(_TEST_USER_EMAIL, _TEST_USER_PASSWORD))
        if r.status_code != 200:
            raise TestError("Auth failed")
        self._token = r.json()["token"]

    def get(self, endpoint: str, prefix: str = API_PREFIX) -> Response:
        """
        Sends a GET request to the specified endpoint.
        Args:
            endpoint (str): The API endpoint to send the GET request to.
            prefix (str, optional): The prefix to be added to the endpoint. Defaults to API_PREFIX.
        Returns:
            Response: The response object from the GET request.
        """
        return self._client.get(prefix+endpoint, headers={"token": self._token})
        

    def post(self, endpoint: str, data: Dict[str, Any], prefix: str = API_PREFIX) -> Response:
        """
        Sends a POST request to the specified endpoint with the given data.

        Args:
            endpoint (str): The API endpoint to send the request to.
            data (Dict[str, Any]): The data to be sent in the request body.
            prefix (str, optional): The prefix to be added to the endpoint. Defaults to API_PREFIX.

        Returns:
            Response: The response object from the POST request.
        """
        return self._client.post(prefix+endpoint, json=data, headers={"token": self._token})

    @staticmethod
    def basic(test_name: str, config_path: str = "config_test.json", debug: bool = False) -> Config:
        """
        Initializes basic tests for the given test name using the specified configuration file.
        Args:
            test_name (str): The name of the test to run.
            config_path (str, optional): The path to the configuration file. Defaults to "config_test.json".
            debug (bool, optional): Whether to enable debug logging. Defaults to False.
        Returns:
            Config: The configuration used for the test.
        """
        if debug: set_logging_dev()
        else: set_logging_production()
        init()
        ApplicationConfig.from_json(config_path)

        logger.info(color_green(f"Running tests for {test_name}"))
        return ApplicationConfig.config

    @classmethod
    def api(cls, test_name: str, config_path: str = "config_test.json", debug: bool = False) -> AppTesting:
        """
        Initializes and returns an instance of AppTesting for API tests.
        Args:
            test_name (str): The name of the test to run.
            config_path (str, optional): The path to the configuration file. Defaults to "config_test.json".
            debug (bool, optional): Whether to enable debug logging. Defaults to False.
        Returns:
            AppTesting: An instance of the AppTesting class initialized with the specified test configuration.
        """
        cfg = ApplicationConfig.from_json(config_path)
        if debug: set_logging_dev()
        else: set_logging_production()
        app = UniBackend(config=cfg)

        logger.info(color_green(f"Running API tests for {test_name}"))
        return cls(app)


if __name__ == '__main__':
    exit()
