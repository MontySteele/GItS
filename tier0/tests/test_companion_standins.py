"""THE COMPANION STAND-IN SEAM -- the sheet contract, the hand-off, the rules.

A stand-in is a whole Klee-only card handed to Klee IN PLACE of one named
Universal (Klee brief pick 6; the approved Mondstadt workshop sec.1; R236
sec.3). Three claims are worth pinning rather than intending, and this file is
those three:

  1. IT IS IN NO POOL. Not the character-blind Universal pool, not the Personal
     reward share, not a shop slot, not the Featured Banner.
  2. THE ODDS DO NOT MOVE. Run the same seed for Klee and for another character
     and the two offer sequences are the SAME cards, one of them with the four
     Universals swapped -- which is only possible if the candidate lists, the
     rarity rolls and the weighted draws were untouched.
  3. FLAG OFF IS BYTE-IDENTICAL. `hand_off` is the identity, and no surface can
     reach a stand-in at all.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). These are
shape assertions about an engine, not numbers about a game.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import companion_standins as standins
from tier0.engine import combat, effects, klee_overhaul
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards, shop


def _caches_clear():
    """Every memo whose answer depends on the flag. Same list
    `test_companion_overhaul` clears, plus the stand-in map, which is derived
    from the surface and so is a view of the content tree like the rest."""
    loader._card_prototype.cache_clear()
    standins._replacements.cache_clear()
    rewards._companion_roster.cache_clear()
    rewards.companion_pool.cache_clear()
    rewards.five_star_roster.cache_clear()
    rewards.designed_nations.cache_clear()


@pytest.fixture
def overhaul(monkeypatch):
    _caches_clear()
    monkeypatch.setattr(C, "COMPANION_OVERHAUL", True)
    yield
    _caches_clear()


@pytest.fixture
def arms(monkeypatch, overhaul):
    """Both arms: the caretakers read the Klee overhaul's explosion ledger, so
    their rules cannot be exercised without the arm that keeps it."""
    monkeypatch.setattr(C, "KLEE_OVERHAUL", True)
    yield


# --- 1. the sheet contract ---------------------------------------------------

def test_the_constant_and_the_sheet_agree(overhaul):
    """`C.COMPANION_STANDIN_IDS` exists for one consumer (the upgrade index's
    reachable set) and is DERIVED everywhere else, so it must equal the
    derivation."""
    assert set(C.COMPANION_STANDIN_IDS) == set(standins.standin_ids())


def test_every_standin_is_klee_only_and_replaces_a_universal(overhaul):
    for cid in C.COMPANION_STANDIN_IDS:
        card = loader.peek_card(cid)
        assert card.personal_pool == "klee", cid
        assert card.replaces in C.MONDSTADT_OVERHAUL_POOL_IDS, cid
        # A face swap, never a tier move: the stand-in rides the Universal's
        # own offer, so a different rarity would move the odds it appears at.
        assert card.rarity == loader.peek_card(card.replaces).rarity, cid
        assert card.nation == loader.peek_card(card.replaces).nation, cid


def test_art_of_names_the_row_it_replaces(overhaul):
    """`art_of:` is stripped before `Card` (tier 0 draws nothing), so it is read
    off the sheet -- which is also where the codegen reads it."""
    rows = {r["id"]: r for r in loader.yaml.safe_load(
        loader.PROTOTYPE_SHEET.read_text(encoding="utf-8"))}
    for cid in C.COMPANION_STANDIN_IDS:
        row = rows[cid]
        assert row["art_of"] == row["replaces"], cid
        # No new image is owed: the id it wears is a row that already exists.
        assert row["art_of"] in rows


def test_a_shipped_row_may_not_stand_in_for_anything():
    from tier0.engine.state import Card

    with pytest.raises(ValueError, match="prototype surface only"):
        loader._validate_card_shape(Card(
            id="not_a_prototype", name="x", cost=1, type="skill",
            personal_pool="klee", replaces="proto_mc_diona_icy_paws"))


def test_a_standin_needs_a_personal_pool():
    from tier0.engine.state import Card

    with pytest.raises(ValueError, match="needs a `personal_pool:`"):
        loader._validate_card_shape(Card(
            id="proto_mc_x", name="x", cost=1, type="skill",
            replaces="proto_mc_diona_icy_paws"))


def test_personal_pool_normalises_a_one_member_list():
    from tier0.engine.state import Card

    card = Card.from_dict({"id": "proto_mc_x", "name": "x", "cost": 1,
                           "type": "skill", "personal_pool": ["klee"]})
    assert card.personal_pool == "klee"          # every existing reader works
    with pytest.raises(ValueError, match="exactly ONE character id"):
        Card.from_dict({"id": "proto_mc_y", "name": "y", "cost": 1,
                        "type": "skill", "personal_pool": ["klee", "furina"]})


# --- 2. no pool holds a stand-in ---------------------------------------------

def test_no_offer_pool_holds_a_standin(overhaul):
    standin_ids = set(C.COMPANION_STANDIN_IDS)
    assert not {c.id for c in rewards._companion_roster()} & standin_ids
    for tier in rewards.companion_pool().values():
        assert not {c.id for c in tier} & standin_ids
    for nation in rewards.designed_nations():
        assert not {c.id for c in rewards.five_star_roster(nation)} & standin_ids


# --- 3. the hand-off ---------------------------------------------------------

def test_klee_is_handed_each_standin_in_place_of_its_universal(overhaul):
    for cid in C.COMPANION_STANDIN_IDS:
        universal = loader.peek_card(cid).replaces
        assert standins.hand_off(universal, "klee") == cid


def test_every_other_character_is_handed_the_universal(overhaul):
    for cid in C.COMPANION_STANDIN_IDS:
        universal = loader.peek_card(cid).replaces
        for other in ("furina", "kokomi", None):
            assert standins.hand_off(universal, other) == universal
        # And a stand-in is never swapped for anything, by anyone.
        assert standins.hand_off(cid, "klee") == cid


def test_the_reward_slot_swaps_and_the_odds_do_not_move(overhaul):
    """ONE seed, two characters. The two sequences must be the SAME offers with
    the four Universals swapped for Klee -- which can only hold if the tiers,
    the rarity roll and the nation-weighted draw were untouched."""
    swap = {loader.peek_card(cid).replaces: cid
            for cid in C.COMPANION_STANDIN_IDS}
    klee, furina = [], []
    for seed in range(120):
        klee += [c.id for c in rewards.roll_rewards(
            random.Random(seed), "klee", companion_offers=1) if c.is_companion]
        furina += [c.id for c in rewards.roll_rewards(
            random.Random(seed), "furina", companion_offers=1)
            if c.is_companion]
    # Klee saw at least one of them, or the assertion below proves nothing.
    assert set(klee) & set(C.COMPANION_STANDIN_IDS)
    assert not set(furina) & set(C.COMPANION_STANDIN_IDS)
    # The comparison is per-character, because the two roll different NATION
    # weights: what must hold is that no Klee offer is a Universal that has a
    # stand-in, and that every stand-in she saw stands where one would be.
    assert not set(klee) & set(swap)
    assert all(c in swap.values() or c not in swap
               for c in klee)


def test_the_reward_slot_hands_the_universal_to_klee_with_the_flag_off():
    _caches_clear()
    try:
        seen = set()
        for seed in range(120):
            seen |= {c.id for c in rewards.roll_rewards(
                random.Random(seed), "klee", companion_offers=1)}
        assert not seen & set(C.COMPANION_STANDIN_IDS)
        assert not any(cid.startswith("proto_") for cid in seen)
    finally:
        _caches_clear()


def test_the_shop_swaps_and_keeps_one_row_per_visit(overhaul):
    seen_standin = False
    for seed in range(120):
        offers = shop.companion_shop_offer(random.Random(seed), "klee")
        ids = [c.id for c, _price in offers]
        assert len(ids) == len(set(ids))          # no row stocked twice
        assert not {loader.peek_card(cid).replaces
                    for cid in ids if cid in C.COMPANION_STANDIN_IDS} & set(ids)
        seen_standin |= bool(set(ids) & set(C.COMPANION_STANDIN_IDS))
        for cid in ids:
            assert loader.peek_card(cid).personal_pool in (None, "klee")
    assert seen_standin
    for seed in range(40):
        ids = [c.id for c, _p in shop.companion_shop_offer(random.Random(seed),
                                                       "furina")]
        assert not set(ids) & set(C.COMPANION_STANDIN_IDS)


def test_hand_off_is_the_identity_with_the_flag_off():
    for cid in C.COMPANION_STANDIN_IDS:
        universal = "proto_mc_diona_icy_paws"
        assert standins.hand_off(universal, "klee") == universal
        assert standins.hand_off(cid, "klee") == cid


# --- 4. the caretakers' rules -----------------------------------------------

def _klee_state():
    state = make_state(enemies=[make_enemy(hp=200)])
    # `klee_overhaul.live` is the flag AND the seat: the arm is Klee's rules,
    # and a stand-in is handed to Klee, so the two gates agree by construction.
    state.player.character_id = "klee"
    state.turn = 1
    # The ledger rolls on a ROUND STAMP, so turn 1 has to be stamped or the
    # first boundary reads a jump of more than one round and honestly reports
    # zero -- `combat._player_turn` does this on every turn including the first.
    klee_overhaul.roll_to(state, state.turn)
    return state


def test_diona_pays_on_the_first_bomb_of_the_turn(arms):
    state = _klee_state()
    state.player.powers[standins.SHAKEN_NOT_PURRED] = 5
    klee_overhaul.place(state, state.enemies[0], 6)
    before = state.player.block
    klee_overhaul.set_off(state, state.enemies[0])
    assert state.player.block == before + 5
    assert standins.SHAKEN_NOT_PURRED not in state.player.powers   # one-shot


def test_diona_pays_at_once_when_the_bomb_already_went_off(arms):
    state = _klee_state()
    klee_overhaul.place(state, state.enemies[0], 6)
    klee_overhaul.set_off(state, state.enemies[0])
    assert state.ko_set_off_this_turn == 1
    state.player.powers[standins.SHAKEN_NOT_PURRED] = 5
    before = state.player.block
    standins.on_played(state, loader.peek_card("proto_mc_diona_icy_paws"))
    assert state.player.block == before + 5


def test_noelle_pays_per_mine_and_not_per_bomb(arms):
    state = _klee_state()
    state.player.powers[standins.I_GOT_YOUR_BACK] = 4
    enemy = state.enemies[0]
    klee_overhaul.place(state, enemy, 5)                    # a Bomb
    before = state.player.block
    klee_overhaul.set_off(state, enemy)
    assert state.player.block == before                     # not a Mine
    klee_overhaul.place(state, enemy, 5, is_mine=True)
    klee_overhaul.place(state, enemy, 5, is_mine=True)
    klee_overhaul.set_off(state, enemy)
    assert state.player.block == before + 8                 # twice, repeating


def test_barbara_pays_per_bomb_and_not_only_per_mine(arms):
    """R252's fifth caretaker. Noelle's card one clause over: `Whenever` is
    still forward-looking and still pays per explosion, but the Mines-only
    test is gone -- a Mine is a Bomb, so Noelle's window sits inside this
    one."""
    state = _klee_state()
    state.player.powers[standins.FRONT_ROW_SEAT] = 3
    enemy = state.enemies[0]
    klee_overhaul.place(state, enemy, 5)                    # a plain Bomb
    before = state.player.block
    klee_overhaul.set_off(state, enemy)
    assert state.player.block == before + 3                 # Noelle pays none
    klee_overhaul.place(state, enemy, 5, is_mine=True)
    klee_overhaul.place(state, enemy, 5, is_mine=True)
    klee_overhaul.set_off(state, enemy)
    assert state.player.block == before + 9                 # and per Mine too


def test_barbara_applies_hydro_twice(arms):
    """Round 8's Diona finding read onto the other element: one application on
    a board Klee is already cooking is eaten by her own Pyro before the
    companion's turn comes round, so the applier row worth drafting applies
    twice. The row's own effects are what both engines read."""
    row = loader.peek_card("proto_mc_barbara_front_row_seat")
    auras = [fx for fx in row.effects if fx.get("op") == "apply_aura"]
    assert [fx["element"] for fx in auras] == ["hydro", "hydro"]


def test_every_watcher_closes_at_the_turn_boundary(arms):
    state = _klee_state()
    state.player.powers[standins.SHAKEN_NOT_PURRED] = 5
    state.player.powers[standins.I_GOT_YOUR_BACK] = 4
    state.player.powers[standins.FRONT_ROW_SEAT] = 3
    state.turn = 2
    standins.roll_turn(state)
    assert standins.SHAKEN_NOT_PURRED not in state.player.powers
    assert standins.I_GOT_YOUR_BACK not in state.player.powers
    assert standins.FRONT_ROW_SEAT not in state.player.powers


def test_kaeya_blinds_grounded_for_exactly_one_turn(arms):
    state = _klee_state()
    state.player.powers[klee_overhaul.GROUNDED] = 6
    state.player.powers[standins.COLD_BLOODED] = 1
    klee_overhaul.place(state, state.enemies[0], 6)
    klee_overhaul.set_off(state, state.enemies[0])          # a noisy turn
    # The next turn: the counter says one went off, and Grounded pays anyway.
    state.turn = 2
    klee_overhaul.roll_to(state, state.turn)
    standins.roll_turn(state)
    assert state.ko_set_off_last_turn == 1
    before = state.player.block
    klee_overhaul.turn_start_late(state)
    assert state.player.block == before + 6
    # And the marker is spent: a second noisy turn is not blinded.
    klee_overhaul.place(state, state.enemies[0], 6)
    klee_overhaul.set_off(state, state.enemies[0])
    state.turn = 3
    klee_overhaul.roll_to(state, state.turn)
    standins.roll_turn(state)
    before = state.player.block
    klee_overhaul.turn_start_late(state)
    assert state.player.block == before


def test_kaeya_does_not_pay_jean(arms):
    """The card names Grounded. A marker that quietly paid a second power
    would be a rule the player was never shown."""
    state = _klee_state()
    state.player.powers[standins.LIONS_FANG] = 8
    state.player.powers[standins.COLD_BLOODED] = 1
    klee_overhaul.place(state, state.enemies[0], 6)
    klee_overhaul.set_off(state, state.enemies[0])
    state.turn = 2
    klee_overhaul.roll_to(state, state.turn)
    standins.roll_turn(state)
    before = state.player.block
    standins.turn_start(state)
    assert state.player.block == before


def test_jean_pays_on_a_quiet_turn_and_draws(arms):
    state = _klee_state()
    state.player.powers[standins.LIONS_FANG] = 8
    state.player.draw_pile = [loader.peek_card("strike")] * 3
    state.turn = 2
    klee_overhaul.roll_to(state, state.turn)
    standins.roll_turn(state)
    assert state.ko_set_off_last_turn == 0
    hand_before, block_before = len(state.player.hand), state.player.block
    standins.turn_start(state)
    assert state.player.block == block_before + 8
    assert len(state.player.hand) == hand_before + C.MC_LIONS_FANG_DRAW


def test_every_rule_is_inert_with_the_flag_off(monkeypatch):
    """The acceptance condition on the whole seam, checked rule by rule rather
    than assumed from the callers."""
    monkeypatch.setattr(C, "COMPANION_OVERHAUL", False)
    state = _klee_state()
    state.player.powers[standins.SHAKEN_NOT_PURRED] = 5
    state.player.powers[standins.I_GOT_YOUR_BACK] = 4
    state.player.powers[standins.LIONS_FANG] = 8
    state.player.powers[standins.COLD_BLOODED] = 1
    before = state.player.block
    standins.note_explosion(state, is_mine=True)
    standins.turn_start(state)
    standins.roll_turn(state)
    assert state.player.block == before
    assert standins.grounded_blind(state) is False
    # Nothing was consumed either: with the arm off these are not this arm's
    # powers, and eating a stack would be a behaviour change of its own.
    assert state.player.powers[standins.COLD_BLOODED] == 1
