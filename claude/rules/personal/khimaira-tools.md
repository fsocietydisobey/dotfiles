# Khimaira tools — when to reach for them

## TL;DR

For conceptual codebase queries, try `seance_semantic_search` BEFORE grep. For ANY UI change (verify it rendered) or browser-visible bug (debug it), use `specter_debug_snapshot` — Specter is a verify tool, not just a debug tool; `tsc passing` ≠ "the user sees what I think they see." For "map this feature / what does it export" questions, call `scarlet_scan_features` or `scarlet_extract_feature_metadata`. For meeting recording / transcription, the `sibyl_*` tools. Reflexive grep loses information these tools have already indexed.

## Why this rule exists

Khimaira ships four perception tools — Séance (semantic search), Specter (browser verify + debug), Scarlet (codebase cartography), Sibyl (audio + transcription) — but in practice they lose to reflexive `Grep` and `Read`. The tools' descriptions alone don't establish primacy; an explicit rule does. This file IS that rule.

The cost asymmetry: grep + a handful of file reads burns 5-20 tool calls and tokens for context that one `seance_semantic_search` would return in a single call. The deciding factor is whether the question is *symbolic* (exact name → grep wins) or *conceptual* (meaning → seance wins).

**Each family section below ends with a full tool index.** This is load-bearing: most `khimaira__*` MCP tools are *deferred* — they appear by NAME in the session's tool list but their schemas aren't loaded until `ToolSearch(query="select:mcp__khimaira__<name>")` fetches them. So if a tool isn't in this rule, the model can't discover it by introspection — it has to know the name to query. The indexes below close that gap. When you need browser interaction beyond the workflow primitives, scan the index first; reach for `evaluate_js` LAST, not first.

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

### Séance — full tool index

Every `seance_*` tool. Use these names directly with `ToolSearch(query="select:mcp__khimaira__seance_<name>")` to load the schema before calling.

| Tool | One-line use case |
|---|---|
| `seance_list_projects` | Show what's indexed. ALWAYS call this first before searching. |
| `seance_semantic_search` | Natural-language query → ranked code chunks. The main primitive. |
| `seance_find_similar` | "What else looks like this symbol?" — duplicate-detection + pattern lookup. Takes (project, file_path, symbol_name). |
| `seance_index_project` | First-time index a project. Slow (parses + embeds all files). |
| `seance_reindex_changed` | Incremental update via `git diff`. Use this after pulls / commits, not full reindex. Project must be a git repo. |

## Specter — browser verification AND debugging via CDP

**MANDATORY FIRST STEP (production):** Every Specter session MUST start with `specter_list_tabs()` → `specter_connect_to_tab(<id>)`. There is no auto-pick — Specter never decides which tab to operate on. Any tool call before `specter_connect_to_tab` raises ConnectionError. This prevents Specter from silently stealing the user's active browser tabs.

**TEST ISOLATION:** Specter integration tests must run against a dedicated Chrome, NOT Joseph's daily Chrome (port 9222). Start the isolated instance before running tests:
```bash
bin/specter-test-chrome &          # launches Chrome on port 9223, isolated profile
SPECTER_TEST_PORT=9223 uv run pytest packages/specter/tests/
```
Without `SPECTER_TEST_PORT`, integration tests skip. The fallback to port 9222 (Joseph's Chrome) is no longer supported.

Specter has two equal-billed use cases. Both are first-class. The most common failure mode is treating it as debug-only and never reaching for it after shipping a UI change — that's how visual regressions leak past `tsc --noEmit`.

**Use case 1 — VERIFY (after any UI change):**

After editing a `.tsx` / `.jsx` / `.vue` / `.svelte` / template file that changes what the user sees, screenshot the result. `tsc passing` is not "the user sees what I think they see." `twMerge` can resolve Tailwind conflicts the opposite of how I expect; `flex-row` can lose to `flex-col`; z-index can hide the change; a stale build can serve the old bundle even though my source edit is correct.

Triggers (any of these = run `specter_debug_snapshot` before reporting done):

- Edited a component file under `apps/` / `src/components/` / `frontend/`
- Added or moved a UI element the user described visually ("draggable card", "new button", "make it red")
- Changed Tailwind classes on anything the user can see
- Rebuilt a bundle that the user is actively viewing in a browser tab

The verification flow:
1. Rebuild if needed (`npm run build` in the affected app — the daemon/server may serve a static `dist/`, so source edits aren't live until rebuild).
2. `specter_list_tabs` → find the relevant tab.
3. `specter_connect_to_tab` + `specter_reload_page` (or `navigate_to` if the change affects routing).
4. `specter_debug_snapshot` → confirm the change is visible.
5. Only if the screenshot looks wrong, drill into console logs / evaluate_js / component tree.

**Use case 2 — DEBUG (when the bug is visible in the browser):**

- Page misbehavior, console errors, network failures, layout regressions
- "Why is this button not working?"
- "What did the API return for that request?"
- React component-tree inspection
- Anything you'd otherwise ask the user to screenshot or open DevTools for

**Skip when** the bug is backend-only (no browser involvement) or the user hasn't started Chrome with `--remote-debugging-port=9222` (Specter needs CDP connectivity). Pure refactors with zero visual impact also skip verify — but the bar is "literally zero visual change," not "I think it looks right."

**Workflow (debugging side):**

0. **For UI-interaction-produces-no-visible-result bugs, START with `specter_get_redux_state(<slice-name>)` — NOT debug_snapshot, NOT source-code inspection, NOT reverting recent changes.** The Redux state is ground truth; the source code is just the theory of how state should look. If a click/toggle/selection produces zero visible response, the slice has the answer in <10 sec: check what the overlay/component hook is actually reading from store. Source inspection comes AFTER state confirms the bug location.

   Observed failure (2026-05-22, jp roster `__bootstrap__` sentinel incident): jp spent significant time reverting the grey-bbox feature + chasing HITL overlay bugs across multiple agent cycles. Root cause was a 1-line slice fix — `verificationSelectionSlice.setQuestion` not evicting the `__bootstrap__` sentinel when real questions arrived. `selectAllQuestionEntries[0]` always resolved to sentinel; `selectedDetectionIds` was always `[]`. One `specter_get_redux_state("verificationSelection")` showed the sentinel at index 0 immediately. Hours of source-code chase avoided by going to state first.

1. **Always start with `specter_debug_snapshot()`** — one call returns screenshot + page info + console errors + network errors + page structure. Use this first for OTHER browser-visible bugs (layout, console errors, network failures); call individual tools only to drill into specifics.
2. For data-shape questions, use `specter_evaluate_js("console.log(JSON.stringify(...))")` then `specter_get_console_logs()`. Do not guess at runtime data — inspect it.
3. For navigation during an in-app flow, prefer `specter_click_element` over `specter_navigate_to` — clicking exercises the app's router and preserves state. Use `specter_router_navigate` for deep-linking; reserve hard `navigate_to` for cross-origin or deliberate resets.
4. Wrong data after an API call? `specter_get_network_log(url_filter='/api/...')` — the bug is often in the response transformation, not the component.

### Specter — full tool index

Every `specter_*` tool, grouped by purpose. The failure mode this list prevents: reaching for `evaluate_js` to hand-roll something that already has a dedicated tool. If a need below sounds like what you have, USE THE NAMED TOOL — it handles framework quirks (React controlled inputs, Next.js routers, redux fiber walks) that hand-rolled JS gets wrong.

**Snapshot + inspect:**
| Tool | Use case |
|---|---|
| `specter_debug_snapshot` | One-shot composite: screenshot + URL + console errors + network errors + page structure. START HERE. |
| `specter_take_screenshot` | PNG of viewport or full page. `selector` arg for element-only screenshot. Read the returned path with the Read tool to view. |
| `specter_get_page_info` | URL + title + readyState. Quick "where am I?". |
| `specter_get_page_structure` | Semantic landmarks tree (nav, main, dialogs, widgets) — better than parsing a screenshot for layout questions. |
| `specter_get_dom_html` | Rendered HTML of `body` or a selector. Inner or outer. |

**Tabs + navigation:**
| Tool | Use case |
|---|---|
| `specter_list_tabs` | All open browser tabs with IDs. Use FIRST to find the right app tab. |
| `specter_connect_to_tab` | Switch Specter's CDP connection to a specific tab. |
| `specter_navigate_to` | Hard URL load (resets state). Use sparingly — prefer `click_element` or `router_navigate`. |
| `specter_router_navigate` | SPA soft navigation (`<a>` click then `location.href` fallback). Preserves Redux/React context. |
| `specter_reload_page` | Reload current tab; `ignore_cache=True` for hard reload. |

**Interaction (each handles the framework quirks evaluate_js can't):**
| Tool | Use case |
|---|---|
| `specter_click_element` | Scrolls into view + fires mousedown→mouseup→click. React-aware. |
| `specter_hover_element` | Synthetic mouseenter+mouseover+mousemove. Reveals hover-only UI. |
| `specter_fill_input` | Type into input/textarea — uses native value setter so React controlled inputs accept it. |
| `specter_select_option` | Pick a `<select>` option by value or visible text. |
| `specter_press_key` | Enter/Escape/Tab/arrows + single chars; supports ctrl/shift/alt/meta modifiers. |
| `specter_set_file_input` | Attach local files to `<input type="file">` via CDP. The ONLY programmatic way; bypasses native-picker restrictions. |

**Scroll + wait:**
| Tool | Use case |
|---|---|
| `specter_scroll_to_element` | Bring an off-screen element into the viewport. Do this before screenshot/click of below-fold content. |
| `specter_scroll_within` | Step-scroll a container (modals, virtualized lists). Reports `atEnd` so you know when to stop. |
| `specter_wait_for_element` | Poll until an element exists + has layout. Use after clicks that trigger lazy load or modals. |
| `specter_wait_for_network_idle` | Wait until no in-flight HTTP requests for `idle_ms`. Use after navigation before screenshot. |

**Logs + errors (buffered automatically — no setup needed):**
| Tool | Use case |
|---|---|
| `specter_get_console_logs` | console.log/warn/error/info with source locations. Filter by `level`, `since`, `limit`. |
| `specter_get_errors` | Unhandled JS exceptions with stack traces. |
| `specter_get_network_log` | All HTTP requests. Filter by `url_filter` substring. |
| `specter_get_network_errors` | Just the 4xx/5xx/network failures. |
| `specter_clear_logs` | Reset all buffers before reproducing a specific bug. |

**React + Redux (works only in dev mode):**
| Tool | Use case |
|---|---|
| `specter_check_react` | Probe what's available (React version, Redux DevTools, Next data). Run before reaching for the deeper tools. |
| `specter_get_component_tree` | Full React fiber tree with props + hooks. Same view as React DevTools. |
| `specter_get_component_at` | "Which component owns this DOM element?" + parent chain. |
| `specter_get_elements_grouped_by_component` | Disambiguates "this selector returns 6 elements" by grouping under their React owner. |
| `specter_get_interactive_elements` | Every clickable/typeable element with a stable selector + role + state. |
| `specter_get_interactive_elements_grouped` | Same, grouped by ARIA landmark + component. Use when the flat list is too long. |
| `specter_get_redux_state` | Read the Redux store via fiber walk. PREFERRED over hand-rolled `evaluate_js` for store reads — walks all fiber roots, handles Next.js multi-root case. |
| `specter_get_redux_actions` | Reports Redux DevTools availability + current state shape. |

**Eval (escape hatch — use the dedicated tools above first):**
| Tool | Use case |
|---|---|
| `specter_evaluate_js` | Run arbitrary JS in the page. Use when no dedicated tool fits — NOT as a first reach. |

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

### Scarlet — full tool index

Every `scarlet_*` tool. Scarlet expects a `features/` folder convention (most React/Next.js); returns cleanly empty on projects that don't fit.

| Tool | Use case |
|---|---|
| `scarlet_analyze_project` | Project overview: framework, TS usage, state lib, test framework, package manager, feature count. Use FIRST to confirm Scarlet applies. |
| `scarlet_scan_features` | List every feature with its current state (has CLAUDE.md? has barrel? counts of components/hooks/slices/api). |
| `scarlet_extract_feature_metadata` | Parse one feature's source with tree-sitter → exports (components, hooks, classes, types, constants) with file paths + line numbers. |
| `scarlet_extract_invariants` | Surface TODOs, FIXME, magic numbers w/ comments, DON'T/NEVER warnings, "intentional"/"deliberate" callouts. Raw material for the gotchas section. |
| `scarlet_list_consumers` | Reverse-dep: which features import from this feature. |
| `scarlet_generate_dep_graph` | Feature → feature dep graph as Mermaid (default) or JSON. Flags deep-imports as tech debt. |
| `scarlet_build_claude_md` | Generate/refresh a feature's CLAUDE.md. Auto sections regenerate; `<!-- BEGIN MANUAL -->` blocks preserved across runs. |
| `scarlet_lint_claude_md` | Check a feature's CLAUDE.md for staleness (Public API drift, missing sections, dead file refs). |
| `scarlet_generate_barrel` | Write `index.{js,ts,tsx}` re-exporting a feature's public surface. Set `write=False` for a dry run. |

## Decision tree — which tool first?

```
Question shape:
├── Exact symbol / known string / single regex
│   └── Grep (or Serena's find_symbol if available)
├── Conceptual codebase question ("how does X work")
│   └── seance_semantic_search (after confirming index exists)
├── Just shipped a UI change → VERIFY it rendered
│   └── specter_debug_snapshot (post-rebuild)
├── Visible-in-browser bug → DEBUG it
│   └── specter_debug_snapshot → drill in
├── Feature structure / dep graph / docs scaffolding
│   └── scarlet_*
└── Cross-file refactor / call-graph navigation
    └── Serena (LSP-based, if available) > grep
```

When in doubt and the project is indexed in Séance, try `seance_semantic_search` first — it has the highest payoff-per-call for the most common case (conceptual question), and a miss is cheap (returns nothing, you fall through to grep).

## Anti-patterns

- **Don't grep when you could semantic-search.** "How does X work" + 8 grep calls + 4 file reads is the failure mode. One `seance_semantic_search` returns the same answer.
- **Don't ship UI changes without a Specter screenshot.** `tsc --noEmit passing` + "the diff looks right" is not verification. Open the tab, screenshot the result, then report done. The user can already see the screen; the AI cannot — Specter closes that gap. Failure mode: shipping a draggable-card change, typechecking, declaring done; user opens the browser and the card is invisible due to a z-index conflict the AI never saw.
- **Don't guess at browser-side state.** If you need to know what `myVar` looks like at runtime, `specter_evaluate_js` it — don't reason from the React source about what state *should* be.
- **Don't ask Scarlet for prose.** It surfaces structure (exports, dep graphs, invariant candidates). Prose comes from the AI reading code with that structure as scaffolding.
- **Don't skip `seance_list_projects` before searching.** A 1-tool-call check beats a 0-result search that wastes a round trip + leaves you unsure if the project is indexed.

## What about `Read`?

`Read` is always available and always cheap when you know the path. The point of these tools isn't to replace `Read` — it's to make `Read` purposeful. Séance tells you *which* files to Read for a conceptual question. Scarlet tells you the *structural shape* before you Read. Specter tells you *runtime behavior* that Read can't show you.
