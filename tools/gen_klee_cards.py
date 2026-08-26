#!/usr/bin/env python3
"""
Emit C# card classes from canonical character YAML design sheets.

The historical filename remains the Klee-compatible entry point. Character
profiles now own sheet, output, namespace, element cadence, and identity;
tools/gen_roster_cards.py runs every profile. Each sheet remains the single
source of truth through implementation, per spec C2. The emitter owns only
mechanics backed by verified C# APIs and refuses to guess at anything else.

WHAT IT DELIBERATELY WILL NOT DO
--------------------------------
Any effect, card-level cost, condition, or lifecycle rule without an implemented
runtime is NOT emitted. A generator that emits a plausible-looking wrong body
is worse than one that emits nothing: the C# would compile, ship, and silently
misplay. Blocked cards are listed in the character manifest with the exact
semantic reason.

Every emitted file carries a DO-NOT-EDIT header naming this script and the
sheet, so a hand edit is visibly wrong rather than quietly lost on regen.

Usage:  python tools/gen_klee_cards.py [--check] [--character klee|furina|kokomi|all]
        python tools/gen_roster_cards.py [--check]
        --check exits nonzero if regenerating would change anything (CI guard).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

# Emitted-source newline. Kept as a name so generated C# templates never
# carry backslash escapes through this file's own string literals.
NEWLINE = chr(10)
NEWLINE_JOIN = NEWLINE

REPO = Path(__file__).resolve().parent.parent

# The repo's ONE effect-tree walk (L4). The generator is exempt from
# lint_effect_branch_scans' source half because its ~40 reads of the field are
# positional, but the reads that ask a whole-card question -- "does this card
# carry Bomb rules", "how many gain_encore sites are there" -- go through the
# shared walk like everyone else's.
sys.path.insert(0, str(REPO))
from tools.effect_walk import (SLY_AUTOPLAY_OP, iter_card_effects,  # noqa: E402
                               iter_effects, sly_autoplays, sly_riders)
# EB-118 sec.4.6. The generator prints the `skill_tag` contribution on the
# face, and it READS the number off tier0 rather than restating it: a printed
# 5 that could drift from the constant is the defect this line exists to
# remove, not one to introduce.
from tier0.constants import BURST_PER_SKILL_TAG                 # noqa: E402

SHEET = REPO / "docs" / "klee-cards.yaml"
# Mirrors tier0/content/upgrades.py UPGRADE_SHEETS, in the same order.
UPGRADE_SHEETS = (REPO / "docs" / "klee-upgrades.yaml",
                  REPO / "docs" / "furina-upgrades.yaml",
                  REPO / "docs" / "kokomi-upgrades.yaml")

# Companion sheets -> home nation. The nation is what the reward slot's
# SAME_NATION_REWARD_SHARE weighting keys on, and tier0's loader derives it
# from the sheet FILENAME (loader.py: `nation = sheet.split("-", 1)[0]`), so
# the mapping is stated once here rather than re-derived per card.
#
# Fontaine entered Klee's slot by user ruling (2026-07-21): "it's probably
# best to have some non-Mondstadt cards in the pool to make sure Klee doesn't
# inadvertently overperform with a 100% Mondstadt roster."
COMPANION_SHEETS = ((REPO / "docs" / "mondstadt-companions.yaml", "mondstadt"),
                    (REPO / "docs" / "fontaine-companions.yaml", "fontaine"),
                    (REPO / "docs" / "inazuma-companions.yaml", "inazuma"))
OUT_DIR = REPO / "klee-mod" / "KleeCode" / "Cards" / "Generated"
MANIFEST = REPO / "klee-mod" / "KleeCode" / "Cards" / "Generated" / "manifest.json"
FURINA_SHEET = REPO / "docs" / "furina-cards.yaml"
FURINA_OUT_DIR = (
    REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina" / "Generated"
)
FURINA_MANIFEST = FURINA_OUT_DIR / "manifest.json"
KOKOMI_SHEET = REPO / "docs" / "kokomi-cards.yaml"
KOKOMI_OUT_DIR = (
    REPO / "klee-mod" / "KleeCode" / "Cards" / "Kokomi" / "Generated"
)
KOKOMI_MANIFEST = KOKOMI_OUT_DIR / "manifest.json"


@dataclass(frozen=True)
class CharacterProfile:
    """Character-specific rules that the shared card emitter must not infer.

    The original generator predates the roster mod and baked Klee's sheet,
    namespace, Pyro cadence, and art helper directly into emitted classes.
    Keeping those choices in a profile makes adding a character an explicit
    data operation while leaving Klee's existing output stable.
    """

    character_id: str
    sheet: Path
    out_dir: Path
    manifest: Path
    namespace: str
    native_element: str
    cadence: str
    generator_script: str
    art_loader: str
    emit_character_identity: bool = False

    def damage_applies_element(self, card: dict) -> bool:
        """Whether this character card's damaging effects carry its element."""
        if self.cadence == "catalyst_attack":
            return card.get("type") == "attack"
        if self.cadence == "skill_grade":
            tags = set(card.get("tags", []))
            has_damage = any(
                effect.get("op") == "damage"
                and effect.get("target") != "self"
                for effect in card.get("effects", [])
            )
            return has_damage and (
                card.get("type") == "skill"
                or "skill_tag" in tags
                or "burst_tag" in tags
            )
        raise ValueError(
            f"{self.character_id}: unknown elemental cadence {self.cadence!r}"
        )


KLEE_PROFILE = CharacterProfile(
    character_id="klee",
    sheet=SHEET,
    out_dir=OUT_DIR,
    manifest=MANIFEST,
    namespace="KleeMod.Cards.Generated",
    native_element="pyro",
    cadence="catalyst_attack",
    generator_script="tools/gen_klee_cards.py",
    art_loader="KleeArt",
)

FURINA_PROFILE = CharacterProfile(
    character_id="furina",
    sheet=FURINA_SHEET,
    out_dir=FURINA_OUT_DIR,
    manifest=FURINA_MANIFEST,
    namespace="KleeMod.Cards.Furina.Generated",
    native_element="hydro",
    cadence="skill_grade",
    generator_script="tools/gen_roster_cards.py",
    art_loader="RosterArt",
    emit_character_identity=True,
)

KOKOMI_PROFILE = CharacterProfile(
    character_id="kokomi",
    sheet=KOKOMI_SHEET,
    out_dir=KOKOMI_OUT_DIR,
    manifest=KOKOMI_MANIFEST,
    namespace="KleeMod.Cards.Kokomi.Generated",
    native_element="hydro",
    # CATALYST, ruled R52 ask N1: every attack of hers applies Hydro. That is
    # the structural third of her elite A6 -- application uptime comes from
    # the cadence, not from authored lines -- so it must be the profile's
    # business and not something each card re-declares.
    cadence="catalyst_attack",
    generator_script="tools/gen_roster_cards.py",
    art_loader="RosterArt",
    emit_character_identity=True,
)

PROFILES = {
    KLEE_PROFILE.character_id: KLEE_PROFILE,
    FURINA_PROFILE.character_id: FURINA_PROFILE,
    KOKOMI_PROFILE.character_id: KOKOMI_PROFILE,
}

# Ops this generator can express with verified Cmd APIs. Anything else blocks
# the card. Keep this set honest -- widening it without a verified call site is
# how we ship silently-wrong cards.
#
# gain_spark landed with the Sparks system (C3 gap-list unlock #1): the call
# site is SparkPower.Gain -> PowerCmd.Apply, the same verified idiom
# BombPower.Place uses. The amount is a LITERAL unless klee-upgrades.yaml
# carries a `spark: +N` delta for the card (M9 ruling 2026-07-20, moved off
# the inline `upgrade:` key by R20); then it
# becomes a named DynamicVar("Sparks", n). That name is not an invented
# placeholder (finding 15's lesson): the base class ctor is
# DynamicVar(string, decimal), DynamicVarSet has a public string indexer,
# and the base game itself ships name-only vars (DynamicVar("Times", ...)
# in CardModel's hover tips) -- all verified in the sts2 decompile.
#
# burst_energy landed with the Burst-energy spike (standing plan item 2): the
# call site is KleeBurstResource.Gain -> CustomResources<T> + PowerCmd, the
# same verified shape SparkPower.Gain uses. Amount is a LITERAL unless
# klee-upgrades.yaml carries a `burst_energy: +N` delta; then it becomes a
# named DynamicVar("BurstEnergy", n) -- the Sparks idiom exactly.
# discard + discard_for_sparks (R36 batch): random discard is
# CardCmd.Discard on a random pick from the kit-exempt pool; chosen discard
# is CardSelectCmd.FromHandForDiscard (the MockDiscardAndAddShivsPotion
# idiom -- forced pick of N, auto-selects-all on a short hand) with the
# SAME kit-exempt filter. KitGrant.NotKitCard is the exemption both ride
# (v1.9 invariant: the Burst is never fodder -- the obligation DECISIONS
# recorded when the kit sprint landed).
# Bomb-manipulation ops (standing-plan batch, 2026-07-20): detonate rides
# BombPower.DetonateOn/DetonateAll (returns the count -- Chained Reactions
# prices its re-bomb per detonation caused by the play, the sim's counter
# diff); modify_bombs rides BombPower.ModifyAll (round stamps mirror
# tier0's Bomb.turn_placed); move_bombs rides BombPower.MoveAllTo (charges
# keep their stamps, +bonus each). chance_bomb_per_detonation rolls
# Rng.CombatTargets.NextFloat() < chance (verified decompile; CombatTargets
# is the established in-combat pick stream).
# spend_spark (EB-118 §4.5) is the Spark SINK: the call site is
# SparkPower.Spend -> PowerCmd.ModifyAmount, the same verified idiom the
# threshold consume already uses, and the price is a LITERAL (no upgrade
# delta reaches it -- a card that pays less on upgrade is a repricing, and
# repricing is [USER]'s call, not codegen's). The cost LINE is emitted
# separately as an IsPlayable override; see `spark_gate_member` in emit().
MECHANICAL_OPS = {"damage", "block", "draw", "place_bomb", "gain_spark",
                  "spend_spark", "burst_energy",
                  "gain_encore", "spend_encore", "raise_fanfare_cap",
                  "gain_fanfare_floor",
                  # Fanfare rework (2026-07-28): the Hyperbeam settle
                  # (Track C.2) and the on-demand bow probe (Track D).
                  "crash_fanfare", "salon_bow",
                  # EB-118 §5.5 (staged): the queue verbs. Both are a
                  # single call into SalonMemberPower, the salon_bow
                  # shape, so they carry no locals and no new grammar.
                  "salon_rotate", "salon_perform",
                  "generate_guest_star",
                  "copy_spotlighted_in_hand",
                  "heal",
                  "apply_power", "discard", "discard_for_sparks",
                  "detonate", "move_bombs", "modify_bombs",
                  "chance_bomb_per_detonation", "conditional",
                  "energy", "scry_discard", "add_card", "exhaust_from",
                  "apply_aura", "swirl", "buff_next_attack", "block_next_turn",
                  "cost_mod", "copy_companion_in_hand",
                  # Curtain Call consolidation ("Take a Bow"): grow_damage is
                  # Rampage's permanent per-instance growth (BaseValue raised
                  # on the card's own var, the SyncDisplay idiom);
                  # refresh_all_auras reuses AuraPower's same-element refresh
                  # so the duration it refreshes TO has one definition.
                  "grow_damage", "refresh_all_auras",
                  # Kokomi (playtest sprint, Track B). gain_charge rides
                  # KokomiResources.GainCharge; summon_kurage rides
                  # KurageSummon.Field (refresh-never-stack); conscript rides
                  # KokomiConscript.Run. All three have verified call sites in
                  # klee-mod/KleeCode/Powers -- the whitelist stays honest.
                  "gain_charge", "summon_kurage", "conscript",
                  # EB-122 (EB-69's fill): the turn-scoped Sly grant. Rides
                  # SlyGrant.Grant, whose whole shape is Hand Trick's --
                  # CardSelectCmd.FromHand filtered to non-Sly Skills, then
                  # the game's own CardCmd.ApplySingleTurnSly, which the game
                  # itself clears at turn end. No mod-side timer exists,
                  # because inventing one is what would have made this a
                  # different mechanic wearing the same name.
                  "grant_sly_this_turn",
                  # recall_to_draw, BOTH sources. The exhaust source arrived
                  # with EB-118 and rides RecallFromExhaust.Recall; the discard
                  # source (Headbutt's shape) arrived with EB-122 and rides
                  # RecallFromDiscard.Recall. One verified call site each in
                  # klee-mod/KleeCode/Powers. (This note said the discard
                  # source was "NOT built and blocks by name below" until
                  # EB-125 caught it: the block was lifted at EB-122 and the
                  # comment was not, so it described a wall that had gone.)
                  "recall_to_draw",
                  "replay_next_companion", "copy_companions_played_this_combat",
                  # EB-118 sec.5.4: the modal surface. choose_one rides
                  # KleeMod.Cards.ModalChoice, a thin wrapper over the base
                  # game's OWN card-level choice
                  # (CardSelectCmd.FromChooseACardScreen + PlayerChoiceContext,
                  # co-op-synced as PlayerChoiceType.Index). Inert on every
                  # committed sheet -- no row is modal today.
                  "choose_one"}

# recall_to_draw (EB-118). `position` is accepted only as its default: the
# destination is top-of-draw in both engines and there is no other placement.
RECALL_FIELDS = {"op", "from", "position", "amount"}

# --- companion batch (2026-07-21) --------------------------------------------
def is_companion(card: dict) -> bool:
    """Companion sheet rows carry `star` (4/5); Klee's sheet never does."""
    return "star" in card


ELEMENT_CS = {"pyro": "Element.Pyro", "hydro": "Element.Hydro",
              "electro": "Element.Electro", "cryo": "Element.Cryo",
              "anemo": "Element.Anemo", "geo": "Element.Geo"}

APPLY_AURA_FIELDS = {"op", "element", "target"}
SWIRL_FIELDS = {"op", "target"}
BUFF_NEXT_FIELDS = {"op", "amount"}

# Charlotte, First-Person Shutter (tier0 _op_block_next_turn).
BLOCK_NEXT_TURN_FIELDS = {"op", "amount"}

# --- small ops (2026-07-20 batch) --------------------------------------------
# add_card token registry: sheet card id -> hand-written C# class. A pool
# reference resolves against the SHEET at generation time instead (the
# archetype/rarity data lives only there), and every resolved member must
# itself be a generated class -- both enforced in blocked_reason.
ADD_CARD_CLASSES = {"confiscated": "Confiscated"}
# add_card's own field totality. EB-90: `sly` used to sit at the head of this
# set under CARD_FIELDS' comment about it, copied whole from there. `sly` is a
# CARD-level key -- the discard branch of a card -- and no sheet has ever put
# it on an add_card EFFECT, so it excused nothing and only made the set read
# as though a rider spelling existed. Dropped; CARD_FIELDS still owns it.
#
# Two spellings of the same two fields are live and both are kept: Klee's
# sheet writes `card` / `zone`, tier0's silent sheet writes `card_id` / `to`,
# and the reader below accepts either (`eff.get("zone") or eff.get("to", ...)`,
# `eff.get("card_id") or eff.get("card")`).
ADD_CARD_FIELDS = {
    "op",
    "card", "card_id",       # the token, by id -- one or the other
    "pool",                  # ... or a sheet pool, resolved at generation
    "zone", "to",            # hand | discard -- one or the other
    "amount",
    "cost_override",
}
GUEST_STAR_FIELDS = {"op", "rarity", "amount", "to", "cost_override"}
ENERGY_FIELDS = {"op", "amount"}
SCRY_FIELDS = {"op", "amount"}
# exhaust_from: dodge_roll's shape only -- a random Status from hand. The
# filterless form (kit-exempt any-card) blocks until a card needs it.
EXHAUST_FROM_FIELDS = {"op", "zone", "filter", "amount",
                       # Kokomi (playtest sprint): `select: chosen` is the
                       # PLAYER picking the victims, not the rng. Her whole
                       # engine is "choose what to rotate out", so a random
                       # pick would not be a smaller version of the card --
                       # it would be a different card.
                       "select"}

# --- conditional op (2026-07-20 batch) ---------------------------------------
# Predicates with a verified C# read, each mirroring tier0 effects.py
# _predicate exactly:
#   this_cost_zero  -> EnergyCost.GetResolved(): "current cost including all
#                      modifiers clamped to 0" (decompile doc) -- the spark
#                      zeroing rides Hook.ModifyEnergyCostInCombat, so a
#                      spark-freed attack reads 0 here, same as the sim's
#                      current_card_cost.
#   has_spark       -> SparkPower.Amount is the bank.
#   reaction_triggered_by_this / killed_target -> snapshot diffs captured at
#                      the top of OnPlay (the sim resets its per-card
#                      counters at resolve_card start).
PREDICATES_CS = {
    "this_cost_zero": "EnergyCost.GetResolved() == 0",
    # SparksAsResolved, NOT the raw Amount: the sim spends the spark charge
    # BEFORE effects resolve; the C# consume executes after (Snap fix), so
    # mid-play reads subtract the pending spend.
    "has_spark": "SparkPower.SparksAsResolved(Owner.Creature) > 0",
    "reaction_triggered_by_this": "ReactionEffects.TotalResolved > reactionsAtStart",
    # tier0: state.reactions_this_turn > 0, a window opened at the top of the
    # player turn BEFORE start-of-turn detonation. ReactionEffects keeps the
    # window as a snapshot of the same monotonic counter.
    "reaction_triggered_this_turn": "ReactionEffects.ReactionTriggeredThisTurn",
    "killed_target": "enemiesAtStart.Any(e => e.IsDead)",
    # fanfare_at_least_N is PARAMETRIC (see predicate_cs / predicate_text):
    # the bar is authored per card and moves at red-pen, so a literal map
    # turned every new threshold into a codegen KeyError.
    "has_salon_members": "SalonMemberPower.Count(Owner.Creature) > 0",
    "spotlight_moved_this_turn":
        "SpotlightSystem.MovedThisTurn(Owner.Creature)",
    # Curtain Call ("Take a Bow"). Both read through CurtainCallHooks rather
    # than inline, so the mirror of each sim predicate lives next to its
    # tracker and the divergence risk is one file, not every card that reads
    # it. enemy_intends_attack drops the sim's `sleep_turns == 0` clause on
    # purpose: nothing in the game SETS sleep, and a sleeping enemy
    # telegraphs SleepIntent rather than AttackIntent, so it fails the intent
    # test on its own (the helper checks IsStunned too).
    "enemy_intends_attack":
        "CurtainCallHooks.EnemyIntendsAttack(Owner.Creature)",
    "hp_lost_this_turn":
        "CurtainCallHooks.HpLostThisTurn(Owner.Creature)",
}

# The if-clause each predicate renders on the card.
PREDICATE_TEXT = {
    "this_cost_zero": "If this cost 0",
    "has_spark": "If you have [gold]Spark[/gold]",
    "reaction_triggered_by_this": "If it triggered an [gold]Elemental Reaction[/gold]",
    "reaction_triggered_this_turn": "If an [gold]Elemental Reaction[/gold] triggered this turn",
    "killed_target": "If it kills",
    "has_salon_members": "If you have a [gold]Salon Member[/gold]",
    "spotlight_moved_this_turn":
        "If you moved the [gold]Spotlight[/gold] this turn",
    "enemy_intends_attack": "If an enemy intends to attack",
    "hp_lost_this_turn": "If you have lost HP this turn",
}

_FANFARE_BAR = re.compile(r"^fanfare_at_least_(\d+)$")
# Same parametric treatment, same reason (see predicate_cs): these bars are
# balance numbers authored per card, so they must be a card edit and never a
# codegen table edit. Kokomi's two banks are the exhaust pile (a count the
# engine already keeps) and Charge.
_CHARGE_BAR = re.compile(r"^charge_at_least_(\d+)$")
_EXHAUST_PILE_BAR = re.compile(r"^exhaust_pile_at_least_(\d+)$")
# Curtain Call: Encore is a HELD buffer, so a threshold on it is the same
# shape as Fanfare's and gets the same parametric treatment for the same
# reason -- moving the bar must be a card edit, never a codegen edit.
_ENCORE_BAR = re.compile(r"^encore_at_least_(\d+)$")
# EB-118 §5.5: WHO is next to perform. Parametric like the bars above, but on
# a CLOSED argument -- the member table, which both engines share -- so an
# unknown name blocks the card instead of generating a branch that can never
# fire. The display names are the faces' own: "the Usher" carries its article.
_LEFTMOST_MEMBER = re.compile(r"^leftmost_salon_member_([a-z]+)$")


def predicate_cs(name: str) -> str | None:
    """C# expression for a sheet predicate, or None if unsupported.

    `fanfare_at_least_N` is generated rather than tabled: the bar is a
    balance number authored per card and moved at red-pen, so tabling it
    made every new threshold a codegen KeyError instead of a card edit.
    """
    name = name or ""
    hit = _FANFARE_BAR.match(name)
    if hit:
        return f"FurinaResources.ReadableFanfare(Owner.Creature) >= {hit.group(1)}"
    hit = _CHARGE_BAR.match(name)
    if hit:
        return f"KokomiResources.GetCharge(Owner.Creature) >= {hit.group(1)}"
    hit = _EXHAUST_PILE_BAR.match(name)
    if hit:
        return (f"KokomiResources.ExhaustPileCount(Owner.Creature) "
                f">= {hit.group(1)}")
    hit = _ENCORE_BAR.match(name)
    if hit:
        return f"FurinaResources.Encore(Owner.Creature) >= {hit.group(1)}"
    hit = _LEFTMOST_MEMBER.match(name)
    # SALON_MEMBER_CS is the one member->enum map, shared with `member:` on
    # the deploy op: a predicate must not grow a second spelling of the same
    # three identities. `random` is not an identity and is excluded -- "if a
    # random member is next" is not a question about the stage.
    member = SALON_MEMBER_CS.get(hit.group(1)) if hit else None
    if member and member != "null":
        return ("SalonMemberPower.LeftmostMember(Owner.Creature) == "
                f"{member}")
    return PREDICATES_CS.get(name)


def predicate_text(name: str) -> str | None:
    """The if-clause the predicate renders on the card face."""
    name = name or ""
    hit = _FANFARE_BAR.match(name)
    if hit:
        return f"If you have at least {hit.group(1)} [gold]Fanfare[/gold]"
    hit = _CHARGE_BAR.match(name)
    if hit:
        return f"If you have at least {hit.group(1)} [gold]Charge[/gold]"
    hit = _EXHAUST_PILE_BAR.match(name)
    if hit:
        return (f"If {hit.group(1)} or more cards are "
                "[gold]Exhausted[/gold]")
    hit = _ENCORE_BAR.match(name)
    if hit:
        # [gold] like its Fanfare/Charge siblings above -- swelling_overture
        # shipped the only un-golded resource keyword on a face (SYS-9).
        return f"If you have at least {hit.group(1)} [gold]Encore[/gold]"
    hit = _LEFTMOST_MEMBER.match(name)
    if hit and SALON_MEMBER_CS.get(hit.group(1), "null") != "null":
        # "next to perform", not "leftmost": the queue's LEFT is a fact about
        # the stage's layout, and what the player is being told is the order
        # of play. The stage names are B5's, so the face and the tooltip that
        # explains the member are titled the same thing.
        return f"If {SALON_MEMBER_NAMES[hit.group(1)]} is next to perform"
    return PREDICATE_TEXT.get(name)


CONDITIONAL_FIELDS = {"op", "if", "then", "else"}

# Ops legal inside a conditional branch: plain resolvers with literal (or
# delta-var) amounts and no local declarations outside their own braces.
# repeat_this is legal ONLY as a conditional's entire then-branch.
BRANCH_OPS = {"damage", "block", "draw", "gain_spark", "gain_encore",
              # EB-119: the OVERDRAW primitive belongs beside its own gain.
              # The modal contract's second mode IS a spend
              # (tier0/tests/test_eb118_modal.py), and without this entry the
              # generator could not emit the contract's own example -- which
              # is how `{op: gain_encore, amount: -2}` came to stand in for it
              # in a fixture. That substitution is a no-op in C#
              # (FurinaResources.GainEncore returns on `amount <= 0`) while
              # the sim moves the meter, so it is now refused outright below.
              "spend_encore",
              "place_bomb", "burst_energy", "energy",
              "buff_next_attack",
              # EB-125: `apply_power` on YOURSELF, and only on yourself. The
              # self arm of the top-level emitter is already a single
              # PowerCmd.Apply with no locals -- the same shape as
              # buff_next_attack's branch resolver above -- so it meets the
              # branch-legality criterion as written. The ENEMY arms do not
              # and stay blocked BY NAME in _branch_op_reason: `enemy` needs
              # the target guard, `random_enemy` and `all_enemies` declare
              # locals inside their own blocks, and emitting them a second,
              # subtly different way here is exactly the drift this table
              # exists to prevent. Sim twin: effects._op_apply_power reached
              # through a conditional; tighten_the_cords is the first row to
              # print it (EB-125 / R202).
              "apply_power",
              # EB-118 §5.5: single calls with no locals, which is the whole
              # branch-legality criterion. The obvious future row is
              # "if the leftmost member is X, do Y" -- see the
              # leftmost_salon_member_ predicate below.
              "salon_rotate", "salon_perform"}

# The exact key set each branch op may carry. Module-level because a modal's
# mode body is emitted through the same `_emit_branch_op` resolvers as a
# conditional branch, so it has to be validated by the same rule -- two copies
# of this table is exactly how a mode body would drift from a branch body.
BRANCH_FIELDS = {
    "damage": {"op", "amount", "target"},
    "block": {"op", "amount"},
    "draw": {"op", "amount"},
    "gain_spark": {"op", "amount"},
    "gain_encore": {"op", "amount"},
    "spend_encore": {"op", "amount"},
    "burst_energy": {"op", "amount"},
    "energy": {"op", "amount"},
    "place_bomb": {"op", "amount", "target", "bomb_damage"},
    "buff_next_attack": {"op", "amount"},
    # EB-125. Deliberately NARROWER than APPLY_POWER_FIELDS: `max_stacks`,
    # `splash_procs_per_turn` and the rest all steer machinery the branch
    # resolver does not emit, so a row carrying one blocks by name instead of
    # silently losing it.
    "apply_power": {"op", "power", "amount", "target"},
}

# EB-118 sec.5.4, codegen leg. Mirrors tier0.engine.effects.MODAL_FIELDS /
# MODE_FIELDS; tier0/tests/test_eb118_modal_parity.py pins the two together.
MODAL_FIELDS = {"op", "modes"}
MODE_FIELDS = {"label", "effects"}


def _branch_op_reason(eff: dict, where: str) -> str | None:
    """Why this effect cannot be emitted inside a branch or a mode body."""
    if eff.get("op") not in BRANCH_OPS:
        return f"op '{eff.get('op')}' inside a {where}"
    unknown = set(eff) - BRANCH_FIELDS[eff["op"]]
    if unknown:
        return (f"branch {eff['op']} field(s) {sorted(unknown)} "
                "not understood")
    if (eff.get("op") == "damage"
            and (eff.get("target") not in DAMAGE_TARGETS
                 or eff.get("target") == "self")):
        return f"branch damage target '{eff.get('target')}'"
    if (eff.get("op") == "place_bomb"
            and eff.get("target") not in BOMB_TARGETS):
        return f"branch place_bomb target '{eff.get('target')}'"
    if eff.get("op") == "apply_power":
        # EB-125. Self only -- see the BRANCH_OPS note. `salon_member` is a
        # typed DEPLOY that also carries the salonReplacements counter, so it
        # is not the plain Apply this resolver emits even though its target
        # reads self.
        if eff.get("power") not in APPLY_POWERS:
            return f"branch apply_power power '{eff.get('power')}'"
        if eff.get("power") == "salon_member":
            return "branch apply_power power 'salon_member' (typed deploy)"
        if eff.get("target") != "self":
            return f"branch apply_power target '{eff.get('target')}'"
    if not isinstance(eff.get("amount", eff.get("bomb_damage")), int):
        return f"branch {eff['op']} amount must be a literal int"
    if eff["op"] in ("gain_encore", "spend_encore") and eff["amount"] <= 0:
        # EB-119, the same bar the top-level meter ops carry in
        # blocked_reason. A negative GAIN is the shape a spend was smuggled
        # in as, and it is not one: it does nothing at all in C#.
        return f"branch {eff['op']} amount must be a positive literal int"
    return None


# The base game's choose-a-card screen refuses more than three options
# (`CardSelectCmd.FromChooseACardScreen`: `if (cards.Count > 3) throw`, read
# off sts2.dll v0.107.1). That is the ceiling on modes, and it belongs here
# rather than in a comment on the sheet -- a four-mode row must BLOCK, not
# ship and throw in front of a player.
MAX_MODES = 3


def _mode_target_type(mode: dict) -> str | None:
    """The C# TargetType a mode body implies, or None for self-only."""
    for eff in mode.get("effects", []):
        if eff.get("op") == "damage" and eff.get("target") != "self":
            return TARGET_CS[eff["target"]]
        if eff.get("op") == "place_bomb":
            return TARGET_CS[eff["target"]]
    return None


def _modal_reason(eff: dict) -> str | None:
    """Why this `choose_one` cannot be emitted. EB-118 sec.5.4.

    The mode bodies go through the SAME resolvers a conditional branch does,
    so they carry the same restriction; what is extra here is the screen's
    three-option ceiling and the target agreement below.
    """
    unknown = set(eff) - MODAL_FIELDS
    if unknown:
        return f"choose_one field(s) {sorted(unknown)} not understood"
    modes = eff.get("modes")
    if not isinstance(modes, list) or len(modes) < 2:
        return "choose_one needs at least 2 modes"
    if len(modes) > MAX_MODES:
        return (f"choose_one with {len(modes)} modes "
                f"(the choose-a-card screen takes at most {MAX_MODES})")
    for mode in modes:
        if not isinstance(mode, dict):
            return "choose_one mode is not a mapping"
        unknown = set(mode) - MODE_FIELDS
        if unknown:
            return f"mode field(s) {sorted(unknown)} not understood"
        if not isinstance(mode.get("label"), str) or not mode["label"]:
            return "mode needs a non-empty label"
        if not isinstance(mode.get("effects"), list) or not mode["effects"]:
            return "mode needs a non-empty effects list"
        for e in mode["effects"]:
            reason = _branch_op_reason(e, "mode body")
            if reason:
                return reason
    # TargetType is a property of the CARD, declared before a mode is picked,
    # so modes that would aim differently are inexpressible -- the player would
    # have aimed the card before choosing what it does.
    targets = {_mode_target_type(mode) for mode in modes}
    targets.discard(None)
    if len(targets) > 1:
        return (f"choose_one modes disagree on TargetType {sorted(targets)} "
                "(the card is aimed before the mode is chosen)")
    return None

# Cards carrying a repeat-conditional re-resolve their other effects (sim
# resolve_card: the repeat excludes only the repeat machinery). The repeated
# body lands inside a for-block, so those other effects must not declare
# method-scope locals a second time -- restrict them to declaration-free ops.
REPEAT_SAFE_OPS = {"damage", "block", "draw", "gain_spark", "burst_energy"}

# The same restriction for a repeat an UPGRADE appends (`add: {op:
# repeat_this}`, R130's take_your_bow+). Superset of REPEAT_SAFE_OPS by
# exactly `salon_bow`, which is a single awaited call with no locals -- the
# only op the new grammar has a card for. Anything else blocks the upgrade
# path loudly rather than emitting an unverified replay.
UPGRADE_REPEAT_OPS = REPEAT_SAFE_OPS | {"salon_bow", "salon_rotate",
                                        "salon_perform"}

# Field whitelists for the bomb ops (UNPARSEABLE discipline: an unknown
# field encodes a mechanic; block loudly, never approximate).
DETONATE_FIELDS = {"op", "target", "bonus"}
MOVE_BOMBS_FIELDS = {"op", "target", "bonus"}
MODIFY_BOMBS_FIELDS = {"op", "scope", "bonus"}
CHANCE_BOMB_FIELDS = {"op", "chance", "bomb_damage"}

# apply_power (power-card pass): sheet power id -> (C# PowerModel class,
# stack cap or None, card-text template with {X} for the amount). Stackable
# powers normally use None, matching native Slay the Spire power stacking;
# a numeric cap is reserved for an explicitly designed exception and is
# cross-checked against the sheet below.
#
# sparks_n_splash is deliberately ABSENT: the Burst kit card lands LAST in
# the power-card pass (standing plan) with its own cost/grant machinery.
APPLY_POWERS = {
    "bomb_damage_up": ("BombDamageUpPower", None,
        "Your [gold]Bombs[/gold] detonate for {X} more damage."),
    # EB-118 sec.4.4. Explosives Workshop's install. `bomb_damage_up` above is
    # what this PAYS INTO and it stays exactly where it is, because a Bomb
    # armed before a trigger and one armed after must detonate at the same
    # number -- which is only true while there is one bomb-damage stat.
    "bomb_damage_per_rotation": ("ExplosivesWorkshopPower", None,
        "The first time each turn you discard or Exhaust a card, your "
        "[gold]Bombs[/gold] deal {X} more damage this combat."),
    "zero_cost_attacks_up": ("ZeroCostAttacksUpPower", None,
        "Your Attacks that cost 0 deal {X} more damage."),
    "spark_per_turn": ("SparkPerTurnPower", None,
        "At the start of your turn, gain {X} [gold]Spark[/gold]."),
    "reaction_bonus_spark_energy": ("ReactionBonusSparkEnergyPower", None,
        "[gold]Elemental Reactions[/gold] grant {X} extra [gold]Spark[/gold] "
        "and 5 extra [gold]Burst Energy[/gold]."),
    "detonation_splash": ("DetonationSplashPower", None,
        "When a [gold]Bomb[/gold] detonates: deal {X} damage to ALL enemies, "
        "ignoring Block, and gain 3 [gold]Burst Energy[/gold]. "
        "Up to 3 times per turn."),
    "detonation_vuln": ("DetonationVulnPower", None,
        "When a [gold]Bomb[/gold] detonates, apply {X} [gold]Vulnerable[/gold] "
        "to that enemy."),
    "spark_threshold_down": ("SparkThresholdDownPower", None,
        "You need {X} fewer [gold]Spark[/gold] for your Attacks to cost 0."),
    "amp_reaction_up": ("AmpReactionUpPower", None,
        "[gold]Vaporize[/gold] and [gold]Melt[/gold] amplify {X}% more."),
    "bomb_and_spark_per_turn": ("BombAndSparkPerTurnPower", None,
        "At the start of your turn, place a 5-damage [gold]Bomb[/gold] on a "
        "random enemy and gain {X} [gold]Spark[/gold]."),
    # Native debuffs (weak/vulnerable batch, 2026-07-20). Semantics verified
    # against the decompiled core: WeakPower x0.75 dealt / VulnerablePower
    # x1.5 taken, Counter stacks, tick at enemy side turn end -- exactly
    # tier0's WEAK_DEALT_MULT / VULNERABLE_TAKEN_MULT and DECAYING rule.
    # No cap either side. {TO} renders the target clause (build_description).
    # Kokomi (playtest sprint, Track B). kurage_ward is ours
    # (Powers/KuragePowers.cs); the other two are the BASE GAME's own
    # Ironclad powers, reused rather than reimplemented -- her sheet asked
    # for exactly their semantics and a private copy would be a second
    # implementation of a rule the engine already owns.
    "metallicize": ("MetallicizePower", None,
        "At the start of your turn, gain {X} Block."),
    # Cap 6 mirrors the sheet's `max_stacks: 6` -- a single-application ward,
    # not a stacking one. Vigil's upgrade moves amount AND cap together
    # (test_vigil_upgrade_moves_the_cap_with_the_amount pins that), so the
    # registry cap has to move with them or the upgrade is silently swallowed.
    "prevent_exhaust_ward": ("PreventExhaustWardPower", 6,
        "The first time you would take unblocked attack damage each turn, "
        "prevent up to {X} of it and [gold]Exhaust[/gold] a random card from "
        "your draw pile."),
    "kurage_ward": ("KurageWardPower", None,
        "Each [gold]Bake-Kurage[/gold] pulse also grants {X} Block."),
    # R73/G2. No cap: the stacking is the ruling, not an oversight, and a cap
    # here would implement the ban [USER] considered and rejected.
    "kurage_amp": ("KurageAmpPower", None,
        "Each [gold]Bake-Kurage[/gold] pulse reads your [gold]Charge[/gold] "
        "for {X} more damage per point."),
    "feel_no_pain": ("FeelNoPainPower", None,
        "Whenever a card is [gold]Exhausted[/gold], gain {X} Block."),
    "dark_embrace": ("DarkEmbracePower", None,
        "Whenever a card is [gold]Exhausted[/gold], draw {X} card{XS}."),
    "weak": ("WeakPower", None,
        "Apply {X} [gold]Weak[/gold]{TO}."),
    "vulnerable": ("VulnerablePower", None,
        "Apply {X} [gold]Vulnerable[/gold]{TO}."),
    # Companion powers (2026-07-21, CompanionPowers.cs): each mirrors a
    # tier0 player_turn_start/end trigger or attack-bonus branch. No caps
    # (the sim clamps none of these).
    "oz_summon": ("OzSummonPower", None,
        "Summon Oz for {X} turns: at the end of your turn, he deals 3 damage "
        "and applies [gold]Electro[/gold] to a random enemy."),
    "witchs_flame": ("WitchsFlamePower", None,
        "At the end of your turn, consume [gold]Pyro[/gold] from each enemy. "
        "For each aura consumed, deal {X} damage and gain 3 "
        "[gold]Burst Energy[/gold]."),
    # Redesigned 2026-07-26 (red-pen item 4): a per-turn Strength ratchet plus
    # the same per-turn Block, replacing a static flat attack bonus.
    "celestial_gift": ("CelestialGiftPower", None,
        "At the start of your turn, gain {X} [gold]Strength[/gold] and 4 "
        "[gold]Block[/gold]."),
    "solar_isotoma": ("SolarIsotomaPower", None,
        "For {X} turns: your Attacks against enemies holding an elemental "
        "aura grant 3 [gold]Block[/gold] per hit."),
    "attack_up_this_turn": ("AttackUpThisTurnPower", None,
        "Your Attacks deal {X} more damage this turn."),
    "strength": ("StrengthPower", None,
        "Gain {X} [gold]Strength[/gold]."),
    # Fontaine (2026-07-21 ruling). shatter_bonus is a flat rider the sim adds
    # inside the Shatter's raw HP subtraction, so FrozenPower reads it there.
    "shatter_bonus": ("ShatterBonusPower", None,
        "Your [gold]Shatters[/gold] deal {X} more damage."),
    # Fontaine 5-star Rares (R64, 2026-07-25). Amounts live on the cards, so
    # none of these adds a constant for the parity lint to drift on.
    "cannon_fire_support": ("CannonFireSupportPower", None,
        "Whenever you play a [gold]Companion[/gold] card, gain {X} "
        "[gold]Block[/gold]."),
    "night_vigil": ("NightVigilPower", None,
        "Your Attacks against enemies holding an elemental aura deal {X} "
        "more damage."),
    "ancient_sea_authority": ("AncientSeaAuthorityPower", None,
        "Elemental auras you apply last {X} extra turn(s)."),
    "masque_red_death": ("MasqueRedDeathPower", None,
        "At the start of each turn, gain {X} [gold]Strength[/gold]. Each turn "
        "your [gold]Bond of Life[/gold] consumes the first 5 "
        "[gold]Block[/gold] you gain."),
    "fanfare_attack_per10": ("FanfareAttackPer10Power", None,
        "Your Attacks deal {X} more damage per 10 [gold]Fanfare[/gold]."),
    # B5 (2026-07-28): the face NAMES the member and says nothing else. The
    # member's act, its bow, and the cap rules moved to hover tips
    # (SalonMemberTips) -- eight cards were reprinting one paragraph that
    # named nobody. {MEMBER} is filled per effect from its `member:` value.
    "salon_member": ("SalonMemberPower", None,
        "Add {X} [gold]{MEMBER}[/gold] to your [gold]Salon[/gold]."),
    "salon_damage_up": ("SalonDamageUpPower", None,
        "[gold]Salon Member[/gold] numbers are {X} higher."),
    # A12 (2026-07-28): the stage's size stops being a constant.
    "salon_cap_up": ("SalonCapUpPower", None,
        "Your [gold]Salon[/gold] has room for {X} more "
        "[gold]Salon Member(s)[/gold]."),
    # ALL max_stacks DROPPED across Furina's sheet (user ruling 2026-07-24).
    # Two rounds: the first dropped the four non-compounding powers; this one
    # drops the rest, matching base StS where Power dupes always stack. An A/B
    # (2000 runs/arm x2 seeds, assigned pilots) put the whole cap set at 0.0pp
    # for the first four and +0.4-0.5pp (p~0.02, favorable) for the compounders,
    # i.e. non-binding at present difficulty. Two of these -- spotlight_mult_bonus
    # and ovation_spend_boost -- ARE genuinely compounding (per-copy % multipliers
    # that pass1-rulings-round2's exponent argument was about); they read minimal
    # ONLY because spotlight/fanfare win <1% pre-calibration. FLAGGED to re-check
    # at difficulty calibration. `salon_member`'s "Maximum 3" is NOT a max_stacks
    # cap -- it is the roster size (a full stage bows the oldest out), core salon
    # rules, and stays. NO numeric cap remains in this registry now.
    "spotlight_discount": ("SpotlightDiscountPower", None,
        "The first [gold]Spotlighted[/gold] card each turn costs {X} less."),
    "spotlight_draw": ("SpotlightDrawPower", None,
        "The first [gold]Spotlighted[/gold] card each turn draws {X} card{XS}."),
    "spotlight_mult_bonus": ("SpotlightMultBonusPower", None,
        "[gold]Spotlighted[/gold] Companion numbers are {X}% stronger "
        "this combat."),
    "spotlight_mult_bonus_turn": ("SpotlightMultBonusTurnPower", None,
        "[gold]Spotlighted[/gold] Companion numbers are {X}% stronger "
        "this turn."),
    "spotlight_flat_damage": ("SpotlightFlatDamagePower", None,
        "[gold]Spotlighted[/gold] Companion damage gains {X}."),
    "spotlight_flat_damage_turn": ("SpotlightFlatDamageTurnPower", None,
        "[gold]Spotlighted[/gold] Companion damage gains {X} this turn."),
    "ovation_spend_boost": ("OvationSpendBoostPower", None,
        "Whenever you spend Encore, [gold]Spotlighted[/gold] Companion "
        "numbers are {X}% stronger this turn."),
    "spotlight_encore_first": ("SpotlightEncoreFirstPower", None,
        "The first [gold]Spotlighted[/gold] card each turn grants {X} Encore."),
    # Curtain Call's activity-triggered set (R85), ported by the "Take a Bow"
    # consolidation sprint. Every one of them pays on an EVENT the player
    # caused rather than on a turn tick -- see Powers/CurtainCallPowers.cs for
    # the trigger sites and their tier0 mirrors. No caps: the activity gate IS
    # the rate limit, so a stack ceiling would be a second, redundant one.
    "salon_deploy_block": ("SalonDeployBlockPower", None,
        "Whenever you deploy a [gold]Salon Member[/gold], gain {X} Block."),
    "salon_bow_block": ("SalonBowBlockPower", None,
        "Whenever a [gold]Salon Member[/gold] takes its final bow, gain "
        "{X} Block."),
    "salon_bow_encore": ("SalonBowEncorePower", None,
        "Whenever a [gold]Salon Member[/gold] takes its final bow, gain "
        "{X} Encore."),
    "cross_examination": ("CrossExaminationPower", None,
        "The first [gold]Elemental Reaction[/gold] you trigger each turn "
        "applies {X} [gold]Vulnerable[/gold] and {X} [gold]Weak[/gold] to "
        "its target."),
    "encore_spend_draw": ("EncoreSpendDrawPower", None,
        "The first time you spend Encore each turn, draw {X} card{XS}."),
    "first_attack_draw": ("FirstAttackDrawPower", None,
        "The first Attack you play each turn draws {X} card{XS}."),
    # A7 (2026-07-29): the last sheet card to reach C#. The trigger lives in
    # FurinaResources.NoteFanfareChanged rather than in the power, because the
    # four Fanfare mutators are static methods, not broadcasts a PowerModel can
    # subscribe to.
    "fanfare_delta_block": ("FanfareDeltaBlockPower", None,
        "Whenever your [gold]Fanfare[/gold] changes amount, gain {X} "
        "[gold]Block[/gold]."),
}

# Powers applied to ENEMIES (native debuffs). Everything else in APPLY_POWERS
# is a self power; blocked_reason enforces the split both ways.
ENEMY_APPLY_POWERS = {"weak", "vulnerable"}

# Sheet fields apply_power may carry. Anything else encodes a mechanic this
# generator does not understand -- fail loudly (UNPARSEABLE discipline).
APPLY_POWER_FIELDS = {"op", "power", "amount", "target", "max_stacks", "note",
                      "splash_procs_per_turn",
                      # EB-26 D2 (ruled 2026-08-10, option (d)): floor-not-clamp.
                      # Opt-in; see NEVER_REDUCES_POWERS below for why it is
                      # not free to put on any row.
                      "never_reduces",
                      # Salon v2: the typed-member rider on salon_member
                      # deploys (rework plan §1).
                      "member",
                      # Companion sheet annotations (oz/albedo): the summon's
                      # element and aura consumption live in the POWER's C#
                      # implementation; the fields are documentation.
                      "summon_element", "consumes_aura"}

# Powers whose C# class implements the floor-not-clamp read (EB-26 D2). The
# sim honours `never_reduces` at its own chokepoint for ANY power, but the mod
# cannot: the composition rule lives in each power's
# TryModifyPowerAmountReceived, so a row asking for the mode on a power that
# does not implement it would ship a sim/mod split. Blocked by name instead
# (same UNPARSEABLE discipline as an unknown field).
NEVER_REDUCES_POWERS = {"prevent_exhaust_ward"}

# The C# each `member:` value emits. `random` is a NULL, which
# SalonMemberPower.Deploy resolves per iteration off the shared combat RNG
# stream (A11). Keyed rather than inlined so an unrecognised member is a
# named blocker instead of a KeyError mid-emit.
SALON_MEMBER_CS = {
    "crabaletta": "SalonMember.Crabaletta",
    "usher": "SalonMember.Usher",
    "chevalmarin": "SalonMember.Chevalmarin",
    "random": "null",
}

# B5: the stage names the faces print. These MUST match
# SalonMemberTips.DisplayName -- the card says "Add Gentilhomme Usher" and the
# tooltip that explains him is titled the same thing, or the player cannot
# tell they are about the same member. Pinned in the codegen tests.
SALON_MEMBER_NAMES = {
    "crabaletta": "Mademoiselle Crabaletta",
    "usher": "Gentilhomme Usher",
    "chevalmarin": "Surintendante Chevalmarin",
    "random": "random Salon Member",
}

# Upgrade keys that all mean "bump the applied power amount" at card level
# (tier0 upgrades.py handles them in one branch too).
# All of these bump the amount of the card's FIRST apply_power/buff_next_attack
# effect -- tier0 upgrades.py handles them in one branch, and `duration` (Oz,
# Solar Isotoma) and `buff` (both Bennetts) join it because the "amount" of
# those powers IS the duration / the attack bonus.
POWER_UPGRADE_KEYS = {"power_amount", "amp_percent", "splash_damage", "vulnerable",
                      "weak", "duration", "buff",
                      # R130 (2026-08-07): Kurage's Oath 5 -> 7. NAME-MATCHED
                      # like weak/vulnerable, which is how the sim binds it.
                      "kurage_ward"}

# Ops the POWER_UPGRADE_KEYS deltas may land on, in the sim's own precedence:
# `next(fx for fx in top if fx["op"] in (...))` -- the FIRST top-level one
# only, which is why Chevreuse's conditional rider stays at its printed value
# while her base buff scales.
POWER_UPGRADE_OPS = ("apply_power", "buff_next_attack")

# Bomb placement targets we have a verified selection idiom for.
#
# EB-118 §4.2 added `all_enemies` -- the DISTRIBUTION form, one Bomb per
# living enemy. It is not a synonym for the random forms and it is not
# interchangeable with them at any `amount` but 1: tier0 loops
# `amount x targets`, so `all_enemies` with `amount: 3` is three Bombs on
# EVERY enemy. The four distribution rows on the sheet all carry
# `amount: 1` for exactly that reason, and `_emit_place_bomb` mirrors the
# nesting order rather than assuming the sheet will stay disciplined.
BOMB_TARGETS = {"enemy", "all_enemies", "random_enemy", "random_enemies"}

# Damage targets we have a confirmed builder for (see AttackCommand).
DAMAGE_TARGETS = {"enemy", "all_enemies", "random_enemy", "random_enemies", "self"}

# Cards already hand-written; never overwrite them.
#
# jumpy_dumpty came off this list once place_bomb landed: its whole sheet entry
# (damage x2 at random enemies + a bomb) is now expressible, and its C1 stub was
# actively wrong -- it dropped the bomb half and retargeted to a chosen enemy.
# Kaboom and DuckAndCover stay hand-written as the reference examples the rest
# of the codebase's comments point at; Pop stays because it is the verified
# bomb card the playtest signed off on.
HAND_WRITTEN = {"kaboom", "duck_and_cover", "pop"}

# R23 aura-application batch (2026-07-20): hand-written because their ops read
# aura/bomb state (conditional-vs-aura, bonus_vs_aura, bonus_vs_bombed,
# refresh_all_auras) -- per-target bonuses live in ModifyDamageAdditive, which
# codegen does not emit.
HAND_WRITTEN |= {"sizzle", "flame_dance", "kaboom_beetle_swarm", "elemental_ecstasy"}

# Kit-grant sprint (2026-07-20): the Burst card is hand-written because its
# lifecycle is machinery, not ops -- granted by KitGrant at a full meter,
# BaseLib custom-resource cost (SetCanonicalCost BurstConstants.KleeMax = 40,
# klee.yaml burst_max / full-meter Spend), Retain keyword, and pool-registered
# only through KleeOffPoolCards (in AllCards so CardModel.Pool resolves, out
# of GetUnlockedCards so no generator can reach it). See Powers/KitBurst.cs.
HAND_WRITTEN |= {"sparks_n_splash"}

# Non-Klee hand-written cards. A SEPARATE set from HAND_WRITTEN above, which
# is Klee-scoped both by its guard and by lint_handwritten_parity.py, whose
# parity rules only know Klee's ops and whose file lookup only knows Cards/.
#
# The point of listing them at all is truthfulness in the generator's report.
# Without this, `ceremonial_garment` came back as "kit card (hand-write it
# against the KitBurst machinery)" -- an instruction that had already been
# carried out, which reads to the next person as outstanding work. A blocked
# reason should say why the generator declined, not hand out a stale TODO.
HAND_WRITTEN_ROSTER = {"let_the_people_rejoice", "ceremonial_garment"}

# R24 (2026-07-20): codegen upgrade defaults are ABOLISHED, not demoted.
# docs/klee-upgrades.yaml is the single source of truth for upgrade deltas.
# A generated card whose sheet entry is missing, or whose ruled delta this
# generator cannot express, ships with NO upgrade path and a loud manifest
# flag (the tier0 UNAPPLIABLE discipline, applied to C#) -- silent defaults
# are how cant_catch_me shipped +3 block against a ruled +2.
#
# Delta keys this generator can express on a card's effects:
#   damage      -> the card's non-self damage effect (DynamicVars.Damage)
#   block       -> block effect (DynamicVars.Block)
#   draw        -> draw effect (DynamicVars.Cards)
#   spark       -> gain_spark effect (DynamicVars["Sparks"], M9 ruling)
#   bomb_damage -> place_bomb effect (Damage or ExtraDamage, see bomb_var)
#   cost        -> EnergyCost.UpgradeBy(n) -- the idiom CardModel.OnUpgrade's
#                  own doc comment prescribes (verified in the decompile)
# Structural upgrades stay blocked unless an exact play-time mirror exists.
# `add: {op: draw, amount: N}` is the current exception: codegen appends an
# IsUpgraded-gated draw after the base effects, matching upgrades.py.
#   discard     -> discard_for_sparks count (DynamicVars["Discards"], R36)
#   sparks      -> discard_for_sparks Spark cap (DynamicVars["Sparks"], R36;
#                  distinct from `spark` = gain_spark on purpose)
#   innate      -> AddKeyword(CardKeyword.Innate) in OnUpgrade (R37; keywords
#                  are instance-owned LocalKeywords, and the base game's own
#                  Innate drives opening-hand placement + keyword text)
#   bonus       -> the detonate/move_bombs/modify_bombs bonus field
#                  (DynamicVars["Bonus"]; single bonus-carrying effect per
#                  card, guarded)
#   chance      -> chance_bomb_per_detonation REPLACEMENT (tier0 upgrades.py
#                  replaces, not bumps); codegen renders percent and emits
#                  the delta in points, computed from the sheet's base
#   conditional_bonus -> bumps the then-branch's first damage (tier0
#                  upgrades.py bumps first damage|block in then; codegen
#                  expresses the damage form via the ExtraDamage var and
#                  flags a then-block card as structural)
#   condition   -> "unconditional" only: tier0 hoists the then-branch out of
#                  the conditional; C# reads (IsUpgraded || pred) at play and
#                  swaps the text via {IfUpgraded:show:...|...} (the runtime
#                  form BaseLib's SimpleLoc generates for upgrade swaps)
#   bombs       -> X-cost bomb count: X_plus_N -> X_plus_(N+val) in tier0;
#                  codegen renders "X+{Bombs:diff()}" off a Bombs var
#   conditional_block / conditional_damage -> EB-140. tier0 bumps EVERY
#                  literal-int matching op the row prints, branches INCLUDED
#                  (upgrades.py: `block` anywhere; non-self `damage`
#                  anywhere). Codegen says the two halves in the two ways it
#                  already has: the TOP-LEVEL half through the op's own var
#                  (Block / Damage, or CalculationBase on a converted rider),
#                  the BRANCH half as an (IsUpgraded ? up : base) literal
#                  swap with {IfUpgraded:show:up|base} rendered beside it --
#                  curtain_cue's shape for the `encore` key. Distinct from
#                  `conditional_bonus`, which moves ONE branch number through
#                  the ExtraDamage var; these move ALL of them.
EXPRESSIBLE_DELTAS = ({"damage", "block", "draw", "spark", "encore",
                       "encore_cost", "fanfare_cost", "fanfare_cap",
                       "fanfare_floor", "heal",
                       "bomb_damage", "burst_energy", "cost",
                       "discard", "sparks", "innate", "retain", "bonus", "chance",
                       "conditional_bonus", "condition", "bombs",
                       # EB-140 (W3/R211's two unemittable keys). See the
                       # header note above: expressibility is decided per card
                       # by _conditional_delta_targets, not by the key alone.
                       "conditional_block", "conditional_damage",
                       "bonus_per_detonation", "bonus_slope",
                       # Fanfare rework Track C.2 (2026-07-28): the
                       # Hyperbeam's upgrade cuts its PRICE (the floor it
                       # digs), so the delta is normally negative.
                       "floor_drop",
                       "cards", "remove",
                       "copy_cost_override", "add",
                       # EB-122: `add`'s POSITION. The emitter appended, full
                       # stop, so an upgrade whose new line resolves in the
                       # MIDDLE of the ruled body was unexpressible and blocked
                       # the whole card's upgrade path (send_the_runner+, D2a).
                       # Names the op it precedes rather than an index, exactly
                       # as tier0's applier does, so a later edit to the base
                       # body cannot silently slide the insertion.
                       "add_before"}
                      | {"generate_cost_override"}
                      # Kokomi (playtest sprint, Track B). Three deltas her
                      # sheet already rules but codegen could not express, so
                      # three of her cards -- one of them a STARTER -- were
                      # shipping with no campfire upgrade at all (G-C1 lint).
                      | {"kurage_turns", "energy", "block_next_turn",
                         # `exhaust: +N` moves how many cards an exhaust_from
                         # takes. The VAR emitter ("Exhausts") already existed;
                         # the key was simply never declared expressible, so
                         # the first card to use it reported "structural
                         # upgrade" and shipped with no campfire path at all.
                         "exhaust",
                         # `formula_per: +N` bumps the PER term of an
                         # amount_formula, which is the ExtraDamage var in the
                         # CalculatedDamageVar triple -- the same slot the
                         # conditional_bonus delta moves.
                         "formula_per",
                         # `times: +N` moves a multi-hit attack's HIT COUNT
                         # (A5, 2026-07-28: Undercurrent 3 -> 5 hits). tier0
                         # has bumped `times` since Klee, but codegen baked
                         # the count in as a literal `.WithHitCount(3)`, so
                         # the key was unexpressible and the first card to
                         # rule it would have shipped with NO campfire path.
                         # Binds to the same effect tier0 does: the first
                         # damage op carrying a literal int `times`.
                         "times",
                         # `formula_base: +N` bumps the BASE term (the
                         # CalculationBase var). Added by F4 because only the
                         # per-term existed, and on an UNCAPPED count the two
                         # are different rulings: per is a slope on something
                         # that only grows, base pays once and stops.
                         "formula_base"}
                      | POWER_UPGRADE_KEYS)

# Ops whose `bonus` field the "bonus" upgrade delta may target.
BONUS_OPS = ("detonate", "move_bombs", "modify_bombs")

# `ancient` is DELIBERATELY ABSENT, and the KeyError a row of that rarity
# would raise here is enforcement rather than a gap. Every Ancient's C# class
# is hand-written (JumpyDumptyMkOmega.cs and the two beside it) and witnessed
# by tools/lint_handwritten_parity.py's ANCIENT_WITNESS; generating one would
# mean two classes for one card, free to drift apart. The rows live in a
# side-sheet this generator never reads (tier0/content/cards/ancients.yaml),
# so the KeyError is the second lock on an already-shut door -- keep it shut.
# R127 / EB-30m.
RARITY_CS = {
    "basic": "CardRarity.Basic",
    "common": "CardRarity.Common",
    "uncommon": "CardRarity.Uncommon",
    "rare": "CardRarity.Rare",
}

TYPE_CS = {"attack": "CardType.Attack", "skill": "CardType.Skill", "power": "CardType.Power"}

TARGET_CS = {
    "enemy": "TargetType.AnyEnemy",
    "all_enemies": "TargetType.AllEnemies",
    "random_enemy": "TargetType.AllEnemies",
    "random_enemies": "TargetType.AllEnemies",
    "self": "TargetType.Self",
}

# The ops whose `target: enemy` spelling means "the player picks one", and
# therefore reads `cardPlay.Target` at resolution. Kept beside TARGET_CS so
# the two cannot drift: every entry here maps through TARGET_CS["enemy"].
AIMING_OPS = ("damage", "place_bomb", "detonate", "move_bombs",
              "apply_aura", "swirl")


def _aims_at_chosen_enemy(eff: dict) -> bool:
    """Does this effect need a target the PLAYER chose?

    The question a card's declared TargetType has to answer. `apply_power`
    is included only for the powers that land on an enemy -- a self-buff
    named `target: self` aims at nothing.

    Asked of the WHOLE played face, branches included (EB-142): an aiming op
    dereferences `cardPlay.Target` wherever it sits, and a branch is printed
    text the player can reach.
    """
    if eff.get("target") != "enemy":
        return False
    if eff.get("op") in AIMING_OPS:
        return True
    return (eff.get("op") == "apply_power"
            and eff.get("power") in ENEMY_APPLY_POWERS)

# A card-level field can alter playability or lifecycle without appearing in
# effects. Treating unknown fields as harmless metadata is therefore unsafe:
# that is how an Encore/Fanfare cost could otherwise disappear while the body
# still compiles. Descriptive/draft metadata is allowlisted beside every
# currently implemented lifecycle field.
CARD_FIELDS = {
    # Kokomi/Silent Sly: extra effects that fire when the card is DISCARDED.
    "sly",
    "id", "name", "cost", "type", "rarity", "solve", "archetypes", "role",
    "effects", "tags", "exhaust", "kit_card", "requires",
    # A9 (2026-07-28): Innate on the BASE card, not only as an upgrade delta.
    # tier0 needed nothing -- Card.innate already existed and combat's
    # surface_innate reads it on any card -- but the generator emitted the
    # keyword only from OnUpgrade, so the field was unknown here and the
    # first card to rule it was BLOCKED. That block is the design working:
    # hearts_swelling reported "card field(s) ['innate'] not understood"
    # rather than shipping a card that starts in hand in the sim and does
    # not in the game.
    "innate",
    # Fanfare rework Track C.1 (2026-07-28): Retain on the BASE card, and
    # EXACTLY the A9 story again one field over. Retain was already emittable
    # as an upgrade delta (`AddKeyword(CardKeyword.Retain)` in OnUpgrade), so
    # the keyword rail existed and only the base-card spelling was missing --
    # which meant Slip Backstage, the first card ruled Retain from print,
    # BLOCKED with "card field(s) ['retain'] not understood". The block is
    # the design working twice: a card that retains in the sim and does not
    # in the game is precisely the divergence this whitelist exists to stop.
    "retain",
    # EB-118: Ethereal on the BASE card, the A9 / Track-C.1 story a third
    # time. The keyword rail below already carried Exhaust/Innate/Retain and
    # the game owns the whole behaviour from the keyword alone
    # (CombatManager.EndPlayerTurnInternal exhausts every hand card whose
    # Keywords contain Ethereal, causedByEthereal: true), so nothing is
    # reimplemented here -- only the base-card spelling was missing, and
    # without this entry the first card ruled Ethereal from print would BLOCK
    # with "card field(s) ['ethereal'] not understood".
    "ethereal",
    # Companion identity/reward metadata.
    "star", "element", "role_c", "personal_pool", "nation", "character",
    "guest_star",
    # Furina resource gates. BaseLib provides affordability and post-effect
    # Fanfare spend; FurinaResourceHooks moves Encore spend pre-effect.
    "encore_cost", "fanfare_cost",
    # Curtain Call (R85): the register a card's NAME speaks in. Purely
    # descriptive naming metadata (salon | archon | private on Furina's
    # sheet) -- nothing mechanical to emit, so it is whitelisted as inert
    # rather than treated as an unexpressed mechanic.
    "register",
    # Track A / R92-3b: when in a fight and when in a run a card is worth
    # playing, `{fight: [...], run: [...]}`. Descriptive taxonomy metadata
    # exactly like `solve` and `register` -- nothing mechanical to emit, so it
    # is whitelisted as inert. Listed here rather than left unknown because
    # this whitelist is deliberately total and would otherwise BLOCK all 219
    # cards. Cross-session note:
    # docs/sprint-axis-validity-track-a-log-2026-08-04.md.
    "tempo_band",
    # Internal, never authored on a sheet: _sly_view stamps it so the text
    # and body emitters know they are rendering the discard branch. Listed
    # here because that view is now run through blocked_reason like any
    # other card, and the field whitelist is deliberately total.
    "_sly_branch",
}


def card_level_reason(
    card: dict, profile: CharacterProfile = KLEE_PROFILE
) -> str | None:
    """Return a blocker for card-level semantics the emitter cannot honor."""
    unknown = set(card) - CARD_FIELDS
    if unknown:
        return f"card field(s) {sorted(unknown)} not understood"
    return None


def pascal(card_id: str) -> str:
    """kaboom -> Kaboom, sorry_jean -> SorryJean, jumpy_dumpty_mk2 -> JumpyDumptyMk2."""
    return "".join(p.capitalize() for p in re.split(r"[_\-]", card_id) if p)


def cs_escape(text: str) -> str:
    """A sheet string as a C# literal body. Backslash first, or the quote
    escape this adds would be escaped a second time."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


_sheet_cards_cache: dict[Path, list] = {}


def _sheet_cards(sheet: Path) -> list[dict]:
    """The parsed rows of one character sheet, read at most once per run."""
    if sheet not in _sheet_cards_cache:
        _sheet_cards_cache[sheet] = yaml.safe_load(
            sheet.read_text(encoding="utf-8"))
    return _sheet_cards_cache[sheet]


def _pool_members(
    pool: str, profile: CharacterProfile = KLEE_PROFILE
) -> list[dict]:
    """tier0 loader.cards_in_pool, resolved against the sheet at generation
    time (archetype/rarity live only there): '<archetype>_<rarity>s'.

    The pool is resolved against the PROFILE'S sheet. It used to be Klee's
    sheet for every profile -- harmless only because `pool:` appears on
    exactly one row repo-wide, and that row is Klee's; a Furina card naming a
    pool would have silently drawn Klee's cards into her token list.
    """
    archetype, _, rarity = pool.rpartition("_")
    rarity = rarity.rstrip("s")
    return sorted((c for c in _sheet_cards(profile.sheet)
                   if c.get("rarity") == rarity
                   and archetype in c.get("archetypes", [])
                   and not c.get("kit_card")),
                  key=lambda c: c["id"])


def _x_formula_reason(card: dict, val) -> str | None:
    """tier0 _amount grammar: 'X' or 'X_plus_N', legal only on an X-cost
    card (state.current_x is the energy spent). None = expressible."""
    if str(card.get("cost")) != "X":
        return f"amount formula '{val}' on a non-X-cost card"
    if val == "X" or (isinstance(val, str) and val.startswith("X_plus_")
                      and val[len("X_plus_"):].isdigit()):
        return None
    return f"amount formula '{val}'"


# Runtime counts legal as a `times:` hit count. Curtain Call's Matinee
# Performance is the one user: a per-member hit whose count is the live cast
# size. Read at resolution off the power stack the deploy site mirrors, which
# is the same read tier0's _runtime_count does -- and the same precedent
# Mirage's enemy_poison_total set for counting over power stacks.
#
# Deliberately a SMALL allowlist, not "any count token". A times value the
# generator cannot express must stay a named blocker: guessing it produces a
# card that compiles and quietly hits once forever while the face promises
# scaling, which is the worst failure this generator has.
RUNTIME_TIMES = {
    "salon_members": "SalonMemberPower.Count(Owner.Creature)",
}

# The clause each runtime count renders on the face. Separate from the C#
# expression because the player reads the CAST, not the power stack that
# happens to mirror it.
RUNTIME_TIMES_TEXT = {
    "salon_members": " once per [gold]Salon Member[/gold]",
}


def _times_reason(card: dict, eff: dict) -> str | None:
    """Why this effect's `times:` cannot be generated, or None.

    EB-132. This test used to live INSIDE the `op == "damage"` arm of
    `blocked_reason`, and that placement was the defect. tier0 honours
    `times:` on five ops -- `_op_damage` (`tier0/engine/effects.py:799`),
    `_op_block` (`:937`), `_op_apply_power` (`:1201`), `_op_repeat_this`
    (`:2444`) and `_op_replay_next_companion` (`:2498`) -- and `_op_block`
    loops the WHOLE gain exactly the way `_op_damage` loops its hits, so
    `{op: block, amount: 2, times: exhaust_pile}` pays `amount x pile` in the
    sim. The block emitter has no hit-count path at all: it writes ONE
    `await CreatureCmd.GainBlock` whatever `times` says. A runtime count was
    therefore a NAMED BLOCKER one arm over and INVISIBLE here. The test is
    hoisted out so it covers every op that reads the field, and each op gets
    the answer its own emitter can honestly back:

      damage -- a literal hit count, a `RUNTIME_TIMES` member and an X
                formula all render (`.WithHitCount`), so the allowlist is
                the whole rule.
      block  -- NOTHING but 1 renders. Building the C# loop is not this
                row's work and inventing one here would be a behaviour
                change nobody asked for: the grammar is honestly
                unavailable in BOTH engines until someone writes it, and a
                named blocker is what that looks like. A literal `times: 3`
                is refused for the same reason a runtime count is -- the
                emitter cannot count either.

    The two remaining ops are covered by their own arms in `blocked_reason`
    and are deliberately left there rather than restated here, so no shape
    acquires a second, differently-worded refusal: `apply_power` refuses
    `times` through `APPLY_POWER_FIELDS` totality, and `repeat_this` /
    `replay_next_companion` each demand a literal int. The correspondence is
    pinned in `tier0/tests/test_eb132_block_times_parity.py`, which reads the
    honouring set off the engine rather than trusting this comment.
    """
    op = eff.get("op")
    times = eff.get("times", 1)
    if op == "damage":
        if (not isinstance(times, int) and times not in RUNTIME_TIMES
                and _x_formula_reason(card, times)):
            return _x_formula_reason(card, times)
        return None
    if op == "block":
        if times != 1:
            return (
                f"times {times!r} on op 'block' -- tier0 loops the whole "
                "Block gain and the emitter has no hit-count path (it would "
                "write one un-looped GainBlock)")
    return None


def _x_expr(val, bombs_var: bool = False) -> str:
    """C# expression for a tier0 amount formula ('x' is ResolveEnergyXValue,
    declared at the top of OnPlay)."""
    if val == "X":
        return "x"
    n = int(val[len("X_plus_"):])
    if bombs_var:
        return 'x + DynamicVars["Bombs"].IntValue'
    return f"x + {n}"


def blocked_reason(
    card: dict, profile: CharacterProfile = KLEE_PROFILE
) -> str | None:
    """Return why this card cannot be generated, or None if it can."""
    card_reason = card_level_reason(card, profile)
    if card_reason:
        return card_reason

    # The Sly branch is CARD BEHAVIOUR and gets the same scrutiny as the
    # played face. It did not, and the result was tidal_lure: its sheet says
    # Vulnerable 1 to a RANDOM enemy, the apply_power emitter treats
    # anything-but-"enemy" as all-enemies, and the guard that would have
    # caught that only ever looked at `effects`. The card generated, compiled,
    # and debuffed the whole room. An unchecked branch is not a smaller
    # surface; it is the same surface with the alarm disconnected.
    if card.get("sly"):
        marker_reason = _sly_marker_reason(card)
        if marker_reason:
            return marker_reason
    if sly_riders(card):
        sly_reason = blocked_reason(_sly_view(card), profile)
        if sly_reason:
            return f"sly branch: {sly_reason}"

    if profile is KLEE_PROFILE and card["id"] in HAND_WRITTEN:
        return "hand-written"

    if card["id"] in HAND_WRITTEN_ROSTER:
        return "hand-written"

    if is_companion(card):
        # Companions apply their element via the card-level IElementalCard,
        # so mixed elemental/non-elemental damage on one card cannot be
        # expressed (tier0 reads applies_element per effect).
        applies = {bool(e.get("applies_element"))
                   for e in card.get("effects", [])
                   if e.get("op") == "damage" and e.get("target") != "self"}
        if len(applies) > 1:
            return "mixed applies_element damage on one companion card"

    # X cost (R34 batch): HasEnergyCostX => true + ResolveEnergyXValue()
    # (CapturedXValue through Hook.ModifyXValue -- the game-canonical X
    # read). The spark-spend exemption for X attacks is already in
    # SparkPower.AppliesTo (!CostsX), the sim's R34 rule.

    # Kit cards: granted-not-drafted, requires-full gate, meter spend. The
    # machinery landed 2026-07-20 (Powers/KitBurst.cs) with sparks_n_splash
    # hand-written; a FUTURE kit card hitting this guard needs the same
    # decision (hand-write it or teach codegen the kit lifecycle) -- loud
    # either way, never generated as ordinary loot.
    if card.get("kit_card") or card.get("requires"):
        return "kit card (hand-write it against the KitBurst machinery)"

    # `amount_formula` (Kokomi's exhaust-pile scalers, playtest sprint Track B).
    # A computed amount that reads a PILE SIZE at resolve time. The generator
    # has no grammar for it, and the failure mode of guessing is the worst
    # kind: a card that emits, compiles, and quietly deals its `base` forever
    # while the face promises scaling. Block loudly instead -- UNPARSEABLE
    # discipline. Teaching this needs a CalculatedVar bound to the exhaust
    # pile, which is Track C work, not a codegen shortcut.
    for effect in card.get("effects", []):
        if ("amount_formula" in effect
                and exhaust_pile_calc_rider(card, effect) is None
                and exhaust_selection_calc_rider(card, effect) is None
                and discards_turn_calc_rider(card, effect) is None):
            formula = effect["amount_formula"]
            return (f"amount_formula (reads {formula.get('count')}) -- needs a "
                    "CalculatedVar bound to that count, not a literal")

    # R20: inline upgrade fields are deprecated repo-wide -- deltas live in
    # *-upgrades.yaml sheets. Block loudly so a stray inline key can never
    # silently diverge from the upgrades sheet.
    if "upgrade" in card:
        return "inline `upgrade:` field (deprecated by R20 -- put the delta in klee-upgrades.yaml)"

    # "Sparks" is one DynamicVar name: a card carrying BOTH gain_spark and
    # discard_for_sparks would collide on it. No such card exists; block
    # loudly if one appears rather than silently overwrite.
    ops_present = {e.get("op") for e in card.get("effects", [])}
    if {"gain_spark", "discard_for_sparks"} <= ops_present:
        return "gain_spark + discard_for_sparks on one card (Sparks var collision)"

    for eff in card.get("effects", []):
        op = eff.get("op")
        if op not in MECHANICAL_OPS:
            return f"op '{op}'"
        # EB-132: hoisted out of the damage arm so it covers every op that
        # honours `times:` -- see _times_reason for which op gets which answer.
        times_reason = _times_reason(card, eff)
        if times_reason:
            return times_reason
        # B1 CLASS FIX (2026-07-28). A `bonus_formula` on a NON-damage op is a
        # blocker unless a rider actually expresses it.
        #
        # Damage is exempt because damage riders always resolve: an
        # unconverted one still rides the PrintedDamage path at resolution
        # (it merely fails to show on the face, which is what the Legibility
        # sprint converted). Every OTHER op had no such path -- the formula
        # was read by nothing, so the card silently shipped its bare base.
        # Thunderous Ovation lost `1_per_2_fanfare` that way for two
        # playtests. Blocking is the honest failure: an UNAPPLIABLE card is
        # visible in the manifest, a quietly-wrong one is not.
        if op != "damage" and eff.get("bonus_formula") is not None \
                and block_calc_rider(card, eff) is None:
            return (f"bonus_formula '{eff['bonus_formula']}' on op '{op}' is "
                    "expressed by no rider (it would render as the bare base)")
        if op == "damage":
            tgt = eff.get("target")
            if tgt not in DAMAGE_TARGETS:
                return f"damage target '{tgt}'"
            if eff.get("times_formula", "2_plus_sparks") != "2_plus_sparks":
                # The sim's only times formula (effects.py raises on others).
                return f"times_formula '{eff['times_formula']}'"
            bf = eff.get("bonus_formula")
            if bf is not None and not (
                    bf.endswith("_per_detonation_this_combat")
                    and bf.partition("_per_")[0].isdigit()) and not re.fullmatch(
                        r"\d+_per_\d+_fanfare", bf) and not re.fullmatch(
                        # Kokomi's Charge reader. Same CalculatedDamageVar path
                        # as Fanfare's -- see charge_calc_rider for why an
                        # honest printed number matters more here than there.
                        r"\d+_per_\d+_charge", bf) and not re.fullmatch(
                        # Curtain Call: Body Slam's grammar -- an attack priced
                        # off the held Encore buffer. READ only, never spent.
                        r"\d+_per_\d+_encore", bf) and not re.fullmatch(
                        # A14: the per-member slope. No divisor -- the salon is
                        # a capped count, so every member is a full step.
                        r"\d+_per_salon_member", bf) and not re.fullmatch(
                        # Track C.3 (2026-07-28): Blocking Notes' Companion
                        # tempo. No divisor, same reason as salon_member --
                        # a big turn is three or four plays, not a pool.
                        r"\d+_per_companion_played_this_turn", bf):
                return f"bonus_formula '{bf}'"
            if "bonus_vs_bombed" in eff:
                return "conditional damage bonus (needs bomb system)"
            if "bonus_vs_aura" in eff:
                if eff.get("target") not in {"enemy", "all_enemies"} \
                        or not isinstance(eff["bonus_vs_aura"], int):
                    return (
                        "bonus_vs_aura requires enemy damage and "
                        "a literal int")
            # `times` is checked by _times_reason at the top of this loop
            # (EB-132) -- it is not a damage-only field.
        if op == "place_bomb":
            if eff.get("target") not in BOMB_TARGETS:
                return f"bomb target '{eff.get('target')}'"
            amt = eff.get("amount")
            if not isinstance(amt, int) and _x_formula_reason(card, amt):
                return _x_formula_reason(card, amt)
        if op in {"salon_rotate", "salon_perform"}:
            # EB-118 §5.5. Same field discipline as the meter ops above,
            # with `amount` OPTIONAL: one rotation and one act are the
            # natural units, so `{op: salon_rotate}` is the common row
            # and the default is the sim's (1).
            unknown = set(eff) - {"op", "amount"}
            if unknown:
                return f"{op} field(s) {sorted(unknown)} not understood"
            amount = eff.get("amount", 1)
            if not isinstance(amount, int) or amount <= 0:
                return f"{op} amount must be a positive literal int"
        if op in {"gain_encore", "spend_encore", "raise_fanfare_cap",
                  "gain_fanfare_floor", "crash_fanfare", "salon_bow",
                  # A Spark price the generator cannot read as a
                  # literal is a price the IsPlayable gate cannot show.
                  "spend_spark"}:
            unknown = set(eff) - {"op", "amount"}
            if unknown:
                return f"{op} field(s) {sorted(unknown)} not understood"
            if not isinstance(eff.get("amount"), int) or eff["amount"] <= 0:
                return f"{op} amount must be a positive literal int"
        if op == "heal":
            unknown = set(eff) - {"op", "amount"}
            if unknown:
                return f"heal field(s) {sorted(unknown)} not understood"
            if not isinstance(eff.get("amount"), int) or eff["amount"] <= 0:
                return "heal amount must be a positive literal int"
            if card.get("rarity") != "rare" or not card.get("exhaust"):
                return "heal requires a Rare card with Exhaust"
        if op == "detonate":
            if eff.get("target") not in {"enemy", "all_enemies"}:
                return f"detonate target '{eff.get('target')}'"
            unknown = set(eff) - DETONATE_FIELDS
            if unknown:
                return f"detonate field(s) {sorted(unknown)} not understood"
        if op == "move_bombs":
            if eff.get("target") != "enemy":
                return f"move_bombs target '{eff.get('target')}' (only a chosen enemy has a selection idiom)"
            unknown = set(eff) - MOVE_BOMBS_FIELDS
            if unknown:
                return f"move_bombs field(s) {sorted(unknown)} not understood"
        if op == "modify_bombs":
            if eff.get("scope", "all") not in {"all", "placed_this_turn"}:
                return f"modify_bombs scope '{eff.get('scope')}'"
            unknown = set(eff) - MODIFY_BOMBS_FIELDS
            if unknown:
                return f"modify_bombs field(s) {sorted(unknown)} not understood"
        if op == "chance_bomb_per_detonation":
            unknown = set(eff) - CHANCE_BOMB_FIELDS
            if unknown:
                return f"chance_bomb_per_detonation field(s) {sorted(unknown)} not understood"
            # The count source is the detonate call earlier in THIS card's
            # effect list (tier0 diffs its counter around the card play; the
            # generated body reads the DetonateOn/DetonateAll return).
            idx = card["effects"].index(eff)
            if not any(e.get("op") == "detonate" for e in card["effects"][:idx]):
                return "chance_bomb_per_detonation without a preceding detonate (no count source)"
        if op == "apply_power":
            power = eff.get("power")
            # A7's deferral is RELEASED (2026-07-29). It stood for two sprints
            # on a real structural gap -- the Fanfare mutators are synchronous
            # and every block grant in the mod is `await CreatureCmd.GainBlock`
            # -- and neither way out it named was ever taken. Threading async
            # through the resource surface is still a co-op-critical refactor,
            # and Creature.GainBlockInternal still has no precedent.
            #
            # The third way, which the deferral note did not consider, is the
            # one already shipping next door: NOTE synchronously, SETTLE at the
            # next awaited hook. CurtainCallHooks.NoteEncoreSpent has done
            # exactly that on the same funnel since R85. See
            # FurinaResources.PendingDeltaBlock for the idiom and its four
            # settle points; the deferral is gone rather than emptied because
            # the gap it named is closed, not merely postponed.
            if power not in APPLY_POWERS:
                return f"apply_power power '{power}' (no PowerModel in the registry)"
            if power in ENEMY_APPLY_POWERS:
                # Native debuffs aim at enemies (tier0 _op_apply_power ->
                # _pick_targets). random targeting has no verified idiom yet.
                if eff.get("target") not in (
                        "enemy", "all_enemies", "random_enemy"):
                    return (f"apply_power target '{eff.get('target')}' "
                            f"for enemy debuff '{power}'")
            elif eff.get("target") != "self":
                return f"apply_power target '{eff.get('target')}' (self power aimed at enemies)"
            unknown = set(eff) - APPLY_POWER_FIELDS
            if unknown:
                # UNPARSEABLE discipline: an unrecognized field encodes a
                # mechanic; block loudly, never approximate.
                return f"apply_power field(s) {sorted(unknown)} not understood"
            # A11: the member value is emitted through a lookup, and a lookup
            # miss mid-emit is a KeyError -- a stack trace, not a decision.
            # Refuse the card by name instead, the way every other
            # unexpressible value on this sheet is refused.
            if "member" in eff and eff["member"] not in SALON_MEMBER_CS:
                return (f"salon member '{eff['member']}' is not one of "
                        f"{sorted(SALON_MEMBER_CS)}")
            # EB-26 D2 option (d). The mode is only expressible where the C#
            # power implements it, and it is meaningless without a cap to
            # raise the stack toward -- refuse both shapes by name.
            if eff.get("never_reduces"):
                if power not in NEVER_REDUCES_POWERS:
                    return (f"never_reduces on power '{power}', which has no "
                            "floor-not-clamp implementation in C# "
                            f"(implemented: {sorted(NEVER_REDUCES_POWERS)})")
                if eff.get("max_stacks") is None:
                    return "never_reduces without max_stacks (no ceiling to raise toward)"
            cap = APPLY_POWERS[power][1]
            if eff.get("max_stacks") != cap and not (eff.get("max_stacks") is None and cap is None):
                # Cap drift between the sheet and the C# power class const.
                raise SystemExit(
                    f"gen_klee_cards: {card['id']}: sheet max_stacks "
                    f"{eff.get('max_stacks')!r} != registered cap {cap!r} for "
                    f"power '{power}' -- update BOTH the C# power and the registry.")
            if power == "detonation_splash" and eff.get("splash_procs_per_turn") != 3:
                raise SystemExit(
                    f"gen_klee_cards: {card['id']}: splash_procs_per_turn "
                    f"{eff.get('splash_procs_per_turn')!r} != 3; the C# cap is the "
                    f"DemolitionConstants.SplashProcCapPerTurn const -- change both.")
        if op == "cost_mod":
            unknown = set(eff) - {"op", "scope", "delta", "duration"}
            if unknown:
                return f"cost_mod field(s) {sorted(unknown)} not understood"
            if eff.get("scope") != "companion_cards":
                return f"cost_mod scope '{eff.get('scope')}'"
            if eff.get("duration") != "this_turn":
                return f"cost_mod duration '{eff.get('duration')}'"
            if not isinstance(eff.get("delta"), int) or eff["delta"] >= 0:
                return "cost_mod delta must be a negative literal int"
        if op == "copy_companion_in_hand":
            # `temp` accepted and IGNORED: tier0 _op_copy_companion_in_hand
            # never reads it (the copy persists) -- the sim is LAW, so the
            # mirror ignores it too rather than inventing a mechanic.
            unknown = set(eff) - {"op", "amount", "temp", "cost_override"}
            if unknown:
                return f"copy_companion_in_hand field(s) {sorted(unknown)} not understood"
            if eff.get("amount", 1) != 1:
                return "copy_companion_in_hand amount > 1 (single-pick idiom only)"
            if "cost_override" in eff and not isinstance(eff["cost_override"], int):
                return "copy_companion_in_hand cost_override must be a literal int"
        if op == "copy_spotlighted_in_hand":
            unknown = set(eff) - {"op", "amount", "cost_override"}
            if unknown:
                return (
                    "copy_spotlighted_in_hand field(s) "
                    f"{sorted(unknown)} not understood")
            if eff.get("amount", 1) != 1:
                return (
                    "copy_spotlighted_in_hand amount > 1 "
                    "(single-pick idiom only)")
            if "cost_override" in eff and not isinstance(
                    eff["cost_override"], int):
                return (
                    "copy_spotlighted_in_hand cost_override must be "
                    "a literal int")
        if op == "replay_next_companion":
            unknown = set(eff) - {"op", "times", "duration"}
            if unknown:
                return f"replay_next_companion field(s) {sorted(unknown)} not understood"
            if eff.get("duration") != "this_turn":
                return f"replay_next_companion duration '{eff.get('duration')}'"
            if not isinstance(eff.get("times", 1), int):
                return "replay_next_companion times must be a literal int"
        if op == "copy_companions_played_this_combat":
            unknown = set(eff) - {"op", "zone", "cost_override"}
            if unknown:
                return f"copy_companions_played field(s) {sorted(unknown)} not understood"
            if eff.get("zone", "hand") != "hand":
                return f"copy_companions_played zone '{eff.get('zone')}'"
            if "cost_override" in eff and not isinstance(eff["cost_override"], int):
                return "copy_companions_played cost_override must be a literal int"
        if op == "apply_aura":
            unknown = set(eff) - APPLY_AURA_FIELDS
            if unknown:
                return f"apply_aura field(s) {sorted(unknown)} not understood"
            if eff.get("element") not in ELEMENT_CS:
                return f"apply_aura element '{eff.get('element')}'"
            if eff.get("target", "enemy") not in ("enemy", "random_enemy",
                                                  "all_enemies"):
                return f"apply_aura target '{eff.get('target')}'"
        if op == "swirl":
            unknown = set(eff) - SWIRL_FIELDS
            if unknown:
                return f"swirl field(s) {sorted(unknown)} not understood"
            if eff.get("target", "enemy") not in ("enemy", "random_enemy",
                                                  "all_enemies"):
                return f"swirl target '{eff.get('target')}'"
        if op == "block_next_turn":
            unknown = set(eff) - BLOCK_NEXT_TURN_FIELDS
            if unknown:
                return f"block_next_turn field(s) {sorted(unknown)} not understood"
            if not isinstance(eff.get("amount"), int):
                return "block_next_turn amount must be a literal int"
        if op == "buff_next_attack":
            unknown = set(eff) - BUFF_NEXT_FIELDS
            if unknown:
                return f"buff_next_attack field(s) {sorted(unknown)} not understood"
            if not isinstance(eff.get("amount"), int):
                return "buff_next_attack amount must be a literal int"
        if op == "energy":
            unknown = set(eff) - ENERGY_FIELDS
            if unknown:
                return f"energy field(s) {sorted(unknown)} not understood"
            if not isinstance(eff.get("amount"), int):
                return "energy amount must be a literal int"
        if op == "scry_discard":
            unknown = set(eff) - SCRY_FIELDS
            if unknown:
                return f"scry_discard field(s) {sorted(unknown)} not understood"
            if not isinstance(eff.get("amount"), int):
                return "scry_discard amount must be a literal int"
        if op == "exhaust_from":
            unknown = set(eff) - EXHAUST_FROM_FIELDS
            if unknown:
                return f"exhaust_from field(s) {sorted(unknown)} not understood"
            # Hand is the only zone either character exhausts from, and it
            # is the sim's default for an omitted `zone` (Kokomi's sheet
            # omits it on every row). Requiring the key explicitly blocked
            # six of her cards -- including a STARTER -- over a field that
            # has exactly one legal value.
            if eff.get("zone", "hand") != "hand":
                return f"exhaust_from zone '{eff.get('zone')}'"
            # An UNFILTERED exhaust_from is legal when the player picks the
            # victims: the sim's pool is "hand minus kit cards" and the
            # chosen branch emits exactly that filter. The any-card pool that
            # was never built is the RANDOM one -- rolling a victim out of the
            # whole hand -- and that is still blocked below.
            if eff.get("filter") != "status" and eff.get("select") != "chosen":
                return "exhaust_from without status filter (any-card pool not built)"
            if eff.get("filter") not in (None, "status"):
                return f"exhaust_from filter '{eff.get('filter')}'"
            # amount > 1 is expressible ONLY on the chosen branch, and the
            # distinction is not pedantry. The sim's RANDOM branch re-rolls
            # against a pool that shrinks after each victim; expressing that
            # faithfully needs a loop that re-reads the hand, which is the
            # thing that was never built. The CHOSEN branch has no such
            # problem: CardSelectCmd.FromHand takes a count and returns N
            # distinct cards in one prompt, which is exactly the sim's
            # "pick the worst, remove it from the pool, repeat" without the
            # loop. Blanket-blocking both cost cleansing_tide (a Common) and
            # moonlit_offering their upgrade paths for no reason.
            # EB-133. The clause below licenses `amount != 1` on the chosen
            # branch because `CardSelectCmd.FromHand` takes a COUNT -- and a
            # count is exactly what a non-literal amount is not. It never
            # checked that the value was an INT, so `{op: exhaust_from,
            # select: chosen, amount: all}` walked past every refusal in this
            # function and met `str(int(eff.get("amount", 1)))` in the chosen
            # emitter: a ValueError stack trace, thrown by the one mechanism
            # whose entire job is to name what cannot be expressed.
            #
            # The row is LEGAL tier0 grammar -- `_op_exhaust_from` reads
            # `n = len(pool) if n == "all" else _amount(state, n)`
            # (`tier0/engine/effects.py:1995-1999`), Stoke's whole-hand shape,
            # and `_amount` accepts the `X` / `X_plus_N` formulas besides.
            #
            # IT IS REFUSED RATHER THAN EMITTED, deliberately. Emitting a
            # pool-sized selection means committing to what
            # `CardSelectorPrefs`' count means when it is not a literal --
            # whether it clamps to the hand, whether a screen that can only be
            # answered one way is shown at all -- and NO decompile is
            # available to read that contract off. No committed row prints the
            # shape, so an emitted body would be a guess at a call contract in
            # code no card compiles: precisely the failure the closed maps in
            # this file (RUNTIME_TIMES, the branch-field tables) exist to
            # prevent. A named blocker is the honest answer until someone with
            # the dll builds the loop.
            amount = eff.get("amount", 1)
            if not isinstance(amount, int):
                return (
                    f"exhaust_from amount {amount!r} is not a literal int "
                    "(the C# selector takes a count; the pool-sized 'all' "
                    "loop and the X formulas are not built)")
            if amount != 1 and eff.get("select") != "chosen":
                return "exhaust_from amount > 1 (random re-pool loop not built)"
        if op == "grant_sly_this_turn":
            # EB-122. `card_type` is the sheet's target filter and the ONLY
            # value with a verified C# read is `skill`: Hand Trick's filter is
            # `card.Type == CardType.Skill`, and the sim's own default is the
            # same word. Another type is expressible in principle and has no
            # card, so it stays a NAMED blocker rather than a guess -- the
            # discipline every closed map in this file states.
            unknown = set(eff) - {"op", "card_type"}
            if unknown:
                return (f"grant_sly_this_turn field(s) {sorted(unknown)} "
                        "not understood")
            if eff.get("card_type", "skill") != "skill":
                return (f"grant_sly_this_turn card_type "
                        f"'{eff['card_type']}' (only 'skill' has a verified "
                        "C# filter)")
        if op == "recall_to_draw":
            # EB-118 §6.4. Constraints 3-6 are runtime pool filters and live
            # in RecallFromExhaust.Recallable; 1 and 2 are card SHAPE and are
            # checked here, because the generator reads the sheet directly and
            # never passes through the tier0 loader that enforces them
            # (loader._validate_recall_shape). A row that reaches the emitter
            # has therefore been checked on both sides of the wall.
            unknown = set(eff) - RECALL_FIELDS
            if unknown:
                return f"recall_to_draw field(s) {sorted(unknown)} not understood"
            src = eff.get("from", "discard")
            if src not in ("exhaust", "discard"):
                return f"recall_to_draw from '{src}'"
            if eff.get("position", "top") != "top":
                return f"recall_to_draw position '{eff.get('position')}'"
            if not isinstance(eff.get("amount", 1), int):
                return "recall_to_draw amount must be a literal int"
            # EB-122: §6.4's card-shape constraints belong to the EXHAUST
            # source and only to it. They price a LOAN out of a pile a card
            # would never otherwise leave; a discard-pile card was always
            # coming back on the next reshuffle, so there is nothing to price
            # and nothing to cycle. `what_the_tokoyo_returns` is an Uncommon
            # that does not Exhaust, and it is legal. tier0 draws the same
            # line at the same place (loader._validate_recall_shape).
            if src == "exhaust":
                if card.get("rarity") not in ("uncommon", "rare"):
                    return (f"recall_to_draw on a {card.get('rarity')} card "
                            f"(EB-118 §6.4 constraint 1: Uncommon or Rare)")
                if not card.get("exhaust"):
                    return ("recall_to_draw on a card that does not Exhaust "
                            "(EB-118 §6.4 constraint 2)")
        if op == "add_card":
            unknown = set(eff) - ADD_CARD_FIELDS
            if unknown:
                return f"add_card field(s) {sorted(unknown)} not understood"
            zone = eff.get("zone") or eff.get("to", "discard")
            if zone not in ("hand", "discard"):
                return f"add_card zone '{zone}'"
            if "pool" in eff:
                members = _pool_members(eff["pool"], profile)
                if not members:
                    return f"add_card pool '{eff['pool']}' resolves empty"
                # Every member must itself generate: CreateCard needs a class.
                bad = [m["id"] for m in members
                       if m["id"] == card["id"] or blocked_reason(m, profile)]
                if bad:
                    return (f"add_card pool '{eff['pool']}' contains "
                            f"ungenerated card(s) {bad}")
            else:
                cid = eff.get("card_id") or eff.get("card")
                if cid not in ADD_CARD_CLASSES:
                    return f"add_card card '{cid}' (no C# token class registered)"
        if op == "generate_guest_star":
            unknown = set(eff) - GUEST_STAR_FIELDS
            if unknown:
                return (
                    "generate_guest_star field(s) "
                    f"{sorted(unknown)} not understood")
            if eff.get("rarity") not in {"common", "uncommon"}:
                return (
                    "generate_guest_star rarity "
                    f"'{eff.get('rarity')}'")
            rarity_rank = {"common": 0, "uncommon": 1, "rare": 2}
            if rarity_rank[eff["rarity"]] > rarity_rank.get(
                    card.get("rarity"), -1):
                return (
                    "generate_guest_star cannot create above generator rarity")
            if not isinstance(eff.get("amount", 1), int) \
                    or eff.get("amount", 1) <= 0:
                return "generate_guest_star amount must be a positive literal int"
            if eff.get("to", "hand") != "hand":
                return (
                    "generate_guest_star destination "
                    f"'{eff.get('to')}'")
            if "cost_override" in eff and not isinstance(
                    eff["cost_override"], int):
                return "generate_guest_star cost_override must be a literal int"
            if not card.get("exhaust"):
                return "generate_guest_star generator must Exhaust"
        if op == "conditional":
            unknown = set(eff) - CONDITIONAL_FIELDS
            if unknown:
                return f"conditional field(s) {sorted(unknown)} not understood"
            if predicate_cs(eff.get("if")) is None:
                return f"conditional predicate '{eff.get('if')}' (no verified C# read)"
            then, els = eff.get("then", []), eff.get("else", [])
            if any(e.get("op") == "repeat_this" for e in then + els):
                # Sim law (resolve_card): repeat_requested re-resolves the
                # effect list minus the repeat machinery. Codegen expresses
                # exactly the sheet's shape: a then-branch that IS the repeat.
                if len(then) != 1 or els:
                    return "repeat_this must be the conditional's entire then-branch"
                if not isinstance(then[0].get("times", 1), int):
                    return "repeat_this times must be a literal int"
                bad = [e["op"] for e in card["effects"]
                       if e is not eff and e["op"] not in REPEAT_SAFE_OPS]
                if bad:
                    return (f"repeat-conditional beside op(s) {sorted(set(bad))} "
                            "(repeated body would redeclare locals)")
            else:
                for branch in (then, els):
                    for e in branch:
                        reason = _branch_op_reason(e, "conditional branch")
                        if reason:
                            return reason
        if op == "choose_one":
            reason = _modal_reason(eff)
            if reason:
                return reason
    if sum(1 for e in card.get("effects", []) if e.get("op") == "choose_one") > 1:
        # One selection local per body (`modeIndex`), and one screen per play:
        # two modals on one card would collide on both.
        return "two choose_one effects on one card (mode selection collision)"
    if sum(1 for e in card.get("effects", []) if e.get("op") == "detonate") > 1:
        return "two detonate effects on one card (count variable collision)"
    if sum(1 for e in card.get("effects", [])
           if e.get("op") == "conditional"
           and any(x.get("op") == "repeat_this" for x in e.get("then", []))) > 1:
        return "two repeat-conditionals on one card (repeatTimes collision)"
    return None


def bomb_var(card: dict) -> str:
    """
    Which DynamicVar carries bomb damage.

    A card that both attacks and places a bomb needs two distinct numbers, and
    both cannot be "Damage" -- DynamicVarSet is keyed by name, so the second
    would overwrite the first. ExtraDamage is a real base-game var with its own
    accessor, so the loc system resolves {ExtraDamage} without inventing a
    custom name whose placeholder support is unverified.

    Cards that only place bombs keep plain Damage, which matches the
    hand-written Pop and keeps their card text reading naturally.
    """
    has_attack = any(
        e["op"] == "damage" and e["target"] != "self" for e in card.get("effects", [])
    )
    return "ExtraDamage" if has_attack else "Damage"


def fanfare_calc_rider(card: dict, eff: dict) -> tuple[int, int, int] | None:
    """Furina Legibility sprint (2026-07-24): a plain Fanfare damage rider
    (`N_per_M_fanfare`) rendered through the base game's CalculatedDamageVar so
    the card face / hover preview and the resolved hit share ONE value path --
    base + N*(Fanfare/M) -- instead of the display showing only the static base
    while PrintedDamage silently adds the rider at resolution (the playtest bug).

    Returns (base, per_n, fanfare_div) or None. Scope guards, both card-level so
    build_vars and build_body agree and no deferred modifier is dropped:
      * a non-self damage effect carrying an N_per_M_fanfare formula;
      * NOT a salon-deploy card -- the salon x3 replacement multiplier is the
        deferred entangled modifier, so those stay on the PrintedDamage path.
    The Spotlight PrintedDamage wrap this bypasses is identity for Furina's own
    cards (Center Stage does not scale her own numbers), so no resolved number
    changes."""
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    m = re.fullmatch(r"(\d+)_per_(\d+)_fanfare", eff.get("bonus_formula", ""))
    if not m:
        return None
    if salon_deploy_card(card):
        return None
    return int(eff["amount"]), int(m.group(1)), int(m.group(2))


def exhaust_pile_calc_rider(card: dict, eff: dict) -> tuple[int, int, str] | None:
    """`amount_formula: {base, per, count: exhaust_pile}` -- her finishers that
    read everything she has rotated off the line so far.

    Same CalculatedDamageVar path as the Charge and Fanfare riders, for the
    same reason: the pile grows all combat, so a face printing only `base`
    would understate the card by more than it states by the time anyone casts
    it. Only the exhaust_pile count is expressible; any other count token
    stays a named blocker rather than a guess.
    """
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    formula = eff.get("amount_formula")
    if not isinstance(formula, dict) or formula.get("count") != "exhaust_pile":
        return None
    return (int(formula.get("base", 0)), int(formula.get("per", 1)),
            "static (card, _) => "
            "KokomiResources.ExhaustPileCount(card.Owner.Creature)")


# EB-118. The `exhaust_selection_*` counts, tier0 token -> the C# accessor
# that answers it. Both sides derive every one of them from the same recorded
# descriptors (tier0 effects.exhaust_selection_counts /
# Powers/ExhaustSelection.cs), so a name here is a name there.
#
# Deliberately a CLOSED map, the same discipline RUNTIME_TIMES states: a count
# token the generator does not know must stay a NAMED BLOCKER. Guessing emits
# a card that compiles and pays its `base` forever while the face promises
# scaling, which is this generator's worst failure.
EXHAUST_SELECTION_COUNTS = {
    "exhaust_selection_size": "Size",
    "exhaust_selection_cost": "Cost",
    "exhaust_selection_attacks": "Attacks",
    "exhaust_selection_skills": "Skills",
    "exhaust_selection_powers": "Powers",
    "exhaust_selection_companions": "Companions",
    "exhaust_selection_personal": "Personal",
    "exhaust_selection_upgraded": "Upgraded",
}

# The clause each count renders on the face. The number itself is honest --
# it goes through the CalculatedDamageVar like every other converted rider --
# so this sentence only has to say WHY it moves.
EXHAUST_SELECTION_TEXT = {
    "exhaust_selection_size": "the number of cards you just "
                              "[gold]Exhausted[/gold]",
    "exhaust_selection_cost": "the total cost of the cards you just "
                              "[gold]Exhausted[/gold]",
    "exhaust_selection_attacks": "the Attacks you just [gold]Exhausted[/gold]",
    "exhaust_selection_skills": "the Skills you just [gold]Exhausted[/gold]",
    "exhaust_selection_powers": "the Powers you just [gold]Exhausted[/gold]",
    "exhaust_selection_companions": "the [gold]Companion[/gold] cards you just "
                                    "[gold]Exhausted[/gold]",
    "exhaust_selection_personal": "your own cards you just "
                                  "[gold]Exhausted[/gold]",
    "exhaust_selection_upgraded": "the upgraded cards you just "
                                  "[gold]Exhausted[/gold]",
}


def exhaust_selection_calc_rider(card: dict,
                                 eff: dict) -> tuple[int, int, str] | None:
    """`amount_formula: {base, per, count: exhaust_selection_*}` (EB-118) --
    a damage number priced off the selection the SAME card just Exhausted.

    Same CalculatedDamageVar path as the exhaust_pile rider beside it, and
    for a sharper version of the same reason: this count does not exist until
    the card resolves, so a face printing only `base` would be the only number
    the player ever sees. The reader is scoped to the resolving card, which is
    exactly the `card` a CalculatedVar multiplier is handed.

    Damage only, matching the pile rider: a block-side reader needs the
    CalculationBase plumbing `block_calc_rider` owns and has no card yet.
    """
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    formula = eff.get("amount_formula")
    if not isinstance(formula, dict):
        return None
    accessor = EXHAUST_SELECTION_COUNTS.get(formula.get("count"))
    if accessor is None:
        return None
    return (int(formula.get("base", 0)), int(formula.get("per", 1)),
            f"static (card, _) => ExhaustSelection.{accessor}(card)")


def discards_turn_calc_rider(card: dict,
                             eff: dict) -> tuple[int, int, str] | None:
    """`amount_formula: {base, per, count: discards_this_turn}` (EB-122, for
    EB-69's `what_the_tokoyo_took`) -- a damage number priced off what the
    seat has thrown away this turn.

    Same CalculatedDamageVar path as the exhaust-pile and exhaust-selection
    riders beside it, and the shape is not an invention: the base game's own
    MementoMori is `CalculationBase 9 + ExtraDamage 4 * (discards this turn)`,
    which is the triple this returns and the card tier0 names as the source of
    the token (`effects._formula_count`). The count only exists mid-turn, so a
    face printing only `base` would understate the card exactly when the
    Assist lane has done its work.

    Damage only, matching the two riders beside it: a block-side reader needs
    `block_calc_rider`'s CalculationBase plumbing and has no card yet.
    """
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    formula = eff.get("amount_formula")
    if not isinstance(formula, dict) \
            or formula.get("count") != "discards_this_turn":
        return None
    return (int(formula.get("base", 0)), int(formula.get("per", 1)),
            "static (card, _) => KokomiResources.DiscardsThisTurn(card)")


def charge_calc_rider(card: dict, eff: dict) -> tuple[int, int, int] | None:
    """Kokomi's Charge damage rider (`N_per_M_charge`), rendered through the
    base game's CalculatedDamageVar for exactly the reason Furina's Fanfare
    rider is (Legibility sprint, 2026-07-24): the face, the hover preview and
    the resolved hit must share ONE value path.

    This matters more for Charge than it did for Fanfare. The bank is uncapped
    and never spent, so by act 3 the rider is routinely larger than the printed
    base -- a face showing only the base would be understating the card by more
    than it states. `all_streams_flow` is her signature reader; if any card in
    the game has to print an honest number, it is that one.

    Returns (base, per_n, charge_div) or None.
    """
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    m = re.fullmatch(r"(\d+)_per_(\d+)_charge", eff.get("bonus_formula", ""))
    if not m:
        return None
    return int(eff["amount"]), int(m.group(1)), int(m.group(2))


def encore_calc_rider(card: dict, eff: dict) -> tuple[int, int, int] | None:
    """Curtain Call's Encore damage rider (`N_per_M_encore`), rendered through
    the same CalculatedDamageVar path as the Fanfare and Charge riders.

    Same argument as those two, and it binds hardest here: Encore is a buffer
    the player deliberately banks, so at the moment anyone casts Poised
    Riposte the rider is exactly the part they were planning around. A face
    printing only the base would understate the card precisely when the play
    matters. The bank is READ, never spent -- consulting it costs nothing.

    Returns (base, per_n, encore_div) or None.
    """
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    m = re.fullmatch(r"(\d+)_per_(\d+)_encore", eff.get("bonus_formula", ""))
    if not m:
        return None
    return int(eff["amount"]), int(m.group(1)), int(m.group(2))


def salon_member_calc_rider(card: dict, eff: dict) -> tuple[int, int, int] | None:
    """A13/A14 (2026-07-28): a per-Salon-member slope (`N_per_salon_member`).

    Grammar note: no `_M_` divisor, unlike the Fanfare/Charge/Encore riders.
    Those divide because they read a large pool where 1:1 would pay absurdly;
    the salon is a capped count of 3 (4 with A12's cap-raise), so every member
    is a full step. `_bonus_formula` in tier0/engine/effects.py splits the same
    two grammars the same way.

    Rendered through the Calculated var path rather than PrintedDamage for the
    Legibility-sprint reason: the whole POINT of the A13/A14 rework is that the
    pilot can see the stage paying. A face that printed only the base would
    hide exactly the number the rework exists to show, and would read
    identically to the threshold version it replaces.

    Returns (base, per_n, 1) -- the trailing 1 keeps the shape of the other
    riders' (base, per, divisor) triple; the multiplier lambda is the raw
    member count.
    """
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    m = re.fullmatch(r"(\d+)_per_salon_member", eff.get("bonus_formula", ""))
    if not m:
        return None
    # A deploy card scaling off the stage it is currently setting would read
    # its own arrival, so those stay on the replacement-multiplier path.
    if salon_deploy_card(card):
        return None
    return int(eff["amount"]), int(m.group(1)), 1


SALON_MEMBER_COUNT_CS = "SalonMemberPower.Count(card.Owner.Creature)"
# Fanfare rework Track C.3 (2026-07-28): Blocking Notes' slope. Mirrors the
# sim's `state.companion_plays_this_turn`, counting Guest Star token plays.
COMPANION_PLAYS_THIS_TURN_CS = (
    "CurtainCallHooks.CompanionPlaysThisTurn(card.Owner.Creature)")


def salon_deploy_card(card: dict) -> bool:
    """Salon-deploy cards render their replacement multiplier through
    `salon_calc_rider` instead of the other riders' path (their scaled value
    depends on the company, not on Spotlight/Fanfare), so the Spotlight and
    Fanfare predicates hand them off here."""
    return any(
        e.get("op") == "apply_power" and e.get("power") == "salon_member"
        for e in card.get("effects", []))


# The var each scaled op renders through, and which replacement constant
# scales it. Damage and block bow x3, every other numeric x2 -- the split the
# inline `(salonReplacements > 0 ? 3 : 1)` / `? 2 : 1` expressions encoded.
SALON_SCALED_VARS = {
    "block": ("CalculatedBlock", "ReplacementDamageMultiplier"),
    "damage": ("CalculatedDamage", "ReplacementDamageMultiplier"),
    # NOT "Cards": DynamicVarSet.Cards is a TYPED accessor that casts to
    # CardsVar, so a CalculatedVar under that name would throw on any read
    # through the property. "Encore"/"PowerAmount" have no typed accessor.
    "draw": ("DrawCards", "ReplacementNumericMultiplier"),
    "gain_encore": ("Encore", "ReplacementNumericMultiplier"),
    "apply_power": ("PowerAmount", "ReplacementNumericMultiplier"),
}


def _salon_calc_target(card: dict) -> tuple[dict, int, str, str] | None:
    """The ONE effect on a salon-deploy card whose printed number the
    replacement rule scales and which can render through a CalculatedVar:
    (effect, deploys before it, var name, multiplier constant).

    Only one, because `CalculatedDamageVar`, `CalculatedBlockVar` and the
    plain `CalculatedVar` all take their base term from the single
    `CalculationBase` var -- a second converted number on the same card would
    compute itself off the first one's base. First eligible effect wins; any
    others keep the inline `salonReplacements` expression (and their face
    keeps under-reporting, which is logged, not silently fixed).

    The deploy count must be STATIC: `WillReplace` is a closed form over the
    pre-play company size plus the deploys this card runs first, so an
    upgradeable deploy amount (a "PowerAmount" var on the deploy itself)
    disqualifies the card rather than guessing.
    """
    if not salon_deploy_card(card):
        return None
    effects = card.get("effects", [])
    deploys = 0
    for eff in effects:
        op = eff.get("op")
        if op == "apply_power" and eff.get("power") == "salon_member":
            if eff is power_upgrade_effect(card):
                return None              # deploy count is not static
            amount = eff.get("amount", 1)
            if not isinstance(amount, int):
                return None
            deploys += amount
            continue
        if deploys == 0:
            continue                     # nothing has bowed yet: not scaled
        if op not in SALON_SCALED_VARS:
            continue
        if op == "damage":
            # self-damage is unscaled; a card carrying its own rider would
            # need a compound multiplier (none exist -- salon cards are
            # excluded from the Fanfare/aura/Spotlight riders).
            if eff.get("target") == "self":
                continue
            if "bonus_formula" in eff or "bonus_vs_aura" in eff:
                continue
        if op == "apply_power":
            # PowerAmount is ours to own only if no OTHER effect already
            # claims it for its upgrade delta (DynamicVarSet throws on a
            # duplicate name -- the 2026-07-23 reward-screen softlock).
            upgrade_owner = power_upgrade_effect(card)
            if upgrade_owner is not None and upgrade_owner is not eff:
                continue
        if op == "draw":
            # A branch draw or an upgrade-added draw emits its own CardsVar;
            # two "Cards" vars is the same duplicate-name softlock.
            if added_draw_upgrade(card) or branch_draw_upgrade(card):
                continue
        if op == "gain_encore":
            # The ruled encore delta lands on EVERY gain_encore site, so the
            # var may only own the amount when there is exactly one site.
            if len([e for e in _effects_everywhere(card)
                    if e.get("op") == "gain_encore"]) != 1:
                continue
            if added_encore_upgrade(card):
                continue
        # One effect per op, so the converted number is unambiguous. The
        # deploys themselves are apply_power too, and never compete for the
        # var, so they do not count against a scaled power.
        if len([e for e in effects if e.get("op") == op
                and not (op == "apply_power"
                         and e.get("power") == "salon_member")]) != 1:
            continue
        var, mult = SALON_SCALED_VARS[op]
        return eff, deploys, var, mult
    return None


def salon_calc_rider(card: dict, eff: dict) -> tuple[int, int, str, str] | None:
    """Furina Legibility sprint, Track L-A4 (salon half): the effect scaled by
    the Salon replacement rule, rendered through a CalculatedVar so the card
    face shows the bowed-in value instead of the unscaled print.
    Returns (printed base, deploys before it, var name, multiplier constant).

    The multiplier calls `SalonMemberPower.ReplacementDelta`, which asks
    `SalonMemberPower.StageIsFull` -- the same predicate `Deploy`'s loop uses.
    One expression of the replacement rule, two readers.

    Timing note that the emission relies on: the card's own deploys mutate the
    company mid-resolution, so the body captures this value at the TOP of
    OnPlay, against the same pre-play state the preview reads.
    """
    target = _salon_calc_target(card)
    if target is None or eff is not target[0]:
        return None
    _, deploys, var, mult = target
    return int(eff["amount"]), deploys, var, mult


def rider_tip_args(card: dict) -> tuple[str, str]:
    """Track L-C: the C# arguments for the re-homed rider tips.

    Returns `(furina_args, kokomi_args)` -- the arguments for
    `FurinaRiderTips.ForCard` and for `KokomiRiderTips.ForChargeRider`
    respectively, each "" when that class has nothing to say. Two strings
    rather than one because the tip helpers are per-character classes, and a
    Charge rate has no business being explained by Furina's helper; the
    SCAN is shared because "which rider did this card convert" is one
    question about one sheet vocabulary.

    Only riders that were CONVERTED get a tip, because only those have had
    their arithmetic removed from the card text. An unconverted rider (the
    Bomb-detonation formula, an AoE aura rider) keeps its full sentence on the
    face, so re-homing it would delete the only place the player could read
    it."""
    args = []
    kokomi_args = []
    for eff in card.get("effects", []):
        # B1: a converted BLOCK rider has had its arithmetic removed from the
        # face exactly as a converted damage rider has, so it earns the same
        # tip. Without this the fix would trade a silent drop for a silent
        # number -- "{CalculatedBlock}" with nothing saying where it came from.
        if calc_rider(card, eff) is None \
                and block_calc_rider(card, eff) is None:
            continue
        m = re.fullmatch(r"(\d+)_per_(\d+)_fanfare", eff.get("bonus_formula", ""))
        members = re.fullmatch(r"(\d+)_per_salon_member",
                               eff.get("bonus_formula", ""))
        companions = re.fullmatch(r"(\d+)_per_companion_played_this_turn",
                                  eff.get("bonus_formula", ""))
        # L4b: Kokomi's Charge rider took the same bargain as the Fanfare one
        # -- the face was cut to "Scales with Charge" and the arithmetic
        # renders inside {CalculatedDamage} -- but no branch here matched
        # `N_per_M_charge`, so the RATE was printed nowhere at all: not on the
        # face, not in a tip. The player could see a number move and never
        # learn what moved it.
        charge = re.fullmatch(r"(\d+)_per_(\d+)_charge",
                              eff.get("bonus_formula", ""))
        if m:
            args.append(f"fanfarePer: {int(m.group(1))}")
            args.append(f"fanfareStep: {int(m.group(2))}")
            if eff.get("op") == "block":
                # Same noun rule as the salon rider below: a Block-granting
                # fanfare rider must not read "+N damage" on hover (SYS-7).
                args.append("grantsBlock: true")
        elif members:
            # A13/A14: same re-homing bargain as the Fanfare rider. The face
            # keeps a short marker, the RATE and what the stage is paying
            # right now live here.
            args.append(f"salonPer: {int(members.group(1))}")
            if eff.get("op") == "block":
                args.append("salonGrantsBlock: true")
        elif companions:
            # Track C.3: same bargain again. The face says it scales; the tip
            # carries the rate and the live count.
            args.append(f"companionPer: {int(companions.group(1))}")
        elif charge:
            # Same two arguments the Fanfare rider takes, and for the same
            # reason: a rate is a numerator AND a denominator, and "+1 per
            # Charge" is a different card from "+1 per 2 Charge".
            kokomi_args.append(f"chargePer: {int(charge.group(1))}")
            kokomi_args.append(f"chargeStep: {int(charge.group(2))}")
            if eff.get("op") == "block":
                # EB-122 / SYS-7, one meter over: `gyorin_formation` is the
                # first Charge rider on a BLOCK op, and this tip is the only
                # surface carrying the rate. Without the noun it would be the
                # single place a player can read it and would say "damage".
                kokomi_args.append("chargeGrantsBlock: true")
        elif "bonus_vs_aura" in eff:
            args.append(f"auraBonus: {int(eff['bonus_vs_aura'])}")
    return ", ".join(args), ", ".join(kokomi_args)


def merged_deploy_text(card: dict) -> tuple[dict[int, int], set[int]]:
    """B5: consecutive deploys of the SAME member render as one sentence.

    Grand Gala deploys Crabaletta twice in a row, which read as "Add 1
    Mademoiselle Crabaletta. Add 1 Mademoiselle Crabaletta." -- the same
    boilerplate this ruling is deleting, wearing a name.

    Returns ({index of the surviving effect: merged amount},
             {indices to skip}), keyed by position in card["effects"].

    TEXT ONLY. The body still emits one Deploy call per effect, because the
    replacement rule bows a member out per deploy and collapsing the calls
    would change what the card does. Merging is refused unless BOTH effects
    carry a literal integer amount and neither is the card's upgrade target
    or a salon-scaled var -- those render a token, not a number, and two
    tokens cannot be added at generation time.
    """
    effects = card.get("effects", [])
    upgrade_target = power_upgrade_effect(card)
    merged: dict[int, int] = {}
    skip: set[int] = set()

    def plain_deploy(eff):
        return (eff.get("op") == "apply_power"
                and eff.get("power") == "salon_member"
                and isinstance(eff.get("amount"), int)
                and eff is not upgrade_target
                and salon_calc_rider(card, eff) is None)

    anchor = None
    for i, eff in enumerate(effects):
        if not plain_deploy(eff):
            anchor = None
            continue
        if (anchor is not None
                and effects[anchor].get("member") == eff.get("member")):
            merged[anchor] += int(eff["amount"])
            skip.add(i)
            continue
        anchor = i
        merged[i] = int(eff["amount"])
    return merged, skip


def salon_member_tip_args(card: dict) -> str:
    """B5: the C# arguments naming which member tips this card carries, or "".

    A random deploy passes `randomMember: true` and the tip helper shows all
    three -- the player is choosing to roll and needs to know the field.
    Order follows the card's own effects so a multi-deploy card's tips read in
    the order it summons them.
    """
    members: list[str] = []
    random_deploy = False
    for eff in card.get("effects", []):
        if eff.get("op") != "apply_power" or eff.get("power") != "salon_member":
            continue
        member = eff.get("member", "crabaletta")
        if member == "random":
            random_deploy = True
        elif SALON_MEMBER_CS[member] not in members:
            members.append(SALON_MEMBER_CS[member])
    if random_deploy:
        return "randomMember: true"
    if not members:
        return ""
    return "members: new[] { " + ", ".join(members) + " }"


def salon_scaled_snapshot(card: dict) -> str | None:
    """The C# local a converted salon card captures before its first deploy,
    or None. Named per var so the body reads plainly."""
    target = _salon_calc_target(card)
    if target is None:
        return None
    return "salonScaled" + target[2].removeprefix("Calculated")


def aura_calc_rider(card: dict, eff: dict) -> tuple[int, int] | None:
    """Furina Legibility sprint, pass 2: a SINGLE-TARGET `bonus_vs_aura` rider
    rendered through CalculatedDamageVar. Returns (base, bonus) or None.

    This is the shape CalculatedVar was built for: `Calculate(target)` receives
    the hovered creature during preview and the real one at resolution, so the
    face greens exactly when you hover an aura'd enemy and the hit agrees.

    AoE (`target: all_enemies`) is deliberately EXCLUDED, and not merely as a
    display nicety: those cards emit a per-target `foreach` that re-tests
    `AuraCmd.Find` for each enemy, whereas AttackCommand resolves a
    CalculatedDamageVar once with `singleTarget == null`. Converting them would
    collapse a per-enemy decision into one flat value -- a real gameplay change
    (Furina's crashing_waves, Klee's flame_dance). They stay as they are."""
    if eff.get("op") != "damage" or eff.get("target") != "enemy":
        return None
    if "bonus_vs_aura" not in eff:
        return None
    if salon_deploy_card(card):
        return None
    return int(eff["amount"]), int(eff["bonus_vs_aura"])


def spotlight_calc_rider(card: dict, eff: dict) -> tuple[int, int] | None:
    """Furina Legibility sprint, pass 3 (Track L-A4): a COMPANION card's plain
    damage rendered through CalculatedDamageVar so the Spotlight GuestCast
    scaling (1.5x + flat) shows on the face and the enemy hover instead of only
    at resolution. Returns (base, 1) or None.

    Companions only. On Furina's own cards the `PrintedDamage` wrap is identity
    -- its bonus path needs `Mode == GuestCast`, and under GuestCast
    `IsSpotlighted` accepts only `ICompanionCard` -- so converting them would
    add a var for no visible change.

    Only the plain shape: a card carrying its own rider (bonus_formula /
    bonus_vs_aura) already owns the CalculatedDamageVar for that rider, and the
    two cannot share one var. None exist today; the guard keeps it that way.
    """
    if not is_companion(card):
        return None
    if eff.get("op") != "damage" or eff.get("target") == "self":
        return None
    if "bonus_formula" in eff or "bonus_vs_aura" in eff:
        return None
    if salon_deploy_card(card):
        return None
    return int(eff["amount"]), 1


def spotlight_block_rider(card: dict, eff: dict) -> int | None:
    """Track L-A4, block half: a COMPANION card's block rendered through the
    base game's `CalculatedBlockVar` so the Spotlight GuestCast scaling shows on
    the face. Returns the printed base, or None.

    `CalculatedBlockVar` is the exact block twin of `CalculatedDamageVar` --
    it overrides UpdateCardPreview to run `Hook.ModifyBlock`, so block-modifying
    powers still reach the preview. It reads `CalculationBase` + `CalculationExtra`.

    Excluded: a card whose DAMAGE already converts. `CalculatedDamageVar` and
    `CalculatedBlockVar` both take their base from the single `CalculationBase`
    var, so a card doing both would compute its block off the damage base.
    freminet_pressurized_floe is the only one, and its damage conversion wins.
    Also excluded: more than one block effect (same collision), and salon-deploy
    cards (the x3 replacement multiplier is still inline)."""
    if not is_companion(card) or eff.get("op") != "block":
        return None
    if salon_deploy_card(card):
        return None
    effects = card.get("effects", [])
    if sum(1 for e in effects if e.get("op") == "block") != 1:
        return None
    if any(calc_rider(card, e) is not None for e in effects):
        return None
    return int(eff["amount"])


def block_calc_rider(card: dict, eff: dict) -> tuple[int, int, str] | None:
    """B1 (playtest-2, 2026-07-28): a scaling rider on a BLOCK op, rendered
    through `CalculatedBlockVar`. Returns (base, extra, multiplier-lambda) or
    None -- the block twin of `calc_rider`, and the same one-predicate-four-
    sites discipline.

    THE DEFECT THIS CLOSES. Every rider predicate in this file gated on
    `op != "damage"`, because until Curtain Call C every rider in the pool
    was a damage rider. Thunderous Ovation hung `1_per_2_fanfare` on a
    *block* op and the generator dropped it without a word: the sheet said
    "6, +1 per 2 Fanfare", the card gave a flat 6, and the playtest reported
    exactly that ("just gave 6 block"). The sim had implemented the rider all
    along, so this was a pure C#-side silent drop.

    The rail already existed -- `spotlight_block_rider` renders companion
    block this way and `salon_calc_rider` renders usher's -- so this adds a
    predicate, not a mechanism.

    Guards mirror `spotlight_block_rider`'s, and for the same reason:
    `CalculationBase` is a SINGLE var, so a card converting two numbers
    through it would compute one off the other's base.
    """
    if eff.get("op") != "block":
        return None
    formula = eff.get("bonus_formula", "")
    m = re.fullmatch(r"(\d+)_per_(\d+)_fanfare", formula)
    # A13 (2026-07-28): the per-member slope rides the same rail on a block op
    # -- Dinner Service is its first card, and the whole point of the rework is
    # that the face shows the stage paying.
    members = re.fullmatch(r"(\d+)_per_salon_member", formula)
    # Fanfare rework Track C.3 (2026-07-28): Blocking Notes' Companion-tempo
    # slope, the third shape on this same rail. Counted per PLAY this turn,
    # including Guest Star token plays -- see the sheet row for why the B2
    # printed-cost lesson does not apply to a payoff.
    companions = re.fullmatch(r"(\d+)_per_companion_played_this_turn", formula)
    # EB-122 (`gyorin_formation`, EB-69's fill): Kokomi's Charge slope on a
    # BLOCK op -- the fourth shape on this rail and the block twin of
    # `charge_calc_rider`. It carries that rider's argument in its sharper
    # form: the bank is uncapped and never spent, so by act 3 the rider is
    # routinely larger than the printed base. Nothing read the formula before,
    # so the card would have rendered and paid a flat 6 -- which is why
    # `blocked_reason` refused to emit it rather than ship a wrong number.
    charge = re.fullmatch(r"(\d+)_per_(\d+)_charge", formula)
    if not m and not members and not companions and not charge:
        return None
    if salon_deploy_card(card):
        return None
    effects = card.get("effects", [])
    if sum(1 for e in effects if e.get("op") == "block") != 1:
        return None
    # Damage conversions and the two other block conversions all claim
    # CalculationBase; whichever the card already has wins and this stays off.
    if any(calc_rider(card, e) is not None for e in effects):
        return None
    if any(spotlight_block_rider(card, e) is not None
           or salon_calc_rider(card, e) is not None for e in effects):
        return None
    if members:
        return int(eff["amount"]), int(members.group(1)), (
            f"static (card, _) => {SALON_MEMBER_COUNT_CS}")
    if companions:
        return int(eff["amount"]), int(companions.group(1)), (
            f"static (card, _) => {COMPANION_PLAYS_THIS_TURN_CS}")
    if charge:
        return int(eff["amount"]), int(charge.group(1)), (
            "static (card, _) => "
            f"KokomiResources.GetCharge(card.Owner.Creature) "
            f"/ {int(charge.group(2))}")
    return int(eff["amount"]), int(m.group(1)), (
        "static (card, _) => "
        f"FurinaResources.ReadableFanfare(card.Owner.Creature) / {int(m.group(2))}")


def calc_rider(card: dict, eff: dict) -> tuple[int, int, str] | None:
    """Unified view of every damage rider that renders through a
    CalculatedDamageVar: (base, extra, multiplier-lambda source). The four
    emission sites -- vars, OnPlay, description token, upgrade target -- all key
    off this one predicate so they cannot disagree about which shape a card is.
    The multiplier func must be static (CalculatedVar rejects instance targets).
    """
    fanfare = fanfare_calc_rider(card, eff)
    if fanfare is not None:
        base, per_n, div = fanfare
        return base, per_n, (
            "static (card, _) => "
            f"FurinaResources.ReadableFanfare(card.Owner.Creature) / {div}")
    pile = exhaust_pile_calc_rider(card, eff)
    if pile is not None:
        return pile
    selection = exhaust_selection_calc_rider(card, eff)
    if selection is not None:
        return selection
    discards = discards_turn_calc_rider(card, eff)
    if discards is not None:
        return discards
    charge = charge_calc_rider(card, eff)
    if charge is not None:
        base, per_n, div = charge
        return base, per_n, (
            "static (card, _) => "
            f"KokomiResources.GetCharge(card.Owner.Creature) / {div}")
    encore = encore_calc_rider(card, eff)
    if encore is not None:
        base, per_n, div = encore
        return base, per_n, (
            "static (card, _) => "
            f"FurinaResources.Encore(card.Owner.Creature) / {div}")
    members = salon_member_calc_rider(card, eff)
    if members is not None:
        base, per_n, _ = members
        return base, per_n, f"static (card, _) => {SALON_MEMBER_COUNT_CS}"
    aura = aura_calc_rider(card, eff)
    if aura is not None:
        base, bonus = aura
        # Guard the null: preview calls Calculate(null) whenever nothing is
        # hovered, and AuraCmd.Find would throw on it.
        return base, bonus, (
            "static (_, target) => "
            "target != null && AuraCmd.Find(target) != null ? 1 : 0")
    spotlight = spotlight_calc_rider(card, eff)
    if spotlight is not None:
        base, extra = spotlight
        # base + 1 * (PrintedDamage(base) - base) == PrintedDamage(base):
        # the same number the card resolves today, now also the number it
        # prints. The delta lives in SpotlightSystem so the arithmetic has
        # exactly one home.
        return base, extra, (
            "static (card, _) => SpotlightSystem.PrintedDamageDelta(card)")
    return None


def salon_calc_var_decls(card: dict, eff: dict) -> list[str] | None:
    """The CalculationBase + extra + CalculatedVar trio for a salon-scaled
    number, or None. Damage reads its extra term from `ExtraDamage` (that is
    what `CalculatedDamageVar.GetExtraVar` overrides to); everything else
    reads `CalculationExtra`."""
    rider = salon_calc_rider(card, eff)
    if rider is None:
        return None
    base, deploys, var, mult = rider
    calc = (
        f"new {var}Var(ValueProp.Move)"
        if var in ("CalculatedDamage", "CalculatedBlock")
        else f'new CalculatedVar("{var}")')
    return [
        f'new CalculationBaseVar({base}m)',
        ('new ExtraDamageVar(1m)' if var == "CalculatedDamage"
         else 'new CalculationExtraVar(1m)'),
        f'{calc}.WithMultiplier(static (card, _) => '
        f'SalonMemberPower.ReplacementDelta(card, {deploys}, '
        f'SalonConstants.{mult}))',
    ]


def build_vars(card: dict) -> list[str]:
    """DynamicVar declarations, in the order the effects use them."""
    out = []
    for eff in card["effects"]:
        op = eff["op"]
        salon_decls = salon_calc_var_decls(card, eff)
        if salon_decls is not None:
            out.extend(salon_decls)
            continue
        # Constructor shapes differ per var and are NOT uniform: DamageVar and
        # BlockVar take (decimal, ValueProp); CardsVar takes a bare int;
        # HpLossVar takes a bare decimal. Verified against the decompiled
        # sts2 sources -- assuming a uniform shape here does not compile.
        if op == "damage" and eff["target"] == "self":
            out.append(f'new HpLossVar({eff["amount"]}m)')
        elif op == "damage":
            rider = calc_rider(card, eff)
            if rider is not None:
                base, extra, mult = rider
                # PerfectedStrike idiom: base + extra * multiplier, so the
                # face/preview (:diff green) and the hit resolve identically.
                out.append(f'new CalculationBaseVar({base}m)')
                out.append(f'new ExtraDamageVar({extra}m)')
                out.append(
                    'new CalculatedDamageVar(ValueProp.Move)'
                    f'.WithMultiplier({mult})')
            elif eff is not damage_var_effect(card):
                pass          # literal; only the upgraded hit declares a var
            else:
                out.append(f'new DamageVar({eff["amount"]}m, ValueProp.Move)')
                if "bonus_formula" in eff and bonus_per_upgrade(card):
                    n = int(eff["bonus_formula"].partition("_per_")[0])
                    out.append(f'new DynamicVar("BonusPer", {n}m)')
            # An upgradeable HIT COUNT is independent of the damage var: A5's
            # Undercurrent upgrades times (3 -> 5) and leaves the per-hit 2
            # alone, so this is not an `elif` on the branches above.
            if eff is times_var_effect(card):
                out.append(f'new DynamicVar("Times", {eff["times"]}m)')
        elif op == "block":
            block_rider = block_calc_rider(card, eff)
            block_base = spotlight_block_rider(card, eff)
            if block_rider is not None:
                base, extra, mult = block_rider
                out.append(f'new CalculationBaseVar({base}m)')
                out.append(f'new CalculationExtraVar({extra}m)')
                out.append(
                    'new CalculatedBlockVar(ValueProp.Move)'
                    f'.WithMultiplier({mult})')
            elif block_base is not None:
                # Mirage idiom: base + 1 * (PrintedBlock(base) - base), which
                # is PrintedBlock(base) -- the number the card already gains,
                # now also the number it prints.
                out.append(f'new CalculationBaseVar({block_base}m)')
                out.append('new CalculationExtraVar(1m)')
                out.append(
                    'new CalculatedBlockVar(ValueProp.Move).WithMultiplier('
                    'static (card, _) => '
                    'SpotlightSystem.PrintedBlockDelta(card))')
            else:
                out.append(f'new BlockVar({eff["amount"]}m, ValueProp.Move)')
        elif op == "draw":
            out.append(f'new CardsVar({int(eff["amount"])})')
        elif op == "discard" and plain_discard_upgrade(card):
            # G6: only an UPGRADEABLE plain discard needs a var, so every
            # existing card keeps its literal and its generated file does not
            # churn. "Discards" collides with no base-game var name (CardsVar
            # is `Cards`, and this card already spends that on its draw).
            out.append(f'new DynamicVar("Discards", {int(eff["amount"])}m)')
        elif op == "place_bomb":
            if bomb_var(card) == "ExtraDamage":
                out.append(f'new ExtraDamageVar({eff["bomb_damage"]}m)')
            else:
                out.append(f'new DamageVar({eff["bomb_damage"]}m, ValueProp.Move)')
            if isinstance(eff.get("amount"), str) and bombs_upgrade(card):
                # X_plus_N with a ruled bombs delta: the +N renders/upgrades.
                n = int(eff["amount"][len("X_plus_"):])
                out.append(f'new DynamicVar("Bombs", {n}m)')
        elif op == "gain_spark" and spark_upgrade(card):
            # Only an upgradeable spark amount needs a var (the new value must
            # render); "Sparks" collides with no base-game var name. Cards
            # without a sheet upgrade keep the literal (see MECHANICAL_OPS).
            out.append(f'new DynamicVar("Sparks", {int(eff["amount"])}m)')
        elif op == "summon_kurage" and kurage_turns_upgrade(card):
            # Same rule as Sparks/BurstEnergy: a var ONLY when the upgrade has
            # to render. Duration is the only thing bake_kurage's upgrade may
            # move -- the pulse numbers are constants and the +1 Charge is
            # untouchable under the resource-curve law -- so one var covers it.
            out.append(
                f'new DynamicVar("KurageTurns", {int(eff.get("amount", 1))}m)')
        elif op == "energy" and energy_upgrade(card):
            out.append(f'new DynamicVar("Energy", {int(eff["amount"])}m)')
        elif op == "block_next_turn" and block_next_turn_upgrade(card):
            out.append(
                f'new DynamicVar("BlockNextTurn", {int(eff["amount"])}m)')
        elif op == "exhaust_from" and exhaust_upgrade(card):
            out.append(
                f'new DynamicVar("Exhausts", {int(eff.get("amount", 1))}m)')
        elif op == "burst_energy" and burst_upgrade(card):
            # Same rule as Sparks: a var only when the upgrade must render.
            out.append(f'new DynamicVar("BurstEnergy", {int(eff["amount"])}m)')
        elif op == "raise_fanfare_cap":
            out.append(
                f'new DynamicVar("FanfareCap", {int(eff["amount"])}m)')
        elif op == "crash_fanfare":
            # Always a var: the Hyperbeam's upgrade IS this number (the
            # floor_drop delta), so the upgraded face has to render it.
            out.append(
                f'new DynamicVar("FloorDrop", {int(eff["amount"])}m)')
        elif op == "gain_fanfare_floor":
            # Always a var, never a literal: BOTH sheet cards carrying this op
            # have a fanfare_floor upgrade delta, so the new value must render
            # on the upgraded card. (G-A2.)
            out.append(
                f'new DynamicVar("FanfareFloor", {int(eff["amount"])}m)')
        elif op == "heal":
            out.append(f'new DynamicVar("Heal", {int(eff["amount"])}m)')
        elif op in POWER_UPGRADE_OPS and eff is power_upgrade_effect(card):
            # Same rule again: only an upgradeable amount needs a var, and
            # only the ONE effect the sim's delta binds to may own it -- a
            # second apply_power on the same card must stay a literal, or the
            # duplicate "PowerAmount" key throws in the DynamicVarSet
            # constructor at reward time (2026-07-23 softlock).
            out.append(f'new DynamicVar("PowerAmount", {int(eff["amount"])}m)')
        elif op == "discard_for_sparks" and discard_upgrade(card) != (0, 0):
            # R36: both numbers render, so both become vars together.
            out.append(f'new DynamicVar("Discards", {int(eff["amount"])}m)')
            out.append(f'new DynamicVar("Sparks", {int(eff["sparks"])}m)')
        elif op in BONUS_OPS and "bonus" in eff and bonus_upgrade(card):
            # Same rule as Sparks: a var only when the upgrade must render.
            out.append(f'new DynamicVar("Bonus", {int(eff["bonus"])}m)')
        elif op == "chance_bomb_per_detonation" and chance_upgrade(card):
            # Rendered as a PERCENT (50 -> 75); the body divides by 100.
            out.append(
                f'new DynamicVar("Chance", {int(round(float(eff["chance"]) * 100))}m)')
        elif op == "add_card" and stash_upgrade(card):
            out.append(f'new DynamicVar("Stash", {int(eff.get("amount", 1))}m)')
        elif op == "conditional":
            # Branch amounts are literals unless a ruled delta targets them:
            # conditional_bonus -> then-first damage (ExtraDamage), draw ->
            # branch draws (Cards then / DrawElse else). repeat-conditionals
            # carry no numbers of their own.
            if any(e.get("op") == "repeat_this" for e in eff.get("then", [])):
                continue
            cb = conditional_bonus_upgrade(card)
            bd = branch_draw_upgrade(card)
            then_var, else_var = branch_draw_vars(card)
            for e in eff.get("then", []):
                if e["op"] == "damage" and cb:
                    out.append(f'new ExtraDamageVar({e["amount"]}m)')
                    cb = 0                       # first damage only
                elif e["op"] == "draw" and bd:
                    out.append(
                        f'new CardsVar({int(e["amount"])})'
                        if then_var == "Cards"
                        else f'new DynamicVar("{then_var}", '
                             f'{int(e["amount"])}m)')
            for e in eff.get("else", []):
                if e["op"] == "draw" and bd:
                    out.append(
                        f'new DynamicVar("{else_var}", {int(e["amount"])}m)')
    if added_draw_upgrade(card):
        out.append(f"new CardsVar({added_draw_upgrade(card)})")
    if added_encore_salon(card) is not None:
        base, deploys = added_encore_salon(card)
        # Same trio as salon_calc_var_decls, for the upgrade-appended encore
        # (SYS-6). The trio owns CalculationBase; a card whose base effects
        # already declare it cannot also express the appended encore this
        # way -- loud, not silent, or SYS-6 re-ships the day such a card is
        # authored.
        if any("CalculationBaseVar(" in d for d in out):
            raise SystemExit(
                f"gen_klee_cards: {card['id']}: upgrade-appended encore "
                "needs the CalculationBase trio but another effect already "
                "owns it")
        out.append(f'new CalculationBaseVar({base}m)')
        out.append('new CalculationExtraVar(1m)')
        out.append(
            'new CalculatedVar("Encore").WithMultiplier(static (card, _) => '
            f'SalonMemberPower.ReplacementDelta(card, {deploys}, '
            'SalonConstants.ReplacementNumericMultiplier))')
    # DynamicVarSet's constructor throws on a duplicate name, and it runs
    # inside CardFactory.CreateForReward -- a collision is a reward-screen
    # softlock on whatever run happens to roll the card. Fail the GENERATOR
    # instead. Typed vars carry their class-derived name (DamageVar ->
    # "Damage"), named vars declare theirs.
    names = [
        (m.group(1)
         if (m := re.search(r'(?:DynamicVar|CalculatedVar)\("(\w+)"', decl))
         else re.match(r"new (\w+?)Var\(", decl).group(1))
        for decl in out
    ]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        raise SystemExit(
            f"gen_klee_cards: {card['id']}: duplicate DynamicVar name(s) "
            f"{dupes} -- DynamicVarSet throws at reward time "
            "(2026-07-23 softlock).")
    return out


_upgrade_deltas: dict | None = None


def upgrade_deltas() -> dict:
    """Per-card delta maps, merged across the upgrade sheets exactly as
    tier0/content/upgrades.py._upgrade_index does (R20: the upgrade sheets are
    the only home for deltas; inline `upgrade:` keys block the card).

    Two sheets since the Fontaine companions entered Klee's reward slot
    (2026-07-21 ruling): their deltas live in furina-upgrades.yaml, and the
    sim merges both, so a generator reading only klee-upgrades.yaml would emit
    unupgradeable cards the sim happily smiths. Duplicate ids across sheets are
    a hard error on the sim side; mirrored here rather than silently
    last-wins.
    """
    global _upgrade_deltas
    if _upgrade_deltas is None:
        merged: dict = {}
        for sheet in UPGRADE_SHEETS:
            if not sheet.exists():
                continue
            entries = yaml.safe_load(sheet.read_text(encoding="utf-8")) or {}
            dupes = set(entries) & set(merged)
            if dupes:
                raise SystemExit(
                    f"gen_klee_cards: {sheet.name}: duplicate upgrade ids "
                    f"{sorted(dupes)} -- the sim raises on this too.")
            merged.update(entries)
        _upgrade_deltas = merged
    return _upgrade_deltas


def upgrade_plan(card: dict) -> tuple[dict, str | None]:
    """(deltas, None) when every ruled delta key is expressible on this card,
    ({}, reason) otherwise.

    Partial application is forbidden (R24): expressing half a ruled upgrade
    silently approximates the other half, which is exactly the failure mode
    the UNAPPLIABLE discipline exists to prevent. A card with an inexpressible
    key gets no upgrade lines at all and a manifest flag naming the key.
    """
    deltas = upgrade_deltas().get(card["id"])
    if not deltas:
        return {}, "no ratified delta in klee-upgrades.yaml"
    effects = card.get("effects", [])
    # Branch effects too: tier0's `everywhere` (draw deltas bump ALL draw
    # ops, branches included -- "both branches" is sheet law).
    everywhere = list(effects)
    for e in effects:
        if e.get("op") == "conditional":
            everywhere.extend(e.get("then", []))
            everywhere.extend(e.get("else", []))
    non_repeat_conditionals = [
        e for e in effects
        if e.get("op") == "conditional"
        and not any(x.get("op") == "repeat_this" for x in e.get("then", []))]
    # EB-140. Computed once, used twice: as the `has` booleans below and as
    # the REASON the loop reports, so an unemittable shape says which shape it
    # was instead of the generic sheet/card-mismatch line.
    cond_reason = {k: _conditional_delta_reason(card, k, deltas)
                   for k in _CONDITIONAL_DELTA_OPS if k in deltas}
    has = {
        "damage": any(e["op"] == "damage" and e["target"] != "self" for e in effects),
        "block": any(e["op"] == "block" for e in effects),
        "draw": any(e["op"] == "draw" for e in everywhere),
        # conditional_bonus: tier0 bumps the then-branch's first damage|block;
        # codegen expresses the damage form (ExtraDamage var). A then-block
        # first would need a second Block var -- structural until needed.
        "conditional_bonus": any(
            next((x for x in c.get("then", [])
                  if x.get("op") in ("damage", "block")), {}
                 ).get("op") == "damage"
            for c in non_repeat_conditionals),
        # EB-140: whole-card expressibility, not a single presence test --
        # these keys bump EVERY matching op, so every one of them has to have
        # somewhere to render.
        "conditional_block": cond_reason.get("conditional_block") is None,
        "conditional_damage": cond_reason.get("conditional_damage") is None,
        "condition": bool(non_repeat_conditionals),
        # bombs: tier0 rewrites X_plus_N -> X_plus_(N+val).
        "bombs": any(e["op"] == "place_bomb"
                     and isinstance(e.get("amount"), str) for e in effects),
        # bonus_per_detonation: tier0 rewrites the bonus_formula's N.
        "bonus_per_detonation": any("bonus_formula" in e for e in effects),
        # bonus_slope: the same rewrite under the name new rows use. See
        # upgrades.py, where one branch serves both keys.
        "bonus_slope": any("bonus_formula" in e for e in effects),
        # floor_drop: tier0 bumps the crash_fanfare amount, and the value
        # renders off the FloorDrop var the op already emits.
        "floor_drop": any(e["op"] == "crash_fanfare" for e in effects),
        # cards: tier0 bumps the add_card amount.
        "cards": any(e["op"] == "add_card" for e in effects),
        # remove: value-checked in the loop below, which owns the whole key
        # because WHICH field must be present depends on the VALUE
        # ('exhaust' and 'ethereal' land; 'self_damage' remains structural).
        "remove": False,
        # copy_cost_override: play-time IsUpgraded read in the copy emission.
        "copy_cost_override": any(e["op"] == "copy_companion_in_hand"
                                  for e in effects) or any(
            e["op"] == "copy_spotlighted_in_hand" for e in effects),
        "generate_cost_override": any(
            e["op"] == "generate_guest_star" for e in effects),
        "spark": any(e["op"] == "gain_spark" for e in effects),
        "encore": any(e["op"] == "gain_encore" for e in everywhere),
        "encore_cost": int(card.get("encore_cost", 0)) > 0,
        "fanfare_cost": int(card.get("fanfare_cost", 0)) > 0,
        "fanfare_cap": any(e["op"] == "raise_fanfare_cap" for e in effects),
        # G-A2. upgrades.py binds this delta to the first TOP-LEVEL
        # gain_fanfare_floor, so `effects` (not `everywhere`) is the right
        # scope -- a floor grant nested inside a conditional would not be the
        # one the sim bumps, and pretending otherwise would silently upgrade
        # the wrong branch.
        "fanfare_floor": any(
            e["op"] == "gain_fanfare_floor" for e in effects),
        "heal": any(e["op"] == "heal" for e in effects),
        "bomb_damage": any(e["op"] == "place_bomb" for e in effects),
        "burst_energy": any(e["op"] == "burst_energy" for e in effects),
        "cost": str(card.get("cost")) != "X",
        # R36: both keys ride the one discard_for_sparks effect.
        # G6 (Neap Tide v2.1) also lets `discard` bind the PLAIN discard op,
        # which Kokomi's Sly lane uses and Klee's Spark lane does not. Mirrors
        # tier0/content/upgrades.py, which tries discard_for_sparks FIRST and
        # falls back -- the two appliers must agree on which effect a delta
        # lands on or the generated card and the simulated card upgrade
        # differently, which no test would catch by value.
        "discard": any(e["op"] in ("discard_for_sparks", "discard")
                       for e in effects),
        "sparks": any(e["op"] == "discard_for_sparks" for e in effects),
        # R37: card-level, any card can become Innate or Retain.
        "innate": True,
        "retain": True,
        # Bomb-op batch: bonus rides a bonus-carrying bomb op; chance is
        # the chance_bomb_per_detonation replacement.
        "bonus": any(e["op"] in BONUS_OPS and "bonus" in e for e in effects),
        "chance": any(e["op"] == "chance_bomb_per_detonation" for e in effects),
        # Structural `add` upgrades are validated by VALUE below, not here:
        # which shapes are expressible depends on the added op and on what the
        # base card already declares, so the whole key is owned by the loop.
        "add": True,
        # EB-122. Position modifier for `add`; its requirement is that the
        # named op is on the card, which is keyed by VALUE and checked below.
        "add_before": True,
        # Kokomi. Each binds to the op that owns the number, so a delta on a
        # card without that op is still reported unexpressible rather than
        # silently dropped on the floor.
        "kurage_turns": any(e["op"] == "summon_kurage" for e in effects),
        "energy": any(e["op"] == "energy" for e in effects),
        "block_next_turn": any(e["op"] == "block_next_turn" for e in effects),
        # Only the CHOSEN branch: raising a RANDOM exhaust_from above 1 has no
        # C# path (the re-pooling loop was never built), so such a card must
        # stay unexpressible and loudly blocked rather than generate wrong.
        "exhaust": any(e["op"] == "exhaust_from"
                       and e.get("select") == "chosen" for e in effects),
        # times: tier0 bumps the first damage|apply_power op's `times`.
        # Codegen expresses the DAMAGE form (the Times var feeds
        # DamageCmd.Attack().WithHitCount). A repeat on apply_power would
        # need its own var and has no card yet -- structural until then, and
        # reported unexpressible rather than silently dropped.
        "times": any(e["op"] == "damage" and e.get("target") != "self"
                     and isinstance(e.get("times"), int) and e["times"] > 1
                     for e in effects),
        # EB-118 joins the same two vars: both riders render through the
        # CalculatedDamageVar triple, so ExtraDamage/CalculationBase are where
        # a `per` / `base` delta lands whichever count it reads.
        # EB-122 joins the discards-this-turn rider to the same two vars, for
        # the same reason: it renders through the identical
        # CalculationBase/ExtraDamage triple, so the deltas land in the same
        # slots whichever count the rider reads.
        "formula_per": any(
            exhaust_pile_calc_rider(card, e) is not None
            or exhaust_selection_calc_rider(card, e) is not None
            or discards_turn_calc_rider(card, e) is not None
            for e in effects),
        "formula_base": any(
            exhaust_pile_calc_rider(card, e) is not None
            or exhaust_selection_calc_rider(card, e) is not None
            or discards_turn_calc_rider(card, e) is not None
            for e in effects),
    }
    # tier0 binds every POWER_UPGRADE_KEYS delta to the first TOP-LEVEL
    # apply_power OR buff_next_attack (upgrades.py takes `next(fx for fx in
    # top if fx["op"] in (...))`), which is how `buff` reaches both Bennett's
    # apply_power and Chevreuse's buff_next_attack.
    for pkey in POWER_UPGRADE_KEYS:
        has[pkey] = any(e["op"] in POWER_UPGRADE_OPS for e in effects)
    for key, value in deltas.items():
        if key not in EXPRESSIBLE_DELTAS:
            return {}, f"delta key '{key}: {value}' not expressible by codegen (structural upgrade)"
        if key == "add":
            added_op = value.get("op") if isinstance(value, dict) else None
            if added_op == "repeat_this":
                # R130 (take_your_bow+): the upgrade appends the repeat rather
                # than a number. Sim law is resolve_card's -- the effect list
                # minus the repeat machinery re-resolves `times` more times --
                # so the emission is the SAME for-block the repeat-conditional
                # tail uses, gated on IsUpgraded instead of a predicate.
                if not (set(value) <= {"op", "times"}
                        and isinstance(value.get("times", 1), int)
                        and value.get("times", 1) > 0):
                    return {}, (
                        f"delta 'add: {value}' (repeat_this times must be a "
                        "positive literal int)")
                bad = [e["op"] for e in effects
                       if e["op"] not in UPGRADE_REPEAT_OPS]
                if bad:
                    return {}, (
                        f"delta 'add: repeat_this' beside op(s) {sorted(set(bad))} "
                        "(no verified re-emission for the repeated body)")
                if any(e.get("op") == "conditional" and any(
                        x.get("op") == "repeat_this" for x in e.get("then", []))
                       for e in effects):
                    return {}, ("delta 'add: repeat_this' on a card that "
                                "already repeats (repeatTimes collision)")
            elif added_op == "discard":
                # EB-122 (send_the_runner+). The CHOSEN branch only: the
                # emitter for a random discard re-pools per pick, and an
                # upgrade-only random throw has no card. Every number is a
                # LITERAL -- an appended effect is not the target of any other
                # delta key, so nothing can move it and no var is needed.
                if not (isinstance(value, dict)
                        and set(value) == {"op", "amount", "select"}
                        and value.get("select") == "chosen"
                        and isinstance(value.get("amount"), int)
                        and value["amount"] > 0):
                    return {}, (
                        f"delta 'add: {value}' (an appended discard must be "
                        "`select: chosen` with a positive literal amount)")
                if any(e.get("op") in ("discard", "discard_for_sparks")
                       for e in everywhere):
                    return {}, (
                        "delta 'add: discard' on a card that already discards "
                        "(the appended throw and the printed one would read "
                        "as one line)")
            elif added_op == "block":
                # EB-122 (wheel_the_ranks+). Literal, and deliberately WITHOUT
                # a BlockVar: `CanonicalVars` is what BaseLib auto-detects
                # `GainsBlock` from, and a card that only gains Block once
                # upgraded must not claim it while unupgraded -- tier0's own
                # Nimble predicate reads the base row, so a declared var would
                # be an eligibility split the moment it shipped
                # (lint_enchant_parity). The upgraded instance says so instead,
                # through an IsUpgraded-valued override.
                if not (isinstance(value, dict)
                        and set(value) == {"op", "amount"}
                        and isinstance(value.get("amount"), int)
                        and value["amount"] > 0):
                    return {}, (
                        f"delta 'add: {value}' (an appended block must carry "
                        "a positive literal amount)")
                if any(e.get("op") == "block" for e in everywhere):
                    return {}, (
                        "delta 'add: block' on a card that already gains "
                        "Block (Block var collision)")
            elif not (isinstance(value, dict)
                      and set(value) == {"op", "amount"}
                      and value.get("op") in {"draw", "gain_encore"}
                      and isinstance(value.get("amount"), int)
                      and value["amount"] > 0):
                return {}, (
                    f"delta 'add: {value}' (only a positive draw, "
                    "gain_encore, block or chosen discard effect, or a "
                    "repeat_this, is expressible)")
            if added_op == "draw" and any(
                    e.get("op") == "draw" for e in everywhere):
                return {}, "delta 'add: draw' on a card with an existing draw (Cards var collision)"
            if added_op != "repeat_this" and any(
                    e.get("op") == "conditional" and any(
                        x.get("op") == "repeat_this" for x in e.get("then", []))
                    for e in effects):
                return {}, "delta 'add: draw' on a repeating card (repeat semantics not expressible)"
        if key == "add_before":
            # EB-122. Same three checks tier0's applier makes, in the same
            # order and for the same reasons (content/upgrades.py): it is a
            # modifier, so it needs an `add`; it names an OP, not an index; and
            # the op has to be on the card, or the applier raises and the
            # position silently would not be honoured here.
            if "add" not in deltas or not isinstance(value, str):
                return {}, (
                    f"delta 'add_before: {value}' without an `add` to place "
                    "(it is a position modifier, not an effect)")
            if deltas["add"].get("op") == "repeat_this":
                return {}, (
                    "delta 'add_before' beside 'add: repeat_this' (a repeat "
                    "re-runs the whole body; it has no position within it)")
            if not any(e.get("op") == value for e in effects):
                return {}, (
                    f"delta 'add_before: {value}' names an op this card does "
                    "not print at top level (sheet/card mismatch)")
            continue
        if key == "condition" and value != "unconditional":
            return {}, f"delta 'condition: {value}' (only 'unconditional' is tier0 grammar)"
        if key == "remove":
            # Both removable values name a base-card KEYWORD FIELD of the same
            # name, so the presence check is the field lookup. Owned here
            # rather than in `has` above: `has` is keyed by delta KEY and this
            # delta's requirement is keyed by its VALUE.
            if value not in ("exhaust", "ethereal"):
                return {}, f"delta 'remove: {value}' not expressible by codegen (structural upgrade)"
            if not card.get(value):
                return {}, (
                    f"delta 'remove: {value}' on a card that does not print "
                    f"{value} (sheet/card mismatch)")
            continue
        if cond_reason.get(key):
            return {}, cond_reason[key]
        if not has[key]:
            return {}, f"delta key '{key}' has no matching effect on this card (sheet/card mismatch)"
    return dict(deltas), None


def added_draw_upgrade(card: dict) -> int:
    """Amount of an upgrade-only draw appended by `add`, or zero.

    The full upgrade plan validates the structural shape and collision rules;
    callers only need the amount for vars, text, and play-time emission.
    """
    added = upgrade_plan(card)[0].get("add")
    return (int(added["amount"])
            if isinstance(added, dict) and added.get("op") == "draw" else 0)


def added_block_upgrade(card: dict) -> int:
    """Amount of an upgrade-only Block grant added by `add`, or zero (EB-122,
    wheel_the_ranks+). Shape validated in upgrade_plan."""
    added = upgrade_plan(card)[0].get("add")
    return (int(added["amount"])
            if isinstance(added, dict) and added.get("op") == "block" else 0)


def added_discard_upgrade(card: dict) -> int:
    """Count of an upgrade-only CHOSEN discard added by `add`, or zero
    (EB-122, send_the_runner+). Shape validated in upgrade_plan."""
    added = upgrade_plan(card)[0].get("add")
    return (int(added["amount"])
            if isinstance(added, dict) and added.get("op") == "discard" else 0)


def added_effect_anchor(card: dict) -> dict | None:
    """The top-level effect an `add` must resolve BEFORE, or None to append.

    EB-122. The anchor is looked up by OP, which is what makes the position
    survive an edit to the base body: tier0's applier does the identical
    `next(e for e in top if e["op"] == before)` and raises when it misses, and
    `upgrade_plan` refuses the card on the same miss, so the two engines can
    never disagree about WHERE the new line goes.
    """
    deltas = upgrade_plan(card)[0]
    before = deltas.get("add_before")
    if not before:
        return None
    return next((e for e in card.get("effects", [])
                 if e.get("op") == before), None)


def added_encore_upgrade(card: dict) -> int:
    """Upgrade-only gain_encore effect appended by `add`, or zero."""
    added = upgrade_plan(card)[0].get("add")
    return (int(added["amount"])
            if isinstance(added, dict)
            and added.get("op") == "gain_encore" else 0)


def added_repeat_upgrade(card: dict) -> int:
    """Extra resolutions of a `repeat_this` appended by `add`, or zero.

    R130's take_your_bow+ is the first card in this grammar. Shape is
    validated in upgrade_plan (positive literal `times`, every top-level op
    in UPGRADE_REPEAT_OPS, no second repeat); callers only need the count.
    """
    added = upgrade_plan(card)[0].get("add")
    return (int(added.get("times", 1))
            if isinstance(added, dict)
            and added.get("op") == "repeat_this" else 0)


def added_encore_salon(card: dict) -> tuple[int, int] | None:
    """(base, deploys) for an upgrade-appended encore on a salon-deploy card,
    or None.

    The sim doubles an appended `add: gain_encore` on a replacement deploy
    exactly as it doubles a printed one, so the number must render through
    the same CalculatedVar + ReplacementDelta trio the printed siblings use
    -- an IsUpgraded literal shows half the real grant on a full stage
    (SYS-6: salon_debut printed "Gain 2 Encore" and granted 4). The appended
    effect resolves after every base effect, so the delta counts ALL of the
    card's deploys; same staticness rule as `_salon_calc_target` -- an
    upgradeable or non-int deploy amount keeps the inline expression rather
    than guessing a closed form.
    """
    base = added_encore_upgrade(card)
    if not base or not salon_deploy_card(card):
        return None
    deploys = 0
    for eff in card.get("effects", []):
        if (eff.get("op") == "apply_power"
                and eff.get("power") == "salon_member"):
            if eff is power_upgrade_effect(card):
                return None          # deploy count is not static
            amount = eff.get("amount", 1)
            if not isinstance(amount, int):
                return None
            deploys += amount
    return base, deploys


def encore_upgrade(card: dict) -> int:
    """Ruled Encore delta. The sim applies it to every gain_encore effect,
    branches included; generated play/text use IsUpgraded at each site."""
    return int(upgrade_plan(card)[0].get("encore", 0))


def spark_upgrade(card: dict) -> int:
    """Ruled Spark upgrade delta (M9): `spark: +N` in klee-upgrades.yaml. 0 = none.
    Zero when the card's upgrade plan is unappliable -- no upgrade renders."""
    return int(upgrade_plan(card)[0].get("spark", 0))


def burst_upgrade(card: dict) -> int:
    """Ruled Burst-energy upgrade delta: `burst_energy: +N`. 0 = none."""
    return int(upgrade_plan(card)[0].get("burst_energy", 0))


def discard_upgrade(card: dict) -> tuple[int, int]:
    """Ruled R36 deltas on discard_for_sparks: (discard: +N, sparks: +M).
    (0, 0) = none; either key alone still upgrades both vars' rendering."""
    deltas = upgrade_plan(card)[0]
    return int(deltas.get("discard", 0)), int(deltas.get("sparks", 0))


def plain_discard_upgrade(card: dict) -> int:
    """G6: a `discard` delta landing on the PLAIN discard op, not Crackle's.

    Zero when the card has no such delta, or when it carries
    discard_for_sparks -- which wins the binding in BOTH appliers (tier0
    upgrades.py tries it first, and this mirrors that order). Getting the
    precedence wrong here would not fail a build; it would upgrade a
    different effect than the simulator does, which is the class of
    divergence the constant-parity gate exists for and cannot see.
    """
    effects = _effects_everywhere(card)
    if any(e["op"] == "discard_for_sparks" for e in effects):
        return 0
    if not any(e["op"] == "discard" for e in effects):
        return 0
    return int(upgrade_plan(card)[0].get("discard", 0))


def bonus_upgrade(card: dict) -> int:
    """Ruled `bonus: +N` delta on the card's bomb op. 0 = none. One
    DynamicVar name ("Bonus") serves it, so a second bonus-carrying effect
    on the same card is a loud stop, not a silent overwrite."""
    delta = int(upgrade_plan(card)[0].get("bonus", 0))
    if delta:
        n = sum(1 for e in card["effects"]
                if e.get("op") in BONUS_OPS and "bonus" in e)
        if n > 1:
            raise SystemExit(
                f"gen_klee_cards: {card['id']}: {n} bonus-carrying bomb ops "
                "-- one 'Bonus' var cannot serve two effects.")
    return delta


def chance_upgrade(card: dict) -> float:
    """Ruled `chance: X` REPLACEMENT (tier0 upgrades.py replaces, never
    bumps). 0.0 = none."""
    return float(upgrade_plan(card)[0].get("chance", 0.0))


def stash_upgrade(card: dict) -> int:
    """Ruled `cards: +N` (secret_stash): bumps the add_card amount. Rides a
    'Stash' var ('Cards' is the draw CardsVar's name). 0 = none."""
    return int(upgrade_plan(card)[0].get("cards", 0))


def bonus_per_upgrade(card: dict) -> int:
    """Ruled `bonus_per_detonation: +N` (grand_finale): the bonus_formula's
    per-detonation rate, rendered/upgraded via the BonusPer var. 0 = none."""
    return int(upgrade_plan(card)[0].get("bonus_per_detonation", 0))


def times_var_effect(card: dict) -> dict | None:
    """The ONE damage effect whose hit count is upgradeable, or None.

    tier0's `times` delta is a _bump_first over damage|apply_power, so only
    the FIRST literal multi-hit damage op is upgradeable -- the same
    first-effect-owns-the-var rule as damage_var_effect. Every other
    multi-hit op keeps rendering its literal count.
    """
    if not times_upgrade(card):
        return None
    return next((e for e in card.get("effects", [])
                 if e["op"] == "damage" and e.get("target") != "self"
                 and isinstance(e.get("times"), int) and e["times"] > 1),
                None)


def times_upgrade(card: dict) -> int:
    """Ruled `times: +N` (A5 undercurrent): the hit count moves on upgrade,
    so the count rides a Times var and renders with diff(). 0 = none."""
    return int(upgrade_plan(card)[0].get("times", 0))


def bombs_upgrade(card: dict) -> int:
    """Ruled `bombs: +N` (controlled_demolition): X_plus_1 -> X_plus_2.
    Rides the Bombs var so the +1 renders with diff(). 0 = none."""
    return int(upgrade_plan(card)[0].get("bombs", 0))


def conditional_bonus_upgrade(card: dict) -> int:
    """Ruled `conditional_bonus: +N` (tail_of_flame): bumps the then-branch's
    first damage. 0 = none. The bump rides the ExtraDamage var, so a card
    whose bombs already claim ExtraDamage is a loud stop."""
    delta = int(upgrade_plan(card)[0].get("conditional_bonus", 0))
    if delta and any(e.get("op") == "place_bomb"
                     for e in _effects_everywhere(card)):
        raise SystemExit(
            f"gen_klee_cards: {card['id']}: conditional_bonus needs the "
            "ExtraDamage var but the card also places bombs -- two claims "
            "on one var name.")
    return delta


# --- EB-140: the two "bump every matching op" keys --------------------------
#
# tier0's appliers (upgrades.py `conditional_block` / `conditional_damage`)
# take the card's `everywhere` scope -- top level AND both arms of every
# conditional -- and bump each matching op whose amount is a LITERAL INT. The
# predicates below are that same test, held next to each other so the two
# engines cannot drift on which op a delta lands on. (Contrast
# `conditional_bonus`, which moves exactly ONE branch number.)
_CONDITIONAL_DELTA_OPS = {
    "conditional_block": lambda e: (e.get("op") == "block"
                                    and isinstance(e.get("amount"), int)),
    "conditional_damage": lambda e: (e.get("op") == "damage"
                                     and e.get("target") != "self"
                                     and isinstance(e.get("amount"), int)),
}


def _conditional_delta_targets(card: dict, key: str) -> tuple[list, list]:
    """(top-level effects, branch effects) this delta bumps on this card.

    Split by WHERE they live because codegen says the two halves in two
    different grammars: the top-level op owns a DynamicVar and upgrades
    through it, while a branch amount is a literal and swaps on an
    `IsUpgraded` read (curtain_cue's shape for the `encore` key).
    """
    match = _CONDITIONAL_DELTA_OPS[key]
    effects = card.get("effects", [])
    top = [e for e in effects if match(e)]
    branch = []
    for eff in effects:
        if eff.get("op") != "conditional":
            continue
        for arm in ("then", "else"):
            branch.extend(e for e in (eff.get(arm) or []) if match(e))
    return top, branch


def _conditional_delta_reason(card: dict, key: str,
                              deltas: dict) -> str | None:
    """None when a `conditional_block`/`conditional_damage` delta is fully
    emittable on this card, else the reason it is not.

    R24's UNAPPLIABLE discipline in its usual direction: a shape the emitter
    cannot say in FULL is reported structural rather than half-applied, since
    half a ruled upgrade is a silent approximation of the other half.
    """
    top, branch = _conditional_delta_targets(card, key)
    what = ("literal-int `block`" if key == "conditional_block"
            else "literal-int non-self `damage`")
    if not top and not branch:
        return (f"delta key '{key}: {deltas[key]}' has no {what} op on this "
                "card (sheet/card mismatch)")
    if len(top) > 1:
        # One op, one var: build_vars declares a single Block/Damage var per
        # card, so a second top-level target would have nowhere to render.
        return (f"delta key '{key}: {deltas[key]}' bumps {len(top)} top-level "
                f"{what} ops and the card declares one var for them "
                "(structural upgrade)")
    if _is_sly_branch(card):
        # Belt and braces: _sly_view already swaps the id so no delta is
        # found, and every Sly amount is a literal that must stay one.
        return (f"delta key '{key}: {deltas[key]}' inside a Sly branch "
                "(structural upgrade)")
    if branch and "conditional_bonus" in deltas:
        # conditional_bonus rewrites the then-branch's first damage through
        # the ExtraDamage var; both keys claiming one branch number would
        # emit one of the two and drop the other.
        return (f"delta key '{key}: {deltas[key]}' shares a branch with a "
                "`conditional_bonus` delta (two claims on one number)")
    for eff in card.get("effects", []):
        if eff.get("op") != "conditional":
            continue
        if not any(e.get("op") == "repeat_this"
                   for e in (eff.get("then") or [])):
            continue
        if any(_CONDITIONAL_DELTA_OPS[key](e)
               for arm in ("then", "else") for e in (eff.get(arm) or [])):
            # A repeat-conditional's body is re-emitted through the repeat
            # tail rather than through _emit_branch_op, so there is no single
            # site an IsUpgraded swap could live on.
            return (f"delta key '{key}: {deltas[key]}' reaches inside a "
                    "repeat-conditional (no swap site)")
    return None


def conditional_block_upgrade(card: dict) -> int:
    """Ruled `conditional_block: +N`, or 0. Expressibility is gated in
    upgrade_plan, so a non-zero answer here is emittable everywhere."""
    return int(upgrade_plan(card)[0].get("conditional_block", 0))


def conditional_damage_upgrade(card: dict) -> int:
    """Ruled `conditional_damage: +N`, or 0. Gated the same way."""
    return int(upgrade_plan(card)[0].get("conditional_damage", 0))


def condition_upgrade(card: dict) -> bool:
    """Ruled `condition: unconditional` (patched_dress): the upgraded card
    runs the then-branch always. C#: predicate reads (IsUpgraded || pred);
    text swaps via {IfUpgraded:show:...|...}."""
    return upgrade_plan(card)[0].get("condition") == "unconditional"


def branch_draw_vars(card: dict) -> tuple[str, str]:
    """(then-branch var, else-branch var) for a card's branch draws.

    Normally the then-branch rides `Cards`, because a card whose draws live
    ONLY in branches has no top-level draw competing for that name
    (eager_to_help). Compose Herself broke that assumption at Curtain Call:
    it draws 2 at top level AND 1 more inside its Encore branch, and tier0's
    draw delta bumps ALL draw ops, so both numbers are upgradeable and both
    need a var. `Cards` is already spoken for by the top-level draw, so the
    branch takes `DrawThen`.

    A third NAME rather than a shared var: DynamicVarSet throws on duplicates
    inside CardFactory.CreateForReward, which is a reward-screen softlock on
    whatever run happens to roll the card.
    """
    top_draws = [e for e in card["effects"] if e.get("op") == "draw"]
    return ("DrawThen" if top_draws else "Cards"), "DrawElse"


def branch_draw_upgrade(card: dict) -> int:
    """Ruled `draw: +N` when the card's draws live inside conditional
    branches (eager_to_help, and Compose Herself which also draws at top
    level). tier0 bumps ALL draw ops; the branch draws ride the vars
    `branch_draw_vars` assigns."""
    delta = int(upgrade_plan(card)[0].get("draw", 0))
    if not delta:
        return 0
    branch_draws = [e for e in _effects_everywhere(card)
                    if e.get("op") == "draw"]
    top_draws = [e for e in card["effects"] if e.get("op") == "draw"]
    # _effects_everywhere is a superset of the top level, so equal counts mean
    # there are no branch draws at all and the plain top-level path applies.
    return 0 if len(branch_draws) == len(top_draws) else delta


def _effects_everywhere(card: dict) -> list[dict]:
    """Every effect on the card, branches included -- the shared walk.

    L4: this used to be a private one-level walk (top level, plus a top-level
    conditional's `then:`/`else:`). It now delegates to
    `tools/effect_walk.iter_effects`, the repo's single walk, so a conditional
    nested inside a branch is visible here too and the generator cannot drift
    from the lints that read the same tree. Identical output on today's sheets
    (no sheet nests a conditional inside a branch).
    """
    return list(iter_effects(card.get("effects", [])))


def power_upgrade(card: dict) -> int:
    """Ruled power-amount delta (power_amount/amp_percent/splash_damage/
    vulnerable all bump the applied amount -- tier0 upgrades.py handles them
    in one branch too). 0 = none."""
    deltas = upgrade_plan(card)[0]
    keys = [k for k in POWER_UPGRADE_KEYS if k in deltas]
    if len(keys) > 1:
        raise SystemExit(
            f"gen_klee_cards: {card['id']}: multiple power upgrade keys {keys} "
            "-- one apply_power effect cannot take two amount deltas.")
    return int(deltas[keys[0]]) if keys else 0


def damage_var_effect(card: dict) -> dict | None:
    """The ONE top-level damage effect that owns the `Damage` var.

    Exactly the power_upgrade_effect rule, one var-name over: tier0's `damage`
    delta is a _bump_first over top-level non-self damage ops, so only the
    FIRST such effect is upgradeable and only it may declare a var. Every
    later damage effect renders its printed literal.

    Curtain Call's Matinee Performance is the first card in the pool with two
    top-level damage ops (a flat hit, then a per-member hit). Before this rule
    both declared "Damage" and the generator's own duplicate-name check fired
    -- which is the check standing in for a DynamicVarSet constructor throw
    inside CardFactory.CreateForReward, i.e. a reward-screen softlock on
    whatever run rolled the card.
    """
    return next((fx for fx in card.get("effects", [])
                 if fx.get("op") == "damage"
                 and fx.get("target") != "self"), None)


def power_upgrade_effect(card: dict) -> dict | None:
    """The ONE top-level effect the ruled power delta binds to, mirroring
    tier0/content/upgrades.py exactly: `weak`/`vulnerable` bump the first
    apply_power whose power NAME contains the word; every other key takes the
    first top-level apply_power/buff_next_attack. Every other power effect on
    the card renders its printed literal and declares NO var -- two effects
    sharing the "PowerAmount" name is a DynamicVarSet constructor throw that
    kills the reward screen (playtest 2026-07-23: stage_lights,
    courtroom_drama)."""
    if not power_upgrade(card):
        return None
    deltas = upgrade_plan(card)[0]
    key = next(k for k in POWER_UPGRADE_KEYS if k in deltas)
    effects = card["effects"]
    if key in ("weak", "vulnerable"):
        word = "vuln" if key == "vulnerable" else "weak"
        hit = next((fx for fx in effects if fx.get("op") == "apply_power"
                    and word in fx.get("power", "")), None)
    elif key == "kurage_ward":
        # R130: the key IS the power name, same name-matched binding the sim
        # uses (upgrades.py, beside weak/vulnerable).
        hit = next((fx for fx in effects if fx.get("op") == "apply_power"
                    and fx.get("power") == "kurage_ward"), None)
    else:
        hit = next((fx for fx in effects
                    if fx.get("op") in POWER_UPGRADE_OPS), None)
    if hit is None:
        # upgrade_plan vets "some POWER_UPGRADE_OPS effect exists" but not the
        # weak/vuln name match; the sim would fail to apply this delta, so a
        # silent literal here would ship a card whose upgrade does nothing.
        raise SystemExit(
            f"gen_klee_cards: {card['id']}: power delta '{key}' matches no "
            "top-level effect (tier0 upgrades.py binding rule) -- fix the "
            "sheet or the delta key.")
    return hit


def _target_guard(lines: list[str], ctx: dict) -> None:
    """One ThrowIfNull per OnPlay (cardPlay.Target is nullable; a
    single-target card played with no target is a bug in the caller, so fail
    loudly rather than silently no-op -- mirrors the hand-written Kaboom).
    ctx-tracked because conditional branches emit into sub-lists, where a
    text scan of `lines` cannot see the outer guard."""
    if not ctx["thrown"]:
        ctx["thrown"] = True
        lines.append(
            'ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");'
        )


def _emit_damage(card: dict, eff: dict, lines: list[str], ctx: dict,
                 amount_expr: str) -> None:
    """The one attack-damage builder -- top level, conditional branches and
    the repeat tail all route here so the targeting idiom cannot drift."""
    times = eff.get("times", 1)
    target = eff["target"]

    call = [f"await DamageCmd.Attack({amount_expr})"]
    x_times = isinstance(times, str)
    # A runtime hit count is gated on the same ">0 or no hits at all" rule as
    # X: tier0 loops `range(times)`, so a count of zero deals NOTHING rather
    # than one default hit. DamageCmd would treat a 0 hit count as one swing.
    times_guard = ("x" if times == "X" or (isinstance(times, str)
                                           and times.startswith("X_plus_"))
                   else RUNTIME_TIMES.get(times) if x_times else None)
    if "times_formula" in eff:
        # 2_plus_sparks (Gleeful Barrage), the sim's only times formula.
        # SparksAtPlay: R39 (2026-07-21 ruling) -- the sim computes times from
        # state.sparks_at_play, the bank BEFORE this card's own spend, because
        # hitting the threshold that makes the card free was otherwise exactly
        # what deleted the sparks it counts.
        call.append(
            ".WithHitCount(2 + SparkPower.SparksAtPlay(Owner.Creature))")
    elif x_times:
        # times: "X" (fish_blasting) or a runtime count (salon_members).
        # tier0 loops range(times): 0 means NO hits, so the whole attack
        # statement is gated below.
        call.append(
            f".WithHitCount({RUNTIME_TIMES.get(times) or _x_expr(times)})")
    elif eff is times_var_effect(card):
        # Ruled `times: +N`: the count lives in a var so OnUpgrade can bump it
        # and the face renders the diff. Literal counts keep the literal.
        call.append('.WithHitCount(DynamicVars["Times"].IntValue)')
    elif times > 1:
        call.append(f".WithHitCount({times})")
    call.append(".FromCard(this)")

    if target == "enemy":
        _target_guard(lines, ctx)
        call.append(".Targeting(cardPlay.Target)")
    elif target == "all_enemies":
        # CombatState is declared nullable but is always set while a
        # card is resolving -- every base-game AoE card dereferences it
        # unguarded.
        call.append(".TargetingAllOpponents(CombatState!)")
    else:  # random_enemy / random_enemies
        # Emitted UNGUARDED on purpose, and that is a first-party fact rather
        # than a trust: decompiled from the shipped sts2.dll v0.107.1
        # (ilspycmd 8.2), AttackCommand.Execute refilters `validTargets` to
        # living creatures on every hit and breaks on
        # `validTargets.Count == 0 && combatState.IsLiveCombat()` BEFORE the
        # Rng.NextItem call -- and CombatState.IsLiveCombat() returns literally
        # `true`. An empty pool ends the hit loop; it does not throw, self-hit
        # or re-hit a corpse. The one throw path on empty targets sits inside
        # the duplicate-exclusion recheck under `allowDuplicates: false`, which
        # this emitter never passes (the default is `true`), so no emitted card
        # can reach it.
        call.append(".TargetingRandomOpponents(CombatState!)")

    call.append('.WithHitFx("vfx/vfx_attack_slash")')
    if target == "all_enemies":
        call.append(".SpawningHitVfxOnEachCreature()")
    call.append(".Execute(choiceContext);")

    stmt = "\n            ".join(call)
    if times_guard:
        stmt = (f"if ({times_guard} > 0)\n        {{\n            "
                + stmt.replace("\n", "\n    ")
                + "\n        }")
    lines.append(stmt)


def _bomb_where(target: str, singular: bool) -> str:
    """The placement clause a Bomb line prints, for ONE target spelling.

    One definition for both description sites (the merged-deploy one-liner
    and the top-level face), because a card that says "on a random enemy"
    on one screen and "on EACH enemy" on another has told the player two
    different things about the same row. `enemy` prints nothing: the aimed
    form is the default reading of "place a Bomb" on an aimable card.
    """
    if target == "enemy":
        return ""
    if target == "all_enemies":
        return " on EACH enemy"
    return " on a random enemy" if singular else " on random enemies"


def _emit_place_bomb(card: dict, eff: dict, lines: list[str], ctx: dict,
                     dmg_expr: str) -> None:
    n = eff["amount"]
    if isinstance(n, str):
        # X-cost count (controlled_demolition): tier0 _amount, X or X_plus_N.
        n = _x_expr(n, bombs_var=bombs_upgrade(card) > 0)
    if eff["target"] == "enemy":
        _target_guard(lines, ctx)
        place = (
            f"await BombPower.Place(choiceContext, cardPlay.Target, {dmg_expr}, "
            "Owner.Creature, this);"
        )
        if n == 1:
            lines.append(place)
        else:
            lines.append(
                f"for (var i = 0; i < {n}; i++)\n        {{\n"
                f"            {place}\n        }}"
            )
    elif eff["target"] == "all_enemies":
        # EB-118 §4.2 distribution. tier0 nests `for _ in range(amount): for
        # enemy in targets`, and re-reads the living enemies on each outer
        # pass -- so the outer loop is the AMOUNT and the enemy sweep is
        # inside it, not the other way round. Every shipped row is
        # `amount: 1`; the loop is written for the general case anyway,
        # because a later row that is not 1 must not silently mean something
        # else in C# than it means in the sim.
        sweep = (
            "foreach (var bombTarget in CombatState!.HittableEnemies.ToList())"
            "\n        {\n"
            f"            await BombPower.Place(choiceContext, bombTarget, "
            f"{dmg_expr}, Owner.Creature, this);\n        }}"
        )
        if n == 1:
            lines.append(sweep)
        else:
            lines.append(
                f"for (var i = 0; i < {n}; i++)\n        {{\n"
                + "\n".join("    " + ln for ln in sweep.split("\n"))
                + "\n        }"
            )
    else:
        # Each bomb rolls its own target, so N bombs can land on N
        # different enemies -- matching Tier 0's per-bomb target pick.
        # HittableEnemies can be empty if the last enemy died earlier in
        # this card's resolution, and NextItem would throw on that.
        lines.append(
            f"for (var i = 0; i < {n}; i++)\n"
            "        {\n"
            "            var candidates = CombatState!.HittableEnemies.ToList();\n"
            "            if (candidates.Count == 0) break;\n"
            "            var bombTarget = Owner.RunState.Rng.CombatTargets.NextItem(candidates);\n"
            "            if (bombTarget == null) break;\n"
            f"            await BombPower.Place(choiceContext, bombTarget, {dmg_expr}, "
            "Owner.Creature, this);\n"
            "        }"
        )


def _stmt_gain_spark(card: dict, eff: dict) -> str:
    amount = ('DynamicVars["Sparks"].IntValue' if spark_upgrade(card)
              else str(int(eff["amount"])))
    return f"await SparkPower.Gain(choiceContext, Owner.Creature, {amount}, this);"


def _stmt_spend_spark(card: dict, eff: dict) -> str:
    # The PAYMENT half of the sink cost line; the GATE half is the IsPlayable
    # override emit() attaches from the same effect. Literal price -- see
    # MECHANICAL_OPS. The return value is deliberately dropped: with the gate
    # in front of it a top-level spend cannot be short, and a card that wants
    # to BRANCH on the payment is a different mechanic than a cost line.
    return ("await SparkPower.Spend(choiceContext, Owner.Creature, "
            f"{int(eff['amount'])}, this);")


def _stmt_burst_energy(card: dict, eff: dict) -> str:
    amount = ('DynamicVars["BurstEnergy"].IntValue' if burst_upgrade(card)
              else str(int(eff["amount"])))
    return f"await KleeBurstResource.Gain(choiceContext, Owner.Creature, {amount}, this);"


def _encore_amount_expr(card: dict, eff: dict) -> str:
    base = int(eff["amount"])
    delta = encore_upgrade(card)
    return f"(IsUpgraded ? {base + delta} : {base})" if delta else str(base)


def energy_upgrade(card: dict) -> int:
    """Ruled energy delta: `energy: +N` in kokomi-upgrades.yaml."""
    return int(upgrade_plan(card)[0].get("energy", 0))


def block_next_turn_upgrade(card: dict) -> int:
    """Ruled deferred-block delta: `block_next_turn: +N` (Sayu's daruma)."""
    return int(upgrade_plan(card)[0].get("block_next_turn", 0))


def exhaust_upgrade(card: dict) -> int:
    """Ruled chosen-exhaust delta: `exhaust: +N` in kokomi-upgrades.yaml."""
    return int(upgrade_plan(card)[0].get("exhaust", 0))


def kurage_turns_upgrade(card: dict) -> int:
    """Ruled Bake-Kurage duration delta: `kurage_turns: +N`. 0 = none."""
    return int(upgrade_plan(card)[0].get("kurage_turns", 0))


def kurage_turns_expr(card: dict, eff: dict) -> str:
    """Duration of a summoned Bake-Kurage.

    A LITERAL unless kokomi-upgrades.yaml carries a `kurage_turns: +N` delta
    for this card, in which case it becomes the named DynamicVar the face
    reads -- the Sparks/BurstEnergy idiom. Duration is the ONLY thing an
    upgrade may move here: the pulse numbers are constants, and the +1 Charge
    is untouchable under the resource-curve law.
    """
    if kurage_turns_upgrade(card):
        return 'DynamicVars["KurageTurns"].IntValue'
    return str(int(eff.get("amount", 1)))


def _conscript_phrase(eff: dict) -> str:
    """Player-facing conscript text.

    R55 VOICE LAW: exhaust is ROTATION, never sacrifice. Forced service is
    Shogunate behaviour and the resistance were volunteers, so the display
    family is Muster/Enlist/Rally. The internal op name stays `conscript`;
    the FACE never says it.

    R78 (Neap Tide v2.1): the grammar is a KEYWORD now. Every conscript card
    used to restate the whole rule -- "transform N cards in your hand into a
    random Inazuma Companion that costs 1 less and Exhausts" -- on nine cards,
    which is ~90 characters of identical text per face and the reason several
    of them were at text budget. "Muster N" says it once; the hover tip
    (KokomiRiderTips.ForMuster, attached by codegen to every conscript card)
    carries the definition.

    DEVIATIONS WRITE OUT ONLY THE DEVIATION, which is the half that makes the
    keyword worth having. `create` mode adds the unit instead of replacing a
    card, and a cost_override pins the recruit's cost -- each prints its own
    clause and nothing else, so what a reader sees on the face is exactly what
    is different about this card.
    """
    n = int(eff.get("amount", 1))
    phrase = f"[gold]Muster[/gold] {n}"
    if eff.get("mode") == "create":
        # The deviation is WHERE the units land, not what they are.
        phrase += f", adding the unit{'' if n == 1 else 's'} to your hand"
    if "cost_override" in eff:
        # The deviation is the price. The keyword's own "costs 1 less" is
        # replaced, not stacked with -- KokomiConscript.RollRecruit treats
        # cost_override as reaching the target ABSOLUTELY.
        phrase += f", at cost {int(eff['cost_override'])}"
    return phrase


def _stmt_gain_encore(
    card: dict, eff: dict, *, salon_scaled: bool = False
) -> str:
    amount = _encore_amount_expr(card, eff)
    if salon_scaled:
        amount = (f"{amount} * (salonReplacements > 0 ? "
                  "SalonConstants.ReplacementNumericMultiplier : 1)")
    return (
        "FurinaResources.GainEncore(Owner.Creature, "
        f"{amount});")


def _branch_amount(card: dict, eff: dict, key: str) -> str:
    """A branch damage/block amount as C#: a bare literal, or the
    `(IsUpgraded ? up : base)` swap a conditional_* delta puts on it.

    EB-140. The BRANCH half of `conditional_block` / `conditional_damage`.
    Branch amounts are literals by construction (see this function's callers),
    so the only way to say "this number is 3 higher when upgraded" is the
    play-time read -- which is exactly what curtain_cue already emits for the
    `encore` key. The TOP-LEVEL half of the same delta rides the op's own
    DynamicVar and is bumped in OnUpgrade instead.
    """
    base = int(eff["amount"])
    delta = (conditional_block_upgrade(card) if key == "conditional_block"
             else conditional_damage_upgrade(card))
    if not delta or not _CONDITIONAL_DELTA_OPS[key](eff):
        return f"{base}m"
    return f"(IsUpgraded ? {base + delta}m : {base}m)"


def _emit_branch_op(
    card: dict, eff: dict, lines: list[str], ctx: dict,
    in_then: bool, cb_state: dict, spotlight_capable: bool
) -> None:
    """Conditional-branch resolvers. Amounts are literals unless a ruled
    delta claims them (see build_vars): conditional_bonus -> then-first
    damage via ExtraDamage; draw delta -> Cards (then) / DrawElse (else)."""
    op = eff["op"]
    if op == "damage":
        if in_then and cb_state.get("pending"):
            cb_state["pending"] = False
            amount = "DynamicVars.ExtraDamage.BaseValue"
        else:
            amount = _branch_amount(card, eff, "conditional_damage")
        if spotlight_capable:
            amount = f"SpotlightSystem.PrintedDamage(this, {amount})"
        _emit_damage(card, eff, lines, ctx, amount)
    elif op == "block":
        amount = _branch_amount(card, eff, "conditional_block")
        if spotlight_capable:
            amount = f"SpotlightSystem.PrintedBlock(this, {amount})"
        lines.append(
            "await CreatureCmd.GainBlock(Owner.Creature, "
            f"new BlockVar({amount}, ValueProp.Move), cardPlay);"
        )
    elif op == "draw":
        if branch_draw_upgrade(card):
            then_var, else_var = branch_draw_vars(card)
            expr = (("DynamicVars.Cards.BaseValue" if then_var == "Cards"
                     else f'DynamicVars["{then_var}"].IntValue') if in_then
                    else f'DynamicVars["{else_var}"].IntValue')
        else:
            expr = f'{int(eff["amount"])}m'
        lines.append(f"await CardPileCmd.Draw(choiceContext, {expr}, Owner);")
    elif op == "gain_spark":
        # Branch sparks are literal (no delta grammar reaches them yet;
        # spark_upgrade targets the top-level gain_spark).
        lines.append(
            f'await SparkPower.Gain(choiceContext, Owner.Creature, {int(eff["amount"])}, this);'
        )
    elif op == "burst_energy":
        lines.append(
            f'await KleeBurstResource.Gain(choiceContext, Owner.Creature, {int(eff["amount"])}, this);'
        )
    elif op == "gain_encore":
        lines.append(_stmt_gain_encore(card, eff))
    elif op == "spend_encore":
        # EB-119. Byte-for-byte the call build_body's top-level arm makes --
        # SpendEncoreOrHp, not SpendEncore -- so a spend inside a branch or a
        # mode body overdraws into HP, prints Fanfare and rings the
        # first-spend hooks exactly as a printed one does. Literal, like every
        # other branch resolver: no delta grammar reaches a printed cost.
        lines.append(
            "await FurinaResources.SpendEncoreOrHp("
            f"choiceContext, Owner.Creature, {int(eff['amount'])}, this);")
    elif op == "salon_rotate":
        # EB-118 §5.5. Literal in a branch, like every other branch resolver:
        # no delta grammar reaches a rotation count.
        lines.append("SalonMemberPower.RotateLeftmost("
                     f'Owner.Creature, {int(eff.get("amount", 1))});')
    elif op == "salon_perform":
        lines.append("await SalonMemberPower.PerformLeftmost("
                     f'choiceContext, Owner.Creature, {int(eff.get("amount", 1))});')
    elif op == "energy":
        # DEFECT FIXED HERE (found by G8, 2026-07-26). An `energy` delta made
        # the CanonicalVars entry and the OnUpgrade bump, but the play emitted
        # the LITERAL -- so an upgraded swift_currents gained 2 energy in the
        # mod while the sim gave 3, and the card face printed 2 either way.
        # It shipped that way. Reading the var is what makes the declared
        # upgrade real; the description half is fixed alongside it.
        amount = ('DynamicVars["Energy"].IntValue' if energy_upgrade(card)
                  else int(eff["amount"]))
        lines.append(f"await PlayerCmd.GainEnergy({amount}, Owner);")
    elif op == "place_bomb":
        _emit_place_bomb(card, eff, lines, ctx, str(int(eff["bomb_damage"])))
    elif op == "buff_next_attack":
        # Always literal in a branch: the POWER_UPGRADE_KEYS deltas bind to
        # the first TOP-LEVEL effect only (tier0 upgrades.py), which is what
        # keeps Chevreuse's reaction rider at its printed value while her base
        # buff scales.
        lines.append(
            f"await PowerCmd.Apply<NextAttackUpPower>(choiceContext, "
            f'Owner.Creature, {int(eff["amount"])}, '
            "applier: Owner.Creature, cardSource: this);"
        )
    elif op == "apply_power":
        # EB-125. Byte-for-byte the SELF arm of build_body's top-level
        # apply_power, which is the only arm _branch_op_reason lets through.
        # Literal for the same reason buff_next_attack is: power_upgrade_effect
        # searches TOP-LEVEL effects only, so a nested apply_power is never the
        # effect a ruled power delta binds to -- and a card whose delta finds no
        # top-level home stops loudly there rather than rendering a wrong var
        # here. Stack caps stay with the power's own
        # TryModifyPowerAmountReceived, so the call site is a plain Apply.
        lines.append(
            f"await PowerCmd.Apply<{APPLY_POWERS[eff['power']][0]}>("
            f'choiceContext, Owner.Creature, {int(eff["amount"])}, '
            "applier: Owner.Creature, cardSource: this);"
        )


def _conditional_block(pred: str, then_lines: list[str],
                       else_lines: list[str]) -> str:
    def body(stmts: list[str]) -> str:
        return "\n".join("            " + s.replace("\n", "\n    ")
                         for s in stmts)
    out = f"if ({pred})\n        {{\n{body(then_lines)}\n        }}"
    if else_lines:
        out += f"\n        else\n        {{\n{body(else_lines)}\n        }}"
    return out


def modal_option_class(card: dict, index: int) -> str:
    """The generated class name for one mode's face on the choice screen."""
    return f"{pascal(card['id'])}Mode{chr(ord('A') + index)}"


def _modes_block(card: dict, mode_bodies: list[list[str]]) -> str:
    """The if/else-if ladder over the answered mode index.

    A ladder rather than a `switch`: the branch bodies are the same statement
    lists `_conditional_block` renders, and one renderer for both keeps a mode
    body and a branch body from drifting apart in whitespace alone.
    """
    def body(stmts: list[str]) -> str:
        return "\n".join("            " + s.replace("\n", "\n    ")
                         for s in stmts)

    out = ""
    for i, stmts in enumerate(mode_bodies):
        head = (f"if (modeIndex == {i})" if i == 0
                else (f"\n        else if (modeIndex == {i})"
                      if i < len(mode_bodies) - 1 else "\n        else"))
        out += f"{head}\n        {{\n{body(stmts)}\n        }}"
    return out


def build_body(
    card: dict, profile: CharacterProfile = KLEE_PROFILE
) -> list[str]:
    """OnPlay statements. Every call here has a verified base-game call site."""
    lines = []
    ctx = {"thrown": False}
    spotlight_capable = is_companion(card) or profile is FURINA_PROFILE
    salon_deploy_present = any(
        effect.get("op") == "apply_power"
        and effect.get("power") == "salon_member"
        for effect in card.get("effects", []))
    salon_deployed = False
    if salon_deploy_present:
        lines.append("var salonReplacements = 0;")
    salon_snapshot = salon_scaled_snapshot(card)
    if salon_snapshot is not None:
        # The card's own deploys mutate the company as they run, so the
        # scaled value is captured HERE -- against the pre-play company the
        # card face read -- and spent below. Face and effect are then the
        # same evaluation of the same expression on the same state.
        target = _salon_calc_target(card)
        var = target[2]
        read = (f"DynamicVars.{var}.Calculate(null)"
                if var in ("CalculatedDamage", "CalculatedBlock")
                else f'((CalculatedVar)DynamicVars["{var}"]).Calculate(null)')
        lines.append(f"var {salon_snapshot} = {read};")
    elif added_encore_salon(card) is not None:
        # Same capture discipline for the upgrade-appended encore (SYS-6):
        # the card's own deploy mutates the company mid-resolution, so the
        # scaled value is read HERE, against the pre-play state the face
        # shows, and spent in the IsUpgraded tail below.
        lines.append(
            "var salonScaledEncore = "
            '((CalculatedVar)DynamicVars["Encore"]).Calculate(null);')
    # Predicate snapshots: the sim resets its per-card counters at
    # resolve_card START, so the C# diff bases are captured at the top of
    # OnPlay, before any effect resolves -- not at the conditional's site.
    preds = {e["if"] for e in card["effects"] if e.get("op") == "conditional"}
    if "reaction_triggered_by_this" in preds:
        lines.append("var reactionsAtStart = ReactionEffects.TotalResolved;")
    if "killed_target" in preds:
        lines.append("var enemiesAtStart = CombatState!.HittableEnemies.ToList();")
    if str(card.get("cost")) == "X":
        # tier0 play_card: current_x = energy actually spent. The captured
        # X value (through Hook.ModifyXValue) is the game's same number.
        lines.append("var x = ResolveEnergyXValue();")
    add_anchor = added_effect_anchor(card)
    for eff in card["effects"]:
        op = eff["op"]

        # EB-122. A POSITIONED `add` resolves in the middle of the ruled body,
        # so it is emitted at its anchor rather than after the loop.
        # send_the_runner+ is ruled draw 2 -> discard 1 chosen -> exhaust 1
        # chosen (D2a); appended, it read draw / exhaust / discard, and the
        # player exhausted before being asked what to throw -- a different
        # card, silently.
        if eff is add_anchor:
            lines.extend(_upgrade_add_lines(card, salon_deploy_present))

        if op == "block":
            if salon_calc_rider(card, eff) is not None:
                lines.append(
                    "await CreatureCmd.GainBlock(Owner.Creature, "
                    f"{salon_snapshot}, "
                    "DynamicVars.CalculatedBlock.Props, cardPlay);")
                continue
            if (spotlight_block_rider(card, eff) is not None
                    or block_calc_rider(card, eff) is not None):
                # Base game's own idiom (Mirage): resolve through the same var
                # the face reads, so preview and gain cannot drift.
                lines.append(
                    "await CreatureCmd.GainBlock(Owner.Creature, "
                    "DynamicVars.CalculatedBlock.Calculate(cardPlay.Target), "
                    "DynamicVars.CalculatedBlock.Props, cardPlay);")
                continue
            amount = ("new BlockVar(" + str(int(eff["amount"]))
                      + "m, ValueProp.Move)" if _is_sly_branch(card)
                      else "DynamicVars.Block")
            if salon_deployed:
                amount = (
                    "new BlockVar(DynamicVars.Block.BaseValue * "
                    "(salonReplacements > 0 ? "
                    "SalonConstants.ReplacementDamageMultiplier : 1), "
                    "ValueProp.Move)")
            if spotlight_capable:
                raw = (
                    "DynamicVars.Block.BaseValue * "
                    "(salonReplacements > 0 ? "
                    "SalonConstants.ReplacementDamageMultiplier : 1)"
                    if salon_deployed else "DynamicVars.Block.BaseValue")
                amount = (
                    "new BlockVar(SpotlightSystem.PrintedBlock("
                    f"this, {raw}), ValueProp.Move)")
            lines.append(
                f"await CreatureCmd.GainBlock(Owner.Creature, {amount}, cardPlay);"
            )

        elif op == "draw":
            amount = (str(int(eff["amount"])) if _is_sly_branch(card)
                      else "DynamicVars.Cards.BaseValue")
            if salon_calc_rider(card, eff) is not None:
                amount = f"(int){salon_snapshot}"
            elif salon_deployed:
                amount += (" * (salonReplacements > 0 ? "
                           "SalonConstants.ReplacementNumericMultiplier : 1)")
            lines.append(
                f"await CardPileCmd.Draw(choiceContext, {amount}, Owner);"
            )

        elif op == "damage" and eff["target"] == "self":
            # Unblockable | Unpowered so self-damage ignores our own Block and
            # Strength, matching how the base game models HP cost.
            lines.append(
                "await CreatureCmd.Damage(choiceContext, Owner.Creature, "
                "DynamicVars.HpLoss.BaseValue, "
                "ValueProp.Unblockable | ValueProp.Unpowered, this);"
            )

        elif op == "place_bomb":
            _emit_place_bomb(card, eff, lines, ctx,
                             f"(int)DynamicVars.{bomb_var(card)}.BaseValue")

        elif op == "damage":
            if calc_rider(card, eff) is not None:
                # Face/preview and hit both route through the one var.
                _emit_damage(card, eff, lines, ctx,
                             "DynamicVars.CalculatedDamage")
                continue
            if salon_calc_rider(card, eff) is not None:
                # Same var, but spent from the pre-deploy snapshot: passing
                # the var itself would make AttackCommand call Calculate()
                # after this card's own deploys had already grown the company.
                _emit_damage(card, eff, lines, ctx, salon_snapshot)
                continue
            amount_expr = (str(int(eff["amount"])) + "m"
                           if _is_sly_branch(card)
                           or eff is not damage_var_effect(card)
                           else "DynamicVars.Damage.BaseValue")
            if "bonus_vs_aura" in eff:
                aura_target = (
                    "cardPlay.Target!" if eff["target"] == "enemy"
                    else "auraTarget")
                amount_expr += (
                    f" + (AuraCmd.Find({aura_target}) != null ? "
                    f"{int(eff['bonus_vs_aura'])} : 0)")
            if "bonus_formula" in eff:
                formula = eff["bonus_formula"]
                if formula.endswith("_per_detonation_this_combat"):
                    # The Big One: flat rider on the printed number, before
                    # external buffs -- exactly the sim's `base +=`.
                    per = ('DynamicVars["BonusPer"].IntValue'
                           if bonus_per_upgrade(card)
                           else formula.partition("_per_")[0])
                    # EPOCH 2 / D2: the count is PER-PLAYER now, so the reader
                    # has to say whose. `Owner` on a CardModel is the Player
                    # (the Creature lives at Owner.Creature) -- the same
                    # distinction that bit KokomiResourceHooks. Passing the
                    # owner keeps a co-op partner's detonations out of this
                    # card's bonus.
                    amount_expr += (
                        f" + {per} * "
                        "BombPower.DetonationsThisCombat(CombatState!, Owner)")
                else:
                    n, _, rest = formula.partition("_per_")
                    per_fanfare = rest.partition("_")[0]
                    amount_expr += (
                        f" + {n} * "
                        f"(FurinaResources.ReadableFanfare(Owner.Creature) / {per_fanfare})")
            if salon_deployed:
                amount_expr = (
                    f"({amount_expr}) * "
                    "(salonReplacements > 0 ? 3 : 1)")
            if spotlight_capable:
                amount_expr = (
                    f"SpotlightSystem.PrintedDamage(this, {amount_expr})")
            if "bonus_vs_aura" in eff and eff["target"] == "all_enemies":
                lines.append(
                    "foreach (var auraTarget in "
                    "CombatState!.HittableEnemies.ToList())\n"
                    "        {\n"
                    f"            await DamageCmd.Attack({amount_expr})\n"
                    "                .FromCard(this)\n"
                    "                .Targeting(auraTarget)\n"
                    '                .WithHitFx("vfx/vfx_attack_slash")\n'
                    "                .Execute(choiceContext);\n"
                    "        }")
            else:
                _emit_damage(card, eff, lines, ctx, amount_expr)

        elif op == "gain_spark":
            lines.append(_stmt_gain_spark(card, eff))

        elif op == "spend_spark":
            lines.append(_stmt_spend_spark(card, eff))

        elif op == "burst_energy":
            lines.append(_stmt_burst_energy(card, eff))

        elif op == "gain_charge":
            # The PREMIUM accrual (kickoff 2.1). The universal exhaust->Charge
            # funnel is the relic's, never card text, so these lines are pure
            # bonus on top and carry no identity gate of their own -- GainCharge
            # gates internally.
            lines.append(
                "KokomiResources.GainCharge(Owner.Creature, "
                f"{int(eff['amount'])});")

        elif op == "summon_kurage":
            lines.append(
                "await KurageSummon.Field(choiceContext, Owner.Creature, "
                f"{kurage_turns_expr(card, eff)}, this);")

        elif op == "grant_sly_this_turn":
            # EB-122. The whole verb lives in SlyGrant so its filter and its
            # end-of-turn expiry have ONE home and cannot be re-spelled per
            # card; the generated body is the call. Sim twin:
            # effects._op_grant_sly_this_turn.
            lines.append(
                "await SlyGrant.Grant(choiceContext, Owner, this);")

        elif op == "conscript":
            override = eff.get("cost_override")
            lines.append(
                "await KokomiConscript.Run(choiceContext, Owner, this, "
                f"{int(eff.get('amount', 1))}, "
                f"createMode: {'true' if eff.get('mode') == 'create' else 'false'}, "
                f"costOverride: {override if override is not None else 'null'});")

        elif op == "gain_encore":
            if salon_calc_rider(card, eff) is not None:
                lines.append(
                    "FurinaResources.GainEncore(Owner.Creature, "
                    f"(int){salon_snapshot});")
                continue
            lines.append(
                _stmt_gain_encore(
                    card, eff, salon_scaled=salon_deployed))

        elif op == "spend_encore":
            lines.append(
                "await FurinaResources.SpendEncoreOrHp("
                f"choiceContext, Owner.Creature, {int(eff['amount'])}, this);")

        elif op == "raise_fanfare_cap":
            lines.append(
                "FurinaResources.RaiseFanfareCap("
                "Owner.Creature, DynamicVars[\"FanfareCap\"].IntValue);")

        elif op == "gain_fanfare_floor":
            lines.append(
                "FurinaResources.GainFanfareFloor("
                "Owner.Creature, DynamicVars[\"FanfareFloor\"].IntValue);")

        elif op == "crash_fanfare":
            # The Hyperbeam settle (Track C.2, 2026-07-28), mirroring
            # resources.drop_fanfare_to_floor: Fanfare falls to its floor and
            # the floor falls by the printed amount. The floor MAY GO
            # NEGATIVE, which is ruled; FurinaResources.DropFanfareToFloor
            # owns the clamp so the two engines cannot disagree about it.
            lines.append(
                "FurinaResources.DropFanfareToFloor("
                "Owner.Creature, DynamicVars[\"FloorDrop\"].IntValue);")

        elif op == "salon_bow":
            # The on-demand bow (Track D, 2026-07-28). The LEFTMOST member --
            # the same end of the FIFO queue a deploy into a full stage
            # displaces -- so this reuses the displacement path rather than
            # introducing a second notion of "which member".
            lines.append(
                "await SalonMemberPower.BowLeftmost("
                f"choiceContext, Owner.Creature, {int(eff.get('amount', 1))});")

        elif op == "salon_rotate":
            # EB-118 §5.5. A reorder and nothing else: no tick, no Encore, no
            # bow. Synchronous by signature, which is what guarantees it.
            lines.append(
                "SalonMemberPower.RotateLeftmost("
                f"Owner.Creature, {int(eff.get('amount', 1))});")

        elif op == "salon_perform":
            # EB-118 §5.5. Resolves through the SAME PerformMember the
            # turn-start upkeep calls, so the Encore upkeep, the dry cut, the
            # Focus scaling and the burst particle are inherited here rather
            # than restated on the card.
            lines.append(
                "await SalonMemberPower.PerformLeftmost("
                f"choiceContext, Owner.Creature, {int(eff.get('amount', 1))});")

        elif op == "heal":
            lines.append(
                "await CreatureCmd.Heal(Owner.Creature, "
                "DynamicVars[\"Heal\"].BaseValue);")

        elif op == "apply_power":
            cls = APPLY_POWERS[eff["power"]][0]
            amount = (
                'DynamicVars["PowerAmount"].IntValue'
                if eff is power_upgrade_effect(card)
                else str(int(eff["amount"]))
            )
            if salon_calc_rider(card, eff) is not None:
                amount = f"(int){salon_snapshot}"
            elif salon_deployed and eff["power"] != "salon_member":
                amount = f"{amount} * (salonReplacements > 0 ? 2 : 1)"
            # Stack caps are enforced by the power's own
            # TryModifyPowerAmountReceived (the sim clamps at apply too), so
            # the call site stays a plain Apply.
            if eff["power"] == "salon_member":
                # Salon v2 (rework plan §1): deploys are member-TYPED. The
                # C# enum mirrors tier0's C.SALON_MEMBERS keys.
                # A11: `random` emits a null, which Deploy resolves per
                # iteration off the shared combat RNG stream. The sim rolls
                # per iteration too, so a multi-deploy card fields a mixed
                # stage in both engines.
                member = SALON_MEMBER_CS[eff.get("member", "crabaletta")]
                lines.append(
                    "salonReplacements += await SalonMemberPower.Deploy("
                    f"choiceContext, Owner.Creature, {amount}, this, "
                    f"{member});")
                salon_deployed = True
            elif eff["power"] in ENEMY_APPLY_POWERS:
                # tier0 _op_apply_power -> _pick_targets: chosen enemy or
                # every living enemy. Native debuff classes; applier is us.
                if eff["target"] == "enemy":
                    _target_guard(lines, ctx)
                    lines.append(
                        f"await PowerCmd.Apply<{cls}>(choiceContext, cardPlay.Target, "
                        f"{amount}, applier: Owner.Creature, cardSource: this);"
                    )
                elif eff["target"] == "random_enemy":
                    # tier0 _pick_targets: ONE enemy, rolled. Same shape the
                    # aura emitter uses. Emitted separately because the
                    # all-enemies branch below used to swallow this target and
                    # debuff the whole room off a one-target sheet line.
                    lines.append(NEWLINE.join([
                        "{",
                        "            var debuffCandidates = CombatState!"
                        ".HittableEnemies.ToList();",
                        "            if (debuffCandidates.Count > 0)",
                        "            {",
                        "                var debuffTarget = Owner.RunState"
                        ".Rng.CombatTargets.NextItem(debuffCandidates);",
                        "                if (debuffTarget != null)",
                        "                {",
                        f"                    await PowerCmd.Apply<{cls}>("
                        f"choiceContext, debuffTarget, {amount}, "
                        "applier: Owner.Creature, cardSource: this);",
                        "                }",
                        "            }",
                        "        }",
                    ]))
                else:  # all_enemies (snapshot: an apply cannot kill, but stay
                    # consistent with every other all-enemies loop we emit)
                    lines.append(
                        "foreach (var debuffTarget in CombatState!.HittableEnemies.ToList())\n"
                        "        {\n"
                        f"            await PowerCmd.Apply<{cls}>(choiceContext, debuffTarget, "
                        f"{amount}, applier: Owner.Creature, cardSource: this);\n"
                        "        }"
                    )
            else:
                lines.append(
                    f"await PowerCmd.Apply<{cls}>(choiceContext, Owner.Creature, "
                    f"{amount}, applier: Owner.Creature, cardSource: this);"
                )

        elif op == "detonate":
            # tier0 _op_detonate: only enemies WITH bombs detonate (DetonateOn
            # returns 0 on a bombless target); bonus rides each bomb inside
            # the same pre-amplification sum as bomb_damage_up. The count
            # feeds chance_bomb_per_detonation when the card carries one.
            bonus = int(eff.get("bonus", 0))
            bonus_arg = (
                ', DynamicVars["Bonus"].IntValue' if bonus_upgrade(card)
                else (f", {bonus}" if bonus else "")
            )
            prefix = (
                "var detonations = "
                if any(e.get("op") == "chance_bomb_per_detonation"
                       for e in card["effects"])
                else ""
            )
            if eff["target"] == "enemy":
                _target_guard(lines, ctx)
                lines.append(
                    f"{prefix}await BombPower.DetonateOn(choiceContext, "
                    f"cardPlay.Target{bonus_arg});"
                )
            else:  # all_enemies
                lines.append(
                    f"{prefix}await BombPower.DetonateAll(choiceContext, "
                    f"CombatState!.HittableEnemies.ToList(){bonus_arg});"
                )

        elif op == "modify_bombs":
            # tier0 _op_modify_bombs: every live bomb (or only this round's --
            # the stamp mirrors Bomb.turn_placed) gains the bonus. Effect
            # order is preserved by this loop, so Chain Fuse's own bomb,
            # placed by the NEXT effect, is not buffed -- same as the sim.
            this_round = "true" if eff.get("scope", "all") == "placed_this_turn" else "false"
            bonus_expr = (
                'DynamicVars["Bonus"].IntValue' if bonus_upgrade(card)
                else str(int(eff["bonus"]))
            )
            lines.append(
                f"BombPower.ModifyAll(CombatState!.HittableEnemies, {bonus_expr}, "
                f"placedThisRoundOnly: {this_round}, CombatState!.RoundNumber);"
            )

        elif op == "move_bombs":
            # tier0 _op_move_bombs: gather ALL bombs from other enemies onto
            # the chosen target, +bonus each; stamps travel with the charges.
            bonus_expr = (
                'DynamicVars["Bonus"].IntValue' if bonus_upgrade(card)
                else str(int(eff.get("bonus", 0)))
            )
            _target_guard(lines, ctx)
            lines.append(
                f"await BombPower.MoveAllTo(choiceContext, cardPlay.Target, "
                f"CombatState!.HittableEnemies, {bonus_expr}, Owner.Creature, this);"
            )

        elif op == "chance_bomb_per_detonation":
            # tier0: per detonation this card caused, roll < chance -> fresh
            # bomb on a random living enemy. `detonations` is the DetonateOn/
            # DetonateAll return captured above (blocked_reason guarantees
            # the preceding detonate). Roll and pick both ride CombatTargets,
            # the established in-combat stream.
            chance_expr = (
                'DynamicVars["Chance"].IntValue / 100f' if chance_upgrade(card)
                else f'{float(eff["chance"])}f'
            )
            lines.append(
                "for (var i = 0; i < detonations; i++)\n"
                "        {\n"
                f"            if (Owner.RunState.Rng.CombatTargets.NextFloat() >= {chance_expr}) continue;\n"
                "            var candidates = CombatState!.HittableEnemies.ToList();\n"
                "            if (candidates.Count == 0) break;\n"
                "            var bombTarget = Owner.RunState.Rng.CombatTargets.NextItem(candidates);\n"
                "            if (bombTarget == null) break;\n"
                f'            await BombPower.Place(choiceContext, bombTarget, {int(eff["bomb_damage"])}, '
                "Owner.Creature, this);\n"
                "        }"
            )

        elif op == "discard":
            # G6: an upgradeable count reads the VAR, so the loop bound and
            # the printed face cannot disagree after an upgrade -- the same
            # preview-truth rule the Furina legibility sprint established.
            n = ('DynamicVars["Discards"].IntValue'
                 if plain_discard_upgrade(card) else int(eff.get("amount", 1)))
            if eff.get("select") == "chosen":
                # CHOSEN discard (`select: chosen`), the base-game "Discard N
                # cards" shape. Emitted through the SAME idiom
                # `discard_for_sparks` above uses and for the same reason: the
                # selection screen picks the whole batch BEFORE any of it
                # leaves the hand, so a rider that draws cannot make the drawn
                # card selectable inside the same discard. tier0's
                # `_op_discard` batches its chosen path identically; the two
                # engines therefore agree on selection MEMBERSHIP as well as
                # on count.
                #
                # `FromHand`'s own rule auto-selects a short hand, which is
                # tier0's `if not candidates: break` -- neither engine asks
                # for a choice it cannot offer.
                #
                # Braced so a card carrying two selections (or a chosen
                # discard beside `discard_for_sparks`) cannot redeclare
                # `picked` -- the same scoping the exhaust_from emission uses.
                lines.append(
                    "{\n"
                    "            var picked = (await CardSelectCmd.FromHandForDiscard(\n"
                    "                choiceContext, Owner,\n"
                    "                new CardSelectorPrefs("
                    f"CardSelectorPrefs.DiscardSelectionPrompt, {n}),\n"
                    "                KitGrant.NotKitCard, this)).ToList();\n"
                    "            await CardCmd.Discard(choiceContext, picked);\n"
                    "        }"
                )
            else:
                # Random discard, kit-exempt pool (tier0 _op_discard: re-pool
                # per pick, stop when empty). CombatTargets is the established
                # rng stream for in-combat random picks (bomb targeting
                # idiom). The re-poll is DELIBERATE on this branch and is the
                # sim's own random semantics -- only the chosen branch batches.
                lines.append(
                    f"for (var i = 0; i < {n}; i++)\n"
                    "        {\n"
                    "            var pool = CardPile.Get(PileType.Hand, Owner)?"
                    ".Cards.Where(KitGrant.NotKitCard).ToList();\n"
                    "            if (pool == null || pool.Count == 0) break;\n"
                    "            var victim = Owner.RunState.Rng.CombatTargets.NextItem(pool);\n"
                    "            if (victim == null) break;\n"
                    "            await CardCmd.Discard(choiceContext, victim);\n"
                    "        }"
                )

        elif op == "discard_for_sparks":
            # R36: forced player-chosen discard of N (auto-selects-all on a
            # short hand -- FromHand's own rule), kit-exempt filter; then
            # Sparks priced by the cards ACTUALLY discarded, capped at M.
            # Empty eligible hand -> empty selection -> no Spark.
            if discard_upgrade(card) != (0, 0):
                n = 'DynamicVars["Discards"].IntValue'
                m = 'DynamicVars["Sparks"].IntValue'
            else:
                n = str(int(eff["amount"]))
                m = str(int(eff["sparks"]))
            lines.append(
                "var picked = (await CardSelectCmd.FromHandForDiscard(\n"
                "            choiceContext, Owner,\n"
                "            new CardSelectorPrefs(CardSelectorPrefs.DiscardSelectionPrompt, "
                f"{n}),\n"
                "            KitGrant.NotKitCard, this)).ToList();\n"
                "        await CardCmd.Discard(choiceContext, picked);\n"
                f"        var sparkGain = Math.Min({m}, picked.Count);\n"
                "        if (sparkGain > 0)\n"
                "        {\n"
                "            await SparkPower.Gain(choiceContext, Owner.Creature, sparkGain, this);\n"
                "        }"
            )

        elif op == "cost_mod":
            # tier0 _op_cost_mod: companion_cost_delta_this_turn += delta.
            # Amount is the REDUCTION (positive; PowerModel amounts are
            # non-negative by default).
            lines.append(
                f"await PowerCmd.Apply<CompanionCostThisTurnPower>(choiceContext, "
                f'Owner.Creature, {-int(eff["delta"])}, '
                "applier: Owner.Creature, cardSource: this);"
            )

        elif op == "copy_companion_in_hand":
            # tier0: random companion in hand, fresh copy to hand. The
            # upgrade's copy_cost_override is a play-time IsUpgraded read
            # (patched_dress precedent -- codegen cannot rewrite OnPlay from
            # OnUpgrade).
            cost_line = ""
            if "cost_override" in eff:
                cost_line = (
                    f"                    copyToken.EnergyCost.SetThisCombat({int(eff['cost_override'])});\n"
                )
            elif "copy_cost_override" in upgrade_plan(card)[0]:
                override = int(upgrade_plan(card)[0]["copy_cost_override"])
                cost_line = (
                    "                    if (IsUpgraded)\n"
                    "                    {\n"
                    f"                        copyToken.EnergyCost.SetThisCombat({override});\n"
                    "                    }\n"
                )
            lines.append(
                "{\n"
                "            var companionsInHand = CardPile.Get(PileType.Hand, Owner)?\n"
                "                .Cards.Where(c => c is ICompanionCard).ToList();\n"
                "            if (companionsInHand != null && companionsInHand.Count > 0)\n"
                "            {\n"
                "                var pickedCompanion = Owner.RunState.Rng.CombatTargets.NextItem(companionsInHand);\n"
                "                if (pickedCompanion != null)\n"
                "                {\n"
                "                    var copyToken = CombatState!.CreateCard(\n"
                "                        ModelDb.GetById<CardModel>(pickedCompanion.Id), Owner);\n"
                # R114 / FLAG-2(i): the copy is built from the PRINTED card --
                # combat-acquired state (a conscript discount, a stripped
                # keyword) does NOT travel -- but "an upgraded target still
                # copies as upgraded": the sim rides the `+` id convention,
                # so the C# copy must carry the upgrade too (SYS-4).
                # UpgradeInternal is the game's own instance-upgrade call,
                # verified at vendor/STS2_MCP/McpMod.Helpers.cs:54-66.
                "                    if (pickedCompanion.IsUpgraded)\n"
                "                    {\n"
                "                        copyToken.UpgradeInternal();\n"
                "                    }\n"
                + cost_line
                + "                    await CardPileCmd.AddGeneratedCardToCombat(copyToken, PileType.Hand, Owner);\n"
                "                }\n"
                "            }\n"
                "        }"
            )

        elif op == "copy_spotlighted_in_hand":
            cost_line = ""
            if "cost_override" in eff:
                cost_line = (
                    "                    spotlightCopy.EnergyCost.SetThisCombat("
                    f"{int(eff['cost_override'])});\n")
            elif "copy_cost_override" in upgrade_plan(card)[0]:
                override = int(
                    upgrade_plan(card)[0]["copy_cost_override"])
                cost_line = (
                    "                    if (IsUpgraded)\n"
                    "                    {\n"
                    "                        spotlightCopy.EnergyCost"
                    f".SetThisCombat({override});\n"
                    "                    }\n")
            # AB-s1 (Q9 / R118, verbatim "Yes."): the copy pool excludes KIT
            # cards, matching the sheet and the sim
            # (_op_copy_spotlighted_in_hand's `not c.kit_card`).
            # KitGrant.NotKitCard is the same predicate
            # every other kit-exempt pool in the codebase rides (Crackle,
            # bright_idea, the Kokomi selectors). Recorded as a MOD BEHAVIOUR
            # CHANGE, not a parity repair -- the undiscardable copied kit
            # Burst stops being reachable in game.
            lines.append(
                "{\n"
                "            var spotlightTargets = CardPile.Get("
                "PileType.Hand, Owner)?.Cards\n"
                "                .Where(SpotlightSystem.IsSpotlighted)\n"
                "                .Where(KitGrant.NotKitCard)"
                ".ToList();\n"
                "            if (spotlightTargets != null "
                "&& spotlightTargets.Count > 0)\n"
                "            {\n"
                "                var selectedSpotlight = Owner.RunState.Rng"
                ".CombatTargets.NextItem(spotlightTargets);\n"
                "                if (selectedSpotlight != null)\n"
                "                {\n"
                "                    var spotlightCopy = CombatState!"
                ".CreateCard(\n"
                "                        ModelDb.GetById<CardModel>("
                "selectedSpotlight.Id), Owner);\n"
                # R114 / FLAG-2(i), same rule as the companion copy above: the
                # printed card travels, and so does the UPGRADE -- the sim's
                # fresh copy keys off the instance id, which is `foo+` for an
                # upgraded target (SYS-4: encore_performance copied upgraded
                # cards out unupgraded). UpgradeInternal provenance:
                # vendor/STS2_MCP/McpMod.Helpers.cs:54-66.
                "                    if (selectedSpotlight.IsUpgraded)\n"
                "                    {\n"
                "                        spotlightCopy.UpgradeInternal();\n"
                "                    }\n"
                + cost_line
                + "                    await CardPileCmd"
                ".AddGeneratedCardToCombat(\n"
                "                        spotlightCopy, PileType.Hand, "
                "Owner);\n"
                "                }\n"
                "            }\n"
                "        }")

        elif op == "replay_next_companion":
            lines.append(
                f"await PowerCmd.Apply<ReplayNextCompanionPower>(choiceContext, "
                f'Owner.Creature, {int(eff.get("times", 1))}, '
                "applier: Owner.Creature, cardSource: this);"
            )

        elif op == "copy_companions_played_this_combat":
            # tier0: unique companions played this combat, in first-play
            # order, fresh tokens (cost_override) to hand.
            override_line = ""
            if "cost_override" in eff:
                override_line = (
                    f"            playedToken.EnergyCost.SetThisCombat({int(eff['cost_override'])});\n"
                )
            # G-B1: owner-scoped. The tracker is combat-wide storage, so the
            # query has to name whose plays it wants -- unfiltered, this card
            # copied the co-op partner's companions.
            lines.append(
                "foreach (var companionPlay in CompanionPlays.PlayedThisCombat(CombatState!, Owner))\n"
                "        {\n"
                "            var playedToken = CombatState!.CreateCard(\n"
                "                ModelDb.GetById<CardModel>(companionPlay.Id), Owner);\n"
                # R114 / FLAG-2(i), the same rule as the two copy ops above:
                # the PRINTED card travels, and so does the UPGRADE. The sim
                # records `card.id` at play time (combat._finish_play), which
                # is `foo+` for an upgraded companion, so its replay is
                # upgraded; the C# ledger carries the flag beside the id
                # because ModelDb.GetById rebuilds pristine (BFF-copy).
                # UpgradeInternal provenance:
                # vendor/STS2_MCP/McpMod.Helpers.cs:54-66. Pool IDENTITY is a
                # separate, now-settled question: BFF-dedupe (ruled
                # 2026-08-06) makes `foo` and `foo+` one entry on BOTH sides,
                # so each companion is replayed once, in the upgrade state of
                # its FIRST play.
                "            if (companionPlay.IsUpgraded)\n"
                "            {\n"
                "                playedToken.UpgradeInternal();\n"
                "            }\n"
                + override_line
                + "            await CardPileCmd.AddGeneratedCardToCombat(playedToken, PileType.Hand, Owner);\n"
                "        }"
            )

        elif op in ("apply_aura", "swirl"):
            # tier0 _op_apply_aura / _op_swirl: resolve_hit with 0 damage --
            # ElementalHit.ApplyOnly is exactly that (apply / refresh /
            # consume+react, no damage call). Swirl IS "trigger anemo".
            element = (ELEMENT_CS[eff["element"]] if op == "apply_aura"
                       else "Element.Anemo")
            tgt = eff.get("target", "enemy")
            aura_lines: list[str] = []
            if tgt == "enemy":
                _target_guard(aura_lines, ctx)
                aura_lines.append(
                    f"await ElementalHit.ApplyOnly(choiceContext, cardPlay.Target, "
                    f"{element}, Owner.Creature);"
                )
            elif tgt == "all_enemies":
                aura_lines.append(
                    "foreach (var auraTarget in CombatState!.HittableEnemies.ToList())\n"
                    "        {\n"
                    f"            await ElementalHit.ApplyOnly(choiceContext, auraTarget, "
                    f"{element}, Owner.Creature);\n"
                    "        }"
                )
            else:  # random_enemy
                aura_lines.append(
                    "{\n"
                    "            var auraCandidates = CombatState!.HittableEnemies.ToList();\n"
                    "            if (auraCandidates.Count > 0)\n"
                    "            {\n"
                    "                var auraTarget = Owner.RunState.Rng.CombatTargets.NextItem(auraCandidates);\n"
                    "                if (auraTarget != null)\n"
                    "                {\n"
                    f"                    await ElementalHit.ApplyOnly(choiceContext, auraTarget, "
                    f"{element}, Owner.Creature);\n"
                    "                }\n"
                    "            }\n"
                    "        }"
                )
            if salon_deployed:
                body = "\n".join(
                    "            " + statement.replace("\n", "\n    ")
                    for statement in aura_lines)
                lines.append(
                    "for (var salonRepeat = 0; salonRepeat < "
                    "(salonReplacements > 0 ? "
                    "SalonConstants.ReplacementNumericMultiplier : 1); "
                    "salonRepeat++)\n"
                    "        {\n"
                    f"{body}\n"
                    "        }")
            else:
                lines.extend(aura_lines)

        elif op == "refresh_all_auras":
            # tier0 _op_refresh_all_auras: every living enemy holding an aura
            # has its remaining duration set back to full. The helper reuses
            # AuraPower's own same-element refresh path, so the value it
            # refreshes TO is defined once.
            lines.append(
                "await CurtainCallHooks.RefreshAllAuras("
                "choiceContext, Owner.Creature, this);"
            )

        elif op == "grow_damage":
            # tier0 _op_grow_damage (Rampage): permanently raise THIS card
            # instance's printed damage. Targets whichever var actually holds
            # the printed number -- CalculationBase on a card carrying a
            # rider, Damage otherwise -- which is the same var the upgrade
            # bumps, so growth and upgrade compound instead of one silently
            # overwriting the other. ResetToBase + the display invalidation
            # are BombPower.SyncDisplay's idiom: without them the card resolves
            # overwriting the other.
            #
            # A bare `BaseValue +=` is the whole operation: DynamicVar's
            # BaseValue setter calls ResetToBase() itself, so the enchanted
            # and preview values follow without a second statement. NOT
            # UpgradeValueBy -- that sets WasJustUpgraded and would paint the
            # number as freshly upgraded every time the card grows.
            grow_var = ('DynamicVars.CalculationBase'
                        if any(calc_rider(card, e) is not None
                               for e in card.get("effects", []))
                        else "DynamicVars.Damage")
            lines.append(f"{grow_var}.BaseValue += {int(eff['amount'])}m;")

        elif op == "buff_next_attack":
            # tier0 _op_buff_next_attack -> next_attack_up, consumed by the
            # next attack card (NextAttackUpPower's AfterCardPlayed).
            amount = ('DynamicVars["PowerAmount"].IntValue'
                      if eff is power_upgrade_effect(card)
                      else str(int(eff["amount"])))
            lines.append(
                f"await PowerCmd.Apply<NextAttackUpPower>(choiceContext, "
                f"Owner.Creature, {amount}, "
                "applier: Owner.Creature, cardSource: this);"
            )

        elif op == "block_next_turn":
            # tier0 _op_block_next_turn: a power the sim POPS at the next
            # player turn start, granting the Block after that turn's reset.
            # An upgradeable amount reads the var OnUpgrade bumps -- a literal
            # here is how tideline_watch and sayu_daruma_gift shipped upgrades
            # that displayed and granted the base number (SYS-1).
            amount = ('DynamicVars["BlockNextTurn"].IntValue'
                      if block_next_turn_upgrade(card)
                      else str(int(eff["amount"])))
            if spotlight_capable:
                amount = f"(int)SpotlightSystem.PrintedBlock(this, {amount})"
            lines.append(
                f"await PowerCmd.Apply<BlockNextTurnPower>(choiceContext, "
                f"Owner.Creature, {amount}, "
                "applier: Owner.Creature, cardSource: this);"
            )

        elif op == "energy":
            # tier0 _op_energy: flat gain, no cap (the game clamps nothing
            # either -- PlayerCmd.GainEnergy is the base-game call).
            # An upgradeable amount reads the var. This is the TOP-LEVEL
            # emitter; there is a second one for branch bodies, and the fix
            # had to land on both -- patching only the other one produced a
            # card whose FACE said "Gain {Energy:diff()}" while its play still
            # granted the base, which is the same preview-vs-effect drift in a
            # new place.
            amount = ('DynamicVars["Energy"].IntValue' if energy_upgrade(card)
                      else int(eff["amount"]))
            lines.append(f'await PlayerCmd.GainEnergy({amount}, Owner);')

        elif op == "scry_discard":
            # tier0 _op_scry_discard looks at the top N and discards the
            # "worst" via the shared pilot heuristic -- which is the sim's
            # stand-in for PLAYER CHOICE (R36 precedent: Crackle's heuristic
            # discard landed as FromHandForDiscard). Top of pile is index 0
            # (CardPile.MoveToTopInternal inserts at 0), so Take(N) is the
            # sim's draw_pile[:n]. The unpicked card stays in place.
            n = int(eff["amount"])
            lines.append(
                "{\n"
                f"            var top = CardPile.Get(PileType.Draw, Owner)?.Cards.Take({n}).ToList();\n"
                "            if (top != null && top.Count > 0)\n"
                "            {\n"
                "                var scryPick = (await CardSelectCmd.FromSimpleGrid(\n"
                "                    choiceContext, top, Owner,\n"
                "                    new CardSelectorPrefs(CardSelectorPrefs.DiscardSelectionPrompt, 1))).ToList();\n"
                "                await CardCmd.Discard(choiceContext, scryPick);\n"
                "            }\n"
                "        }"
            )

        elif op == "exhaust_from" and eff.get("select") == "chosen":
            # Kokomi: the player chooses. Kit cards stay exempt (v1.9 -- the
            # Burst is never fodder), the same filter the discard ops ride.
            # Every exhaust pays Charge through the relic funnel, so this op
            # is her engine's throttle and the CHOICE is the gameplay -- a
            # random pick would not be a smaller version of this card, it
            # would be a different card.
            # ROTATION LAW ([USER] 2026-08-23): the selector offers one of
            # HER cards -- KokomiResources.OwnCard, which is NotKitCard AND
            # not a Status/Curse. Sim twin: _op_exhaust_from drops junk from
            # the unfiltered pool under her relic hook. A card that may eat
            # junk says so with an explicit `filter:` (the branch below).
            n = ('DynamicVars["Exhausts"].IntValue'
                 if exhaust_upgrade(card) else str(int(eff.get("amount", 1))))
            # EB-118: the selection's identity context. Opened BEFORE the
            # screen so a cancelled or empty selector leaves an EMPTY context
            # rather than the previous effect's, recorded per victim, closed
            # once -- the same three beats _op_exhaust_from makes, and the
            # reason a second selector on one card replaces the first.
            lines.append(NEWLINE.join([
                "{",
                "            ExhaustSelection.Open(this);",
                "            var toExhaust = (await CardSelectCmd.FromHand(",
                "                choiceContext, Owner,",
                "                new CardSelectorPrefs(",
                "                    CardSelectorPrefs.ExhaustSelectionPrompt, "
                f"{n}),",
                "                KokomiResources.OwnCard, this)).ToList();",
                "            foreach (var victim in toExhaust)",
                "            {",
                "                ExhaustSelection.Record(this, victim);",
                "                await CardCmd.Exhaust(choiceContext, victim);",
                "            }",
                "",
                "            ExhaustSelection.Close(this);",
                "        }",
            ]))

        elif op == "exhaust_from":
            # tier0 _op_exhaust_from with filter status: RANDOM victim from
            # the hand's Status cards (not chosen -- the sim rolls rng).
            # EB-118: a filtered exhaust records its victims too -- the
            # context is the op's, not Kokomi's. Opened unconditionally so
            # "no Status in hand" reads as an empty selection on both sides.
            lines.append(
                "{\n"
                "            ExhaustSelection.Open(this);\n"
                "            var statusCards = CardPile.Get(PileType.Hand, Owner)?\n"
                "                .Cards.Where(c => c.Rarity == CardRarity.Status).ToList();\n"
                "            if (statusCards != null && statusCards.Count > 0)\n"
                "            {\n"
                "                var victim = Owner.RunState.Rng.CombatTargets.NextItem(statusCards);\n"
                "                if (victim != null)\n"
                "                {\n"
                "                    ExhaustSelection.Record(this, victim);\n"
                "                    await CardCmd.Exhaust(choiceContext, victim);\n"
                "                }\n"
                "            }\n"
                "\n"
                "            ExhaustSelection.Close(this);\n"
                "        }"
            )

        elif op == "recall_to_draw":
            # EB-118, exhaust source. The whole verb -- the eligible pool, the
            # top-of-draw placement and the gained Exhaust -- lives in
            # RecallFromExhaust so the six constraints have ONE C# home and
            # cannot be re-spelled per card. The generated body is the call.
            # Sim twin: effects._op_recall_to_draw with `from: exhaust`.
            #
            # EB-122: the DISCARD source is the same verb reading the other
            # pile, and it has its own home for the same reason -- the two are
            # deliberately asymmetric (unfiltered vs §6.4-filtered, no loan
            # keyword vs Exhaust), so one class holding both would have to
            # branch on the source at every line.
            n = str(int(eff.get("amount", 1)))
            home = ("RecallFromExhaust"
                    if eff.get("from", "discard") == "exhaust"
                    else "RecallFromDiscard")
            lines.append(
                f"await {home}.Recall(\n"
                f"            choiceContext, Owner, this, {n});"
            )

        elif op == "add_card":
            zone = eff.get("zone") or eff.get("to", "discard")
            pile = "PileType.Hand" if zone == "hand" else "PileType.Discard"
            n = int(eff.get("amount", 1))
            if "pool" in eff:
                # Pool resolved from the sheet at generation time; picks are
                # WITH replacement (tier0: rng.choice per pick), each pick a
                # fresh instance. AddGeneratedCardToCombat's own full-hand
                # rule (redirect to discard) is the sim's _add_token rule.
                members = _pool_members(eff["pool"], profile)
                count = ('DynamicVars["Stash"].IntValue'
                         if stash_upgrade(card) else str(n))
                model_list = ",\n".join(
                    f"                ModelDb.Card<{pascal(m['id'])}>()"
                    for m in members)
                cost_line = ""
                if "cost_override" in eff:
                    # tier0 token.cost stays overridden for the token's whole
                    # combat lifetime -> SetThisCombat.
                    cost_line = (f"                token.EnergyCost.SetThisCombat("
                                 f'{int(eff["cost_override"])});\n')
                lines.append(
                    "{\n"
                    "            var stashPool = new List<CardModel>\n"
                    "            {\n"
                    f"{model_list}\n"
                    "            };\n"
                    f"            for (var i = 0; i < {count}; i++)\n"
                    "            {\n"
                    "                var canonical = Owner.RunState.Rng.CombatTargets.NextItem(stashPool);\n"
                    "                if (canonical == null) break;\n"
                    "                var token = CombatState!.CreateCard(canonical, Owner);\n"
                    f"{cost_line}"
                    f"                await CardPileCmd.AddGeneratedCardToCombat(token, {pile}, Owner);\n"
                    "            }\n"
                    "        }"
                )
            else:
                cid = eff.get("card_id") or eff.get("card")
                cls = ADD_CARD_CLASSES[cid]
                token_lines = (
                    f"            var token = CombatState!.CreateCard<{cls}>(Owner);\n"
                    f"            await CardPileCmd.AddGeneratedCardToCombat(token, {pile}, Owner);\n"
                )
                body = token_lines if n == 1 else (
                    f"            for (var i = 0; i < {n}; i++)\n"
                    "            {\n"
                    + token_lines.replace("            ", "                ")
                    + "            }\n"
                )
                lines.append("{\n" + body + "        }")

        elif op == "generate_guest_star":
            override = eff.get("cost_override")
            ruled_override = upgrade_plan(card)[0].get(
                "generate_cost_override")
            if override is not None:
                override_expr = str(int(override))
            elif ruled_override is not None:
                override_expr = (
                    f"IsUpgraded ? {int(ruled_override)} : (int?)null")
            else:
                override_expr = "null"
            lines.append(
                "await GuestStarGenerator.Generate("
                f"choiceContext, this, \"{eff['rarity']}\", "
                f"{int(eff.get('amount', 1))}, {override_expr});")

        elif op == "conditional":
            then = eff.get("then", [])
            if any(e.get("op") == "repeat_this" for e in then):
                # Evaluated at the conditional's position (sim: the predicate
                # reads counters as of this point in the effect list); the
                # replay itself lands after the list (repeat tail below).
                times = int(then[0].get("times", 1))
                lines.append(
                    f"var repeatTimes = ({predicate_cs(eff['if'])}) ? {times} : 0;"
                )
            else:
                pred = predicate_cs(eff["if"])
                if condition_upgrade(card):
                    # condition: unconditional (tier0 hoists the then-branch
                    # on upgrade) -- the upgraded card runs it always.
                    pred = f"IsUpgraded || {pred}"
                cb_state = {"pending": conditional_bonus_upgrade(card) > 0}
                then_lines: list[str] = []
                for e in then:
                    _emit_branch_op(
                        card, e, then_lines, ctx, True, cb_state,
                        spotlight_capable)
                else_lines: list[str] = []
                for e in eff.get("else", []):
                    _emit_branch_op(
                        card, e, else_lines, ctx, False, cb_state,
                        spotlight_capable)
                lines.append(_conditional_block(pred, then_lines, else_lines))

        elif op == "choose_one":
            # EB-118 sec.5.4. The screen, the co-op sync and the automation
            # seam are all the base game's (ModalChoice wraps them); what is
            # generated is the option list, the record, and the ladder.
            modes = eff["modes"]
            options = ",\n            ".join(
                f"ModalChoice.CreateOption<{modal_option_class(card, i)}>(Owner)"
                for i in range(len(modes)))
            lines.append(
                "var modeOptions = new List<CardModel>\n        {\n"
                f"            {options},\n        }};")
            lines.append("var modeIndex = await ModalChoice.SelectMode("
                         "choiceContext, Owner, modeOptions);")
            labels = ", ".join(f'"{cs_escape(m["label"])}"' for m in modes)
            lines.append("ModalChoice.RecordChoice(this, modeIndex, "
                         f"new[] {{ {labels} }}[modeIndex]);")
            mode_bodies: list[list[str]] = []
            for mode in modes:
                stmts: list[str] = []
                for e in mode["effects"]:
                    _emit_branch_op(card, e, stmts, ctx, True,
                                    {"pending": False}, spotlight_capable)
                mode_bodies.append(stmts)
            lines.append(_modes_block(card, mode_bodies))

    # Structural upgrade append (tier0 upgrades.py: card.effects.append).
    # It resolves after every base effect and before the repeat tail -- unless
    # `add_before` gave it a position, in which case the loop above has already
    # emitted it at that op and this is a no-op.
    if added_effect_anchor(card) is None:
        lines.extend(_upgrade_add_lines(card, salon_deploy_present))

    # Repeat tail (sim resolve_card): a repeat re-resolves the effect list
    # minus the repeat machinery, `times` more times. The replayed ops are
    # REPEAT_SAFE_OPS / UPGRADE_REPEAT_OPS only (upgrade_plan and
    # blocked_reason both gate on it), so the block declares no method-scope
    # locals twice.
    rep = next((e for e in card["effects"] if e.get("op") == "conditional"
                and any(x.get("op") == "repeat_this"
                        for x in e.get("then", []))), None)
    if rep is not None:
        lines.append(
            "for (var r = 0; r < repeatTimes; r++)\n        {\n"
            + _repeat_body(card, ctx, skip=rep)
            + "\n        }"
        )
    elif added_repeat_upgrade(card):
        # R130: the repeat arrives from the UPGRADE (`add: {op: repeat_this}`)
        # rather than from a printed conditional, so the gate is IsUpgraded
        # and `times` is the literal the sheet ruled. Same body, same law.
        lines.append(
            f"if (IsUpgraded)\n        {{\n"
            f"            for (var r = 0; r < {added_repeat_upgrade(card)}; r++)\n"
            "            {\n"
            + _repeat_body(card, ctx, skip=None, indent=16)
            + "\n            }\n        }"
        )

    return lines


def _upgrade_add_lines(card: dict, salon_deploy_present: bool) -> list[str]:
    """The IsUpgraded-gated statements a structural `add` delta contributes.

    Factored out (EB-122) because the emission now has TWO sites: appended
    after the base effects, which is what every `add` did before, and inserted
    at the op an `add_before` names. One list, two call sites, so the two
    positions cannot come to mean different bodies.
    """
    lines: list[str] = []
    if added_draw_upgrade(card):
        lines.append(
            "if (IsUpgraded)\n"
            "        {\n"
            "            await CardPileCmd.Draw(choiceContext, DynamicVars.Cards.BaseValue, Owner);\n"
            "        }"
        )
    if added_encore_upgrade(card):
        if added_encore_salon(card) is not None:
            # SYS-6: replacement-scaled through the var the face renders, so
            # the printed number and the grant cannot drift.
            amount = "(int)salonScaledEncore"
        else:
            amount = str(added_encore_upgrade(card))
            if salon_deploy_present:
                # Non-static deploy count: the closed-form var is
                # unavailable, so the grant keeps the inline rule.
                amount += (" * (salonReplacements > 0 ? "
                           "SalonConstants.ReplacementNumericMultiplier : 1)")
        lines.append(
            "if (IsUpgraded)\n"
            "        {\n"
            "            FurinaResources.GainEncore("
            f"Owner.Creature, {amount});\n"
            "        }"
        )
    if added_block_upgrade(card):
        # EB-122. Inline BlockVar, NOT a CanonicalVars entry: BaseLib
        # auto-detects `GainsBlock` from that list, and a card whose Block
        # exists only after a smith must not claim it before one -- tier0's
        # Nimble predicate reads the base row, so the declaration would be an
        # eligibility split (lint_enchant_parity) rather than a var. The
        # upgraded instance answers true through the GainsBlock override the
        # emitter writes instead. Same literal shape a Sly branch's Block uses.
        lines.append(
            "if (IsUpgraded)\n"
            "        {\n"
            "            await CreatureCmd.GainBlock(Owner.Creature, "
            f"new BlockVar({added_block_upgrade(card)}m, ValueProp.Move), "
            "cardPlay);\n"
            "        }"
        )
    if added_discard_upgrade(card):
        # EB-122. Byte-for-byte the chosen-discard emitter's own screen -- one
        # selection for the whole batch, kit-exempt pool -- so an appended
        # throw and a printed one cannot come to mean different things. Braced
        # for the same reason that one is: `picked` may not be redeclared.
        lines.append(
            "if (IsUpgraded)\n"
            "        {\n"
            "            var pickedUpgrade = (await CardSelectCmd.FromHandForDiscard(\n"
            "                choiceContext, Owner,\n"
            "                new CardSelectorPrefs("
            f"CardSelectorPrefs.DiscardSelectionPrompt, {added_discard_upgrade(card)}),\n"
            "                KitGrant.NotKitCard, this)).ToList();\n"
            "            await CardCmd.Discard(choiceContext, pickedUpgrade);\n"
            "        }"
        )
    return lines


def _repeat_body(card: dict, ctx: dict, skip: dict | None,
                 indent: int = 12) -> str:
    """The replayed effect list for a repeat, as an indented C# block.

    Mirrors resolve_card: every effect except the repeat machinery itself.
    Shared by the printed repeat-conditional tail and the R130 upgrade-added
    repeat so the two cannot drift.
    """
    body: list[str] = []
    for eff in card["effects"]:
        if skip is not None and eff is skip:
            continue
        op = eff["op"]
        if op == "damage":
            _emit_damage(card, eff, body, ctx, "DynamicVars.Damage.BaseValue")
        elif op == "block":
            body.append(
                "await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block, cardPlay);"
            )
        elif op == "draw":
            body.append(
                "await CardPileCmd.Draw(choiceContext, DynamicVars.Cards.BaseValue, Owner);"
            )
        elif op == "gain_spark":
            body.append(_stmt_gain_spark(card, eff))
        elif op == "burst_energy":
            body.append(_stmt_burst_energy(card, eff))
        elif op == "salon_bow":
            body.append(
                "await SalonMemberPower.BowLeftmost("
                f"choiceContext, Owner.Creature, {int(eff.get('amount', 1))});")
        elif op == "salon_rotate":
            body.append(
                "SalonMemberPower.RotateLeftmost("
                f"Owner.Creature, {int(eff.get('amount', 1))});")
        elif op == "salon_perform":
            body.append(
                "await SalonMemberPower.PerformLeftmost("
                f"choiceContext, Owner.Creature, {int(eff.get('amount', 1))});")
    pad = " " * indent
    return "\n".join(pad + s.replace("\n", "\n" + " " * 4) for s in body)


# Predicates that are true only because something the card hit is now DEAD.
# Inside such a branch the killed body is already out of the live-enemy
# population both engines roll `random_enemy` against (tier0 _pick_targets
# filters living_enemies; TargetingRandomOpponents draws from HittableEnemies),
# so a random pick CANNOT return the corpse and the face is entitled to print
# the stronger word. DERIVED, not a card special case: it reads the branch's
# own predicate, and it is deliberately gated to the THEN arm -- in an `else`
# arm the predicate is false, nothing died, and "other" would be a lie.
KILL_PREDICATES = frozenset({"killed_target", "killed_target_fatal"})


def _branch_amount_text(card: dict, eff: dict, key: str) -> str:
    """The rendered form of `_branch_amount`: a bare number, or the
    `{IfUpgraded:show:up|base}` swap beside it. EB-140; kept next to the
    emitter it mirrors so the face and the effect cannot print different
    numbers."""
    base = int(eff["amount"])
    delta = (conditional_block_upgrade(card) if key == "conditional_block"
             else conditional_damage_upgrade(card))
    if not delta or not _CONDITIONAL_DELTA_OPS[key](eff):
        return str(base)
    return f"{{IfUpgraded:show:{base + delta}|{base}}}"


def _branch_text(card: dict, branch: list[dict], in_then: bool,
                 predicate: str = "") -> str:
    """Card text for a conditional branch: literal numbers unless a ruled
    delta claims the var (mirrors _emit_branch_op's amount policy)."""
    bits = []
    cb_pending = in_then and conditional_bonus_upgrade(card) > 0
    after_kill = in_then and predicate in KILL_PREDICATES
    rnd = (" to a random other enemy" if after_kill
           else " to a random enemy")
    for e in branch:
        op = e["op"]
        if op == "damage":
            tgt = {"all_enemies": " to ALL enemies",
                   "random_enemy": rnd,
                   "random_enemies": rnd}.get(e["target"], "")
            if cb_pending:
                cb_pending = False
                bits.append(f"deal {{ExtraDamage:diff()}} damage{tgt}")
            else:
                bits.append(
                    f'deal {_branch_amount_text(card, e, "conditional_damage")}'
                    f" damage{tgt}")
        elif op == "block":
            bits.append(
                f'gain {_branch_amount_text(card, e, "conditional_block")} '
                "[gold]Block[/gold]")
        elif op == "draw":
            if branch_draw_upgrade(card):
                then_var, else_var = branch_draw_vars(card)
                var = then_var if in_then else else_var
                bits.append(
                    f"draw {{{var}:diff()}} card{{{var}:plural:|s}}")
            else:
                n = int(e["amount"])
                bits.append("draw 1 card" if n == 1 else f"draw {n} cards")
        elif op == "gain_spark":
            n = int(e["amount"])
            bits.append("gain 1 [gold]Spark[/gold]" if n == 1
                        else f"gain {n} [gold]Sparks[/gold]")
        elif op == "burst_energy":
            bits.append(f'gain {int(e["amount"])} [gold]Burst Energy[/gold]')
        elif op == "gain_charge":
            bits.append(f'gain {int(e["amount"])} [gold]Charge[/gold]')
        elif op == "summon_kurage":
            bits.append("summon [gold]Bake-Kurage[/gold]")
        elif op == "conscript":
            bits.append(_conscript_phrase(e))
        elif op == "gain_encore":
            base = int(e["amount"])
            delta = encore_upgrade(card)
            amount = (
                f"{{IfUpgraded:show:{base + delta}|{base}}}"
                if delta else str(base))
            bits.append(f"gain {amount} [gold]Encore[/gold]")
        elif op == "spend_encore":
            # EB-119. The shortfall clause is not decoration -- it is the
            # difference between this op and the encore_cost gate, and the
            # top-level arm in build_description prints it too.
            bits.append(f'spend {int(e["amount"])} [gold]Encore[/gold] '
                        "(losing HP for any shortfall)")
        elif op == "energy":
            bits.append(f"gain {int(e['amount'])} Energy")
        elif op == "place_bomb":
            n, d = e["amount"], int(e["bomb_damage"])
            where = _bomb_where(e["target"], n == 1)
            if n == 1:
                bits.append(f"place a [gold]Bomb[/gold]{where} dealing {d} damage")
            else:
                bits.append(
                    f"place {n} [gold]Bombs[/gold]{where}, each dealing {d} damage")
        elif op == "buff_next_attack":
            # Literal: POWER_UPGRADE_KEYS deltas bind to the first TOP-LEVEL
            # effect, so a branch rider never renders a var.
            bits.append(
                f'your next Attack deals {int(e["amount"])} more damage')
        elif op == "apply_power":
            # EB-125. The power's own template, lowercased into the branch
            # clause and stripped of its full stop, so "If your Exhaust pile
            # has 3 or more cards: at the start of your turn, gain 1 Block."
            # reads as one sentence. Literal amount, same rule as
            # buff_next_attack above.
            txt = (APPLY_POWERS[e["power"]][2]
                   .replace("{X}", str(int(e["amount"])))
                   .replace("{XS}", "" if int(e["amount"]) == 1 else "s")
                   .replace("{TO}", "").rstrip("."))
            bits.append(txt[0].lower() + txt[1:])
        else:
            # A branch op with no text arm renders an EMPTY clause -- which is
            # how Chevreuse first generated "If a reaction triggered: ."
            # BRANCH_OPS and this table must move together.
            raise SystemExit(
                f"gen_klee_cards: {card['id']}: branch op '{op}' is in "
                "BRANCH_OPS but has no _branch_text arm -- it would render an "
                "empty clause.")
    return " and ".join(bits) + "."


_KLEE_ROW_IDS: set[str] | None = None


def _is_klee_row(card: dict) -> bool:
    """Is this row on KLEE's sheet? EB-118 sec.4.6's scope, and only that.

    THE MECHANIC IS NOT KLEE-ONLY and this gate does not pretend otherwise:
    `combat.play_card` pays BURST_PER_SKILL_TAG to ANY character with a Burst
    meter, so Furina's thirteen `skill_tag` rows and Kokomi's one pay the
    same invisible 5. sec.4.6 sits under the packet's Klee section and rules
    "every one of the FIFTEEN", so fifteen faces is what this batch prints.
    Extending the line to the other fourteen is the same legibility argument
    and is deliberately NOT taken here -- it is a change to two other
    characters' faces that no ruling in this packet asked for.
    """
    global _KLEE_ROW_IDS
    if _KLEE_ROW_IDS is None:
        _KLEE_ROW_IDS = {row["id"] for row in
                         yaml.safe_load(SHEET.read_text(encoding="utf-8"))}
    return card.get("id") in _KLEE_ROW_IDS

def _upgrade_add_text(card: dict) -> list[str]:
    """The `{IfUpgraded:show:...|}` clauses a structural `add` contributes.

    EB-122: factored out beside `_upgrade_add_lines` and for the same reason.
    The FACE has to place the new sentence where the new effect resolves, or a
    positioned upgrade would read in one order and play in another -- which is
    the failure the position exists to prevent, wearing different clothes.
    Every payload is pipe-free, the one nesting the swap-parse forbids.
    """
    out: list[str] = []
    if added_draw_upgrade(card):
        n = added_draw_upgrade(card)
        draw = "Draw 1 card." if n == 1 else f"Draw {n} cards."
        out.append("{IfUpgraded:show:" + draw + "|}")
    if added_encore_upgrade(card):
        n = added_encore_upgrade(card)
        if added_encore_salon(card) is not None:
            # SYS-6: the appended encore doubles on a replacement deploy, so
            # the face renders the live var, not the unscaled literal.
            out.append(
                "{IfUpgraded:show:Gain {Encore:diff()} "
                "[gold]Encore[/gold].|}")
        else:
            out.append(
                "{IfUpgraded:show:Gain "
                f"{n} [gold]Encore[/gold].|}}")
    if added_block_upgrade(card):
        out.append(
            "{IfUpgraded:show:Gain "
            f"{added_block_upgrade(card)} [gold]Block[/gold].|}}")
    if added_discard_upgrade(card):
        # The chosen-discard emitter's own wording ("Discard 1 card."), so an
        # appended throw and a printed one read identically.
        n = added_discard_upgrade(card)
        out.append(
            "{IfUpgraded:show:Discard "
            f"{n} card{'' if n == 1 else 's'}.|}}")
    return out


def build_description(card: dict) -> str:
    """
    Card text. Syntax is copied from base-game strings observed at runtime:
    single-braced SmartFormat placeholders, :diff() for the upgrade delta, and
    [gold] for keyword highlight.
    """
    parts = []
    deltas = upgrade_plan(card)[0]
    for field, label in (("encore_cost", "Encore"),
                         ("fanfare_cost", "Fanfare")):
        base_cost = int(card.get(field, 0))
        if not base_cost:
            continue
        delta = int(deltas.get(field, 0))
        rendered = (
            f"{{IfUpgraded:show:{max(0, base_cost + delta)}|{base_cost}}}"
            if delta else str(base_cost))
        parts.append(f"Spend {rendered} [gold]{label}[/gold].")
    salon_named = False          # B5: has a deploy already said "your Salon"?
    deploy_amounts, deploy_skip = merged_deploy_text(card)
    add_anchor = added_effect_anchor(card)
    for eff_index, eff in enumerate(card["effects"]):
        if eff_index in deploy_skip:
            continue
        op = eff["op"]

        # EB-122: a positioned `add` reads where it resolves. Placed BEFORE
        # the skip check would be wrong -- a merged deploy still occupies its
        # position -- so it sits with the sentence it precedes.
        if eff is add_anchor:
            parts.extend(_upgrade_add_text(card))

        if op == "block":
            if _is_sly_branch(card):
                parts.append(
                    f'Gain {int(eff["amount"])} [gold]Block[/gold].')
                continue
            tok = ("CalculatedBlock"
                   if spotlight_block_rider(card, eff) is not None
                   or salon_calc_rider(card, eff) is not None
                   or block_calc_rider(card, eff) is not None else "Block")
            parts.append(f"Gain {{{tok}:diff()}} [gold]Block[/gold].")
            # The L-C bargain both ways: a CONVERTED rider's arithmetic moves
            # to the hover tip, but the face must still declare that the card
            # scales, or it reads as a flat number on the reward screen -- the
            # exact misread B1 shipped. The damage path has always emitted
            # this marker; the block path did not, so B1's fix traded a silent
            # drop for a silent number. Fixed here (A13).
            if block_calc_rider(card, eff) is not None:
                formula = eff.get("bonus_formula", "")
                stat = ("Salon" if formula.endswith("_per_salon_member")
                        else "Companions"
                        if formula.endswith("_per_companion_played_this_turn")
                        else formula.rpartition("_")[2].title())
                parts.append(f"Scales with [gold]{stat}[/gold].")

        elif op == "block_next_turn":
            if block_next_turn_upgrade(card):
                # The next-turn half moves with the upgrade, so the face must
                # show the NEW number (SYS-1: tideline_watch printed 8 while
                # the sim banked 12).
                parts.append(
                    "At the start of your next turn, gain "
                    "{BlockNextTurn:diff()} [gold]Block[/gold].")
            else:
                # Literal: the `block` delta binds to the plain block op
                # (sheet: "now-block 3->5; next-turn block stays 3").
                parts.append(
                    f'At the start of your next turn, gain {int(eff["amount"])} '
                    "[gold]Block[/gold].")

        elif op == "draw":
            # {Cards:plural:|s} pluralizes off the LIVE value, so "Draw 1
            # card" correctly becomes "Draw 2 cards" after upgrade. This is
            # the token BaseLib's SimpleLoc pipeline generates for "card(s)"
            # in #-prefixed strings; we emit runtime form directly.
            if _is_sly_branch(card):
                n = int(eff["amount"])
                parts.append("Draw 1 card." if n == 1 else f"Draw {n} cards.")
                continue
            v = ("DrawCards" if salon_calc_rider(card, eff) is not None
                 else "Cards")
            parts.append(f"Draw {{{v}:diff()}} card{{{v}:plural:|s}}.")

        elif op == "place_bomb":
            var = bomb_var(card)
            n = eff["amount"]
            if isinstance(n, str):
                # X_plus_N renders "X+N"; with a ruled bombs delta the +N
                # rides the Bombs var so the upgrade shows.
                if bombs_upgrade(card):
                    n = "X+{Bombs:diff()}"
                else:
                    n = f'X+{int(n[len("X_plus_"):])}' if n != "X" else "X"
            where = _bomb_where(eff["target"], n == 1)
            if n == 1:
                parts.append(
                    f"Place a [gold]Bomb[/gold]{where} dealing {{{var}:diff()}} damage."
                )
            else:
                parts.append(
                    f"Place {n} [gold]Bombs[/gold]{where}, each dealing "
                    f"{{{var}:diff()}} damage."
                )

        elif op == "damage" and eff["target"] == "self":
            parts.append("Lose {HpLoss} HP.")

        elif op == "damage":
            times = eff.get("times", 1)
            target = eff["target"]
            if "times_formula" in eff:        # 2_plus_sparks
                # Plural targets like every other multi-hit branch below:
                # both engines re-roll the target per hit, and "a random
                # enemy" read as single-target spray (SYS-9, gleeful_barrage).
                parts.append(
                    "Deal {Damage:diff()} damage to random enemies, "
                    "2+[gold]Sparks[/gold] times.")
                continue
            if times in RUNTIME_TIMES:        # times: a live count
                suffix = RUNTIME_TIMES_TEXT[times]
                times = 2                     # phrasing: plural targets
            elif isinstance(times, str):      # times: "X"
                suffix = " X times"
                times = 2                     # phrasing: plural targets
            elif eff is times_var_effect(card):
                # Ruled `times: +N`: the count must render from the var so the
                # upgrade shows green, which also means no "twice"/"three
                # times" word form -- the diff token needs a numeral.
                suffix = " {Times:diff()} times"
                times = 2                     # phrasing: plural targets
            else:
                suffix = {1: "", 2: " twice", 3: " three times", 4: " four times"}.get(
                    times, f" {times} times"
                )
            tok = ("CalculatedDamage"
                   if calc_rider(card, eff) is not None
                   or salon_calc_rider(card, eff) is not None else "Damage")
            if _is_sly_branch(card):
                tok = None                    # literal, see _sly_view
            if tok == "Damage" and eff is not damage_var_effect(card):
                tok = None                    # see damage_var_effect
            if tok is None:
                amount_txt = str(int(eff["amount"]))
                where = {"enemy": "",
                         "all_enemies": " to ALL enemies"}.get(
                             target, " to a random enemy")
                parts.append(f"Deal {amount_txt} damage{where}{suffix}.")
                continue
            if target == "enemy":
                parts.append(f"Deal {{{tok}:diff()}} damage{suffix}.")
            elif target == "all_enemies":
                parts.append(f"Deal {{{tok}:diff()}} damage to ALL enemies{suffix}.")
            else:
                plural = "random enemies" if times > 1 else "a random enemy"
                parts.append(f"Deal {{{tok}:diff()}} damage to {plural}{suffix}.")
            # Track L-C: a rider whose arithmetic now lands inside the printed
            # number keeps only a short marker here; the rate (and what it is
            # worth right now) moves to the hover tip. A rider that is NOT
            # converted keeps its full sentence -- its number is not on the
            # face, so the text is the only place the player can read it.
            rehomed = calc_rider(card, eff) is not None
            if exhaust_pile_calc_rider(card, eff) is not None:
                # The number is already honest (it renders through the
                # CalculatedVar); this sentence says WHY it moves. Without it
                # the card is a damage number that changes for no stated
                # reason, which is the exact confusion Track C exists to stop.
                parts.append(
                    "Scales with the number of cards [gold]Exhausted[/gold].")
            if exhaust_selection_calc_rider(card, eff) is not None:
                # Same job as the pile sentence above, and needed more: this
                # count does not exist until the card resolves, so without it
                # the face is a number that appears from nowhere.
                parts.append("Scales with "
                             + EXHAUST_SELECTION_TEXT[eff["amount_formula"]
                                                      ["count"]] + ".")
            if discards_turn_calc_rider(card, eff) is not None:
                # EB-122. Third sentence in the same family: the number is
                # honest (it renders through the CalculatedVar), and this says
                # WHY it moves. It also tells the pilot the count is per TURN,
                # which is the whole play pattern -- throw first, then swing.
                parts.append(
                    "Scales with the cards you discarded this turn.")
            if "bonus_formula" in eff:
                formula = eff["bonus_formula"]
                if formula.endswith("_per_detonation_this_combat"):
                    per = ("{BonusPer:diff()}" if bonus_per_upgrade(card)
                           else formula.partition("_per_")[0])
                    parts.append(
                        f"+{per} damage per [gold]Bomb[/gold] detonated this combat.")
                elif rehomed:
                    # Name the RESOURCE the formula actually reads. This said
                    # "Fanfare" unconditionally, which put another character's
                    # mechanic on the face of every Kokomi Charge reader --
                    # including her signature one -- while the arithmetic
                    # underneath was correct. A face that names the wrong stat
                    # is worse than one that says nothing.
                    # A13/A14: `rpartition("_")` would name this rider
                    # "Member", which is not what anything in the game or on
                    # the sheet is called. The stage is the Salon.
                    stat = ("Salon" if formula.endswith("_per_salon_member")
                        else "Companions"
                        if formula.endswith("_per_companion_played_this_turn")
                            else formula.rpartition("_")[2].title())
                    parts.append(f"Scales with [gold]{stat}[/gold].")
                else:
                    n, _, rest = formula.partition("_per_")
                    step, _, stat = rest.partition("_")
                    parts.append(
                        f"+{n} damage per {step} [gold]{stat.title()}[/gold].")
            if "bonus_vs_aura" in eff:
                if rehomed:
                    parts.append("Bonus damage vs. an elemental aura.")
                else:
                    parts.append(
                        f"+{int(eff['bonus_vs_aura'])} damage if the enemy "
                        "has an elemental aura.")

        elif op == "gain_spark":
            if spark_upgrade(card):
                # Plural token off the LIVE value, same idiom as draw above.
                parts.append(
                    "Gain {Sparks:diff()} [gold]Spark{Sparks:plural:|s}[/gold]."
                )
            else:
                n = int(eff["amount"])
                parts.append(
                    "Gain 1 [gold]Spark[/gold]." if n == 1
                    else f"Gain {n} [gold]Sparks[/gold]."
                )

        elif op == "spend_spark":
            # The price is printed FIRST because it is a cost line: a player
            # reads what the card charges before what it buys. The card is
            # unplayable below it (the IsPlayable gate), so this sentence
            # describes a gate, never a partial spend.
            n = int(eff["amount"])
            parts.append(
                "Spend 1 [gold]Spark[/gold]." if n == 1
                else f"Spend {n} [gold]Sparks[/gold]."
            )

        elif op == "burst_energy":
            if burst_upgrade(card):
                parts.append("Gain {BurstEnergy:diff()} [gold]Burst Energy[/gold].")
            else:
                parts.append(f'Gain {int(eff["amount"])} [gold]Burst Energy[/gold].')

        elif op == "gain_charge":
            parts.append(
                f'Gain {int(eff["amount"])} [gold]Charge[/gold].')

        elif op == "summon_kurage":
            # The pulse arithmetic is NOT spelled out here. It is a computed
            # number (base + per-Charge x bank) and belongs in the rendered
            # var / hover tip where it updates live -- the Furina legibility
            # lesson: a face that prints stale arithmetic teaches the wrong
            # number. The face says what the card DOES; the tip says what it
            # is worth right now.
            turns = ("{KurageTurns:diff()}" if kurage_turns_upgrade(card)
                     else str(int(eff.get("amount", 1))))
            parts.append(
                f"Summon [gold]Bake-Kurage[/gold] for {turns} turn"
                + ("{KurageTurns:plural:|s}" if kurage_turns_upgrade(card)
                   else ("" if int(eff.get("amount", 1)) == 1 else "s"))
                + ".")

        elif op == "conscript":
            phrase = _conscript_phrase(eff)
            parts.append(phrase[0].upper() + phrase[1:] + ".")

        elif op == "gain_encore":
            base = int(eff["amount"])
            delta = encore_upgrade(card)
            if salon_calc_rider(card, eff) is not None:
                # The var carries both the upgrade (CalculationBase bumps)
                # and the salon x2, so it replaces the IfUpgraded swap.
                amount = "{Encore:diff()}"
            else:
                amount = (
                    f"{{IfUpgraded:show:{base + delta}|{base}}}"
                    if delta else str(base))
            parts.append(f"Gain {amount} [gold]Encore[/gold].")

        elif op == "spend_encore":
            parts.append(
                f"Spend {int(eff['amount'])} [gold]Encore[/gold]; "
                "lose HP for any shortfall.")

        # THE TWO FANFARE KEYWORDS (rework Track B, 2026-07-28, RULED). These
        # replaced sentences with a printed keyword each, because the value
        # they carry used to arrive invisibly -- every Power granted 5 floor
        # (rares 8) and no card said so.
        elif op == "raise_fanfare_cap":
            # "Fanfare Cap", never bare "Cap": the Salon's member cap is also
            # a per-player stat since A12, and one word cannot mean both.
            parts.append("[gold]Fanfare Cap[/gold] +{FanfareCap:diff()}.")

        elif op == "gain_fanfare_floor":
            # Bare "Fanfare +X" for the FULL grant -- current, baseline and
            # cap together. The convention is only unambiguous because no card
            # grants transient Fanfare directly (all four generation sources
            # are indirect); register lint L12 is the blocker that keeps it
            # that way, on the sheet AND on effects.OPS.
            parts.append("[gold]Fanfare[/gold] +{FanfareFloor:diff()}.")

        elif op == "crash_fanfare":
            # Two sentences because it is two things happening, and the
            # SECOND one is the cost -- burying it in a subclause is how a
            # card that digs a hole reads as a card that just resets.
            parts.append(
                "Your [gold]Fanfare[/gold] falls to its baseline, and that "
                "baseline falls by {FloorDrop:diff()}.")

        elif op == "salon_bow":
            n = int(eff.get("amount", 1))
            parts.append(
                "The leftmost member of your [gold]Salon[/gold] takes their "
                "bow." if n == 1 else
                f"The leftmost {n} members of your [gold]Salon[/gold] take "
                "their bows.")

        elif op == "salon_rotate":
            # "Moves to the back" and not "rotates": the player is told what
            # happens to the member, not what happens to the data structure.
            n = int(eff.get("amount", 1))
            parts.append(
                "The leftmost member of your [gold]Salon[/gold] moves to the "
                "back." if n == 1 else
                f"The leftmost member of your [gold]Salon[/gold] moves to the "
                f"back, {n} times.")

        elif op == "salon_perform":
            n = int(eff.get("amount", 1))
            parts.append(
                "The leftmost member of your [gold]Salon[/gold] performs "
                "now." if n == 1 else
                f"The leftmost member of your [gold]Salon[/gold] performs "
                f"now, {n} times.")

        elif op == "heal":
            parts.append("Heal {Heal:diff()} HP.")

        elif op == "apply_power":
            template = APPLY_POWERS[eff["power"]][2]
            if "member" in eff:
                # B5: name WHO. A11's random deploy says so instead -- it can
                # field any of the three, and the tooltip lists all three.
                #
                # Only the FIRST deploy on a card says "to your Salon". Full
                # Ensemble makes three, and three copies of the same
                # prepositional phrase is the boilerplate this ruling exists
                # to delete, just reworded.
                if salon_named:
                    template = template.replace(
                        " to your [gold]Salon[/gold]", "")
                salon_named = True
                template = template.replace(
                    "{MEMBER}", SALON_MEMBER_NAMES[eff["member"]])
            x = ("{PowerAmount:diff()}"
                 if eff is power_upgrade_effect(card)
                 or salon_calc_rider(card, eff) is not None
                 else str(deploy_amounts.get(eff_index, 0)
                          or int(eff["amount"])))
            to = {"all_enemies": " to ALL enemies",
                  "random_enemy": " to a random enemy"}.get(
                      eff.get("target"), "")
            # {XS}: noun agreement for the draw templates. A var amount
            # pluralizes at runtime off the live value; a literal is pinned
            # here -- "draws 2 card" is how supporting_cast shipped (SYS-9).
            xs = ("{PowerAmount:plural:|s}" if x.startswith("{")
                  else ("" if x == "1" else "s"))
            parts.append(template.replace("{X}", x).replace("{XS}", xs)
                         .replace("{TO}", to))

        elif op == "detonate":
            where = ("an enemy's" if eff["target"] == "enemy" else "ALL")
            parts.append(f"Detonate {where} [gold]Bombs[/gold].")
            bonus = int(eff.get("bonus", 0))
            if bonus_upgrade(card):
                parts.append("Detonations deal {Bonus:diff()} more damage.")
            elif bonus:
                parts.append(f"Detonations deal {bonus} more damage.")

        elif op == "modify_bombs":
            scope = ("placed this turn "
                     if eff.get("scope", "all") == "placed_this_turn" else "")
            amt = ("{Bonus:diff()}" if bonus_upgrade(card)
                   else str(int(eff["bonus"])))
            parts.append(
                f"[gold]Bombs[/gold] {scope}deal {amt} more damage."
            )

        elif op == "move_bombs":
            parts.append("Move ALL [gold]Bombs[/gold] to an enemy.")
            bonus = int(eff.get("bonus", 0))
            if bonus_upgrade(card):
                parts.append("Moved [gold]Bombs[/gold] deal {Bonus:diff()} more damage.")
            elif bonus:
                parts.append(f"Moved [gold]Bombs[/gold] deal {bonus} more damage.")

        elif op == "chance_bomb_per_detonation":
            chance = ("{Chance:diff()}" if chance_upgrade(card)
                      else str(int(round(float(eff["chance"]) * 100))))
            parts.append(
                f"Each detonation: {chance}% chance to place a new "
                f'{int(eff["bomb_damage"])}-damage [gold]Bomb[/gold] on a '
                "random enemy."
            )

        elif op == "generate_guest_star":
            amount = int(eff.get("amount", 1))
            rarity = eff["rarity"].capitalize()
            noun = "card" if amount == 1 else "cards"
            parts.append(
                f"Add {amount} random {rarity} [gold]Companion[/gold] "
                f"{noun} to your hand.")
            if "generate_cost_override" in deltas:
                # Number agreement with the generated count (SYS-9:
                # an_invitation adds ONE guest and said "They").
                pronoun = "It costs" if amount == 1 else "They cost"
                parts.append(
                    "{IfUpgraded:show:" + pronoun + " 0 this turn.|}")

        elif op == "cost_mod":
            n = -int(eff["delta"])
            parts.append(
                f"[gold]Companion[/gold] cards cost {n} less this turn.")

        elif op == "copy_companion_in_hand":
            base_txt = ("Add a copy of a random [gold]Companion[/gold] card "
                        "in your hand to your hand.")
            if "cost_override" in eff:
                parts.append(base_txt + f" The copy costs {int(eff['cost_override'])}.")
            elif "copy_cost_override" in upgrade_plan(card)[0]:
                o = int(upgrade_plan(card)[0]["copy_cost_override"])
                parts.append(
                    "{IfUpgraded:show:" + base_txt + f" The copy costs {o}.|"
                    + base_txt + "}")
            else:
                parts.append(base_txt)

        elif op == "copy_spotlighted_in_hand":
            base_txt = (
                "Add a copy of a random [gold]Spotlighted[/gold] card "
                "in your hand to your hand.")
            if "cost_override" in eff:
                parts.append(
                    base_txt
                    + f" The copy costs {int(eff['cost_override'])}.")
            elif "copy_cost_override" in upgrade_plan(card)[0]:
                override = int(
                    upgrade_plan(card)[0]["copy_cost_override"])
                parts.append(
                    "{IfUpgraded:show:" + base_txt
                    + f" The copy costs {override}.|"
                    + base_txt + "}")
            else:
                parts.append(base_txt)

        elif op == "replay_next_companion":
            t = int(eff.get("times", 1))
            times_txt = "an extra time" if t == 1 else f"{t} extra times"
            parts.append(
                "The next [gold]Companion[/gold] card you play this turn "
                f"is played {times_txt}.")

        elif op == "copy_companions_played_this_combat":
            clause = ("Add a copy of every [gold]Companion[/gold] card "
                      "played this combat to your hand.")
            if eff.get("cost_override") is not None:
                clause += f' They cost {int(eff["cost_override"])}.'
            parts.append(clause)

        elif op == "apply_aura":
            el = eff["element"].capitalize()
            where = {"enemy": "", "random_enemy": " to a random enemy",
                     "all_enemies": " to ALL enemies"}[eff.get("target", "enemy")]
            parts.append(f"Apply [gold]{el}[/gold]{where}.")

        elif op == "swirl":
            tgt = eff.get("target", "enemy")
            parts.append("[gold]Swirl[/gold] ALL enemies' auras."
                         if tgt == "all_enemies"
                         else "[gold]Swirl[/gold] an enemy's aura.")

        elif op == "refresh_all_auras":
            parts.append("Refresh ALL elemental auras.")

        elif op == "grow_damage":
            parts.append(
                f'Permanently increase this card\'s damage by '
                f'{int(eff["amount"])} this combat.')

        elif op == "buff_next_attack":
            n = ("{PowerAmount:diff()}" if eff is power_upgrade_effect(card)
                 else str(int(eff["amount"])))
            parts.append(f"Your next Attack deals {n} more damage.")

        elif op == "energy":
            n = int(eff["amount"])
            # Same defect as the play emitter: an upgradeable amount printed
            # its BASE forever. The var renders the diff so the face, the
            # upgrade preview and the energy actually gained all agree.
            parts.append("Gain {Energy:diff()} Energy."
                         if energy_upgrade(card) else f"Gain {n} Energy.")

        elif op == "scry_discard":
            n = int(eff["amount"])
            # "top 1 cards ... discard one" was curtain_up's face (SYS-9).
            parts.append(
                "Look at the top card of your draw pile; discard it."
                if n == 1 else
                f"Look at the top {n} cards of your draw pile; discard one.")

        elif op == "exhaust_from" and eff.get("select") == "chosen":
            n = ("{Exhausts:diff()}" if exhaust_upgrade(card)
                 else str(int(eff.get("amount", 1))))
            # A var amount pluralizes off the LIVE value -- pinning "s" to
            # the upgraded count is how ebb_tide's base face read "Exhaust 1
            # cards" (SYS-9).
            plural = ("{Exhausts:plural:|s}" if n.startswith("{")
                      else "" if n == "1" else "s")
            # VOICE LAW (R55): the card says what happens, and what happens is
            # a rotation. No "sacrifice", no "destroy" -- the unit leaves the
            # line intact. Exhaust is the game's keyword and stays.
            parts.append(
                f"[gold]Exhaust[/gold] {n} card{plural} from your hand.")

        elif op == "exhaust_from":
            parts.append("Exhaust a random Status card from your hand.")

        elif op == "grant_sly_this_turn":
            # EB-122. A RUN of identical grants is one sentence, the B5 rule
            # (`merged_deploy_text`) applied to a second verb: the_gunbai_turns
            # prints the op three times, and three copies of the same line is
            # the boilerplate that ruling deletes. The body still emits one
            # call per effect -- each opens its own screen and each picks a
            # DIFFERENT Skill, because the filter excludes what a previous
            # grant already touched -- so merging is text only.
            run_start = eff_index == 0 or (
                card["effects"][eff_index - 1].get("op") != op
                or card["effects"][eff_index - 1].get("card_type", "skill")
                != eff.get("card_type", "skill"))
            if not run_start:
                continue
            n = 0
            for later in card["effects"][eff_index:]:
                if (later.get("op") != op
                        or later.get("card_type", "skill")
                        != eff.get("card_type", "skill")):
                    break
                n += 1
            what = "a Skill" if n == 1 else f"{n} Skills"
            parts.append(
                f"Give {what} in your hand [gold]Sly[/gold] this turn.")

        elif op == "recall_to_draw":
            # EB-118. The face carries BOTH halves of the bargain: where the
            # card comes back to, and that it comes back on loan. The gained
            # Exhaust is the whole reason the card is priced as a loan and
            # not as a second copy, so it is printed, not left to a keyword
            # the player has to notice on the returned card.
            n = int(eff.get("amount", 1))
            what = ("a card" if n == 1 else f"{n} cards")
            if eff.get("from", "discard") == "exhaust":
                parts.append(
                    f"Choose {what} from your [gold]Exhaust[/gold] pile; put "
                    f"{'it' if n == 1 else 'them'} on top of your draw pile. "
                    f"{'It gains' if n == 1 else 'They gain'} "
                    f"[gold]Exhaust[/gold].")
            else:
                # EB-122, the discard source. The loan sentence is ABSENT and
                # its absence is the pricing: nothing is granted, because a
                # discard-pile card was coming back on the next reshuffle
                # anyway and the card is only buying the order.
                parts.append(
                    f"Choose {what} from your discard pile; put "
                    f"{'it' if n == 1 else 'them'} on top of your draw pile.")

        elif op == "add_card":
            n = eff.get("amount", 1)
            zone_txt = ("your hand"
                        if (eff.get("zone") or eff.get("to", "discard")) == "hand"
                        else "your discard pile")
            if "pool" in eff:
                archetype, _, rarity = eff["pool"].rpartition("_")
                rarity = rarity.rstrip("s").capitalize()
                count = "{Stash:diff()}" if stash_upgrade(card) else str(int(n))
                clause = (f"Add {count} random [gold]{archetype}[/gold] "
                          f"{rarity} cards to {zone_txt}.")
                if eff.get("cost_override") == 0:
                    clause += " They cost 0 this combat."
                elif "cost_override" in eff:
                    clause += f' They cost {int(eff["cost_override"])} this combat.'
                parts.append(clause)
            else:
                name = eff.get("card_id") or eff.get("card")
                name = name.replace("_", " ").title()
                a_card = (f"a [gold]{name}[/gold]" if int(n) == 1
                          else f"{int(n)} [gold]{name}[/gold] cards")
                parts.append(f"Add {a_card} to {zone_txt}.")

        elif op == "conditional":
            pred_txt = predicate_text(eff["if"])
            then = eff.get("then", [])
            if any(e.get("op") == "repeat_this" for e in then):
                parts.append(f"{pred_txt}: play this card again.")
            else:
                then_txt = _branch_text(card, then, in_then=True,
                                        predicate=eff["if"])
                clause = f"{pred_txt}: {then_txt}"
                els = eff.get("else", [])
                if els:
                    clause += (" Otherwise: "
                               + _branch_text(card, els, in_then=False,
                                              predicate=eff["if"]))
                if condition_upgrade(card):
                    # {IfUpgraded:show:upgraded|normal} -- the runtime form
                    # BaseLib's SimpleLoc MakeUpgradeSwap generates. Pipe is
                    # the separator, so pipes in either arm (e.g. plural
                    # tokens) would break parsing -- stop loudly.
                    upgraded = then_txt[0].upper() + then_txt[1:]
                    if "|" in upgraded or "|" in clause:
                        raise SystemExit(
                            f"gen_klee_cards: {card['id']}: condition-swap "
                            "text contains '|' -- cannot nest in "
                            "{IfUpgraded:show:...}.")
                    clause = "{IfUpgraded:show:" + upgraded + "|" + clause + "}"
                parts.append(clause)

        elif op == "choose_one":
            # RAILS ("no new named keyword"): the face is ordinary card text.
            # "Choose one:" is a sentence, not a keyword -- no [gold], no
            # tooltip, nothing registered in KleeKeywords. Each mode prints
            # its own authored label, which is that mode's card text and the
            # same string its option class shows on the screen.
            labels = " | ".join(m["label"].rstrip(".")
                                for m in eff["modes"])
            parts.append(f"Choose one: {labels}.")

        elif op == "discard":
            n = int(eff.get("amount", 1))
            # PREVIEW TRUTH: "random" is a claim about who picks, and the
            # emitter used to print it whatever `select` said -- a chosen
            # discard read as a random one on the face while the body (now)
            # opens a selection screen. The word tracks the branch that
            # emits, exactly as the body does.
            picker = "" if eff.get("select") == "chosen" else " random"
            if plain_discard_upgrade(card):
                # Upgradeable: the face must show the NEW number, so it
                # renders through the var like every other upgraded count.
                parts.append(
                    "Discard {Discards:diff()}" + picker + " "
                    "card{Discards:plural:|s}.")
            elif picker:
                parts.append(
                    "Discard a random card." if n == 1
                    else f"Discard {n} random cards."
                )
            else:
                # No article form on the chosen branch: canon's own selection
                # cards print the numeral ("Discard 1 card."), which is also
                # what `discard_for_sparks` and the chosen `exhaust_from`
                # print next door.
                parts.append(
                    f"Discard {n} card{'' if n == 1 else 's'}."
                )

        elif op == "discard_for_sparks":
            # `sparks` is a CAP on the total, never a rate: tier0
            # _op_discard_for_sparks does `gain = min(fx["sparks"], discarded)`
            # -- 1 Spark per card ACTUALLY discarded, capped (R36 ratifies the
            # same reading, and the emitted C# matches with Math.Min).
            #
            # Bug hunt 2026-07-21: the old template substituted that cap into
            # "gain {Sparks} Sparks PER CARD DISCARDED", which reads as a rate.
            # At 1/1 the two coincide, so only the upgrade lied -- Crackle+ read
            # "discard 2: gain 2 Sparks per card discarded" (parsed as 4) and
            # granted 2, which is the difference between crossing the 3-Spark
            # free-attack threshold and not. The rate is always 1; the cap is
            # printed separately, and only when it can actually bind.
            n, m = int(eff["amount"]), int(eff["sparks"])
            d_n, d_m = discard_upgrade(card)
            if (d_n, d_m) != (0, 0):
                text = ("Discard {Discards:diff()} card{Discards:plural:|s}: "
                        "gain 1 [gold]Spark[/gold] per card discarded.")
                # The cap binds only if it can be lower than the discard count
                # in some reachable state (base or upgraded).
                if m < n or (m + d_m) < (n + d_n):
                    text += " Maximum {Sparks:diff()}."
                parts.append(text)
            else:
                cards_w = "a card" if n == 1 else f"{n} cards"
                text = f"Discard {cards_w}: gain 1 [gold]Spark[/gold] per card discarded."
                if m < n:
                    text += f" Maximum {m}."
                parts.append(text)

    if added_effect_anchor(card) is None:
        parts.extend(_upgrade_add_text(card))
    if added_repeat_upgrade(card):
        # Same sentence the printed repeat-conditional uses ("play this card
        # again"), swapped in on upgrade. Pipe-free payload, as the swap-parse
        # requires.
        n = added_repeat_upgrade(card)
        again = ("Play this card again." if n == 1
                 else f"Play this card {n} more times.")
        parts.append("{IfUpgraded:show:" + again + "|}")

    # Sly. DEFECT FIX (v0.5 fill): the discard hook generated correctly from
    # the first Sly card onward, but the card FACE never mentioned it -- so
    # drifting_lantern, the sheet's self-declared "Sly teaching card", printed
    # "Gain 4 Block." and taught nothing. A mechanic a player cannot read is a
    # mechanic that does not exist at the table. Rendered off the same text
    # builder as the played face, through _sly_view so the numbers here are
    # LITERAL: no upgrade delta reaches a Sly branch (upgrades sheet header,
    # "no sly-delta key exists in the applier"), and rendering a {Var:diff()}
    # would print the played face's upgraded number on a line that never moves.
    # The RESERVED auto-play marker is deliberately absent from this line:
    # it renders as `CardKeyword.Sly` through the game's own auto-keyword
    # pipeline, exactly like Exhaust/Innate/Retain, and spelling it into the
    # description string as well would print the word twice (the A9 note on
    # the CanonicalKeywords rail is the same reasoning). `_sly_view` already
    # drops it, so a marker-only row produces no text and no line.
    # EB-118 sec.4.6: the `skill_tag` contribution becomes VISIBLE. The tag
    # is worth BURST_PER_SKILL_TAG burst energy on play and always has been,
    # paid by KleeElementalHooks.AfterCardPlayed off the ISkillTagCard
    # marker -- a real number on fifteen faces that no face printed. The tag,
    # its membership and the meter arithmetic do NOT move here; only the
    # reading does.
    #
    # NOT A KEYWORD, by sec.1 rail 1: `Burst +5` is a visible effect LINE, and
    # Klee gets no third keyword out of this pass. So it is rendered as plain
    # text with only the resource name highlighted -- the same treatment the
    # `burst_energy` op's own line already gets -- and it is deliberately
    # NOT added to CanonicalKeywords, where the game's auto-keyword pipeline
    # would give it a tooltip and a capitalised badge and make it one.
    #
    # LITERAL, never a var: the number is a CONSTANT of the tag rather than a
    # property of the card, no upgrade delta can reach it, and rendering it
    # through {Var:diff()} would invite exactly the drift this line exists to
    # remove.
    if "skill_tag" in (card.get("tags") or ()) and _is_klee_row(card):
        parts.append(f"[gold]Burst[/gold] +{BURST_PER_SKILL_TAG}.")

    if sly_riders(card):
        sly_text = build_description(_sly_view(card)).strip()
        if sly_text:
            parts.append(f"[gold]Sly[/gold]: {sly_text}")

    return " ".join(parts)


def _is_sly_branch(card: dict) -> bool:
    """True while emitting a card's Sly branch (see _sly_view).

    Every amount inside a Sly branch is LITERAL. The played face's
    DynamicVars belong to the played face: a Sly branch that reached for
    them printed and dealt the upgraded number on a line the sim never
    upgrades, and -- worse -- reached for vars the card does not declare at
    all when the branch used an op the played face lacks (Quiet Harbor's
    Sly draw against a card whose only var is Block).
    """
    return bool(card.get("_sly_branch"))


def _sly_view(card: dict) -> dict:
    """The card as its Sly branch sees itself: the sly list as the effects,
    and an id no upgrade sheet knows.

    The id swap is the load-bearing part. Both the text builder and the body
    emitter ask `upgrade_plan(card)` whether a delta claims a given op, and
    they key that on the card id -- so a Sly branch built under the real id
    inherited the PLAYED face's deltas. Driftglass (hit 8, Sly hit 5) emitted
    `DynamicVars.Damage` for the Sly hit and so dealt 8 on discard, and
    drifting_lantern's Sly Block upgraded from 4 to 6 alongside its played
    face. Both contradict the sim, which never moves a Sly number.

    EB-71 (R174), C# leg: the branch is built from `sly_riders(card)`, not
    from the whole `sly` list. Since the unification the list may also carry
    the reserved `{op: sly_autoplay}` marker, which is the base-game keyword
    and NOT an effect -- it emits as `CardKeyword.Sly` on the CanonicalKeywords
    rail (beside Exhaust/Innate/Retain) and has no body. Feeding it to the
    effect emitter is exactly the "plausible-looking wrong body" this
    generator refuses to write.
    """
    view = {**card, "id": card["id"] + "__sly", "_sly_branch": True,
            "effects": sly_riders(card), "cost": card.get("cost", 0)}
    # A Sly branch has no Sly branch of its own. Leaving the key in place
    # made build_description recurse into itself forever.
    view.pop("sly", None)
    return view


def _sly_marker_reason(card: dict) -> str | None:
    """Block a row whose Sly list the emitter cannot read as printed text.

    Two failures, both of which used to reach the emitter as an effect and
    come out the far side as C#:

      * a rider that is not a mapping with an `op` -- the pre-EB-71 spelling
        `sly: true` lands here, and so does any hand-migrated row that kept a
        boolean. `Card.from_dict` refuses those by name sim-side; this is the
        same refusal on the codegen side of the wall.
      * the reserved auto-play marker carrying anything else. Bare, it is the
        printed base-game keyword. `until: turn_end` is Hand Trick's RUNTIME
        grant (state.SLY_AUTOPLAY_THIS_TURN), which no card PRINTS and the
        mod has no rail for -- a generated card cannot express "Sly until the
        end of this turn", so a sheet that asks for it must block rather than
        ship a permanent keyword.
    """
    sly = card.get("sly")
    if not isinstance(sly, list):
        return (f"sly branch: `sly:` is {sly!r}, not an effect list. Since "
                f"EB-71 (R174) the base-game keyword is spelled "
                f"[{{op: {SLY_AUTOPLAY_OP}}}], not a boolean.")
    for fx in sly:
        if not isinstance(fx, dict) or not fx.get("op"):
            return (f"sly branch: rider {fx!r} is not an effect mapping. "
                    f"Since EB-71 (R174) `sly:` is an effect list; the "
                    f"base-game keyword is the reserved rider "
                    f"[{{op: {SLY_AUTOPLAY_OP}}}].")
        if fx.get("op") == SLY_AUTOPLAY_OP and set(fx) != {"op"}:
            extra = sorted(set(fx) - {"op"})
            return (f"sly branch: the reserved {SLY_AUTOPLAY_OP} rider is the "
                    f"printed base-game keyword and takes no other key; this "
                    f"row adds {extra}. A turn-scoped grant is runtime state, "
                    f"not printed text, and has no C# rail.")
    return None


def build_upgrade(card: dict) -> list[str]:
    # R24: every line comes from a ruled delta in klee-upgrades.yaml; effects
    # without a delta key upgrade nothing (e.g. snap's Spark rider stays put
    # while its damage bumps -- R1: the upgrade must not move the resource
    # curve). Lines follow effect order; a cost delta lands last. The `done`
    # set guards against a delta double-applying if a card ever carries two
    # effects of the same op.
    deltas, reason = upgrade_plan(card)
    if reason:
        return []
    key_for = {"block": "block", "draw": "draw", "gain_spark": "spark",
               "place_bomb": "bomb_damage", "burst_energy": "burst_energy",
               "heal": "heal",
               "summon_kurage": "kurage_turns", "energy": "energy",
               "block_next_turn": "block_next_turn",
               # G6: the PLAIN discard op. Shares the "Discards" var name with
               # discard_for_sparks deliberately -- no card carries both ops
               # (plain_discard_upgrade returns 0 if it does), so the name is
               # unambiguous per card and the two grammars read alike.
               "discard": "discard",
               "exhaust_from": "exhaust"}
    var_for = {"block": "DynamicVars.Block", "draw": "DynamicVars.Cards", "gain_spark": 'DynamicVars["Sparks"]',
               "burst_energy": 'DynamicVars["BurstEnergy"]', "apply_power": 'DynamicVars["PowerAmount"]',
               "buff_next_attack": 'DynamicVars["PowerAmount"]',
               "heal": 'DynamicVars["Heal"]',
               "summon_kurage": 'DynamicVars["KurageTurns"]',
               "energy": 'DynamicVars["Energy"]',
               "block_next_turn": 'DynamicVars["BlockNextTurn"]',
               "discard": 'DynamicVars["Discards"]',
               "exhaust_from": 'DynamicVars["Exhausts"]'}
    lines, done = [], set()
    for eff in card["effects"]:
        op = eff["op"]
        if op == "discard_for_sparks":
            # R36: one effect, two delta keys -- both vars move together.
            for key, var in (("discard", 'DynamicVars["Discards"]'),
                             ("sparks", 'DynamicVars["Sparks"]')):
                if key in deltas and key not in done:
                    done.add(key)
                    lines.append(f"{var}.UpgradeValueBy({int(deltas[key])}m);")
            continue
        if op in BONUS_OPS and "bonus" in eff and "bonus" in deltas \
                and "bonus" not in done:
            done.add("bonus")
            lines.append(
                f'DynamicVars["Bonus"].UpgradeValueBy({int(deltas["bonus"])}m);')
            continue
        if op == "chance_bomb_per_detonation" and "chance" in deltas \
                and "chance" not in done:
            # tier0 upgrades.py REPLACES chance; a DynamicVar only bumps, so
            # the delta is computed here from the sheet's base -- both values
            # are static, so the rendered number is exact.
            done.add("chance")
            pts = int(round(float(deltas["chance"]) * 100
                            - float(eff["chance"]) * 100))
            lines.append(f'DynamicVars["Chance"].UpgradeValueBy({pts}m);')
            continue
        if op in POWER_UPGRADE_OPS:
            # Only the effect the sim binds the delta to owns the var (see
            # power_upgrade_effect) -- keying off "first POWER_UPGRADE_OPS
            # effect" here would bump the wrong effect for a name-matched
            # weak/vulnerable delta listed after another power.
            key = (next((k for k in POWER_UPGRADE_KEYS if k in deltas), None)
                   if eff is power_upgrade_effect(card) else None)
        elif op == "damage" and eff["target"] != "self":
            key = "damage"
        else:
            key = key_for.get(op)
        if key is None or key not in deltas or key in done:
            continue
        done.add(key)
        if salon_calc_rider(card, eff) is not None:
            # Salon-converted numbers (block/draw/power alike) all keep their
            # printed base in CalculationBase, so that is what upgrades.
            var = "DynamicVars.CalculationBase"
        elif key == "damage":
            # Converted riders have no "Damage" var -- their base lives in
            # CalculationBase (the CalculatedDamageVar's base term).
            var = ("DynamicVars.CalculationBase"
                   if calc_rider(card, eff) is not None
                   else "DynamicVars.Damage")
        elif key == "block" and (spotlight_block_rider(card, eff) is not None
                                 or block_calc_rider(card, eff) is not None):
            # Converted block has no "Block" var -- its base is CalculationBase.
            var = "DynamicVars.CalculationBase"
        elif key == "bomb_damage":
            var = f"DynamicVars.{bomb_var(card)}"
        else:
            var = var_for[op]
        lines.append(f"{var}.UpgradeValueBy({int(deltas[key])}m);")
    if "times" in deltas and times_var_effect(card) is not None:
        # Post-loop: the loop keys a damage op to "damage", so a card that
        # upgrades BOTH its per-hit number and its hit count (none today, but
        # the sheet can rule it) would otherwise drop whichever key lost.
        done.add("times")
        lines.append(
            f'DynamicVars["Times"].UpgradeValueBy({int(deltas["times"])}m);')
    if "formula_per" in deltas:
        # The PER term of an amount_formula lives in ExtraDamage (the middle
        # slot of the CalculatedDamageVar triple: base + per * count), so the
        # upgrade bumps that var and the face re-renders itself.
        done.add("formula_per")
        lines.append(
            f'DynamicVars.ExtraDamage.UpgradeValueBy({int(deltas["formula_per"])}m);')
    if "formula_base" in deltas:
        # The BASE term lives in CalculationBase (the first slot of the same
        # triple). Same var the plain `damage` delta already targets on a
        # converted rider -- see the calc_rider branch above -- so this is the
        # existing path, reached by an explicit key instead of by inference.
        done.add("formula_base")
        lines.append(
            f'DynamicVars.CalculationBase.UpgradeValueBy({int(deltas["formula_base"])}m);')
    if "conditional_bonus" in deltas:
        # tier0: bump the then-branch's first damage (the ExtraDamage var;
        # expressibility gated in upgrade_plan/conditional_bonus_upgrade).
        done.add("conditional_bonus")
        lines.append(
            f'DynamicVars.ExtraDamage.UpgradeValueBy({int(deltas["conditional_bonus"])}m);')
    for ckey in ("conditional_block", "conditional_damage"):
        # EB-140. tier0 bumps EVERY matching op, branches included, so the
        # delta is emitted in two places and this is only one of them: the
        # TOP-LEVEL op moves through its own var here, while each BRANCH
        # amount swaps on an IsUpgraded read at play time (_branch_amount).
        # A card with only a branch target therefore lands a comment and no
        # statement -- the same shape `encore` leaves on curtain_cue, and the
        # shape lint_upgrade_coverage's layer 3 holds to the SHEET rather
        # than to the manifest.
        if ckey not in deltas:
            continue
        done.add(ckey)
        top, branch = _conditional_delta_targets(card, ckey)
        val = int(deltas[ckey])
        for eff in top:
            if salon_calc_rider(card, eff) is not None:
                var = "DynamicVars.CalculationBase"
            elif ckey == "conditional_block":
                var = ("DynamicVars.CalculationBase"
                       if (spotlight_block_rider(card, eff) is not None
                           or block_calc_rider(card, eff) is not None)
                       else "DynamicVars.Block")
            else:
                var = ("DynamicVars.CalculationBase"
                       if calc_rider(card, eff) is not None
                       else "DynamicVars.Damage")
            lines.append(f"{var}.UpgradeValueBy({val}m);")
        if branch:
            how_many = ("the branch amount swaps" if len(branch) == 1
                        else f"all {len(branch)} branch amounts swap")
            lines.append(
                f"// {ckey}: {how_many} on an IsUpgraded read at play time; "
                "the text swaps via {IfUpgraded:show:...|...}.")
    if branch_draw_upgrade(card):
        # tier0 draw deltas bump ALL draw ops, branches included. Only the
        # BRANCH vars are emitted here: when the card also draws at top level
        # that draw owns `Cards` and the plain top-level draw path above has
        # already bumped it, so repeating it here would upgrade one number
        # twice (caught on Compose Herself, whose OnUpgrade briefly carried
        # two identical Cards bumps).
        d = int(deltas["draw"])
        done.add("draw")
        for name in dict.fromkeys(branch_draw_vars(card)):
            if not any(f'"{name}"' in decl or f"{name}Var(" in decl
                       for decl in build_vars(card)):
                continue
            lines.append(
                f"DynamicVars.Cards.UpgradeValueBy({d}m);" if name == "Cards"
                else f'DynamicVars["{name}"].UpgradeValueBy({d}m);')
    if "condition" in deltas:
        done.add("condition")
        lines.append(
            "// condition: unconditional -- expressed at play time as "
            "(IsUpgraded || predicate); the text swaps via {IfUpgraded:show:...}.")
    if "bombs" in deltas:
        done.add("bombs")
        lines.append(f'DynamicVars["Bombs"].UpgradeValueBy({int(deltas["bombs"])}m);')
    for bkey in ("bonus_per_detonation", "bonus_slope"):
        if bkey not in deltas:
            continue
        # One rewrite, two names (upgrades.py: one branch serves both keys) --
        # each steepens the card's bonus_formula. WHERE the slope lives
        # depends on the rendering shape: a converted rider keeps it in
        # CalculationExtra (the middle slot of the Calculated*Var trio, which
        # the face re-reads), the unconverted Bomb shape in the flat BonusPer
        # var. Pick by the declared vars so the bump lands on the number the
        # face actually renders. (SYS-1: blocking_notes shipped an EMPTY
        # OnUpgrade because only the old key name had a branch here.)
        done.add(bkey)
        decls = build_vars(card)
        if any("CalculationExtraVar(" in d for d in decls):
            slope_var = 'DynamicVars["CalculationExtra"]'
        elif any('"BonusPer"' in d for d in decls):
            slope_var = 'DynamicVars["BonusPer"]'
        else:
            raise SystemExit(
                f"gen_klee_cards: {card['id']}: delta '{bkey}' has no "
                "declared slope var to land on -- the card would ship an "
                "empty OnUpgrade")
        lines.append(f"{slope_var}.UpgradeValueBy({int(deltas[bkey])}m);")
    if "floor_drop" in deltas:
        # Track C.2 (upgrades.py floor_drop): NEGATIVE deltas are the normal
        # direction -- the crash gets SHALLOWER. The op always declares the
        # FloorDrop var (build_vars), so the bump re-prints itself. (SYS-1:
        # the_final_verdict shipped an empty OnUpgrade for want of this
        # branch.)
        done.add("floor_drop")
        lines.append(
            'DynamicVars["FloorDrop"].UpgradeValueBy('
            f'{int(deltas["floor_drop"])}m);')
    if "encore" in deltas:
        done.add("encore")
        salon_encore = next(
            (e for e in card["effects"]
             if e.get("op") == "gain_encore"
             and salon_calc_rider(card, e) is not None), None)
        if salon_encore is not None:
            # A salon-converted encore prints {Encore:diff()} off the
            # CalculatedVar, so its base upgrades like any other var instead
            # of the amount swapping on an IsUpgraded read.
            lines.append(
                "DynamicVars.CalculationBase.UpgradeValueBy("
                f'{int(deltas["encore"])}m);')
        else:
            lines.append(
                "// encore: every gain_encore site reads IsUpgraded at play "
                "time (branches included).")
    if "fanfare_cap" in deltas:
        done.add("fanfare_cap")
        lines.append(
            'DynamicVars["FanfareCap"].UpgradeValueBy('
            f'{int(deltas["fanfare_cap"])}m);')
    if "fanfare_floor" in deltas:
        done.add("fanfare_floor")
        lines.append(
            'DynamicVars["FanfareFloor"].UpgradeValueBy('
            f'{int(deltas["fanfare_floor"])}m);')
    if "cards" in deltas:
        done.add("cards")
        lines.append(f'DynamicVars["Stash"].UpgradeValueBy({int(deltas["cards"])}m);')
    if deltas.get("remove") == "exhaust":
        # tier0: card.exhaust = False. Keywords are instance-owned, so this
        # touches only the upgraded copy; the auto-keyword text follows.
        done.add("remove")
        lines.append("RemoveKeyword(CardKeyword.Exhaust);")
    if deltas.get("remove") == "ethereal":
        # tier0: card.ethereal = False. The canon shape verbatim -- Apparition,
        # EchoForm and VoidForm each print Ethereal and each remove it in
        # OnUpgrade with this one line and nothing else.
        done.add("remove")
        lines.append("RemoveKeyword(CardKeyword.Ethereal);")
    if "copy_cost_override" in deltas:
        done.add("copy_cost_override")
        lines.append(
            "// copy_cost_override: expressed at play time as an IsUpgraded "
            "read in OnPlay; the text swaps via {IfUpgraded:show:...}.")
    if "generate_cost_override" in deltas:
        done.add("generate_cost_override")
        lines.append(
            "// generate_cost_override: applied to each generated card at "
            "play time when IsUpgraded.")
    if "add" in deltas:
        done.add("add")
        add_op = deltas["add"]["op"]
        if add_op == "draw":
            lines.append(
                "// add: draw -- expressed at play time as an IsUpgraded-gated "
                "draw appended after the base effects.")
        elif add_op == "repeat_this":
            lines.append(
                "// add: repeat_this -- expressed at play time as an "
                "IsUpgraded-gated replay of the base effects (sim "
                "resolve_card).")
        else:
            where = ("appended after the base effects"
                     if "add_before" not in deltas
                     else f"resolved before the {deltas['add_before']} row")
            lines.append(
                f"// add: {add_op} -- expressed at play time as an "
                f"IsUpgraded-gated effect {where}.")
    if "add_before" in deltas:
        # EB-122. The position is consumed by the `add` emission above (and by
        # build_body / build_description, which place the statement and the
        # sentence). Marked done so the SYS-1 guard sees the key expressed.
        done.add("add_before")
    if "encore_cost" in deltas:
        done.add("encore_cost")
        lines.append(
            "CustomResources<EncoreResource>.Cost(this)!.UpgradeCostBy("
            f'{int(deltas["encore_cost"])});')
    if "fanfare_cost" in deltas:
        done.add("fanfare_cost")
        lines.append(
            "CustomResources<FanfareResource>.Cost(this)!.UpgradeCostBy("
            f'{int(deltas["fanfare_cost"])});')
    if "cost" in deltas:
        done.add("cost")
        lines.append(f'EnergyCost.UpgradeBy({int(deltas["cost"])});')
    if "innate" in deltas:
        # R37: boolean, only `true` is a ruling (tier0 applier enforces the
        # same). Keywords are instance-owned, so this touches only the
        # upgraded copy.
        if deltas["innate"] is not True:
            raise SystemExit(
                f"gen_klee_cards: {card['id']}: innate delta must be `true`")
        done.add("innate")
        lines.append("AddKeyword(CardKeyword.Innate);")
    if "retain" in deltas:
        if deltas["retain"] is not True:
            raise SystemExit(
                f"gen_klee_cards: {card['id']}: retain delta must be `true`")
        done.add("retain")
        lines.append("AddKeyword(CardKeyword.Retain);")
    # The SYS-1 guard. upgrade_plan and this function are two lists of the
    # same grammar, and every key that upgrade_plan approves but no branch
    # here consumes ships as a silently partial upgrade -- exactly what R24's
    # UNAPPLIABLE discipline forbids and exactly how blocking_notes,
    # the_final_verdict and tideline_watch shipped. A miss is a generation
    # failure, never a green build.
    missed = sorted(set(deltas) - done)
    if missed:
        raise SystemExit(
            f"gen_klee_cards: {card['id']}: upgrade_plan approved delta "
            f"key(s) {missed} that build_upgrade did not express -- add the "
            "emitter branch or make upgrade_plan block the card (R24: no "
            "partial upgrades)")
    return lines


def emit(
    card: dict, profile: CharacterProfile = KLEE_PROFILE
) -> str:
    cls = pascal(card["id"])
    is_attack = card["type"] == "attack"
    # Sheet header: "ALL attacks apply pyro; applies_element omitted = true for
    # attacks". Skills carry no element. COMPANIONS are exempt from cadence
    # (tier0 _element_for): they apply their element only where the sheet
    # says applies_element -- the card-level interface carries it, so a
    # companion card mixing elemental and non-elemental damage would be
    # inexpressible (blocked_reason guards it).
    if is_companion(card):
        elemental = any(e.get("op") == "damage" and e.get("applies_element")
                        for e in card.get("effects", []))
        element_cs = ELEMENT_CS[card["element"]]
    else:
        elemental = profile.damage_applies_element(card)
        element_cs = ELEMENT_CS[profile.native_element]

    # UI affordances derive from the same mechanics as play resolution.
    # A damage-bearing IElementalCard supplies its card element; apply-only
    # skills supply the element written on their effect; Swirl supplies Anemo.
    preview_element_cs = element_cs if elemental else None
    if preview_element_cs is None:
        elemental_effect = next((e for e in card.get("effects", [])
                                 if e.get("op") in ("apply_aura", "swirl")), None)
        if elemental_effect is not None:
            preview_element_cs = (
                ELEMENT_CS[elemental_effect["element"]]
                if elemental_effect["op"] == "apply_aura"
                else "Element.Anemo")

    aura_keyword_by_element = {
        "pyro": "KleeKeywords.AppliesPyro",
        "hydro": "KleeKeywords.AppliesHydro",
        "electro": "KleeKeywords.AppliesElectro",
        "cryo": "KleeKeywords.AppliesCryo",
    }
    aura_elements = []
    if elemental:
        source_element = (
            card["element"] if is_companion(card) else profile.native_element
        )
        if source_element in aura_keyword_by_element:
            aura_elements.append(source_element)
    for e in card.get("effects", []):
        if e.get("op") == "apply_aura" and e.get("element") in aura_keyword_by_element:
            aura_elements.append(e["element"])
    aura_elements = list(dict.fromkeys(aura_elements))
    # L4: the Bomb rules text is a question about the WHOLE effect tree, not
    # about the top level. `sparkly_explosion` places its two Bombs inside the
    # kill-conditional's `then:`, so the flat scan this replaced shipped the
    # card with `includesBombRules: false` -- it named a mechanic and withheld
    # the rules for it. A branch-gated Bomb is still a Bomb on the face.
    includes_bomb_rules = any(e.get("op") in {
        "place_bomb", "detonate", "modify_bombs", "move_bombs",
        "chance_bomb_per_detonation"
    } for e in _effects_everywhere(card))

    # The card's declared TargetType follows its FIRST damaging effect; a card
    # that only blocks or draws targets Self.
    #
    # EB-118 §4.2 exception, and it is a correctness one rather than a
    # preference: an effect that AIMS (`target: enemy`) dereferences
    # `cardPlay.Target`, which the game only fills in for `TargetType.AnyEnemy`.
    # `jumpy_dumpty` is the shape that exposed it -- two random-enemy hits
    # FIRST, then a Bomb the player places -- and under the plain first-match
    # rule it would declare `AllEnemies`, take no target, and throw on its own
    # ThrowIfNull in front of a player. So a chosen target anywhere in the top
    # level wins over an earlier unaimed one. This is exactly the packet's
    # sentence made mechanical: Klee controls where she prepares explosions,
    # she does not always control where the spray lands.
    # EB-142, and it is the same correctness exception one level deeper: the
    # scan above used to read the TOP LEVEL only, so a card whose ONLY aiming
    # op sits inside a `conditional` branch declared `TargetType.Self`, took no
    # target, and threw its own ThrowIfNull mid-OnPlay -- swallowed by
    # TaskHelper.LogTaskExceptions, so the branch silently did nothing in front
    # of a player. `take_it_from_the_top` is the shape that exposed it (Block 5
    # at the top level, `spotlight_moved_this_turn` -> 10 damage in the branch):
    # Block landed, the damage never did, on both faces. A card AIMS if any op
    # ANYWHERE in its played face aims -- the player picks the target on play,
    # exactly as tier0's single aim policy binds one creature for the whole
    # card play (C18). `lint_generated_structure` now fails the shape outright.
    aimed = any(_aims_at_chosen_enemy(e) for e in _effects_everywhere(card))
    target_type = TARGET_CS["enemy"] if aimed else "TargetType.Self"
    for eff in ([] if aimed else card["effects"]):
        if eff["op"] == "damage" and eff["target"] != "self":
            target_type = TARGET_CS[eff["target"]]
            break
        # A bomb aimed at a chosen enemy makes the whole card enemy-targeted,
        # even when nothing about it deals direct damage (e.g. Double Pop).
        if eff["op"] == "place_bomb":
            target_type = TARGET_CS[eff["target"]]
            break
        # Same rule for the bomb-manipulation ops: a chosen-enemy detonate
        # (Quick Fuse) or move destination (Careful Arrangement) makes the
        # card enemy-targeted; detonate-all reads as AllEnemies.
        if eff["op"] in ("detonate", "move_bombs"):
            target_type = TARGET_CS[eff["target"]]
            break
        # Enemy debuffs too: Surprise Visit is nothing but a chosen-enemy
        # Vulnerable, so the apply is what makes the card aimable.
        if (eff["op"] == "apply_power"
                and eff.get("power") in ENEMY_APPLY_POWERS):
            target_type = TARGET_CS[eff["target"]]
            break
        # Element ops (companions): a chosen-enemy swirl/apply_aura makes
        # the card aimable, same rule as place_bomb.
        if eff["op"] in ("apply_aura", "swirl"):
            target_type = TARGET_CS[eff.get("target", "enemy")]
            break
        # EB-118: a modal's aiming verb sits inside a mode body, so a card
        # whose only enemy-facing effect is modal would declare TargetType.Self
        # and be unaimable. blocked_reason has already refused modes that
        # disagree, so the first mode that names a target names the card's.
        if eff["op"] == "choose_one":
            modal_target = next(
                (t for t in (_mode_target_type(m) for m in eff["modes"])
                 if t is not None), None)
            if modal_target is not None:
                target_type = modal_target
                break

    vars_ = build_vars(card)
    body = build_body(card, profile)
    upgrade = build_upgrade(card)
    _, no_upgrade_reason = upgrade_plan(card)
    desc = build_description(card)

    interfaces = "CustomCardModel"
    if elemental:
        interfaces += ", IElementalCard"
    if is_companion(card):
        interfaces += ", ICompanionCard"
    elif profile.emit_character_identity:
        interfaces += ", ICharacterCard"
    # Sheet `skill_tag` -> ISkillTagCard: worth BURST_PER_SKILL_TAG burst
    # energy when played (KleeElementalHooks.AfterCardPlayed reads the marker).
    if "skill_tag" in card.get("tags", []):
        interfaces += ", ISkillTagCard"
    # EB-26 D2 option (d). The apply mode is a property of the ROW, and the
    # mod's only per-application channel is the cardSource -- so the card
    # declares the mode and its ceiling, and the power reads it off the card
    # that applied it (KuragePowers.PreventExhaustWardPower).
    never_reduces_eff = next(
        (eff for eff in card.get("effects", [])
         if eff.get("op") == "apply_power" and eff.get("never_reduces")), None)
    if never_reduces_eff:
        interfaces += ", INeverReducingApplier"
    # EB-118 §6.4 constraint 3: a card that retrieves from Exhaust may never
    # be retrieved from Exhaust. The sim reads that off the printed effect
    # tree (effects.retrieves_from_exhaust); C# has no effect tree at runtime,
    # so the same shape is stamped as a marker interface and the pool filter
    # asks the type. Stamped from the SHEET, so the two answers have one
    # source.
    # EB-122: the marker is about the EXHAUST source, so the stamp asks the
    # source. The sim's twin already did -- `effects.retrieves_from_exhaust`
    # tests `fx["from"] == RECALL_EXHAUST_SOURCE` -- and this side did not,
    # because the discard source was blocked and no row could reach the
    # difference. `what_the_tokoyo_returns` reads the DISCARD pile and is not
    # part of the exhaust cycle; stamping it would have excluded it from a
    # pool it belongs in, silently, on a claim no sheet row makes.
    # EB-134: `iter_card_effects`, not `iter_effects`. The Sly branch is
    # emitted into THIS class (see `_sly_view` and the `sly_body` block
    # below), so a sly-borne exhaust retriever is a retriever the C# pool
    # filter must be able to see by type -- and `sly:` is a card-LEVEL list
    # that no effect-level recursion reaches. The stamp and its sim twin
    # (`effects.retrieves_from_exhaust`) now walk the same halves of the card.
    if any(eff.get("op") == "recall_to_draw"
           and eff.get("from", "discard") == "exhaust"
           for eff in iter_card_effects(card)):
        interfaces += ", IExhaustRetriever"

    ind = "\n        "
    vars_cs = (",".join(f"{ind}    {v}" for v in vars_)).lstrip()
    vars_block = f"            {vars_cs}\n" if vars_cs else ""
    body_cs = ind.join(body)
    # RULED 2026-07-21: companions upgrade like any other card. They used to
    # emit MaxUpgradeLevel 0 on the companion sheets' "companions never scale"
    # header, which contradicted the upgrade sheets -- the sim honours those
    # deltas and tier05 smiths companions at rest sites, so the mod was
    # measuring a power curve it could not produce.
    upgrade_cs = (
        ind.join(upgrade)
        if upgrade
        else f"// R24: NO upgrade path -- {no_upgrade_reason}. Flagged in manifest."
    )

    # Sly (Kokomi, playtest sprint): the card's `sly` list fires when the card
    # is DISCARDED, not played. tier0 resolves victim.sly at the discard site,
    # so the mod hangs it on the card's own AfterCardDiscarded hook -- the
    # effects are the card's, and putting them anywhere else would separate a
    # card's behaviour from the card.
    # EB-71 (R174), C# leg: the hook carries the AUTHORED riders only. The
    # reserved marker is the base game's own Sly (CardCmd.DiscardAndDraw ->
    # CardCmd.AutoPlay, AutoPlayType.SlyDiscard) and the engine already owns
    # that behaviour once the keyword is on the card; a hook that also
    # resolved it as effects would skip the card-played events the payoffs
    # read -- the reading the tech-debt audit (§5) refused sim-side, refused
    # here for the same reason. A marker-only row emits no hook at all.
    # EB-118 sec.5.4: one option class per mode, in the card's own file.
    # The screen takes CARDS, so each mode needs a face; ModalOptionCard
    # supplies everything but the two authored strings. They live beside the
    # card because a mode's text is that card's text -- the same reasoning
    # that keeps a Sly rider on the card that prints it.
    modal_option_classes = ""
    modal_eff = next((e for e in card["effects"]
                      if e.get("op") == "choose_one"), None)
    if modal_eff is not None:
        for i, mode in enumerate(modal_eff["modes"]):
            label = cs_escape(mode["label"])
            modal_option_classes += f'''
/// <summary>Mode {i} of {card["id"]}. A face for the choose-a-card screen;
/// never played, never in a pile, never in a pool.</summary>
public sealed class {modal_option_class(card, i)} : ModalOptionCard
{{
    public override List<(string, string)>? Localization => new()
    {{
        ("title", "{label}"),
        ("description", "{label}"),
    }};
}}
'''

    sly_cs = ""
    if sly_riders(card):
        # _sly_view, not a plain effects swap: see its docstring. Under the
        # card's own id the emitter reached for the played face's DynamicVars
        # and silently printed the wrong number on discard.
        sly_body = ind.join(build_body(_sly_view(card), profile))
        # Only declare the placeholder when the body actually threads one
        # through; an unconditional declaration is a CS0219 on every Sly
        # branch that happens not to need it.
        cardplay_decl = ""
        if "cardPlay" in sly_body:
            cardplay_decl = (
                "        // A discard is not a play, so there is no CardPlay "
                "to attribute\n"
                "        // these effects to. The shared body emitter threads "
                "one through for\n"
                "        // VFX and source attribution; null is the honest "
                "value here, and\n"
                "        // every API it reaches takes a nullable CardPlay.\n"
                "        CardPlay? cardPlay = null;\n")
        sly_cs = f'''
    /// <summary>Sly: resolves when THIS card is discarded.</summary>
    public override async Task AfterCardDiscarded(
        PlayerChoiceContext choiceContext, CardModel card)
    {{
        if (card != this) return;
{cardplay_decl}        {sly_body}
    }}
'''

    # EB-84. `CardModel.GainsBlock` is the game's answer to "does this card
    # gain Block?", and the base game's Nimble enchantment gates its whole
    # eligibility on it (`Nimble.CanEnchant` -> `card.GainsBlock`), as does the
    # Block hover tip. BaseLib's CustomCardModel auto-detects it by looking for
    # a BlockVar / CalculatedBlockVar in CanonicalVars -- which is exactly
    # right for a card whose Block is a printed number, and WRONG for a card
    # whose Block row sits inside a `conditional`: build_vars walks the top
    # level only, so that card declares no BlockVar, auto-detects to false, and
    # the game will never offer it Nimble even though the block it does gain
    # goes through CreatureCmd.GainBlock with the cardPlay attached and would
    # collect the rider correctly.
    #
    # `block_next_turn` deliberately does NOT count. The delayed half is paid
    # by the base game's own BlockNextTurnPower in AfterBlockCleared, with
    # `cardPlay: null` -- no cardSource, so no enchantment hook. Declaring
    # GainsBlock for a card whose only Block arrives that way would offer the
    # player a Nimble that cannot pay (the base game's Prolong has the same
    # shape and does not claim it). tier0's own Nimble predicate used to
    # count that op -- EB-85 divergence 4 -- and it was fixed on the sim side
    # 2026-08-13 (`enchantments._grants_block`), so the two engines agree
    # here now and nothing is being papered over.
    gains_block_member = ""
    if added_block_upgrade(card) and not any(
            eff.get("op") == "block" for eff in _effects_everywhere(card)):
        # EB-122 (wheel_the_ranks+). Block that exists only after a smith, so
        # the claim has to move with the smith. `=> true` would be a lie on the
        # unupgraded card and an eligibility split against tier0, whose Nimble
        # predicate reads the BASE row (`enchantments._grants_block`); `false`
        # would be a lie on the upgraded one, whose Block does go through
        # CreatureCmd.GainBlock with the cardPlay attached and would collect
        # the rider. The property is the only place that distinction can live,
        # and no BlockVar is declared for exactly this reason.
        gains_block_member = (
            "\n    /// <summary>Block arrives only from the ruled upgrade "
            "(`add: block`), so the\n    /// claim moves with it -- see "
            "gen_klee_cards `_upgrade_add_lines` (EB-122).</summary>\n"
            "    public override bool GainsBlock => IsUpgraded;\n"
        )
    elif (any(eff.get("op") == "block" for eff in _effects_everywhere(card))
            and not any("BlockVar(" in v for v in vars_)):
        # The summary deliberately does NOT spell the declaration block's own
        # name: lint_generated_structure locates that block by the first
        # occurrence of the word in the file, so a comment above it that
        # mentions it moves the scan onto prose and reports every var the card
        # declares as missing (caught by test_generated_structure on the first
        # run of this branch).
        gains_block_member = (
            "\n    /// <summary>Block arrives from a conditional row, so this "
            "card declares no\n    /// BlockVar and BaseLib's auto-detect "
            "cannot see it (EB-84).</summary>\n"
            "    public override bool GainsBlock => true;\n"
        )

    element_member = ""
    if elemental and is_companion(card):
        element_member = (
            "\n    /// <summary>Sheet applies_element: this companion attack applies its element.</summary>\n"
            f"    public Element Element => {element_cs};\n"
        )
    elif elemental:
        # The cadence sentence comes from the PROFILE, never a per-character
        # branch: the old Klee/else split pinned Furina's skill-grade sentence
        # onto every other roster, so all 18 elemental Kokomi cards shipped
        # claiming a Skill cadence while her profile (R52) is catalyst
        # (SYS-10).
        char = profile.character_id.title()
        elem = profile.native_element.title()
        if profile.cadence == "catalyst_attack":
            sentence = (f"Sheet: all {char} attacks apply {elem} "
                        "(catalyst-grade cadence).")
        else:
            sentence = ("Sheet cadence: damaging Skills, Burst-tagged cards, "
                        f"and skill-tagged cards apply {elem}.")
        element_member = (
            f"\n    /// <summary>{sentence}</summary>\n"
            f"    public Element Element => {element_cs};\n"
        )
    if profile.emit_character_identity and not is_companion(card):
        element_member += (
            "\n    /// <summary>Roster identity used by character-aware mechanics "
            "such as Spotlight.</summary>\n"
            f'    public string CharacterId => "{profile.character_id}";\n'
        )
    if never_reduces_eff:
        element_member += (
            "\n    /// <summary>Sheet `never_reduces: true` (EB-26 D2, floor-not-clamp):\n"
            "    /// this application raises the power toward NeverReducingCap and\n"
            "    /// never lowers a higher standing stack.</summary>\n"
            f"    public int NeverReducingCap => {int(never_reduces_eff['max_stacks'])};\n"
        )
    if is_companion(card):
        personal = card.get("personal_pool")
        personal_cs = f'"{personal}"' if personal else "null"
        element_member += (
            "\n    /// <summary>Companion identity (companion sheet): star drives the\n"
            "    /// reward slot's rarity tier; PersonalPool gates per-character\n"
            "    /// offers; Nation drives SAME_NATION_REWARD_SHARE weighting.</summary>\n"
            f"    public int Star => {int(card['star'])};\n\n"
            f"    public Element CompanionElement => {element_cs};\n\n"
            f"    public string? PersonalPool => {personal_cs};\n\n"
            f'    public string? Nation => "{card["nation"]}";\n'
        )
    if str(card["cost"]) == "X":
        # X cost: canonical 0 + the CardModel virtual (CardEnergyCost ctor
        # ignores the canonical when CostsX).
        element_member += (
            "\n    protected override bool HasEnergyCostX => true;\n"
        )

    # exhaust: true -> the base game's own Exhaust keyword. CanonicalKeywords
    # is the virtual CardModel exposes for exactly this; keyword text renders
    # via the game's auto-keyword pipeline, so the description string does NOT
    # hand-write "Exhaust." (first exercised by da_da_da/all_my_treasures when
    # gain_spark unblocked them -- every earlier exhaust card was blocked, so
    # the generator never needed this before).
    #
    # skill_tag additionally emits the ElementalSkill DISPLAY keyword
    # (playtest finding 2026-07-20: the tag was invisible on cards). Gameplay
    # still reads ISkillTagCard; the keyword is what the player sees.
    keywords = []
    # EB-118. FIRST in the array, because the canon pairing spells it that way
    # (Apparition: `{ Ethereal, Exhaust }`) and an Ethereal card is very often
    # also an Exhaust card. The keyword is the whole implementation: the game's
    # own end-of-turn sweep reads Keywords and exhausts the card
    # (causedByEthereal: true), so there is no body to emit and no hook to
    # register. `remove: ethereal` upgrades ride the RemoveKeyword path in
    # build_upgrade, exactly as Apparition/EchoForm/VoidForm do.
    if card.get("ethereal"):
        keywords.append("CardKeyword.Ethereal")
    if card.get("exhaust"):
        keywords.append("CardKeyword.Exhaust")
    # A9: base-card Innate rides the same CanonicalKeywords rail as Exhaust,
    # so the banner renders through the game's auto-keyword pipeline and the
    # description string stays free of the word (see the note above).
    # OnUpgrade's AddKeyword path is unchanged and still serves `innate: true`
    # deltas -- a card can be born Innate or become it, not both.
    if card.get("innate"):
        keywords.append("CardKeyword.Innate")
    # Same rail, same reasoning (Track C.1, 2026-07-28). OnUpgrade's
    # AddKeyword path still serves `retain: true` deltas; a card can be born
    # retaining or become it, not both.
    if card.get("retain"):
        keywords.append("CardKeyword.Retain")
    # EB-71 (R174), C# leg: the reserved `sly_autoplay` rider IS the base-game
    # keyword, so it rides the same rail rather than being emitted as a body.
    # The game owns the whole behaviour from the keyword (auto-play the
    # discarded card for free), which is what tier0's marker stands for; the
    # authored riders beside it, if any, still emit as AfterCardDiscarded.
    # Inert on every committed sheet -- no row prints the marker today.
    if sly_autoplays(card):
        keywords.append("CardKeyword.Sly")
    if "skill_tag" in card.get("tags", []):
        keywords.append("KleeKeywords.ElementalSkill")
    keywords.extend(aura_keyword_by_element[e] for e in aura_elements)
    keywords_member = ""
    if keywords:
        keywords_member = (
            "\n    public override IEnumerable<CardKeyword> CanonicalKeywords =>\n"
            "        new[] { " + ", ".join(keywords) + " };\n"
        )

    includes_confiscated_rules = any(
        eff.get("op") == "add_card" and eff.get("card") == "confiscated"
        for eff in card.get("effects", []))
    tooltip_member = ""
    tips_expr = ""
    if preview_element_cs is not None or includes_bomb_rules or includes_confiscated_rules:
        trigger_arg = preview_element_cs or "Element.None"
        bomb_arg = "true" if includes_bomb_rules else "false"
        confiscated_arg = (
            ", includesConfiscatedRules: true"
            if includes_confiscated_rules else "")
        tips_expr = (
            "KleeCardTooltips.ForCard(base.ExtraHoverTips, this, "
            f"{trigger_arg}, includesBombRules: {bomb_arg}"
            f"{confiscated_arg})")
    # Track L-C: the arithmetic the card text no longer carries. Wraps the
    # element/bomb tips when both apply, so one override yields both lists.
    rider_args, charge_rider_args = rider_tip_args(card)
    if rider_args:
        tips_expr = (
            f"FurinaRiderTips.ForCard({tips_expr or 'base.ExtraHoverTips'}, "
            f"this, {rider_args})")
    # L4b: the Charge rate, in Kokomi's own tip class. Same bargain as above
    # -- the face keeps the short "Scales with Charge" marker, the rate and
    # what it is paying right now live in the tip.
    if charge_rider_args:
        tips_expr = (
            "KokomiRiderTips.ForChargeRider("
            f"{tips_expr or 'base.ExtraHoverTips'}, this, "
            f"{charge_rider_args})")
    # B5: a deploy card carries the tip for every member it can field, plus
    # the cap rules its face no longer prints. Attached from the EFFECT, not
    # from a card list, so a new deploy card cannot ship naming a member that
    # nothing on screen explains.
    salon_tip_args = salon_member_tip_args(card)
    if salon_tip_args:
        tips_expr = (
            f"SalonMemberTips.ForCard({tips_expr or 'base.ExtraHoverTips'}, "
            f"this, {salon_tip_args})")
    # Kokomi's two hidden reads. Neither can render on a card face -- the
    # pulse resolves at end of turn from a bank that will have moved, and the
    # Garment rider lands on OTHER cards -- so the hover tip is the only
    # surface either number has. See KokomiRiderTips for the argument.
    if profile is KOKOMI_PROFILE:
        if any(eff.get("op") == "summon_kurage"
               for eff in card.get("effects", [])):
            tips_expr = (
                "KokomiRiderTips.ForKuragePulse("
                f"{tips_expr or 'base.ExtraHoverTips'}, this)")
        if card.get("type") == "attack":
            tips_expr = (
                "KokomiRiderTips.ForGarmentAttack("
                f"{tips_expr or 'base.ExtraHoverTips'}, this)")
        # R78: every Muster card carries the keyword's definition, because
        # the faces no longer restate it. Attached from the OP rather than
        # from a card list, so a new conscript card cannot ship with a
        # keyword nothing on screen defines.
        if any(eff.get("op") == "conscript"
               for eff in _effects_everywhere(card)):
            tips_expr = (
                "KokomiRiderTips.ForMuster("
                f"{tips_expr or 'base.ExtraHoverTips'}, this)")
    if tips_expr:
        tooltip_member = (
            "\n    protected override IEnumerable<IHoverTip> ExtraHoverTips =>\n"
            f"        {tips_expr};\n"
        )
    hover_using = (
        "\nusing MegaCrit.Sts2.Core.HoverTips;" if tooltip_member else "")

    source_header = (
        "//     Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml.\n"
        if profile is KLEE_PROFILE
        else (
            f"//     Generated by {profile.generator_script} from "
            f"docs/{profile.sheet.name}.\n"
        )
    )
    upgrade_header = (
        "//     Upgrade deltas come from docs/klee-upgrades.yaml (R24 2026-07-20: the\n"
        "//     upgrades sheet is the single source of truth; codegen defaults abolished).\n"
        if profile is KLEE_PROFILE
        else (
            f"//     Upgrade deltas come from docs/{profile.character_id}-upgrades.yaml; "
            "unexpressible deltas block the upgrade path.\n"
        )
    )
    extra_usings = ""
    if profile is not KLEE_PROFILE:
        extra_usings = "\nusing KleeMod;\nusing KleeMod.Cards;"
    pool_comment = (
        "    // autoAdd: false -- KleeCardPool declares pool membership itself in\n"
        "    // GenerateAllCards. BaseLib's auto-registration would need a [Pool]\n"
        "    // attribute and would register every card a second time."
        if profile is KLEE_PROFILE
        else (
            "    // autoAdd: false -- the character-aware roster pool owns membership.\n"
            "    // Partially generated character sheets must never auto-register cards."
        )
    )
    # Base-game content keys on CardTag.Strike/Defend AND CardRarity.Basic
    # together: LargeCapsule.GetStrikeForCharacter is
    # `CardPool.AllCards.First(c => c.Rarity == Basic && c.Tags.Contains(
    # CardTag.Strike))` -- an untagged basic makes that First() throw inside
    # the Ancient event's option handler and hangs the room (playtest
    # 2026-07-23). Mirror the hand-written Kaboom/DuckAndCover pair: the
    # basic attack is the character's Strike, the basic blocker its Defend.
    tag = None
    if card["rarity"] == "basic":
        if card["type"] == "attack" and any(
                e.get("op") == "damage" and e.get("target") != "self"
                for e in card["effects"]):
            tag = "Strike"
        elif any(e.get("op") == "block" for e in card["effects"]):
            tag = "Defend"
    tags_member = (
        "\n\n    protected override HashSet<CardTag> CanonicalTags => "
        f"new() {{ CardTag.{tag} }};"
        if tag else "")
    # EB-118 §4.5, the Spark cost line. Sparks are a PowerModel and not a
    # CustomResource, so BaseLib's SetCanonicalCost rail below cannot carry
    # this price: the gate is CardModel.IsPlayable, the extension point the
    # game documents for exactly this ("Grand Finale is only playable if your
    # draw pile is empty") and the mirror of tier0 card_playable's
    # `spark_cost` check. TOP-LEVEL spends only, the sim's rule -- a price
    # inside a conditional branch cannot be shown before the play, and
    # SparkPower.Spend refuses it there instead.
    spark_price = sum(int(eff["amount"]) for eff in card["effects"]
                      if eff.get("op") == "spend_spark")
    spark_gate_member = (
        "\n\n    // The Spark cost line (EB-118): unplayable below the price,\n"
        "    // which is how the cost is shown rather than silently failing.\n"
        "    protected override bool IsPlayable =>\n"
        f"        SparkPower.CanSpend(Owner.Creature, {spark_price});"
        if spark_price else "")
    resource_cost_setup = []
    if int(card.get("encore_cost", 0)) > 0:
        resource_cost_setup.append(
            "CustomResources<EncoreResource>.SetCanonicalCost("
            f"this, {int(card['encore_cost'])});")
    if int(card.get("fanfare_cost", 0)) > 0:
        resource_cost_setup.append(
            "CustomResources<FanfareResource>.SetCanonicalCost("
            f"this, {int(card['fanfare_cost'])});")
    resource_cost_cs = (
        "        " + "\n        ".join(resource_cost_setup) + "\n"
        if resource_cost_setup else "")

    return f'''// <auto-generated>
{source_header.rstrip()}
//     DO NOT EDIT. Edits are lost on the next regen -- change the sheet instead.
//
//     Sheet entry: id={card["id"]} rarity={card["rarity"]} cost={card["cost"]}
{upgrade_header.rstrip()}
// </auto-generated>

// Roslyn treats <auto-generated> files as outside the project's nullable
// context, so the ? annotations below need it re-enabled explicitly (CS8669).
#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Elements;
using KleeMod.Powers;{extra_usings}
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;{hover_using}
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace {profile.namespace};

public sealed class {cls} : {interfaces}
{{{gains_block_member}{element_member}{keywords_member}{tooltip_member}
    public override Texture2D? CustomPortrait => {profile.art_loader}.CardPortrait("{card["id"]}");

    public override List<(string, string)>? Localization => new()
    {{
        ("title", "{card["name"].replace('"', chr(92) + chr(34))}"),
        ("description", "{desc}"),
    }};{tags_member}{spark_gate_member}

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {{
{vars_block.rstrip()}
        }};

{pool_comment}
    public {cls}()
        : base({0 if str(card["cost"]) == "X" else card["cost"]}, {TYPE_CS[card["type"]]}, {RARITY_CS[card["rarity"]]}, {target_type}, autoAdd: false)
    {{
{resource_cost_cs}    }}

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {{
        {body_cs}
    }}

    protected override void OnUpgrade()
    {{
        {upgrade_cs}
    }}
{sly_cs}}}
{modal_option_classes}'''


# --- the driver ---------------------------------------------------------------
#
# ONE driver (F3, 2026-08-08). Reading a sheet, splitting it into emitted /
# blocked / no-upgrade-path, emitting a roster class, comparing or writing the
# output tree, and printing the summary are the same job for every character.
# They used to be written three times -- `_run_klee` / `_run_furina` /
# `_run_kokomi`, with the ~50-line check-and-write block copied verbatim into
# each -- which is how Kokomi's copy ended up silently dropping the R24
# "no upgrade path" report its two siblings print.
#
# What is genuinely per-character is DATA, and only that is left per-character
# below: the extra sheets a profile draws from (Klee's companions, Furina's
# Guest Stars), its manifest SCHEMA -- Klee's is a different shape and STAYS a
# different shape, because it is committed output -- and the vocabulary it
# clusters its blockers under.


@dataclass(frozen=True)
class ProfilePlan:
    """Everything one profile's regen would write, computed before it writes.

    `--check` and the real write then read the same object through the same
    code, which is the property three hand-kept copies could not hold.
    """

    generated: dict[str, str]       # card id -> emitted .cs source
    manifest_src: str               # exact manifest bytes, newline included
    stale_label: str                # "" | "Furina " | "Kokomi "
    up_to_date: str                 # the exact --check success line
    summary: list[str]              # printed only after a real write


def _script_name(profile: CharacterProfile) -> str:
    """`tools/gen_roster_cards.py` -> `gen_roster_cards`, for log prefixes."""
    return Path(profile.generator_script).stem


def _emit_sheet(
    profile: CharacterProfile,
) -> tuple[list[dict], dict[str, str], dict[str, str], dict[str, str]]:
    """Split one character sheet into emitted / blocked / no-upgrade-path.

    Returns the raw rows too: the blocked-cluster mappers need the card a
    reason came from, not just the reason.
    """
    cards = yaml.safe_load(profile.sheet.read_text(encoding="utf-8"))
    generated: dict[str, str] = {}
    blocked: dict[str, str] = {}
    no_upgrade: dict[str, str] = {}
    for card in cards:
        reason = blocked_reason(card, profile)
        if reason:
            blocked[card["id"]] = reason
            continue
        generated[card["id"]] = emit(card, profile)
        _, upgrade_reason = upgrade_plan(card)
        if upgrade_reason:
            no_upgrade[card["id"]] = upgrade_reason
    return cards, generated, blocked, no_upgrade


def _roster_class(
    *,
    profile: CharacterProfile,
    source_sheet: Path,
    note: str,
    cls: str,
    card_ids,
    summary: str = "",
) -> str:
    """A generated `public static class <cls>` holding one ModelDb card list.

    The three rosters (companions, a character's personal pool, Guest Stars)
    are the same file with a different second header line, class name and
    membership, so the shape lives here once.
    """
    entries = NEWLINE_JOIN.join(
        f"        ModelDb.Card<{pascal(card_id)}>()," for card_id in sorted(card_ids))
    sheet_rel = source_sheet.relative_to(REPO).as_posix()
    return f'''// <auto-generated>
//     Generated by {profile.generator_script} from {sheet_rel}.
//     {note}
// </auto-generated>

#nullable enable

using System.Collections.Generic;
using MegaCrit.Sts2.Core.Models;

namespace {profile.namespace};

{summary}public static class {cls}
{{
    private static List<CardModel>? _all;

    public static IReadOnlyList<CardModel> All => _all ??= new List<CardModel>
    {{
{entries}
    }};
}}
'''


# Klee's companion roster is the one roster class carrying a doc comment: the
# 4th reward slot is not obvious from the class name, and the "NOT in the pool"
# half is exactly the mistake a reader would otherwise make.
COMPANION_ROSTER_SUMMARY = """/// <summary>
/// Every companion card. The 4th reward slot (CompanionSlot) draws from
/// here; companions are NOT in KleeCardPool (tier05 character_pool excludes
/// them -- the slot is their only door).
/// </summary>
"""


def _blocked_clusters(
    cards: list[dict], blocked: dict[str, str], cluster_of
) -> dict[str, list[str]]:
    """Group blocked ids by the runtime system they wait on."""
    cards_by_id = {card["id"]: card for card in cards}
    clusters: dict[str, list[str]] = {}
    for card_id, reason in blocked.items():
        clusters.setdefault(
            cluster_of(cards_by_id[card_id], reason), []).append(card_id)
    return clusters


def _check_plan(profile: CharacterProfile, plan: ProfilePlan) -> int:
    """--check: per-card content, EXTRA .cs files in the out dir, and the
    manifest bytes. All three, or a deleted sheet row lingers as a live class.
    """
    stale = []
    for card_id, source in plan.generated.items():
        path = profile.out_dir / f"{pascal(card_id)}.cs"
        if not path.exists() or path.read_text(encoding="utf-8") != source:
            stale.append(card_id)
    expected_files = {f"{pascal(card_id)}.cs" for card_id in plan.generated}
    # `glob` on a directory that does not exist yields nothing rather than
    # raising, so a never-generated character reads as "everything is stale".
    actual_files = {path.name for path in profile.out_dir.glob("*.cs")}
    extra_files = sorted(actual_files - expected_files)
    manifest_stale = (
        not profile.manifest.exists()
        or profile.manifest.read_text(encoding="utf-8") != plan.manifest_src
    )
    if stale or extra_files or manifest_stale:
        if stale:
            print(
                f"stale {plan.stale_label}generated cards: "
                f"{', '.join(sorted(stale))}",
                file=sys.stderr,
            )
        if extra_files:
            print(
                f"stale {plan.stale_label}generated files: "
                f"{', '.join(extra_files)}",
                file=sys.stderr,
            )
        if manifest_stale:
            print(f"stale {plan.stale_label}generated manifest", file=sys.stderr)
        return 1
    print(plan.up_to_date)
    return 0


def _write_plan(profile: CharacterProfile, plan: ProfilePlan) -> None:
    profile.out_dir.mkdir(parents=True, exist_ok=True)
    # Clear stale files so a card removed from the sheet does not linger.
    for old in profile.out_dir.glob("*.cs"):
        old.unlink()
    for card_id, source in plan.generated.items():
        path = profile.out_dir / f"{pascal(card_id)}.cs"
        path.write_text(source, encoding="utf-8")
    profile.manifest.write_text(plan.manifest_src, encoding="utf-8")


def _plan_klee(profile: CharacterProfile) -> ProfilePlan:
    """Klee: her own sheet PLUS every companion sheet and the reward roster.

    Her manifest keeps its own shape -- `generated`/`companions`/`blocked`/
    `upgrades`, with no `profile`, `coverage` or `runtime_clusters` -- because
    those bytes are committed output, not a style choice this refactor gets to
    settle.
    """
    _, generated, blocked, no_upgrade = _emit_sheet(profile)

    # Companions -- a blocked companion is a build failure, not a manifest
    # entry. Both rosters are user-ratified in scope (Mondstadt 2026-07-21;
    # Fontaine same day, "as long as the 50% nationality weighting is
    # respected"). Guest Star cards are skipped: they are Furina personal-pool
    # cameos generated mid-combat by her own cards, never offered in a reward
    # slot (tier05 companion_pool filters `not c.guest_star`), and nothing in
    # the Klee mod can create one.
    companions: dict[str, str] = {}
    for sheet_path, nation in COMPANION_SHEETS:
        for card in yaml.safe_load(sheet_path.read_text(encoding="utf-8")):
            if card.get("guest_star"):
                continue
            card.setdefault("nation", nation)
            reason = blocked_reason(card, profile)
            if reason:
                raise SystemExit(
                    f"{_script_name(profile)}: companion {card['id']} blocked: "
                    f"{reason} -- the whole roster is ratified in scope; "
                    "extend the generator, do not skip.")
            companions[card["id"]] = emit(card, profile)

            # MANIFEST HOLE CLOSED (bug hunt 2026-07-21). This loop used to
            # skip upgrade_plan entirely, so no_upgrade_path listed only
            # klee-cards.yaml rows -- and the R24 safety net, which exists to
            # make "the sim can upgrade this and the mod cannot" visible,
            # covered zero companions while hiding 14 real divergences.
            # RULED 2026-07-21: companions upgrade per the sheets, so the
            # divergence is closed at the source; what remains here are the
            # genuinely inexpressible deltas, same as any other card.
            _, upgrade_reason = upgrade_plan(card)
            if upgrade_reason:
                no_upgrade[card["id"]] = upgrade_reason
    generated.update(companions)

    # The roster class the reward slot draws from (CompanionSlot.Roll):
    # generated so the sheet stays the single source of truth.
    generated["companion_roster"] = _roster_class(
        profile=profile,
        source_sheet=COMPANION_SHEETS[0][0],
        note=("DO NOT EDIT. Edits are lost on the next regen -- change the "
              "sheet instead."),
        cls="CompanionRoster",
        card_ids=companions,
        summary=COMPANION_ROSTER_SUMMARY,
    )

    manifest = {
        "_comment": (
            f"Generated by {profile.generator_script} from "
            f"{profile.sheet.relative_to(REPO).as_posix()}. "
            "'blocked' cards need systems or hand-finishing; the reason names what stopped codegen."
        ),
        "generated": sorted(set(generated) - set(companions)
                            - {"companion_roster"}),
        "companions": sorted(companions),
        "blocked": dict(sorted(blocked.items())),
        "upgrades": {
            "_comment": "R24 (2026-07-20): docs/klee-upgrades.yaml is the single "
                        "source of truth for upgrade deltas; codegen defaults are "
                        "ABOLISHED. Generated cards listed below ship with NO "
                        "upgrade path (UNAPPLIABLE discipline) until their delta "
                        "is ratified, made numeric, or hand-finished.",
            "no_upgrade_path": dict(sorted(no_upgrade.items())),
        },
    }

    by_reason: dict[str, int] = {}
    for reason in blocked.values():
        key = reason.split("(")[0].strip()
        by_reason[key] = by_reason.get(key, 0) + 1
    summary = [f"generated {len(generated)} cards, blocked {len(blocked)}"]
    summary += [f"  blocked x{n}: {reason}"
                for reason, n in sorted(by_reason.items(), key=lambda kv: -kv[1])]
    summary += [f"  no upgrade path: {cid} -- {why}"
                for cid, why in sorted(no_upgrade.items())]

    return ProfilePlan(
        generated=generated,
        manifest_src=json.dumps(manifest, indent=2) + NEWLINE,
        stale_label="",
        up_to_date=f"{_script_name(profile)}: up to date",
        summary=summary,
    )


def _furina_runtime_cluster(card: dict, reason: str) -> str:
    """Stable workstream labels for Furina's blocked coverage manifest."""
    # Hand-written is not a GAP -- it is a finished decision, and bucketing it
    # under a workstream turns completed work into a standing item on the
    # coverage report. Checked first so no ops-based rule can reclaim it.
    if reason == "hand-written":
        return "hand_written"
    effects = card.get("effects", [])
    ops = {effect.get("op") for effect in effects}
    powers = {
        effect.get("power")
        for effect in effects
        if effect.get("op") == "apply_power"
    }
    predicates = {
        effect.get("if")
        for effect in effects
        if effect.get("op") == "conditional"
    }
    if (
        reason.startswith(("encore_cost", "fanfare_cost"))
        or ops
        & {
            "gain_encore",
            "spend_encore",
            "raise_fanfare_cap",
            "gain_fanfare_floor",
        }
        or any("fanfare" in str(power) for power in powers)
        or any("fanfare" in str(predicate) for predicate in predicates)
    ):
        return "encore_fanfare_resources"
    if (
        any("salon" in str(power) for power in powers)
        or any("salon" in str(predicate) for predicate in predicates)
    ):
        return "salon"
    if (
        "spotlight" in reason
        or "companion" in reason
        or any("spotlight" in str(power) for power in powers)
        or any("spotlight" in str(predicate) for predicate in predicates)
    ):
        return "spotlight"
    if "guest" in reason:
        return "guest_stars"
    if reason.startswith("kit card"):
        return "kit_burst"
    if "heal" in reason:
        return "healing"
    if "raise_fanfare_cap" in reason:
        return "encore_fanfare_resources"
    return "shared_emitter_gap"


def _kokomi_runtime_cluster(card: dict, reason: str) -> str:
    """Group blockers by the RUNTIME SYSTEM they wait on, not by card.

    The cluster name is what tells a reader whether the gap is one afternoon
    of work or a system nobody has built -- "12 cards blocked" says nothing,
    "12 cards blocked on the ward" says exactly what to do next.
    """
    # Hand-written first, for the same reason as Furina's mapper: it is a
    # finished decision, not a coverage gap, and every ops-based rule below
    # would happily reclaim it into a workstream that has nothing left to do.
    # ceremonial_garment trips `charge_engine` on exactly this path.
    if reason == "hand-written":
        return "hand_written"
    ops = {eff.get("op") for eff in card.get("effects", [])}
    powers = {eff.get("power") for eff in card.get("effects", [])
              if eff.get("op") == "apply_power"}
    if "prevent_exhaust_ward" in powers:
        return "prevention_ward"
    if {"conscript"} & ops:
        return "conscript"
    if {"gain_charge", "summon_kurage"} & ops:
        return "charge_engine"
    if "sly" in str(card.get("tags", [])):
        return "sly_discard"
    if reason.startswith("kit card"):
        return "kit_burst"
    return "shared_emitter_gap"


def _plan_roster(
    profile: CharacterProfile,
    *,
    cadence: str,
    cluster_of,
    guest_stars: bool = False,
) -> ProfilePlan:
    """The roster-character plan: Furina and Kokomi share it exactly.

    A partial character pool is intentionally INERT. Generated classes use
    autoAdd:false and no character pool references them until every runtime
    cluster exists, so codegen can advance card by card without ever shipping
    a half-built reward pool. Blocked cards are named, counted and clustered
    rather than silently dropped -- an unlisted card is a bug, an unlisted
    BLOCKER is a lie.
    """
    cards, generated, blocked, no_upgrade = _emit_sheet(profile)
    main_generated_ids = set(generated)
    cs_name = pascal(profile.character_id)

    generated[f"{profile.character_id}_card_roster"] = _roster_class(
        profile=profile,
        source_sheet=profile.sheet,
        note=(f"Every generated personal-pool card; {cs_name}CardPool owns "
              "membership."),
        cls=f"{cs_name}CardRoster",
        card_ids=main_generated_ids,
    )

    # Guest Stars are temporary Companion cards generated only by Furina's
    # personal-pool cards. They are emitted beside her (not into the shared
    # reward roster), and are intentionally not smithable.
    guest_star_ids: list[str] | None = None
    if guest_stars:
        guest_star_ids = []
        fontaine_sheet = next(
            path for path, nation in COMPANION_SHEETS if nation == "fontaine")
        for guest in yaml.safe_load(
                fontaine_sheet.read_text(encoding="utf-8")):
            if not guest.get("guest_star"):
                continue
            guest.setdefault("nation", "fontaine")
            reason = blocked_reason(guest, profile)
            if reason:
                raise SystemExit(
                    f"{_script_name(profile)}: guest star {guest['id']} "
                    f"blocked: {reason}")
            generated[guest["id"]] = emit(guest, profile)
            guest_star_ids.append(guest["id"])
        generated["guest_star_roster"] = _roster_class(
            profile=profile,
            source_sheet=fontaine_sheet,
            note=(f"Guest Stars are temporary {cs_name} generation targets, "
                  "never reward cards."),
            cls="GuestStarRoster",
            card_ids=guest_star_ids,
        )

    clusters = _blocked_clusters(cards, blocked, cluster_of)

    sheet_rel = profile.sheet.relative_to(REPO).as_posix()
    manifest: dict = {
        "_comment": (
            f"Generated by {profile.generator_script} from {sheet_rel}. "
            "Only cards whose complete runtime grammar is implemented are emitted. "
            "Blocked cards are not auto-registered or added to a partial pool."
        ),
        "profile": {
            "character": profile.character_id,
            "element": profile.native_element,
            "cadence": cadence,
            "namespace": profile.namespace,
        },
        "coverage": {
            "total": len(cards),
            "generated": len(main_generated_ids),
            "blocked": len(blocked),
        },
        "generated": sorted(main_generated_ids),
    }
    if guest_star_ids is not None:
        manifest["guest_stars"] = sorted(guest_star_ids)
    manifest["blocked"] = dict(sorted(blocked.items()))
    manifest["runtime_clusters"] = {
        key: sorted(value) for key, value in sorted(clusters.items())
    }
    manifest["upgrades"] = {
        "_comment": (
            f"docs/{profile.character_id}-upgrades.yaml is authoritative. A "
            "generated card listed below ships without an upgrade until its "
            "full delta is expressible; partial upgrade application is "
            "forbidden."
        ),
        "no_upgrade_path": dict(sorted(no_upgrade.items())),
    }

    guest_note = (
        f" (+{len(guest_star_ids)} Guest Stars)" if guest_star_ids else "")
    summary = [
        f"{profile.character_id}: generated {len(main_generated_ids)} cards"
        f"{guest_note}, blocked {len(blocked)}"
    ]
    summary += [f"  {cluster}: {len(card_ids)}"
                for cluster, card_ids in sorted(clusters.items())]
    # Kokomi's copy of this driver never printed the R24 line; that was the
    # triplication losing a report, not a decision. Her no_upgrade map is
    # empty today, so unifying it changes no output that exists.
    summary += [f"  no upgrade path: {card_id} -- {why}"
                for card_id, why in sorted(no_upgrade.items())]

    return ProfilePlan(
        generated=generated,
        manifest_src=json.dumps(manifest, indent=2) + NEWLINE,
        stale_label=f"{cs_name} ",
        up_to_date=(
            f"{_script_name(profile)}: {profile.character_id} up to date"),
        summary=summary,
    )


def _plan_furina(profile: CharacterProfile) -> ProfilePlan:
    return _plan_roster(
        profile,
        cadence=(
            "damage on Skill, skill_tag, or burst_tag cards applies Hydro; "
            "plain Attacks do not"
        ),
        cluster_of=_furina_runtime_cluster,
        guest_stars=True,
    )


def _plan_kokomi(profile: CharacterProfile) -> ProfilePlan:
    return _plan_roster(
        profile,
        cadence=(
            "CATALYST (R52 ask N1): every Attack applies Hydro. Application "
            "uptime is structural, not authored per card."
        ),
        cluster_of=_kokomi_runtime_cluster,
    )


# Character #4 lands here, and `lint_roster_registry` (S11) fails until it
# does: the registry sweep looks for `def _plan_<id>(` in this file.
PLAN_BUILDERS = {
    "klee": _plan_klee,
    "furina": _plan_furina,
    "kokomi": _plan_kokomi,
}


def _run_profile(profile: CharacterProfile, check: bool) -> int:
    """The one driver: plan, then either compare or write."""
    plan = PLAN_BUILDERS[profile.character_id](profile)
    if check:
        return _check_plan(profile, plan)
    _write_plan(profile, plan)
    for line in plan.summary:
        print(line)
    return 0


def main(
    argv: list[str] | None = None, *, default_character: str = "klee"
) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--check", action="store_true", help="fail if output would change"
    )
    ap.add_argument(
        "--character",
        choices=(*PROFILES, "all"),
        default=default_character,
        help="character profile to generate (legacy script defaults to klee)",
    )
    args = ap.parse_args(argv)

    selected = PROFILES.values() if args.character == "all" else (
        PROFILES[args.character],)
    return max((_run_profile(profile, args.check) for profile in selected),
               default=0)


if __name__ == "__main__":
    raise SystemExit(main())
