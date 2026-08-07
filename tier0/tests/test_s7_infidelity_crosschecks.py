"""S7 sim-infidelity cross-checks: the five behaviours the S13 exploit ledger
routed here, each resolved against the C# mod and pinned.

WHY THIS FILE EXISTS
--------------------
`review/redteam/exploit-ledger.md` § "Routed to S7" lists five sim behaviours
that "smell like implementation artifacts rather than rules" and asks for a
tier0-vs-C# verdict *before any design session treats them as game facts*.
All five were read against `klee-mod/KleeCode/` and all five came back
MATCHING -- the C# does the same thing, and in four of the five cases its own
comments name the sim line it was ported from. So the exploit lines that rest
on them are design material after all, not sim artifacts.

These are PARITY PINS, not balance opinions. Each test cites the sim site and
the C# site it locks together; if either side moves, the pin goes red and
whoever moved it has to move the other side or re-open the verdict.

THE FIVE, WITH THEIR C# COUNTERPARTS
------------------------------------
1. Swirl aura self-refresh
   sim  tier0/engine/reactions.py:96-99 (consume) + :108-111 (spread)
   C#   klee-mod/KleeCode/Powers/ReactionEffects.cs:279-305
2. Detonation-order Vulnerable self-amplification
   sim  tier0/engine/effects.py:443-480 (the per-bomb loop)
   C#   klee-mod/KleeCode/Powers/BombPower.cs:467-484
        + Powers/DemolitionPowers.cs:129-153 (DetonationVulnPower)
3. Conscript nation hard-default 'inazuma'
   sim  tier0/engine/effects.py:2101
   C#   klee-mod/KleeCode/Powers/KokomiConscript.cs:57 (a `const`, and the
        only nation the C# can express -- Run() takes no nation parameter)
4. Kurage direct `p.block +=` bypass
   sim  tier0/engine/effects.py:2652-2655
   C#   klee-mod/KleeCode/Powers/KuragePowers.cs:96-106 (ValueProp.Unpowered,
        ruled canonical as NC-11 / R116)
5. Per-effect-dict relic no-dedupe
   sim  tier0/engine/relics.py:108-158, :186-200
   C#   no klee-mod counterpart for these hooks (they model BASE-GAME relics);
        the structural analogue is the per-instance relic dispatch in
        BombPower.cs:502-508, which likewise does not dedupe by type.
"""

import random

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, powers, reactions, relics
from tier0.engine.state import Bomb, Card, CombatState
from tier0.tests.conftest import make_enemy, make_state


# ---------------------------------------------------------------------------
# 1. Swirl aura self-refresh -- MATCHES C#.
#
# reactions.resolve_hit clears the aura (reactions.py:97-98) and then _react's
# anemo branch re-applies it to every living enemy (reactions.py:108-111) --
# the source among them, so the enemy that just paid its aura gets a fresh
# full-duration copy of the same element.
#
# ReactionEffects.cs:279-305 does exactly this and says so:
#     "the consumed aura is applied to EVERY living enemy -- the original
#      target included (its own aura was consumed first, so it gets a fresh
#      copy)."
# AuraPower.cs:151-157 is the ordering half ("Consume the aura BEFORE
# resolving effects"), and AuraCmd.Apply / AuraCmd.Refresh
# (ElementalApplication.cs:239-282) both land on Duration(applier), i.e. the
# sim's aura_duration(state).
# ---------------------------------------------------------------------------

def test_swirl_returns_the_consumed_aura_to_the_enemy_it_was_taken_from():
    """Anemo into a Pyro aura consumes it and immediately gives it back at
    FULL duration. Parity pin: reactions.py:96-99/108-111 vs
    ReactionEffects.cs:279-305 (Reaction.Swirl includes the target)."""
    state = make_state()
    enemy = state.enemies[0]

    reactions.apply_aura(state, enemy, "pyro")
    enemy.aura_turns_left = 1                      # about to expire
    reactions.resolve_hit(state, enemy, "anemo", 5)

    assert enemy.aura == "pyro"
    assert enemy.aura_turns_left == reactions.aura_duration(state)


def test_swirl_spreads_the_consumed_aura_to_every_other_living_enemy():
    """The same loop that feeds the source also seeds the rest of the board,
    at full duration. C#: `foreach (var e in swirlTargets)` over
    CombatState.HittableEnemies (ReactionEffects.cs:285-303)."""
    state = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b"),
                               make_enemy(name="c")])
    source = state.enemies[0]

    reactions.apply_aura(state, source, "cryo")
    reactions.resolve_hit(state, source, "anemo", 5)

    assert [e.aura for e in state.enemies] == ["cryo", "cryo", "cryo"]
    assert all(e.aura_turns_left == reactions.aura_duration(state)
               for e in state.enemies)


def test_swirl_overwrites_a_different_aura_on_a_bystander_without_reacting():
    """A bystander carrying another element is REPLACED outright -- no second
    reaction. C#: `await PowerCmd.Remove(existing)` then AuraCmd.Apply
    (ReactionEffects.cs:290-302), never a reaction lookup."""
    state = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    source, bystander = state.enemies

    reactions.apply_aura(state, source, "pyro")
    reactions.apply_aura(state, bystander, "hydro")
    before = state.reactions_this_card

    reactions.resolve_hit(state, source, "anemo", 5)

    assert bystander.aura == "pyro"
    assert state.reactions_this_card == before + 1        # swirl only


# ---------------------------------------------------------------------------
# 2. Detonation-order Vulnerable self-amplification -- MATCHES C#.
#
# effects.detonate_bombs applies Explosive Frags' Vulnerable INSIDE the
# per-bomb loop, after that bomb's damage call (effects.py:478-480), so bomb
# #1's debuff multiplies bombs #2..#N of the same detonation.
#
# BombPower.cs:467-484 runs the identical shape -- `foreach (var damage in
# payloads) { await ElementalHit.Deal(...); await
# NotifyDetonationListeners(...); }` -- and DetonationVulnPower is one of
# those listeners (DemolitionPowers.cs:144-153), whose own comment reads
# "Per bomb, uncapped -- the sim has no proc gate here." A detonation is NOT
# atomic in the mod either.
# ---------------------------------------------------------------------------

def _detonation_damage_events(state):
    return [ev["amount"] for ev in state.log
            if ev["event"] == "damage" and ev.get("source") == "bomb"]


def test_first_bomb_vulnerable_amplifies_the_later_bombs_of_the_same_volley():
    """Three identical bombs, one stack of detonation_vuln: bomb #1 lands
    raw, #2 and #3 land Vulnerable-amplified. Parity pin:
    effects.py:443-480 vs BombPower.cs:467-484 + DemolitionPowers.cs:144."""
    state = make_state(enemies=[make_enemy(hp=500)])
    enemy = state.enemies[0]
    enemy.bombs = [Bomb(damage=10) for _ in range(3)]
    state.player.powers["detonation_vuln"] = 1

    effects.detonate_bombs(state, enemy)

    amplified = int(10 * C.VULNERABLE_TAKEN_MULT)
    assert _detonation_damage_events(state) == [10, amplified, amplified]


def test_a_lone_bomb_never_amplifies_itself():
    """The Vulnerable lands AFTER the damage, so a single-bomb detonation is
    unamplified -- the self-amp needs a second bomb in the same volley."""
    state = make_state(enemies=[make_enemy(hp=500)])
    enemy = state.enemies[0]
    enemy.bombs = [Bomb(damage=10)]
    state.player.powers["detonation_vuln"] = 1

    effects.detonate_bombs(state, enemy)

    assert _detonation_damage_events(state) == [10]
    assert enemy.powers.get("vulnerable", 0) == 1


def test_detonation_vulnerable_is_withheld_from_a_corpse():
    """`if vuln and enemy.alive` -- C#: `if (target.IsDead) return;`
    (DemolitionPowers.cs:149)."""
    state = make_state(enemies=[make_enemy(hp=5)])
    enemy = state.enemies[0]
    enemy.bombs = [Bomb(damage=99)]
    state.player.powers["detonation_vuln"] = 2

    effects.detonate_bombs(state, enemy)

    assert not enemy.alive
    assert enemy.powers.get("vulnerable", 0) == 0


# ---------------------------------------------------------------------------
# 3. Conscript nation hard-default 'inazuma' -- MATCHES C#.
#
# effects.py:2101 reads `fx.get("nation", "inazuma")`. The C# has no nation
# parameter AT ALL: KokomiConscript.Nation is a `const string = "inazuma"`
# (KokomiConscript.cs:57) and Run() is called with
# (amount, createMode, costOverride) only -- see the nine generated call
# sites, and gen_klee_cards.py:3147-3153, which never emits a nation.
#
# So the sim's default IS the C# behaviour, and the `nation` key is the one
# thing that could break it: any sheet that set it would be silently dropped
# by codegen. The second test is the guard that keeps that unreachable.
# ---------------------------------------------------------------------------

def _conscript_state(seed=0):
    return CombatState(player=loader.build_player("kokomi"),
                       enemies=[make_enemy(hp=300)],
                       rng=random.Random(seed))


def _conscript_card(**fx):
    effect = {"op": "conscript", "amount": 1}
    effect.update(fx)
    return Card(id="s7_conscript_probe", name="probe", cost=0, type="skill",
                character="kokomi", effects=[effect])


def test_conscript_default_pool_is_inazuma_matching_the_csharp_const():
    """No `nation` on the effect dict -> the Inazuma roster, which is the only
    pool KokomiConscript can produce (KokomiConscript.cs:57, 112-114)."""
    for seed in range(12):
        state = _conscript_state(seed)
        effects.resolve_card(state, _conscript_card(mode="create"))
        (recruit,) = state.player.hand
        assert recruit.is_companion
        assert recruit.nation == "inazuma"


def test_the_default_pool_is_exactly_the_csharp_roster_filter():
    """C#: `CompanionRoster.All.Where(card => card.Nation == "inazuma")`
    (KokomiConscript.cs:112-114). Sim: loader.companion_pool('inazuma'). The
    pin is that the sim's default argument selects that same set."""
    pool = loader.companion_pool("inazuma")
    assert pool, "the inazuma companion pool is empty"
    assert {c.nation for c in pool} == {"inazuma"}


def test_no_shipped_card_overrides_the_conscript_nation():
    """The `nation` key is expressible in the sim DSL and NOT expressible in
    C# -- gen_klee_cards.py:3147-3153 emits amount/mode/cost_override and
    nothing else, and KokomiConscript.Run has no nation parameter. As long as
    no sheet sets it the two sides cannot diverge; the day one does, this pin
    goes red instead of the mod going quiet."""
    offenders = []
    for card in loader._card_index().values():
        for fx in card.effects or []:
            if fx.get("op") == "conscript" and "nation" in fx:
                offenders.append((card.id, fx["nation"]))
    assert offenders == [], (
        "conscript `nation` override(s) found; C# KokomiConscript has no "
        "nation parameter, so these would silently be inazuma in the mod")


# ---------------------------------------------------------------------------
# 4. Kurage direct `p.block +=` bypass -- MATCHES C#, and the bypass is RULED.
#
# The pulse writes Block raw (effects.py:2652-2655), skipping
# powers.modify_block_gained. That funnel's own docstring
# (powers.py:75-81) says passive/power Block is deliberately exempt from
# Frail and Dexterity, and KuragePowers.cs:100-105 cites the same ruling:
#     "NC-11 (R116, Errata Batch 2 item 4): power-sourced block is RAW.
#      Unpowered, not Move, so neither Frail nor Dexterity sees it -- tier0
#      writes `p.block +=` here, deliberately bypassing
#      powers.modify_block_gained."
# ---------------------------------------------------------------------------

def _pulse_block(state):
    return sum(ev["amount"] for ev in state.log if ev["event"] == "block")


def test_kurage_pulse_block_ignores_frail():
    """Frail is a CARD-block debuff. The jellyfish's mending is power-sourced,
    so it pays in full. Parity pin: effects.py:2652-2655 vs
    KuragePowers.cs:96-106 (ValueProp.Unpowered)."""
    state = make_state()
    p = state.player
    p.powers["kurage_summon"] = 1
    p.powers["kurage_ward"] = 12
    p.powers["frail"] = 3

    effects.player_turn_end_triggers(state)

    expected = C.KURAGE_PULSE_BLOCK + 12
    assert _pulse_block(state) == expected
    assert p.block == expected


def test_kurage_pulse_block_ignores_dexterity():
    """The other half of the same exemption: Dexterity lives in
    modify_block_gained (powers.py:102), which this path never enters."""
    state = make_state()
    p = state.player
    p.powers["kurage_summon"] = 1
    p.powers["kurage_ward"] = 12
    p.powers["dexterity"] = 5

    effects.player_turn_end_triggers(state)

    assert _pulse_block(state) == C.KURAGE_PULSE_BLOCK + 12


def test_the_card_block_funnel_still_bites_so_the_bypass_is_specific():
    """Control: the same Frail that the pulse ignores does reduce ordinary
    card Block. The bypass is a property of power-sourced Block, not a hole
    in Frail."""
    p = make_state().player
    p.powers["frail"] = 3
    assert powers.modify_block_gained(p, 12) == int(12 * C.FRAIL_BLOCK_MULT)


# ---------------------------------------------------------------------------
# 5. Per-effect-dict relic no-dedupe -- MATCHES the C# dispatch shape.
#
# relics.py walks `player.relic_effects` and acts on EVERY dict; two copies of
# the same relic pay twice. That is the same shape as the mod's own relic
# dispatch -- BombPower.NotifyDetonationListeners iterates
# `player.Relics.ToList()` and fires each instance, with no dedupe by type
# (BombPower.cs:502-508).
#
# NO DIRECT C# COUNTERPART EXISTS for these particular hooks: festive_popper,
# prismatic_gem and Red Skull are BASE-GAME relics that tier05 models
# (tier05/content/relics.yaml); klee-mod ships only its own four relics. So
# the ledger's "harness-only" note stands on the reachability argument, not on
# a C# behaviour: HeldRelics.add is idempotent per id (tier05/relics.py:327)
# and the reward rolls draw from `unowned_common` / `unowned_ancient`
# (tier05/relics.py:129, 204), so a legal run cannot hold two.
#
# These pins guard the EXECUTION, which is what becomes load-bearing the day
# any source hands out a second copy.
# ---------------------------------------------------------------------------

def test_two_identical_combat_start_aoe_dicts_both_fire():
    """Per-effect-dict, not per-hook: duplicates stack (relics.py:133-136)."""
    state = make_state(enemies=[make_enemy(hp=100)])
    state.player.relic_effects = [
        {"hook": "combat_start_aoe", "amount": 9},
        {"hook": "combat_start_aoe", "amount": 9},
    ]
    relics.reset_combat(state)

    relics.apply_combat_start(state)

    assert state.enemies[0].hp == 100 - 18


def test_two_identical_every_n_turns_energy_dicts_both_fire():
    """The turn-start loop has the same shape (relics.py:186-193)."""
    state = make_state()
    state.player.relic_effects = [
        {"hook": "every_n_turns_energy", "n": 2, "amount": 1},
        {"hook": "every_n_turns_energy", "n": 2, "amount": 1},
    ]
    relics.reset_combat(state)
    before = state.player.energy

    relics.on_player_turn_start(state, turn=2)

    assert state.player.energy == before + 2


def test_two_identical_combat_start_block_dicts_both_fire():
    """Same again on the block hook -- the no-dedupe is a property of the
    loop, not of one hook (relics.py:110-114)."""
    state = make_state()
    state.player.relic_effects = [
        {"hook": "combat_start_block", "amount": 4},
        {"hook": "combat_start_block", "amount": 4},
    ]
    relics.reset_combat(state)

    relics.apply_combat_start(state)

    assert state.player.block == 8


def test_conditional_power_is_the_one_hook_that_does_dedupe():
    """CHANGE DETECTOR, NOT A RATIFIED PARITY CLAIM.

    `reevaluate_conditionals` keys its bookkeeping on
    `cond:{power}:{when}:{threshold}` (relics.py:221), so two IDENTICAL
    conditional_power dicts collapse into a single application while every
    other hook stacks. There is no C# Red Skull to arbitrate this against --
    it is a base-game relic klee-mod does not implement -- and duplicates are
    unreachable in a legal run, so S7 recorded the asymmetry rather than
    "fixing" one side toward the other. This test exists so the asymmetry
    cannot change silently."""
    state = make_state(hp=20)
    state.player.max_hp = 100
    state.player.relic_effects = [
        {"hook": "conditional_power", "power": "strength", "amount": 3,
         "when": "hp_below", "threshold": 0.5},
        {"hook": "conditional_power", "power": "strength", "amount": 3,
         "when": "hp_below", "threshold": 0.5},
    ]
    relics.reset_combat(state)

    relics.reevaluate_conditionals(state)

    assert state.player.powers.get("strength", 0) == 3      # not 6


def test_conditional_power_dicts_that_differ_do_both_apply():
    """The dedupe is keyed, not blanket: two conditional_power dicts with
    different thresholds are different keys and both land."""
    state = make_state(hp=20)
    state.player.max_hp = 100
    state.player.relic_effects = [
        {"hook": "conditional_power", "power": "strength", "amount": 3,
         "when": "hp_below", "threshold": 0.5},
        {"hook": "conditional_power", "power": "strength", "amount": 3,
         "when": "hp_below", "threshold": 0.25},
    ]
    relics.reset_combat(state)

    relics.reevaluate_conditionals(state)

    assert state.player.powers.get("strength", 0) == 6
