"""Furina resources (kickoff §4): the Encore buffer and Fanfare stacks.

Deliberately low in the import graph (state + constants only) so both
effects.py and powers.py can use these hooks without a cycle.

Encore: unbounded per-combat buffer (v1.6 house style -- governed by
opportunity cost, made safe by the per-combat reset in run_fight). It
absorbs damage before HP; absorption emits its own event and is credited
to A4 sustain, NEVER A3 block (kickoff §2 harness note, Tier 0 binding --
without this accounting rule she grows a phantom third elite axis).

Fanfare: a READ-ONLY momentum stat since "The Tide Turns" (2026-07-24).
Generation is activity-based ONLY (HP lost, Encore gained, Encore spent,
Center Stage card played); it DECAYS each turn from turn 2; and it rests on
a permanent floor built from constellation grants. Cards read it and gate on
it. **No card spends it** -- the spend grammar was retired because Encore
already is her spendable resource and a second one was a redundant system.

There is deliberately no per-turn passive ACCRUAL path in this module or
anywhere else -- passive accrual is stall payoff, and the healing policy
exists to kill exactly that. A floor is not accrual: it is static value that
does not grow with time, so stalling still earns nothing.

The gate is Player.fanfare_cap (0 = the character has no Fanfare resource;
mirrors the burst_max pattern). The cap itself is now a high safety rail
rather than a design dial -- under decay the ceiling does not bind.
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
    applied = p.fanfare - before
    # Pass 4 Q1a: the clamp used to be SILENT -- only `amount` (what landed)
    # was emitted, so generation thrown away at the cap left no trace and no
    # sweep could see saturation. `requested`/`wasted` are the overflow read;
    # a fully-wasted gain emits too, which is exactly the case that matters.
    state.emit("gain_fanfare", amount=applied, source=source,
               total=p.fanfare, requested=n, wasted=n - applied)


def _decay_amount(p) -> int:
    """How much the meter fades this turn: flat, or proportional when the
    fraction knob is armed. One shape at a time -- the fraction takes
    precedence so a sweep can switch shapes without touching the flat value
    it is being compared against.

    The proportional form takes its cut of the WHOLE meter and lets the
    floor clamp protect the baseline, rather than taking a cut of the amount
    above the floor. That keeps the player-facing rule to one line ("Fanfare
    fades by N% each turn") which is the entire argument the flat shape won
    on; a rule that reads "N% of the amount above your baseline" gives back
    the legibility the flat form was chosen for.

    At least 1 always comes off while above the floor, so a small meter
    cannot stall at a value that rounds down to nothing.
    """
    if C.FANFARE_DECAY_FRACTION > 0:
        if p.fanfare <= p.fanfare_floor:
            return 0
        return max(1, round(p.fanfare * C.FANFARE_DECAY_FRACTION))
    return C.FANFARE_DECAY_PER_TURN


def decay_fanfare(state: CombatState) -> None:
    """F-A1: the meter fades each turn, never below the floor.

    Applied at the START of the player turn and only from turn 2, so the
    opening hand plays against what the player actually built rather than
    against an immediate tax. Flat rather than proportional by ratified
    design -- see FANFARE_DECAY_PER_TURN for why the tooltip argument won.

    This is the load-bearing half of the read-only rework: without it the
    pool sits pinned at its ceiling and every card that "scales with
    Fanfare" is a constant wearing a meter.
    """
    p = state.player
    if not p.fanfare_cap or state.turn < 2:
        return
    before = p.fanfare
    p.fanfare = max(p.fanfare_floor, p.fanfare - _decay_amount(p))
    # Emitted even when nothing fell: "the meter was already resting on its
    # floor" is a distinct and interesting state from "the meter decayed",
    # and a silent no-op would make the two indistinguishable downstream --
    # the exact mistake the pass-4 clamp made.
    state.emit("fanfare_decay", amount=before - p.fanfare, total=p.fanfare,
               floor=p.fanfare_floor, at_floor=p.fanfare <= p.fanfare_floor)


def gain_fanfare_floor(state: CombatState, n: int, source: str) -> None:
    """F-A3: a permanent constellation grant.

    Raises floor, cap AND current together. Raising the cap alongside the
    floor is load-bearing rather than bookkeeping: a floor that pushed
    current up toward an unmoved ceiling would simply re-pin the meter, and
    keeping the two apart is what preserved the gradient in W2.

    LEGAL under the no-passive-accrual law (kickoff §4): a floor is STATIC
    value, not accrual -- it does not grow with time, so stalling still
    earns nothing. The law is intact, not amended. Stated here because a
    floor superficially resembles the per-turn accrual §4 bans forever, and
    the distinction is the whole reason this package is allowed to exist.
    """
    p = state.player
    if not p.fanfare_cap or n <= 0:
        return                    # inert for everyone without the resource
    p.fanfare_floor += n
    p.fanfare_cap += n
    p.fanfare = min(p.fanfare_cap, p.fanfare + n)
    state.emit("fanfare_floor_granted", amount=n, source=source,
               floor=p.fanfare_floor, cap=p.fanfare_cap, total=p.fanfare)


def note_fanfare_read(state: CombatState, kind: str) -> None:
    """Instrument for the gate that asks whether the stat is LIVE.

    Sampled where a card actually READS the meter, which is not the same
    place as the turn-start snapshot: the pool refills mid-turn and spills,
    so a turn-start sample can look healthy while every read still lands on
    a pinned meter. Pass 4 measured both and they disagreed by 25 points.

    Records BOTH pins. At-cap alone cannot see the floor-stacking failure
    mode, because a grant raises the cap alongside the floor -- so a meter
    pinned on its floor never reads at-cap, and a gate written only against
    at-cap would stay silent through exactly the risk it was written for.
    """
    p = state.player
    if not p.fanfare_cap:
        return
    state.emit("fanfare_read", kind=kind, total=p.fanfare, cap=p.fanfare_cap,
               floor=p.fanfare_floor, at_cap=p.fanfare >= p.fanfare_cap,
               at_floor=p.fanfare <= p.fanfare_floor)


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


def gain_charge(state: CombatState, n: int, source: str) -> None:
    """Kokomi's Charge (kickoff v1 §2.1): uncapped, never expended,
    card-event-driven only. Callers gate on the tamakushi_casket relic
    hook (the accrual laws live ON the relic; a player without it has no
    Charge engine and this is never reached). No passive per-turn accrual
    path exists in this module or anywhere else — same law as Fanfare
    above, same reason (stall payoff), deliberately not designed."""
    if n <= 0:
        return
    p = state.player
    p.charge += n
    state.emit("gain_charge", amount=n, source=source, total=p.charge)


def note_player_hp_loss(state: CombatState, n: int) -> None:
    """Fanfare hook for TRUE HP loss (enemy hits reaching HP, DoT,
    self-damage, Encore overdraw). Callers deduct HP themselves; this
    only records the flux."""
    if n <= 0:
        return
    state.hp_lost_this_turn += n
    state.player_damage_events += 1
    gain_fanfare(state, n * C.FANFARE_PER_HP_LOST, "hp_lost")
