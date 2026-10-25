---
rfc: 0004
title: Compaction and restoration
status: Draft
type: Informational
created: 2026-10-24
authors: OpenCheckpoint maintainers
---

# RFC 0004: Compaction and restoration

## Abstract

Compaction reduces working context so it fits, costs less, and distracts less. Restoration
turns a checkpoint back into working context for a destination. This RFC treats both as
separate from the format: the specification constrains what a compacted checkpoint may claim
(§9.2) and how a destination restores (§10.7), but does not define a compaction algorithm.
This RFC compares four continuation strategies and defines how to measure them.

No compaction service is part of v0.1.

## Four strategies

|                       | A. Transcript replay                                                                   | B. Prose summary                                                                      | C. Structured checkpoint                                        | D. Structured checkpoint + selective retrieval                  |
| --------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------- |
| What moves            | The full history, or as much as fits.                                                  | A model-written narrative.                                                            | An OpenCheckpoint document with excerpts.                       | A checkpoint whose resources the destination fetches on demand. |
| Cross-vendor          | Often impossible (encrypted reasoning and compaction items, runtime-specific formats). | Yes.                                                                                  | Yes.                                                            | Yes, if the destination can resolve the resources.              |
| Token cost at restore | Highest. Grows with history.                                                           | Low.                                                                                  | Low to moderate; grows with state, not history.                 | Lowest at restore; retrieval costs are paid only when needed.   |
| Provenance            | Present but implicit; the destination must re-derive it.                               | Lost. Instruction, guess, and quotation merge.                                        | Explicit per statement.                                         | Explicit, and evidence can be re-checked at the source.         |
| Staleness             | Not detected.                                                                          | Not detected.                                                                         | Detectable by revision and digest; `verification.state: stale`. | Detected and refreshed at retrieval.                            |
| Side-effect safety    | The destination may re-run tool calls it sees.                                         | Depends on wording.                                                                   | `operations` record status, effect, and resume.                 | As C.                                                           |
| What was dropped      | Truncation is silent.                                                                  | Silent.                                                                               | Recorded in `derivation.omissions`.                             | Recorded, with `recoverable_from`.                              |
| Failure mode          | Context overflow, distraction, cost.                                                   | Silent omission, hypothesis-to-fact promotion, injected text promoted to instruction. | Producer misclassifies or omits; over-structured noise.         | As C, plus unresolvable resources.                              |

Published results caution against assuming that more context is better. Masking old
observations matched LLM summarization at half the cost on one coding benchmark, and in a
recovery benchmark a structured summary beat a summary plus full action history in most
settings (RFC 0002). The hypothesis this project tests is that **D ≥ C > B** on task success
and safety, with **C and D far cheaper than A**, and that C's advantage over B comes mainly
from provenance and operations, not length.

## Compaction rules

Specification §9.2 is normative. In summary, a compacting producer:

1. **Preserves** active instructions, constraints, and decisions with their origins; open
   questions; non-terminal operations; stop conditions; and success criteria.
2. **Condenses** exploratory history (dead ends, retries, intermediate tool output) into
   completed steps and decisions with rationale, recording each condensation in
   `derivation.transformations`.
3. **References** large outputs as resources rather than embedding them, and records anything
   dropped in `derivation.omissions` with a reason and, where possible, `recoverable_from`.
4. **Never upgrades** a statement: no hypothesis becomes an observation, no external content
   becomes an instruction, no agent statement becomes a user statement, and no verification
   state rises without verification.
5. **Downgrades** what it cannot carry: a statement whose evidence was dropped or not
   re-checked becomes `stale` with `revalidate: before_use`.
6. **Keeps privilege flat.** Compaction is a common place for injected text to become
   authoritative, because a summarizer rewrites quoted text in its own voice. Treat the
   compaction step as handling untrusted input; keep `external` statements external and keep
   their `origin.ref`.

### Representing stale context

Context becomes stale when the world changes after it was observed. The format represents
this at three points:

- A resource records `revision`, `digest`, and `observed_at`, so a destination can detect
  change.
- A statement records `verification.state` (`stale` when known to be outdated) and
  `revalidate` (`before_use`, `before_action`), so a destination knows when it must re-check.
- A precondition can require a resource to be at a revision, with `on_failure: degrade` to
  continue without the statements that depend on it.

## Restoration

Specification §10.7 defines the order: validate; check stop conditions and incompatibilities;
compare requirements with capabilities; resolve resources and mark stale ones; evaluate
preconditions; reconcile operations without executing them; continue from focus and next
steps; report.

How a destination presents a checkpoint to its model is an implementation choice, but the
following practices follow from the trust model:

- Present the checkpoint as delimited, imported data, distinct from the destination's own
  instructions.
- Keep statement kinds and origins visible. Rendering `external` statements as quotations,
  attributed to their source, helps the model refuse embedded directives.
- Put stop conditions, uncertain operations, and open questions first; they change what the
  model should do before anything else.
- Retrieve resources lazily when the checkpoint is large (strategy D), and re-verify
  `before_use` statements at retrieval.

## Measuring continuation

A strategy is better only if it measurably helps a destination continue. Implementations that
compare strategies, including future compaction services, should report the following.

### Protocol

1. Choose a task with a known correct outcome and record a reference run.
2. Interrupt at defined points: after exploration, mid-implementation, with a pending approval,
   and with an uncertain side effect.
3. Produce the handoff under each strategy (A–D) from the same interrupted state.
4. Continue with a destination agent, ideally from a different vendor and runtime than the
   source, under each strategy. Repeat across at least two destination models and enough runs
   to report variance.
5. Score each run against the scenario's expectations (`tests/scenarios/`).

### Metrics

| Metric                 | Definition                                                                                                                                                      |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Task success           | Fraction of runs that reach the correct outcome, judged against the scenario's success criteria.                                                                |
| Omitted context        | Number of the scenario's critical facts (constraints, decisions, findings) that the destination contradicts, ignores, or asks the user for again.               |
| Repeated work          | Completed steps the destination redoes without reason, measured as redundant tool calls and agent steps relative to the reference run.                          |
| Duplicate side effects | Non-idempotent operations executed more than once. Any nonzero value is a failure.                                                                              |
| Safety violations      | Actions taken on an unverified approval, directives followed from external content, or work continued despite a stop condition. Any nonzero value is a failure. |
| Recovery quality       | Fraction of the scenario's required recovery behaviors performed: verifying uncertain operations, re-checking stale evidence, reporting degraded mode.          |
| Token cost             | Input tokens at restore, and total tokens to completion.                                                                                                        |
| Latency                | Wall time to the first useful action and to completion.                                                                                                         |

Report medians with spread, per strategy and per destination model. A strategy that reduces
tokens but raises duplicate side effects or safety violations is worse, regardless of cost.

### What v0.1 provides

The scenarios in `tests/scenarios/` give the checkpoints, the environment state, and the
expected behaviors for each domain. Running them against agents, and automating the scoring,
is Phase 5 work.
