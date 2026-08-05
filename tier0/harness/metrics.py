"""Per-fight stat extraction from the event log (spec §2 feeds off this).

M1 ships the raw per-fight stats + degeneracy flags; the 7-axis
normalization lands in M2 once the battery exists to calibrate against.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tier0 import constants as C
from tier0.engine.state import CombatState


@dataclass
class FightStats:
    won: bool
    turns: int
    hp_start: int
    hp_end: int
    total_damage_dealt: int
    damage_by_turn: dict[int, int]
    energy_by_turn: dict[int, int]
    total_block_gained: int
    damage_blocked: int             # enemy damage absorbed by player block
    energy_spent: int
    cards_drawn_extra: int          # draws beyond the base 5/turn
    energy_generated_extra: int     # energy beyond the base 3/turn
    healing: int                    # A4: healing done (incl. post-fight)
    encore_absorbed: int            # A4: chip absorbed by Encore (kickoff
                                    # §2 harness note, BINDING: never A3)
    debuff_stacks_applied: int      # A6: weak+vuln stacks put on enemies
    debuffed_intents: int           # enemy intents taken while weak/vuln
    aura_intents: int               # A6 v2 (R18): intents taken while
                                    # the actor carried an elemental aura
    total_intents: int
    reactions: int
    reaction_damage: int
    auras_wasted: int
    cards_played: int = 0
    # --- Kokomi telemetry (kickoff §7). prevented is REPORTED ONLY: not
    # folded into damage_blocked and not credited to A4 — axis credit for
    # ward prevention is a metric-redefinition and therefore red-pen (the
    # Encore-accounting precedent). charge_gained is the meter's flux;
    # engine_closure_turns counts the report-only R14 diagnostic. ---
    prevented: int = 0              # damage prevented by the exhaust ward
    charge_gained: int = 0          # total Charge accrued this fight
    engine_closure_turns: int = 0   # turns flagged by the v0 detector
    regrets: int = 0                # pilot_regret samples (spec §6)
    enemy_actions: int = 0          # intents taken + sleep skips (§2.2a)
    control_negated: float = 0.0    # action-equivalents negated by
                                    # COMPANION-sourced control (frozen
                                    # attack = 0.5; future full stuns = 1.0)
    # --- HP trajectory (Kokomi stability instrument, 2026-07-29). Player HP
    # at the END of each round, in round order; `hp_start` is the value before
    # round 1, so the full trajectory is [hp_start, *hp_by_round]. A LIST and
    # not a turn-keyed dict like damage_by_turn: the ordering IS the datum, and
    # merging staged fights is then concatenation rather than key arithmetic.
    # Read only by tier05.run_metrics.trajectory_profile -- REPORTED, never
    # banded (band declaration is a [USER] ruling; R51/D5).
    hp_by_round: list[int] = field(default_factory=list)
    # --- D1, reactions share-of-damage (Last Call track D, 2026-08-05). The
    # THREE ways a reaction puts damage on the board, kept apart because they
    # are not the same claim and a future session will want to say which one it
    # is talking about:
    #   amp    -- the Vaporize/Melt multiplier's DELTA over the unamplified hit
    #             (the base hit is a base op's damage; only the uplift is the
    #             reaction's), read off the `reaction` event's amp_delta;
    #   splash -- Overload's explosion, overkill-clamped at the emit site;
    #   dot    -- Electro-Charged's DoT ticking on an ENEMY. This one is NOT
    #             inside total_damage_dealt: dot_tick is not a `damage` event,
    #             so the denominator has to be widened for it -- see
    #             damage_all_ops.
    # `reaction_damage` above is amp + splash and keeps its exact pre-instrument
    # value: it feeds the ratified A6 axis and summarize()'s
    # reaction_damage_share, and this track moves no number that anything reads.
    reaction_damage_amp: int = 0
    reaction_damage_splash: int = 0
    reaction_damage_dot: int = 0
    # --- D2, the per-turn record (same track). One row per player turn:
    #   [turn, hp_at_open, block_at_open, block_at_end, hits_in, damage_in]
    # `hp_at_open`/`block_at_open` are the `turn_open` sample (block here is
    # what SURVIVED the enemy, not what the player built); `block_at_end` is the
    # `turn_close` sample, or -1 when the turn never closed because the fight
    # ended inside it. `hits_in`/`damage_in` are the enemy phase that FOLLOWED
    # this player turn: how many attack hits landed and their total arriving
    # damage BEFORE block/ward/Encore. A list of small lists, not a dict: the
    # ordering is the datum and merging staged fights is then concatenation
    # (the hp_by_round precedent above). tier0 models ONE seat, so there is no
    # per-seat axis here; a seat dimension is a co-op instrument and is not
    # invented by a one-seat sim.
    turn_trajectory: list[list[int]] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)

    @property
    def hp_delta(self) -> int:
        return self.hp_end - self.hp_start

    @property
    def damage_from_reactions(self) -> int:
        """Absolute damage attributable to reaction ops (D1 numerator)."""
        return (self.reaction_damage_amp + self.reaction_damage_splash
                + self.reaction_damage_dot)

    @property
    def damage_all_ops(self) -> int:
        """D1 denominator: every point of damage the player put on an enemy.
        total_damage_dealt PLUS the enemy-side DoT, which the `damage` event
        stream never carried."""
        return self.total_damage_dealt + self.reaction_damage_dot

    @property
    def damage_from_base_ops(self) -> int:
        return self.damage_all_ops - self.damage_from_reactions

    @property
    def reaction_share(self) -> float:
        """Reaction damage / all damage, this fight. 0.0 on a zero-damage
        fight -- an undefined share is reported as no share, never as 1.0."""
        return self.damage_from_reactions / max(1, self.damage_all_ops)


def merge_stages(stages: list["FightStats"]) -> "FightStats":
    """Merge back-to-back stage fights (GAUNTLET) into one fight record.
    Later stages' turn numbers are offset so the damage curve is continuous."""
    if len(stages) == 1:
        return stages[0]
    merged = stages[0]
    for s in stages[1:]:
        offset = merged.turns
        for t, v in s.damage_by_turn.items():
            merged.damage_by_turn[t + offset] = v
        for t, v in s.energy_by_turn.items():
            merged.energy_by_turn[t + offset] = v
        # Concatenation, not key-offsetting: a staged gauntlet's HP curve runs
        # continuously across the stage break (stage 2 opens on stage 1's HP),
        # so the rounds simply follow one another.
        merged.hp_by_round = list(merged.hp_by_round) + list(s.hp_by_round)
        # Turn rows carry their turn number, so unlike hp_by_round they are
        # offset as well as concatenated -- a gauntlet's stage-2 turn 1 is the
        # run's turn (stage-1 turns + 1), matching damage_by_turn.
        merged.turn_trajectory = list(merged.turn_trajectory) + [
            [row[0] + offset, *row[1:]] for row in s.turn_trajectory]
        merged.turns += s.turns
        merged.hp_end = s.hp_end
        merged.total_damage_dealt += s.total_damage_dealt
        merged.total_block_gained += s.total_block_gained
        merged.damage_blocked += s.damage_blocked
        merged.energy_spent += s.energy_spent
        merged.cards_drawn_extra += s.cards_drawn_extra
        merged.energy_generated_extra += s.energy_generated_extra
        merged.healing += s.healing
        merged.encore_absorbed += s.encore_absorbed
        merged.debuff_stacks_applied += s.debuff_stacks_applied
        merged.debuffed_intents += s.debuffed_intents
        merged.aura_intents += s.aura_intents
        merged.total_intents += s.total_intents
        merged.reactions += s.reactions
        merged.reaction_damage += s.reaction_damage
        merged.reaction_damage_amp += s.reaction_damage_amp
        merged.reaction_damage_splash += s.reaction_damage_splash
        merged.reaction_damage_dot += s.reaction_damage_dot
        merged.auras_wasted += s.auras_wasted
        merged.cards_played += s.cards_played
        merged.prevented += s.prevented
        merged.charge_gained += s.charge_gained
        merged.engine_closure_turns += s.engine_closure_turns
        merged.regrets += s.regrets
        merged.enemy_actions += s.enemy_actions
        merged.control_negated += s.control_negated
        merged.flags = sorted(set(merged.flags) | set(s.flags))
    merged.won = all(s.won for s in stages)
    return merged


def extract(state: CombatState, hp_start: int) -> FightStats:
    dmg_by_turn: dict[int, int] = {}
    energy_by_turn: dict[int, int] = {}
    total_dmg = block = blocked = energy = 0
    extra_draws = extra_energy = healing = encore_absorbed = debuff_stacks = 0
    debuffed_intents = aura_intents = total_intents = cards_played = 0
    regrets = 0
    prevented = charge_gained = engine_closure_turns = 0
    reactions = reaction_dmg = auras_wasted = sleeps = 0
    control_negated = 0.0
    react_amp = react_splash = react_dot = 0
    flags: list[str] = []
    hp_by_round: list[int] = []
    # D2: per-turn accumulators, keyed by turn number. Turn-keyed dicts, not a
    # row appended per event -- the same shape damage_by_turn/energy_by_turn
    # already use, so the hot path stays one integer add per event.
    turn_open: dict[int, tuple[int, int]] = {}
    turn_close: dict[int, int] = {}
    hits_in: dict[int, int] = {}
    damage_in: dict[int, int] = {}
    won = False
    turns = state.turn

    for ev in state.log:
        e = ev["event"]
        if e == "damage":
            total_dmg += ev["amount"]
            dmg_by_turn[ev["turn"]] = dmg_by_turn.get(ev["turn"], 0) + ev["amount"]
            if ev.get("source") == "reaction_splash":
                reaction_dmg += ev["amount"]
                react_splash += ev["amount"]
        elif e == "block":
            block += ev["amount"]
        elif e == "player_hit":
            blocked += ev["blocked"]
            t = ev["turn"]
            hits_in[t] = hits_in.get(t, 0) + 1
            damage_in[t] = damage_in.get(t, 0) + ev.get("incoming", 0)
        elif e == "turn_open":
            turn_open[ev["turn"]] = (ev["hp"], ev["block"])
        elif e == "turn_close":
            turn_close[ev["turn"]] = ev["block"]
        elif e == "dot_tick":
            # Enemy-side DoT is Electro-Charged's and nothing else's (the only
            # apply_power("dot") on an enemy in the sim is reactions._react).
            if not ev.get("to_player", True):
                react_dot += ev.get("effective", ev["amount"])
        elif e == "play":
            energy += ev["cost"]
            cards_played += 1
            energy_by_turn[ev["turn"]] = (energy_by_turn.get(ev["turn"], 0)
                                          + ev["cost"])
        elif e == "pilot_regret":
            regrets += 1
        elif e == "extra_draw":
            extra_draws += ev["amount"]
        elif e == "add_card" and ev["to"] == "hand":
            extra_draws += 1        # tokens-to-hand are velocity (A5)
        elif e == "energy":
            extra_energy += ev["amount"]
        elif e == "heal":
            healing += ev["amount"]
        elif e == "encore_absorb":
            encore_absorbed += ev["amount"]
        elif e == "prevent_exhaust":
            prevented += ev["amount"]
        elif e == "gain_charge":
            charge_gained += ev["amount"]
        elif e == "engine_closure":
            engine_closure_turns += 1
        elif e == "apply_power":
            if ev["power"] in ("weak", "vulnerable") and ev["target"] != "player":
                debuff_stacks += ev["stacks"]
        elif e == "intent":
            total_intents += 1
            if ev["debuffed"]:
                debuffed_intents += 1
            if ev.get("aura"):          # A6 v2 (R18) application uptime
                aura_intents += 1
        elif e == "enemy_sleep":
            sleeps += 1             # scripted self-sleep: an action, but
                                    # never companion-sourced negation
        elif e == "frozen_action":
            # §2.2a control_uptime: a frozen attack is half-negated.
            if ev["kind"] == "attack" and ev["by_companion"]:
                control_negated += 1 - C.FROZEN_DAMAGE_MULT
        elif e == "reaction":
            reactions += 1
            reaction_dmg += int(ev["amp_delta"])
            react_amp += int(ev["amp_delta"])
        elif e == "aura_wasted":
            auras_wasted += 1
        elif e == "round_hp":
            hp_by_round.append(ev["hp"])
        elif e == "degeneracy":
            flags.append(ev["kind"])
        elif e == "amp_stack_warning":
            flags.append("AMP_STACK")
        elif e == "fight_end":
            won = ev["won"]
            turns = ev["turns"]

    # D2: one row per player turn that actually opened. -1 for block_at_end
    # marks a turn the fight ended inside -- an unsampled value, never a zero.
    turn_trajectory = [
        [t, turn_open[t][0], turn_open[t][1], turn_close.get(t, -1),
         hits_in.get(t, 0), damage_in.get(t, 0)]
        for t in sorted(turn_open)]

    t3 = sum(dmg_by_turn.get(t, 0) for t in (1, 2, 3)) / 3
    t10 = sum(dmg_by_turn.get(t, 0) for t in (8, 9, 10)) / 3
    if t3 > 0 and t10 / t3 > C.RUNAWAY_SCALING_RATIO:
        flags.append("SUPERLINEAR")

    enemy_actions = total_intents + sleeps
    # §2.2a: a won fight where companions negated most of the enemy's
    # output means the supports were the key ingredient.
    if (won and enemy_actions
            and control_negated / enemy_actions > C.CONTROL_UPTIME_CARRY):
        flags.append("SUPPORT_CARRY")

    return FightStats(
        won=won, turns=turns, hp_start=hp_start,
        hp_end=max(0, state.player.hp),
        total_damage_dealt=total_dmg, damage_by_turn=dmg_by_turn,
        energy_by_turn=energy_by_turn,
        total_block_gained=block, damage_blocked=blocked,
        energy_spent=energy,
        cards_drawn_extra=extra_draws, energy_generated_extra=extra_energy,
        healing=healing, encore_absorbed=encore_absorbed,
        debuff_stacks_applied=debuff_stacks,
        debuffed_intents=debuffed_intents, aura_intents=aura_intents,
        total_intents=total_intents,
        reactions=reactions,
        reaction_damage=reaction_dmg, auras_wasted=auras_wasted,
        cards_played=cards_played, prevented=prevented,
        charge_gained=charge_gained,
        engine_closure_turns=engine_closure_turns, regrets=regrets,
        enemy_actions=enemy_actions, control_negated=control_negated,
        hp_by_round=hp_by_round,
        reaction_damage_amp=react_amp,
        reaction_damage_splash=react_splash,
        reaction_damage_dot=react_dot,
        turn_trajectory=turn_trajectory,
        flags=sorted(set(flags)))


def summarize(all_stats: list[FightStats]) -> dict:
    n = len(all_stats)
    if n == 0:
        return {}
    wins = sum(s.won for s in all_stats)
    return {
        "fights": n,
        "winrate": wins / n,
        "avg_turns": sum(s.turns for s in all_stats) / n,
        "avg_hp_delta": sum(s.hp_delta for s in all_stats) / n,
        "avg_dpt": sum(s.total_damage_dealt / max(1, s.turns)
                       for s in all_stats) / n,
        "avg_energy_per_turn": sum(s.energy_spent / max(1, s.turns)
                                   for s in all_stats) / n,
        "reactions_per_fight": sum(s.reactions for s in all_stats) / n,
        # Spec §4.4: healthy reaction-archetype = 25-45% damage share;
        # aura starvation (spec §8) = reaction-deck fights with 0 reactions.
        "reaction_damage_share": (sum(s.reaction_damage for s in all_stats)
                                  / max(1, sum(s.total_damage_dealt
                                               for s in all_stats))),
        "aura_starved_fights": sum(1 for s in all_stats
                                   if s.reactions == 0) / n,
        "auras_wasted_per_fight": sum(s.auras_wasted for s in all_stats) / n,
        "pilot_regret_rate": (sum(s.regrets for s in all_stats)
                              / max(1, sum(s.cards_played for s in all_stats))),
        # §2.2a: fraction of enemy actions negated by companion control.
        "control_uptime": (sum(s.control_negated for s in all_stats)
                           / max(1, sum(s.enemy_actions for s in all_stats))),
        "flagged_fights": sum(1 for s in all_stats if s.flags),
        "flags": sorted({f for s in all_stats for f in s.flags}),
    }


def reaction_share(all_stats: list[FightStats]) -> dict:
    """D1's aggregate hook: reactions' share of total damage across a battery,
    in one call.

    POOLED, not averaged over fights: sum(reaction) / sum(all), so a 6-damage
    fight does not weigh as much as a 300-damage one. `share_by_fight_mean` is
    the per-fight mean alongside it, because the two answer different questions
    and a report that quotes one without saying which is unreadable.

    Reports numbers only. Whether a share is high or low is a design reading and
    is not made here; `summarize()["reaction_damage_share"]` is the OLDER,
    narrower figure (amp + splash over total_damage_dealt) and is left alone --
    it feeds the ratified A6 axis, and this function is not a redefinition of
    it. Where they disagree, the difference is exactly the Electro-Charged DoT.
    """
    n = len(all_stats)
    if n == 0:
        return {}
    total = sum(s.damage_all_ops for s in all_stats)
    react = sum(s.damage_from_reactions for s in all_stats)
    return {
        "fights": n,
        "damage_all_ops": total,
        "damage_from_reactions": react,
        "damage_from_base_ops": total - react,
        "share": react / max(1, total),
        "share_by_fight_mean": sum(s.reaction_share for s in all_stats) / n,
        "amp": sum(s.reaction_damage_amp for s in all_stats),
        "splash": sum(s.reaction_damage_splash for s in all_stats),
        "dot": sum(s.reaction_damage_dot for s in all_stats),
        "fights_with_any_reaction_damage": sum(
            1 for s in all_stats if s.damage_from_reactions),
    }


def turn_profile(all_stats: list[FightStats]) -> dict[int, dict]:
    """D2's aggregate hook: the per-turn record pooled across a battery.

    Keyed by turn number; every figure is a mean over the fights that REACHED
    that turn, and `fights` is how many those were. Never interpolated and never
    carried across from a neighbouring turn -- a turn no fight reached is simply
    absent, the same rule the Track B curve tables run on. `block_at_end` skips
    the -1 rows (turns the fight ended inside), and `block_end_samples` says how
    many rows survived that filter, so a mean over two turns is not mistaken for
    a mean over two hundred.
    """
    rows: dict[int, list[list[int]]] = {}
    for s in all_stats:
        for row in s.turn_trajectory:
            rows.setdefault(row[0], []).append(row)
    out: dict[int, dict] = {}
    for turn in sorted(rows):
        rs = rows[turn]
        closed = [r[3] for r in rs if r[3] >= 0]
        out[turn] = {
            "fights": len(rs),
            "mean_hp_at_open": sum(r[1] for r in rs) / len(rs),
            "mean_block_at_open": sum(r[2] for r in rs) / len(rs),
            "block_end_samples": len(closed),
            "mean_block_at_end": (sum(closed) / len(closed)) if closed else None,
            "mean_incoming_hits": sum(r[4] for r in rs) / len(rs),
            "mean_incoming_damage": sum(r[5] for r in rs) / len(rs),
        }
    return out
