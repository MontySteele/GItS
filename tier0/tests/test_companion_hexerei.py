"""THE HEXEREI FAMILY STAND-INS -- the four rules, the hand-off, the flag.

Four Klee-only cards handed to Klee in place of four Hexerei Universals (R236
sec.3), on the stand-in seam (deleted 2026-10-08, project review pick 3; none
of the four is a stand-in since 2026-10-03). This file owns what these four
DO:

  1. EACH RULE FIRES ON ITS OWN EVENT AND ON NO OTHER. Albedo pays on any
     reaction, Sucrose only on one that deals damage, Fischl only on an Electro
     one, Nicole only on a card that counts as a Companion (a Hexerei card
     until R276 pick 2).
  2. KLEE IS HANDED EACH ONE IN PLACE OF ITS UNIVERSAL, and nobody else is.
  3. FLAG OFF, NOTHING HAPPENS -- checked on each function rather than assumed
     from the callers.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). These are
shape assertions about an engine, not numbers about a game.
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import companion_hexerei as hexerei
from tier0.engine import effects, reactions
from tier0.tests.conftest import make_enemy, make_state

# THE SHIPPED WORLD, NAMED (legacy cleanup stage 3, 2026-10-01): the sim
# defaults to the current kits, and these pins read the shipped ones.

#: The slice, and the Universal each row stands in for.
FAMILY = {
    # The Klee status package (2026-10-01): Dust of Purification is Albedo's
    # stand-in now; Tectonic Tide's Power left with legacy cleanup stage 5.
    "proto_mc_albedo_dust_of_purification": "proto_mc_albedo_solar_isotoma",
    "proto_mc_fischl_sinful_hex": "proto_mc_fischl_nightrider",
    "proto_mc_nicole_ladder_of_ascent": "proto_mc_nicole_revelation",
    "proto_mc_sucrose_mollis_favonius": "proto_mc_sucrose_gust",
}


def _caches_clear():
    from tier05 import rewards

    loader.reset_arm_caches()
    rewards._companion_roster.cache_clear()
    rewards.companion_pool.cache_clear()
    rewards.five_star_roster.cache_clear()
    rewards.designed_nations.cache_clear()


@pytest.fixture
def overhaul(monkeypatch):
    _caches_clear()
    yield
    _caches_clear()


def _state():
    state = make_state(enemies=[make_enemy(hp=400)])
    state.player.character_id = "klee"
    state.turn = 1
    return state


def _react(state, trigger, aura, damage=10, enemy=None):
    """Stand `aura` on an enemy and hit it with `trigger`, which reacts.

    The whole pipeline, not a hand-called hook: the readers under test hang off
    `reactions._react`, so a test that called them directly would prove they
    work and not that they are reached.
    """
    enemy = enemy or state.enemies[0]
    reactions.apply_aura(state, enemy, aura, "test")
    effects.deal_damage_to_enemy(state, enemy, damage, element=trigger,
                                 source="attack")
    return enemy


def _paid(state, event):
    return [e for e in state.log if e.get("event") == event]


# --- the sheet ---------------------------------------------------------------

def test_the_four_left_the_stand_in_seam(overhaul):
    """The Klee-only companions (2026-10-03,
    review/active/mondstadt-companions-2026-10-03.md sec.4): none of the four
    is a stand-in any more. Fischl's, Sucrose's and Nicole's are shared
    Universals; Albedo's Dust of Purification is in Klee's own draftable
    pool. Each is still a Companion card and replaces nothing."""
    for cid in FAMILY:
        card = loader.peek_card(cid)
        assert card.personal_pool is None, cid
        assert card.replaces is None, cid
        assert card.is_companion, cid
    shared = set(FAMILY) - {"proto_mc_albedo_dust_of_purification"}
    assert shared <= set(C.MONDSTADT_OVERHAUL_POOL_IDS)
    assert "proto_mc_albedo_dust_of_purification" in C.KLEE_OVERHAUL_POOL_IDS


# --- Albedo, Tectonic Tide (the Power; its row was cut 2026-10-01) -----------

# --- Sucrose, Mollis Favonius ------------------------------------------------

@pytest.mark.parametrize("trigger,aura", [
    ("hydro", "pyro"),          # vaporize   -- an amplifier
    ("cryo", "pyro"),           # melt       -- the other amplifier
    ("pyro", "electro"),        # overload   -- the splash
])
def test_sucrose_adds_to_a_reaction_that_deals_damage(overhaul, trigger, aura):
    state = _state()
    state.player.powers[hexerei.MOLLIS_FAVONIUS] = 4
    _react(state, trigger, aura)
    assert [e["amount"] for e in _paid(state, "mc_mollis_favonius")] == [4]


@pytest.mark.parametrize("trigger,aura", [
    ("anemo", "pyro"),          # swirl        -- spreads, deals nothing
    ("geo", "pyro"),            # crystallize  -- Block, deals nothing
    ("electro", "cryo"),        # superconduct -- Vulnerable, deals nothing
    ("hydro", "electro"),       # electrocharged -- a dot POWER, not damage
    ("cryo", "hydro"),          # frozen       -- control, deals nothing
])
def test_sucrose_adds_nothing_to_a_reaction_that_deals_nothing(
        overhaul, trigger, aura):
    """Durin's White boundary, and the card must keep it: "deal 4 additional
    damage" has nothing to add to a reaction whose own damage is zero."""
    state = _state()
    state.player.powers[hexerei.MOLLIS_FAVONIUS] = 4
    _react(state, trigger, aura)
    assert not _paid(state, "mc_mollis_favonius")


def test_sucrose_names_the_three_reactions_it_pays():
    """The Varka payoff round (2026-10-10): the face said "Elemental
    Reactions" and the code pays three (`CompanionHexerei.DamagingReactions`).
    Card, Power and table name the same three."""
    import re
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    words = ("[gold]Melt[/gold], [gold]Vaporize[/gold] and "
             "[gold]Overloaded[/gold] deal")
    card = loader.get_card("proto_mc_sucrose_mollis_favonius")
    sheet = (repo / "docs" / "prototype-surface.yaml").read_text(
        encoding="utf-8")
    row = sheet.split("id: proto_mc_sucrose_mollis_favonius", 1)[1]
    assert words in row.split("effects:", 1)[0]
    cs = (repo / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
          / "CompanionHexerei.cs").read_text(encoding="utf-8")
    table = re.search(r"DamagingReactions =\s*\{([^}]*)\}", cs).group(1)
    assert sorted(re.findall(r"Reaction\.(\w+)", table)) == [
        "Melt", "Overload", "Vaporize"]
    assert "[gold]Melt[/gold], [gold]Vaporize[/gold] and" in cs
    assert card is not None


def test_sucrose_pays_once_per_overload_and_not_once_per_splashed_body(
        overhaul):
    state = _state()
    state.enemies.append(make_enemy(hp=400, name="second"))
    state.enemies.append(make_enemy(hp=400, name="third"))
    state.player.powers[hexerei.MOLLIS_FAVONIUS] = 4
    reacted = _react(state, "pyro", "electro", enemy=state.enemies[0])
    paid = _paid(state, "mc_mollis_favonius")
    assert [e["target"] for e in paid] == [reacted.name]


def test_sucrose_closes_at_the_turn_end_whether_or_not_it_paid(overhaul):
    state = _state()
    state.player.powers[hexerei.MOLLIS_FAVONIUS] = 4
    state.player.powers[hexerei.SINFUL_HEX] = 5
    effects.companion_overhaul_turn_end(state)
    assert hexerei.MOLLIS_FAVONIUS not in state.player.powers
    assert hexerei.SINFUL_HEX not in state.player.powers


# --- Fischl, Undone Be Thy Sinful Hex ----------------------------------------

@pytest.mark.parametrize("trigger,aura", [
    ("pyro", "electro"),        # overload       -- Electro is the aura
    ("electro", "pyro"),        # overload       -- Electro is the trigger
    ("electro", "cryo"),        # superconduct
    ("hydro", "electro"),       # electrocharged
    ("anemo", "electro"),       # a Swirl OF Electro is an Electro reaction
])
def test_fischl_pays_on_any_reaction_with_electro_in_it(overhaul, trigger,
                                                        aura):
    state = _state()
    state.player.powers[hexerei.SINFUL_HEX] = 5
    _react(state, trigger, aura)
    assert _paid(state, "mc_sinful_hex")


@pytest.mark.parametrize("trigger,aura", [
    ("hydro", "pyro"),          # vaporize
    ("cryo", "pyro"),           # melt
    ("cryo", "hydro"),          # frozen
    ("anemo", "cryo"),          # a Swirl of something else
])
def test_fischl_is_silent_on_a_reaction_with_no_electro(overhaul, trigger,
                                                        aura):
    state = _state()
    state.player.powers[hexerei.SINFUL_HEX] = 5
    _react(state, trigger, aura)
    assert not _paid(state, "mc_sinful_hex")


def test_the_electro_test_reads_the_name_and_the_consumed_aura(overhaul):
    """The derivation the slice leans on, stated as its own claim: no hook
    signature widened, so this pair has to be enough."""
    assert hexerei.is_electro_reaction("overload", "pyro")
    assert hexerei.is_electro_reaction("superconduct", "cryo")
    assert hexerei.is_electro_reaction("electrocharged", "hydro")
    assert hexerei.is_electro_reaction("swirl", "electro")
    assert hexerei.is_electro_reaction("crystallize", "electro")
    assert not hexerei.is_electro_reaction("vaporize", "pyro")
    assert not hexerei.is_electro_reaction("swirl", "cryo")


def test_fischls_volley_applies_electro_and_terminates(overhaul):
    """It deals ELECTRO, so it can react again -- and the chain is bounded:
    every link spends a standing aura and creates none."""
    state = _state()
    state.enemies.append(make_enemy(hp=400, name="second"))
    state.player.powers[hexerei.SINFUL_HEX] = 5
    reactions.apply_aura(state, state.enemies[1], "pyro", "test")
    _react(state, "electro", "cryo", enemy=state.enemies[0])   # superconduct
    # At least one volley landed, and the run finished -- an unbounded chain
    # would not have returned at all.
    assert _paid(state, "mc_sinful_hex")


# --- Nicole, Ladder of Divine Ascent -----------------------------------------

def test_nicole_pays_on_any_companion_card_and_on_no_other(overhaul):
    """R276 pick 2: the Ladder reads "a Companion card". Diona's Icy Paws,
    which carried no Hexerei mark, pays now; a plain Klee card does not."""
    from tier0.engine.state import Card

    state = _state()
    state.player.powers[hexerei.LADDER_OF_ASCENT] = 6
    hexerei.note_card_played(
        state, loader.peek_card("proto_mc_sucrose_astable"))
    assert len(_paid(state, "mc_ladder_of_ascent")) == 1
    hexerei.note_card_played(
        state, loader.peek_card("proto_mc_diona_icy_paws"))
    assert len(_paid(state, "mc_ladder_of_ascent")) == 2
    hexerei.note_card_played(
        state, Card(id="proto_ko_plain", name="x", cost=1, type="skill"))
    assert len(_paid(state, "mc_ladder_of_ascent")) == 2


def test_nicole_deals_the_played_cards_element(overhaul):
    state = _state()
    state.player.powers[hexerei.LADDER_OF_ASCENT] = 6
    card = loader.peek_card("proto_mc_fischl_oz")                # electro
    hexerei.note_card_played(state, card)
    assert _paid(state, "mc_ladder_of_ascent")[0]["element"] == "electro"
    assert state.enemies[0].aura == "electro"


def test_a_companion_card_with_no_element_deals_plain_damage(overhaul):
    """R236 pick 6's own sentence. Read off a Card built for the test rather
    than off a row, so the claim survives every row on the sheet carrying one.
    """
    from tier0.engine.state import Card

    state = _state()
    state.player.powers[hexerei.LADDER_OF_ASCENT] = 6
    hexerei.note_card_played(state, Card(
        id="proto_mc_x", name="x", cost=1, type="skill", tags=["companion"]))
    assert _paid(state, "mc_ladder_of_ascent")[0]["element"] == "none"
    assert state.enemies[0].aura is None


def test_nicoles_own_card_is_a_companion(overhaul):
    """She pays for herself once, because her stand-in is a Companion card."""
    assert loader.peek_card("proto_mc_nicole_ladder_of_ascent").is_companion


# --- everyone else is unchanged ----------------------------------------------

def test_no_rule_here_fires_without_its_own_power(overhaul):
    """The arm is ON and Klee holds none of the three: a reaction and a card
    play must move nothing this slice owns."""
    state = _state()
    _react(state, "hydro", "pyro")
    _react(state, "electro", "cryo")
    hexerei.note_card_played(
        state, loader.peek_card("proto_mc_sucrose_astable"))
    for event in ("mc_mollis_favonius", "mc_sinful_hex",
                  "mc_ladder_of_ascent"):
        assert not _paid(state, event), event


def test_the_arms_other_reaction_readers_still_get_their_event(overhaul):
    """The registration is an ADDITION to `companion_overhaul_reaction`, not a
    replacement: Dahlia's Block and the Swirl counter must be untouched."""
    state = _state()
    state.player.powers["mc_favonian_favor"] = 3
    before = state.player.block
    _react(state, "anemo", "pyro")
    assert state.player.block == before + 3
    assert state.mi_swirls_this_turn == 1
