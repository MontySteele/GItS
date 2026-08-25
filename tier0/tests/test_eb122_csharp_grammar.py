"""EB-122: the C# grammar EB-69's five blocked cards were waiting on.

`EB-69` filled Kokomi's pool in tier0 and left a DECLARED asymmetry: five of
her seventy-six cards had no C# emitter and two GENERATED cards shipped with no
upgrade at all under the no-partial-upgrades rule. Every block named an
unimplemented runtime grammar rather than a defect, and this file is the pin
for each grammar now that it exists.

WHAT IS PINNED HERE, and why this file rather than the card's own:

  * the emitted C# for each of the five shapes, asserted through `gen.emit` --
    the `test_eb71_cs_parity.py` idiom. The generated files themselves are
    guarded by `gen_roster_cards.py --check`, which proves they are what the
    generator produces; these are the claims about WHAT it should produce.
  * the sim-side facts each emission mirrors, read from tier0 rather than
    restated, so a sheet or engine change moves both sides of the assertion.
  * the two premises that make a declared divergence safe, as tests rather
    than as prose: no committed Kokomi row prints the base-game Sly keyword
    (which is what keeps `SlyGrant`'s wide filter and the sim's narrow one
    answering the same question), and no committed row asks the exhaust source
    (which is what keeps §6.4's exclusions off the discard branch).

The RUNNABLE half of the C# leg is `klee-mod/KleeTests` -- a card PLAY is
outside the headless boundary, so the mod's own tests pin the predicates that
run and the call sets of the methods that cannot.
"""

from __future__ import annotations

import pytest
import yaml

from tier0.content import loader
from tier0.engine import effects, state
from tools import gen_klee_cards as gen

PROFILE = gen.KOKOMI_PROFILE


def _row(cid: str) -> dict:
    """The REAL sheet row, so every assertion below is about a shipped card
    rather than a synthetic twin that happens to agree with it today."""
    rows = yaml.safe_load(PROFILE.sheet.read_text(encoding="utf-8"))
    hit = next((r for r in rows if r.get("id") == cid), None)
    assert hit is not None, f"{cid} is not on the sheet any more"
    return hit


def _emit(cid: str) -> str:
    row = _row(cid)
    reason = gen.blocked_reason(row, PROFILE)
    assert reason is None, f"{cid} is blocked again: {reason}"
    return gen.emit(row, PROFILE)


# --- all five come off the blocked list ------------------------------------

@pytest.mark.parametrize("cid", [
    "the_gunbai_turns", "raise_the_sashimono", "what_the_tokoyo_took",
    "gyorin_formation", "what_the_tokoyo_returns",
])
def test_the_five_eb69_blocked_cards_generate(cid):
    assert gen.blocked_reason(_row(cid), PROFILE) is None


# --- grant_sly_this_turn: one op, two cards --------------------------------

def test_the_sly_grant_rides_the_one_shared_home():
    """One C# home for the verb, the RecallFromExhaust discipline: two cards
    print it, and a per-card re-spelling is how two copies of one rule drift."""
    for cid in ("the_gunbai_turns", "raise_the_sashimono"):
        src = _emit(cid)
        assert "await SlyGrant.Grant(choiceContext, Owner, this);" in src, cid
        # No card re-spells the filter or the expiry.
        assert "ApplySingleTurnSly" not in src, cid
        assert "IsSlyThisTurn" not in src, cid


def test_a_run_of_grants_is_one_sentence_and_three_calls():
    """B5's rule on a second verb. the_gunbai_turns prints the op three times;
    three copies of one line is the boilerplate that ruling deletes. The BODY
    still emits one call per effect, because each opens its own screen and each
    picks a different Skill -- the filter excludes what a previous grant
    already touched -- so the merge is text only."""
    src = _emit("the_gunbai_turns")
    assert src.count("await SlyGrant.Grant(") == 3
    assert "Give 3 Skills in your hand [gold]Sly[/gold] this turn." in src
    assert "Give a Skill" not in src

    single = _emit("raise_the_sashimono")
    assert single.count("await SlyGrant.Grant(") == 1
    assert "Give a Skill in your hand [gold]Sly[/gold] this turn." in single


def test_a_card_type_with_no_verified_filter_is_a_named_blocker():
    """The closed-map discipline: `skill` is the game's own filter and the
    sheet's only value, and another type would be a guess wearing a name."""
    probe = {"id": "sly_grant_probe", "name": "Probe", "cost": 1,
             "type": "skill", "rarity": "uncommon", "character": "kokomi",
             "archetypes": ["assist"], "role": "glue",
             "effects": [{"op": "grant_sly_this_turn", "card_type": "attack"}]}
    reason = gen.blocked_reason(probe, PROFILE)
    assert "only 'skill' has a verified C# filter" in reason


def test_no_kokomi_row_prints_the_base_game_sly_keyword():
    """THE PREMISE UNDER SlyGrant'S DECLARED DIVERGENCE, as a test rather than
    an assumption.

    The sim's target filter asks the NARROW question -- "did a grant already
    land on this card this turn" -- and deliberately leaves a printed-Sly Skill
    a legal target (`state.sly_granted_this_turn`). The game's filter asks the
    wide one, `!IsSlyThisTurn`, which a printed keyword also answers true; its
    narrow half is a PRIVATE field on CardModel, so the wide question is the
    only one the mod can ask without reflection. The two coincide on every card
    that can reach the screen only while no Kokomi row prints the keyword. If
    one ever does, this fails and the question gets asked again instead of the
    two pools silently disagreeing."""
    offenders = [
        c.id for c in loader._card_index().values()
        if getattr(c, "character", None) == "kokomi"
        and state.sly_autoplays(c)]
    assert offenders == [], offenders


# --- what_the_tokoyo_took: a CalculatedVar bound to a COUNT -----------------

def test_the_discards_this_turn_rider_is_mementomoris_triple():
    """base + per * (discards this turn), rendered through the same
    CalculationBase / ExtraDamage / CalculatedDamageVar trio the base game's
    MementoMori uses -- which is the card tier0 names as the source of the
    token (`effects._formula_count`). A literal here would have shipped a face
    promising scaling and a hit that never scaled."""
    src = _emit("what_the_tokoyo_took")
    assert "new CalculationBaseVar(6m)" in src
    assert "new ExtraDamageVar(4m)" in src
    assert ("new CalculatedDamageVar(ValueProp.Move).WithMultiplier("
            "static (card, _) => KokomiResources.DiscardsThisTurn(card))"
            in src)
    # The face says WHY the number moves, and says the count is per TURN --
    # which is the whole play pattern: throw first, then swing.
    assert "Scales with the cards you discarded this turn." in src


def test_the_ruled_formula_base_delta_lands_on_the_base_term():
    """`formula_base: 3` is the sheet's ruling and CalculationBase is the first
    slot of the triple -- the same var MementoMori's own OnUpgrade bumps."""
    src = _emit("what_the_tokoyo_took")
    assert "DynamicVars.CalculationBase.UpgradeValueBy(3m);" in src


def test_the_sheet_row_still_reads_the_count_this_rider_serves():
    """Guard the premise: if the row stops reading `discards_this_turn` this
    whole section is testing a card that no longer exists."""
    card = loader.peek_card("what_the_tokoyo_took")
    formula = card.effects[0]["amount_formula"]
    assert formula["count"] == "discards_this_turn"
    assert (formula["base"], formula["per"]) == (6, 4)


def test_an_unknown_count_token_is_still_a_named_blocker():
    probe = {"id": "count_probe", "name": "Probe", "cost": 1, "type": "attack",
             "rarity": "rare", "character": "kokomi",
             "archetypes": ["assist"], "role": "payoff",
             "effects": [{"op": "damage", "target": "enemy",
                          "amount_formula": {"base": 6, "per": 4,
                                             "count": "moons_this_combat"}}]}
    assert "moons_this_combat" in gen.blocked_reason(probe, PROFILE)


# --- gyorin_formation: a bonus_formula rider on a BLOCK op -----------------

def test_the_charge_rider_renders_through_the_block_var():
    """B1's rail, one meter over. Without it the card renders and pays a flat
    6 while the sheet says "6, +1 per 2 Charge" -- which is why the generator
    refused it rather than shipping a wrong number."""
    src = _emit("gyorin_formation")
    assert "new CalculationBaseVar(6m)" in src
    assert "new CalculationExtraVar(1m)" in src
    assert ("new CalculatedBlockVar(ValueProp.Move).WithMultiplier("
            "static (card, _) => KokomiResources.GetCharge(card.Owner.Creature)"
            " / 2)" in src)
    assert "Gain {CalculatedBlock:diff()} [gold]Block[/gold]." in src
    assert "Scales with [gold]Charge[/gold]." in src
    # The block delta upgrades the base term, not a Block var the card no
    # longer declares.
    assert "DynamicVars.CalculationBase.UpgradeValueBy(3m);" in src


def test_the_charge_tip_says_block_on_a_block_card():
    """SYS-7, one meter over. The hover tip is the ONLY surface carrying the
    RATE, so a hardcoded noun would be the single place the player can read it
    and would read it wrong."""
    src = _emit("gyorin_formation")
    assert "chargeGrantsBlock: true" in src


def test_the_next_turn_half_is_untouched_by_the_rider():
    """Only the immediate Block scales. The sheet's second row is a flat 6 and
    the sim reads no formula on it, so a rider that leaked across would be a
    live value change hiding in a display fix."""
    card = loader.peek_card("gyorin_formation")
    nxt = next(fx for fx in card.effects if fx["op"] == "block_next_turn")
    assert "bonus_formula" not in nxt
    assert "gain 6 [gold]Block[/gold]" in _emit("gyorin_formation")


# --- what_the_tokoyo_returns: recall_to_draw from DISCARD ------------------

def test_the_discard_recall_has_its_own_home_and_grants_no_loan():
    """The two sources are deliberately asymmetric -- unfiltered vs
    §6.4-filtered, no loan keyword vs Exhaust -- so one class holding both
    would branch on the source at every line."""
    src = _emit("what_the_tokoyo_returns")
    assert "await RecallFromDiscard.Recall(" in src
    assert "RecallFromExhaust" not in src
    # The marker is the EXHAUST pool's cycle exclusion; a discard reader is not
    # in that cycle. tier0 reads the same distinction off `from`.
    assert "IExhaustRetriever" not in src
    assert "It gains [gold]Exhaust[/gold]" not in src
    assert "Choose a card from your discard pile; put it on top of your " \
           "draw pile." in src


def test_both_faces_recall_and_only_the_sly_face_can_self_recall():
    """THE D3 CONTRACT, crossing the wall. The played face is resolving and so
    is not in a pile; the Sly face IS in the discard pile when its rider fires,
    because CardCmd.DiscardAndDraw adds the victim to the pile BEFORE firing
    Hook.AfterCardDiscarded (verified against sts2.dll v0.107.1) -- exactly the
    ordering `test_eb69_tokoyo_returns_selfrecall.py` pins on the sim side. The
    emission is the SAME call on both faces, which is what makes the two
    engines' asymmetry the same asymmetry."""
    src = _emit("what_the_tokoyo_returns")
    assert src.count("await RecallFromDiscard.Recall(") == 2
    assert "AfterCardDiscarded" in src
    # The Sly line is on the face, or the mechanic does not exist at the table.
    assert "[gold]Sly[/gold]: Choose a card from your discard pile" in src


def test_the_mod_leg_carries_the_unfiltered_claim_and_no_loan():
    """Structural parity pin -- a live CombatState is outside the headless C#
    boundary, so this reads the one method both engines route through. Sim
    twin: `effects._op_recall_to_draw`'s discard branch, whose whole content is
    that it applies no filter."""
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    text = (repo / "klee-mod" / "KleeCode" / "Powers"
            / "RecallFromDiscard.cs").read_text(encoding="utf-8")
    assert "PileType.Discard" in text
    assert "PileType.Draw" in text
    assert "CardPilePosition.Top" in text
    # Never the hand, and never a loan: the two things the exhaust branch does
    # that this one must not.
    assert "PileType.Hand" not in text
    assert "AddKeyword" not in text
    # No pool predicate at all -- the discard branch is the raw pile.
    assert "Recallable" not in text


def test_the_sim_discard_branch_is_still_unfiltered():
    """The C# leg is only right while the contract it mirrors holds. Pinned by
    behaviour rather than by reading the source: a card in the pile that every
    filter the exhaust branch applies would have excluded still comes back."""
    import random
    from tier0.engine.state import Card, CombatState
    from tier0.tests.conftest import make_enemy

    player = loader.build_player("kokomi")
    player.draw_pile, player.hand = [], []
    player.exhaust_pile = []
    junk = Card(id="junk", name="junk", cost=1, type="status",
                rarity="status", character="kokomi", effects=[])
    player.discard_pile = [junk]
    st = CombatState(player=player, enemies=[make_enemy(hp=100)],
                     rng=random.Random(0))
    src = Card(id="src", name="src", cost=1, type="skill", rarity="uncommon",
               character="kokomi", effects=[])
    effects._resolve_effects(
        st, [{"op": "recall_to_draw", "amount": 1}], src)
    assert st.player.draw_pile and st.player.draw_pile[0] is junk, \
        "the discard branch is unfiltered (EB-69 / D3, R198)"


def test_exactly_one_committed_row_asks_the_exhaust_source():
    """The premise that kept §6.4's exclusions hypothetical is SPENT, and this
    test records what spending it cost -- which is nothing.

    It used to assert the list was empty, and said that if a row ever asked
    for the exhaust source the constraints would stop being hypothetical.
    W3 (EB-118 Phase 3, R211) shipped `shell_of_sanctuary`'s rewrite
    ("Salvage the Line"), so `lint_recall_exhaust`'s card-shape leg is no
    longer vacuous and the shape rules it enforces are met BY CONSTRUCTION:
    Uncommon, and it Exhausts itself. Both are checked on the codegen side
    and again at load, so this row cannot regress into a Common or into a
    non-Exhausting retriever without a loader error.
    """
    asking = sorted(
        c.id for c in loader._card_index().values()
        for fx in list(c.effects or []) + list(c.sly or [])
        if fx.get("op") == "recall_to_draw" and fx.get("from") == "exhaust")
    assert asking == ["shell_of_sanctuary"]

    row = loader.get_card("shell_of_sanctuary")
    assert row.rarity == "uncommon" and row.exhaust is True


# --- the two unexpressible upgrade deltas ----------------------------------

def test_send_the_runner_upgrades_in_the_ruled_order():
    """D2a rules draw 2 -> discard 1 chosen -> exhaust 1 chosen. Appended, it
    read draw / exhaust / discard: the player exhausted before being asked what
    to throw, which is a different card."""
    src = _emit("send_the_runner")
    assert "DynamicVars.Cards.UpgradeValueBy(1m);" in src
    assert src.index("var pickedUpgrade") < src.index(
        "ExhaustSelection.Open(this);")
    assert src.index("{IfUpgraded:show:Discard 1 card.|}") < src.index(
        "[gold]Exhaust[/gold] 1 card from your hand.")
    # The appended throw rides the SAME screen a printed chosen discard does.
    assert "CardSelectCmd.FromHandForDiscard(" in src
    assert "KitGrant.NotKitCard" in src


def test_wheel_the_ranks_gains_its_block_only_when_upgraded():
    src = _emit("wheel_the_ranks")
    assert ("await CreatureCmd.GainBlock(Owner.Creature, "
            "new BlockVar(3m, ValueProp.Move), cardPlay);" in src)
    assert "{IfUpgraded:show:Gain 3 [gold]Block[/gold].|}" in src
    # Its Sly Block is a DIFFERENT number on a line the sim never upgrades.
    assert "[gold]Sly[/gold]: Gain 4 [gold]Block[/gold]." in src


def test_the_upgrade_only_block_claims_gainsblock_only_when_upgraded():
    """The eligibility half, and it is not cosmetic. BaseLib auto-detects
    `GainsBlock` from CanonicalVars, and the game's Nimble gates its whole
    eligibility on it (`Nimble.CanEnchant` -> `card.GainsBlock`). tier0's
    predicate reads the BASE row (`enchantments._grants_block`), so a declared
    BlockVar would be an eligibility split the moment it shipped, and a flat
    `false` would refuse a Nimble the upgraded card could actually pay."""
    src = _emit("wheel_the_ranks")
    assert "public override bool GainsBlock => IsUpgraded;" in src
    assert "new BlockVar(3m" in src              # inline, at the call site
    assert "new BlockVar(3m, ValueProp.Move)\n" not in src   # not a var decl


def test_both_engines_apply_the_same_two_deltas():
    """Cross-engine row: the sim's applier is the authority on WHAT the upgrade
    is, and these are the two the C# now expresses. Read from tier0 rather than
    restated, so a re-ruling moves both sides."""
    # `get_card("<id>+")` is the M7 door to the upgraded form and hands back a
    # FRESH copy; the applier mutates what it is given, so reaching into the
    # shared index here would poison every later reader of the row.
    runner = loader.get_card("send_the_runner+")
    assert [fx["op"] for fx in runner.effects] == [
        "draw", "discard", "exhaust_from"]
    assert runner.effects[0]["amount"] == 2
    assert runner.effects[1]["select"] == "chosen"

    wheel = loader.get_card("wheel_the_ranks+")
    assert [fx["op"] for fx in wheel.effects] == ["discard", "draw", "block"]
    assert wheel.effects[-1]["amount"] == 3
