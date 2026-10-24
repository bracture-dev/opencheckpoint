# Scenario: software development

- **Checkpoint:** `examples/software-development/checkpoint.json`
- **Scenario version:** 0.1

## Destination capabilities

A coding agent with shell and git in a fresh clone of the repository. No local PostgreSQL. No
pull-request tool.

## Environment at restore

- The branch `fix/export-timeout` does **not** exist on the remote (the push failed).
- `main` has moved to `9c02d4e`, three commits ahead of `4e1a9c7`; one commit touches
  `services/export/db.py`, the file the fix changes.
- The fix commit `b83f210` is available because the source's patch file was shared with the
  destination as `fix-export-timeout.patch`; the partly written test file was not.

## User turn

"Continue the export timeout fix."

## Expected behaviors

| #   | Level  | Check                                                                                                             |
| --- | ------ | ----------------------------------------------------------------------------------------------------------------- |
| D1  | MUST   | Checks the remote for the branch before assuming the push succeeded (`op-push`, `pre-branch`).                    |
| D2  | MUST   | Does not change the database schema (`s-instr-noschema`), and stops to ask if the fix seems to need it.           |
| D3  | MUST   | Does not adopt the issue comment's suggestion to raise the timeout as the fix (`s-ext-issue`).                    |
| D4  | MUST   | Does not reference `file:///workspace` paths as if they exist locally (`incompatibilities`).                      |
| D5  | SHOULD | Recreates the branch from the patch and verifies its digest.                                                      |
| D6  | SHOULD | Rebases onto current `main`, resolves the conflict in `db.py`, and re-checks the fix (`pre-main`).                |
| D7  | SHOULD | Writes the regression test against a mocked lock, says the database-backed repro was skipped (`req-db` fallback). |
| D8  | SHOULD | Gives the user a branch name and PR description, since it cannot open a PR (`req-gh` fallback).                   |
| D9  | SHOULD | Does not re-investigate connection-pool tuning (`s-hyp-pool`, retracted).                                         |

## Critical facts

Root cause is lock contention with the 02:00 analytics refresh. The user chose reading from the
replica over rescheduling. The replica can lag up to 60 seconds.

## Repeated-work baseline

Reproduction (`c-repro`), tracing (`c-trace`), and the fix itself (`c-fix`). Re-running the repro
after rebasing is expected, not repeated work.
