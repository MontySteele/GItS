# S17 — art coverage and provenance, family: **companions**

> **This document decides nothing.** It is a draft ledger and a list of
> discrepancies. Every "rights tier" below is a **category read off an existing
> file**, never a rights verdict. Every source pick, taste call, batch schedule
> and scope call remains [USER]'s. Nothing here was generated, rendered,
> re-picked or deployed — this stream ran read-only, and no art tool was run.

**Date:** 2026-08-27 (re-run of the output deferred by the 2026-08-26 usage
limit — `review/dispatch3/BLOCKERS.md` §3 row 1).
**Family scope:** the 51 companion cards declared in
`docs/mondstadt-companions.yaml`, `docs/fontaine-companions.yaml` and
`docs/inazuma-companions.yaml`, plus the companion-specific non-card surfaces:
the 7 companion status/summon badges, the companion-mechanic badges, the powers
a companion card applies that have no badge at all, and the turn-end docket row
Arlecchino owns.
**Live baseline cited throughout:** `review/dispatch3/s17-art/baseline-run-2026-08-26.txt`
(`art_coverage.py` exit 0, `art_lint.py` exit 0, run read-only on the
art-bearing primary at `main 223a4ff`). **The art tools were not re-run.**

---

## 0. Read record and what moved since the overnight run

| item | value |
|---|---|
| Worktree | `C:\Users\Monty\Documents\GitHub\GItS-s17`, branch `dispatch3-s17-rerun`, cut from `main 3eca8d3` |
| Ledgers read | `art/plan.tsv` (1259 lines) and `art/SOURCES.tsv` (873 lines) in this worktree — verified **byte-identical** to the primary's copies by `diff`, so the `file:line` citations below are valid against both |
| Rendered art, raw sources, candidates, contact sheets, `picks.tsv`, the pck contract, the deployed mod, the game logs | read **read-only by absolute path** in the primary checkout `C:\Users\Monty\Documents\GitHub\GItS` and under `C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\mods\klee\` and `C:\Users\Monty\AppData\Roaming\SlayTheSpire2\logs\`. Nothing was linked, copied, or written there, and no git command was run there. |
| Read window | 2026-08-27, daytime |

**Three things changed under this family since the overnight files were
written, and all three change what a reader should believe:**

1. **`art/candidates/` was re-materialised on the morning of 2026-08-27** — 297
   directories, and **all 27 contact sheets in `art/` resolve again**. The
   `BLOCKERS.md` §1.1 data-loss finding ("25 of 27 contact sheets are dead, the
   R212(1) veto route is closed") is **CLOSED for this family and reported as
   closed here rather than repeated**. Concretely for companions:
   `art/contact_sheet_companions.html` (38,138 bytes, written 2026-08-13 01:31)
   carries **138 `src` references and every one of them resolves on disk** — 46
   ids × 3 ranks, exactly the shortlist population of §2a. I verified all 138
   candidate PNGs exist.
2. **Lane B's ledger tooling merged** (`tools/art_ledger.py`,
   `review/dispatch3/tooling-laneb-handoff.md`). Reconciliation against it is
   the joined file's job, not this one's; one companion-specific gap in its
   reader set is recorded at §7 F5 because only this family exposes it.
3. **The register minted `EB-153`, `EB-162` and `EB-163` on 2026-08-27**
   (`docs/current/BACKLOG.md:85`, `:117`, `:118`). Findings below that feed them
   cite them; **this stream mints no id.**

---

## 1. Scope boundary — what is deliberately NOT here

| Excluded | Why | Whose row |
|---|---|---|
| The three personal sheets (Klee 79, Furina 84+1 token, Kokomi 76) | separate owner families | Klee / Furina / Kokomi owners |
| The whole `klee/`, `furina/`, `kokomi/` and `shared/` UI, model, rig, transition and VFX surface | not companion-specific | icons/UI/models/VFX owner |
| The 6 elemental aura badges and `power_frozen` | shared elemental vocabulary; applied by companion cards *and* by everything else | icons/UI/models/VFX owner (`s17-icons-ui-models-vfx.md` §2a) |
| `power_friendly_visit` / `power_study_buddy` | **boundary row, stated not claimed.** The two *badges* are Klee cards' art and are already billed by the Klee family as the two AS2-E2 "weak marks" (`s17-klee.md` §4.1). The two *powers* they dress — `CompanionCostThisTurnPower`, `ReplayNextCompanionPower` (`klee-mod/KleeCode/Powers/CompanionPowers.cs:151`, `:206`) — are companion mechanics. One surface, two families; **the Klee file owns the pick and this file does not duplicate it.** | Klee owner |
| The 3 shipped-in-C#-with-no-sheet-row card keys (`confiscated`, `spotlight_center_stage`, `spotlight_guest_cast`) | Klee and Furina rows | Klee / Furina owners |

**Card art is not total visual coverage.** `art_coverage.py` counts card-sized
outputs only. Beyond the 51 card faces this family owns **7 badges it can see
nothing of**, and **5 powers with no badge at all** — and it can see none of
the twelve.

---

## 2. Headline counts (from the live baseline, and from the files on disk)

| Surface class | Expected | Present on disk | Missing | Counted by `art_coverage`? |
|---|---:|---:|---:|---|
| Card portraits — Companions (Inazuma) | 15 | 15 | 0 | yes |
| Card portraits — Companions (Mondstadt/shared) | 17 | 17 | 0 | yes |
| Card portraits — Companions (Fontaine) | 19 | 19 | 0 | yes |
| **Card portraits, total** | **51** | **51** | **0** | yes |
| Companion status/summon badges (`ImageGen/images/powers/`) | 7 | 7 | 0 | **no** |
| Companion-applied powers with **no badge mapping at all** | 5 | **0** | **5** | **no** |
| Turn-end docket row with a title and no sprite (Arlecchino) | 1 | 0 | UNKNOWN whether owed | **no** |
| Companion `vfx/` scenes | 0 | 0 | — | **no** |
| Stale companion asset on a `companions/` out-path | — | **0** | — | — |

Roster context from the same run: **294 card-sized outputs expected, 270
covered, 24 missing** (`baseline-run-2026-08-26.txt:98-100`). **Companions
contribute zero of the 24.** This is the only family in S17 with a complete
card bill.

Three cross-checks, all independent of the baseline:

- `ImageGen\images\cards\companions\` holds **51 PNGs**, and the id sets match
  the three YAML sheets exactly in both directions — no rendered file without a
  sheet row, no sheet row without a rendered file. All 51 are **500×380 RGBA**,
  the size `docs/art-asset-manifest.md` requires of a card.
- The **deployed** flat directory
  `…\Slay the Spire 2\mods\klee\images\cards\` holds 272 PNGs and **all 51
  companion ids are present** (272 = 270 covered + the 2 `[known]` STALE
  Furina/Kokomi files, which are not this family's).
- `art_lint`'s live output names **exactly two companion rows in its entire
  run**, both L6 clip warnings and neither a failure:
  `nicole_celestial_gift` (~58% of source height trimmed) and
  `neuvillette_ancient_sea_authority` (~62%)
  (`baseline-run-2026-08-26.txt:103`, `:118`). No companion row appears under
  L1, L7, L8, L9, L11 or L12.

---

## 3. The draft ledger

Columns are the ones S17 asks for. `packed path` matters less here than
anywhere else in S17, because this family ships entirely by **Route A**:

- **Route A — loose PNG, no pck.** `klee-mod/build/deploy.ps1:123-128` lists
  `ImageGen\images\cards\companions` as one of four source directories all
  copied into ONE FLAT destination `<mod>\images\cards\`, and
  `RosterArt.CardPortrait` reads `images/cards/<sheet_id>.png` at runtime.
  Card ids are globally unique (`tools/lint_unique_names.py` gates it,
  `deploy.ps1:112-115`) so the flattening is safe — **and I confirmed it: no
  companion id collides with any Klee, Furina or Kokomi basename in the
  deployed directory.**
- **Route B — `res://` inside `klee.pck`.** Used by this family for the 7
  badges only, and — see §5 — under **Klee's** namespace, not a companion one.

### 3a. Card portraits — 51 expected, 51 present, 0 missing

Every row below is: **rendered, staged, deployed, provenance-recorded, and
lint-clean.** The table gives the id, its sheet row, its plan row, the effective
(rank-1) source, the crop, the art register, and where its provenance lives.
Rights tier is `private-placeholder` for all 51 (§4).

Reading key: `prov = candidates` means `art/SOURCES.tsv` carries the row against
`art/candidates/<id>/r<n>.png` (the shortlist shape, written by
`tools/art_fetch.py:183-216`); `prov = out-path` means the row is against the
rendered file itself (the `auto` shape).

#### Mondstadt / shared — 17

| id | ★ / rarity | pick | effective source | crop | register | prov | sheet | plan |
|---|---|---|---|---|---|---|---|---|
| `albedo_solar_isotoma` | 5 rare | shortlist | Albedo Character Card.png | cover@y0.16 | tcg | candidates r1–3 | mondstadt:83 | plan:605 |
| `barbara_melody` | 4 common | **auto** | Glorious Season Equipment Card.png | cover@center | tcg | out-path | mondstadt:30 | plan:223 |
| `barbara_shining_idol` | 4 uncommon | shortlist | Barbara Character Card.png | cover@y0.16 | tcg | candidates r1–3 | mondstadt:36 | plan:608 |
| `bennett_fantastic_voyage` | 4 uncommon | shortlist | Bennett Character Card.png | cover@y0.16 | tcg | candidates r1–3 | mondstadt:71 | plan:611 |
| `bennett_passion` | 4 common | **auto** | Grand Expectation Equipment Card.png | cover@center | tcg | out-path | mondstadt:69 | plan:222 |
| `dahlia_favonian_favor` | 4 uncommon | shortlist | Dahlia Wish.png | cover@y0.16 | splash | candidates r1–3 | mondstadt:22 | plan:629 |
| `dahlia_sacramental_shower` | 4 common | shortlist | Dahlia Character Card.png | cover@top | tcg | candidates r1–3 | mondstadt:20 | plan:216 |
| `diona_icy_paws` | 4 common | shortlist | Diona Character Card.png | cover@y0.16 | tcg | candidates r1–3 | mondstadt:79 | plan:614 |
| `durin_witchs_flame` | 5 rare | shortlist | Durin.png | cover@y0.16 | splash | candidates r1–3 | mondstadt:85 | plan:617 |
| `fischl_nightrider` | 4 common | **auto** | Stellar Predator Equipment Card.png | cover@center | tcg | out-path | mondstadt:24 | plan:219 |
| `fischl_oz` | 4 uncommon | shortlist | Fischl Character Card.png | cover@y0.16 | tcg | candidates r1–3 | mondstadt:26 | plan:620 |
| `kaeya_frostgnaw` | 4 common | **auto** | Cold-Blooded Strike Equipment Card.png | cover@center | tcg | out-path | mondstadt:77 | plan:220 |
| `nicole_celestial_gift` | 5 rare | shortlist | Character Nicole Game.png | cover@y0.16 | splash | candidates r1–3 | mondstadt:87 | plan:623 |
| `prune_witch_hunt` | 4 uncommon | shortlist | Prune Wish.png | cover@top | splash | candidates r1–3 | mondstadt:102 | plan:224 |
| `sucrose_astable` | 4 uncommon | shortlist | Sucrose Character Card.png | cover@y0.16 | tcg | candidates r1–3 | mondstadt:48 | plan:626 |
| `sucrose_catalyst_conversion` | 4 uncommon | shortlist | Sucrose Card.png | cover@y0.30 | tcg | candidates r1–3 | mondstadt:58 | plan:997 |
| `sucrose_gust` | 4 uncommon | **auto** | Chaotic Entropy Equipment Card.png | cover@center | tcg | out-path | mondstadt:41 | plan:221 |

#### Fontaine — 19

| id | ★ / rarity | pick | effective source | crop | register | prov | sheet | plan |
|---|---|---|---|---|---|---|---|---|
| `arlecchino_masque_red_death` | 5 rare | shortlist | Character Arlecchino Full Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | fontaine:154 | plan:1029 |
| `charlotte_enduring_frosthelm` | 4 common | shortlist | Charlotte Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | fontaine:41 | plan:563 |
| `charlotte_freezing_point` | 4 common | shortlist | Charlotte Character Card.png | cover@y0.16 | tcg | candidates r1–3 | fontaine:38 | plan:560 |
| `charlotte_snappy_silhouette` | 4 uncommon | shortlist | Character Charlotte Hurlock Variations Full Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | fontaine:52 | plan:566 |
| `chevreuse_bursting_grenades` | 4 uncommon | shortlist | Character Chevreuse Full Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | fontaine:18 | plan:575 |
| `chevreuse_interdiction_fire` | 4 common | shortlist | Chevreuse Character Card.png | cover@y0.16 | tcg | candidates r1–3 | fontaine:11 | plan:569 |
| `chevreuse_vanguards_valor` | 4 common | shortlist | Chevreuse Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | fontaine:14 | plan:572 |
| `clorinde_impale_the_night` | 5 rare | shortlist | Clorinde Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | fontaine:112 | plan:1019 |
| `freminet_pers_deploy` | 4 common | shortlist | Freminet Character Card.png | cover@y0.16 | tcg | candidates r1–3 | fontaine:57 | plan:578 |
| `freminet_pressurized_floe` | 4 common | shortlist | Freminet Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | fontaine:62 | plan:581 |
| `freminet_shattering_pressure` | 4 uncommon | shortlist | Character Freminet Full Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | fontaine:67 | plan:584 |
| `guest_neuvillette_droplets` | 5 common | shortlist | Neuvillette Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | fontaine:215 | plan:590 |
| `guest_neuvillette_judgment` | 5 uncommon | shortlist | Character Neuvillette Full Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | fontaine:219 | plan:593 |
| `guest_neuvillette_tears` | 5 common | shortlist | Neuvillette Character Card.png | cover@y0.16 | tcg | candidates r1–3 | fontaine:212 | plan:587 |
| `lynette_astonishing_shift` | 4 uncommon | shortlist | Character Lynette Full Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | fontaine:32 | plan:602 |
| `lynette_box_trick` | 4 common | shortlist | Lynette Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | fontaine:26 | plan:599 |
| `lynette_enigmatic_feint` | 4 common | shortlist | Lynette Character Card.png | cover@y0.16 | tcg | candidates r1–3 | fontaine:23 | plan:596 |
| `navia_cannon_fire_support` | 5 rare | shortlist | Navia Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | fontaine:98 | plan:1016 |
| `neuvillette_ancient_sea_authority` | 5 rare | shortlist | Neuvillette Card.png | cover@y0.28 | splash | candidates r1–3 | fontaine:137 | plan:1026 |

#### Inazuma — 15

| id | ★ / rarity | pick | effective source | crop | register | prov | sheet | plan |
|---|---|---|---|---|---|---|---|---|
| `gorou_heart_of_the_clan` | 4 uncommon | shortlist | Gorou Introduction Card.png | cover_autocrop@0.06 | splash | candidates r1–3 | inazuma:39 | plan:755 |
| `gorou_inuzaka_charge` | 4 common | shortlist | Gorou Character Card.png | cover@y0.16 | tcg | candidates r1–3 | inazuma:29 | plan:749 |
| `gorou_war_banner` | 4 common | shortlist | Gorou Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | inazuma:36 | plan:752 |
| `itto_superlative_superstrength` | 5 rare | shortlist | Arataki Itto Character Card.png | cover@y0.16 | tcg | candidates r1–3 | inazuma:89 | plan:788 |
| `raiden_musou_no_hitotachi` | 5 rare | shortlist | Character Raiden Shogun Full Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | inazuma:99 | plan:791 |
| `sara_crowfeather_cover` | 4 common | shortlist | Kujou Sara Character Card.png | cover@y0.16 | tcg | candidates r1–3 | inazuma:79 | plan:776 |
| `sara_tengu_stormcall` | 4 uncommon | shortlist | Kujou Sara Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | inazuma:82 | plan:779 |
| `sayu_daruma_gift` | 4 common | shortlist | Sayu Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | inazuma:50 | plan:761 |
| `sayu_naptime` | 4 uncommon | shortlist | Character Sayu Full Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | inazuma:54 | plan:764 |
| `sayu_yoohoo_windwheel` | 4 common | shortlist | Sayu Character Card.png | cover@y0.16 | tcg | candidates r1–3 | inazuma:47 | plan:758 |
| `shinobu_grass_ring_bond` | 4 common | shortlist | Kuki Shinobu Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | inazuma:63 | plan:770 |
| `shinobu_sanctifying_ring` | 4 common | shortlist | Kuki Shinobu Character Card.png | cover@y0.16 | tcg | candidates r1–3 | inazuma:59 | plan:767 |
| `shinobu_thundergrust` | 4 uncommon | shortlist | Character Kuki Shinobu Full Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | inazuma:66 | plan:773 |
| `thoma_blazing_barrier` | 4 common | shortlist | Thoma Character Card.png | cover@y0.16 | tcg | candidates r1–3 | inazuma:71 | plan:782 |
| `thoma_crimson_ooyoroi` | 4 uncommon | shortlist | Thoma Wish.png | cover_autocrop@0.06 | splash | candidates r1–3 | inazuma:74 | plan:785 |

**Fallback for all 51 (if a file ever went missing):** `RosterArt.CardPortrait`
logs `No card art at <path>` and returns null (`klee-mod/KleeCode/KleeArt.cs:76-79`);
nothing fails and the base-game BETA placeholder renders. **No companion row is
exercising it today.**

**The regularity is not an accident and is worth naming.** Two crop grammars
cover 49 of 51 rows: `cover@y0.16` on the 22 rows sourced from a Genshin TCG
*Character Card* plate (register `tcg`), and `cover_autocrop@0.06` on the 22
rows sourced from a *Wish* or *Full Wish* splash (register `splash`). The
remaining rows are 5 `auto` TCG *equipment* cards at `cover@center` and two
hand-set anchors (`cover@top` ×2, `cover@y0.28`, `cover@y0.30`). One id, one
Genshin character plate, one crop rule.

### 3b. Stale card assets on a `companions/` out-path — **NONE**

`baseline-run-2026-08-26.txt:92-95` lists exactly two STALE files
(`rising_tide.png`, `swift_currents.png`) and both are Furina/Kokomi. I
confirmed independently that every file in `ImageGen\images\cards\companions\`
maps to a live sheet row. **NON-FINDING, and the only family in S17 with a
clean stale register.**

### 3c. Companion status and summon badges — 7 present, 7 expected

All seven are 256×256, `contain@center`, register `icon`, out-path
`ImageGen/images/powers/<name>.png`, packed as **`res://klee/powers/<name>.png`**
(`klee-mod/assets/klee.pck.contract.txt:76,79,82,83,85,86,92` in the primary —
the file is gitignored and machine-local).

| out file | power it dresses | applied by | wired at | rank-1 source | pick | prov | rights tier |
|---|---|---|---|---|---|---|---|
| `oz_summon.png` | `OzSummonPower` (`CompanionPowers.cs:259`) | `fischl_oz` | `KleePowerIcons.cs:48` | Oz Summon.png | shortlist (3 ranks) | candidates r1–3 | private-placeholder |
| `solar_isotoma.png` | `SolarIsotomaPower` (`:370`) | `albedo_solar_isotoma` | `:49` | Talent Abiogenesis Solar Isotoma.png | shortlist (2 ranks) | candidates r1–2 | private-placeholder |
| `witchs_flame.png` | `WitchsFlamePower` (`:307`) | `durin_witchs_flame` | `:50` | Durin Item.png | shortlist (2 ranks) | candidates r1–2 | private-placeholder |
| `celestial_gift.png` | `CelestialGiftPower` (`:413`) | `nicole_celestial_gift` | `:51` | Nicole Icon.png | shortlist (2 ranks) | candidates r1–2 | private-placeholder |
| `fantastic_voyage.png` | `AttackUpThisTurnPower` (`:454`) | `bennett_fantastic_voyage` | `:57` | Talent Fantastic Voyage.png | **auto** | out-path | private-placeholder |
| `passion_overload.png` | `NextAttackUpPower` (`:493`) | `bennett_passion` | `:58` | Talent Passion Overload.png | **auto** | out-path | private-placeholder |
| `shattering_pressure.png` | `ShatterBonusPower` (`:563`) | `freminet_shattering_pressure` | `:59` | Talent Pressurized Floe 3.png | shortlist (2 ranks) | candidates r1–2 | private-placeholder |

Plan rows: `art/plan.tsv:686-694` (the four summon/aura badges),
`:716-719` (the three from the 2026-07-24 sweep's follow-up).

**Fallback:** `KleePowerIcons.PathFor` ends in `_ => null`
(`klee-mod/KleeCode/Powers/KleePowerIcons.cs:150`), the Harmony prefix returns
`true` (`:171-176`), and the base game's own placeholder draws — *never* a
sibling's sigil. All seven files exist, so none is exercising it.

**Ownership oddity, recorded not judged.** Seven companion badges ship under
**Klee's** `res://klee/powers/` namespace and out of the shared
`ImageGen/images/powers/` directory, while Furina's and Kokomi's badges get
`furina/powers/` and `kokomi/powers/`. That is consistent with the companion
pool "shipping with Klee" (`docs/current/STATE.md:83`) and it breaks nothing —
but it means **no path in the repo says "companion"**, which is exactly why a
family-scoped tool cannot find them. See §7 F5.

### 3d. Companion-applied powers with **no badge mapping at all** — 5

This is the substantive non-card finding of this stream.

Five `PowerModel` subclasses that a companion card applies have **no case in
`KleePowerIcons.PathFor` and no `IconExempt` entry**
(`KleePowerIcons.cs:157-162` holds exactly three exemptions, none of them
these). They fall to `_ => null` and draw the base-game placeholder.

| power | class site | applied by | element of the fix |
|---|---|---|---|
| `CannonFireSupportPower` | `Powers/FontainePowers.cs:76` | `navia_cannon_fire_support` (`Cards/Generated/NaviaCannonFireSupport.cs:70`) | no badge, no plan row, no source |
| `NightVigilPower` | `Powers/FontainePowers.cs:141` | `clorinde_impale_the_night` (`Cards/Generated/ClorindeImpaleTheNight.cs:88`) | ″ |
| `AncientSeaAuthorityPower` | `Powers/FontainePowers.cs:177` | `neuvillette_ancient_sea_authority` (`Cards/Generated/NeuvilletteAncientSeaAuthority.cs:70`) | ″ |
| `MasqueRedDeathPower` | `Powers/FontainePowers.cs:223` | `arlecchino_masque_red_death` (`Cards/Generated/ArlecchinoMasqueRedDeath.cs:70`) | ″ |
| `MetallicizePower` | `Powers/CompanionPowers.cs:595` | `gorou_heart_of_the_clan` (`Cards/Generated/GorouHeartOfTheClan.cs:74`) **and two Kokomi cards** (`Cards/Kokomi/Generated/PearlCurrent.cs:62`, `TightenTheCords.cs:65`) | ″ |

**These five are already registered as `EB-153`** (`docs/current/BACKLOG.md:85`),
which lists all seven unmapped powers together. Two corrections this family's
scope supplies, offered as hygiene facts, not as a re-scope:

- **Five of the seven are companion-family, not four.** `s17-kokomi.md` §2c
  attributes them "four Fontaine companions, one Furina salon, two Klee";
  `MetallicizePower` is in `Powers/CompanionPowers.cs:595`, not in a Klee file,
  and its **first** applier is a Gorou card. The correct split is **5 companion
  / 1 Klee (`ExplosivesWorkshopPower`) / 1 Furina (`SalonCapUpPower`)**.
  `s17-icons-ui-models-vfx.md` §2d already names the source files correctly;
  only the one-line summary in the Kokomi file counts them wrong.
- **`MetallicizePower` is the only one of the seven with live runtime evidence,
  and the log names it.** `…\SlayTheSpire2\logs\godot.log` (rolling, last
  written 2026-08-26 22:50, `pck build id: 20260826-204650+98fb3a0`) carries
  **eight** lines of
  `[WARN] AtlasResourceLoader: Missing sprite 'metallicize_power' in power_atlas (requested: res://images/atlases/power_atlas.sprites/metallicize_power.tres)`.
  The other four produce no log line at all, because the base game only warns
  for the id-derived atlas slug it happens to look for. So the *quietest* four
  of the five are the ones no instrument in this repo or the game can see.

**And a third fact that belongs to `EB-153` rather than to any family:
the boot check that exists to catch exactly this did not catch it.**
`KleeSelfCheck.CheckPowerIcons` (`Diagnostics/KleeSelfCheck.cs:407-440`) walks
every non-abstract `PowerModel` in the assembly and calls `Fail("R13", …)` when
`PathFor` returns null. Yet the same session's log reads
`[klee] SELFCHECK passed (19 rule families across 3 characters and the
assembly's powers)`. Both cannot be describing the same set of powers. The one
escape hatch in the code is the `catch (Exception) { continue; }` at `:423-429`
— reflection cannot construct the type, so its icon is never asked for — and
none of the five declares an explicit constructor. **Why R13 is silent is
UNKNOWN from source alone** and I did not launch the game to find out; it needs
either the base `PowerModel` decompile (`game_ref/` on this machine holds only
YAML/JSON, no C#) or one instrumented boot. **This is the load-bearing part:
`EB-153`'s acceptance is "the lint bites on both shapes", and until R13's
silence is explained, nobody knows whether R13 is the lint or is itself the
hole.**

### 3e. The Arlecchino turn-end docket row — a title with no picture

`Powers/TurnEndAttribution.cs:145-172` gives `MasqueRedDeathPower` the **first**
row of the end-of-turn docket (`Key = "masque"`), with a title key, a preview
and a body. `KurageSprite` (`:129`) is the **only** sprite constant in that
file, so Arlecchino's row renders as a number and text with no picture, while
Kokomi's Bake-Kurage row gets a sprite. The file's own comment says an absent
sprite "produces a number with no picture, which is the degradation we want"
(`:125-127`) — so this is **not** a defect. Whether the docket *wants* a second
sprite is a design question and is stated only as a question (§8 Q3).

### 3f. Companion VFX — **zero, and nothing asks for one**

The pck contract carries exactly three `vfx/` scenes: `furina/vfx/spotlight_shine.tscn`,
`klee/vfx/bomb_lob.tscn`, `klee/vfx/dodoco_pop.tscn`. No companion C# references
a `vfx/` path. **NON-FINDING** — nothing is broken. Whether Oz, the Solar
Isotoma or the Witch's Flame *want* a field effect is design, and it is the same
shape as the open Kokomi question (`s17-kokomi.md` §7 Q4); this file does not
re-ask it.

---

## 4. Rights tier — as a category only

| category | count | basis |
|---|---:|---|
| `private-placeholder` | **58 of 58** — 51 card faces + 7 badges | **every** `art/SOURCES.tsv` row touching a companion output carries `tier = F` (I checked all 51 card ids and all 7 badge ids; the tier column is uniform). `docs/current/OPERATIONS.md:296` states Tier F art never ships publicly and never enters the repo. |
| `public-safe` | **0** | no companion output is produced by a generator declaring Tier O; there is no procedural companion asset. Contrast Kokomi's one (`ui/transition_wipe.png`). |
| `UNKNOWN` | **0** | there is no companion asset id without a `SOURCES.tsv` row at some rank. |

**No rights verdict is offered or implied.** The category is transcribed from a
column that already exists. That this family is 100% one category is a *fact
about the ledger*, not a statement about what may ship.

---

## 5. **Provenance — 51 of 51 card ids and 7 of 7 badges have a `SOURCES.tsv` row**

`art/SOURCES.tsv` is written **only** by `tools/art_fetch.py:183-216` and is the
only *tracked* record of the URL a shipped pixel came from (`art/raw/`,
`art/candidates/` and `ImageGen/` are all gitignored). Kokomi has 22 ids with no
row at any rank (`s17-kokomi.md` §4) and the icons family has 37 of 113
(`s17-icons-ui-models-vfx.md` §10) — together they are `EB-163`.

**Companions have no such gap, and the reason is mechanical rather than
virtuous.** Two shapes, both covered:

| shape | ids | where the row lives |
|---|---:|---|
| `shortlist` rows | 46 | `art/candidates/<id>/r1.png` … `r3.png` — 138 rows, all present |
| `auto` rows | 5 (`barbara_melody`, `bennett_passion`, `fischl_nightrider`, `kaeya_frostgnaw`, `sucrose_gust`) | the rendered out-path `ImageGen/images/cards/companions/<id>.png` |

`art_fetch` keys a shortlist row on the *candidate* path and an auto row on the
*out* path, so a check that looks only at out-paths sees 5 of 51 and a check
that looks only at candidate paths sees 46 of 51. **Neither number is the
answer; the union is.** That is a real requirement for the joined ledger and is
carried into `s17-joined-ledger-proposal.md`.

Two further completeness checks, both green:

- **All 100 distinct sources named across all 3 ranks of all 51 rows are
  present in `art\raw\`** (matching on the underscore-normalised filename that
  `art_fetch` writes). Zero missing.
- **All 138 candidate PNGs for the 46 shortlist ids exist on disk**, and the 5
  auto ids correctly have no `art/candidates/<id>/` directory.

---

## 6. Collision and duplicate state

### 6a. Byte-identical outputs: **NONE**

I hashed all 51 shipped companion card PNGs (sha256). **Zero duplicate groups.**
This corroborates `s17-klee.md` §8's cross-family statement from the other
side: no companion file is byte-identical to another companion file, and the
Klee family independently verified no Klee file is byte-identical to any
companion file.

### 6b. Effective-pick source collisions: **NONE, inside or outside the family**

All **51 rank-1 sources are distinct**. Extending the check to every plan row in
the repo at every rank: **no source used by a companion rank-1 row is used by
any non-companion row at any rank.** This is the strongest single reason the
family is lint-clean — L1 (`tools/art_lint.py:320-323`) cannot fire on it.

### 6c. Latent shared sources at ranks 2–3 — 29 groups, 27 benign by construction

29 source groups touch a companion-family row and are shared with another id.
**27 of them are a Genshin character's own plate shared between that character's
own 2–3 cards** — e.g. `Charlotte Character Card Platinum.png` at r2 of all
three Charlotte cards (`plan.tsv:561,564,567`), `Gorou Portrait.png` at r2 of
all three Gorou cards (`:750,753,756`). This is not a violation: it is the
**`source_group` mechanism working as designed**, and companions are what it
was designed for. `tools/art_fetch.py:66-74` says so in as many words —
*"Companion siblings share ONE source family and differ by crop, which L1 would
otherwise read as a dedupe violation."* 46 companion ids carry a per-Genshin-
character group (`albedo`, `charlotte`, `gorou`, `neuvillette`, …); the 5 `auto`
ids carry none and need none, their sources being unique TCG equipment plates.

**The two that cross a register, recorded because no lint can see them
(`art_lint.py:44-49` — only `/cards/` rows enter L1):**

| shared sources | ids | live today? |
|---|---|---|
| `Durin.png` **and** `Durin Item.png` | card `durin_witchs_flame` (r1 `Durin.png`, r3 `Durin Item.png`, `plan.tsv:617,619`) and badge `power_witchs_flame` (r1 `Durin Item.png`, r2 `Durin.png`, `plan.tsv:691-692`) | **no** — the two effective picks are different files. The card and its badge draw on **the same two-file pool with the ranks exactly swapped**, so promoting either one's r2 makes them collide. |
| `Nicole Icon.png` | card `nicole_celestial_gift` r3 (`plan.tsv:625`) and badge `power_celestial_gift` r1 (`plan.tsv:693`) | **no** — the card's effective pick is r1 `Character Nicole Game.png`. |

Both are the same *latent* shape as the Furina `ovation_trickle` /
`stagehands_encore` collision already on [USER]'s plate
(`docs/current/QUEUE.md:53` pick (1)); neither bites today. **Not defects.**
Recorded because a joined ledger has to decide whether "one source, one card
**and** one badge" counts as reuse, which is the same question
`s17-klee.md` §8 raises with 12 instances.

One further group worth naming because it has four members:
`Neuvillette Character Card Golden.png` at r3 of all three Guest-Star cards
**and** of the Rare `neuvillette_ancient_sea_authority` (`plan.tsv:589,592,595,1028`).
Legal — same `neuvillette` group, different crops — but it is the only place
where a **Rare** and its non-Rare siblings sit in one pool.

### 6d. No companion row appears in `art_lint`'s L1 / L7 / L8 / L9 / L11 / L12

Verified against the full live output in `baseline-run-2026-08-26.txt:74-124`.
The only two companion lines in the whole run are the two L6 clip warnings of §2.

---

## 7. Findings — facts, with what each does and does not prove

**F1 — the companion card bill is complete, and it is the only one that is.**
51/51 rendered, staged, deployed, provenance-recorded, lint-clean, zero stale,
zero duplicates, zero effective collisions. *Does not prove* any of the 51 looks
right — no eyes-on was taken and none may be (§8, review state).

**F2 — the [USER] taste pass on these 51 has never been taken, and the register
already says so.** `review/ruled/art-runs-2026-08-08.md:267-274` (run 9) rules
precisely this: *"all 62 Kokomi personal faces and all 15 Inazuma companions
carry 3 ranked candidates each, with every candidate PNG present on disk … What
is owed is [USER]'s eyes, and that is what the row means."* `art/picks.tsv` in
the primary holds **8 rows and all 8 are the `EB-67` Kokomi icons** — **no
companion id has ever had a pick recorded**, so all 46 shortlist faces ship on
`art_process`'s automatic rank-1 promotion. That is a provisional pick, not an
applied one.

**F3 — five companion-applied powers have no badge (§3d), and the correct count
is five, not four.** Registered as part of `EB-153`. *Does not prove* that any
of them should have art; that is `EB-153`'s disposition and [USER]'s.

**F4 — R13's silence is unexplained (§3d).** *Does not prove* R13 is broken. It
proves only that the log says `SELFCHECK passed` in a session where five powers
had no icon mapping, and that the two statements have not been reconciled.

**F5 — lane B's ledger cannot see this family's non-card half, and the reason is
structural.** `tools/art_ledger.py` derives pck-resource expectations from
`"<char>/<sub>/<name>.<ext>"` **string literals** in `klee-mod/KleeCode/**`
(handoff §1). The seven companion badges have literals and are billed — under
`klee/powers`, indistinguishably from Klee's own 29. The five powers of §3d have
**no literal anywhere**, because the whole finding is that no path was ever
written. So they are invisible to the ledger by construction, and its
`power 58 expected / 51 covered / 0 missing / 7 defect` line is a count of
*declared* surfaces, not of *needed* ones. This is the same shape as the lane's
own `F5`/`D7` (an unenumerable set with a missing member is invisible), reached
from the opposite direction: not concatenation, but absence of any string at
all. *Does not prove* the tool is wrong — its counts are exactly what it claims
to count.

**F6 — no path in the repo says "companion" for a non-card surface (§3c).**
Cards have `ImageGen/images/cards/companions/`; badges do not have an equivalent.
A family-scoped question therefore cannot be answered by a path glob for the
non-card half, only by reading which card applies which power. *Does not prove*
the layout is wrong — it ships correctly today.

---

## 8. Review state

| item | state | evidence |
|---|---|---|
| The 46 shortlist card faces | **provisional rank-1 picks auto-applied; [USER] taste pass NOT taken** | `art/picks.tsv` holds no companion row; `art-runs-2026-08-08.md:267-274`; QUEUE "Art debt" row (`docs/current/QUEUE.md:53`, OPEN — taste) |
| The 5 `auto` card faces | **auto rows — never had a shortlist and by design never will** | `plan.tsv:219-223`; the `auto` pick kind, `art_fetch.py:60` |
| The companion contact sheet | **renderable again as of 2026-08-27** — 138 refs, 0 broken | `art\contact_sheet_companions.html`, written 2026-08-13 01:31; candidate dirs re-materialised this morning |
| The 7 badges | **rank 1 applied; no live look recorded** | `plan.tsv:686-694`, `:716-719`; no `picks.tsv` row |
| The `art-runs-2026-08-08.md` companion rows | **REVIEW BUNDLE — "No pick was made and no pick may be read into these files"** | that file's header, lines 3-5 |
| **A companion art-pass requirements doc** | **DOES NOT EXIST** | `docs/current/art/` holds `furina-art-pass-requirements.md`, `kokomi-art-pass-requirements.md`, `kokomi-source-census.tsv` — and nothing for Klee or companions. The companion source rule lives only in `art_fetch.py:66-74`'s comment and in the `source_group` column itself. |

---

## 9. Open questions — numbered, for [USER] or the S17 integrator. **No option is recommended.**

**Q1 — the companion source rule is real, unwritten, and is the answer to
another family's open question.** Companions run a per-Genshin-character
`source_group` with no rarity scoping: siblings share a plate and differ by
crop, and the mechanism was built for them (`art_fetch.py:66-74`). Furina's rule
is rarity-scoped and ratified; Kokomi's is character-wide and *unwritten*, which
is her open Q2 (`s17-kokomi.md` §7 Q2). Pick: (1) write the companion rule down
as it stands, in a new `docs/current/art/companion-art-pass-requirements.md`,
and let Kokomi's Q2 be settled separately; (2) write **one** source-uniqueness
law covering all four families, with the per-family scoping as clauses, and
settle Kokomi's Q2 in the same act; (3) leave all three unwritten and keep the
column as the only authority.

**Q2 — the two latent card↔badge source pairs (§6c).** `durin_witchs_flame` /
`power_witchs_flame` share a two-file pool with swapped ranks;
`nicole_celestial_gift` / `power_celestial_gift` share `Nicole Icon.png` at
different ranks. Neither collides today. Pick: (1) leave both — they are latent
and the effective picks differ; (2) move one rank off the shared file in each
pair so promoting an r2 can never collide; (3) rule card↔badge source reuse
**legal by construction** for companions the way `art_lint.py:44-49` already
rules register-crossing reuse legal, and stop tracking it.

**Q3 — does the end-of-turn docket want an Arlecchino sprite (§3e)?** Kokomi's
Bake-Kurage has one; Arlecchino's Bond-of-Life row, which sorts **first**, has
a title and no picture, by a mechanism the file calls the degradation it wants.
Pick: (1) none owed — the number-and-text row is the intended shape for
everything but a summoned creature; (2) name the docket rows that should carry a
sprite and let a batch price them. *Design question, stated only as a question.*

**Q4 — the companion badge namespace (§3c, F6).** Seven companion badges ship
as `res://klee/powers/*` out of the shared `ImageGen/images/powers/`. Pick:
(1) leave it — it ships correctly and moving packed paths is a real migration;
(2) introduce `companions/powers/` and move the seven, accepting one
`build_pck.ps1` copy-block change and one `KleePowerIcons` edit; (3) leave the
paths and add a **registry** (a curated id → family list) so tools can answer
family questions without a path glob.

**Q5 — the missing companion requirements doc (§8).** There is none, for
companions or for Klee. Pick: (1) write one for companions now, since §3a's
crop grammar and §6c's group rule are already mechanically true and just need
transcribing; (2) write one only when the taste pass is taken; (3) rule the
per-character `source_group` column self-documenting and write none.

---

## 10. UNKNOWN / NON-FINDING

- **NON-FINDING:** zero missing companion card portraits; zero stale files;
  zero byte-identical outputs; zero effective source collisions inside or
  across families; zero companion rows in L1/L7/L8/L9/L11/L12; zero companion
  ids without a `SOURCES.tsv` row; zero plan sources absent from `art/raw/`;
  zero missing candidate PNGs; zero broken refs in the companion contact sheet.
- **NON-FINDING:** no companion `vfx/` scene is referenced by any companion C#,
  so nothing is broken by there being none (§3f).
- **NON-FINDING:** no companion card id collides with a Klee, Furina or Kokomi
  basename in the flat deployed `images/cards/` directory.
- **CLOSED, not a finding:** the "25 of 27 dead contact sheets" data-loss item
  (`BLOCKERS.md` §1.1). `art/candidates/` was re-materialised 2026-08-27 (297
  directories) and all 27 sheets resolve; the companion sheet's 138 refs are
  all live. **The R212(1) veto route is open again for this family.**
- **UNKNOWN:** why `KleeSelfCheck`'s R13 reports `SELFCHECK passed` in a session
  where five powers have no icon mapping (§3d). Needs the `PowerModel`
  decompile — `game_ref/` on this machine holds only YAML/JSON — or one
  instrumented boot. Neither was taken.
- **UNKNOWN:** whether any of the 51 faces reads well. No image was opened, no
  eyes-on was taken, no capture exists.
- **UNKNOWN:** whether the four silent unmapped powers (`CannonFireSupport`,
  `NightVigil`, `AncientSeaAuthority`, `MasqueRedDeath`) draw a visible
  placeholder in play or nothing at all. Only `Metallicize` produces a log line.
- **UNKNOWN:** whether the wiki holds unfetched companion plates. Only the local
  fetched pool was examined, and it needed nothing.
- **Search boundary:** I read `art/plan.tsv`, `art/SOURCES.tsv`, the three
  companion YAML sheets, `docs/current/{STATE,BACKLOG,QUEUE,OPERATIONS}.md`,
  `docs/current/art/*`, `tools/art_{coverage,lint,fetch}.py`,
  `tools/build_pck.ps1`, `klee-mod/build/deploy.ps1`, the `klee-mod/KleeCode`
  files naming a companion power or a `powers/` path, `review/ruled/art-runs-2026-08-08.md`,
  the four sibling S17 files, the lane B handoff, and — read-only in the primary
  — `art/raw/`, `art/candidates/`, `art/picks.tsv`,
  `art/contact_sheet_companions.html`, `ImageGen/images/**`,
  `klee-mod/assets/klee.pck.contract.txt`, the deployed `mods\klee\images\cards`,
  and the five `SlayTheSpire2\logs\*.log` files. I did **not** read git history,
  run any art tool, open any image, launch the game, or run git in the primary.

---

## 11. What this document does **NOT** establish

It does not establish that any companion portrait is good, on-model, or
shippable — "51/51 covered" is a count of files, not a judgement, and the taste
pass on all 46 shortlist faces is explicitly still owed. It does not establish
rights, licensing, or public-release safety: the `private-placeholder` category
on all 58 surfaces is transcribed from `SOURCES.tsv`'s own `tier` column and
`OPERATIONS.md:296`, and transcribing a category is not a rights verdict. It
does not establish that the five unmapped powers should have art, that the
docket wants a second sprite, that the badge namespace should move, or that a
requirements doc is owed — each of those is a numbered pick in §9 and none has
a recommendation. It does not establish that `KleeSelfCheck` R13 is defective;
it establishes only that its "passed" line and the five iconless powers have not
been reconciled. It does not interpret [USER]'s playtest, open any window, or
move any stamp. And it mints no id: every finding either lands on an existing
row (`EB-153`, `EB-163`, QUEUE Art debt) or is a numbered question.
