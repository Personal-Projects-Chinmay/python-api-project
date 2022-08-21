import datetime

from sqlalchemy import (
    TIMESTAMP,
    Column,
    ForeignKeyConstraint,
    Index,
    Integer,
    UniqueConstraint,
)

from models.base import Base


class LikedPost(Base):
    __tablename__ = "liked_post"

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="user_post_unique"),
        ForeignKeyConstraint(["user_id"], ["user.id"]),
    )  # user.id is the user table in user.py and id column

    id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    user_id = Column(Integer, nullable=False)
    post_id = Column(Integer, nullable=False)  # which user liked which post


Index("liked_post_user_id_idx", LikedPost.user_id)  # .c to access column value
