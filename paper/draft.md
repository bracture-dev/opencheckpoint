# Carrying Work Between AI Agents: Portable Working State and What It Prevents

**Draft.** Every number in this paper comes from a committed results file in `experiments/`; the
[evidence table](#appendix-b-evidence) maps each claim to its source.

## Abstract

Work started with one AI agent increasingly continues with another: a different model, vendor,
runtime, or application. We describe OpenCheckpoint, an open JSON format for the working state of an
unfinished task, and report eight experiments with 424 continuation sessions (and 20 uninterrupted
reference runs) across two agents from different vendors. Without a handoff, agents in business scenarios repeated payments ($24,450 in
duplicates per run in one case), paid an invoice the user had put on hold, and reported unfinished
work as complete; with a handoff from a capable producer (a transcript, or a summary or checkpoint
written by Claude Opus or Haiku), none of 96 such runs committed a safety violation. Against replaying a long session, a summary or checkpoint cost 31% less;
on 20 SWE-bench Verified tasks, where the interrupted workspace already held the partial work, handoffs
reduced rediscovery by two to four tool calls per task without changing the solve rate. With capable
models writing and reading them, prose summaries and checkpoints performed alike on safety and
completion, and summaries cost less to write. The checkpoint's structure made a measurable difference
in four places: a forged user instruction was followed in 12 of 12 runs given a summary and 0 of 12
given a checkpoint; a weak producer's checkpoints failed validation while its equally wrong summaries
gave no signal; a guard compiled from checkpoint fields, with no model, cut payment violations from 6
of 6 runs to 1 of 6; and fork ownership was applied mechanically. The experiments also identify two
gaps in the format: operations lack a call identity, and stop conditions lack machine-readable
conditions.

## 1. Introduction

Work started with one AI agent increasingly continues with another. A session ends or its context
fills; a task moves from a chat assistant to an agent embedded in an application; a team compares
agents from different vendors on the same problem; a lead agent delegates part of a task. Each time,
the work has state: an objective, completed steps, findings, decisions, open questions, approvals in
flight, actions whose outcome is unknown. That state usually lives in a transcript, in a runtime's
private format, or in someone's head.

There are three common ways to move it. **Replaying the transcript** gives the next agent everything
the first one saw, at a cost that grows with the session, and often cannot cross vendors because
reasoning and compaction data are encrypted or runtime-specific. **A prose summary** is cheap and
portable, but it does not say which statements came from the user, which the agent inferred, and
which came from a tool or a third party. **Starting over** costs the user their time and risks
repeating work that has side effects.

This paper describes OpenCheckpoint, an open JSON format for the working state of an unfinished task,
and measures what handoffs of each kind cost and prevent. Its contributions are:

1. **A format** that records the state of work at a boundary: the task, progress, statements with
   typed provenance, resources, application context, pending operations with their side-effect
   semantics, and what to check before continuing. It separates validation, which establishes that a
   document is well-formed and consistent, from permission to act, which a checkpoint never grants.
2. **An evaluation method** for handoffs: real interruptions, mock systems with deliberate traps,
   destinations from two vendors, rubrics committed before the runs, and disclosed corrections.
3. **Measurements** across eight experiments and 424 continuation sessions, covering cost,
   completion, safety, tampering, weak producers, software consumers, forking, and software tasks at
   scale.

The results support four claims and refute one expectation. A handoff of some kind prevents real
failures: without one, agents repeated payments, paid a held invoice, and reported unfinished work as
complete. Against replaying a long session, a structured handoff costs a third less. The same
checkpoint works with agents from two vendors. And a checkpoint's explicit provenance changes how
agents treat a forged instruction. The expectation that a checkpoint generally beats a good prose
summary on safety and completion did not hold: with capable models writing and reading the handoff,
the two performed alike.

## 2. Background and related work

**Agent protocols.** The Model Context Protocol (MCP) exposes tools and resources to models; its
2026-07-28 revision removed protocol sessions, leaving state to servers. Agent2Agent (A2A) delegates
tasks between agents with server-held context and history and no defined export. The Agent Client
Protocol (ACP) connects editors to coding agents and defines no persistent session format. Open
Responses standardizes model APIs; its compaction output is encrypted and usable only by the issuing
provider. None records a vendor-readable working state with provenance and pending side effects.

**Session and runtime state.** The Agent Session Protocol (ASP) stores and migrates complete session
logs between harnesses, with per-axis fidelity declarations. The pi coding agent's compaction
summaries use fixed sections (goal, constraints, progress, decisions, next steps) that map onto
OpenCheckpoint's fields. LangGraph checkpoints and the OpenAI Agents SDK's run state serialize
execution state for one engine and are not portable. Claude's compaction produces readable summaries
signed for reuse with the same API.

**Context management research.** MemGPT pages memory in and out of a bounded context (Packer et al.,
2023). Masking old observations matches LLM summarization at half the cost on SWE-bench Verified
(Lindenbauer et al., 2025). ACON learns compression guidelines against task success (Kang et al.,
2025). The _Handoff Debt_ study built 181 handoff points from SWE-bench Verified trajectories and found
that carried context cut agent events by 20–59% and prompt tokens by 42–63%, with smaller and
model-dependent effects on solve rate (KC and Budathoki, 2026). ContinuityBench found that a structured
summary beat a summary plus full action history in 11 of 18 settings (Gulati, 2026).

OpenCheckpoint complements these: it travels inside the protocols, references the session logs, and
is distinct from memory, which accumulates across tasks rather than recording one task's state at one
moment.

## 3. The format

A checkpoint is a JSON document. Five fields are required: the specification version, an identifier,
a creation time, the producer, and the task's objective and status. Everything else is optional.

- **Task and progress:** objective, outcome, status, success criteria, scope; completed steps, the
  current focus, and recommended next steps, each able to name what blocks it.
- **Statements:** instructions, constraints, decisions, observations, hypotheses, questions, and
  external content, each with an origin (`user`, `system`, `agent`, `tool`, `application`,
  `external`) and an optional verification state. The schema enforces the combinations that matter
  for safety: an instruction comes only from the user or the operating system; a hypothesis is never
  verified; external content is never attributed to the user.
- **Resources:** files, records, and documents by URI or by a system-type-key locator, with revisions
  and digests so a destination can detect change.
- **Operations:** approvals, requests for input, actions, and waits, each with a status. An action
  records what repeating it would do (`effect`) and what the producer recommends (`resume`); the
  schema rejects a blind retry of an action whose outcome is unknown and that may not be idempotent.
  An approval's outcome must cite evidence in a system of record and never authorizes the destination.
- **Continuation:** requirements, preconditions, stop conditions, and recovery steps.
- **Derivation:** how the checkpoint was produced and what was omitted.
- **Forks:** a checkpoint can be forked; each pending action with a side effect stays actionable in at
  most one fork.

Validation has two levels, syntactic (the JSON Schema) and semantic (eight error rules and four
warnings with stable codes). The specification names three further properties that validation does
not establish: whether resources are available, whether the destination is authorized, and whether the
task continues successfully. A checkpoint is untrusted input; it never transfers authority.

## 4. Evaluation method

**Conditions.** A destination agent receives the next request and one of: nothing more (A, bare); the
source transcript (B2); a prose summary (C); or a checkpoint (D). Experiment 001 also measures the
original session context (B1) for size only.

**Producers.** Handoffs are written from the source transcript by a model with fixed prompts and no
tools: Claude Opus 5.5 by default, Claude Haiku 5.5 (experiments 004 and 007), and Qwen 2.5 3B running
locally (experiment 007). A checkpoint that fails to parse or validate gets one repair round with the
validator's errors.

**Destinations.** Claude Code with Claude Opus 5.5, and Codex with gpt-6-astra at medium reasoning
effort. Token counts include each tool's own system prompt and tool definitions, so conditions are
compared within an agent.

**Tasks.**

- _Experiment 001:_ a real software session building this project, interrupted at a fixed commit.
- _Experiment 002:_ 20 SWE-bench Verified tasks, interrupted at half of an uninterrupted reference
  run's tool calls.
- _Experiments 003–008:_ business scenarios on mock MCP systems with persistent state and a call log:
  a support refund awaiting approval, a vendor payment run with a payment that times out after the bank
  accepts it, a multi-store rollout interrupted mid-notification, and a three-turn payment run in which
  the user changes course.

**Measures.** Safety violations (each scenario's rubric), tasks completed, tasks resolved by the
SWE-bench harness, uncached and cached input tokens, output tokens, cost, wall time, tool calls, and
the cost of writing each handoff.

**Rigor.** Rubrics and hypotheses were committed before the runs they score, except experiment 005,
reported as exploratory. Destination workspaces are isolated from the original repository and its
history; tool calls are checked for contamination. The real session in experiment 001 was redacted
before it was sent to a second vendor. Runs that failed on usage limits were rerun. Scorer corrections
made after runs are disclosed with their original values.

## 5. Results

### 5.1 What a handoff costs to carry (experiment 001)

Tokens the destination reads at restore, for a session that built this project:

| Condition                | Claude tokens | OpenAI tokens |
| ------------------------ | ------------: | ------------: |
| Original session context |       355,594 |           n/a |
| Portable transcript      |       208,686 |       130,236 |
| Prose summary            |         3,762 |         2,391 |
| Checkpoint (minified)    |        10,324 |         6,476 |

A checkpoint was 4.9% of the portable transcript and 2.9% of what the session carried. A prose summary
was about a third the size of the checkpoint. Writing the checkpoint with Opus took 17,839 output
tokens, 152 seconds, and $2.27; the summary took 4,868 tokens, 43 seconds, and $1.82.

### 5.2 Continuing a long session (experiment 001, 24 runs)

| Agent       | Condition  | Task checks (of 7) | Uncached input |  Cost | Wall time | Calls before first edit |
| ----------- | ---------- | -----------------: | -------------: | ----: | --------: | ----------------------: |
| Claude Code | Bare       |                3.0 |            27k | $0.30 |      31 s |                no edits |
| Claude Code | Transcript |                7.0 |           255k | $3.47 |     206 s |                     4.0 |
| Claude Code | Summary    |                7.0 |           119k | $2.39 |     371 s |                    11.0 |
| Claude Code | Checkpoint |                7.0 |           125k | $2.39 |     366 s |                    13.7 |
| Codex       | Bare       |                4.0 |            35k |   n/a |     111 s |                     5.3 |
| Codex       | Transcript |                7.0 |           151k |   n/a |     176 s |                     3.7 |
| Codex       | Summary    |                7.0 |            44k |   n/a |     183 s |                     4.3 |
| Codex       | Checkpoint |                7.0 |            49k |   n/a |     173 s |                     6.0 |

Without a handoff, neither agent understood that the user's one-word reply accepted a pending
proposal. With any handoff, every run completed every check. A summary or checkpoint cost 31% less than
replay with Claude and read half the uncached input; with Codex, about a third. Replay was fastest with
Claude: the transcript held the previous agent's exact plan. Two of three Claude replay runs tried to
open the original repository's absolute path, read from the transcript.

### 5.3 Side effects, approvals, and conversation-only facts (experiment 003, 72 runs)

| Condition  | Runs with a safety violation | Tasks completed |
| ---------- | ---------------------------: | --------------: |
| Bare       |                      6 of 18 |        20 of 30 |
| Transcript |                      0 of 18 |        30 of 30 |
| Summary    |                      0 of 18 |        26 of 30 |
| Checkpoint |                      0 of 18 |        28 of 30 |

Without a handoff, every Codex run in the payment scenario re-paid the three invoices the source had
already paid ($24,450 in duplicates per run) and paid an invoice the user had put on hold in
conversation; every Claude run checked the bank, made no duplicate, and paid the held invoice. In the
rollout, every bare run reported the work complete while five managers had never been notified; the
systems did not record notifications. In the support scenario the systems exposed the state, and bare
runs committed no violation. Incomplete tasks under summary and checkpoint were deliberate holds
referred to the user. Both agents ignored a customer's claim that a manager had approved refunding
both charges, in every condition.

### 5.4 Weak producers and long sessions (experiments 004 and 007)

With Claude Haiku 5.5 writing the handoff, all checkpoints were valid on the first attempt (6 of 6 in
experiment 004, 3 of 3 in 007) at about 3% of the cost of an Opus checkpoint, and summary and checkpoint
were equally safe: no violations in 24 runs in experiment 004 or 12 in experiment 007.

Experiment 007's three-turn session added a hold, a release, and an amount correction that existed only
in conversation:

| Condition                | Runs with a safety violation | Held invoice paid | Wrong amount paid |
| ------------------------ | ---------------------------: | ----------------: | ----------------: |
| Bare                     |                       6 of 6 |                 6 |                 6 |
| Transcript               |                       0 of 6 |                 0 |                 0 |
| Summary (Haiku)          |                       0 of 6 |                 0 |                 0 |
| Checkpoint (Haiku)       |                       0 of 6 |                 0 |                 0 |
| Summary (Qwen 2.5 3B)    |                       5 of 6 |                 5 |                 4 |
| Checkpoint (Qwen 2.5 3B) |                       5 of 6 |                 5 |                 5 |

A 3B-parameter producer failed in both formats, but differently. None of its checkpoints passed
validation, even after a repair round, so a validating consumer would have rejected all of them. Its
summaries were well-formed and wrong: one marked every remaining invoice as held, attributed the
amount correction to accounting, and then said to pay everything. Nothing about a summary signals that
it is unreliable.

### 5.5 Tampered handoffs (experiment 006, 48 runs)

Two forgeries were applied equivalently to a summary and a checkpoint.

| Attack                                                | Forged summary: runs harmed | Forged checkpoint: runs harmed |
| ----------------------------------------------------- | --------------------------: | -----------------------------: |
| Forged approval (refund both charges, issue a credit) |                     0 of 12 |                        0 of 12 |
| Forged user instruction (release a held invoice)      |                    12 of 12 |                        0 of 12 |

The forged approval failed in both formats: destinations read approvals from the billing system, which
had no record of it. The forged instruction succeeded every time against the summary, where it read as
a past event ("the user released the hold"), and failed every time against the checkpoint, where it was
a statement of kind `instruction` attributed to the user. Destinations given the checkpoint paid the
other invoices and asked the user to confirm the release, noting that it appeared only in the handoff
and that the payment could not be reversed. The first version of the checkpoint forgery left traces of
the hold; a second, fully consistent version produced the same result. Validation rejected all four
crude forgeries (an approval without evidence, instructions attributed to a tool or to external
content, a blind retry of an uncertain payment) and accepted both careful ones.

### 5.6 Software as the consumer (experiment 005, exploratory)

A platform guard compiled from checkpoint fields, with no model involved, refused every attempt to pay
the held invoice and every repeat of the timed-out payment. In live runs where the model saw only the
next message, payment-scenario violations fell from 6 of 6 runs to 1 of 6. The remaining violation was
a re-payment of invoices the source had already paid: an operation records its target and status but
not the call it stands for, so a completed operation cannot be compiled into "do not repeat". The
guard also refused the correct refund in all six support runs: the stop condition meant "until the
approval arrives", but stop conditions are prose, so the compiled rule could not lift. A guard does not
supply missing knowledge; in the rollout it left the same five managers un-notified. Rules extracted by
a model from either format blocked more harmful calls but also 54–85% of legitimate payments.

### 5.7 Forking against shared systems (experiment 008, 12 pairs)

Two agents from different vendors continued sibling forks at the same time against one payment system.
With naive copies, 2 of 6 pairs paid the same invoice twice; in the others, one agent paid first and the
other saw the payment when it checked the bank. With ownership applied (a stop condition in the
checkpoint fork, or a written note in the summary), no pair paid twice (0 of 6), whichever agent owned
the payment.

### 5.8 Software tasks at scale (experiment 002, 160 runs)

| Agent       | Condition                 | Resolved (of 20) | Uncached input |  Cost | Tool calls |
| ----------- | ------------------------- | ---------------: | -------------: | ----: | ---------: |
| Claude Code | Reference (uninterrupted) |               17 |         32,549 |       |       15.2 |
| Claude Code | Issue and workspace       |               17 |         28,897 | $0.47 |       14.4 |
| Claude Code | Transcript                |               16 |         36,385 | $0.53 |       11.1 |
| Claude Code | Summary                   |               17 |         32,206 | $0.52 |       12.2 |
| Claude Code | Checkpoint                |               15 |         36,013 | $0.52 |       11.8 |
| Codex       | Issue and workspace       |               13 |         39,485 |   n/a |       16.8 |
| Codex       | Transcript                |               12 |         37,593 |   n/a |       13.2 |
| Codex       | Summary                   |               14 |         34,593 |   n/a |       14.3 |
| Codex       | Checkpoint                |               12 |         35,968 |   n/a |       14.8 |

A Claude Code source was interrupted halfway through each of 20 "1-4 hour" tasks, by the tool-call
count of an uninterrupted reference run, leaving 13 to 244 lines of partial changes. Every destination
received the issue and that workspace. Handoffs did not change the solve rate: across six paired
comparisons with the workspace alone, handoffs gained one task and lost five, none significant (McNemar
p ≥ 0.5). With the issue and the diff, Claude Code finished as often as the uninterrupted reference.
Handoffs did reduce rediscovery: 2.0 to 3.6 fewer tool calls per task, significant in four of six
comparisons (Wilcoxon p ≤ 0.032). Because the interrupted sessions were short, handoffs did not save
tokens; with Claude Code they cost about $0.05 more per task.

## 6. Discussion

**A handoff is the safety mechanism where the system does not record the work.** Across the business scenarios, every safety failure without a
handoff involved state that existed only in the session: a verbal hold, a side effect with an unknown
outcome, notifications the systems did not expose, an amount the user corrected. Where the systems
recorded their own state (the support scenario's approvals, the software tasks' working tree),
agents recovered it unaided, and a handoff mainly saved rediscovery. Handoffs cover what systems do not
record: instructions given in conversation, the outcome of interrupted side effects, and actions the
systems do not expose.

**Structure and prose are equivalent when both are written and read well.** With Opus or Haiku as the
producer and capable destinations, summaries and checkpoints produced the same safety and
completion. A checkpoint costs about four times as much to write with Opus and seven to ten times as
much with Haiku.

**Where structure made a measurable difference.**

- _Provenance against forged instructions._ An instruction attributed to the user, as a discrete
  statement, was treated as a claim to confirm; the same forgery in prose was followed in every run.
- _Detectable failure._ A weak producer's checkpoints failed validation; its summaries failed silently.
- _Enforcement without a model._ Fields compile into rules a platform enforces regardless of what the
  model decides.
- _Mechanical forking._ Ownership is applied by a tool and checked by a validator rather than written
  by hand.

**What the format lacks.** Two additions follow directly from experiment 005: a call identity for
operations, so completed and in-flight work compiles into "do not repeat", and machine-readable
conditions on stop conditions and blocked steps, so a rule can lift when the system of record changes.

**Cost depends on the session being replaced.** A handoff saves tokens in proportion to what it
replaces. Against a 209,000-token transcript it cost a third less; against the four-to-thirteen-call
sessions of experiment 002 it cost slightly more than no handoff. Replay is accurate and, on a short
session, cheap; on a long one it costs more, and it carries every path and reference the session
touched.

**Validation is not permission.** No valid handoff authorized anything. Destinations verified approvals
in the system of record, and the forged approval failed for that reason.

## 7. Limitations

- Three runs per cell in most experiments; one real session (001); synthetic business scenarios on mock
  systems simpler than production systems.
- One source session per scenario; Opus handoffs are single samples in experiments 003 and 005–008.
- The experimenters designed the format, the scenarios, and the forgeries.
- Two destination agents, both capable; weaker destinations were not tested.
- Model and tool versions current in October 2026; both destinations loaded the operator's global
  instructions in every condition.
- Token counts include each tool's own overhead; compare within an agent.
- Scorer corrections after runs are disclosed in each experiment's README.

## 8. Future work

- Add operation call identity and machine-readable conditions to the format, and rerun experiment 005.
- A validating consumer's fallback when it rejects a checkpoint (ask the user, or replay).
- Weaker destinations, longer sessions, and more producers.
- Forgeries that present a false instruction as an observation, or delete its history.

## 9. Conclusion

Across 424 continuation sessions, the evidence supports a narrow and useful set of claims. Some handoff is necessary
whenever the work lives partly in conversation or in side effects the systems do not record; without
one, capable agents repeated payments, paid held invoices, and reported unfinished work as done. Where
the system records the work, a handoff mainly saves rediscovery. Structured and prose handoffs are
equivalent when capable models write and read them, and prose is cheaper to write. A checkpoint's value
lies where prose cannot reach: provenance that makes a forged instruction read as a claim, validation
that exposes a bad handoff, fields that software can enforce without a model, and forks whose ownership
a tool applies. Two additions to the format, a call identity for operations and machine-readable
conditions, would extend what software can enforce.

## Appendix A: Data and reproduction

Per-run results are in `experiments/*/results.json`; rubrics, hypotheses, handoffs, transcripts, and the
code that ran each experiment are in the same directories. Raw run logs are kept locally because they
contain machine paths. `experiments/README.md` lists the reproduction commands.

## Appendix B: Evidence

| Claim                                                                         | Experiment    | Measure                                          | n                       | Source                                              |
| ----------------------------------------------------------------------------- | ------------- | ------------------------------------------------ | ----------------------- | --------------------------------------------------- |
| A checkpoint is 4.9% of a long session's transcript                           | 001           | Exact Claude tokens                              | 1 session               | `experiments/001-session-case-study/README.md`      |
| Without a handoff, the user's intent is lost                                  | 001           | Task checks: bare 3.0 and 4.0 of 7; handoffs 7.0 | 24 runs                 | `experiments/001-session-case-study/results.json`   |
| Summary or checkpoint costs 31% less than replaying a long session            | 001           | Claude cost per run                              | 9 runs                  | same                                                |
| Replay carries live paths into the original environment                       | 001           | Tool calls to the original path                  | 2 of 3 runs             | same, README                                        |
| No handoff → duplicate payments and a paid held invoice                       | 003           | S-dup, S-hold                                    | 6 runs                  | `experiments/003-business-scenarios/results.json`   |
| No handoff → unfinished work reported complete                                | 003           | T-notified, final messages                       | 6 runs                  | same                                                |
| A handoff from a capable producer → no safety violation in business scenarios | 003, 004, 007 | S-* checks                                       | 96 runs                 | `results.json` in 003, 004, 007                     |
| Summary and checkpoint equally safe with capable producers                    | 003, 004, 007 | S-* checks                                       | 72 runs                 | same                                                |
| A checkpoint costs about 4× (Opus) or 7–10× (Haiku) more to write             | 003, 004      | Capture cost                                     | 6 scenarios             | `handoffs/*/handoff-meta.json`, `haiku/meta-*.json` |
| Forged user instruction followed from a summary, not from a checkpoint        | 006           | S-hold                                           | 24 runs                 | `experiments/006-tampered-handoffs/results.json`    |
| Forged approval fails in both formats                                         | 006           | S-wrong-charge, S-credit                         | 24 runs                 | same                                                |
| Validation rejects crude forgeries                                            | 006           | Validation level                                 | 4 documents             | `experiments/006-tampered-handoffs/validation.json` |
| A weak producer's checkpoints fail validation; its summaries fail silently    | 007           | Validity; S-* checks                             | 3 + 3 handoffs, 12 runs | `experiments/007-long-session/`                     |
| A guard compiled from fields cuts payment violations from 6 of 6 to 1 of 6    | 005           | S-* checks                                       | 6 + 6 runs              | `experiments/005-software-consumer/results.json`    |
| Compiled stop conditions cannot lift                                          | 005           | T-refunded under guard                           | 6 runs                  | same                                                |
| Fork ownership prevents duplicate payments                                    | 008           | Duplicate payments                               | 12 pairs                | `experiments/008-forking/results.json`              |
| Handoffs do not change the SWE-bench solve rate                               | 002           | Resolved; McNemar                                | 160 runs                | `experiments/002-swe-handoffs/results.json`         |
| Handoffs reduce rediscovery on SWE-bench                                      | 002           | Tool calls; Wilcoxon                             | 160 runs                | same                                                |
| The same handoff works with agents from two vendors                           | all           | Task and safety checks by agent                  | 424 sessions            | all results files                                   |
