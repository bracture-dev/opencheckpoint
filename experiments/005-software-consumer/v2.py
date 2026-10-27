# SPDX-License-Identifier: Apache-2.0
"""Experiment 005, version 2: the same guard after the format gained `call`, `applies_to`, and `until`.

  python v2.py handoffs [SCENARIO...]
                           Opus writes a new checkpoint per scenario from the unchanged source
                           transcript, with the current specification and schema. Each attempt is
                           kept in handoff-meta.json; rerun a scenario whose checkpoint is invalid.
  python v2.py compile     version 1 and version 2 rules from each new checkpoint
  python v2.py replay      replay experiment 003 and 004 runs through the v1 rules from 003's
                           checkpoints and the v1 and v2 rules from the new ones

Live runs use experiment 003's pipeline with a version 2 rule file:
  python ../003-business-scenarios/pipeline.py run AGENT SCENARIO A REPEAT --root runs-v2 \\
      --guard rules-v2/SCENARIO/compiled-v2.json --tag=+compiled-v2
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EXP / "003-business-scenarios"))
import guard_v2  # noqa: E402
import pipeline  # noqa: E402
from compile_guard import compile_rules, compile_rules_v2  # noqa: E402
from replay import READS, SCENARIOS, SIDE_EFFECTS, harmful, run_logs  # noqa: E402

HANDOFFS = HERE / "handoffs-v2"
RULES = HERE / "rules-v2"
# One producer error, corrected for a separate, labeled rule set: Opus pointed the uncertain
# INV-103 payment's `record` at the payment-list tool, which no system can report a status for.
# The payment's record is the payment for invoice INV-103.
CORRECTIONS = {"payments": {"op-pay-103": {"record": "res-inv-103"}}}


def cmd_handoffs(*only: str) -> None:
    spec = (pipeline.REPO / "spec/versions/v0.1.md").read_text()
    schema = (pipeline.REPO / "spec/schema/v0.1/checkpoint.schema.json").read_text()
    prompt = (EXP / "003-business-scenarios/prompts/producer-checkpoint.md").read_text()
    for s in only or SCENARIOS:
        transcript = (EXP / "003-business-scenarios/handoffs" / s / "transcript.md").read_text()
        c = pipeline.produce(prompt, f"{transcript}\n\n=== SPECIFICATION ===\n\n{spec}\n\n=== JSON SCHEMA ===\n\n{schema}")
        d = HANDOFFS / s
        d.mkdir(parents=True, exist_ok=True)
        (d / "checkpoint.json").write_text(json.dumps(json.loads(pipeline.strip_fences(c["result"])), indent=2,
                                                      ensure_ascii=False) + "\n")
        attempt = {"capture": pipeline.capture(c), "validation": pipeline.validate(d / "checkpoint.json")}
        meta_path = d / "handoff-meta.json"
        attempts = json.loads(meta_path.read_text())["attempts"] if meta_path.exists() else []
        meta_path.write_text(json.dumps({"attempts": [*attempts, attempt]}, indent=2) + "\n")
        print(s, attempt["validation"]["level"], attempt["capture"])


def cmd_compile(*_: str) -> None:
    for s in SCENARIOS:
        doc = json.loads((HANDOFFS / s / "checkpoint.json").read_text())
        (RULES / s).mkdir(parents=True, exist_ok=True)
        (RULES / s / "compiled-v1.json").write_text(json.dumps(compile_rules(doc), indent=2) + "\n")
        (RULES / s / "compiled-v2.json").write_text(json.dumps(compile_rules_v2(doc), indent=2) + "\n")
        if s in CORRECTIONS:
            for o in doc["operations"]:
                o.update(CORRECTIONS[s].get(o["id"], {}))
            (RULES / s / "compiled-v2-corrected.json").write_text(json.dumps(compile_rules_v2(doc), indent=2) + "\n")


def refused_v1(rules: dict, scenario: str, call: dict, history: list[dict]) -> bool:
    values = {str(v) for v in call["args"].values()}
    if any(r["key"] in values for r in rules.get("block", [])):
        return True
    verified = any(c["tool"] in READS[scenario] for c in history)
    return any(r["key"] in values for r in rules.get("verify_first", [])) and not verified


def cmd_replay(*_: str) -> None:
    rows = []
    for s in SCENARIOS:
        source_log = [json.loads(x) for x in (EXP / "003-business-scenarios/handoffs" / s / "source-log.jsonl").read_text().splitlines()]
        state = json.loads((EXP / "003-business-scenarios/handoffs" / s / "handoff-state.json").read_text())
        rule_sets = {
            "v1 rules, 003 checkpoint": json.loads((HERE / "rules" / s / "compiled--opus-checkpoint.json").read_text()),
            "v1 rules, new checkpoint": json.loads((RULES / s / "compiled-v1.json").read_text()),
            "v2 rules, new checkpoint": json.loads((RULES / s / "compiled-v2.json").read_text()),
        }
        if (RULES / s / "compiled-v2-corrected.json").exists():
            rule_sets["v2 rules, record corrected"] = json.loads((RULES / s / "compiled-v2-corrected.json").read_text())
        for exp, m, log in run_logs():
            if m["scenario"] != s:
                continue
            calls = [c for c in log if c["phase"] == "destination"]
            for name, rules in rule_sets.items():
                h_total = h_blocked = l_total = l_blocked = 0
                for i, c in enumerate(calls):
                    if c["tool"] not in SIDE_EFFECTS:
                        continue
                    history = calls[:i]
                    bad = harmful(s, c, history, source_log)
                    if name.startswith("v2"):
                        verified = any(h["tool"] in READS[s] for h in history)
                        hit = guard_v2.refusal(rules, c["tool"], c["args"], verified,
                                               lambda key: guard_v2.record_status(state, key)) is not None
                    else:
                        hit = refused_v1(rules, s, c, history)
                    h_total += bad
                    h_blocked += bad and hit
                    l_total += not bad
                    l_blocked += (not bad) and hit
                rows.append({"scenario": s, "experiment": exp, "agent": m["agent"], "condition": m["condition"],
                             "repeat": m["repeat"], "rules": name, "harmful": h_total, "harmful_blocked": h_blocked,
                             "legit": l_total, "legit_blocked": l_blocked})
    (HERE / "replay-v2.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(f"{'scenario':10}{'rules':28}{'harmful blocked':>17}{'legitimate blocked':>22}")
    for s in SCENARIOS:
        for name in ("v1 rules, 003 checkpoint", "v1 rules, new checkpoint", "v2 rules, new checkpoint",
                     "v2 rules, record corrected"):
            rs = [r for r in rows if r["scenario"] == s and r["rules"] == name]
            if not rs:
                continue
            h, hb = sum(r["harmful"] for r in rs), sum(r["harmful_blocked"] for r in rs)
            lg, lb = sum(r["legit"] for r in rs), sum(r["legit_blocked"] for r in rs)
            print(f"{s:10}{name:28}{f'{hb}/{h}':>17}{f'{lb}/{lg} ({lb / lg:.0%})' if lg else '-':>22}")


if __name__ == "__main__":
    {"handoffs": cmd_handoffs, "compile": cmd_compile, "replay": cmd_replay}[sys.argv[1]](*sys.argv[2:])
