# /khimaira-brainstorm — Closed-loop brainstorm: explore → critique → resolve → update

Brainstorm a topic with khimaira (single Claude call producing divergent generation + self-critique). The file under `brainstorms/` is a **working artifact, not the deliverable**. The deliverable is concrete updates to whatever task spec / IMPLEMENTATION.md / TODO.md / code is in scope. Joseph's repeated complaint: "sometimes brainstorm just adds a ton of material to read" — your job is to do the reading, surface only what's actionable, and propose edits.

## Steps

1. **Resolve topic + context.**
   - **If $ARGUMENTS is non-empty:** use $ARGUMENTS verbatim as the `topic`.
   - **If $ARGUMENTS is empty: just go.** Synthesize a `topic` (one short sentence) from the conversation's overall direction. The slash command is the green light — no clarification preamble.
   - **Bundling rule for `context`:** dump *everything relevant* — Joseph's framing, prior assistant takes, ideas already generated, constraints surfaced, decisions locked, review feedback if any. Long-context models handle this fine. Truncate only if you'd exceed ~50KB.
   - **Identify the target spec(s) if any.** If the conversation is about a specific task (e.g. `tasks/planned/<slug>/IMPLEMENTATION.md`), note the file paths — you'll need them in step 4. Include them in `context` so the brainstorm can reference them.

2. **Call `mcp__khimaira__brainstorm`** with the resolved `topic` / `context` / `cwd`. Returns a file path.

3. **Read the saved file with the Read tool.** This is the brainstorm's full output (divergent ideas + self-critique).

4. **Resolve, don't summarize.** Walk the brainstorm and identify:
   - **Open questions that the brainstorm settled** — ideas that survive the critique pass and are clearly the right direction.
   - **Open questions that need *Joseph's* call** — points where the brainstorm offers options but the choice is a personal preference / strategic call.
   - **Concrete spec deltas** — if a target spec was identified in step 1, draft the actual edits the brainstorm implies. File path + before/after, not just descriptions.
   - **Items to discard** — ideas the critique flagged as fabricated, redundant, or out-of-scope. Don't surface these to Joseph; they're noise.

5. **Surface the resolution, not the brainstorm.** Reply inline with a TIGHT structure:
   ```
   ## What this brainstorm settles
   - <bullet per resolved question>

   ## What needs your call
   - <bullet per open question, with the options>

   ## Proposed spec updates (if applicable)
   - <file>: <one-line summary of the change>
   - <file>: <one-line summary of the change>

   File: <relative path to brainstorm file, in case Joseph wants the full record>
   ```
   Length target: ≤30 lines of inline reply. Joseph's complaint about "ton of material to read" is the failure mode to avoid.

6. **On Joseph's approval, apply the spec updates** via Edit tool. Don't ask again per file — one approval covers the proposed batch.

7. **If Joseph wants the full brainstorm**, the file path is in step 5; he can open it. The auto-open via `xdg-open` (or `KHIMAIRA_OPEN_CMD` if set) also fires from khimaira's side.

## Notes

- **Single Claude call** (~$0.03–0.10, ~60–120s). Used to be parallel Claude + Gemini; Gemini was unreliable (intermittent multi-minute hangs, empty outputs) and the prior-art half rarely earned its keep for design-space brainstorms. `/khimaira-research` stays Gemini-driven for genuine prior-art questions.
- Claude's output already contains both `## Divergent ideas` and `## Critique` sections per the system prompt. The critique pass catches its own fabricated claims and overconfidence — but the session-side resolution in step 4 is a second pass with the conversation context, which catches different things.
- For empty-args invocations, if the conversation is genuinely ambiguous about *what* to brainstorm, ask the user before spending the LLM call. A 5-second clarification beats a $0.10 wrong-topic brainstorm. But err on the side of going if there's a plausible read.
- **Don't follow up with `/khimaira-architect` automatically.** Joseph approves the spec updates from the brainstorm directly; architect is a separate tool for fresh planning, not a chained refinement step.
