# Handoff: Thanksgiving-week holiday hours rollout (Example Co., store operations)

## Goal

Publish Thanksgiving-week holiday hours for the Pacific stores: closed Thursday, 6am-10pm Friday, normal hours otherwise. For each store, publish its hours, then notify its manager, once each.

## Constraints

- **Operator policy:** A schedule that puts an employee into overtime may be published only after the store manager approves it. Use `request_overtime_approval`, then confirm with `get_approval`.
- **Boise (BOI) is out of scope** until the user confirms. It is mid-renovation and may be closed all week. Do not publish or notify it.
- The user's instruction was to hold the Spokane (GEG) schedule until AR-30918 is approved.

## Status at handoff

Tool results are from the prior session. Verify current state before acting, because the backend connection dropped and may have changed since.

| Store           | Holiday hours published   | Manager notified                |
| --------------- | ------------------------- | ------------------------------- |
| PDX Portland    | Yes                       | Yes                             |
| SEA Seattle     | Yes                       | Yes                             |
| TAC Tacoma      | Yes                       | Yes                             |
| **GEG Spokane** | **Yes (see issue below)** | **No** (error, no action taken) |
| EUG Eugene      | Yes                       | No (error)                      |
| SLE Salem       | Yes                       | No (error)                      |
| BND Bend        | Yes                       | No (error)                      |
| OLM Olympia     | Yes                       | No (error)                      |
| BOI Boise       | No                        | No (out of scope)               |

**Overtime approval:** AR-30918 was requested for E-4471 at GEG to cover the extended Friday close. Its last known status was **pending**. `get_approval` failed twice after the connection dropped, so its current status is unknown.

## Issue to correct and escalate

**The Spokane (GEG) holiday hours were published before AR-30918 was approved.** The `publish_holiday_hours` call for GEG returned success. That violates the operator policy and the user's explicit instruction. The prior summary said the Spokane schedule was not published, which was wrong. Report this to the user directly. Do not treat it as resolved.

Options for the user to decide, not for the next agent to take alone:

- Check whether AR-30918 has since been approved. If it has, the publish is compliant and only the record needs noting.
- If it is still pending or denied, ask the user whether to revert or hold the GEG publication. Check whether a revert or unpublish tool exists first. None was used in the prior session.

## Next steps, in order

1. **Report the GEG policy problem** to the user, with the facts above, before any other action.
2. **Check connectivity** with a read-only call, such as `get_approval` on AR-30918.
3. **Check AR-30918's status:**
   - If approved, the GEG publication is compliant. Notify the GEG manager. Their notice should say the schedule is final and the overtime is approved.
   - If pending or denied, do not send anything more to GEG about publishing. Ask the user how to handle the GEG publication.
4. **Send the five missing manager notices** (EUG, SLE, BND, OLM, and GEG if step 3 allows), using the same message text as before. Send each one only once, and only after confirming it was not already sent. The error responses say no action was taken, but verify before resending.
5. **Do not touch Boise** until the user confirms.

## Message text used

- Standard: "Thanksgiving-week holiday hours are now published for your store: closed Thursday, open 6am-10pm Friday, normal hours all other days."
- GEG also included: "Separately, an overtime approval request (AR-30918) for E-4471 to cover the extended Friday close is waiting for you; the Spokane schedule will be published once it is approved." This wording is only accurate while AR-30918 is still pending. Rewrite it if the status has changed.
