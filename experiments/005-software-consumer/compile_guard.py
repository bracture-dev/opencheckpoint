# SPDX-License-Identifier: Apache-2.0
"""Compile platform guard rules from a checkpoint's fields, with no model involved.

  python compile_guard.py CHECKPOINT.json > rules.json

Rules come only from v0.1 fields:
- an operation whose resume is do_not_resume or ask, or that a stop condition references, blocks
  side-effecting calls on its target;
- an operation that is uncertain, or awaiting with resume verify_first, requires a read of the
  system before side-effecting calls on its target.

An operation's target is matched to tool calls through the target resource's locator key (or the
last segment of its URI). v0.1 has no field that names the tool call an operation stands for, so
completed operations cannot be compiled into "do not repeat" rules; see README.md.
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


if __name__ == "__main__":
    print(json.dumps(compile_rules(json.loads(Path(sys.argv[1]).read_text())), indent=2))
