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

def test_fontaine_sheet_loads_ratified_roster():
    cards = _fontaine_cards()
    shared = [c for c in cards if not c.guest_star]
    guests = [c for c in cards if c.guest_star]
    # 4 characters x 3-card kits (kickoff §10) + Guest Star set v0.1.
    assert len(shared) == 12
    assert {c.character for c in shared} == set(FONTAINE_4STARS)
    for char in FONTAINE_4STARS:
        assert sum(1 for c in shared if c.character == char) == 3
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
    # No banner participation either: Fontaine has no *designed* shared
    # 5-stars yet, and the guests must not stand in for them.
    assert rewards.five_star_roster("fontaine") == []


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
    assert st.player.block == 3
    assert st.player.powers["block_next_turn"] == 3
    combat._player_turn(st, lambda s: None)   # resets block, then trigger
    assert st.player.block == 3
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
    assert hp_before - e.hp == 8 + C.SHATTER_DAMAGE + 4


def test_backstroke_applies_no_element():
    # Budget guard: the flag is explicit on the sheet; the hit must not
    # apply cryo even under a catalyst-cadence player.
    st = make_state(enemies=[make_enemy(hp=200)])
    st.player.cadence = "catalyst"
    st.player.element = "pyro"
    effects.resolve_card(st, loader.get_card("freminet_pressurized_floe"))
    assert st.enemies[0].aura is None
