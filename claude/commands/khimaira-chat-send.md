# /khimaira-chat-send <chat_id> <body...> — send a chat message

Send a message to a chat you're an accepted member of. The message lands in every other accepted member's context as a `<channel>` block within ~1s.

## Steps

1. Parse `$ARGUMENTS`: first token = `<chat_id>`, everything after = body.
2. Resolve your own session id.
3. Call `mcp__khimaira__chat_send(session_id=<my_id>, chat_id=<chat_id>, body=<body>)`.
4. Print confirmation: `💬 sent (msg id <id>) to <chat_id>`.

## Notes

- If you're not an accepted member, the daemon returns 403 and the tool surfaces the error verbatim.
- Body is verbatim — supports markdown, code blocks, etc. The receiving agent sees it inside the `<channel>` tag body.
- For sending the same message to many sessions outside an active chat, use `/tell <session> <message>` per peer instead — chat is for ongoing conversation, not broadcast.
