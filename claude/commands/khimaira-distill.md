# /khimaira-distill [summary] — push curated domain knowledge into mnemosyne mid-session

For domain-lead sessions only. Extracts learnings into mnemosyne's PROVISIONAL layer so they're
available to future sessions even if the Stop hook never fires (long-lived leads rarely hit Stop).

**Two knowledge sinks for leads:**
- **mnemosyne PROVISIONAL** (this command) — surfaced at SessionStart via `mcp__khimaira__session_state`; good for patterns, footguns, key discoveries
- **`docs/domain/<domain>-knowledge.md`** (AUTHORITATIVE) — permanent human-readable reference; write here too

## Usage

```
/khimaira-distill
/khimaira-distill "key learnings from this spike: ..."
```

`$ARGUMENTS` = curated summary text (optional). If empty, you write the summary interactively in step 4.

## Steps

**1. Resolve session name + CWD**

Read session name from the `🆔 khimaira session_id` SessionStart block, or call
`mcp__khimaira__session_list()` and identify the current session. Store as `session_name` and `my_session_id`.
Use `$CWD` for the working directory.

**2. Detect domain**

Run (use the khimaira venv which has the package installed):
```bash
/home/_3ntropy/dev/khimaira/.venv/bin/python3 -c "
from khimaira.hooks.session_end_utils import detect_domain
print(detect_domain('SESSION_NAME_HERE'))
"
```
(substitute the actual session name)

If domain is `"general"`, branch on whether this is a MASTER session vs another non-lead role:

**Master-fan-out branch** (session name matches `*-0`, `master-*`, `janice-*`, or similar master-shaped pattern — typically the chat creator + orchestrator role):

This is the master-distill path. Master sessions accumulate cross-cutting knowledge (orchestration decisions, dispatch sequencing, architecture calls relayed from architect, gate adjudications). That knowledge belongs in *multiple* `project:domain` keys — one per code-domain the session touched + a `project:orchestration` key for master-level decisions.

Fan-out steps:
1. **Identify relevant target domains.** Read the summary text (`$ARGUMENTS` or the interactive summary from step 4). Map content to one or more of: `backend`, `frontend`, `data`, `devops`, `orchestration`. Default if uncertain: `orchestration` always + any code-domain explicitly mentioned in the summary.
2. **Split the summary by target domain.** For each target, extract the slice of bullets/paragraphs that belongs to that domain. Drop bullets that apply to none. Bullets that apply to multiple → duplicate into each relevant slice (small redundancy is fine; mnemosyne's Haiku distiller dedupes downstream).
3. **Loop the distill call** (Step 5 below) once per non-empty `(domain, slice)` pair. Build qualified key as `{project}:{domain}` per Step 3.
4. **Report** each distill result separately in Step 6 — show domain + pairs_extracted per call.

Skip the "general / hard stop" exit. Proceed to Step 3 (project detection) → Step 4 (summary write/parse) → Step 5 (multi-distill loop) → Step 6 (per-domain report).

**Non-master "general" branch** (session is an agent/consultant/gatekeeper/observer/critic/verifier/tracker/intake/analyst/architect — not a domain lead and not master):
```
⚠️ /khimaira-distill from a non-lead non-master session ("SESSION_NAME") doesn't have a natural domain target.
For agent/consultant/gatekeeper/critic/verifier/analyst/architect/observer/tracker/intake sessions, knowledge capture happens automatically via:
- the PostToolUse `harvest_approval` hook (per approved task)
- the session-end Stop hook (on session close)
Manual /khimaira-distill from these roles is rarely the right move.
If you really want to distill from here, set a lead session name first:
  mcp__khimaira__session_set_name(session_id, "<project>-<area>-lead-1")
```
Then stop.

**Detection tip:** if uncertain whether you're "master-shaped," check the chat membership: master is typically the `created_by` of the roster chat (per the 4-layer Themis role resolution, L2 `created_by-is-master` resolves master role from chat meta). If unsure, default to the master-fan-out branch — over-capturing into multiple project:domain keys is recoverable; failing to capture isn't.

**3. Detect project → build qualified domain key**

```bash
/home/_3ntropy/dev/khimaira/.venv/bin/python3 -c "
from khimaira.hooks.session_end_utils import detect_project
print(detect_project('CWD_HERE'))
"
```
(substitute actual cwd)

Build: `qualified_domain = "<project>:<domain>"` if project is non-empty and not `"unknown"`.

If `detect_project` returns `""` or `"unknown"` (cwd not inside a known project root):
```
⚠️ project undetectable from cwd — would distill to bare domain "<domain>" (no project prefix).
Bare keys collide across projects: jeevy:frontend and khimaira:frontend are separate;
plain "frontend" is shared by both. Confirm cwd is inside a known project root
(check `khimaira attached`) or proceed knowingly with the bare key.
```
Then ask the user to confirm before continuing (or stop if clearly wrong).

**4. Write the curated summary**

- If `$ARGUMENTS` is non-empty: use it verbatim as the summary.
- If `$ARGUMENTS` is empty: write a CONCISE summary now before proceeding.

Good summary content (target 5–15 bullets, no raw tool outputs):
- Patterns discovered this session
- Footguns and non-obvious constraints
- Key file paths / symbols worth knowing
- Architectural decisions made + why
- "Things I wish I knew when I started this session"

**5. Distill into mnemosyne**

```bash
/home/_3ntropy/dev/khimaira/.venv/bin/python3 - <<'PYEOF'
from khimaira.hooks.mnemosyne_client import distill
import json, sys

result = distill(
    domain="QUALIFIED_DOMAIN_HERE",
    transcript="""SUMMARY_HERE""",
    session_slug="SESSION_NAME_HERE",
)
if result is None:
    print("FAIL")
else:
    print(json.dumps(result))
PYEOF
```

Use the Bash tool to execute this, substituting actual values. The heredoc avoids quoting issues with multi-line summaries.

**6. Report result**

- If result is not `"FAIL"` / not None:
  ```
  ✅ distilled → QUALIFIED_DOMAIN — N pairs stored
  ```
  (N = `result.get("pairs_extracted", result.get("count", "?"))`)

- If result is `"FAIL"` (None from client = mnemosyne unreachable):
  ```
  ⚠️ mnemosyne unreachable (port 8766) — pair NOT stored.
  Check: curl http://127.0.0.1:8766/domains
  The Stop hook will retry on session end if the daemon recovers.
  ```

**7. Smoke-verify (optional but recommended)**

To confirm the pair landed under the right key:
```bash
curl -s http://127.0.0.1:8766/domains | python3 -m json.tool
```
Look for `"QUALIFIED_DOMAIN"` in the output with a non-zero pair count.

## Notes

- mnemosyne runs on port 8766. Fail-open: unreachable → report clearly, don't crash.
- The Stop hook auto-distills from the raw transcript on session exit. This command is the mid-session
  path — use it after significant discoveries rather than waiting for the session to end.
- Curated > raw: a 10-bullet summary distills better than 10,000 lines of transcript.
- The qualified domain key (`project:domain`, e.g. `jeevy:frontend`) prevents cross-project pollution.
  The same domain name in different projects gets separate mnemosyne namespaces.
