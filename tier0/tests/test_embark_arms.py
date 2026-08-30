"""EB-188: the door that lets a blind whole-fight run carry a prototype arm.

The gate after a pair read ADVANCES an arm is whole-fight blind play, and it
could not run for ANY arm: prototype rows are quarantined out of every pool by
construction, so a blind run cannot draw one. `understudy/embark.py --arm`
grants the row into the STARTING DECK once the run is open, through the dev
door that already existed -- `give_card` with `pile: "deck"` is the run-scoped
route (`RunState.CreateCard` + `CardPileCmd.Add`), the same pair a card reward
runs, so no C# was added.

Nothing here launches a game. The three refusals, the wire spelling, the grant
body and the record's identity line are all reachable with an injected version
tuple and a stub wire, which is the point: the LIVE acceptance is a sealed
blind run and it is owed from the art-bearing checkout, but a door whose
refusals are only provable live is a door nobody can trust before then.
"""

from __future__ import annotations

import json

import pytest

from understudy import blindplay, bridge, embark

DEV = ("0.2.1314+proto", "the deployed `mods\\klee\\manifest.json` `version`")
RELEASE = ("0.2.1314", "the deployed `mods\\klee\\manifest.json` `version`")
UNREAD = ("", "no deployed package at ...\\mods\\klee\\manifest.json")

ARM = "proto_spark_priced_draw"


# ------------------------------------------------------------- refusals ----

def test_an_unknown_arm_is_refused_against_the_surface():
    """Refused HERE rather than by the far side's `unknown card id`: the
    question the operator got wrong is which rows the surface holds, and a
    slice whose rows have already left it cannot be granted at all."""
    with pytest.raises(embark.EmbarkError) as excinfo:
        embark.check_arms(["proto_not_a_row"], DEV)
    assert "proto_not_a_row" in str(excinfo.value)
    assert "prototype-surface.yaml" in str(excinfo.value)


def test_a_release_build_is_refused():
    """The prototype classes are `Compile Remove`d unless PrototypeCards=true,
    so on a release build there is no id to grant. `deploy_proto.ps1` stamps
    `+proto` and `deploy.ps1` never does, so the stamp is the whole check."""
    with pytest.raises(embark.EmbarkError) as excinfo:
        embark.check_arms([ARM], RELEASE)
    assert "+proto" in str(excinfo.value)
    assert "deploy_proto" in str(excinfo.value)


def test_an_unreadable_build_is_refused_rather_than_assumed():
    """Not-read is not a dev build. A door that opens when it cannot see is
    not a door."""
    with pytest.raises(embark.EmbarkError) as excinfo:
        embark.check_arms([ARM], UNREAD)
    assert "could not be read" in str(excinfo.value)


def test_a_dev_build_and_a_real_row_pass():
    assert embark.check_arms([ARM], DEV) == DEV


# ------------------------------------------------------------- the grant ---

def test_the_wire_spelling_is_the_give_card_id():
    assert embark.wire_id(ARM) == "KLEEMOD-PROTO_SPARK_PRICED_DRAW"
    assert embark.wire_id("  proto_x  ") == "KLEEMOD-PROTO_X"


def test_the_grant_goes_into_the_deck_not_a_combat_pile(monkeypatch):
    """EB-91: the scope is part of the path. A combat-scoped grant is a
    GENERATED card -- not in the deck, gone at the end of the fight -- which
    is not a starting deck and would answer a different question."""
    calls: list[dict] = []

    def fake(card_id, count=1, upgraded=False, pile="deck"):
        calls.append({"card_id": card_id, "count": count,
                      "upgraded": upgraded, "pile": pile})
        return {"status": "ok", "card_name": "Rummage", "message": "granted"}

    monkeypatch.setattr(bridge, "give_card", fake)
    granted = embark.grant_arms([ARM])
    assert calls == [{"card_id": "KLEEMOD-PROTO_SPARK_PRICED_DRAW",
                      "count": 1, "upgraded": False, "pile": "deck"}]
    assert granted[0]["arm"] == ARM
    assert granted[0]["card_name"] == "Rummage"


def test_a_failed_grant_stops_the_embark(monkeypatch):
    """A half-granted run would produce a record naming cards the deck does
    not hold, which is worse than no run."""
    monkeypatch.setattr(bridge, "give_card",
                        lambda *a, **k: {"status": "error",
                                         "message": "no run in progress"})
    with pytest.raises(embark.EmbarkError) as excinfo:
        embark.grant_arms([ARM])
    assert "no run in progress" in str(excinfo.value)


def test_the_refusal_lands_before_the_game_is_launched(monkeypatch):
    """The build and the row id are facts about the machine and the request.
    Learning them after the launch costs a launch and a teardown for nothing.
    """
    from understudy import soak

    def explode(*a, **k):                                     # pragma: no cover
        raise AssertionError("the game was launched despite a bad --arm")

    monkeypatch.setattr(soak, "Session", explode)
    monkeypatch.setattr(embark, "check_arms",
                        lambda arms, version=None: (_ for _ in ()).throw(
                            embark.EmbarkError("refused")))
    with pytest.raises(embark.EmbarkError):
        embark.embark("klee", arms=[ARM])


def test_a_plain_embark_never_checks_the_build(monkeypatch):
    """No `--arm`, no build question: an ordinary embark is unchanged."""
    monkeypatch.setattr(embark, "check_arms",
                        lambda *a, **k: (_ for _ in ()).throw(
                            AssertionError("checked the build with no arms")))

    class Boom(Exception):
        pass

    def stop(*a, **k):
        raise Boom

    from understudy import soak
    monkeypatch.setattr(soak, "Session", stop)
    with pytest.raises(Boom):
        embark.embark("kokomi")


# ---------------------------------------------------------- the record -----

def _sidecar(tmp_path, seed, arms):
    blob = {"stamp": "20260829-000000", "run_seed": seed}
    if arms is not None:
        blob["arms_granted"] = arms
    (tmp_path / "embark-20260829-000000.json").write_text(
        json.dumps(blob), encoding="utf-8")
    return tmp_path


def test_the_record_names_the_arms_granted_into_this_run(tmp_path):
    d = _sidecar(tmp_path, "F128JG2J44Z5",
                 [{"card_id": "KLEEMOD-PROTO_SPARK_PRICED_DRAW"}])
    named, source = blindplay.granted_arms("F128JG2J44Z5", d)
    assert named == "KLEEMOD-PROTO_SPARK_PRICED_DRAW"
    assert "matched by run seed" in source


def test_a_sidecar_from_another_run_does_not_lend_its_arms(tmp_path):
    """The seed is the run's identity (R95). A stale sidecar naming arms on
    somebody else's run would be a record that is simply false."""
    d = _sidecar(tmp_path, "OTHERSEED0000",
                 [{"card_id": "KLEEMOD-PROTO_SPARK_PRICED_DRAW"}])
    assert blindplay.granted_arms("F128JG2J44Z5", d)[0] == "(none)"


def test_a_run_with_no_grant_says_so_positively(tmp_path):
    d = _sidecar(tmp_path, "F128JG2J44Z5", None)
    named, source = blindplay.granted_arms("F128JG2J44Z5", d)
    assert named == "(none)"
    assert "no `--arm` grant" in source


def test_the_identity_block_prints_the_line():
    text = blindplay.record_markdown(
        {"session_id": "x", "guardrail": "g", "fight_records": [],
         "run_record": ""},
        {"run_seed": "F128JG2J44Z5",
         "arms_granted": "KLEEMOD-PROTO_SPARK_PRICED_DRAW",
         "arms_granted_source": "the embark sidecar"})
    assert "- **arms_granted**: KLEEMOD-PROTO_SPARK_PRICED_DRAW" in text
    assert "- **arms_granted_source**: the embark sidecar" in text


def test_the_guardrail_travels_with_the_grant():
    """A caveat that lives only in a comment is a caveat that is not in the
    record. The endpoint stamps it, `bridge` keeps the harness-side copy, and
    the sidecar records it beside the grant."""
    assert "not one the generators produced" in bridge.GRANT_GUARDRAIL


# ------------------------------- the shipped half (`KLEESPARK-W3`) ---------
#
# A registration can need a deck at a stated maker : sink ratio, and on the
# Spark arm the sinks are prototype rows while the makers are SHIPPED ones.
# The door granted prototypes only, so that deck could not be built at all --
# and granting the makers around the harness would leave them out of the
# embark sidecar, which is where the sealed record reads `arms_granted` from.

SHIPPED_MAKER = "skip_and_hop"


def test_a_shipped_card_id_is_accepted():
    """`KLEESPARK-W3` sec 18.2's six makers are shipped rows, not prototypes."""
    assert embark.check_arms([SHIPPED_MAKER], DEV) == DEV


def test_a_shipped_only_grant_does_not_need_a_proto_build():
    """A shipped row exists in a release build, so refusing one there would
    be the door refusing to open on a question nobody asked."""
    assert embark.check_arms([SHIPPED_MAKER], RELEASE) == RELEASE


def test_a_prototype_row_in_the_list_still_forces_the_proto_check():
    """One prototype id anywhere in the list and the build stamp binds."""
    with pytest.raises(embark.EmbarkError) as excinfo:
        embark.check_arms([SHIPPED_MAKER, ARM], RELEASE)
    assert "+proto" in str(excinfo.value)


def test_an_id_on_neither_surface_is_still_refused():
    with pytest.raises(embark.EmbarkError) as excinfo:
        embark.check_arms(["not_a_card_anywhere"], DEV)
    assert "not_a_card_anywhere" in str(excinfo.value)
    assert "shipped card id" in str(excinfo.value)


def test_the_kind_is_recorded_beside_every_grant(monkeypatch):
    """The sidecar says which surface each granted row came off, so a record
    of a mixed deck does not read as a record of an all-prototype one."""
    monkeypatch.setattr(bridge, "give_card",
                        lambda *a, **k: {"status": "ok", "card_name": "x"})
    granted = embark.grant_arms([ARM, SHIPPED_MAKER])
    assert [g["kind"] for g in granted] == ["prototype", "shipped"]


def test_the_shipped_index_holds_the_six_klee_makers():
    """Named rather than counted: these are the rows sec 18.2 grants, and a
    sheet rename that dropped one would silently shrink the deck."""
    ids = embark.shipped_ids()
    for cid in ("skip_and_hop", "warm_glow", "snap", "hot_hands",
                "all_my_treasures", "da_da_da"):
        assert cid in ids
    assert ARM not in ids          # the prototype surface is NOT in this set
