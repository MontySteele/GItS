# Silent Anchor — Kickoff v0.1 (design doc)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

2026-07-27. Status: DRAFT for red-pen; execution brief lives in
`docs/silent-anchor-sprint-plan.md` (handed to Opus).

## 1. Purpose

Add the **Silent** as the second supported OFFICIAL character, in the same
sense Ironclad is one today — a *reference anchor*, not a roster member:

1. **Distinctness instrument** — `tools/card_distinctness_report.py` gets a
   second `OFFICIAL:` row. The gate thresholds are PROPOSED single-anchor
   numbers and the module docstring already names this exact work as their
   ratification condition: *"the concentration threshold waits for the
   Silent anchor — the most archetype-concentrated OFFICIAL character is
   the test of whether concentration itself is the divergence."*
2. **Sim layer** — a `real_silent` character scoreable on the same seven
   axes as Klee/Furina/Kokomi and real_ironclad, via the same
   extract → supplement → assemble pipeline.

Non-goals: no playable Silent, no roster entry, no C#/mod work, no art. The
anchor exists to calibrate instruments, nothing else.

## 2. What already exists (check-if-solved audit)

- `tier0/content/characters/ref_silent.yaml` — the six-ish-card *scoring
  construct* (shiv_package of `*_like` cards). Same role as `ref_ironclad`:
  a validity check for the axis math, useless as a content baseline. It is
  in `roster.REFERENCE_IDS` (roster.py:170) but absent from
  `tier05/runner.CHARACTER_PLANS` and `rewards.NO_COMPANION_CHARACTERS`.
- `tier0/content/cards/silent.yaml` — hand-rolled `*_like` cards including
  `shiv` and `blade_dance_like` via `add_card`; `tag_damage_shiv` scaling
  is honoured (effects.py ~424).
- `tools/extract_base_game_pool.py` is already character-parameterised
  (its own docstring uses `Silent` as the example) — with one hard blocker,
  see §5.
- `card_distinctness_report._game_ref_pools()` globs `game_ref/*_pool.yaml`:
  the moment `silent_pool.yaml` exists locally, `OFFICIAL:silent` appears
  with **zero code changes**.

## 3. Silent kit facts (wiki survey, 2026-07-27)

Scoping input ONLY. **The local sts2.dll is ground truth for every number**;
where wiki and DLL disagree, the DLL wins and the wiki claim is discarded.
Sources: keengamer.com Silent guide, pcgamesn.com/slay-the-spire-2/silent,
sts2.untapped.gg card list (fetched 2026-07-27).

- Pool size: **89–91 cards** (sources disagree; extraction settles it).
  Either way it is ~15% larger than Ironclad's 76 — the anchor row should
  note pool size when comparing concentration.
- Starting deck (12 cards): 5× Strike, 5× Defend, **Neutralize** (0-cost,
  3 dmg + 1 Weak), **Survivor** (8 block, *discard 1 card* — a CHOSEN
  discard, see gap table §6).
- HP: 70 per StS1 precedent and `ref_silent.yaml`; DLL char facts are the
  authority.
- Starting relic: **Ring of the Snake** — extra card draw at combat start.
  Unlike Burning Blood (post-fight heal, battery-inert, ruling 1), this one
  ACTS IN COMBAT — whether real_silent carries it is a parity ruling, not a
  mechanical detail. See ask A1 (§8).
- Archetypes (three, per every source): **Sly/discard** (new StS2 keyword:
  "If this card is discarded from your hand before the end of your turn,
  play it for free" — 8 cards carry it, 2 grant it), **Shiv** (generated
  0-cost attacks), **Poison** (DoT that bypasses block). Block quality is
  deliberately poor; defense leans on **Dexterity**.
- Powers seen in card lists: Dexterity, Thorns, Accuracy, After Image,
  Noxious Fumes, Wraith Form, Envenom-style on-hit poison, Weak/Frail.

## 4. IP rule (unchanged, restated because it binds every track)

`.gitignore` game_ref/ + csharp-build-spec.md §0.3: decompiled material is
REFERENCE ONLY. Every extraction output is a local, gitignored artifact.
The committed tools stay structural (no per-card tables, no base-game
numbers). Hand-translation pass files (`silent_pool_pass*.yaml`) live in
game_ref/ like Ironclad's. PARITY NOT FIDELITY; NEVER APPROXIMATE — a card
the DSL cannot express is excluded with a stated reason.

## 5. Architecture: replicate the real_ironclad wiring

The Ironclad pipeline generalises almost everywhere. Touchpoints (verified
2026-07-27):

| Layer | Ironclad today | Silent change |
|---|---|---|
| Extractor | `tools/extract_base_game_pool.py` char-parameterised | **BLOCKER: `ID_PREFIX = "ic_"` is a module constant** (used at ~:290/:726/:1035/:1061). Must derive per character (`si_`) or every Silent id collides. |
| Assembler | `tools/build_ironclad_sheet.py` — inputs/outputs hardcoded | Generalise (`build_official_sheet.py --character silent`) or clone; MUST keep fail-closed + disjointness + `--verify` guarantees. |
| Loader cards | `loader.EXTERNAL_CARD_SHEETS = {"ironclad_pool.yaml": "real_ironclad"}` (loader.py:43) + `EXTERNAL_CARD_LAYERS` | Add `"silent_pool.yaml": "real_silent"` + pass layers. Absent-file behaviour (silent skip) is already what CI needs. |
| Loader char | `char_*.yaml` glob (loader.py ~354) | `char_real_silent.yaml` picked up with zero edits. |
| Upgrades | `upgrades.EXTERNAL_UPGRADE_SHEETS` tuple | Append `silent-upgrades.yaml`. |
| tier05 | `NO_COMPANION_CHARACTERS` (rewards.py:27); `CHARACTER_PLANS` patch (runner.py ~49) | Add `real_silent` to both (and decide whether `ref_silent` joins tier05 at all — default: no, out of scope). |
| Pilot | `ironclad` pilot in `tier0/content/pilots/archetypes.yaml` | New `silent` pilot; needs a discard-choice heuristic (new pilot surface — ask A3). |
| Tests | `test_real_ironclad.py` (skip-guarded), `test_anchor_lock.py` (CI half) | Mirror both: local pins for the assembled pool; CI-side proof that a fresh clone loads with no `si_` cards and `real_silent` absent. |
| Digest | `game_ref/` feeds the measurement-world digest | Automatic; landing the pool CHANGES the digest — label runs accordingly (one variable per window). |
| Distinctness | `*_pool.yaml` glob | Zero changes. |

## 6. DSL gap analysis (the real work)

refpowers.py is 100% Ironclad; the mod-side `powers.py` set is closed by
design ("nothing else until a card needs it"). Silent-relevant state, from
a verified engine audit:

| Mechanic | Today | Class |
|---|---|---|
| Chosen discard ("discard 1") | `_op_discard` is RANDOM-only | **P0** — Survivor is in the STARTING DECK; without it real_silent cannot even be built. Needs op + pilot heuristic. |
| Poison | generic `dot` only: decays at turn START, no stacking semantics audit, no Catalyst | **P0** — poison is a third of the kit. Implement verified base-game poison in the parity layer (refpowers pattern: implement + adversarial verification before it joins the extractor's SUPPORTED_POWERS dial). |
| Dexterity | ABSENT (only Frail touches block gain) | **P0** — hang off the `refpowers.gain_block` chokepoint, the parity-side block funnel built for exactly this. |
| Shiv generation | `add_card` + `generate_from_pool` exist; hand/discard destinations only, no draw-pile insert | **Mostly done**; Accuracy covered by `tag_damage_shiv`. |
| Sly (play-for-free on discard) | An on-discard `sly` hook EXISTS (effects.py ~952) but it is **Kokomi Assist-lane semantics wearing the same name** — fires only from `_op_discard`, resolves an authored effect list, does not "play" the card | **P1 / naming hazard.** Decide: extend (resolve the card's own effects on discard ≈ free play, minus card-played events) or refuse. Either way the two Slys must be disambiguated in code comments before both characters use the word. |
| Envenom / Thousand Cuts (on-attack / on-card-play hooks) | ABSENT — no such trigger exists | **P2** — implement only if the exclusion histogram says they gate many cards; otherwise UNIMPLEMENTED with reasons, like stampede/hellraiser. |
| Wraith Form / Intangible, After Image | ABSENT | **P2** — same rule. |
| Weak/Frail/Vulnerable, Thorns-adjacent | Weak/Frail/Vulnerable present; check Thorns | P1 audit. |

Expectation to pre-register loosely: Ironclad's first structural pass
emitted 35/87. Silent leans harder on triggers and card-generation, so the
FIRST-pass emitted fraction should be LOWER; the exclusion histogram — not
the wiki — then prioritises which gaps to close. That histogram is itself a
headline measurement of the DSL (extractor docstring: the split "measures
how much of a real base-game pool our DSL can even hold").

## 7. Distinctness: what the second anchor is for

Baseline (2026-07-27, this machine):

```
pool                  cards vocab hapax  top%  uniq% maxclu rider% neardup decide%
furina                   78    26    10   31%    62%      5    37%      73     26%
klee                     76    34    22   36%    61%      5    25%      26     20%
kokomi                   61    21    13   33%    56%      7    34%      23     30%
OFFICIAL:ironclad        76    40    33   57%    86%      4    26%      18     20%
```

With `OFFICIAL:silent` present:

1. **Ratify or revise** the PROPOSED gate (uniq ≥ 75 / maxclu ≤ 4 /
   neardup ≤ 0.33·cards) against TWO anchors instead of one.
2. **Decide the concentration question**: if Silent (the most
   archetype-concentrated official pool) posts top% near our 31–36%, then
   concentration is normal and vocab/top% stay ungated; if she posts
   Ironclad-like 57%, low top% is normal too and the gap is elsewhere.
   Either result is binding (null results are binding).
3. Only then does the gate move from PROPOSED to ratified — a [USER]
   red-pen, since it is a metric/band definition.

Caveat for the comparison itself: the emitted/excluded split biases the
anchor toward simple cards (the excluded ones are the interesting ones —
the ironclad-cards.yaml snapshot incident proved how badly). The
distinctness row must come from the ASSEMBLED `silent_pool.yaml` after the
supplement passes, and the report row should be read next to its coverage
fraction (emitted+supplemented / total), not alone.

## 8. Decision-ready asks ([USER] red-pen; everything else is
Claude-may-proceed under house rules)

> **ALL FIVE RULED 2026-07-27.** A1 implement · A2 defer until the pool
> completes · A3 defer likewise · A4 implement true to the game, plus a
> tech-debt note to unify with Kokomi's `sly` · A5 bulk-add. What each
> ruling actually changed is in §9 of
> `docs/silent-anchor-sprint-log-2026-07-27.md`; the recommendations below
> are left as written so the record shows what was recommended against what
> was decided. **A4's recommendation was wrong** — it argued for refusing
> the RESTRICTED reading, which is not an argument against the real one.

- **A1 — Ring of the Snake.** real_ironclad got Burning Blood as
  `heal_after_won_fight` because it is battery-inert. Ring of the Snake
  (combat-start draw) is NOT inert. Options: (a) omit — parity world has
  no relics, accept the anchor drafts without her engine; (b) model as a
  `relic_hook` draw at combat start, mirroring ruling 1's shape.
  Recommendation: **(b)** — Ironclad's anchor kept his starting relic, and
  an anchor missing her card engine understates decide%/velocity-adjacent
  behaviour in the sim layer. Distinctness is unaffected either way.
- **A2 — Gate ratification** after the two-anchor table exists (§7). The
  sprint DELIVERS the table and a proposed ruling; it does not self-ratify.
  > **CLOSED 2026-07-27 (second ruling, complete-pool data):** recalibrated
  > on the two-anchor floor and RATIFIED — uniq ≥ 70 / maxclu ≤ 5 /
  > neardup ≤ 0.40/card, top%/vocab permanently gate-free, gate enforced as
  > a red suite test. R81; full evidence in
  > `docs/a2-gate-ratification-2026-07-27.md`.
- **A3 — Pilot heuristics.** The `silent` pilot needs a discard-choice
  rule and shiv/poison play-priorities. Proposal ships in the sprint as
  PLACEHOLDER-flagged weights; red-pen before any anchor number derived
  from tier05 runs is quoted as load-bearing (D4: the instrument must
  model the changed object).
- **A4 — Sly implementation vs refusal** (§6). Recommendation: attempt the
  restricted form (resolve-own-effects-on-discard), refuse loudly if the
  card list forces true replay semantics (hellraiser precedent).
- **A5 — reserved-card-names.txt bulk pass.** Today it holds ONE Silent
  entry (Grand Finale). Card NAMES are public wiki material, not decompiled
  data, so a bulk `Name | base game Silent (StS2)` block is IP-clean and
  turns a structurally-invisible defect into a lint (the house pattern).
  ~90 lines added to a 27-line curated file is a character change to that
  file's nature, hence the ask. Recommendation: bulk-add.

## 9. Version/measurement discipline

- Landing `silent_pool.yaml` changes the measurement-world digest on this
  machine; the frozen battery and `test_anchor_lock` numbers are untouched
  (no CONSTANTS_VERSION bump). CI never sees game_ref and must stay green
  in total absence — the anchor-lock test family is the proof and gets
  Silent clauses.
- One variable per window: extraction lands and is measured BEFORE any
  gate-threshold discussion; DSL-gap implementations land power-by-power
  with the dial (SUPPORTED_POWERS) moving only after each adversarial
  verification pass, exactly as the Ironclad entries did.
