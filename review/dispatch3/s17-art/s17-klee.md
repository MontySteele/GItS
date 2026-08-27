# S17 — art coverage and provenance: the **Klee** family

> **Decides nothing.** This is an inventory with citations. No source is
> picked, no rights verdict is issued, no image was generated, no art tool was
> re-run, no taste call is made. Technical suggestions are labelled
> **PROPOSED**. Anything that is [USER]'s is written as a numbered pick list at
> the end.
>
> **Scope:** every Klee visual surface — card portraits, power badges, relic
> icons, the character model and its shell scenes, character-select and
> top-panel UI, VFX, the overhead gauge, and the surfaces where Klee currently
> renders *someone else's* art. Card art is **not** total visual coverage, and
> this file is written to make that visible.
>
> **Baseline:** the live read-only `art_coverage` / `art_lint` run on the
> art-bearing primary checkout, `review/dispatch3/s17-art/baseline-run-2026-08-26.txt`
> (`main 223a4ff`, both tools `exit=0`). Everything below joins to that file;
> I did not re-run either tool.

---

## 0. How to read this in one minute

| Question | Answer |
|---|---|
| Is Klee's **card** art done? | Almost. 76 of 79 sheet rows have a portrait; 3 are unhunted; 1 C#-only token has none. |
| Is Klee's **visual** coverage done? | No. Card art is **76 of the 124 Klee-family images that ship** (129 image files exist on disk; 5 are authoring-only masters). The other 48 are badges, icons, model textures and layer cuts — and 5 more surfaces have never been built at all. |
| Any surface where Klee shows the wrong art? | Yes, by design in one place (2 shipped card portraits are byte-identical to 2 others) and by fallback in another (4 co-op arm textures + 5 combat SFX resolve to **Ironclad's**). |
| Anything broken that a person can see? | **Yes: every Klee art review sheet is dead.** All 60 candidate folders `art/contact_sheet_klee.html` points at are gone from disk. Cheap to fix — see §7.1. |
| Anything wasteful? | **Yes: 1.18 MB of the 9.14 MB pack (12.3%) is two source masters nothing loads.** §7.2. |
| Is anything blocked on [USER]? | Three small calls, §10. None of them block the ledger or the tooling lanes. |

---

## 1. The three ledgers this family actually has, and what each one can answer

There is no single Klee art ledger today. There are three partial ones, and
the gaps between them are where the surprises live.

| Ledger | File | What it records | What it **cannot** answer |
|---|---|---|---|
| The plan | `art/plan.tsv` (1259 lines) | `asset_id → out-path, dims, crop mode, pick/rank, source title, art register` | Whether the file on disk still matches the plan; anything a generator script writes |
| The provenance file | `art/SOURCES.tsv` (872 data rows) | `filename → source_url, tier, replace_priority` | Where a **shortlist-picked** shipped file came from — see §1.1 |
| The pack contract | `klee-mod/assets/klee.pck.contract.txt` (134 lines, 60 of them `res://klee/…`) | Exactly what landed in the built `.pck` | Anything shipped as a loose PNG — i.e. every card portrait |

**Citation caveat on the third one:** `*.pck.contract.txt` is **gitignored**
(`.gitignore:64`) and is *derived from what actually landed*
(`tools/build_pck.ps1:118-124`). It is a machine-local artifact, not a
repo-tracked file — so every packed-path citation below is a statement about
this machine's current build, not about the repository. I checked it against
the deployed copy in the game directory and they are byte-identical, so it is
the live truth here.

Plus two things that are neither: `docs/art-asset-manifest.md` (the Klee bill
by category, `:9-24`) and `tools/art_lint.py`'s curated allowlists
(`PENDING_RED_PEN :284-303`, `KNOWN_IDENTICAL :708-745`, `GENERATOR_OWNED
:420-444`), which hold the facts nothing else can infer.

### 1.1 The provenance hole, stated precisely

`art/SOURCES.tsv` has 872 data rows. **772 of them name an `art/candidates/<id>/rN.png`
path, and only 100 name a shipped `ImageGen/images/…` out-path.** (Measured by
this stream, read-only.)

That is because `pick=auto` rows get a provenance row against their shipped
out-path, and `pick=shortlist` rows get one against the *candidate* path
instead. So for a shortlist pick the chain is:

```
shipped file  →  (no SOURCES row)  →  plan.tsv rank-1 row  →  art/candidates/<id>/r1.png  →  SOURCES row → URL
```

Two hops, and the middle hop is a directory that **is currently empty for this
whole family** (§7.1). Concretely, for Klee:

- 61 of the 100 out-path rows are Klee-family; **19** of those are card
  portraits. Klee ships **76** card portraits, so **57 shipped Klee card
  portraits carry no provenance row against the file itself.**
- Of the 29 Klee power badges, **21 have an out-path provenance row and 8 do
  not** — and the split is exactly `auto` vs `shortlist`. The 8 without:
  `celestial_gift`, `friendly_visit`, `frozen`, `oz_summon`,
  `shattering_pressure`, `solar_isotoma`, `study_buddy`, `witchs_flame`.
- 3 shipped Klee UI files have no provenance row **and correctly should not
  have a URL** because they are derived or procedural, but nothing in the
  ledger says so: `ui/char_icon_outline.png`, `ui/select_portrait_locked.png`,
  `ui/transition_wipe.png`.

**PROPOSED (Lane B, `EB-148`):** the ledger schema needs the join
`out-path → plan rank-1 → source URL` computed directly, and a `derived_from`
field distinct from `source_url`, so "derived from our own file" never reads
the same as "provenance unknown". A row with neither should be the error.

---

## 2. Rights tier as a **category** (no verdict here)

The repo's own three-tier policy is in `docs/art-asset-manifest.md:77-81`:
Tier P programmatic, **Tier F found/official — private builds only, never
distributed**, Tier O original/commissioned — the only tier that ships
publicly. `art/plan.tsv:1` and `docs/art-sprint-spec.md:1` both label the whole
sprint Tier F.

**Every one of the 872 rows in `art/SOURCES.tsv` is tier `F`.** (Measured:
`awk` over column 3 — the tier column has exactly one distinct value.)

I therefore assign these **categories** — not verdicts, and not a rights
opinion:

| Category | Klee surfaces in it | Basis |
|---|---|---|
| **private-placeholder** | all 76 card portraits; 29 power badges; 1 relic icon; 7 UI textures; 3 model textures; 10 model layer cuts; and `ui/select_portrait_locked.png` + `ui/char_icon_outline.png`, which are derived from private-placeholder files | tier `F` in `SOURCES.tsv`, or derived from a tier-`F` file |
| **public-safe (structure only)** | 8 `.tscn` scenes (6 shell + 2 VFX), 1 `.tres` material, 1 `build_id.tres`, 2 loc `.json` — geometry, shader code and strings authored in this repo | authored in `tools/build_pck.ps1` (`:293, :425, :479, :497, :513, :646, :744`) and `klee-mod/pck-src/` — but they **reference** private-placeholder textures |
| **public-safe (original pixels)** | `ui/transition_wipe.png` only | procedurally generated, fixed seed, no external source; `tools/gen_transition_wipe.py:1-20` labels it "Tier O, procedural" |
| **UNKNOWN** | none in this family | — |

**Klee has exactly one shipped image that is not private-placeholder.** That
is the honest number for any future public-release conversation, and it is not
a criticism of anything — Tier F was the deliberate policy.

---

## 3. Ledger — card portraits (76 shipped, 79 expected + 1 token)

**Route:** loose PNGs, **not** in the pack. `klee-mod/KleeCode/KleeArt.cs:55-80`
loads `<mod>/images/cards/<cardId>.png` at runtime;
`klee-mod/build/deploy.ps1:112-144` stages four source dirs into **one flat
`images/cards/` directory**. Klee's source dir is
`ImageGen/images/cards/klee/`.

**Fallback:** none, by design — a missing file logs `No card art at …` and the
card renders with the base BETA placeholder (`KleeArt.cs:77-80`,
`deploy.ps1:144`).

**Dimensions:** all 76 shipped files are exactly 500×380, matching
`docs/art-asset-manifest.md:11`. (Measured.)

**Rights tier:** private-placeholder (tier F).

**Deployed:** 272 files in the live flat card dir = 76 Klee + 83 Furina + 62
Kokomi + 51 companions (read-only from the game dir). **No basename collisions
across the four source dirs** — measured, and worth stating because the flat
staging makes one possible.

### 3.1 The exception rows (the other 70 are clean)

| id | State | Source (plan rank-1) | Review state | Collision / duplicate | Blocking unknown |
|---|---|---|---|---|---|
| `hold_the_line` | **MISSING** (uncommon skill) | **no plan row at all** | never hunted | — | no source hunted; see §3.2 |
| `powder_charge` | **MISSING** (uncommon skill) | **no plan row at all** | never hunted | — | same |
| `smoke_and_sparks` | **MISSING** (uncommon skill) | **no plan row at all** | never hunted | — | same |
| `confiscated` | **MISSING**, and it is a **C#-only token**, not a sheet row | r2 `Klee Shorts 2023-06-12.png`, r3 `Klee Birthday 2022 - Shorts.png` (`art/plan.tsv:1142-1143`) — **there is no r1** | candidates staged by art run 8 (`review/active/art-runs-2026-08-08.md:181`), sheet `art/contact_sheet_eb54_eb36.html` — **sheet is dead, §7.1** | — | needs an r1 or a promotion of r2/r3; that is a taste call |
| `spark_knight_style` | shipped, but **byte-identical to `kaboom.png`** | **plan row commented out** (`art/plan.tsv:179-200`) — ruled to the rehunt pile 2026-07-27 | RULED: kaboom keeps `Klee Character Card`, this one re-hunts (`art_lint.py:725-745`) | **duplicate, allowlisted** `KNOWN_IDENTICAL` | new art not yet hunted; `art_coverage` still counts it *covered*, which is correct-by-rule and misleading-by-eye |
| `catalytic_conversion` / `spark_collection` | both shipped, **byte-identical to each other** | both effectively `Item Dodoco's Marvelous Magic.png` | **PENDING RED-PEN**, allowlisted in `art_lint.PENDING_RED_PEN:302` and `KNOWN_IDENTICAL:709`; both lines print in the baseline run (L1 + L12) | **duplicate + source collision** | needs a re-pick on one side — taste |
| `no_holding_back` | shipped | r1 `Klee Multi Wish.png` (`art/plan.tsv:145`) | flagged `L6 WARN` in the baseline run (cover trims ~76% of source height — possible head/limb clip); candidate sheet `art/contact_sheet_eb39_no_holding_back.html` — **dead, §7.1** | — | eyes-on |

**Cross-check of the four ledgers, done for this family (measured):**

- sheet ids **not** on disk: exactly the 3 above.
- on disk but **not** a sheet id: **none** (Klee has no stale card file — unlike Furina's `rising_tide.png` and Kokomi's `swift_currents.png` in the baseline run's STALE block).
- effective plan pick with **no** file on disk: **none**.
- on disk with **no** effective plan pick: exactly `spark_knight_style`.

`pop` was checked specifically because `art/plan.tsv:23-29` says it "renders no
portrait until the rehunt lands" — **that comment is now stale**: `pop` was
re-hunted and has a live rank-1 row at `art/plan.tsv:650`
(`Starlit Sky Firework Card 11.png`) and a shipped file. NON-FINDING, recorded
so the next reader does not chase it.

### 3.2 The three unhunted cards — what the fetched pool holds

`docs/art-claimed-sources.tsv` (derived file, regenerated 2026-08-26 17:18)
records **285 claimed effective card picks** and **184 free fetched titles**
(`:4`, `:291`). Filtering the free block for Klee-relevant titles leaves four
card-eligible names — `Jumpy Dumpty Preview.gif`, `Klee Birthday 2022 -
Shorts.png`, `Klee Portrait.png`, `Klee Shorts 2023-06-12.png` — **and all four
are already staged as rank-2/3 candidates** for `confiscated` and
`no_holding_back`.

So: **the already-fetched pool contains zero unclaimed Klee card faces.** This
is the same shape as the Furina exhaustion finding
(`review/active/art-runs-2026-08-08.md:428-433`), which was recorded for Furina
only.

**This does not say the wiki is exhausted** — only the local fetched pool as
that derived file records it. A fresh `art_hunt` is the untried move, and
whether to spend it is not mine to decide.

---

## 4. Ledger — power badges (29, all shipped, all 256×256)

**Route:** packed. `klee-mod/KleeCode/Powers/KleePowerIcons.cs:26-151` maps each
`PowerModel` to `res://klee/powers/<name>.png` via `KleePck.Path`, which
returns `null` when absent so the base-game placeholder shows instead of
throwing (`KleePck.cs:30-45`). Patched onto `PowerModel.PackedIconPath` and
`ResolvedBigIconPath` (`:165-199`).

**Packed paths:** `klee.pck.contract.txt:65-93`. **Source dir:**
`ImageGen/images/powers/` (`build_pck.ps1:134-141`). **Fallback:** base-game
placeholder on `null`. **Rights tier:** private-placeholder.

**Note on namespace:** `klee/powers/` is the **roster-shared** badge namespace,
not Klee-only. Nine of the 29 are companion or cross-character effects that
happen to live under Klee's prefix. That is deliberate
(`docs/art-asset-manifest.md:13` — "aura icons are shared mod-wide (pay once,
every character reuses)"), and it means "Klee's power art" over-counts Klee if
read naively.

| # | Packed id | Consumer (`KleePowerIcons.cs`) | Source (plan rank-1) | Prov. row | Notes |
|---|---|---|---|---|---|
| 1 | `spark` | `SparkPower` (`:28`) | `Sparks 'n' Splash Buff Icon.png` | yes | also used as particle texture in **both** VFX scenes |
| 2 | `bomb` | `BombPower` (`:29`) | `Item Special Jumpy Dumpty Dodoco.png` | yes | **3 consumers**: badge, `bomb_lob.tscn` sprite, gauge cap icon (`GaugeBridge.cs:128`) |
| 3 | `burst` | `BurstMeterPower` (`:30`) | `Item Jumbo Sparks 'n' Splash Statue.png` | yes | |
| 4 | `bomb_damage_up` | `:31` | `Item Kaboom Box.png` | yes | source shared with card `secret_stash` |
| 5 | `detonation_splash` | `:32` | `Constellation Blazing Delight.png` | yes | |
| 6 | `detonation_vuln` | `:33` | `Constellation Explosive Frags.png` | yes | |
| 7 | `bomb_and_spark_per_turn` | `:34` | `Item Let's Go, Dodoco!.png` | yes | source shared with card `playtime_forever` |
| 8 | `spark_per_turn` | `:35` | `Item Slumbering Fireworks.png` | yes | source shared with card `endless_fireworks` |
| 9 | `zero_cost_attacks_up` | `:36` | `Constellation Nova Burst.png` | yes | |
| 10 | `spark_threshold_down` | `:37` | `Item Sparkly Shiny Dodoco!.png` | yes | source shared with card `sparkly_treasure` |
| 11 | `reaction_bonus_spark_energy` | `:38` | `Item Dodoco's Marvelous Magic.png` | yes | **source shared with the `catalytic_conversion`/`spark_collection` pair** — a 3-way |
| 12 | `amp_reaction_up` | `:39` | `Item Dodoco's Duet.png` | yes | source shared with card `vermillion_pact` |
| 13 | `sparks_n_splash` | `:40` | `Talent Sparks 'n' Splash.png` | yes | |
| 14 | `aura_pyro` | `AuraPower` (`:142-143`, path built by string concat) | `Element Pyro.svg` | yes | **shared mod-wide**; source also feeds both energy icons |
| 15–19 | `aura_hydro`, `aura_electro`, `aura_cryo`, `aura_anemo`, `aura_geo` | same | matching `Element_*.svg` | yes | 6 elements total, matching `Element.cs:6-15` (no Dendro) — **complete** |
| 20 | `oz_summon` | `OzSummonPower` (`:47`) | `Oz Summon.png` (shortlist r1) | **no** | Fischl companion |
| 21 | `solar_isotoma` | `:48` | `Talent Abiogenesis Solar Isotoma.png` | **no** | Albedo companion |
| 22 | `witchs_flame` | `:49` | `Durin Item.png` | **no** | Durin companion |
| 23 | `celestial_gift` | `:50` | `Nicole Icon.png` | **no** | Nicole companion |
| 24 | `friendly_visit` | `CompanionCostThisTurnPower` (`:55`) | `Constellation Exquisite Compound.png` | **no** | **flagged a "weak mark"** — §4.1 |
| 25 | `study_buddy` | `ReplayNextCompanionPower` (`:56`) | `Constellation Sparkly Explosion.png` | **no** | **flagged a "weak mark"** — §4.1 |
| 26 | `fantastic_voyage` | `AttackUpThisTurnPower` (`:57`) | `Talent Fantastic Voyage.png` | yes | Bennett |
| 27 | `passion_overload` | `NextAttackUpPower` (`:58`) | `Talent Passion Overload.png` | yes | Bennett |
| 28 | `shattering_pressure` | `ShatterBonusPower` (`:59`) | `Talent Pressurized Floe 3.png` | **no** | Freminet |
| 29 | `frozen` | `FrozenPower` (`:60`) | `Status Frozen Player.gif` @50% | **no** | reaction status, roster-wide |

**Coverage: 29 requested, 29 present, 0 placeholders.** Every path
`KleePowerIcons` names in the `klee/` namespace resolves. (Contrast Furina, who
still has 7 `NOPE` placeholders — BACKLOG `EB-65`, `docs/current/BACKLOG.md:79`.
Not this family's problem, noted so the joined ledger does not blur them.)

### 4.1 The two weak marks

`review/active/art-runs-2026-08-08.md:59-72` names four icons that "have no
good source and are flagged for re-hunt, not presented as good". **Two are in
Klee's namespace:** `power_friendly_visit` and `power_study_buddy`. Both keep
their incumbent rank-1; r2/r3 candidates were staged
(`art/plan.tsv` — `Item Gift.png` / `Trifolium.png`, `Book Ragged Notebook.png`
/ `Trifolium Shape.png`) onto `art/contact_sheet_eb54_e2_icons.html`.

- **Review state:** materials produced, never looked at. QUEUE `S4-G17`
  (`docs/current/QUEUE.md:48`) carries the "AS2-E2 icon picks" eyes-on and
  points at the Art-debt row; **the Art-debt row's three picks
  (`docs/current/QUEUE.md:53`) are all Furina or Kokomi — neither Klee icon is
  individually named anywhere in QUEUE.** Under R212(1) that means the
  incumbent rank-1 stands unless vetoed on the sheet.
- **Blocking unknown:** the sheet is dead (§7.1), so the veto route does not
  currently work.

---

## 5. Ledger — relic icons (1 file, **2 relics**)

| Relic (C# type) | Player-facing name | Rarity | Icon path | Source | State |
|---|---|---|---|---|---|
| `Relics.PoundingSurprise` | Pounding Surprise | Starter | `klee/relics/pounding_surprise.png` (`PoundingSurprise.cs:68-72`) | `Pounding Surprise Equipment Card.png`, prov. row present | shipped, 256×256 |
| `Relics.ExplosiveFrags` | **Dodoco Tales** | Ancient | **the same** `klee/relics/pounding_surprise.png` (`UpgradedStarterRelics.cs:158-163`) | — | **shares the starter's icon** |

**This is a real duplicate and it is in no ledger.** `art_lint`'s L1
duplicate-source rule is scoped to `/cards/` only
(`tools/art_lint.py:320-323`), `art_coverage` counts relic icons by *file*, and
`plan.tsv` has one relic row. So the collision is invisible to every gate.

Context, not a verdict: `Dodoco Tales` is the Touch-of-Orobas upgrade of
Pounding Surprise. Whether an upgraded starter *should* wear its own icon is a
design/taste call — the base game gives Burning Blood → Black Blood distinct
art, which is why this is worth surfacing rather than assuming it is fine.
`docs/art-asset-manifest.md:14` budgets `~10` relic icons at full character;
**1 exists.**

---

## 6. Ledger — model, shell scenes, UI, VFX

### 6.1 Character model and its layer cut

| Packed path | Dims | Produced by | Source | Consumer | Rights |
|---|---|---|---|---|---|
| `klee/model/combat_model.png` | 240×280 | `art_process` (`plan.tsv` `combat_model`, mode `sprite`) | `Character Klee Full Wish.png` | fallback path in `Klee.cs:249-255` when the scene is missing | private-placeholder |
| `klee/model/layers/klee_combat_{body,dodoco,dumpty,floaters,smoke}.png` | 124×195, 41×49, 98×110, 240×256, 154×202 | `tools/cut_combat_layers.py`, staged by `build_pck.ps1:147-152` | all cut from `Character Klee Full Wish.png` | `combat.tscn` sprite layers | private-placeholder |
| `klee/model/character_klee_full_wish.png` | 1069×1245 | `plan.tsv` mode `raw` | wiki full-wish render | **none — see §7.2** | private-placeholder |
| `klee/model/klee_character_card.png` | 420×720 | `plan.tsv` mode `raw` | wiki TCG card | **none — see §7.2** | private-placeholder |

The full-res masters `ImageGen/images/model/layers/klee_layer_*.png`
(528×847 … 1058×1124) are authoring inputs and correctly do **not** ship —
`build_pck.ps1:147-152` copies only `layers/combat/*.png`. `layers.json` /
`layers_combat.json` also stay out (the copy is `*.png`). NON-FINDING,
verified against the contract.

### 6.2 Shell scenes and materials (authored, not hunted)

| Packed path | Authored in | Notes |
|---|---|---|
| `klee/model/combat.tscn` | `klee-mod/pck-src/klee/model/combat.tscn` (git-tracked) | 5 sprite layers under `Visuals/Facing/Rig` + `AnimationPlayer` + `AnimationTree`; the preferred combat visual (`Klee.cs:233-243`) |
| `klee/model/combat_visuals.tscn` | `build_pck.ps1:479` heredoc | pre-animation-sprint fallback (`Klee.cs:167-169`) |
| `klee/model/character_sprite.tscn` | `build_pck.ps1:497` | **merchant** anim (`Klee.cs:215-216`) |
| `klee/model/rest_character.tscn` | `build_pck.ps1:513` | rest-site anim (`Klee.cs:207-208`). The two paths must differ — sharing one softlocked the first campfire (`Klee.cs:202-206`) |
| `klee/ui/character_icon.tscn` | `build_pck.ps1:425` | `CustomIconPath` |
| `klee/ui/char_select_bg_klee.tscn` | `build_pck.ps1:293` | select splash scene |
| `klee/materials/klee_transition_mat.tres` | `build_pck.ps1:646` | threshold-wipe shader over `transition_wipe.png` |
| `klee/build_id.tres` | `build_pck.ps1:744` | build stamp |
| `klee/localization/eng/{ancients,card_keywords}.json` | `build_pck.ps1:583-643` | text, not art; consumed by name (`KleeSelfCheck.cs:360`, `KleeMod.cs:136`) |

**Asymmetry worth one line:** Furina and Kokomi each get a dedicated
`model/merchant_character.tscn` in the contract; **Klee reuses
`character_sprite.tscn` for the merchant.** Functionally fine, and
`Klee.cs:210-214` records a *known-benign* log error at every merchant visit
(`NMerchantCharacter._Ready` builds a `MegaSpineBinding` on a static
`Sprite2D`, throws, Godot swallows it, the sprite renders, the `relaxed_loop`
idle is lost — "unfixable without patching game code — accepted").

### 6.3 UI (12 packed entries; 10 textures + 2 scenes)

| Packed path | Dims | Producer | Source | Prov. row | Rights category |
|---|---|---|---|---|---|
| `ui/select_portrait.png` | 132×195 | `art_process` | `Character Klee Full Wish.png` | yes | private-placeholder |
| `ui/select_portrait_locked.png` | 132×195 | **derived** by `art_process.py:444-460` (desaturate 0.15 + brightness 0.55) | — | **no** | private-placeholder (derived) |
| `ui/char_icon.png` | 88×88 | `art_process` | `Klee Icon.png` | yes | private-placeholder |
| `ui/char_icon_outline.png` | 88×88 | **`tools/gen_char_icon_outlines.py`** (`GENERATOR_OWNED`, `art_lint.py:442`) | derived from `char_icon.png` | **no** | private-placeholder (derived) |
| `ui/map_marker.png` | 49×64 | `art_process` | `Klee Side Icon.png` | yes | private-placeholder |
| `ui/selection_splash.png` | 1920×1200 | `art_process` | `Klee Wish.png` | yes | private-placeholder |
| `ui/select_bg.png` | 1920×1080 | `art_process` | `Namecard Background Klee Explosive.png` | yes | private-placeholder |
| `ui/transition_wipe.png` | 960×540, mode `L` | **`tools/gen_transition_wipe.py`** (`GENERATOR_OWNED`) | none — procedural, fixed seed | **no** | **public-safe (original pixels)** |
| `ui/energy_icon_74.png` | 74×74 | `art_process` | `Element Pyro.svg` | yes | private-placeholder — **no consumer, §7.3** |
| `ui/energy_icon_22.png` | 22×22 | `art_process` | `Element Pyro.svg` | yes | private-placeholder — **no consumer, §7.3** |
| `ui/character_icon.tscn`, `ui/char_select_bg_klee.tscn` | — | `build_pck.ps1` | — | n/a | public-safe (structure) |

All dimensions match `docs/art-asset-manifest.md:15-19` exactly. (Measured.)

**Klee is the fallback donor.** `build_pck.ps1:220-244` and `:254-278` fill nine
required paths for Furina and Kokomi from Klee's namespace when the character
has no file. Measured on the current tree: **Kokomi needs zero fills; Furina
needs exactly one — `ui/transition_wipe.png`.** That one is sanctioned and
documented (`gen_transition_wipe.py:12-14`, and
`docs/current/art/furina-art-pass-requirements.md:407`). So Klee's single
public-safe original pixel is currently doing double duty as Furina's wipe.

### 6.4 VFX, gauge, docket

| Surface | Path | Art it uses | Dedicated art? |
|---|---|---|---|
| Bomb lob | `klee/vfx/bomb_lob.tscn` (`pck-src`, tracked) | `res://klee/powers/bomb.png` sprite + `res://klee/powers/spark.png` particles (`:3-4`) | **no** |
| Dodoco pop | `klee/vfx/dodoco_pop.tscn` (`pck-src`, tracked) | `res://klee/model/layers/klee_combat_dodoco.png` + `spark.png` particles (`:3-4`) | **no** |
| Overhead Burst gauge | `shared/gauge.tscn` | colours in code + `CapIconPath = "klee/powers/bomb.png"` (`Vfx/GaugeBridge.cs:117-138`) | **no** |
| End-of-turn docket | `shared/turn_end_docket.tscn` | no `ext_resource` at all — chips draw power icons at runtime | **no** |

**Klee's entire VFX surface is composition over existing badges and one model
layer. Zero dedicated VFX art assets exist, and none are missing** — the scenes
are complete and reference only files that ship. Recorded because "VFX" in a
coverage table would otherwise read as a hole.

### 6.5 Surfaces where Klee renders someone **else's** art

`klee-mod/KleeCode/KleeAssetPathFallback.cs:76-107` enumerates all 22
path-valued `CharacterModel` members. Thirteen are overridden per character;
**nine are overridden by nobody**, and for Klee a Harmony postfix rewrites the
id so they resolve to **Ironclad's** assets.

| Surface | What Klee actually shows / plays | Why | Manifest budget |
|---|---|---|---|
| `ArmPointingTexturePath` | Ironclad's arm | no override anywhere (`:95-98`) | `docs/art-asset-manifest.md:21` — co-op minigame poses, 422×1200 ×4, **0 built (deferred)** |
| `ArmRockTexturePath` | Ironclad's arm | same | same |
| `ArmPaperTexturePath` | Ironclad's arm | same | same |
| `ArmScissorsTexturePath` | Ironclad's arm | same | same |
| `CharacterSelectSfx`, `CharacterTransitionSfx`, `AttackSfx`, `CastSfx`, `DeathSfx` | Ironclad's FMOD events | same (`:102-106`) | audio — S19's surface, listed here only so the count is honest |
| `EnergyCounterPath` | base `ironclad_energy_counter.tscn` | explicit, `Klee.cs:176-177`, labelled "Temporary shared base-game surfaces" | `docs/art-asset-manifest.md:16` — energy icons built, **scene not authored** (BACKLOG `EB-40`, `:102`, says all three characters do this) |
| `TrailPath` | base `card_trail_ironclad.tscn` | explicit, `Klee.cs:179-180` | not in the manifest bill |
| Victory transition | base | never built | `docs/art-asset-manifest.md:20` — 2560×1200, **0 built (deferred)** |

`KleeAssetPathFallback.cs:44-47` also records the open asymmetry in [USER]'s
words-in-code: the postfix only fires for Klee, so **Furina and Kokomi have no
fallback for those 9 paths at all**, and whether that manifests in play is
explicitly **UNMEASURED**. Out of my scope; flagged for the joined ledger.

---

## 7. Defects found (all verified, all reproducible)

### 7.1 Every Klee art review sheet is unrenderable — **the headline**

`art/contact_sheet_klee.html` contains **106 `<img src="candidates/…">`
references across 60 candidate directories. All 60 directories are missing
from disk.** Same for every other Klee-touching sheet:

| Sheet | Candidate dirs referenced | Missing |
|---|---|---|
| `art/contact_sheet_klee.html` | 60 | **60** |
| `art/contact_sheet_eb39_no_holding_back.html` | 1 | **1** |
| `art/contact_sheet_eb54_eb36.html` (holds `confiscated`) | 3 | **3** |
| `art/contact_sheet_eb54_e2_icons.html` (holds both Klee weak marks) | 4 | **4** |

`art/candidates/` currently holds **22 directories, all Kokomi**, from today's
two runs. **Roster-wide, 25 of the 27 contact sheets on disk are fully dead**;
the only two that resolve are today's `contact_sheet_eb121_kokomi_fill.html`
and `contact_sheet_eb67_kokomi_icons.html`. That includes sheets QUEUE rows
name directly: `contact_sheet_eb54_s4g12.html` (`S4-G12`, 6/6 missing) and
`contact_sheet_eb88_energy_orb.html` (`M19`, 1/1 missing).

**Why this matters here and not as a curiosity:** R212(1) delegates art picks
to Claude *with [USER]'s veto exercised on the contact sheet*. The veto route
is the sheet. Right now the sheet renders 106 broken images.

**Cause: not established.** `art/candidates/` and `art/contact_sheet_*.html`
are gitignored Tier F (`.gitignore:14-17`), so nothing is recoverable from git,
and `art_process.py` contains no delete (`shutil` is only used for `copyfile`,
`:271`, `:317`). The likeliest explanation on the evidence is that the older
candidates lived in worktrees that have since been purged — the identical
failure is already recorded once, for the `S4-G12` sheet, at
`review/active/art-runs-2026-08-08.md:79-81` ("the old one lived in a retired
worktree"). Stated as a hypothesis, not a finding.

**The repair is cheap and needs no network.** I checked every one of the **173
Klee-family plan rows at every rank** against `art/raw/` (483 files):
**0 sources are missing.** So all four Klee sheets regenerate from local raw
with `art_process.py --assets …` + `art_contact_sheet.py`. **PROPOSED** — I did
not run it (charter: no art tools in the primary).

### 7.2 1.18 MB of the 9.14 MB pack is two files nothing loads

`res://klee/model/character_klee_full_wish.png` and
`res://klee/model/klee_character_card.png` are `mode=raw` **source masters**.
I grepped every `.cs` in `KleeCode/`, every `.tscn` in `pck-src/` and the
generated scenes in the build work dir: **no reference of any kind.**

Measured from the live build work dir (`klee-mod/dist/pck-work/.godot/imported/`,
timestamped with the current build):

| File | Imported `.ctex` size |
|---|---|
| `character_klee_full_wish.png` | 727,284 B |
| `klee_character_card.png` | 450,924 B |
| **total** | **1,178,208 B** |
| `klee-mod/assets/klee.pck` | 9,586,076 B |
| **share of the pack** | **12.29%** |

**Mechanism:** `build_pck.ps1:134-141` copies `*.png` from `ui, powers, relics,
model` for Klee **with no exclusion filter**. The exclusion that exists —
`$pckExclude = '*_cutout.png'`, `:202` — is applied **only** to the
Furina/Kokomi loop (`:204-215`). That filter was added because Kokomi's 8.6 MB
cached cutout "silently doubled the download for a file with no consumer"
(`:186-201`). These two are the same defect, one loop up, unguarded.

**PROPOSED (Lane C / the build-script owner):** exclude by *role*, not by name
— the two masters are inputs to `cut_combat_layers.py` and `art_process`, not
runtime resources. Either move them out of `model/` into a sources dir, or
extend an exclusion to the Klee loop. **Note this is a shared-file edit**
(`tools/build_pck.ps1`) and charter §5 says shared build-script changes belong
to exactly one named integrator — so this is a patch note, not a lane action.

### 7.3 Two packed UI textures have no consumer

`res://klee/ui/energy_icon_74.png` (3,668 B imported) and
`energy_icon_22.png` (708 B imported) ship with **no C# or scene reference**.
Size is negligible; the finding is ledger-shaped, not size-shaped.

This is **already documented for Furina** —
`docs/current/art/furina-art-pass-requirements.md:418-423`: "No C# in the mod
references them… Producing them changes nothing in-game until someone authors
a … energy-counter scene. Keep them in the bill … but treat the scene as the
blocking work, not the art." BACKLOG `EB-40` (`:102`) confirms **all three
characters** return the base `ironclad_energy_counter.tscn`.

**The gap is that no Klee-side document says this.** `docs/current/art/` holds
`furina-art-pass-requirements.md` and `kokomi-art-pass-requirements.md` and
**nothing for Klee** — Klee's bill lives in `docs/art-asset-manifest.md`, which
predates the finding. A reader working from Klee's manifest would think the
energy icons are live.

### 7.4 The relic icon collision (§5)

Two relics, one icon file, invisible to every gate. Restated here so the defect
list is complete.

---

## 8. Collision and duplicate register for this family

Two ids sharing one **source** is legal in several places and illegal in one.
`art_lint`'s L1 only looks inside `/cards/` (`tools/art_lint.py:320-323`), so
card↔badge collisions are structurally invisible. Measured across all Klee
rank-1 rows (cards + powers + relic + ui + model):

| Shared source | Ids sharing it | Seen by a gate? |
|---|---|---|
| `Character Klee Full Wish.png` | `sparks_n_splash` (card), `select_portrait`, `combat_model`, `model_source_full_wish` — **plus all 10 layer cuts** | no (different registers) |
| `Item Dodoco's Marvelous Magic.png` | `catalytic_conversion`, `spark_collection`, `power_reaction_bonus_spark_energy` | **partly** — L1 sees the two cards (allowlisted, prints in the baseline); the badge is invisible to it |
| `Element Pyro.svg` | `power_aura_pyro`, `energy_icon_large`, `energy_icon_small` | no |
| `Namecard Background Klee Explosive.png` | `explosives_workshop` (card), `select_bg` | no |
| `Klee Wish.png` | `big_badda_boom` (card), `selection_splash` | no |
| `Klee Character Card.png` | `kaboom` (card), `model_source_tcg_alt` | no |
| `Item Special Jumpy Dumpty Dodoco.png` | `quick_fuse` (card), `power_bomb` | no |
| `Item Sparkly Shiny Dodoco!.png` | `sparkly_treasure` (card), `power_spark_threshold_down` | no |
| `Item Slumbering Fireworks.png` | `endless_fireworks` (card), `power_spark_per_turn` | no |
| `Item Let's Go, Dodoco!.png` | `playtime_forever` (card), `power_bomb_and_spark_per_turn` | no |
| `Item Kaboom Box.png` | `secret_stash` (card), `power_bomb_damage_up` | no |
| `Item Dodoco's Duet.png` | `vermillion_pact` (card), `power_amp_reaction_up` | no |
| — (no shared source; shared **file**) | `pounding_surprise` relic icon on **both** Klee relics | **no** — §5 |

**Byte-identical shipped files (measured, sha256 over the whole family):**
exactly two pairs, both already allowlisted — `kaboom` ≡ `spark_knight_style`
and `catalytic_conversion` ≡ `spark_collection`. **No unlisted duplicates, and
no Klee file is byte-identical to any Furina, Kokomi or companion file.**
NON-FINDING, and a useful one: the cross-character-fallback risk that Lane C
is chartered to check does not currently exist in the *source* tree.

**PROPOSED (Lane B):** the ledger should carry a `source_key` column joined
across **all** registers, not just cards, so a card↔badge collision is at
least *reportable*. Whether any of them is a *defect* is taste and is not
mine — most of them look deliberate (a card and its badge sharing a motif).

---

## 9. NON-FINDINGS and UNKNOWNS

**NON-FINDINGS** — checked, nothing wrong:

1. No stale Klee card file (nothing on disk that is not a sheet id). Furina and Kokomi each have one; Klee has none.
2. No card-id basename collision across the four dirs that stage into one flat deployed `images/cards/`.
3. Every Klee power-badge path `KleePowerIcons` names resolves to a real file — 29/29, no `NOPE` placeholders.
4. All 6 elemental aura icons exist and match `Element.cs`'s 6 members exactly.
5. All shipped dimensions match `docs/art-asset-manifest.md`: cards 500×380 ×76, badges 256×256 ×29, relic 256×256, and every UI size.
6. Klee's VFX scenes are complete — they reference only files that ship.
7. Full-res layer masters and `layers*.json` correctly stay out of the pack.
8. The deployed `klee.pck.contract.txt` is byte-identical to the repo copy, so the packed surface list is current.
9. `art/plan.tsv:23-29`'s claim that `pop` "renders no portrait" is stale — it was re-hunted at `:650`.
10. All 173 Klee-family plan rows at every rank have their raw source present locally.

**UNKNOWN** — could not be established from the repo:

- **Why the candidate directories vanished.** Gitignored, so unrecoverable and untraceable. Worktree-purge is a hypothesis, not a finding.
- **Whether any of the 12 card↔badge source collisions reads badly in play.** That is eyes-on, and no capture isolates it.
- **Whether the Ironclad arm textures and 5 FMOD events are noticeable.** `KleeAssetPathFallback.cs:52` says explicitly UNMEASURED, and I did not launch the game.
- **Klee's own art-pass review record.** `docs/current/art/` has Furina and Kokomi files and none for Klee; the Klee taste pass is cited as `docs/archive/art-taste-pass.md`, which is not in HEAD and lives at tag `pre-simplification-2026-08-06`. I ran no git commands, so its content is unread.
- **Whether `docs/art-claimed-sources.tsv` is current.** It is a derived file (`:1`), last written 2026-08-26 17:18, i.e. before today's Kokomi runs. My §3.2 exhaustion statement is bounded to it.
- **Whether the wiki holds unfetched Klee card faces.** Only the local fetched pool was examined.

---

## 10. What returns to [USER] — numbered picks, no blanks

**Pick 1 — the two Klee relics share one icon (§5).**
1. Leave it: `Dodoco Tales` keeps Pounding Surprise's icon; record it as intended and add it to a duplicate allowlist so it stops being invisible.
2. Give the upgraded starter its own icon (base-game precedent: Burning Blood → Black Blood are distinct), which opens one hunt.

**Pick 2 — the two Klee "weak mark" badges, `friendly_visit` and `study_buddy` (§4.1).**
1. Keep both incumbents — the R212(1) default if no pick lands.
2. Take a staged r2 for one or both (`Item Gift` / `Trifolium`; `Book Ragged Notebook` / `Trifolium Shape`).
3. Re-hunt both.
Answering 2 or 3 requires the sheet, which needs §7.1 first.

**Pick 3 — the three unhunted cards, `hold_the_line`, `powder_charge`, `smoke_and_sparks`, with the local pool holding zero unclaimed Klee faces (§3.2).**
1. Spend a fresh `art_hunt` on Klee.
2. Ship them on the Tier P programmatic frame (the standing "art never blocks the build" policy, `docs/art-asset-manifest.md:78`).
3. Re-crop an already-claimed Klee source into a second face, accepting a deliberate motif reuse.

**Not a pick — engineering, and it goes to the lanes, not to [USER]:** §7.1 sheet
regeneration, §7.2 the pack leak, §7.3 the Klee-side energy-icon note, and the
Lane B schema requirements in §1.1 and §8.

---

## 11. PROPOSED batches (disjoint, one owner each)

| Batch | Owner | Content | Depends on |
|---|---|---|---|
| **K-1 Sheet revival** | the art-bearing primary's owner (single owner — it writes `art/candidates/`) | Re-render the four Klee sheets from local raw; verify 0 broken `src`. No fetch, no plan edit, no pick. | nothing |
| **K-2 Ledger rows** | Lane B (`EB-148`) | Ingest §3–§6 as fixture rows; implement the `out-path → plan rank-1 → URL` join and `derived_from` (§1.1); add the cross-register `source_key` (§8) | K-1 not required |
| **K-3 Pack-leak patch note** | the single named `build_pck.ps1` integrator | §7.2, as a patch note + fixture, not a race on the shared file | — |
| **K-4 Klee art-pass note** | docs owner | The Klee-side statement of §7.3 and §6.5 — no new bill, no new ids | — |
| **K-5 Card bill** | blocked on Pick 3 | The 3 unhunted cards + `confiscated`'s missing r1 | [USER] |

---

## What this does **NOT** establish

It does not establish that any Klee art is good, bad, on-brand, or shippable —
no taste judgement was made and none is implied by a row being "clean". It does
not establish rights, licensing, or public-release safety: the tier
**categories** in §2 are read straight off `SOURCES.tsv`'s own column and the
repo's own three-tier policy, and assigning a category is not a rights verdict.
It does not establish that the missing candidate directories were deleted by
any particular action. It does not establish in-play behaviour of anything —
the game was not launched, no capture was taken, and no playtest was
interpreted. It does not establish that the wiki pool is exhausted for Klee,
only that the locally fetched pool as of a file written 2026-08-26 17:18 holds
no unclaimed Klee card faces. And it does not price any of the batches in §11;
they are ordered, not estimated.
