## Act assets (a zone dressing's own background, rest site and map art)

Scope: the files an `ActModel` needs so the game's own loaders are satisfied
without borrowing another zone's. Read this when a dressing is added, when an
act asset moves, or when a dressed run throws out of `BackgroundAssets`.

```powershell
# regenerate the whole placeholder set (art-bearing main checkout)
.venv\Scripts\python.exe tools\gen_act_placeholders.py
.venv\Scripts\python.exe tools\gen_act_placeholders.py --check   # staleness gate
.venv\Scripts\python.exe tools\gen_act_placeholders.py --list    # the res:// rows
powershell -File tools\build_pck.ps1                             # then the pack
```

### The shape

There are **six dressings**, two a face for each of the three acts (R273
layout 1): act 1 as Mondstadt or Liyue, act 2 as Natlan or Inazuma, act 3 as
Fontaine or Sumeru. Act 1's pair dresses two base zones; acts 2 and 3 have one
base zone each (the Hive, Glory) with two faces standing on it. **None of that
reaches this page** — a face costs the same eighteen files either way, because
every path derives from `ActModel.FilePathIdentifier`, which is
`Id.Entry.ToLowerInvariant()` — `MONDSTADT` → `mondstadt`, `NATLAN` →
`natlan`. The five properties
over it are **non-virtual** (`ActModel.cs:52-64`, `:248`), so a subclass cannot
move a single one of them: the file is at the derived path, or it is nowhere.

| What | Path (`<id>` = the lowercased `Id.Entry`) | Count | Size | Root node the engine casts to | Fallback if missing |
|---|---|---|---|---|---|
| Background layer scene | `res://scenes/backgrounds/<id>/layers/<id>_bg_NN_x.tscn` | 5 groups × ≥1 variant | — | `Control` (ours: `TextureRect`) | **none — throws** |
| Foreground layer scene | `res://scenes/backgrounds/<id>/layers/<id>_fg_x.tscn` | ≥1 | — | `Control` | none (fg may be absent, but a *badly named* file throws) |
| Layer plate | `res://teyvat/backgrounds/<id>/<id>_bg_NN.png`, `…_fg.png` | 6 | 1382×648 | — | dangling `ExtResource` |
| Background root scene | `res://scenes/backgrounds/<id>/<id>_background.tscn` | 1 | — | **`NCombatBackground`** | **none — cast throws** |
| Rest-site scene | `res://scenes/rest_site/<id>_rest_site.tscn` | 1 | — | `Control`, must carry `%RestSiteLighting` | **none — throws** |
| Rest-site plate | `res://teyvat/rest_site/<id>_rest_site_bg.png` | 1 | 1382×648 | — | dangling `ExtResource` |
| Map ground | **the BASE ZONE's** `res://images/packed/map/map_bgs/<zone>/map_{top,middle,bottom}_<zone>.png` | 0 of ours | 2035×1440 | — | **none — throws**, which is why the patch below exists |
| Map overlay | `res://teyvat/map/<id>_wordmark.png`, `<id>_vignette.png` | 2 | 900×160, 2035×1440 | `TextureRect` | **absent is fine** — the overlay stands down |
| Act title | loc table `acts`, key `<Id.Entry>.title` | 1 row | — | — | renders the raw key |
| Map colours | `MapTraveledColor` / `MapUntraveledColor` / `MapBgColor`, `abstract` on `ActModel` | 3 | — | — | compile error |

Fifteen files a dressing, plus one loc row and three colours that live in
C#. Six dressings, so 90 rows and six loc rows. The two overlay pictures are
counted separately because they are OPTIONAL: every one of the fifteen throws
when it is missing, and neither of the two does.

**The five rules underneath the table**, each of them a throw if broken:

1. `BackgroundAssets`'s constructor (`Rooms/BackgroundAssets.cs`) opens
   `res://scenes/backgrounds/<id>/layers` with `DirAccess` and throws
   `InvalidOperationException` if the directory is absent, if it holds a
   subdirectory, or if **any** file there matches neither `_bg_` nor `_fg_`.
2. It groups the `_bg_` files by the segment after `_bg_` (`00`, `01`, …),
   sorts the groups by that key, and draws **one file per group** with
   `rng.NextItem`, then makes **one further draw** over the `_fg_` list. The
   number of draws is therefore the number of groups plus one, whatever the
   variant count — so a dressing that keeps the base zone's **group count**
   consumes the base zone's rng identically. Overgrowth, Underdocks, the Hive
   and Glory all ship `bg_00`..`bg_04` plus a foreground; so do all six
   dressings.
3. `NCombatBackground.Create` instantiates the background root and **casts** it
   to `NCombatBackground`, then calls `GetNodeOrNull("Layer_00")` ..
   `Layer_{n-1}` for the chosen layers and `"Foreground"` for the fg, throwing
   on a miss. The root scene needs those six child nodes by plain name.
4. `NRestSiteRoom._Ready` does `control.GetNode<Control>("%RestSiteLighting")`
   — `GetNode`, not `GetNodeOrNull` — so the rest-site scene must carry a node
   with that name and `unique_name_in_owner = true`.
5. `ActModel.AssetPaths` hands the background scene and all three map PNGs to
   `PreloadManager.LoadActAssets`, so a missing one fails the act's preload
   rather than the screen that draws it. That is exactly why the map ground had
   to be *redirected* rather than merely un-filled (the section below): an
   emptied `map_bgs/<id>/` directory is a failed preload, not a blank screen.

### The root scene is the only one that needs BaseLib

A mod pck cannot carry an `ext_resource type="Script"` row (the `SD-SCRIPT`
rule; scripts do not ship in a mod pack, and `NCombatBackground`'s own script
is the game's, at `res://src/Core/Nodes/Rooms/NCombatBackground.cs`). So the
background root is a script-less `Control` and BaseLib's scene conversion turns
it into an `NCombatBackground` on instantiation — the EB-760 mechanism the
still portrait already uses, with one extra step: **BaseLib ships six node
factories and none of them is for this type**, so
`klee-mod/KleeCode/Teyvat/NCombatBackgroundFactory.cs` supplies the missing one
and `TeyvatActAssets.RegisterActBackgrounds` builds it and registers every
dressing's root scene at `[ModInitializer]` time. Everything else in the table — layer scenes,
the rest site — is instantiated as a plain `Control` and needs no conversion at
all.

### The placeholder recipe

`tools/gen_act_placeholders.py` writes two-stop vertical gradients in the
nation's colours — Mondstadt sky-blue over meadow green, Liyue amber over
stone, Natlan warm red over gold, Inazuma violet over indigo, Fontaine teal
over white, Sumeru green over sand — darkening each layer toward the
foreground so five flat plates read as five planes. It writes **only** under
`ImageGen/images/teyvat/` (gitignored, Tier F) and `klee-mod/pck-src/scenes/` (committed, because a `.tscn` is text
and because `pck-src` overlays the export work directory verbatim, which is the
only thing that can put a file at `res://scenes/...`). `git status --short
ImageGen` prints nothing after a run; the forty-eight scene sources are
committed and `--check` fails if one drifts from what the generator would
write.

### The map ground is the game's own, and the dressing sits over it

**Reverted 2026-09-17**, on [USER]'s read of the shipped frame: *"the map is
harder to read than the normal Slay the Spire 2 map; I like the basic idea but
perhaps we went off the rails replacing the map background with Genshin images
and we should instead try to come up with a Genshin-themed map overlay that
keeps the basic idea of the map intact."*

What shipped on 2026-09-17 morning was eighteen real location stills — three a
face, 2035×1440, at `res://images/packed/map/map_bgs/<id>/` — **overriding** the
base game's painted map wall. The map's node icons, its travelled and
untravelled path lines and its legend are all drawn against that wall's low
contrast, so a bright city plate underneath them takes contrast away everywhere
at once; Sumeru's teal icons over a bright plate and Natlan's top reading
celestial were both named on sight.

**The revert is a patch, not a deletion**, and the reason is rule 5 above.
`MapTopBgPath`, `MapMidBgPath` and `MapBotBgPath` derive from
`FilePathIdentifier` and are non-virtual, so emptying the directory leaves three
derived paths that the act's *preload* then fails on.
`KleeCode/Teyvat/Patches/ActMapBgPathPatch.cs` postfixes all three getters and
swaps the face's id for the base zone's inside whatever string the getter built
— `mondstadt` → `overgrowth`, `natlan` → `hive` — which is the same mapping
`TeyvatFrame.AssetAlias` already holds. A string swap rather than a rebuilt path
because the only part of that string that is ours is the identifier, and it
appears twice; the prefix and the extension are the game's and nothing here
wants to depend on them. `AncientPicture.Borrow` still guards it, so a face that
one day ships a *readable* ground of its own wins on `ResourceLoader.Exists`
with no code change.

**What dresses the map now** is `KleeCode/Teyvat/MapOverlay.cs`, attached by a
Harmony postfix on `NMapScreen.Open`
(`review/dispatch3/s12-public-patterns/s12c-act-map.md`, the "Map-screen
overlay" row, is the pinned precedent), and it is three children of one
`MouseFilter = Ignore` `Control`:

| Child | What | Where it comes from |
|---|---|---|
| `NationTint` | `ColorRect`, the nation's hue at **12%** | `MapOverlay.Tints`, one hex a face |
| `NationVignette` | the face's own location still, darkened to 35% and alpha-masked **clear across the central 70% width / 80% height** | `art/plan.tsv`, mode `vignette` |
| `NationWordmark` | the nation's white loading-screen emblem, in a transparent 900×160 strip at the top centre | `art/plan.tsv`, mode `contain` |

The clear box is the design: the overlay may not touch the part of the frame
where nodes, paths and the legend are drawn, so the still exists only in the
margins. `tools/art_process.py`'s `vignette` mode is the three constants
(`VIGNETTE_DARKEN`, `VIGNETTE_CLEAR`, `VIGNETTE_EDGE_ALPHA`) and
`tier0/tests/test_map_overlay_plan.py` measures both ends of the ramp off them.

**Everything about the overlay is optional and the arm-off build is
byte-identical.** `MapOverlay.ShouldAttach` leads with `TeyvatFrame.Enabled`; a
base zone reached with the arm on dresses nothing; each picture is asked of
`ResourceLoader.Exists` before it is loaded, so a pack that predates the art
draws the base map; and the insertion point is reached with `GetNodeOrNull`
through a candidate list, falling back to the screen itself at child index 1.
That last part is a **guess** — `game_ref/` holds no decompile of `NMapScreen` —
and the first attach of a run logs two levels of the screen's child tree to
`godot.log` behind the arm so it stops being one. Grep `teyvat:maptree`.

Sizes are the engine's, not a taste. The layer `TextureRect`'s rect is
2764.8 × 1296 with `expand_mode = 1`, which **scales** the texture to the rect,
so the plate is authored at half that on exact aspect. The map screen's three
`TextureRect`s are `expand_mode = 1`, `stretch_mode = 5`
(KEEP_ASPECT_CENTERED), so **aspect** is what must be right — and the vignette
is authored at the base game's own 2035 × 1440 for exactly that reason, so its
clear centre lands over the ground it covers.

### The layer scenes must ship as `.tscn`, not as `.tscn.remap`

`tools/build_pck.ps1`'s generated `project.godot` carries

```
[editor]

export/convert_text_resources_to_binary=false
```

and that line is load-bearing. It is a **project setting**, not an export-preset
option, and it defaults to **true** — with it on, Godot packs every `.tscn` as a
binary `.scn` under `.godot/imported/` plus a `<name>.tscn.remap` stub at the
original path.

`ResourceLoader` follows a remap transparently, so anything reached **by name**
loads either way: the background root
(`SceneHelper.GetScenePath("backgrounds/<id>/<id>_background")`), the rest site,
the still portraits. The **layers** are not reached by name.
`Rooms/BackgroundAssets`'s constructor `DirAccess.Open`s
`res://scenes/backgrounds/<id>/layers` and takes each `GetNext()` filename
**verbatim** (`text + "/" + next`), so on a remapped pack it builds
`.../<id>_bg_00_a.tscn.remap` — a path no loader recognizes. The preload marks
it failed (`AssetLoadingSession.cs:235` → `AssetCache.MarkAssetFailed`), and
`NCombatBackground.AddLayer`'s `GetScene` then throws
`AssetLoadException: Asset previously failed to load` **inside**
`CombatManager.SetUpCombat`: combat never starts and the run is stuck on floor
1. That is the blocking defect of
`git show ecfa839d:review/records/teyvat-proofs-3-2026-09-15.md`, and it only surfaced once the
placeholder sets were complete enough for the alias to stand down and the real
layer paths to be used for the first time.

The base game settles what correct looks like. `SlayTheSpire2.pck` carries 173
raw `scenes/backgrounds/*/layers/*.tscn` entries and **not one** `.tscn.remap`;
its only 56 remaps are `.gd.remap`, and this pack ships no scripts at all
(`script_export_mode=2`). So the setting is not a workaround — it is matching
the packaging the engine's own code was written against.

It also re-aligns the pack with its own contract, which is derived from the
export **work directory** and so has always listed
`...liyue_bg_00_a.tscn` while the shipped pack held
`...liyue_bg_00_a.tscn.remap`. Nothing compares the contract's rows to the
pack's actual entries, which is why that divergence was silent.

Two things guard it now: `tier0/tests/test_act_placeholder_plan.py` pins the
line inside that heredoc, and `TeyvatActAssets.HasDressedAssets` asks
`FileAccess.FileExists` — **not** `ResourceLoader.Exists`, which answers only
for paths a loader recognizes and so cannot see a `.remap` at all — whether a
stub sits where the first layer should be. If one does, the dressing keeps the
alias and draws the base zone's art: a picture we did not choose, rather than a
run that cannot be played.

One consequence to know: `AssetCache`'s failed-asset set is never cleared for
the process lifetime, so a client that has already hit this must be
**restarted**, not merely re-deployed into.

### Real art: the plan produces, `media/ACT.tsv` records

**Landed 2026-09-17, revised the same day.** The twenty-four pictures a
dressing actually shows — `bg_00`, the rest site, the map wordmark and the map
vignette, six dressings by four surfaces — are real wiki files now, fetched and
cropped by twenty-four `art/plan.tsv` rows and recorded one-for-one in
`media/ACT.tsv` (the three map-ground rows a face used to carry are the revert
above; the vignette reuses the still the retired `map_middle` row fetched, so
the change cost six new downloads and not twelve) (`operations/media.md` §1, §2;
the survey is `research/teyvat-act-art-sources-2026-09-17.md`). No scene is
re-authored and nothing in `klee-mod/KleeCode` changes: the scene names the
path, the plan names the picture, the ledger names where it came from.

The generator keeps every path the plan does not claim. `plan_owned()` reads
`art/plan.tsv` for out-paths under
`ImageGen/images/teyvat/backgrounds|rest_site|map`, and both `write_all`
and `--check` skip them, so there is still exactly one producer per out-path.
What it still writes for a dressed face is the four layers and the foreground
over a real `bg_00`, as **fully transparent** plates: `NCombatBackground`
stacks `Layer_00`..`Layer_04` and the foreground over one another, so a
gradient on `bg_01` would hide the landscape underneath it. Transparency is the
generator's job rather than five more plan rows because a transparent plate is
not art — no source to pick, no crop to judge, nothing for a veto to look at.
Parallax is not attempted.

A plate [USER] supplies by hand still takes the `media/raw/act/…` →
`media/out/act/…` route of `operations/media.md` §1, with `<act-or-scene>`
reserved as `act1_mondstadt`, `act1_liyue`, `act2_natlan`, `act2_inazuma`,
`act3_fontaine` and `act3_sumeru`.

One thing the sources make you crop around: the wiki's in-game location stills
carry a burnt-in **GENSHIN IMPACT wordmark in the bottom-right corner**, and
the plan's `focus` column is the rule that removes it. A 1382×648 plate off a
16:9 source has 130 scaled pixels of spare height, so `top` spends all of it
off the bottom; a 2035×1440 vignette fills the height exactly on a 16:9
source, so its only spare strip is horizontal and `x0.42` spends it off the
right. The wordmarks are `Emblem <Nation> White.png`, which carry no such
mark.

### The alias patch, and when it still fires

`KleeCode/Teyvat/Patches/ActFilePathIdentifierPatch.cs` rewrites the identifier
so a dressing wears the base zone's clothes. With this set landed it **stands
down for every dressing**: `TeyvatActAssets.HasDressedAssetsCached` asks
`ResourceLoader.Exists` for the first layer scene, the background root and the
rest-site scene — and `FileAccess.FileExists` that no `.tscn.remap` stub stands
where that first layer should be (the section above) — and the postfix returns
untouched when all four answers agree.
It still fires — and must — for a dressing with no set of its own and for a
build whose pck predates one, because the set is **all-or-nothing**: there is
no engine state in which two of the three files are used and the third falls
back. (A directory is not a resource, which is why the probe asks for the first
layer *scene* rather than for the `layers` path.)
