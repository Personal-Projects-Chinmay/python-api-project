import os
from typing import List, Optional, Union

from databases import Database
from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Row
from sqlalchemy.sql.expression import Delete, Insert, Select

from app.config import Config


class DatabaseClient:
    def __init__(self, config: Config, tables: Optional[List[str]]):
        self.config = config
        self.engine = create_engine(self.config.postgres_host, future=True)
        self.metadata = MetaData(self.engine)
        self._reflect_metadata()  # metadata.tables["user"]
        if tables:  # does not trigger if tables is None or len(tables) == 0
            self._set_internal_database_tables(tables)

        if os.getenv("app_env") == "test":
            self.database = Database(self.config.postgres_host, force_rollback=True)
        else:
            self.database = Database(self.config.postgres_host)

    def _reflect_metadata(self) -> None:
        self.metadata.reflect()  # bring in the current state of database, might miss tables if they dont have primary key

    async def connect(self):
        await self.database.connect()

    async def disconnect(self):
        await self.database.disconnect()

    def _set_internal_database_tables(self, tables: List[str]):
        # e.g. sets DatabaseClient.user = DatabaseClient.metadata.tables["user"] if "user" in tables
        # for table in tables:
        #     setattr(self, table, self.metadata.tables[table])
        self.user = self.metadata.tables["user"]
        self.liked_post = self.metadata.tables["liked_post"]

    async def get_first(self, query: Union[Select, Insert]) -> Optional[Row]:
        async with self.database.transaction():
            res = await self.database.fetch_one(query)
        return res

    async def get_all(self, query: Select) -> List[Row]:
        async with self.database.transaction():  # required if transaction gets stuck in between then automatically handles
            res = await self.database.fetch_all(query)
        return res

    async def get_paginated(self, query: Select, limit: int, offset: int) -> List[Row]:
        query = query.limit(limit).offset(
            offset
        )  # limit the amout of data being sent in chunks
        return await self.get_all(query)

    async def execute_in_transaction(self, query: Delete):
        async with self.database.transaction():
            await self.database.execute(query)


# replace select statements in sql using python objects
