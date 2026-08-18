import base64
import json

from unittest.mock import patch

import pytest

from passport_verification.handler import lambda_handler
from passport_verification.storage import S3UploadError
from tests.conftest import build_event


class FakeContext:
    aws_request_id = "test-request-id"


@pytest.fixture(autouse=True)
def mock_s3_upload():
    with patch(
        "passport_verification.handler.upload_passport_image",
        return_value="passports/test-key.bin",
    ) as mock:
        yield mock


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


def test_integration_valid_passport(synthetic_image_base64):
    event = build_event(
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "passport_image": synthetic_image_base64,
            "extracted_passport_details": {
                "first_name": "Jane",
                "last_name": "Doe",
                "expiry_date": "2030-12-31",
            },
        }
    )

    response = lambda_handler(event, FakeContext())

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"success": True}


def test_integration_wrong_first_name(synthetic_image_base64):
    event = build_event(
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "passport_image": synthetic_image_base64,
            "extracted_passport_details": {
                "first_name": "John",
                "last_name": "Doe",
                "expiry_date": "2030-12-31",
            },
        }
    )

    response = lambda_handler(event, FakeContext())

    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["success"] is False
    assert body["failure_reasons"] == ["FIRST_NAME_MISMATCH"]


def test_integration_expired_passport(synthetic_image_base64):
    event = build_event(
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "passport_image": synthetic_image_base64,
            "reference_date": "2026-08-13",
            "extracted_passport_details": {
                "first_name": "Jane",
                "last_name": "Doe",
                "expiry_date": "2026-08-12",
            },
        }
    )

    response = lambda_handler(event, FakeContext())

    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["success"] is False
    assert body["failure_reasons"] == ["PASSPORT_EXPIRED"]


def test_integration_multiple_failures(synthetic_image_base64):
    event = build_event(
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "passport_image": synthetic_image_base64,
            "reference_date": "2026-08-13",
            "extracted_passport_details": {
                "first_name": "John",
                "last_name": "Smith",
                "expiry_date": "2026-08-12",
            },
        }
    )

    response = lambda_handler(event, FakeContext())

    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["success"] is False
    assert set(body["failure_reasons"]) == {
        "FIRST_NAME_MISMATCH",
        "LAST_NAME_MISMATCH",
        "PASSPORT_EXPIRED",
    }


def test_s3_upload_failure_returns_500(synthetic_image_base64):
    event = build_event(
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "passport_image": synthetic_image_base64,
        }
    )

    with patch(
        "passport_verification.handler.upload_passport_image",
        side_effect=S3UploadError("S3 Connection failed"),
    ):
        response = lambda_handler(event, FakeContext())

    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"success": False}


