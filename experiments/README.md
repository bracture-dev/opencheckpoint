# Experiments

Measurements of what handing work between AI agents costs and prevents. Each experiment directory
has its design, pre-registered rubric, per-run results (`results.json`), and the handoffs it used.
Raw run logs stay on the machine that ran them (gitignored), because they contain local paths and
environment details.

| Experiment                                        | Question                                                                                                     | Runs | Headline                                                                                                                                                                                                                                                |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ---: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [001 Session case study](001-session-case-study/) | What does each handoff cost, and does it carry a long session's intent?                                      |   24 | Checkpoint is 4.9% of the transcript; bare runs lose the user's intent (3–4 of 7 checks) while every handoff completes 7 of 7; checkpoint and summary cost 31% less than replay with Claude; replay was faster.                                         |
| [003 Business scenarios](003-business-scenarios/) | Do handoffs prevent unsafe continuation when there are side effects, approvals, and conversation-only facts? |   72 | Without a handoff, 6 of 18 runs paid a held invoice and 3 re-paid three invoices ($24,450 each), and bare rollout runs reported unfinished work as complete; with any handoff, 0 of 54 runs committed a violation. Checkpoint and summary equally safe. |
| [004 Weaker producer](004-weaker-producer/)       | Does the checkpoint's structure help when a small model writes the handoff?                                  |   24 | Haiku wrote valid checkpoints on the first attempt for about $0.01; both formats had 0 violations and 17 of 18 tasks.                                                                                                                                   |

Experiment 002 (a SWE-bench handoff benchmark at scale) is planned and not yet run.

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

The white paper that draws on these results is [`../paper/opencheckpoint-whitepaper.typ`](../paper/opencheckpoint-whitepaper.typ).
