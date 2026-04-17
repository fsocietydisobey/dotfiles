# Error Handling

## Philosophy

- **Never swallow errors silently.** Every caught error must be logged, re-thrown, or handled with an explicit user-facing action. `catch (e) {}` is never acceptable.
- **Errors are information.** They should tell you what went wrong, where, and ideally why. Design error messages for the developer debugging at 2am.
- **Fail fast, fail loudly.** If something is wrong, surface it immediately. Don't let bad state propagate through the system until it causes a confusing failure somewhere else.

## Backend patterns

- Use a consistent error response envelope across all API endpoints:
  ```json
  { "error": { "code": "RESOURCE_NOT_FOUND", "message": "Human-readable description", "details": {} } }
  ```
- Map exception types to HTTP status codes explicitly. Don't let unhandled exceptions return 500 with a stack trace to the client.
- Catch errors at route handler boundaries. Services and repositories should throw typed exceptions — routes catch and transform to HTTP responses.
- Log the full error (with stack trace) server-side. Return a safe, actionable message client-side.

## Frontend patterns

- Use React Error Boundaries to catch rendering errors. Don't let one broken component take down the entire page.
- Network errors: implement retry logic with exponential backoff for transient failures (max 3 retries). Don't retry 4xx errors.
- Validate data from the backend before rendering. If a required field is missing, show a graceful fallback — not a crash.
- Show actionable error messages to users. "Something went wrong" is not actionable. "Failed to load your projects. Check your connection and try again." is.

## General rules

- **Don't use exceptions for flow control.** Exceptions are for exceptional situations. Use return values or result types for expected outcomes.
- **Include context in error messages.** Not just "File not found" — "File not found: /uploads/user_123/avatar.png". Include the ID, the path, the operation that failed.
- **Distinguish recoverable from unrecoverable.** A network timeout is recoverable (retry). A corrupted database record is not (alert and stop).
- **Error boundaries should be at layer transitions.** Route handlers, API clients, event handlers, background job processors.
