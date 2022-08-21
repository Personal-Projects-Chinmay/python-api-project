#! /usr/bin/env python

import pytest


@pytest.fixture(scope="session")
def valid_user_id() -> int:
    return 0


@pytest.fixture(scope="session")
def invalid_user_delete_id() -> int:
    return 1
