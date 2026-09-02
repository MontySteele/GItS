"""The INAZUMA half of the companion overhaul -- twenty-four rows, one flag.

Source: the approved workshop `companion-workshop-inazuma-2026-09-01.md`
(approved 2026-09-01 at its four default picks, its sec.9; a Paper artefact on
another branch and not in this tree). Its sec.2 nation shape is "Inazuma reads
the HP bar" and eight of the rows do; its sec.1 pricing rule is what makes the
nine Commons beat a Strike.

THE FIRST SECTION IS STILL THE ONE THAT MATTERS. `C.COMPANION_OVERHAUL` ships
OFF, and this arm widens two things every shipped run walks -- the tail of
`deal_damage_to_enemy` and the card-play loop -- so "flag off changes nothing"
is pinned here rather than intended, exactly as the Mondstadt waves pin theirs.

ONE FLAG FOR BOTH NATIONS. There is no `INAZUMA_OVERHAUL` property: the arm
means "the companion pool is the approved workshops' pool", and a second
property would let a build offer one nation's rewrites beside the other
nation's shipped rows -- a state no document describes.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). These are
shape assertions about an engine, not numbers about a game.
"""

import re
from pathlib import Path

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards

REPO = Path(__file__).resolve().parents[2]

#: The fifteen rows the workshop retires from the offerable pool. Read off the
#: shipped sheet rather than listed, so the day a sixteenth Inazuma row ships
#: this test asks about it too.
SHIPPED_INAZUMA = tuple(sorted(
    c.id for c in loader._card_index().values()
    if c.is_companion and c.nation == "inazuma"))


def _caches_clear():
    loader._card_prototype.cache_clear()
    rewards._companion_roster.cache_clear()
    rewards.companion_pool.cache_clear()
    rewards.five_star_roster.cache_clear()
    rewards.designed_nations.cache_clear()


@pytest.fixture
def overhaul(monkeypatch):
    """The flag ON, with every id-resolving cache cleared going in and out."""
    _caches_clear()
    monkeypatch.setattr(C, "COMPANION_OVERHAUL", True)
    yield
    _caches_clear()


def _play(state, card_id):
    effects.resolve_card(state, loader.get_card(card_id))


def _attack(amount=6, element="pyro"):
    return Card(id="probe", name="Probe", cost=1, type="attack",
                element=element,
                effects=[{"op": "damage", "amount": amount, "target": "enemy",
                          "applies_element": True}])


# ---------------------------------------------------------------------------
# THE FLAG IS OFF, AND THAT IS THE ACCEPTANCE CONDITION
# ---------------------------------------------------------------------------

def test_the_flag_ships_off_and_owns_two_nations():
    assert C.COMPANION_OVERHAUL is False
    assert C.COMPANION_OVERHAUL_NATIONS == ("mondstadt", "inazuma")


def test_flag_off_every_shipped_inazuma_row_is_still_offerable():
    offerable = {c.id for cards in rewards.companion_pool().values()
                 for c in cards}
    assert set(SHIPPED_INAZUMA) <= offerable


def test_flag_off_the_two_new_hooks_are_no_ops():
    """Both sit on paths a shipped run walks every turn -- the tail of
    `deal_damage_to_enemy` and the card-play loop -- so this is a property of
    two shipped functions rather than of the arm."""
    st = make_state()
    st.player.powers["mi_crimson_ooyoroi"] = 2
    st.enemies[0].powers["mi_aurous_blaze"] = 2
    before = (dict(st.player.powers), st.player.block,
              [e.hp for e in st.enemies], st.mi_damage_dealt_this_card)

    effects.companion_overhaul_damage_dealt(st, st.enemies[0], 9, "card")
    effects.companion_overhaul_card_played(st, _attack())

    assert (dict(st.player.powers), st.player.block,
            [e.hp for e in st.enemies],
            st.mi_damage_dealt_this_card) == before


def test_flag_off_the_two_turn_blocks_are_no_ops():
    st = make_state()
    st.player.powers.update({
        "mi_juuga": 3, "mi_daruma": 2, "mi_sanctifying_ring": 3,
        "mi_sesshou_sakura": 3, "mi_soumetsu": 2, "mi_kyouka": 2,
        "mi_tamoto": 3, "mi_naptime": 2, "mi_stormcall": 1,
        "mi_surprise_dispatch": 1, "mi_war_banner": 2,
        "mi_blazing_barrier": 6, "mi_crowfeather": 4,
    })
    before = (dict(st.player.powers), st.player.block,
              [e.hp for e in st.enemies])
    effects.inazuma_overhaul_turn_start(st)
    effects.inazuma_overhaul_turn_end(st)
    assert (dict(st.player.powers), st.player.block,
            [e.hp for e in st.enemies]) == before


def test_flag_off_ignore_block_is_not_reachable_and_block_still_eats():
    """`ignore_block` defaults False, which is the whole of "every shipped
    caller is byte-identical"."""
    st = make_state(enemies=[make_enemy(hp=50)])
    st.enemies[0].block = 20
    effects.deal_damage_to_enemy(st, st.enemies[0], 8, source="companion")
    assert st.enemies[0].hp == 50
    assert st.enemies[0].block == 12


def test_flag_off_mend_still_refuses_to_resolve():
    """`mend` belongs to two arms and resolves under one. With the companion
    flag off it is still the KOKOMI arm's verb, still C# first, and still
    raises by name rather than healing something quietly."""
    st = make_state()
    row = Card(id="probe", name="p", cost=1, type="skill",
               effects=[{"op": "mend", "amount": 10}])
    with pytest.raises(NotImplementedError, match="KOKOMI_OVERHAUL"):
        effects.resolve_card(st, row)


# ---------------------------------------------------------------------------
# THE FLAG IS ON: THE POOL
# ---------------------------------------------------------------------------

def test_all_twenty_four_are_offerable_and_the_shipped_fifteen_are_not(overhaul):
    offerable = {c.id for cards in rewards.companion_pool().values()
                 for c in cards}
    assert set(C.INAZUMA_OVERHAUL_POOL_IDS) <= offerable
    assert not (set(SHIPPED_INAZUMA) & offerable)


def test_the_pool_ids_and_the_sheet_agree(overhaul):
    on_sheet = {c.id for c in loader.prototype_cards()
                if c.id.startswith("proto_mi_")}
    assert on_sheet == set(C.INAZUMA_OVERHAUL_POOL_IDS)
    assert len(C.INAZUMA_OVERHAUL_POOL_IDS) == 24


def test_the_rarity_split_is_the_workshops_enumeration(overhaul):
    """9 Common, 11 Uncommon, 4 Rare. The workshop's sec.4 prints "12 Uncommon"
    and counts Gorou's Kokomi-side PERSONAL among them; a Personal is not a
    Universal and is not built, so the Universals' own split is one short in
    that tier. Pinned so the discrepancy is a recorded fact rather than a
    miscount somebody re-derives later."""
    split = {}
    for cid in C.INAZUMA_OVERHAUL_POOL_IDS:
        card = loader.peek_card(cid)
        split[card.rarity] = split.get(card.rarity, 0) + 1
    assert split == {"common": 9, "uncommon": 11, "rare": 4}


def test_every_row_is_an_inazuma_universal(overhaul):
    for cid in C.INAZUMA_OVERHAUL_POOL_IDS:
        card = loader.peek_card(cid)
        assert card.is_companion, cid
        assert card.nation == C.INAZUMA_OVERHAUL_NATION, cid
        assert card.personal_pool is None, cid       # no Personal, no stand-in
        assert card.rarity in C.RARITY_ODDS, cid


def test_mondstadt_still_moves_too(overhaul):
    """One flag, two nations: turning the arm on must not have traded one
    replacement for the other."""
    offerable = {c.id for cards in rewards.companion_pool().values()
                 for c in cards}
    assert set(C.MONDSTADT_OVERHAUL_POOL_IDS) <= offerable


def test_the_banner_roster_moves_with_the_pool(overhaul):
    featured = {c.id for c in rewards.five_star_roster("inazuma")}
    assert featured
    assert all(i.startswith("proto_mi_") for i in featured)
    offerable = {c.id for cards in rewards.companion_pool().values()
                 for c in cards}
    assert featured <= offerable


def test_every_row_resolves_without_raising(overhaul):
    """The staging floor: a prototype that throws cannot be tried. Played
    against a two-enemy board with an aura up, then walked through both turn
    boundaries so the powers each row applies actually fire."""
    for cid in C.INAZUMA_OVERHAUL_POOL_IDS:
        st = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
        st.enemies[1].aura = "hydro"
        st.player.block = 9
        st.player.draw_pile = [Card(id=f"f{i}", name="f", cost=1,
                                    type="skill") for i in range(5)]
        _play(st, cid)
        effects.inazuma_overhaul_turn_end(st)
        effects.inazuma_overhaul_turn_start(st)


# ---------------------------------------------------------------------------
# THE ORDER IS LAW, AND IT IS THE ONE THE MOD WALKS
# ---------------------------------------------------------------------------

def test_the_end_of_turn_order_is_the_one_the_mod_walks():
    """Five of these put an element on an enemy that may already carry one and
    four draw from the rng, so a divergence here is a divergence in which
    reactions fire and in every later roll of the fight."""
    src = (REPO / "tier0" / "engine" / "effects.py").read_text(
        encoding="utf-8")
    body = src.split("def inazuma_overhaul_turn_end(")[1].split("\ndef ")[0]
    seen = list(dict.fromkeys(re.findall(r'"(mi_[a-z_]+)"', body)))
    assert seen == ["mi_juuga", "mi_daruma", "mi_sanctifying_ring",
                    "mi_sesshou_sakura", "mi_soumetsu", "mi_kyouka",
                    "mi_tamoto", "mi_crimson_ooyoroi", "mi_war_banner",
                    "mi_naptime", "mi_crowfeather"], seen


def test_the_start_of_turn_order_is_the_one_the_mod_walks():
    src = (REPO / "tier0" / "engine" / "effects.py").read_text(
        encoding="utf-8")
    body = src.split("def inazuma_overhaul_turn_start(")[1].split("\ndef ")[0]
    seen = list(dict.fromkeys(re.findall(r'"(mi_[a-z_]+)"', body)))
    assert seen == ["mi_blazing_barrier", "mi_naptime", "mi_stormcall",
                    "mi_surprise_dispatch"], seen


def test_the_element_override_order_puts_the_blanket_first():
    """Five riders can now claim the element and LAST WINS, so the sequence is
    blanket riders first and one-shots after -- with Varka's banked Swirl last
    of all, because its element is the one the board produced a moment ago."""
    src = (REPO / "tier0" / "engine" / "effects.py").read_text(
        encoding="utf-8")
    body = src.split("def companion_overhaul_card_start(")[1]
    body = body.split("\ndef ")[0]
    riders = [m for m in re.findall(r'"(m[ci]_[a-z_]+)"', body)
              if m in ("mc_lightning_fang", "mi_kyouka",
                       "mc_passion_overload", "mi_crowfeather",
                       "mc_swirl_charge")]
    assert list(dict.fromkeys(riders)) == [
        "mc_lightning_fang", "mi_kyouka", "mc_passion_overload",
        "mi_crowfeather", "mc_swirl_charge"]


# ---------------------------------------------------------------------------
# GOROU
# ---------------------------------------------------------------------------

def test_inuzaka_banks_half_of_what_it_actually_landed(overhaul):
    st = make_state(enemies=[make_enemy(hp=50)])
    _play(st, "proto_mi_gorou_inuzaka")
    assert st.enemies[0].hp == 42
    assert st.player.block == 4                       # 8 // 2


def test_inuzaka_reads_the_landed_number_and_not_the_printed_one(overhaul):
    """Strength moves the hit, so it moves the Block: the printed 8 is not the
    number the card banks, which is the whole reason the op exists."""
    st = make_state(enemies=[make_enemy(hp=50)])
    st.player.powers["strength"] = 4
    _play(st, "proto_mi_gorou_inuzaka")
    assert st.enemies[0].hp == 38
    assert st.player.block == 6                       # 12 // 2


def test_inuzaka_banks_nothing_off_a_hit_the_enemy_blocked(overhaul):
    """HP, not the swing: the conservative reading of "the damage dealt"."""
    st = make_state(enemies=[make_enemy(hp=50)])
    st.enemies[0].block = 30
    _play(st, "proto_mi_gorou_inuzaka")
    assert st.player.block == 0


def test_the_play_total_does_not_survive_the_card(overhaul):
    st = make_state(enemies=[make_enemy(hp=50)])
    _play(st, "proto_mi_gorou_inuzaka")
    _play(st, "proto_mi_gorou_inuzaka")
    # Two plays, two independent halves -- never 8 banked off a running total.
    assert st.player.block == 8


def test_the_war_banner_lends_real_dexterity_and_takes_it_back(overhaul):
    st = make_state()
    _play(st, "proto_mi_gorou_war_banner")
    assert st.player.powers["dexterity"] == 2
    assert st.player.powers["mi_war_banner"] == 2
    effects.inazuma_overhaul_turn_end(st)             # this turn
    assert st.player.powers["dexterity"] == 2
    effects.inazuma_overhaul_turn_end(st)             # and the next
    assert "dexterity" not in st.player.powers
    assert "mi_war_banner" not in st.player.powers


def test_the_war_banner_takes_back_only_its_own_two(overhaul):
    st = make_state()
    st.player.powers["dexterity"] = 5                 # somebody else's
    _play(st, "proto_mi_gorou_war_banner")
    effects.inazuma_overhaul_turn_end(st)
    effects.inazuma_overhaul_turn_end(st)
    assert st.player.powers["dexterity"] == 5


def test_juuga_fires_three_turns_and_stops(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    _play(st, "proto_mi_gorou_juuga")
    for _ in range(4):
        effects.inazuma_overhaul_turn_end(st)
    assert st.enemies[0].hp == 90 - 3 * C.MI_JUUGA_DMG
    assert "mi_juuga" not in st.player.powers


# ---------------------------------------------------------------------------
# SAYU -- THE NATION'S SHAPE, AND THE PROMISE THAT BREAKS
# ---------------------------------------------------------------------------

def test_the_daruma_attacks_high_and_guards_low(overhaul):
    st = make_state(hp=80, enemies=[make_enemy(hp=90)])
    _play(st, "proto_mi_sayu_daruma")
    effects.inazuma_overhaul_turn_end(st)
    assert st.enemies[0].hp == 90 - C.MI_DARUMA_DMG
    assert st.player.block == 0

    st = make_state(hp=80, enemies=[make_enemy(hp=90)])
    st.player.hp = 20
    _play(st, "proto_mi_sayu_daruma")
    effects.inazuma_overhaul_turn_end(st)
    assert st.enemies[0].hp == 90
    assert st.player.block == C.MI_DARUMA_BLOCK


def test_the_daruma_reads_the_bar_when_it_acts_not_when_summoned(overhaul):
    st = make_state(hp=80, enemies=[make_enemy(hp=90)])
    _play(st, "proto_mi_sayu_daruma")                 # summoned at full HP
    st.player.hp = 20                                 # and then the fight
    effects.inazuma_overhaul_turn_end(st)
    assert st.player.block == C.MI_DARUMA_BLOCK


def test_naptime_pays_on_a_turn_with_no_attack(overhaul):
    st = make_state()
    st.player.draw_pile = [Card(id=f"f{i}", name="f", cost=1, type="skill")
                           for i in range(5)]
    _play(st, "proto_mi_sayu_naptime")
    assert st.player.block == 4
    effects.inazuma_overhaul_turn_end(st)
    effects.inazuma_overhaul_turn_start(st)
    assert len(st.player.hand) == 2


def test_naptime_breaks_on_a_turn_with_one(overhaul):
    st = make_state()
    st.player.draw_pile = [Card(id=f"f{i}", name="f", cost=1, type="skill")
                           for i in range(5)]
    _play(st, "proto_mi_sayu_naptime")
    st.attacks_played_this_turn = 1                   # an Attack resolved
    effects.inazuma_overhaul_turn_end(st)
    effects.inazuma_overhaul_turn_start(st)
    assert st.player.hand == []
    assert "mi_naptime" not in st.player.powers


# ---------------------------------------------------------------------------
# KUKI SHINOBU -- THE HP PRICE AND THE HP READS
# ---------------------------------------------------------------------------

def test_the_sanctifying_ring_is_paid_in_plain_hp(overhaul):
    """"Lose 3 HP" is plain HP loss, and this engine spells that
    `{op: damage, target: self}` -- the shipped Hot Hands row's own line."""
    st = make_state(hp=80)
    st.player.block = 20
    _play(st, "proto_mi_shinobu_sanctifying_ring")
    assert st.player.hp == 77
    assert st.player.block == 20                      # Block does not pay it


def test_the_ring_sweeps_the_board_and_guards_for_three_turns(overhaul):
    st = make_state(enemies=[make_enemy(hp=60, name="a"),
                             make_enemy(hp=60, name="b")])
    _play(st, "proto_mi_shinobu_sanctifying_ring")
    effects.inazuma_overhaul_turn_end(st)
    assert [e.hp for e in st.enemies] == [55, 55]
    assert st.player.block == C.MI_SANCTIFYING_RING_BLOCK


def test_the_grass_ring_pays_double_after_the_ring_bites(overhaul):
    st = make_state(hp=80)
    _play(st, "proto_mi_shinobu_grass_ring")
    assert st.player.block == 4
    st = make_state(hp=80)
    st.hp_lost_this_turn = 3
    _play(st, "proto_mi_shinobu_grass_ring")
    assert st.player.block == 8


def test_thundergrust_hits_harder_under_half(overhaul):
    st = make_state(hp=80, enemies=[make_enemy(hp=60)])
    _play(st, "proto_mi_shinobu_thundergrust")
    assert st.enemies[0].hp == 52
    st = make_state(hp=80, enemies=[make_enemy(hp=60)])
    st.player.hp = 20
    _play(st, "proto_mi_shinobu_thundergrust")
    assert st.enemies[0].hp == 47


# ---------------------------------------------------------------------------
# THOMA
# ---------------------------------------------------------------------------

def test_the_barrier_thickens_when_its_own_block_is_eaten(overhaul):
    st = make_state()
    _play(st, "proto_mi_thoma_blazing_barrier")
    assert st.player.block == 6
    assert st.player.powers["mi_blazing_barrier"] == 6
    st.player.block -= 4
    effects.companion_overhaul_block_absorbed(st, st.enemies[0], 4, 6)
    assert st.player.block == 2 + C.MI_BLAZING_BARRIER_BLOCK
    assert st.player.powers["mi_blazing_barrier"] == 2


def test_the_barrier_stops_once_its_mark_is_gone(overhaul):
    st = make_state()
    st.player.block = 6
    st.player.powers["mi_blazing_barrier"] = 6
    effects.companion_overhaul_block_absorbed(st, st.enemies[0], 6, 6)
    assert "mi_blazing_barrier" not in st.player.powers
    st.player.block = 9
    effects.companion_overhaul_block_absorbed(st, st.enemies[0], 3, 9)
    assert st.player.block == 9                       # nothing more


def test_ooyoroi_answers_every_attack_and_only_attacks(overhaul):
    st = make_state(enemies=[make_enemy(hp=60)])
    _play(st, "proto_mi_thoma_crimson_ooyoroi")
    effects.companion_overhaul_card_played(st, _attack())
    assert st.enemies[0].hp == 60 - C.MI_OOYOROI_DMG
    assert st.player.block == C.MI_OOYOROI_BLOCK
    skill = Card(id="s", name="s", cost=1, type="skill", effects=[])
    effects.companion_overhaul_card_played(st, skill)
    assert st.player.block == C.MI_OOYOROI_BLOCK      # unmoved


def test_ooyoroi_runs_out_after_two_turns(overhaul):
    st = make_state(enemies=[make_enemy(hp=60)])
    _play(st, "proto_mi_thoma_crimson_ooyoroi")
    effects.inazuma_overhaul_turn_end(st)
    effects.inazuma_overhaul_turn_end(st)
    assert "mi_crimson_ooyoroi" not in st.player.powers
    effects.companion_overhaul_card_played(st, _attack())
    assert st.player.block == 0


# ---------------------------------------------------------------------------
# KUJOU SARA
# ---------------------------------------------------------------------------

def test_crowfeather_pays_four_and_makes_the_attack_electro(overhaul):
    st = make_state(enemies=[make_enemy(hp=60)])
    _play(st, "proto_mi_sara_crowfeather_cover")
    assert st.player.powers["mi_crowfeather"] == 4
    effects.resolve_card(st, _attack())
    assert st.enemies[0].hp == 50                     # 6 + 4
    assert st.enemies[0].aura == "electro"
    assert "mi_crowfeather" not in st.player.powers


def test_crowfeather_expires_with_the_turn_whether_or_not_it_paid(overhaul):
    st = make_state()
    _play(st, "proto_mi_sara_crowfeather_cover")
    effects.inazuma_overhaul_turn_end(st)
    assert "mi_crowfeather" not in st.player.powers


def test_stormcall_pays_next_turn_and_only_next_turn(overhaul):
    st = make_state(enemies=[make_enemy(hp=60)])
    _play(st, "proto_mi_sara_tengu_stormcall")
    assert st.enemies[0].hp == 55
    # An ELECTRO probe, so it refreshes the aura the card left rather than
    # reacting off it -- the rider is what is under test, not the reaction.
    effects.resolve_card(st, _attack(element="electro"))
    assert st.enemies[0].hp == 49                     # same turn: no rider
    effects.inazuma_overhaul_turn_start(st)
    assert st.player.powers["attack_up_this_turn"] == C.MI_STORMCALL_BONUS
    effects.resolve_card(st, _attack(element="electro"))
    assert st.enemies[0].hp == 38                     # 6 + 5


# ---------------------------------------------------------------------------
# ITTO AND RAIDEN
# ---------------------------------------------------------------------------

def test_superlative_superstrength_is_both_halves_whole(overhaul):
    st = make_state(enemies=[make_enemy(hp=60)])
    _play(st, "proto_mi_itto_superlative_superstrength")
    assert st.enemies[0].hp == 46
    assert st.player.block == 12
    assert st.enemies[0].aura == "geo" or st.enemies[0].aura is None


def test_musou_reads_the_companions_you_played(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    _play(st, "proto_mi_raiden_musou_no_hitotachi")
    assert st.enemies[0].hp == 70
    st = make_state(enemies=[make_enemy(hp=90)])
    st.companions_played = ["a", "b", "c"]
    _play(st, "proto_mi_raiden_musou_no_hitotachi")
    assert st.enemies[0].hp == 90 - (20 + 15)


# ---------------------------------------------------------------------------
# THE NEW NINE
# ---------------------------------------------------------------------------

def test_kazuha_hits_the_board_and_swirls_each_aura(overhaul):
    """"Swirl each" is the ANEMO the Attack applies to each body, not a second
    op: a `swirl` op after the damage would re-apply Anemo to a body the hit
    has already cleared. The proof is the SPREAD -- this engine's Swirl copies
    the consumed aura onto every living enemy -- so one hydro on the board
    becomes hydro on all three."""
    st = make_state(enemies=[make_enemy(hp=60, name="a"),
                             make_enemy(hp=60, name="b"),
                             make_enemy(hp=60, name="c")])
    st.enemies[0].aura = "hydro"
    _play(st, "proto_mi_kazuha_slash")
    assert [e.hp for e in st.enemies] == [50, 50, 50]
    assert [e.aura for e in st.enemies] == ["hydro", "hydro", "hydro"]


def test_the_sakura_level_up_by_placement_and_cap_at_three(overhaul):
    st = make_state(enemies=[make_enemy(hp=200)])
    _play(st, "proto_mi_yae_sesshou_sakura")
    effects.inazuma_overhaul_turn_end(st)
    assert st.enemies[0].hp == 200 - C.MI_SAKURA_DMG
    st = make_state(enemies=[make_enemy(hp=200)])
    for _ in range(4):
        _play(st, "proto_mi_yae_sesshou_sakura")
    effects.inazuma_overhaul_turn_end(st)
    # Three fire: 4, 7, 7. The fourth is placed and never pays.
    assert st.enemies[0].hp == 200 - (C.MI_SAKURA_DMG
                                      + 2 * (C.MI_SAKURA_DMG
                                             + C.MI_SAKURA_BONUS))


def test_the_sakura_swing_with_your_strength(overhaul):
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.powers["strength"] = 3
    _play(st, "proto_mi_yae_sesshou_sakura")
    effects.inazuma_overhaul_turn_end(st)
    assert st.enemies[0].hp == 200 - (C.MI_SAKURA_DMG + 3)


def test_aurous_blaze_detonates_on_a_skill_and_not_on_an_attack(overhaul):
    st = make_state(enemies=[make_enemy(hp=90, name="a"),
                             make_enemy(hp=90, name="b")])
    _play(st, "proto_mi_yoimiya_aurous_blaze")
    assert st.enemies[0].powers["mi_aurous_blaze"] == 2

    # A Skill's damage line on the marked body: the blast answers.
    skill = Card(id="s", name="s", cost=1, type="skill",
                 effects=[{"op": "damage", "amount": 5, "target": "enemy"}])
    effects.resolve_card(st, skill)
    assert st.enemies[0].hp == 90 - 5 - C.MI_AUROUS_BLAZE_DMG
    assert st.enemies[1].hp == 90 - C.MI_AUROUS_BLAZE_DMG


def test_aurous_blaze_ignores_an_attack(overhaul):
    st = make_state(enemies=[make_enemy(hp=90, name="a"),
                             make_enemy(hp=90, name="b")])
    _play(st, "proto_mi_yoimiya_aurous_blaze")
    effects.resolve_card(st, _attack(amount=5, element="geo"))
    assert st.enemies[1].hp == 90                     # no blast


def test_soumetsu_sweeps_twice_then_ends_on_the_big_one(overhaul):
    st = make_state(enemies=[make_enemy(hp=200, name="a"),
                             make_enemy(hp=200, name="b")])
    _play(st, "proto_mi_ayaka_soumetsu")
    effects.inazuma_overhaul_turn_end(st)
    assert [e.hp for e in st.enemies] == [192, 192]
    effects.inazuma_overhaul_turn_end(st)
    # The second turn's own 8, and THEN the 16 it ends on.
    assert [e.hp for e in st.enemies] == [168, 168]
    effects.inazuma_overhaul_turn_end(st)
    assert [e.hp for e in st.enemies] == [168, 168]


def test_kyouka_rides_your_attacks_then_pops(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    _play(st, "proto_mi_ayato_kyouka")
    effects.resolve_card(st, _attack(amount=6, element="geo"))
    assert st.enemies[0].hp == 80                     # 6 + 4
    assert st.enemies[0].aura == "hydro"              # the override, not Geo
    effects.inazuma_overhaul_turn_end(st)
    effects.inazuma_overhaul_turn_end(st)
    assert st.enemies[0].hp == 80 - C.MI_KYOUKA_FINALE
    assert "mi_kyouka" not in st.player.powers


def test_heartstopper_reads_the_swirls_this_turn(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    _play(st, "proto_mi_heizou_heartstopper")
    assert st.enemies[0].hp == 84
    st = make_state(enemies=[make_enemy(hp=90)])
    st.mi_swirls_this_turn = 2
    _play(st, "proto_mi_heizou_heartstopper")
    assert st.enemies[0].hp == 90 - (6 + 8)


def test_a_swirl_is_counted_at_the_one_reaction_site(overhaul):
    st = make_state()
    effects.companion_overhaul_reaction(st, st.enemies[0], "swirl", "hydro")
    effects.companion_overhaul_reaction(st, st.enemies[0], "vaporize", "hydro")
    assert st.mi_swirls_this_turn == 1


def test_the_parcel_goes_off_next_turn(overhaul):
    st = make_state(enemies=[make_enemy(hp=60)])
    _play(st, "proto_mi_kirara_surprise_dispatch")
    assert st.player.block == 8
    assert st.enemies[0].hp == 60
    effects.inazuma_overhaul_turn_start(st)
    assert st.enemies[0].hp == 60 - C.MI_SURPRISE_DISPATCH_DMG
    effects.inazuma_overhaul_turn_start(st)
    assert st.enemies[0].hp == 60 - C.MI_SURPRISE_DISPATCH_DMG


def test_the_snack_hits_high_and_mends_low(overhaul):
    st = make_state(hp=80, enemies=[make_enemy(hp=90, name="a"),
                                    make_enemy(hp=90, name="b")])
    _play(st, "proto_mi_mizuki_anraku")
    assert [e.hp for e in st.enemies] == [72, 72]

    st = make_state(hp=80, enemies=[make_enemy(hp=90)])
    st.mi_entry_hp = 80
    st.player.hp = 30
    _play(st, "proto_mi_mizuki_anraku")
    assert st.enemies[0].hp == 90
    assert st.player.hp == 40


def test_tamoto_walks_past_block(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    st.enemies[0].block = 30
    _play(st, "proto_mi_chiori_hasode")
    effects.inazuma_overhaul_turn_end(st)
    assert st.enemies[0].hp == 90 - C.MI_TAMOTO_DMG
    assert st.enemies[0].block == 30


# ---------------------------------------------------------------------------
# MEND, MADE CHARACTER-AGNOSTIC
# ---------------------------------------------------------------------------

def test_mend_never_heals_past_the_hp_you_entered_the_fight_with(overhaul):
    st = make_state(hp=80)
    st.mi_entry_hp = 60                               # walked in hurt
    st.player.hp = 55
    assert effects.mend(st, 10) == 5
    assert st.player.hp == 60
    assert effects.mend(st, 10) == 0
    assert st.player.hp == 60


def test_mend_is_the_same_keyword_for_every_character(overhaul):
    """A Universal, so Klee and Furina draft it too. The bound is the fight's
    entry HP whoever plays it -- one rule, one function, no character test."""
    for character in ("klee", "furina", "kokomi"):
        st = make_state(hp=80)
        st.player.character_id = character
        st.mi_entry_hp = 70
        st.player.hp = 40
        assert effects.mend(st, 12) == 12
        assert st.player.hp == 52


def test_the_entry_ceiling_is_captured_at_the_top_of_the_fight():
    """Not on first ask: a lazy capture taken after the first hit would cap a
    Mend at a ceiling the fight had already lowered."""
    src = (REPO / "tier0" / "engine" / "combat.py").read_text(encoding="utf-8")
    assert "state.mi_entry_hp = player.hp" in src
    st = make_state(hp=80)
    st.player.hp = 50
    # And the lazy fallback, for a state no fight opened: captured on FIRST
    # ask, never re-taken, so a later hit cannot move a ceiling already read.
    assert effects.companion_overhaul_entry_hp(st) == 50
    st.player.hp = 20
    assert effects.companion_overhaul_entry_hp(st) == 50
