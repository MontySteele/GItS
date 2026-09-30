#!/usr/bin/env python3
"""VARKA OATH REWORK -- the paper-stage sim report (exploration, not quotable).

    .venv/Scripts/python.exe -m tools.varka_oath_report --seeds 400 --seed 7 --jobs 14

Answers sec.11.6 of `review/active/varka-paper-kit-2026-09-28.md` (branch
`varka-oath-paper`) with the arm `tier0.engine.varka_oath` switched on for
THIS PROCESS ONLY. Nothing on disk moves: no constant, sheet or stamp.

Instruments:
  * CURVE -- granted decks against driver-only training dummies (999 HP,
    Varka at 999 HP, fights capped at 12 turns in this process), so every
    fight runs turns 1-12. One dummy hitting 8 a turn, or three hitting 3.
  * RUN -- a stylised act 1 on the tier-0.5 act-1 pools (`tier05/acts.py`):
    floors N N N N E R N N E R B (first three N easy, the rest hard; two
    elites; the boss drawn from the act-1 boss pool). A card reward of three
    after every fight (rarity C/U/R 60/37/3 after a normal fight, 50/40/10
    after an elite), a draft rule per policy (below), rests heal 30% of max
    HP. No relics beyond the Fang, no potions, no gold, no shops, no
    upgrades, no events. Encounters, HP rolls and offers are drawn from
    arm-independent streams, so every arm meets the same fights and offers.
  * STARTERS -- every act-1 encounter at full HP with starter decks only:
    the Oath starter (each Knight) and the reference Ironclad and Silent
    starters (their repo pilots), split by the number of enemies.
  * BRANCH -- STAY or SWITCH from one mid-fight state: two runs of the same
    seed, identical up to the branch turn, then three turns measured.
  (The batch-one comparison was dropped on the 2026-09-29 second spec
  update: compare options within the new design.)

Draft rules (a score per card; skip when the best offer scores under 3;
per-card caps):
  * focused (home element E): pool Knight of E 10 (cap 3), Favonius Drill 8
    (2), Oath of the Knights 8 (1), Eye of the Storm 7 (2), Wall of Gales 7,
    Tempest Charge 6, Wind Wall 6 (2),
    Grand Master's Order 5 (1), Stormward Stance 5 (1), Sworn Brotherhood 5
    (1), Tailwind Stride 5 (1), Favonius Cut 5 (1), Gale Sweep 5 (1), Squall
    4, Updraft 4, Converging Winds 3 (1), anything else 0-2; off-element
    Knights 0.
  * juggling: every pool Knight 8 (cap 1 each), Boreas Unbound 8 (1), Rally
    to the Banner 7 (1), Sworn Brotherhood 7 (1), Four Winds' Accord 6 (1),
    Favonius Drill 6 (2), Wind Wall 6 (2), Eye of the Storm
    4 (1), Oath of the Knights 4 (1), the Anemo Attacks as focused.
"""

from __future__ import annotations

import argparse
import random
import statistics as st
import sys
from collections import defaultdict

ELEMENTS = ("pyro", "hydro", "electro", "cryo")
# R3b (the default since the 2026-09-29 third update): Oath per card play,
# Ascension's elemental hit gains none. R3 is the previous default (Oath per
# application / per Swirl). V1 / V2 are the paper's picks on top of R3b.
VARIANTS = {"R3b": dict(payout=True, apply_oath=True, per_card=True),
            "R3": dict(payout=True, apply_oath=True, per_card=False),
            "V1": dict(payout=False, apply_oath=True, per_card=True),
            "V2": dict(payout=True, apply_oath=False, per_card=True)}
DEF = "R3b"
# Starter-evenness round (all on R3b; the section `svar` only).
SVARIANTS = {
    "S1": dict(VARIANTS[DEF], starter_set="S1"),
    "S2": dict(VARIANTS[DEF], starter_set="S2"),
    "S3": dict(VARIANTS[DEF], pay_electro=3),
    "S4": dict(VARIANTS[DEF], starter_set="S1", pay_electro=3),
    "S2+S3": dict(VARIANTS[DEF], starter_set="S2", pay_electro=3),
    "S5": dict(VARIANTS[DEF], starter_set="S5"),
    "S6": dict(VARIANTS[DEF], starter_set="S6"),
    "S7": dict(VARIANTS[DEF], starter_set="S7"),
}
ALLVAR = dict(VARIANTS, **SVARIANTS)
TEMPLATE = ["N", "N", "N", "N", "E", "R", "N", "N", "E", "R", "B"]

DUMMIES = {
    "dummy1": [dict(name="dummy", hp=999, intents=[
        {"kind": "attack", "amount": 8}])],
    "dummy3": [dict(name=f"dummy{i}", hp=999, intents=[
        {"kind": "attack", "amount": 3}]) for i in range(3)],
}


def enable():
    from tier0.engine import varka_oath
    varka_oath.enable()


def _dummy(name):
    import copy
    from tier0.engine.state import Enemy
    return [Enemy(hp=d["hp"], max_hp=d["hp"], name=d["name"],
                  intents=copy.deepcopy(d["intents"]))
            for d in DUMMIES[name]]


# --- decks -----------------------------------------------------------------

def deck_for(kind, home):
    from tier0.engine import varka_oath as O
    base = O.starter(home)
    k = O.POOL_KNIGHTS
    if kind == "starter":
        return base
    if kind == "F":            # focused, a mid-act build
        return base + [k[home], k[home], "favonius_drill", "favonius_drill",
                       "tempest_charge", "eye_of_the_storm",
                       "oath_of_the_knights"]
    if kind == "F+":           # the most focus the pool allows
        return deck_for("F", home) + ["grand_masters_order",
                                      "sworn_brotherhood", "wall_of_gales",
                                      "gale_sweep", k[home]]
    if kind == "J":            # juggling, a mid-act build
        return base + [k[e] for e in ELEMENTS] + [
            "favonius_drill", "tempest_charge", "eye_of_the_storm",
            "oath_of_the_knights", "rally_to_the_banner"]
    raise KeyError(kind)


# --- one fight ---------------------------------------------------------------

def oath_fight(deck, enemies, policy, home, seed, hp=None, variant="R3b"):
    from tier0.engine import combat, varka_oath as O
    from tier0.engine.varka_oath_pilot import VarkaOathPilot
    player = O.build_player(deck, hp=hp, **ALLVAR[variant])
    start = player.hp
    s = combat.run_fight(player, enemies, VarkaOathPilot(policy, home),
                         seed=seed)
    vs = player.varka
    plays = defaultdict(int)
    for r in s.log:
        if r.get("event") == "play":
            plays[r["card"]] += 1
    return {"won": bool(s.player.alive) and not s.living_enemies,
            "turns": s.turn, "hp_lost": start - max(0, s.player.hp),
            "hp_end": max(0, s.player.hp),
            "asc": list(vs.asc), "turn_oath": list(vs.turn_oath),
            "eye": list(vs.eye_rows), "okn_block": vs.okn_block,
            "okn_rows": list(vs.okn_rows), "okn": vs.okn,
            "plays": dict(plays), "swirls": vs.swirls,
            "pay": dict(vs.pay), "switches": vs.switches,
            "oath_end": dict(vs.oath), "current": vs.current,
            "fang_turn": vs.asc_created_turn}


def ref_fight(character, pilot_id, enemies, seed, hp=None):
    from tier0.content import loader
    from tier0.engine import combat
    from tier0.pilot.policy import make_pilot
    player = loader.build_player(character)
    if hp is not None:
        player.hp = min(hp, player.max_hp)
    start = player.hp
    s = combat.run_fight(player, enemies,
                         make_pilot(loader.pilot_weights(pilot_id)),
                         seed=seed)
    return {"won": bool(s.player.alive) and not s.living_enemies,
            "turns": s.turn, "hp_lost": start - max(0, s.player.hp),
            "hp_end": max(0, s.player.hp), "max_hp": player.max_hp}


# --- the act-1 run --------------------------------------------------------------

RARITY = {"N": (60, 37, 3), "E": (50, 40, 10)}

F_SCORE = {"favonius_drill": (8, 2), "oath_of_the_knights": (8, 1),
           "eye_of_the_storm": (7, 2), "wall_of_gales": (7, 1),
           "tempest_charge": (6, 2), "wind_wall": (6, 2),
           "grand_masters_order": (5, 1), "stormward_stance": (5, 1),
           "sworn_brotherhood": (5, 1), "tailwind_stride": (5, 1),
           "favonius_cut": (5, 1), "gale_sweep": (5, 1), "squall": (4, 2),
           "updraft": (4, 2), "converging_winds": (3, 1),
           "knights_roll_call": (1, 1), "rally_to_the_banner": (1, 1),
           "four_winds_accord": (0, 0), "boreas_unbound": (1, 1)}
J_SCORE = dict(F_SCORE, **{
    "boreas_unbound": (8, 1), "rally_to_the_banner": (7, 1),
    "sworn_brotherhood": (7, 1), "four_winds_accord": (6, 1),
    "favonius_drill": (6, 2), "eye_of_the_storm": (4, 1),
    "oath_of_the_knights": (4, 1), "knights_roll_call": (4, 1)})

def _offer(rng, kind, pool):
    w = RARITY[kind]
    out = []
    while len(out) < 3:
        r = rng.choices(("common", "uncommon", "rare"), weights=w)[0]
        c = rng.choice(pool[r])
        if c not in out:
            out.append(c)
    return out


def _score(card, deck, policy, home):
    from tier0.engine import varka_oath as O
    knight_el = {v: k for k, v in O.POOL_KNIGHTS.items()}
    if card in knight_el:
        if policy == "focused":
            s, cap = (10, 3) if knight_el[card] == home else (0, 0)
        else:
            s, cap = (8, 1)
    else:
        s, cap = (F_SCORE if policy == "focused" else J_SCORE).get(
            card, (0, 0))
    if deck.count(card) >= cap:
        return 0
    return s


REFS = {"ref_ironclad": ("ref_ironclad", "generic", 80),
        "ref_silent": ("ref_silent", "silent", 70)}


def run_act1(seed, policy, home, variant="R3b", draft=True):
    """One stylised act 1. policy in focused / juggling / ref_*.
    `draft=False` keeps the starter all act (the reference kits always do:
    the calibration rows)."""
    from tier0.engine import varka_oath as O
    from tier05 import acts
    enc_rng = random.Random(seed)
    draw = acts.ActDraw(enc_rng, act=0)
    offer_rng = random.Random(seed + 10 ** 6)
    if policy in REFS:
        deck, pool = [], O.POOL        # offers drawn, never taken
    else:
        deck = O.starter(home)
        pool = O.POOL
    max_hp = REFS[policy][2] if policy in REFS else 80
    if policy in REFS:
        draft = False
    hp = max_hp
    fights = []
    for floor, kind in enumerate(TEMPLATE):
        if kind == "R":
            hp = min(max_hp, hp + int(0.3 * max_hp))
            continue
        spec = draw.encounter_for(kind, enc_rng)
        enemies = acts.spawn(spec, enc_rng)
        fseed = seed * 100 + floor
        n_enemies = len(enemies)
        if policy in REFS:
            ch, pil, _ = REFS[policy]
            r = ref_fight(ch, pil, enemies, fseed, hp=hp)
        else:
            r = oath_fight(deck, enemies, policy, home, fseed, hp=hp,
                           variant=variant)
        r.update(kind=kind, enc=spec["id"], floor=floor, hp_in=hp,
                 deck_size=len(deck), n_enemies=n_enemies, deck=list(deck))
        fights.append(r)
        hp = r["hp_end"]
        if not r["won"]:
            break
        if kind != "B":
            offer = _offer(offer_rng, kind, pool)
            if not draft:
                continue
            scored = sorted(((_score(c, deck, policy, home), c)
                             for c in offer), reverse=True)
            if scored[0][0] >= 3:
                deck.append(scored[0][1])
    won = bool(fights) and fights[-1]["kind"] == "B" and fights[-1]["won"]
    return {"seed": seed, "policy": policy, "home": home,
            "variant": variant if draft else "S", "won": won, "fights": fights,
            "deck": list(deck), "hp_lost": sum(f["hp_lost"] for f in fights),
            "floor_died": None if won else fights[-1]["floor"]}


# --- workers -----------------------------------------------------------------------

def _w_run(args):
    enable()
    return run_act1(*args)


def _w_curve(args):
    from tier0 import constants as C
    enable()
    deck_kind, home, policy, dummy, seed, variant = args
    C.MAX_TURNS = 13                      # this worker process only
    r = oath_fight(deck_for(deck_kind, home), _dummy(dummy), policy, home,
                   seed, hp=999, variant=variant)
    r.update(deck=deck_kind, home=home, policy=policy, dummy=dummy,
             variant=variant)
    return r


def pmap(fn, jobs, argl):
    if jobs <= 1:
        return [fn(a) for a in argl]
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(jobs) as pool:
        return pool.map(fn, argl, chunksize=8)


# --- stats -----------------------------------------------------------------------------

def m(xs, d=1):
    xs = list(xs)
    return f"{st.mean(xs):.{d}f}" if xs else "-"


def msd(xs, d=1):
    xs = list(xs)
    if not xs:
        return "-"
    return f"{st.mean(xs):.{d}f} ±{st.pstdev(xs):.{d}f}"


def pct(k, n):
    return f"{100.0 * k / n:.1f}%" if n else "-"


def ci95(k, n):
    if not n:
        return 0.0
    p = k / n
    return 196.0 * (p * (1 - p) / n) ** 0.5


# --- sections ------------------------------------------------------------------------------

def sec_curve(out, seeds, seed0, jobs):
    out("\n## 1. Ascension curve (training dummies, Varka at 999 HP, "
        f"turns 1-12; n = {seeds} fights per row, seeds {seed0}.."
        f"{seed0 + seeds - 1})")
    cells = []
    for home in ELEMENTS:
        for deck, pol in (("starter", "focused"), ("starter", "juggling"),
                          ("F", "focused"), ("J", "juggling"),
                          ("F+", "focused")):
            for dummy in DUMMIES:
                for v in VARIANTS:
                    if v not in (DEF, "R3") and deck not in ("F", "J"):
                        continue
                    cells.append((deck, home, pol, dummy, v))
    argl = [c[:4] + (seed0 + i, c[4]) for c in cells for i in range(seeds)]
    rows = pmap(_w_curve, jobs, argl)
    by = defaultdict(list)
    for r in rows:
        by[(r["deck"], r["home"], r["policy"], r["dummy"],
            r["variant"])].append(r)
    flags = []
    for dummy in DUMMIES:
        for v in VARIANTS:
            out(f"\n### {dummy}, variant {v}: current-element Oath at the "
                "start of turn t / mean Ascension damage per cast on turn t "
                "(printed 6 + 3 x Oath; share of fights casting that turn)")
            out("| deck / policy / start | " + " | ".join(
                f"t{t}" for t in (1, 2, 3, 4, 6, 8, 10, 12)) + " | casts/fight"
                " | max cast |")
            out("|---" * 11 + "|")
            for home in ELEMENTS:
                for deck, pol in (("starter", "focused"),
                                  ("starter", "juggling"), ("F", "focused"),
                                  ("J", "juggling"), ("F+", "focused")):
                    rs = by.get((deck, home, pol, dummy, v))
                    if not rs:
                        continue
                    cellsx = []
                    for t in (1, 2, 3, 4, 6, 8, 10, 12):
                        o = [next((x[2] for x in r["turn_oath"]
                                   if x[0] == t), 0) for r in rs]
                        casts = [a for r in rs for a in r["asc"]
                                 if a["turn"] == t]
                        share = len({id(r) for r in rs for a in r["asc"]
                                     if a["turn"] == t})
                        cellsx.append(
                            f"{m(o)} / {m(a['printed'] for a in casts)}"
                            f" ({100 * share // len(rs)}%)")
                    allc = [a for r in rs for a in r["asc"]]
                    mx = max((a["printed"] for a in allc), default=0)
                    out(f"| {deck} / {pol} / {home} | " + " | ".join(cellsx)
                        + f" | {len(allc) / len(rs):.2f} | {mx} |")
                    by8 = [a["printed"] for a in allc if a["turn"] <= 8]
                    over = sum(1 for x in by8 if x > 60)
                    m8 = [a["printed"] for a in allc if a["turn"] == 8]
                    if over or (m8 and st.mean(m8) > 60):
                        flags.append(f"{dummy} {v} {deck}/{pol}/{home}: "
                                     f"{over} casts over 60 by turn 8 "
                                     f"(of {len(by8)}); mean at t8 "
                                     f"{m(m8)}")
    out("\n**Flag (Ascension alone over 60 per cast by turn 8):**")
    for f in flags or ["none"]:
        out(f"- {f}")
    return by


def sec_turn1(out, seeds, seed0):
    """sec.11.3's worked turn: how often does a Barbara start play it?"""
    from tier0.engine import combat, varka_oath as O
    from tier0.engine.varka_oath_pilot import VarkaOathPilot
    from tier05 import acts
    out("\n## 1b. Turn one with Barbara: Shining Miracle, R3b "
        f"(starter, focused, n = {seeds} per encounter)")
    out("| encounter | Barbara in the opening hand | ...with Windbound too"
        " | turn-1 damage (all fights) | turn-1 Block | turn-1 dmg / Block "
        "when both are in hand | hit 18 dmg and 13 Block |")
    out("|---|---|---|---|---|---|---|")
    easy = acts.pools(0)["easy"]
    for spec in easy + acts.pools(0)["elite"]:
        rows = []
        for i in range(seeds):
            enemies = acts.spawn(spec, random.Random(seed0 + i))
            player = O.build_player(O.starter("hydro"), **VARIANTS[DEF])
            s = combat.run_fight(player, enemies,
                                 VarkaOathPilot("focused", "hydro"),
                                 seed=seed0 + i)
            t1 = [r for r in s.log]
            # turn-1 slice: from the first turn_open to the second
            opens = [k for k, r in enumerate(s.log)
                     if r.get("event") == "turn_open"]
            end = opens[1] if len(opens) > 1 else len(s.log)
            sl = s.log[opens[0]:end] if opens else []
            plays = [r["card"] for r in sl if r.get("event") == "play"]
            dmg = sum(r.get("amount", 0) for r in sl
                      if r.get("event") == "damage")
            blk = sum(r.get("amount", 0) for r in sl
                      if r.get("event") == "block")
            rows.append((("varka_barbara_shining_miracle" in plays),
                         ("varka_windbound_execution" in plays), dmg, blk))
            del t1
        n = len(rows)
        bb = [r for r in rows if r[0]]
        both = [r for r in rows if r[0] and r[1]]
        hit = sum(1 for r in rows if r[2] >= 18 and r[3] >= 13)
        out(f"| {spec['id']} | {pct(len(bb), n)} | {pct(len(both), n)} | "
            f"{m(r[2] for r in rows)} | {m(r[3] for r in rows)} | "
            f"{m(r[2] for r in both)} / {m(r[3] for r in both)} | "
            f"{pct(hit, n)} |")
    out("(\"Played on turn 1\" is read off the play log; Block counts every "
        "Block event of turn 1, including Defends.)")


def _size(n):
    return "1 enemy" if n == 1 else "2 enemies" if n == 2 else "3+ enemies"


SIZES = ("1 enemy", "2 enemies", "3+ enemies")


def sec_runs(out, seeds, seed0, jobs):
    out(f"\n## 2. Stylised act 1: win rate and HP loss by starting Knight "
        f"(n = {seeds} runs per cell, seeds {seed0}..{seed0 + seeds - 1}, "
        "paired: every cell meets the same fights and offers)")
    argl = []
    for v in VARIANTS:
        for pol in ("focused", "juggling"):
            for home in ELEMENTS:
                for i in range(seeds):
                    argl.append((seed0 + i, pol, home, v))
    for i in range(seeds):
        # calibration rows: starters kept all act, no drafting
        argl.append((seed0 + i, "ref_ironclad", "none", DEF, False))
        argl.append((seed0 + i, "ref_silent", "none", DEF, False))
        for home in ELEMENTS:
            argl.append((seed0 + i, "focused", home, DEF, False))
    rows = pmap(_w_run, jobs, argl)
    by = defaultdict(list)
    for r in rows:
        by[(r["variant"], r["policy"], r["home"])].append(r)
    for v in VARIANTS:
        out(f"\n### Variant {v}")
        out("| policy | start | act won (±95% CI) | HP lost (act) | HP lost, "
            "elite 1 | HP lost, every elite | boss won when reached |")
        out("|---|---|---|---|---|---|---|")
        for pol in ("focused", "juggling"):
            wins = []
            for home in ELEMENTS:
                rs = by[(v, pol, home)]
                n = len(rs)
                k = sum(r["won"] for r in rs)
                wins.append(100 * k / n)
                e1 = [next((f["hp_lost"] for f in r["fights"]
                            if f["kind"] == "E"), None) for r in rs]
                e1 = [x for x in e1 if x is not None]
                ea = [f["hp_lost"] for r in rs for f in r["fights"]
                      if f["kind"] == "E"]
                boss = [f for r in rs for f in r["fights"]
                        if f["kind"] == "B"]
                out(f"| {pol} | {home} | {pct(k, n)} ±{ci95(k, n):.1f} | "
                    f"{msd(r['hp_lost'] for r in rs)} | {msd(e1)} | "
                    f"{msd(ea)} (n={len(ea)}) | "
                    f"{pct(sum(f['won'] for f in boss), len(boss))} |")
            out(f"| {pol} | spread | max - min = "
                f"{max(wins) - min(wins):.1f} points | | | | |")

    out("\n**Every fight of the drafted runs split by the number of enemies "
        "at the start (R3b; HP lost per fight, fights won, n fights).** "
        "Single-enemy fights are nibbit, mawler, fogmog (it summons), "
        "sewer_clam, byrdonis, bygone_effigy and both bosses; 2 is "
        "slime_group; 3+ is inklets (3) and phantasmal_gardener (4).")
    out("| policy | start | " + " | ".join(SIZES) + " |")
    out("|---|---|---|---|---|")
    for pol in ("focused", "juggling"):
        for home in ELEMENTS:
            cells = []
            for sz in SIZES:
                fs = [f for r in by[(DEF, pol, home)] for f in r["fights"]
                      if _size(f["n_enemies"]) == sz]
                cells.append(f"{m(f['hp_lost'] for f in fs)} HP, "
                             f"{pct(sum(f['won'] for f in fs), len(fs))} "
                             f"(n={len(fs)})")
            out(f"| {pol} | {home} | " + " | ".join(cells) + " |")

    out("\n**Calibration: the same act with the starter kept all act "
        "(no drafting).**")
    out("| arm | act won | HP lost (act) | HP lost, elite 1 | "
        "died at the first elite |")
    out("|---|---|---|---|---|")
    for pol, home in ([("focused", h) for h in ELEMENTS]
                      + [("ref_ironclad", "none"), ("ref_silent", "none")]):
        rs = by[("S", pol, home)]
        n = len(rs)
        k = sum(r["won"] for r in rs)
        e1 = [next((f["hp_lost"] for f in r["fights"] if f["kind"] == "E"),
                   None) for r in rs]
        e1 = [x for x in e1 if x is not None]
        d1 = sum(1 for r in rs if not r["won"]
                 and r["fights"][-1]["kind"] == "E"
                 and sum(f["kind"] == "E" for f in r["fights"]) == 1)
        label = f"Oath starter, {home}" if pol == "focused" else pol
        out(f"| {label} | {pct(k, n)} ±{ci95(k, n):.1f} | "
            f"{msd(r['hp_lost'] for r in rs)} | {msd(e1)} | {pct(d1, n)} |")

    out("\n**Ascension in the drafted runs, every cast in every fight: mean "
        "printed damage (6 + 3 x Oath) by the turn cast, casts over 60 by "
        "turn 8, and the largest.**")
    out("| variant | policy | start | t1-2 | t3-4 | t5-6 | t7-8 | t9-12 | "
        "t13+ | casts / fight | casts > 60 by t8 (fights) | max |")
    out("|---|---|---|---|---|---|---|---|---|---|---|---|")
    buckets = ((1, 2), (3, 4), (5, 6), (7, 8), (9, 12), (13, 99))
    for v in VARIANTS:
        for pol in ("focused", "juggling"):
            for home in ELEMENTS:
                rs = by[(v, pol, home)]
                casts = [a for r in rs for f in r["fights"] for a in f["asc"]]
                nf = sum(len(r["fights"]) for r in rs)
                cells = [m(a["printed"] for a in casts
                           if lo <= a["turn"] <= hi) for lo, hi in buckets]
                over = sum(1 for a in casts if a["turn"] <= 8
                           and a["printed"] > 60)
                fl = sum(1 for r in rs for f in r["fights"]
                         if any(a["turn"] <= 8 and a["printed"] > 60
                                for a in f["asc"]))
                mx = max((a["printed"] for a in casts), default=0)
                out(f"| {v} | {pol} | {home} | " + " | ".join(cells)
                    + f" | {len(casts) / max(1, nf):.2f} | {over} ({fl}) "
                    f"| {mx} |")

    # What produced the flag, and what those decks carried.
    out("\n**The fights that tripped the flag (R3b, a cast over 60 by turn "
        "8): the encounter, the enemies at the start, and the drafted deck "
        "against the rest of the same start's fights.**")
    for pol in ("focused", "juggling"):
        for home in ELEMENTS:
            flagged, rest = [], []
            for r in by[(DEF, pol, home)]:
                for f in r["fights"]:
                    hit = any(a["turn"] <= 8 and a["printed"] > 60
                              for a in f["asc"])
                    (flagged if hit else rest).append(f)
            if not flagged:
                continue
            encs = defaultdict(int)
            for f in flagged:
                encs[f"{f['enc']} ({f['n_enemies']})"] += 1
            top = ", ".join(f"{k} {v}" for k, v in sorted(
                encs.items(), key=lambda kv: -kv[1])[:5])
            out(f"- {pol}/{home}: {len(flagged)} fights of "
                f"{len(flagged) + len(rest)}. Encounters: {top}.")
            cnt_f, cnt_r = defaultdict(float), defaultdict(float)
            for f in flagged:
                for c in f["deck"]:
                    cnt_f[c] += 1 / len(flagged)
            for f in rest:
                for c in f["deck"]:
                    cnt_r[c] += 1 / max(1, len(rest))
            keys = sorted(set(cnt_f) | set(cnt_r),
                          key=lambda c: -(cnt_f[c] - cnt_r[c]))
            more = ", ".join(f"{c} {cnt_f[c]:.2f} vs {cnt_r[c]:.2f}"
                             for c in keys[:5] if cnt_f[c] - cnt_r[c] > 0.05)
            less = ", ".join(f"{c} {cnt_f[c]:.2f} vs {cnt_r[c]:.2f}"
                             for c in keys[::-1][:5]
                             if cnt_r[c] - cnt_f[c] > 0.05)
            out(f"  - copies per deck, flagged vs the rest: more "
                f"{more or '-'}; fewer {less or '-'}; deck size "
                f"{m((len(f['deck']) for f in flagged), 1)} vs "
                f"{m((len(f['deck']) for f in rest), 1)}; HP lost in the "
                f"fight {m(f['hp_lost'] for f in flagged)} vs "
                f"{m(f['hp_lost'] for f in rest)}.")

    out("\nDeaths by floor kind (R3b): " + "; ".join(
        f"{pol}/{home}: " + ", ".join(
            f"{kd} {sum(1 for r in by[(DEF, pol, home)] if not r['won'] and r['fights'][-1]['kind'] == kd)}"
            for kd in ("N", "E", "B"))
        for pol in ("focused", "juggling") for home in ELEMENTS))
    return by


def sec_readers(out, runs, seeds, seed0, jobs):
    out("\n## 3. Oath readers against Defend: Block per Energy")
    out("From the act-1 runs (R3b), every play of the card; Defend is 5 per "
        "Energy printed. Oath of the Knights: its whole fight's Block for "
        "its 1 Energy (fights where it was played).")
    out("| policy | start | Eye plays | Eye Block per play (p10/p50/p90) |"
        " Eye played at 0 Oath | OotK fights | OotK Block per fight | "
        "OotK per turn it was up |")
    out("|---|---|---|---|---|---|---|---|")
    from tools.varka_paper_report import q
    for pol in ("focused", "juggling"):
        for home in ELEMENTS + ("all",):
            homes = ELEMENTS if home == "all" else (home,)
            eyes, okn, oknt = [], [], []
            for h in homes:
                for r in runs[(DEF, pol, h)]:
                    for f in r["fights"]:
                        eyes += [x[1] for x in f["eye"]]
                        if f["okn"]:
                            okn.append(f["okn_block"])
                            oknt += [x[1] for x in f["okn_rows"]]
            if not eyes and not okn:
                continue
            zero = sum(1 for x in eyes if x == 0)
            eq = (f"{m(eyes)} ({q(eyes, .1):.0f}/{q(eyes, .5):.0f}/"
                  f"{q(eyes, .9):.0f})" if eyes else "-")
            out(f"| {pol} | {home} | {len(eyes)} | {eq} | "
                f"{pct(zero, len(eyes))} | {len(okn)} | {m(okn)} | "
                f"{m(oknt)} |")
    # the granted-deck read, fixed decks on the dummies' siblings: real fights
    out("\nGranted decks (R3b, and R3 = the old default) on the act-1 "
        "elites and bosses at full HP, "
        f"n = {seeds} per deck, start and fight (5 fights). F = focused "
        "build, J = juggling build; 'J / focused' plays the juggling build "
        "without switching (it holds the off-element Knights), which splits "
        "the deck's cost from the switching's cost:")
    argl = []
    from tier05 import acts
    specs = acts.pools(0)["elite"] + acts.boss_pool(0)
    for v in (DEF, "R3"):
        for home in ELEMENTS:
            for deck, pol in (("F", "focused"), ("F+", "focused"),
                              ("J", "focused"), ("J", "juggling")):
                for spec in specs:
                    for i in range(seeds):
                        argl.append((deck, home, pol, spec["id"], seed0 + i,
                                     v))
    rows = pmap(_w_granted, jobs, argl)
    by = defaultdict(list)
    for r in rows:
        by[(r["variant"], r["deck"], r["policy"], r["home"])].append(r)
        by[(r["variant"], r["deck"], r["policy"], "all")].append(r)
    out("| rules / deck / policy / start | Eye Block per play | OotK Block "
        "per fight (per turn up) | Defend | fights won | HP lost | switches "
        "per fight | Swirls per fight |")
    out("|---|---|---|---|---|---|---|---|")
    for v, home in [(v, h) for v in (DEF, "R3") for h in ELEMENTS + ("all",)]:
        for dk, pol in (("F", "focused"), ("F+", "focused"),
                        ("J", "focused"), ("J", "juggling")):
            rs = by[(v, dk, pol, home)]
            eyes = [x[1] for r in rs for x in r["eye"]]
            okn = [r["okn_block"] for r in rs if r["okn"]]
            oknt = [x[1] for r in rs for x in r["okn_rows"]]
            out(f"| {v} / {dk} / {pol} / {home} | {m(eyes)} "
                f"(n={len(eyes)}) | "
                f"{m(okn)} ({m(oknt)}) (n={len(okn)}) | 5 | "
                f"{pct(sum(r['won'] for r in rs), len(rs))} | "
                f"{msd(r['hp_lost'] for r in rs)} | "
                f"{m((r['switches'] for r in rs), 2)} | "
                f"{m((r['swirls'] for r in rs), 2)} |")
    return by


def _w_granted(args):
    from tier05 import acts
    enable()
    deck, home, pol, eid, seed, v = args
    specs = acts.pools(0)["elite"] + acts.boss_pool(0)
    spec = next(e for e in specs if e["id"] == eid)
    enemies = acts.spawn(spec, random.Random(seed))
    r = oath_fight(deck_for(deck, home), enemies, pol, home, seed,
                   variant=v)
    r.update(deck=deck, home=home, policy=pol, enc=eid, variant=v)
    return r


STARTER_ARMS = (tuple("oath_" + e for e in ELEMENTS)
                + tuple("oathR3_" + e for e in ELEMENTS)
                + ("ironclad", "silent"))


def _all_specs():
    from tier05 import acts
    p = acts.pools(0)
    return [("N-easy", e) for e in p["easy"]] + [
        ("N-hard", e) for e in p["hard"]] + [
        ("E", e) for e in p["elite"]] + [("B", e) for e in acts.boss_pool(0)]


def _w_starter(args):
    enable()
    arm, eid, seed = args
    from tier05 import acts
    tier, spec = next((t, e) for t, e in _all_specs() if e["id"] == eid)
    enemies = acts.spawn(spec, random.Random(seed))
    n = len(enemies)
    if arm.startswith("oath"):
        v = "R3" if arm.startswith("oathR3_") else DEF
        home = arm.split("_", 1)[1]
        from tier0.engine import varka_oath as O
        r = oath_fight(O.starter(home), enemies, "focused", home, seed,
                       variant=v)
    elif arm == "ironclad":
        r = ref_fight("ref_ironclad", "generic", enemies, seed)
    else:
        r = ref_fight("ref_silent", "silent", enemies, seed)
    r.update(arm=arm, enc=eid, tier=tier, n_enemies=n)
    return r


def sec_starters(out, seeds, seed0, jobs):
    out("\n## 4. Starter decks at full HP on every act-1 encounter, split by "
        f"the number of enemies (n = {seeds} per arm and encounter, seeds "
        f"{seed0}..)")
    specs = _all_specs()
    argl = [(a, e["id"], seed0 + i) for a in STARTER_ARMS for _, e in specs
            for i in range(seeds)]
    rows = pmap(_w_starter, jobs, argl)
    by = defaultdict(list)
    for r in rows:
        by[(r["arm"], r["enc"])].append(r)
        by[(r["arm"], _size(r["n_enemies"]))].append(r)
        if r["tier"] == "E":
            by[(r["arm"], "elite")].append(r)
    out("\n**By enemy count** (win % / HP lost per fight; HP lost counts to "
        "death). oath_* = R3b rules, oathR3_* = the old default. Ironclad "
        "starts at 80 HP, Silent at 70.")
    out("| arm | 1 enemy | 2 enemies | 3+ enemies | act-1 elites (all 3) |")
    out("|---|---|---|---|---|")
    for a in STARTER_ARMS:
        cells = []
        for key in SIZES + ("elite",):
            rs = by[(a, key)]
            cells.append(f"{pct(sum(r['won'] for r in rs), len(rs))} / "
                         f"{m(r['hp_lost'] for r in rs)}")
        out(f"| {a} | " + " | ".join(cells) + " |")
    out("\n**By encounter** (win % / HP lost):")
    out("| encounter (enemies) | " + " | ".join(STARTER_ARMS) + " |")
    out("|---" * (len(STARTER_ARMS) + 1) + "|")
    for tier, e in specs:
        rs0 = by[(STARTER_ARMS[0], e["id"])]
        cells = []
        for a in STARTER_ARMS:
            rs = by[(a, e["id"])]
            cells.append(f"{pct(sum(r['won'] for r in rs), len(rs))} / "
                         f"{m(r['hp_lost'] for r in rs)}")
        out(f"| {tier} {e['id']} ({rs0[0]['n_enemies']}) | "
            + " | ".join(cells) + " |")
    return by


# --- STAY vs SWITCH from one mid-fight state -----------------------------------

BRANCH_PAIRS = {
    # to-element: (encounters, first turn, last turn, condition name)
    "hydro": (("byrdonis", "bygone_effigy", "vantom", "lagavulin_matriarch"),
              4, 6, "a Hydro Knight in hand and at least 12 unblocked damage "
              "coming"),
    "cryo": (("byrdonis", "bygone_effigy", "vantom", "lagavulin_matriarch"),
             4, 6, "a Cryo Knight in hand, one enemy"),
    "electro": (("phantasmal_gardener", "inklets"), 3, 6,
                "an Electro Knight in hand and 3+ enemies standing"),
}


MOVERS = ("none", "unbound", "rally", "sworn")


def branch_deck(to_el, unbound):
    from tier0.engine import varka_oath as O
    return O.starter("pyro") + ["amber", O.POOL_KNIGHTS[to_el],
                                "favonius_drill", "tempest_charge",
                                "wind_wall", "eye_of_the_storm", "updraft"]


class BranchPilot:
    """Focused Pyro until the branch turn T (the first turn in [lo, hi]
    meeting the pair's condition). STAY keeps Pyro. SWITCH plays the
    to-element Knight first on turn T, then either stays on that element
    ("switch": its Pyro Knights are held) or plays the new element for the
    rest of turn T only and goes back to focused Pyro from T+1
    ("switch_back": the next Pyro Knight it plays switches it back).
    The runs are identical up to T: same seed, same decisions."""

    def __init__(self, to_el, mode, lo, hi, rally=False):
        from tier0.engine.varka_oath_pilot import VarkaOathPilot
        self.rally = rally
        self.rally_done = False
        self.pyro = VarkaOathPilot("focused", "pyro")
        self.after = VarkaOathPilot("focused", to_el)
        self.to_el, self.lo, self.hi = to_el, lo, hi
        self.switch = mode != "stay"
        self.back = mode == "switch_back"
        self.T = None
        self.forced = False
        self.rows = {}

    def _cond(self, state):
        from tier0.engine import varka_oath as O
        from tier0.engine.combat import card_playable
        from tier0.pilot.policy import _incoming_damage
        p = state.player
        k = [c for c in p.hand if O.knight_element(c) == self.to_el
             and card_playable(state, c)]
        if not k or p.varka.current != "pyro":
            return False
        if self.to_el == "hydro":
            return _incoming_damage(state) - p.block >= 12
        if self.to_el == "cryo":
            return len(state.living_enemies) == 1
        return len(state.living_enemies) >= 3

    def _fresh(self, state):
        return sum(1 for e in state.living_enemies
                   if e.aura and not e.aura_spent)

    def __call__(self, state):
        from tier0.engine import varka_oath as O
        vs = state.player.varka
        t = state.turn
        if t not in self.rows:
            self.rows[t] = {"start_fresh": self._fresh(state),
                            "hp": state.player.hp,
                            "oath": O.current_oath(vs),
                            "current": vs.current}
            if self.T is None and self.lo <= t <= self.hi and self._cond(
                    state):
                self.T = t
                self.rows[t]["oath_all"] = dict(vs.oath)
                if self.rally:
                    # Rally to the Banner in hand at the branch, every arm
                    state.player.hand.append(
                        O.make_card("rally_to_the_banner"))
        self.rows[t]["end_fresh"] = self._fresh(state)
        if (self.T is not None and self.switch and t >= self.T
                and not (self.back and t > self.T)):
            if not self.forced:
                self.forced = True
                k = next(c for c in state.player.hand
                         if O.knight_element(c) == self.to_el)
                tgt = self.pyro._paint_target(
                    state, self.to_el, self.pyro._dmg_est(state, vs, k))
                vs.playing = k
                vs.aim = tgt
                return k
            if self.rally and not self.rally_done and t == self.T:
                self.rally_done = True
                from tier0.engine.combat import card_playable
                r = next((c for c in state.player.hand
                          if c.id == "varka_rally_to_the_banner"
                          and card_playable(state, c)), None)
                if r is not None:
                    vs.playing = r
                    vs.aim = None
                    return r
            c = self.after(state)
        else:
            c = self.pyro(state)
        if c is None:
            self.rows[t]["end_fresh"] = self._fresh(state)
        return c


def _w_branch(args):
    from tier0.engine import combat, varka_oath as O
    from tier05 import acts
    enable()
    to_el, mover, v, eid, seed = args
    encs, lo, hi, _ = BRANCH_PAIRS[to_el]
    tier, spec = next((t, e) for t, e in _all_specs() if e["id"] == eid)
    res = {}
    for mode in ("stay", "switch", "switch_back"):
        enemies = acts.spawn(spec, random.Random(seed))
        player = O.build_player(branch_deck(to_el, False),
                                **VARIANTS[v])
        if mover == "unbound":
            player.varka.unbound = 1     # Boreas Unbound already in play
        if mover == "sworn":
            player.varka.sworn = 1       # Sworn Brotherhood already in play
        pilot = BranchPilot(to_el, mode, lo, hi, rally=mover == "rally")
        s = combat.run_fight(player, enemies, pilot, seed=seed)
        T = pilot.T
        if T is None:
            return None
        opens = [k for k, r in enumerate(s.log)
                 if r.get("event") == "turn_open"]
        start = opens[T - 1]
        end = opens[T + 2] if len(opens) > T + 2 else len(s.log)
        sl = s.log[start:end]
        hp0 = s.log[start]["hp"]
        hp3 = s.log[end]["hp"] if end < len(s.log) else max(0, s.player.hp)
        fresh_next = [pilot.rows.get(T + d, {}).get("start_fresh")
                      for d in (1, 2, 3)]
        fresh_end = [pilot.rows.get(T + d, {}).get("end_fresh")
                     for d in (0, 1, 2)]
        res[mode] = {
            "T": T, "oath": pilot.rows[T]["oath"],
            "dmg": sum(r.get("amount", 0) for r in sl
                       if r.get("event") == "damage"),
            "block": sum(r.get("amount", 0) for r in sl
                         if r.get("event") == "block"),
            "hp_lost": hp0 - hp3,
            "fresh_next": fresh_next, "fresh_end": fresh_end,
            "won": bool(s.player.alive) and not s.living_enemies,
            "fight_hp_lost": player.max_hp - max(0, s.player.hp),
            "energy": player.varka.unbound_energy}
    assert res["stay"]["T"] == res["switch"]["T"] == res[
        "switch_back"]["T"]
    return {"to": to_el, "mover": mover, "variant": v, "enc": eid,
            "seed": seed,
            "stay": res["stay"], "switch": res["switch"],
            "switch_back": res["switch_back"]}


def sec_branch(out, seeds, seed0, jobs):
    out("\n## 5. STAY or SWITCH from the same mid-fight state (3 turns)")
    out("Deck: the Pyro starter (Amber: Fiery Rain) + Amber: Baron Bunny, "
        "one pool Knight of the new element, Favonius Drill, Tempest "
        "Charge, Wind Wall, Eye of the Storm, Updraft; in the 'Unbound' rows "
        "Boreas Unbound is in play from turn 1 (not a card in the deck); in "
        "the 'Sworn' rows Sworn Brotherhood is in play from turn 1; in the "
        "'Rally' rows a Rally to the Banner is put in hand at the branch in "
        "every arm, and both SWITCH arms play it right after the new Knight "
        "(STAY's pilot plays it only if 3+ Oath sits outside Pyro). Both "
        "runs play focused Pyro, identically, up to turn T: the first turn "
        "in the window meeting the condition. On T, STAY keeps Pyro; SWITCH "
        "plays the new Knight first, then either holds the new element (hold) or "
        "goes back to focused Pyro from T+1 (back). "
        "The window is turns T, T+1, T+2. 'Fresh aura' = an enemy wearing a "
        "fresh aura at the start of the next turn (after auras tick): "
        "something for the next Anemo hit to Swirl.")
    argl = []
    for v in (DEF, "R3"):
        for to_el, (encs, lo, hi, _) in BRANCH_PAIRS.items():
            for mover in MOVERS:
                for eid in encs:
                    for i in range(seeds):
                        argl.append((to_el, mover, v, eid, seed0 + i))
    rows = [r for r in pmap(_w_branch, jobs, argl) if r is not None]
    by = defaultdict(list)
    for r in rows:
        by[(r["variant"], r["to"], r["mover"])].append(r)
        by[(r["variant"], r["to"], r["mover"], r["enc"])].append(r)
    out("\nEach cell is STAY / SWITCH (then hold the new element) / SWITCH "
        "(this turn only, then back to Pyro). 'loses less HP' is the share of paired states where "
        "that SWITCH arm lost less HP than STAY over the three turns.")
    out("\n| rules | pair | n | T | Pyro Oath at T | damage | Block | HP lost | "
        "SWITCH loses less HP / more (hold; back) | fresh aura at start "
        "of T+1 | ... T+2 | ... T+3 | fight won |")
    out("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    arms = ("stay", "switch", "switch_back")
    for v, (to_el, (encs, lo, hi, cond)) in [
            (v, kv) for v in (DEF, "R3") for kv in BRANCH_PAIRS.items()]:
        for mover in MOVERS:
            rs = by[(v, to_el, mover)]
            if not rs:
                continue

            def tri(key):
                return " / ".join(m(r[a][key] for r in rs) for a in arms)

            def fr(d):
                cells = []
                for a in arms:
                    v = [r[a]["fresh_next"][d] for r in rs
                         if r[a]["fresh_next"][d] is not None]
                    cells.append(pct(sum(1 for y in v if y > 0), len(v)))
                return " / ".join(cells)
            bw = []
            for a in ("switch", "switch_back"):
                better = sum(1 for r in rs
                             if r[a]["hp_lost"] < r["stay"]["hp_lost"])
                worse = sum(1 for r in rs
                            if r[a]["hp_lost"] > r["stay"]["hp_lost"])
                bw.append(f"{pct(better, len(rs))} / {pct(worse, len(rs))}")
            won = " / ".join(pct(sum(r[a]["won"] for r in rs), len(rs))
                             for a in arms)
            out(f"| {v} | Pyro -> {to_el}"
                f"{'' if mover == 'none' else ' + ' + mover} | "
                f"{len(rs)} | {m(r['stay']['T'] for r in rs)} | "
                f"{m(r['stay']['oath'] for r in rs)} | {tri('dmg')} | "
                f"{tri('block')} | {tri('hp_lost')} | {'; '.join(bw)} | "
                f"{fr(0)} | {fr(1)} | {fr(2)} | {won} |")
        out(f"  (condition for {to_el}: {cond}; window turns {lo}-{hi}; "
            f"encounters {', '.join(encs)})")
    out("\nBy encounter (R3b, no mover), STAY / SWITCH-hold / "
        "SWITCH-back:")
    for to_el, (encs, *_rest) in BRANCH_PAIRS.items():
        for eid in encs:
            rs = by[(DEF, to_el, "none", eid)]
            if not rs:
                out(f"- {to_el} / {eid}: no branch state reached")
                continue
            out(f"- {to_el} / {eid} (n={len(rs)}): damage " + " / ".join(
                m(r[a]["dmg"] for r in rs) for a in arms) + "; Block "
                + " / ".join(m(r[a]["block"] for r in rs) for a in arms)
                + "; HP lost " + " / ".join(
                    m(r[a]["hp_lost"] for r in rs) for a in arms))
    return by


def _w_svar_fight(args):
    enable()
    v, home, eid, seed = args
    from tier05 import acts
    from tier0.engine import varka_oath as O
    tier, spec = next((t, e) for t, e in _all_specs() if e["id"] == eid)
    enemies = acts.spawn(spec, random.Random(seed))
    n = len(enemies)
    r = oath_fight(O.starter(home), enemies, "focused", home, seed,
                   variant=v)
    return {"v": v, "home": home, "tier": tier, "n": n, "won": r["won"],
            "hp_lost": r["hp_lost"]}


def sec_svar(out, seeds, seed0, jobs):
    names = (DEF,) + tuple(SVARIANTS)
    out("\n## 6. Starter evenness: S-variants on R3b (focused pilot; n = "
        f"{seeds} runs per cell, seeds {seed0}..{seed0 + seeds - 1})")
    out("S1 = Barbara: Shining Miracle paints ONE enemy. S2 = Amber 5 Pyro, "
        "Lisa 3 Electro + draw 2, Kaeya 3 Cryo + 1 Vulnerable, each to ALL "
        "(Barbara as printed). S3 = Electro payout 3 to ALL. S4 = S1 + S3. "
        "S2+S3 is also run. Block test: S5 = S1 with 0 Block on Shining "
        "Miracle; S6 = S1 and the other three starter Knights +5 Block; S7 = "
        "S1 with Barbara at 5 Block and the other three +5 Block.")
    argl = [(seed0 + i, "focused", h, v, d) for v in names for h in ELEMENTS
            for d in (True, False) for i in range(seeds)]
    rows = pmap(_w_run, jobs, argl)
    by = defaultdict(list)
    for r, a in zip(rows, argl):
        by[(a[3], a[1 + 1], a[4])].append(r)
    fargs = [(v, h, e["id"], seed0 + i) for v in names for h in ELEMENTS
             for _, e in _all_specs() for i in range(seeds)]
    frows = pmap(_w_svar_fight, jobs, fargs)
    fb = defaultdict(list)
    for r in frows:
        fb[(r["v"], r["home"], _size(r["n"]))].append(r)
        if r["tier"] == "E":
            fb[(r["v"], r["home"], "elite")].append(r)
    out("\n| variant | start | act won, drafted (±95% CI) | act won, "
        "starter only | HP lost per drafted fight: 1 enemy / 3+ enemies | "
        "starter at full HP, HP lost: 1 enemy / 3+ / elites |")
    out("|---|---|---|---|---|---|")
    summary = []
    for v in names:
        wins = {}
        for h in ELEMENTS:
            rs = by[(v, h, True)]
            n = len(rs)
            k = sum(r["won"] for r in rs)
            wins[h] = 100 * k / n
            so = by[(v, h, False)]
            ks = sum(r["won"] for r in so)
            f1 = [f["hp_lost"] for r in rs for f in r["fights"]
                  if f["n_enemies"] == 1]
            f3 = [f["hp_lost"] for r in rs for f in r["fights"]
                  if f["n_enemies"] >= 3]
            out(f"| {v} | {h} | {pct(k, n)} ±{ci95(k, n):.1f} | "
                f"{pct(ks, len(so))} | {m(f1)} / {m(f3)} | "
                f"{m(r['hp_lost'] for r in fb[(v, h, '1 enemy')])} / "
                f"{m(r['hp_lost'] for r in fb[(v, h, '3+ enemies')])} / "
                f"{m(r['hp_lost'] for r in fb[(v, h, 'elite')])} |")
        lead = max(wins, key=wins.get)
        behind = [h for h in ELEMENTS if wins[lead] - wins[h] > 10]
        summary.append(
            f"- {v}: leader {lead} {wins[lead]:.1f}%, spread "
            f"{max(wins.values()) - min(wins.values()):.1f} points; more "
            f"than 10 behind the leader: {', '.join(behind) or 'none'}")
    out("")
    for s_ in summary:
        out(s_)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--only",
                    default="curve,turn1,runs,readers,starters,branch")
    args = ap.parse_args(argv)
    enable()
    lines = []

    def out(s=""):
        print(s)
        lines.append(s)
        sys.stdout.flush()

    only = args.only.split(",")
    out(f"# Varka Oath rework sim -- `python -m tools.varka_oath_report "
        f"--seeds {args.seeds} --seed {args.seed} --only {args.only}`")
    if "curve" in only:
        sec_curve(out, args.seeds, args.seed, args.jobs)
    if "turn1" in only:
        sec_turn1(out, args.seeds, args.seed)
    runs = None
    if "runs" in only or "readers" in only:
        runs = sec_runs(out, args.seeds, args.seed, args.jobs)
    if "readers" in only:
        sec_readers(out, runs, args.seeds, args.seed, args.jobs)
    if "starters" in only:
        sec_starters(out, args.seeds, args.seed, args.jobs)
    if "branch" in only:
        sec_branch(out, args.seeds, args.seed, args.jobs)
    if "svar" in only:
        sec_svar(out, args.seeds, args.seed, args.jobs)
    return lines


if __name__ == "__main__":
    main()
