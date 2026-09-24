"""`EB-418` -- the per-fight Spark ledger: every gain names its source.

THE DEFECT THIS FILE EXISTS FOR. The r11 Opus seat watched Spark go 1 to 2 in
fight 3 round 1 with no Bomb going off, and could not account for it:

    "Pounding Surprise says Sparks come from bombs going off, and the Spark
    keyword says 'Start each combat with 1. Pounding Surprise grants more.'
    Neither explains this gain... This is the one number in the kit I could not
    read off the screen."

IT WAS A RULE AND NOT A DEFECT. The grant was `Little Hexenzirkul`
(`effects.klee_companion_spark`, C# `KleeCompanionSpark`) -- the kit
declaration LAW:145 requires because a Companion card may not print a signature
resource on its own face -- and the seat had just played Diona, one of Klee's
coven Personals. The ruled companions packet says so outright: "the kit already
pays a rider neither card prints"
(`review/ruled/klee-personal-companions-2026-08-31.md` sec.2, fact one). So the
mod PRINTS it now, on the Companion's own face
(`ArmKeywordTips.ForCovenSpark`), and this file is the pin that stops the next
income arriving unnamed.

THE PIN IS THE ARGUMENT, not a list. `effects.gain_sparks` takes a REQUIRED
`source` and emits it, so a new Spark income cannot be written without naming
itself -- a curated list of known sources would have to be updated by the same
commit that forgets to. The whole-fight test below is the non-vacuous half: it
plays real fights and reads the ledger the fights actually mint.
"""

from __future__ import annotations

import collections
import inspect
import pathlib

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, klee_overhaul
from tier0.engine.combat import play_card, run_fight
from tier0.pilot.policy import make_pilot
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards

REPO = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture
def overhaul(monkeypatch):
    """The arm on, both id-resolving caches cleared either side."""
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()
    monkeypatch.setattr(C, "KLEE_OVERHAUL", True)
    yield
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()


def _klee_state(enemies=None):
    st = make_state(enemies=enemies)
    st.player.character_id = "klee"
    st.player.element = "pyro"
    st.player.cadence = "catalyst"
    st.player.relic_hooks.append(klee_overhaul.SPARK_RELIC_HOOK)
    st.in_player_turn = True
    return st


def _gains(state):
    """The per-fight ledger: one row per Spark that landed, and its source."""
    return state.spark_ledger


# --- the argument -----------------------------------------------------------

def test_the_gain_chokepoint_cannot_be_called_without_naming_a_source():
    """`source` is REQUIRED and has no default.

    SEEN TO FAIL: give the parameter a default and this test passes a call with
    no name into the engine, which is exactly the state `EB-418` was filed on.
    """
    sig = inspect.signature(effects.gain_sparks)
    param = sig.parameters["source"]
    assert param.default is inspect.Parameter.empty
    assert param.annotation == "str"


def test_the_ledger_carries_the_name_the_call_site_gave_it():
    state = _klee_state()

    effects.gain_sparks(state, 2, source="probe:the_name")

    row, = _gains(state)
    assert (row["amount"], row["before"], row["total"], row["source"]) == (
        2, 0, 2, "probe:the_name")
    # ...and the EVENT is untouched. Two fixed-seed log digests hash the whole
    # stream, and an instrument may not move a measurement.
    event, = [e for e in state.log if e["event"] == "gain_spark"]
    assert set(event) == {"turn", "event", "amount", "total"}


# --- the per-fight ledger ---------------------------------------------------

@pytest.mark.parametrize("seed", [3, 7, 11, 19])
def test_every_spark_gain_in_a_whole_fight_names_its_source(overhaul, seed):
    """The row's acceptance, read off real fights rather than a fixture.

    Four seeds and a real pilot, because the sources that fire depend on what
    the pilot draws: the opening Spark lands on every one, the relic's
    per-explosion Spark on any fight that sets a Bomb off, and a Powder-Charge
    hand spends before it gains.
    """
    pilot = make_pilot(loader.pilot_weights("demolition"))
    player = loader.build_player("klee")
    state = run_fight(player, loader.build_encounter("punisher"), pilot,
                      seed=seed)

    gains = _gains(state)
    assert gains, "a Klee fight with no Spark income at all is not a read"
    for row in gains:
        assert row.get("source"), row
        # A source names WHAT and WHERE, in the C# ledger's own vocabulary
        # (`SparkPower.Gain`'s `source`, `MeterLedger` since `EB-216`).
        assert ":" in row["source"], row

    # The opening bank is on every fight and is the one source the Spark
    # keyword tip already printed -- the denominator for the rest.
    assert any(row["source"] == "kit:opening_spark" for row in gains)


def test_the_sources_a_klee_fight_mints_are_the_arms_own_rules(overhaul):
    """Nothing unattributed and nothing from another arm's economy."""
    pilot = make_pilot(loader.pilot_weights("demolition"))
    player = loader.build_player("klee")
    state = run_fight(player, loader.build_encounter("punisher"), pilot,
                      seed=7)

    kinds = collections.Counter(row["source"].split(":", 1)[0]
                                for row in _gains(state))
    assert set(kinds) <= {"kit", "relic", "power", "card", "companion"}, kinds


# --- the grant the seat could not read --------------------------------------

def test_under_the_arm_a_companion_play_is_no_gain_at_all(overhaul):
    """The r11 find was a Spark arriving with no Bomb going off, paid by a
    Companion play. On 2026-09-23 [USER] turned that income off under the arm
    ("worth decreasing now to go back to the old levels and then see if play
    is Spark-constrained"), so the three cards that used to reproduce it -- a
    Universal (Razor), the coven Personal the seat played (Diona) and a card
    outside the old family (Gorou's War Banner) -- now leave the bank and the
    ledger untouched. The ledger name below still stands for the off-arm
    world.
    """
    for cid in ("proto_mc_razor_claw_and_thunder",
                "proto_mc_diona_shaken_not_purred",
                "proto_mi_gorou_war_banner"):
        card = loader.get_card(cid)
        assert card.is_companion, cid

        state = _klee_state(enemies=[make_enemy(hp=39, name="spinner")])
        state.player.sparks = 1
        state.player.hand = [card]

        play_card(state, card)

        assert state.player.sparks == 1, cid
        assert "companion:personal/play" not in [
            row["source"] for row in _gains(state)], cid


def test_the_name_is_the_rules_and_not_one_companions(overhaul):
    """`EB-219` moved the grant off Prune's face and keyed it on a SET, so a
    ledger row saying "prune" over another witch's play is the same unreadable
    number one surface further in. Both engines say `companion:personal/play`."""
    src = (REPO / "klee-mod" / "KleeCode" / "Powers"
           / "KleeCompanionSpark.cs").read_text(encoding="utf-8")
    assert 'source: "companion:personal/play"' in src
    assert "companion:prune/play" not in src
