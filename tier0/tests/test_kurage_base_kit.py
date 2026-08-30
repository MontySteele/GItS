"""THE KURAGE BASE KIT, VERSION 4: the jellyfish is always on, and one
Muster card takes Bake-Kurage's seat in the starter deck.

[USER], 2026-08-29, verbatim and the whole spec:

    "I think that we will want to make Bake-Kurage part of the base kit
    (always on) rather than a separate card. So yes, we could add one Muster
    card to the base deck to teach the pattern."

It answers sec.11.8: at the starter floor the v3 rule fired exactly once per
fight, on the one free card, and the bank was never spent and never blocked --
so the interesting half of the design (bank toward a card you cannot yet
afford; be blocked when you over-bank) was DRAFTED and never PRINTED. A Muster
in the opening deck prints RULE 1 in fight 1: the card sacrificed to it enters
the memory at three times its cost, which is a price the starter can fail to
pay.

EVERYTHING HERE IS QUARANTINED behind `C.KURAGE_MEMORY` (and, for the
jellyfish and the starter swap, `C.KURAGE_ALWAYS_ON` beneath it). The GOLDEN
tests at the top are the acceptance condition on the flag: with the flag off
the starter is the printed one and no jellyfish exists that a card did not
summon.

NO NUMBER TAKEN OFF THIS ARM IS QUOTABLE ANYWHERE (R213 B / R215 B). Every
assertion below is about what the engine DOES.
"""

import copy
import random

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, effects
from tier0.engine.state import CombatState, KurageMemory
from tier0.pilot.policy import make_pilot
from tier0.tests.conftest import make_enemy
from tier05 import rewards, shop

DROP = "bake_kurage"
ADD = "to_the_front"


@pytest.fixture
def base_kit(monkeypatch):
    """The flag ON, and the base kit with it. Every test that takes this
    fixture is testing the prototype; every test that does not is testing
    the shipped engine."""
    monkeypatch.setattr(C, "KURAGE_MEMORY", True)
    monkeypatch.setattr(C, "KURAGE_ALWAYS_ON", True)


@pytest.fixture
def v3_arm(monkeypatch):
    """The memory rule WITHOUT the base kit -- the v3 arm, kept reachable by
    one constant so a revert is a flip and not a re-authoring."""
    monkeypatch.setattr(C, "KURAGE_MEMORY", True)
    monkeypatch.setattr(C, "KURAGE_ALWAYS_ON", False)


def kokomi_state(enemies=None, seed=0):
    p = loader.build_player("kokomi")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def fight(seed=1, hp=(120, 60)):
    p = loader.build_player("kokomi")
    return combat.run_fight(p, [make_enemy(hp=h) for h in hp],
                            make_pilot(loader.pilot_weights("commander")),
                            seed=seed)


# --------------------------------------------------------------------------
# THE GOLDEN: flag off is today, exactly
# --------------------------------------------------------------------------

def test_the_base_kit_constant_is_only_read_under_the_master_flag():
    """`KURAGE_ALWAYS_ON` ships True. That is harmless and deliberate: it is
    read only where `KURAGE_MEMORY` has already been checked, and
    `KURAGE_MEMORY` is the quarantine."""
    assert C.KURAGE_MEMORY is False
    assert C.KURAGE_ALWAYS_ON is True


def test_flag_off_the_printed_starter_is_untouched():
    ids = loader.starting_deck("kokomi")
    assert DROP in ids and ADD not in ids
    assert len(ids) == 12
    assert [c.id for c in loader.build_player("kokomi").draw_pile] == ids


def test_flag_off_no_jellyfish_exists_that_no_card_summoned():
    st = fight()
    assert not [e for e in st.log if e["event"] == "kurage_base_kit"]


def test_flag_off_the_summon_still_counts_down():
    """The v0.4 jellyfish, unmoved: summoned for KURAGE_DURATION turns, one
    turn spent per pulse."""
    st = kokomi_state()
    effects._op_summon_kurage(st, {"op": "summon_kurage"},
                              loader.get_card(DROP))
    assert st.player.powers["kurage_summon"] == C.KURAGE_DURATION
    st.kurage_last_card_type = "skill"
    effects.player_turn_end_triggers(st)
    assert st.player.powers["kurage_summon"] == C.KURAGE_DURATION - 1


# --------------------------------------------------------------------------
# A -- THE ALWAYS-ON JELLYFISH
# --------------------------------------------------------------------------

def test_the_jellyfish_is_on_the_field_from_the_start_of_combat(base_kit):
    st = fight()
    installed = [e for e in st.log if e["event"] == "kurage_base_kit"]
    assert len(installed) == 1 and installed[0]["persistent"] is True
    # And it was there BEFORE the first turn opened.
    assert st.log.index(installed[0]) < min(
        i for i, e in enumerate(st.log) if e["event"] == "turn_open")


def test_it_is_hers_alone(base_kit):
    """The base kit is Kokomi's. A Companion-playing Klee must not acquire a
    jellyfish because a constant is on."""
    p = loader.build_player("klee")
    st = combat.run_fight(p, [make_enemy(hp=60)],
                          make_pilot(loader.pilot_weights("demolition")),
                          seed=1)
    assert not [e for e in st.log if e["event"] == "kurage_base_kit"]
    assert not p.powers.get("kurage_summon", 0)


def test_the_pulse_fires_on_turn_one_with_nothing_summoned(base_kit):
    st = fight()
    assert [e for e in st.log if e["event"] == "kurage_pulse"]
    assert not [e for e in st.log if e["event"] == "summon_kurage"]


def test_the_jellyfish_never_expires(base_kit):
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    st.kurage_last_card_type = "skill"
    for _ in range(20):
        effects.player_turn_end_triggers(st)
    assert st.player.powers["kurage_summon"] == 1


def test_the_pulse_fires_every_turn_end(base_kit):
    st = fight()
    turns = len([e for e in st.log if e["event"] == "turn_open"])
    pulses = len([e for e in st.log if e["event"] == "kurage_pulse"])
    # One pulse per player turn end; the last turn may end in a kill before
    # the turn-end triggers run, so the pulse count is turns or turns-1.
    assert turns - 1 <= pulses <= turns


def test_with_always_on_off_the_v3_arm_is_whole(v3_arm):
    """The revert is one constant: no install at combat start, and the
    jellyfish is back to something a card must summon."""
    st = fight()
    assert not [e for e in st.log if e["event"] == "kurage_base_kit"]
    st2 = kokomi_state()
    effects._op_summon_kurage(st2, {"op": "summon_kurage"},
                              loader.get_card(DROP))
    assert st2.player.powers["kurage_summon"] == 1
    st2.kurage_last_card_type = "skill"
    effects.player_turn_end_triggers(st2)
    assert st2.player.powers["kurage_summon"] == 1      # v3: no decrement


# --------------------------------------------------------------------------
# B -- THE STARTER DECK
# --------------------------------------------------------------------------

def test_the_starter_swaps_the_summon_for_a_muster(base_kit):
    ids = loader.starting_deck("kokomi")
    assert DROP not in ids
    assert ids.count(ADD) == 1
    assert len(ids) == 12                      # the count does not move


def test_the_battery_and_the_run_read_the_same_starter(base_kit):
    """One seam, `loader._starter_ids`, so tier 0's `build_player` and tier
    0.5's `starting_deck` cannot disagree about what she opens with."""
    assert [c.id for c in loader.build_player("kokomi").draw_pile] \
        == loader.starting_deck("kokomi")


def test_the_swap_survives_the_randomized_starter_roll(base_kit):
    """The support slot's roll and the base-kit swap touch different cards
    and must compose."""
    for seed in range(8):
        ids = loader.starting_deck("kokomi", rng=random.Random(seed))
        assert DROP not in ids and ids.count(ADD) == 1 and len(ids) == 12


def test_no_other_character_starter_moves(base_kit):
    for cid in ("klee", "furina"):
        assert loader.starting_deck(cid) == \
            loader._character_index()[cid]["starting_deck"]


def test_the_sheets_did_not_move(base_kit):
    """The swap is CODE. The printed sheet still prints Bake-Kurage, which is
    what makes the flag a targeted revert."""
    spec = loader._character_index()["kokomi"]
    assert DROP in spec["starting_deck"] and ADD not in spec["starting_deck"]


def test_the_muster_in_the_starter_enrols_the_sacrifice_at_three_times_cost(
        base_kit):
    """THE WHOLE POINT OF B. Playing the starter's Muster in fight 1 puts the
    card it ate into the memory, priced at 3x -- so the bank, the afford and
    the block are printed rather than drafted."""
    st = kokomi_state()
    card = next(c for c in st.player.draw_pile if c.id == ADD)
    st.player.draw_pile.remove(card)
    st.player.hand.append(loader.get_card("waters_edge"))
    st.player.energy = 3
    st.player.hand.append(card)
    combat.play_card(st, card)
    assert [m.card_id for m in st.kurage_queue] == ["waters_edge"]
    entry = st.kurage_queue[0]
    assert entry.rule == "muster"
    # THE NUMBER IS [USER]'S RULE, so it is written out rather than
    # re-derived from the constant it is testing: "cards cost Charge equal
    # to 3x their Cost". Water's Edge is a 1, so the price is a 3.
    assert (entry.cost, entry.price) == (1, 3)
    assert entry.price == entry.cost * C.KURAGE_MEMORY_COST_PER_ENERGY


def test_the_starter_muster_can_bank_a_price_the_starter_cannot_yet_pay(
        base_kit):
    """sec.11.8's missing half, now reachable at the floor: a front priced
    above the bank BLOCKS, and the bank holds."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1       # as combat start installs it
    st.player.hand.append(loader.get_card("waters_edge"))
    effects._op_conscript(st, {"op": "conscript", "amount": 1},
                          loader.get_card(ADD))
    st.player.charge = 1                       # under the price of 3
    assert effects.kurage_fire(st) is False
    assert len(st.kurage_queue) == 1
    assert st.player.charge == 1               # unspent, not lost
    assert [e for e in st.log if e["event"] == "kurage_memory_blocked"]


# --------------------------------------------------------------------------
# C -- WHAT `summon_kurage` MEANS WHEN THE JELLYFISH IS PERMANENT.
# Each test below pins the LEAST-INVASIVE DEFAULT this build chose, and each
# default is a numbered pick returning to [USER] in sec.12.
# --------------------------------------------------------------------------

def test_c1_the_summon_op_is_an_idempotent_no_op(base_kit):
    """Pick 1. `bake_kurage`'s first leg sets a bit that is already set; its
    second leg (gain_charge 1) still pays."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    before = st.player.charge
    play = loader.get_card(DROP)
    st.player.energy = 3
    st.player.hand.append(play)
    combat.play_card(st, play)
    assert st.player.powers["kurage_summon"] == 1
    assert st.player.charge == before + 1
    assert [e for e in st.log
            if e["event"] == "summon_kurage" and e.get("base_kit")]


def test_c2_the_kurage_turns_upgrade_is_inert(base_kit):
    """Pick 2. An upgraded Bake-Kurage is mechanically identical to a base
    one, exactly as it already was under v3."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    effects._op_summon_kurage(st, {"op": "summon_kurage", "amount": 2},
                              loader.get_card(DROP + "+"))
    assert st.player.powers["kurage_summon"] == 1


def test_c3_the_casket_refresh_pays_nothing(base_kit):
    """Pick 3. Refreshing a jellyfish that never expires is a max(1, 1)."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    effects.OPS["apply_power"](st, {"op": "apply_power",
                                    "power": "ceremonial_garment",
                                    "amount": 1, "target": "self"},
                               loader.get_card("waters_edge"))
    assert st.player.powers["kurage_summon"] == 1


def test_c4_the_oaths_ward_is_ruled_and_no_longer_rides_the_pulse(base_kit):
    """Pick 4 is RULED ([USER], 2026-08-29) and the default this test used to
    pin is gone: the pulse no longer carries the ward at all, however many
    stacks are standing. The ward's own section below has the rest."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    st.player.powers["kurage_ward"] = 5
    st.kurage_last_card_type = "skill"
    paid = []
    for _ in range(3):
        st.player.block = 0
        effects.player_turn_end_triggers(st)
        paid.append(st.player.block)
    assert paid == [C.KURAGE_MEMORY_PULSE_BLOCK] * 3


def test_c5_the_fires_summon_gate_can_no_longer_fail_in_a_real_fight(
        base_kit):
    """Pick 5, RULED (R224 A). The dial that let the accelerator keyword fire
    without a jellyfish is DELETED, so both doors -- the automatic fire and the
    keyword -- ask the one question. Under the base kit that question can never
    be answered no in a real fight, which is why the two settings read the same
    and only one of them survives."""
    st = kokomi_state()
    assert st.player.powers.get("kurage_summon", 0) == 0   # a bare state
    st = fight()
    assert st.player.powers.get("kurage_summon", 0) == 1   # a real fight


def test_c5b_the_keyword_asks_the_same_summon_question_as_the_automatic_fire(
        base_kit):
    """The collapsed branch, pinned from the manual side: on a state with no
    jellyfish the keyword fires nothing and pays nothing, exactly as the
    automatic door does. This is the assertion the deleted dial's `False`
    setting used to break."""
    st = armed([memory_entry(price=0)], charge=0)
    st.player.powers.pop("kurage_summon", None)
    effects.OPS["play_front_memory"](st, {"op": "play_front_memory"},
                                     loader.get_card("waters_edge"))
    assert len(st.kurage_queue) == 1
    assert not effects.kurage_fire(st, manual=True)


# --------------------------------------------------------------------------
# KURAGE'S OATH, RE-KEYED TO THE MEMORY PLAY (sec.12.4 pick 4, RULED).
#
# [USER], 2026-08-29: "Let's rewrite it to '3 block per memory played,
# upgrade to 5' as a placeholder and see if it needs adjusting later."
#
# The numbers are a PLACEHOLDER in [USER]'s own word and nothing here is a
# balance claim; the tests below are about WHEN the ward pays and about the
# face carrying the ruled figures, never about whether they are right.
# --------------------------------------------------------------------------

def armed(entries, charge=0, ward=0):
    """A state with the base kit installed, a memory queue, and optionally
    the Oath standing."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    st.player.charge = charge
    if ward:
        st.player.powers["kurage_ward"] = ward
    st.kurage_queue.extend(entries)
    return st


def memory_entry(price=0, card_id="gorou_inuzaka_charge"):
    return KurageMemory(card_id=card_id, cost=price // 3, price=price)


def test_the_ward_pays_on_the_automatic_memory_play(base_kit):
    st = armed([memory_entry()], ward=3)
    st.player.block = 0
    assert effects.kurage_fire(st) is True
    assert st.player.block == 3
    paid = [e for e in st.log if e["event"] == "kurage_ward_paid"]
    assert len(paid) == 1 and paid[0]["amount"] == 3
    assert paid[0]["manual"] is False


def test_the_ward_pays_on_a_stir_play_too(base_kit):
    """The acceleration keyword fires the front outside the automatic
    rhythm, and a memory play is a memory play."""
    st = armed([memory_entry()], ward=3)
    st.player.block = 0
    effects.OPS["play_front_memory"](st, {"op": "play_front_memory"},
                                     loader.get_card("waters_edge"))
    assert st.player.block == 3
    paid = [e for e in st.log if e["event"] == "kurage_ward_paid"]
    assert len(paid) == 1 and paid[0]["manual"] is True


def test_the_ward_does_not_pay_on_the_pulse_under_the_flag(base_kit):
    """THE HALF THAT MOVED. Under the base kit the pulse fires every turn
    end; if the ward still rode it, the Oath would pay per turn for free."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    st.player.powers["kurage_ward"] = 3
    st.kurage_last_card_type = "skill"
    st.player.block = 0
    effects.player_turn_end_triggers(st)
    assert st.player.block == C.KURAGE_MEMORY_PULSE_BLOCK
    assert not [e for e in st.log if e["event"] == "kurage_ward_paid"]


def test_a_blocked_memory_pays_no_ward(base_kit):
    """The ward is per memory PLAYED. A front she cannot afford is not a
    play, so it pays nothing -- which is the whole reason the trigger moved
    off a pulse that cannot be blocked out of."""
    st = armed([memory_entry(price=9)], charge=1, ward=3)
    st.player.block = 0
    assert effects.kurage_fire(st) is False
    assert st.player.block == 0
    assert not [e for e in st.log if e["event"] == "kurage_ward_paid"]


def test_an_empty_memory_pays_no_ward(base_kit):
    st = armed([], ward=3)
    st.player.block = 0
    assert effects.kurage_fire(st) is False
    assert st.player.block == 0


def test_the_ward_is_paid_once_per_play_not_once_per_turn(base_kit):
    """Two fires in one turn (the automatic one plus a Stir) pay twice."""
    st = armed([memory_entry(), memory_entry()], ward=3)
    st.player.block = 0
    assert effects.kurage_fire(st) is True
    effects.OPS["play_front_memory"](st, {"op": "play_front_memory"},
                                     loader.get_card("waters_edge"))
    assert st.player.block == 6
    assert len([e for e in st.log if e["event"] == "kurage_ward_paid"]) == 2


def test_the_amount_is_the_cards_and_never_a_constant(base_kit):
    """3 base, 5 upgraded -- and both come off whatever stacks the card
    applied, so there is no code-side override that could disagree with the
    printed face."""
    for stacks in (3, 5):
        st = armed([memory_entry()], ward=stacks)
        st.player.block = 0
        assert effects.kurage_fire(st) is True
        assert st.player.block == stacks


def test_the_surface_row_prints_the_ruled_placeholder(base_kit):
    """The FACE half of the ruling: the staged row carries [USER]'s 3, on
    the quarantined surface, with the shipped row untouched."""
    rows = {c.id: c for c in loader.prototype_cards()}
    row = rows["proto_kurages_oath_memory"]
    assert row.name == "Kurage's Oath"
    assert (row.cost, row.type, row.rarity) == (1, "power", "common")
    assert row.effects == [{"op": "apply_power", "power": "kurage_ward",
                            "amount": 3, "target": "self"}]


def test_the_shipped_oath_row_did_not_move():
    """No flag, no fixture: the printed sheet is untouched by all of this."""
    shipped = loader.get_card("kurages_oath")
    assert shipped.effects == [{"op": "apply_power", "power": "kurage_ward",
                                "amount": 5, "target": "self"}]
    assert loader.get_card("kurages_oath+").effects[0]["amount"] == 7


def test_flag_off_the_ward_still_rides_the_pulse():
    """THE HARD REQUIREMENT. With the flag off the shipped Oath is exactly
    what it has always been: its ward is paid by the jellyfish's pulse, on
    top of KURAGE_PULSE_BLOCK, and no memory play exists to pay it."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    st.player.powers["kurage_ward"] = 5
    st.player.block = 0
    effects.player_turn_end_triggers(st)
    assert st.player.block == C.KURAGE_PULSE_BLOCK + 5
    assert not [e for e in st.log if e["event"] == "kurage_ward_paid"]


# --------------------------------------------------------------------------
# THE OFFERABLE POOL: under the flag, the staged Oath is the ONLY Oath.
#
# [USER], 2026-08-29, of the staged face: "Why does the power print 5 instead
# of 3, exactly?" Because with the flag on the ward is paid on a MEMORY PLAY
# and its amount is read off whatever card applied it -- so a flagged run that
# DRAFTED the shipped `kurages_oath` paid 5 per memory play under a face that
# says per pulse. Text that cannot bind is a defect (D4). Both sheets are
# frozen, so the fix is on the OFFER side: `loader._pool_substitutions` swaps
# the staged row in at the same rarity and `rewards.character_pool` -- the one
# source every offer surface reads (fight rewards, the shop, the event card
# screens, the tier 0.5 drafter) -- applies it.
#
# NO NUMBER HERE IS QUOTABLE (R213 B / R215 B). Every assertion is about which
# ids a run can be handed.
# --------------------------------------------------------------------------

SHIPPED_OATH = "kurages_oath"
PROTO_OATH = "proto_kurages_oath_memory"


def _drop_pool_caches():
    """Both memoized views of "what can be offered". The flag is read at pool
    ASSEMBLY, so a monkeypatched flag over a warm cache tests nothing."""
    loader.reset_caches()
    rewards.character_pool.cache_clear()


@pytest.fixture
def cold_pools():
    """Pools rebuilt on the way in and dropped again on the way out, so a
    flag-off test after a flag-on one is never reading the flagged cache."""
    _drop_pool_caches()
    yield
    _drop_pool_caches()


@pytest.fixture
def offer_pool(base_kit, cold_pools):
    """The base kit, with cold pools. Order matters: `base_kit` sets the
    flags, `cold_pools` then drops anything assembled without them."""


def offered_ids(character="kokomi", seeds=range(40)):
    """Every id the run layer can put in front of `character`, across the
    surfaces that roll: the assembled pool itself, the post-fight reward
    screen and the shop. The event card screens and the tier 0.5 drafter read
    `rewards.character_pool` and nothing else, so the pool half of this set is
    exactly what they can reach."""
    ids = {c.id for cs in rewards.character_pool(character).values()
           for c in cs}
    for seed in seeds:
        ids |= {c.id for c in rewards.roll_card_offers(
            random.Random(seed), character, C.REWARD_CARD_OFFERS)}
        ids |= {c.id for c in shop.shop_offer(random.Random(seed), character)}
    return ids


def test_flag_off_the_shipped_oath_is_the_only_oath_offered(cold_pools):
    """THE GOLDEN. No flag, no substitution: the pool is the printed one and
    the prototype id is unreachable from every offer surface."""
    ids = offered_ids()
    assert SHIPPED_OATH in ids
    assert PROTO_OATH not in ids
    assert loader.pool_substitutions("kokomi") == {}


def test_flag_on_the_shipped_oath_is_never_offered(offer_pool):
    """The defect itself: with the flag on, a run must not be able to draft
    the 5."""
    assert SHIPPED_OATH not in offered_ids()


def test_flag_on_the_staged_oath_is_offered_in_its_place(offer_pool):
    assert PROTO_OATH in offered_ids()
    assert loader.pool_substitutions("kokomi") == {SHIPPED_OATH: PROTO_OATH}


def test_the_swap_keeps_the_rarity_slot_and_the_slot_count(offer_pool):
    """SAME SLOT, SAME WEIGHT. The prototype is filed where the shipped row
    was and every rarity tier keeps the size it had, so the odds a Kokomi run
    is offered any given tier are the odds it always had. The symmetric
    difference pins that the swap moved TWO ids and no others."""
    flagged = rewards.character_pool("kokomi")
    shipped_rarity = loader.peek_card(SHIPPED_OATH).rarity
    assert PROTO_OATH in {c.id for c in flagged[shipped_rarity]}
    flagged_sizes = {r: len(cs) for r, cs in flagged.items()}
    flagged_slot = {c.id for c in flagged[shipped_rarity]}
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(C, "KURAGE_MEMORY", False)
        _drop_pool_caches()
        plain = rewards.character_pool("kokomi")
        plain_sizes = {r: len(cs) for r, cs in plain.items()}
        plain_slot = {c.id for c in plain[shipped_rarity]}
    assert flagged_sizes == plain_sizes
    assert flagged_slot ^ plain_slot == {SHIPPED_OATH, PROTO_OATH}


def test_the_offered_prototype_is_a_real_card_that_applies_three(offer_pool):
    """Resolvable BY ID, which is the structural requirement: every offer
    surface re-reads its pick through `loader.get_card(pick.id)` and the run
    layer stores decks as id strings and re-derives them every screen."""
    card = loader.get_card(PROTO_OATH)
    assert card.name == "Kurage's Oath"
    st = kokomi_state()
    effects.resolve_card(st, card)
    assert st.player.powers["kurage_ward"] == 3


def test_the_quarantine_still_holds_for_the_shipped_index(offer_pool):
    """R213 unweakened: the prototype is reachable through the substitution
    table and nowhere else. `_card_index` is what the digests, the codegen,
    the balance reports and the version stamps read."""
    assert PROTO_OATH not in loader._card_index()
    assert PROTO_OATH in loader._substituted_card_index()


def test_no_upgraded_shipped_oath_can_be_offered(offer_pool):
    """The 7 is the 5's upgrade and the same defect one step on. Offers are
    base rows by construction; this pins that the flagged pool holds no
    upgraded id at all, so the check cannot rot into a claim about one name."""
    ids = offered_ids()
    assert SHIPPED_OATH + "+" not in ids
    assert not [i for i in ids if i.endswith("+")]


# -- EB-213: the substituted Oath can be smithed, and to the ruled number ----
#
# [USER]'s placeholder is "3 block per memory played, upgrade to 5". The 5 was
# a note on the row and nothing else: the prototype surface had NO upgrade
# channel, so `has_upgrade` was False for every substituted row and the
# campfire skipped it. The row now carries `upgrade: {kurage_ward: +2}` -- the
# arithmetic between his two endpoints, and the same delta the shipped Oath
# already carries (R130) -- and the shipped upgrade path reads it from there.

def test_the_substituted_oath_can_be_upgraded(offer_pool):
    assert upgrades.has_upgrade(PROTO_OATH)


def test_the_substituted_oaths_upgrade_is_the_ruled_five(offer_pool):
    """The whole of `EB-213`'s acceptance on the sim side. Not a balance
    claim: nothing on this surface is quotable (R213 B / R215 B), and the
    assertion is that the campfire reaches the number [USER] ruled."""
    base = loader.get_card(PROTO_OATH)
    up = loader.get_card(PROTO_OATH + upgrades.SUFFIX)
    assert base.effects[0]["amount"] == C.KURAGE_MEMORY_PULSE_BLOCK - 2
    assert up.effects[0]["amount"] == C.KURAGE_MEMORY_PULSE_BLOCK


def test_the_upgraded_ward_is_what_a_memory_play_actually_pays(base_kit):
    """The number reaches the ENGINE, not just the sheet: a card is a face
    until the ward it applies is the ward the memory play pays."""
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    effects.resolve_card(st, loader.get_card(PROTO_OATH + upgrades.SUFFIX))
    assert st.player.powers["kurage_ward"] == 5
    st.kurage_queue.append(memory_entry(price=0))
    st.player.block = 0
    assert effects.kurage_fire(st) is True
    assert st.player.block == 5


def test_the_swap_is_hers_alone(offer_pool):
    """A substitution keyed to a constant must not reach another roster."""
    for other in ("klee", "furina"):
        assert loader.pool_substitutions(other) == {}
        assert PROTO_OATH not in offered_ids(other)


# -- the mutations: each names a way the seam could have been written wrong --

def test_mutation_a_substitution_that_moved_a_rarity_is_refused(offer_pool,
                                                                monkeypatch):
    """A face swap must not become a tier promotion, which would move the
    odds the card is offered at -- a balance change smuggled in as a
    quarantine."""
    real = loader.peek_card

    def wrong_rarity(card_id):
        card = real(card_id)
        if card_id == PROTO_OATH:
            card = copy.deepcopy(card)
            card.rarity = "rare"
        return card

    monkeypatch.setattr(loader, "peek_card", wrong_rarity)
    rewards.character_pool.cache_clear()
    with pytest.raises(ValueError, match="between rarity tiers"):
        rewards.character_pool("kokomi")


def test_mutation_a_substitution_pointing_at_a_deleted_row_is_refused(
        offer_pool, monkeypatch):
    """The R213 deletion rule takes rows OFF the surface. A constant left
    pointing at one must say so at load, not as a KeyError on someone's
    reward screen."""
    monkeypatch.setattr(C, "KURAGE_MEMORY_POOL_ADD", "proto_not_on_the_sheet")
    _drop_pool_caches()
    with pytest.raises(ValueError, match="not on prototype-surface.yaml"):
        loader._substituted_card_index()


def test_mutation_the_flag_alone_gates_the_second_index(cold_pools):
    """With the flag off there is no substitution table at all -- not an
    empty filter over one, no table."""
    assert loader._substituted_card_index() == {}


# --------------------------------------------------------------------------
# THE SMOKE: five whole starter-deck fights, no numbers claimed
# --------------------------------------------------------------------------

def test_five_starter_fights_run_to_completion_under_the_base_kit(base_kit):
    """NO NUMBER IS ASSERTED and none may be quoted. sec.12 reports the
    SHAPE this same run produced; the pilot does not value the memory, so
    this exercises the rule and never the decision."""
    for seed in (1, 2, 3, 4, 5):
        st = fight(seed=seed)
        assert st.over or not st.living_enemies or not st.player.alive
        assert not [e for e in st.log if e["event"] == "UNIMPLEMENTED"]
