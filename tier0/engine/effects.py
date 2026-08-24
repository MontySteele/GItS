"""Atomic effect resolvers — the card DSL.

v1 ops per tier0-simulator-spec.md §4.2, extended per
klee-character-design.md §6 for the real card sheet: detonate, move_bombs,
modify_bombs, burst_energy, swirl, refresh_all_auras, buff_next_attack,
cost_mod, conditional, repeat_this, formula amounts, companion ops.
"""

from __future__ import annotations

import copy

from typing import Optional

from tier0 import constants as C
from tier0.engine import powers, reactions, resources
from tier0.engine.state import (SLY_AUTOPLAY_THIS_TURN, Bomb, Card,
                                CombatState, Enemy, grant_sly_autoplay,
                                remove_instance, sly_autoplays,
                                sly_granted_this_turn, sly_riders,
                                sync_fanfare_cap_to_max_hp)


def _amount(state: CombatState, val) -> int:
    """Resolve a literal or formula amount (X-cost cards)."""
    if isinstance(val, int):
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
                   card: Optional[Card] = None) -> int:
    """Scaling riders on a damage or block amount.

    Two grammars, and the difference is deliberate:

      N_per_<thing>      a full step per unit, for SMALL counts --
                         'detonation_this_combat', 'salon_member'
      N_per_M_<resource> a ratio, for LARGE pools -- 'fanfare', 'charge',
                         'encore' -- where 1:1 would pay far too much
    """
    n, _, rest = formula.partition("_per_")
    if not n.isdigit():
        raise ValueError(f"unknown bonus_formula {formula!r}")
    if rest == "detonation_this_combat":
        return int(n) * state.detonations_total
    if rest == "salon_member":
        # A13/A14 (2026-07-28): a slope on the stage itself. No _M_ divisor
        # because the salon is a small capped count (3, or 4 with A12's
        # cap-raise power) -- every member is a full step, unlike Fanfare
        # where the ratio is what keeps a 40-point meter from paying 40.
        # Reads powers['salon_member'], the same mirror has_salon_members and
        # the `salon_members` runtime count read, so a member that left the
        # stage stops paying immediately.
        return int(n) * state.player.powers.get("salon_member", 0)
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
        resources.note_fanfare_read(state, "bonus_formula",
                                    card=card.id if card else None)
        # `readable`, not the raw field: the meter can sit BELOW ZERO since
        # the Hyperbeam (Track C.2), and a rider reading -12 would pay
        # NEGATIVE damage -- an attack that heals the enemy. Effects shut off
        # rather than invert; see resources.drop_fanfare_to_floor.
        return int(n) * (resources.readable(state.player) // int(m))
    if what == "charge" and m.isdigit():
        # Kokomi finisher reads (kickoff §2.2): Charge is READ, never
        # consumed. Rate limits (Rare / Exhaust / cost >= 2) live on the
        # card rows, not here — this is only the arithmetic.
        resources.note_charge_read(state, "bonus_formula",
                                   card=card.id if card else None)
        return int(n) * (state.player.charge // int(m))
    if what == "encore" and m.isdigit():
        # Curtain Call C (R85): damage reading the held buffer -- Body
        # Slam is the direct StS precedent for an attack priced off a
        # defensive pool. READ only, never consumed; the private-register
        # attack (poised_riposte) is the one card on the rate.
        return int(n) * (state.player.encore // int(m))
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
    if token == "cards_drawn_this_combat":
        return state.cards_drawn_this_combat
    if token == "enemy_poison_total":
        return sum(e.powers.get("poison", 0) for e in state.living_enemies)
    if token == "salon_members":
        # Curtain Call C (R85): the live cast count. A power-stack read at
        # resolution time -- Mirage's enemy_poison_total is the in-repo
        # precedent for a CalculatedVar over power stacks; the mirror
        # powers['salon_member'] == len(salon) is maintained at the deploy
        # site. Matinée Performance's per-member hits are the one user.
        return p.powers.get("salon_member", 0)
    if token == "leftmost_salon_act":
        # EB-118 §5.5: what the NEXT performer's act is worth right now --
        # the printed base plus the Focus term and Grand Salon, at the price
        # the stage can currently pay. The reward half of the leftmost read:
        # a card body can pay off the performer it is about to move or
        # perform without restating the member table. 0 on an empty stage.
        #
        # Resolves through salon_tick_amount, the same expression
        # salon_member_act pays out and the C# role chip renders.
        if not p.salon:
            return 0
        paid = p.encore >= C.SALON_TICK_ENCORE_COST
        return salon_tick_amount(state, p.salon[0], paid)
    if token == "X":
        # Skewer: hit count = the energy actually spent, the same number
        # `amount: X` resolves. Spelled with the same token deliberately.
        return state.current_x
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
    if token.startswith(EXHAUST_SELECTION_PREFIX):
        counts = exhaust_selection_counts(state.exhaust_selection)
        key = token[len(EXHAUST_SELECTION_PREFIX):]
        if key in counts:
            return counts[key]
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


def _default_target(state: CombatState) -> Optional[Enemy]:
    """tier0's single-target aim -- the lowest-HP living enemy, the same one
    _pick_targets('enemy') returns and resolve_card snapshots for its aura
    predicate. Dismantle's hit-count predicate and Dominate/MoltenFist's
    power-reading formula both need the enemy the card is about to (or just
    did) hit. CAVEAT, inherent to the model and shared with Bash/Uppercut:
    across ops the aim is RE-picked, so a hit that kills the aimed enemy
    hands the rider to whoever is lowest-HP next, not to a corpse."""
    living = state.living_enemies
    return min(living, key=lambda e: e.hp) if living else None


def _pick_targets(state: CombatState, spec: str) -> list[Enemy]:
    living = state.living_enemies
    if not living:
        return []
    if spec in ("enemy", "lowest_hp_enemy"):        # pilot aims at lowest HP
        # PARITY, not fidelity: the base game rolls a RANDOM enemy for
        # TargetType.AnyEnemy on an autoplay, and the variance profile is
        # the whole identity of Havoc/Cascade. Keeping tier0's lowest-HP aim
        # for free plays would hand those cards a pilot's judgement they do
        # not have. Set only for the duration of a free play.
        if state.force_random_targeting:
            return [state.rng.choice(living)]
        return [min(living, key=lambda e: e.hp)]
    if spec == "all_enemies":
        return list(living)
    if spec in ("random_enemy", "random_enemies"):
        return [state.rng.choice(living)]
    raise ValueError(f"unknown target spec {spec!r}")


def _element_for(state: CombatState, fx: dict, card: Card) -> Optional[str]:
    """Cadence dial (design doc §2.3; Furina kickoff §1).

    catalyst: every attack applies the character's element unless the
    sheet says applies_element: false. Cards with their own element
    (companions) apply that instead.

    skill (Furina, Skill-grade): only Skill/Burst-tagged cards apply the
    CHARACTER's element -- attacks never auto-apply, which is what buys
    the higher base numbers within her low-statline identity. Companion
    cards are exempt from cadence entirely: what a companion applies is
    the sheet's explicit call (application budgets depend on it)."""
    if "applies_element" in fx:
        return card.element if fx["applies_element"] else None
    if (card.type == "attack" and fx["op"] == "damage"
            and state.player.cadence == "catalyst"):
        return card.element if card.element != "none" else state.player.element
    if (state.player.cadence == "skill" and fx["op"] == "damage"
            and not card.is_companion
            and state.player.element != "none"
            and (card.type == "skill" or "burst" in card.tags
                 or "skill_tag" in card.tags)):
        return state.player.element
    return None


# R33 lint-law (DECISIONS 87, the dead-knob exercise counter): a sweep
# that concludes "no effect" must show its swept constant was READ at
# least once per cell. This is the instrument-side tally; experiments
# reset it per cell and assert before publishing a null. E1 (pass 2)
# would have failed this loudly -- that catch is why it exists.
KNOB_READS: dict = {}


def reset_knob_reads() -> None:
    KNOB_READS.clear()


# Diagnostic switch retained for controlled Center/Guest comparisons;
# production never sets it outside experiments and tests.
SPOTLIGHT_FORCE: Optional[str] = None


def both_spotlight_modes(state: CombatState) -> bool:
    """Furina's upgraded starter (Touch of Orobas -> The Curtain Never Falls,
    red-pen R2): both Spotlight modes permanently in force.

    Thin wrapper so the four Spotlight readers below say what they mean and
    the relic test lives in one place. Late import: `relics` imports
    `refpowers`, so a module-level import here would close a cycle.
    """
    from tier0.engine import relics                  # late import (cycle)
    return relics.spotlight_both_modes(state.player)


def center_stage_active(state: CombatState, card: Card) -> bool:
    """Center Stage's half for THIS card: does playing it mint Fanfare?

    Her own cards only, in both worlds. Under the mode that is implied (only
    her cards are lit at all); under R2's upgrade it has to be said, because
    Companions are lit too and Guest Cast's "their plays generate no Fanfare"
    clause survives the upgrade -- R2 reading 1 drops the exclusivity, not
    the targeting. Mirrors C# `SpotlightSystem.CenterStageActive(owner) &&
    card is ICharacterCard { CharacterId: "furina" }`.
    """
    p = state.player
    if both_spotlight_modes(state):
        return bool(p.character_id and card.character == p.character_id)
    return p.spotlight == p.character_id


def is_spotlighted(state: CombatState, card: Card) -> bool:
    """Whether a card receives Spotlight play texture in the active mode."""
    p = state.player
    if both_spotlight_modes(state):
        # C# SpotlightSystem.IsSpotlighted: each half keeps its own card
        # class, and under the upgrade both halves are live at once.
        return bool(card.is_companion
                    or (p.character_id and card.character == p.character_id))
    target = p.spotlight
    if target == C.SPOTLIGHT_GUEST_CAST:
        return card.is_companion
    return bool(target and card.character == target)


def is_outward_spotlighted(state: CombatState, card: Card) -> bool:
    """Whether Spotlight may change this card's printed numbers."""
    if both_spotlight_modes(state):
        # Guest Cast's half ONLY. Without the card-class test the multiplier
        # would leak onto her own cards, which Center Stage explicitly does
        # not do (C# OutwardMultiplier keeps the same gate for the same
        # reason). No `spotlight` read: under the upgrade the designation is
        # irrelevant, which is the whole point of the ruling.
        return is_spotlighted(state, card) and card.is_companion
    return (is_spotlighted(state, card)
            and state.player.spotlight != state.player.character_id)


def spotlight_mult(state: CombatState, card: Card) -> float:
    """Guest Cast numeric empowerment, including card-mediated bonuses.

    Center Stage always returns 1.0, even if Spotlight bonus powers are
    installed. Guest Cast and the legacy named-partner diagnostic path read
    the outward base plus combat- or turn-scoped bonuses.

    §2.2a extension, ENGINE-ENFORCED: this helper is plumbed into damage,
    Block, and (when the DSL grows one) element-application counts -- and
    nowhere else. Draw, energy, cost, and turn-economy ops have no path
    to it, so 'numbers only' is structure, not per-card discipline."""
    p = state.player
    if not is_outward_spotlighted(state, card):
        return 1.0
    cap = C.SPOTLIGHT_CARDS_PER_TURN_CAP     # schematized, OFF by default
    if cap is not None and state.spotlighted_cards_this_turn > cap:
        return 1.0
    base = C.SPOTLIGHT_BASE_MULT
    KNOB_READS["SPOTLIGHT_BASE_MULT"] = (
        KNOB_READS.get("SPOTLIGHT_BASE_MULT", 0) + 1)
    bonus = (p.powers.get("spotlight_mult_bonus", 0)
             + p.powers.get("spotlight_mult_bonus_turn", 0))
    return base + bonus / 100.0


def _spotlight_scale(state: CombatState, card: Card, amount: int) -> int:
    m = spotlight_mult(state, card)
    return int(amount * m) if m != 1.0 else amount


def deal_damage_to_enemy(state: CombatState, enemy: Enemy, base: float,
                         element: Optional[str] = None,
                         source: str = "card") -> float:
    """Full damage pipeline: strength/weak -> reaction amp -> vulnerable ->
    block -> hp. Returns damage actually dealt to HP (for metrics)."""
    # Solar Isotoma (Crystallize engine): attack hits vs aura'd enemies
    # grant block — checked before the hit can consume the aura.
    if (source == "attack" and enemy.aura
            and state.player.powers.get("solar_isotoma", 0)):
        state.player.block += C.SOLAR_ISOTOMA_BLOCK
    was_frozen = enemy.frozen > 0   # snapshot: a hit can't shatter the
    dmg = powers.modify_damage_dealt(state.player, base)  # freeze it applies
    unamped = dmg                   # EB-57: the pre-amplifier counterfactual
    log_mark = len(state.log)
    dmg = reactions.resolve_hit(state, enemy, element, dmg)
    amped = dmg != unamped
    from_card = source in ("card", "attack")
    # `source` names what dealt it; "card" and "attack" are the two card
    # sources, everything else (bombs, summon pulses, shatter, splash) is
    # the base game's `cardSource == null` case.
    dmg = powers.modify_damage_taken(enemy, dmg, from_card=from_card)
    # Slow (§10.9 promotion): +N% damage from Attacks per card played this
    # turn. cards_played_this_turn increments at play, BEFORE resolution, so
    # the attacking card counts itself -- the base-game trigger order.
    slow_mult = (1 + enemy.slow * state.cards_played_this_turn / 100.0
                 if enemy.slow and source == "attack" else 1.0)
    if slow_mult != 1.0:
        dmg *= slow_mult
    dmg = int(dmg)
    if base > 0 and dmg > base * C.AMP_STACK_LIMIT:
        state.emit("amp_stack_warning", base=base, final=dmg, target=enemy.name)
    block_before, hp_before = enemy.block, enemy.hp
    blocked = min(enemy.block, dmg)
    enemy.block -= blocked
    hp_dmg = dmg - blocked
    was_alive = enemy.alive
    effective = min(hp_dmg, max(0, enemy.hp))   # overkill doesn't count
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
        un_hp = un - min(block_before, un)
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
    # envenom.
    from tier0.engine import refpowers as _refpowers
    _refpowers.envenom_on_hit(state, enemy, hp_dmg, source)
    # Skittish (§10.9 promotion): "The first time it is hit each turn, it
    # gains N Block." AFTER the whole hit resolves (incl. any detonation
    # rider), so the triggering attack is never mitigated by it; the latch
    # resets in combat._player_turn.
    if (enemy.skittish and not enemy.skittish_fired and source == "attack"
            and enemy.alive):
        enemy.skittish_fired = True
        enemy.block += enemy.skittish
        state.emit("skittish_block", target=enemy.name,
                   amount=enemy.skittish)
    return hp_dmg


def _detonate_bombs_on_hit(state: CombatState, enemy: Enemy, source: str) -> None:
    # Bombs detonate early when the enemy is hit by an Attack card (§4.2).
    if source != "attack" or not enemy.bombs or not enemy.alive:
        return
    detonate_bombs(state, enemy)


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
            gain_sparks(state, 1)
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
            if p.burst_max:
                resources.gain_burst(
                    state, C.DETONATION_SPLASH_BURST, "detonation_splash")
        vuln = p.powers.get("detonation_vuln", 0)         # Explosive Frags
        if vuln and enemy.alive:
            powers.apply_power(state, enemy, "vulnerable", vuln)


def gain_sparks(state: CombatState, n: int) -> None:
    state.player.sparks += n
    state.emit("gain_spark", amount=n, total=state.player.sparks)


def spend_spark_amount(fx: dict) -> int:
    """The literal Spark price on one `spend_spark` effect.

    A LITERAL positive int, not `_amount`: `combat.spark_cost` reads the same
    number off the printed effect with no state in hand, and a price the
    playability gate cannot read is a price that fires without being shown.
    Raises rather than approximating -- the loader's vocabulary check reports
    an unknown op, and this reports an unpriceable one.
    """
    amount = fx.get("amount")
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        raise ValueError(
            f"spend_spark amount must be a positive literal int, got "
            f"{amount!r}")
    return amount


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


def _add_token(state: CombatState, card: Card, zone: str) -> None:
    if zone == "hand" and len(state.player.hand) < C.MAX_HAND_SIZE:
        state.player.hand.append(card)
    else:
        state.player.discard_pile.append(card)
    # Kokomi §7 engine_closure diagnostic: every created card funnels
    # through here (add_card tokens, generators, conscript-create), so the
    # per-turn creation count is structural. Report-only (R14).
    state.cards_created_this_turn += 1
    state.emit("add_card", card=card.id, to=zone)


# --- ops ---

def _op_damage(state: CombatState, fx: dict, card: Card) -> None:
    element = _element_for(state, fx, card)
    source = "attack" if card.type == "attack" else "card"

    if fx.get("target") == "self":            # Hot Hands / No Holding Back
        state.player.hp -= fx["amount"]       # HP loss, ignores block AND
        state.emit("self_damage", amount=fx["amount"])   # Encore: a priced
        resources.note_player_hp_loss(state, fx["amount"])  # cost stays paid
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
    if state.salon_replacements_this_card:
        base *= C.SALON_REPLACE_DAMAGE_MULT
    # Spotlight scales the card's own printed damage -- before external
    # buffs (strength/next_attack_up are not printed numbers) and before
    # per-target riders (v1 boring baseline; riders logged as design room).
    base = _spotlight_scale(state, card, base)
    # Star of the Show: flat rider on Spotlighted cards' damage. Card-level
    # texture (kickoff §3.2 ratified design space), NOT the baseline knob.
    # Pass 2 adds the this-turn variant (stage_lights) on the same pipe.
    if is_outward_spotlighted(state, card):
        base += (state.player.powers.get("spotlight_flat_damage", 0)
                 + state.player.powers.get("spotlight_flat_damage_turn", 0))
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
    bombed_at_cast = ({id(e) for e in state.enemies if e.bombs}
                      if fx.get("bonus_vs_bombed") else frozenset())

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

    for _ in range(times):
        for enemy in _pick_targets(state, target):
            hit = base
            if fx.get("bonus_vs_bombed") and id(enemy) in bombed_at_cast:
                hit += fx["bonus_vs_bombed"]
            if fx.get("bonus_vs_aura") and enemy.aura:
                hit += fx["bonus_vs_aura"]
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
    raw = (_calc_amount(state, fx["amount_formula"], card)
           if "amount_formula" in fx else fx["amount"])
    # Same rider grammar damage already carries (F-B1): a defensive card may
    # scale on the meter too. Applied BEFORE the Salon multiplier and before
    # Spotlight, exactly where damage applies its own -- a rider that landed
    # after those would be multiplied by them and quietly outscale its
    # printed twin.
    if "bonus_formula" in fx:
        raw += _bonus_formula(state, fx["bonus_formula"], card)
    if state.salon_replacements_this_card:
        raw *= C.SALON_REPLACE_DAMAGE_MULT
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
    # Not Spotlight-scaled (Spotlight scales printed numbers; an enchantment
    # is not printed), but Frail does bite it, exactly as the hook order does:
    # the enchant additive lands before the multiplicative listeners.
    for _ in range(times):
        amount = _spotlight_scale(state, card, raw) + card.enchant_block
        # Frail bites each printed card-block gain before the refpower funnel.
        amount = powers.modify_block_gained(state.player, amount)
        state.player.block += amount
        state.block_gains_this_card += 1
        state.block_gained_this_card += amount
        state.emit("block", amount=amount)


def _op_block_next_turn(state: CombatState, fx: dict, card: Card) -> None:
    # Charlotte, First-Person Shutter: pre-emptive block that lands at the
    # start of the player's NEXT turn (after the turn-start block reset).
    # Sustain-over-time identity without true healing (R8-shaped).
    # Spotlight scales it at play time (printed Block is printed Block).
    amount = _amount(state, fx["amount"])
    if state.salon_replacements_this_card:
        amount *= C.SALON_REPLACE_DAMAGE_MULT
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
    powers.apply_power(state, state.player, "block_next_turn",
                       _spotlight_scale(state, card, amount))


def _op_draw(state: CombatState, fx: dict, card: Card) -> None:
    if fx.get("amount_formula") == "per_aura":     # Elemental Ecstasy
        # Checked FIRST: the row carries no flat `amount`, and running it
        # through _amount would raise before this branch could fire -- the
        # pass-4 grammar widening did exactly that and broke every fight
        # that played the card (caught by the R84 roster re-run).
        n = sum(1 for e in state.living_enemies if e.aura)
    else:
        n = _amount(state, fx.get("amount"))
    if state.salon_replacements_this_card:
        n *= C.SALON_REPLACE_NUMERIC_MULT
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


def _salon_amount(state: CombatState, base: int) -> int:
    """A Salon member numeric amount (Salon v2): base + the Fanfare Focus
    term (+1 per SALON_FOCUS_PER held, read live) + Grand Salon."""
    p = state.player
    if not p.fanfare_cap:
        return base + p.powers.get("salon_damage_up", 0)
    # The Salon-v2 Focus analogue is the read that matters most to this
    # sprint: it is where "a constant wearing a meter" was measured.
    resources.note_fanfare_read(state, "salon_focus")
    # Clamped: a negative meter must not chip the stage. Negative member
    # ticks are the exact reading that would look like a bug rather than a
    # cost (Track C.2, PROPOSED semantics, flagged for review).
    focus = resources.readable(p) // C.SALON_FOCUS_PER
    return base + focus + p.powers.get("salon_damage_up", 0)


def _salon_bow(state: CombatState, member: str) -> None:
    """The displaced member's final bow (Salon v2, rework plan §1): its
    UNIQUE payoff. No Encore upkeep, Focus/Grand-Salon scaled numerics,
    feeds the Burst meter like a tick."""
    p = state.player
    spec = C.SALON_MEMBERS[member]["bow"]
    dmg = spec.get("damage", 0)
    if dmg and state.living_enemies:
        enemy = state.rng.choice(state.living_enemies)
        deal_damage_to_enemy(state, enemy, _salon_amount(state, dmg),
                             element="hydro", source="salon_final_bow")
    blk = spec.get("block", 0)
    if blk:
        amt = _salon_amount(state, blk)
        p.block += amt
        state.emit("block", amount=amt)
    if spec.get("aura_all"):
        for enemy in state.living_enemies:
            reactions.resolve_hit(state, enemy, "hydro", 0)
    enc = spec.get("encore", 0)
    if enc:
        resources.gain_encore(state, enc, "salon_final_bow")
    if p.burst_max:
        resources.gain_burst(state, C.SALON_TICK_BURST, "salon_final_bow")
    # Stagehands (Curtain Call B, R85): the crew strikes the set behind
    # every bow. Activity-gated on the bow event itself; unscaled printed
    # numbers, same reasoning as salon_deploy_block above.
    blk = p.powers.get("salon_bow_block", 0)
    if blk:
        p.block += blk
        state.emit("block", amount=blk)
    enc2 = p.powers.get("salon_bow_encore", 0)
    if enc2:
        resources.gain_encore(state, enc2, "salon_bow_encore")
    state.emit("salon_final_bow", member=member)


def salon_slots(player) -> int:
    """How many members this player's stage holds.

    A12 (2026-07-28) promoted the cap from a constant to a per-player stat.
    C.SALON_MEMBER_SLOTS stays the BASE -- it is what the constant-parity gate
    compares against SalonConstants.MemberSlots on the C# side -- and the
    cap-raise power adds to it. Every reader goes through here so a new one
    cannot accidentally re-hardcode 3.
    """
    return C.SALON_MEMBER_SLOTS + player.powers.get("salon_cap_up", 0)


def _deploy_salon_members(state: CombatState, amount: int,
                          member: str = "crabaletta") -> None:
    """Salon v2 deploy (rework plan §1): the typed FIFO queue with Defect
    evoke geometry. Deploying into full slots bows the OLDEST member OUT
    (its unique bow) and the new member takes the vacated slot — the v1
    rule (the excess deploy bowed itself and never entered) is the
    archive. powers['salon_member'] mirrors len(queue) so every count
    read (has_salon_members, the pilot, instruments) is unchanged."""
    p = state.player
    if member != "random" and member not in C.SALON_MEMBERS:
        raise ValueError(f"unknown salon member {member!r}")
    for _ in range(amount):
        # A11 (2026-07-28): `member: random` de-dupes the starter from the
        # Chevalmarin card. Rolled PER DEPLOY, not once per card, so a
        # multi-deploy card can field a mixed stage. Sorted keys because the
        # roll must not depend on dict insertion order.
        entering = (state.rng.choice(sorted(C.SALON_MEMBERS))
                    if member == "random" else member)
        if len(p.salon) >= salon_slots(p):
            state.salon_replacements_this_card += 1
            _salon_bow(state, p.salon.pop(0))
        p.salon.append(entering)
        # `entering`, not `member`: an observer of this event wants to know
        # WHO took the stage, and "random" is not a member.
        state.emit("salon_deploy", member=entering, company=list(p.salon))
        # Fortissimo Guard (Curtain Call B, R85): block per DEPLOY, per
        # deployment event rather than per card -- Full Ensemble's three
        # deploys are three cues. Direct add + emit, the _salon_bow block
        # pattern; deliberately NOT Focus/Grand-Salon scaled (the power's
        # printed number is the whole payout, matching its own note field).
        blk = p.powers.get("salon_deploy_block", 0)
        if blk:
            p.block += blk
            state.emit("block", amount=blk)
    p.powers["salon_member"] = len(p.salon)


def _op_apply_power(state: CombatState, fx: dict, card: Card) -> None:
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
    if (state.salon_replacements_this_card
            and fx["power"] != "salon_member"):
        amount *= C.SALON_REPLACE_NUMERIC_MULT
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
    if fx.get("target", "self") == "self":
        if fx["power"] == "salon_member":
            _deploy_salon_members(state, amount,
                                  fx.get("member", "crabaletta"))
            return
        # Tamakushi Casket link (v0.4 §1.3, her canon A1 passive): casting
        # the Garment while the Kurage is fielded refreshes the jellyfish's
        # duration. The E-into-Q loop, verbatim. Guarded on the summon
        # already being out -- the Burst does not conjure one from nothing.
        if (fx["power"] == "ceremonial_garment"
                and state.player.powers.get("kurage_summon", 0)):
            # max(), not a hard set (audit 2026-07-26 s1.4; fixed in EPOCH 1).
            # This assigned KURAGE_DURATION outright, so playing the Garment
            # after an UPGRADED summon (kurage_turns +1, i.e. 2 turns) pulled
            # the jellyfish back down to 1 and DELETED the turn the upgrade
            # had paid for. R56/R57's "restoring a longer duration is safe"
            # was true of the design and false of the wiring. Now matches
            # _op_summon_kurage, which has always used max(): a refresh tops
            # the timer up and never shortens it.
            turns = max(state.player.powers["kurage_summon"],
                        C.KURAGE_DURATION)
            state.player.powers["kurage_summon"] = turns
            state.emit("kurage_refreshed", turns=turns)
        powers.apply_power(state, state.player, fx["power"], amount,
                           max_stacks=cap, never_reduces=floor)
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
            for enemy in _pick_targets(state, target):
                powers.apply_power(state, enemy, fx["power"], amount,
                                   max_stacks=cap, never_reduces=floor)


def _op_apply_aura(state: CombatState, fx: dict, card: Card) -> None:
    times = (C.SALON_REPLACE_NUMERIC_MULT
             if state.salon_replacements_this_card else 1)
    for _ in range(times):
        targets = _pick_targets(state, fx.get("target", "enemy"))
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


def _op_place_bomb(state: CombatState, fx: dict, card: Card) -> None:
    for _ in range(_amount(state, fx.get("amount", 1))):
        for enemy in _pick_targets(state, fx.get("target", "random_enemy")):
            enemy.bombs.append(Bomb(damage=fx["bomb_damage"],
                                    element=fx.get("element", "pyro"),
                                    turn_placed=state.turn))
            state.emit("bomb_placed", target=enemy.name,
                       damage=fx["bomb_damage"])


def _op_detonate(state: CombatState, fx: dict, card: Card) -> None:
    for enemy in _pick_targets(state, fx.get("target", "enemy")):
        if enemy.bombs:
            detonate_bombs(state, enemy, bonus=fx.get("bonus", 0))


def _op_move_bombs(state: CombatState, fx: dict, card: Card) -> None:
    # Careful Arrangement: gather all bombs onto one enemy, +bonus each.
    targets = _pick_targets(state, fx.get("target", "enemy"))
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


def _op_burst_energy(state: CombatState, fx: dict, card: Card) -> None:
    if state.player.burst_max:
        # The card-text source. Keeps its own `burst_energy` event as well as
        # the shared `burst_income` one: the old event is what existing
        # reports and tests read, and C5 is diagnostic -- it does not get to
        # break a surface that already works.
        resources.gain_burst(state, fx["amount"], "card")
        state.emit("burst_energy", amount=fx["amount"],
                   total=state.player.burst_energy)


def _op_swirl(state: CombatState, fx: dict, card: Card) -> None:
    targets = _pick_targets(state, fx.get("target", "enemy"))
    # A human will aim a single-target Swirl at an aura when one exists.
    # Tier 0 otherwise hard-aims every AnyEnemy card at lowest HP, which made
    # Anemo cards blank whenever the aura happened to sit elsewhere.
    if fx.get("target", "enemy") == "enemy" and targets and not targets[0].aura:
        aura_targets = [e for e in state.living_enemies if e.aura]
        if aura_targets:
            targets = [min(aura_targets, key=lambda e: e.hp)]
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
    gain_sparks(state, fx.get("amount", 1))


def _op_spend_spark(state: CombatState, fx: dict, card: Card) -> None:
    """The Spark SINK (EB-118 §4.5): sparks are a resource with a competing
    use, and this is the competition.

    The COST LINE, not an overdraw: a card printing this op at top level is
    unplayable below its price (combat.spark_cost -> combat.card_playable),
    the encore_cost gate's shape, so the cost is visible before the energy
    is spent. `spend_sparks` refuses a short bank as well -- the gate cannot
    see a spend nested in a conditional branch, and an unpayable price must
    fail loudly wherever it is reached rather than half-paying.
    """
    spend_sparks(state, spend_spark_amount(fx))


def _op_gain_encore(state: CombatState, fx: dict, card: Card) -> None:
    # Her "healing" effects grant Encore (kickoff §4). Unbounded per-combat.
    amount = _amount(state, fx["amount"])
    if state.salon_replacements_this_card:
        amount *= C.SALON_REPLACE_NUMERIC_MULT
    resources.gain_encore(state, amount, "gain_encore_op", card.id)


def _op_spend_encore(state: CombatState, fx: dict, card: Card) -> None:
    """The OVERDRAW primitive (kickoff §4, Salon grammar): drains Encore
    first; any shortfall drains TRUE HP -- greed is legal and priced.
    Cards that must not overdraw use the encore_cost field (playability
    gate in combat.card_playable) instead of this op."""
    resources.spend_encore_or_hp(state, _amount(state, fx["amount"]),
                                 "spend_encore_op", card.id)


def _op_spotlight_designate(state: CombatState, fx: dict, card: Card) -> None:
    """Choose between Center Stage and Guest Cast.

    Center Stage designates Furina: her cards create Fanfare but receive no
    numeric Spotlight bonus. Guest Cast designates the Companion category:
    every Companion card is empowered, but those plays create no Fanfare.
    A ready Companion in hand makes Guest Cast immediately useful; otherwise
    the selector defaults to Center Stage. The diagnostic override retains
    forced self/companion arms for experiments."""
    p = state.player
    companion_in_hand = any(c.is_companion and not c.kit_card for c in p.hand)
    companion_anywhere = any(
        c.is_companion and not c.kit_card
        for c in (p.hand + p.draw_pile + p.discard_pile))
    if SPOTLIGHT_FORCE == "self":
        target = p.character_id or None
    elif SPOTLIGHT_FORCE == "companion":
        target = C.SPOTLIGHT_GUEST_CAST if companion_anywhere else None
    elif companion_in_hand:
        target = C.SPOTLIGHT_GUEST_CAST
    else:
        target = p.character_id or (
            C.SPOTLIGHT_GUEST_CAST if companion_anywhere else None)
    if target is None:
        return                                   # nothing valid to aim at
    if target != p.spotlight:
        p.spotlight = target
        state.spotlight_moved_this_turn = True      # selector-payoff window
        state.spotlight_moves_this_combat += 1
        mode = ("guest_cast" if target == C.SPOTLIGHT_GUEST_CAST
                else "center_stage")
        state.emit("spotlight_designated", character=target, mode=mode)


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


def _op_salon_bow(state: CombatState, fx: dict, card: Card) -> None:
    """The on-demand bow (Track D, the D6 probe, 2026-07-28).

    The LEFTMOST member takes their bow: `salon.pop(0)`, the same end of the
    FIFO queue a deploy into a full stage displaces. That is the whole point
    of choosing leftmost over a target -- the player already knows which
    member is next out, because the deploy rule taught them, so the probe
    costs no new reading.

    Defect-evoke analogue, and it enters NOW because Track A changed what it
    is worth: a bow that pays Encore is an Encore SINK's opposite, and under
    single-leg Fanfare the Encore it grants no longer mints on arrival. It is
    a bow trigger whose value is the bow, not the buffer -- which is exactly
    the thing the probe wants to measure.

    Inert on an empty stage, silently: "take a bow" with no company is a
    no-op, not an error, so the card is never unplayable and never wasted in
    a way the player cannot see coming from the stage itself.
    """
    p = state.player
    for _ in range(_amount(state, fx.get("amount", 1))):
        if not p.salon:
            break
        _salon_bow(state, p.salon.pop(0))
    p.powers["salon_member"] = len(p.salon)


def _op_salon_rotate(state: CombatState, fx: dict, card: Card) -> None:
    """Rotate the leftmost member to the BACK of the queue (EB-118 §5.5).

    A pure reorder: the member keeps its identity, performs NO tick, drains
    NO Encore and triggers NO bow or replacement effect. It buys exactly one
    thing -- which performer the FIFO end offers next, to `salon_bow`, to a
    deploy landing on a full stage, and to the `leftmost_salon_member_*`
    reads. powers['salon_member'] is untouched by construction: the queue's
    length cannot change here.

    Inert on an empty stage, and NOT silently: unlike `salon_bow`, whose
    no-op is legible from the empty stage itself, a rotate that found nothing
    to rotate is invisible in the state afterwards. `conscript_whiffed` is
    the pattern.
    """
    p = state.player
    if not p.salon:
        state.emit("salon_rotate_whiffed")
        return
    for _ in range(_amount(state, fx.get("amount", 1))):
        p.salon.append(p.salon.pop(0))
    state.emit("salon_rotate", company=list(p.salon))


def _op_salon_perform(state: CombatState, fx: dict, card: Card) -> None:
    """The leftmost member performs NOW (EB-118 §5.5): an extra slot passive,
    off-turn, at the standard price.

    Resolves through `salon_member_act` -- the same function the turn-start
    upkeep calls -- so the Encore upkeep, the dry three-quarters, the
    Focus/Grand-Salon scaling, the burst particle and the `salon_tick`
    telemetry row are inherited rather than restated. That sharing is the
    contract, not an implementation convenience.

    The member STAYS on stage: this is a performance, not a bow, and not a
    rotation. `amount: N` therefore performs the leftmost member N times;
    pair it with `salon_rotate` to spread the acts across the company.
    """
    p = state.player
    if not p.salon:
        state.emit("salon_perform_whiffed")
        return
    for _ in range(_amount(state, fx.get("amount", 1))):
        if not salon_member_act(state, p.salon[0]):
            break


def _op_generate_guest_star(state: CombatState, fx: dict, card: Card) -> None:
    """Guest Star generation (kickoff §9), four guardrails all structural:
    this-combat-only (tokens live in combat piles; decks rebuild from ids
    per fight), generators Exhaust (sheet field), equal-rarity (the pool
    is filtered to fx['rarity'] == the generator's own printed rarity),
    and the pool is shared companions + the Guest Star set ONLY — playable
    characters' personal cards are structurally absent because they are
    neither companions nor guest_star rows."""
    _generate(state, fx, "guest_star")


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


    # FLAG-2(i) (R114, Errata Batch 2 item 8): THE COPY IS BUILT FROM THE
    # PRINTED CARD, not deep-copied from the instance in hand. Verbatim:
    # "Copy ops inherit the printed card's bounds... the printed bound
    # travels with the copy."
    #
    # `loader.get_card` returns a fresh copy of the SHEET's card, and the
    # upgraded form rides the `+` id convention, so an upgraded target still
    # copies as upgraded. What no longer travels is whatever the instance
    # picked up during this combat -- an Exhaust the sheet prints and some
    # effect stripped, a cost another copy op zeroed (the `copy_dup_5`
    # taint), a damage number that grew in play. That is exactly what the mod
    # does: `CombatState.CreateCard(ModelDb.GetById<CardModel>(id))` copies
    # the canonical model, and a printed keyword like Exhaust is declared per
    # MODEL, so the C# copy has always carried it.
    #
    # WHAT THIS DOES NOT CLOSE: X3's loop. A copy is still an extra USE of an
    # Exhaust card, and no bound the sheet prints on one instance can limit
    # the number of instances. The pin reports accordingly.
def _op_copy_spotlighted_in_hand(state: CombatState, fx: dict,
                                 card: Card) -> None:
    """Encore Performance (kickoff §9): duplicate a Spotlighted card in
    hand. Dead without a LIT target and a drafted one — BY DESIGN
    (duplication deepens a committed kit; it must not conjure one).

    EB-100: the question is `is_spotlighted`, never the raw `p.spotlight`
    pointer. Under Furina's upgraded starter (R2) tier0 stops granting the
    selector token, so `p.spotlight` stays None for the entire run while
    every one of her cards reads as lit — and the C# card asks
    `SpotlightSystem.IsSpotlighted`, which honours `BothModes`
    (`EncorePerformance.cs:61-64`). On the same board the game copied and
    the sim copied nothing. The pointer guard was pure redundancy before the
    upgrade existed (with no designation `is_spotlighted` is False for
    everything, so `targets` is empty and the check below returns anyway),
    so it is deleted rather than widened: `if not targets` says the same
    thing in both worlds and cannot go stale behind a second lighting mode.
    """
    from tier0.content import loader
    p = state.player
    targets = [c for c in p.hand if is_spotlighted(state, c)
               and not c.kit_card]
    if not targets:
        return
    for _ in range(fx.get("amount", 1)):
        chosen = loader.get_card(state.rng.choice(targets).id)
        if "cost_override" in fx:
            chosen.cost_delta_this_combat = fx["cost_override"] - chosen.cost
        _add_token(state, chosen, "hand")
        state.emit("encore_performance_copy", card=chosen.id)


def _op_heal(state: CombatState, fx: dict, card: Card) -> None:
    p = state.player
    amount = fx["amount"]
    if state.salon_replacements_this_card:
        amount *= C.SALON_REPLACE_NUMERIC_MULT
    healed = min(amount, p.max_hp - p.hp)
    p.hp += healed
    state.emit("heal", amount=healed)


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
            token = loader.get_card(cid)
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
    chosen = fx.get("select", "random") == "chosen"
    sly_batch: list[Card] = []
    # `amount: hand_size` is how "discard your hand" is spelled -- resolved
    # ONCE, here, before the first card leaves, so it cannot chase its own
    # shrinking pool. The loop's own `if not pool: break` already handles a
    # hand smaller than the number asked for.
    for _ in range(_amount(state, fx.get("amount", 1))):
        pool = [c for c in state.player.hand if not c.kit_card]
        if not pool:
            break
        victim = _worst_card(pool) if chosen else state.rng.choice(pool)
        remove_instance(state.player.hand, victim)
        state.player.discard_pile.append(victim)
        state.discards_this_turn += 1
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
        # loop instead — see the batch note below.
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


def _op_exhaust_from(state: CombatState, fx: dict, card: Card) -> None:
    hand = state.player.hand
    # DEFECT FIX: the status branch used to rebuild the pool from `hand` and
    # so dropped the kit-card exemption two lines above -- a status-filtered
    # exhaust could eat the granted Burst, breaking the v1.9 invariant that
    # the kit never enters a pile. Filter the exempt pool instead.
    pool = [c for c in hand if not c.kit_card]   # same invariant as discard
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
        victim = _worst_card(pool) if chosen else state.rng.choice(pool)
        pool = [c for c in pool if c is not victim]
        remove_instance(hand, victim)
        state.player.exhaust_pile.append(victim)
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
    """Effect list walk including conditional branches."""
    for fx in effects:
        yield fx
        for branch in ("then", "else"):
            if isinstance(fx.get(branch), list):
                yield from _walk_effects(fx[branch])


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
        state.emit("discard", card=victim.id, chosen=True)
        discarded += 1
    gain = min(fx.get("sparks", discarded), discarded)
    if gain:
        gain_sparks(state, gain)


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
    "reaction_triggered_by_this",
    "reaction_triggered_this_turn",
    "killed_target",
    "killed_target_fatal",
    "drew_skill_this_card",
    "card_exhausted_this_turn",
    "hp_lost_this_turn",
    "enemy_intends_attack",
    "has_salon_members",
    "spotlight_set",
    "spotlight_moved_this_turn",
    "spotlight_unmoved_this_combat",
    "spotlighted_card_played_this_turn",
    # EB-118. Ownership is a yes/no on the sheet, so it is a name, not a
    # count prefix; the COUNTS are reachable as amounts.
    "exhaust_selection_has_companion",
    "exhaust_selection_has_personal",
})

# Parameterised predicates: prefix + an argument the branch parses itself.
# `target_has_power_` takes a power name (unbounded by design -- the next card
# that reads a power needs no new predicate); the rest take an integer.
PREDICATE_PREFIXES = frozenset({
    "target_has_power_",
    "self_has_power_",
    "exhaust_pile_at_least_",
    "charge_at_least_",
    "fanfare_at_least_",
    "encore_at_least_",
    # EB-118 §5.5: WHO is next to perform. Parameterised on the member name
    # rather than tabled per member, for the same reason the integer bars are
    # -- but the argument is closed here, because SALON_MEMBERS is: a typo'd
    # member is a load-time failure, not a branch that never fires.
    "leftmost_salon_member_",
    # EB-118. `_has_type_` takes a card TYPE (a closed vocabulary, validated
    # below); the other two take an integer like their neighbours.
    "exhaust_selection_has_type_",
    "exhaust_selection_cost_at_least_",
    "exhaust_selection_size_at_least_",
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
        if prefix == "leftmost_salon_member_":
            return arg in C.SALON_MEMBERS
        if prefix == "exhaust_selection_has_type_":
            return arg in CARD_TYPES
        # The integer forms must actually carry an integer. A typo'd
        # `fanfare_at_least_ten` would otherwise pass a name-only check and
        # raise from int() mid-combat -- the very failure being moved earlier.
        return arg.isdigit()
    return False


def _predicate(state: CombatState, name: str) -> bool:
    if name == "this_cost_zero":
        return state.current_card_cost == 0
    if name == "has_spark":
        return state.player.sparks > 0
    if name == "target_has_nonpyro_aura":
        # Snapshotted at card start — the card's own first hit may consume
        # the aura via reaction, which is exactly what the bonus rewards.
        return state.target_had_offelement_aura
    if name == "reaction_triggered_by_this":
        return state.reactions_this_card > 0
    if name == "reaction_triggered_this_turn":
        # Chevreuse Vanguard's Valor. RULED: ANY reaction counts, not
        # Overload-only -- must never be a dead draw off-Pyro/Electro.
        return state.reactions_this_turn > 0
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
    if name.startswith("charge_at_least_"):
        # Kokomi threshold read (v0.5 sheet fill). A THRESHOLD is not a
        # proportional read: it pays a flat, printed bonus once the bank
        # clears a bar, so it cannot participate in the multiplicative-read
        # risk that §2.2 rate-limits the per-point readers for. Charge is
        # still never spent here -- crossing the bar changes nothing about
        # the bank.
        return state.player.charge >= int(name.rsplit("_", 1)[1])
    if name == "card_exhausted_this_turn":
        return state.cards_exhausted_this_turn > 0
    if name == "hp_lost_this_turn":
        return state.hp_lost_this_turn > 0
    if name == "enemy_intends_attack":
        # Frozen enemies still attack under v1.5 (at -50%), so they count.
        return any(e.current_intent()["kind"] == "attack"
                   and e.sleep_turns == 0
                   for e in state.living_enemies)
    # --- Furina sheet-pass predicates ---
    if name == "has_salon_members":
        return state.player.powers.get("salon_member", 0) > 0
    if name.startswith("leftmost_salon_member_"):
        # EB-118 §5.5: which performer is NEXT -- the head of the FIFO queue,
        # the same end `salon_bow` pops, `salon_perform` acts on and a deploy
        # into a full stage displaces. Reads the queue, not the mirror
        # counter: powers['salon_member'] carries the count and cannot carry
        # identity. False on an empty stage for every member name.
        want = name[len("leftmost_salon_member_"):]
        salon = state.player.salon
        return bool(salon) and salon[0] == want
    if name == "spotlight_set":
        return state.player.spotlight is not None
    if name == "spotlight_moved_this_turn":
        # R2 makes the upgraded starter the SELECTOR-PAYOFF ENABLER: with the
        # selector card gone there is no designation event left to move, so
        # without this every selector-payoff card on her sheet (curtain_cue,
        # directors_cut) would become dead text the moment the relic was
        # taken -- the upgrade would silently SUBTRACT from her pool while
        # appearing to add to it. Mirrors C# SpotlightSystem.MovedThisTurn,
        # which is `BothModes(creature) || <the resource>` for this reason.
        return both_spotlight_modes(state) or state.spotlight_moved_this_turn
    if name == "spotlight_unmoved_this_combat":
        # Commitment payoff: designated once and never re-aimed. False
        # while nothing is designated (an empty stage is not commitment).
        return (state.player.spotlight is not None
                and state.spotlight_moves_this_combat <= 1)
    if name == "spotlighted_card_played_this_turn":
        return state.spotlighted_cards_this_turn > 0
    if name.startswith("fanfare_at_least_"):
        resources.note_fanfare_read(state, "threshold")
        # Clamped for consistency with every other reader. It cannot change
        # an answer today -- every printed threshold is positive, so a
        # negative meter fails either way -- and it is written this way so a
        # future `fanfare_at_least_0` reads as "she has any" rather than as
        # "always true, even mid-Hyperbeam-debt".
        return resources.readable(state.player) >= int(name.rsplit("_", 1)[1])
    if name.startswith("encore_at_least_"):
        return state.player.encore >= int(name.rsplit("_", 1)[1])
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


def retrieves_from_exhaust(card: Card) -> bool:
    """Does this card itself retrieve from the exhaust pile? (EB-118 §6.4
    constraint 3.)

    A card-shape property, read off the printed effect tree rather than a
    hand-set flag, so a future sheet row cannot arm the capability and forget
    to declare it. The C# twin is the IExhaustRetriever marker interface,
    which the generator stamps from this same shape.
    """
    return any(fx.get("op") == "recall_to_draw"
               and fx.get("from") == RECALL_EXHAUST_SOURCE
               for fx in _walk_effects(card.effects))


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
         target_had_offelement_aura, current_attack_bonus, sparks_at_play,
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


def _op_gain_charge(state: CombatState, fx: dict, card: Card) -> None:
    """Kokomi: explicit bonus-Charge effect line (kickoff §2.1 — premium
    cards may grant bonus Charge beyond the universal accrual). The base
    per-exhaust accrual lives at the funnel (refpowers), never here."""
    resources.gain_charge(state, _amount(state, fx.get("amount", 1)),
                          source=card.id)


def _op_summon_kurage(state: CombatState, fx: dict, card: Card) -> None:
    """Bake-Kurage as a persistent summon (v0.4 plan §1).

    The jellyfish holds the field for KURAGE_DURATION turns and pulses at
    the owner's turn end (player_turn_end_triggers). Stacks ARE turns
    remaining -- the oz_summon grammar -- so this REFRESHES to the full
    duration rather than adding to it: a second jellyfish is not a bigger
    jellyfish, and the Garment's Casket link refreshes through this same
    path. Duration is the only state; the pulse reads the Charge bank live
    at fire time, so a summon made at Charge 0 still grows all fight.
    """
    turns = _amount(state, fx.get("amount", C.KURAGE_DURATION))
    p = state.player
    p.powers["kurage_summon"] = max(p.powers.get("kurage_summon", 0), turns)
    KNOB_READS["KURAGE_DURATION"] = KNOB_READS.get("KURAGE_DURATION", 0) + 1
    state.emit("summon_kurage", turns=p.powers["kurage_summon"])


def _op_conscript(state: CombatState, fx: dict, card: Card) -> None:
    """Conscript (kickoff §2.3, the Commander verb).

    transform mode (default): transform a card in hand into a random
    same-nation Companion card; it costs CONSCRIPT_COST_DELTA less
    (floor 0) and gains Exhaust. Pays card identity, feeds Charge when the
    conscript is consumed (played -> exhausted -> funnel). Net deck delta
    is ZERO, which is what makes the verb legal at Common under the
    Kokomi deck-size law.

    create mode ({mode: create}): the SAME conscription grammar but the
    recruit is created into hand instead of replacing a card — net
    POSITIVE delta, therefore Uncommon+ only (lint-enforced on her sheet).

    The transformed pick is the _worst_card in hand (the player conscripts
    chaff, not payoffs), excluding kit cards (v1.9 invariant) and cards
    that are already companions (re-conscripting a recruit is rules-legal
    but pilot-daft; excluding it here is pilot judgement, not law).
    Replacement happens AT the original index (CardCmd.Transform parity,
    same argument as transform_in_hand)."""
    from tier0.content import loader                # late import (cycle)
    pool = loader.companion_pool(fx.get("nation", "inazuma"))
    for _ in range(_amount(state, fx.get("amount", 1))):
        recruit = copy.deepcopy(state.rng.choice(pool))
        if "cost_override" in fx:
            recruit.cost = fx["cost_override"]
        elif isinstance(recruit.cost, int):
            recruit.cost = max(0, recruit.cost + C.CONSCRIPT_COST_DELTA)
        recruit.exhaust = True
        recruit.conscripted = True
        if fx.get("mode") == "create":
            _add_token(state, recruit, "hand")
            continue
        hand = state.player.hand
        # ROTATION LAW ([USER] 2026-08-23): a Muster transforms one of HER
        # cards. A Status or a Curse is not a recruit -- conscripting a
        # Dazed used to be free curse removal that also paid Charge when the
        # recruit rotated out. Unconditional here (the verb is hers alone;
        # the shared exhaust_from keys the same law on the relic hook).
        candidates = [c for c in hand
                      if not c.kit_card and not c.is_companion
                      and not c.is_junk]
        if not candidates:
            state.emit("conscript_whiffed")
            return
        victim = _worst_card(candidates)
        hand[hand.index(victim)] = recruit
        state.emit("conscript", was=victim.id, into=recruit.id)


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


OPS = {
    "damage": _op_damage,
    "block": _op_block,
    "block_next_turn": _op_block_next_turn,
    "draw": _op_draw,
    "draw_while": _op_draw_while,
    "energy": _op_energy,
    "apply_power": _op_apply_power,
    "apply_aura": _op_apply_aura,
    "place_bomb": _op_place_bomb,
    "detonate": _op_detonate,
    "move_bombs": _op_move_bombs,
    "modify_bombs": _op_modify_bombs,
    "burst_energy": _op_burst_energy,
    "swirl": _op_swirl,
    "refresh_all_auras": _op_refresh_all_auras,
    "buff_next_attack": _op_buff_next_attack,
    "cost_mod": _op_cost_mod,
    "gain_spark": _op_gain_spark,
    "spend_spark": _op_spend_spark,
    "gain_encore": _op_gain_encore,
    "spend_encore": _op_spend_encore,
    "spotlight_designate": _op_spotlight_designate,
    "gain_fanfare_floor": _op_gain_fanfare_floor,
    "raise_fanfare_cap": _op_raise_fanfare_cap,
    "crash_fanfare": _op_crash_fanfare,
    "salon_bow": _op_salon_bow,
    "salon_rotate": _op_salon_rotate,
    "salon_perform": _op_salon_perform,
    "generate_guest_star": _op_generate_guest_star,
    "copy_spotlighted_in_hand": _op_copy_spotlighted_in_hand,
    "heal": _op_heal,
    "add_card": _op_add_card,
    "discard": _op_discard,
    "discard_for_sparks": _op_discard_for_sparks,
    "exhaust_from": _op_exhaust_from,
    "scry_discard": _op_scry_discard,
    "conditional": _op_conditional,
    "repeat_this": _op_repeat_this,
    "grow_damage": _op_grow_damage,
    "chance_bomb_per_detonation": _op_chance_bomb_per_detonation,
    "copy_companion_in_hand": _op_copy_companion_in_hand,
    "replay_next_companion": _op_replay_next_companion,
    "copy_companions_played_this_combat": _op_copy_companions_played,
    # --- Kokomi (kickoff v1 §7) ---
    "gain_charge": _op_gain_charge,
    "conscript": _op_conscript,
    "summon_kurage": _op_summon_kurage,          # v0.4 O4 salvage
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
    # Control provenance (§2.2a) — with the kickoff ask §6.7 attribution
    # (PROPOSED): a CONSCRIPTED companion is self-sourced (Kokomi paid a
    # card of her own deck for it), so its control does not count toward
    # SUPPORT_CARRY; drafted companions count normally.
    state.current_card_companion = (card.is_companion
                                    and not card.conscripted)
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
    state.discards_this_card = 0
    state.last_drawn_type = ""
    state.salon_replacements_this_card = 0
    state.detonations_at_card_start = state.detonations_total
    state.repeat_requested = 0
    # Predicate snapshot: does the default target hold an off-element aura?
    living = state.living_enemies
    tgt = min(living, key=lambda e: e.hp) if living else None
    state.target_had_offelement_aura = bool(
        tgt and tgt.aura and tgt.aura != state.player.element)
    # Per-card flat attack bonus. Computed by the shared pure helper so the
    # pilot's estimate cannot drift from what actually resolves (v0.4 W1);
    # the two side effects the helper must NOT have live here instead:
    # Bennett's next_attack_up is CONSUMED by this play, and the Garment
    # divisor's KNOB_READS tick counts real resolutions, not estimates.
    bonus = flat_attack_bonus(state, card, state.current_card_cost)
    if card.type == "attack":
        p = state.player
        p.powers.pop("next_attack_up", 0)
        if p.powers.get("ceremonial_garment", 0) and p.charge:
            KNOB_READS["GARMENT_CHARGE_DIVISOR"] = (
                KNOB_READS.get("GARMENT_CHARGE_DIVISOR", 0) + 1)
            # EB-78 (2): the same resolution, tallied for the reads-per-turn
            # distribution. Sharing this site's condition is the point --
            # KNOB_READS already established it as the place a real Garment
            # read happens, as opposed to the pilot's estimate of one.
            resources.note_charge_read(state, "garment", card=card.id)
        # Garment attack rider (v0.4 §1.3): while the state holds, her
        # attacks ALSO restore the party -- her burst's actual behaviour,
        # translated to Block under the R52 healing law via the Charlotte
        # precedent. Applied on the play, before the damage resolves, so
        # it is up in time for the same turn's enemy swing.
        if p.powers.get("ceremonial_garment", 0):
            p.block += C.GARMENT_ATTACK_BLOCK
            state.emit("block", amount=C.GARMENT_ATTACK_BLOCK)
            KNOB_READS["GARMENT_ATTACK_BLOCK"] = (
                KNOB_READS.get("GARMENT_ATTACK_BLOCK", 0) + 1)
    state.current_attack_bonus = bonus

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


def flat_attack_bonus(state: CombatState, card: Card, cost: int) -> int:
    """The per-card flat bonus every attack card carries, as a PURE READ.

    Bennett's next_attack_up, Nicole's celestial_gift, the Bennett-burst
    attack_up_this_turn window, Spark Knight Style's zero-cost rider,
    Rapturous Applause's Fanfare term, and Kokomi's Ceremonial Garment
    Charge read all land here — flat, folded in before strength/vulnerable.

    Consumes nothing and touches no telemetry, so the pilot may call it to
    price a play it has not made (v0.4 W1: the pilot previously saw NONE of
    these, so it valued every attack at its printed number and played
    straight through its own buff windows -- most visibly the Garment, where
    a priest-median bank is worth more than most cards' printed damage).
    The consuming pop and the KNOB_READS tick stay at the real call site.
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
    if cost == 0:
        bonus += p.powers.get("zero_cost_attacks_up", 0)
    # Rapturous Applause: attacks +N per 10 Fanfare ("stacks grant flat
    # power bonuses", kickoff §4). Reads the pool, spends nothing.
    n = p.powers.get("fanfare_attack_per10", 0)
    if n:
        resources.note_fanfare_read(state, "attack_power")
        bonus += n * (resources.readable(p) // 10)
    # Ceremonial Garment (Kokomi kit, kickoff §2.2 Shape B): while the state
    # is active her attack cards READ Charge, scaled down by the divisor
    # knob — repeated-but-bounded payoff, never a spend.
    if p.powers.get("ceremonial_garment", 0) and p.charge:
        bonus += p.charge // C.GARMENT_CHARGE_DIVISOR
    return bonus


# --- player-side power triggers, called from the combat loop ---

def player_turn_start_triggers(state: CombatState) -> None:
    p = state.player
    if ("ethereal_spotlight" in p.relic_hooks           # Furina's relic
            and not both_spotlight_modes(state)):
        # Selector to hand each turn (kickoff §3.1). Ethereal: unplayed
        # copies vanish at end of turn (combat loop), so the deck never
        # silts up with selectors. Emits its own event, NOT add_card --
        # whether selector cadence counts toward A5 velocity is an open
        # accounting ruling; until ruled it must not inflate the axis.
        #
        # THE SELECTOR STOPS ARRIVING under R2's upgrade: with both modes
        # always on it has nothing left to choose, so C# CurtainNeverFalls
        # deliberately does NOT override AfterPlayerTurnStart the way the
        # base EtherealSpotlightRelic does. Funnel Contract §3 is intact --
        # the designation funnel is not removed, moved or renamed and every
        # existing caller (a drafted `spotlight_designate` card) still routes
        # through it. An upgraded Furina simply never FIRES it again.
        from tier0.content import loader                # late import (cycle)
        if not any(c.id == "ethereal_spotlight" for c in p.hand):
            # HAND-FULL FALLBACK (sitting 2026-08-06, family X14 leg (b)):
            # "if the hand is full, one random card is discarded before the
            # spotlight is added." Before this the grant was simply skipped,
            # so the relic that exists to guarantee Furina a play was exactly
            # what a jammed hand starved.
            #
            # The victim pool is _op_discard's pool rule -- kit cards are
            # never fodder (the v1.9 invariant) -- and the draw comes from the
            # DEDICATED selector stream, not state.rng.
            if len(p.hand) >= C.MAX_HAND_SIZE:
                pool = [c for c in p.hand if not c.kit_card]
                if pool:
                    victim = state.selector_rng.choice(pool)
                    remove_instance(p.hand, victim)
                    p.discard_pile.append(victim)
                    state.discards_this_turn += 1
                    state.emit("discard", card=victim.id)
                    state.emit("selector_hand_full_discard", card=victim.id)
            # A hand of nothing but kit cards has no legal victim; the grant is
            # skipped as before rather than breaking the kit invariant.
            if len(p.hand) < C.MAX_HAND_SIZE:
                p.hand.append(loader.get_card("ethereal_spotlight"))
                state.emit("selector_granted")
    n = p.powers.pop("block_next_turn", 0)              # Charlotte
    if n:
        # Deliberately raw: this payout predates both block funnels and
        # neither may touch it (Dexterity must not scale power block; the
        # power that banked it has expired by now). A future block-gain hook
        # will not see this gain unless it is rerouted on purpose.
        p.block += n
        state.emit("block", amount=n)
    # --- the two Ancient income powers (R127 / EB-30m) ------------------
    # PLACED ABOVE `salon_tick` DELIBERATELY, and above the whole income
    # group below it (celestial_gift / masque_red_death / spark_per_turn all
    # sit AFTER the upkeep). That asymmetry is the point rather than an
    # accident of insertion order: EB-2 was the C#-side race between
    # SalonPowers' upkeep and FurinaResources' Encore income inside one
    # `AfterPlayerTurnStart` broadcast, and this is the sim declaring which
    # way that race falls -- income BEFORE upkeep, so the card's printed
    # "at the start of your turn" funds the Salon ticks of the same turn
    # instead of the next one. Do not tidy these down to join the other
    # per-turn blocks; tier0/tests/test_eb30m_ancients.py pins the order
    # against exactly that edit.
    #
    # THE C# NOW MATCHES BY CONSTRUCTION (2026-08-07): both income powers
    # were staged out of `AfterPlayerTurnStart` into `BeforeSideTurnStart`,
    # a strictly earlier broadcast, so the upkeep can no longer run first.
    # That puts them before the C# hand draw as well, which is where this
    # hook already sat -- and it is inert either way, because neither power
    # reads the hand, the deck or the energy: each only moves a meter.
    n = p.powers.get("charge_per_turn", 0)         # Princess of Watatsumi
    if n:
        resources.gain_charge(state, n, "charge_per_turn")
    n = p.powers.get("encore_per_turn", 0)         # All the World's a Stage
    if n:
        resources.gain_encore(state, n, source="encore_per_turn")
    salon_tick(state)                                   # Furina (kickoff §5)
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
    n = p.powers.get("spark_per_turn", 0)               # Endless Fireworks
    if n:
        gain_sparks(state, n)
    n = p.powers.get("bomb_and_spark_per_turn", 0)      # Playtime Forever
    for _ in range(n):
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            enemy.bombs.append(Bomb(damage=C.PLAYTIME_BOMB_DAMAGE,
                                    turn_placed=state.turn))
            state.emit("bomb_placed", target=enemy.name,
                       damage=C.PLAYTIME_BOMB_DAMAGE)
        gain_sparks(state, 1)


def salon_tick_amount(state: CombatState, member: str, paid: bool) -> int:
    """What this member's tick is worth RIGHT NOW: the printed base plus the
    Focus term and Grand Salon (_salon_amount), then the dry reduction when
    the member cannot pay. Crabaletta and Chevalmarin print damage, the Usher
    prints Block; each member prints exactly one numeric, so one reader
    answers for all three.

    The mirror of C# SalonMemberPower.TickValue, and the reason both exist:
    the resolution path and every reader of "what will this member do" must
    be the same expression, not two copies that agree until one is edited.
    """
    spec = C.SALON_MEMBERS[member]["tick"]
    base = spec.get("damage", 0) or spec.get("block", 0)
    amt = _salon_amount(state, base)
    return amt if paid else int(amt * C.SALON_DRY_DAMAGE_MULT)


def salon_member_act(state: CombatState, member: str) -> bool:
    """ONE member's slot passive, with the full standard bill: the Encore
    upkeep, the dry three-quarters when it goes unpaid, the Focus/Grand-Salon
    scaling, the burst particle, and the `salon_tick` telemetry row.

    THE ONLY implementation of a member acting. `salon_tick` runs it once per
    member at the start of the player turn; the `salon_perform` op runs it on
    demand for the leftmost member. A second copy of this body is the defect
    this shape exists to make impossible -- a card that performs a member
    must not be able to drift from the upkeep that performs the same member.

    Returns False when the stage cannot act at all (the player is dead, or
    there is no living enemy left to act against) -- the caller's break
    condition, kept here so the on-demand verb inherits it rather than
    restating it.
    """
    p = state.player
    if not p.alive or not state.living_enemies:
        return False
    spec = C.SALON_MEMBERS[member]["tick"]
    paid = p.encore >= C.SALON_TICK_ENCORE_COST
    state.emit("salon_tick", member=member, paid=paid)
    if paid:
        # No `card`: the upkeep bill is the STAGE's, not any one card's,
        # and the per-member cut already exists on the `salon_tick` row
        # that tier05.encore_telemetry reads.
        resources.spend_encore(state, C.SALON_TICK_ENCORE_COST,
                               "salon_upkeep")
    if spec.get("damage", 0):
        enemy = state.rng.choice(state.living_enemies)
        deal_damage_to_enemy(state, enemy,
                             salon_tick_amount(state, member, paid),
                             element="hydro", source="salon")
    if spec.get("block", 0):
        amt = salon_tick_amount(state, member, paid)
        p.block += amt
        state.emit("block", amount=amt)
    if p.burst_max:
        # §1 particle economy
        resources.gain_burst(state, C.SALON_TICK_BURST, "salon_tick")
    return True


def salon_tick(state: CombatState) -> None:
    """Salon v2 (rework plan §1): each active member performs its UNIQUE
    slot passive at the START of the player turn, in queue order
    (Klee-bomb timing, not Oz timing -- the sheet-pass 1 measurement
    decision stands: end-of-turn upkeep drained the buffer BEFORE enemy
    hits and zeroed her elite A4; start-of-turn ticks let absorption take
    first bite and the upkeep eats what survived the night). Upkeep is
    unchanged from v1: each member pays 1 Encore for full numerics; a dry
    member cannot overdraw HP and resolves numerics at three-quarters
    (hydro application on damage ticks still applies either way). Numeric
    amounts carry the Fanfare Focus term + Grand Salon (_salon_amount)."""
    p = state.player
    # D8 telemetry (salon UI sprint, 2026-07-28). EMIT-ONLY: the snapshot is
    # taken BEFORE the first member spends, because the question the D8 lever
    # is about is whether the stage arrives at upkeep with enough fuel to run
    # itself -- read it after the loop and a stage that drained itself to
    # exactly zero looks identical to one that never had a member at all.
    if p.salon:
        state.emit("salon_upkeep", members=len(p.salon), encore=p.encore,
                   cost=C.SALON_TICK_ENCORE_COST * len(p.salon))
    for member in list(p.salon):
        if not salon_member_act(state, member):
            break


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
    if p.powers.get("kurage_summon", 0):                # Kokomi (v0.4 §1)
        # The jellyfish's turn-end pulse: a little damage that READS the
        # Charge bank (never spends it), hydro application, and Block for
        # the party. This is where O4 puts the periodic output that v0.3
        # had loaded onto the Burst -- canon keeps the metronome on the
        # summon, so the instrument stops reading it as frontload.
        # R73/G2: "Before Sun and Moon" adds +1 to the MULTIPLIER, and
        # stacks -- two copies read the bank at +2. Stacking was ratified
        # deliberately over a ban ([USER], G2): draft dilution self-corrects
        # at full roster, and the compounding pair is a C4 telemetry watch
        # rather than a rule. Note this multiplies an uncapped, never-spent
        # bank (R80), so it is the steepest term the sheet can offer and the
        # only sanctioned way back up from R73's cut.
        amp = p.powers.get("kurage_amp", 0)
        multiplier = C.KURAGE_PULSE_PER_CHARGE + amp
        dmg = C.KURAGE_PULSE_BASE + p.charge * multiplier
        KNOB_READS["KURAGE_PULSE_PER_CHARGE"] = (
            KNOB_READS.get("KURAGE_PULSE_PER_CHARGE", 0) + 1)
        resources.note_charge_read(state, "kurage_pulse")   # EB-78 (2)
        # P2 runaway telemetry (playtest sprint, Track P). Report-only; no
        # rule reads this event. The x4 bank read is the one term in the kit
        # that only ever grows, and [USER]'s standing caveat is "watch act 3".
        # Emitting the pulse SIZE (with the bank that produced it) means the
        # next sheet to add a Charge source re-arms that question by itself,
        # instead of it depending on someone remembering to ask. Emitted
        # before the living-enemies check so a pulse into an empty board is
        # still a sample of the CURVE -- filtering by what happened to be
        # standing would bias the tail downward exactly when fights end fast.
        # `amp` rides the event so C4's overlap watch can separate the two
        # ways the tail rises -- a bigger bank, or a bought multiplier --
        # without re-deriving either from the deck list.
        state.emit("kurage_pulse", amount=dmg, charge=p.charge,
                   amp=amp, landed=bool(state.living_enemies))
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            deal_damage_to_enemy(state, enemy, dmg, element="hydro",
                                 source="companion")
        # Block lands whether or not an enemy was standing: the healer's
        # mending is Block under the R52 healing law. The BASELINE is off
        # since the v0.4 starter rework (KURAGE_PULSE_BLOCK 0); the mending
        # is now DRAFTED, via the kurage_ward power (Kurage's Oath). Both
        # terms ride the same line so restoring the baseline stays a
        # one-constant change.
        blk = C.KURAGE_PULSE_BLOCK + p.powers.get("kurage_ward", 0)
        if blk:
            p.block += blk
            state.emit("block", amount=blk)
            KNOB_READS["KURAGE_PULSE_BLOCK"] = (
                KNOB_READS.get("KURAGE_PULSE_BLOCK", 0) + 1)
        p.powers["kurage_summon"] -= 1
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
            if p.burst_max:
                resources.gain_burst(
                    state, C.WITCHS_FLAME_BURST, "witchs_flame")
            state.emit("witchs_flame_consumed", target=enemy.name,
                       burst_energy=C.WITCHS_FLAME_BURST)
    if p.powers.get("solar_isotoma", 0):                # Albedo, 3 turns
        p.powers["solar_isotoma"] -= 1
    p.powers.pop("attack_up_this_turn", None)           # Bennett burst
