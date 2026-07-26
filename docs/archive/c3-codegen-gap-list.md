# C3 codegen — gap list

**Date:** 2026-07-20. **Status:** 21 of 75 sheet cards generated, 3 hand-written,
**51 blocked**. Produced for the overnight queue's "C3 codegen for the remaining
~44 cards — generation only, gap-list what needs hands".

## The finding, up front

**Codegen cannot meaningfully extend further right now, and adding generator
features would not change that.** Every remaining card is blocked on a *runtime
system that does not exist yet*, not on the generator's expressiveness. The
generator already handles damage / block / draw / place_bomb; what is left needs
Sparks, the Burst meter, auras, powers, or predicates to exist first.

So the honest deliverable tonight is this list and its ordering, not more
generated files. Writing card shells against systems that do not exist would
produce code that compiles and lies.

## Blocked cards by unlocking system

| system | cards | notes |
|---|---|---|
| Power cards | 13 | 8 are `type: power`; 3 are skills using `apply_power` |
| Conditionals | 9 | predicate vocabulary; 4 also need auras/bombs |
| One-off card ops | 9 | 9 distinct ops — worst ratio on the board |
| **Sparks** | **8** | **one system, eight cards** |
| Bomb API (detonate/modify/move) | 5 | extends a system that already ships |
| Burst meter | 2 | `burst_energy` op |
| X-cost | 2 | energy-scaling support |
| Formula damage | 2 | `gleeful_barrage`, `grand_finale` |
| Auras | 1 direct | but gates ~4 conditionals and the whole reaction identity |

## Recommended unlock order

**1. Sparks — 8 cards, one system.** Best ratio on the board by a wide margin,
it is already a listed C2 item ("player counter + at-3-next-attack-free"), and
`tier0/engine/effects.py` is a working reference implementation. Also unblocks
the Pounding Surprise starting relic, which is currently why Klee has no
starting relic at all (see DECISIONS finding 10 — a character with no starting
relic is not a supported state, and we are only clear of it because we borrow
Silent's pools).

Cards: `all_my_treasures`, `cant_catch_me`, `da_da_da`, `hot_hands`,
`skip_and_hop`, `spark_collection`, `sparkly_treasure`, `warm_glow`.

**2. Bomb API extensions — 5 cards, no new state.** `detonate`, `modify_bombs`,
`move_bombs` all operate on `BombPower`, which is built and playtest-verified.
The recursion guard and the deep-clone hook — the two things that were subtle —
are already solved. Lowest-risk real work available.

**3. Auras — 1 card directly, but this is the real blocker.** Nothing applies
auras, so the reaction system is written and completely inert, bombs cannot
apply Pyro on detonation (`TODO(C2)` in `BombPower.Detonate`), and ~4 of the 9
conditionals depend on aura predicates. Its value is not its card count; it is
that the S1 success criterion (a Pyro hit onto a Hydro aura reading ×1.5 and
clearing the aura) cannot be demonstrated without it.

**4. Power cards — 13 cards, but 13 bespoke bodies.** Codegen can emit the card
shells mechanically; every `PowerModel` behind them is hand work of roughly
`BombPower`'s size. Worth splitting: generate the shells, hand-write the powers
in rarity order so the pool's rare tier stops being one card deep.

**5. Conditionals — 9 cards, needs a predicate vocabulary** (`target_has_aura`,
`target_has_bomb`, `spark_count >= n`, …). Partly gated on (3). Design the
vocabulary once against the sheet rather than growing it per card.

**6. Long tail — X-cost (2), formula damage (2), Burst meter (2), one-off ops
(9).** The one-offs are nine distinct mechanics for nine cards; they should be
done last and possibly trimmed. Several are "anything↔companions" bridge cards
whose value depends on the companion pool being interesting, which is a Tier 0.5
question that now has data.

## Standing obligation (M7 ruling R5): kit-Burst grant behavior

The build owes v1.9 Burst semantics alongside the Burst-meter system
above: Bursts are **kit, not deck contents** — never in the draftable
pool or any pile; granted to hand when the meter first fills; Retain
(v1.4); cast empties the meter and returns the card to the kit; a
refill re-grants it. The sim's reference implementation is
`grant_charged_kit` in `tier0/engine/combat.py` (including the
random-discard/exhaust exemption the review workflow caught). Logged
per ruling R5; no action until the C3 sweep.

## Pool-shape consequence

The current 21-card generated pool is **14 common / 5 uncommon / 1 rare** plus 3
basics. That single rare is a live problem for two reasons:

- Reward screens roll Rare at 5% and the new R3b guard exists precisely because
  thin tiers are fragile.
- It muddies any C2-telemetry-vs-Tier-0 comparison, since Tier 0 draws from the
  full 75-card sheet. **The sim and the build are not drafting from the same
  pool**, and every comparison between them inherits that.

Power cards (step 4) are where the rare tier lives — 5 of the 8 blocked `type:
power` cards are rare. That is an argument for pulling step 4 earlier than its
ratio suggests.

## Not done tonight, deliberately

Sparks was tempting — it is the best ratio and it is spec'd C2 work. I did not
build it unattended. It is a new player-side counter that has to hook attack
cost modification, the morning session is a playtest, and shipping an untested
mechanic into the build that playtest depends on risks the playtest itself.
Same call as the keyword-registration item (DECISIONS finding 20). It is the
first thing I would do with you awake.
