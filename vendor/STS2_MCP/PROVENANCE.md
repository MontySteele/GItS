# STS2_MCP — provenance

upstream: https://github.com/Gennadiyev/STS2MCP
pin: 55e0648
pin-subject: Fix game API compatibility with STS2 v0.107 (#123)
pin-date: 2026-07-29
license: MIT
license-holder: Yikun Ji (Kunologist)
vendored: 2026-08-04
vendored-by: Understudy sprint, work item W1
ruling: docs/understudy-p0-findings.md ruling 1, RATIFIED by [USER] 2026-08-04

## Why this pin and not a release

The latest tagged release is **0.4.0, dated 2026-05-05**, and it predates our
game build. The pin above is the commit that carries the v0.107 compatibility
fix, and v0.107.1 is exactly what we ship against. Installing the release
binary instead of building this snapshot is the one way to reproduce the
version-pin failure the kickoff brief worried about — P0 stop-and-surface
item 2 says so, and this paragraph is where a hurried session is meant to
read it.

The in-tree `mod_manifest.json` still says `"version": "0.4.0"` and
`McpMod.Version` still says `0.4.0`; upstream did not bump either on this
commit. Neither string is a version pin. **This file is the pin.**

## Environment it was verified against

| Thing | Value |
|---|---|
| Game | v0.107.1, commit 59260271, dated 2026-06-18 |
| main_assembly_hash | -1555940892 |
| Toolchain | .NET SDK 9.0.316, `net9.0` |
| Build | `dotnet build -c Release` against `data_sts2_windows_x86_64` — 0 warnings, 0 errors |

## What was pruned from the snapshot

Carried: the C# mod (11 `McpMod.*.cs` files), `STS2_MCP.csproj`,
`mod_manifest.json`, `LICENSE`, `README.md`, and `docs/raw-simplified.md` +
`docs/raw-full.md` — the wire protocol, which is the contract `understudy/`
codes against and the thing a future session will actually need to read.

Dropped, and why:

- `mcp/` (the optional Python MCP server, `server.py` + `pyproject.toml` +
  `uv.lock`). We speak the HTTP API directly from `understudy/`; an MCP
  wrapper is a second client we would have to keep working for no gain.
- `build.ps1`. Superseded by `klee-mod/build/deploy_bridge.ps1`, which reads
  `GameDir` from our `local.props` like every other build path in this repo
  instead of an `STS2_GAME_DIR` environment variable, and which owns the
  install and uninstall steps upstream leaves to the reader.
- `STS2_MCP.sln`, `.github/`, `.claude/`, `AGENTS.md`, `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `.gitignore`, `docs/teaser.png` — upstream project
  furniture, not code we build or run.

Pruning is recorded rather than hidden: `UPSTREAM_MANIFEST.tsv` lists exactly
what we carry, and `tools/lint_vendor_pin.py` fails if the tree and the list
disagree in either direction.

## What we changed

**One line, in one upstream file.**

| File | Status | Change |
|---|---|---|
| `McpMod.cs` | `gits-modified` | Added an `else if (path == "/api/v1/gits/speed")` arm to the `HandleRequest` route chain, marked in-file with `GItS LOCAL EDIT`. Nothing else in the file is touched. |
| `gits/GitsSpeed.cs` | GItS addition | The whole of work item W2 — the speed affordance. Not upstream, never sent upstream in this form. |

Everything else is byte-identical to `55e0648`.

The route arm is an edit rather than a Harmony patch because upstream's
routing is a plain if/else chain in one method: patching it would mean
rewriting the same chain from outside, in more code, less legibly, to protect
a purity we can simply record instead.

## Refreshing the pin

1. `git clone https://github.com/Gennadiyev/STS2MCP && git checkout <new sha>`
2. Copy the carried files over this directory (the list is
   `UPSTREAM_MANIFEST.tsv`, `status == upstream`).
3. Re-apply the `McpMod.cs` route arm above.
4. Update `pin`, `pin-subject`, `pin-date` and the environment table here.
5. `python tools/lint_vendor_pin.py --write`, and **read the diff** — if it
   touches more than you meant, that is the finding.
6. Rebuild and re-verify against the game version in the table.

Upstreaming the speed endpoint stays open; MIT does not require it and this
sprint did not spend time on it.
