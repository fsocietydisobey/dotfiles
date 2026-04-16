# Security

## Secrets management

- **No secrets in code.** Ever. All secrets come from environment variables or a secrets manager.
- Commit `.env.example` with required variable names and comments — never commit `.env` files with real values.
- API keys, database credentials, tokens, and signing keys must never appear in source code, logs, error messages, or frontend bundles.

## Input validation

- **Validate at system boundaries** — user input, API requests, webhook payloads, file uploads, URL parameters. Never trust external data.
- Backend: use Pydantic models or equivalent schema validation for all request bodies. Validate types, ranges, formats, and lengths.
- Frontend: validate before sending to backend (UX) and never trust backend responses blindly if rendering user-generated content.
- Sanitize all user-provided strings before rendering in HTML (prevent XSS). Use framework-provided escaping — don't roll your own.

## SQL injection prevention

- **Never interpolate user input into SQL strings.** Use parameterized queries, ORM methods, or query builders exclusively.
- If writing raw SQL, use `$1`, `%s`, or named parameter syntax — never f-strings or string concatenation with user data.

## Authentication & authorization

- Enforce auth at the API layer, not just the UI. A missing frontend button is not access control.
- Check permissions on every request — don't assume a valid session means the user can access the resource.
- Use row-level security (RLS) in the database when the platform supports it.

## OWASP awareness

- Stay aware of the OWASP Top 10. When writing code that handles user input, authentication, file uploads, redirects, or session management — think about the relevant attack vectors.
- Don't disable CORS protections without understanding the implications. Don't use `*` for allowed origins in production.
- Don't expose stack traces, internal paths, or database errors to end users.

## Dependency security

- Run `npm audit` / `pip audit` regularly. Don't ignore high/critical vulnerabilities.
- Before adding a dependency, check its maintenance status, download count, license, and known vulnerabilities.
