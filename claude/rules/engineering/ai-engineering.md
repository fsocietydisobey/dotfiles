# AI Engineering

## TL;DR

The LLM is a bounded perception component, not the system. Cross the boundary once — unstructured → structured → code — and never let the model past it: it turns messy input into a validated schema; every load-bearing decision on that structured data is deterministic code. Resolve/match deterministic-first (exact → algorithmic fuzzy → LLM residual, human-gated). Propose, don't dispose.

## The core boundary: unstructured → structured → code

- **The one invariant.** An LLM's job is to turn *unstructured* input (a PDF, a drawing, a messy query, raw logs) into *structured* data conforming to a strict schema. Once data is structured, the LLM is done — every decision, match, route, or mutation on it is deterministic code.
- **Never hand the LLM a decision it could make as a join.** "Here are 6 assemblies, build the parent-child tree" is the anti-pattern: non-deterministic, unverifiable, irreversible-by-inference. If a relationship is derivable from data the documents already carry, it's a deterministic match, not an inference.
- **The model is a peripheral, not the brain.** Call it like a specialized, somewhat-unreliable device from deterministic application code — it is not the orchestrator of control flow.

## Determinism over probability (for load-bearing logic)

- Load-bearing logic — entity resolution, dependency sequencing, business routing, mutations — must be deterministic. Probability is acceptable only at the perception edge, never on the decision.
- Control flow is code, not LLM-inferred. The graph/orchestrator decides routing; the model fills bounded nodes. "The model is confident" is never a control-flow signal.
- The more consequential or irreversible the action, the more deterministic the path and the stronger the gate before it.

## Compound AI systems (systems over models)

- Production AI is a **system of mostly-deterministic components with the LLM at specific, bounded nodes** — not a monolithic mega-prompt. The deterministic scaffolding *is* the system; the model is one function call within it.
- Decompose into micro-tasks: one node extracts, a function queries the DB, another node formats. Isolate failures — a formatting failure doesn't lose the extraction. Unit-test the deterministic nodes; swap a cheaper/faster model into the easy ones.
- The architecture holds the state; the model only transforms it.

## Perception–validation split (IDP) + the tollgate

- **Perception (LLM):** map messy input to a strict schema — the model's *only* job.
- **Tollgate (validation):** enforce the schema at the boundary (Pydantic / typed schema). Schema mismatch → fail loud → automated retry. The model can't bypass the scaffolding because its output cannot enter the system until it validates.
- **Execution (deterministic):** validated data hits traditional code. The model has *zero agency* over execution — if it extracted `{action: migrate, target: production}`, the code that runs the migration is 100% deterministic.
- **Constrained generation:** box the model even within perception — JSON schema, enums, function-/tool-calling — so output is verifiable, not free-form prose you re-parse.

## Entity resolution = a deterministic-first funnel

Matching messy input to canonical records: reaching for an LLM or vector DB *first* is overkill (latency, cost, hallucination on a solved problem). Funnel cheapest-and-most-predictable first:

1. **Exact / normalized match (SQL).** Lowercase, strip, blocking keys, join. Handles the bulk at ~zero marginal cost.
2. **Algorithmic fuzzy.** Levenshtein / Jaro-Winkler on the residual; auto-match above a threshold.
3. **LLM residual (last resort).** Only the tiny ambiguous tail — and even then the model **ranks candidates for a human**; it does not commit the match.

## Propose, don't dispose

- AI **proposes** candidates; deterministic logic + a human **dispose**. Copilot suggests; you accept.
- The model's output is an input to a gate, never a committed action. Auto-commit scales with reversibility: trivial + reversible can auto-apply on a clean deterministic match; consequential / irreversible always gates.

## The ingestion / perception pipeline (file → structured)

Messy inputs (PDF, CAD/STEP, Office, slides) don't change the architecture — they push the boundary one step left. A perception pipeline sits *before* extraction:

- **Route by type.** An ingestion node identifies the MIME type and dispatches to the right parser.
- **Parse deterministically where the format allows.**
  - **Structured formats are NOT LLM input.** STEP/IGES (ISO 10303), Office XML, well-formed tables — parse with a real parser (CAD kernel, `python-pptx`/`python-docx`, a table extractor) → JSON/Markdown. Feeding their raw text to a context window is wasteful and hallucination-prone.
  - **Spatial / visual formats** (scanned PDFs, drawings): use layout-aware document→Markdown (vision models / Document AI / Textract / Docling / Unstructured) to preserve table + layout structure, *then* extract. Naive text strippers turn a table into gibberish and break validation downstream.
- **Then** the LLM converts the cleaned representation to the schema → validate → entity-resolve → execute.

## Anti-patterns

- The mega-prompt that reasons + plans + executes + formats in one call.
- Passing structured formats (STEP, Office XML) as raw text into a context window.
- Letting the LLM make a business decision, commit a mutation, or pick a target by similarity/position.
- Confidence used as a control-flow gate.
- Free-form prose output you re-parse instead of a validated schema.
- Vector/LLM matching for a problem exact + algorithmic fuzzy ER already solves.

## Industry prior art

- **Compound AI systems** — Berkeley "systems over models."
- **Intelligent Document Processing** — Google Document AI, AWS Textract, Docling/Unstructured: ML extracts → rules validate/match/route; the model never decides.
- **Entity resolution / record linkage** — decades old: deterministic blocking + matching first; probabilistic/ML on the residual only.
- **Human-in-the-loop / active learning** — propose → human disposes.
- **Constrained decoding / structured outputs** — schema-bounded generation.

## Cross-references

- A project's **hard agent rules** (no auto-fire of destructive actions; no inferred-target mutations; no confidence-based HITL bypass; LLM produces candidates, merge is mechanical) are this philosophy written down as enforceable invariants — point to them from the agent layer.
- Pairs with `error-handling` (fail loud at the tollgate) and `testing` (deterministic nodes are unit-testable; perception is the integration boundary where real-data tests live).
