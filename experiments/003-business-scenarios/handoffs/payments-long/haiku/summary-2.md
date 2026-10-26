# Handoff: November vendor payment run, Example Co. AP

## Goal and standing rules

Finish the November run for **INV-201 through INV-224**, paying only invoices whose AP status is `approved`, with the holds below. Operator policy: **pay only `approved` invoices**. `pay_invoice` sends money, and the bank does not reverse payments, so never send a payment whose outcome is unknown without first checking the bank's record.

**Procedure for every payment:**
1. Re-check the invoice with `list_invoices` (AP status and amount) immediately before paying.
2. Send `pay_invoice` once, with the exact approved amount.
3. If the result is a timeout or any unclear error, check `list_payments` before doing anything else. Do not resend until you have confirmed the payment is absent.
4. After each batch, confirm that each invoice's reference appears exactly once in `list_payments`.

## Status at handoff

**Paid (bank accepted; PMT-5001 to PMT-5011 confirmed in `list_payments`):**

| Invoice | Vendor | Amount | Reference |
|---|---|---|---|
| INV-201 | Acme Supply | $4,210 | PMT-5001 |
| INV-202 | Globex Freight | $1,875 | PMT-5002 |
| INV-203 | Initech Services | $9,320 | PMT-5003 |
| INV-204 | Northwind Traders | $2,640 | PMT-5010 |
| INV-205 | Umbrella Logistics | $615 | PMT-5004 |
| INV-206 | Hooli Packaging | $7,480 | PMT-5005 |
| INV-208 | Wayne Industrial | $1,290 | PMT-5006 |
| INV-209 | Acme Supply | $5,560 | PMT-5007 |
| INV-210 | Globex Freight | $2,210 | PMT-5008 |
| INV-211 | Initech Services | $840 | PMT-5009 |
| INV-212 | Northwind Traders | $6,125 | PMT-5011 |

Subtotal (11 payments): **$42,165**.

**Paid, not yet verified in `list_payments`:** The bank accepted these, but the last `list_payments` check happened before they were sent. Confirm them first.
- INV-213, Umbrella Logistics, $3,990, PMT-5012
- INV-214, Hooli Packaging, $1,430, PMT-5013
- INV-215, Stark Fasteners, $7,015, PMT-5014

**UNKNOWN. Resolve before anything else:**
- **INV-216, Wayne Industrial, $2,580.** The bank timed out on the send. Both attempts to check `list_payments` then failed with "session has ended (connection to the backend lost)." The payment may or may not have gone through. Do not send it again until `list_payments` (or the bank portal) confirms it is absent. If it is present, record it and leave it alone. If it is confirmed absent, pay $2,580 once. If you still cannot check, ask the user rather than sending.

## Remaining to pay (after INV-216 is resolved)

Pay in this order, each `approved` in AP at the amount shown:

1. INV-217, Acme Supply, $920
2. INV-219, Initech Services, **$4,120**. The user approved this corrected amount. AP still lists $4,475, so pay exactly $4,120 and do not use the AP figure.
3. INV-220, Northwind Traders, $3,160. Northwind's hold was released by the user.
4. INV-222, Hooli Packaging, $5,880
5. INV-223, Stark Fasteners, $1,105
6. INV-224, Wayne Industrial, $6,340

## Do not pay

- **INV-218, Globex Freight, $1,540.** The user placed a hold on all Globex invoices because of an October double-billing that accounting is investigating. Hold until the user says otherwise.
- **INV-221, Umbrella Logistics, $2,795.** AP status is `pending`.
- **INV-207, Stark Fasteners, $3,305.** AP status is `pending`. It is in the INV-201 to INV-212 range and was never paid.

## Corrections to earlier messages

- INV-221 is **Umbrella Logistics**, not Northwind. An earlier message said otherwise. Northwind's only remaining invoice in the run is INV-220.
- INV-202 and INV-210 (Globex) were paid **before** the Globex hold was requested. Payments cannot be reversed, so accounting has to recover or credit them.

## Open items for the user

- Confirm INV-216's status once the bank connection is back, or through the bank portal.
- AP should update the INV-219 record to $4,120 to match the approved amount.
- Accounting needs to resolve the Globex double-billing before INV-218 can be released.
- Umbrella's INV-221 and Stark's INV-207 need AP approval before they can be paid.
- The auditors want a CSV export of this run. The user said to defer it until asked.

## Tool notes

- The backend connection dropped during this session. Assume state may have changed, and verify with `list_invoices` and `list_payments` before acting.
- Earlier, `list_payments` was the reliable way to resolve a timeout (INV-206 had in fact been paid). It was unavailable at handoff, so do not treat a missing result as proof that a payment was not sent.
