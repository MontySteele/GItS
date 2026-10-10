using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

// ======================================================================
// FURINA, THE SALON'S TAB (2026-10-05) -- THE POWERS.
//
// A power here is a switch the rules ask about (`FurinaStage.ModsOf`); every
// Fanfare move, Drain and Repay is the ledger's and the director's.
// ======================================================================

/// <summary>
/// FURINA'S FANFARE, AS A BADGE (rule 3). The number on the icon is her
/// Fanfare (<see cref="DisplayAmount"/>, the ledger's); the hover adds this
/// turn's gained and spent counts. Installed at combat open and asked again
/// every turn start (<see cref="FurinaStage.InstallBadge"/>).
///
/// On her own screen the number is drawn by the energy-area gauge
/// (<see cref="Vfx.FanfareCounter"/>) and this badge's status-strip node is
/// suppressed; the model stays, so the rules, the wire and a co-op partner's
/// view of her keep it.
/// </summary>
public sealed class FanfarePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Fanfare"),
        ("description",
            "Gain 1 [gold]Fanfare[/gold] for each HP you lose or "
          + "[gold]Repay[/gold]. [gold]Spend[/gold] pays it."),
        ("smartDescription",
            "You have {Fanfare} [gold]Fanfare[/gold]. Gain 1 "
          + "[gold]Fanfare[/gold] for each HP you lose or [gold]Repay[/gold]. "
          + "This turn: gained {Gained}, spent {Spent}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override bool ShouldPlayVfx => false;

    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[]
    {
        new LedgerVar("Fanfare", l => l.Fanfare),
        new LedgerVar("Gained", l => l.GainedThisTurn),
        new LedgerVar("Spent", l => l.SpentThisTurn),
    };

    /// <summary>Her Fanfare, read off the ledger.</summary>
    public override int DisplayAmount
    {
        get
        {
            if (!IsMutable || Owner == null || !FurinaStage.LiveFor(Owner))
            {
                return 0;
            }
            return FurinaStageLedger.For(Owner).Fanfare;
        }
    }

    /// <summary>Redraw the icon's number.</summary>
    internal void Refresh()
    {
        if (!IsMutable || Owner == null) return;
        InvokeDisplayAmountChanged();
    }

    /// <summary>
    /// NEUVILLETTE'S LINE on her card hits (the pool to 75): "Your Hydro
    /// damage deals 2 more." [3] This badge rides on her for the whole
    /// combat, so it is where the card-hit half is read; the non-card half
    /// (a guest's act, a Power's hit) is <see cref="ElementalHit.Deal"/>'s,
    /// off the same <see cref="FurinaStage.HydroBonus"/>. PURE.
    ///
    /// NO TARGET IS ASKED FOR (2026-10-10): the bonus is hers, not the
    /// enemy's, and a card in her hand previews with a null target, so a
    /// <c>target == null</c> gate dropped it from the face as it did High
    /// Stakes'. Her own body is still refused.
    /// </summary>
    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (cardSource == null || !props.IsPoweredAttack()) return 0m;
        var element = CompanionOverhaulRiders.ElementFor(cardSource, dealer);
        return FurinaStage.HydroBonus(dealer, element);
    }

    /// <summary>A number read off her ledger when the tip is drawn.</summary>
    private sealed class LedgerVar : DynamicVar
    {
        private readonly System.Func<FurinaStageLedger, int> _read;

        public LedgerVar(string name, System.Func<FurinaStageLedger, int> read)
            : base(name, 0m)
        {
            _read = read;
        }

        private int Live
        {
            get
            {
                if (_owner is not FanfarePower { IsMutable: true } badge
                    || badge.Owner is not { } furina
                    || !FurinaStage.LiveFor(furina))
                {
                    return 0;
                }
                return _read(FurinaStageLedger.For(furina));
            }
        }

        protected override decimal GetBaseValueForIConvertible() => Live;

        public override string ToString() =>
            Live.ToString(CultureInfo.InvariantCulture);
    }
}

/// <summary><i>Salon's Encore</i>: "Whenever you Drain, deal 3 damage to ALL
/// enemies." [4] Copies add.</summary>
public sealed class SalonsEncorePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Salon's Encore"),
        ("description",
            "Whenever you [gold]Drain[/gold], deal [blue]{Amount}[/blue] "
          + "damage to ALL enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Thunderous Applause</i>: "Whenever you Spend, deal 3 damage to
/// ALL enemies." [4] A spend-all is one Spend. Copies add.</summary>
public sealed class ThunderousApplausePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Thunderous Applause"),
        ("description",
            "Whenever you [gold]Spend[/gold], deal [blue]{Amount}[/blue] "
          + "damage to ALL enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// <i>Universal Revelry</i> (the pool-40 paper, sec.2, back to the research
/// paper's sec.15): "Whenever you Drain or Repay, gain that much additional
/// Fanfare." Hits do not count; it does not trigger itself; a second copy
/// adds again (+2x, never multiplicative; <see cref="StageDirector"/>'s
/// loop readers).
/// </summary>
public sealed class UniversalRevelryPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Universal Revelry"),
        ("description",
            "Whenever you [gold]Drain[/gold] or [gold]Repay[/gold], gain that "
          + "much additional [gold]Fanfare[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Ousia Surge</i>: "The first time you Drain each turn, draw 1
/// card." [Innate] Copies add cards.</summary>
public sealed class OusiaSurgePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Ousia Surge"),
        ("description",
            "The first time you [gold]Drain[/gold] each turn, draw "
          + "[blue]{Amount}[/blue] card."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>A Five-Century Act</i> (2026-10-09): "HP you Drain past your
/// line also returns when combat ends." The curtain call reads it
/// (<see cref="FurinaStageLedger.CurtainCall"/>). A second copy adds
/// nothing.</summary>
public sealed class FiveCenturyActPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "A Five-Century Act"),
        ("description",
            "HP you [gold]Drain[/gold] past your line also returns when "
          + "combat ends."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Critics' Darling</i>: "Whenever you Drain or Repay, deal that
/// much damage to a random enemy." Copies add.</summary>
public sealed class CriticsDarlingPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Critics' Darling"),
        ("description",
            "Whenever you [gold]Drain[/gold] or [gold]Repay[/gold], deal that "
          + "much damage to a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Bis!</i>: "Whenever you Spend all your Fanfare, keep half of
/// it." [Innate] Half rounds down; a second copy adds nothing
/// (<see cref="FurinaStageLedger.SpendAll"/>).</summary>
public sealed class BisPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Bis!"),
        ("description",
            "Whenever you [gold]Spend[/gold] all your [gold]Fanfare[/gold], "
          + "keep half of it."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// <i>Fountain of Lucine</i>: "At the start of your next 3 turns, Repay 3.
/// Gain 1 Block for any HP it could not Repay." [4] (The Repay floor,
/// 2026-10-09: each turn's Repay pays its own floor.) The card applies its Repay as this power's amount; at her turn start
/// <see cref="FurinaStage"/> schedules what it has not yet seen for three
/// turns (one schedule per play) and makes the Repays due. The number on the
/// icon is the Repay owed at her next turn start; the power leaves when
/// nothing is owed.
/// </summary>
public sealed class FountainOfLucinePower : PowerModel, ILocalizationProvider
{
    public const string Title = "Fountain of Lucine";

    public List<(string, string)>? Localization => new()
    {
        ("title", Title),
        ("description",
            "At the start of your turn, [gold]Repay[/gold] what this "
          + "Fountain still owes. Gain 1 [gold]Block[/gold] for any HP it "
          + "could not [gold]Repay[/gold]."),
        ("smartDescription",
            "At the start of your turn, [gold]Repay[/gold] [blue]{Due}[/blue]. "
          + "Gain 1 [gold]Block[/gold] for any HP it could not "
          + "[gold]Repay[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[]
    {
        new DueVar(),
    };

    /// <summary>The Repay owed at her next turn start.</summary>
    public override int DisplayAmount => Due(this);

    private static int Due(FountainOfLucinePower power)
    {
        if (!power.IsMutable || power.Owner == null
            || !FurinaStage.LiveFor(power.Owner))
        {
            return (int)power.Amount;
        }
        var ledger = FurinaStageLedger.For(power.Owner);
        return ledger.RepayDueNext
               + System.Math.Max(0, (int)power.Amount - ledger.FountainSeen);
    }

    /// <summary>The tip's number: the same Repay owed.</summary>
    private sealed class DueVar : DynamicVar
    {
        public DueVar() : base("Due", 0m)
        {
        }

        private int Live =>
            _owner is FountainOfLucinePower power ? Due(power) : 0;

        protected override decimal GetBaseValueForIConvertible() => Live;

        public override string ToString() =>
            Live.ToString(CultureInfo.InvariantCulture);
    }

    /// <summary>Redraw the icon's number.</summary>
    internal void Refresh()
    {
        if (!IsMutable || Owner == null) return;
        InvokeDisplayAmountChanged();
    }
}

/// <summary>
/// CENTER OF ATTENTION, Furina's second Ancient: "The first Spend you choose
/// each turn takes no Fanfare." A free Spend moves nothing, so it is no Spend
/// (Thunderous Applause and the spent-this-turn count do not see it). The
/// latch is this power's own round number. Game-side only, like every
/// Ancient.
/// </summary>
public sealed class CenterOfAttentionPower : PowerModel, ILocalizationProvider
{
    private int _claimedRound = -1;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Center of Attention"),
        ("description",
            "The first [gold]Spend[/gold] you choose each turn takes no "
          + "[gold]Fanfare[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    private static int Round(Creature owner) =>
        owner.CombatState?.RoundNumber ?? 0;

    private static CenterOfAttentionPower? Open(Creature? owner)
    {
        if (owner == null || !FurinaStage.LiveFor(owner)) return null;
        var power = owner.Powers.OfType<CenterOfAttentionPower>().FirstOrDefault();
        if (power == null || power._claimedRound == Round(owner)) return null;
        return power;
    }

    /// <summary>Is the turn's free Spend still open? A read.</summary>
    public static bool Covers(Creature? owner) => Open(owner) != null;

    /// <summary>Take the turn's free Spend: true once a turn.</summary>
    public static bool TryClaim(Creature owner)
    {
        var power = Open(owner);
        if (power == null) return false;
        power._claimedRound = Round(owner);
        return true;
    }
}
