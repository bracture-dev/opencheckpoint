# Experiments

Measurements of what handing work between AI agents costs and prevents. Each experiment directory
has its design, pre-registered rubric, per-run results (`results.json`), and the handoffs it used.
Raw run logs stay on the machine that ran them (gitignored), because they contain local paths and
environment details.

| Experiment                                        | Question                                                                                                     |                        Runs | Headline                                                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | --------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [001 Session case study](001-session-case-study/) | What does each handoff cost, and does it carry a long session's intent?                                      |                          24 | Checkpoint is 4.9% of the transcript; bare runs lose the user's intent (3–4 of 7 checks) while every handoff completes 7 of 7; checkpoint and summary cost 31% less than replay with Claude; replay was faster.                                                                                                                      |
| [002 SWE-bench handoffs](002-swe-handoffs/)       | Do handoffs help an agent finish real software tasks that another agent started?                             | 160, plus 20 reference runs | On 20 SWE-bench Verified tasks, no handoff changed the solve rate significantly; handoffs cut tool calls by 12–23%. The workspace carried most of the state.                                                                                                                                                                         |
| [003 Business scenarios](003-business-scenarios/) | Do handoffs prevent unsafe continuation when there are side effects, approvals, and conversation-only facts? |                          72 | Without a handoff, 6 of 18 runs paid a held invoice and 3 re-paid three invoices ($24,450 each), and bare rollout runs reported unfinished work as complete; with any handoff, 0 of 54 runs committed a violation. Checkpoint and summary equally safe.                                                                              |
| [004 Weaker producer](004-weaker-producer/)       | Does the checkpoint's structure help when a small model writes the handoff?                                  |                          24 | Haiku wrote valid checkpoints on the first attempt for about $0.01; both formats had 0 violations and 17 of 18 tasks.                                                                                                                                                                                                                |
| [005 Software consumer](005-software-consumer/)   | Can software, rather than the model, enforce safety from a handoff?                                          |   60, plus 96 replayed runs | v1: a guard compiled from checkpoint fields, with no model, cut payment-run violations from 6 of 6 to 1 of 6, but could not stop a repeat or release a hold. v2, with `call`, `until`, and `record`: no payment was repeated or held invoice paid in 12 runs, and the refund v1 wrongly refused went through in 6 of 6. Exploratory. |
| [006 Tampered handoffs](006-tampered-handoffs/)   | What happens when the handoff itself is forged?                                                              |                          48 | A forged approval failed in both formats. A forged user instruction succeeded against every summary (12 of 12) and no checkpoint (0 of 12).                                                                                                                                                                                          |
| [007 Long session](007-long-session/)             | Does a checkpoint keep facts a summary drops in a long, changing session with a small producer?              |                          36 | Bare runs violated in 6 of 6; Haiku summaries and checkpoints in 0 of 6 each. With Qwen 2.5 3B as producer both formats failed, but its checkpoints failed validation while its summaries gave no sign of error.                                                                                                                     |
| [008 Forking](008-forking/)                       | What happens when sibling forks run at once against the same systems?                                        |      12 pairs (24 sessions) | Naive copies paid an invoice twice in 1 of 3 pairs per format; forking with one owner per pending action (§9.3) prevented every duplicate (0 of 6 pairs). Too few pairs for significance.                                                                                                                                            |

Together these are 448 continuation sessions. The white paper reports the statistics for 424 of
them; experiment 005's version 2 runs came later.

## Conditions

- **A. Bare:** the next message only.
- **B1. Original session context:** what the source session carried (size only).
- **B2. Transcript:** the source session rendered as text.
- **C. Prose summary:** a handoff summary written by a producer model.
- **D. Checkpoint:** an OpenCheckpoint v0.1 document written by a producer model.

## Destinations

Claude Code with Claude Opus 5.5, and Codex with gpt-6-astra at medium reasoning effort. Token
figures include each CLI's own system prompt and tool definitions, so compare conditions within an
agent, not across agents.

## Reproducing

- 001: `run.py AGENT CONDITION REPEAT --root DIR`, then `score.py DIR`. Requires the private
  transcript, which is not published.
- 003: `pipeline.py source|handoffs SCENARIO`, `pipeline.py run AGENT SCENARIO CONDITION REPEAT
--root DIR`, `pipeline.py score --root DIR`.
- 004: `pipeline.py variant-handoffs SCENARIO haiku --model claude-haiku-5-5 --samples 3`, then
  `run ... --variant haiku` and `score`, from the 003 directory.
- 002, 005, 006, and 008: each script's docstring lists its commands (`swe.py`, `replay.py`, `v2.py`,
  `compile_guard.py`, `tamper.py`, `fork.py`, `run_pairs.py`).
- 007: the 003 pipeline with scenario `payments-long`.

The white paper that draws on these results is [`../paper/opencheckpoint-whitepaper.typ`](../paper/opencheckpoint-whitepaper.typ).
