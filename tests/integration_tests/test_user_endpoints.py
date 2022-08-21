#! /usr/bin/env python

from fastapi.testclient import TestClient


def test_delete_user_success(base_testing_app):
    user_id = 1
    with TestClient(base_testing_app) as testing_app:
        response = testing_app.delete(f"/user/{user_id}")
        assert response.status_code == 200


# def test_double_delete_user_fails(base_testing_app):
#     user_id = 1
#     with TestClient(base_testing_app) as testing_app:
#         response = testing_app.delete(f"/user/{user_id}")
#         assert response.status_code == 200

#         second_response = testing_app.delete(f"/user/{user_id}")
#         assert second_response.status_code == 404
#         assert second_response.json() == "User does not exist"


# def test_invalid_delete_user_id_fails(base_testing_app, invalid_user_delete_id):
#     with TestClient(base_testing_app) as testing_app:
#         second_response = testing_app.delete(f"/user/{invalid_user_delete_id}")
#         assert second_response.status_code == 404
#         assert second_response.json() == "User does not exist"


def test_put_user_returns_correct_results(base_testing_app, sample_full_user_profile):
    with TestClient(base_testing_app) as testing_app:
        user_id = 1
        response = testing_app.put(f"/user/{user_id}", json=sample_full_user_profile)

        assert response.status_code == 200


def test_put_user_twice_returns_correct_results(
    base_testing_app, sample_full_user_profile
):
    with TestClient(base_testing_app) as testing_app:
        user_id = 1
        response = testing_app.put(f"/user/{user_id}", json=sample_full_user_profile)
        assert response.status_code == 200

        second_response = testing_app.put(
            f"/user/{user_id}", json=sample_full_user_profile
        )
        assert second_response.status_code == 200


# def test_get_valid_user_returns_correct_result(base_testing_app, valid_user_id):
#     with TestClient(base_testing_app) as testing_app:
#         response = testing_app.get(f"/user/{valid_user_id}")

#         assert response.status_code == 200
#         assert response.json()["long_bio"] == "This is our longer bio"


def test_rate_limit_works(
    base_testing_app, testing_rate_limit, sample_full_user_profile
):
    user_id = 1
    with TestClient(base_testing_app) as testing_app:
        testing_app.put(f"/user/{user_id}", json=sample_full_user_profile)
        for i in range(testing_rate_limit * 2):
            response = testing_app.get(f"/user/{user_id}")
            if "X-app-rate-limit" not in response.headers:
                assert response.status_code == 429
