# Downfall animation-pipeline investigation — Track M

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

**Date:** 2026-08-05 · **Findings only.** This memo informs the animation path
choice. It decides nothing, licenses nothing, authors no rig, and changes no
pipeline. It is a **supplement** to `docs/animation-capability-memo.md`
(Track F1) — that memo is not edited, and every number in it still says what it
said.

Ground truth order, as briefed: **installed pack first, repository second.** The
`.pck` is what actually ships; the repository explains how it got that way, and
where the two disagree the disagreement is itself a finding (§2).

Sources used, all read-only:

- `…\steamapps\workshop\content\2868840\3747508091\Downfall.pck` (Downfall
  0.1.7, `Downfall.json`), 4,313 entries, parsed with the S5 reader
  (`tools/probe_spine_pck/pck_read.py`).
- `…\common\Slay the Spire 2\SlayTheSpire2.pck` (15,658 entries) and
  `libspine_godot.windows.template_release.x86_64.dll`.
- `github.com/lamali292/Downfall` at HEAD, cloned to a scratch directory. No
  Downfall code and no base-game asset is copied into this repository.

---

## Answers first

| | Question | Answer |
|---|---|---|
| **M-Q1** | Does the installed Downfall pck contain `.skel`/`.atlas` as raw packed files? | **NO — and the distinction turns out not to matter.** It ships `.spskel`/`.spatlas`, but those are the *near-identity* output of the importer: the `.spskel` is the raw Spine binary byte-for-byte, and the `.spatlas` is a four-key JSON envelope around the verbatim `.atlas` text. Neither carries a `.import` descriptor, and neither lives in `.godot/imported/`. §1 |
| **M-Q2** | Does Downfall's build treat Spine files specially? | **NO.** They do not use `--export-pack` at all. `build/pack_mod.gd` walks the project with `PCKPacker` and `add_file`s everything that is not a raw image or audio file — Spine data is opaque bytes to their packer. **That is the one thing our build does differently**, and it is measurable (§3). |
| **M-Q3** | Does a probe `.tscn` survive OUR `build_pck` and load in-game? | **YES for `.spskel`/`.spatlas` — measured in-game: `ROOT=SpineSprite`, `data_loaded=true`, and it visibly draws. NO for raw `.skel`/`.atlas`: `No loader found`. The MegaDot editor never knew any of the types.** §3 |
| **M-Q4** | Which Downfall characters use Spine vs other? | **10 of 11 use Spine; Hexaghost alone does not.** Full per-scene node census in §4. |
| **M-Q5** | How does Downfall drive animations from C#? | A Harmony **postfix on `NCreature.SetAnimationTrigger`** dispatching to an `IAnimatedVisuals` interface on the scene script, which calls `SpineBody.GetAnimationState()` and sets named clips with explicit per-trigger mix times. **Our router is already the same patch shape**; the delta is the target, not the plumbing. §5 |
| **M-Q6** | Licence facts | Editor licence is per named person, **$69 Essential / $379 Professional** (measured today), one-time, under a $500k revenue ceiling. **Neither agreement contains any clause about generating skeleton data without the Editor** — and the shipped runtime loads `.spjson` / `.spine-json`. Flagged, not concluded. §6 |
| **M-Q7** | What changes in F1's cost table? | F1's Path A blocker moves from *"the pack build fails"* to *"one `include_filter` line"*, with in-game load still open. PROPOSED revised table in §7. |

---

## 1. M-Q1 — what the installed Downfall pack actually contains

**Answer: NO, not raw. It ships converted resources — but the conversion is
almost nothing, and the shipped form needs no importer.**

Extension census of `Downfall.pck` (4,313 entries): 1,702 `.tres`, 858 `.json`,
722 `.import`, 694 `.ctex`, 167 `.tscn`, 69 `.uid`, **38 `.spatlas`**, 28
`.oggvorbisstr`, **26 `.spskel`**, 3 `.gdshader`, 2 `.gd`. Searching the whole
pack for `.skel` or `.atlas` returns **zero hits**.

The spine files sit at ordinary `res://` paths beside their scenes —
`Champ/scenes/character/champ.spskel`, `champ.spatlas`, each with a 20-byte
`.uid` sidecar — and, decisively, **not** under `.godot/imported/`. The pack's
722 `.godot/imported/` entries are all `.ctex` and `.oggvorbisstr`: **every PNG
is imported, no Spine file is.**

Compare the base game, which *is* the editor-import path:

```
.godot/imported/punch_construct.skel-2e25427da2bfb94405919d1cac6eef21.spskel
animations/monsters/punch_construct/punch_construct.skel.import
    [remap]
    importer="spine.skel"
    type="SpineSkeletonFileResource"
    path="res://.godot/imported/punch_construct.skel-2e254….spskel"
```

Now the content of those imported files, read out of both packs:

| | first bytes |
|---|---|
| base game `punch_construct…spskel` | `09 bc 10 a1 c5 45 1e 99` `07` `4.2.43` `…` |
| Downfall `champ.spskel` | `00 00 00 00 00 00 00 00` `07` `4.2.11` `…` |

That is the **Spine 4.2 binary skeleton format itself** — 8-byte hash, then the
length-prefixed version string. The `spine.skel` importer copies the bytes and
changes the extension. Nothing else.

`.spatlas` is barely more: a JSON object with exactly four keys.

```json
{"atlas_data": "<the .atlas text, verbatim>",
 "normal_texture_prefix": "n",
 "source_path": "res://Champ/scenes/character/champ.atlas",
 "specular_texture_prefix": "s"}
```

Note that `source_path` names a file **that is not in the pack**. The importer
ran on their machine; only its output shipped.

Two further facts, both load-bearing:

1. **The scene references the shipped form directly.**
   `Champ/scenes/character/champ.tscn` in the installed pack (620 bytes, plain
   text) declares
   `[ext_resource type="SpineAtlasResource" path="res://Champ/scenes/character/champ.spatlas"]`
   and the matching `SpineSkeletonFileResource` → `champ.spskel`, with a
   `SpineSkeletonDataResource` **inlined as a `sub_resource`** rather than kept
   in a separate `_skel_data.tres` the way the base game does it.
2. **The shipped runtime carries its own loaders.** Strings in
   `libspine_godot.windows.template_release.x86_64.dll` — the template_release
   build, the only one the game ships — include
   `SpineSkeletonFileResourceFormatLoader`, `SpineAtlasResourceFormatLoader`,
   and next to `SpineSkeletonFileResource.cpp`'s `load_from_file`, the
   extension list **`.spjson` `.spine-json` `spjson` `spskel` `.spskel`
   `.skel`**; next to `SpineAtlasResource.cpp`'s `load_from_atlas_file`,
   **`spatlas` `.atlas`**.

   **Do not read that string list as the set of extensions the loader claims.**
   The in-game probe (§3b) settles it: `.spskel`/`.spatlas` load, and raw
   `.skel`/`.atlas` produce `No loader found for resource` at the same boot,
   from the same pack. `load_from_file` accepting a `.skel` *path* and the
   `ResourceFormatLoader` *recognising* the `.skel` extension are two different
   things, and only the second one is what a `.tscn` `ext_resource` needs.

**So the hypothesis under test is confirmed, with the spelling pinned down.**
Mods do not need editor import artefacts — the runtime resolves these types
itself — but the resolvable spelling is **`.spskel`/`.spatlas`, not raw**. That
is exactly what Downfall 0.1.7 ships. Their *repository* has since migrated to
raw `.skel` (§2); that form is not evidenced as working by anything here, and
our probe says it does not load unaided, so the most likely explanation is that
their stock-Godot editor imports it and their packer follows the `.import`
remap. **The conversion we would need is not an importer — it is a file rename
plus a four-key JSON wrapper.**

**F1 §1d stands exactly as written** — MegaDot has no spine importer, and
`importer="spine.skel"` cannot run. What this section removes is the *inference*
that followed: the pack build does not need that importer, because nothing in
the shipped chain is an imported resource.

---

## 2. M-Q2 — Downfall's build pipeline, and where ours differs

**Answer: no special treatment. Spine files are opaque bytes to their packer.**

`build/pack_mod.gd` (their entire packing step, run as
`godot -s pack_mod.gd -- <out> <folders…>`):

```gdscript
const SKIP_EXTENSIONS: Array[String] = [
    ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".svg", ".tga",
    ".ogg", ".mp3", ".wav",
]
…
    var is_raw_image: bool = SKIP_EXTENSIONS.any(…)
    if not is_raw_image:
        var err: int = packer.add_file(full_path, full_path)
    if file_name.ends_with(".import"):
        _pack_imported_dependency(packer, full_path)
```

`PCKPacker.add_file`, file by file. The only classification in the whole script
is *"is this a raw image or a sound"* — those are skipped, because their
imported `.ctex`/`.oggvorbisstr` is added instead by following the `.import`
remap. **A `.skel` is not an image, so it is added. There is no importer in the
loop and no resource type is ever resolved.**

**This is the difference from ours.** `tools/build_pck.ps1` runs
`MegaDot --headless --import` then `--export-pack 'pck'`, against a preset with

```
export_filter="all_resources"
include_filter=""
```

Godot's `all_resources` means *resources* — files the editor can classify.
Without the spine extension, MegaDot classifies none of the four spine
extensions, so they fall outside the filter. §3 measures exactly that.

Three smaller pipeline facts worth carrying:

- **They build against the game's own assets by junction.**
  `build/link-assets.ps1` and `mod.build.props` link `src, images, fonts,
  localization, materials, models, scenes, animations, banks, debug_audio,
  shaders, themes, addons` from an `AssetSourcePath` into the project root — all
  of them `.gitignore`d. `addons` is in that list, which is how their editor
  gets `addons/spine/spine_godot_extension.gdextension` **from the game
  directory**. They did not obtain a spine editor build; they borrowed the
  game's own, and it works for them because they drive stock Godot, not
  MegaDot. Whether the same junction would give MegaDot 4.5.1 a working editor
  extension is untested by anyone here — the `.gdextension` names a
  `windows.editor.x86_64` binary that F1 established does not ship.
- **Their repo is mid-migration between the two spelling conventions.** Tracked
  today: 5 `.spine` **Spine Editor project files** (Automaton, Awakened, Champ,
  SlimeBoss, Snecko — 39–46 KB binaries), 5 raw `.skel` + 5 `.atlas` under
  `<Char>/scenes/character/spine/`, and 17 `.spskel` + 30 `.spatlas` committed
  directly (Collector, Gremlins, Guardian, Hermit, the slimes). Repo HEAD's
  `champ.tscn` points at `res://Champ/scenes/character/spine/champ.skel`;
  installed 0.1.7's points at `res://Champ/scenes/character/champ.spskel`. Same
  version string in both `Downfall.json` files, so the raw form is newer than
  the shipped pack and **is not evidenced as shipped-and-working by anything
  measured here.** The runtime string table (§1) is the only support for it.
- **`*.import` is `.gitignore`d** except for three PNG globs, so their raw
  `.skel`/`.atlas` carry no import descriptor even in the repository.

---

## 3. M-Q3 — the probe

### 3a. Packing half — **MEASURED, offline, today**

Apparatus: `tools/probe_spine_pck/` (README there; nothing wired into the
pipeline). One base-game rig — `punch_construct`, 54 bones / 44 regions, the
worked example from F1 §1b — copied read-only out of `SlayTheSpire2.pck` into a
scratch directory outside the repo. The generator **refuses** an `--out` inside
the repo. Three scenes, one scratch project, two export presets: `strict` is the
preset `build_pck.ps1` writes verbatim, `wide` differs by one line —
`include_filter="*.skel,*.atlas,*.spskel,*.spatlas"`.

**Import step:** `MegaDot --headless --path … --import` → **exit 0, zero ERROR
lines**, one file imported (`rig.png`). The spine files were silently ignored.
This matters because `build_pck.ps1` throws on any `ERROR` in the import log:
**the import gate does not fire.**

**Export step:** both presets exit 0. Both print errors that nobody checks:

```
ERROR: No loader found for resource: res://spineprobe/rig.skel
       (expected type: SpineSkeletonFileResource)
ERROR: Cannot get class 'SpineSkeletonDataResource'.
ERROR: res://spineprobe/probe_raw.tscn:7 - Parse Error: .
ERROR: Failed loading resource: res://spineprobe/probe_raw.tscn.
```

**`build_pck.ps1` checks the import log for `ERROR` and does not check the
export log.** A spine pack would build "successfully" with those four lines in
the console. Recorded as an observation about our script, not a request to
change it.

Contents of the two packs, read back with the S5 parser:

| entry | strict | wide |
|---|:--:|:--:|
| `spineprobe/probe_control.tscn.remap` + exported `.scn` | ✔ | ✔ |
| `spineprobe/probe_raw.tscn` (text, unconverted) | ✔ | ✔ |
| `spineprobe/probe_imported.tscn` (text, unconverted) | ✔ | ✔ |
| `.godot/imported/rig.png-….ctex` | ✔ | ✔ |
| `spineprobe/rig.skel` | ✘ | ✔ |
| `spineprobe/rig.atlas` | ✘ | ✔ |
| `spineprobe/rig.spskel` | ✘ | ✔ |
| `spineprobe/rig.spatlas` | ✘ | ✔ |
| total entries | 9 | 13 |

Three findings from that table:

1. **The rig data is dropped by our current preset and kept by one extra
   `include_filter` line.** Both spellings behave identically; there is nothing
   to choose between `.skel` and `.spskel` at the packing layer.
2. **The spine scenes survive in both packs — as source text.** MegaDot could
   not parse them, so it stored the `.tscn` verbatim instead of converting it to
   a binary `.scn` with a `.remap` (which is what it did to the control scene).
   That is the behaviour a mod wants: an engine that *can* parse it gets the
   original text.
3. **The control arm passes in both**, so nothing above is an artefact of a
   broken export.

**The failure F1 predicted — "our pipeline cannot import a Spine rig, the pack
build fails before any question of how the rig looks" — did not occur.** The
build does not fail. It silently omits four files, and one preset line stops it.

### 3b. Loading half — **MEASURED in-game, 2026-08-05**

Deployed as prepared: one new folder `mods\spineprobe` (manifest + 8 KB dll +
the 527 KB `wide` pack), launched **through Steam** (`steam://rungameid/2868840`
— never the exe directly, see §3c), main menu reached, quit, removed.

Verbatim from `%APPDATA%\SlayTheSpire2\logs\godot.log`:

```
[INFO] Loading Godot PCK …\mods\spineprobe\spineprobe.pck
[INFO] [spineprobe] M-Q3 probe starting.
[INFO] [spineprobe] res://spineprobe/probe_control.tscn EXISTS=True
[INFO] [spineprobe] res://spineprobe/probe_control.tscn LOADED=True
[INFO] [spineprobe] res://spineprobe/probe_control.tscn ROOT=Sprite2D name=Visuals
[INFO] [spineprobe] res://spineprobe/probe_raw.tscn EXISTS=True
ERROR: No loader found for resource: res://spineprobe/rig.atlas (expected type: SpineAtlasResource)
ERROR: No loader found for resource: res://spineprobe/rig.skel (expected type: SpineSkeletonFileResource)
ERROR: res://spineprobe/probe_raw.tscn:7 - Parse Error: [ext_resource] referenced non-existent resource at: res://spineprobe/rig.atlas.
ERROR: Failed loading resource: res://spineprobe/probe_raw.tscn.
[INFO] [spineprobe] res://spineprobe/probe_raw.tscn LOADED=False
[INFO] [spineprobe] res://spineprobe/probe_imported.tscn EXISTS=True
[INFO] [spineprobe] res://spineprobe/probe_imported.tscn LOADED=True
[INFO] [spineprobe] res://spineprobe/probe_imported.tscn ROOT=SpineSprite name=Visuals
[INFO] [spineprobe] res://spineprobe/probe_imported.tscn SKELETON data_loaded=true
[INFO] [spineprobe] M-Q3 probe done.
…
[INFO] [spineprobe] res://spineprobe/probe_imported.tscn ATTACHED to root at (640,540)
```

Per arm:

| Arm | EXISTS | LOADED | ROOT | SKELETON | Answer |
|---|:--:|:--:|---|---|---|
| `probe_control.tscn` (`Sprite2D`) | ✔ | ✔ | `Sprite2D` | n/a | **YES** — pack and mount are sound, so nothing below is an artefact |
| `probe_raw.tscn` (`.skel`+`.atlas`) | ✔ | **✘** | — | — | **NO** — packed fine, **type resolution failed**: `No loader found`, for the atlas *and* the skeleton |
| `probe_imported.tscn` (`.spskel`+`.spatlas`) | ✔ | ✔ | **`SpineSprite`** | **`data_loaded=true`** | **YES** |

**And it draws.** A screen capture at the profile screen shows the
`punch_construct` rig rendered over the menu at its authoring scale — pale
segmented limbs and a fist filling the right third of a 1280×720 window. Setup
pose, since the probe sets no animation. The fifth observable — *everything
resolves and still nothing draws* — did not occur.

**M-Q3, answered.** A `.tscn` naming `SpineSprite`, `SpineAtlasResource`,
`SpineSkeletonFileResource` and `SpineSkeletonDataResource`, packed by an editor
that can parse none of those types and emitted four `ERROR` lines while packing
it, **loads, resolves, instantiates and renders in the shipped game.** The
editor importer is not on the path. The one thing that is on the path is the
file spelling: `.spskel`/`.spatlas`, which is a rename and a JSON wrapper away
from a Spine export.

Two lines the probe did *not* need but which sharpen the failure taxonomy:
`probe_raw.tscn` failed at **`LOADED`**, not at `EXISTS` — precisely the
distinction the arms were designed to separate, and it worked. Had we only
tested the raw spelling we would have concluded Path A′ was dead.

### 3c. Restoration

Checked against the baseline captured before deployment:

- **mods list unchanged** — `klee, quick_fingers, STS2AutoSlayMod`;
  `mods\spineprobe` removed.
- **install root: all 13 files hash to baseline.** Nothing in the install
  modified.
- **`steam_appid.txt` ABSENT.** It does **not** ship with the game — it appears
  only when the exe is run outside Steam. This session never created one
  (launched via `steam://rungameid/2868840`), and none is present now. *An
  earlier draft of this memo recorded it as "ships with the game, so the rule is
  no NEW one" — that was wrong, and it was wrong because the baseline observed a
  leaked copy from another session. The correct end state is absent.* Both
  scripts now enforce that.
- **`default\1\settings.save` mtime unchanged.**
- **No run left behind.** Checked across every profile including
  `steam\<id>\profileN\saves`, where runs actually park — not `default\1`. No
  run file exists in any of them; `progress.save` is byte-identical in both the
  vanilla and modded profile trees. The one file that did move was
  `steam\<id>\settings.save` (2949 → 3062 bytes), which the game rewrites on
  quit. The first cleanup run reported that as a failure; the classifier was too
  coarse and now separates run files from user state, so a clean session stops
  crying wolf.
- Scratch project deleted, **rig copy included**; probe build output deleted.
  No base-game asset was ever written inside the repo — the generator refuses an
  `--out` under it.

### 3d. Prepared apparatus (retained)

Everything below stays in the tree so the result is reproducible without
re-deriving it. It is wired into nothing.

- `tools/probe_spine_pck/SpineProbe/` — a throwaway mod (`spineprobe`,
  `affects_gameplay: false`, no dependencies, no patches, no registrations).
  **Compiles clean** against `sts2.dll` + `GodotSharp.dll`
  (`dotnet build -c Release` → `spineprobe.dll`).
- `deploy_probe.ps1` — captures a reversibility baseline *first* (mods listing,
  `settings.save` mtime, `steam_appid.txt` presence + mtime — it ships with the
  game, so the rule is "no **new** one", sha256 of every file in the install
  root), then creates exactly one new folder, `<GameDir>\mods\spineprobe`,
  containing `manifest.json` + `spineprobe.dll` + `spineprobe.pck` (the `wide`
  pack). Nothing existing is edited or overwritten. Refuses to run while the
  game process is alive.
- `cleanup_probe.ps1` — deletes that folder, deletes the scratch project (rig
  copy included) and the probe's build output, then re-checks each baseline item
  and prints OK/NOTE/FAIL per item. A moved `settings.save` mtime is a NOTE, not
  a FAIL: launching the game is what the probe asked for.

**Failure modes, distinguished in advance** — three arms × five observables, all
printed to `godot.log` as `[spineprobe]` lines:

| Arm | What it isolates |
|---|---|
| `probe_control.tscn` — plain `Sprite2D` | if this fails, the pack or the mod mount is broken and spine was never the subject |
| `probe_raw.tscn` — `SpineSprite` → `.skel` + `.atlas` | Downfall repo-HEAD spelling |
| `probe_imported.tscn` — `SpineSprite` → `.spskel` + `.spatlas` | Downfall installed-0.1.7 spelling |

| Observable | False means |
|---|---|
| `EXISTS=` (`ResourceLoader.Exists`) | packing failure — the file is not in the mounted pack |
| `LOADED=` (`Load<PackedScene>`) | **type-resolution failure** — the engine could not find `SpineSkeletonFileResource` / `SpineSkeletonDataResource` |
| `ROOT=SpineSprite` | the type resolved but the node is not what the scene declared |
| `SKELETON data_loaded=` (`is_skeleton_data_loaded`, called by class-name binding, exactly as the game does it per S5) | types resolved, data did not — the **silent no-render** mode |
| `ATTACHED` + eyes on the menu | everything resolved and still nothing draws |

Run order, as executed: `dotnet build` → `deploy_probe.ps1` → **launch through
Steam** → main menu → quit → read `godot.log` → `cleanup_probe.ps1`.

**Launch through Steam, never the exe.** Running `SlayTheSpire2.exe` directly
makes it write `steam_appid.txt` into the install root — a footprint the Steam
launch does not leave, and one that outlives a killed session. With Steam
already running, `start steam://rungameid/2868840` costs nothing and leaves
nothing.

---

## 4. M-Q4 — the census

**10 of 11 character folders use Spine. Hexaghost is the sole exception.**
Per-scene node types, read out of the installed pack (`SpineSprite` counted from
`[node … type=]` declarations):

| Folder | `SpineSprite` | `AnimationPlayer` / `AnimationTree` | `.spskel` in pack | Visual shape |
|---|---:|---:|---:|---|
| Automaton | 1 | 0 | 1 | Spine, `Visuals` = instanced `automaton.tscn` |
| Awakened | 1 | 0 | 1 | Spine |
| Champ | 1 | 0 | 1 | Spine |
| Collector | 2 | 0 | 2 | Spine ×2 (`collector`, `torchhead`) |
| Gremlins | 6 | 0 | 6 | Spine ×6; `combat.tscn`'s `Visuals` is a **plain `Node2D`** — the six gremlin rigs are attached at runtime |
| Guardian | 1 | 1 | 3 | Spine; the lone `AnimationPlayer` is `stasis_slot.tscn`, a UI element |
| Hermit | 1 | 0 | 1 | Spine |
| **Hexaghost** | **0** | **1 + 1** | **0** | **No Spine.** `hexaghost2.tscn` is 19 KB of `GPUParticles2D` + `Curve`/`CurveTexture` + `ParticleProcessMaterial` + `ShaderMaterial` over one `hexaghost_core.png`, driven by an `AnimationPlayer`/`AnimationTree` pair |
| SlimeBoss | 16 | 15 + 15 | 6 | **Hybrid**: 16 Spine visuals *and* 15 `combat/*_slime.tscn` each carrying an `AnimationPlayer` + `AnimationTree` |
| Snecko | 1 | 0 | 3 | Spine |
| Downfall (shared) | 0 | 0 (+1 `AnimatedSprite2D` on `card.tscn`) | 0 | UI only |

Repo cross-check agrees and adds provenance: the five folders holding a `.spine`
**Spine Editor project** are Automaton, Awakened, Champ, SlimeBoss, Snecko —
each with a raw `.skel`/`.atlas` pair under `scenes/character/spine/`. The other
Spine users (Collector, Gremlins, Guardian, Hermit, the slime visuals) carry
committed `.spskel`/`.spatlas` and **no editor project**.

**Observation, not recommendation.** The split does not run along "how important
is this character". It runs along **whether a jointed body exists to rig**. Ten
of eleven are humanoid or creature bodies with limbs; the one that is not — a
ring of six flames around a core, with nothing that bends — is the one built
from particles and shaders instead, and it is not visibly the poorer for it. The
second-order split, editor project vs. committed `.spskel` only, marks where
somebody sat down in the Editor versus where a rig arrived already made.

Also observable: **`.spskel` version strings vary** (`champ.spskel` self-reports
`4.2.11`; the base game's rigs report `4.2.43`), and 0.1.7 is a shipped,
playable mod. The runtime tolerates a rig older than the one the game was built
against, at least across 4.2 point releases.

---

## 5. M-Q5 — how Downfall drives animation, and what it means for our router

Three layers.

**1. The dispatch is a Harmony postfix — the same patch we already run.**

```csharp
[HarmonyPatch(typeof(NCreature), nameof(NCreature.SetAnimationTrigger))]
public static class NCreatureAnimationPatch {
    private static void Postfix(NCreature __instance, string trigger) {
        if (__instance.Visuals is IAnimatedVisuals downfallAnimation)
            downfallAnimation.OnAnimationTrigger(trigger);
    }
}
```

`DownfallCode/Patches/NCreatureAnimationPatch.cs`. There is a second one for
death (`NCreatureDeathAnimationPatch`, hard-coding `"Dead"`) and a third for the
merchant idle. **`klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs` is this
patch pair already** — same target method, same postfix shape, plus our
`StartDeathAnim` postfix for the same reason theirs exists. The one structural
difference: they find the target through an **interface on a scene script**
(`IAnimatedVisuals`), we find it by **node lookup** (`%AnimationTree`), because
our pipeline forbids scripts in scenes (`klee-mod/pck-src/README.md`). Our own
comment already credits their patch shape as the precedent.

**2. The per-character handler names clips and mix times explicitly.**
`ChampCode/Vfx/NChampCreatureVisuals.cs`, in full shape:

```csharp
private const float DefaultMix = 0.2f;  ToIdleMix = 0.35f;
                    AttackMix  = 0.1f;  DeathMix  = 0.4f;  HitMix = 0.05f;

case "Attack":
    _animState?.SetAnimationWithMix(AttackAnim, AttackMix, false);
    _animState?.QueueAnimation(IdleAnim, ToIdleMix);
```

`_animState` comes from `_sprite = SpineBody; _animState = _sprite?.GetAnimationState();`
in `_Ready`. Clip names are chosen by a C# state property — Champ's `IdleAnim`
switches over a `Stance` enum into `"Idle"` / `"IdleBerserker"` /
`"IdleDefensive"` / `"IdleUltimate"`, and `HitAnim` likewise. **Triggers handled
across the roster: `Idle`, `Attack`, `Hit`, `Cast`, `Dead`** — the same set our
`TriggerToState` maps, minus `Revive` and `PowerUp`.

Two notes on the types: `MegaSprite` / `MegaAnimationState` / `MegaSkeleton` /
`MegaBone` are the **base game's own** `Core.Bindings.MegaSpine` wrappers, and
`SpineBody` is a property on the base `NCreatureVisuals`. Downfall never names a
spine GDExtension type in C# — matching S5 §5, which found the game talks to
Spine by class-name binding. And they wrap every call in
`DownfallCode/Compatibility/CompatibilityAnimation.cs`, a reflection layer whose
comment is worth carrying verbatim: *"a direct call bakes one version's
signature into IL and JIT-crashes the entire containing method on the other
version. Known drift: 107 `SetAnimation`/`AddAnimation`/`AddEmptyAnimation`
return `MegaTrackEntry`; 108 returns void."*

**3. Spine and `AnimationTree` are not exclusive.** `NSlimeCreatureVisuals`
holds an `AnimationNodeStateMachinePlayback` from `%AnimationTree` **and** a
Spine body, translating triggers to `_playback.Travel("idle"/"attack")` while
separately attaching Godot `Node2D` children to named Spine bones:

```csharp
var skeleton = SpineBody?.GetSkeleton();
TryAttach(skeleton, "bone8",  "%Crown");
TryAttach(skeleton, "eye",    "%Eye");
SpineBody?.ConnectWorldTransformsChanged(Callable.From<Variant>(OnWorldTransformsChanged));
```

**What this maps to on our side.** Our router's target is `%AnimationTree`; for a
Spine visual the target would instead be `SpineBody.GetAnimationState()`, which
is reachable from `NCreature.Visuals` **without any script in the scene** —
`SpineBody` is a base-class property, not something the scene must declare. The
router's existing shape (per-trigger lookup, inert when the node is absent)
survives; what it needs is a second branch, not a rewrite. And per §5's slime
evidence the two branches can coexist on one creature. *This is a mapping, not a
plan; nothing here is proposed for implementation.*

One further consequence worth stating plainly: if `Visuals` **is** a
`SpineSprite`, `NCreature` builds its own `_spineAnimator` (F1 §2a: it does so
exactly when `Visuals.HasSpineAnimation`), so the game's native animation
channel comes back to life and the router stops being load-bearing at all.
Downfall's `Champ.cs` still carries a full `GenerateAnimator` /
`CreatureAnimator` state graph in the base-game idiom — **commented out**, in
favour of the Harmony patch. Recorded as observed; why they switched is not
evidenced.

---

## 6. M-Q6 — licence facts, with sources

Facts only. **The licence call is [USER]'s** and nothing below is a conclusion
about what we may do.

**(a) Shipping `.skel` data.** The
[Spine Runtimes License](https://en.esotericsoftware.com/spine-runtimes-license)
governs the *Runtimes*, and defers: *"Integration of the Spine Runtimes into
software or otherwise creating derivative works of the Spine Runtimes is
permitted under the terms and conditions of Section 2 of the Spine Editor
License Agreement."* It adds that *"redistribution of the Products in any form
must include this license and copyright notice"* and that *"each user of the
Products must obtain their own Spine Editor license."* Per S5, the game already
ships `libspine_godot…dll`; a mod adds no runtime binary. The agreement text
found is about the Runtimes and about Editor licensing — **it contains no clause
that separately governs distributing exported skeleton data.**

**(b) Authoring new rigs.** [Spine Editor
License](https://en.esotericsoftware.com/spine-editor-license) §2.1: *"You may
integrate the Spine Runtimes into software … provided that (a) each Product adds
significant and primary functionality to the Spine Runtimes; and (b) **You have
a valid Spine Editor license at the time the Spine Runtimes are integrated into
each Product**."* §2.4: *"A valid Spine Editor license is required to (a)
integrate the Spine Runtimes into software … or (b) modify, adapt, develop, or
otherwise create derivative works that contain the Spine Runtimes,"* with the
illustrative example *"Each user of such an SDK, game toolkit, or software
library must obtain a Spine Editor license because the applications they are
creating contain the Spine Runtimes."* §1.4.1: *"The Spine Trial license does
not grant rights to integrate, distribute, or otherwise make use of the Spine
Runtimes. Section 2 does not apply to the Spine Trial license."*

Prices, re-verified today at
[spine-purchase](https://en.esotericsoftware.com/spine-purchase) — F1 §1c
deliberately did not quote the Professional figure, so this closes that gap:

| Tier | Price | Terms |
|---|---|---|
| Essential | **$99 → $69** (discounted rate shown) | one-time; *"Each named person using Spine Essential requires their own license"* |
| Professional | **$449 → $379** (discounted rate shown) | one-time; same per-named-person wording; upgrade from Essential *"at any time for the difference in price"* |
| Enterprise | **$2499 base + $379 per user** | annual; required at *"$500,000 USD or more annual revenue"* |

Meshes are a Professional feature (S5), and every shipped base-game rig uses
them (F1 §1b).

**(c) Generating skeleton data programmatically, without the Editor —
FLAGGED, because it is load-bearing for cost-per-entity.**

**Neither agreement contains any clause about it.** The Runtimes agreement does
not address whether skeleton data may be created outside the Editor and does not
restrict third-party tools that produce Spine data; the Editor agreement
contains no clause permitting *or* prohibiting programmatic JSON/binary
generation. The obligations that do exist are attached to **integrating the
Runtimes**, not to authoring data.

Three adjacent facts that make the question live rather than academic:

1. **The format is publicly documented** by Esoteric —
   [spine-json-format](https://en.esotericsoftware.com/spine-json-format), with
   a linked `/spine-binary-format` — and the page says *"Spine can import data
   in this format, allowing interoperability with other tools"* and *"You do not
   need to write your own loading code unless you are writing your own runtime
   from scratch."*
2. **The shipped runtime loads JSON.** The extension list in
   `libspine_godot…template_release…dll` includes **`.spjson` and
   `.spine-json`**, not only the binary spellings (§1). A generated JSON
   skeleton would be loadable by the very binary already in the game folder,
   with no editor and no binary writer anywhere in the chain.
3. The skeleton's `"spine"` version attribute exists so *"tools can enforce a
   particular Spine version"* — i.e. the format anticipates non-Editor
   producers.

**What this does not say:** that the licence permits it, that a generated rig
would look like a hand-made one, or that we have any such generator. Flagged for
[USER] as the single highest-leverage open question on Path A, because the whole
per-seat licence line in F1's cost table hangs on the premise that authoring
requires the Editor.

**(d) Downfall's own terms.** `LICENSE` is **MIT**, *"Copyright (c) 2026
lamali"* — covering their repository. Their *assets* are a different matter and
the MIT text makes no asset carve-out: the characters are Slay the Spire 1
figures (Champ, Automaton, Awakened, Collector, Gremlins, Guardian, Hermit,
Hexaghost, Slime Boss, Snecko) and the pack's spine rigs are of those figures.
The five committed `.spine` Editor project files are evidence that rigs are
authored in the licensed Editor. **Nothing of theirs — code, asset, or `.spine`
project — is copied into this repository; §5's mapping is behavioural
description.**

---

## 7. M-Q7 — revised cost table (**PROPOSED** — final for this pass; §3b is in)

Supplement to F1 §4, which is unchanged and remains the reference. New column
**A′** is the same technology reached without the editor importer.

| | **A — Spine (F1, via editor import)** | **A′ — Spine runtime path *(new, PROPOSED)*** | **B — Skeleton2D** | **C — layered Sprite2D** |
|---|---|---|---|---|
| Licence $ (per person, one-off) | ~$69 → Professional tier (F1 §1c) | **$69 Essential / $379 Professional, measured §6** — *unless* §6(c) resolves in favour of non-Editor generation, in which case unknown and possibly $0 | $0 | $0 |
| Tooling gap (one-off) | **BLOCKER: no spine editor extension for MegaDot 4.5.1** (F1 §1d) | **CLOSED, measured end-to-end: one `include_filter` line in the export preset (§3a) + ship the `.spskel`/`.spatlas` spelling (§3b). No editor extension, no importer, no MegaDot change.** | none known, unproven | none — shipped |
| Format conversion, one-off | n/a — the importer does it | **~10 lines**: `.skel` → `.spskel` is a rename (bytes identical, §1); `.atlas` → `.spatlas` is a four-key JSON wrapper. Raw spellings **do not load** (§3b), so this step is mandatory and is the whole of it | n/a | n/a |
| Rig acquisition, per entity | Editor authoring | **Editor authoring, OR generation into `.spjson` — §6(c) unresolved** | — | — |
| Authoring hours class | 1 day → 5–10 days (F1 §1e) | **unchanged where the Editor is used**; the generated branch is unquantified and no generator exists in this repo | 1 day → 3+ days | 0.5 → 1.5 days |
| Review rounds | 2–4 | 2–4 | 2–4 | 2–4, measured |
| Runtime risk | low once loading works | **low, measured**: loads, resolves `SpineSprite`, reports `data_loaded=true`, and renders, in our own pack (§3b). Residual risk is combat integration and damage-frame timing, not loading | low–medium | lowest |
| Visual ceiling | base-game parity | base-game parity — same runtime, same data | true deformation, unproven | rigid layers only |
| Working example in reach | 101 (base game) | **101 base-game + 10 of 11 Downfall characters (one shipping a `4.2.11` rig against a `4.2.43` runtime) + 1 of ours, tonight** | 0 | 2 (ours) |

**The delta, in one line:** F1 priced Path A with a pipeline blocker of
*"unknown; non-zero and possibly large"* standing in front of the first rig.
Measured, that blocker is **one export-preset line and a ten-line format
shim** — and the load it was supposed to prevent has now happened. What remains
expensive on Path A is unchanged and was never the tooling: **the licence per
person and the authoring hours per rig**, a median base-game rig being 64 bones
and 28 separately-drawn pieces (F1 §1b) — which for us is a *drawing* bill
before it is a rigging bill.

**The parts of F1's Path A that this does NOT touch**, and which remain the
whole cost: the per-person Editor licence (§6a/b), the authoring hours, the
review loop, and — unresolved — whether a rig can be produced without the
Editor at all (§6c). A cleared tooling gap is not a cleared path, and this is
not a recommendation to take it.

---

## 8. What this changes about the capability spike

Addressed to the `animation-sprint-2` stream.

1. **Two of the spike's open items are closed, and neither closed the way it was
   framed.** F1 §6 item 6 — *"that a spine-enabled MegaDot 4.5.1 editor binary
   can be obtained or built at all"* — is **moot**: nothing in the shipped chain
   is an imported resource (§1), and no editor extension is needed to build or
   to load. F1 §6 item 1 — *"in-engine load of a custom creature skeleton…
   nothing here proves a non-`Sprite2D` `Visuals` child survives at runtime"* —
   is **answered YES** (§3b): a `SpineSprite` scene loaded, resolved and drew
   from our own pack. What is *not* answered is the same item's harder half:
   the probe parented its node to the menu root, **not** into a creature under
   `NCreatureVisuals`' name-based bind. See item 4.
2. **The router does not need rebuilding for any path.**
   `CreatureAnimationRouter` is already the patch shape Downfall runs in
   production on ten characters (§5). Path A′ would add a branch targeting
   `SpineBody.GetAnimationState()`; Paths B and C keep the `%AnimationTree`
   branch they have. **No path invalidates the plumbing** — and if `Visuals` is
   a `SpineSprite`, the game's own `_spineAnimator` revives and the router
   becomes optional for that creature.
3. **Spine and `AnimationTree` are not a fork in the road.** The slimes run both
   at once, with Godot nodes parented to named Spine bones (§5). A future
   character could be a Spine body with layered `Sprite2D` accessories, which is
   a shape neither F1's three-path framing nor ours currently has a name for.
4. **The name-not-type claim is load-bearing and now has evidence on both
   sides.** F1 §2a rests on `NCreatureVisuals` binding children by NAME — which
   is what lets a `Sprite2D` sit where the base game puts a `SpineSprite`.
   Track I's playtest captures record the mirror-image failure: Furina's
   merchant scene auto-converts to `NMerchantCharacter` and the game then throws
   **`Expected BoundObject to be a SpineSprite, but it is a Sprite2D!`** — a
   base-game *Spine* bind site receiving our `Sprite2D` and failing loudly but
   non-fatally.

   **Attribution, honestly:** that error is Track I's capture, not ours. It does
   **not** appear in tonight's `godot.log`, and it could not have — the probe
   boot reached the main menu and never opened a merchant, and the probe's own
   node was parented to the root rather than into a creature. So it is carried
   here as corroborating evidence to verify further, not as a Track M
   measurement.

   What it does establish, taken with §3b: **the name-based contract is not
   universal.** Some base-game sites bind by name (F1 §2a's placeholder scenes,
   and our two shipped characters) and at least one binds by *type* and says so.
   That cuts both ways for the path choice — it is a cost on Paths B and C
   (every such site is a potential loud failure with a non-Spine `Visuals`) and
   a *saving* on Path A′ (a real `SpineSprite` satisfies them all). **The
   remaining Path A′ unknown is therefore not "does it load" but "does it seat"
   — a `SpineSprite` as an actual creature's `Visuals`, in combat, taking
   hits.** That is the next probe, and it is a bigger one.
5. **Two things to be careful about, found in passing, both about our own
   scripts.** `build_pck.ps1` gates on `ERROR` in the *import* log and not the
   *export* log, and the export step is where the spine errors appear (§3a) —
   so a half-packed spine build would look green. And the derived contract is
   built from the **work directory**, not from the pack, so it would list four
   resources the `strict` preset did not ship. Neither is a request to change
   anything; both are recorded because they would bite in exactly the scenario
   this memo is about.
6. **Nothing here is a path decision, and none of it moves the pilot.** The
   tooling gap on Path A′ is cleared; the licence, the drawing bill and the
   review loop are not, and they were always the larger numbers.

### Kokomi as pilot — carried over unchanged

F1 §5 stands verbatim: **a recommended pilot for whichever path [USER] picks,
not a vote for a path.** She is the only one of the three characters without a
layered combat rig (a static 240×280 still from `tools/gen_kokomi_stills.py`);
her open art item is already the live one (Track D); her source art already has a
solved cutout and head-centring rule, which is where every path starts; her shell
track is DONE and pinned, so a rig change cannot be confused with a shell change;
and she has never been seen in-game with her own combat model.

The counter-consideration F1 recorded rather than buried also stands, and this
memo sharpens it rather than softening it: she has the thinnest source pool, and
Path A/A′'s median of **28 separately-drawn atlas regions is a drawing bill**.
§6(c) is the only finding that could change that arithmetic, and it is
unresolved.
