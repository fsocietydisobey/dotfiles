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

If domain is `"general"`:
```
⚠️ /khimaira-distill is for domain-lead sessions only.
This session ("SESSION_NAME") doesn't match a domain-lead pattern (backend-lead, frontend-lead, data-lead, devops-lead).
Set a lead session name first: mcp__khimaira__session_set_name(session_id, "<project>-frontend-lead-1")
```
Then stop.

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
