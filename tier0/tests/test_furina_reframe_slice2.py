"""Furina reframe, SLICE 2 -- the five rows, the drain op, and the aimed Evoke
as the emitter writes it.

The design is `review/ruled/furina-reframe-2026-08-29.md` (R220 A): sec.6.2's
row list, sec.4.4's Evoke, sec.4.6's drain, sec.5's starter delta. Slice one
built the RULES in both engines behind `FURINA_REFRAME` and left the prototype
surface with no row that speaks them; these five rows are that list, and they
are UNRUN -- no seat, no sim round, and under R215 B no number in them is
quotable.

WHAT THIS FILE IS AND IS NOT. `C# FIRST, sim at Balance`
(`docs/current/operations/prototype.md`) is the standing rule, so the ROWS'
behaviour is graded in the mod and pinned in
`klee-mod/KleeTests/Prototype/FurinaReframeSliceTwoTests.cs`. What is here is
the half that has to exist in this engine anyway:

  * `drain_fanfare` IS an op in `effects.OPS`, because the tier0 loader
    validates every prototype row's vocabulary at LOAD -- a row carrying an op
    this engine does not know cannot be committed at all. Given the op, the
    twin was three lines and a count, so it is a real implementation rather
    than a stub;
  * `fanfare_drained` IS in the count registry for the same reason, one door
    over (`EB-135`);
  * the EMITTED SOURCE is read here for the one fact no C# pin can make -- see
    the last section.
"""

import random
import re
from pathlib import Path

import pytest
import yaml

from tier0.content import loader, upgrades
from tier0.engine import effects, furina_reframe, resources
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy

REPO = Path(__file__).resolve().parents[2]
GENERATED = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"

#: The slice, in sheet order. Named once so a row deleted under R213 B's
#: deletion rule takes its pins with it rather than leaving a green file
#: asserting things about nothing.
ROWS = ("proto_fr_salon_debut_named",
        "proto_fr_curtain_call",
        "proto_fr_exit_stage_left",
        "proto_fr_let_the_people_rejoice",
        "proto_fr_intermission")


def furina_state(enemies=None, seed=0):
    p = loader.build_player("furina")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def _card(effects_list, **kw):
    d = dict(id="furina_slice2_test", name="t", cost=1, type="skill",
             character="furina", effects=list(effects_list))
    d.update(kw)
    return Card(**d)


def _sheet_rows():
    return {row["id"]: row for row in
            yaml.safe_load(loader.PROTOTYPE_SHEET.read_text(encoding="utf-8"))
            or []}


def _emitted(class_name):
    return (GENERATED / f"{class_name}.cs").read_text(encoding="utf-8")


def _manifest():
    import json
    return json.loads((GENERATED / "manifest.json").read_text(encoding="utf-8"))


def _face(source):
    return re.search(r'\("description", "((?:[^"\\]|\\.)*)"\)',
                     source).group(1)


# ======================================================================
# 0. THE ROWS ARE ON THE SURFACE AND THEY LOAD
# ======================================================================

def test_the_five_rows_are_committed_and_legal():
    """`loader.prototype_cards` is the schema gate: `Card.from_dict` is total
    on the fields, `_validate_card_shape` runs the same vocabulary checks the
    shipped index runs, and the ids must carry the prototype prefix and collide
    with no shipped card. A row that failed any of those could not be here."""
    cards = {c.id: c for c in loader.prototype_cards()}

    for row in ROWS:
        assert row in cards, row
        assert cards[row].character == "furina"

    # The Rare is the slice's one Attack; the other four are Skills, which is
    # what makes the drain pair a damage row and a survival row rather than two
    # of the same card (`F11` (1) / `F12` (1)).
    assert cards["proto_fr_let_the_people_rejoice"].type == "attack"
    assert {cards[r].type for r in ROWS if r != "proto_fr_let_the_people_rejoice"} \
        == {"skill"}


def test_the_rare_drain_is_a_proto_twin_and_not_the_shipped_kit_card():
    """sec.4.6 stages `let_the_people_rejoice` as a PROTOTYPE TWIN: the shipped
    row is a `kit_card` gated on a full Burst meter and costs 0, and this one
    is a real card with a real cost that reads the HELD meter and never a
    threshold. Neither gate may travel with it -- `kit_card` would make the row
    inexpressible by name, and a `requires` would put back the threshold the
    reframe took out."""
    row = _sheet_rows()["proto_fr_let_the_people_rejoice"]

    assert "kit_card" not in row
    assert "requires" not in row
    assert row["cost"] == 2

    shipped = loader.get_card("let_the_people_rejoice")
    assert shipped.kit_card is True
    assert shipped.requires == "burst_energy_full"


# ======================================================================
# 1. THE DRAIN OP -- sec.4.6
# ======================================================================

def _drain(state, **kw):
    card = _card([{"op": "drain_fanfare"}], **kw)
    effects.resolve_card(state, card)
    return card


@pytest.mark.parametrize("held", [0, 17])
def test_a_drain_takes_the_whole_held_meter(held):
    """0 and 17: the row is playable at ANY value because neither drain card
    carries a `requires` gate, so a drain of nothing is a wasted play the
    player can see coming from the meter."""
    st = furina_state()
    resources.gain_fanfare(st, held, "fixture")
    assert st.player.fanfare == held

    _drain(st)

    assert st.player.fanfare == 0
    assert st.fanfare_drained_this_card == held


def test_a_drain_at_the_cap_takes_the_cap():
    """The ceiling is not a second rule: `gain_fanfare` clamps, so over-filling
    and draining takes exactly the cap. Worth pinning rather than assuming --
    the drain is the first op in this kit that moves the whole meter in a
    line."""
    st = furina_state()
    cap = st.player.fanfare_cap
    assert cap > 0
    resources.gain_fanfare(st, cap + 50, "fixture")
    assert st.player.fanfare == cap

    _drain(st)

    assert st.player.fanfare == 0
    assert st.fanfare_drained_this_card == cap


def test_a_drain_moves_neither_the_floor_nor_the_cap():
    """THE WHOLE DIFFERENCE FROM `crash_fanfare`, the op beside it on the same
    meter: that card's price IS the falling baseline, and this card's price is
    the meter itself. A drain that also dropped the floor would be The Final
    Verdict wearing a different name."""
    st = furina_state()
    resources.gain_fanfare_floor(st, 4, "fixture")
    floor, cap = st.player.fanfare_floor, st.player.fanfare_cap
    resources.gain_fanfare(st, 6, "fixture")

    _drain(st)

    assert st.player.fanfare_floor == floor
    assert st.player.fanfare_cap == cap


def test_a_debt_cannot_be_drained():
    """Track C.2 leaves the meter below zero on purpose and every reader clamps
    at zero (`resources.readable`). So a drain finds nothing, takes nothing and
    LEAVES THE HOLE: paying a card for a debt would make the settle a resource
    rather than a price."""
    st = furina_state()
    resources.drop_fanfare_to_floor(st, 5, "fixture")
    held = st.player.fanfare
    assert held < 0

    _drain(st)

    assert st.player.fanfare == held
    assert st.fanfare_drained_this_card == 0


def test_a_non_fanfare_character_drains_nothing():
    """Every leg of this arm is character-scoped and so is the op: in co-op the
    other seat may be Klee, and `fanfare_cap` 0 is how this engine spells "this
    character has no Fanfare resource"."""
    st = furina_state()
    st.player.fanfare_cap = 0

    _drain(st)

    assert st.fanfare_drained_this_card == 0


def test_the_drain_says_it_happened():
    """D4, and this ledger's whole reason: the fact leaves NO trace in the
    state afterwards. A meter at 0 because nothing was earned and a meter at 0
    because twelve were just spent are the same board a moment later."""
    st = furina_state()
    resources.gain_fanfare(st, 12, "fixture")

    card = _drain(st)

    drained = [ev for ev in st.log if ev["event"] == "fanfare_drained"]
    assert len(drained) == 1
    assert drained[0]["amount"] == 12
    assert drained[0]["source"] == f"card:{card.id}"


# ======================================================================
# 2. THE COUNT -- what the drain BUYS
# ======================================================================

def test_the_count_is_the_drain_and_not_the_meter():
    """THE DEFECT THE COUNT EXISTS TO STOP, and it is silent in every other
    reading: by the time the payoff resolves the meter is 0, so an effect that
    read the METER would pay nothing every time while the face promised
    scaling. Both rows' shapes are exercised on one card."""
    st = furina_state()
    resources.gain_fanfare(st, 7, "fixture")

    effects.resolve_card(st, _card([
        {"op": "drain_fanfare"},
        {"op": "block", "amount_formula": {"base": 0, "per": 1,
                                           "count": "fanfare_drained"}},
    ]))

    assert st.player.fanfare == 0
    assert st.player.block == 7


def test_the_rare_pays_its_base_plus_one_per_point_drained():
    """The Rare's own shape: `base 5, per 1`. At 6 held that is 11 to ALL
    enemies, and at 0 held it is the printed 5 -- the card is never dead, it is
    only small, which is the whole of "playable at any Fanfare value"."""
    for held, expect in ((6, 11), (0, 5)):
        enemy = make_enemy(hp=300)
        st = furina_state(enemies=[enemy])
        resources.gain_fanfare(st, held, "fixture")

        effects.resolve_card(st, _card([
            {"op": "drain_fanfare"},
            {"op": "damage",
             "amount_formula": {"base": 5, "per": 1, "count": "fanfare_drained"},
             "target": "all_enemies"},
        ], type="attack"))

        assert 300 - enemy.hp == expect, held


def test_the_count_is_cleared_per_card_play():
    """Cross-card scoping, the same rule `discards_this_card` and its
    neighbours keep: the card AFTER a drain must read nothing, whatever it
    asks. Without this a second Intermission in the same turn would pay out the
    first one's number on an empty meter."""
    st = furina_state()
    resources.gain_fanfare(st, 9, "fixture")
    effects.resolve_card(st, _card([{"op": "drain_fanfare"}]))
    assert st.fanfare_drained_this_card == 9

    effects.resolve_card(st, _card([
        {"op": "block", "amount_formula": {"base": 0, "per": 1,
                                           "count": "fanfare_drained"}}]))

    assert st.fanfare_drained_this_card == 0
    assert st.player.block == 0


def test_focus_never_scales_the_drained_amount():
    """THE REFRAME'S SCALING INVARIANT (sec.4.4): the Focus term multiplies
    PERFORMANCE numerics and nothing else. A full stage and a live Evoke leg
    must not move a drain by a point -- the meter's own number is the meter's
    own number, and a rider on it would let the stage pay twice for one
    turn."""
    st = furina_state()
    st.player.salon = ["crabaletta", "chevalmarin", "usher"]
    st.player.powers["salon_member"] = 3
    resources.gain_fanfare(st, 20, "fixture")

    with_stage = None
    for staged in (True, False):
        s = furina_state()
        if staged:
            s.player.salon = list(st.player.salon)
            s.player.powers["salon_member"] = 3
        resources.gain_fanfare(s, 20, "fixture")
        effects.resolve_card(s, _card([{"op": "drain_fanfare"}]))
        if with_stage is None:
            with_stage = s.fanfare_drained_this_card
        else:
            assert s.fanfare_drained_this_card == with_stage == 20


def test_the_count_is_registered_where_the_loader_looks():
    """`EB-135`. A token the resolver knows and the registry omits makes the
    LOAD check reject valid content; a token in the registry the resolver
    ignores documents a spelling nothing reads. Both directions are pinned
    generically in `test_content_boundaries`; this is the row-level half."""
    assert effects.is_known_count("fanfare_drained")
    loader._validate_effect_vocabulary("probe_card", [
        {"op": "drain_fanfare"},
        {"op": "block", "amount_formula": {"count": "fanfare_drained"}}])


def test_the_op_is_registered_and_takes_no_fields():
    """NO FIELDS AT ALL, and that is the rule rather than an omission: the op
    takes the whole held meter, so an `amount:` would be a number the card
    could not honour. The emitter refuses one by name; here the sim's own door
    is checked."""
    assert "drain_fanfare" in effects.OPS
    with pytest.raises(ValueError, match="unknown"):
        loader._validate_effect_vocabulary("probe_card", [
            {"op": "drain_fanfar"}])


# ======================================================================
# 3. THE UPGRADES -- the Prototype-stage rule, extended to a fifth arm
# ======================================================================

def test_four_rows_carry_the_designers_upgrade_and_the_rare_takes_the_rule():
    """`EB-283` / `EB-315`, and BOTH channels are live on this slice.

    An AUTHORED `upgrade:` block always wins -- that is how a ruled delta
    replaces the Prototype-stage default without the rule having to be removed
    -- and four of these five rows carry one: an Encore rider on the starter, a
    price cut on each Evoke, and Retain on the survival drain. The Rare
    declares nothing and takes the rule's own last-resort clause, which reads
    its cost because a formula-scaled hit has no literal to bump.

    The reframe is IN `PROTOTYPE_DEFAULT_PREFIXES` all the same, and that is
    not redundant: the list is what makes a row declaring nothing get a
    campfire that does something, and the Rare is the row proving it.
    """
    assert "proto_fr_" in upgrades.PROTOTYPE_DEFAULT_PREFIXES
    rows = _sheet_rows()
    manifest = _manifest()["upgrades"]

    assert rows["proto_fr_salon_debut_named"]["upgrade"] == {
        "add": {"op": "gain_encore", "amount": 2}}
    assert rows["proto_fr_curtain_call"]["upgrade"] == {"encore_cost": -1}
    assert rows["proto_fr_exit_stage_left"]["upgrade"] == {"encore_cost": -1}
    assert rows["proto_fr_intermission"]["upgrade"] == {"retain": True}
    assert "upgrade" not in rows["proto_fr_let_the_people_rejoice"]

    # The manifest is what the emitted C# was actually built from, so the
    # authored blocks and the derived one are read there rather than off the
    # sheet a second time.
    for row_id in ROWS:
        assert manifest.get(row_id), row_id
    assert manifest["proto_fr_let_the_people_rejoice"] == {
        "cost": upgrades.PROTOTYPE_COST_DELTA}
    assert upgrades.prototype_default_delta(
        "proto_fr_let_the_people_rejoice", 2,
        rows["proto_fr_let_the_people_rejoice"]["effects"]) == {
            "cost": upgrades.PROTOTYPE_COST_DELTA}


def test_the_upgrade_is_visible_on_every_face():
    """The gate's own question, asked of the committed tree: an upgrade a
    player cannot SEE is a campfire choice nobody can grade. The slice uses
    three of the four shapes `gen_prototype_cards` accepts -- an
    `{IfUpgraded:show:...}` clause, the keyword rail and the cost pip -- and
    every row uses exactly one."""
    for cls in ("ProtoFrSalonDebutNamed", "ProtoFrCurtainCall",
                "ProtoFrExitStageLeft"):
        assert "{IfUpgraded:show:" in _face(_emitted(cls)), cls

    # Retain shows on the KEYWORD RAIL under the art, not in the sentence.
    keeper = _emitted("ProtoFrIntermission")
    assert "AddKeyword(CardKeyword.Retain)" in keeper
    assert "{IfUpgraded:show:" not in _face(keeper)

    rare = _emitted("ProtoFrLetThePeopleRejoice")
    assert "EnergyCost.UpgradeBy(-1)" in rare
    assert "{IfUpgraded:show:" not in _face(rare)


def test_the_encore_price_upgrades_on_the_face_and_at_the_gate():
    """THE DEFECT THIS SLICE HIT, and it is `EB-288`/`EB-291`'s class arriving
    through the one field that was meant to be free text.

    A prototype row states its own face (`EB-215`), so the two Evokes wrote
    "Spend 2 [gold]Encore[/gold]." as a LITERAL. `upgrade: {encore_cost: -1}`
    then emitted a real `UpgradeCostBy(-1)` -- the gate and the badge charge the
    moved number -- while the face went on printing the old one, and the
    emitter's own visibility gate refused the row for exactly that reason
    ("OnUpgrade moves no var and the face prints no upgradable number").

    The price is the EMITTER'S sentence now, on both face paths, built by the
    one `meter_price_clauses`. So a row's `description:` says what the card
    DOES and never what it costs, and the printed price and the charged price
    are one number.
    """
    rows = _sheet_rows()
    for row_id in ("proto_fr_curtain_call", "proto_fr_exit_stage_left"):
        assert "Spend" not in rows[row_id]["description"], row_id
        assert "Encore" not in rows[row_id]["description"], row_id

    # 2 -> 1: the base game's own swap, the shape `dress_rehearsal` ships.
    curtain = _face(_emitted("ProtoFrCurtainCall"))
    assert curtain.startswith("Spend {IfUpgraded:show:1|2} [gold]Encore[/gold].")

    # 1 -> 0: THE WHOLE SENTENCE GOES on the `+` card, and the separator goes
    # with it. "Spend 0 [gold]Encore[/gold]." is not a smaller price, it is a
    # line claiming a cost the card does not have -- and the rendered path's
    # own first clause already skips a row priced at 0.
    exit_face = _face(_emitted("ProtoFrExitStageLeft"))
    assert exit_face.startswith(
        "{IfUpgraded:show:|Spend 1 [gold]Encore[/gold]. }[gold]Evoke[/gold]")
    assert "Spend 0" not in exit_face

    # The gate moves with the face: one emitted call, on the resource the
    # playability check refuses on and the badge reads.
    for cls in ("ProtoFrCurtainCall", "ProtoFrExitStageLeft"):
        assert ("CustomResources<EncoreResource>.Cost(this)!.UpgradeCostBy(-1);"
                ) in _emitted(cls), cls


def test_the_price_sentence_has_one_builder_for_both_face_paths():
    """The rendered path and the authored path cannot disagree about what a
    price looks like or about whether it upgrades, because there is one
    function. Driven directly, which is the only way to see the third shape
    without a row that has it."""
    import sys
    sys.path.insert(0, str(REPO / "tools"))
    import gen_klee_cards as gen                             # noqa: E402

    assert gen.meter_price_clauses({"encore_cost": 2}, {}) == [
        "Spend 2 [gold]Encore[/gold]."]
    assert gen.meter_price_clauses({"encore_cost": 2}, {"encore_cost": -1}) == [
        "Spend {IfUpgraded:show:1|2} [gold]Encore[/gold]."]
    assert gen.meter_price_clauses({"encore_cost": 1}, {"encore_cost": -1}) == [
        "{IfUpgraded:show:|Spend 1 [gold]Encore[/gold].}"]
    # An over-large delta is a sheet defect, not a refund.
    assert gen.meter_price_clauses({"encore_cost": 1}, {"encore_cost": -4}) == [
        "{IfUpgraded:show:|Spend 1 [gold]Encore[/gold].}"]
    # A row with no price prints no sentence, upgraded or not.
    assert gen.meter_price_clauses({}, {"encore_cost": -1}) == []

    # And the vanishing clause takes the following space INSIDE the hole, so
    # the `+` face does not open with a blank.
    assert gen._face_from_parts(
        ["{IfUpgraded:show:|Spend 1 [gold]Encore[/gold].}", "Evoke."]) == (
            "{IfUpgraded:show:|Spend 1 [gold]Encore[/gold]. }Evoke.")


# ======================================================================
# 4. THE EMITTED SOURCE -- the one fact no C# pin can make
# ======================================================================
#
# `SalonMember.Chevalmarin` is compiled into the emitted body as an ENUM
# OPERAND, and `KleeTests/Harness/Il.Calls` reads call TOKENS -- it can say the
# row calls `BowLeftmost`, never which member it names. The two halves of the
# aim pin name each other in their comments so neither can be deleted quietly;
# this is the half that can read the argument.

def test_the_aimed_evoke_names_chevalmarin_and_the_unaimed_one_names_nobody():
    """sec.4.4 / the slot-6 ruling (2026-08-30): the dedicated Evoke CHOOSES
    which member it removes, and the front is what it takes when nothing is
    named. Both rows go through the ONE shipped verb -- registering a
    `salon_evoke` op would have moved the priced-op set, which is a
    DRAFTER_VERSION bump for a synonym -- so the difference between them is
    exactly this argument."""
    aimed = _emitted("ProtoFrExitStageLeft")
    front = _emitted("ProtoFrCurtainCall")

    assert ("SalonMemberPower.BowLeftmost(choiceContext, Owner.Creature, 1, "
            "SalonMember.Chevalmarin);") in aimed
    # AND THE UNAIMED ROW EMITS NO ARGUMENT AT ALL. The verb's third parameter
    # defaults to null, which is the front, so a row that names nobody is
    # byte-identical to what it was before the slot-6 ruling -- which is what
    # keeps the SHIPPED tree (`take_your_bow` prints the same call) out of this
    # slice's diff.
    assert ("SalonMemberPower.BowLeftmost(choiceContext, Owner.Creature, 1);"
            ) in front
    assert "SalonMember." not in front

    shipped = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina"
               / "Generated" / "TakeYourBow.cs").read_text(encoding="utf-8")
    assert ("SalonMemberPower.BowLeftmost(choiceContext, Owner.Creature, 1);"
            ) in shipped


def test_the_named_deploy_names_crabaletta():
    """sec.5's starter delta: a NAMED member, so which member is on the board
    is a decision and not a coin flip. The shipped starter deploys
    `SalonMember` `random` and this one does not, which is the entire row."""
    named = _emitted("ProtoFrSalonDebutNamed")

    assert "SalonMember.Crabaletta);" in named
    assert "SalonMemberPower.Deploy(" in named
    # ... and the shipped row it is a delta OF still rolls, so the two are a
    # real A/B rather than a rename.
    shipped = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina"
               / "Generated" / "SalonDebut.cs").read_text(encoding="utf-8")
    assert "random Salon Member" in shipped


def test_both_drain_rows_bind_their_number_to_the_drain():
    """The multiplier is where the count is chosen, and binding it to
    `FurinaResources.ReadableFanfare` -- what every OTHER Fanfare rider in the
    mod binds to -- would resolve to 0 on both rows every time."""
    for cls in ("ProtoFrLetThePeopleRejoice", "ProtoFrIntermission"):
        source = _emitted(cls)
        assert "WithMultiplier(static (card, _) => FurinaDrain.Amount(card))" \
            in source, cls
        assert "FurinaResources.ReadableFanfare" not in source, cls
        assert "FurinaDrain.Drain(Owner.Creature);" in source, cls


def test_the_three_words_carry_their_definitions():
    """`EB-272`: the tip is attached because the face PRINTED the word. The
    generic join is pinned for every keyword in `test_arm_keyword_tips.py`;
    this is the slice-level half, which also says WHICH word each row prints --
    a Deploy row taking the Evoke definition would pass the generic gate."""
    owed = {"ProtoFrSalonDebutNamed": "ForDeploy",
            "ProtoFrCurtainCall": "ForEvoke",
            "ProtoFrExitStageLeft": "ForEvoke",
            "ProtoFrLetThePeopleRejoice": "ForDrain",
            "ProtoFrIntermission": "ForDrain"}
    for cls, call in owed.items():
        source = _emitted(cls)
        assert f"ArmKeywordTips.{call}(" in source, cls


def test_the_faces_print_what_the_rows_do():
    """The face is the row's own (`EB-215`), so this is the one place the
    printed sentence and the emitted body are compared. Every clause below is a
    rule the body carries out."""
    faces = {cls: _face(_emitted(cls)) for cls in
             ("ProtoFrSalonDebutNamed", "ProtoFrCurtainCall",
              "ProtoFrExitStageLeft", "ProtoFrLetThePeopleRejoice",
              "ProtoFrIntermission")}

    assert faces["ProtoFrSalonDebutNamed"].startswith(
        "[gold]Deploy[/gold] Mademoiselle Crabaletta.")
    # The Encore price is PRINTED, which is this sheet's shipped convention
    # (`Spend N [gold]Encore[/gold].` on every priced Furina row), and it is
    # the EMITTER's sentence rather than the row's -- the upgraded halves are
    # `test_the_encore_price_upgrades_on_the_face_and_at_the_gate`.
    assert ("Spend {IfUpgraded:show:1|2} [gold]Encore[/gold]."
            in faces["ProtoFrCurtainCall"])
    assert "Spend 1 [gold]Encore[/gold]." in faces["ProtoFrExitStageLeft"]
    # THE FALLBACK IS PRINTED, and it has to be: the engine does not waste an
    # aimed Evoke whose member is absent, it Evokes the front and says so
    # (`furina_reframe.EVOKE_TARGET_ABSENT`). A face that stopped at the name
    # would leave the player guessing at exactly the moment it matters.
    assert "or the front member if she is not on stage" in \
        faces["ProtoFrExitStageLeft"]
    for cls in ("ProtoFrLetThePeopleRejoice", "ProtoFrIntermission"):
        assert faces[cls].startswith(
            "[gold]Drain[/gold] your [gold]Fanfare[/gold]."), cls
    assert "to ALL enemies" in faces["ProtoFrLetThePeopleRejoice"]


def test_the_absent_aim_the_face_promises_is_the_one_the_engine_takes(
        monkeypatch):
    """The face above is checked against the RULE rather than against a second
    copy of its own sentence: Exit Stage Left prints "or the front member if
    she is not on stage", and what the engine does is Evoke the front and SAY
    SO. The aim leaves no trace in the state afterwards, which is why the
    report exists at all (D4).

    THE LEG HAS TO BE ON for the aim to mean anything -- with it off the
    argument is ignored and the verb pops the front, which is the shipped bow
    to the digit. Both halves are asserted, because "the shipped bow comes back
    when the leg does not apply" is the acceptance condition of the whole
    quarantine.
    """
    monkeypatch.setattr(furina_reframe, "FURINA_REFRAME", True)
    monkeypatch.setattr(furina_reframe, "FURINA_REFRAME_EVOKE", True)

    st = furina_state()
    st.player.salon = ["usher", "crabaletta"]
    st.player.powers["salon_member"] = 2
    st.player.encore = 9

    assert furina_reframe.evoke_target_index(st.player, "chevalmarin") \
        == furina_reframe.EVOKE_TARGET_ABSENT

    effects.resolve_card(st, _card(
        [{"op": "salon_bow", "amount": 1, "member": "chevalmarin"}]))

    # The front member left, not nobody: an aimed card that cannot find its
    # member is an UNAIMED Evoke, never a wasted one.
    assert st.player.salon == ["crabaletta"]
    absent = [ev for ev in st.log if ev["event"] == "salon_evoke_target_absent"]
    assert len(absent) == 1
    assert absent[0]["member"] == "chevalmarin"

    # ... and the aim that CAN be found takes its own member out of the middle
    # of the queue, which is the slot-6 ruling's whole content.
    st2 = furina_state()
    st2.player.salon = ["usher", "chevalmarin"]
    st2.player.powers["salon_member"] = 2
    st2.player.encore = 9
    effects.resolve_card(st2, _card(
        [{"op": "salon_bow", "amount": 1, "member": "chevalmarin"}]))
    assert st2.player.salon == ["usher"]
