# /khimaira-recall-bugs [diff | test-file | description] — surface relevant escaped-bug seams

The **recall** side of the escaped-bugs flywheel (companion to `/khimaira-distill-bugs`). Given
a code change or a test you're about to write/review, retrieve the most-similar past escapes
from the corpus and surface their **seam-class + catching-test pattern** — so you add the real
test BEFORE the bug ships, not after a live failure teaches you.

Use it: at test-write time, in code review, and — wired into the gatekeeper role (lean; the
legacy verifier it absorbs) — before any SHIP verdict on a change that touches a node-bearing
/ data-flow / DB / env surface.

## Usage

```
/khimaira-recall-bugs                         # uses the current diff (git diff)
/khimaira-recall-bugs path/to/test_foo.py     # recall against a specific test/source file
/khimaira-recall-bugs "soft-deleting a project row via is_deleted=true"   # free-text
```

## Steps

**1. Resolve project + the query text**

- Project: `detect_project(cwd)` (khimaira venv) → domain `escaped-bugs:<project>`.
- Query text:
  - empty → `git diff` (staged + unstaged) in cwd; if huge, the changed file list + hunks.
  - a path → read that file.
  - free-text → use verbatim.

**2. Load the corpus**

Read BOTH sources (corpus markdown is human-curated; the store is the machine index):
- `<project_root>/shared-docs/ESCAPED-BUGS-LOG.md` — the structured entries.
- `~/dev/ai-lab/mnemosyne/data/escaped-bugs:<project>.jsonl` — the stored pairs:
  ```bash
  /home/_3ntropy/dev/ai-lab/mnemosyne/.venv/bin/python3 -c "
  from mnemosyne import store
  import json
  for r in store.load('escaped-bugs:PROJECT_HERE'):
      print(json.dumps({'instruction': r['instruction'], 'response': r['response']}))"
  ```

**3. Match (scale-appropriate)**

- **Small corpus (≲ a few dozen):** read all entries; you (the model) judge which seam-classes
  the query touches by the heuristic — does the change/test involve: a producer event or the
  mutate chokepoint (`producer-mechanism` / `producer→event-payload`), a column/row shape or a
  mock dict literal (`mock-vs-schema`), DB/view/CTE/SQL (`SQL-logic`), an entry surface that
  differs from what tests fire (`entry-path`), env/container/proxy/bucket (`environment-config`),
  or an integration test that might skip (`L0 assert-it-runs`)? Cite the matching entries.
- **Larger corpus:** semantic-search it via Séance (`seance_semantic_search`) or the mnemosyne
  oracle (`mnemosyne_ask(question, project=...)`) over the escaped-bugs domain; rank by similarity.

**4. Report — actionable, not just "here are some bugs"**

```
🔍 seam recall for <query> — escaped-bugs:<project>

⚠️ Touches seam(s): <seam-class>[, <seam-class>]
Most similar past escapes:
  • <slug> [<seam-class>] — <one-line why it escaped> → catching-test: L<n> <pattern>
  • ...

Recommended catching-tests BEFORE this ships:
  - L<n>: <concrete test to add for THIS change>

⛔ if no seam matches: "No close escaped-bug match. Still verify integration seams
   (producer→projector, real-DB SQL, schema-contract, env) aren't mocked-past."
```

## Notes

- **No match ≠ safe.** A small corpus has blind spots; absence of a match is not coverage.
  Always fall through to the generic seam checklist (L1–L4 + L0).
- This is the read primitive the **gatekeeper gate** uses (lean; legacy: verifier gate): a
  SHIP verdict on a seam-touching change should be preceded by a recall + a named
  catching-test (see gatekeeper.md / legacy verifier.md).
- Pairs with `/khimaira-distill-bugs` (capture). Capture grows the corpus; recall spends it.
- The corpus's meta-lesson applies to recall too: if you recommend a catching-test, it must be
  one that EXECUTES (not a skip-guarded integration test that silently no-ops).
