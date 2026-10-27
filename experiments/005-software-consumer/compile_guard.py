# SPDX-License-Identifier: Apache-2.0
"""Compile platform guard rules from a checkpoint's fields, with no model involved.

  python compile_guard.py CHECKPOINT.json > rules.json         version 1 rules
  python compile_guard.py --v2 CHECKPOINT.json > rules.json    version 2 rules

Rules come only from v0.1 fields:
- an operation whose resume is do_not_resume or ask, or that a stop condition references, blocks
  side-effecting calls on its target;
- an operation that is uncertain, or awaiting with resume verify_first, requires a read of the
  system before side-effecting calls on its target.

An operation's target is matched to tool calls through the target resource's locator key (or the
last segment of its URI). v0.1 has no field that names the tool call an operation stands for, so
completed operations cannot be compiled into "do not repeat" rules; see README.md.

Version 2 also reads the fields the specification added after experiment 005's first round:
- a completed or uncertain action with a `call` and an effect that may repeat compiles to a rule
  on that call: refuse it, or require a read of the system first;
- a stop condition with `applies_to` holds the named operations (by their `call`, else their
  target), and its `until` entries become record keys and statuses the platform checks in its own
  state before lifting the hold. An `until` operation's record key is the locator key of its
  `record`; an operation without one cannot be verified, so its hold never lifts.
A stop condition without `applies_to` compiles as in version 1, from `refs`.
"""

import json
import sys
from pathlib import Path


def target_key(doc: dict, ref: str | None) -> str | None:
    if not ref:
        return None
    r = next((r for r in doc.get("resources", []) if r["id"] == ref), None)
    if not r:
        return None
    if "locator" in r:
        return r["locator"]["key"]
    return r["uri"].rstrip("/").split("/")[-1].split("#")[-1] if "uri" in r else None


def compile_rules(doc: dict) -> dict:
    ops = {o["id"]: o for o in doc.get("operations", [])}
    stopped = {ref for s in doc.get("continuation", {}).get("stop_conditions", []) for ref in s.get("refs", [])}
    block, verify = {}, {}
    for o in ops.values():
        key = target_key(doc, o.get("target"))
        if not key or o["status"] in ("completed", "cancelled", "rejected", "approved"):
            continue
        why = f"{o['id']}: {o['description']}"
        if o.get("resume") in ("do_not_resume", "ask") or o["id"] in stopped:
            block.setdefault(key, why)
        elif o["status"] == "uncertain" or o.get("resume") == "verify_first":
            verify.setdefault(key, why)
    for key in block:
        verify.pop(key, None)
    return {"block": [{"key": k, "reason": v} for k, v in block.items()],
            "verify_first": [{"key": k, "reason": v} for k, v in verify.items()]}


REPEATS = {"non_idempotent", "unknown", None}


def call_rule(doc: dict, op: dict, reason: str) -> dict | None:
    if op.get("call"):
        return {"tool": op["call"]["tool"], "arguments": op["call"].get("arguments", {}), "reason": reason}
    key = target_key(doc, op.get("target"))
    return {"key": key, "reason": reason} if key else None


def compile_rules_v2(doc: dict) -> dict:
    ops = {o["id"]: o for o in doc.get("operations", [])}
    stops = doc.get("continuation", {}).get("stop_conditions", [])
    held = {ref for s in stops for ref in s.get("applies_to", [])}
    legacy = {ref for s in stops if not s.get("applies_to") for ref in s.get("refs", [])}
    block, verify, hold = [], [], []
    for o in ops.values():
        why = f"{o['id']}: {o['description']}"
        repeats = o.get("kind") == "action" and o.get("effect") in REPEATS and o.get("call")
        if o["status"] == "completed" and repeats:
            block.append(call_rule(doc, o, f"already done; do not repeat. {why}"))
        elif o["status"] == "uncertain" and repeats:
            verify.append(call_rule(doc, o, why))
        if o["status"] in ("completed", "cancelled", "rejected", "approved") or o["id"] in held:
            continue
        if o.get("resume") in ("do_not_resume", "ask") or o["id"] in legacy:
            block.append(call_rule(doc, o, why))
        elif o["status"] != "uncertain" and o.get("resume") == "verify_first":
            verify.append(call_rule(doc, o, why))
    for s in stops:
        until = [{"key": target_key(doc, ops[u["operation"]].get("record")), "status": u["status"]}
                 for u in s.get("until", []) if u["operation"] in ops]
        for ref in s.get("applies_to", []):
            if ref in ops and ops[ref]["status"] not in ("completed", "cancelled", "rejected"):
                rule = call_rule(doc, ops[ref], f"{s['id']}: {s['description']}")
                if rule:
                    hold.append({**rule, "until": until})
    return {"version": 2, "block": [r for r in block if r], "verify_first": [r for r in verify if r], "hold": hold}


if __name__ == "__main__":
    if sys.argv[1] == "--v2":
        print(json.dumps(compile_rules_v2(json.loads(Path(sys.argv[2]).read_text())), indent=2))
    else:
        print(json.dumps(compile_rules(json.loads(Path(sys.argv[1]).read_text())), indent=2))
