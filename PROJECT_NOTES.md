# Project Notes — Passport Verification Proof of Concept (POC)

This document is a comprehensive, beginner-friendly guide to the current design, implementation, and deployment state of the Passport Verification POC. It explains all technical elements, code flows, AWS resources, security rules, and testing procedures.

---

## 1. Project Purpose and Scope

### Purpose
The goal of this Proof of Concept (POC) is to build a secure, lightweight AWS-based passport verification backend. It serves as a foundation for verifying uploaded passport document details against a user's expected profile data (e.g., first and last name) before confirming their identity.

### Scope Boundaries
*   **In-Scope (Current Implementation)**:
    *   **Payload Structural Validation**: Checking that the payload contains required fields and that the image is a valid base64 string.
    *   **Secure Storage**: Decoding the base64 passport image and uploading it securely to AWS S3.
    *   **Verification Engine**: Comparing extracted passport details (supplied in the request payload) against the expected profile details (also in the payload), including name normalization and document expiry checks.
    *   **Lambda Orchestration**: A Lambda handler that parses requests, invokes validation, stores images, and invokes verification.
*   **Out-of-Scope (Future Phase)**:
    *   **Automated OCR / Text Extraction**: The Lambda function does not currently extract text from the passport image. Instead, mock-extracted details (`extracted_passport_details`) are provided directly in the incoming API request payload for testing verification logic. Implementing OCR (e.g., via AWS Textract) is left for a future phase.
    *   **Alternative Forms of Identification**: The system currently supports passport document verification only.
    *   **Custom KMS Key Encryption**: The S3 bucket uses standard Amazon S3 managed server-side encryption (SSE-S3) without custom KMS keys.

---

## 2. Technical Architecture

The POC uses a serverless request-driven architecture:

```text
       [ Client Request ]
               │  POST /verify-passport (first_name, last_name, passport_image, extracted_details)
               ▼
┌──────────────────────────────┐
│    API Gateway HTTP API      │  (Exposes endpoint, forwards route to Lambda)
└──────────────┬───────────────┘
               │
               ▼  Invokes
┌──────────────────────────────┐
│  AWS Lambda Function         │  (Orchestrates flow in src/passport_verification/handler.py)
└──────────────┬───────────────┘
               ├──────────────────────────────────────────────┐
               ▼ (Step 1: Validate payload structure)          ▼ (Step 2: Upload decoded image)
┌──────────────────────────────┐              ┌──────────────────────────────┐
│ Structural Validation        │              │ Amazon S3 Storage            │
│ (validation.py)              │              │ (storage.py)                 │
└──────────────────────────────┘              │ Target Bucket:               │
                                              │ - passport-verification-poc- │
                                              │   2004-pp                    │
                                              │ Folder Prefix:               │
                                              │ - passports/                 │
                                              └──────────────────────────────┘
               │
               ▼ (Step 3: Run verification logic)
┌──────────────────────────────┐
│ Verification Engine          │
│ (verification.py)            │
└──────────────────────────────┘
```

### Flow Breakdown for Beginners:
1.  **Client POST Request**: A client submits a JSON payload to the API Gateway endpoint (`POST /verify-passport`).
2.  **API Gateway Routing**: API Gateway receives the HTTP request and triggers the Lambda function.
3.  **Structural Validation**: The Lambda handler verifies that the request has the correct schema (non-empty fields, valid base64 encoding).
4.  **S3 Image Upload**: The Lambda handler decodes the base64 image into raw bytes and uploads it to a private S3 bucket.
5.  **Passport Verification**: The Lambda handler compares the user's expected names and the details extracted from the document (checking name matches and expiration).
6.  **HTTP Response**: The handler returns a success status (HTTP 200) or structured failure reason list (HTTP 400 or HTTP 500).

---

## 3. Python Project Structure

The project code is organized under `src/` and `tests/` directories as follows:

```text
.
├── PROJECT_NOTES.md                      <-- This documentation file
├── README.md                             <-- Setup and run instructions
├── requirements.txt                      <-- Core dependencies (boto3)
├── requirements-dev.txt                  <-- Dev dependencies (pytest)
│
├── src/
│   └── passport_verification/
│       ├── __init__.py                   <-- Packages exports
│       ├── handler.py                    <-- Lambda entry point & routing orchestration
│       ├── models.py                     <-- Immutable data structures (dataclasses)
│       ├── response.py                   <-- Formats responses for API Gateway integration
│       ├── storage.py                    <-- Handles uploading images to AWS S3
│       ├── validation.py                 <-- Performs request shape/structural validation
│       └── verification.py               <-- Contains passport business logic (name/expiry)
│
└── tests/
    ├── __init__.py                       <-- Pytest marker
    ├── conftest.py                       <-- Pytest fixtures (synthetic image, event builder)
    ├── test_handler.py                   <-- Tests the integration flow & error codes
    ├── test_storage.py                   <-- Tests S3 upload, configuration & errors
    ├── test_validation.py                <-- Tests payload validation rules
    └── test_verification.py              <-- Tests name matching & expiry business logic
```

### Explanation of Files:
*   [handler.py](file:///c:/Users/panwa/Desktop/Passport%20verification%20poc/src/passport_verification/handler.py): Orchestrates the entire application flow. It parses incoming event JSON bodies, catches validation and S3 upload exceptions, and calls the verification engine.
*   [models.py](file:///c:/Users/panwa/Desktop/Passport%20verification%20poc/src/passport_verification/models.py): Defines data structures using Python `@dataclass(frozen=True)` to represent request/response data cleanly and safely (guaranteeing immutability).
*   [validation.py](file:///c:/Users/panwa/Desktop/Passport%20verification%20poc/src/passport_verification/validation.py): Performs sanity checks on the request shape before doing any AWS operations.
*   [verification.py](file:///c:/Users/panwa/Desktop/Passport%20verification%20poc/src/passport_verification/verification.py): Implements business verification constraints (comparing names and dates).
*   [storage.py](file:///c:/Users/panwa/Desktop/Passport%20verification%20poc/src/passport_verification/storage.py): Connects to AWS S3 using `boto3` to store raw passport document images.
*   [response.py](file:///c:/Users/panwa/Desktop/Passport%20verification%20poc/src/passport_verification/response.py): Wraps results in an API Gateway HTTP API v2 integration structure.

---

## 4. Code Execution and Verification Flows

### A. Request Structural Validation Flow
Before processing any data or invoking AWS resources, the system validates the incoming JSON structure using `validate_request_payload` in `validation.py`.

1.  **Field Existence**: Verifies that `first_name`, `last_name`, and `passport_image` fields are present in the JSON body.
2.  **Field Format**: Verifies that all three fields are strings and are not empty or solely whitespace (using `.strip()`).
3.  **Base64 Image Decoding**: Validates that `passport_image` is a valid base64-encoded string. It uses `base64.b64decode(..., validate=True)` to enforce strict padding and encoding checks.
4.  **Empty Image Check**: Asserts that the decoded byte array has a length greater than `0`.

If any of these structural checks fail, the validation flow stops immediately, returns `is_valid = False`, and the handler responds with an HTTP 400 Bad Request error.

### B. Passport Verification Flow
Once the payload structure is validated and the image is stored, the handler performs business logic validation using `verify_passport_details` in `verification.py`.

1.  **Name Normalization**:
    *   Names are stripped of leading/trailing whitespaces.
    *   Names are compared case-insensitively (e.g. `"Jane"` matches `"  jane  "`).
2.  **Expiry Check**:
    *   Compares the passport's `expiry_date` (extracted details) against a `reference_date` (defaults to today's date using `date.today()`).
    *   A passport is valid (not expired) if its expiry date is **greater than or equal to** the reference date.
3.  **Failure Logging**:
    *   If any verification check fails, specific code identifiers are added to a list:
        *   `FIRST_NAME_MISMATCH`
        *   `LAST_NAME_MISMATCH`
        *   `PASSPORT_EXPIRED`
4.  **Result Aggregation**: Returns a consolidated response listing all failures, allowing the client to correct all mistakes at once.

---

## 5. AWS Resource Configurations

### AWS Lambda
*   **Function Name**: `passport-verification-poc`
*   **Runtime**: Python 3.12
*   **Handler**: `passport_verification.handler.lambda_handler`
*   **Role**: Attached to `PassportVerificationLambdaRole`
*   **Deployment**: Package is zipped into `lambda-deployment.zip` and uploaded to the Lambda service.

### API Gateway HTTP API
*   **API Name**: `passport-verification-api`
*   **Route**: `POST /verify-passport`
*   **Integration**: Configured as an AWS Lambda integration pointing directly to the `passport-verification-poc` Lambda function.
*   **Stage**: `$default` stage (auto-deploy enabled) allowing immediate live endpoint testing.

### S3 Image Storage Bucket
*   **Bucket Name**: `passport-verification-poc-2004-pp` (private bucket located in AWS region `us-east-1`).
*   **Object Prefix (Directory)**: All decoded passport images are stored under the `passports/` folder.
*   **Key Strategy**: To prevent name collisions and protect user identities, files are stored as `passports/<UUIDv4>.bin` (e.g., `passports/123e4567-e89b-12d3-a456-426614174000.bin`).
*   **Environment Variable**: The environment variable `PASSPORT_BUCKET` controls which bucket to upload to. If it is not set, the code falls back to using the default bucket `passport-verification-poc-2004-pp`.

### S3 Error Handling & S3UploadError
*   The upload logic is wrapped in a `try...except` block in `storage.py`.
*   It catches `BotoCoreError` and `ClientError` (from the `botocore` package) and raises a custom `S3UploadError`.
*   The Lambda `handler.py` catches `S3UploadError` and:
    1.  Logs the internal error message for developers in AWS CloudWatch.
    2.  Returns a generic HTTP 500 Internal Server Error message (`{"success": false}`) to the client. This hides internal AWS architecture details and prevents security exposure of AWS credentials/tracebacks to API clients.

### AWS IAM Roles & Policies
*   **IAM Execution Role**: `PassportVerificationLambdaRole`. This role allows the Lambda function to execute and write logs to AWS CloudWatch.
*   **Inline IAM Policy**: `PassportVerificationS3Access`. Attached to the Lambda execution role. It grants least-privilege access, permitting only `s3:PutObject` on the target bucket and paths:
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

## 6. Automated Testing (31 Tests Passed)

We have a robust test suite of **31 tests** using the `pytest` framework. All tests run locally using mock data and virtual environments, keeping test execution decoupled from live AWS systems.

### Run Command
```bash
python -m pytest tests/ -v
```

### Test Case Overview:
*   **End-to-End API Integration Tests (`test_handler.py`)**:
    *   **Success Test**: Verifies that a valid JSON request payload containing valid structural details and valid `extracted_passport_details` results in HTTP 200 and `{"success": true}`.
    *   **Failure Tests**: Verifies that wrong fields return HTTP 400 and appropriate error lists. For example:
        *   Wrong first name: returns `{"success": false, "failure_reasons": ["FIRST_NAME_MISMATCH"]}`.
        *   Expired passport: returns `{"success": false, "failure_reasons": ["PASSPORT_EXPIRED"]}`.
        *   Multiple concurrent errors: returns all matching error codes (e.g. `FIRST_NAME_MISMATCH`, `LAST_NAME_MISMATCH`, `PASSPORT_EXPIRED`).
    *   **S3 Upload Integration Error Test**: Mocks S3 upload failure to verify the handler catches it and returns HTTP 500.
*   **S3 Upload Verification Tests (`test_storage.py`)**:
    *   Verifies that the upload function generates unique keys under the `passports/` prefix.
    *   Verifies default bucket fallback and custom bucket lookup via the `PASSPORT_BUCKET` environment variable.
    *   Verifies that `botocore` client errors are caught and converted to `S3UploadError`.
*   **Structural Validation Tests (`test_validation.py`)**:
    *   Checks for missing or empty fields, spaces-only strings, invalid base64 padding, and empty images.
*   **Passport Verification Logic Tests (`test_verification.py`)**:
    *   Validates business criteria: normalizations, expiry boundaries (today, tomorrow, expired), reference date defaults, and multiple failure reasons.

---

## 7. Git and Version Control Status

*   **Ignored Files**:
    *   `lambda-package/` (contains build packages for Lambda deployment) and `lambda-deployment.zip` (the actual deployment zip) are excluded from version control.
    *   This is enforced in the [.gitignore](file:///c:/Users/panwa/Desktop/Passport%20verification%20poc/.gitignore) file to prevent large, auto-generated binary files from bloating the Git history.
*   **Git Status**:
    *   The workspace working tree is clean. All source files and test scripts are fully committed.
    *   No changes are automatically committed or pushed to GitHub as part of cleanup tasks.

---

## 8. Known Limitations and Future Improvements

1.  **OCR Text Extraction**:
    *   *Current limitation*: Verification parameters must be manually supplied in the payload for validation.
    *   *Future improvement*: Integrate AWS Textract to automatically scan, read, and extract the names and expiry dates from the uploaded passport image directly within the Lambda function.
2.  **Image Header & Content Validation**:
    *   *Current limitation*: The validation package only checks base64 structure and size length. It does not verify if the decoded file is actually a PNG/JPG image or a spoofed file.
    *   *Future improvement*: Read image magic bytes (e.g., using PIL/Pillow or standard image library checks) to verify that uploaded content matches allowed mime-types (PNG, JPEG).
3.  **Image File-Size Limits**:
    *   *Current limitation*: The payload size limit is handled by API Gateway (maximum payload limit of 10MB for HTTP APIs). No code limits are currently enforced.
    *   *Future improvement*: Explicitly check the byte array size of the decoded passport image in the code and reject payloads larger than a configurable size (e.g., 5MB) early to save S3 storage and processing costs.
4.  **Fine-Grained KMS Encryption**:
    *   *Current limitation*: Default S3-managed encryption keys (SSE-S3) are used.
    *   *Future improvement*: Transition to Customer Managed Keys (SSE-KMS) to enable stricter security auditing and access policies over raw passport images.