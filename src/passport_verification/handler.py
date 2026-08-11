import json
import logging
from typing import Any

from passport_verification.models import VerificationResponse
from passport_verification.response import build_api_gateway_response
from passport_verification.validation import validate_request_payload

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _parse_body(event: dict[str, Any]) -> dict[str, object] | None:
    body = event.get("body")
    if body is None:
        return None

    if isinstance(body, dict):
        return body

    if isinstance(body, str):
        if body == "":
            return None
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            return None
        if isinstance(parsed, dict):
            return parsed
        return None

    return None


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    request_id = getattr(context, "aws_request_id", None) if context else None
    logger.info("Processing verification request", extra={"request_id": request_id})

    payload = _parse_body(event)
    validation_result = validate_request_payload(payload)

    if not validation_result.is_valid:
        logger.info(
            "Request failed structural validation",
            extra={"request_id": request_id},
        )
        return build_api_gateway_response(
            status_code=400,
            response=VerificationResponse(success=False),
        )

    logger.info(
        "Request passed structural validation",
        extra={"request_id": request_id},
    )
    return build_api_gateway_response(
        status_code=200,
        response=VerificationResponse(success=True),
    )
