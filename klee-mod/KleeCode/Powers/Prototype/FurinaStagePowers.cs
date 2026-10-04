using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

// ======================================================================
// FURINA, THE STAGE (v2, the re-founding) -- THE POWERS.
//
// QUARANTINED: this folder is Compile Remove'd from a release build, so the
// only rows that may name one of these are `proto_fs_` rows. A power here is
// a switch the rules ask about (`FurinaStage.ModsOf`, the turn-start powers
// in `FurinaStage.TurnStart`); every Fanfare move is the ledger's.
// ======================================================================

/// <summary>
/// FURINA'S FANFARE, AS A BADGE (sec.1 rule 5; sec.8: "Both counts show on
/// the Fanfare badge"). The number on the icon is her Fanfare
/// (<see cref="DisplayAmount"/>, the ledger's); the hover adds this turn's
/// gained and spent counts. Installed at combat open and asked again every
/// turn start (<see cref="FurinaStage.InstallBadge"/>).
///
/// On her own screen the number is drawn by the energy-area gauge
/// (<see cref="Vfx.FanfareCounter"/>, whose hover carries the flow counts)
/// and this badge's status-strip node is suppressed; the model stays, so the
/// rules, the wire and a co-op partner's view of her keep it.
/// </summary>
public sealed class FanfarePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Fanfare"),
        ("description",
            "Your performers act front to back at the end of your turn. "
          + "Stars pay for their acts in [gold]Fanfare[/gold]."),
        ("smartDescription",
            "You have {Fanfare} [gold]Fanfare[/gold]. This turn: gained "
          + "{Gained}, spent {Spent}."),
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

/// <summary>
/// REHEARSAL (sec.1 rule 6, sec.6 pick 2): "Every performer's damage and Block
/// act deals 1 more per stack, guests included." A Power with stacks, its
/// badge showing the total. Energy, draw and Fanfare never scale. Placed by
/// Dress Rehearsal, Premiere Season, The Curtain Never Falls and Curtain
/// Water; read by <see cref="FurinaStage.ModsOf"/>.
/// </summary>
public sealed class RehearsalPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Rehearsal"),
        ("description",
            "Your performers' damage and [gold]Block[/gold] acts deal "
          + "[blue]{Amount}[/blue] more."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Premiere Season</i>: "At the start of your turn, gain 1
/// Rehearsal." Copies add (<see cref="FurinaStage.TurnStart"/>).</summary>
public sealed class PremiereSeasonPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Premiere Season"),
        ("description",
            "At the start of your turn, gain [blue]{Amount}[/blue] "
          + "[gold]Rehearsal[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Full House</i>: "If every seat is filled at the end of your
/// turn, your performers act twice." Each copy adds one more act.</summary>
public sealed class FullHousePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Full House"),
        ("description",
            "If every seat is filled at the end of your turn, your performers "
          + "act [blue]{Amount}[/blue] more {Amount:plural:time|times}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Sold Out</i>: "Your stage has a fourth seat."</summary>
public sealed class SoldOutPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sold Out"),
        ("description", "Your stage has a fourth seat."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Thunderous Applause</i> (sec.8): "Whenever a performer Bows,
/// draw 1 card." The Fanfare half is the base Bow rule now. Copies add.
/// </summary>
public sealed class ThunderousApplausePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Thunderous Applause"),
        ("description",
            "Whenever a performer [gold]Bow[/gold]s, draw [blue]{Amount}[/blue] "
          + "{Amount:plural:card|cards}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>A Five-Century Act</i>: "The first time each turn a performer
/// Bows and leaves, it returns at the back if a seat is free." One copy is
/// the whole rule.</summary>
public sealed class FiveCenturyActPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "A Five-Century Act"),
        ("description",
            "The first time each turn a performer [gold]Bow[/gold]s and "
          + "leaves, it returns at the back if a seat is free."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// <i>Arkhe Alignment</i>: "At the start of your turn, choose Ousia or
/// Pneuma." Ousia: this turn the performers' acts deal double damage (copies
/// add a multiple each). Pneuma (sec.8): "Gain 2 Fanfare" (2 a copy). The
/// game's own choose-a-card screen, the two faces in
/// <c>ArkheOptions.cs</c>; one question a turn however many copies.
/// </summary>
public sealed class ArkheAlignmentPower : PowerModel, ILocalizationProvider
{
    /// <summary>Pneuma's Fanfare, per copy.</summary>
    public const int PneumaFanfare = 2;

    public const string PneumaTitle = "Pneuma";

    public List<(string, string)>? Localization => new()
    {
        ("title", "Arkhe Alignment"),
        ("description",
            "At the start of your turn, choose [gold]Ousia[/gold] or "
          + "[gold]Pneuma[/gold]. Stacks add."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override IEnumerable<MegaCrit.Sts2.Core.HoverTips.IHoverTip>
        ExtraHoverTips =>
        global::KleeMod.Cards.ArmKeywordTips.ForPneuma(
            global::KleeMod.Cards.ArmKeywordTips.ForOusia(
                base.ExtraHoverTips, null!),
            null!);

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player?.Creature != Owner) return;
        if (!FurinaStage.LiveFor(Owner)) return;
        var pneuma = await Ask(choiceContext, player);
        await Choose(choiceContext, Owner, pneuma, (int)Amount);
    }

    /// <summary>Ousia or Pneuma, on the choose-a-card screen. True for
    /// Pneuma.</summary>
    internal static async Task<bool> Ask(PlayerChoiceContext choiceContext,
                                         Player player)
    {
        var combatState = player.Creature?.CombatState;
        if (combatState == null) return false;
        var options = new List<CardModel>
        {
            combatState.CreateCard(ModelDb.Card<ArkheOusiaOption>(), player),
            combatState.CreateCard(ModelDb.Card<ArkhePneumaOption>(), player),
        };
        var selected = await CardSelectCmd.FromChooseACardScreen(
            choiceContext, options, player, canSkip: false);
        return selected is ArkhePneumaOption;
    }

    /// <summary>
    /// The choice's effect, separate from the screen so a pin can ask it.
    /// Ousia: this turn's act damage is x(1 + copies), never lower than a
    /// multiple already chosen this turn. Pneuma: gain 2 Fanfare a copy.
    /// </summary>
    public static async Task Choose(PlayerChoiceContext choiceContext,
                                    Creature owner, bool pneuma, int copies)
    {
        if (copies <= 0) return;
        var ledger = FurinaStageLedger.For(owner);
        if (pneuma)
        {
            using (ledger.CausedBy(PneumaTitle))
            {
                await FurinaStage.Gain(choiceContext, owner,
                                       PneumaFanfare * copies, PneumaTitle);
            }
            return;
        }
        ledger.ActDamageMultiplier = System.Math.Max(
            ledger.ActDamageMultiplier, 1 + copies);
        FurinaStage.RefreshBadges(owner);
    }
}

/// <summary><i>Revolving Stage</i>: "At the start of your turn, Cue your
/// front performer." Each copy Cues once.</summary>
public sealed class RevolvingStagePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Revolving Stage"),
        ("description",
            "At the start of your turn, [gold]Cue[/gold] your front "
          + "performer."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Season Tickets</i>: "At the start of your turn, gain 1
/// Fanfare" (2 upgraded). Copies add.</summary>
public sealed class SeasonTicketsPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Season Tickets"),
        ("description",
            "At the start of your turn, gain [blue]{Amount}[/blue] "
          + "[gold]Fanfare[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Star Billing</i>: "Whenever a Guest Star joins the stage,
/// draw 2 cards", a second copy's repeat included. Copies add.</summary>
public sealed class StarBillingPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Star Billing"),
        ("description",
            "Whenever a Guest Star joins the stage, draw "
          + "[blue]{Amount}[/blue] {Amount:plural:card|cards}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Tide of Applause</i>: "Whenever you trigger an Elemental
/// Reaction, gain 2 Fanfare" (3 upgraded), paid at the one site the mod
/// resolves a reaction (<see cref="FurinaStage.OnReaction"/>).</summary>
public sealed class TideOfApplausePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Tide of Applause"),
        ("description",
            "Whenever you trigger an [gold]Elemental Reaction[/gold], gain "
          + "[blue]{Amount}[/blue] [gold]Fanfare[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Regina of All Waters</i>: "At the start of your turn, apply
/// Hydro to ALL enemies."</summary>
public sealed class ReginaOfAllWatersPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Regina of All Waters"),
        ("description",
            "At the start of your turn, apply [gold]Hydro[/gold] to ALL "
          + "enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Soliloquy</i>: "While no one is on stage, your Attacks deal 3
/// more damage" (4 upgraded), per hit, read off the live stage.</summary>
public sealed class SoliloquyPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Soliloquy"),
        ("description",
            "While no one is on stage, your Attacks deal "
          + "[blue]{Amount}[/blue] additional damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        if (!FurinaStage.LiveFor(Owner) || FurinaStage.Occupied(Owner))
        {
            return 0m;
        }
        return Amount;
    }
}

/// <summary><i>One-Woman Show</i>: "At the start of your turn, if no one is
/// on stage, gain 1 Energy and draw 2 cards." Copies add.</summary>
public sealed class OneWomanShowPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "One-Woman Show"),
        ("description",
            "At the start of your turn, if no one is on stage, gain "
          + "[blue]{Amount}[/blue] [gold]Energy[/gold] and draw twice "
          + "that many cards."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Critics' Darling</i> (sec.10): "Whenever your Fanfare changes,
/// deal that much damage to a random enemy." Every change -- a gain, a Spend,
/// a star's payment -- once per copy (<see cref="StageDirector.Settle"/>).
/// </summary>
public sealed class CriticsDarlingPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Critics' Darling"),
        ("description",
            "Whenever your [gold]Fanfare[/gold] changes, deal that much "
          + "damage to a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary><i>Star Turn</i>: "Whenever a Guest Star joins the stage, it
/// acts at once" (a star pays). Copies add.</summary>
public sealed class StarTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Star Turn"),
        ("description",
            "Whenever a Guest Star joins the stage, it acts at once."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// CENTER OF ATTENTION, Furina's second Ancient: "The first Spend you choose
/// each turn takes no Fanfare." A free Spend moves nothing, so it is no Spend
/// (Clorinde's line and the spent-this-turn count do not see it). The latch
/// is this power's own round number. Game-side only, like every Ancient.
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
