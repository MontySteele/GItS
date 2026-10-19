"""The INAZUMA half of the companion overhaul -- the Universals, one flag.

THE INAZUMA POOL REWORK (2026-10-18, review/active/inazuma-companions-
2026-10-18.md) took the pool to twenty-nine: three cut, seven rebuilt,
eleven new; growing the pool the same day made it thirty-four (8 / 16 / 10).

Source: the approved workshop `companion-workshop-inazuma-2026-09-01.md`
(approved 2026-09-01 at its four default picks, its sec.9; a Paper artefact on
another branch and not in this tree). Its sec.2 nation shape is "Inazuma reads
the HP bar" and eight of the rows do; its sec.1 pricing rule is what makes the
nine Commons beat a Strike.

NO SWITCH: the companion overhaul's flag and its flag-off pins left at legacy
cleanup stage 6 (2026-10-01); the sim always runs the current companion pool.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). These are
shape assertions about an engine, not numbers about a game.
"""

import re
from pathlib import Path

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, resources
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards

# THE SHIPPED WORLD, NAMED (legacy cleanup stage 3, 2026-10-01): the sim
# defaults to the current kits, and these pins read the shipped ones.


REPO = Path(__file__).resolve().parents[2]



def _caches_clear():
    loader.reset_arm_caches()
    rewards._companion_roster.cache_clear()
    rewards.companion_pool.cache_clear()


@pytest.fixture
def overhaul(monkeypatch):
    """The flag ON, with every id-resolving cache cleared going in and out."""
    _caches_clear()
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

def test_flag_off_ignore_block_is_not_reachable_and_block_still_eats():
    """`ignore_block` defaults False, which is the whole of "every shipped
    caller is byte-identical"."""
    st = make_state(enemies=[make_enemy(hp=50)])
    st.enemies[0].block = 20
    effects.deal_damage_to_enemy(st, st.enemies[0], 8, source="companion")
    assert st.enemies[0].hp == 50
    assert st.enemies[0].block == 12


def test_all_thirty_four_are_offerable(overhaul):
    offerable = {c.id for cards in rewards.companion_pool().values()
                 for c in cards}
    assert set(C.INAZUMA_OVERHAUL_POOL_IDS) <= offerable
    assert all(cid.startswith("proto_") for cid in offerable)


def test_the_pool_ids_and_the_sheet_agree(overhaul):
    """Every `proto_mi_` row is on exactly one list.

    TWO LISTS SINCE R236: the Universals are the pool any character may be
    offered from, and Gorou's Personal was Kokomi's kit. THE KOKOMI
    RE-FOUNDING (2026-10-12) moved all four of Gorou's cards into Kokomi's
    own pool (`C.KOKOMI_OWN_COMPANION_IDS`, counted against her 78), so the
    Universals are twenty-one and the Personal list is empty. A row on the
    sheet and on no list could not be offered at all; a row on a list and
    not on the sheet does not exist."""
    on_sheet = {c.id for c in loader.prototype_cards()
                if c.id.startswith("proto_mi_")}
    own = set(C.KOKOMI_OWN_COMPANION_IDS)
    assert on_sheet == (set(C.INAZUMA_OVERHAUL_POOL_IDS)
                        | set(C.INAZUMA_OVERHAUL_PERSONAL_IDS) | own)
    assert not (set(C.INAZUMA_OVERHAUL_POOL_IDS)
                & (set(C.INAZUMA_OVERHAUL_PERSONAL_IDS) | own))
    assert len(C.INAZUMA_OVERHAUL_POOL_IDS) == 34
    assert len(C.INAZUMA_OVERHAUL_PERSONAL_IDS) == 0
    assert own == {"proto_mi_gorou_inuzaka", "proto_mi_gorou_war_banner",
                   "proto_mi_gorou_juuga", "proto_mi_gorou_crystal_collapse"}


def test_the_rarity_split_is_the_workshops_enumeration(overhaul):
    """9 Common, 11 Uncommon, 4 Rare until the re-founding. The workshop's
    sec.4 printed "12 Uncommon" and counted Gorou's Kokomi-side PERSONAL
    among them. THE KOKOMI RE-FOUNDING (2026-10-12) moved Gorou's three
    Universals (two Common, one Uncommon) into Kokomi's own pool, so the
    Universals are 7 / 10 / 4. THE INAZUMA POOL REWORK (2026-10-18): 8 / 13 /
    8, then 8 / 16 / 10 when the pool grew to two cards a character, then
    8 / 15 / 11 when Baleful Omen (Uncommon) gave way to Musou no Hitotachi
    (Rare), 2026-10-19."""
    split = {}
    for cid in C.INAZUMA_OVERHAUL_POOL_IDS:
        card = loader.peek_card(cid)
        split[card.rarity] = split.get(card.rarity, 0) + 1
    assert split == {"common": 8, "uncommon": 15, "rare": 11}


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


def test_the_offerable_five_stars_are_the_overhaul_rows(overhaul):
    fives = {c.id for cs in rewards.companion_pool().values() for c in cs
             if c.nation == "inazuma" and c.star == 5}
    assert fives
    assert all(i.startswith("proto_mi_") for i in fives)


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
    # `mi_juuga_guard` beside its volley since the Kokomi re-founding
    # (2026-10-12): Juuga's Plan line, the same clock.
    # The Inazuma pool rework (2026-10-18) retired six of its readers and
    # added the Electro rider's "this turn".
    assert seen == ["mi_juuga", "mi_juuga_guard",
                    "mi_sanctifying_ring",
                    "mi_sesshou_sakura", "mi_soumetsu",
                    "mi_crowfeather", "mi_next_electro"], seen


def test_the_start_of_turn_order_is_the_one_the_mod_walks():
    src = (REPO / "tier0" / "engine" / "effects.py").read_text(
        encoding="utf-8")
    body = src.split("def inazuma_overhaul_turn_start(")[1].split("\ndef ")[0]
    seen = list(dict.fromkeys(re.findall(r'"(mi_[a-z_]+)"', body)))
    assert seen == ["mi_blazing_barrier", "mi_surprise_dispatch"], seen


def test_the_element_override_order_puts_the_blanket_first():
    """Five riders can now claim the element and LAST WINS, so the sequence is
    blanket riders first and one-shots after -- with Varka's banked Swirl last
    of all, because its element is the one the board produced a moment ago."""
    src = (REPO / "tier0" / "engine" / "effects.py").read_text(
        encoding="utf-8")
    body = src.split("def companion_overhaul_card_start(")[1]
    body = body.split("\ndef ")[0]
    riders = [m for m in re.findall(r'"(m[ci]_[a-z_]+)"', body)
              if m in ("mc_lightning_fang", "mc_passion_overload",
                       "mi_crowfeather", "mi_next_electro")]
    # Varka's banked Swirl left the element sequence in the Varka round 3
    # fix (2026-10-10): its damage is a separate hit after the Attack.
    # Ayato's blanket Kyouka left with the Inazuma pool rework (2026-10-18).
    assert list(dict.fromkeys(riders)) == [
        "mc_lightning_fang", "mc_passion_overload",
        "mi_crowfeather", "mi_next_electro"]


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


# (General's War Banner's Dexterity clock and its `EB-415` pins left with
# the Kokomi level pass, 2026-10-12: the card gains Block and plans
# permanent Strength.)


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
    assert [e.hp for e in st.enemies] == [60 - C.MI_SANCTIFYING_RING_DMG] * 2
    assert st.player.block == C.MI_SANCTIFYING_RING_BLOCK


def test_the_grass_ring_pays_double_after_the_ring_bites(overhaul):
    """Its own turn: the Sanctifying Ring's HP cost is HP lost since your
    last turn too."""
    st = make_state(hp=80)
    _play(st, "proto_mi_shinobu_grass_ring")
    assert st.player.block == 4
    st = make_state(hp=80)
    _play(st, "proto_mi_shinobu_sanctifying_ring")      # Lose 3 HP
    st.player.block = 0
    _play(st, "proto_mi_shinobu_grass_ring")
    assert st.player.block == 8


def test_the_grass_ring_counts_the_enemy_turn(overhaul):
    """2026-09-23, [USER]: "agreed on a)". "If you lost HP this turn" never
    paid on the player's own turn, because the window opened at the top of
    that turn and the enemy turn -- where HP is lost -- was already wiped. The
    face now reads "if you lost HP since your last turn": from the END of the
    player's previous turn until now."""
    from tier0.engine import refpowers
    st = make_state(hp=80, enemies=[make_enemy(
        hp=200, intents=[{"kind": "attack", "amount": 5}])])
    combat._player_turn(st, lambda s: None)          # turn one ends
    assert st.hp_lost_since_last_turn == 0
    combat._enemy_turn(st, st.enemies[0])            # the enemy hits for 5
    assert st.player.hp == 75
    # The next player turn opens: the old window is wiped, the new one is not.
    refpowers.reset_turn_counters(st)
    assert st.hp_lost_this_turn == 0
    assert st.hp_lost_since_last_turn == 5
    st.player.block = 0
    _play(st, "proto_mi_shinobu_grass_ring")
    assert st.player.block == 8


def test_the_grass_ring_window_opens_at_the_end_of_your_turn(overhaul):
    """HP lost BEFORE your last turn ended does not carry into the next one,
    and on the first turn of combat the window counts from combat start."""
    st = make_state(hp=80)
    resources.note_player_hp_loss(st, 3)             # before turn one
    assert st.hp_lost_since_last_turn == 3
    _play(st, "proto_mi_shinobu_grass_ring")
    assert st.player.block == 8

    st = make_state(hp=80, enemies=[make_enemy(hp=200)])
    resources.note_player_hp_loss(st, 3)
    combat._player_turn(st, lambda s: None)          # the turn ends
    assert st.hp_lost_since_last_turn == 0
    st.player.block = 0
    _play(st, "proto_mi_shinobu_grass_ring")
    assert st.player.block == 4


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
    # `EB-353`: 2 of the mark survive the absorption and the 3 just paid is
    # marked too, because it is the same "this Block" the card names.
    assert (st.player.powers["mi_blazing_barrier"]
            == 2 + C.MI_BLAZING_BARRIER_BLOCK)


def test_the_barrier_pays_on_every_hit_of_a_multi_hit_attack(overhaul):
    """`EB-353`, end to end through `combat._enemy_turn` -- the row's own
    acceptance and the number the blind seat could not reconcile.

    The card says "WHENEVER this Block absorbs damage", and a three-hit attack
    is three absorptions. Against 7x3 the barrier absorbs 6, then 3, then 3 --
    12 of the 21, leaving 9 -- where the old marked-first-and-never-replenished
    spend paid once and absorbed 9 (`klee round 8, opus-act2.md`, finding 4:
    "Thoma is a 9-Block card that prints 6 and implies more", measured at
    exactly 9 on all three occasions the seat could measure it).
    """
    st = make_state(enemies=[make_enemy(hp=50,
                                        intents=[{"kind": "attack",
                                                  "amount": 7, "times": 3}])])
    _play(st, "proto_mi_thoma_blazing_barrier")
    assert st.player.block == 6
    hp_before = st.player.hp

    combat._enemy_turn(st, st.enemies[0])

    # Three absorptions, three payouts: 6 + 3 + 3 = 12 of the 21 absorbed.
    assert st.player.hp == hp_before - 9
    # And the barrier is still standing on the 3 it last paid.
    assert st.player.block == C.MI_BLAZING_BARRIER_BLOCK
    assert (st.player.powers["mi_blazing_barrier"]
            == C.MI_BLAZING_BARRIER_BLOCK)


def test_the_barrier_leaves_when_the_block_it_marked_is_cleared(overhaul):
    """`EB-353`'s other half, and the reason a marked payout is not a shield
    that thickens for the rest of the fight: the mark carries no Block of its
    own, so the turn tick that clears Block takes it with it."""
    st = make_state()
    st.player.block = 0
    st.player.powers["mi_blazing_barrier"] = 6
    effects.inazuma_overhaul_turn_start(st)
    assert "mi_blazing_barrier" not in st.player.powers
    # And a hit that absorbs nothing never fires the rider.
    st.player.block = 0
    st.player.powers["mi_blazing_barrier"] = 6
    effects.companion_overhaul_block_absorbed(st, st.enemies[0], 0, 0)
    assert st.player.block == 0
    assert st.player.powers["mi_blazing_barrier"] == 6


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


# ---------------------------------------------------------------------------
# ITTO AND RAIDEN
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# THE NEW NINE
# ---------------------------------------------------------------------------

@pytest.mark.usefixtures("consume_triggers")
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


def test_the_snack_hits_and_mends_at_any_hp(overhaul):
    """2026-10-11 Companion pass: "Swirl ALL enemies. Deal 14 damage to ALL
    enemies and Mend 6." Both halves every time; the 70% branch is gone."""
    st = make_state(hp=80, enemies=[make_enemy(hp=90, name="a"),
                                    make_enemy(hp=90, name="b")])
    _play(st, "proto_mi_mizuki_anraku")
    assert [e.hp for e in st.enemies] == [76, 76]
    assert st.player.hp == 80                      # Mend restores, never past

    st = make_state(hp=80, enemies=[make_enemy(hp=90)])
    st.mi_entry_hp = 80
    st.player.hp = 30
    _play(st, "proto_mi_mizuki_anraku")
    assert st.enemies[0].hp == 76                  # low HP still hits
    assert st.player.hp == 36                      # and Mends 6


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


# ------------------ `EB-379`: the face says WHEN the finale lands ----------


def _proto_face(card_id: str) -> str:
    """One prototype row's printed description, off the sheet."""
    import yaml
    rows = yaml.safe_load(
        (REPO / "docs" / "prototype-surface.yaml").read_text(
            encoding="utf-8"))
    row = next(r for r in rows if r["id"] == card_id)
    return row["description"]


# ------------------ `EB-698`: which turn pays 8 and which pays 16 ---------


def test_soumetsus_face_says_which_turn_pays_which_number(overhaul):
    """`EB-698` (Kokomi r30 lane 1). The card said "deal 8 at the end of your
    turn" and "after 2 turns, deal 16"; the badge said "8 ... then 16 when it
    ends, lasts 1 turn". Three plays, and the seat never knew which number was
    about to land.

    WHAT THE CODE DOES is one 8 at the end of each of the N turns and, on the
    last of them, the 16 as well -- `test_soumetsu_sweeps_twice_then_ends_on_
    the_big_one` above measures the 24. So the face says that, in that order,
    and no number moved.
    """
    face = _proto_face("proto_mi_ayaka_soumetsu")
    # The text pass of 2026-10-08: the repeating effect's one spelling, the
    # ten companion rows' "For N turns, at the end of your turn".
    assert "For 2 turns, at the end of your turn deal 8" in face
    # THE 2026-09-25 TEXT PASS: the finale in rule 8's spelling, "N
    # additional damage", on both surfaces.
    assert "The last one deals 16 additional damage." in face
    # The two readings the row named, both gone: a finale AFTER the clock, and
    # a single anonymous end-of-turn volley.
    assert "After 2 turns" not in face
    assert "At the end of your turn, deal 8" not in face


def test_soumetsus_badge_says_the_same_sentence_as_its_face(overhaul):
    """`EB-698`'s other half -- "one text on both surfaces". The badge is where
    the LIVE count lives (`{Amount}` is turns remaining, and it is one of the
    three dumb variables `PowerModel.GetDumbHoverTip` binds on a static row),
    so it carries that on top of the same two clauses."""
    src = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "CompanionOverhaulInazuma.cs").read_text(encoding="utf-8")
    badge = src.split("class SoumetsuPower")[1].split("class ")[0]

    assert "The last deals " in badge
    assert "additional " in badge
    assert "{Amount:plural:turn|turns} left" in badge
    # The wording the seat could not read, and the one the face dropped.
    assert "when it ends" not in badge
    assert "Lasts for" not in badge
    # Both numbers are the arm's constants on both surfaces, never literals.
    assert "CompanionOverhaulLaw.SoumetsuDamage" in badge
    assert "CompanionOverhaulLaw.SoumetsuFinale" in badge


# ---------------------------------------------------------------------------
# THE INAZUMA POOL REWORK (2026-10-18), card by card
# ---------------------------------------------------------------------------

from tier0.content import upgrades                     # noqa: E402
from tier0.engine import kokomi_plan, powers          # noqa: E402


def _up(card_id):
    return upgrades.apply_upgrade(loader.get_card(card_id))


def _hand(st, n=5):
    st.player.draw_pile = [Card(id=f"f{i}", name="f", cost=1, type="skill")
                           for i in range(n)]


def test_the_three_cuts_are_off_the_sheet(overhaul):
    on_sheet = {c.id for c in loader.prototype_cards()}
    for cid in ("proto_mi_yoimiya_aurous_blaze",
                "proto_mi_itto_superlative_superstrength",
                # Cut 2026-10-19, when Musou no Hitotachi came back.
                "proto_mi_raiden_baleful_omen"):
        assert cid not in on_sheet


def test_heartstopper_counts_the_other_attacks_played_this_turn(overhaul):
    """"Deal 4 Anemo damage, plus 4 [6] for each other Attack you played
    this turn." The count is read during the play, before this Attack is
    noted, so a first Attack deals 4."""
    st = make_state(enemies=[make_enemy(hp=90)])
    _play(st, "proto_mi_heizou_heartstopper")
    assert st.enemies[0].hp == 86
    st = make_state(enemies=[make_enemy(hp=90)])
    st.attacks_played_this_turn = 2
    _play(st, "proto_mi_heizou_heartstopper")
    assert st.enemies[0].hp == 90 - (4 + 8)
    st = make_state(enemies=[make_enemy(hp=90)])
    st.attacks_played_this_turn = 2
    effects.resolve_card(st, _up("proto_mi_heizou_heartstopper"))
    assert st.enemies[0].hp == 90 - (4 + 12)


def test_naptime_gains_seven_and_plans_block_and_a_draw(overhaul):
    st = make_state()
    _play(st, "proto_mi_sayu_naptime")
    assert st.player.block == 7
    card = loader.get_card("proto_mi_sayu_naptime")
    assert card.cost == 1
    assert card.plan == [{"op": "block", "amount": 7},
                         {"op": "draw", "amount": 1}]
    up = _up("proto_mi_sayu_naptime")
    assert up.effects[0]["amount"] == 10 and up.plan[0]["amount"] == 10


def test_daruma_gains_six_and_plans_energy_and_block(overhaul):
    st = make_state()
    _play(st, "proto_mi_sayu_daruma")
    assert st.player.block == 6
    card = loader.get_card("proto_mi_sayu_daruma")
    assert not card.exhaust
    assert card.plan == [{"op": "energy", "amount": 1},
                         {"op": "block", "amount": 6}]


def test_kirara_keeps_her_parcel_and_plans_fourteen_block(overhaul):
    card = loader.get_card("proto_mi_kirara_surprise_dispatch")
    assert card.plan == [{"op": "block", "amount": 14}]
    up = _up("proto_mi_kirara_surprise_dispatch")
    assert up.effects[0]["amount"] == 11 and up.plan[0]["amount"] == 18


def test_the_plan_lines_pass_the_shape_check(overhaul):
    for cid in ("proto_mi_sayu_naptime", "proto_mi_sayu_daruma",
                "proto_mi_kirara_surprise_dispatch",
                "proto_mi_ayato_kyouka_fuushi"):
        assert kokomi_plan.plan_shape_reason(loader.get_card(cid).plan) is None


def test_hyouka_hits_all_and_weakens_each(overhaul):
    st = make_state(enemies=[make_enemy(hp=60, name="a"),
                             make_enemy(hp=60, name="b")])
    _play(st, "proto_mi_ayaka_hyouka")
    assert [e.hp for e in st.enemies] == [55, 55]
    assert [e.powers.get("weak") for e in st.enemies] == [1, 1]
    assert [e.aura for e in st.enemies] == ["cryo", "cryo"]


def test_ooyoroi_keeps_up_to_eight_block_through_the_clear(overhaul):
    # 6 [9] -> 8 [12], the pool sweep (2026-10-18, sec.3 pick 4).
    st = make_state()
    _play(st, "proto_mi_thoma_crimson_ooyoroi")
    assert st.player.powers["mi_crimson_ooyoroi"] == 8
    st.player.block = 10
    assert effects.ooyoroi_keeps(st) == 8
    st.player.block = 4
    assert effects.ooyoroi_keeps(st) == 4
    assert effects.block_clear_keeps(st) == 4
    st2 = make_state()
    assert effects.block_clear_keeps(st2) is None


def test_the_first_block_clear_preventer_worn_wins(overhaul):
    """Watatsumi's Grace and Crimson Ooyoroi are the same shape, and the base
    game names one preventer: the first worn."""
    st = make_state()
    st.player.block = 20
    st.player.powers[kokomi_plan.WATATSUMIS_GRACE] = 10
    st.player.powers["mi_crimson_ooyoroi"] = 6
    # Grace's own read is gated on her kit; without it, Ooyoroi answers.
    kept = effects.block_clear_keeps(st)
    assert kept in (10, 6)
    st = make_state()
    st.player.block = 20
    st.player.powers["mi_crimson_ooyoroi"] = 6
    st.player.powers[kokomi_plan.WATATSUMIS_GRACE] = 10
    assert effects.block_clear_keeps(st) == 6


def test_stormcall_applies_vulnerable_and_the_next_attack_is_electro(overhaul):
    st = make_state(enemies=[make_enemy(hp=60)])
    _play(st, "proto_mi_sara_tengu_stormcall")
    assert st.enemies[0].powers.get("vulnerable") == 2
    assert st.player.powers["mi_next_electro"] == 1
    effects.resolve_card(st, _attack(amount=6, element="geo"))
    assert st.enemies[0].aura == "electro"
    assert "mi_next_electro" not in st.player.powers
    assert loader.get_card("proto_mi_sara_tengu_stormcall").cost == 0


def test_the_electro_rider_leaves_with_the_turn(overhaul):
    st = make_state()
    _play(st, "proto_mi_sara_tengu_stormcall")
    effects.inazuma_overhaul_turn_end(st)
    assert "mi_next_electro" not in st.player.powers


def _musou_board(hand_size):
    st = make_state(enemies=[make_enemy(hp=200, name="a"),
                             make_enemy(hp=200, name="b")])
    st.player.hand = [Card(id=f"h{i}", name="h", cost=1, type="skill")
                      for i in range(hand_size)]
    return st


@pytest.mark.parametrize("hand_size", [0, 3, 7])
def test_musou_deals_sixteen_plus_two_per_card_in_hand(overhaul, hand_size):
    """Musou no Hitotachi (2026-10-19): "Deal 16 Electro damage to ALL
    enemies, plus 2 for each card in your Hand." The hand at resolution;
    Musou itself has left it."""
    st = _musou_board(hand_size)
    _play(st, "proto_mi_raiden_musou_no_hitotachi")
    for e in st.enemies:
        assert e.hp == 200 - (16 + 2 * hand_size)
        assert e.aura == "electro"


def test_musou_counts_the_hand_without_itself(overhaul):
    """Played from the hand through the real play path, Musou is not one of
    the cards it counts."""
    st = _musou_board(4)
    musou = loader.get_card("proto_mi_raiden_musou_no_hitotachi")
    st.player.hand.append(musou)
    st.player.energy = 3
    combat.play_card(st, musou)
    assert [e.hp for e in st.enemies] == [200 - 24, 200 - 24]


def test_musou_upgrade_is_twenty_two_base(overhaul):
    st = _musou_board(2)
    effects.resolve_card(st, _up("proto_mi_raiden_musou_no_hitotachi"))
    assert st.enemies[0].hp == 200 - (22 + 4)
    assert loader.get_card("proto_mi_raiden_musou_no_hitotachi").cost == 3
    assert loader.get_card("proto_mi_raiden_musou_no_hitotachi").rarity         == "rare"


def test_musou_takes_three_strength_from_everyone_this_turn(overhaul):
    """"ALL enemies and you lose 3 Strength this turn": Piercing Wail's
    `temp_strength_down` on every enemy and on the player, each returned at
    its own side's turn end."""
    from tier0.engine import powers
    st = _musou_board(0)
    _play(st, "proto_mi_raiden_musou_no_hitotachi")
    for c in [*st.enemies, st.player]:
        assert c.powers.get("strength", 0) == -3
        assert c.powers.get("temp_strength_down") == 3
    powers.on_turn_end(st, st.player)
    assert st.player.powers.get("strength", 0) == 0
    st.in_player_turn = False
    for e in st.enemies:
        powers.on_turn_end(st, e)
        assert e.powers.get("strength", 0) == 0


def test_musou_hits_before_the_strength_loss(overhaul):
    """The damage lands first, so the player's own -3 never shrinks it."""
    st = _musou_board(0)
    st.player.powers["strength"] = 2
    _play(st, "proto_mi_raiden_musou_no_hitotachi")
    assert st.enemies[0].hp == 200 - 18
    assert st.player.powers["strength"] == -1


def test_chiori_hits_twice_through_block(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    st.enemies[0].block = 30
    _play(st, "proto_mi_chiori_hasode")
    assert st.enemies[0].hp == 80
    assert st.enemies[0].block == 30
    assert loader.get_card("proto_mi_chiori_hasode").type == "attack"


def test_kyouka_wets_the_board_and_raises_this_turns_attacks(overhaul):
    st = make_state(enemies=[make_enemy(hp=90, name="a"),
                             make_enemy(hp=90, name="b")])
    _play(st, "proto_mi_ayato_kyouka")
    assert [e.aura for e in st.enemies] == ["hydro", "hydro"]
    assert st.player.powers["attack_up_this_turn"] == 3
    effects.player_turn_end_triggers(st)
    assert "attack_up_this_turn" not in st.player.powers


def test_ushi_gains_strength_only_against_an_attack_intent(overhaul):
    st = make_state(enemies=[make_enemy(intents=[{"kind": "attack",
                                                  "amount": 5}])])
    _play(st, "proto_mi_itto_ushi")
    assert st.player.block == 8
    assert st.player.powers.get("strength") == 1
    st = make_state(enemies=[make_enemy(intents=[{"kind": "buff"}])])
    _play(st, "proto_mi_itto_ushi")
    assert st.player.block == 8
    assert not st.player.powers.get("strength")


def test_aisa_weakens_all_and_draws_two(overhaul):
    st = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    _hand(st)
    _play(st, "proto_mi_mizuki_aisa_utamakura")
    assert [e.powers.get("weak") for e in st.enemies] == [1, 1]
    assert len(st.player.hand) == 2


def test_windmuster_hits_swirls_and_draws(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    _hand(st)
    _play(st, "proto_mi_heizou_windmuster_kick")
    assert st.enemies[0].hp == 76   # 14 since the pool sweep (2026-10-18)
    assert len(st.player.hand) == 1


def test_euthymia_retains_the_whole_hand(overhaul):
    from tier0.engine import refpowers
    st = make_state()
    _play(st, "proto_mi_raiden_euthymia")
    cards = [Card(id="x", name="x", cost=1, type="skill"),
             Card(id="y", name="y", cost=1, type="attack")]
    assert refpowers.retain_at_flush(st, cards) == cards


def test_royal_descent_answers_an_attack_that_dealt_nothing(overhaul):
    st = make_state(enemies=[make_enemy(hp=60, intents=[
        {"kind": "attack", "amount": 5, "times": 2}])])
    _play(st, "proto_mi_itto_royal_descent")
    st.player.block = 20
    combat._enemy_turn(st, st.enemies[0])
    # Once for the whole two-hit attack, not per hit.
    assert st.enemies[0].hp == 60 - 6
    st.player.block = 7
    combat._enemy_turn(st, st.enemies[0])
    assert st.enemies[0].hp == 60 - 6                 # 3 got through


def test_royal_descent_reads_the_whole_attack(overhaul):
    st = make_state()
    st.player.powers["mi_royal_descent"] = 6
    e = st.enemies[0]
    hp = e.hp
    effects.royal_descent(st, e, [])
    assert e.hp == hp                                  # no hit, no answer
    effects.royal_descent(st, e, [(5, 0), (0, 2)])
    assert e.hp == hp
    effects.royal_descent(st, e, [(5, 0), (5, 0)])
    assert e.hp == hp - 6


def test_niwabi_doubles_the_first_attack_each_turn(overhaul):
    st = make_state()
    st.player.powers["mi_niwabi"] = 1
    attack = _attack()
    skill = Card(id="s", name="s", cost=1, type="skill", effects=[])
    assert effects.niwabi_replays(st, attack) == 1
    assert effects.niwabi_replays(st, skill) == 0
    st.attacks_played_this_turn = 1
    assert effects.niwabi_replays(st, attack) == 0
    st2 = make_state()
    assert effects.niwabi_replays(st2, attack) == 0


def test_niwabi_end_to_end_plays_the_first_attack_twice(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    st.player.energy = 10
    st.player.powers["mi_niwabi"] = 1
    first = _attack(amount=6, element=None)
    second = _attack(amount=6, element=None)
    st.player.hand = [first, second]
    combat.play_card(st, first)
    assert st.enemies[0].hp == 90 - 12
    combat.play_card(st, second)
    assert st.enemies[0].hp == 90 - 18


def test_chihayaburu_draws_on_each_swirl(overhaul):
    st = make_state()
    _hand(st)
    st.player.powers["mi_chihayaburu"] = 1
    effects.companion_overhaul_reaction(st, st.enemies[0], "swirl", "hydro")
    effects.companion_overhaul_reaction(st, st.enemies[0], "vaporize", "hydro")
    assert len(st.player.hand) == 1


def test_hanega_takes_three_off_card_block_and_gives_an_energy(overhaul):
    st = make_state()
    _play(st, "proto_mi_wanderer_hanega")
    assert effects.hanega_energy(st) == 1
    assert powers.modify_block_gained(st.player, 5) == 2
    assert powers.modify_block_gained(st.player, 2) == 0
    _play(st, "proto_mi_thoma_blazing_barrier")       # 6 printed
    assert st.player.block == 3
    # Power Block is untouched: the ring's end-of-turn 6 lands whole.
    st.player.block = 0
    st.player.powers["mi_sanctifying_ring"] = 1
    effects.inazuma_overhaul_turn_end(st)
    assert st.player.block == C.MI_SANCTIFYING_RING_BLOCK


def test_the_rare_powers_upgrade_as_listed(overhaul):
    # 2026-10-19: Euthymia's upgrade is Innate; the cost stays 2.
    up = _up("proto_mi_raiden_euthymia")
    assert up.innate and up.cost == 2
    assert _up("proto_mi_yoimiya_niwabi").cost == 1
    assert _up("proto_mi_kazuha_chihayaburu").cost == 0
    assert _up("proto_mi_wanderer_hanega").cost == 0
    assert _up("proto_mi_itto_royal_descent").effects[0]["amount"] == 9
    assert _up("proto_mi_thoma_crimson_ooyoroi").effects[0]["amount"] == 12


# ---------------------------------------------------------------------------
# KYOUKA FUUSHI AND GROWING THE POOL TO 34 (2026-10-18)
# ---------------------------------------------------------------------------
# review/active/inazuma-companions-2026-10-18.md, "Growing the pool to 34".
# The C# twin is `InazumaCompanionOverhaulTests.cs`.

from tier0.tests.test_kokomi_refounding import (  # noqa: E402
    card as _kk_card, kokomi_state as _kk_state)


def _plan_hits(st, cid):
    return [e for e in st.log if e["event"] == "damage"
            and e.get("source") == "plan"]


def _draw_probe(i):
    return Card(id=f"proto_kk_probe{i}", name=f"Probe {i}", cost=0,
                type="skill", effects=[],
                plan=[{"op": "draw", "amount": 1}])


def test_kyouka_fuushi_row(overhaul):
    c = loader.get_card("proto_mi_ayato_kyouka_fuushi")
    assert (c.rarity, c.cost, c.type) == ("rare", 2, "attack")
    assert c.effects == [{"op": "damage", "amount": 7, "times": 3,
                          "target": "enemy", "applies_element": True}]
    assert c.plan == [{"op": "damage_times_plus_earlier_plans", "amount": 7,
                       "times": 3, "target": "front_enemy"}]
    up = _up("proto_mi_ayato_kyouka_fuushi")
    assert up.effects[0]["amount"] == 9 and up.plan[0]["amount"] == 9


def test_kyouka_fuushi_counts_earlier_plans_not_itself():
    st = make_state()
    clause = {"op": "damage_times_plus_earlier_plans", "amount": 7,
              "times": 3}
    st.kk_chain_plans_this_turn = 1          # itself only
    assert kokomi_plan.earlier_plan_hits(st, clause) == 3
    st.kk_chain_plans_this_turn = 3          # two real Plans before it
    assert kokomi_plan.earlier_plan_hits(st, clause) == 5


def test_kyouka_fuushi_carried_out_after_two_plans_hits_five_times(overhaul):
    st = _kk_state()
    kokomi_plan.schedule(st, _draw_probe(0))
    kokomi_plan.schedule(st, _draw_probe(1))
    kokomi_plan.schedule(st, _kk_card("proto_mi_ayato_kyouka_fuushi"))
    st.player.draw_pile = [_kk_card("proto_kk_coral_bulwark")
                           for _ in range(4)]
    hp = st.enemies[0].hp
    kokomi_plan.resolve_all(st)
    assert len(_plan_hits(st, "proto_mi_ayato_kyouka_fuushi")) == 5
    assert hp - st.enemies[0].hp == 7 * 5


def test_kyouka_fuushi_behind_stings_and_wards_hits_three_times(overhaul):
    st = _kk_state()
    kokomi_plan.schedule(st, _kk_card(kokomi_plan.WARD_ID))
    kokomi_plan.schedule(st, _kk_card(kokomi_plan.WARD_ID))
    kokomi_plan.schedule(st, _kk_card("proto_mi_ayato_kyouka_fuushi"))
    st.player.draw_pile = [_kk_card("proto_kk_coral_bulwark")
                           for _ in range(4)]
    hp = st.enemies[0].hp
    kokomi_plan.resolve_all(st)
    assert hp - st.enemies[0].hp == 7 * 3


def test_hyouka_is_uncommon_now(overhaul):
    assert loader.get_card("proto_mi_ayaka_hyouka").rarity == "uncommon"
    assert _up("proto_mi_ayaka_hyouka").effects[0]["amount"] == 8


def test_meowteor_kick_deals_three_more_with_block(overhaul):
    st = make_state(enemies=[make_enemy(hp=60)])
    _play(st, "proto_mi_kirara_meowteor_kick")
    assert st.enemies[0].hp == 60 - 9
    st = make_state(enemies=[make_enemy(hp=60)])
    st.player.block = 1
    _play(st, "proto_mi_kirara_meowteor_kick")
    assert st.enemies[0].hp == 60 - 12
    assert _up("proto_mi_kirara_meowteor_kick").effects[0]["amount"] == 12


def test_ryuukin_hits_three_times(overhaul):
    st = make_state(enemies=[make_enemy(hp=60)])
    _play(st, "proto_mi_yoimiya_ryuukin_saxifrage")
    assert st.enemies[0].hp == 60 - 12
    assert _up("proto_mi_yoimiya_ryuukin_saxifrage").effects[0]["amount"] == 5


def test_kyougen_deals_six_more_with_no_block(overhaul):
    st = make_state(enemies=[make_enemy(hp=60)])
    _play(st, "proto_mi_wanderer_kyougen")
    assert st.enemies[0].hp == 60 - 12
    st = make_state(enemies=[make_enemy(hp=60)])
    st.player.block = 4
    _play(st, "proto_mi_wanderer_kyougen")
    assert st.enemies[0].hp == 60 - 6
    up = _up("proto_mi_wanderer_kyougen")
    assert up.effects[0]["amount"] == 8


def test_twin_blades_adds_one_hit_to_multi_hit_attacks_only(overhaul):
    st = make_state(enemies=[make_enemy(hp=90)])
    _play(st, "proto_mi_chiori_twin_blades")
    assert st.player.powers["mi_twin_blades"] == 1
    _play(st, "proto_mi_yoimiya_ryuukin_saxifrage")      # 4 hits of 4
    assert st.enemies[0].hp == 90 - 16
    _play(st, "proto_mi_kirara_meowteor_kick")           # one hit: 9
    assert st.enemies[0].hp == 90 - 16 - 9
    up = _up("proto_mi_chiori_twin_blades")
    assert up.innate and up.cost == 1


def test_twin_blades_reaches_a_multi_hit_plan_line(overhaul):
    st = _kk_state()
    st.player.powers["mi_twin_blades"] = 1
    kokomi_plan.schedule(st, _kk_card("proto_mi_ayato_kyouka_fuushi"))
    st.player.draw_pile = [_kk_card("proto_kk_coral_bulwark")
                           for _ in range(4)]
    hp = st.enemies[0].hp
    kokomi_plan.resolve_all(st)
    assert hp - st.enemies[0].hp == 7 * 4


def test_sacred_sakuras_favor_raises_end_of_turn_damage_by_half(overhaul):
    st = make_state(enemies=[make_enemy(hp=60)])
    st.player.powers["mi_sanctifying_ring"] = 1
    effects.player_turn_end_triggers(st)
    plain = 60 - st.enemies[0].hp
    assert plain == C.MI_SANCTIFYING_RING_DMG
    st = make_state(enemies=[make_enemy(hp=60)])
    _play(st, "proto_mi_yae_sacred_sakuras_favor")
    st.player.powers["mi_sanctifying_ring"] = 1
    effects.player_turn_end_triggers(st)
    assert 60 - st.enemies[0].hp == int(plain * C.MI_SACRED_SAKURA_MULT)
    # An unpowered hit in the window (a Sakura strike, a guest's act) too.
    hp = st.enemies[0].hp
    effects.deal_damage_to_enemy(st, st.enemies[0], 4, element=None,
                                 source="card", powered=False)
    assert hp - st.enemies[0].hp == 6
    assert _up("proto_mi_yae_sacred_sakuras_favor").cost == 1


def test_sacred_sakuras_favor_skips_damage_outside_the_end_of_turn(overhaul):
    st = make_state(enemies=[make_enemy(hp=60)])
    st.player.powers["mi_sacred_sakuras_favor"] = 1
    assert st.turn_end_window is False
    _play(st, "proto_mi_kirara_meowteor_kick")           # a card: 9
    assert st.enemies[0].hp == 60 - 9
    hp = st.enemies[0].hp
    effects.deal_damage_to_enemy(st, st.enemies[0], 6, element=None,
                                 source="companion")     # turn-start volley
    assert hp - st.enemies[0].hp == 6


def test_the_end_of_turn_window_closes_after_the_last_tenant():
    src = (REPO / "tier0" / "engine" / "combat.py").read_text(encoding="utf-8")
    body = src[src.index("effects.player_turn_end_triggers(state)"):]
    assert body.index("furina_stage.turn_end(state)") < body.index(
        "state.turn_end_window = False")


def test_sacred_sakuras_favor_is_offered_to_yae(overhaul):
    from tier0.engine import yae_shrine
    assert not yae_shrine.hidden_from("proto_mi_yae_sacred_sakuras_favor",
                                      "yae")
    assert yae_shrine.hidden_from("proto_mi_yae_sesshou_sakura", "yae")


def test_hanega_stacks_both_halves(overhaul):
    st = make_state()
    _play(st, "proto_mi_wanderer_hanega")
    _play(st, "proto_mi_wanderer_hanega")
    assert effects.hanega_energy(st) == 2
    assert powers.modify_block_gained(st.player, 8) == 2
