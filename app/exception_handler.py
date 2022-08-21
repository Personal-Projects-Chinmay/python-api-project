#! /usr/bin/env python

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.exceptions import UserAlreadyExists, UserNotFound

logger = logging.getLogger(__name__)


def add_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(UserNotFound)
    async def handle_user_not_found_exception(request: Request, exc: UserNotFound):
        logger.error(f"Non-existent user_id: {exc.user_id} was requested")
        return JSONResponse(status_code=404, content="User does not exist")

    @app.exception_handler(UserAlreadyExists)
    async def handle_user_exist_exception(request: Request, exc: UserAlreadyExists):
        logger.error("Tried to insert user that already exists")
        return JSONResponse(status_code=400, content="User already exist")

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error_exception(request: Request, exc: IntegrityError):
        logger.error("Encountered integrity error when inserting user")
        return JSONResponse(
            status_code=400, content="User conflicts with existing user"
        )  # it may not be nice for consumer but can also add content=str(exc)

    return None
