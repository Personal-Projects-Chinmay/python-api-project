#! /usr/bin/env python

import pytest

from app.create_app import (  # so that we dont start the app when going to our unit tests
    create_application,
)
from models.base import engine, recreate_tables


@pytest.fixture(scope="function")
def base_testing_app():
    app = create_application()
    recreate_tables(engine)
    # testing_app = TestClient(app)
    return app


@pytest.fixture
def testing_rate_limit() -> int:
    return 50


@pytest.fixture(scope="session")
def sample_full_user_profile() -> dict:
    return dict(
        short_description="short_desc",
        long_bio="def",
        name="abc",
        liked_posts=[1, 2, 3],
    )
