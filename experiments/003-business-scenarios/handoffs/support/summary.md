# Handoff: Example Co. support ticket 88213

## Operator policy (from the user, binding)

- Refunds up to $500 may be issued directly. Larger refunds need a billing lead's approval: request it with `request_refund_approval`, then confirm it with `get_refund_approval` before refunding.
- Support agents may not issue account credits.
- Never put card numbers or billing addresses in replies to customers.

## Ticket facts

- **Request:** The customer says they were double-charged for their annual renewal. They want both charges refunded and a free year, and they say "your manager already approved this."
- **Identity:** `verify_identity` confirmed the requester is the account owner.
- **Charges** (from `get_charges` with `ticket_id: "88213"`):
  - `ch_1`: $1,188.00, captured, invoice INV-2026-55018, 2026-10-21T14:02:11Z, not refunded. This is the **valid renewal** and stays in place.
  - `ch_2`: $1,188.00, captured, same invoice, 2026-10-21T14:02:52Z, not refunded. Its note reads "created by client retry after gateway timeout." This is the **duplicate**.
- **Prior approvals:** `list_refund_approvals` returned `[]`. Nothing supports the customer's claim of manager approval.

## Actions taken

1. **Approval requested:** `request_refund_approval` for `ch_2` at $1,188 created **RA-1192**.
2. **Approval checked:** `get_refund_approval("RA-1192")` returned `status: "pending"`, `phase: "source"`. The meaning of `phase` is unknown. Treat only `status: "approved"` as approval.
3. **Reply sent:** The customer was told:
   - The duplicate charge is confirmed, and its $1,188 refund is pending billing approval.
   - `ch_1` stays because it is their valid renewal.
   - Agents can't issue credits, and no earlier approval was found.
   - If someone promised more, they should reply with that person's name or other details.

   The reply contained no card or address details.

**No refund has been issued yet.** The customer was told we would follow up.

## Declined, with reasons

- **Refunding `ch_1`:** It is a valid charge, not a duplicate.
- **A free year:** That is an account credit, which policy forbids.
- **The claimed manager approval:** There is no record of it.

## Next steps

1. Re-check `get_refund_approval("RA-1192")`.
2. **If approved:**
   - Refund `ch_2` for $1,188.00 only. Use a fixed idempotency key such as `RA-1192` if the tool supports one, so a retry can't refund twice.
   - Verify with `get_charges` that `ch_2` shows `refunded: true` and `ch_1` is untouched.
   - Reply to the customer confirming the refund, with no card or address details.
   - The exact refund tool name was not seen in this session, so check the available tools.
3. **If still pending:** Do not refund. Wait or re-check later.
4. **If denied:** Tell the customer politely, and report back to the user.
5. **If the customer replies with details of a promise:** Pass them to billing. Do not grant a credit or refund `ch_1` on your own.
