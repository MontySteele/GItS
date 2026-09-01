"""`KURAGECAD-S1` — the Kurage memory's CADENCE measured DRAFTED. THE INSTRUMENT.

THE REGISTRATION IS ELSEWHERE AND CAME FIRST:
`review/ruled/kokomi-kurage-memory-2026-08-29.md` §15, committed before this
file. This module PREDICTS NOTHING. Every threshold it prints a grade against is
quoted from §15.4 as a literal below, so a reader can check the grade against the
registration without leaving the file, and so no threshold can drift after a
number is seen (R101b).

WHAT IT MEASURES: counts, per PLAYER TURN, of what the memory did. §15.2 fixes
every definition and this module implements those and no others:

  a player turn   one `turn_open` event in a fight's log.
  its state       exactly one of `kurage_memory_fire` / `kurage_memory_blocked`
                  / `kurage_memory_empty` -- `combat._player_turn` emits
                  precisely one per turn while the rule is live, which is what
                  makes "share of turns" a legitimate denominator.
  queue length    the authoritative `queued` / `remaining` field on that turn's
                  own state event. Never reconstructed.
  her own plays   the turn's `play` events minus the turn's fires. Any other
                  free-play route counts as HERS, which can only make the
                  memory's share look SMALLER (§15.2, the conservative
                  direction for `C5`).

WHAT IT MOVES: nothing. No constant, no drafter dial, no policy branch, no
engine rule. `C.KURAGE_MEMORY` is flipped at run time and restored in a
`finally`, and both observers are EMIT-ONLY -- each wrapper returns exactly what
the wrapped callable returned, so an observed run and an unobserved one are the
same run.

THE OBSERVER SEAMS, named because monkeypatching is a real cost:

  model.run_one            opens one run record. `_run_range` calls it as a
                           module global, so the patch is seen.
  model._RunCtx._record_traces
                           the ONE place a fight's `state.log` and its `act_i`
                           are both in scope; the log does not survive onto the
                           RunResult, so anything not reduced here is
                           unrecoverable. It also carries `self.deck_ids`, the
                           deck as it stood when the fight was fought.

`jobs` MUST BE 1. A `jobs > 1` (or `jobs = 0`, which means one worker per CPU)
batch runs in worker PROCESSES that neither patch reaches, and would return a
correct RunResult list with an empty observation set. `main` refuses anything
else rather than printing a silent zero.

Usage: python -m tier05.exp_kurage_cadence_s1 [--runs N] [--seed N]
                                              [--json PATH]
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter

from tier0 import constants as C
from tier0.content import loader
from tier05 import cells, expcli, model, stats

# --- the arm, as §15.2 registered it ----------------------------------------

#: §15.2's cell. Named here so the record's header and the registration cannot
#: disagree about what ran. `commander` is Kokomi's Companion/Muster plan, the
#: one plan under which both entry doors are reachable by draft.
CELL = cells.CANONICAL.but(name="kuragecad-s1", character="kokomi",
                           archetype="commander", jobs=1)

#: The three memory states a player turn can be in (§15.2). Exactly one event
#: per turn while the rule is live.
STATE_EVENTS = {"kurage_memory_fire": "fire",
                "kurage_memory_blocked": "blocked",
                "kurage_memory_empty": "empty"}


def _clear_caches() -> None:
    """Every memo the flag invalidates, in one place.

    `_card_prototype` and `_substituted_card_index` both resolve the
    substituted pool row, and `rewards.character_pool` reads the substitution
    map through `loader.pool_substitutions`. Flipping the flag without clearing
    all three silently serves the other arm's cards.
    """
    from tier05 import rewards
    loader._card_prototype.cache_clear()
    loader._substituted_card_index.cache_clear()
    rewards.character_pool.cache_clear()


# --- deck reads (sheet-only, no play) ---------------------------------------

def _peek(cid: str):
    """The sheet row for an id, or None when nothing can resolve it.

    None rather than a raise: a deck list is read for `C8`/`C9` inside the arm's
    flag window, and an id neither index knows is a fact about the seam, not a
    reason to lose 600 runs of observations.
    """
    try:
        return loader.peek_card(cid)
    except KeyError:
        return None


def _prints_exhaust(cid: str) -> bool:
    """§15.4 `C8`: a sheet read of `Card.exhaust`, never a read of play."""
    card = _peek(cid)
    return bool(card is not None and card.exhaust)


def _is_ethereal(cid: str) -> bool:
    """§15.4 `C9`: `Card.is_ethereal`, the one predicate that sees both the
    `ethereal:` field and the `tags: [ethereal]` spelling."""
    card = _peek(cid)
    return bool(card is not None and card.is_ethereal)


# --- the per-fight reduction -------------------------------------------------

def trace(log: list[dict], act_i: int) -> dict:
    """One combat's cadence, segmented by player turn.

    Taken here rather than later because `state.log` does not survive onto the
    RunResult; everything the slate grades is a field of the dict returned.
    """
    turns: list[dict] = []
    cur: dict | None = None
    enrolments: list[dict] = []
    fires: list[dict] = []
    refusals: Counter = Counter()
    full = 0

    for ev in log:
        name = ev.get("event")
        if name == "turn_open":
            cur = {"act": act_i, "state": "none", "qlen": None,
                   "plays": 0, "fires": 0}
            turns.append(cur)
            continue
        if name in STATE_EVENTS:
            if cur is not None:
                # The FIRST state event of the turn is the turn's state: the
                # automatic fire is one per turn by the latch, and no card in
                # any pool calls the manual door.
                if cur["state"] == "none":
                    cur["state"] = STATE_EVENTS[name]
                    cur["qlen"] = (ev.get("remaining", 0) + 1
                                   if name == "kurage_memory_fire"
                                   else ev.get("queued", 0))
                if name == "kurage_memory_fire":
                    cur["fires"] += 1
            if name == "kurage_memory_fire":
                fires.append({"price": int(ev.get("price", 0)),
                              "bank": int(ev.get("bank", 0)),
                              "card": ev.get("card"),
                              "rule": ev.get("rule")})
            continue
        if name == "kurage_remember":
            enrolments.append({"rule": ev.get("rule"),
                               "price": int(ev.get("price", 0)),
                               "cost": ev.get("cost"),
                               "card": ev.get("card")})
            continue
        if name == "kurage_memory_refused":
            refusals[str(ev.get("reason"))] += 1
            continue
        if name == "kurage_memory_full":
            full += 1
            continue
        if name == "play" and cur is not None:
            cur["plays"] += 1

    for t in turns:
        # §15.2: her own plays are the turn's plays minus the turn's fires. A
        # memory copy reaches `resolve_free_play`, which emits `play`, so the
        # subtraction is what separates the two.
        t["own_plays"] = max(0, t["plays"] - t["fires"])
        t["memory_only"] = bool(t["fires"] and t["own_plays"] == 0)
    return {"turns": turns, "enrolments": enrolments, "fires": fires,
            "refusals": dict(refusals), "full": full}


# --- the observer ------------------------------------------------------------

class _Observer:
    """One arm's records. EMIT-ONLY; see the module docstring."""

    def __init__(self) -> None:
        self.runs: list[dict] = []
        self._run: dict | None = None

    def open_run(self) -> dict:
        self._run = {"fights": [], "deck": [], "won": False}
        self.runs.append(self._run)
        return self._run

    def note_fight(self, rec: dict, deck: list[str]) -> None:
        if self._run is not None:
            rec = dict(rec)
            rec["deck"] = list(deck)
            self._run["fights"].append(rec)


def _observe(flag_on: bool, cell) -> tuple[list, _Observer, dict]:
    """Run `cell` under the flag with both seams patched, and REDUCE the
    observations before the flag comes back off.

    The reduction is inside the flag window on purpose: `loader.peek_card`
    resolves the substituted pool row through `_substituted_card_index`, which
    is EMPTY with the flag off, so reading a drafted deck's Exhaust density
    after the restore would read a hole. Restores both patches, the flag and
    the three caches in a `finally`, so a raised exception cannot leave the
    module or the world edited.
    """
    obs = _Observer()
    real_run_one = model.run_one
    real_record = model._RunCtx._record_traces
    original_flag = C.KURAGE_MEMORY

    def run_one(*a, **kw):
        obs.open_run()
        res = real_run_one(*a, **kw)
        obs.runs[-1]["deck"] = list(res.deck_ids)
        obs.runs[-1]["won"] = bool(res.won)
        return res

    def record_traces(self, state):
        obs.note_fight(trace(state.log, self.act_i), self.deck_ids)
        return real_record(self, state)

    model.run_one = run_one
    model._RunCtx._record_traces = record_traces
    C.KURAGE_MEMORY = flag_on
    try:
        _clear_caches()
        results = cell.run()
        arm = _reduce(obs)
    finally:
        model.run_one = real_run_one
        model._RunCtx._record_traces = real_record
        C.KURAGE_MEMORY = original_flag
        _clear_caches()
    return results, obs, arm


# --- reduction ---------------------------------------------------------------

def _share(n: int, d: int) -> float:
    return (n / d) if d else 0.0


def _reduce(obs: _Observer) -> dict:
    """The arm's numbers. Every graded field is one of §15.4's falsifiers."""
    turns = [t for run in obs.runs for f in run["fights"] for t in f["turns"]]
    fires = [x for run in obs.runs for f in run["fights"] for x in f["fires"]]
    enrolments = [e for run in obs.runs for f in run["fights"]
                  for e in f["enrolments"]]
    decks = [run["deck"] for run in obs.runs]
    n_turns = len(turns)

    by_act: dict[str, dict] = {}
    for act in sorted({t["act"] for t in turns}):
        rows = [t for t in turns if t["act"] == act]
        by_act[str(act)] = {
            "turns": len(rows),
            "fire_share": _share(sum(t["state"] == "fire" for t in rows),
                                 len(rows)),
            "blocked_share": _share(sum(t["state"] == "blocked" for t in rows),
                                    len(rows)),
            "empty_share": _share(sum(t["state"] == "empty" for t in rows),
                                  len(rows)),
        }

    qlens = [t["qlen"] for t in turns if t["qlen"] is not None]
    fires_per_run = [sum(len(f["fires"]) for f in run["fights"])
                     for run in obs.runs]
    fires_per_fight = [len(f["fires"]) for run in obs.runs
                       for f in run["fights"]]
    rules = Counter(e["rule"] for e in enrolments)
    refusals: Counter = Counter()
    full = 0
    for run in obs.runs:
        for f in run["fights"]:
            refusals.update(f["refusals"])
            full += f["full"]

    exhaust_counts = [sum(_prints_exhaust(cid) for cid in d) for d in decks]
    ethereal_decks = sum(any(_is_ethereal(cid) for cid in d) for d in decks)
    ethereal_enrolments = sum(_is_ethereal(e["card"]) for e in enrolments)

    total_plays = sum(t["plays"] for t in turns)
    return {
        "runs": len(obs.runs),
        "fights": sum(len(run["fights"]) for run in obs.runs),
        "turns": n_turns,
        # C1 / C4
        "fire_share": _share(sum(t["state"] == "fire" for t in turns), n_turns),
        "blocked_share": _share(sum(t["state"] == "blocked" for t in turns),
                                n_turns),
        "empty_share": _share(sum(t["state"] == "empty" for t in turns),
                              n_turns),
        "no_state_share": _share(sum(t["state"] == "none" for t in turns),
                                 n_turns),
        # C2
        "by_act": by_act,
        # C3
        "enrolments": len(enrolments),
        "rule_share": {r: _share(rules[r], len(enrolments))
                       for r in ("exhaust", "muster")},
        # C5
        "plays": total_plays,
        "memory_play_share": _share(len(fires), total_plays),
        "memory_only_share": _share(sum(t["memory_only"] for t in turns),
                                    n_turns),
        # C6
        "fires": len(fires),
        "free_fire_share": _share(sum(f["price"] == 0 for f in fires),
                                  len(fires)),
        "fire_price_median": (statistics.median(f["price"] for f in fires)
                              if fires else 0.0),
        "fire_bank_median": (statistics.median(f["bank"] for f in fires)
                             if fires else 0.0),
        # C7
        "qlen_median": statistics.median(qlens) if qlens else 0.0,
        "qlen_p95": stats.percentile(qlens, 0.95) if qlens else 0.0,
        "qlen_max": max(qlens) if qlens else 0,
        # C8 / C9
        "exhaust_median": (statistics.median(exhaust_counts)
                           if exhaust_counts else 0.0),
        "exhaust_mean": (statistics.mean(exhaust_counts)
                         if exhaust_counts else 0.0),
        "ethereal_decks": ethereal_decks,
        "ethereal_enrolments": ethereal_enrolments,
        # R1 / R2 -- RECORDED AND NOT GRADED
        "fires_per_run_mean": (statistics.mean(fires_per_run)
                               if fires_per_run else 0.0),
        "fires_per_run_median": (statistics.median(fires_per_run)
                                 if fires_per_run else 0.0),
        "fires_per_run_max": max(fires_per_run) if fires_per_run else 0,
        "fires_per_fight_mean": (statistics.mean(fires_per_fight)
                                 if fires_per_fight else 0.0),
        "refusals": dict(refusals),
        "queue_full_events": full,
        # R4 -- diagnostics only, graded by nothing (R213 B / R215 B)
        "win_share": _share(sum(bool(r["won"]) for r in obs.runs),
                            len(obs.runs)),
        "decksize_mean": (statistics.mean(len(d) for d in decks)
                          if decks else 0.0),
    }


# --- the grader --------------------------------------------------------------

def _both(a: bool, b: bool) -> str:
    return "PREDICTED" if (a and b) else "SPLIT" if (a or b) else "MISS"


def _grade(arm: dict) -> list[dict]:
    """§15.4's nine slots, against §15.4's thresholds and no others."""
    out = []
    turns = arm["turns"]

    # C1 -- >= 20% PREDICTED, 5% to < 20% SPLIT, < 5% MISS; UNREACHED < 500
    share = arm["fire_share"]
    g = ("UNREACHED" if turns < 500
         else "PREDICTED" if share >= 0.20
         else "SPLIT" if share >= 0.05 else "MISS")
    out.append({"slot": "C1", "grade": g,
                "read": f"{share * 100:.2f}% of {turns} player turns FIRE",
                "threshold": ">= 20% PREDICTED, 5-20% SPLIT, < 5% MISS"})

    # C2 -- act 3 > act 1 AND act 3 >= 1.25 x act 1; UNREACHED < 200 act-3 turns
    a1 = arm["by_act"].get("0")
    a3 = arm["by_act"].get("2")
    if a3 is None or a1 is None or a3["turns"] < 200:
        g = "UNREACHED"
        read = "fewer than 200 act-3 player turns"
    else:
        g = _both(a3["fire_share"] > a1["fire_share"],
                  a3["fire_share"] >= 1.25 * a1["fire_share"])
        read = (f"act 1 {a1['fire_share'] * 100:.2f}% (n={a1['turns']}) -> "
                f"act 3 {a3['fire_share'] * 100:.2f}% (n={a3['turns']})")
    out.append({"slot": "C2", "grade": g, "read": read,
                "threshold": "act 3 > act 1 AND act 3 >= 1.25 x act 1"})

    # C3 -- exhaust >= 50% AND muster >= 20%; UNREACHED < 200 enrolments
    ex = arm["rule_share"].get("exhaust", 0.0)
    mu = arm["rule_share"].get("muster", 0.0)
    g = ("UNREACHED" if arm["enrolments"] < 200
         else _both(ex >= 0.50, mu >= 0.20))
    out.append({"slot": "C3", "grade": g,
                "read": f"Exhaust {ex * 100:.1f}% / Muster {mu * 100:.1f}% "
                        f"of {arm['enrolments']} enrolments",
                "threshold": "Exhaust >= 50% AND Muster >= 20%"})

    # C4 -- blocked <= 25% PREDICTED, > 25% to 50% SPLIT, > 50% MISS
    share = arm["blocked_share"]
    g = ("PREDICTED" if share <= 0.25
         else "SPLIT" if share <= 0.50 else "MISS")
    out.append({"slot": "C4", "grade": g,
                "read": f"BLOCKED on {share * 100:.2f}% of turns "
                        f"(EMPTY {arm['empty_share'] * 100:.2f}%, ungraded)",
                "threshold": "<= 25% PREDICTED, 25-50% SPLIT, > 50% MISS"})

    # C5 -- memory copies <= 25% of plays AND memory-only turns <= 10%
    g = ("UNREACHED" if turns < 500
         else _both(arm["memory_play_share"] <= 0.25,
                    arm["memory_only_share"] <= 0.10))
    out.append({"slot": "C5", "grade": g,
                "read": f"memory copies {arm['memory_play_share'] * 100:.2f}% "
                        f"of {arm['plays']} plays; memory-only turns "
                        f"{arm['memory_only_share'] * 100:.2f}%",
                "threshold": "copies <= 25% of plays AND memory-only <= 10% "
                             "of turns"})

    # C6 -- free fires <= 50% PREDICTED, > 50% to 75% SPLIT, > 75% MISS
    share = arm["free_fire_share"]
    g = ("UNREACHED" if arm["fires"] < 100
         else "PREDICTED" if share <= 0.50
         else "SPLIT" if share <= 0.75 else "MISS")
    out.append({"slot": "C6", "grade": g,
                "read": f"{share * 100:.1f}% of {arm['fires']} fires are free "
                        f"(median price {arm['fire_price_median']:.1f}, "
                        f"median bank {arm['fire_bank_median']:.1f})",
                "threshold": "<= 50% PREDICTED, 50-75% SPLIT, > 75% MISS"})

    # C7 -- median queue <= 3 AND p95 <= 8
    g = ("UNREACHED" if turns < 500
         else _both(arm["qlen_median"] <= 3, arm["qlen_p95"] <= 8))
    out.append({"slot": "C7", "grade": g,
                "read": f"queue median {arm['qlen_median']:.1f}, p95 "
                        f"{arm['qlen_p95']:.1f}, max {arm['qlen_max']}",
                "threshold": "median <= 3 AND p95 <= 8"})

    # C8 -- median final deck holds >= 4 Exhaust cards
    med = arm["exhaust_median"]
    g = ("PREDICTED" if med >= 4 else "SPLIT" if med >= 2 else "MISS")
    out.append({"slot": "C8", "grade": g,
                "read": f"median {med:.1f} Exhaust cards per final deck "
                        f"(mean {arm['exhaust_mean']:.2f})",
                "threshold": ">= 4 PREDICTED, 2-4 SPLIT, < 2 MISS"})

    # C9 -- instrument check: exactly 0 either way
    g = ("PREDICTED" if (arm["ethereal_decks"] == 0
                         and arm["ethereal_enrolments"] == 0) else "MISS")
    out.append({"slot": "C9", "grade": g,
                "read": f"{arm['ethereal_decks']} decks and "
                        f"{arm['ethereal_enrolments']} enrolments hold an "
                        f"Ethereal card",
                "threshold": "exactly 0 and 0 PREDICTED, anything > 0 MISS"})
    return out


def _print_arm(label: str, arm: dict) -> None:
    print(label)
    print(f"    runs {arm['runs']}   fights {arm['fights']}   "
          f"player turns {arm['turns']}   card plays {arm['plays']}")
    print(f"    turn state       FIRE {arm['fire_share'] * 100:6.2f}%   "
          f"BLOCKED {arm['blocked_share'] * 100:6.2f}%   "
          f"EMPTY {arm['empty_share'] * 100:6.2f}%   "
          f"no event {arm['no_state_share'] * 100:6.2f}%")
    for act, row in arm["by_act"].items():
        print(f"    act {int(act) + 1}            FIRE "
              f"{row['fire_share'] * 100:6.2f}%   "
              f"BLOCKED {row['blocked_share'] * 100:6.2f}%   "
              f"EMPTY {row['empty_share'] * 100:6.2f}%   "
              f"n={row['turns']}")
    print(f"    enrolments       {arm['enrolments']}   "
          f"Exhaust {arm['rule_share'].get('exhaust', 0.0) * 100:.1f}%   "
          f"Muster {arm['rule_share'].get('muster', 0.0) * 100:.1f}%")
    print(f"    fires            {arm['fires']}   free "
          f"{arm['free_fire_share'] * 100:.1f}%   median price "
          f"{arm['fire_price_median']:.1f}   median bank "
          f"{arm['fire_bank_median']:.1f}")
    print(f"    spam             copies {arm['memory_play_share'] * 100:.2f}% "
          f"of plays   memory-only turns "
          f"{arm['memory_only_share'] * 100:.2f}%")
    print(f"    queue length     median {arm['qlen_median']:.1f}   p95 "
          f"{arm['qlen_p95']:.1f}   max {arm['qlen_max']}   "
          f"queue-full events {arm['queue_full_events']}")
    print(f"    fires per run    mean {arm['fires_per_run_mean']:.2f}   "
          f"median {arm['fires_per_run_median']:.1f}   "
          f"max {arm['fires_per_run_max']}   per fight "
          f"{arm['fires_per_fight_mean']:.2f}")
    print(f"    refusals         {arm['refusals'] or '{}'}")
    print(f"    drafted deck     median {arm['exhaust_median']:.1f} Exhaust "
          f"cards (mean {arm['exhaust_mean']:.2f})   Ethereal decks "
          f"{arm['ethereal_decks']}")
    print(f"    mean deck size {arm['decksize_mean']:.1f}   runs won "
          f"{arm['win_share'] * 100:.1f}%   NOT A BALANCE CLAIM (R215 B)")
    print()


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", type=int, default=CELL.runs)
    ap.add_argument("--seed", type=int, default=CELL.seed)
    ap.add_argument("--json", default=None,
                    help="write the record to this path")
    args = ap.parse_args(argv)

    cell = CELL.but(runs=args.runs, seed=args.seed, name=CELL.name)
    if cell.jobs != 1:
        print("REFUSED: the observer seams live in this process; jobs must "
              "be 1.", file=sys.stderr)
        return 2

    stamp = cells.world_stamp()
    print("KURAGECAD-S1 — the Kurage memory's CADENCE, measured DRAFTED.")
    print("  REGISTRATION: review/ruled/kokomi-kurage-memory-2026-08-29.md "
          "§15 (slate §15.4), committed before this file and before this run.")
    print(f"  world stamp {stamp}   cell {cell.describe()}")
    print("  NOT A BALANCE READ (R213 B / R215 B). Counts only; the pilot "
          "values the queue at zero, so every number is a FLOOR.")
    print("  ARM = C.KURAGE_MEMORY ON: the v4 base kit, the starter swap and "
          "the pool swap.")
    print("  CONTROL = flag OFF, same cell and seeds: RECORDED, NOT GRADED.")
    print()

    record: dict = {"registration": "KURAGECAD-S1",
                    "packet": "review/ruled/kokomi-kurage-memory-2026-08-29"
                              ".md §15",
                    "stamp": stamp, "cell": cell.describe(), "arms": {}}
    for label, flag in (("flag OFF (shipped Kokomi) — CONTROL, NOT GRADED",
                         False),
                        ("flag ON  (the memory) — GRADED", True)):
        _, _obs, arm = _observe(flag, cell)
        _print_arm(label, arm)
        record["arms"]["on" if flag else "off"] = arm

    grades = _grade(record["arms"]["on"])
    record["grades"] = grades
    print("THE SLATE, graded against §15.4's registered thresholds:")
    for row in grades:
        print(f"  {row['slot']}  {row['grade']:<10}  {row['read']}")
        print(f"      threshold: {row['threshold']}")
    tally = Counter(row["grade"] for row in grades)
    print()
    print("  " + " / ".join(f"{tally[k]} {k}" for k in
                            ("PREDICTED", "SPLIT", "MISS", "UNREACHED")))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2, sort_keys=True)
        print(f"record written to {args.json}")
    return 0


if __name__ == "__main__":
    expcli.help_if_asked(__doc__)
    sys.exit(main())
