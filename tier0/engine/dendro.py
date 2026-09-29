"""DENDRO, phase two of the element port -- SIM ONLY, EXPLORATORY, switched off.

The ruled boundaries are `review/ruled/dendro-boundaries-2026-09-06.md`
(R264, every pick at its default) and the element-home ruling's sec.7.2 /
sec.7.4 (`review/ruled/element-home-review-2026-09-28.md`). `BACKLOG.md` holds
the real phase-two build; this module is the sim half of it, written for the
Nahida paper sim (2026-09-29) and kept cleanly separable so the real build can
take it, rewrite it, or delete it without touching anything else:

  * ONE SWITCH, `DENDRO_ENGINE`, default False. With it off,
    `reactions.resolve_hit` never reaches this module and the engine is
    byte-identical to the shipped world (`tier0/tests/test_nahida_paper_sim.py`
    pins a whole-log digest both ways).
  * NO ROW CARRIES `element: dendro` (the ruling's sec.1 rule). The only
    Dendro hits in this engine are the ones a switched-on caller deals.
  * NOTHING MEASURED HERE IS QUOTABLE as a balance number (R215 B's reading
    for prototype rows): it is a rule made runnable.

What is modelled, in the ruling's words:

  * Dendro is a fifth AURA element: one per enemy, the shared duration, a
    same-element hit refreshes it.
  * BLOOM (Dendro + Hydro, either order) consumes the aura and leaves a
    DENDRO CORE on that enemy. A Core bursts on its own at the END OF YOUR
    NEXT TURN for `CORE_BURST` to that enemy; a PYRO hit on the enemy pops it
    early as BURGEON (`CORE_BURST` to every enemy); an ELECTRO hit pops it as
    HYPERBLOOM (`CORE_BURST * HYPERBLOOM_MULT` to that enemy). At most
    `CORE_CAP` Cores per enemy; a Bloom past the cap bursts the oldest (a
    plain burst) and adds the new one. Core damage is flat, pipeline-free,
    applies no aura, and is STOPPED BY BLOCK (sec.3: "a Core is a thing that
    explodes, not a shock").
  * QUICKEN (Dendro + Electro) consumes the aura; for `QUICKEN_TURNS` turns
    every Electro or Dendro hit on that enemy deals `+QUICKEN_BONUS` (pick 3,
    canon gating).
  * BURNING (Dendro + Pyro) consumes the aura; `BURNING_DOT` a turn for
    `BURNING_TURNS`, stopped by Block, never stacks; while it burns the enemy
    holds a Pyro aura, refreshed each tick. A Pyro or Dendro hit re-lights it
    (duration reset); a reaction that CONSUMES the held Pyro ends it; Swirl
    and Crystallize (which no longer consume, element port sec.3) do not
    (sec.7.2).
  * NO REACTION (pick 2 default): Dendro with Cryo, and Anemo or Geo on a
    Dendro aura, are plain hits; the standing aura stands.

Where the ruling leaves a number or a timing open this module takes a
reading and says so at the site (`OPEN READING`). The Nahida report lists
them.

Every Dendro reaction (Bloom, Quicken, Burning, a Core's burst, Burgeon,
Hyperbloom) reports through `reactions.note_reaction`, the ONE reaction event
(element port sec.7.3), so a listener such as Nahida's Purification needs no
hook of its own.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

#: THE SWITCH. Read at call time by `reactions.resolve_hit` and the two
#: combat turn sites. Default False: the shipped world has no Dendro.
DENDRO_ENGINE = False

# The ruling's sec.6 numbers, at their disclosed defaults (D picks for the sim).
CORE_BURST = 6
HYPERBLOOM_MULT = 2
CORE_CAP = 2
QUICKEN_BONUS = 3
QUICKEN_TURNS = 2
BURNING_DOT = 3
BURNING_TURNS = 3

#: The damage-event `source` values this module emits, so a reader can split
#: reaction damage from card damage without re-deriving it.
SOURCE_CORE = "dendro_core"
SOURCE_BURNING = "dendro_burning"


@dataclass
class EnemyDendro:
    """The Dendro-side state one enemy carries. Kept OFF `Enemy` (a shared
    dataclass the mod mirrors) so the module stays separable: it lives in a
    per-combat side table keyed by the enemy's identity."""
    cores: list[int] = field(default_factory=list)   # turn each Core was made
    quicken: int = 0                                  # turns left
    burning: int = 0                                  # ticks left


def _table(state) -> dict[int, EnemyDendro]:
    tbl = state.__dict__.get("_dendro")
    if tbl is None:
        tbl = {}
        state.__dict__["_dendro"] = tbl
    return tbl


def of(state, enemy) -> EnemyDendro:
    tbl = _table(state)
    d = tbl.get(id(enemy))
    if d is None:
        d = EnemyDendro()
        tbl[id(enemy)] = d
    return d


def peek(state, enemy) -> Optional[EnemyDendro]:
    """Read-only: the enemy's Dendro state, or None if it never had any."""
    tbl = state.__dict__.get("_dendro")
    return tbl.get(id(enemy)) if tbl else None


# ---------------------------------------------------------------------------
# the hit
# ---------------------------------------------------------------------------

def resolve_hit(state, enemy, element: str, damage: float, source: str,
                classic: Callable) -> float:
    """`reactions.resolve_hit` with Dendro in the world. `classic` is the
    shipped resolver, called for every pair that does not involve Dendro."""
    from tier0.engine import reactions            # late: reactions imports us
    d = of(state, enemy)

    # QUICKEN's rider (pick 3, canon gating): Electro and Dendro hits only.
    if element in ("electro", "dendro") and d.quicken > 0:
        damage += QUICKEN_BONUS
        state.emit("quicken_bonus", target=enemy.name, amount=QUICKEN_BONUS)

    # A Core popped early. OPEN READING: one Pyro or Electro hit pops ONE Core
    # (the oldest); the ruling says what a pop does, not how many a hit pops.
    if d.cores and element == "pyro":
        d.cores.pop(0)
        reactions.note_reaction(state, enemy, "burgeon", "pyro", "core")
        for other in list(state.living_enemies):
            _core_damage(state, other, CORE_BURST)
    elif d.cores and element == "electro":
        d.cores.pop(0)
        reactions.note_reaction(state, enemy, "hyperbloom", "electro", "core")
        _core_damage(state, enemy, CORE_BURST * HYPERBLOOM_MULT)

    aura = enemy.aura
    if element == "dendro" or aura == "dendro":
        return _dendro_pair(state, enemy, element, aura, damage, d)

    was_burning = d.burning > 0
    out = classic(state, enemy, element, damage, source)
    if was_burning:
        if element == "pyro":
            d.burning = BURNING_TURNS             # re-lit; the tick stays put
        elif enemy.aura != "pyro":
            # Another reaction consumed the Pyro Burning was holding.
            d.burning = 0
            state.emit("burning_ended", target=enemy.name, by=element)
    return out


def _set_aura(state, enemy, element: str) -> None:
    """`reactions.apply_aura` minus its AURA_ELEMENTS gate, which this module
    must not widen (the shipped set is pinned)."""
    from tier0.engine import reactions
    enemy.aura = element
    enemy.aura_turns_left = reactions.aura_duration(state)
    enemy.aura_spent = False
    state.emit("aura_applied", element=element, target=enemy.name,
               source="dendro")


def _dendro_pair(state, enemy, element: str, aura: Optional[str],
                 damage: float, d: EnemyDendro) -> float:
    from tier0.engine import reactions
    if aura is None:
        _set_aura(state, enemy, element)
        return damage
    if aura == element:                           # Dendro on Dendro: refresh
        enemy.aura_turns_left = reactions.aura_duration(state)
        enemy.aura_spent = False
        return damage
    other = aura if element == "dendro" else element
    if other in ("cryo", "anemo", "geo"):
        # Pick 2: a plain hit, and the standing aura stands.
        state.emit("no_reaction", trigger=element, aura=aura,
                   target=enemy.name)
        return damage
    # Every Dendro reaction consumes the aura (one-aura rule untouched).
    enemy.aura = None
    enemy.aura_turns_left = 0
    enemy.aura_spent = False
    if other == "hydro":
        _add_core(state, enemy, d)
        reactions.note_reaction(state, enemy, "bloom", element, aura)
    elif other == "electro":
        d.quicken = QUICKEN_TURNS
        reactions.note_reaction(state, enemy, "quicken", element, aura)
    elif other == "pyro":
        d.burning = BURNING_TURNS
        _set_aura(state, enemy, "pyro")            # Burning holds Pyro up
        reactions.note_reaction(state, enemy, "burning", element, aura)
    return damage


def _add_core(state, enemy, d: EnemyDendro) -> None:
    if len(d.cores) >= CORE_CAP:
        d.cores.pop(0)
        _plain_burst(state, enemy)
    d.cores.append(state.turn)
    state.emit("core_made", target=enemy.name, cores=len(d.cores))


def _plain_burst(state, enemy) -> None:
    from tier0.engine import reactions
    # "A Core bursting counts as a reaction, which is canon" (Nahida paper
    # sec.5); the ruling's sec.7.3 event names it an automatic source.
    reactions.note_reaction(state, enemy, "bloom_burst", "dendro", "core")
    _core_damage(state, enemy, CORE_BURST)


def _core_damage(state, enemy, amount: int) -> None:
    """Flat, pipeline-free, no aura, not an Attack -- and stopped by Block."""
    if not enemy.alive:
        return
    from tier0.engine import refpowers
    blocked = min(enemy.block, amount)
    enemy.block -= blocked
    hp_dmg = int(refpowers._intangible_cap(enemy, amount - blocked))
    effective = min(hp_dmg, max(0, enemy.hp))
    enemy.hp -= hp_dmg
    state.emit("damage", target=enemy.name, amount=effective,
               blocked=blocked, base=amount, source=SOURCE_CORE)


def _tick_damage(state, enemy, amount: int) -> None:
    if not enemy.alive:
        return
    from tier0.engine import refpowers
    blocked = min(enemy.block, amount)
    enemy.block -= blocked
    hp_dmg = int(refpowers._intangible_cap(enemy, amount - blocked))
    effective = min(hp_dmg, max(0, enemy.hp))
    enemy.hp -= hp_dmg
    state.emit("damage", target=enemy.name, amount=effective,
               blocked=blocked, base=amount, source=SOURCE_BURNING)


# ---------------------------------------------------------------------------
# the turn
# ---------------------------------------------------------------------------

def turn_start(state) -> None:
    """Player turn start: Quicken's clock. Quickened on turn T lasts T and
    T+1 (`QUICKEN_TURNS` = 2)."""
    if not DENDRO_ENGINE:
        return
    for e in state.living_enemies:
        d = peek(state, e)
        if d and d.quicken > 0:
            d.quicken -= 1


def turn_end(state) -> None:
    """End of the PLAYER's turn, before any enemy acts.

    Cores made on an earlier turn burst now ("at the end of your next
    turn"). Then Burning ticks. OPEN READING: the ruling gives Burning a tick
    per turn and no site; it ticks here, beside the Core, and refreshes the
    held Pyro aura each tick.
    """
    if not DENDRO_ENGINE:
        return
    for e in list(state.living_enemies):
        d = peek(state, e)
        if not d:
            continue
        due = [t for t in d.cores if t < state.turn]
        for _ in due:
            if not e.alive:
                break
            d.cores.pop(0)
            _plain_burst(state, e)
    for e in list(state.living_enemies):
        d = peek(state, e)
        if not d or d.burning <= 0:
            continue
        _tick_damage(state, e, BURNING_DOT)
        d.burning -= 1
        if e.alive:
            _set_aura(state, e, "pyro")
