---
title: Model Context Protocol
description: Carrying checkpoints as MCP resources and referencing MCP resources from checkpoints.
sidebar:
  order: 1
---

## Exposing a checkpoint as a resource

An MCP server that produces or stores checkpoints can list each one as a resource:

- `uri`: any URI the server controls, for example `checkpoints://tasks/1412/latest`.
- `mimeType`: `application/vnd.opencheckpoint+json`.
- The resource contents are the checkpoint document as text.

A client or host that restores the checkpoint follows the
[restoration procedure](../../specification/#107-restoration-procedure). A checkpoint fetched
through MCP is still untrusted input.

## Referencing MCP resources

A checkpoint resource can carry an MCP resource URI directly in `uri`, including custom schemes.
Use `resolver` to hint which server can resolve it:

```json
{
  "id": "r-design-doc",
  "kind": "document",
  "uri": "docs://projects/atlas/design.md",
  "resolver": { "protocol": "mcp", "hint": { "server": "docs" } },
  "revision": "2026-10-20T11:00:00Z"
}
```

The hint names a server, never credentials. The destination resolves the URI through its own
MCP connections, with its own authorization.

## Mapping

| MCP                                                                                    | OpenCheckpoint                                               |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `Resource.uri`, `mimeType`, `size`                                                     | `resource.uri`, `media_type`, `size`                         |
| `Annotations.lastModified`                                                             | `resource.revision` or `observed_at`                         |
| `input_required` result                                                                | an `operation` with `kind: input`, `status: awaiting`        |
| Tasks extension status `working`, `input_required`, `completed`, `failed`, `cancelled` | `task.status` and operation status, where the meanings match |
| `_meta` reverse-DNS keys                                                               | `extensions` reverse-DNS keys (same convention)              |
