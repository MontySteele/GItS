# S17 — Furina art coverage and provenance, draft ledger

**Research rail, surplus-dispatch-3, 2026-08-26. This file decides nothing.**
It is a census and a draft ledger for one family (Furina). It makes no art
pick, no rights verdict, no taste judgement, and mints no `EB-`/`M-`/`R-` id.
Every open call named below is already an existing `QUEUE.md` or `BACKLOG.md`
row and is cited, not re-opened.

**What this does NOT establish.** It does not establish that any source is
legally usable, that any candidate is good, that the seven missing power
sigils should be filled from the sources on their shortlists, or which orb set
Furina's energy counter should wear. It does not read the deployed game: no
tool was run against the installation and nothing was launched. It does not
re-run `art_coverage.py` or `art_lint.py` — the numbers below are read from
the recorded baseline. Where a claim rests on a file's own docstring rather
than a measurement, it says so.

---

## 0. Sources of truth used here

| what | where | note |
|---|---|---|
| Coverage + lint baseline | `review/dispatch3/s17-art/baseline-run-2026-08-26.txt` | live read-only run on the art-bearing primary, `main 223a4ff`, both tools `exit=0` |
| Card-art bill | `C:\Users\Monty\Documents\GitHub\GItS\tools\art_coverage.py` (scope note at `:93-99`) | counts **card-sized outputs only** |
| Lint rules | `C:\Users\Monty\Documents\GitHub\GItS\tools\art_lint.py` | `GENERATOR_OWNED` at `:420-446` |
| Pick plan | `C:\Users\Monty\Documents\GitHub\GItS\art\plan.tsv` (1259 lines) | columns at `:2`; rank 1 = effective pick |
| Source ledger | `C:\Users\Monty\Documents\GitHub\GItS\art\SOURCES.tsv` (873 rows) | `filename → source_url → tier → replace_priority` |
| Packed set | `C:\Users\Monty\Documents\GitHub\GItS\klee-mod\assets\klee.pck.contract.txt` | **46** `res://furina/` resources of 132 total |
| Pack staging | `C:\Users\Monty\Documents\GitHub\GItS\tools\build_pck.ps1` | copy blocks at `:134-215`, fallback at `:220-244` |
| Card staging | `C:\Users\Monty\Documents\GitHub\GItS\klee-mod\build\deploy.ps1:109-146` | loose PNGs, **not** in the pck |
| Deferral register | `C:\Users\Monty\Documents\GitHub\GItS\klee-mod\build\validate.ps1:892-925` | `$pckDeferred`, the live list of knowingly-absent art |
| Requirements | `C:\Users\Monty\Documents\GitHub\GItS\docs\current\art\furina-art-pass-requirements.md` | tiers at `:65-67`, paths `:122-140`, ledger rule `:156-165`, non-card bill `:393-478` |

**Contract provenance check.** I hashed the local pck and it matches the
contract's own `sha256` (`70B227FB…D60468`), so the contract does describe
`klee-mod/assets/klee.pck` as it sits on disk (mtime 2026-08-26 20:46). Both
files are gitignored (`.gitignore:63-64`), so this is a local build artifact,
not a tracked record. **UNVERIFIED:** whether that pck is byte-identical to
the one inside the installed `0.2-1155` build [USER] is playtesting (build id
`20260826-193602+223a4ff`, per PREFLIGHT) — the pck's `build_id.tres` is
inside the pack and I did not unpack it.

---

## 1. The headline: card art is a minority of Furina's visual surface

`art_coverage.py` bills **card-sized outputs only** and says nothing about the
other Furina surfaces. Counting every surface the family actually has:

| surface class | expected | present | absent | where it ships |
|---|---:|---:|---:|---|
| Card portraits (sheet rows) | 84 | 81 | **3** | loose PNG next to the dll |
| Card portrait (token) | 1 | 1 | 0 | loose PNG |
| Card portraits (C#-only keys, no sheet row) | 2 | 0 | **2** | loose PNG |
| Power / status sigils | 22 | 15 | **7** | `res://furina/powers/` |
| Starting relic icon | 1 | 1 | 0 | `res://furina/relics/` |
| Salon summon sprites | 3 | 3 | 0 | `res://furina/salon/` |
| Salon role glyphs | 3 | 3 | 0 | `res://furina/salon/` |
| Combat rig layers (shipped cut) | 4 | 4 | 0 | `res://furina/model/layers/` |
| Combat still + rest/merchant still | 1 | 1 | 0 | `res://furina/model/` |
| UI textures | 10 | 9 | **1 (falls back)** | `res://furina/ui/` |
| Energy-counter orb layers | 5 (base-scene bill) | **0** | 5 | nowhere — no scene exists |
| Authored scenes / materials | 9 | 9 | 0 | `res://furina/{ui,model,vfx,materials}/` |

**Totals.** Card-sized bill for Furina = **87 expected / 82 present / 5
absent**. Non-card bill = **58 expected / 45 present / 13 absent**, where the
13 = 7 power sigils + 1 UI wipe (present in the pck, but as *Klee's* file) +
5 orb layers. See §4–§6 for each.

Do not confuse that 45 with the **46** `res://furina/` lines in the pck
contract: the contract counts what is packed, so it includes the nine authored
scenes/materials, counts the Klee-filled wipe as present, and excludes nothing
for being borrowed. The two numbers measure different things and agree with
each other exactly once you account for that.

`art_coverage.py`'s Furina lines report only the card block, and they report
it correctly — the point is that "24 missing" repo-wide is a **card** number,
and Furina's non-card hole is separately 13 rows deep.

Baseline lines for the card block (`baseline-run-2026-08-26.txt:13-19`,
`:47-50`, `:56-58`, `:66-69`):

```
Furina token            expected  1  covered  1  missing 0
Furina personal sheet   expected 84  covered 81  missing 3
  uncommon 2  change_the_bill, take_it_from_the_top
  rare     1  grand_gala
Shipped in C# with no sheet row -- 3, of which 2 are Furina:
  klee-mod\KleeCode\Cards\Furina\SpotlightCards.cs  spotlight_center_stage, spotlight_guest_cast
TOTAL card-sized outputs expected: 294   covered: 270   missing: 24
```

---

## 2. Ledger conventions used in §3–§8

Columns are the charter's. To keep the tables readable, the constant columns
are stated once here and only exceptions are repeated in a row.

- **Rights tier (CATEGORY only — I assign no verdict).** The repo's own two
  tiers are defined at `furina-art-pass-requirements.md:65-67`: **Tier F**
  = found/official/fan, *private playtest builds only*; **Tier O** =
  original/commissioned, *the only art permitted in a public build*. I map
  Tier F → `private-placeholder`, Tier O → `public-safe`, and anything with
  no declared tier → `UNKNOWN`. Where a tier comes from a generator's own
  docstring rather than `SOURCES.tsv`, the row says "declared by producer".
  **Every rights decision remains [USER]'s.**
- **Source.** `art/SOURCES.tsv` row where one exists. Two keying conventions
  are in use and both are legitimate: an `auto` pick is keyed by its
  **out-path**; a `shortlist` pick is keyed by its **candidate path**
  (`art/candidates/<asset_id>/rN.png`). A naive out-path join therefore
  *misses* every shortlist-promoted asset — see §9 finding F5.
- **Packed path.** From the live `klee.pck.contract.txt`, which is *derived
  from what actually landed* (`build_pck.ps1:789-823`), not asserted.
- **Fallback.** What the game renders when the file is absent.
- **Review state.** From `docs/current/art/`, `review/active/art-runs-*.md`,
  and the open `QUEUE.md` rows. "SHIPPED, no recorded eyes-on" means the file
  is on disk and packed but I found no record of [USER] approving it by eye.
- **Collision/duplicate state.** Two ids sharing one effective source, or two
  outputs that are pixel-identical (`art_lint` L1/L7/L12).

---

## 3. Card portraits — 87 rows, 82 present

**Rendered output:** `ImageGen/images/cards/furina/<id>.png`.
**Measured:** all **83** PNGs on disk are exactly `500x380`, 8-bit RGBA
(`ct6`), matching the requirement at `furina-art-pass-requirements.md:144`.
83 on disk = 81 sheet-covered + 1 token + 1 stale.
**Packed path:** none. Card art is **not in the pck** — `deploy.ps1:109-146`
stages every character's card dir into one flat `images/cards/` next to the
dll and `RosterArt.CardPortrait` (`klee-mod/KleeCode/KleeArt.cs:23`, loader at
`:55-85`) loads `images/cards/<sheetId>.png` at runtime.
**Fallback:** `KleeArt.cs:76-79` — a missing file logs
`No card art at <path>` and returns `null`, which renders BaseLib's "BETA"
placeholder (`deploy.ps1:144`).
**Rights tier:** I joined all 83 outputs to their rank-1 plan row and then to
`SOURCES.tsv` (via out-path or `art/candidates/<id>/r1.png`). **Result: 83/83
resolve, every one `tier=F`, `replace_priority=high`.** Category for the whole
block: `private-placeholder`. Zero provenance holes.
**Review state:** batch 1–3 sheets exist (`art/contact_sheet_identity.html`,
`contact_sheet_salon-fanfare.html`, `contact_sheet_spotlight.html`), review
batches defined at `furina-art-pass-requirements.md:515-528`. Twelve Curtain
Call faces plus the four `R166` re-hunt rows are **OPEN eyes-on** at QUEUE
`S4-G12`/`CC-G1`/`CC-G2` (`docs/current/QUEUE.md:47`).

### 3a. The five absent card rows

| expected id | why absent | plan rows | source shortlist | blocking unknown |
|---|---|---:|---|---|
| `change_the_bill` (uncommon, salon) | **never hunted** — sheet row exists (`docs/furina-cards.yaml:472`), `art/plan.tsv` has **zero** rows for it | 0 | none | no candidate exists; this is a hunt, not a pick |
| `take_it_from_the_top` (uncommon, spotlight) | **never hunted** — sheet row at `docs/furina-cards.yaml:622`, **zero** plan rows | 0 | none | same |
| `grand_gala` (rare, salon) | hunted eight times, **no rank 1 was ever set** | 8 (ranks 2–8 live, r1 commented out at `art/plan.tsv:386`) | r2 `Item Furina Banquet`, r3 `Opera Epiclese - Neuvillette's Seat`, r4–r5 wallpapers, r6–r8 gala/banquet set | already a [USER] taste pick — QUEUE **Art debt**, pick (3) (`docs/current/QUEUE.md:53`) |
| `spotlight_center_stage` (C#-only key) | mechanics shipped, art never picked | 2 (ranks 2–3, `art/plan.tsv:1138-1139`) | r2 `Tabletop Troupe Pros Furina.png` (2160²), r3 `Item Festival Spotlight.png` | no rank 1; both Spotlight rows are `furina_pool`, so their crops must differ (L7) |
| `spotlight_guest_cast` (C#-only key) | same | 2 (`art/plan.tsv:1140-1141`) | r2 `Opera Epiclese - Neuvillette's Seat.png`, r3 `Tabletop Troupe Pros Navia.png` | same |

`change_the_bill` and `take_it_from_the_top` are the two `Win3` Salon/Spotlight
rows that took Furina's sheet from 82 to 84 (`docs/current/STATE.md:114-115`).
The art pipeline has not been told they exist. **That is the single largest
Furina gap this census found that is not already on a register row.**

### 3b. Stale file that must never be counted as coverage

| file | status | recorded reason |
|---|---|---|
| `ImageGen/images/cards/furina/rising_tide.png` | **STALE**, on disk, packed nowhere, counted nowhere | `baseline-run-2026-08-26.txt:63` — card cut by A4 (playtest-2 red-pen, 2026-07-28); kept because the asset is already cleared through `SOURCES.tsv`. Re-examined 2026-07-29: the ledger description was **wrong** — the bytes are `A Wish For Smooth Sailing Quest Still 2`, a chibi resort panorama with no Furina focus. |

---

## 4. Power / status sigils — 22 wired, 15 present, 7 absent

**Wiring:** `klee-mod/KleeCode/Powers/KleePowerIcons.cs` — 22 `furina/powers/*`
paths (`:68-72`, `:80-89`, `:99-104`, `:109-110`).
**Rendered output:** `ImageGen/images/furina/powers/<asset>.png`, **all 15
measured at exactly `256x256` RGBA**, matching
`furina-art-pass-requirements.md:455`.
**Packed path:** `res://furina/powers/<asset>.png`, staged by the character
loop at `build_pck.ps1:204-215`; all 15 appear in the contract.
**Fallback:** `KleePck.Path` returns `null` when a file is absent, the Harmony
prefix declines (`KleePowerIcons.cs:169-178`), and the base-game placeholder
draws. This is deliberate: `KleePowerIcons.cs:135-140` refuses to let a new
power inherit a sibling's sigil, because that reads as intentional.
**Rights tier:** `private-placeholder` (Tier F) for all 15 with rows.

### 4a. The 15 present

| asset id | rank-1 source (plan) | `SOURCES.tsv` row keyed at | review state |
|---|---|---|---|
| `fanfare` | `Talent Let the People Rejoice.png` | `art/candidates/power_furina_fanfare/r1.png` (`SOURCES.tsv:539`) | SHIPPED, no recorded eyes-on |
| `rising_ovation` | `Constellation A Woman Adapts Like Duckweed in Water.png` | out-path | SHIPPED |
| `salon_member` | `Talent Salon Solitaire.png` | out-path | SHIPPED |
| `grand_salon` | `Talent Salon Solitaire 2.png` | out-path | SHIPPED |
| `all_the_worlds_a_stage` | `Talent Endless Waltz.png` | out-path | SHIPPED |
| `center_stage` | `Talent The Sea Is My Stage.png` | out-path | SHIPPED |
| `guest_cast` | `Constellation They Know Not Life…` | out-path | SHIPPED |
| `leading_role` | `Constellation His Name I Now Know, It Is…!` | out-path | SHIPPED |
| `supporting_cast` | `Constellation My Secret Is Hidden Within Me…` | out-path | SHIPPED |
| `top_billing` | `Constellation Love Is a Rebellious Bird…` | out-path | SHIPPED |
| `limelight` | `Constellation Hear Me — Let Us Raise the Chalice of Love!` | out-path | SHIPPED |
| `star_of_the_show` | `Animula Choragi Shape.png` | out-path | SHIPPED |
| `stage_lights` | `Talent Unheard Confession.png` | out-path | SHIPPED |
| `standing_ovation` | `Furina Icon.png` | `art/candidates/power_furina_standing_ovation/r1.png` (`SOURCES.tsv:553`) | SHIPPED |
| `ovation_trickle` | `Item Furina Banquet.png` | `art/candidates/power_furina_ovation_trickle/r1.png` (`SOURCES.tsv:554`) | SHIPPED |

Twelve are keyed at their out-path; three (`fanfare`, `standing_ovation`,
`ovation_trickle`) only at their candidate path, because those three were
`pick=shortlist` rather than `pick=auto`. Both are real ledger rows; see §9 F5.

### 4b. The 7 absent — BACKLOG `EB-65`

Register row: `docs/current/BACKLOG.md:79`. Deferral is *registered*, not
silent: each has an entry in `$pckDeferred` with a reason
(`klee-mod/build/validate.ps1:903-924`), and `validate.ps1:994-1001` fails the
build in the **other** direction too — a deferral whose art has landed, or that
nothing references, is itself an error. That is a well-built gate.

| expected id | power it labels | shortlist r2 | shortlist r3 | plan lines | raw source on disk? |
|---|---|---|---|---|---|
| `fortissimo_guard` | Block per Salon deploy | `Item Fontaine Completeness.png` | `Sword Hydro.png` (128², ×2.0) | `art/plan.tsv:1125-1126` | both PRESENT |
| `stagehands` | Block per Salon bow | `Item Movable Small Spotlight.png` | `Icon Opera Epiclese.png` — **FLAG 64×58, ×4.0 upscale** | `:1127-1128` | both PRESENT |
| `stagehands_encore` | the Encore half of Stagehands | `Item Ovations That Ceased Upon Festivity.png` | `Item Festival Spotlight.png` | `:1129-1130` | both PRESENT |
| `courtroom_drama` | first reaction each turn | `Item Fontaine Judgment.png` | `Icon The Duke's Office.png` — **FLAG 64×64, ×4.0 upscale** | `:1131-1132` | both PRESENT |
| `the_gallery_stirs` | first Encore spend draws | `Item Fontaine Big News.png` | `Item Theater Tickets.png` | `:1133-1134` | both PRESENT |
| `quick_change` | first Attack each turn draws | `Item Fontaine Redemption.png` | `Item Fontaine Lucine.png` | `:1135-1136` | both PRESENT |
| `unheard_confession` | Block whenever Fanfare changes | `Animula Choragi.png` (1080², Furina's own Animula symbol) | `Item Fontaine Attunement.png` | `:1123-1124` | both PRESENT |

Shortlist reasoning is at `review/active/art-runs-2026-08-08.md:146-171`.
All 14 raw sources are on disk under `C:\Users\Monty\Documents\GitHub\GItS\art\raw\`
(verified file-by-file), so re-rendering the candidates is a tool run with no
fetch. **Blocking unknown: see §9 F1 — none of these seven has a rank-1 row.**

---

## 5. Salon summons and role glyphs — 6 rows, all present

The Salon Members are Furina's summon surface. They are *not* card art and
*not* power badges; they are creature sprites drawn on a stage scene beside
her, which is why `build_pck.ps1:163-171` gives them their own copy block for
the same stated reason Kokomi's Bake-Kurage creature gets one.

| expected id | rendered output | measured | packed path | source | rights tier | review state |
|---|---|---|---|---|---|---|
| `member_usher` | `ImageGen/images/furina/salon/member_usher.png` | 121×144 | `res://furina/salon/member_usher.png` | `Salon Members Summon.png` (`SOURCES.tsv`, tier F, prio high) | `private-placeholder` | OPEN eyes-on, QUEUE `S4-G17` item `AS2-D5` |
| `member_chevalmarin` | `…/member_chevalmarin.png` | 129×144 | `res://furina/salon/member_chevalmarin.png` | same source, different cut | `private-placeholder` | same |
| `member_crabaletta` | `…/member_crabaletta.png` | 120×144 | `res://furina/salon/member_crabaletta.png` | same source, different cut | `private-placeholder` | same |
| `glyph_block` | `…/salon/glyph_block.png` | 32×32 | `res://furina/salon/glyph_block.png` | **generated**, `tools/gen_salon_glyphs.py` | `public-safe` — **Tier O declared by its producer** (`gen_salon_glyphs.py:2`); [USER] owns the verdict | OPEN eyes-on, `AS2-D5` |
| `glyph_damage` | `…/salon/glyph_damage.png` | 32×32 | `res://furina/salon/glyph_damage.png` | same generator | same | same |
| `glyph_support` | `…/salon/glyph_support.png` | 32×32 | `res://furina/salon/glyph_support.png` | same generator | same | same |

Consumers: `klee-mod/KleeCode/Vfx/SalonVisualsBridge.cs:71-77` (sprites) and
`:100-110` (glyphs), on the stage scene `furina/ui/salon_stage.tscn` (`:49`).
Per-sprite geometry is carried in `ImageGen/images/furina/salon/members.json`
(target height 144). Glyphs are **white masters tinted per member through
`Modulate`** (`SalonVisualsBridge.cs:98-108`), so one file per role serves
three hues and the dry state — a deliberately shared file, not a collision.

**Fallback:** none authored. If a member sprite is absent `KleePck.Path`
returns `null` and the stage slot has no texture; I did not find a placeholder
path for this surface. **UNKNOWN** — I did not trace what
`SalonVisualsBridge` does with a null sprite; that read was out of scope here.

**Captures that exist for the eyes-on:** `art/eb52_captures/d5_salon_1member.png`,
`art/eb52_captures/d5_salon_stage_2members_encore5.png`,
`art/eb52_captures/_crop_stage.png`.

---

## 6. UI — 10 rows, 9 present, 1 live fallback; plus the energy counter

| expected id | rendered output | measured | packed path | source | tier | state |
|---|---|---|---|---|---|---|
| `select_portrait` | `furina/ui/select_portrait.png` | 132×195 | `res://furina/ui/select_portrait.png` | `Furina (Genshin Impact).png` (Wikipedia render) via `gen_furina_stills.py` | `private-placeholder` (F) | SHIPPED |
| `select_portrait_locked` | `…/select_portrait_locked.png` | 132×195 | packed | derived from the above by the same generator | `private-placeholder` | SHIPPED |
| `char_icon` | `…/char_icon.png` | 88×88 | packed | same Wikipedia render, `gen_furina_stills.py` | `private-placeholder` | SHIPPED |
| `char_icon_outline` | `…/char_icon_outline.png` | 88×88 | packed | **derived** from `char_icon.png` by `tools/gen_char_icon_outlines.py`; no `SOURCES.tsv` row (correct — it has no upstream) | inherits `private-placeholder` | SHIPPED |
| `map_marker` | `…/map_marker.png` | 49×64 | packed | same Wikipedia render | `private-placeholder` | SHIPPED |
| `selection_splash` | `…/selection_splash.png` | 1920×1200 | packed | `Furina Card 2.png` | `private-placeholder`, prio **high** | SHIPPED |
| `select_bg` | `…/select_bg.png` | 1920×1080 | packed | `Namecard Background Furina Banquet.png` | `private-placeholder` | SHIPPED |
| `energy_icon_74` | `…/energy_icon_74.png` | 74×74 | packed | `Element Hydro.svg` | `private-placeholder` | SHIPPED, **no consumer** (see below) |
| `energy_icon_22` | `…/energy_icon_22.png` | 22×22 | packed | `Element Hydro.svg` | `private-placeholder` | SHIPPED, **no consumer** |
| `transition_wipe` | **ABSENT** under `furina/ui/` | — | `res://furina/ui/transition_wipe.png` **is** in the contract | **filled from Klee** by `Copy-FurinaFallback` (`build_pck.ps1:220-244`) | inherits Klee's | **the one live Klee fallback for Furina** |

`build_pck.ps1:233-244` lists nine assets eligible for the Klee fill. Furina
supplies her own for eight of them; **`transition_wipe.png` is the only one
she does not**, and the requirements doc already sanctions sharing it
(`furina-art-pass-requirements.md:407`, "generated by
`tools/gen_transition_wipe.py`, not hunted; sharing Klee's is fine"). Note the
asymmetry: `art_lint.GENERATOR_OWNED` registers `.../klee` and `.../kokomi`
`transition_wipe.png` but **not** a Furina one (`art_lint.py:437-438`) —
consistent with her not having one. The build log line to watch for is
`Furina fallback: ui\transition_wipe.png <- Klee` (`build_pck.ps1:230`); the
acceptance criterion at `furina-art-pass-requirements.md:565-570` says to read
that log, not the screen, because a fallback looks like working art.

### 6a. Energy counter — QUEUE `M19`, cited not picked

`Furina.cs:100-101` points `CustomEnergyCounterPath` at the **base game's**
`res://scenes/combat/energy_counters/ironclad_energy_counter.tscn`. So Furina
has **no energy-counter scene of her own**, and her two Hydro energy icons
have no consumer — stated plainly in the requirements at
`furina-art-pass-requirements.md:418-423`: "Producing them changes nothing
in-game until someone authors a Furina energy-counter scene. Keep them in the
bill … but treat the scene as the blocking work, not the art."

The orb layer set is **[USER]'s open pick at QUEUE `M19`**
(`docs/current/QUEUE.md:51`): (1) **A Fontaine Hydro — default**, (2) B Opera
Pale, (3) C Tidal, sheet `art/contact_sheet_eb88_energy_orb.html`, ungated
under R212(1) so the default ships if no pick lands. **I cite it and pick
nothing.**

Three facts about that surface, already recorded and worth carrying because
they constrain any future art:

1. `energy_orb_dark.tres` is the **darkening material applied at Energy 0**,
   not the container the five textures live under. The "five" is the base
   scene's authoring choice, not a code constraint — both loops are
   `GetChildren()` (`tools/gen_energy_orb_layers.py:20-46`, read out of the
   shipped assembly with `ilspycmd -t
   MegaCrit.Sts2.Core.Nodes.Combat.NEnergyCounter` on 2026-08-13).
2. There are **two stacks**: `%RotationLayers` children are spun by `_Process`
   at `delta · num · (i + 1)` degrees, so a rotation layer must be centred and
   must read while tumbling.
3. The base scene itself **could not be read**: `SlayTheSpire2.pck` is `GDPC`
   format 3 with `pack_flags = 2` (PACK_DIR_ENCRYPTED). Layer *roles* are
   therefore an inference from the class contract, and 256×256 is a production
   choice, not a measured size. Both are labelled as inference on the sheet.

---

## 7. Model, combat rig, and authored scenes

| expected id | rendered output | measured | packed? | note |
|---|---|---|---|---|
| `combat_model` | `furina/model/combat_model.png` | 240×280 | **yes** | produced by `gen_furina_stills.py` (`art_lint.py:421`); also serves rest/merchant |
| `furina_combat_coat_back` | `furina/model/layers/combat/…` | 208×130 | **yes** | cut by `tools/cut_combat_layers.py furina` |
| `furina_combat_sword` | ” | 83×95 | **yes** | ” |
| `furina_combat_body` | ” | 210×280 | **yes** | ” |
| `furina_combat_hat` | ” | 72×66 | **yes** | ” |
| `furina_layer_{body,coat_back,hat,sword}` | `furina/model/layers/…` | 200×440 / 198×200 / 69×103 / 78×145 | **no — masters, by design** | `build_pck.ps1:143-161` ships only the `layers/combat` derivatives |
| `furina_wikipedia_cutout` | `furina/model/furina_wikipedia_cutout.png` | 227×440 | **no — excluded** | `build_pck.ps1:186-202`, `$pckExclude = '*_cutout.png'`; it is a cached working render with no consumer |

All model/layer rows carry the same `SOURCES.tsv` upstream — the Wikipedia
Furina render — tier **F**, priority **high**. Category:
`private-placeholder`.

Authored (not "art", but they are packed surfaces this family owns):
`furina/ui/char_select_bg_furina.tscn` (`build_pck.ps1:332-369`),
`furina/ui/character_icon.tscn` (`:443-448`),
`furina/model/combat_visuals.tscn` (`:488-493`),
`furina/model/rest_character.tscn` + `merchant_character.tscn` (`:526-541`),
`furina/materials/furina_transition_mat.tres` (`:674-697`), plus three
git-tracked scene sources overlaid from `klee-mod/pck-src/`
(`build_pck.ps1:733-740`): `furina/model/combat.tscn`,
`furina/ui/salon_stage.tscn`, `furina/vfx/spotlight_shine.tscn`.
`salon_stage.tscn` and `spotlight_shine.tscn` declare **no** `ext_resource`
textures — they are geometry and animation only, and pull their sprites at
runtime through `SalonVisualsBridge`. Boot-time presence of all of these is
asserted by `klee-mod/KleeCode/Diagnostics/KleeSceneTelemetry.cs:36-38,55,75`.

Relic: `ImageGen/images/furina/relics/ethereal_spotlight.png`, 256×256, packed
at `res://furina/relics/ethereal_spotlight.png`, rank-1 source `Item Shining
Spotlight.png` (`SOURCES.tsv:512`, tier F, prio medium), consumed by
`Relics/EtherealSpotlightRelic.cs:76,79` and
`Relics/UpgradedStarterRelics.cs:412,416`, each with `?? base.…IconPath` as
the fallback. Name drift worth noting: the requirements bill it as
`relics/ethereal_spotlight_relic.png` (`furina-art-pass-requirements.md:451`);
the shipped slug has no `_relic` suffix.

---

## 8. Collision and duplicate state

Computed over every Furina plan row (292 rows, 102 at rank 1) plus the
generator-owned paths that have no plan row.

| # | shared source | ids sharing it | verdict-free reading |
|---|---|---|---|
| C1 | `Astra Carnival Cat's Tail Gathering 2024 S5 Artwork.png` | `crowd_work`, `standing_ovation` (cards) | **the only pixel-identical Furina pair.** `art_lint` L12 reports `crowd_work == standing_ovation` as KNOWN IDENTICAL (allowlisted) — `baseline-run-2026-08-26.txt:81` |
| C2 | `Item Ovations That Ceased Upon Festivity.png` | `power_furina_ovation_trickle` **r2**, `power_furina_stagehands_encore` **r2** | this is the sigil COLLISION already on [USER]'s plate — QUEUE **Art debt** pick (1), `docs/current/QUEUE.md:53`. It bites only if `stagehands_encore` is filled from r2; `ovation_trickle` shipped from its **r1** (`Item Furina Banquet.png`), so today they do not collide on disk |
| C3 | `Salon Members Summon.png` | card `salon_debut` (`art/plan.tsv:323`) **and** all three summon sprites (`SOURCES.tsv`) | **cross-surface, four outputs from one source.** No lint sees it: L1/L7/L12 compare cards to cards, and the three sprites have no plan row at all. Intentional or not is [USER]'s read |
| C4 | `Chanson of Many Waters … Furina & Charlotte Shorts.png` | `duet`, `many_waters_melody` (cards) | two rank-1 cards, one source, different crops. Not flagged by L1 in the live run, so the effective crops differ |
| C5 | `Furina Profile.png` | `deep_breath` (card), `fortissimo_guard` (**card**, not the sigil) | same |
| C6 | `Item Shining Spotlight.png` | `limelight` (card), `relic_ethereal_spotlight` | card + relic icon, different surfaces |
| C7 | `Namecard Background Furina Banquet.png` | `dinner_service` (card), `furina_select_bg` | card + UI backdrop |
| C8 | `Item Furina Banquet.png` | `overflowing_hospitality` (card), `power_furina_ovation_trickle` | card + sigil |
| C9 | `Opera Epiclese Courtroom.png` | `courtroom_drama` (card), `witness_stand` (card) | two cards, one source, different crops |
| C10 | `Element Hydro.svg` | `furina_energy_icon_large`, `furina_energy_icon_small`, **and Klee's `power_aura_hydro`** | the only Furina rank-1 source shared with a non-Furina out-path; the element sigil is genuinely shared UI vocabulary |

Also standing against Furina rows in the live lint (all **allowlisted**, none
failing, `baseline-run-2026-08-26.txt:74-88`):

- **L8 undersize ×6** — `endless_waltz`, `gentilhomme_usher`,
  `mademoiselle_crabaletta`, `full_ensemble`, `supporting_cast` (all 480×270
  Salon Solitaire preview GIFs) and `rapturous_applause` (447×328). Each is
  smaller than the 500×380 card **in both axes**, i.e. upscale blur.
- **L9 banned family ×1** — `curtain_cue`, from the `Ride the Waves to a
  Rendezvous` family: the file is a framed concept-art **page** with the
  GENSHIN IMPACT wordmark above and ©COGNOSPHERE below. Reaching the painting
  needs a manual crop with [USER]'s eyes on it.
- **L6 clip warnings ×4** (never a failure) — `stage_presence` (~61% of source
  height trimmed), `let_the_people_rejoice` (~76%), `the_sea_is_my_stage`
  (~62%), `reginas_mercy` (~62%).
- **L11 generator-owned** — six Furina paths are registered
  (`art_lint.py:421-426`, `:433-435`, `:443`). See §9 F4 for the ones that are not.

---

## 9. Findings — facts, with what each does and does not prove

**F1 — `EB-65`'s stated next action cannot execute as written. (CONFIRMED)**
`docs/current/BACKLOG.md:79` says "**Next action:** apply rank 1, land the
PNGs, commit the sheet. **Gate:** none — R212(1): Claude picks, [USER] vetoes
on the sheet." But **none of the seven has a rank-1 plan row**: every row for
all seven asset ids is rank 2 or 3 (`art/plan.tsv:1123-1136`, verified by
enumerating ranks per asset id). `review/active/art-runs-2026-08-08.md:149-151`
says so explicitly — "Every row is rank 2 or 3; there is no rank 1, so no file
lands and the S12 deferral stays valid." R212(1) authorises *applying* a
shortlist rank 1; it does not authorise *creating* one. **What this does not
establish:** whether promoting an r2 to r1 is inside or outside R212(1). That
reading is [USER]'s, and it is the one thing standing between `EB-65` and a
mechanical close.

**F2 — Two Furina cards have never entered the art pipeline. (CONFIRMED)**
`change_the_bill` and `take_it_from_the_top` have sheet rows
(`docs/furina-cards.yaml:472`, `:622`) and **zero** rows in `art/plan.tsv`
(`grep -c` = 0 for both). They are the two `Win3` additions
(`docs/current/STATE.md:114-115`). Every other Furina card-sized output has at
least two candidates. **What this does not establish:** whether they are worth
hunting now — the 2026-08-08 scarcity note
(`review/active/art-runs-2026-08-08.md:187-200`) says the free Furina pool at
card scale is down to low single digits, so a hunt may legitimately return
empty.

**F3 — Every contact sheet [USER] is asked to look at is currently a page of
broken images. (CONFIRMED)** `art/candidates/` is gitignored
(`.gitignore:15`) and today holds **22 directories, all from the 2026-08-13
Kokomi sweep**. `art/contact_sheet_eb88_energy_orb.html` (the `M19` sheet)
points at `candidates/furina_energy_orb/set_a_fontaine/composed.png` — that
directory **does not exist**. Same for
`contact_sheet_eb54_power_sigils.html` → `candidates/power_furina_unheard_confession/r2.png`,
`contact_sheet_eb54_grand_gala.html`, and `contact_sheet_eb54_eb36.html`.
**Mitigation is cheap and I verified it:** all 14 raw sources for the seven
sigils are present under `art/raw/`, and `gen_energy_orb_layers.py` is
deterministic with no arguments — so re-materialising every Furina sheet is a
tool run, not a fetch. **What this does not establish:** that anyone should
run those tools tonight. [USER] is playtesting and this is a research stream;
I ran nothing.

**F4 — Three Furina generator-owned out-paths are not registered in
`art_lint.GENERATOR_OWNED`. (CONFIRMED, low severity)** `salon/member_*.png`
are written by `tools/cut_salon_members.py:40` and
`model/layers/combat/*.png` plus `model/layers/*.png` by
`tools/cut_combat_layers.py`, but none appears in the L11 table
(`art_lint.py:420-446`), which does list the three salon **glyphs** and the six
`gen_furina_stills.py` outputs. No violation exists today because no plan row
claims those paths (verified: zero `plan.tsv` matches for `model/layers` or
`furina/salon`). The exposure is prospective: L11 exists precisely so a future
plan row cannot quietly claim a generator's out-path, and for these three it
would not fire. **PROPOSED (technical, no design content):** add the entries.
Not done here — this stream writes no repo files.

**F5 — Provenance is complete but keyed two ways. (CONFIRMED, not a defect)**
All 83 Furina card outputs and all 15 present sigils resolve to a
`SOURCES.tsv` row, tier F. But an `auto` pick is keyed by out-path and a
`shortlist` pick by `art/candidates/<id>/rN.png`. Of the 15 sigils, 12 are
keyed at the out-path and 3 (`fanfare`, `standing_ovation`, `ovation_trickle`)
only at the candidate path; **all 83 card outputs** are candidate-keyed —
`SOURCES.tsv` contains **zero** rows under `ImageGen/images/cards/furina/`.
Any Lane-B ledger tool that joins on the out-path alone will report 83 Furina
cards as unsourced when they are fully sourced. That is the one schema fact
worth carrying into `EB-148`.

**F6 — Furina's one live Klee fallback is `ui/transition_wipe.png`.
(CONFIRMED)** She supplies eight of the nine assets in the fill list
(`build_pck.ps1:233-244`); the wipe is the ninth, and sharing it is
sanctioned (`furina-art-pass-requirements.md:407`). The `select_bg` half of
that sanction is **stale** — she has had her own `select_bg.png` (1920×1080,
Furina Banquet namecard) since at least this checkout, so the doc's "currently
`select_bg` and `transition_wipe`" (`:436`) over-counts by one.

**F7 — The `§8` icon bill in the requirements doc no longer names the shipped
files. (CONFIRMED, documentation drift)** `furina-art-pass-requirements.md:453-476`
bills `powers/encore.png`, `burst_meter.png`, `salon_damage_up.png`,
`fanfare_attack.png`, `spotlight_boost.png`, `spotlight_damage.png`,
`spotlight_discount.png`, `spotlight_draw.png`, `ovation_spend_boost.png`,
`spotlight_encore.png`. What ships is `grand_salon.png`,
`rising_ovation.png`, `top_billing.png` / `limelight.png`,
`star_of_the_show.png` / `stage_lights.png`, `leading_role.png`,
`supporting_cast.png`, `standing_ovation.png`, `ovation_trickle.png` — and two
of the doc's rows (`encore`, `burst_meter`) correspond to displays that were
**retired** (`KleePowerIcons.cs:145-149`, `IconExempt` at `:157-162`). The doc
also bills "14 minimum" where 22 are now wired. The live authorities are
`KleePowerIcons.PathFor` and `$pckDeferred`, not the doc.

**F8 — The energy icons are art without a consumer. (CONFIRMED)** Both ship,
both are packed, and `Furina.cs:100-101` routes the counter to the base game's
Ironclad scene, so neither is ever drawn. The blocking work is the **scene**,
not the art — the doc says so at `:418-423` and `M19` is only the layer-set
pick.

---

## 10. NON-FINDINGS and UNKNOWNs

- **NON-FINDING — no Furina provenance hole.** I looked for outputs on disk
  with no source row and found none: 83/83 cards and 15/15 sigils resolve.
- **NON-FINDING — no failing lint against a Furina row.** All Furina lint
  output in the baseline is allowlisted notes and warnings;
  `art_lint: plan OK`, `exit=0`.
- **NON-FINDING — no unintended Klee art on a Furina surface other than the
  wipe.** Eight of nine fill-eligible assets are hers.
- **UNKNOWN — what the Salon stage renders when a member sprite is absent.**
  I did not trace the null path in `SalonVisualsBridge`.
- **UNKNOWN — whether the local pck is the one in the installed 0.2-1155.**
  The contract matches the local pck by sha256; the installed build's identity
  is inside the pack and I did not unpack it.
- **UNKNOWN — eyes-on approval history for the 15 shipped sigils and the 6
  salon rows.** I found sheets and open QUEUE eyes-on rows, but no record of a
  completed approval; "SHIPPED, no recorded eyes-on" in §4a/§5 means exactly
  that, not "rejected".
- **UNKNOWN — rights.** Every category in this file is read off a declared
  tier. No claim here is a rights opinion.
- **UNKNOWN — VFX texture inventory.** `spotlight_shine.tscn` carries no
  `ext_resource`; whether it needs textures it does not declare was not traced.

---

## 11. Numbered questions for [USER]

**No id is minted.** These are pick lists, never blanks. Two of them are
existing register rows restated so a cold read can walk them; the rest are new
questions this census raised, and each is a pick, not a blank.

1. **`EB-65` unblock (new question, blocks an existing BACKLOG row).** The
   seven sigils have no rank 1, so R212(1) has nothing to apply.
   (a) Claude promotes each shortlist r2 to r1 and lands the seven under
   R212(1), veto on the sheet — treating "apply rank 1" as covering "apply the
   top-ranked candidate"; (b) [USER] picks r2-or-r3 per row off a regenerated
   sheet; (c) leave `EB-65` deferred and re-hunt first, accepting that
   `art-runs-2026-08-08.md:197-200` says the free pool is exhausted for this
   brief; (d) re-scope `EB-65` to say what it actually needs.
2. **`change_the_bill` / `take_it_from_the_top` (new).** (a) hunt both now
   and accept whatever the thin pool returns; (b) hunt and accept an empty
   result as a recorded zero; (c) leave both unhunted until a Tier O pass;
   (d) reuse an existing Furina crop deliberately and record the reuse.
3. **Furina contact sheets are unrenderable (new).** (a) re-materialise the
   Furina candidate directories from `art/raw` in a later working session
   before the next art sitting; (b) leave them and review from sources
   directly; (c) change nothing — the sheets are historical records, not live
   review surfaces.
4. **`M19` — energy orb layer set.** Already OPEN and already a pick list at
   `docs/current/QUEUE.md:51`: (1) A Fontaine Hydro (**default**, ships under
   R212(1) if no pick lands), (2) B Opera Pale, (3) C Tidal. **Cited, not
   picked.** Note F8: the layer set does nothing until an energy-counter scene
   exists.
5. **Art debt picks (1) and (3).** Already OPEN at `docs/current/QUEUE.md:53`:
   the `ovation_trickle`/`stagehands_encore` sigil collision, and `grand_gala`
   r6 provisional. §8 C2 confirms the collision is on the **r2 rows** only, so
   it is live only if `stagehands_encore` is filled from r2. **Cited, not
   picked.**
6. **Doc drift, §8 of the requirements (new, hygiene-shaped).** (a) rewrite
   `furina-art-pass-requirements.md:407` and `:453-476` in place to match the
   shipped names and the 22-path bill; (b) leave the doc as the original brief
   and let `KleePowerIcons` + `$pckDeferred` be the only live authority;
   (c) delete the §8 icon table and point at the code. Under CLAUDE.md's
   hygiene norm (a) may be a normal commit rather than a pick — that call is
   [USER]'s and this file makes no edit.

---

*Written on the research rail. No file in the primary checkout was modified,
no art tool was executed, and the game was neither launched nor deployed to.
Disclosure: one read-only `git check-ignore -v` was run in the primary to
confirm `.gitignore` coverage of the pck contract; it mutates nothing, and no
other git command was run anywhere.*
