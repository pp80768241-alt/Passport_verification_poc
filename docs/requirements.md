# Passport Verification POC — Requirements

## 1. Purpose

Build a Proof of Concept (POC) for passport/document verification. The POC should demonstrate a simple AWS-based API flow and provide the foundation for adding the full verification logic.

## 2. Confirmed Requirements

- AWS region: `us-east-1`.
- The current company repository exists, but access is restricted for now.
- Therefore, the POC should be developed separately/local to begin with, unless Nikhil provides repository access later.
- The technical stack for the initial POC is:
  - API endpoint
  - AWS Lambda
  - Simple success/failure response
  - Image storage
- Uploaded images will be stored.
- Stored images must be protected with encryption.
- The eventual verification flow must check:
  1. The uploaded document is an acceptable passport/user ID document according to the final business rule.
  2. The first name on the document matches the currently logged-in user's first name.
  3. The last name on the document matches the currently logged-in user's last name.
  4. The document is valid and not expired.
- If all required passport/document controls pass, the system should mark the verification as confirmed.

## 3. Initial POC Scope

For the first POC, the external API response can be a simple success/failure message.

Initial conceptual flow:

Client
→ API
→ Lambda
→ secure image storage
→ success/failure

The complete document-analysis and verification logic can be added incrementally after the basic flow works.

## 4. Proposed Initial Inputs

The initial API should be designed around:

- `first_name` — current logged-in user's first name.
- `last_name` — current logged-in user's last name.
- `passport_image` — uploaded passport/document image.

The exact transport format (for example, multipart upload versus an S3 upload/presigned-URL flow) is still a design decision for the POC.

## 5. Initial Output

For the initial POC:

```json
{
  "success": true
}
```

or

```json
{
  "success": false
}
```

The final production response may expose more specific verification states, but that is not required for the first POC unless Nikhil requests it.

## 6. Security Requirements

- Passport/document images must not be publicly accessible.
- S3/object storage must use server-side encryption.
- IAM permissions should follow least privilege.
- Sensitive document contents should not be unnecessarily written to logs.
- No AWS credentials or secrets should be committed to Git.
- Development should use test/synthetic documents where possible.

## 7. Out of Scope for the Initial POC

- Production integration with the restricted company repository.
- Full frontend implementation.
- A custom ML/computer-vision model.
- Final production authentication/authorization design unless supplied by the existing system.
- Final retention/deletion policy.
- Final document-matching rules beyond the requirements currently known.
- Production deployment without approval.

## 8. Open Questions / Decisions Needed

1. Does "passport" mean passport only, or should other government ID cards be accepted?
2. Nikhil used both "passport" and "User ID card" in the original requirement; this needs clarification.
3. What image formats are supported?
4. What is the maximum image/file size?
5. Should the logged-in user's identity be obtained from an authentication token/session rather than sent directly as request fields?
6. What exact name matching rules should be used for middle names, spacing, punctuation, and ordering?
7. Which AWS document-analysis service should be used?
8. Does document validity mean only readable/structurally valid, or is authenticity verification required?
9. What is the required image retention period?
10. Should encryption use SSE-S3 or SSE-KMS?
11. What exact API response should be returned for individual failure reasons?
12. What AWS account/resource naming conventions should be followed?

## 9. Success Criteria for the POC

The POC is successful when:

- A request can reach the API.
- The API invokes Lambda.
- Lambda can validate the basic request.
- The uploaded image can be securely stored.
- Storage encryption is enabled.
- Lambda can return a simple success/failure response.
- The design is documented clearly enough to extend into full verification.
