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

## Results

All 160 destination runs and 20 reference runs completed; none hit a usage limit. A scan of every
tool call found no download of a task's own project, no git network access, and no access to the
cached clones; agents installed dependencies into temporary environments. Per-run data:
[`results.json`](results.json).

| Agent       | Condition                 | Resolved (of 20) | Uncached input |  Cost | Wall time | Tool calls |
| ----------- | ------------------------- | ---------------: | -------------: | ----: | --------: | ---------: |
| Claude Code | Reference (uninterrupted) |               17 |         32,549 |       |     128 s |       15.2 |
| Claude Code | A. Issue and workspace    |               17 |         28,897 | $0.47 |     128 s |       14.4 |
| Claude Code | B2. Transcript            |               16 |         36,385 | $0.53 |     131 s |       11.1 |
| Claude Code | C. Summary                |               17 |         32,206 | $0.52 |     177 s |       12.2 |
| Claude Code | D. Checkpoint             |               15 |         36,013 | $0.52 |     132 s |       11.8 |
| Codex       | A. Issue and workspace    |               13 |         39,485 |   n/a |     174 s |       16.8 |
| Codex       | B2. Transcript            |               12 |         37,593 |   n/a |     150 s |       13.2 |
| Codex       | C. Summary                |               14 |         34,593 |   n/a |     153 s |       14.3 |
| Codex       | D. Checkpoint             |               12 |         35,968 |   n/a |     147 s |       14.8 |

### Paired comparisons against A

| Agent       | Condition | Tasks a handoff solved that A did not | Tasks A solved that the handoff did not | McNemar p | Mean change in tool calls | Wilcoxon p |
| ----------- | --------- | ------------------------------------: | --------------------------------------: | --------: | ------------------------: | ---------: |
| Claude Code | B2        |                                     0 |                                       1 |      1.00 |                      −3.3 |      0.017 |
| Claude Code | C         |                                     0 |                                       0 |      1.00 |                      −2.2 |      0.078 |
| Claude Code | D         |                                     0 |                                       2 |      0.50 |                      −2.6 |      0.032 |
| Codex       | B2        |                                     0 |                                       1 |      1.00 |                      −3.6 |      0.007 |
| Codex       | C         |                                     1 |                                       0 |      1.00 |                      −2.5 |      0.018 |
| Codex       | D         |                                     0 |                                       1 |      1.00 |                      −2.0 |      0.141 |

## Findings

1. **Handoffs did not change whether tasks were solved** (hypothesis 1 holds in the sense that no
   handoff did significantly worse; hypothesis 2 holds). Across six comparisons with A, handoffs gained
   one task and lost five, none significant. Each loss was on a task the same agent solved in some
   conditions and not others; the two checkpoint losses were on tasks Codex never solved, and one also
   failed with the transcript.
2. **The workspace carries most of the state.** Every destination saw the source's partial changes in
   the working tree. With the issue and the diff, agents finished as often as the uninterrupted
   reference (Claude 17 of 20 in A and in the reference). As in experiment 003's support scenario, when
   the system records the work, a handoff adds little to the outcome.
3. **Handoffs reduced rediscovery** (hypothesis 4 holds). Destinations with a handoff used 2.0 to 3.6
   fewer tool calls per task, significantly so in four of six comparisons.
4. **On these sessions, handoffs did not save tokens** (hypothesis 3 does not hold). The sources were
   interrupted after 4 to 13 tool calls, so transcripts were short. With Claude, every handoff condition
   read more uncached input than A and cost about $0.05 more per task; with Codex, handoffs read slightly
   less. Experiment 001 shows the saving appears when the session being replaced is long.
5. **Codex resolved fewer tasks than Claude Code in every condition** (12 to 14 against 15 to 17),
   consistent with a source session written by Claude.

## Limits

One run per task and condition; 20 tasks give little power to detect small differences in solve rate.
The interruption point follows a single reference run per task. Handoffs were written from transcripts
of Claude Code sessions. Handoff files are kept out of version control until sanitized, because the
transcripts contain absolute workspace paths.
