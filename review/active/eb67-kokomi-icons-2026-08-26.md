# EB-67 — Kokomi's relic and power icons

**Date:** 2026-08-26 · **Branch:** `eb67-kokomi-icons` · **Authority:** R212(1)
(art picks: Claude ranks and applies rank 1, `art_lint` still bites, [USER]
vetoes on the contact sheet).

**Contact sheet:**
`art/contact_sheet_eb67_kokomi_icons.html` on the main checkout
(`C:\Users\Monty\Documents\GitHub\GItS\art\`). Open it in a browser. It shows
all three candidates for all eight icons side by side, with rank 1 pre-selected.

---

## 1. What was broken

In the live session on 2026-08-08 two of Kokomi's icons drew the game's `NOPE`
placeholder: the **Pearl of Wisdom** relic in the relic strip, and the
**Bake-Kurage** badge.

Those two were the ones somebody happened to see. The real gap was bigger and
had two halves, both of which had to be fixed for anything to render:

1. **No art.** The mod's asset pack carried Kokomi's model, her UI and her
   Bake-Kurage field sprite — and nothing else. There was no `kokomi/relics/`
   and no `kokomi/powers/` folder anywhere in the pipeline, so every icon path
   the code asked for came back empty and the game fell through to its
   placeholder.
2. **No wiring for the powers.** Separately, the file that tells the game which
   picture each status badge should wear (`KleePowerIcons.cs`) had **no Kokomi
   section at all**. Klee has one, Furina has one, Kokomi had none. So even if
   the art had existed, all six of her status badges would still have drawn the
   placeholder.

The relics were already wired correctly — only the art was missing there.

`tools/build_pck.ps1` needed **no change**. It has always copied
`kokomi\powers` and `kokomi\relics`; it was printing `SKIPPED — no source` every
build because those source folders did not exist. Creating them is the fix.

## 2. What was produced — eight icons

Every Kokomi relic and power the mod registers is now covered. Nothing was left
out.

All eight are **256×256 RGBA**, which is the size every Klee and Furina power
and relic icon already uses (checked against the files on disk, not against a
document).

| # | icon | what wears it | rank 1 source (**applied**) |
|---|---|---|---|
| 1 | `kokomi/relics/pearl_of_wisdom.png` | the **Pearl of Wisdom** relic, and its upgraded form Pearl of Insight — both point at this one file, which is how Klee's and Furina's starter relics already work | `Item Sango Pearl.png` — the clean pearl orb, 256×256, used at exactly its own size with no resizing at all |
| 2 | `kokomi/powers/pearl.png` | the pearl that caps her **Burst gauge** | `Item Sango Pearl Wild.png` — a pearl sitting in an opened shell |
| 3 | `kokomi/powers/bake_kurage.png` | the **Bake-Kurage** badge (the second thing captured broken) | `Bake-Kurage Summon.png` — the game's own art for this exact summon |
| 4 | `kokomi/powers/kurages_oath.png` | **Kurage's Oath** (each Bake-Kurage pulse also grants Block) | `Talent Kurage's Oath.png` — the jellyfish sigil, name-for-name |
| 5 | `kokomi/powers/before_sun_and_moon.png` | **Before Sun and Moon** (the Kurage pulse hits harder) | `Sangonomiya Kokomi Vision.png`, cropped tight onto the Vision itself |
| 6 | `kokomi/powers/ceremonial_garment.png` | **Ceremonial Garment** | `Ceremonial Garment Buff Icon.png` — literally the game's own buff icon for this buff |
| 7 | `kokomi/powers/vigil_of_the_deep.png` | **Vigil of the Deep** (cards are protected from exhausting) | `Namecard Background Sangonomiya Kokomi The Deep.png` — the underwater scene |
| 8 | `kokomi/powers/princess_of_watatsumi.png` | **Princess of Watatsumi** (Charge each turn) | `Talent Princess of Watatsumi.png` — the swimmer sigil, name-for-name |

**Five of the eight are exact name matches** (1, 3, 4, 6, 8) — the source file
is named for the very thing the icon represents. Those five are as close to
"not a judgement call" as this kind of pick gets.

**No two of the eight wear the same picture.** That was a hard constraint, not a
preference: the mod's own notes record that when two different powers share a
sigil, players read it as deliberate — and cleaning up exactly that confusion is
why this file has a rule against it.

## 3. The full shortlist — what else was on the table

Rank 1 is marked **applied**. Ranks 2 and 3 exist so a veto has somewhere to go.

### 1 · `pearl_of_wisdom.png` — the Pearl of Wisdom relic

| rank | source | note |
|---|---|---|
| **1 — applied** | `Item Sango Pearl.png` | A clean pearl orb, already 256×256, so it is used pixel-for-pixel with no resizing. The single cleanest image in the whole set. |
| 2 | `Item Sango Pearl Wild.png` | The same pearl sitting in an opened pink shell. More object-like, arguably more "relic", but it is a screenshot with background clutter. |
| 3 | `Sangonomiya Kokomi Vision.png` | Her Vision. Generic — it says "Kokomi", not "a pearl". |

**The one deliberate call in this set.** Both pearl icons wanted the clean orb.
It went to the relic because the relic draws larger, draws permanently in the
relic strip, and is the surface the live capture actually flagged. That is a
tiebreak on how big the thing renders, not on taste — but it is a call, and it
is the easiest one to overturn: see §5.

### 2 · `pearl.png` — the cap on her Burst gauge

| rank | source | note |
|---|---|---|
| **1 — applied** | `Item Sango Pearl Wild.png` | Pearl in an opened shell, zoomed in so the shell fills the frame. Reads as a pearl at small size. Second choice by quality, first by availability — see the note above. |
| 2 | `Sangonomiya Kokomi Vision.png` | Her Vision. Distinct, but it is a crop of her clothing rather than an object. |
| 3 | `Item Sango Pearl.png` | The clean orb — i.e. swap this pair if you prefer. |

### 3 · `bake_kurage.png` — the Bake-Kurage badge

| rank | source | note |
|---|---|---|
| **1 — applied** | `Bake-Kurage Summon.png` | The game's own summon art: a glowing jellyfish on a starfield. Exact name, exact subject. |
| 2 | `Talent Kurage's Oath.png` | The flat jellyfish sigil. Cleaner as a badge, but it belongs to **Kurage's Oath** by name, and two jellyfish badges would read as one effect. |
| 3 | `Kurage's Oath Preview.gif` | A frame from the skill preview. It is a wide landscape shot with a small figure in it; unusable at badge size. Listed so the shortlist is honest, not as a recommendation. |

### 4 · `kurages_oath.png` — Kurage's Oath

| rank | source | note |
|---|---|---|
| **1 — applied** | `Talent Kurage's Oath.png` | The game's own sigil for the skill of that name. A clean round badge. It is a 128×128 source doubled to 256 — the same doubling every Klee element sigil already ships with. |
| 2 | `Kurage's Oath Preview.gif` | Landscape preview frame; same problem as above. |
| 3 | `Bake-Kurage Summon.png` | A lower crop of the summon art. |

### 5 · `before_sun_and_moon.png` — Before Sun and Moon

**This is the weakest pick in the set and the honest place to say so.** There is
no art in the source pool named for this power, and nothing depicting a sun or a
moon.

| rank | source | note |
|---|---|---|
| **1 — applied** | `Sangonomiya Kokomi Vision.png`, cropped tight | Cropping in on the Vision itself gives a clean gold-ringed blue emblem that reads as a badge and looks like nothing else in the set. The *read* is "her power", which is vague — but it is legible and distinct. |
| 2 | `Talent Nereid's Ascension.png` | A clean round sigil, and it would be a fine badge on its own. **Rejected at rank 1 because it is the same emblem as the Ceremonial Garment buff icon** (icon 6) — same two fish, same plume, different frame. Side by side in the status bar those two would read as the same buff. |
| 3 | `Icon Emoji Paimon's Paintings 13 Sangonomiya Kokomi 2.png` | A chibi sticker of Kokomi with a green up-arrow. It is genuinely the best *"this makes something stronger"* read in the pool — and it has **"+100" printed on it**, which would read as a game number. Offered, not recommended. |

If none of these three please you, the honest next move is a hand-made crop or
paid art, not another trawl of the same pool.

### 6 · `ceremonial_garment.png` — Ceremonial Garment

| rank | source | note |
|---|---|---|
| **1 — applied** | `Ceremonial Garment Buff Icon.png` | This *is* the game's buff icon for this exact buff. As close to a free win as the set contains. It is 100×100 blown up to 256, which is the largest enlargement in the set (2.6×) — soft edges, but it is the right picture. |
| 2 | `Nereid's Ascension Ceremonial Garment Water Preview.gif` | Preview frame; dark blue and hard to read small. |
| 3 | `Nereid's Ascension Ceremonial Garment Attack Preview.gif` | Same, one skill preview over. |

### 7 · `vigil_of_the_deep.png` — Vigil of the Deep

| rank | source | note |
|---|---|---|
| **1 — applied** | `Namecard Background Sangonomiya Kokomi The Deep.png` | Named "The Deep" and it is a calm teal underwater scene with coral silhouettes. A scene rather than a symbol, but clean, legible, and unmistakably "the deep". |
| 2 | `Item Sangonomiya Kokomi The Deep.png` | The same artwork as a small framed namecard thumbnail — the white border shows. Strictly worse. |
| 3 | `Nereid's Ascension Ceremonial Garment Water Preview.gif` | A later frame of the preview. |

### 8 · `princess_of_watatsumi.png` — Princess of Watatsumi

| rank | source | note |
|---|---|---|
| **1 — applied** | `Talent Princess of Watatsumi.png` | The game's own sigil for the passive of that name. Exact match; a clean round badge, doubled from 128 like the others. |
| 2 | `Sangonomiya Kokomi Item.png` | Her character-card stack. Reads as "Kokomi", not as an effect. |
| 3 | `Side by Side We Venture Character Kokomi.png` | A chibi sticker. Off-register beside the sigils. |

## 4. What is on the branch

- `art/plan.tsv` — 24 new rows (eight icons × three candidates) plus a comment
  block explaining the gap and the reasoning. **This is the part that matters.**
  The picture files themselves live in `ImageGen/images/`, which is deliberately
  never committed (the art is licensed for private builds only), so the plan is
  the thing that travels and the pictures get re-made from it on the machine
  that builds.
- `klee-mod/KleeCode/Powers/KleePowerIcons.cs` — the missing Kokomi section: six
  lines mapping her six status badges to the six new files, with a comment
  recording why the block was absent.
- `review/active/eb67-kokomi-icons-2026-08-26.md` — this file.
- `docs/current/BACKLOG.md` — the EB-67 row's **Next action** only. The row stays
  open, because its acceptance is a live look and nobody has taken one yet.

Not on the branch, on purpose:

- The eight PNGs. Generated and checked in this branch's working copy (all eight
  confirmed 256×256 RGBA), but `ImageGen/images/` is never committed.
- The contact sheet HTML. `art/contact_sheet_*.html` is never committed either —
  same rule, and the same as every earlier art run, which all cite their sheet
  by path. It is written and waiting at
  `C:\Users\Monty\Documents\GitHub\GItS\art\contact_sheet_eb67_kokomi_icons.html`.
- Any change to `tools/build_pck.ps1`. It never needed one.

## 5. How to veto

Open the contact sheet, click a different candidate, press **Export picks.tsv**,
then on the main checkout run:

```
python tools/art_process.py --apply-picks art/picks.tsv
```

That overwrites just the icons you changed. Nothing else moves.

**The single most likely veto** is icon 1 versus icon 2 — the two pearls. If you
want the clean orb on the Burst gauge instead of the relic, pick rank 3 on
`power_kokomi_pearl` and rank 2 on `relic_pearl_of_wisdom`; that swaps them.
Both files are already rendered and waiting.

## 6. What still needs the main checkout

Nothing below can be done from a worktree, and none of it has been done.

1. **Merge the branch**, then re-make the pictures:
   `python tools/art_process.py --apply-picks art/picks.tsv` (with the eight
   asset ids listed at rank 1, or just re-run the sheet's export). This creates
   `ImageGen/images/kokomi/powers/` and `ImageGen/images/kokomi/relics/` on the
   machine that builds.
2. **`tools/build_pck.ps1`.** It will stop printing `SKIPPED: kokomi\powers` and
   `SKIPPED: kokomi\relics` and start packing them. That line changing is the
   proof the fix landed.
3. **Deploy.**
4. **One live look**, which is what actually closes EB-67: start a Kokomi run and
   confirm (a) the **Pearl of Wisdom** relic in the relic strip is a pearl and
   not `NOPE`, and (b) the **Bake-Kurage** badge is a jellyfish and not `NOPE`.
   The other six icons ride along on the same fix; if those two render, they all
   do.

The C# change could not be compiled from the worktree either — the build needs a
machine-local config file that only the main checkout has. It is six lines in a
pattern the file already uses forty-five times, but it is **unverified against a
compiler** and the build in step 2's neighbourhood is the first thing that will
say so.

## 7. One thing found on the way, out of scope

The same audit that found Kokomi's six unwired powers found **seven more powers
with no icon mapping at all**, none of them Kokomi's:

`AncientSeaAuthorityPower`, `CannonFireSupportPower`, `ExplosivesWorkshopPower`,
`MasqueRedDeathPower`, `MetallicizePower`, `NightVigilPower`, `SalonCapUpPower`.

Four are Fontaine companion powers, one is a Furina Salon power, two are Klee's.
Each of them draws the same `NOPE` placeholder today, for the same reason. This
is reported, not filed — opening a row for it is not this task's call.
