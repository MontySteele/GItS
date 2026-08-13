# Atlas — klee-mod-build-pck

> **Lifecycle: LIVING** — expected to change; read it to work on the project.

Scope: `klee-mod/build/` (deploy, validate, version, deploy_bridge, bitecheck),
`klee-mod/pck-src/`, `klee-mod/Klee/manifest.json`, plus the pck producer that
lives outside the directory but belongs to this pipeline: `tools/build_pck.ps1`.

## 1. Purpose

The **packaging and gating layer**: it turns `KleeCode` + ImageGen art into a
staged `mods/klee` package (manifest, `klee.dll`, flat card PNGs, `klee.pck` and
its contract), gates that stage with static rules, and either copies it into the
game or zips it for co-op handoff. It is deliberately **not** a runtime
validator — anything needing evaluated values (`StartingRelics`, loc keys after
BaseLib prefixing, pool rarity) lives in `KleeCode/Diagnostics/KleeSelfCheck.cs`
(`validate.ps1:1-11`, `klee-mod/DECISIONS.md:200-222`) — and not an art
pipeline: pixels are produced under `ImageGen/` (Tier F, gitignored) and this
layer only imports and packs them. `deploy_bridge.ps1` ships a **test harness**,
never a shipped artifact, and it must never enter the handoff zip
(`deploy_bridge.ps1:14-17`).

## 2. Entry points

Windows PowerShell 5.1, run from `klee-mod\` unless noted:

```powershell
.\build\deploy.ps1                          # build + stage + validate + deploy to <GameDir>\mods\klee
.\build\deploy.ps1 -Package                 # also zip dist\klee-v<MAJOR-AUTO>.zip (handoff)
.\build\deploy.ps1 -AllowIncompleteGameRef  # tolerate a stale game_ref/ (S7 escape hatch)
.\build\validate.ps1 -StageDir <stage> -SourceDir .\KleeCode -GameDir <game>
.\build\validate.ps1 ... -StaticOnly        # every rule except S7's pytest run (~5s inner loop)
.\build\deploy_bridge.ps1                   # install vendor\STS2_MCP to <GameDir>\mods\STS2_MCP
.\build\deploy_bridge.ps1 -Remove           # the one-command undo
..\tools\build_pck.ps1 [-MegaDot <editor.exe>]   # rebuild klee-mod\assets\klee.pck + contract
```

Manual Harmony bite-check (`build/bitecheck/README.md:7-20`; expected on an
unmodified tree: `[klee] harmony: 17 patch class(es) armed.`), then the portable
pins, which need no game install:

```sh
cd klee-mod/build/bitecheck && dotnet build && ./bin/Debug/harmony-bitecheck.exe
PYTHONPATH=. python3 -m pytest tier0/tests/test_manifest_version_gate.py \
  tier0/tests/test_gate_repairs.py tier0/tests/test_pck_reference_gate.py \
  tier0/tests/test_repo_python_convention.py -q
```

In-process (dot-source `build/version.ps1`): `Get-PackageVersion`,
`Get-ManifestMajor`, `Get-AutoVersion`, `Test-VersionPolicy`,
`ConvertTo-ComparableVersion`, `Get-InstalledGameVersion`.

## 3. Key invariants

- **Never build in place.** ModManager walks `mods/` recursively and JSON-parses
  every `*.json`; build output under `mods/` throws on every boot for every mod.
  Stage a clean package and copy exactly that (`deploy.ps1:1-15`), enforced as
  rule S1 (`validate.ps1:55-60`) and re-enforced for the bridge
  (`deploy_bridge.ps1:86-101`).
- **Version is `MAJOR-AUTO`.** MAJOR lives in `Klee/manifest.json` and no tool
  writes it; AUTO is `git rev-list --count HEAD`, `+dirty` when the tree is
  dirty (`version.ps1:52-106`). The stamp is applied to the **staged** manifest
  only (`deploy.ps1:78-89`), and S3 fails when staged ≠ computed
  (`version.ps1:218-224`).
- **Version comparisons must compare.** `min_version`, `min_game_version` and the
  staged version are numeric comparisons; an unparseable string reports as
  unparseable, never as satisfied (`version.ps1:124-216`). The game's version
  comes from `release_info.json`, not the exe's placeholder `1.0.0.0`
  (`version.ps1:229-241`).
- **Manifest ↔ package agreement.** `has_dll` implies `<id>.dll` is present (and
  vice versa); `has_pck` implies a `.pck` plus a `roster-pck-v3` contract whose
  `sha256=` line matches the file (`validate.ps1:71-113`). Schema as shipped:
  `id/name/author/description/version/has_dll/has_pck/min_game_version/dependencies/affects_gameplay`
  (`klee-mod/Klee/manifest.json:1-17`).
- **JSON re-serialization depth.** Restamping the staged manifest uses
  `ConvertTo-Json -Depth 10`; the default 2 flattens `dependencies` into type
  names (`deploy.ps1:86-88`).
- **The pck contract is DERIVED, not asserted.** It is generated from the files
  that actually landed in the work dir, excluding `.godot`, `project.godot`,
  `export_presets.cfg`, `klee.pck` and `.import` (`tools/build_pck.ps1:795-808`).
  A skipped copy block therefore shows up downstream as a missing resource.
- **Every shipped scene needs a `resource=` line**; S6c fails a deploy whose
  staged contract omits a source-referenced resource
  (`klee-mod/pck-src/README.md:19-20`, `validate.ps1:496-514`).
- **Encoding gate: all `.ps1` are pure ASCII.** S8 scans every `.ps1` under the
  repo root (excluding `.venv/dist/obj/bin/pck-work/node_modules`) byte by byte;
  PS 5.1 reads a BOM-less script as ANSI, so a non-ASCII byte ships as mojibake.
  Opt out per line with `# ascii-exempt: <reason>` (`validate.ps1:718-771`).
- **Native stderr convention.** Every native call in a build script goes through
  an EAP-lowering helper (`Invoke-RepoPython`, `validate.ps1:274-297`;
  `Invoke-NativeCaptured`, `tools/build_pck.ps1:57-71`); pinned by
  `tier0/tests/test_repo_python_convention.py`.
- **Machine-local paths never commit**: `local.props` (gitignored) supplies
  `GameDir` + `BaseLibDll` and the build errors out without them
  (`Directory.Build.props:18-25`, `local.props.example:1-21`). **One out-path,
  one producer**: `deploy.ps1` owns `mods\klee`, `deploy_bridge.ps1` owns
  `mods\STS2_MCP` and refuses to run if they collide (`deploy_bridge.ps1:46-50`).

## 4. Rulings that shaped it

- **R70** (`tier0/DECISIONS.md:2209-2266`) — manifest version becomes MAJOR-AUTO;
  deploy refuses to overwrite an existing handoff zip, `+dirty` is loud but not
  fatal, and S3 stops being decorative. All of `version.ps1` implements it.
- **R13** (`klee-mod/DECISIONS.md:1905-1926`) — every power must resolve to an
  icon that exists in the merged pck, checked at boot by reflection. This is why
  S12 does not try to evaluate concatenated C# paths (`validate.ps1:860-865`) and
  why a missing icon degrades to the base-game placeholder rather than a
  sibling's sigil.
- **D4** (`tier0/DECISIONS.md:2446-2503`) — a quantitative claim used as
  rationale carries a measurement or is marked UNMEASURED. Origin case is this
  module: validate.ps1's "S7 takes minutes" was 0.17s of an 84.0s gate. Hence the
  printed timing line (`validate.ps1:996-1002`) and the corrections in
  `version.ps1:159-166`.
- **R66** (`tier0/DECISIONS.md:1989-1999`) — Kokomi's archetype vocabulary made
  a silent-registry mismatch concrete; cited as one of the two motivating
  failures for S11, the roster-registry gate that is the pre-Zhongli gate
  (`validate.ps1:805-832`).
- *Dated findings (no R-number) that bind here:* "an art out-path may have
  exactly one producer" (`klee-mod/DECISIONS.md:1852-1884`, art_lint L11, cited
  by `deploy_bridge.ps1:10-12`) and "text tools must declare their encoding"
  (`klee-mod/DECISIONS.md:1886-1904`).

## 5. Traps

- **`$artSrcDirs` is a hand-maintained list of every roster character**
  (`deploy.ps1:118-128`). Omitting one fails nothing — green build, green gates,
  loaded mod, blank portraits. Kokomi shipped that way for a day. S9 checks the
  *outcome* against the stage, in both the "no staged art at all" and "partial
  copy" directions (`validate.ps1:649-716`).
- **`$pckDeferred` is checked in BOTH directions** (`validate.ps1:871-912`,
  `:981-989`): art that has landed, or an entry nothing references any more, is a
  stale exemption and fails. Portable half:
  `tier0/tests/test_pck_reference_gate.py`. S12 also excludes probe files by name
  — `KleeSceneTelemetry.cs` carries deliberately-absent paths
  (`validate.ps1:938-947`) — and drops whole comment lines only, since a naive
  `//` strip would eat real `res://` literals (`validate.ps1:949-957`).
- **Furina/Kokomi fallback copies are non-negotiable**
  (`tools/build_pck.ps1:232-262`): a null `Custom*Path` does not degrade safely —
  `AssetPaths` hands the game an id-derived path, the preload fails and the run
  crashes during map generation.
- **`-Exclude` on a directory path returns nothing.** Working-file exclusion uses
  `Where-Object { $_.Name -notlike '*_cutout.png' }`; the `-Exclude` form
  silently copied zero images and dropped both characters onto Klee's fallbacks
  (`tools/build_pck.ps1:172-200`).
- **One scene path = one conversion target**, and **no scripts in pck scenes**:
  BaseLib's registry is path-keyed (reusing a scene for rest site and merchant
  caused the first-campfire softlock, hence three near-identical sprite scenes
  per character), and the assembly has no ScriptPath mapping
  (`tools/build_pck.ps1:498-565`, `klee-mod/pck-src/README.md:16-23`,
  `klee-mod/DECISIONS.md:1704-1712`).
- **S7's game_ref decision table is three-way**: absent → committed-only with a
  banner; **incomplete → FAIL** (the stale-reference case that masked a red
  suite); complete → `--verify` then full-suite auto mode
  (`validate.ps1:517-606`). `-StaticOnly` skips only the suite, prints a loud
  banner, and is never what deploy passes (`validate.ps1:25-29`, `:608-616`).
- **The game holds a lock on `klee.dll`.** deploy fails fast if
  `SlayTheSpire2` is running, except under `-Package`, where the zip is built and
  only the local copy is skipped (`deploy.ps1:55-63`, `:221-226`).
- **`*.pck`, `dist\`, `*.zip` and `ImageGen/` are gitignored Tier F.** Every
  machine builds its own pack; handoff zips are passed privately
  (`deploy.ps1:24-30`, `tools/build_pck.ps1:14-16`). `klee/build_id.tres`
  (timestamp + short sha) is stamped into every pack so a stale pck announces
  itself in `godot.log` (`tools/build_pck.ps1:726-735`), and WebP bytes wearing a
  `.png` name are re-encoded in the scratch copy only, because Godot's PNG
  importer hard-fails on them (`tools/build_pck.ps1:737-753`).

## 6. Reading order

1. `klee-mod/build/deploy.ps1` — the whole shipping path in 238 lines.
2. `klee-mod/build/version.ps1` — R70's MAJOR-AUTO policy and `Test-VersionPolicy`.
3. `klee-mod/build/validate.ps1` — S1-S12; every rule's header names the bug it caught.
4. `tools/build_pck.ps1` — copy blocks, heredoc scenes, import/export, derived contract.
5. `klee-mod/pck-src/README.md` — the four rules for git-tracked scene sources.
6. `tier0/DECISIONS.md:2209` (R70) and `tier0/DECISIONS.md:2446` (D4).
