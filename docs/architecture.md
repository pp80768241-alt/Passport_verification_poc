# Passport Verification POC — Technical Architecture

## 1. Objective

Create a minimal, secure AWS architecture that can later support passport/document verification.

## 2. AWS Region

`us-east-1`

## 3. Initial Architecture

```text
                    Client
                      |
                      | POST /verify-passport
                      v
              +----------------+
              |  API Gateway   |
              +-------+--------+
                      |
                      v
              +----------------+
              |     Lambda     |
              |   Python       |
              +-------+--------+
                      |
                      | Store uploaded image
                      v
              +----------------+
              |       S3       |
              | Private +      |
              | Encrypted      |
              +----------------+
```

The initial POC returns a simple success/failure response.

## 4. Future Verification Architecture

```text
Client
  |
  v
API Gateway
  |
  v
Lambda
  |
  +----> Validate request
  |
  +----> Store image securely in S3
  |
  +----> Document/passport analysis
  |          |
  |          +----> Document type
  |          +----> First name
  |          +----> Last name
  |          +----> Expiry date
  |
  +----> Verification engine
             |
             +----> Document check
             +----> First-name match
             +----> Last-name match
             +----> Expiry check
             |
             v
        confirmed / failure
```

## 5. Components

### API Gateway

Responsibilities:
- Expose the HTTP API.
- Receive the verification request.
- Invoke Lambda.
- Return the Lambda response.

### AWS Lambda

Responsibilities:
- Validate request structure.
- Coordinate image storage.
- Later coordinate document analysis and verification.
- Return the verification result.

### Amazon S3

Responsibilities:
- Store uploaded document images.
- Keep objects private.
- Use server-side encryption.

### Document Analysis Service

Not finalized yet.

Responsibilities in the future:
- Analyze the uploaded document.
- Determine whether it is an acceptable document type.
- Extract required fields such as names and expiry date.

The exact AWS service and API should be selected after confirming the requirement and testing sample responses.

## 6. API Input — Proposed

Conceptually:

```text
POST /verify-passport

first_name
last_name
passport_image
```

The final request encoding is still open.

## 7. API Output — POC

Success:

```json
{
  "success": true
}
```

Failure:

```json
{
  "success": false
}
```

## 8. Future Internal Verification Result

A more detailed internal result can be modeled as:

```json
{
  "confirmed": true,
  "checks": {
    "document_valid": true,
    "name_match": true,
    "expiry_valid": true
  }
}
```

This detailed structure is proposed for internal design only and is not required as the initial external POC response.

## 9. Design Principles

- Keep the first POC minimal.
- Separate API handling from verification logic.
- Keep S3 private.
- Use least-privilege IAM.
- Avoid unnecessary AWS services.
- Do not expose sensitive document data in API responses or logs.
- Keep the design extensible for later production integration.

## 10. Current Constraints

- Existing company repository access is restricted.
- Development therefore starts as a separate POC.
- Production integration and deployment depend on further instructions from Nikhil/Ali.
