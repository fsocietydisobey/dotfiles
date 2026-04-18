# /create-study-guide

Generate a deep reverse-engineering study guide for a specific feature, bug fix, or architectural pattern that was recently worked on. Matches the style and depth of `shared-docs/joseph/notes/HITL_PAUSE_RESUME.md` — a document someone can read standalone and then open any of the touched files with full context.

Writes to `shared-docs/joseph/notes/<SLUG>.md` by default. Always ask the user the three clarifying questions below before researching.

## Arguments

- `$ARGUMENTS` — topic/feature (e.g., `hitl pause resume`, `digest table separation`, `source manager folders`).

If no arguments provided, ask the user what the study guide should cover.

## Step 1 — Ask the three clarifying questions

Before doing any research, ask **in a single message** (don't drip these out one at a time):

1. **Stack scope** — frontend only / backend only / both? (Default: both — most features span the stack.)
2. **Depth** — deep (full reverse-engineering, ~400 lines, every phase + component + invariant) or shallow (overview only, ~100 lines, just problem + architecture + key files)?
3. **Anchor** — optional: any specific files, commits, or recent dates you want centered? (e.g., "the work from 2026-04-17 through 2026-04-18" or "focus on the changes in `backend/core/agents/nodes/digestion/`")

Wait for answers before proceeding.

## Step 2 — Research

Based on the user's answers, gather material:

### 2a. Semantic search

Call `mcp__seance__semantic_search` with the topic. Use `project="jeevy_portal"`. Read the top 10 results to surface the obvious files.

### 2b. Scoped grep

Grep for distinctive terms from the topic:
- If topic is `hitl pause resume` → grep for `_should_pause`, `abort_digest_hitl_to_paused`, `paused_for_ingest`, `is_resume_entry`
- For a generic topic like `digest table separation` → grep for the exact entity names

### 2c. Git recency

```bash
git -C /home/_3ntropy/work/jeevy_portal log --since='60 days ago' --all --oneline | grep -i '<topic keyword>'
```

For each relevant commit: `git show --stat <sha>` for file lists; `git show <sha>` for the diffs if the commit is small enough to be useful context. Build a chronology: what was added, changed, or removed, and when.

### 2d. Read the files

For each file identified in 2a/2b/2c, read it (or the relevant sections). For backend graphs: read the graph topology file + every node referenced. For frontend features: read the feature's root component + Redux slice + SSE provider if it's event-driven. For migrations: read the migration SQL + the endpoints that consume it.

### 2e. Check for existing docs

```bash
find /home/_3ntropy/work/jeevy_portal/shared-docs/joseph/notes -iname "*<topic-related>*"
```

If a related study guide exists, reference it and focus the new one on what's not covered.

## Step 3 — Produce the study guide

Follow the HITL_PAUSE_RESUME.md structure. Exact section list for **deep mode**:

```
# <Title> — <one-line-tagline>

**Author's note (Joseph, YYYY-MM-DD):** <one-paragraph context: what this is, which branch / commits, why it was worth documenting, who the audience is.>

---

## 1. The problem (or: the feature)

<What was broken or missing before. Symptoms, observed incidents, or "we needed X but had Y." Concrete enough that a reader understands the motivation without prior context.>

---

## 2. Architecture at a glance

<One Mermaid diagram showing the primary flow. Include subgraphs for logical grouping. Use `flowchart LR` or `flowchart TB` — pick what reads better.>

<Below the diagram: 3-5 bullet points naming the key invariants that shape the architecture.>

---

## 3. End-to-end sequence (the walk)

<Optional: a numbered timeline table showing a concrete example run — events, actor columns. Pulls from git log or actual traces when available.>

### Phase-by-phase breakdown

**Phase A — <name>**

File: `<path>`

<What happens here, numbered 1/2/3. Link to specific functions, specific line ranges when known.>

**Phase B — <name>**

<Repeat for each phase.>

---

## 4. Component-by-component reference

### 4.1 `<function or component name>` (`<file path>`)

<What it does, its contract, its writes/emits, why it exists. Include a table if there are multiple state writes or branches.>

### 4.2 `<next thing>`

<...>

---

## 5. Subtle invariants (must-holds)

<Numbered list of rules that, if broken, reproduce one of the original bugs. Each item: the rule, plus a brief "why" that references a specific failure mode.>

---

## 6. Failure modes → fixes (historical)

| Bug | Root cause | Fix |
|---|---|---|
| <symptom> | <cause> | <fix / commit reference> |

<Fill this from git log if the study guide is for a bug fix chain. Skip this section for pure feature docs.>

---

## 7. Testing map

- **Unit:** <test file paths + what they cover>
- **Integration:** <test file paths, or "none yet — candidate: ..." with a concrete suggestion>
- **Operational / manual:** <scripts, repro steps>

---

## 8. Adding a new <similar thing> — checklist

<If the architecture is extensible (e.g. "adding a new HITL gate"), write a numbered checklist for the future person who needs to add one. Omit this section if the architecture isn't meant to be extended.>

---

## 9. Files touched (reference card)

Backend:
- `<path>` — <one-line purpose>
- ...

Frontend:
- `<path>` — <one-line purpose>
- ...

---

## 10. What NOT to do

- Don't <anti-pattern>. <Why it's tempting and what breaks.>
- Don't <another anti-pattern>. <Why.>
```

### Shallow mode

If the user chose shallow, produce only sections 1, 2, 3 (condensed), and 9. Skip components / invariants / failure modes / testing / checklist / what-not. Target ~100 lines total.

## Step 4 — Write the file

Path: `/home/_3ntropy/work/jeevy_portal/shared-docs/joseph/notes/<SLUG>.md`

Slug rules:
- UPPERCASE with underscores (matches the existing convention: `HITL_PAUSE_RESUME.md`, `LANGGRAPH_E2E_STUDY_GUIDE.md`)
- Descriptive, not generic: `HITL_PAUSE_RESUME.md` not `HITL.md`
- Append `_STUDY_GUIDE` if the title would otherwise be ambiguous with a project folder name
- If a file already exists at that path, ask the user whether to overwrite, append, or pick a different slug.

## Step 5 — Report

Print:
- The output path
- A 2-3 sentence summary of what's in the guide (sections covered, notable inclusions like mermaid diagrams / failure tables)
- Suggested follow-ups: *"Consider adding an integration test at `<path>`"*, *"Reference this from `<feature>/CLAUDE.md`"*, etc. Keep suggestions actionable.

## Style conventions (match HITL_PAUSE_RESUME.md)

- **Concrete file paths with line numbers** where meaningful: `backend/api/v1/endpoints/deliverables.py:141`
- **Tables** for anything enumerable: writes, SSE emits, test files, failure modes
- **"Why"** after every rule or invariant — the failure mode that rule prevents
- **Direct voice** — "The subgraph re-enters from START" not "The subgraph may re-enter from START"
- **Dates in ISO format**: `2026-04-18` not `April 18, 2026`
- **Author's note** at the top with Joseph's name and date, explaining scope

## Mermaid diagrams — use liberally

Per the global conventions rule, **use Mermaid diagrams everywhere a flow, state transition, hierarchy, or sequence would otherwise be prose**. Prefer Mermaid over ASCII art and over long paragraphs describing "A calls B then C calls D."

Concrete places to reach for Mermaid in a study guide:

| Situation | Diagram type | Example from HITL_PAUSE_RESUME |
|---|---|---|
| "This is how the pieces fit together" | `flowchart TB` or `flowchart LR` with subgraphs | §2 architecture at a glance |
| "Here's what happens over time, actor by actor" | `sequenceDiagram` | (would replace §3 timeline table in many guides) |
| "This entity moves between these states" | `stateDiagram-v2` | useful for status enums like `paused_for_ingest → verified → ready` |
| "These components depend on / import from these" | `graph TD` or `graph LR` | useful when cross-feature coupling matters |
| "This is the decision tree at a routing point" | `flowchart TD` with diamond decision nodes | rule 0.4 / router logic |

Aim for 2–4 diagrams in a deep guide, 1–2 in a shallow guide. One diagram per major section is a good ceiling. Don't add decorative diagrams — every one should communicate something prose can't as cleanly.

When in doubt: if a paragraph has three or more "and then" / "which calls" / "which writes" phrases, convert it to a sequence or flowchart diagram.

## When to prefer shallow over deep

- The topic was a 1-2 file change
- It was a straightforward feature add, not a bug-fix chain with multiple failure modes
- There's no interesting architectural pattern to reverse-engineer — just normal CRUD
- The user explicitly asked for shallow

## Anti-patterns (don't do these)

- **Don't paraphrase the code.** If the reader has to context-switch to the file anyway, a "loose English translation of what the code does" wastes their time. Add context the code doesn't carry: why it's shaped this way, what breaks if you change it, what the alternatives were.
- **Don't list every file.** The "Files touched" section is a navigation index, not a grep dump. Only include files the reader will actually need to understand the feature.
- **Don't add a section if it would be empty or one-liner.** If there are no testing artifacts, say so and suggest one — don't leave a blank `## 7. Testing map` section.
- **Don't fabricate dates or commit hashes.** If you can't find git evidence, write "2026-04 (approximate)" — don't invent precision.
- **Don't forget to ask the three clarifying questions in step 1.** They shape everything downstream.
