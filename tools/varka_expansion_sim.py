#!/usr/bin/env python3
"""VARKA EXPANSION -- the paper's sec.5 sim (Prototype stage, exploration,
not a Balance measurement).

    .venv/Scripts/python.exe -m tools.varka_expansion_sim --seeds 500 --seed 7 --jobs 14 --json out.json
    .venv/Scripts/python.exe -m tools.varka_expansion_sim --report out.json [--against old.json]

Answers sec.5.2 of `review/active/varka-expansion-2026-10-01.md` on the
BUILT rows (tier0 with `C.SWIRL_PAYS` on for THIS PROCESS ONLY, as the
Varka tests switch it; nothing on disk moves). The pool is read off whatever checkout
runs it -- every `proto_vk_` row of rarity Common/Uncommon/Rare -- so the
same file run on the pre-expansion commit (41 rows) and on main (78) is the
paired pool comparison (`--against`).

RUN -- the stylised act the earlier Varka sims used (PR #768,
`tools/kokomi_expansion_sim.py`): the tier-0.5 act-1 pools, floors
N N N N E R N N E R B, then a rest and an act-2 boss from the act-2 boss pool.
A card reward of three after every non-boss-2 fight (rarity C/U/R 60/37/3
after a normal fight, 50/40/10 after an elite or the boss), rests heal 30%.
Boreas's Fang and nothing else: no potions, gold, shops, upgrades or events.
Encounters, HP rolls and offers come from pilot-independent streams, so every
pilot meets the same fights and offers (paired).

GAUNTLET -- the deck each drafter WOULD carry (all nine offers drafted as if
every fight were won) fights every act-1 elite, act-1 boss and act-2 boss at
full HP. Deck strength apart from attrition.

STARTS -- the starter Knight is one of four. Every pilot runs every seed on
the four starts the default drafter does, except the mono-element pilots,
which run their own element's start only (a mono deck is built off its own
starter Knight) and are compared against the default drafter on that start.

DRAFTERS -- the default (`tier05.draft.score_offer`, archetype "generic",
skip under `C.DRAFT_SKIP_THRESHOLD`) and seven forced decks (paper sec.2's
table; deck lists in DECKS below, the paper's "Deck" column for the new
cards, the existing cards by what they read). A forced drafter scores a card
of its deck 10 (a Power or Rare cap 1, else cap 2; a Knight of its element
cap 3), a "support" card 7 (cap 2), a card that works against the deck -1
(mono pilots: another element's Knights and payoffs), anything else the
default's own score. The default drafter prices the `varka` op at 0 (a
deliberate zero in `tier05/draft.py`), so a row that op dominates would never
be taken; the harness gives every pool row the default scores under the skip
line against the starter the median of the others (`_nominal`), Kokomi's
fix.

THE REBALANCE (review/active/varka-rebalance-2026-10-03.md, aoe-trim sec.4;
built 2026-10-03, PR #863): the `elem_` pilots are the paper's borrowing decks
(`deck_lists`), and `report_bars` reads its bars (starter spread, element
spread, cross-element plays, Block, multi-target share, the paper's cards,
and with `--against` a paired comparison). The PR #863 measurement ran these
rows as a sim overlay before they reached the sheet; its tables are in the
PR body. `--no-gauntlet` skips the gauntlet's fights (at full HP it wins
every act-1 fight and loses every act-2 boss, so it separates nothing) and
keeps its drafts.

    .venv/Scripts/python.exe -m tools.varka_expansion_sim --seeds 2400 --seed 7 --jobs 15 --no-gauntlet --json new.json
    .venv/Scripts/python.exe -m tools.varka_expansion_sim --report new.json --against old.json

THE PLAY PILOT is the stock `generic` pilot, as the open-Oath paired sim
used, with one INSTRUMENT SURFACE (not a design claim): the `varka` and
`add_knight` ops, which the stock scorer cannot see, are valued as their
nearest stock op (`_translate`) so it plays them. Nothing in the engine's
resolution moves.

THE DISCARD SEQUENCER (2026-10-03, [USER]: "Agreed - let's make the sim
useful."): the second INSTRUMENT SURFACE. The stock scorer has no plan for
a turn, so it played Short Circuit last at 0 Energy, never played Chain
Lightning after a discard and did not price the cards Violet Storm throws
away. `_electro_pick` orders his four discard cards before the stock pilot
picks; it prices each card in hand by the stock scorer's own value with its
Energy charge added back (`_gross`) and a turn by a greedy best-per-Energy
fill (`_plan`):
  * SHORT CIRCUIT now when the hand after its discards, plus its draws and
    its Energy (and Chain Lightning's discount), is worth more than the
    whole hand without it; its discards are the lowest-value cards
    (`_discard_victims`, the chosen-discard pick, is replaced for this
    process only). A draw is priced as a typical card of the draw pile (its
    median by value; the pilot never reads the pile's order). Since the
    Short Circuit change (2026-10-03: discard 2, draw 2 [3], gain 1 Energy)
    the amounts are read off the card, as they always were.
  * CHAIN LIGHTNING after the discards: Short Circuit goes first when it is
    worth it, and its discount is in the plan that says so.
  * VIOLET STORM now when its hits on the hand as it stands are worth at
    least the best turn on the rest of the hand plus its hits on what that
    leaves; otherwise held (played at the end of the turn if nothing else
    is).
  * STORM BATTERY before either discard card, with the hand still full.
Nothing the engine resolves moves; the choices are the player's.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics as st
import sys
import traceback
from collections import Counter, defaultdict

TEMPLATE = ["N", "N", "N", "N", "E", "R", "N", "N", "E", "R", "B"]
RARITY = {"N": (60, 37, 3), "E": (50, 40, 10), "B": (50, 40, 10)}
ELEMENTS = ("pyro", "hydro", "electro", "cryo")
P = "proto_vk_"

# Varka defence (review/active/varka-defence-2026-10-01.md, 2026-10-01):
# Favonian Standard left FOCUS and Four Banners left SWITCH with their cards;
# the total-Oath and element-change Block (Gale Mantle, Windborne Resolve)
# joins SWITCH, the paper's "split and switch decks". Gust Ward is in no list
# (every deck's filler; the default scores price it).
# The combo pass (review/active/varka-combo-pass-2026-10-04.md, 2026-10-04):
# Oath of the Knights and Knightly Guard left FOCUS, West Wind Shield left
# GALE, Gale Mantle and Tailwind Guard left SWITCH with their cards; Pyro's
# Exhaust engine and Cryo's two status payoffs join their PAYOFFS.
FOCUS = ["oathsworn_strike", "eye_of_the_storm",
         "stormward_stance",
         "dawn_winds_march", "azure_devour", "sworn_brotherhood",
         "northwind_avatar", "tailwind_stride",
         "pathfinders_mark", "vow_of_the_blade",
         "unwavering_banner", "oath_unto_death", "grand_masters_verdict",
         "wolfpack", "oathbound_aegis"]
KNIGHTS = {
    "pyro": ["amber_baron_bunny", "amber_sharpshooter",
             "diluc_searing_onslaught"],
    "hydro": ["barbara_show_begin", "barbara_whisper_of_water",
              "barbara_wellspring_hymn"],
    "cryo": ["kaeya_frostgnaw", "mika_starfrost_swirl", "eula_icetide_vortex"],
    "electro": ["lisa_violet_arc", "razor_claw_and_thunder",
                "lisa_pulsating_witch"],
}
# Element identities (review/active/varka-element-identities-2026-10-01.md,
# 2026-10-01): Retaliating Tide is Hydro's Rare in Unbroken Tide's place, and
# Electro's list gains the four discard-and-spend cards. Pressure Front left
# GALE and Four Winds' Accord left SWITCH with their cards.
# The rebalance (sec.4): each element's borrowing payoff joins its list.
PAYOFFS = {"pyro": ["blazing_charge", "wildfire_oath", "kindled_edge",
                    "stoke_the_flames", "ember_cleave", "pyre_oath"],
           "hydro": ["tidal_bulwark", "retaliating_tide", "rippling_guard"],
           "cryo": ["glacial_edict", "absolute_zero", "frost_ward",
                    "shatter", "deep_freeze"],
           "electro": ["static_field", "thundering_verdict", "charged_lunge",
                       "short_circuit", "chain_lightning", "violet_storm",
                       "storm_battery"]}
GALE = ["gale_sweep", "crosswind", "rising_gale", "tempest_charge",
        "jean_dandelion_breeze", "storm_surge", "wall_of_gales",
        "converging_winds", "eye_wall",
        "crosscurrent", "twin_gales", "downburst", "eye_of_stormterror"]
SWITCH = ["shifting_gale", "cycle_of_seasons", "windborne_resolve",
          "weathervane",
          "tempest_of_the_four_winds", "twin_gales", "oathbound_aegis",
          "change_of_guard", "boreas_unbound",
          "rally_to_the_banner"]
MUSTER = ["knights_roll_call", "grand_masters_order", "knightly_strike",
          "assembly_at_the_cathedral", "charge_of_the_knights",
          "the_order_answers"]
ALL_KNIGHTS = [k for ks in KNIGHTS.values() for k in ks] + [
    "noelle_steadfast_maid"]


def _deck(core, support=(), against=()):
    return {"core": [P + c for c in core], "support": [P + c for c in support],
            "against": [P + c for c in against]}


DECKS = {
    **{f"mono_{el}": _deck(
        KNIGHTS[el] + PAYOFFS[el], FOCUS + ["noelle_steadfast_maid"],
        [k for e2 in ELEMENTS if e2 != el
         for k in KNIGHTS[e2] + PAYOFFS[e2]])
       for el in ELEMENTS},
    "gale": _deck(GALE),
    "switch": _deck(SWITCH, [k for ks in KNIGHTS.values() for k in ks]),
    "muster": _deck(MUSTER, ALL_KNIGHTS),
}
#: Rebalance sec.4's "borrows" for Electro: the generic draw cards.
GENERIC_DRAW = ["rising_gale", "tempest_charge", "tailwind_stride",
                "change_of_guard", "vow_of_the_blade", "dawn_patrol",
                "eye_of_stormterror", "noelle_steadfast_maid"]


def deck_lists():
    """The forced decks. The `elem_` pilots are the rebalance
    paper's borrowing decks (sec.4's "Borrows" column, read as a drafter):
    their element's Knights and payoffs are core, every OTHER element's
    Knights (the appliers) are support beside the Oath cards, and only the
    other elements' payoffs work against them. Electro also borrows the
    generic draw cards."""
    payoffs = {el: list(PAYOFFS[el]) for el in ELEMENTS}
    decks = {
        **{f"mono_{el}": _deck(
            KNIGHTS[el] + payoffs[el], FOCUS + ["noelle_steadfast_maid"],
            [k for e2 in ELEMENTS if e2 != el
             for k in KNIGHTS[e2] + payoffs[e2]])
           for el in ELEMENTS},
        **{f"elem_{el}": _deck(
            KNIGHTS[el] + payoffs[el],
            FOCUS + ["noelle_steadfast_maid"]
            + [k for e2 in ELEMENTS if e2 != el for k in KNIGHTS[e2]]
            + (GENERIC_DRAW if el == "electro" else []),
            [k for e2 in ELEMENTS if e2 != el for k in payoffs[e2]])
           for el in ELEMENTS},
        "gale": _deck(GALE),
        "switch": _deck(SWITCH, [k for ks in KNIGHTS.values() for k in ks]),
        "muster": _deck(MUSTER, ALL_KNIGHTS),
    }
    return decks, payoffs


DECKS.update({k: v for k, v in deck_lists()[0].items()
              if k.startswith("elem_")})
PILOTS = ("default",) + tuple(DECKS)


def element_of():
    """{card id: Oath element} -- the Knights, the starter Knights and each
    element's payoffs; every other row is generic (absent)."""
    from tier0.engine import varka_oath as V
    out = {cid: el for el, cid in V.STARTER_KNIGHT_IDS.items()}
    _, payoffs = deck_lists()
    for el in ELEMENTS:
        for c in KNIGHTS[el] + payoffs[el]:
            out[P + c] = el
    return out


def starts_for(pilot):
    if pilot.startswith(("mono_", "elem_")):
        return (pilot[5:],)
    return ELEMENTS


# --- the process switch and the scorer surface --------------------------------

_ENABLED = False


def enable():
    global _ENABLED
    if _ENABLED:
        return
    from tier0 import constants as C
    C.SWIRL_PAYS = True
    from tier0.content import loader
    loader.reset_arm_caches()
    from tier0.pilot import policy
    orig = policy._active_effects

    def active(state, effect_list, card=None):
        for fx in orig(state, effect_list, card):
            yield from _translate(state, fx)

    policy._active_effects = active
    from tier0.engine import effects
    orig_victims = effects._discard_victims

    def victims(state, n, chosen):
        if not chosen:
            yield from orig_victims(state, n, chosen)
            return
        yield from lowest_victims(state, n)

    effects._discard_victims = victims
    _ENABLED = True


def _translate(state, fx):
    """A `varka` / `add_knight` clause as its nearest stock op, for the stock
    scorer only (the engine resolves the real op)."""
    op = fx.get("op")
    if op == "add_knight":
        yield {"op": "draw", "amount": 1}
        return
    if op != "varka":
        yield fx
        return
    from tier0.engine import varka_oath as V
    led = V.ledger(state.player)
    cur = led.current if led else None
    oath = led.oath if led else {e: 0 for e in ELEMENTS}
    cur_oath = oath[cur] if cur else 0
    n_en = len(state.living_enemies)
    kind = fx.get("kind")
    base, per, amt = fx.get("base", 0), fx.get("per", 0), fx.get("amount", 0)
    el = cur or "pyro"
    # An application of an Oath element by his card gains 1 Oath of it (and
    # feeds the next Swirl): one self Power stack, the stock scorer's setup.
    oath_proxy = {"op": "apply_power", "power": "vk_oath_proxy", "amount": 1,
                  "target": "self"}
    if kind in ("apply_current_element", "pathfinders_mark"):
        if cur or kind == "pathfinders_mark":
            yield {"op": "apply_aura", "element": el,
                   "target": "all_enemies" if fx.get("upgraded") else "enemy"}
            yield oath_proxy
    elif kind == "crosscurrent":
        fresh = any(e.aura for e in state.living_enemies)
        if fresh:
            # The Swirl's payout, twice (`varka_oath._pay`), plus its Oath.
            if cur == "pyro":
                yield {"op": "damage", "amount": 2 * V.SWIRL_PYRO_DAMAGE,
                       "target": "enemy"}
            elif cur == "hydro":
                yield {"op": "block", "amount": 2 * V.SWIRL_HYDRO_BLOCK}
            elif cur == "cryo":
                yield {"op": "apply_power", "power": "vulnerable",
                       "amount": 2 * V.SWIRL_CRYO_VULNERABLE,
                       "target": "enemy"}
            elif cur == "electro":
                yield {"op": "damage",
                       "amount": 2 * V.SWIRL_ELECTRO_DAMAGE_ALL,
                       "target": "all_enemies"}
            yield {"op": "swirl", "target": "enemy"}
            yield oath_proxy
    elif kind == "current_element_strike":
        yield {"op": "damage", "amount": base, "target": "enemy"}
    elif kind == "blazing_charge":
        yield {"op": "damage", "amount": base + per * oath["pyro"],
               "target": "enemy"}
    elif kind == "thundering_verdict":
        # Element identities: X times (`_est` prices "X" as the bank).
        yield {"op": "damage", "amount": base + per * oath["electro"],
               "target": "all_enemies", "times": "X"}
    elif kind == "electro_strike":
        yield {"op": "damage", "amount": base, "target": "enemy"}
        yield oath_proxy
    elif kind == "electro_all":
        yield {"op": "damage", "amount": base, "target": "all_enemies"}
        yield oath_proxy
    elif kind == "violet_storm":
        # One hit per OTHER card in hand (the card itself is in hand while
        # it is priced); the discard itself is not priced (the stock scorer
        # has no value for losing the hand).
        n = max(0, len(state.player.hand) - 1)
        if n:
            yield {"op": "damage", "amount": base, "target": "random_enemy",
                   "times": n}
    elif kind == "awakening":
        more = amt if any(e.aura == "electro"
                          for e in state.living_enemies) else 0
        yield {"op": "damage", "amount": base + more, "target": "enemy"}
        yield oath_proxy
    # --- the rebalance's kinds (2026-10-03) ---

    elif kind == "kindled_edge":
        # The "more" if any enemy wears an aura Pyro reacts with.
        react = any(e.aura in ("hydro", "cryo", "electro")
                    for e in state.living_enemies)
        yield {"op": "damage", "amount": base * (2 if react else 1),
               "target": "enemy"}
        yield oath_proxy
    elif kind == "storm_battery":
        # One hit per OTHER card in hand (the card is in hand while priced).
        n = max(0, len(state.player.hand) - 1)
        if n:
            yield {"op": "damage", "amount": per * n,
                   "target": "all_enemies"}
            yield oath_proxy
    elif kind == "frost_ward":
        n = sum(1 for e in state.living_enemies if e.aura)
        if n:
            yield {"op": "apply_power", "power": "weak", "amount": 1,
                   "target": "enemy"}
            yield {"op": "block", "amount": amt * n}
    elif kind == "gleeful_songs":
        n = sum(1 for e in state.living_enemies
                if e.aura in ("pyro", "cryo", "electro"))
        yield {"op": "apply_aura", "element": "hydro",
               "target": "all_enemies"}
        yield {"op": "block", "amount": base + per * n}
        yield oath_proxy
    elif kind == "rippling_guard":
        yield {"op": "block",
               "amount": base + per * state.cards_played_this_turn}
    elif kind == "echo_block":
        yield {"op": "block_next_turn", "amount": 2 * amt}
    elif kind == "tempest":
        yield {"op": "damage", "amount": base, "target": "enemy", "times": 4}
    elif kind == "ascension_hit":
        yield {"op": "damage", "amount": per * cur_oath, "target": "enemy"}
    elif kind == "avatar_hit":
        yield {"op": "damage", "amount": base + per * cur_oath,
               "target": "enemy"}
    elif kind == "glacial_edict":
        n = 1 + oath["cryo"] // max(1, amt)
        yield {"op": "apply_power", "power": "weak", "amount": n,
               "target": "enemy"}
        yield {"op": "apply_power", "power": "vulnerable", "amount": n,
               "target": "enemy"}
    elif kind == "draw_per_enemy":
        yield {"op": "draw", "amount": n_en}
    elif kind == "swirl_fresh_auras":
        yield {"op": "swirl", "target": "enemy"}
    elif kind in ("gain_current_oath", "double_current_oath", "rally",
                  "oath_per_cryo_enemy"):
        # Oath is setup: priced as one self Power stack.
        if cur or kind == "rally":
            yield {"op": "apply_power", "power": "vk_oath_proxy",
                   "amount": max(1, cur_oath if kind == "double_current_oath"
                                 else 1), "target": "self"}
    elif kind == "swirled_oath":
        # Downburst: its Oath when the hit can Swirl (any enemy wears an aura).
        if any(e.aura for e in state.living_enemies):
            yield {"op": "apply_power", "power": "vk_oath_proxy",
                   "amount": amt, "target": "self"}
    # --- the combo pass's kinds (2026-10-04) ---
    elif kind == "gain_pyro_oath":
        yield {"op": "apply_power", "power": "vk_oath_proxy", "amount": amt,
               "target": "self"}
    elif kind == "pyro_strike":
        yield {"op": "damage", "amount": base, "target": "enemy"}
        yield oath_proxy
    elif kind == "shatter":
        # Priced against the enemy carrying the most Weak and Vulnerable.
        stacks = max((V.weak_and_vulnerable(e)
                      for e in state.living_enemies), default=0)
        yield {"op": "damage", "amount": base + per * stacks,
               "target": "enemy"}
        yield oath_proxy
    elif kind == "deep_freeze":
        e = max(state.living_enemies, key=V.weak_and_vulnerable,
                default=None)
        if e is not None:
            for name in ("weak", "vulnerable"):
                n = int(e.powers.get(name, 0))
                if n:
                    yield {"op": "apply_power", "power": name, "amount": n,
                           "target": "enemy"}
    elif kind in ("change_of_guard", "cleanse", "swirled_take_more"):
        return
    else:
        return


# --- the discard sequencer (see the docstring) -----------------------------------

SHORT_CIRCUIT, CHAIN_LIGHTNING = P + "short_circuit", P + "chain_lightning"
VIOLET_STORM, STORM_BATTERY = P + "violet_storm", P + "storm_battery"


def _base_id(card):
    return card.id.rstrip("+")


def _gross(state, card):
    """A card's value to the stock scorer with its Energy charge added back
    (0 for a card that cannot be played): what it is worth if paid for."""
    from tier0.content import loader
    from tier0.engine import combat
    from tier0.pilot import policy
    if not combat.card_playable(state, card):
        return 0.0
    w = loader.pilot_weights("generic")
    return max(0.0, policy._score(state, card, w)
               + w["cost"] * combat.card_cost(state, card))


def lowest_victims(state, n):
    """A chosen discard's batch, picked up front off the hand as it stands
    (the engine's contract): the `n` lowest-value cards."""
    cands = [c for c in state.player.hand if not c.kit_card]
    return sorted(cands, key=lambda c: _gross(state, c))[:n]


def _plan(state, cards, energy, discounted=0):
    """(value, cards left unplayed) of the best greedy turn: the cards by
    value per Energy, each played while the bank pays for it. Chain
    Lightning's cost falls by `discounted` more discards."""
    from tier0.engine import combat
    priced = []
    for c in cards:
        cost = combat.card_cost(state, c)
        if _base_id(c) == CHAIN_LIGHTNING:
            cost = max(0, cost - discounted)
        priced.append((_gross(state, c), cost, c))
    priced.sort(key=lambda t: t[0] / max(t[1], 0.5), reverse=True)
    value, left = 0.0, []
    for v, cost, c in priced:
        if v > 0 and cost <= energy:
            value += v
            energy -= cost
        else:
            left.append(c)
    return value, left


def _typical_draws(state, d):
    """`d` stand-ins for the cards a draw brings: the draw pile's median
    card by value (the discard pile's when the draw pile is empty), never its
    order. Empty when there is nothing to draw."""
    p = state.player
    pile = list(p.draw_pile) or list(p.discard_pile)
    if d <= 0 or not pile:
        return []
    ranked = sorted(pile, key=lambda c: _gross(state, c))
    return [ranked[len(ranked) // 2]] * min(d, len(pile))


def _short_circuit_now(state, sc):
    from tier0.engine import combat
    p = state.player
    n = sum(fx.get("amount", 0) for fx in sc.effects
            if fx.get("op") == "discard")
    others = [c for c in p.hand if c is not sc]
    if not others:
        return False
    keep = sorted(others, key=lambda c: _gross(state, c))[n:]
    keep = keep + _typical_draws(state, sum(
        fx.get("amount", 0) for fx in sc.effects if fx.get("op") == "draw"))
    gained = sum(fx.get("amount", 0) for fx in sc.effects
                 if fx.get("op") == "energy")
    left = p.energy - combat.card_cost(state, sc) + gained
    with_sc, _ = _plan(state, keep, left, discounted=min(n, len(others)))
    without, _ = _plan(state, others, p.energy)
    return with_sc >= without


def _violet_storm_now(state, vs):
    from tier0.engine import combat
    p = state.player
    others = [c for c in p.hand if c is not vs]
    if not others:
        return False
    now = _gross(state, vs)
    per_hit = now / len(others)
    rest, left = _plan(state, others, p.energy - combat.card_cost(state, vs))
    return now >= rest + per_hit * len(left)


def _electro_pick(state, base):
    """His discard cards' order; None hands the turn to the stock pilot
    with any held card hidden from it."""
    from tier0.engine import combat
    p = state.player
    ready = {}
    for c in p.hand:
        b = _base_id(c)
        if (b in (SHORT_CIRCUIT, VIOLET_STORM, STORM_BATTERY, CHAIN_LIGHTNING)
                and combat.card_playable(state, c)
                and combat.card_cost(state, c) <= p.energy):
            ready.setdefault(b, c)
    if not ready.keys() & {SHORT_CIRCUIT, VIOLET_STORM}:
        return base(state)
    sc, vs = ready.get(SHORT_CIRCUIT), ready.get(VIOLET_STORM)
    discard_now = None
    if sc is not None and _short_circuit_now(state, sc):
        discard_now = sc
    elif vs is not None and _violet_storm_now(state, vs):
        discard_now = vs
    if discard_now is not None:
        sb = ready.get(STORM_BATTERY)
        if sb is not None and _gross(state, sb) > 0:
            return sb
        return discard_now
    hidden = [c for c in p.hand
              if _base_id(c) in (SHORT_CIRCUIT, VIOLET_STORM)]
    saved = p.hand
    p.hand = [c for c in saved if all(c is not h for h in hidden)]
    try:
        pick = base(state)
    finally:
        p.hand = saved
    if pick is not None:
        return pick
    # Nothing else worth playing: a held discard card goes last (Short
    # Circuit's Electro, Violet Storm's hits on what is left).
    for c in (vs, sc):
        if c is not None and _gross(state, c) > 0:
            return c
    return None


def make_pilot():
    """The stock `generic` pilot, with his Powers played first when
    affordable, most expensive first (the Kokomi expansion harness's rule:
    the stock scorer prices a one-stack Power as almost nothing, so it holds
    them and a play rate would read the scorer, not the card), then the
    discard sequencer (`_electro_pick`)."""
    from tier0.content import loader
    from tier0.engine import combat
    from tier0.pilot.policy import make_pilot as stock
    base = stock(loader.pilot_weights("generic"))

    def pilot(state):
        p = state.player
        powers = [c for c in p.hand if c.type == "power"
                  and c.id.startswith(P)
                  and combat.card_playable(state, c)
                  and combat.card_cost(state, c) <= p.energy]
        if powers:
            return max(powers, key=lambda c: combat.card_cost(state, c))
        return _electro_pick(state, base)

    return pilot


# --- pool and drafting -----------------------------------------------------------

def pool():
    from tier0.content import loader
    out = {"common": [], "uncommon": [], "rare": []}
    for c in loader.prototype_cards():
        if c.id.startswith(P) and c.rarity in out:
            out[c.rarity].append(c.id)
    return out


def _offer(rng, kind, pl):
    w = RARITY[kind]
    out = []
    while len(out) < 3:
        r = rng.choices(("common", "uncommon", "rare"), weights=w)[0]
        c = rng.choice(pl[r])
        if c not in out:
            out.append(c)
    return out


_NOMINAL: dict = {}


def _nominal(element):
    """Rows the default scores under the skip line against the starter get
    the median of the rest, once per process per start."""
    if element not in _NOMINAL:
        from tier0 import constants as C
        from tier0.content import loader
        from tier0.engine import varka_oath as V
        from tier05 import draft
        starter = [loader.get_card(c) for c in V.starter_ids(element)]
        ids = [c for r in pool().values() for c in r]
        sc = {c: draft.score_offer(_draft_view(loader.get_card(c)), starter,
                                   "generic")
              for c in ids}
        priced = sorted(v for v in sc.values()
                        if v >= C.DRAFT_SKIP_THRESHOLD)
        med = st.median(priced) if priced else 1.0
        _NOMINAL[element] = (med, frozenset(
            c for c, v in sc.items() if v < C.DRAFT_SKIP_THRESHOLD))
    return _NOMINAL[element]


#: The rebalance overlay's kinds as stock ops FOR THE DRAFTER ONLY, at a
#: nominal board (one reacting enemy, two other cards played, four cards in
#: hand, two enemies with an aura). The default drafter prices `varka` at 0,
#: and the rows these replace printed stock ops it priced (Gleeful Songs' and
#: Wind Wall's Block, Gust Ward's Block and draw); without this the new rows
#: would read as blanks beside the rows they replace. Razor's Awakening
#: is priced here too since it went single-target.
def _draft_ops(fx):
    kind = fx.get("kind")
    base, per, amt = fx.get("base", 0), fx.get("per", 0), fx.get("amount", 0)
    if kind == "gleeful_songs":
        return [{"op": "apply_aura", "element": "hydro",
                 "target": "all_enemies"},
                {"op": "block", "amount": base + per}]
    if kind == "rippling_guard":
        return [{"op": "block", "amount": base + 2 * per}]
    if kind == "echo_block":
        return [{"op": "block_next_turn", "amount": 2 * amt}]
    if kind == "frost_ward":
        return [{"op": "apply_power", "power": "weak", "amount": 1,
                 "target": "enemy"}, {"op": "block", "amount": 2 * amt}]
    if kind == "kindled_edge":
        return [{"op": "damage", "amount": base + base // 2,
                 "target": "enemy"}]
    if kind == "storm_battery":
        return [{"op": "damage", "amount": 4 * per,
                 "target": "all_enemies"}]
    if kind == "awakening":
        return [{"op": "damage", "amount": base + amt // 2,
                 "target": "enemy"}]
    return None


def _draft_view(card):
    """The card the default drafter scores: the overlay's kinds swapped for
    `_draft_ops`; any other card as it is."""
    if not any(_draft_ops(fx) for fx in card.effects
               if fx.get("op") == "varka"):
        return card
    import copy
    view = copy.copy(card)
    effects = []
    for fx in card.effects:
        ops = _draft_ops(fx) if fx.get("op") == "varka" else None
        effects.extend(ops if ops else [fx])
    view.effects = effects
    return view


def _default(card, deck_cards, element):
    from tier05 import draft
    med, low = _nominal(element)
    if card.id in low:
        return med
    return draft.score_offer(_draft_view(card), deck_cards, "generic")


def _score(card, deck, deck_cards, pilot, element):
    from tier0 import constants as C
    floor = C.DRAFT_SKIP_THRESHOLD
    if pilot == "default":
        return _default(card, deck_cards, element), floor
    d = DECKS[pilot]
    if card.id in d["against"]:
        return -1.0, floor
    if card.id in d["core"]:
        knight = (pilot.startswith(("mono_", "elem_"))
                  and card.id[len(P):] in KNIGHTS.get(pilot[5:], ()))
        cap = 3 if knight else (
            1 if (card.type == "power" or card.rarity == "rare") else 2)
        if deck.count(card.id) < cap:
            return 10.0, floor
    elif card.id in d["support"]:
        if deck.count(card.id) < 2:
            return 7.0, floor
    return _default(card, deck_cards, element), floor


def _draft(offer, deck, pilot, element):
    from tier0.content import loader
    from tier0.engine import varka_oath as V
    deck_cards = [loader.get_card(c) for c in V.starter_ids(element) + deck]
    best, best_s, floor = None, float("-inf"), 0.0
    for cid in offer:
        s, floor = _score(loader.get_card(cid), deck, deck_cards, pilot,
                          element)
        if s > best_s:
            best, best_s = cid, s
    return best if best_s >= floor else None


# --- one fight, one run ----------------------------------------------------------

def fight(element, deck, enemies, seed, hp):
    from tier0.engine import combat, varka_oath as V
    # Instrument only: enemy names repeat ("inklet" x3), and the report tells
    # a multi-target hit from a single one by the `damage` event's target.
    # Names are log text in the engine, so nothing a fight does moves.
    for i, e in enumerate(enemies):
        e.name = f"{e.name}#{i}"
    player = V.build_player(element, extra=tuple(deck))
    player.hp = min(hp, player.max_hp)
    start = player.hp
    full = V.starter_ids(element) + list(deck)
    try:
        s = combat.run_fight(player, enemies, make_pilot(), seed=seed)
    except Exception as exc:                      # noqa: BLE001 -- reported
        return {"won": False, "turns": 0, "hp_lost": start, "hp_end": 0,
                "plays": {}, "oath": 0, "stall": False, "deck": full,
                "error": f"{type(exc).__name__}: {exc}",
                "trace": traceback.format_exc(limit=6)}
    plays = Counter(r["card"] for r in s.log if r.get("event") == "play")
    led = getattr(s.player, "varka_ledger", None)
    oath = sum(led.oath.values()) if led else 0
    won = bool(s.player.alive) and not s.living_enemies
    block, dmg, multi = _log_reads(s.log)
    return {"won": won, "turns": s.turn,
            "hp_lost": start - max(0, s.player.hp),
            "hp_end": max(0, s.player.hp), "plays": dict(plays),
            "oath": oath, "stall": s.player.alive and bool(s.living_enemies),
            "deck": full, "error": None, "block": block, "dmg": dmg,
            "dmg_multi": multi, "enemies": len(enemies)}


#: Log events that open a new damage group: a card play, and each of his
#: Powers' own triggers (their damage is theirs, not the last card's).
_GROUP_MARKS = frozenset({"play", "varka_cycle_of_seasons", "varka_assembly",
                          "varka_absolute_zero", "varka_retaliating_tide",
                          "varka_baron_bunny"})


def _log_reads(log):
    """(Block gained, damage dealt to enemies, the part of it dealt by
    MULTI-TARGET groups). A group is the events from one card play (or one
    Power trigger) to the next, cut at each turn; it is multi-target when its
    hits struck two or more different enemies (`fight` numbers the names). Damage counts
    HP lost plus Block stripped."""
    block = 0
    dmg = multi = 0.0
    group: list = []
    turn = None

    def close():
        nonlocal multi
        ids = {e for e, _ in group}
        if len(ids) >= 2:
            multi += sum(a for _, a in group)

    for r in log:
        ev = r.get("event")
        if ev == "block":
            block += r.get("amount", 0)
            continue
        if ev in _GROUP_MARKS or r.get("turn") != turn:
            close()
            group = []
            turn = r.get("turn")
        if ev == "damage" and r.get("target") != "player":
            a = float(r.get("amount", 0)) + float(r.get("blocked", 0) or 0)
            dmg += a
            group.append((r.get("target"), a))
    close()
    return block, dmg, multi


def run(seed, pilot, element):
    from tier05 import acts
    enc_rng = random.Random(seed)
    draw = acts.ActDraw(enc_rng, act=0)
    offer_rng = random.Random(seed + 10 ** 6)
    pl = pool()
    deck: list = []
    hp = max_hp = 80
    fights, offers = [], []
    act1 = False
    for floor, kind in enumerate(TEMPLATE + ["B2"]):
        if kind == "R":
            hp = min(max_hp, hp + int(0.3 * max_hp))
            continue
        if kind == "B2":
            hp = min(max_hp, hp + int(0.3 * max_hp))
            spec = enc_rng.choice(acts.boss_pool(1))
        else:
            spec = draw.encounter_for(kind, enc_rng)
        enemies = acts.spawn(spec, enc_rng)
        r = fight(element, deck, enemies, seed * 100 + floor, hp)
        r.update(kind=kind, enc=spec["id"])
        fights.append(r)
        hp = r["hp_end"]
        if not r["won"]:
            break
        if kind == "B":
            act1 = True
        if kind in RARITY:
            offer = _offer(offer_rng, kind, pl)
            pick = _draft(offer, deck, pilot, element)
            offers.append((offer, pick))
            if pick:
                deck.append(pick)
    won = fights[-1]["kind"] == "B2" and fights[-1]["won"]
    return {"seed": seed, "pilot": pilot, "element": element, "act1": act1,
            "won": won, "fights": fights, "offers": offers}


def gauntlet(seed, pilot, element):
    from tier05 import acts
    offer_rng = random.Random(seed + 10 ** 6)
    pl = pool()
    deck: list = []
    offers = []
    for kind in [k for k in TEMPLATE if k != "R"]:
        offer = _offer(offer_rng, kind, pl)
        pick = _draft(offer, deck, pilot, element)
        offers.append((offer, pick))
        if pick:
            deck.append(pick)
    specs = ([("E", e) for e in acts.pools(0)["elite"]]
             + [("B", e) for e in acts.boss_pool(0)]
             + [("B2", e) for e in acts.boss_pool(1)])
    fights = []
    for i, (kind, spec) in enumerate(specs):
        erng = random.Random(seed * 1000 + i)
        r = fight(element, deck, acts.spawn(spec, erng), seed * 1000 + i, 80)
        r.update(kind=kind, enc=spec["id"])
        fights.append(r)
    return {"seed": seed, "pilot": pilot, "element": element,
            "offers": offers, "fights": fights}


def _slim(r):
    """Drop the per-fight deck list: `_fight_decks` rebuilds it from the
    starter and the picks (a 2,400-seed file is otherwise ~700 MB)."""
    for f in r["fights"]:
        f.pop("deck", None)
    return r


def _fight_decks(r):
    """(fight, Counter of its deck) for each fight of a run or gauntlet. A
    run's fight i holds the starter and the picks of the i offers before it
    (every won fight but the last is followed by one offer); a gauntlet's
    every fight holds all its picks."""
    from tier0.engine import varka_oath as V
    starter = V.starter_ids(r["element"])
    picks = [pick for _, pick in r["offers"]]
    gauntlet = "act1" not in r
    for i, f in enumerate(r["fights"]):
        if "deck" in f:                              # an older file
            yield f, Counter(f["deck"])
            continue
        got = picks if gauntlet else picks[:i]
        yield f, Counter(starter + [c for c in got if c])


def _w(args):
    enable()
    return _slim(run(*args))


def _wg(args):
    enable()
    return _slim(gauntlet(*args))


def _wo(args):
    """`--no-gauntlet`: the gauntlet's nine drafts only, no fights."""
    enable()
    seed, pilot, element = args
    offer_rng = random.Random(seed + 10 ** 6)
    pl = pool()
    deck, offers = [], []
    for kind in [k for k in TEMPLATE if k != "R"]:
        offer = _offer(offer_rng, kind, pl)
        pick = _draft(offer, deck, pilot, element)
        offers.append((offer, pick))
        if pick:
            deck.append(pick)
    return {"seed": seed, "pilot": pilot, "element": element,
            "offers": offers, "fights": []}


def pmap(fn, jobs, argl):
    if jobs <= 1:
        enable()
        return [fn(a) for a in argl]
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(jobs, initializer=enable) as p:
        return p.map(fn, argl, chunksize=8)


# --- report ------------------------------------------------------------------------

def ci(k, n):
    if not n:
        return 0.0
    p = k / n
    return 196.0 * (p * (1 - p) / n) ** 0.5


def pc(k, n):
    return f"{100.0 * k / n:.1f} ±{ci(k, n):.1f}" if n else "-"


def paired_diff(a, b):
    """Mean difference (pp) of two paired 0/1 lists and its 95% half-width."""
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    if n < 2:
        return 0.0, 0.0
    m = st.mean(d)
    return 100 * m, 196 * st.stdev(d) / n ** 0.5


def report(data, against=None, out=print):
    runs, gaunt = data["runs"], data["gauntlet"]
    by = defaultdict(list)
    for r in runs:
        by[(r["pilot"], r["element"])].append(r)
    gb = defaultdict(list)
    for r in gaunt:
        gb[(r["pilot"], r["element"])].append(r)
    present = [p for p in PILOTS if any(r["pilot"] == p for r in runs)]
    out(f"# Varka expansion sim -- pool {data['pool_size']} "
        f"({data['pool_counts']}), {data['seeds']} seeds from {data['seed']}")

    def rows(pilot):
        return [r for e in starts_for(pilot) for r in by[(pilot, e)]]

    def grows(pilot):
        return [r for e in starts_for(pilot) for r in gb[(pilot, e)]]

    out("\n## Act won, the stylised run (paired seeds)")
    out("| pilot | starts | n | act 1 | act-2 boss given act 1 | run (both) "
        "| gauntlet: A1 elites | A1 bosses | A2 bosses | all | Oath/fight |")
    out("|---|---|---|---|---|---|---|---|---|---|---|")
    for pilot in present:
        rs, gs = rows(pilot), grows(pilot)
        n = len(rs)
        a1 = sum(r["act1"] for r in rs)
        w = sum(r["won"] for r in rs)
        cells = []
        for kind in ("E", "B", "B2", None):
            fs = [f for g in gs for f in g["fights"]
                  if kind is None or f["kind"] == kind]
            cells.append(pc(sum(f["won"] for f in fs), len(fs)))
        oath = [f["oath"] for r in rs for f in r["fights"]]
        out(f"| {pilot} | {','.join(e[0].upper() for e in starts_for(pilot))}"
            f" | {n} | {pc(a1, n)} | {pc(w, a1)} | {pc(w, n)} | "
            + " | ".join(cells) + f" | {st.mean(oath) if oath else 0:.2f} |")

    out("\n## Forced decks against the default drafter (paired, same starts)")
    out("| pilot | act 1 diff | run diff | gauntlet diff (all fights) | "
        "within 10? |")
    out("|---|---|---|---|---|")
    for pilot in [p for p in present if p != "default"]:
        a, b, ga = [], [], []
        for e in starts_for(pilot):
            mine = {r["seed"]: r for r in by[(pilot, e)]}
            base = {r["seed"]: r for r in by[("default", e)]}
            for s in mine:
                a.append((mine[s]["act1"], base[s]["act1"]))
                b.append((mine[s]["won"], base[s]["won"]))
            gm = {r["seed"]: r for r in gb[(pilot, e)]}
            gd = {r["seed"]: r for r in gb[("default", e)]}
            for s in gm:
                if gm[s]["fights"] and gd[s]["fights"]:
                    ga.append((st.mean(f["won"] for f in gm[s]["fights"]),
                               st.mean(f["won"] for f in gd[s]["fights"])))
        d1 = paired_diff(*zip(*a))
        d2 = paired_diff(*zip(*b))
        d3 = paired_diff(*zip(*ga)) if ga else (0.0, 0.0)
        ok = all(d[0] > -10 for d in (d1, d3))
        out(f"| {pilot} | {d1[0]:+.1f} ±{d1[1]:.1f} | {d2[0]:+.1f} "
            f"±{d2[1]:.1f} | {d3[0]:+.1f} ±{d3[1]:.1f} | "
            f"{'yes' if ok else 'NO'} |")

    if against is not None:
        out("\n## Pool comparison, default drafter (paired seeds and starts)")
        old = {(r["seed"], r["element"]): r for r in against["runs"]
               if r["pilot"] == "default"}
        oldg = {(r["seed"], r["element"]): r for r in against["gauntlet"]
                if r["pilot"] == "default"}
        new = {(r["seed"], r["element"]): r for r in runs
               if r["pilot"] == "default"}
        newg = {(r["seed"], r["element"]): r for r in gaunt
                if r["pilot"] == "default"}
        keys = sorted(set(old) & set(new))
        gkeys = sorted(set(oldg) & set(newg))
        out(f"pool {against['pool_size']} -> {data['pool_size']}, "
            f"n = {len(keys)} paired runs")
        out("| read | old | new | new - old (paired) |")
        out("|---|---|---|---|")
        for label, fn in (("act 1 won", lambda r: r["act1"]),
                          ("run won (act 1 + act-2 boss)",
                           lambda r: r["won"])):
            o = [fn(old[k]) for k in keys]
            nw = [fn(new[k]) for k in keys]
            d = paired_diff(nw, o)
            out(f"| {label} | {pc(sum(o), len(o))} | {pc(sum(nw), len(nw))}"
                f" | {d[0]:+.1f} ±{d[1]:.1f} |")
        out(f"| act-2 boss given act 1 | "
            f"{pc(sum(old[k]['won'] for k in keys), sum(old[k]['act1'] for k in keys))} | "
            f"{pc(sum(new[k]['won'] for k in keys), sum(new[k]['act1'] for k in keys))} | "
            f"(conditional, unpaired) |")
        for kind, label in (("E", "gauntlet A1 elites"),
                            ("B", "gauntlet A1 bosses"),
                            ("B2", "gauntlet A2 bosses"),
                            (None, "gauntlet all")):
            def share(r):
                fs = [f["won"] for f in r["fights"]
                      if kind is None or f["kind"] == kind]
                return st.mean(fs) if fs else 0.0
            o = [share(oldg[k]) for k in gkeys]
            nw = [share(newg[k]) for k in gkeys]
            d = paired_diff(nw, o)
            out(f"| {label} | {100 * st.mean(o):.1f} | {100 * st.mean(nw):.1f}"
                f" | {d[0]:+.1f} ±{d[1]:.1f} |")
        for label, src in (("old", against), ("new", data)):
            oath = [f["oath"] for r in src["runs"] if r["pilot"] == "default"
                    for f in r["fights"]]
            out(f"Oath per fight ({label}, default): {st.mean(oath):.2f}")

    out("\n## Cards: default drafter's take rate and play rate")
    out("Offered/taken: the default drafter's gauntlet drafts (nine offers a "
        "seed a start). Played = share of fights whose deck held it in which "
        "it was played at least once (all pilots, runs and gauntlet). "
        "Flags: TAKEN >70% of offers; DEAD played in <5% of fights held "
        "(30+ fights held).")
    out("| card | rarity | offered | taken | fights held | played in | "
        "plays/fight held (per copy) | flag |")
    out("|---|---|---|---|---|---|---|---|")
    meta = data["cards"]
    off, tak = Counter(), Counter()
    for g in gaunt:
        if g["pilot"] != "default":
            continue
        for offer, pick in g["offers"]:
            for c in offer:
                off[c] += 1
            if pick:
                tak[pick] += 1
    held, played, plays, copies = Counter(), Counter(), Counter(), Counter()
    for src in (runs, gaunt):
        for r in src:
            for f, deck in _fight_decks(r):
                for c, n in deck.items():
                    held[c] += 1
                    copies[c] += n
                    k = f["plays"].get(c, 0)
                    plays[c] += k
                    played[c] += k > 0
    flags = []
    for cid, (name, rar) in sorted(meta.items(),
                                   key=lambda kv: ("cur".index(kv[1][1][0]),
                                                   kv[1][0])):
        flag = []
        if off[cid] and tak[cid] / off[cid] > 0.70:
            flag.append("TAKEN")
        if held[cid] >= 30 and played[cid] / held[cid] < 0.05:
            flag.append("DEAD")
        if held[cid] < 30:
            flag.append("thin")
        if flag and flag != ["thin"]:
            flags.append(f"{name} ({'/'.join(flag)})")
        out(f"| {name} | {rar[0].upper()} | {off[cid]} | "
            f"{pc(tak[cid], off[cid]) if off[cid] else '-'} | {held[cid]} | "
            f"{(100 * played[cid] / held[cid]) if held[cid] else 0:.1f}% | "
            f"{(plays[cid] / copies[cid]) if copies[cid] else 0:.2f} | "
            f"{' '.join(flag)} |")
    out(f"\nFlagged: {', '.join(flags) or 'none'}.")

    errs = Counter()
    stalls = Counter()
    nf = 0
    for src in (runs, gaunt):
        for r in src:
            for f in r["fights"]:
                nf += 1
                if f.get("error"):
                    errs[f["error"].splitlines()[0][:160]] += 1
                if f.get("stall"):
                    stalls[f["enc"]] += 1
    out(f"\n## Throws and stalls ({nf} fights)")
    out(f"Throws: {sum(errs.values())}; "
        + ("; ".join(f"{k} x{v}" for k, v in errs.most_common(10)) or "none"))
    out(f"Stalls (turn cap, both alive): {sum(stalls.values())}; "
        + (", ".join(f"{k} x{v}" for k, v in stalls.most_common(10))
           or "none"))
    if data.get("traces"):
        out("\nFirst trace:\n" + data["traces"][0])
    report_bars(data, against, out)


#: The rebalance paper's new and rewritten pool rows (the card bar reads
#: these; the starter Knights have the starter bar).
REBALANCE_CARDS = ("kindled_edge", "storm_battery", "frost_ward",
                   "rippling_guard", "barbara_show_begin",
                   "barbara_whisper_of_water", "razor_claw_and_thunder",
                   "wildfire_oath", "absolute_zero", "cycle_of_seasons",
                   # The combo pass (2026-10-04): its five new rows and the
                   # cards it changed.
                   "stoke_the_flames", "ember_cleave", "pyre_oath",
                   "shatter", "deep_freeze", "unwavering_banner",
                   "amber_baron_bunny", "charge_of_the_knights",
                   "kaeya_frostgnaw")


def _act1(rs):
    return sum(r["act1"] for r in rs), len(rs)


def report_bars(data, against=None, out=print):
    """The rebalance paper's bars (secs.5 and 6): the element spread, the
    starter spread, cross-element plays, Block and multi-target damage, and
    the new cards. Every rate is act 1 won on the stylised run."""
    runs, gaunt = data["runs"], data["gauntlet"]
    elements = data.get("elements") or element_of()
    by = defaultdict(list)
    for r in runs:
        by[(r["pilot"], r["element"])].append(r)
    have = {r["pilot"] for r in runs}
    out("\n# Rebalance bars")

    out("\n## Starter bar: default drafter, act 1 by forced starter Knight")
    out("| start | n | act 1 |")
    out("|---|---|---|")
    rates = {}
    for el in ELEMENTS:
        k, n = _act1(by[("default", el)])
        if n:
            rates[el] = 100 * k / n
            out(f"| {el} | {n} | {pc(k, n)} |")
    if rates:
        spread = max(rates.values()) - min(rates.values())
        out(f"Spread {spread:.1f} points (bar: within 5) -> "
            f"{'MET' if spread <= 5 else 'MISSED'}")

    out("\n## Element bar: each element deck (own start) and the mixed deck")
    out("| deck | n | act 1 |")
    out("|---|---|---|")
    groups = {}
    for fam in ("mono", "elem"):
        cells = {}
        for el in ELEMENTS:
            pilot = f"{fam}_{el}"
            if pilot not in have:
                continue
            k, n = _act1(by[(pilot, el)])
            cells[pilot] = 100 * k / n
            out(f"| {pilot} | {n} | {pc(k, n)} |")
        groups[fam] = cells
    mixed = {}
    for pilot in ("default", "switch"):
        if pilot in have:
            rs = [r for el in ELEMENTS for r in by[(pilot, el)]]
            k, n = _act1(rs)
            mixed[pilot] = 100 * k / n
            out(f"| {pilot} (mixed, all four starts) | {n} | {pc(k, n)} |")
    for fam, cells in groups.items():
        for mix, rate in mixed.items():
            if not cells:
                continue
            vals = list(cells.values()) + [rate]
            spread = max(vals) - min(vals)
            out(f"Spread {fam}_* + {mix}: {spread:.1f} points (bar: within "
                f"10) -> {'MET' if spread <= 10 else 'MISSED'}")

    out("\n## Cross-element plays (a deck playing the cards of an Oath "
        "element other than its start; runs, all fights)")
    out("Other = a Knight, starter Knight or payoff of an Oath element other "
        "than the start. Bar: at least three such plays a run.")
    out("| deck | start | runs | other plays/run | distinct other cards/run "
        "| runs with 3+ other plays |")
    out("|---|---|---|---|---|---|")
    for pilot in [p for p in PILOTS if p in have]:
        for el in starts_for(pilot):
            rs = by[(pilot, el)]
            if not rs:
                continue
            tot, dist, three = [], [], 0
            for r in rs:
                c = Counter()
                for f in r["fights"]:
                    for cid, k in f["plays"].items():
                        e2 = elements.get(cid.rstrip("+"))
                        if e2 and e2 != el:
                            c[cid] += k
                tot.append(sum(c.values()))
                dist.append(len(c))
                three += sum(c.values()) >= 3
            out(f"| {pilot} | {el} | {len(rs)} | {st.mean(tot):.2f} | "
                f"{st.mean(dist):.2f} | {pc(three, len(rs))} |")

    out("\n## Block gained and multi-target damage (runs, all fights)")
    out("Multi-target share: damage from card plays and Power triggers whose "
        "hits struck 2+ different enemies, over all damage dealt (HP lost "
        "plus Block stripped); fights with 2+ enemies only.")
    out("| deck | fights | Block/fight | damage/fight | multi-target share "
        "(2+ enemy fights) |")
    out("|---|---|---|---|---|")
    for pilot in [p for p in PILOTS if p in have]:
        fs = [f for el in starts_for(pilot) for r in by[(pilot, el)]
              for f in r["fights"] if "block" in f]
        if not fs:
            continue
        multi = [f for f in fs if f.get("enemies", 1) >= 2]
        md = sum(f["dmg"] for f in multi)
        share = 100 * sum(f["dmg_multi"] for f in multi) / md if md else 0
        out(f"| {pilot} | {len(fs)} | {st.mean(f['block'] for f in fs):.1f} "
            f"| {st.mean(f['dmg'] for f in fs):.1f} | {share:.1f}% |")

    out("\n## The paper's cards (default drafter's gauntlet drafts; played "
        "= all pilots, runs and gauntlet)")
    out("Won with/without: the default drafter's RUN fights at an elite or "
        "the act-1 boss (where runs are lost), won with the card in the deck "
        "against without it (fights held by a pilot of any start). "
        "Survivorship leans it: a card held at a boss was drafted by a deck "
        "that got there.")
    out("| card | offered | taken | played in | elite+boss won with | "
        "without | diff |")
    out("|---|---|---|---|---|---|---|")
    off, tak = Counter(), Counter()
    held, played = Counter(), Counter()
    with_w, with_n = Counter(), Counter()
    tot_w = tot_n = 0
    for g in gaunt:
        if g["pilot"] != "default":
            continue
        for offer, pick in g["offers"]:
            for c in offer:
                off[c] += 1
            if pick:
                tak[pick] += 1
    for r in runs:
        if r["pilot"] != "default":
            continue
        for f, deck in _fight_decks(r):
            if f["kind"] not in ("E", "B"):
                continue
            tot_w += f["won"]
            tot_n += 1
            for c in deck:
                with_w[c] += f["won"]
                with_n[c] += 1
    for src in (runs, gaunt):
        for r in src:
            for f, deck in _fight_decks(r):
                for c in deck:
                    held[c] += 1
                    played[c] += f["plays"].get(c, 0) > 0
    names = data["cards"]
    for short in REBALANCE_CARDS:
        cid = P + short
        if cid not in names:
            continue
        ww, wn = with_w[cid], with_n[cid]
        ow, on = tot_w - ww, tot_n - wn
        a = f"{100 * ww / wn:.1f} (n {wn})" if wn else "-"
        b = f"{100 * ow / on:.1f}" if on else "-"
        d = (f"{100 * ww / wn - 100 * ow / on:+.1f}" if wn and on else "-")
        out(f"| {names[cid][0]} | {off[cid]} | "
            f"{pc(tak[cid], off[cid]) if off[cid] else '-'} | "
            f"{(100 * played[cid] / held[cid]) if held[cid] else 0:.1f}% | "
            f"{a} | {b} | {d} |")

    if against is not None:
        out("\n## Paired against the other file (same seeds, starts, "
            "offers by slot)")
        out("| deck | start | n | other | this | this - other (paired) |")
        out("|---|---|---|---|---|---|")
        old = {(r["pilot"], r["element"], r["seed"]): r
               for r in against["runs"]}
        for pilot in [p for p in PILOTS if p in have]:
            starts = list(starts_for(pilot))
            for el in starts + (["all"] if len(starts) > 1 else []):
                els = starts if el == "all" else [el]
                pairs = [(r["act1"], old[(pilot, e, r["seed"])]["act1"])
                         for e in els for r in by[(pilot, e)]
                         if (pilot, e, r["seed"]) in old]
                if not pairs:
                    continue
                a, b = zip(*pairs)
                d = paired_diff(a, b)
                out(f"| {pilot} | {el} | {len(pairs)} | "
                    f"{pc(sum(b), len(b))} | {pc(sum(a), len(a))} | "
                    f"{d[0]:+.1f} ±{d[1]:.1f} |")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=500)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--jobs", type=int, default=14)
    ap.add_argument("--pilots", default=",".join(PILOTS))
    ap.add_argument("--json", help="write the raw results here")
    ap.add_argument("--report", help="report a --json file instead of running")
    ap.add_argument("--against", help="a --json file from the other pool")
    ap.add_argument("--no-gauntlet", action="store_true",
                    help="skip the gauntlet's fights (its drafts are kept "
                         "for the card table)")
    args = ap.parse_args(argv)
    if args.report:
        with open(args.report, encoding="utf-8") as fh:
            data = json.load(fh)
        against = None
        if args.against:
            with open(args.against, encoding="utf-8") as fh:
                against = json.load(fh)
        report(data, against)
        return
    enable()
    from tier0.content import loader
    pl = pool()
    seeds = [args.seed + i for i in range(args.seeds)]
    pilots = [p for p in args.pilots.split(",") if p]
    argl = [(s, p, e) for p in pilots for e in starts_for(p) for s in seeds]
    print(f"{len(argl)} runs + {len(argl)} gauntlets", file=sys.stderr)
    runs = pmap(_w, args.jobs, argl)
    gaunt = pmap(_wg if not args.no_gauntlet else _wo, args.jobs, argl)
    traces = [f["trace"] for src in (runs, gaunt) for r in src
              for f in r["fights"] if f.get("trace")][:3]
    for src in (runs, gaunt):
        for r in src:
            for f in r["fights"]:
                f.pop("trace", None)
    data = {"seeds": args.seeds, "seed": args.seed,
            "elements": element_of(),
            "pool_size": sum(len(v) for v in pl.values()),
            "pool_counts": {k: len(v) for k, v in pl.items()},
            "cards": {c: (loader.get_card(c).name, r)
                      for r, cs in pl.items() for c in cs},
            "runs": runs, "gauntlet": gaunt, "traces": traces}
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
    report(data)


if __name__ == "__main__":
    main()
