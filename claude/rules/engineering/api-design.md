# API Design

## REST conventions

- Use **plural nouns** for resource endpoints: `/api/v1/projects`, `/api/v1/users`.
- Use HTTP methods correctly: GET (read), POST (create), PUT (full replace), PATCH (partial update), DELETE (remove).
- Nest resources logically: `/api/v1/projects/{id}/members`, not `/api/v1/project-members?project_id={id}`.
- Use query parameters for filtering, sorting, and pagination: `?status=active&sort=-created_at&limit=20`.

## Versioning

- Version the API in the URL path: `/api/v1/`, `/api/v2/`.
- Don't break existing clients. If a change is backward-incompatible, it goes in a new version.
- Deprecate before removing. Mark deprecated endpoints in responses and documentation before cutting them.

## Response envelope

- Use a consistent response structure across all endpoints:
  ```json
  {
    "data": { ... },
    "meta": { "page": 1, "total": 42 }
  }
  ```
- Error responses use a different envelope (see error-handling.md).
- Always return appropriate HTTP status codes: 200 (success), 201 (created), 204 (no content), 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 409 (conflict), 422 (validation error), 500 (server error).

## Pagination

- **Always paginate list endpoints.** Never return unbounded result sets.
- Use cursor-based pagination for large or real-time datasets (`?cursor=abc123&limit=20`).
- Offset-based pagination (`?page=1&limit=20`) is fine for small, stable datasets.
- Include pagination metadata in the response: total count (when cheap to compute), next/previous cursors or page numbers.

## Request/response conventions

- Request bodies: accept the most convenient format for the client. Validate strictly on the server.
- Response bodies: return only what the client needs. Be consistent with field names and types across endpoints.
- Use ISO 8601 for dates/times. Always UTC with timezone indicator: `2025-01-15T14:30:00Z`.
- Use UUIDs for public-facing IDs. Auto-increment integers are fine for internal database keys but shouldn't leak to clients.

## Documentation

- Every endpoint should be documented with: method, path, description, request body/params, response shape, error cases.
- Use OpenAPI/Swagger when the framework supports it (FastAPI generates this automatically — keep it accurate).
- Include example requests and responses in documentation.
