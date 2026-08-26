"""EB-139 / R211 (`C20`): the Swirl aura-aware BIND.

THE ONE QUESTION `C18` LEFT OPEN, AND THE ANSWER IT GOT. `EB-136`/R210 bound
every `target: enemy` op of a card to a single creature picked at card-play
construction, and reported exactly one branch it would not guess at:
`_op_swirl` used to RE-AIM a single-target Swirl at whichever living body
carried an aura when the bound aim carried none. That re-take put
`sayu_yoohoo_windwheel`'s `damage 4` on one creature and its Swirl on another
-- a card scattering across two bodies where the mod puts both on
`cardPlay.Target`. R211 ([USER] 2026-08-25) ruled it:

  * FOR MANUALLY-MODELLED PLAY, if ANY living enemy carries an aura at
    card-play construction, the WHOLE CARD binds to the LOWEST-HP AURA-BEARING
    enemy. Otherwise the normal lowest-HP bind.
  * FORCED-RANDOM AUTOPLAY STAYS RANDOM AND RECEIVES NO CORRECTIVE RE-AIM.

WHY IT IS A BIND AND NOT A RE-TAKE, stated because the shape is the ruling.
A Swirl's entire payload IS the aura it lands on: aimed at an auraless body it
does nothing at all. So an aimed Swirl is the one card shape where the mouse
pick a human makes is READABLE OFF THE BOARD rather than a matter of taste,
and moving the aura-awareness up to `bind_card_aim` answers R210's objection
instead of restating it -- one creature for the whole play, damage and Swirl
together. Every card that does NOT carry an aimed Swirl keeps the documented
lowest-HP aim R210 declined to re-open; this is not a board-wide aim rule and
the negative pins below are what hold it to that.

BOARDS ARE BUILT SO THE OLD ENGINE AND THE NEW ONE DISAGREE, the same
discipline `test_eb136_same_target_binding.py` states: every board here puts
an aura somewhere the lowest-HP aim is not, and the three-body boards
separate "an aura-bearer" from "the LOWEST-HP aura-bearer" so a test cannot
pass by picking the wrong bearer.
"""

from __future__ import annotations

import random

from tier0.content import loader
from tier0.engine import effects
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state

#: The `sayu_yoohoo_windwheel` shape -- the ONE live row that carries an aimed
#: Swirl AND a second aimed op, which is what made the old re-take visible.
SAYU = [
    {"op": "damage", "amount": 4, "target": "enemy", "applies_element": False},
    {"op": "swirl", "target": "enemy"},
]


def _enemy(hp, name, aura=None):
    e = make_enemy(hp=hp, name=name)
    if aura:
        e.aura, e.aura_turns_left = aura, 3
    return e


def _card(cid, effs, ctype="attack", **kw) -> Card:
    return Card(id=cid, name=cid, cost=1, type=ctype, effects=effs, **kw)


# ---------------------------------------------------------------------------
#  ACCEPTANCE PIN 1 -- aura present: the WHOLE CARD goes to the lowest-HP
#  aura-bearer
# ---------------------------------------------------------------------------

def test_the_whole_card_binds_to_the_lowest_hp_aura_bearer():
    """THE ROW'S FIRST ACCEPTANCE PIN. Three bodies, and all three answers
    differ: `low` is lowest-HP overall and carries nothing, `mid` is the
    LOWEST-HP AURA-BEARER, `fat` is an aura-bearer too. C18 aimed at `low` and
    re-took the Swirl onto... whichever bearer was lowest, which is the same
    creature `mid` -- so the SWIRL half alone cannot distinguish the engines.
    The DAMAGE half can, and both are asserted here."""
    low = _enemy(20, "low")
    mid = _enemy(50, "mid", aura="pyro")
    fat = _enemy(90, "fat", aura="hydro")
    state = make_state([low, mid, fat])

    effects.resolve_card(state, _card("sayu_yoohoo_windwheel", SAYU))

    assert mid.hp == 46, "the damage did not follow the bind onto the bearer"
    assert low.hp == 20, "the damage stayed on the lowest-HP body"
    assert fat.hp == 90, "the bind took the FAT bearer, not the lowest-HP one"


def test_the_swirl_spreads_from_the_body_the_card_bound_to():
    """The Swirl half of the same pin, read through the reaction rather than
    through HP. Anemo is trigger-only and never sticks, so a Swirl on an
    auraless body does nothing; a Swirl on `mid`'s Pyro reacts and `_react`
    spreads that Pyro over the living board. `low` ending the play Pyro'd is
    the observable that the Swirl found an aura at all."""
    low = _enemy(20, "low")
    mid = _enemy(50, "mid", aura="pyro")
    state = make_state([low, mid])

    effects.resolve_card(state, _card("sucrose_gust", [
        {"op": "swirl", "target": "enemy"},
        {"op": "draw", "amount": 1},
    ], ctype="skill"))

    assert low.aura == "pyro", "the Swirl bound to the auraless body"


def test_a_swirl_inside_a_conditional_arm_still_gates_the_bind():
    """`prune_witch_hunt` puts its Swirl at the top level, but nothing stops a
    future row from putting one inside a branch, and the emitter's own aiming
    walk reads the whole tree. `_card_swirls_at_aim` walks `then`/`else` and
    mode bodies for the same reason: a Swirl this card can land is a Swirl."""
    low = _enemy(20, "low")
    mid = _enemy(50, "mid", aura="pyro")
    state = make_state([low, mid])

    effects.resolve_card(state, _card("hypothetical_branching_swirl", [
        {"op": "conditional", "if": "spotlight_set",
         "then": [{"op": "block", "amount": 3}],
         "else": [{"op": "swirl", "target": "enemy"}]},
        {"op": "damage", "amount": 4, "target": "enemy",
         "applies_element": False},
    ]))

    assert mid.hp == 46 and low.hp == 20
    assert low.aura == "pyro", "the branch's Swirl never fired"


# ---------------------------------------------------------------------------
#  ACCEPTANCE PIN 2 -- no aura anywhere: the normal lowest-HP bind
# ---------------------------------------------------------------------------

def test_with_no_aura_on_the_board_the_bind_is_the_normal_lowest_hp_pick():
    """The `else` half of the ruling, and the reason it has to be pinned: an
    implementation that reached for `min(bearers)` on an empty bearer list
    would raise, and one that fell through to `all_enemies` would silently
    widen a single-target card."""
    low, fat = _enemy(20, "low"), _enemy(90, "fat")
    state = make_state([low, fat])

    effects.resolve_card(state, _card("sayu_yoohoo_windwheel", SAYU))

    assert low.hp == 16 and fat.hp == 90
    assert low.aura is None and fat.aura is None   # nothing to spread


def test_a_dead_aura_bearer_does_not_pull_the_bind():
    """"ANY LIVING enemy", literally. A corpse still carrying a banked aura
    until the next settle (`reactions.close_dead_auras`, EB-58) must not drag
    the aim onto itself -- the card would fizzle its damage into a corpse and
    Swirl an aura that is about to close."""
    low, fat = _enemy(20, "low"), _enemy(90, "fat", aura="pyro")
    fat.hp = 0
    state = make_state([low, fat])

    effects.resolve_card(state, _card("sayu_yoohoo_windwheel", SAYU))

    assert low.hp == 16, "the bind walked onto a corpse's aura"


# ---------------------------------------------------------------------------
#  ACCEPTANCE PIN 3 -- forced-random autoplay is UNCHANGED
# ---------------------------------------------------------------------------

def _autoplayed(seed: int, effs: list[dict]) -> tuple:
    """One free play of `effs` on a fixed board, returning both bodies' HP.

    `force_random_targeting` is the free-play path (`effects._free_play`), and
    the ruling leaves it alone: an autoplay has no human at the mouse, so
    modelling one there would hand Havoc/Cascade a judgement the mod never
    gives them."""
    low, fat = _enemy(60, "low"), _enemy(90, "fat", aura="pyro")
    state = make_state([low, fat])
    state.rng = random.Random(seed)
    state.force_random_targeting = True
    effects.resolve_card(state, _card("sayu_yoohoo_windwheel", effs))
    return low.hp, fat.hp


def test_forced_random_autoplay_receives_no_corrective_re_aim():
    """The aura sits on `fat` on every seed. If the ruled bind leaked into the
    autoplay path, EVERY seed would put the 4 on `fat`. It does not: across 40
    seeds both bodies are hit, which is the random roll surviving."""
    hit_low = sum(_autoplayed(s, SAYU)[0] == 56 for s in range(40))
    assert 0 < hit_low < 40, "the autoplay roll was replaced by the aura bind"


def test_the_autoplay_roll_is_the_same_roll_it_was_before():
    """Stronger than the spread above, and the actual no-change claim: the
    creature a free play picks is `rng.choice(living)` on the SAME single draw
    R210 introduced. Reproduced here against the roll taken by hand."""
    for seed in range(20):
        rolled = random.Random(seed).choice(["low", "fat"])
        low_hp, fat_hp = _autoplayed(seed, SAYU)
        if rolled == "low":
            assert (low_hp, fat_hp) == (56, 90)
        else:
            assert (low_hp, fat_hp) == (60, 86)


# ---------------------------------------------------------------------------
#  ACCEPTANCE PIN 4 -- `times` follows the bind
# ---------------------------------------------------------------------------

def test_every_hit_of_a_multi_hit_row_lands_on_the_bound_aura_bearer():
    """R210 Q2 under the new bind: `times` re-checks the SAME creature and
    never re-picks, so all four hits go to the aura-bearer rather than
    walking back down to whoever is lowest-HP."""
    low = _enemy(20, "low")
    mid = _enemy(50, "mid", aura="pyro")
    state = make_state([low, mid])

    effects.resolve_card(state, _card("hypothetical_multihit_swirl", [
        {"op": "damage", "amount": 2, "target": "enemy", "times": 4,
         "applies_element": False},
        {"op": "swirl", "target": "enemy"},
    ]))

    assert mid.hp == 42 and low.hp == 20


def test_the_hits_after_the_bound_bearer_dies_fizzle():
    """And the fizzle half, unchanged: `AttackCommand.Execute` breaks on an
    empty refiltered target list. The hits do not walk to the survivor just
    because the bearer the card bound to is now a corpse."""
    low = _enemy(20, "low")
    frail = _enemy(3, "frail", aura="pyro")
    state = make_state([low, frail])

    effects.resolve_card(state, _card("hypothetical_multihit_swirl", [
        {"op": "damage", "amount": 2, "target": "enemy", "times": 4,
         "applies_element": False},
        {"op": "swirl", "target": "enemy"},
    ]))

    assert not frail.alive
    assert low.hp == 20, "the surviving hits walked off the dead aim"


# ---------------------------------------------------------------------------
#  ACCEPTANCE PIN 5 -- the dead-target rules are untouched
# ---------------------------------------------------------------------------

def test_an_aimed_swirl_still_lands_on_the_corpse_it_bound_to():
    """`CORPSE_TARGETABLE_OPS` is unchanged and this proves the bind did not
    quietly re-introduce a liveness filter: the damage kills the bound bearer,
    and the Swirl still reaches its banked aura (`ElementalHit.ApplyOnly` ->
    `AuraCmd.Apply` -> `PowerCmd.Apply<XAuraPower>`), so the Pyro spreads."""
    low = _enemy(20, "low")
    frail = _enemy(4, "frail", aura="pyro")
    state = make_state([low, frail])

    effects.resolve_card(state, _card("sayu_yoohoo_windwheel", SAYU))

    assert not frail.alive
    assert low.aura == "pyro", "the Swirl fizzled on the corpse it bound to"


def test_aimed_damage_after_the_bearer_dies_still_fizzles():
    """The other side of the non-uniform rule: a second damage row on the same
    card does NOT walk to the survivor once the bound bearer is dead."""
    low = _enemy(20, "low")
    frail = _enemy(4, "frail", aura="pyro")
    state = make_state([low, frail])

    effects.resolve_card(state, _card("hypothetical_double_swing_swirl", [
        {"op": "damage", "amount": 4, "target": "enemy",
         "applies_element": False},
        {"op": "damage", "amount": 9, "target": "enemy",
         "applies_element": False},
        {"op": "swirl", "target": "enemy"},
    ]))

    assert not frail.alive and low.hp == 20


def test_an_aimed_power_still_lands_on_the_corpse_the_swirl_card_bound_to():
    """`PowerCmd.Apply` guards only on `CanReceivePowers`. The aura-aware bind
    changes WHICH creature, never the corpse rule that follows it."""
    low = _enemy(20, "low")
    frail = _enemy(4, "frail", aura="pyro")
    state = make_state([low, frail])

    effects.resolve_card(state, _card("hypothetical_debuff_swirl", [
        {"op": "damage", "amount": 4, "target": "enemy",
         "applies_element": False},
        {"op": "apply_power", "power": "weak", "amount": 2,
         "target": "enemy"},
        {"op": "swirl", "target": "enemy"},
    ]))

    assert not frail.alive
    assert frail.powers.get("weak") == 2
    assert low.powers.get("weak", 0) == 0


# ---------------------------------------------------------------------------
#  ACCEPTANCE PIN 6 -- the bind is Swirl-SHAPED, not board-shaped
# ---------------------------------------------------------------------------

def test_a_card_with_no_swirl_ignores_the_auras_on_the_board():
    """THE NEGATIVE PIN THAT HOLDS THE ARCHIVE SCOPE DOWN, and the reason the
    scope statement can name six cards rather than every card in the repo. An
    ordinary attack on a board full of auras still aims lowest-HP. Read this
    one as the boundary of the ruling: the aura-awareness is a property of an
    aimed Swirl, not of the board."""
    low = _enemy(20, "low")
    mid = _enemy(50, "mid", aura="pyro")
    state = make_state([low, mid])

    effects.resolve_card(state, _card("bash", [
        {"op": "damage", "amount": 8, "target": "enemy",
         "applies_element": False},
        {"op": "apply_power", "power": "vulnerable", "amount": 2,
         "target": "enemy"},
    ]))

    assert low.hp == 12 and low.powers.get("vulnerable") == 2
    assert mid.hp == 50 and not mid.powers.get("vulnerable")


def test_an_all_enemies_swirl_does_not_move_a_cards_aim():
    """`lynette_astonishing_shift` pairs an aimed Swirl with `damage
    target: all_enemies`; the mirror case -- an `all_enemies` SWIRL beside an
    aimed damage row -- has no aim to correct, because the Swirl already hits
    the whole board. So it must not gate the bind."""
    low = _enemy(20, "low")
    mid = _enemy(50, "mid", aura="pyro")
    state = make_state([low, mid])

    effects.resolve_card(state, _card("hypothetical_board_swirl", [
        {"op": "swirl", "target": "all_enemies"},
        {"op": "damage", "amount": 4, "target": "enemy",
         "applies_element": False},
    ]))

    assert low.hp == 16 and mid.hp == 50


# ---------------------------------------------------------------------------
#  THE SCOPE PIN -- which live rows this reaches, read off the sheets
# ---------------------------------------------------------------------------

#: The archive scope of `C20`, ENUMERATED. Every live row carrying a Swirl
#: that lands on the play's bound aim -- one Inazuma row, two Fontaine, three
#: Mondstadt (one of them `personal_pool: klee`). No character sheet prints a
#: Swirl at all, which is why this list is entirely companions and why
#: `ref_ironclad` / `real_ironclad` / `real_silent` -- who draw no companion
#: rewards (`tier05.rewards.NO_COMPANION_CHARACTERS`) -- sit outside it.
SWIRL_ROWS = frozenset((
    "lynette_astonishing_shift",
    "lynette_enigmatic_feint",
    "prune_witch_hunt",
    "sayu_yoohoo_windwheel",
    "sucrose_astable",
    "sucrose_gust",
))


def test_the_live_sheets_carry_exactly_the_enumerated_swirl_rows():
    """DERIVED, NEVER LISTED -- the lint half of the archive-scope statement in
    `constants.py`'s `C20` block. If a later sheet window prints a seventh
    aimed Swirl, this fails and the scope paragraph gets corrected rather than
    silently outgrown."""
    live = {cid for cid, card in loader._card_index().items()
            if effects._card_swirls_at_aim(card)}
    assert live == SWIRL_ROWS
