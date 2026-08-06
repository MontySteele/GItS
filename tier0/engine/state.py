"""Combat state: player, enemies, piles. No rules logic here — just data
and the pile-manipulation primitives that everything else builds on.

Determinism contract: ALL randomness flows through CombatState.rng
(a random.Random seeded by the harness). Nothing may import the global
`random` module functions.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Optional

from tier0 import constants as C


def _copy_plain(val):
    """Deep-copy yaml-shaped data (dict / list / immutable scalar).

    Card payloads never hold cycles, class instances or shared aliases, so
    this needs none of ``copy.deepcopy``'s memo bookkeeping -- which is the
    whole reason it is several times faster. Anything that is not a dict or
    list is returned as-is, which is correct for the str/int/bool/None leaves
    that yaml produces.
    """
    t = type(val)
    if t is dict:
        return {k: _copy_plain(v) for k, v in val.items()}
    if t is list:
        return [_copy_plain(v) for v in val]
    return val


# Every container-valued field on Card. Card.__deepcopy__ copies exactly
# these and shares the rest; test_state.py pins the list against the
# dataclass definition so a new mutable field cannot be added silently.
_MUTABLE_FIELDS = ("effects", "solve", "tempo_band", "archetypes", "tags",
                   "companion", "sly", "upgrade", "enchant_effects")

# Card fields that a sheet row may NEVER declare again, with the reason the
# author needs. House pattern: a caught mistake becomes a lint, so the next
# person meets the rule instead of the symptom.
RETIRED_CARD_FIELDS = {
    "fanfare_cost": (
        "Fanfare is a read-only momentum stat ('The Tide Turns', F-A4) -- "
        "no card spends it, and Encore is Furina's only managed resource. "
        "A card that wants to reward a full meter READS it "
        "(bonus_formula: N_per_M_fanfare) or gates on it "
        "(if: fanfare_at_least_N); a card that wants to raise the player's "
        "permanent baseline grants a floor (op: gain_fanfare_floor)."),
}


def remove_instance(pile: list, card: "Card") -> bool:
    """Remove exactly THIS instance from the pile; True if it was there.

    Card is a dataclass, so `list.remove` / `in` compare by VALUE and two
    fresh copies of the same card are equal twins -- a value-based remove can
    take the twin and leave `card` aliased into two piles. Twins are not
    interchangeable either: cost_delta_this_combat, free_this_turn and
    sly_this_turn are per-INSTANCE state. Every remove-from-a-card-pile must
    go through here.
    """
    for i, c in enumerate(pile):
        if c is card:
            del pile[i]
            return True
    return False


@dataclass
class Card:
    id: str
    name: str
    cost: Any                     # int or "X"
    type: str                     # attack | skill | power
    rarity: str = "common"        # basic | common | uncommon | rare
    element: str = "none"
    effects: list[dict] = field(default_factory=list)
    exhaust: bool = False
    solve: list[str] = field(default_factory=list)
    # Charter A0 / R92-3b. Two orthogonal scales:
    #   {fight: [early|mid|late], run: [early|late]}
    # `solve` answers "what does this card do"; this answers "WHEN is that
    # worth anything", which is the coordinate the Act 2 wall lives on -- a
    # pool can be fully covered on `solve` and still have every one of an
    # archetype's answers land in the wrong half of the fight.
    #
    # INERT HERE BY DESIGN. Nothing in the engine reads it; it is descriptive
    # metadata of the same class as `register` and `solve` beside it, and the
    # C# codegen whitelists it the same way. It is DECLARED rather than left
    # unknown because from_dict below refuses unknown fields, and the sheets
    # carry it on all 219 rows. Values are machine-derived
    # (tools/role_tempo.py::fight_bands / run_bands) and written by
    # tools/suggest_role_tempo_tags.py --land, whose --check fails if a hand
    # edit moves one away from the rule that produced it. Cross-session note:
    # docs/sprint-axis-validity-track-a-log-2026-08-04.md.
    tempo_band: dict = field(default_factory=dict)
    archetypes: list[str] = field(default_factory=list)
    role: str = "glue"
    tags: list[str] = field(default_factory=list)
    companion: Optional[dict] = None
    # Companion-sheet fields (mondstadt-companions.yaml)
    star: Optional[int] = None
    role_c: Optional[str] = None          # applier | buffer | trigger
    personal_pool: Optional[str] = None
    requires: Optional[str] = None        # e.g. burst_energy_full
    nation: Optional[str] = None          # set by the loader from the sheet name
    # principles v1.9: kit, not loot. Never in the draftable pool or the
    # starting deck; granted to hand when the Burst meter first fills, and
    # returns to the kit (no pile) after play so a refill re-grants it.
    kit_card: bool = False
    # R37: starts in the opening hand (top of the shuffled draw pile).
    # Today only upgrades set this ({innate: true} -- Catalytic Converter+);
    # sparks_n_splash's "innate-on-charge" is its OWN mechanism, untouched.
    innate: bool = False
    # Ordinary Retain. Burst cards also retain through their kit tag, but a
    # card upgrade such as Hot Hands+ can now express the base-game keyword
    # without pretending to be a Burst.
    retain: bool = False
    # principles v1.8: standard-banner 5-stars (Jean/Mona/Diluc) are ordinary
    # nation-pool rares that participate in the banner roll like anyone else.
    # The tag exists so that IF banner-variance data shows bad-roll bricking,
    # flipping them to always-available "off-banner floor" status is one flag
    # rather than a redesign. No card carries it yet -- those 5-stars are not
    # designed (Mona's Omen is blocked on the amp-cap conversation).
    standard: bool = False
    # Furina kickoff §3.1: shared schema, all sheets. Companion rows derive
    # it from the id prefix and personal sheets from the filename (loader);
    # an explicit field wins. Cards with no character are invalid Spotlight
    # targets -- the selector greys them out rather than erroring.
    character: Optional[str] = None
    # Curtain Call sweep (R85): the register a card's NAME speaks in. Shared
    # schema on purpose -- Columbina and future characters inherit the field;
    # the value vocabulary is per-character (Furina: salon | archon | private,
    # enforced by tools/lint_furina_registers.py -- the same-action-same-nation
    # precedent applied to naming). Purely descriptive: NOTHING in the engine
    # or the drafter may ever read it (cell-1 byte-identity is the pin).
    register: Optional[str] = None
    # Kokomi kickoff §2.3: combat-local provenance stamped by the conscript
    # op (the generated_by_guest_star pattern). PROPOSED reading of ruling
    # ask §6.7: a conscripted companion is SELF-sourced for SUPPORT_CARRY /
    # control-provenance purposes — she paid a card of her own deck for it.
    conscripted: bool = False
    # Kokomi Assist lane (kickoff §2.3 discard verb): Sly — effects that
    # fire when this card is discarded BY A CARD EFFECT. The end-of-turn
    # hand flush is NOT a Sly trigger, and neither are draw-pile discards
    # (scry); both scopings are enforced (and commented) at the one trigger
    # site in effects._op_discard. Empty on every non-Kokomi card.
    sly: list[dict] = field(default_factory=list)
    # BASE-GAME `CardKeyword.Sly` (ask A4, ruled 2026-07-27: implement it
    # true to the game). A DIFFERENT MECHANIC FROM `sly` ABOVE, wearing the
    # same word: when this card is discarded from hand by a card effect it
    # is AUTO-PLAYED for free (CardCmd.DiscardAndDraw -> CardCmd.AutoPlay,
    # AutoPlayType.SlyDiscard), which is a whole card play -- it fires the
    # card-played hooks, counts toward cards_played_this_turn, and routes to
    # its own result pile afterwards. Kokomi's `sly` resolves an authored
    # effect list instead and plays nothing. The unification of the two is
    # filed as tech debt (docs/tech-debt-audit-2026-07-26.md); until it
    # lands, the trigger site in effects._op_discard handles both and the
    # extractor maps CardKeyword.Sly onto THIS field only.
    sly_keyword: bool = False
    # Guest Star rows (fontaine-companions.yaml): generated cameos, scoped
    # to a personal pool. Never in shared rewards or the banner roll; the
    # equal-rarity clause on generators is what respects 5-star scarcity.
    guest_star: bool = False
    # Combat-local provenance: set on every card created by a Guest Star
    # generator, including ordinary shared companions pulled by that effect.
    # Guest Cast treats this temporary guest like every other Companion.
    generated_by_guest_star: bool = False
    # "Spend N Encore:" cost line (kickoff §4). A playability gate, not an
    # overdraw: cards that may legally overdraw into HP use the
    # spend_encore op instead.
    encore_cost: int = 0
    # NOTE: `fanfare_cost` was RETIRED by "The Tide Turns" (F-A4). Fanfare is
    # a read-only momentum stat; no card spends it. See RETIRED_CARD_FIELDS.
    # Base-game parity (Ironclad pool): CanBeGeneratedInCombat. Feed sets it
    # false so a generator cannot conjure the card that permanently raises
    # max HP. MUST be honored by generate_from_pool -- otherwise Stoke
    # over-generates and the whole comparison biases upward.
    generatable: bool = True
    # Base-game parity: HowlFromBeyond's AfterAutoPostPlayPhaseEntered hook.
    # When this card is sitting in the EXHAUST pile at the end of the player
    # turn it plays itself once for free and then goes to discard. A narrow
    # boolean on purpose -- one card in 87 does not justify a general
    # `triggers:` framework, and the house rule is implement-or-log, not
    # generalize. Read by effects.player_turn_end_triggers.
    on_exhaust_autoplay: bool = False
    # DrumOfBattle: an explicit AfterCardExhausted payout. This is card
    # metadata rather than an on-play effect: playing Drum normally sends it
    # to discard; only another effect exhausting it grants the energy.
    on_exhaust_energy: int = 0
    # Stomp: its combat hook applies a this-turn discount for each Attack the
    # owner has already played. Keeping the rate on the card lets card_cost()
    # read the live turn counter without mutating the printed/base cost.
    cost_reduction_per_attack_this_turn: int = 0
    # Pinpoint. Declarative and read at cost time, which is exactly
    # equivalent to the base game's two halves (a retroactive ReduceCostBy
    # when it enters combat, then -1 per Skill afterwards) without needing
    # an out-of-play hook: at any moment both say "printed cost minus the
    # Skills played this turn", and both reset at the turn boundary.
    cost_reduction_per_skill_this_turn: int = 0
    # EnergyCost.AddThisTurn / AddThisCombat / SetToFreeThisTurn -- state the
    # base game keeps on the CARD INSTANCE, not on its owner. Two copies of
    # the same card discount themselves independently, and the combat-scoped
    # one survives the card leaving hand and being redrawn. `free_this_turn`
    # is a SET, not a delta: Bullet Time zeroes the cost outright.
    cost_delta_this_turn: int = 0
    cost_delta_this_combat: int = 0
    free_this_turn: bool = False
    # Hand Trick grants Sly for one turn only. Kept separate from the printed
    # `sly_keyword` so the grant expires without editing what the card prints.
    sly_this_turn: bool = False
    # Enchantment rider (R82, docs/enchantments-design-2026-07-27.md).
    # Per-INSTANCE like the cost fields above: two Shivs may differ in
    # enchantment, and deepcopy clone sites (Anger/Nightmare shapes) carry
    # the rider with the instance -- the correct base-game answer. The
    # run-wide enchantment SUBSYSTEM (grant screens, enchanting relics) is
    # outside the parity world with relics and events; these two fields are
    # the whole mechanic. Ratified as open house design space.
    enchant_damage: int = 0       # flat rider on this attack's damage
    enchant_effects: list[dict] = field(default_factory=list)  # after own fx
    # --- Status cards (multi-act §10.2 injection op; engine/statuses.py).
    # type == "status" cards are UNPLAYABLE (combat.card_playable) and exist
    # only inside a combat: enemies inject them into the player's piles; the
    # run layer rebuilds the player from deck_ids each fight, so they never
    # leak into the deck. Both fields are 0 on every designed card, so the
    # frozen battery and all existing content are dead branches. ---
    status_eot_damage: int = 0    # Burn/Wither: damage at end of player turn
    #                               while in hand (blockable, StS-real)
    status_draw_damage: int = 0   # Toxic (§10.3 ratified): HP loss on draw
    # DEPRECATED (ruled R20, 2026-07-20): a parallel M9 session introduced
    # inline `upgrade:` fields on klee-cards.yaml rows; the ruling made
    # *-upgrades.yaml sheets the ONE upgrade convention. Tier 0 IGNORES
    # this field, and the loader now emits a loud warning per offending
    # sheet (silent-ignore risked an inline-only upgrade that never
    # applies). The field itself stays so the loader never hard-fails on
    # a shared sheet again; the M9 revert landed 2026-07-20 and the
    # no-inline-upgrades test (test_upgrades) now runs un-allowlisted.
    upgrade: Optional[dict] = None

    @property
    def is_companion(self) -> bool:
        return self.role_c is not None or "companion" in self.tags

    @classmethod
    def from_dict(cls, d: dict) -> "Card":
        known = {f for f in cls.__dataclass_fields__}
        # Retired grammar fails LOUDLY and by name, never silently ignored:
        # a sheet row that still declares a dead field is a card whose author
        # believes it does something. The generic "unknown fields" message
        # below would technically catch these, but it reads as a typo rather
        # than as a retirement, and the fix is different in each case.
        retired = sorted(set(d) & set(RETIRED_CARD_FIELDS))
        if retired:
            why = "; ".join(f"{f}: {RETIRED_CARD_FIELDS[f]}" for f in retired)
            raise ValueError(
                f"card {d.get('id')!r} declares RETIRED field(s) "
                f"{retired} -- {why}")
        unknown = set(d) - known
        if unknown:
            raise ValueError(f"card {d.get('id')!r}: unknown fields {sorted(unknown)}")
        return cls(**d)

    def __deepcopy__(self, memo):
        """Hand-rolled deep copy. Cards are copied on every ``get_card`` and
        every in-combat clone (Dual Wield, conscript, Armaments), which put
        generic ``copy.deepcopy`` at ~half of a Tier 0.5 run's total runtime:
        it walks all ~40 fields through the memo machinery even though all but
        a handful are immutable scalars.

        The copy is byte-identical to the generic one -- ``_MUTABLE_FIELDS``
        holds every container-valued field, and card payloads are plain
        yaml-shaped data (dict/list/scalar), so ``_copy_plain`` covers them.
        ``test_state.py`` pins both claims against ``copy.deepcopy`` for the
        whole loaded card index.
        """
        new = Card.__new__(Card)
        memo[id(self)] = new
        d = dict(self.__dict__)
        for name in _MUTABLE_FIELDS:
            val = d[name]
            if val is not None:           # an EMPTY list still gets a fresh
                d[name] = _copy_plain(val)   # one -- apply_upgrade appends
        new.__dict__ = d
        return new


@dataclass
class Bomb:
    """Delayed damage charge on an enemy (Klee signature, spec §4.2)."""
    damage: int
    element: str = "pyro"
    turn_placed: int = 0          # for modify_bombs scope: placed_this_turn


@dataclass
class Fighter:
    hp: int
    max_hp: int
    block: int = 0
    powers: dict[str, int] = field(default_factory=dict)   # name -> stacks

    @property
    def alive(self) -> bool:
        return self.hp > 0


@dataclass
class Player(Fighter):
    energy: int = 0
    sparks: int = 0
    element: str = "none"         # character element (catalyst cadence)
    cadence: str = "skill"        # catalyst: every attack applies element
    burst_energy: int = 0
    burst_max: int = 0            # 0 = character has no burst meter
    draw_pile: list[Card] = field(default_factory=list)
    hand: list[Card] = field(default_factory=list)
    discard_pile: list[Card] = field(default_factory=list)
    exhaust_pile: list[Card] = field(default_factory=list)
    relic_hooks: list[str] = field(default_factory=list)   # e.g. ["spark_on_detonation"]
    # --- combat-side relic engine (engine/relics.py); EMPTY on the frozen
    # battery, so every relic code path is a dead branch there (anchor lock).
    # Battery players are built by loader.build_player, which never sets this;
    # only build_player_from_ids(relic_effects=...) in the run layer does. ---
    relic_effects: list[dict] = field(default_factory=list)  # dicts keyed 'hook'
    # power name -> the card id that power was told to create. Set by an
    # apply_power row carrying `payload`; read by the refpowers hook that
    # makes the card. Keeps decompiled card ids out of committed engine code
    # while letting a parity power create a character's own token.
    power_payloads: dict[str, str] = field(default_factory=dict)
    first_hp_loss_fired: bool = False        # on_first_hp_loss_draw, per combat
    relic_conditional_applied: dict[str, int] = field(default_factory=dict)
    #                                        # conditional_power (Red Skull):
    #                                        # key -> delta currently applied,
    #                                        # so re-eval never drifts/doubles
    # --- combat-side potions (engine/potions.py); EMPTY on the frozen battery,
    # so every potion code path is a dead branch there (anchor lock). Battery
    # players are built by loader.build_player, which never sets these; only
    # build_player_from_ids in the run layer does. potion_slots is the held
    # capacity (Potion Belt relic raises it); node_kind gives combat.py the
    # elite/boss context the offensive branch reads, "" everywhere else. ---
    potions: list[str] = field(default_factory=list)
    potion_slots: int = C.POTION_SLOTS
    node_kind: str = ""           # "", "normal", "elite", or "boss"
    kit_cards: list[Card] = field(default_factory=list)    # v1.9: the Burst(s)
    # --- Furina (kickoff §3/§4); inert defaults for everyone else ---
    character_id: str = ""        # who this player IS (self-Spotlight rate)
    # --- Kokomi (kickoff v1 §2.1): the Bake-Kurage meter. Uncapped, never
    # expended, read (not consumed) by finisher effects; accrues ONLY at
    # the exhaust funnel + explicit gain_charge lines + converted Strength.
    # Reset per combat in run_fight. Dead field for everyone else. ---
    charge: int = 0
    encore: int = 0               # unbounded per-combat buffer (v1.6 style)
    fanfare: int = 0              # read-only momentum stat; global pool
    fanfare_cap: int = 0          # 0 = character has no Fanfare resource.
                                  # Since "The Tide Turns" this is a high
                                  # SAFETY RAIL, not a design dial -- under
                                  # decay the ceiling does not bind.
    # The out-of-combat ceiling, used by run_fight to REWIND fanfare_cap
    # between fights. `player` is one object reused across every combat in a
    # run, so without a rewind the cap ratchets upward all run.
    #
    # WHY A SNAPSHOT RATHER THAN A SUBTRACTION. run_fight used to rewind with
    # `fanfare_cap -= fanfare_floor`, which was exact only while
    # gain_fanfare_floor was the ONLY writer of either field and always moved
    # both by the same n. The Fanfare rework (2026-07-28) broke that
    # coincidence twice over: `raise_fanfare_cap` (Track B) moves the cap
    # alone, and `drop_fanfare_to_floor` (Track C.2) moves the floor alone
    # and DOWNWARD. Under the old arithmetic a Fanfare Cap card leaked its
    # headroom into every later fight and a Hyperbeam ADDED ceiling on the
    # way out. A snapshot cannot drift no matter how many writers exist.
    fanfare_cap_base: int = 0
    # The baseline the meter rests on. Decay clamps here, never below. The
    # "Fanfare +X" keyword raises floor, cap AND current together
    # (resources.gain_fanfare_floor) -- raising the cap alongside the floor
    # is what keeps the gradient alive instead of re-pinning the meter.
    #
    # MAY BE NEGATIVE since the Hyperbeam (Track C.2, RULED): The Final
    # Verdict digs the floor out from under the meter, and the player climbs
    # back out with activity. Readers clamp at zero via resources.readable,
    # so a negative meter turns effects off rather than inverting them.
    fanfare_floor: int = 0
    # Salon v2 (rework 2026-07-23): the typed member queue, FIFO, max
    # SALON_MEMBER_SLOTS, duplicates legal (Defect-orb geometry). SOURCE OF
    # TRUTH for the Salon; powers["salon_member"] mirrors len(salon) so
    # every count read (has_salon_members, pilot, instruments) still works.
    salon: list[str] = field(default_factory=list)
    spotlight: Optional[str] = None   # THE per-player registry: one
                                  # designated character at a time; a second
                                  # designation re-aims, never stacks. The
                                  # guest-cast sentinel means every Companion
                                  # card rather than one named character.

    def __post_init__(self) -> None:
        # Seed the out-of-combat ceiling from the printed one, so EVERY
        # construction path is correct without having to know about the
        # field: the two loader builders, the batteries, and every test that
        # hand-rolls a Player. Setting it only at the loader would have made
        # run_fight rewind a hand-built Furina's cap to ZERO on her second
        # fight -- a silent character-loses-her-resource bug reachable only
        # from paths the loader does not own.
        #
        # `or` rather than a None sentinel: 0 means "no Fanfare resource" for
        # the cap already, so the two spellings of absent agree.
        if not self.fanfare_cap_base:
            self.fanfare_cap_base = self.fanfare_cap


@dataclass
class Enemy(Fighter):
    name: str = "enemy"
    intents: list[dict] = field(default_factory=list)      # rotating script
    intent_index: int = 0
    aura: Optional[str] = None
    aura_turns_left: int = 0
    bombs: list[Bomb] = field(default_factory=list)
    # Klee survival sprint: the first attack action this enemy makes while
    # Bombed is suppressed. This per-enemy combat latch keeps an armed-Bomb
    # engine from becoming permanent Weak against bosses.
    bomb_suppression_spent: bool = False
    is_boss: bool = False
    # NC-7 alpha (Q13 / R117, verbatim "I'd say A"): the sim's mechanical
    # mirror of the game's `MinionPower` fact -- the assembly's ONLY
    # per-creature "secondary enemy" concept (reflection findings recorded in
    # review/parity-sweep/noncard-triage-memo.md, NC-7 EXECUTION NOTE).
    # Read by reactions._react: in a boss ROOM, only minion-flagged creatures
    # can be Frozen; every other creature takes the Vulnerable substitution.
    # Set True by combat's summon intent (the game applies MinionPower to
    # summoned adds -- gas-bomb/guardbot/parafright/tough-egg dossiers) and
    # authorable per-enemy in yaml, same passthrough as is_boss. No authored
    # roster enemy carries it today: Kaiser Crab's claws are slotted
    # monsters, NOT minions, verified by reflection in the execution note.
    is_minion: bool = False
    sleep_turns: int = 0        # skips its turn while > 0 (BURST CHECK)
    # NC-7 (R116, Errata Batch 2 item 5): a DURATION COUNTER, not a one-shot
    # boolean. Turns remaining, decremented once at the end of the enemy side
    # (combat._run_rounds); stacking EXTENDS it. While it is above zero the
    # enemy's actions deal FROZEN_DAMAGE_MULT, and the first Attack hit
    # Shatters (bonus damage, and Shatter clears the whole counter).
    #
    # The mod's `FrozenPower` was already a `PowerStackType.Counter` on an
    # unconditional `AfterSideTurnEnd(Enemy)` clock; the sim carried a boolean
    # consumed by ACTING. R116 ruled the mod's timer canonical and this is the
    # sim adopting it. Consequences that follow from the timer rather than
    # from any separate decision: a double freeze lasts two enemy sides, a
    # sleeping or skipping enemy loses its freeze anyway, and a freeze that
    # lands after the enemy has already acted is spent by that same side-end.
    frozen: int = 0
    frozen_by_companion: bool = False   # control_uptime provenance (§2.2a)
    # Base-game parity: ShouldOwnerDeathTriggerFatal. The game gates Fatal
    # effects (Feed) on the target's powers all agreeing the death counts --
    # summoned adds do not. Defaults True; the summon intent in
    # combat._enemy_turn must set it False or Feed farms minions for
    # permanent max HP, which is exactly the invisible upward bias this
    # project exists to catch. Read by effects.deal_damage_to_enemy.
    counts_for_fatal: bool = True
    # --- Multi-act §10.2 boss ops (all inert-by-default; battery never sets
    # them, so every branch is dead on the frozen anchor). ---
    # Kaiser Crab's Crab Rage: {"powers": {name: stacks}, "block": int}
    # applied ONCE at this enemy's next turn start after any ally has died.
    ally_death_buff: Optional[dict] = None
    ally_death_fired: bool = False
    # HP-threshold phases (Test Subject): remaining phase specs, each
    # {"hp": int, "intents": [...]}. When hp <= 0 with phases remaining, the
    # enemy revives into the next phase (combat._settle_phases) instead of
    # dying; counts_for_fatal must be False until the LAST phase (spawn and
    # _settle_phases maintain this) so Feed cannot farm phase-downs.
    phases: list[dict] = field(default_factory=list)
    # §10.9 promotions (2026-07-23 red-pen): the per-card-played enemy
    # counterplay class, previously skipped as "flavor". Inert-by-default,
    # same contract as the §10.2 ops -- the battery never sets either, so
    # every branch is dead on the frozen anchor.
    # Slow N (Bygone Effigy): "Whenever you play a card, this enemy receives
    # N% more damage from Attacks this turn." Resets each player turn (reads
    # state.cards_played_this_turn, which already resets there).
    slow: int = 0
    # Skittish N (Phantasmal Gardener): "The first time it is hit each turn,
    # it gains N Block. Does not stack." The latch resets each player turn.
    skittish: int = 0
    skittish_fired: bool = False
    # The turn this enemy entered its CURRENT phase; `ramp` counts from here,
    # not from combat start (combat._settle_phases stamps it on each revive).
    # 0 for every unphased enemy, which is combat start -- so the frozen
    # battery and every single-bar roster enemy are untouched.
    phase_start_turn: int = 0
    # How many times each intent index has been TAKEN this combat, for
    # `ramp_per_use`. Keyed by index so a rotation is unambiguous.
    intent_uses: dict[int, int] = field(default_factory=dict)

    def current_intent(self) -> dict:
        return self.intents[self.intent_index % len(self.intents)]

    def advance_intent(self) -> None:
        self.intent_uses[self.intent_index % len(self.intents)] = (
            self.intent_uses.get(self.intent_index % len(self.intents), 0) + 1)
        self.intent_index += 1

    def ramped_amount(self, intent: dict, turn: int) -> int:
        """This intent's attack amount at `turn`, with both ramp shapes.

        `ramp` is PER TURN, counted from the start of this enemy's current
        phase (`ramp_after` delays the start further). Phase-relative is the
        whole point: a ramping intent that first appears in a boss's SECOND
        phase must not arrive pre-ramped by however long the first bar took
        to chew through. Unphased enemies have phase_start_turn 0, so
        Byrdonis and the frozen PUNISHER are bit-identical to before.

        `ramp_per_use` is PER USE of this intent -- the "it grows every time
        it is taken" shape (Test Subject's Multi-Claw gains a hit each use).
        Turn-ramping cannot express it: the value would depend on how many
        non-attack beats sit between two uses, so adding a beat would
        silently retune the enemy.

        Both default to absent, and an intent may set either or neither.
        """
        amount = intent["amount"]
        ramp = intent.get("ramp", 0)
        if ramp:
            elapsed = turn - self.phase_start_turn - intent.get("ramp_after", 0)
            amount += ramp * max(0, elapsed)
        per_use = intent.get("ramp_per_use", 0)
        if per_use:
            amount += per_use * self.intent_uses.get(
                self.intent_index % len(self.intents), 0)
        return amount


@dataclass
class CombatState:
    player: Player
    enemies: list[Enemy]
    rng: random.Random
    # DEDICATED STREAM for the hand-full selector fallback (sitting 2026-08-06,
    # family X14 leg (b)). A new stochastic surface never draws from `rng`:
    # doing so would advance the main stream on every jammed-hand turn and
    # silently renumber every measurement taken before the fallback existed --
    # the same reason tier05 draws the banner from random.Random(seed + 2e9).
    # Offset 4e9; the registry of taken offsets lives in understudy/rng.py.
    # The default keeps direct CombatState(...) construction (tests, fixtures)
    # working; run_fight seeds it from the fight seed.
    selector_rng: random.Random = field(
        default_factory=lambda: random.Random(4 * 10 ** 9))
    turn: int = 0
    cards_played_this_turn: int = 0
    log: list[dict] = field(default_factory=list)          # event stream for metrics
    # Formula / conditional context (reset per card play in resolve_card)
    detonations_total: int = 0            # The Big One formula
    reactions_this_card: int = 0          # reaction_triggered_by_this
    reactions_this_turn: int = 0          # reaction_triggered_this_turn
    encore_spend_draws_this_turn: int = 0  # encore_spend_draw once-per-turn
    #                                        latch (Curtain Call, R85)
                                          # (Chevreuse; reset per turn)
    kills_this_card: int = 0              # killed_target
    # Kills that the base game's Fatal gate would honor (Enemy
    # .counts_for_fatal). Separate from kills_this_card so the existing
    # killed_target predicate keeps its exact meaning for Klee/Furina.
    fatal_kills_this_card: int = 0        # killed_target_fatal (Feed)
    exhausted_this_card: int = 0          # generate_from_pool amount_formula
    block_gains_this_card: int = 0        # exact multi-gain block hooks
    # The block those gains actually PRODUCED, which is a different question:
    # DodgeAndRoll pays BlockNextTurn equal to what GainBlock returned, after
    # Dexterity and Frail. Kept beside the count rather than replacing it --
    # refpowers reads the count to divide a per-gain allowance.
    block_gained_this_card: int = 0
    discards_this_card: int = 0           # CalculatedGamble's draw-back count
    last_drawn_type: str = ""             # EscapePlan's drawn-card branch
    salon_replacements_this_card: int = 0 # overflow count for current card
    cards_exhausted_this_turn: int = 0     # EvilEye / ForgottenRitual
    # Kokomi §2.4: the prevention ward's per-round latch ("first unblocked
    # hit per turn"); reset at player turn start with the other windows.
    prevention_used_this_turn: bool = False
    # Kokomi §7 engine_closure diagnostic (report-only, R14): cards created
    # into any pile this player turn (add_card tokens, conscript-create,
    # generators). Reset at player turn start.
    cards_created_this_turn: int = 0
    hp_lost_this_turn: int = 0             # Spite's live history predicate
    player_damage_events: int = 0          # TearAsunder hit-count history
    # Free-play machinery (Havoc / Cascade / HowlFromBeyond). The depth
    # counter backstops the seen_states guard in combat._player_turn, which
    # only samples BETWEEN pilot plays and is structurally blind to a nested
    # free-play chain. force_random_targeting matches the base game, which
    # rolls a random enemy for TargetType.AnyEnemy autoplays rather than
    # using tier0's lowest-HP pilot aim -- variance IS the point of Havoc.
    free_play_depth: int = 0
    force_random_targeting: bool = False
    current_card_cost: int = 0            # this_cost_zero
    current_x: int = 0                    # X-cost cards
    sparks_at_play: int = 0               # bank BEFORE this card's own spark
                                          # spend (Gleeful Barrage; R39)
    companions_played: list[str] = field(default_factory=list)
    # Blocking Notes' slope (rework Track C.3, 2026-07-28). A per-TURN count
    # where companions_played above is a per-COMBAT list, so the two cannot be
    # derived from each other and both have to exist.
    #
    # Counts the Guest Star TOKEN plays too, deliberately: the B2
    # printed-cost lesson (a cost-<=0 play neither benefits nor consumes) does
    # NOT apply here, because this is a PAYOFF and not a discount. A payoff
    # that ignored generated Companions would punish the deck that generates
    # them, which is the deck this card is for.
    companion_plays_this_turn: int = 0
    companion_cost_delta_this_turn: int = 0   # cost_mod op
    replay_next_companion: int = 0            # Study Buddy
    current_card_companion: bool = False      # control provenance (§2.2a)
    spotlighted_cards_this_turn: int = 0      # Ovation + the reserve cap
    # B2 (playtest-2, 2026-07-28): Leading Role's OWN first-play window,
    # counting only Spotlighted plays whose PRINTED cost is >= 1.
    #
    # Separate from the counter above on purpose. That one is the Spotlight
    # activity count and feeds Ovation, the reserve cap, spotlight_draw and
    # spotlight_encore_first -- all of which should keep counting every
    # Spotlighted play, free ones included. Only the DISCOUNT has to ignore
    # cost-0 plays, because only the discount is unable to pay them: it
    # skips `originalCost <= 0` and then found its window already spent.
    # Ethereal Spotlight's free token is Spotlighted under Center Stage and
    # arrives every turn, so in practice the discount never fired at all.
    spotlighted_paid_cards_this_turn: int = 0
                                              # (SPOTLIGHT_CARDS_PER_TURN_CAP)
    spotlight_moved_this_turn: bool = False   # selector-payoff predicates
    spotlight_moves_this_combat: int = 0      # (sheet pass 1)
    # --- base-game Ironclad parity (engine/refpowers.py); inert otherwise ---
    in_player_turn: bool = False          # StS2 CombatState.CurrentSide, which
                                          # Inferno and Rupture both gate on
    card_play_depth: int = 0              # >0 while a card is mid-play
                                          # (Rupture's deferral window)
    rupture_pending: int = 0              # strength owed to the card in play
    # OutbreakPower's internal `timesPoisoned`. Combat-local and NOT reset per
    # turn: the source keeps it on the power's Data object for the whole
    # fight and takes it mod 3, so a third poison two turns later still pays.
    outbreak_poisonings: int = 0
    # CardDiscardedEntry / CardDrawnEntry, the two combat-history counts the
    # Silent's calculated-damage cards read. `discards_this_turn` counts only
    # CARD-EFFECT discards from hand -- the end-of-turn flush reaches the
    # discard pile through CardPileCmd.Add and is not a CardCmd.Discard, so
    # the base game does not count it either. `cards_drawn_this_combat` is
    # NOT reset per turn; Murder scales across the whole fight.
    discards_this_turn: int = 0
    cards_drawn_this_combat: int = 0
    # THE ONLY THING COMBAT SAYS TO THE RUN LAYER ABOUT REWARDS, and it is a
    # statement of fact rather than a grant: "this fight earned N extra card
    # screens". The Hunt is the first source ([USER], 2026-07-27: the reward
    # is not in-combat -- if the effect fires you get an extra reward on the
    # REWARDS SCREEN afterwards, which is also what the base game does:
    # CombatRoom.AddExtraReward queues a CardReward for the room, and the
    # room hands it over when the fight is already over).
    #
    # combat.py must never roll, offer or draft anything: rewards are the run
    # layer's, exactly as the Burning Blood heal is (tier05/model.py, "combat
    # stays emit-only"). A tier 0 fight run on its own leaves this counter
    # sitting on the state, unread and harmless, which is the correct
    # behaviour for a layer that has no reward screen at all.
    extra_card_screens: int = 0
    dark_embrace_ethereal_count: int = 0  # deferred to after the hand flush
    attacks_played_this_turn: int = 0     # Juggling's ==3 trigger
    skills_played_this_turn: int = 0      # Pinpoint's self-discount
    # CardPlaysFinished this turn, counted per card TAG. PhantomBlades pays
    # only on the first tagged card played each turn, and "finished" is the
    # word that matters: the card currently resolving is not in here yet.
    tag_plays_this_turn: dict = field(default_factory=dict)
    block_gain_card_plays_this_turn: int = 0   # Unmovable's per-turn allowance
    no_energy_gain_ceiling: Optional[int] = None  # NoEnergyGain, seeded when
                                          # the power lands (not at the refill)

    def emit(self, event: str, **data: Any) -> None:
        self.log.append({"turn": self.turn, "event": event, **data})

    @property
    def living_enemies(self) -> list[Enemy]:
        return [e for e in self.enemies if e.alive]

    @property
    def over(self) -> bool:
        return not self.player.alive or not self.living_enemies

    # --- pile primitives ---

    def shuffle_discard_into_draw(self) -> None:
        self.rng.shuffle(self.player.discard_pile)
        self.player.draw_pile = self.player.discard_pile + self.player.draw_pile
        self.player.discard_pile = []

    def draw(self, n: int, from_hand_draw: bool = False) -> None:
        # StS2 gates every draw behind Hook.ShouldDraw. Only NoDrawPower
        # (Battle Trance) uses it, and it lets the turn-start hand draw
        # through -- hence the flag, which combat._player_turn sets.
        from tier0.engine import refpowers        # late import avoids cycle
        p = self.player
        if not refpowers.should_draw(p, from_hand_draw):
            self.emit("draw_denied", amount=n)
            return
        for _ in range(n):
            if not p.draw_pile:
                if not p.discard_pile:
                    return
                self.shuffle_discard_into_draw()
            if len(p.hand) >= C.MAX_HAND_SIZE:
                return
            card = p.draw_pile.pop(0)
            p.hand.append(card)
            self.cards_drawn_this_combat += 1
            # EscapePlan reads the TYPE of the card its own draw produced
            # (`(await Draw(1)).FirstOrDefault()`, then `.Type == Skill`).
            # Cleared at card start, so a card that drew NOTHING -- empty
            # piles, full hand -- reads as the source's null and pays out
            # nothing, rather than seeing whatever the last card drew.
            self.last_drawn_type = card.type
            self.emit("draw", card=card.id)
            # Hook.AfterCardDrawn, per CARD. CorrosiveWave and Speedster are
            # the only readers today and both are dead branches without a
            # Silent power up, but the site has to be inside the loop: they
            # pay per card drawn, not per draw effect.
            refpowers.after_card_drawn(self, card, from_hand_draw)
            if card.status_draw_damage:
                # Toxic (§10.3, ratified semantics): unblockable HP loss the
                # moment it is drawn. Late import mirrors refpowers above.
                from tier0.engine import resources
                p.hp -= card.status_draw_damage
                resources.note_player_hp_loss(self, card.status_draw_damage)
                self.emit("status_draw_damage", card=card.id,
                          amount=card.status_draw_damage)
