using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using System.Threading.Tasks;
using BaseLib.Abstracts;

namespace KleeMod.Powers;

/// <summary>
/// Spark-archetype player powers (power-card pass). Reference implementation
/// tier0/engine/combat.py spark_threshold and effects.py resolve_card /
/// player_turn_start_triggers. Numbers are LAW from tier0.
/// </summary>
public sealed class SparkPerTurnPower : PowerModel, ILocalizationProvider
{
    // Endless Fireworks: gain Amount Sparks at the start of your turn
    // (sim: player_turn_start_triggers, `spark_per_turn`).
    public List<(string, string)>? Localization => new()
    {
        ("title", "Endless Fireworks"),
        ("description",
            "At the start of your turn, gain {Amount} [gold]Spark[/gold]"
          + "{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner || Amount <= 0) return;
        await SparkPower.Gain(choiceContext, Owner, Amount, cardSource: null);
    }
}

/// <summary>
/// Spark Knight Style: attacks that cost 0 deal Amount more damage.
///
/// The sim's predicate is PAID cost (`state.current_card_cost == 0`), not
/// printed cost -- printed-0 attacks, Spark-freed attacks and anything else
/// zeroed all qualify. EnergyCost.GetResolved() is the game's own
/// "cost after it was played" accessor (IntimidatingHelmet precedent) and
/// captures X-cost values correctly. During a card's resolution a Spark-freed
/// attack still reads 0 (the Spark spend happens post-resolution), so the
/// mid-play read agrees with what was paid.
/// </summary>
public sealed class ZeroCostAttacksUpPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Spark Knight Style"),
        ("description", "Your Attacks that cost 0 deal {Amount} more damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        if (cardSource.EnergyCost.GetResolved() != 0) return 0m;
        return Amount;
    }
}

/// <summary>
/// True Spark Knight: the free-attack threshold drops by Amount, floored at 1
/// (sim: combat.py spark_threshold, `max(1, 3 - spark_threshold_down)`).
/// Pure marker -- <see cref="SparkPower"/> reads it for both the cost gate
/// and the spend, so gate and spend can never disagree.
/// </summary>
public sealed class SparkThresholdDownPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "True Spark Knight"),
        ("description",
            "You need {Amount} fewer [gold]Spark[/gold]{Amount:plural:|s} "
          + "for your Attacks to cost 0 (minimum 1)."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}
