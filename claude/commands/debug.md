# /debug — Browser debugging workflow

Run the Specter debugging workflow on the current browser tab.

## Steps

1. Call `list_tabs` to see what's open in the browser.
2. Call `take_screenshot` to capture the current visual state. Read the screenshot to understand what the user sees.
3. Call `get_console_logs(level="error")` and `get_errors` to check for JavaScript exceptions.
4. Call `get_network_errors` to check for failed API calls (4xx/5xx).
5. If React is running (`check_react`), call `get_component_at("main")` to inspect the component tree at the main content area.
6. Summarize findings: what's visually wrong (from screenshot), what errors exist (from console), what API calls failed (from network), what component is rendering (from React).
7. If the cause is identifiable, suggest the fix with specific file paths and line numbers. Use Séance or grep to locate the relevant source code.
