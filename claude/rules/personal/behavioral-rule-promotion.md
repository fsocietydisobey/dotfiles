# Behavioral-Rule Promotion to Structural

## TL;DR

When a behavioral discipline rule keeps being violated (observed ≥2 times),
promote it to STRUCTURAL via the 3-layer template: role-doc section +
Themis hint (severity=warn) + lint test guarding the role-doc text.
Behavioral rules drift; structural rules don't. Observed across 6+ gaps
in the 2026-05-25/2026-05-26 session.

## Why this exists

Behavioral discipline rules ("master should consult architect before
asking user", "intake should fan out specialists when implementer hits
a research blocker") work for a while, then drift. Joseph hits the same
failure mode twice — once is bad luck, twice is a class. The discipline
needs structural enforcement at that point.

## The 3-layer template

For each behavioral rule worth promoting:

1. **Role-doc section** (`packages/khimaira/src/khimaira/roles/<role>.md`)
   — explicit subsection naming the rule + trigger conditions + correct
   behavior + worked example from the violating incident. Markdown text;
   loads every session. Catches the rule by raising awareness at the
   moment of decision.

2. **Themis hint rule** (`packages/themis/src/themis/rules/<role>.yaml`,
   severity=`warn`) — detects the violation pattern at tool-call time
   via condition function. Doesn't block; nudges. Catches drift when
   the role-doc text didn't pre-empt it. Some rules can't be structurally
   enforced (content-pattern matching is fragile); skip this layer when
   detection isn't tractable.

3. **Lint test** (`packages/khimaira/tests/test_role_convention_lint.py`)
   — asserts the role-doc text + Themis rule are present. Catches silent
   regression (someone edits the doc and accidentally removes the rule).

## Examples observed (2026-05-25 / 2026-05-26)

Behavioral rules promoted to structural in one session:

1. **silent-sessions** — daemon-side substrate fix + master-side observability convention + lint guards
2. **master-serializes-parallel-work** — pre-dispatch independence checkpoint in master.md + IN-MASTER-6 Themis hint + lint tests
3. **master-defaults-to-user** — pre-AskUserQuestion routing table in master.md + IN-MASTER-4 question-text-shape condition + lint tests
4. **worktree-stranding** — Step 7 Reconcile in master.md + merge_intent in agent.md + IN-AGENT-4 Themis hint + lint tests
5. **specter selector-scope-falsified** — class reversal via Phase A audit (see bug-class-enumeration.md case study 2); Phase B fix pending mechanism clarification
6. **idle-state silent-treatment** — Stay-oriented section in master.md + Status translation in intake.md + status template + lint tests
7. **agent-skip-BEGIN-gate** (META-IRONIC) — agent-2 jumped BEGIN gate on the task codifying BEGIN-gate scope. Caught + tracked but fix would require Themis on chat_task_update from agent before master's chat_task_signal_start. Deferred Cat 2 if recurs.
8. **intake-skip-master-mediation** (IMMEDIATE RECURRENCE) — intake-1 dispatched mnemosyne distiller restore directly to agent-3 (msg-c27d2bb49268), bypassing master's chat_task_create + BEGIN gate. Happened within minutes of BEGIN-gate scope landing in 9ba8b95. Confirms role-doc-only enforcement insufficient for intake; Themis structural enforcement candidate Cat 2.

## When NOT to promote

- Single observed violation — not yet a pattern; observe-before-fix
- Rule is too context-sensitive to structurally enforce (e.g. "use
  good judgment on naming") — leave behavioral
- Themis detection would require fragile content-pattern matching
  (skip layer 2; rely on role-doc + lint only)

## Cross-references

- [[bug-class-enumeration]] — class-level fix discipline; this rule
  promotes behavioral classes to structural form
- engineering rules — general engineering discipline; this rule
  applies specifically to roster-coordination behavioral rules

## Industry prior art

- **Promoting team conventions to lint rules** (eslint, ruff,
  pre-commit hooks) — same pattern at codebase scale
- **Behavioral interview rubrics → structured competency frameworks**
  in hiring (Netflix, Google) — same shape outside engineering
