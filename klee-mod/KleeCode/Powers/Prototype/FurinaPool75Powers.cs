using System.Collections.Generic;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

// ======================================================================
// FURINA, THE POOL TO 75 (review/active/furina-pool-growth-2026-10-09.md,
// ruled 2026-10-09) -- THE NEW POWERS.
//
// As with the Salon's Tab's powers (`FurinaStagePowers.cs`), each is a switch
// the rules ask about (`FurinaStage.ModsOf`, `FurinaStage.TurnStart`); every
// Fanfare move, Drain, Repay and act is the ledger's and the director's. Sim
// twin: `tier0/engine/furina_tide.py`, through `furina_stage.ARM_POWER_IDS`.
// ======================================================================

/// <summary><i>Grand Entrance</i>: "Whenever you play a Guest Star, Repay 4.
/// Gain 1 Block for any HP it could not Repay." [6] (The Repay floor,
/// 2026-10-09.) Copies add.</summary>
public sealed class GrandEntrancePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Grand Entrance"),
        ("description",
            "Whenever you play a Guest Star, [gold]Repay[/gold] "
          + "[blue]{Amount}[/blue]. Gain 1 [gold]Block[/gold] for any HP it "
          + "could not [gold]Repay[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Showstopper</i>: "At the end of your turn, Spend 5: your
/// guests act again." Each copy buys one more round, while the bank holds 5
/// and a guest is on stage (<see cref="StageDirector.EndOfTurn"/>).</summary>
public sealed class ShowstopperPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Showstopper"),
        ("description",
            "At the end of your turn, [gold]Spend[/gold] 5: your guests act "
          + "again."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Ensemble Cast</i>: "You have 4 guest seats." A second copy
/// adds nothing.</summary>
public sealed class EnsembleCastPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Ensemble Cast"),
        ("description",
            "You have " + FurinaStageLaw.EnsembleSeats + " guest seats."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Crescendo</i>: "The first time you Spend each turn, draw 1
/// card." [Innate] Copies add cards.</summary>
public sealed class CrescendoPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Crescendo"),
        ("description",
            "The first time you [gold]Spend[/gold] each turn, draw "
          + "[blue]{Amount}[/blue] card."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Prima Donna</i>: "At the start of your turn, if you have 10
/// or more Fanfare, gain 1 Energy." Copies add Energy.</summary>
public sealed class PrimaDonnaPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Prima Donna"),
        ("description",
            "At the start of your turn, if you have 10 or more "
          + "[gold]Fanfare[/gold], gain [blue]{Amount}[/blue] Energy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Standing Room Only</i>: "Whenever you Spend all your Fanfare
/// (at least 1), gain 1 Strength." Copies add.</summary>
public sealed class StandingRoomOnlyPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Standing Room Only"),
        ("description",
            "Whenever you [gold]Spend[/gold] all your [gold]Fanfare[/gold] "
          + "and it is at least 1, gain [blue]{Amount}[/blue] "
          + "[gold]Strength[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Hymn of Renewal</i>: "Whenever you Repay 4 or more HP at
/// once, gain 1 Strength." It counts the HP the Repay actually returned,
/// not the number printed on the card (the paper's Review section; on this
/// hover and the sheet comment, not on the card face). Copies add.</summary>
public sealed class HymnOfRenewalPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Hymn of Renewal"),
        ("description",
            "Whenever you [gold]Repay[/gold] 4 or more HP at once, gain "
          + "[blue]{Amount}[/blue] [gold]Strength[/gold]. Only HP actually "
          + "regained counts."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>High Stakes</i>: "While you are within 5 HP of your Drain
/// line, your Attacks deal 4 more damage." [6] Copies add.</summary>
public sealed class HighStakesPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "High Stakes"),
        ("description",
            "While you are within 5 HP of your [gold]Drain[/gold] line, your "
          + "Attacks deal [blue]{Amount}[/blue] additional damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The bonus, read at the hit: her Attacks only (a card's
    /// powered hit), while she stands within 5 HP of the line. PURE.
    /// </summary>
    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == null || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return FurinaStage.NearLine(Owner) ? Amount : 0m;
    }
}

/// <summary><i>Regina of All Waters</i>: "At the start of your turn, Drain 3.
/// If you do, gain 1 Strength." Each copy Drains and gains on its own.
/// </summary>
public sealed class ReginaOfAllWatersPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Regina of All Waters"),
        ("description",
            "At the start of your turn, [gold]Drain[/gold] 3. If you do, gain "
          + "1 [gold]Strength[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Pneuma Tides</i>: "At the start of your turn, Repay 2. Gain 1
/// Vigor for any HP it could not Repay." [3] (The Repay floor, 2026-10-09.)
/// Copies add to one Repay.</summary>
public sealed class PneumaTidesPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Pneuma Tides"),
        ("description",
            "At the start of your turn, [gold]Repay[/gold] "
          + "[blue]{Amount}[/blue]. Gain 1 [gold]Vigor[/gold] for any HP it "
          + "could not [gold]Repay[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// <i>Gentle Current</i>'s "Next turn, Repay 4. Gain 1 Block for any HP it
/// could not Repay." [5] (the Repay floor, 2026-10-09): the Repay owed at her
/// next turn start, as the base game's <c>EnergyNextTurnPower</c> owes an
/// Energy. Two plays in a turn add into one Repay. Leaves when paid
/// (<see cref="FurinaStage.TurnStart"/>).
/// </summary>
public sealed class RepayNextTurnPower : PowerModel, ILocalizationProvider
{
    public new const string Title = "Gentle Current";

    public List<(string, string)>? Localization => new()
    {
        ("title", Title),
        ("description",
            "Next turn, [gold]Repay[/gold] [blue]{Amount}[/blue]. Gain 1 "
          + "[gold]Block[/gold] for any HP it could not [gold]Repay[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>The Masquerade</i> (the block gap,
/// review/records/furina-drain-line-round-2026-10-09.md pick 2, ruled
/// 2026-10-09): "Whenever you Drain, gain that much Block." [Cost 0] "That
/// much" is the HP actually drained, past the line included; a guest act's
/// Drain stops at the line, so it pays less. Copies add
/// (<see cref="StageDirector.Drain"/>).</summary>
public sealed class TheMasqueradePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", StageDirector.MasqueradeTitle),
        ("description",
            "Whenever you [gold]Drain[/gold], gain that much "
          + "[gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}
