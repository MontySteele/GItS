"""Furina's infinite-loop probe: self-sustaining cycles among her cards.

    .venv/Scripts/python.exe -m tier0.harness.furina_loop_probe
    .venv/Scripts/python.exe -m tier0.harness.furina_loop_probe --pre-fix
    .venv/Scripts/python.exe -m tier0.harness.furina_loop_probe --json out.json

THE CRITERION (the 2026-10-04 loop audit, kept for the Salon's Tab,
2026-10-05). A combination of at most three distinct cards (any copies), on a
deck thinned to just those cards, whose repeated play keeps Energy at 0 or
above and refills the hand indefinitely. A Power is played once and stays, so
a Power is an ENVIRONMENT here that uses up one of the three slots.

WHAT IS SEARCHED. Every row of Furina's sheet (`proto_fs_*` in
`docs/prototype-surface.yaml`), base and upgraded -- the starter and the
slice's 24. Exhaust cards leave the deck, so they cannot be a cycle's
members. Each combination is tried under every environment: no Power or one
of her Powers (base or upgraded), and two opening stages (empty; three
guests). A static screen (`profile` / `could_cycle`) drops a combination only
when no mix of plays can balance cards drawn against cards played and Energy
gained against Energy paid; every survivor is PLAYED in the real engine
(`combat.play_card`), copies 1-3 of each card, every priority order of its
cards x "take every Drain and Spend mode offered" / "take none".

THE BODY IS A REAL ONE. Furina enters at 78 of 78 HP, so the Drain line is
39 and the HP loan is bounded exactly as in a fight (the 2026-10-04 probe ran
on an unkillable HP pool; a Drain makes HP a resource, so it would have
counted unbounded Drain room as a loop). She starts with 10 Fanfare.

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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pre-fix", action="store_true",
                    help="put back the loop the 2026-10-04 audit fixed")
    ap.add_argument("--json", help="write the findings here")
    ap.add_argument("--jobs", type=int, default=1,
                    help="worker processes, one environment each")
    args = ap.parse_args(argv)
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
