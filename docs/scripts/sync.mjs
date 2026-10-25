// SPDX-License-Identifier: Apache-2.0
//
// Builds the generated part of the documentation site from the repository, so the
// site never restates the specification, the schema, the RFCs, the examples, or the
// project documents. Generated paths are listed in docs/.gitignore.

import {
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
  copyFileSync,
  existsSync,
} from "node:fs";
import { dirname, join, posix } from "node:path";
import { fileURLToPath } from "node:url";

const docs = join(dirname(fileURLToPath(import.meta.url)), "..");
const repo = join(docs, "..");
const content = join(docs, "src/content/docs");
const GITHUB = "https://github.com/opencheckpoint/opencheckpoint";

const read = (p) => readFileSync(join(repo, p), "utf8");

// Repository path → site route. A route ending in "/" is a page; otherwise a static file.
const routes = new Map();
// Site route → { source, title, order, body }.
const pages = [];

function page(source, route, { title, order, extra = "" } = {}) {
  routes.set(source, route);
  pages.push({ source, route, title, order, extra });
}

// ---- collect pages ----

page("spec/versions/v0.1.md", "specification/");
routes.set("spec/schema/v0.1/checkpoint.schema.json", "schema/v0.1/checkpoint.schema.json");
routes.set("spec/schema/v0.1", "reference/schema/");
routes.set("spec/README.md", "specification/");

page("rfcs/README.md", "rfcs/", { title: "RFC process", order: 0 });
for (const f of readdirSync(join(repo, "rfcs")).sort()) {
  const m = f.match(/^(\d{4})-.+\.md$/);
  if (m && m[1] !== "0000")
    page(`rfcs/${f}`, `rfcs/${f.replace(/\.md$/, "")}/`, { order: Number(m[1]) });
}
routes.set("rfcs/0000-template.md", null);

page("examples/README.md", "examples/", { title: "Overview", order: 0 });
const exampleDirs = readdirSync(join(repo, "examples"), { withFileTypes: true })
  .filter((d) => d.isDirectory())
  .map((d) => d.name)
  .sort();
for (const [i, name] of exampleDirs.entries()) {
  const json = read(`examples/${name}/checkpoint.json`);
  routes.set(`examples/${name}/checkpoint.json`, `examples/${name}.ocp.json`);
  page(`examples/${name}/README.md`, `examples/${name}/`, {
    order: i + 1,
    extra: `\n## The checkpoint\n\n[Download](../${name}.ocp.json) · [View on GitHub](${GITHUB}/blob/main/examples/${name}/checkpoint.json)\n\n\`\`\`json\n${json}\`\`\`\n`,
  });
  routes.set(`examples/${name}`, `examples/${name}/`);
}

page("tests/conformance/README.md", "conformance/", { title: "Conformance suite", order: 0 });
page("tests/scenarios/README.md", "conformance/scenarios/", {
  title: "Behavioral scenarios",
  order: 1,
});
routes.set("tests/scenarios", "conformance/scenarios/");
for (const f of readdirSync(join(repo, "tests/scenarios")).sort())
  if (f !== "README.md" && f.endsWith(".md"))
    page(`tests/scenarios/${f}`, `conformance/scenarios/${f.replace(/\.md$/, "")}/`, { order: 2 });

const projectDocs = [
  ["GOVERNANCE.md", "Governance"],
  ["CONTRIBUTING.md", "Contributing"],
  ["MAINTAINERS.md", "Maintainers"],
  ["ROADMAP.md", "Roadmap"],
  ["SECURITY.md", "Security policy"],
  ["CODE_OF_CONDUCT.md", "Code of conduct"],
  ["CHANGELOG.md", "Changelog"],
];
for (const [i, [f, title]] of projectDocs.entries())
  page(f, `project/${f.replace(/\.md$/, "").toLowerCase().replace(/_/g, "-")}/`, {
    title,
    order: i,
  });

// ---- markdown transformation ----

function splitFrontMatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n/);
  if (!m) return { meta: {}, body: text };
  const meta = {};
  for (const line of m[1].split("\n")) {
    const kv = line.match(/^(\w+):\s*(.*)$/);
    if (kv) meta[kv[1]] = kv[2].replace(/^"(.*)"$/, "$1");
  }
  return { meta, body: text.slice(m[0].length) };
}

function relativeUrl(fromRoute, toRoute) {
  const fromDir = fromRoute.endsWith("/") ? fromRoute : posix.dirname(fromRoute) + "/";
  if (toRoute.endsWith("/")) {
    const rel = posix.relative(fromDir, toRoute);
    return rel === "" ? "./" : rel + "/";
  }
  return posix.relative(fromDir, toRoute);
}

function rewriteLinks(body, source, fromRoute) {
  return body.replace(/\]\(([^)\s]+)\)/g, (whole, target) => {
    if (/^([a-z]+:|#)/i.test(target)) return whole;
    const [path, anchor] = target.split("#");
    const repoPath = posix.normalize(posix.join(posix.dirname(source), path)).replace(/\/$/, "");
    const route = routes.get(repoPath);
    const hash = anchor ? `#${anchor}` : "";
    if (route) return `](${relativeUrl(fromRoute, route)}${hash})`;
    const isDir = existsSync(join(repo, repoPath)) && !/\.[a-z]+$/i.test(repoPath);
    return `](${GITHUB}/${isDir ? "tree" : "blob"}/main/${repoPath}${hash})`;
  });
}

const yaml = (s) => JSON.stringify(s);

function render({ source, route, title, order, extra }) {
  const { meta, body: raw } = splitFrontMatter(read(source));
  let body = raw;
  const h1 = body.match(/^# (.+)\n/m);
  if (h1) body = body.replace(h1[0], "");
  const pageTitle = title ?? meta.title ?? h1?.[1] ?? source;

  let preamble = "";
  if (meta.rfc) {
    preamble = `| RFC | Type | Status | Created |\n|---|---|---|---|\n| ${meta.rfc} | ${meta.type} | ${meta.status} | ${meta.created} |\n\n`;
  }
  const sourceNote = `\n\n---\n\n*Generated from [\`${source}\`](${GITHUB}/blob/main/${source}). Edit it there.*\n`;
  const fm = [
    "---",
    `title: ${yaml(h1 && meta.rfc ? h1[1].replace(/^RFC \d+: /, "") : pageTitle)}`,
  ];
  if (order !== undefined) fm.push("sidebar:", `  order: ${order}`);
  fm.push("editUrl: " + yaml(`${GITHUB}/edit/main/${source}`), "---", "");
  return (
    fm.join("\n") + preamble + rewriteLinks(body.trim() + "\n" + extra, source, route) + sourceNote
  );
}

// ---- schema reference ----

function schemaReference() {
  const schema = JSON.parse(read("spec/schema/v0.1/checkpoint.schema.json"));
  const anchor = (name) => name.toLowerCase();
  const cell = (s) =>
    String(s ?? "")
      .replace(/\|/g, "\\|")
      .replace(/\n/g, " ");

  function type(s) {
    if (!s) return "any";
    if (s.$ref) {
      const name = s.$ref.split("/").pop();
      return `[${name}](#${anchor(name)})`;
    }
    if (s.const !== undefined) return `\`${JSON.stringify(s.const)}\``;
    if (s.enum) return s.enum.map((v) => `\`${v}\``).join(", ");
    if (s.type === "array") return `array of ${type(s.items)}`;
    if (s.type === "object" && s.properties) return "object (below)";
    let t = s.type ?? "any";
    if (s.format) t += ` (${s.format})`;
    if (s.maxLength) t += `, ≤ ${s.maxLength} chars`;
    return t;
  }

  function section(name, s, depth = 2) {
    const out = [`${"#".repeat(depth)} ${name}`, ""];
    if (s.description) out.push(s.description, "");
    if (s.properties) {
      const required = new Set(s.required ?? []);
      out.push("| Property | Type | Required | Description |", "|---|---|---|---|");
      for (const [prop, ps] of Object.entries(s.properties))
        out.push(
          `| \`${prop}\` | ${cell(type(ps))} | ${required.has(prop) ? "yes" : ""} | ${cell(ps.description)} |`,
        );
      out.push("");
      if (s.anyOf)
        out.push(
          `At least one of: ${s.anyOf.map((a) => a.required.map((r) => `\`${r}\``).join(", ")).join(" or ")}.`,
          "",
        );
      if (s.additionalProperties === false) out.push("No other properties are allowed.", "");
      for (const [prop, ps] of Object.entries(s.properties)) {
        const inner = ps.type === "array" ? ps.items : ps;
        if (inner?.type === "object" && inner.properties)
          out.push(...section(`${name}.${prop}`, inner, Math.min(depth + 1, 4)));
      }
    } else if (s.type || s.pattern) {
      out.push(`Type: ${type(s)}${s.pattern ? `, pattern \`${s.pattern}\`` : ""}.`, "");
    }
    const rules = (s.allOf ?? []).map((r) => r.description).filter(Boolean);
    if (rules.length) out.push("**Rules**", "", ...rules.map((r) => `- ${r}`), "");
    return out;
  }

  const lines = [
    "---",
    'title: "Schema reference"',
    `editUrl: ${yaml(`${GITHUB}/edit/main/spec/schema/v0.1/checkpoint.schema.json`)}`,
    "---",
    "",
    `Generated from the [v0.1 JSON Schema](../../schema/v0.1/checkpoint.schema.json) (\`${schema.$id}\`). The [specification](../../specification/) governs the meaning of each field; this page lists their shape.`,
    "",
    ...section("Checkpoint (top level)", { ...schema, description: undefined }),
  ];
  for (const [name, def] of Object.entries(schema.$defs)) lines.push(...section(name, def));
  return lines.join("\n");
}

// ---- write ----

for (const dir of ["specification", "reference", "rfcs", "examples", "conformance", "project"])
  rmSync(join(content, dir), { recursive: true, force: true });
rmSync(join(docs, "public/schema"), { recursive: true, force: true });
rmSync(join(docs, "public/examples"), { recursive: true, force: true });

for (const p of pages) {
  const file = join(
    content,
    isIndex(p.route) ? `${p.route}index.md` : `${p.route.replace(/\/$/, "")}.md`,
  );
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, render(p));
}

function isIndex(route) {
  return [
    "specification/",
    "rfcs/",
    "examples/",
    "conformance/",
    "conformance/scenarios/",
  ].includes(route);
}

mkdirSync(join(content, "reference"), { recursive: true });
writeFileSync(join(content, "reference/schema.md"), schemaReference());

mkdirSync(join(docs, "public/schema/v0.1"), { recursive: true });
copyFileSync(
  join(repo, "spec/schema/v0.1/checkpoint.schema.json"),
  join(docs, "public/schema/v0.1/checkpoint.schema.json"),
);
mkdirSync(join(docs, "public/examples"), { recursive: true });
for (const name of exampleDirs)
  copyFileSync(
    join(repo, `examples/${name}/checkpoint.json`),
    join(docs, `public/examples/${name}.ocp.json`),
  );

console.log(`synced ${pages.length + 1} pages from the repository`);
