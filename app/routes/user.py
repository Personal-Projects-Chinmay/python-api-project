#! /usr/bin/env python
import logging

from fastapi import APIRouter, Depends

from app.clients.db import DatabaseClient
from app.clients.redis import RedisCache
from app.dependencies import rate_limit
from app.schemas.user import (
    CreateUserResponse,
    FullUserProfile,
    MultipleUsersResponse,
)
from app.services.user import UserService

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)-6s %(name)-15s %(asctime)s %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
    filename="log.txt",
)  # output the logs in logs.txt
logger.setLevel(logging.INFO)  # debug -> info -> warning -> error -> critical

console = logging.StreamHandler()
logger.addHandler(console)


def create_user_router(
    database_client: DatabaseClient, redis_cache: RedisCache
) -> APIRouter:  # profile_infos and users_content as args of dict earlier
    user_router = APIRouter(
        prefix="/user",
        tags=["user"],
        dependencies=[Depends(rate_limit)],  # add dependendencies across all endpoints
    )
    user_service = UserService(database_client)

    # Get list of all users
    @user_router.get(
        "/all", response_model=MultipleUsersResponse
    )  # need this at top otherwise it will try to match user_id param and complain
    async def get_all_users_paginated(
        start: int = 0, limit: int = 2
    ):  # have a start and end limit othewise the data would be too large to send in segments
        cache_key = redis_cache.get_pagination_key(limit)  # pagination:{limit}
        # user:pagination:5       0: [....]   1: [.....]
        # company:pagination:5    0: [....]   1: [.....]
        multiple_users_response = await redis_cache.hget(
            cache_key, start, redis_cache.user_prefix
        )
        if multiple_users_response:
            # return MultipleUsersResponse(**json.loads(multiple_users_response))
            return multiple_users_response

        users, total = await user_service.get_all_users_with_pagination(start, limit)
        formatted_users = MultipleUsersResponse(users=users, total=total)

        await redis_cache.hset(
            cache_key, {start: formatted_users}, redis_cache.user_prefix
        )
        await redis_cache.sadd(
            redis_cache.get_pagination_set_key(), limit, redis_cache.user_prefix
        )  # sets: user:pagination [1,5,10,20]  hashes: user:pagination:{limit}, now we can delete the specific limit that we want e.g. user:pagination:1
        return formatted_users

    @user_router.get("/{user_id}", response_model=FullUserProfile)
    async def get_user_by_id(
        user_id: int,
    ):  # meaning response value will be set to the return value of rate limit function
        """
        Endpoint for retrieving a FullUserProfile by the user's unique integer id
        :param user_id: int - unique monotonically increasing integer id
        :return: FullUserProfile
        """
        # try:
        # rate_limit(response)                                                          # calling rate limit function but better way through dependencies
        full_user_profile = await redis_cache.get(
            user_id, redis_cache.user_prefix
        )  # no longer a string but a python object
        if full_user_profile:
            # full_user_profile = FullUserProfile(**json.loads(full_user_profile))      # converting str to dict and json.dumps for vice-versa
            return full_user_profile

        full_user_profile = await user_service.get_user_info(user_id)
        await redis_cache.set(
            user_id, full_user_profile, redis_cache.user_prefix
        )  # no need to pass full_user_profile.json()
        # except KeyError:                                                              # better way to do this is using global exception handler
        #     logger.error(f"Non-existent user_id {user_id} was requested")
        #     raise HTTPException(status_code=404, detail="User does not exist")
        return full_user_profile

    # Update/Create existing user details
    @user_router.put("/{user_id}", response_model=CreateUserResponse)
    async def update_user(
        user_id: int, full_profile_info: FullUserProfile
    ) -> CreateUserResponse:
        user_id = await user_service.create_update_user(
            full_profile_info, user_id
        )  # always set in db first then cache
        await redis_cache.set(user_id, full_profile_info, redis_cache.user_prefix)
        await redis_cache.clear_pagination_cache(redis_cache.user_prefix)
        created_user_id = CreateUserResponse(user_id=user_id)
        return created_user_id

    # Delete cache
    @user_router.delete("/flush-cache", status_code=200)
    async def flushdb():
        await redis_cache.flushdb()
        return

    # Delete existing user
    @user_router.delete("/{user_id}")
    async def remove_user(user_id: int):
        logger.info(f"About to delete user_id {user_id}")
        # try:
        await user_service.delete_user(user_id)
        # except KeyError:
        #     raise HTTPException(status_code=404, detail={"msg": "User does not exist", "user_id": user_id})
        await redis_cache.delete(user_id, prefix=redis_cache.user_prefix)
        await redis_cache.clear_pagination_cache(redis_cache.user_prefix)

    # Sending data to server
    @user_router.post("/", response_model=CreateUserResponse, status_code=201)
    async def add_user(
        full_profile_info: FullUserProfile,
    ):  # input as pydantic model to know the expected body type
        user_id = await user_service.create_user(full_profile_info)
        await redis_cache.set(user_id, full_profile_info, redis_cache.user_prefix)
        await redis_cache.clear_pagination_cache(redis_cache.user_prefix)
        created_user_id = CreateUserResponse(
            user_id=user_id
        )  # convert to pydantic model CreateUserResponse
        return created_user_id

    # Modify existing user info
    # @user_router.patch("/{user_id}", response_model=FullUserProfile)
    # async def patch_user(user_id: int, user_profile_info: UserProfileInfo):
    #     if user_id not in profile_infos:
    #         pass
    #     await user_service.partial_update_user(user_id, user_profile_info)
    #     return user_service.get_user_info(user_id)

    @user_router.on_event("startup")  # when app starts up connect to db
    async def startup():
        await database_client.connect()

    @user_router.on_event("shutdown")  # when app shuts down disconnect from db
    async def shutdown():
        await database_client.disconnect()

    return user_router


# using async functions if function waiting for a response, the next function resumes its application
