"""`EB-495` D6 — enemy-side retaliation, built in the sim.

`ThornsPower`, `FlameBarrierPower` and `CurlUpPower` existed on the PLAYER's
side of `refpowers.py` and nowhere on the enemy's, so an Attack into an enemy
carrying Thorns cost HP in the game and nothing in the sim. The atlas's whole
T6 column was `none*`.

THE THREE POWERS ARE THREE DIFFERENT HOOKS, and reading them apart is most of
this file:

    ThornsPower.BeforeDamageReceived (:19)
        dealer != null && (IsPoweredAttack() || cardSource is Omnislice)
        ABOVE Block and ABOVE LoseHp — a fully blocked hit is thorned, and so
        is a killing blow.

    FlameBarrierPower.AfterDamageReceived (:20)
        dealer != null && IsPoweredAttack(), and it takes the DamageResult as
        `_` — no unblocked > 0. But AfterDamageReceived is skipped for a
        creature the hit killed (CreatureCmd.cs:410), so a killing blow does
        NOT burn.

    CurlUpPower.AfterDamageReceived (:31)
        IsPoweredAttack() && cardSource != null, and it does not act: it
        REMEMBERS the card, and pays the Block when that card's play finishes
        (AfterCardPlayed, :49).

THE NEGATIVE HALF IS THE LOAD-BEARING ONE. All three ask
`IsPoweredAttack()`, which every kit verb fails by construction —
`ElementalHit.Deal` passes `ValueProp.Unpowered` with `dealer: null`. So a
Bomb, a Plan, a Mine and a performance are never thorned, never burned and
never curl a Louse, in either engine. The atlas's T6 column says `none` for
every one of those rows and this repair must not move a single one of them.

WHAT THE SIM'S FIGHTS REACH. `ThornsPower` is granted by `SpinyToad:76` and
`Toadpole:110`, both `Underdocks` bodies and neither present in
`tier05/content/act1_pool.yaml`. `CurlUpPower` is granted by
`LouseProgenitor:70` — and `louse_progenitor` IS in `act2_pool.yaml`, where
its comment already reads "UNIMPLEMENTED: Curl Up 14 (folded into the block
beat)". `FlameBarrierPower` is granted by no monster in the assembly at all;
it is the player's card. No encounter file was touched by this repair, so
every one of these stands the power up by hand.
"""

from __future__ import annotations

import pytest

from tier0.engine import effects, refpowers
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state


KIT_SOURCES = ("bomb", "set_off", "bomb_echo", "plan", "casket", "salon",
               "salon_final_bow", "furina_stage/act", "furina_stage/bow",
               "companion", "burst")


def _armed(power, amount=5, hp=200, enemy_block=0, player_block=0):
    enemy = make_enemy(hp=hp)
    enemy.powers[power] = amount
    enemy.block = enemy_block
    state = make_state(enemies=[enemy])
    state.player.block = player_block
    return state, enemy


def _damage_card(card_type="attack", amount=6):
    return Card(id="pin_hit", name="pin", cost=1, type=card_type,
                effects=[{"op": "damage", "amount": amount, "target": "enemy"}])


# ---------------------------------------------------------------------------
# Thorns — BeforeDamageReceived
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("source", ["attack", "card"])
def test_a_card_hit_is_thorned_whatever_the_card_is_called(source):
    """`IsPoweredAttack()` is `Move` without `Unpowered` and says nothing
    about `CardType.Attack`, which is D1/D2's finding one power over."""
    state, enemy = _armed("thorns", 5)
    hp = state.player.hp
    effects.deal_damage_to_enemy(state, enemy, 6, source=source)
    assert state.player.hp == hp - 5


def test_a_fully_blocked_hit_is_still_thorned():
    """BeforeDamageReceived fires ABOVE the Block computation
    (`CreatureCmd.cs:285-286`) and Thorns never looks at a `DamageResult`."""
    state, enemy = _armed("thorns", 5, enemy_block=50)
    hp = state.player.hp
    effects.deal_damage_to_enemy(state, enemy, 6, source="attack")
    assert enemy.block == 44
    assert state.player.hp == hp - 5


def test_a_killing_blow_is_still_thorned():
    """The other half of the same placement: the hook fires above
    `LoseHpInternal`, so a corpse still pays. The AfterDamageReceived readers
    below are denied exactly this."""
    state, enemy = _armed("thorns", 5, hp=4)
    hp = state.player.hp
    effects.deal_damage_to_enemy(state, enemy, 40, source="attack")
    assert not enemy.alive
    assert state.player.hp == hp - 5


def test_the_players_own_block_absorbs_a_retaliation():
    """`ValueProp.Unpowered` is not `Unblockable`."""
    state, enemy = _armed("thorns", 5, player_block=3)
    hp = state.player.hp
    effects.deal_damage_to_enemy(state, enemy, 6, source="attack")
    assert state.player.block == 0
    assert state.player.hp == hp - 2


@pytest.mark.parametrize("source", KIT_SOURCES)
def test_no_kit_verb_is_thorned(source):
    """THE PIN THAT MAY NOT MOVE. Every kit verb leaves the mod through
    `ElementalHit.Deal` — `Unpowered`, `dealer: null` — so `IsPoweredAttack()`
    is false and Thorns has never fired for one in the game either."""
    state, enemy = _armed("thorns", 5)
    hp = state.player.hp
    effects.deal_damage_to_enemy(state, enemy, 6, source=source)
    assert state.player.hp == hp, source


def test_an_unpowered_card_hit_is_not_thorned():
    """The flag read literally, D2's precedent: a card-sourced hit that
    refuses the dealer's terms is `Unpowered` and fails the predicate."""
    state, enemy = _armed("thorns", 5)
    hp = state.player.hp
    effects.deal_damage_to_enemy(state, enemy, 6, source="attack",
                                 powered=False)
    assert state.player.hp == hp


# ---------------------------------------------------------------------------
# FlameBarrier — AfterDamageReceived
# ---------------------------------------------------------------------------

def test_an_enemy_flame_barrier_burns_a_card_hit():
    state, enemy = _armed("flame_barrier", 4)
    hp = state.player.hp
    effects.deal_damage_to_enemy(state, enemy, 6, source="attack")
    assert state.player.hp == hp - 4


def test_an_enemy_flame_barrier_burns_a_fully_blocked_hit():
    """`DamageResult _` — the power never reads it, so there is no
    `unblocked > 0` to fail. But `WasFullyBlocked` does NOT skip the
    broadcast: only a kill does."""
    state, enemy = _armed("flame_barrier", 4, enemy_block=50)
    hp = state.player.hp
    effects.deal_damage_to_enemy(state, enemy, 6, source="attack")
    assert state.player.hp == hp - 4


def test_an_enemy_flame_barrier_does_not_burn_on_the_blow_that_kills_it():
    """`CreatureCmd.Damage:410`. This is the line that separates FlameBarrier
    from Thorns, and it is asserted rather than assumed because the two powers
    read identically in every other respect."""
    state, enemy = _armed("flame_barrier", 4, hp=4)
    hp = state.player.hp
    effects.deal_damage_to_enemy(state, enemy, 40, source="attack")
    assert not enemy.alive
    assert state.player.hp == hp


@pytest.mark.parametrize("source", KIT_SOURCES)
def test_no_kit_verb_is_burned(source):
    state, enemy = _armed("flame_barrier", 4)
    hp = state.player.hp
    effects.deal_damage_to_enemy(state, enemy, 6, source=source)
    assert state.player.hp == hp, source


def test_an_enemy_barrier_expires_at_the_players_side_turn_end():
    """`AfterSideTurnEnd` removes the power when `Owner.Side != side`
    (`:29`), so an enemy's barrier covers the player's turn and then goes —
    the mirror image of the player's, which `after_enemy_side_turn_end`
    removes at the enemy side's end."""
    state, enemy = _armed("flame_barrier", 4)
    refpowers.on_fighter_turn_end(state, state.player)
    assert "flame_barrier" not in enemy.powers
    hp = state.player.hp
    effects.deal_damage_to_enemy(state, enemy, 6, source="attack")
    assert state.player.hp == hp


def test_the_enemy_side_removal_leaves_the_players_own_barrier_alone():
    """The control on the line above: the two lifetimes are two different
    hook firings and folding them would spend the player's barrier a half
    round early."""
    state, enemy = _armed("flame_barrier", 4)
    state.player.powers["flame_barrier"] = 7
    refpowers.on_fighter_turn_end(state, state.player)
    assert state.player.powers["flame_barrier"] == 7


# ---------------------------------------------------------------------------
# CurlUp — AfterDamageReceived, paid at AfterCardPlayed
# ---------------------------------------------------------------------------

def test_curl_up_pays_its_block_after_the_card_and_not_during_it():
    """The timing IS the power: `AfterDamageReceived` only remembers the
    card, and `AfterCardPlayed` gains the Block. So the hit that woke it is
    never mitigated by the Block it bought."""
    enemy = make_enemy(hp=200)
    enemy.powers["curl_up"] = 14
    state = make_state(enemies=[enemy])
    card = _damage_card()
    snap = refpowers.before_card_played(state, card)
    effects.resolve_card(state, card)
    assert enemy.block == 0            # not yet
    assert enemy.hp == 194             # the hit landed in full
    refpowers.after_card_played(state, card, snap)
    assert enemy.block == 14
    assert "curl_up" not in enemy.powers     # PowerCmd.Remove, not Decrement


def test_curl_up_fires_once_and_is_spent():
    """`PowerCmd.Remove(this)`, so a second card buys nothing. Read off the
    Block ledger: the first card grants 14 and its own 6 had already landed on
    HP, the second card's 6 is eaten by that Block and grants nothing, so the
    body ends on 8 Block and 194 HP."""
    enemy = make_enemy(hp=200)
    enemy.powers["curl_up"] = 14
    state = make_state(enemies=[enemy])
    for _ in range(2):
        card = _damage_card()
        snap = refpowers.before_card_played(state, card)
        effects.resolve_card(state, card)
        refpowers.after_card_played(state, card, snap)
    assert enemy.block == 8
    assert enemy.hp == 194
    assert "curl_up" not in enemy.powers


@pytest.mark.parametrize("source", KIT_SOURCES)
def test_no_kit_verb_curls_a_louse(source):
    """`cardSource != null` AND `IsPoweredAttack()` — a kit verb fails both.
    Asserted through the latch rather than the Block, because the Block is a
    turn away and the latch is the decision."""
    state, enemy = _armed("curl_up", 14)
    effects.deal_damage_to_enemy(state, enemy, 6, source=source)
    assert enemy.curl_up_card is None, source


def test_a_hit_outside_any_card_play_leaves_the_latch_alone():
    """`cardSource == null` spelled as "no card is in flight". A direct
    `deal_damage_to_enemy(source="attack")` outside a play is exactly the
    case, and it is the one a future caller is most likely to reach for."""
    state, enemy = _armed("curl_up", 14)
    assert state.card_in_flight is None
    effects.deal_damage_to_enemy(state, enemy, 6, source="attack")
    assert enemy.curl_up_card is None


def test_a_killing_blow_does_not_arm_curl_up():
    state, enemy = _armed("curl_up", 14, hp=4)
    state.card_in_flight = "whatever"
    effects.deal_damage_to_enemy(state, enemy, 40, source="attack")
    assert not enemy.alive
    assert enemy.curl_up_card is None


def test_the_card_in_flight_is_restored_and_not_cleared():
    """A nested play — an autoplay, a Sly rider — must hand the outer card
    back, or the game's reference comparison would be answered `null` for the
    rest of the outer card's resolution."""
    enemy = make_enemy(hp=200)
    state = make_state(enemies=[enemy])
    outer, inner = _damage_card(), _damage_card()
    inner.id = "pin_inner"
    o_snap = refpowers.before_card_played(state, outer)
    assert state.card_in_flight == "pin_hit"
    i_snap = refpowers.before_card_played(state, inner)
    assert state.card_in_flight == "pin_inner"
    refpowers.after_card_played(state, inner, i_snap)
    assert state.card_in_flight == "pin_hit"
    refpowers.after_card_played(state, outer, o_snap)
    assert state.card_in_flight is None


# ---------------------------------------------------------------------------
# The control
# ---------------------------------------------------------------------------

def test_an_enemy_carrying_none_of_them_is_byte_identical():
    """Why no published sim number moved: every branch D6 added is keyed on a
    power no shipped encounter authors."""
    enemy = make_enemy(hp=200)
    state = make_state(enemies=[enemy])
    hp = state.player.hp
    effects.deal_damage_to_enemy(state, enemy, 40, source="attack")
    assert enemy.hp == 160
    assert state.player.hp == hp
    assert enemy.curl_up_card is None
