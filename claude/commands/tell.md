# /tell <target> <message> — send to anything (session OR project)

Smart-routed one-way send. The `<target>` can be:
- A **session name** (e.g. `khimaira-builder`) — delivered as a notice to that session's inbox.
- A **khimaira-attached project label** (e.g. `backend`, `khimaira`) — delivered as a handoff scoped to that project's cwd, so ANY future session running there sees it.

You don't pick the primitive. The server figures out which one based on the name and routes accordingly.

Use for:
- "FYI session X, I went with option C"
- "FYI anyone in jeevy_portal, starting from commit Y watch for Z"
- "thanks, landed"
- Any "you don't need to reply" cross-session note

For "I need an answer back in this same turn" use `/ask`.
To force project-handoff semantics (e.g. if there's both a session AND a project with the same name), use `/handoff <project> <message>` directly.

## Steps

1. `$ARGUMENTS` should be `<target> <message>`. Parse:
   - First whitespace-separated token = target (session name OR project label)
   - Everything after = message body
   - If parse fails, render usage: `/tell <session_or_project> <message>`. List currently-known targets by calling `mcp__khimaira__session_list` (sessions) and `Bash: khimaira attached` (projects).

2. Resolve your own session id (sender). Use the SessionStart hook value; fall back to `mcp__khimaira__session_list` if unknown.

3. Hit the smart-route endpoint via curl:
   ```bash
   curl -sS -X POST 'http://127.0.0.1:8740/api/route' \
     -H 'Content-Type: application/json' \
     -d '{"target":"<target>","text":"<message>","from_session_id":"<my_id>"}'
   ```

4. Parse the response. The `routed_as` field tells you which primitive was used:
   - `"notice"` — print `📨 sent as notice to session <target_session_id>`
   - `"project_handoff"` — print `📦 sent as project handoff scoped to <scope_cwd> — any future session in project '<project_label>' will see it`

5. **On 404** (neither session nor project matched): the response detail will say so. Print it verbatim and suggest the user run `khimaira attached` to see project labels or `session_list()` to see active session names.

## Notes

- The smart routing means `/tell backend "..."` works whether `backend` is a running session OR a khimaira-attached project (in the user's case: it's a project). Don't ask the user to disambiguate; let the server route.
- For notices: receiver agent's UserPromptSubmit hook surfaces the note on their next turn. Auto-expires after 3 surfaces if never explicitly acked.
- For project handoffs: receiver session's SessionStart hook surfaces it on first boot in matching cwd. 7-day TTL by default.
