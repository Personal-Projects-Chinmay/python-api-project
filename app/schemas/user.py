#! /usr/bin/env python

from typing import List, Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    username: str = Field(  # Field is used to describe parameters
        alias="name",
        title="The Username",
        description="This is the username of the user",
        min_length=1,
        max_length=20,
        default=None,
    )
    liked_posts: Optional[List[int]] = Field(
        description="Array of post ids the user liked",
        # min_items=2,
        # max_items=10
    )


class UserProfileInfo(BaseModel):
    short_description: str
    long_bio: str


class FullUserProfile(
    User, UserProfileInfo
):  # no need to inherit BaseModel as it is already by User class
    pass


class MultipleUsersResponse(BaseModel):
    users: List[FullUserProfile]
    total: int


class CreateUserResponse(BaseModel):
    user_id: int
