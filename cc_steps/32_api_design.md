# API & Contract Design

If it has an API, design the contract deliberately:

- **Versioning.** Version from day one (`/v1/`, header, or media type). You will need to evolve without breaking clients.
- **Backward compatibility.** Additive changes only within a version: add fields, never remove/rename/repurpose. Breaking changes mean a new version.
- **Pagination.** Never return unbounded lists. Cursor-based scales better than offset for large/changing datasets.
- **Error shape.** One consistent error envelope (code, message, machine-readable detail) across every endpoint. Correct HTTP status codes.
- **Rate limiting.** Protect the service; return `429` with `Retry-After`; communicate limits in headers.
- **Idempotency keys.** For unsafe operations (payments, creates), accept a client-supplied idempotency key so a retried request doesn't double-act. This is how you make "exactly once" out of an unreliable network.
- **Contract tests.** Pin request/response shapes to catch breaking changes before clients do.
