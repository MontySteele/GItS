"""`X9READ-S1` — the GRADER for Kokomi's charge reads per turn (`EB-78` (2)).

THE REGISTRATION IS ELSEWHERE AND CAME FIRST:
`review/active/charge-reads-per-turn-registration-2026-08-13.md` §5, drafted
under R212(2) and committed before any run, revised 2026-08-30 on the pair
review's correction and COUNTERSIGNED under R233. This module PREDICTS
NOTHING. Every threshold it grades against is quoted from §5.3 / §5.4 as a
literal below, so a reader can check a grade without leaving the file and so
no threshold can drift after a number is seen (R101b).

WHAT IT READS. Two events the instrument already emits
(`tier0/engine/resources.py:270`, `tier0/engine/combat.py:1049`) — nothing is
added to either emit by this file, and the engine is untouched:

  `charge_read`        one per resolved read: `kind`, `card`, `bank`, `turn`.
  `charge_reads_turn`  once per COMPLETED player turn: `total`, `by_source`.
                       Every event also carries `turn` from `state.emit`.

THE TWO JOBS THE RAW STREAM KEEPS, and why the shares do not use it (§5.3's
revision note). §2.1's truncation drops the turn that killed the last enemy,
and that turn's attack-side reads still land in the RAW stream while its
`kurage_pulse` never does — the pulse rides `turn_close` behind the same door
as the sample. A share taken off the raw stream therefore over-states the
repeatable side by an unknown amount. So `X4`, `X5` and `W9`'s Limb A sum
`charge_reads_turn`.`by_source` over completed turns only; the raw stream is
used for exactly two things — `X7`'s truncation cross-check and `X6`'s
play-boundary segmentation.

`X6`'s SEGMENTATION, which the instrument does not do for the grader (§5.3,
`X6`'s data source). A segment OPENS at a `play` event and CLOSES at the next
`play`, at the turn's `charge_reads_turn`, at the next `turn_open`, or at the
end of the fight's log. Reads are attributed to the open segment. It is
**NOT** keyed on `card` id: a card played twice in one turn would collide, and
the whole quantity `X6` grades is a per-PLAY one. The end-of-turn
`kurage_pulse` lands in the last play's segment and cannot disturb the count,
because a double read is `garment` AND `bonus_formula` together and the pulse
is neither.

WHAT IT MOVES: nothing. No constant, no drafter dial, no policy branch, no
engine rule. Reduction only; every function here is pure over a log.

NOT A BALANCE READ (R213 B / R215 B, Guardrail-7). Counts only. The pilot does
not steer toward a Garment turn, so `X4` and `X6` are FLOORS on what a player
who plays toward the double read would produce (§5.3 blind spot 2).
"""

from __future__ import annotations

import statistics
from collections import Counter
from dataclasses import dataclass, field

from tier05 import stats

#: The three counted sources, exactly as `note_charge_read` tags them (§2).
READ_KINDS = ("garment", "kurage_pulse", "bonus_formula")

#: "Repeatable" is the WORKSHOP's word, not a pick made here (§5.4):
#: `kurage_pulse` is once per turn and workshop §3.2 calls that frequency
#: "already a natural bound"; the other two are not bounded within the turn.
REPEATABLE_KINDS = ("garment", "bonus_formula")

#: §5.1's derived ceiling. Reported as `W9`'s SEVERITY INDICATOR only — it
#: gates nothing (§5.4, revised 2026-08-30).
DERIVED_CEILING = 5


def _is_attack(card_id: str | None) -> bool:
    """Sheet read of `Card.type`, never a read of play.

    False rather than a raise on an id no index knows: an unresolvable id is a
    fact about the seam, not a reason to lose a run's observations. It can only
    make `X6`'s denominator SMALLER, which is the direction that makes the
    graded share LARGER — i.e. it cannot flatter the prediction.
    """
    if not card_id:
        return False
    from tier0.content import loader
    try:
        card = loader.peek_card(card_id)
    except KeyError:
        return False
    return bool(card is not None and card.type == "attack")


@dataclass
class ChargeTrace:
    """One combat's charge reads, reduced.

    Taken at `model._RunCtx._record_traces`, because `state.log` does not
    survive onto the `RunResult` and anything not reduced there is
    unrecoverable.
    """

    act: int = 0
    #: One row per COMPLETED player turn: `{"turn", "total", "by_source"}`.
    turns: list[dict] = field(default_factory=list)
    #: Every `charge_read` event, by kind — INCLUDING the truncated final
    #: turn's. This is `X7`'s cross-check and nothing else.
    raw_reads: Counter = field(default_factory=Counter)
    #: Bank size at read time, by kind (`R3` — a SIZE, graded by nothing).
    banks: dict = field(default_factory=dict)
    attack_plays: int = 0
    double_plays: int = 0
    #: `turn_open` events — the denominator `R4`'s dropped-turn count needs.
    turns_opened: int = 0


def trace(log: list[dict], act_i: int = 0) -> ChargeTrace:
    """One combat's reduction. Pure; reads the log and nothing else."""
    out = ChargeTrace(act=act_i)
    seg_open = False
    seg_attack = False
    seg_kinds: set[str] = set()

    def close_segment() -> None:
        nonlocal seg_open, seg_attack, seg_kinds
        if seg_open and seg_attack:
            out.attack_plays += 1
            if all(k in seg_kinds for k in REPEATABLE_KINDS):
                out.double_plays += 1
        seg_open = False
        seg_attack = False
        seg_kinds = set()

    for ev in log:
        name = ev.get("event")
        if name == "turn_open":
            close_segment()
            out.turns_opened += 1
        elif name == "play":
            close_segment()
            seg_open = True
            seg_attack = _is_attack(ev.get("card"))
        elif name == "charge_read":
            kind = str(ev.get("kind"))
            out.raw_reads[kind] += 1
            out.banks.setdefault(kind, []).append(int(ev.get("bank", 0)))
            if seg_open:
                seg_kinds.add(kind)
        elif name == "charge_reads_turn":
            close_segment()
            out.turns.append({
                "turn": int(ev.get("turn", 0)),
                "total": int(ev.get("total", 0)),
                "by_source": dict(ev.get("by_source") or {}),
            })
    close_segment()
    return out


def _share(n: float, d: float) -> float:
    return (n / d) if d else 0.0


def _points(values: list[int]) -> dict:
    """§3's Q1 set in full — `mean / p50 / p90 / p99 / max` (`R1`)."""
    if not values:
        return {"n": 0, "mean": 0.0, "p50": 0.0, "p90": 0.0, "p99": 0.0,
                "max": 0}
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "p50": stats.percentile(values, 0.50),
        "p90": stats.percentile(values, 0.90),
        "p99": stats.percentile(values, 0.99),
        "max": max(values),
    }


def aggregate(traces: list[ChargeTrace]) -> dict:
    """Pooled over TURNS, not over combats.

    A per-combat average of per-combat percentiles is not a percentile of
    anything, and the distribution is the whole question — so the samples are
    pooled and the statistic is taken once, over the pool.
    """
    turns = [t for tr in traces for t in tr.turns]
    totals = [t["total"] for t in turns]

    by_source: Counter = Counter()
    for t in turns:
        for kind, n in t["by_source"].items():
            by_source[str(kind)] += int(n)
    completed_reads = sum(by_source.values())

    raw: Counter = Counter()
    banks: dict[str, list[int]] = {}
    for tr in traces:
        raw.update(tr.raw_reads)
        for kind, vals in tr.banks.items():
            banks.setdefault(kind, []).extend(vals)

    # `X7`: turns 1-5 against turns 6+, on the turn number the emit carries.
    early = [t["total"] for t in turns if t["turn"] <= 5]
    late = [t["total"] for t in turns if t["turn"] >= 6]

    per_kind = {
        kind: _points([t["by_source"].get(kind, 0) for t in turns])
        for kind in READ_KINDS
    }
    by_act: dict[str, dict] = {}
    for act in sorted({tr.act for tr in traces}):
        rows = [t for tr in traces if tr.act == act for t in tr.turns]
        act_early = [r["total"] for r in rows if r["turn"] <= 5]
        act_late = [r["total"] for r in rows if r["turn"] >= 6]
        by_act[str(act)] = {
            "turns": len(rows),
            "mean": (statistics.mean([r["total"] for r in rows])
                     if rows else 0.0),
            "early_mean": statistics.mean(act_early) if act_early else 0.0,
            "late_mean": statistics.mean(act_late) if act_late else 0.0,
        }

    attack_plays = sum(tr.attack_plays for tr in traces)
    double_plays = sum(tr.double_plays for tr in traces)
    turns_opened = sum(tr.turns_opened for tr in traces)

    return {
        "combats": len(traces),
        # -- X1 / X2 / X3 and R1's full point set -------------------------
        "turns": len(turns),
        "levels": _points(totals),
        # -- X4 / X5 / W9 Limb A: COMPLETED turns only (§5.3's revision) ---
        "completed_reads": completed_reads,
        "by_source": dict(by_source),
        "share": {k: _share(by_source.get(k, 0), completed_reads)
                  for k in READ_KINDS},
        "repeatable_share": _share(
            sum(by_source.get(k, 0) for k in REPEATABLE_KINDS),
            completed_reads),
        # A composition tipped by an absent summon must be visible on its
        # face (§5.4, revised): the pulse share and the pulseless turns.
        "turns_without_pulse": sum(
            1 for t in turns if not t["by_source"].get("kurage_pulse")),
        # -- X6 ----------------------------------------------------------
        "attack_plays": attack_plays,
        "double_plays": double_plays,
        "double_share": _share(double_plays, attack_plays),
        # -- X7 ----------------------------------------------------------
        "early_turns": len(early),
        "late_turns": len(late),
        "early_mean": statistics.mean(early) if early else 0.0,
        "late_mean": statistics.mean(late) if late else 0.0,
        "gap": ((statistics.mean(late) if late else 0.0)
                - (statistics.mean(early) if early else 0.0)),
        # -- R2 / R3 / R4, recorded and graded by nothing ------------------
        "per_kind": per_kind,
        "raw_reads": dict(raw),
        "raw_total": sum(raw.values()),
        "bank_median": {k: (statistics.median(v) if v else 0.0)
                        for k, v in sorted(banks.items())},
        "bank_mean": {k: (statistics.mean(v) if v else 0.0)
                      for k, v in sorted(banks.items())},
        "bank_max": {k: (max(v) if v else 0) for k, v in sorted(banks.items())},
        "turns_opened": turns_opened,
        "turns_dropped": max(0, turns_opened - len(turns)),
        "reads_dropped": max(0, sum(raw.values()) - completed_reads),
        "by_act": by_act,
    }


# --- the grader --------------------------------------------------------------
#
# §5.3's seven falsifiers, quoted as literals. Nothing here reads a field the
# instrument does not emit, and nothing is added at grading time.

def grade(m: dict) -> list[dict]:
    """The seven slots, against §5.3's thresholds and no others."""
    out: list[dict] = []
    turns = m["turns"]
    lv = m["levels"]

    # X1 -- >= 1.0 and < 2.0 PREDICTED; 2.0 to < 3.0 SPLIT; >= 3.0 or < 1.0
    #       MISS. UNREACHED under 5,000 sampled player turns.
    mean = lv["mean"]
    g = ("UNREACHED" if turns < 5000
         else "PREDICTED" if 1.0 <= mean < 2.0
         else "SPLIT" if 2.0 <= mean < 3.0 else "MISS")
    out.append({"slot": "X1", "grade": g,
                "read": f"mean {mean:.3f} reads per turn over {turns} "
                        f"sampled player turns",
                "threshold": ">= 1.0 and < 2.0 PREDICTED; 2.0 to < 3.0 SPLIT; "
                             ">= 3.0 or < 1.0 MISS"})

    # X2 -- p90 <= 3 PREDICTED; 4 to 5 SPLIT; > 5 MISS. The percentile is
    # tier05.stats' linear interpolation (the repo's ONE convention), so a
    # value can land strictly between 3 and 4; the partition the slot writes
    # is honoured by reading "4 to 5" as the interval above 3 up to 5.
    p90 = lv["p90"]
    g = ("UNREACHED" if turns < 5000
         else "PREDICTED" if p90 <= 3
         else "SPLIT" if p90 <= 5 else "MISS")
    out.append({"slot": "X2", "grade": g,
                "read": f"p90 {p90:.2f} reads per turn",
                "threshold": "<= 3 PREDICTED; 4 to 5 SPLIT; > 5 MISS"})

    # X3 -- max <= 8 PREDICTED; 9 to 13 SPLIT; > 13 MISS. Never UNREACHED:
    # a max is defined on any non-empty sample.
    mx = lv["max"]
    g = ("PREDICTED" if mx <= 8 else "SPLIT" if mx <= 13 else "MISS")
    out.append({"slot": "X3", "grade": g,
                "read": f"max {mx} reads in one turn",
                "threshold": "<= 8 PREDICTED; 9 to 13 SPLIT; > 13 MISS"})

    # X4 -- garment share < 50% PREDICTED; 50% to 65% SPLIT; > 65% MISS.
    #       UNREACHED under 5,000 reads summed from completed turns.
    reads = m["completed_reads"]
    s = m["share"]["garment"]
    g = ("UNREACHED" if reads < 5000
         else "PREDICTED" if s < 0.50
         else "SPLIT" if s <= 0.65 else "MISS")
    out.append({"slot": "X4", "grade": g,
                "read": f"garment {s * 100:.2f}% of {reads} completed-turn "
                        f"reads",
                "threshold": "< 50% PREDICTED; 50-65% SPLIT; > 65% MISS"})

    # X5 -- bonus_formula share < 15% PREDICTED; 15% to 30% SPLIT; > 30% MISS.
    s = m["share"]["bonus_formula"]
    g = ("UNREACHED" if reads < 5000
         else "PREDICTED" if s < 0.15
         else "SPLIT" if s <= 0.30 else "MISS")
    out.append({"slot": "X5", "grade": g,
                "read": f"bonus_formula {s * 100:.2f}% of {reads} "
                        f"completed-turn reads",
                "threshold": "< 15% PREDICTED; 15-30% SPLIT; > 30% MISS"})

    # X6 -- double read < 5% of attack plays PREDICTED; 5% to 15% SPLIT;
    #       > 15% MISS. UNREACHED under 1,000 attack plays.
    plays = m["attack_plays"]
    s = m["double_share"]
    g = ("UNREACHED" if plays < 1000
         else "PREDICTED" if s < 0.05
         else "SPLIT" if s <= 0.15 else "MISS")
    out.append({"slot": "X6", "grade": g,
                "read": f"{m['double_plays']} of {plays} attack plays carry "
                        f"both reads ({s * 100:.2f}%)",
                "threshold": "< 5% PREDICTED; 5-15% SPLIT; > 15% MISS"})

    # X7 -- rises and gap < 1.0 PREDICTED; rises and gap >= 1.0 SPLIT;
    #       flat or falls MISS. UNREACHED under 2,000 turns at turn >= 6.
    gap = m["gap"]
    g = ("UNREACHED" if m["late_turns"] < 2000
         else "PREDICTED" if 0 < gap < 1.0
         else "SPLIT" if gap >= 1.0 else "MISS")
    out.append({"slot": "X7", "grade": g,
                "read": f"turns 1-5 mean {m['early_mean']:.3f} "
                        f"(n={m['early_turns']}) -> turns 6+ mean "
                        f"{m['late_mean']:.3f} (n={m['late_turns']}); gap "
                        f"{gap:+.3f}",
                "threshold": "rises and gap < 1.0 PREDICTED; rises and gap "
                             ">= 1.0 SPLIT; flat or falls MISS"})
    return out


def evaluate_w9(m: dict) -> dict:
    """§5.4's watch trigger. Two limbs, EITHER of which fires alone.

    Limb A: `garment` + `bonus_formula` > 50% of completed-turn reads.
    Limb B: the `X6` double-read share > 50% of attack plays.

    The `p50` is the SEVERITY INDICATOR and gates nothing (revised
    2026-08-30) — it labels a firing loud (`p50` > 5) or quiet.
    """
    limb_a = m["repeatable_share"] > 0.50
    limb_b = m["double_share"] > 0.50
    p50 = m["levels"]["p50"]
    return {
        "fired": bool(limb_a or limb_b),
        "limb_a": limb_a,
        "limb_b": limb_b,
        "repeatable_share": m["repeatable_share"],
        "double_share": m["double_share"],
        # The MARGIN, recorded whether or not it fires: how far each limb sat
        # from its own 50%.
        "limb_a_margin": m["repeatable_share"] - 0.50,
        "limb_b_margin": m["double_share"] - 0.50,
        "p50": p50,
        "severity": ("loud" if p50 > DERIVED_CEILING else "quiet"),
        # Named beside any firing so a composition tipped by an absent summon
        # is visible on its face.
        "kurage_pulse_share": m["share"]["kurage_pulse"],
        "turns_without_pulse": m["turns_without_pulse"],
    }
