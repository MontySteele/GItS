"""KLEE'S FOUR COVEN PERSONALS -- the flag, and both sides of it (R236).

The source is the approved workshop `companion-workshop-mondstadt-2026-09-01.md`
sec.4 and the Prune entry in its sec.3 (a Paper artefact on the
companion-workshop branch, not in this tree). Same arm and same flag as
`test_companion_overhaul.py` beside it, so the FIRST section is the same one
that matters: with `C.COMPANION_OVERHAUL` off nothing here exists, and that is
an acceptance condition rather than an intention.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). These are
shape assertions about an engine, not numbers about a game.
"""

from pathlib import Path

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, companion_coven, effects, klee_overhaul
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards

PRUNE = "proto_mc_prune_hexhunter_chime"
SAYU = "proto_mc_sayu_silencers_secret"
QIQI = "proto_mc_qiqi_herald_of_frost"
YAOYAO = "proto_mc_yaoyao_yuegui_throwing_mode"


def _caches_clear():
    loader._card_prototype.cache_clear()
    rewards._companion_roster.cache_clear()
    rewards.companion_pool.cache_clear()
    rewards.five_star_roster.cache_clear()
    rewards.designed_nations.cache_clear()


@pytest.fixture
def overhaul(monkeypatch):
    """The companion arm ON, with every id-resolving cache cleared."""
    _caches_clear()
    monkeypatch.setattr(C, "COMPANION_OVERHAUL", True)
    yield
    _caches_clear()


@pytest.fixture
def both_arms(monkeypatch):
    """The companion arm AND the Klee overhaul, which is what the two
    Bomb-speaking rows need: a Bomb is the Klee arm's rule."""
    _caches_clear()
    monkeypatch.setattr(C, "COMPANION_OVERHAUL", True)
    monkeypatch.setattr(C, "KLEE_OVERHAUL", True)
    yield
    _caches_clear()


def _klee_state(**kw):
    st = make_state(**kw)
    st.player.character_id = "klee"
    return st


def _pool_ids(pool):
    return {c.id for cards in pool.values() for c in cards}


# ---------------------------------------------------------------------------
# THE FLAG IS OFF, AND THAT IS THE ACCEPTANCE CONDITION
# ---------------------------------------------------------------------------

def test_the_flag_ships_off():
    assert C.COMPANION_OVERHAUL is False


def test_flag_off_no_coven_row_can_be_offered():
    offerable = _pool_ids(rewards.companion_pool())
    assert not (set(C.COVEN_PERSONAL_POOL_IDS) & offerable)


def test_flag_off_prunes_shipped_row_is_still_offerable():
    assert "prune_witch_hunt" in _pool_ids(rewards.companion_pool())


def test_flag_off_the_coven_hooks_are_no_ops():
    """Every function in the module returns before touching anything, asserted
    against a state that CARRIES the coven's powers -- a hook that ran with the
    flag off would be a silent second rule set on every shipped run."""
    st = _klee_state()
    st.player.powers.update({"cvn_hexhunter_chime": 1,
                             "cvn_herald_of_frost": 3, "cvn_yuegui": 3})
    before = (dict(st.player.powers), st.player.block,
              [e.hp for e in st.enemies], [len(e.ko_charges) for e in st.enemies])
    companion_coven.turn_start(st)
    companion_coven.turn_end(st)
    companion_coven.note_swirl(st, "hydro")
    assert st.cvn_swirl_element == ""
    assert (dict(st.player.powers), st.player.block,
            [e.hp for e in st.enemies],
            [len(e.ko_charges) for e in st.enemies]) == before


def test_flag_off_an_explosion_is_still_pyro():
    """The one shipped path this arm reaches into. `bomb_element` is read at
    every explosion, so its flag-off answer is the acceptance condition on
    `klee_overhaul._explode` staying what it was."""
    assert companion_coven.bomb_element(_klee_state()) == "pyro"


def test_flag_off_a_five_star_personal_clause_is_unreachable():
    """`rewards._banner_filtered` grew a `personal_pool` clause for Qiqi. It
    cannot fire on any shipped tree, because no shipped companion is both a
    five-star and a Personal -- pinned rather than assumed, so the day one
    ships this test asks about it."""
    both = [c for c in loader._card_index().values()
            if c.is_companion and c.star == 5 and c.personal_pool is not None]
    assert both == []


# ---------------------------------------------------------------------------
# THE FLAG IS ON: THE FOUR ROWS ARE KLEE'S, AND ONLY KLEE'S
# ---------------------------------------------------------------------------

def test_flag_on_every_coven_row_resolves_to_a_klee_personal(overhaul):
    for cid in C.COVEN_PERSONAL_POOL_IDS:
        card = loader.peek_card(cid)
        assert card.is_companion, cid
        assert card.personal_pool == "klee", cid
        assert card.rarity in C.RARITY_ODDS, cid


def test_flag_on_the_coven_is_in_the_offerable_pool(overhaul):
    assert set(C.COVEN_PERSONAL_POOL_IDS) <= _pool_ids(rewards.companion_pool())


def test_flag_on_the_coven_carries_its_characters_real_nations(overhaul):
    nations = {cid: loader.peek_card(cid).nation
               for cid in C.COVEN_PERSONAL_POOL_IDS}
    assert nations[PRUNE] == "mondstadt"
    assert nations[SAYU] == "inazuma"
    assert nations[QIQI] == "liyue"
    assert nations[YAOYAO] == "liyue"


def test_flag_on_the_coven_is_not_on_the_banner(overhaul):
    """Qiqi is a five-star character, and `five_star_roster` excludes Personals
    by name -- a Personal is Klee's kit, not a draw. So no banner features her
    AND `_banner_filtered` must not gate her, which is the pair of facts that
    keeps her offerable at all."""
    assert loader.peek_card(QIQI).star == 5
    assert QIQI not in {c.id for c in rewards.five_star_roster("liyue")}
    kept = rewards._banner_filtered([loader.peek_card(QIQI)], frozenset())
    assert [c.id for c in kept] == [QIQI]


def test_flag_on_the_chime_supersedes_prunes_shipped_row(overhaul):
    """R236: under the arm the Chime IS Prune's card. The supersession is the
    replacement's own nation filter -- `prune_witch_hunt` is a Mondstadt
    companion the pool lists do not name -- so there is no second rule to
    remember and nothing to keep in step."""
    offerable = _pool_ids(rewards.companion_pool())
    assert "prune_witch_hunt" not in offerable
    assert PRUNE in offerable


# ---------------------------------------------------------------------------
# WHAT EACH CARD DOES
# ---------------------------------------------------------------------------

def test_the_chime_gives_the_next_bomb_the_swirled_element(both_arms):
    st = _klee_state()
    enemy = st.enemies[0]
    enemy.aura = "hydro"
    st.cvn_swirl_element = "hydro"
    st.player.powers["cvn_hexhunter_chime"] = 1
    assert companion_coven.bomb_element(st) == "hydro"


def test_the_chime_is_spent_by_ONE_bomb(both_arms):
    """"The next Bomb", singular. A three-charge Set off is three explosions
    and only the first of them carries the element."""
    st = _klee_state()
    st.cvn_swirl_element = "cryo"
    st.player.powers["cvn_hexhunter_chime"] = 1
    assert companion_coven.bomb_element(st) == "cryo"
    assert companion_coven.bomb_element(st) == "pyro"
    assert "cvn_hexhunter_chime" not in st.player.powers


def test_the_chime_with_no_swirl_this_turn_is_pyro(both_arms):
    st = _klee_state()
    st.player.powers["cvn_hexhunter_chime"] = 1
    assert companion_coven.bomb_element(st) == "pyro"


def test_a_bomb_with_no_chime_is_pyro(both_arms):
    st = _klee_state()
    st.cvn_swirl_element = "electro"
    assert companion_coven.bomb_element(st) == "pyro"


def test_the_chime_does_not_survive_the_turn(both_arms):
    st = _klee_state()
    st.player.powers["cvn_hexhunter_chime"] = 1
    companion_coven.turn_end(st)
    assert "cvn_hexhunter_chime" not in st.player.powers


def test_the_swirl_latch_is_written_at_the_reaction_site(both_arms):
    """The latch is unconditional, because the Attack that arms the Chime
    swirls BEFORE it arms. Written at the one site the engine resolves a
    reaction, so it cannot disagree with the Swirl counter beside it."""
    st = _klee_state()
    effects.companion_overhaul_reaction(st, st.enemies[0], "swirl", "hydro")
    assert st.cvn_swirl_element == "hydro"
    effects.companion_overhaul_reaction(st, st.enemies[0], "swirl", "cryo")
    assert st.cvn_swirl_element == "cryo"          # LAST WINS
    effects.companion_overhaul_reaction(st, st.enemies[0], "vaporize", "hydro")
    assert st.cvn_swirl_element == "cryo"          # not a Swirl, not a latch


def test_the_swirl_latch_is_turn_scoped(both_arms):
    """Cleared on the same line as the Swirl COUNT it rides beside, so the two
    can never disagree about which turn it is."""
    src = (Path(combat.__file__).read_text(encoding="utf-8")
           .split("state.mi_swirls_this_turn = 0")[1][:400])
    assert 'state.cvn_swirl_element = ""' in src


def test_an_exploding_bomb_reads_the_chime(both_arms):
    """End to end through the real explosion, which is the only claim that
    matters: `_explode` is where rule 5's Pyro used to be a literal."""
    st = _klee_state()
    enemy = st.enemies[0]
    enemy.aura = "pyro"
    st.cvn_swirl_element = "hydro"
    st.player.powers["cvn_hexhunter_chime"] = 1
    klee_overhaul.place(st, enemy, 6)
    klee_overhaul.set_off(st, enemy)
    # Hydro on a Pyro aura is a Vaporize, which a Pyro explosion could not be.
    assert st.reactions_this_turn == 1


def test_the_herald_applies_cryo_twice_and_pays_block(overhaul):
    st = _klee_state()
    st.enemies = [make_enemy(hp=99)]
    st.player.powers["cvn_herald_of_frost"] = 3
    companion_coven.turn_start(st)
    assert st.player.block == C.CVN_HERALD_BLOCK
    assert st.enemies[0].aura == "cryo"
    # PAY, THEN TICK: three turns means this one and two more.
    assert st.player.powers["cvn_herald_of_frost"] == 2


def test_the_heralds_second_application_is_a_real_second_hit(overhaul):
    """"Twice" is two applications at one body, which is what lets the card be
    its own reaction: the first Cryo meets the Hydro standing, the second lands
    on the aura the first left."""
    st = _klee_state()
    st.enemies = [make_enemy(hp=99)]
    st.enemies[0].aura = "hydro"
    st.player.powers["cvn_herald_of_frost"] = 1
    companion_coven.turn_start(st)
    assert st.reactions_this_turn == 1             # Frozen, off the first
    assert st.enemies[0].aura == "cryo"            # left by the second


def test_the_herald_expires(overhaul):
    st = _klee_state()
    st.player.powers["cvn_herald_of_frost"] = 1
    companion_coven.turn_start(st)
    assert "cvn_herald_of_frost" not in st.player.powers


def test_yuegui_places_a_bomb_at_the_end_of_the_turn(both_arms):
    st = _klee_state()
    st.enemies = [make_enemy(hp=99)]
    st.player.powers["cvn_yuegui"] = 3
    companion_coven.turn_end(st)
    charges = st.enemies[0].ko_charges
    assert [c.size for c in charges] == [C.CVN_YUEGUI_BOMB_SIZE]
    assert not charges[0].is_mine
    assert st.player.powers["cvn_yuegui"] == 2


def test_yuegui_ticks_even_where_the_bomb_cannot_land(overhaul):
    """The companion arm on and the KLEE arm off: a Bomb is that arm's rule, so
    nothing is placed -- and the card's three turns still pass, which is what
    keeps the power from becoming permanent on a board it could not reach."""
    st = _klee_state()
    st.enemies = [make_enemy(hp=99)]
    st.player.powers["cvn_yuegui"] = 2
    companion_coven.turn_end(st)
    assert st.enemies[0].ko_charges == []
    assert st.player.powers["cvn_yuegui"] == 1


def test_yuegui_expires(both_arms):
    st = _klee_state()
    st.player.powers["cvn_yuegui"] = 1
    companion_coven.turn_end(st)
    assert "cvn_yuegui" not in st.player.powers


# ---------------------------------------------------------------------------
# THE ROWS THEMSELVES
# ---------------------------------------------------------------------------

def test_sayus_row_is_the_shipped_grammar(overhaul):
    """No power and no new op: a Swirl, a Block and the `bomb_went_off_this_turn`
    predicate the Klee arm already reads."""
    ops = [fx["op"] for fx in loader.peek_card(SAYU).effects]
    assert ops == ["swirl", "block", "conditional"]
    assert loader.peek_card(SAYU).effects[-1]["if"] == "bomb_went_off_this_turn"


def test_the_bomb_predicate_answers_for_sayu(both_arms):
    st = _klee_state()
    assert effects._predicate(st, "bomb_went_off_this_turn") is False
    klee_overhaul.place(st, st.enemies[0], 4)
    klee_overhaul.set_off(st, st.enemies[0])
    assert effects._predicate(st, "bomb_went_off_this_turn") is True


def test_every_coven_row_carries_an_upgrade(overhaul):
    """`EB-315`: an arm row has an upgrade or says why not, and none of the
    four says why not. Three take the Prototype-stage rule off their own
    printed numbers; Prune DECLARES hers, because the derived default would
    also bump the Chime's marker stack -- a number the face does not print,
    and one that would arm the rider twice."""
    from tier0.content import upgrades
    for cid in C.COVEN_PERSONAL_POOL_IDS:
        row = loader.peek_card(cid)
        assert row.no_upgrade is None, cid
        declared = row.upgrade or {}
        derived = upgrades.prototype_default_delta(
            cid, row.cost, row.effects, exhaust=row.exhaust)
        assert declared or derived, cid
    prune = loader.peek_card(PRUNE)
    assert prune.upgrade == {"damage": upgrades.PROTOTYPE_DAMAGE_DELTA}
