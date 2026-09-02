"""EB-253: the pilot's Fanfare estimates are not reads either.

THE DEFECT, AND WHY IT IS ITS OWN ROW. `EB-242` fixed exactly one instrument
-- `note_charge_read`, Kokomi's Charge bank -- because that was the instrument
whose registration had been graded. `note_fanfare_read` is a DIFFERENT
instrument with a different registration, and it carried the identical
exposure: the pilot prices a Fanfare rider through the engine's own helpers on
purpose, so that its price cannot drift from what resolving the card pays, and
both of those helpers filed a `fanfare_read` on the way past. A hand of four
Fanfare readers therefore wrote four "the meter was read" rows into a turn in
which the player played nothing.

TWO SITES, not one, and the second is the one the row's Scope names the HELPER
rather than the caller for:

  * `effects._bonus_formula`, the `N_per_M_fanfare` leg -- the exact twin of
    the charge leg `EB-242` repaired, reached from `policy._expected_damage`
    and `policy._raw_block`.
  * `effects.flat_attack_bonus`, the `attack_power` read Rapturous Applause
    prints -- reached from `policy._expected_damage` for EVERY attack in hand,
    which is why it was the larger of the two. Its own docstring claimed it
    "touches no telemetry"; that claim is what this row makes true.

WHAT IS DELIBERATELY UNTOUCHED. What a RESOLVED play tallies, at both sites,
because the instrument exists to see the live meter being read in play and a
fix that muted a resolve leg would be a second defect wearing the first one's
clothes. The `salon_focus` site already had this fix in its own spelling
(`note=False`, `policy.py`), and the `threshold` site was never exposed: the
pilot keeps its own copy of `fanfare_at_least_` PRECISELY because the engine's
predicate files a census row on the way past (`policy._ENGINE_LIVE_PREDICATES`
does not list it). Both are pinned below so a later tidy-up cannot delete the
reason.
"""

import random

import pytest

from tier0.content import loader
from tier0.engine import effects, resources
from tier0.engine.state import Card, CombatState
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy


FANFARE_RIDER = {"op": "damage", "amount": 5, "target": "enemy",
                 "bonus_formula": "1_per_2_fanfare"}
FANFARE_BLOCK = {"op": "block", "amount": 6, "bonus_formula": "1_per_2_fanfare"}


def _state(fanfare: int = 20) -> CombatState:
    st = CombatState(player=loader.build_player("furina"),
                     enemies=[make_enemy(hp=300)], rng=random.Random(0))
    st.player.fanfare_cap = max(st.player.fanfare_cap, 40)
    st.player.fanfare = fanfare
    st.log.clear()
    return st


def _card(**kw) -> Card:
    d = dict(id="eb253_probe", name="probe", cost=1, type="attack",
             character="furina", rarity="common")
    d.update(kw)
    return Card(**d)


def _reads(st: CombatState) -> list[dict]:
    return [ev for ev in st.log if ev["event"] == "fanfare_read"]


def test_the_pilots_damage_estimate_tallies_no_fanfare_read():
    """`policy._expected_damage` prices the rider through the engine's own
    helper -- that shared helper is why the pilot's price cannot drift from
    what resolves -- and pricing a card is not playing it."""
    st = _state()
    card = _card(effects=[FANFARE_RIDER])
    assert policy._expected_damage(st, card) > 5      # the rider IS read
    assert _reads(st) == []


def test_the_pilots_block_estimate_tallies_no_fanfare_read():
    """The second caller of the same helper, `policy._raw_block`."""
    st = _state()
    card = _card(type="skill", effects=[FANFARE_BLOCK])
    assert policy._raw_block(st, card) > 6
    assert _reads(st) == []


def test_pricing_an_attack_under_rapturous_applause_tallies_nothing():
    """`flat_attack_bonus`, the larger leg. The Applause rider is a PLAYER
    power, so once it is up the pilot pays this read for every attack it
    scores -- not only for cards that print a Fanfare formula."""
    st = _state()
    st.player.powers["fanfare_attack_per10"] = 2
    card = _card(effects=[{"op": "damage", "amount": 6, "target": "enemy"}])
    assert policy._expected_damage(st, card) > 6      # the rider IS read
    assert _reads(st) == []


def test_a_whole_pilot_turn_of_deliberation_tallies_nothing():
    """The shape the instrument actually saw. A pilot scores every card in
    hand every play, so one turn's deliberation over a hand of readers was
    a fistful of reads against a turn in which the player played none."""
    st = _state()
    st.player.powers["fanfare_attack_per10"] = 2
    st.player.hand = [_card(id=f"eb253_probe_{i}", effects=[FANFARE_RIDER])
                      for i in range(4)]
    st.player.energy = 3
    pilot = policy.make_pilot(loader.pilot_weights("salon"))
    assert pilot(st) is not None, "a hand of playable readers must be scored"
    assert _reads(st) == []


def test_what_a_resolved_play_tallies_is_untouched():
    """The other direction, and the one a careless fix breaks: resolving a
    card that prints the rider still files exactly one `bonus_formula` read,
    tagged with the card that read it."""
    st = _state()
    card = _card(effects=[FANFARE_RIDER])
    effects.resolve_card(st, card)
    reads = _reads(st)
    assert [ev["kind"] for ev in reads] == ["bonus_formula"]
    assert reads[0]["card"] == "eb253_probe"
    assert reads[0]["total"] == 20 and reads[0]["cap"] == st.player.fanfare_cap


def test_what_a_resolved_attack_under_applause_tallies_is_untouched():
    """The `attack_power` leg's resolve side, pinned for the same reason."""
    st = _state()
    st.player.powers["fanfare_attack_per10"] = 2
    card = _card(effects=[{"op": "damage", "amount": 6, "target": "enemy"}])
    effects.resolve_card(st, card)
    assert [ev["kind"] for ev in _reads(st)] == ["attack_power"]


def test_the_direct_probes_of_both_primitives_are_still_reads():
    """A caller that says nothing is a resolution, because every caller in
    the engine is one. The exemption is DECLARED by the estimate, which is
    what keeps a new resolve path from silently opting out of the tally."""
    st = _state()
    assert effects._bonus_formula(st, "1_per_2_fanfare") == 10
    assert [ev["kind"] for ev in _reads(st)] == ["bonus_formula"]

    st = _state()
    st.player.powers["fanfare_attack_per10"] = 2
    card = _card(effects=[])
    assert effects.flat_attack_bonus(st, card, 1) == 4
    assert [ev["kind"] for ev in _reads(st)] == ["attack_power"]
    assert effects.flat_attack_bonus(st, card, 1, valuation=True) == 4
    assert len(_reads(st)) == 1


def test_the_charge_leg_of_the_same_helper_is_untouched():
    """EB-242's instrument, from this side. The two legs share a function and
    a flag and nothing else; a fix to one must not retune the other."""
    st = CombatState(player=loader.build_player("kokomi"),
                     enemies=[make_enemy(hp=300)], rng=random.Random(0))
    st.player.charge = 8
    assert effects._bonus_formula(st, "1_per_2_charge") == 4
    assert st.charge_reads_this_turn == {"bonus_formula": 1}


@pytest.mark.parametrize("name", ["fanfare_at_least_10"])
def test_the_threshold_site_was_never_exposed(name):
    """The pilot does NOT delegate `fanfare_at_least_` to the engine, and the
    reason is this instrument: `_ENGINE_LIVE_PREDICATES` is the allowlist of
    predicates that are safe to ask live because they file nothing. This
    pins that the threshold predicate stays off it, so a later tidy-up that
    "simplifies" the pilot's copy away re-opens EB-253 loudly."""
    assert name not in policy.SCORABLE_PREDICATES
    assert not name.startswith(policy._ENGINE_LIVE_PREFIXES)
    st = _state()
    assert effects._predicate(st, name) is True
    assert [ev["kind"] for ev in _reads(st)] == ["threshold"]


def test_the_salon_focus_site_keeps_its_own_spelling():
    """`_salon_focus`'s exemption predates this row and is spelled `note`
    rather than `valuation` because it is a different kind of call. Pinned so
    the two spellings are a recorded decision rather than a drift."""
    st = _state()
    st.player.powers["salon_member"] = 2
    noted = effects._salon_amount(st, 5, note=True)
    quiet_state = _state()
    quiet_state.player.powers["salon_member"] = 2
    quiet = effects._salon_amount(quiet_state, 5, note=False)
    assert noted == quiet
    assert [ev["kind"] for ev in _reads(st)] == ["salon_focus"]
    assert _reads(quiet_state) == []
