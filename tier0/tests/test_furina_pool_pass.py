"""FURINA POOL PASS ONE (`EB-493`) -- the four arm-only Commons, both sides of
the flag.

The design is `review/active/furina-pool-pass-2026-09-05.md` sec.2, four FOLLOWS
off the doctrine read (`review/records/card-audit-2026-09-04.md` sec.5.5).
Rounds 9 and 10 read the Salon as furniture -- one Deploy in the whole deck,
most Companion plays printing "No member on stage: performs nobody", and no
card of Furina's own that asks a member to act -- and each row answers one
reading:

    Curtain Rises   a second Deploy SHAPE: a deploy on an Attack
    Second Course   a second performance, priced in Encore
    Rolling Tide    the kit's own perform verb on a card she can draft
    Guest List      a Companion generator in the offer pool, without Exhaust

WHAT THIS FILE IS AND IS NOT, and it is `test_furina_reframe_slice2.py`'s note
one pass later. `C# FIRST, sim at Balance`
(`docs/current/operations/prototype.md`) is the standing rule, so the rows'
behaviour in front of a player is graded in the mod and pinned in
`klee-mod/KleeTests/Prototype/FurinaPoolPassTests.cs`. What is here is the half
this engine owns anyway: the ONE new argument the pass needed
(`salon_perform`'s `member:`), the four rows' resolution through the ops both
engines share, and the seam that offers them.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype row's numbers are
seeds, and every assertion below is about a shape.
"""

import random
import re
from pathlib import Path

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, furina_reframe
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy
from tier05 import rewards

FR = furina_reframe

REPO = Path(__file__).resolve().parents[2]

#: The pass, in sheet order, against the shipped Common each replaces. Named
#: once so a row deleted under R213 B's deletion rule takes its pins with it
#: rather than leaving a green file asserting things about nothing.
PASS_ROWS = {
    "proto_fr_curtain_rises": "house_call",
    "proto_fr_second_course": "dinner_service",
    "proto_fr_rolling_tide": "undercurrent",
    "proto_fr_guest_list": "blocking_notes",
}


def furina_state(enemies=None, seed=0):
    p = loader.build_player("furina")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def _staged(members, encore=9, fanfare=0, seed=0, enemies=None):
    st = furina_state(enemies=enemies, seed=seed)
    p = st.player
    p.salon = list(members)
    p.powers["salon_member"] = len(p.salon)
    p.encore = encore
    p.fanfare = fanfare
    return st


def _events(state, name):
    return [ev for ev in state.log if ev["event"] == name]


def _tick_members(state):
    return [ev["member"] for ev in _events(state, "salon_tick")]


def _card(**kw):
    d = dict(id="furina_pool_pass_test", name="t", cost=0, type="skill",
             character="furina")
    d.update(kw)
    return Card(**d)


@pytest.fixture
def arm(monkeypatch):
    """The whole arm, and the id caches cleared on the way in and out -- a
    `proto_fr_` id only resolves under the master flag, and `loader` memoizes
    the index that answers."""
    loader.reset_caches()
    rewards.character_pool.cache_clear()
    for flag in ("FURINA_REFRAME", "FURINA_REFRAME_MANUAL",
                 "FURINA_REFRAME_EVOKE", "FURINA_REFRAME_METER"):
        monkeypatch.setattr(FR, flag, True)
    yield
    loader.reset_caches()
    rewards.character_pool.cache_clear()


@pytest.fixture
def manual(monkeypatch):
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)
    monkeypatch.setattr(FR, "FURINA_REFRAME_MANUAL", True)


@pytest.fixture
def meter(monkeypatch):
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)
    monkeypatch.setattr(FR, "FURINA_REFRAME_METER", True)


# ======================================================================
# 0. THE ROWS, AND THE SEAM THAT OFFERS THEM
# ======================================================================

def test_the_four_rows_are_on_the_surface_and_name_their_shipped_row():
    rows = {c.id: c for c in loader.prototype_cards()}
    for proto, shipped in PASS_ROWS.items():
        assert proto in rows, f"{proto} left the surface without its pins"
        assert rows[proto].replaces == shipped
        assert rows[proto].character == "furina"


def test_every_swap_is_common_for_common():
    """A substitution is a face swap. Moving a card between tiers moves the
    odds it is offered at, which is a balance change smuggled in as a
    quarantine -- `rewards.character_pool` raises on one, and this is the read
    from the sheet side."""
    rows = {c.id: c for c in loader.prototype_cards()}
    for proto, shipped in PASS_ROWS.items():
        assert rows[proto].rarity == "common"
        assert loader.peek_card(shipped).rarity == "common"


def test_the_map_carries_all_four(arm):
    assert loader.pool_substitutions("furina") == dict(FR.POOL_SUBS)
    for proto, shipped in PASS_ROWS.items():
        assert FR.POOL_SUBS[shipped] == proto


def test_the_arm_off_offers_the_shipped_commons_and_no_prototype():
    """The acceptance condition on the flag, for this pass's own four."""
    loader.reset_caches()
    rewards.character_pool.cache_clear()
    ids = {c.id for cards in rewards.character_pool("furina").values()
           for c in cards}
    for proto, shipped in PASS_ROWS.items():
        assert shipped in ids
        assert proto not in ids


def test_the_arm_on_offers_the_four_and_not_the_shipped_commons(arm):
    ids = {c.id for cards in rewards.character_pool("furina").values()
           for c in cards}
    for proto, shipped in PASS_ROWS.items():
        assert proto in ids
        assert shipped not in ids


# ======================================================================
# 1. THE ONE NEW ARGUMENT -- `salon_perform`'s `member:`
#
# An ARGUMENT on the shipped verb and not a second op, for the reason the
# aimed Evoke is: `tools/lint_op_parity.py` compares the KEY SET of
# `effects.OPS` against the drafter's priced-op table, so a synonym would have
# bought a `DRAFTER_VERSION` stamp for a verb both engines already have.
# ======================================================================

def test_the_pass_registered_no_new_op():
    assert "salon_perform" in effects.OPS
    assert "salon_perform_member" not in effects.OPS
    assert "salon_perform_named" not in effects.OPS


def _perform(member=None, amount=1):
    fx = {"op": "salon_perform"}
    if amount != 1:
        fx["amount"] = amount
    if member is not None:
        fx["member"] = member
    return _card(effects=[fx])


def test_an_unaimed_perform_still_takes_the_front(manual):
    st = _staged(["usher", "crabaletta"], encore=9)

    effects.resolve_card(st, _perform())

    assert _tick_members(st) == ["usher"]


def test_an_aimed_perform_takes_the_member_it_names(manual):
    """The whole reason the argument exists: a deploy APPENDS, so the member a
    card just named is at the BACK and the front is somebody else."""
    st = _staged(["usher", "crabaletta"], encore=9)

    effects.resolve_card(st, _perform("crabaletta"))

    assert _tick_members(st) == ["crabaletta"]
    assert st.player.salon == ["usher", "crabaletta"]     # nobody moved


def test_an_aim_at_a_member_who_is_not_on_stage_takes_the_front_and_says_so(
        manual):
    """The slot-6 ruling's fallback for the aimed Evoke, applied to the aimed
    performance: an aimed card that cannot find its member is an unaimed one,
    never a wasted one -- and D4 says the fact is emitted rather than silent,
    because the aim leaves no trace in the state afterwards."""
    st = _staged(["usher"], encore=9)

    effects.resolve_card(st, _perform("chevalmarin"))

    assert _tick_members(st) == ["usher"]
    assert [ev["member"] for ev
            in _events(st, "salon_perform_target_absent")] == ["chevalmarin"]


def test_an_aimed_perform_on_an_empty_stage_whiffs_like_an_unaimed_one(manual):
    st = _staged([], encore=9)

    effects.resolve_card(st, _perform("crabaletta"))

    assert len(_events(st, "salon_perform_whiffed")) == 1
    assert _events(st, "salon_perform_target_absent") == []
    assert _tick_members(st) == []


def test_a_typo_in_the_aim_is_a_load_error_and_not_a_front_performance(manual):
    """`_op_salon_bow`'s reason one verb over: a name that quietly degraded
    into "the front member" is the one failure an aimed verb could hide for a
    whole sprint."""
    st = _staged(["usher"], encore=9)

    with pytest.raises(ValueError, match="unknown salon member"):
        effects.resolve_card(st, _perform("paimon"))


def test_the_aim_is_inert_on_a_stage_the_arm_never_touched():
    """With every flag off the op is the shipped op: it performs whoever is at
    the front, exactly as `change_the_bill` has always made it."""
    st = _staged(["usher", "crabaletta"], encore=9)

    effects.resolve_card(st, _perform("crabaletta"))

    # The AIM still lands -- it is the field, not the flag, that decides who
    # performs -- but nothing else about the op moved: no reframe mint, no
    # rotation, no bow. (The Fanfare that does move here is the SHIPPED
    # meter's Encore-spent leg, which the arm's sec.4.1 retires and this build
    # still runs.)
    assert _tick_members(st) == ["crabaletta"]
    assert st.player.salon == ["usher", "crabaletta"]
    assert _events(st, "salon_evoke") == []
    assert [ev for ev in _events(st, "gain_fanfare")
            if ev["source"] == "salon_performance"] == []


# ======================================================================
# 2. CURTAIN RISES -- a deploy on an ATTACK
# ======================================================================

def test_curtain_rises_hits_and_then_deploys(arm):
    st = _staged([], encore=9)
    hp = st.enemies[0].hp
    printed = C.SALON_MEMBERS["usher"]["tick"]["block"]

    effects.resolve_card(st, loader.get_card("proto_fr_curtain_rises"))

    assert st.player.salon == ["usher"]
    # The hit landed AND the usher performed as he arrived: 6 damage, then his
    # Block. The two are separable because only one of them is Block.
    assert st.enemies[0].hp == hp - 6
    assert st.player.block == printed
    assert _tick_members(st) == ["usher"]


def test_curtain_rises_deploys_without_performing_with_the_manual_leg_off(
        monkeypatch):
    """The deploy-performs clause is the MANUAL leg's, so the row is a plain
    deploy without it -- the acceptance condition on the leg, read through a
    row rather than through a synthetic card."""
    loader.reset_caches()
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)
    st = _staged([], encore=9)

    effects.resolve_card(st, loader.get_card("proto_fr_curtain_rises"))

    assert st.player.salon == ["usher"]
    assert st.player.block == 0
    assert _tick_members(st) == []
    loader.reset_caches()


def test_curtain_rises_upgrades_its_damage_and_not_its_deploy(arm):
    st = _staged([], encore=9)
    hp = st.enemies[0].hp

    effects.resolve_card(st, loader.get_card("proto_fr_curtain_rises+"))

    assert st.enemies[0].hp == hp - 9
    assert st.player.salon == ["usher"]


# ======================================================================
# 3. SECOND COURSE -- a second performance, priced in Encore
# ======================================================================

def test_second_course_is_unplayable_below_its_encore_price(arm):
    """The packet's own sentence: "Unplayable below 3 Encore." That is the
    `encore_cost` GATE (`combat.card_playable`) and never the `spend_encore`
    OP, which is the overdraw primitive and would let the card be played at 0
    Encore for 3 HP."""
    card = loader.get_card("proto_fr_second_course")
    assert card.encore_cost == 3

    st = _staged([], encore=2)
    st.player.energy = 3            # the Energy gate is a separate line
    assert not combat.card_playable(st, card)

    st.player.encore = 3
    assert combat.card_playable(st, card)


def test_the_upgrade_cuts_the_price_by_one(arm):
    st = _staged([], encore=2)
    st.player.energy = 3
    up = loader.get_card("proto_fr_second_course+")

    assert up.encore_cost == 2
    assert combat.card_playable(st, up)


def test_second_course_deploys_crabaletta_and_she_performs_twice(arm):
    """One performance as she arrives (the deploy-performs clause) and one
    more that the Encore buys."""
    st = _staged([], encore=9)
    hp = st.enemies[0].hp
    printed = C.SALON_MEMBERS["crabaletta"]["tick"]["damage"]

    effects.resolve_card(st, loader.get_card("proto_fr_second_course"))

    assert st.player.salon == ["crabaletta"]
    assert _tick_members(st) == ["crabaletta", "crabaletta"]
    assert st.enemies[0].hp == hp - 2 * printed
    # Two performances, two trigger mints, and the mint is the ONE site inside
    # `salon_member_act` rather than a second one on the card.
    assert st.player.fanfare == 2 * FR.FANFARE_PER_TRIGGER


def test_the_extra_performance_is_crabalettas_even_off_a_full_stage(arm):
    """The deploy onto a full stage Evokes the FRONT, so the member the card
    named is at the back and the front is somebody else. The promise is about
    Crabaletta, which is what the aim buys."""
    st = _staged(["usher", "chevalmarin", "usher"], encore=9)

    effects.resolve_card(st, loader.get_card("proto_fr_second_course"))

    assert len(_events(st, "salon_evoke")) == 1            # the front usher
    assert st.player.salon == ["chevalmarin", "usher", "crabaletta"]
    assert _tick_members(st) == ["crabaletta", "crabaletta"]


# ======================================================================
# 4. ROLLING TIDE -- the kit's own perform verb
# ======================================================================

def test_rolling_tide_hits_all_enemies_twice_and_performs_the_front(arm):
    enemies = [make_enemy(hp=40), make_enemy(hp=40)]
    st = _staged(["usher", "crabaletta"], encore=9, enemies=enemies)

    effects.resolve_card(st, loader.get_card("proto_fr_rolling_tide"))

    for e in st.enemies:
        assert e.hp == 40 - 4                              # 2 damage, twice
    assert _tick_members(st) == ["usher"]
    assert st.player.salon == ["usher", "crabaletta"]      # a perform, not a
                                                           # bow or a rotation


def test_rolling_tide_performs_nobody_on_an_empty_stage_and_says_so(arm):
    """The losing line the packet names: with an empty stage this is a worse
    Undercurrent. `salon_perform_whiffed` is what a display reads to print
    EB-477's "No member on stage: performs nobody"."""
    enemies = [make_enemy(hp=40)]
    st = _staged([], encore=9, enemies=enemies)

    effects.resolve_card(st, loader.get_card("proto_fr_rolling_tide"))

    assert st.enemies[0].hp == 40 - 4                      # the hit still lands
    assert len(_events(st, "salon_perform_whiffed")) == 1
    assert _tick_members(st) == []


def test_rolling_tide_upgrades_every_hit(arm):
    enemies = [make_enemy(hp=40)]
    st = _staged([], encore=9, enemies=enemies)

    effects.resolve_card(st, loader.get_card("proto_fr_rolling_tide+"))

    assert st.enemies[0].hp == 40 - 6                      # 3 damage, twice


# ======================================================================
# 5. GUEST LIST -- a generator in the pool, and no Exhaust
# ======================================================================

def test_guest_list_blocks_and_adds_a_common_companion(arm):
    st = _staged([], encore=9)

    effects.resolve_card(st, loader.get_card("proto_fr_guest_list"))

    assert st.player.block == 3
    assert len(st.player.hand) == 1
    made = st.player.hand[0]
    assert made.rarity == "common"
    assert made.is_companion or made.guest_star
    assert made.generated_by_guest_star


def test_guest_list_does_not_exhaust_and_the_shipped_generator_does(arm):
    """THE ONE GUARDRAIL THIS ROW MOVES, and it is the only one of the four
    that is a balance rule rather than a structural fact. This-combat-only,
    equal-rarity and the companion-plus-Guest-Star pool are all properties of
    the code; "generators Exhaust" is a sheet field, and the pass buys An
    Invitation's verb back at a price of an Energy and no Exhaust."""
    assert not loader.get_card("proto_fr_guest_list").exhaust
    assert loader.get_card("an_invitation").exhaust

    st = _staged([], encore=9)
    st.player.energy = 3
    card = loader.get_card("proto_fr_guest_list")
    st.player.hand = [card]

    combat.play_card(st, card)

    assert card in st.player.discard_pile
    assert card not in st.player.exhaust_pile


def test_guest_list_upgrades_its_block_and_not_its_generation(arm):
    st = _staged([], encore=9)

    effects.resolve_card(st, loader.get_card("proto_fr_guest_list+"))

    assert st.player.block == 5
    assert len(st.player.hand) == 1


# ======================================================================
# 6. THE TWO ENGINES' MAPS ARE ONE MAP
#
# `EB-491`'s LESSON, ONE ARM OVER. R252 added four rows to the sheet, to the
# ops, to the powers, to the codegen and to both engines' tests, and every
# gate was green -- because nothing added them to the mod's OFFER roster, and
# that roster's only pin was a COUNT. The rows shipped unofferable: a live
# seat played eight fights and was offered none of them while the sim offered
# all four the whole time. `tools/lint_arm_pool_parity.py` closed it for the
# arms whose roster is a `Slice()`; this arm's is a one-for-one SWAP, so the
# same claim is made here, against the map both engines answer to.
#
# READ OFF THE SOURCE, not off a build, for that lint's reason verbatim: the
# swap resolves every row through `ModelDb.Card<T>()`, which throws until the
# game boots. The ids come from the `Sheet entry: id=` header every generated
# file carries, which is the same seam `tools/lint_ancient_coverage.py` reads
# and what makes a RENAME visible -- a renamed row regenerates its file with
# the new id and the old type argument stops resolving.
# ======================================================================

SWAP_METHOD = REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype" / \
    "FurinaReframe.cs"


def _class_to_id():
    """`{generated class name: sheet id}` over both generated trees."""
    out = {}
    for tree in (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
                 / "Generated",
                 REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina"
                 / "Generated"):
        for path in tree.glob("*.cs"):
            hit = re.search(r"Sheet entry: id=(\S+)",
                            path.read_text(encoding="utf-8"))
            if hit:
                out[path.stem] = hit.group(1)
    return out


def _swap_body():
    src = SWAP_METHOD.read_text(encoding="utf-8")
    start = src.index("public static IEnumerable<CardModel> SwapOfferedRiders")
    end = src.index("\n    }", start)
    return src[start:end]


def test_the_mod_swaps_exactly_the_rows_the_sim_swaps():
    """BOTH DIRECTIONS. The shipped ids the C# method filters OUT are exactly
    `POOL_SUBS`' keys, and the prototype ids it concats IN are exactly its
    values -- so neither engine can carry a substitution the other does not
    make, which is the failure that cost `EB-491` a whole seat round."""
    names = _class_to_id()
    body = _swap_body()
    named = {names[cls] for cls in names
             if re.search(rf"\b(?:FurinaGen\.)?{re.escape(cls)}\b", body)}

    assert named == set(FR.POOL_SUBS) | set(FR.POOL_SUBS.values())
