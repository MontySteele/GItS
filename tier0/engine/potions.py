"""The COMBAT-SIDE potion engine (potion pass).

WHY THIS FILE EXISTS
--------------------
Potions add mid-combat, player-initiated effects the frozen 3.0 battery must
never feel. The safety mechanism is the same single seam the relic engine
(engine/relics.py) uses: potions live on the NEW field ``Player.potions`` (a
list of potion-id strings), which is EMPTY on every battery player -- they are
built by ``loader.build_player``, which never sets it; only
``build_player_from_ids(potions=...)`` in the run layer does. Every public
function below opens with ``if not player.potions: return`` (or returns
False/0), so on the battery this whole module is dead code. Same guard
discipline ``spark_on_detonation``, ``frail`` and the relic engine keep.

Payloads REUSE the already-implemented vocabulary -- block/heal/draw/energy
directly, ``powers.apply_power`` for strength/weak/vulnerable, and
``refpowers.unpowered_damage`` for direct damage. No new powers are invented.
An unknown potion id is logged loudly (UNIMPLEMENTED), never faked.

POTION VOCABULARY (id -> effect; amounts in constants.py):
    block_potion      gain POTION_BLOCK Block
    fire_potion       POTION_FIRE_DAMAGE unpowered damage to ONE enemy
    blood_potion      heal POTION_BLOOD_HEAL_FRACTION of max HP
    strength_potion   +POTION_STRENGTH Strength (combat-scoped; decays with the
                      combat like any power, gone next fight)
    swift_potion      draw POTION_SWIFT_DRAW
    weak_potion       POTION_WEAK Weak to one enemy
    fear_potion       POTION_FEAR_VULN Vulnerable to one enemy
    energy_potion     +POTION_ENERGY Energy
    fairy_in_a_bottle PASSIVE: on lethal damage, revive at
                      POTION_FAIRY_REVIVE_FRACTION of max HP (see
                      try_fairy_revive, called at the enemy-damage site)

USE POLICY: a bounded greedy heuristic, NOT a solver. try_use_potions runs at
the player's turn start (after the draw, before the pilot loop). Fairy is never
proactively drunk -- it is a passive revive handled at the lethal-damage site.
"""

from __future__ import annotations

from tier0 import constants as C
from tier0.engine import powers, refpowers
from tier0.engine.state import CombatState, Enemy, Player

# Potions the use-policy may proactively DRINK (fairy is passive; excluded).
DRINKABLE = frozenset({
    "block_potion", "fire_potion", "blood_potion", "strength_potion",
    "swift_potion", "weak_potion", "fear_potion", "energy_potion",
})
# Full recognised set (drinkable + the passive fairy). Anything outside this is
# logged UNIMPLEMENTED rather than silently faked.
KNOWN = DRINKABLE | {"fairy_in_a_bottle"}
# Potions whose effect needs an enemy target.
_TARGETED = frozenset({"fire_potion", "weak_potion", "fear_potion"})


# ---------------------------------------------------------------------------
# Effect application.
# ---------------------------------------------------------------------------

def apply_potion(state: CombatState, pid: str, target: Enemy | None = None) -> None:
    """Apply potion ``pid``'s effect to the fight, reusing existing mechanics.
    ``target`` is required (or defaulted) only for the targeted potions. Does
    NOT touch player.potions -- the caller (_drink) owns consumption. An
    unknown id logs UNIMPLEMENTED and does nothing."""
    p = state.player
    if pid in _TARGETED and target is None:
        target = _lowest_hp_enemy(state)
        if target is None:                    # no living enemy: nothing to hit
            state.emit("potion_fizzle", potion=pid, reason="no_target")
            return

    if pid == "block_potion":
        p.block += C.POTION_BLOCK
    elif pid == "fire_potion":
        refpowers.unpowered_damage(state, target, C.POTION_FIRE_DAMAGE)
    elif pid == "blood_potion":
        heal = int(C.POTION_BLOOD_HEAL_FRACTION * p.max_hp)
        healed = min(heal, p.max_hp - p.hp)
        if healed > 0:
            p.hp += healed
            state.emit("heal", amount=healed, source="potion")
    elif pid == "strength_potion":
        powers.apply_power(state, p, "strength", C.POTION_STRENGTH, applier=p)
    elif pid == "swift_potion":
        state.draw(C.POTION_SWIFT_DRAW)
    elif pid == "weak_potion":
        powers.apply_power(state, target, "weak", C.POTION_WEAK, applier=p)
    elif pid == "fear_potion":
        powers.apply_power(state, target, "vulnerable", C.POTION_FEAR_VULN,
                           applier=p)
    elif pid == "energy_potion":
        p.energy += C.POTION_ENERGY
    else:
        # fairy_in_a_bottle is passive and must never be routed here; any id
        # not in KNOWN is a real gap. Either way: log, do not fake.
        state.emit("UNIMPLEMENTED", potion=pid,
                   reason="potion id not applicable via apply_potion")
        return
    state.emit("potion_used", potion=pid,
               target=(getattr(target, "name", None) if pid in _TARGETED else None))


def _drink(state: CombatState, pid: str, target: Enemy | None = None) -> None:
    """Consume ONE ``pid`` from the player's held potions and apply it."""
    state.player.potions.remove(pid)
    apply_potion(state, pid, target)


# ---------------------------------------------------------------------------
# Incoming-damage estimation (heuristic; never crashes on non-attack intents).
# ---------------------------------------------------------------------------

def _intent_damage(state: CombatState, enemy: Enemy) -> int:
    """Approximate total damage this enemy's CURRENT intent would deal to the
    player this round (all hits), through the existing damage funnels. 0 for
    any non-attack intent. Approximate on purpose -- it drives a heuristic."""
    intent = enemy.current_intent()
    if intent.get("kind") != "attack":
        return 0
    amount = intent["amount"] + intent.get("ramp", 0) * max(
        0, state.turn - intent.get("ramp_after", 0))
    times = intent.get("times", 1)
    dmg = powers.modify_damage_dealt(enemy, amount)      # +strength, x weak
    dmg = powers.modify_damage_taken(state.player, dmg, enemy)  # x vulnerable
    return max(0, int(dmg)) * times


def estimate_incoming(state: CombatState) -> int:
    """Sum every living enemy's telegraphed attack damage for the coming enemy
    turn (pre player Block). Block is subtracted by the caller."""
    return sum(_intent_damage(state, e) for e in state.living_enemies)


def _biggest_attacker(state: CombatState) -> tuple[Enemy | None, int]:
    """The living enemy with the largest single telegraphed attack this round,
    and that damage. (None, 0) if no enemy is attacking."""
    best: Enemy | None = None
    best_dmg = 0
    for e in state.living_enemies:
        d = _intent_damage(state, e)
        if d > best_dmg:
            best, best_dmg = e, d
    return best, best_dmg


def _lowest_hp_enemy(state: CombatState) -> Enemy | None:
    living = state.living_enemies
    return min(living, key=lambda e: e.hp) if living else None


def _highest_hp_enemy(state: CombatState) -> Enemy | None:
    living = state.living_enemies
    return max(living, key=lambda e: e.hp) if living else None


def _has_boss(state: CombatState) -> bool:
    return any(e.is_boss for e in state.living_enemies)


# ---------------------------------------------------------------------------
# Use policy: bounded greedy, at most one defensive + one offensive per turn.
# ---------------------------------------------------------------------------

def try_use_potions(state: CombatState) -> None:
    """Called at the player's turn start (after the draw, before the pilot
    loop). Dead branch on the battery (potions empty)."""
    p: Player = state.player
    if not p.potions:
        return
    _try_defensive(state)
    # Offensive drinks are gated to ELITE/BOSS fights (node context set by the
    # run layer). "" (battery / normal) never reaches the offensive branch.
    if p.node_kind in ("elite", "boss"):
        _try_offensive(state)


def _try_defensive(state: CombatState) -> None:
    """If the coming enemy turn would drop the player to <= the safety margin,
    drink the best defensive potion held (block_potion > blood_potion). Fairy
    is NOT drunk here -- it is a passive revive."""
    p = state.player
    net = estimate_incoming(state) - p.block
    if net <= 0:
        return
    if p.hp - net > C.POTION_DEFENSIVE_MARGIN:
        return                                # projected to survive the turn
    for pid in ("block_potion", "blood_potion"):   # priority order
        if pid in p.potions:
            _drink(state, pid)
            return


def _try_offensive(state: CombatState) -> None:
    """Elite/boss only. At most ONE offensive potion per turn, in priority
    order: close a kill (fire) > blunt a big telegraphed hit (weak) > race a
    dangerous enemy / boss (fear, then strength). Conservative by design: on a
    plain elite with no big telegraph and nothing in fire range, nothing is
    drunk."""
    p = state.player

    # 1. fire_potion closes a kill outright.
    if "fire_potion" in p.potions:
        killable = [e for e in state.living_enemies
                    if 0 < e.hp <= C.POTION_FIRE_DAMAGE]
        if killable:
            _drink(state, "fire_potion", min(killable, key=lambda e: e.hp))
            return

    attacker, big = _biggest_attacker(state)
    big_hit = attacker is not None and big >= C.POTION_BIG_HIT_FRACTION * p.max_hp

    # 2. weak_potion blunts a big telegraphed hit (-25% damage dealt).
    if big_hit and "weak_potion" in p.potions:
        _drink(state, "weak_potion", attacker)
        return

    # 3. fear_potion (Vulnerable) races a dangerous enemy or the boss.
    if "fear_potion" in p.potions and (big_hit or _has_boss(state)):
        target = attacker if big_hit else _highest_hp_enemy(state)
        if target is not None:
            _drink(state, "fear_potion", target)
            return

    # 4. strength_potion races an elite/boss (combat-scoped +Strength).
    if "strength_potion" in p.potions and (big_hit or _has_boss(state)):
        _drink(state, "strength_potion")
        return


# ---------------------------------------------------------------------------
# Fairy in a Bottle: passive revive, called at the lethal-damage site.
# ---------------------------------------------------------------------------

def try_fairy_revive(state: CombatState) -> bool:
    """At the moment the player would die (hp <= 0 from a hit), if a fairy is
    held, consume it and set hp to POTION_FAIRY_REVIVE_FRACTION of max HP
    instead. Returns whether it saved the player. Dead branch on the battery
    (no potions). A multi-hit intent can still kill after the fairy is spent:
    once consumed it is gone, so the next lethal hit finds nothing to save it."""
    p = state.player
    if not p.potions or "fairy_in_a_bottle" not in p.potions:
        return False
    p.potions.remove("fairy_in_a_bottle")
    p.hp = max(1, int(C.POTION_FAIRY_REVIVE_FRACTION * p.max_hp))
    state.emit("fairy_revive", hp=p.hp)
    return True
