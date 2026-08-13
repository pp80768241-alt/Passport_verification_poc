"""Passport verification POC — local foundation."""

from passport_verification.models import (
    ExtractedPassportDetails,
    PassportVerificationResult,
)
from passport_verification.verification import verify_passport_details
