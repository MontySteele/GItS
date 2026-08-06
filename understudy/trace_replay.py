"""Reconstruct what a recorded fight did, and compare two recordings of it.

    python -m understudy.trace_replay <stamp>            # every run in a soak
    python -m understudy.trace_replay <stamp> --run 1    # one run
    python -m understudy.trace_replay <stampA> <stampB>  # compare two soaks

NOT `understudy/replay.py`, AND THE NAME IS A COLLISION WORTH READING ABOUT.
P1.5's spec named `understudy/replay.py`, and no such file existed at the
commit P1.5 branched from. One landed on `main` from the S7 fidelity audit
while this work was in flight, and it is a DIFFERENT INSTRUMENT wearing the
same word:

    understudy/replay.py        S7. Drives tier0's combat model through the
                                recorded action sequence and diffs the two
                                instruments' numbers. It reads the sim.
    understudy/trace_replay.py  P1.5. Reads two soak logs and reports whether
                                the RECORDINGS agree. It reads nothing but
                                JSONL.

The landed file keeps the name it landed with; this one moved. **Which module
P1.5's acceptance clause meant is a question for the red pen, not for a
session** -- but the clause's own words are "reconstruction only, no rules
retyped", and that describes this file rather than the one that drives an
engine. Surfaced in `docs/archive/sprint-understudy-p15-log-2026-08-05.md`.

THE REASON THIS FILE EXISTS AT ALL. P1.5 item 1 makes two soaks
runnable on the SAME seed; item 3 puts the selector answers in the fight
record. Together those make a recorded fight comparable to another recording
of the same fight, which is the whole of "one variable per measurement window"
(R95). This module is the reader that performs the comparison.

WHAT THIS IS NOT, STATED FIRST BECAUSE IT IS THE EASY MISTAKE
**It does not simulate anything and it never will.** No rule is retyped here:
no damage formula, no meter law, no draft score. It reads two JSONL logs the
soak wrote and reports whether the recorded traces agree. A reconstruction
that computed what SHOULD have happened would be a third engine, and the repo
already carries the two it can keep honest (tier0 and the mod).

THE TRACE, AND WHY IT IS THESE FIELDS
A fight's trace is the ordered sequence of things the game was ASKED and the
meters it showed when asked:

    cards_played      what was played, in order, with the round
    selectors         which selector answers were given, from which offers
    meters_by_turn    fanfare / salon / salon_cap / encore at each opening

Two runs of the same seed driven by the same policy must produce identical
traces. A divergence is a fact about the two builds, not about the bot -- and
that is only true because `understudy.rng` keeps the game seed out of the
policy stream, so the policy is a pure function of the wire state.

`hp_trajectory` and the damage totals are deliberately NOT part of the trace
identity: they are the OUTPUT a comparison is trying to measure, and folding
them into the identity would make every interesting result an inequality of
the thing being compared with itself.

GUARDRAIL-7 STILL APPLIES. Two identical traces prove the harness is
deterministic. They are not evidence about balance, difficulty or fun.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from understudy.report import LOG_DIR, latest_stamp, load, read_run_log

# The fight-record keys that make up a trace. Ordered, because the report
# prints the first disagreement and a stable order makes two reports of the
# same divergence read the same.
TRACE_KEYS = ("cards_played", "selectors", "meters_by_turn")

# Fields that IDENTIFY a fight within a run, as opposed to describing it.
FIGHT_KEYS = ("act", "floor", "kind")


def fights(stamp: str, run_index: int) -> list[dict]:
    """Every closed fight record in one run, in the order it closed."""
    return [r for r in read_run_log(stamp, run_index)
            if r.get("record") == "fight"]


def seed_of(stamp: str, run_index: int) -> dict[str, Any]:
    """What this run's seed was, and whether it was CHOSEN or rolled.

    `chosen` is None on a read-back run (R95's arm) and a string on a P1.5
    chosen-seed run. `honoured` is None when nothing was chosen -- a run that
    asked for nothing cannot have been refused.
    """
    for r in read_run_log(stamp, run_index):
        if r.get("record") == "seed_read_back":
            return {"seed": r.get("seed"), "chosen": r.get("chosen"),
                    "honoured": r.get("honoured")}
    return {"seed": None, "chosen": None, "honoured": None}


def trace(fight: dict) -> dict[str, Any]:
    """The comparable part of one fight record.

    Missing keys read as empty rather than raising: a record written by a
    pre-P1.5 soak carries no `selectors`, and the honest report on that is
    "this run recorded no selector answers", not a crash.
    """
    return {k: fight.get(k) or [] for k in TRACE_KEYS}


def selector_lines(fight: dict) -> list[str]:
    """Human-readable reconstruction of the selector channel.

    THE OFFERED LIST IS PRINTED, not just the answer. "Center Stage" alone
    does not say whether Guest Cast was even available, and a reconstruction
    that cannot say so has not reconstructed the choice.
    """
    out = []
    for row in fight.get("selectors") or []:
        rnd, screen, idx, chosen, offered = (list(row) + [None] * 5)[:5]
        offered = offered or []
        marks = " | ".join(
            f"*{name}*" if i == idx else str(name)
            for i, name in enumerate(offered)) or "(no cards on the wire)"
        out.append(f"    t{rnd} {screen}[{idx}] -> "
                   f"{chosen or '(no card named)'}   from: {marks}")
    return out


def describe_run(stamp: str, run_index: int) -> str:
    seed = seed_of(stamp, run_index)
    fs = fights(stamp, run_index)
    lines = [f"run {run_index:03d}  seed={seed['seed']}"
             + (f"  CHOSEN={seed['chosen']} honoured={seed['honoured']}"
                if seed["chosen"] else "  (read-back)")]
    for i, f in enumerate(fs):
        meters = f.get("meters_by_turn") or []
        encore = [m[4] for m in meters if len(m) > 4]
        unseen = all(e == -1 for e in encore) if encore else True
        lines.append(
            f"  fight {i}: act {f.get('act')} floor {f.get('floor')} "
            f"{f.get('kind')}  turns={f.get('turns')} "
            f"outcome={f.get('outcome')}  "
            f"plays={len(f.get('cards_played') or [])} "
            f"selectors={len(f.get('selectors') or [])} "
            f"encore={'UNSEEN' if unseen else 'read'}")
        lines += selector_lines(f)
    return "\n".join(lines)


def compare_runs(a: tuple[str, int], b: tuple[str, int]) -> list[str]:
    """Report every trace divergence between two recordings of one run.

    An empty list is the acceptance condition: same seed, same actions, same
    recorded selector answers and meter readings.
    """
    (sa, ia), (sb, ib) = a, b
    findings: list[str] = []

    seed_a, seed_b = seed_of(sa, ia), seed_of(sb, ib)
    if seed_a["seed"] != seed_b["seed"]:
        findings.append(
            f"SEED: {seed_a['seed']} != {seed_b['seed']} -- these are two "
            f"different runs, and nothing below is a comparison")
        return findings

    fa, fb = fights(sa, ia), fights(sb, ib)
    if len(fa) != len(fb):
        findings.append(f"FIGHT COUNT: {len(fa)} != {len(fb)}")

    for i, (x, y) in enumerate(zip(fa, fb)):
        where = f"fight {i} (act {x.get('act')} floor {x.get('floor')})"
        for key in FIGHT_KEYS:
            if x.get(key) != y.get(key):
                findings.append(f"{where}: {key} {x.get(key)!r} != {y.get(key)!r}")
        ta, tb = trace(x), trace(y)
        for key in TRACE_KEYS:
            if ta[key] != tb[key]:
                findings.append(
                    f"{where}: {key} diverges\n"
                    f"      A: {json.dumps(ta[key])[:300]}\n"
                    f"      B: {json.dumps(tb[key])[:300]}")
    return findings


def render(stamp: str, run: int | None = None) -> str:
    index = load(stamp)
    runs = ([run] if run is not None
            else [r.get("index", i + 1)
                  for i, r in enumerate(index.get("runs") or [])])
    if not runs:
        runs = [1]
    out = [f"REPLAY  soak {stamp}  character={index.get('character')}  "
           f"policy={index.get('policy')}  seeds={index.get('seeds')}", ""]
    for i in runs:
        out.append(describe_run(stamp, int(i)))
        out.append("")
    out.append(
        "Guardrail-7: a reconstruction proves the RECORDING is faithful and "
        "the harness deterministic. It is not evidence about balance, "
        "difficulty, fun or legibility.")
    return "\n".join(out)


def render_compare(stamp_a: str, stamp_b: str, run: int | None = None) -> str:
    runs_a = load(stamp_a).get("runs") or []
    runs = [run] if run is not None else list(range(1, len(runs_a) + 1))
    out = [f"REPLAY COMPARE  A={stamp_a}  B={stamp_b}", ""]
    clean = True
    for i in runs:
        findings = compare_runs((stamp_a, i), (stamp_b, i))
        if findings:
            clean = False
            out.append(f"run {i:03d}: {len(findings)} divergence(s)")
            out += [f"    {f}" for f in findings]
        else:
            sd = seed_of(stamp_a, i)
            out.append(f"run {i:03d}: IDENTICAL  seed={sd['seed']}"
                       + (f" (chosen {sd['chosen']})" if sd["chosen"] else ""))
    out.append("")
    out.append("VERDICT: identical traces" if clean
               else "VERDICT: traces diverge -- see above")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("stamp", nargs="?", default=None)
    ap.add_argument("other", nargs="?", default=None,
                    help="a second soak stamp; comparing two recordings of "
                         "the same seed is the P1.5 acceptance shape")
    ap.add_argument("--run", type=int, default=None)
    args = ap.parse_args(argv)

    stamp = args.stamp or latest_stamp()
    if stamp is None:
        raise SystemExit(f"no soak logs under {LOG_DIR}")
    if args.other:
        print(render_compare(stamp, args.other, args.run))
    else:
        print(render(stamp, args.run))
    return 0


if __name__ == "__main__":
    sys.exit(main())
