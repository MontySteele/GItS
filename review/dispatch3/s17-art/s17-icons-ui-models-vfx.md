# S17 — art coverage and provenance: **icons, UI, models, VFX**

> **This decides nothing.** It is an inventory with citations. It assigns no
> rights verdict (rights tier appears only as a three-value CATEGORY), makes no
> taste call, picks no source, and generated no images. Every technical note is
> `PROPOSED` or a bare fact. Numbered pick lists at the end are [USER]'s.
>
> **Family scope:** everything in the mod's visual surface that is **not** a
> card portrait and **not** a character-owned card badge — power/status icons,
> relic icons, character-shell UI, transitions, energy counter, models and
> combat rigs, summons and field entities, shared UI scenes, VFX, fonts.
> Cross-character and cross-*game* fallbacks are first-class rows here.
>
> **What this does NOT establish.** It does not prove any surface *looks* right
> — no eyes-on was taken and none may be. It does not measure anything, open a
> window, or interpret [USER]'s playtest. It does not settle whether a shared
> source is acceptable, whether a fallback should be extended, or whether any
> asset may ship publicly. Where a claim needed the running game, it is either
> quoted from a log [USER]'s own session already wrote, or marked UNKNOWN.

---

## 0. Read record

| item | value |
|---|---|
| Live tool baseline (cited, not re-run) | `review/dispatch3/s17-art/baseline-run-2026-08-26.txt` — `art_coverage.py` **exit 0**, `art_lint.py` **exit 0** ("plan OK"), taken **19:51** against `main 223a4ff`, working tree clean |
| Primary checkout `main` when this file was written | `794c065` — read from `C:\Users\Monty\Documents\GitHub\GItS\.git\HEAD` and `.git\refs\heads\main` as **files**. No git command was run in the primary. It has moved since PREFLIGHT recorded `223a4ff`. |
| Deployed / built PCK | `klee-mod\assets\klee.pck` **9,586,076 bytes**, built **2026-08-26 20:46**; contract `roster-pck-v3`, `sha256=70B227FB…D60468`, **132 resources**. The game's own log confirms the same pack is live: `pck build id: 20260826-204650+98fb3a0`. |
| Runtime evidence | `C:\Users\Monty\AppData\Roaming\SlayTheSpire2\logs\godot.log` and `godot2026-08-26T20.56.20.log`, read-only. The game was **not** launched by this stream. |
| Read window | 2026-08-26 ~22:30–22:55 local |

**THE TREE MOVED UNDER THE BASELINE, AND THIS FAMILY IS WHERE IT MOVED.**
`art/plan.tsv` was modified at **20:15**, `art/picks.tsv` written at **20:18**,
and eight Kokomi icon outputs landed at **20:34** — all *after* the 19:51
baseline. So the cited `art_lint` "plan OK" was taken against a `plan.tsv` that
no longer exists, and the cited `art_coverage` totals predate the icon landing.
Card totals are unaffected (the eight are not cards). Every icon-family claim
below is read from the **current** files, not from the baseline, and says so.

---

## 1. The one-paragraph shape of this family

The mod's non-card visual surface is delivered by exactly one artifact: the
**PCK**, `res://` paths merged into the game at mod-read time
(`klee-mod/KleeCode/KleePck.cs:7-25`). **All 132 packed resources belong to this
family — zero card portraits are in the pack**; card art ships as loose PNGs
next to the DLL (`KleeArt.cs:9-21`, `klee-mod/build/deploy.ps1:109-142`). So
"card art coverage" and "this family's coverage" are measured by two different
mechanisms that share no tooling, and **only the card half has a coverage tool**
(§8).

Packed resource count by namespace (from `klee-mod/assets/klee.pck.contract.txt`):

| namespace | count | | namespace | count | | namespace | count |
|---|---:|---|---|---:|---|---|---:|
| `klee/powers` | 29 | | `furina/powers` | 15 | | `kokomi/ui` | 10 |
| `klee/ui` | 12 | | `furina/ui` | 13 | | `kokomi/powers` | 7 |
| `klee/model` | 12 | | `furina/model` | 9 | | `kokomi/model` | 4 |
| `klee/vfx` | 2 | | `furina/salon` | 6 | | `kokomi/summon` | 1 |
| `klee/localization` | 2 | | `furina/vfx` | 1 | | `kokomi/relics` | 1 |
| `klee/relics` | 1 | | `furina/relics` | 1 | | `kokomi/materials` | 1 |
| `klee/materials` | 1 | | `furina/materials` | 1 | | `shared/` | 2 |
| `klee/build_id.tres` | 1 | | | | | **total** | **132** |

**Fonts: NON-FINDING.** Zero `.ttf`/`.otf`/`.fnt` in the contract, and zero
audio (`.ogg`/`.wav`) — grep over the contract returns 0. The mod ships no font
and no audio file of any kind. Audio is referenced only as FMOD event *paths*
into the base game (§6).

---

## 2. Ledger — power and status badge icons

**Expected ids are DERIVED, not listed:** every one is a `KleePck.Path(...)`
literal in `klee-mod/KleeCode/Powers/KleePowerIcons.cs`. Rendered outputs live
under `ImageGen/images/**` (gitignored). Packed path = `res://<same relative
path>`. Rights tier is **private-placeholder** for every row in this section
(§7). Fallback for every row is identical and is the file's stated policy: a
missing file makes `KleePck.Path` return `null`, the Harmony prefix returns
`true`, and the base game's own placeholder draws — *never* a sibling's sigil
(`KleePowerIcons.cs:20-22`, `:135-140`, `:165-199`).

### 2a. Klee — 29 packed, 29 expected, **complete**

23 named cases (`KleePowerIcons.cs:28-60`) plus the one concatenated case
`klee/powers/aura_<element>.png` (`:142-143`). `Elements/Element.cs:6-15`
declares exactly six elements, and all six aura files are packed — so the
dynamic family is closed, not open-ended.

| sub-group | ids | source register | review state |
|---|---|---|---|
| Klee kit (13) | `spark`, `bomb`, `burst`, `bomb_damage_up`, `detonation_splash`, `detonation_vuln`, `bomb_and_spark_per_turn`, `spark_per_turn`, `zero_cost_attacks_up`, `spark_threshold_down`, `reaction_bonus_spark_energy`, `amp_reaction_up`, `sparks_n_splash` | `plan.tsv` auto rows, register `icon`, `contain`, 256² | shipped; no open row |
| Auras (6) | `aura_{pyro,hydro,cryo,electro,anemo,geo}` | `Element <X>.svg`, auto, 256² | shipped |
| Companion summons (4) | `oz_summon`, `solar_isotoma`, `witchs_flame`, `celestial_gift` | shortlist r1; wired 2026-07-24 sweep | shipped |
| The six the summon sweep missed | `friendly_visit`, `study_buddy`, `fantastic_voyage`, `passion_overload`, `shattering_pressure`, `frozen` | shortlist/auto | `friendly_visit`, `study_buddy` are two of the four **AS2-E2 "weak marks"** — new r2/r3 offered, incumbent r1 kept (`review/ruled/art-runs-2026-08-08.md:59-73`); the pick sits in QUEUE **Art debt** / `S4-G17` |

### 2b. Furina — 15 packed, **22 expected, 7 absent (registered deferral)**

15 shipped (`KleePowerIcons.cs:68-89`): `fanfare`, `rising_ovation`,
`salon_member`, `grand_salon`, `all_the_worlds_a_stage`, `center_stage`,
`guest_cast`, `leading_role`, `supporting_cast`, `top_billing`, `limelight`,
`star_of_the_show`, `stage_lights`, `standing_ovation`, `ovation_trickle`.

**Seven are wired-ahead-of-art and verifiably absent at runtime.** `godot.log`
(this evening's session, build `20260826-204650`) carries exactly seven
`pck resource missing` lines and no others:

```
[WARN] [klee] pck resource missing: res://furina/powers/fortissimo_guard.png
[WARN] [klee] pck resource missing: res://furina/powers/stagehands.png
[WARN] [klee] pck resource missing: res://furina/powers/stagehands_encore.png
[WARN] [klee] pck resource missing: res://furina/powers/courtroom_drama.png
[WARN] [klee] pck resource missing: res://furina/powers/the_gallery_stirs.png
[WARN] [klee] pck resource missing: res://furina/powers/quick_change.png
[WARN] [klee] pck resource missing: res://furina/powers/unheard_confession.png
```

| expected id | consumer power | plan rows present | blocking unknown |
|---|---|---|---|
| `furina/powers/fortissimo_guard.png` | `SalonDeployBlockPower` | **r2, r3 only — no r1** | no rank-1 candidate has ever been hunted |
| `furina/powers/stagehands.png` | `SalonBowBlockPower` | r2, r3 only | r3 is a 64×58 source at ×4.0 upscale (flagged) |
| `furina/powers/stagehands_encore.png` | `SalonBowEncorePower` | r2, r3 only | **r2 collides with `ovation_trickle` r2** (§9) |
| `furina/powers/courtroom_drama.png` | `CrossExaminationPower` | r2, r3 only | r3 is 64×64 at ×4.0 (flagged) |
| `furina/powers/the_gallery_stirs.png` | `EncoreSpendDrawPower` | r2, r3 only | — |
| `furina/powers/quick_change.png` | `FirstAttackDrawPower` | r2, r3 only | — |
| `furina/powers/unheard_confession.png` | `FanfareDeltaBlockPower` | r2, r3 only | r2 shares `Animula Choragi.png` with `power_furina_fanfare` r2 (dead ranks; blessed) |

**This is a REGISTERED deferral, not an unnoticed gap.** All seven are named,
with their reason, in `klee-mod/build/validate.ps1`'s `$pckDeferred` block
(`:890-925`), and S12 fails **in both directions** — if the art lands and the
exemption stays, or if the exemption stays and nothing references the path any
more (`validate.ps1:993-1005`). `art-runs-2026-08-08.md:146-171` records that
"**every row is rank 2 or 3; there is no rank 1, so no file lands and the S12
deferral stays valid**" — the absence is by construction, not by accident.
`KleePowerIcons.cs:91-104` and `:106-110` carry the same policy at the call site.

Also confirmed by the log's own timing: the seven warns appear at line **836** of
`godot2026-08-26T20.56.20.log`, during Furina's registration, whereas
`SELFCHECK passed` is logged at line **223**. So `KleeSelfCheck` R13's reflection
sweep does not reach these types at boot; the misses surface later and only in
the log. **UNVERIFIED:** the mechanism (R13 skips any type
`Activator.CreateInstance` cannot construct — `KleeSelfCheck.cs:416-428`; whether
that is the branch taken here was not proved, and proving it needs a run).

### 2c. Kokomi — 7 packed, 7 expected, **complete as of 20:34 tonight**

The six status badges (`KleePowerIcons.cs:125-133`) plus `kokomi/powers/pearl.png`,
whose consumer is **not** a power badge at all: it is the *cap icon* on her
overhead Burst gauge (`Vfx/GaugeBridge.cs:173`, applied at `:347-355`). Klee's
gauge uses `klee/powers/bomb.png` the same way (`GaugeBridge.cs:129`) — one file,
two consumers, deliberate.

| expected id | rendered | packed | landed |
|---|---|---|---|
| `kokomi/relics/pearl_of_wisdom.png` | `ImageGen/images/kokomi/relics/` | `res://kokomi/relics/pearl_of_wisdom.png` | 2026-08-26 20:34 |
| `kokomi/powers/pearl.png` | `ImageGen/images/kokomi/powers/` | `res://kokomi/powers/pearl.png` | 20:34 |
| `kokomi/powers/bake_kurage.png` | ″ | ″ | 20:34 |
| `kokomi/powers/kurages_oath.png` | ″ | ″ | 20:34 |
| `kokomi/powers/before_sun_and_moon.png` | ″ | ″ | 20:34 |
| `kokomi/powers/ceremonial_garment.png` | ″ | ″ | 20:34 |
| `kokomi/powers/vigil_of_the_deep.png` | ″ | ″ | 20:34 |
| `kokomi/powers/princess_of_watatsumi.png` | ″ | ″ | 20:34 |

**Review state: OPEN, awaiting one live look.** `review/records/eb67-kokomi-icons-2026-08-26.md`
§6 item 4 names the acceptance: start a Kokomi run and confirm the Pearl of
Wisdom relic and the Bake-Kurage badge are not `NOPE`. Contact sheet at
`art/contact_sheet_eb67_kokomi_icons.html` (written 19:50). Applied under
R212(1); veto route is documented in §5 of that file.

### 2d. Seven powers with **no icon mapping at all** — reported, not filed

`eb67-kokomi-icons-2026-08-26.md:293-303` records seven further `PowerModel`
subclasses with no case in `KleePowerIcons.PathFor` and no `IconExempt` entry:
`AncientSeaAuthorityPower`, `CannonFireSupportPower`, `ExplosivesWorkshopPower`,
`MasqueRedDeathPower`, `MetallicizePower`, `NightVigilPower`, `SalonCapUpPower`.
All seven classes verified present in the source
(`Powers/FontainePowers.cs` ×4, `Powers/DemolitionPowers.cs`,
`Powers/CompanionPowers.cs`, `Powers/SalonPowers.cs:637`), and none appears in
`KleePowerIcons.cs`. They fall to `_ => null` and draw the base-game placeholder.
**No register row exists for them** — that document states, correctly, that
opening one was not its call. It is not this file's call either.

---

## 3. Ledger — relic icons

Three files serve **six** relics. Reuse is deliberate: an upgraded starter wears
its base relic's icon.

| packed path | base relic | upgraded relic | fallback when absent |
|---|---|---|---|
| `res://klee/relics/pounding_surprise.png` | `PoundingSurprise` (`Relics/PoundingSurprise.cs:69,72`) | `ExplosiveFrags` (`UpgradedStarterRelics.cs:159,162`) | `?? base.PackedIconPath` / `?? base.BigIconPath` — the id-derived base-game slug |
| `res://furina/relics/ethereal_spotlight.png` | `EtherealSpotlightRelic` (`:76,79`) | `CurtainNeverFalls` (`UpgradedStarterRelics.cs:412,416`) | ″ |
| `res://kokomi/relics/pearl_of_wisdom.png` | `PearlOfWisdomRelic` (`:99,102`) | `PearlOfInsightRelic` (`UpgradedStarterRelics.cs:329,332`) | ″ |

All three packed and present. Kokomi's landed tonight; the other two are older.
Rights tier: **private-placeholder** (all three from wiki item art via
`plan.tsv` shortlists).

---

## 4. Ledger — character-shell UI

Nine `Custom*Path` surfaces per character, plus two authored scenes. Sources are
split between wiki hunts (`plan.tsv`) and **generators** — `art_lint.py`'s
`GENERATOR_OWNED` table (`:420-445`) is the authoritative producer map, and it
checks itself (a named generator that no longer emits the filename is a lint
failure, `:477-486`).

| surface | Klee | Furina | Kokomi | producer |
|---|---|---|---|---|
| `ui/select_portrait.png` | ✅ plan `select_portrait` | ✅ | ✅ | Klee: `art_process`; F/K: `gen_*_stills.py` |
| `ui/select_portrait_locked.png` | ✅ (derived) | ✅ | ✅ | derived; F/K in `GENERATOR_OWNED` |
| `ui/char_icon.png` | ✅ plan `char_icon` | ✅ | ✅ | Klee: plan; F/K: `gen_*_stills.py` |
| `ui/char_icon_outline.png` | ✅ | ✅ | ✅ | **all three** `gen_char_icon_outlines.py` (EB-37) |
| `ui/map_marker.png` | ✅ plan | ✅ | ✅ | Klee: plan; F/K: stills |
| `ui/selection_splash.png` | ✅ plan | ✅ | ✅ | Klee: plan; F/K: stills |
| `ui/select_bg.png` | ✅ plan | ✅ plan `furina_select_bg` | ✅ plan `kokomi_select_bg` | `art_process` |
| `ui/transition_wipe.png` | ✅ | ❌ **falls back to Klee** | ✅ | `gen_transition_wipe.py` |
| `ui/character_icon.tscn` | ✅ | ✅ | ✅ | heredoc in `build_pck.ps1:418-472` |
| `ui/char_select_bg_<id>.tscn` | ✅ | ✅ | ✅ | heredoc in `build_pck.ps1:290-414` |
| `materials/<id>_transition_mat.tres` | ✅ | ✅ | ✅ | heredoc `build_pck.ps1:672-745` |
| `ui/energy_icon_74.png` / `_22.png` | ✅ packed | ✅ packed | ❌ **absent** | `plan.tsv` from `Element <X>.svg` |

**`char_icon_outline` is a real surface, not decoration.** It is read by the
base game's co-op vote container and Ancient dialogue line; all three characters
once returned the *fill* for it and rendered the icon twice. Measured out of the
shipped game pack: the outline is the fill's silhouette re-emitted pure white,
dilated ~4.5px on an 85px canvas (`tools/gen_char_icon_outlines.py:1-40`). The
gap is closed and pinned in **both directions** by
`tier0/tests/test_visual_contract_gaps.py:36-58` — `OUTLINE_IS_FILL` is an
**empty dict**, and character four inheriting the gap silently is a test failure.

**The energy icons are packed and have NO consumer.** All three characters point
`CustomEnergyCounterPath` at the base game's own scene
(`Klee.cs:176-177`, `Furina.cs:100-101`, `Kokomi.cs:155-156`), verified live in
the log: `Registered scene 'res://scenes/combat/energy_counters/ironclad_energy_counter.tscn'
for auto-conversion to NEnergyCounter`. A repo-wide grep for `energy_icon` finds
**no C# reference at all** — only `plan.tsv`, the contract, and prose.
`docs/current/art/furina-art-pass-requirements.md:418-423` says this explicitly:
"*`energy_icon_74`/`energy_icon_22` have no consumer yet … treat the scene as
the blocking work, not the art.*" Kokomi has neither file and no fallback fills
them, which is consistent — nothing reads them.

---

## 5. Ledger — transitions (the named case)

| id | rendered output | packed path | fallback | rights tier |
|---|---|---|---|---|
| `klee/ui/transition_wipe.png` | `ImageGen/images/ui/transition_wipe.png` | `res://klee/ui/transition_wipe.png` | none needed | **public-safe** (procedural, `gen_transition_wipe.py`) |
| `kokomi/ui/transition_wipe.png` | `ImageGen/images/kokomi/ui/transition_wipe.png` | `res://kokomi/ui/transition_wipe.png` | none needed | **public-safe** (procedural) |
| `furina/ui/transition_wipe.png` | **does not exist** | `res://furina/ui/transition_wipe.png` **is packed** | **Klee's file, copied into Furina's namespace at build time** | inherits Klee's — public-safe |

**Evidence, three independent legs:**

1. `ImageGen/images/furina/ui/` contains no `transition_wipe.png` (directory
   listed in full; ten files for Klee, nine for Furina, eight for Kokomi).
2. `tools/build_pck.ps1:222-247` — `Copy-FurinaFallback` fills nine relative
   paths from Klee when Furina has none, `transition_wipe.png` among them, and
   prints `Furina fallback: <path> <- Klee` in dark yellow.
3. `tools/gen_transition_wipe.py:11-13` states it as intent: "**Furina
   deliberately has no wipe of her own and keeps Klee's via build_pck's
   Copy-FurinaFallback (art-sprint-spec sec.8 sanctions the shared fallback).**"
   `docs/current/art/furina-art-pass-requirements.md:414-416` calls
   `select_bg` and `transition_wipe` "the two sanctioned fallback lines".

**So this fallback is sanctioned, and today it is the ONLY one firing.** Kokomi's
equivalent list (`build_pck.ps1:257-281`) covers the same nine paths, but every
one of her nine files exists, so no Kokomi fallback fires. `select_bg`, the
*other* sanctioned line, no longer fires either — Furina and Kokomi both have
their own (`furina_select_bg`, `kokomi_select_bg` in `plan.tsv`).

**The build-log signal is the only check.** `furina-art-pass-requirements.md:426-437`
records why: once a fallback fills a path, "a missing Furina asset now renders
as **Klee art** rather than as an obvious hole, and the §11 criterion 'render
without falling back to Klee assets' is no longer verifiable by eye… Check the
build output, not the screen." Nothing in the suite or in `validate.ps1` asserts
the fallback count. **BLOCKING UNKNOWN:** the fallback lines are printed to the
`build_pck.ps1` console and are not captured anywhere on disk, so this stream
could not read tonight's build output — the three legs above are inference from
file presence plus the copy block, and they agree, but the log line itself was
not seen. Marked **VERIFIED-BY-CONSTRUCTION, log line UNSEEN**.

---

## 5A. Ledger — models and rigs, summons, shared UI scenes, VFX

### 5A.1 Combat models and rigs

Three delivery shapes, and which one a character gets is the whole story.

| character | `CustomVisualPath` chain | rig | layers packed | rest / merchant |
|---|---|---|---|---|
| Klee | `klee/model/combat.tscn` — C# null-coalesced to `klee/model/combat_visuals.tscn` (`Klee.cs:167-169`) | **animated** — `combat.tscn` carries `Facing` + `AnimationTree`, 5 layer textures | `body`, `dodoco`, `dumpty`, `floaters`, `smoke` | `rest_character.tscn` + `character_sprite.tscn` (merchant) |
| Furina | `furina/model/combat.tscn` — null-coalesced to `furina/model/combat_visuals.tscn` (`Furina.cs:95-97`) | **animated** — same convention, 4 layer textures | `body`, `coat_back`, `hat`, `sword` | `rest_character.tscn` + `merchant_character.tscn` |
| Kokomi | `kokomi/model/combat_visuals.tscn` **only** (`Kokomi.cs:151-152`) | **static sprite** — no rig exists | none | `rest_character.tscn` + `merchant_character.tscn` |

**Kokomi's missing rig is the family's one EXPECTED-MISSING row, and it is
declared in three places rather than hidden.** `KleeSceneTelemetry.cs:41-46`
carries `kokomi/model/combat.tscn` in its probe list *because* it is absent, and
tonight's log shows exactly the intended single line:
`convention scene MISSING: res://kokomi/model/combat.tscn (falls back to base
behavior — rebuild/redeploy the pck)`. The list holds **24** scenes and the
other **23 report `ok`** in the same boot — one miss, and it is the declared one. `Kokomi.cs:139-150` records why the null-coalesced chain was
*removed* rather than left aspirational — "*a branch that probes a path no build
step produces is dead on every run, and a dead branch reads as a working
feature*" — and `validate.ps1:951-961` excludes `KleeSceneTelemetry.cs` from S12
for the matching reason: feeding a deliberate-absence report to a
must-be-packed rule would turn it into a build failure.

*Note a stale comment, not a defect:* `KleeSceneTelemetry.cs:42-43` says she
"runs on the `combat_visuals.tscn` fallback, which the pck builder fills from
Klee." She has her own `kokomi/model/combat_model.png`
(`ImageGen/images/kokomi/model/`, and in `GENERATOR_OWNED` under
`gen_kokomi_stills.py`), so **no Klee fallback fires for her model today** —
only the scene wrapper is generic.

**Two packed model sources have no consumer at all.**
`res://klee/model/character_klee_full_wish.png` (240 KB) and
`res://klee/model/klee_character_card.png` (134 KB) are packed by the blanket
`model/*.png` copy (`build_pck.ps1:132-140`) and are referenced by **no C# file
and no `.tscn`** — grep across `klee-mod/` returns nothing for either stem. They
are `plan.tsv` `raw`-mode rows (`model_source_full_wish`, `model_source_tcg_alt`)
kept as cut sources. `build_pck.ps1:180-197` already added `$pckExclude =
'*_cutout.png'` for exactly this class of working file — and it catches
`furina_wikipedia_cutout.png` and `kokomi_portrait_cutout.png` (neither is in
the contract; Kokomi's is 8.6 MB) — but Klee's two predate the naming convention
and slip through. ~374 KB of a 9.59 MB pack. **PROPOSED (engineering):** widen
the exclusion or rename the two sources; no design content either way.

### 5A.2 Summons and field entities

| packed path | what it is | producer | consumer |
|---|---|---|---|
| `res://kokomi/summon/bake_kurage.png` | the Bake-Kurage **creature on the field**, ~36 px in a docket slot | `tools/cut_kurage_summon.py` (hand polygon, from `art/raw/Bake-Kurage_Summon.png`) — in `GENERATOR_OWNED` | `Powers/TurnEndAttribution.cs:129` |
| `res://furina/salon/member_{usher,chevalmarin,crabaletta}.png` | the three Salon members as stage mini-sprites | `tools/cut_salon_members.py` (hand polygons, from `art/raw/Salon_Members_Summon.png`) — **NOT in `GENERATOR_OWNED`** (§8) | `Vfx/SalonVisualsBridge.cs:74-76` |
| `res://furina/salon/glyph_{damage,block,support}.png` | role chips under each member; white-on-transparent masters tinted per member at runtime | `tools/gen_salon_glyphs.py` — procedural, **public-safe** | `Vfx/SalonVisualsBridge.cs:105-107` |

`build_pck.ps1:161-176` gives the Kurage its own `kokomi\summon` namespace with
the reason stated: it is "a CREATURE on the field, not a status badge — the same
distinction `furina\salon` draws". The two Bake-Kurage files are therefore a
deliberate pair, not a duplicate (§9d).

**JSON sidecars do not ship.** `members.json`, `kurage.json`, `layers.json` and
`layers_combat.json` sit beside their PNGs in `ImageGen/` but the copy blocks
take `*.png` only, and none appears in the contract. Their numbers are re-read
from the *tool* where a test needs them, deliberately:
`tier0/tests/test_visual_contract_gaps.py:147-151` — "*Read from the TOOL, not
from `ImageGen/images/furina/salon/members.json` — that file is gitignored Tier F
output and absent on a fresh clone.*"

### 5A.3 Shared UI scenes — the only `shared/` namespace

| packed path | consumer | required node (boot-checked) |
|---|---|---|
| `res://shared/gauge.tscn` | `Vfx/GaugeBridge.cs:243` — the overhead resource gauges (Klee Burst, Furina Burst, Kokomi Burst, Kokomi Charge) | `ValueLabel` |
| `res://shared/turn_end_docket.tscn` | `Vfx/TurnEndPreviewBridge.cs:60` — the end-of-turn attribution docket | `ChipLabel1` |
| `res://furina/ui/salon_stage.tscn` | `Vfx/SalonVisualsBridge.cs:49` | `RibbonLabel` |

All three are **script-less, texture-less scenes**: none declares a single
`ext_resource`. Geometry and labels only; every texture is injected at runtime by
its bridge. That is what makes them public-safe and what makes them invisible to
any art check.

`KleeSceneTelemetry.cs:57-80` explains why the node list exists: every bridge
uses `GetNodeOrNull` and is inert when its node is absent, "*which is the right
runtime posture and the wrong debugging one — a renamed or dropped node turns
the feature off and looks exactly like 'the feature does nothing'*". `%Facing`
is the named example. No node-missing warning appears in tonight's log.

Open eyes-on rows attach here: `M26` (docket legibility, frames in
`art/eb52_captures/`), `M16` (`SceneSlots` 4 vs reachable 3), and `S4-G17`'s
`AS2-D5` (the salon).

### 5A.4 VFX — three scenes, all ours, all reusing existing textures

| packed path | consumer | textures it references |
|---|---|---|
| `res://klee/vfx/bomb_lob.tscn` | `Vfx/KleeCombatVfx.cs:27` | `res://klee/powers/bomb.png`, `res://klee/powers/spark.png` |
| `res://klee/vfx/dodoco_pop.tscn` | `Vfx/KleeCombatVfx.cs:28` | `res://klee/model/layers/klee_combat_dodoco.png`, `res://klee/powers/spark.png` |
| `res://furina/vfx/spotlight_shine.tscn` | `Vfx/KleeCombatVfx.cs:29` | **none** — pure geometry |

**Kokomi has no VFX scene**, and none is referenced for her. Everything else
visual-effect-shaped in the mod is base-game (§6a). The reuse in the first two
rows means four icon/layer files each have a second consumer inside a particle
system — a re-crop of `spark.png` or `bomb.png` moves the VFX too.

## 6. Cross-character and cross-**game** fallbacks (first-class rows)

Two distinct mechanisms, often confused:

**(a) Deliberate base-game reuse — 3 surfaces × 3 characters.**
Every roster character points three `Custom*Path` overrides at Ironclad's own
assets rather than at anything of ours:

| property | value | sites |
|---|---|---|
| `CustomEnergyCounterPath` | `res://scenes/combat/energy_counters/ironclad_energy_counter.tscn` | `Klee.cs:176`, `Furina.cs:100`, `Kokomi.cs:155` |
| `CustomTrailPath` | `res://scenes/vfx/card_trail_ironclad.tscn` | `Klee.cs:179`, `Furina.cs:102`, `Kokomi.cs:157` |
| attack hit FX | `"vfx/vfx_attack_slash"` via `WithHitFx(...)` | **87** card files across all three characters, e.g. `Cards/Kaboom.cs:73`, `Cards/Kokomi/Generated/AllStreamsFlow.cs:78`; also `Kokomi.cs:211-214` `GetArchitectAttackVfx()`. It is the *only* hit FX the mod names — there is no per-character or per-element variant. |

**(b) The 9-path asymmetry — and it is NO LONGER UNMEASURED.**
`KleeAssetPathFallback.cs:76-107` lists 22 path-valued `CharacterModel` members.
Thirteen are overridden by all three characters. **Nine are overridden by
nobody**: four arm textures (`ArmPointing/Rock/Paper/Scissors`) and five FMOD
event paths (`CharacterSelectSfx`, `CharacterTransitionSfx`, `AttackSfx`,
`CastSfx`, `DeathSfx`). The Harmony postfix that rewrites them to `ironclad`
**runs only when the instance is Klee** (`:130-142`), so Furina and Kokomi have
no fallback for those nine at all. The file registers the open question for
[USER] and says: "*Whether the gap manifests in play is **UNMEASURED** — no play
session has been run against it either way*" (`:49-54`).

A play session has now been run. `godot.log` contains, and contains **only**,
these six sfx misses — no `kleemod-klee` line appears, because Klee's are
redirected:

```
cannot find sfx path: event:/sfx/characters/kleemod-furina/kleemod-furina_attack
cannot find sfx path: event:/sfx/characters/kleemod-furina/kleemod-furina_select
cannot find sfx path: event:/sfx/characters/kleemod-kokomi/kleemod-kokomi_attack
cannot find sfx path: event:/sfx/characters/kleemod-kokomi/kleemod-kokomi_select
cannot find sfx path: event:/sfx/ui/wipe_kleemod-furina
cannot find sfx path: event:/sfx/ui/wipe_kleemod-kokomi
```

**Fact, with its limits stated.** The audible half of the asymmetry manifests
for both non-Klee characters, including the *transition* wipe sfx, which is this
family's own surface. `CastSfx` and `DeathSfx` produced no lines in the sessions
read, and the four **arm textures are UNKNOWN** — they are the co-op
rock/paper/scissors minigame surface, and nothing in the logs read reaches it.
**This changes no design call:** the code's own registration ("extend, leave, or
rule the 9 paths out of scope") remains [USER]'s, and is restated as pick (4) in
§11. What has changed is only that the answer is no longer being decided against
an unmeasured claim.

---

## 7. Rights tier — as a CATEGORY only

This stream assigns **no rights verdict**. Three observable categories:

| category | what puts a row in it | rows in this family |
|---|---|---|
| **private-placeholder** | derived from a `plan.tsv` row, i.e. wiki-fetched. `art/SOURCES.tsv` records **tier `F`** on **872 of 872 rows** — there is no other tier value in the file. `plan.tsv:1` heads itself "Tier F — private build only, never ships." | every power icon, every relic icon, every hunted UI surface (`select_portrait`, `char_icon`, `map_marker`, `selection_splash`, `select_bg`), every model still, every combat layer, the salon member sprites, the Kurage summon sprite |
| **public-safe** | procedurally generated from geometry with no fetched input | `transition_wipe` ×3 (`gen_transition_wipe.py`), `furina/salon/glyph_{damage,block,support}.png` (`gen_salon_glyphs.py:1-22` — "*there is no wiki art for 'a small sword icon', and a Tier F crop would be both wrong for the job and undistributable*"), the EB-88 orb candidate layers (`gen_energy_orb_layers.py:1-16`), and every authored `.tscn`/`.tres` in the pack |
| **UNKNOWN** | derived from a private-placeholder input by a generator, so the *derivation* is ours but the pixels are not | `char_icon_outline` ×3 (dilated alpha of a Tier-F fill), `select_portrait_locked` ×3 (desaturated Tier-F portrait) |

The repo enforces the separation structurally rather than by policy prose:
`.gitignore:12-19` excludes `art/raw/`, `art/candidates/`, `art/contact_sheet*.html`,
`art/picks.tsv` and `ImageGen/images/` — **the entire rendered set is
untracked**, and `.gitignore:63-64` additionally excludes `*.pck` and
`*.pck.contract.txt`. Only `art/SOURCES.tsv`, `art/SOURCES.txt` and `art/plan.tsv`
are tracked. Consequence for CI, already documented:
`docs/current/atlas/tools.md:197-199` — "*`art_coverage` in CI asserts nothing
about art: `ImageGen/` is gitignored Tier F and absent on a runner, so the bill
is empty by construction — the job proves the tool still runs.*"

---

## 8. What the live tools actually cover — and the hole this family sits in

| gate | scope | does it see this family? |
|---|---|---|
| `tools/art_coverage.py` | **card art only.** "Card-art coverage check, ROSTER-WIDE" (`:1`); two universes are canonical card sheets and C#-requested card art keys (`:44-52`). Totals `294 expected / 270 covered / 24 missing`. | **NO.** Not one icon, UI surface, model, or VFX scene is in its denominator. |
| `tools/art_lint.py` L1/L2/L3/L4/L5/L8/L9/L10/L12 | **effective picks in `/cards/` out-paths only** (`:44-49`; L9 at `:490-494`; L12 hashes `ImageGen/images/cards/**`, `:748-778`) | **NO.** |
| `art_lint.py` L6 (cover-crop warn) | any effective pick | partially — L6 warns fire on card rows in the baseline; non-card `cover` rows would be eligible |
| `art_lint.py` **L11** | `GENERATOR_OWNED` out-paths | **YES**, and it is the one lint that is *about* this family: 21 non-card out-paths, each naming its generator, checked in both directions (`:420-486`) |
| `validate.ps1` **S6c** | `: CustomCharacterModel` classes, `.tscn`/`.tres` only | partially — character preload scenes only; **"no PNG has ever been checked by anything, in any rule"** before S12 (`validate.ps1:864-877`) |
| `validate.ps1` **S12** | every `"<ns>/…png|tscn|tres|ogg|wav"` literal in every `.cs`, namespaces derived from the live contract | **YES — this is the family's real gate.** Known limit stated in-file: concatenated paths (the aura family) are not matched (`:882-887`) |
| `KleeSelfCheck` **R13** | every concrete `PowerModel` in the assembly that `Activator` can construct | **YES at boot**, and it covers the aura family S12 cannot (`KleeSelfCheck.cs:394-445`). Never throws; findings are log errors (`:29-32`). Reported `SELFCHECK passed` tonight. |
| `KleeSceneTelemetry` | 24 convention scenes + 7 required node names | **YES**, boot-log only, no gate (`Diagnostics/KleeSceneTelemetry.cs:24-80`) |

**The hole, stated plainly:** there is **no coverage tool** for this family. S12
answers "does every path C# names resolve", which is a *referential* question.
Nothing answers "is every surface this family *has* actually covered" — the
question `art_coverage.py` answers for cards. That is precisely the charter's
acceptance line "card art is not mistaken for total visual coverage", and it is
the gap Lane B's ledger would fill.

**GENERATOR_OWNED is incomplete for this family — 3 producers unregistered.**
`GENERATOR_OWNED` (21 entries) omits every out-path of:

- `tools/cut_combat_layers.py` → `ImageGen/images/{model,furina/model}/layers/combat/*.png` (9 files, packed)
- `tools/cut_salon_members.py` → `ImageGen/images/furina/salon/member_{usher,chevalmarin,crabaletta}.png` (3 files, packed)
- `tools/gen_furina_stills.py` / `gen_kokomi_stills.py` cached cutouts (`*_cutout.png`, deliberately not packed)

`cut_kurage_summon.py`'s single out-path **is** registered, and it is the exact
sibling of `cut_salon_members.py` (its own header says it follows that file
"verbatim", `:19-20`). So the omission is asymmetric rather than principled. The
consequence L11 exists to prevent — two producers claiming one out-path, the
`SOURCES.tsv` row going stale, the next `art_process` run silently overwriting
generated art — is currently unguarded for 12 packed files. **PROPOSED
(engineering, no design content):** add those 12 out-paths to `GENERATOR_OWNED`.
No row is proposed for the cutouts, which have no plan row and no packed path.

---

## 9. Collision and duplicate state

**Nothing lints source reuse in this family.** L1 (no two effective picks share
a source) enters `/cards/` rows only, by explicit ruling — "*Register-CROSSING
reuse is legal by construction (only `/cards/` rows enter L1)*"
(`art_lint.py:44-49`). L12 (pixel-identical crops) hashes
`ImageGen/images/cards/**` only. So every row below is **unchecked by any tool**.

**(a) Within this family — 4 effective-pick source collisions.** Computed from
`plan.tsv` (auto rows + shortlist rank 1, non-`/cards/` out-paths):

| shared source | ids sharing it | reading |
|---|---|---|
| `Element Pyro.svg` | `energy_icon_large`, `energy_icon_small`, `power_aura_pyro` | size variants of one element sigil; benign by construction |
| `Element Hydro.svg` | `furina_energy_icon_large`, `furina_energy_icon_small`, `power_aura_hydro` | same |
| `Character Klee Full Wish.png` | `combat_model`, `model_source_full_wish`, `select_portrait` | one render feeding the model chain; benign |
| **`Namecard Background Sangonomiya Kokomi The Deep.png`** | **`kokomi_select_bg`** and **`power_kokomi_vigil_of_the_deep`** | **the character-select backdrop and a status badge now wear the same artwork.** Different crops (1920×1080 `cover` vs 256×256 `cover`), so not pixel-identical. |

The fourth row **is new as of tonight's EB-67 run** and is *outside* what that
run checked: `eb67-kokomi-icons-2026-08-26.md:76-80` states "No two of the eight
wear the same picture", which is true **within the eight** — `kokomi_select_bg`
is not one of the eight. Reported as a fact; **whether it matters is a taste call
and is [USER]'s** (pick (2), §11).

**(b) The one collision already in the register.** QUEUE **Art debt** row, pick
(1): "*the `ovation_trickle`/`stagehands_encore` sigil COLLISION — move one off
the shared source*". Confirmed in `plan.tsv`: `power_furina_ovation_trickle` r2
and `power_furina_stagehands_encore` r2 are both
`Item Ovations That Ceased Upon Festivity.png`. Neither is currently effective —
`ovation_trickle`'s effective pick is r1 `Item Furina Banquet.png`, and
`stagehands_encore` has no rank 1 at all — so **the collision is latent: it bites
the day `stagehands_encore` is promoted**, which is also the day its `$pckDeferred`
entry must be deleted (`art-runs-2026-08-08.md:168-171`).

**(c) Card ↔ non-card shared sources — 19, all blessed by rule.** e.g.
`Klee Wish.png` serves both the card `big_badda_boom` and `selection_splash`
(named as the worked example in `art_lint.py:48-49`); `Item Sango Pearl.png`
serves the card `ritual_purification` and `relic_pearl_of_wisdom`;
`Namecard Background Klee Explosive.png` serves `explosives_workshop` and
`select_bg`. Listed for completeness, not as findings.

**(d) One file, two consumers — deliberate, twice.** `klee/powers/bomb.png` is a
status badge *and* Klee's Burst-gauge cap icon (`GaugeBridge.cs:129`). Kokomi's
Bake-Kurage has **two different files on purpose**: `kokomi/powers/bake_kurage.png`
(the status badge) and `kokomi/summon/bake_kurage.png` (the creature on the
field). `KleePowerIcons.cs:121-124` says so in as many words.

**(e) VFX scenes reuse icon textures.** `klee/vfx/bomb_lob.tscn` external-references
`res://klee/powers/bomb.png` and `res://klee/powers/spark.png`;
`klee/vfx/dodoco_pop.tscn` references `res://klee/model/layers/klee_combat_dodoco.png`
and `spark.png`. So four icon/layer files have a second consumer inside the
particle system — relevant to any future re-crop.

---

## 10. Provenance — 37 of 113 non-card outputs have no `SOURCES.tsv` row

Diff of `ImageGen/images/{ui,powers,relics,model,furina,kokomi}/**/*.png` on
disk (**113** files) against `art/SOURCES.tsv` rows under `ImageGen/images/`
excluding `/cards/` (**76** rows). Every SOURCES row has a file; **37 files have
no row**. They fall into three kinds, and only the third is a live gap.

**Kind 1 — generated or derived; provenance is the generator (17 files). No gap.**
Procedural, no fetched input at all: `furina/salon/glyph_{damage,block,support}.png`
(`gen_salon_glyphs.py`), `ui/transition_wipe.png` and
`kokomi/ui/transition_wipe.png` (`gen_transition_wipe.py`). Derived from another
of our own outputs: `char_icon_outline.png` ×3 (`gen_char_icon_outlines.py`),
`ui/select_portrait_locked.png` (`art_process.py:457-459`, "desaturated+darkened").
Generator-owned cuts and stills whose *raw* input is named in the generator's own
header rather than in the ledger: `kokomi/summon/bake_kurage.png`
(`cut_kurage_summon.py:1-8`, from `art/raw/Bake-Kurage_Summon.png`),
`kokomi/model/combat_model.png` and `kokomi/ui/{char_icon,map_marker,select_portrait,select_portrait_locked,selection_splash}.png`
(`gen_kokomi_stills.py`). Plus two cached working renders excluded from the pack:
`furina/model/furina_wikipedia_cutout.png`, `kokomi/model/kokomi_portrait_cutout.png`.
`gen_transition_wipe.py:15-17` states the convention: "*Outputs are not in
`art/plan.tsv` because they are generated, not wiki-sourced… Registered in
`art_lint.GENERATOR_OWNED` so no plan row can claim these paths.*"

**Kind 2 — shortlist picks whose provenance lives on the CANDIDATE row (12 files).**
`powers/{oz_summon,solar_isotoma,witchs_flame,celestial_gift,friendly_visit,study_buddy,shattering_pressure,frozen}.png`,
`furina/powers/{fanfare,ovation_trickle,standing_ovation}.png`,
`furina/relics/ethereal_spotlight.png`. Verified: `art/SOURCES.tsv` carries rows for
`art/candidates/<asset_id>/rN.png` with the pinned wiki URL — e.g.
`art/candidates/power_oz_summon/r1.png`,
`art/candidates/relic_ethereal_spotlight/r1..r3.png`. The provenance exists; it
just is not keyed on the shipped path. **A ledger joining shipped output → source
must follow `plan.tsv` `asset_id` → candidate row, not look up the out-path.**
This is the single most important shape note for Lane B.

**Kind 3 — LIVE GAP: the 8 icons that landed tonight have no `SOURCES.tsv` row
at all, on either key (8 files).** `art/SOURCES.tsv` was last written
**2026-08-16 16:18**; the eight outputs landed **2026-08-26 20:34**, and a grep
for `art/candidates/power_kokomi_*` and `art/candidates/relic_pearl_of_wisdom/`
in `SOURCES.tsv` returns **nothing**. The sources themselves are recorded — in
`review/records/eb67-kokomi-icons-2026-08-26.md` §2 (a table naming each rank-1
source file) and in the 24 new `plan.tsv` rows — but **not in the ledger whose
job that is**. `SOURCES.tsv` is generated by `art_fetch.py` from `plan.tsv`
(`art/SOURCES.txt:5-6`), and the eight rank-1 sources were already on disk in
`art/raw/`, so no fetch ran and no rows were written. Affected:
`kokomi/relics/pearl_of_wisdom.png` and `kokomi/powers/{pearl,bake_kurage,kurages_oath,before_sun_and_moon,ceremonial_garment,vigil_of_the_deep,princess_of_watatsumi}.png`.

**Why it matters, in the repo's own words** (`art/SOURCES.txt:9-13`): "*if the
project ever goes public this is the replace-checklist, and the courtesy-credit
list…*". Eight shipped surfaces are currently outside it. **PROPOSED
(engineering):** run `art_fetch.py` (or an equivalent ledger pass) so the
twenty-four new candidate rows land in `SOURCES.tsv`. No pick, no rights call.

---

## 11. Blocking unknowns and [USER] pick lists

Numbered, never blanks. Nothing here is decided.

**(1) `M19` — the Hydro energy-orb layer set. The eyes-on cannot be taken today.**
QUEUE `M19` says "candidates ready" and points at
`art/contact_sheet_eb88_energy_orb.html`. That sheet references 21 images under
`art/candidates/furina_energy_orb/set_{a_fontaine,b_opera,c_tidal}/` — and
**`art/candidates/furina_energy_orb/` does not exist**. `art/candidates/`
currently holds 22 directories, all of them EB-67/EB-121 Kokomi rows. The sheet
is a page of broken images.
*Not lost:* the producer `tools/gen_energy_orb_layers.py` is tracked and
deterministic, so re-running it restores all three sets.
**Pick:** (a) re-render the candidates and take the `M19` look as written —
**the default, and the only option that unblocks the row tonight**;
(b) leave `M19` blocked until the orb is scheduled with its scene work;
(c) close `M19` on the standing default (set **A — Fontaine Hydro** ships under
R212(1) if no pick lands), and re-render only if the default is vetoed.
*Second-order fact, already recorded and not re-litigated here:* the art is not
the blocking work — `furina-art-pass-requirements.md:418-423` says the
**energy-counter scene** is, and no such scene exists for any character.

**(2) The new Kokomi source collision.** `Namecard Background Sangonomiya Kokomi The Deep.png`
now serves both `kokomi_select_bg` (character-select backdrop) and
`power_kokomi_vigil_of_the_deep` (status badge). **Pick:** (a) accept — different
crops, different registers, no rule broken; (b) move `vigil_of_the_deep` to its
r2 `Item Sangonomiya Kokomi The Deep.png` or r3; (c) move the backdrop instead.
*No recommendation.* Note only that r2 for the badge is described in the run doc
as "*strictly worse*" (`eb67-…:141`), so (b) is not free.

**(3) The seven unmapped powers from `eb67-…` §7.** They have no register row
anywhere. **Pick:** (a) file one BACKLOG row covering all seven; (b) file none
and leave them at the base-game placeholder; (c) rule them out of scope as
companion/base-mirror powers that should not carry our sigils. This stream mints
no id.

**(4) The 9-path asymmetry (arm textures + FMOD events).** The code registers the
question and this file supplies the missing measurement (§6). **Pick, exactly as
`KleeAssetPathFallback.cs:52-54` framed it:** (a) extend the postfix to Furina and
Kokomi; (b) leave it, accepting silent select/attack/wipe cues for two of three
characters; (c) rule the nine out of scope. The file's own argument against (a)
— that it would also mask the stale-pck warning — stands unchanged.

**(5) Open eyes-on rows already in QUEUE that belong to this family**, listed so
the morning read can see them together, not to re-rank them: `S4-G17` (AS2-E2
icon picks, AS2-D5 salon, AS2-B5 motion/facing), `M26` (end-of-turn docket read),
`M16` (docket `SceneSlots` 4 vs reachable 3), **Art debt** picks (1)–(3), and
`M19`. Ranking is untouched.

---

## 12. Explicit UNKNOWNs and NON-FINDINGS

- **NON-FINDING — fonts.** The mod packs no font. Zero `.ttf`/`.otf`/`.fnt` in
  the 132-resource contract. All text rides the base game's fonts. Nothing to
  ledger.
- **NON-FINDING — audio files.** Zero `.ogg`/`.wav` packed. Audio exists only as
  FMOD *event path strings* into the base game (§6). Audio belongs to S19.
- **UNKNOWN — the four arm textures.** `ArmPointing/Rock/Paper/Scissors` are the
  co-op minigame surface. No log read reaches them, and co-op has no automated
  backstop (`STATE.md`, klee-mod bullet). Neither present nor proven absent.
- **UNKNOWN — `CastSfx` / `DeathSfx`.** No lines in the sessions read. Consistent
  with either "not triggered" or "not missing".
- **UNSEEN — the `Furina fallback: … <- Klee` build line.** §5's conclusion rests
  on file absence plus the copy block plus the generator's stated intent. The
  console line itself is not captured to disk and was not read.
- **UNVERIFIED — why R13 does not flag the seven deferred Furina sigils.** The
  ordering proves it does not reach them (§2b); the mechanism was not proved.
- **NOT ASSESSED — whether any surface looks correct.** No eyes-on was taken.
  `S4-G17`, `M26` and the EB-67 live look remain unmet.
- **NOT ASSESSED — the base game's own `ironclad_energy_counter.tscn` internals.**
  `SlayTheSpire2.pck` is `GDPC` format 3 with `pack_flags = 2`
  (`PACK_DIR_ENCRYPTED`), so the scene and its five textures are not readable off
  disk (`art-runs-2026-08-08.md:348-354`). Layer roles there are inference, and
  that document already labels them as such.
- **Dormant rows, including `SKIP-10.9`: not touched.** No dormant row appears in
  any table above.

## 13. Search boundary

Read: `klee-mod/assets/klee.pck.contract.txt`; `tools/build_pck.ps1` (all 835
lines); `klee-mod/pck-src/**` (9 files); `klee-mod/KleeCode/` — `KleePck.cs`,
`KleeArt.cs`, `KleeAssetPathFallback.cs`, `Klee.cs`, `Furina.cs`, `Kokomi.cs`,
`Powers/KleePowerIcons.cs`, `Diagnostics/KleeSceneTelemetry.cs`,
`Diagnostics/KleeSelfCheck.cs` (R13 region), `Vfx/GaugeBridge.cs`,
`Vfx/SalonVisualsBridge.cs`, `Vfx/KleeCombatVfx.cs`, `Vfx/TurnEndPreviewBridge.cs`,
`Powers/TurnEndAttribution.cs` and `Powers/CurtainCallPowers.cs` (path/class
regions), `Relics/*.cs`, `Elements/Element.cs`, plus repo-wide greps for
`KleePck.Path`, `res://`, `energy_icon`, `WithHitFx`, and the four JSON sidecars;
`klee-mod/build/validate.ps1` (S2, S6c, S12); `klee-mod/build/deploy.ps1`;
`art/{plan,picks,SOURCES}.tsv`, `art/SOURCES.txt`, the contact-sheet HTML index;
`ImageGen/images/**` file listing (no image was opened); `tools/art_coverage.py`,
`tools/art_lint.py`, `tools/cut_*.py`, `tools/gen_*.py` headers;
`tier0/tests/test_visual_contract_gaps.py`; `docs/current/art/*`;
`docs/current/atlas/tools.md`; `docs/current/QUEUE.md`;
`review/ruled/art-runs-2026-08-08.md`,
`review/records/eb67-kokomi-icons-2026-08-26.md`;
`.gitignore`; the two most recent `godot*.log` files.

Not read: `game_ref/`, any decompile (none was needed — no claim here rests on
base-game internals beyond what a repo doc already measured), `docs/*-cards.yaml`,
git history, the Downfall reference tree, any image file's pixels.

Not run: `art_coverage.py`, `art_lint.py`, `build_pck.ps1`, any deploy, the game,
any git command, any image generation.
