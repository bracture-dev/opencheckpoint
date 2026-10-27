# Security policy

## Scope

OpenCheckpoint is a specification. Security issues include:

- Flaws in the specification or schema that let a conforming consumer be manipulated into an
  unsafe action: authority transfer, prompt injection that the statement model fails to contain,
  replay of side effects, or acceptance of forged approvals.
- Gaps in the [threat model](docs/src/content/docs/security.md#threat-model).
- Vulnerabilities in the repository's tooling, documentation site, or any SDK published from this
  repository.

Report a vulnerability in a third-party product that implements OpenCheckpoint to that product's
maintainers.

## Reporting

Report vulnerabilities privately through GitHub's private vulnerability reporting on this
repository (Security → Report a vulnerability). Do not open a public issue.

Include what is affected (section, schema path, or file), how it can be exploited, and, if
possible, a fixture that demonstrates it.

## Process

Maintainers acknowledge reports within five business days, agree on a disclosure timeline with
the reporter (normally no more than 90 days), and credit the reporter unless asked not to. Maintainers
fix a specification flaw in a new version and publish the change and its rationale in the
changelog and the threat model.

## Supported versions

Only the latest published specification version and the `main` branch receive fixes during the
0.x series.
