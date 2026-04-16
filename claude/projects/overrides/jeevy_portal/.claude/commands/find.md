---
description: Find code related to a vague concept or topic across the codebase using a structured multi-tool search
---

The user is asking about a topic without naming a specific file, symbol, or path. Find the relevant code using a structured multi-tool search — don't grep blindly, don't guess.

## The problem you're solving

Vague queries like "where's the rate limiting logic?" or "how does the auth flow work?" can't be answered by reading random files. Without vector embeddings (we don't have them — see `nvim-notes/AI-WORKFLOW.md` for why), you need to search deliberately through layers of increasing fuzziness.

## Search strategy — work through these IN ORDER

### Step 1: Check the glossary

The glossary at `shared-docs/architecture/GLOSSARY.md` is hand-curated. The user has already mapped common concepts to file locations. **Always check this first.**

If the topic matches a glossary entry, jump straight to those files. **Stop here** if you have a confident match. Don't burn tool calls searching when the answer is already documented.

If the glossary has a partial match (e.g., the user asked about "throttling" and the glossary has "rate limiting"), follow the linked files anyway and verify they cover what was asked.

### Step 2: Check the architecture maps

If the glossary has nothing, read the relevant architecture map(s) from `shared-docs/architecture/`:

| Topic area | Map to read |
|---|---|
| Backend services / business logic | `BACKEND_SERVICES.md` |
| HTTP endpoints | `BACKEND_API.md` |
| LangGraph agents | `BACKEND_AGENTS.md` |
| Frontend feature modules | `FRONTEND_FEATURES.md` |
| Frontend state management | `FRONTEND_STORE.md` |
| Shared/cross-cutting frontend | `FRONTEND_SHARED.md` |

The architecture maps describe each domain at a high level. They'll tell you which directory to look in even if they don't name the exact file.

### Step 3: Serena symbol search

Use Serena's `find_symbol` with the topic keywords. Try **multiple variations** in parallel — don't just try the original term:

- Original term: `rate limit`
- Camel case: `rateLimit`, `RateLimit`
- Snake case: `rate_limit`
- Common synonyms: for "rate limit" try `throttle`, `quota`, `limiter`, `RateLimiter`

Serena returns symbols (classes, functions, methods) by name with file:line references and signatures. This is dramatically more accurate than grep for code-related queries because it understands the symbol table, not just the text.

### Step 4: Serena pattern search

Use Serena's `search_for_pattern` with regex variations of the term. Look for:
- Function/class definitions: `def.*rate.?limit`, `class.*RateLimit`
- Configuration keys: `RATE_LIMIT`, `rate_limit:`, `"rateLimit"`
- Comments mentioning the topic: `# .*rate.limit`

### Step 5: Glob common locations

Based on the topic category, glob likely directories:

| Topic type | Likely locations |
|---|---|
| HTTP middleware concepts | `backend/core/middleware/**/*.py`, `backend/api/v1/__init__.py` |
| Service-layer concepts | `backend/core/services/**/*.py` |
| Agent / LLM concepts | `backend/core/agents/**/*.py` |
| Frontend UI concepts | `frontend/src/features/**/*.tsx`, `frontend/src/shared/**/*.tsx` |
| Frontend state concepts | `frontend/src/store/**/*.ts`, `frontend/src/store/**/*.js` |
| Database/schema concepts | `backend/core/models/**/*.py`, `backend/alembic/versions/*.py` |

### Step 6: Last resort — broad ripgrep

If steps 1-5 find nothing confident, use the Grep tool with broad patterns. But this is the *last* resort — by this point you should suspect the concept doesn't exist in the codebase yet.

## Reporting the result

Return a ranked list of the top 3-5 most likely files:

```
**Top matches for "<topic>":**

1. `path/to/file.py:line` — <1 sentence on what this file does and why it matches>
   - Found via: <which step found it: glossary / arch map / Serena symbol / Serena pattern / glob>

2. `path/to/other.py:line` — ...

**Confidence:** high / medium / low

**If low confidence:** explain what you searched for and why nothing matched. Suggest the user clarify or confirm the concept exists.
```

## After answering

If you found the answer through fallback search (not the glossary), **suggest the user add it to `shared-docs/architecture/GLOSSARY.md`** so future sessions skip the search. This is how the glossary stays useful — every successful search becomes a future shortcut.

## What NOT to do

- **Don't guess.** If you can't find it, say so. Don't fabricate a file path that "probably exists."
- **Don't read every file in a directory.** Use Serena's overview tools instead.
- **Don't grep with overly narrow terms.** "rate limit" might appear as "throttle" or "quota" — try variations before giving up.
- **Don't skip the glossary.** It's the cheapest, most accurate source. Always check first.
- **Don't recommend embeddings as a fix.** We deliberately skipped them — see `nvim-notes/AI-WORKFLOW.md` for the reasoning.
