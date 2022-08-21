from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base

from app.config import Config

Base = declarative_base()
config = Config()

engine = create_engine(config.postgres_host)  # add echo=True to print the logs


def recreate_tables(engine: Engine):  # helper function
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
