# /debug — Browser debugging workflow

Run the Specter debugging workflow on the current browser tab.

## Steps

1. Call `list_tabs` to see what's open. Pick the app tab (NOT `pipeline-tracer.html`, NOT `devtools://`). Call `connect_to_tab(id)` if needed.
2. Call `debug_snapshot` — this returns screenshot + page info + console errors + network errors + page structure in one call.
3. Read the screenshot to understand the visual state.
4. Analyze the page structure to understand what sections exist and their state (selected tabs, expanded/collapsed panels).
5. Check the console errors and network errors for root causes.
6. If more context is needed:
   - `get_component_at("main")` to see the React component and its props
   - `get_redux_state("relevant.path")` to check the store
   - `hover_element` on containers to reveal hidden action buttons
7. Summarize findings: what's visually wrong, what errors exist, what API calls failed, what component is rendering.
8. If the cause is identifiable, suggest the fix with specific file paths and line numbers. Use Séance or grep to locate the relevant source code.
