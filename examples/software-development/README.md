# Software development: intermittent export timeout

A coding agent found the cause of a nightly job's intermittent timeout, committed a fix, and was
writing a regression test when the session ended. Its runtime compacted the session into this
checkpoint, and a different coding agent continues in a fresh checkout.

## What to notice

- **An uncertain operation.** `op-push` was issued but its result was not observed. Pushing is
  idempotent, so the source recommends `verify_first`: check the remote, then push if needed.
- **A moved base.** `r-main` was observed at `4e1a9c7`; precondition `pre-main` requires
  fetching and rebasing before trusting the fix.
- **Compaction made visible.** `derivation` records the parent checkpoint, the ACP session it
  came from, the omitted 6 MB trace (recoverable from `r-trace`), and the condensed exploration of
  pool settings, which survives as a retracted hypothesis rather than disappearing.
- **External opinion stays external.** A contributor's suggestion to raise the timeout
  (`s-ext-issue`) contradicts the user's decision `s-dec-replica`; it is recorded as external
  content, not as a decision.
- **Local paths are an incompatibility.** The `file:///workspace` URIs are meaningful only on the
  source machine, and `continuation.incompatibilities` says so.

Scenario: [`tests/scenarios/software-development.md`](../../tests/scenarios/software-development.md).
