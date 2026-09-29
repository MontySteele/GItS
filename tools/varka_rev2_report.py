#!/usr/bin/env python3
"""VARKA PAPER SIM, REVISION TWO -- the exploration report (not quotable).

    .venv/Scripts/python.exe -m tools.varka_rev2_report --fights 400 --seed 7

Answers sec.9.7 of `review/active/varka-paper-kit-2026-09-28.md` (branch
char4-paper-rev2), in order, with the arm `tier0.engine.varka_paper` switched
on for THIS PROCESS ONLY and every Varka built with `rev=2`. Revision one
stays runnable beside it (`tools/varka_paper_report.py`). Every cell is n
fights on seeds `seed + i`, the same seeds in every cell, so cells pair.

Driver-only encounters (never in the content tree; built here as Enemy
lists): MIXED3, a three-enemy pack with one multi-hitter, one heavy hitter
and one debuffer; MULTIHIT and HEAVY, a single boss of each intent profile
for the Wind-choice question.

Paper stage: under R215 B no number here is a balance claim.
"""

from __future__ import annotations

import argparse
import itertools
import statistics as st
import sys
from collections import Counter

from tools.varka_paper_report import (_enable_world, _set_kit_arms,
                                      _turn_damage, fmt, pct, q, run_other)

DECKS = {
    "A bare starter": [],
    "C2 +4 Knights +Windbound +Tempest": [
        "amber", "barbara", "lisa", "kaeya", "windbound_execution",
        "tempest_charge"],
    "FW2 Four Winds +Swirlers": [
        "amber", "barbara", "lisa", "kaeya", "windbound_execution",
        "windbound_execution", "favonius_cut", "wind_wall",
        "stormward_stance", "grand_masters_order", "tempest_charge",
        "gale_sweep"],
}
POLICIES = (("a", "absorb"), ("b", "swirl"), ("c", "smart"))
PACKS = ("swarm", "attrition", "mixed3")
BOSSES = ("tank_boss", "punisher")
WINDS = ("pyro", "hydro", "electro", "cryo")
PROFILE = {"swarm": "pack", "attrition": "pack", "mixed3": "pack",
           "tank_boss": "mixed boss (8 / buff / 4x3)",
           "punisher": "single heavy (9, ramping)",
           "multihit": "multi-hit (2x4)", "heavy": "single heavy (16)"}

# --- driver-only encounters -------------------------------------------------

CUSTOM = {
    "mixed3": [
        dict(name="slasher", hp=36, intents=[
            {"kind": "attack", "amount": 2, "times": 3}]),
        dict(name="brute", hp=48, intents=[
            {"kind": "attack", "amount": 10},
            {"kind": "block", "amount": 8}]),
        dict(name="hexer", hp=30, intents=[
            {"kind": "debuff", "power": "weak", "amount": 1},
            {"kind": "attack", "amount": 6}]),
    ],
    "multihit": [
        dict(name="flurry", hp=150, is_boss=True, intents=[
            {"kind": "attack", "amount": 2, "times": 4},
            {"kind": "attack", "amount": 2, "times": 4},
            {"kind": "buff", "power": "strength", "amount": 1}]),
    ],
    "heavy": [
        dict(name="crusher", hp=150, is_boss=True, intents=[
            {"kind": "attack", "amount": 16},
            {"kind": "block", "amount": 10},
            {"kind": "attack", "amount": 10}]),
    ],
}


def _stages(enc):
    from tier0.content import loader
    return [enc] if enc in CUSTOM else loader.encounter_stages(enc)


def _enemies(stage):
    import copy
    from tier0.content import loader
    from tier0.engine.state import Enemy
    if stage in CUSTOM:
        return [Enemy(hp=d["hp"], max_hp=d["hp"], name=d["name"],
                      intents=copy.deepcopy(d["intents"]),
                      is_boss=d.get("is_boss", False))
                for d in CUSTOM[stage]]
    return loader.build_encounter(stage)


# --- one cell ------------------------------------------------------------------

def run_v2(extra, enc, F, S, policy="smart", threshold=3, asc="A",
           fixed=None):
    from tier0.engine import combat, varka_paper
    from tier0.engine.varka_paper_pilot import VarkaPilot2
    pilot = VarkaPilot2(policy=policy, threshold=threshold)
    rows = []
    for i in range(F):
        carry, rec = None, None
        for stage in _stages(enc):
            player = varka_paper.build_player(extra, rev=2, asc_version=asc,
                                              fixed_winds=fixed)
            if carry is not None:
                player.hp = carry
            start = player.hp
            s = combat.run_fight(player, _enemies(stage), pilot, seed=S + i)
            vs = player.varka
            tdmg = _turn_damage(s.log)
            r = {"won": bool(s.player.alive) and not s.living_enemies,
                 "turns": s.turn, "hp_lost": start - max(0, s.player.hp),
                 "dmg": sum(tdmg), "absorbs": list(vs.absorbs),
                 "swirls": vs.swirls, "asc": list(vs.ascension),
                 "knights": list(vs.knight_hits), "recollect": vs.recollect,
                 "winds": dict(vs.winds), "wv": dict(vs.wind_value)}
            if rec is None:
                rec = r
            else:                               # gauntlet: merge
                rec["won"] = r["won"]
                for k in ("turns", "hp_lost", "dmg", "swirls", "recollect"):
                    rec[k] += r[k]
                for k in ("absorbs", "asc", "knights"):
                    rec[k] += r[k]
            carry = s.player.hp
            if not s.player.alive:
                break
        rows.append(rec)
    return rows


def score(r):
    """Outcome order for a paired comparison: a win beats a loss; between
    wins, less HP lost, then fewer turns; between losses, more damage
    dealt."""
    if r["won"]:
        return (1, -r["hp_lost"], -r["turns"])
    return (0, r["dmg"], 0)


def outcome(rows):
    n = len(rows)
    won = [r for r in rows if r["won"]]
    return (f"win {pct(len(won), n)}; turns(won) "
            f"{fmt([r['turns'] for r in won])}; hp lost "
            f"{fmt([r['hp_lost'] for r in rows])}")


def short(rows):
    n = len(rows)
    won = [r for r in rows if r["won"]]
    hp = [r["hp_lost"] for r in rows]
    tw = [r["turns"] for r in won]
    t = (f"{st.mean(tw):.1f}+/-{st.pstdev(tw):.1f} "
         f"[{q(tw, .1):.0f}/{q(tw, .5):.0f}/{q(tw, .9):.0f}]" if tw else "-")
    return (f"{100.0 * len(won) / n:.1f}% | {t} | "
            f"{st.mean(hp):.1f}+/-{st.pstdev(hp):.1f} "
            f"[{q(hp, .1):.0f}/{q(hp, .5):.0f}/{q(hp, .9):.0f}]")


def paired(xs, ys):
    """Share of seeds where x beats y, ties, loses (by `score`)."""
    b = sum(1 for x, y in zip(xs, ys) if score(x) > score(y))
    t = sum(1 for x, y in zip(xs, ys) if score(x) == score(y))
    return b, t, len(xs) - b - t


# --- the questions ----------------------------------------------------------------

def r1(F, S, out):
    out("\n## 1. Absorb vs Swirl: policies a (absorb whenever a new Wind), "
        "b (swirl only), c (smart); threshold 3, Ascension A")
    out("cell: win % | turns (won) mean+/-sd [p10/p50/p90] | HP lost "
        "mean+/-sd [p10/p50/p90] | absorbs/fight | swirls/fight | "
        "Winds at end")
    store = {}
    for deck in DECKS:
        out(f"\n### {deck}")
        for enc in PACKS + BOSSES:
            for tag, pol in POLICIES:
                rows = run_v2(DECKS[deck], enc, F, S, policy=pol)
                store[(deck, enc, tag)] = rows
                ab = [len(r["absorbs"]) for r in rows]
                sw = [r["swirls"] for r in rows]
                wn = [len(r["winds"]) for r in rows]
                out(f"- {enc:9s} {tag}: {short(rows)} | abs "
                    f"{st.mean(ab):.2f}+/-{st.pstdev(ab):.2f} | swirl "
                    f"{st.mean(sw):.2f}+/-{st.pstdev(sw):.2f} | winds "
                    f"{st.mean(wn):.2f}")
            a, b, c = (store[(deck, enc, t)] for t in "abc")
            for name, other in (("a", a), ("b", b)):
                w, t, l = paired(c, other)
                out(f"    paired c vs {name}: c better {pct(w, F)}, tie "
                    f"{pct(t, F)}, worse {pct(l, F)}")
            abs_c = sum(len(r["absorbs"]) for r in c)
            sw_c = sum(r["swirls"] for r in c)
            out(f"    c: {abs_c / F:.2f} Absorbs and {sw_c / F:.2f} Swirls "
                f"per fight ({pct(abs_c, abs_c + sw_c)} of its verbs are "
                f"Absorbs)")
        # dominance
        for x in "abc":
            for y in "abc":
                if x == y:
                    continue
                ge = all(
                    sum(r["won"] for r in store[(deck, e, y)])
                    >= sum(r["won"] for r in store[(deck, e, x)])
                    and st.mean(r["hp_lost"] for r in store[(deck, e, y)])
                    <= st.mean(r["hp_lost"] for r in store[(deck, e, x)])
                    for e in PACKS + BOSSES)
                if ge:
                    out(f"  DOMINANCE ({deck}): {x} is weakly dominated by "
                        f"{y} on every encounter (win and mean HP lost)")
    return store


def r2(F, S, out):
    out("\n## 2. Single-Wind runs: one Wind held from turn 1, no Absorb "
        "gains, swirl-only pilot (b), Ascension fired when drawn "
        "(threshold 0, so 'none' fires on the same schedule)")
    encs = PACKS + BOSSES + ("multihit", "heavy")
    for deck in ("C2 +4 Knights +Windbound +Tempest",
                 "FW2 Four Winds +Swirlers"):
        out(f"\n### {deck}")
        best = {}
        for enc in encs:
            cells = {"none": run_v2(DECKS[deck], enc, F, S, policy="swirl",
                                    threshold=0, fixed=())}
            for w in WINDS:
                cells[w] = run_v2(DECKS[deck], enc, F, S, policy="swirl",
                                  threshold=0, fixed=(w,))
            out(f"- {enc} ({PROFILE[enc]}):")
            for k, rows in cells.items():
                sw = [r["swirls"] for r in rows]
                out(f"    {k:8s} {short(rows)} | swirls "
                    f"{st.mean(sw):.2f}")
            ranked = sorted(WINDS, key=lambda w: (
                -sum(r["won"] for r in cells[w]),
                st.mean(r["hp_lost"] for r in cells[w]),
                st.mean(r["turns"] for r in cells[w])))
            best[enc] = ranked[0]
            # paired: best vs runner-up
            w, t, l = paired(cells[ranked[0]], cells[ranked[1]])
            out(f"    BEST {ranked[0]} (then {', '.join(ranked[1:])}); "
                f"paired best vs {ranked[1]}: better {pct(w, F)}, tie "
                f"{pct(t, F)}, worse {pct(l, F)}")
        out(f"  best Wind per encounter: " + ", ".join(
            f"{e} {best[e]}" for e in encs))
        out(f"  PASS (best differs by encounter): "
            f"{len(set(best.values())) > 1}")


def r3(F, S, out):
    out("\n## 3. Ascension A vs B x thresholds 1-4 (policy c), paired by "
        "seed")
    for deck in ("A bare starter", "C2 +4 Knights +Windbound +Tempest"):
        out(f"\n### {deck}")
        for enc in BOSSES + ("attrition", "mixed3", "swarm"):
            out(f"- {enc}")
            for ver in ("A", "B"):
                cells = {th: run_v2(DECKS[deck], enc, F, S, policy="smart",
                                    threshold=th, asc=ver)
                         for th in (1, 2, 3, 4)}
                for th, rows in cells.items():
                    reasons = Counter(a[3] for r in rows for a in r["asc"])
                    fires = [len(r["asc"]) for r in rows]
                    extra = ""
                    if ver == "B":
                        rc = [r["recollect"] for r in rows]
                        extra = (f" | re-collections/fight "
                                 f"{st.mean(rc):.2f}+/-{st.pstdev(rc):.2f}")
                    wat = [a[1] for r in rows for a in r["asc"]]
                    out(f"    {ver} th{th}: {short(rows)} | fires/fight "
                        f"{st.mean(fires):.2f} (threshold "
                        f"{reasons['threshold'] / F:.2f}, kill "
                        f"{reasons['kill'] / F:.2f}, prevent-lethal "
                        f"{reasons['prevent_lethal'] / F:.2f}) | Winds at "
                        f"fire {st.mean(wat) if wat else float('nan'):.2f}"
                        + extra)
                for early in (1, 2):
                    w, t, l = paired(cells[early], cells[4])
                    flag = "  <-- early wins > 1/4" if w > F / 4 else ""
                    pairs = list(zip(cells[early], cells[4]))
                    ew = sum(1 for x, y in pairs if x["won"] and not y["won"])
                    ww = sum(1 for x, y in pairs if y["won"] and not x["won"])
                    bl = sum(1 for x, y in pairs
                             if not x["won"] and not y["won"])
                    out(f"    {ver}: fire at {early} beats wait-for-4 in "
                        f"{pct(w, F)}, ties {pct(t, F)}, loses "
                        f"{pct(l, F)}{flag}; win flips early-only {ew}, "
                        f"wait-only {ww}; both lost {bl}")


def r4(store, F, out):
    out("\n## 4. Knight hits that reacted instead of painting (from the "
        "section 1 cells; revision one: 64-74% after an Absorb in packs)")
    for deck in ("C2 +4 Knights +Windbound +Tempest",
                 "FW2 Four Winds +Swirlers"):
        for enc in PACKS + ("tank_boss",):
            for tag, _ in POLICIES:
                rows = store[(deck, enc, tag)]
                hits = [h for r in rows for h in r["knights"]]
                after = [h for h in hits if h[1]]
                re_all = sum(1 for h in hits if h[3].startswith("reacted"))
                re_sp = sum(1 for h in hits if h[3] == "reacted_spent")
                re_af = sum(1 for h in after if h[3].startswith("reacted"))
                out(f"- {deck} / {enc} / {tag}: reacted {pct(re_all, len(hits))}"
                    f" (on a spent copy {pct(re_sp, len(hits))}); after an "
                    f"Absorb that turn {pct(re_af, len(after))}")


# --- section 9.4 scenarios -------------------------------------------------------

def _scenario_state(hp=40):
    import random
    from tier0.engine import reactions, varka_paper as V
    from tier0.engine.state import CombatState, Enemy
    en = [Enemy(hp=hp, max_hp=hp, name=n,
                intents=[{"kind": "attack", "amount": 5}]) for n in "ABC"]
    player = V.build_player(rev=2)
    vs = player.varka
    vs.winds = {"hydro": 0}
    state = CombatState(player=player, enemies=en, rng=random.Random(0))
    state.turn = 2
    player.draw_pile = [V.make_card("defend") for _ in range(5)]
    player.hand = [V.make_card(n) for n in
                   ("lisa", "windbound_execution", "tempest_charge",
                    "strike")]
    player.energy = 3
    a, b, c = en
    reactions.apply_aura(state, a, "pyro")          # the partner's, fresh
    reactions.apply_aura(state, b, "hydro")
    b.aura_spent = True                              # last turn's copy
    return state


def _play_line(line):
    """`line`: [(card name, target letter, fang?)]. Returns the outcome."""
    from tier0.engine import combat
    state = _scenario_state()
    p = state.player
    vs = p.varka
    by = {e.name: e for e in state.enemies}
    hp0 = {e.name: e.hp for e in state.enemies}
    for name, tgt, fang in line:
        card = next(c for c in p.hand if c.id in (f"varka_{name}", name))
        if p.energy < combat.card_cost(state, card):
            return None
        vs.playing, vs.aim, vs.fang_want = card, by[tgt], fang
        combat.play_card(state, card)
    a = by["A"]
    return {"dmg": {n: hp0[n] - by[n].hp for n in hp0},
            "total": sum(hp0[n] - by[n].hp for n in hp0),
            "block": p.block, "winds": sorted(vs.winds),
            "a_keeps_pyro": a.aura == "pyro" and not a.aura_spent,
            "auras": {n: (by[n].aura, "spent" if by[n].aura_spent
                          else "fresh") if by[n].aura else None
                      for n in hp0},
            "reactions": [e.get("reaction") for e in state.log
                          if e.get("event") == "reaction"],
            "hand": len(p.hand)}


def r5(out):
    out("\n## 5. Section 9.4's three lines, built exactly (A fresh Pyro, B "
        "spent Hydro, C clean, each 40 HP; Hydro Wind held; hand Lisa, "
        "Windbound, Tempest Charge, Strike; 3 Energy; Fang declined unless "
        "named)")
    lines = {
        "Line 1 (take and pay off)": [("windbound_execution", "A", False),
                                      ("lisa", "C", False),
                                      ("tempest_charge", "C", False)],
        "Line 2 (leave the partner's Pyro)": [("lisa", "C", False),
                                              ("windbound_execution", "C",
                                               False),
                                              ("strike", "B", False)],
        "Line 3 (the trap)": [("tempest_charge", "A", False),
                              ("lisa", "C", False),
                              ("windbound_execution", "B", False)],
    }
    for name, line in lines.items():
        o = _play_line(line)
        out(f"- {name}: damage {o['total']} (A {o['dmg']['A']}, B "
            f"{o['dmg']['B']}, C {o['dmg']['C']}); Block {o['block']}; "
            f"Winds {o['winds']}; partner Pyro on A survives: "
            f"{o['a_keeps_pyro']}; reactions {o['reactions']}; auras after "
            f"{o['auras']}; hand after {o['hand']}")
    # exhaustive search over every 3-card line of the 4 (targets x Fang)
    names = ("lisa", "windbound_execution", "tempest_charge", "strike")
    res = []
    for perm in itertools.permutations(names, 3):
        for tg in itertools.product("ABC", repeat=3):
            for fg in itertools.product((False, True), repeat=3):
                if any(f and n not in ("strike", "tempest_charge")
                       for n, f in zip(perm, fg)):
                    continue
                line = list(zip(perm, tg, fg))
                o = _play_line(line)
                if o:
                    res.append((line, o))
    out(f"  exhaustive: {len(res)} legal lines of 3 cards (order x target x "
        f"Fang)")

    def desc(line):
        return " > ".join(f"{n.split('_')[0]}->{t}{'(Fang)' if f else ''}"
                          for n, t, f in line)
    top = max(res, key=lambda t: (t[1]["total"], t[1]["block"]))
    out(f"  most damage: {top[1]['total']} dmg, {top[1]['block']} Block, "
        f"Winds {top[1]['winds']}, Pyro kept {top[1]['a_keeps_pyro']}: "
        f"{desc(top[0])}")
    kept = [t for t in res if t[1]["a_keeps_pyro"]]
    if kept:
        kt = max(kept, key=lambda t: (len(t[1]["winds"]), t[1]["total"]))
        out(f"  most Winds while A keeps its Pyro: {kt[1]['total']} dmg, "
            f"Winds {kt[1]['winds']}: {desc(kt[0])}")
        kd = max(kept, key=lambda t: (t[1]["total"], len(t[1]["winds"])))
        out(f"  most damage while A keeps its Pyro: {kd[1]['total']} dmg, "
            f"Winds {kd[1]['winds']}: {desc(kd[0])}")
    three = [t for t in res if len(t[1]["winds"]) >= 3]
    if three:
        t3 = max(three, key=lambda t: t[1]["total"])
        out(f"  most damage reaching 3 Winds: {t3[1]['total']} dmg, "
            f"Pyro kept {t3[1]['a_keeps_pyro']}: {desc(t3[0])}")
    # Pareto front on (damage, Winds, Pyro kept, Block)
    key = lambda o: (o["total"], len(o["winds"]), o["a_keeps_pyro"],  # noqa
                     o["block"])
    front = []
    for line, o in res:
        k = key(o)
        if not any(all(a >= b for a, b in zip(key(o2), k)) and key(o2) != k
                   for _, o2 in res):
            front.append((k, line))
    seen = set()
    out("  Pareto front (damage, Winds, Pyro kept, Block):")
    for k, line in sorted(front, reverse=True):
        if k in seen:
            continue
        seen.add(k)
        out(f"    {k}: {desc(line)}")
    trap_like = [t for t in res if t[0][0][0] == "tempest_charge"
                 and t[0][0][1] == "A"]
    best_trap = max(trap_like, key=lambda t: (t[1]["total"],
                                              len(t[1]["winds"])))
    out(f"  best line opening with the trap's Tempest on A: "
        f"{best_trap[1]['total']} dmg, Winds {best_trap[1]['winds']}: "
        f"{desc(best_trap[0])}")


def r6(F, S, out):
    out("\n## 6. Turns to kill beside the other kits (won fights), same "
        "seeds; Varka rev 2 = policy c, threshold 3, Ascension A")
    for enc in ("swarm", "attrition", "burst_check", "tank_boss", "punisher",
                "gauntlet"):
        out(f"\n{enc}")
        for label, deck in (("Varka r2 starter", "A bare starter"),
                            ("Varka r2 FW2", "FW2 Four Winds +Swirlers")):
            rows = run_v2(DECKS[deck], enc, F, S, policy="smart")
            out(f"  {label:18s} {outcome(rows)}")
        _set_kit_arms(True)
        try:
            for label, ch, pil in (("Klee (overhaul)", "klee", "demolition"),
                                   ("Kokomi (overhaul)", "kokomi", "priest"),
                                   ("Furina (Stage)", "furina", "salon"),
                                   ("Ironclad (ref)", "ref_ironclad",
                                    "generic"),
                                   ("Silent (ref)", "ref_silent", "silent")):
                try:
                    rows = run_other(ch, pil, enc, F, S)
                except Exception as exc:           # a kit the harness lacks
                    out(f"  {label:18s} unavailable: {exc!r}")
                    continue
                out(f"  {label:18s} {outcome(rows)}")
        finally:
            _set_kit_arms(False)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fights", type=int, default=400)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--only", default="123456")
    args = ap.parse_args(argv)
    _enable_world()
    lines = []

    def out(s=""):
        print(s)
        lines.append(s)
        sys.stdout.flush()

    F, S = args.fights, args.seed
    out(f"VARKA PAPER SIM, REVISION TWO (exploration; not quotable). "
        f"fights/cell {F}, seeds {S}..{S + F - 1}; SWIRL_PAYS and "
        f"CRYSTALLIZE_KEEPS_AURA on; HP 80 (placeholder)")
    store = None
    if "1" in args.only or "4" in args.only:
        store = r1(F, S, out) if "1" in args.only else r1(F, S, lambda s: 0)
    if "2" in args.only:
        r2(F, S, out)
    if "3" in args.only:
        r3(F, S, out)
    if "4" in args.only:
        r4(store, F, out)
    if "5" in args.only:
        r5(out)
    if "6" in args.only:
        r6(F, S, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
