# AGENTS.md — global instructions for Codex CLI

Third sync target for the same source-of-truth rules that drive Claude Code
(`~/dotfiles/claude/rules/`) and Cursor (`~/dotfiles/cursor/rules/`). See
`~/dotfiles/claude/rules/personal/workflow.md` → "Rule file sync" for the
sync discipline this file is bound by.

Codex's AGENTS.md has no `@file`-import mechanism (verified against Codex's
own dogfooded `AGENTS.md` in its source tree, which is flat markdown with no
import syntax) — Claude Code's CLAUDE.md inlines each rule file directly via
`@path` imports; this file can't do that, so it carries the same content as
`~/dotfiles/claude/rules/DIGEST.md` (the load-bearing-principles version of
every rule) inlined below, plus pointers to the full rule files for depth.
**When DIGEST.md regenerates (`claude/rules/.generate-digest.sh`), manually
re-sync the "Digest" section below in the same change** — this file doesn't
auto-regenerate the way DIGEST.md does.

## Digest

### Personal

**approach** — INTJ-T style — directness, depth over surface, real
trade-offs. Challenge bad ideas with reasoning, never silently agree.
Research before implementing; understand who calls a file before changing
it. Full: `~/dotfiles/claude/rules/personal/approach.md`

**bug-class-enumeration** — For any bug consult framed as "fix THIS
instance", first output must be a bug-class enumeration: abstract the class,
list ALL known code paths, mark each BROKEN/SAFE/UNKNOWN. Then design fixes
that close the CLASS, not the instance — a chokepoint (bug unrepresentable
by construction) beats an arm (patches the paths visible now). Full:
`~/dotfiles/claude/rules/personal/bug-class-enumeration.md`

**workflow** — Format every file you modify (Prettier/Black) — never bypass
pre-commit hooks. Workflow: research → fact-check docs → plan with detail →
implement → verify. Full: `~/dotfiles/claude/rules/personal/workflow.md`

**orchestration** — Default to decomposing and orchestrating substantive,
parallelizable work via subagents from the first turn — don't wait to be told
to "parallelize" or "spawn agents." Fan out independent slices concurrently,
serialize shared-file work, keep the adversarial-verify layer. Subagents
propose/implement; you keep every load-bearing decision. Full:
`~/dotfiles/claude/rules/personal/orchestration.md`

**khimaira-tools** — For conceptual codebase queries on khimaira/jeevy, try
`seance_semantic_search` before grep, and `notebook_ask` for a code-grounded
narrative answer (the mnemosyne oracle was retired 2026-07-24 — it went stale
faster than it could re-bake). For any UI change, verify it rendered (Specter-
equivalent — Codex has no browser-CDP tool yet; screenshot/manual check
instead). Full: `~/dotfiles/claude/rules/personal/khimaira-tools.md`

### Engineering

**conventions** — Match existing patterns first. camelCase frontend (except
React PascalCase, module CONSTANTS); PEP 8 + Black backend. Names must
reflect what they do — no `data`, `result`, `temp`. Delete dead code the
moment it's confirmed dead.

**error-handling** — Never swallow errors silently — log, re-throw, or
handle explicitly. Fail fast and loud. Include context (path, ID, operation)
in messages. Backend uses `{error: {code, message, details}}` envelope; map
exceptions → HTTP status explicitly.

**security** — No secrets in code, ever — env vars or secrets manager only.
Validate at every system boundary. Parameterized queries always; never
interpolate user input into SQL. Enforce auth at the API layer, not the UI.

**testing** — Tests catch regressions and document behavior. Test behavior
not implementation. Always cover the unhappy path. Deterministic only — no
flaky tests. High coverage on critical paths; don't chase 100%.

**debugging** — Reproduce first — without a reliable repro you can't verify
the fix. Read the actual error, trace data flow, isolate the layer, form a
hypothesis, test it, fix the root cause (not the symptom), add a test.

**performance** — Measure first, optimize second. No blocking I/O in async
handlers. Paginate list endpoints. Index columns used in WHERE/JOIN/ORDER BY.
Cache deliberately — stale cache is worse than no cache.

**database** — Never edit existing migrations — create a new one.
Parameterized queries only. snake_case tables/columns. Foreign-key
constraints + NOT NULL by default.

**api-design** — REST with plural-noun resources and proper HTTP verbs.
URL-versioned (`/api/v1/`). Consistent `{data, meta}` envelope. Paginate
everything.

**dependencies** — Check if existing packages cover the need before adding.
Evaluate maintenance + downloads + license + bundle size. Pin exact
versions; commit lockfiles.

**ai-engineering** — The LLM is a bounded perception component, not the
system. Cross the boundary once — unstructured → structured → code — never
let the model past it. Resolve/match deterministic-first. Propose, don't
dispose.

Full engineering rule bodies: `~/dotfiles/claude/rules/engineering/*.md`

## Codex-specific notes (not in the Claude Code digest)

- **Git commits, pre-commit hooks**: pure git-level infrastructure — apply
  automatically to any `git commit` regardless of which tool drives it.
  Nothing to port mechanically here; the only thing that needs saying is the
  behavioral convention: if a pre-commit hook fails, fix the underlying
  issue — never `git commit --no-verify` to route around it. Same rule as
  Claude Code, restated because there's no shared enforcement layer between
  the two tools to rely on instead.
- **Only create commits when explicitly asked.** Don't commit proactively
  just because a change looks complete.
- **khimaira MCP tools available**: `khimaira-chat` (cross-session real-time
  chat — `chat_send`, `chat_my_chats`, etc.) and `khimaira` (the full
  session/notebook/seance/scarlet/themis/kg surface). Both registered in
  `~/.codex/config.toml`. The `khimaira` server has no blanket
  auto-approval — expect normal per-tool approval prompts until the user
  explicitly opts into automating that.
- **Internal roster pattern** (2026-07-15): `spawn_agent` subagents get
  Themis role governance via `khimaira.hooks.codex_pretool` — role is
  derived from the EXACT `task_name` passed to `spawn_agent` (must be
  `consultant`, `gatekeeper`, `agent_1`, or `agent_2` — anything else falls
  through ungoverned, Themis fails open not closed on an unrecognized role).
  See `packages/khimaira/src/khimaira/hooks/codex_roster_prompts.py` for the
  exact role-instruction text to pass in each subagent's initial message —
  `spawn_agent` has no system-prompt parameter, so the entire behavioral
  grounding has to live there.
- **No genuine mid-turn push exists in Codex today** (confirmed 2026-07-15
  via exhaustive testing — app-server thread injection evicts the owning
  client, MCP progress notifications aren't surfaced to the model). Delivery
  is turn-boundary hooks + the optional `codex_watcher.py` kitty-injection
  daemon for near-real-time latency on genuinely idle sessions.
