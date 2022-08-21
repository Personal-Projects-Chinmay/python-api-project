#! /usr/bin/env python

import pytest
from aioresponses import aioresponses

from sample_requests.async_requests import sample_async_get_request


@pytest.mark.asyncio
async def test_sample_async_get_request_works_properly():
    base_url = ""
    endpoint_prefix = ""
    user_id = 1

    with aioresponses() as m:
        m.get(
            f"{base_url}{endpoint_prefix}{user_id}",
            status=200,
            headers={"some_headers": "1"},
            payload={"user": user_id},
        )

        status_code, json_response, headers = await sample_async_get_request(
            base_url, endpoint_prefix, user_id
        )  # needa to be intended as same level as the contact maanger otherwise request would not be properly intercepted then

    assert status_code == 200
    assert json_response["user"] == user_id
    assert headers["some_headers"] == "1"
