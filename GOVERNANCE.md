# Governance

This document describes how OpenCheckpoint is run today and how governance is meant to evolve.

## Principles

- **Open:** all technical decisions are made in public, on GitHub issues, discussions, and pull
  requests.
- **Neutral:** no single company controls the specification. Maintainers disclose their
  affiliations, and governance will require maintainers from multiple organizations as the
  project grows.
- **Evidence-based:** changes to the format are justified by implementation experience,
  examples, or measurement, not preference.
- **Conservative:** the specification grows only when a need is demonstrated.

## Roles

- **Contributors** are anyone who opens an issue, comments, or submits a pull request.
- **Maintainers** review and merge pull requests, shepherd RFCs, cut releases, and uphold the
  code of conduct. They are listed in [MAINTAINERS.md](MAINTAINERS.md) with their affiliations.
- **Specification editors** are the maintainers responsible for the normative text and schema.
  Every change to `spec/` needs approval from an editor.

## Becoming a maintainer

A contributor with a sustained record of high-quality contributions and reviews may be nominated
by any maintainer. Nominations are decided by the maintainers by lazy consensus (below). The
project actively seeks maintainers from organizations not yet represented.

Maintainers who are inactive for six months may be moved to emeritus status by the other
maintainers.

## Decision-making

- **Lazy consensus.** Most decisions are made on pull requests. A pull request with approval
  from a maintainer (and an editor, for `spec/`) and no unresolved objection after the review
  period may be merged. The review period is two business days for editorial and tooling
  changes and seven days for normative changes.
- **RFCs.** Normative changes follow the [RFC process](rfcs/README.md). An RFC is accepted when
  the shepherd calls for consensus and no maintainer objects within seven days.
- **Voting.** If consensus cannot be reached, any maintainer may call a vote. A proposal passes
  with a majority of maintainers. Normative changes and changes to this document need two thirds.
- **Conflicts of interest.** Maintainers abstain from votes where they have a conflict of
  interest beyond their disclosed affiliation.

While maintainers come from a single organization, normative changes additionally require a
public comment period of at least fourteen days, announced in GitHub Discussions, so that
outside reviewers can object.

## Releases and versioning

The specification follows the version policy in §5 of the specification. A release tags the
specification, the schema, the fixtures, and the documentation together. Each release has a
changelog entry. Published schemas are never edited.

## Code of conduct

All participants follow the [code of conduct](CODE_OF_CONDUCT.md). Maintainers enforce it.

## Changes to governance

Changes to this document are Process RFCs and need a two-thirds vote of maintainers.
