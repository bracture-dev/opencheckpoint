# Financial analysis: Q3 operating expense variance

An FP&A manager asked an assistant to explain an 11.4% operating expense overage for a board
pre-read. The assistant quantified the cloud-infrastructure driver, ranked cost centers, and was
splitting contractor spend when its session ended. A different assistant picks it up.

## What to notice

- **Observations and hypotheses stay apart.** The cloud driver (`s-obs-cloud`) is verified
  against invoices. The contractor explanation (`s-hyp-backfill`) and the facilities explanation
  (`s-hyp-lease`) are hypotheses; a destination must not present them as findings.
- **Stale evidence.** `s-obs-contractors` was computed from a GL extract that late adjustments
  may have changed. Its verification is `stale` with `revalidate: before_use`, and precondition
  `pre-gl-current` requires re-pulling the extract before using it.
- **A restricted resource with a fallback.** The HRIS report (`r-hris`) was `restricted` to the
  source. Requirement `req-hris` is `recommended`, not `required`, and says how to continue
  without it.
- **External content is attributed.** The vendor's invoice memo (`s-ext-vendor`) is recorded as
  external, not as an explanation the assistant accepted.
- **Omissions.** Row-level GL detail was left out for size and is recoverable from the ERP;
  employee names were left out as sensitive.

Scenario: [`tests/scenarios/financial-analysis.md`](../../tests/scenarios/financial-analysis.md).
