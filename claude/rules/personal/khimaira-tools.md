# Khimaira tools — when to reach for them

## TL;DR

For conceptual codebase queries, try `seance_semantic_search` BEFORE grep. For frontend bugs you can see in the browser, start with `specter_debug_snapshot`. For "map this feature / what does it export" questions, call `scarlet_scan_features` or `scarlet_extract_feature_metadata`. For meeting recording / transcription, the `sibyl_*` tools. Reflexive grep loses information these tools have already indexed.

## Why this rule exists

Khimaira ships three perception tools — Séance (semantic search), Specter (browser debug), Scarlet (codebase cartography) — but in practice they lose to reflexive `Grep` and `Read`. The tools' descriptions alone don't establish primacy; an explicit rule does. This file IS that rule.

The cost asymmetry: grep + a handful of file reads burns 5-20 tool calls and tokens for context that one `seance_semantic_search` would return in a single call. The deciding factor is whether the question is *symbolic* (exact name → grep wins) or *conceptual* (meaning → seance wins).

## Séance — semantic search

**Use when** the question is conceptual, not symbolic:

- "How does auth work in this app?"
- "Where do we handle retries / rate limiting / pagination?"
- "Find code related to <topic>" when the topic isn't a function name
- "What handles file uploads?"
- Looking for *patterns* across a codebase (e.g. "all places we serialize datetimes")

**Skip when** you have an exact symbol or string — `Grep` is faster and cheaper for those.

**Workflow:**

1. Check `seance_list_projects()` to confirm the project is indexed (one quick call).
2. If yes, call `seance_semantic_search(query=<natural-language-query>, project=<name>, top_k=10)`.
3. Read the top 2-3 results with the standard `Read` tool to build context, then proceed.
4. If the project ISN'T indexed, fall back to grep + recommend the user run `khimaira attach <project>` (which will eventually auto-index) or invoke `seance_index_project(path=...)` directly.

If `semantic_search` returns nothing useful, rephrase the query more abstractly — embeddings are sensitive to framing. Don't keyword-optimize the query; describe what you're looking for conceptually.

## Specter — browser debugging via CDP

**Use when** the bug is visible in the browser:

- Page misbehavior, console errors, network failures, layout regressions
- "Why is this button not working?"
- "What did the API return for that request?"
- React component-tree inspection
- Anything you'd otherwise ask the user to screenshot or open DevTools for

**Skip when** the bug is backend-only (no browser involvement) or the user hasn't started Chrome with `--remote-debugging-port=9222` (Specter needs CDP connectivity).

**Workflow:**

1. **Always start with `specter_debug_snapshot()`** — one call returns screenshot + page info + console errors + network errors + page structure. Use this first; call individual tools only to drill into specifics.
2. For data-shape questions, use `specter_evaluate_js("console.log(JSON.stringify(...))")` then `specter_get_console_logs()`. Do not guess at runtime data — inspect it.
3. For navigation during an in-app flow, prefer `specter_click_element` over `specter_navigate_to` — clicking exercises the app's router and preserves state. Use `specter_router_navigate` for deep-linking; reserve hard `navigate_to` for cross-origin or deliberate resets.
4. Wrong data after an API call? `specter_get_network_log(url_filter='/api/...')` — the bug is often in the response transformation, not the component.

## Sibyl — meeting recording + transcription

**Use when** the user mentions a meeting, audio file, or transcript:

- "Start recording the meeting" → `sibyl_record_start`
- "I'm done with the meeting" → `sibyl_record_stop(recording_id)`
- "What's still recording?" → `sibyl_list_active_recordings`
- "Transcribe this audio file" → `sibyl_transcribe(audio_path)`
- "Summarize / extract action items from this meeting" → `sibyl_process(audio_path)` (full LangGraph pipeline: transcribe → summarize + extract + emotion in parallel)
- "Just give me a summary of this transcript" → `sibyl_summarize(transcript)`

**Skip when** there's no audio source — Sibyl needs a WAV file or live mic / system-audio capture. Doesn't generate audio from text.

**Workflow:**

- For an in-progress meeting: `record_start` → meeting happens → `record_stop` returns the path → `process(path)` runs the full pipeline in one call.
- For an existing audio file: `process(path)` directly.
- For narrower needs, `transcribe` (transcript only) or `summarize` (transcript → summary) are cheaper than the full pipeline.

Sibyl's name comes from the Cumaean Sibyl whose body withered until only her voice remained, preserved in writing — same shape as a meeting recording outliving its moment.

## Scarlet — codebase cartography

**Use when** the question is about *structure*, not behavior:

- "What features does this project have?"
- "What does this feature export?"
- "What's the dependency graph?"
- "Generate / refresh a CLAUDE.md for feature X"
- "Find consumers of this feature"
- Onboarding a new feature into the AI-readable docs scaffolding

**Skip when** the codebase isn't feature-organized (returns `[]` cleanly but you've wasted a tool call) — Scarlet expects a `features/` folder convention. Most React/Next.js projects fit; most monorepos and Python libraries don't.

**Workflow:**

1. `scarlet_analyze_project(project_root)` to confirm framework + structure
2. `scarlet_scan_features(project_root)` to list features
3. For one feature: `scarlet_extract_feature_metadata(feature_path)` to see exports + structure
4. `scarlet_extract_invariants(feature_path)` surfaces warning comments / TODOs / magic numbers worth knowing
5. `scarlet_build_claude_md(...)` to generate the docs skeleton; you fill in Vocabulary / Conventions / Common tasks / Gotchas from reading code

Scarlet generates **structure**; you generate **meaning**. Don't expect prose from it — that's your job.

## Decision tree — which tool first?

```
Question shape:
├── Exact symbol / known string / single regex
│   └── Grep (or Serena's find_symbol if available)
├── Conceptual codebase question ("how does X work")
│   └── seance_semantic_search (after confirming index exists)
├── Visible-in-browser bug
│   └── specter_debug_snapshot → drill in
├── Feature structure / dep graph / docs scaffolding
│   └── scarlet_*
└── Cross-file refactor / call-graph navigation
    └── Serena (LSP-based, if available) > grep
```

When in doubt and the project is indexed in Séance, try `seance_semantic_search` first — it has the highest payoff-per-call for the most common case (conceptual question), and a miss is cheap (returns nothing, you fall through to grep).

## Anti-patterns

- **Don't grep when you could semantic-search.** "How does X work" + 8 grep calls + 4 file reads is the failure mode. One `seance_semantic_search` returns the same answer.
- **Don't guess at browser-side state.** If you need to know what `myVar` looks like at runtime, `specter_evaluate_js` it — don't reason from the React source about what state *should* be.
- **Don't ask Scarlet for prose.** It surfaces structure (exports, dep graphs, invariant candidates). Prose comes from the AI reading code with that structure as scaffolding.
- **Don't skip `seance_list_projects` before searching.** A 1-tool-call check beats a 0-result search that wastes a round trip + leaves you unsure if the project is indexed.

## What about `Read`?

`Read` is always available and always cheap when you know the path. The point of these tools isn't to replace `Read` — it's to make `Read` purposeful. Séance tells you *which* files to Read for a conceptual question. Scarlet tells you the *structural shape* before you Read. Specter tells you *runtime behavior* that Read can't show you.
