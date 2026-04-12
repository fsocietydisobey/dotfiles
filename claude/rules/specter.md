# Specter (browser debugging)

Specter is an MCP server that connects to a Chromium browser via CDP and gives you direct access to the browser during debugging — console logs, screenshots, React component tree, network activity, and page interaction.

**Prerequisite:** Chromium must be running with `chromium --remote-debugging-port=9222`.

## Debugging workflow

1. **See:** `take_screenshot` — capture what the user sees. Read the PNG to analyze the visual state.
2. **Check errors:** `get_console_logs(level="error")` + `get_errors` — find JS exceptions and console errors with stack traces.
3. **Check network:** `get_network_errors` — find failed API calls (4xx/5xx).
4. **Inspect React:** `get_component_at(selector)` — find which component owns a DOM element, its props, and parent chain. `check_react` first to verify React is available.
5. **Inspect state:** `get_redux_state(path)` — read Redux store (e.g., `auth.session`). Or `evaluate_js` for any runtime state.
6. **Interact:** `get_interactive_elements` to see every button/link/input on the page with labels and selectors. Then `click_element`, `fill_input`, or `select_option` to act.
7. **Wait:** `wait_for_element(selector)` after clicking something that triggers navigation or renders new content.
8. **Verify:** `take_screenshot` again to confirm the fix or see the result of the interaction.

## When to use Specter

- Frontend bugs where the error is in the browser, not the code (wrong props, stale state, failed API calls)
- Visual debugging — "does this look right?" → take a screenshot and check
- Tracing data flow — follow the data from API response → Redux state → component props → rendered DOM
- Interaction testing — click through a flow, fill forms, verify behavior without the user doing it manually

## Quick reference

```
take_screenshot(full_page=False, selector=None)
get_console_logs(level=None, since=None, limit=50)
get_errors(since=None, limit=50)
get_network_errors(since=None, limit=50, url_filter=None)
get_network_log(since=None, limit=50, url_filter=None)
evaluate_js(expression)
get_page_info()
get_dom_html(selector="body", outer=False)
check_react()
get_component_tree(max_depth=15, max_children=50)
get_component_at(selector)
get_redux_state(path="")
get_interactive_elements(role=None)
click_element(selector)
fill_input(selector, value)
select_option(selector, option_value)
wait_for_element(selector, timeout_ms=10000)
list_tabs()
clear_logs()
```
