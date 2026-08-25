"""EB-134: a `recall_to_draw` hiding in a `sly:` list is still a retriever.

THE DEFECT WAS ONE LINE AND IT DISARMED FOUR CHECKS. `effects.
retrieves_from_exhaust` walked `_walk_effects(card.effects)`, and `Card.sly`
(`tier0/engine/state.py:262`) is its OWN effect list that no amount of
recursion from inside `card.effects` reaches. Everything that asks "is this
card a retriever" rides that one predicate, so a `sly:`-borne
`{op: recall_to_draw, from: exhaust}` escaped:

  1. `loader._validate_recall_shape` — constraint 1 (Uncommon-or-Rare) never
     ran, so a COMMON permanent retriever loaded clean;
  2. the same, constraint 2 (the retrieval card must itself Exhaust);
  3. `effects.recall_exhaust_pool` — the sly retriever read as ELIGIBLE
     FODDER, including for itself, which is precisely the cycle the
     exclusion exists to prevent: the pile stops being a one-way rotation;
  4. `tools/lint_recall_exhaust` — the sweep rides the same walk, so the
     lint agreed with the defect rather than catching it;

and the codegen's `IExhaustRetriever` stamp (the C# twin of (3)) omitted the
marker, so the mod's pool filter could not see the card by type either.

THE FIX IS ONE WALK, TWO SPELLINGS. `effects.walk_card_effects` (Card
objects) and `effect_walk.iter_card_effects` (sheet rows) yield the played
face's tree AND the Sly branch's. `_walk_effects` / `iter_effects` are left
alone on purpose: `_printed_power` ranks what a card pays when you PLAY it,
and folding a discard-only rider into that scalar would mis-rank every Assist
card for every chooser. The choice is per-question, so the walk is
per-question, which is the discipline `iter_effects_top` already states.

NO LIVE CARD IS AFFECTED, checked rather than assumed — see
`test_no_live_row_is_a_sly_exhaust_retriever`. Fourteen committed rows carry
Sly riders and exactly one of them prints `recall_to_draw`
(`what_the_tokoyo_returns`), from the DISCARD pile, which is a different verb
outside §6.4's exhaust cycle. So no record and no generated file moves here;
the row's content fence is discharged rather than tested against a shipped
card, and the fabricated-card technique the filing used is kept.
"""

from __future__ import annotations

import random

import pytest
import yaml

from tier0.content import loader
from tier0.engine import effects
from tier0.engine.state import Card, CombatState, Player
from tools import effect_walk
from tools import gen_klee_cards as gen

SHEETS = ["docs/klee-cards.yaml", "docs/furina-cards.yaml",
          "docs/kokomi-cards.yaml"]

RECALL = {"op": "recall_to_draw", "from": "exhaust", "amount": 1}


def _row(*, sly: bool, rarity="uncommon", exhaust=True, cid="fab_retriever"):
    """A retriever whose recall sits in `sly:` or at the top level.

    The pair is the whole test: EVERY assertion below is made twice, and the
    two answers must agree. A fix that made the sly row answer differently
    from its top-level twin would be a new divergence wearing the old one's
    clothes.
    """
    row = {
        "id": cid, "name": "Fabricated Retriever", "cost": 1,
        "type": "skill", "rarity": rarity,
        "effects": [{"op": "draw", "amount": 1}],
    }
    if exhaust:
        row["exhaust"] = True
    if sly:
        row["sly"] = [dict(RECALL)]
    else:
        row["effects"] = [dict(RECALL)]
    return row


def _card(**kw) -> Card:
    return Card.from_dict(_row(**kw))


BOTH = pytest.mark.parametrize("sly", [True, False],
                               ids=["sly-nested", "top-level"])


# --- the predicate itself --------------------------------------------------

@BOTH
def test_the_predicate_sees_both_halves_of_the_card(sly):
    assert effects.retrieves_from_exhaust(_card(sly=sly)) is True


def test_the_autoplay_marker_is_not_an_effect():
    """`{op: sly_autoplay}` is a card PLAY, not an effect list (EB-71/R174),
    and must not be mistaken for one by the widened walk."""
    row = _row(sly=True)
    row["sly"].insert(0, {"op": "sly_autoplay"})
    card = Card.from_dict(row)
    ops = [fx.get("op") for fx in effects.walk_card_effects(card)]
    assert "sly_autoplay" not in ops
    assert effects.retrieves_from_exhaust(card) is True


def test_a_sly_discard_recall_is_not_an_exhaust_retriever():
    """The live near-miss, as a test. `what_the_tokoyo_returns` prints
    exactly this shape; widening the walk must not drag the discard verb into
    §6.4's exhaust cycle."""
    row = _row(sly=True)
    row["sly"] = [{"op": "recall_to_draw", "amount": 1}]     # default: discard
    assert effects.retrieves_from_exhaust(Card.from_dict(row)) is False


# --- seams 1 and 2: the loader's shape law ---------------------------------

@BOTH
def test_loader_refuses_a_common_retriever(sly):
    with pytest.raises(ValueError, match="constraint 1"):
        loader._validate_recall_shape(_card(sly=sly, rarity="common"))


@BOTH
def test_loader_refuses_a_non_exhausting_retriever(sly):
    with pytest.raises(ValueError, match="constraint 2"):
        loader._validate_recall_shape(_card(sly=sly, exhaust=False))


@BOTH
def test_loader_accepts_a_legal_retriever(sly):
    loader._validate_recall_shape(_card(sly=sly))            # no raise


# --- seam 3: the runtime pool ----------------------------------------------

@BOTH
def test_a_retriever_is_not_fodder_for_the_pool(sly):
    """Constraint 3. The sly retriever must be excluded both as another
    card's target and as its own."""
    reader = _card(sly=sly, cid="fab_reader")
    victim = _card(sly=sly, cid="fab_victim")
    ordinary = Card.from_dict({
        "id": "fab_ordinary", "name": "Ordinary", "cost": 1,
        "type": "skill", "rarity": "common",
        "effects": [{"op": "draw", "amount": 1}]})
    state = CombatState(player=Player(hp=10, max_hp=10), enemies=[],
                        rng=random.Random(0))
    state.player.exhaust_pile = [victim, ordinary, reader]
    pool = {c.id for c in effects.recall_exhaust_pool(state, reader)}
    assert pool == {"fab_ordinary"}, pool


# --- seam 4: the lint sweep ------------------------------------------------

@BOTH
def test_the_lint_sees_the_retrieval_line(sly):
    from tools import lint_recall_exhaust as lint
    assert len(lint._retrieval_rows(_row(sly=sly))) == 1


@BOTH
def test_the_lint_reports_the_shape_breaches(sly):
    """The sweep's own findings, not just its walk: a Common non-exhausting
    sly retriever must produce the RARITY and NOT SELF-EXHAUSTING lines."""
    from tools import lint_recall_exhaust as lint
    row = _row(sly=sly, rarity="common", exhaust=False)
    rows = lint._retrieval_rows(row)
    assert rows, "the sweep cannot see the line at all"
    assert row.get("rarity") not in lint.ALLOWED_RARITIES
    assert not row.get("exhaust")


# --- the codegen stamp -----------------------------------------------------

@BOTH
def test_codegen_stamps_the_marker_interface(sly):
    row = _row(sly=sly)
    row["effects"] = [{"op": "draw", "amount": 1}] if sly else row["effects"]
    assert "IExhaustRetriever" in gen.emit(row, gen.KOKOMI_PROFILE), (
        "the C# pool filter cannot see this card by type")


def test_a_sly_discard_recall_is_not_stamped():
    row = _row(sly=True)
    row["sly"] = [{"op": "recall_to_draw", "amount": 1}]
    assert "IExhaustRetriever" not in gen.emit(row, gen.KOKOMI_PROFILE)


# --- the shared walks agree ------------------------------------------------

@BOTH
def test_the_two_walks_answer_the_same_question(sly):
    """`effects.walk_card_effects` (Card objects) and
    `effect_walk.iter_card_effects` (sheet rows) are the same reading on the
    two sides of the loader wall; a drift between them is how this defect
    would come back one seam at a time."""
    row = _row(sly=sly)
    sheet_ops = sorted(fx.get("op")
                       for fx in effect_walk.iter_card_effects(row))
    card_ops = sorted(fx.get("op")
                      for fx in effects.walk_card_effects(Card.from_dict(row)))
    assert sheet_ops == card_ops


# --- the content fence -----------------------------------------------------

def test_no_live_row_is_a_sly_exhaust_retriever():
    """The row's content fence, checked rather than trusted.

    If this goes red a shipped card just became a retriever through its Sly
    branch, which is a RECORD and CODEGEN change (`IExhaustRetriever` lands
    on it, and the loader starts enforcing constraints 1-2 against it) — a
    finding to report, not something to ship quietly."""
    offenders = []
    for sheet in SHEETS:
        for row in yaml.safe_load(open(sheet, encoding="utf-8")):
            if not isinstance(row, dict):
                continue
            for fx in effect_walk.iter_effects(effect_walk.sly_riders(row)):
                if (fx.get("op") == "recall_to_draw"
                        and fx.get("from", "discard") == "exhaust"):
                    offenders.append((sheet, row.get("id"), fx))
    assert offenders == [], offenders


def test_the_one_live_sly_recall_is_the_discard_verb():
    """The near-miss, pinned so it is not rediscovered. Exactly one committed
    row prints `recall_to_draw` in `sly:`, and it reads the DISCARD pile."""
    rows = yaml.safe_load(open("docs/kokomi-cards.yaml", encoding="utf-8"))
    hits = [(r["id"], fx)
            for r in rows if isinstance(r, dict)
            for fx in effect_walk.iter_effects(effect_walk.sly_riders(r))
            if fx.get("op") == "recall_to_draw"]
    assert [cid for cid, _ in hits] == ["what_the_tokoyo_returns"], hits
    assert hits[0][1].get("from", "discard") == "discard"
