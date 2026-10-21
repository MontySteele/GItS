"""Kokomi's loop probe: self-sustaining cycles among her cards.

    .venv/Scripts/python.exe -m tier0.harness.kokomi_loop_probe
    .venv/Scripts/python.exe -m tier0.harness.kokomi_loop_probe --named
    .venv/Scripts/python.exe -m tier0.harness.kokomi_loop_probe --named --pre-fix
    .venv/Scripts/python.exe -m tier0.harness.kokomi_loop_probe --json out.json

Furina's probe (`tier0/harness/furina_loop_probe.py`) is the model. Kokomi
needs two halves, because a Plan pays NEXT turn: a cycle of hers can close
inside one turn (cards that refill the hand and the Energy) or across turns
(a Plan whose carry-out hands back the card that wrote it).

THE IN-TURN SWEEP (the default run) is Furina's criterion verbatim: a
combination of at most three distinct cards (any copies), on a deck thinned
to just those cards, whose repeated play keeps Energy at 0 or above and
refills the hand indefinitely. A Power is an ENVIRONMENT that uses up one of
the three slots; Exhaust cards and Powers are never members. Every row of her
sheet (`proto_kk_*` owned by `kokomi`), base and upgraded. A static screen
(`could_cycle`) drops a combination only when no mix of plays can balance
cards gained against cards played and Energy gained against Energy paid; a
Sting or Ward a card adds counts as a card gained. Every survivor is PLAYED
(`combat.play_card`) on two boards: an enemy that never attacks (so every
card with a Plan line is written on the Bake-Kurage, the pilot's own rule,
`kokomi_plan.plan_aimed_at_pet`) and one that always does (so every card is
played face-up). One long turn of `PLAYS` plays SUSTAINS when Energy did not
fall over its second half, and is PRODUCTIVE when that half grew anything.

THE NAMED RUNS (`--named`) are the cross-turn half: the BACKLOG's known set
and the v2 check, each played over `TURNS` whole turns of the engine's own
turn (`combat._player_turn` then `combat._enemy_turn`: draw 5, the morning's
Plans, play, end of turn), every base/upgraded variant, copy count and board.
A run is a RUNAWAY when a turn trips the engine's own infinite detector (the
`degeneracy` event: 25 plays, or a repeated state); it GROWS when a turn's
output (damage dealt, Block held, Weak and Vulnerable applied) rises on every
one of the last `TURNS // 2` turns; it is PERPETUAL when Stings or Wards are
still being made on every one of those turns while nothing but Stings and
Wards is played (the jellyfish feeding itself).

`--pre-fix` puts back the one loop the Kokomi card paper v2 closed (Kurage
Canopy and Endless Shoal paying for a Sting's or Ward's carry-out), so the
probe is seen to find it. `tier0/tests/test_kokomi_loop_probe.py` pins both
directions. AN INSTRUMENT, not a balance number (R215 B).
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import dataclasses
import itertools
import json
import random
import sys
from typing import Iterable, Iterator, Optional

from tier0.content import loader
from tier0.engine import combat, kokomi_plan
from tier0.engine.state import CombatState, Enemy, Player

PREFIX = "proto_kk_"
UP = "+"
STING = "proto_kk_sting"
WARD = "proto_kk_ward"

#: One long turn: the run's length, and its second half is the window.
PLAYS = 60
START_ENERGY = 3
#: Copies of each card: 1-3 in a combination of one or two cards, 1-2 in one
#: of three.
MAX_COPIES = 3
MAX_COPIES_TRIPLE = 2
ENEMY_HP = 10 ** 9
PLAYER_HP = 10 ** 6

#: The two boards. An enemy that intends no attack makes the pilot write
#: every card with a Plan line; one that intends an attack makes it play them
#: face-up (`kokomi_plan.plan_aimed_at_pet`).
BOARDS: dict[str, list[dict]] = {
    "plan": [{"kind": "block", "amount": 0}],
    "face": [{"kind": "attack", "amount": 6}],
}


# ----------------------------------------------------------------------
# The cards.
# ----------------------------------------------------------------------
def sheet_ids() -> list[str]:
    return [c.id for c in loader.prototype_cards()
            if c.id.startswith(PREFIX)
            and getattr(c, "character", "kokomi") == "kokomi"]


def variants() -> dict[str, object]:
    out = {}
    for cid in sheet_ids():
        for vid in (cid, cid + UP):
            try:
                out[vid] = loader.get_card(vid)
            except ValueError:
                continue
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
    """Can this card be a cycle's member? Not a Power (played once), not an
    Exhaust card (it leaves) and not a token (a Sting or a Ward exhausts)."""
    return (not is_power(card) and not card.exhaust
            and card.rarity != "token")


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
#: The ops that put a card in her hand, face-up or as a Plan's line.
_CARD_OPS = ("draw", "add_card", "draw_pile_to_hand", "add_stings")
_CARD_KINDS = ("shoal_call", "add_sting", "add_ward", "add_companions",
               "call_the_generals", "choose_common_companion")


@dataclasses.dataclass(frozen=True)
class Profile:
    cost: int        # the lowest it can cost
    cards: int       # the most cards it can put in hand, either line
    energy: int      # the most Energy it can give, either line


def profile(card) -> Profile:
    cards = energy = 0
    for fx in list(_walk(card.effects)) + list(_walk(card.plan)):
        op = fx.get("op")
        amount = fx.get("amount", 1)
        amount = amount if isinstance(amount, int) else 3
        if op in _CARD_OPS or (op == "kokomi"
                               and fx.get("kind") in _CARD_KINDS):
            cards += max(1, amount)
        elif op in ("energy", "each_player_energy",
                    "energy_if_attacked_since"):
            energy += amount
    cost = 0 if card.cost == "X" else int(card.cost)
    return Profile(cost, cards, energy)


def could_cycle(profiles: list[Profile]) -> bool:
    """Is there ANY mix of plays (1-4 of each card a pass) whose cards gained
    cover the cards played and whose Energy gained covers the Energy paid?
    Over-generous on purpose: both lines summed, every token a card."""
    rows = [(p.cards - 1, p.energy - p.cost) for p in profiles]
    for n in itertools.product(range(1, 5), repeat=len(rows)):
        cards = sum(k * r[0] for k, r in zip(n, rows))
        energy = sum(k * r[1] for k, r in zip(n, rows))
        if cards >= 0 and energy >= 0:
            return True
    return False


# ----------------------------------------------------------------------
# The board.
# ----------------------------------------------------------------------
def _state(board: str, powers: dict, seed: int = 0) -> CombatState:
    p = Player(hp=PLAYER_HP, max_hp=PLAYER_HP, character_id="kokomi",
               element="hydro", cadence="catalyst")
    p.relic_hooks.append(loader.OVERHAUL_CASKET_HOOK)
    p.energy = START_ENERGY
    p.powers.update(powers)
    st = CombatState(player=p,
                     enemies=[Enemy(hp=ENEMY_HP, max_hp=ENEMY_HP,
                                    name="target",
                                    intents=copy.deepcopy(BOARDS[board]))],
                     rng=random.Random(seed))
    st.in_player_turn = True
    st.turn = 2
    return st


@contextlib.contextmanager
def pre_fix() -> Iterator[None]:
    """The loop the Kokomi card paper v2 closed (sec.2 change 5): Kurage
    Canopy and Endless Shoal paid for every carry-out, a Sting's and a Ward's
    included. Puts that back for the length of the block."""
    was = kokomi_plan.jellyfish_line
    kokomi_plan.jellyfish_line = lambda entry: False
    try:
        yield
    finally:
        kokomi_plan.jellyfish_line = was


@dataclasses.dataclass
class Snapshot:
    energy: int
    dealt: int
    block: int
    powers: int
    queued: int

    @classmethod
    def of(cls, st) -> "Snapshot":
        p = st.player
        return cls(int(p.energy), sum(e.max_hp - e.hp for e in st.enemies),
                   int(p.block),
                   sum(v for v in p.powers.values() if isinstance(v, int)),
                   len(st.kk_plan_queue))


@dataclasses.dataclass
class Run:
    plays: int
    sustained: bool
    productive: bool
    growth: dict


def play_out(cards: list, order: list[str], *, board: str,
             powers: Optional[dict] = None, seed: int = 0,
             plays: int = PLAYS) -> Run:
    """One long turn: `cards` start in hand (a deck thinned to them), and
    each play takes the highest-priority playable card (`order`, by id)."""
    st = _state(board, dict(powers or {}), seed)
    st.player.hand = [copy.deepcopy(c) for c in cards]
    rank = {cid: i for i, cid in enumerate(order)}
    mid = None
    n = 0
    while n < plays and not st.over:
        options = [c for c in st.player.hand if combat.card_playable(st, c)]
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
    sustained = growth["energy"] >= 0
    productive = sustained and any(v > 0 for v in growth.values())
    return Run(n, sustained, productive, growth)


# ----------------------------------------------------------------------
# The in-turn search.
# ----------------------------------------------------------------------
@dataclasses.dataclass
class Finding:
    cards: tuple[str, ...]          # the members' variant ids
    copies: tuple[int, ...]
    power: Optional[str]            # the Power variant id, or None
    board: str
    order: tuple[str, ...]
    productive: bool
    growth: dict

    def label(self) -> str:
        parts = [f"{n}x {c[len(PREFIX):]}" for c, n in zip(self.cards,
                                                           self.copies)]
        env = [f"board {self.board}"]
        if self.power:
            env.insert(0, "power " + self.power[len(PREFIX):])
        grew = ", ".join(f"{k} +{v}" for k, v in self.growth.items() if v > 0)
        return (" + ".join(parts) + " [" + "; ".join(env) + "]"
                + (f" -> {grew}" if grew else " -> inert"))


def _members(pool: dict) -> list[str]:
    return sorted(cid for cid, c in pool.items() if is_member(c))


def _powers(pool: dict) -> list[Optional[str]]:
    return [None] + sorted(cid for cid, c in pool.items() if is_power(c))


def try_combo(pool: dict, combo: tuple[str, ...],
              power: Optional[str]) -> Optional[Finding]:
    """Every copy count, board and priority order for one combination under
    one environment. The first PRODUCTIVE run found wins; else the first
    sustained one; else None."""
    grants = dict(power_grants(pool[power])) if power else {}
    top = MAX_COPIES_TRIPLE if len(combo) >= 3 else MAX_COPIES
    inert = None
    for copies in itertools.product(range(1, top + 1), repeat=len(combo)):
        cards = [pool[cid] for cid, n in zip(combo, copies)
                 for _ in range(n)]
        for board in BOARDS:
            for order in itertools.permutations(combo):
                run = play_out(cards, list(order) + [STING, WARD],
                               board=board, powers=grants)
                if not run.sustained:
                    continue
                found = Finding(combo, copies, power, board, order,
                                run.productive, run.growth)
                if run.productive:
                    return found
                inert = inert or found
    return inert


def search_env(power: Optional[str], max_cards: int = 3,
               only: Optional[Iterable[str]] = None) -> list[Finding]:
    """Every combination of up to `max_cards` distinct cards (the Power, if
    any, takes a slot) under one environment. A combination is skipped when
    a smaller one already loops PRODUCTIVELY here, or restates a smaller
    inert one. `only` narrows the members (the tests)."""
    pool = variants()
    members = _members(pool)
    if only is not None:
        keep = set(only)
        members = [m for m in members if m in keep]
    profiles = {cid: profile(pool[cid]) for cid in members}
    slots = max_cards - (1 if power else 0)
    found: list[Finding] = []
    productive: list[set] = []
    inert: list[set] = []
    for k in range(1, slots + 1):
        for combo in itertools.combinations(members, k):
            seen = set(combo)
            if any(s <= seen for s in productive):
                continue
            if not could_cycle([profiles[c] for c in combo]):
                continue
            hit = try_combo(pool, combo, power)
            if hit is None:
                continue
            if hit.productive:
                productive.append(seen)
            elif any(s <= seen for s in inert):
                continue
            else:
                inert.append(seen)
            found.append(hit)
    return found


def search(max_cards: int = 3, jobs: int = 1,
           powers: Optional[Iterable[Optional[str]]] = None,
           only: Optional[Iterable[str]] = None) -> list[Finding]:
    """`search_env` over every environment: no Power or one of hers."""
    pool = variants()
    envs = list(_powers(pool) if powers is None else powers)
    if jobs > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            parts = list(ex.map(search_env, envs,
                                itertools.repeat(max_cards),
                                itertools.repeat(only)))
    else:
        parts = [search_env(e, max_cards, only) for e in envs]
    return [f for part in parts for f in part]


# ----------------------------------------------------------------------
# THE NAMED RUNS: whole turns.
# ----------------------------------------------------------------------
#: Whole turns a named run lasts; its second half is the window.
TURNS = 8

#: Name -> (members with copies, Powers, boards). Base ids; every
#: base/upgraded variant of each is tried.
NAMED: dict[str, tuple[tuple[tuple[str, int], ...], tuple[str, ...],
                       tuple[str, ...]]] = {
    # The BACKLOG's known set, review r3 (`kokomi-review-r3-2026-10-13.md`
    # sec.3): eight Stings at 8 plus 16 from the Shape for 3 Energy, a
    # one-turn 80 that exhausts both Calls. A burst, not a loop; kept, listed.
    # Closed by the Kokomi taste audit (2026-10-21): Shoal Call Plans them.
    "shoal_shape_of_water": (
        (("proto_kk_shoal_call", 2), ("proto_kk_the_shape_of_water", 1)),
        ("proto_kk_watchful_shoal",), ("face",)),
    # The BACKLOG's known set, review r4 (`kokomi-review-r4-2026-10-13.md`
    # sec.3): Kurage Canopy plus one Ward. A Ward written as a Plan returned a
    # Ward the next morning, with 1 Weak on the front enemy and the Casket's
    # 3 Block: "a steady 0-cost Weak and 3 Block a turn". The Kokomi card
    # paper v2 (sec.2 change 5) took a Sting's or Ward's carry-out off Canopy
    # and Endless Shoal, which closes it; `--pre-fix` puts it back.
    "canopy_ward": (
        (("proto_kk_ward", 1),), ("proto_kk_kurage_canopy",), ("plan",)),
    # The same cycle on Endless Shoal's Sting (review r4, the same section:
    # "and a Sting under Endless Shoal").
    "endless_shoal_sting": (
        (("proto_kk_sting", 1),), ("proto_kk_endless_shoal",), ("plan",)),
    # THE V2 CHECK (2026-10-18): Shoal Call's Stings written as Plans, with
    # Feint and Turning Tide paying per Plan carried out that morning. It
    # must stay bounded: the Calls and the Stings exhaust, so the morning's
    # count is the hand's.
    "shoal_feint_turning_tide": (
        (("proto_kk_shoal_call", 2), ("proto_kk_feint", 1),
         ("proto_kk_turning_tide_chain", 1)), (), ("plan",)),
    # And with Endless Shoal and Kurage Canopy out, the two Powers that turn
    # a carry-out into a card.
    "shoal_feint_turning_tide_engines": (
        (("proto_kk_shoal_call", 2), ("proto_kk_feint", 1),
         ("proto_kk_turning_tide_chain", 1)),
        ("proto_kk_endless_shoal", "proto_kk_kurage_canopy"), ("plan",)),
}


def _variants_of(pool: dict, base: str) -> list[str]:
    return [v for v in (base, base + UP) if v in pool]


def _token(card_id: str) -> bool:
    return card_id.rstrip(UP) in (STING, WARD)


def play_turns(cards: list, order: list[str], *, board: str,
               powers: Optional[dict] = None, seed: int = 0,
               turns: int = TURNS) -> dict:
    """`cards` as the whole deck over `turns` rounds of the engine's own
    turn: her turn (`combat._player_turn`: Block clear, the Casket, Energy,
    draw 5, the morning's Plans, the generators, play by `order`, end of
    turn), then the enemy's. Returns per-turn plays and output, and the three
    verdicts."""
    st = _state(board, dict(powers or {}), seed)
    p = st.player
    p.hand = []
    p.draw_pile = [copy.deepcopy(c) for c in cards]
    st.turn = 0
    rank = {cid: i for i, cid in enumerate(order)}

    def pilot(state):
        options = [c for c in state.player.hand
                   if combat.card_playable(state, c)]
        if not options:
            return None
        return min(options, key=lambda c: rank.get(c.id, len(rank)))

    rows = []
    for _ in range(turns):
        if st.over:
            break
        before = len(st.log)
        dealt = sum(e.max_hp - e.hp for e in st.enemies)
        combat._player_turn(st, pilot)
        for enemy in list(st.enemies):
            if st.over:
                break
            combat._enemy_turn(st, enemy)
        events = st.log[before:]
        rows.append({
            "plays": sum(1 for e in events if e["event"] == "play"),
            "card_plays": sum(1 for e in events if e["event"] == "play"
                              and not _token(str(e.get("card", "")))),
            "dealt": sum(e.max_hp - e.hp for e in st.enemies) - dealt,
            "block": next((e["block"] for e in events
                           if e["event"] == "turn_close"), 0),
            "debuffs": sum(int(e.get("stacks") or 0) for e in events
                           if e["event"] == "apply_power"
                           and e.get("target") != "player"
                           and e.get("power") in ("weak", "vulnerable")),
            "tokens": sum(int(e.get("amount") or 0) for e in events
                          if e["event"] == "kk_jellyfish_added"),
            "runaway": any(e["event"] == "degeneracy"
                           and e.get("kind") == "INFINITE" for e in events),
        })
    window = rows[-(turns // 2):]
    out = {k: [r[k] for r in rows]
           for k in ("plays", "dealt", "block", "debuffs", "tokens")}
    out["runaway"] = any(r["runaway"] for r in rows)
    out["growing"] = len(window) > 1 and any(
        all(b[k] > a[k] for a, b in zip(window, window[1:]))
        for k in ("dealt", "block", "debuffs"))
    # FED BY ITSELF: Stings or Wards made on every turn of the window while
    # nothing but Stings and Wards was played -- a Feint that comes round
    # and pays Endless Shoal is the Power's job, not a cycle.
    out["perpetual"] = (len(rows) == turns
                        and all(r["tokens"] > 0 and r["card_plays"] == 0
                                for r in window))
    return out


def named_report(name: str, fixed: bool = True) -> dict:
    """One named combination, every variant, copy count and board: the worst
    case (a runaway, then growth, then a perpetual cycle, then the most plays
    in a turn)."""
    members, powers, boards = NAMED[name]
    pool = variants()
    worst = None
    ctx = contextlib.nullcontext() if fixed else pre_fix()
    with ctx:
        for combo in itertools.product(*(_variants_of(pool, m)
                                         for m, _ in members)):
            for pw in (list(itertools.product(
                    *(_variants_of(pool, m) for m in powers))) or [()]):
                grants: dict = {}
                for v in pw:
                    for pid, amount in power_grants(pool[v]):
                        grants[pid] = grants.get(pid, 0) + amount
                cards = [pool[c] for c, (_, k) in zip(combo, members)
                         for _ in range(k)]
                order = list(combo) + [STING + UP, STING, WARD + UP, WARD]
                for board in boards:
                    run = play_turns(cards, order, board=board,
                                     powers=grants)
                    row = dict(run, cards=list(combo), powers=list(pw),
                               board=board)
                    rank = (run["runaway"], run["growing"],
                            run["perpetual"], max(run["plays"] or [0]))
                    if worst is None or rank > worst[0]:
                        worst = (rank, row)
    return {"name": name, "fixed": fixed,
            "worst": worst[1] if worst else None}


def report(jobs: int = 1) -> dict:
    found = search(jobs=jobs)
    return {"productive": [f.label() for f in found if f.productive],
            "inert": [f.label() for f in found if not f.productive]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--named", action="store_true",
                    help="the known set and the v2 check, over whole turns")
    ap.add_argument("--pre-fix", action="store_true",
                    help="with --named: put back the loop v2 closed")
    ap.add_argument("--json", help="write the findings here")
    ap.add_argument("--jobs", type=int, default=1,
                    help="worker processes, one environment each")
    args = ap.parse_args(argv)
    if args.named:
        rows = [named_report(n, fixed=not args.pre_fix) for n in NAMED]
        for row in rows:
            w = row["worst"]
            verdict = ("RUNAWAY" if w["runaway"] else
                       "GROWS" if w["growing"] else
                       "PERPETUAL" if w["perpetual"] else "bounded")
            print(f"{row['name']}: {verdict} (cards {w['cards']}, powers "
                  f"{w['powers']}, board {w['board']}; plays {w['plays']}, "
                  f"dealt {w['dealt']}, tokens {w['tokens']})")
        out: object = rows
    else:
        out = report(args.jobs)
        for kind in ("productive", "inert"):
            print(f"{kind.upper()} ({len(out[kind])})")
            for label in out[kind]:
                print("  " + label)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
