#! /usr/bin/env python

from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from pydantic import BaseModel
from sqlalchemy import create_engine

from app.clients.db import DatabaseClient
from app.config import Config
from app.schemas.user import FullUserProfile
from app.services.user import UserService
from models.base import engine, recreate_tables
from models.liked_post import LikedPost
from models.user import User


class SQliteConfig(
    BaseModel
):  # need to create as the existing uses the postgres connection
    host: str


class SQLiteDatabaseClient(DatabaseClient):
    def __init__(
        self, sqlite_config: SQliteConfig
    ):  # extends the DatabaseClient initializing the parent class with the tables and a temp engine
        temp_engine = create_engine(sqlite_config.host)
        recreate_tables(temp_engine)
        super(SQLiteDatabaseClient, self).__init__(sqlite_config, tables=["user", "liked_post"])  # type: ignore[arg-type]


@pytest.fixture
def _profile_infos():
    val = {
        0: {
            "short_description": "My bio description",
            "long_bio": "This is our longer bio",
        }
    }
    return val


@pytest.fixture
def _users_content():
    val = {0: {"liked_posts": [1] * 9}}
    return val


@pytest.fixture(scope="session")
def testing_config() -> Config:
    return Config()


@pytest.fixture(scope="session")
def sqlite_testing_config() -> SQliteConfig:
    host = "sqlite:///testting.db"
    return SQliteConfig(host=host)


@pytest_asyncio.fixture
async def testing_db_client(testing_config) -> DatabaseClient:  # type: ignore
    recreate_tables(engine)  # need to recreate tables for fresh session
    database_client = DatabaseClient(testing_config, ["user", "liked_post"])
    await database_client.connect()
    yield database_client  # yield so that after it is done we execute reset of code
    await database_client.disconnect()


@pytest_asyncio.fixture
async def sqlite_testing_db_client(sqlite_testing_config) -> DatabaseClient:
    database_client = SQLiteDatabaseClient(sqlite_testing_config)
    return database_client


@pytest.fixture
def user_service(testing_db_client) -> UserService:
    user_service = UserService(testing_db_client)
    return user_service  # does not need to match the function name


@pytest.fixture
def sqlite_user_service(sqlite_testing_db_client):
    sqlite_user_service = UserService(sqlite_testing_db_client)
    return sqlite_user_service


@pytest.fixture  # no scope going to reset every single time
def mocking_database_client() -> DatabaseClient:
    def side_effect(*args, **kwargs):
        return (1,)

    mock = (
        AsyncMock()
    )  # Mock(), MagicMock() has special dunder elements present for synchronous methods
    mock.user = User.__table__
    mock.liked_post = LikedPost.__table__
    mock.get_first.side_effect = side_effect  # AsyncMock(side_effect=[(1, ), (2. )])    # on first call returns 1 an second call returns 2
    return mock


@pytest.fixture
def user_service_mocked_db(mocking_database_client: DatabaseClient):
    user_service = UserService(mocking_database_client)
    return user_service


@pytest.fixture(
    scope="function", autouse=True
)  # scope defines at which level you want this function to be called, there can be some places where we want the functions to have same state and not called everytime for all the functions in same scope
def testing_fixture():  # autouse to true then every function will automatically use this
    print("Initializing fixture")
    yield "a"
    print("teardown stuff")


@pytest.fixture(scope="session")
def sample_full_user_profile():
    return FullUserProfile(
        short_description="short_desc",
        long_bio="def",
        name="abc",
        liked_posts=[1, 2, 3],
    )


# scope levels: function -> class -> module(file level) -> package(folder level) -> sesssion(only once across whole testing session)
