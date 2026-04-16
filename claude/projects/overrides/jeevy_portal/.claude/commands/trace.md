---
description: Trace the data flow for a feature or endpoint end-to-end across the stack
---

Trace the data flow for the feature, endpoint, or user action I describe — from the UI click all the way to the database and back.

## Before you start

Read `shared-docs/architecture/INDEX.md` if you haven't already this session. Use it to locate the relevant architecture map(s) for the layer you're tracing.

## What to produce

A top-to-bottom trace showing every hop, with file paths and line numbers at each step:

1. **Frontend trigger** — the component, button, or effect that initiates the action
   - Which feature module (`frontend/src/features/<domain>/`)
   - Which Redux action, RTK Query endpoint, or direct fetch
   - What payload shape is sent

2. **Network layer** — the API call
   - RTK Query endpoint definition (`*Api.ts`)
   - HTTP method, URL, request body
   - Base query chain: `conditionalBaseQuery → fastApiBaseQuery` (snake_case conversion)

3. **Backend route** — the FastAPI handler
   - File: `backend/api/v1/<domain>.py`
   - Pydantic request model
   - Dependencies injected (auth, tenant, db session)

4. **Service layer** — the business logic
   - File: `backend/core/services/<domain>/`
   - Which service methods are called, in what order
   - External service calls (Gemini, Qdrant, other microservices)

5. **Repository / data access**
   - SQL queries or ORM calls
   - Qdrant collections touched
   - Redis keys read/written

6. **Database schema** — the tables involved
   - Joins, filters, tenant scoping
   - Any RLS policies

7. **Response path** — back up through the stack
   - Response envelope shape
   - snake_case → camelCase conversion on the way out
   - Redux cache updates, component re-renders

## Output format

Use a Mermaid sequence diagram showing the flow, followed by a numbered list of the hops with file:line references so I can jump to each one.

Highlight any surprising behavior, potential bottlenecks, or places where the flow deviates from the standard pattern documented in the architecture maps.
