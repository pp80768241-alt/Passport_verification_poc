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

## 5. Day 2 Work Being Implemented

- **Extracted Details Data Model**: Introduced `ExtractedPassportDetails` to encapsulate first/last names and document expiry date extracted from passports.
- **Verification Engine**: Implemented `verify_passport_details()` to evaluate name matching and document expiry.
  - **Name Matching**: Normalized matching with case insensitivity and whitespace trimming.
  - **Expiry Verification**: Expiry date compared against reference date (or current date `date.today()`).
- **Result Structure**: Introduced `PassportVerificationResult` displaying boolean outcomes for name matches, expiration checks, and a tuple of `failure_reasons` if any checks fail.
- **Unit Testing**: Implemented 9 unit tests checking validation success/failure paths, normalization edge cases, and date limits.

---

## 6. Decisions and Out-of-Scope Items

- **Out of Scope (Day 2)**:
  - **OCR/Document Extraction**: The validation layer assumes extraction has already occurred. Direct image analysis, OCR, or AWS Textract integrations are omitted from this phase.
  - **AWS Deployments**: No AWS Terraform templates, S3 uploads, or live API Gateway integrations.
  - **Storage & Security**: Image storage in S3, encryption keys (SSE-S3 vs SSE-KMS), and custom KMS config are deferred.
  - **Alternative IDs**: Limited strictly to passport document verification. Driver's licenses or other government IDs are out of scope.
