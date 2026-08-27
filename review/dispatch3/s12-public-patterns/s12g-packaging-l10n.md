# S12g — Packaging, localization, distribution (public StS2 mod patterns)

> **This document decides nothing.** It is a cited description of how one
> released public Slay the Spire 2 mod builds, versions, translates, and ships
> itself. Every "we could" below is written as a question, never a proposal.
> Reference-reading only (charter §3.7): nothing here was copied into our tree.

**Primary source:** `lamali292/Downfall` pinned at
`32e61132052ae58e32cd33342d24136ffe18be12` (commit dated 2026-08-26, message
`fix(csproj): adjust default submods and streamline property group
configuration`). Cited below as `Downfall@32e6113:<path>:<line>`.
**License:** MIT, "Copyright (c) 2026 lamali" (`Downfall@32e6113:LICENSE:1-3`).
**Our side, read-only:** `C:\Users\Monty\Documents\GitHub\GItS\klee-mod\**` and
`C:\Users\Monty\Documents\GitHub\GItS\tools\build_pck.ps1`.

---

## Overview

Downfall is a released, Workshop-distributed StS2 mod shipping **eleven
characters out of one package**, and it answers with working code five things
we have not settled.

1. **The package is three files in a folder** — `Downfall.dll`, `Downfall.json`,
   `Downfall.pck` (plus a dev-only `.pdb`). Same manifest shape we already use.
2. **Multi-character is a build switch:** one MSBuild property lists which
   character folders compile and pack. Two are in the repo and not in that list.
3. **Localization is a committed file tree** — one folder per character, per
   language, one JSON per table — plus a Harmony patch, because bundling breaks
   the base game's own loc discovery.
4. **Translation is outsourced** to a hosted platform (Paratranz), one project
   per language, pulled nightly by CI and committed back to `main`.
5. **Release is two workflows:** one bumps versions and pushes a tag; the tag
   triggers the build, the zip, the GitHub release, and the Workshop upload.

The transferable finding is that localization is a source tree with a supply
chain, not a string table filled in at the end.

---

## Pattern table A — build outputs and package shape

| Pattern | Purpose | Pinned source | Base type it hangs off |
|---|---|---|---|
| Three-file mod package | `mods/<ModId>/` gets `<ModId>.dll` + `<ModId>.json` + `<ModId>.pck`; `.pdb` copied only when it exists | `Downfall@32e6113:Downfall.csproj:48-60` | — (MSBuild `Copy` target; no StS2 type) |
| Manifest fields | `id`, `name`, `author`, `description`, `version`, `has_pck`, `has_dll`, `min_game_version`, `dependencies[{id,min_version}]`, `affects_gameplay` | `Downfall@32e6113:Downfall.json:2-17` | Read back at runtime via `ModManager.GetLoadedMods()` → `mod.manifest.version` (`DownfallMainFile.cs:123-128`) |
| Submod gating by MSBuild property | One property decides which character folders are compiled *and* packed; default list is nine of eleven | `Downfall@32e6113:Downfall.csproj:18,21,27-29,37-46` | — (MSBuild item group) |
| Per-submod compile fan-in | `<Compile Include="%(Submod.Identity)Code/**/*.cs">` — code folder is `<Name>Code`, asset folder is `<Name>` | `Downfall@32e6113:Downfall.csproj:39-41` | — (MSBuild) |
| Localization files as analyzer input | Same target adds `<AdditionalFiles Include="%(Submod.Identity)/localization/**/*.json">` so a Roslyn analyzer can see them | `Downfall@32e6113:Downfall.csproj:41` | Roslyn `AdditionalFiles` → `Alchyr.Sts2.ModAnalyzers` |
| PCK packed by a headless Godot script | `godot --headless -s build/pack_mod.gd -- <out.pck> <folder…>`, using Godot's `PCKPacker` at alignment 16 | `Downfall@32e6113:Downfall.csproj:100-104`; `build/pack_mod.gd:25-31` | Godot `PCKPacker`, `SceneTree` |
| Pack the *imported* asset, not the source | Raw `.png/.jpg/.webp/.ogg/.mp3/.wav` are skipped; the `.import` file's `remap` path (the `.ctex` in `.godot/imported`) is packed instead | `Downfall@32e6113:build/pack_mod.gd:3-6,83-92,97-111` | Godot `ConfigFile` / `.import` remap keys |
| `.gdignore` as a pack-exclusion marker | A folder holding a `.gdignore` is skipped entirely by the packer (and by Godot's importer) | `Downfall@32e6113:build/pack_mod.gd:67-68`; markers at `ImageGen/.gdignore`, `*/scenes/character/images/.gdignore` | Godot filesystem convention |
| Publicized game assembly | `Krafs.Publicizer` opens `sts2` and four named `BaseLib` members for compile-time access | `Downfall@32e6113:build/mod.build.props:141,146-157` | `Krafs.Publicizer` 2.3.0 |
| Compile-time reference: installed game *or* NuGet | If `Sts2DataDir` exists, reference the real `sts2.dll`/`0Harmony.dll`; otherwise pull `lamali.StS2.RefLib` reference assemblies (this is what makes CI work without owning the game) | `Downfall@32e6113:build/mod.build.props:109-133` | — (MSBuild condition) |
| Generated art is gitignored, built before import | `ImageGen` writes atlases into `*/images/atlases|powers|relics|enchantments`, all gitignored, all regenerated in CI before Godot imports | `Downfall@32e6113:.gitignore:58-61`; `.github/workflows/publish.yml:94-98` | — (standalone `dotnet run` tool) |
| Base-game assets reached by junction | Thirteen root folders (`src`, `images`, `scenes`, `localization`, `banks`, …) are junctions into a GDRE-extracted copy of the base game and are gitignored at the repo root | `Downfall@32e6113:build/link-assets.ps1:22-40`; `build/mod.build.props:54,57-62`; `.gitignore:43-55` | — (Windows junction / `CreateSymbolicLink`) |
| UID scrubber | `.tscn`/`.tres` files get `uid="uid://…"` stripped, with explicit refusal to follow junctions out of the project | `Downfall@32e6113:build/nuke_uids.py:16,21-33,67-76` | Godot resource UIDs |

## Pattern table B — release and distribution

| Pattern | Purpose | Pinned source | Base type it hangs off |
|---|---|---|---|
| Two-stage release: prepare → tag → build | `release-prepare.yml` bumps versions, commits `Release vX.Y.Z`, pushes an **annotated tag whose message carries `steam=true|false`**; the tag push triggers `release.yml`, which reads the flag back out of the tag | `Downfall@32e6113:.github/workflows/release-prepare.yml:28-66`; `release.yml:3-5,31-36` | — (GitHub Actions) |
| Version bumped in two files by regex | `<Version>/<AssemblyVersion>/<FileVersion>` in `build/mod.build.props` and `"version"` in `Downfall.json`, rewritten with `perl -0pi` at prepare time and re-synced with `sed` at release time | `release-prepare.yml:30-48`; `release.yml:75-78`; values at `build/mod.build.props:13-15` and `Downfall.json:6` | — (text substitution) |
| Manifest dependency floor auto-synced from the NuGet pin | `BaseLibVersion` is copied into `Downfall.json`'s `dependencies[BaseLib].min_version`, with a comment warning the two may not be the same number | `release-prepare.yml:54-56` | — |
| Build-time secret injection | CI overwrites a committed `BuildSecrets.cs` (whose checked-in value is `null`) with the real metrics key from a repo secret | `release.yml:88-95`; `Downfall@32e6113:DownfallCode/Data/BuildSecrets.cs:1-6` | `ModManager.OnMetricsUpload` (`DownfallMainFile.cs:50`) |
| Release artifact = zip of the mod folder | `find … -name '*.pdb' -delete`, then `zip -r Downfall-<version>.zip Downfall` | `release.yml:108-115` | — |
| GitHub release with a generated banner | `gh release create` with `--generate-notes` plus two authored lines naming the StS2 floor and the BaseLib requirement ("not included — install it separately") | `release.yml:117-130` | GitHub CLI |
| Steam Workshop upload from CI | `steam-workshop-deploy@v4` with appId `2868840`, `publishedFileId` from a repo *variable*, TOTP generated in-workflow from a shared secret | `release.yml:132-149` | Steam Workshop (item pre-created outside CI) |
| Continuous dev artifact | `publish.yml` builds on every push to `main` and every PR, uploads `output/mods/Downfall` as a 14-day artifact, skips commits starting `Release v`, cancels superseded runs | `publish.yml:2-20,115-120` | — |
| Engine + extension pinned as CI env vars | `MEGADOT_VERSION: 4.5.1-m.14`, `SPINE_VERSION: 4.2-4.5.1-stable`, both downloaded and cached by key | `publish.yml:15-17,42-49,77-92`; local equivalent at `build/setup.ps1:21-43` | — |
| Cold-import retry | Godot import is run twice ("first cold import often exits non-zero while bootstrapping `.godot/`") | `publish.yml:100-105`; `release.yml:83-86` | Godot `--headless --import` |
| Subscribe route advertised in the README | Steam Workshop badge, item `3747508091` | `Downfall@32e6113:README.md:7` | — |
| Contribution route | Fork, branch, PR to default branch; hand review | `Downfall@32e6113:contribution-guidelines.md:4-5` | — |

## Pattern table C — localization topology

| Pattern | Purpose | Pinned source | Base type it hangs off |
|---|---|---|---|
| Path convention `res://<ModId>/localization/<lang>/<table>.json` | The base game's own discovery shape for modded loc tables | `Downfall@32e6113:DownfallCode/Patches/GetModdedLocTablesPatch.cs:18` | `MegaCrit.Sts2.Core.Modding.ModManager.GetModdedLocTables(language, file)` |
| Bundled-submod loc registry + Harmony postfix | Because only one `Mod` entry ("Downfall") registers, the base lookup never checks `res://Champ/localization/…`; each submod calls `Register(ModId)` and a postfix appends every registered id's path if `ResourceLoader.Exists` | `Downfall@32e6113:DownfallCode/Localization/BundledSubmodLocRegistry.cs:3-21`; `Patches/GetModdedLocTablesPatch.cs:8-22`; call sites e.g. `ChampCode/ChampMainFile.cs:34` | Harmony postfix on `ModManager.GetModdedLocTables`; `Godot.ResourceLoader` |
| Custom table registration | A table name the base game does not know (`champ_stances`, `gems`, `ghostflames`, `encode`, `chants`, `card_modifiers`, `artists`) must be registered before use | `DownfallMainFile.cs:39-40`; `ChampMainFile.cs:27`; `GuardianMainFile.cs:31`; `HexaghostMainFile.cs:31`; `AutomatonMainFile.cs:29`; `AwakenedMainFile.cs:29` | `CustomLocTableManager.Register(string)` — **BaseLib**: not defined anywhere in the Downfall tree, and `using BaseLib.Utils;` is the only candidate import (`ChampMainFile.cs:1`) |
| Key scheme `<PREFIX>-<ENTRY>.<field>` | e.g. `CHAMP-ADRENAL_ARMOR.title` / `.description`, `DOWNFALL-ECHO.card_title`; prefix is the mod/character, entry is UPPER_SNAKE | `Downfall@32e6113:Champ/localization/eng/cards.json:2-3`; `Downfall/localization/eng/card_keywords.json:3-5` | `MegaCrit.Sts2.Core.Localization.LocString(table, key)` (`DownfallMainFile.cs:55`) |
| Values are SmartFormat templates + BBCode | `{Block:diff()}`, `{Cards:plural:a card\|{Cards:diff()} cards}`, `[gold]…[/gold]` | `Champ/localization/eng/cards.json:2,8` | SmartFormat 3.x; game rich-text |
| Table names in use (25 distinct) | `powers` 120 files, `cards` 110, `relics` 107, `events` 71, `ancients` 70, `characters` 67, `card_keywords` 62, `static_hover_tips` 61, `potions` 34, `enchantments` 33, `combat_messages` 27, `gameplay_ui` 25, `card_selection` 22, `monsters` 18, then `ghostflames`/`settings_ui`/`rest_site_ui`/`gems`/`encode`/`champ_stances`/`card_modifiers`/`artists`/`afflictions` (7 each), `chants` 6, `credits` 5 | file census over `*/localization/*/ *.json` at `Downfall@32e6113` (counted 2026-08-26) | — |
| Eleven languages, English as source | `eng` (116 files) `jpn` 115, `zhs` 114, `ita` 111, `kor` 109, `fra` 102, `rus` 97, `spa` 40, `deu` 34, `ptb` 34, `zht` 30 | same census | — |
| Hosted translation platform, one project per language | Nine Paratranz project ids: zhs, deu, fra, kor, jpn, rus, ita, ptb, spa | `Downfall@32e6113:.github/configs/paratranz.json:2-12` | Paratranz REST API |
| Nightly pull, committed by a bot | `download.yml` runs `cron: "0 0 * * *"`, writes files, commits "Sync translations from Paratranz" and pushes with a deploy key | `.github/workflows/download.yml:4-5,16-18,33-44` | — |
| Source push and per-language push are manual | `upload.yml` (English source → every project) and `upload_lang.yml` (one chosen language's existing translations) are `workflow_dispatch` only | `upload.yml:5`; `upload_lang.yml:4-19` | — |
| Only reviewed strings come back, in source key order | `para_download.py` keeps items with `stage >= 1`, then rebuilds the output file by walking the **English** file's keys and emitting only those that were translated | `.github/scripts/para_download.py:35-39,42-66` | — |
| Compile-time localization analyzer | `.editorconfig` sets `STS001` (missing localization keys) and `STS002` (no localization JSON found) to `warning`, and `STS003` too | `Downfall@32e6113:.editorconfig:4-12` (STS001 at `:5-6`, STS002 at `:8-9`); package `Alchyr.Sts2.ModAnalyzers` 0.1.9 at `build/mod.build.props:142` | NuGet package page (retrieved 2026-08-26): STS001 "Symbol must have defined localization" (declared **Error**), STS002 "Localization files must be added as additional files for analysis", STS003 "Model should inherit a CustomModel", STS004 "Model must be added to a pool using PoolAttribute" — https://www.nuget.org/packages/Alchyr.Sts2.ModAnalyzers/0.1.9 |
| Plural rules patched for Chinese | SmartFormat has no `zh` plural delegate; a Harmony postfix on `LocManager.LoadLocFormatters` reflectively assigns the English rule to `zh` | `Downfall@32e6113:DownfallCode/Patches/PluralRulesPatch.cs:8-19` | Harmony postfix on `MegaCrit.Sts2.Core.Localization.LocManager.LoadLocFormatters`; `SmartFormat.Utilities.PluralRules` |
| Translator credit as a first-class loc surface | `ModCredits.Register` declares a `LOC` section with per-language children (`LOC_ZHS`, `LOC_FRA`, `LOC_ITA`, `LOC_RUS`, `LOC_KOR`, `LOC_JPN`); `LOC_PTB` and `LOC_DEU` are commented out | `DownfallCode/DownfallMainFile.cs:90-107` | `ModCredits` — **BaseLib** (not defined in-tree) |

---

## Dependency pins, in one place

| Thing | Declared value | Where |
|---|---|---|
| StS2 floor (manifest) | `0.107.1` | `Downfall.json:9` |
| StS2 compile flag | `DefineConstants … ;V107` | `Downfall.csproj:23` |
| StS2 reference assemblies (CI, no game installed) | `lamali.StS2.RefLib` **0.111.0-beta** | `build/mod.build.props:130` |
| BaseLib (compile) | `Alchyr.Sts2.BaseLib` **3.4.5** | `build/mod.build.props:20,140` |
| BaseLib (runtime floor, manifest) | **3.4.5** | `Downfall.json:13` |
| Godot SDK / engine | `Godot.NET.Sdk/4.5.1`; MegaDot `4.5.1-m.14` in CI | `Downfall.csproj:1`; `publish.yml:16` |
| spine-godot extension | `4.2-4.5.1-stable`, fetched from an S3 URL at setup and in CI | `build/setup.ps1:22`; `publish.yml:17,81-85` |
| .NET | `TargetFramework net9.0`, `LangVersion 14`; CI installs `9.0.x` | `Downfall.csproj:5-6`; `publish.yml:29-31` |
| Analyzers / tooling | `Krafs.Publicizer` 2.3.0, `Alchyr.Sts2.ModAnalyzers` 0.1.9 | `build/mod.build.props:141-142` |
| BaseLib acquisition for players | Not bundled. BaseLib's own README: "download the `.dll`, `.pck`, and `.json` from releases and put them in `Slay the Spire 2/mods`" | https://github.com/Alchyr/BaseLib-StS2 (retrieved 2026-08-26, page not commit-pinned); Downfall's release banner says the same in one line (`release.yml:121-126`) |

---

## Gotchas

1. **Two version sources of truth, kept in step by regex.** `build/mod.build.props`
   holds `<Version>/<AssemblyVersion>/<FileVersion>`; `Downfall.json` holds
   `"version"`. `release-prepare.yml` rewrites both with `perl`, and
   `release.yml` rewrites the manifest again with `sed` from the tag name. A
   hand edit to one of them drifts silently until a release run overwrites it.
2. **The manifest's BaseLib floor is copied from the *NuGet* version, and the
   workflow says so out loud:** "NuGet BaseLib version may differ from the
   in-game BaseLib mod version the loader checks — remove this line if they
   don't match" (`release-prepare.yml:54-56`). A self-documented hazard.
3. **The repo contradicts itself on .NET.** README requires "C# .Net 10"
   (`README.md:37,88`); `Downfall.csproj:5` targets `net9.0`; CI installs
   `9.0.x` (`publish.yml:29-31`). Take the csproj.
4. **The reference assemblies are newer than the declared floor.** RefLib
   `0.111.0-beta` compiles against a game newer than `min_game_version 0.107.1`,
   and the gap is absorbed at runtime by feature *detection*, not by version
   numbers: `GameVersion.HasCardLocation` / `HasNCardUpdatePortrait` probe for a
   type and a method, and the patch list branches on them
   (`DownfallCode/Compatibility/GameVersion.cs:9-14`;
   `DownfallCode/Utils/PatchManager.cs:73-82`).
5. **One package with many characters costs you a localization patch.** This is
   the single most important gotcha in this file: bundling means one `Mod` entry
   registers, so the base game never looks in the other characters' loc folders.
   Downfall pays for it with a registry plus a Harmony postfix
   (`BundledSubmodLocRegistry.cs:3-11` states the problem in its own words).
6. **Partial translations are the normal state, by design.** `para_download.py`
   writes only keys at `stage >= 1`. `Champ/localization/deu/cards.json` is a
   file of `.title` rows with no `.description` rows at all. This only works if
   a missing key falls back per-key to English — see NON-FINDING N1.
7. **`zht` (traditional Chinese) has no Paratranz project.** Thirty files exist
   in the tree; `configs/paratranz.json` lists nine languages and `zht` is not
   among them, so neither the nightly pull nor either upload workflow touches
   it. It is a manual or legacy set.
8. **Two character trees ship in the repo but not in the build.** `Collector`
   and `Gremlins` are absent from the default `Submods` list
   (`Downfall.csproj:18`, `local.props.example:11`), removed from the
   `sts2.csproj` compile set (`sts2.csproj:34-35`), and excluded by name from
   both Paratranz scripts (`para_upload.py:56`,
   `para_upload_translations.py:61`). The pinned commit's own message is about
   adjusting that list.
9. **Localization can break formatting, not just wording.** SmartFormat ships no
   `zh` plural rule, so `{n:plural:…}` in Chinese needed a reflective patch.
10. **The build is not self-contained.** Thirteen root folders are junctions
    into a GDRE-extracted copy of the base game and are gitignored at the root
    (`.gitignore:43-55`) while the *same folder name* under a character
    directory is committed (`Champ/localization/**` is tracked). Note this cuts
    against our own standing rule — never link a gitignored asset tree into a
    worktree (`CLAUDE.md` norms, `OPERATIONS.md`). Same hazard, opposite policy.
11. **Godot leaks `uid://` references into scene files**, which is why
    `build/nuke_uids.py` exists — and it explicitly refuses to walk out through
    a junction, which is exactly the failure mode gotcha 10 sets up.
12. **Cold Godot imports exit non-zero**, so CI runs the import twice with
    `|| true` on the first pass.
13. **Pointers out of my subsystem** (one line each, not pursued):
    - `FmodStudio.RegisterBank("res://Downfall/audio/…bank")` +
      `RegisterGuidMappings("…/GUIDs.txt")` (`DownfallMainFile.cs:109-111`) is
      the audio packaging seam → **S19**.
    - The spine-godot runtime extension fetched at build time
      (`build/setup.ps1:21-43`) is an animation dependency → **S16**.
    - `GameVersion` feature detection and `ExtendedSaveTypes.RegisterListSaveType`
      (`DownfallMainFile.cs:41`) → **S12f**.
    - `ImageGen` atlas generation and its hash cache → **S17**.

---

## Transfer questions (against our own abstractions)

These are questions, not recommendations. Each names the file that would have
to change and what we would have to learn or decide first.

1. **Where should our English strings live?** Today they are split across three
   places: a C# dictionary merged into the `cards` table at boot
   (`klee-mod/KleeCode/KleeMod.cs:77` onward,
   `LocManager.Instance.GetTable("cards").MergeWith(...)`), a PowerShell
   here-string that writes `card_keywords.json` during the pack
   (`tools/build_pck.ps1:583-585`), and the three ruled selection prompts.
   Downfall keeps all of it as committed JSON under
   `res://<ModId>/localization/eng/`. **Question:** which of our three surfaces
   can even become a file, given that the code-side copy exists deliberately so
   a code-only playtest rebuild never renders raw keys (`KleeMod.cs` comment at
   the `card_keywords` merge)?
2. **Do we already agree on the path convention?** `tools/build_pck.ps1:579-583`
   documents `res://<modid>/localization/<lang>/<table>.json` and stages
   `klee/localization/eng/`. That is the same convention Downfall's patch
   rebuilds. **Question:** is anything about our layout incompatible with a
   later multi-language tree, or is it only that `eng` is the only folder?
3. **Do we want any language but English before a public build?** If yes, who
   owns the pipeline — and is running an account on a hosted translation
   platform something [USER] is willing to own at all? Downfall's answer costs
   nine platform projects, one API secret, a deploy key, and a bot that pushes
   to `main` nightly.
4. **What is the fallback when a key is missing in the player's language?**
   Downfall's whole model depends on it being per-key to English, but the rule
   lives in the base game's `LocManager`, not in Downfall. **This is a direct
   ask of S13.** And a second half we cannot answer either: do strings injected
   at runtime by `MergeWith` participate in that fallback the same way file
   strings do?
5. **Do we ever want a per-character build switch?** Downfall's `Submods`
   property compiles and packs a chosen subset. Ours is one package for the
   whole roster. **Question:** what would break if a build could omit a
   character — `tier0/roster.py` ship order, the generated-card manifests, save
   identity, co-op version matching?
6. **Do we want an "in the tree, not in the build" lane** for a character that
   is written but not released (Downfall's `Collector`/`Gremlins`)? Our codegen
   manifests are coverage ledgers (`STATE.md` → mod card coverage); would a
   deliberately unbuilt character read as a coverage hole or as a gate?
7. **Which version number does a public manifest carry?** Ours is MAJOR-AUTO —
   `0.2` by hand plus the repo commit count, chosen because two co-op players
   must be able to see *who is behind* (`klee-mod/build/version.ps1` header).
   Downfall's is semver `X.Y.Z` from a tag. **Question:** does a public release
   need a human-readable semver *as well as* the lockstep-comparable count, and
   which of the two goes in `manifest.json`?
8. **Do we want CI at all, and of which shape?** Downfall has three distinct
   distribution routes: a 14-day artifact on every push/PR, a GitHub release
   zip on a tag, and a Workshop push. We currently have one: a local
   `deploy.ps1 -Package` zip handed off privately, because the art is
   private-tier (`klee-mod/build/deploy.ps1` `-Package` comment). **Question:**
   is a public route wanted, and does any of it work without `gh` on this
   machine (memory: `gh-cli-not-installed`)?
9. **Is a Steam Workshop item something [USER] intends to own?** Downfall's CI
   holds a Steam username, password, and a TOTP shared secret, and updates a
   pre-created `publishedFileId` (`release.yml:132-149`). That is a credentials
   decision and a one-way door, not an engineering one.
10. **How do we declare and acquire BaseLib for a non-developer?** Our
    `klee-mod/local.props.example` points at a machine-specific Workshop path
    (`…/workshop/content/2868840/3737335127/BaseLib/BaseLib.dll`); our manifest
    floor is `3.3.6` while `STATE.md` pins the environment at `3.3.7.0` and
    Downfall now requires `3.4.5`. **Question:** what changed between those
    versions, what is our true floor, and what would a player be told to do?
11. **Do we want a compile-time missing-localization check?** Downfall gets one
    free from `Alchyr.Sts2.ModAnalyzers` (STS001), and *downgrades it from error
    to warning* in `.editorconfig`. We already have coverage ledgers in the
    generated manifests. **Question:** would an analyzer catch anything our
    manifests do not, and would it be a gate or a report (R204 makes that
    distinction load-bearing for axes; the same question applies here)?
12. **Is our PCK packing doing the same thing theirs is?** Downfall packs the
    imported `.ctex` from each `.import` remap and skips the raw image; ours
    drives the MegaDot editor (`tools/build_pck.ps1` header). Whether the two
    produce equivalent packs is an unanswered engineering question — and it
    overlaps Lane A / S17, so it is flagged, not pursued.

---

## NON-FINDINGS (explicit)

Each of these is a real answer: I looked and the evidence is not there.

- **N1 — the fallback-language rule is not established by this repo.** Downfall
  ships deliberately partial language files, so it must be relying on a
  per-key fallback, but no file in the pinned tree states the rule. The
  behaviour lives in the base game's `LocManager` /
  `ModManager.GetModdedLocTables`. **UNVERIFIED here; owed to S13.**
- **N2 — no localization completeness check runs in CI.** The only loc check is
  the compile-time analyzer, and `.editorconfig:6` lowers STS001 from its
  declared Error to Warning. No workflow validates that every `eng` key has a
  counterpart, or that no key is orphaned.
- **N3 — no manual-install instructions exist in the repo.** The release zip's
  shape (a top-level `Downfall` folder) and BaseLib's own README imply
  extraction into `Slay the Spire 2/mods`, but Downfall never says so. The
  release banner only says BaseLib is not included (`release.yml:121-126`).
  Treat "extract into mods/" as inference, not as a cited fact.
- **N4 — `mod_image.png` has no consumer in this tree.** Every submod ships one
  (`Champ/mod_image.png`, etc.), and a grep across every file type in the pinned
  tree returns no reference from any `.cs`, `.json`, `.godot`, `.ps1`, `.gd`, or
  `.yml`. Its reader is outside this repo — base game or BaseLib. **Do not read
  the filename as proof of a mod-browser thumbnail feature.**
- **N5 — no Workshop listing assets or listing localization in the repo.** No
  description text, no preview image, no tag/metadata file. The Workshop item is
  configured out-of-band; CI only pushes the folder to an existing
  `publishedFileId`.
- **N6 — no per-language font, CJK font packaging, or RTL handling anywhere.**
  Fonts come in as a junction to the base game's `fonts/` folder and are never
  touched by the mod's build.
- **N7 — no PCK signing, checksum, or integrity manifest.** Nothing verifies the
  shipped `.pck` against anything.
- **N8 — no changelog file.** Release notes are `gh release --generate-notes`
  plus the two-line authored banner.
- **N9 — no platform-specific packaging.** One folder ships for all platforms;
  the OS branches in `build/mod.build.props:79-106` only resolve *developer*
  paths (`ModsPath`, `Sts2DataDir`) for Windows / Linux / macOS.
- **N10 — no uninstall or removal procedure, and no save-migration step in the
  release workflow.** Absence is the finding; save/version compatibility is
  **S12f's** row, not mine.

---

## Search boundary

- **Date:** 2026-08-26. **Runner:** local Windows machine, read-only clone at
  `…\scratchpad\Downfall` (depth-1), verified `git rev-parse HEAD` =
  `32e61132052ae58e32cd33342d24136ffe18be12`.
- **I did not need to widen** (charter §7): Downfall implements my subsystem
  end to end, so the primary source answered the question. No second mod was
  searched for.
- **Three external primary sources were opened**, only to pin two dependency
  facts I could not settle from the tree. These are publisher-owned pages, not
  summaries, but they are **not commit-pinned** — retrieval date 2026-08-26:
  - `https://www.nuget.org/packages/Alchyr.Sts2.ModAnalyzers/0.1.9` — analyzer
    ids and their declared severities.
  - `https://www.nuget.org/packages/Alchyr.Sts2.BaseLib/3.4.5` — package
    description and publish date (2026-08-14).
  - `https://github.com/Alchyr/BaseLib-StS2` — BaseLib's own install
    instruction and MIT license.
  - One web search was run to locate the BaseLib repository
    (`Alchyr BaseLib Slay the Spire 2 github repository releases`, domains
    restricted to github.com and nuget.org). Its result text was used only to
    find the URL; every claim above comes from the fetched page.
- **Files read in full** in the pinned tree: `README.md`, `LICENSE`,
  `contribution-guidelines.md`, `Downfall.json`, `Downfall.csproj`,
  `sts2.csproj`, `local.props.example`, `.gitignore`, `.editorconfig`,
  `build/{setup.ps1,link-assets.ps1,mod.build.props,pack_mod.gd,nuke_uids.py}`,
  all six `.github/workflows/*.yml`, all three `.github/scripts/para_*.py`,
  `.github/configs/paratranz.json`, `DownfallCode/DownfallMainFile.cs`,
  `ChampCode/ChampMainFile.cs`,
  `DownfallCode/Localization/BundledSubmodLocRegistry.cs`,
  `DownfallCode/Patches/{GetModdedLocTablesPatch.cs,PluralRulesPatch.cs}`,
  `DownfallCode/Utils/PatchManager.cs`,
  `DownfallCode/Compatibility/GameVersion.cs`,
  `DownfallCode/Data/BuildSecrets.cs`, `ImageGen/{ImageGen.csproj,Program.cs}`,
  plus `project.godot` §`[application]`/`[autoload]`/`[editor_plugins]`.
  Census commands over `*/localization/**` counted files, table names, and
  language codes; sample loc files read: `Champ/localization/eng/cards.json`,
  `Champ/localization/deu/cards.json`,
  `Downfall/localization/eng/card_keywords.json`.
- **Our side, read-only:** `klee-mod/Klee/manifest.json`,
  `klee-mod/Directory.Build.props`, `klee-mod/local.props.example`,
  `klee-mod/build/{deploy.ps1,version.ps1}` (headers),
  `klee-mod/KleeCode/KleeMod.cs:60-140`, `tools/build_pck.ps1:1-60,570-600`,
  `docs/current/STATE.md`. **No file in the primary checkout was modified and no
  git command was run anywhere.** Nothing was built, deployed, or launched.

---

## What this does NOT establish

- **It does not establish that any of this is right for us.** Every pattern here
  is one author's solution to one mod's problem. Whether we localize at all,
  ship publicly, use CI, or own a Workshop item are [USER]'s calls, untouched.
- **It does not establish base-game behaviour.** The fallback-language rule
  (N1), whether `mod_image.png` has a consumer (N4), and whether
  `GetModdedLocTables` is the *only* discovery path are engine facts. S13 owns
  them; nothing here should be read as evidence about the engine.
- **It is n = 1.** One mod, by one author who also publishes the surrounding
  tooling (`lamali.StS2.RefLib`) and works alongside BaseLib's author. Its
  conventions may be house style rather than platform norms.
- **It establishes no rights.** Downfall's MIT license covers Downfall's own
  code. It does not cover the base-game assets the build junctions in, its art,
  its audio banks, or its translations. Nothing here says what we may
  distribute; our own art rights tier is untouched and remains [USER]'s.
- **It does not establish that the Workshop route is open to us** — that needs
  an account, upload rights against appId `2868840`, and credentials in CI.
- **It proposes no code, no schema, no id, and no design.** No BACKLOG or QUEUE
  row is minted here; the twelve transfer questions are questions.
