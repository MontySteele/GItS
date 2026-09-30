#!/usr/bin/env python3
"""VARKA OATH, R4 -- the paper at HEAD (sec.3-6, batch two; exploration).

    .venv/Scripts/python.exe -m tools.varka_oath_r4 --seeds 400 --seed 7 --jobs 14

Answers sec.10's four "still to show" checks of
`review/active/varka-paper-kit-2026-09-28.md` (branch `varka-oath-paper`,
HEAD) on the 41-card pool with the 8-Block starter Knights, R3b Oath rules
(per card; Ascension's own hit gains none), Eye of the Storm Exhausting, and
BOTH Electro payouts: E-AoE (3 to ALL per Swirl) and E-Draw (draw 1 per
Swirl). The engine is `tier0.engine.varka_oath` built with `r4=True`, behind
the Varka paper arm's switch (off on disk). Instruments and pilots are the
ones `tools/varka_oath_report.py` documents; this module adds R4 drafting
(`F4_SCORE` / `J4_SCORE`), a stay/switch driver with the R4 movers, reader
ledgers for Favonian Standard and Dawn Wind's March, and pick/play rates for
the 18 new cards.

Draft rules (score, cap; skip under 3), R4:
  * focused (home E): each pool Knight of E 10 (cap 2), Favonian Standard 8,
    Oath of the Knights 8, Favonius Drill 8 (2), Dawn Wind's March 7,
    Knightly Guard 7 (2), Eye of the Storm 7 (2), Wall of Gales 7,
    Oathsworn Strike 6 (2), Jean 6, Tempest Charge 6 (2), Wind Wall 6 (2),
    Azure Devour 5, Crosswind 5 (2), Storm Surge 5, Northwind Avatar 5,
    Grand Master's Order / Stormward / Sworn / Tailwind Stride / Favonius Cut
    / Gale Sweep 5 (1), Unfurled Banner 4, Rising Gale 4, Squall / Updraft 4
    (2), Converging 3, Change of Guard 3, Tailwind Guard 2; off-element
    Knights 0.
  * juggling: every pool Knight 8 (cap 1), Boreas Unbound 8, Change of Guard
    7, Tailwind Guard 7, Rally 7, Sworn 7, Accord 6, Knightly Guard 6 (2),
    Jean 6, Favonius Drill 6 (2), Wind Wall 6 (2), Crosswind 5 (2), Storm
    Surge 5, Eye 4, Oath of the Knights 4, Oathsworn Strike 4, Northwind 4,
    Rising Gale 4, Azure 3, Unfurled 3, Favonian Standard 2, Dawn 2; the
    remaining Anemo Attacks as focused.
"""

from __future__ import annotations

import argparse
import random
import sys
from collections import defaultdict

from tools import varka_oath_report as R
from tools.varka_oath_report import (ELEMENTS, SIZES, TEMPLATE, _all_specs,
                                     _size, ci95, m, msd, pct, pmap)

V4 = {"E-AoE": dict(payout=True, apply_oath=True, per_card=True,
                    pay_electro=3, r4=True),
      "E-Draw": dict(payout=True, apply_oath=True, per_card=True,
                     electro_draw=True, r4=True)}
R.ALLVAR.update(V4)

F4_SCORE = {
    "favonian_standard": (8, 1), "oath_of_the_knights": (8, 1),
    "favonius_drill": (8, 2), "dawn_winds_march": (7, 1),
    "knightly_guard": (7, 2), "eye_of_the_storm_x": (7, 2),
    "wall_of_gales": (7, 1), "oathsworn_strike": (6, 2), "jean": (6, 1),
    "tempest_charge": (6, 2), "wind_wall": (6, 2), "azure_devour": (5, 1),
    "crosswind": (5, 2), "storm_surge": (5, 1), "northwind_avatar": (5, 1),
    "grand_masters_order": (5, 1), "stormward_stance": (5, 1),
    "sworn_brotherhood": (5, 1), "tailwind_stride": (5, 1),
    "favonius_cut": (5, 1), "gale_sweep": (5, 1), "unfurled_banner": (4, 1),
    "rising_gale": (4, 1), "squall": (4, 2), "updraft": (4, 2),
    "converging_winds": (3, 1), "change_of_guard": (3, 1),
    "tailwind_guard": (2, 1), "knights_roll_call": (1, 1),
    "rally_to_the_banner": (1, 1), "four_winds_accord": (0, 0),
    "boreas_unbound": (1, 1)}
J4_SCORE = dict(F4_SCORE, **{
    "boreas_unbound": (8, 1), "change_of_guard": (7, 1),
    "tailwind_guard": (7, 1), "rally_to_the_banner": (7, 1),
    "sworn_brotherhood": (7, 1), "four_winds_accord": (6, 1),
    "knightly_guard": (6, 2), "favonius_drill": (6, 2),
    "eye_of_the_storm_x": (4, 1), "oath_of_the_knights": (4, 1),
    "oathsworn_strike": (4, 2), "northwind_avatar": (4, 1),
    "azure_devour": (3, 1), "unfurled_banner": (3, 1),
    "favonian_standard": (2, 1), "dawn_winds_march": (2, 1),
    "knights_roll_call": (4, 1)})


def _score4(card, deck, policy, home):
    from tier0.engine import varka_oath as O
    el = next((e for e, ks in O.POOL_KNIGHTS4.items() if card in ks), None)
    if el is not None:
        if policy == "focused":
            s, cap = (10, 2) if el == home else (0, 0)
        else:
            s, cap = (8, 1)
    else:
        s, cap = (F4_SCORE if policy == "focused" else J4_SCORE).get(
            card, (0, 0))
    return 0 if deck.count(card) >= cap else s


def run_act1_r4(seed, policy, home, variant, draft=True):
    from tier0.engine import varka_oath as O
    from tier05 import acts
    enc_rng = random.Random(seed)
    draw = acts.ActDraw(enc_rng, act=0)
    offer_rng = random.Random(seed + 10 ** 6)
    deck = O.starter4(home)
    hp = max_hp = 80
    fights, offers = [], []
    for floor, kind in enumerate(TEMPLATE):
        if kind == "R":
            hp = min(max_hp, hp + int(0.3 * max_hp))
            continue
        spec = draw.encounter_for(kind, enc_rng)
        enemies = acts.spawn(spec, enc_rng)
        n_enemies = len(enemies)
        r = R.oath_fight(deck, enemies, policy, home, seed * 100 + floor,
                         hp=hp, variant=variant)
        r.update(kind=kind, enc=spec["id"], floor=floor, hp_in=hp,
                 n_enemies=n_enemies, deck=list(deck))
        fights.append(r)
        hp = r["hp_end"]
        if not r["won"]:
            break
        if kind != "B":
            offer = R._offer(offer_rng, kind, O.POOL4)
            if not draft:
                continue
            scored = sorted(((_score4(c, deck, policy, home), c)
                             for c in offer), reverse=True)
            pick = scored[0][1] if scored[0][0] >= 3 else None
            offers.append((tuple(offer), pick))
            if pick:
                deck.append(pick)
    won = bool(fights) and fights[-1]["kind"] == "B" and fights[-1]["won"]
    return {"seed": seed, "policy": policy, "home": home, "variant": variant,
            "draft": draft, "won": won, "fights": fights, "deck": deck,
            "offers": offers, "hp_lost": sum(f["hp_lost"] for f in fights)}


def _w_run4(args):
    R.enable()
    return run_act1_r4(*args)


def _w_starter4(args):
    from tier0.engine import varka_oath as O
    from tier05 import acts
    R.enable()
    v, home, eid, seed = args
    tier, spec = next((t, e) for t, e in _all_specs() if e["id"] == eid)
    enemies = acts.spawn(spec, random.Random(seed))
    n = len(enemies)
    r = R.oath_fight(O.starter4(home), enemies, "focused", home, seed,
                     variant=v)
    return {"v": v, "home": home, "tier": tier, "n": n, "won": r["won"],
            "hp_lost": r["hp_lost"]}


# --- 1. the starters, both Electro payouts ------------------------------------

def sec_starters(out, seeds, seed0, jobs):
    out(f"\n## R4-1. Electro and the starters (n = {seeds} runs per cell, "
        f"seeds {seed0}..{seed0 + seeds - 1}, paired)")
    argl = [(seed0 + i, pol, h, v, d) for v in V4
            for pol in ("focused", "juggling") for h in ELEMENTS
            for d in (True, False) for i in range(seeds)
            if d or pol == "focused"]
    rows = pmap(_w_run4, jobs, argl)
    by = defaultdict(list)
    for r in rows:
        by[(r["variant"], r["policy"], r["home"], r["draft"])].append(r)
    fargs = [(v, h, e["id"], seed0 + i) for v in V4 for h in ELEMENTS
             for _, e in _all_specs() for i in range(seeds)]
    fb = defaultdict(list)
    for r in pmap(_w_starter4, jobs, fargs):
        fb[(r["v"], r["home"], _size(r["n"]))].append(r)
        if r["tier"] == "E":
            fb[(r["v"], r["home"], "elite")].append(r)
    out("\n| Electro payout | pilot | start | act won (±95% CI) | starter "
        "only | HP lost per drafted fight: 1 enemy / 3+ | starter at full "
        "HP, HP lost: 1 enemy / 3+ / elites |")
    out("|---|---|---|---|---|---|---|")
    summary = []
    for v in V4:
        for pol in ("focused", "juggling"):
            wins = {}
            for h in ELEMENTS:
                rs = by[(v, pol, h, True)]
                n, k = len(rs), sum(r["won"] for r in rs)
                wins[h] = 100 * k / n
                so = by[(v, pol, h, False)]
                f1 = [f["hp_lost"] for r in rs for f in r["fights"]
                      if f["n_enemies"] == 1]
                f3 = [f["hp_lost"] for r in rs for f in r["fights"]
                      if f["n_enemies"] >= 3]
                sos = (pct(sum(r["won"] for r in so), len(so))
                       if so else "-")
                full = (f"{m(r['hp_lost'] for r in fb[(v, h, '1 enemy')])} / "
                        f"{m(r['hp_lost'] for r in fb[(v, h, '3+ enemies')])}"
                        f" / {m(r['hp_lost'] for r in fb[(v, h, 'elite')])}"
                        if pol == "focused" else "-")
                out(f"| {v} | {pol} | {h} | {pct(k, n)} ±{ci95(k, n):.1f} | "
                    f"{sos} | {m(f1)} / {m(f3)} | {full} |")
            lead = max(wins, key=wins.get)
            behind = [h for h in ELEMENTS if wins[lead] - wins[h] > 10]
            summary.append(
                f"- {v} / {pol}: leader {lead} {wins[lead]:.1f}%, spread "
                f"{max(wins.values()) - min(wins.values()):.1f} points; more "
                f"than 10 behind: {', '.join(behind) or 'none'}")
    out("")
    for s_ in summary:
        out(s_)
    return by


# --- 2. stay / switch with the R4 movers ------------------------------------------

MOVERS4 = ("none", "unbound", "change_of_guard", "tailwind_guard")


def branch_deck4(to_el):
    from tier0.engine import varka_oath as O
    return O.starter4("pyro") + ["amber", O.POOL_KNIGHTS4[to_el][0],
                                 "favonius_drill", "tempest_charge",
                                 "wind_wall", "eye_of_the_storm_x",
                                 "updraft"]


class BranchPilot4(R.BranchPilot):
    """R.BranchPilot with R4 movers: `inject` is put in hand at the branch
    in every arm (Change of Guard or Tailwind Guard). With Change of Guard
    the SWITCH-back arm returns to Pyro on T+1 by playing it (Block = Pyro
    Oath) instead of waiting for a Pyro Knight."""

    def __init__(self, to_el, mode, lo, hi, inject=None):
        super().__init__(to_el, mode, lo, hi)
        self.inject = inject
        self.injected = False
        self.cog_back_done = False

    def __call__(self, state):
        from tier0.engine import varka_oath as O
        from tier0.engine.combat import card_playable
        vs = state.player.varka
        t = state.turn
        if (self.T is not None and self.inject and not self.injected):
            self.injected = True
            state.player.hand.append(O.make_card(self.inject))
        if (self.inject == "change_of_guard" and self.back and self.T
                is not None and t == self.T + 1 and not self.cog_back_done
                and vs.current != "pyro"):
            self.cog_back_done = True
            c = next((c for c in state.player.hand
                      if c.id == "varka_change_of_guard"
                      and card_playable(state, c)), None)
            if c is not None and vs.oath.get("pyro", 0) > 0:
                vs.cog_choice = "pyro"
                vs.playing, vs.aim = c, None
                if t not in self.rows:
                    self.rows[t] = {"start_fresh": self._fresh(state),
                                    "hp": state.player.hp,
                                    "oath": O.current_oath(vs),
                                    "current": vs.current}
                return c
        return super().__call__(state)


def _w_branch4(args):
    from tier0.engine import combat, varka_oath as O
    from tier05 import acts
    R.enable()
    to_el, mover, v, eid, seed = args
    encs, lo, hi, _ = R.BRANCH_PAIRS[to_el]
    tier, spec = next((t, e) for t, e in _all_specs() if e["id"] == eid)
    res = {}
    for mode in ("stay", "switch", "switch_back"):
        enemies = acts.spawn(spec, random.Random(seed))
        player = O.build_player(branch_deck4(to_el), **R.ALLVAR[v])
        if mover == "unbound":
            player.varka.unbound = 1
        pilot = BranchPilot4(to_el, mode, lo, hi,
                             inject=mover if mover in (
                                 "change_of_guard", "tailwind_guard")
                             else None)
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
        res[mode] = {
            "T": T, "oath": pilot.rows[T]["oath"],
            "dmg": sum(r.get("amount", 0) for r in sl
                       if r.get("event") == "damage"),
            "block": sum(r.get("amount", 0) for r in sl
                         if r.get("event") == "block"),
            "hp_lost": hp0 - hp3,
            "won": bool(s.player.alive) and not s.living_enemies,
            "tg": sum(b for _, b in player.varka.tg_rows),
            "cog": len(player.varka.cog_rows)}
    return {"to": to_el, "mover": mover, "variant": v, "enc": eid,
            "stay": res["stay"], "switch": res["switch"],
            "switch_back": res["switch_back"]}


def sec_branch(out, seeds, seed0, jobs):
    out("\n## R4-2. STAY or SWITCH from one state, with the Switch cards "
        "(3 turns)")
    out("Deck: the R4 Pyro starter + Amber: Baron Bunny, the first pool "
        "Knight of the new element, Favonius Drill, Tempest Charge, Wind "
        "Wall, Eye of the Storm (Exhaust), Updraft. As before: focused Pyro "
        "to turn T; STAY / SWITCH-hold / SWITCH-back. 'unbound' = Boreas "
        "Unbound in play from turn 1. 'change_of_guard' / 'tailwind_guard' = "
        "that card put in hand at T in every arm; with Change of Guard the "
        "SWITCH-back arm returns to Pyro on T+1 by playing it; otherwise "
        "every arm's pilot may play it as a Block card.")
    argl = [(to, mv, v, eid, seed0 + i) for v in V4
            for to, (encs, *_r) in R.BRANCH_PAIRS.items()
            for mv in MOVERS4 for eid in encs for i in range(seeds)]
    rows = [r for r in pmap(_w_branch4, jobs, argl) if r is not None]
    by = defaultdict(list)
    for r in rows:
        by[(r["variant"], r["to"], r["mover"])].append(r)
    arms = ("stay", "switch", "switch_back")
    out("\n| Electro payout | pair | mover | n | damage | Block | HP lost | "
        "SWITCH-hold / SWITCH-back loses less HP than STAY | fight won |")
    out("|---|---|---|---|---|---|---|---|---|")
    for v in V4:
        for to in R.BRANCH_PAIRS:
            for mv in MOVERS4:
                rs = by[(v, to, mv)]
                if not rs:
                    continue

                def tri(key):
                    return " / ".join(m(r[a][key] for r in rs) for a in arms)
                bw = " / ".join(pct(sum(1 for r in rs if r[a]["hp_lost"]
                                        < r["stay"]["hp_lost"]), len(rs))
                                for a in ("switch", "switch_back"))
                won = " / ".join(pct(sum(r[a]["won"] for r in rs), len(rs))
                                 for a in arms)
                out(f"| {v} | Pyro -> {to} | {mv} | {len(rs)} | "
                    f"{tri('dmg')} | {tri('block')} | {tri('hp_lost')} | "
                    f"{bw} | {won} |")
    return by


# --- 3, 4, 5 from the drafted runs ------------------------------------------------------

def sec_asc(out, by):
    out("\n## R4-3. Ascension in the drafted runs: casts over 60 by turn 8")
    out("| Electro payout | pilot | start | fights | fights with a cast > 60 "
        "by t8 | mean cast t7-8 | max cast | where / what the decks carried |")
    out("|---|---|---|---|---|---|---|---|")
    for v in V4:
        for pol in ("focused", "juggling"):
            for h in ELEMENTS:
                fs = [f for r in by[(v, pol, h, True)] for f in r["fights"]]
                flag = [f for f in fs if any(
                    a["turn"] <= 8 and a["printed"] > 60 for a in f["asc"])]
                c78 = [a["printed"] for f in fs for a in f["asc"]
                       if 7 <= a["turn"] <= 8]
                mx = max((a["printed"] for f in fs for a in f["asc"]),
                         default=0)
                note = "-"
                if flag:
                    encs = defaultdict(int)
                    cards = defaultdict(float)
                    for f in flag:
                        encs[f["enc"]] += 1
                        for c in f["deck"][10:]:
                            cards[c] += 1 / len(flag)
                    top = sorted(cards.items(), key=lambda kv: -kv[1])[:4]
                    note = (", ".join(f"{k} {n}" for k, n in encs.items())
                            + "; " + ", ".join(f"{c} {x:.1f}"
                                               for c, x in top)
                            + f"; deck {m(len(f['deck']) for f in flag)}")
                out(f"| {v} | {pol} | {h} | {len(fs)} | {len(flag)} | "
                    f"{m(c78)} | {mx} | {note} |")


def sec_readers(out, by):
    out("\n## R4-4. Readers against Defend (5 Block for 1 Energy), from the "
        "drafted runs")
    out("Block per play for Eye of the Storm (Exhaust; 1 Energy); Block per "
        "fight it was in play for the Powers (Oath of the Knights 1 Energy, "
        "Favonian Standard 1, Dawn Wind's March 2).")
    out("| Electro payout | pilot | Eye per play (n) | OotK per fight (n) | "
        "Standard per fight (n) | Dawn's March per fight (n) |")
    out("|---|---|---|---|---|---|")
    for v in V4:
        for pol in ("focused", "juggling"):
            eyes, okn, std, dawn = [], [], [], []
            for h in ELEMENTS:
                for r in by[(v, pol, h, True)]:
                    for f in r["fights"]:
                        eyes += [x[1] for x in f["eye"]]
                        if f["okn"]:
                            okn.append(f["okn_block"])
                        if f.get("std_on"):
                            std.append(f["std_block"])
                        if f.get("dawn_on"):
                            dawn.append(f["dawn_block"])
            out(f"| {v} | {pol} | {m(eyes)} ({len(eyes)}) | {m(okn)} "
                f"({len(okn)}) | {m(std)} ({len(std)}) | {m(dawn)} "
                f"({len(dawn)}) |")


def sec_newcards(out, by):
    from tier0.engine import varka_oath as O
    out("\n## R4-5. The 18 new cards: pick and play rates (drafted runs, "
        "both payouts pooled)")
    out("Offered = times in a 3-card offer; picked = share of those offers "
        "that took it; plays per fight = plays in fights where the deck held "
        "it, per copy.")
    out("| card | focused: offered / picked / plays per fight | juggling: "
        "offered / picked / plays per fight |")
    out("|---|---|---|")
    for c in O.NEW4:
        cells = []
        for pol in ("focused", "juggling"):
            off = pk = 0
            plays, held = 0, 0
            for v in V4:
                for h in ELEMENTS:
                    for r in by[(v, pol, h, True)]:
                        for offer, pick in r["offers"]:
                            if c in offer:
                                off += 1
                                pk += pick == c
                        for f in r["fights"]:
                            n = f["deck"].count(c)
                            if n:
                                held += n
                                plays += f["plays"].get(f"varka_{c}", 0)
            cells.append(f"{off} / {pct(pk, off)} / "
                         f"{(plays / held) if held else 0:.2f}")
        out(f"| {c} | {cells[0]} | {cells[1]} |")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=400)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--jobs", type=int, default=14)
    ap.add_argument("--only", default="starters,branch")
    args = ap.parse_args(argv)
    R.enable()

    def out(s=""):
        print(s)
        sys.stdout.flush()

    out(f"# Varka Oath R4 -- `python -m tools.varka_oath_r4 --seeds "
        f"{args.seeds} --seed {args.seed} --only {args.only}`")
    only = args.only.split(",")
    if "starters" in only:
        by = sec_starters(out, args.seeds, args.seed, args.jobs)
        sec_asc(out, by)
        sec_readers(out, by)
        sec_newcards(out, by)
    if "branch" in only:
        sec_branch(out, args.seeds, args.seed, args.jobs)
    if "r5" in only:
        sec_r5(out, args.seeds, args.seed, args.jobs)



# ==========================================================================
#  R5: paper sec.10 Picks (pick 2 ruled; picks 3 and 4 as arms). E-AoE only.
# ==========================================================================

_R5_SWAP = {"lisa": "lisa_r5", "amber": "amber_r5"}
_R5_BASE = dict(V4["E-AoE"], swap=_R5_SWAP)
V5 = {
    "a": _R5_BASE,
    "a-Lisa4": dict(_R5_BASE, swap=dict(_R5_SWAP, lisa="lisa_r5_4")),
    "b": dict(_R5_BASE, std_amt=4, dawn_amt=3),
    "c": dict(_R5_BASE, swap=dict(_R5_SWAP,
                                  northwind_avatar="northwind_avatar_c")),
    "d": dict(_R5_BASE, std_amt=4, dawn_amt=3,
              swap=dict(_R5_SWAP, northwind_avatar="northwind_avatar_c")),
    "a-PyroAll": dict(_R5_BASE, pyro_all=True),
}
R.ALLVAR.update({f"R5{k}": v for k, v in V5.items()})


def sec_r5(out, seeds, seed0, jobs):
    out(f"\n## R5. Pick 2 ruled (Lisa, Baron Bunny); picks 3 and 4 as arms "
        f"(E-AoE; n = {seeds} runs per cell, seeds {seed0}.., paired)")
    out("a = pick 2 baseline; a-Lisa4 = Lisa at 4 per Attack; b = a + "
        "Favonian Standard 4, Dawn Wind's March 3; c = a + Northwind Avatar "
        "cost 2, 10/10 + 2 per Oath; d = b + c; a-PyroAll = a + the "
        "contingency Pyro payout (3 to every enemy wearing the Swirled "
        "element after the Swirl).")
    argl = [(seed0 + i, pol, h, f"R5{k}", True) for k in V5
            for pol in ("focused", "juggling") for h in ELEMENTS
            for i in range(seeds)]
    rows = pmap(_w_run4, jobs, argl)
    by = defaultdict(list)
    for r in rows:
        by[(r["variant"][2:], r["policy"], r["home"])].append(r)
    out("\n| arm | pilot | Pyro | Hydro | Electro | Cryo | spread | >10 "
        "behind the leader |")
    out("|---|---|---|---|---|---|---|---|")
    for k in V5:
        for pol in ("focused", "juggling"):
            w = {}
            cells = []
            for h in ELEMENTS:
                rs = by[(k, pol, h)]
                n, won = len(rs), sum(r["won"] for r in rs)
                w[h] = 100 * won / n
                cells.append(f"{w[h]:.1f} ±{ci95(won, n):.1f}")
            lead = max(w, key=w.get)
            behind = [h for h in ELEMENTS if w[lead] - w[h] > 10]
            out(f"| {k} | {pol} | " + " | ".join(cells)
                + f" | {max(w.values()) - min(w.values()):.1f} | "
                f"{', '.join(behind) or 'none'} |")

    def rates(k, pol, name, pid):
        off = pk = plays = held = 0
        for h in ELEMENTS:
            for r in by[(k, pol, h)]:
                for offer, pick in r["offers"]:
                    if name in offer:
                        off += 1
                        pk += pick == name
                for f in r["fights"]:
                    c = f["deck"].count(name)
                    if c:
                        held += c
                        plays += f["plays"].get(pid, 0)
        return (f"{pct(pk, off)} of {off} offers; "
                f"{(plays / held) if held else 0:.2f} plays per fight held")
    out("\n**Lisa and Baron Bunny (pick and play rates; arm a unless "
        "named)**")
    for pol in ("focused", "juggling"):
        out(f"- {pol}: Lisa {rates('a', pol, 'lisa', 'varka_lisa_r5')}; "
            f"Lisa at 4 {rates('a-Lisa4', pol, 'lisa', 'varka_lisa_r5_4')}; "
            f"Baron Bunny {rates('a', pol, 'amber', 'varka_amber_r5')}")
    for k, pid in (("a", 3), ("a-Lisa4", 4)):
        for pol in ("focused", "juggling"):
            lr = [x for h in ELEMENTS for r in by[(k, pol, h)]
                  for f in r["fights"] for x in f.get("lisa_rows", [])]
            out(f"- Lisa Block per play, {pid} per Attack, {pol}: "
                f"{m(x[2] for x in lr)} (Attacks before her "
                f"{m(x[1] for x in lr)}; n = {len(lr)})")
    out("\n**Readers under b (focused; Block per fight the Power was in "
        "play) against a**")
    for k in ("a", "b"):
        std = [f["std_block"] for h in ELEMENTS for r in by[(k, "focused", h)]
               for f in r["fights"] if f["std_on"]]
        dawn = [f["dawn_block"] for h in ELEMENTS
                for r in by[(k, "focused", h)] for f in r["fights"]
                if f["dawn_on"]]
        out(f"- {k}: Favonian Standard {m(std)} (n = {len(std)}); Dawn "
            f"Wind's March {m(dawn)} (n = {len(dawn)})")
    out("\n**Northwind Avatar** (focused / juggling):")
    for k, pid in (("a", "varka_northwind_avatar"),
                   ("c", "varka_northwind_avatar_c")):
        out(f"- {k}: " + " / ".join(
            rates(k, pol, "northwind_avatar", pid)
            for pol in ("focused", "juggling")))
    out("\n**Ascension: drafted fights with a cast over 60 by turn 8**")
    for k in V5:
        cells = []
        for pol in ("focused", "juggling"):
            fs = [f for h in ELEMENTS for r in by[(k, pol, h)]
                  for f in r["fights"]]
            fl = [f for f in fs if any(a["turn"] <= 8 and a["printed"] > 60
                                       for a in f["asc"])]
            mx = max((a["printed"] for f in fs for a in f["asc"]), default=0)
            cells.append(f"{pol} {len(fl)} of {len(fs)} (max {mx})")
        out(f"- {k}: " + "; ".join(cells))
    return by


if __name__ == "__main__":
    main()
