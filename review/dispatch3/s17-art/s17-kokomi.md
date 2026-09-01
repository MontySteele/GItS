# S17 — art coverage and provenance, family: **Kokomi**

> **This document decides nothing.** It is a draft ledger and a list of
> discrepancies. Every "rights tier" below is a **category read off an existing
> file**, never a rights verdict. Every source pick, taste call, batch schedule
> and scope call remains [USER]'s. Nothing here was generated, rendered,
> re-picked or deployed — this stream ran read-only.

**Date:** 2026-08-26 (overnight, surplus-dispatch-3)
**Family scope:** everything under the `kokomi` namespace — her 76 card faces,
her 7 power icons, her 1 relic icon, the Bake-Kurage summon sprite, and her
character shell (UI / model / materials / scenes).
**Live baseline cited throughout:** `review/dispatch3/s17-art/baseline-run-2026-08-26.txt`
(`art_coverage.py` exit 0, `art_lint.py` exit 0, run read-only on the
art-bearing primary at `main 223a4ff`). The art tools were **not** re-run from
this worktree.

---

## 0. Scope boundary — what is deliberately NOT here

| Excluded | Why | Whose row |
|---|---|---|
| Inazuma companions (15 faces: Gorou 3, Sayu 3, Shinobu 3, Sara 2, Thoma 2, Itto 1, Raiden 1) | S17 fans out by **owner/family**, and companions are their own family. They ship in Kokomi's nation pool but not in her namespace. `art_coverage` bills them **15 / 15 / 0**. | companions owner |
| Klee-namespace and shared UI (`ImageGen/images/ui/`, the six shared aura sigils, `shared/gauge.tscn`, `shared/turn_end_docket.tscn`) | Shared surfaces, not hers | icons/UI/models/VFX owner |
| Furina's 7 `$pckDeferred` power sigils (`klee-mod/build/validate.ps1:903-925`) | Furina family | Furina owner |
| The two `art_lint` L12 identical pairs and the L9 `curtain_cue` ban | Both are Klee/Furina rows | Klee / Furina owners |

**Card art is not total visual coverage.** `art_coverage.py` counts
card-sized outputs only. Beyond her 76 card faces this family owns **24 further
surfaces** — 7 power icons, 1 relic icon, 1 summon sprite, 9 shell rasters and
6 build-authored scenes/materials — and the coverage tool cannot see a single
one of them.

---

## 1. Headline counts (from the live baseline, not from prose)

| Surface class | Expected | Present on disk | Missing | Counted by `art_coverage`? |
|---|---:|---:|---:|---|
| Card portraits (personal sheet) | 76 | 61 | **15** | yes |
| Power icons (`kokomi/powers/`) | 7 | 7 | 0 | **no** |
| Relic icon (`kokomi/relics/`) | 1 | 1 | 0 | **no** |
| Summon sprite (`kokomi/summon/`) | 1 | 1 | 0 | **no** |
| Character shell — UI + model rasters | 9 | 9 | 0 | **no** |
| Build-authored scenes / materials | 6 | 6 | 0 | **no** |
| Animated combat rig (`model/combat.tscn` + `model/layers/`) | 1 + n | **0** | 1 + n | **no** |
| VFX scenes (`kokomi/vfx/`) | UNKNOWN | 0 | UNKNOWN | **no** |
| Stale asset on a `kokomi/` out-path | — | 1 (`swift_currents.png`) | — | listed as STALE, not coverage |

Roster context from the same run: **294 card-sized outputs expected, 270
covered, 24 missing**; Kokomi is **15 of those 24** — just under two-thirds of
the entire roster's outstanding card-art bill.

---

## 2. The draft ledger

Columns are the ones S17 asks for. `packed path` distinguishes the **two
completely different shipping routes** this mod uses:

- **Route A — loose PNG, no pck.** `klee-mod/build/deploy.ps1:109-138` copies
  `ImageGen/images/cards/{klee,furina,kokomi,companions}/*.png` into ONE FLAT
  directory `<mod>/images/cards/`, and `RosterArt.CardPortrait` reads
  `images/cards/<sheet_id>.png` at runtime (`klee-mod/KleeCode/KleeArt.cs:55-81`).
  Card ids are globally unique so the flattening is safe.
- **Route B — `res://` inside `klee.pck`.** `tools/build_pck.ps1:204-215` copies
  `ImageGen/images/kokomi/{ui,powers,relics,model}/*.png`;
  `:178-185` copies `kokomi\summon` separately; `:254-278` fills any of nine
  named UI/model relatives from Klee if hers is absent (`Copy-KokomiFallback`).

### 2a. Card portraits — 76 expected, 61 present, 15 missing

All 61 present faces are 500×380 RGBA under
`ImageGen/images/cards/kokomi/`, all deployed (I counted **272** PNGs in the
live `<game>\mods\klee\images\cards`, which is exactly 270 covered + the 2
STALE files, so the staging is complete and the stale pair ships too).

**The 15 missing, with their state:**

| # | id | rarity | rank-1 source (plan) | candidates on disk | `SOURCES.tsv` row | blocking unknown |
|---|---|---|---|---|---|---|
| 1 | `the_gunbai_turns` | rare | Character Card Golden | r1,r2,r3 | **none** | pick not applied |
| 2 | `all_hands` | rare | Character Card Golden | r1,r2,r3 | **none** | pick not applied |
| 3 | `what_the_tokoyo_took` | rare | Character Card Golden | r1,r2,r3 | **none** | pick not applied |
| 4 | `gyorin_formation` | rare | Character Card Golden | r1,r2,r3 | **none** | pick not applied |
| 5 | `council_at_bourou` | uncommon | Character Card Golden | r1,r2,r3 | **none** | pick not applied |
| 6 | `open_the_stores` | uncommon | Character Card Golden | r1,r2,r3 | **none** | pick not applied |
| 7 | `wheel_the_ranks` | uncommon | Expression 3 | r1,r2,r3 | **none** | pick not applied |
| 8 | `what_the_tokoyo_returns` | uncommon | P. Paintings 39 | r1,r2,r3 | **none** | pick not applied |
| 9 | `raise_the_sashimono` | uncommon | Character Card Platinum | r1,r2,r3 | **none** | pick not applied |
| 10 | `crane_wing` | uncommon | Wish | r1,r2,r3 | **none** | pick not applied |
| 11 | `send_the_runner` | common | Wish | r1,r2,r3 | **none** | pick not applied |
| 12 | `massed_volley` | common | Full Wish | r1,r2,r3 | **none** | pick not applied |
| 13 | `hold_the_narrows` | common | Profile | r1,r2,r3 | **none** | pick not applied |
| 14 | `tighten_the_cords` | common | Bake-Kurage Summon | r1,r2,r3 | **none** | pick not applied |
| 15 | `watch_of_the_shallows` | uncommon | **NO RANK 1 EXISTS** (ranks 2/3/4 only) | **none** | 3 rows, stale | **[USER] pick required — `art_process` cannot promote anything** |

Rows 1–14 are `EB-69`'s fourteen pool-fill faces, shortlisted under `EB-121`
(`art/plan.tsv:1155-1197`, contact sheet
`art/contact_sheet_eb121_kokomi_fill.html`, written 2026-08-26 16:08 — I
verified it carries exactly those 14 ids and no others). Rarity read from
`docs/kokomi-cards.yaml`.

Row 15 is different in kind and the plan says so in a comment
(`art/plan.tsv:1145-1151`): `watch_of_the_shallows` arrived after the Kokomi art
pass and was **deliberately given no rank 1**, because `art_process` promotes
rank 1 automatically and a rank 1 would have made a pick nobody made. It has 3
`SOURCES.tsv` rows from the 2026-08-13 run
(`art/contact_sheet_run9_watch_of_the_shallows.html`) but
`art/candidates/watch_of_the_shallows/` **does not exist on disk any more**, so
even the sheet it cites has no pixels behind it today.

**Fallback for all 15:** the base-game BETA placeholder portrait.
`RosterArt.CardPortrait` logs `No card art at <path>` and returns null
(`KleeArt.cs:76-79`); nothing fails. This is the invisible-failure shape the
Kokomi requirements doc already warns about
(`docs/current/art/kokomi-art-pass-requirements.md` §1: *"the game renders the
BETA placeholder for an unplanned face and NOTHING fails"*).

**Rights tier category for every one of the 61 present + 15 planned:**
`private-placeholder`. Every `art/SOURCES.tsv` row that covers a Kokomi
candidate carries `tier = F`; `docs/current/OPERATIONS.md:296` states Tier F art
never ships and never enters the repo.

### 2b. Stale card asset on a Kokomi out-path — 1

| out-path | state | evidence |
|---|---|---|
| `ImageGen/images/cards/kokomi/swift_currents.png` | **rendered, staged, deployed, and read by nothing** | `docs/kokomi-cards.yaml:462` — *"swift_currents: MERGED INTO moonlit_offering (G8, [USER], this pass)"*. `art/plan.tsv:935-937` still carries a live 3-rank shortlist for it. The baseline run lists it under **STALE (files with no sheet row — NOT coverage)**. I confirmed the file is present in the deployed mod at `<game>\mods\klee\images\cards\swift_currents.png`. |

Not a defect by itself — the STALE note explains the keep-don't-delete decision
— but it is a live plan row for a card that does not exist, and it does reach
the shipped build.

### 2c. Power icons — 7 of 7 present

All seven are **256×256 RGBA**, `ImageGen/images/kokomi/powers/`, written
2026-08-26 20:34. Packed as `res://kokomi/powers/<name>.png`
(`klee-mod/assets/klee.pck.contract.txt`, and confirmed present in the
**deployed** contract at `<game>\mods\klee\klee.pck.contract.txt`).

| out file | worn by | wired at | rank-1 source | rights tier |
|---|---|---|---|---|
| `bake_kurage.png` | `KurageSummonPower` badge | `KleePowerIcons.cs:125` | Bake-Kurage Summon.png | private-placeholder |
| `kurages_oath.png` | `KurageWardPower` | `KleePowerIcons.cs:126` | Talent Kurage's Oath.png | private-placeholder |
| `before_sun_and_moon.png` | `KurageAmpPower` | `KleePowerIcons.cs:127` | Kokomi Vision.png (tight crop) | private-placeholder |
| `ceremonial_garment.png` | `CeremonialGarmentPower` | `KleePowerIcons.cs:128-129` | Ceremonial Garment Buff Icon.png | private-placeholder |
| `vigil_of_the_deep.png` | `PreventExhaustWardPower` | `KleePowerIcons.cs:130-131` | Namecard BG …The Deep.png | private-placeholder |
| `princess_of_watatsumi.png` | `ChargePerTurnPower` | `KleePowerIcons.cs:132-133` | Talent Princess of Watatsumi.png | private-placeholder |
| `pearl.png` | **not a status badge** — the cap icon on her Burst gauge | `klee-mod/KleeCode/Vfx/GaugeBridge.cs:173` (`CapIconPath`) | Item Sango Pearl Wild.png | private-placeholder |

**Fallback:** `KleePowerIcons.PathFor` ends in `_ => null`, and a null there
renders the base game's `NOPE` placeholder — that is the defect `EB-67` was
opened on (`review/records/eb67-kokomi-icons-2026-08-26.md` §1). There is no
Klee-borrowing fallback for `powers/`; `Copy-KokomiFallback` covers only the
nine UI/model relatives listed at `tools/build_pck.ps1:268-276`.

**No unwired Kokomi power remains.** `EB-67` §7 lists seven powers still with no
icon mapping (`AncientSeaAuthorityPower`, `CannonFireSupportPower`,
`ExplosivesWorkshopPower`, `MasqueRedDeathPower`, `MetallicizePower`,
`NightVigilPower`, `SalonCapUpPower`) and **none of them is Kokomi's** — four
Fontaine companions, one Furina salon, two Klee. Recorded here only so the
Kokomi family is not blamed for them; filing is not this stream's call.

### 2d. Relic icon — 1 file, 2 relics

| out file | worn by | wired at | source | collision state |
|---|---|---|---|---|
| `ImageGen/images/kokomi/relics/pearl_of_wisdom.png` (256×256 RGBA) | **Pearl of Wisdom** AND its upgrade **Pearl of Insight** | `PearlOfWisdomRelic.cs:99,102`; `UpgradedStarterRelics.cs:329,332` | Item Sango Pearl.png, `contain@center`, used at native 256×256 with no resample | **two ids, one file — sanctioned**, the same arrangement Klee's Pounding Surprise and Furina's Ethereal Spotlight already use |

Packed as `res://kokomi/relics/pearl_of_wisdom.png`.
**Declared fallback:** `?? base.PackedIconPath` / `?? base.BigIconPath`, with
`IconBaseName => "snake_ring"` and a comment naming it *"FALLBACK ICON while
her art pass is outstanding"* (`PearlOfWisdomRelic.cs:90-96`). See §7 Q1 — the
declared fallback and the observed live behaviour disagree.

### 2e. Bake-Kurage summon sprite — 1

| field | value |
|---|---|
| out | `ImageGen/images/kokomi/summon/bake_kurage.png`, **64×128 RGBA** |
| producer | `tools/cut_kurage_summon.py` — a **generator**, not a plan row; registered at `tools/art_lint.py:436` so no plan row may claim the path (L11) |
| sidecar | `kurage.json` (`{"target_h":128,"sprite":{"file":"bake_kurage.png","w":64,"h":128}}`) — written by the same generator, and **does not ship**: the summon copy block at `tools/build_pck.ps1:182-185` copies `*.png` only |
| packed | `res://kokomi/summon/bake_kurage.png` — its OWN namespace, not `powers/`, because it is a creature on the field rather than a status badge (`tools/build_pck.ps1:173-177`) |
| consumer | `klee-mod/KleeCode/Powers/TurnEndAttribution.cs:129` (`KurageSprite`), the end-of-turn attribution docket |
| fallback | **graceful and deliberate**: a null path hides the sprite and the numbered chip still renders. `TurnEndAttribution.cs:126-127` — *"an absent file cannot produce a NOPE placeholder here — it produces a number with no picture, which is the degradation we want."* |
| collision | **distinct file from `kokomi/powers/bake_kurage.png`** — same name, different size, different job, both ship. Flagged in `KleePowerIcons.cs:120-124` so the pair is not mistaken for a duplicate. |
| rights tier | private-placeholder (cut from `Bake-Kurage Summon.png`, Tier F) |

### 2f. Character shell — 9 rasters + 6 build-authored resources

Track marked **DONE 2026-07-25** in
`docs/current/art/kokomi-art-pass-requirements.md` §5a (commit `68fb11b`).

| out | dims | producer | packed path | fallback | rights tier |
|---|---|---|---|---|---|
| `ui/select_portrait.png` | 132×195 | `gen_kokomi_stills.py` (`art_lint.py:428`) | `res://kokomi/ui/select_portrait.png` | Klee's, via `Copy-KokomiFallback` | private-placeholder |
| `ui/select_portrait_locked.png` | 132×195 | derived from the portrait (`art_lint.py:429`) | `res://kokomi/ui/select_portrait_locked.png` | Klee's | private-placeholder |
| `ui/char_icon.png` | 88×88 | `gen_kokomi_stills.py` (`art_lint.py:431`) | `res://kokomi/ui/char_icon.png` | Klee's | private-placeholder |
| `ui/char_icon_outline.png` | 88×88 | `gen_char_icon_outlines.py` (`art_lint.py:444`) — derived from her own `char_icon.png` | `res://kokomi/ui/char_icon_outline.png` | Klee's | derived → private-placeholder |
| `ui/map_marker.png` | 49×64 | `gen_kokomi_stills.py` (`art_lint.py:432`) | `res://kokomi/ui/map_marker.png` | Klee's | private-placeholder |
| `ui/selection_splash.png` | 1920×1200 (only 1080 rows visible — §5a note 3) | `gen_kokomi_stills.py` (`art_lint.py:430`) | `res://kokomi/ui/selection_splash.png` | Klee's | private-placeholder |
| `ui/select_bg.png` | 1920×1080 | **`art_process`** — the ONLY Kokomi plan row for a shell surface (`art/plan.tsv:975`, `kokomi_select_bg`, `auto`, Namecard BG …The Deep) | `res://kokomi/ui/select_bg.png` | Klee's | private-placeholder — **and the only Kokomi output with a real `SOURCES.tsv` provenance row**, tier `F` |
| `ui/transition_wipe.png` | 960×540, mode **L** | `gen_transition_wipe.py` (`art_lint.py:438`), **procedural, fixed seed** | `res://kokomi/ui/transition_wipe.png` | Klee's | **public-safe** — the generator's own docstring says *"Tier O, procedural"* (`tools/gen_transition_wipe.py:1`). Note Furina deliberately has none and keeps Klee's; Kokomi has her own ("a tide coming in"). |
| `model/combat_model.png` | 240×280 | `gen_kokomi_stills.py` (`art_lint.py:427`) | `res://kokomi/model/combat_model.png` | Klee's | private-placeholder |

Working cache, correctly **excluded** from the pck:
`ImageGen/images/kokomi/model/kokomi_portrait_cutout.png`, 4900×5700, **8.6 MB**
— filtered by the `*_cutout.png` suffix rule at `tools/build_pck.ps1:186-212`,
a rule written because shipping it once nearly doubled an 8.3 MB pack.

Build-authored (no art file, written as text by `build_pck.ps1` at pack time):
`kokomi/ui/char_select_bg_kokomi.tscn` (:378), `kokomi/ui/character_icon.tscn`
(:461), `kokomi/model/combat_visuals.tscn` (:551),
`kokomi/model/rest_character.tscn` (:560),
`kokomi/model/merchant_character.tscn` (:569),
`kokomi/materials/kokomi_transition_mat.tres` (:702).

### 2g. Surfaces Kokomi does **not** have

| surface | Klee | Furina | Kokomi | status |
|---|---|---|---|---|
| `model/combat.tscn` (animated combat rig) | yes | yes | **no** | **EXPECTED MISSING, declared in code.** `KleeSceneTelemetry.cs:39-44` lists it precisely so the miss is logged at boot; `Kokomi.cs:140-152` refuses to write a `?? ` chain naming a resource nothing produces; `Kokomi.cs:174-197` runs the static `combat_model.png` path instead. `validate.ps1:948-960` excludes `KleeSceneTelemetry.cs` from S12 as a **probe** file so this absence cannot fail a build. |
| `model/layers/*.png` (cut combat layers) | 5 | 4 | **0** | follows from the above — no rig, no layers, no `Facing`, no `AnimationTree` |
| `vfx/*.tscn` | 2 (`bomb_lob`, `dodoco_pop`) | 1 (`spotlight_shine`) | **0** | **UNKNOWN whether any is owed.** No Kokomi C# references a `kokomi/vfx/` path, so nothing is broken; whether her kit *wants* one is a design question, not a coverage fact. |
| `ui/energy_icon_22.png` / `_74.png` | yes | yes | **no** | **NOT a gap.** All three characters set `CustomEnergyCounterPath` to the base game's `res://scenes/combat/energy_counters/ironclad_energy_counter.tscn` (`Klee.cs:175-176`, `Furina.cs:100-101`, `Kokomi.cs:155-156`), and a repo-wide search finds **zero** consumers of `energy_icon_*.png` in any `.cs`, `.ps1`, `.py` or `.tscn`. The Klee and Furina files are packed and unread. Kokomi's absence is consistent, not deficient. |

---

## 3. Rights tier — as a category only

| category | count | basis |
|---|---:|---|
| `private-placeholder` | 99 of her 100 surfaces (76 card faces + 23 of the 24 non-card) | every `art/SOURCES.tsv` row touching a Kokomi output carries `tier = F`; `docs/current/OPERATIONS.md:296` and `docs/current/art/kokomi-art-pass-requirements.md` §1 (*"Tier F (found/official) is private-playtest only; a public build needs Tier O"*) |
| `public-safe` | 1 (`ui/transition_wipe.png`) | `tools/gen_transition_wipe.py:1` declares Tier O, procedural, deterministic |
| `UNKNOWN` | the 22 asset ids in §4 | no `SOURCES.tsv` row exists for them at any rank |

**No rights verdict is offered or implied.** The public/private split is
[USER]'s and the governing principles file
(`teyvat-spire-design-principles.md` §9) is not in HEAD — it is retired to git
history, and `OPERATIONS.md:296` is the standing restatement.

---

## 4. **Provenance gap — 22 Kokomi asset ids have no `SOURCES.tsv` row at any rank**

This is the most substantive finding of this stream.

`art/SOURCES.tsv` is written **only** by `tools/art_fetch.py:183-216`, and it
keys a shortlist row on `art/candidates/<asset_id>/r<rank>.png`. It is one of
only two tracked art ledgers — `art/raw/`, `art/candidates/` and
`ImageGen/images/` are all gitignored (`.gitignore`, "Tier F art … Only the
ledgers (SOURCES.tsv, plan.tsv) and tools are tracked").

So `SOURCES.tsv` is **the only tracked record of the URL a shipped pixel came
from**. For 22 Kokomi ids that record does not exist:

| group | ids | on disk | consequence |
|---|---|---|---|
| the 8 `EB-67` icons | `relic_pearl_of_wisdom`, `power_kokomi_pearl`, `power_kokomi_bake_kurage`, `power_kokomi_kurages_oath`, `power_kokomi_before_sun_and_moon`, `power_kokomi_ceremonial_garment`, `power_kokomi_vigil_of_the_deep`, `power_kokomi_princess_of_watatsumi` | **rendered, packed, and in the DEPLOYED build** | shipped pixels whose only tracked provenance is a wiki **title string** in `art/plan.tsv:1236-1259`, not a pinned URL |
| the 14 `EB-69`/`EB-121` fill faces | rows 1–14 of §2a | candidates rendered, not applied | same, one step earlier |

**Why it happened (verified, not guessed):** every raw source these 22 rows need
is already in `art/raw/` from the July hunt — I checked all 42 distinct rank-1..3
sources and **every one is present**. `art_fetch` therefore never had to run
after the new plan rows landed, and `art_fetch` is the only writer of
`SOURCES.tsv`. `art_process` renders happily from `art/raw/` without it. Nothing
in the gate notices: `art_lint` exits 0, `art_coverage` exits 0, `validate.ps1`
S12 passes.

For contrast, of the 86 Kokomi asset ids in `art/plan.tsv`, exactly **one** —
`kokomi_select_bg` — has a `SOURCES.tsv` row against its own out-path, and only
because it is an `auto` row rather than a `shortlist` row.

**This is a candidate confirmed-defect for BACKLOG triage, not a filing.** It is
also a direct, ready-made requirement for **tool lane B** (`EB-148`): a ledger
that joins expected surface → source → output → packed path would fail here
today.

---

## 5. Collision and duplicate state

### 5a. Byte-identical outputs: **NONE**

I hashed every shipped Kokomi output (61 card faces + 9 shell rasters + 7 power
icons + 1 relic + 1 summon). **Zero duplicate groups.** The two `L12` identical
pairs in the baseline `art_lint` run (`crowd_work == standing_ovation`,
`catalytic_conversion == spark_collection`) are both Furina/Klee.

### 5b. Shared-source collisions that the lint does not police

`art_lint`'s L1/L7 dedupe applies **only to rows whose out-path contains
`/cards/`** (`tools/art_lint.py:320-323`). The eight `EB-67` icon rows and
`kokomi_select_bg` are outside it entirely, which is why these are green:

| shared source | ids | governed by L1/L7? |
|---|---|---|
| `Item Sango Pearl.png` | `relic_pearl_of_wisdom` (icon) + `ritual_purification` (card) | **no** — icon row is out of scope |
| `Item Sango Pearl Wild.png` | `power_kokomi_pearl` (icon) + `cleansing_tide` (card) | **no** |
| `Sangonomiya Kokomi Vision.png` | `power_kokomi_before_sun_and_moon` (icon) + `pearl_diver` (card) | **no** |
| `Namecard BG …The Deep.png` | `power_kokomi_vigil_of_the_deep` (icon) + `kokomi_select_bg` (UI) + `ebb_tide` (card) | **no** — the plan comment at `art/plan.tsv:1057` records this as deliberate |
| `Bake-Kurage Summon.png` | `power_kokomi_bake_kurage` (icon) + `before_sun_and_moon` (card) + `tighten_the_cords` (card) | partially — only the two card rows are in scope |

None of these is a defect. They are recorded because a joined ledger has to
decide whether "one source, one card **and** one icon" counts as reuse.

### 5c. Card-face source concentration — **all 77 Kokomi card rows carry `source_group = kokomi_pool`**

Measured from `art/plan.tsv` (231 rows / 3 ranks = 77 ids, **zero blank**).
`source_group` is column 13 (`tools/art_fetch.py:66-74`). A group relaxes strict
L1 to L7: siblings may share a source **provided the crop differs**
(`tools/art_lint.py:331-347`).

Rank-1 concentration, all legal under L7:

| source | ids on it |
|---|---:|
| Sangonomiya Kokomi Character Card Golden.png | 7 |
| Sangonomiya Kokomi Card.png | 6 |
| Character Sangonomiya Kokomi Game.png | 6 |
| Character Card Showcase.png | 6 |
| Sangonomiya Kokomi Character Card.png | 6 |
| Character Card Platinum.png | 6 |
| Sangonomiya Kokomi Wish.png | 6 |
| Sangonomiya Kokomi Portrait.png | 5 |
| Introduction Card.jpg / Full Wish.png / The Deep.png | 3 each |

**The comparison that makes this a question, not a fact:** Furina's
source-uniqueness rule was **amended and ratified 2026-07-23** and is
rarity-scoped (`docs/current/art/furina-art-pass-requirements.md:100-116`):

- basics + rares (20 cards) — **STRICT**, blank `source_group`, one unique
  source each;
- commons + uncommons (56) — pooled as `furina_pool`, crop must differ.

Kokomi has **no equivalent split**. Her 5 basics and 14 rares are all in
`kokomi_pool`, and concretely:

| identity cards | share this one source | crops |
|---|---|---|
| **all 5 basics** — `waters_edge`, `coral_guard`, `bake_kurage`, `tactical_retreat`, `tide_reading` | `Sangonomiya Kokomi Portrait.png` | `cover@y0.33 / 0.41 / 0.50 / 0.59 / 0.67` |
| 4 rares — `the_gunbai_turns`, `all_hands`, `what_the_tokoyo_took`, `gyorin_formation` | `Character Card Golden.png` | `cover@y0.22 / 0.33 / 0.44 / 0.56` |
| 4 rares — `sango_prayer`, `vigil_of_the_deep`, `epiphany_of_the_deep`, `prayer_to_the_moon` | `Sangonomiya Kokomi Wish.png` | `cover@x0.47 / 0.53 / 0.33 / 0.40` |
| 2 rares — `honor_guard`, `grand_conscription` | `Character Card Platinum.png` | `cover@y0.22 / 0.67` |
| 2 rares — `ceremonial_garment`, `depths_judgment` | `Character Sangonomiya Kokomi Full Wish.png` | `cover@y0.38 / 0.62` |

Under Furina's ratified regime, **12 of Kokomi's 19 identity cards would be L1
violations**. Under her own plan they are green.

This is very likely **deliberate** — her requirements doc §2 rules crop reuse
mandatory against 34 sources for 76 faces — but **it was never written down as
a rarity-scoped rule the way Furina's was**, and her §6 open question 1 (*"Crop
reuse budget — this is now the load-bearing question"*) has **never been
answered**. This is a design/taste call and therefore [USER]'s: see §7 Q2.

### 5d. One source is over its computed budget

`docs/current/art/kokomi-source-census.tsv` reports
`Sangonomiya Kokomi Wish.png` at **slots 5, claimed 6** — one anchor past what
its own geometry supports, with an empty `free_anchors` column. The
requirements doc §2 already names this source as the one whose shipped anchors
sit off-grid (`x0.33/0.40/0.47/0.53`, clustered in the low half of a range that
runs to `0.67`). Recorded, not judged.

Headroom that does exist, from the same census:
`Multi Wish.png` 6 free, `Bake-Kurage Summon.png` 4 free,
`Namecard BG …The Deep.png` 4 free, `Profile.png` 2 free,
`Expression 1.png` and `Side by Side…Kokomi.png` 1 each — **18 free
(source, anchor) slots against 15 missing faces.**

---

## 6. Review state

| item | state | evidence |
|---|---|---|
| Kokomi's 61 shipped faces | **provisional rank-1 picks applied; [USER] taste pass NOT taken** | `kokomi-art-pass-requirements.md` §1 and the QUEUE "Art debt" row (`docs/current/QUEUE.md:53`, OPEN — taste). Sheets: `art/contact_sheet_kokomi-{identity,commander,priest,assist}.html`, all written 2026-08-13 01:31 |
| The 14 `EB-69` fill faces | **shortlisted and rendered, rank 1 is a PROPOSAL not a provisional pick, NOT applied** | requirements §1; `art/contact_sheet_eb121_kokomi_fill.html` (2026-08-26 16:08) |
| `watch_of_the_shallows` | **candidate set only, no rank 1 by design** | `art/plan.tsv:1145-1154`; `review/ruled/art-runs-2026-08-08.md:293-297` (run 9a); sheet `art/contact_sheet_run9_watch_of_the_shallows.html` |
| The 8 `EB-67` icons | **rank 1 APPLIED under R212(1); [USER] veto still open on the sheet; acceptance is ONE live look, not taken** | `docs/current/BACKLOG.md:80`; `review/records/eb67-kokomi-icons-2026-08-26.md` §§2,5,6; sheet `art/contact_sheet_eb67_kokomi_icons.html` (2026-08-26 19:50, verified to carry exactly those 8 ids) |
| Character shell (9 surfaces) | **DONE 2026-07-25**, commit `68fb11b`, picks applied at `6f1b969` | requirements §5a |
| `Character Details 1` manual crop for a Rare | **OPEN — [USER] taste**, L9's one named exception | `docs/current/QUEUE.md:53` pick (2); requirements §2 and §6 Q3 |
| `art-runs-2026-08-08.md` Kokomi rows | **REVIEW BUNDLE — "No pick was made and no pick may be read into these files"** | that file's header, lines 3-5 |

---

## 7. Open questions — numbered, for [USER] or the S17 integrator. **No option is recommended.**

**Q1 — the relic fallback disagrees with itself.**
`PearlOfWisdomRelic.cs:90-96` declares a working fallback: `IconBaseName =
"snake_ring"`, a real Silent relic icon, described in its own doc comment as
*"FALLBACK ICON while her art pass is outstanding"*. But the 2026-08-08 live
capture that opened `EB-67` recorded the Pearl of Wisdom relic drawing `NOPE`
(`review/records/eb67-kokomi-icons-2026-08-26.md` §1). Both cannot be right.
Pick: (1) the live look that closes `EB-67` settles it and nothing else is
needed; (2) treat the declared fallback as untrusted and open a row.
*Not resolvable from source — it needs the game.*

**Q2 — Kokomi's source-uniqueness rule was never written.**
Furina's is rarity-scoped and ratified (basics+rares strict, commons+uncommons
pooled). Kokomi's 77 card rows are pooled without exception, putting all 5
basics on one source and 12 of 19 identity cards on shared sources (§5c). Pick:
(1) ratify character-wide pooling for Kokomi as-is, and say so in her
requirements doc; (2) adopt Furina's rarity split for her too, and accept that
re-crops are owed on up to 12 identity faces; (3) something between — e.g.
strict on the 5 basics only. **This is the same question as her §6 Q1 crop-reuse
budget, which has never been answered.**

**Q3 — `swift_currents` (§2b).** A merged-away card keeps a live 3-rank plan
row and a rendered PNG that ships to the game. Pick: (1) leave it — the STALE
note already explains the keep; (2) comment the plan row out and let the file
stay on disk; (3) retire both.

**Q4 — does Kokomi's kit want a `vfx/` scene?** Klee has 2, Furina 1, Kokomi 0,
and nothing is broken. Pick: (1) none owed; (2) name the cues and let S19/lane A
price them. *This is a design question and it is stated only as a question.*

---

## 8. UNKNOWN / NON-FINDING

- **NON-FINDING:** no byte-identical Kokomi outputs (§5a).
- **NON-FINDING:** no Kokomi power, relic or shell surface is referenced in C#
  and absent from the pck. `validate.ps1:984-1001` fails the deploy in **both**
  directions, and Kokomi's two former `$pckDeferred` entries are gone from the
  list at `validate.ps1:892-925` — which is only legal if the art landed.
- **NON-FINDING:** the missing `ui/energy_icon_*` is not a gap (§2g).
- **UNKNOWN:** whether a Kokomi `vfx/` scene is owed (Q4).
- **UNKNOWN:** the real fallback the relic icon takes (Q1).
- **UNKNOWN:** whether `kokomi_pool` on all 77 rows is a sanctioned exemption or
  an unwritten one (Q2).
- **UNKNOWN:** whether `art/candidates/watch_of_the_shallows/` was cleaned
  deliberately or lost. Its 3 `SOURCES.tsv` rows survive; the pixels do not.
- **Search boundary:** I read `art/plan.tsv`, `art/SOURCES.tsv`,
  `docs/current/art/*`, `docs/kokomi-cards.yaml`, `tools/art_*.py`,
  `tools/build_pck.ps1`, `klee-mod/build/{deploy,validate}.ps1`, the
  `klee-mod/KleeCode` files that name a `kokomi/` path, and the files on disk
  under `ImageGen/images/kokomi*`, `art/raw/`, `art/candidates/`. I did **not**
  read git history, did not run any art tool, and did not open any image.

---

## 9. In-flight tonight — `EB-67`, NOT duplicated here

`EB-67` is being produced on its own branch tonight (sibling worktree
`../GItS-eb67` exists). This stream **duplicated none of it**. What I observed
read-only, with timestamps, because it changes what a morning reader will see:

| time (2026-08-26) | observation |
|---|---|
| 16:08 | `art/contact_sheet_eb121_kokomi_fill.html` written (the 14 fill faces) |
| 19:44–19:48 | `art/candidates/{relic_pearl_of_wisdom,power_kokomi_*}/r1..r3.png` written |
| 19:50 | `art/contact_sheet_eb67_kokomi_icons.html` written |
| 20:34 | the 8 rank-1 icons applied to `ImageGen/images/kokomi/{powers,relics}/`; `art/picks.tsv` holds exactly those 8 ids at rank 1 |
| 20:39 | `klee-mod/assets/klee.pck` + contract rebuilt; contract gained all 8 `kokomi/` icon resources |
| ~20:46–20:51 | deployed: `<game>\mods\klee\manifest.json` reads **`0.2-1159`** (preflight recorded [USER] playtesting on `0.2-1155`), and the deployed contract carries the 8 icons |

The `EB-67` C# arm is present in the primary at
`klee-mod/KleeCode/Powers/KleePowerIcons.cs:112-133`, and Kokomi's two entries
are **gone** from `validate.ps1`'s `$pckDeferred`. Since S12 fails a deploy on
a stale exemption in either direction, the successful deploy is itself evidence
the pck arm landed. **The one thing `EB-67` still owes — the live look — is
unchanged and is not something this stream can take.**

---

## 10. What this document does **NOT** establish

It does not establish that any pick is good, that any source may be
distributed, that any rarity split should change, that `kokomi_pool` is wrong,
that a VFX scene is owed, or that Kokomi's art bill should be scheduled ahead of
anything else. It records what is on disk, what the tracked ledgers say, what
the code loads, and where those three disagree. Every disagreement above is
either a numbered question for [USER] or a candidate row for BACKLOG triage by
someone with the authority to file one — and this stream filed nothing, minted
no id, and changed no file outside `review/dispatch3/`.
