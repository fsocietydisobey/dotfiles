# Bug-Class Enumeration

## TL;DR

For any bug consult framed as "fix THIS instance", the architect's FIRST output must
be a bug-class enumeration: abstract the class, list ALL known code paths, mark each
BROKEN/SAFE/UNKNOWN. Then design fixes that close the CLASS, not the instance. Master
requests enumeration first; reviews verify class coverage, not just the diff.

## Why this exists

Silent-tab-mutation in Specter required 4 commits over 2 days (ba7bd89, b853250,
258d341, plus test isolation). Each fixed only the surface visible at consult time.
The root cause: architect was asked to fix an instance, not enumerate the class. Critic
+ verifier are diff-reviewers — they verify the submitted fix but don't enumerate
adjacent broken paths. Class-level analysis must happen before fix design.

**Anti-pattern this rule prevents:** whack-a-mole debugging — fixing one surface,
shipping, finding another surface, shipping again. Each fix addresses the symptom
visible at consult time; the class is never closed.

## The template

When receiving a bug consult, architect's FIRST response output (before fix design):

```
Bug class: [one-line abstract statement of the CLASS — not the specific instance]

Known code paths in this class:
1. [path] — status: [BROKEN / SAFE / UNKNOWN] — [one-line explanation]
2. [path] — status: [BROKEN / SAFE / UNKNOWN] — [one-line explanation]
...

Coverage decision:
  [fix all BROKEN paths in one task]
  OR [fix path X now; leave Y as deliberate technical debt because <reason>]
  OR [declare class scope X-Y-Z; document UNKNOWN paths for follow-up audit]

Test verification of CLASS (not path):
  [how does a single test — or invariant check — catch any future regression
   of this class, regardless of which specific path it enters through?]
```

ONLY after master confirms the enumeration + coverage decision should the architect
design the fix spec.

## Worked example — Specter silent-tab-mutation

**Bug class abstract:** Any code path that ends with Specter's connected target being
something other than what the calling agent explicitly chose.

**Known paths:**
1. `connect(target_id=None)` auto-pick — status: BROKEN (picks targets[0], not agent choice)
2. Stale `_last_target_id` reconnect (b853250) — status: WAS BROKEN, fixed
3. `connect(target_id=X)` where X was MRU-picked by integration test caller — status: BROKEN (caller inherited auto-pick pattern)
4. `Target.createTarget` — status: SAFE (agent explicitly requested new tab)
5. CDP race: attaching to wrong target after navigation — status: UNKNOWN
6. `_force_reconnect()` — status: WAS BROKEN, fixed in b853250

**Coverage decision:** Fix all 3 BROKEN paths in one enumeration task. Flag UNKNOWN
for follow-up audit.

**Test verification of class:** One integration test asserting "after any Specter
call sequence, `_connection._connected_target.id == the_id_the_agent_passed_to_connect_to_tab`"
would have caught all 3 broken paths. Without a class-level invariant test, path-by-path
fixes can pass individually while leaving the class open.

**What actually happened:** 4 separate consult-fix cycles, each closing one visible
path. Total cost: ~2 days vs ~2 hours with upfront enumeration.

## When to apply this protocol

- Any bug consult where the fix description is "when X happens, Y breaks" — the
  "when X happens" is the path, not the class. Ask: what's the general condition?
- Any bug where the phrase "and also" appears in the diagnosis (multiple surfaces
  already visible)
- Any security fix where a class of vulnerabilities is suspected
- Any time critic or verifier report a "worth-noting" adjacent to the bug being fixed

**When NOT to apply:** single-surface, clearly bounded bugs where the path IS the
class (e.g., off-by-one in a specific calculation with no related paths).

## Evidence quality (audit-grade vs inspection-grade)

Every BROKEN / SAFE / UNKNOWN classification carries an implicit EVIDENCE QUALITY:

- **Audit-grade:** the architect (or implementer) ran the code under test and OBSERVED the behavior. The classification is empirical.
- **Inspection-grade:** the architect read source / comments and HYPOTHESIZED the behavior. The classification is theoretical until tested.

**Default:** UNKNOWN for any path the architect did not live-test. Inspection alone is NOT sufficient evidence to classify BROKEN or SAFE — code comments can mislead (today's Specter case study 2), runtime behavior can diverge from documented intent, framework / library behavior can change between versions.

**When inspection-grade is acceptable:**
- The code path is small + unambiguous (one-line function, no side effects)
- The hypothesis is corroborated by recent test runs (architect cites `git log -p` evidence)
- The classification is SAFE based on absence-of-mechanism (e.g. "this tool doesn't resolve DOM elements at all, so render-state doesn't apply")

**When audit-grade is mandatory:**
- Any BROKEN classification based primarily on code-comment interpretation
- Any path involving CDP / browser / framework internals (their behavior is documentation-vs-runtime divergent)
- Any path where the architect's confidence is "this should be X" rather than "I tested this and observed X"

Tag your classifications with `[audit-grade]` or `[inspection-grade]` when ambiguity matters. Default UNKNOWN means inspection-grade was attempted but not sufficient.

## Error-string anti-pattern

When the visible bug symptom is an error string ("Object id doesn't reference a Node", "ECONNREFUSED", "Element not found"), enumeration must list EVERY code path that could produce that error — not just the most-plausible one.

**The trap:** architect anchors on the first plausible mechanism for the error string ("objectId fails on hidden elements") and builds the class around that hypothesis. Other paths that produce the SAME error string get collapsed into the same class. The fix targets the wrong mechanism; sibling failure modes remain BROKEN.

**Today's Specter case study (May 2026):** "Object id doesn't reference a Node" was produced by selector-scope failure (shadow DOM / iframe — DOM.querySelector returns null → JS injection fails with that error), NOT by objectId-vs-backendNodeId resolution strategy (architect's anchor hypothesis). Audit-grade testing falsified the resolution-strategy class. Without audit-first discipline, the wrong fix would have shipped.

**Discipline:** for any error-string anchored consult, enumeration must include a section listing EVERY mechanism that produces that error in the relevant subsystem. Audit-first becomes mandatory for any UNKNOWN producer.

## Audit-first threshold (when two-phase becomes mandatory)

The Specter case study (commit msg-825a1cab2707) showed two-phase audit-first preventing a wrong-direction fix. Articulating when two-phase becomes MANDATORY:

**Two-phase audit-first MANDATORY when:**
- UNKNOWN classifications dominate (≥50% of enumerated paths)
- Any BROKEN classification is inspection-grade (not audit-grade)
- The bug symptom is an error string (per anti-pattern above)
- The fix path crosses subsystem boundaries (frontend↔backend↔CDP↔OS)

**Two-phase audit-first OPTIONAL (single-phase fix acceptable) when:**
- All paths are SAFE / BROKEN at audit-grade evidence
- Fix is purely within a known-tested code path
- Architect cites recent test runs that confirm the mechanism

When mandatory, the brief structure is:
- **Phase A**: audit deliverables only — read code, run tests, post audit table to chat
- **Phase B**: master gates on audit findings — confirms scope before fix dispatch
- **Phase C**: class-invariant test against audit-confirmed mechanism

See Specter case study 2 (below) for a concrete two-phase example where audit reversed architect's enumeration.

## Case study 2 — Specter selector-scope reversal (2026-05-26)

**Architect's first-cut enumeration (msg-c264c1012469):**
- Class: "objectId-based CDP resolution fails on non-default render states (hidden, detached, virtualized, shadow-rooted)"
- Evidence: comment inspection at packages/specter/src/specter/browser/interact.py:769 ("objectId skips the node-ID lookup dance")
- Classifications: set_file_input BROKEN (inspection-grade), others UNKNOWN

**Audit phase (Phase A, msg-ef2020b5f1cc):**
- Live tested CSS-hidden variants (display:none, visibility:hidden, opacity:0, off-screen, hidden attribute) — ALL PASSED for set_file_input
- Tested shadow DOM + iframe — ALL FAILED across all interaction tools
- Architect's class FALSIFIED — the objectId-vs-backendNodeId distinction is NOT the bug; the bug is selector-scope (DOM.querySelector not piercing shadow/iframe boundaries)

**Refined class (msg-43f1fe10bd01):** "All Specter interaction tools using `document.querySelector` silently return 'element not found' for elements inside shadow DOM or iframe contexts. Failure is selector scope, not resolution strategy."

**Lessons:**
1. Comment inspection ("code says X") ≠ runtime behavior ("code does X under test") — see § Evidence quality
2. Error-string anchoring collapsed multiple producers into one wrong hypothesis — see § Error-string anti-pattern
3. Two-phase audit-first PREVENTED shipping a wrong-direction fix — see § Audit-first threshold

The audit-first discipline worked exactly as designed. Phase A's reversal isn't a discipline failure — it's the discipline's success. Architect's wrong enumeration was caught before agent shipped code.

## Industry prior art

- **Fault Tree Analysis (FTA)** — aerospace/safety engineering (NASA, IEC 61025):
  enumerate all failure paths in a fault tree before designing mitigations.
- **Microsoft Banned Functions pattern** — explicit class-level discipline
  (`strcpy` → `strcpy_s`): the fix is not "patch this strcpy" but "ban the class,
  fix every instance."
- **Toyota 5 Whys** — root-cause family: ask "why" until the root class surfaces,
  not the proximate cause.

## Cross-references

- [[approach]] — "Research & thoroughness": understand the full picture before changing
- [[master]] (khimaira role): architect-consult section for requesting enumeration
