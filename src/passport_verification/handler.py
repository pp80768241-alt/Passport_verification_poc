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

    if payload is not None:
        extracted_data = payload.get("extracted_passport_details")
        if extracted_data is not None:
            if not isinstance(extracted_data, dict):
                return build_api_gateway_response(
                    status_code=400,
                    response=VerificationResponse(
                        success=False,
                        failure_reasons=("INVALID_EXTRACTED_DATA",),
                    ),
                )

            ext_first_name = extracted_data.get("first_name")
            ext_last_name = extracted_data.get("last_name")
            ext_expiry_str = extracted_data.get("expiry_date")

            if (
                not isinstance(ext_first_name, str)
                or not isinstance(ext_last_name, str)
                or not isinstance(ext_expiry_str, str)
            ):
                return build_api_gateway_response(
                    status_code=400,
                    response=VerificationResponse(
                        success=False,
                        failure_reasons=("INVALID_EXTRACTED_DATA",),
                    ),
                )

            from datetime import date
            try:
                ext_expiry = date.fromisoformat(ext_expiry_str)
            except ValueError:
                return build_api_gateway_response(
                    status_code=400,
                    response=VerificationResponse(
                        success=False,
                        failure_reasons=("INVALID_EXPIRY_DATE_FORMAT",),
                    ),
                )

            from passport_verification.models import ExtractedPassportDetails
            from passport_verification.verification import verify_passport_details

            extracted = ExtractedPassportDetails(
                first_name=ext_first_name,
                last_name=ext_last_name,
                expiry_date=ext_expiry,
            )

            ref_date_str = payload.get("reference_date")
            ref_date = None
            if ref_date_str and isinstance(ref_date_str, str):
                try:
                    ref_date = date.fromisoformat(ref_date_str)
                except ValueError:
                    pass

            assert validation_result.request is not None
            verification_result = verify_passport_details(
                extracted=extracted,
                expected_first_name=validation_result.request.first_name,
                expected_last_name=validation_result.request.last_name,
                reference_date=ref_date,
            )

            if not verification_result.is_verified:
                logger.info(
                    "Request failed passport verification",
                    extra={
                        "request_id": request_id,
                        "failure_reasons": verification_result.failure_reasons,
                    },
                )
                return build_api_gateway_response(
                    status_code=400,
                    response=VerificationResponse(
                        success=False,
                        failure_reasons=verification_result.failure_reasons,
                    ),
                )

    return build_api_gateway_response(
        status_code=200,
        response=VerificationResponse(success=True),
    )
