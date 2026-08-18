import os
import uuid
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

DEFAULT_BUCKET = "passport-verification-poc-2004-pp"


class S3UploadError(Exception):
    """Raised when an S3 image upload operation fails."""

    pass


def upload_passport_image(
    image_bytes: bytes,
    bucket_name: str | None = None,
    s3_client: Any = None,
) -> str:
    """Uploads decoded passport image bytes to S3 under the 'passports/' prefix.

    Args:
        image_bytes: Decoded bytes of the passport image.
        bucket_name: Target S3 bucket name. Defaults to PASSPORT_BUCKET env var
          or DEFAULT_BUCKET.
        s3_client: Optional pre-configured boto3 S3 client (useful for dependency injection / mocking).

    Returns:
        The generated S3 object key (e.g. 'passports/uuid.bin').

    Raises:
        S3UploadError: If the upload operation fails due to boto3/S3 errors.
    """
    if bucket_name is None:
        bucket_name = os.getenv("PASSPORT_BUCKET", DEFAULT_BUCKET)

    if s3_client is None:
        s3_client = boto3.client("s3")

    object_key = f"passports/{uuid.uuid4()}.bin"

    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=image_bytes,
        )
    except (BotoCoreError, ClientError) as e:
        raise S3UploadError(f"Failed to upload image to S3: {e}") from e

    return object_key
