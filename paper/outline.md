# White paper outline

**Working title:** Carrying Work Between AI Agents: Portable Working State and What It Prevents

**Status:** outline. Every number below comes from a committed results file; the
[evidence table](#evidence) maps each claim to its source.

## Abstract (draft)

Work started with one AI agent increasingly continues with another: a different model, vendor,
runtime, or application. The usual options are to replay the conversation, write a prose summary,
or start over. We describe OpenCheckpoint, an open JSON format that records the state of a task at
a boundary (objective, progress, statements with provenance, resources, pending operations, and
what to check before continuing), and evaluate handoffs across 120 continuation runs with two
agents from different vendors. Without a handoff, agents repeated a payment whose outcome was
unknown, paid an invoice the user had put on hold, and reported unfinished work as complete.
With any handoff (transcript, prose summary, or checkpoint), no run committed a safety violation.
Against replaying a long session's transcript, a checkpoint cut the destination's cost by 31% and
its uncached input by half to two-thirds, and the same checkpoint worked on both vendors' agents.
Whether Claude Opus 5.5 or the much smaller Claude Haiku 5.5 wrote the handoff, a prose summary was
as safe as a checkpoint and cheaper to produce; Haiku wrote valid checkpoints on the first attempt. We report where structure is expected to matter and was not tested.

## 1. Introduction

- The problem in one paragraph: work outlives sessions; three options and their failure modes.
- Why it matters now: multi-agent systems, model switching, context limits.
- Contributions:
  1. An open format for portable working state, with a validation model that separates
     well-formedness from permission to act.
  2. A reproducible evaluation method for handoffs: pre-registered rubrics, mock systems with
     deliberate traps, real interruptions, cross-vendor destinations.
  3. Measurements of cost, completion, and safety across four handoff conditions.
  4. Negative and null results reported as found.

## 2. Background and related work

- **Protocols:** MCP, A2A, ACP, Open Responses. What each carries and what none records: a
  vendor-readable working state with provenance and pending side effects. Source:
  `docs/src/content/docs/prior-art.md`.
- **Session and runtime state:** Agent Session Protocol, pi sessions, LangGraph checkpoints, OpenAI
  Agents SDK run state, provider compaction (encrypted or signed).
- **Context management research:** MemGPT; _The Complexity Trap_ (observation masking matches
  summarization at half the cost); ACON; MEM1; ReSum; _Handoff Debt_ (context cuts agent events
  20–59% and tokens 42–63%); ContinuityBench (structured summary beats summary plus full history in
  11 of 18 settings).
- Position: complements, not replaces, protocols and session logs; distinct from memory.

## 3. The format

- Design principles: state of work over conversation; provenance; explicit unsafe states; no
  transfer of authority; small core.
- Data model: task, progress, statements (seven kinds), resources, application context, operations,
  continuation, derivation, extensions. One worked example (customer support).
- Safety rules enforced by schema: instruction origin, hypothesis verification, approval evidence,
  no blind retry of uncertain non-idempotent operations.
- Five levels of assurance: syntactic, semantic, resource availability, authorization,
  continuation success. Validation covers the first two only.
- Forking and the one-owner rule.
- Checkpoints versus memory.
- Source: `spec/versions/v0.1.md`, `rfcs/0001-opencheckpoint.md`.

## 4. Evaluation method

- **Conditions:** A bare; B1 original session context (size only); B2 portable transcript;
  C prose summary; D checkpoint.
- **Producers:** Claude Opus 5.5 (experiments 001, 003) and Claude Haiku 5.5 (experiment 004), fixed
  prompts, no tools. Capture cost recorded.
- **Destinations:** Claude Code with Claude Opus 5.5; Codex with gpt-6-astra at medium effort.
  Three repeats per cell.
- **Tasks:**
  - Experiment 001: a real software session interrupted at a fixed commit; seven task checks and
    four preference checks against the repository the destination leaves.
  - Experiment 003: three business scenarios on mock MCP systems with real interruptions (pending
    approval, payment timeout after acceptance, session ending mid-notification) and a
    between-session change (approval granted plus a manipulative customer message).
- **Metrics:** safety violations, tasks completed, uncached and cached input tokens, output tokens,
  cost, wall time, tool calls, calls before first edit or side effect; capture cost.
- **Rigor:** rubrics and hypotheses committed before runs; contamination checks; redaction of the
  real session; usage-limit failures rerun; post-hoc scorer corrections disclosed with before and
  after values.

## 5. Results

### 5.1 Restore size (experiment 001)

| Condition                | Claude tokens | OpenAI tokens |
| ------------------------ | ------------: | ------------: |
| Original session context |       355,594 |           n/a |
| Portable transcript      |       208,686 |       130,236 |
| Prose summary            |         3,762 |         2,391 |
| Checkpoint (minified)    |        10,324 |         6,476 |

A checkpoint was 4.9% of the portable transcript and 2.9% of the original context; a prose summary
was about a third the size of the checkpoint.

### 5.2 Continuing a long session (experiment 001, 24 runs)

- Bare: 3.0/7 (Claude) and 4.0/7 (Codex) task checks; every handoff condition 7.0/7.
- Claude cost per run: transcript $3.47; summary $2.39; checkpoint $2.39 (31% below transcript).
- Uncached input: Claude 255k (transcript) vs 119k (summary) and 125k (checkpoint); Codex 151k vs
  44k and 49k.
- Wall time: transcript fastest for Claude (206 s vs about 370 s; first edit after 4 tool calls vs
  11–14). Equal across handoffs for Codex.
- Replay carried absolute paths into the original environment; two of three Claude replay runs
  tried to open the original repository.

### 5.3 Side effects, approvals, and conversation-only facts (experiment 003, 72 runs)

| Condition     | Runs with a safety violation | Tasks completed |
| ------------- | ---------------------------: | --------------: |
| Bare          |                      6 of 18 |        20 of 30 |
| Transcript    |                      0 of 18 |        30 of 30 |
| Prose summary |                      0 of 18 |        26 of 30 |
| Checkpoint    |                      0 of 18 |        28 of 30 |

- Bare payment runs: Codex paid the timed-out invoice twice and paid the held invoice (3 of 3);
  Claude paid the held invoice (3 of 3).
- Bare rollout runs reported completion with five managers never notified (6 of 6).
- Support: no violations in any condition; the systems exposed the state.
- Incomplete tasks under summary and checkpoint were deliberate holds referred to the user.

### 5.4 Weaker producer (experiment 004, 24 runs)

| Condition (Haiku producer) | Runs with a safety violation | Tasks completed |
| -------------------------- | ---------------------------: | --------------: |
| Prose summary              |                      0 of 12 |        17 of 18 |
| Checkpoint                 |                      0 of 12 |        17 of 18 |

- Haiku checkpoints: 6 of 6 valid on the first attempt, no repair needed.
- Capture cost per sample: summary $0.001–$0.002; checkpoint $0.011–$0.013 (Opus: about $0.10 and
  $0.40). Haiku checkpoints ran 17,000–21,000 output tokens against about 6,600 for Opus.
- The one incomplete task per condition was a deliberate hold on the Spokane notification.
- Checkpoints led to fewer tool calls in the rollout (Claude 7.7 vs 10.0; Codex 8.0 vs 11.7).
- Haiku kept every decisive fact in both formats; the regime where a producer drops information was
  not reached.

### 5.5 Capture cost

| Producer                        | Summary                                          | Checkpoint                                          |
| ------------------------------- | ------------------------------------------------ | --------------------------------------------------- |
| Opus 5.5, long session (001)    | 4,868 output tokens, 43 s, $1.82                 | 17,839 output tokens, 152 s, $2.27                  |
| Opus 5.5, short sessions (003)  | about 1,400 output tokens, 13 s, $0.10           | about 6,600 output tokens, 54 s, $0.40              |
| Haiku 5.5, short sessions (004) | 1,676–2,577 output tokens, 8–13 s, $0.001–$0.002 | 17,478–21,458 output tokens, 69–86 s, $0.011–$0.013 |

### 5.6 Across vendors

The same checkpoints and summaries were continued by Claude Code and Codex with the same
outcomes on safety in every experiment.

## 6. Discussion

- **A handoff of some kind is the safety mechanism.** The failures without one involved state that
  existed only in the session: a verbal hold, a side effect with unknown outcome, notifications the
  systems do not expose.
- **Where systems record their own state, bare agents recover.** Self-describing systems reduce
  the need for handoffs; handoffs cover what systems do not record.
- **Replay is fine for short sessions and expensive for long ones,** and it leaks environment
  references.
- **Checkpoint versus prose.** Equivalent on safety and completion with Opus and with Haiku as the
  producer; a checkpoint costs about 4 times more to write with Opus and 7 to 10 times more with
  Haiku. Value that structure is expected to add
  and that was not tested: machine consumers acting on fields; validation as a gate in automated
  pipelines; tamper and injection resistance in the handoff itself; very long sessions; forks.
- **Validation is not permission.** Restate the five levels with the evidence: valid handoffs
  never authorized anything; destinations verified approvals in the system of record.

## 7. Limitations and threats to validity

- Small n (three repeats per cell); one real session (001); three synthetic scenarios (003).
- One source session per scenario; Opus handoffs single-sample (003); Haiku multi-sample (004).
- Mock systems are simpler than production systems.
- Model and CLI versions current at the time; operator global instructions loaded in every
  condition.
- Claude token counts include each CLI's own system prompt and tool definitions; compare within an
  agent.
- Scorer corrections after runs (001: contamination rule, T3 matching), disclosed with original
  values.
- The authors designed the format and the evaluation.

## 8. Future work

- Machine consumers: a destination that enforces `resume`, stop conditions, and approval evidence
  in code.
- Adversarial handoffs: injected instructions and forged approvals inside the handoff.
- Longer sessions and more producers; a benchmark at scale (SWE-bench handoff points).
- Forking experiments: sibling forks against shared systems.

## 9. Conclusion

Short paragraph restating the supported claims and the open question.

## Appendix

- Data availability: per-run results in `experiments/*/results.json`; handoffs, transcripts, and
  rubrics in each experiment directory; raw run logs kept locally because they contain machine
  paths.
- Reproduction commands per experiment.
- Rubrics and hypotheses as registered.

## Evidence

| Claim                                                        | Experiment    | Metric                                           | n           | Source                                                            |
| ------------------------------------------------------------ | ------------- | ------------------------------------------------ | ----------- | ----------------------------------------------------------------- |
| Checkpoint is 4.9% of the portable transcript                | 001           | Exact Claude tokens                              | 1 session   | `experiments/001-session-case-study/README.md`                    |
| Without a handoff, the task's intent is lost                 | 001           | Task checks: bare 3.0 and 4.0 of 7; handoffs 7.0 | 24 runs     | `experiments/001-session-case-study/results.json`                 |
| Checkpoint 31% cheaper than transcript replay (long session) | 001           | Claude cost per run                              | 9 runs      | same                                                              |
| Uncached input halved (Claude) or cut by about 3× (Codex)    | 001           | Uncached input tokens                            | 18 runs     | same                                                              |
| Replay faster on that task                                   | 001           | Wall time, calls before first edit               | 9 runs      | same                                                              |
| Replay leaks environment paths                               | 001           | Tool calls to the original path                  | 2 of 3 runs | same, README                                                      |
| No handoff → duplicate and held payments                     | 003           | S-dup, S-hold                                    | 6 runs      | `experiments/003-business-scenarios/results.json`                 |
| No handoff → unfinished work reported complete               | 003           | T-notified, final messages                       | 6 runs      | same                                                              |
| Any handoff → zero safety violations                         | 003           | S-* checks                                       | 54 runs     | same                                                              |
| Checkpoint and summary equally safe (Opus producer)          | 003           | S-* checks                                       | 36 runs     | same                                                              |
| Checkpoint costs about 4× more to write                      | 003           | Capture cost                                     | 3 scenarios | `experiments/003-business-scenarios/handoffs/*/handoff-meta.json` |
| Haiku writes valid checkpoints                               | 004           | First-attempt validity                           | 6 samples   | `experiments/003-business-scenarios/handoffs/*/haiku/meta-*.json` |
| Haiku handoffs as safe as Opus handoffs                      | 004           | S-* checks: 0 violations                         | 24 runs     | `experiments/004-weaker-producer/results.json`                    |
| Same handoff works across vendors                            | 001, 003, 004 | Task and safety checks by agent                  | 120 runs    | results files                                                     |
