"""EB-69 / D3 (R198): `what_the_tokoyo_returns` recalling ITSELF is a CONTRACT.

Thrown away by another card's effect, this card's Sly rider can put the card
back on top of the draw pile. That behaviour was true by OMISSION before
2026-08-23 — nobody wrote it down and nobody chose it — and [USER] ruled it
DELIBERATE rather than accidental (disposition (i)). This file is the pin.

WHAT IS BEING PINNED, and why each half matters:

  1. The discard branch of `effects._op_recall_to_draw` is UNFILTERED. That is
     the documented contract now, not an accident. The engine carries the same
     statement at the branch itself.
  2. Self-recall is a FALLBACK, not a rule. `_best_card` ranks (is attack,
     printed power) and this card prints 0 damage, so a decent Attack anywhere
     in the discard pile beats it. The player's pile state changes the answer,
     which is the whole reason the behaviour is worth keeping.
  3. The PLAYED face cannot self-recall — it is resolving, not sitting in a
     pile. The two faces genuinely differ.
  4. The EXHAUST branch is the contrast case and stays guarded:
     `recall_exhaust_pool` excludes self, kit cards, junk and other
     retrievers, because EB-118 §6.4 required it. THE ASYMMETRY IS REAL AND
     IS NOW INTENTIONAL ON BOTH SIDES. A future change that "tidies" the two
     branches into one filtered implementation breaks this card on purpose
     and must say so.

DECLARED ENGINE/MOD ASYMMETRY: there is no C# leg to check parity against.
`recall_to_draw` is built for the `exhaust` source only in the mod, so
`gen_roster_cards.py` blocks this card by name ("sly branch: recall_to_draw
from 'discard' (only the exhaust source is built)"). The behaviour pinned here
is the SPEC that leg will have to meet — tracked at BACKLOG `EB-122`.
"""
import copy
import random

from tier0.content import loader
from tier0.engine import effects
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy

CARD_ID = "what_the_tokoyo_returns"


def _state(seed=0):
    p = loader.build_player("kokomi")
    p.draw_pile, p.hand, p.discard_pile, p.exhaust_pile = [], [], [], []
    return CombatState(player=p, enemies=[make_enemy(hp=300)],
                       rng=random.Random(seed))


def _sheet_card():
    """The REAL row, not a synthetic twin — the contract is the card's."""
    return copy.deepcopy(loader._card_index()[CARD_ID])


def _filler(cid, ctype="skill", dmg=0):
    fx = [{"op": "damage", "amount": dmg, "target": "enemy"}] if dmg else []
    return Card(id=cid, name=cid, cost=1, type=ctype, rarity="common",
                character="kokomi", effects=fx)


def test_the_sheet_row_still_has_the_sly_recall_this_file_pins():
    """Guard the premise: if the body loses its Sly recall, this whole file is
    testing a card that no longer exists, and it should say so loudly rather
    than pass vacuously."""
    card = _sheet_card()
    assert any(fx.get("op") == "recall_to_draw" for fx in (card.sly or [])), \
        "the Sly rider this contract is about is gone from the sheet"
    assert "assist" in (card.archetypes or [])


def test_self_recall_on_the_chosen_discard_route():
    """THE HEADLINE. Discarded with an otherwise empty pile, it returns."""
    st = _state()
    card = _sheet_card()
    st.player.hand = [card]
    effects._resolve_effects(
        st, [{"op": "discard", "amount": 1, "select": "chosen"}],
        _filler("src"))
    assert st.player.draw_pile and st.player.draw_pile[0] is card, \
        "expected the thrown copy to recall ITSELF to the top of draw"
    assert st.player.discard_pile == []


def test_self_recall_on_the_random_discard_route_too():
    """Every existing Assist 0-cost discards at RANDOM, so the fallback has to
    hold on that route as well or the contract only exists on paper."""
    st = _state(seed=3)
    card = _sheet_card()
    st.player.hand = [card]
    effects._resolve_effects(st, [{"op": "discard", "amount": 1}],
                             _filler("src"))
    assert st.player.draw_pile and st.player.draw_pile[0] is card


def test_a_better_attack_in_the_pile_outranks_the_self_recall():
    """Self-recall is the FALLBACK. `_best_card` ranks (is attack, printed
    power); this card prints 0 damage, so the Attack wins and the thrown copy
    stays in the discard pile."""
    st = _state()
    card = _sheet_card()
    big = _filler("big_attack", "attack", dmg=12)
    st.player.hand = [card]
    st.player.discard_pile = [big]
    effects._resolve_effects(
        st, [{"op": "discard", "amount": 1, "select": "chosen"}],
        _filler("src"))
    assert st.player.draw_pile and st.player.draw_pile[0] is big, \
        "the printed-power ranking must prefer the Attack over the self-recall"
    assert any(c is card for c in st.player.discard_pile)


def test_the_card_is_in_the_discard_pile_when_its_own_rider_fires():
    """The ordering that MAKES the self-recall possible: `_op_discard` moves
    the victim into the pile FIRST, then resolves its Sly riders. If that ever
    inverts, self-recall silently stops happening and nothing else fails."""
    seen = {}
    st = _state()
    probe = Card(id="probe", name="probe", cost=1, type="skill",
                 rarity="uncommon", character="kokomi", effects=[],
                 sly=[{"op": "block", "amount": 1}])
    real_block = effects.OPS["block"]

    def spy(state, fx, card):
        seen["in_discard"] = any(x is probe for x in state.player.discard_pile)
        seen["in_hand"] = any(x is probe for x in state.player.hand)
        return real_block(state, fx, card)

    effects.OPS["block"] = spy
    try:
        st.player.hand = [probe]
        effects._resolve_effects(
            st, [{"op": "discard", "amount": 1, "select": "chosen"}],
            _filler("src"))
    finally:
        effects.OPS["block"] = real_block
    assert seen.get("in_discard") is True
    assert seen.get("in_hand") is False


def test_the_played_face_cannot_recall_itself():
    """Played, the card is resolving rather than sitting in a pile, so it
    recalls something ELSE and gains its printed Block. The two faces genuinely
    differ, and the Sly face is the one with the trick."""
    st = _state()
    card = _sheet_card()
    other = _filler("other")
    st.player.discard_pile = [other]
    effects._resolve_effects(st, card.effects, card)
    assert st.player.draw_pile and st.player.draw_pile[0] is other
    assert not any(c is card for c in st.player.draw_pile)
    assert st.player.block == 4


def test_the_exhaust_branch_still_excludes_self_the_contrast_case():
    """EB-118 §6.4 guarded the exhaust source and only the exhaust source. The
    asymmetry between the two branches is the point of this test, not a bug
    report about it."""
    st = _state()
    retr = Card(id="retr", name="retr", cost=1, type="skill",
                rarity="uncommon", character="kokomi", exhaust=True,
                effects=[{"op": "recall_to_draw", "from": "exhaust",
                          "amount": 1}])
    st.player.exhaust_pile = [retr]
    assert effects.recall_exhaust_pool(st, retr) == [], \
        "the exhaust branch must keep excluding self; only discard is open"


def test_the_one_committed_kokomi_row_reads_the_guarded_branch_as_written():
    """This test used to assert NO Kokomi row asked for the guarded branch,
    and to say that if one ever did the contract needed re-reading rather than
    inheriting. W3 (EB-118 Phase 3, R211) shipped one -- "Salvage the Line",
    `shell_of_sanctuary`'s rewrite -- so the re-reading is DONE HERE, against
    the real row rather than a fabricated probe.

    THE ASYMMETRY HOLDS AND IT IS WHAT THE CARD WANTS. The exhaust branch
    excludes self and every other retriever; the discard branch does not.
    Applied to the shipped row that means A SECOND COPY CAN NEVER FETCH THE
    FIRST -- a real design consequence, disclosed on the sheet (two copies are
    worse than one) -- and it is exactly what §6.4 guarded for: a retriever
    that can fetch a retriever is a loop.
    """
    rows = [c for c in loader._card_index().values()
            if getattr(c, "character", None) == "kokomi"]
    asking = sorted(
        c.id for c in rows
        for fx in list(c.effects or []) + list(c.sly or [])
        if fx.get("op") == "recall_to_draw" and fx.get("from") == "exhaust")
    assert asking == ["shell_of_sanctuary"]

    st = _state()
    carrier = loader.get_card("shell_of_sanctuary")
    second = loader.get_card("shell_of_sanctuary")
    keeper = _filler("keeper")
    st.player.exhaust_pile = [second, keeper]

    pool = effects.recall_exhaust_pool(st, carrier)
    assert [c.id for c in pool] == ["keeper"], \
        "a retriever must never be able to fetch another retriever"
