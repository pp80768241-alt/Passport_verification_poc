# Passport Verification POC — Implementation Task List

## Working Method

Implement in small increments.

Recommended primary coding workflow:
- Use one primary coding agent (Cursor or Claude Code).
- Review meaningful changes before accepting them.
- Use Kimi K3 later as an independent reviewer/second opinion if desired.
- Keep Git as the source of truth.
- Do not deploy changes automatically.

---

## Phase 1 — Requirements & Local Setup

### Task 1.1 — Confirm requirements
- [ ] Record confirmed requirements from Nikhil.
- [ ] Record open questions.
- [ ] Do not treat assumptions as final requirements.

### Task 1.2 — Create POC repository
- [ ] Create separate local/Git repository because company repository access is restricted.
- [ ] Create Python project structure.
- [ ] Add README.
- [ ] Add `.gitignore`.

### Task 1.3 — Basic development checks
- [ ] Python environment works.
- [ ] Git works.
- [ ] Tests can run locally.

---

## Phase 2 — AWS Foundation

### Task 2.1 — AWS account/region verification
- [ ] Confirm AWS identity.
- [ ] Confirm `us-east-1`.
- [ ] Confirm which account/resources are safe to use.
- [ ] Do not deploy to an unknown account.

### Task 2.2 — S3 design
- [ ] Define private bucket.
- [ ] Enable/verify Block Public Access.
- [ ] Decide SSE-S3 vs SSE-KMS with requirements in mind.
- [ ] Define object-key strategy.

### Task 2.3 — IAM design
- [ ] Define Lambda execution role.
- [ ] Grant only required permissions.
- [ ] Avoid AdministratorAccess for application execution.

---

## Phase 3 — API and Lambda POC

### Task 3.1 — Lambda handler
- [ ] Create Python Lambda handler.
- [ ] Parse request.
- [ ] Validate required inputs.
- [ ] Return simple success/failure.

### Task 3.2 — API Gateway
- [ ] Create/configure API endpoint.
- [ ] Connect API Gateway to Lambda.
- [ ] Test request → Lambda → response.

### Task 3.3 — Image handling
- [ ] Decide POC upload method.
- [ ] Validate image presence/type/size.
- [ ] Store image in private encrypted S3.
- [ ] Return success/failure.

### Milestone — POC Complete
- [ ] API works.
- [ ] Lambda is invoked.
- [ ] Image is stored securely.
- [ ] Encryption is enabled.
- [ ] Simple response works.
- [ ] Basic errors are handled.

---

## Phase 4 — Document Verification Research

### Task 4.1 — Select document-analysis approach
- [ ] Identify the appropriate AWS service.
- [ ] Confirm it can support the required document fields.
- [ ] Test with safe sample documents.
- [ ] Inspect actual service responses.

### Task 4.2 — Document parser
- [ ] Convert service output into an internal structured model.
- [ ] Extract document type.
- [ ] Extract first name.
- [ ] Extract last name.
- [ ] Extract expiry date.

---

## Phase 5 — Verification Logic

### Task 5.1 — Document check
- [ ] Determine whether the uploaded document is an accepted document type.
- [ ] Define behavior for unreadable/unsupported documents.

### Task 5.2 — Name matching
- [ ] Normalize names.
- [ ] Apply the approved exact/business matching rule.
- [ ] Test matching and mismatch cases.

### Task 5.3 — Expiry check
- [ ] Parse expiry date.
- [ ] Compare against current date.
- [ ] Handle missing/invalid dates.

### Task 5.4 — Confirmation
- [ ] Combine required checks.
- [ ] Set `confirmed=true` only when all required checks pass.
- [ ] Define failure reasons internally.

---

## Phase 6 — Reliability

### Task 6.1 — Error handling
- [ ] Missing input.
- [ ] Invalid file.
- [ ] Unsupported format.
- [ ] Oversized file.
- [ ] Corrupt/unreadable image.
- [ ] Document-analysis failure.
- [ ] AWS permission/service failure.
- [ ] Timeout.
- [ ] Missing required document field.

### Task 6.2 — Testing
- [ ] Unit tests.
- [ ] Integration tests.
- [ ] Valid document case.
- [ ] Wrong-name case.
- [ ] Expired-document case.
- [ ] Random/non-document image case.
- [ ] Missing-field cases.

---

## Phase 7 — Security & Cost Review

- [ ] Review IAM permissions.
- [ ] Verify S3 privacy.
- [ ] Verify encryption.
- [ ] Review CloudWatch logs for sensitive data.
- [ ] Review AWS resource costs.
- [ ] Remove unnecessary resources.
- [ ] Confirm no secrets are in Git.

---

## Phase 8 — Documentation & Handover

- [ ] Update README.
- [ ] Update architecture document.
- [ ] Update security document.
- [ ] Document API input/output.
- [ ] Document deployment/setup steps.
- [ ] Document known limitations.
- [ ] Document unresolved requirements.
- [ ] Prepare demo/test evidence for Nikhil.

---

## Suggested 14-Day Schedule

| Day | Focus |
|---|---|
| 1 | Requirements, architecture, AWS fundamentals, local setup |
| 2 | IAM, S3, encryption |
| 3 | Lambda |
| 4 | API Gateway → Lambda |
| 5 | Image → encrypted S3 + POC milestone |
| 6 | Document-analysis research |
| 7 | Field extraction |
| 8 | Name matching |
| 9 | Expiry validation |
| 10 | Complete verification engine |
| 11 | Error handling |
| 12 | Security + cost review |
| 13 | Testing + documentation |
| 14 | Final QA + handover |

## Priority Rule

If time becomes limited, prioritize:

1. Working POC
2. Security
3. Core verification logic
4. Tests
5. Documentation
6. Nice-to-have improvements
