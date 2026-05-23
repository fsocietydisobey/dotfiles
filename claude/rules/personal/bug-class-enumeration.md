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
