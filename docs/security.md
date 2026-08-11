# Passport Verification POC — Security & Access

## 1. Security Objective

Passport/document images contain highly sensitive identity information. The POC must therefore avoid public exposure, excessive permissions, accidental logging, and credential leakage.

## 2. S3 Security

The document storage bucket should:

- Remain private.
- Have S3 Block Public Access enabled.
- Use server-side encryption.
- Avoid public bucket policies.
- Restrict object access through IAM.

### Encryption Options

Two options should be evaluated:

**SSE-S3**
- S3 manages the encryption keys.
- Simple operational model.
- Suitable candidate for the initial POC unless the company requires customer-managed keys.

**SSE-KMS**
- Uses AWS KMS.
- Provides more control over key usage and permissions.
- Requires additional IAM/KMS configuration.

The final choice should be confirmed against company security requirements.

## 3. IAM

Use least privilege.

Conceptually:

```text
Lambda execution role
    |
    +--> permission to write required objects to the specific S3 bucket/prefix
    |
    +--> permission required by the selected document-analysis service
    |
    +--> CloudWatch logging permissions required for application logs
```

Do not use broad administrator permissions for the Lambda execution role.

Do not create long-lived AWS access keys inside the application.

## 4. Data Protection

Avoid logging:

- Passport images.
- Full OCR/document-analysis responses when they contain sensitive personal data.
- Passport numbers or other unnecessary identity fields.
- Authentication tokens.
- Secrets.

Logs should contain only information necessary for troubleshooting, such as request correlation IDs and non-sensitive error categories.

## 5. Credentials and Secrets

Never commit:

```text
AWS access keys
AWS secret keys
API keys
Passwords
Tokens
Private certificates
```

to GitHub.

Use AWS IAM roles and approved secret-management mechanisms where secrets are genuinely required.

## 6. Authentication / User Identity

The final system should ideally obtain the current user's identity from the application's authenticated session/token rather than trusting arbitrary first/last-name values supplied by an untrusted client.

For the POC, the exact authentication mechanism is not yet defined.

Therefore, `first_name` and `last_name` are treated as proposed inputs for brainstorming/testing, not as a final security design.

## 7. File Validation

Before storing/processing an uploaded image, the application should eventually validate:

- File is present.
- File type/format is allowed.
- File size is within the configured limit.
- File can be processed.
- Filename/path cannot cause unintended object placement.

Do not trust the client-provided filename or MIME type alone.

## 8. S3 Object Naming

Avoid using raw user-provided filenames as object keys.

Use a generated identifier, for example:

```text
verification/<generated-id>/document
```

This reduces collisions and prevents user-controlled filenames from becoming part of the storage path.

## 9. Retention

The retention period has not been specified.

Before production, confirm:
- How long images must be stored.
- Whether automatic deletion is required.
- Whether failed verification images should be retained.
- Whether lifecycle rules should be configured.

Do not invent a retention period for production.

## 10. Development Safety

- Use synthetic/test documents whenever possible.
- Do not upload real passports to an AI coding agent.
- Do not place real passport images in Git.
- Do not use production credentials during development.
- Keep development AWS permissions restricted.

## 11. Security Acceptance Criteria

Before handover:

- [ ] S3 bucket is private.
- [ ] S3 encryption is enabled.
- [ ] Public access is blocked.
- [ ] Lambda IAM permissions are least privilege.
- [ ] No credentials/secrets are committed.
- [ ] Sensitive document data is not unnecessarily logged.
- [ ] File validation exists where applicable.
- [ ] Retention policy is documented or explicitly marked pending.
