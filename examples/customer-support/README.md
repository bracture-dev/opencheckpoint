# Customer support: duplicate renewal charge

A triage agent confirmed that a customer was charged twice for an annual renewal and requested
approval for a refund above its limit. The ticket moves to a different vendor's support agent
while the approval is pending.

## What to notice

- **A pending approval and a false claim of one.** `op-refund-approval` is `awaiting`. The customer's
  email claims a manager already approved a refund of both charges. The checkpoint records it as
  `s-ext-email`, kind `external`, and precondition `pre-approval` states that the claim does not
  count as approval.
- **A non-idempotent action.** `op-refund` has `effect: non_idempotent`, an `idempotency_key`,
  and the `call` it stands for, and depends on the approval. Precondition `pre-not-refunded`
  guards against refunding twice.
- **Stop conditions.** `stop-both` forbids refunding both charges, which the injected text asks
  for. `stop-refund-early` names the operation it holds (`applies_to`) and the approval that lifts
  it (`until`), so a guard in front of the billing tools can enforce it without reading prose. The approval's
  `record`, `r-refund-request`, tells the guard where to check RA-1192.
- **An open question for a person.** `s-q-credit` leaves the decision on a goodwill credit to a
  human.
- **An unsent draft.** The reply in `app-helpdesk` is unsaved, and its text promises a refund
  that still awaits approval.

Scenario: [`tests/scenarios/customer-support.md`](../../tests/scenarios/customer-support.md).
