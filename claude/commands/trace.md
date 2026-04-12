# /trace — Trace a feature's data flow

Trace how data flows through a feature, from API to store to component to DOM. Pass a feature name as the argument.

## Usage

`/trace quotes`
`/trace drawings`

## Steps

1. Call `extract_feature_metadata` on the feature path to get all exports (components, hooks, slices, API endpoints).
2. Call `semantic_search` on Séance with queries like "API endpoint for <feature>", "Redux slice for <feature>", "data fetching in <feature>" to find the data flow entry points.
3. If Specter is connected and the feature is visible in the browser:
   - Call `get_component_at` on a relevant DOM element to find the component and its props.
   - Call `get_redux_state` with relevant state paths.
   - Call `get_network_log(url_filter="/api/v1/<feature>")` to see recent API calls.
4. Present the data flow as a sequence:
   - **API layer:** which endpoints are called, what they return
   - **Store layer:** which slice/RTK Query cache holds the data
   - **Component layer:** which component receives the data as props
   - **DOM layer:** what the user sees
5. Identify any gaps or issues in the flow (missing cache tags, stale data, prop drilling).
