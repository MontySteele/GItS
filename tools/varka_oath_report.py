#!/usr/bin/env python3
"""VARKA OATH REWORK -- the paper-stage sim report (exploration, not quotable).

    .venv/Scripts/python.exe -m tools.varka_oath_report --seeds 200 --seed 7 --jobs 8

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
  * ELITES -- the three act-1 elites at full HP with starter decks only,
    the Oath starter (each Knight), the batch-one starter (sec.10 as built,
    through the revision-2.1 arm: the Fang as the fork, 2.2's pilot, Muster
    0, Ascension 1, Winds as built with Electro = 1 Energy) and the reference
    Ironclad and Silent starters (their repo pilots).

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
VARIANTS = {"V0": dict(payout=True, apply_oath=True),
            "V1": dict(payout=False, apply_oath=True),
            "V2": dict(payout=True, apply_oath=False)}
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

def oath_fight(deck, enemies, policy, home, seed, hp=None, variant="V0"):
    from tier0.engine import combat, varka_oath as O
    from tier0.engine.varka_oath_pilot import VarkaOathPilot
    player = O.build_player(deck, hp=hp, **VARIANTS[variant])
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


def b1_player(extra, hp=None):
    from tier0.engine import varka_paper as V
    p = V.build_player(extra, rev=2, fork=True, winds_set="B1",
                       muster_cost=0)
    for c in p.draw_pile:
        if c.id == "varka_four_winds_ascension":
            c.cost = 1
    if hp is not None:
        p.hp = hp
    return p


def b1_fight(extra, enemies, seed, hp=None):
    from tier0.engine import combat
    from tier0.engine.varka_paper_pilot import VarkaPilot2
    player = b1_player(extra, hp)
    start = player.hp
    s = combat.run_fight(player, enemies,
                         VarkaPilot2(policy="smart", threshold=3,
                                     smart_rule="v22"), seed=seed)
    return {"won": bool(s.player.alive) and not s.living_enemies,
            "turns": s.turn, "hp_lost": start - max(0, s.player.hp),
            "hp_end": max(0, s.player.hp)}


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
# The batch-one arm drafts from the cards the revision-2 arm models.
B1_SCORE = {"amber": (8, 2), "barbara": (8, 2), "lisa": (8, 2),
            "kaeya": (8, 2), "windbound_execution": (7, 2),
            "tempest_charge": (6, 2), "wind_wall": (6, 2),
            "favonius_cut": (5, 1), "gale_sweep": (4, 1), "squall": (4, 2),
            "grand_masters_order": (4, 1), "stormward_stance": (4, 1),
            "converging_winds": (3, 1)}
B1_POOL = {"common": ["windbound_execution", "squall", "gale_sweep",
                      "wind_wall", "amber", "barbara", "lisa", "kaeya"],
           "uncommon": ["tempest_charge", "favonius_cut",
                        "grand_masters_order", "stormward_stance"],
           "rare": ["converging_winds"]}


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
    if policy == "b1":
        s, cap = B1_SCORE.get(card, (0, 0))
    elif card in knight_el:
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


def run_act1(seed, policy, home, variant="V0", draft=True):
    """One stylised act 1. policy in focused / juggling / b1 / ref_*.
    `draft=False` keeps the starter all act (the reference kits always do:
    the calibration rows)."""
    from tier0.engine import varka_oath as O
    from tier05 import acts
    enc_rng = random.Random(seed)
    draw = acts.ActDraw(enc_rng, act=0)
    offer_rng = random.Random(seed + 10 ** 6)
    if policy == "b1":
        deck = []                              # extras on the b1 starter
        pool = B1_POOL
    elif policy in REFS:
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
        if policy == "b1":
            r = b1_fight(deck, enemies, fseed, hp=hp)
        elif policy in REFS:
            ch, pil, _ = REFS[policy]
            r = ref_fight(ch, pil, enemies, fseed, hp=hp)
        else:
            r = oath_fight(deck, enemies, policy, home, fseed, hp=hp,
                           variant=variant)
        r.update(kind=kind, enc=spec["id"], floor=floor, hp_in=hp,
                 deck_size=len(deck))
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


def _w_elite(args):
    from tier05 import acts
    enable()
    arm, eid, seed = args
    spec = next(e for e in acts.pools(0)["elite"] if e["id"] == eid)
    enemies = acts.spawn(spec, random.Random(seed))
    if arm.startswith("oath_"):
        home = arm[5:]
        from tier0.engine import varka_oath as O
        r = oath_fight(O.starter(home), enemies, "focused", home, seed)
    elif arm == "batch_one":
        r = b1_fight([], enemies, seed)
    elif arm == "ironclad":
        r = ref_fight("ref_ironclad", "generic", enemies, seed)
    elif arm == "silent":
        r = ref_fight("ref_silent", "silent", enemies, seed)
    r.update(arm=arm, elite=eid, seed=seed)
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
                for v in ("V0", "V1", "V2"):
                    if v != "V0" and deck not in ("F", "J"):
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
        for v in ("V0", "V1", "V2"):
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
    out("\n## 1b. Turn one with Barbara: Shining Miracle "
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
            player = O.build_player(O.starter("hydro"))
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
        argl.append((seed0 + i, "b1", "none", "V0"))
        # calibration rows: starters kept all act, no drafting
        argl.append((seed0 + i, "b1", "none", "V0", False))
        argl.append((seed0 + i, "ref_ironclad", "none", "V0", False))
        argl.append((seed0 + i, "ref_silent", "none", "V0", False))
        for home in ELEMENTS:
            argl.append((seed0 + i, "focused", home, "V0", False))
    rows = pmap(_w_run, jobs, argl)
    by = defaultdict(list)
    for r in rows:
        by[(r["variant"], r["policy"], r["home"])].append(r)
    out("\ncell: act won % (±95% CI) | HP lost over the act (all runs) | "
        "HP lost per won fight | died on floor (mean) | deck size at end")
    for v in VARIANTS:
        out(f"\n### Variant {v}")
        out("| policy | start | act won | HP lost (act) | HP lost, elite 1 |"
            " HP lost, both elites | boss won when reached |")
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
    rs = by[("V0", "b1", "none")]
    n = len(rs)
    k = sum(r["won"] for r in rs)
    e1 = [next((f["hp_lost"] for f in r["fights"] if f["kind"] == "E"),
               None) for r in rs]
    e1 = [x for x in e1 if x is not None]
    ea = [f["hp_lost"] for r in rs for f in r["fights"] if f["kind"] == "E"]
    out(f"\nBatch one (sec.10 as built, revision-2 arm, subset pool): act "
        f"won {pct(k, n)} ±{ci95(k, n):.1f}; HP lost {msd(r['hp_lost'] for r in rs)};"
        f" elite 1 {msd(e1)}; both elites {msd(ea)} (n={len(ea)})")
    out("\n**Calibration: the same act with the starter kept all act "
        "(no drafting).**")
    out("| arm | act won | HP lost (act) | HP lost, elite 1 | "
        "died at elite 1 |")
    out("|---|---|---|---|---|")
    for pol, home in ([("focused", h) for h in ELEMENTS]
                      + [("b1", "none"), ("ref_ironclad", "none"),
                         ("ref_silent", "none")]):
        rs = by[("S", pol, home)]
        n = len(rs)
        k = sum(r["won"] for r in rs)
        e1 = [next((f["hp_lost"] for f in r["fights"] if f["kind"] == "E"),
                   None) for r in rs]
        e1 = [x for x in e1 if x is not None]
        d1 = sum(1 for r in rs if not r["won"]
                 and r["fights"][-1]["kind"] == "E"
                 and sum(f["kind"] == "E" for f in r["fights"]) == 1)
        label = {"focused": f"Oath starter, {home}",
                 "b1": "batch-one starter"}.get(pol, pol)
        out(f"| {label} | {pct(k, n)} ±{ci95(k, n):.1f} | "
            f"{msd(r['hp_lost'] for r in rs)} | {msd(e1)} | {pct(d1, n)} |")
    out("\n**Ascension in the drafted runs (V0 and V2), every cast in every "
        "fight: mean printed damage (6 + 3 x Oath) by the turn cast, "
        "casts over 60, and the largest.**")
    out("| variant | policy | start | t1-2 | t3-4 | t5-6 | t7-8 | t9-12 | "
        "t13+ | casts / fight | casts > 60 by t8 | max |")
    out("|---|---|---|---|---|---|---|---|---|---|---|---|")
    buckets = ((1, 2), (3, 4), (5, 6), (7, 8), (9, 12), (13, 99))
    for v in ("V0", "V2"):
        for pol in ("focused", "juggling"):
            for home in ELEMENTS:
                rs = by[(v, pol, home)]
                casts = [a for r in rs for f in r["fights"] for a in f["asc"]]
                nf = sum(len(r["fights"]) for r in rs)
                cells = [m(a["printed"] for a in casts
                           if lo <= a["turn"] <= hi) for lo, hi in buckets]
                over = sum(1 for a in casts if a["turn"] <= 8
                           and a["printed"] > 60)
                mx = max((a["printed"] for a in casts), default=0)
                out(f"| {v} | {pol} | {home} | " + " | ".join(cells)
                    + f" | {len(casts) / max(1, nf):.2f} | {over} | {mx} |")
    # where runs die
    out("\nDeaths by floor kind (V0): " + "; ".join(
        f"{pol}/{home}: " + ", ".join(
            f"{kd} {sum(1 for r in by[('V0', pol, home)] if not r['won'] and r['fights'][-1]['kind'] == kd)}"
            for kd in ("N", "E", "B"))
        for pol in ("focused", "juggling") for home in ELEMENTS))
    return by


def sec_readers(out, runs, seeds, seed0, jobs):
    out("\n## 3. Oath readers against Defend: Block per Energy")
    out("From the act-1 runs (V0), every play of the card; Defend is 5 per "
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
                for r in runs[("V0", pol, h)]:
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
    out("\nGranted decks (V0) on the act-1 elites and bosses at full HP, "
        f"n = {seeds} per deck, start and fight (5 fights). F = focused "
        "build, J = juggling build; 'J / focused' plays the juggling build "
        "without switching (it holds the off-element Knights), which splits "
        "the deck's cost from the switching's cost:")
    argl = []
    from tier05 import acts
    specs = acts.pools(0)["elite"] + acts.boss_pool(0)
    for home in ELEMENTS:
        for deck, pol in (("F", "focused"), ("J", "focused"),
                          ("J", "juggling")):
            for spec in specs:
                for i in range(seeds):
                    argl.append((deck, home, pol, spec["id"], seed0 + i))
    rows = pmap(_w_granted, jobs, argl)
    by = defaultdict(list)
    for r in rows:
        by[(r["deck"], r["policy"], r["home"])].append(r)
        by[(r["deck"], r["policy"], "all")].append(r)
    out("| deck / policy / start | Eye Block per play | OotK Block per "
        "fight (per turn up) | Defend | fights won | HP lost | switches "
        "per fight | Swirls per fight |")
    out("|---|---|---|---|---|---|---|---|")
    for home in ELEMENTS + ("all",):
        for dk, pol in (("F", "focused"), ("J", "focused"),
                        ("J", "juggling")):
            rs = by[(dk, pol, home)]
            eyes = [x[1] for r in rs for x in r["eye"]]
            okn = [r["okn_block"] for r in rs if r["okn"]]
            oknt = [x[1] for r in rs for x in r["okn_rows"]]
            out(f"| {dk} / {pol} / {home} | {m(eyes)} (n={len(eyes)}) | "
                f"{m(okn)} ({m(oknt)}) (n={len(okn)}) | 5 | "
                f"{pct(sum(r['won'] for r in rs), len(rs))} | "
                f"{msd(r['hp_lost'] for r in rs)} | "
                f"{m((r['switches'] for r in rs), 2)} | "
                f"{m((r['swirls'] for r in rs), 2)} |")
    return by


def _w_granted(args):
    from tier05 import acts
    enable()
    deck, home, pol, eid, seed = args
    specs = acts.pools(0)["elite"] + acts.boss_pool(0)
    spec = next(e for e in specs if e["id"] == eid)
    enemies = acts.spawn(spec, random.Random(seed))
    r = oath_fight(deck_for(deck, home), enemies, pol, home, seed)
    r.update(deck=deck, home=home, policy=pol, enc=eid)
    return r


def sec_elites(out, runs, seeds, seed0, jobs):
    from tier05 import acts
    out("\n## 4. Act-1 elites: HP lost at full HP with starter decks "
        f"(n = {seeds} per arm and elite, seeds {seed0}..)")
    arms = ["oath_" + e for e in ELEMENTS] + ["batch_one", "ironclad",
                                              "silent"]
    eids = [e["id"] for e in acts.pools(0)["elite"]]
    argl = [(a, e, seed0 + i) for a in arms for e in eids
            for i in range(seeds)]
    rows = pmap(_w_elite, jobs, argl)
    by = defaultdict(list)
    for r in rows:
        by[(r["arm"], r["elite"])].append(r)
    out("| arm | " + " | ".join(f"{e}: win / HP lost" for e in eids)
        + " | mean HP lost |")
    out("|---" * (len(eids) + 2) + "|")
    for a in arms:
        cells, allhp = [], []
        for e in eids:
            rs = by[(a, e)]
            allhp += [r["hp_lost"] for r in rs]
            cells.append(f"{pct(sum(r['won'] for r in rs), len(rs))} / "
                         f"{msd(r['hp_lost'] for r in rs)}")
        out(f"| {a} | " + " | ".join(cells) + f" | {m(allhp)} |")
    out("(Ironclad starts at 80 HP and Silent at 70; HP lost counts to "
        "death, so a loss is the whole of the HP carried in.)")
    return by


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--only", default="curve,turn1,runs,readers,elites")
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
    if "elites" in only:
        sec_elites(out, runs, args.seeds, args.seed, args.jobs)
    return lines


if __name__ == "__main__":
    main()
