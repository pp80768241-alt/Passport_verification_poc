# Passport Verification Proof of Concept (POC)

## 1. Project Overview
This repository contains a secure, serverless backend application designed to handle passport document verification. It processes client verification requests, validates payloads structurally, stores passport image files securely in Amazon S3, and verifies identity matching details.

---

## 2. Objective
The objective of this Proof of Concept (POC) is to establish a secure and highly scalable serverless backend for passport verification on AWS. It implements robust structural validation and business matching rules (e.g., name similarity and passport expiration checks) while showcasing cloud-native security best practices.

---

## 3. Current Architecture
The request flow follows a serverless architecture:

```text
[ Client ]
    │
    │  POST /verify-passport
    ▼
┌──────────────────────────┐
│   API Gateway HTTP API   │  (Exposes endpoint, routes client requests)
└───────────┬──────────────┘
            │
            │  Invokes
            ▼
┌──────────────────────────┐
│    AWS Lambda Function   │  (Executes python orchestrator handler.py)
└───────────┬──────────────┘
            ├──────────────────────────────────────────────┐
            ▼                                              ▼
┌──────────────────────────┐                      ┌──────────────────────────┐
│   Verification Engine    │                      │    Amazon S3 Storage     │
│  (verification.py logic) │                      │ (storage.py - saves raw) │
└──────────────────────────┘                      └──────────────────────────┘
```

1. **Client Request**: The client submits a JSON request to the API Gateway.
2. **API Gateway HTTP API**: Gateway receives the request and forwards it to trigger the AWS Lambda execution handler.
3. **AWS Lambda**: The handler coordinates structural checks, writes decoded images to S3, runs matching engine checks, and returns API Gateway HTTP API v2-compatible JSON responses.

---

## 4. Technology Stack
- **Python**: Core programming language runtime (version 3.12).
- **AWS Lambda**: Serves as the compute element hosting the execution handler.
- **API Gateway HTTP API**: Entry point providing cost-effective API routing.
- **Amazon S3**: High-durability object storage vault for documents.
- **AWS IAM**: Manages security policies for least-privilege resource access.
- **pytest**: Framework for local unit and integration tests.

---

## 5. Project Structure
The repository is structured as follows:

```text
.
├── PROJECT_NOTES.md         # Complete developer configuration & notes
├── README.md                # Overview and setup instructions (this file)
├── requirements.txt         # Production/runtime requirements
├── requirements-dev.txt     # Development and testing requirements
│
├── src/
│   └── passport_verification/
│       ├── __init__.py      # Package definition
│       ├── handler.py       # Main Lambda orchestrator handler
│       ├── models.py        # Immutable request/response schemas
│       ├── response.py      # HTTP integration response mapper
│       ├── storage.py       # AWS S3 image upload operations
│       ├── validation.py    # Shape checks & base64 validation
│       └── verification.py  # Matching and expiration logic
│
└── tests/
    ├── __init__.py
    ├── conftest.py          # Pytest shared fixtures and event mock builders
    ├── test_handler.py      # API Gateway integration and status code tests
    ├── test_storage.py      # S3 error wrappers and UUID key tests
    ├── test_validation.py   # Base64 decoder payload checks
    └── test_verification.py # Name normalize and date logic tests
```

---

## 6. Verification Flow
1. **Body Parsing**: Lambda extracts the JSON body from the incoming API Gateway proxy event.
2. **Structural Validation**: Checks fields presence (`first_name`, `last_name`, `passport_image`), checks data types, and validates the base64 structure of the image, returning HTTP 400 on error.
3. **Storage Upload**: Decodes the base64 string into bytes, uploads it to S3, and captures any S3/Boto3 client failures to output HTTP 500.
4. **Detail Verification**: Normalizes names (removes whitespace, compares case-insensitively) and checks that the passport expiration date is greater than or equal to the comparison date.
5. **Response Compilation**: Aggregates all matching/expiry failures (e.g. `FIRST_NAME_MISMATCH`, `PASSPORT_EXPIRED`) and returns HTTP 400 on failures or HTTP 200 on validation success.

---

## 7. S3 Storage
- **Target Bucket**: `passport-verification-poc-2004-pp`
- **Object Prefix**: `passports/`
- **Key Strategy**: File keys are saved using generated UUIDs (`passports/<UUIDv4>.bin`) to avoid collisions and obscure client identifiers.
- **Encryption**: The bucket uses default Amazon S3 managed server-side encryption (SSE-S3).

---

## 8. IAM
- **Lambda Execution Role**: `PassportVerificationLambdaRole`
- **S3 Access Policy**: The inline policy `PassportVerificationS3Access` attached to the execution role restricts write permissions to the designated directory structure:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::passport-verification-poc-2004-pp/passports/*"
        }
    ]
}
```

---

## 9. API
- **Endpoint**: `POST /verify-passport`

### Request Schema
```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "passport_image": "<base64-encoded-string-content>",
  "extracted_passport_details": {
    "first_name": "Jane",
    "last_name": "Doe",
    "expiry_date": "2030-01-01"
  },
  "reference_date": "2026-08-21"
}
```

### Response Schema

#### Successful Matching (HTTP 200)
```json
{
  "success": true
}
```

#### Matching Rule Failures (HTTP 400)
```json
{
  "success": false,
  "failure_reasons": [
    "FIRST_NAME_MISMATCH",
    "PASSPORT_EXPIRED"
  ]
}
```

#### Formatting & Syntax Failures (HTTP 400)
```json
{
  "success": false
}
```

#### Upload / Server Faults (HTTP 500)
```json
{
  "success": false
}
```

---

## 10. Testing
The test suite consists of **31 automated tests** executing locally using pytest.

### Test Categories
1. **End-to-End API Integration (`test_handler.py`)**: Tests full execution pipeline, mapping of status codes (200, 400, 500) to API responses, and exception wrappers.
2. **S3 Storage (`test_storage.py`)**: Verifies S3 helper methods, namespace collision avoidance, environment lookup, and client error wrapping.
3. **Structural Validation (`test_validation.py`)**: Covers empty parameters, spaces-only strings, base64 formatting checks, and decoding errors.
4. **Matching Engine (`test_verification.py`)**: Validates name comparisons (case, padding, mismatch details), date normalization, and expiration checks.

---

## 11. Live API Testing
During live API testing on AWS:
- **Successful Requests**: Verified that submissions matching expected criteria return an HTTP 200 response with `{"success": true}`.
- **Failure Scenarios**: Verified that expired passports or invalid name pairs return HTTP 400 with granular matching error code lists.
- **S3 Upload Verification**: Checked that decoded images are successfully written to `passport-verification-poc-2004-pp` under the `passports/` folder.

---

## 12. Security
- **S3 Private Settings**: The storage bucket has **Block Public Access** enabled, ensuring no assets are accessible from the public internet.
- **Zero Hardcoded Credentials**: Authentication credentials, AWS credentials, API keys, and sensitive developer data are not stored in the repository. Access is managed dynamically via Lambda IAM Execution Roles.

---

## 13. Current Limitations
- **No Native OCR**: The backend does not implement image text extraction or scanning (OCR). Verification fields must be manually provided via `extracted_passport_details` in the JSON request body.
- **No Database Storage**: Database persistence layers (such as Amazon DynamoDB or Amazon Aurora) are not implemented in the current version.
- **POC Scope**: The project acts as a serverless proof of concept using mock data structures for testing validations and flow logic.

---

## 14. Future Improvements
- **AWS Textract OCR Integration**: Replace request-provided parameters with automatic document scans.
- **Payload Verification**: Check image headers/magic-bytes to verify that content formats are valid (e.g., PNG/JPEG) before S3 storage.
- **Image Size Limits**: Implement early rejection of base64 payloads larger than 5MB to optimize cost.
- **Custom KMS Encryption**: Integrate SSE-KMS with Customer Managed Keys (CMK) for auditability.

---

## 15. How to Run Tests Locally

### Local Setup
Ensure Python 3.12 is installed, then create and activate a virtual environment:

```bash
# Create environment
python -m venv .venv

# Activate environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements-dev.txt
```

### Run pytest
Execute the suite of 31 tests:
```bash
python -m pytest tests/ -v
```
