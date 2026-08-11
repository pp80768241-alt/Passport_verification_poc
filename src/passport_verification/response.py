import json
from typing import Any

from passport_verification.models import ApiGatewayResponse, VerificationResponse


def build_api_gateway_response(
    status_code: int,
    response: VerificationResponse,
) -> dict[str, Any]:
    api_response = ApiGatewayResponse(status_code=status_code, body=response.to_dict())
    return {
        "statusCode": api_response.status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(api_response.body),
    }
