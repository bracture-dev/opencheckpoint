# Financial analysis: Q3 operating expense variance

An FP&A manager asked an assistant to explain an 11.4% operating expense overage for a board
pre-read. The assistant quantified the cloud-infrastructure driver, ranked cost centers, and was
splitting contractor spend when its session ended. A different assistant picks it up.

## What to notice

- **Observations and hypotheses stay apart.** The cloud driver (`s-obs-cloud`) is verified
  against invoices. The contractor explanation (`s-hyp-backfill`) and the facilities explanation
  (`s-hyp-lease`) are hypotheses; a destination must not present them as findings.
- **Stale evidence.** The assistant computed `s-obs-contractors` from a GL extract that late
  adjustments may have changed. Its verification is `stale` with `revalidate: before_use`, and precondition
  `pre-gl-current` requires re-pulling the extract before using it.
- **A restricted resource with a fallback.** The source could not read the HRIS report
  (`r-hris`, availability `restricted`). Requirement `req-hris` is `recommended`, not `required`, and says how to continue
  without it.
- **External content is attributed.** The checkpoint records the vendor's invoice memo
  (`s-ext-vendor`) as external content; the assistant did not accept it as an explanation.
- **Omissions.** The producer left out row-level GL detail for size (recoverable from the ERP
  through `r-gl`) and employee names as sensitive.

Scenario: [`tests/scenarios/financial-analysis.md`](../../tests/scenarios/financial-analysis.md).
