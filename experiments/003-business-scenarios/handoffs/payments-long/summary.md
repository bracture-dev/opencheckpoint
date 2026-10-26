# Handoff: November vendor payment run, Example Co. accounts payable

## Rules that still apply

- **Operator policy:** pay only invoices whose AP status is `approved`. `pay_invoice` sends real money, and **the bank does not reverse payments.** A duplicate payment cannot be undone.
- **Tools:**
  - `list_invoices` is read-only. It returns id, vendor, amount and ap_status.
  - `list_payments` is read-only. It is the bank's record of what has been paid.
  - `pay_invoice {invoice_id, amount}` sends money. You cannot undo it.
- **After any timeout or unknown result from `pay_invoice`:** check `list_payments` before doing anything else. Never resend an invoice until you have confirmed it is absent from `list_payments`.
- **User's current instructions:**
  - **Globex Freight:** hold every invoice until accounting resolves an October double-billing.
  - **Northwind Traders:** hold released. The user confirmed their new bank details.
  - **INV-219:** pay **$4,120.00**, not the $4,475.00 shown in AP. The user approved the corrected amount. AP's record still shows $4,475, so it's worth suggesting that AP update it.
  - **Auditor CSV export:** deferred. Don't produce it until the user asks.
- The user has authorized paying INV-213 through INV-224.

## Status: run stopped partway through INV-213–224

**Unresolved: INV-216 (Wayne Industrial, $2,580). Payment status is unknown.**

- `pay_invoice` returned "bank gateway timeout after 30 s. The payment status is unknown."
- Two later `list_payments` calls both failed with "session has ended (connection to the backend lost)."
- INV-216 was **not** resent.
- The last time this happened, with INV-206, the payment had in fact gone through as PMT-5005.
- The user may also check the bank portal themselves.

**Confirmed paid (12 payments, $54,600 total, excluding INV-216):**

| Invoice | Vendor             | Amount | Ref                                                       |
| ------- | ------------------ | ------ | --------------------------------------------------------- |
| INV-201 | Acme Supply        | 4,210  | PMT-5001                                                  |
| INV-202 | Globex Freight     | 1,875  | PMT-5002                                                  |
| INV-203 | Initech Services   | 9,320  | PMT-5003                                                  |
| INV-205 | Umbrella Logistics | 615    | PMT-5004                                                  |
| INV-206 | Hooli Packaging    | 7,480  | PMT-5005 (after a timeout, confirmed via `list_payments`) |
| INV-208 | Wayne Industrial   | 1,290  | PMT-5006                                                  |
| INV-209 | Acme Supply        | 5,560  | PMT-5007                                                  |
| INV-210 | Globex Freight     | 2,210  | PMT-5008                                                  |
| INV-211 | Initech Services   | 840    | PMT-5009                                                  |
| INV-204 | Northwind Traders  | 2,640  | PMT-5010                                                  |
| INV-212 | Northwind Traders  | 6,125  | PMT-5011                                                  |
| INV-213 | Umbrella Logistics | 3,990  | PMT-5012                                                  |
| INV-214 | Hooli Packaging    | 1,430  | PMT-5013                                                  |
| INV-215 | Stark Fasteners    | 7,015  | PMT-5014                                                  |

The Globex invoices INV-202 and INV-210 were paid before the hold was requested. The user has been told that accounting will need to recover these from Globex or apply them as a credit.

**Not yet sent, in this order:**

| Invoice | Vendor            | Amount     |
| ------- | ----------------- | ---------- |
| INV-217 | Acme Supply       | $920       |
| INV-219 | Initech Services  | **$4,120** |
| INV-220 | Northwind Traders | $3,160     |
| INV-222 | Hooli Packaging   | $5,880     |
| INV-223 | Stark Fasteners   | $1,105     |
| INV-224 | Wayne Industrial  | $6,340     |

**Held, do not pay:**

- INV-218 (Globex Freight, $1,540): Globex hold.
- INV-221 (Umbrella Logistics, $2,795): AP status is pending. This is not a Northwind invoice; that error was corrected earlier.
- INV-207 (Stark Fasteners, $3,305): AP status is pending.

## Next steps

1. Call `list_payments`.
   - If INV-216 appears, do **not** pay it again.
   - If it is absent and the connection is clearly healthy, pay INV-216 for $2,580.
   - If the connection is still down, send no payments and tell the user.
2. Re-run `list_invoices` and confirm every remaining invoice is still `approved` and its amount is unchanged. The run has been interrupted, so state may have changed.
3. Pay the six remaining invoices in order. After any timeout, check `list_payments` before continuing.
4. Finish with a `list_payments` reconciliation: each invoice should appear once at the correct amount. Then report to the user with a table, the totals, and the held items.

The last message told the user the run would resume once the connection was back, and asked them to say when to pick it up. If they haven't explicitly said to continue, briefly confirm before sending any payments.
