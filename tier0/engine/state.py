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
    # Today only upgrades set this ({innate: true} -- Catalytic Conversion+);
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
    # Spendable Fanfare payoff. Like encore_cost this is a playability gate,
    # but it is paid once after the card resolves so Fanfare scaling on that
    # card reads the audience level that funded the performance.
    fanfare_cost: int = 0
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
        unknown = set(d) - known
        if unknown:
            raise ValueError(f"card {d.get('id')!r}: unknown fields {sorted(unknown)}")
        return cls(**d)


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
    encore: int = 0               # unbounded per-combat buffer (v1.6 style)
    fanfare: int = 0              # capped activity stacks; global pool
    fanfare_cap: int = 0          # 0 = character has no Fanfare resource
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
    sleep_turns: int = 0        # skips its turn while > 0 (BURST CHECK)
    frozen: bool = False        # v1.5: next action -50% dmg; first attack
                                # hit Shatters (bonus dmg, removes Frozen)
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

    def current_intent(self) -> dict:
        return self.intents[self.intent_index % len(self.intents)]

    def advance_intent(self) -> None:
        self.intent_index += 1


@dataclass
class CombatState:
    player: Player
    enemies: list[Enemy]
    rng: random.Random
    turn: int = 0
    cards_played_this_turn: int = 0
    log: list[dict] = field(default_factory=list)          # event stream for metrics
    # Formula / conditional context (reset per card play in resolve_card)
    detonations_total: int = 0            # The Big One formula
    reactions_this_card: int = 0          # reaction_triggered_by_this
    reactions_this_turn: int = 0          # reaction_triggered_this_turn
                                          # (Chevreuse; reset per turn)
    kills_this_card: int = 0              # killed_target
    # Kills that the base game's Fatal gate would honor (Enemy
    # .counts_for_fatal). Separate from kills_this_card so the existing
    # killed_target predicate keeps its exact meaning for Klee/Furina.
    fatal_kills_this_card: int = 0        # killed_target_fatal (Feed)
    exhausted_this_card: int = 0          # generate_from_pool amount_formula
    block_gains_this_card: int = 0        # exact multi-gain block hooks
    salon_replacements_this_card: int = 0 # overflow count for current card
    cards_exhausted_this_turn: int = 0     # EvilEye / ForgottenRitual
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
    companion_cost_delta_this_turn: int = 0   # cost_mod op
    replay_next_companion: int = 0            # Study Buddy
    current_card_companion: bool = False      # control provenance (§2.2a)
    spotlighted_cards_this_turn: int = 0      # Ovation + the reserve cap
                                              # (SPOTLIGHT_CARDS_PER_TURN_CAP)
    spotlight_moved_this_turn: bool = False   # selector-payoff predicates
    spotlight_moves_this_combat: int = 0      # (sheet pass 1)
    # --- base-game Ironclad parity (engine/refpowers.py); inert otherwise ---
    in_player_turn: bool = False          # StS2 CombatState.CurrentSide, which
                                          # Inferno and Rupture both gate on
    card_play_depth: int = 0              # >0 while a card is mid-play
                                          # (Rupture's deferral window)
    rupture_pending: int = 0              # strength owed to the card in play
    dark_embrace_ethereal_count: int = 0  # deferred to after the hand flush
    attacks_played_this_turn: int = 0     # Juggling's ==3 trigger
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
            self.emit("draw", card=card.id)
            if card.status_draw_damage:
                # Toxic (§10.3, ratified semantics): unblockable HP loss the
                # moment it is drawn. Late import mirrors refpowers above.
                from tier0.engine import resources
                p.hp -= card.status_draw_damage
                resources.note_player_hp_loss(self, card.status_draw_damage)
                self.emit("status_draw_damage", card=card.id,
                          amount=card.status_draw_damage)
