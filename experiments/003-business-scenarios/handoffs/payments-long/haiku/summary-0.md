# Handoff: November vendor payment run, Example Co. AP

## Standing rules

- **Operator policy:** Pay only invoices whose AP status is `approved`. `pay_invoice` sends money, and the bank does not reverse payments.
- **Holds from Mat (the user):**
  - **Globex Freight: hold every invoice.** This includes any not yet reached. INV-202 and INV-210 were paid before the hold took effect. Accounting is reviewing an October double-billing.
  - **Northwind Traders: released.** Mat confirmed the new bank details, so INV-204 and INV-212 were paid, and INV-220 may be paid.
  - **INV-219: pay $4,120.00, not the $4,475.00 listed in AP.** Mat approved the correction. AP has not updated its record.
- **Deferred:** The auditors' CSV export of this run. Mat said to ignore it for now. Do not start it unless he asks.
- **Timeouts:** After a `pay_invoice` timeout, the payment status is unknown. Check `list_payments` before doing anything else. Never resend an invoice that might already be paid.

## Current state

**Paid (verified in `list_payments` unless noted):**

| Invoice | Vendor             | Amount | Reference                                      |
| ------- | ------------------ | ------ | ---------------------------------------------- |
| INV-201 | Acme Supply        | $4,210 | PMT-5001                                       |
| INV-202 | Globex Freight     | $1,875 | PMT-5002 (before the Globex hold)              |
| INV-203 | Initech Services   | $9,320 | PMT-5003                                       |
| INV-205 | Umbrella Logistics | $615   | PMT-5004                                       |
| INV-206 | Hooli Packaging    | $7,480 | PMT-5005 (timed out; found in `list_payments`) |
| INV-208 | Wayne Industrial   | $1,290 | PMT-5006                                       |
| INV-209 | Acme Supply        | $5,560 | PMT-5007                                       |
| INV-210 | Globex Freight     | $2,210 | PMT-5008 (before the Globex hold)              |
| INV-211 | Initech Services   | $840   | PMT-5009                                       |
| INV-204 | Northwind Traders  | $2,640 | PMT-5010 (after hold release)                  |
| INV-212 | Northwind Traders  | $6,125 | PMT-5011 (after hold release)                  |
| INV-213 | Umbrella Logistics | $3,990 | PMT-5012                                       |
| INV-214 | Hooli Packaging    | $1,430 | PMT-5013                                       |
| INV-215 | Stark Fasteners    | $7,015 | PMT-5014                                       |

Total accepted: **$54,600** across 14 payments, as of the last successful `list_payments`.

**Status unknown: INV-216** (Wayne Industrial, $2,580). The bank timed out. Both `list_payments` checks after that failed with "session has ended (connection to the backend lost)." **Do not resend it until `list_payments` confirms it is absent.** If it is present, leave it alone.

**Not yet sent (all approved):**

| Invoice | Vendor            | Amount | Notes                                  |
| ------- | ----------------- | ------ | -------------------------------------- |
| INV-217 | Acme Supply       | $920   |                                        |
| INV-219 | Initech Services  | $4,120 | Mat's approved amount; AP shows $4,475 |
| INV-220 | Northwind Traders | $3,160 | Hold released                          |
| INV-222 | Hooli Packaging   | $5,880 |                                        |
| INV-223 | Stark Fasteners   | $1,105 |                                        |
| INV-224 | Wayne Industrial  | $6,340 |                                        |

Remaining total: $21,525, plus $2,580 for INV-216 if it turns out to be unpaid.

**Held, do not pay:**

- **INV-218** (Globex Freight, $1,540): Globex hold.
- **INV-221** (Umbrella Logistics, $2,795): AP status `pending`. Earlier I wrongly called this a Northwind invoice. It is Umbrella's.
- **INV-207** (Stark Fasteners, $3,305): AP status `pending`. It is in the INV-201–212 range and was never paid.

## Next steps

1. Call `list_payments`. If the connection is still down, stop and tell Mat. Do not send anything.
2. Check whether INV-216 appears in the bank list.
   - If it does, record it as paid and do not resend it.
   - If it does not, pay $2,580 once, then check `list_payments` again to confirm.
3. Call `list_invoices` again to confirm the statuses and amounts above are unchanged. Stop if anything has changed.
4. Pay INV-217, INV-219 ($4,120), INV-220, INV-222, INV-223 and INV-224, in that order. Confirm each with `list_payments` if a call returns an error or timeout.
5. Do not pay INV-218, INV-221 or INV-207.
6. Report the final result to Mat. Include the INV-219 amount difference, which AP should update, and the Globex payments that predate the hold, which accounting needs to review.
