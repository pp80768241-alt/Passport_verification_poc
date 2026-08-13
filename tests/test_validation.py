import base64

from passport_verification.validation import (
    validate_request_payload,
)


def test_valid_payload(synthetic_image_base64):
    result = validate_request_payload(
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "passport_image": synthetic_image_base64,
        }
    )

    assert result.is_valid is True
    assert result.request is not None
    assert result.request.first_name == "Jane"
    assert result.request.last_name == "Doe"


def test_missing_field():
    result = validate_request_payload({"first_name": "Jane", "last_name": "Doe"})

    assert result.is_valid is False
    assert result.request is None


def test_empty_string_field(synthetic_image_base64):
    result = validate_request_payload(
        {
            "first_name": "   ",
            "last_name": "Doe",
            "passport_image": synthetic_image_base64,
        }
    )

    assert result.is_valid is False


def test_invalid_base64():
    result = validate_request_payload(
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "passport_image": "not-valid-base64",
        }
    )

    assert result.is_valid is False


def test_empty_decoded_image():
    result = validate_request_payload(
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "passport_image": base64.b64encode(b"").decode("ascii"),
        }
    )

    assert result.is_valid is False
