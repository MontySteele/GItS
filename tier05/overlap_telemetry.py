"""C4: the carry-card overlap watch (Neap Tide addendum, 2026-07-26).

Reads the deck and the combat log; changes nothing and gates nothing. R14:
this is a diagnostic, and no acceptance target lives here.

WHY THIS EXISTS, AND WHY IT LANDS BEFORE PLAYTEST THREE IS INTERPRETED.

Playtest two was carried by a PAIR of cards, not by one -- and that was only
visible in hindsight, from a hand's report, because nothing in the instrument
could see two cards at once. Every column the sim owns is per-card (pick rate,
play rate) or per-run (win rate). A card that is fine alone and dominant
alongside one specific other card reads as "fine" in both.

Three cards are on this watch, and each is here for a stated reason:

  before_sun_and_moon   G2 ratified it STACKING over an objection. It moves a
                        COEFFICIENT on a bank that is uncapped and never spent
                        (R80), so two copies is not "twice a card" -- at the
                        landed x3 one upgraded copy is already x5. The
                        objection was heard and overruled on the grounds that
                        draft dilution self-corrects at full roster. That is a
                        prediction, and this is the column that grades it.
  honor_guard           R75 made it a 0-cost Rare with Exhaust. A 0-cost card
                        is a card that never competes for a turn, so its
                        drafted-to-played gap is the whole question.
  epiphany_of_the_deep  "Song of Pearls" -- the priest/assist Rare payoff, and
                        the other end of every deck that wants the amp.

WHAT IS MEASURED, fixed here so no later run can redefine it mid-sweep:

- draft rate          share of runs whose FINAL deck holds >= 1 copy. Final
                      deck, not offers: a card taken and later removed did not
                      carry the run.
- copies              mean copies among runs that drafted it, and the max. The
                      stacking question is a COPIES question and a mean of
                      0/1/2 hides the 2s.
- co-draft rate       share of runs holding >= 1 of BOTH, per pair. Reported
                      against the INDEPENDENCE baseline (p_a * p_b) rather than
                      raw, because a high co-draft rate between two commonly
                      drafted cards is arithmetic, not a finding. What would be
                      a finding is co-drafting ABOVE chance -- decks seeking
                      the pair out.
- win when both       win rate on runs holding both, next to win-when-either
                      and win-when-neither. Three cells, because "both is
                      strong" means nothing without knowing what one is worth.
- play rate           mean plays per run among runs that drafted it. This is
                      the drafted-vs-used gap, and it is the reason the trace
                      half of this module exists at all: the deck tells you
                      what was taken and only the log tells you what was cast.

SMALL-CELL DISCIPLINE. A rare card in a 600-run cell can be drafted in a
handful of runs, and a win rate over 7 runs is noise wearing a percent sign.
Every derived rate is reported WITH its denominator, and `format_block` marks
a cell `n<MIN_CELL` instead of printing a number it cannot support. No
threshold, no gate -- just a refusal to render a number that would be read as
one.

WHAT THIS INSTRUMENT CANNOT DO, MEASURED AND STATED UP FRONT. The `win both`
column is NOT gradeable in the sim's current world, and pretending otherwise
would be worse than not printing it. Kokomi wins ~3% of runs and the pairs
co-draft at ~1-2%, so the win cell holds ~0.02-0.06% of the sample: 2000
commander runs put 36 runs in the largest pair cell, all losses, which is
indistinguishable from the 3% base rate. Separating a pair effect from noise
there needs a cell in the tens of thousands. The DRAFT and PLAY columns ARE
gradeable today and answer real questions; the WIN column is a placeholder
that becomes meaningful only if her win rate rises. This is precisely the
division of labour playtest three exists for -- a hand can tell you the pair
felt inevitable after two drafts, and no amount of runs at a 3% win rate can.

FIRST READING (2000 runs, seed 11, commander; 400 each priest/assist), for
whoever compares against it later:
  * honor_guard 9.8% draft, 2.89 plays/run when held, 8 of 196 drafted runs
    never cast it. epiphany_of_the_deep 3.6% draft, 0.25 plays/run, 56 of 72
    never cast it. R75 made honor_guard a 0-cost, and a 0-cost card never
    competes for a turn -- that gap is the ruling showing up in a column.
  * every pair that exists at all has LIFT above 1 (1.69 to 3.61). Decks do
    seek these together. The rates are small because the cards are Rare and
    Uncommon; the lift says the co-draft is not chance.
  * before_sun_and_moon reaches 3 copies. G2's stacking is not theoretical.
  * honor_guard is drafted 0.0% in priest and assist cells -- it is
    `archetypes: [commander]`, so its columns are structurally empty
    elsewhere. Read this table PER PLAN or the zeroes will read as a finding.

RELATED, AND NOT THE SAME INSTRUMENT. kurage_telemetry also prints a block
labelled C4 ("Before Sun and Moon overlap"). That one is measured at PULSE
time -- what the amp was worth when the jellyfish fired. This one is measured
at DECK and PLAY time. They answer different halves of the same ratification
and neither replaces the other.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

# The watch list. A curated list, not a rule: adding a card here is a decision
# about what playtest three is being asked to look at, and it should be made
# on purpose. Order is the report order.
WATCHED = ("before_sun_and_moon", "honor_guard", "epiphany_of_the_deep")

# Below this many runs in a cell, the rate is not reported. Chosen as the point
# where a single run moves the number by more than 5pp; it is a rendering rule,
# not an acceptance threshold (R14).
MIN_CELL = 20


@dataclass
class OverlapTrace:
    """One combat's plays of the watched cards."""

    plays: dict[str, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(self.plays.values())


def trace(log: list[dict]) -> OverlapTrace:
    """Watched-card plays in one fight.

    Taken from the log rather than from a counter on the player because the
    fight log does not survive onto the RunResult -- only the reduced trace
    does, the same reason burst_telemetry and kurage_telemetry are shaped this
    way. Powers are counted as plays: `before_sun_and_moon` is a Power, so it
    is cast exactly once per copy per combat, and that IS its play rate.
    """
    out = OverlapTrace()
    for ev in log:
        if ev.get("event") != "play":
            continue
        card = ev.get("card")
        if card in WATCHED:
            out.plays[card] = out.plays.get(card, 0) + 1
    return out


def _copies(deck_ids: list[str], card: str) -> int:
    return sum(1 for c in deck_ids if c == card)


def aggregate(results: list) -> dict:
    """RunResults -> the C4 table.

    Takes whole RunResults rather than pre-extracted pieces because the
    question is a JOIN: the deck says what was drafted, the traces say what was
    played, and `won` says what it was worth. Splitting them into three
    aggregators is how the pair became invisible in the first place.
    """
    runs = len(results)
    if not runs:
        return {}

    held: dict[str, list[bool]] = {c: [] for c in WATCHED}
    copies: dict[str, list[int]] = {c: [] for c in WATCHED}
    plays: dict[str, list[int]] = {c: [] for c in WATCHED}
    wins = [bool(r.won) for r in results]

    # STRICT attribute access, not getattr-with-default. The runner already
    # reads kurage_traces this way on purpose: a default here would swallow a
    # real RunResult regression -- the field silently disappearing would render
    # as "nobody played these cards", which is a legible and completely wrong
    # answer. A missing field should be an AttributeError, loudly.
    for r in results:
        deck = list(r.deck_ids or [])
        per_card: dict[str, int] = {}
        for _act, t in (r.overlap_traces or []):
            for card, n in t.plays.items():
                per_card[card] = per_card.get(card, 0) + n
        for card in WATCHED:
            n = _copies(deck, card)
            copies[card].append(n)
            held[card].append(n > 0)
            plays[card].append(per_card.get(card, 0))

    def rate(flags: list[bool]) -> float:
        return sum(flags) / len(flags) if flags else 0.0

    def win_rate(mask: list[bool]) -> tuple[float, int]:
        picked = [w for w, m in zip(wins, mask) if m]
        if not picked:
            return 0.0, 0
        return sum(picked) / len(picked), len(picked)

    cards = {}
    for card in WATCHED:
        drafted = [i for i, h in enumerate(held[card]) if h]
        held_copies = [copies[card][i] for i in drafted]
        held_plays = [plays[card][i] for i in drafted]
        w, n = win_rate(held[card])
        cards[card] = {
            "draft_rate": rate(held[card]),
            "drafted_runs": len(drafted),
            "mean_copies": (sum(held_copies) / len(held_copies)
                            if held_copies else 0.0),
            "max_copies": max(held_copies) if held_copies else 0,
            "multi_copy_runs": sum(1 for c in held_copies if c > 1),
            "mean_plays": (sum(held_plays) / len(held_plays)
                           if held_plays else 0.0),
            "never_played_runs": sum(1 for p in held_plays if p == 0),
            "win_when_held": w,
            "win_when_held_n": n,
        }

    pairs = {}
    for a, b in combinations(WATCHED, 2):
        both = [ha and hb for ha, hb in zip(held[a], held[b])]
        either = [ha or hb for ha, hb in zip(held[a], held[b])]
        neither = [not e for e in either]
        only = [e and not bo for e, bo in zip(either, both)]
        w_both, n_both = win_rate(both)
        w_only, n_only = win_rate(only)
        w_neither, n_neither = win_rate(neither)
        expected = cards[a]["draft_rate"] * cards[b]["draft_rate"]
        pairs[(a, b)] = {
            "co_draft_rate": rate(both),
            # Observed over expected-if-independent. 1.0 means the pair appears
            # exactly as often as two unrelated cards of those rates would;
            # above 1.0 means decks are seeking it. This is the number to read,
            # not the raw rate.
            "lift": (rate(both) / expected) if expected else 0.0,
            "win_both": w_both, "n_both": n_both,
            "win_one": w_only, "n_one": n_only,
            "win_neither": w_neither, "n_neither": n_neither,
        }

    return {"runs": runs, "cards": cards, "pairs": pairs}


def format_block(agg: dict) -> str:
    """Report-only rendering. '' when no watched card was ever drafted, so
    every non-Kokomi character prints nothing rather than a wall of zeroes."""
    if not agg or not any(c["drafted_runs"] for c in agg["cards"].values()):
        return ""

    def pct(value: float, n: int) -> str:
        return f"{value * 100:5.1f}" if n >= MIN_CELL else f"  n<{MIN_CELL}"

    lines = [f"  C4 overlap watch (report-only, R14; {agg['runs']} runs)",
             f"    {'card':22} {'draft%':>7} {'copies':>7} {'max':>4} "
             f"{'2+':>4} {'plays':>6} {'unplayed':>9} {'win%|held':>10}"]
    for card, c in agg["cards"].items():
        lines.append(
            f"    {card:22} {c['draft_rate'] * 100:7.1f} "
            f"{c['mean_copies']:7.2f} {c['max_copies']:4d} "
            f"{c['multi_copy_runs']:4d} {c['mean_plays']:6.2f} "
            f"{c['never_played_runs']:9d} "
            f"{pct(c['win_when_held'], c['win_when_held_n']):>10}")

    lines.append(f"    {'pair':45} {'co%':>6} {'lift':>6} "
                 f"{'win both':>9} {'win one':>8} {'win none':>9}")
    for (a, b), p in agg["pairs"].items():
        lines.append(
            f"    {a + ' + ' + b:45} {p['co_draft_rate'] * 100:6.1f} "
            f"{p['lift']:6.2f} {pct(p['win_both'], p['n_both']):>9} "
            f"{pct(p['win_one'], p['n_one']):>8} "
            f"{pct(p['win_neither'], p['n_neither']):>9}")
    lines.append(f"    (lift = co-draft / independence baseline; "
                 f"cells under n={MIN_CELL} are withheld, not zero)")
    return "\n".join(lines)
