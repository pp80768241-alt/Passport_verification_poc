import os
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from passport_verification.storage import (
    DEFAULT_BUCKET,
    S3UploadError,
    upload_passport_image,
)


def test_successful_upload():
    mock_s3_client = MagicMock()
    sample_bytes = b"fake-passport-image-bytes"

    object_key = upload_passport_image(
        image_bytes=sample_bytes,
        bucket_name="my-test-bucket",
        s3_client=mock_s3_client,
    )

    assert object_key.startswith("passports/")
    assert object_key.endswith(".bin")
    mock_s3_client.put_object.assert_called_once_with(
        Bucket="my-test-bucket",
        Key=object_key,
        Body=sample_bytes,
    )


def test_unique_object_key_generation():
    mock_s3_client = MagicMock()
    sample_bytes = b"image-bytes"

    key1 = upload_passport_image(image_bytes=sample_bytes, s3_client=mock_s3_client)
    key2 = upload_passport_image(image_bytes=sample_bytes, s3_client=mock_s3_client)

    assert key1 != key2
    assert key1.startswith("passports/")
    assert key2.startswith("passports/")


def test_correct_bucket_usage_default():
    mock_s3_client = MagicMock()
    sample_bytes = b"image-bytes"

    upload_passport_image(image_bytes=sample_bytes, s3_client=mock_s3_client)

    mock_s3_client.put_object.assert_called_once()
    call_kwargs = mock_s3_client.put_object.call_args.kwargs
    assert call_kwargs["Bucket"] == DEFAULT_BUCKET


def test_correct_bucket_usage_env_var(monkeypatch):
    monkeypatch.setenv("PASSPORT_BUCKET", "env-configured-bucket")
    mock_s3_client = MagicMock()
    sample_bytes = b"image-bytes"

    upload_passport_image(image_bytes=sample_bytes, s3_client=mock_s3_client)

    mock_s3_client.put_object.assert_called_once()
    call_kwargs = mock_s3_client.put_object.call_args.kwargs
    assert call_kwargs["Bucket"] == "env-configured-bucket"


def test_s3_client_failure_handling():
    mock_s3_client = MagicMock()
    error_response = {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}}
    mock_s3_client.put_object.side_effect = ClientError(
        error_response, "PutObject"
    )

    with pytest.raises(S3UploadError) as exc_info:
        upload_passport_image(
            image_bytes=b"sample-image",
            s3_client=mock_s3_client,
        )

    assert "Failed to upload image to S3" in str(exc_info.value)
