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
                   "companion", "sly", "upgrade", "enchant_effects",
                   "enchant_first_play_effects", "plan")

# Card fields that a sheet row may NEVER declare again, with the reason the
# author needs. House pattern: a caught mistake becomes a lint, so the next
# person meets the rule instead of the symptom.
RETIRED_CARD_FIELDS = {
    "sly_keyword": (
        "The two Sly mechanics were unified on the standard effect-list "
        "grammar (EB-71, R174): the base-game keyword is now the reserved "
        "rider `sly: [{op: sly_autoplay}]` on the same `sly:` field Kokomi's "
        "Assist lane already used. A row that printed `sly_keyword: true` "
        "becomes `sly: [{op: sly_autoplay}]`; an EXTRACTED sheet must be "
        "re-emitted by tools/extract_base_game_pool.py, which writes the new "
        "shape."),
    "fanfare_cost": (
        "Fanfare is a read-only momentum stat ('The Tide Turns', F-A4) -- "
        "no card spends it, and Encore is Furina's only managed resource. "
        "A card that wants to reward a full meter READS it "
        "(bonus_formula: N_per_M_fanfare) or gates on it "
        "(if: fanfare_at_least_N); a card that wants to raise the player's "
        "permanent baseline grants a floor (op: gain_fanfare_floor)."),
}


# --- the unified Sly grammar (EB-71, R174) --------------------------------
#
# `Card.sly` is an effect list. One reserved rider in it means "the base-game
# keyword": when a card effect discards this card, PLAY it for free rather
# than resolve a list. `SLY_AUTOPLAY_OP` is deliberately absent from
# `tier0.engine.effects.OPS` -- it is not an on-play verb, it is never
# dispatched, and registering it would put an unpriceable entry in front of
# `tools/lint_op_parity.py`. Everything that reads printed effects reads
# `sly_riders()`, which filters it out, so the marker is worth exactly zero
# to the drafter -- the pre-unification price of the keyword, unchanged.
SLY_AUTOPLAY_OP = "sly_autoplay"
# The printed keyword (extractor output, Master Planner's permanent mark).
SLY_AUTOPLAY = {"op": SLY_AUTOPLAY_OP}
# Hand Trick's grant: the same rider, swept at the turn boundary.
SLY_AUTOPLAY_THIS_TURN = {"op": SLY_AUTOPLAY_OP, "until": "turn_end"}


def sly_autoplays(card: "Card") -> bool:
    """True when this card's Sly is the base-game auto-play keyword."""
    return any(fx.get("op") == SLY_AUTOPLAY_OP for fx in card.sly)


def sly_autoplays_permanently(card: "Card") -> bool:
    """True when the auto-play rider on this card has no expiry.

    The narrow question Master Planner asks. Before EB-71 it read the printed
    `sly_keyword` boolean, which Hand Trick's one-turn grant never set -- so
    playing a Hand-Tricked Skill under Master Planner upgraded that grant to
    permanent. Asking `sly_autoplays()` here instead would swallow the
    upgrade and let the grant expire, which is a live value change.
    """
    return any(fx.get("op") == SLY_AUTOPLAY_OP and "until" not in fx
               for fx in card.sly)


def sly_granted_this_turn(card: "Card") -> bool:
    """True when a TURN-SCOPED auto-play rider is on this instance.

    The narrow question Hand Trick's target filter asks, kept narrow on
    purpose: before EB-71 it read the `sly_this_turn` boolean, which a
    PRINTED keyword never set, so a printed-Sly Skill was a legal Hand Trick
    target. Asking `sly_autoplays()` here instead would quietly shrink the
    target pool and move combat value.
    """
    return any(fx.get("op") == SLY_AUTOPLAY_OP
               and fx.get("until") == "turn_end" for fx in card.sly)


def sly_riders(card: "Card") -> list[dict]:
    """The AUTHORED half of a card's Sly -- the effects a discard resolves."""
    return [fx for fx in card.sly if fx.get("op") != SLY_AUTOPLAY_OP]


def grant_sly_autoplay(card: "Card", rider: dict = SLY_AUTOPLAY) -> None:
    """Add the auto-play rider to ONE INSTANCE (rebinding, never appending).

    `Card.sly` is deep-copied per instance, but the sheet-loaded index card is
    shared until it is copied; rebinding to a fresh list means a grant can
    never leak backwards into the printed row.
    """
    card.sly = list(card.sly) + [dict(rider)]


def remove_instance(pile: list, card: "Card") -> bool:
    """Remove exactly THIS instance from the pile; True if it was there.

    Card is a dataclass, so `list.remove` / `in` compare by VALUE and two
    fresh copies of the same card are equal twins -- a value-based remove can
    take the twin and leave `card` aliased into two piles. Twins are not
    interchangeable either: cost_delta_this_combat, free_this_turn and a
    granted `sly` rider are per-INSTANCE state. Every remove-from-a-card-pile
    must go through here.
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
    # TWO vocabularies, split by C.RARITY_ODDS membership. Offered (draft,
    # reward, shop): common | uncommon | rare. Only ever REACHED, because
    # they have no odds row at all: basic | token | status | curse | event |
    # ancient. The split is declared in constants.py (RARITY_ODDS +
    # ACQUISITION_ONLY_RARITIES) and a rarity in neither table is a typo the
    # suite fails on, rather than a card that quietly leaves every pool.
    rarity: str = "common"
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
    # THE HEXEREI FAMILY MARK -- ONE WORD, NO EFFECT (the approved Mondstadt
    # companion workshop, sec.1 pick 2: "Hexerei is one word on a Universal.
    # It does nothing by itself. Klee's own readers and any future Hexerei
    # character's carry the payoff"). NOTHING in either engine reads this
    # field today; it is carried so a later reader can see which rows the
    # family owns without the mark having to be re-derived from a character
    # list. A field rather than a `tags:` entry because `tags` is already read
    # by four unrelated predicates (`is_companion`, `is_ethereal`, the sly
    # view, the skill_tag rail) and adding an inert word to a list that four
    # things filter is how an inert word stops being inert.
    hexerei: bool = False
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
    # EB-118: Ethereal printed on the BASE card. Until now the keyword was
    # reachable only through `tags: [ethereal]`, which is how the engine
    # sheets spell it for Statuses, Curses and the Spotlight token -- a
    # vocabulary personal sheets do not use for lifecycle keywords (they use
    # `exhaust:`, `innate:`, `retain:`). The field is the personal-sheet
    # spelling of the SAME keyword; `is_ethereal` below is the single
    # predicate the engine reads, so the two doors cannot drift apart.
    #
    # ORTHOGONAL TO `is_junk`. Ethereal is a timing keyword and junk is a
    # rarity class: an Ethereal PERSONAL card is still one of Kokomi's own
    # cards and still pays her Charge funnel when it burns (LAW, Kokomi
    # identity, [USER] 2026-08-23; pinned in test_ethereal_base_field).
    ethereal: bool = False
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
    # QUARANTINED (prototype surface only, R213 E1 / EB-183). The SECOND
    # reading of R216 D's Muster subsidy, and the one slice 2 could not put on
    # a card: slice 2 flipped the SIGN of the order's Charge line, which is an
    # effect list; this reading is a property of the exhaust FUNNEL. A recruit
    # whose order PAID FOR IT -- the order reduced the recruit's cost below its
    # printed one -- pays no Charge when it Exhausts, so one order cannot both
    # cheapen the unit AND be waged for rotating it out.
    #
    # THE STAMP IS WRITTEN AT ONE DOOR (`effects._op_conscript`, on a
    # `subsidy: waived` conscript op) and READ AT ONE DOOR
    # (`refpowers.after_card_exhausted`'s funnel). No shipped card carries the
    # op key, so on every shipped pool this field is False on every instance
    # and the funnel branch is dead -- which is the byte-identity guard
    # tier0/tests/test_eb183_muster_subsidy_funnel.py pins.
    #
    # SCOPED TO THE ORDER, NOT TO THE FUNNEL AT LARGE, deliberately: R226's
    # signed Charge LAW says the funnel does NOT narrow (her own cards AND
    # original Companions, Companions INCLUDED). A blanket Companion carve-out
    # would contradict that text; a prototype ORDER whose own recruits waive
    # their wage asks the open question without touching the shipped rule.
    muster_subsidised: bool = False
    # QUARANTINED (C.KURAGE_MEMORY, v3). Two combat-local provenance stamps of
    # the same class as `conscripted` above and `generated_by_guest_star`
    # below, and both are the difference between a rule and a loop:
    #   * `kurage_remembered` -- this INSTANCE has already enrolled in the
    #     memory. The general once-only guard, and the only one v3 keeps: a
    #     card cannot enrol twice for one Exhaust, and the two entry rules do
    #     not have to know about each other to stay honest.
    #   * `from_kurage_memory` -- this instance IS a memory copy. A copy never
    #     enrols, never pays Charge, never keys the pulse and is removed from
    #     combat rather than filed in a pile.
    # Both default False and nothing outside a flag branch reads either.
    kurage_remembered: bool = False
    from_kurage_memory: bool = False
    # THE PLAN LINE (QUARANTINED, C.KOKOMI_OVERHAUL, draft 6) -- the SECOND
    # HALF OF A PRINTED FACE, and the reason it is a card field rather than a
    # side table: what the card does if it is played on the Bake-Kurage
    # instead of where it would normally go is printed ON the card, in the
    # same effect vocabulary `effects:` speaks, and the C# emitter already
    # builds `IPlannedCard.PlanClauses` from this very key
    # (`gen_klee_cards.CARD_FIELDS` carries `plan`). Two readers, one
    # declaration.
    #
    # THE CLAUSES ARE THE SHEET'S OWN DICTS, not a typed record. The C# has to
    # type them (`KokomiPlan.Planned`) because a captured closure over the
    # writing card's context would be a use-after-free across the turn
    # boundary; this engine has no context to capture and already speaks
    # effect dicts everywhere, so the honest twin of "the clauses the sheet
    # declares" is the list the sheet declared. `kokomi_plan.PLAN_KINDS` is
    # the `Kind` enum's twin and refuses anything outside it.
    #
    # PROTOTYPE SURFACE ONLY, like `description:` -- no shipped sheet row
    # prints a Plan, and `tools/gen_klee_cards.card_level_reason` refuses one
    # on any character but Kokomi.
    plan: list[dict] = field(default_factory=list)
    # SLY -- ONE field, ONE word, one trigger (EB-71, R174; formerly two
    # near-identical mechanics, `sly` and `sly_keyword`). Effects that fire
    # when this card is discarded BY A CARD EFFECT. The end-of-turn hand
    # flush is NOT a Sly trigger, and neither are draw-pile discards (scry);
    # both scopings are enforced (and commented) at the one trigger site in
    # effects._op_discard.
    #
    # Two shapes ride the one list, and their BEHAVIOUR is unchanged by the
    # unification:
    #   * ordinary riders -- Kokomi's Assist lane (kickoff §2.3 discard
    #     verb): an authored effect list the discard resolves, playing
    #     nothing. Empty on every non-Kokomi card.
    #   * `SLY_AUTOPLAY` -- the base-game `CardKeyword.Sly` (ask A4, ruled
    #     2026-07-27: implement it true to the game): the discarded card is
    #     AUTO-PLAYED for free (CardCmd.DiscardAndDraw -> CardCmd.AutoPlay,
    #     AutoPlayType.SlyDiscard), a whole card play that fires the
    #     card-played hooks, counts toward cards_played_this_turn, and routes
    #     to its own result pile afterwards.
    # The autoplay rider is deliberately NOT an entry in the engine's OPS
    # registry and is never dispatched through `_resolve_effects`: the
    # tech-debt audit (§5) refused the reading where the keyword resolves an
    # effect list instead of playing the card, because that skips the
    # card-played events the Silent's own payoffs read. It is a marker the
    # one trigger site recognises; `sly_riders()` below is what everything
    # else reads, so the marker adds no printed value anywhere.
    sly: list[dict] = field(default_factory=list)
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
    # EB-83, the on-draw hook. `EnergyCost.SetThisCombat` is the base game's
    # ABSOLUTE combat-scoped cost modifier -- the one Slither writes when the
    # card is drawn -- where every field above it is RELATIVE. Kept as its own
    # field rather than folded into `cost_delta_this_combat` because a delta
    # cannot express "this card now costs 2" without first knowing what it
    # costs, and the point of a randomiser is that it does not care.
    # `on_draw_randomise_cost` is the roll's EXCLUSIVE bound (the game rolls
    # `NextInt(4)`, i.e. 0..3). Both are None on every card that ships today,
    # so both are inert and the frozen battery is byte-identical.
    cost_set_this_combat: int | None = None
    on_draw_randomise_cost: int | None = None
    # (Hand Trick's one-turn Sly grant used to be its own boolean,
    # `sly_this_turn`. EB-71 folded it into the unified `sly` list above as
    # `SLY_AUTOPLAY_THIS_TURN`, a rider carrying `until: turn_end`; the
    # turn sweep in refpowers.reset_turn_counters drops exactly those riders,
    # so a granted Sly still expires without editing what the card prints.)
    # Enchantment rider (R82, docs/archive/enchantments-design-2026-07-27.md).
    # Per-INSTANCE like the cost fields above: two Shivs may differ in
    # enchantment, and deepcopy clone sites (Anger/Nightmare shapes) carry
    # the rider with the instance -- the correct base-game answer. The
    # run-wide enchantment SUBSYSTEM (grant screens, enchanting relics) is
    # outside the parity world with relics and events; these two fields are
    # the whole mechanic. Ratified as open house design space.
    # R82 REOPENED ([USER], 2026-08-10, M7): the run layer now attaches
    # NAMED enchantments to deck cards from events (tier0/content/
    # enchantments.py), and five of the eight names it needs are not
    # expressible as flat damage plus an on-play effect list. The fields
    # below are that minimal extension -- still per-instance, still no
    # registry, still nothing that looks up an enchantment by name. Every
    # one is inert on a card with no enchantment, so the frozen battery and
    # all existing content stay byte-identical.
    enchant_damage: int = 0       # flat rider on this attack's damage
    enchant_effects: list[dict] = field(default_factory=list)  # after own fx
    enchant_block: int = 0        # Nimble: paid on EVERY Block gain (EB-85)
    enchant_damage_mult: float = 1.0        # Corrupted: x1.5 on this attack
    enchant_first_play_damage: int = 0      # Vigorous: first play of a combat
    enchant_first_play_effects: list[dict] = field(default_factory=list)
    #                                       Sown / Swift: first play of a combat
    enchant_top_of_draw: bool = False       # Perfect Fit: RESHUFFLE only
    enchant_played_this_combat: bool = False   # the first-play gate itself
    # --- Status cards (multi-act §10.2 injection op; engine/statuses.py).
    # type == "status" cards are UNPLAYABLE (combat.card_playable) and exist
    # only inside a combat: enemies inject them into the player's piles; the
    # run layer rebuilds the player from deck_ids each fight, so they never
    # leak into the deck. Both fields are 0 on every designed card, so the
    # frozen battery and all existing content are dead branches. ---
    status_eot_damage: int = 0    # Burn/Wither: damage at end of player turn
    #                               while in hand (blockable, StS-real)
    status_draw_damage: int = 0   # Toxic (§10.3 ratified): HP loss on draw
    # Normality (Field of Man-Sized Holes, 2026-08-10): "you cannot play more
    # than 3 cards this turn", read WHILE IN HAND by combat.card_playable.
    # A hand cap rather than a per-card gate, which is why it lives here and
    # not in `requires` -- the curse restricts every OTHER card, never itself
    # (it is a status and unplayable by type already).
    status_play_cap: int = 0
    # DEPRECATED (ruled R20, 2026-07-20): a parallel M9 session introduced
    # inline `upgrade:` fields on klee-cards.yaml rows; the ruling made
    # *-upgrades.yaml sheets the ONE upgrade convention. Tier 0 IGNORES
    # this field, and the loader now emits a loud warning per offending
    # sheet (silent-ignore risked an inline-only upgrade that never
    # applies). The field itself stays so the loader never hard-fails on
    # a shared sheet again; the M9 revert landed 2026-07-20 and the
    # no-inline-upgrades test (test_upgrades) now runs un-allowlisted.
    upgrade: Optional[dict] = None
    # `EB-315`. THE OPT-OUT FROM THE PROTOTYPE-STAGE UPGRADE RULE, and the one
    # field on this class whose value is a SENTENCE. The rule
    # (`content/upgrades.prototype_default_delta`) gives every staged row a
    # campfire choice, and `tier0/tests/test_prototype_surface.py` now holds
    # every row of the four overhaul arms to having one -- so a row that
    # genuinely cannot upgrade has to SAY SO, in the row, with the reason,
    # instead of being invisible in a gap between a rule's reach and a
    # register nobody reads. It is prototype-surface only (the loader refuses
    # it on a shipped id, exactly as it refuses `plan:`): a shipped upgrade is
    # a ruled number in `docs/<character>-upgrades.yaml`, and "this card has
    # none" is said there by the id's absence.
    #
    # BOTH ENGINES READ IT, which is why it is a field rather than a codegen
    # comment: `upgrades._prototype_deltas` skips a row declaring it, so the
    # sim cannot smith a card the mod prints as base-only.
    no_upgrade: Optional[str] = None

    @property
    def is_companion(self) -> bool:
        return self.role_c is not None or "companion" in self.tags

    @property
    def is_ethereal(self) -> bool:
        """Ethereal by either spelling -- the printed field or the tag.

        ONE predicate, for the reason `is_junk` below is one: combat reads
        the keyword at three seams (the retain split, the flush filter, the
        ethereal sweep) and a second door that only two of them knew about
        would burn a card in one place and discard it in another.
        """
        return self.ethereal or "ethereal" in self.tags

    @property
    def is_junk(self) -> bool:
        """A Status or a Curse -- never one of YOUR cards in the sense
        Kokomi's rotation law uses (LAW, Kokomi identity, [USER]
        2026-08-23). One predicate shared by the conscript pool, the
        chosen-exhaust pool and the Charge funnel so the three cannot
        drift apart. Lives on Card because refpowers and effects both need
        it and neither may import the other."""
        return self.rarity in ("status", "curse")

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


def fanfare_cap_base_term(max_hp: int) -> int:
    """The Fanfare ceiling's BASE term, taken from LIVE max HP (EB-97).

    `docs/current/characters/furina-identity-record.md` (ex-LAW) says
    "Fanfare is capped at %maxHP", and the mod reads it that
    way every time it is asked: `FurinaResources.FanfareCap` computes
    `FanfareCapFraction * creature.MaxHp + capBonus` from the creature's
    CURRENT MaxHp. tier0 used to freeze the base term at the sheet's printed
    `hp` and carry that number through every max-HP move in the run, so a
    Decipher (-24) or a Feed (+7) never reached the ceiling and the two
    engines disagreed -- inside a single combat, in Feed's case.

    Truncating `int()` rather than rounding, to match C#'s `(int)` cast on
    the same product. Clamped at zero because the term is a ceiling and a
    negative max HP is not a state either engine represents.
    """
    return int(C.FANFARE_CAP_FRACTION * max(0, max_hp))


def sync_fanfare_cap_to_max_hp(player: "Player") -> None:
    """Re-derive the cap's base term from the player's live max HP.

    Moves `fanfare_cap` and `fanfare_cap_base` by the SAME delta so every
    bonus riding on top of the base term survives: the in-combat grants
    (`raise_fanfare_cap`, `gain_fanfare_floor`) sit in `fanfare_cap` alone
    and must not be rewound here, and a hand-rolled cap (the batteries, the
    probes, every test that seats a number directly) is a bonus too as far
    as this is concerned -- it is preserved exactly while max HP holds still.

    A no-op for a character with no Fanfare resource, and a no-op while max
    HP has not moved since the last sync.

    Does NOT re-clamp the meter. The mod clamps in `GainFanfare` only, so a
    meter above a freshly-lowered ceiling stays put until the next gain
    drags it down -- `resources.gain_fanfare` has the same `min()` and gets
    there the same way.
    """
    if not player.fanfare_cap_base and not player.fanfare_cap:
        return                                   # no Fanfare resource
    delta = (fanfare_cap_base_term(player.max_hp)
             - fanfare_cap_base_term(player.fanfare_cap_hp))
    player.fanfare_cap_hp = player.max_hp
    if not delta:
        return
    player.fanfare_cap_base = max(0, player.fanfare_cap_base + delta)
    player.fanfare_cap = max(0, player.fanfare_cap + delta)


@dataclass
class Fighter:
    hp: int
    max_hp: int
    block: int = 0
    powers: dict[str, int] = field(default_factory=dict)   # name -> stacks
    # EB-95: the authority's `SkipNextDurationTick`, held per power name. A
    # duration Debuff freshly applied to a player-side creature does not lose
    # a stack to the AfterSideTurnEnd(enemy) tick that follows the application
    # within the same enemy side. Only the player ever carries entries.
    skip_next_duration_tick: set[str] = field(default_factory=set)

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
    # EB-83: THE STRUCTURED-POWER SIDECAR. `powers` is a `name -> int` map, so
    # a power carrying TWO numbers -- an amount AND a duration -- has nowhere
    # to put the second one. This is that second field, keyed by power name,
    # exactly as `power_payloads` above is: the engine already answers "this
    # power needs one more field than a stack count" with a sidecar map beside
    # `powers` rather than with a parallel object graph, and a second answer to
    # one question is how two lifetimes drift apart.
    #
    # The SPLIT is the engine's own stacks-are-turns grammar (`kurage_summon`,
    # `colossus`, `intangible`, `double_damage`, `ceremonial_garment`):
    # `powers[name]` holds TURNS REMAINING and this holds the amount those
    # turns pay. So the tick, the expiry and every existing reader of `powers`
    # keep working unchanged, and only the payout consults the sidecar.
    #
    # LIFETIME IS EXACTLY `powers`' LIFETIME -- default-empty on a freshly
    # built Player, and tier 0.5 builds one per fight (`tier05/model.py` ->
    # `loader.build_player_from_ids`), which is the whole of "survives nothing
    # across combats". Neither map is swept in `run_fight`, and this one must
    # not acquire a sweep that `powers` does not have: a carrier cleared on a
    # pass its own power is not cleared on is a power with an amount of zero,
    # which pays silently rather than expiring loudly. The op that writes it
    # deletes BOTH entries at expiry, so nothing lingers even within a combat.
    timed_power_amounts: dict[str, int] = field(default_factory=dict)
    first_hp_loss_fired: bool = False        # on_first_hp_loss_draw, per combat
    # THE MONDSTADT COMPANION OVERHAUL (QUARANTINED, C.COMPANION_OVERHAUL).
    # Nicole's Revelation asks whether you "had Block left at the end of your
    # last turn", and that cannot be read at the START of this one: the turn
    # tick clears Block before any start-of-turn power runs. So the answer is
    # LATCHED at the tail of `player_turn_end_triggers` and read at the head of
    # the next turn.
    #
    # A FIELD RATHER THAN A POWER STACK, on `first_hp_loss_fired`'s precedent
    # one line up: it is a per-combat yes/no about the player, not a stack that
    # anything applies, ticks or displays, and a fake power in `powers` would
    # show up in every digest that counts them. False on a freshly built Player
    # and re-zeroed in `run_fight` beside the other per-combat resources, so a
    # reused Player cannot carry one fight's answer into the next.
    mc_held_block_at_turn_end: bool = False
    # THE SAME ARM'S SECOND WAVE. Varka's Sturm und Drang says "your next
    # Attack deals 6 more damage OF THE SWIRLED ELEMENT", so the charge it
    # banks carries TWO numbers -- how much, and which element. The AMOUNT is
    # an ordinary power stack (`mc_swirl_charge`, so a second Swirl adds to it
    # exactly the way every other stack does); the ELEMENT has no stack to
    # live in, so it is latched here, on `mc_held_block_at_turn_end`'s own
    # precedent one line up. Overwritten by the LATEST Swirl, which is what
    # "the swirled element" names on a card that has just watched one happen.
    # Empty string means no charge is banked; the amount is the authority and
    # this is only read while it is non-zero.
    mc_swirl_element: str = ""
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
    character_id: str = ""        # who this player IS (Center Stage owner;
                                  # which cards read as "hers" vs Guest Cast)
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
    # The max HP the cap's base term was last derived from (EB-97). Not a
    # design number -- it is the bookkeeping that lets sync_fanfare_cap_to_
    # max_hp move the base term by a DELTA and so leave every bonus riding
    # on top of it (in-combat grants, hand-seated caps) untouched. Seeded in
    # __post_init__ from the constructed max HP so every build path is right
    # without knowing about the field.
    fanfare_cap_hp: int = 0
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
        # EB-97: the max HP the seated cap is understood to have come from.
        # Same reasoning as the line above -- seed it on EVERY construction
        # path, or a hand-built Furina's first max-HP move would be read as
        # a move away from 0 and re-derive the whole ceiling.
        if not self.fanfare_cap_hp:
            self.fanfare_cap_hp = self.max_hp


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
    # per-creature "secondary enemy" concept (reflection findings recorded
    # at `git show pre-simplification-2026-08-06:review/parity-sweep/
    # noncard-triage-memo.md`, NC-7 EXECUTION NOTE).
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
    # THE MONDSTADT COMPANION OVERHAUL (QUARANTINED, C.COMPANION_OVERHAUL).
    # Eula's Lightfall Sword is PLACED ON A TARGET and "for 2 turns it counts
    # your Attacks". The turns live in the ordinary power stack
    # (`powers['mc_lightfall_sword']`, ticked like every other duration); the
    # TALLY has no stack to live in, so it is a field on the body carrying the
    # blade -- `Player.mc_held_block_at_turn_end`'s precedent, on the other
    # side of the board. A second power id would have shown up as a power in
    # every digest that counts them, which a counter inside another power is
    # not. Zero on a fresh Enemy, and an Enemy is built per fight.
    mc_lightfall_tally: int = 0
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

    def ramped_times(self, intent: dict) -> int:
        """This intent's HIT COUNT, with the per-use growth shape.

        `times_ramp_per_use` is Multi-Claw's real mechanic (R128): the
        intent permanently gains hits each time it is taken -- 3, then 4,
        then 5. Until R128 this was approximated as `ramp_per_use` on the
        AMOUNT (30 -> 39 -> 48 against the real 30 -> 40 -> 50), which
        matched the totals within a hit but got the hit count wrong -- and
        hit count is load-bearing once per-hit powers exist: Painful Stabs
        wounds per hit, Intangible caps per hit."""
        times = intent.get("times", 1)
        per_use = intent.get("times_ramp_per_use", 0)
        if per_use:
            times += per_use * self.intent_uses.get(
                self.intent_index % len(self.intents), 0)
        return times



@dataclass
class KurageMemory:
    """ONE entry in the Kurage's memory (QUARANTINED, C.KURAGE_MEMORY, v3).

    v2 queued bare card ids and paid one flat threshold for any of them. v3
    prices each memory off the face that entered and aims it at the body the
    original was played against, so the queue has to carry more than an id:

      card_id    -- carries UPGRADE STATE (`foo` vs `foo+`), the loader's own
                    grammar, and is re-materialised through `loader.get_card`
                    at fire time.
      cost       -- the remembered face's own cost, as that instance read it
                    (permanent upgrade and a Muster's -1 included; temporary
                    combat discounts excluded by construction, because this is
                    read off the CARD and never off `combat.card_cost`).
      price      -- KURAGE_MEMORY_COST_PER_ENERGY x cost, computed once at
                    entry so the strip can SHOW it for the whole time the
                    memory is queued.
      target     -- the enemy the original was played against, or None. None
                    is the honest answer for a card that was never played --
                    a Muster's sacrifice, an Ethereal burn, a manual Exhaust
                    from hand -- and it means the fallback rule aims the copy.
      ephemeral  -- the original did NOT print Exhaust, i.e. somebody had to
                    burn it by hand. RECORDED, and currently behaviour-free:
                    v3 removes EVERY memory copy from combat, so there is no
                    second pile for a non-ephemeral copy to go to. It is kept
                    because it is what the strip must show and what a later
                    ruling would attach behaviour to.
      rule       -- "muster" (Rule 1) or "exhaust" (Rule 2). Report-only, and
                    the two rules never read it: they are independent.
    """
    card_id: str
    cost: int
    price: int
    target: Optional["Enemy"] = None
    ephemeral: bool = False
    rule: str = "exhaust"


@dataclass
class PlanEntry:
    """ONE Plan (QUARANTINED, `C.KOKOMI_OVERHAUL`, draft 6).

    THE TWIN OF `KokomiPlan.Entry`, and the unit everything downstream counts
    in: the pending badge, Change of Plans' "your front Plan", Nereid's
    Ascension's "carries out every Plan twice" and the
    whenever-a-Plan-is-carried-out payoffs (Treatise, Song of Pearls). War
    Council prints two clauses and is ONE Plan, which is what its face says.

      card_id  -- the card that wrote it. Kept for the LOG the way the C#
                  keeps `Source` for the strip, and for nothing else.
      clauses  -- the whole of what will happen: the row's own `plan:` list,
                  verbatim. NOT a closure and NOT a snapshot of the board.
      card     -- set for a `replay_exhausted` clause ONLY (Moon's
                  Reflection's chosen card), the one place a Plan holds an
                  object instead of a number. It is the instance that was
                  taken OUT of the exhaust pile, so the replay plays the card
                  the player chose rather than a fresh copy of its id.

    NO STORED ENEMY, deliberately, and it is the C#'s own reason: a Plan
    written last turn cannot hold a reference to an enemy that may be dead by
    the time it resolves, so the target is a RULE (`front_enemy` /
    `all_enemies`) resolved at carry-out.
    """
    card_id: str
    clauses: list[dict] = field(default_factory=list)
    card: Optional["Card"] = None

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
    # Set once at fight start from the built deck: does any card impose a
    # per-turn play cap (Normality)? Keeps combat.card_playable -- the
    # pilot's hot path -- from walking the hand on every check in the 100%
    # of fights where nothing does.
    hand_play_cap: bool = False
    log: list[dict] = field(default_factory=list)          # event stream for metrics
    # Formula / conditional context (reset per card play in resolve_card)
    detonations_total: int = 0            # The Big One formula
    reactions_this_card: int = 0          # reaction_triggered_by_this
    reactions_this_turn: int = 0          # reaction_triggered_this_turn
    # THE INAZUMA COMPANION OVERHAUL (QUARANTINED, C.COMPANION_OVERHAUL). The
    # SWIRLS this player turn, which is the count Heizou's Heartstopper Strike
    # prints ("deals 4 more for each Swirl this turn"). A second counter beside
    # `reactions_this_turn` rather than a filter over it, because that one is a
    # bare integer with no reaction names in it; written at the one site each
    # engine resolves a reaction, inside the arm's flag branch, and cleared
    # with the reaction window at the top of the player turn.
    mi_swirls_this_turn: int = 0
    encore_spend_draws_this_turn: int = 0  # encore_spend_draw once-per-turn
    #                                        latch (Curtain Call, R85)
    # INSTRUMENT ONLY (EB-78 (2); resources.note_charge_read writes it and
    # nothing reads it back). Charge-bank reads this turn, keyed by source --
    # "garment" / "kurage_pulse" / "bonus_formula" -- so the distribution can
    # be reported under either reading of the workshop's unsettled §6 scope
    # boundary. Reset at the top of the player turn, emitted at turn close.
    # It is NOT a budget: R188 ruled there is none, and no code path consults
    # this dict to decide whether a read may happen.
    charge_reads_this_turn: dict[str, int] = field(default_factory=dict)
                                          # (Chevreuse; reset per turn)
    kills_this_card: int = 0              # killed_target
    # Kills that the base game's Fatal gate would honor (Enemy
    # .counts_for_fatal). Separate from kills_this_card so the existing
    # killed_target predicate keeps its exact meaning for Klee/Furina.
    fatal_kills_this_card: int = 0        # killed_target_fatal (Feed)
    exhausted_this_card: int = 0          # generate_from_pool amount_formula
    # EB-118 -- the Exhaust IDENTITY context, as opposed to the COUNT beside
    # it. One printed descriptor per card the CURRENT exhaust_from took
    # (effects.exhaust_descriptor); the later effects of the SAME card read
    # derived totals off it. Two facts keep it from becoming a combat-global
    # `last_exhausted`, which is the shape this deliberately is not:
    # resolve_card opens an empty one per card play, and a second exhaust_from
    # REBINDS rather than appends. Never cleared in place -- combat's
    # free-play context saves the list OBJECT (see _FREE_PLAY_CONTEXT).
    exhaust_selection: list[dict] = field(default_factory=list)
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
    # CARDS THAT REACHED THE EXHAUST PILE THIS PLAYER TURN, counted AT THE
    # APPEND rather than at the AfterCardExhausted hook -- which is what makes
    # it a different number from `cards_exhausted_this_turn` above, and why it
    # is a second field rather than a reuse of that one.
    #
    # The hook counter is DEFERRED while a card is resolving: `exhaust_card`
    # returns early at `card_play_depth > 0` and the batch is swept by
    # `after_card_played` AFTER the card's own effects have run. And
    # `_op_exhaust_from` appends directly, so it never reaches that counter
    # mid-play by any route at all. A card that Exhausts something and then
    # reads the count -- Pearl Barrage's whole-turn prototype shape, R215 C --
    # would therefore not see the card it had just Exhausted.
    #
    # This one is incremented at both `player.exhaust_pile.append` sites, so
    # it answers "how many cards have gone to the pile this turn, INCLUDING
    # the one the resolving card just sent there". Nothing shipped reads it:
    # it exists for the quarantined `exhausts_this_turn` runtime count
    # (R213 B), and it is purely additive, so no shipped card's number moves.
    exhausts_this_turn: int = 0
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
    # EB-136 / R210 (C18): tier0's mirror of C#'s `CardPlay.Target`. That
    # property is `init`-only -- immutable once the play is constructed -- so
    # every `target: enemy` op of one card resolves against ONE creature, and
    # `CardCmd.AutoPlay` rolls the autoplay pick ONCE from `HittableEnemies`
    # BEFORE resolution rather than lazily at the first aimed op.
    # `effects.resolve_card` writes both fields at the top of a play and clears
    # them in its `finally`; `combat._FREE_PLAY_CONTEXT` saves and restores them
    # so a free play cannot leave its aim behind for the outer card.
    # `card_aim_bound` exists because `None` is a LEGAL bound value (an empty
    # board) and must not read as "no play in flight": the pilot calls
    # `_default_target` between plays and has to see live state, not the last
    # card's corpse.
    card_aim: Optional[Enemy] = None
    card_aim_bound: bool = False
    current_card_cost: int = 0            # this_cost_zero
    # THE MONDSTADT COMPANION OVERHAUL'S ELEMENT OVERRIDE (QUARANTINED,
    # C.COMPANION_OVERHAUL). Which element THIS Attack applies, when a rewritten
    # companion power has changed the answer -- "" while none has, which is
    # every board in every release build. Snapshotted once per play beside
    # `current_attack_bonus` and read by `_element_for`, for the reason that
    # bonus is snapshotted: the riders that set it are CONSUMED by the play, so
    # a per-hit re-read would apply the element to the first hit of a multi-hit
    # Attack and nothing else. Saved and restored across a free play with the
    # rest of the per-card context (`combat._FREE_PLAY_CONTEXT`).
    mc_attack_element_override: str = ""
    # THE INAZUMA COMPANION OVERHAUL (QUARANTINED, C.COMPANION_OVERHAUL). Damage
    # this CARD PLAY has actually put on enemy HP, which is what Gorou's Inuzaka
    # All-Round Defense reads: "Gain Block equal to half the damage dealt". A
    # per-play counter beside `block_gained_this_card` above and saved with it
    # across a free play, for the same reason -- an auto-play in the middle of
    # an outer card would otherwise leave its number behind for the outer card
    # to bank. Written only inside a flag branch (`deal_damage_to_enemy`).
    mi_damage_dealt_this_card: int = 0
    # THE MEND CEILING (QUARANTINED, C.COMPANION_OVERHAUL). The HP the player
    # walked into this fight with, which is the Kokomi brief's one rule for the
    # keyword and therefore the bound on Mizuki's Universal in ANYONE's hands.
    # Per COMBAT, so it lives here and not on Player, which survives the fight.
    # Zero means "not captured yet"; `effects.companion_overhaul_entry_hp` is
    # the one reader and captures on first ask.
    mi_entry_hp: int = 0
    current_x: int = 0                    # X-cost cards
    sparks_at_play: int = 0               # bank BEFORE this card's own spark
                                          # spend (Gleeful Barrage; R39)
    # Best Friends Forever's pool: the companions played this COMBAT, unique
    # by BASE id and in first-play order (`foo` and `foo+` are one entry --
    # BFF-dedupe, ruled 2026-08-06). combat._finish_play is the only writer
    # and owns that uniqueness; readers walk the list as-is.
    companions_played: list[str] = field(default_factory=list)
    # --- THE KURAGE'S MEMORY (QUARANTINED, C.KURAGE_MEMORY; the proposal at
    # review/ruled/kokomi-kurage-memory-2026-08-29.md). Every field below is
    # written ONLY inside a flag branch, so with the flag off they hold their
    # defaults for the life of every fight and nothing reads them.
    #
    # SCOPE IS PER FIGHT, and that is why the queue lives HERE rather than on
    # Player beside `charge`: `companions_played` two lines up is the same
    # scope for the same reason, and CombatState is rebuilt by `run_fight`, so
    # the memory empties when the fight ends with no reset line to forget.
    # (`Player.charge` needs its explicit rewind precisely because Player is
    # the object that survives the fight.)
    #
    # The queue holds KurageMemory RECORDS (above), not Card objects -- the
    # `_op_copy_companions_played` grammar, where an id is re-materialised
    # through the loader at use time, plus the three things v3 needs and v2
    # did not: the entering face's cost, the 3x price computed once, and the
    # stored target. The id still carries upgrade state (`foo` vs `foo+`).
    kurage_queue: list[KurageMemory] = field(default_factory=list)
    # The target each card SHE PLAYED was bound to, keyed by `id(card)` (the
    # `drawn_in_hand` idiom). Written at the bind in `effects.resolve_card`
    # and read once, at entry, so a card that enters the memory after a play
    # carries the body it hit. A card that never played is simply absent, and
    # absence is what the random fallback means.
    kurage_play_targets: dict = field(default_factory=dict)
    # The type ("attack"/"skill"/"power") of the last card KOKOMI HERSELF
    # played this turn -- the pulse's key. Cleared at turn start; the
    # jellyfish's own auto-play never writes it (recursion rule 2).
    kurage_last_card_type: str = ""
    # The enemy her own last attack was aimed at (PICK E1's "follows her
    # lead"). Survives the turn deliberately: under PICK B1 the fire happens
    # at turn START, so the only attack it can follow is last turn's.
    kurage_last_attack_target: Optional[Enemy] = None
    # True for exactly the duration of a jellyfish auto-play. BOTH recursion
    # rules read it: a replayed Companion does not re-enter the memory, and it
    # does not become "the last card Kokomi played".
    kurage_autoplaying: bool = False
    kurage_fired_this_turn: bool = False      # one card per turn, maximum
    # PICK E1's aim, handed to `bind_card_aim` for the duration of the
    # auto-play. None means "no override" -- E2 leaves it None on purpose and
    # lets the shipped forced-random roll stand.
    kurage_aim: Optional[Enemy] = None
    # QUARANTINED (C.KOKOMI_OVERHAUL, draft 6): THE PLAN QUEUE, front first.
    #
    # PER FIGHT, on `CombatState`, which is this engine's whole answer to the
    # C#'s "per player" (R205): tier 0 runs ONE seat, so a per-player table
    # would be a dictionary with one key. The property that matters -- one
    # seat's Plans are never another's -- holds by construction here, and the
    # per-FIGHT half is what `CombatState` being rebuilt by `run_fight` buys.
    kk_plan_queue: list[PlanEntry] = field(default_factory=list)
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
    # QUARANTINED (C.KOKOMI_OVERHAUL). Chain of Command's "each Companion card
    # you played LAST turn", and the twin of
    # `KokomiOverhaulLedger.CompanionsPlayedLastTurn`. Rolled from the counter
    # above at the ONE place that counter is cleared (`combat._player_turn`),
    # which is what keeps the card and the count from disagreeing about which
    # turn "last" was. A Plan written on turn N is carried out at the top of
    # N+1, AFTER that roll, so what it reads is turn N -- the turn the player
    # was looking at when they wrote it.
    companion_plays_last_turn: int = 0
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
    # --- EB-17, the card-flow instrument (Klee survival sprint plan §4;
    # missed-requirements §2.2). BOOKKEEPING ONLY, and the whole of it is
    # log-side: nothing in the engine, the pilot, an axis or the C# side reads
    # either dict, and no branch anywhere is gated on them. They exist so that
    # `draw` and `play` can carry the two facts a log reader cannot recover on
    # its own -- WHICH INSTANCE was drawn and WHEN -- because Card is a
    # dataclass and two copies of one card id compare equal, so a per-id tally
    # over the event stream cannot tell a card that sat in hand all fight from
    # a fresh copy of the same card played the turn it arrived.
    #
    #   drawn_in_hand    id(card) -> (card, turn drawn, is-first-copy), for
    #                    the instances CURRENTLY IN HAND BY A DRAW. The Card
    #                    itself is held in the tuple deliberately: a live
    #                    reference is what makes id() safe as a key, since an
    #                    object that cannot be collected cannot have its
    #                    address handed to a later card. Entries are dropped
    #                    when the instance leaves hand (played, or flushed --
    #                    combat.py owns both sites) and the map is rebuilt to
    #                    the retained hand at every turn flush, so a card that
    #                    leaves hand through an effects.py path (a discard op,
    #                    an exhaust op) is stale for at most one turn.
    #   first_copy_drawn card id -> the FIRST instance of that id to be drawn
    #                    this combat. Keyed by the instance and not by a
    #                    boolean so that the first copy stays the first copy
    #                    across a discard and a re-draw -- "did the forced
    #                    copy convert" is a question about the copy, not
    #                    about the turn it happened to arrive on.
    drawn_in_hand: dict[int, tuple] = field(default_factory=dict)
    first_copy_drawn: dict[str, "Card"] = field(default_factory=dict)
    # EB-256: the fight stopped because nothing was moving, not because
    # somebody won it. Written ONCE by `combat._run_rounds`' no-progress
    # detector, beside the `fight_stall` row it files, and read by
    # `tier05.model`, which takes the run's outcome kind off it. It is the
    # FIELD half deliberately: `fight_end` grew no key, so the log of a fight
    # that does not stall is byte-identical to what it was before this landed
    # and the two whole-log acceptance digests still hold.
    #
    # NOT a game-state field: `over` does not consult it, no effect reads it,
    # and a stalled fight leaves the loop through the same condition every
    # other fight leaves it through. See `combat.STALL_ROUNDS` for the
    # detector, and for why a stall is neither a win nor a loss.
    stalled: bool = False

    def emit(self, event: str, **data: Any) -> None:
        self.log.append({"turn": self.turn, "event": event, **data})

    def drawn_context(self, card: "Card") -> tuple[int, bool]:
        """EB-17: `(turn this instance was drawn, is-first-copy)` for a card
        sitting in hand, or `(-1, False)` when this instance did not reach
        hand by a draw (a token added to hand, a kit Burst, a status injected
        into hand, or a card auto-played out of a pile).

        Identity-checked against the stored Card, never by id() alone: -1 is
        "not drawn" and is never confused with turn 0."""
        entry = self.drawn_in_hand.get(id(card))
        if entry is None or entry[0] is not card:
            return -1, False
        return entry[1], entry[2]

    @property
    def living_enemies(self) -> list[Enemy]:
        return [e for e in self.enemies if e.alive]

    @property
    def over(self) -> bool:
        return not self.player.alive or not self.living_enemies

    # --- pile primitives ---

    def shuffle_discard_into_draw(self) -> None:
        self.rng.shuffle(self.player.discard_pile)
        merged = self.player.discard_pile + self.player.draw_pile
        # Perfect Fit (R82 reopened): "whenever this would be shuffled into
        # your Draw Pile, place it on the top instead." THIS IS THE ONLY SITE
        # (EB-85 divergence 5): `PerfectFit.ModifyShuffleOrder` opens with
        # `if (!isInitialShuffle && cards.Contains(base.Card))`, so the
        # combat-start shuffle is explicitly refused and combat.surface_innate
        # no longer rides the flag -- hoisting there made the enchantment a
        # free Innate. Order among top-placed cards stays shuffle-relative,
        # exactly as innate's does -- no hidden second sort.
        if any(c.enchant_top_of_draw for c in merged):
            merged = ([c for c in merged if c.enchant_top_of_draw]
                      + [c for c in merged if not c.enchant_top_of_draw])
        self.player.draw_pile = merged
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
            # EB-17. `setdefault(...) is card` is the whole first-copy rule:
            # the first instance of an id to be drawn claims the slot and
            # keeps it for the rest of the combat, so a copy that is drawn,
            # flushed and drawn again is still the same first copy.
            first_copy = self.first_copy_drawn.setdefault(card.id, card) is card
            self.drawn_in_hand[id(card)] = (card, self.turn, first_copy)
            # EscapePlan reads the TYPE of the card its own draw produced
            # (`(await Draw(1)).FirstOrDefault()`, then `.Type == Skill`).
            # Cleared at card start, so a card that drew NOTHING -- empty
            # piles, full hand -- reads as the source's null and pays out
            # nothing, rather than seeing whatever the last card drew.
            self.last_drawn_type = card.type
            # `first_copy` is EB-17's only addition to this row: an added key
            # on an event that already fired per card drawn, so the instrument
            # costs one dict entry and no new event.
            self.emit("draw", card=card.id, first_copy=first_copy)
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
