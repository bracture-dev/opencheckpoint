// SPDX-License-Identifier: Apache-2.0
// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// Served as a GitHub Pages project site until the project has its own domain.
const site = process.env.SITE_URL ?? "https://opencheckpoint.github.io";
const base = process.env.SITE_BASE ?? "/opencheckpoint";

export default defineConfig({
  site,
  base,
  integrations: [
    starlight({
      title: "OpenCheckpoint",
      description:
        "An open format for carrying unfinished work between AI models, agents, and applications.",
      logo: { src: "./src/assets/mark.svg", alt: "" },
      favicon: "/favicon.svg",
      customCss: ["./src/styles/theme.css"],
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/opencheckpoint/opencheckpoint",
        },
      ],
      editLink: {
        baseUrl: "https://github.com/opencheckpoint/opencheckpoint/edit/main/docs/",
      },
      lastUpdated: false,
      sidebar: [
        {
          label: "Start here",
          items: [
            { label: "Introduction", slug: "introduction" },
            { label: "Why OpenCheckpoint", slug: "why" },
            { label: "Core concepts", slug: "concepts" },
          ],
        },
        {
          label: "Specification",
          items: [
            { label: "Specification v0.1", slug: "specification" },
            { label: "Schema reference", slug: "reference/schema" },
            { label: "Validation and compatibility", slug: "validation" },
            { label: "Compaction and restoration", slug: "compaction" },
            { label: "Security and trust", slug: "security" },
          ],
        },
        { label: "Examples", items: [{ autogenerate: { directory: "examples" } }] },
        {
          label: "SDKs",
          items: [
            { label: "TypeScript", slug: "sdks/typescript" },
            { label: "Go", slug: "sdks/go" },
            { label: "Rust", slug: "sdks/rust" },
            { label: "Python", slug: "sdks/python" },
          ],
        },
        { label: "Interoperability", items: [{ autogenerate: { directory: "interop" } }] },
        { label: "Conformance", items: [{ autogenerate: { directory: "conformance" } }] },
        { label: "RFCs", items: [{ autogenerate: { directory: "rfcs" } }] },
        { label: "Project", items: [{ autogenerate: { directory: "project" } }] },
      ],
    }),
  ],
});
