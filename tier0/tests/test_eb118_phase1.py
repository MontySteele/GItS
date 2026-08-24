"""EB-118 Phase 1 -- the acceptance pins for the cleanup batch.

Phase 1 is the coordinated card-body/C#-parity batch that HOLDS card ids,
rarities, roles and archetypes (packet §3). What it moves is bodies, and
several of its results are stated as facts about a POOL rather than about
one card. Those are pinned here, over the whole sheet, so a later row
cannot reintroduce a retired shape one card at a time.

Per-card behaviour lives in the pin-card files beside this one. What is
here is the batch's own contract.
"""

import sys
from pathlib import Path

import yaml

from tier0.content import loader
from tier0.engine import combat, effects
from tier0.tests.conftest import make_enemy, make_state

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))



def _sheet(name):
    with open(REPO / "docs" / f"{name}-cards.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _row(name, cid):
    return next(c for c in _sheet(name) if c["id"] == cid)


def _play(state, card_id, energy=5):
    card = loader.get_card(card_id)
    state.player.energy = energy
    state.player.hand.append(card)
    combat.play_card(state, card)
    return card


def _events(state, name):
    return [ev for ev in state.log if ev["event"] == name]


# --- §4.3: two direct faces gain a readable second price --------------------

def test_blast_radius_charges_a_chosen_discard():
    """The face was flat AoE with nothing to decide. The price is a CHOSEN
    discard -- a random one would be variance rather than a decision, and
    decisions are the packet's whole subject. Base damage is untouched:
    §4.3 says add the second price first and reprice in its own window."""
    enemies = [make_enemy(hp=40), make_enemy(hp=40)]
    state = make_state(enemies=enemies)
    state.player.hand.append(loader.get_card("strike"))
    state.player.hand.append(loader.get_card("defend"))

    _play(state, "blast_radius")

    assert [e.hp for e in enemies] == [31, 31]
    discards = _events(state, "discard")
    assert len(discards) == 1 and discards[0]["chosen"] is True
    assert len(state.player.discard_pile) >= 1


def test_no_holding_back_pays_both_of_its_prices():
    """Two prices, both existing grammar: the card Exhausts, and it adds one
    `confiscated` -- Klee's already-shipped status-price vocabulary, not an
    inline Burn injector -- to the discard pile."""
    enemies = [make_enemy(hp=40), make_enemy(hp=40)]
    state = make_state(enemies=enemies)

    card = _play(state, "no_holding_back")

    assert [e.hp for e in enemies] == [26, 26]
    assert [c.id for c in state.player.exhaust_pile] == ["no_holding_back"]
    assert card not in state.player.hand
    assert [c.id for c in state.player.discard_pile] == ["confiscated"]


def test_both_face_prices_survive_the_upgrade():
    """§4.3 keeps the ruled damage upgrade for the structural pass and says
    BOTH prices remain. An upgrade that quietly bought off a price would be
    the second ruling this batch is not allowed to make."""
    base, up = loader.get_card("blast_radius"), loader.get_card("blast_radius+")
    assert up.effects[0]["amount"] == base.effects[0]["amount"] + 3
    assert up.effects[-1] == {"op": "discard", "amount": 1, "select": "chosen"}

    nhb, nhb_up = (loader.get_card("no_holding_back"),
                   loader.get_card("no_holding_back+"))
    assert nhb_up.effects[0]["amount"] == nhb.effects[0]["amount"] + 4
    assert nhb_up.exhaust is True
    assert nhb_up.effects[-1]["card"] == "confiscated"


# --- §4.6: the `skill_tag` contribution becomes visible ---------------------

MOD_CARDS = REPO / "klee-mod" / "KleeCode" / "Cards"


def _cs_source(cid):
    """The shipped C# for one Klee row -- generated or hand-written."""
    cls = "".join(part.title() for part in cid.split("_")).replace("Mk2", "Mk2")
    for path in (MOD_CARDS / "Generated", MOD_CARDS):
        for candidate in path.glob("*.cs"):
            text = candidate.read_text(encoding="utf-8")
            if f"class {cls} " in text or f"class {cls}(" in text \
                    or f"class {cls}\n" in text or f"class {cls}:" in text:
                return text
    return None


def test_every_skill_tag_face_prints_the_burst_it_pays():
    """The tag was worth BURST_PER_SKILL_TAG on play and no face said so --
    a real number on fifteen cards that the player could only learn by
    watching the meter. Every one of them now prints it, the hand-written
    `pop` included, which is the card this pin exists for: it does not come
    out of the generator and would have been the one that stayed silent."""
    from tier0 import constants as C

    tagged = [c["id"] for c in _sheet("klee")
              if "skill_tag" in (c.get("tags") or ())]
    assert len(tagged) == 15

    line = f"[gold]Burst[/gold] +{C.BURST_PER_SKILL_TAG}."
    for cid in tagged:
        source = _cs_source(cid)
        assert source is not None, cid
        assert line in source, cid


def test_the_burst_line_is_text_and_not_a_third_keyword():
    """Rail 1 of the packet's binding rails: Klee gets no third keyword out
    of this pass. A `CardKeyword` would give the line a badge, a tooltip and
    a place in the game's auto-keyword pipeline -- which is what a keyword
    IS. So the text is checked to exist and the keyword list is checked not
    to name it."""
    marker = "IEnumerable<CardKeyword> CanonicalKeywords"
    for cid in ("pop", "mine_toss", "all_my_treasures"):
        source = _cs_source(cid)
        assert "[gold]Burst[/gold] +5." in source, cid
        # The DECLARATION, not any prose that mentions it -- the whole point
        # of the pin is which list the word is in.
        assert marker in source, cid
        declaration = source.split(marker, 1)[1].split(";", 1)[0]
        assert "Burst" not in declaration, cid


def test_the_meter_arithmetic_did_not_move():
    """The other half of §4.6: the tag, its membership and its arithmetic
    are untouched, and only the reading changed. One play, one payment, at
    the constant the face now prints."""
    from tier0 import constants as C

    state = make_state(enemies=[make_enemy(hp=200)])
    state.player.burst_max = 100

    _play(state, "pop")

    income = [(ev["source"], ev["amount"])
              for ev in _events(state, "burst_income")]
    assert income == [("skill_tag", C.BURST_PER_SKILL_TAG)]
