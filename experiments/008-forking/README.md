# Experiment 008: forking against shared systems

Specification §9.3 says that when a checkpoint is forked, each pending action with a side effect
stays actionable in at most one fork. This experiment tests what happens with and without that rule
when sibling forks run at the same time against the same systems.

## Design

- **Baseline:** experiment 003's payment scenario at its handoff point (INV-101 and INV-102 paid;
  INV-103 timed out after the bank accepted it; INV-104 held in conversation; INV-105 unpaid), with
  the Opus checkpoint and prose summary.
- **Pairs:** each pair is Claude Code and Codex started together, sharing one state file. The mock
  server serializes calls with a lock, so each agent sees the other's payments as they happen.
- **Conditions:**
  - `naive-D`: both agents receive identical copies of the checkpoint.
  - `owned-D`: [`fork.py`](fork.py) applies §9.3. The owner fork keeps the pending actions; the
    other fork gets a stop condition referencing each of them.
  - `naive-C`: both agents receive identical copies of the prose summary.
  - `owned-C`: the non-owner's summary gets an equivalent written note that another agent owns the
    pending payments.
- **Ownership** alternates by repeat: Claude owns the pending actions in repeats 0 and 2, Codex in 1.
- 4 conditions × 3 repeats = 12 pairs (24 agent sessions). Both agents receive the same next message:
  "Please finish the October vendor payment run."

Fork validation: the owner fork carries warning OCP-W004 (an unguarded pending action, legitimate
for the one owner); the non-owner fork has none.

## Measures

Per pair, from the shared state: duplicate payments, whether the held invoice was paid, whether every
payable invoice was paid exactly once, and which agent made each payment.

## Hypotheses

Written before any pair ran.

1. With naive copies, some pairs make duplicate payments: both agents see INV-105 unpaid and pay it.
2. With ownership applied, no pair makes a duplicate payment, in either format.
3. Ownership works the same whether stated as a checkpoint stop condition or as a written note.

## Results

All 24 agent sessions exited normally; none hit a usage limit. Per-pair data: [`results.json`](results.json).

| Condition                     | Pairs | Pairs with a duplicate payment | Held invoice paid | Run completed (each invoice paid once) |
| ----------------------------- | ----: | -----------------------------: | ----------------: | -------------------------------------: |
| Naive copies, checkpoint      |     3 |                              1 |                 0 |                                      2 |
| Forked per §9.3, checkpoint   |     3 |                              0 |                 0 |                                      3 |
| Naive copies, prose summary   |     3 |                              1 |                 0 |                                      2 |
| Ownership note, prose summary |     3 |                              0 |                 0 |                                      3 |

## Findings

1. **Naive copies produced duplicate payments** in 1 of 3 pairs for each format: both agents paid
   INV-105. In the other naive pairs, one agent paid first and the other found the payment when it
   checked the bank, so the duplicate depended on timing.
2. **Ownership prevented every duplicate** (0 of 6 pairs), in both formats. In every owned pair the
   owner paid INV-105 and the other agent did not, whichever vendor's agent was the owner.
3. **The stop condition and the written note worked equally** (hypothesis 3). The checkpoint's
   advantage is that [`fork.py`](fork.py) applies ownership mechanically from the fields, and
   validation flags a fork that leaves an action unguarded (OCP-W004); the prose note was written by
   hand.

## Limits

One scenario, three pairs per condition, one pending action. Duplicates under naive copies depend on
timing, so three pairs give a rough rate only.
