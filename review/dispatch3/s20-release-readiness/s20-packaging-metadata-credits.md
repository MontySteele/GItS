# S20 — Packaging, metadata, and credits: what we ship and what a public release would have to carry

> **This document decides nothing.** It is an inventory of the packaging and
> metadata surface as it stands on 2026-08-26, not a promise that any of it
> will be supported, translated, published, or licensed. Every rights, money,
> scope, and ship call below is marked as [USER]'s and is written as a
> numbered pick list, never as a blank or a recommendation.
> Reference-reading only: nothing from Downfall or the base game was copied.

**Family:** packaging / metadata / credits (one of the seven S20 splits).
The other six families — save/update/removal, 1/2/3-player, performance/size/
load, controller/resolution/text, colour/effect/reduced-motion, and
localization seams — are elsewhere; where a fact of mine touches theirs, I
leave a one-line pointer rather than a second opinion.

**Sources read (all read-only).**

- Our tree, primary checkout `C:\Users\Monty\Documents\GitHub\GItS`, cited as
  repo `path:line`.
- The **live installed mod**, `…\Slay the Spire 2\mods\klee\`, and the live
  boot log `%APPDATA%\SlayTheSpire2\logs\godot.log`, both read 2026-08-26.
- The **base-game decompile** in the dispatch scratchpad, cited as
  `<Namespace.Type>::<member>` plus `sts2src/<path>:<line>`.
- **BaseLib 3.4.5** decompile in the scratchpad, cited as `baselib/<path>:<line>`.
- **Downfall** pinned at `lamali292/Downfall@32e61132052ae58e32cd33342d24136ffe18be12`,
  cited as `Downfall@32e6113:<path>:<line>`.

---

## Overview — the six things worth knowing

1. **Our shipped version string is not a legal semantic version, and the game
   says so on every boot.** `0.2-1159` fails the game's parser; the mod still
   loads, but the game holds no comparable version for us. This is a real
   defect whose only clean remedies touch LAW (the `MAJOR-AUTO` rule), so the
   remedy is [USER]'s pick, not a hygiene fix. (Case **P1**.)
2. **The manifest is the entire metadata surface, and it has exactly nine
   fields.** The game's `ModManifest` defines no URL, no licence, no credits,
   no tags, no icon path. Whatever a release wants to say about itself, it says
   in `name`, `author`, `description` — or outside the manifest entirely.
   (Case **P4**, and the field table below.)
3. **There is a real in-game credits surface and we use none of it.** BaseLib —
   which we already depend on — patches the base credits screen and takes
   registrations. Downfall uses it for team, art, sound, and nine localization
   teams. We register nothing and ship no `credits` loc table. (Case **P4**.)
4. **The packaged mod is 100% Tier F art.** All 872 rows of `art/SOURCES.tsv`
   are tier `F`, and the deployed package carries 272 loose card PNGs (69 MB)
   plus a 9.6 MB pck. Deploy's own handoff text says the zip must be handed off
   privately. A public release cannot ship today's package as-is; that is a
   rights call, not an engineering one. (Case **P8**.)
5. **The install route is manual-only and private.** Extract a gitignored zip
   into `mods\`; recipients also need BaseLib from the Workshop. There is no
   Workshop item, no release workflow, and no first-publish step. The base game
   exposes no in-game upload API — publishing is external tooling by design.
   (Cases **P7**, **N2**.)
6. **The BaseLib pin is three different numbers in three places and nothing
   joins them.** The manifest asks for `>= 3.3.6`, `STATE.md` records the
   frozen pin as `3.3.7.0`, and the machine compiles and runs against `3.4.5.0`.
   Whether we already use a 3.4-only API is UNKNOWN tonight. (Case **P6**.)

---

## The joined matrix

Read `DEFECT` as "something is wrong and could be fixed without asking anyone
about taste, rights, money, or scope" and `[USER] SCOPE` as "nothing is broken;
somebody has to decide what we are promising." A row can be both, and two rows
below are — the defect half and the scope half are named separately.

| # | Case | Reproduction | Current status | Automation candidate | Defect or scope call |
|---|---|---|---|---|---|
| P1 | Package version is not a valid semantic version | Boot the game with the mod installed; read `godot.log` | **DEFECT** (confirmed live) | **yes** — `Test-VersionPolicy` in `klee-mod/build/version.ps1`, pinned by `tier0/tests/test_manifest_version_gate.py` | Defect; its remedies all amend LAW → the pick is [USER]'s |
| P2 | `klee.dll` assembly version is never stamped (`1.0.0.0`) | Boot; read the initializer line in `godot.log` | **DEFECT** (cosmetic/diagnostic) | **yes** — `dotnet build` properties in `deploy.ps1`; assert in `validate.ps1` S2 | Defect |
| P3 | No `LICENSE` / `NOTICE` at the root of a public repo | `ls LICENSE* COPYING* NOTICE*` at repo root | **UNKNOWN by design** — no licence has been chosen | no (a file, not a check) — a presence check is trivial once the answer exists | **[USER] SCOPE** (rights) |
| P4 | No credits surface: `ModCredits` unused, no `credits` loc table | Grep `KleeCode` for `ModCredits`; grep the pck contract for `localization/*/credits.json` | **NOT-SUPPORTED-BY-DESIGN** today (mechanism exists and is unused) | **yes, partially** — a lint could require a `credits` table once one exists | Mechanism = technical; **who is credited and how = [USER] SCOPE** |
| P5 | No `mod_image.png`, so the modding screen shows an empty image slot | Open Mods in the main menu; compare against BaseLib/Downfall rows | **DEFECT-by-omission**, soft-failing (texture is set to `null`) | **yes** — `validate.ps1` S2 / S12 (pck contract) | Defect (the missing file); **what the image depicts = [USER] SCOPE** (art/rights) |
| P6 | Declared BaseLib `min_version` is hand-written and joins nothing | Read the three numbers in the three files | **DEFECT** (no gate); **UNKNOWN** whether currently violated | **yes** — `validate.ps1` S3 already parses both versions; the missing half is comparing the *compiled-against* dll | Defect |
| P7 | Install route is a private manual zip; no Workshop item, no release job | `.github/workflows/repo.yml`; `deploy.ps1 -Package` handoff text | **NOT-SUPPORTED-BY-DESIGN** (recorded refusal) | **yes, later** — a release workflow is buildable; the first Workshop publish is manual by Steam's design | **[USER] SCOPE** (ship) |
| P8 | The packaged payload is entirely Tier F art | `cut -f3 art/SOURCES.tsv \| sort \| uniq -c` | **NOT-SUPPORTED-BY-DESIGN** — Tier F never ships publicly | n/a — already gated by `.gitignore` and prose | **[USER] SCOPE** (rights) |
| P9 | CI builds and tests, but never packages | `.github/workflows/repo.yml:1-13` | **WORKS** as specified (documented NOT-doing list) | **yes** — the refusal is scoped, not technical | Scope call, already recorded |
| P10 | A shipped card PNG has no live row in the art plan | Join deployed `images/cards/*.png` against `art/plan.tsv` column `out` | **DEFECT** (ledger, 1 of 272) | **yes** — belongs to S17 / Lane B's ledger, not here | Defect — **owner: S17 / Lane B** |
| P11 | Manifest is written with a UTF-8 BOM | Hex-read the deployed `manifest.json` | **WORKS** — verified, not merely assumed | no | Non-finding |
| P12 | Zip handoffs accumulate in `dist/` | `ls klee-mod/dist` | **WORKS** as designed (overwrite refusal) | no | Informational |

---

## Case detail

### P1 — `0.2-1159` is not a valid semantic version — DEFECT

**What the game does.** `ModManager` parses every mod's declared version with
the game's own semver implementation and keeps the parsed object for
comparisons; when the parse fails it warns and leaves the mod's version `null`,
then loads the mod anyway
(`MegaCrit.Sts2.Core.Modding.ModManager`::`ProcessMod`,
`sts2src/MegaCrit.Sts2.Core.Modding/ModManager.cs:695-706`).

**Why ours fails.** `SemanticVersion.FromString` walks the string character by
character. A `-` is legal only once the parser has reached the *patch*
component; reaching a `-` while still in `Minor` throws
(`MegaCrit.Sts2.Core.Debug.SemanticVersion`::`FromString`,
`sts2src/MegaCrit.Sts2.Core.Debug/SemanticVersion.cs:102-107`). Our string is
`MAJOR-AUTO` with a two-part MAJOR — `0.2` then `-` — so it throws in `Minor`
every time. `+dirty` builds fail at the same character, earlier than the `+`
ever matters.

**Reproduction (already run tonight, no game launch required).** The live boot
log records it verbatim:

```
[WARN] Mod klee declares version 0.2-1159 which is not a valid Semantic Version
```

`%APPDATA%\SlayTheSpire2\logs\godot.log:140`, from the deployed build
`0.2-1159` (`…\mods\klee\manifest.json:6`, read 2026-08-26). The mod then loads
normally (`godot.log:141-176`, `Finished mod initialization for 'Teyvat Spire
Roster' (klee)`).

**Blast radius — measured, not assumed.**

- The Mods screen prints the **raw string**, not the parsed object
  (`NModInfoContainer`::`Fill`,
  `sts2src/…ModdingScreen/NModInfoContainer.cs:88-95`), so `0.2-1159` still
  *displays* correctly. The human-readable half of R70 survives.
- Multiplayer join compares a **game** version and an id-database hash, not mod
  versions (`sts2src/MegaCrit.Sts2.Core.Multiplayer.Game/JoinFlow.cs:89`), so
  the co-op desync diagnosis R70 was built for does not depend on this parse.
  (Co-op identity proper belongs to the 1/2/3-player family — pointer only.)
- The concrete loss: **any future mod that declares a dependency on `klee` with
  a `min_version` is refused**, because our parsed version is `null`
  (`ModManager.cs:810-812`, the `mod2.version == null` branch, which raises
  `MOD_ERROR.DEPENDENCY_VERSION_INVALID`). Nothing depends on us today, so this
  is a latent defect, not a live break.
- Plus one warning in every player's log forever, which is the kind of noise
  that trains people to ignore logs.

**Why this is not a hygiene fix.** `MAJOR-AUTO` is written into LAW —
"**manifest.json version is MAJOR-AUTO:** MAJOR bumped only by [USER] at
release" (`docs/current/LAW.md:390-392`, R68/R70) — and the whole policy is
argued in `klee-mod/build/version.ps1:1-33`. Changing the emitted shape amends
LAW, which the charter reserves to [USER].

**PROPOSED remedies, as a numbered pick list ([USER]'s pick; none is
recommended here).**

1. Emit `MAJOR.AUTO` — `0.2.1159` — treating AUTO as the patch component.
   Parses; sorts monotonically; the higher trailing number is still the newer
   build; MAJOR stays two-part and stays [USER]'s. Cost: the printed string
   changes shape, so old zip names and the `-` in prose ("the part after '-'",
   `klee-mod/build/deploy.ps1:215`) need a sweep.
2. Emit `MAJOR.0-AUTO` — `0.2.0-1159` — keeping the dash. Parses, and numeric
   prerelease parts compare numerically
   (`SemanticVersion.cs:209-232`). Caveat worth knowing before picking: a
   prerelease sorts *below* the same release version
   (`SemanticVersion.cs:201-208`), so `0.2.0-1159` reads as older than a plain
   `0.2.0`.
3. Emit `MAJOR.AUTO+dirty` for dirty trees instead of appending `+dirty` to a
   prerelease — metadata is legal after patch (`SemanticVersion.cs:115-139`)
   and is ignored in comparisons, which is arguably the correct semantics for
   "same commit, unknown contents".
4. Change nothing and accept the warning, recording the dependency consequence.

**Automation seam.** `Test-VersionPolicy` (`klee-mod/build/version.ps1:168-236`)
is already the gate deploy and validate share, and it is already unit-tested
from Python (`tier0/tests/test_manifest_version_gate.py:1-40`, which drives the
real PowerShell function rather than re-implementing it). A semver-shape
assertion belongs there. Note that test is Windows-only by nature, so it does
not run on the ubuntu CI (`.github/workflows/repo.yml:27-42`); a pure-Python
lint reading `klee-mod/Klee/manifest.json` would be the CI-visible half.

### P2 — the built dll carries no version — DEFECT (minor)

`godot.log:143` records `Calling initializer method of type KleeMod.KleeMod for
klee, Version=1.0.0.0` — the .NET default, because `KleeCode.csproj` sets no
`Version` / `AssemblyVersion` / `FileVersion`
(`klee-mod/KleeCode/KleeCode.csproj:3-13`) and `deploy.ps1` passes none to
`dotnet build` (`klee-mod/build/deploy.ps1:67`). Any crash report, Sentry
event, or user-supplied dll identifies itself as `1.0.0.0`. Downfall passes the
release version through to all three properties
(`Downfall@32e6113:.github/workflows/release.yml:100-106`). Automation seam:
one `/p:Version=` on the build line plus a `validate.ps1` S2 assertion that the
dll's `FileVersion` matches the staged manifest.

### P3 — no licence file — [USER] SCOPE (rights)

`ls LICENSE* COPYING* NOTICE*` at the repo root returns nothing (2026-08-26).
The repo is public (`origin = https://github.com/MontySteele/GItS.git`,
`.git/config`), and its own `.gitignore` reasons about that publicness
repeatedly (`.gitignore:11-12`, "repo is public"). Meanwhile the house *already*
has a licence discipline pointing inward: `vendor/README.md:20-27` refuses
copyleft precisely because "GItS is a public repo and that is a decision well
above a sprint's pay grade", and the one vendored component carries its
upstream MIT text and a provenance file
(`vendor/STS2_MCP/LICENSE:1`, `vendor/STS2_MCP/PROVENANCE.md:1-10`). So
inbound licence hygiene is handled and **outbound is simply unanswered**.

For contrast, not for imitation: Downfall is MIT, `Copyright (c) 2026 lamali`
(`Downfall@32e6113:LICENSE:1-3`).

**What a public release would have to carry here, as a pick list ([USER]'s):**
(1) a licence for our own code, or an explicit "all rights reserved"; (2) a
statement of what the licence does *not* cover (the art, see P8); (3) an
attribution notice for MIT-licensed vendored source if any of it ever ships in
a distributed artifact — today `vendor/STS2_MCP` is a bridge we build for
testing and is not in the mod package (`deploy.ps1:75-77` stages the manifest
and dll only), so nothing is owed yet.

### P4 — the credits surface: nine manifest fields, one unused BaseLib API — mechanism technical, content [USER]'s

**The manifest is the whole schema.** `ModManifest` declares exactly nine
JSON-mapped fields — `id`, `name`, `author`, `description`, `version`,
`has_pck`, `has_dll`, `dependencies`, `affects_gameplay`, `min_game_version`
(`sts2src/MegaCrit.Sts2.Core.Modding/ModManifest.cs:18-46`); `dependencies`
holds `{id, min_version}` pairs
(`sts2src/MegaCrit.Sts2.Core.Modding/ModDependency.cs:5-17`). There is **no**
url, licence, credits, tag, category, or icon-path field. We populate all nine
(`klee-mod/Klee/manifest.json:1-16`). Unknown JSON keys are simply not
deserialized, so inventing `"license": …` in the manifest would carry no
meaning to the game.

**What the player actually sees.** The Mods screen prints
`[gold]Author[/gold]: <author>`, `[gold]Version[/gold]: <version>`, then the
description, then any load errors in red
(`sts2src/…ModdingScreen/NModInfoContainer.cs:85-118`), with the row label
taken from `name` (`NModMenuRow.cs:135`). Today that reads *Author: Monty* —
which is the complete attribution surface the mod currently has.

**The real credits screen is reachable and unused.** BaseLib patches the base
credits screen (`NCreditsScreenPatch` postfixes `_Ready`,
`baselib/Baselib/Patches/UI/NCreditsScreenPatch.cs:10-15`) and exposes
`BaseLib.Utils.ModCredits.Register(modId, params Section[])`, where each
`Section` names a loc key and a layout (`Names`, `Roles`, `Columns3`) and may
nest children; the text is resolved from the `credits` loc table
(`baselib/Baselib/Utils/ModCredits.cs:9-61`). Downfall registers seven
top-level sections including a nested localization group
(`Downfall@32e6113:DownfallCode/DownfallMainFile.cs:90-106`) against
`Downfall/localization/eng/credits.json:1-32`, and separately attributes card
art per-card through its own `Artist` type and an `artists` loc table
(`Downfall@32e6113:DownfallCode/Abstract/DownfallCardModel.cs:21-24`;
`Downfall/localization/eng/artists.json:2-3`, key `ART_BY` = "Art by {name}",
rendered as a card hover tip).

**Ours.** `grep -rn "ModCredits" klee-mod/KleeCode` returns nothing, and the
packed loc surface is two English tables — `res://klee/localization/eng/
ancients.json` and `card_keywords.json`
(`klee-mod/assets/klee.pck.contract.txt:50-51`). No `credits`, no `artists`,
no second language. (Language coverage itself belongs to the localization-seams
family — pointer only.)

**[USER] SCOPE, as a pick list:** (1) whether a credits screen entry exists at
all; (2) if yes, which sections and which names — including how Claude-authored
code and pipeline work is or is not named; (3) whether per-card art attribution
is wanted, which only becomes answerable once P8's rights question is answered.
Nothing here is decided by this document.

### P5 — no mod image on the Mods screen — DEFECT-by-omission

The Mods screen loads `res://<mod id>/mod_image.png` if it exists and otherwise
sets the texture to `null`
(`sts2src/…ModdingScreen/NModInfoContainer.cs:74-83`). That path is pck-mounted
only, so a loose PNG beside the dll cannot satisfy it. Our pck contract has no
such resource (`klee-mod/assets/klee.pck.contract.txt`, 134 lines, no
`mod_image`), and `klee-mod/pck-src/` holds only `klee/`, `furina/`, and
`shared/` scene sources. Downfall ships one per character folder
(`Downfall@32e6113:Downfall/mod_image.png`, and ten siblings). Fails soft — an
empty slot, no error. Automation seam: assert its presence in `validate.ps1`
S2, or in the S12 pck-contract rule (`klee-mod/build/validate.ps1:856`). The
image itself is art, so what it depicts is [USER]'s and is bound by P8.

### P6 — the BaseLib pin joins nothing — DEFECT

Three numbers, three files, no gate between them:

| Where | Number | Evidence |
|---|---|---|
| What we *ask players for* | `>= 3.3.6` | `klee-mod/Klee/manifest.json:11-14` |
| What `STATE.md` records as the frozen pin | `3.3.7.0` | `docs/current/STATE.md:159` |
| What we *compile and run against* on this machine | `3.4.5.0` | installed `BaseLib.json` version `v3.4.5` (Workshop item `3737335127`); `godot.log:126` `Starting PatchAll for assembly BaseLib, Version=3.4.5.0` |

`3.3.6` appears nowhere but the manifest itself (grep across `tools/`,
`klee-mod/`, `docs/current/` returns only the manifest, the staged copy, and
two comments in `version.ps1`). The deploy gate *does* compare properly — it
parses both sides and fails when the installed version is lower
(`klee-mod/build/version.ps1:180-200`, the R70 fix for audit 3.5) — but it can
only ever check `installed >= declared`. Since the installed version is the one
we compile against, that comparison passes *by construction on the build
machine* and can never notice that the declared floor has drifted below what
the code actually needs.

**The failure it permits:** we bind to an API added in BaseLib 3.4.x, ship a
manifest saying 3.3.6 is enough, and a player on 3.3.6 passes the game's
dependency gate and then crashes on a missing member. **UNKNOWN tonight**
whether we already do this: proving it needs a member-level diff of BaseLib
3.3.6/3.3.7 against 3.4.5, and only 3.4.5 is available locally. I did not
approximate it.

**Automation seam (yes):** at deploy time, read the `FileVersion` of the
`BaseLibDll` the build actually referenced (`klee-mod/local.props`) and require
it to satisfy the declared `min_version`; louder still, require the declared
floor to be *deliberately* raised rather than silently outgrown. The gate
already has both version parsers.

### P7 — install route: manual, private, one-way — [USER] SCOPE (ship)

**What exists.** `deploy.ps1 -Package` zips the validated stage into
`klee-mod/dist/klee-v<version>.zip` and prints the handoff instructions:
extract into `<game>\mods\`, land as `mods\klee\`, recipients also need BaseLib
from the Workshop and game `>= min_game_version`, and all co-op peers must run
this exact build (`klee-mod/build/deploy.ps1:200-216`). The zip is refused if a
file of that name exists, because same-name-different-contents is the desync
the version scheme exists to prevent (`deploy.ps1:186-199`). `dist/` and
`*.zip` are gitignored (`.gitignore:44,50`), and the script's own header says
the zip carries Tier F art and must be handed off **privately**
(`deploy.ps1:28-30`).

**What does not exist.** No Workshop item for `klee` (subscribed items on this
machine are BaseLib `3737335127`, Downfall `3747508091`, PengoTarot
`3747679239`). No release workflow: CI is three ubuntu jobs — pytest, lints,
and an R-number namespace lint — with an explicitly recorded NOT-doing list of
"no Windows runner, no pck build, no deploy automation, no coverage number, no
scheduled runs" (`.github/workflows/repo.yml:1-13`, pointing at
`docs/current/rationale/serenitea-g3-ci-proposal.md`). No changelog file, no
release notes template, no tag convention for releases.

**What a Workshop route would require, from a working example.** Downfall's
release is two workflows: one bumps versions and pushes an annotated tag whose
message carries a `steam=true|false` flag; the tag triggers the build, the zip,
a GitHub release with a generated banner naming the minimum game version and
the BaseLib requirement, and finally a Workshop upload
(`Downfall@32e6113:.github/workflows/release.yml:108-148`). Note two things a
first-time publisher has to supply that no workflow generates: the upload step
takes a **pre-existing** `publishedFileId` (`release.yml:141-147`), so the item
must be created by hand first, and Steam credentials plus a shared secret for
TOTP live as repo secrets. Workshop-side metadata — preview image, description,
visibility, tags — is Steam's surface, not the manifest's, and is set on the
item rather than in the package.

**Confirmed absence of an in-game route:** the base-game decompile contains no
`SteamUGC.CreateItem` or `SubmitItemUpdate` call anywhere; the only UGC calls
are read-side (`GetSubscribedItems`, `GetItemInstallInfo`,
`sts2src/MegaCrit.Sts2.Core.Modding/ModManager.cs:581-606`). Publishing is
external tooling by design.

**[USER] SCOPE, pick list:** (1) public release at all — yes/no; (2) if yes,
Workshop, GitHub release, both, or continued private handoff; (3) who holds the
Steam account and secrets; (4) whether release automation is built before or
after the first manual publish. **None of these is answerable before P8.**

### P8 — the package is entirely Tier F art — [USER] SCOPE (rights), the gating one

Every one of the 872 rows in `art/SOURCES.tsv` carries tier `F`
(`cut -f3 art/SOURCES.tsv | sort | uniq -c` → `872 F`, plus the header), and
858 of the 872 source URLs point at one wiki CDN host. The art plan's own
header says it plainly: "Tier F — private build only, never ships"
(`art/plan.tsv:1`). LAW-side, `docs/current/OPERATIONS.md:296` states that Tier
F art never ships and never enters the repo, and only the ledgers and tools are
tracked.

The live deployed package is therefore, by content: `klee.dll` (877 KB),
`klee.pck` (9.6 MB), the pck contract, `manifest.json`, and **272 loose card
PNGs totalling 69 MB** (`…\mods\klee\images\cards`, counted 2026-08-26). Recent
handoff zips run ~80 MB (`klee-mod/dist/klee-v0.2-826.zip`, 80,592,322 bytes).
(Size and load-time consequences belong to the performance/size family —
pointer only.)

**What this means for a public release, stated without deciding anything:** the
current package cannot be the public artifact. A public release requires either
original or licence-cleared art for every packaged surface, or a package that
ships no art and falls back to placeholders — the fallback path exists
(`deploy.ps1:139-147`, "cards will fall back to BETA placeholder"). Which of
those, and on what timeline, is [USER]'s call and is exactly the question S17
is inventorying from the coverage side. I make no rights judgement here.

### P9 — CI packages nothing — WORKS as specified

Recorded above under P7. Listed separately because it is the automation
*seam* for most of this file: the three jobs run on ubuntu and touch no
Windows-only gate, so any packaging or metadata check that must run in CI has
to be pure Python reading committed files. Everything that needs the game, the
pck, or PowerShell stays in `validate.ps1` on the deploy machine.

### P10 — one shipped card image has no live plan row — DEFECT (owner: S17 / Lane B)

Joining the 272 deployed card filenames against the `out` column of
`art/plan.tsv` leaves exactly one deployed file with no live row:
`spark_knight_style.png`. It is not unexplained — the plan records that the row
was deliberately commented out when its pick was withdrawn, and notes that
"spark_knight_style's PNG is already on disk" so it keeps shipping
(`art/plan.tsv:185-187`, row itself commented at `art/plan.tsv:201`). Its
provenance still exists in the other ledger (`art/SOURCES.tsv:142`, tier F).

I record it here only because it is a *package-contents* fact — the shipped
payload contains a file the live ledger no longer describes. The general form
of this (stale rows, orphan outputs, ledger-vs-package joins) is S17's and Lane
B's; do not fix it from this file.

### P11 — the UTF-8 BOM is tolerated — NON-FINDING (verified, not assumed)

The deployed `manifest.json` begins with a UTF-8 BOM, because PowerShell 5.1's
`Set-Content -Encoding utf8` writes one (`klee-mod/build/deploy.ps1:88`). The
mod loads regardless (`godot.log:141-176`), and the game's own dependency,
BaseLib, ships a manifest with a BOM as well
(`…workshop\content\2868840\3737335127\BaseLib\BaseLib.json`). Our own tooling
strips it defensively on the read side (`klee-mod/build/version.ps1:35-42`).
Nothing to do.

### P12 — old handoff zips accumulate — informational

`klee-mod/dist/` holds five zips from `0.2-218` (2026-07-27) through `0.2-826`
(2026-08-16), ~390 MB total, all gitignored. This is the overwrite-refusal rule
working as designed (`deploy.ps1:186-199`); nothing prunes them, and nothing is
supposed to. Housekeeping, not a defect.

---

## Manifest field-by-field, ours against the schema and against Downfall

| Field | Schema | Ours | Downfall | Note |
|---|---|---|---|---|
| `id` | `ModManifest.cs:18-19` | `klee` | `Downfall` | Also the pck resource root (`res://klee/…`) and the mod-image path. |
| `name` | `:21-22` | `Teyvat Spire Roster` | `Downfall` | Row label on the Mods screen (`NModMenuRow.cs:135`). |
| `author` | `:24-25` | `Monty` | `lamali` | The only attribution field the schema has. |
| `description` | `:27-28` | one sentence naming Klee, Furina, reactions, Companions | template boilerplate | Ours is **stale**: it omits Kokomi, who ships (`STATE.md` roster; `godot.log:176` "Klee, Furina and Kokomi registered"). Hygiene-sized, but the text is player-facing copy → [USER]'s to word. |
| `version` | `:30-31` | `0.2-1159` | `0.1.16` | See P1: theirs parses, ours does not. |
| `has_pck` / `has_dll` | `:33-37` | both true | both true | Lying either way is a silent no-op mod; `validate.ps1` S2 checks both against the staged files (`validate.ps1:78-91`). |
| `dependencies` | `:39-40` | BaseLib `>= 3.3.6` | BaseLib `>= 3.4.5` | See P6. |
| `affects_gameplay` | `:42-43` | true | true | BaseLib keys gameplay enablement off it (`godot.log:183`). |
| `min_game_version` | `:45-46` | `0.107.1` | `0.107.1` | Verified live against `release_info.json` (`version.ps1:238-252`); installed game is `v0.107.1`, commit `59260271`. Matches. |
| *absent* | — | — | — | No url, licence, credits, tags, category, or icon field exists in the schema. |

---

## What a public release would have to carry — the inventory, not a plan

Grouped by who owns the answer. Nothing below is scheduled, promised, or
recommended.

**Answerable as engineering (no taste, rights, money, or scope):**

1. A version string the game can parse (P1 — but the *shape* is a LAW pick).
2. A stamped assembly version (P2).
3. A gate joining the declared BaseLib floor to the one we compile against (P6).
4. A `mod_image.png` present in the pck, once an image exists (P5).
5. A description that names the shipped roster (P4 table row — wording is
   [USER]'s).
6. A release/packaging job, if and when there is something to release (P7/P9).

**[USER]'s, and blocking:**

1. **Public release, yes or no** — everything else is downstream.
2. **Art rights** (P8): original, cleared, or art-free package.
3. **Licence** for our code, and an explicit statement about what it excludes
   (P3).
4. **Credits content** — sections, names, and whether card art is attributed
   per-card (P4).
5. **Distribution channel and the account that owns it** (P7).
6. **The version-format pick** (P1), because it amends LAW.

---

## UNKNOWN

- Whether our C# already uses a BaseLib member that did not exist at the
  declared floor `3.3.6` (P6). Needs BaseLib 3.3.6/3.3.7 assemblies to diff;
  only 3.4.5 is on this machine. Not approximated.
- Whether the Workshop route imposes package-shape requirements beyond
  "a folder containing the manifest and payload" — Downfall uploads its built
  mod folder directly (`release.yml:145`), which is suggestive but is one
  example, not a specification.
- Whether the base game or BaseLib enforces any manifest field's *format*
  beyond version parsing (id character set, name length, description length).
  I found no such validation in `ModManifest.ReadFromStream`
  (`ModManifest.cs:48-86`), but I did not read every consumer of every field.

## NON-FINDINGS

- **N1 — no manifest field for licence, url, credits, or tags.** Searched the
  full `ModManifest` type; the schema is nine fields
  (`ModManifest.cs:18-46`). Not a gap in our manifest — the surface does not
  exist.
- **N2 — no in-game Steam Workshop upload path.** No `CreateItem` /
  `SubmitItemUpdate` anywhere in the base-game decompile; UGC use is read-side
  only (`ModManager.cs:581-606`). Publishing is external tooling.
- **N3 — the BOM is not a defect** (P11), verified against a live boot and
  against BaseLib's own shipped manifest.
- **N4 — no packaging-side rights metadata is missing from the *package*,**
  because there is nowhere in the package to put it. If rights text must ship,
  it ships as a file beside the dll or as loc text, not as manifest metadata.

## Search boundary

Read: our `klee-mod/**` build and manifest surface, `tools/build_pck.ps1`,
`.github/workflows/repo.yml`, `.gitignore`, `README.md`, `vendor/`, the two art
ledgers, the live installed mod folder, one live boot log, the base-game
decompile's `MegaCrit.Sts2.Core.Modding` and `…ModdingScreen` namespaces plus
`SemanticVersion`, BaseLib 3.4.5's `ModCredits` and credits patches, and
Downfall's manifest, release workflows, credits/artists loc tables, and the
`ModCredits` call site. **Not read:** the full 1057-line `validate.ps1` (rules
S4–S16 were sampled by header, not line by line), the other six S20 families'
surfaces, `docs/current/rationale/serenitea-g3-ci-proposal.md` (cited only as
the recorded refusal it is named as), and anything requiring the game to be
launched. No git command was run anywhere; no file outside this one was written.

## Cross-family pointers (one line each, no second opinions)

- Mod-model **ID collisions** warned at `godot.log:224-225`
  (`FanfareMeterPower` twice; `ExplosiveFrags` card vs relic, "might break
  multiplayer") → save/ID and 1/2/3-player families.
- `res://kokomi/model/combat.tscn` **missing from the shipped pck**
  (`godot.log:163`, falls back to base behaviour) → S16/S17 and Lane C's
  package-contents gate.
- **69 MB of loose PNGs plus a 9.6 MB pck, ~80 MB zips** → performance/size/load
  family.
- **Two English loc tables, no other language** → localization-seams family.
- **Stale/orphan ledger rows** (P10) → S17 and Lane B.
- **Deployed build is `0.2-1159`**, while `PREFLIGHT.md` recorded `0.2-1155` at
  dispatch time; [USER] redeployed during the evening. Informational, and it
  means any figure here is pinned to the 20:46 build id
  `20260826-204650+98fb3a0` (`godot.log:147`).

---

## What this does NOT establish

It does not establish that a public release is desirable, feasible, legal, or
scheduled; it does not choose a licence, a channel, a version format, an art
rights position, or a single name for a credits screen. It does not prove the
mod is broken — the mod loads and runs on the live build. It does not measure
package size against any budget, does not evaluate localization coverage, and
does not assess save, multiplayer, accessibility, or performance readiness.
Where a fix would touch LAW or a ratified artifact, this file names the pick
and stops.
