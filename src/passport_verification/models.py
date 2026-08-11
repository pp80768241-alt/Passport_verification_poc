from dataclasses import dataclass
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
