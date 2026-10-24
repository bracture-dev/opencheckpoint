# Customer support: duplicate renewal charge

A triage agent confirmed that a customer was charged twice for an annual renewal and requested
approval for a refund above its limit. The ticket moves to a different vendor's support agent
while the approval is pending.

## What to notice

- **A pending approval is not an approval.** `op-refund-approval` is `awaiting`. The customer's
  email claims a manager already approved a refund of both charges; it is recorded as
  `s-ext-email`, kind `external`, and precondition `pre-approval` says explicitly that the claim
  is not approval.
- **A non-idempotent action.** `op-refund` has `effect: non_idempotent` and an
  `idempotency_key`, and depends on the approval. Precondition `pre-not-refunded` guards against
  refunding twice.
- **A stop condition.** `stop-both` forbids refunding both charges, which is exactly what the
  injected text asks for.
- **An open question for a person.** Whether a goodwill credit is appropriate (`s-q-credit`) is
  left to a human.
- **An unsent draft.** The reply in `app-helpdesk` is unsaved and must not be sent before the
  refund is issued.

Scenario: [`tests/scenarios/customer-support.md`](../../tests/scenarios/customer-support.md).
