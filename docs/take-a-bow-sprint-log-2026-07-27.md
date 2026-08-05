# "Take a Bow" — Curtain Call consolidation sprint log

**Date:** 2026-07-27
**Branch:** `take-a-bow-consolidation` (off `main` @ 7e74efe)
**Character:** MECHANICAL. Zero design decisions, per the sprint charter.
**Ratifies:** DECISIONS R86

---

## 0. Preconditions

| | check | result |
|---|---|---|
| P1 | Curtain Call on main; no furina `KNOWN_FAILING` | PASS — merged as PR #10; `KNOWN_FAILING` holds only klee/kokomi rows |
| P2 | nine renames present in `furina-cards.yaml` | PASS — 9/9 exact, 78 cards, no sheet edit needed |
| P3 | suite green on the base | PASS — 1278 passed, 1 skipped |
| P4 | `Microsoft.NET.Sdk`; Godot 4.5 present | PASS — dotnet 9.0.316, MegaDot 4.5.1 |

P1 initially FAILED and was re-checked after a pull: the merge had landed
remotely and this clone had not seen it.

---

## 1. Track A — C# parity for the twelve deferred cards

`FURINA_DEFERRED_TO_CONSOLIDATION` is empty and **deleted**.
**Manifest 78 total / 77 generated / 1 blocked** (the hand-written kit Burst).

The twelve, and the grammar each was waiting on:

| card | was refused for | now |
|---|---|---|
| `fortissimo_guard` | `salon_deploy_block` | `SalonDeployBlockPower`, in the Deploy loop |
| `pit_orchestra` | `salon_bow_block` **+ `salon_bow_encore`** | two powers, both in `Bow` |
| `courtroom_drama` | `cross_examination` | `CrossExaminationPower`, first reaction |
| `crowd_work` | `encore_spend_draw` | `EncoreSpendDrawPower`, deferred draw |
| `quick_change` | `first_attack_draw` | `FirstAttackDrawPower`, per play index |
| `poised_riposte` | `bonus_formula 1_per_3_encore` | through the unified `calc_rider` |
| `warmup_act` | `enemy_intends_attack` | `CurtainCallHooks.EnemyIntendsAttack` |
| `graceful_retreat` | `hp_lost_this_turn` | `CurtainCallHooks.HpLostThisTurn` |
| `swelling_overture` | `encore_at_least_8` | parametric bar, as Fanfare's |
| `crescendo` | `grow_damage` | `BaseValue +=` on the printed var |
| `torrential_turn` | `refresh_all_auras` | AuraPower's own refresh path |
| `matinee_performance` | `times: salon_members` | `WithHitCount`, gated `> 0` |

**Six powers, not five.** `pit_orchestra` carries two, and `blocked_reason`
only ever reported the first — the count in R85's own note was low.

### Two things that needed judgment

**The deferred draw.** `SpendEncore` is synchronous and holds no
`PlayerChoiceContext` — it is called from the cost settle and from Salon
upkeep. The Gallery Stirs records its window there and the draw flushes from
every async Furina hook that can follow a spend, which is the deferral
SpotlightSystem already uses for its own first-play draw.

**The reset site.** Per-turn windows reset in `BeforeSideTurnStart`, not
`AfterPlayerTurnStart`. Salon upkeep SPENDS Encore in that second broadcast,
and order between models inside one broadcast is not guaranteed — resetting
there would make the draw depend on it. `BeforeSideTurnStart` is a strictly
earlier broadcast, so the ordering is guaranteed rather than assumed. This
also matches the sim, which zeroes the counter at the top of the turn.

**`cross_examination` reads the dealer.** The reaction COUNTERS are
deliberately global (red-pen R1). A power is owned by a creature, so the
question can only be asked of whoever caused the reaction. Solo — the only
configuration the sim models — the dealer is the player.

### Two latent generator defects, found on real cards

Both are the class that only appears when a new card SHAPE arrives, which is
why they survived every previous pass.

1. **Compose Herself** draws at top level *and* inside a branch, and tier0's
   draw delta bumps ALL draw ops — so both numbers are upgradeable and both
   need a var. `Cards` was taken. Branch draws now get their own name. *The
   first cut of that fix upgraded `Cards` twice; caught by reading the emitted
   `OnUpgrade`, not by a test.*
2. **Matinee Performance** is the pool's first card with two top-level damage
   ops, and both declared `"Damage"` — a `DynamicVarSet` constructor throw
   inside `CardFactory.CreateForReward`, i.e. **a reward-screen softlock on
   whatever run rolls the card**. Same shape as the 2026-07-23 incident.
   `damage_var_effect` now binds the var to the one effect tier0 upgrades.

### Parity vectors

Extended with the card-body READS: `N_per_M_{fanfare,encore}` riders and
`{fanfare,encore}_at_least_N` thresholds, both derived through the sim's own
`_bonus_formula` and `_predicate` so the table cannot be hand-fudged into
agreement with a bug. What they actually pin is integer division at the step
boundaries (Python floors, C# truncates; they agree only while both banks are
non-negative) and `>=` vs `>`.

**Verified RED** by perturbing one C# row, then restored.

### Register isolation

Generated output is byte-identical with the `register` field stripped from
every card. Asserted as byte-identity rather than as "the word does not
appear": the failure that matters is the field silently participating in a
decision, and an output diff catches every form of that.

---

## 2. Track B — renderer fixtures + register lint

`tools/lint_register_isolation.py`, wired into `test_sheet_lints`: nothing
under `tier0/engine` or `tier05` may read the field. `state.py`'s declaration
is the only exemption; `tools/` is deliberately not scanned, because guiding
art selection is the entire point of having a register.

Cell 1 proved the isolation empirically — renames and registers landed
together, byte-identical — but a measurement only speaks for the code that
existed when it ran. **Verified RED** against a planted read in
`tier05/model.py`, then restored.

Both renderer fixtures (`torrential_turn`'s single-target aura rider, and the
L-C rider tips on it and `crescendo`) now read the **generated files** rather
than `gen.emit()`. They had been describing cards that did not ship.

---

## 3. Track C — art rehunt (STAGED FOR G1, nothing locked)

Every row still carries `pick=shortlist`; selection happens in the contact
sheet. Seven candidates added across the four REHUNT rows, chosen on register
voice. Sheets rebuilt: `identity`, `salon-fanfare`, `spotlight`.

**One verify-keep is OVERTURNED.** `standing_room_only` ("The House Rises",
archon) was dispositioned keep on "full-house iconography". Rank 1 is
`Item Theater Tickets.png` — a flat pink item GLYPH of a ticket, no house in
it at all — while rank 3 is the Opera Epiclese itself at nation scale.
Checked by eye on both, not inferred from titles. It goes to G1.

No source needed fetching: all seven candidates were already in the local raw
pool, so no row of `SOURCES.tsv` had to move.

**It moved anyway, and was restored.** `art_fetch.py --help` is not a
recognized flag — the script takes no arguments — so asking for help RAN a
full fetch and rewrote `SOURCES.tsv` with 188/169 lines of churn across Klee,
Raiden and Itto rows unrelated to this sprint. Restored with
`git checkout -- art/SOURCES.tsv`, which is exactly the restore step the
art-pass law prescribes after any fetch.

**Flagged:** `audience_participation` is the weakest of the four shortlists.
The free pool is thin on nation-scale crowds and both additions are
compromises, one of them a carnival — the same objection that got the
original `crowd_work` pick rejected. If G1 rejects all five, that row needs a
genuine fetch pass, not another re-rank of what is already local.

---

## 4. Track D — build validation

Release build clean (0 errors; 13 warnings, none from the twelve new cards).
Pck packs at 114 resources. `validate: OK`. **Deployed 0.2-217.**

Two gates bit, which is the point of having them:

- **R13** fails the boot on any iconless PowerModel. The six new powers had
  no case in `KleePowerIcons` — load-bearing, not cosmetic. Each is now named
  individually, including both halves of Stagehands: separate powers, and a
  shared sigil would read as intentional rather than as missing art.
- **S12** then caught the same thing from the other side: referenced textures
  not in the pck. This sprint carried no art budget, so the six are declared
  in the deferred-art allowlist with reasons — the remedy the validator
  itself names. Each degrades to the base-game placeholder, the honest render
  for "no art yet". The gate holds both directions, so a stale exemption
  fails too.

### G2 checklist — [USER], evidence slots empty

Loading in Godot, rendering and playing are not things this agent can do.

| # | check | evidence |
|---|---|---|
| 1 | mod loads in Godot 4.5, no boot SELFCHECK errors | _(pending)_ |
| 2 | all twelve cards render: name, type frame, rarity banner, cost, body | _(pending)_ |
| 3 | `fortissimo_guard` pays per DEPLOY (Full Ensemble = three cues) | _(pending)_ |
| 4 | `pit_orchestra` pays Block **and** Encore on a bow | _(pending)_ |
| 5 | `courtroom_drama` fires on the FIRST reaction only | _(pending)_ |
| 6 | `crowd_work` draws on the first Encore spend only | _(pending)_ |
| 7 | `quick_change` draws on the first Attack only | _(pending)_ |
| 8 | upgrade forms render on all twelve (Touch of Orobas precedent) | _(pending)_ |
| 9 | solo Furina A0 smoke run to first elite | _(pending)_ |

**Worth watching at #2:** `crescendo`'s growth is a `BaseValue +=` on the
card instance. The sim's growth is combat-scoped because the card object
circulates through combat piles only. Whether StS2's combat deck holds copies
or the master-deck instances was not determinable from outside the game, so
**does Crescendo's damage reset between combats?** is an open question that
one playthrough answers and no static check can.

---

## 5. Open at close

> **IDENTIFIER NOTE, 2026-08-06 (housekeeping sweep, Track X).** `G1`/`G2` here
> are the **Curtain Call** mint (R86): canonical qualified forms **`CC-G1`**
> and **`CC-G2`**, tracked jointly by S4 as `S4-G12`. Not S4's `S4-G1`/`S4-G2`.
> Resolver: `docs/registry/identifiers.md` §2.1. Live status:
> `docs/registry/user-queue.md` §2.

- **G1** — contact-sheet eyes-on: four REHUNT rows + the `standing_room_only`
  overturn. Nothing locked until then.
- **G2** — the checklist above.
- Six power icons are declared art debt in the deferred-art allowlist.
- `audience_participation` may need a real fetch pass.
- Crescendo's cross-combat growth, per #2 above.
