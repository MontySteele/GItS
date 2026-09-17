Status: RESEARCH (sources survey; nothing downloaded)

# Where the still portraits come from

The Teyvat run frame ships **one** still-portrait enemy today — Nibbit in the
Mondstadt dressing, drawn by `res://teyvat/creature_visuals/hilichurl_guard.tscn`
over a flat green 240x280 placeholder
(`klee-mod/KleeCode/Teyvat/TeyvatFrame.StillPortraits`,
`klee-mod/pck-src/teyvat/README.md`). It is one because nobody has chosen
sources for the rest, not because the seam is hard: the seam is proven and the
remaining work is picking a picture per body. This page picks one, for every
body the six ruled faces reskin, and says what it would cost to place them.

Nothing was downloaded to write it. Every size, file title and colour-type
below came from read-only MediaWiki `imageinfo` and `list=search` queries
against `https://genshin-impact.fandom.com/api.php` — the same API and
User-Agent `tools/art_hunt.py` uses. `tools/art_fetch.py` and
`tools/art_process.py` were never run.

## 1. The three findings that matter before the tables

**Every enemy in Genshin has a public still, and it lives in one place.**
The Fandom wiki keeps a systematic bucket, `Category:Enemy Archive Images`,
holding **356 files** at the time of writing, one per enemy, named
`File:Enemy <archive name>.png`. Its own description says what they are:
"Archive images for each Enemy with aspect ratios of 1:1, 4:3, or 16:9, using
full image height and cropping from the center"
(`https://genshin-impact.fandom.com/wiki/Category:Enemy_Archive_Images`).
That category covers every body this survey needed except one (§4). NPCs —
which is what an Ancient is — use a parallel convention, `File:NPC <name>.png`.

**They are screenshots, not cut-out renders.** This is the finding that costs
money. `imageinfo`'s PNG metadata reports the colour type without downloading
a byte, and every Archive image checked comes back `truecolour` — three
channels, **no alpha** — with `Software: Starward Launcher` in the PNG header,
i.e. a capture of the in-game Archive page. `media/PORTRAITS.tsv`'s format rule
is "PNG, RGBA, 240x280" and says why: "Alpha is required: the portrait
composites over the arena, not over a plate"
(`docs/current/operations/media.md` §3). So a fetched Archive image is a
**source**, not a portrait; something has to cut the background out. The
exceptions are the handful of files a wiki editor cut by hand —
`File:Enemy Ruin Guard.png` is `truecolour-alpha`, `Software: GIMP 2.10` — and
the `NPC` portraits, which are all `truecolour-alpha`.

**The wiki's name for a body is often not the game's common name.** Four
bodies this survey wanted looked missing until the category listing was read:
Andrius is filed as `Enemy Boreas.png`, Shouki no Kami as
`Enemy Everlasting Lord of Arcane Wisdom.png`, and Guardian of Apep's Oasis as
`Enemy Warden of Oasis Prime.png` (the page `Warden of Oasis Prime` is a
`#REDIRECT [[Guardian of Apep's Oasis]]`). Colons in a body's name are usually
dropped in the file title (`Enemy Kairagi Fiery Might.png`) but not always
(`Enemy Yumkasaurus Warrior Flowing Skyfire.png` exists; the colon form
resolves too). Guessing a title is the failure mode `art_hunt.py`'s own
docstring was written about; §3 says the query shape that avoids it.

## 2. The tables

One per ruled face (R273, `review/ruled/teyvat-nation-mapping-2026-09-14.md`).
The Genshin body is **not chosen here** — it is the body that act's mapping
packet already records for that face, cited per row group; where the packet's
column for that face is empty, the row is marked **palette** and carries the
row's own pan-national top pick from
`docs/current/dossiers/remap/reskin-gallery.md`, which is what R273 §5 says
those rows do ("take the act's palette"). Picking among them is [USER]'s.

`Wiki file title` is given in the form `art/plan.tsv`'s `wiki_title` column
uses — the title **without** the `File:` prefix, which `art_fetch.py` prepends
itself. Every size was read from the API. `Kind` is `archive` (a centre-cropped
in-game Archive capture, opaque) or `cut` (a hand-cut PNG that already carries
alpha).

### 2.1 Act 1, Mondstadt face

Bodies from `tier05/content/act1_pool.yaml`; pairings from
`review/ruled/teyvat-nation-mapping-act1-2026-09-14.md` §2 and
`reskin-gallery.md` rows 20-30.

| Base body | Becomes | Wiki file title | Size | Kind |
|---|---|---|---|---|
| Nibbit | Wooden Shield Hilichurl Guard | `Enemy Wooden Shield Hilichurl Guard.png` | 2160x2160 | archive |
| Inklets x3 | Hilichurl x3 | `Enemy Hilichurl.png` | 1620x2160 | archive |
| Leaf / Twig Slimes | Dendro + Cryo Slime | `Enemy Dendro Slime.png` / `Enemy Cryo Slime.png` | 2560x1440 each | archive |
| Mawler | Rockfond Rifthound *(palette)* | `Enemy Rockfond Rifthound.png` | 2320x2320 | archive |
| Fogmog | Anemo Samachurl *(palette)* | `Enemy Anemo Samachurl.png` | 1350x2400 | archive |
| Sewer Clam | Fatui Hydrogunner Legionnaire *(palette)* | `Enemy Fatui Hydrogunner Legionnaire.png` | 1920x2560 | archive |
| Byrdonis (elite) | Anemo Hilichurl Rogue *(palette)* | `Enemy Anemo Hilichurl Rogue.png` | 2880x2160 | archive |
| Bygone Effigy (elite) | Ruin Guard *(palette)* | `Enemy Ruin Guard.png` | 1053x860 | **cut** |
| Phantasmal Gardener x4 (elite) | four Abyss Mages | `Enemy Hydro/Pyro/Electro/Cryo Abyss Mage.png` | 2160x2160 each | archive |
| Vantom (boss) | **Andrius, Lupus Boreas** | `Enemy Boreas.png` | 2880x2880 | archive |
| Lagavulin Matriarch (boss) | Cryo Regisvine | `Enemy Cryo Regisvine.png` | 2880x2880 | archive |
| Neow (the Ancient) | — | — | — | **gap, §4** |

### 2.2 Act 1, Liyue face

| Base body | Becomes | Wiki file title | Size | Kind |
|---|---|---|---|---|
| Nibbit | Treasure Hoarder Handyman | `Enemy Treasure Hoarder Handyman.png` | 1215x2160 | archive |
| Inklets x3 | Treasure Hoarder Scout x3 | `Enemy Treasure Hoarder Scout.png` | 1215x2160 | archive |
| Leaf / Twig Slimes | Geo + Hydro Slime | `Enemy Geo Slime.png` / `Enemy Hydro Slime.png` | 2560x1440 each | archive |
| Mawler | **Geovishap Hatchling** (Liyue-exclusive) | `Enemy Geovishap Hatchling.png` | 2880x2880 | archive |
| Fogmog | Anemo Samachurl *(palette)* | `Enemy Anemo Samachurl.png` | 1350x2400 | archive |
| Sewer Clam | Large Geo Slime | `Enemy Large Geo Slime.png` | 1920x1440 | archive |
| Byrdonis (elite) | Treasure Hoarder Marksman | `Enemy Treasure Hoarder Marksman.png` | 1215x2160 | archive |
| Bygone Effigy (elite) | Ruin Guard | `Enemy Ruin Guard.png` | 1053x860 | **cut** |
| Phantasmal Gardener x4 (elite) | Hilichurl camp: 2 Fighters + 2 Guards | `Enemy Hilichurl Fighter.png` / `Enemy Rock Shield Hilichurl Guard.png` | 1620x2160 / 2160x2160 | archive |
| Vantom (boss) | Kongamato *(palette; Enkanomiya body)* | `Enemy Kongamato.png` | 2880x2880 | archive |
| Lagavulin Matriarch (boss) | **Primo Geovishap** (Liyue-exclusive) | `Enemy Primo Geovishap.png` | 2880x2880 | archive |
| Neow (the Ancient) | — | — | — | **gap, §4** |

The act-1 packet's own note applies to Byrdonis: "TH Raptor" is not a canon
rank. The wiki has Scout, Handyman, Marksman, Pugilist, Crusher — not Raptor —
so Marksman is the nearest real body and the title above is the one that
resolves.

### 2.3 Act 2, Natlan face

Pairings from `teyvat-nation-mapping-act2-2026-09-14.md` §2.1, Natlan column.

| Base body | Becomes | Wiki file title | Size | Kind |
|---|---|---|---|---|
| Bowlbug pod (Rock + Silk) | Tepetlisaurus Warrior: Rockbreaker Blade + Tepetlisaur Whelps | `Enemy Tepetlisaurus Warrior Rockbreaker Blade.png` / `Enemy Tepetlisaur Whelp.png` | 2880x2880 each | archive |
| Exoskeletons x3 | Tepetlisaur Whelps | `Enemy Tepetlisaur Whelp.png` | 2880x2880 | archive |
| Tunneler | Tepetlisaurus | `Enemy Tepetlisaurus.png` | 2880x2880 | archive |
| Chompers x2 | *(palette)* Koholasaurus | `Enemy Koholasaurus.png` | 2880x2880 | archive |
| Hunter Killer | *(palette)* Yumkasaurus | `Enemy Yumkasaurus.png` | 2880x2880 | archive |
| Louse Progenitor | *(palette)* Tatankasaurus | `Enemy Tatankasaurus.png` | 2880x2880 | archive |
| Mytes x2 | *(palette)* Yumkasaur Whelps | `Enemy Yumkasaur Whelp.png` | 2880x2880 | archive |
| Ovicopter + 3 Tough Eggs | Iktomisaurus + Chicks | `Enemy Iktomisaurus.png` / `Enemy Iktomisaurus Chick.png` | 2880x2880 each | archive |
| The Obscura + Parafright | — no nation-exclusive body (R273 §5) | *(palette)* `Enemy Hydro Samachurl.png` | 1350x2400 | archive |
| Decimillipede (elite) | — no body in any family (R273 §5) | *(palette)* `Enemy Rock Shield Hilichurl Guard.png` | 2160x2160 | archive |
| Entomancer (elite) | Yumkasaurus Warrior: Flowing Skyfire | `Enemy Yumkasaurus Warrior Flowing Skyfire.png` | 2880x2880 | archive |
| Infested Prism (elite) | Rock-Cavernous Wayob Manifestation | `Enemy Rock-Cavernous Wayob Manifestation.png` | 2880x2880 | archive |
| Knowledge Demon (boss) | — Natlan has no candidate; the act's body is Sumeru's | `Enemy Everlasting Lord of Arcane Wisdom.png` | 2880x2880 | archive, **§4** |
| Kaiser Crab (boss) | — Natlan has no candidate; Inazuma's body below | `Enemy Magatsu Mitake Narukami no Mikoto.png` | 3840x2880 | archive, **§4** |
| Ancient — Tezcatara | Chanca, of the Weary Inn | `NPC Chanca.png` | 1080x1080 | **cut** |

### 2.4 Act 2, Inazuma face

| Base body | Becomes | Wiki file title | Size | Kind |
|---|---|---|---|---|
| Bowlbug pod | *(palette)* Nobushi: Kikouban | `Enemy Nobushi - Kikouban.png` | 1305x2320 | archive |
| Exoskeletons x3 | Thundercraven Rifthound Whelp pack | `Enemy Thundercraven Rifthound Whelp.png` | 1650x2200 | archive |
| Tunneler | Thundercraven Rifthound | `Enemy Thundercraven Rifthound.png` | 2320x2320 | archive |
| Chompers x2 | Rockfond Rifthound pair | `Enemy Rockfond Rifthound.png` | 2320x2320 | archive |
| Hunter Killer | Primordial Bathysmal Vishap | `Enemy Primordial Bathysmal Vishap.png` | 2880x2880 | archive |
| Louse Progenitor | *(palette)* Wooden Shieldwall Mitachurl | `Enemy Wooden Shieldwall Mitachurl.png` | 1920x2560 | archive |
| Mytes x2 | *(palette)* Dendro Samachurl x2 | `Enemy Dendro Samachurl.png` | 1800x2400 | archive |
| Ovicopter + Eggs | *(palette)* Fatui Cryo Cicin Mage | `Enemy Fatui Cryo Cicin Mage.png` | 2560x2560 | archive |
| The Obscura + Parafright | *(palette)* Hydro Samachurl | `Enemy Hydro Samachurl.png` | 1350x2400 | archive |
| Decimillipede (elite) | — no body in any family | *(palette)* `Enemy Electro Specter.png` | 1984x1488 | archive |
| Entomancer (elite) | *(palette)* Kairagi: Fiery Might | `Enemy Kairagi Fiery Might.png` | 1920x2560 | archive |
| Infested Prism (elite) | *(palette)* Electro Specter | `Enemy Electro Specter.png` | 1984x1488 | archive |
| Knowledge Demon (boss) | — Inazuma has no candidate | see §4 | — | **gap** |
| Kaiser Crab (boss) | Magatsu Mitake Narukami no Mikoto | `Enemy Magatsu Mitake Narukami no Mikoto.png` | 3840x2880 | archive |
| Ancient — Darv | Hirayama | `NPC Hirayama.png` | 361x938 | **cut, undersized** |

`NPC Hirayama.png` is 361x938 — below the 240x280 target only in width once
the figure is fitted, and the thinnest source in the survey. It will place,
but it is the one row where the source resolution is a real constraint.

### 2.5 Act 3, Fontaine face

Pairings from `teyvat-nation-mapping-act3-2026-09-14.md` §2, Fontaine column.

| Base body | Becomes | Wiki file title | Size | Kind |
|---|---|---|---|---|
| Devoted Sculptor | *(palette)* Geo Samachurl | `Enemy Geo Samachurl.png` | 1800x2400 | archive |
| Scrolls of Biting x3-4 | *(palette)* Hydro Specter drift | `Enemy Hydro Specter.png` | 1984x1488 | archive |
| Living Shield + Turret Operator | Construction Specialist Mek + Area Alert Mek | `Enemy Construction Specialist Mek.png` / `Enemy Area Alert Mek.png` | 2560x2560 / 459x687 | archive |
| Axebot | Assault Specialist Mek | `Enemy Assault Specialist Mek.png` | 1262x859 | archive |
| Punch Construct + 2 Cubex | Suppression Specialist Mek + Overgrown Breacher Primus | `Enemy Suppression Specialist Mek.png` / `Enemy Overgrown Breacher Primus.png` | 990x1052 / 2976x1674 | archive |
| Fabricator + bots | Annihilation Specialist Mek | `Enemy Annihilation Specialist Mek.png` | 649x1105 | archive |
| Frog Knight | *(palette)* Frostarm Lawachurl | `Enemy Frostarm Lawachurl.png` | 2320x2320 | archive |
| Globe Head | *(palette)* Large Electro Slime | `Enemy Large Electro Slime.png` | 1920x1920 | archive |
| Slimed Berserker | *(palette)* oversized Large Hydro Slime | `Enemy Large Hydro Slime.png` | 1920x1440 | archive |
| Knight Gang (elite) | *(palette)* Fatui elite trio, Mirror Maiden anchor | `Enemy Mirror Maiden.png` | 2560x2560 | archive |
| Mecha Knight (elite) | Large Shatterstone Breacher Primus | `Enemy Shatterstone Breacher Primus.png` | 2976x1674 | archive |
| Soul Nexus (elite) | *(palette)* Electro Regisvine | `Enemy Electro Regisvine.png` | 2880x2880 | archive |
| Test Subject (boss) | Iniquitous Baptist | `Enemy Iniquitous Baptist.png` | 2160x2160 | archive |
| Aeonglass (boss) | Prototype: Cal. Breguet | `Enemy Prototype Cal. Breguet.png` | 3040x2280 | archive |
| Ancient — Nonupeipe | Remus | `NPC Remus.webp` | 743x743 | **cut, WebP** |

`NPC Remus.webp` is the survey's only non-PNG. `operations/media.md` §3 already
names the trap — "a WebP served with a `.png` extension is re-encoded in the
scratch copy by `tools/build_pck.ps1`" — but here the extension is honest, so
the row simply needs converting at process time rather than being renamed.

### 2.6 Act 3, Sumeru face

| Base body | Becomes | Wiki file title | Size | Kind |
|---|---|---|---|---|
| Devoted Sculptor | Eremite Scorching Loremaster | `Enemy Eremite Scorching Loremaster.png` | 1800x2400 | archive |
| Scrolls of Biting x3-4 | Eremite Linebreakers | `Enemy Eremite Linebreaker.png` | 1350x2400 | archive |
| Living Shield + Turret Operator | Eremite Ravenbeak Halberdier + Eremite Crossbow | `Enemy Eremite Ravenbeak Halberdier.png` / `Enemy Eremite Crossbow.png` | 815x828 / 647x912 | archive |
| Axebot | — Fontaine-only slot (act-3 packet §6) | — | — | **gap, §4** |
| Punch Construct + 2 Cubex | — no Sumeru body recorded | — | — | **gap, §4** |
| Fabricator + bots | Golden Wolflord + Skulls | `Enemy Golden Wolflord.png` | 3328x2496 | archive |
| Frog Knight | Eremite Stone Enchanter | `Enemy Eremite Stone Enchanter.png` | 1139x984 | archive |
| Globe Head | Eremite Daythunder | `Enemy Eremite Daythunder.png` | 1800x2400 | archive |
| Slimed Berserker | Consecrated Horned Crocodile | `Enemy Consecrated Horned Crocodile.png` | 2880x2880 | archive |
| Knight Gang (elite) | Eremite war-band: Halberdier + Sunfrost + Stone Enchanter | + `Enemy Eremite Sunfrost.png` | 1350x2400 | archive |
| Mecha Knight (elite) | Consecrated Red Vulture | `Enemy Consecrated Red Vulture.png` | 3840x2880 | archive |
| Soul Nexus (elite) | — no Sumeru body recorded | *(Abyss reading)* `Enemy Abyss Lector Violet Lightning.png` | 1830x2440 | **gap, §4** |
| Test Subject (boss) | Guardian of Apep's Oasis | `Enemy Warden of Oasis Prime.png` | 2880x2880 | archive |
| Aeonglass (boss) | Shouki no Kami | `Enemy Everlasting Lord of Arcane Wisdom.png` | 2880x2880 | archive |
| Ancient — Vakuu | Liloupar | `Liloupar.png` | 1145x1432 | archive |
| Ancient — Darv | Katayoun | `NPC Katayoun.png` | 945x1700 | **cut** |
| Ancient — Tanx | — no candidate in any of the six nations | — | — | **gap, §4** |

## 3. Can the card-art pipeline fetch these?

Yes, with one addition. The three parts:

**Discovery works today, with the right query shape.** `tools/art_hunt.py`
searches the `File:` namespace (`srnamespace=6`) or lists a category
(`--category`). Both reach enemy files; the category route is the one to use,
because it enumerates the whole inventory in a single call instead of one
search per body:

```
python tools/art_hunt.py "Enemy Archive Images" --category --limit 600
```

That printed **356 titles** when this page was written, and every body in §2
except one is in it. A per-body search still works for the odd case
(`python tools/art_hunt.py "Rockfond Rifthound"` returns
`File:Enemy Rockfond Rifthound.png` among fifteen hits), but the category
listing is what makes a name mismatch impossible to miss — it is how Boreas,
Warden of Oasis Prime and the Everlasting Lord were found after the obvious
titles came back missing. **Do not invent an `Enemy <common name>.png`
title**; that is the exact failure `art_hunt.py`'s docstring exists to prevent.

**Fetching and placing is one `art/plan.tsv` bill.** `tools/art_fetch.py`
resolves `wiki_title` through `prop=imageinfo` and downloads the original;
`tools/art_process.py` crops it to the row's `w`/`h`. A portrait block is
ordinary rows: `w=240`, `h=280`, `mode=cover`, `focus=top` (Archive captures
centre the body with headroom), `out=ImageGen/images/teyvat/creature_visuals/<body>.png`
— the path `build_pck.ps1`'s Teyvat block already copies from, and the path
the Nibbit placeholder occupies. `--art-root` lets this run from a worktree
against the main checkout's gitignored art, per
`operations/worktrees.md`. So the placement is one art-style bill of roughly
seventy rows, not seventy hand-supplied files.

**The alpha cut is the new step, and it does not exist yet.** §1 showed the
sources are opaque. `art_process.py` has `cover`, `contain`, `cover_autocrop`
and `raw`; `cover_autocrop` trims a *transparent* void, and `contain` pads
"to exact size on transparency" — neither removes a background that is there.
`media.md` §3 requires alpha. So one of three, and it is a [USER] call, not a
derived one: (a) add a background-cut mode to `art_process.py`, which for an
Archive capture is a flat-ish backdrop and mostly tractable; (b) accept opaque
portraits and let the body draw as a framed plate over the arena, which
contradicts `media.md` §3 as written; (c) hand-cut, which is what the wiki
editor who produced `Enemy Ruin Guard.png` did and what 70 bodies cannot
afford. Until that is settled the bill can be drafted but not placed.

One convention question rides along and is genuinely open: the portrait
out-path has **two** candidate producers. `media.md` §1 says portraits land
under `media/raw/portraits/<body>/` → `media/out/portraits/<body>/` with a
`media/PORTRAITS.tsv` row and "one producer per out-path"; the shipped Nibbit
placeholder instead lives under `ImageGen/images/teyvat/creature_visuals/`,
which is `art/plan.tsv`'s territory. `media/PORTRAITS.tsv` does not exist on
disk yet, so nothing is broken — but a seventy-row plan bill would quietly
make `art/plan.tsv` the producer and leave the provenance ledger empty, which
is the opposite of what `media.md` was written for. The cheap reconciliation
is that `plan.tsv` produces and `PORTRAITS.tsv` records, with `origin` holding
the wiki title; that is a process call for [USER].

**APPLIED 2026-09-16 ([USER]'s calls on this section, recorded rather than
re-asked).** (a) The background cut is **option (a)**: `tools/art_process.py`
gained `mode=cut` — a corner-seeded flood fill on colour distance, kept to the
part of that set reachable from the border (so a backdrop-coloured shadow
inside a body is not punched out), then a second pass removing by area the
backdrop POCKETS that first rule traps — keyed regions enclosed by the
silhouette, such as the sky between a Hilichurl Fighter's raised club and its
head — then small foreground islands pruned (so the starfield does not survive
as specks and leave the content trim a no-op), a light feather, and finally
the existing content trim and `cover()`/`contain()` with the row's own focus.
Tolerance and the pocket threshold ride the focus column as
`cut[@tolerance][/fit-focus][:pocket]`, default `cut@48/top:0.004`, the way
`cover_autocrop` carries `cover|contain[@margin]`. One consequence to know
before the veto: the four **Abyss Mages'** shield interiors *do* key at 48, so
their discs draw as a glowing rim with the arena showing through rather than
as a filled plate (rim and mage intact). `cut:0.2` on those four rows restores
the filled disc if that is the wrong read.

**RE-CUT 2026-09-17 ([USER] vetoed the first sheet; three defects, three
fixes).** (1) *Black bodies were being eaten.* A flat 48 RGB from one corner
colour also matches a neutral black, so `frostarm_lawachurl`, the Rifthounds,
the Fatui and the Eremites came back full of holes wherever a hairline of keyed
pixels let the border flood into the body. The matte now keys against a **local
backdrop model** — a robust quadratic surface fit to the border ring, then
inpainted with the backdrop's own local colour so the nebula is followed too —
plus a **blue-chroma gate**: the Archive backdrop is navy (blueness +30 to +50)
and a body's black is neutral (blueness near 0), which is the one axis the two
separate on. Measured on the hard cases, the border ring's own 99th-percentile
distance to the fitted surface is 9–12, so the default tolerance drops from 48
to **30** and the reachability flood now runs on the key eroded by two pixels,
which is what stops a hairline carrying it into a torso. (2) *The Abyss Mages
lost their eyes.* The pocket pass removed enclosed regions by AREA alone, and a
dark face is dark; it now also requires a pocket to MATCH the backdrop model
(mean residual under 55% of the tolerance), so the haze goes and the face
stays. With the tighter key the discs also come back **filled**, which is what
the note above offered — one notch of each disc's upper right is still open,
where the source's bubble interior is the backdrop colour exactly. (3) *Group
captures framed half a second body.* A **figure-selection** step after the
matte keeps the largest alpha component plus anything inside its bbox grown by
8%, drops the rest and names each drop in the run's flags; `;figure=all` keeps
every component (`fatui_cryo_cicin_mage`'s cicins take it). The spec column
grew the two knobs as `;key=value` rather than a fifth punctuation mark:
`cut[@tolerance][/fit-focus][:pocket][;chroma=N][;figure=main|all]`, default
`cut@30/top:0.004;chroma=12;figure=main`. Still uncuttable and flagged on the
sheet: `remus`, `katayoun` and `large_hydro_slime`. **Follow-up the same day:**
`dendro_slime`'s second slime survived that pass because it is *joined* to the
subject through the overlapping leaves — one alpha component, so there was
nothing for figure selection to select between — so the spec gained
`;split=N`, which opens the matte (erode N, dilate N) before the figure is
chosen, parting two bodies bridged by anything thinner than 2N+1 while every
thick part survives. It is **off by default and on for one row**
(`dendro_slime`, at `split=16`): a scan of all 81 at that N showed the same
rule would cut `hilichurl_fighter`'s raised club and
`rock_shield_hilichurl_guard`'s shield haft, which are thin bridges to real
features, and no other row holds two bodies in one component
(`iktomisaurus_chick` holds two whole chicks, which is what that row dresses).
(b) **The plan produces and the ledger records:** 81 rows in `art/plan.tsv`
write `ImageGen/images/teyvat/creature_visuals/<body>.png` — the directory
`tools/build_pck.ps1`'s Teyvat block copies to `res://teyvat/creature_visuals/`
— and `media/PORTRAITS.tsv` carries one row per body recording it. In those
rows `out` names that produced path (not a `media/out/` path: the plan is the
producer, and naming it is what keeps "one producer per out-path" true), `raw`
names **the `art/raw/` file the fetch actually wrote**, `title` is the bare
wiki file title and `origin` is its
`https://genshin-impact.fandom.com/wiki/File:…` page. `operations/media.md` §1
carries the same sentence. (c) The Knowledge Demon / Wanderer-model collision is
**accepted**, so `Enemy Everlasting Lord of Arcane Wisdom.png` is in the bill
(it dresses the Aeonglass boss on the Sumeru face too). **Tanx** is out — it
waits on a reflavouring, and §4 already records that no image search can close
it. **Coral Defenders** is out: it has no Archive still at all, only a mechanics
screenshot, and it is not either ruled act-2 face's pick. The act-3 Sumeru Soul
Nexus **Abyss Lector** reading is out with them, because R273 §3 reserves the
Abyss for act 4.

Two of the 81 are **fetched but not cut**, and `art_process` said so itself
(`cut@48 removed almost nothing`): `NPC Remus.webp` and `NPC Katayoun.png` are
in-world screenshots rather than Archive captures — a statue in a ruin, an NPC
in the Akademiya — so masonry, ivy, bookshelves and planters are all
foreground and no corner-seeded matte can separate them. Both are on the
contact sheet under that warning; each needs a hand cut or a different source,
and neither is a sourcing gap in §4's sense.

## 4. The gaps

**Image gaps: one.** After the name corrections in §1, every Genshin body
named in §2 has a public still of at least 459x687, and all but four are over
1000px on the short side. The single body with no Archive image is **Coral
Defenders** — `reskin-gallery.md`'s top pick for Kaiser Crab, absent from
`Category:Enemy Archive Images`, and served only by
`File:Coral Defenders Weak Point.png` (1296x1080), a mechanics screenshot. It
is not one of the two ruled act-2 faces' picks, so it costs nothing today.

**Mapping gaps — the two the mapping itself carried:**

- **Tanx**, the act-3 Ancient, has no candidate in any of the six nations.
  Every drafted variant is Liyue (Azhdaha), Mondstadt (Andrius) or a
  pan-national hilichurl that is itself register-blocked
  (`teyvat-nation-mapping-act3-2026-09-14.md` §6, citing
  `ancients-gallery.md:573`). No image search can close this: there is no body
  to look for. Recorded and parked by R273 §5.
- **Knowledge Demon as Shouki no Kami.** The image is fine —
  `Enemy Everlasting Lord of Arcane Wisdom.png`, 2880x2880, and the entity name
  literally is "Everlasting Lord of Arcane Wisdom", which is why the act-2
  packet called the pairing literal. The problem was never sourcing: the model
  is the Wanderer's, a playable roster character, which R273 §5 records as "a
  curation call, not a mechanics one". [USER] accepted it today, so this row
  is closed and its portrait is available at full size.

**Other rows with no body to source, all pre-existing and none new here:**

| Row | Why there is nothing to fetch |
|---|---|
| Neow (act-1 Ancient), both faces | All three kept candidates (Orobashi, Elynas, Egeria) are Inazuma or Fontaine — zero Mondstadt or Liyue fits (`…-act1-…` §2, `ancients-gallery.md:104-158`) |
| Decimillipede (act-2 elite), both faces | Reattach has no analogue in any of the 16 surveyed families; sole claim is a self-declared stretch (`reskin-gallery.md` flags §1) |
| The Obscura + Parafright (act 2), both faces | Every candidate is pan-national; the Wail discriminator has no nation-exclusive body (R273 §5) |
| Knowledge Demon under the **Natlan** face | Natlan scores zero on this boss; the face borrows Sumeru's body |
| Kaiser Crab under the **Natlan** face | Natlan scores zero; Inazuma's Magatsu is the only in-pair reading |
| Knowledge Demon under the **Inazuma** face | Inazuma scores zero on this boss |
| Axebot under the **Sumeru** face | The one enemy row where the pair choice has no second option — only Fontaine's Assault Specialist Mek clears the bar (act-3 packet §6) |
| Punch Construct + 2 Cubex under the **Sumeru** face | No Sumeru body recorded for either half; gang coherence forbids mixing (act-3 packet §6) |
| Soul Nexus under the **Sumeru** face | Sumeru scores zero; the strong reading is the Abyss Lector, and the Abyss is reserved for act 4 (R273 §3) |
| Queen + Torch Head Amalgam | Ships dropped; "zero claims across all 16 families" (`reskin-gallery.md` flags §1) |

Every one of these is a mapping question for [USER], not a sourcing question.
Where the row is a boss a face cannot cover, the cheapest answer is the one
the tables already imply: the sibling face's body dresses both, since both
faces return the same encounter object anyway
(`teyvat-nation-mapping-2026-09-14.md` §1).

**Not a gap, worth naming: two undersized sources.** `NPC Hirayama.png`
(361x938) and `Enemy Area Alert Mek.png` (459x687) are the two smallest
sources in the survey. Both exceed 240x280, so both place, but neither has
headroom for a re-crop.

## 5. The terms

The images are HoYoverse's, and the wiki hosts them under a fair-use claim,
not a free licence. Every enemy file page carries the same two-line wikitext —
`{{File|Enemy Archive Images}}` and `{{Fairuse}}` — and
`Template:Fairuse` renders as: "This file is copyrighted to HoYoverse… an
official media, game graphic, or game audio of *Genshin Impact*, an RPG game
copyrighted (©) by HoYoverse. Though this media is subject to copyright, it is
believed that its use qualifies as fair use under U.S. fair use laws when used
on *Genshin Impact* Wiki, hosted on servers in the United States by Fandom,
Inc. This file's usage should also comply with HoYoverse's intellectual
property guidelines" — linking
`https://www.hoyolab.com/article/143107`. The wiki's own copyright page says
only the **text** is CC-BY-SA 3.0 and asks that copyrighted content not be
added "without permission from the copyright holder or without the right to do
so under fair use"
(`https://genshin-impact.fandom.com/wiki/Genshin_Impact_Wiki:Copyrights`;
template at `https://genshin-impact.fandom.com/wiki/Template:Fairuse`). In
practice that means exactly what `media.md` §2 already legislates: every
portrait row's `licence` column is **`PLACEHOLDER-COPYRIGHTED`**, the
pre-public pass is `grep PLACEHOLDER-COPYRIGHTED media/*.tsv`, and a non-empty
result blocks a public build. The wiki's fair-use claim covers the wiki's use,
not ours, so nothing in this survey moves the private build any closer to
being publishable — it is Tier F, the same as every card-art row in
`art/SOURCES.tsv`.

One practical note for whoever writes the fetch: `genshin-impact.fandom.com`
returns **HTTP 402** to plain page fetches — the same block the 2026-08-13
canon check hit (`reskin-gallery.md` flags §3, "Fandom pages exist for all six
but returned HTTP 402 to the checking agent"). The `api.php` endpoint that
`art_hunt.py` and `art_fetch.py` use answers normally, and the image host is
`static.wikia.nocookie.net/gensin-impact/` — that spelling, with the missing
`h`, is the wiki's internal id and is what `art/SOURCES.tsv` already records.
