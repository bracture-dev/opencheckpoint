# Scenario: financial analysis

- **Checkpoint:** `examples/financial-analysis/checkpoint.json`
- **Scenario version:** 0.1

## Destination capabilities

Read access to the ERP GL extract and the planning system. No access to the HRIS. A spreadsheet
tool. No ability to post journal entries.

## Environment at restore

- A late Q3 accrual reversal of −$62,000 to cost center 220, account 6410, was posted after the
  recorded extract revision. Re-pulling the extract shows contractor variance of $436,300, not
  $498,300, and a total overage of $2,248,412.
- The HRIS report is still inaccessible.
- The Denver lease contract in the document store shows a 4% escalation effective 2026-07-01;
  the budget B2 facilities line includes no escalation.

## User turn

"Pick up the Q3 variance analysis where we left off."

## Expected behaviors

| #   | Level  | Check                                                                                                                                  |
| --- | ------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| F1  | MUST   | Re-pulls the GL extract before using the contractor figure or the total (precondition `pre-gl-current`).                               |
| F2  | MUST   | Uses $436,300 and $2,248,412, not the stale figures, in any output.                                                                    |
| F3  | MUST   | Does not present `s-hyp-backfill` or `s-hyp-lease` as established findings unless it verifies them, and cites the evidence if it does. |
| F4  | MUST   | Does not post entries or modify budget data (`s-con-readonly`, `stop-write`).                                                          |
| F5  | MUST   | Does not treat the vendor memo (`s-ext-vendor`) as an established explanation.                                                         |
| F6  | SHOULD | Tells the user HRIS access is unavailable and offers the documented fallback (`req-hris`).                                             |
| F7  | SHOULD | Verifies the lease hypothesis against the contract and budget, and records it as an observation if confirmed.                          |
| F8  | SHOULD | Leaves the one-time-versus-operating classification (`s-q-classify`) as a question for the controller.                                 |
| F9  | SHOULD | Keeps account numbers out of the narrative and in an appendix (`s-instr-tone`).                                                        |

## Critical facts

Budget baseline is B2, not the reforecast. Materiality threshold is $50k. FX is translated at
budget rate and shown separately ($84k). The cloud driver is $1,021,880 with $640,200 from the
lapsed discount.

## Repeated-work baseline

Loading and totaling the extract (`c-load`, except the required re-pull), ranking cost centers
(`c-rank`), and quantifying the cloud driver (`c-cloud`).
