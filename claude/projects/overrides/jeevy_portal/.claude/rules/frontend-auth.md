# Frontend Auth and Session Rules

Session and permissions in `frontend/src/` live **only** in the Redux store. There is no WorkOS session Context, no `AuthProvider`, and no component-level session fetch. These are non-negotiable — violating them creates auth inconsistencies that are very hard to debug.

## The only place session and permissions live

- **Session:** `state.auth.session` in the Redux store.
- **Permissions:** `state.auth.permissions` in the Redux store.
- **Loading state:** `state.auth.isLoading` in the Redux store.
- **Initial fetch:** handled once by `AuthBootstrap` on app load via `dispatch(fetchSession())`.
- **Provider tree:** `StoreProvider → AuthBootstrap → ToastProvider → children`. Do not add any auth provider between these.

## How to read auth (pick the right hook)

| You need                                  | Use                                                                        |
| ----------------------------------------- | -------------------------------------------------------------------------- |
| Session, loading, or refetch              | `useSession()` from `@/store/hooks`                                        |
| Permission checks (shop module access)    | `useShopPermissions()` from `@/shared/hooks/useShopPermissions`            |
| Raw auth state (selector access)          | `useAppSelector((state) => state.auth)`                                    |
| Check super user                          | `isSuperUser(session)` from `@/shared/utils/permissions`                   |
| Gate UI by permission                     | `<PermissionGate module="X" requireWrite>` from `useShopPermissions`       |

- **Never use `useContext` for session or permissions.** There is no such Context. If you find yourself looking for one, you're in the wrong pattern.
- **Never call `fetch('/api/auth/session')` directly from a component.** The only place that call lives is inside the `fetchSession` thunk, and it's only invoked by `AuthBootstrap` (once on load) or `refetch()` (explicit re-fetch).

## How to write auth

- **Only via Redux dispatch.** The valid actions:
  - `dispatch(setSession(...))` — update session
  - `dispatch(setPermissions(...))` — update permissions
  - `dispatch(setAuthLoading(...))` — update loading flag
  - `dispatch(clearAuth())` — logout
  - `dispatch(fetchSession())` — re-fetch from `/api/auth/session` and update store
- **For refetch from a component:** call `refetch()` returned from `useSession()` — it's already wired to `dispatch(fetchSession())`.
- **Never mutate `state.auth` directly or stash session in local component state.** If a component needs session data, it reads from the hook every render — no snapshots.

## What NOT to do

- **Don't roll your own auth.** No custom session hooks, no React Context for auth, no local fetches to `/api/auth/session`.
- **Don't import from `@workos-inc/*` for session handling in the app runtime.** The WorkOS SDK is used only at the Next.js proxy boundary (in `app/api/` proxy routes). Inside `frontend/src/`, session comes from Redux.
- **Don't guard routes at the UI layer only.** Route-level protection belongs in middleware or layout bootstrap. A missing frontend button is not access control — backend enforces auth too.
- **Don't pass session as a prop through component trees.** Any component that needs session calls `useSession()` directly. Prop-drilling auth creates stale data and forces re-renders in the wrong places.

## Common patterns

### Checking a permission before rendering a button

```jsx
import { PermissionGate } from "@/shared/hooks/useShopPermissions";

<PermissionGate module="project_notes" requireWrite>
  <button onClick={handleAddNote}>Add Note</button>
</PermissionGate>;
```

### Reading session in a component

```jsx
import { useSession } from "@/store/hooks";

function MyComponent() {
  const { session, isLoading, isAuthenticated, refetch } = useSession();
  if (isLoading) return <Spinner />;
  if (!isAuthenticated) return <LoggedOut />;
  return <div>Hello, {session.user.firstName}</div>;
}
```

### Forcing a session refetch after a mutation

```jsx
const { refetch } = useSession();
await saveProfile(updatedData);
await refetch(); // pulls fresh session into Redux
```

## Reference (patterns and examples)

- **`frontend/study-guides/auth/auth_rtk_pattern.md`** — full before/after walkthrough of the Redux-only pattern and why the old Context approach was removed.
- **`frontend/study-guides/auth/rtk_auth_how_to_use.md`** — hook usage cheatsheet with more examples.
- **`frontend/study-guides/auth/redux_store_js.md`** — store structure, auth slice, thunks.
- Canonical design doc: `docs/design-guides/AUTH_RTK_PATTERN.md`.
