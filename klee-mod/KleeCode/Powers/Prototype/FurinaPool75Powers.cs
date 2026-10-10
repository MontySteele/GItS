using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
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

/// <summary>
/// <i>High Stakes</i> (reworked by the Spend round,
/// <c>review/records/furina-spend-round-2026-10-10.md</c>, "What changes" 3,
/// and again by round 2, <c>furina-spend-round-2-2026-10-10.md</c> change 1):
/// "Your Attacks deal 1 additional damage for every 5 HP you have Drained
/// this combat." [every 4]. The old card ("within 5 HP of your Drain line")
/// was NEVER AGAIN three times over two rounds: the line band punished the
/// play the kit teaches. Round 1's "Drained and not Repaid" sat near 0,
/// because Salon Solitaire Repays every turn: it peaked at +2 in three plays.
///
/// THE AMOUNT IS THE DIVISOR (5, 4 upgraded:
/// <see cref="FurinaStageLaw.HighStakesEvery"/>). It reads the ledger's gross
/// count (<see cref="FurinaStageLedger.DrainedThisCombat"/>, every Drain's HP,
/// which no Repay lowers), rounded down, and adds it to each powered Attack
/// hit, as Strength does. What it added is filed for the play telemetry
/// (<see cref="AfterDamageGiven"/>).
///
/// COPIES ADD, AS SEPARATE INSTANCES. A divisor cannot stack by summing (two
/// copies at 5 would read "every 10"), so each play is its own instance
/// (<see cref="PowerInstanceType.Instanced"/>, the base game's
/// <c>AutomationPower</c> shape) and each adds its own bonus.
///
/// THE BADGE SHOWS THE BONUS NOW (<see cref="DisplayAmount"/>, refreshed by
/// <see cref="FurinaStage.RefreshBadges"/> on every Drain and Repay), and the
/// hover says it in words.
/// </summary>
public sealed class HighStakesPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "High Stakes"),
        ("description",
            "Your Attacks deal 1 additional damage for every "
          + "[blue]{Amount}[/blue] HP you have [gold]Drained[/gold] this "
          + "combat."),
        ("smartDescription",
            "Your Attacks deal 1 additional damage for every "
          + "[blue]{Amount}[/blue] HP you have [gold]Drained[/gold] this "
          + "combat. Now: [blue]{Bonus}[/blue] additional damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerInstanceType InstanceType =>
        PowerInstanceType.Instanced;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[] { new BonusVar() };

    /// <summary>This copy's bonus a hit now. PURE.</summary>
    public int Bonus =>
        IsMutable && Owner != null
            ? FurinaStageLaw.HighStakesBonus(
                FurinaStage.DrainedThisCombatOf(Owner), Amount)
            : 0;

    /// <summary>The badge: the bonus now, not the divisor.</summary>
    public override int DisplayAmount => Bonus;

    /// <summary>Redraw the badge's number.</summary>
    internal void Refresh()
    {
        if (!IsMutable || Owner == null) return;
        InvokeDisplayAmountChanged();
    }

    /// <summary>The bonus, read at the hit: her Attacks only (a card's
    /// powered hit). PURE.</summary>
    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == null || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return Bonus;
    }

    /// <summary>The play telemetry's <c>high_stakes_bonus</c> (the Spend
    /// round 2, 2026-10-10): the bonus this copy added to a hit that landed,
    /// capped at what the hit dealt (HP and Block). A read for the record;
    /// nothing the rules ask.</summary>
    public override Task AfterDamageGiven(
        PlayerChoiceContext choiceContext, Creature dealer, DamageResult result,
        ValueProp props, Creature target, CardModel? cardSource)
    {
        if (dealer != Owner || !props.IsPoweredAttack()) return Task.CompletedTask;
        if (cardSource is not { Type: CardType.Attack }) return Task.CompletedTask;
        if (!FurinaStage.LiveFor(Owner)) return Task.CompletedTask;
        FurinaStageLedger.For(Owner!).NoteHighStakes(
            FurinaStageLaw.HighStakesCredit(
                Bonus, (int)(result.UnblockedDamage + result.BlockedDamage)));
        return Task.CompletedTask;
    }

    /// <summary>`{Bonus}` in the hover, read live.</summary>
    private sealed class BonusVar : DynamicVar
    {
        public BonusVar() : base("Bonus", 0m)
        {
        }

        private int Live => _owner is HighStakesPower power ? power.Bonus : 0;

        protected override decimal GetBaseValueForIConvertible() => Live;

        public override string ToString() =>
            Live.ToString(System.Globalization.CultureInfo.InvariantCulture);
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
