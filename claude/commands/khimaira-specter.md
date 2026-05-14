# /khimaira-specter — browser debugging via Specter (CDP)

Use the Specter tool family (`mcp__khimaira__specter_*`) to inspect or interact with the browser via the Chrome DevTools Protocol. Specter attaches to a Chromium running with `--remote-debugging-port=9222` and gives you eyes into the page: console, network, screenshots, DOM, React component tree, Redux state, runtime JS.

## Steps

1. **Start with `mcp__khimaira__specter_debug_snapshot`** — one call returns screenshot + page info + console errors + network errors + page structure. This is your baseline; almost any debug request starts here.
2. **Read `$ARGUMENTS`** for the specific intent and drill in:
   - *"check the console / why is there an error"* → `specter_get_console_logs(level='error')` + `specter_get_errors`
   - *"what did the API return for X"* → `specter_get_network_log(url_filter=...)`
   - *"inspect the page / find this element"* → `specter_get_interactive_elements_grouped` or `specter_get_component_tree`
   - *"click / fill / interact"* → `specter_click_element`, `specter_fill_input`, `specter_select_option`
   - *"what does Redux look like"* → `specter_get_redux_state`
   - *"take a screenshot"* → `specter_take_screenshot`
3. **Don't guess at runtime data.** If you need to know what a variable holds at runtime, call `specter_evaluate_js("console.log(JSON.stringify(myVar))")` then `specter_get_console_logs()`. 10 seconds of inspection beats 10 minutes of wrong guesses.
4. **Prefer clicking over URL navigation** for in-app flows. The app's router controls state — `specter_click_element` preserves it; `specter_navigate_to` is a full-page reset and Next.js can strip query params on programmatic navigation.

## Prerequisites

Chromium must be running with `--remote-debugging-port=9222`. If `debug_snapshot` returns a connection error, tell the user to launch their browser with that flag (or use `khimaira dev` which handles it).

## Notes

- Specter is read-mostly + intentional-write. Don't fire-and-forget — explain what you're going to click before clicking.
- Network errors after `wait_for_network_idle` are usually the real bug; don't skip that wait between interaction and inspection.
- For multi-step debugging that hits cross-layer behavior (frontend ↔ backend ↔ db), consider escalating to the `khimaira-deep-debug` subagent which has these tools pre-authorized.
