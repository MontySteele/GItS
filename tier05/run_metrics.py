"""Run-level metrics (spec §5, M5 slice): fragility is the point —
winrate, death-node heatmap, HP trajectory percentile bands. The A4 saga
proved fight-level metrics can't express "62 HP, reluctant defense";
these can.
"""

from __future__ import annotations

import math
import random
from collections import Counter

from tier0 import constants as C
from tier0.harness import metrics as t0_metrics
from tier05 import route, stats
from tier05.model import RunResult


# The two shared statistics (sim-hygiene sprint, 2026-07-29). This module
# defined the CANONICAL copy of both -- its linear-interpolation percentile is
# the convention tier05.stats standardised on -- so these are re-exported under
# their old private names rather than chased through every call site.
_percentile = stats.percentile
_wilson95 = stats.wilson95


def summarize_runs(results: list[RunResult]) -> dict:
    n = len(results)
    if n == 0:
        return {}
    wins = sum(r.won for r in results)
    deaths = Counter(r.death_node for r in results if r.death_node is not None)
    # §11: node_kinds is the path WALKED, so a run that died is short. Bands
    # and the heatmap are indexed by FLOOR, and every path visits exactly one
    # room per floor -- so the axis is MAP_FLOORS * n_acts, never results[0]'s
    # length (that would size the whole report off one unlucky run).
    n_nodes = C.MAP_FLOORS * max(1, results[0].n_acts)
    # HP trajectory bands: per node position, over runs that REACHED it.
    bands = []
    for pos in range(n_nodes):
        alive_here = [r.hp_by_node[pos] for r in results
                      if len(r.hp_by_node) > pos]
        if not alive_here:
            bands.append(None)
            continue
        bands.append({"p25": _percentile(alive_here, 0.25),
                      "p50": _percentile(alive_here, 0.50),
                      "p75": _percentile(alive_here, 0.75),
                      "reached": len(alive_here)})
    picks = sum(1 for r in results for d in r.decisions if d["picked"])
    screens = sum(len(r.decisions) for r in results)
    online = [r.time_to_online for r in results if r.time_to_online]
    return {
        "runs": n,
        "wins": wins,
        "winrate": wins / n,
        "winrate_wilson95": _wilson95(wins, n),
        "death_heatmap": dict(sorted(deaths.items())),
        "hp_bands": bands,
        "avg_final_deck": sum(len(r.deck_ids) for r in results) / n,
        # P5 (playtest sprint): the same average, split by outcome.
        # SURVIVORSHIP CHECK, observation only -- no rule reads it. The pooled
        # figure rides at/over DRAFT_DECK_SOFT_CAP, and that is ambiguous by
        # construction: a run that dies on floor 4 contributes a small deck it
        # never got to grow, so heavy decks and short runs push the mean in
        # opposite directions and can cancel. Splitting says which. Winners
        # bigger than losers means the cap is being ridden by runs that are
        # WORKING; losers bigger means bloat is a cause of death.
        "avg_final_deck_won": (
            sum(len(r.deck_ids) for r in results if r.won) / max(1, wins)
            if wins else None),
        "avg_final_deck_lost": (
            sum(len(r.deck_ids) for r in results if not r.won) / (n - wins)
            if n - wins else None),
        "pick_rate": picks / max(1, screens),
        "regretted_decisions": sum(r.regret_samples for r in results),
        "median_time_to_online": (sorted(online)[len(online) // 2]
                                  if online else None),
        "online_rate": len(online) / n,
        "act_funnel": act_funnel(results),      # §10.6 (len 1 at --acts 1)
        "route": route_profile(results),        # §11
    }


def route_profile(results: list[RunResult]) -> dict:
    """§11 acceptance instrument. Reports the elite-count DISTRIBUTION and how
    it moves with arrival HP, because the target (median ~2.5, range 1-4) is
    only half the claim -- a policy that always takes exactly two hits the
    median and is still wrong. Also reports the walked composition, so a route
    policy that quietly stops visiting shops is visible.

    Elites are counted PER ACT, which is the unit the target is stated in."""
    if not results:
        return {}
    per_act, comp = [], Counter()
    for r in results:
        for a in range(max(1, r.n_acts)):
            seg = r.node_kinds[a * C.MAP_FLOORS:(a + 1) * C.MAP_FLOORS]
            if len(seg) == C.MAP_FLOORS:        # only acts actually completed
                per_act.append(sum(1 for k in seg if k == "E"))
        comp.update(r.node_kinds)
    n_runs = len(results)
    dist = Counter(per_act)
    # Does the count respond to run state? Split completed acts by whether the
    # run was above or below half HP entering them.
    healthy, hurt = [], []
    for r in results:
        for a in range(max(1, r.n_acts)):
            seg = r.node_kinds[a * C.MAP_FLOORS:(a + 1) * C.MAP_FLOORS]
            if len(seg) < C.MAP_FLOORS:
                continue
            start = a * C.MAP_FLOORS
            hp_in = r.hp_by_node[start] if len(r.hp_by_node) > start else 0
            (healthy if hp_in and hp_in > 0.5 * max(r.hp_by_node or [1])
             else hurt).append(sum(1 for k in seg if k == "E"))
    return {
        "acts_measured": len(per_act),
        "elites_per_act_mean": (sum(per_act) / len(per_act)) if per_act else 0.0,
        "elites_per_act_median": (sorted(per_act)[len(per_act) // 2]
                                  if per_act else None),
        "elites_distribution": dict(sorted(dist.items())),
        "in_target_band": (sum(v for k, v in dist.items() if 1 <= k <= 4)
                           / len(per_act)) if per_act else 0.0,
        "elites_when_healthy": (sum(healthy) / len(healthy)) if healthy else None,
        "elites_when_hurt": (sum(hurt) / len(hurt)) if hurt else None,
        "nodes_per_run": {k: round(v / n_runs, 2)
                          for k, v in sorted(comp.items())},
        "events_seen_per_run": round(
            sum(len(r.events) for r in results) / n_runs, 2),
        "event_options": dict(Counter(
            f"{e['event']}:{e['option']}" for r in results
            for e in r.events).most_common(8)),
        "regret": pooled_route_regret(results),      # EB-16w
    }


def pooled_route_regret(results: list[RunResult]) -> dict:
    """The route twin of `summarize_runs`' `regretted_decisions`: every act of
    every run's `route_regret` output, pooled (EB-16w).

    `RunResult.route_regret` holds ONE sampler dict per act, because a run
    walks one map per act and the sampler re-plans within a map. Pooling is
    additive on the counts and sample-weighted on `mean_regret`.

    NO POOLED PERCENTILES. p50/p90 are not recoverable from per-act summaries,
    and inventing them by averaging act medians would produce a number that
    looks like a distribution read and is not one. A caller that needs the
    pooled distribution takes the gaps themselves off `route_decisions`, via
    `route_regret_gaps` -- that is what `tools/regret_distribution.py` does
    (EB-72), and it is the only surface in the tree that prints them.
    `max_regret` pools honestly (a max of maxes is a max) and is reported."""
    per_act = [d for r in results for d in r.route_regret]
    if not per_act:
        return {}
    sampled = sum(d["sampled"] for d in per_act)
    return {
        "acts_sampled": len(per_act),
        "decisions": sum(d["decisions"] for d in per_act),
        "forced": sum(d["forced"] for d in per_act),
        "sampled": sampled,
        "regretted": sum(d["regretted"] for d in per_act),
        "regret_rate": (sum(d["regretted"] for d in per_act) / sampled
                        if sampled else 0.0),
        "mean_regret": (sum(d["mean_regret"] * d["sampled"] for d in per_act)
                        / sampled) if sampled else 0.0,
        "max_regret": max(d["max_regret"] for d in per_act),
        "margin": ROUTE_REGRET_MARGIN,   # uncalibrated; see its comment
    }


# --- route_regret (§4.2's third countermeasure) -----------------------------
#
# UNCALIBRATED, AND KNOWN TO BE (EB-16w, 2026-08-07). A full point of
# hindsight advantage, the same bar `draft_regret` sets -- but that bar is
# itself a hardcoded literal in `draft.py` (the `+ 1.0` at the regret
# comparison), pinned by a mutation-audit test (MEDIUM-11,
# test_pin_tier05_draft.py) and never derived from a measurement or a ruling.
# There is therefore NO mechanical calibration procedure to copy: this value is
# a literal analogy of a literal, and EB-16w's "calibrate it" half stays open
# until either a pre-registered measurement or a [USER] ruling sets it.
# The units are not even the same -- a draft score is one card's worth of
# printed damage/Block, a path value is a sum of room `want`s over sixteen
# floors -- so a point is a much smaller relative gap here.
# READ THE DISTRIBUTION, NOT THE RATE, until that is settled: `mean_regret`,
# `p50/p90_regret` and `max_regret` are margin-free and are the reportable
# numbers; `regretted` / `regret_rate` are the only two keys this threshold
# touches, and they exist for symmetry with the drafter.
# R164 (2026-08-10) ruled the shape of the settlement: PRE-REGISTER the
# measurement, do NOT ratify 1.0. The printer that made a registration
# possible is `tools/regret_distribution.py` and the packet is
# `review/active/regret-margin-registration-2026-08-12.md` (EB-72). Neither
# derives this number; both are careful not to.
ROUTE_REGRET_MARGIN = 1.0
# The sample rate is homed in tier0/constants.py beside its draft twin
# (EB-16w), where the reason for the 1.0 and the no-version-bump reading are
# written down. Re-exported under the module name it shipped with so callers
# and tests that reach for `run_metrics.ROUTE_REGRET_SAMPLE` keep working.
ROUTE_REGRET_SAMPLE = C.ROUTE_REGRET_SAMPLE


def route_regret_gaps(rng: random.Random, act_map, decisions: list[dict],
                      hindsight: route.RouteState, policy_name: str,
                      sample: float = C.ROUTE_REGRET_SAMPLE
                      ) -> tuple[list[float], int]:
    """The RAW gap sample behind `route_regret`, plus the forced-floor count.

    Split out (EB-72) so a caller that needs the POOLED distribution can have
    the gaps themselves. `pooled_route_regret` refuses to invent p50/p90 from
    per-act summaries and says so in its docstring -- correctly, because a
    median of medians is not a median -- and its advice to such a caller is to
    "sample the gaps itself off `route_decisions`". That advice used to mean
    re-implementing the loop below, which is exactly how two definitions of one
    number get into a repo. There is one loop, here, and `route_regret` is a
    summary OF it.

    NOTHING HERE READS A MARGIN. The gap sample is margin-free by construction:
    the threshold enters one line later, in `route_regret`, and only to count
    `regretted` / `regret_rate`. That separation is the whole reason this
    function exists as its own name -- under R164 the margin is not ratified,
    so the quotable read has to be reachable without touching it.

    Returns `(gaps, forced)`. `gaps` has one entry per SAMPLED forked decision,
    in walk order, zeros included: a decision the policy got right in hindsight
    is a 0.0 in the sample, not an absence from it, and dropping those would
    turn every percentile into a percentile of the regrets rather than of the
    decisions.
    """
    gaps: list[float] = []
    forced = 0
    for d in decisions:
        options = d["options"]
        if len(options) < 2:
            forced += 1
            continue
        if rng.random() >= sample:
            continue
        picked = d["picked"]
        taken = route.path_value(act_map, picked, policy_name, hindsight)[0]
        best_alt = max(route.path_value(act_map, r, policy_name, hindsight)[0]
                       for r in options if r.id != picked.id)
        gaps.append(max(0.0, best_alt - taken))
    return gaps, forced


def route_regret(rng: random.Random, act_map, decisions: list[dict],
                 hindsight: route.RouteState, policy_name: str,
                 sample: float = C.ROUTE_REGRET_SAMPLE,
                 margin: float = ROUTE_REGRET_MARGIN) -> dict:
    """The road not taken, re-priced in hindsight (research §4.2).

    `decisions` come from `route.walk_decisions`; `hindsight` is the state the
    alternatives are re-planned in. Regret for one decision is

        max(0, best OTHER option's path value - the taken option's), both
        under `policy_name`'s own value function, in `hindsight`

    which is the drafter's construction one level up: `draft_regret` re-scores
    sampled offers in the FINAL DECK context and asks whether some other card
    then outscores the pick. Here the deck's counterpart is the run STATE,
    because state is the only thing a route policy's valuation depends on --
    `_make_value` reads `hp_frac` for the rest discount, and the policy prefs
    read `elites_taken` (twice: the rising HP bar and the `< 4` cap) for the
    elite gate.

    THE STATE MUST BE THE ACT'S OWN TERMINAL STATE, not the run's. Unlike a
    deck, a RouteState does not accumulate across the run: `elites_taken` and
    `rests_taken` are ACT-LOCAL and reset at every boundary. Pricing act 0
    against act 2's snapshot therefore fed act-2 elites into act-0's elite gate
    -- hindsight the run did not possess at that decision (fixed 2026-08-08;
    `model._run_range` passes `route_decisions[i]["hindsight"]`).

    WHY HINDSIGHT IS THE WHOLE INSTRUMENT. In the deciding state this number is
    zero by construction: `_route` takes the argmax over exactly these path
    values, so no alternative can beat the pick. A regret is therefore never a
    planner bug and always the thing §4.2 asked for -- the lane that was worth
    taking while the run was healthy and was not worth it by the time the run
    arrived. That is precisely the hunter-vs-cautious comparison the "elite
    relics are underpriced" finding rests on, made per-decision instead of
    per-cohort.

    Floors with a single successor are FORCED, not chosen, and are excluded
    from the denominator (reported as `forced`) -- a road with no fork has no
    road not taken, and counting them would dilute the rate with the map's
    shape rather than the policy's judgement.

    Returns the gap distribution, not just a count: the drafter's integer works
    because a card either regrets or does not, whereas a route regret has a
    magnitude and the magnitude is what an A/B between two policies reads.
    """
    gaps, forced = route_regret_gaps(rng, act_map, decisions, hindsight,
                                     policy_name, sample=sample)
    regretted = sum(1 for g in gaps if g > margin)
    n = len(gaps)
    return {
        "policy": policy_name,
        "decisions": len(decisions),
        "forced": forced,
        "sampled": n,
        "regretted": regretted,
        "regret_rate": regretted / n if n else 0.0,
        "mean_regret": (sum(gaps) / n) if n else 0.0,
        "p50_regret": _percentile(gaps, 0.50),
        "p90_regret": _percentile(gaps, 0.90),
        "max_regret": max(gaps) if gaps else 0.0,
    }


def act_funnel(results: list[RunResult]) -> list[dict]:
    """§10.6 (multi-act): the per-act funnel -- what share of runs REACHED
    each act and what share CLEARED its boss. This is the surface the whole
    extension exists for: a frontloaded build shows a steep cleared-rate
    fall-off between act 1 and act 3; a scaling build holds.

    Denominator is ALL runs (not reached-conditional) so acts compose:
    cleared[act] is monotonically non-increasing by construction."""
    if not results:
        return []
    n_acts = results[0].n_acts
    tpl = C.MAP_FLOORS               # §11: one room per floor, always
    n = len(results)
    out = []
    for a in range(n_acts):
        reached = sum(1 for r in results
                      if r.death_node is None or r.death_node >= a * tpl)
        cleared = sum(1 for r in results if r.acts_completed > a)
        out.append({"act": a + 1, "reached": reached, "cleared": cleared,
                    "reached_rate": reached / n, "cleared_rate": cleared / n})
    return out


NEAR_DEATH_FRACTION = 0.15      # "one bad turn from dead"


def survival_profile(results: list[RunResult], max_hp: int) -> dict:
    """Fragility as SCALARS, normalized by max HP.

    Pass-4 sim-fidelity finding (2026-07-21): `hp_bands` already carried
    this signal and was already printed, but the design conversation
    travelled on the run-winrate scalar alone, which compresses "she
    spends the whole act one bad turn from dead" into a single percent.
    Absolute HP is also uninterpretable across characters with different
    max HP (Klee 62 vs REF_IRONCLAD 80) -- so everything here is a
    FRACTION of max, which is what makes an anchor comparison possible.

    Not banded, deliberately: bands are user-ratified (house rule). This
    reports; a ruling decides what is acceptable.
    """
    if not results:
        return {}
    # PER-RUN fight positions (audit 2026-07-26 s2.4, fixed in EPOCH 1).
    #
    # This used to read `kinds = results[0].node_kinds` and treat that ONE
    # run's room layout as the axis for the whole cohort. Under RUNTEMPLATE
    # 6+ routing there is no shared layout: one run's floor 4 is an elite and
    # another's is a shop. So every fragility scalar below was cross-sampling
    # HP from floors that were different room types run to run -- and worse,
    # results[0] is just whichever run came first, and dead runs are SHORT,
    # so an unlucky first run could size the axis down to almost nothing.
    # This module's own docstring (:47-49) already forbids exactly this for
    # the HP bands; survival_profile was the one place that still did it.
    #
    # The axis is FLOORS, as everywhere else in this module. At each floor a
    # run is sampled only if THAT RUN fought there.
    n_nodes = C.MAP_FLOORS * max(1, results[0].n_acts)
    # Fights only: N/E/B. R (rest), T (treasure) and $ (shop) are non-fight
    # nodes -- their HP entries carry the previous value and must not be
    # read as a fight's survival sample (RUNTEMPLATE_VERSION 3).
    pct = []
    for pos in range(n_nodes):
        # Keep the original run cohort at every fight. A run that died before
        # this position contributes 0 HP instead of disappearing from the
        # sample; otherwise later medians are conditional on survival and an
        # early death can make the reported act-health curve look healthier.
        #
        # A run that REACHED this floor but did not fight on it is excluded
        # rather than zeroed: its HP entry is a carried-over value from the
        # previous node, so counting it would be reading a rest stop as a
        # fight's survival sample -- the defect, in miniature.
        vals = []
        fought_here = False
        for r in results:
            if len(r.node_kinds) > pos:
                if r.node_kinds[pos] in ("N", "E", "B"):
                    fought_here = True
                    vals.append(r.hp_by_node[pos]
                                if len(r.hp_by_node) > pos else 0)
            else:
                vals.append(0)      # died before reaching this floor
        # A floor nobody fought on is not a fight position for this cohort.
        if not fought_here:
            continue
        pct.append(_percentile(vals, 0.50) / max_hp if vals else 0.0)
    floor = NEAR_DEATH_FRACTION * max_hp
    ever_near = sum(1 for r in results
                    if any(0 < h <= floor for h in r.hp_by_node))
    return {
        "median_hp_pct_by_fight": pct,
        # Mean of the median HP fraction across the act: one number for
        # "how much health does this character actually run on".
        "act_median_hp_pct": sum(pct) / len(pct) if pct else 0.0,
        # Share of the act the median run spends under 30% HP.
        "act_share_below_30pct": (sum(1 for p in pct if p < 0.30)
                                  / len(pct) if pct else 0.0),
        # Share of runs that ever touch the near-death floor while alive.
        "near_death_rate": ever_near / len(results),
        "max_hp": max_hp,
    }


def stability_profile(results: list[RunResult], max_hp: int) -> dict:
    """Kokomi's stability band -- HP-trajectory FLATNESS. (E1, missed-req 1.3.)

    R51 moved her healer fantasy *entirely* here: "the healer fantasy moves
    entirely to the stability band (HP-trajectory flatness) in the act-level
    realistic sims". The kickoff s3 pre-registered it as her acceptance
    signature -- "her acceptance signature is HP-trajectory flatness, not
    winrate margin" -- and proposed the shape as "max HP-loss variance across
    battery".

    Until now no such metric existed anywhere. `survival_profile` reports how
    LOW her HP gets; that is fragility, and it is generic and pre-Kokomi.
    Flatness is a different question: not "how close to death" but "how
    JAGGED". A character who ends every fight at 60% and one who alternates
    95% and 25% can share a median and share nothing else, and the second is
    the one whose fantasy is broken.

    THIS INSTRUMENT LANDS DARK, ON PURPOSE. Every value below is REPORTED and
    none is asserted, and `band` is explicitly None. The acceptance band is a
    [USER] ruling. Same house rule `survival_profile` states for itself:
    "bands are user-ratified. This reports; a ruling decides what is
    acceptable."

    The original gate was BLIND declaration -- the band on record before any
    playtest HP data was reviewed. **D5 (2026-07-27) amends that**, because
    HP-trajectory data was reviewed during the Kokomi playtest sprint and a
    blind declaration stopped being possible. Under D5: that playtest is
    EXPLORATORY and grades nothing; the band is declared from DESIGN INTENT,
    informed by those observations and recorded as such; declaration comes
    BEFORE the post-rework confirmatory playtest, which grades it; and the
    band MAY NOT be revised against the playtest that grades it. That last
    clause is what still keeps the target from being drawn around the shot --
    the Goodhart failure the axis-validity session (D3) was opened to
    investigate one instrument over.

    Everything is a FRACTION of max HP, so a band declared for Kokomi can be
    read against Klee (62) and REF_IRONCLAD (80) without rescaling.

    `prevented` is the ruled feed and rides here (R51: "ward prevention stays
    a reported telemetry stream (FightStats.prevented) feeding the stability
    band, never axis-credited"). It has been extracted by `metrics.py` since
    the kickoff and read by NOTHING -- audit s6 lists it among the metrics no
    report prints. This is the report.
    """
    if not results or max_hp <= 0:
        return {}

    # Per-FIGHT HP loss, as a fraction of max, pooled across every run.
    # Read off FightStats rather than differencing hp_by_node: node HP carries
    # forward across rests and shops, so a difference there measures the rest
    # economy as much as the fight (the survival_profile lesson, one door
    # over). hp_start/hp_end bracket the fight itself.
    losses: list[float] = []
    per_run_worst: list[float] = []
    prevented_total = 0
    fights_total = 0
    for run in results:
        run_losses = []
        for fight in run.fight_stats:
            lost = max(0, fight.hp_start - fight.hp_end)
            run_losses.append(lost / max_hp)
            prevented_total += getattr(fight, "prevented", 0)
            fights_total += 1
        if run_losses:
            losses.extend(run_losses)
            per_run_worst.append(max(run_losses))

    if not losses:
        return {"band": None, "fights": 0}

    mean_loss = sum(losses) / len(losses)
    # Population SD: this is the whole cohort of fights, not a sample of one.
    variance = sum((x - mean_loss) ** 2 for x in losses) / len(losses)
    sd = math.sqrt(variance)
    # The SIXTH hand-rolled percentile, found after the sim-hygiene sprint
    # unified the other five (2026-07-29): this one was nearest-rank, inside a
    # module whose own convention is linear. No published number quoted it.
    p90 = _percentile(losses, 0.90)
    total_lost_hp = sum(losses) * max_hp

    return {
        # THE headline flatness number: spread of per-fight HP loss.
        "hp_loss_sd_pct": sd,
        # Scale-free companion. A character who loses little AND evenly has a
        # small SD for an uninteresting reason; the coefficient of variation
        # separates "flat because nothing hits her" from "flat because she
        # absorbs evenly", which is the distinction her fantasy turns on.
        "hp_loss_cv": sd / mean_loss if mean_loss > 0 else 0.0,
        "hp_loss_mean_pct": mean_loss,
        # The kickoff's literal phrasing -- "max HP-loss" -- as the mean over
        # runs of each run's WORST single fight. One catastrophic fight is
        # exactly the spike the fantasy forbids.
        "worst_fight_loss_pct": (sum(per_run_worst) / len(per_run_worst)
                                 if per_run_worst else 0.0),
        # p90 alongside the worst, because a max over ~14 fights x 600 runs is
        # an extreme-value statistic and moves on noise.
        "hp_loss_p90_pct": p90,
        # R51's ruled feed. Reported only, never axis-credited.
        "prevented_per_fight": prevented_total / fights_total,
        # What share of the incoming the ward actually ate. The denominator is
        # damage that WOULD have landed, so prevention and real loss are
        # commensurable.
        "prevented_share": (prevented_total / (prevented_total + total_lost_hp)
                            if (prevented_total + total_lost_hp) > 0 else 0.0),
        "fights": fights_total,
        "max_hp": max_hp,
        # DARK until [USER] rules. Not a placeholder for whoever runs this
        # next to fill in -- the None is the point.
        "band": None,
    }


#: HP fractions the trajectory report counts rounds beneath. 0.50 is "half
#: health", the level at which a player starts routing around fights; 0.30 is
#: `NEAR_DEATH_FRACTION`'s neighbourhood, kept here as its own literal so the
#: two instruments cannot silently drift into sharing a threshold that only one
#: of them has a reason for.
TRAJECTORY_LOW_FRACTIONS: tuple[float, ...] = (0.50, 0.30)


def _drawdown(curve: list[float]) -> float:
    """The largest fall from a running high. The standard definition."""
    peak = curve[0]
    worst = 0.0
    for h in curve:
        peak = max(peak, h)
        worst = max(worst, peak - h)
    return worst


def trajectory_profile(results: list[RunResult], max_hp: int,
                       low_fractions: tuple[float, ...] = None) -> dict:
    """WITHIN-fight HP trajectory: jaggedness, drawdown, time spent low.

    The second half of the stability instrument (R51, D5), and the half
    `stability_profile` structurally could not see. That one reads `hp_start`
    and `hp_end`, which is one number per fight: a fight entered at 100% and
    left at 80% reads identically whether it was four even 5% chips or a dive
    to 25% and a recovery. The dive is the thing Kokomi's fantasy forbids, and
    it was invisible.

    This reads `FightStats.hp_by_round` -- player HP at the end of every round,
    sampled in the engine's round loop where `state.player.hp` is authoritative
    (HP also moves through paths that emit no `player_hit` and no `heal`, so a
    derived trajectory would be wrong on exactly the cards a stability reading
    is about).

    Three questions, because "flat" turns out to be three claims:

    1. **Jaggedness** -- `within_fight_sd_pct`: the mean over fights of the SD
       of end-of-round HP *inside* that fight. Deliberately per-fight and then
       averaged rather than pooled: pooling would mostly measure the act's
       downward drift, which is attrition, not jaggedness.
    2. **Spike depth** -- `max_drawdown_pct`: the classic peak-to-trough, run
       scale. The largest fall from any running high in the run's whole HP
       curve, averaged over runs, with `p90_drawdown_pct` beside it because a
       mean drawdown hides the tail that actually kills.
       `worst_round_drop_pct` is the same question at round resolution: the
       single biggest one-round fall, which is the burst a ward is supposed to
       eat.

       **Run-scale drawdown SATURATES in this cohort and is the weakest column
       here.** ~90% of tier-0.5 runs end in death, and the round before the
       lethal one is usually a sliver of HP, so every arm of the first reading
       came out at 0.95-1.01 whether the character was flat or jagged: a run
       that dies has by definition fallen almost all the way. Reported anyway,
       because it is the standard definition and a future world with a higher
       winrate will make it bite -- but the DISCRIMINATING columns today are
       `within_fight_sd_pct`, `worst_round_drop_pct` and the below-threshold
       shares. `survived_drawdown_pct` is the uncensored companion: the same
       statistic over only the fights the player walked out of, so it is the
       deepest trough she actually RECOVERED from. It carries a survivorship
       bias in the opposite direction (a run that dies in fight 2 contributes
       one fight of curve), which is why both are printed and neither is
       presented as the answer.
    3. **Time spent low** -- `round_share_below_XX`: the fraction of all rounds
       fought whose end-of-round HP is under that fraction of max. A character
       who spends a third of her rounds under half health is not stable however
       small her SD is.

    Everything is a FRACTION of max HP, so a Kokomi reading and a Klee reading
    are directly comparable -- the `survival_profile` / `stability_profile`
    house rule. Values above 1.0 are possible and are not bugs: `max_hp` is the
    character's STARTING max, and `gain_max_hp` moves the real ceiling up
    mid-run.

    **THE LETHAL ROUND IS EXCLUDED FROM EVERY COLUMN**, and this is the one
    judgement call in the module worth arguing with. Measured with it included,
    `max_drawdown_pct` came out at 1.03-1.08 for all six arms of the first
    reading -- because ~90% of tier-0.5 runs end in death, and a death is a fall
    to zero from wherever you were, so the column was reporting the death rate
    in a costume. Time-spent-low had the same leak: a round that ends at 0 HP is
    trivially under every threshold. Dying is what the WINRATE table measures.
    This instrument is about the shape of a living character's HP curve, so the
    round she does not survive is dropped and counted in `lethal_rounds`.

    **THIS INSTRUMENT DECLARES NO BAND.** Every value is REPORTED. `band` is
    None and stays None: declaring an acceptance band is a reserved [USER]
    ruling (R51 put Kokomi's whole healer fantasy on this instrument, and D5
    rules where the band may come from and when it may be graded -- from design
    intent, recorded as such, before the confirmatory playtest, and never
    revised against the playtest that grades it). Nothing here judges, and the
    absence of a verdict key is pinned by test.
    """
    if not results or max_hp <= 0:
        return {}
    fracs = (TRAJECTORY_LOW_FRACTIONS if low_fractions is None
             else low_fractions)

    per_fight_sd: list[float] = []
    per_run_drawdown: list[float] = []
    survived_drawdown: list[float] = []
    worst_round_drops: list[float] = []
    rounds_total = 0
    lethal_rounds = 0
    rounds_below = {f: 0 for f in fracs}

    for run in results:
        # The run's HP curve: every fight's rounds, in order, each fight opened
        # by its own hp_start so a rest-stop heal between fights shows up as
        # the recovery it is rather than as a phantom mid-fight spike.
        curve: list[float] = []
        # The same curve restricted to fights the player walked out of: an
        # uncensored drawdown, because it never contains the approach to a
        # death. Survivorship runs the other way (a run that dies in fight 2
        # contributes one fight), so the pair is reported, not reconciled.
        lived: list[float] = []
        for fight in run.fight_stats:
            rounds = [h / max_hp for h in getattr(fight, "hp_by_round", ())]
            # The lethal round out, everywhere. See the docstring: with it in,
            # every column becomes a restatement of the death rate.
            while rounds and rounds[-1] <= 0.0:
                rounds.pop()
                lethal_rounds += 1
            if not rounds:
                # A fight recorded before this instrument existed, or one that
                # ended inside its first player turn. Skipped, not zeroed: a
                # missing trajectory is not a flat one.
                continue
            start = fight.hp_start / max_hp
            within = [start] + rounds
            if len(rounds) > 1:
                mean = sum(within) / len(within)
                per_fight_sd.append(math.sqrt(
                    sum((x - mean) ** 2 for x in within) / len(within)))
            drops = [max(0.0, a - b) for a, b in zip(within, within[1:])]
            if drops:
                worst_round_drops.append(max(drops))
            rounds_total += len(rounds)
            for f in fracs:
                rounds_below[f] += sum(1 for h in rounds if h < f)
            curve.extend(within)
            if getattr(fight, "hp_end", 0) > 0:
                lived.extend(within)
        if curve:
            per_run_drawdown.append(_drawdown(curve))
        if lived:
            survived_drawdown.append(_drawdown(lived))

    if not rounds_total:
        return {"band": None, "rounds": 0, "lethal_rounds": lethal_rounds}

    def _mean(xs):
        return sum(xs) / len(xs) if xs else 0.0

    out = {
        "within_fight_sd_pct": _mean(per_fight_sd),
        "max_drawdown_pct": _mean(per_run_drawdown),
        "p90_drawdown_pct": _percentile(per_run_drawdown, 0.90),
        "survived_drawdown_pct": _mean(survived_drawdown),
        "survived_drawdown_runs": len(survived_drawdown),
        "worst_round_drop_pct": _mean(worst_round_drops),
        "rounds": rounds_total,
        "rounds_per_run": rounds_total / len(results),
        # Rounds dropped as lethal. Visible, not silent: the exclusion is a
        # judgement call and a reader has to be able to see how much of the
        # cohort it removed.
        "lethal_rounds": lethal_rounds,
        "max_hp": max_hp,
        # DARK until [USER] rules. Not a placeholder to be filled in.
        "band": None,
    }
    for f in fracs:
        out[f"round_share_below_{int(f * 100)}"] = rounds_below[f] / rounds_total
    return out


def banner_variance(results: list[RunResult]) -> dict:
    """v1.8 addendum: the bad-roll-bricking detector.

    Groups runs by the banner they rolled and reports the spread of winrate
    across those groups. If some featured lineups are meaningfully worse than
    others, this is where it shows up -- and a large spread is the evidence
    that would flip `standard: true` companions to off-banner floor status.

    Degenerate while a nation has no more 5-stars than banner slots: every run
    rolls the same lineup, so there is exactly one group and the spread is 0.
    Reported as `degenerate` rather than silently looking like a clean result,
    because "no variance" and "no variation possible" are different claims.
    """
    if not results:
        return {}
    groups: dict[frozenset[str], list[RunResult]] = {}
    for r in results:
        groups.setdefault(r.banner, []).append(r)
    rates = {b: sum(x.won for x in rs) / len(rs) for b, rs in groups.items()}
    values = list(rates.values())
    return {
        "distinct_banners": len(groups),
        "degenerate": len(groups) <= 1,
        "winrate_by_banner": {tuple(sorted(b)): v for b, v in rates.items()},
        "spread": (max(values) - min(values)) if len(values) > 1 else 0.0,
        "runs_per_banner": {tuple(sorted(b)): len(rs)
                            for b, rs in groups.items()},
    }


def conditional_assembly(results: list[RunResult], card_ids: list[str]) -> dict:
    """v1.8 addendum: dream-team assembly becomes P(assembly | featured).

    Unconditional assembly stops being the meaningful number once a banner
    gates availability -- a run that never had the card featured was never in
    the running, and averaging it in measures the banner rather than the
    draft. Denominator is runs where every required 5-star was featured;
    4-stars are never gated, so they impose no condition.
    """
    if not results:
        return {}
    required = set(card_ids)
    eligible = [r for r in results
                if required.issubset(r.banner | _ungated(required, r))]
    assembled = [r for r in eligible if required.issubset(set(r.deck_ids))]
    return {
        "eligible_runs": len(eligible),
        "eligible_rate": len(eligible) / len(results),
        "assembled": len(assembled),
        "conditional_rate": (len(assembled) / len(eligible)
                             if eligible else None),
        "unconditional_rate": sum(
            1 for r in results if required.issubset(set(r.deck_ids))
        ) / len(results),
    }


def _ungated(required: set[str], r: RunResult) -> set[str]:
    """Required ids that the banner does not gate (anything not a 5-star)."""
    from tier0.content import loader
    return {cid for cid in required
            if loader.get_card(cid).star != 5}


def encore_census(results: list[RunResult]) -> dict:
    """EB-20w: the EB-20 fight census pooled over a run cohort.

    Delegates every definition to `tier0.harness.metrics.encore_census_profile`
    over the cohort's `fight_stats` -- per-card grant/spend attribution, peak,
    empty-turn rate, and the Fanfare-leg split are all the fight census's, not
    restated here, so the run-layer number and the `--encore-census` fight
    number can never be two definitions wearing one name. The saturation half
    (dry/full/runway rates) stays with `tier05/encore_telemetry.py`, which
    reads the event log rather than FightStats.

    Same fence as the profile itself: measures, picks nothing -- the D8 lever
    is [USER]'s. Returns {} for a cohort with no Encore in it."""
    return t0_metrics.encore_census_profile(
        [s for r in results for s in r.fight_stats])


def floor_kind_labels(results: list[RunResult]) -> list[str]:
    """Per floor, the mix of node kinds the cohort actually walked.

    Under §11 routing there is no single 'kind' for a floor -- one run's
    floor 4 is an elite and another's is a shop. The label is the two
    commonest kinds with their shares, so the report shows the distribution
    instead of pretending it is a template."""
    if not results:
        return []
    n_nodes = C.MAP_FLOORS * max(1, results[0].n_acts)
    out = []
    for i in range(n_nodes):
        seen = Counter(r.node_kinds[i] for r in results
                       if len(r.node_kinds) > i)
        if not seen:
            out.append("-")
            continue
        total = sum(seen.values())
        out.append(" ".join(f"{k}{round(100 * v / total)}"
                            for k, v in seen.most_common(2)))
    return out


def print_run_report(character: str, archetype: str, s: dict,
                     node_kinds: list[str], survival: dict | None = None,
                     *, stamp: str) -> None:
    """Print the run report. `stamp` is MANDATORY (R68, 2026-07-26).

    A report without a stamp line is not citable in a sprint doc or a
    ruling, so it is a keyword-only required argument rather than an
    optional courtesy -- an omitted stamp has to be a TypeError at the call
    site, not a slightly thinner report that reads fine and cannot be
    checked. Build it with `tier05.cells.Cell.stamp()`; passing a
    hand-written string is allowed but is the thing R68 exists to stop.
    """
    print(f"\n=== Tier 0.5 runs: {character}/{archetype} "
          f"({s['runs']} runs) ===")
    print(f"  {stamp}")
    lo, hi = s["winrate_wilson95"]
    print(f"  run winrate      {s['winrate']:.1%} "
          f"({s['wins']}/{s['runs']}; Wilson 95% {lo:.1%}-{hi:.1%})")
    funnel = s.get("act_funnel") or []
    if len(funnel) > 1:                     # §10.6: multi-act runs only
        print("  act funnel       " + "   ".join(
            f"act{f['act']} reached {f['reached_rate']:.0%} "
            f"cleared {f['cleared_rate']:.0%}" for f in funnel))
    if survival:
        print(f"  survival         act median HP "
              f"{survival['act_median_hp_pct']:.0%} of max "
              f"({survival['max_hp']} HP)   "
              f"{survival['act_share_below_30pct']:.0%} of the act under 30%"
              f"   near-death {survival['near_death_rate']:.0%} of runs")
        print("                   median HP% by fight: "
              + " ".join(f"{p:.0%}" for p in
                         survival["median_hp_pct_by_fight"]))
    won, lost = s.get("avg_final_deck_won"), s.get("avg_final_deck_lost")
    # P5: both halves or neither. A single-sided split invites reading the
    # one number that happens to be present as the whole story.
    split = (f"   (won {won:.1f} / lost {lost:.1f})"
             if won is not None and lost is not None else "")
    print(f"  final deck size  {s['avg_final_deck']:.1f}{split}   "
          f"pick rate {s['pick_rate']:.0%}   "
          f"regrets {s['regretted_decisions']}")
    onl = s["median_time_to_online"]
    print(f"  time-to-online   median {onl} fights, "
          f"online in {s['online_rate']:.0%} of runs")
    # §11: node kinds vary per run, so the column reports what the COHORT
    # actually walked at that floor rather than one run's label -- a fixed
    # label would be a lie the moment routing exists.
    print("  floor kinds        reached   p25/p50/p75 HP   deaths")
    for i, kind in enumerate(node_kinds):
        b = s["hp_bands"][i]
        d = s["death_heatmap"].get(i, 0)
        bar = "█" * round(40 * d / max(1, s["runs"]))
        if b is None:
            print(f"  {i:>4}  {kind:<11}  (never reached)")
            continue
        print(f"  {i:>4}  {kind:<11}  {b['reached']:>7}   "
              f"{b['p25']:>4.0f}/{b['p50']:>4.0f}/{b['p75']:>4.0f}       "
              f"{d:>4} {bar}")
