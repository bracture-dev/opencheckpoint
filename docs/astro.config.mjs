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
      logo: {
        light: "./src/assets/lockup-horizontal-light.svg",
        dark: "./src/assets/lockup-horizontal-dark.svg",
        alt: "OpenCheckpoint",
        replacesTitle: true,
      },
      favicon: "/favicon.svg",
      head: [
        {
          tag: "link",
          attrs: { rel: "icon", type: "image/png", sizes: "32x32", href: `${base}/favicon-32.png` },
        },
        {
          tag: "link",
          attrs: { rel: "icon", type: "image/png", sizes: "16x16", href: `${base}/favicon-16.png` },
        },
      ],
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
            { label: "Using OpenCheckpoint", slug: "using" },
          ],
        },
        {
          label: "Specification",
          items: [
            { label: "Specification v0.1", slug: "specification" },
            { label: "Schema reference", slug: "reference/schema" },
            { label: "Validation and compatibility", slug: "validation" },
            { label: "Security and trust", slug: "security" },
          ],
        },
        {
          label: "Guides",
          items: [
            { label: "Compaction and restoration", slug: "compaction" },
            { label: "Forking a baseline", slug: "forking" },
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
        {
          label: "Design",
          items: [
            { label: "RFC 0001: OpenCheckpoint v0.1", slug: "rfcs/0001-opencheckpoint" },
            { label: "RFC process", slug: "rfcs" },
            { label: "Prior art", slug: "prior-art" },
          ],
        },
        { label: "Project", items: [{ autogenerate: { directory: "project" } }] },
      ],
    }),
  ],
});
