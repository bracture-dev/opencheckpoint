# SPDX-License-Identifier: Apache-2.0
"""Fork a checkpoint per specification §9.3: python fork.py CHECKPOINT N OWNER OUT_DIR

Writes N forks to OUT_DIR/fork-K.json. Each gets a new id, the checkpoint as parent, and
derivation.method "forked". Fork OWNER keeps every pending action; every other fork gets a stop
condition referencing each non-terminal action whose effect is not "none", so it stays actionable
in one fork only.
"""

import copy
import json
import sys
import uuid
from pathlib import Path

TERMINAL = {"completed", "cancelled", "rejected"}


def fork(doc: dict, n: int, owner: int) -> list[dict]:
    forks = []
    for k in range(n):
        f = copy.deepcopy(doc)
        f["id"] = f"urn:uuid:{uuid.uuid4()}"
        f["parent"] = {"id": doc["id"]}
        f["derivation"] = {"method": "forked", "inputs": [{"checkpoint": doc["id"]}],
                           "transformations": [{"description": f"Fork {k + 1} of {n}."}]}
        if k != owner:
            owned = [o for o in f.get("operations", [])
                     if o["kind"] == "action" and o["status"] not in TERMINAL and o.get("effect") != "none"]
            if owned:
                stops = f.setdefault("continuation", {}).setdefault("stop_conditions", [])
                stops.append({"id": "stop-not-owner",
                              "description": f"Another fork owns these pending actions. Do not perform them; "
                                             f"report their status only.",
                              "refs": [o["id"] for o in owned]})
                f["derivation"]["transformations"].append(
                    {"description": "Pending actions are owned by another fork and guarded by stop-not-owner.",
                     "affected": [o["id"] for o in owned]})
        forks.append(f)
    return forks


if __name__ == "__main__":
    src, n, owner, out = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4])
    out.mkdir(parents=True, exist_ok=True)
    for k, f in enumerate(fork(json.loads(src.read_text()), n, owner)):
        (out / f"fork-{k}.json").write_text(json.dumps(f, indent=2, ensure_ascii=False) + "\n")
