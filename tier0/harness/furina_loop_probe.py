"""Furina's infinite-loop probe: self-sustaining cycles among her cards.

    .venv/Scripts/python.exe -m tier0.harness.furina_loop_probe
    .venv/Scripts/python.exe -m tier0.harness.furina_loop_probe --pre-fix
    .venv/Scripts/python.exe -m tier0.harness.furina_loop_probe --json out.json
    .venv/Scripts/python.exe -m tier0.harness.furina_loop_probe --named

`--named` is the pool-to-75 paper's sec.6 check
(`review/active/furina-pool-growth-2026-10-09.md`): the four combinations it
names, each played out in one long turn (the criterion below, with up to
three members and the named Powers, so a four-card combination fits) and
over several whole turns (`play_turns`: draw 5, play, the end of the turn's
guest acts and Showstopper, discard), every variant, copy count, order and
choice policy.

THE CRITERION (the 2026-10-04 loop audit, kept for the Salon's Tab,
2026-10-05). A combination of at most three distinct cards (any copies), on a
deck thinned to just those cards, whose repeated play keeps Energy at 0 or
above and refills the hand indefinitely. A Power is played once and stays, so
a Power is an ENVIRONMENT here that uses up one of the three slots.

WHAT IS SEARCHED. Every row of Furina's sheet (`proto_fs_*` in
`docs/prototype-surface.yaml`), base and upgraded -- the starter and the
pool of 75. Exhaust cards leave the deck, so they cannot be a cycle's
members. Each combination is tried under every environment: no Power or one
of her Powers (base or upgraded), and two opening stages (empty; three
guests). A static screen (`profile` / `could_cycle`) drops a combination only
when no mix of plays can balance cards drawn against cards played and Energy
gained against Energy paid; every survivor is PLAYED in the real engine
(`combat.play_card`), copies 1-3 of each card, every priority order of its
cards x "take every Drain and Spend mode offered" / "take none".

THE BODY IS A REAL ONE. Furina enters at 78 of 78 HP, so the Drain line is
59 and the HP loan is bounded exactly as in a fight: since the Drain line
rule (2026-10-09) a Drain may go past the line but never to 0 HP, so her HP
is the bound (the 2026-10-04 probe ran on an unkillable HP pool; a Drain
makes HP a resource, so it would have counted unbounded Drain room as a
loop). She starts with 10 Fanfare.

A RUN is one long turn against an enemy that cannot die and never attacks.
It SUSTAINS when it reaches `PLAYS` plays and, between play `PLAYS // 2` and
the end, neither Energy nor Fanfare fell. A sustained run is PRODUCTIVE when
that window grew anything: Fanfare, damage dealt, Block, Energy, next turn's
Energy, a Power's stacks, a guest's acts, or HP. Otherwise it is INERT.

`--pre-fix` puts back the one loop fix that still has a card (Interval
Bell's Spend mode gaining its Energy now, not next turn) so the probe can be
seen to catch what it fixed. `tier0/tests/test_furina_loop_probe.py` pins
both directions. AN INSTRUMENT, not a balance number.
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import itertools
import json
import random
import sys
from typing import Iterable, Optional

from tier0.content import loader
from tier0.engine import combat
from tier0.engine import furina_stage as FS
from tier0.engine.state import CombatState, Enemy, Player

PREFIX = "proto_fs_"
UP = "+"

#: One long turn: the run's length, and its second half is the window.
PLAYS = 60
START_ENERGY = 3
START_FANFARE = 10
START_HP = 78
#: Copies of each card: 1-3 in a combination of one or two cards, 1-2 in one
#: of three.
MAX_COPIES = 3
MAX_COPIES_TRIPLE = 2
ENEMY_HP = 10 ** 9

#: The opening stages tried: empty, and three guests seated.
STAGES: dict[str, tuple[str, ...]] = {
    "empty": (),
    "three_guests": ("charlotte", "wriothesley", "clorinde"),
}

#: The loop fix the 2026-10-04 audit made that still has a card on the
#: sheet. `prefix_patch` applies it to the loaded cards.
PRE_FIX = ("Interval Bell's Spend mode gains 1 Energy now",)


# ----------------------------------------------------------------------
# The cards.
# ----------------------------------------------------------------------
def sheet_ids() -> list[str]:
    return [c.id for c in loader.prototype_cards() if c.id.startswith(PREFIX)
            and getattr(c, "character", "furina") == "furina"
            and not c.id.startswith("proto_mf_")]


def variant(card_id: str, pre_fix: bool = False):
    """A fresh copy of one card variant (`id` or `id+`), or None when the row
    has no upgrade. `pre_fix` puts the found loop back."""
    try:
        card = loader.get_card(card_id)
    except ValueError:
        return None
    if pre_fix:
        _pre_fix(card)
    return card


def _pre_fix(card) -> None:
    base = card.id.split(UP)[0]
    if base == PREFIX + "interval_bell":
        for fx in _walk(card.effects):
            if fx.get("op") == "stage_energy_next":
                fx["op"] = "energy"


def variants(pre_fix: bool = False) -> dict[str, object]:
    out = {}
    for cid in sheet_ids():
        for vid in (cid, cid + UP):
            card = variant(vid, pre_fix)
            if card is not None:
                out[vid] = card
    return out


def _walk(effects: Iterable[dict]):
    for fx in effects or []:
        yield fx
        for branch in ("then", "else"):
            yield from _walk(fx.get(branch))
        for mode in fx.get("modes") or []:
            yield from _walk(mode.get("effects"))


def is_power(card) -> bool:
    return card.type == "power"


def is_member(card) -> bool:
    """Can this card be a cycle's member? Not a Power (played once) and not
    an Exhaust card (it leaves)."""
    return not is_power(card) and not card.exhaust


def power_grants(card) -> tuple[tuple[str, int], ...]:
    """A Power card's `apply_power` grants to herself."""
    return tuple((fx["power"], int(fx.get("amount", 1)))
                 for fx in _walk(card.effects)
                 if fx.get("op") == "apply_power"
                 and fx.get("target", "self") == "self"
                 and isinstance(fx.get("amount", 1), int))


# ----------------------------------------------------------------------
# The static screen: a NECESSARY condition only.
# ----------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class Profile:
    cost: int        # the lowest it can cost
    draw: int        # the most cards it can put in hand (every mode summed)
    energy: int      # the most Energy it can give this turn
    guest: bool      # does it summon a Guest Star?
    repays: bool     # can it Repay (Charlotte's line draws on one)?


def profile(card) -> Profile:
    draw = energy = 0
    guest = repays = False
    for fx in _walk(card.effects):
        op = fx.get("op")
        amount = fx.get("amount", 1)
        amount = amount if isinstance(amount, int) else 3
        if op in ("draw", "draw_to_hand_size"):
            draw += amount
        elif op == "energy":
            energy += amount
        if op == "stage_guest":
            guest = True
            repays = repays or fx.get("member") == "charlotte"
        if op in ("stage_repay", "stage_repay_all"):
            repays = True
    cost = 0 if card.cost == "X" else int(card.cost)
    return Profile(cost, draw, energy, guest, repays)


def could_cycle(profiles: list[Profile], powers: dict[str, int]) -> bool:
    """Is there ANY mix of plays (1-4 of each card a pass) whose cards drawn
    cover the cards played and whose Energy gained covers the Energy paid?
    Over-generous on purpose: every mode's draw summed, and a Repay worth
    Charlotte's draw on every pass."""
    rows = []
    for p in profiles:
        d = p.draw + (1 if p.repays else 0)
        rows.append((d - 1, p.energy - p.cost))
    for n in itertools.product(range(1, 5), repeat=len(rows)):
        cards = sum(k * r[0] for k, r in zip(n, rows))
        energy = sum(k * r[1] for k, r in zip(n, rows))
        if cards >= 0 and energy >= 0:
            return True
    return False


# ----------------------------------------------------------------------
# The dynamic run.
# ----------------------------------------------------------------------
class Decider:
    """The choice inside a card: take every Drain and Spend mode offered
    (`take`), or none."""

    def __init__(self, take: bool):
        self.take = take

    def spend_mode(self, state, modes):
        priced = [i for i, m in enumerate(modes)
                  if FS.spend_mode_amount(m) is not None
                  or FS.drain_mode_amount(m) is not None]
        if not priced:
            return None
        index = priced[0]
        keep = next((i for i in range(len(modes)) if i != index), 0)
        if self.take and FS.mode_offered(state.player, modes[index]):
            return index
        return keep


@dataclasses.dataclass
class Snapshot:
    energy: int
    fanfare: int
    dealt: int
    block: int
    energy_next: int
    powers: int
    acts: int
    hp: int

    @classmethod
    def of(cls, st) -> "Snapshot":
        p = st.player
        f = p.ftd
        return cls(int(p.energy), int(f.fanfare),
                   sum(e.max_hp - e.hp for e in st.enemies), int(p.block),
                   int(f.energy_next),
                   sum(v for v in p.powers.values() if isinstance(v, int)),
                   sum(f.ledger["guest_acts"].values()), int(p.hp))


@dataclasses.dataclass
class Run:
    plays: int
    sustained: bool
    productive: bool
    growth: dict


def _state(stage, powers: dict, seed: int, take: bool):
    p = Player(hp=START_HP, max_hp=START_HP, character_id="furina",
               element="hydro", cadence="skill")
    p.stage_decider = Decider(take)
    FS.reset_for_combat(p)
    p.ftd.stage = list(stage)
    p.ftd.fanfare = START_FANFARE
    p.energy = START_ENERGY
    p.powers.update(powers)
    st = CombatState(player=p,
                     enemies=[Enemy(hp=ENEMY_HP, max_hp=ENEMY_HP,
                                    name="target",
                                    intents=[{"kind": "block", "amount": 0}])],
                     rng=random.Random(seed))
    st.turn = 2
    return st


def play_out(cards: list, order: list[str], *, take: bool, stage=(),
             powers: Optional[dict] = None, seed: int = 0,
             plays: int = PLAYS) -> Run:
    """One run: `cards` start in hand (a deck thinned to them), and each play
    takes the highest-priority playable card (`order`, by id)."""
    st = _state(stage, dict(powers or {}), seed, take)
    st.player.hand = [copy.deepcopy(c) for c in cards]
    rank = {cid: i for i, cid in enumerate(order)}
    mid = None
    n = 0
    while n < plays and not st.over:
        options = [c for c in st.player.hand
                   if combat.card_playable(st, c)]
        if not options:
            break
        card = min(options, key=lambda c: rank.get(c.id, len(rank)))
        combat.play_card(st, card)
        n += 1
        if n == plays // 2:
            mid = Snapshot.of(st)
    if n < plays or mid is None:
        return Run(n, False, False, {})
    end = Snapshot.of(st)
    growth = {k: getattr(end, k) - getattr(mid, k)
              for k in dataclasses.asdict(end)}
    sustained = growth["energy"] >= 0 and growth["fanfare"] >= 0
    productive = sustained and any(v > 0 for v in growth.values())
    return Run(n, sustained, productive, growth)


# ----------------------------------------------------------------------
# The search.
# ----------------------------------------------------------------------
@dataclasses.dataclass
class Finding:
    cards: tuple[str, ...]          # the members' variant ids
    copies: tuple[int, ...]
    power: Optional[str]            # the Power variant id, or None
    stage: str
    take: bool
    order: tuple[str, ...]
    productive: bool
    growth: dict

    def key(self) -> tuple:
        return (self.cards, self.power)

    def label(self) -> str:
        parts = [f"{n}x {c[len(PREFIX):]}" for c, n in zip(self.cards,
                                                           self.copies)]
        env = []
        if self.power:
            env.append("power " + self.power[len(PREFIX):])
        env.append(f"stage {self.stage}")
        env.append("Drain/Spend taken" if self.take else "no Drain/Spend")
        grew = ", ".join(f"{k} +{v}" for k, v in self.growth.items() if v > 0)
        return (" + ".join(parts) + " [" + "; ".join(env) + "]"
                + (f" -> {grew}" if grew else " -> inert"))


def _members(pool: dict) -> list[str]:
    return sorted(cid for cid, c in pool.items() if is_member(c))


def _powers(pool: dict) -> list[Optional[str]]:
    return [None] + sorted(cid for cid, c in pool.items() if is_power(c))


def has_choice(cards) -> bool:
    """Does any card print a Drain or Spend (a mode, a fixed price, or a
    spend-all)? Only then is "take none" a different run."""
    return any(fx.get("op") in ("stage_spend", "stage_spend_all",
                                "stage_drain")
               for c in cards for fx in _walk(c.effects))


def touches_stage(cards, power: Optional[str]) -> bool:
    """Does the opening stage matter: a guest summon or a Repay or Drain on
    a card (guests' lines read them), or a Power?"""
    return bool(power) or any(str(fx.get("op", "")).startswith("stage_")
                              for c in cards for fx in _walk(c.effects))


def try_combo(pool: dict, combo: tuple[str, ...],
              power: Optional[str]) -> Optional[Finding]:
    """Every copy count, opening stage, priority order and choice policy for
    one combination under one environment. The first PRODUCTIVE run found
    wins; else the first sustained one; else None."""
    grants = dict(power_grants(pool[power])) if power else {}
    members = [pool[c] for c in combo]
    takes = (True, False) if has_choice(members) else (True,)
    stages = (STAGES if touches_stage(members, power)
              else {"empty": STAGES["empty"]})
    top = MAX_COPIES_TRIPLE if len(combo) >= 3 else MAX_COPIES
    inert = None
    for copies in itertools.product(range(1, top + 1), repeat=len(combo)):
        cards = [pool[cid] for cid, n in zip(combo, copies)
                 for _ in range(n)]
        for stage_name, stage in stages.items():
            for order in itertools.permutations(combo):
                for take in takes:
                    run = play_out(cards, list(order), take=take,
                                   stage=stage, powers=grants)
                    if not run.sustained:
                        continue
                    found = Finding(combo, copies, power, stage_name,
                                    take, order, run.productive, run.growth)
                    if run.productive:
                        return found
                    inert = inert or found
    return inert


def search_env(pre_fix: bool, power: Optional[str], max_cards: int = 3,
               only: Optional[Iterable[str]] = None) -> list[Finding]:
    """Every combination of up to `max_cards` distinct cards (the Power, if
    any, takes a slot) under one environment. A combination is skipped when
    a smaller one already loops PRODUCTIVELY here; over an inert subset it
    is still played and reported only if it is productive. `only` narrows
    the members (the tests)."""
    pool = variants(pre_fix)
    members = _members(pool)
    if only is not None:
        keep = set(only)
        members = [m for m in members if m in keep]
    profiles = {cid: profile(pool[cid]) for cid in members}
    grants = dict(power_grants(pool[power])) if power else {}
    slots = max_cards - (1 if power else 0)
    found: list[Finding] = []
    productive: list[set] = []
    inert: list[set] = []
    for k in range(1, slots + 1):
        for combo in itertools.combinations(members, k):
            seen = set(combo)
            if any(s <= seen for s in productive):
                continue
            if not could_cycle([profiles[c] for c in combo], grants):
                continue
            hit = try_combo(pool, combo, power)
            if hit is None:
                continue
            if hit.productive:
                productive.append(seen)
            elif any(s <= seen for s in inert):
                continue                    # restates a smaller inert cycle
            else:
                inert.append(seen)
            found.append(hit)
    return found


def _env_job(args) -> list[Finding]:
    return search_env(*args)


def search(pre_fix: bool = False, max_cards: int = 3, jobs: int = 1,
           powers: Optional[Iterable[Optional[str]]] = None,
           only: Optional[Iterable[str]] = None) -> list[Finding]:
    """`search_env` over every environment: no Power or one of hers.
    Returns the minimal findings (`_minimal`)."""
    pool = variants(pre_fix)
    envs = [(pre_fix, power, max_cards,
             tuple(only) if only is not None else None)
            for power in (_powers(pool) if powers is None else powers)]
    if jobs > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            parts = list(ex.map(_env_job, envs))
    else:
        parts = [_env_job(e) for e in envs]
    return _minimal([f for part in parts for f in part])


def _restates(f: Finding, g: Finding) -> bool:
    """Does `g` already say what `f` says: its cards a subset of `f`'s, its
    environment a part of `f`'s (no Power or the same one), and it loops at
    least as well?"""
    return (g is not f
            and set(g.cards) <= set(f.cards)
            and g.power in (None, f.power)
            and (g.productive or not f.productive)
            and (len(g.cards), g.power is not None)
            < (len(f.cards), f.power is not None))


def _minimal(found: list[Finding]) -> list[Finding]:
    """Drop every finding another one already restates (`_restates`)."""
    return [f for f in found if not any(_restates(f, g) for g in found)]


# ----------------------------------------------------------------------
# Inert cycles: does anything on her sheet make them productive?
# ----------------------------------------------------------------------
def awaken(pool: dict, finding: Finding) -> list[str]:
    """Each Power (in place of the finding's) and each seated guest that
    turns an inert cycle productive, by name."""
    woke = []
    cards = [pool[c] for c, n in zip(finding.cards, finding.copies)
             for _ in range(n)]
    for power in _powers(pool)[1:]:
        if len(finding.cards) + 1 > 3:
            break
        for take in (True, False):
            run = play_out(cards, list(finding.order), take=take,
                           stage=STAGES[finding.stage],
                           powers=dict(power_grants(pool[power])))
            if run.productive:
                woke.append("power " + power[len(PREFIX):])
                break
    for guest in FS.GUESTS:
        for take in (True, False):
            run = play_out(cards, list(finding.order), take=take,
                           stage=STAGES["empty"] + (guest,))
            if run.productive:
                woke.append("guest " + guest)
                break
    return woke


def report(pre_fix: bool, jobs: int = 1) -> dict:
    findings = search(pre_fix, jobs=jobs)
    pool = variants(pre_fix)
    out = {"pre_fix": pre_fix, "productive": [], "inert": []}
    for f in findings:
        row = {"label": f.label(), "cards": list(f.cards),
               "copies": list(f.copies), "power": f.power,
               "stage": f.stage, "take": f.take, "growth": f.growth}
        if f.productive:
            out["productive"].append(row)
        else:
            row["made_productive_by"] = awaken(pool, f)
            out["inert"].append(row)
    return out


# ----------------------------------------------------------------------
# THE POOL TO 75's NAMED COMBINATIONS (sec.6).
# ----------------------------------------------------------------------
#: Name -> (members, Powers, opening stages). Members and Powers are base
#: ids; every base/upgraded variant of each is tried.
NAMED: dict[str, tuple[tuple[str, ...], tuple[str, ...],
                       tuple[tuple[str, ...], ...]]] = {
    # "Encore! with Escoffier": Escoffier's line Repays 1 on every act.
    "encore_escoffier": (
        ("proto_fs_encore",), (),
        (("escoffier",), ("charlotte", "escoffier"),
         ("charlotte", "sigewinne", "escoffier"))),
    # "Tutti!, Showstopper and Bring the House Down together."
    "tutti_showstopper_house": (
        ("proto_fs_tutti", "proto_fs_bring_the_house_down"),
        ("proto_fs_showstopper",),
        (("charlotte", "wriothesley", "clorinde"),
         ("escoffier", "charlotte", "sigewinne"))),
    # "Final Bow with Grand Entrance: a guest leaves, its card returns, and
    # it is played again."
    "final_bow_grand_entrance": (
        ("proto_fs_final_bow", "proto_fs_guest_star_charlotte"),
        ("proto_fs_grand_entrance",),
        ((), ("sigewinne",))),
    # "Overdraft, Soothing Waters, Sold Out and Crescendo together. This is
    # the one cycle not bounded by HP."
    "energy_cycle": (
        ("proto_fs_overdraft", "proto_fs_soothing_waters",
         "proto_fs_sold_out"),
        ("proto_fs_crescendo",),
        ((),)),
}

#: Whole turns a `play_turns` run lasts, and the plays one turn may make
#: before it counts as a runaway.
TURNS = 6
TURN_PLAYS = 60


def _variants_of(pool: dict, base: str) -> list[str]:
    return [v for v in (base, base + UP) if v in pool]


def play_turns(cards: list, order: list[str], *, take: bool, stage=(),
               powers: Optional[dict] = None, seed: int = 0,
               turns: int = TURNS) -> dict:
    """`cards` as the whole deck over `turns` turns: each turn opens (the
    flow counts reset, Energy 3 plus what is owed), draws 5, plays by
    `order` until nothing is playable or `TURN_PLAYS` plays (a runaway),
    then the end of her turn runs (the guests act oldest first, Showstopper,
    the Singer) and the hand is discarded. Returns per-turn plays and what
    the run grew."""
    from tier0.engine import furina_tide as T
    st = _state(stage, dict(powers or {}), seed, take)
    p = st.player
    p.hand = []
    p.draw_pile = [copy.deepcopy(c) for c in cards]
    rank = {cid: i for i, cid in enumerate(order)}
    start = Snapshot.of(st)
    per_turn: list[int] = []
    runaway = False
    for t in range(turns):
        st.turn = t + 1
        T.turn_open(st)
        p.energy = START_ENERGY + T.energy_kept(st)
        st.draw(5)
        T.turn_start(st)
        n = 0
        while n < TURN_PLAYS and not st.over:
            options = [c for c in p.hand if combat.card_playable(st, c)]
            if not options:
                break
            card = min(options, key=lambda c: rank.get(c.id, len(rank)))
            combat.play_card(st, card)
            n += 1
        runaway = runaway or n >= TURN_PLAYS
        per_turn.append(n)
        T.end_of_turn(st)
        keep = [c for c in p.hand if getattr(c, "retain", False)]
        p.discard_pile.extend(c for c in p.hand if c not in keep)
        p.hand = keep
    end = Snapshot.of(st)
    return {"plays_per_turn": per_turn, "runaway": runaway,
            "growth": {k: getattr(end, k) - getattr(start, k)
                       for k in dataclasses.asdict(end)}}


def named_report(name: str) -> dict:
    """One sec.6 combination, every variant: the best single-turn run (a
    productive one if any) and the multi-turn runs' worst case."""
    members, powers, stages = NAMED[name]
    pool = variants(False)
    out = {"name": name, "members": list(members), "powers": list(powers),
           "single_turn": None, "multi_turn": None}
    member_sets = itertools.product(*(_variants_of(pool, m)
                                      for m in members))
    power_sets = list(itertools.product(*(_variants_of(pool, m)
                                          for m in powers))) or [()]
    best = None
    worst_turns = None
    for combo in member_sets:
        for pw in power_sets:
            grants: dict = {}
            for v in pw:
                for pid, amount in power_grants(pool[v]):
                    grants[pid] = grants.get(pid, 0) + amount
            takes = (True, False) if has_choice([pool[c] for c in combo]) \
                else (True,)
            for copies in itertools.product(range(1, MAX_COPIES_TRIPLE + 1),
                                            repeat=len(combo)):
                cards = [pool[c] for c, k in zip(combo, copies)
                         for _ in range(k)]
                for stage in stages:
                    for order in itertools.permutations(combo):
                        for take in takes:
                            run = play_out(cards, list(order), take=take,
                                           stage=stage, powers=grants)
                            row = {"cards": list(combo), "copies":
                                   list(copies), "powers": list(pw),
                                   "stage": list(stage), "take": take,
                                   "plays": run.plays,
                                   "sustained": run.sustained,
                                   "productive": run.productive,
                                   "growth": run.growth}
                            rank_ = (run.productive, run.sustained,
                                     run.plays)
                            if best is None or rank_ > best[0]:
                                best = (rank_, row)
                            turns = play_turns(cards, list(order),
                                               take=take, stage=stage,
                                               powers=grants)
                            trow = dict(row, **turns)
                            trank = (turns["runaway"],
                                     max(turns["plays_per_turn"]))
                            if worst_turns is None or trank > worst_turns[0]:
                                worst_turns = (trank, trow)
    out["single_turn"] = best[1] if best else None
    out["multi_turn"] = worst_turns[1] if worst_turns else None
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pre-fix", action="store_true",
                    help="put back the loop the 2026-10-04 audit fixed")
    ap.add_argument("--json", help="write the findings here")
    ap.add_argument("--jobs", type=int, default=1,
                    help="worker processes, one environment each")
    ap.add_argument("--named", action="store_true",
                    help="the pool-to-75 paper's four sec.6 combinations")
    args = ap.parse_args(argv)
    if args.named:
        rows = [named_report(name) for name in NAMED]
        for row in rows:
            s, m = row["single_turn"], row["multi_turn"]
            verdict = ("PRODUCTIVE LOOP" if s and s["productive"] else
                       "inert loop" if s and s["sustained"] else "no loop")
            print(f"{row['name']}: one turn -> {verdict}"
                  + (f" ({s['plays']} plays, cards {s['cards']} x"
                     f"{s['copies']}, powers {s['powers']}, stage "
                     f"{s['stage']}, growth "
                     f"{ {k: v for k, v in s['growth'].items() if v} })"
                     if s and s["sustained"] else ""))
            if m:
                print(f"    {TURNS} turns, worst case: plays per turn "
                      f"{m['plays_per_turn']}, runaway {m['runaway']}, "
                      f"cards {m['cards']} x{m['copies']}, powers "
                      f"{m['powers']}, stage {m['stage']}, growth "
                      f"{ {k: v for k, v in m['growth'].items() if v} }")
        if args.json:
            with open(args.json, "w", encoding="utf-8") as fh:
                json.dump(rows, fh, indent=2)
        return 0
    out = report(args.pre_fix, args.jobs)
    for kind in ("productive", "inert"):
        print(f"{kind.upper()} ({len(out[kind])})")
        for row in out[kind]:
            extra = ""
            if kind == "inert" and row["made_productive_by"]:
                extra = "  [made productive by: " + ", ".join(
                    row["made_productive_by"]) + "]"
            print("  " + row["label"] + extra)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
