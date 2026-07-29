"""Furina resources (kickoff §4): the Encore buffer and Fanfare stacks.

Deliberately low in the import graph (state + constants only) so both
effects.py and powers.py can use these hooks without a cycle.

Encore: unbounded per-combat buffer (v1.6 house style -- governed by
opportunity cost, made safe by the per-combat reset in run_fight). It
absorbs damage before HP; absorption emits its own event and is credited
to A4 sustain, NEVER A3 block (kickoff §2 harness note, Tier 0 binding --
without this accounting rule she grows a phantom third elite axis).

Fanfare: a READ-ONLY momentum stat since "The Tide Turns" (2026-07-24).
Generation is activity-based ONLY; it DECAYS each turn from turn 2; and it
rests on a floor built from what her cards PRINT. Cards read it and gate on
it. **No card spends it** -- the spend grammar was retired because Encore
already is her spendable resource and a second one was a redundant system.

SINGLE-LEG since the Fanfare rework (2026-07-28, Track A, RULED). Fanfare
prints when Encore goes DOWN and never when it goes up, so the four sources
are now:

    hp_lost           true HP lost                      (note_player_hp_loss)
    encore_spent      deliberate spends and upkeep      (spend_encore)
    encore_absorbed   the buffer eating a hit           (absorb_into_encore)
    center_stage      a card played while SHE holds it  (spotlight)

`encore_gained` is GONE. All four are INDIRECT -- nothing hands the player
transient Fanfare outright -- which is the property the "Fanfare +X" keyword
convention rests on and tools/lint_furina_registers.py L12 enforces.

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


def note_fanfare_change(state: CombatState, before: int) -> None:
    """A7 (Unheard Confession, 2026-07-28): pay Block whenever the meter MOVES.

    Every fanfare mutation in the sim funnels through this module -- gain,
    decay, floor-raise -- so calling this at each of those three sites is the
    whole trigger surface, and a fourth mutation added later without a call
    here is the only way to break it.

    Fires on a change in EITHER direction. The ruling's wording is "whenever
    Fanfare changes amount", and the decay half is what makes the power more
    than a second gain-rider: her meter fades 20% every turn from turn 2, so
    the card pays on the way down as well as the way up.

    A gain that lands entirely at the cap is NOT a change (applied == 0), so
    a saturated meter stops paying -- deliberate, and the same saturation the
    pass-4 telemetry made visible.

    Unscaled printed number, following salon_bow_block: this is a power's
    activity payout, not a card's printed Block, so Spotlight does not read it.
    """
    n = state.player.powers.get("fanfare_delta_block", 0)
    if not n or state.player.fanfare == before:
        return
    state.player.block += n
    state.emit("block", amount=n)
    state.emit("fanfare_delta_block", amount=n)


def gain_fanfare(state: CombatState, n: int, source: str) -> None:
    p = state.player
    if not p.fanfare_cap or n <= 0:
        return
    before = p.fanfare
    p.fanfare = min(p.fanfare_cap, p.fanfare + n)
    applied = p.fanfare - before
    note_fanfare_change(state, before)
    # Pass 4 Q1a: the clamp used to be SILENT -- only `amount` (what landed)
    # was emitted, so generation thrown away at the cap left no trace and no
    # sweep could see saturation. `requested`/`wasted` are the overflow read;
    # a fully-wasted gain emits too, which is exactly the case that matters.
    state.emit("gain_fanfare", amount=applied, source=source,
               total=p.fanfare, requested=n, wasted=n - applied)


def _decay_amount(p) -> int:
    """How much the meter fades this turn: PROPORTIONAL, always.

    R67 (2026-07-26) deleted the flat shape outright. There used to be a
    second branch here returning FANFARE_DECAY_PER_TURN whenever the
    fraction was 0, described as "one shape at a time so a sweep can switch
    shapes" -- but the 20% ruling made the fraction permanently nonzero, so
    the flat branch was unreachable and the sweep that switched shapes
    reported five identical rows. The ruled world is 20% proportional, full
    stop, and it is now the only world this function can express.

    The proportional form takes its cut of the WHOLE meter and lets the
    floor clamp protect the baseline, rather than taking a cut of the amount
    above the floor. That keeps the player-facing rule to one line ("Fanfare
    fades by N% each turn") which is the entire argument the flat shape won
    on; a rule that reads "N% of the amount above your baseline" gives back
    the legibility the flat form was chosen for.

    At least 1 always comes off while above the floor, so a small meter
    cannot stall at a value that rounds down to nothing.
    """
    if p.fanfare <= p.fanfare_floor:
        return 0
    return max(1, round(p.fanfare * C.FANFARE_DECAY_FRACTION))


def decay_fanfare(state: CombatState) -> None:
    """F-A1: the meter fades each turn, never below the floor.

    Applied at the START of the player turn and only from turn 2, so the
    opening hand plays against what the player actually built rather than
    against an immediate tax. PROPORTIONAL (20% of current, min 1) by
    [USER] ruling 2026-07-24 -- see FANFARE_DECAY_FRACTION, which REVERSED
    the plan's flat-over-proportional direction. The flat alternative it
    reversed no longer exists in the tree at all: R67 deleted the knob and
    its unreachable branch (audit 2026-07-26 §2.1).

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
    note_fanfare_change(state, before)


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
    before = p.fanfare
    p.fanfare_floor += n
    p.fanfare_cap += n
    p.fanfare = min(p.fanfare_cap, p.fanfare + n)
    note_fanfare_change(state, before)
    state.emit("fanfare_floor_granted", amount=n, source=source,
               floor=p.fanfare_floor, cap=p.fanfare_cap, total=p.fanfare)


def raise_fanfare_cap(state: CombatState, n: int, source: str) -> None:
    """The **Fanfare Cap +X** keyword: headroom only (Track B, 2026-07-28).

    The deliberate contrast with gain_fanfare_floor above, which moves all
    three numbers. Nothing is granted here; the meter is only allowed to go
    further if activity takes it there.

    See effects._op_raise_fanfare_cap for the standing measurement note --
    the cap has not been a binding number since F-A5, so this keyword is the
    cheap half of the pair by construction rather than by tuning.
    """
    p = state.player
    if not p.fanfare_cap or n <= 0:
        return                    # inert for everyone without the resource
    p.fanfare_cap += n
    state.emit("fanfare_cap_raised", amount=n, source=source,
               cap=p.fanfare_cap, total=p.fanfare)


def drop_fanfare_to_floor(state: CombatState, floor_drop: int,
                          source: str) -> int:
    """The Hyperbeam settle (Track C.2, 2026-07-28): crash the meter, then
    dig the floor out from under it. Returns what the meter fell by.

    THE FLOOR MAY GO NEGATIVE, and that is RULED rather than tolerated. A
    negative floor is a hole the player climbs out of with activity: decay
    still clamps to it exactly as before, so a meter at -12 sits at -12 and
    every point of generation counts against the debt.

    READERS CLAMP. Every consumer of the meter -- the Salon Focus term, the
    bonus_formula riders, the fanfare_at_least predicates -- reads
    `max(0, fanfare)`, so a negative meter turns effects OFF rather than
    inverting them. That is a PROPOSED semantic, flagged at review: the
    harsher StS-style inversion (members ticking for negative numbers) is a
    one-line flip in `readable`, and negative member ticks chipping the stage
    would read as a bug rather than as a cost.

    The cap is deliberately NOT lowered. The floor falling is the price; the
    ceiling falling too would make the card quietly worse the second time it
    is played in a combat, which is a different card.
    """
    p = state.player
    if not p.fanfare_cap:
        return 0
    before = p.fanfare
    p.fanfare_floor -= floor_drop
    p.fanfare = max(p.fanfare_floor, min(p.fanfare, p.fanfare_floor))
    note_fanfare_change(state, before)
    state.emit("fanfare_crashed", amount=before - p.fanfare, source=source,
               floor=p.fanfare_floor, total=p.fanfare)
    return before - p.fanfare


def readable(player) -> int:
    """What a Fanfare READER sees: the meter, clamped at zero.

    The single chokepoint for the Track C.2 negative-floor semantics. Every
    reader goes through here so "effects shut off, they do not invert" is one
    fact in one place, and so the [USER] flip to StS-style inversion at
    review is a one-line change rather than a hunt.

    Deliberately takes a PLAYER rather than a CombatState: several readers
    (the pilot's valuation terms, the C# mirror's tests) hold a player and no
    state, and a signature that forced them to fabricate one would have
    guaranteed the clamp got skipped somewhere.
    """
    return max(0, player.fanfare)


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
    """Fill the buffer. Prints NO Fanfare (Track A, RULED 2026-07-28).

    Fanfare prints when Encore goes DOWN, never when it goes up. The
    `encore_gained` leg used to mint here, which made every Encore point pay
    the meter twice -- once arriving, once leaving -- and that double-count
    was 47% of all generation under the greedy pilot and 62% under the
    stoker. A flywheel whose majority output is itself is not a flywheel with
    a tuning problem; it is a flywheel with a shape problem.
    """
    p = state.player
    p.encore += n
    state.emit("gain_encore", amount=n, total=p.encore)


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
            gain_burst(state, spent * C.BURST_PER_ENCORE_SPENT,
                       "encore_spent")
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
        # The Gallery Stirs (Curtain Call B/C, R85): the FIRST spend event
        # each turn draws. Activity-gated by construction -- a turn that
        # spends nothing draws nothing (the sheet header's no-passive-accrual
        # law) -- and once-per-turn so the flux plan cannot loop it into a
        # draw engine the way a per-event rate would.
        n = p.powers.get("encore_spend_draw", 0)
        if n and state.encore_spend_draws_this_turn == 0:
            state.encore_spend_draws_this_turn = 1
            state.draw(n)
            state.emit("extra_draw", amount=n)
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
    metrics route to A4 -- it must never be folded into `blocked`.

    PRINTS FANFARE since Track A (RULED 2026-07-28). Absorption is the third
    Encore REDUCTION path and it used to be the only one worth nothing, which
    was an asymmetry rather than a rule: absorbed Encore is deferred Block
    that will never block a future hit, so cashing it is a real cost and the
    audience sees the same wound either way.

    That is what makes the post-Track-A rule sayable in one line: every point
    of damage past Block prints exactly 1 Fanfare -- through here if the
    buffer eats it, through note_player_hp_loss if HP does. Before this
    change absorbed damage printed 0 and the same hit paid differently
    depending on a buffer the player could not see the far side of.
    """
    p = state.player
    absorbed = min(p.encore, dmg)
    if absorbed:
        p.encore -= absorbed
        state.emit("encore_absorb", amount=absorbed)
        gain_fanfare(state, absorbed * C.FANFARE_PER_ENCORE_ABSORBED,
                     "encore_absorbed")
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


def gain_burst(state: CombatState, n: int, source: str) -> None:
    """Burst energy, with the SOURCE recorded (C5, Neap Tide v2.1).

    Deliberately shaped like `gain_charge` above: same signature, same emit
    grammar, so the two meters can be read with one habit.

    WHY IT EXISTS. Burst income arrived at ten scattered `p.burst_energy +=`
    sites across five modules, none of which said where the energy came from.
    "How does her meter actually fill?" was therefore unanswerable from the
    log -- you could see the meter move and not what moved it -- and P8 is a
    claim about exactly that (mustered-companion exhausts should be top-two
    income in commander decks). A prediction that cannot be read off the
    instrument is not gradeable.

    The `burst_max` gate stays at the CALL SITES rather than moving in here.
    It reads as a natural thing to centralise and it is not: several callers
    do other work under the same gate, so folding it in would leave those
    conditionals half-migrated and their intent less obvious, not more.

    R14: diagnostic. Nothing reads these events to make a decision.
    """
    if n <= 0:
        return
    p = state.player
    p.burst_energy += n
    state.emit("burst_income", amount=n, source=source,
               total=p.burst_energy)


def note_player_hp_loss(state: CombatState, n: int) -> None:
    """Fanfare hook for TRUE HP loss (enemy hits reaching HP, DoT,
    self-damage, Encore overdraw). Callers deduct HP themselves; this
    only records the flux."""
    if n <= 0:
        return
    state.hp_lost_this_turn += n
    state.player_damage_events += 1
    gain_fanfare(state, n * C.FANFARE_PER_HP_LOST, "hp_lost")
