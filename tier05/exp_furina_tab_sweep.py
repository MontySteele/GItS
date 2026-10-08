"""Furina, the Salon's Tab: a tier 0.5 sweep ahead of [USER]'s first play.

    .venv/Scripts/python.exe -m tier05.exp_furina_tab_sweep --runs 1000 --jobs 0
    .venv/Scripts/python.exe -m tier05.exp_furina_tab_sweep --runs 1000 --jobs 0 --json out.json

WHAT IT RUNS. Whole runs (every act, `--realistic` loadout: relics and
potions) through `tier05.model.run_one`, the same machinery as
`tier05.runner`, over the same seeds in every cell:

- Furina under three draft policies (`blind` = uniform random from the
  screen, the offer floor; `adaptive` = greedy by the drafter's score;
  `assigned` = her `salon` plan) x both routes (`hunter`, `cautious`).
- The two reference characters the run sim carries (`real_ironclad`,
  `real_silent`) under the same policies and routes. The base five's other
  three have no run-sim arm.
- THE K3 CELLS: Furina, adaptive draft, hunter route, with the in-card Drain
  choice made three ways (`DECIDERS`): `always` (the shipped sim decider,
  `furina_stage.FurinaTideDecider`: take every legal Drain mode), `never`
  (decline every Drain mode; fixed-price Drain cards are still played), and
  `covered` (take a Drain mode only when her Block already covers the
  posted hit). The card-play pilot is unchanged in all three, so the card it
  chooses still assumes the shipped decider.

WHAT IT READS, per fight: node kind and act, turns, HP in and out (after
the curtain call), the Fanfare ledger, the Drain
modes offered, blocked by the line and taken, and every card played. Per run:
the draft screens (offered, picked) and the final deck.

An INSTRUMENT, not a balance number: prototype rows, no stamp is claimed
(`EXPERIMENTS.md` binds at Balance). Run i is a pure function of seed + i.
"""

from __future__ import annotations

import argparse
import collections
import inspect
import json
import statistics
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor

DECIDERS = ("always", "never", "covered")
POLICIES = ("blind", "adaptive", "assigned")
ROUTES = ("hunter", "cautious")
REFERENCES = ("real_ironclad", "real_silent")

#: Per-fight Drain-mode tallies, reset by the fight wrapper.
_TALLY: dict = {}


def _base(cid: str) -> str:
    return cid.split("+")[0]


def _make_decider(kind: str):
    from tier0.engine import furina_stage as FS
    from tier0.pilot.policy import _incoming_damage

    class SweepDecider(FS.FurinaTideDecider):
        def spend_mode(self, state, modes):
            priced = [i for i, m in enumerate(modes)
                      if FS.spend_mode_amount(m) is not None
                      or FS.drain_mode_amount(m) is not None]
            if len(priced) != 1:
                return None
            index = priced[0]
            keep = next((i for i in range(len(modes)) if i != index), 0)
            mode = modes[index]
            if FS.drain_mode_amount(mode) is None:
                return index if FS.mode_offered(state.player, mode) else keep
            _TALLY["offers"] = _TALLY.get("offers", 0) + 1
            if not FS.mode_offered(state.player, mode):
                _TALLY["blocked"] = _TALLY.get("blocked", 0) + 1
                return keep
            if kind == "never":
                take = False
            elif kind == "covered":
                take = state.player.block >= _incoming_damage(state)
            else:
                take = True
            if take:
                _TALLY["taken"] = _TALLY.get("taken", 0) + 1
                return index
            return keep

    return SweepDecider()


def _install(decider: str) -> None:
    """Patch, inside a worker, the decider and the fight call."""
    from tier0.engine import furina_stage as FS
    from tier05 import model

    FS.FURINA_TIDE_DECIDER = _make_decider(decider)
    real = model.run_fight

    def fight(player, enemies, pilot, seed=None, **kw):
        frame = inspect.currentframe().f_back
        ctx = frame.f_locals.get("self")
        kind = frame.f_locals.get("kind", "?")
        _TALLY.clear()
        hp_in = player.hp
        state = real(player, enemies, pilot, seed=seed, **kw)
        plays = collections.Counter(
            _base(e["card"]) for e in state.log if e.get("event") == "play")
        per_turn = collections.Counter(
            e["turn"] for e in state.log if e.get("event") == "play")
        dmg_turn = collections.Counter()
        for e in state.log:
            if e.get("event") == "damage":
                dmg_turn[e["turn"]] += int(e.get("amount") or 0)
        rec = {"kind": kind, "act": getattr(ctx, "act_i", -1) + 1,
               "won": state.player.alive and not state.living_enemies,
               "turns": state.turn, "hp_in": hp_in,
               "hp_out": state.player.hp, "max_hp": state.player.max_hp,
               "plays": dict(plays),
               "max_plays_turn": max(per_turn.values(), default=0),
               "max_damage_turn": max(dmg_turn.values(), default=0),
               "drain_offers": _TALLY.get("offers", 0),
               "drain_blocked": _TALLY.get("blocked", 0),
               "drain_taken": _TALLY.get("taken", 0)}
        ftd = getattr(state.player, "ftd", None)
        if ftd is not None:
            L = ftd.ledger
            rec.update({
                "drained": L["drained"], "drains": L["drains"],
                "repaid": L["repaid"], "gained": L["gained"],
                "gained_by": dict(L["gained_by"]), "spent": L["spent"],
                "spends": L["spends"], "fanfare_end": L["fanfare_end"],
                "curtain_repaid": L["curtain_repaid"],
                "unrepaid_end": L["unrepaid_end"]})
        if ctx is not None:
            ctx._sweep_fights.append(rec)
        return state

    model.run_fight = fight


def _run_block(args) -> list[dict]:
    (character, plan, pilot, policy, route, decider, seed, lo, hi) = args
    from tier05 import draft, model
    _install(decider)
    out = []
    for i in range(lo, hi):
        fights: list[dict] = []
        # The fight wrapper finds the run's context through its caller's
        # frame; hand it a list by patching the class attribute per run.
        model._RunCtx._sweep_fights = fights
        r = model.run_one(character, plan, pilot, draft.POLICIES[policy],
                          seed + i, grant_relics=True, grant_potions=True,
                          route_name=route)
        out.append({
            "seed": seed + i, "won": r.won,
            "acts_completed": r.acts_completed,
            "deck": [_base(c) for c in r.deck_ids],
            "screens": [{"offers": [_base(c.id) for c in d["offers"]],
                         "picked": _base(d["picked"]) if d["picked"]
                         else None} for d in r.decisions],
            "fights": fights})
    return out


def run_cell(character, policy, route, decider, runs, seed, jobs):
    from tier05 import runner
    plan, pilot = runner.resolve_plan(character, None)
    import os
    workers = max(1, min((os.cpu_count() or 1) if jobs == 0 else jobs, runs))
    edges = [runs * k // workers for k in range(workers + 1)]
    blocks = [(character, plan, pilot, policy, route, decider, seed, lo, hi)
              for lo, hi in zip(edges, edges[1:]) if lo < hi]
    if workers == 1:
        return [r for b in blocks for r in _run_block(b)]
    with ProcessPoolExecutor(max_workers=len(blocks),
                             initializer=_quiet) as pool:
        return [r for block in pool.map(_run_block, blocks) for r in block]


def _quiet() -> None:
    warnings.filterwarnings("ignore")


# ----------------------------------------------------------------------
# Readings.
# ----------------------------------------------------------------------
def _mean(xs):
    xs = list(xs)
    return statistics.mean(xs) if xs else float("nan")


def summarize(results: list[dict]) -> dict:
    n = len(results)
    fights = [f for r in results for f in r["fights"]]
    out = {"runs": n,
           "win": sum(r["won"] for r in results) / n,
           "act1": sum(r["acts_completed"] >= 1 for r in results) / n,
           "act2": sum(r["acts_completed"] >= 2 for r in results) / n,
           "deck": _mean(len(r["deck"]) for r in results)}
    prof = {}
    for act in (1, 2, 3):
        for kind in ("N", "E", "B"):
            fs = [f for f in fights if f["act"] == act and f["kind"] == kind]
            if not fs:
                continue
            prof[f"{act}{kind}"] = {
                "n": len(fs),
                "won": sum(f["won"] for f in fs) / len(fs),
                "turns": _mean(f["turns"] for f in fs),
                "hp_lost": _mean(f["hp_in"] - f["hp_out"] for f in fs
                                 if f["won"]),
                "hp_lost_pct": _mean(100 * (f["hp_in"] - f["hp_out"])
                                     / f["max_hp"] for f in fs if f["won"]),
            }
    out["profile"] = prof
    deaths = collections.Counter(
        f"{f['act']}{f['kind']}" for r in results for f in r["fights"]
        if not f["won"])
    out["deaths"] = dict(deaths)
    if fights and "drained" in fights[0]:
        off = sum(f["drain_offers"] for f in fights)
        blk = sum(f["drain_blocked"] for f in fights)
        tak = sum(f["drain_taken"] for f in fights)
        out["k3"] = {
            "mode_offers": off, "blocked_by_line": blk, "taken": tak,
            "taken_of_legal": tak / (off - blk) if off - blk else float("nan"),
            "drains_per_fight": _mean(f["drains"] for f in fights),
            "drained_hp_per_fight": _mean(f["drained"] for f in fights),
            "repaid_per_fight": _mean(f["repaid"] for f in fights),
            "curtain_per_fight": _mean(f["curtain_repaid"] for f in fights),
            "fanfare_gained": _mean(f["gained"] for f in fights),
            "fanfare_spent": _mean(f["spent"] for f in fights),
            "fanfare_left": _mean(f["fanfare_end"] for f in fights),
        }
        out["runaway"] = {
            "max_plays_turn": max(f["max_plays_turn"] for f in fights),
            "p999_plays_turn": sorted(f["max_plays_turn"] for f in fights)[
                int(0.999 * (len(fights) - 1))],
            "max_damage_turn": max(f["max_damage_turn"] for f in fights),
            "p999_damage_turn": sorted(f["max_damage_turn"] for f in fights)[
                int(0.999 * (len(fights) - 1))],
        }
        by = collections.Counter()
        for f in fights:
            by.update(f["gained_by"])
        out["fanfare_sources"] = {k: v / len(fights) for k, v in by.items()}
    return out


def card_table(results: list[dict]) -> dict:
    """Per card: offered, picked when offered, share of final decks holding
    it, win rate with and without it, plays per fight when held."""
    offered = collections.Counter()
    picked = collections.Counter()
    for r in results:
        for s in r["screens"]:
            offered.update(set(s["offers"]))
            if s["picked"]:
                picked[s["picked"]] += 1
    n = len(results)
    out = {}
    for cid in sorted(offered):
        have = [r for r in results if cid in r["deck"]]
        lack = [r for r in results if cid not in r["deck"]]
        held_fights = [f for r in have for f in r["fights"]]
        out[cid] = {
            "offered": offered[cid], "picked": picked[cid],
            "pick_rate": picked[cid] / offered[cid],
            "in_deck": len(have) / n,
            "win_with": (sum(r["won"] for r in have) / len(have)
                         if have else float("nan")),
            "win_without": (sum(r["won"] for r in lack) / len(lack)
                            if lack else float("nan")),
            "acts_with": _mean(r["acts_completed"] for r in have),
            "acts_without": _mean(r["acts_completed"] for r in lack),
            "plays_per_fight": _mean(f["plays"].get(cid, 0)
                                     for f in held_fights),
        }
        # THE RANDOMISED READ (meaningful under the blind draft, which takes
        # uniformly from the screen): runs offered this card in the first
        # EARLY screens, split by whether it was taken there.
        took, passed = [], []
        for r in results:
            early = r["screens"][:EARLY]
            if not any(cid in s["offers"] for s in early):
                continue
            (took if any(s["picked"] == cid for s in early)
             else passed).append(r)
        out[cid].update({
            "early_took": len(took), "early_passed": len(passed),
            "early_acts_took": _mean(r["acts_completed"] for r in took),
            "early_acts_passed": _mean(r["acts_completed"] for r in passed),
            "early_win_took": (sum(r["won"] for r in took) / len(took)
                               if took else float("nan")),
            "early_win_passed": (sum(r["won"] for r in passed) / len(passed)
                                 if passed else float("nan")),
        })
    return out


#: Screens counted as "early" by `card_table`'s randomised read.
EARLY = 4


def starter_plays(results: list[dict]) -> dict:
    fights = [f for r in results for f in r["fights"]]
    tot = collections.Counter()
    for f in fights:
        tot.update(f["plays"])
    return {k: v / len(fights) for k, v in tot.most_common()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--jobs", type=int, default=0)
    ap.add_argument("--json")
    ap.add_argument("--quick", action="store_true",
                    help="adaptive/hunter/always and the K3 cells only")
    ap.add_argument("--no-cards", action="store_true",
                    help="skip the per-card tables")
    ap.add_argument("--policy", action="append", choices=POLICIES,
                    help="run only these draft policies (repeatable)")
    ap.add_argument("--only", action="append",
                    help="run only this character's cells (repeatable); the "
                         "reference arms need `game_ref/`, which a worktree "
                         "does not have")
    args = ap.parse_args(argv)
    warnings.filterwarnings("ignore")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    cells = []
    if args.quick:
        cells += [("furina", "adaptive", "hunter", d) for d in DECIDERS]
    else:
        cells += [("furina", p, r, "always") for p in POLICIES
                  for r in ROUTES]
        cells += [("furina", "adaptive", "hunter", d) for d in DECIDERS
                  if d != "always"]
        cells += [(c, p, r, "always") for c in REFERENCES
                  for p in ("blind", "adaptive") for r in ROUTES]
    if args.only:
        cells = [c for c in cells if c[0] in args.only]
    if args.policy:
        cells = [c for c in cells if c[1] in args.policy]
    report: dict = {"runs": args.runs, "seed": args.seed, "cells": {}}
    for cell in cells:
        res = run_cell(*cell, args.runs, args.seed, args.jobs)
        key = "/".join(cell)
        row = summarize(res)
        if cell[0] == "furina" and cell[3] == "always" and \
                cell[2] == "hunter":
            row["cards"] = card_table(res)
            row["plays"] = starter_plays(res)
        report["cells"][key] = row
        k3 = row.get("k3", {})
        print(f"{key:40s} win {row['win']:6.1%}  act1 {row['act1']:6.1%}  "
              f"act2 {row['act2']:6.1%}  deck {row['deck']:4.1f}"
              + (f"  drains taken {k3['taken_of_legal']:.0%}" if k3 else ""),
              flush=True)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1, default=float)
    return 0


if __name__ == "__main__":
    from tier05 import expcli
    expcli.help_if_asked(__doc__)
    raise SystemExit(main())
