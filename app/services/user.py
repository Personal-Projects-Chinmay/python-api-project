#! /usr/bin/env python

from typing import Dict, List, Optional, Tuple, Union

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import Select

from app.clients.db import DatabaseClient
from app.exceptions import UserAlreadyExists, UserNotFound
from app.schemas.user import FullUserProfile


class UserService:
    def __init__(self, database_client: DatabaseClient) -> None:
        self.database_client = database_client

    async def get_all_users_with_pagination(
        self, offset: int, limit: int
    ) -> Tuple[List[FullUserProfile], int]:
        query = self._get_user_info_query()
        users = await self.database_client.get_paginated(query, limit, offset=offset)

        total_query = select(func.count(self.database_client.user.c.id).label("total"))
        total_res = await self.database_client.get_first(total_query)
        total = 0
        if total_res:
            total = total_res[0]
        user_infos = []

        for user in users:
            user_info = dict(zip(user._mapping.keys(), user._mapping.values()))
            full_user_profile = FullUserProfile(**user_info)
            user_infos.append(full_user_profile)

        return user_infos, total

    async def create_user(self, full_profile_info: FullUserProfile) -> int:
        # Alternatively could create a pydantic model but will require some
        # refactor of other models to keep things clean
        data = dict(
            username=full_profile_info.username,
            short_description=full_profile_info.short_description,
            long_bio=full_profile_info.long_bio,
        )
        insert_stmt = (
            insert(self.database_client.user)
            .values(**data)
            .returning(self.database_client.user.c.id)
        )  # usually insert doesnt return anything but here can use returning to return the id column
        insert_stmt = insert_stmt.on_conflict_do_nothing(
            index_elements=["username"]
        )  # for multiple we can easily do e.g. .values([{**data}])
        res = await self.database_client.get_first(insert_stmt)  # (1, )
        if not res:
            raise UserAlreadyExists
        user_id = res[
            0
        ]  # as res is a tuple we need only first element which is the id column
        return user_id

    async def create_update_user(
        self, full_profile_info: FullUserProfile, user_id: int
    ) -> int:
        """
        Create user and new unique user id if not exist otherwise update the user.
        Placeholder implementation later to be updated with DB.
        :param full_profile_info: FullUserProfile - User information saved in database
        :param user_id: Optional[int] - user_id if already exists, otherwise to be set
        :return: user_id: int - existing or new user id
        """
        data_no_id = dict(
            username=full_profile_info.username,
            short_description=full_profile_info.short_description,
            long_bio=full_profile_info.long_bio,
        )
        data: Dict[str, Union[str, int]] = {**data_no_id, "id": user_id}

        # query = self._get_user_info_query(user_id)
        query = select(self.database_client.user).where(
            self.database_client.user.c.id == user_id
        )
        user = await self.database_client.get_first(query)
        if not user:
            stmt = (
                insert(self.database_client.user)
                .values(**data)
                .returning(
                    self.database_client.user.c.id
                )  # postgres supports this but sqlite does not
            )
        else:
            stmt = (
                update(self.database_client.user)
                .where(self.database_client.user.c.id == user_id)
                .values(**data_no_id)
            )
        await self.database_client.get_first(stmt)
        return user_id

    async def get_user_info(
        self, user_id: int = 0
    ) -> FullUserProfile:  # changing to integer becoz of databases (strings are usually in kind of hash form)
        query = self._get_user_info_query(user_id)
        user = await self.database_client.get_first(query)
        if not user:
            raise UserNotFound(user_id=user_id)

        user_info = dict(zip(user._mapping.keys(), user._mapping.values()))

        return FullUserProfile(**user_info)

    # async def partial_update_user(self, user_id: int, user_profile_info: UserProfileInfo) -> None:
    #     short_description = user_profile_info.short_description
    #     long_bio = user_profile_info.long_bio
    #     self.profile_infos[user_id] = {
    #         "short_description": short_description,
    #         "long_bio": long_bio,
    #     }
    #     return None

    async def delete_user(self, user_id: int) -> None:
        delete_stmt = delete(self.database_client.user).where(
            self.database_client.user.c.id == user_id
        )
        await self.database_client.execute_in_transaction(delete_stmt)

    def _get_user_info_query(self, user_id: Optional[int] = None) -> Select:
        liked_posts_query = select(
            self.database_client.liked_post.c.user_id,
            func.array_agg(self.database_client.liked_post.c.post_id).label(
                "liked_posts"
            ),  # if table has 5 rows then the array agg func brings them into single row with 5 elements
        ).group_by(self.database_client.liked_post.c.user_id)
        if user_id:
            liked_posts_query = liked_posts_query.where(
                self.database_client.liked_post.c.user_id == user_id
            )
        liked_posts_query = liked_posts_query.cte("liked_posts_query")

        query = select(
            self.database_client.user.c.short_description,
            self.database_client.user.c.long_bio,
            self.database_client.user.c.username.label("name"),
            liked_posts_query.c.liked_posts,
        ).join(
            liked_posts_query,
            liked_posts_query.c.user_id == self.database_client.user.c.id,
            isouter=True,
        )
        if user_id:
            query = query.where(self.database_client.user.c.id == user_id)

        return query
