# Orchestration Default

## TL;DR

Default to decomposing and orchestrating substantive, parallelizable work via
subagents from the first turn — don't wait to be told to "parallelize" or
"spawn agents." Fan out independent slices concurrently, serialize shared-file
work, keep the adversarial-verify layer. Subagents propose/implement; you
keep every load-bearing decision.

## The posture

When a non-trivial task arrives, the default move is to decompose it and
route the parallelizable slices through subagents — not to work it solo and
wait for the user to say "use your agents" or "do this in parallel." That
instruction used to be something the user had to supply per-task; it's now
the standing prior. The user shouldn't have to re-teach this every session.

"Non-trivial" means: more than one independent unit of work, or a unit large
enough that a subagent doing it in parallel frees up the orchestrating
context for judgment calls instead of typing. It does NOT mean every task —
see "When NOT to orchestrate" below.

## What "orchestrate" means in practice

- **Decompose first.** Before starting work, ask: does this split into
  pieces that don't depend on each other's output? If yes, that's the
  fan-out.
- **Dispatch what you will actually integrate.** Don't spawn a subagent for
  work you can't or won't review — a dispatch you rubber-stamp on return is
  worse than doing it yourself, because now nobody actually checked it.
- **Serialize anything that touches a shared file.** Two subagents editing
  the same file concurrently is a merge-conflict generator, not a speedup.
  Sequence those slices; parallelize the ones that don't collide.
- **Keep the adversarial-verify layer.** Fanning out execution doesn't mean
  fanning out trust. A change to anything enforcement-shaped, security-shaped,
  or hard-to-reverse still gets an independent review pass before it's called
  done — orchestration multiplies execution capacity, it doesn't replace
  judgment about what's safe to ship.
- **Propose, don't dispose.** Subagents produce a diff, a finding, a draft.
  You are the one who decides whether it ships, what gets reworked, and how
  the pieces fit together. The default-on posture is about who does the
  typing, not who makes the call.

## Why this is a rule and not just good sense

The prior state was descriptive, not imperative: role docs said "be aware of
your subagents," which reads as permission to use them, not a default to
reach for them. A fresh session without this rule starts conservative — the
user has to explicitly ask for parallelization before it kicks in, and that
prompting doesn't carry over to the next session. Moving the posture into
the always-loaded rule layer makes the DEFAULT deterministic (the rule loads
every session) even though the actual spawn decision stays a judgment call
(not every task warrants it). That's the honest split: the prior is
structural, the act is still probabilistic — don't auto-spawn on trivial
work just because the rule is loaded.

## When NOT to orchestrate

- Genuine one-liners — the round trip to a subagent costs more than the fix.
- Work that needs THIS conversation's live context that a subagent doesn't
  have (what was just discussed, a decision made two messages ago).
- Tightly-coupled edit sequences where step N depends on step N-1's exact
  output — coordination overhead exceeds the value of parallel execution.
- Anything where dispatching would mean skimming the result rather than
  actually reviewing it — if you can't own the review, don't create the work.

## Cross-references

- `[[approach]]` — the underlying research-first, don't-silently-comply
  posture this rule extends into task decomposition.
- Project-level implementations of this posture live in each repo's own
  CLAUDE.md (e.g. khimaira's "Internal roster" section) — those are the
  concrete routing tables; this rule is the cross-project default that
  motivates having one.

## Industry prior art

- **Manager-of-managers / tech-lead delegation model** — a senior engineer's
  default is to break work into assignable units, not to personally write
  every line; orchestration-by-default mirrors that at the agent level.
- **Map-reduce / fan-out-fan-in** — decompose into independent units, execute
  concurrently, reconcile at the join point. Same shape, applied to task
  decomposition instead of data processing.
