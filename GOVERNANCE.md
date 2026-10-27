# Governance

This document describes how OpenCheckpoint runs today and how its governance will change as the
project grows.

## Principles

- **Open:** the project makes all technical decisions in public, on GitHub issues, discussions,
  and pull requests.
- **Neutral:** no single company controls the specification. Maintainers disclose their
  affiliations, and governance will require maintainers from multiple organizations as the
  project grows.
- **Evidence-based:** a change to the format must rest on implementation experience, examples,
  or measurement. Preference alone does not justify one.
- **Conservative:** the specification grows only when a need is demonstrated.

## Roles

- **Contributors** are anyone who opens an issue, comments, or submits a pull request.
- **Maintainers** review and merge pull requests, shepherd RFCs, cut releases, and uphold the
  code of conduct. They are listed in [MAINTAINERS.md](MAINTAINERS.md) with their affiliations.
- **Specification editors** are the maintainers responsible for the normative text and schema.
  Every change to `spec/` needs approval from an editor.

## Becoming a maintainer

Any maintainer may nominate a contributor with a sustained record of high-quality contributions
and reviews. The maintainers decide nominations by lazy consensus (below). The project seeks
maintainers from organizations not yet represented.

The other maintainers may move a maintainer who has been inactive for six months to emeritus
status.

## Decision-making

- **Lazy consensus.** Maintainers make most decisions on pull requests. A pull request with approval
  from a maintainer (and an editor, for `spec/`) and no unresolved objection after the review
  period may be merged. The review period is two business days for editorial and tooling
  changes and seven days for normative changes.
- **RFCs.** Normative changes follow the [RFC process](rfcs/README.md). An RFC is accepted when
  the shepherd calls for consensus and no maintainer objects within seven days.
- **Voting.** If the maintainers cannot reach consensus, any maintainer may call a vote. A proposal passes
  with a majority of maintainers. Normative changes and changes to this document need two thirds.
- **Conflicts of interest.** Maintainers abstain from votes where they have a conflict of
  interest beyond their disclosed affiliation.

While maintainers come from a single organization, normative changes also require a
public comment period of at least fourteen days, announced in GitHub Discussions, so that
outside reviewers can object.

## Releases and versioning

The specification follows the version policy in §5 of the specification. A release tags the
specification, the schema, the fixtures, and the documentation together. Each release has a
changelog entry. Maintainers never edit a published schema.

## Code of conduct

All participants follow the [code of conduct](CODE_OF_CONDUCT.md). Maintainers enforce it.

## Changes to governance

Changes to this document are Process RFCs and need a two-thirds vote of maintainers.
