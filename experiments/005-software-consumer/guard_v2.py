# SPDX-License-Identifier: Apache-2.0
"""Apply version 2 guard rules (compile_guard.py --v2) to one tool call.

The live mock server and the offline replay both call refusal(), so they enforce the same rules.

A rule matches a call by `tool` and `arguments` when the tool names agree (ignoring a client's
prefix such as `mcp__server__`, or a `system.` qualifier) and every recorded argument has an equal
value; or, for a rule without a call, by `key` when any argument equals it. A hold lifts when every
`until` record has the required status in the platform's own state.
"""

from collections.abc import Callable
from typing import Any


def tool_name(name: str) -> str:
    return name.split("__")[-1].split(".")[-1]


def same(a: Any, b: Any) -> bool:
    if isinstance(a, int | float) and isinstance(b, int | float):
        return float(a) == float(b)
    return str(a) == str(b)


def matches(rule: dict, name: str, args: dict[str, Any]) -> bool:
    if "tool" in rule:
        return tool_name(rule["tool"]) == tool_name(name) and all(
            k in args and same(v, args[k]) for k, v in rule.get("arguments", {}).items()
        )
    return rule["key"] in {str(v) for v in args.values()}


def label(rule: dict) -> str:
    return rule.get("key") or f"{tool_name(rule['tool'])}({rule.get('arguments', {})})"


def refusal(rules: dict, name: str, args: dict[str, Any], verified: bool,
            status_of: Callable[[str], str | None]) -> str | None:
    for rule in rules.get("block", []):
        if matches(rule, name, args):
            return f"Blocked by the platform: {label(rule)}: {rule['reason']}"
    for rule in rules.get("hold", []):
        if matches(rule, name, args) and not (
            rule["until"] and all(u["key"] and status_of(u["key"]) == u["status"] for u in rule["until"])
        ):
            waiting = ", ".join(f"{u['key']} {u['status']}" for u in rule["until"]) or "never lifts"
            return f"Blocked by the platform until {waiting}: {rule['reason']}"
    for rule in rules.get("verify_first", []):
        if matches(rule, name, args) and not verified:
            return f"Blocked by the platform: {label(rule)} must be verified in the system first: {rule['reason']}"
    return None


def record_status(state: dict, key: str) -> str | None:
    """The status of record `key` in the platform's state: an item with that id and a status (an
    approval request), or a payment made for it, which the payment system reports as completed."""
    for value in state.values():
        for item in value if isinstance(value, list) else []:
            if isinstance(item, dict) and item.get("id") == key and "status" in item:
                return item["status"]
    if any(key in (p.get("invoice_id"), p.get("reference")) for p in state.get("payments", [])):
        return "completed"
    return None
