"""`EB-495` D5 — the enemy side of `Hook.AfterDamageReceived`, built.

WHAT WAS MISSING. `refpowers.on_damage_received` reads `state.player.powers`
and is called from one site for damage the PLAYER received
(`combat.py`), so nothing a kit verb did could ever be seen by the enemy it
hit. The atlas's whole T5 column read `none*` — an absence, not a decision —
and the consequence was written down in its own words: "no sim number is a
forecast of a fight against a Hardened-Shell body".

WHAT THE GAME ACTUALLY DOES, off the decompile rather than off the card:

    Hook.AfterDamageReceived(..., result, props, dealer, cardSource)
        broadcast from CreatureCmd.Damage:416, and ONLY
        `if (!result.WasTargetKilled || !originalTarget.IsDead)` (:410)

so the hook has no attack filter of its own and skips a killing blow
entirely. `HardenedShellPower` supplies the rest:

    AfterDamageReceived (:52)   return on result.WasFullyBlocked, then
                                damageReceivedThisTurn += result.UnblockedDamage
    ModifyHpLostBeforeOstyLate  return Math.Min(amount, Amount - taken)  (:38)
    BeforeSideTurnStart (:66)   taken = 0, with NO side filter

THE ENEMY-SIDE T5 POPULATION IS ONE POWER. The three names the atlas listed
beside it — `EmotionChip`, `LavaLamp`, `BeatingRemnant` — are all in
`Models/Relics/` and read the hook for the creature that owns them, which is
never a monster. `HardenedShellPower` is granted by exactly one body,
`SkulkingColony:56`, at 20.

NO SIM FIGHT AUTHORS IT TODAY, and that is the point of pinning it here
rather than in an encounter: `tier0/content/encounters/` is the frozen
battery and `tier05/content/act*_pool.yaml` has no Skulking Colony, so every
assertion below stands the power up by hand through the `powers:` door those
pools already own. Nothing in any shipped fight changed, which is why no
battery band moved.
"""

from __future__ import annotations

import pytest

from tier0.engine import effects, refpowers
from tier0.tests.conftest import make_enemy, make_state


KIT_SOURCES = ("attack", "card", "bomb", "set_off", "bomb_echo", "plan",
               "casket", "salon", "salon_final_bow", "furina_stage/act",
               "furina_stage/bow", "companion", "burst")


def _shelled(amount=20, hp=200, block=0):
    enemy = make_enemy(hp=hp)
    enemy.powers["hardened_shell"] = amount
    enemy.block = block
    return make_state(enemies=[enemy]), enemy


# ---------------------------------------------------------------------------
# The cap
# ---------------------------------------------------------------------------

def test_the_shell_caps_one_hit_at_its_allowance():
    """`ModifyHpLostBeforeOstyLate`: a 40 into a 20-point shell removes 20."""
    state, enemy = _shelled(amount=20)
    effects.deal_damage_to_enemy(state, enemy, 40, source="attack")
    assert enemy.hp == 180


def test_the_allowance_is_spent_across_hits_within_the_turn():
    """The counter is a running total, not a per-hit clamp: 12 then 12 into a
    20-point shell removes 12 and then 8."""
    state, enemy = _shelled(amount=20)
    effects.deal_damage_to_enemy(state, enemy, 12, source="attack")
    assert enemy.hp == 188
    effects.deal_damage_to_enemy(state, enemy, 12, source="attack")
    assert enemy.hp == 180


def test_a_spent_shell_admits_nothing_more_this_turn():
    state, enemy = _shelled(amount=10)
    effects.deal_damage_to_enemy(state, enemy, 30, source="attack")
    assert enemy.hp == 190
    effects.deal_damage_to_enemy(state, enemy, 30, source="attack")
    assert enemy.hp == 190


def test_the_reset_restores_the_whole_allowance():
    """`BeforeSideTurnStart`, whose override never reads the `side` it is
    handed — so each side's start restores it, which is what
    `reset_enemy_damage_caps` is called twice a round to say."""
    state, enemy = _shelled(amount=10)
    effects.deal_damage_to_enemy(state, enemy, 30, source="attack")
    assert enemy.hp == 190
    refpowers.reset_enemy_damage_caps(state)
    effects.deal_damage_to_enemy(state, enemy, 30, source="attack")
    assert enemy.hp == 180


def test_block_is_spent_before_the_cap_sees_the_hit():
    """`Hook.ModifyHpLost(BeforeOsty)` runs on `max(amount - blocked, 0)`
    (`CreatureCmd.cs:286`), so Block and the shell compose rather than
    compete: 5 Block plus a 10 shell eats 15 of a 30."""
    state, enemy = _shelled(amount=10, block=5)
    effects.deal_damage_to_enemy(state, enemy, 30, source="attack")
    assert enemy.hp == 190
    assert enemy.block == 0


# ---------------------------------------------------------------------------
# The accumulator, and the predicates that gate it
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("source", KIT_SOURCES)
def test_every_verb_spends_the_shell_including_every_kit_verb(source):
    """THE LOAD-BEARING PIN. `AfterDamageReceived` has no attack filter and
    `HardenedShellPower` adds none — no `IsPoweredAttack`, no `dealer`, no
    `cardSource` — so a Bomb, a Plan, a Mine and a performance all spend the
    shell in the game exactly as an Attack card does. This is the one column
    where a kit verb is NOT invisible to a base-game trigger, which is why D5
    was a comparability gap and not a cosmetic one."""
    state, enemy = _shelled(amount=20)
    effects.deal_damage_to_enemy(state, enemy, 6, source=source)
    assert enemy.hardened_shell_taken == 6, source


def test_an_unpowered_hit_still_spends_the_shell():
    """The `Unpowered` flag is the thing every OTHER trigger reads and this
    one does not. Pinned so a later edit cannot quietly borrow D1/D2's
    predicate for a power that never had it."""
    state, enemy = _shelled(amount=20)
    effects.deal_damage_to_enemy(state, enemy, 6, source="attack",
                                 powered=False)
    assert enemy.hardened_shell_taken == 6


def test_a_fully_blocked_hit_spends_nothing():
    """`if (result.WasFullyBlocked) return;` (`:57`). Block present, nothing
    through: the shell is untouched."""
    state, enemy = _shelled(amount=20, block=50)
    effects.deal_damage_to_enemy(state, enemy, 6, source="attack")
    assert enemy.hardened_shell_taken == 0


def test_a_killing_blow_fires_the_funnel_for_nobody():
    """`CreatureCmd.Damage:410` skips the whole broadcast for a creature the
    hit killed. Asserted through the accumulator because that is the only
    enemy-side reader there is: a shell whose owner died records nothing.

    The shell does NOT save it — the cap is `ModifyHpLost`, a different hook,
    and it ran first: 5 HP behind a 20-point allowance still dies to a 40."""
    state, enemy = _shelled(amount=20, hp=5)
    effects.deal_damage_to_enemy(state, enemy, 40, source="attack")
    assert not enemy.alive
    assert enemy.hardened_shell_taken == 0


def test_the_accumulator_counts_the_loss_and_not_the_overkill():
    """`DamageResult.UnblockedDamage` and `.OverkillDamage` are separate
    fields and the readers add up the first. A 40 into a 30 HP body behind a
    50-point shell spends 30, not 40 — and this is checked on a body that
    SURVIVES, because the killing-blow gate above would hide it."""
    state, enemy = _shelled(amount=50, hp=30)
    enemy.hp = 30
    effects.deal_damage_to_enemy(state, enemy, 25, source="attack")
    assert enemy.hardened_shell_taken == 25


def test_an_enemy_without_the_power_is_byte_identical():
    """The control, and the reason no published sim number moved: every
    branch added by D5 is keyed on a power no shipped encounter authors."""
    enemy = make_enemy(hp=200)
    state = make_state(enemies=[enemy])
    effects.deal_damage_to_enemy(state, enemy, 40, source="attack")
    assert enemy.hp == 160
    assert enemy.hardened_shell_taken == 0
