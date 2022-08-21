#! /usr/bin/env python

from pydantic import BaseSettings, PostgresDsn, RedisDsn


class Config(BaseSettings):
    # DB_HOST = os.getenv("DB_HOST", "my.database.com")
    postgres_host: PostgresDsn  # os.getenv("db_host")
    redis_host: RedisDsn

    class Config:
        env_prefix = "db_"
