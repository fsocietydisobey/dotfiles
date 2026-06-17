# /khimaira-distill-bugs [bug description] — capture an escaped bug into the seam corpus

Capture a bug that **passed green tests but broke live** into the escaped-bugs corpus — the
labeled dataset a future learner trains on. Each entry maps
`(code-shape + mock-assumption) → seam-class → catching-test-pattern`. The training signal
is the **seam** the green test was blind to.

This is the **capture** stage of the escaped-bugs flywheel (Phase 1): it appends the
structured entry to the corpus file AND distills it into mnemosyne for retrieval, so future
sessions (and eventually a fine-tuned seam-predictor) get it. Companion to `/khimaira-distill`
(domain knowledge) — this one is specifically for *test-blind-spot* knowledge.

## When to use

- Right after a live test / real-use failure reveals a bug the unit suite passed clean.
- During a post-mortem of any "green CI, broken in prod" incident.
- NOT for ordinary bugs the tests *should* have caught and a normal test fixes — this corpus
  is specifically for **seam escapes** (the test mocked the exact boundary where the bug lived).

## Usage

```
/khimaira-distill-bugs
/khimaira-distill-bugs "created project → job node born ghost; deliverables shell event has no edge_derivations..."
```

`$ARGUMENTS` = free-text description of the escaped bug (optional). If empty, elicit the
fields interactively in step 3.

## Steps

**1. Resolve session + project + corpus file**

- Session id: from the `🆔 khimaira session_id` SessionStart block (or `session_list()`).
- Project: run the khimaira venv —
  ```bash
  /home/_3ntropy/dev/khimaira/.venv/bin/python3 -c "
  from khimaira.hooks.session_end_utils import detect_project
  print(detect_project('CWD_HERE'))"
  ```
- **Corpus file** (default convention): `<project_root>/shared-docs/ESCAPED-BUGS-LOG.md`.
  - jeevy: `/home/_3ntropy/work/jeevy_portal/shared-docs/ESCAPED-BUGS-LOG.md`
  - If it doesn't exist, offer to create it with the standard header + the `## 4. Schema for
    future entries` block (copy the shape from the jeevy corpus) before appending.

**2. Classify the seam-class**

Map the escape to ONE of the seam-class vocabulary (extend if a genuinely new class appears):
`entry-path` · `producer→event-payload` · `producer-mechanism` · `mock-vs-schema` ·
`SQL-logic` · `environment-config` · `contract` · `frontend-render`.

Heuristic — what did the test mock that diverged from reality?
| The test mocked… | → seam-class | → catching-test layer |
|---|---|---|
| a different entry event than real creation emits | `entry-path` | L1 real-producer→projector |
| the event dict (injected a field the real producer omits) | `producer→event-payload` | L1 |
| the delete/write mechanism (called the handler directly / hard vs soft) | `producer-mechanism` | L1 (real chokepoint) |
| a column/row shape (dict literal ≠ real schema) | `mock-vs-schema` | L3 schema-contract vs information_schema |
| the DB (so view/CTE/SQL logic never ran) | `SQL-logic` | L2 real-DB integration |
| nothing — env/container/proxy/bucket only fails live | `environment-config` | L4 Specter-in-CI |
| an integration test that **skipped** (wrong driver / missing fixture) | `environment-config · RECURSIVE` | **L0 assert-it-runs** (executed>0, not just failures==0) |

**3. Extract the 5 audit-grade fields** (from `$ARGUMENTS` or by eliciting)

```
### <bug-slug> [<seam-class>]
- **Symptom (live):** the observed BEHAVIOR in real use (not the stack trace)
- **Root-cause (audit-grade):** the specific mechanism — NAME the function / column / value / event
- **Why the test missed it:** the SPECIFIC mock false-assumption (what it stubbed that diverged from reality)
- **Catching-test:** the real test that exercises the seam + [ADDED <task-id> | FORWARD]
```

**AUDIT-GRADE discipline (load-bearing):** the root-cause must name the concrete
function/column/value/event — not "the handler was wrong." If the description is
inspection-grade (a hypothesis, not observed), tag it `[evidence: inspection-grade]` and
flag that it needs live confirmation. A vague entry trains the learner on noise.

**L0 reminder:** if the catching-test is an integration test, the entry MUST note it was
verified to **EXECUTE** (not skip) — a skipped test is green and re-escapes. "N passed, 1
skipped" is not coverage.

**4. Append to the corpus** (atomic)

Insert the formatted block into `## 2. Escaped bugs` of the corpus file (write to `.tmp`,
rename). Don't disturb the meta-class / forward-strategy / schema sections.

**5. Store the structured pair in mnemosyne (DIRECT — not Haiku-distilled)**

The corpus row IS the training/retrieval example, and it's already curated — so store it
**directly** via `store.append`, NOT `distill()`. `distill()` re-runs a Haiku distiller that
would mangle the precise `situation → seam-class + catching-test` signal the fine-tune needs.
Store the pair as `(instruction = the situation, response = seam-class + catching-test)`:
```bash
/home/_3ntropy/dev/ai-lab/mnemosyne/.venv/bin/python3 - <<'PYEOF'
from mnemosyne import store
rec_id = store.append(
    domain="escaped-bugs:PROJECT_HERE",
    instruction=(
        "Escaped bug — green tests, broke live. "
        "Symptom: SYMPTOM_HERE. "
        "The test mocked: MOCK_ASSUMPTION_HERE (code-shape: CODE_SHAPE_HERE). "
        "What seam-class is this and what catching-test closes it?"
    ),
    response=(
        "Seam-class: SEAM_CLASS_HERE. "
        "Catching-test: L<n> — CATCHING_TEST_PATTERN_HERE."
    ),
    source_session="SESSION_NAME_HERE",
)
print("stored", rec_id)
PYEOF
```
This lands in `~/dev/ai-lab/mnemosyne/data/escaped-bugs:<project>.jsonl` (append-only). It is
both retrieval-ready (Phase 1) and fine-tune-ready (Phase 3 reads the same store). Fail-open:
if the write fails, the corpus-file append (step 4) still succeeded — note it.

**6. Report + smoke-verify**

```
🐛 escaped bug captured → <bug-slug> [<seam-class>]
   corpus: <corpus-file> (+1 entry)
   mnemosyne: escaped-bugs:<project> — N pairs
   catching-test: <ADDED task-id | FORWARD>  (L<n> seam layer)
```
- Verify the corpus file grew: `grep -c '^### ' <corpus-file>`.
- If FORWARD (catching-test not yet written), suggest: "this seam has no live test yet —
  want me to draft the L<n> catching-test, or hand to the roster?"

## Notes

- **The flywheel:** capture (this command) → retrieve (Séance/mnemosyne over the corpus at
  review time) → enforce (Themis seam-detectors + the L0 assert-it-runs gate) → gate
  (verifier consults the corpus before SHIP) → verify-live (Specter-in-CI) → learn (mnemosyne
  fine-tune once the corpus is large enough). This command feeds them all.
- **Don't fine-tune yet.** At a handful of entries, retrieval beats training. The corpus must
  reach dozens-to-hundreds of audit-grade entries before a seam-predictor fine-tune is worth
  it — this command is how it gets there.
- **The corpus's own meta-lesson:** a mechanism that silently no-ops is worse than none (the
  skipped test that read green). Every entry's catching-test must be verified to FIRE.
- Cross-project: defaults to the cwd project's `shared-docs/ESCAPED-BUGS-LOG.md`; the same
  command works for khimaira's own escapes (`escaped-bugs:khimaira`).
