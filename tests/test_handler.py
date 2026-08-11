import base64
import json

from passport_verification.handler import lambda_handler
from tests.conftest import build_event


class FakeContext:
    aws_request_id = "test-request-id"


def test_valid_request_returns_success(synthetic_image_base64):
    event = build_event(
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "passport_image": synthetic_image_base64,
        }
    )

    response = lambda_handler(event, FakeContext())

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"success": True}
    assert response["headers"]["Content-Type"] == "application/json"


def test_missing_first_name_returns_failure(synthetic_image_base64):
    event = build_event(
        {
            "last_name": "Doe",
            "passport_image": synthetic_image_base64,
        }
    )

    response = lambda_handler(event, FakeContext())

    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"success": False}


def test_missing_last_name_returns_failure(synthetic_image_base64):
    event = build_event(
        {
            "first_name": "Jane",
            "passport_image": synthetic_image_base64,
        }
    )

    response = lambda_handler(event, FakeContext())

    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"success": False}


def test_missing_passport_image_returns_failure():
    event = build_event({"first_name": "Jane", "last_name": "Doe"})

    response = lambda_handler(event, FakeContext())

    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"success": False}


def test_invalid_json_body_returns_failure():
    event = build_event("{not-json")

    response = lambda_handler(event, FakeContext())

    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"success": False}


def test_invalid_base64_image_returns_failure():
    event = build_event(
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "passport_image": "!!!not-base64!!!",
        }
    )

    response = lambda_handler(event, FakeContext())

    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"success": False}


def test_empty_body_returns_failure():
    event = build_event("")

    response = lambda_handler(event, FakeContext())

    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"success": False}
