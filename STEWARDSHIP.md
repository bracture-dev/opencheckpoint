# Foundation stewardship

OpenCheckpoints is intended to be stewarded by a neutral foundation. The Agentic AI Foundation
(AAIF), a Linux Foundation directed fund, is the natural candidate: it hosts MCP and A2A, and
Open Responses names it as liaison. This document records what that foundation's published
process requires and what this project must resolve before applying.

**OpenCheckpoints is not affiliated with, endorsed by, or under consideration by AAIF or any
other foundation.** AAIF's proposal form asks projects not to describe themselves as donated or
contributed before every approval is complete; this project will follow that rule.

Requirements below were read from AAIF's published documents on 2026-10-24 (project proposal
process v0.3 and project lifecycle policy). They may have changed since; check the sources before
acting.

## What AAIF's process expects

- **Entry stage: Sandbox.** An OSI-approved permissive license; a working implementation; at
  least one active maintainer and a stated intent to grow contributors; a one-to-two-page thesis
  on who will use the project and what would justify promotion; transfer of trademarks and
  accounts; adoption of a Linux Foundation technical charter. Sandbox projects are reviewed after
  six months and are expected to apply for Growth within twelve.
- **Growth** additionally requires production use by at least two unaffiliated organizations,
  commits from at least two organizations over six months, named committers, and a TC sponsor.
- **Proposal:** an issue on `aaif/project-proposals`, reviewed by the CTO, acknowledged by
  Technical Committee members, voted by the TC and the Governing Board, then signed with LF Legal.
- **Licensing:** code under an OSI-approved permissive license. Comparable projects use
  Apache-2.0 for code and specification and CC-BY-4.0 for documentation, with DCO sign-off and no
  CLA. This repository already follows that pattern.
- **Trademarks:** project marks must be transferred to and held by LF Projects, LLC or the Linux
  Foundation.

## Status of this repository against those expectations

| Item                                                                            | Status                                                                                                                                      |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Apache-2.0 for code and specification; CC-BY-4.0 for docs                       | Done.                                                                                                                                       |
| DCO sign-off, no CLA, contributors keep copyright                               | Documented in CONTRIBUTING.md; enforce with a DCO check once the repository is public.                                                      |
| SPDX headers in source files                                                    | Done for tooling; required for new files.                                                                                                   |
| GOVERNANCE.md, MAINTAINERS.md, CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md | Done.                                                                                                                                       |
| Public process for specification changes                                        | Done (RFCs).                                                                                                                                |
| CI and release workflow                                                         | CI done; release workflow to be added with the first tagged release.                                                                        |
| Working implementation                                                          | Schema validation and semantic checks exist in the conformance harness; the TypeScript SDK (Phase 2) is the first reference implementation. |
| Sandbox thesis                                                                  | Not written. RFC 0001 contains most of the material.                                                                                        |
| OpenSSF Best Practices badge or security posture statement                      | Not started.                                                                                                                                |
| Maintainers from more than one organization                                     | Not met. One maintainer, one organization.                                                                                                  |
| Unaffiliated adopters                                                           | Not met.                                                                                                                                    |

## To resolve before applying

1. **Trademark.** Search and, if clear, register "OpenCheckpoints" in a form that can be
   assigned to LF Projects, LLC. Do not design a logo until the name is cleared.
2. **Accounts and domain.** The `opencheckpoints` GitHub organization is currently owned by an
   individual and billed to a company address. Before applying, add owners from at least one other
   organization, and register a project domain in a way that can be transferred. The schema `$id`
   uses the GitHub Pages URL until then; moving it requires a new specification version.
3. **Contributor history.** Keep every contribution under Apache-2.0 or CC-BY-4.0 with DCO
   sign-off from the first public commit, so no relicensing is needed later.
4. **Neutral maintainership.** Recruit maintainers and specification editors from at least two
   other organizations, ideally from carrier-protocol communities (MCP, A2A, ACP) and from agent
   runtimes.
5. **Independent implementations.** At least two producers or consumers maintained by
   organizations other than the founding maintainer's.
6. **Patent posture.** Apache-2.0 includes a patent license from contributors. Confirm with the
   foundation whether a specification-specific patent policy is expected before applying.
7. **Sandbox thesis and proposal form.** Draft them once items 1–5 are under way.
