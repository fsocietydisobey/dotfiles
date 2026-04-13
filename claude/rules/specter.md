# Specter (browser debugging)

Specter is an MCP server that connects to a Chromium browser via CDP and gives you direct access to the browser during debugging — console logs, screenshots, React component tree, network activity, and page interaction.

**Prerequisite:** Chromium must be running with `chromium --remote-debugging-port=9222`.

## Debugging workflow

0. **Connect to the right tab:** Call `list_tabs()` to see all open tabs. Pick the app tab — NOT `pipeline-tracer.html` (that's a separate debugger), NOT `devtools://` URLs. Call `connect_to_tab(id)` to switch. Do this on first use or when you're unsure which tab you're on.
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

## When to use Specter

- Frontend bugs where the error is in the browser, not the code (wrong props, stale state, failed API calls)
- Visual debugging — "does this look right?" → take a screenshot and check
- Tracing data flow — follow the data from API response → Redux state → component props → rendered DOM
- Interaction testing — click through a flow, fill forms, verify behavior without the user doing it manually

## Effective patterns

### Start with `debug_snapshot` instead of 5 separate calls
`debug_snapshot` returns screenshot + page info + console errors + network errors + page structure in one call. Use this as the starting point for any debugging session instead of calling each tool separately.

### Use `get_page_structure` before interacting
Before clicking anything, call `get_page_structure` to understand the layout — what sections exist, which tab is selected, what's expanded/collapsed. This prevents clicking the wrong thing because you didn't know the context.

### Hover before looking for action buttons
Many UI elements (table row actions, edit icons, dropdown triggers) only appear on hover. If `get_interactive_elements` doesn't show what you expect, `hover_element` on the parent container first, then call `get_interactive_elements` again.

### Navigate by clicking, not by URL
To navigate the app, use `get_interactive_elements` to find links/buttons, then `click_element` to click them — the same way a user would. Do NOT try to manipulate URLs programmatically. The app's router controls navigation and will strip/rewrite URLs set externally.

### Wait for network after actions
After `click_element`, `navigate_to`, or `reload_page`, call `wait_for_network_idle()` before taking a screenshot. Otherwise you'll capture loading spinners instead of the final state.

### Use `press_key` for form completion
After `fill_input`, use `press_key("Enter")` to submit. Use `press_key("Escape")` to close modals/dialogs. Use `press_key("Tab")` to move between form fields.

### Keyboard for dropdowns
Custom dropdowns (not native `<select>`) often need: `click_element` to open → `press_key("ArrowDown")` to navigate → `press_key("Enter")` to select.

### Navigation is clicking, not URL manipulation
The app's router controls the URL. Don't try to set it programmatically. To navigate: `get_interactive_elements(role="link")` to find links, then `click_element(selector)` to click one. Wait with `wait_for_network_idle()` after.

## Debugging anti-patterns — DON'T DO THESE

### Don't guess at data shapes — inspect them
When debugging data issues (wrong props, missing fields, snake_case vs camelCase), **never guess**. Use `evaluate_js` to inject a console.log and inspect the actual runtime data:
```
evaluate_js("console.log('PROPS:', JSON.stringify(document.querySelector('.my-component').__reactFiber$?.memoizedProps, null, 2))")
```
Then call `get_console_logs` to read the output. 10 seconds of inspection saves 10 minutes of wrong guesses.

### Don't take screenshots to verify data — check the data directly
If the question is "does this component have the right data?", don't take a screenshot and try to read pixel values. Use `evaluate_js` or `get_component_at` to check the actual props and state.

### Don't skip console logs when debugging
Before fixing anything, ALWAYS check `get_console_logs(level="error")` and `get_errors`. The answer is often already in the console. A stack trace pointing to the exact line is worth more than any amount of code-reading.

### Don't guess at API response shapes — check the network
When debugging "the data is wrong after an API call", use `get_network_log(url_filter="/api/v1/...")` to see the actual request/response. If the status is 200 but the data is wrong, the bug is in the response transformation, not the component.

### Inject diagnostic logs instead of modifying code
When you need to understand what's happening inside a function at runtime, use `evaluate_js` to inject temporary `console.log` statements via monkey-patching, NOT by editing the source file. Read them back with `get_console_logs`. This is faster and doesn't require a reload.

## Quick reference

```
# Compound
debug_snapshot()

# Page understanding
get_page_structure()
get_page_info()
get_dom_html(selector="body", outer=False)
take_screenshot(full_page=False, selector=None)

# Console & network
get_console_logs(level=None, since=None, limit=50)
get_errors(since=None, limit=50)
get_network_errors(since=None, limit=50, url_filter=None)
get_network_log(since=None, limit=50, url_filter=None)

# React & Redux
check_react()
get_component_tree(max_depth=15, max_children=50)
get_component_at(selector)
get_redux_state(path="")
get_redux_actions()

# Interaction
get_interactive_elements(role=None)
hover_element(selector)
click_element(selector)
fill_input(selector, value)
select_option(selector, option_value)
press_key(key, modifiers=None, selector=None)

# Navigation & waiting (navigate by clicking links, not by URL)
reload_page(ignore_cache=False)
wait_for_element(selector, timeout_ms=10000)
wait_for_network_idle(idle_ms=500, timeout_ms=10000)

# Runtime
evaluate_js(expression)

# Tab management
list_tabs()
connect_to_tab(tab_id)
clear_logs()
```
