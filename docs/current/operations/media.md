## Media pipeline (music and still portraits)

Scope: the **music tracks** and the **enemy / NPC still portraits** of the
Teyvat run frame (R272, `review/ruled/teyvat-run-frame-2026-09-14.md` §1.4,
§2, §5). Tier F exactly as art is: the files never ship to the repo, never
enter a commit, and are supplied by [USER] into gitignored raw roots on the
art-bearing main checkout. **Only the ledgers and the tools are tracked.** A
copyright pass is owed before anything is public, so every row carries its
provenance from the first file placed and the pass is a filter on one column.
Character stills are NOT in scope — they stay with `operations/art.md`.

**Where a portrait becomes a creature in the game (`EB-811`).** The ledger
records a plate; what *wires* it is one table,
`docs/current/dossiers/content/enemy-dressings.tsv`, whose row says which body
dresses which base-game `Id.Entry` on which face, under which display name, at
which size class (`regular` / `elite` / `boss`, scaling the plate and its
bounds together). `tools/gen_teyvat_creature_scenes.py` reads that table and
writes both halves together — the committed scene
`klee-mod/pck-src/teyvat/creature_visuals/<body>.tscn` and the C# tables
`TeyvatFrame.StillPortraits` and `MonsterNames`
(`klee-mod/KleeCode/Teyvat/TeyvatCreaturesGenerated.cs`) — so a body cannot get
its picture without its name. Run it with `--check` before a push;
`tier0/tests/test_teyvat_creature_scenes.py` rides that gate. Dressing one more
body is therefore a `plan.tsv` row, a `PORTRAITS.tsv` row and a table row, and
no code change at all.

### 1. Layout

```
media/raw/music/<scene>/<track>.ogg              gitignored, [USER] fills
media/raw/portraits/<body>/<name>.png           gitignored, [USER] fills
media/out/music/<scene>/<track>.ogg             gitignored, produced
media/out/portraits/<body>/<name>.png           gitignored, produced
media/MUSIC.tsv                                 tracked ledger
media/PORTRAITS.tsv                             tracked ledger
media/ACT.tsv                                   tracked ledger
```

`<body>`: the enemy or NPC id as the mod names it, one directory per body.

**`<scene>` is a SLOT, and the grammar has exactly two shapes** (2026-09-17,
`research/sts2-music-map-2026-09-17.md`):

```
<face>/<slot>     face-scoped, nested one level
menu | shop | rest    global, a bare name
```

`<face>` is one per face, `act<N>_<nation>` — `act1_mondstadt`, `act1_liyue`,
`act2_natlan`, `act2_inazuma`, `act3_fontaine`, `act3_sumeru` (R273's layout 1,
two faces per act). `<slot>` is one of **`combat`, `elite`, `boss`, `map`** —
twenty-four face scenes, plus the three global ones, twenty-seven in all, and
that list is the packager's whitelist verbatim.

**Why those four and not the game's ten.** `NRunMusicController.UpdateMusic`
reads only the act: it draws one FMOD event out of `ActModel.BgMusicOptions`
against the run seed and nothing else. Room variation in the base game is a
**parameter** (`Progress`, ten values) on that one event, moved by
`UpdateTrack()`, and the only place the game swaps the whole event is a boss
encounter's `EncounterModel.CustomBgm`. Our replacement is a whole file, so a
slot is a file: the four are the four room characters worth a different piece
of music, and `Treasure`, `Event` and a won combat all take the face's `map`
loop. The event list and the full trigger table are in the research page.

**Global means no dressing resolves it.** `menu` plays over the main menu,
where there is no run and no act at all; `shop` and `rest` are deliberately
one track each across all six nations, so a merchant reads as a merchant
everywhere. A global slot has **no fallback** — nothing filed means the game's
own music plays on.

**These names are the spec and the reader resolves to them.**
`TeyvatFrame.MediaScene(entry, slot)` turns a dressing's `Id.Entry` and a slot
into the scene name, so a track filed here is found without a packager-side
rename — the packager copies the `scene` column through verbatim, because a
rename there would be a second name for the same thing and the ledger would
stop describing the pack. The twenty-seven scenes are pinned against the six
faces and the seven slots in `KleeTests`, and against the packager's own list
in `tier0/tests/test_music_ledger_gate.py`, which holds the three sides —
whitelist, this page's list, and the resolver's own slot set — against each
other.

**Nesting is measured, not assumed** (MegaDot 4.5.1 headless, the packager's
own `project.godot` and export preset, 2026-09-17). Exporting
`teyvat/music/act1_mondstadt/combat/music_combat_A.ogg` packs exactly the two
entries a flat scene packs — `.godot/imported/<name>.ogg-<hash>.oggvorbisstr`
and `teyvat/music/act1_mondstadt/combat/<name>.ogg.import` — and with that pack
mounted, `DirAccess.get_files_at` of the nested directory returns
`["music_combat_A.ogg.import"]`, `get_directories_at` of the parent returns
`["boss", "combat"]`, `ResourceLoader.exists` is true for the stripped `.ogg`
and false for the sidecar, and the load returns an `AudioStreamOggVorbis`.
`DirAccess.dir_exists_absolute` of a nested scene with nothing filed answers
false and prints nothing, which is the silence `EB-758` bought.

`media/out/` is what the packager reads; nothing else is packaged. **One
producer per out-path** — exactly one ledger row may name a given `out`, and
only the media tool writes under `media/out/`; a hand-placed file there is a
defect, the rule `art/plan.tsv` already runs under.

**The enemy still portraits are the one surface where `art/plan.tsv` is the
producer and this file is only the record** (ruled 2026-09-16,
`research/teyvat-portrait-sources-2026-09-16.md` §3 addendum): their sources
are wiki files, which is `plan.tsv`'s whole job, so an `art/plan.tsv` row
fetches and cuts each one into
`ImageGen/images/teyvat/creature_visuals/<body>.png` — the directory
`tools/build_pck.ps1`'s Teyvat block already copies to
`res://teyvat/creature_visuals/` — and the `media/PORTRAITS.tsv` row for that
body records it, with `out` naming that produced path, `raw` the `art/raw/`
file the fetch wrote, and `origin` the wiki `File:` page. That is not an
exception to "one producer per out-path"; it is how the rule is kept, since
routing the same pixels through `media/out/` as well would create the second
producer. `media/raw/portraits/` and `media/out/portraits/` stay the route for
a portrait [USER] supplies by hand.

**Act plates: the plan produces and `media/ACT.tsv` records**, the same
reconciliation the still portraits took, and for the same reason — their
sources are wiki files, which is `art/plan.tsv`'s whole job (ruled 2026-09-17,
`research/teyvat-act-art-sources-2026-09-17.md`). Thirty plan rows, six
dressings by five surfaces, fetch and crop each plate into
`ImageGen/images/teyvat/backgrounds/<id>/<id>_bg_00.png`,
`ImageGen/images/teyvat/rest_site/<id>_rest_site_bg.png` and
`ImageGen/images/teyvat/map_bgs/<id>/map_{top,middle,bottom}_<id>.png` — the
directories `tools/build_pck.ps1`'s Teyvat act blocks already copy from — and
`media/ACT.tsv` carries one row per plate recording it, columns
`out raw dressing surface w h title origin licence notes` with `surface` one of
`bg_00`, `rest_site`, `map_top`, `map_middle`, `map_bottom`. `out` names the
produced path (not a `media/out/` path: the plan is the producer, and naming it
is what keeps "one producer per out-path" true), `raw` the `art/raw/` file the
fetch wrote, `title` the bare wiki file title and `origin` its
`https://genshin-impact.fandom.com/wiki/File:…` page.
`media/raw/act/` and `media/out/act/` stay the route for a plate [USER]
supplies by hand.

What is different — and the reason act plates have a page of their own,
`operations/act-assets.md` — is that their `res://` paths are **not ours to
choose**: `ActModel`'s five asset-path properties are non-virtual and derive
every one of them from the act id, so the `out` column names the file and the
act's id names where it goes. `tools/gen_act_placeholders.py` keeps every path
no plan row claims, filling it with a nation-tinted gradient and taking no
ledger row at all — it is a generator, on `gen_furina_stills.py`'s terms, not a
media drop — and it reads `art/plan.tsv` to know which those are. Over a real
`bg_00` it also writes the four layers and the foreground as fully TRANSPARENT
plates, so the landscape underneath shows through.

Both ledgers are **UTF-8, no BOM**, like `art/plan.tsv` and `art/SOURCES.tsv`.
**Line endings are LF and are not this page's to choose:** `.gitattributes` is
`* text=auto eol=lf` repo-wide, so a CRLF ledger is converted on the way into
the index and checked back out as LF — a machine that hand-wrote CRLF gets
`git add`'s "CRLF will be replaced by LF" warning and a file that does not match
itself after the next checkout. Read them the tolerant way regardless
(`encoding="utf-8", newline=""` then `rstrip("\r\n")`, or .NET's
`File.ReadAllLines`), because a ledger edited in a Windows editor arrives with
CRLF until git normalises it, and split on TAB alone — a stray `\r` riding into
`notes` makes the last column silently stop matching. TSV and not CSV, and not
by taste: `.gitignore` ignores `*.csv` repo-wide, so a `.csv` ledger would be
untracked and the provenance record would not exist.

### 2. Ledger columns

`media/MUSIC.tsv`:

```
out	raw	scene	title	origin	licence	loop_start_s	notes
```

`media/PORTRAITS.tsv`:

```
out	raw	body	surface	w	h	title	origin	licence	notes
```

`media/ACT.tsv`:

```
out	raw	dressing	surface	w	h	title	origin	licence	notes
```

- `out` / `raw` — paths under `media/out/` and `media/raw/`. `out` is the
  packager's key and is unique across the file.
- `scene` / `body` + `surface` / `dressing` + `surface` — where it plays, who
  it draws, or which plate of which dressing it is.
- `title` — the source's own name ("Rage Beneath the Mountains", the wiki file
  title), never a paraphrase.
- `origin` — the official OST album and track number, or a URL [USER] supplies;
  the style of `art/SOURCES.tsv:source_url`.
- `licence` — **defaults to `PLACEHOLDER-COPYRIGHTED`.** Also `ORIGINAL`,
  `CC-BY-<x>`, `PUBLIC-DOMAIN`. The pre-public pass is
  `grep PLACEHOLDER-COPYRIGHTED media/*.tsv` and nothing else; a non-empty
  result blocks a public build.
- `loop_start_s` — seconds; blank means loop from 0 (§3).
- `w` / `h` — the portrait's exact pixel size, so a wrong-sized drop is caught
  in the ledger rather than in the frame.

### 3. Formats

**Music: OGG Vorbis is the default** (`AudioStreamOggVorbis`). MP3 is accepted
(`AudioStreamMP3`) and is the only other format to place; never WAV. Both carry
`loop` and `loop_offset`, so the **loop convention is one ledger column, not a
filename suffix**: the packager sets `loop = true` and `loop_offset` from
`loop_start_s`. Loop points are never encoded in the audio.

**Portraits: PNG, RGBA, 240x280** — the size the roster's own combat surface
uses (`tools/gen_furina_stills.py` header: `model/combat_model.png 240x280`),
so a still enemy body draws by the route our characters already take out of
combat (`klee-mod/KleeCode/Vfx/StaticPortraitIdle.cs`). A body that
needs a different size states it in `w`/`h` and says why in `notes`. Alpha is
required: the portrait composites over the arena, not over a plate. A WebP
served with a `.png` extension is re-encoded in the scratch copy by
`tools/build_pck.ps1` already; never fix one by hand in `media/raw/`.

### 4. The manifest gate

There is no manifest to extend — `tools/build_pck.ps1` has **hand-written copy
blocks**, one per surface, each a `Test-Path` + `Copy-Item` that calls
`Note-Skip` on a missing source, and the pck contract is DERIVED from the work
directory after the export (`contract=roster-pck-v3`). So the smallest
extension is one more copy block, gated on the ledger:

1. Read `media/MUSIC.tsv` and `media/PORTRAITS.tsv` with the encoding rule
   above.
2. For each row, copy `media/out/<out>` into the scratch project. **A file
   under `media/out/` with no ledger row is never copied**, and a row whose
   `out` is missing on disk calls `Note-Skip` like every other block — the
   build stays green and prints the gap, art never blocks the build.
3. Write the `.import` loop settings for each audio file from `loop_start_s`.

Nothing else changes in the preset — it stays `export_filter="all_resources"` —
and the derived contract picks the track up with no edit, listing
`res://teyvat/music/<scene>/<track>.ogg`, which is the path that loads. What
makes this more than a one-line manifest addition is that the script is a list
of literal blocks with no table to add a row to, and `Select-PackablePngs` /
`$pckExclude` are PNG-only — audio needs its own enumeration.

**What the pack holds is not the `.ogg`, and that is measured**, not assumed
(MegaDot 4.5.1 headless, the packager's own `project.godot` and export preset).
Importing and exporting `teyvat/music/act1_mondstadt/windborne_dreams.ogg`
packs exactly two entries for it:

```
.godot/imported/windborne_dreams.ogg-<hash>.oggvorbisstr
teyvat/music/act1_mondstadt/windborne_dreams.ogg.import
```

With that pack mounted, `DirAccess.get_files_at` of the directory returns
`["windborne_dreams.ogg.import"]` and nothing else; `ResourceLoader.exists` is
**true** for `.../windborne_dreams.ogg` and **false** for the `.import`. So a
reader that enumerates a music directory must strip `.import` before it asks
the loader — `TeyvatMusic.ImportSuffix` does, and `KleeTests` pins it. Same
class of trap as the `.tscn.remap` stubs above, but the audio importers have no
"ship it as source" switch, so this half of the repair is on the reader rather
than in `project.godot`.

The loop settings of step 3 are written **before** `--import`: Godot's audio
importers read `[params]` out of an existing `.import` and keep them, filling
in `[remap]path` and `[deps]` themselves. Measured the same way — a
hand-written file carrying only `importer` and `[params]` came back with
`loop=true` / `loop_offset=1.25` intact and the loaded `AudioStreamOggVorbis`
reported `loop` true and `loop_offset` 1.25. A blank `loop_start_s` writes no
`.import` at all, so the importer's defaults stand.

Order is unchanged and non-negotiable: **`build_pck` before deploy**, on the
art-bearing main checkout only (`operations/build-deploy.md`).

### 5. `.gitignore` lines

Added to `.gitignore` with this doc; the ledgers stay tracked because they are
not under either root.

```
media/raw/
media/out/
```

### 6. Before any file is placed

```powershell
# 1. roots (main checkout only; gitignored, never committed)
New-Item -ItemType Directory -Force media\raw\music\act1_mondstadt\combat, media\out\music\act1_mondstadt\combat
# 2. drop media\raw\music\act1_mondstadt\combat\windborne_dreams.ogg
# 3. ONE row in media\MUSIC.tsv (UTF-8, LF, tab-separated), e.g.
#    music/act1_mondstadt/combat/windborne_dreams.ogg <TAB> (same)
#    <TAB> act1_mondstadt/combat <TAB> Windborne Dreams
#    <TAB> City of Winds and Idylls d1 t3
#    <TAB> PLACEHOLDER-COPYRIGHTED <TAB> 12.4 <TAB>
# 4. INVISIBLE to git -- prints nothing:
git status --porcelain media/raw media/out
# 5. VISIBLE to the ledger -- prints the row:
Select-String -Path media\MUSIC.tsv -SimpleMatch windborne_dreams
```

If step 4 prints anything, stop: the ignore lines are missing and a commit
would distribute the track.

### 7. Not decided here

- **How music reaches the speakers.** A Godot `AudioStreamPlayer` in the pck
  with the FMOD music bus ducked is the default; an FMOD bank is the fallback
  if the duck cannot hold. The spike decides (run-frame §2, §4.4), and this
  page only says where the file lives.
- **Which counterpart, per slot.** The twenty-seven picks are E defaults under
  the R212 ladder, disclosed in the PR that filed them and vetoed by ear; the
  reason for each is its ledger row's `notes`. What is NOT decided here is
  whether a given face wants a *different* track — that is [USER]'s ear, one
  row at a time, and costs a file swap and one `notes` edit.
- **Loop points.** Every row's `loop_start_s` is blank, because Genshin's music
  wems carry no `smpl` chunk (`research/teyvat-music-sources-2026-09-16.md` §6)
  and most of these are seamless-at-zero loop bodies already. A track that
  audibly restarts wrong gets a hand-measured number in that column and nothing
  else changes.
- **Stingers.** `event:/temp/sfx/game_over` is the game's own and stays: there
  is no clean short counterpart in the extraction, and the run frame has no
  reason to own a death sound. There is no victory or credits music in the
  managed assembly to replace.
