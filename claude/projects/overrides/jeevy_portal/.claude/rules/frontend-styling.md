# Frontend Styling Rules

Invariants for all CSS, CSS modules, and Tailwind work in `frontend/src/`. These are the non-negotiable parts of the styling system — patterns and examples live in the study guides linked at the bottom.

## Theme variables (colors, surfaces, borders, radii, shadows)

- **Use only theme variables** via `var(--*)` for all colors, backgrounds, borders, radii, shadows, and transitions. The variables are defined in `frontend/src/styles/themes/dark.css`, `light.css`, and `space.css` and imported via `src/styles/globals.css`.
- **No raw hex values** (`#1a1a1a`) or `rgba()` in component CSS for backgrounds, text, or borders. Every color reference must resolve through the theme system so all three themes (dark / light / space) and any future themes work automatically.
- **No "one-off" color variables in component files.** If a color you need doesn't exist yet, add a new variable to **each** theme file in `src/styles/themes/` and document it in `frontend/study-guides/styling/THEME_SYSTEM.md`. Never define it locally in a component's CSS module.
- **Exception:** third-party chart colors (Recharts, etc.) that are not part of the app theme may stay hardcoded.

### Required variable usage by surface

| Surface                   | Variable                                    |
| ------------------------- | ------------------------------------------- |
| Page / shell background   | `var(--bg-deep)`                            |
| Cards, panels, sections   | `var(--bg-surface)` or `var(--bg-elevated)` |
| Hover rows / buttons      | `var(--bg-hover)`                           |
| Active / pressed / select | `var(--bg-active)`                          |
| Modals, dropdowns         | `var(--bg-overlay)`                         |
| Default borders           | `var(--border)`                             |
| Focused / active borders  | `var(--border-active)`                      |
| Main text, headings       | `var(--text-primary)`                       |
| Labels, supporting        | `var(--text-secondary)`                     |
| Placeholders, hints       | `var(--text-muted)`                         |
| Primary button / link     | `var(--primary)`                            |
| Error text / destructive  | `var(--error)` / `var(--error-soft)`        |
| Success / warning / info  | `var(--success)` / `var(--warning)` / `var(--info)` (and `-soft` variants) |

### Radii and shadows

- Use `var(--radius-sm)`, `var(--radius-md)`, `var(--radius-lg)`, `var(--radius-xl)` — never raw `6px` / `8px` / `12px`.
- Use `var(--shadow-sm)`, `var(--shadow-md)`, `var(--shadow-lg)` for elevation; `var(--shadow-glow)` for focus rings.
- Use `var(--transition-fast)` / `var(--transition-base)` / `var(--transition-smooth)` for state changes.

## Breakpoints (Vuetify / Material Design)

**Use only these five breakpoints. Do not invent custom pixel values.**

| Name | Min width | Use for                          |
| ---- | --------- | -------------------------------- |
| `xs` | 0px       | Phones, single-column            |
| `sm` | 600px     | Large phones, small tablets      |
| `md` | 960px     | Large tablet, laptop             |
| `lg` | 1264px    | Desktop                          |
| `xl` | 1904px    | 4k, ultra-wide                   |

- **Mobile-first.** Write base (`xs`) styles first, then add `sm:`, `md:`, `lg:`, `xl:` modifiers for larger screens.
- **Max one breakpoint per decision.** Prefer "show at `md` and up" rather than "hide at `sm` and show at `md`" when they mean the same thing.
- **Existing code may still use `1280px` or `1920px`.** When you touch those media queries, convert to **1264px** and **1904px** to match the Vuetify standard.
- **In CSS:** media queries must use the literal pixel values — CSS does not allow `var()` inside `@media`:
  ```css
  @media (min-width: 600px)  { /* sm */ }
  @media (min-width: 960px)  { /* md */ }
  @media (min-width: 1264px) { /* lg */ }
  @media (min-width: 1904px) { /* xl */ }
  ```
- **In JavaScript** (for `matchMedia`), import from `src/styles/breakpoints.js`: `maxWidthQuery('md')`, `minWidthQuery('lg')`, or `breakpoints.md`. Don't hardcode pixel values.

## Spacing scale (4px-based)

**Use only these values for margin, padding, and gap. No arbitrary pixel values (no `13px`, `27px`).**

| Step | Value | Use for                         |
| ---- | ----- | ------------------------------- |
| 0    | 0     | Reset                           |
| 1    | 4px   | Icon + label gap                |
| 2    | 8px   | Inline spacing                  |
| 3    | 12px  | Small gaps between elements     |
| 4    | 16px  | Default gap between blocks      |
| 5    | 20px  | Section spacing                 |
| 6    | 24px  | Card / layout padding, gutters  |
| 8    | 32px  | Large section spacing           |
| 10   | 40px  | Page section spacing            |
| 12   | 48px  | Major section separation        |
| 16   | 64px  | Hero / large blocks             |

Tailwind's default scale already matches this (`p-2` = 8px, `gap-4` = 16px, etc.). Use the numeric classes; don't use arbitrary values like `p-[13px]`.

## Layout primitives over utility soup

- **Prefer layout components** (`Stack`, `Container`, `Row`, `Grid` in `src/shared/components/`) over long Tailwind utility strings for responsive behavior.
- If the same responsive pattern appears in multiple components, **extract it to a shared component or a small set of utility classes** and reference that — don't copy-paste utility strings.
- When no layout primitive exists for a pattern you need, prefer adding one to `shared/components/` over repeating the utility string in three files.

## Reference (patterns and examples)

These study guides contain patterns and worked examples that expand on the rules above. Read them when you need to implement something, but the rules above are the authoritative invariants:

- **`frontend/study-guides/styling/THEME_SYSTEM.md`** — full variable reference with a by-surface component checklist.
- **`frontend/study-guides/styling/responsive_and_styling_rules.md`** — breakpoint/spacing rationale and AI-assisted styling rules.
- **`frontend/study-guides/styling/compact-card-styling-pattern.md`** — dense/compact modal card layout (3-piece structure, inputs, labels).
- **`frontend/study-guides/styling/ADDING_THEMES.md`** — step-by-step for adding a new theme.
- **`frontend/study-guides/styling/theme-conversion-todo.md`** — CSS files still to convert from hex/rgba to theme variables.
