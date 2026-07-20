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
    total_intents: int
    reactions: int
    reaction_damage: int
    auras_wasted: int
    cards_played: int = 0
    regrets: int = 0                # pilot_regret samples (spec §6)
    enemy_actions: int = 0          # intents taken + sleep skips (§2.2a)
    control_negated: float = 0.0    # action-equivalents negated by
                                    # COMPANION-sourced control (frozen
                                    # attack = 0.5; future full stuns = 1.0)
    flags: list[str] = field(default_factory=list)

    @property
    def hp_delta(self) -> int:
        return self.hp_end - self.hp_start


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
        merged.total_intents += s.total_intents
        merged.reactions += s.reactions
        merged.reaction_damage += s.reaction_damage
        merged.auras_wasted += s.auras_wasted
        merged.cards_played += s.cards_played
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
    debuffed_intents = total_intents = cards_played = regrets = 0
    reactions = reaction_dmg = auras_wasted = sleeps = 0
    control_negated = 0.0
    flags: list[str] = []
    won = False
    turns = state.turn

    for ev in state.log:
        e = ev["event"]
        if e == "damage":
            total_dmg += ev["amount"]
            dmg_by_turn[ev["turn"]] = dmg_by_turn.get(ev["turn"], 0) + ev["amount"]
            if ev.get("source") == "reaction_splash":
                reaction_dmg += ev["amount"]
        elif e == "block":
            block += ev["amount"]
        elif e == "player_hit":
            blocked += ev["blocked"]
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
        elif e == "apply_power":
            if ev["power"] in ("weak", "vulnerable") and ev["target"] != "player":
                debuff_stacks += ev["stacks"]
        elif e == "intent":
            total_intents += 1
            if ev["debuffed"]:
                debuffed_intents += 1
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
        elif e == "aura_wasted":
            auras_wasted += 1
        elif e == "degeneracy":
            flags.append(ev["kind"])
        elif e == "amp_stack_warning":
            flags.append("AMP_STACK")
        elif e == "fight_end":
            won = ev["won"]
            turns = ev["turns"]

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
        debuffed_intents=debuffed_intents, total_intents=total_intents,
        reactions=reactions,
        reaction_damage=reaction_dmg, auras_wasted=auras_wasted,
        cards_played=cards_played, regrets=regrets,
        enemy_actions=enemy_actions, control_negated=control_negated,
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
