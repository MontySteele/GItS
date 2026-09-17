Status: RESEARCH + PLACED (survey, bill and pixels; the veto is the contact sheet)

# Where the act plates come from

Until today every picture the six Teyvat dressings showed was a two-stop
vertical gradient out of `tools/gen_act_placeholders.py` — sky-blue over meadow
green for Mondstadt, amber over stone for Liyue, and so on. Eighteen files a
dressing, none of them art. This page says which real pictures replace the five
that a player actually looks at, where they were found, and what the terms are.

Thirty plates are placed: six dressings × five surfaces. The other thirteen
files a dressing owns are scenes (which are text, not pictures) and the four
layers plus the foreground stacked over `bg_00` — and those five are now fully
transparent plates, because `NCombatBackground` draws `Layer_00`..`Layer_04`
and the foreground over one another and an opaque gradient on `bg_01` would
simply hide the landscape. Parallax is not attempted.

## 1. The three findings that matter before the tables

**The wiki keeps a systematic in-game location still for nearly every named
place in Teyvat, at `File:<Location Name>.png`.** That family is the whole
answer. It is not enumerable as one category, but it is enumerable per nation:
`Category:<Nation> Locations` lists the location PAGES, and a page named
`Windrise` has a file named `File:Windrise.png`. Counted that way:

| Nation | location pages | with a same-name file | file ≥ 1900px wide |
|---|---|---|---|
| Mondstadt | 79 | 58 | 52 |
| Liyue | 128 | 102 | 101 |
| Natlan | 139 | 95 | 80 |
| Inazuma | 98 | 79 | 73 |
| Fontaine | 126 | 100 | 95 |
| Sumeru | 139 | 119 | 111 |

Sizes run 1920×1080 (the bulk) through 2560×1440 and 3840×2160 to 5120×2880.
Every one of the thirty picks below is from this family, and every one of them
is a downscale or a ≤ 1.34× upscale — under `art_process`'s 1.6 upscale flag,
which never fired on this bill.

**The obvious-sounding families are the wrong ones.** Five were enumerated
and rejected before this one was found:

- `Category:Viewpoint Previews` — 266 files, exactly the "in-game landscape
  still, per region" shape the brief asked for, and enumerable per nation
  through `Category:<Nation> Viewpoints` (Mondstadt 13, Liyue 40, Natlan 42,
  Inazuma 18, Fontaine 37, Sumeru 52). They are all **1024×512**. That is a
  1.35× upscale to a 1382×648 combat plate and a **2.8×** upscale to a
  2035×1440 map plate. Rejected on resolution alone.
- **Loading screens** — the brief's first preference, and there is essentially
  no such family: `allimages` with prefix `Loading Screen` returns four files
  in total, of which exactly one is a region (`File:Loading Screen Mondstadt.png`,
  1364×746). `Category:Loading Screen Emblems` is 56 emblems, not landscapes.
- `Category:Version Wallpapers` — 120 files at 2560×1440 to 4096×2304, the
  highest resolution on the wiki, but they are version key art: characters in
  the frame, usually two or three of them, often with a wordmark. Wrong
  register for a background wall.
- `Category:<Nation> Concept Art` exists only for Mondstadt (14), Liyue (34),
  Inazuma (14) and Fontaine (18), so it cannot cover six faces, and the
  Fontaine set is eighteen frames of one 1920×1080 developer feature.
- `Category:Region Maps` has all six nations at 2200×2200 to 4900×4900 and was
  seriously considered for the map plates: one painted nation map, cropped at
  three vertical anchors, would give a genuinely continuous wall. It was
  dropped because the aspect does not allow it — a 2035×1440 crop is 71% of a
  square source's height, so the three anchors clamp into three nearly
  identical bands. Three distinct landscapes, as the brief's default says, is
  what the shape actually permits.

**The stills carry a burnt-in GENSHIN IMPACT wordmark in the bottom-right
corner**, and the first crop of the first dressing shipped it. The fix is the
`focus` column, not a new mode. A 1382×648 plate off a 16:9 source has 130
scaled pixels of spare height, so `top` spends all of it off the bottom, where
the mark is; a 2035×1440 map plate fills the height exactly on a 16:9 source,
so its only spare strip is horizontal and `x0.42` spends it off the right.
Every one of the thirty plates was looked at afterwards and no mark survives.

## 2. The picks

`Title` is given in the form `art/plan.tsv`'s `wiki_title` column uses — the
title **without** the `File:` prefix, which `art_fetch.py` prepends itself.
Every size was read from the API before the row was written; every row's
`licence` is `PLACEHOLDER-COPYRIGHTED` (§4).

### 2.1 Act 1, Mondstadt

| Surface | Title | Source size | What it shows |
|---|---|---|---|
| `bg_00` | `Windrise.png` | 1920×1080 | the great oak over the meadow, cliffs behind |
| rest site | `Angel's Share Interior 1F.png` | 1920×1080 | the tap room: barrels, lamps, the bar |
| map top | `Stormterror's Lair.png` | 3840×2107 | heights — the broken tower and its waterfall |
| map middle | `Mondstadt City.png` | 4096×2304 | the walled city on its island, windmills turning |
| map bottom | `Cider Lake.png` | 1920×1080 | water — the shallows under the city cliff |

### 2.2 Act 1, Liyue

| Surface | Title | Source size | What it shows |
|---|---|---|---|
| `bg_00` | `Guyun Stone Forest.png` | 1920×1080 | the stone pillars standing out of the sea |
| rest site | `Xinyue Kiosk Interior.png` | 1920×1080 | the dining room: round tables, lanterns, tea |
| map top | `Mt. Xuanlian.png` | 3840×2160 | heights — karst spires and hanging sakura |
| map middle | `Liyue Harbor.png` | 4096×2304 | the harbour, junks, lantern bridges |
| map bottom | `Yaoguang Shoal.png` | 1920×1080 | water — sandbars and orange trees |

### 2.3 Act 2, Natlan

| Surface | Title | Source size | What it shows |
|---|---|---|---|
| `bg_00` | `Tequemecan Valley.png` | 2560×1440 | red mesas, green terraces, a saurian in frame |
| rest site | `Weary Inn.png` | 2560×1440 | the common room under its awnings |
| map top | `Ancient Sacred Mountain.png` | 3840×2160 | heights — floating isles above the cloud deck |
| map middle | `Stadium of the Sacred Flame.png` | 3840×2160 | the arena and its blue banners |
| map bottom | `Toyac Springs.png` | 2560×1440 | water — pools, lily pads, drifting rock |

The Natlan rest site is the same Weary Inn the still-portrait survey already
names for Chanca (`teyvat-portrait-sources-2026-09-16.md` §2.3).

### 2.4 Act 2, Inazuma

| Surface | Title | Source size | What it shows |
|---|---|---|---|
| `bg_00` | `Narukami Island.png` | 1920×1080 | sakura crags over the coastal plain |
| rest site | `Uyuu Restaurant Interior.png` | 1920×1080 | the counter under a row of paper lanterns |
| map top | `Amakumo Peak.png` | 1920×1080 | heights — the violet peak at storm-dusk |
| map middle | `Inazuma City.png` | 4096×2304 | Tenshukaku over the town, in mist |
| map bottom | `Nazuchi Beach.png` | 1920×1080 | water — the beached wrecks |

### 2.5 Act 3, Fontaine

| Surface | Title | Source size | What it shows |
|---|---|---|---|
| `bg_00` | `Belleau Region.png` | 2560×1440 | the countryside under its aqueduct, tower behind |
| rest site | `Hotel Debord Interior.png` | 1920×1080 | the lobby under a glass dome |
| map top | `West Slopes of Mont Automnequi.png` | 3840×2160 | heights — the peak, pines and the viaduct |
| map middle | `Court of Fontaine.png` | 3840×2160 | the city on its ring of water |
| map bottom | `Elynas.png` | 3840×2160 | water — sunlit roots and fish, below the surface |

`bg_00` was re-picked after looking at the first crop. The first pick,
`Salacia Plain.png`, turns out to be an **underwater** shot; it is
unmistakably Fontaine but wrong for an arena, and the Fontaine face's bodies
are the clockwork Meks, which are dry-land enemies. `Elynas` keeps the
underwater register where it belongs, on the bottom map plate.

### 2.6 Act 3, Sumeru

| Surface | Title | Source size | What it shows |
|---|---|---|---|
| `bg_00` | `Caravan Ribat.png` | 1920×1080 | the desert caravanserai in its rock cleft |
| rest site | `Lambad's Tavern Interior.png` | 1920×1080 | stained glass, low tables, a shaft of sun |
| map top | `Mt. Damavand.png` | 1920×1080 | heights — the sandstorm that never stops |
| map middle | `Sumeru City.png` | 1920×1080 | the city in the branches of the Divine Tree |
| map bottom | `Sobek Oasis.png` | 1920×1080 | water — palms and a pool in the red rock |

`bg_00` was re-picked here too. `Hypostyle Desert.png` is technically fine and
visually almost nothing: the source is hazed to a pale lavender wash with no
contrast left, which is a bad wall to fight in front of. The Sumeru face wears
Eremites and Consecrated beasts (`teyvat-portrait-sources-2026-09-16.md` §2.6),
so the dressing leans desert, and `Caravan Ribat` is desert with architecture
in it. The map wall still spans the whole nation — sandstorm, rainforest city,
oasis — because the map screen shows the country, not the arena.

## 3. The bill, and who produces what

Thirty rows in `art/plan.tsv`, `mode=cover`, `pick=auto`, `rank=1`,
`source=png`, `register=splash`, writing to

```
ImageGen/images/teyvat/backgrounds/<id>/<id>_bg_00.png      1382x648  focus top
ImageGen/images/teyvat/rest_site/<id>_rest_site_bg.png      1382x648  focus top
ImageGen/images/teyvat/map_bgs/<id>/map_{top,middle,bottom}_<id>.png
                                                            2035x1440 focus x0.42
```

— the three directories `tools/build_pck.ps1`'s Teyvat act blocks already copy
to `res://teyvat/backgrounds/`, `res://teyvat/rest_site/` and
`res://images/packed/map/map_bgs/`. `media/ACT.tsv` carries one row per plate
(`out raw dressing surface w h title origin licence notes`). **The plan
produces and the ledger records**, exactly the reconciliation the still
portraits took on 2026-09-16, and `operations/media.md` §1 now carries both
sentences.

`tools/gen_act_placeholders.py` keeps every path the plan does not claim. A new
`plan_owned()` reads `art/plan.tsv` for out-paths under
`ImageGen/images/teyvat/backgrounds|rest_site|map_bgs`, and both `write_all`
and the `--check` staleness gate skip them, so there is still exactly one
producer per out-path and `--check` cannot demand a file the generator no
longer writes. The bill is read from the generator's OWN checkout rather than
from `--root`, which is the same split `art_process.py`'s `--art-root` already
runs under: otherwise a worktree run would consult main's plan, find no act
rows, and paint gradients over the landscapes it had just fetched.

The five plates over a real `bg_00` stay the generator's job and turn fully
transparent. That is the generator's rather than five more plan rows because a
transparent plate is not art: there is no source to pick, no crop to judge and
nothing for a veto to look at — the line `gen_furina_stills.py` and the salon
glyphs already sit on. Four new tests in
`tier0/tests/test_act_placeholder_plan.py` pin all of it: the bill claims
exactly thirty paths, `write_all` writes none of them, every layer over a real
`bg_00` is alpha-zero at 1382×648, `--check` reports nothing missing on a fresh
tree, and every bill row has a ledger row with a `PLACEHOLDER-COPYRIGHTED`
licence and a `File:` origin.

## 4. The gaps

**Sourcing gaps: none.** All thirty surfaces are filled, from one family, with
no surface falling back to namecard art and no upscale over 1.34×. Two picks
were re-made by eye rather than by rule (§2.5, §2.6) and both are recorded
above and flagged on the contact sheet.

**What is deliberately not done.** Parallax: `bg_01`..`bg_04` and `fg` carry no
picture, so the combat background is one flat plate rather than five planes.
Separating a still into depth layers is a hand-paint job or a matte per
dressing, and neither is a sourcing question. The nation-tinted gradient
recipe stays in the generator for any dressing added later, and it is still
what a seventh face would get until it has a bill of its own.

**What could not be verified here.** Nothing was launched. These plates are
pixels on disk at the right sizes in the right directories; whether the combat
background, the rest site and the map screen actually draw them is the running-
game proof, and it is the main session's after the merge — `build_pck` then a
`+proto` deploy with the `TeyvatFrame` arm ON. The transparent-layer decision
in particular is a claim about draw order (`NCombatBackground` stacks
`Layer_00`..`Layer_04` and the foreground) that is read out of the decompiled
source and not yet seen on screen.

## 5. The terms

Unchanged from the portrait survey, which is unchanged from `media.md` §2. The
images are HoYoverse's, hosted by the wiki under a fair-use claim rather than a
free licence: every file page carries `{{Fairuse}}`, whose template text says
the media "is subject to copyright" and that its use "qualifies as fair use
under U.S. fair use laws **when used on Genshin Impact Wiki**". That claim
covers the wiki's use, not ours. So every `media/ACT.tsv` row's `licence`
column is **`PLACEHOLDER-COPYRIGHTED`**, the pre-public pass is
`grep PLACEHOLDER-COPYRIGHTED media/*.tsv`, and a non-empty result blocks a
public build. Thirty rows is thirty more things to replace before this can ever
be public; it is Tier F, private build only, exactly like every card-art row in
`art/SOURCES.tsv`.

One practical note, carried forward because it is still true:
`genshin-impact.fandom.com` returns **HTTP 402** to plain page fetches, while
the `api.php` endpoint `art_hunt.py` and `art_fetch.py` use answers normally.
Thirty downloads were taken for this pass, paced at the fetcher's own 0.4s
interval. Never invent a `File:` title; enumerate the category first.
