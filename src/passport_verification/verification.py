from datetime import date
from passport_verification.models import ExtractedPassportDetails, PassportVerificationResult


def verify_passport_details(
    extracted: ExtractedPassportDetails,
    expected_first_name: str,
    expected_last_name: str,
    reference_date: date | None = None,
) -> PassportVerificationResult:
    """Verifies that extracted passport details match the expected user's first and last name

    and that the passport has not expired as of the reference_date (defaults to today).
    """
    if reference_date is None:
        reference_date = date.today()

    first_name_match = (
        extracted.first_name.strip().lower() == expected_first_name.strip().lower()
    )
    last_name_match = (
        extracted.last_name.strip().lower() == expected_last_name.strip().lower()
    )
    is_not_expired = extracted.expiry_date >= reference_date

    failure_reasons: list[str] = []
    if not first_name_match:
        failure_reasons.append("FIRST_NAME_MISMATCH")
    if not last_name_match:
        failure_reasons.append("LAST_NAME_MISMATCH")
    if not is_not_expired:
        failure_reasons.append("PASSPORT_EXPIRED")

    is_verified = first_name_match and last_name_match and is_not_expired

    return PassportVerificationResult(
        is_verified=is_verified,
        first_name_match=first_name_match,
        last_name_match=last_name_match,
        is_not_expired=is_not_expired,
        failure_reasons=tuple(failure_reasons),
    )
