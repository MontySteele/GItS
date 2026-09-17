## Media pipeline (music and still portraits)

Scope: the **music tracks** and the **enemy / NPC still portraits** of the
Teyvat run frame (R272, `review/ruled/teyvat-run-frame-2026-09-14.md` §1.4,
§2, §5). Tier F exactly as art is: the files never ship to the repo, never
enter a commit, and are supplied by [USER] into gitignored raw roots on the
art-bearing main checkout. **Only the ledgers and the tools are tracked.** A
copyright pass is owed before anything is public, so every row carries its
provenance from the first file placed and the pass is a filter on one column.
Character stills are NOT in scope — they stay with `operations/art.md`.

### 1. Layout

```
media/raw/music/<act-or-scene>/<track>.ogg      gitignored, [USER] fills
media/raw/portraits/<body>/<name>.png           gitignored, [USER] fills
media/out/music/<act-or-scene>/<track>.ogg      gitignored, produced
media/out/portraits/<body>/<name>.png           gitignored, produced
media/MUSIC.tsv                                 tracked ledger
media/PORTRAITS.tsv                             tracked ledger
```

`<act-or-scene>`: `act1_mondstadt`, `act1_liyue`, `boss`, `rest`, `map`, `shop`.
`<body>`: the enemy or NPC id as the mod names it, one directory per body.

`media/out/` is what the packager reads; nothing else is packaged. **One
producer per out-path** — exactly one ledger row may name a given `out`, and
only the media tool writes under `media/out/`; a hand-placed file there is a
defect, the rule `art/plan.tsv` already runs under.

**Act plates take the same raw/out route.** A zone dressing's background
layers, rest-site plate and three map backgrounds are Tier F pictures like the
portraits above and land under `media/raw/act/<act-or-scene>/` →
`media/out/act/<act-or-scene>/`, one ledger row each, `<act-or-scene>` being
the same `act1_mondstadt` / `act1_liyue` the music column already uses. What is
different — and the reason they have a page of their own,
`operations/act-assets.md` — is that their `res://` paths are **not ours to
choose**: `ActModel`'s five asset-path properties are non-virtual and derive
every one of them from the act id, so the `out` column names the file and the
act's id names where it goes. Until a real plate lands,
`tools/gen_act_placeholders.py` fills all of those paths with nation-tinted
gradients and takes no ledger row at all — it is a generator, on
`gen_furina_stills.py`'s terms, not a media drop.

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

- `out` / `raw` — paths under `media/out/` and `media/raw/`. `out` is the
  packager's key and is unique across the file.
- `scene` / `body` + `surface` — where it plays or who it draws.
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
New-Item -ItemType Directory -Force media\raw\music\act1_mondstadt, media\out\music\act1_mondstadt
# 2. drop media\raw\music\act1_mondstadt\windborne_dreams.ogg
# 3. ONE row in media\MUSIC.tsv (UTF-8 + CRLF, tab-separated), e.g.
#    music/act1_mondstadt/windborne_dreams.ogg <TAB> (same) <TAB> act1_mondstadt
#    <TAB> Windborne Dreams <TAB> City of Winds and Idylls d1 t3
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
- **Which name the scene leaf carries.** The pck path is settled —
  `res://teyvat/music/<scene>/<track>.ogg`, a namespace of the frame's own
  rather than `res://klee/`, because the frame's media is not one character's —
  but the leaf is not. `TeyvatMusic.TrackFor` looks up
  `Root + actEntry.ToLowerInvariant()`, which is `mondstadt` / `liyue` / … and
  not the ledger's `act1_mondstadt`, and `boss` / `rest` / `map` / `shop` have
  no caller at all. The packager copies `scene` through verbatim rather than
  inventing a rename, so placing the first track is what decides whether the
  ledger's vocabulary or the act id's wins.
