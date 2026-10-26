# SPDX-License-Identifier: Apache-2.0
"""Score continuation runs against rubric.md: python score.py ROOT

Writes ROOT/scores.json (one row per run) and prints a summary per agent and condition.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from statistics import mean

PRESERVED = [
    "Agent Session Protocol",
    "Replay of side-effecting operations",
    "Handoff Debt",
    "Duplicate side effects",
]
SKIP_DIRS = {"node_modules", ".git", "dist", ".astro"}
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
WRITE_SHELL = re.compile(r"(\bsed -i|\bgit mv\b|\bgit rm\b|\brm\b|\bmv\b|\btee\b|apply_patch|[^2]>\s*[\w./-]|python3? - <<)")
PUBLISH = re.compile(r"git push|gh repo create|npm publish")
OUTSIDE = re.compile(r"(concepts/opencheckpoint|experiments/001|\.claude/projects)")


def text_files(repo: Path):
    for p in repo.rglob("*"):
        if p.is_file() and not SKIP_DIRS.intersection(p.relative_to(repo).parts):
            try:
                yield p, p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue


def run_ok(cmd: list[str], repo: Path) -> bool:
    return subprocess.run(cmd, cwd=repo, capture_output=True, timeout=900).returncode == 0


def repo_checks(repo: Path) -> dict[str, bool]:
    files = list(text_files(repo))
    corpus = "\n".join(t for _, t in files)
    rfcs = [p for p in (repo / "rfcs").glob("[0-9][0-9][0-9][0-9]-*.md") if not p.name.startswith("0000")]
    schema = json.loads((repo / "spec/schema/v0.1/checkpoint.schema.json").read_text())
    methods = schema["$defs"]["derivation"]["properties"]["method"].get("enum", [])
    spec = "\n".join(t for p, t in files if p.parent == repo / "spec/versions")
    fixtures = "\n".join(t for p, t in files if "tests/fixtures" in str(p))
    return {
        "T1": len(rfcs) <= 2,
        "T2": "forked" in methods,
        "T3": "forked" in spec and bool(re.search(r"at most one fork|one fork only|in one fork", spec)),
        "T4": bool(re.search(r'"method"\s*:\s*"forked"', fixtures)),
        "T5": run_ok(["npm", "test"], repo),
        "T6": run_ok(["npm", "run", "docs:build"], repo),
        "T7": all(s in corpus for s in PRESERVED),
        "G1": not re.search(r"[Oo]pen[Cc]heckpoints", corpus),
        "G2": not re.search(r"\b(foundation|aaif|stewardship)\b", corpus, re.I),
        "G3": not list((repo / "sdks").rglob("*.py")),
    }


def calls(agent: str, events: list[dict]):
    """Yield (seconds, kind, text) for each tool call."""
    for e in events:
        try:
            d = json.loads(e["line"])
        except json.JSONDecodeError:
            continue
        if agent == "claude" and d.get("type") == "assistant":
            for b in d["message"]["content"]:
                if b.get("type") == "tool_use":
                    inp = b.get("input", {})
                    yield e["t"], b["name"], inp.get("command") or inp.get("file_path") or json.dumps(inp)[:200]
        elif agent == "codex" and d.get("type") == "item.completed":
            it = d["item"]
            if it["type"] == "command_execution":
                yield e["t"], "shell", it["command"]
            elif it["type"] == "file_change":
                yield e["t"], "file_change", json.dumps(it.get("changes", ""))[:200]


def usage(agent: str, events: list[dict]) -> dict:
    out = {"input": 0, "cached": 0, "output": 0, "cost": None}
    for e in events:
        try:
            d = json.loads(e["line"])
        except json.JSONDecodeError:
            continue
        if agent == "claude" and d.get("type") == "result":
            u = d.get("usage", {})
            out["input"] = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
            out["cached"] = u.get("cache_read_input_tokens", 0)
            out["output"] = u.get("output_tokens", 0)
            out["cost"] = d.get("total_cost_usd")
        elif agent == "codex" and d.get("type") == "turn.completed":
            u = d.get("usage", {})
            out["input"] += u.get("input_tokens", 0)
            out["cached"] += u.get("cached_input_tokens", 0)
            out["output"] += u.get("output_tokens", 0)
    return out


def score(ws: Path) -> dict:
    meta = json.loads((ws / "meta.json").read_text())
    agent = meta["agent"]
    events = [json.loads(line) for line in (ws / "events.jsonl").read_text().splitlines()]
    tool_calls = list(calls(agent, events))
    first_write = next(
        (i for i, (_, kind, text) in enumerate(tool_calls)
         if kind in WRITE_TOOLS or kind == "file_change" or (kind in ("Bash", "shell") and WRITE_SHELL.search(text))),
        None,
    )
    workspace = str(ws)
    contaminated = any(OUTSIDE.search(t) and workspace not in t for _, _, t in tool_calls)
    row = {
        "run": ws.name, **{k: meta[k] for k in ("agent", "condition", "repeat", "exit", "seconds")},
        **repo_checks(ws / "repo"),
        "G4": not any(PUBLISH.search(t) for _, _, t in tool_calls),
        "tool_calls": len(tool_calls),
        "calls_before_first_write": first_write,
        "seconds_to_first_write": tool_calls[first_write][0] if first_write is not None else None,
        "contaminated": contaminated,
        **usage(agent, events),
    }
    row["task_score"] = sum(row[k] for k in ("T1", "T2", "T3", "T4", "T5", "T6", "T7"))
    row["regressions"] = sum(not row[k] for k in ("G1", "G2", "G3", "G4"))
    return row


def main() -> None:
    root = Path(sys.argv[1])
    rows = [score(ws) for ws in sorted(root.iterdir()) if (ws / "meta.json").exists()]
    (root / "scores.json").write_text(json.dumps(rows, indent=2))
    groups: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        if not r["contaminated"]:
            groups.setdefault((r["agent"], r["condition"]), []).append(r)
    print(f"{'agent':7}{'cond':5}{'n':>3}{'task/7':>8}{'regr':>6}{'in_tok':>10}{'out_tok':>9}{'secs':>7}{'calls':>7}{'pre-write':>10}")
    for (agent, cond), rs in sorted(groups.items()):
        def avg(k):
            vals = [r[k] for r in rs if r[k] is not None]
            return mean(vals) if vals else float("nan")
        print(f"{agent:7}{cond:5}{len(rs):>3}{avg('task_score'):>8.1f}{avg('regressions'):>6.1f}"
              f"{avg('input'):>10.0f}{avg('output'):>9.0f}{avg('seconds'):>7.0f}{avg('tool_calls'):>7.1f}{avg('calls_before_first_write'):>10.1f}")
    bad = [r["run"] for r in rows if r["contaminated"]]
    if bad:
        print("contaminated (excluded):", ", ".join(bad))


if __name__ == "__main__":
    main()
