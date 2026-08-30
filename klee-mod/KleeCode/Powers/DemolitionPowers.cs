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
/// The bomb-damage STAT: each stack adds to EVERY bomb detonation's damage.
/// Read at detonation in <see cref="BombPower"/>, BEFORE amplification --
/// the sim computes `bomb.damage + bonus + bomb_damage_up` and only then
/// hands the total to the elemental pipeline (effects.py detonate_bombs).
///
/// EB-118 sec.4.4 (2026-08-24) took the card off it. Explosives Workshop no
/// longer applies this directly; <see cref="ExplosivesWorkshopPower"/> does,
/// once per turn, when the player discards or Exhausts. So the TITLE moved
/// with the card: this is now the derived stat and says so, and the card's
/// name belongs to the power the card actually installs. Nothing else about
/// it changes, and deliberately: it is still the ONE bomb-damage number, so
/// a Bomb armed before a trigger and one armed after detonate the same.
/// </summary>
public sealed class BombDamageUpPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Bomb Damage"),
        ("description", "Your [gold]Bombs[/gold] detonate for {Amount} more damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

}

/// <summary>
/// Explosives Workshop (EB-118 sec.4.4): the first time each turn the owner
/// discards or Exhausts a card, add Amount to <see cref="BombDamageUpPower"/>
/// for the rest of the combat.
///
/// ONE WINDOW OVER TWO EVENT FAMILIES. The latch is a single bool, not one
/// per hook, because "the first time each turn you discard OR Exhaust" is one
/// trigger: a turn that discards and then Exhausts pays once. Sim twin:
/// `effects.note_rotation_event`, which asks whether the COMBINED
/// discard+exhaust count for the turn is exactly 1 -- the same question, in
/// the shape the sim's counters make natural.
///
/// THE RESET RIDES BeforeSideTurnStart(Player), matching the sim, where both
/// counters are zeroed at the player's turn start. The window therefore runs
/// from one player turn start to the next and spans the enemy turn, so an
/// Ethereal card burning off at end of turn can be the turn's first event.
/// That is the sim's window, deliberately copied rather than tightened to
/// "your own side's turn" -- the tighter guard the base game's Tingsha uses
/// would have made the two engines disagree on exactly that card.
///
/// NO FILTER ON THE VICTIM. Unlike the Kokomi rotation law's funnel, a
/// Status or Curse leaving hand pays here: sec.4.4 names Klee's own
/// status-exhaust route as a trigger. What is checked is OWNERSHIP, which
/// the sim gets for free with one seat and co-op does not: a partner's
/// discard is not the owner's first event.
/// </summary>
public sealed class ExplosivesWorkshopPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Explosives Workshop"),
        ("description",
            "The first time each turn you discard or Exhaust a card, your "
          + "[gold]Bombs[/gold] deal {Amount} more damage this combat."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    private bool _paidThisTurn;

    public override Task AfterCardDiscarded(
        PlayerChoiceContext choiceContext, CardModel card) =>
        Pay(choiceContext, card);

    public override Task AfterCardExhausted(
        PlayerChoiceContext choiceContext, CardModel card,
        bool causedByEthereal) =>
        Pay(choiceContext, card);

    public override Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side == CombatSide.Player) _paidThisTurn = false;
        return Task.CompletedTask;
    }

    private async Task Pay(PlayerChoiceContext choiceContext, CardModel card)
    {
        if (Amount <= 0 || _paidThisTurn) return;
        if (card.Owner?.Creature != Owner) return;

        _paidThisTurn = true;
        Flash();
        await PowerCmd.Apply<BombDamageUpPower>(
            choiceContext, Owner, Amount, applier: Owner, cardSource: null);
    }
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
            // EB-89: the grant and the per-turn cap are interpolated.
            // {Amount} is a DynamicVar token, so its braces are doubled
            // to survive interpolation.
            $"When a [gold]Bomb[/gold] detonates: deal {{Amount}} damage to "
          + "ALL enemies, ignoring Block, and gain "
          + $"{DemolitionConstants.SplashBurst} [gold]Burst Energy[/gold]. "
          + $"Up to {DemolitionConstants.SplashProcCapPerTurn} times per "
          + "turn."),
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

        // CombatState?. -- the idiom every neighbouring file uses. A power can
        // outlive its combat by a frame (a detonation resolving as the room
        // tears down), and this hook is reached from an async continuation
        // where the NRE lands as a black screen, not an error.
        var enemies = CombatState?.HittableEnemies.ToList();
        if (enemies is { Count: > 0 })
        {
            await CreatureCmd.Damage(
                choiceContext, enemies, Amount,
                ValueProp.Unblockable | ValueProp.Unpowered,
                dealer: null, cardSource: null, cardPlay: null);
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
            await SparkPower.Gain(choiceContext, Owner, 1, cardSource: null,
                source: "power:bomb_and_spark_per_turn/turn_start");
        }
    }
}
