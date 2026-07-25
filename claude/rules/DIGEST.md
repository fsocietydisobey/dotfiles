# Rules Digest

> **Auto-generated from each rule's `## TL;DR` section. Don't edit by hand —
> edit the underlying rule and re-run `claude/rules/.generate-digest.sh`.
> Pre-commit hook regenerates on every commit that touches a rule.**

_Load-bearing principles only. Full rule bodies live next to this file._

## personal

**approach** — INTJ-T style — directness, depth over surface, real trade-offs. Challenge bad ideas with reasoning, never silently agree. Research before implementing; understand who calls a file before changing it.

**behavioral-rule-promotion** — When a behavioral discipline rule keeps being violated (observed ≥2 times),
promote it to STRUCTURAL via the 3-layer template: role-doc section +
Themis hint (severity=warn) + lint test guarding the role-doc text.
Behavioral rules drift; structural rules don't. Observed across 6+ gaps
in the 2026-05-25/2026-05-26 session.

**bug-class-enumeration** — For any bug consult framed as "fix THIS instance", the architect's FIRST output must
be a bug-class enumeration: abstract the class, list ALL known code paths, mark each
BROKEN/SAFE/UNKNOWN. "Close the class" means install the CHOKEPOINT — one mandatory path
+ a bypass-gate that makes the bug unrepresentable — NOT patch every known path (that's an
"arm"; the class reopens on the next path). Root-fix test: "can new code still create this
bug?" Yes → arm, physically-no → chokepoint. Master requests enumeration first; reviews
verify class coverage, not just the diff.

**khimaira-tools** — For conceptual codebase queries, try `seance_semantic_search` BEFORE grep; for a code-grounded narrative "what does X do / how does Y work" answer, `notebook_ask` (it cites the live code and flags stale notes). For ANY UI change (verify it rendered) or browser-visible bug (debug it), use `specter_debug_snapshot` — Specter is a verify tool, not just a debug tool; `tsc passing` ≠ "the user sees what I think they see." For "map this feature / what does it export" questions, call `scarlet_scan_features` or `scarlet_extract_feature_metadata`. For meeting recording / transcription, the `sibyl_*` tools. Reflexive grep loses information these tools have already indexed.

**orchestration** — Default to decomposing and orchestrating substantive, parallelizable work via
subagents from the first turn — don't wait to be told to "parallelize" or
"spawn agents." Fan out independent slices concurrently, serialize shared-file
work, keep the adversarial-verify layer. Subagents propose/implement; you
keep every load-bearing decision.

**workflow** — Format every file you modify (Prettier/Black) — never bypass pre-commit hooks. Workflow: research → fact-check docs → plan with detail → implement → verify. Keep `~/.claude/rules/`, `~/.cursor/rules/`, and `~/.codex/AGENTS.md` in sync.
One to three sentences. Lead with the rule itself, no preamble. The
reader has the rest of the file right there if they want depth.

## engineering

**ai-engineering** — The LLM is a bounded perception component, not the system. Cross the boundary once — unstructured → structured → code — and never let the model past it: it turns messy input into a validated schema; every load-bearing decision on that structured data is deterministic code. Resolve/match deterministic-first (exact → algorithmic fuzzy → LLM residual, human-gated). Propose, don't dispose.

**api-design** — REST with plural-noun resources and proper HTTP verbs. URL-versioned (`/api/v1/`). Consistent `{data, meta}` envelope. Paginate everything (cursor for large/realtime, offset for small/stable). ISO 8601 UTC timestamps; UUIDs in public surface.

**conventions** — Match existing patterns first. camelCase frontend (except React PascalCase, module CONSTANTS); PEP 8 + Black backend. Names must reflect what they do — no `data`, `result`, `temp`. Delete dead code the moment it's confirmed dead.

**database** — Never edit existing migrations — create a new one. Parameterized queries only. snake_case tables/columns. Index WHERE/JOIN/ORDER BY columns. Foreign-key constraints + NOT NULL by default. Row-level security for multi-tenant.

**debugging** — Reproduce first — without a reliable repro you can't verify the fix. Read the actual error, trace data flow, isolate the layer, form a hypothesis, test it, fix the root cause (not the symptom), add a test. Don't shotgun-debug.

**dependencies** — Check if existing packages cover the need before adding. Evaluate maintenance + downloads + license + bundle size. Pin exact versions; commit lockfiles. Run `npm audit` / `pip audit` regularly. Clean up config + types when removing a dep.

**error-handling** — Never swallow errors silently — log, re-throw, or handle explicitly. Fail fast and loud. Include context (path, ID, operation) in messages. Backend uses `{error: {code, message, details}}` envelope; map exceptions → HTTP status explicitly.

**performance** — Measure first, optimize second. No blocking I/O in async handlers. Lazy-load on frontend; watch for N+1 queries. Index columns used in WHERE/JOIN/ORDER BY. Paginate all list endpoints. Cache deliberately — stale cache is worse than no cache.

**security** — No secrets in code, ever — env vars or secrets manager only. Validate at every system boundary. Parameterized queries always; never interpolate user input into SQL. Enforce auth at the API layer, not the UI.

**testing** — Tests catch regressions and document behavior. Test behavior not implementation. Always cover the unhappy path. Deterministic only — no flaky tests. High coverage on critical paths; don't chase 100%.

---
_Regenerate: `claude/rules/.generate-digest.sh` · Source: each rule's TL;DR section_
