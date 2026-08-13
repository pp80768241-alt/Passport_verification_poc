# Passport Verification POC

Local foundation for a passport/document verification proof of concept on AWS.

## Day 1 Scope

This repository currently includes:

- A minimal Python Lambda-style handler
- Basic structural input validation for `first_name`, `last_name`, and `passport_image`
- Local unit tests using synthetic image data only

`success: true` means the request passed basic structural validation only. It does **not** verify passport authenticity, OCR fields, name matching, expiry, or document type.

## Out of Scope (Day 1)

- AWS deployment (Lambda, API Gateway, S3, IAM)
- Document verification logic
- Real passport images
- Authentication/session integration

## Project Layout

```text
src/passport_verification/
  handler.py      Lambda entry point
  validation.py   Input validation
  models.py       Request/response models
  response.py     API Gateway response builder
tests/
  test_handler.py
  test_validation.py
```

## Local Setup

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt
```

## Run Tests

```bash
python -m pytest tests/ -v
```

## Request Shape (Local)

The handler expects an API Gateway HTTP API v2-style event with a JSON body:

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "passport_image": "<base64-encoded synthetic image bytes>"
}
```

## Responses

Success (structural validation passed):

```json
{
  "success": true
}
```

Failure (missing/invalid input):

```json
{
  "success": false
}
```

## Development Notes

- Do not commit AWS credentials, secrets, or real passport images.
- See `docs/` for requirements, architecture, security, and task planning.
