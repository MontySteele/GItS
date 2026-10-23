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
// FURINA, THE POOL TO 75 (review/ruled/furina-pool-growth-2026-10-09.md,
// ruled 2026-10-09) -- THE NEW POWERS.
//
// As with the Salon's Tab's powers (`FurinaStagePowers.cs`), each is a switch
// the rules ask about (`FurinaStage.ModsOf`, `FurinaStage.TurnStart`); every
// Fanfare move, Drain, Repay and act is the ledger's and the director's. Sim
// twin: `tier0/engine/furina_tide.py`, through `furina_stage.ARM_POWER_IDS`.
// ======================================================================

/// <summary><i>Grand Entrance</i>: "Whenever you play a Guest Star, Repay 4."
/// [6] Its Block floor is the rule's since furina-next paper 3 (2026-10-16),
/// so the face drops the clause it printed (the Repay floor, 2026-10-09).
/// Copies add.</summary>
public sealed class GrandEntrancePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Grand Entrance"),
        ("description",
            "Whenever you play a Guest Star, [gold]Repay[/gold] "
          + "[blue]{Amount}[/blue]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Showstopper</i>: "At the end of your turn, Spend 5 [3]: your
/// guests act again." Each copy buys one more round, while the bank holds its
/// price and a guest is on stage (<see cref="StageDirector.EndOfTurn"/>).
/// A copy the upgraded card installed Spends 3 (the upgrade census,
/// 2026-10-23; was cost -1) and pays first
/// (<see cref="UpgradeTwinPower.UpgradedCopies"/>). One badge for both
/// versions.</summary>
public sealed class ShowstopperPower : UpgradeTwinPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Showstopper"),
        ("description",
            "At the end of your turn, [gold]Spend[/gold] 5: your guests act "
          + "again."),
        ("smartDescription",
            "At the end of your turn, [gold]Spend[/gold] "
          + "{Upgraded:cond:>0?3|5}: your guests act again."),
    };
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

/// <summary><i>Crescendo</i> (furina-next, 2026-10-16): "At the start of
/// your turn, gain 2 [3] Fanfare, then 2 [3] more each turn after." It counts
/// from the turn it is played: played on turn 1 it pays 2, 4, 6 on turns 2
/// to 4. The amount is the step; what each copy has paid is the ledger's
/// (<see cref="StageDirector.Crescendo"/>), so a later copy starts small.
/// </summary>
public sealed class CrescendoPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Crescendo"),
        ("description",
            "At the start of your turn, gain [blue]{Amount}[/blue] "
          + "[gold]Fanfare[/gold], then [blue]{Amount}[/blue] more each "
          + "turn after."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Prima Donna</i> (furina-next, 2026-10-16): "At the start of
/// your turn, if you Spent last turn, gain 1 Energy." [and draw 1 card.]
/// Last turn is her previous turn, its end-of-turn Spends included; a Spend
/// of 0 is no Spend (<see cref="StageDirector.PrimaDonna"/>). Every copy adds
/// Energy; a copy the upgraded card installed also adds a card
/// (<see cref="UpgradeTwinPower.UpgradedCopies"/>). One badge for both
/// versions since the icon declutter (2026-10-19); it was a "+" twin.</summary>
public sealed class PrimaDonnaPower : UpgradeTwinPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Prima Donna"),
        ("description",
            "At the start of your turn, if you [gold]Spent[/gold] last turn, "
          + "gain {Amount:energyIcons()}."),
        ("smartDescription",
            "At the start of your turn, if you [gold]Spent[/gold] last turn, "
          + "gain {Amount:energyIcons()}"
          + "{Upgraded:cond:==1? and draw [blue]1[/blue] card|>1? and draw "
          + "[blue]{}[/blue] cards|}."),
    };
}

/// <summary><i>Standing Room Only</i> (furina-next, 2026-10-16): "Whenever
/// you Spend, gain 1 Strength." Every Spend of at least 1 counts, whoever
/// makes it: her cards, Full House, Navia's and Freminet's acts, Showstopper
/// (<see cref="StageDirector"/>'s one after-Spend hook). Copies add.</summary>
public sealed class StandingRoomOnlyPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Standing Room Only"),
        ("description",
            "Whenever you [gold]Spend[/gold], gain [blue]{Amount}[/blue] "
          + "[gold]Strength[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Regina of All Waters</i>: "At the start of your turn, Drain 3,
/// never past your line. If you do, gain 1 Strength." Each copy Drains and
/// gains on its own; the Drain stops at the line (2026-10-10).
/// </summary>
public sealed class ReginaOfAllWatersPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Regina of All Waters"),
        ("description",
            "At the start of your turn, [gold]Drain[/gold] 3, never past "
          + "your line. If you do, gain 1 [gold]Strength[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>The Masquerade</i> (the block gap,
/// review/records/furina-drain-line-round-2026-10-09.md pick 2, ruled
/// 2026-10-09): "Whenever you Drain, gain that much Block." [plus 2] "That
/// much" is the HP actually drained, past the line included; a guest act's
/// Drain stops at the line, so it pays less. Copies add
/// (<see cref="StageDirector.Drain"/>); a copy the upgraded card installed
/// adds 2 more a Drain (the upgrade census, 2026-10-23; was cost -1). One
/// badge for both versions (<see cref="UpgradeTwinPower"/>).</summary>
public sealed class TheMasqueradePower : UpgradeTwinPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", StageDirector.MasqueradeTitle),
        ("description",
            "Whenever you [gold]Drain[/gold], gain that much "
          + "[gold]Block[/gold]."),
        ("smartDescription",
            "Whenever you [gold]Drain[/gold], gain that much "
          + "[gold]Block[/gold]{Upgraded:cond:>0? plus 2|}."),
    };
}

// ======================================================================
// THE DIVERSITY PASS (review/ruled/furina-diversity-pass-2026-10-11.md,
// ruled 2026-10-11): the two guest styles' Powers.
// ======================================================================

/// <summary><i>Leading Lady</i> (style 1, stars support and Furina hits):
/// "Gain 1 Strength. Your Attacks deal 1 additional damage for each guest
/// on stage." [2 Strength] (The paper's "1 more damage", in the house
/// template, rule 8 of the text pass: "additional damage".) The card applies the base game's Strength; this
/// power is the second sentence. Its amount is the bonus a guest, so copies
/// add. It adds to each powered Attack hit she deals, as Strength does
/// (High Stakes' gates), so guest acts, which are unpowered, never take it.
/// Sim twin: <c>furina_stage.leading_lady_bonus</c>.</summary>
public sealed class LeadingLadyPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Leading Lady"),
        ("description",
            "Your Attacks deal [blue]{Amount}[/blue] additional damage for each "
          + "guest on stage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The bonus a hit now: the amount times the guests on stage.
    /// PURE.</summary>
    public int Bonus =>
        IsMutable && Owner != null
            ? Amount * FurinaStage.Of(Owner).Count
            : 0;

    /// <summary>Her Attacks only (a card's powered hit), no target asked
    /// for (High Stakes' reading, so the face previews it).</summary>
    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return Bonus;
    }
}

/// <summary><i>Full House</i> (style 2, stars hit and Furina feeds them):
/// "Whenever a guest's act deals damage, Spend up to 4: it deals that much
/// more." [6] A switch the director asks about
/// (<see cref="StageDirector.FullHouse"/>); its amount is the cap, so
/// copies add their caps into one Spend.</summary>
public sealed class FullHousePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", StageDirector.FullHouseTitle),
        ("description",
            "Whenever a guest's act deals damage, [gold]Spend[/gold] up to "
          + "[blue]{Amount}[/blue]: it deals that much additional damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}
