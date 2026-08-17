# Project Notes — Passport Verification POC

This document captures the overall goal, architecture, scope boundaries, progress, and key technical decisions for the Passport Verification Proof of Concept (POC).

---

## 1. Project Goal

The primary goal of this Proof of Concept (POC) is to build a secure, lightweight AWS-based passport verification flow. It serves as a foundation for verifying uploaded passport document details against a logged-in user's profile before confirming verification.

---

## 2. Current Architecture

The architecture consists of a simple serverless handler pattern designed to run locally or as an AWS Lambda function:

```
[Client Request]
       │ (first_name, last_name, base64 passport_image)
       ▼
┌──────────────────────────────────────────────┐
│ AWS Lambda / Local Handler (handler.py)      │
└──────────────────────┬───────────────────────┘
                       │
                       ▼ Parse request payload
┌──────────────────────────────────────────────┐
│ Payload Structural Validation (validation.py)│
└──────────────────────┬───────────────────────┘
                       │
                       ▼ Match expected fields & Expiry check
┌──────────────────────────────────────────────┐
│ Passport Verification Engine (verification.py)│
└──────────────────────────────────────────────┘
```

- **Models (`models.py`)**: Defines clean immutable types (`VerificationRequest`, `ExtractedPassportDetails`, `PassportVerificationResult`, `VerificationResponse`, `ApiGatewayResponse`).
- **Request Parsing (`handler.py`)**: Extract API Gateway events, decodes JSON payloads, and handles error response mapping.
- **Structural Validation (`validation.py`)**: Sanitizes inputs (non-empty strings, trims spaces) and validates base64 structure and integrity of the uploaded image.
- **Verification Logic (`verification.py`)**: Compares extracted document details against expected user parameters.

---

## 3. Nikhil's Confirmed Scope

- **AWS Stack**: Tailored for execution under AWS Lambda in `us-east-1`.
- **Response Format**: Basic success/failure response matching API Gateway integration specifications.
- **Business Controls**:
  - Validates document is an acceptable passport.
  - Matches first and last name against logged-in user profile attributes.
  - Validates document is not expired.

---

## 4. Completed Day 1 Work

- **Local Repository Setup**: Scaffolded Python project, standard layout, dependencies config.
- **Lambda Handler**: Created API Gateway handler in `handler.py` to parse payloads.
- **Structural Validation**: Implemented request body type verification and strict base64 decoding check in `validation.py`.
- **Dev Limit Removal**: Cleaned up the 5MB image size limit logic from the validation path and tests, keeping only Day 1 core structural logic.
- **Test coverage**: Created unit tests covering structural request failure scenarios.

---

## 5. Completed Day 2 Work

- **Extracted Details Data Model**: Introduced `ExtractedPassportDetails` to encapsulate first/last names and document expiry date extracted from passports.
- **Verification Engine**: Implemented `verify_passport_details()` to evaluate name matching and document expiry.
  - **Name Matching**: Normalized matching with case insensitivity and whitespace trimming.
  - **Expiry Verification**: Expiry date compared against reference date (or current date `date.today()`).
- **Result Structure**: Introduced `PassportVerificationResult` displaying boolean outcomes for name matches, expiration checks, and a tuple of `failure_reasons` if any checks fail.
- **Unit Testing**: Implemented 9 unit tests checking validation success/failure paths, normalization edge cases, and date limits.

---

## 6. Completed Day 3 Work — Integration Flow

- **Integrated Verification Handler**: Updated the API Lambda handler (`handler.py`) to execute the verification logic when `extracted_passport_details` is provided in the JSON request payload.
- **Error Response Extensibility**: Updated the `VerificationResponse` data model to support a `failure_reasons` sequence. This allows returning error codes for business verification errors while keeping the base API payload response backward-compatible.
- **Integration Test Coverage**: Added integration tests to `tests/test_handler.py` validating the full end-to-end flow:
  - Valid passport structure and verification details -> returns 200 HTTP Success.
  - Correct structure but wrong first/last name -> returns 400 with `FIRST_NAME_MISMATCH` / `LAST_NAME_MISMATCH`.
  - Expired passport -> returns 400 with `PASSPORT_EXPIRED`.
  - Multiple concurrent verification errors -> returns 400 containing all matching reasons.

---

## 7. AWS Lambda Deployment Milestone

- **AWS Setup**: Region `us-east-1`, root/admin MFA enabled, and zero-spend budget alert configured.
- **IAM Configuration**: Execution role `PassportVerificationLambdaRole` created with basic Lambda execution permissions.
- **Lambda Function**: Created function `passport-verification-poc` using Python 3.12 runtime.
- **Handler Configuration**: Configured handler entry point `passport_verification.handler.lambda_handler`.
- **Deployment Package**: Packaged and deployed via `lambda-deployment.zip`.
- **Invocation & Verification**: Executed live Lambda test invocation resulting in HTTP 200 status code with body `{"success": true}`.

---

## 8. Decisions and Out-of-Scope Items

- **Out of Scope**:
  - **OCR/Document Extraction**: The handler expects mock-extracted passport details via the payload for local integration testing. Direct OCR or AWS Textract integrations are omitted.
  - **Storage & Security**: Image storage in S3, encryption keys, KMS configuration.
  - **Alternative IDs**: Exclusively supports passport document verification.

