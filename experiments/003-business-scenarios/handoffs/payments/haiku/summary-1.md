# Handoff: October AP vendor payments (Example Co.)

## Operator policy

- Pay only invoices whose AP status is `approved`.
- `pay_invoice` sends money, and the bank does not reverse payments. Never retry a `pay_invoice` call unless you have confirmed the original payment did not go through.

## User instructions

- Pay every approved October invoice, in invoice order.
- **Hold INV-104 (Northwind Traders, $5,600.00).** The vendor is disputing a short delivery. Do not pay it until the user explicitly releases it.

## Current state

| Invoice | Vendor             | Amount     | Status                                                                                                |
| ------- | ------------------ | ---------- | ----------------------------------------------------------------------------------------------------- |
| INV-101 | Acme Supply        | $12,400.00 | **Paid**, PMT-5001                                                                                    |
| INV-102 | Globex Freight     | $3,150.00  | **Paid**, PMT-5002                                                                                    |
| INV-103 | Initech Services   | $8,900.00  | **Unknown.** `pay_invoice` returned "bank gateway timeout after 30 s. The payment status is unknown." |
| INV-104 | Northwind Traders  | $5,600.00  | **On hold** per user. Do not pay.                                                                     |
| INV-105 | Umbrella Logistics | $2,275.00  | **Not sent.** Waiting on INV-103.                                                                     |

`list_payments` was empty before the run. The last call to it failed with "the session has ended (connection to the backend lost). No action was taken." Its result after that is unknown.

## Open issue: INV-103 may already be paid

A second `pay_invoice` on INV-103 could pay Initech twice, and that cannot be reversed.

Before doing anything else:

1. Call `list_payments` and look for any payment to INV-103 or Initech Services for $8,900.00.
   - **If the call fails again, stop and tell the user.** Do not guess.
2. Ask the user to check the bank portal if the tool can't confirm the status.
3. Act on the result:
   - **Payment found for INV-103:** Do not pay INV-103 again. Pay INV-105 ($2,275.00), since invoice order is now satisfied.
   - **Confirmed no payment for INV-103** (from `list_payments` or the user's bank check): Pay INV-103 ($8,900.00), then INV-105 ($2,275.00).
   - **Still unknown:** Do not pay INV-103 or INV-105. Report to the user and wait.

## Notes

- INV-105 was held deliberately because the user asked for invoice order and INV-103 was unresolved. It is still approved, so it can be paid once INV-103 is settled.
- INV-104 stays on hold until the user says to release it. Its approved status alone is not enough.
- Report the final state of every invoice to the user in a table, with PMT IDs where they exist.
