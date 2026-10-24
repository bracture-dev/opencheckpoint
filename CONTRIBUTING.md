# Contributing to OpenCheckpoints

OpenCheckpoints is judged first as an open standard, second as a developer experience, and third
as a reference implementation. Contributions that improve the specification's clarity,
correctness, or neutrality are as valuable as code.

## Ways to contribute

- **Review the specification.** Open an issue for anything ambiguous, contradictory, or
  unimplementable. Say which section, what you expected, and why.
- **Implement it.** Build a producer or consumer in your agent, runtime, or application and
  report what was hard. Implementation experience is the strongest evidence for a change.
- **Add fixtures.** A fixture that exposes a gap between the specification and the schema is a
  high-value contribution.
- **Propose a change.** Changes to normative text or the schema go through an RFC
  ([rfcs/README.md](rfcs/README.md)).
- **Improve the documentation.** The site lives in `docs/`.

## Before you start

- Search existing issues and discussions.
- For anything larger than a small fix, open a discussion first.
- Read the [code of conduct](CODE_OF_CONDUCT.md).

## Pull requests

1. Fork the repository and create a branch.
2. Make the change. Keep a pull request to one purpose.
3. Run `npm test` and `npx prettier --check .`; CI runs both and builds the documentation.
4. Sign off every commit (see below).
5. Open the pull request and describe what changed and why.

Changes to `spec/` must keep the specification, the schema, the fixtures, and the conformance
manifest consistent in the same pull request. A new normative rule needs at least one valid and
one invalid fixture.

## Developer Certificate of Origin

Every commit must be signed off, certifying the [Developer Certificate of
Origin 1.1](https://developercertificate.org/):

```sh
git commit -s -m "Clarify uncertain operation semantics"
```

This adds `Signed-off-by: Your Name <you@example.com>` to the commit message. There is no CLA,
and contributors keep their copyright.

## Licensing of contributions

By contributing, you agree that your contribution is licensed under the Apache License 2.0, or,
for documentation prose under `docs/src/content/`, under Creative Commons Attribution 4.0. New
source files carry an SPDX header (`SPDX-License-Identifier: Apache-2.0`) where the file format
allows comments.

## Neutrality

OpenCheckpoints must remain independent of any model, provider, runtime, framework, or company.
Contributions must not introduce dependencies on a particular vendor's service, must not use a
vendor's branding, and must disclose affiliations relevant to a proposal. Examples use fictional
names and systems.

## Style

- Specification text uses RFC 2119 keywords only for requirements, and describes the current
  state of the format.
- JSON uses two-space indentation; Markdown and JSON are formatted with Prettier.
- Prefer a small, precise change over a broad one.
