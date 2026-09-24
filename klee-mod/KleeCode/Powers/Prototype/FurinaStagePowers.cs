using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

// ======================================================================
// FURINA, THE STAGE -- BATCH TWO'S FIVE POWERS (R276 pick 3).
//
// QUARANTINED: this folder is Compile Remove'd from a release build, so the
// only rows that may name one of these are `proto_fs_` rows on the prototype
// surface. The RULES each power adds live in `FurinaStage` beside the rule
// they bend -- the end-of-turn sweep, the bow, the damage order, the acts --
// and a power here is the switch those rules ask about. Nothing in this file
// moves a bar itself; every bar move is the ledger's.
// ======================================================================

/// <summary>
/// <i>Full House</i>: "At the end of your turn, if all three seats are filled,
/// your performers act twice." Counter: each copy adds one more act
/// (<see cref="FurinaStage.EndOfTurnActs"/> reads the sum).
/// </summary>
public sealed class FullHousePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Full House"),
        ("description",
            "At the end of your turn, if all three seats are filled, each "
          + "performer acts [blue]{Amount}[/blue] more "
          + "{Amount:plural:time|times}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// <i>Thunderous Applause</i>: "Whenever a performer takes a Bow, draw 1 card
/// and Raise 2 Fanfare on the back performer." INSTANCED, one badge per copy,
/// so each copy draws its own card and Raises its own Amount
/// (<see cref="FurinaStage.Bow"/>'s after-bow step).
/// </summary>
public sealed class ThunderousApplausePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Thunderous Applause"),
        ("description",
            "Whenever a performer takes a [gold]Bow[/gold], draw 1 card and "
          + "[gold]Raise[/gold] [blue]{Amount}[/blue] [gold]Fanfare[/gold] "
          + "on the back performer."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerInstanceType InstanceType =>
        PowerInstanceType.Instanced;
}

/// <summary>
/// <i>A Rapt Audience</i>: "Whenever an enemy hits the lead performer, Raise
/// half the Fanfare it lost (rounded up) on the back performer"; upgraded,
/// all of it. The Amount is the PERCENTAGE, 50 or 100, so copies add
/// (<see cref="FurinaStage.AbsorbHit"/>). It does nothing when the lead IS
/// the back performer.
/// </summary>
public sealed class RaptAudiencePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "A Rapt Audience"),
        ("description",
            "Whenever an enemy hits the lead performer, [gold]Raise[/gold] "
          + "[blue]{Amount}[/blue]% of the [gold]Fanfare[/gold] it lost, "
          + "rounded up, on the back performer."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// <i>A Five-Century Act</i>: "Whenever a performer takes a Bow, it returns to
/// the back seat with 1 Fanfare." One copy is the whole rule -- a performer
/// returns once however many are in play -- so the amount is a count of
/// copies and nothing reads it (<see cref="FurinaStage.Bow"/>).
/// </summary>
public sealed class FiveCenturyActPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "A Five-Century Act"),
        ("description",
            "Whenever a performer takes a [gold]Bow[/gold], it returns to the "
          + "back seat with 1 [gold]Fanfare[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// <i>Arkhe Alignment</i>: "At the start of your turn, choose: Ousia (acts
/// deal double damage) or Pneuma (acts give double Block; the lead regains 2
/// Fanfare)."
///
/// THE GAME'S OWN CHOOSE-A-CARD SCREEN, the Ethereal Spotlight's pattern: two
/// combat-scoped option cards (<see cref="ArkheOusiaOption"/>,
/// <see cref="ArkhePneumaOption"/>), created through
/// <c>CombatState.CreateCard</c> because the screen dereferences an option's
/// owner. The choice sets this turn's multipliers on the ledger, which
/// <see cref="FurinaStage.Perform"/> reads and the end-of-turn sweep resets.
///
/// ONE QUESTION A TURN, HOWEVER MANY COPIES. The player is asked once, and
/// copies ADD: the Amount is the copy count, and each copy adds one more
/// multiple of the act's printed number (one copy x2, two x3). Pneuma's lead
/// regain is 2 per copy. A prompt per copy would be per-turn friction for no
/// decision the single question does not already carry.
/// </summary>
public sealed class ArkheAlignmentPower : PowerModel, ILocalizationProvider
{
    /// <summary>What the Pneuma half gives the lead.</summary>
    public const int PneumaLeadRegain = 2;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Arkhe Alignment"),
        ("description",
            "At the start of your turn, choose [gold]Ousia[/gold] or "
          + "[gold]Pneuma[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Round four: the Ousia and Pneuma tips belong to THIS power
    /// and its card, and to nothing that merely shares a word with them
    /// (<i>Ousia Surge</i>, <i>Pneuma Refrain</i>). The card gets them off its
    /// golded face; the badge gets them here. Neither tip reads the card.
    /// </summary>
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
        var combatState = Owner.CombatState;
        if (combatState == null) return;
        var options = new List<CardModel>
        {
            combatState.CreateCard(ModelDb.Card<ArkheOusiaOption>(), player),
            combatState.CreateCard(ModelDb.Card<ArkhePneumaOption>(), player),
        };
        var selected = await CardSelectCmd.FromChooseACardScreen(
            choiceContext, options, player, canSkip: false);
        Choose(Owner, selected is ArkhePneumaOption, (int)Amount);
    }

    /// <summary>The choice's effect, separate from the screen so a headless
    /// pin can ask it. With <paramref name="copies"/> in play the chosen half
    /// is x(1 + copies); Pneuma's lead regains 2 per copy.</summary>
    public static void Choose(MegaCrit.Sts2.Core.Entities.Creatures.Creature owner,
                              bool pneuma, int copies = 1)
    {
        if (copies <= 0) return;
        var ledger = FurinaStageLedger.For(owner);
        if (pneuma)
        {
            ledger.ActBlockMultiplier = 1 + copies;
            FurinaStage.RegainLead(owner, PneumaLeadRegain * copies);
        }
        else
        {
            ledger.ActDamageMultiplier = 1 + copies;
        }
    }
}
