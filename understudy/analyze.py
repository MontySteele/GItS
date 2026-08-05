"""Read a Phase-0 decision log and print the M1/M2 numbers.

Deliberately dumb: it sums the log and says what it summed. Every derived
figure carries its denominator, because a `tokens/decision` or an `agreement`
number quoted without one is exactly what the AutoSlay correction was about.

    python -m understudy.analyze understudy/logs/phase0-<seed>.jsonl
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

# The conventional English-text ratio. Labelled everywhere it is used, because
# it is an estimate and the report must never let it read as a measurement.
CHARS_PER_TOKEN = 4.0


def load(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else None
    if path is None or not path.exists():
        print(f"usage: python -m understudy.analyze <log.jsonl>", file=sys.stderr)
        return 2
    rows = load(path)

    sessions = [r for r in rows if r.get("event") == "session_begin"]
    decisions = [r for r in rows if "mine" in r]
    auto = [r for r in decisions if r.get("auto")]
    mine = [r for r in decisions if not r.get("auto")]
    planned = [r for r in mine if r.get("plan_step", 0) > 0]
    read = [r for r in mine if r.get("state_chars", 0) > 0]

    print(f"log: {path.name}")
    if sessions:
        print(f"seed: {sessions[0].get('seed')}")
    print()
    print("=== VOLUME ===")
    print(f"log lines                     {len(rows)}")
    print(f"actions posted                {len(decisions)}")
    print(f"  mechanical (auto verb)      {len(auto)}")
    print(f"  LLM-issued                  {len(mine)}")
    print(f"    read a state first        {len(read)}")
    print(f"    later steps of a plan     {len(planned)}")
    floors = sorted({(r.get("act"), r.get("floor")) for r in decisions
                     if r.get("floor") is not None})
    print(f"floors traversed              {len(floors)}  {floors[:2]}..{floors[-1:]}")

    print()
    print("=== M1 (MEASUREMENT, marginal only) ===")
    sc = sum(r.get("state_chars", 0) for r in mine)
    wc = sum(r.get("why_chars", 0) for r in mine)
    n = max(1, len(read))
    print(f"state chars read              {sc}   ({sc / n:.0f} per read decision)")
    print(f"reasoning chars written       {wc}   ({wc / n:.0f} per read decision)")
    print(f"marginal chars / decision     {(sc + wc) / n:.0f}")
    print(f"ESTIMATED tokens / decision   {(sc + wc) / n / CHARS_PER_TOKEN:.0f}"
          f"   (at {CHARS_PER_TOKEN} chars/token; MARGINAL ONLY -- excludes the"
          f" conversation context re-read each turn, which is unobservable"
          f" from inside the harness and is the larger half)")
    walls = [r["wall_ms"] for r in mine if r.get("wall_ms")]
    if walls:
        walls.sort()
        print(f"wall ms / decision            median {walls[len(walls)//2]}, "
              f"mean {sum(walls)//len(walls)}")

    print()
    print("=== M2 (agreement, by category) ===")
    cat = collections.Counter()
    agree = collections.Counter()
    disagree = collections.Counter()
    nocf = collections.Counter()
    forced = 0
    for r in mine:
        c = r.get("category", "?")
        cat[c] += 1
        if r.get("agree") is True:
            agree[c] += 1
        elif r.get("agree") is False:
            disagree[c] += 1
        else:
            nocf[c] += 1
        notes = (r.get("policy_v0") or {}).get("notes") or {}
        if notes.get("n_options") == 1:
            forced += 1

    print(f"{'category':<14}{'total':>7}{'agree':>7}{'differ':>8}{'no cf':>7}"
          f"{'agree%':>9}")
    for c in sorted(cat):
        d = agree[c] + disagree[c]
        pct = f"{100 * agree[c] / d:.0f}%" if d else "-"
        print(f"{c:<14}{cat[c]:>7}{agree[c]:>7}{disagree[c]:>8}{nocf[c]:>7}{pct:>9}")
    tot_a, tot_d = sum(agree.values()), sum(disagree.values())
    den = tot_a + tot_d
    print(f"{'ALL SCORED':<14}{den:>7}{tot_a:>7}{tot_d:>8}{'':>7}"
          + (f"{100 * tot_a / den:.0f}%" if den else "-").rjust(9))
    print(f"\nof which forced (single-option map screens): {forced}")

    # INDEPENDENCE. Every play after the first in a turn is conditioned on my
    # earlier choice: once I diverge, policy_v0 is answering a state my own
    # play created, so the comparison stops being a test of the same question.
    # The turn-opening decisions are the ones where both arms genuinely face
    # the same board. Reported beside the raw rate, never instead of it.
    openers = []
    prev_ended = True
    for r in mine:
        if r.get("category") == "sequencing":
            if prev_ended:
                openers.append(r)
            prev_ended = r["mine"].get("action") == "end_turn"
        else:
            prev_ended = True
    oa = sum(1 for r in openers if r.get("agree") is True)
    od = sum(1 for r in openers if r.get("agree") is False)
    print()
    print("=== M2, turn-opening combat decisions only ===")
    print(f"comparisons {oa + od}, agree {oa}, differ {od}, "
          + (f"agree {100 * oa / (oa + od):.0f}%" if oa + od else "-"))
    print("(the subset where both arms face the same board; the 121 raw "
          "sequencing rows are NOT independent of each other)")

    print()
    print("=== disagreements, in order ===")
    for r in mine:
        if r.get("agree") is False:
            pv = r.get("policy_v0") or {}
            print(f"[{r['i']:>3}] a{r.get('act')}f{r.get('floor')} "
                  f"{r.get('category')}: mine={json.dumps(r['mine'])} "
                  f"policy={pv.get('label')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
