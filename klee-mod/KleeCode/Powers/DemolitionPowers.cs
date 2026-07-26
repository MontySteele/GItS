using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Demolition-archetype player powers (power-card pass). Reference
/// implementation tier0/engine/effects.py detonate_bombs and
/// player_turn_start_triggers; every number here is LAW from tier0 -- never
/// re-derived.
/// </summary>
public static class DemolitionConstants
{
    /// <summary>tier0 constants.py DETONATION_SPLASH_BURST = 3.</summary>
    public const int SplashBurst = 3;

    /// <summary>tier0 constants.py DETONATION_SPLASH_PROC_CAP = 3 (per turn).</summary>
    public const int SplashProcCapPerTurn = 3;

    /// <summary>tier0 constants.py PLAYTIME_BOMB_DAMAGE = 5.</summary>
    public const int PlaytimeBombDamage = 5;
}

/// <summary>
/// Explosives Workshop: each stack adds to EVERY bomb detonation's damage.
/// Read at detonation in <see cref="BombPower"/>, BEFORE amplification --
/// the sim computes `bomb.damage + bonus + bomb_damage_up` and only then
/// hands the total to the elemental pipeline (effects.py detonate_bombs).
/// </summary>
public sealed class BombDamageUpPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Explosives Workshop"),
        ("description", "Your [gold]Bombs[/gold] detonate for {Amount} more damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

}

/// <summary>
/// Blazing Delight: each bomb detonation splashes ALL enemies for Amount
/// damage and grants Burst energy, capped at
/// <see cref="DemolitionConstants.SplashProcCapPerTurn"/> procs per turn.
///
/// Sim semantics (effects.py detonate_bombs): per BOMB, not per card; the
/// splash is a raw `hp -=` -- element-less (no aura, no reaction) and
/// block-bypassing, hence Unblockable|Unpowered here; the Burst grant sits
/// INSIDE the proc gate, so a capped detonation grants nothing. The cap
/// counter zeroes at TURN START before bombs detonate, exactly like the sim
/// (R35: the earlier end-of-turn reset leaned on a closed-world "nothing
/// procs on enemy turns" argument -- the ruling replaces the argument with
/// the sim's structure). Ordering proof: hook listeners iterate allies
/// before enemies, so this player-power reset runs before any enemy
/// BombPower detonation in the same BeforeSideTurnStart broadcast.
/// </summary>
public sealed class DetonationSplashPower
    : PowerModel, ILocalizationProvider, IBombDetonationListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Blazing Delight"),
        ("description",
            "When a [gold]Bomb[/gold] detonates: deal {Amount} damage to ALL "
          + "enemies, ignoring Block, and gain 3 [gold]Burst Energy[/gold]. "
          + "Up to 3 times per turn."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    private int _procsThisTurn;

    public async Task OnBombDetonated(
        PlayerChoiceContext choiceContext, Creature? applier, Creature target,
        int damage)
    {
        if (applier != Owner || Amount <= 0) return;
        if (_procsThisTurn >= DemolitionConstants.SplashProcCapPerTurn) return;
        _procsThisTurn++;

        var enemies = CombatState.HittableEnemies.ToList();
        if (enemies.Count > 0)
        {
            await CreatureCmd.Damage(
                choiceContext, enemies, Amount,
                ValueProp.Unblockable | ValueProp.Unpowered,
                dealer: null, cardSource: null);
        }

        await KleeBurstResource.Gain(
            choiceContext, Owner, DemolitionConstants.SplashBurst,
            cardSource: null);
    }

    public override Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side == CombatSide.Player) _procsThisTurn = 0;
        return Task.CompletedTask;
    }
}

/// <summary>
/// Explosive Frags: each bomb detonation applies Amount Vulnerable to the
/// detonated enemy, if it survived (sim: `if vuln and enemy.alive`).
/// Per bomb, uncapped -- the sim has no proc gate here.
/// </summary>
public sealed class DetonationVulnPower
    : PowerModel, ILocalizationProvider, IBombDetonationListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Explosive Frags"),
        ("description",
            "When a [gold]Bomb[/gold] detonates, apply {Amount} "
          + "[gold]Vulnerable[/gold] to that enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task OnBombDetonated(
        PlayerChoiceContext choiceContext, Creature? applier, Creature target,
        int damage)
    {
        if (applier != Owner || Amount <= 0) return;
        if (target.IsDead) return;

        await PowerCmd.Apply<VulnerablePower>(
            choiceContext, target, Amount, applier: Owner, cardSource: null);
    }
}

/// <summary>
/// Playtime Forever: at the start of your turn, place a Bomb
/// (<see cref="DemolitionConstants.PlaytimeBombDamage"/> damage) on a random
/// enemy and gain 1 Spark, Amount times.
///
/// Sim (effects.py player_turn_start_triggers): the bomb needs a living
/// enemy; the Spark is granted unconditionally inside the loop. Turn-start
/// triggers run AFTER bombs detonate in the sim's turn order, which the hook
/// choice preserves: detonation rides BeforeSideTurnStart, this rides
/// AfterPlayerTurnStart. A bomb placed here therefore sits through the enemy
/// turn and detonates next turn (or early, on an Attack hit) -- same cadence
/// as the sim's `turn_placed` bookkeeping.
/// </summary>
public sealed class BombAndSparkPerTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Playtime Forever"),
        ("description",
            "At the start of your turn, place a 5-damage [gold]Bomb[/gold] "
          + "on a random enemy and gain 1 [gold]Spark[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;

        for (var i = 0; i < Amount; i++)
        {
            var candidates = CombatState.HittableEnemies.ToList();
            if (candidates.Count > 0)
            {
                var target = CombatState.RunState.Rng.CombatTargets.NextItem(candidates);
                if (target != null)
                {
                    await BombPower.Place(
                        choiceContext, target,
                        DemolitionConstants.PlaytimeBombDamage,
                        Owner, cardSource: null);
                }
            }
            await SparkPower.Gain(choiceContext, Owner, 1, cardSource: null);
        }
    }
}
