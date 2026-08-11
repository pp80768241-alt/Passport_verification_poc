import base64

from passport_verification.validation import (
    DEFAULT_MAX_IMAGE_BYTES,
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


def test_exceeds_dev_safety_limit(synthetic_image_base64):
    oversized = base64.b64encode(b"x" * (DEFAULT_MAX_IMAGE_BYTES + 1)).decode("ascii")

    result = validate_request_payload(
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "passport_image": oversized,
        }
    )

    assert result.is_valid is False


def test_custom_dev_safety_limit_allows_smaller_limit(synthetic_image_base64):
    small_limit = 10

    result = validate_request_payload(
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "passport_image": synthetic_image_base64,
        },
        max_image_bytes=small_limit,
    )

    assert result.is_valid is False
