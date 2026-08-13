from datetime import date
from passport_verification.models import ExtractedPassportDetails
from passport_verification.verification import verify_passport_details


def test_verify_passport_fully_valid():
    extracted = ExtractedPassportDetails(
        first_name="Jane",
        last_name="Doe",
        expiry_date=date(2030, 12, 31),
    )

    result = verify_passport_details(
        extracted=extracted,
        expected_first_name="Jane",
        expected_last_name="Doe",
        reference_date=date(2026, 8, 13),
    )

    assert result.is_verified is True
    assert result.first_name_match is True
    assert result.last_name_match is True
    assert result.is_not_expired is True
    assert len(result.failure_reasons) == 0


def test_verify_passport_first_name_mismatch():
    extracted = ExtractedPassportDetails(
        first_name="John",
        last_name="Doe",
        expiry_date=date(2030, 12, 31),
    )

    result = verify_passport_details(
        extracted=extracted,
        expected_first_name="Jane",
        expected_last_name="Doe",
        reference_date=date(2026, 8, 13),
    )

    assert result.is_verified is False
    assert result.first_name_match is False
    assert result.last_name_match is True
    assert result.is_not_expired is True
    assert result.failure_reasons == ("FIRST_NAME_MISMATCH",)


def test_verify_passport_last_name_mismatch():
    extracted = ExtractedPassportDetails(
        first_name="Jane",
        last_name="Smith",
        expiry_date=date(2030, 12, 31),
    )

    result = verify_passport_details(
        extracted=extracted,
        expected_first_name="Jane",
        expected_last_name="Doe",
        reference_date=date(2026, 8, 13),
    )

    assert result.is_verified is False
    assert result.first_name_match is True
    assert result.last_name_match is False
    assert result.is_not_expired is True
    assert result.failure_reasons == ("LAST_NAME_MISMATCH",)


def test_verify_passport_expired():
    extracted = ExtractedPassportDetails(
        first_name="Jane",
        last_name="Doe",
        expiry_date=date(2026, 8, 12),
    )

    result = verify_passport_details(
        extracted=extracted,
        expected_first_name="Jane",
        expected_last_name="Doe",
        reference_date=date(2026, 8, 13),
    )

    assert result.is_verified is False
    assert result.first_name_match is True
    assert result.last_name_match is True
    assert result.is_not_expired is False
    assert result.failure_reasons == ("PASSPORT_EXPIRED",)


def test_verify_passport_expiring_today():
    # Passport expiring today is considered not expired / valid
    extracted = ExtractedPassportDetails(
        first_name="Jane",
        last_name="Doe",
        expiry_date=date(2026, 8, 13),
    )

    result = verify_passport_details(
        extracted=extracted,
        expected_first_name="Jane",
        expected_last_name="Doe",
        reference_date=date(2026, 8, 13),
    )

    assert result.is_verified is True
    assert result.first_name_match is True
    assert result.last_name_match is True
    assert result.is_not_expired is True
    assert len(result.failure_reasons) == 0


def test_verify_passport_expiring_tomorrow():
    extracted = ExtractedPassportDetails(
        first_name="Jane",
        last_name="Doe",
        expiry_date=date(2026, 8, 14),
    )

    result = verify_passport_details(
        extracted=extracted,
        expected_first_name="Jane",
        expected_last_name="Doe",
        reference_date=date(2026, 8, 13),
    )

    assert result.is_verified is True
    assert result.first_name_match is True
    assert result.last_name_match is True
    assert result.is_not_expired is True
    assert len(result.failure_reasons) == 0


def test_verify_passport_name_normalization():
    # Case insensitivity and whitespace trimming should allow matching
    extracted = ExtractedPassportDetails(
        first_name="  jaNe  ",
        last_name=" doE\n",
        expiry_date=date(2030, 12, 31),
    )

    result = verify_passport_details(
        extracted=extracted,
        expected_first_name="JANE\t",
        expected_last_name="  Doe ",
        reference_date=date(2026, 8, 13),
    )

    assert result.is_verified is True
    assert result.first_name_match is True
    assert result.last_name_match is True
    assert result.is_not_expired is True
    assert len(result.failure_reasons) == 0


def test_verify_passport_multiple_failures():
    extracted = ExtractedPassportDetails(
        first_name="John",
        last_name="Smith",
        expiry_date=date(2026, 8, 12),
    )

    result = verify_passport_details(
        extracted=extracted,
        expected_first_name="Jane",
        expected_last_name="Doe",
        reference_date=date(2026, 8, 13),
    )

    assert result.is_verified is False
    assert result.first_name_match is False
    assert result.last_name_match is False
    assert result.is_not_expired is False
    assert result.failure_reasons == (
        "FIRST_NAME_MISMATCH",
        "LAST_NAME_MISMATCH",
        "PASSPORT_EXPIRED",
    )


def test_verify_passport_default_reference_date():
    # When reference_date is None, verify_passport_details should use date.today()
    extracted = ExtractedPassportDetails(
        first_name="Jane",
        last_name="Doe",
        expiry_date=date(1970, 1, 1),
    )

    result = verify_passport_details(
        extracted=extracted,
        expected_first_name="Jane",
        expected_last_name="Doe",
    )

    # Today is 2026, so 1970 is definitely expired
    assert result.is_not_expired is False
    assert "PASSPORT_EXPIRED" in result.failure_reasons
