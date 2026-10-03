#!/usr/bin/env python3
"""VARKA EXPANSION -- the paper's sec.5 sim (Prototype stage, exploration,
not a Balance measurement).

    .venv/Scripts/python.exe -m tools.varka_expansion_sim --seeds 500 --seed 7 --jobs 14 --json out.json
    .venv/Scripts/python.exe -m tools.varka_expansion_sim --report out.json [--against old.json]

Answers sec.5.2 of `review/active/varka-expansion-2026-10-01.md` on the
BUILT rows (tier0 with `C.SWIRL_PAYS` and `C.CRYSTALLIZE_KEEPS_AURA` on
for THIS PROCESS ONLY, as the Varka tests
switch them; nothing on disk moves). The pool is read off whatever checkout
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

THE REBALANCE WORLD (review/active/varka-rebalance-2026-10-03.md secs.2-5,
aoe-trim-2026-10-03.md sec.4 on branch aoe-trim; SIM ONLY, nothing built in
C#): `--world rebalance` swaps the paper's rows in over the sheet
(`rebalance_rows`, written to a temporary sheet the loader reads) and turns on
`varka_oath.REBALANCE` (Wildfire Oath, Absolute Zero, Cycle of Seasons).
`--world current` (the default) is the sheet, run for run what main runs.
`--knob name=int` moves one of the paper's numbers (KNOBS), never a text.
The `elem_` pilots are the paper's borrowing decks (`deck_lists`); the
`report_bars` section reads the paper's bars. `--no-gauntlet` skips the
gauntlet's fights (at full HP it wins every act-1 fight and loses every
act-2 boss, so it separates nothing) and keeps its drafts.

    .venv/Scripts/python.exe -m tools.varka_expansion_sim --seeds 2400 --seed 7 --jobs 15 --world current --no-gauntlet --json base.json
    .venv/Scripts/python.exe -m tools.varka_expansion_sim --seeds 2400 --seed 7 --jobs 15 --world rebalance --no-gauntlet --json new.json
    .venv/Scripts/python.exe -m tools.varka_expansion_sim --report new.json --against base.json

THE PLAY PILOT is the stock `generic` pilot, as the open-Oath paired sim
used, with one INSTRUMENT SURFACE (not a design claim): the `varka` and
`add_knight` ops, which the stock scorer cannot see, are valued as their
nearest stock op (`_translate`) so it plays them. Nothing in the engine's
resolution moves.
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
FOCUS = ["favonius_drill", "oathsworn_strike", "eye_of_the_storm",
         "stormward_stance", "oath_of_the_knights",
         "dawn_winds_march", "azure_devour", "sworn_brotherhood",
         "northwind_avatar", "wind_wall", "knightly_guard", "tailwind_stride",
         "pathfinders_mark", "cavalry_charge", "vow_of_the_blade",
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
PAYOFFS = {"pyro": ["blazing_charge", "wildfire_oath"],
           "hydro": ["tidal_bulwark", "retaliating_tide"],
           "cryo": ["glacial_edict", "absolute_zero"],
           "electro": ["static_field", "thundering_verdict", "charged_lunge",
                       "short_circuit", "chain_lightning", "violet_storm"]}
GALE = ["gale_sweep", "crosswind", "rising_gale", "tempest_charge",
        "jean_dandelion_breeze", "storm_surge", "wall_of_gales",
        "converging_winds", "west_wind_shield", "eye_wall",
        "crosscurrent", "twin_gales", "downburst", "eye_of_stormterror"]
SWITCH = ["shifting_gale", "cycle_of_seasons", "windborne_resolve",
          "gale_mantle", "weathervane",
          "tempest_of_the_four_winds", "twin_gales", "oathbound_aegis",
          "change_of_guard", "boreas_unbound", "tailwind_guard",
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
# THE REBALANCE PAPER (review/active/varka-rebalance-2026-10-03.md sec.4):
# each element's new payoff joins its element's list. Kept apart from the
# lists above so those name only live sheet rows; `deck_lists` merges them
# under `--world rebalance`, where `rebalance_rows` puts them in the pool.
REBALANCE_PAYOFFS = {"pyro": ["kindled_edge"], "hydro": ["rippling_guard"],
                     "cryo": ["frost_ward"], "electro": ["storm_battery"]}
#: Rebalance sec.4's "borrows" for Electro: the generic draw cards.
GENERIC_DRAW = ["rising_gale", "tempest_charge", "tailwind_stride",
                "change_of_guard", "vow_of_the_blade", "dawn_patrol",
                "eye_of_stormterror", "noelle_steadfast_maid"]


def deck_lists(world="current"):
    """The forced decks for a world. The `elem_` pilots are the rebalance
    paper's borrowing decks (sec.4's "Borrows" column, read as a drafter):
    their element's Knights and payoffs are core, every OTHER element's
    Knights (the appliers) are support beside the Oath cards, and only the
    other elements' payoffs work against them. Electro also borrows the
    generic draw cards. Same drafter in both worlds, so a paired read is the
    pool's change, not the drafter's."""
    payoffs = {el: list(PAYOFFS[el]) + (REBALANCE_PAYOFFS[el]
                                        if world == "rebalance" else [])
               for el in ELEMENTS}
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


def element_of(world="current"):
    """{card id: Oath element} -- the Knights, the starter Knights and each
    element's payoffs; every other row is generic (absent)."""
    from tier0.engine import varka_oath as V
    out = {cid: el for el, cid in V.STARTER_KNIGHT_IDS.items()}
    _, payoffs = deck_lists(world)
    for el in ELEMENTS:
        for c in KNIGHTS[el] + payoffs[el]:
            out[P + c] = el
    return out


def starts_for(pilot):
    if pilot.startswith(("mono_", "elem_")):
        return (pilot[5:],)
    return ELEMENTS


# --- the rebalance world: an OVERLAY on the sheet, sim only ---------------------
#
# The paper's rows are NOT on `docs/prototype-surface.yaml`: the sheet compiles
# to the mod, and these rows need C# the paper has not had built (new `varka`
# kinds, Wildfire Oath / Absolute Zero / Cycle of Seasons rule changes). Under
# `--world rebalance` the harness writes the sheet with these rows swapped in
# to a temporary file, points the loader at it, and turns on
# `varka_oath.REBALANCE`. Texts are the paper's verbatim; the numbers are
# KNOBS so a variant can move only numbers.

#: The paper's first numbers (rebalance secs.3-5; aoe-trim sec.4 keeps
#: Awakening's and Cycle of Seasons' numbers).
KNOBS = {
    "amber_damage": 7, "amber_block": 4,
    "barbara_block": 6, "barbara_next": 3,
    "lisa_block": 5, "lisa_draw": 1,
    "kaeya_block": 5, "kaeya_weak": 1,
    "gleeful_base": 4, "gleeful_per": 3,
    "rippling_base": 3, "rippling_per": 2,
    "whisper_block": 4,
    "kindled_base": 7,
    "storm_per": 2,
    "frost_per": 3,
    "awakening_base": 4, "awakening_more": 3,
    "cycle_amount": 4,
}


def rebalance_rows(knobs=None):
    """{replaced id: new row dict} for the overlay; the key is the row it
    stands in for (same position, same id unless the paper names a new card).
    """
    k = dict(KNOBS, **(knobs or {}))
    unknown = set(k) - set(KNOBS)
    if unknown:
        raise ValueError(f"unknown knobs {sorted(unknown)}")
    vk = "proto_vk_"
    base = {"character": "varka", "authored_by": ["claude"]}
    knight = {"nation": "mondstadt", "star": 4, "role_c": "applier",
              "personal_pool": "varka"}
    rows = {
        # sec.5: four different starter Knights (rarity basic, same ids).
        vk + "amber_fiery_rain": {
            **base, **knight, "id": vk + "amber_fiery_rain",
            "name": "Amber: Precise Shot", "rarity": "basic",
            "element": "pyro", "cost": 1, "type": "skill",
            "description": "Deal 7 [10] Pyro damage. Gain 4 [5] Block.",
            "effects": [{"op": "damage", "amount": k["amber_damage"],
                         "target": "enemy", "applies_element": True},
                        {"op": "block", "amount": k["amber_block"]}],
            "upgrade": {"damage": 3, "block": 1}},
        vk + "barbara_melody_loop": {
            **base, **knight, "id": vk + "barbara_melody_loop",
            "name": "Barbara: Glorious Season", "rarity": "basic",
            "element": "hydro", "cost": 1, "type": "skill",
            "description": "Gain 6 [8] Block. Apply Hydro. Next turn, gain "
                           "3 [4] Block.",
            "effects": [{"op": "block", "amount": k["barbara_block"]},
                        {"op": "apply_aura", "element": "hydro",
                         "target": "enemy"},
                        {"op": "block_next_turn",
                         "amount": k["barbara_next"]}],
            "upgrade": {"block": 2, "block_next_turn": 1}},
        vk + "lisa_lightning_rose": {
            **base, **knight, "id": vk + "lisa_lightning_rose",
            "name": "Lisa: Induced Aftershock", "rarity": "basic",
            "element": "electro", "cost": 1, "type": "skill",
            "description": "Gain 5 [7] Block. Apply Electro. Draw 1 [2] "
                           "card(s).",
            "effects": [{"op": "block", "amount": k["lisa_block"]},
                        {"op": "apply_aura", "element": "electro",
                         "target": "enemy"},
                        {"op": "draw", "amount": k["lisa_draw"]}],
            "upgrade": {"block": 2, "draw": 1}},
        vk + "kaeya_glacial_waltz": {
            **base, **knight, "id": vk + "kaeya_glacial_waltz",
            "name": "Kaeya: Hidden Strength", "rarity": "basic",
            "element": "cryo", "cost": 1, "type": "skill",
            "description": "Gain 5 [7] Block. Apply Cryo and 1 Weak.",
            "effects": [{"op": "block", "amount": k["kaeya_block"]},
                        {"op": "apply_aura", "element": "cryo",
                         "target": "enemy"},
                        {"op": "apply_power", "power": "weak",
                         "amount": k["kaeya_weak"], "target": "enemy"}],
            "upgrade": {"block": 2}},
        # sec.3: Hydro scales.
        vk + "barbara_show_begin": {
            **base, **knight, "id": vk + "barbara_show_begin",
            "name": "Barbara: Gleeful Songs", "rarity": "common",
            "element": "hydro", "cost": 1, "type": "skill",
            "description": "Apply Hydro to ALL enemies. Gain 4 [6] Block, "
                           "plus 3 [4] for each enemy it reacts on.",
            "effects": [{"op": "varka", "kind": "gleeful_songs",
                         "target": "all_enemies", "base": k["gleeful_base"],
                         "per": k["gleeful_per"]}],
            "upgrade": {"varka_base": 2, "varka_per": 1}},
        vk + "wind_wall": {
            **base, "id": vk + "rippling_guard", "name": "Rippling Guard",
            "cost": 1, "type": "skill", "rarity": "common",
            "description": "Apply Hydro to an enemy. Gain 3 Block, plus 2 [3] "
                           "for each other card you played this turn.",
            "effects": [{"op": "apply_aura", "element": "hydro",
                         "target": "enemy"},
                        {"op": "varka", "kind": "rippling_guard",
                         "base": k["rippling_base"],
                         "per": k["rippling_per"]}],
            "upgrade": {"varka_per": 1}},
        vk + "barbara_whisper_of_water": {
            **base, **knight, "id": vk + "barbara_whisper_of_water",
            "name": "Barbara: Whisper of Water", "rarity": "uncommon",
            "element": "hydro", "cost": 1, "type": "skill",
            "description": "Apply Hydro to an enemy. Gain 4 [6] Block now and "
                           "at the start of your next 2 turns.",
            "effects": [{"op": "apply_aura", "element": "hydro",
                         "target": "enemy"},
                        {"op": "block", "amount": k["whisper_block"]},
                        {"op": "varka", "kind": "echo_block",
                         "amount": k["whisper_block"]}],
            "upgrade": {"block": 2, "varka_amount": 2}},
        # sec.4: payoffs that borrow.
        vk + "cavalry_charge": {
            **base, "id": vk + "kindled_edge", "name": "Kindled Edge",
            "cost": 1, "type": "attack", "rarity": "common",
            "description": "Deal 7 [10] Pyro damage. If it sets off an "
                           "Elemental Reaction, deal 7 [10] more.",
            "effects": [{"op": "varka", "kind": "kindled_edge",
                         "target": "enemy", "base": k["kindled_base"]}],
            "upgrade": {"varka_base": 3}},
        vk + "gust_ward": {
            **base, "id": vk + "storm_battery", "name": "Storm Battery",
            "cost": 1, "type": "attack", "rarity": "uncommon",
            "description": "Deal 2 [3] Electro damage to ALL enemies for each "
                           "other card in your hand.",
            "effects": [{"op": "varka", "kind": "storm_battery",
                         "target": "all_enemies", "per": k["storm_per"]}],
            "upgrade": {"varka_per": 1}},
        vk + "favonius_drill": {
            **base, "id": vk + "frost_ward", "name": "Frost Ward",
            "cost": 1, "type": "skill", "rarity": "common",
            "description": "Apply 1 Weak to each enemy with an aura. Gain "
                           "3 [4] Block for each.",
            "effects": [{"op": "varka", "kind": "frost_ward",
                         "target": "all_enemies", "amount": k["frost_per"]}],
            "upgrade": {"varka_amount": 1}},
        # aoe-trim sec.4: Awakening at one enemy, same numbers.
        vk + "razor_claw_and_thunder": {
            **base, **knight, "id": vk + "razor_claw_and_thunder",
            "name": "Razor: Awakening", "rarity": "common",
            "element": "electro", "cost": 1, "type": "skill",
            "description": "Deal Electro damage to an enemy, more if it "
                           "already has Electro.",
            "effects": [{"op": "varka", "kind": "awakening_single",
                         "target": "enemy", "base": k["awakening_base"],
                         "amount": k["awakening_more"]}],
            "upgrade": {"varka_base": 2}},
    }
    return rows, k


def _overlay_sheet(knobs=None):
    """The sheet with the rebalance rows swapped in (Wildfire Oath, Absolute
    Zero and Cycle of Seasons keep their rows: their change is the rule,
    `varka_oath.REBALANCE`; Cycle's number is a knob)."""
    import copy
    import yaml
    rows, k = rebalance_rows(knobs)
    raw = yaml.safe_load(_SHEET.read_text(encoding="utf-8"))
    out = []
    for d in raw:
        d = copy.deepcopy(d)
        if d.get("id") in rows:
            d = rows[d["id"]]
        elif d.get("id") == P + "cycle_of_seasons":
            d["effects"][0]["amount"] = k["cycle_amount"]
            d["description"] = ("Whenever your current element changes, deal "
                                "4 [6] damage to a random enemy.")
        elif d.get("id") == P + "wildfire_oath":
            d["description"] = ("Your first Attack each turn deals additional "
                                "damage equal to half your Pyro Oath.")
        elif d.get("id") == P + "absolute_zero":
            d["description"] = ("Whenever you apply Weak or Vulnerable to an "
                                "enemy, deal damage equal to your Cryo Oath "
                                "to it.")
        out.append(d)
    return out


# --- the process switch and the scorer surface --------------------------------

_ENABLED = False
WORLD = "current"
_SHEET = None


def set_world(world="current", knobs=None):
    """Point this process at a world: `current` is the sheet as it stands;
    `rebalance` is the overlay (`_overlay_sheet`) plus `varka_oath.REBALANCE`.
    Re-entrant (the tests flip it both ways)."""
    global WORLD, _SHEET
    import os
    import tempfile
    from pathlib import Path
    import yaml
    from tier0.content import loader
    from tier0.engine import varka_oath as V
    if _SHEET is None:
        _SHEET = loader.PROTOTYPE_SHEET
    loader.PROTOTYPE_SHEET = _SHEET
    if world == "rebalance":
        fd, path = tempfile.mkstemp(prefix="varka-rebalance-",
                                    suffix=".yaml")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            yaml.safe_dump(_overlay_sheet(knobs), fh, allow_unicode=True,
                           sort_keys=False)
        loader.PROTOTYPE_SHEET = Path(path)
        V.REBALANCE = True
    elif world == "current":
        V.REBALANCE = False
    else:
        raise ValueError(f"unknown world {world!r}")
    WORLD = world
    DECKS.clear()
    DECKS.update(deck_lists(world)[0])
    loader._prototype_index.cache_clear()
    loader.reset_arm_caches()
    _NOMINAL.clear()


def enable(world=None, knobs=None):
    global _ENABLED
    if world is not None:
        set_world(world, knobs)
    if _ENABLED:
        return
    from tier0 import constants as C
    C.SWIRL_PAYS = True
    C.CRYSTALLIZE_KEEPS_AURA = True
    from tier0.content import loader
    loader.reset_arm_caches()
    from tier0.pilot import policy
    orig = policy._active_effects

    def active(state, effect_list, card=None):
        for fx in orig(state, effect_list, card):
            yield from _translate(state, fx)

    policy._active_effects = active
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
        fresh = any(e.aura and not getattr(e, "aura_spent", False)
                    for e in state.living_enemies)
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
        yield {"op": "damage", "amount": base, "target": "all_enemies"}
    # --- the rebalance overlay's kinds (sim only) ---
    elif kind == "awakening_single":
        more = amt if any(e.aura == "electro"
                          for e in state.living_enemies) else 0
        yield {"op": "damage", "amount": base + more, "target": "enemy"}
        yield oath_proxy
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
    elif kind in ("change_of_guard", "cleanse", "swirled_take_more"):
        return
    else:
        return


def make_pilot():
    """The stock `generic` pilot, with his Powers played first when
    affordable, most expensive first (the Kokomi expansion harness's rule:
    the stock scorer prices a one-stack Power as almost nothing, so it holds
    them and a play rate would read the scorer, not the card)."""
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
        return base(state)

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
#: would read as blanks beside the rows they replace. The old world's kinds
#: are untouched, so `--world current` drafts exactly as before.
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
    if kind == "awakening_single":
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


def pmap(fn, jobs, argl, world="current", knobs=None):
    if jobs <= 1:
        enable(world, knobs)
        return [fn(a) for a in argl]
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(jobs, initializer=enable,
                                      initargs=(world, knobs)) as p:
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
                   "wildfire_oath", "absolute_zero", "cycle_of_seasons")


def _act1(rs):
    return sum(r["act1"] for r in rs), len(rs)


def report_bars(data, against=None, out=print):
    """The rebalance paper's bars (secs.5 and 6): the element spread, the
    starter spread, cross-element plays, Block and multi-target damage, and
    the new cards. Every rate is act 1 won on the stylised run."""
    runs, gaunt = data["runs"], data["gauntlet"]
    world = data.get("world", "current")
    elements = data.get("elements") or element_of(world)
    by = defaultdict(list)
    for r in runs:
        by[(r["pilot"], r["element"])].append(r)
    have = {r["pilot"] for r in runs}
    out(f"\n# Rebalance bars -- world `{world}`"
        + (f", knobs {data['knobs']}" if data.get("knobs") else ""))

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
        out("\n## Paired against the other world (same seeds, starts, "
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
    ap.add_argument("--world", default="current",
                    choices=("current", "rebalance"),
                    help="rebalance: the paper's overlay rows and rules "
                         "(sim only, `rebalance_rows`)")
    ap.add_argument("--no-gauntlet", action="store_true",
                    help="skip the gauntlet (its offers still drafted for "
                         "the card table)")
    ap.add_argument("--knob", action="append", default=[],
                    help="name=int, a rebalance number (KNOBS); repeatable")
    args = ap.parse_args(argv)
    knobs = {}
    for kv in args.knob:
        name, _, val = kv.partition("=")
        knobs[name] = int(val)
    if knobs and args.world != "rebalance":
        ap.error("--knob moves the rebalance world's numbers only")
    if args.report:
        with open(args.report, encoding="utf-8") as fh:
            data = json.load(fh)
        against = None
        if args.against:
            with open(args.against, encoding="utf-8") as fh:
                against = json.load(fh)
        report(data, against)
        return
    enable(args.world, knobs)
    from tier0.content import loader
    pl = pool()
    seeds = [args.seed + i for i in range(args.seeds)]
    pilots = [p for p in args.pilots.split(",") if p]
    argl = [(s, p, e) for p in pilots for e in starts_for(p) for s in seeds]
    print(f"{len(argl)} runs + {len(argl)} gauntlets", file=sys.stderr)
    runs = pmap(_w, args.jobs, argl, args.world, knobs)
    gaunt = pmap(_wg if not args.no_gauntlet else _wo, args.jobs, argl,
                 args.world, knobs)
    traces = [f["trace"] for src in (runs, gaunt) for r in src
              for f in r["fights"] if f.get("trace")][:3]
    for src in (runs, gaunt):
        for r in src:
            for f in r["fights"]:
                f.pop("trace", None)
    data = {"seeds": args.seeds, "seed": args.seed, "world": args.world,
            "knobs": dict(KNOBS, **knobs) if args.world == "rebalance"
            else {},
            "elements": element_of(args.world),
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
