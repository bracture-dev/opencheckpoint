// SPDX-License-Identifier: Apache-2.0
//
// Runs the additional checks. For every case in this folder's manifest it shows two things:
// what the repository's harness alone says today, and what it says with these checks. Every
// invalid case here passes the harness alone; that is the gap each check closes. It then runs
// the repository's own manifest and examples with the checks on, to show they change no result.
//
//   node contrib/checks/run.mjs

import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { check } from "../../tools/conformance.mjs";
import { checkAll } from "./checks.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..");
const read = (p) => readFileSync(p, "utf8");
const codes = (list) => [...new Set(list.map((e) => e.code))].sort().join(",");

let failures = 0;
const fail = (id, why) => {
  failures++;
  console.log(`FAIL ${id}: ${why}`);
};

// Compare a result with a manifest expectation; return a reason it differs, or "".
function differs(result, want) {
  const level = want.result === "valid" ? "ok" : want.result;
  if (result.level !== level) return `expected ${want.result}, got ${result.level}`;
  if (want.result === "semantic" && codes(result.errors) !== [...want.errors].sort().join(","))
    return `expected ${want.errors}, got ${codes(result.errors)}`;
  if (codes(result.warnings) !== [...(want.warnings ?? [])].sort().join(","))
    return `expected warnings ${want.warnings ?? []}, got ${codes(result.warnings)}`;
  return "";
}

function runManifest(dir, { gap }) {
  const manifest = JSON.parse(read(join(dir, "manifest.json")));
  for (const c of manifest.cases) {
    const text = read(join(dir, c.file));
    const parentText = c.parent ? read(join(dir, c.parent)) : undefined;
    const why = differs(checkAll(text, parentText), c.expect);
    if (why) {
      fail(c.id, why);
      continue;
    }
    if (!gap) continue;
    let today;
    try {
      today = check(JSON.parse(text), parentText && JSON.parse(parentText)).level;
    } catch {
      today = "unreadable";
    }
    if (c.expect.result !== "valid" && today !== "ok")
      fail(c.id, `the harness alone already reports ${today}, so this case shows no gap`);
    else console.log(`ok   ${c.id}${c.expect.result === "valid" ? "" : "  (harness alone: ok)"}`);
  }
}

console.log("Cases for the additional checks:");
runManifest(here, { gap: true });

console.log("\nThe repository's own cases and examples, with the additional checks on:");
const before = failures;
runManifest(join(root, "tests", "conformance"), { gap: false });
for (const d of readdirSync(join(root, "examples"), { withFileTypes: true })) {
  const file = join(root, "examples", d.name, "checkpoint.json");
  if (d.isDirectory() && existsSync(file) && checkAll(read(file)).level !== "ok")
    fail(`examples/${d.name}`, "no longer valid with the additional checks");
}
if (failures === before) console.log("no result changed");

console.log(failures ? `\n${failures} failure(s)` : "\nall cases passed");
process.exit(failures ? 1 : 0);
