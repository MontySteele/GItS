"""EB-118: exhaust-pile retrieval as a SOURCE on recall_to_draw.

The packet's §6.4 lists six constraints and says where each is enforced:
one op, one pool filter, one loader check -- never card-author discipline.
This file is the executable form of that list.

  1. Uncommon or Rare .............. loader._validate_recall_shape (+ the
  2. the retrieval card Exhausts ...  codegen's blocked_reason, both legs
                                      pinned below)
  3. no kit card, no retriever (the card ITSELF included)  effects.
  4. top of the DRAW pile, never the hand                  recall_exhaust_
  5. the returned card gains Exhaust for the combat        pool /
  6. no Status, no Curse (C11)                             _op_recall_to_draw

The design bargain the tests are protecting: the retrieval card and a draw
slot are the price, and what comes back is on LOAN -- one more use, then it
rotates again and pays Charge again at the ordinary funnel. Banked Charge
never falls, because Charge is never spent (LAW).
"""
import random
import subprocess
import sys
from pathlib import Path

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy
from tier05 import draft

REPO = Path(loader.__file__).resolve().parents[2]

RECALL = {"op": "recall_to_draw", "from": "exhaust", "amount": 1}


def kokomi_state(seed=0):
    p = loader.build_player("kokomi")
    p.draw_pile, p.hand, p.discard_pile = [], [], []
    return CombatState(player=p, enemies=[make_enemy(hp=300)],
                       rng=random.Random(seed))


def kokomi_card(**kw):
    d = dict(id="kokomi_test", name="t", cost=0, type="skill",
             character="kokomi")
    d.update(kw)
    return Card(**d)


def retriever(**kw):
    d = dict(id="probe_recall", name="Probe Recall", cost=1, type="skill",
             character="kokomi", rarity="uncommon", exhaust=True,
             effects=[dict(RECALL)])
    d.update(kw)
    return Card(**d)


def a_keeper():
    """An ordinary personal card -- eligible by every constraint."""
    return kokomi_card(id="keeper", cost=1, type="attack",
                       rarity="common",
                       effects=[{"op": "damage", "amount": 6,
                                 "target": "enemy"}])


# --- the positive case ----------------------------------------------------

def test_a_personal_card_comes_back_on_top_of_the_draw_pile_on_loan():
    st = kokomi_state()
    keeper = a_keeper()
    st.player.exhaust_pile = [keeper]
    st.player.draw_pile = [kokomi_card(id="under")]

    effects.resolve_card(st, retriever())

    assert st.player.draw_pile[0] is keeper          # constraint 4: TOP
    assert keeper not in st.player.exhaust_pile
    assert keeper.exhaust is True                    # constraint 5: on loan
    assert st.player.hand == []                      # constraint 4: NOT hand


def test_the_loan_is_per_instance_not_per_row():
    """The returned card gains Exhaust for the rest of THIS combat. The
    sheet row and any twin of the card elsewhere in the deck are untouched
    -- the flag lives on the instance, like cost_delta_this_combat."""
    st = kokomi_state()
    keeper = a_keeper()
    twin = a_keeper()
    st.player.exhaust_pile = [keeper]
    st.player.hand = [twin]

    effects.resolve_card(st, retriever())

    assert keeper.exhaust is True
    assert twin.exhaust is False
    assert loader.peek_card("waterspout").exhaust is True   # sheet unmoved
    assert loader.peek_card("pearl_diver").exhaust is False


def test_the_returned_card_pays_charge_again_when_it_re_exhausts():
    """The C11 funnel, end to end: a retrieved PERSONAL card is not junk, so
    its second rotation pays Charge at refpowers.after_card_exhausted like
    any other exhaust. Nothing about retrieval is a special case there --
    that is the point of gaining the ordinary keyword rather than a flag.
    """
    st = kokomi_state()
    keeper = a_keeper()
    st.player.exhaust_pile = [keeper]
    pull = retriever()
    st.player.hand = [pull]
    st.player.energy = 3

    combat.play_card(st, pull)
    # The retrieval card itself Exhausts (constraint 2) and pays once.
    assert pull in st.player.exhaust_pile
    assert st.player.charge == C.CHARGE_PER_EXHAUST

    st.player.hand = [keeper]
    st.player.energy = 3
    combat.play_card(st, keeper)

    assert keeper in st.player.exhaust_pile
    assert st.player.charge == 2 * C.CHARGE_PER_EXHAUST
    # Charge is never SPENT (LAW): taking a card out of the pile weakens
    # pile READERS while it is gone, and the bank does not fall.
    assert st.player.charge >= C.CHARGE_PER_EXHAUST


def test_the_pile_reader_is_the_only_thing_the_loan_costs():
    """While the card is out of the pile, exhaust-pile scalers see one card
    fewer -- and that is the whole of the downside, by design."""
    st = kokomi_state()
    st.player.exhaust_pile = [a_keeper(), a_keeper()]
    before = len(st.player.exhaust_pile)

    effects.resolve_card(st, retriever())

    assert len(st.player.exhaust_pile) == before - 1


# --- the red cases: constraints 3 and 6 -----------------------------------

def test_a_kit_card_is_never_retrieved():
    st = kokomi_state()
    kit = kokomi_card(id="ceremonial_garment", kit_card=True)
    st.player.exhaust_pile = [kit]

    effects.resolve_card(st, retriever())

    assert st.player.draw_pile == []
    assert kit in st.player.exhaust_pile
    assert kit.exhaust is False


@pytest.mark.parametrize("junk_id", ["confiscated", "curse_guilty"])
def test_a_status_or_curse_is_never_retrieved(junk_id):
    """Constraint 6, which is the C11 rotation law read from the other end:
    junk is not one of YOUR cards, so it neither pays Charge on the way out
    nor comes back."""
    st = kokomi_state()
    junk = loader.get_card(junk_id)
    st.player.exhaust_pile = [junk]

    effects.resolve_card(st, retriever())

    assert st.player.draw_pile == []
    assert junk in st.player.exhaust_pile


def test_another_retrieval_card_is_never_retrieved():
    """Constraint 3, the cycle exclusion: a retriever pulling a retriever is
    how the exhaust pile stops being a one-way rotation."""
    st = kokomi_state()
    other = retriever(id="other_recall")
    st.player.exhaust_pile = [other]

    effects.resolve_card(st, retriever())

    assert st.player.draw_pile == []
    assert other in st.player.exhaust_pile


def test_the_retrieval_card_cannot_retrieve_itself():
    """The self case of constraint 3, tested on the ROUTE that produces it:
    the retrieval card Exhausts, so it lands in the pile it reads. It is
    excluded twice over -- as a retriever, and by instance identity."""
    st = kokomi_state()
    pull = retriever()
    st.player.exhaust_pile = [pull]

    effects.resolve_card(st, pull)

    assert st.player.draw_pile == []
    assert pull in st.player.exhaust_pile


def test_the_instance_guard_holds_even_for_a_card_the_predicate_misses():
    """`is not card` is the belt to the predicate's braces: whatever else is
    true of the playing card, it is not its own target."""
    st = kokomi_state()
    plain = a_keeper()
    st.player.exhaust_pile = [plain]

    pool = effects.recall_exhaust_pool(st, plain)

    assert pool == []


def test_junk_and_kit_do_not_block_an_eligible_card():
    """The exclusions must narrow the pool, not empty it: with junk, a kit
    card and one real card in the pile, the real card comes back."""
    st = kokomi_state()
    keeper = a_keeper()
    st.player.exhaust_pile = [loader.get_card("curse_guilty"),
                              kokomi_card(id="kit", kit_card=True),
                              keeper,
                              retriever(id="other_recall")]

    effects.resolve_card(st, retriever())

    assert st.player.draw_pile == [keeper]
    assert len(st.player.exhaust_pile) == 3


def test_a_companion_card_stays_eligible():
    """§6.4 says so explicitly: only kit, retrievers and junk are out."""
    st = kokomi_state()
    companion = loader.get_card("gorou_war_banner")
    st.player.exhaust_pile = [companion]

    effects.resolve_card(st, retriever())

    assert st.player.draw_pile == [companion]
    assert companion.exhaust is True


def test_an_empty_or_fully_excluded_pile_is_a_no_op():
    st = kokomi_state()
    effects.resolve_card(st, retriever())
    assert st.player.draw_pile == []
    assert st.player.hand == []


# --- the discard source is unchanged --------------------------------------

def test_the_discard_source_still_works_and_grants_no_loan():
    """Headbutt's shape is untouched: same op, other pile, and NO gained
    Exhaust -- the loan is what the exhaust pile is charged for."""
    st = kokomi_state()
    keeper = a_keeper()
    st.player.discard_pile = [keeper]

    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "recall_to_draw", "amount": 1}]))

    assert st.player.draw_pile == [keeper]
    assert keeper.exhaust is False


def test_an_unknown_source_still_raises():
    st = kokomi_state()
    with pytest.raises(ValueError):
        effects.resolve_card(st, kokomi_card(
            effects=[{"op": "recall_to_draw", "from": "hand"}]))


def test_no_placement_but_the_top_exists():
    st = kokomi_state()
    with pytest.raises(ValueError):
        effects.resolve_card(st, kokomi_card(
            effects=[{"op": "recall_to_draw", "from": "exhaust",
                      "position": "bottom"}]))


# --- constraints 1 and 2: card SHAPE, at load -----------------------------

def test_a_common_retriever_refuses_to_load():
    with pytest.raises(ValueError, match="Uncommon-or-Rare"):
        loader._validate_recall_shape(retriever(rarity="common"))


def test_a_retriever_that_does_not_exhaust_refuses_to_load():
    with pytest.raises(ValueError, match="must itself Exhaust"):
        loader._validate_recall_shape(retriever(exhaust=False))


def test_a_legal_retriever_loads():
    for rarity in ("uncommon", "rare"):
        loader._validate_recall_shape(retriever(rarity=rarity))


def test_the_shape_check_reaches_a_conditional_branch():
    """A capability armed inside a `then:` is still armed. The shape check
    walks the tree for the same reason _validate_effect_vocabulary does."""
    hidden = retriever(rarity="common", effects=[
        {"op": "conditional", "if": "has_spark",
         "then": [dict(RECALL)], "else": []}])
    assert effects.retrieves_from_exhaust(hidden)
    with pytest.raises(ValueError):
        loader._validate_recall_shape(hidden)


def test_exactly_one_shipped_card_uses_the_capability():
    """The staged capability has its first carrier, and the design call was
    [USER]'s exactly as this test was written to require.

    It used to assert the list was EMPTY -- EB-118 landed retrieval as staged
    infrastructure and nothing shipped on it. W3 (EB-118 Phase 3, R211) rewrote
    `shell_of_sanctuary` into "Salvage the Line", the repo's first
    Exhaust-retrieving row, and the shape rules that governed the staging are
    satisfied BY CONSTRUCTION rather than by exemption: Uncommon (a Common
    retriever is refused by name) and self-Exhausting (a retriever that does
    not Exhaust is refused by name).
    """
    carriers = sorted(c.id for c in loader._card_index().values()
                      if effects.retrieves_from_exhaust(c))
    assert carriers == ["shell_of_sanctuary"]

    card = loader.get_card("shell_of_sanctuary")
    assert card.rarity in ("uncommon", "rare")
    assert card.exhaust is True


# --- engine closure -------------------------------------------------------

def test_retrieval_creates_no_card_so_the_closure_detector_stays_quiet():
    """The tier0 closure detector counts cards CREATED against cards
    consumed. Retrieval moves a card between piles and creates none, so a
    turn spent retrieving is not a positive-sum cycle -- and the detector
    must not learn to say it is."""
    p = loader.build_player("kokomi")
    p.draw_pile, p.discard_pile = [], []
    p.hand = [retriever()]
    p.exhaust_pile = [a_keeper()]
    state = combat.run_fight(
        p, [make_enemy(hp=1, intents=[{"kind": "block", "amount": 0}])],
        lambda s: next((c for c in s.player.hand
                        if c.id == "probe_recall"), None),
        seed=0)
    assert not any(ev["event"] == "engine_closure" for ev in state.log)


def test_the_closure_lint_sweeps_the_whole_graph_and_is_clean():
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_recall_exhaust.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "ENGINE CLOSURE swept" in res.stdout
    # A verdict needs a denominator (lint_strict_domination's rule).
    assert "swept 0 card(s)" not in res.stdout


# --- the drafter: the generic price applies, no D move --------------------

def test_the_two_sources_price_identically():
    """PROPOSED (see STATIC_RECALL_VALUE): the exhaust source gets no hook
    of its own, so this is the pinned proof that the generic price applies
    -- not an assertion that the two are worth the same to a player."""
    disc = draft._op_price({"op": "recall_to_draw", "amount": 1})
    exh = draft._op_price(dict(RECALL))
    assert disc == exh == draft.STATIC_RECALL_VALUE


def test_the_op_is_still_priced_exactly_once():
    assert "recall_to_draw" in draft.STATIC_OP_PRICING
    assert "recall_to_draw" in effects.OPS


# --- the C# leg -----------------------------------------------------------

CS = (REPO / "klee-mod" / "KleeCode" / "Powers" / "RecallFromExhaust.cs")


def test_the_generator_emits_the_shared_call_and_the_marker():
    from tools import gen_klee_cards as gen
    row = {"id": "probe_recall", "name": "Probe Recall", "cost": 1,
           "type": "skill", "rarity": "uncommon", "exhaust": True,
           "character": "kokomi", "archetypes": ["priest"], "role": "glue",
           "effects": [dict(RECALL)]}
    assert gen.blocked_reason(row, gen.KOKOMI_PROFILE) is None
    src = gen.emit(row, gen.KOKOMI_PROFILE)
    # ONE C# home for the six constraints; the body is the call.
    assert "await RecallFromExhaust.Recall(" in src
    assert "IExhaustRetriever" in src
    # The face carries both halves of the bargain.
    assert "on top of your draw pile" in src
    assert "It gains [gold]Exhaust[/gold]" in src


def test_the_generator_refuses_the_shapes_the_loader_refuses():
    from tools import gen_klee_cards as gen
    base = {"id": "probe_recall", "name": "Probe Recall", "cost": 1,
            "type": "skill", "rarity": "uncommon", "exhaust": True,
            "character": "kokomi", "effects": [dict(RECALL)]}
    common = dict(base, rarity="common")
    assert "constraint 1" in gen.blocked_reason(common, gen.KOKOMI_PROFILE)
    no_exhaust = dict(base, exhaust=False)
    assert "constraint 2" in gen.blocked_reason(no_exhaust, gen.KOKOMI_PROFILE)
    # A source neither engine knows is still a NAMED blocker.
    bad_source = dict(base, effects=[{"op": "recall_to_draw",
                                      "from": "deck", "amount": 1}])
    assert "recall_to_draw from 'deck'" in gen.blocked_reason(
        bad_source, gen.KOKOMI_PROFILE)


def test_the_six_constraints_are_the_exhaust_sources_and_only_its():
    """EB-122 restages the line this file used to hold, which read "the
    discard source is not built". It IS built now -- `what_the_tokoyo_returns`
    ships it -- and the claim that replaced it is the interesting one: §6.4's
    CARD-SHAPE constraints belong to the exhaust source alone.

    They price a LOAN out of a pile a card would never otherwise leave. A
    discard-pile card was coming back on the next reshuffle regardless, so
    there is nothing to price and no cycle to break, and Uncommon-or-Rare and
    self-Exhaust would refuse a legal card for a reason that does not apply to
    it. tier0 draws the same line in the same place
    (`loader._validate_recall_shape`)."""
    from tools import gen_klee_cards as gen
    discard = {"id": "probe_recall_discard", "name": "Probe", "cost": 1,
               "type": "skill", "rarity": "common", "character": "kokomi",
               "archetypes": ["assist"], "role": "glue",
               "effects": [{"op": "recall_to_draw", "amount": 1}]}
    # Common, and does not Exhaust: both fatal on the exhaust source, neither
    # relevant here.
    assert gen.blocked_reason(discard, gen.KOKOMI_PROFILE) is None
    src = gen.emit(discard, gen.KOKOMI_PROFILE)
    assert "await RecallFromDiscard.Recall(" in src
    # NOT an exhaust retriever: that marker is the exhaust pool's cycle
    # exclusion and a discard reader is not in that cycle. The sim reads the
    # same distinction off `from` (`effects.retrieves_from_exhaust`).
    assert "IExhaustRetriever" not in src
    # No loan is granted, and the face does not claim one.
    assert "It gains [gold]Exhaust[/gold]" not in src
    assert "from your discard pile" in src


def test_both_engines_exclude_the_same_three_things():
    """The parity pin. A live CombatState is outside the headless C#
    boundary, so the mod's leg is pinned on the source of the one function
    both engines route through (klee-mod/KleeTests carries the runnable
    half). Sim twin: effects.recall_exhaust_pool."""
    text = CS.read_text(encoding="utf-8")
    for needle in ("KitGrant.NotKitCard", "KokomiResources.IsJunk",
                   "IExhaustRetriever", "CardPilePosition.Top",
                   "PileType.Draw", "CardKeyword.Exhaust"):
        assert needle in text, needle
    assert "PileType.Hand" not in text
