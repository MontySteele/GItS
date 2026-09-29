#!/usr/bin/env python3
"""VARKA PAPER SIM -- the exploration report (paper stage; not quotable).

    .venv/Scripts/python.exe -m tools.varka_paper_report --fights 300 --seed 7

Answers the seven questions of the character-4 Varka sim spec on the tier-0
battery encounters (`tier0/content/encounters`), with the arm
`tier0.engine.varka_paper` switched on for THIS PROCESS ONLY (with the element
port's `C.SWIRL_PAYS` / `C.CRYSTALLIZE_KEEPS_AURA`, and the companion arm so
Sturm und Drang reads). Every number is n fights on consecutive seeds
(`seed + i`), printed as mean, standard deviation and p10/p50/p90.

The comparison kits (Q7) are the current prototypes, their arms turned on the
way their own tests turn them on: Klee (`C.KLEE_OVERHAUL`, demolition pilot),
Kokomi (`C.KOKOMI_OVERHAUL`, priest pilot), Furina (`furina_stage.FURINA_STAGE`,
salon pilot), plus the reference Ironclad and Silent starters (generic and
silent pilots). Starters only, on the same encounters and seeds.

Paper stage: under R215 B no prototype number is a balance claim. This is the
answer to "do we understand the mechanical output", nothing more.
"""

from __future__ import annotations

import argparse
import statistics as st
import sys
from collections import Counter, defaultdict

DECKS = {
    "A bare starter": [],
    "B +2 Knights": ["amber", "barbara"],
    "C +4 Knights +Windbound": ["amber", "barbara", "lisa", "kaeya",
                                "windbound_execution"],
    "FW Four Winds deck": ["amber", "barbara", "lisa", "kaeya",
                           "windbound_execution", "windbound_execution",
                           "favonius_cut", "wind_wall", "stormward_stance",
                           "grand_masters_order"],
    "GALE deck": ["amber", "barbara", "lisa", "kaeya", "converging_winds",
                  "proto_mc_varka_sturm_und_drang", "gale_sweep",
                  "gale_sweep", "squall", "tempest_charge"],
}
PACKS = ("swarm", "attrition")
BOSSES = ("tank_boss", "punisher")
ALL_ENC = ("swarm", "attrition", "burst_check", "tank_boss", "punisher",
           "gauntlet")


def _enable_world():
    from tier0 import constants as C
    from tier0.engine import furina_stage, varka_paper
    varka_paper.enable()
    C.COMPANION_OVERHAUL = True


def _set_kit_arms(on: bool):
    from tier0 import constants as C
    from tier0.engine import furina_stage
    C.KLEE_OVERHAUL = on
    C.KOKOMI_OVERHAUL = on
    furina_stage.FURINA_STAGE = on


# --- stats ----------------------------------------------------------------

def q(xs, p):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    k = (len(xs) - 1) * p
    f = int(k)
    c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)


def fmt(xs, digits=1):
    if not xs:
        return "n=0"
    m = st.mean(xs)
    sd = st.pstdev(xs) if len(xs) > 1 else 0.0
    return (f"{m:.{digits}f} +/-{sd:.{digits}f} "
            f"[p10 {q(xs, .1):.{digits}f} p50 {q(xs, .5):.{digits}f} "
            f"p90 {q(xs, .9):.{digits}f}] n={len(xs)}")


def pct(k, n):
    return f"{100.0 * k / n:.1f}% ({k}/{n})" if n else "n=0"


# --- one fight -------------------------------------------------------------

def _turn_damage(log):
    per, cur = [], None
    for r in log:
        ev = r.get("event")
        if ev == "turn_open":
            per.append(0)
        elif ev == "damage" and per:
            per[-1] += r.get("amount", 0)
    return per


def run_varka(extra, encounter, fights, seed, threshold=3, aim="smart",
              gale=False, disabled=frozenset()):
    from tier0.content import loader
    from tier0.engine import combat, varka_paper
    from tier0.engine.varka_paper_pilot import VarkaPilot
    pilot = VarkaPilot(threshold=threshold, aim=aim, gale=gale)
    rows = []
    for i in range(fights):
        carry = None
        rec = None
        for stage in loader.encounter_stages(encounter):
            player = varka_paper.build_player(extra, disabled)
            if carry is not None:
                player.hp = carry
            start = player.hp
            s = combat.run_fight(player, loader.build_encounter(stage),
                                 pilot, seed=seed + i)
            vs = player.varka
            tdmg = _turn_damage(s.log)
            r = {"won": bool(s.player.alive) and not s.living_enemies,
                 "turns": s.turn, "hp_lost": start - max(0, s.player.hp),
                 "dmg": sum(tdmg), "turn_dmg": tdmg,
                 "winds": dict(vs.winds), "asc": list(vs.ascension),
                 "knights": list(vs.knight_hits),
                 "rows": list(vs.turn_rows), "wv": dict(vs.wind_value),
                 "absorbs": list(vs.absorbs), "swirls": vs.swirls,
                 "reactions": Counter(e.get("reaction") for e in s.log
                                      if e.get("event") == "reaction")}
            if rec is None:
                rec = r
            else:                       # gauntlet: merge the stages
                rec["won"] = r["won"]
                rec["turns"] += r["turns"]
                rec["hp_lost"] += r["hp_lost"]
                rec["dmg"] += r["dmg"]
                rec["turn_dmg"] += r["turn_dmg"]
            carry = s.player.hp
            if not s.player.alive:
                break
        rows.append(rec)
    return rows


def run_other(character, pilot_id, encounter, fights, seed):
    from tier0.content import loader
    from tier0.engine import combat
    from tier0.pilot.policy import make_pilot
    pilot = make_pilot(loader.pilot_weights(pilot_id))
    rows = []
    for i in range(fights):
        carry, rec = None, None
        for stage in loader.encounter_stages(encounter):
            player = loader.build_player(character)
            if carry is not None:
                player.hp = carry
            start = player.hp
            s = combat.run_fight(player, loader.build_encounter(stage),
                                 pilot, seed=seed + i)
            tdmg = _turn_damage(s.log)
            r = {"won": bool(s.player.alive) and not s.living_enemies,
                 "turns": s.turn, "hp_lost": start - max(0, s.player.hp),
                 "dmg": sum(tdmg), "turn_dmg": tdmg}
            if rec is None:
                rec = r
            else:
                rec["won"] = r["won"]
                for k in ("turns", "hp_lost", "dmg"):
                    rec[k] += r[k]
                rec["turn_dmg"] += r["turn_dmg"]
            carry = s.player.hp
            if not s.player.alive:
                break
        rows.append(rec)
    return rows


def outcome(rows):
    n = len(rows)
    won = [r for r in rows if r["won"]]
    return (f"win {pct(len(won), n)}; turns(won) {fmt([r['turns'] for r in won])}; "
            f"hp lost {fmt([r['hp_lost'] for r in rows])}")


# --- the questions -----------------------------------------------------------

def q1(F, S, out):
    out("\n## Q1. Wind collection: turn each Wind count is first reached")
    out("(turn of the fight the k-th Wind arrived; 'reached' = share of fights "
        "that got there before the fight ended)")
    for deck in ("A bare starter", "B +2 Knights", "C +4 Knights +Windbound"):
        for enc in PACKS + BOSSES:
            rows = run_varka(DECKS[deck], enc, F, S)
            out(f"\n{deck} / {enc}: fight length {fmt([r['turns'] for r in rows])}")
            for k in (1, 2, 3, 4):
                ts = []
                for r in rows:
                    turns = sorted(r["winds"].values())
                    if len(turns) >= k:
                        ts.append(turns[k - 1])
                out(f"  {k} Wind(s): reached {pct(len(ts), len(rows))}; "
                    f"turn {fmt(ts)}")
            first = Counter()
            for r in rows:
                for el, t in r["winds"].items():
                    first[el] += 1
            out("  Winds gained (fights): " + ", ".join(
                f"{el} {first[el]}" for el in ("pyro", "hydro", "electro",
                                               "cryo")))


def q2(F, S, out):
    out("\n## Q2. Ascension timing (threshold = Winds held before firing; "
        "every policy also fires when the estimate kills)")
    for deck in ("A bare starter", "C +4 Knights +Windbound",
                 "FW Four Winds deck"):
        for enc in ("tank_boss", "punisher", "attrition", "swarm"):
            out(f"\n{deck} / {enc}")
            res = {}
            for th in (1, 2, 3, 4):
                rows = run_varka(DECKS[deck], enc, F, S, threshold=th)
                res[th] = rows
                fired = [r["asc"][0] for r in rows if r["asc"]]
                out(f"  fire at {th}: fired {pct(len(fired), len(rows))}; "
                    f"Asc dmg {fmt([a[2] for a in fired])}; "
                    f"winds at fire {fmt([a[1] for a in fired], 2)}; "
                    f"fire turn {fmt([a[0] for a in fired])}")
                out(f"      {outcome(rows)}")
            # paired, same seeds: wait (3) vs early (2)
            e, w = res[2], res[3]
            dt = [b["turns"] - a["turns"] for a, b in zip(e, w)
                  if a["won"] and b["won"]]
            dh = [b["hp_lost"] - a["hp_lost"] for a, b in zip(e, w)]
            better = sum(1 for x in dh if x < 0)
            worse = sum(1 for x in dh if x > 0)
            flips = sum(1 for a, b in zip(e, w) if a["won"] != b["won"])
            out(f"  PAIRED wait(3) - early(2): turns {fmt(dt, 2)}; "
                f"hp lost {fmt(dh, 2)}; wait lost less HP in "
                f"{pct(better, len(dh))}, more in {pct(worse, len(dh))}; "
                f"win/loss flips {flips}")


def q3(F, S, out):
    out("\n## Q3. What each Wind is worth (direct tallies, and paired "
        "ablation: the Wind still counts for Ascension but does nothing)")
    for deck in ("C +4 Knights +Windbound", "FW Four Winds deck"):
        for enc in ("tank_boss", "attrition", "swarm"):
            base = run_varka(DECKS[deck], enc, F, S)
            out(f"\n{deck} / {enc}: all Winds live -> {outcome(base)}; "
                f"dmg/fight {fmt([r['dmg'] for r in base])}")
            wv = defaultdict(list)
            for r in base:
                for k, v in r["wv"].items():
                    wv[k].append(v)
            out(f"  tallies per fight: Pyro +2 on {fmt(wv['pyro_hits'])} hits "
                f"(= {st.mean(wv['pyro_hits']) * 2:.1f} dmg before mods); "
                f"Hydro Block {fmt(wv['hydro_block'])}; Electro cards "
                f"{fmt(wv['electro_draws'], 2)}; Cryo Weak stacks "
                f"{fmt(wv['cryo_weak'], 2)}")
            for el in ("pyro", "hydro", "electro", "cryo"):
                abl = run_varka(DECKS[deck], enc, F, S, disabled={el})
                dturn = [a["turns"] - b["turns"] for a, b in zip(abl, base)
                         if a["won"] and b["won"]]
                dhp = [a["hp_lost"] - b["hp_lost"] for a, b in zip(abl, base)]
                held = sum(1 for r in base if el in r["winds"])
                wr = (sum(r["won"] for r in abl) - sum(r["won"] for r in base))
                out(f"  without {el:7s} (held in {pct(held, len(base))}): "
                    f"+turns {fmt(dturn, 2)}; +hp lost {fmt(dhp, 2)}; "
                    f"wins {wr:+d}")


def q4(F, S, out):
    out("\n## Q4. Four Winds deck vs Gale deck (same seeds)")
    for enc in PACKS + BOSSES:
        for deck, gale in (("FW Four Winds deck", False),
                           ("GALE deck", True)):
            rows = run_varka(DECKS[deck], enc, F, S, gale=gale)
            mx = [max(r["turn_dmg"] or [0]) for r in rows]
            allturns = [d for r in rows for d in r["turn_dmg"]]
            rc = Counter()
            for r in rows:
                rc.update(r["reactions"])
            out(f"\n{deck} / {enc}: {outcome(rows)}")
            out(f"  dmg/fight {fmt([r['dmg'] for r in rows])}; "
                f"max single-turn dmg per fight {fmt(mx)}; "
                f"highest turn seen {max(mx)}; turns >= 50 dmg: "
                f"{sum(1 for d in allturns if d >= 50)}/{len(allturns)}")
            out(f"  swirls/fight {fmt([r['swirls'] for r in rows])}; "
                f"absorbs/fight {fmt([len(r['absorbs']) for r in rows])}; "
                f"reactions/fight: " + ", ".join(
                    f"{k} {v / len(rows):.2f}" for k, v in rc.most_common()))


def q5(F, S, out):
    out("\n## Q5. 'Strike deck' turns: opening hand holds no Knight/Muster "
        "and no enemy wears a fresh aura")
    for deck in ("A bare starter", "B +2 Knights", "C +4 Knights +Windbound",
                 "FW Four Winds deck"):
        for enc in ("tank_boss", "attrition"):
            rows = run_varka(DECKS[deck], enc, F, S)
            allrows = [t for r in rows for t in r["rows"]]
            k = sum(t["strike_turn"] for t in allrows)
            byturn = []
            for tn in (1, 2, 3, 4, 5):
                sub = [t for t in allrows if t["turn"] == tn]
                byturn.append(f"t{tn} {100.0 * sum(t['strike_turn'] for t in sub) / max(1, len(sub)):.0f}%")
            zero_w = [sum(1 for t in r["rows"] if t["winds"] == 0)
                      for r in rows]
            out(f"{deck} / {enc}: strike turns {pct(k, len(allrows))}; "
                + ", ".join(byturn)
                + f"; turns spent with 0 Winds per fight {fmt(zero_w)}")


def q6(F, S, out):
    out("\n## Q6. Knight plays: paint or react? (smart aim paints a clean "
        "enemy; naive aim is the engine's lowest-HP default)")
    for deck in ("C +4 Knights +Windbound", "FW Four Winds deck"):
        for enc in ("swarm", "attrition", "tank_boss"):
            for aim in ("smart", "naive"):
                rows = run_varka(DECKS[deck], enc, F, S, aim=aim)
                hits = [h for r in rows for h in r["knights"]]
                after = [h for h in hits if h[1]]
                c_all = Counter(h[3] for h in hits)
                c_aft = Counter(h[3] for h in after)
                wasted = sum(1 for h in hits if h[3].startswith("reacted")
                             and not h[4])
                out(f"{deck} / {enc} / {aim}: {outcome(rows)}")
                out(f"   all Knight hits {len(hits)}: " + ", ".join(
                    f"{k} {pct(v, len(hits))}" for k, v in c_all.most_common()))
                out(f"   after an Absorb that turn {len(after)}: " + ", ".join(
                    f"{k} {pct(v, len(after))}" for k, v in c_aft.most_common()))
                out(f"   wasted paints (reacted while that Wind was not yet "
                    f"held): {wasted} = {wasted / len(rows):.2f}/fight")


def q7(F, S, out):
    out("\n## Q7. Turns to kill, starters on the battery (won fights), "
        "same seeds")
    rows_out = []
    for enc in ALL_ENC:
        out(f"\n{enc}")
        for label, extra in (("Varka starter", DECKS["A bare starter"]),
                             ("Varka FW deck", DECKS["FW Four Winds deck"])):
            rows = run_varka(extra, enc, F, S)
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
                except Exception as exc:          # a kit the harness lacks
                    out(f"  {label:18s} unavailable: {exc!r}")
                    continue
                out(f"  {label:18s} {outcome(rows)}")
        finally:
            _set_kit_arms(False)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fights", type=int, default=300)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--only", default="1234567")
    args = ap.parse_args(argv)
    _enable_world()
    lines = []

    def out(s=""):
        print(s)
        lines.append(s)
        sys.stdout.flush()

    out(f"VARKA PAPER SIM (exploration; not quotable). fights/cell "
        f"{args.fights}, seeds {args.seed}..{args.seed + args.fights - 1}; "
        f"SWIRL_PAYS and CRYSTALLIZE_KEEPS_AURA on; HP 80 (placeholder)")
    for k, fn in (("1", q1), ("2", q2), ("3", q3), ("4", q4), ("5", q5),
                  ("6", q6), ("7", q7)):
        if k in args.only:
            fn(args.fights, args.seed, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
