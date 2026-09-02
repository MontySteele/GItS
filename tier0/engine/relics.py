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
    combat_start_spark       {hook, amount}                 Klee only (Spark)
    every_n_turns_energy     {hook, n, amount}              when turn % n == 0
    every_n_turns_draw       {hook, n, amount}              when turn % n == 0
    on_first_hp_loss_draw    {hook, amount}                 once per combat
    card_name_damage_bonus   {hook, substring, amount}      flat +dmg rider
    conditional_power        {hook, power, amount, when, threshold}   Red Skull
    charge_per_exhaust       {hook, amount}                 Kokomi only (RATE)
    burst_per_exhaust        {hook, amount}                 Kokomi only (RATE)
    spotlight_both_modes     {hook}                         Furina only (FLAG)
    damage_per_exhaust       {hook, amount}                 unpowered, random enemy

The last three are RULE CHANGES rather than effects, and are dispatched
differently for that reason -- see "Touch of Orobas" below.

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
    "combat_start_aoe", "combat_start_spark",
    "every_n_turns_energy", "every_n_turns_draw",
    "on_first_hp_loss_draw", "card_name_damage_bonus", "conditional_power",
    "charge_per_exhaust", "burst_per_exhaust", "spotlight_both_modes",
    "damage_per_exhaust",
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
        elif hook == "combat_start_spark":
            # Klee's upgraded starter (Dodoco Tales, red-pen item 5 -- the
            # relic displayed as "Explosive Frags" until R69 renamed it off
            # the Rare Power card of that name).
            # A WINDFALL, not a rate: the rejected design doubled her
            # per-detonation income, which compounds with every bomb she
            # ever plays; this is a fixed opening bank that a long fight
            # dilutes. That is why it survived red-pen where the doubling
            # did not, and the shape matters more than the number.
            #
            # Inert for anyone without the Spark system, so an Orobas
            # variant that somehow reached another character grants nothing
            # rather than silently minting a resource they cannot spend.
            # Gated on the starter's own hook rather than on a character id:
            # the upgraded relic ADDS to the base behaviour rather than
            # replacing it (the C# ExplosiveFrags keeps the detonation
            # listener), so spark_on_detonation is still present and is the
            # honest test for "this player runs the Spark economy".
            #
            # AND NOT UNDER THE KLEE OVERHAUL (QUARANTINED, C.KLEE_OVERHAUL).
            # Rule 4 says Sparks come ONLY from explosions, so an act-2 Touch
            # of Orobas keeps the per-explosion RATE and loses the OPENING
            # WINDFALL -- otherwise the upgrade hands out a bank before any
            # Bomb has gone off, which is the opposite of what R242's own
            # opening Spark was priced against. The mod gates the identical
            # clause at `ExplosiveFrags.AfterPlayerTurnStart` on the same flag,
            # and its `OnBombExploded` half stays live.
            from tier0.engine import klee_overhaul  # late import (cycle)
            amt = int(fx["amount"])
            if (amt > 0 and "spark_on_detonation" in p.relic_hooks
                    and not klee_overhaul.live(state)):
                from tier0.engine import effects   # late import (cycle)
                effects.gain_sparks(state, amt)
    # conditional_power is evaluated at combat start too (Red Skull may already
    # be active if the fight opens below the HP threshold).
    reevaluate_conditionals(state)


def _heal(state: CombatState, amount: int) -> None:
    p = state.player
    if amount <= 0:
        return
    healed = min(amount, p.max_hp - p.hp)
    if healed > 0:
        p.hp += healed
        state.emit("heal", amount=healed, source="relic")


# ---------------------------------------------------------------------------
# Touch of Orobas: the upgraded-starter reads.
#
# Orobas (act-2 Ancient) swaps the STARTER relic for an upgraded form, so what
# it does depends entirely on who holds it. Modelled narrowly and per character
# ([USER] ruling 2026-07-26, option 1): one owner-gated row per variant in
# tier05/content/relics.yaml, no relic-upgrade table.
#
# Klee's variant ADDS an effect (`combat_start_spark`), which is why it is a
# branch in apply_combat_start above like every other relic. The other two do
# not add anything -- they CHANGE A RULE the kit already runs every fight:
#
#   Kokomi  Pearl of Insight       the exhaust funnel's accrual RATE
#   Furina  The Curtain Never Falls  the Spotlight's mode EXCLUSIVITY
#
# A rule change has no site at combat start to fire from; it has to be read
# where the rule runs. So these two are READS rather than writes, called from
# refpowers.after_card_exhausted and effects/combat's Spotlight path. Same
# layer discipline either way: both open on `if not player.relic_effects`, so
# the frozen battery never reaches them.
#
# THE NUMBERS LIVE ON THE RELIC, and are read off it rather than restated at
# the grant site. That is the C#'s own shape and the reason for it is on the
# record: `PearlOfInsightRelic` declared doubled constants that were read by
# nothing but its own description string, so the relic panel promised doubled
# accrual and the funnel granted the base rate (audit sec.1.1, pinned by
# tier0/tests/test_starter_relic_upgrades.py). Restating the numbers at the
# grant site is exactly how the two came to disagree.
# ---------------------------------------------------------------------------

def exhaust_accrual(player, charge: int, burst: int) -> tuple[int, int]:
    """Kokomi's per-exhaust (Charge, Burst) rates, after any relic override.

    `charge`/`burst` are the BASE rates the caller would otherwise grant
    (C.CHARGE_PER_EXHAUST / C.KOKOMI_BURST_PER_EXHAUST). A held Pearl of
    Insight REPLACES them -- it is not additive, mirroring
    `KokomiResourceHooks.ExhaustCharge/ExhaustBurst`, which pick one value or
    the other rather than summing.

    The caller is already inside the `tamakushi_casket` gate, so this needs no
    economy test of its own: a player with no Charge engine never asks.
    """
    if not player.relic_effects:
        return charge, burst
    for fx in player.relic_effects:
        hook = fx.get("hook")
        if hook == "charge_per_exhaust":
            charge = int(fx["amount"])
        elif hook == "burst_per_exhaust":
            burst = int(fx["amount"])
    return charge, burst


# ---------------------------------------------------------------------------
# Exhaust payouts.
# ---------------------------------------------------------------------------

def on_card_exhausted(state: CombatState) -> None:
    """damage_per_exhaust: "whenever you Exhaust a card, deal X damage to a
    random enemy" (EB-82; Forgotten Soul, the relic Grave of the Forgotten
    grants).

    Built as UNUSED MACHINERY (2026-08-12) and ARMED by the conversion that
    followed: `forgotten_soul` in `tier05/content/relics.yaml` carries the
    hook and Grave of the Forgotten's Accept branch is its one source. The
    order is the point -- the event-relic admission rule forbids inventing an
    engine hook inline inside a conversion, so the hook shipped first and on
    its own. The frozen battery still cannot feel it: battery players carry
    no `relic_effects`, and the function opens on that.

    Shape decisions, all of them the existing engine's rather than new:

    * UNPOWERED, like `combat_start_aoe` and Speedster's per-draw hit. The
      relic is not an attack, so Strength must not scale it and no attack
      hook may fire off it.
    * ONE random living enemy per exhaust, drawn from `state.rng` through
      the same `rng.choice(living)` the `random_enemy` target spec uses. A
      dead field means no target and no draw at all, so an exhaust with
      the board already clear consumes no randomness.
    * Called from the ONE exhaust funnel (`refpowers.after_card_exhausted`),
      which is what makes "whenever one of your cards is Exhausted"
      structural rather than per-site discipline -- the same argument the
      Tamakushi Casket accrual is written on.
    """
    p = state.player
    if not p.relic_effects:
        return
    for fx in p.relic_effects:
        if fx.get("hook") != "damage_per_exhaust":
            continue
        amount = int(fx["amount"])
        living = state.living_enemies
        if amount <= 0 or not living:
            continue
        refpowers.unpowered_damage(state, state.rng.choice(living), amount)
        state.emit("relic_exhaust_damage", amount=amount)


def spotlight_both_modes(player) -> bool:
    """Furina's upgraded starter (The Curtain Never Falls, red-pen R2).

    Both Spotlight modes in force permanently: her own cards mint Fanfare
    (Center Stage's half) AND Companions are multiplied (Guest Cast's half).
    R2 reading 1: the upgrade removes the two modes' EXCLUSIVITY, never their
    TARGETING -- neither half reaches across to the other's card class, so an
    upgraded Furina still gets no numeric boost on her own cards and her
    Companions still mint no Fanfare.

    Gated on `ethereal_spotlight` in `relic_hooks` for the same reason
    `combat_start_spark` is gated on `spark_on_detonation`: the honest test
    for "this player runs the Spotlight economy" is the starter's own hook,
    which the upgrade keeps rather than removes (C# `CurtainNeverFalls` is a
    FLAG -- `SpotlightSystem` holds every gate, the relic holds none). An
    owner-gated row should never reach anyone else; this is the belt as well
    as the braces.
    """
    if not player.relic_effects:
        return False
    if "ethereal_spotlight" not in player.relic_hooks:
        return False
    return any(fx.get("hook") == "spotlight_both_modes"
               for fx in player.relic_effects)


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
    reevaluate_conditionals(state)


def reevaluate_conditionals(state: CombatState) -> None:
    """conditional_power (Red Skull): while a condition holds, the player has
    +amount of a power. Re-evaluated cleanly against the delta ALREADY applied,
    so toggling never drifts or double-applies -- the stored delta is the single
    source of truth for what this relic currently contributes to the stack.
    Public because combat HP changes can cross the threshold between turns.
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
