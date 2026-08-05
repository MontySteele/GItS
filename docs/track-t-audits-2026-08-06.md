# Track T — mechanical audits ordered by the 2026-08-06 sitting (families X2, X7, X8)

Batch: "Second Wind". Base: `main` @ e43d57c. Branch: `findings/track-t`.
Authority: [USER]'s 2026-08-06 sitting verdicts on the S13 exploit ledger
(`review/redteam/exploit-ledger.md`, families X2 / X7 / X8).

**Standing scope.** Two of the three sweeps are FINDINGS ONLY (T-2, T-3): the verdicts
order a check, not a change. The one ratified action lives in §1. No constants, no card
stats, no schema, no drafter code, no `RARITY_ODDS` were touched anywhere in this branch.

**Instrument.** All three sweeps read the loaded card index
(`tier0.content.loader._card_index()`), which is the union of every committed sheet:

| sheet | rows |
|---|---|
| `docs/klee-cards.yaml` | 76 |
| `docs/furina-cards.yaml` | 82 |
| `docs/kokomi-cards.yaml` | 61 |
| `docs/mondstadt-companions.yaml` | 17 |
| `docs/fontaine-companions.yaml` | 19 |
| `docs/inazuma-companions.yaml` | 15 |
| `tier0/content/cards/colorless_event.yaml` | 2 |
| `tier0/content/cards/curses.yaml` | 9 |
| `tier0/content/cards/ironclad_starter.yaml` + `ironclad_package.yaml` | 3 + 6 |
| `tier0/content/cards/silent.yaml` | 6 |
| `tier0/content/cards/tokens.yaml` | 2 |
| **total** | **298** |

**Scope limitation, stated rather than hidden.** The worktree has no `game_ref/`, so the
sweeps ran under `GITS_REFERENCE_MODE=committed-only` and the two base-game reference
pools (`real_ironclad`, `real_silent`, loaded from the gitignored `ironclad_pool.yaml` /
`silent_pool.yaml`) are ABSENT from the 298. Those are decompiled base-game rows, not
mod content, and the X2/X7/X8 verdicts are about mod cards — but a base-game 0-cost
cantrip would not have been seen by §1. Re-running §1 on a checkout with `game_ref/`
present is a five-minute job and is the honest way to close that hole.

Upgraded forms were read through `loader.get_card("<id>+")` (a fresh deep copy).
NOTE for anyone re-running this: `loader.peek_card()` returns the SHARED prototype and
`upgrades.apply_upgrade()` mutates in place — calling `apply_upgrade(peek_card(x))`
silently corrupts the card index for the rest of the process. Use `get_card("<id>+")`.

---

## 1 · T-1 (family X2) — self-replacing 0-cost non-exhaust engines

**Verdict (verbatim).** "Not a problem; power in line with existing Uncommon Colorless…
infinite cycling engines gated to Uncommon rarity or higher. **If this is Common, it
needs a bump.**"

### 1.1 Methodology — the predicate

A row is a **match** when all three hold on its PRINTED (base) form:

1. `cost == 0`;
2. `exhaust` is falsy (it returns to a pile and comes back around);
3. it puts a replacement for itself back into hand — operationally, its
   **net hand delta is ≥ 0**: `draw − discard − exhaust_from − discard_for_sparks ≥ 1`
   unconditionally, or an op that adds a copy of the card itself to hand/deck.

Legs 1+2+3 together are exactly the `sayu_naptime` shape the ledger names: 0 energy in,
0 cards out, so the play is free in both currencies and repeats until the engine's
25-play degeneracy detector fires (`combat.py:505-514`).

`scry_discard` is NOT counted as a hand cost (it discards from the draw pile).
Conditional draw (inside a `conditional` op or carrying an `if:`) is counted separately
and never promotes a row to "match" — a conditional replacement is not an unconditional
engine. Upgraded forms are reported separately in §1.4 and are NOT matches.

Reproduce: 41 of the 298 rows are 0-cost non-exhaust; filter them by legs 3.

### 1.2 Matches (printed form)

| card id | sheet / pool | rarity | cost | effects | net hand delta |
|---|---|---|---|---|---|
| `sayu_naptime` | inazuma companions | **uncommon** | 0 | block 3 + draw 1 | 0 (hand-neutral) |
| `sucrose_gust` | mondstadt companions | **common → uncommon** | 0 | swirl + draw 1 | 0 (hand-neutral) |
| `florid_cadenza` | furina-cards | **uncommon** | 0 | draw 1 (+2 if fanfare ≥ 12) | +0 / +2 |

Three matches, one of them Common. Two of the three are already at or above the gate.

`sucrose_gust` is `sayu_naptime`'s shape line for line: printed 0-cost, non-exhaust,
draws its own replacement — it just swirls instead of blocking. It is not a theoretical
match: S13's own corpus already runs it as the engine of two centrally-replayed lines,
`klee_bombs_3_swirl_spark_free_bomb_infinite` (infinite, verified) and
`klee_bombs_4_swirl_spark_attrition_t1_clear`, whose hypothesis says in as many words
that `sucrose_gust+` "replaces itself AND re-triggers a reaction on every single play,
forever". Both lines run 14 copies of it.

### 1.3 Action taken

**`sucrose_gust`: `rarity: common` → `rarity: uncommon`** in
`docs/mondstadt-companions.yaml`, per sitting 2026-08-06 family X2. Rarity field only —
cost, effects, star, element, role, type and the upgrade row
(`docs/klee-upgrades.yaml:98`, `draw: +1`) are untouched.

One consequential bookkeeping edit rode along, and it is called out here rather than
buried: the bump made `sucrose_gust` (now uncommon) strictly dominate `moon_signal`
(common) at cost 0, which `tools/lint_strict_domination.py` fails on as a NEW cross-sheet
finding. The identical pair `sayu_naptime`→`moon_signal` is already an allowlisted,
red-pen-queued entry in that lint; `sucrose_gust`→`moon_signal` was added beside it with
the same rationale, because the finding is INHERITED from the ratified rarity move and is
not a new design choice. Nothing was suppressed: the entry is enumerated, and
`test_the_cross_sheet_allowlist_is_not_stale` deletes it the day the pair stops
dominating.

Parity note for the docket (no action taken): the C# side reads companion rarity from
`Star`, not from the sheet's `rarity` field — `KleeCode/Cards/Generated/SucroseGust.cs`
carries `rarity=common` only in its `<auto-generated>` header comment and exposes
`public int Star => 4`. So this bump moves the **sim** reward tier and the design sheet,
and the mod's reward tier for companions is driven by star elsewhere. Whether the gate
is therefore enforceable in C# at all is a question for the implementer's parity check,
not something this sweep may decide.

### 1.4 Borderline — reported, NO action taken

**(a) Upgrade-gated engines.** These are Common (or basic) rows whose PRINTED form fails
the predicate and whose UPGRADED form passes it. They are 0-cost, non-exhaust and
self-replacing once upgraded, so they are within the verdict's *language* ("infinite
cycling engines") while sitting outside its *mechanical audit* line, which names
"self-replacing 0-cost non-exhaust **companions**" — and none of these is a companion.
Held for a one-line ruling on whether the gate reads printed or upgraded form.

| card id | base rarity | printed form | upgraded form | net hand delta (+) |
|---|---|---|---|---|
| `quick_fuse+` | common (klee) | detonate | detonate + **draw 1** | +0 (self-replacing) |
| `to_the_front+` | common (kokomi) | conscript 1 | conscript 1 + **draw 1** | **+1** (hand-positive) |
| `moon_signal+` | common (kokomi) | discard 1 + draw 1 | discard 1 + **draw 2** | +0 (self-replacing, pays a discard) |
| `sucrose_gust+` | (now uncommon) | swirl + draw 1 | swirl + **draw 2** | **+1** |
| `sayu_naptime+` | uncommon | block 3 + draw 1 | block 3 + **draw 2** | **+1** |
| `florid_cadenza+` | uncommon | draw 1 (+2 cond.) | **draw 3** flat | **+2** |
| `tactical_retreat+` | basic (kokomi) | draw 1 + discard 1 | draw 2 + discard 2 | −1 (fails) |

`to_the_front+` is the sharpest of these: 0-cost, non-exhaust, conscripts a companion
AND draws its own replacement, at Common.

**(b) Enabler-dependent 0-costs.** `barbara_shining_idol` (mondstadt, **uncommon**,
printed cost 1, block 5 + apply hydro + draw 1) is the ledger's named block variant of
this family, but it only reaches 0 cost through X1's `companion_cost_delta_this_turn`
accumulator. It is not printed 0-cost, so it fails leg 1 and is outside the predicate.
Already at Uncommon in any case.

**(c) Conditional replacement.** `curtain_cue` (furina, **uncommon**, 0-cost,
non-exhaust) draws 1 only when `spotlight_moved_this_turn`. Conditional, and already
above the gate.

**(d) Hand-neutral but non-cycling.** `to_the_front` (kokomi, **common**, printed form)
is 0-cost and hand-neutral — but the card it adds is a conscripted *companion*, not a
copy of itself, so the loop terminates after one iteration. Excluded on leg 3.

**(e) Fails leg 3 on a sink** (listed so the denominator is visible): `crackle`,
`ebb_tide`, `pearl_diver` / `pearl_diver+`, `steady_the_line`, `whispered_word`,
`moon_signal` (printed), `study_of_explosions`, `curtain_up`, `tactical_retreat`.

---

## 2 · T-2 (family X7) — the Klee pool against the new spark law

**Verdict (verbatim).** "Gate repeatable spark generation behind Uncommon **or** make
sure no card below Rare is both 'sparks + draw enabler'."

The verdict is disjunctive as stated, and the sitting record routes it as such. This
sweep reports both legs independently so the disjunction can be resolved at the docket
rather than guessed here.

### 2.1 Methodology

Population: the 76 rows of `docs/klee-cards.yaml` (`character == "klee"`), plus a
whole-index cross-check for spark generation outside Klee's personal sheet.

- **Spark generator** = the row resolves `gain_spark` or `discard_for_sparks`, at any
  nesting depth (top level or inside a `conditional` branch), OR applies a power whose
  implementation mints sparks: `spark_per_turn` (`effects.py:2389`),
  `bomb_and_spark_per_turn` (`effects.py:2392`), `sparks_n_splash`,
  `reaction_bonus_spark_energy` (`reactions.py:159-162`). Power-based generation was
  swept explicitly — an op-name-only filter misses it, and a per-turn power is the
  purest form of "repeatable".
- **Repeatable** = the generation can fire more than once per combat: the card is
  non-`exhaust` (so it recurs every deck cycle), or it applies a persistent per-turn
  power. A one-shot self-exhausting generator is NOT repeatable.
- **Draw-enabler** = the row resolves a `draw` op (flat, formula, or conditional).
  Discard/scry/exhaust-selection ops are NOT counted as draw.
- "Below Uncommon" = `basic` or `common`. "Below Rare" = `basic`, `common`, `uncommon`.

### 2.2 Leg (a) — "repeatable spark generation gated behind Uncommon"

**6 violations, all Common, all non-exhaust.**

| card id | rarity | cost | exhaust | spark generation | printed / upgraded |
|---|---|---|---|---|---|
| `crackle` | common | 0 | no | `discard_for_sparks` 1 (sparks 1) | → 2 (sparks 2) |
| `skip_and_hop` | common | 0 | no | `gain_spark` 1 | 1 |
| `sparkly_treasure` | common | 0 | no | `gain_spark` 1 | → 2 |
| `snap` | common | 1 | no | `gain_spark` 1 | 1 |
| `spark_collection` | common | 1 | no | `gain_spark` 2 | → 3 |
| `warm_glow` | common | 1 | no | `gain_spark` 1 | 1 |

No `basic` Klee row generates sparks. Compliant rows above the line, for contrast:
`sugar_rush`, `hot_hands`, `cant_catch_me`, `endless_fireworks` (`spark_per_turn`),
`catalytic_conversion` (`reaction_bonus_spark_energy`) at **uncommon**;
`all_my_treasures`, `da_da_da`, `sparkly_explosion`, `playtime_forever`,
`sparks_n_splash`, `true_spark_knight` at **rare**.

Cross-check outside the Klee sheet: exactly one non-Klee row mints sparks —
`prune_witch_hunt` (mondstadt companion, **uncommon**, 1-cost, non-exhaust,
`gain_spark` 1 unconditional plus 1 more on a reaction). Uncommon: compliant with
leg (a), and it carries no draw, so compliant with leg (b) too.

**Reading note the docket needs.** Under a strict reading of "repeatable" — *the card
generates sparks more than once per PLAY, or closes a loop* — the count drops to **0
Commons**: the loop in X7(a) is `sugar_rush+` (uncommon, whose upgrade is
`{remove: exhaust}`) and `bright_idea` (uncommon), not any Common. Under the plain
reading — *a Common that mints sparks and can be replayed every deck cycle* — it is the
6 rows above, which is most of Klee's Common spark economy. Both counts are stated
because which one the law means is a design call, not a sweep result.

### 2.3 Leg (b) — "no card below Rare is both spark-generator and draw-enabler"

**1 violation.**

| card id | rarity | cost | effects |
|---|---|---|---|
| `cant_catch_me` | **uncommon** | 1 | block 2 (→4) + `gain_spark` 1 + `draw` 1 |

`cant_catch_me` is both legs on one printed row, at Uncommon, non-exhaust, and its
upgrade keeps both. It is the only card in the entire 298-row index below Rare that
generates a spark and draws a card.

Borderline, reported, no action:

- `crackle` (common) — `discard_for_sparks` is a forced hand *discard*, the inverse of
  a draw enabler. Counted as spark-gen only. It is however the closest adjacent shape,
  since hand-filtering and drawing are neighbours in deck-quality terms.
- `eager_to_help` (common, 1-cost) — `has_spark ? draw 3 : draw 2` (upgraded). A
  draw-enabler whose SIZE keys off the spark bank, but it mints nothing. Fails the
  generator leg; it is the tightest "spark + draw" *adjacency* below Rare and the docket
  should see it if the law is meant to bar the pairing rather than the ops.
- `borrowed_brilliance+`, `study_buddy+`, `bright_idea`, `alchemical_curiosity`,
  `ammo_scavenging`, `combustion_study`, `friendly_visit`, `quick_fuse+`,
  `elemental_ecstasy` — draw-enablers below Rare with no spark generation. Compliant.

### 2.4 Action

**None.** Findings only, per the task and per the routing line in the sitting record.

### 2.5 POINTER — the reading question in §2.2 was answered (2026-08-06)

*Appended by Track W. Nothing above is rewritten; §2.2's two counts stand as
this sweep produced them.*

[USER] ruled the limb-(a) reading on **2026-08-06**, verbatim: ***"infinite
sparks must not be achievable at Common"*** — some Common spark generation is
fine. Neither of §2.2's two counts is the answer: the criterion is
**unboundedness**, not "mints sparks" (broad) and not "loops per play"
(strict).

The six broad-reading candidates were re-read one by one against that
criterion, to the S13 evidentiary standard (a committed, replay-verified line
on a Common-or-lower deck). **3 violations** — `crackle`, `skip_and_hop`,
`sparkly_treasure`, all the 0-cost ones, all riding one Common cost-floor
engine — and **3 cleared** — `snap`, `spark_collection`, `warm_glow`, held down
by the 3-energy turn budget with no Common energy or cost reduction able to
reach them.

- Verdict table, the engine, and the bound that clears each survivor:
  `docs/dockets/klee-rework.md` **§2c**.
- The annotation itself: `tier0/DECISIONS.md`, R109, dated [USER] annotation.
- Lines and replay results: `review/redteam/exploit-lines-x7a.json`,
  `review/redteam/replay-results-x7a.json`.

Limb (b) (§2.3) is untouched by the clarification.

---

## 3 · T-3 (family X8) — the two uncapped bomb-damage terms

**Verdict (verbatim).** "Not a problem at higher rarity — need to check these cards."

### 3.1 Identification of the two terms

From `review/redteam/exploit-ledger.md` §X8 and the cited code, bomb damage is
`dmg = bomb.damage + bonus + p.powers["bomb_damage_up"]` at `effects.py:443`, and the
family's two uncapped terms are:

**Term 1 — the additive PER-BOMB damage bonus.** Four independent writers, none of them
capped per card, per bomb, or per turn:

| writer | site | mechanism |
|---|---|---|
| `modify_bombs` op | `effects.py:925-930` | adds `bonus` to `bomb.damage` for every bomb on every living enemy |
| `move_bombs` op | `effects.py:907-922` | adds `bonus` to `bomb.damage` for each bomb it gathers |
| `detonate` op's `bonus` kwarg | `effects.py:904` → `detonate_bombs(..., bonus=)` | rides `dmg` for every bomb in the volley |
| `bomb_damage_up` power | `effects.py:443` | flat per-bomb adder, permanent for the combat |

**Term 2 — `detonations_total`.** A monotonic per-combat counter incremented once per
bomb detonated (`effects.py:444`), never decayed, never spent, with no ceiling
(`state.py:515`). It is consumed as a raw multiplier by the `N_per_detonation_this_combat`
bonus formula (`effects.py:66-67`).

The product of the two is the family: term 1 raises what each detonation is worth, term 2
counts them forever and sells the count back as damage.

### 3.2 Term 1 carriers — every card that writes a per-bomb bonus

| card id | name | rarity | cost | exhaust | bonus (printed → upgraded) |
|---|---|---|---|---|---|
| `chain_fuse` | Chain Fuse | **common** | 1 | no | `modify_bombs` scope `placed_this_turn`, **+3 → +5** per bomb, plus places 1 |
| `careful_arrangement` | Careful Arrangement | **common** | 1 | no | `move_bombs`, **+2 → +4** per bomb moved |
| `remote_detonator` | Remote Detonator | **uncommon** | 1 | no | `detonate` all enemies with **bonus 2 → 4** per bomb |
| `explosives_workshop` | Explosives Workshop | **uncommon** | 1 | no (power) | `bomb_damage_up` **+2** per copy, permanent |

Two of the four are **Common**, both non-exhaust, both 1-cost, and `chain_fuse` — the
ledger's named enabler — is the one whose scope is "every bomb on every living enemy".

Rarity finding to carry to the docket: `docs/klee-character-design.md:50` records a
ratified design intent of "stack caps on scaling powers (**bomb_damage_up ≤ 4**)". That
cap is **not implemented**. `powers.apply_power` honours a `max_stacks` argument
(`powers.py:183-184`), but it is only ever supplied from a card row's `max_stacks` field
(`effects.py:803, 850, 871`), and NO Klee row carries one — `explosives_workshop` applies
`bomb_damage_up: 2` with `max_stacks: None`. Every Klee scaling power is in the same
position (`zero_cost_attacks_up`, `spark_threshold_down`, `detonation_vuln`,
`amp_reaction_up`, `detonation_splash`, `spark_per_turn`). This is a shipped-intent /
shipped-code divergence, not a design question, and it is the direct cause of term 1
being uncapped in the power lane.

### 3.3 Term 2 carriers

**Reader (the card that sells the counter):**

| card id | name | rarity | cost | formula |
|---|---|---|---|---|
| `grand_finale` | "The Big One" | **rare** | 2 | damage 10 + `2_per_detonation_this_combat` |

`grand_finale` is the ONLY consumer of `N_per_detonation_this_combat` anywhere in the
298 rows — the uncapped read is a single Rare card. A second, *scoped* reader exists and
is not part of the exploit: `chance_bomb_per_detonation` on `chained_reactions` (rare)
reads `detonations_total − detonations_at_card_start` (`effects.py:1718`), i.e. only the
detonations its own play caused.

**Producers (everything that pumps the counter).** The structural point for the docket:
bombs detonate AUTOMATICALLY at turn start (`combat.py:452-454`, "bombs from last turn go
off"), so `detonations_total` grows from bomb PLACEMENT alone — no detonator card is
required, and there is no rarity gate on the counter's growth at all.

*Direct detonators* — 3 cards:

| card id | rarity | cost | exhaust |
|---|---|---|---|
| `quick_fuse` | **common** | 0 | no |
| `remote_detonator` | **uncommon** | 1 | no |
| `chained_reactions` | **rare** | 0 | no |

*Indirect producers (bomb placers)* — 15 rows, since every bomb placed is a detonation
counted:

| rarity | cards |
|---|---|
| **basic** | `pop`, `jumpy_dumpty` |
| **common** | `ammo_scavenging`, `bomb_voyage`, `chain_fuse`, `double_pop`, `fish_flavored_bait`, `mine_toss`, `sorry_jean` |
| **uncommon** | `bombs_away`, `cluster_charge`, `controlled_demolition`, `jumpy_dumpty_mk2`, `trip_wire` |
| **rare** | `all_my_treasures`, `sparkly_explosion`, `playtime_forever` (per-turn free bomb, `bomb_and_spark_per_turn`) |

### 3.4 Answering the verdict's own question

"Not a problem at higher rarity" holds cleanly for **term 2's read**: the multiplier is a
single Rare (`grand_finale`), and `chained_reactions` — the only other detonation-count
reader — is Rare and self-scoped. It does NOT hold for **term 1's writers**: `chain_fuse`
and `careful_arrangement` are non-exhaust **Commons** that write an unbounded per-bomb
adder, and `chain_fuse`'s scope is board-wide. Nor does it hold for term 2's *growth*,
which is driven by basic- and common-rarity bomb placers plus an automatic turn-start
detonation that no card gates.

### 3.5 Action

**None.** Findings only.

---

## 4 · Summary of actions

| sweep | matches | action |
|---|---|---|
| T-1 (X2) | 3 printed matches (1 Common) + 3 upgrade-gated Commons borderline | **`sucrose_gust` common → uncommon** (rarity field only), per sitting 2026-08-06 family X2; plus the inherited domination-lint allowlist entry it forced |
| T-2 (X7) | leg (a): 6 Common violations (0 under the strict reading of "repeatable"); leg (b): 1 violation, `cant_catch_me` (uncommon) | none — findings only |
| T-3 (X8) | term 1: 4 carriers, 2 Common; term 2: 1 Rare reader, 18 producers down to basic | none — findings only; flags the unimplemented `bomb_damage_up ≤ 4` cap |

Suite at close: `GITS_REFERENCE_MODE=committed-only python -m pytest tier0/tests
tier05/tests -q` — green.
