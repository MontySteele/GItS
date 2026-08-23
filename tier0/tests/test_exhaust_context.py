"""EB-118 -- the card-resolution-scoped Exhaust identity context.

The card you chose to Exhaust tells the exhausting card what to do. What is
recorded is printed identity (id, cost, type, rarity, companion/personal
ownership, upgrade state) for the selection the resolving `exhaust_from` just
took, and what a LATER effect on the SAME card can read off it is derived
totals -- printed cost, counts by type, by ownership, by upgrade state.

MOST OF THIS FILE IS THE SCOPING, because the scoping is the part a
combat-global `last_exhausted` would get wrong and no card would notice until
one read another card's victims:

  * the card played AFTER an exhausting card sees NOTHING;
  * two `exhaust_from` effects on ONE card each see their own selection --
    the second OPENS its own context rather than appending to the first;
  * a free play landing mid-resolution cannot hand its victims to the outer
    card;
  * nothing survives a combat.

The mechanism is character-neutral. Kokomi's rotation law (C11) filters her
unfiltered pool before any of this runs, so her context never carries junk;
an explicit `filter: status` card (Klee's Dodge Roll shape) resolves through
the same op and records its victims too. There is deliberately NO "Status
exhausted" reward grammar -- the context reports rarity and stops there.
"""
import random

from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy


def kokomi_state(seed=0):
    p = loader.build_player("kokomi")
    return CombatState(player=p, enemies=[make_enemy(hp=300)],
                       rng=random.Random(seed))


def a_card(**kw):
    d = dict(id="t", name="t", cost=0, type="skill", character="kokomi")
    d.update(kw)
    return Card(**d)


def burner(*, amount=1, effects_after=(), **kw):
    """A card that chooses `amount` cards to Exhaust, then does whatever
    `effects_after` says -- the shape every reader on the sheet will have."""
    fx = [dict({"op": "exhaust_from", "amount": amount, "select": "chosen"},
               **kw)]
    return a_card(id="burner", effects=fx + list(effects_after))


def block_reading(count, base=0, per=1):
    """A later effect that prices itself off the selection. `amount_formula`
    is the CalculatedVar shape the C# codegen renders, so the test drives the
    same grammar a sheet row would."""
    return {"op": "block",
            "amount_formula": {"base": base, "per": per, "count": count}}


# --- 1. the descriptors ---------------------------------------------------

def test_the_selection_records_all_six_printed_descriptors():
    st = kokomi_state()
    victim = a_card(id="fodder+", cost=2, type="power", rarity="uncommon",
                    tags=["companion"])
    st.player.hand = [victim]
    effects.resolve_card(st, burner())
    assert st.exhaust_selection == [{
        "id": "fodder+", "cost": 2, "type": "power", "rarity": "uncommon",
        "companion": True, "upgraded": True}]


def test_descriptor_fields_are_the_declared_set():
    """The C# twin records these six off a CardModel; a field added on one
    side only is a parity break, so the tuple is the contract."""
    st = kokomi_state()
    st.player.hand = [a_card(id="fodder")]
    effects.resolve_card(st, burner())
    assert (tuple(st.exhaust_selection[0])
            == effects.EXHAUST_SELECTION_FIELDS)


def test_an_x_cost_victim_contributes_nothing_to_the_printed_total():
    """An X-cost card in hand has no spent value. The descriptor keeps "X"
    raw rather than coercing it to a number a formula would then pay for."""
    st = kokomi_state()
    st.player.hand = [a_card(id="xc", cost="X"), a_card(id="two", cost=2)]
    effects.resolve_card(st, burner(amount=2))
    assert {d["cost"] for d in st.exhaust_selection} == {"X", 2}
    assert effects.exhaust_selection_counts(st.exhaust_selection)["cost"] == 2


# --- 2. the derived reads -------------------------------------------------

def test_a_later_effect_reads_the_total_printed_cost():
    st = kokomi_state()
    st.player.hand = [a_card(id="a", cost=2), a_card(id="b", cost=3)]
    effects.resolve_card(st, burner(
        amount=2, effects_after=[block_reading("exhaust_selection_cost")]))
    assert st.player.block == 5


def test_a_later_effect_reads_counts_by_type():
    st = kokomi_state()
    st.player.hand = [a_card(id="a", type="attack"),
                      a_card(id="b", type="attack"),
                      a_card(id="c", type="power")]
    for count, expected in (("exhaust_selection_attacks", 2),
                            ("exhaust_selection_powers", 1),
                            ("exhaust_selection_skills", 0)):
        st.player.block = 0
        st.player.hand = [a_card(id="a", type="attack"),
                          a_card(id="b", type="attack"),
                          a_card(id="c", type="power")]
        effects.resolve_card(st, burner(
            amount=3, effects_after=[block_reading(count, base=10)]))
        assert st.player.block == 10 + expected, count


def test_a_later_effect_reads_ownership_and_upgrade_counts():
    st = kokomi_state()

    def hand():
        return [a_card(id="own"), a_card(id="own2+"),
                a_card(id="guest", tags=["companion"])]

    for count, expected in (("exhaust_selection_companions", 1),
                            ("exhaust_selection_personal", 2),
                            ("exhaust_selection_upgraded", 1),
                            ("exhaust_selection_size", 3)):
        st.player.block = 0
        st.player.hand = hand()
        effects.resolve_card(st, burner(
            amount=3, effects_after=[block_reading(count)]))
        assert st.player.block == expected, count


def test_the_conditionals_read_the_selection_not_the_pile():
    """`exhaust_pile_at_least_` asks about everything ever rotated off the
    line; these ask about the one choice just made."""
    st = kokomi_state()
    st.player.exhaust_pile = [a_card(id="old", type="attack")]
    st.player.hand = [a_card(id="fresh", type="skill", cost=1)]
    fired = {}
    for name in ("exhaust_selection_has_type_attack",
                 "exhaust_selection_has_type_skill",
                 "exhaust_selection_has_personal",
                 "exhaust_selection_has_companion",
                 "exhaust_selection_size_at_least_1",
                 "exhaust_selection_cost_at_least_2"):
        st.player.hand = [a_card(id="fresh", type="skill", cost=1)]
        st.log.clear()
        effects.resolve_card(st, burner(effects_after=[
            {"op": "conditional", "if": name, "then": []}]))
        fired[name] = next(ev["fired"] for ev in st.log
                           if ev["event"] == "conditional")
    assert fired == {"exhaust_selection_has_type_attack": False,
                     "exhaust_selection_has_type_skill": True,
                     "exhaust_selection_has_personal": True,
                     "exhaust_selection_has_companion": False,
                     "exhaust_selection_size_at_least_1": True,
                     "exhaust_selection_cost_at_least_2": False}


def test_a_card_that_never_exhausted_reads_an_empty_selection():
    """Not an error: "nothing was chosen" is a reading, the same one
    drew_skill_this_card gives a card that drew nothing."""
    st = kokomi_state()
    effects.resolve_card(st, a_card(
        effects=[block_reading("exhaust_selection_cost", base=4)]))
    assert st.player.block == 4


# --- 3. THE SCOPING -------------------------------------------------------

def test_the_next_card_played_sees_no_context():
    st = kokomi_state()
    st.player.hand = [a_card(id="fodder", cost=3)]
    effects.resolve_card(st, burner(amount=1))
    assert st.exhaust_selection

    reader = a_card(id="reader", effects=[
        block_reading("exhaust_selection_cost")])
    effects.resolve_card(st, reader)
    assert st.exhaust_selection == []
    assert st.player.block == 0


def test_two_exhaust_from_effects_on_one_card_each_see_their_own():
    """The ruled replaces/opens rule. The second selection is not the first
    plus the second -- it IS the second, and the reader between them saw the
    first alone."""
    st = kokomi_state()
    st.player.hand = [a_card(id="a", cost=2), a_card(id="b", cost=5)]
    card = a_card(id="twice", effects=[
        {"op": "exhaust_from", "amount": 1, "select": "chosen"},
        block_reading("exhaust_selection_cost"),
        {"op": "exhaust_from", "amount": 1, "select": "chosen"},
        block_reading("exhaust_selection_cost"),
    ])
    effects.resolve_card(st, card)
    # _worst_card takes the highest-cost non-attack first: b (5), then a (2).
    assert [d["id"] for d in st.exhaust_selection] == ["a"]
    assert st.player.block == 5 + 2


def test_a_second_exhaust_from_that_finds_nothing_opens_an_empty_context():
    """The replace is unconditional. A second rotation with an empty hand
    must not leave the first one's victims standing for the reader after
    it -- that is the leak this whole context is shaped to prevent."""
    st = kokomi_state()
    st.player.hand = [a_card(id="only", cost=3)]
    card = a_card(id="twice", effects=[
        {"op": "exhaust_from", "amount": 1, "select": "chosen"},
        {"op": "exhaust_from", "amount": 1, "select": "chosen"},
        block_reading("exhaust_selection_cost"),
    ])
    effects.resolve_card(st, card)
    assert st.exhaust_selection == []
    assert st.player.block == 0


def test_a_free_play_cannot_hand_its_victims_to_the_outer_card():
    """combat._FREE_PLAY_CONTEXT restores the list OBJECT. An inner card that
    exhausts mid-resolution opens its own; the outer card keeps reading the
    selection it opened."""
    st = kokomi_state()
    inner = a_card(id="inner", effects=[
        {"op": "exhaust_from", "amount": 1, "select": "chosen"}])
    st.player.hand = [a_card(id="outer_fodder", cost=2),
                      a_card(id="inner_fodder", cost=9)]
    outer = a_card(id="outer", effects=[
        {"op": "exhaust_from", "amount": 1, "select": "chosen"},
        {"op": "autoplay_from_draw", "amount": 1},
        block_reading("exhaust_selection_cost"),
    ])
    # inner_fodder is the worst card, so the OUTER exhaust takes it (cost 9)
    # and the free play takes what is left (cost 2). The outer reader must
    # still price itself off its own victim.
    st.player.draw_pile = [inner]
    effects.resolve_card(st, outer)
    assert [ev["victims"] for ev in st.log
            if ev["event"] == "exhaust_selection"] == [["inner_fodder"],
                                                       ["outer_fodder"]]
    assert [d["id"] for d in st.exhaust_selection] == ["inner_fodder"]
    assert st.player.block == 9


def test_nothing_survives_a_combat():
    st = kokomi_state()
    st.player.hand = [a_card(id="fodder", cost=4)]
    effects.resolve_card(st, burner())
    assert st.exhaust_selection

    fresh = kokomi_state()
    assert fresh.exhaust_selection == []
    assert fresh.exhaust_selection is not st.exhaust_selection


# --- 4. character neutrality ----------------------------------------------

def test_kokomis_context_never_carries_junk():
    """Her rotation law filters the pool BEFORE the record is written, so the
    context cannot report a Status even to a card that asks about rarity."""
    st = kokomi_state()
    st.player.hand = [loader.get_card("curse_guilty"),
                      loader.get_card("confiscated"),
                      a_card(id="hers", cost=1)]
    effects.resolve_card(st, burner(amount=3))
    assert [d["id"] for d in st.exhaust_selection] == ["hers"]


def test_an_explicit_status_filter_records_its_victims_too():
    """Dodge Roll's shape. The context mechanism is the op's, not Kokomi's --
    a junk-eater's selection is recorded like anyone else's, rarity and all.
    Recording it is NOT a reward grammar: no card reads it, and none may."""
    st = kokomi_state()
    status = loader.get_card("confiscated")
    st.player.hand = [status, a_card(id="keep")]
    effects.resolve_card(st, a_card(
        effects=[{"op": "exhaust_from", "amount": 1, "filter": "status"}]))
    assert [d["id"] for d in st.exhaust_selection] == [status.id]
    assert st.exhaust_selection[0]["rarity"] == "status"


def test_a_player_without_her_hook_records_the_junk_it_takes():
    p = loader.build_player("ref_ironclad")
    st = CombatState(player=p, enemies=[make_enemy(hp=50)],
                     rng=random.Random(0))
    st.player.hand = [loader.get_card("curse_guilty")]
    effects.resolve_card(st, Card(
        id="true_grit_plus", name="t", cost=0, type="skill",
        effects=[{"op": "exhaust_from", "amount": 1, "select": "chosen"}]))
    assert [d["rarity"] for d in st.exhaust_selection] == ["curse"]


# --- 5. the emitted parity row --------------------------------------------

def test_one_row_per_resolved_selection_carrying_ids_and_derived_values():
    st = kokomi_state()
    st.player.hand = [a_card(id="a", cost=2, type="attack"),
                      a_card(id="b+", cost=3, tags=["companion"])]
    effects.resolve_card(st, burner(amount=2))
    rows = [ev for ev in st.log if ev["event"] == "exhaust_selection"]
    assert len(rows) == 1
    row = rows[0]
    assert row["card"] == "burner"
    assert sorted(row["victims"]) == ["a", "b+"]
    assert (row["size"], row["cost"], row["attacks"], row["skills"],
            row["powers"], row["companions"], row["personal"],
            row["upgraded"]) == (2, 5, 1, 1, 0, 1, 1, 1)


def test_an_empty_selection_still_emits_its_row():
    """"Nothing was there to take" is a reading, not a gap -- a parity test
    comparing streams must see the same number of rows on both sides."""
    st = kokomi_state()
    effects.resolve_card(st, burner())
    row = next(ev for ev in st.log if ev["event"] == "exhaust_selection")
    assert row["victims"] == [] and row["size"] == 0


def test_the_row_carries_exactly_the_declared_keys():
    st = kokomi_state()
    st.player.hand = [a_card(id="a")]
    effects.resolve_card(st, burner())
    row = next(ev for ev in st.log if ev["event"] == "exhaust_selection")
    assert (tuple(k for k in row if k not in ("turn", "event"))
            == effects.EXHAUST_SELECTION_ROW_KEYS)


def test_the_played_card_routes_normally_around_all_of_this():
    """Guard on the op's existing behaviour: recording a selection moves no
    card. The victims are in the exhaust pile and nowhere else."""
    st = kokomi_state()
    fodder = a_card(id="fodder", cost=2)
    st.player.hand = [fodder]
    b = burner()
    st.player.hand.append(b)
    st.player.energy = 3
    combat.play_card(st, b)
    assert fodder in st.player.exhaust_pile
    assert fodder not in st.player.hand
    assert [d["id"] for d in st.exhaust_selection] == ["fodder"]
