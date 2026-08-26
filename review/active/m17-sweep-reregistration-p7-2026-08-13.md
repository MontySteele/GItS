# M17 — force-first-copy paired winrate, **re-registered under `P7`**: DRAFT

> **Lifecycle: DRAFT, awaiting [USER]'s countersign at QUEUE `M17`. UNRUN.**
> This is the second of the two drafts `M17` says do not exist yet. It is a
> **new registration standing beside** the frozen `EB-17p` packet — not a
> re-grade of it, not an amendment to it.
>
> **R101b holds absolutely.** `review/active/eb17p-registration-draft-2026-08-08.md`
> and `review/active/eb17p-results-2026-08-10.txt` are **untouched** by this
> packet. Their §13 grade stands as published. Where this packet quotes them it
> quotes them; it never edits them.
>
> **Prediction slots (§8) are FILLED, 2026-08-26, and they are [USER]'s.** Per
> EXPERIMENTS law and the R121 precedent, predictions are authored design-side
> and land as their own commit **before** any seed in the registered range is
> run — which is how they landed: the fill is its own commit, taken before any
> registered seed had been run, and **§8 is not edited again.**
>
> **PARTLY FILLED 2026-08-13 by R189, and STILL NOT COUNTERSIGNED.** Four slots
> are settled and written in below: §7's `N` (**2,400 pairs per card**), §7's
> cost ceiling (**4 hours, stop-and-report**), §8.1's redesign trigger
> (**carried forward unchanged**), and the §8 `Q4` materiality threshold
> (**5%**). The **route** is settled too: **measure-first** — the sweep runs
> first, and the `elemental_ecstasy` redesign lands after the graded read as its
> own `C` bump.
>
> **The countersign is deliberately WITHHELD, and that is not an oversight.**
> R189 ruled that this packet is not signed at `C9`: the `RT`/`C` window is
> still open, the world will move at its close, and predictions are filled
> against the SETTLED world. The filled slots above are carried into the
> post-window restamp, the packet is re-stamped if the world moved, §8's
> per-arm prediction table is filled **then**, and the countersign comes after
> that. Signing now would date the packet to a world it will not run in.
>
> **§9's "Order of operations" was reconciled to that sequence on 2026-08-24.**
> As drafted it put the countersign first and asked [USER] to fill §7 — both
> contradicted this note and R189's ruling. The packet is DRAFT and
> uncountersigned, so the correction is made in place; no measurement record is
> touched and R101b is not in play.
>
> **THE POST-WINDOW RE-STAMP IS TAKEN, 2026-08-25: `RT10/D14/P7/C9` →
> `RT12/D17/P10/C19`.** This is step (2) of §9's own order, and it is execution
> of R189's sequence rather than a new ruling. The world the packet was drafted
> against closed long ago and moved four more times after the target the
> registers last named: `EB-118`'s richness pass ran to completion (`C13`–`C17`,
> `C19`, `D16`, `D17`, `P8`–`P10`) and `EB-136`'s same-target binding landed at
> `C18`. §3 now names the live world, §9's `S1` fires on that world, and the
> spent tripwires and spent sequencing are marked spent rather than left to fire
> as stale citations — the `P12` precedent from the payoff-reach registration,
> where a tripwire left naming a superseded world "fired on every arm of every
> run for the single reason that its string named a superseded world — a stale
> citation, not a finding."
>
> **WHAT THE RE-STAMP DID NOT DO, deliberately.** It filled nothing, graded
> nothing and measured nothing. §8's per-arm table and the direction half of the
> `Q4` slot were left blank for [USER] at the re-stamp and were filled
> afterwards, on 2026-08-26, in their own commit and against the settled world —
> which is the order R189 ruled.
> **The `borrowed_brilliance` bare-form play rate was NOT re-measured**,
> and that is a rule and not an omission: it is the `Q4` read, [USER]'s
> direction for `Q4` is not written down yet, and taking the number first is
> exactly the blind-grading breach EXPERIMENTS forbids. The `P7`-era ~6.1%
> quoted in §1 stays what it is — an archive figure from a superseded world,
> context and never a comparator.
>
> **ONE DISCLOSURE FOR THE COUNTERSIGN, and it is not a recommendation.** §8's
> `Q4` materiality threshold (5%) was filled by R189 at `P7`, and it was
> recorded there as [USER]'s chosen threshold rather than an evidence-derived
> one — so a world move does not invalidate it by construction, and it is
> carried forward unchanged here. The world has nonetheless moved `P7` → `P10`
> since the fill, and nobody has seen a bare-form figure in this world at all.
> Whether to leave 5% standing or re-rule it is [USER]'s and is available at the
> countersign; this packet does not touch it either way.

---

## 0. Plain-English summary

Back in August we ran an experiment on five of Klee's cards. For each card we
took 2,400 runs, forced one copy of that card into the deck, and compared
against the same 2,400 runs without it — same seeds, same maps, same relics,
one card different. One of the five arms was a deliberately blank card (a spare
copy of Klee's basic attack) so we could tell "this card is bad" apart from
"any extra card dilutes the deck".

That experiment is finished and graded. But two things have happened since:

1. **The world moved.** The experiment ran in the world stamped
   `RT9/D14/P6/C8`. What ships today is **`RT12/D17/P10/C19`** — **all four**
   fields changed, and the packet has been re-stamped to say so (2026-08-25;
   as first drafted it read `RT10/D14/P7/C9` and three of four). By our own
   stamp law, the old numbers are not today's numbers.
2. **One arm turned out to be measuring the pilot, not the card.**
   `borrowed_brilliance` was drawn 40,396 times and played **zero** times. That
   was the simulated pilot refusing to value the card, not the card being
   unplayable. `P7` (R176) fixed the pilot's valuation, and the base card now
   plays about **6.1%** of the time (60 of 981, measured).

So R180 ruled: re-run it. **The same five cards, not a narrowed set** — because
the blank-card arm and the other three arms are what make any one number
readable, and dropping them would leave a single-card experiment that cannot be
graded against anything.

This document is that re-run, written out in full so it can be countersigned.
It is the same instrument, the same protocol and the same five arms as before,
re-stamped to today's world. **What is deliberately empty is the prediction
table** — those are [USER]'s, they get written down before anything runs, and
the results are graded blind against them afterwards.

**When it runs matters**, and §9.1 said so: the payoff-reach sprint went first
under the approved settle-first plan, and this sweep runs after it, in a world
that has not moved in between. **That sequencing is now SPENT, not pending** —
the payoff-reach sprint ran and was graded blind on 2026-08-24, and everything
§9.1 ordered ahead of this sweep has landed. What is left in front of the run
is §8's fill and the countersign, both [USER]'s.

---

## 1. Provenance and what has changed

**Parent.** `EB-17p`, `review/active/eb17p-registration-draft-2026-08-08.md`,
countersigned and graded 2026-08-10 (3 PREDICTED / 1 SPLIT / 1 MISS). The
register's phrase is unchanged: *"two decks on the same seeds, one with a copy
forced in, one without."*

**Authority for this packet.** QUEUE `M17`, **R180 (2026-08-12)**: the two
trigger-fired cards are split; `elemental_ecstasy` goes to redesign, and
`borrowed_brilliance` is *"remeasured before any design act — specifically by
re-running the REGISTERED five-card sweep, re-registered under `P7`, **never a
narrowed single-card experiment**"*.

**The three things that changed since the parent ran:**

| | parent (`EB-17p`) | this packet |
|---|---|---|
| world stamp | `RT9 / D14 / P6 / C8` | **`RT12 / D17 / P10 / C19`** |
| `borrowed_brilliance` base-card play rate | **0 plays / 40,396 draws** (§13.8) | **UNMEASURED IN THIS WORLD — it is the `Q4` read** |
| status of §13's Δ figures | the published grade | **`P6` reads**; the pilot has moved `P6` → `P10` since |

**The middle row was rewritten at the 2026-08-25 re-stamp, and the reason is
blind grading.** As drafted it read *"~6.1% (60 / 981, measured under `P7`)"*.
That figure is real, it is quoted by R180, and it is now a **`P7` reading in a
`P10` world** — archive under stamp law (R68) like every other cross-stamp
number in this packet. It was **not** re-taken at `P10`, and re-taking it is
forbidden rather than merely unnecessary: the bare form's
`played_when_drawn_rate` *is* the `Q4` estimand (§2), [USER]'s direction for
`Q4` is still blank, and reading an estimand before its prediction exists is
the retro-fit §8 is built to prevent. The ~6.1% survives in this packet only
where it already was — §8's note on the `Q4` threshold — labelled as context
that a grader must never present as evidence.

**What has NOT changed, and may not:** the arm set (§5), the estimand (§2.3),
the pairing (§4), the metric definitions (§6) and the grading discipline (§9).
Those are copied forward deliberately. A re-registration that also redesigned
the instrument would answer a different question and would not be comparable to
anything, including itself.

**What this packet is NOT.** It is not a re-grade of `EB-17p` §13, not an
erratum to it, and not a claim that its grade was wrong. `EB-17p` measured its
world correctly. This measures a different world.

---

## 2. Questions

**Q1 (primary).** For a named card `X`, does forcing one copy of `X` into the
deck at run start change the run's winrate, holding the seed fixed, **at
`RT12/D17/P10/C19`**? Estimand: **Δ = P(win | forced) − P(win | not forced)**,
paired by seed.

**Q2 (secondary, descriptive).** Within the forced arm, the card's own flow —
`draws_per_fight`, `played_when_drawn_rate`, `dead_in_hand_rate`,
`force_first_copy_rate` (`metrics.card_flow_profile`, per card id).

**Q3 (secondary).** Compliance — does the assignment survive the run (§6.3).

**Q4 (new here, and the reason R180 ordered the re-run).** Does
`borrowed_brilliance`'s §13.8 anomaly clear under `P7`? Specifically: is the
bare form's `played_when_drawn_rate` **non-zero** in this world, and does its
Δ-vs-filler move relative to the parent's −0.17 pp?

**Q4 is graded as a descriptive question with a stated direction, not as a
comparison to the parent's number.** The parent's −0.17 pp was taken at `P6`
and may not be subtracted from anything measured here — stamp law (R68). What
Q4 asks is what this world says, and [USER]'s §8 prediction for that arm is
what it is graded against.

**Q4's own second clause moved worlds too, and the re-stamp says so rather than
quietly widening it.** As drafted, "does its Δ-vs-filler move relative to the
parent's −0.17 pp" named a `P6` figure while the packet was pinned at `P7`;
the packet is now at `P10` and the gap is three pilot versions wide, not one.
Nothing about the clause changes — it was never a subtraction and R68 already
forbade making it one — but the honest sentence at the grade is "the `P6` world
read −0.17 pp, this world reads Y", with both stamps printed (§11).

**Not asked here.** Whether any observed Δ justifies a redesign of any card.
That is the design act, downstream of the grade, and [USER]'s — exactly as in
the parent (§1, "Not asked here").

---

## 3. World, cell and arms

**Stamp, pinned: `RT12 / D17 / P10 / C19`.** Re-stamped 2026-08-25 from the
`RT10 / D14 / P7 / C9` this section was drafted against.

| field | value | source |
|---|---|---|
| `RT` `RUNTEMPLATE_VERSION` | **12** | `tier0/constants.py:844` — the run-layer half of the window-2 correctness batch (`EB-104`) |
| `D` `DRAFTER_VERSION` | **17** | `tier0/constants.py:2422` — `EB-118` Phase-3 Window 3's two new pricing terms (R211): `STATIC_SPARK_SPEND_COST = 2.5` and `spotlight_moved_this_turn` at share 0.167 |
| `P` `POLICY_VERSION` | **10** | `tier05/draft.py:2087` — `EB-118` Phase-3 Window 3's exhaust-chooser repair (R211), `PILOT_WEIGHTS_VERSION` **5** beside it |
| `C` `CONSTANTS_VERSION` | **19** | `tier0/constants.py:2174` — `EB-118` Phase-3 Window 3's card-body pass (R211): eight sheet rows across all three characters |

Read live via `tier05.cells` and reprinted by `Cell.stamp()` on every table.
**Pinned for this experiment**; a bump in any of the four before execution
re-registers (§9, S1). **All four fields are now live risk**, which is a change
from what this line said as drafted (`RT` and `C`, not `D`): the payoff-reach
`D14` pin that made `D` safe was discharged on 2026-08-24 and `D` has moved
twice since.

### 3.1 What moved into this cell between `C9` and `C19`

The re-stamp is not a string edit, so this subsection says what the new world
actually does to the six arms. It is **static analysis of sheets, dials and
scorer code** — no run of any kind was taken, and nothing below is a measured
winrate.

**The five swept cards did not move.** `friendly_visit`, `study_buddy`,
`borrowed_brilliance`, `elemental_ecstasy` and `kaboom` have byte-identical
sheet rows and byte-identical `docs/klee-upgrades.yaml` entries between the
`C9` world (`3b3b730`) and `C19` (`1eb5b45`) — whole rows, not just
`role`/`archetypes`. Their current labels: `friendly_visit`
`[reaction]`/`glue`, `study_buddy` `[reaction]`/`payoff`,
`borrowed_brilliance` `[reaction]`/`glue`, `elemental_ecstasy`
`[reaction]`/`glue`, `kaboom` `[generic]`/`glue`, basic. §5's table stands
verbatim, with one transcription correction that is **not** world movement: its
`friendly_visit` rarity cell read `common` and now reads `uncommon`, which is
what the sheet has printed since the **X7 rarity erratum (R161)** landed inside
`C9`'s own window — so the cell was already wrong in the world this packet was
drafted against, and the byte-identity claim above is unaffected.

**The `reaction` plan's membership did not move either.** The set of Klee rows
tagged `archetypes: [reaction]` is **14 ids at both commits, with an empty set
difference**, pinned by `tier0/tests/test_klee.py:91`. Of the five Klee label
changes anywhere in the span — four at `C15` (`big_badda_boom`
`[demolition, generic]` → `[generic]`; `explosive_frags`, `all_my_treasures`,
`playtime_forever` `payoff` → `glue`/`enabler`) and one at `C17`
(`sparkly_explosion` dropping `spark`) — **none is reaction-tagged.**

**What DID move is the shelf around them, and there are three mechanisms.**

1. **The pool grew and the plan's share of it shrank.** Klee's sheet goes
   **76 → 79 rows** and her draftable pool **71 → 74**, entirely in the
   **Uncommon** bucket (**28 → 31**), from `C19`'s three ratified Spark sinks
   (`powder_charge`, `hold_the_line`, `smoke_and_sparks`). Offers are
   **archetype-blind** — `shop_offer` and every reward screen roll rarity
   first and then `rng.choice` over the character's whole bucket
   (`tier05/rewards.character_pool`) — so three uncommons the `reaction` plan
   earns no on-plan credit for now compete for the same slot. The plan's share
   of the draftable pool falls **19.7% → 18.9%**. This also means the same rng
   draw maps to a different card from the first Uncommon roll onward: the
   shelf renumbers.
2. **`big_badda_boom` is repriced, and this is the largest single pricing
   effect on this cell.** `D16` made `STATIC_ETHEREAL_SHARE` (0.6) reach a
   draftable row for the first time, taking the card's static power
   **8.0000 → 4.8000**. `score_offer` folds that in as
   `min(3.0, _static_power/3.0)` (`tier05/draft.py:1741`), i.e.
   **2.667 → 1.600, a −1.07 offer-score swing on every plan including
   `reaction`** — larger than the entire `+0.8` generic-tag credit the card
   earns under a reaction plan. It is a Klee **Common**, so it is on the shelf
   constantly.
3. **`D17` prices the three new sinks, and one of them lands in a place worth
   naming.** `hold_the_line` prices to **0.0000**, below
   `DRAFT_SKIP_THRESHOLD = 0.5` (`tier0/constants.py:2431`) — while
   simultaneously collecting the archetype-blind **`+2.5`** defence-quota
   credit whenever deck block density is under `DRAFT_BLOCK_DENSITY_MIN`
   (`tier05/draft.py:1779-1780`). Those two pull opposite ways and are stated
   together rather than one at a time. `powder_charge` prices 7.0000 →
   **2.0000** and `smoke_and_sparks` 6.0000 → **1.0000**. R211 kept
   `STATIC_SPARK_VALUE` at 0.0, so **no other Klee row's price moves at
   `D17`.** None of the three can advance the `reaction` core: `core_complete`
   / `_core_progress` want `_is_applier` or `_is_amp_payoff`, `role_c` is a
   companion-only field absent from every `klee-cards.yaml` row, and all three
   sinks are `role: glue`.

**Which pilot bumps reach this cell, and which provably do not.**

- **`P8`** (`PILOT_POLICIES_ENABLED` True) — **reaches it conditionally.** Its
  Klee limb is bomb placement in the concentration form, which a `reaction`
  deck can hold because offers are archetype-blind. `C18` has since superseded
  that hook for `target: enemy` (`_op_place_bomb` no longer calls
  `pilot.policy.bomb_placement_target`), with no edit to `policy.py`.
- **`P9`** (mode chooser) — **does NOT reach it.** The only modal card in the
  repo is `deep_breath`, a Furina Uncommon. Klee's pool holds no `choose_one`
  row.
- **`P10`** (formula-aware exhaust chooser) — **does NOT reach it.** Exactly
  two rows on any sheet print an `exhaust_selection_*` formula, `pearl_barrage`
  and `the_tide_remembers`, **both Kokomi**; the hook returns 0.0 for every
  card that prints none, so every other carrier's pick is unchanged.

**Which `C` bumps reach it.** `C12` (two Klee rows cost more), `C13` (twelve
`place_bomb` rows leave `target: random_enemy`, `big_badda_boom` re-bodied,
Explosives Workshop becomes a per-rotation power), `C15` (labels, above),
`C17` (`sparkly_explosion` re-bodied), `C18` (the same-target binding — every
combat number for every character, the anchor's included) and `C19` (the three
sinks). **`C14` and `C16` do not**: `C14` is Furina-only and `C16`'s own block
states "KLEE IS UNTOUCHED".

**One half of the `reaction` pool is off the Klee sheet, and it is unmoved.**
`tier0/content/loader.py:240-242` appends `reaction` at load time to any
Mondstadt companion `_is_reaction_fuel()` accepts, so the live reaction pool
has a companion half reached through the companion reward slot.
`docs/mondstadt-companions.yaml` changed by **comment only** across the span,
so that half is unmoved — named as unmoved rather than left unexamined,
because §3's original rationale ("all four register-named cards are Klee cards
tagged `archetypes: [reaction]`") does not mention it exists.

**What none of this licenses.** No causal claim may be read out of any of it.
`C15`'s own pre-registration (`review/active/eb118-w1-preregistration-2026-08-24.md`
§3) forbids a role-versus-tag attribution for any tier-0.5 number taken after
that bump, because both fields feed one scorer; and the standing baseline's
`klee / reaction` row (**6.0%**, [5.2, 6.9], at `RT12/D17/P10/C19`) is a
different seed base and a different `n` from this sweep, with no cause assigned
to its Δ. **This subsection exists to say the world moved and where, not to
predict what §8 should say.**

**Base cell.** `cells.CANONICAL.but(character="klee", archetype="reaction",
name="m17p7")` — the ratified cell (R68): seed 11, route `hunter`, policy
`assigned`, realistic loadout (relics + potions), all registered acts. Same
cell as the parent, for the same reason: all four register-named cards are Klee
cards tagged `archetypes: [reaction]`, and `assigned` is the policy under which
"the deck the plan wanted" is a well-defined control.

**Note on the cell's pilot.** Under `P6` the `assigned` policy's scorer did not
value `copy_companion_in_hand` / `replay_next_companion`; under `P7` it does
(R176), which is the change R180 ordered this re-run for. The pilot has since
moved twice more — `P8` threw the pilot-policy switch and `P9` the mode
chooser; `P10`'s exhaust-chooser repair reaches only two Kokomi rows (§3.1).
The cell name is the same; **the pilot inside it is not the same pilot**, and
that is the whole point of the re-run. What is measured here is cards under
`P10`.

**Arms.** Six, exactly as the parent:

| arm | `force_cards` | role |
|---|---|---|
| `control` | `None` | anchor; byte-identical to the unmodified world |
| `forced(friendly_visit)` | `[friendly_visit]` | register card 1 |
| `forced(study_buddy)` | `[study_buddy]` | register card 2 |
| `forced(borrowed_brilliance)` | `[borrowed_brilliance]` | register card 3 — **the card R180 ordered re-measured** |
| `forced(elemental_ecstasy)` | `[elemental_ecstasy]` | register card 4 |
| `forced(kaboom)` | `[kaboom]` | **filler / deck-dilution negative control** |

`control` is run **once** and reused as the paired partner for every `X`, as in
the parent.

---

## 4. Seeds and pairing

- Base seed **11** (the ratified cell). Run *i* of a batch is a pure function of
  `seed + i` (`tier05/model.py`), so pairing is **by index**: run *i* of
  `forced(X)` and run *i* of `control` share seed `11 + i`.
- Registered seed range: `11 … 11 + N − 1`, `N` from §7.
- **Excluded, explicitly:** `424242 …`, the `--smoke` seed base the sweep
  script uses for "does it run" checks (`tier05/exp_eb17p_forced_copy.py`,
  parent §10). Any pre-run check uses `--smoke` and its banner; nothing below
  it may be quoted.
- **The same seeds as the parent are used again, deliberately.** They are the
  ratified cell's seeds. This is **not** a paired comparison against the
  parent's runs — the worlds differ, so a seed number means a different run in
  each. Same seeds, different world, no cross-world pairing. Stated here so
  nobody constructs one at grading time.

---

## 5. The sweep — which cards

**The set is fixed by R180 and may not be narrowed.** All five, in the
register's order, plus the filler:

| id | name | rarity | cost | note |
|---|---|---|---|---|
| `friendly_visit` | Friendly Visit | uncommon | 1 | Block 5 + companion cost −1 + draw 1 |
| `study_buddy` | Study Buddy | uncommon | 1 | Block 6 + replay-next-companion |
| `borrowed_brilliance` | Borrowed Brilliance | uncommon | 1 | free temp copy of a companion in hand |
| `elemental_ecstasy` | "Sweet Dreams" | uncommon | 2 | aura refresh + per-aura draw + conditional Block 8 |
| **`kaboom`** | "Kaboom!" | basic | 1 | **deck-size negative control** |

**5.1 The filler stays `kaboom`.** [USER] chose it on 2026-08-10 and the
reasoning is unchanged: it is a duplicate of Klee's own starting Strike
(`tier0/content/characters/klee.yaml`), so forcing a copy changes the deck's
*size* and its *ratio of basics to everything else*, and nothing else. Its own
Δ-vs-control is the size of pure dilution in this cell, and it is the first row
read at the grade (§9). A test pins that Klee's starter still contains `kaboom`
(`tier05/tests/test_eb17p_force_cards.py`); if it ever stops, the negative
control has quietly become a real card and the test fails.

**5.2 Card-id family.** Every read pools `X` with `X+` (`upgrades.SUFFIX`),
because a smith node rewrites the id in place. A read keyed on the bare id
would score an upgraded forced copy as an absent one.

**5.3 One arm, two names.** "Sweet Dreams" and "Elemental Ecstasy" are the same
card; the sheet renamed it for display on 2026-07-20 and kept the id
(`docs/klee-cards.yaml:178-183`). One registered arm, not two.

**5.4 If the `elemental_ecstasy` redesign lands first.** Then this arm measures
a different card and the packet is re-stamped (to whatever the redesign's own
`CONSTANTS_VERSION` bump makes live — as drafted this line said `C10`, which
was the next integer in 2026-08-13 and is nine behind the world now) before it
runs; the consequences of that ordering are laid out in the companion packet
`review/active/m17-elemental-ecstasy-redesign-2026-08-13.md` §6, and the choice
is [USER]'s. **The arm is not dropped under either ordering.**

**The choice has since been made and this branch is not the one taken.** R189
settled the route as **measure-first**, so the sweep runs before the redesign
and the redesign lands after the graded read as its own `C` bump; R205 then
ruled the redesign's one unsettled sub-shape (Block moves to 5). Verified at
the 2026-08-25 re-stamp: `elemental_ecstasy` still prints
`target_has_nonpyro_aura` and `block: 8` on the sheet, so the redesign has
**not** landed and this arm still measures the card §8's prediction will be
written about. **All five arm cards' sheet rows and upgrade rows are
byte-identical between the `C9` world this packet was drafted in and
`C19`** — checked row by row, not assumed — so the re-stamp moved the world
around these cards without moving the cards.

---

## 6. Metrics — unchanged from the parent

### 6.1 Primary (Q1)
Per card `X`, over the `N` seed-matched pairs:
`delta_win` = winrate(`forced(X)`) − winrate(`control`), with exact McNemar on
the discordant pairs (`b`, `c`) as the test and a paired bootstrap (resampling
*pairs*, own RNG stream, own seed, never a run seed) for the interval.
Discordant and concordant counts are printed; a Δ with no discordant count
beside it is not citable. Unpaired Wilson intervals per arm are printed for
continuity and are **not** the test.

### 6.1b Co-primary — card versus filler
`delta_vs_filler(X) = winrate(forced(X)) − winrate(forced(kaboom))`, paired by
seed index over the same `N` pairs, same machinery. **Retained as a co-primary**
— [USER] added it on the parent's countersign, and it is the contrast that
distinguished "this card is harmful" from "this card is doing nothing" in
§13.4. Both co-primaries are graded; neither may be dropped after the read
because the other was more flattering.

**What §6.1b does not inherit.** Both of its arms are treated, so a §6.1b delta
is **internally valid and externally unanchored** — it may not be quoted against
any archived winrate. If S2 fires, §6.1 is void and §6.1b survives only as a
comparison of two treated arms, and the report must say so.

**No multiplicity correction is registered**, for either contrast, for the
parent's reason: the grade is not a hunt for a significant row. Each card is
graded against a direction and a threshold [USER] wrote down before any number
existed. A row that was not predicted and turns up significant is a hypothesis
for a new registration, not a finding.

### 6.2 Secondary run-level
`delta_act1`, `delta_acts`, `delta_decksize`, `delta_fights` — same pairing,
same reporting shape.

### 6.3 Compliance and contamination census (Q3)
Forced arm: share of runs whose FINAL deck still holds the `X` family; share
removed at rest; share upgraded; mean family copies. Control arm: share of runs
that drafted the `X` family on their own. **This bounds what the design can
see**: a control arm that already holds `X` often attenuates ITT Δ by
construction.

### 6.4 Pre-registered secondary subgroup
Δ restricted to pairs where the control run never acquired the `X` family, with
its own `n`. **Secondary. It may not be promoted to primary after the read.**
(For `kaboom` this subgroup is empty by construction — the parent's was `n = 2`
— and it is reported and disregarded.)

### 6.5 Card-flow read (Q2, Q4)
`metrics.card_flow_profile` over the forced arm's `fight_stats`, restricted to
the `X` family: `draws_per_fight`, `played_when_drawn_rate`,
`dead_in_hand_rate`, `force_first_copy_rate`, printed per form **and**
family-pooled.

**The `borrowed_brilliance` bare-form line is the Q4 read** and the script
already prints it per form, so no new column is needed.

**Instrument visibility (D4), confirmed.** `RunResult.fight_stats` carries the
EB-17 counters through to tier 0.5 and `card_flow_profile` consumes them
unchanged; this is the same one-seat sim instrument the parent used, on the
same objects. No C#-only limb, no `support` term.

---

## 7. Sizing

Unchanged from the parent, and for the same reasons.

**Variance model.** Binary outcome at the run level; for a paired binary
contrast the variance is carried by the discordant pairs,
`SE(Δ) = sqrt(d / N)`. Minimum detectable Δ at two-sided α = 0.05, power 0.80
(factor 2.80):

| pairs `N` | MDE at `d = 0.11` (conservative) | MDE at `d = 0.05` (optimistic) | runs (1 control + 5 treated) |
|---|---|---|---|
| 600 (ratified cell) | 3.8 pp | 2.6 pp | 3,600 |
| 1,200 | 2.7 pp | 1.8 pp | 7,200 |
| **2,400 (proposed default)** | **1.9 pp** | **1.3 pp** | **14,400** |
| 4,800 | 1.4 pp | 0.9 pp | 28,800 |

> **`N` — FILLED 2026-08-13 (R189): 2,400 pairs per card.** The parent's
> registered value, confirmed rather than moved: 2,400 runs on each of six arms,
> 14,400 runs total, conservative MDE **1.9 pp**. Confirming the parent's `N` is
> what keeps this a like-for-like re-read of the same question rather than a
> differently-powered new one.

**A note the parent could not have written.** The parent's §7.1 declined to
register the optimistic column for the card-versus-filler contrast on the
grounds that the correlation between two treated arms was unknown; §13.5
recorded that this refusal *"was correct as discipline and wrong as a guess"* —
the filler contrast resolved best (`d ≈ 0.051–0.092`). **This packet still
registers only the conservative figure**, 1.9 pp at `N = 2,400`, because the
realised `d` in that table is a `P6` observation and the pilot has moved to
`P10` since. Quoting a `P6` discordant rate as this packet's sizing assumption
would be exactly the cross-stamp borrowing §4 forbids — and the gap is four
pilot versions wide now, not one, which strengthens the refusal rather than
weakening it.

**`N` is fixed at countersign and may not be extended after a read.** Adding
runs because an interval "almost" excluded a threshold is optional stopping;
S4 is the only path from a null to more data, and it goes back through [USER].

> **COST CEILING — FILLED 2026-08-13 (R189): 4 hours wall-clock,
> stop-and-report**, the parent's value carried forward. The parent's actual run
> took **2 minutes 57 seconds** for the full 14,400 runs, so the ceiling was
> never approached; it is retained as discipline, not as a live constraint, and
> a ceiling that has never bound is exactly the kind worth keeping.

Stop-and-report means what it says: if the sweep is still running at the
ceiling it stops and reports what it has, the partial result is graded as
partial, the arms that finished are not promoted to the whole answer, and any
grade drawn from fewer than the registered `N` quotes its own realised MDE.

---

## 8. Predictions — **FILLED 2026-08-26. [USER]'s, before any number is read**

Per EXPERIMENTS (*"pre-registered from design intent … never revised against
the playtest that grades it"*) and the R121 precedent that predictions are
authored design-side and appended **as their own commit before any measurement
runs**. **The commit that carries this section is that commit**: it lands
before any seed in §4's registered range has been run, it contains nothing but
the fill, and §8 is not edited again — the grade is written beside it, never
over it.

For **each** arm, [USER] states a direction and a threshold for **both**
co-primaries — an ungraded co-primary is just a number nobody committed to.

| card | §6.1 sign of Δ vs control | threshold (pp) that counts as a real move | §6.1b sign of Δ vs filler | confidence |
|---|---|---|---|---|
| `friendly_visit` | **positive** | **+2 pp — expected to be met or exceeded** | **positive, ≥ +2 pp** | **high** |
| `study_buddy` | **positive** | **+2 pp — probably below it against control** | **positive, probably ≥ +2 pp** | **medium** |
| `borrowed_brilliance` | **positive** | **+2 pp** | **positive** | **LOW** |
| `elemental_ecstasy` ("Sweet Dreams") | **near-null; slightly negative if anything** | **±2 pp — predicted INSIDE the band** | **null — inside ±2 pp** | **medium-high** |
| `kaboom` (filler, negative control) | **slightly negative (dilution)** | **±2 pp — predicted INSIDE the band** | — (it is the baseline) | **high** |

**Disclosure for the grader, recorded with the fill.** These directions were
authored 2026-08-26 with the parent's `P6` read in view — archive under this
packet's own rule (§11), never a comparator. The `friendly_visit`,
`study_buddy`, `elemental_ecstasy` and `kaboom` rows track that read. The
`borrowed_brilliance` row does **not**: it is set from DESIGN INTENT — the
parent's own *"positive, likely ≥ +2"* — rather than from the `P6` zero-plays
read, because `Q4`'s premise is that the `P6` pilot refused the card and the
repaired pilot this sweep runs under does not. A near-null prediction beside a
">5% played" prediction would only cohere if the card failed WHEN PLAYED —
which §8.1's trigger (b) tests independently.

**The ±2 pp threshold is [USER]'s choice**, carried forward from the parent the
same way §8.1's trigger was — not computed from §7's MDE and not derived from
any read.

**Q4 slot — `borrowed_brilliance` bare-form play rate. THRESHOLD FILLED
2026-08-13 (R189): 5%.** `played_when_drawn_rate` on the un-upgraded form is
material at or below **5%** — a bare card the pilot plays fewer than one time
in twenty when it is in hand is a card the pilot is refusing, not a card losing
a close call.

**Recorded as what it is: [USER]'s chosen materiality threshold, NOT derived
from evidence.** The measured `P7` figure quoted by R180 is ~**6.1%**
(60/981); it came from a different read, it is not a prediction, and 5% was not
computed from it. A grader must not later present this number as if the data
implied it. That the ruled threshold sits just under the one figure anyone has
seen is a fact about the threshold, and is written down here rather than
noticed at grading time.

**DIRECTION — FILLED 2026-08-26, with the rest of §8.** The bare form's
`played_when_drawn_rate` is predicted **NON-ZERO and ABOVE the 5% materiality
threshold**: the pilot repair R180 ordered this re-run for has removed the
categorical refusal §13.8 recorded at `P6` (zero plays in 40,396 draws), and
the `P10` pilot the sweep runs under carries it. **No large winrate gain is
predicted from that alone** — the card is situational even when it is played —
so a play rate above 5% sitting beside a small §6.1 delta is the PREDICTED
shape here, not a contradiction to be reconciled at the grade.

**What that prediction rests on, stated so the grade cannot mis-attribute it.**
The reaching change is `P7`'s valuation fix (R176), carried unchanged into
`P10`. §3.1 records that `P9`'s and `P10`'s own limbs provably do **not** reach
this cell, so a nonzero read here is not evidence about either of them.

**A note for whoever transcribes [USER]'s words.** In the parent, [USER] wrote
directions against the control plus one statement about the filler, and the
filler column followed by arithmetic rather than by a second judgement — which
was recorded so a grader could see it was not an independent prediction scored
as a separate success. **If [USER] works the same way this time, record it the
same way.**

**Recorded, 2026-08-26: not the same way.** The filler column above is stated
per row and carries its own qualifiers (`study_buddy`'s "probably", the two
inside-band nulls), so it is a second judgement rather than arithmetic off the
control column, and both co-primaries are graded as independent predictions.

### 8.1 The redesign trigger — **FILLED 2026-08-13 (R189): CARRIED FORWARD UNCHANGED**

The parent's trigger is adopted verbatim as this registration's trigger. Both
of its clauses are expressible in §6's columns — that was checked before the
fill, per the first constraint below — so nothing new is owed and no column is
added at grading time.

The parent's trigger (§8.1 there) was, and now is: a card is a redesign
candidate if
**either (a)** the filler-adjusted result is confidently below −2 pp — read as
the §6.1b interval's **upper** bound below −2 pp — **or (b)** the card performs
no better than filler (Δ vs filler ≤ 0) while its family-pooled
`dead_in_hand_rate` is ≥ 25%.

**It was reproduced here as context and is now the filled slot** — [USER]
carried it forward verbatim rather than amending it. Two constraints applied to
what was written, and both were checked at the fill:

- **A trigger must be expressible in §6's columns**, or it cannot be graded as
  registered. A trigger naming a quantity this sweep does not measure requires
  a new column in a re-registration — never a metric quietly added at grading
  time. (The parent's two clauses both are; anything new must be checked
  before the predictions are committed.)
- **The trigger names a candidate, not a verdict.** Firing it redesigns
  nothing. Whether to redesign, reprice or retire a card is a design act,
  downstream of the grade, and [USER]'s.

**One consequence worth naming before it is written.** If the trigger carries
forward unchanged and fires again for `borrowed_brilliance` under `P7`, R180's
"remeasure before any design act" condition is discharged and the design act
becomes available. If it does **not** fire under `P7`, that is the finding
R180 was asking for, and `borrowed_brilliance` needs no redesign. Both outcomes
are useful; neither is predicted here.

---

## 9. Grading procedure and stop conditions

**Blind.** The runner writes one report; grading compares it against §8's
committed table **without editing §8**. The predictions commit must exist
before the sweep is launched, and the sweep's report is not opened by the
author of the predictions before the grade is recorded.

**Order of operations — RECONCILED 2026-08-24 to R189's ruled sequence.** As
first drafted, this list put the countersign at step 1 and asked [USER] to fill
§7's `N` and cost ceiling at step 3. Both were stale: R189 (2026-08-13) filled
§7 already, and ruled that **predictions are filled against the settled world,
before the countersign** — which is what the header note above says and what
§9.1 sequences. The list contradicted them; it now agrees with them. Nothing
about the grading discipline changed, only the order this file states.

1. The open `RT`/`C` window closes — **DONE 2026-08-24.** The window closed
   and the world kept moving after it; `EB-118`'s richness pass ran to
   completion on 2026-08-25 and `EB-136` landed inside the same span.
2. **Re-stamp §3 if the world moved** — **DONE 2026-08-25**,
   `RT10/D14/P7/C9` → `RT12/D17/P10/C19`, with §3.1 recording what the move
   reaches. A world that moved and was not re-stamped is an S1 event at
   launch, not a detail.
3. Confirm the §10 engineering prerequisites still hold at the new stamp,
   suite green — **DONE 2026-08-25; tallies at §10.1.** (They are built;
   §10 is a re-verification, not a rebuild.)
4. **[USER] fills §8** — the per-arm prediction table and the DIRECTION half of
   the `Q4` slot — and it is committed as **its own commit, nothing else in
   it.** (§7's `N` = 2,400 pairs and the 4-hour cost ceiling are already
   filled, R189, and are not re-asked here; §8.1's redesign trigger is filled
   too.) **DONE 2026-08-26** — its own commit, nothing else in it, taken before
   any seed in §4's registered range had been run.
5. **Countersign this packet.** **OPEN — [USER], QUEUE `M17`.**
6. Run the sweep at the pinned stamp. Report only; read nothing into it.
   **The exact command is at §9.2**; nothing is left to decide at run time.
7. Blind grade against §8; the grade is its own commit.
8. Any design act is downstream of the grade and is [USER]'s.

**Steps 1–3 are marked DONE in place rather than removed, because they are the
record of what the re-stamp discharged.** Everything ahead of the run is now
steps 4 and 5, and both are [USER]'s.

**Order of reading, at the grade** — this order and no other, because reading
them in any other order lets one number colour the next:

1. The **compliance census** (§6.3), per card. If a card's assignment did not
   survive, or the control arm drafted it constantly, that card's grade is
   settled here as *underpowered by contamination* and its deltas are not
   graded at all (S4).
2. The **filler's §6.1 row** — the size of pure dilution in this cell.
3. Each card's **§6.1** delta against control, versus its §8 prediction.
4. Each card's **§6.1b** delta against filler, versus its §8 prediction.
5. The §6.2 secondaries, the §6.4 subgroup and the §6.5 card-flow columns, as
   description — **including the Q4 bare-form line.**

A card is graded **PREDICTED** only if both co-primaries land as §8 said they
would. One right and one wrong is **SPLIT**, with which half went wrong named —
not rounded to whichever half agreed.

**Stop conditions / tripwires — the run stops and re-registers if:**

- **S1.** Any of `RT/D/P/C` differs at launch from **`RT12/D17/P10/C19`**.
  (Re-stamped 2026-08-25; it named `RT10/D14/P7/C9` as drafted. A tripwire left
  naming a superseded world does not catch a divergence — it fires on every arm
  of every run because its string is stale, which is a citation defect and not
  a finding. That is the `P12` lesson from the payoff-reach registration,
  applied here before the run rather than after it.)
- **S2.** The `force_cards=None` byte-identity pin fails — the control arm is
  then not an anchor and nothing in the report is comparable to the roster
  table.
- **S3. SPENT — it cannot fire and it is not deleted.** As written it stopped
  the run if "the staged `EB-43` / **`DRAFTER 15`** change has landed", because
  R121's order placed `D15` at step (5), after blind-first grading of the
  payoff-reach sprint, and a sweep run across that landing is a sweep run in
  two worlds. **`D15` landed 2026-08-24**, and `D16` and `D17` landed after it.
  The condition it guarded — this sweep straddling the `D15` boundary — is now
  impossible: the boundary is behind the packet, not ahead of it. What S3
  protected is now protected by **S1**, which pins all four fields at
  `RT12/D17/P10/C19` and fires on a bump in any direction. **The two-way fork
  S3 offered resolved to the re-stamp arm**, as `M17`'s own row and
  EXPERIMENTS both record.
  **Its parenthetical was a prediction and events falsified it, which is worth
  recording rather than quietly deleting.** It read: "`EB-43` = `D15` is
  registered law. **`EB-28` = `D16` and `EB-32` = `P8` are plausible inference
  and are NOT registered law** — R180 says so explicitly, and this tripwire
  does not silently extend to them." The refusal to extend was right, and the
  inference was wrong: **`D16` and `P8` were both taken by `EB-118` Phase 2**
  (`D16` at `6056a05`, `P8` at `d3bf0e0`, both 2026-08-24, window order by
  R191), not by `EB-28` or `EB-32`. Declining to bind a tripwire to an
  unregistered guess is exactly why nothing had to be unwound when the guess
  turned out false.
- **S4.** Compliance (§6.3) collapses — the forced copy fails to survive to the
  final deck in a large share of runs, or the control arm's natural acquisition
  is so common that ITT cannot separate the arms. The grade is recorded as
  **underpowered by contamination, not null**, and any re-run is a new
  registration.
- **S5.** A null read at the registered `N` is graded as **"no move larger than
  the §7 MDE"** — never as "no effect". The MDE is quoted with it, and §6.1b
  quotes the conservative 1.9 pp figure at `N = 2,400`.
- **S6 (new here). LIVE, and narrower than it was.** **The
  `elemental_ecstasy` redesign lands after this packet is countersigned but
  before it runs.** That is a `CONSTANTS_VERSION` bump, so S1 catches it
  mechanically; S6 exists to name the expected case rather than leave it to be
  discovered as a surprise. The remedy is a re-stamp of §3 and a fresh look at
  §8's `elemental_ecstasy` row, because the prediction would have been written
  about a different card. **What narrowed it:** R189 settled the route as
  measure-first and R205 ruled the redesign's shape (Block moves to 5), so the
  redesign is scheduled *after* the graded read by ruling, not merely by
  preference. Verified 2026-08-25: the card still prints
  `target_has_nonpyro_aura` and `block: 8`, so it has not landed early.

### 9.1 Sequencing — when this may run. **DISCHARGED 2026-08-24; recorded, not pending.**

**Every step this section ordered ahead of the sweep has landed.** The
payoff-reach freeze (`P12`) ran from its freeze act to its graded read with no
`RT`/`D`/`P`/`C` bump inside it, the sprint was graded blind on 2026-08-24, and
`EB-43`'s `D15` landed the same day as step (5) of R121's order. **Nothing in
this subsection gates the sweep any more.** It is kept because it is the record
of the order the run was registered under, and a grader reading the report
needs to know the sweep ran *after* payoff-reach rather than beside it.

**This sweep does not run during the payoff-reach freeze window unless the
world is identical to the one it is registered against.** (The freeze is over;
the sentence is the registered condition, not a live constraint.)

The registered experiment order, per the approved **settle-first** plan
(`payoff-reach-reregistration.md` §6.6 P12; EXPERIMENTS, Active registrations):

1. The open `RT`/`C` window lands — `M14`'s batch (`EB-70`, the `EB-82`
   conversion, the `EB-85` batch, `EB-69`) — and a dependency re-check passes.
2. The payoff-reach registration re-stamps its §6 **if the world moved**, then
   the freeze begins: **no `RT`/`D`/`P`/`C` bump lands on the sprint's branch
   until its graded read.**
3. The payoff-reach sprint runs under the pinned `D14`, and is graded
   blind-first.
4. **This sweep runs after that**, at whatever `RT/D/P/C` is live at that
   moment — which must be re-verified against §3 and is an S1 event if it
   differs.
5. Then the staged `EB-43` / D15 lands with its re-baseline (R121 step 5). This
   sweep must be graded before that, or S3 fires.

**Why this ordering and not the reverse.** Both registrations are pinned at
`D14`; both want one world for the duration; and R180 states the `P7` remeasure
*"slots in after payoff-reach under the pinned D14 — that ordering is the
experiment order"*. This packet does not propose changing it.

**The interaction with the redesign, in one line.** If [USER] chooses
redesign-first (companion packet §6, Route 2), the redesign is a `C` bump and
therefore cannot land inside the freeze either — it lands before the freeze
begins or after the payoff-reach graded read, and this packet is re-stamped to
whatever that bump makes live before it runs. (As drafted this line said `C10`;
R189 then chose **measure-first**, so Route 2 is not the route and the
re-stamp it describes is not owed.)

**How step 5 came out, since the list above ran.** Step 4 — "this sweep runs
after that, at whatever `RT/D/P/C` is live at that moment, which must be
re-verified against §3 and is an S1 event if it differs" — is exactly what the
2026-08-25 re-stamp did: the live world was re-verified against §3, it differed,
and §3 was moved to match rather than the difference being discovered at launch.
Step 5's "this sweep must be graded before `D15` lands, or S3 fires" is the
clause that went the other way: `D15` landed first, so that arm is spent and
S3 is spent with it (§9, S3).

### 9.2 The exact run, once §8 is filled and the packet is countersigned

**Nothing here is a decision.** Every value below is already registered: the
cell is §3's, `N` is §7's, the arms are §5's, and the script is §10.4's,
reused as-is. This block exists so that step 6 is typing, not judgement.

Run from the repo root. `PYTHONPATH=.` is required for the sim entry points
(`OPERATIONS.md`).

**(0) Confirm the world, before anything else.** S1 is a stop condition, so it
is checked rather than assumed:

```
PYTHONPATH=. python3 -c "from tier05 import cells; v=cells.CANONICAL.versions; print('RT{RT}/D{D}/P{P}/C{C}'.format(**v))"
```

This must print exactly `RT12/D17/P10/C19`. **If it prints anything else, S1
has fired: stop, do not run the sweep, and re-register.**

**(1) The sweep — the registered range, once.**

```
PYTHONPATH=. python3 -m tier05.exp_eb17p_forced_copy --runs 2400 --jobs 0 | tee review/active/m17-sweep-results-2026-08-25.txt
```

- `--runs 2400` is §7's registered `N`, 2,400 pairs per card. **It is fixed at
  countersign and may not be extended after a read** (§7).
- `--jobs 0` is "use every core" and moves no registered value; the parent ran
  14,400 runs in 2 min 57 s, against §7's 4-hour stop-and-report ceiling.
- **No `--seed` and no `--route`.** The registered seed base is 11 and the
  route is `hunter`, both from `cells.CANONICAL`; passing either would override
  a registered value.
- **`--smoke` must NOT be passed.** It moves every arm onto seed base
  `424242`, which §4 excludes by construction. Use it for "does it run"
  checks only, never for the sweep.
- The header the script prints carries the stamp
  (`cell=eb17p[runs=2400] seed=11 runs=2400 RT12/D17/P10/C19`), which is what
  makes the report citable under R68. The cell label reads `eb17p[...]` rather
  than `m17p7` for the reason recorded at §10.1.

**(2) Publish the raw output, unedited**, on the `EB-17p` and payoff-reach
precedent: the instrument's own stdout with a provenance header naming the
registration, the run date, the world, the instrument and the commit — not a
rewrite. The filename above is the convention (`*-results-<date>.txt` beside
the packet).

**(3) Grade blind, in §9's prescribed order of reading**, against §8's
committed table, **without editing §8**. The grade is its own commit.

**The output of (1) is not opened by whoever authored §8 before (3) is
recorded.** That is the blind in blind grading, and it is the one step in this
block that a command cannot enforce.

## 10. Engineering prerequisites — built, and RE-VERIFIED at the new stamp

All of the parent's five prerequisites are **already built and in the tree**;
nothing new is owed. What was owed before the countersign is a
**re-verification at the new stamp**, not a rebuild — **and it is DONE,
2026-08-25, at `RT12/D17/P10/C19` on `main` = `1eb5b45`.** The tallies are at
§10.1. The list below is the register of what had to hold:

1. `force_cards` on `model.run_one` / `run_many` / `_setup_run` / `Cell`,
   applied at the end of `_setup_run`, default `None` — **built**.
2. The `force_cards=None` byte-identity test (the precondition for S2) —
   **built**, and it must pass at `RT12/D17/P10/C19`, not merely at
   `RT9/.../C8` or at the `RT10/.../C9` this line named as drafted.
3. The forced-id-present + run-start-RNG-unchanged test — **built**.
4. `tier05/exp_eb17p_forced_copy.py`, the sweep script — **built**; it takes
   `--runs`, `--jobs` and the `--smoke` flag that moves every arm onto the
   §4-excluded seed base and prints a banner saying nothing below it may be
   quoted. **The script is reused as-is; no arm, column or default is edited
   for this packet.** Only the cell name and the stamp differ, and both come
   from the live world.
5. Pairing helpers (`mcnemar_exact`, paired bootstrap) in `tier05/stats.py` —
   **built**.

**Re-verification checklist for §9 step (3)** (as drafted this said "step (2)",
which was the pre-reconciliation numbering): run the full suite green; confirm
the byte-identity test passes at the pinned stamp; confirm
`tier05/tests/test_eb17p_force_cards.py`'s `kaboom`-in-starter pin still holds
after the rarity movement in the range (the `C9` X7/X8 promotions moved Commons
to Uncommons and did not touch Klee's starter, and nothing from `C10` to `C19`
touched it either, so this is expected to pass — it is listed because "expected
to pass" is not "checked").

### 10.1 The re-verification, executed

Taken 2026-08-25 on `main` = `1eb5b45`, in a sibling worktree, at the live
`RT12/D17/P10/C19`. **Nothing in §5's registered seed range was run**, and
nothing below is a measurement of this experiment.

| check | command | result |
|---|---|---|
| prerequisites 1–5, all pins | `python -m pytest tier05/tests/test_eb17p_force_cards.py -q` | **13 passed** |
| suite green (fast lane) | `python -m pytest -m "not battery" --ignore=tier0/tests/test_card_distinctness.py -q` | **3297 passed, 45 skipped, 84 deselected, 13 xfailed** |
| lints | `python tools/run_lints.py --lane ci` | **14 lints passed** |
| the script still runs, on the §4-EXCLUDED seeds only | `PYTHONPATH=. python3 -m tier05.exp_eb17p_forced_copy --smoke --runs 6 --jobs 0` | banner printed; header reads `cell=eb17p-SMOKE seed=424242 runs=6 RT12/D17/P10/C19` |

Named pins behind prerequisite 2 and 3: `test_force_cards_none_is_byte_for_byte_unchanged`,
`test_force_cards_none_batch_is_element_for_element_identical`,
`test_forced_id_is_in_the_deck_at_run_start`,
`test_run_start_rng_consumption_is_unchanged_by_injection`, and — the §10
checklist's own item — `test_the_filler_is_klees_own_basic_attack`. **S2's
precondition therefore holds at the new stamp**, so the control arm is still an
anchor.

**The smoke run's output is not quotable and was not read past the header**, per
§4: `--smoke` moves every arm onto seed base `424242`, which §4 excludes by
construction, and its banner says so in the file's own words.

**One naming reconciliation, recorded rather than performed silently.** §3 calls
this cell `m17p7`; the script's `BASE` is `cells.CANONICAL.but(character="klee",
archetype="reaction", name="eb17p")` (`tier05/exp_eb17p_forced_copy.py:66-67`),
and `cells.parse_overrides` accepts only `--runs/--seed/--route/--jobs` — there
is no `--name`. Since §10.4 forbids editing the script for this packet, the run
will stamp itself `cell=eb17p[runs=2400]`. **Every field that is not the label
is identical** — character, archetype, seed, route, policy, loadout, acts — so
`m17p7` and `eb17p[runs=2400]` name one cell. The label in the report is the
script's; `m17p7` is this packet's name for it. (Same shape as the payoff-reach
registration's `C1` arm-naming reconciliation: recorded, not resolved by editing
a frozen instrument.)

---

## 11. Known limits, declared

- **ITT, not per-protocol.** A removed or upgraded copy stays in its assigned
  arm; assignment is at run start and compliance is measured, never enforced.
- **Deck dilution is confounded with the card** without the filler arm; with
  it, dilution is measured, not assumed away.
- **One cell.** `klee/reaction`, `assigned`, `hunter`, realistic. Nothing here
  generalises to another plan, another route, or the adaptive policy.
- **One seat.** The sim models one seat; nothing about co-op is measurable here.
- **The filler contrast is unanchored.** Both of its arms are treated, so a
  §6.1b delta may not be set beside any archived winrate.
- **Two copies look alike.** When a treated run ends holding two copies of the
  swept family, nothing distinguishes the forced copy from a drafted one; §6.3's
  columns are counts of the **family**, and are labelled that way in the output.
- **No cross-stamp comparison.** Nothing in this packet's output may be
  differenced against `EB-17p` §13. The two reads describe two worlds. Where
  this packet's grade wants to say "it moved", the honest sentence is "the
  earlier world read X, this world reads Y", with both stamps printed.
- **The pilot is not validated by this sweep.** This measures cards under
  `P10`; it does not test whether `P10`'s valuation — or `P7`'s, `P8`'s or
  `P9`'s inside it — is *right*. That is a different question and would be a
  different registration. **This limit got wider at the re-stamp, not
  narrower:** as drafted it disclaimed one pilot version, and the packet now
  runs three further ones deep.

---

## Countersign line — one word, [USER]: COUNTERSIGN / REVISE / DECLINE

`________`

**Slots FILLED 2026-08-13 by R189:** §7 `N` = 2,400 pairs/card, §7 cost ceiling
= 4 hours stop-and-report, §8.1's trigger carried forward unchanged, and §8's
`Q4` materiality threshold = 5%.

**Slots STILL OPEN:** §8's per-arm prediction table (direction, threshold,
filler sign and confidence for all five arms) and the direction half of the
`Q4` slot.

**The countersign was WITHHELD by R189 until after the post-window restamp** —
the world moves at the close of the open `RT`/`C` window and predictions are
filled against the settled world. **THE RESTAMP IS DONE (2026-08-25,
`RT12/D17/P10/C19`), so the condition R189 withheld the countersign on is
satisfied and the countersign is next.** What stands between this packet and
its run is now exactly two [USER] acts, in this order: **fill §8** (the per-arm
prediction table and the direction half of the `Q4` slot), then **countersign
above**. §9.2 is the run, and it is mechanical. **Until both are done the
packet is NOT cleared to launch and no seed in the registered range may be
run.**

— drafted 2026-08-13 on branch `overnight-burn-2026-08-12`, per QUEUE `M17` /
R180. **Re-stamped 2026-08-25 at `main` = `1eb5b45`** under R189's own
sequence — execution, not a new ruling. Zero design authority exercised: every
threshold, direction and taste call is [USER]'s, §8 is untouched and still
blank, and the `Q4` estimand was deliberately not measured. The frozen
`EB-17p` registration and results file were read and not edited (R101b).
