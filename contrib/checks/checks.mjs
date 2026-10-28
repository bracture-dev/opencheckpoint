// SPDX-License-Identifier: Apache-2.0
//
// Additional checks for OpenCheckpoint v0.1, layered on the repository's own harness.
//
// Each check enforces a MUST that spec/versions/v0.1.md already states and that
// tools/conformance.mjs does not check yet. Nothing here changes the harness: checkAll() runs
// the harness's check() first and adds its own findings after it. Rule codes are placeholders.

import { check } from "../../tools/conformance.mjs";

const TERMINAL_OPS = new Set(["completed", "cancelled", "rejected"]);

// §3: a checkpoint is I-JSON. JSON.parse keeps the last of two members with the same name,
// accepts an unpaired surrogate, and turns an out-of-range number into Infinity, so these are
// checked on the text. Parsers differ on which duplicate they keep, so two consumers of the same
// file can read two different documents.
export function checkText(text) {
  const problems = [];
  const stack = [];
  const path = () =>
    "/" +
    stack
      .slice(0, -1)
      .map((f) => f.key ?? f.index)
      .join("/");
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    const top = stack.at(-1);
    if (ch === '"') {
      let j = i + 1;
      while (text[j] !== '"') j += text[j] === "\\" ? 2 : 1;
      if (top?.keys && top.expectKey) {
        const key = JSON.parse(text.slice(i, j + 1));
        if (top.keys.has(key)) problems.push(`${path()} has the member "${key}" more than once`);
        top.keys.add(key);
        top.key = key;
      }
      i = j;
    } else if (ch === "{") stack.push({ keys: new Set(), expectKey: true });
    else if (ch === "[") stack.push({ index: 0 });
    else if (ch === "}" || ch === "]") stack.pop();
    else if (ch === ":") top.expectKey = false;
    else if (ch === ",") {
      if (top.keys) top.expectKey = true;
      else top.index++;
    }
  }
  const lone = /[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/;
  const walk = (v, at) => {
    if (typeof v === "string" && lone.test(v)) problems.push(`${at} has an unpaired surrogate`);
    else if (typeof v === "number" && !Number.isFinite(v))
      problems.push(`${at} is outside IEEE 754 double precision`);
    else if (v && typeof v === "object")
      for (const [k, x] of Object.entries(v)) {
        if (lone.test(k)) problems.push(`${at} has a member name with an unpaired surrogate`);
        walk(x, `${at === "/" ? "" : at}/${k}`);
      }
  };
  walk(JSON.parse(text), "/");
  return problems;
}

// Rules on one document.
export function checkDocument(doc) {
  const errors = [];
  const err = (code, path, message) => errors.push({ code, path, message });

  // §9.1, §10.2: a destination may act on constraints and decisions as the user's intent, so
  // text from a tool or a third party cannot carry them. The schema already stops it from
  // becoming an instruction.
  for (const [i, s] of (doc.statements ?? []).entries())
    if (
      (s.kind === "constraint" || s.kind === "decision") &&
      (s.origin.type === "tool" || s.origin.type === "external")
    )
      err(
        "OCP-S011",
        `/statements/${i}`,
        `${s.kind} "${s.id}" has origin ${s.origin.type}; record third-party text as external`,
      );

  // §9.2: a compacted checkpoint records what it dropped and what it condensed.
  if (doc.derivation?.method === "compacted")
    for (const field of ["omissions", "transformations"])
      if (!doc.derivation[field])
        err(
          "OCP-S010",
          "/derivation",
          `a compacted checkpoint records its ${field}, even as an empty list (§9.2)`,
        );

  return errors;
}

// Rules between a parent and a child.
export function checkLineage(parent, child) {
  const errors = [];
  const fail = (code, path, message) => errors.push({ code, path, message });

  // §6.5: a statement's kind never changes in place. A confirmed hypothesis is superseded by a
  // new observation; it does not become one.
  const kinds = new Map((parent.statements ?? []).map((s) => [s.id, s.kind]));
  for (const [i, s] of (child.statements ?? []).entries())
    if (kinds.has(s.id) && kinds.get(s.id) !== s.kind)
      fail(
        "OCP-T004",
        `/statements/${i}`,
        `"${s.id}" was ${kinds.get(s.id)} in the parent and cannot become ${s.kind}`,
      );

  if (child.derivation?.method === "compacted") errors.push(...checkCompaction(parent, child));
  return errors;
}

// §9.2, the parts a validator can check when it holds a compacted child and its parent. An object
// counts as carried only under its own id and in its own collection, so a statement rewritten
// under a new id is a dropped statement. Compaction condenses what the parent recorded; it does
// not record new events, so a carried object keeps the status and fields it had.
function checkCompaction(parent, child) {
  const errors = [];
  const fail = (code, path, message) => errors.push({ code, path, message });
  const status = (s) => s.status ?? "active";
  const sameSet = (a, b, key) => {
    if (!a || !b) return !a && !b;
    const x = new Set(a.map(key));
    const y = new Set(b.map(key));
    return x.size === y.size && [...x].every((k) => y.has(k));
  };

  const statements = new Map((child.statements ?? []).map((s) => [s.id, s]));
  const operations = new Map((child.operations ?? []).map((o) => [o.id, o]));
  const stops = new Map((child.continuation?.stop_conditions ?? []).map((s) => [s.id, s]));

  for (const [i, p] of (parent.statements ?? []).entries()) {
    const path = `/statements/${i}`;
    const c = statements.get(p.id);
    const kept =
      ["instruction", "constraint", "decision", "question"].includes(p.kind) &&
      status(p) === "active";
    if (!c) {
      if (kept) fail("OCP-T003", path, `active ${p.kind} "${p.id}" was dropped by compaction`);
      continue;
    }
    if (kept && status(c) !== "active")
      fail("OCP-T003", path, `active ${p.kind} "${p.id}" is ${status(c)} after compaction`);
    if (c.origin?.type !== p.origin?.type)
      fail(
        "OCP-T004",
        path,
        `"${p.id}" had origin ${p.origin?.type} and now has ${c.origin?.type}`,
      );
    const at = c.verification?.checked_at;
    if (
      c.verification?.state === "verified" &&
      p.verification?.state !== "verified" &&
      !(at && Date.parse(at) > Date.parse(parent.created_at))
    )
      fail("OCP-T005", path, `"${p.id}" became verified with no check after the parent`);
    if (status(p) !== "active" && status(c) === "active")
      fail("OCP-T006", path, `"${p.id}" was ${status(p)} in the parent and is active again`);
  }

  // A terminal operation may be dropped, but one carried under its id keeps its kind.
  for (const [i, o] of (parent.operations ?? []).entries()) {
    const path = `/operations/${i}`;
    const c = operations.get(o.id);
    if (c && c.kind !== o.kind) fail("OCP-T004", path, `operation "${o.id}" changed kind`);
    if (TERMINAL_OPS.has(o.status)) continue;
    if (!c) fail("OCP-T003", path, `${o.status} operation "${o.id}" was dropped`);
    else if (c.status !== o.status)
      fail("OCP-T003", path, `${o.status} operation "${o.id}" is ${c.status} after compaction`);
  }

  // A stop condition is kept under its id with exactly the operations it held and exactly the
  // entries that lift it. §9.2 has no exception, so an omission does not excuse a dropped one.
  for (const [i, s] of (parent.continuation?.stop_conditions ?? []).entries()) {
    const path = `/continuation/stop_conditions/${i}`;
    const c = stops.get(s.id);
    if (!c) {
      fail("OCP-T003", path, `stop condition "${s.id}" was dropped`);
      continue;
    }
    if (!sameSet(s.applies_to, c.applies_to, (a) => a))
      fail("OCP-T003", path, `stop condition "${s.id}" changed applies_to`);
    if (!sameSet(s.until, c.until, (u) => `${u.operation}\u0000${u.status}`))
      fail("OCP-T003", path, `stop condition "${s.id}" changed until`);
  }
  return errors;
}

// The harness's check(), then these checks. Takes document text, so the I-JSON check can run.
export function checkAll(text, parentText) {
  const problems = checkText(text);
  if (problems.length) return { level: "schema", errors: problems, warnings: [] };
  const doc = JSON.parse(text);
  const parent = parentText === undefined ? undefined : JSON.parse(parentText);
  const base = check(doc, parent);
  if (base.level === "schema") return base;
  const errors = [...base.errors, ...checkDocument(doc)];
  if (parent) errors.push(...checkLineage(parent, doc));
  return { level: errors.length ? "semantic" : "ok", errors, warnings: base.warnings };
}
