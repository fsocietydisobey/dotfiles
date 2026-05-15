# /khimaira-chat <peers...> [--new] [--title "..."] — create a chat room

Create (or resume) a real-time chat with one or more other Claude Code sessions. Messages land in each peer's context as `<channel source="khimaira-chat" ...>` blocks within ~1s.

Default: stable per-pair-or-group `chat_id` derived from member ids. The same members re-running this command resume the existing transcript. Pass `--new` to start a fresh transcript with a distinct id.

## Steps

1. Parse `$ARGUMENTS`:
   - Optional `--new` flag (boolean; default false)
   - Optional `--title "..."` flag (string)
   - Remaining tokens = peer session names or UUIDs (one or more required)
   - On malformed args render: `Usage: /khimaira-chat <peer1> [peer2 ...] [--new] [--title "Group Name"]`

2. Resolve your own session id (sender). Use the SessionStart hook value; fallback to `mcp__khimaira__session_list`.

3. Call `mcp__khimaira__chat_create_room(session_id=<my_id>, members=[peer1, peer2, ...], title=<title>, fresh=<--new>)`.

4. Print the response — includes the `chat_id`, full member list with states, and the title. Tell the user to share the `chat_id` with peers if they want to invite manually later (the create call already sent invites to all listed peers).

5. Each peer's next prompt will surface an inbox-style hint; they accept with `/khimaira-chat-accept <chat_id>`. Until they accept, your sends queue won't be delivered to them (they're `pending`).

## When NOT to use

- For "leave a note for them to see when they wake" → `/tell <session> <message>` (uses `session_post_notice`, doesn't require an active chat)
- For "I need an answer right now" → `/ask <session> <question>` (blocks for synchronous reply)
- For one-shot scheduled work targeted at a session → `/schedule-task <session> <when> <prompt>`

Chat is for ongoing back-and-forth conversation, where both parties are active.
