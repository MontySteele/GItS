"""Fontaine companion set v0.1 (Furina sprint 1, kickoff doc §10).

Sheet-structure locks: the ratified roster and the Cryo application
budget are enforced here so a later card edit answers to the kickoff's
convergence levers, not to a review. Plus the three DSL additions the
sheet flagged inline (reaction_triggered_this_turn, block_next_turn,
shatter_bonus) and the Guest Star reward exclusions.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects
from tier0.tests.conftest import make_enemy, make_state

FONTAINE_4STARS = ("chevreuse", "lynette", "charlotte", "freminet")


def _fontaine_cards():
    return [c for c in loader._card_index().values()
            if c.nation == "fontaine"]


# --- sheet structure ---

FONTAINE_5STARS = ("navia", "clorinde", "neuvillette", "arlecchino")


def test_fontaine_sheet_loads_ratified_roster():
    cards = _fontaine_cards()
    shared = [c for c in cards if not c.guest_star]
    bench = [c for c in shared if c.star == 4]
    rares = [c for c in shared if c.star == 5]
    guests = [c for c in cards if c.guest_star]

    # 4 characters x 3-card kits (kickoff §10).
    assert len(bench) == 12
    assert {c.character for c in bench} == set(FONTAINE_4STARS)
    for char in FONTAINE_4STARS:
        assert sum(1 for c in bench if c.character == char) == 3

    # 5-star Rares, added 2026-07-25 (R64). §4.2 is EXACTLY ONE CARD each --
    # asserted per character rather than on the total, because four cards
    # from three characters would also sum to four.
    assert {c.character for c in rares} == set(FONTAINE_5STARS)
    for char in FONTAINE_5STARS:
        assert sum(1 for c in rares if c.character == char) == 1
    assert all(c.rarity == "rare" for c in rares)
    # The roster now EXCEEDS BANNER_FEATURED_SLOTS, which is the whole point of
    # the sprint that added them: it is what makes the banner selective.
    assert len(rares) > C.BANNER_FEATURED_SLOTS

    assert {c.character for c in guests} == {"neuvillette"}
    assert 2 <= len(guests) <= 3          # kickoff §9: 2-3 Neuvillette cards


def test_character_field_derivation():
    # Companion sheets: id prefix. Personal sheets: filename. Explicit wins.
    assert loader.get_card("fischl_nightrider").character == "fischl"
    assert loader.get_card("prune_witch_hunt").character == "prune"
    assert loader.get_card("kaboom").character == "klee"
    assert loader.get_card("guest_neuvillette_tears").character == "neuvillette"
    # Engine test pools carry no character: invalid Spotlight targets.
    assert loader.get_card("strike").character is None


def test_cryo_application_budget():
    """Convergence lever 1: Charlotte and Freminet each get exactly ONE
    Cryo-applying card; the sheet must not quietly grow a second."""
    for char in ("charlotte", "freminet"):
        appliers = []
        for c in _fontaine_cards():
            if c.character != char:
                continue
            for fx in c.effects:
                if (fx.get("applies_element")
                        or (fx.get("op") == "apply_aura"
                            and fx.get("element") == "cryo")):
                    appliers.append(c.id)
                    break
        assert len(appliers) == 1, (char, appliers)


def test_healing_law_holds_on_fontaine_sheet():
    # R8 conjunctive law, by construction: the set contains no heal op at
    # all (sub-Rare sustain routes through Block -- Charlotte/droplets
    # conversions). The global sweep in test_errata also covers this; the
    # sheet-local assertion documents the by-construction claim.
    for c in _fontaine_cards():
        assert not any(fx.get("op") == "heal" for fx in c.effects), c.id


# --- Guest Star scoping ---

def test_guest_star_never_in_shared_rewards():
    from tier05 import rewards
    assert all(not c.guest_star
               for cs in rewards.companion_pool().values() for c in cs)
    # No banner participation either. This used to assert the roster was
    # EMPTY, which proved the exclusion only because Fontaine had no designed
    # shared 5-stars -- a vacuous pass that would have gone on reading green if
    # a guest had leaked in the moment real Rares landed. Now that four exist
    # (R64), assert the separation directly: the roster is exactly the shared
    # Rares, and no guest id appears in it.
    roster = rewards.five_star_roster("fontaine")
    assert {c.id for c in roster} == {
        "navia_cannon_fire_support",
        "clorinde_impale_the_night",
        "neuvillette_ancient_sea_authority",
        "arlecchino_masque_red_death",
    }
    assert all(not c.guest_star and c.personal_pool is None for c in roster)
    # D2 in the flesh: Neuvillette is in the banner roster AND has cameos, and
    # they are different cards.
    guest_ids = {c.id for c in _fontaine_cards() if c.guest_star}
    assert guest_ids and not (guest_ids & {c.id for c in roster})


def test_personal_pool_not_offered_cross_character():
    """Probed on a REAL character. This used the invented id
    "furina_probe" until 2026-07-21; once card ownership became required
    (rewards.character_pool) that id had an empty pool, so the assertions
    below passed vacuously against zero offers."""
    from tier05 import rewards
    rng = random.Random(7)
    offered = {c.id for _ in range(300)
               for c in rewards.roll_rewards(rng, "furina")}
    assert offered, "empty offer set would make this test vacuous"
    assert "prune_witch_hunt" not in offered
    # Checked on the guest_star FLAG, not an id prefix. The prefix form
    # ("guest_") silently false-positives on Furina's own uncommon
    # "The Guest List" (guest_list) -- it only ever passed because the
    # probe character had no Furina cards to offer in the first place.
    assert not any(loader.get_card(cid).guest_star for cid in offered)
    # The leak this file was written to catch, stated directly: a reward
    # screen only ever offers cards the character owns (companions aside,
    # which are a shared pool by design).
    assert all(loader.get_card(cid).character == "furina"
               for cid in offered
               if not loader.get_card(cid).is_companion)


def test_unowned_character_pool_fails_loudly():
    """The rare->uncommon->common fallback used to run off the end and
    raise a bare KeyError from a dict literal. An empty pool is a config
    error and must say so."""
    from tier05 import rewards
    with pytest.raises(ValueError, match="no draftable cards"):
        rewards.roll_rewards(random.Random(1), "furina_probe")


# --- DSL: reaction_triggered_this_turn (Chevreuse) ---

def test_vanguards_valor_scales_on_any_reaction():
    st = make_state(enemies=[make_enemy(hp=200)])
    card = loader.get_card("chevreuse_vanguards_valor")
    st.reactions_this_turn = 0
    effects.resolve_card(st, card)
    assert st.player.powers.get("next_attack_up", 0) == 3   # base only
    st.player.powers.pop("next_attack_up")
    # Any reaction this turn -- swirl by another card counts (the ruling:
    # never a dead draw off-Pyro/Electro).
    e = st.enemies[0]
    effects.resolve_card(st, loader.get_card("dahlia_sacramental_shower"))
    effects.resolve_card(st, loader.get_card("sucrose_gust"))
    assert st.reactions_this_turn > 0
    effects.resolve_card(st, card)
    assert st.player.powers.get("next_attack_up", 0) == 6   # base + rider


def test_reactions_this_turn_resets_at_turn_start():
    st = make_state(enemies=[make_enemy(hp=200)])
    st.reactions_this_turn = 3
    combat._player_turn(st, lambda s: None)
    assert st.reactions_this_turn == 0


# --- DSL: block_next_turn (Charlotte) ---

def test_frosthelm_blocks_now_and_next_turn():
    st = make_state(enemies=[make_enemy(hp=200)])
    effects.resolve_card(st, loader.get_card("charlotte_enduring_frosthelm"))
    assert st.player.block == 4
    assert st.player.powers["block_next_turn"] == 4
    combat._player_turn(st, lambda s: None)   # resets block, then trigger
    assert st.player.block == 4
    assert "block_next_turn" not in st.player.powers   # consumed, no carry


# --- DSL: shatter_bonus (Freminet) ---

def test_shatter_bonus_adds_to_shatter_damage():
    st = make_state(enemies=[make_enemy(hp=200)])
    e = st.enemies[0]
    # Freeze: hydro aura + cryo attack (Pers), then cash with the untagged
    # attack (Backstroke) under Shattering Pressure.
    effects.resolve_card(st, loader.get_card("guest_neuvillette_tears"))
    effects.resolve_card(st, loader.get_card("freminet_pers_deploy"))
    assert e.frozen
    effects.resolve_card(st, loader.get_card("freminet_shattering_pressure"))
    hp_before = e.hp
    effects.resolve_card(st, loader.get_card("freminet_pressurized_floe"))
    assert not e.frozen
    shatters = [ev for ev in st.log if ev["event"] == "damage"
                and ev.get("source") == "shatter"]
    assert shatters and shatters[-1]["base"] == C.SHATTER_DAMAGE + 4
    assert hp_before - e.hp == 10 + C.SHATTER_DAMAGE + 4


def test_backstroke_applies_no_element():
    # Budget guard: the flag is explicit on the sheet; the hit must not
    # apply cryo even under a catalyst-cadence player.
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.cadence = "catalyst"
    st.player.element = "pyro"
    effects.resolve_card(st, loader.get_card("freminet_pressurized_floe"))
    assert st.enemies[0].aura is None


# --- 5-star Rares (R64, 2026-07-25): the four new powers ---

def _play(st, card_id):
    """play_card goes through the real hand/energy path -- the companion hook
    being tested lives there, not in resolve_card."""
    card = loader.get_card(card_id)
    st.player.hand.append(card)
    st.player.energy = 9
    combat.play_card(st, card)
    return card


def test_cannon_fire_support_pays_on_every_companion_play():
    """Navia's trigger is the CARD TYPE, not an element -- deliberately, so
    nothing here pre-commits Crystallize (Zhongli's archetype owns it)."""
    st = make_state(enemies=[make_enemy(hp=200)])
    _play(st, "navia_cannon_fire_support")
    # Her own play does not pay itself: the hook runs before resolution, so the
    # power is not up yet when her own card play is observed.
    assert st.player.block == 0
    assert st.player.powers["cannon_fire_support"] == 3

    _play(st, "lynette_box_trick")
    assert st.player.block == 3
    _play(st, "charlotte_snappy_silhouette")
    assert st.player.block == 6


def test_cannon_fire_support_ignores_non_companion_cards():
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.powers["cannon_fire_support"] = 3
    _play(st, "kaboom")                                  # Klee's own card
    assert st.player.block == 0


def test_night_vigil_pays_only_against_an_aura_and_only_on_attacks():
    """Clorinde reads the board before she moves. Same hook and same ordering
    as Albedo's solar_isotoma -- read BEFORE the hit consumes the aura."""
    st = make_state(enemies=[make_enemy(hp=300)])
    e = st.enemies[0]
    st.player.powers["night_vigil"] = 3

    # No aura: the rider is worth nothing.
    before = e.hp
    effects.resolve_card(st, loader.get_card("kaeya_frostgnaw"))   # 6, cryo
    assert before - e.hp == 6
    assert e.aura == "cryo"

    # Aura up: the SAME card now pays +3, and the rider is collected even
    # though this hit reacts the aura away.
    before = e.hp
    effects.resolve_card(st, loader.get_card("chevreuse_interdiction_fire"))
    melt = C.MELT_MULT                    # pyro onto cryo
    assert before - e.hp == int((7 + 3) * melt)


def test_night_vigil_does_not_pay_bombs_or_summons():
    """'Your Attacks' means card Attacks. A bomb tick is not one."""
    st = make_state(enemies=[make_enemy(hp=300)])
    e = st.enemies[0]
    st.player.powers["night_vigil"] = 5
    e.aura = "hydro"
    before = e.hp
    effects.deal_damage_to_enemy(st, e, 10, element=None, source="bomb")
    assert before - e.hp == 10


def test_ancient_sea_authority_extends_applied_and_refreshed_auras():
    st = make_state(enemies=[make_enemy(hp=200)])
    e = st.enemies[0]
    effects.resolve_card(st, loader.get_card("guest_neuvillette_tears"))
    assert e.aura_turns_left == C.AURA_DURATION_TURNS

    st2 = make_state(enemies=[make_enemy(hp=200)])
    e2 = st2.enemies[0]
    effects.resolve_card(
        st2, loader.get_card("neuvillette_ancient_sea_authority"))
    effects.resolve_card(st2, loader.get_card("guest_neuvillette_tears"))
    assert e2.aura_turns_left == C.AURA_DURATION_TURNS + 1
    # Refresh must agree with application -- the reason aura_duration() is a
    # function rather than the constant read at three call sites.
    e2.aura_turns_left = 1
    effects.resolve_card(st2, loader.get_card("guest_neuvillette_tears"))
    assert e2.aura_turns_left == C.AURA_DURATION_TURNS + 1


def test_ancient_sea_authority_applies_no_element_of_its_own():
    """It is authority over water, not more water. If it applied Hydro it
    would re-open the mass-Frozen watchlist the guest card deliberately
    priced with self-damage."""
    st = make_state(enemies=[make_enemy(hp=200)])
    effects.resolve_card(
        st, loader.get_card("neuvillette_ancient_sea_authority"))
    assert all(e.aura is None for e in st.enemies)


def test_masque_of_the_red_death_buffs_attacks_and_blocks_healing():
    st = make_state(enemies=[make_enemy(hp=300)], hp=40)
    e = st.enemies[0]
    effects.resolve_card(st, loader.get_card("arlecchino_masque_red_death"))
    before = e.hp
    effects.resolve_card(st, loader.get_card("kaeya_frostgnaw"))   # 6 base
    assert before - e.hp == 6 + 4

    # The Bond of Life half: healing is offered and refused, not silently lost.
    st.player.hp = 40
    effects.resolve_card(st, loader.get_card("singer_of_many_waters"))
    assert st.player.hp == 40
    blocked = [ev for ev in st.log if ev["event"] == "heal_blocked"]
    assert blocked and blocked[-1]["by"] == "masque_red_death"


def test_masque_does_not_buff_bombs():
    st = make_state(enemies=[make_enemy(hp=300)])
    e = st.enemies[0]
    st.player.powers["masque_red_death"] = 4
    before = e.hp
    effects.deal_damage_to_enemy(st, e, 10, element=None, source="bomb")
    assert before - e.hp == 10
