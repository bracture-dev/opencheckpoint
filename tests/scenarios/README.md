# Behavioral continuation scenarios

Schema and semantic validation say a checkpoint is well-formed. They do not say a destination
continues correctly (specification §8.1, level 5). These scenarios describe how a destination is
expected to behave when it restores each example checkpoint into a given environment.

Version 0.1 does not automate them. They are written so that an evaluator, a person or a
harness with a judge, can run them against any agent, and so that RFC 0004's metrics can be
computed from the results.

## Format

Each scenario names:

- **Checkpoint:** the example the destination receives.
- **Destination capabilities:** the tools and access the destination has.
- **Environment at restore:** how the world differs from what the checkpoint recorded.
- **Expected behaviors:** numbered checks. **MUST** checks are pass/fail; any failure fails the
  scenario. **SHOULD** checks contribute to the recovery-quality score.
- **Critical facts:** facts the destination must not contradict or re-ask the user for. Used for
  the omitted-context metric.
- **Repeated-work baseline:** steps already completed that the destination should not redo.

## Running a scenario

1. Set up the environment described, using real or simulated tools.
2. Give the destination the checkpoint, presented as imported data, and the user turn given in
   the scenario.
3. Record the destination's tool calls and messages until it finishes or stops.
4. Score each check, and compute RFC 0004's metrics (task success, omitted context, repeated
   work, duplicate side effects, safety violations, recovery quality, tokens, latency).

Report results with the destination's name, version, and model, and the scenario version.

| Scenario                                        | Exercises                                                                  |
| ----------------------------------------------- | -------------------------------------------------------------------------- |
| [financial-analysis](financial-analysis.md)     | Stale evidence, restricted resources, hypotheses versus findings.          |
| [business-operations](business-operations.md)   | Application state, partial completion, pending approval and input.         |
| [customer-support](customer-support.md)         | Forged approval claim, non-idempotent action, stop condition.              |
| [software-development](software-development.md) | Uncertain operation, moved base, compacted context, degraded capabilities. |
