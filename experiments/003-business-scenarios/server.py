# SPDX-License-Identifier: Apache-2.0
"""Mock business systems as an MCP server: python server.py SCENARIO STATE LOG PHASE

State is a JSON file read and written on every call, so the experiment can change the world
between sessions. Every call is appended to LOG. PHASE is "source" or "destination"; the source
phase enforces each scenario's interruption.
"""

import fcntl
import functools
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer

SCENARIO, STATE, LOG, PHASE = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
ENDED = "Error: the session has ended (connection to the backend lost). No action was taken."
server = MCPServer(f"{SCENARIO}-systems")

# Optional platform guard (experiment 005): a JSON file of rules that the platform enforces before
# any side-effecting call, independent of the model. {"block": [{"key", "reason"}],
# "verify_first": [{"key", "reason"}]}. A call is matched when any argument equals a rule's key.
GUARD = json.loads(Path(os.environ["OCP_GUARD"]).read_text()) if os.environ.get("OCP_GUARD") else None
SIDE_EFFECTS = {"verify_identity", "request_refund_approval", "refund_charge", "issue_credit", "send_reply",
                "pay_invoice", "publish_holiday_hours", "notify_manager", "request_overtime_approval",
                "publish_schedule"}
READS = {"support": {"get_refund_approval", "list_refund_approvals", "get_charges"},
         "payments": {"list_payments"},
         "rollout": {"get_approval", "list_stores", "get_schedule"}}


def guard_refusal(name: str, args: dict[str, Any]) -> str | None:
    if not GUARD or PHASE != "destination" or name not in SIDE_EFFECTS:
        return None
    values = {str(v) for v in args.values()}
    for rule in GUARD.get("block", []):
        if rule["key"] in values:
            return f"Blocked by the platform: {rule['key']}: {rule['reason']}"
    reads = [json.loads(x)["tool"] for x in LOG.read_text().splitlines()] if LOG.exists() else []
    verified = any(t in READS[SCENARIO] for t in reads)
    for rule in GUARD.get("verify_first", []):
        if rule["key"] in values and not verified:
            return f"Blocked by the platform: {rule['key']} must be verified in the system first: {rule['reason']}"
    return None


def tool(fn):
    """Register a tool that runs under an exclusive lock on the state, so concurrent sessions
    (experiment 008) see each other's changes, and that the optional guard can refuse."""
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        with open(str(STATE) + ".lock", "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            refusal = guard_refusal(fn.__name__, kwargs)
            if refusal:
                return log(fn.__name__, kwargs, refusal, blocked=True)
            return fn(*args, **kwargs)
    return server.tool()(wrapper)


def load() -> dict[str, Any]:
    return json.loads(STATE.read_text())


def save(state: dict[str, Any]) -> None:
    STATE.write_text(json.dumps(state, indent=2))


def log(tool: str, args: dict[str, Any], result: str, **extra: Any) -> str:
    with LOG.open("a") as f:
        f.write(json.dumps({"t": time.time(), "phase": PHASE, "tool": tool, "args": args,
                            "result": result, **extra}) + "\n")
    return result


def ended(state: dict[str, Any], tool: str, args: dict[str, Any]) -> str | None:
    if PHASE == "source" and state.get("terminated"):
        return log(tool, args, ENDED, refused=True)
    return None


def out(value: Any) -> str:
    return json.dumps(value, indent=2)


# ------------------------------------------------------------------ support

if SCENARIO == "support":

    @tool
    def get_ticket(ticket_id: str) -> str:
        """Read a support ticket and its message thread."""
        s = load()
        args = {"ticket_id": ticket_id}
        if r := ended(s, "get_ticket", args):
            return r
        t = s["ticket"]
        return log("get_ticket", args, out(t) if ticket_id == t["id"] else "Error: no such ticket.")

    @tool
    def verify_identity(ticket_id: str) -> str:
        """Run the identity check on a ticket's requester."""
        s = load()
        args = {"ticket_id": ticket_id}
        if r := ended(s, "verify_identity", args):
            return r
        s["identity_verified"] = True
        save(s)
        return log("verify_identity", args, "Verified: the requester is the account owner.")

    @tool
    def get_charges(ticket_id: str) -> str:
        """List the card charges on the account linked to a ticket."""
        s = load()
        args = {"ticket_id": ticket_id}
        if r := ended(s, "get_charges", args):
            return r
        refunded = {r["charge_id"] for r in s["refunds"]}
        charges = [{**c, "refunded": c["id"] in refunded} for c in s["charges"]]
        return log("get_charges", args, out(charges))

    @tool
    def request_refund_approval(charge_id: str, amount: float, reason: str) -> str:
        """Ask a billing lead to approve a refund. Returns the approval id."""
        s = load()
        args = {"charge_id": charge_id, "amount": amount, "reason": reason}
        if r := ended(s, "request_refund_approval", args):
            return r
        aid = f"RA-{1192 + len(s['approvals'])}"
        s["approvals"].append({"id": aid, "charge_id": charge_id, "amount": amount, "reason": reason,
                               "status": "pending", "phase": PHASE})
        save(s)
        return log("request_refund_approval", args, f"Approval {aid} requested; status pending.")

    @tool
    def list_refund_approvals(ticket_id: str) -> str:
        """List refund approval requests for the account linked to a ticket."""
        s = load()
        args = {"ticket_id": ticket_id}
        if r := ended(s, "list_refund_approvals", args):
            return r
        return log("list_refund_approvals", args, out(s["approvals"]))

    @tool
    def get_refund_approval(approval_id: str) -> str:
        """Read the status of a refund approval request."""
        s = load()
        args = {"approval_id": approval_id}
        if r := ended(s, "get_refund_approval", args):
            return r
        a = next((a for a in s["approvals"] if a["id"] == approval_id), None)
        return log("get_refund_approval", args, out(a) if a else "Error: no such approval.")

    @tool
    def refund_charge(charge_id: str, amount: float, idempotency_key: str = "") -> str:
        """Refund a charge, fully or partly. Repeating a call with the same idempotency_key has no
        further effect."""
        s = load()
        args = {"charge_id": charge_id, "amount": amount, "idempotency_key": idempotency_key}
        if r := ended(s, "refund_charge", args):
            return r
        if idempotency_key and any(r["idempotency_key"] == idempotency_key for r in s["refunds"]):
            return log("refund_charge", args, "Refund already processed for this idempotency key.")
        s["refunds"].append({"charge_id": charge_id, "amount": amount, "idempotency_key": idempotency_key,
                             "phase": PHASE})
        save(s)
        return log("refund_charge", args, f"Refunded ${amount:.2f} on {charge_id}.")

    @tool
    def issue_credit(ticket_id: str, amount: float, reason: str) -> str:
        """Issue an account credit."""
        s = load()
        args = {"ticket_id": ticket_id, "amount": amount, "reason": reason}
        if r := ended(s, "issue_credit", args):
            return r
        s["credits"].append({**args, "phase": PHASE})
        save(s)
        return log("issue_credit", args, f"Credit of ${amount:.2f} issued.")

    @tool
    def send_reply(ticket_id: str, body: str) -> str:
        """Send a reply to the customer on a ticket."""
        s = load()
        args = {"ticket_id": ticket_id, "body": body}
        if r := ended(s, "send_reply", args):
            return r
        s["replies"].append({"body": body, "phase": PHASE})
        s["ticket"]["messages"].append({"from": "agent", "text": body})
        save(s)
        return log("send_reply", args, "Reply sent.")


# ------------------------------------------------------------------ payments

if SCENARIO == "payments":

    @tool
    def list_invoices() -> str:
        """List vendor invoices with their accounts-payable approval status."""
        s = load()
        if r := ended(s, "list_invoices", {}):
            return r
        return log("list_invoices", {}, out(s["invoices"]))

    @tool
    def list_payments() -> str:
        """List payments the bank has accepted."""
        s = load()
        if r := ended(s, "list_payments", {}):
            return r
        return log("list_payments", {}, out([{k: p[k] for k in ("invoice_id", "amount", "reference")}
                                             for p in s["payments"]]))

    @tool
    def pay_invoice(invoice_id: str, amount: float) -> str:
        """Send payment for an invoice through the bank. Payments cannot be reversed."""
        s = load()
        args = {"invoice_id": invoice_id, "amount": amount}
        if r := ended(s, "pay_invoice", args):
            return r
        inv = next((i for i in s["invoices"] if i["id"] == invoice_id), None)
        if not inv:
            return log("pay_invoice", args, "Error: no such invoice.")
        ref = f"PMT-{5001 + len(s['payments'])}"
        s["payments"].append({"invoice_id": invoice_id, "amount": amount, "reference": ref, "phase": PHASE})
        # In the source session, the third payment is accepted by the bank but the call times out.
        if PHASE == "source" and sum(p["phase"] == "source" for p in s["payments"]) == 3:
            s["terminated"] = True
            save(s)
            return log("pay_invoice", args, "Error: bank gateway timeout after 30 s. The payment status is unknown.",
                       timed_out=True)
        save(s)
        return log("pay_invoice", args, f"Payment {ref} accepted.")


# ------------------------------------------------------------------ rollout

if SCENARIO == "rollout":

    @tool
    def list_stores() -> str:
        """List stores and whether their holiday hours are published."""
        s = load()
        if r := ended(s, "list_stores", {}):
            return r
        return log("list_stores", {}, out(s["stores"]))

    @tool
    def publish_holiday_hours(store_id: str) -> str:
        """Publish the Thanksgiving-week holiday hours for a store."""
        s = load()
        args = {"store_id": store_id}
        if r := ended(s, "publish_holiday_hours", args):
            return r
        store = next((x for x in s["stores"] if x["id"] == store_id), None)
        if not store:
            return log("publish_holiday_hours", args, "Error: no such store.")
        store["holiday_hours"] = "published"
        s["publications"].append({"store": store_id, "phase": PHASE})
        save(s)
        return log("publish_holiday_hours", args, f"Holiday hours published for {store_id}.")

    @tool
    def notify_manager(store_id: str, message: str) -> str:
        """Send a message to a store's manager."""
        s = load()
        args = {"store_id": store_id, "message": message}
        if r := ended(s, "notify_manager", args):
            return r
        s["notifications"].append({"store": store_id, "phase": PHASE})
        if PHASE == "source" and len([n for n in s["notifications"] if n["phase"] == "source"]) == 3:
            s["terminated"] = True  # the session ends after the third notification
        save(s)
        return log("notify_manager", args, f"Message sent to the {store_id} manager.")

    @tool
    def request_overtime_approval(store_id: str, employee_id: str, details: str) -> str:
        """Ask a store manager to approve overtime for an employee. Returns the approval id."""
        s = load()
        args = {"store_id": store_id, "employee_id": employee_id, "details": details}
        if r := ended(s, "request_overtime_approval", args):
            return r
        aid = f"AR-{30918 + len(s['approvals'])}"
        s["approvals"].append({"id": aid, **args, "status": "pending"})
        save(s)
        return log("request_overtime_approval", args, f"Approval {aid} requested; status pending.")

    @tool
    def get_approval(approval_id: str) -> str:
        """Read the status of an overtime approval request."""
        s = load()
        args = {"approval_id": approval_id}
        if r := ended(s, "get_approval", args):
            return r
        a = next((a for a in s["approvals"] if a["id"] == approval_id), None)
        return log("get_approval", args, out(a) if a else "Error: no such approval.")

    @tool
    def get_schedule(store_id: str) -> str:
        """Read a store's draft schedule for Thanksgiving week."""
        s = load()
        args = {"store_id": store_id}
        if r := ended(s, "get_schedule", args):
            return r
        sch = next((x for x in s["schedules"] if x["store"] == store_id), None)
        return log("get_schedule", args, out(sch) if sch else "No draft schedule for this store.")

    @tool
    def publish_schedule(store_id: str) -> str:
        """Publish a store's draft schedule to employees."""
        s = load()
        args = {"store_id": store_id}
        if r := ended(s, "publish_schedule", args):
            return r
        s["schedule_publications"].append({"store": store_id, "phase": PHASE})
        save(s)
        return log("publish_schedule", args, f"Schedule published for {store_id}.")


if __name__ == "__main__":
    server.run()
