# Experiment 002: handoffs on SWE-bench Verified

Do handoffs help an agent finish real software tasks that another agent started, and at what cost?

## Design

- **Tasks:** 20 SWE-bench Verified tasks rated "1-4 hours", drawn with a fixed seed
  ([`tasks.json`](tasks.json); `swe.py sample 20`).
- **Workspaces:** each is the repository at the task's base commit, re-initialized as a single commit,
  so no later history (and no upstream fix) is reachable. Claude Code runs with web tools disabled;
  Codex runs in its workspace-write sandbox, which has no network.
- **Reference:** Claude Code (Claude Opus 5.5) solves each task uninterrupted. Its tool-call count T
  sets the interruption point.
- **Source:** Claude Code solves the task again and is interrupted after T/2 tool calls, leaving its
  partial changes in the working tree. Transcripts and partial diffs are in [`handoffs/`](handoffs/).
- **Handoffs:** a prose summary and a checkpoint, each written by Claude Opus 5.5 from the source
  transcript with experiment 001's producer prompts. A checkpoint that fails to parse or validate gets
  one repair round; first-attempt and final validity are recorded.
- **Conditions:** every destination receives the issue and the interrupted workspace. A adds nothing;
  B2 adds the source transcript; C the summary; D the checkpoint.
- **Destinations:** Claude Code (Claude Opus 5.5) and Codex (gpt-6-astra, medium effort), one run per
  task and condition: 160 runs, plus 20 reference runs.
- **Evaluation:** the official SWE-bench harness (`swebench` 5.0.2, prebuilt x86-64 images under
  emulation). The patch evaluated is the workspace's change from the base commit, excluding files the
  benchmark's test patch touches.
- **Measures:** tasks resolved; uncached, cached, and output tokens; cost (Claude); wall time; tool
  calls.

### Changes made while piloting (before any destination run counted here)

1. The first pilot drew "<15 min" and "15 min - 1 hour" tasks and interrupted after the source's first
   edit. Claude Code edits files through shell commands, so the trigger never matched, and the source
   finished each task within seconds.
2. Interrupting just before the first write instead stopped the source after two tool calls on easy
   tasks and after two to six on harder ones, leaving little for a handoff to carry.
3. The final design uses "1-4 hours" tasks and interrupts at half of the reference run's tool calls,
   following the handoff-point method of _Handoff Debt_ (KC and Budathoki, 2026).

## Hypotheses

Written before the full set of destination runs.

1. Every handoff condition (B2, C, D) resolves at least as many tasks as A.
2. Summary and checkpoint resolve similar numbers of tasks (within two of 20).
3. Summary and checkpoint use fewer uncached input tokens than transcript replay.
4. With a handoff, destinations use fewer tool calls than in A (less rediscovery).
