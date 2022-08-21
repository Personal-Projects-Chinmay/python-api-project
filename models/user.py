import datetime

from sqlalchemy import TIMESTAMP, Column, Integer, String, UniqueConstraint

from models.base import Base


class User(Base):
    __tablename__ = "user"  # table contains user object hence singular

    __table_args__ = (
        UniqueConstraint("username", name="username_unique"),
    )  # needs to be a tuple

    id = Column(Integer, primary_key=True)  # can be a UUID string instead of integer
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    username = Column(String, nullable=False)
    short_description = Column(String, nullable=False)
    long_bio = Column(String)
    # can add email, password columns
