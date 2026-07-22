"""The COMBAT-SIDE relic engine (relic pass).

WHY THIS FILE EXISTS
--------------------
Relics add combat effects the frozen 3.0 battery must never feel. The safety
mechanism is a single seam: relic combat effects are read off the NEW field
``Player.relic_effects`` (a list of dicts keyed by ``hook``), which is EMPTY on
every battery player -- they are built by ``loader.build_player`` from character
yaml that carries no ``relic_effects``. Every public function below therefore
opens with ``if not player.relic_effects: return`` (or returns 0), so on the
battery this whole module is dead code. Same guard discipline the
``spark_on_detonation`` path and ``engine/refpowers.py`` already keep.

Mirrors the card-DSL idiom: card effects are dicts keyed by ``op`` (effects.py),
relic effects are dicts keyed by ``hook``.

HOOK VOCABULARY (combat-scoped -- the ONLY hooks acted on here):
    combat_start_block       {hook, amount}
    combat_start_power       {hook, power, amount}
    combat_start_heal        {hook, amount}                 capped at max_hp
    combat_start_energy      {hook, amount}                 TURN 1 only
    combat_start_draw        {hook, amount}                 TURN 1 only
    combat_start_enemy_power {hook, power, amount}          applied to ALL enemies
    combat_start_aoe         {hook, amount}                 unpowered dmg to all
    every_n_turns_energy     {hook, n, amount}              when turn % n == 0
    every_n_turns_draw       {hook, n, amount}              when turn % n == 0
    on_first_hp_loss_draw    {hook, amount}                 once per combat
    card_name_damage_bonus   {hook, substring, amount}      flat +dmg rider
    conditional_power        {hook, power, amount, when, threshold}   Red Skull

RUN-SCOPED hooks (applied in tier05, NOT here) are recognised and IGNORED
silently so they never trip the UNIMPLEMENTED alarm; anything in NEITHER set is
logged loudly (house rule: never approximate a DSL gap silently).
"""

from __future__ import annotations

from tier0.engine import powers, refpowers
from tier0.engine.state import CombatState

# Hooks this module actively implements.
COMBAT_HOOKS = frozenset({
    "combat_start_block", "combat_start_power", "combat_start_heal",
    "combat_start_energy", "combat_start_draw", "combat_start_enemy_power",
    "combat_start_aoe", "every_n_turns_energy", "every_n_turns_draw",
    "on_first_hp_loss_draw", "card_name_damage_bonus", "conditional_power",
})

# Hooks handled in the run layer (tier05/model.py, tier05/relics.py). They may
# legitimately ride along in relic_effects; ignore them here without alarm.
RUN_HOOKS = frozenset({
    "on_pickup_maxhp", "gold_on_pickup", "gold_per_fight", "post_rest_heal",
    "shop_heal", "post_rest_energy", "book_of_five_rings", "fishing_rod",
    "elite_combat_start",
})

# The two conditions conditional_power understands. Anything else is logged.
_CONDITIONS = ("hp_below",)


def _validate(state: CombatState) -> None:
    """Loud UNIMPLEMENTED for any hook string in neither vocabulary. Run once
    per combat (from apply_combat_start) so it never spams per turn."""
    for fx in state.player.relic_effects:
        hook = fx.get("hook")
        if hook in COMBAT_HOOKS or hook in RUN_HOOKS:
            if hook == "conditional_power" and fx.get("when") not in _CONDITIONS:
                state.emit("UNIMPLEMENTED", hook=hook, when=fx.get("when"),
                           reason="conditional_power 'when' not understood")
            continue
        state.emit("UNIMPLEMENTED", hook=hook,
                   reason="relic hook not handled by the combat engine")


# ---------------------------------------------------------------------------
# Fight start.
# ---------------------------------------------------------------------------

def reset_combat(state: CombatState) -> None:
    """Clear per-combat relic counters. Called at true fight start (before the
    first player turn) so a reused Player object cannot leak state across
    fights."""
    p = state.player
    if not p.relic_effects:
        return
    p.first_hp_loss_fired = False
    p.relic_conditional_applied = {}


def apply_combat_start(state: CombatState) -> None:
    """The combat_start_* family. Called ONCE, on the first player turn, AFTER
    the turn-start block clear / energy reset / hand draw -- so block survives
    the clear, and the TURN-1-only energy/draw riders stack on top of the
    turn's own refill and draw rather than being wiped by them.

    Nothing acts between fight start and the first player turn's setup (enemies
    do not move first), so applying the persistent riders (block/power/heal/
    enemy_power/aoe) here is behaviourally identical to applying them at fight
    start, and correct for the energy/draw riders that the earlier site cannot
    host.
    """
    p = state.player
    if not p.relic_effects:
        return
    _validate(state)
    for fx in p.relic_effects:
        hook = fx.get("hook")
        if hook == "combat_start_block":
            amt = int(fx["amount"])
            if amt > 0:
                p.block += amt
                state.emit("relic_block", amount=amt)
        elif hook == "combat_start_power":
            powers.apply_power(state, p, fx["power"], int(fx["amount"]),
                               applier=p)
        elif hook == "combat_start_heal":
            _heal(state, int(fx["amount"]))
        elif hook == "combat_start_energy":
            amt = int(fx["amount"])
            p.energy += amt
            state.emit("relic_energy", amount=amt, turn=state.turn)
        elif hook == "combat_start_draw":
            n = int(fx["amount"])
            if n > 0:
                state.draw(n)
                state.emit("extra_draw", amount=n)
        elif hook == "combat_start_enemy_power":
            for enemy in state.living_enemies:
                powers.apply_power(state, enemy, fx["power"], int(fx["amount"]),
                                   applier=p)
        elif hook == "combat_start_aoe":
            amt = int(fx["amount"])
            for enemy in list(state.living_enemies):
                refpowers.unpowered_damage(state, enemy, amt)
    # conditional_power is evaluated at combat start too (Red Skull may already
    # be active if the fight opens below the HP threshold).
    _reeval_conditionals(state)


def _heal(state: CombatState, amount: int) -> None:
    p = state.player
    if amount <= 0:
        return
    healed = min(amount, p.max_hp - p.hp)
    if healed > 0:
        p.hp += healed
        state.emit("heal", amount=healed, source="relic")


# ---------------------------------------------------------------------------
# Player turn start.
# ---------------------------------------------------------------------------

def on_player_turn_start(state: CombatState, turn: int) -> None:
    """every_n_turns_energy / every_n_turns_draw (on turns where turn % n == 0)
    and the conditional_power re-eval. Runs EVERY player turn (including turn 1;
    the combat_start energy/draw riders in apply_combat_start are turn-1 ONLY
    and are a separate family)."""
    p = state.player
    if not p.relic_effects:
        return
    for fx in p.relic_effects:
        hook = fx.get("hook")
        if hook == "every_n_turns_energy":
            n = int(fx["n"])
            if n > 0 and turn % n == 0:
                amt = int(fx["amount"])
                p.energy += amt
                state.emit("relic_energy", amount=amt, turn=turn)
        elif hook == "every_n_turns_draw":
            n = int(fx["n"])
            if n > 0 and turn % n == 0:
                amt = int(fx["amount"])
                if amt > 0:
                    state.draw(amt)
                    state.emit("extra_draw", amount=amt)
    _reeval_conditionals(state)


def _reeval_conditionals(state: CombatState) -> None:
    """conditional_power (Red Skull): while a condition holds, the player has
    +amount of a power. Re-evaluated cleanly against the delta ALREADY applied,
    so toggling never drifts or double-applies -- the stored delta is the single
    source of truth for what this relic currently contributes to the stack.
    """
    p = state.player
    for fx in p.relic_effects:
        if fx.get("hook") != "conditional_power":
            continue
        when = fx.get("when")
        if when not in _CONDITIONS:
            continue                          # already logged by _validate
        power = fx["power"]
        amount = int(fx["amount"])
        threshold = fx.get("threshold", 0.5)
        key = f"cond:{power}:{when}:{threshold}"
        met = False
        if when == "hp_below":
            met = p.hp <= threshold * p.max_hp
        want = amount if met else 0
        have = p.relic_conditional_applied.get(key, 0)
        if want != have:
            delta = want - have
            p.powers[power] = p.powers.get(power, 0) + delta
            p.relic_conditional_applied[key] = want
            state.emit("relic_conditional", power=power, delta=delta,
                       active=bool(want))


# ---------------------------------------------------------------------------
# HP loss and attack damage riders.
# ---------------------------------------------------------------------------

def note_hp_loss(state: CombatState) -> None:
    """on_first_hp_loss_draw: the FIRST time the player loses HP this combat,
    draw. Fires at most once per combat. Called from the enemy-damage site."""
    p = state.player
    if not p.relic_effects or p.first_hp_loss_fired:
        return
    p.first_hp_loss_fired = True
    for fx in p.relic_effects:
        if fx.get("hook") == "on_first_hp_loss_draw":
            n = int(fx["amount"])
            if n > 0:
                state.draw(n)
                state.emit("extra_draw", amount=n)


def card_damage_bonus(player, card) -> int:
    """card_name_damage_bonus: attacks whose card id OR name contains the
    substring deal +amount. Additive, folded in BEFORE strength/vulnerable --
    the caller adds this to the card's base amount, so it stacks like any flat
    +damage rider."""
    if not player.relic_effects:
        return 0
    bonus = 0
    for fx in player.relic_effects:
        if fx.get("hook") != "card_name_damage_bonus":
            continue
        sub = fx["substring"]
        if sub in card.id or sub in (card.name or ""):
            bonus += int(fx["amount"])
    return bonus
