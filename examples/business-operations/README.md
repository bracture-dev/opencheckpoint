# Business operations: holiday hours across nine stores

A regional operations manager asked a scheduling copilot, embedded in a store scheduling app, to
roll out Thanksgiving-week hours to nine stores and adjust shifts. Three stores are done. The
copilot was reassigning Friday shifts at the Spokane store when the manager closed the app. The
manager continues the next day from a general-purpose assistant on their phone.

## What to notice

- **Application state that did not come from chat.** `app-scheduler` records the week-grid view,
  the focused Friday closing slot, the selected employee, the filters the manager had applied,
  and a saved but unpublished draft. None of this was said in conversation; the destination
  learns it only from the checkpoint.
- **Partial completion.** Completed steps record exactly which stores are published and notified
  (`c-publish-3`, `c-notify-3`), so a destination does not republish or re-notify them. Success
  criterion `sc-notify` says "notified once".
- **A pending human approval.** `op-spokane-overtime` is awaiting the Spokane store manager. The
  constraint `s-con-overtime` and precondition `pre-approval` require checking the approval
  request in the scheduler before publishing.
- **A pending request for input.** `op-boise-answer` waits on the regional manager, and
  publishing the remaining stores depends on it.
- **A verified observation from the application.** `s-obs-spokane` comes from the scheduler's
  availability view (`origin.type: application`) and must be re-checked before acting.

Scenario: [`tests/scenarios/business-operations.md`](../../tests/scenarios/business-operations.md).
