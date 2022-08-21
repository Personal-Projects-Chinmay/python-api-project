#! /usr/bin/env python

import time

from fastapi import HTTPException, Response

count = 0
start_time = (
    time.time()
)  # kind of logical bug here as it takes into account the start time when app starts and not when first request comes in, ignoring for now
reset_interval = 10
limit = 50


def rate_limit(response: Response) -> None:
    global start_time
    global count

    if time.time() > start_time + reset_interval:
        start_time = time.time()
        count = 0
    if count >= limit:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "timeout": round(start_time + reset_interval - time.time(), 2)
                + 0.01,  # time remaining
            },
        )
    count += 1
    response.headers["X-app-rate-limit"] = f"{count}:{limit}"
    return None
