"""Atomic effect resolvers — the card DSL.

v1 ops per tier0-simulator-spec.md §4.2, extended per
klee-character-design.md §6 for the real card sheet: detonate, move_bombs,
modify_bombs, burst_energy, swirl, refresh_all_auras, buff_next_attack,
cost_mod, conditional, repeat_this, formula amounts, companion ops.
"""

from __future__ import annotations

import copy
from functools import lru_cache

from typing import Optional, Sequence

from tier0 import constants as C
from tier0.engine import (companion_coven, companion_hexerei, coop,
                          furina_stage, klee_overhaul, kokomi_plan,
                          lions_fang, powers, reactions, resources, statuses,
                          varka_oath)
from tier0.engine.state import (SLY_AUTOPLAY_THIS_TURN, Bomb, Card,
                                CombatState, Enemy,
                                grant_sly_autoplay,
                                remove_instance, sly_autoplays,
                                sly_granted_this_turn, sly_riders,
                                sync_fanfare_cap_to_max_hp)


def _amount(state: CombatState, val) -> int:
    """Resolve a literal or formula amount (X-cost cards)."""
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        # Big Badda Boom's echo base (2026-09-26): a total with each
        # explosion's Vulnerable taken back out, which is fractional by
        # construction; the pipeline truncates once, at the end, as it
        # does for every other term.
        return val
    if val == "X":
        return state.current_x
    if isinstance(val, str) and val.startswith("X_plus_"):
        return state.current_x + int(val[len("X_plus_"):])
    if isinstance(val, str) and val.startswith("-"):
        # Malaise applies StrengthPower with -X and WeakPower with +X, i.e.
        # one number spent twice with opposite signs. A leading minus negates
        # whatever formula follows it, so the pair stays visibly the SAME
        # value on the row and the upgrade cannot move one without the other.
        return -_amount(state, val[1:])
    if val == "exhausted_this_card":
        # Stoke: "exhaust your hand, generate that many cards". The count is
        # captured by the exhaust op as it runs, matching the dll, which
        # reads exhaustCount off the selection list before exhausting.
        return state.exhausted_this_card
    if isinstance(val, str):
        # Any _runtime_count token is a legal amount. The two grammars were
        # separate only by accident of which op needed a live number first:
        # `times` on damage/block has always read runtime counts, while
        # `amount` could not, so Calculated Gamble ("discard your hand, draw
        # that many") had no spelling despite every piece existing. An
        # unknown token still raises out of _runtime_count, so this widens
        # the vocabulary without softening the failure.
        return _runtime_count(state, val)
    raise ValueError(f"unknown amount formula {val!r}")


def _bonus_formula(state: CombatState, formula: str,
                   card: Optional[Card] = None, *,
                   valuation: bool = False) -> int:
    """Scaling riders on a damage or block amount.

    `valuation=True` says THIS CALL IS AN ESTIMATE, not a resolution (EB-242).
    The pilot prices a rider through this exact helper on purpose -- that is
    what keeps its price from drifting from what resolving the card pays --
    but a price is not a play, so an estimate must not tick the reads-per-turn
    instrument. `resources.note_charge_read` declared the two pilot sites out
    of scope from the day it landed, and §2 of the charge registration says
    deliberation is deliberately NOT counted; the flag is that declaration
    made executable. Everything else -- both engine resolve sites, and the
    suite's direct probes of the primitive -- is a resolution and tallies
    exactly what it always did, because the DEFAULT is the resolve path and
    the exemption has to be asked for.

    Two grammars, and the difference is deliberate:

      N_per_<thing>      a full step per unit, for SMALL counts --
                         'detonation_this_combat'
      N_per_M_<resource> a ratio, for LARGE pools -- 'fanfare' -- where 1:1
                         would pay far too much
    """
    n, _, rest = formula.partition("_per_")
    if not n.isdigit():
        raise ValueError(f"unknown bonus_formula {formula!r}")
    if rest == "detonation_this_combat":
        return int(n) * state.detonations_total
    if rest == "companion_played_this_turn":
        # Blocking Notes (rework Track C.3, 2026-07-28): Companion TEMPO. No
        # _M_ divisor for the same reason salon_member has none -- this is a
        # small count (a big turn is three or four Companions), not a pool,
        # and every play should be a full step.
        #
        # Counts the card CURRENTLY resolving too if it is a Companion,
        # because combat._finish_play increments before resolve_card. That
        # only matters for a Companion that also grants Block, of which there
        # are none today; recorded so the off-by-one is a decision rather
        # than a discovery.
        return int(n) * state.companion_plays_this_turn
    m, _, what = rest.partition("_")
    if what == "fanfare" and m.isdigit():
        # EB-253: the fanfare twin of the charge leg below. The pilot prices
        # a Fanfare rider through this same helper, and a price is not a
        # play -- `note_fanfare_read` is the LIVE-meter instrument, so
        # deliberation counted there reports the pilot's turn as the
        # player's. Same declaration, same default: every engine resolve
        # site and every direct probe still tallies exactly what it did.
        if not valuation:
            resources.note_fanfare_read(state, "bonus_formula",
                                        card=card.id if card else None)
        # `readable`, not the raw field: the meter can sit BELOW ZERO since
        # the Hyperbeam (Track C.2), and a rider reading -12 would pay
        # NEGATIVE damage -- an attack that heals the enemy. Effects shut off
        # rather than invert; see resources.drop_fanfare_to_floor.
        return int(n) * (resources.readable(state.player) // int(m))
    raise ValueError(f"unknown bonus_formula {formula!r}")


# --- EB-118: card-resolution-scoped Exhaust identity context ---------------
#
# The card you chose to Exhaust tells the exhausting card what to do. What is
# recorded is PRINTED IDENTITY ONLY -- six descriptors a CardModel carries too,
# which is what lets the C# twin (Powers/ExhaustSelection.cs) record the same
# row off the same facts. Nothing here reads sim-only state.
#
# THE SCOPING, which is the whole point and the thing a `last_exhausted`
# global would get wrong:
#   * resolve_card opens an EMPTY selection per card play, so the next card
#     played reads nothing;
#   * combat._FREE_PLAY_CONTEXT saves and restores it, so a free play landing
#     mid-resolution cannot hand its victims to the outer card;
#   * a SECOND exhaust_from on one card opens its own -- the list is REBOUND,
#     never cleared in place, because the free-play save holds the object.
#
# Kokomi's rotation law (C11) filters her unfiltered pool before any of this
# runs, so her context never carries junk. The mechanism is character-neutral:
# an explicit `filter: status` card (Dodge Roll's shape) records its victims
# here too. There is deliberately NO "Status exhausted" reward grammar -- the
# context reports rarity, and what a card does with that is a sheet decision.
EXHAUST_SELECTION_PREFIX = "exhaust_selection_"

# The descriptor a victim leaves behind, in emission order.
EXHAUST_SELECTION_FIELDS = ("id", "cost", "type", "rarity",
                            "companion", "upgraded")


def exhaust_descriptor(card: Card) -> dict:
    """The printed identity of one exhausted card.

    `cost` is the PRINTED cost and is kept raw: an X-cost card in hand has no
    spent value, so it stays "X" here and contributes 0 to the derived total
    rather than being silently coerced to a number a formula would pay for.
    `upgraded` reads the id suffix, which survives an enchantment mark
    (`x@sharp-2+`) because upgrades.apply_upgrade re-attaches the mark INSIDE
    the suffix.
    """
    from tier0.content import upgrades          # late import avoids cycle
    return {"id": card.id, "cost": card.cost, "type": card.type,
            "rarity": card.rarity, "companion": card.is_companion,
            "upgraded": card.id.endswith(upgrades.SUFFIX)}


def exhaust_selection_counts(selection: list[dict]) -> dict:
    """Derived reads over a selection. ONE definition, three consumers: the
    `exhaust_selection_*` runtime counts, the `exhaust_selection_*` predicates
    and the emitted parity row -- so a formula can never report a different
    number from the row a parity test compares against C#."""
    return {
        "size": len(selection),
        # Non-int costs (X) contribute nothing; see exhaust_descriptor.
        "cost": sum(d["cost"] for d in selection
                    if isinstance(d["cost"], int)),
        "attacks": sum(1 for d in selection if d["type"] == "attack"),
        "skills": sum(1 for d in selection if d["type"] == "skill"),
        "powers": sum(1 for d in selection if d["type"] == "power"),
        "companions": sum(1 for d in selection if d["companion"]),
        # PERSONAL is the complement of companion, spelled out rather than
        # inferred: a card that rewards rotating your OWN cards out asks a
        # different question from `size - companions`, and the sheet should
        # be able to say which one it means.
        "personal": sum(1 for d in selection if not d["companion"]),
        "upgraded": sum(1 for d in selection if d["upgraded"]),
    }


# The parity row, key for key and in order. The C# twin renders the same keys
# (ExhaustSelection.ParityRow); test_exhaust_context_parity.py reads them out
# of the C# source and compares, so neither side can add or rename a column
# alone. `victims` is the id list -- the same ids CardCmd.Exhaust takes.
EXHAUST_SELECTION_ROW_KEYS = ("card", "victims") + tuple(
    exhaust_selection_counts([]))


def exhaust_selection_row(state: CombatState, card: Card) -> dict:
    row = {"card": card.id,
           "victims": [d["id"] for d in state.exhaust_selection]}
    row.update(exhaust_selection_counts(state.exhaust_selection))
    return row


def _runtime_count(state: CombatState, token: str,
                   current_card: Optional[Card] = None) -> int:
    """A live integer the base-game CalculatedX/CalculatedDamage vars read at
    resolution time, not a number the pilot could pre-compute -- which is
    exactly why the real game defers them to play time:

      exhaust_pile   AshenStrike (ExtraDamage x cards in the exhaust pile)
      player_block   BodySlam (ExtraDamage x the owner's CURRENT Block)
      attacks_in_hand ExpectAFight (Energy x Attacks in hand at play time)
      strike_cards   PerfectedStrike (all cards carrying the structurally
                     extracted Strike tag, including the playing card)
      player_damage_events TearAsunder (unblocked player-damage entries this
                     combat, counted per event rather than per HP)

    Silent coverage pass (2026-07-27) -- six more, each named after the
    CalculatedVar multiplier it serves:

      attacks_played_this_turn  Finisher (hit count = Attacks played this
                     turn; the counter already existed for Juggling)
      skills_in_hand Flechettes (hit count = Skills in hand at play time)
      other_cards_in_hand PreciseCut (damage FALLS with hand size; the card
                     subtracts itself, hence "other")
      discards_this_turn MementoMori (CardDiscardedEntry this turn -- the
                     end-of-turn flush does not go through CardCmd.Discard
                     and so does not count, verified in CombatManager)
      cards_drawn_this_combat Murder (CardDrawnEntry for the owner, NOT
                     reset per turn)
      enemy_poison_total Mirage (summed Poison across LIVING enemies)
      X              Skewer (hit count = the energy an X card spent, the
                     same value `amount: X` reads)
    """
    p = state.player
    if token == "exhaust_pile":
        return len(p.exhaust_pile)
    if token == "player_block":
        return p.block
    if token == "attacks_in_hand":
        return sum(1 for c in p.hand if c.type == "attack")
    if token == "strike_cards":
        piles = (p.draw_pile, p.hand, p.discard_pile, p.exhaust_pile)
        cards = [c for pile in piles for c in pile]
        if (current_card is not None
                and all(c is not current_card for c in cards)):
            cards.append(current_card)  # play_card has removed it from hand
        return sum("strike" in c.tags for c in cards)
    if token == "player_damage_events":
        return state.player_damage_events
    if token == "attacks_played_this_turn":
        return state.attacks_played_this_turn
    if token == "skills_in_hand":
        return sum(1 for c in p.hand if c.type == "skill")
    if token == "other_cards_in_hand":
        # The playing card has already left hand (play_card removes it before
        # resolution), so "other" is simply the hand as it stands -- which is
        # what the source computes the long way round by subtracting itself.
        return len(p.hand)
    if token == "discards_this_turn":
        return state.discards_this_turn
    if token == "exhausts_this_turn":
        # CURRENT-KIT USE ONLY (R213 B): no shipped row reads this token. It
        # is the counting basis R215 C routed to the Kokomi slice -- "how many
        # cards had been exhausted that whole turn" -- against `exhaust_pile`
        # (the whole fight) and `exhaust_selection_cost` (the one chosen card).
        # Counted at the pile append, so a card that Exhausts and then reads
        # sees its own victim; see CombatState.exhausts_this_turn.
        return state.exhausts_this_turn
    if token == "cards_drawn_this_combat":
        return state.cards_drawn_this_combat
    if token == "enemy_poison_total":
        return sum(e.powers.get("poison", 0) for e in state.living_enemies)
    if token == "X":
        # Skewer: hit count = the energy actually spent, the same number
        # `amount: X` resolves. Spelled with the same token deliberately.
        return state.current_x
    if token == "sparks_spent":
        # (R276, Fireworks Finale): one hit per Spark the all-in
        # price spent -- the bank at play, which is what such a price spends
        # (`grow_largest_bomb`'s reading). The mod's twin is the `sparksSpent`
        # local its X-price line declares.
        return int(state.sparks_at_play)
    if token == "exhausted_this_card":
        return state.exhausted_this_card
    # Coverage pass 4 (2026-07-27). Each is a count the base game takes off
    # a pile or a command result at resolution time:
    #   hand_size            CalculatedGamble / StormOfSteel, which discard
    #                        the hand and pay out per card discarded. Read
    #                        BEFORE the discard op runs, which is the order
    #                        the source reads it in too (`cards.Count()` is
    #                        evaluated before DiscardAndDraw).
    #   discards_this_card   the same number read AFTER the discard, for the
    #                        second half of those cards. Not `hand_size`
    #                        again: by then the hand is empty.
    #   block_gained_this_card  DodgeAndRoll applies BlockNextTurn equal to
    #                        the block CreatureCmd.GainBlock actually
    #                        returned -- post-Dexterity, post-Frail, not the
    #                        printed number. block_gains_this_card is a
    #                        COUNT of gains and cannot answer this.
    # CURRENT-KIT USE ONLY (R213 B): no shipped row reads either token. Both
    # belong to the INAZUMA companion overhaul and both are counts this engine
    # already keeps -- which is the whole reason the two rows that print them
    # are expressible at all.
    if token == "companions_played_this_combat":
        # Raiden's Musou no Hitotachi: "5 more for each Companion CARD you
        # played this combat". `companions_played` is the Best Friends Forever
        # pool, unique by base id and written once per card play -- so the
        # count is CARDS and not PLAYS, which is what "each Companion card"
        # names. The C# twin reads `CompanionPlays.PlayedThisCombat`, which is
        # deduped by `(Owner, ModelId)` for the same ruling (2026-08-06).
        return len(state.companions_played)
    if token == "companions_played_this_turn":
        # CURRENT-KIT USE ONLY (R250, round-4d sec.6 pick 1): Chain of
        # Command's now-line, "deal 3 damage for each Companion card you
        # played this turn" -- the live half beside the Plan clause's
        # `damage_per_companion_last_turn`. `state.companion_plays_this_turn`
        # is the same unconditional per-play counter `_finish_play` already
        # keeps for Blocking Notes and for the Plan line's own morning
        # handover (`kokomi_plan.roll_turn`), so this reads the one count
        # rather than minting a second.
        return state.companion_plays_this_turn
    if token == "plans_carried_out_this_turn":
        # CURRENT-KIT USE ONLY (the Casket pass, 2026-09-28) -- Feint and
        # Sango Isshin, "for each Plan carried out this turn". Every
        # carry-out this turn, a doubled one twice, written at the plan bus.
        # The C# twin is `KokomiOverhaulLedger.PlansCarriedOutThisTurn`.
        return state.kk_plans_carried_out_this_turn
    if token == "plans_written_this_turn":
        # CURRENT-KIT USE ONLY (pool completion, 2026-10-01) -- Shoal of
        # Spears, "for each Plan you wrote this turn". Every write onto the
        # Bake-Kurage this turn, counted at `kokomi_plan.schedule`. The C#
        # twin is `KokomiOverhaulLedger.PlansWrittenThisTurn`.
        return state.kk_plans_written_this_turn
    if token == "casket_count":
        # CURRENT-KIT USE ONLY (the Casket pass) -- Driftglass and Depths'
        # Judgment, the Tamakushi Casket's count. The C# twin is
        # `KokomiOverhaulLedger.CasketCount`.
        return state.kk_casket
    if token == "debuffs_on_target":
        # CURRENT-KIT USE ONLY (R276) -- Well Laid, "plus 3 for each debuff on
        # the enemy". The AIMED enemy, `_power_amount_formula`'s read: the
        # card's single target is the default aim when it resolves. DISTINCT
        # debuffs, not stacks -- `kokomi_plan.debuff_count`, the twin of
        # `KokomiOverhaulKit.DebuffCount`.
        return kokomi_plan.debuff_count(_default_target(state))
    if token == "plan_energy_waiting":
        # CURRENT-KIT USE ONLY (the Kokomi expansion, batch one) -- Weight of
        # the Plan, "plus 3 for each Energy paid for the Plans waiting". The
        # C# twin is `KokomiPlan.EnergyWaiting`.
        return kokomi_plan.plan_energy_waiting(state)
    if token == "plans_held":
        # CURRENT-KIT USE ONLY (Kokomi round 9 pick 1, the tempo shelf) --
        # Tide Chart, "draw 1 card for each Plan the Bake-Kurage holds".
        #
        # THE QUEUE ITSELF, and it has to be: "holds" means WRITTEN and not yet
        # carried out, which is `kk_plan_queue` and nothing else.
        # `kk_plans_this_morning` is the depth of the morning just drained --
        # the number Tide Wall reads -- so a card played after the drain would
        # find yesterday's plans there and pay for cards the jellyfish no
        # longer holds. The C# twin is `KokomiPlan.PlansHeld`, the length of
        # the same queue read at the same moment.
        return len(state.kk_plan_queue)
    if token == "swirls_this_turn":
        # Heizou's Heartstopper Strike: "4 more for each Swirl this turn".
        return state.mi_swirls_this_turn
    if token == "fanfare_drained":
        # CURRENT-KIT USE ONLY (R213 B): the FURINA REFRAME's two drain rows
        # (packet §4.6, `F11` (1) and `F12` (1)). What `drain_fanfare` took
        # FROM THIS PLAY, read by the effects that follow it on the card.
        #
        # A PER-CARD NUMBER AND NOT A METER READ, which is the whole reason it
        # is a count at all: by the time the damage or the Block resolves the
        # meter is 0, so an effect that read `p.fanfare` here would pay out
        # nothing every time. Written by `_op_drain_fanfare`, cleared per card
        # play beside `discards_this_card` and its neighbours.
        return state.fanfare_drained_this_card
    # FURINA (the Salon's Tab). `stage_spent` is what THIS play spent
    # ("Spend all your Fanfare"), read back by the effect after it, because
    # by the time the damage resolves the Fanfare it measures is gone;
    # written by `_op_stage_spend` and `_op_stage_spend_all`, cleared per
    # card play beside `fanfare_drained_this_card`. 0 for anyone else.
    if token == "stage_spent":
        return state.stage_spent_this_card
    # THE POOL TO 75 (2026-10-09): Undercurrent's, Balance the Books',
    # Rising Tide's and Grand Absolution's counts (`furina_stage`'s readers;
    # the C# `FurinaStage` twins). 0 for anyone else.
    if token == "stage_drains":
        return furina_stage.drains_this_combat(p)
    if token == "stage_half_drained":
        return furina_stage.half_drained(p)
    if token == "stage_repays_turn":
        return furina_stage.repays_this_turn(p)
    if token == "stage_repaid":
        return furina_stage.repaid_this_play(p)
    if token == "hand_size":
        return len(p.hand)
    if token == "discards_this_card":
        return state.discards_this_card
    if token == "block_gained_this_card":
        return state.block_gained_this_card
    # EB-118: the Exhaust identity context. `exhausted_this_card` above is the
    # COUNT; these are the derived reads off the DESCRIPTORS of the selection
    # the current card's exhaust_from just resolved. Registered as one prefix
    # family rather than eight tokens so the vocabulary and the emitted parity
    # row cannot disagree about what exists -- both enumerate the same dict.
    if token == "enemies_with_bomb":
        # AoE trim, 2026-10-03 (Bombs Away!): "plus 2 for each enemy with a
        # Bomb". LIVING enemies holding one of Klee's charges (Mines are
        # Bombs, rule 6), read at resolution -- after the card's own Bomb.
        return sum(1 for e in state.living_enemies
                   if klee_overhaul.holds_charge(e))
    if token.startswith(EXHAUST_SELECTION_PREFIX):
        counts = exhaust_selection_counts(state.exhaust_selection)
        key = token[len(EXHAUST_SELECTION_PREFIX):]
        if key in counts:
            return counts[key]
    # VARKA, THE OATH REWORK (`varka_oath.count`): his current element's
    # Oath and how many elements he has Oath in. 0 for anyone who is not
    # Varka, so no shipped read can move.
    if (token == "current_oath" or token == "oath_elements"
            or token == "enemies_with_aura" or token == "hydro_oath"
            or token == "knights_played_this_combat"
            or token == "half_total_oath"):
        return varka_oath.count(state, token)
    raise ValueError(f"unknown runtime count {token!r}")


def _calc_amount(state: CombatState, formula: dict,
                 current_card: Optional[Card] = None) -> int:
    """CalculatedDamageVar / CalculatedVar grammar: base + per * count, where
    count is a _runtime_count token. base defaults 0 (BodySlam), per defaults
    1 (ExpectAFight's 1-per-Attack)."""
    return (formula.get("base", 0)
            + formula.get("per", 1)
            * _runtime_count(state, formula["count"], current_card))


def _power_amount_formula(state: CombatState, formula: dict) -> int:
    """apply_power Amount read off a live power stack on the default-aim
    enemy (Dominate's StrengthPerVulnerable, MoltenFist's Vulnerable
    doubling). Evaluated AFTER any preceding op in the same card, so Dominate
    reads the +1 Vulnerable it just applied."""
    if "target_power" in formula:
        tgt = _default_target(state)
        return tgt.powers.get(formula["target_power"], 0) if tgt else 0
    raise ValueError(f"unknown apply_power amount_formula {formula!r}")


# EB-136 / R210 (C18). The ops whose `target: enemy` spelling means "the one
# creature the player picked", and which therefore read `cardPlay.Target` in
# C#. Deliberately the SAME list the emitter carries as `AIMING_OPS`
# (`tools/gen_klee_cards.py:1070`) plus `apply_power` on an enemy-landing
# power, because the two answering differently is the divergence this repair
# closes: the sheet row that makes a card declare `TargetType.AnyEnemy` in the
# mod is the sheet row that binds the aim in the sim.
AIMING_OPS = frozenset(("damage", "place_bomb", "detonate", "move_bombs",
                        "apply_aura", "swirl", "apply_power",
                        # (C.KLEE_OVERHAUL). The arm's four aimed
                        # verbs, restoring the "same list the emitter carries"
                        # promise above -- `gen_klee_cards.AIMING_OPS` has held
                        # them since the ops landed, on EB-142's argument (an
                        # aiming op dereferences `cardPlay.Target` wherever it
                        # sits). No shipped row prints one, so this widening is
                        # unreachable outside the arm.
                        "set_off", "plant_bomb", "grow_bombs", "merge_bombs",
                        # R276's Hair Trigger, on the same terms.
                        "mine_bombs",
                        # The Klee scaling pass's Witch's Homework (klee-next).
                        "plant_homework_bomb"))

# Ops whose aimed target may be a CORPSE. C#'s dead-target rule is op-dependent
# and this frozenset is that asymmetry, written down once:
#
#   * DAMAGE FIZZLES. `AttackCommand.Execute` refilters its one-element
#     `GetPossibleTargets()` by `IsAlive` on EVERY hit and breaks on empty
#     (`CombatState.IsLiveCombat()` returns literally `true`), with
#     `CreatureCmd.Damage`'s `if (originalTarget2.IsDead) continue;` behind it.
#     No retarget, no corpse hit.
#   * EVERYTHING ELSE HERE LANDS ON THE CORPSE, because every one of them
#     reaches the target through `PowerCmd.Apply`, whose only guard is
#     `CanReceivePowers` -- and `Creature`'s own first-party doc says why the
#     guard is not `IsHittable`: "a creature is not hittable if it's dead, but
#     dead creatures can still have powers applied to them". `apply_power` is
#     the decompile-settled case (audit sec.3.2); `place_bomb`
#     (`BombPower.Place` -> `PowerCmd.Apply`), `move_bombs`
#     (`BombPower.MoveAllTo` -> `PowerCmd.Apply` on `dest`) and `apply_aura` /
#     `swirl` (`ElementalHit.ApplyOnly` -> `AuraCmd.Apply` ->
#     `PowerCmd.Apply<XAuraPower>`) are our own mod code reaching the same
#     door. `detonate` is the odd one and lands here on its own evidence:
#     `BombPower.DetonateOn` reads `target.Powers.OfType<BombPower>()` with NO
#     aliveness test at all, and the mod already RECOGNISES the corpse case --
#     `RecordDetonation(..., onCorpse: target is { IsDead: true })`, the EB-18
#     counter. The charges are spent; the damage behind them is what dies at
#     `CreatureCmd.Damage`.
#
# `strip_block` is absent deliberately: it is not one of the emitter's aiming
# ops, no C# behaviour is recorded for it on a corpse, and a dead creature's
# Block is 0 -- so the two readings are observationally identical and the
# non-inventive one is the default.
CORPSE_TARGETABLE_OPS = frozenset(("apply_power", "place_bomb", "detonate",
                                   "move_bombs", "apply_aura", "swirl"))


def _card_aims_at_enemy(card: Card) -> bool:
    """Does this card ever aim, i.e. would the mod declare
    `TargetType.AnyEnemy` for it?

    Only consulted on the `force_random_targeting` path, where the answer
    decides whether the bind CONSUMES AN RNG DRAW: `CardCmd.AutoPlay` rolls
    `Rng.CombatTargets` only `if (card2.TargetType == TargetType.AnyEnemy)`, so
    a free-played card that aims at nothing must not eat a roll. The
    deterministic bind needs no such gate (a lowest-HP read is free), which is
    why this walk is off the hot path entirely.

    Walks the WHOLE effect tree -- conditional arms, mode bodies and the
    enchantment riders -- where the emitter's `_aims_at_chosen_enemy` reads
    top-level rows and mode bodies only. Over-answering costs one roll; the
    emitter under-answering is its own bug (its `ThrowIfNull` catches it).
    """
    def walk(effects) -> bool:
        for fx in effects or ():
            if (fx.get("target") == "enemy" and fx.get("op") in AIMING_OPS):
                return True
            if walk(fx.get("then")) or walk(fx.get("else")):
                return True
            for mode in fx.get("modes") or ():
                if walk(mode.get("effects")):
                    return True
        return False
    return (walk(card.effects) or walk(card.enchant_effects)
            or walk(card.enchant_first_play_effects))


def _card_swirls_at_aim(card: Card) -> bool:
    """Does this card carry a Swirl that lands on the play's BOUND AIM?

    The gate on EB-139's aura-aware bind (R211, C20), and the reason that bind
    is not a board-wide aim rule: a Swirl's whole payload IS the aura it lands
    on, so an aimed Swirl is the one card shape where the mouse pick a human
    makes is knowable from the board rather than a matter of taste. Every other
    card keeps the documented lowest-HP aim R210 declined to re-open.

    `target: all_enemies` Swirls do not gate it -- they hit the whole board and
    have no aim to move. Walks the same whole tree `_card_aims_at_enemy` does,
    for the same reason: a Swirl inside a conditional arm or a mode body is
    still a Swirl this card can land.
    """
    def walk(effects) -> bool:
        for fx in effects or ():
            if (fx.get("op") == "swirl"
                    and fx.get("target", "enemy") in ("enemy",
                                                      "lowest_hp_enemy")):
                return True
            if walk(fx.get("then")) or walk(fx.get("else")):
                return True
            for mode in fx.get("modes") or ():
                if walk(mode.get("effects")):
                    return True
        return False
    return (walk(card.effects) or walk(card.enchant_effects)
            or walk(card.enchant_first_play_effects))


def bind_card_aim(state: CombatState, card: Card) -> Optional[Enemy]:
    """C#'s `CardPlay.Target`, rolled ONCE at card-play construction.

    `CardPlay.Target` is `public required Creature? Target { get; init; }` --
    immutable for the life of the play -- and on an autoplay `CardCmd.AutoPlay`
    fills it from `HittableEnemies` BEFORE `OnPlayWrapper` is entered. So the
    binding moment is here, ahead of every op: a bound aim is picked pre-AoE,
    not lazily at the first aimed row.

    WHICH creature is, for every card but one shape, still not re-opened: a
    manual play's target is the human's mouse pick, which no engine rule
    mirrors, so tier0 keeps its documented lowest-HP identity choice. R210 took
    the pick ONCE instead of per op; R211 (EB-139, C20) added the ONE ruled
    exception below. Destination SCORING stays severed as a later design
    question -- nothing here scores a destination, it reads one predicate off
    the board.
    """
    living = state.living_enemies
    if not living:
        return None
    # PARITY, not fidelity: the base game rolls a RANDOM enemy for
    # TargetType.AnyEnemy on an autoplay, and the variance profile is the whole
    # identity of Havoc/Cascade. Keeping tier0's lowest-HP aim for free plays
    # would hand those cards a pilot's judgement they do not have. Set only for
    # the duration of a free play -- and now rolled ONCE PER CARD, which is
    # where `CardCmd.AutoPlay` rolls it, rather than once per op.
    #
    # THIS BRANCH IS FIRST, AND THAT ORDER IS THE RULING: forced-random autoplay
    # stays random and receives NO corrective re-aim (R211). A free play has no
    # human at the mouse, so modelling one there would hand Havoc/Cascade a
    # judgement the mod never gives them -- the same argument that put the roll
    # here in the first place.
    # (C.KURAGE_MEMORY), and FIRST because it is an override of
    # the forced-random branch below rather than a competitor to it. PICK E1
    # says the jellyfish's replay "follows her lead" -- the enemy Kokomi's own
    # last attack aimed at -- which is the one auto-play in the engine that is
    # deliberately NOT random, because the whole defence of this design is
    # that the strip can SHOW the target before it fires (D4). `kurage_aim` is
    # non-None only for the duration of a memory auto-play, and only under
    # KURAGE_TARGET_RULE == "follow_her_last_attack"; E2 leaves it None and
    # falls through to the shipped roll.
    if state.kurage_aim is not None and _card_aims_at_enemy(card):
        return state.kurage_aim
    if state.force_random_targeting and _card_aims_at_enemy(card):
        return state.rng.choice(living)
    # EB-139 / R211: the aura-aware bind, for MANUALLY-MODELLED play only. If
    # ANY living enemy carries an aura when the play is constructed, the WHOLE
    # CARD binds to the lowest-HP AURA-BEARING enemy. This replaces the aim
    # RE-TAKE that used to live inside `_op_swirl` -- which is what C18 pinned
    # as unruled, because a re-take put a card's damage and its Swirl on two
    # different creatures. One bind, taken here, keeps
    # `sayu_yoohoo_windwheel`'s `damage 4` and its Swirl on one body, and it is
    # the body a human aims at: a Swirl on an auraless target does nothing at
    # all.
    if _card_swirls_at_aim(card):
        bearers = [e for e in living if e.aura]
        if bearers:
            return min(bearers, key=lambda e: e.hp)
    return min(living, key=lambda e: e.hp)


def _default_target(state: CombatState) -> Optional[Enemy]:
    """The enemy a card-reading predicate or formula is talking about.

    INSIDE a card play this is the bound aim and nothing else -- Dismantle's
    hit-count predicate and Dominate/MoltenFist's power-reading formula both
    mean `cardPlay.Target`, and under R210 that is a single creature for the
    whole play, DEAD OR ALIVE. The C17-and-earlier caveat this docstring used
    to carry (the aim is re-picked across ops, so a hit that kills it hands the
    rider to whoever is lowest-HP next) is exactly what EB-136 repaired.

    OUTSIDE a card play -- the pilot's estimates, which run between plays --
    there is no `CardPlay` yet, so the honest answer is the live lowest-HP
    read: the aim the next play WOULD bind.
    """
    if state.card_aim_bound:
        return state.card_aim
    living = state.living_enemies
    return min(living, key=lambda e: e.hp) if living else None


def _pick_targets(state: CombatState, spec: str,
                  allow_dead: bool = False) -> list[Enemy]:
    """Resolve one op's `target:` spec to the creatures it hits.

    `enemy` / `lowest_hp_enemy` return the play's BOUND aim (R210) -- the same
    creature for every aimed op of the card. `allow_dead` is the per-op half of
    C#'s non-uniform dead-target rule (see `CORPSE_TARGETABLE_OPS`): False fizzles
    on a corpse the way `AttackCommand` does, True lands on it the way
    `PowerCmd.Apply` does. It reaches the bound aim ONLY -- `all_enemies` and
    the random specs draw from `HittableEnemies`, which excludes the dead in
    both engines.
    """
    if spec in ("enemy", "lowest_hp_enemy"):
        if state.card_aim_bound:
            aim = state.card_aim
            if aim is None:                    # bound on an empty board
                return []
            return [aim] if (aim.alive or allow_dead) else []
        # No card play in flight (a direct op call, or a probe driving the
        # resolver by hand). The aim the next play would bind.
        living = state.living_enemies
        if not living:
            return []
        if state.force_random_targeting:
            return [state.rng.choice(living)]
        return [min(living, key=lambda e: e.hp)]
    living = state.living_enemies
    if not living:
        return []
    if spec == "all_enemies":
        return list(living)
    if spec in ("random_enemy", "random_enemies"):
        return [state.rng.choice(living)]
    raise ValueError(f"unknown target spec {spec!r}")


def owner_identity(owner: Optional[str]) -> tuple[str, str]:
    """The OWNING kit's (element, cadence), or ("none", "") for a card no kit
    owns -- a base basic, a token, a colorless, a curse, a reference pool's.

    THE ELEMENT IS ON THE CARD, NOT ON WHOEVER PLAYS IT ([USER], 2026-10-05:
    "I think that that Kokomi effect is a legacy design. We changed things (or
    tried to change them) so that that effect just lives in the card pool as a
    symbol on relevant elemental cards and the card states 'deals [element]
    damage' or 'applies [element]'."). A kit's cadence is how the codegen
    decides which of ITS rows carry the element and the gem
    (`gen_klee_cards.CharacterProfile.damage_applies_element`), so the sim
    reads the same cadence off the same owner -- never off `state.player`.
    Klee's Attack applies Pyro in Kokomi's hand, Furina's plain Attack applies
    nothing in Klee's, and a base Strike applies nothing for anybody.

    Varka has no character yaml (his player is built by `varka_oath`), so
    his identity is read off that module's own constants.
    """
    if not owner:
        return ("none", "")
    return _owner_identity_cached(owner)


@lru_cache(maxsize=None)
def _owner_identity_cached(owner: str) -> tuple[str, str]:
    if owner == varka_oath.CHARACTER:
        return (varka_oath.ELEMENT, "catalyst")
    from tier0.content import loader                # late import (cycle)
    spec = loader._character_index().get(owner)
    if not spec:
        return ("none", "")
    return (spec.get("element", "none"), spec.get("cadence", "skill"))


def printed_element(card: Card, fx: dict) -> Optional[str]:
    """What element this damage clause of this card PRINTS, before any rider.
    Who holds the card is never asked (see `owner_identity`).

    In order: a clause that declares `applies_element` says so itself (true
    takes the card's own `element`, else its owning kit's); a companion
    applies only what its clauses declare; a card that names its own
    `element` (an Ancient, `jumpy_dumpty_mk_omega`) applies it on its
    damage; otherwise the OWNING kit's cadence answers -- catalyst: its
    Attacks; skill (Furina): its damaging Skills and Burst/skill-tagged cards.

    The mod's twin is `CatalystCadence.PrintedElement`, which reads
    `HitElement` and `IElementalCard` -- the two declarations the codegen
    emits from exactly these rules -- and nothing else.
    """
    if "applies_element" in fx:
        if not fx["applies_element"]:
            return None
        element = (card.element if card.element != "none"
                   else owner_identity(getattr(card, "character", None))[0])
        return element if element != "none" else None
    if card.is_companion or fx["op"] != "damage":
        return None
    if card.element != "none":
        return card.element
    element, cadence = owner_identity(getattr(card, "character", None))
    if element == "none":
        return None
    if cadence == "catalyst" and card.type == "attack":
        return element
    if cadence == "skill" and (card.type == "skill" or "burst" in card.tags
                               or "skill_tag" in card.tags):
        return element
    return None


def _element_for(state: CombatState, fx: dict, card: Card) -> Optional[str]:
    """Which element this damage clause applies: a rider's override, else
    what the card prints (`printed_element`).

    THE ELEMENT IS THE CARD'S ([USER], 2026-10-05 -- quoted at
    `owner_identity`). Until that ruling this read the PLAYER's cadence and
    element, so a card that named none took the element of whoever played it,
    and R276 pick 2 widened that to every damaging card in Kokomi's arm. Both
    are gone: a kit's cadence now only says which of ITS OWN rows carry its
    element, and the two Kokomi Skills that relied on the widening (Opening
    Gambit, Second Wave) declare `applies_element: true` on the sheet.

    THE MONDSTADT COMPANION OVERHAUL'S ELEMENT OVERRIDE is read
    FIRST and on damage from an Attack only. Three rewritten cards print an
    element on the ATTACK rather than on themselves -- Bennett's "your next
    Attack ... applies Pyro", Razor's "for 2 turns, your Attacks apply
    Electro", Varka's "your next Attack deals 6 more damage of the swirled
    element" -- and none of them can be said by the card being played. The
    override is snapshotted once per play
    (`state.mc_attack_element_override`, set beside `current_attack_bonus`),
    so every hit of a multi-hit Attack applies the same element and a card
    that consumes the rider cannot half-apply it.

    IT OVERRIDES AN `applies_element: false` ROW TOO. "Your next Attack applies
    Pyro" is a statement about the Attack, not a modifier to a statement the
    Attack was already making, so a row that would have applied nothing applies
    Pyro. That is the literal reading; the alternative -- the override only
    replacing an element that was already going to land -- would make the three
    cards silently dead against the sheet's several no-element Attacks."""
    if (state.mc_attack_element_override
            and fx["op"] == "damage" and card.type == "attack"):
        return state.mc_attack_element_override
    return printed_element(card, fx)


# R33 lint-law (DECISIONS 87, the dead-knob exercise counter): a sweep
# that concludes "no effect" must show its swept constant was READ at
# least once per cell. This is the instrument-side tally; experiments
# reset it per cell and assert before publishing a null. E1 (pass 2)
# would have failed this loudly -- that catch is why it exists.
KNOB_READS: dict = {}


def reset_knob_reads() -> None:
    KNOB_READS.clear()


#: `EB-495` D1/D2. The sim's spelling of the game's "this damage came out of
#: a card". In C# that is `command.ModelSource is CardModel` together with
#: `DamageProps.HasFlag(ValueProp.Move)`, and the mod's generator emits EVERY
#: damage clause -- a Skill's and a Power's included -- as
#: `DamageCmd.Attack(...).FromCard(...)`, so the card's printed `type:` is
#: never read. tier0 mints exactly two `source` literals off a card
#: (`_op_damage`: `"attack"` when `card.type == "attack"`, `"card"`
#: otherwise); every kit verb mints its own, and in the game every kit verb
#: leaves through `ElementalHit.Deal`, which carries no `ModelSource` at all.
#: So "the damage came out of a card" is membership in this pair.
CARD_DAMAGE_SOURCES = ("attack", "card")

#: Hits Principle of Purity's Dark does not add to: a reaction's or a shipped
#: detonation's splash, a Shatter and poison are not her Pyro damage.
PURITY_DARK_EXCLUDED = frozenset(("reaction_splash", "detonation_splash",
                                  "shatter", "poison"))


def deal_damage_to_enemy(state: CombatState, enemy: Enemy, base: float,
                         element: Optional[str] = None,
                         source: str = "card",
                         ignore_block: bool = False,
                         powered: bool = True) -> float:
    """Full damage pipeline: strength/weak -> reaction amp -> vulnerable ->
    block -> hp. Returns damage actually dealt to HP (for metrics).

    `ignore_block` is the companion kit's (once `C.COMPANION_OVERHAUL`) and
    has exactly one caller: Chiori's Tamoto, whose printed text is "deal 6 Geo
    damage to a random enemy, IGNORING BLOCK". It skips the enemy's Block pool and nothing
    else -- the hit is still powered, still reacts, still counts as a hit and
    is still capped by Intangible, because unblockable is not uncappable
    (R128, the rule the Shatter path below already keeps). Default False, so
    every shipped caller is byte-identical.

    `powered=False` is passed by the current kits' verb doors (the call-site
    census in `tier0/tests/test_eb495_kit_verb_triggers.py` lists them).
    False drops the dealer's Strength and Weak
    (`ValueProp.Unpowered` on the dealer's side) and nothing else -- the aura
    still lands, the reaction still fires, and the target's Vulnerable,
    Intangible cap and Block still apply -- so it is NOT
    `refpowers.unpowered_damage`, which skips all of those and is what a
    Power's own damage takes. Default True, so every shipped caller is
    byte-identical, and the C# twin is one flag as well
    (`ElementalHit.Deal(..., powered: false)`).

    THE TWO ARMS ASK FOR IT FOR DIFFERENT REASONS, which is worth keeping
    straight because the flag reads as a fact about the DEALER and only one of
    them means it that way:

      * C.KOKOMI_OVERHAUL -- the Tamakushi Casket's strike and, since `EB-334`
        (R246 pick 1), every Plan's damage. Both are hits the BAKE-KURAGE deals
        rather than she does, and a pet carries no Strength. Here the flag is
        a fact about who is swinging.
      * C.KLEE_OVERHAUL -- `klee_overhaul._explode`, `EB-343` (ruled R248): a
        Bomb carries the TARGET's modifiers only, so a charge enters at its
        printed size. Here the dealer IS Klee, and the flag states the RULE
        instead.

    (The shipped Salon's `salon_member_act` passed it too, until the Salon
    left the sim on 2026-10-08.)"""
    # THE DEAD TAKE NOTHING (EB-136 / R210, C18). `CreatureCmd.Damage` opens
    # its per-target loop with `if (originalTarget2.IsDead) continue;`, so a
    # corpse absorbs no damage, fires no reaction and pays no on-hit rider --
    # and that guard sits at the FUNNEL, below `AttackCommand`, which is why it
    # is written here rather than only at `_pick_targets`. It is what makes a
    # corpse detonation spend its charges for nothing (`_op_detonate`) and it
    # also fixes a case that predates the binding: bomb 2 of a pile whose bomb
    # 1 killed used to run the reaction pipeline on the body, which could
    # consume an aura and splash off it.
    state.last_hit_landed = 0
    if not enemy.alive:
        return 0.0
    # Solar Isotoma (Crystallize engine): attack hits vs aura'd enemies
    # grant block — checked before the hit can consume the aura.
    if (source == "attack" and enemy.aura
            and state.player.powers.get("solar_isotoma", 0)):
        state.player.block += C.SOLAR_ISOTOMA_BLOCK
    was_frozen = enemy.frozen > 0   # snapshot: a hit can't shatter the
    #                                 freeze it applies
    dmg = (powers.modify_damage_dealt(state.player, base) if powered
           else float(base))
    unamped = dmg                   # EB-57: the pre-amplifier counterfactual
    # Durin, Principle of Purity / DARK (AoE trim, 2026-10-03): "Your Pyro
    # damage deals 4 more." EVERY Pyro hit she deals -- card, Bomb, Mine,
    # companion volley and the Power's own turn-start hit -- in the additive
    # phase, before the amplifier, where the flat bonuses live. A reaction's
    # splash is the reaction's damage, not Pyro damage, and is left alone.
    if element == "pyro" and source not in PURITY_DARK_EXCLUDED:
        dmg += state.player.powers.get("mc_purity_dark", 0)
    # FURINA'S NEUVILLETTE (the pool to 75): "Your Hydro damage deals 2
    # more" [3], on the same additive phase and the same exclusions -- her
    # cards' Hydro, a guest's, his own act's. The C# twin is
    # `FurinaStage.HydroBonus` (`ElementalHit.Deal` and her Fanfare badge's
    # `ModifyDamageAdditive`).
    if element == "hydro" and source not in PURITY_DARK_EXCLUDED:
        dmg += furina_stage.hydro_bonus(state)
    log_mark = len(state.log)
    dmg = reactions.resolve_hit(state, enemy, element, dmg)
    amped = dmg != unamped
    from_card = source in ("card", "attack")
    # `source` names what dealt it; "card" and "attack" are the two card
    # sources, everything else (bombs, summon pulses, shatter, splash) is
    # the base game's `cardSource == null` case.
    dmg = powers.modify_damage_taken(enemy, dmg, from_card=from_card)
    # Slow (§10.9 promotion): +N% damage from Attacks per card played this
    # turn BEFORE this one. `EB-532`: the live read (`EB-525`, Furina r12
    # lane 1) is that the attacking card does not count itself -- "it counts
    # the cards played BEFORE this one" is the sentence the page now prints
    # -- and the mod is the base game's Slow, so this engine follows it.
    # cards_played_this_turn increments at play, before resolution, which
    # is why the card in flight is subtracted back out here.
    slow_mult = (1 + enemy.slow * max(0, state.cards_played_this_turn - 1) / 100.0
                 if enemy.slow and source == "attack" else 1.0)
    if slow_mult != 1.0:
        dmg *= slow_mult
    dmg = int(dmg)
    # WHAT THE HIT LANDED FOR, before Block takes its share: the number the
    # C#'s `ElementalHit.Deal` returns (the truncated amount it hands
    # `CreatureCmd.Damage`). Big Badda Boom's "what your Bombs dealt" reads it,
    # so Block a Bomb removed counts, as base-game "damage dealt" does
    # (2026-10-04). The return value below stays the HP figure.
    landed = state.last_hit_landed = dmg
    if base > 0 and dmg > base * C.AMP_STACK_LIMIT:
        state.emit("amp_stack_warning", base=base, final=dmg, target=enemy.name)
    block_before, hp_before = enemy.block, enemy.hp
    # Hook.BeforeDamageReceived on the ENEMY -- `EB-495` D6, Thorns. HERE and
    # not at the tail with the rest of the funnel, because the game fires it
    # at `CreatureCmd.cs:285`, one line ABOVE the Block computation: a fully
    # blocked hit is thorned, and so is a killing blow, both of which the
    # AfterDamageReceived readers below are denied. `ThornsPower` is the
    # assembly's only override of this hook.
    #
    # The damage the hit is about to deal is already settled (`dmg`, one line
    # up) and Thorns cannot change it, so putting the call on this line rather
    # than at the top of the function is a placement, not a reordering.
    from tier0.engine import refpowers as _rp_thorns    # late import (cycle)
    _rp_thorns.enemy_retaliates_before_the_hit(state, enemy, source, powered)
    # (C.COMPANION_OVERHAUL). `absorb` is the Block this hit may be
    # eaten by, which is the whole of "ignoring Block": zero for Chiori's
    # Tamoto and the standing pool for every other hit in the engine. Named
    # rather than branched, so the amp counterfactual below reads the same
    # number this hit did.
    absorb = 0 if ignore_block else block_before
    blocked = min(absorb, dmg)
    enemy.block -= blocked
    hp_dmg = dmg - blocked
    # `EB-495` D5, the HP-loss half. `Hook.ModifyHpLost(..., BeforeOsty)` runs
    # on exactly this quantity in the game -- `max(modifiedAmount - blocked,
    # 0)` at `CreatureCmd.cs:286` -- and `HardenedShellPower` is the only
    # override of it in the assembly. A no-op for every enemy that does not
    # carry the power, which today is every enemy in every sim encounter.
    from tier0.engine import refpowers as _rp        # late import (cycle)
    hp_dmg = _rp.enemy_hardened_shell_cap(enemy, hp_dmg)
    was_alive = enemy.alive
    effective = min(hp_dmg, max(0, enemy.hp))   # overkill doesn't count
    # `EB-603`. THE SAME CLAMP, KEPT for the arm reader at the tail. `hp_dmg`
    # is the swing past Block and carries the OVERKILL; `effective` is what
    # the body actually lost, which is the number the `damage` emit has always
    # printed and the number Gorou's "half the damage dealt" is about.
    removed = effective
    enemy.hp -= hp_dmg
    state.emit("damage", target=enemy.name, amount=effective, blocked=blocked,
               base=base, source=source)
    if amped:
        # EB-57: the amp counter is settled HERE, not at the moment the aura
        # was consumed. `reactions._react` can only see `out - damage`, which
        # sits ABOVE every multiplier that scales the amplified hit
        # (Vulnerable/Cruelty/DoubleDamage via modify_damage_taken, the Slow
        # term) and above block and the overkill clamp -- so an amped hit into
        # a Vulnerable body under-reported its own uplift, and Superconduct
        # applies Vulnerable, so reaction decks manufactured that under-read.
        # The honest quantity is REALIZED uplift: run the unamplified hit
        # through the identical downstream chain against the SAME pre-hit
        # block and HP, and report the difference in damage that actually
        # landed. An amp whose whole contribution was overkill (or eaten by
        # block) therefore reports 0, which is the same clamp `_splash` and
        # the `damage` emit already use.
        un = powers.modify_damage_taken(enemy, unamped, from_card=from_card)
        if slow_mult != 1.0:
            un *= slow_mult
        un = int(un)
        un_hp = un - min(absorb, un)
        # The counterfactual runs the identical downstream chain, and since
        # `EB-495` D5 that chain includes the shell cap. Without this line an
        # amped hit into a Hardened Shell would credit the amplifier with
        # damage the shell refused -- the same over-read this block exists to
        # remove, one clamp later. The cap is read against the SAME pre-hit
        # spent allowance as the real hit, because `un` is that same hit.
        un_hp = _rp.enemy_hardened_shell_cap(enemy, un_hp)
        realized = effective - min(un_hp, max(0, hp_before))
        reactions.settle_amp_delta(state, log_mark, realized)
    # Frozen v2 Shatter (v1.5): the first Attack hit on a frozen enemy
    # deals bonus damage and removes Frozen. Direct HP, like splash.
    if was_frozen and enemy.frozen > 0 and source == "attack" and enemy.alive:
        # NC-7 (R116): Shatter clears the WHOLE timer, not one turn of it --
        # the mod's `PowerCmd.Remove` removes the power with all its stacks,
        # and a Shatter that left a stack behind would be a freeze the
        # player paid to end and did not.
        enemy.frozen = 0
        # shatter_bonus (Freminet, Shattering Pressure): flat rider on the
        # Shatter itself. Burst-direction growth -- every Shatter still
        # ENDS a freeze, so this cannot become control uptime.
        shatter = C.SHATTER_DAMAGE + state.player.powers.get("shatter_bonus", 0)
        from tier0.engine import refpowers          # late import (cycle)
        shatter = int(refpowers._intangible_cap(enemy, shatter))  # R128: the
        #                            cap is per hit, and a direct-HP hit is
        #                            still a hit -- unblockable != uncappable
        sh = min(shatter, max(0, enemy.hp))
        enemy.hp -= shatter
        state.emit("damage", target=enemy.name, amount=sh, blocked=0,
                   base=shatter, source="shatter")
        state.emit("shatter", target=enemy.name)
        # `sh`, not `shatter` (audit 2026-07-26 s1.7, fixed in EPOCH 1). The
        # emitted amount was already overkill-clamped and the RETURNED total
        # was not, so this one function reported two different answers for
        # the same hit depending on which you read. The docstring promises
        # "damage actually dealt to HP", which is the clamped one.
        hp_dmg += sh
        # `EB-603`: `sh` is already overkill-clamped, so the arm's total takes
        # it whole.
        removed += sh
    if was_alive and not enemy.alive:
        state.kills_this_card += 1
        # The base game's Fatal gate: cardPlay.Target.Powers.All(p =>
        # p.ShouldOwnerDeathTriggerFatal()). Summoned adds are excluded, so
        # Feed cannot farm them for permanent max HP.
        if enemy.counts_for_fatal:
            state.fatal_kills_this_card += 1
    if hp_dmg > 0:
        _detonate_bombs_on_hit(state, enemy, source)
    # Hook.AfterDamageGiven -- Envenom. Placed on the POWERED attack pipeline
    # only (this function), which is what IsPoweredAttack() means; the
    # Unpowered path in refpowers.unpowered_damage deliberately does not
    # envenom. `EB-495` D2: `powered` travels with it, because a caller INSIDE
    # this pipeline can still refuse the dealer's terms, and the game's
    # predicate is that flag rather than the card's type.
    from tier0.engine import refpowers as _refpowers
    _refpowers.envenom_on_hit(state, enemy, hp_dmg, source, powered)
    # Hook.AfterDamageReceived on the ENEMY -- `EB-495` D5 and D6, the funnel
    # tier0 did not have. BELOW Envenom for the reason the game orders them
    # that way: `AfterDamageGiven` is broadcast first (`CreatureCmd.cs:406`)
    # and `AfterDamageReceived` second (`:416`), both inside
    # `CreatureCmd.Damage` and both ABOVE `Hook.AfterAttack`, which is where
    # Skittish below sits.
    #
    # THE THREE FACTS THE BODY CANNOT RECOVER, all settled here:
    #   * `killed` -- `was_alive and not enemy.alive`. The game skips the
    #     whole broadcast for a creature this hit killed (`:410`), and by the
    #     time the funnel is called the HP has already moved.
    #   * `fully_blocked` -- `WasFullyBlocked` transcribed (`:299`): not
    #     Unblockable, Block was present or spent, and nothing reached HP.
    #     `ignore_block` is the sim's `ValueProp.Unblockable`.
    #   * `unblocked` -- `effective`, i.e. the OVERKILL-CLAMPED loss, because
    #     `DamageResult.UnblockedDamage` and `.OverkillDamage` are separate
    #     fields in the game and only the first is what the readers add up.
    _refpowers.enemy_on_damage_received(
        state, enemy, unblocked=effective,
        fully_blocked=(not ignore_block
                       and (blocked > 0 or enemy.block > 0)
                       and hp_dmg <= 0),
        killed=(was_alive and not enemy.alive),
        source=source, powered=powered)
    # Skittish (§10.9 promotion): "The first time it is hit each turn, it
    # gains N Block." AFTER the whole hit resolves (incl. any detonation
    # rider), so the triggering attack is never mitigated by it; the latch
    # resets in combat._player_turn.
    #
    # `EB-495` D1, repaired: the gate is CARD-SOURCED, not Attack-typed.
    # `SkittishPower.AfterAttack` asks
    # `command.DamageProps.HasFlag(ValueProp.Move) && command.ModelSource is
    # CardModel` (`Models/Powers/SkittishPower.cs:58`) and never reads the
    # card's `type:`, so the 17 non-Attack cards that deal damage wake it in
    # the game. tier0 asked `source == "attack"` and did not -- one-sided, so
    # the GAME is the truth and this line is the model catching up. Same
    # shape as `EB-521`'s Thorns finding.
    if (enemy.skittish and not enemy.skittish_fired
            and source in CARD_DAMAGE_SOURCES
            and enemy.alive):
        enemy.skittish_fired = True
        enemy.block += enemy.skittish
        state.emit("skittish_block", target=enemy.name,
                   amount=enemy.skittish)
    # (C.COMPANION_OVERHAUL). The INAZUMA arm's two damage-site
    # readers, both after the whole hit has resolved. See
    # `companion_overhaul_damage_dealt` for what each one is and why it is
    # here rather than anywhere else.
    # `EB-603`: `removed` AND NOT `hp_dmg`, which is what this function's
    # own docstring has always promised ("it counts damage that reached
    # HP, not the swing") and what `hp_dmg` is not: the swing carries the
    # overkill, so a killing blow paid Block for damage no body took.
    companion_overhaul_damage_dealt(state, enemy, removed, source)
    # Re-stated last: a reader above may have dealt a hit of its own.
    state.last_hit_landed = landed
    return hp_dmg


def _detonate_bombs_on_hit(state: CombatState, enemy: Enemy, source: str) -> None:
    # Bombs detonate early when the enemy is hit by an Attack card (§4.2).
    if source != "attack" or not enemy.bombs or not enemy.alive:
        return
    detonate_bombs(state, enemy)


def note_rotation_event(state: CombatState) -> None:
    """Explosives Workshop's once-per-turn latch (EB-118 sec.4.4).

    "The first time each turn you discard OR Exhaust a card" is ONE window
    over TWO event families, so the latch cannot live inside either family's
    handler: it is the COMBINED count that has to be 1. Both counters are
    zeroed together at the player's turn start, and every caller increments
    its own counter immediately BEFORE calling here, so the sum reads 1 on
    exactly the first event of the turn and never again -- no third piece of
    state, and no way for the two families to each pay once.

    WHAT IT PAYS INTO IS THE POINT. It increments the same `bomb_damage_up`
    the detonation reads, rather than a second bomb-damage stat, which is
    what makes already-placed and future Bombs agree: a Bomb armed three
    turns ago detonates at today's number. The packet asks for exactly that.

    The trigger is deliberately blind to WHICH card left -- an ordinary card
    discarded to pay a price, a card Exhausted by its own keyword, and
    Klee's status-exhaust route all count. The bound is the once-per-turn
    latch, not a filter on the victim (sec.4.4; and LAW's Klee A1/A2 rail --
    connective scaling stays bounded and never displaces her frontload).
    """
    n = state.player.powers.get("bomb_damage_per_rotation", 0)
    if not n:
        return
    if state.discards_this_turn + state.cards_exhausted_this_turn != 1:
        return
    state.player.powers["bomb_damage_up"] = (
        state.player.powers.get("bomb_damage_up", 0) + n)
    state.emit("workshop_trigger", amount=n)


def detonate_bombs(state: CombatState, enemy: Enemy, bonus: int = 0) -> None:
    bombs, enemy.bombs = enemy.bombs, []
    p = state.player
    for bomb in bombs:
        dmg = bomb.damage + bonus + p.powers.get("bomb_damage_up", 0)
        state.detonations_total += 1
        state.emit("bomb_detonation", target=enemy.name, damage=dmg)
        deal_damage_to_enemy(state, enemy, dmg, element=bomb.element,
                             source="bomb")
        if "spark_on_detonation" in p.relic_hooks:
            gain_sparks(state, 1,
                        source="relic:pounding_surprise/detonation")
        splash = p.powers.get("detonation_splash", 0)     # Blazing Delight
        if splash and C.DETONATION_SPLASH_PROC_CAP is not None:
            procs = getattr(state, "splash_procs_this_turn", 0)
            if procs >= C.DETONATION_SPLASH_PROC_CAP:
                splash = 0
            else:
                state.splash_procs_this_turn = procs + 1
        if splash:
            for other in state.living_enemies:
                # Overkill clamped out of the ACCOUNTING, not out of the hit
                # (audit 2026-07-26 s1.7, fixed in EPOCH 1). See the same fix
                # and the same reasoning in reactions._splash: the canonical
                # deal_damage_to_enemy path has always clamped, these two
                # splash paths did not, and total_damage_dealt sums exactly
                # these emitted amounts. Detonation splash hits EVERY living
                # enemy at once, so it over-read hardest against wide boards
                # of small adds -- the demolition archetype's whole premise.
                from tier0.engine import refpowers  # late import (cycle)
                sp = int(refpowers._intangible_cap(other, splash))  # R128
                effective = min(sp, max(0, other.hp))
                other.hp -= sp
                state.emit("damage", target=other.name, amount=effective,
                           source="detonation_splash")
        vuln = p.powers.get("detonation_vuln", 0)         # Explosive Frags
        if vuln and enemy.alive:
            powers.apply_power(state, enemy, "vulnerable", vuln)


def gain_sparks(state: CombatState, n: int, source: str) -> None:
    """Every Spark that lands, and the NAME of what made it (`EB-418`).

    `source` IS REQUIRED, and it is required because the r11 Opus seat could
    not name one: "My Spark went 1 to 2 with no bomb going off... This is the
    one number in the kit I could not read off the screen." The grant was
    `klee_companion_spark`, which is a real kit rule and was printed
    nowhere; the mod prints it now, and this argument is the pin that stops the
    NEXT unnamed income arriving. The C# twin is `SparkPower.Gain`'s own
    `source` parameter, which has carried exactly these strings into
    `MeterLedger` since `EB-216` -- the two vocabularies are the same
    vocabulary, so a ledger row read off the wire and an event read off a sim
    fight name the same rule.
    """
    before = state.player.sparks
    state.player.sparks += n
    # THE LEDGER IS BESIDE THE EVENT AND NOT INSIDE IT. The `gain_spark` event
    # sits inside two fixed-seed log digests taken before their arms existed,
    # and a diagnostic that moved one of those would be answering a question
    # about instrumentation with a measurement about the game. `CombatState
    # .spark_ledger` says why at greater length; the mod draws the same line
    # (`SparkPower.Gain` -> `Diagnostics.MeterLedger`).
    state.spark_ledger.append({"source": source, "amount": n,
                               "before": before, "total": state.player.sparks})
    state.emit("gain_spark", amount=n, total=state.player.sparks)
    # (R276): Spark Knight rides this chokepoint, as its C# twin
    # rides `SparkPower.Gain` -- every Spark any source grants passes here.
    klee_overhaul.spark_knight(state, state.player.sparks - before)


def klee_companion_spark(state: CombatState, card: Card) -> None:
    """"Little Hexenzirkul" -- Klee's kit answering a COMPANION play.

    UNDER THE ARM IT PAYS NOTHING (2026-09-23). R276 pick 2 had widened it to
    any card that counts as a Companion, Alice-marked plays included, and
    [USER] turned it off: "It sounds like we've massively increased the Spark
    generation and it's worth decreasing now to go back to the old levels and
    then see if play is Spark-constrained." The readers still ask
    `companion_hexerei.counts_as_companion`; only the Spark stops. Off the arm
    the shipped Personal-Companion gate and the amounts are unchanged, so the
    paragraphs below now describe the off-arm world and the history.

    THE DECLARATION LAW:145 REQUIRES, and the ONLY place a Companion play mints
    Sparks. The clause (countersigned R224, 2026-08-30) reads: "Companion cards
    may not themselves grant signature resources. A character-owned engine may
    respond to a Companion play and generate its resource where that
    character's kit explicitly declares the trigger and bounds the amount
    generated per Companion play." So the grant is HERE, in Klee's kit -- and
    `prune_witch_hunt`'s face, which used to print two `gain_spark` ops, prints
    none (EB-219).

    WHAT THE KIT DECLARES IS NOW THE PRINTED WORD (`EB-642`, R265 pick 1).
    [USER] played act 1 and read the second mark as noise: "the 'Klee's own'
    text on the Personals is not needed". So the trigger is the FAMILY MARK --
    one word, one rule -- and a Universal printing `Hexerei` grants exactly as a
    Personal printing it does. The ownership half leaves the faces in the same
    commit (`gen_klee_cards._family_tags`), because the mark and the payment
    have to say the same thing or the r20 defect returns pointing the other way.

    THE CHARACTER GATE IS EXPLICIT NOW, and it is `EB-434`: the old test was
    "the player's own Personal Companion" with no character in it, so Kokomi
    playing Gorou banked a Spark she has no surface to read. Sparks are Klee's
    resource and the tip says "gives Klee"; nobody else is paid.

    THE COMPANION GATE IS GONE UNDER THE ARM (`EB-663`, r24 lane 1). The rule
    tested COMPANION *and* Hexerei, so a Klee card carrying the mark -- Alice's
    Introduction Magic itself, or any card her this-turn window marks -- printed
    the keyword, fired the family's readers (Coven Errand, Witches' Circle) and
    paid nothing. One word cannot mean two sets on one screen. Under the arm the
    test is exactly "does this card count as Hexerei", which is the readers'
    own question; the character gate below is untouched.

    THE ARM DECIDES WHICH TEST, and that is R213 B rather than taste: no
    SHIPPED sheet row carries the family key at all, so a Hexerei-only rule
    would silently retire the grant `EB-219` moved into the kit at parity. With
    the arm off the shipped Personal-Companion pool answers, exactly as it has
    since `EB-219` -- Companion gate included, because that is the world the
    clause was countersigned over; with the arm on the printed mark answers,
    which is the world R265 ruled on. The Balance surface does not move for a
    prototype arm.

    WHAT THE ARM'S PERSONALS LOSE, said out loud: eight prototype coven rows
    (Barbara, Diona, Noelle, Kaeya, Jean, Sayu, Qiqi, YaoYao) carry
    `personal_pool: klee` and no family key, so under the arm they stop
    granting. That is the rule as ruled -- they print no word, so they pay no
    Spark -- and the fix, if the coven is meant to pay, is to mark those rows
    as family on the sheet, which is a design call and not this build's.

    WHY `companion_hexerei.counts_as_companion` AND NOT `is_companion`
    DIRECTLY: the readers (Coven Errand, Witches' Circle) ask that function,
    and Alice's Introduction Magic's this-turn window is part of the set for
    them. A rule that paid on a narrower set than the readers count would be a
    second definition of one question.

    WHY THE CALL SITE IS WHERE IT IS (`combat._finish_play`, after the FIRST
    resolution of the play):
      * ONCE PER PLAY. `_finish_play` is the shared half of every card play --
        manual and auto -- and the replay loop sits inside it, so minting on the
        first pass is "once per Companion play" by construction rather than by
        discipline. A replay (Study Buddy) is one card being resolved twice, and
        a per-play bound a replay can double is not a bound.
      * AFTER a resolution, because `reactions_this_card` is the answer to "did
        this play trigger a reaction" and it does not exist before one.
    C# says the same thing at the twin site (`KleeElementalHooks`), where
    `CompanionPlays.Record` already means "once per Companion play".

    PARITY IS THE WHOLE SPEC. See the constants block: 1 / 2 / 2 / 3 are the
    four numbers Prune's face paid and the three limbs reproduce them.
    """
    from tier0.content import upgrades          # late import avoids cycle
    if state.player.character_id != "klee":
        # `EB-434`. It is KLEE's kit that declared the trigger, and hers is the
        # only Spark surface in the game; a grant nobody can read is not a
        # grant. The old spelling of this line asked the card's pool instead of
        # the player, so Gorou paid Kokomi.
        return
    # 2026-09-23: no Companion play mints a Spark under the arm. The
    # readers (`companion_hexerei.counts_as_companion`) are untouched.
    return
    if not card.is_companion:
        return
    if card.personal_pool != "klee":
        return
    n = C.KLEE_COMPANION_SPARK_BASE
    if state.reactions_this_card > 0:
        n += C.KLEE_COMPANION_SPARK_REACTION_BONUS
    if card.id.endswith(upgrades.SUFFIX):
        # The upgrade is expressed at play time as an upgraded-flag read, which
        # is what the sheet's `kit_spark` key declares: a Companion may not
        # print a signature-resource number, upgraded or not.
        n += C.KLEE_COMPANION_SPARK_UPGRADED_BONUS
    n = min(n, C.KLEE_COMPANION_SPARK_MAX_PER_PLAY)
    if n <= 0:
        return
    state.emit("klee_companion_spark", card=card.id, amount=n)
    gain_sparks(state, n, source="companion:personal/play")


#: The one non-literal a Spark price may be spelled with: X, "spend all your
#: Sparks". The round-11 pool pass's Stoke the Fuse is the first and only row
#: that prints it, and it is a WORD rather than a number because the amount is
#: not a number the card prints -- the face says "all your Sparks" and the
#: gate says "at least one" (`spend_spark_price` below).
SPEND_ALL = "all"


def spend_spark_is_all(fx: dict) -> bool:
    """Is this Spark price the X price -- "spend all your Sparks"?"""
    return fx.get("amount") == SPEND_ALL


def spend_spark_amount(fx: dict) -> int:
    """The literal Spark price on one `spend_spark` effect.

    A LITERAL positive int, not `_amount`: `combat.spark_cost` reads the same
    number off the printed effect with no state in hand, and a price the
    playability gate cannot read is a price that fires without being shown.
    Raises rather than approximating -- the loader's vocabulary check reports
    an unknown op, and this reports an unpriceable one. `SPEND_ALL` raises
    here too, and deliberately: an X price has no literal, so every reader
    that wants a number goes through `spend_spark_price` and says which
    number it wanted.
    """
    amount = fx.get("amount")
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        raise ValueError(
            f"spend_spark amount must be a positive literal int, got "
            f"{amount!r}")
    return amount


def spend_spark_price(fx: dict) -> int:
    """What the PLAYABILITY GATE charges for this Spark price.

    The literal for a printed price, and 1 for the X price: "spend all your
    Sparks" is unplayable at an empty bank and playable at any bank that holds
    one, which is exactly a price of 1 read through `combat.card_playable`'s
    existing `sparks < price` clause. The mod says the same thing the same way
    -- an X row's `PrintedSparkPrice` is 1 -- so the number shown and the
    number gated on cannot drift apart across the two engines.

    It is NOT what the card pays: the payment is `_op_spend_spark`'s, which
    empties the bank. Two readers, two questions, and the split is the point.
    """
    if spend_spark_is_all(fx):
        return 1
    return spend_spark_amount(fx)


def spend_sparks(state: CombatState, n: int) -> bool:
    """Spend n Sparks. ALL OR NOTHING; returns whether the bank paid.

    Sparks have no overdraw currency -- the shortfall-drains-HP grammar is
    Furina's Encore alone (resources.spend_encore_or_hp) -- so a short bank
    pays NOTHING rather than draining what it holds: a partial spend leaves
    the payer believing it was paid, which is the silent-fire this op exists
    to make impossible. The refusal is EMITTED, never swallowed.

    Below the free-Attack threshold is a legal place to land: the bank is a
    resource with competing uses, and combat.spark_threshold reads the LIVE
    bank at every site (card_cost and play_card both call it), so a spend
    that drops under the bar forfeits the free Attack on the very next read.
    """
    p = state.player
    if p.sparks < n:
        state.emit("spend_spark_refused", amount=n, bank=p.sparks)
        return False
    p.sparks -= n
    state.emit("spend_spark", amount=n, total=p.sparks)
    return True


def token_card(card_id: str) -> Card:
    """One door from a stored card ID back to a fresh Card instance.

    Powers that make cards keep an ID, not an object -- Infinite Blades
    carries its token id as a row payload, Nightmare remembers what
    `SetSelectedCard` would have cloned. Almost every such id is pool
    content and comes from the loader; the exception is a STATUS, which
    `engine.statuses` synthesizes under `status_<x>` and which is
    deliberately in no pool and no loader index at all. Nightmare chooses
    from HAND and an enemy-injected Dazed is in hand, so the loader lookup
    raised `KeyError: 'status_dazed'` and killed the whole run (EB-123).

    THE LOADER IS ASKED FIRST, and the status door opens only inside the
    handler for the KeyError the loader itself raised. That ordering is the
    point rather than a detail: every id the loader already resolved is
    resolved by the same call with the same result, so no measured number
    can move -- the only behaviour that can differ is behaviour that used
    to be a crash. An id neither side knows still raises, because a typo'd
    payload is a defect and a resolver that quietly invented a card in its
    place would hide it.
    """
    from tier0.content import loader                # late import (cycle)
    try:
        return loader.get_card(card_id)
    except KeyError:
        status = statuses.status_from_card_id(card_id)
        if status is None:
            raise
        return status


def _add_token(state: CombatState, card: Card, zone: str) -> None:
    if zone == "hand" and len(state.player.hand) < C.MAX_HAND_SIZE:
        state.player.hand.append(card)
    else:
        # Every status a card of ours makes lands here, as the base game's do
        # (Turbo, Overclock, Gunk Up, Boost Away, Fight Through). The old
        # `draw` zone (shuffled in at a random depth) is gone: [USER],
        # 2026-10-03, "I agree that we should adopt the same convention".
        state.player.discard_pile.append(card)
    # Kokomi §7 engine_closure diagnostic: every created card funnels
    # through here (add_card tokens, generators, conscript-create), so the
    # per-turn creation count is structural. Report-only (R14).
    state.cards_created_this_turn += 1
    state.emit("add_card", card=card.id, to=zone)


# --- ops ---

def bonus_if_amount(state: CombatState, fx: dict) -> int:
    """The `bonus_if:` rider (AoE trim, 2026-10-03): `{if: <predicate>,
    amount: N}` adds N to the op's printed number when the predicate holds.
    One vocabulary with `conditional`'s `if:`, checked at load
    (`loader._validate_effect_vocabulary`). 0 when absent."""
    rider = fx.get("bonus_if")
    if not rider:
        return 0
    return int(rider["amount"]) if _predicate(state, rider["if"]) else 0


def _op_damage(state: CombatState, fx: dict, card: Card) -> None:
    element = _element_for(state, fx, card)
    source = "attack" if card.type == "attack" else "card"

    if fx.get("target") == "self":            # Hot Hands / No Holding Back
        state.player.hp -= fx["amount"]       # HP loss, ignores block AND
        state.emit("self_damage", amount=fx["amount"])   # Encore: a priced
        resources.note_player_hp_loss(state, fx["amount"])  # cost stays paid
        return

    # VARKA (`varka_oath.fresh_aura_sweep`): Gale Sweep's `only_if:
    # fresh_aura`, each fresh-aura enemy hit once through this op aimed at
    # its body. Dead for anyone who is not Varka.
    if (fx.get("only_if") == "fresh_aura"
            and varka_oath.live(state.player)):
        varka_oath.fresh_aura_sweep(state, fx, card)
        return

    # (R276): the Klee arm's per-hit riders. Each hit comes back
    # through this op aimed at its body, so nothing below is bypassed.
    if klee_overhaul.damage_rider(fx) and klee_overhaul.live(state):
        klee_overhaul.resolve_damage_rider(state, fx, card)
        return

    times = fx.get("times", 1)
    if "times_formula" in fx:
        formula = fx["times_formula"]
        if isinstance(formula, dict):
            times = _calc_amount(state, formula, card)
        elif formula != "2_plus_sparks":
            raise ValueError(f"unknown times_formula {fx['times_formula']!r}")
        else:
            # R39: the bank as it was at play time, NOT the post-spend bank --
            # otherwise going free at the threshold is what removes the sparks
            # the card counts.
            times = 2 + state.sparks_at_play  # Gleeful Barrage
    times = _amount(state, times)

    if "amount_formula" in fx:                # AshenStrike, BodySlam
        base = _calc_amount(state, fx["amount_formula"], card)
    else:
        base = _amount(state, fx["amount"])
    if "bonus_formula" in fx:
        base += _bonus_formula(state, fx["bonus_formula"], card)
    if card.type == "attack":
        base += state.current_attack_bonus
        # Inky enchantment (R82): the rider rides the instance, so an
        # enchanted Shiv hits harder while an ordinary one in the same hand
        # does not. Flat, folded in with current_attack_bonus.
        base += card.enchant_damage
        # Vigorous (R82 reopened): the same flat rider, but only on the
        # card's FIRST play each combat. The gate is cleared at the end of
        # the play that consumed it (resolve_card_play), so every hit of a
        # multi-hit first play collects it -- which is what "the first time
        # this card is played, it deals X additional damage" says.
        if (card.enchant_first_play_damage
                and not card.enchant_played_this_combat):
            base += card.enchant_first_play_damage
        # Corrupted: "deal 50% more damage". A MULTIPLIER, applied to the
        # card's own printed-and-riden damage and before strength/vulnerable,
        # which is where every other enchantment term sits. Truncated, the
        # engine's convention for a fractional damage term.
        if card.enchant_damage_mult != 1.0:
            base = int(base * card.enchant_damage_mult)
        # masque_red_death LEFT this sum at the 2026-07-25 redesign, for the
        # same reason celestial_gift left flat_attack_bonus at the 2026-07-26
        # red pen (the note there states the rule). It used to be a flat "+N
        # damage on your Attacks"; it is now a per-turn STRENGTH ratchet plus
        # a Bond of Life that eats the first block, and the Strength half is
        # applied as a real power in player_turn_start_triggers
        # (powers.deal_damage folds it in after this read). Leaving the rider
        # here as well paid the companion twice -- once as flat damage, once
        # as Strength -- and MasqueRedDeathPower carries no damage modifier at
        # all, so the sim was diverging from the shipped mod on top of that.
        # card_name_damage_bonus relic rider (dead branch on the battery:
        # relic_effects is empty). Flat, folded in BEFORE strength/vulnerable,
        # matching current_attack_bonus above.
        if state.player.relic_effects:
            from tier0.engine import relics       # late import avoids cycle
            base += relics.card_damage_bonus(state.player, card)
    # tag_damage_<tag> powers (Accuracy-like -> shiv) add per-hit.
    base += sum(state.player.powers.get(f"tag_damage_{t}", 0)
                for t in card.tags)
    # PhantomBladesPower pays only on the FIRST tagged card played each turn
    # ("num > 0 -> return 0", counting CardPlaysFinished this turn). The
    # playing card has not finished, so the first one sees a count of zero
    # and every later one sees at least one.
    n = state.player.powers.get("phantom_blades", 0)
    tag = state.player.power_payloads.get("phantom_blades")
    if n and tag and tag in card.tags:
        if not state.tag_plays_this_turn.get(tag, 0):
            base += n

    # R72 (2026-07-26): the vs-bombed bonus is a SNAPSHOT taken at cast, the
    # Sizzle idiom -- not a live per-hit read. Under the live read, hit 1 of a
    # multi-hit attack detonated the target's bombs and hits 2-3 then found no
    # bombs to be bonused against, so Kaboom Beetle Swarm could never pay its
    # printed bonus more than once (playtest finding 2026-07-20). The card's
    # own detonation is the payoff the bonus rewards; reading state the card
    # already consumed made the rider partly unreachable, the same failure
    # Sizzle's aura predicate avoids. Taken once per cast, so a replay
    # re-snapshots -- which is correct, a replay IS a new cast.
    # R276 (Fish Fry): under the Klee overhaul a Bomb is a charge on
    # `ko_charges`, so the snapshot reads both lists -- with the arm off the
    # second is always empty and the shipped read is unchanged.
    bombed_at_cast = ({id(e) for e in state.enemies
                       if e.bombs or e.ko_charges}
                      if fx.get("bonus_vs_bombed") else frozenset())
    # AoE trim, 2026-10-03 (Team Effort): `bonus_if: {if: <predicate>,
    # amount: N}` -- "N more if ...". ONE damage op owning one upgradable
    # number, the predicate read once at cast (the snapshot idiom above).
    base += bonus_if_amount(state, fx)

    # A POWER THAT REWRITES THIS ROW'S TargetType. FanOfKnivesPower does
    # exactly that to the Shiv (`TargetType => HasFanOfKnives ? AllEnemies :
    # AnyEnemy`), so the token's target is not a property of the token alone.
    # Declared ON the row, which is the contract refpowers.UNIMPLEMENTED
    # recorded when the Shiv was translated single-target: the power and this
    # field had to land in the same pass, and they did.
    target = fx.get("target", "enemy")
    widen = fx.get("target_all_if_power")
    if widen and state.player.powers.get(widen, 0):
        target = "all_enemies"

    # The Furina seat round (2026-09-26): `element_hits: N` -- only the FIRST N
    # hits carry the element the row declares (Bubble Aria: "the first hit
    # carries Hydro"). The rest are asked again with the declaration off, so a
    # rider still wins over them exactly as it does over any plain hit. The
    # codegen twin is `gen_klee_cards._emit_damage`: the carried hits inside
    # `HitElement.Carry`, then the rest at the same printed number.
    element_hits = fx.get("element_hits")
    rest_element = (_element_for(state, {**fx, "applies_element": False}, card)
                    if element_hits else None)

    for hit_index in range(times):
        if element_hits and hit_index == element_hits:
            element = rest_element
        # R210 Q2 -- the same binding INSIDE one op. `AttackCommand.Execute`
        # re-filters its target list by `IsAlive` on every hit and
        # `break`s the moment it is empty, so hits 2..N of a multi-hit attack
        # re-check the SAME `_singleTarget` and stop when it dies. tier0 used
        # to re-pick per hit, which spread Matinee Performance's 2s across
        # whoever was lowest-HP next. Aimed damage never lands on a corpse
        # (`allow_dead` stays False), so the empty list IS the death and the
        # break is C#'s literal shape.
        targets = _pick_targets(state, target)
        if not targets:
            break
        for enemy in targets:
            hit = base
            if fx.get("bonus_vs_bombed") and id(enemy) in bombed_at_cast:
                hit += fx["bonus_vs_bombed"]
            if fx.get("bonus_vs_aura") and enemy.aura:
                hit += fx["bonus_vs_aura"]
            # `EB-441`. The aura rider's twin, on the enemy's DEBUFFS. Same
            # per-target shape and the same classification the
            # `target_has_debuff` predicate uses -- `kokomi_plan.has_debuff`,
            # this engine's stand-in for the game's `PowerType.Debuff` -- so a
            # branch rewritten as a rider asks exactly the question it asked
            # as a branch.
            if fx.get("bonus_vs_debuff") and kokomi_plan.has_debuff(enemy):
                hit += fx["bonus_vs_debuff"]
            # THE KOKOMI EXPANSION's Ceremonial Garment: N more per debuff on
            # THIS body, her Attacks only. 0 without the Power or the arm.
            hit += kokomi_plan.garment_bonus(state, card, enemy)
            # Clorinde, Night Vigil: the same per-target aura rider, sourced
            # from a POWER instead of the card. Read before the hit resolves,
            # because resolve_hit consumes the aura it is keyed on -- the
            # identical ordering solar_isotoma needs.
            if enemy.aura and card.type == "attack":
                hit += state.player.powers.get("night_vigil", 0)
            # Bully: ExtraDamage x the DEFENDER's own stacks of a named power,
            # evaluated per target -- same shape as the aura/bomb riders above.
            rider = fx.get("bonus_per_target_power")
            if rider:
                hit += rider["per"] * enemy.powers.get(rider["power"], 0)
            deal_damage_to_enemy(state, enemy, hit, element=element,
                                 source=source)


def _op_block(state: CombatState, fx: dict, card: Card) -> None:
    if fx.get("target") == coop.ALLY:
        # THE CO-OP SET (Joint Orders): "Another player gains 6 Block." One
        # seat, nobody to give it to -- see `engine/coop.py`.
        coop.no_other_player(state, "block", card)
        return
    raw = (_calc_amount(state, fx["amount_formula"], card)
           if "amount_formula" in fx else fx["amount"])
    if "arm_amount" in fx:
        # The upgrades sheet's `arm_block` key: under the Klee arm the upgraded
        # Personal Companion's Block is the arm's number.
        raw = fx["arm_amount"]
    # Same rider grammar damage already carries (F-B1): a defensive card may
    # scale on the meter too.
    if "bonus_formula" in fx:
        raw += _bonus_formula(state, fx["bonus_formula"], card)
    times = fx.get("times", 1)
    times = (_runtime_count(state, times, card)
             if isinstance(times, str) else times)
    # Nimble (R82 reopened; EB-85 divergence 3 fixed the cadence). The rider
    # is paid on EVERY Block gain, not once per card play. The game applies
    # it inside `Hook.ModifyBlock`:
    #
    #     if (cardSource != null && cardSource.Enchantment != null) {
    #         num += enchantment.EnchantBlockAdditive(num); ... }
    #
    # with no status gate and no latch of any kind (contrast `Swift`, which
    # flips `Status = EnchantmentStatus.Disabled` after its first payout), and
    # `Hook.ModifyBlock` runs once per `CreatureCmd.GainBlock` call. So a
    # two-row Block card collects Nimble twice, and a `times` loop collects it
    # per iteration -- each of those is its own GainBlock. tier0 paid it once
    # per play off a state latch, which under-counted every multi-gain card.
    # Frail bites it, exactly as the hook order does: the enchant additive
    # lands before the multiplicative listeners.
    for _ in range(times):
        amount = raw + card.enchant_block
        # Frail bites each printed card-block gain before the refpower funnel.
        amount = powers.modify_block_gained(state.player, amount)
        state.player.block += amount
        state.block_gains_this_card += 1
        state.block_gained_this_card += amount
        state.emit("block", amount=amount)


def _op_block_half_damage(state: CombatState, fx: dict, card: Card) -> None:
    """(`C.COMPANION_OVERHAUL`). Gorou's Inuzaka All-Round Defense:
    "Gain Block equal to half the damage dealt."

    THE NUMBER IS THIS PLAY'S OWN, and it has to be: the printed 8 is not what
    landed once Strength, Weak, an amplifier and the target's Block have had
    their say, so the card reads the running total
    (`state.mi_damage_dealt_this_card`, written at the tail of
    `deal_damage_to_enemy`) rather than its own face. Kokomi's
    `block_half_surge` is the same shape asking the same question of a
    different total, which is why this is a second op and not a widening of
    that one: her clause reads a Tide and this one reads a hit.

    HALF, ROUNDED DOWN, the direction every division in this repo takes.

    THE GAIN GOES THROUGH THE PRINTED-BLOCK FUNNEL, not raw: this is a card's
    own Block line, so Frail bites it and it counts toward the per-card gain
    counters exactly as `block` above does. (The arm's POWERS grant raw Block
    -- NC-11 -- and that distinction is between a power and a card, not
    between this op and its neighbour.)
    """
    amount = state.mi_damage_dealt_this_card // 2
    if amount <= 0:
        return
    amount = powers.modify_block_gained(state.player, amount)
    state.player.block += amount
    state.block_gains_this_card += 1
    state.block_gained_this_card += amount
    state.emit("block", amount=amount)


def _op_block_next_turn(state: CombatState, fx: dict, card: Card) -> None:
    # Charlotte, First-Person Shutter: pre-emptive block that lands at the
    # start of the player's NEXT turn (after the turn-start block reset).
    # Sustain-over-time identity without true healing (R8-shaped).
    amount = _amount(state, fx["amount"])
    # NIMBLE DOES NOT RIDE HERE (EB-85 divergence 4). This op is the sim's
    # mirror of `BlockNextTurnPower`, and that power pays out with
    #
    #     await CreatureCmd.GainBlock(base.Owner, base.Amount,
    #                                 ValueProp.Unpowered, null);
    #
    # in `AfterBlockCleared`. The trailing null is the `CardPlay`, and
    # `GainBlock` passes `cardPlay?.Card` as the card source, so
    # `Hook.ModifyBlock` has no `cardSource.Enchantment` to read and the
    # enchantment is never consulted -- the Block arrives from a POWER on a
    # later turn, not from a card play. tier0 folded the rider into the
    # power's amount, which made `tideline_watch` (inert in game) a boosted
    # card here. The eligibility half is in `enchantments._grants_block`.
    powers.apply_power(state, state.player, "block_next_turn", amount)


# EB-83. The power name is the op name: one string, so `powers`, the sidecar
# and the emitted row cannot spell the same power three ways.
BLOCK_AT_TURN_START = "block_at_turn_start"


def block_at_turn_start_turns(fx: dict) -> int:
    """The literal duration on one `block_at_turn_start` effect.

    A LITERAL positive int, not `_amount`, on the `spend_spark_amount`
    precedent and for a sharper version of its reason: this number is not
    consumed once at play time, it decides how many FUTURE turns the power
    survives, and a duration resolved against combat state at play time would
    read as printed text that means something different every time it is
    played. The AMOUNT may be a formula (it is snapshotted at play time, which
    is what makes it honest); the DURATION may not.

    Raises rather than approximating -- the loader's vocabulary check reports
    an unknown op, and this reports an unplayable duration. `tier0/content/
    loader.py::_validate_effect_vocabulary` calls it at LOAD, so a sheet row
    that gets it wrong fails before a player ever meets the card.
    """
    turns = fx.get("turns")
    if not isinstance(turns, int) or isinstance(turns, bool) or turns <= 0:
        raise ValueError(
            f"block_at_turn_start turns must be a positive literal int, got "
            f"{turns!r}")
    return turns


def _op_block_at_turn_start(state: CombatState, fx: dict, card: Card) -> None:
    """Gain `amount` Block at the start of each of your next `turns` turns.

    THE DURATION-SCOPED REPEATING TWIN of `block_next_turn` (EB-83). That op
    is a one-shot bank popped whole at the next turn start; this one pays the
    same delayed Block once per turn for a printed number of turns, which is
    the shape `powers` alone cannot hold -- an int stack is one number and this
    power is two. The pair lives in `Player.timed_power_amounts`, the sidecar
    `power_payloads` established; `powers[BLOCK_AT_TURN_START]` holds TURNS
    REMAINING, the engine's own stacks-are-turns grammar, and is the LONGEST
    live instance's (see the stacking note below).

    THE AMOUNT IS SNAPSHOTTED AT PLAY TIME and never re-read: printed Block is
    printed Block at the moment it is printed, and a later Frail or a later No
    Block cannot shrink a half that was already banked.

    NIMBLE DOES NOT RIDE HERE, for `block_next_turn`'s reason verbatim: the
    Block arrives from a POWER on a later turn, so there is no `cardSource`
    for an enchantment hook to read. `enchantments._grants_block`'s allowlist
    excludes this op by construction and says so.

    NOT ROUTED THROUGH `powers.apply_power`: that function's stacking is
    additive on the stack count, and here the stack count is a DURATION, where
    additive means "playing it twice makes it last twice as long" -- the
    opposite of what every other duration in this engine does (the Ceremonial
    Garment refresh and `_op_summon_kurage` both take `max`). Written directly
    for the same reason `_op_summon_kurage` is, and emitting its own row the
    same way.

    STACKING IS INDEPENDENT INSTANCES, RULED R247 ([USER], 2026-09-03: "For
    wood carvings - agreed, 2 independent instances (5 for 2)"). A second
    casting does not merge with a standing one at all: each application is its
    own *(amount, turns)* pair, pays its own amount at every turn start it is
    still alive for, and expires on its own clock. Two Chinju Wards played on
    one turn are two 5-for-2 instances -- 10, then 10, then nothing -- and one
    played on each of two turns pays 5, then 10, then 5.

    That is `ToricToughnessPower`'s own rule and not a sim invention: the class
    declares `PowerInstanceType.Instanced` and `PowerStackType.Counter`, so the
    game holds one power object per play with the turns in its `Amount` and
    the Block in its own `BlockVar`, and `SetBlock`'s docstring says why ("this
    is necessary because Amount is used to track the number of turns left").
    The shipped placeholder before R247 was additive-on-amount / `max`-on-turns,
    which differed from this only when two instances had DIFFERENT durations --
    it stretched the smaller amount over the longer clock.

    THE COST OF THE RULING IS THE SIDECAR'S SHAPE: `powers` is `name -> int`
    and instancing needs a list where there was one integer, so
    `timed_power_amounts[name]` is now a LIST of `[amount, turns]` pairs.
    `powers[name]` stays the single int every generic reader wants and is the
    longest live instance's turns remaining -- non-zero exactly while the power
    is live, and still turns rather than a count of anything else.
    """
    amount = _amount(state, fx["amount"])
    turns = block_at_turn_start_turns(fx)
    p = state.player
    # R247: APPEND, never merge. The instance list is the power, and
    # `powers[name]` is the derived summary rather than the storage -- deriving
    # it here and at the payout from the same list is what stops the two
    # answers drifting.
    instances = p.timed_power_amounts.setdefault(BLOCK_AT_TURN_START, [])
    instances.append([amount, turns])
    p.powers[BLOCK_AT_TURN_START] = max(t for _, t in instances)
    state.emit(BLOCK_AT_TURN_START, amount=amount, turns=turns,
               instances=len(instances))


def _op_draw(state: CombatState, fx: dict, card: Card) -> None:
    if fx.get("amount_formula") == "per_aura":     # Elemental Ecstasy
        # Checked FIRST: the row carries no flat `amount`, and running it
        # through _amount would raise before this branch could fire -- the
        # pass-4 grammar widening did exactly that and broke every fight
        # that played the card (caught by the R84 roster re-run).
        n = sum(1 for e in state.living_enemies if e.aura)
    elif isinstance(fx.get("amount_formula"), dict):
        # Tide Chart: `{base: 0, per: 1, count: plans_held}`. THE SAME
        # `_calc_amount` GRAMMAR `damage` and `block` already carry, and it is
        # widened here rather than approximated on the row: a draw priced off a
        # live count has no other spelling (`amount:` takes a bare count token
        # and cannot carry a base or a per), and the two grammars were separate
        # only by accident of which op needed a live number first.
        n = _calc_amount(state, fx["amount_formula"], card)
    else:
        n = _amount(state, fx.get("amount"))
    state.draw(n)
    state.emit("extra_draw", amount=n)   # A5 velocity accounting


def _op_draw_while(state: CombatState, fx: dict, card: Card) -> None:
    """Pillage: draw one card at a time and KEEP drawing while the card just
    drawn is of `while_type` (Attack) and the hand is not full.

    A fixed CombatState.draw(n) cannot express this -- the exit condition is
    WHAT was drawn -- so this drives the draw one card at a time and inspects
    the card that actually landed in hand (draw() appends, so it is hand[-1]).

    The non-matching card that ends the loop is KEPT: the stop condition is a
    LOOK at the drawn card, not a rejection of it, matching the base game.
    Bounded by the deck -- draw() adds nothing once the hand is full, both
    piles are empty, or NoDraw denies, and a hand that did not grow ends the
    loop. The count guard is a pure backstop against an impossible infinite.
    """
    want = fx.get("while_type", "attack")
    p = state.player
    for _ in range(2 * C.MAX_HAND_SIZE):
        before = len(p.hand)
        state.draw(1)
        if len(p.hand) == before:
            break                          # hand full, deck empty, or denied
        state.emit("extra_draw", amount=1)   # A5 velocity, like _op_draw
        if p.hand[-1].type != want:
            break


def _op_energy(state: CombatState, fx: dict, card: Card) -> None:
    amount = (_calc_amount(state, fx["amount_formula"], card)  # ExpectAFight
              if "amount_formula" in fx else fx["amount"])
    state.player.energy += amount
    state.emit("energy", amount=amount)


#: `EB-415`. The sidecar key the banner banks its grant under -- the same name
#: as the power, exactly as `power_payloads` and `summon_damage` are keyed.
WAR_BANNER = "mi_war_banner"


def war_banner_grant(state: CombatState) -> int:
    """How much Dexterity the standing banner(s) handed out.

    The arm's constant is the fallback and not the rule: a banner raised by
    anything but its own card -- a test seat, the understudy's power door --
    never wrote the sidecar, and `C.MI_WAR_BANNER_DEXTERITY` is what that
    banner would have granted.
    """
    banked = state.player.timed_power_amounts.get(WAR_BANNER)
    if not banked:
        return C.MI_WAR_BANNER_DEXTERITY
    return banked[0][0] or C.MI_WAR_BANNER_DEXTERITY


def _bank_war_banner_grant(state: CombatState, card: Card) -> None:
    """Add the Dexterity THIS play granted to the standing banner's ledger.

    The number is read off the card's own effects rather than off a constant,
    which is the whole of `EB-415`: the row applies `dexterity` and then this
    clock, the upgrade moves the FIRST of those to 3, and the take-back was
    reading the second one's constant. A row that applies the clock without a
    Dexterity grant beside it banks nothing and keeps the fallback.
    """
    granted = sum(int(eff.get("amount", 0))
                  for eff in card.effects
                  if eff.get("op") == "apply_power"
                  and eff.get("power") == "dexterity"
                  and eff.get("target", "self") == "self"
                  and isinstance(eff.get("amount"), int))
    if granted <= 0:
        return
    instances = state.player.timed_power_amounts.setdefault(
        WAR_BANNER, [[0, 0]])
    instances[0][0] += granted
    instances[0][1] = state.player.powers.get(WAR_BANNER, 0)


def _op_apply_power(state: CombatState, fx: dict, card: Card) -> None:
    if fx.get("target") == coop.ALLY:
        # THE CO-OP SET (Pass the Match, Guest of Honor): a power placed ON
        # another player. One seat, nobody to place it on -- `engine/coop.py`.
        coop.no_other_player(state, "apply_power", card)
        return
    cap = fx.get("max_stacks")
    # `never_reduces` (EB-26 D2, ruled 2026-08-10, option (d)): an opt-in apply
    # mode. The application raises the stack toward ITS OWN cap and never
    # lowers a standing higher one. Absent on every other row in every sheet,
    # and absent means today's behaviour exactly.
    floor = bool(fx.get("never_reduces", False))
    if "amount_formula" in fx:                 # Dominate, MoltenFist
        amount = _power_amount_formula(state, fx["amount_formula"])
    else:
        # Through _amount, so a power amount can be X, -X or a runtime count
        # like every other op's. Literal ints pass through untouched.
        amount = _amount(state, fx["amount"])
    # MoltenFist reads the target's current Vulnerable and applies that many
    # MORE -- inert against a target with none, so the guard skips the apply.
    # Dominate needs no guard: it applies 1 first, so its read is always >= 1.
    if fx.get("guard") == "nonzero" and amount <= 0:
        return
    # POWERS THAT MAKE CARDS carry the card id as a PAYLOAD from the row that
    # applied them. InfiniteBladesPower creates the owner's Shiv every turn,
    # and refpowers.py is committed engine while a base-game card id is
    # decompiled game data (.gitignore:28) -- so the id may not appear there.
    # This keeps it where it already lives, in the gitignored card row, and
    # leaves the engine holding only "whatever this power was told to make".
    if "payload" in fx:
        state.player.power_payloads[fx["power"]] = fx["payload"]
    # `EB-463`. THE SUMMON'S PRINTED DAMAGE, BANKED AT PLAY: `summon_damage:`
    # says "this power will deal a number the CARD prints", and it is taken
    # HERE, while the card is in play, because the power fires turns later
    # when the card is gone (R72's snapshot rule; the mod's twin is
    # `SummonDamage.Note`).
    if "summon_damage" in fx:
        state.player.summon_damage[fx["power"]] = int(fx["summon_damage"])
    if fx.get("target", "self") == "self":
        powers.apply_power(state, state.player, fx["power"], amount,
                           max_stacks=cap, never_reduces=floor)
        # `EB-415`. THE BANNER BANKS WHAT ITS CARD JUST GRANTED. `powers` is a
        # name -> int map holding TURNS REMAINING for this clock, so the
        # Dexterity it will owe back has nowhere else to live; the sidecar
        # `timed_power_amounts` is the engine's one answer to "this power needs
        # a field beside its stack count" and this is its second user. Read off
        # the CARD's own effects, so the upgraded face (3 Dexterity) banks 3 --
        # which is the whole defect: the take-back was the arm's constant, 2,
        # and every upgraded play leaked the difference. The mod's twin banks
        # the same number at `WarBannerPower.AfterPowerAmountChanged`.
        if fx["power"] == "mi_war_banner":
            _bank_war_banner_grant(state, card)
    else:
        # `times` re-picks the target EVERY pass. BouncingFlask throws three
        # separate flasks at three separately-rolled random enemies, so
        # resolving the target once and applying three stacks would be a
        # different card: same total poison, none of the spread, and a
        # completely different answer against three enemies.
        times = fx.get("times", 1)
        times = (_runtime_count(state, times, card)
                 if isinstance(times, str) else times)
        # Same TargetType-rewrite contract as _op_damage: FanOfKnivesPower
        # changes the SHIV's target, and Inky's Weak reads the card's LIVE
        # TargetType -- so the rider row declares the widen and follows the
        # damage wherever the power sends it (R82).
        target = fx["target"]
        widen = fx.get("target_all_if_power")
        if widen and state.player.powers.get(widen, 0):
            target = "all_enemies"
        for _ in range(times):
            # R210 Q3: an aimed power LANDS ON THE CORPSE. `PowerCmd.Apply`
            # guards on `CanReceivePowers`, which -- unlike `IsHittable` three
            # lines above it in `Creature` -- deliberately does not test
            # `IsDead`, and the first-party doc comment says so in as many
            # words. So there is no death-break here the way there is in
            # `_op_damage`: every stack of a `times` loop lands, on a body or
            # on a corpse. The `enemy` spec is the only one this reaches --
            # `random_enemy` still re-rolls per pass, which is the note above.
            for enemy in _pick_targets(state, target, allow_dead=True):
                powers.apply_power(state, enemy, fx["power"], amount,
                                   max_stacks=cap, never_reduces=floor)


def _op_apply_aura(state: CombatState, fx: dict, card: Card) -> None:
    # R210 Q3: `ElementalHit.ApplyOnly` reaches `AuraCmd.Apply`, which is
    # `PowerCmd.Apply<XAuraPower>` -- the corpse-accepting door. An aura
    # banked on a corpse is closed by `reactions.close_dead_auras` at the
    # next settle, which is the sim's own honest bookkeeping and not a
    # divergence: the mod's aura power sits on the dead creature too.
    targets = _pick_targets(state, fx.get("target", "enemy"),
                            allow_dead=True)
    # Track H, LOG-ONLY: one row per resolution of an aura-applying VERB.
    # Distinct from `aura_applied`, which is the verb's EFFECT and is
    # silent when the op resolves into nothing (dead target, off-list
    # element). "How often does the op fire" and "how often does an aura
    # land" are two questions and the audit's claim is about the first.
    state.emit("aura_op", op="apply_aura", card=card.id,
               element=fx["element"], targets=len(targets))
    for enemy in targets:
        reactions.resolve_hit(state, enemy, fx["element"], 0,
                              "apply_aura_op")


def _pilot_policies():
    """The EB-118 switch, or None while it is off.

    LATE IMPORT, and the only direction this dependency may run in: the pilot
    imports this module, so the engine may reach the pilot at CALL time and
    never at import time. The flag is read off the module rather than bound at
    import so a test (and the Phase-2 landing) can flip one name.
    """
    from tier0.pilot import policy
    return policy if policy.PILOT_POLICIES_ENABLED else None


def _mode_chooser():
    """The EB-118 2C switch, or None while it is off.

    A SECOND flag rather than a second reader of the first, because R191 gave
    the mode chooser its own activation window and the 2A pair flips first:
    sharing `PILOT_POLICIES_ENABLED` would activate mode valuation inside 2A's
    window and leave 2C's POLICY_VERSION bump with nothing to attribute. Same
    late-import rule and same read-off-the-module rule as above.
    """
    from tier0.pilot import policy
    return policy if policy.MODE_CHOOSER_ENABLED else None


def _op_place_bomb(state: CombatState, fx: dict, card: Card) -> None:
    spec = fx.get("target", "random_enemy")
    # EB-118 (1)'s CONCENTRATION HOOK IS SUPERSEDED BY R210 FOR `target:
    # enemy`, and that is the ruling rather than a regression. `place_bomb` is
    # one of the emitter's `AIMING_OPS`, so in the mod every bomb of a
    # placement goes on `cardPlay.Target` -- All of My Treasures emits a
    # six-iteration loop over the ONE bound creature, Trip Wire puts its bomb
    # and its Weak on the same one. A per-bomb chooser is three independently
    # picked destinations where the mod has one, which is the divergence this
    # row closes restated, and the row struck per-op aim hooks from its own
    # scope for exactly that reason. Destination SCORING is severed as a later
    # design question; until it is asked, the bound lowest-HP aim is the
    # documented identity choice and the hook does not get to re-take it
    # mid-card. The hook still owns the `random_enemy` spellings, which are a
    # variance profile rather than a decision and never read `cardPlay.Target`
    # -- and the engine no longer has a spelling that asks the chooser, so the
    # call site is gone rather than gated. `pilot.policy.bomb_placement_score`
    # and `bomb_placement_target` are LEFT STANDING, unchanged: they are the
    # destination-scoring machinery the severed question will need, and no
    # pilot weight or heuristic moved in this repair.
    for _ in range(_amount(state, fx.get("amount", 1))):
        # R210 Q3: `BombPower.Place` is `PowerCmd.Apply<BombPower>`, so a bomb
        # lands on a corpse. It detonates for nothing (the damage dies at
        # `CreatureCmd.Damage`), but it is THERE, and `move_bombs` can gather
        # it. Placement stays inside the `amount` loop -- the bind is per card,
        # so every bomb of one placement goes to the same creature, which is
        # the six-iteration loop All of My Treasures emits.
        targets = _pick_targets(state, spec, allow_dead=True)
        for enemy in targets:
            enemy.bombs.append(Bomb(damage=fx["bomb_damage"],
                                    element=fx.get("element", "pyro"),
                                    turn_placed=state.turn))
            state.emit("bomb_placed", target=enemy.name,
                       damage=fx["bomb_damage"])


def _op_detonate(state: CombatState, fx: dict, card: Card) -> None:
    # R210 Q3, and this op's verdict rests on its OWN evidence rather than on
    # the PowerCmd door: `BombPower.DetonateOn` reads
    # `target.Powers.OfType<BombPower>()` with no aliveness test whatsoever,
    # and the mod already names the case -- `RecordDetonation(..., onCorpse:
    # target is { IsDead: true })`, the EB-18 counter that REPORTS AND NEVER
    # GRADES. So a detonation on a corpse HAPPENS: the charges are spent, the
    # counter ticks, and the damage behind them dies at `CreatureCmd.Damage`
    # (`deal_damage_to_enemy`'s dead-target return, this file).
    for enemy in _pick_targets(state, fx.get("target", "enemy"),
                               allow_dead=True):
        if enemy.bombs:
            detonate_bombs(state, enemy, bonus=fx.get("bonus", 0))


def _op_move_bombs(state: CombatState, fx: dict, card: Card) -> None:
    # Careful Arrangement: gather all bombs onto one enemy, +bonus each.
    # R210 Q3: the DESTINATION may be a corpse -- `BombPower.MoveAllTo` hands
    # `dest` to `PowerCmd.Apply`, which accepts one. The SOURCES may not: the
    # emitted call passes `CombatState!.HittableEnemies`, and `IsHittable`
    # opens with `if (IsDead) return false;`, so a corpse's own pile is never
    # gathered. `living_enemies` below is exactly that list.
    targets = _pick_targets(state, fx.get("target", "enemy"), allow_dead=True)
    if not targets:
        return
    dest = targets[0]
    moved = []
    for e in state.living_enemies:
        if e is not dest:
            moved.extend(e.bombs)
            e.bombs = []
    for bomb in moved:
        bomb.damage += fx.get("bonus", 0)
        dest.bombs.append(bomb)
    if moved:
        state.emit("bombs_moved", count=len(moved), to=dest.name)


def _op_modify_bombs(state: CombatState, fx: dict, card: Card) -> None:
    scope = fx.get("scope", "all")
    for e in state.living_enemies:
        for bomb in e.bombs:
            if scope == "all" or (scope == "placed_this_turn"
                                  and bomb.turn_placed == state.turn):
                bomb.damage += fx["bonus"]


def _op_swirl(state: CombatState, fx: dict, card: Card) -> None:
    # R210 Q3: same corpse-accepting door as apply_aura (`ElementalHit
    # .ApplyOnly` -> `AuraCmd.Apply` -> `PowerCmd.Apply<XAuraPower>`).
    # AND NOTHING ELSE. There is no aim re-take here any more (EB-139 / R211,
    # C20). This op used to re-aim a single-target Swirl at whichever living
    # body carried an aura when the bound aim carried none -- the ONE question
    # C18 left open, and the reason it was open is that a re-take put
    # `sayu_yoohoo_windwheel`'s damage on one creature and its Swirl on
    # another. R211 answered it at the BIND (see `bind_card_aim`): the whole
    # card goes to the lowest-HP aura-bearer, so by the time this op runs the
    # aura-aware creature IS the bound aim and asking again could only disagree
    # with the damage that preceded it.
    targets = _pick_targets(state, fx.get("target", "enemy"), allow_dead=True)
    state.emit("aura_op", op="swirl", card=card.id, element="anemo",
               targets=len(targets))
    for enemy in targets:
        reactions.resolve_hit(state, enemy, "anemo", 0, "swirl_op")


def _op_refresh_all_auras(state: CombatState, fx: dict, card: Card) -> None:
    refreshed = 0
    for e in state.living_enemies:
        if e.aura:
            e.aura_turns_left = reactions.aura_duration(state)
            refreshed += 1
    state.emit("aura_op", op="refresh_all_auras", card=card.id,
               element="", targets=refreshed)


def _op_buff_next_attack(state: CombatState, fx: dict, card: Card) -> None:
    powers.apply_power(state, state.player, "next_attack_up", fx["amount"])


def _op_cost_mod(state: CombatState, fx: dict, card: Card) -> None:
    scope = fx.get("scope")
    if scope == "companion_cards":
        state.companion_cost_delta_this_turn += fx["delta"]  # reset at turn start
        return
    if scope == "hand_free_this_turn":
        # BulletTime: every card in hand costs 0 for the rest of the turn.
        # X-COST CARDS ARE EXEMPT (`if (!card.EnergyCost.CostsX)`) and the
        # exemption is not cosmetic -- an X card resolves at the energy it
        # spent, so freeing one would make it resolve at X = 0 and do
        # nothing. Same conclusion combat.card_cost already reached for
        # FreeAttack, reached again here.
        for held in state.player.hand:
            if held.cost != "X":
                held.free_this_turn = True
        state.emit("hand_freed", cards=len(state.player.hand))
        return
    if scope == "self_this_combat":
        # UpMySleeve: `EnergyCost.AddThisCombat(-1)` on the playing instance,
        # so each copy discounts ITSELF and the discount survives the card
        # cycling through the discard pile.
        card.cost_delta_this_combat += fx["delta"]
        state.emit("cost_mod", card=card.id,
                   total=card.cost_delta_this_combat)
        return
    raise ValueError(f"unknown cost_mod scope {scope!r}")


def _op_grant_sly_this_turn(state: CombatState, fx: dict, card: Card) -> None:
    """HandTrick: give one card in hand single-turn Sly.

    The base game filters to Skills that are not ALREADY Sly this turn
    (`card.Type == Skill && !card.IsSlyThisTurn`), so a second Hand Trick in
    a turn picks a different card rather than wasting itself. Chosen through
    the same `_best_card` pilot surface every other selection uses.

    EB-71 (R174): the grant is the unified `sly_autoplay` rider carrying
    `until: turn_end`, not a separate `sly_this_turn` boolean. The target
    filter still asks the NARROW question the boolean answered -- "did a
    grant already land on this card THIS TURN" -- and deliberately not
    "is this card Sly at all": a printed-keyword Skill was a legal target
    before the unification and stays one, so no pick moves.
    """
    want = fx.get("card_type", "skill")
    pool = [c for c in state.player.hand
            if c.type == want and not sly_granted_this_turn(c)
            and not c.kit_card]
    if not pool:
        return
    pick = _best_card(pool)
    grant_sly_autoplay(pick, SLY_AUTOPLAY_THIS_TURN)
    state.emit("granted_sly", card=pick.id)


def _op_gain_spark(state: CombatState, fx: dict, card: Card) -> None:
    gain_sparks(state, fx.get("amount", 1), source=f"card:{card.id}/gain_spark")


def _op_spend_spark(state: CombatState, fx: dict, card: Card) -> None:
    """The Spark SINK (EB-118 §4.5): sparks are a resource with a competing
    use, and this is the competition.

    The COST LINE, not an overdraw: a card printing this op at top level is
    unplayable below its price (combat.spark_cost -> combat.card_playable),
    the encore_cost gate's shape, so the cost is visible before the energy
    is spent. `spend_sparks` refuses a short bank as well -- the gate cannot
    see a spend nested in a conditional branch, and an unpayable price must
    fail loudly wherever it is reached rather than half-paying.

    THE X PRICE (`amount: all`) EMPTIES THE BANK, whatever it holds. It is
    still all-or-nothing by construction -- the amount asked for IS the bank
    -- and the gate in front of it is a price of 1 (`spend_spark_price`), so
    a card that would spend nothing is not playable in the first place. The
    bank it reads is the LIVE one and not `sparks_at_play`, because this is
    the payment; the payout beside it reads the pre-spend number.
    """
    if spend_spark_is_all(fx):
        spend_sparks(state, state.player.sparks)
        return
    spend_sparks(state, spend_spark_amount(fx))


def _op_gain_fanfare_floor(state: CombatState, fx: dict, card: Card) -> None:
    """The **Fanfare +X** keyword: current, floor and cap raised together.

    Since the Fanfare rework (2026-07-28, Track B, RULED) this is a PRINTED
    keyword and a RARE POWER payoff, not an invisible automatic. It used to
    fire for free on every Power played -- see the deleted block in
    combat._finish_play -- and the whole track is about moving that value
    onto faces the player can read.

    Reads as the full grant because all three move: the meter jumps now, and
    it can never fall back past where the grant put it. That is why the
    keyword is bare "Fanfare" rather than "Fanfare Floor" -- the floor is the
    lasting half, but the immediate half is what the player feels first.

    Inert for characters without the resource, like every Fanfare path.
    """
    resources.gain_fanfare_floor(state, fx["amount"], f"card:{card.id}")


def _op_raise_fanfare_cap(state: CombatState, fx: dict, card: Card) -> None:
    """The **Fanfare Cap +X** keyword: headroom only, nothing granted.

    UN-RETIRED by the Fanfare rework (2026-07-28, Track B, RULED). This op
    died with the kickoff §4 uncapper clause because a ceiling nobody reached
    was worth nothing, and it returns for a different job: it is the SMALL
    half of the keyword pair, the thing a common or uncommon Power prints
    instead of the 5 free floor points it used to receive silently.

    Spelled "Fanfare Cap" on every face, never bare "Cap" -- the Salon's
    member cap is also a per-player stat since A12, and one word cannot mean
    both.

    STATED PLAINLY, because it changes how these numbers should be read: the
    cap has been a NON-BINDING safety rail since F-A5, and the sprint's own
    battery measured read-at-cap at under 1% under every pilot. A card that
    prints only "Fanfare Cap +X" is therefore close to inert AT CURRENT
    CONSTANTS. That is a measurement, not an argument against the keyword --
    the pair exists so the two grants can be priced apart, and the cap half
    becomes live the moment floors stack or decay softens. It is recorded
    here so nobody reads a flat result off these cards as a bug.
    """
    resources.raise_fanfare_cap(state, fx["amount"], f"card:{card.id}")


def _op_crash_fanfare(state: CombatState, fx: dict, card: Card) -> None:
    """The Hyperbeam settle (Track C.2, 2026-07-28): The Final Verdict.

    Fanfare falls to its floor, and the FLOOR falls by `amount`. The gavel
    falls once and the house is silent afterwards -- and stays quieter than
    it started, which is the price that makes "deal damage equal to Fanfare"
    a card rather than a free hit.

    Deliberately a SEPARATE op from the damage line rather than a rider on
    it, so the sheet reads in the order the card resolves: the attack reads
    the meter, THEN the meter crashes. Folding the crash into the damage op
    would make the ordering an implementation detail of one op instead of a
    visible line on the card.

    The floor MAY GO NEGATIVE (RULED). See resources.drop_fanfare_to_floor
    for the semantics and for the PROPOSED reader-clamp that goes with it.
    """
    resources.drop_fanfare_to_floor(state, fx["amount"], f"card:{card.id}")


def _op_drain_fanfare(state: CombatState, fx: dict, card: Card) -> None:
    """(R213 B): the FURINA REFRAME's drain, slice two.

    THE WHOLE OP. The held meter goes to 0 and the amount it held is recorded
    as this play's `fanfare_drained`, which the effects after it on the same
    card read through the ordinary `amount_formula: {count: fanfare_drained}`
    grammar. Two rows print it -- the Rare all-enemy hit (§4.6, `F11` (1)) and
    the survival twin beside it (`F12` (1)) -- and the pair is the point: with
    one card draining, draining is a button; with two, it is a plan.

    A SEPARATE OP AND NOT A RIDER, for `crash_fanfare`'s reason one line up:
    the sheet then reads in the order the card resolves -- the meter empties,
    THEN the number that empties it is spent -- and the ordering is a visible
    line on the row rather than an implementation detail inside a damage op.

    WHAT IT DOES NOT TOUCH, each deliberately:

      * THE FLOOR. `crash_fanfare` is the op that moves it, and moving it is
        that card's whole price; a drain is a SPEND of what has been earned,
        so the baseline the meter rests on is left exactly where it was.
      * THE CAP. Same argument from the other end, and `crash_fanfare`'s own
        note gives it: a falling ceiling would make the card quietly worse the
        second time it is played in one combat, which is a different card.
      * THE FOCUS TERM. The reframe's scaling invariant (packet §4.4) is that
        Focus multiplies PERFORMANCE numerics and nothing else, so the drained
        amount is the meter's own number and no rider reaches it. `salon_bow`
        is where the Focus term lives and it is not on this card.
      * DECAY. Untouched: an emptied meter decays from 0 like any other.

    Playable at any value, including 0 -- it reads the HELD meter and never a
    threshold, which is why neither row carries a `requires` gate. A drain of
    nothing is a wasted card and the player can see that coming from the
    meter, exactly as an empty stage is visible to `salon_bow`.
    """
    p = state.player
    if not p.fanfare_cap:                       # not a Fanfare character
        state.fanfare_drained_this_card = 0
        return
    before = p.fanfare
    drained = resources.readable(p)             # a debt cannot be drained
    p.fanfare -= drained
    state.fanfare_drained_this_card = drained
    resources.note_fanfare_change(state, before)
    state.emit("fanfare_drained", amount=drained, source=f"card:{card.id}",
               floor=p.fanfare_floor, total=p.fanfare)


def _generation_pool(state: CombatState, fx: dict, which: str) -> list[Card]:
    from tier0.content import loader                # late import avoids cycle
    if which == "guest_star":
        return loader.guest_star_generation_pool(fx["rarity"])
    if which == "character":
        # Stoke: CardFactory.GetForCombat over the character's own unlocked
        # pool, ALL rarities (no equal-rarity clause -- that guardrail is
        # specific to Guest Star generation, not the base game's).
        get_pool = getattr(loader, "character_generation_pool", None)
        if get_pool is None:
            raise NotImplementedError(
                "UNIMPLEMENTED: generate_from_pool(pool: character) needs "
                "loader.character_generation_pool(character_id), which does "
                "not exist yet. Refusing to substitute another pool -- a "
                "silently wrong generation pool is exactly the invisible "
                "bias this project exists to catch. Exclude Stoke until the "
                "loader entry point lands.")
        # CanBeGeneratedInCombat, honored HERE so no pool source can forget
        # it: Feed opts out, and generating it would hand the character a
        # permanent max-HP engine it never drafted.
        pool = [c for c in get_pool(state.player.character_id)
                if c.generatable and not c.kit_card]
        if not pool:
            raise ValueError(
                f"empty generation pool for {state.player.character_id!r}")
        return sorted(pool, key=lambda c: c.id)     # determinism under seed
    raise ValueError(f"unknown generation pool {which!r}")


def _generate(state: CombatState, fx: dict, which: str) -> None:
    import copy as _copy
    from tier0.content import loader, upgrades      # late import avoids cycle
    pool = _generation_pool(state, fx, which)
    amount = fx.get("amount", fx.get("amount_formula", 1))
    for _ in range(_amount(state, amount)):
        pick = _copy.deepcopy(state.rng.choice(pool))
        if fx.get("upgraded") and upgrades.has_upgrade(pick.id):
            # Stoke+ generates upgraded cards. The `+` id convention in
            # loader.get_card carries the upgraded form for free; a card
            # with no expressible upgrade simply arrives unupgraded, which
            # is the same visible-skip policy upgrades.UNAPPLIABLE uses.
            pick = loader.get_card(pick.id + upgrades.SUFFIX)
        if which == "guest_star":
            pick.generated_by_guest_star = True
        if "cost_override" in fx:
            # FLAG-2(ii) / NC-12 / SYS-3 (R114, Errata Batch 2 item 8):
            # "costs 0 THIS TURN", which is what the sheet prints ("They cost
            # 0 this turn") and what the mod does --
            # `GuestStarGenerator.Generate` ends in
            # `generated.EnergyCost.SetThisTurn(cost)`, verified at the three
            # cards that reach it (An Invitation, Guest List, Command
            # Performance). C# was already correct, so this is a SIM-ONLY
            # parity repair, not a design change.
            #
            # tier0 used to write `pick.cost = 0` onto the token, permanently:
            # a guest generated on turn 2 was still free on turn 9, and a
            # 0-cost token that got copied carried the zero into its copies
            # (the `copy_dup_5` taint). The turn-scoped per-instance fields
            # already exist for exactly this -- they are the base game's
            # `EnergyCost.SetToFreeThisTurn` / `AddThisTurn` -- and
            # `refpowers` sweeps them across every pile at the turn boundary,
            # so a freed token that is discarded and redrawn is not still
            # free.
            #
            # DISTINCT FROM FLAG-1's accumulator, which R114 said may not be
            # conflated with this: that one is state on the PLAYER, this one
            # is state on the CARD.
            override = fx["cost_override"]
            if override == 0:
                pick.free_this_turn = True
            else:
                # `free_this_turn` is a set-to-zero, so a non-zero override
                # rides the turn-scoped delta instead. No sheet prints one
                # today; the branch exists because `SetThisTurn` takes a
                # value and a silent no-op here would be the worse failure.
                pick.cost_delta_this_turn = override - pick.cost
        _add_token(state, pick, fx.get("to", "hand"))
        if which == "guest_star":
            state.emit("guest_star_generated", card=pick.id)
        else:
            state.emit("card_generated", card=pick.id, pool=which)


def _op_generate_from_pool(state: CombatState, fx: dict, card: Card) -> None:
    """Base-game CardPileCmd.AddGeneratedCardsToCombat (Stoke). The singular
    AddGeneratedCardToCombat (Anger, InfernalBlade) is this same op with a
    fixed id and amount 1 -- use add_card for those. Anger's
    CardCmd.PreviewCardPileAdd is pure UI and is implemented as nothing."""
    _generate(state, fx, fx.get("pool", "character"))


def _op_heal(state: CombatState, fx: dict, card: Card) -> None:
    p = state.player
    amount = fx["amount"]
    healed = min(amount, p.max_hp - p.hp)
    p.hp += healed
    state.emit("heal", amount=healed)


def companion_overhaul_entry_hp(state: CombatState) -> int:
    """The HP the player walked into this fight with -- every Mend's ceiling.

    (`C.COMPANION_OVERHAUL`), and it is the SIM TWIN of
    `KokomiOverhaulLedger.EntryHp`, captured the same two ways for the same
    reason: `combat.new_combat` records it at the top of the fight, and this
    reader captures it on first ask if nothing did -- so a state built by a
    fixture, or by a path that never opened a combat, still caps a Mend at
    something honest rather than at zero.

    PER COMBAT, on `CombatState`, because that is the object `run_fight`
    rebuilds; `Player` survives the fight and would carry one fight's ceiling
    into the next.
    """
    if not state.mi_entry_hp:
        state.mi_entry_hp = state.player.hp
    return state.mi_entry_hp


def mend(state: CombatState, amount: int) -> int:
    """MEND: heal, never above the HP you entered the fight with. Returns the
    HP that actually landed.

    ONE FUNCTION, AND IT IS THE KOKOMI ARM'S KEYWORD, NOT A SECOND ONE. The
    rule is the Kokomi brief's ("heal never above entry HP", its sec.4 rule 4),
    the C# implementation is `KokomiRules.Mend`, and this is that rule's only
    spelling in this engine -- so a Universal that prints Mend and one of her
    own cards that prints it cannot come to mean different things.

    CHARACTER-AGNOSTIC ON PURPOSE. Mizuki's Anraku Secret Spring Therapy is a
    UNIVERSAL: Klee or Furina can draft it, and "the one true heal in the pool"
    has to be the same keyword with the same bound in whoever's hands it lands.
    The C# half is the same change made from the other side -- `KokomiRules.Mend`
    stops asking whether the creature is Kokomi and starts asking whether
    EITHER arm is live for it -- rather than a second Mend written for the
    companion pool.

    WHAT IT DOES NOT CARRY. Sango Isshin's overflow ("Mend past your entry HP
    becomes Hydro damage") is a draft-2 rule the ruled brief's sec.6 cut; draft
    6's Sango Isshin is an Attack with a planned all-enemies half and no
    overflow at all. With no such power the excess is simply lost, which is
    what the cap has always meant on both sides.
    """
    room = companion_overhaul_entry_hp(state) - state.player.hp
    landed = min(amount, room) if room > 0 else 0
    if landed <= 0:
        return 0
    state.player.hp += landed
    state.emit("heal", amount=landed, keyword="mend")
    return landed


def _op_mend(state: CombatState, fx: dict, card: Card) -> None:
    """The `mend` op: the Universal keyword above (Mizuki's Anraku Secret
    Spring Therapy), and Kokomi's two Rares and one planned clause.
    """
    mend(state, _amount(state, fx["amount"]))


def _op_add_card(state: CombatState, fx: dict, card: Card) -> None:
    from tier0.content import loader                # late import avoids cycle
    zone = fx.get("zone") or fx.get("to", "discard")
    n = _amount(state, fx.get("amount", 1))
    if fx.get("card") == "self":                    # Anger: clone THIS card
        # CreateClone() of the playing instance -- so Anger+ clones an
        # UPGRADED copy. A fixed card_id add would reload the base id and
        # silently downgrade the clone (the whole point of the mechanic is
        # that the clone inherits this instance's upgrade state).
        import copy as _copy
        for _ in range(n):
            clone = _copy.deepcopy(card)
            if "cost_override" in fx:
                clone.cost = fx["cost_override"]
            _add_token(state, clone, zone)
        return
    if "pool" in fx:                                # Secret Stash
        pool_cards = loader.cards_in_pool(fx["pool"])
        picks = [state.rng.choice(pool_cards) for _ in range(n)]
        ids = [c.id for c in picks]
    else:
        ids = [fx.get("card_id") or fx["card"]] * n
    for cid in ids:
        # `upgraded` is the IsUpgraded branch on HiddenDaggers and StormOfSteel
        # -- they upgrade the tokens they just made. Loaded as the upgraded
        # card rather than created-then-upgraded, which is the same result and
        # keeps the upgrade grammar in one place.
        if fx.get("upgraded"):
            from tier0.content import upgrades
            # ONLY the missing-entry shapes (ValueError from apply_upgrade,
            # KeyError for an unknown id) may degrade to the base copy: a
            # loader defect masquerading as a missing upgrade would quietly
            # play base cards forever.
            try:
                token = loader.get_card(cid + upgrades.SUFFIX)
            except (KeyError, ValueError):
                state.emit("UNIMPLEMENTED", op="add_card", card=cid,
                           reason="no upgrade entry; created unupgraded")
                token = loader.get_card(cid)
        else:
            # THE STATUS BATCH (Flotsam Surge): a synthesized status id
            # (`status_dazed`) resolves through `token_card`, which asks the
            # loader first, so every pool id resolves exactly as before.
            token = token_card(cid)
        if "cost_override" in fx:
            token.cost = fx["cost_override"]
        # Enchant-at-creation (R82, Blade Of Ink): the rider attaches in the
        # same resolution that creates the token, so "a card that never
        # existed in the deck" is not a special case.
        enchant = fx.get("enchant")
        if enchant:
            token.enchant_damage += enchant.get("damage", 0)
            token.enchant_effects = (list(token.enchant_effects)
                                     + list(enchant.get("effects", [])))
        _add_token(state, token, zone)


def _discard_victims(state: CombatState, n: int, chosen: bool):
    """The victims of one `discard` op, in the order they are discarded.

    BATCH-SELECTION CONTRACT (chosen only). Canon's discard screen picks the
    WHOLE batch before any of it leaves the hand, so selection membership is
    decided against the hand as it stood when the op began. This walk
    therefore takes all `n` picks up front off ONE candidate list that only
    ever shrinks -- it never re-reads `state.player.hand`.

    That matters because the caller resolves each victim's authored Sly rider
    INLINE, and Kokomi's riders draw, recall and create. Re-polling the hand
    per pick let a card that did not exist when the player was asked become
    the next victim (`drifting_lantern`'s `sly: draw 1` thrown to
    `open_the_stores`' discard-2 is the live shape). Rider TIMING is
    unchanged -- each victim still discards and fires in order; only
    MEMBERSHIP is fixed up front. A rider that moves a not-yet-processed
    victim out of hand is handled by the caller's `remove_instance` guard.

    RANDOM keeps its per-pick re-poll, deliberately. It is the DEFAULT and
    every card that discards without `select:` was priced against it; nothing
    in the decompile reference was read to say canon batches the random path
    too, so it is left exactly as it was rather than flipped on a guess.
    """
    if chosen:
        candidates = [c for c in state.player.hand if not c.kit_card]
        picks: list[Card] = []
        for _ in range(n):
            if not candidates:
                break
            victim = _worst_card(candidates)
            picks.append(victim)
            candidates = [c for c in candidates if c is not victim]
        yield from picks
        return
    for _ in range(n):
        pool = [c for c in state.player.hand if not c.kit_card]
        if not pool:
            return
        yield state.rng.choice(pool)


def _op_discard(state: CombatState, fx: dict, card: Card) -> None:
    # Kit cards are exempt: the v1.9 invariant is that the Burst never
    # enters a pile. Without this, a random discard (Bright Idea) moved
    # the granted Burst to discard, it circulated as loot on reshuffle,
    # and grant_charged_kit -- which dedups against HAND only -- appended
    # the same object a second time. Review-workflow catch, repro'd.
    #
    # `select: chosen` is the base-game "Discard N cards" shape (Silent's
    # Survivor is in her STARTING DECK, so real_silent cannot be built
    # without it). Same random/chosen split `_op_exhaust_from` already
    # makes, through the same `_worst_card` pilot surface, so a chosen
    # discard is not a second heuristic to keep honest. Random stays the
    # DEFAULT: every existing card that discards does so at random, and a
    # silent flip would re-price them.
    #
    # WHO is discarded is `_discard_victims`' business and its batch-selection
    # contract is stated there; WHAT each discard does is this function's. The
    # split is the point: selection membership must be answerable without
    # reading the rider machinery below it.
    chosen = fx.get("select", "random") == "chosen"
    sly_batch: list[Card] = []
    # `amount: hand_size` is how "discard your hand" is spelled -- resolved
    # ONCE, here, before the first card leaves, so it cannot chase its own
    # shrinking pool. The victim walk's own empty-pool stop already handles a
    # hand smaller than the number asked for.
    n = _amount(state, fx.get("amount", 1))
    for victim in _discard_victims(state, n, chosen):
        # A rider fired by an EARLIER victim in the same batch may already
        # have moved this one out of hand (`open_the_stores`' Sly exhaust is
        # the live shape: discard 2 chosen, and the first card's rider
        # exhausts a card that may be the second pick). Skip it rather than
        # resurrect it from wherever it went -- the same rule the
        # `sly_batch` walk below applies to the discard pile.
        if not remove_instance(state.player.hand, victim):
            continue
        state.player.discard_pile.append(victim)
        state.discards_this_turn += 1
        note_rotation_event(state)          # EB-118 sec.4.4, seam 1 of 3
        state.discards_this_card += 1
        if chosen:
            state.emit("discard", card=victim.id, chosen=True)
        else:
            state.emit("discard", card=victim.id)
        # SLY — the one trigger site for BOTH halves of the unified grammar
        # (EB-71, R174; see state.Card.sly and docs/silent-anchor-kickoff §6).
        # Fires ONLY on card-effect discards from hand. A CHOSEN discard is
        # still a card-effect discard, so it triggers too. The end-of-turn
        # hand flush is NOT Sly (a silent turn pays nothing — the
        # activity-gating law), and draw-pile discards (scry_discard) are not
        # either; discard_for_sparks is Klee's own verb and no Klee card
        # carries a sly list.
        #
        # AUTHORED riders (Kokomi's Assist lane) resolve HERE, inline, with
        # the discarded card as context, AFTER it reaches the discard pile
        # (StS2 order). The base-game auto-play rider resolves after the
        # loop instead — see the batch note below. Inline is the RULED
        # timing and is unchanged; what a rider can no longer do is add to
        # the batch it is part of (`_discard_victims`).
        riders = sly_riders(victim) if victim.sly else []
        if riders:
            state.emit("sly", card=victim.id)
            _resolve_effects(state, riders, victim)
        if sly_autoplays(victim):
            sly_batch.append(victim)
    # BASE-GAME Sly (the `sly_autoplay` rider, ask A4). Deliberately AFTER
    # the loop:
    # CardCmd.DiscardAndDraw discards the WHOLE batch first -- each card
    # reaching the pile and firing AfterCardDiscarded, which is the hook
    # Kokomi's `sly` above is standing in for -- and only then auto-plays the
    # Sly ones, in discard order. Its own docstring warns that discarding in
    # a loop gets this timing wrong, so the batch is not cosmetic: with two
    # Sly cards, the second is already in the discard pile while the first
    # resolves, and a card counting the pile sees it.
    #
    # KNOWN ORDERING DIVERGENCE: the game draws BETWEEN the batch discard and
    # the auto-plays (that is what DiscardAndDraw exists for). tier0 spells
    # "discard N, draw M" as two ops, so a following draw op lands AFTER the
    # auto-plays here. Recorded rather than papered over -- fixing it means a
    # combined op, and no emitted Silent row needs one yet.
    for victim in sly_batch:
        if state.over or not state.player.alive:
            break
        if not remove_instance(state.player.discard_pile, victim):
            continue          # an effect already moved it; do not resurrect
        state.emit("sly_autoplay", card=victim.id)
        _free_play(state, victim, force_exhaust=False)


def kokomi_rotation_law(player) -> bool:
    """Does this player's Exhaust economy run under Kokomi's rotation law?

    Keyed on the Tamakushi Casket relic hook -- the SAME seam the Charge
    funnel in refpowers.after_card_exhausted is keyed on -- so the law and
    the accrual it governs are switched by one fact. The upgraded starter
    (Pearl of Insight) keeps the hook, so the law survives the upgrade.
    A real_ironclad True Grit+ has no hook and keeps its any-card pool."""
    return "tamakushi_casket" in player.relic_hooks


def exhaust_pool(state: CombatState, fx: dict,
                 exclude: Optional[Card] = None) -> list[Card]:
    """The already-legal candidates ONE `exhaust_from` may take.

    ONE definition, TWO consumers, which is why it is a named function rather
    than eight lines inside the op: `_op_exhaust_from` builds the real pool
    with it at RESOLUTION time, and `policy._forecast_exhaust_selection`
    (`EB-145`) builds the same pool at SCORE time. A pilot pricing the payout
    of its own selection therefore cannot disagree with the pool the engine
    will actually offer it -- the Track C.2 lesson, applied to a pool instead
    of to a predicate.

    `exclude` is the card being PLAYED. At resolution time it has already left
    hand (`combat.play_card` removes the instance before resolving), at score
    time it has not, so the score-time caller names it and the two callers see
    the same list. Identity, never equality: `Card` is a value-equality
    dataclass and two copies of one row are two candidates.

    DEFECT FIX kept from the inline form: the status branch used to rebuild the
    pool from `hand` and so dropped the kit-card exemption -- a status-filtered
    exhaust could eat the granted Burst, breaking the v1.9 invariant that the
    kit never enters a pile. Filter the exempt pool instead.
    """
    pool = [c for c in state.player.hand
            if not c.kit_card and c is not exclude]  # same invariant as discard
    if fx.get("filter") == "status":
        pool = [c for c in pool if c.rarity == "status"]
    elif fx.get("filter") == "non_attack":
        pool = [c for c in pool if c.type != "attack"]
    elif kokomi_rotation_law(state.player):
        # ROTATION LAW ([USER] 2026-08-23): Kokomi rotates her OWN cards
        # out, never a Status or a Curse. The unfiltered pool -- chosen or
        # random -- drops junk under her law; a card that IS allowed to eat
        # junk says so with an explicit `filter:` (Dodge Roll's shape), which
        # is the branch above and is untouched. The old behaviour ("statuses
        # and curses count too, accepted quirk", kickoff v1 §2.1) made her
        # uniquely status-resistant for free; that quirk is retired, and the
        # design space it vacates is a dedicated Uncommon/Rare card.
        pool = [c for c in pool if not c.is_junk]
    return pool


def _op_exhaust_from(state: CombatState, fx: dict, card: Card) -> None:
    hand = state.player.hand
    pool = exhaust_pool(state, fx)
    n = fx.get("amount", 1)
    # Stoke exhausts the WHOLE hand and then generates that many cards. The
    # count is fixed BEFORE any exhausting (the dll reads exhaustCount off
    # the selection list up front), which is what len(pool) here gives us.
    n = len(pool) if n == "all" else _amount(state, n)
    # TrueGrit's split: base form exhausts at RANDOM, the upgrade lets the
    # player choose -- exactly the split _op_discard_for_sparks already
    # makes, and it reuses the same _worst_card instrument surface.
    chosen = fx.get("select", "random") == "chosen"
    # EB-118: OPEN this effect's own context. Rebound, not cleared in place --
    # combat._FREE_PLAY_CONTEXT saved the outer card's list OBJECT, and an
    # in-place clear here would empty that too. A second exhaust_from on the
    # same card therefore replaces the first's record, which is the ruled
    # behaviour: two rotations on one card are two questions, not one pile.
    # Opened BEFORE the loop, so an empty pool leaves an empty selection
    # rather than the previous effect's.
    selection: list[dict] = []
    state.exhaust_selection = selection
    for _ in range(n):
        if not pool:
            break
        if chosen:
            # EB-118 (2): the chosen branch only. A random exhaust is not a
            # decision, and `_op_discard`/`_op_conscript` keep the placeholder
            # -- this policy is scoped to `exhaust_from`, where the payout is
            # on the exhausting card.
            pol = _pilot_policies()
            victim = (pol.exhaust_victim(state, pool, card) if pol is not None
                      else _worst_card(pool))
        else:
            victim = state.rng.choice(pool)
        pool = [c for c in pool if c is not victim]
        remove_instance(hand, victim)
        state.player.exhaust_pile.append(victim)
        # The second of the two append sites CombatState.exhausts_this_turn
        # is maintained at. This one is the reason the field exists: the
        # victim lands here MID-PLAY, and the same card's later effects can
        # read the count that includes it.
        state.exhausts_this_turn += 1
        state.exhausted_this_card += 1
        # Recorded off the instance BEFORE anything downstream can touch it,
        # and from the PRINTED fields only, so the row is the same one the
        # mod's selector path can build off a CardModel.
        selection.append(exhaust_descriptor(victim))
        if chosen:
            state.emit("exhaust", card=victim.id, chosen=True)
        else:
            state.emit("exhaust", card=victim.id)
    # The parity row, emitted once per resolved selection (including the empty
    # one -- "nothing was there to take" is a reading, not a gap). Emit-only:
    # nothing in the engine reads this back, the formulas read the context.
    state.emit("exhaust_selection", **exhaust_selection_row(state, card))


def _worst_card(cards: list[Card]) -> Card:
    # Shared v1 "lowest-value" pick: highest cost non-attack first (pilot
    # heuristic placeholder; spec allows dumb). INSTRUMENT SURFACE: every
    # chosen-discard measurement rides this choice -- if a window result
    # looks heuristic-shaped, this is the knob to probe.
    return max(cards, key=lambda c: (c.type != "attack",
                                     c.cost if isinstance(c.cost, int) else 99))


def _best_card(cards: list[Card]) -> Card:
    # Mirror of _worst_card for "pick a GOOD card" selections (Headbutt's
    # recall). Prefer an attack, then the most printed power. INSTRUMENT
    # SURFACE: every recall measurement rides this choice.
    return max(cards, key=lambda c: (c.type == "attack", _printed_power(c)))


def _walk_effects(effects: list[dict]):
    """Effect list walk including conditional branches and modal modes."""
    for fx in effects:
        yield fx
        for branch in ("then", "else"):
            if isinstance(fx.get(branch), list):
                yield from _walk_effects(fx[branch])
        # A mode body is printed text the same way a branch is -- the player
        # can always reach it -- so `_printed_power` must see it or a modal
        # card scores as blank to every chooser that ranks on printed power.
        for mode in fx.get("modes") or ():
            if isinstance(mode, dict) and isinstance(mode.get("effects"), list):
                yield from _walk_effects(mode["effects"])


def _printed_power(card: Card) -> int:
    """Sum of printed damage and Block on a card — the crude 'how big is
    this card' scalar the choice heuristics rank by. Deliberately reads
    PRINTED numbers only (no strength, no Spotlight, no formulas): the
    pilot is choosing before resolution, and a formula amount is not a
    number it could compare anyway."""
    total = 0
    for fx in _walk_effects(card.effects):
        if fx.get("op") not in ("damage", "block"):
            continue
        amount, times = fx.get("amount"), fx.get("times", 1)
        if isinstance(amount, int) and isinstance(times, int):
            total += amount * times
    return total


def _best_upgrade_target(hand: list[Card], idxs: list[int]) -> int:
    """Armaments' choice: greedy delta — the eligible card that gains the
    most printed damage+block from being upgraded. Ties break to the lowest
    hand index so the pick stays deterministic under a fixed seed.
    INSTRUMENT SURFACE (same convention as _worst_card)."""
    import copy as _copy
    from tier0.content import upgrades              # late import avoids cycle

    def delta(i: int) -> int:
        # Score the same live instance the upgrade will mutate. Reloading the
        # base row erases Rampage growth and temporary generated-card state.
        upped = upgrades.apply_upgrade(_copy.deepcopy(hand[i]))
        return _printed_power(upped) - _printed_power(hand[i])

    return max(idxs, key=lambda i: (delta(i), -i))


def _op_discard_for_sparks(state: CombatState, fx: dict, card: Card) -> None:
    """R36 (Crackle redesign, user-ratified 2026-07-20): FORCED,
    PLAYER-CHOSEN discard; 1 Spark per card ACTUALLY discarded, capped at
    fx["sparks"]. Short hand discards min(amount, hand); an empty hand
    yields no fodder and NO Spark -- the Spark is priced BY the discard
    (an empty-hand free Spark converges on the exact design the ratified
    band rejected, 0.668 vs 0.65). Kit cards are exempt fodder (the v1.9
    invariant, same pool rule as _op_discard)."""
    discarded = 0
    for _ in range(fx.get("amount", 1)):
        pool = [c for c in state.player.hand if not c.kit_card]
        if not pool:
            break
        victim = _worst_card(pool)          # the pilot's chosen discard
        remove_instance(state.player.hand, victim)
        state.player.discard_pile.append(victim)
        state.discards_this_turn += 1
        note_rotation_event(state)          # EB-118 sec.4.4, seam 2 of 3
        state.emit("discard", card=victim.id, chosen=True)
        discarded += 1
    gain = min(fx.get("sparks", discarded), discarded)
    if gain:
        gain_sparks(state, gain, source=f"card:{card.id}/discard_for_sparks")


def _op_scry_discard(state: CombatState, fx: dict, card: Card) -> None:
    # Look at top N, discard the "worst" (shared heuristic above).
    n = fx.get("amount", 1)
    top = state.player.draw_pile[:n]
    if not top:
        return
    worst = _worst_card(top)
    remove_instance(state.player.draw_pile, worst)
    state.player.discard_pile.append(worst)
    state.emit("scry_discard", card=worst.id)


def _op_scry_bottom(state: CombatState, fx: dict, card: Card) -> None:
    """`EB-655`, READ THE FIELD: "look at the top N cards of your draw pile and
    put one of them on the bottom".

    THE PILOT BOTTOMS THE HIGHEST-COST CARD, which is this engine's stand-in
    for player choice and is stated rather than hidden: the sim has no human,
    a look-and-bottom is only worth anything if somebody chooses, and "the one
    I can least afford next turn" is the crude legible version of the
    judgement. `_worst_card`'s precedent (`scry_discard`) is the same shape one
    verb over, and the mod puts a real selection screen here instead
    (`gen_klee_cards`'s emitter, `ScryBottom.Prompt`).

    THE CARD IS MOVED WITHIN THE DRAW PILE, not discarded: an empty or shorter
    pile is a printed no-op, and a pile of one card puts that card back where
    it already was, which is the honest answer to a look with no choice in it.
    """
    n = fx.get("amount", 1)
    top = state.player.draw_pile[:n]
    if not top:
        return
    pick = max(top, key=lambda c: (c.cost if isinstance(c.cost, int) else 0))
    remove_instance(state.player.draw_pile, pick)
    state.player.draw_pile.append(pick)
    state.emit("scry_bottom", card=pick.id, seen=len(top))


def _op_scry_take(state: CombatState, fx: dict, card: Card) -> None:
    """`EB-679` (pool pass four), READ THE FIELD: "look at the top N cards of
    your draw pile; put one into your hand and the rest on the bottom".

    SELECTION AND NOT A LOOK, which is the whole redesign. `scry_bottom` asked
    the player to bury one card of two and r26's lane never made a decision off
    it -- burying the card you like least is a choice about the card you did
    not want, and the seats valued taking the card they DID. So the pick comes
    to hand and everything it was seen beside goes to the bottom, which is what
    makes the number on the face worth moving (3, and 4 upgraded).

    THE PILOT TAKES THE LOWEST-COST CARD, this engine's stand-in for player
    choice, stated rather than hidden -- `_op_scry_bottom`'s convention read
    the other way round, because the card wanted now is the one that can be
    paid for now.  The mod puts a real selection screen here instead
    (`ScryBottom.TakePrompt`, and `gen_klee_cards`'s emitter).

    THE REST GO TO THE BOTTOM IN THE ORDER THEY WERE SEEN, so nothing leaves
    the deck and the pile beneath them is untouched. A pile shorter than N is
    read short rather than refused, and an empty pile is a printed no-op --
    the shape `_op_scry_bottom` already keeps.
    """
    n = fx.get("amount", 1)
    top = state.player.draw_pile[:n]
    if not top:
        return
    pick = min(top, key=lambda c: (c.cost if isinstance(c.cost, int) else 0))
    for seen in top:
        remove_instance(state.player.draw_pile, seen)
    state.player.hand.append(pick)
    for seen in top:
        if seen is not pick:
            state.player.draw_pile.append(seen)
    state.emit("scry_take", card=pick.id, seen=len(top))


def _op_conditional(state: CombatState, fx: dict, card: Card) -> None:
    fired = _predicate(state, fx["if"])
    # D4 telemetry (salon UI sprint, 2026-07-28). EMIT-ONLY, and deliberately
    # generic rather than a graceful_retreat special case: "how often does
    # this rider actually fire" is a question every conditional on the sheet
    # can be asked, and a card-specific counter would have to be rewritten
    # for the next suspect. The event carries the predicate NAME so a
    # fire-rate can be read per card, per predicate, or both.
    state.emit("conditional", card=card.id, predicate=fx["if"], fired=fired)
    branch = fx["then"] if fired else fx.get("else", [])
    _resolve_effects(state, branch, card)


# --- the modal / choose-one surface (EB-118 sec.5.4, LIVE) -----------------
#
# A `choose_one` effect carries `modes:`, a list of 2+ dicts, each one a
# `label:` and an ordinary `effects:` list. It is NOT a new keyword: the
# label is the plain card text of that mode and the bodies are the same op
# vocabulary the rest of the sheet uses, so a modal card reads as ordinary
# card text and no keyword tooltip is owed.
#
# The distinction from `conditional` is WHO decides. A conditional reads a
# predicate off the board; a modal asks the player. That makes mode selection
# a play-time CHOICE, which in this engine means the chooser seam beside
# `_worst_card` / `_best_card` -- the same surface `select: chosen` exhaust,
# chosen discard and Armaments' upgrade target already ride.
#
# ONE SHIPPED CARD IS MODAL: `deep_breath`, the Phase-2C prototype (R192 chose
# the card, R194 ruled the pair, R205 re-bodied mode 2). That is the whole
# reach of this surface and it is a discipline, not an accident -- the pattern
# is not copied until the pilot and the price can distinguish the modes
# (packet sec.5.4). The frozen calibration battery holds no modal card, so it
# cannot move across the chooser's flip; that is checked, not assumed.

MODES_KEY = "modes"
MODE_FIELDS = frozenset({"label", "effects"})
MODAL_FIELDS = frozenset({"op", MODES_KEY})
MIN_MODES = 2


# --- EB-182: per-option playability (R224 item 17, option 3) ---------------
#
# THE RULE, one sentence: a mode whose body OPENS with a resource spend is
# that mode's COST LINE, and a mode the bank cannot pay is not offered.
#
# WHY THE OPENING EFFECT AND NOT ANY SPEND IN THE BODY. The label a priced
# mode prints is "Spend 3 Encore: draw 3" -- a price, a colon, a payout -- and
# the colon is exactly the boundary this reads. A spend further down a body is
# a CONSEQUENCE of the mode rather than its admission fee (it may be paid out
# of what the same body just generated), and the engine keeps refusing those
# where they resolve: `spend_sparks` is all-or-nothing, `ChargeUnpaid` stops
# the card, `spend_encore_or_hp` overdraws. So this is the modal twin of
# `combat.spark_cost` / `combat.charge_cost`'s "TOP-LEVEL ops only" rule, one
# nesting level down, and it stops exactly where those stop.
#
# CONSEQUENCE, STATED: `deep_breath` mode 2 (`spend_encore 3`) was takeable on
# a short bank and overdrew the shortfall into HP. It is now not offered below
# 3 Encore. That is the acceptance EB-182 was filed with -- "a short bank
# cannot pick a dead mode" -- and it is a real behaviour change on one shipped
# card, not a display fix. The Klee arm this unblocks (Bag of Tricks, a
# Spark-priced mode) is the second consumer.
MODE_PRICE_OPS = {
    "spend_spark": ("sparks", "Sparks"),
}


def mode_price(state: CombatState, mode: dict):
    """`(bank field, meter name, amount)` for a priced mode, else None.

    The amount is read the way the PAYING op reads it: the two literal-only
    meters through their own validators (so a malformed price fails here the
    way it fails at resolution), Encore through `_amount`, which admits the
    state-dependent forms that op already accepts.
    """
    body = mode.get("effects") or []
    if not body:
        return None
    fx = body[0]
    op = fx.get("op")
    if op not in MODE_PRICE_OPS:
        return None
    field, meter = MODE_PRICE_OPS[op]
    amount = spend_spark_amount(fx)
    return field, meter, int(amount)


def mode_affordable(state: CombatState, mode: dict) -> bool:
    """Is this mode OFFERED? True for an unpriced, unrefused mode.

    Two gates, and they are two rules. EB-182's PRICE asks whether the bank can
    pay; `EB-746`'s RULE asks whether the board admits the mode at all -- the
    Stage's Spend, offered only when Furina holds its whole price in Fanfare
    (`furina_stage.mode_offered`). A mode neither reaches is offered, which
    keeps every unpriced fixture byte-identical.
    """
    if furina_stage.mode_offered(state.player, mode) is False:
        return False
    price = mode_price(state, mode)
    if price is None:
        return True
    field, _meter, amount = price
    return getattr(state.player, field) >= amount


def mode_refusal(state: CombatState, mode: dict) -> Optional[str]:
    """Why this mode is not offered -- naming the price AND the bank.

    None when the mode IS offered. The string is the printable half of the
    rule: a staged-turn packet, the falsifier and a replay all reach it
    through `combat.modal_refusal`, so a refused line can say what was short
    instead of merely not appearing.
    """
    rule = furina_stage.mode_refusal(state.player, mode)   # `EB-746`
    if rule is not None:
        return rule
    price = mode_price(state, mode)
    if price is None:
        return None
    field, meter, amount = price
    bank = getattr(state.player, field)
    if bank >= amount:
        return None
    label = mode.get("label") or "(unlabelled mode)"
    return f"{label!r} needs {amount} {meter}, bank holds {bank}"


def offered_modes(state: CombatState, modes: list[dict]) -> list[int]:
    """The mode indexes a player may actually pick, in sheet order."""
    return [i for i, mode in enumerate(modes) if mode_affordable(state, mode)]


def _chosen_mode(state: CombatState, modes: list[dict], card: Card) -> int:
    """Which mode does the pilot take?

    INSTRUMENT SURFACE, same convention as `_worst_card`: every modal
    measurement rides this choice, so a policy replaces ONE function rather
    than N call sites.

    Switch OFF (the shipped default): the fixed index this seam was staged
    with, byte for byte. Switch ON (EB-118 2C, under R191's own
    POLICY_VERSION window): `policy.choose_mode` -- argmax of the pilot's
    existing per-op play valuations over the live board, minus the HP an
    overdrawing spend would cost, ties to the lowest index.

    The two do not meet at a seam: index 0 is what that tie-break returns
    when the modes score the same, so the staged fixed index is the
    DEGENERATE CASE of the policy rather than a rule surviving beside it.
    Turning the switch on is the POLICY_VERSION event -- every tier0.5 number
    taken with a modal card in the pool renumbers -- which is why the flip is
    a landing act and not an edit here.

    `tier0.pilot.policy._active_effects` calls this same function for its
    forecast, so the pilot's read of a modal card and the mode that actually
    resolves cannot disagree.

    EB-182: the choice is made over the OFFERED modes only, so the pilot, the
    falsifier and a replay all inherit per-option playability from this one
    seam without knowing the rule. On a board where every mode is offered the
    filter is the identity and the chooser sees the list it always saw --
    which is what keeps an unpriced fixture byte-identical.
    """
    offered = offered_modes(state, modes)
    if not offered:
        # `combat.card_playable` refuses a card whose TOP-LEVEL `choose_one`
        # has no affordable mode, so the only way here is a modal nested
        # inside a conditional branch -- a shape no sheet uses and one the
        # cost line cannot see. Offer everything rather than resolving
        # nothing: the paying ops still refuse at resolution, which is the
        # loud half of the same rule.
        offered = list(range(len(modes)))
    # `EB-746`, FURINA'S STAGE, AND FIRST. The Stage's Spend is a choice on
    # play, and a pilot with no opinion about it takes index 0 forever -- a
    # Furina who never spends, which is a different character from the one
    # the seats play. `furina_stage.spend_mode_index` asks the Stage's decider
    # (`policy.FurinaStageDecider.spend_mode`); it answers None on every board
    # the rule does not reach, including every other character's, so nothing
    # below it moves and `POLICY_VERSION` is untouched.
    stage_pick = furina_stage.spend_mode_index(state, modes)
    if stage_pick is not None and stage_pick in offered:
        return stage_pick
    pol = _mode_chooser()
    if pol is None:
        return offered[0]
    return offered[pol.choose_mode(state, [modes[i] for i in offered], card)]


def _op_choose_one(state: CombatState, fx: dict, card: Card) -> None:
    modes = fx[MODES_KEY]
    index = _chosen_mode(state, modes, card)
    mode = modes[index]
    # Parity + telemetry: the C# side records the same event name and the
    # same three fields (klee-mod/KleeCode/Cards/ModalChoice.cs), so a mode
    # taken in either engine reads the same. Generic like the `conditional`
    # emit -- the label is the mode's printed text, so a take-rate can be
    # read per card, per mode, or both.
    state.emit("mode_chosen", card=card.id, index=index,
               label=mode.get("label"))
    _resolve_effects(state, mode.get("effects", []), card)


# The predicate vocabulary, as data. `_predicate` below stays an if-chain --
# each branch carries the ruling that put it there, and that prose is worth
# more than a dispatch table -- but a chain cannot be ENUMERATED, and the
# loader needs to enumerate it: a misspelled `if:` on a sheet used to load
# fine and raise the first time the card was played, which for a rare card
# means in front of a player rather than in a test.
#
# Kept honest by test_content_boundaries.py, which parses the chain and
# asserts these two collections match it exactly in both directions. Adding a
# predicate without listing it here fails; listing one that does not exist
# fails too.
PREDICATE_NAMES = frozenset({
    "this_cost_zero",
    "has_spark",
    "target_has_nonpyro_aura",
    "target_has_aura",
    # THE KOKOMI OVERHAUL, DRAFT 6. Undertow's "if the enemy has
    # a debuff". A LIVE read and not a snapshot, unlike its two aura siblings
    # above: the card that prints it applies nothing before the branch, and
    # what it is asking about is the board as the hit lands.
    "target_has_debuff",
    "reaction_triggered_by_this",
    "reaction_triggered_this_turn",
    "killed_target",
    "killed_target_fatal",
    "drew_skill_this_card",
    "card_exhausted_this_turn",
    "hp_lost_this_turn",
    # Grass Ring of Sanctification (2026-09-23): HP lost since the end of the
    # player's previous turn, the enemy turn included.
    "hp_lost_since_last_turn",
    "enemy_intends_attack",
    # EB-118. Ownership is a yes/no on the sheet, so it is a name, not a
    # count prefix; the COUNTS are reachable as amounts.
    "exhaust_selection_has_companion",
    "exhaust_selection_has_personal",
    # The Klee overhaul's two per-turn reads (C.KLEE_OVERHAUL).
    # Registered so the slice's rows load and validate; the chain REFUSES them
    # for the same reason the arm's ops refuse, and for the same one sentence:
    # slice one is C# first and the sim is not brought up.
    "bomb_went_off_this_turn",
    "bomb_reacted_this_turn",
    # R244's third, on the same gate and for the same reason: Coven Errand's
    # "if you played a Companion card this turn" (Hexerei until R276).
    # Reachable from a `conditional`
    # like its two neighbours AND from `plant_bomb`'s `wide_if:`, which is one
    # vocabulary read at two doors rather than two vocabularies.
    "companion_played_this_turn",
    # R276's pool expansion, on the same gate: "if no Bomb went off this
    # turn" (rule 7's first counter, read the other way round). No row prints
    # it since Sit Tight moved its check to the end of the turn (2026-09-23).
    "no_bomb_went_off_this_turn",
    # The Kokomi overhaul's own per-turn read (
    # C.KOKOMI_OVERHAUL): Sango Isshin's "if the Bake-Kurage carried out a
    # Plan this turn". Unlike the two above this one IS answered -- draft 6
    # runs in both engines.
    "plan_carried_out_this_turn",
    # THE SAME ARM'S SECOND (`EB-711`, pool pass seven -- the row that
    # printed it was withdrawn 2026-09-08 and the predicate stays): "if the
    # Bake-Kurage is holding a Plan". The QUEUE, read
    # live at the moment the card resolves -- the same object
    # `_runtime_count`'s `plans_held` measures, and NOT the morning's depth,
    # for the reason `KokomiPlan.PlansHeld` states: a Plan written earlier
    # this turn is held, a Dusk entry is held until it resolves, and a queue
    # the morning drained is not.
    "plan_held",
    # THE FURINA RULES PASS (2026-10-01), Opening Number: "If this is the
    # first card you played this turn".
    "first_card_this_turn",
    # THE POOL TO 75 (2026-10-09): Against the Tide's "within 5 HP of your
    # Drain line" and Clean Slate's "no drained HP left".
    "stage_near_line",
    "stage_none_drained",
    # VARKA, THE OATH REWORK (`varka_oath.PREDICATES`): "if you have a
    # current element", "if you played a Knight this turn", "if it Swirls".
    # False for anyone who is not Varka and with the switch off.
    "has_current_element",
    "knight_played_this_turn",
    "swirled_by_this",
    # THE EXPANSION (2026-10-01): Amber: Sharpshooter, Shifting Gale.
    "target_has_pyro",
    "element_changed_this_turn",
})

# Parameterised predicates: prefix + an argument the branch parses itself.
# `target_has_power_` takes a power name (unbounded by design -- the next card
# that reads a power needs no new predicate); the rest take an integer.
PREDICATE_PREFIXES = frozenset({
    "target_has_power_",
    "self_has_power_",
    "exhaust_pile_at_least_",
    "fanfare_at_least_",
    # EB-118. `_has_type_` takes a card TYPE (a closed vocabulary, validated
    # below); the other two take an integer like their neighbours.
    "exhaust_selection_has_type_",
    "exhaust_selection_cost_at_least_",
    "exhaust_selection_size_at_least_",
    # THE MONDSTADT COMPANION OVERHAUL (C.COMPANION_OVERHAUL).
    # An HP fraction, parameterised on the percentage for the same reason the
    # meter bars are: the threshold is a printed balance number (Noelle's
    # "below half HP", Bennett's "above 70% HP"), so moving one is a card edit
    # and never an engine edit.
    "hp_pct_below_",
    "hp_pct_above_",
    # The same arm's second wave. Razor's Claw and Thunder: "If this is the
    # third Attack you played this turn". Parameterised on the ordinal for the
    # same reason as its neighbours -- the number is the card's, not the
    # engine's.
    "nth_attack_this_turn_",
})

# The card types `exhaust_selection_has_type_` may name. Closed on purpose:
# a typo'd `..._has_type_attacks` would otherwise load fine and read False
# forever, which is the silent-scaling failure the vocabulary check exists
# to stop.
CARD_TYPES = frozenset({"attack", "skill", "power"})


def is_known_predicate(name: str) -> bool:
    """Would `_predicate` recognise this name? Pure, state-free, load-safe."""
    if name in PREDICATE_NAMES:
        return True
    for prefix in PREDICATE_PREFIXES:
        if not name.startswith(prefix):
            continue
        arg = name[len(prefix):]
        if not arg:
            return False
        if prefix in ("target_has_power_", "self_has_power_"):
            return True
        if prefix == "exhaust_selection_has_type_":
            return arg in CARD_TYPES
        # The integer forms must actually carry an integer. A typo'd
        # `fanfare_at_least_ten` would otherwise pass a name-only check and
        # raise from int() mid-combat -- the very failure being moved earlier.
        return arg.isdigit()
    return False


# EB-135. The `_runtime_count` vocabulary, registered the way the predicate
# vocabulary above is and for the identical reason. `if:` was load-checked and
# `amount_formula.count:` was not -- the ONE grammar the check exists for that
# it did not cover -- so a typo'd count loaded clean and raised
# `unknown runtime count` the first time the card RESOLVED, which is verbatim
# the failure `_validate_effect_vocabulary`'s docstring says it was written to
# end. For a Rare that means in front of a player rather than in a test, and on
# the co-op seat there is no sim backstop at all.
#
# Data mirroring code, so it is derived from `_runtime_count`'s own if-chain
# and compared in BOTH directions by
# `tier0/tests/test_content_boundaries.py` -- the same anti-rot pin
# `PREDICATE_NAMES` carries. A token the chain resolves but this set omits
# would make the validator reject valid content; a token here the chain
# ignores documents a spelling nothing reads.
RUNTIME_COUNT_NAMES = frozenset({
    # CURRENT-KIT USE ONLY (R276) -- Fireworks Finale's "for each Spark spent".
    "sparks_spent",
    # FURINA'S STAGE. Registered here as well as resolved in `_runtime_count`
    # for this registry's own reason: the loader validates every count token
    # at LOAD off this set, so a token only the resolver knows is a card that
    # raises the first time it is played.
    "stage_spent",
    # THE POOL TO 75 (2026-10-09).
    "stage_drains", "stage_half_drained", "stage_repays_turn",
    "stage_repaid",
    "exhaust_pile",
    "player_block",
    "attacks_in_hand",
    "strike_cards",
    "player_damage_events",
    "attacks_played_this_turn",
    "skills_in_hand",
    "other_cards_in_hand",
    "discards_this_turn",
    "exhausts_this_turn",
    "cards_drawn_this_combat",
    "enemy_poison_total",
    "X",
    "exhausted_this_card",
    "hand_size",
    "discards_this_card",
    "block_gained_this_card",
    # CURRENT-KIT USE ONLY (R213 B) -- the INAZUMA companion overhaul's two.
    # Registered here as well as resolved in `_runtime_count`, because the
    # loader validates every count token at LOAD off this set and a row whose
    # token is only in the resolver is a card that raises the first time it is
    # played (EB-135, the defect this registry exists for).
    "companions_played_this_combat",
    "swirls_this_turn",
    # CURRENT-KIT USE ONLY (R250) -- the Kokomi overhaul's Chain of Command,
    # the now-line twin of the Plan clause's `damage_per_companion_last_turn`.
    "companions_played_this_turn",
    # CURRENT-KIT USE ONLY -- the Kokomi overhaul's tempo shelf, Tide Chart's
    # "for each Plan the Bake-Kurage holds". Registered here as well as
    # resolved in `_runtime_count` for this registry's own reason: the loader
    # validates every count token at LOAD off this set, so a token only the
    # resolver knows is a card that raises the first time it is played.
    "plans_held",
    # CURRENT-KIT USE ONLY (`EB-492`) -- Well Laid's "for each Plan the
    # Bake-Kurage carried out this morning". Registered here as well as
    # resolved in `_runtime_count` for this registry's own reason: the loader
    # validates every count token at LOAD off this set.
    # CURRENT-KIT USE ONLY (R276) -- Well Laid's "for each debuff on the
    # enemy". Same registry reason as the two above.
    "debuffs_on_target",
    # CURRENT-KIT USE ONLY (the Casket pass, 2026-09-28) -- Feint's and Sango
    # Isshin's carry-outs this turn, and Driftglass's and Depths' Judgment's
    # Casket. Same registry reason as the rows above.
    "plans_carried_out_this_turn",
    "casket_count",
    # CURRENT-KIT USE ONLY (pool completion, 2026-10-01) -- Shoal of Spears'
    # Plans written this turn. Same registry reason.
    "plans_written_this_turn",
    # CURRENT-KIT USE ONLY (the Kokomi expansion, batch one) -- Weight of the
    # Plan's "Energy paid for the Plans waiting". Same registry reason.
    "plan_energy_waiting",
    # CURRENT-KIT USE ONLY (R213 B) -- the drain op's count. Same
    # reason as the two above: the loader validates every count token at LOAD
    # off this set.
    "fanfare_drained",
    # VARKA, THE OATH REWORK (`varka_oath.COUNTS`). `attacks_played_this_turn`
    # (Lisa: Infinite Circuit) is the shared counter registered above.
    "current_oath",
    "oath_elements",
    # THE EXPANSION (2026-10-01): West Wind Shield, Tidal Bulwark, Charge of
    # the Knights (`varka_oath.COUNTS`).
    "enemies_with_aura",
    "hydro_oath",
    "knights_played_this_combat",
    # VARKA DEFENCE (2026-10-01): Gale Mantle (`varka_oath.COUNTS`).
    "half_total_oath",
    # AoE trim, 2026-10-03: Bombs Away!'s "for each enemy with a Bomb".
    "enemies_with_bomb",
})

# The one prefix family, exactly as `PREDICATE_PREFIXES` carries its own.
# The legal keys are READ OFF `exhaust_selection_counts` rather than listed:
# that function is already the single definition its three consumers share,
# and a second hand-written copy here is precisely the drift this registry
# exists to prevent.
RUNTIME_COUNT_PREFIXES = frozenset({EXHAUST_SELECTION_PREFIX})


def is_known_count(token: str) -> bool:
    """Would `_runtime_count` resolve this token? Pure, state-free, load-safe.

    The mirror of `is_known_predicate`, and the same contract: no
    `CombatState`, no side effects, safe to call from the loader.
    """
    if not isinstance(token, str):
        return False
    if token in RUNTIME_COUNT_NAMES:
        return True
    if token.startswith(EXHAUST_SELECTION_PREFIX):
        key = token[len(EXHAUST_SELECTION_PREFIX):]
        return key in exhaust_selection_counts([])
    return False


# TWO GRAMMARS WEAR THE SAME KEY, and a load check that did not know it would
# refuse shipped content. `amount_formula:` is the COUNT grammar
# (`_calc_amount`, `{base, per, count}`) on damage / block / energy and on any
# dict `times_formula`, but on `apply_power` it is the POWER-READING grammar
# (`_power_amount_formula`, `{target_power: <name>}`) — Dominate and
# MoltenFist are the two users, both in the reference Ironclad pool.
POWER_FORMULA_OPS = frozenset({"apply_power"})

# The ops that read `amount: "all"` THEMSELVES, before `_amount` ever sees it.
# `_op_exhaust_from` resolves it as the eligible pool size (the whole-hand
# shape; ic_fiend_fire and ic_second_wind print it), and `_op_spend_spark`
# resolves it as the whole bank -- the X price, "spend all your Sparks", which
# the round-11 pool pass's Stoke the Fuse is the first and only row to print.
# Anywhere else "all" is a typo that would reach `_amount` and raise.
AMOUNT_ALL_OPS = frozenset({"exhaust_from", "spend_spark"})


def is_known_amount(val) -> bool:
    """Would `_amount` resolve this amount? Pure, state-free, load-safe.

    `_amount` accepts four spellings and the last of them is the whole count
    vocabulary above -- `amount: hand_size` is Calculated Gamble's shape --
    so a typo'd string amount fails at exactly the same moment and for
    exactly the same reason a typo'd `count:` does. Same door, same guard.
    """
    if isinstance(val, bool):
        return False
    if isinstance(val, int):
        return True
    if not isinstance(val, str):
        return False
    if val == "X":
        return True
    if val.startswith("X_plus_"):
        return val[len("X_plus_"):].isdigit()
    if val.startswith("-"):
        # Malaise's sign-flip: one number spent twice with opposite signs.
        return bool(val[1:]) and is_known_amount(val[1:])
    return is_known_count(val)


def _predicate(state: CombatState, name: str) -> bool:
    if name == "this_cost_zero":
        return state.current_card_cost == 0
    if name == "has_spark":
        return state.player.sparks > 0
    if name == "target_has_nonpyro_aura":
        # Snapshotted at card start — the card's own first hit may consume
        # the aura via reaction, which is exactly what the bonus rewards.
        return state.target_had_offelement_aura
    if name == "target_has_debuff":
        # THE KOKOMI OVERHAUL, DRAFT 6. Undertow's branch. The
        # mod asks the game's own `PowerType.Debuff` classification
        # (`KokomiOverhaulKit.HasDebuff`); tier0's `powers` dict carries no
        # type beside the count, so `kokomi_plan.ENEMY_DEBUFFS` is that
        # classification written out -- and what it can and cannot see is
        # documented there rather than here, so there is one list.
        #
        # READ OFF THE BOUND AIM, like every other target predicate in this
        # function: "the enemy" is the creature this play is aimed at, decided
        # before any op ran (R210).
        return kokomi_plan.has_debuff(_default_target(state))
    if name == "target_has_aura":
        # The any-aura sibling (R189's Option C2 for `elemental_ecstasy`).
        # ANY element counts, INCLUDING the player's own: LAW says no
        # character card applies an off-element aura, so a Pyro character
        # gated on `target_has_nonpyro_aura` can never turn her own branch
        # on, which is the whole defect C2 repairs.
        #
        # Snapshotted at card start for the SAME reason its off-element
        # sibling is, not because today's only user needs it: the one card
        # printing this consumes no aura before the branch, but an attack
        # that printed it would, and the two names must not disagree about
        # when they are read.
        return state.target_had_aura
    if name == "reaction_triggered_by_this":
        return state.reactions_this_card > 0
    if name == "reaction_triggered_this_turn":
        # Chevreuse Vanguard's Valor. RULED: ANY reaction counts, not
        # Overload-only -- must never be a dead draw off-Pyro/Electro.
        return state.reactions_this_turn > 0
    if name == "bomb_went_off_this_turn" or name == "bomb_reacted_this_turn":
        # THE KLEE OVERHAUL'S TWO PER-TURN READS (
        # C.KLEE_OVERHAUL), and they are rule 7's two counters read off the
        # arm's ledger -- `KleeOverhaulLedger.SetOffThisTurn > 0` for Run Away!
        # and `.ReactedThisTurn > 0` for Sizzle and Perfect Timing, which is
        # the same pair of expressions the emitter writes into those three
        # cards (`gen_klee_cards.PREDICATE_CS`).
        #
        # NEITHER IS A SYNONYM FOR `reaction_triggered_this_turn`, which counts
        # every reaction rather than a BOMB's -- that is the whole reason the
        # arm carries its own counter instead of reading the engine's.
        #
        # REFUSED with the flag off or on a seat that is not Klee, for the
        # reason the arm's ops refuse there: the rows are unreachable, so a
        # False would be a game this engine never played rather than an answer.
        if not klee_overhaul.live(state):
            raise NotImplementedError(
                f"predicate {name!r} belongs to the KLEE_OVERHAUL arm. It is "
                "answered only with Klee in the seat "
                "-- the mod answers it off `KleeOverhaulLedger` behind "
                "`-p:PrototypeCards=true -p:KleeOverhaul=true`.")
        return (state.ko_set_off_this_turn > 0
                if name == "bomb_went_off_this_turn"
                else state.ko_reacted_this_turn > 0)
    if name == "companion_played_this_turn":
        # COVEN ERRAND's read (R244), on the same gate its two neighbours take
        # and for the same reason: the row is unreachable off the arm, so a
        # False would be a game this engine never played rather than an answer.
        # The counter is the arm's ledger, written at the one site such a
        # play is noticed -- `klee_overhaul.note_companion_played`, which is what
        # `companion_hexerei.note_card_played` calls once it has asked the
        # mark's one question.
        if not klee_overhaul.live(state):
            raise NotImplementedError(
                "predicate 'companion_played_this_turn' belongs to the "
                "KLEE_OVERHAUL arm. It is answered only with "
                "Klee in the seat -- the mod answers "
                "it off `KleeOverhaulLedger` behind `-p:PrototypeCards=true`.")
        return klee_overhaul.played_companion_this_turn(state)
    if name == "no_bomb_went_off_this_turn":
        # R276's Sit Tight printed it at play time; since 2026-09-23 the card
        # pays at the end of the turn (`klee_overhaul.sit_tight_turn_end`) and
        # no row prints this. Kept as vocabulary, on its neighbours' gate.
        if not klee_overhaul.live(state):
            raise NotImplementedError(
                f"predicate {name!r} belongs to the KLEE_OVERHAUL arm. It is "
                "answered only with Klee in the "
                "seat -- the mod answers it off `KleeOverhaulLedger` behind "
                "`-p:PrototypeCards=true`.")
        return state.ko_set_off_this_turn == 0
    if name == "plan_carried_out_this_turn":
        # SANGO ISSHIN's condition (C.KOKOMI_OVERHAUL). Written
        # at the ONE place a Plan is carried out (`kokomi_plan._resolve_entry`)
        # so the morning queue, Change of Plans' early resolution and The Moon
        # Overlooks the Waters' play-time one all count -- they all carry a
        # Plan out, which is the phrase the card prints.
        return state.kk_plan_carried_out_this_turn
    if name == "plan_held":
        # HER BASIC DEFEND's condition (`EB-711`). The QUEUE, and
        # the same one `_runtime_count`'s `plans_held` counts -- one definition
        # of "holding a Plan" per engine, so the card's rider and Breakwater's
        # per-Plan clause cannot disagree. Read LIVE, which is what makes the
        # card ask its question by ordering: written-then-Defend holds one and
        # Defend-then-written holds none.
        return bool(state.kk_plan_queue)
    if name == "killed_target":
        return state.kills_this_card > 0
    if name == "drew_skill_this_card":
        # EscapePlan: its own draw produced a Skill. Cleared at card start,
        # so "drew nothing" (empty piles, full hand) is False rather than
        # whatever the previous card happened to draw -- which is the
        # source's `FirstOrDefault() != null && .Type == Skill`.
        return state.last_drawn_type == "skill"
    if name == "killed_target_fatal":
        # Feed. The base game's Fatal gate ignores deaths whose owner says
        # they should not trigger it (summoned adds) -- see
        # Enemy.counts_for_fatal. Distinct from killed_target so Klee's and
        # Furina's existing kill riders keep their exact meaning.
        return state.fatal_kills_this_card > 0
    if name.startswith("self_has_power_"):
        # Tracking applies 1 more if the owner ALREADY has it and 2 if not --
        # a card that reads its own power before applying it. The mirror of
        # target_has_power_, and parameterised for the same reason: the next
        # card that reads one of the player's powers needs no new predicate.
        return state.player.powers.get(name[len("self_has_power_"):], 0) > 0
    if name.startswith("target_has_power_"):
        # Dismantle: the hit-count branch reads whether the default-aim enemy
        # carries a named power AT PLAY TIME. The conditional resolves the
        # predicate before any damage op inside its branch, so this is a clean
        # pre-hit read. Parameterised on the power name (target_has_power_
        # vulnerable today) so the next such card needs no new predicate.
        tgt = _default_target(state)
        power = name[len("target_has_power_"):]
        return bool(tgt and tgt.powers.get(power, 0) > 0)
    if name.startswith("exhaust_pile_at_least_"):
        # PactsEnd: the AoE fires only when the exhaust pile already holds at
        # least N cards; otherwise the card resolves as nothing.
        n = int(name.rsplit("_", 1)[1])
        return len(state.player.exhaust_pile) >= n
    # EB-118. These read the CURRENT selection (the exhaust_from earlier in
    # this same card), not the pile: the pile is everything ever rotated off
    # the line, this is the one choice just made. A card with no exhaust_from
    # before the conditional reads an empty selection and every branch here
    # is False, which is the honest answer rather than an error -- the same
    # reading `drew_skill_this_card` gives a card that drew nothing.
    if name.startswith("exhaust_selection_cost_at_least_"):
        counts = exhaust_selection_counts(state.exhaust_selection)
        return counts["cost"] >= int(name.rsplit("_", 1)[1])
    if name.startswith("exhaust_selection_size_at_least_"):
        counts = exhaust_selection_counts(state.exhaust_selection)
        return counts["size"] >= int(name.rsplit("_", 1)[1])
    if name.startswith("exhaust_selection_has_type_"):
        want = name[len("exhaust_selection_has_type_"):]
        return any(d["type"] == want for d in state.exhaust_selection)
    if name == "exhaust_selection_has_companion":
        return any(d["companion"] for d in state.exhaust_selection)
    if name == "exhaust_selection_has_personal":
        return any(not d["companion"] for d in state.exhaust_selection)
    if name == "card_exhausted_this_turn":
        return state.cards_exhausted_this_turn > 0
    if name == "stage_near_line":
        return furina_stage.near_line(state.player)
    if name == "stage_none_drained":
        return furina_stage.none_drained(state.player)
    if name == "hp_lost_this_turn":
        return state.hp_lost_this_turn > 0
    if name == "hp_lost_since_last_turn":
        return state.hp_lost_since_last_turn > 0
    if name == "enemy_intends_attack":
        # Frozen enemies still attack under v1.5 (at -50%), so they count.
        return any(e.current_intent()["kind"] == "attack"
                   and e.sleep_turns == 0
                   for e in state.living_enemies)
    # --- Furina sheet-pass predicates ---
    if name == "first_card_this_turn":
        # Opening Number (the Furina rules pass, 2026-10-01). This engine
        # counts a play BEFORE it resolves (`combat.play_card`, the auto-play
        # path too), so the card asking is the first when the count is 1. The
        # C# twin counts AFTER (`FurinaStageLedger.CardsPlayedThisTurn`), so
        # it asks for 0; both spell "no card before this one".
        return state.cards_played_this_turn == 1
    if name.startswith("fanfare_at_least_"):
        resources.note_fanfare_read(state, "threshold")
        # Clamped for consistency with every other reader. It cannot change
        # an answer today -- every printed threshold is positive, so a
        # negative meter fails either way -- and it is written this way so a
        # future `fanfare_at_least_0` reads as "she has any" rather than as
        # "always true, even mid-Hyperbeam-debt".
        return resources.readable(state.player) >= int(name.rsplit("_", 1)[1])
    if name.startswith("hp_pct_below_"):
        # THE MONDSTADT COMPANION OVERHAUL. Noelle's
        # Breastplate: "If you are below half HP, gain 4 more."
        #
        # CROSS-MULTIPLIED, never divided. `hp / max_hp` is a float here and
        # `CurrentHp / MaxHp` is a decimal in C#, and a card whose branch flips
        # at exactly half would then be at the mercy of two different rounding
        # stories at the one HP value a player notices. `hp * 100 < max * N` is
        # exact in both engines.
        n = int(name.rsplit("_", 1)[1])
        return state.player.hp * 100 < state.player.max_hp * n
    if name.startswith("hp_pct_above_"):
        # Bennett's Fantastic Voyage: "If you are above 70% HP". STRICTLY
        # above, and the sibling above is STRICTLY below, so AT the bar both
        # read False -- which is what the printed words say, and is why these
        # are two predicates rather than one with a flipped sense.
        n = int(name.rsplit("_", 1)[1])
        return state.player.hp * 100 > state.player.max_hp * n
    if name.startswith("nth_attack_this_turn_"):
        # Razor's Claw and Thunder: "If this is the third Attack you played
        # this turn."
        #
        # THE `+ 1` IS THE CARD ASKING THE QUESTION, and it is arithmetic
        # rather than a choice. `state.attacks_played_this_turn` is incremented
        # in `refpowers.after_card_played`, which runs AFTER
        # `effects.resolve_card` -- so while this predicate is being evaluated
        # the counter holds the Attacks played BEFORE this one, and the card
        # asking whether it is the third is itself the third.
        #
        # The C# twin counts at the OTHER end (`CompanionOverhaulLedger` notes
        # the play in `BeforeCardPlayed`, so its number already includes the
        # card) and therefore compares without the `+ 1`. Two spellings, one
        # value, each written down against the other -- and the pin that they
        # agree is `tier0/tests/test_companion_overhaul_hooks.py`.
        n = int(name.rsplit("_", 1)[1])
        return state.attacks_played_this_turn + 1 == n
    if (name == "has_current_element" or name == "knight_played_this_turn"
            or name == "swirled_by_this" or name == "target_has_pyro"
            or name == "element_changed_this_turn"):
        return varka_oath.predicate(state, name)
    raise ValueError(f"unknown predicate {name!r}")


def _op_repeat_this(state: CombatState, fx: dict, card: Card) -> None:
    state.repeat_requested = fx.get("times", 1)     # honored by resolve_card


def _op_grow_damage(state: CombatState, fx: dict, card: Card) -> None:
    """Rampage: permanently raise this card instance's printed damage.

    The card object circulates through the combat piles, so mutating its own
    first damage op preserves growth across redraws; deepcopy-based clones
    inherit the amount they cloned from, matching CardModel clone semantics.
    """
    hit = next((effect for effect in card.effects
                if effect.get("op") == "damage"
                and isinstance(effect.get("amount"), int)), None)
    if hit is None:
        raise ValueError(f"{card.id}: grow_damage has no literal damage op")
    hit["amount"] += fx["amount"]
    state.emit("grow_damage", card=card.id, amount=fx["amount"],
               total=hit["amount"])


def _op_chance_bomb_per_detonation(state: CombatState, fx: dict,
                                   card: Card) -> None:
    # Chained Reactions: per detonation caused by this card so far, a
    # chance to place a fresh bomb on a random enemy.
    n = state.detonations_total - state.detonations_at_card_start
    for _ in range(n):
        if state.rng.random() < fx["chance"] and state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            enemy.bombs.append(Bomb(damage=fx["bomb_damage"],
                                    turn_placed=state.turn))
            state.emit("bomb_placed", target=enemy.name,
                       damage=fx["bomb_damage"])


def _op_copy_companion_in_hand(state: CombatState, fx: dict, card: Card) -> None:
    """Borrowed Brilliance. FLAG-2(i): built from the printed card, for the
    reasons written out above `_op_copy_spotlighted_in_hand`."""
    from tier0.content import loader
    comps = [c for c in state.player.hand if c.is_companion]
    if not comps:
        return
    for _ in range(fx.get("amount", 1)):
        chosen = loader.get_card(state.rng.choice(comps).id)
        if "cost_override" in fx:            # Borrowed Brilliance upgrade
            # THIS COMBAT, not this turn: the mod's twin is
            # `EnergyCost.SetThisCombat(0)` (BorrowedBrilliance.cs), and a
            # token that exists only for this combat cannot tell the two
            # apart today -- writing the scope down is what stops the next
            # reader assuming it inherits FLAG-2(ii)'s turn bound.
            chosen.cost_delta_this_combat = fx["cost_override"] - chosen.cost
        _add_token(state, chosen, "hand")


def _op_replay_next_companion(state: CombatState, fx: dict, card: Card) -> None:
    state.replay_next_companion += fx.get("times", 1)   # reset at turn start


def _op_copy_companions_played(state: CombatState, fx: dict, card: Card) -> None:
    """Best Friends Forever: one copy of each companion played this combat.

    The ledger is ALREADY unique in first-play order -- combat._finish_play
    dedupes on the BASE id when it records (BFF-dedupe, RULED 2026-08-06: an
    upgraded companion is the same pool entry as its base), the same place
    and the same key as C#'s CompanionPlays.Record. So this loop is a plain
    walk: a second dedupe here would either be a no-op or, if it used a
    different key, silently outrank the ruled one.
    """
    from tier0.content import loader
    for cid in state.companions_played:
        token = loader.get_card(cid)
        if "cost_override" in fx:
            token.cost = fx["cost_override"]
        _add_token(state, token, fx.get("zone", "hand"))


def _op_upgrade_in_hand(state: CombatState, fx: dict, card: Card) -> None:
    """Armaments (base: choose 1; upgraded: every upgradable card in hand).

    Eligibility is upgrades.has_upgrade, which already excludes `+` ids and
    the UNAPPLIABLE set -- so a card whose upgrade the sim cannot express is
    visibly skipped rather than pretend-upgraded.
    """
    import copy as _copy
    from tier0.content import upgrades              # late import avoids cycle
    hand = state.player.hand
    idxs = [i for i, c in enumerate(hand) if upgrades.has_upgrade(c.id)]
    if not idxs:
        return
    if fx.get("scope", "chosen") == "chosen":
        idxs = [_best_upgrade_target(hand, idxs)]
    # Replace BY INDEX. Card is a plain dataclass with eq=True, so
    # list.remove matches by value (combat.play_card already relies on
    # that); a remove/append rebuild would silently reorder the hand and
    # perturb every downstream heuristic that reads hand order.
    for i in idxs:
        # Upgrade the LIVE instance rather than reloading a pristine base row.
        # Rampage's accumulated damage, generated-card cost overrides, and
        # clone state are all combat mutations the real CardModel preserves.
        hand[i] = upgrades.apply_upgrade(_copy.deepcopy(hand[i]))
        state.emit("upgrade_in_hand", card=hand[i].id)


def _op_gain_max_hp(state: CombatState, fx: dict, card: Card) -> None:
    """Feed. CreatureCmd.GainMaxHp raises max HP by `amount` AND heals by
    the same amount -- the heal is part of the command, not a second effect.

    CROSS-TIER FLAG: in the real game this is PERMANENT for the run.
    combat.run_fight is single-combat and never persists hp/max_hp, so
    unless tier05 carries the gain between fights, Feed is systematically
    undervalued and the point of the card vanishes.
    """
    p = state.player
    n = _amount(state, fx["amount"])
    p.max_hp += n
    p.hp += n
    # EB-97: the Fanfare ceiling rides LIVE max HP, so Feed raises it MID
    # FIGHT exactly as `FurinaResources.FanfareCap` does -- the one place the
    # two engines used to diverge inside a single combat.
    sync_fanfare_cap_to_max_hp(p)
    state.emit("gain_max_hp", amount=n)


def _op_draw_to_hand_size(state: CombatState, fx: dict, card: Card) -> None:
    """Expertise: draw until the hand holds `amount` cards; never discard
    down to it.

    `Math.Max(0, Cards - Hand.Count)` in the source, which is a subtraction
    and not a loop -- so a hand ALREADY at or above the number draws nothing,
    and this cannot be spelled as draw_while (whose exit condition is what
    was drawn). The hand is counted AFTER the card left it, matching the
    source: Expertise reads `PlayerCombatState.Hand.Cards.Count` from inside
    its own OnPlay, by which point the card is on the play stack.
    """
    want = _amount(state, fx["amount"])
    n = max(0, want - len(state.player.hand))
    if not n:
        return
    state.draw(n)
    state.emit("extra_draw", amount=n)


def _op_strip_block(state: CombatState, fx: dict, card: Card) -> None:
    """Expose: remove ALL of the target's Block (CreatureCmd.LoseBlock with
    the target's own Block as the amount).

    Not damage: it deletes the block outright, so nothing that reads damage
    -- Thorns, reactions, on-hit riders -- fires. Enemies rarely carry block
    in tier0, which makes this look inert; it is not approximated for that
    reason, because whether enemy block matters is a question about the
    ENCOUNTER set, and rounding the card off would answer it by fiat.
    """
    for enemy in _pick_targets(state, fx.get("target", "enemy")):
        if enemy.block:
            state.emit("strip_block", target=enemy.name, amount=enemy.block)
            enemy.block = 0


def _op_chain_attack(state: CombatState, fx: dict, card: Card) -> None:
    """EchoingSlash: a volley that repeats once more per enemy it KILLED.

        attackCount = 1
        while attackCount > 0:
            attackCount--
            results = Damage(HittableEnemies, ...)
            attackCount += results.Count(r => r.WasTargetKilled)

    Two kills in one volley therefore buy two more volleys, not one. Every
    other repeat in the DSL is a fixed count, which is why this is its own op
    rather than a `times` value: the count is not knowable until the damage
    has resolved.

    Bounded by the enemy list -- an enemy dies once and nothing respawns, so
    the kill budget for the whole chain is len(enemies). The guard is a pure
    backstop against an impossible infinite, the same shape draw_while uses.
    """
    inner = {k: v for k, v in fx.items() if k != "op"}
    inner["op"] = "damage"
    pending, guard = 1, len(state.enemies) + 1
    while pending > 0 and guard > 0 and not state.over:
        pending -= 1
        guard -= 1
        before = state.kills_this_card
        _op_damage(state, inner, card)
        pending += state.kills_this_card - before


def _op_extra_card_screen(state: CombatState, fx: dict, card: Card) -> None:
    """The Hunt. Record that this fight earned `amount` extra card reward
    screens; grant nothing.

    THE SEAM IS DELIBERATE ([USER] ruling, 2026-07-27). Strictly the reward
    is not in-combat: the effect fires during the fight, and the extra offer
    appears on the rewards screen afterwards. So combat's whole job is to say
    that it happened. tier05/model.py reads `state.extra_card_screens` after
    a won fight and rolls the screens; a fight LOST after this fires pays
    nothing, because a lost fight shows no rewards screen -- which is the
    base game's behaviour too, and falls out of the run layer's existing
    control flow rather than needing a rule here.

    Nothing else in tier0 may read this counter. It is not a resource, it
    does not decay, and no card should ever branch on it.
    """
    state.extra_card_screens += _amount(state, fx.get("amount", 1))
    state.emit("extra_card_screen", total=state.extra_card_screens)


# EB-118: the exhaust pile as a recall_to_draw SOURCE, not a parallel op
# family. One verb ("put a card back on top of the draw pile"), two piles it
# may reach into; a second op would have duplicated the placement rule, the
# kit exemption and the pilot's choice surface three ways.
RECALL_SOURCES = ("discard", "exhaust")
RECALL_EXHAUST_SOURCE = "exhaust"


def walk_card_effects(card: Card):
    """Every PRINTED effect on a card — the played face's tree AND the Sly
    branch's.

    EB-134. `Card.sly` is its own effect list (`state.py:262`) and
    `_walk_effects` stops at `card.effects`, so a question answered by that
    walk alone is answered about the played face only. For a CAPABILITY
    question — "can this card do X at all" — that is simply wrong: a Sly
    rider is printed text the player can always reach, exactly like a
    conditional branch or a modal mode body, both of which `_walk_effects`
    already descends into.

    Deliberately a SECOND function rather than a change to `_walk_effects`.
    Some callers want the played face and are right to: `_printed_power`
    ranks what a card pays when you PLAY it, and folding a discard-only rider
    into that scalar would mis-rank every Assist card for every chooser. The
    rule is per-question, so the walk is per-question too — which is the same
    discipline `tools/effect_walk.iter_effects_top` states on the sheet side.

    The reserved `{op: sly_autoplay}` marker is filtered out by `sly_riders`:
    it is a card PLAY, not an effect list, and is never dispatched as an op
    (EB-71 / R174).
    """
    yield from _walk_effects(card.effects)
    yield from _walk_effects(sly_riders(card))


def retrieves_from_exhaust(card: Card) -> bool:
    """Does this card itself retrieve from the exhaust pile? (EB-118 §6.4
    constraint 3.)

    A card-shape property, read off the printed effect tree rather than a
    hand-set flag, so a future sheet row cannot arm the capability and forget
    to declare it. The C# twin is the IExhaustRetriever marker interface,
    which the generator stamps from this same shape.

    EB-134: the walk is `walk_card_effects`, so the Sly branch counts. It
    used to be `_walk_effects(card.effects)`, and that ONE blind spot
    disarmed four checks at once, because everything downstream rides this
    single predicate — `loader._validate_recall_shape` skipped constraints 1
    and 2 (Uncommon-or-Rare, self-exhausting) at LOAD, `recall_exhaust_pool`
    offered a sly retriever as fodder for itself and so broke the cycle
    exclusion the pile's one-way rotation rests on, and
    `tools/lint_recall_exhaust` swept straight past it. A capability hidden
    in a `sly:` list is still a capability.
    """
    return any(fx.get("op") == "recall_to_draw"
               and fx.get("from") == RECALL_EXHAUST_SOURCE
               for fx in walk_card_effects(card))


def recall_exhaust_pool(state: CombatState, card: Card) -> list[Card]:
    """The eligible targets in the exhaust pile (EB-118 §6.4, constraints
    3 / 6). Enforced HERE rather than by card-author discipline, and shared
    by the op and the closure sweep so the two cannot drift.

    * kit cards are never fodder and never loot (the v1.9 invariant every
      other pile pool rides);
    * a card that itself retrieves from Exhaust is ineligible, INCLUDING
      this one -- that exclusion is what keeps the pile from closing into a
      cycle, and the `is not card` clause covers the route where the
      retrieval card has already been routed to the pile;
    * Status and Curse are ineligible (`is_junk`, the C11 rotation-law
      predicate). Ordinary personal and Companion cards stay eligible.
    """
    return [c for c in state.player.exhaust_pile
            if not c.kit_card
            and not c.is_junk
            and not retrieves_from_exhaust(c)
            and c is not card]


def _op_recall_to_draw(state: CombatState, fx: dict, card: Card) -> None:
    """Headbutt: put a chosen card from the discard pile on TOP of the draw
    pile. Index 0 IS the top -- state.draw pops index 0 and
    combat.surface_innate prepends. No-op on an empty source pile.

    `from: exhaust` (EB-118) reads the exhaust pile instead, through
    `recall_exhaust_pool`, and the returned card GAINS Exhaust for the rest
    of combat (constraint 5): it is on loan for one more use, then rotates
    again and grants Charge again under normal law -- the funnel in
    refpowers.after_card_exhausted sees a personal card and pays it, C11
    included. Removing it from the pile temporarily weakens only pile
    READERS; banked Charge does not fall, because Charge is never spent
    (LAW). Destination is the draw pile in both branches -- never the hand
    (constraint 4).
    """
    p = state.player
    src = fx.get("from", "discard")
    if src not in RECALL_SOURCES:
        raise ValueError(f"unknown recall_to_draw source {src!r}")
    pos = fx.get("position", "top")
    if pos != "top":
        raise ValueError(f"unknown recall_to_draw position {pos!r}")
    from_exhaust = src == RECALL_EXHAUST_SOURCE
    pile = p.exhaust_pile if from_exhaust else p.discard_pile
    for _ in range(_amount(state, fx.get("amount", 1))):
        # THE DISCARD BRANCH IS UNFILTERED ON PURPOSE (EB-69 / D3, R198,
        # 2026-08-23). It is the raw pile: no `c is not card` clause, no kit
        # filter, no junk filter -- so a card discarded by an effect can have
        # its own Sly rider recall ITSELF. `what_the_tokoyo_returns` is the
        # card that reads this, and [USER] ruled the behaviour DELIBERATE
        # rather than an accident to be excluded. It is a FALLBACK, not a
        # rule: `_best_card` prefers a real Attack in the pile. The asymmetry
        # with the exhaust branch below -- which DOES exclude self, kit, junk
        # and other retrievers, because EB-118 §6.4 required it -- is now
        # intentional on both sides. Tidying the two into one filtered path
        # breaks a shipped card; pinned by
        # tier0/tests/test_eb69_tokoyo_returns_selfrecall.py.
        pool = recall_exhaust_pool(state, card) if from_exhaust else pile
        if not pool:
            return
        pick = _best_card(pool)
        remove_instance(pile, pick)
        if from_exhaust:
            # Rest-of-combat, per INSTANCE: the sheet row is untouched and a
            # twin of the same card elsewhere in the deck is unaffected.
            pick.exhaust = True
        p.draw_pile.insert(0, pick)
        state.emit("recall_to_draw", card=pick.id, source=src)


def _op_transform_in_hand(state: CombatState, fx: dict, card: Card) -> None:
    """PrimalForce: transform every Attack in hand into GiantRock.

    CardCmd.Transform replaces the original AT ITS ORIGINAL PILE INDEX, so
    this replaces in place (same ordering argument as upgrade_in_hand).
    The `+` suffix convention in loader.get_card carries the upgraded
    variant, so the upgrade is a plain `into` string replace.

    The base game also gates on Card.IsTransformable. No tier0 flag exists
    for it: whether any Ironclad Attack is untransformable must be verified
    against the sheet, and adding a flag nothing sets would be an assumption
    wearing the costume of a check. Kit cards ARE excluded -- the v1.9
    invariant is that the Burst never leaves the kit.
    """
    from tier0.content import loader                # late import avoids cycle
    hand = state.player.hand
    filt = fx.get("filter")
    for i, c in enumerate(hand):
        if c.kit_card or (filt and c.type != filt):
            continue
        hand[i] = loader.get_card(fx["into"])
        state.emit("transform", was=c.id, into=hand[i].id)


# Backstop for nested free plays. The seen_states guard in
# combat._player_turn only samples BETWEEN pilot plays, so a Havoc chain
# that flips more Havocs is structurally invisible to it. Belongs in
# tier0/constants.py; it lives here because that file is owned by a
# concurrent edit -- move it when the sheet lands.
MAX_FREE_PLAY_DEPTH = 10


def _free_play(state: CombatState, card: Card,
               force_exhaust: bool = False) -> None:
    """Shared driver for the two base-game free plays: autoplay_from_draw
    (Havoc, Cascade) and the on-exhaust autoplay sweep (HowlFromBeyond).

    The actual play MUST go through combat.resolve_free_play, not
    _resolve_effects: every piece of card-play bookkeeping (pile routing,
    cards_played_this_turn, the `play` event, the per-card context block)
    lives in combat.play_card. Resolving effects directly here would let a
    free play silently clobber the OUTER card's killed_target and
    repeat_this state mid-resolution, and that corruption is invisible in
    results -- which is precisely why this is an engine change and not an op.

    CONTRACT with combat.resolve_free_play(state, card, force_exhaust):
      1. no energy deduction, no spark spend, no encore_cost gate;
      2. save and RESTORE the whole per-card context block resolve_card
         sets (current_card_companion, reactions_this_card,
         kills_this_card, fatal_kills_this_card, exhausted_this_card,
         exhaust_selection,
         detonations_at_card_start, repeat_requested,
         target_had_offelement_aura, target_had_aura,
         current_attack_bonus, sparks_at_play,
         current_x, current_card_cost);
      3. current_card_cost = 0 for the free play (this_cost_zero and
         zero_cost_attacks_up both read it), then restore;
      4. route afterwards: force_exhaust -> exhaust; else card.exhaust or
         type == "power" -> exhaust; else discard. The card is NOT in hand,
         so it must not attempt hand.remove;
      5. increment cards_played_this_turn and emit play(cost=0, free=True),
         so MAX_CARDS_PER_TURN can see free plays;
      6. current_x = player.energy when card.cost == "X" (CardCmd.AutoPlay
         sets CapturedXValue from remaining energy).
    """
    from tier0.engine import combat                 # late import avoids cycle
    play = getattr(combat, "resolve_free_play", None)
    if play is None:
        raise NotImplementedError(
            "UNIMPLEMENTED: combat.resolve_free_play(state, card, "
            "force_exhaust) does not exist. Havoc, Cascade and "
            "HowlFromBeyond CANNOT be scored without it and must be "
            "excluded from the sheet. Refusing to approximate a free play "
            "by resolving effects inline: that silently corrupts the outer "
            "card's per-card context. See _free_play's contract docstring.")
    if state.free_play_depth >= MAX_FREE_PLAY_DEPTH:
        state.emit("degeneracy", kind="INFINITE", reason="free_play_depth")
        return
    state.free_play_depth += 1
    prev_random = state.force_random_targeting
    state.force_random_targeting = True
    try:
        play(state, card, force_exhaust=force_exhaust)
    finally:
        state.force_random_targeting = prev_random
        state.free_play_depth -= 1


def prevent_damage_exhaust(state: CombatState, incoming: int) -> int:
    """Kokomi's prevention ward (kickoff §2.4): the first time each turn an
    attack would deal unblocked damage, prevent up to the ward's stacks and
    Exhaust a random card from the draw pile — prevention priced in future
    draws. Returns the damage actually prevented.

    The exhaust routes through refpowers.exhaust_card, i.e. THE funnel, so
    the proc itself feeds Charge (getting attacked fuels the finisher —
    the stability identity as mechanic). An empty draw pile reshuffles
    first (ShuffleIfNecessary parity with every other draw-pile read); if
    draw AND discard are both empty the ward cannot pay and does not
    proc — the deck really is her second HP bar, and it can run out.

    Rate limit: once per player-turn-round (prevention_used_this_turn,
    reset with the other per-turn windows). Rare-gating and magnitude live
    on the card row (R16: power in the cards)."""
    p = state.player
    stacks = p.powers.get("prevent_exhaust_ward", 0)
    if (stacks <= 0 or incoming <= 0 or state.prevention_used_this_turn):
        return 0
    if not p.draw_pile:
        state.shuffle_discard_into_draw()
    if not p.draw_pile:
        return 0                       # fuel exhausted: defenseless
    from tier0.engine import refpowers              # late import (cycle)
    state.prevention_used_this_turn = True
    victim = p.draw_pile.pop(state.rng.randrange(len(p.draw_pile)))
    refpowers.exhaust_card(state, victim)
    prevented = min(incoming, stacks)
    state.emit("prevent_exhaust", amount=prevented, card=victim.id)
    return prevented


def _op_autoplay_from_draw(state: CombatState, fx: dict, card: Card) -> None:
    """Havoc (1, forceExhaust) and Cascade (X, no forceExhaust).

    ORDERING, observable and deliberate: the dll selects ALL n cards first
    (moving each to the Play pile inside the selection loop) and only THEN
    plays them in order. Cascade for 3 therefore takes the top 3 up front
    and cannot re-select a card it already queued. ShuffleIfNecessary runs
    before EACH selection, not once.
    """
    p = state.player
    pos = fx.get("position", "top")
    if pos != "top":
        raise ValueError(f"unknown autoplay_from_draw position {pos!r}")
    queued = []
    for _ in range(_amount(state, fx.get("amount", 1))):
        if not p.draw_pile:
            state.shuffle_discard_into_draw()       # ShuffleIfNecessary
        if not p.draw_pile:
            break                                   # deck genuinely empty
        queued.append(p.draw_pile.pop(0))
    for queued_card in queued:
        if state.over:
            break
        _free_play(state, queued_card,
                   force_exhaust=fx.get("force_exhaust", False))


def _op_autoplay_from_exhaust(state: CombatState, fx: dict, card: Card) -> None:
    """KnifeTrap: auto-play EVERY tagged card in the exhaust pile.

    The list is snapshotted before the first play, exactly as the source
    does (`.ToList()` before the foreach) -- a card this effect exhausts
    while resolving must not be replayed by the same effect, which is a live
    hazard because the tokens it plays typically exhaust themselves back
    into the pile it is iterating.

    `upgrade_first` is the card's IsUpgraded branch: each is upgraded before
    it is played, not after.
    """
    p = state.player
    tag = fx.get("tag")
    victims = [c for c in p.exhaust_pile if not tag or tag in c.tags]
    if not victims:
        return
    from tier0.content import loader, upgrades
    for victim in victims:
        if state.over or not p.alive:
            break
        if not remove_instance(p.exhaust_pile, victim):
            continue
        if fx.get("upgrade_first"):
            # Same boundary as _op_add_card: only missing-entry shapes degrade.
            try:
                victim = loader.get_card(victim.id + upgrades.SUFFIX)
            except (KeyError, ValueError):
                state.emit("UNIMPLEMENTED", op="autoplay_from_exhaust",
                           card=victim.id,
                           reason="no upgrade entry; played unupgraded")
        state.emit("autoplay_from_exhaust", card=victim.id)
        _free_play(state, victim, force_exhaust=False)


def _op_remember_card(state: CombatState, fx: dict, card: Card) -> None:
    """Nightmare: choose a card in hand now; the POWER copies it later.

    The chosen card is stored as an ID rather than as the object, matching
    `SetSelectedCard`, which clones the card and clears its affliction before
    keeping it -- what is remembered is the CARD, not that instance's
    accumulated combat state.
    """
    pool = [c for c in state.player.hand if not c.kit_card]
    if not pool:
        return
    pick = _best_card(pool)
    state.player.power_payloads[fx["power"]] = pick.id
    state.emit("remembered_card", card=pick.id, power=fx["power"])


# ---------------------------------------------------------------------------
# THE KLEE OVERHAUL'S OPS (C.KLEE_OVERHAUL).
#
# THE ARM IS BUILT NOW (`EB-312`). These eight used to RAISE, on the slice
# packet's sec.5 ("All of it goes behind the prototype switch, C# first... The
# Python sim is not brought up for slice one"), and the twin was raised
# deliberately after the C# had proved the rules through five prototype rounds:
# `engine/klee_overhaul.py` is that build, and it mirrors
# `KleeCode/Powers/Prototype/ProtoBombPower.cs` and its neighbours clause for
# clause.
#
# WHAT STILL REFUSES: every verb, WITH THE FLAG OFF or on a seat that is not
# Klee. The rows are unreachable there (`loader._card_prototype` refuses a
# `proto_ko_` id with the flag off), so reaching one is a DEFECT and not a
# degradation -- a silent no-op would be the worst possible stand-in, since the
# sim would keep running and keep reporting numbers for a card whose printed
# text never happened.
#
# EVERY ARM BELOW IS ONE CALL INTO `klee_overhaul`, deliberately rather than
# tidily: the rules live in that module, so a card cannot express a variant of
# a rule by being resolved differently here. It is the same discipline
# `gen_klee_cards` keeps on the other side, where every one of these ops emits
# exactly one awaited call into `ProtoBombPower`.
def _op_klee_overhaul_off(state: CombatState, fx: dict, card: Card) -> None:
    raise NotImplementedError(
        f"card {card.id!r}: op {fx['op']!r} belongs to the KLEE_OVERHAUL arm "
        "(slice one, the Bomb). It resolves only with Klee in the seat -- the "
        "mod's `IKleeCharacter` test, mirrored -- so reaching this is a "
        "defect rather than a degradation.")


def _op_set_off(state: CombatState, fx: dict, card: Card) -> None:
    """RULE 2, in its four card-facing spellings (`SetOffAimed`, `SetOffAll`,
    `SetOffRandom`).

    THE ORDER IS HELD HERE, not by the order two rows happen to sit in: the
    Bombs go off first, one at a time, and the card's own damage lands after.
    `damage: 0` -- the sheet's absent key -- is "a Set off with no Attack
    behind it".

    THE CARD'S OWN HIT GOES BACK THROUGH `_op_damage`, which is the whole
    reason this op does not deal it itself: the mod hands the printed number to
    `DamageCmd.Attack(...).FromCard(...)`, the same pipeline any other Attack
    row takes, so Strength, the flat per-card bonus, the Pyro cadence,
    Vulnerable and the enchantment riders all apply exactly as they do to a
    printed `damage` row. A second, smaller copy of that pipeline here is the
    drift the delegation exists to prevent.
    """
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    # ONCE MORE!'s NOTE (`EB-732`), taken HERE and above every branch below:
    # "the last Set off card you played this combat" is a fact about the CARD,
    # not about a charge, so a Set off played into an empty board still counts.
    # C# twin: the same note at the head of `ProtoBombPower.SetOffAimed`,
    # `SetOffAll` and `SetOffRandom`, the three card-facing entry points.
    klee_overhaul.note_set_off_card(state, card)
    # BOOM BADGE (playtest 2026-09-24), spent HERE, once per Set off clause
    # and beside the note above, so every enemy this clause reaches shares the
    # one doubling. C# twin: `BoomBadgePower.Spend` at the head of each
    # card-facing entry point in `ProtoBombPower`.
    badge = klee_overhaul.take_boom_badge(state, card)
    damage = int(fx.get("damage", 0) or 0)
    spec = fx.get("target", "enemy")

    def hit(enemy) -> None:
        if damage <= 0 or not enemy.alive:
            return
        with klee_overhaul.aimed_at(state, enemy):
            _op_damage(state, {"op": "damage", "amount": damage,
                               "target": "enemy"}, card)

    if spec == "all_enemies":
        for enemy in list(state.living_enemies):
            if not enemy.alive:
                continue
            klee_overhaul.set_off(state, enemy, card, badge=badge)
            hit(enemy)
        return

    if spec in ("random_enemy", "random_enemies"):
        # RULE 2's LAST SENTENCE: "For random-target Attacks, per target hit."
        # The roll happens once per hit and each rolled enemy's Bombs go off
        # before that hit lands -- four rolls is four Set offs, not one Set off
        # and four hits. The candidates are re-read each time, so a hit that
        # killed its target cannot be rolled again.
        #
        # `EB-516`, THE AIM (Klee r18, packet sec.4 item 2). The roll is drawn
        # from the enemies CARRYING one of her charges, and falls back to every
        # living enemy only when none does. Tinder Toss and Rapid Fire share
        # one fault and one rule fixes both: a random Set off that lands on a
        # Bomb-less body breaks the arm's only economic loop (a Spark-priced
        # Set off into a bombed body costs nothing net), and the r17 and r18
        # seats named those two rows the least-wanted cards in the pool. The
        # NUMBERS are untouched -- the same rolls, the same hits, a narrower
        # bag to draw from -- and `SetOffRandom` is the twin.
        for _ in range(int(fx.get("times", 1))):
            living = state.living_enemies
            if not living:
                return
            bombed = [e for e in living if klee_overhaul.holds_charge(e)]
            enemy = state.rng.choice(bombed or living)
            klee_overhaul.set_off(state, enemy, card, badge=badge)
            hit(enemy)
        return

    if fx.get("charge") == "largest":
        # POCKET MATCH (playtest 2026-09-24): only the single largest charge
        # on the aimed enemy goes off, before the card's own hit
        # (`ProtoBombPower.SetOffLargestAimed`).
        for enemy in _pick_targets(state, spec, allow_dead=True):
            klee_overhaul.set_off_largest(state, enemy, card, badge=badge)
            hit(enemy)
        return

    # `allow_dead=True`, and it is rule 3 rather than a shrug: `SetOff` takes
    # the pile before it looks at anything, and its per-charge death test then
    # sends every charge to `JumpCharges`. A Set off aimed at a body that died
    # earlier in the same play therefore MOVES the pile instead of losing it,
    # which is the case R210's bind makes reachable (one creature for the whole
    # play, dead or alive). The card's own hit still fizzles on the corpse,
    # because `_op_damage` picks its targets with `allow_dead` False.
    targets = _pick_targets(state, spec, allow_dead=True)
    wide = fx.get("wide_if")
    if wide and _predicate(state, wide):
        # R276 (Team Effort): EVERY enemy's Bombs go off, one enemy at a time
        # and before the damage, and the card's own hit stays on the aimed
        # body. `ProtoBombPower.SetOffAllThenHit`'s twin.
        for enemy in list(state.living_enemies):
            klee_overhaul.set_off(state, enemy, card, badge=badge)
        for enemy in targets:
            hit(enemy)
        return
    for enemy in targets:
        klee_overhaul.set_off(state, enemy, card, badge=badge)
        hit(enemy)


def _op_plant_bomb(state: CombatState, fx: dict, card: Card) -> None:
    """Rule 1's charge, planted. `Place` / `PlaceOnAll` / `PlaceOnRandom`.

    `allow_dead=True` on the aimed spelling for the reason `place_bomb` already
    carries in `CORPSE_TARGETABLE_OPS`: placing reaches the target through
    `PowerCmd.Apply`, whose only guard is `CanReceivePowers`, and the game's own
    doc says dead creatures can still have powers applied to them. The sweep is
    what moves it off the corpse again.

    `wide_if:` -- COVEN ERRAND (R244, R276). "Place a Bomb 5. If you played a
    Companion card this turn, place it on ALL enemies instead." The widening is a FIELD ON
    THE OP rather than a `conditional` wrapping two `plant_bomb`s, and the
    printed face is the argument: there is ONE Bomb here and one printed size,
    so there must be one op owning one upgradable number. Two ops would need a
    branch to own a var it cannot own (`gen_klee_cards._authored_face_numbers`:
    only a top-level effect does), and the `+` card would print 7 in one clause
    while placing 5 in the other -- `EB-288`'s defect class exactly. The
    predicate is the same vocabulary a `conditional` reads, checked at LOAD by
    `loader._validate_effect_vocabulary` for the same reason the `if:` key is.
    """
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    # AoE trim, 2026-10-03 (Coven Errand): "Bomb 5, 8 if you played a
    # Companion" is the printed size plus a `bonus_if:` rider.
    size = int(fx["size"]) + bonus_if_amount(state, fx)
    is_mine = bool(fx.get("mine", False))
    payload = int(fx.get("payload_mine_all", 0))
    spec = fx.get("target", "enemy")
    wide = fx.get("wide_if")
    if wide and _predicate(state, wide):
        spec = "all_enemies"
    if spec == "all_enemies":
        # Mine Toss: a SNAPSHOT, so a payload firing mid-sweep cannot change
        # who is swept.
        for enemy in list(state.living_enemies):
            klee_overhaul.place(state, enemy, size, is_mine, payload)
        return
    for enemy in _pick_targets(state, spec, allow_dead=(spec == "enemy")):
        klee_overhaul.place(state, enemy, size, is_mine, payload)


def _op_grow_bombs(state: CombatState, fx: dict, card: Card) -> None:
    """Chain Fuse: every Bomb on ONE enemy grows by `amount`. `GrowOn`'s twin,
    and it reads no aliveness test on the target for the same reason the C#
    does not: the pile is a power on the creature, corpse or not."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    amount = int(fx["amount"])
    for enemy in _pick_targets(state, fx.get("target", "enemy"),
                               allow_dead=True):
        klee_overhaul.grow_pile(enemy, amount)
        state.emit("ko_bombs_grew", amount=amount, target=enemy.name,
                   charges=len(enemy.ko_charges))


def _op_plant_bomb_copy_largest(state: CombatState, fx: dict,
                                card: Card) -> None:
    """All of My Treasures! (`EB-491`). ONE call, and the row carries no
    number: the size is read off the board inside `klee_overhaul`, so no card
    can express a second reading of "your largest Bomb"."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    if fx.get("target") == "all_enemies":
        # Klee pre-Balance sweep (2026-10-03): ALL enemies, one size read.
        klee_overhaul.place_copy_of_largest_on_all(state)
        return
    dest = _pick_targets(state, fx.get("target", "enemy"), allow_dead=True)
    klee_overhaul.place_copy_of_largest(state, dest[0] if dest else None)


def _op_merge_bombs(state: CombatState, fx: dict, card: Card) -> None:
    """Careful Arrangement. See `klee_overhaul.merge_all_to` for the two
    defaults the card text does not state."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    dest = _pick_targets(state, fx.get("target", "enemy"), allow_dead=True)
    klee_overhaul.merge_all_to(state, dest[0] if dest else None,
                               int(fx.get("growth", 0)))


def _op_remove_bomb_for_block(state: CombatState, fx: dict,
                              card: Card) -> None:
    """Sorry, Jean...: remove the largest Bomb and gain Block equal to its
    size. ONE call, so the number removed and the number gained cannot drift."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    multiplier = int(fx.get("multiplier", 1))
    if multiplier != 1:
        # R276 (Favonius Escort): "Gain Block equal to twice its size."
        klee_overhaul.remove_largest_for_block_times(state, multiplier)
        return
    klee_overhaul.remove_largest_for_block(state)


def _op_block_largest_bomb(state: CombatState, fx: dict, card: Card) -> None:
    """Careful Now (R252): gain Block equal to your largest Bomb, capped.

    The cap is the ROW's printed number (`cap:`) and the whole rule is ONE call
    into the arm, so the number read and the number gained cannot drift -- the
    same shape `remove_bomb_for_block` above takes for the same reason. Unlike
    that one it SPENDS NOTHING: the pile is read and left where it is.
    """
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    if fx.get("target") == coop.ALLY:
        # THE CO-OP SET (Hide Here!): the same read, paid to ANOTHER player.
        # One seat, nobody to pay -- `engine/coop.py`.
        coop.no_other_player(state, "block_largest_bomb", card)
        return
    klee_overhaul.block_for_largest_bomb(state, int(fx["cap"]))


def _op_grow_largest_bomb(state: CombatState, fx: dict, card: Card) -> None:
    """Stoke the Fuse (the round-11 pool pass): the largest Bomb grows by
    `per_spark` for every Spark this card spent.

    ONE call into the arm, so the number of Sparks read and the growth applied
    are one arithmetic -- `block_largest_bomb`'s shape above, and the same
    reason. The Sparks are read there, off `state.sparks_at_play`, because
    this op is legal only behind an all-in `spend_spark` price and the bank at
    play IS what such a card spent.
    """
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    klee_overhaul.grow_largest_per_spark(state, int(fx["per_spark"]))


def _op_damage_from_bombs(state: CombatState, fx: dict, card: Card) -> None:
    """THE KLEE TEMPO PAPER (2026-10-07, Simmer and Taste Test): damage READ
    off her Bombs that leaves them cooking. `ProtoBombPower.DealFromBombs`'s
    twin.

    `read: largest_half` is Simmer's "plus half your largest Bomb's size" --
    the largest single charge on the living board (`largest_charge`), halved
    and rounded down. `read: target_total` is Taste Test's "damage equal to
    all your Bombs on the enemy" -- every charge on the aimed body, Mines
    included (`total_size`). `amount` is the printed flat part.

    IT READS THE PILE AND DOES NOT SPEND IT: nothing goes off, no Spark is
    minted, no Mine answers. But it IS the card's own hit -- one `_op_damage`
    Attack, so Pyro, the reaction, Strength and Vulnerable land as on any
    other Attack of hers. A read of zero deals nothing.
    """
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    base = int(fx.get("amount", 0) or 0)
    read = fx.get("read")
    if read == "largest_half":
        _enemy, _index, size = klee_overhaul.largest_charge(state)
        bombs = size // 2
    elif read == "target_total":
        targets = _pick_targets(state, fx.get("target", "enemy"))
        bombs = klee_overhaul.total_size(targets[0]) if targets else 0
    else:
        raise ValueError(f"damage_from_bombs read {read!r} on {card.id}")
    total = base + bombs
    if total <= 0:
        return
    _op_damage(state, {"op": "damage", "amount": total,
                       "target": fx.get("target", "enemy")}, card)


def _op_damage_set_off_total(state: CombatState, fx: dict,
                             card: Card) -> None:
    """Big Badda Boom's second clause: "Then deal damage equal to what the
    Bombs dealt." `DealSetOffTotal`'s twin.

    READ OFF THE LEDGER, because by now the pile is gone -- which is exactly
    why the number is remembered rather than recomputed. `EB-270`: the ledger
    banks what each explosion LANDED for, so this is the card's printed promise
    and not the raw charge sum it used to be.
    """
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    # 2026-09-26: the ECHO BASE, not the landed total -- this is a card
    # attack and the pipeline below applies the target's Vulnerable to it, so
    # handing it a number that had already paid one paid it twice. C# twin:
    # `KleeOverhaulLedger.SetOffEchoBaseThisPlay`.
    total = state.ko_set_off_echo_base_this_play
    if total <= 0:
        return
    _op_damage(state, {"op": "damage", "amount": total,
                       "target": fx.get("target", "enemy")}, card)


def _op_multiply_set_off(state: CombatState, fx: dict, card: Card) -> None:
    """The Big One arms the multiplier -- the ROW's number (`multiplier`, 4
    since R243: "move The Big One to 4x with no flat number") -- and the Set
    off behind it on the same row spends it, which is what "set off this way"
    means."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    multiplier = int(fx["multiplier"])
    state.emit("ko_multiplier_armed", multiplier=multiplier)
    klee_overhaul.arm_multiplier(state, multiplier)


def _op_draw_per_set_off(state: CombatState, fx: dict, card: Card) -> None:
    """Ammo Scavenging: rule 7's first counter, spent."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    klee_overhaul.draw_per_set_off(state)


def _op_companion_mark_hand(state: CombatState, fx: dict, card: Card) -> None:
    """Alice's Introduction Magic (R244, R276): "All cards in your hand count as
    Companion cards this turn." `IntroductionMagicPower`'s twin.

    AN ARM VERB THAT TOUCHES NO BOMB, and it is Klee's anyway: every card that
    READS "a Companion card was played" is hers. The rule itself lives in
    `companion_hexerei`; this is the op, and
    `klee_overhaul.mark_hand_companion` is the arm's gate between them.
    """
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    klee_overhaul.mark_hand_companion(state)


def _op_mine_bombs(state: CombatState, fx: dict, card: Card) -> None:
    """Hair Trigger (R276): "Your Bombs on this enemy become a Mine." One call
    into the arm, `ProtoBombPower.MineAllOn`'s twin. A corpse is aimable for
    `_op_grow_bombs`' reason: the pile is on the creature, corpse or not."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    for enemy in _pick_targets(state, fx.get("target", "enemy"),
                               allow_dead=True):
        klee_overhaul.mine_all_on(state, enemy)


def _op_return_to_hand(state: CombatState, fx: dict, card: Card) -> None:
    """Blast Shield (`EB-732`): "Return this card to your hand."

    ONE call into the arm, which raises the per-play flag `combat._finish_play`
    reads at its routing line -- see `klee_overhaul.mark_return_to_hand` for
    why the move cannot be made here and for the C# seam that answers the same
    question one layer up.
    """
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    klee_overhaul.mark_return_to_hand(state)


# --- THE KOKOMI OVERHAUL, DRAFT 6 (C.KOKOMI_OVERHAUL) ---------
#
# THE ARM IS BUILT NOW. It used to refuse the way the Klee arm above still
# does, on its slice packet's sec.5 ("the Python sim is not brought up for
# slice one"), and the twin was raised deliberately after the C# had proved the
# rule: `engine/kokomi_plan.py` is that build, and it mirrors
# `KleeCode/Powers/Prototype/KokomiPlan.cs` clause for clause.
#
# WHAT STILL REFUSES, and why each one does:
#   * every verb, WITH THE FLAG OFF or on a seat that is not Kokomi. The rows
#     are unreachable there (`loader._card_prototype` refuses a `proto_kk_` id
#     with the flag off), so reaching one is a DEFECT and not a degradation --
#     a silent no-op would be the worst possible stand-in.
#   * the two PLAN-ONLY clauses, always, from a body. They are registered in
#     `OPS` because `loader._validate_effect_vocabulary` checks a row's `plan:`
#     list through the same vocabulary the body takes, and they are resolved by
#     `kokomi_plan` and by nothing else; a top-level spelling would be a
#     different, unpriced card. `gen_klee_cards.PLAN_ONLY_OPS` refuses the same
#     two in an `effects:` list on the other side.
# THE POOL EXPANSION's five (R276). One call each into `klee_overhaul`,
# the arm's discipline; C# twins in `KleeExpansion` and `ProtoBombPower`.
def _op_grow_largest(state: CombatState, fx: dict, card: Card) -> None:
    """One More Charge and Treasure Map: the largest Bomb grows by `amount`,
    and with a bar the grown Bomb is measured AFTER the growth."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    klee_overhaul.grow_largest_by(state, int(fx["amount"]),
                                  int(fx.get("draw_if_at_least", 0)),
                                  int(fx.get("draw", 0)))


def _op_transform_statuses_into(state: CombatState, fx: dict,
                                card: Card) -> None:
    """THE KLEE STATUS PACKAGE: Klee Can Explain!'s transform."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    klee_overhaul.transform_statuses_into(state, str(fx["card"]))


def _op_exhaust_statuses_grow_largest(state: CombatState, fx: dict,
                                      card: Card) -> None:
    """THE KLEE STATUS PACKAGE: Albedo -- Dust of Purification."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    klee_overhaul.exhaust_statuses_grow_largest(state, int(fx["amount"]))


def _op_lose_strength(state: CombatState, fx: dict, card: Card) -> None:
    """"ALL enemies lose N Strength." PERMANENT, Disarm's and Malaise's kind:
    negative Strength on the target, not a this-turn loss (the mod's
    `PowerCmd.Apply<StrengthPower>` at minus N). First carrier: Kitchen
    Alchemy (defence in the status pile, 2026-10-01). With `per_status`
    (Kitchen Alchemy, reworked 2026-10-02): "Exhaust every status in your
    hand; they lose 1 more for each." The exhausts first, then ONE loss of
    the base plus `per_status` for each (`KleeStatusPackage.LossWithStatuses`).
    With `this_turn` (Cover Your Ears!, Klee final pass 2026-10-02) the loss
    is Piercing Wail's instead: `temp_strength_down`, the TemporaryStrength
    shape `refpowers` already runs for Mangle, returned at the end of the
    enemy's own turn.
    """
    amount = int(_amount(state, fx["amount"]))
    if fx.get("this_turn"):
        for enemy in _pick_targets(state, fx.get("target", "enemy")):
            powers.apply_power(state, enemy, "temp_strength_down", amount,
                               applier=state.player)
        return
    if "per_status" in fx:
        if not klee_overhaul.live(state):
            _op_klee_overhaul_off(state, fx, card)    # always raises
        exhausted = klee_overhaul.exhaust_statuses(state)
        amount += int(fx["per_status"]) * exhausted
        state.emit("ko_kitchen_alchemy", exhausted=exhausted, loss=amount)
    for enemy in _pick_targets(state, fx.get("target", "enemy")):
        powers.apply_power(state, enemy, "strength", -amount,
                           applier=state.player)


def _op_multiply_largest_bomb(state: CombatState, fx: dict,
                              card: Card) -> None:
    """Half a Mountain: the largest Bomb's current size times `factor`."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    klee_overhaul.multiply_largest(state, int(fx["factor"]))


def _op_fetch_from_discard(state: CombatState, fx: dict, card: Card) -> None:
    """Treasure Map and Come Back and Play!: one card of the kind out of the
    discard pile into the hand; none of the kind and the card plays on."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    klee_overhaul.fetch_from_discard(state, fx["filter"])


def _op_add_random_companion(state: CombatState, fx: dict,
                             card: Card) -> None:
    """Tag Along and Adventure Club: random Companion cards, free this
    turn."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    klee_overhaul.add_random_companions(state, int(fx["amount"]))


def _op_plant_homework_bomb(state: CombatState, fx: dict,
                            card: Card) -> None:
    """THE KLEE SCALING PASS (klee-next, 2026-10-05): Witch's Homework's
    Bomb. The sim places it at its printed size and does NOT model the
    run-long growth: the row is grant-only (in no pool, `C.KLEE_OVERHAUL_
    POOL_IDS`), so no sim run draws it, and the sim's Balance machinery is
    parked (`review/active/klee-balance-measurement-2026-10-05.md` pick 3).
    The C# is `KleeScalingPass`."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    for enemy in _pick_targets(state, "enemy", allow_dead=True):
        klee_overhaul.place(state, enemy, int(fx["size"]))


def _op_grant_kapow_each_turn(state: CombatState, fx: dict,
                              card: Card) -> None:
    """Alice's Detonator: install the twin the card's upgrade names
    (`upgraded_grant`, written onto the effect by the upgrade applier)."""
    if not klee_overhaul.live(state):
        _op_klee_overhaul_off(state, fx, card)        # always raises
    klee_overhaul.install_detonator(state, bool(fx.get("upgraded", False)))


def _op_kokomi_overhaul_off(state: CombatState, fx: dict,
                            card: Card) -> None:
    raise NotImplementedError(
        f"card {card.id!r}: op {fx['op']!r} belongs to the KOKOMI_OVERHAUL "
        "arm (draft 6, the Plan). It resolves only with Kokomi in the seat -- "
        "the mod's `KokomiOverhaul.LiveFor` gate, mirrored -- so reaching "
        "this is a defect rather than a degradation.")


def _op_kokomi_plan_only(state: CombatState, fx: dict, card: Card) -> None:
    raise NotImplementedError(
        f"card {card.id!r}: op {fx['op']!r} is a PLAN-ONLY clause of the "
        "KOKOMI_OVERHAUL arm. It is legal inside a row's `plan:` list and "
        "nowhere else -- `engine.kokomi_plan` is its only resolver, and "
        "`gen_klee_cards.PLAN_ONLY_OPS` refuses it in an `effects:` list on "
        "the C# side. Registered here only so the loader's vocabulary check "
        "accepts the `plan:` list that carries it.")


def _op_carry_out_front_plan(state: CombatState, fx: dict,
                             card: Card) -> None:
    """Change of Plans: the jellyfish carries out your front Plan now."""
    if not kokomi_plan.live(state):
        _op_kokomi_overhaul_off(state, fx, card)      # always raises
    kokomi_plan.resolve_front(state)


def _op_draw_after_plans(state: CombatState, fx: dict, card: Card) -> None:
    """Tide Chart (`EB-478`, R257): "Next turn, after the Bake-Kurage carries
    out its Plans, draw 1 card for each."

    THE PLAY WRITES A PROMISE AND DRAWS NOTHING. The count this row multiplies
    does not exist yet on the turn the card is played -- that is the defect the
    redesign answers -- so the whole op is one call into `kokomi_plan`, which
    owns the promise and the payment alike.
    """
    if not kokomi_plan.live(state):
        _op_kokomi_overhaul_off(state, fx, card)      # always raises
    kokomi_plan.promise_tide_chart(state, int(fx.get("per", 1)),
                                   int(fx.get("amount", 0)))


def _op_plan_from_exhaust(state: CombatState, fx: dict, card: Card) -> None:
    """Moon's Reflection's one screen. See `kokomi_plan.schedule_from_exhaust`
    for the two shapes it splits into and for the chooser's status."""
    if not kokomi_plan.live(state):
        _op_kokomi_overhaul_off(state, fx, card)      # always raises
    kokomi_plan.schedule_from_exhaust(state, card)


def _op_damage_quarter_max_hp(state: CombatState, fx: dict,
                              card: Card) -> None:
    """Sango Isshin's now-line: a quarter of her Max HP, Hydro, at the aim.

    THE ROW'S OWN TARGET, unlike its planned half: the now-line lands where the
    card was aimed (`target: enemy`, this engine's bound aim) and the planned
    half lands on the front or on everybody, which is what "the same to every
    enemy" says. `KokomiRules.QuarterMaxHp` / `QuarterMaxHpAll` are the same
    split one file over, both reading one `QuarterOfMaxHp`.
    """
    if not kokomi_plan.live(state):
        _op_kokomi_overhaul_off(state, fx, card)      # always raises
    amount = kokomi_plan.quarter_of_max_hp(state)
    if amount <= 0:
        return
    for enemy in _pick_targets(state, fx.get("target", "enemy")):
        deal_damage_to_enemy(state, enemy, amount, element="hydro",
                             source="attack" if card.type == "attack"
                             else "card")


def _op_fetch_open_casket(state: CombatState, fx: dict, card: Card) -> None:
    """What the Tokoyo Returns (the Casket pass, 2026-09-28). The first Open
    the Casket in her draw pile, else her discard pile, goes to her hand; see
    `kokomi_plan.fetch_open_casket`."""
    if not kokomi_plan.live(state):
        _op_kokomi_overhaul_off(state, fx, card)      # always raises
    kokomi_plan.fetch_open_casket(state)


def _op_casket_double(state: CombatState, fx: dict, card: Card) -> None:
    """What the Tokoyo Took (the Casket pass): "Double the Casket's count"."""
    if not kokomi_plan.live(state):
        _op_kokomi_overhaul_off(state, fx, card)      # always raises
    kokomi_plan.double_casket(state)


def _op_open_casket(state: CombatState, fx: dict, card: Card) -> None:
    """Open the Casket, the relic's token (the Casket pass): "Gain Strength
    equal to the Casket's count, then empty it." See
    `kokomi_plan.open_casket`."""
    if not kokomi_plan.live(state):
        _op_kokomi_overhaul_off(state, fx, card)      # always raises
    kokomi_plan.open_casket(state)


def _op_cancel_all_plans_cash(state: CombatState, fx: dict,
                              card: Card) -> None:
    """Ebb Tide (`EB-643`). Per ENTRY and not per carry-out; see
    `kokomi_plan.cancel_all_plans_cash` for why that is the face's own word."""
    if not kokomi_plan.live(state):
        _op_kokomi_overhaul_off(state, fx, card)      # always raises
    kokomi_plan.cancel_all_plans_cash(state)


def _op_redirect_queued_plans(state: CombatState, fx: dict,
                              card: Card) -> None:
    """Converging Tide (`EB-643`): the queue as it stands re-aims at the enemy
    this card was played on.

    THE ROW'S OWN TARGET, through the same `_pick_targets` door every other
    aimed now-line takes, so "this enemy" is the body the play was aimed at and
    never a second definition of the front. A play that reaches no living body
    stamps nothing, which `kokomi_plan.redirect_queued_plans` records.
    """
    if not kokomi_plan.live(state):
        _op_kokomi_overhaul_off(state, fx, card)      # always raises
    targets = _pick_targets(state, fx.get("target", "enemy"))
    kokomi_plan.redirect_queued_plans(state, targets[0] if targets else None)


def _op_remove_debuff(state: CombatState, fx: dict, card: Card) -> None:
    """Cleansing Wave's cleanse. The reading (the FIRST standing debuff, no
    choice offered) is recorded at `kokomi_plan.remove_one_debuff`."""
    if not kokomi_plan.live(state):
        _op_kokomi_overhaul_off(state, fx, card)      # always raises
    kokomi_plan.remove_one_debuff(state)


# ----------------------------------------------------------------------
# FURINA, THE SALON'S TAB (`tier0.engine.furina_stage`, on the research
# slice's rules, `furina_tide`). Each verb unpacks its row and delegates to
# that module, which is the ONE implementation of every rule. Every one is
# inert for anyone who is not Furina.
# ----------------------------------------------------------------------
def _op_stage_drain(state: CombatState, fx: dict, card: Card) -> None:
    """"Drain N": a fixed price ("Drain 5. Deal 24 damage.") or a mode's
    head ("Drain 3: deal 12 instead"). The gate offered it only above the
    line (`furina_stage.mode_offered`, `fixed_price_refusal`)."""
    furina_stage.drain(state, _amount(state, fx.get("amount", 1)))


def _op_stage_repay(state: CombatState, fx: dict, card: Card) -> None:
    """"Repay N": regain up to N drained HP."""
    furina_stage.repay(state, _amount(state, fx.get("amount", 1)))


def _op_stage_repay_all(state: CombatState, fx: dict, card: Card) -> None:
    """Singer of Many Waters: "Repay all your drained HP." """
    furina_stage.repay_all(state)


def _op_stage_guest(state: CombatState, fx: dict, card: Card) -> None:
    """A Guest Star card: "Summon X." The pool to 75 (sec.3): the card
    exhausts, its guest's seat holds it until the guest leaves, and an
    upgraded one (`upgrades`' `guest_upgraded`) raises the guest's line or
    act."""
    furina_stage.guest_star(state, fx["member"],
                            upgraded=bool(fx.get("upgraded")), card=card)


def _op_furina(state: CombatState, fx: dict, card: Card) -> None:
    """THE POOL TO 75's guest verbs, one `kind` per card
    (`furina_stage.kind`, the C# `FurinaCards`). Inert off Furina."""
    furina_stage.kind(state, fx, card)


def _op_stage_spend(state: CombatState, fx: dict, card: Card) -> None:
    """A Spend N: a mode's payment ("Spend 6: deal 12 ... instead") or a
    fixed price ("Spend 4. Deal 11 Hydro damage.")."""
    paid = furina_stage.spend(state, _amount(state, fx.get("amount", 1)))
    state.stage_spent_this_card = paid


def _op_stage_spend_all(state: CombatState, fx: dict, card: Card) -> None:
    """"Spend all your Fanfare." What was spent is this play's
    `stage_spent` (0 held: no Spend)."""
    state.stage_spent_this_card = furina_stage.spend_all(state)


def _op_stage_energy_next(state: CombatState, fx: dict, card: Card) -> None:
    """"Gain N Energy next turn" (Interval Bell, Salon's Tab): owed on her
    record and paid at her next turn (`furina_tide.energy_kept`); the C#
    twin applies the game's `EnergyNextTurnPower`."""
    furina_stage.energy_next_turn(state, int(fx.get("amount", 1)))


def _op_kokomi(state: CombatState, fx: dict, card: Card) -> None:
    """THE KOKOMI EXPANSION's now-line verbs, one `kind` per card
    (`kokomi_plan.kind`). The aimed kind (Salt in the Wound) reads the body
    the play was aimed at, through `_pick_targets`."""
    if not kokomi_plan.live(state):
        _op_kokomi_overhaul_off(state, fx, card)      # always raises
    target = None
    if fx.get("target") == "enemy":
        picked = _pick_targets(state, "enemy")
        target = picked[0] if picked else None
    kokomi_plan.kind(state, fx, card, target)


def _op_varka(state: CombatState, fx: dict, card: Card) -> None:
    """VARKA's Oath verbs, one `kind` per rule (`varka_oath.op_varka`).
    Refused by name for anyone who is not Varka, or with the switch off."""
    varka_oath.op_varka(state, fx, card)


def _op_add_knight(state: CombatState, fx: dict, card: Card) -> None:
    """Knights' Roll Call (`varka_oath.op_add_knight`)."""
    varka_oath.op_add_knight(state, fx, card)


OPS = {
    "damage": _op_damage,
    "block": _op_block,
    "block_next_turn": _op_block_next_turn,
    # (C.COMPANION_OVERHAUL) -- the Inazuma arm's one new op.
    "block_half_damage": _op_block_half_damage,
    BLOCK_AT_TURN_START: _op_block_at_turn_start,
    "draw": _op_draw,
    "draw_while": _op_draw_while,
    "energy": _op_energy,
    "apply_power": _op_apply_power,
    "apply_aura": _op_apply_aura,
    # VARKA, THE OATH REWORK (`varka_oath`): his rules' one op, and
    # Knights' Roll Call.
    "varka": _op_varka,
    # THE KOKOMI EXPANSION, BATCH ONE (2026-09-29): the now-line verbs, one
    # op with a `kind:` (Varka's shape).
    "kokomi": _op_kokomi,
    # FURINA, THE POOL TO 75 (2026-10-09): her guest verbs, one op with a
    # `kind:` (Kokomi's shape).
    "furina": _op_furina,
    "add_knight": _op_add_knight,
    "place_bomb": _op_place_bomb,
    "detonate": _op_detonate,
    "move_bombs": _op_move_bombs,
    "modify_bombs": _op_modify_bombs,
    "swirl": _op_swirl,
    "refresh_all_auras": _op_refresh_all_auras,
    "buff_next_attack": _op_buff_next_attack,
    "cost_mod": _op_cost_mod,
    "gain_spark": _op_gain_spark,
    "spend_spark": _op_spend_spark,
    # FURINA, THE SALON'S TAB.
    "stage_drain": _op_stage_drain,
    "stage_repay": _op_stage_repay,
    "stage_repay_all": _op_stage_repay_all,
    "stage_guest": _op_stage_guest,
    "stage_spend": _op_stage_spend,
    "stage_spend_all": _op_stage_spend_all,
    "stage_energy_next": _op_stage_energy_next,
    "gain_fanfare_floor": _op_gain_fanfare_floor,
    "raise_fanfare_cap": _op_raise_fanfare_cap,
    "crash_fanfare": _op_crash_fanfare,
    "drain_fanfare": _op_drain_fanfare,
    "heal": _op_heal,
    "add_card": _op_add_card,
    "discard": _op_discard,
    "discard_for_sparks": _op_discard_for_sparks,
    "exhaust_from": _op_exhaust_from,
    "scry_discard": _op_scry_discard,
    "scry_bottom": _op_scry_bottom,
    "scry_take": _op_scry_take,
    "conditional": _op_conditional,
    "choose_one": _op_choose_one,                # EB-118 surface, unused
    "repeat_this": _op_repeat_this,
    "grow_damage": _op_grow_damage,
    "chance_bomb_per_detonation": _op_chance_bomb_per_detonation,
    "copy_companion_in_hand": _op_copy_companion_in_hand,
    "replay_next_companion": _op_replay_next_companion,
    "copy_companions_played_this_combat": _op_copy_companions_played,
    # --- Klee overhaul, slice one (C.KLEE_OVERHAUL) ---
    # BUILT (`EB-312`): `engine/klee_overhaul.py` is the twin, and every arm
    # here is one call into it. They refuse with the flag off or on a seat that
    # is not Klee -- see `_op_klee_overhaul_off`.
    "set_off": _op_set_off,
    "plant_bomb": _op_plant_bomb,
    "plant_homework_bomb": _op_plant_homework_bomb,
    "grow_bombs": _op_grow_bombs,
    "merge_bombs": _op_merge_bombs,
    # THE POOL PASS's three (`EB-491`), on the same terms as every arm verb
    # above: one call each into `klee_overhaul`, and a raise with the flag off
    # or on a seat that is not Klee.
    "plant_bomb_copy_largest": _op_plant_bomb_copy_largest,
    "remove_bomb_for_block": _op_remove_bomb_for_block,
    # R252's verb, the defence shelf's own (Careful Now). Beside Sorry, Jean...
    # because it reads the same pile, and distinct from it because it spends
    # nothing -- see `_op_block_largest_bomb`.
    "block_largest_bomb": _op_block_largest_bomb,
    # The round-11 pool pass's verb (Stoke the Fuse), and the arm's one
    # SPARK-SHAPED payout: it reads the bank the card just spent and pours it
    # into a single charge. Beside `grow_bombs` because it grows, and distinct
    # from it because it grows ONE Bomb by a number no row prints whole --
    # see `_op_grow_largest_bomb`.
    "grow_largest_bomb": _op_grow_largest_bomb,
    "damage_set_off_total": _op_damage_set_off_total,
    # The Klee tempo paper (2026-10-07): Simmer and Taste Test.
    "damage_from_bombs": _op_damage_from_bombs,
    "multiply_set_off": _op_multiply_set_off,
    "draw_per_set_off": _op_draw_per_set_off,
    # R244's one new verb, the readers' enabler (renamed at R276). It touches
    # no Bomb and is still the arm's, because the cards that READ a Companion
    # play are Klee's -- see `_op_companion_mark_hand`.
    "companion_mark_hand": _op_companion_mark_hand,
    # R276's Hair Trigger -- see `_op_mine_bombs`.
    "mine_bombs": _op_mine_bombs,
    # POOL PASS TWO's two (`EB-732`), and both are about a CARD rather than a
    # charge: Blast Shield routes its own play to the hand, Once More! takes
    # the last Set off card back out of the discard pile.
    "return_to_hand": _op_return_to_hand,
    # R276, the pool expansion's five.
    "grow_largest": _op_grow_largest,
    "multiply_largest_bomb": _op_multiply_largest_bomb,
    "transform_statuses_into": _op_transform_statuses_into,
    "exhaust_statuses_grow_largest": _op_exhaust_statuses_grow_largest,
    "lose_strength": _op_lose_strength,
    "fetch_from_discard": _op_fetch_from_discard,
    "add_random_companion": _op_add_random_companion,
    "grant_kapow_each_turn": _op_grant_kapow_each_turn,
    # --- Kokomi overhaul, DRAFT 6 (C.KOKOMI_OVERHAUL) -----
    # Registered so the rows load, priced so the drafter is honest, resolved by
    # nothing -- see `_op_kokomi_overhaul_unbuilt` for why raising is the shape.
    #
    # DRAFT 6 REPLACED THE VERBS, IT DID NOT ADD TO THEM. `gain_tide`,
    # `surge`, `block_half_surge`, `exert`, `draw_per_tide`,
    # `play_top_of_draw`, `draw_companion_from_draw` and the old `plan` OP are
    # gone: the ruled brief's sec.6 cuts Tide, Surge, Exert and the pulse by
    # name, and draft 6's Plan is a top-level `plan:` LIST on the row rather
    # than a clause inside a body. An op left registered for a rule nothing has
    # is a row waiting to print it.
    # RESOLVED under `C.COMPANION_OVERHAUL` (a Universal prints it) as well as
    # under the Kokomi arm -- see `_op_mend`.
    "mend": _op_mend,
    "remove_debuff": _op_remove_debuff,
    "carry_out_front_plan": _op_carry_out_front_plan,
    "plan_from_exhaust": _op_plan_from_exhaust,
    # `EB-478`, R257. Tide Chart's promise: a now-line that draws NOTHING now.
    "draw_after_plans": _op_draw_after_plans,
    "damage_quarter_max_hp": _op_damage_quarter_max_hp,
    # The two PLAN-ONLY clauses. They never appear in an `effects:` list -- the
    # codegen refuses one there by name -- but they are registered here anyway,
    # because `loader.prototype_cards` validates a row's `plan:` list through
    # the same vocabulary check the body takes and an unregistered clause could
    # not be staged at all. `engine.kokomi_plan` resolves them off a `plan:`
    # list; reached from a BODY they refuse, which is what makes "plan-only"
    # a property of the code.
    # THREE now, and the third is Crystal Collapse's (R236). Same terms: it is
    # registered so `loader.prototype_cards` can validate the row's `plan:`
    # list through the body's own vocabulary check, and it refuses when it is
    # reached from an `effects:` list.
    "play_copy_of_companion": _op_kokomi_plan_only,
    # FOUR, and the fourth is Tide Wall's (`EB-335`, R246 pick 2): "Gain N
    # Block for each Plan the Bake-Kurage carries out this morning". Same
    # terms, and plan-only for a reason of its own -- the count it multiplies
    # is a fact about a MORNING, so a now-line spelling would print a number
    # that is zero every time it is read.
    # FIVE, and the fifth is Breakwater's (`EB-685`, pool pass five): "plus N
    # Block for each Plan the Bake-Kurage is HOLDING". Same terms, and
    # plan-only for the line above's reason one count over -- a now-line
    # spelling would read the queue before the turn's Plans were written and
    # pay for a queue the player has not built yet.
    "block_per_plan_held": _op_kokomi_plan_only,
    # NINE, and four of them are `EB-643`'s (R265). Same terms as the four
    # above, and plan-only for one reason they share: each names a POSITION in
    # a running drain -- "the next Plan", "each Plan carried out after this
    # one" -- so a now-line spelling would ask about a drain that is not
    # running and answer nothing every time it was played.
    # R267 pick 3: Scout Ahead is back on the positional count. Both spellings
    # stay registered; only `draw_per_plan_after` is on a row today.
    "draw_per_plan_this_turn": _op_kokomi_plan_only,
    "next_plan_double_damage": _op_kokomi_plan_only,
    "next_plan_extra_carry_out": _op_kokomi_plan_only,
    # `EB-655`, Battle Plan's grant. Legal in a `plan:` list and nowhere else.
    # R276 PICK 1, the halves rewrite: five Plan-only clauses.
    "first_attack_twice": _op_kokomi_plan_only,
    "first_card_free": _op_kokomi_plan_only,
    # Kokomi core pass: Chain of Command's switch, Stolen Chapter's narrowed.
    # THE CO-OP SET's two Plan clauses about another player (`engine/coop.py`).
    coop.ALLY_DRAW: _op_kokomi_plan_only,
    coop.OTHERS_ATTACK_DAMAGE_THIS_TURN: _op_kokomi_plan_only,
    "block_front_intent": _op_kokomi_plan_only,
    # `EB-643`, R265. THE THREE NOW-LINES THAT OPERATE ON THE QUEUE: take the
    # newest Plan back (Second Thoughts), cash the whole queue in (Ebb Tide),
    # and re-aim what is already written (Converging Tide). They are the
    # arm's first verbs that UNWRITE a Plan, which is the pool pass's whole
    # answer to a queue that empties on a timer.
    "cancel_all_plans_cash": _op_cancel_all_plans_cash,
    "redirect_queued_plans": _op_redirect_queued_plans,
    # THE CASKET PASS (2026-09-28). What the Tokoyo Returns and What the
    # Tokoyo Took work the Tamakushi Casket's count; `open_casket` is the
    # relic's token (built in `kokomi_plan.open_the_casket_card`, on no
    # sheet); `casket_gain` is Pearl Diver's plan clause, legal in a `plan:`
    # list and nowhere else.
    "fetch_open_casket": _op_fetch_open_casket,
    "casket_double": _op_casket_double,
    "open_casket": _op_open_casket,
    # THE KOKOMI EXPANSION, BATCH ONE: four plan-only clauses (Lull, Undertide
    # Lance, Evening Watch, Brace for the Tide).
    "energy_if_alone": _op_kokomi_plan_only,
    "damage_if_alone": _op_kokomi_plan_only,
    "block_per_attacking_enemy": _op_kokomi_plan_only,
    "double_block": _op_kokomi_plan_only,
    # POOL COMPLETION (2026-10-01): Tactical Relay's two plan-only clauses.
    "each_player_energy": _op_kokomi_plan_only,
    "each_player_draw": _op_kokomi_plan_only,
    # THE STATUS BATCH (2026-10-01): four plan-only clauses that read the
    # hand just drawn.
    "block_per_status_in_hand": _op_kokomi_plan_only,
    "exhaust_statuses_in_hand": _op_kokomi_plan_only,
    "transform_statuses_in_hand": _op_kokomi_plan_only,
    "discard_and_draw": _op_kokomi_plan_only,
    # --- base-game parity ops (the real Ironclad pool) ---
    "upgrade_in_hand": _op_upgrade_in_hand,
    "gain_max_hp": _op_gain_max_hp,
    "recall_to_draw": _op_recall_to_draw,
    "extra_card_screen": _op_extra_card_screen,
    "draw_to_hand_size": _op_draw_to_hand_size,
    "strip_block": _op_strip_block,
    "chain_attack": _op_chain_attack,
    "autoplay_from_exhaust": _op_autoplay_from_exhaust,
    "remember_card": _op_remember_card,
    "grant_sly_this_turn": _op_grant_sly_this_turn,
    "transform_in_hand": _op_transform_in_hand,
    "generate_from_pool": _op_generate_from_pool,
    "autoplay_from_draw": _op_autoplay_from_draw,
}


def _resolve_effects(state: CombatState, effects: list[dict],
                     card: Card) -> None:
    for fx in effects:
        if fx["op"] not in OPS:
            raise ValueError(f"card {card.id!r}: unknown op {fx['op']!r}")
        OPS[fx["op"]](state, fx, card)


def resolve_card(state: CombatState, card: Card) -> None:
    # THE BIND, and it is the FIRST line of a play for a reason (EB-136 /
    # R210, C18). `CardPlay.Target` is filled in when the play is CONSTRUCTED,
    # before `OnPlayWrapper` is entered, so the aim is picked ahead of every
    # op -- pre-AoE, pre-kill, pre-anything this card is about to do. Cleared
    # in the `finally` so the pilot's between-play estimates read live state
    # instead of the last card's corpse.
    state.card_aim = bind_card_aim(state, card)
    state.card_aim_bound = True
    # VARKA (`varka_oath.begin_play`): this play's Oath scope opens, and a
    # Knight sets his current element BEFORE its effects resolve. Both are
    # dead for anyone who is not Varka.
    varka = varka_oath.live(state.player)
    if varka:
        varka_oath.begin_play(state, card)
    try:
        _resolve_card_bound(state, card)
        # THE FURINA RESEARCH SLICE (`furina_tide`, sim only): the same door
        # for the research proposal's rows. Dead without the `ftd` tag.
        if "ftd" in card.tags:
            from tier0.engine import furina_tide    # late: avoids the cycle
            furina_tide.resolve_card(state, card)
    finally:
        if varka:
            varka_oath.end_play(state, card)
        state.card_aim = None
        state.card_aim_bound = False


def _resolve_card_bound(state: CombatState, card: Card) -> None:
    # Control provenance (§2.2a): a companion's control counts toward
    # SUPPORT_CARRY.
    state.current_card_companion = card.is_companion
    state.reactions_this_card = 0
    state.kills_this_card = 0
    state.fatal_kills_this_card = 0
    state.exhausted_this_card = 0
    # EB-118: a fresh, EMPTY identity context per card play. Rebound rather
    # than cleared for the reason _op_exhaust_from states. This line is the
    # whole cross-card scoping guarantee -- the card after an exhausting card
    # reads nothing, whatever it asks.
    state.exhaust_selection = []
    state.block_gains_this_card = 0
    state.block_gained_this_card = 0
    # (C.COMPANION_OVERHAUL). Gorou's "half the damage dealt", on
    # the same line as the two Block counters and for the same scoping reason:
    # the card after an Attack must bank nothing from it.
    state.mi_damage_dealt_this_card = 0
    state.discards_this_card = 0
    # (R213 B), on the same line and for the same scoping reason:
    # the card after a drain must not read the drain's number.
    state.fanfare_drained_this_card = 0
    # FURINA'S STAGE, on the same line as the drain above and for its reason:
    # the card after a Spend must not read the Spend's number.
    state.stage_spent_this_card = 0
    # THE POOL TO 75: and the card after a Repay must not read its HP.
    furina_stage.begin_play(state)
    state.last_drawn_type = ""
    state.detonations_at_card_start = state.detonations_total
    # (C.KLEE_OVERHAUL). Big Badda Boom's play-scoped memory,
    # opened BY THE CARD THAT READS IT and by no other row -- the emitter
    # prepends `KleeOverhaulLedger.For(...).BeginPlay()` to exactly the rows
    # carrying `damage_set_off_total`, and `klee_overhaul.begin_play` asks the
    # same question of the same effect list. On the line beside
    # `detonations_at_card_start` because it is the same idiom one arm over: a
    # per-play memory opened at the top of the play that reads it.
    klee_overhaul.begin_play(state, card)
    state.repeat_requested = 0
    # Predicate snapshot: does the default target hold an off-element aura?
    # Reads the BOUND aim (R210) rather than re-deriving the lowest-HP pick,
    # so Sizzle's predicate and Sizzle's two damage rows cannot disagree about
    # which creature the card is talking about -- and under a free play's
    # forced random targeting the predicate now follows the rolled aim instead
    # of a lowest-HP body the card will never touch.
    tgt = state.card_aim
    state.target_had_offelement_aura = bool(
        tgt and tgt.aura and tgt.aura != state.player.element)
    # Its any-aura sibling (R189 C2), taken off the SAME bound aim in the
    # same breath so the two predicates can never describe different bodies.
    state.target_had_aura = bool(tgt and tgt.aura)
    # Per-card flat attack bonus. Computed by the shared pure helper so the
    # pilot's estimate cannot drift from what actually resolves (v0.4 W1);
    # the side effect the helper must NOT have lives here instead: Bennett's
    # next_attack_up is CONSUMED by this play.
    bonus = flat_attack_bonus(state, card, state.current_card_cost)
    if card.type == "attack":
        p = state.player
        p.powers.pop("next_attack_up", 0)
    state.current_attack_bonus = bonus
    # VARKA: Stormward Stance's part of that bonus, which his elemental
    # follow-up hits (not Anemo) do not take. A no-op for anyone else.
    varka_oath.note_attack_bonus(state, card)
    state.mc_attack_element_override = companion_overhaul_card_start(state, card)

    # THE PLAN AIM (C.KOKOMI_OVERHAUL, draft 6). "Played on the
    # Bake-Kurage" is a property of the PLAY -- `CardPlay.Target` in the mod,
    # decided by the player before `OnPlay` is entered -- so it is asked HERE,
    # after the per-card context is open and before the first op, which is the
    # same moment the aim above is bound.
    #
    # THE `return` IS THE MOD'S. `OnPlay`'s pet branch schedules and returns,
    # so a card played on the jellyfish does NONE of its now-line: not the
    # body, not the repeat loop, not the enchantment riders. The cost is
    # already paid (`combat.play_card` charged it before this) and the card is
    # already out of hand, which is the whole shape of rule 2.
    if kokomi_plan.plan_aimed_at_pet(state, card):
        kokomi_plan.schedule(state, card)
        return

    _resolve_effects(state, card.effects, card)
    if state.repeat_requested:                          # Perfect Timing
        times, state.repeat_requested = state.repeat_requested, 0
        for _ in range(times):
            _resolve_effects(
                state,
                [fx for fx in card.effects if fx["op"] != "repeat_this"
                 and not (fx["op"] == "conditional"
                          and any(e.get("op") == "repeat_this"
                                  for e in fx.get("then", [])))],
                card)
    # Enchantment rider (R82): appended AFTER the card's own resolution --
    # Inky's Weak lands on whoever the play targeted, once per play. The
    # damage half of the rider is in _op_damage (it must ride each hit).
    if card.enchant_effects:
        _resolve_effects(state, card.enchant_effects, card)
    # First-play-only riders (R82 reopened): Sown's Energy and Swift's draw.
    # Fired after the ordinary rider, then the gate closes for the rest of
    # the combat. The gate is a per-INSTANCE field and the run layer rebuilds
    # every card from its deck id each fight, so "each combat" needs no reset
    # of its own -- but combat start clears it anyway, for the tier-0 paths
    # that replay one built player across fights.
    if (card.enchant_first_play_effects
            and not card.enchant_played_this_combat):
        _resolve_effects(state, card.enchant_first_play_effects, card)
    # Guarded rather than set unconditionally: a card with no first-play
    # rider must come out of a play byte-identical to the way it went in,
    # or two value-equal twins (state.remove_instance's whole warning)
    # would stop being twins the moment one of them is played.
    if card.enchant_first_play_damage or card.enchant_first_play_effects:
        card.enchant_played_this_combat = True
    # (C.KOKOMI_OVERHAUL). Core pass, TREATISE: a card with a Plan
    # line played NORMALLY -- a write returned above, before any of this.
    kokomi_plan.note_face_up_plan_card(state, card)


def flat_attack_bonus(state: CombatState, card: Card, cost: int, *,
                      valuation: bool = False) -> int:
    """The per-card flat bonus every attack card carries, as a PURE READ.

    Bennett's next_attack_up, Nicole's celestial_gift, the Bennett-burst
    attack_up_this_turn window, Spark Knight Style's zero-cost rider,
    Rapturous Applause's Fanfare term, and Kokomi's Ceremonial Garment
    Charge read all land here — flat, folded in before strength/vulnerable.

    Consumes nothing, so the pilot may call it to price a play it has not
    made (v0.4 W1: the pilot previously saw NONE of these, so it valued every
    attack at its printed number and played straight through its own buff
    windows -- most visibly the Garment, where a priest-median bank is worth
    more than most cards' printed damage). The consuming pop and the
    KNOB_READS tick stay at the real call site.

    EB-253, and the reason this line no longer reads "touches no telemetry":
    it did. Rapturous Applause's Fanfare term files a `fanfare_read` on the
    way past, so the pilot's price for every attack in hand landed in the
    LIVE-meter instrument as if the player had played them all. The fix is
    EB-242's, one instrument over -- `valuation=True` DECLARES the call an
    estimate and tallies nothing, and the default stays the resolve path so a
    new resolve site has to opt out on purpose rather than by omission.
    """
    if card.type != "attack":
        return 0
    p = state.player
    # celestial_gift LEFT this sum at the 2026-07-26 red-pen redesign. It used
    # to be a static flat +N to attacks; it is now a per-turn STRENGTH ratchet,
    # and Strength is applied as a real power (powers.deal_damage folds it in
    # after this read). Leaving it here as well would have paid the buff twice
    # -- once as flat damage, once as Strength -- which is exactly the
    # double-count class the AoE-blindness finding warned about.
    bonus = (p.powers.get("next_attack_up", 0)
             + p.powers.get("attack_up_this_turn", 0))
    # THE MONDSTADT COMPANION OVERHAUL'S THREE ATTACK RIDERS.
    # Flat, and folded in exactly where `next_attack_up` is folded in --
    # they say the same English ("deals N more") and a second summing site
    # is how two riders come to disagree about whether Strength lands
    # before or after them. All three STACK with each other and with the
    # shipped pair: three separate sentences, three separate numbers, and
    # nothing on any of the three faces says otherwise.
    #
    #   mc_passion_overload   Bennett -- one Attack, consumed on it
    #   mc_lightning_fang     Razor   -- every Attack, 2 turns
    #   mc_swirl_charge       Varka   -- one Attack, banked per Swirl
    #
    # `mc_lightning_fang`'s stack is TURNS REMAINING, not damage, so its
    # contribution is the constant rather than the stack; the other two
    # hold their own printed number, so a second copy pays twice.
    bonus += p.powers.get("mc_passion_overload", 0)
    bonus += p.powers.get("mc_swirl_charge", 0)
    if p.powers.get("mc_lightning_fang", 0):
        bonus += C.MC_LIGHTNING_FANG_BONUS
    # THE INAZUMA ARM'S TWO, on the same terms and in the same sum:
    #   mi_crowfeather  Sara  -- one Attack, its stack IS the number
    #   mi_kyouka       Ayato -- every Attack, 2 turns, so the stack is
    #                            TURNS and the constant is the number
    # Sara's Tengu Stormcall is deliberately NOT here: it pays into the
    # shipped `attack_up_this_turn` at the start of the turn it names, and
    # that key is already the first term of this sum.
    bonus += p.powers.get("mi_crowfeather", 0)
    if p.powers.get("mi_kyouka", 0):
        bonus += C.MI_KYOUKA_BONUS
    if cost == 0:
        bonus += p.powers.get("zero_cost_attacks_up", 0)
    # FURINA'S HIGH STAKES (the pool to 75): "While you are within 5 HP of
    # your Drain line, your Attacks deal 4 more damage" [6]. A pure read of
    # her HP against the line; 0 for anyone else. The C# twin is
    # `HighStakesPower.ModifyDamageAdditive`.
    bonus += furina_stage.high_stakes_bonus(state)
    # Rapturous Applause: attacks +N per 10 Fanfare ("stacks grant flat
    # power bonuses", kickoff §4). Reads the pool, spends nothing.
    n = p.powers.get("fanfare_attack_per10", 0)
    if n:
        if not valuation:                          # EB-253, see the docstring
            resources.note_fanfare_read(state, "attack_power")
        bonus += n * (resources.readable(p) // 10)
    # THE SAME CLAUSE AT THE REFRAME ARM'S GRANULARITY (2026-09-07). The arm's
    # meter ranges 0-15 where the shipped one ranges 20-30, so the arm copy of
    # this rider halves the THRESHOLD and keeps the payout: 1 per 5 Fanfare is
    # the shipped 1 per 10 read on a meter half the size, and not a bigger
    # number on the same one.
    n5 = p.powers.get("fanfare_attack_per5", 0)
    if n5:
        if not valuation:                          # EB-253, see the docstring
            resources.note_fanfare_read(state, "attack_power")
        bonus += n5 * (resources.readable(p) // 5)
    # VARKA (`varka_oath.attack_bonus`): Stormward Stance, on his Anemo
    # Attacks while his current element's Oath is at the bar. 0 for anyone
    # else.
    bonus += varka_oath.attack_bonus(state, card)
    return bonus


# --- player-side power triggers, called from the combat loop ---

def player_turn_start_triggers(state: CombatState) -> None:
    p = state.player
    n = p.powers.pop("block_next_turn", 0)              # Charlotte
    if n:
        # Deliberately raw: this payout predates both block funnels and
        # neither may touch it (Dexterity must not scale power block; the
        # power that banked it has expired by now). A future block-gain hook
        # will not see this gain unless it is rerouted on purpose.
        p.block += n
        state.emit("block", amount=n)
    # EB-83 -- the DURATION-SCOPED twin of the pop above, at the same seam and
    # deliberately adjacent to it: both are delayed Block landing after the
    # turn-start block reset, and splitting them across the function is how one
    # of them acquires a different set of hooks by accident.
    #
    # PAY, THEN TICK, THEN EXPIRE, PER INSTANCE. An instance applied on turn N
    # (during the player's own turn, after this function has already run for
    # turn N) with `turns: 2` pays at the start of N+1 and N+2 and is gone
    # before N+3 -- exactly "the start of your next 2 turns", and it never pays
    # on the turn it was played.
    #
    # R247 ([USER], 2026-09-03) made the instances INDEPENDENT, so the loop is
    # over the list rather than over one summed amount: every live instance
    # pays its own Block and ticks its own clock, and a short one expiring does
    # not shorten or lengthen a long one standing beside it. `powers[name]` is
    # re-derived from the survivors rather than decremented, because it is a
    # summary of the list and not a second copy of the truth.
    #
    # ONE `block` ROW PER INSTANCE, not one summed row: the game pays each
    # `ToricToughnessPower` through its own `CreatureCmd.GainBlock` in its own
    # `AfterBlockCleared`, and a reader counting Block gains should see what
    # the game does.
    #
    # THE PAYOUT IS RAW, sharing `block_next_turn`'s argument above verbatim
    # rather than restating it: neither block funnel may touch a gain the card
    # that banked it is no longer the source of. The two delayed-Block ops must
    # not drift, so they get one behaviour and it is written once.
    instances = p.timed_power_amounts.get(BLOCK_AT_TURN_START) or []
    if instances:
        for amount, _turns in instances:
            if amount:
                p.block += amount
                state.emit("block", amount=amount)
        live = [[amount, turns - 1] for amount, turns in instances
                if turns - 1 > 0]
        if live:
            p.timed_power_amounts[BLOCK_AT_TURN_START] = live
            p.powers[BLOCK_AT_TURN_START] = max(t for _, t in live)
        else:
            # BOTH entries leave together. The sidecar outliving the power is a
            # stale instance list waiting for the next application to append to.
            p.powers.pop(BLOCK_AT_TURN_START, None)
            p.timed_power_amounts.pop(BLOCK_AT_TURN_START, None)
    # Nicole -- REDESIGNED 2026-07-26 (red-pen, item 4). Was "+N flat attack
    # damage, and 4 Block each turn"; is now "gain N Strength and 4 Block each
    # turn". The rationale on the record: a 2-cost Power must clear a high bar
    # (Silent's damage-to-Weak at 1, Ironclad's +4-Strength-per-turn at 3,
    # Defect's double-first-card at 3), and SCALING Strength is what earns the
    # slot where a static flat bonus did not.
    #
    # The power's amount is Strength PER TURN, not a total -- it ratchets, so
    # a deck holding it wants the fight to go long. Block stays a constant
    # because nothing on the card scales it and the upgrade is cost-only.
    n = p.powers.get("celestial_gift", 0)
    if n:
        powers.apply_power(state, p, "strength", n, applier=p)
        p.block += C.CELESTIAL_GIFT_BLOCK
    # Arlecchino -- Strength half. Routed through powers.apply_power, NOT
    # written into p.powers directly, so Kokomi's LAW 3 chokepoint sees it and
    # converts it to Charge. That interaction is meant to fall out of the
    # standard path rather than be special-cased anywhere.
    n = p.powers.get("masque_red_death", 0)
    if n:
        powers.apply_power(state, p, "strength", n, applier=p)
    # Neuvillette -- co-op notes pick 4 (2026-10-02): "At the start of your
    # turn, apply Hydro to a random enemy." One per copy (the amount counts
    # copies; the upgrade is a cost cut), through `resolve_hit` like the
    # apply_aura op, so it reacts and credits. C# twin:
    # `AncientSeaAuthorityPower.AfterPlayerTurnStart`.
    for _ in range(p.powers.get("ancient_sea_authority", 0)):
        if not state.living_enemies:
            break
        enemy = state.rng.choice(list(state.living_enemies))
        reactions.resolve_hit(state, enemy, "hydro", 0,
                              "ancient_sea_authority")
    n = p.powers.get("spark_per_turn", 0)               # Endless Fireworks
    if n:
        gain_sparks(state, n, source="power:endless_fireworks/turn_start")
    n = p.powers.get("bomb_and_spark_per_turn", 0)      # Playtime Forever
    for _ in range(n):
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            enemy.bombs.append(Bomb(damage=C.PLAYTIME_BOMB_DAMAGE,
                                    turn_placed=state.turn))
            state.emit("bomb_placed", target=enemy.name,
                       damage=C.PLAYTIME_BOMB_DAMAGE)
        gain_sparks(state, 1, source="power:playtime_forever/turn_start")
    companion_overhaul_turn_start(state)


def companion_overhaul_turn_start(state: CombatState) -> None:
    """THE MONDSTADT COMPANION OVERHAUL's start-of-turn block (`C.COMPANION_OVERHAUL`). Three powers, and no other engine site reads them.

    A SEPARATE FUNCTION, called from the tail of
    `player_turn_start_triggers`, for two reasons that agree. It keeps a
    quarantined arm's whole start-of-turn behaviour in one greppable place, the
    way the C# side keeps its end-of-turn behaviour in one listener; and it
    makes "does the arm run at all" a single call a reader can follow, rather
    than three branches interleaved with the shipped income group.

    AFTER the shipped block, not before. The two overhaul powers that grant
    Block are new income, and every existing income power already sits after
    the upkeep by the EB-2 ruling recorded above -- inserting a fourth income
    source in the middle of that group would be re-opening a settled race.

    C# twins: `SignatureMixPower` and `RevelationPower`, each overriding
    `AfterPlayerTurnStart`. The two are COMMUTATIVE -- neither reads a value
    the other writes -- which is why the C# side lets them keep their own
    broadcast while the end-of-turn six get one listener. (Mona's omen was a
    third until 2026-10-03, when her card moved to Vulnerable on play.)
    """
    p = state.player
    # Diona, Signature Mix -- stacks are TURNS REMAINING (the `oz_summon`
    # grammar). PAY, THEN TICK, THEN EXPIRE, exactly as `block_at_turn_start`
    # above does: applied on turn N during the player's own turn, `turns: 2`
    # pays at the start of N+1 and N+2 and is gone before N+3.
    n = p.powers.get("mc_signature_mix", 0)
    if n:
        # RAW, sharing `block_next_turn`'s argument verbatim: neither block
        # funnel may touch a gain the card that banked it is no longer the
        # source of.
        p.block += C.MC_SIGNATURE_MIX_BLOCK
        state.emit("block", amount=C.MC_SIGNATURE_MIX_BLOCK)
        if n > 1:
            p.powers["mc_signature_mix"] = n - 1
        else:
            del p.powers["mc_signature_mix"]
    # Nicole, Revelation Uncreated Light -- PERMANENT, stacks are COPIES. The
    # Strength half reads the latch written at the end of the previous turn
    # (see `Player.mc_held_block_at_turn_end`); on the turn the card is played
    # the latch is False, because there was no previous turn to hold Block
    # through.
    n = p.powers.get("mc_revelation", 0)
    if n:
        blk = C.MC_REVELATION_BLOCK * n
        p.block += blk
        state.emit("block", amount=blk)
        if p.mc_held_block_at_turn_end:
            powers.apply_power(state, p, "strength",
                               C.MC_REVELATION_STRENGTH * n, applier=p)
    # ---- the second wave's two start-of-turn readers ----------------------
    # Diona, Icy Paws -- CLAMP, not a payout. `mc_icy_paws` marks how much of
    # the standing Block came from that card; Block is cleared at the top of
    # the player's turn (`combat._player_turn`, before this runs), so the mark
    # is clamped to what is actually left. Written as a clamp rather than as a
    # clear beside the block reset so it stays correct under Barricade, which
    # suppresses the reset: the mark then survives exactly as far as the Block
    # it names does.
    n = p.powers.get("mc_icy_paws", 0)
    if n:
        left = min(n, p.block)
        if left > 0:
            p.powers["mc_icy_paws"] = left
        else:
            del p.powers["mc_icy_paws"]
    # Barbara, Melody Loop -- LAST, and hosted on the ENEMY. "For 3 turns, at
    # the start of your turn apply Hydro to target enemy": the target is a
    # CHOSEN body, and a power that lives ON that body needs no machinery to
    # remember which one it was. Stacks are TURNS REMAINING; FIRE, THEN TICK.
    #
    # LAST BECAUSE IT IS THE ONE THAT APPLIES AN ELEMENT, and the two above
    # it do not: they grant the player Block or Strength, so neither can be
    # changed by an aura landing or a reaction firing. Two Melody Loops cannot disturb each other either
    # -- each applies to its own host and nothing else -- which is why the C#
    # twin is allowed to keep its own `AfterPlayerTurnStart` broadcast beside
    # the other three rather than joining the end-of-turn listener.
    for enemy in list(state.living_enemies):
        n = enemy.powers.get("mc_melody_loop", 0)
        if not n:
            continue
        reactions.resolve_hit(state, enemy, "hydro", 0, "mc_melody_loop")
        if n > 1:
            enemy.powers["mc_melody_loop"] = n - 1
        else:
            del enemy.powers["mc_melody_loop"]
    # Durin, Principle of Purity (AoE trim, 2026-10-03): "At the start of your
    # turn, deal 4 Pyro damage to a random enemy." PERMANENT, the stack is the
    # damage (copies add into one hit). After Melody Loop, the other element.
    n = p.powers.get("mc_purity_strike", 0)
    if n and state.living_enemies:
        enemy = state.rng.choice(state.living_enemies)
        deal_damage_to_enemy(state, enemy, n, element="pyro",
                             source="companion")
    inazuma_overhaul_turn_start(state)
    # ---- and KLEE'S COVEN PERSONALS, last (R236) --------------
    # Qiqi's Herald applies Cryo, which can resolve a reaction, so it runs
    # after the overhaul's own start-of-turn powers in one written-down
    # sequence (Mona's omen, which Vulnerabled the board here, left
    # 2026-10-03). `tier0.engine.companion_coven`.
    companion_coven.turn_start(state)
    # Jean's Lion's Fang, Fair Protector, after it -- Grounded's shape with a
    # card on it. LAST, and commutative with everything above: it grants Block
    # and a draw and reads only the explosion counter, which nothing here
    # writes.
    lions_fang.turn_start(state)
    _companion_overhaul_turn_start_late(state)


def _companion_overhaul_turn_start_late(state: CombatState) -> None:
    """THE START-OF-TURN TAIL, after every other start-of-turn block there is.

    `EB-470` moved Lisa's Lightning Rose here from the end of the turn: fired
    at the end of the player's turn its Vulnerable was unobservable, because
    the stack falls off at the end of the enemy's turn and no player card ever
    saw it (Klee r15 run 2, three fights, never a stack on any board). Fired
    here the stack is live for every play the player then makes.

    LAST, AND WRITTEN DOWN, because it is not commutative with what runs above
    it: the volley draws a target from `state.rng` and puts Electro on a body
    that may already carry an aura, Barbara's Melody Loop lays Hydro and Qiqi's Herald lays Cryo. The C# twin
    is `CompanionOverhaulTurnEnd.AfterPlayerTurnStartLate`, and the 0.111.0
    hook contract runs `AfterPlayerTurnStartLate` strictly after every
    `AfterPlayerTurnStart` -- which is exactly this position, and the only
    position the two engines can both name without a second ordered listener.
    """
    p = state.player
    # Lisa, Lightning Rose -- stacks are TURNS REMAINING. The Vulnerable lands
    # on the SAME enemy the damage hit and AFTER it: the printed sentence is
    # one clause about one enemy, and debuffing first would amplify the card's
    # own hit by 50% on a card that does not say so.
    if p.powers.get("mc_lightning_rose", 0):
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            deal_damage_to_enemy(state, enemy, C.MC_LIGHTNING_ROSE_DMG,
                                 element="electro", source="companion")
            if enemy.hp > 0:
                powers.apply_power(state, enemy, "vulnerable",
                                   C.MC_LIGHTNING_ROSE_VULN, applier=p)
        p.powers["mc_lightning_rose"] -= 1
        if p.powers["mc_lightning_rose"] <= 0:
            del p.powers["mc_lightning_rose"]


def inazuma_overhaul_turn_start(state: CombatState) -> None:
    """THE INAZUMA companion overhaul's start-of-turn block (`C.COMPANION_OVERHAUL`). Three readers, and no other engine site reads them.

    AFTER the Mondstadt block and not interleaved with it, for the reason that
    block sits after the shipped income group: a second nation's rewrites are
    new income and a settled order is not reopened to make room for them. The
    C# twin is `InazumaCompanionTurnStart`, which walks the same three in the
    same order.

        mi_blazing_barrier  Thoma   -- the Block mark, CLAMPED (not a payout)
        mi_naptime          Sayu    -- the deferred draw
        mi_stormcall        Sara    -- next turn's blanket Attack rider
        mi_surprise_dispatch Kirara -- the parcel, LAST because it is the only
                                       one that deals damage
    """
    p = state.player
    # Thoma, Blazing Barrier -- the same CLAMP Diona's paws take above, and for
    # the identical reason: `mi_blazing_barrier` marks how much of the standing
    # Block that card put there, Block is cleared at the top of the turn, and a
    # mark outliving the Block it names would thicken a shield that is gone.
    n = p.powers.get("mi_blazing_barrier", 0)
    if n:
        left = min(n, p.block)
        if left > 0:
            p.powers["mi_blazing_barrier"] = left
        else:
            del p.powers["mi_blazing_barrier"]
    # Sayu, Naptime -- "At the start of your next turn, draw 2 if you played no
    # Attacks this turn." The CONDITION is about the turn the card was played,
    # so it is answered at the end of that turn (`inazuma_overhaul_turn_end`
    # deletes the promise when an Attack was played); anything still standing
    # here has already earned its draw. Stacks are CARDS, so two Naptimes draw
    # four, and the promise is popped WHOLE -- it is kept once, not ticked.
    n = p.powers.pop("mi_naptime", 0)
    if n:
        state.draw(n)
        state.emit("extra_draw", amount=n)   # A5 velocity accounting, as _op_draw
    # Kujou Sara, Tengu Stormcall -- "Next turn, your Attacks deal 5 more."
    # POPPED WHOLE and paid into the shipped `attack_up_this_turn`, which is
    # already summed by `flat_attack_bonus` and already cleared at the end of
    # the player's turn -- so "next turn" needs no clock of its own and the
    # rider cannot outlive the turn it was promised for. Stacks are COPIES.
    n = p.powers.pop("mi_stormcall", 0)
    if n:
        powers.apply_power(state, p, "attack_up_this_turn",
                           C.MI_STORMCALL_BONUS * n, applier=p)
    # Kirara, Surprise Dispatch -- "Next turn, deal 10 damage to a random
    # enemy." LAST in this block because it is the only one of the four that
    # can kill something, so every reader above it sees the same board it would
    # have seen alone. The damage carries NO element, because the card names
    # none (Albedo's Solar Isotoma made the same call), and it runs the
    # pipeline like every other power-sourced hit (NC-1).
    for _ in range(p.powers.pop("mi_surprise_dispatch", 0)):
        if not state.living_enemies:
            break
        enemy = state.rng.choice(state.living_enemies)
        deal_damage_to_enemy(state, enemy, C.MI_SURPRISE_DISPATCH_DMG,
                             element=None, source="companion")


def _exhaust_autoplay_sweep(state: CombatState) -> None:
    """HowlFromBeyond: Hook.AfterAutoPostPlayPhaseEntered, which the game's
    CombatManager invokes ONCE per player turn while ending the turn
    (Phase = AutoPostPlay, immediately before BeforeTurnEnd). Howl's
    override fires when the card is sitting in the player's EXHAUST pile
    and auto-plays it for free; it carries no Exhaust keyword, so
    GetResultPileTypeForCardPlay sends it to DISCARD afterwards.

    ONE-SHOT, NOT A LOOP. The flagged cards are snapshotted before any of
    them plays, and each is pulled out of the exhaust pile first -- so a
    card that re-exhausts itself cannot trigger again this sweep. The loop
    reading is the obvious wrong implementation; this must stay pinned by a
    test.

    Only reachable via another card exhausting Howl (Brand, BurningPact,
    TrueGrit+, Stoke, Havoc's forceExhaust). Zero flagged cards is the
    universal case -- Klee and Furina never enter this loop body.
    """
    p = state.player
    flagged = [c for c in p.exhaust_pile if c.on_exhaust_autoplay]
    for c in flagged:
        if state.over or not p.alive:
            return
        remove_instance(p.exhaust_pile, c)
        _free_play(state, c, force_exhaust=False)


def player_turn_end_triggers(state: CombatState) -> None:
    p = state.player
    # Arlecchino -- Bond of Life half, once per turn, clamped at zero.
    #
    # WHY END-OF-TURN AND NOT AT THE MOMENT BLOCK IS GAINED. The card reads
    # "the first 5 Block you gain each turn does not count", and eating it at
    # the gain site would need a funnel that does not exist: Block is added at
    # ~15 places, and modify_block_gained deliberately covers CARD block only
    # (its docstring: passive/power Block from Metallicize, Crystallize and
    # Solar Isotoma is intentionally exempt from Frail). Deducting once at turn
    # end is ARITHMETICALLY IDENTICAL -- eating the first 5 leaves
    # max(0, gained - 5), and so does subtracting 5 at the end and clamping --
    # and it is universal, so Navia's or Crystallize's Block cannot dodge the
    # Bond the way a card-only funnel would let it.
    #
    # The one case where the two differ is a card that READS current Block
    # mid-turn: the `player_block` formula token (Body Slam). That card is
    # reference-pool only and the refs take no companions
    # (rewards.NO_COMPANION_CHARACTERS), so the divergence is unreachable
    # today. Recorded rather than assumed away -- if a roster character ever
    # gets a Block-reading card, this is the note that says to move the
    # deduction to a real gain funnel.
    if p.powers.get("masque_red_death", 0):
        paid = min(p.block, C.MASQUE_BOND_BLOCK)
        p.block -= paid
        state.emit("bond_of_life", amount=paid, owed=C.MASQUE_BOND_BLOCK)
    # Runs FIRST: the game's AutoPostPlay phase lands after the player's
    # plays and before turn end, so the free play resolves ahead of the
    # other end-of-turn triggers and well ahead of the enemy turn.
    _exhaust_autoplay_sweep(state)
    if p.powers.get("sparks_n_splash", 0):              # the Burst
        for _ in range(C.SPARKS_N_SPLASH_HITS):
            if not state.living_enemies:
                break
            enemy = state.rng.choice(state.living_enemies)
            deal_damage_to_enemy(state, enemy, C.SPARKS_N_SPLASH_HIT_DMG,
                                 element="pyro", source="burst")
        p.powers["sparks_n_splash"] -= 1
    if p.powers.get("oz_summon", 0):                    # Fischl
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            deal_damage_to_enemy(state, enemy, C.OZ_DMG,
                                 element="electro", source="companion")
        p.powers["oz_summon"] -= 1
    if p.powers.get("witchs_flame", 0):                 # Durin (permanent)
        # Turn Klee's Pyro saturation into a setup window instead of adding
        # still more Pyro. Each consumed aura pays damage + Burst Energy, then
        # leaves the enemy clear for Hydro/Cryo to establish the next reaction.
        damage = p.powers["witchs_flame"]
        for enemy in list(state.living_enemies):
            if enemy.aura != "pyro":
                continue
            enemy.aura = None
            enemy.aura_turns_left = 0
            deal_damage_to_enemy(state, enemy, damage,
                                 element=None, source="companion")
            state.emit("witchs_flame_consumed", target=enemy.name,
                       burst_energy=C.WITCHS_FLAME_BURST)
    if p.powers.get("solar_isotoma", 0):                # Albedo, 3 turns
        p.powers["solar_isotoma"] -= 1
    p.powers.pop("attack_up_this_turn", None)           # Bennett burst
    companion_overhaul_turn_end(state)


def companion_overhaul_turn_end(state: CombatState) -> None:
    """THE MONDSTADT COMPANION OVERHAUL's end-of-turn block (`C.COMPANION_OVERHAUL`). Five powers and one latch, in this order
    (`EB-470` moved the sixth, Lisa's Lightning Rose, to the start of the
    turn -- see `companion_overhaul_turn_start`):

        mc_glacial_waltz     Cryo volley, one target
        mc_oz                Electro volley, one target per stack
        mc_grand_ode         Anemo Swirl, every enemy
        mc_dandelion_breeze  Anemo Swirl on the aura-bearer, then Block
        mc_isotoma_bloom     unelemented damage on the aura-bearer, then Block
        mc_revelation        the LATCH, last

    THE ORDER IS LAW, and the C# twin (`CompanionOverhaulTurnEnd`) walks the
    same list. Four of the five put an ELEMENT on an enemy that may already
    carry one, so the order decides which reactions fire; two of them draw
    from `state.rng`, so it also decides every later roll in the fight. That
    is EB-19/races-c, and this arm answers it the same way the shipped chain
    does: one sequence, written down once per engine.

    THE LATCH IS LAST because two of the five GRANT Block, and Nicole's
    question is whether the player ENDED the turn holding any.

    AFTER the shipped chain, not interleaved with it. This block is appended
    to `player_turn_end_triggers`, and the C# twin rides `AfterSideTurnEnd`
    while `TurnEndSequencer` owns `BeforeSideTurnEnd` -- so the two engines
    put this arm in the same place relative to Klee's Burst volley and
    Kokomi's pulse, which are the shipped tenants a flagged run can still hold.
    """
    p = state.player

    # Kaeya, Glacial Waltz -- stacks are TURNS REMAINING. FIRE, THEN TICK (the
    # AuraPower own-decay idiom the shipped volleys use), so a stack count
    # still means "this many more turns, including this one".
    if p.powers.get("mc_glacial_waltz", 0):
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            deal_damage_to_enemy(state, enemy, C.MC_GLACIAL_WALTZ_DMG,
                                 element="cryo", source="companion")
        p.powers["mc_glacial_waltz"] -= 1
        if p.powers["mc_glacial_waltz"] <= 0:
            del p.powers["mc_glacial_waltz"]

    # Fischl, Oz at Your Side -- PERMANENT, stacks are COPIES. No tick: the
    # workshop's sec.1 rule is that a Power has no turn limit, and its sec.3
    # note says so about this card by name ("a Power cannot be reapplied, so
    # Oz stays out"). Re-rolled per volley, because a volley can kill.
    for _ in range(p.powers.get("mc_oz", 0)):
        if not state.living_enemies:
            break
        enemy = state.rng.choice(state.living_enemies)
        deal_damage_to_enemy(state, enemy, C.MC_OZ_DMG,
                             element="electro", source="companion")

    # Lisa, Lightning Rose fired HERE, third, until `EB-470`. It now fires at
    # the START of the player's turn, at the tail of
    # `companion_overhaul_turn_start`, so its Vulnerable is live for the plays
    # that follow it.

    # Venti, Wind's Grand Ode -- stacks are TURNS REMAINING. Swirl is a
    # damage-less Anemo application, which is exactly what the `swirl` op is,
    # so the two cannot mean different things.
    if p.powers.get("mc_grand_ode", 0):
        for enemy in list(state.living_enemies):
            reactions.resolve_hit(state, enemy, "anemo", 0, "swirl_op")
        p.powers["mc_grand_ode"] -= 1
        if p.powers["mc_grand_ode"] <= 0:
            del p.powers["mc_grand_ode"]

    # Jean, Dandelion Breeze -- PERMANENT, stacks are COPIES. The Block is
    # paid whether or not a Swirl landed: the sentence is two clauses joined
    # by a bare "and", not a consequence, and that is also the reading that
    # keeps a Rare Power from being dead against an aura-less board.
    for _ in range(p.powers.get("mc_dandelion_breeze", 0)):
        target = _mc_most_auras(state)
        if target is not None:
            reactions.resolve_hit(state, target, "anemo", 0, "swirl_op")
        p.block += C.MC_DANDELION_BREEZE_BLOCK
        state.emit("block", amount=C.MC_DANDELION_BREEZE_BLOCK)

    # Albedo, Solar Isotoma -- PERMANENT, stacks are COPIES. BOTH halves are
    # inside the condition ("if any enemy has an aura, deal 8 damage to that
    # enemy AND gain 4 Block" is one guarded sentence, unlike Jean's), so no
    # aura on the board means no damage and no Block. The damage carries NO
    # element, because the card's text names none, and it runs the pipeline
    # (NC-1: power-sourced damage scales with the player) while the Block
    # stays raw (NC-11).
    for _ in range(p.powers.get("mc_isotoma_bloom", 0)):
        target = _mc_most_auras(state)
        if target is None:
            break
        deal_damage_to_enemy(state, target, C.MC_ISOTOMA_DMG,
                             element=None, source="companion")
        p.block += C.MC_ISOTOMA_BLOCK
        state.emit("block", amount=C.MC_ISOTOMA_BLOCK)

    # ---- the second wave's four end-of-turn readers, still before the latch -
    # THE LATCH STAYS LAST, which is why these go here rather than after it:
    # none of the four grants the player Block, so inserting them changes no
    # answer, and Nicole's question is still asked of the board the player
    # actually ended the turn holding.
    #
    # Eula, Glacial Illumination -- the counting blade, hosted on the ENEMY the
    # card chose. Stacks are TURNS REMAINING; TICK, THEN FIRE AT ZERO, which is
    # the opposite order from the volleys above and is what the printed
    # sentence says: "for 2 turns it counts your Attacks; THEN it deals 8 plus
    # 5 per Attack counted". Placed on your turn with 2 turns, it counts this
    # turn's Attacks and next turn's, and pays at the end of the second.
    #
    # THE BLADE'S DAMAGE CARRIES NO ELEMENT, because the card's text names
    # none -- Albedo's Solar Isotoma above it made the same call for the same
    # reason. It runs the pipeline (NC-1: power-sourced damage scales with the
    # player) like every other power-sourced hit in this block.
    for enemy in list(state.living_enemies):
        n = enemy.powers.get("mc_lightfall_sword", 0)
        if not n:
            continue
        if n > 1:
            enemy.powers["mc_lightfall_sword"] = n - 1
            continue
        del enemy.powers["mc_lightfall_sword"]
        deal_damage_to_enemy(
            state, enemy,
            C.MC_LIGHTFALL_BASE
            + C.MC_LIGHTFALL_PER_ATTACK * enemy.mc_lightfall_tally,
            element=None, source="companion")
        enemy.mc_lightfall_tally = 0
    # Dahlia, Favonian Favor and Bennett, Passion Overload -- both say THIS
    # TURN, and both are therefore popped whole here whether or not they ever
    # paid. Bennett's is the one that can also be spent early: an Attack
    # consumes it at `companion_overhaul_card_start`, and this is the other
    # end of the same promise.
    p.powers.pop("mc_favonian_favor", None)
    p.powers.pop("mc_passion_overload", None)
    # The Hexerei stand-ins' two this-turn windows close on the same line and
    # for the same reading. `tier0.engine.companion_hexerei`.
    companion_hexerei.roll_turn_end(state)
    # Razor, Lightning Fang -- stacks are TURNS REMAINING, and unlike the
    # volleys above it fires nothing here: what it does happens on every Attack
    # the player makes (`flat_attack_bonus`, `_element_for`), so end of turn is
    # only where the clock runs down.
    if p.powers.get("mc_lightning_fang", 0):
        p.powers["mc_lightning_fang"] -= 1
        if p.powers["mc_lightning_fang"] <= 0:
            del p.powers["mc_lightning_fang"]
    # ---- THE INAZUMA ARM'S end-of-turn block, still before the latch --------
    # Same argument as the four second-wave readers above: none of it grants
    # the player Block except Shinobu's ring, and that one is INSIDE this
    # block rather than after the latch precisely so Nicole's question is
    # asked of the board the player really ended the turn holding.
    inazuma_overhaul_turn_end(state)
    # ---- KLEE'S COVEN PERSONALS, still before the latch (R236) -------------
    # Yaoyao's Yuegui draws a target from `state.rng`, so its position decides
    # every later roll; it grants no Block, so it cannot change the answer
    # Nicole's latch is about to record. `tier0.engine.companion_coven`.
    companion_coven.turn_end(state)
    # Nicole's latch, LAST. Written unconditionally rather than only while she
    # is on the board: a card drafted mid-fight must not read a stale answer
    # from the turn before it existed, and the field is per-combat anyway.
    p.mc_held_block_at_turn_end = p.block > 0


def inazuma_overhaul_turn_end(state: CombatState) -> None:
    """THE INAZUMA companion overhaul's end-of-turn block (`C.COMPANION_OVERHAUL`). Eight powers, in this order:

        mi_juuga              Gorou   -- Geo volley, one target
        mi_daruma             Sayu    -- the HP-bar split: a volley or Block
        mi_sanctifying_ring   Shinobu -- Electro to ALL, then Block
        mi_sesshou_sakura     Yae     -- one Electro volley per Sakura
        mi_soumetsu           Ayaka   -- Cryo to ALL, then the finale at zero
        mi_kyouka             Ayato   -- the clock, and the 12 it ends on
        mi_tamoto             Chiori  -- Geo volley, ignoring Block
        mi_crimson_ooyoroi    Thoma   -- the clock only; it fires on Attacks
        mi_war_banner         Gorou   -- the clock, and the Dexterity it takes
        mi_naptime            Sayu    -- the promise, kept or broken
        mi_crowfeather        Sara    -- "this turn", popped whole

    THE ORDER IS LAW, exactly as it is for the Mondstadt block this one is
    appended to, and for the same two reasons: five of these put an ELEMENT on
    an enemy that may already carry one, so the order decides which reactions
    fire, and four draw from `state.rng`, so it decides every later roll in the
    fight. The C# twin (`CompanionOverhaulTurnEnd`) walks the same list.

    IN THE WORKSHOP'S sec.3 CHARACTER ORDER, with the three clock-only entries
    last: a tick and two removals cannot change an outcome by running in a
    different order, so they are grouped rather than interleaved.
    """
    p = state.player

    # Gorou, Juuga: Forward Unto Victory -- stacks are TURNS REMAINING. FIRE,
    # THEN TICK, the idiom every volley in this arm uses.
    if p.powers.get("mi_juuga", 0):
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            deal_damage_to_enemy(state, enemy, C.MI_JUUGA_DMG,
                                 element="geo", source="companion")
        _mi_tick(p, "mi_juuga")

    # Sayu, Muji-Muji Daruma -- the nation's shape on a card: "if you are above
    # 70% HP deal 6 damage to a random enemy; otherwise gain 6 Block". The bar
    # is read HERE, at the moment the Daruma acts, not when it was summoned --
    # "if you are" is present tense and the whole point of the split is that it
    # follows the fight. The damage carries NO element: the card names none.
    if p.powers.get("mi_daruma", 0):
        if _mi_above_pct(p, 70):
            if state.living_enemies:
                enemy = state.rng.choice(state.living_enemies)
                deal_damage_to_enemy(state, enemy, C.MI_DARUMA_DMG,
                                     element=None, source="companion")
        else:
            p.block += C.MI_DARUMA_BLOCK
            state.emit("block", amount=C.MI_DARUMA_BLOCK)
        _mi_tick(p, "mi_daruma")

    # Kuki Shinobu, Sanctifying Ring -- stacks are TURNS REMAINING. The Block
    # is paid whether or not the ring found a body, because the printed
    # sentence joins the two clauses with a bare "and" (Jean's Dandelion Breeze
    # made the same reading for the same construction).
    if p.powers.get("mi_sanctifying_ring", 0):
        for enemy in list(state.living_enemies):
            deal_damage_to_enemy(state, enemy, C.MI_SANCTIFYING_RING_DMG,
                                 element="electro", source="companion")
        p.block += C.MI_SANCTIFYING_RING_BLOCK          # RAW (NC-11)
        state.emit("block", amount=C.MI_SANCTIFYING_RING_BLOCK)
        _mi_tick(p, "mi_sanctifying_ring")

    # Yae Miko, Sesshou Sakura -- stacks are SAKURA, capped at 3 by the card
    # ("Up to 3"), and PERMANENT: the card places a totem, not a timer.
    #
    # "EACH SAKURA YOU PLACE WHILE ONE IS OUT DEALS 3 MORE" is read as a
    # statement about the SAKURA BEING PLACED, which is what its subject says:
    # the first one out deals 4 and every later one deals 7, whether one or two
    # were already standing. So the volleys are 4, 7, 7 -- and the order in
    # which they are fired is the placement order, which is the only order a
    # counter can hold. Each is its own hit at its own random target, because
    # each Sakura is its own totem; "plus your Strength" is what the shared
    # pipeline already does to every power-sourced hit in this arm (NC-1), so
    # the clause is printed rather than implemented.
    #
    # "UP TO 3" IS READ AT THE FIRE, not at the placement, and both engines
    # read it here: a fourth Sakura can be placed and simply never fires. That
    # is the conservative direction (R212's one-way rule -- the doubt pays
    # LESS), and it is the reading that needs no stack cap in either engine.
    for i in range(min(p.powers.get("mi_sesshou_sakura", 0), C.MI_SAKURA_CAP)):
        if not state.living_enemies:
            break
        enemy = state.rng.choice(state.living_enemies)
        deal_damage_to_enemy(
            state, enemy,
            C.MI_SAKURA_DMG + (C.MI_SAKURA_BONUS if i else 0),
            element="electro", source="companion")

    # Kamisato Ayaka, Soumetsu -- stacks are TURNS REMAINING, and the card ends
    # on a bigger hit: "for 2 turns ... deal 8 to ALL. THEN deal 16 to ALL."
    # FIRE, TICK, AND FIRE AGAIN AT ZERO -- both on the same turn when the
    # clock runs out, because "then" is what happens after the two turns and
    # the second turn's own 8 is one of them.
    if p.powers.get("mi_soumetsu", 0):
        for enemy in list(state.living_enemies):
            deal_damage_to_enemy(state, enemy, C.MI_SOUMETSU_DMG,
                                 element="cryo", source="companion")
        if _mi_tick(p, "mi_soumetsu"):
            for enemy in list(state.living_enemies):
                deal_damage_to_enemy(state, enemy, C.MI_SOUMETSU_FINALE,
                                     element="cryo", source="companion")

    # Kamisato Ayato, Kyouka -- stacks are TURNS REMAINING; the window itself
    # is spent on every Attack (`flat_attack_bonus`, `_element_for`), so all
    # that happens here is the clock, and the illusion that pops at zero.
    if p.powers.get("mi_kyouka", 0):
        if _mi_tick(p, "mi_kyouka") and state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            deal_damage_to_enemy(state, enemy, C.MI_KYOUKA_FINALE,
                                 element="hydro", source="companion")

    # Chiori, Fluttering Hasode -- Tamoto, "ignoring Block". The one caller of
    # `deal_damage_to_enemy(ignore_block=True)` in the repo.
    if p.powers.get("mi_tamoto", 0):
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            # `EB-463`: the number the CARD printed, with the card's own
            # play-time fold on it. The constant is the fallback, so a Tamoto
            # applied by anything but the `summon_damage:` grammar is the
            # number it always was.
            deal_damage_to_enemy(state, enemy,
                                 p.summon_damage.get("mi_tamoto",
                                                     C.MI_TAMOTO_DMG),
                                 element="geo", source="companion",
                                 ignore_block=True)
        _mi_tick(p, "mi_tamoto")

    # ---- the three clocks that fire nothing here ---------------------------
    # Thoma, Crimson Ooyoroi -- what it does happens on every Attack the player
    # plays (`companion_overhaul_card_played`); this is only the clock.
    _mi_tick(p, "mi_crimson_ooyoroi")
    # Gorou, General's War Banner -- the clock, and at zero it TAKES BACK the
    # Dexterity it granted. Granting real Dexterity rather than a private
    # modifier is what makes "2 Dexterity" mean what every other Dexterity in
    # the engine means; the stack it hands back is ITS OWN, so a banner that
    # expires beside somebody else's Dexterity leaves that alone.
    #
    # `EB-415`: "its own" is the amount it BANKED at play (`war_banner_grant`),
    # not the arm's constant -- the upgraded face grants 3 and the constant is
    # 2, so reading the constant here leaked 1 permanent Dexterity a play. The
    # ledger goes with the power, because a sidecar a power's expiry does not
    # clear is an amount that pays again on the next banner.
    if _mi_tick(p, "mi_war_banner"):
        owed = war_banner_grant(state)
        p.timed_power_amounts.pop(WAR_BANNER, None)
        left = p.powers.get("dexterity", 0) - owed
        if left > 0:
            p.powers["dexterity"] = left
        else:
            p.powers.pop("dexterity", None)
    # Yoimiya, Aurous Blaze -- "for 2 turns", hosted on the ENEMY: the clock,
    # where the mod's walk ticks it (after the banner). The sim had no clock
    # for it before the AoE trim (2026-10-03).
    for enemy in state.enemies:
        _mi_tick(enemy, "mi_aurous_blaze")
    # Sayu, Naptime -- the promise breaks if an Attack was played this turn.
    # Read here rather than at the start of the next turn because "this turn"
    # is THIS turn, and the counter is cleared at the next turn's start.
    if state.attacks_played_this_turn:
        p.powers.pop("mi_naptime", None)
    # Kujou Sara, Crowfeather Cover -- "this turn", so the promise is popped
    # whole whether or not an Attack ever spent it. Bennett's Passion Overload
    # is popped four lines above for the identical sentence.
    p.powers.pop("mi_crowfeather", None)


def _mi_tick(fighter, power: str) -> bool:
    """Tick one turn off a duration, returning True the turn it EXPIRES.

    One helper because eight of the arm's powers are the same clock and a
    ninth spelling of "decrement, delete at zero" is how two of them come to
    disagree about whether a stack of 1 fires this turn. Returns False for a
    power that was not standing at all, so `if _mi_tick(...)` reads as "did
    this one just run out".
    """
    n = fighter.powers.get(power, 0)
    if not n:
        return False
    if n > 1:
        fighter.powers[power] = n - 1
        return False
    del fighter.powers[power]
    return True


def _mi_above_pct(fighter, pct: int) -> bool:
    """The nation's shape, as one predicate: is this fighter above `pct`% HP?

    CROSS-MULTIPLIED rather than divided, which is the rule the sheet's own
    `hp_pct_above_N` predicate keeps (`tools/gen_klee_cards.py`) -- so a power
    reading the bar and a card reading it cannot round the one HP value a
    player notices in different directions.
    """
    return fighter.hp * 100 > fighter.max_hp * pct


def _mc_most_auras(state: CombatState):
    """The living enemy holding the most elemental auras, or None.

    An enemy in this engine holds AT MOST ONE aura (`Enemy.aura` is a single
    field), so "the most" is a count over {0, 1} and this is really "the first
    aura-bearer in board order". It is written as a max anyway, and the C#
    twin (`CompanionOverhaulTargeting.MostAuras`) is written the same way,
    because Jean's card prints "the most" and an engine that grew a second
    aura slot must not silently keep answering the one-slot question.

    `max` returns the FIRST maximal element and .NET's `OrderByDescending` is
    documented stable, so the two engines break a tie the same way.
    """
    if not state.living_enemies:
        return None
    best = max(state.living_enemies, key=lambda e: 1 if e.aura else 0)
    return best if best.aura else None


# =============================================================================
# THE MONDSTADT COMPANION OVERHAUL, SECOND WAVE -- THE HOOKS (
# `C.COMPANION_OVERHAUL`).
#
# The first pass shipped twenty-one of the approved workshop's thirty-four
# Universals and left THIRTEEN out, each because its printed text wanted an
# engine hook that existed in neither engine. These are those hooks. Every one
# is written so that with the flag off it returns before touching anything --
# the same acceptance condition the arm's two turn blocks carry, pinned in
# `tier0/tests/test_companion_overhaul_hooks.py` rather than intended.
#
# NO NEW OP AND NO NEW TARGET SPELLING. Every one of the thirteen rows is an
# `apply_power` (or a `damage` with the shipped `amount_formula` grammar), so
# the sheets' vocabulary is unchanged; what is new is WHERE the resulting
# powers are read. The five call sites are named here once:
#
#   companion_overhaul_card_start        effects._resolve_card_bound, beside
#                                        `next_attack_up`'s consuming pop
#   companion_overhaul_before_enemy_hit  combat._enemy_turn, after the hit's
#                                        damage is computed and before Block
#   companion_overhaul_block_absorbed    combat._enemy_turn, immediately after
#                                        Block is spent
#   companion_overhaul_reaction          reactions._react, at the counter site
#   companion_overhaul_reaction_mult     reactions._react and reactions._splash
# =============================================================================


def companion_overhaul_card_start(state: CombatState, card: Card) -> str:
    """The arm's per-PLAY block: returns the element THIS Attack applies.

    Called from `_resolve_card_bound` right after `current_attack_bonus` is
    snapshotted, which is the one moment that satisfies all three of its jobs
    at once -- the bonus has already been read (so a rider may be consumed),
    the card's effects have not run (so the element is settled before the
    first hit), and both play paths pass through it (so an auto-play cannot
    skip the consumption).

    THREE RIDERS CAN CLAIM THE ELEMENT AND THE ORDER IS LAW, written here and
    mirrored in the C# `CompanionOverhaulRiders.ElementFor`:

        mc_lightning_fang     Razor   -- Electro, every Attack, 2 turns
        mc_passion_overload   Bennett -- Pyro, one Attack
        mc_swirl_charge       Varka   -- the swirled element, one Attack

    LAST WINS, and the sequence is blanket first, one-shots after, because a
    one-shot the player has just bought and is spending on THIS Attack is the
    more specific claim; Varka's is last of the two because its element is the
    one the board produced a moment ago and is the only one that can differ
    from play to play. The DAMAGE halves of all three stack and are summed in
    `flat_attack_bonus`; only the element is exclusive, because an Attack
    applies one element.

    Returns "" -- meaning "no override, the cadence dial answers" -- for every
    non-Attack, for every board with none of the three up, and always while
    the flag is off.
    """
    if card.type != "attack":
        return ""
    p = state.player
    # Eula, Glacial Illumination -- "for 2 turns it COUNTS YOUR ATTACKS". The
    # tally is taken here, before the Attack resolves, so an Attack that kills
    # the blade's host is not counted by a blade that will never pay out.
    for enemy in state.living_enemies:
        if enemy.powers.get("mc_lightfall_sword", 0):
            enemy.mc_lightfall_tally += 1
    # Mika, Starfrost Swirl -- "your next Attack costs 1 less". The DISCOUNT is
    # read in `combat.card_cost`, which is pure and is called by the playability
    # gate as well; the CONSUMPTION is here, at the one site both play paths
    # reach, so a card cannot be priced twice or refunded.
    p.powers.pop("mc_starfrost_discount", None)
    override = ""
    if p.powers.get("mc_lightning_fang", 0):
        override = "electro"
    # THE INAZUMA ARM'S TWO RIDERS join the same sequence, at the same two
    # tiers, in sheet order after Mondstadt's :
    #   mi_kyouka      Ayato -- Hydro, every Attack, 2 turns   (blanket)
    #   mi_crowfeather Sara  -- Electro, one Attack            (one-shot)
    # Blanket first, one-shots after, LAST WINS -- the rule this function
    # already keeps, applied to five riders instead of three. Varka's stays
    # last of all: its element is the one the board produced a moment ago.
    if p.powers.get("mi_kyouka", 0):
        override = "hydro"
    if p.powers.pop("mc_passion_overload", 0):
        override = "pyro"
    if p.powers.pop("mi_crowfeather", 0):
        override = "electro"
    if p.powers.pop("mc_swirl_charge", 0):
        override = p.mc_swirl_element or override
        p.mc_swirl_element = ""
    return override


def companion_overhaul_before_enemy_hit(state: CombatState, enemy: Enemy,
                                        dmg: int) -> int:
    """The two TRAPS, fired before an enemy's hit lands. Returns the damage
    that hit now deals.

    THE HOOK IS THE ONE KLEE'S MINE ALREADY USES, and that is reuse rather
    than a parallel: the mod answers "an enemy is about to hit you" with
    `PowerModel.BeforeDamageReceived`, which fires after the damage number is
    settled and before Block is spent, and this is the sim's same moment
    (`combat._enemy_turn`, after `powers.modify_damage_taken` and before
    `blocked = min(...)`). A second, earlier "an enemy INTENDS to attack"
    trigger was available -- the intent is known thirty lines further up, and
    `enemy_intends_attack` already reads it -- and was refused for exactly the
    reason the Mine refuses it: an intent can be answered and then not happen,
    while a hit about to land cannot.

    ONE STACK PER HIT, and the traps are self-limiting the way the Mine is.
    "The next time an enemy attacks you" is one attack, so two copies of the
    card are two traps that answer two hits -- never one hit twice. A
    multi-hit intent spends one trap on its first hit and finds none on the
    second, which is the Mine's own consumption rule met again.

    ORDER IS LAW: the Shower first, Baron Bunny second, in sheet order. Both
    put an element on a board that may already carry one and both can kill, so
    the order decides which reactions fire -- EB-19/races-c, answered the way
    the arm's end-of-turn block answers it. The C# twin
    (`CompanionOverhaulIncomingHit`) walks the same list.

    Baron Bunny no longer reduces the hit (the co-op run, 2026-10-02): the
    card's this-turn Strength loss does that job, before the attack.
    """
    p = state.player
    # Dahlia, Sacramental Shower: "the next time an enemy attacks you, deal 9
    # Hydro damage to it FIRST" -- to IT, the attacker, and before its hit.
    if p.powers.get("mc_sacramental_shower", 0):
        _mc_spend_one(p, "mc_sacramental_shower")
        deal_damage_to_enemy(state, enemy, C.MC_SHOWER_DMG,
                             element="hydro", source="companion")
    # Amber, Explosive Puppet: "deal 8 Pyro damage to ALL enemies". One
    # attack spends one trap.
    if p.powers.get("mc_baron_bunny", 0):
        _mc_spend_one(p, "mc_baron_bunny")
        # `EB-565`, `EB-463`'s grammar one card over: the triggered damage is
        # the number the CARD printed, folded at play.
        puppet = p.summon_damage.get("mc_baron_bunny", C.MC_BARON_BUNNY_DMG)
        for other in list(state.living_enemies):
            deal_damage_to_enemy(state, other, puppet,
                                 element="pyro", source="companion")
    return dmg


def _mc_spend_one(fighter, power: str) -> None:
    """Spend one stack of a trap, deleting the key at zero."""
    n = fighter.powers.get(power, 0)
    if n > 1:
        fighter.powers[power] = n - 1
    else:
        fighter.powers.pop(power, None)


def companion_overhaul_block_absorbed(state: CombatState, enemy: Enemy,
                                      blocked: int, block_before: int) -> None:
    """Diona, Icy Paws: "When THIS Block absorbs damage, apply Cryo to the
    attacker."

    THE ENGINE HAS ONE BLOCK POOL, so "this Block" cannot be a separate pile;
    it is a MARK on the pool, `mc_icy_paws`, holding how much of the standing
    Block the card put there. A hit that spends any Block spends the mark with
    it, floored at zero -- which is the reading where the marked Block is
    eaten FIRST.

    THAT CHOICE IS ONE-WAY AND IT IS THE CONSERVATIVE ONE (R212's
    derived-not-picked rule). Marked-first means the mark runs out sooner and
    the paws bite on FEWER hits than marked-last would; there is no third
    reading, because a single pool cannot say which coin was spent. The mark is
    also clamped to the standing Block on the way in, so Block cleared at turn
    start takes the mark with it whether or not Barricade suppressed the clear.

    Fires ONCE PER ABSORBING HIT while the mark stands, which is what "when
    this Block absorbs damage" says: it is a trigger on the absorption, not on
    the card and not on the turn.
    THE KLEE ARM'S ONE READER OF THE SAME EVENT (`C.KLEE_OVERHAUL`, `EB-732`) IS FIRST AND HAS ITS OWN FLAG. Return to
    Sender is the paws' construction with a Bomb on the attacker instead of an
    aura, and it rides this function rather than a fourth call site because
    `blocked` exists nowhere else in this engine -- the same argument that put
    Thoma's barrier here. FIRST, so a board carrying both plants the charge
    before any mark below it moves; none of the three can change what another
    sees, because the marks are separate keys and `block_before` is the one
    number all of them read. The C# listener walks them in this order for the
    same reason.
    """
    klee_overhaul.block_absorbed(state, enemy, blocked, block_before)
    p = state.player
    if blocked <= 0:
        return
    mark = min(p.powers.get("mc_icy_paws", 0), block_before)
    if mark > 0:
        if enemy.alive:
            reactions.resolve_hit(state, enemy, "cryo", 0, "mc_icy_paws")
        left = mark - blocked
        if left > 0:
            p.powers["mc_icy_paws"] = left
        else:
            p.powers.pop("mc_icy_paws", None)
    # THE INAZUMA ARM's second reader of the same mark. Thoma's
    # Blazing Barrier: "Gain 6 Block. Whenever this Block absorbs damage, gain
    # 3 Block." Identical construction to the paws above -- one pool, so "this
    # Block" is a MARK on it, marked-eaten-FIRST, spent by whatever the hit
    # absorbed -- and the payout is Block instead of an aura.
    #
    # SECOND, after the paws, so a board carrying both applies the element
    # before the shield thickens; neither can change the other's answer (the
    # marks are separate keys and `block_before` is the number both read), and
    # the C# listener walks them in this order for the same reason.
    #
    # `EB-353`. THE NEW BLOCK IS MARKED, and that is what makes the rider fire
    # ONCE PER ABSORPTION. The card says "WHENEVER this Block absorbs damage",
    # and a three-hit attack is three absorptions; with the payout unmarked the
    # first hit spent the whole mark and the barrier paid exactly once, for any
    # attack. The blind act-2 seat measured 9 absorbed on all three occasions
    # it could (`klee round 8, opus-act2.md`, finding 4) and wrote "Thoma is a
    # 9-Block card that prints 6 and implies more". Per absorption the same 7x3
    # absorbs 6 + 3 + 3 = 12.
    #
    # NOT A SHIELD THAT THICKENS FOR THE FIGHT, which is what the old note here
    # feared: the mark carries no Block of its own, it is clamped to
    # `block_before` on the way in, and `inazuma_overhaul_turn_start` deletes a
    # mark with no Block behind it -- so the barrier lives exactly one enemy
    # turn per play. C# twin: `BlockMark.Absorb`, with the payout as its one
    # argument (the paws pass 0 and keep the plain marked-first spend).
    mark = min(p.powers.get("mi_blazing_barrier", 0), block_before)
    if mark > 0:
        p.block += C.MI_BLAZING_BARRIER_BLOCK           # RAW (NC-11)
        state.emit("block", amount=C.MI_BLAZING_BARRIER_BLOCK)
        p.powers["mi_blazing_barrier"] = (max(mark - blocked, 0)
                                          + C.MI_BLAZING_BARRIER_BLOCK)


def companion_overhaul_reaction(state: CombatState, enemy: Enemy,
                                name: str, aura: str) -> None:
    """The two REACTION readers, called from `reactions._react` at the site
    that already counts a reaction -- so "a reaction happened" has one
    definition in this engine, and these two cannot disagree with
    `reaction_triggered_this_turn` about it.

    C# twin: `CompanionOverhaulReactions.Note`, called from the single
    `ReactionEffects.Resolve`, which is that engine's same one site. The mod
    counts reactions there and broadcasts none; this call is the broadcast,
    kept to one consumer class so it does not become a bus nobody owns.
    """
    p = state.player
    # Dahlia, Favonian Favor: "Whenever a reaction happens this turn, gain 3
    # Block." The stack IS the 3, so a second copy pays twice. ANY reaction
    # counts, exactly as `reaction_triggered_this_turn` counts any; the card
    # names none.
    n = p.powers.get("mc_favonian_favor", 0)
    if n:
        # RAW, like every other power-sourced Block in this arm (NC-11).
        p.block += n
        state.emit("block", amount=n)
    # Varka, Sturm und Drang: "Whenever a Swirl happens, your next Attack deals
    # 6 more damage OF THE SWIRLED ELEMENT." The amount banks as an ordinary
    # stack (so two Swirls before one Attack bank twice, which is what
    # "whenever" says); the element is latched on the player, LAST WINS.
    # KLEE'S HEXEREI FAMILY, the third and fourth readers of this event
    # (R236 sec.3): Albedo's Tectonic Tide pays on ANY reaction,
    # Fischl's Sinful Hex on an ELECTRO one -- which is derived from `name` and
    # `aura` rather than passed, so no signature here widened for the slice.
    # `tier0.engine.companion_hexerei` argues both, and why a volley that can
    # react again is safe to fire from inside this site.
    companion_hexerei.note_reaction(state, enemy, name, aura)
    if name == "swirl":
        # THE INAZUMA ARM'S Swirl WINDOW. Heizou's Heartstopper
        # Strike prints "deals 4 more for each Swirl this turn", so the count
        # is taken at the one site this engine resolves a reaction -- beside
        # Varka's latch, off the same event, so "a Swirl happened" has one
        # definition here and the two readers cannot disagree.
        state.mi_swirls_this_turn += 1
        n = p.powers.get("mc_sturm_und_drang", 0)
        if n:
            p.powers["mc_swirl_charge"] = p.powers.get("mc_swirl_charge", 0) + n
            p.mc_swirl_element = aura
        # KLEE'S COVEN, third reader of the same event (R236).
        # Prune's Chime latches unconditionally rather than asking whether it
        # is up, because the Attack that arms it swirls BEFORE it arms --
        # `companion_coven.note_swirl` argues it.
        companion_coven.note_swirl(state, aura)


def companion_overhaul_reaction_mult(state: CombatState) -> float:
    """Durin, Principle of Purity / WHITE (AoE trim, 2026-10-03): "Enemies
    take X% more damage from Elemental Reactions."

    THE MULTIPLIER IS ON THE REACTION'S OWN DAMAGE, not on the hit that
    triggered it: a Vaporize that turns a 10 into a 20 has dealt 10 damage AS
    A REACTION, and 50% makes that 15 rather than making the whole 20 a 30.

    WHAT IT REACHES, exhaustively, and both engines reach the same two places:
    the AMPLIFIER's contribution (Vaporize and Melt) and the OVERLOAD splash.
    Superconduct, Frozen, Crystallize and Swirl deal no damage of their own,
    and Electro-Charged applies a dot POWER rather than damage, so it is left
    alone.

    The stack IS the percentage (50, 75 upgraded), copies add. TEAM-WIDE as
    printed: every player's reactions against enemies. The sim seats one
    player, so the holder's reactions are every player's.
    """
    pct = state.player.powers.get("mc_purity_white", 0)
    if not pct:
        return 1.0
    return 1.0 + pct / 100.0


# =============================================================================
# THE INAZUMA COMPANION OVERHAUL -- ITS OWN TWO HOOKS (
# `C.COMPANION_OVERHAUL`).
#
# Everything else the Inazuma workshop's twenty-four rows want was already
# built: the two turn blocks, the Block-absorption trigger, the next-Attack
# element override, the reaction event and the pre-enemy-attack moment are the
# Mondstadt arm's, reused row for row. These are the two the arm could not
# reach, and both hang off a site the engine already ran:
#
#   companion_overhaul_damage_dealt   effects.deal_damage_to_enemy, at the
#                                     tail, after the whole hit has resolved
#   companion_overhaul_card_played    combat._finish_play, beside
#                                     `refpowers.after_card_played`
#
# Both return before touching anything with the flag off, which is the same
# acceptance condition the Mondstadt hooks carry and is pinned in
# `tier0/tests/test_inazuma_companion_overhaul.py` rather than intended.
# =============================================================================


def companion_overhaul_damage_dealt(state: CombatState, enemy: Enemy,
                                    hp_dmg: float, source: str) -> None:
    """The two readers of a hit that has just landed on an enemy.

    GOROU'S RUNNING TOTAL. "Gain Block equal to half the damage dealt"
    (Inuzaka All-Round Defense) needs a number the card cannot compute for
    itself: the printed 8 is not what landed once Strength, Weak, an amplifier
    and the target's Block have had their say. So the play keeps a total, and
    `block_half_damage` reads it.

    IT COUNTS DAMAGE THAT REACHED HP, not the swing. That is the conservative
    reading of "the damage dealt" (R212's one-way rule: the doubt pays LESS
    Block), and it is what a body actually lost.

    `EB-603` MADE THAT SENTENCE TRUE. The caller used to hand this `hp_dmg`,
    which is the swing PAST BLOCK and carries the overkill, so a killing blow
    paid Block for damage no body took -- and `deal_damage_to_enemy` had the
    clamped figure in hand all along, because it is the number its own
    `damage` event prints. The C# twin reads
    `DamageResult.UnblockedDamage - OverkillDamage`, which is that same
    quantity on the other side and not a second definition.

    YOIMIYA'S MARK. "Whenever it takes damage from a card that is not an
    Attack, deal 6 Pyro damage to all enemies." `source` is this engine's own
    name for what dealt a hit, and it distinguishes exactly the three cases the
    sentence needs: "attack" is an Attack card, "card" is a card that is not
    one, and everything else (a bomb, a volley, a Shatter, a splash) came from
    no card at all. So the mark fires on `source == "card"` and nothing else --
    which also means the volley it fires cannot re-trigger any mark, its own
    included, because a power-sourced hit is not a card.

    GUARDED HERE AS WELL AS AT THE CALL SITE. `deal_damage_to_enemy` checks the
    flag before calling, which is what keeps a shipped hit from paying for a
    function call it does not need; this guard is what lets the acceptance test
    assert the property of the FUNCTION rather than of one caller.
    """
    if hp_dmg > 0 and source in ("card", "attack"):
        # CARD-SOURCED ONLY, which is what "the damage dealt" names on a card
        # that deals it -- and it is also what keeps the two engines counting
        # the same thing: the mod totals this off `AfterDamageReceived` where
        # the DEALER is the player and a `cardSource` is present, and its
        # power-sourced hits (`ElementalHit.Deal`) carry neither.
        state.mi_damage_dealt_this_card += int(hp_dmg)
    # Yoimiya's mark left this reader at the AoE trim (2026-10-03): it now
    # answers a Skill PLAY (`companion_overhaul_card_played`).


#: The card that marks the body. Its own play does not answer its own mark:
#: "for 2 turns, whenever you play a Skill" reads as the Skills after it.
AUROUS_BLAZE_CARD = "proto_mi_yoimiya_aurous_blaze"


def _aurous_blaze_on_skill(state: CombatState, card: Card) -> None:
    """Yoimiya, Aurous Blaze (AoE trim, 2026-10-03): "For 2 turns, whenever
    you play a Skill, deal 3 Pyro damage to that enemy." Each marked body
    takes the card's printed 3 (`summon_damage:`) once per Skill played,
    after the Skill resolves. The stack is TURNS REMAINING, so a second mark
    lengthens the window and does not double the hit; it ticks at the end of
    the turn (`inazuma_overhaul_turn_end`)."""
    if card.type != "skill" or card.id.rstrip("+") == AUROUS_BLAZE_CARD:
        return
    dmg = state.player.summon_damage.get("mi_aurous_blaze",
                                         C.MI_AUROUS_BLAZE_DMG)
    for enemy in list(state.living_enemies):
        if enemy.powers.get("mi_aurous_blaze", 0):
            deal_damage_to_enemy(state, enemy, dmg, element="pyro",
                                 source="companion")


def companion_overhaul_card_played(state: CombatState, card: Card) -> None:
    """Thoma's Crimson Ooyoroi: "For 2 turns, whenever you play an Attack, deal
    5 Pyro damage to a random enemy and gain 3 Block."

    AFTER THE CARD RESOLVES, which is where the mod's `AfterCardPlayed` puts
    it and where this engine already counts an Attack -- so the rider answers
    the board the Attack left behind, and a killing Attack's rider finds one
    fewer body. Called from `combat._finish_play` beside
    `refpowers.after_card_played`, the one site both play paths reach.

    ONE VOLLEY PER PLAY, not per stack: the stack is TURNS REMAINING (the arm's
    standing rule for a timed power), so a second Ooyoroi lengthens the window.
    The clock itself runs down at the end of the turn, in
    `inazuma_overhaul_turn_end`, like every other duration here.
    """
    _aurous_blaze_on_skill(state, card)
    if card.type != "attack":
        return
    p = state.player
    if not p.powers.get("mi_crimson_ooyoroi", 0):
        return
    if state.living_enemies:
        enemy = state.rng.choice(state.living_enemies)
        deal_damage_to_enemy(state, enemy, C.MI_OOYOROI_DMG,
                             element="pyro", source="companion")
    p.block += C.MI_OOYOROI_BLOCK                       # RAW (NC-11)
    state.emit("block", amount=C.MI_OOYOROI_BLOCK)
