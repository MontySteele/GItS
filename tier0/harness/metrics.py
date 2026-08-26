"""Per-fight stat extraction from the event log (spec §2 feeds off this).

M1 ships the raw per-fight stats + degeneracy flags; the 7-axis
normalization lands in M2 once the battery exists to calibrate against.
"""

from __future__ import annotations

import copy
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
    #   amp    -- the Vaporize/Melt multiplier's REALIZED DELTA over the
    #             unamplified hit (the base hit is a base op's damage; only the
    #             uplift is the reaction's), read off the `reaction` event's
    #             amp_delta. EB-57: that key is settled at the BOTTOM of
    #             effects.deal_damage_to_enemy, so it carries every multiplier
    #             that scales the amplified hit (Vulnerable/Cruelty/
    #             DoubleDamage, Slow) and is clamped by block and by overkill
    #             exactly like the `damage` emit -- an amp that only added
    #             overkill reports 0. It was previously sampled at the moment
    #             the aura was consumed, i.e. ABOVE all of that, which
    #             OVER-read on overkill and blocked hits and UNDER-read on
    #             every hit into a Vulnerable body (and Superconduct applies
    #             Vulnerable). Reads taken before that fix are not comparable;
    #   splash -- Overload's explosion, overkill-clamped at the emit site;
    #   dot    -- Electro-Charged's DoT ticking on an ENEMY. This one is NOT
    #             inside total_damage_dealt: dot_tick is not a `damage` event,
    #             so the denominator has to be widened for it -- see
    #             damage_all_ops.
    # `reaction_damage` above is amp + splash and feeds summarize()'s
    # reaction_damage_share. Track D itself moved no number; EB-57 does -- the
    # amp term is now the realized uplift, so `reaction_damage` and
    # `reaction_damage_share` are not comparable across that fix. `axes.raw`
    # reads none of these (A6 is swarm DPT + debuff stacks + aura_intents), so
    # the ratified A6 scores and the ref_ironclad/starter = 3.00 anchor are
    # untouched by it.
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
    # --- H1/H2, the aura+payoff counters (Last Call track H, 2026-08-05).
    # LOG-SIDE ONLY: every one of these is a tally of events the engine
    # already emitted (plus the `aura_op` row and the `aura_applied` `source`
    # key track H added, both emit-only). Nothing here is read by combat,
    # by an axis, or by the C# side -- FightStats is sim-local, and the
    # Py<->C# parity schema is understudy/soak.py's, not this one.
    #
    #   aura_ops                    resolutions of an aura-applying VERB
    #                               (apply_aura / swirl / refresh_all_auras),
    #                               keyed by op name. Counts the OP, not its
    #                               effect: an op that resolves into nothing
    #                               still counts here and not below.
    #   aura_applications_by_source what actually PUT an aura up, keyed by
    #                               provenance: `hit` (an element-tagged
    #                               attack landing on a clean enemy),
    #                               `apply_aura_op`, `swirl_op`,
    #                               `swirl_spread` (Swirl copying an aura
    #                               onto the other bodies).
    #   aura_applications_by_element same events keyed by element.
    #   reactions_by_name           the `reaction` event split by which
    #                               reaction fired. Sums to `reactions`.
    #   conditional_evaluated /     the `conditional` op's D4 rows, keyed by
    #   conditional_fired           PREDICATE (not by card -- the payoff
    #                               question is about the predicate, and the
    #                               per-card cut already exists in
    #                               tier05.conditional_telemetry, which reads
    #                               the log directly). `evaluated` is the
    #                               denominator: a card that repeats itself
    #                               evaluates twice in one play.
    aura_ops: dict[str, int] = field(default_factory=dict)
    aura_applications_by_source: dict[str, int] = field(default_factory=dict)
    aura_applications_by_element: dict[str, int] = field(default_factory=dict)
    reactions_by_name: dict[str, int] = field(default_factory=dict)
    conditional_evaluated: dict[str, int] = field(default_factory=dict)
    conditional_fired: dict[str, int] = field(default_factory=dict)
    # --- EB-17, the card-flow counters (Klee survival sprint plan §4, owed
    # again as next-step 3 of the sprint report; missed-requirements §2.2).
    # The plan's words: "Do not use raw pick rate as the redesign trigger. The
    # current static drafter values only printed damage and Block, so draw,
    # debuffs, generation, Bombs, and many engines are invisible. First add or
    # run paired evidence for: offered / picked / played-when-drawn;
    # conditional activation and dead-in-hand rate; ...; force-first-copy
    # paired winrate." Offered/picked are DRAFT-side and already exist
    # (tools/archive/klee_dead_cards.py); these three are the combat-side half.
    #
    # LOG-SIDE ONLY, on the track-H fence: every one is a tally of events the
    # engine emits, all of them keyed BY CARD ID (the unit the dead-card
    # question is asked in), and none of them is read by combat, by the pilot,
    # by an axis or by the C# side. Nothing here grades anything.
    #
    #   card_draws            draws of this id (the denominator for the two
    #                         rates below). Counts DRAWS, not copies: a card
    #                         drawn, flushed and redrawn counts twice.
    #   card_plays            plays of this id, from any source.
    #   played_when_drawn     plays whose INSTANCE was drawn into hand on the
    #                         same player turn it was played on. The literal
    #                         reading of the plan's phrase. `card_plays` minus
    #                         this is the rest: cards Retained into a later
    #                         turn, tokens created into hand, kit Bursts, and
    #                         auto-plays out of a pile -- none of which was
    #                         "played when drawn" and all of which used to be
    #                         indistinguishable in a per-id tally.
    #   dead_in_hand          DRAWN instances that left hand UNPLAYED: thrown
    #                         away by the end-of-turn flush (to discard, or to
    #                         exhaust for an unplayed Ethereal), or still held
    #                         in hand when the combat ended. Retention is not
    #                         death -- a Retained card is counted only once it
    #                         finally leaves unplayed or the fight ends on it.
    #                         Instances that leave hand some OTHER way (a
    #                         discard op, an exhaust op) are neither played
    #                         when drawn nor dead in hand: they were consumed,
    #                         which is a third outcome and not this one, so
    #                         the two rates do not sum to 1 and are not meant
    #                         to.
    #   force_first_copy      0/1 per card id per COMBAT: the first copy of
    #                         this id to be drawn was also PLAYED. This is the
    #                         fight-side half of the plan's "force-first-copy
    #                         paired winrate" -- the register asks what a deck
    #                         does when one copy is forced into it, and the
    #                         part a combat can answer is whether that copy
    #                         converted. Forcing the copy into the deck and
    #                         pairing the seeds is the CALLER's (tier0's
    #                         kernel builds no decks and rolls no rewards);
    #                         card_flow_profile() below carries the winrate
    #                         split that the pairing is read against.
    #   force_first_copy_drawn 0/1 per card id per COMBAT: the first copy
    #                         reached hand at all. The denominator of
    #                         force_first_copy -- a copy that was never drawn
    #                         did not fail to convert, it never got the
    #                         chance, and the two must not be pooled.
    card_draws: dict[str, int] = field(default_factory=dict)
    card_plays: dict[str, int] = field(default_factory=dict)
    played_when_drawn: dict[str, int] = field(default_factory=dict)
    dead_in_hand: dict[str, int] = field(default_factory=dict)
    force_first_copy: dict[str, int] = field(default_factory=dict)
    force_first_copy_drawn: dict[str, int] = field(default_factory=dict)
    # --- EB-20, the Encore economy census (BACKLOG EB-20, instrument for the
    # D8 lever: "19/78 grant, 1 spends, absorption automatic"). D8's DIRECTION
    # is ruled and its VALUE is unpicked; nothing here picks it. Same fence as
    # tracks D and H and EB-17: every counter is a tally of events the engine
    # emits, none is read by combat, by the pilot, by an axis or by the C#
    # side, and none of them grades anything.
    #
    # The engine side of this is provenance ONLY -- `source` and `card` keys
    # added to `gain_encore` / `encore_spent` / `encore_overdraw`, `source` to
    # `encore_absorb`. Every quantity below was already in the log; what was
    # missing was WHO. `encore_absorbed` above is the pre-existing total and
    # keeps its exact value: it feeds the ratified A4 axis and this track
    # moves no number that anything reads.
    #
    #   encore_granted            points the buffer RECEIVED, pooled, and the
    #   _by_card / _by_source     same points keyed by the card that caused
    #                             them and by the mechanism that delivered
    #                             them. A grant with no card behind it
    #                             (`salon_final_bow`, `salon_bow_encore`) is
    #                             ABSENT from _by_card, never a zero row and
    #                             never bucketed under a fake id.
    #   encore_spent              points DELIBERATELY drained, ditto. Kept
    #   _by_card / _by_source     apart from absorption on purpose: LAW makes
    #                             them two Fanfare legs, and D8's sentence
    #                             counts spenders (1 card) separately from
    #                             the automatic sink.
    #   encore_overdrawn          TRUE HP paid when a spend outran the buffer
    #                             (`encore_overdraw`). Not Encore at all --
    #                             it is what a spend cost when there was no
    #                             Encore to spend, and pooling it with
    #                             `encore_spent` would inflate the sink.
    #   encore_absorbed_by_source the automatic sink split by what it ate:
    #                             `enemy_hit` or `dot`. No card key exists
    #                             because no card causes absorption.
    #   encore_residual           Encore still held when the combat ENDED, off
    #   encore_residual_samples   the `encore_end` row -- generated and never
    #                             needed. The sample count is the denominator
    #                             and is 0 for a character with no Encore
    #                             resource at all, which is how "no residual"
    #                             stays distinguishable from "residual zero".
    #   encore_peak               the highest the buffer ever stood this
    #                             combat, reconstructed from the log (the
    #                             three mutation sites all emit, and
    #                             `gain_encore` carries the running total).
    #   encore_zero_turns         turn snapshots that found the buffer EMPTY,
    #   encore_turns_sampled      out of the snapshots taken. Sampled at the
    #                             `fanfare_turn` row -- after turn-start
    #                             triggers, Salon upkeep, energy and draw,
    #                             before the first card -- because that is the
    #                             state the pilot decides in and the state the
    #                             enemy phase will arrive against. The
    #                             PRE-upkeep sample is a different number and
    #                             already exists on `salon_upkeep`
    #                             (tier05.encore_telemetry reads it).
    #   encore_at_turn            the same snapshot kept per turn, so the
    #                             trajectory is readable and not only its two
    #                             summary statistics. Turn-keyed like
    #                             damage_by_turn, and offset the same way on a
    #                             gauntlet merge.
    #   fanfare_by_leg            Fanfare that LANDED, keyed by generation leg
    #   fanfare_wasted_by_leg     (`hp_lost` / `encore_spent` /
    #                             `encore_absorbed` / `center_stage`), and the
    #                             generation thrown away at the cap. The two
    #                             Encore legs are the ones EB-20 is about;
    #                             all four are recorded so their share has a
    #                             denominator. There is deliberately no
    #                             `encore_gained` leg to record -- Fanfare
    #                             prints when Encore goes DOWN, never up
    #                             (LAW; Track A 2026-07-28), and an empty
    #                             bucket here is the instrument's own check on
    #                             that rule rather than a hole in it.
    encore_granted: int = 0
    encore_granted_by_card: dict[str, int] = field(default_factory=dict)
    encore_granted_by_source: dict[str, int] = field(default_factory=dict)
    encore_spent: int = 0
    encore_spent_by_card: dict[str, int] = field(default_factory=dict)
    encore_spent_by_source: dict[str, int] = field(default_factory=dict)
    encore_overdrawn: int = 0
    encore_absorbed_by_source: dict[str, int] = field(default_factory=dict)
    encore_residual: int = 0
    encore_residual_samples: int = 0
    encore_peak: int = 0
    encore_zero_turns: int = 0
    encore_turns_sampled: int = 0
    encore_at_turn: dict[int, int] = field(default_factory=dict)
    fanfare_by_leg: dict[str, int] = field(default_factory=dict)
    fanfare_wasted_by_leg: dict[str, int] = field(default_factory=dict)
    # --- O-1 (Track O slice 12, ruled 2026-08-06). A multi-stage encounter
    # (`gauntlet`) is ONE record but TWO combats, and every per-fight rate
    # below used to divide the two combats' events by one record. The stage
    # records this record was merged from are kept here so that a per-COMBAT
    # denominator is recoverable; EMPTY on a single-combat record, which is
    # therefore one combat by itself (see `combats` and `per_combat`).
    # Counts only -- nothing here is read by combat, by an axis, or by C#.
    stages: list["FightStats"] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)

    @property
    def hp_delta(self) -> int:
        return self.hp_end - self.hp_start

    @property
    def aura_applications(self) -> int:
        """Every aura this fight put up, from any source (H1 numerator)."""
        return sum(self.aura_applications_by_source.values())

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

    @property
    def encore_drained(self) -> int:
        """Every point that LEFT the buffer: deliberate spends PLUS the
        automatic sink. The denominator the grant total is read against.

        Absorption belongs in here and this is not a judgement call: absorbed
        points did the job the buffer exists for, and reading grants against
        spends alone reports every point the buffer ATE as a point it wasted.
        tier05.encore_telemetry's first run made exactly that error and its
        module note records it; the rule is restated here rather than
        cross-referenced because a denominator that is wrong in one place is
        wrong everywhere it is copied to."""
        return self.encore_spent + self.encore_absorbed

    @property
    def combats(self) -> int:
        """How many COMBATS this record is. 1 for an ordinary fight; the
        stage count for a merged multi-stage encounter. The denominator of
        every per-fight EVENT rate (O-1)."""
        return len(self.stages) or 1


def per_combat(all_stats: list["FightStats"]) -> list["FightStats"]:
    """The battery's records expanded to one record per COMBAT.

    O-1: `gauntlet` is two combats behind one merged record, so a rate that
    divides by `len(all_stats)` carries a different unit on that encounter
    than on the other five, and a battery-wide row pools the two units.
    Aggregates that count EVENTS PER FIGHT denominate over this expansion;
    pooled counts and every ratio-of-sums are identical either way, and the
    record-level figures that describe the ENCOUNTER ATTEMPT rather than a
    combat (winrate, avg_turns, hp delta, flags) deliberately do NOT use it --
    a gauntlet is one attempt whose HP carries across the stage break."""
    out: list["FightStats"] = []
    for s in all_stats:
        out.extend(s.stages or [s])
    return out


def merge_stages(stages: list["FightStats"]) -> "FightStats":
    """Merge back-to-back stage fights (GAUNTLET) into one fight record.
    Later stages' turn numbers are offset so the damage curve is continuous.

    The merged record keeps the stage records on `.stages`, so a per-combat
    denominator survives the merge (O-1). Because they are kept, stage 1 is
    COPIED rather than accumulated into in place -- the caller's stage records
    have to still read as the individual combats they were."""
    if len(stages) == 1:
        return stages[0]
    merged = copy.deepcopy(stages[0])
    for s in stages[1:]:
        offset = merged.turns
        for t, v in s.damage_by_turn.items():
            merged.damage_by_turn[t + offset] = v
        for t, v in s.energy_by_turn.items():
            merged.energy_by_turn[t + offset] = v
        # EB-20's trajectory, offset with the other turn-keyed curves: a
        # gauntlet's stage-2 turn 1 is the run's turn (stage-1 turns + 1).
        for t, v in s.encore_at_turn.items():
            merged.encore_at_turn[t + offset] = v
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
        # EB-20. The buffer RESETS to 0 at the top of every combat
        # (run_fight), so a gauntlet's two stages each run their own economy:
        # the counts sum, the residual sums (both stages generated Encore they
        # never needed, and `encore_residual_samples` sums with it so the mean
        # per combat stays honest), and the PEAK is a max -- two stages that
        # each reached 9 did not reach 18.
        merged.encore_granted += s.encore_granted
        merged.encore_spent += s.encore_spent
        merged.encore_overdrawn += s.encore_overdrawn
        merged.encore_residual += s.encore_residual
        merged.encore_residual_samples += s.encore_residual_samples
        merged.encore_peak = max(merged.encore_peak, s.encore_peak)
        merged.encore_zero_turns += s.encore_zero_turns
        merged.encore_turns_sampled += s.encore_turns_sampled
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
        # Track H counters are plain tallies, so a gauntlet merges them by
        # key-wise addition (no turn offset: none of them is turn-keyed).
        for attr in ("aura_ops", "aura_applications_by_source",
                     "aura_applications_by_element", "reactions_by_name",
                     "conditional_evaluated", "conditional_fired",
                     # EB-17's three COUNTS merge the same way. Their two
                     # indicators do not -- see below.
                     "card_draws", "card_plays", "played_when_drawn",
                     "dead_in_hand",
                     # EB-20's provenance tables, likewise: plain tallies,
                     # none of them turn-keyed. `encore_at_turn` IS turn-keyed
                     # and is offset below with the other curves.
                     "encore_granted_by_card", "encore_granted_by_source",
                     "encore_spent_by_card", "encore_spent_by_source",
                     "encore_absorbed_by_source",
                     "fanfare_by_leg", "fanfare_wasted_by_leg"):
            dst, src = getattr(merged, attr), getattr(s, attr)
            for k, v in src.items():
                dst[k] = dst.get(k, 0) + v
        # EB-17's first-copy pair is 0/1 PER COMBAT, so it merges by OR and
        # not by addition: a gauntlet whose stage 1 converted the copy and
        # whose stage 2 did not is one attempt in which it converted, and a
        # summed 2 would read as two conversions out of one denominator. Each
        # stage record keeps its own 0/1, so per_combat() still recovers the
        # per-combat unit -- which is what card_flow_profile() denominates on.
        for attr in ("force_first_copy", "force_first_copy_drawn"):
            dst, src = getattr(merged, attr), getattr(s, attr)
            for k, v in src.items():
                dst[k] = 1 if (dst.get(k, 0) or v) else 0
        merged.flags = sorted(set(merged.flags) | set(s.flags))
    merged.won = all(s.won for s in stages)
    # The combats this record IS. Set last, and from the ORIGINALS, so the
    # per-combat denominator is the stages as they were fought (O-1).
    merged.stages = list(stages)
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
    # Track H: aura + payoff tallies, all log-side.
    aura_ops: dict[str, int] = {}
    aura_src: dict[str, int] = {}
    aura_elem: dict[str, int] = {}
    reactions_by_name: dict[str, int] = {}
    cond_eval: dict[str, int] = {}
    cond_fired: dict[str, int] = {}
    # EB-17: the card-flow tallies, all keyed by card id.
    card_draws: dict[str, int] = {}
    card_plays: dict[str, int] = {}
    pwd: dict[str, int] = {}
    dead: dict[str, int] = {}
    ffc: dict[str, int] = {}
    ffc_drawn: dict[str, int] = {}
    # EB-20: the Encore census. `enc_now` is the buffer reconstructed as the
    # log is walked -- exact, not estimated: the buffer has exactly three
    # mutation sites in the engine (gain / spend / absorb) and all three emit,
    # and `gain_encore` carries the post-gain running total, so the walk
    # re-anchors on every gain instead of accumulating drift.
    enc_granted = enc_spent = enc_overdrawn = 0
    enc_grant_card: dict[str, int] = {}
    enc_grant_src: dict[str, int] = {}
    enc_spend_card: dict[str, int] = {}
    enc_spend_src: dict[str, int] = {}
    enc_absorb_src: dict[str, int] = {}
    enc_at_turn: dict[int, int] = {}
    fanfare_leg: dict[str, int] = {}
    fanfare_wasted: dict[str, int] = {}
    enc_now = enc_peak = enc_zero_turns = enc_turns_sampled = 0
    enc_residual = enc_residual_samples = 0
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
            cid = ev["card"]
            card_plays[cid] = card_plays.get(cid, 0) + 1
            # EB-17. `drawn_turn` is -1 for an instance that never reached
            # hand by a draw, and -1 can never equal a turn number, so the
            # comparison needs no separate "was it drawn" branch.
            if ev.get("drawn_turn", -1) == ev["turn"]:
                pwd[cid] = pwd.get(cid, 0) + 1
            if ev.get("first_copy"):
                # 0/1 per combat: the same first copy can be played twice in
                # one fight (played, discarded, redrawn, played again) and
                # that is still ONE copy that converted.
                ffc[cid] = 1
        elif e == "dead_in_hand":
            cid = ev["card"]
            dead[cid] = dead.get(cid, 0) + 1
        elif e == "draw":
            cid = ev["card"]
            card_draws[cid] = card_draws.get(cid, 0) + 1
            if ev.get("first_copy"):
                ffc_drawn[cid] = 1      # 0/1 per combat, as above
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
            # EB-20. `encore_absorbed` above is the pre-existing A4 figure and
            # is untouched; the split beside it is the new read.
            enc_now -= ev["amount"]
            src = ev.get("source", "unattributed")
            enc_absorb_src[src] = enc_absorb_src.get(src, 0) + ev["amount"]
        elif e == "gain_encore":
            enc_granted += ev["amount"]
            # The emitted `total` is the buffer AFTER the gain -- authoritative,
            # so the walk cannot drift.
            enc_now = ev["total"]
            enc_peak = max(enc_peak, enc_now)
            src = ev.get("source", "unattributed")
            enc_grant_src[src] = enc_grant_src.get(src, 0) + ev["amount"]
            cid = ev.get("card")
            if cid is not None:
                enc_grant_card[cid] = enc_grant_card.get(cid, 0) + ev["amount"]
        elif e == "encore_spent":
            enc_spent += ev["amount"]
            enc_now -= ev["amount"]
            src = ev.get("source", "unattributed")
            enc_spend_src[src] = enc_spend_src.get(src, 0) + ev["amount"]
            cid = ev.get("card")
            if cid is not None:
                enc_spend_card[cid] = enc_spend_card.get(cid, 0) + ev["amount"]
        elif e == "encore_overdraw":
            # HP, not Encore: the buffer was already empty. Never added to
            # enc_now, and never pooled with the spend.
            enc_overdrawn += ev["amount"]
        elif e == "fanfare_turn":
            # The Furina-guarded turn snapshot, taken at the point the pilot
            # decides. See the FightStats note for why this sample point and
            # not `turn_open`.
            enc_turns_sampled += 1
            enc_at_turn[ev["turn"]] = enc_now
            if enc_now == 0:
                enc_zero_turns += 1
        elif e == "gain_fanfare":
            leg = ev["source"]
            fanfare_leg[leg] = fanfare_leg.get(leg, 0) + ev["amount"]
            w = ev.get("wasted", 0)
            if w:
                fanfare_wasted[leg] = fanfare_wasted.get(leg, 0) + w
        elif e == "encore_end":
            enc_residual = ev["encore"]
            enc_residual_samples = 1
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
            name = ev["reaction"]
            reactions_by_name[name] = reactions_by_name.get(name, 0) + 1
        elif e == "aura_op":
            op = ev["op"]
            aura_ops[op] = aura_ops.get(op, 0) + 1
        elif e == "aura_applied":
            src = ev.get("source", "hit")
            aura_src[src] = aura_src.get(src, 0) + 1
            el = ev["element"]
            aura_elem[el] = aura_elem.get(el, 0) + 1
        elif e == "conditional":
            pred = ev["predicate"]
            cond_eval[pred] = cond_eval.get(pred, 0) + 1
            if ev["fired"]:
                cond_fired[pred] = cond_fired.get(pred, 0) + 1
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
        aura_ops=aura_ops,
        aura_applications_by_source=aura_src,
        aura_applications_by_element=aura_elem,
        reactions_by_name=reactions_by_name,
        conditional_evaluated=cond_eval,
        conditional_fired=cond_fired,
        card_draws=card_draws,
        card_plays=card_plays,
        played_when_drawn=pwd,
        dead_in_hand=dead,
        force_first_copy=ffc,
        force_first_copy_drawn=ffc_drawn,
        encore_granted=enc_granted,
        encore_granted_by_card=enc_grant_card,
        encore_granted_by_source=enc_grant_src,
        encore_spent=enc_spent,
        encore_spent_by_card=enc_spend_card,
        encore_spent_by_source=enc_spend_src,
        encore_overdrawn=enc_overdrawn,
        encore_absorbed_by_source=enc_absorb_src,
        encore_residual=enc_residual,
        encore_residual_samples=enc_residual_samples,
        encore_peak=enc_peak,
        encore_zero_turns=enc_zero_turns,
        encore_turns_sampled=enc_turns_sampled,
        encore_at_turn=enc_at_turn,
        fanfare_by_leg=fanfare_leg,
        fanfare_wasted_by_leg=fanfare_wasted,
        flags=sorted(set(flags)))


def summarize(all_stats: list[FightStats]) -> dict:
    """Battery summary. `fights` counts RECORDS (one per encounter attempt);
    `combats` counts the combats inside them, which is two per `gauntlet`
    record. The event rates below (`reactions_per_fight`,
    `auras_wasted_per_fight`, `aura_starved_fights`) denominate over COMBATS
    per O-1; winrate, turns, HP and flags stay per attempt."""
    n = len(all_stats)
    if n == 0:
        return {}
    combats = per_combat(all_stats)
    nc = len(combats)
    wins = sum(s.won for s in all_stats)
    return {
        "fights": n,
        "combats": nc,
        "winrate": wins / n,
        "avg_turns": sum(s.turns for s in all_stats) / n,
        "avg_hp_delta": sum(s.hp_delta for s in all_stats) / n,
        "avg_dpt": sum(s.total_damage_dealt / max(1, s.turns)
                       for s in all_stats) / n,
        "avg_energy_per_turn": sum(s.energy_spent / max(1, s.turns)
                                   for s in all_stats) / n,
        "reactions_per_fight": sum(s.reactions for s in combats) / nc,
        # Spec §4.4: healthy reaction-archetype = 25-45% damage share;
        # aura starvation (spec §8) = reaction-deck fights with 0 reactions.
        "reaction_damage_share": (sum(s.reaction_damage for s in all_stats)
                                  / max(1, sum(s.total_damage_dealt
                                               for s in all_stats))),
        # A COMBAT with no reaction is a starved combat: a starved gauntlet
        # stage merged with a reacting one used to read as not starved (O-1).
        "aura_starved_fights": sum(1 for s in combats
                                   if s.reactions == 0) / nc,
        "auras_wasted_per_fight": sum(s.auras_wasted for s in combats) / nc,
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
    combats = per_combat(all_stats)
    nc = len(combats)
    total = sum(s.damage_all_ops for s in all_stats)
    react = sum(s.damage_from_reactions for s in all_stats)
    return {
        "fights": n,
        "combats": nc,
        "damage_all_ops": total,
        "damage_from_reactions": react,
        "damage_from_base_ops": total - react,
        "share": react / max(1, total),
        # Per COMBAT, not per record: a mean over fights has to be a mean over
        # fights on every encounter, including the two-stage one (O-1).
        "share_by_fight_mean": sum(s.reaction_share for s in combats) / nc,
        "amp": sum(s.reaction_damage_amp for s in all_stats),
        "splash": sum(s.reaction_damage_splash for s in all_stats),
        "dot": sum(s.reaction_damage_dot for s in all_stats),
        "fights_with_any_reaction_damage": sum(
            1 for s in combats if s.damage_from_reactions),
    }


# The predicates a card uses to CASH IN a reaction or an aura -- the "reaction
# payoff ops" the 2026-07-26 audit called unused. Named here so the harvest
# and the tests read the same list, and so adding a payoff predicate to the
# DSL without adding it here is a visible omission rather than a silent one.
# `target_has_nonpyro_aura` and its any-aura sibling `target_has_aura` are
# AURA payoffs rather than reaction payoffs (they read the board state a
# reaction would consume), and are listed for that reason -- the split is kept
# in the reporting, not merged away. Both names appear because C2 (R189) moved
# ONE row from the first to the second: a harvest that knew only the old name
# would have reported `elemental_ecstasy`'s fire rate as zero from the day it
# was repaired.
REACTION_PAYOFF_PREDICATES = ("reaction_triggered_by_this",
                              "reaction_triggered_this_turn")
AURA_PAYOFF_PREDICATES = ("target_has_nonpyro_aura", "target_has_aura")


def aura_profile(all_stats: list[FightStats]) -> dict:
    """H1's aggregate hook: how often aura-applying ops fire, and what puts
    auras on the board, across a battery.

    POOLED counts plus per-fight rates, on the `reaction_share` pattern.
    Reports numbers only; whether an application rate is adequate is a design
    reading and is not made here.

    Per-fight rates denominate over COMBATS (`combats`), not over records
    (`fights`): the two differ exactly on a multi-stage encounter, and mixing
    the units made `gauntlet` read double every other encounter (O-1).
    """
    n = len(all_stats)
    if n == 0:
        return {}
    combats = per_combat(all_stats)
    nc = len(combats)

    def _pool(attr: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for s in all_stats:
            for k, v in getattr(s, attr).items():
                out[k] = out.get(k, 0) + v
        return out

    ops = _pool("aura_ops")
    by_source = _pool("aura_applications_by_source")
    by_element = _pool("aura_applications_by_element")
    applications = sum(by_source.values())
    turns = sum(s.turns for s in all_stats)
    return {
        "fights": n,
        "combats": nc,
        "aura_ops": ops,
        "aura_ops_total": sum(ops.values()),
        "aura_ops_per_fight": sum(ops.values()) / nc,
        "applications": applications,
        "applications_per_fight": applications / nc,
        "applications_per_turn": applications / max(1, turns),
        "applications_by_source": by_source,
        "applications_by_element": by_element,
        "reactions": sum(s.reactions for s in all_stats),
        "reactions_by_name": _pool("reactions_by_name"),
        "auras_wasted": sum(s.auras_wasted for s in all_stats),
        "fights_with_any_aura": sum(1 for s in combats
                                    if s.aura_applications),
    }


def payoff_profile(all_stats: list[FightStats]) -> dict:
    """H2's aggregate hook: conditional-rider trigger counts, keyed by
    predicate, pooled over a battery.

    `by_predicate` carries EVERY predicate the cohort evaluated, so the table
    is readable as a whole; `reaction_payoff` and `aura_payoff` are the two
    slices the audit's "reaction payoff ops are unused" sentence is about.
    A predicate that no card in the cohort carries is ABSENT, not zero -- the
    two are different findings (nothing drafted it vs. it drafted and never
    fired) and collapsing them is exactly the confusion the harvest exists to
    settle. `evaluated` is the denominator; see FightStats.
    """
    n = len(all_stats)
    if n == 0:
        return {}
    nc = len(per_combat(all_stats))       # O-1: per COMBAT, see aura_profile
    evaluated: dict[str, int] = {}
    fired: dict[str, int] = {}
    for s in all_stats:
        for k, v in s.conditional_evaluated.items():
            evaluated[k] = evaluated.get(k, 0) + v
        for k, v in s.conditional_fired.items():
            fired[k] = fired.get(k, 0) + v
    by_pred = {
        k: {"evaluated": v, "fired": fired.get(k, 0),
            "rate": fired.get(k, 0) / v if v else 0.0,
            "evaluated_per_fight": v / nc}
        for k, v in sorted(evaluated.items())
    }

    def _slice(names) -> dict:
        rows = {k: by_pred[k] for k in names if k in by_pred}
        ev = sum(r["evaluated"] for r in rows.values())
        fi = sum(r["fired"] for r in rows.values())
        return {"predicates": rows, "evaluated": ev, "fired": fi,
                "rate": fi / ev if ev else 0.0,
                "absent": [k for k in names if k not in by_pred]}

    return {
        "fights": n,
        "combats": nc,
        "by_predicate": by_pred,
        "reaction_payoff": _slice(REACTION_PAYOFF_PREDICATES),
        "aura_payoff": _slice(AURA_PAYOFF_PREDICATES),
    }


def card_flow_profile(all_stats: list[FightStats]) -> dict:
    """EB-17's aggregate hook: what happened to each card between the draw
    that produced it and the pile it ended in, pooled over a battery.

    One row per card id that the cohort DREW or PLAYED. A card the cohort
    never saw is ABSENT rather than zero, the payoff_profile rule: "no deck
    carried it" and "every deck carried it and nobody played it" are different
    findings and pooling them is exactly what this instrument exists to stop.

    Per-fight units denominate over COMBATS (O-1), like every other aggregate
    here: a `gauntlet` record is two combats, each of which drew its own deck.

    Reports numbers only. Whether a played-when-drawn rate is low, or a
    dead-in-hand rate high enough to redesign a card, is a design reading and
    is not made here -- which is the whole point of the gate this closes: the
    sprint plan's rule is "do not use raw pick rate as the redesign trigger",
    and a trigger needs a number before it can be argued about.

    The `force_first_copy` block is the fight-side half of the register's
    "force-first-copy paired winrate". `winrate_first_copy_played` and
    `winrate_first_copy_dead` split the combats that DREW the first copy by
    whether it converted; the delta between them is a within-arm split and is
    deliberately NOT called the paired winrate, because the register's pairing
    is two arms on the same seeds (a deck with the copy forced in against the
    same deck without it) and tier0's kernel neither builds decks nor drafts.
    Forcing the copy is the caller's; this is what the caller reads afterwards.
    """
    n = len(all_stats)
    if n == 0:
        return {}
    combats = per_combat(all_stats)
    nc = len(combats)

    def _pool(attr: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for s in combats:
            for k, v in getattr(s, attr).items():
                out[k] = out.get(k, 0) + v
        return out

    draws = _pool("card_draws")
    plays = _pool("card_plays")
    pwd = _pool("played_when_drawn")
    dead = _pool("dead_in_hand")
    ffc = _pool("force_first_copy")
    ffc_drawn = _pool("force_first_copy_drawn")

    def _split(cid: str) -> tuple[list, list]:
        """The combats that DREW the first copy of `cid`, split by whether it
        converted into a play. Combats that never drew it are in NEITHER --
        they are the denominator of a different question."""
        played = [s for s in combats
                  if s.force_first_copy_drawn.get(cid)
                  and s.force_first_copy.get(cid)]
        deadc = [s for s in combats
                 if s.force_first_copy_drawn.get(cid)
                 and not s.force_first_copy.get(cid)]
        return played, deadc

    def _wr(rows) -> float | None:
        """Winrate over `rows`, or None on an empty split. None and not 0.0:
        an undefined winrate is not a loss, and a report that prints 0% for
        "never happened" is a report that will be misread."""
        return (sum(s.won for s in rows) / len(rows)) if rows else None

    by_card: dict[str, dict] = {}
    for cid in sorted(set(draws) | set(plays)):
        d = draws.get(cid, 0)
        seen = ffc_drawn.get(cid, 0)
        played_rows, dead_rows = _split(cid)
        by_card[cid] = {
            "draws": d,
            "draws_per_fight": d / nc,
            "plays": plays.get(cid, 0),
            "played_when_drawn": pwd.get(cid, 0),
            "played_when_drawn_rate": (pwd.get(cid, 0) / d) if d else None,
            "dead_in_hand": dead.get(cid, 0),
            "dead_in_hand_rate": (dead.get(cid, 0) / d) if d else None,
            "first_copy_drawn_combats": seen,
            "force_first_copy": ffc.get(cid, 0),
            "force_first_copy_rate": (ffc.get(cid, 0) / seen) if seen else None,
            "winrate_first_copy_played": _wr(played_rows),
            "winrate_first_copy_dead": _wr(dead_rows),
        }
    return {
        "fights": n,
        "combats": nc,
        "by_card": by_card,
        "draws": sum(draws.values()),
        "plays": sum(plays.values()),
        "played_when_drawn": sum(pwd.values()),
        "dead_in_hand": sum(dead.values()),
    }


# The Fanfare generation legs, in LAW's order (kickoff §4; LAW "Fanfare is
# capped at %maxHP" bullet). Named here so the census and the tests read the
# same list, and so a leg added to engine/resources.py without being added
# here shows up in `legs_unexpected` rather than silently joining a total.
# There is deliberately no `encore_gained` entry: Fanfare prints when Encore
# goes DOWN, never up (Track A, RULED 2026-07-28), and the fact that the
# cohort never emits one is a reading of the log, not an assumption of it.
FANFARE_LEGS = ("hp_lost", "encore_spent", "encore_absorbed", "center_stage")
# The two legs EB-20 is about. The other two are carried so these have a
# denominator -- a share with no denominator is a number nobody can argue with.
ENCORE_FANFARE_LEGS = ("encore_spent", "encore_absorbed")


def encore_census_profile(all_stats: list[FightStats]) -> dict:
    """EB-20's aggregate hook: where Furina's Encore comes from, where it
    goes, and what it was still holding when the music stopped.

    The instrument for the D8 lever, whose direction is ruled and whose value
    is unpicked. It picks nothing. There is no target here, no band, no
    "healthy" grant/drain ratio and no verdict on whether 19 granters against
    1 spender is the right shape -- that is [USER]'s call and a design act does
    not happen in an aggregate function. Same fence as reaction_share,
    aura_profile, payoff_profile and card_flow_profile.

    Two census words ARE ruled (R122, 2026-08-07), both by "read the meter,
    not the sheet": the `encore_cost` GATE is not a spender -- a sink that
    fired 0 of 17,709 observed spends is not part of the measured economy --
    and power-sourced Encore (`spotlight_encore_first`, 5.9% of grants)
    counts toward the grant side, because the D8 saturation read is about
    what refills the bar, not which sheet row fed it. Sheet-side counts
    (18/82 granting, 5 taking off the buffer) stay reported beside the
    measured ones; the lever's VALUE stays open.

    ENCORE-LIVE COMBATS ONLY. Every per-combat figure denominates over
    `encore_combats` -- combats that granted, absorbed, or reported an
    end-of-combat residual -- and not over every combat in the battery. Encore
    is Furina's alone in content, so pooling a Klee battery's zero rows into
    the denominator would halve every rate for no reason but the cohort's
    composition. `combats` is reported beside it so the filter is visible.
    Returns {} when the cohort has no Encore in it at all, which is the honest
    answer for a battery that was never about this resource.

    RESIDUAL is `encore_end` -- the buffer at the final bell, generated and
    never needed. It sums across a gauntlet's stages because the buffer resets
    per combat and each stage wasted its own; `residual_samples` sums with it,
    so the mean stays per combat.

    DRAINED is spends PLUS absorption, never spends alone. See
    FightStats.encore_drained for why, and for the instrument that got it
    wrong first.
    """
    n = len(all_stats)
    if n == 0:
        return {}
    combats = per_combat(all_stats)
    live = [s for s in combats
            if s.encore_granted or s.encore_absorbed
            or s.encore_residual_samples]
    if not live:
        return {}
    nl = len(live)

    def _pool(attr: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for s in live:
            for k, v in getattr(s, attr).items():
                out[k] = out.get(k, 0) + v
        return out

    granted_card = _pool("encore_granted_by_card")
    spent_card = _pool("encore_spent_by_card")
    granted = sum(s.encore_granted for s in live)
    spent = sum(s.encore_spent for s in live)
    absorbed = sum(s.encore_absorbed for s in live)
    drained = spent + absorbed
    residual = sum(s.encore_residual for s in live)
    residual_n = sum(s.encore_residual_samples for s in live)
    sampled = sum(s.encore_turns_sampled for s in live)
    zeros = sum(s.encore_zero_turns for s in live)
    peaks = [s.encore_peak for s in live]

    by_card: dict[str, dict] = {}
    for cid in sorted(set(granted_card) | set(spent_card)):
        g, sp = granted_card.get(cid, 0), spent_card.get(cid, 0)
        by_card[cid] = {
            "granted": g,
            "granted_per_combat": g / nl,
            # Which side of D8's "19 grant, 1 spends" sentence this card is
            # on, measured rather than counted off the sheet: a card that
            # prints a grant and never resolves one is not a granter in play.
            "share_of_granted": (g / granted) if granted else None,
            "spent": sp,
            "spent_per_combat": sp / nl,
            "share_of_spent": (sp / spent) if spent else None,
            "combats_granting": sum(1 for s in live
                                    if s.encore_granted_by_card.get(cid)),
            "combats_spending": sum(1 for s in live
                                    if s.encore_spent_by_card.get(cid)),
        }

    applied = _pool("fanfare_by_leg")
    wasted = _pool("fanfare_wasted_by_leg")
    total_applied = sum(applied.values())
    legs = {
        leg: {"applied": applied.get(leg, 0),
              "wasted": wasted.get(leg, 0),
              "share": (applied.get(leg, 0) / total_applied)
              if total_applied else None}
        for leg in FANFARE_LEGS if leg in applied or leg in wasted
    }
    encore_leg_applied = sum(applied.get(leg, 0)
                             for leg in ENCORE_FANFARE_LEGS)
    return {
        "fights": n,
        "combats": len(combats),
        "encore_combats": nl,
        # One row per card id that GRANTED or SPENT a point in this cohort. A
        # card that prints an Encore grant and never resolved one is ABSENT
        # rather than zero -- the payoff_profile rule again, and here it is
        # exactly the question: "19 of 78 cards grant" is a sheet count, and
        # what a battery can say is how many of them a fight actually sees.
        "by_card": by_card,
        "granted": granted,
        "granted_per_combat": granted / nl,
        "granted_by_card": granted_card,
        "granted_by_source": _pool("encore_granted_by_source"),
        "spent": spent,
        "spent_per_combat": spent / nl,
        "spent_by_card": spent_card,
        "spent_by_source": _pool("encore_spent_by_source"),
        "absorbed": absorbed,
        "absorbed_per_combat": absorbed / nl,
        "absorbed_by_source": _pool("encore_absorbed_by_source"),
        # HP, not Encore. Reported beside the spend it belongs to and never
        # inside it.
        "overdrawn": sum(s.encore_overdrawn for s in live),
        "overdrawn_per_combat": sum(s.encore_overdrawn for s in live) / nl,
        "drained": drained,
        "drained_per_combat": drained / nl,
        # Above 1.0 means the cohort minted Encore it never used. None, not
        # 0.0 or infinity, when nothing was ever drained: a buffer that filled
        # and was never touched is the most saturated case there is, and
        # reporting it as a ratio's extreme prints the strongest finding as a
        # divide-by-zero.
        "gain_drain_ratio": (granted / drained) if drained else None,
        "residual": residual,
        "residual_samples": residual_n,
        "residual_per_combat": (residual / residual_n) if residual_n else None,
        # Residual over grants: the fraction of everything she made that was
        # still sitting there at the end. The most direct statement of the
        # saturation D8 is a lever over.
        "residual_share_of_granted": (residual / granted) if granted else None,
        "peak_mean": sum(peaks) / nl,
        "peak_max": max(peaks),
        "turns_sampled": sampled,
        "zero_turns": zeros,
        "zero_turn_rate": (zeros / sampled) if sampled else None,
        "combats_with_any_grant": sum(1 for s in live if s.encore_granted),
        "combats_with_any_spend": sum(1 for s in live if s.encore_spent),
        "combats_with_any_absorb": sum(1 for s in live if s.encore_absorbed),
        "fanfare_applied": total_applied,
        "fanfare_by_leg": legs,
        # A leg that no fight in the cohort generated is ABSENT from
        # `fanfare_by_leg` and listed here instead -- the payoff_profile rule:
        # "nothing generated it" and "it generated zero" are different
        # findings. `legs_unexpected` is the other direction and should stay
        # empty: a leg name the engine emits that LAW does not list is either
        # a new leg nobody registered or `encore_gained` coming back.
        "legs_absent": [leg for leg in FANFARE_LEGS if leg not in legs],
        "legs_unexpected": sorted(set(applied) - set(FANFARE_LEGS)),
        "fanfare_from_encore": encore_leg_applied,
        "fanfare_from_encore_share": ((encore_leg_applied / total_applied)
                                      if total_applied else None),
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
