import base64
import binascii
from dataclasses import dataclass

from passport_verification.models import VerificationRequest


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    request: VerificationRequest | None = None


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and value.strip() != ""


def validate_request_payload(
    payload: dict[str, object] | None,
) -> ValidationResult:
    if payload is None:
        return ValidationResult(is_valid=False)

    first_name = payload.get("first_name")
    last_name = payload.get("last_name")
    passport_image = payload.get("passport_image")

    if not all(
        _is_non_empty_string(field)
        for field in (first_name, last_name, passport_image)
    ):
        return ValidationResult(is_valid=False)

    assert isinstance(first_name, str)
    assert isinstance(last_name, str)
    assert isinstance(passport_image, str)

    try:
        decoded_image = base64.b64decode(passport_image, validate=True)
    except (binascii.Error, ValueError):
        return ValidationResult(is_valid=False)

    if len(decoded_image) == 0:
        return ValidationResult(is_valid=False)

    return ValidationResult(
        is_valid=True,
        request=VerificationRequest(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            passport_image=passport_image.strip(),
        ),
    )
