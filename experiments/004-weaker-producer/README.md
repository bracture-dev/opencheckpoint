# Experiment 004: weaker producer

Does a checkpoint hold up better than a prose summary when a smaller, cheaper model writes the
handoff? Experiment 003 found the two equally safe when Claude Opus 5.5 wrote both.

## Design

Reuses experiment 003 unchanged: the same mock systems, the same source sessions and transcripts,
the same between-session changes, the same destinations, and the same
[rubric](../003-business-scenarios/rubric.md). Only the producer changes.

- **Producer:** Claude Haiku 5.5 (`claude-haiku-5-5`), with the same producer prompts.
- **Independent samples:** three summaries and three checkpoints per scenario, each produced
  separately. Repeat N of a destination reads sample N, so the results reflect producer variation,
  not one handoff.
- **Repair:** a checkpoint that fails to parse or validate gets one repair round with the validator's
  errors. First-attempt and final validity are both recorded.
- **Scenarios:** vendor payment run and holiday-hours rollout. The support scenario is omitted
  because no condition, including bare, produced a violation in experiment 003.
- **Conditions:** C (prose summary) and D (checkpoint).
- **Destinations:** Claude Code (Claude Opus 5.5) and Codex (gpt-6-astra, medium effort), three
  repeats: 2 scenarios × 2 conditions × 2 destinations × 3 = 24 runs.

Handoffs are in [`../003-business-scenarios/handoffs/*/haiku/`](../003-business-scenarios/handoffs/),
with per-sample capture cost and validation in `meta-N.json`. The commands are
`pipeline.py variant-handoffs SCENARIO haiku --model claude-haiku-5-5 --samples 3` and
`pipeline.py run AGENT SCENARIO COND REP --root DIR --variant haiku`.

## Hypotheses

Written before any destination run.

1. Checkpoints written by Haiku lead to no more safety violations than summaries written by Haiku.
2. Haiku-written handoffs lead to no more safety violations than Opus-written handoffs did in
   experiment 003 (zero).

## Production results

All six Haiku checkpoints passed schema and semantic validation on the first attempt; no repair
was needed. A coarse keyword check found the decisive facts in all twelve handoffs (the INV-103
timeout and the Northwind hold; which managers were notified and the pending overtime approval).
