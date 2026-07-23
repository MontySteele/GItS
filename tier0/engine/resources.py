"""Furina resources (kickoff §4): the Encore buffer and Fanfare stacks.

Deliberately low in the import graph (state + constants only) so both
effects.py and powers.py can use these hooks without a cycle.

Encore: unbounded per-combat buffer (v1.6 house style -- governed by
opportunity cost, made safe by the per-combat reset in run_fight). It
absorbs damage before HP; absorption emits its own event and is credited
to A4 sustain, NEVER A3 block (kickoff §2 harness note, Tier 0 binding --
without this accounting rule she grows a phantom third elite axis).

Fanfare: capped at a fraction of maxHP; generation is activity-based
ONLY (HP lost, Encore gained, Encore spent, Center Stage card played).
There is deliberately no per-turn passive accrual path in this module or
anywhere else -- passive accrual is stall payoff, and the healing policy
exists to kill exactly that. Payoff cards may spend the pool to reopen room
beneath its cap. The gate is Player.fanfare_cap (0 = the character has no
Fanfare resource; mirrors the burst_max pattern).
"""

from __future__ import annotations

from tier0 import constants as C
from tier0.engine.state import CombatState


def gain_fanfare(state: CombatState, n: int, source: str) -> None:
    p = state.player
    if not p.fanfare_cap or n <= 0:
        return
    before = p.fanfare
    p.fanfare = min(p.fanfare_cap, p.fanfare + n)
    if p.fanfare != before:
        state.emit("gain_fanfare", amount=p.fanfare - before, source=source,
                   total=p.fanfare)


def spend_fanfare(state: CombatState, n: int) -> int:
    """Pay a gated Fanfare cost and reopen room beneath the cap."""
    p = state.player
    spent = min(p.fanfare, n)
    if spent:
        p.fanfare -= spent
        state.emit("fanfare_spent", amount=spent, total=p.fanfare)
    return spent


def gain_encore(state: CombatState, n: int) -> None:
    p = state.player
    p.encore += n
    state.emit("gain_encore", amount=n, total=p.encore)
    gain_fanfare(state, n * C.FANFARE_PER_ENCORE_GAINED, "encore_gained")


def spend_encore(state: CombatState, n: int) -> int:
    """Drain up to n from the buffer; returns what was actually drained.
    Spending is Fanfare flux (the drain->refill->spend cycle) and burst
    particles (kickoff §1: her economy leans on Encore spend)."""
    p = state.player
    spent = min(p.encore, n)
    if spent:
        p.encore -= spent
        state.emit("encore_spent", amount=spent)
        gain_fanfare(state, spent * C.FANFARE_PER_ENCORE_SPENT, "encore_spent")
        if p.burst_max:
            p.burst_energy += spent * C.BURST_PER_ENCORE_SPENT
        # Standing Ovation, R32.1 FLIP (pass 3): the spend-payoff power.
        # Per spend EVENT (not per point -- points already pay Fanfare and
        # burst above), grant turn-scoped Spotlight percentage points
        # through the same §2.2a pipe. Direct dict add by design: this
        # module stays low in the import graph (no powers import), and
        # spotlight_mult_bonus_turn is uncapped-expiring (powers.EXPIRING
        # pops it at turn end).
        boost = p.powers.get("ovation_spend_boost", 0)
        if boost:
            p.powers["spotlight_mult_bonus_turn"] = (
                p.powers.get("spotlight_mult_bonus_turn", 0) + boost)
            state.emit("ovation_spend_boost", amount=boost)
    return spent


def spend_encore_or_hp(state: CombatState, n: int) -> None:
    """The overdraw primitive shared by the spend_encore op and the Salon
    tick upkeep: drain Encore first, any shortfall drains TRUE HP --
    greed is legal and priced (kickoff §4/§5)."""
    spent = spend_encore(state, n)
    short = n - spent
    if short:
        state.player.hp -= short
        state.emit("encore_overdraw", amount=short)
        note_player_hp_loss(state, short)


def absorb_into_encore(state: CombatState, dmg: int) -> int:
    """Route incoming player damage through the Encore buffer AFTER block.
    Returns the damage that still reaches HP. The emitted event is what
    metrics route to A4 -- it must never be folded into `blocked`."""
    p = state.player
    absorbed = min(p.encore, dmg)
    if absorbed:
        p.encore -= absorbed
        state.emit("encore_absorb", amount=absorbed)
    return dmg - absorbed


def note_player_hp_loss(state: CombatState, n: int) -> None:
    """Fanfare hook for TRUE HP loss (enemy hits reaching HP, DoT,
    self-damage, Encore overdraw). Callers deduct HP themselves; this
    only records the flux."""
    if n <= 0:
        return
    state.hp_lost_this_turn += n
    state.player_damage_events += 1
    gain_fanfare(state, n * C.FANFARE_PER_HP_LOST, "hp_lost")
