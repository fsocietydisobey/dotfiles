# /khimaira-orient [question | path | (empty)] — warm up session context

Run a structured orient sweep so the agent has the codebase mental model loaded BEFORE the user starts giving instructions. Solves the "first 5-10 tool calls of every fresh session are spent re-discovering project shape" problem.

## Arguments — three shapes

- **Empty** → orient on the current working directory.
- **Looks like a path** (starts with `/`, `~`, or `.`) → orient on that path instead of cwd.
- **Anything else** → treat as a focused question. Orient on cwd, then narrow with seance.

Examples:
```
/khimaira-orient
/khimaira-orient how does auth work in jeevy_portal
/khimaira-orient ~/work/jeevy_portal
/khimaira-orient ~/work/jeevy_portal where does retry logic live
```

## Phase budget

Aim for ~12-15 tool calls total. Each phase has a soft budget; skip phases that don't apply.

## Steps

### 1. Parse `$ARGUMENTS`

- Strip leading whitespace.
- If empty: `target_path = cwd`, `question = None`.
- If first token starts with `/`, `~`, or `.`: `target_path = first token` (expand `~`), `question = rest if any`.
- Else: `target_path = cwd`, `question = $ARGUMENTS`.

Resolve `target_path` to an absolute path.

### 2. Project identification (~3 tool calls)

Read the project's identity layer:
- `Read <target_path>/CLAUDE.md` — if present, this is the canonical agent-readable description
- `Read <target_path>/README.md` — fallback when no CLAUDE.md
- `Read <target_path>/NORTH_STAR.md` — strategic doc, if present
- `Read <target_path>/pyproject.toml` OR `package.json` OR `Cargo.toml` OR `go.mod` — detect language/framework

In parallel: `Bash: cd <target_path> && git log --oneline -5 && git status --short` — recent commits + working-tree state.

Don't read all four type files — pick the first present. If none, fall back to `Bash: ls -la <target_path>` to eyeball structure.

### 3. Cross-session signals (~3 tool calls)

- `mcp__khimaira__session_state(<my-session-id>, recent=5)` — what this session has decided + touched (catches mid-session resumes)
- `mcp__khimaira__session_list()` — what other sessions exist in this workspace
- `mcp__khimaira__session_consume_handoffs(<my-session-id>, cwd=<target_path>)` — pull any project-scoped handoffs waiting for this session

If `consume_handoffs` returns non-empty, surface them with **directive framing** — they're tasks waiting to be picked up, not FYIs.

### 4. Structural map (~2-3 tool calls)

- `mcp__khimaira__scarlet_analyze_project(path=<target_path>)` — framework + state mgmt + folder strategy
- `mcp__khimaira__scarlet_scan_features(path=<target_path>)` — if features-organized; returns [] cleanly otherwise
- If scarlet returns nothing useful (project isn't features-organized, e.g. Python monorepo): fall through to `Bash: ls -la <target_path>` + maybe `Glob` for `**/*.py` count by directory

### 5. Focused search (~3-5 tool calls, only if `question` was provided)

- `mcp__khimaira__seance_list_projects()` — confirm an index exists. The project name is usually the basename of `target_path`.
- If indexed: `mcp__khimaira__seance_semantic_search(query=<question>, project=<name>, top_k=10)`
- Read the top 2-3 result files (full Read, not partial — seance returns chunks, you want the surrounding context)
- If NOT indexed:
  - For a quick orient, skip indexing (would take 30s-2min) — fall through to `Grep` for keywords from the question
  - Note to user in the synthesis: "project not in seance index — narrow search ran via grep. Run `seance index_project` to enable semantic search."

### 6. Open work surface (~1-2 tool calls)

- `mcp__khimaira__list_tasks(hook_safe_only=false)` — assigned tasks from configured task sources (jsonl, github, linear)
- `Bash: ls <target_path>/tasks/ 2>/dev/null` — in-tree task specs (if the convention is followed)

Optional: `mcp__khimaira__session_recent_decisions(recent_per_session=3)` for a cross-session decision feed.

### 7. Synthesis — render a structured orient report

Format the result so a user (or a future read-back) can scan in ~30 seconds:

```
📍 Orient: <target_path>

## Project
<1-2 sentences from CLAUDE.md/README. What this is, who uses it.>
<Language/framework, e.g. "Python 3.12 uv workspace, FastAPI + LangGraph">

## Current state
- HEAD: <short sha> <commit message>
- Working tree: <clean | N modified | N untracked>
- Active sessions in this project: <names + statuses>
- Pending handoffs: <count, or "none">

## Focused answer  (only if question)
<2-4 paragraphs synthesizing from seance results + read files.
Cite file:line for every claim.>

## Watch for
- <gotcha 1 from CLAUDE.md or invariant patterns>
- <gotcha 2 — uncommitted sibling-session work? schema drift? known broken test?>
- <gotcha 3 — open question or in-flight handoff worth knowing about>

## Open work
- Tasks: <N open from task sources — list 3-5 most relevant>
- In-tree specs: <tasks/<name>/IMPLEMENTATION.md files modified recently>

✅ Oriented. Awaiting instructions.
```

If no question was provided, skip the "Focused answer" section but still produce all others.

## Anti-patterns

- **Don't list every file.** This is orient, not inventory. ~10 most-relevant files.
- **Don't skip the cross-session check.** A pending handoff that you don't surface here will surprise the user mid-task. Step 3 is load-bearing.
- **Don't run all phases in series when they can parallelize.** Steps 2 (project identification), 3 (cross-session), 5 (focused search), 6 (open work) can fire in parallel batches via multiple tool calls in a single message.
- **Don't index seance silently.** If the project isn't indexed, surface that explicitly in the synthesis + suggest the user invoke `seance index_project` — don't trigger a 30s-2min indexing without consent.
- **Don't speculate.** If you don't know something, say so. The orient sets up TRUTH baseline; bad orients compound into bad downstream decisions.

## When NOT to use

- **Mid-task** — orient is for fresh-session startup. Calling it mid-conversation re-loads context the agent already has, burns tool calls + tokens.
- **Single-file work** — if the user already named the file (e.g. "fix the typo on `utils.py:42`"), orient is overkill. Just open + fix.
- **Quick factual asks** — "what's the Python version constraint" doesn't need a 15-call orient. Read one file.

## Related commands

- `/scan` — narrower: scarlet structural scan only. No question handling, no cross-session.
- `/search <q>` — focused seance search only. No orient.
- `/khimaira-seance <q>` — full seance family directive. Similar but skips the project-identification + handoff steps.
- `/handoffs` — surfaces just the cwd-scoped handoffs. /khimaira-orient does this AS PART OF orient + more.

When the user wants the breadth (project + state + question + open work) → /khimaira-orient. When they want a specific slice → narrower tool.
