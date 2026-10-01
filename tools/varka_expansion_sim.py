#!/usr/bin/env python3
"""VARKA EXPANSION -- the paper's sec.5 sim (Prototype stage, exploration,
not a Balance measurement).

    .venv/Scripts/python.exe -m tools.varka_expansion_sim --seeds 500 --seed 7 --jobs 14 --json out.json
    .venv/Scripts/python.exe -m tools.varka_expansion_sim --report out.json [--against old.json]

Answers sec.5.2 of `review/active/varka-expansion-2026-10-01.md` on the
BUILT rows (tier0 with `varka_oath.VARKA_OATH`, `C.SWIRL_PAYS` and
`C.CRYSTALLIZE_KEEPS_AURA` on for THIS PROCESS ONLY, as the Varka tests
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

FOCUS = ["favonius_drill", "oathsworn_strike", "eye_of_the_storm",
         "stormward_stance", "oath_of_the_knights", "favonian_standard",
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
SWITCH = ["shifting_gale", "cycle_of_seasons", "four_banners", "weathervane",
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
PILOTS = ("default",) + tuple(DECKS)


def starts_for(pilot):
    if pilot.startswith("mono_"):
        return (pilot[5:],)
    return ELEMENTS


# --- the process switch and the scorer surface --------------------------------

_ENABLED = False


def enable():
    global _ENABLED
    if _ENABLED:
        return
    from tier0 import constants as C
    from tier0.engine import varka_oath as V
    V.VARKA_OATH = True
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
        sc = {c: draft.score_offer(loader.get_card(c), starter, "generic")
              for c in ids}
        priced = sorted(v for v in sc.values()
                        if v >= C.DRAFT_SKIP_THRESHOLD)
        med = st.median(priced) if priced else 1.0
        _NOMINAL[element] = (med, frozenset(
            c for c, v in sc.items() if v < C.DRAFT_SKIP_THRESHOLD))
    return _NOMINAL[element]


def _default(card, deck_cards, element):
    from tier05 import draft
    med, low = _nominal(element)
    if card.id in low:
        return med
    return draft.score_offer(card, deck_cards, "generic")


def _score(card, deck, deck_cards, pilot, element):
    from tier0 import constants as C
    floor = C.DRAFT_SKIP_THRESHOLD
    if pilot == "default":
        return _default(card, deck_cards, element), floor
    d = DECKS[pilot]
    if card.id in d["against"]:
        return -1.0, floor
    if card.id in d["core"]:
        knight = pilot.startswith("mono_") and card.id[len(P):] in KNIGHTS.get(
            pilot[5:], ())
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
    return {"won": won, "turns": s.turn,
            "hp_lost": start - max(0, s.player.hp),
            "hp_end": max(0, s.player.hp), "plays": dict(plays),
            "oath": oath, "stall": s.player.alive and bool(s.living_enemies),
            "deck": full, "error": None}


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
    """Drop the per-fight deck list down to what the report reads."""
    for f in r["fights"]:
        f["deck"] = Counter(f["deck"])
    return r


def _w(args):
    enable()
    return _slim(run(*args))


def _wg(args):
    enable()
    return _slim(gauntlet(*args))


def pmap(fn, jobs, argl):
    if jobs <= 1:
        return [fn(a) for a in argl]
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(jobs) as p:
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
                ga.append((st.mean(f["won"] for f in gm[s]["fights"]),
                           st.mean(f["won"] for f in gd[s]["fights"])))
        d1 = paired_diff(*zip(*a))
        d2 = paired_diff(*zip(*b))
        d3 = paired_diff(*zip(*ga))
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
                return st.mean(fs)
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
            for f in r["fights"]:
                for c, n in f["deck"].items():
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


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=500)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--jobs", type=int, default=14)
    ap.add_argument("--pilots", default=",".join(PILOTS))
    ap.add_argument("--json", help="write the raw results here")
    ap.add_argument("--report", help="report a --json file instead of running")
    ap.add_argument("--against", help="a --json file from the other pool")
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
    gaunt = pmap(_wg, args.jobs, argl)
    traces = [f["trace"] for src in (runs, gaunt) for r in src
              for f in r["fights"] if f.get("trace")][:3]
    for src in (runs, gaunt):
        for r in src:
            for f in r["fights"]:
                f.pop("trace", None)
    data = {"seeds": args.seeds, "seed": args.seed,
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
