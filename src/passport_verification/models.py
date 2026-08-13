from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class VerificationRequest:
    first_name: str
    last_name: str
    passport_image: str


@dataclass(frozen=True)
class VerificationResponse:
    success: bool

    def to_dict(self) -> dict[str, bool]:
        return {"success": self.success}


@dataclass(frozen=True)
class ApiGatewayResponse:
    status_code: int
    body: dict[str, Any]


@dataclass(frozen=True)
class ExtractedPassportDetails:
    first_name: str
    last_name: str
    expiry_date: date


@dataclass(frozen=True)
class PassportVerificationResult:
    is_verified: bool
    first_name_match: bool
    last_name_match: bool
    is_not_expired: bool
    failure_reasons: tuple[str, ...]

