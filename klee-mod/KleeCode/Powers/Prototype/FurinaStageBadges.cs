using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

// ======================================================================
// FURINA, THE STAGE -- THE BADGES THAT SAY WHAT THE STAGE DOES (2026-09-25).
//
// THE FIND. The owner's friend played the arm in co-op on 0.2.3737+proto and
// "found it very hard to understand what was going on from the tooltips,
// such as what each summoned actor actually did ... the core loop was held
// back by constant confusion as to what things did." Nothing on screen said
// what a performer does: the bodies carried only a name, and the acts and the
// bows lived in doc comments and in the Bow tip's list.
//
// SO EACH PERFORMER WEARS A BADGE, THE BASE GAME'S WAY. Hovering a creature
// shows its powers' hover tips (`Creature.HoverTips` walks `_powers`), and
// the base game gives Osty a visible power for exactly this -- `OstyCmd.Summon`
// applies `DieForYouPower` to the pet, a `Single` Buff with no number and
// `ShouldPlayVfx => false`. A performer's badge is that shape: titled with its
// name, carrying its act and its bow, and changing no number. And Furina
// wears one more, `The Stage`, which is the rules of the whole board in four
// sentences.
//
// THEY MOVE NOTHING. No hook is overridden here; a badge is text on a body.
// The amount is hidden (`Single`), so the wire's `DisplayAmount` is a
// constant 1 and the seat page's status rows cannot read a number into it.
// ======================================================================

/// <summary>
/// A PERFORMER'S BADGE: its name and what it does at the end of her turn.
/// The same sentence <c>ArmKeywordTips.ForUsher</c> and its two siblings
/// print on the cards that name the performer. No Bow clause since draft 3
/// (2026-09-25): a Bow is the act once more (<c>ArmKeywordTips.ForBow</c>).
///
/// THE ACT'S NUMBER IS LIVE (<see cref="ActVar"/>): under Arkhe Alignment's
/// Ousia or Pneuma the act is doubled this turn (<see cref="FurinaStage.Perform"/>
/// multiplies by <see cref="FurinaStageLedger.ActDamageMultiplier"/> or
/// <see cref="FurinaStageLedger.ActBlockMultiplier"/>), and the badge reads
/// those two multipliers rather than doing its own arithmetic -- the
/// preview-truth rule. The static <c>description</c> is the canonical face a
/// copy with no owner shows; the in-combat hover uses <c>smartDescription</c>.
/// </summary>
public abstract class StagePerformerBadge : PowerModel
{
    /// <summary>Which member of the cast this badge describes.</summary>
    public abstract StagePerformer Performer { get; }

    /// <summary>The act's printed number, before this turn's Arkhe multiple.
    /// </summary>
    protected abstract int BaseAct { get; }

    public override PowerType Type => PowerType.Buff;

    /// <summary>No number on the badge: it is a description, not a counter,
    /// which is <c>DieForYouPower</c>'s own choice for Osty.</summary>
    public override PowerStackType StackType => PowerStackType.Single;

    /// <summary>Quiet, as Osty's is: a performer arriving is not a buff
    /// landing.</summary>
    public override bool ShouldPlayVfx => false;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[] { new ActVar(BaseAct) };

    /// <summary>
    /// The act this performer will perform at the end of this turn: its
    /// printed number times this turn's Arkhe multiple (Pneuma for Usher's
    /// Block, Ousia for the two damage acts). The printed number wherever
    /// there is no stage to ask -- a canonical copy, or a pet whose owner is
    /// not a live Furina.
    /// </summary>
    internal int LiveAct()
    {
        // A canonical copy has no owner, and `Owner` asserts mutability.
        if (!IsMutable) return BaseAct;
        var furina = Owner?.PetOwner?.Creature;
        if (!FurinaStage.LiveFor(furina)) return BaseAct;
        var ledger = FurinaStageLedger.For(furina!);
        var multiple = Performer == StagePerformer.Usher
            ? ledger.ActBlockMultiplier
            : ledger.ActDamageMultiplier;
        return BaseAct * multiple;
    }

    /// <summary>
    /// <c>{Act}</c>, READ AT FORMAT TIME -- <c>ProtoBombPower</c>'s
    /// <c>SetOffDamageVar</c> shape: the game hands the var itself to
    /// SmartFormat and formats it through <c>ToString()</c>, so the var asks
    /// the ledger when the tip is drawn rather than storing a number that an
    /// Arkhe choice later in the turn would leave stale.
    /// </summary>
    private sealed class ActVar : DynamicVar
    {
        public ActVar(int printed) : base("Act", printed)
        {
        }

        private int Live =>
            (_owner as StagePerformerBadge)?.LiveAct() ?? (int)BaseValue;

        protected override decimal GetBaseValueForIConvertible() => Live;

        public override string ToString() =>
            Live.ToString(CultureInfo.InvariantCulture);
    }

    /// <summary>
    /// Pin this performer's badge on its body. Called by
    /// <c>FurinaStagePets.Field</c> the moment the body is fielded, so a body
    /// never stands on the stage without saying what it does. Silent, no
    /// applier and no card, as <c>OstyCmd.Summon</c> applies Osty's.
    /// </summary>
    public static async Task Pin(Creature pet, StagePerformer who)
    {
        if (pet.Powers.OfType<StagePerformerBadge>().Any()) return;
        var context = new ThrowingPlayerChoiceContext();
        switch (who)
        {
            case StagePerformer.Chevalmarin:
                await Apply<ChevalmarinBadgePower>(context, pet);
                break;
            case StagePerformer.Crabaletta:
                await Apply<CrabalettaBadgePower>(context, pet);
                break;
            case StagePerformer.Neuvillette:
                await Apply<NeuvilletteBadgePower>(context, pet);
                break;
            case StagePerformer.Clorinde:
                await Apply<ClorindeBadgePower>(context, pet);
                break;
            case StagePerformer.Navia:
                await Apply<NaviaBadgePower>(context, pet);
                break;
            case StagePerformer.Chevreuse:
                await Apply<ChevreuseBadgePower>(context, pet);
                break;
            case StagePerformer.Wriothesley:
                await Apply<WriothesleyBadgePower>(context, pet);
                break;
            case StagePerformer.Sigewinne:
                await Apply<SigewinneBadgePower>(context, pet);
                break;
            case StagePerformer.Charlotte:
                await Apply<CharlotteBadgePower>(context, pet);
                break;
            case StagePerformer.Lynette:
                await Apply<LynetteBadgePower>(context, pet);
                break;
            default:
                await Apply<UsherBadgePower>(context, pet);
                break;
        }
    }

    private static Task Apply<T>(PlayerChoiceContext context, Creature pet)
        where T : PowerModel =>
        PowerCmd.Apply<T>(context, pet, 1, applier: null, cardSource: null,
                          silent: true);
}

/// <summary>Gentilhomme Usher's badge: Block at the end of her turn (brief
/// sec.3 rule 10).</summary>
public sealed class UsherBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Usher;

    protected override int BaseAct => FurinaStageLaw.ActUsherBlock;

    public List<(string, string)>? Localization => new()
    {
        ("title", FurinaStageLedger.DisplayName(StagePerformer.Usher)),
        ("description",
            "End of your turn: gain " + FurinaStageLaw.ActUsherBlock
          + " [gold]Block[/gold]."),
        ("smartDescription",
            "End of your turn: gain {Act} [gold]Block[/gold]."),
    };
}

/// <summary>Surintendante Chevalmarin's badge: 2 damage to every enemy at
/// the end of her turn. No Hydro since draft 3 (2026-09-25).</summary>
public sealed class ChevalmarinBadgePower
    : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Chevalmarin;

    protected override int BaseAct => FurinaStageLaw.ActChevalmarinDamage;

    public List<(string, string)>? Localization => new()
    {
        ("title", FurinaStageLedger.DisplayName(StagePerformer.Chevalmarin)),
        ("description",
            "End of your turn: deal " + FurinaStageLaw.ActChevalmarinDamage
          + " damage to ALL enemies."),
        ("smartDescription",
            "End of your turn: deal {Act} damage to ALL enemies."),
    };
}

/// <summary>Mademoiselle Crabaletta's badge: damage to a random enemy at the
/// end of her turn. No Hydro since draft 3 (2026-09-25).</summary>
public sealed class CrabalettaBadgePower
    : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Crabaletta;

    protected override int BaseAct => FurinaStageLaw.ActCrabalettaDamage;

    public List<(string, string)>? Localization => new()
    {
        ("title", FurinaStageLedger.DisplayName(StagePerformer.Crabaletta)),
        ("description",
            "End of your turn: deal " + FurinaStageLaw.ActCrabalettaDamage
          + " damage to a random enemy."),
        ("smartDescription",
            "End of your turn: deal {Act} damage to a random enemy."),
    };
}

// ---- THE GUEST CAST (2026-09-25) -----------------------------------------
//
// One badge per guest, each the same sentence as that guest's tip
// (`ArmKeywordTips.ForNeuvillette` and the seven beside it), numerals from
// `FurinaStageLaw` (`EB-89`). A damage act's number is live under Ousia
// (`{Act}`), as the trio's is; the others print no number that moves.

public sealed class NeuvilletteBadgePower : StagePerformerBadge,
                                            ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Neuvillette;

    protected override int BaseAct => FurinaStageLaw.ActNeuvilletteDamage;

    public List<(string, string)>? Localization => new()
    {
        ("title", FurinaStageLedger.DisplayName(Performer)),
        ("description",
            "End of your turn: pay " + FurinaStageLaw.ActNeuvillettePrice
          + " of his Fanfare to deal " + FurinaStageLaw.ActNeuvilletteDamage
          + " [gold]Hydro[/gold] damage to ALL enemies."),
        ("smartDescription",
            "End of your turn: pay " + FurinaStageLaw.ActNeuvillettePrice
          + " of his Fanfare to deal {Act} [gold]Hydro[/gold] damage to ALL "
          + "enemies."),
    };
}

public sealed class ClorindeBadgePower : StagePerformerBadge,
                                         ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Clorinde;

    protected override int BaseAct => FurinaStageLaw.ActClorindeDamage;

    public List<(string, string)>? Localization => new()
    {
        ("title", FurinaStageLedger.DisplayName(Performer)),
        ("description",
            "End of your turn: take " + FurinaStageLaw.ActClorindeTax
          + " Fanfare from each other performer to deal "
          + FurinaStageLaw.ActClorindeDamage
          + " [gold]Electro[/gold] damage to a random enemy."),
        ("smartDescription",
            "End of your turn: take " + FurinaStageLaw.ActClorindeTax
          + " Fanfare from each other performer to deal {Act} "
          + "[gold]Electro[/gold] damage to a random enemy."),
    };
}

public sealed class NaviaBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Navia;

    protected override int BaseAct => 0;

    public List<(string, string)>? Localization => new()
    {
        ("title", FurinaStageLedger.DisplayName(Performer)),
        ("description",
            "End of your turn: deal [gold]Geo[/gold] damage equal to her "
          + "Fanfare to a random enemy."),
        ("smartDescription",
            "End of your turn: deal [gold]Geo[/gold] damage equal to her "
          + "Fanfare to a random enemy."),
    };
}

public sealed class ChevreuseBadgePower : StagePerformerBadge,
                                          ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Chevreuse;

    protected override int BaseAct => 0;

    public List<(string, string)>? Localization => new()
    {
        ("title", FurinaStageLedger.DisplayName(Performer)),
        ("description",
            "End of your turn: [gold]Spend[/gold] "
          + FurinaStageLaw.ActChevreusePrice + " to gain "
          + FurinaStageLaw.ActChevreuseEnergy
          + " [gold]Energy[/gold] next turn."),
        ("smartDescription",
            "End of your turn: [gold]Spend[/gold] "
          + FurinaStageLaw.ActChevreusePrice + " to gain "
          + FurinaStageLaw.ActChevreuseEnergy
          + " [gold]Energy[/gold] next turn."),
    };
}

public sealed class WriothesleyBadgePower : StagePerformerBadge,
                                            ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Wriothesley;

    protected override int BaseAct => 0;

    public List<(string, string)>? Localization => new()
    {
        ("title", FurinaStageLedger.DisplayName(Performer)),
        ("description",
            "End of your turn: deal [gold]Cryo[/gold] damage to a random "
          + "enemy equal to twice the Fanfare he lost since his last act."),
        ("smartDescription",
            "End of your turn: deal [gold]Cryo[/gold] damage to a random "
          + "enemy equal to twice the Fanfare he lost since his last act."),
    };
}

public sealed class SigewinneBadgePower : StagePerformerBadge,
                                          ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Sigewinne;

    protected override int BaseAct => 0;

    public List<(string, string)>? Localization => new()
    {
        ("title", FurinaStageLedger.DisplayName(Performer)),
        ("description",
            "End of your turn: give " + FurinaStageLaw.ActSigewinneGift
          + " of her Fanfare to the performer behind her, or to your front "
          + "performer if she is at the back."),
        ("smartDescription",
            "End of your turn: give " + FurinaStageLaw.ActSigewinneGift
          + " of her Fanfare to the performer behind her, or to your front "
          + "performer if she is at the back."),
    };
}

public sealed class CharlotteBadgePower : StagePerformerBadge,
                                          ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Charlotte;

    protected override int BaseAct => 0;

    public List<(string, string)>? Localization => new()
    {
        ("title", FurinaStageLedger.DisplayName(Performer)),
        ("description",
            "End of your turn: each other performer gains "
          + FurinaStageLaw.ActCharlotteGift + " [gold]Fanfare[/gold]."),
        ("smartDescription",
            "End of your turn: each other performer gains "
          + FurinaStageLaw.ActCharlotteGift + " [gold]Fanfare[/gold]."),
    };
}

public sealed class LynetteBadgePower : StagePerformerBadge,
                                        ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Lynette;

    protected override int BaseAct => 0;

    public List<(string, string)>? Localization => new()
    {
        ("title", FurinaStageLedger.DisplayName(Performer)),
        ("description",
            "End of your turn: [gold]Swirl[/gold] a random enemy with an "
          + "aura."),
        ("smartDescription",
            "End of your turn: [gold]Swirl[/gold] a random enemy with an "
          + "aura."),
    };
}

/// <summary>
/// THE STAGE, ON FURINA: when the cast acts and the damage order, on the
/// body a player hovers first. Applied at combat open and re-asked every turn
/// start (<see cref="FurinaStage.InstallBadge"/>), so a fight never runs
/// without it. It moves nothing.
///
/// A NEW POWER AND NOT A REUSE, because the arm has no Furina-side power that
/// is always on: Salon Solitaire is a relic, and the batch-two powers are
/// cards' powers a run may never draft. It sits in the power row under her
/// health bar; the damage-order strip (<c>FurinaStageStrip</c>) is a gauge on
/// the second row ABOVE her, so the two do not meet.
/// </summary>
public sealed class StageSummaryPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "The Stage"),
        // 2026-09-25 (opus-furina-l2b, (c) 3): THE SEAT COUNT. Neither this
        // badge nor the Summon tip's full-stage clause said how many seats
        // there are, and the seat "never dared a third summon". The number is
        // the law's, interpolated.
        // Draft 3 (2026-09-25): rule 12, the fade, replaces the damage-order
        // sentence, which the Fanfare tip carries on every card that prints
        // the word.
        ("description",
            "Up to " + FurinaStageLaw.Seats + " performers. At the end of "
          + "your turn, those behind the front lose half their Fanfare "
          + "above " + FurinaStageLaw.FadeThreshold + "."),
    };

    public override PowerType Type => PowerType.Buff;

    /// <summary>No number: the badge is a rule, not a counter.</summary>
    public override PowerStackType StackType => PowerStackType.Single;

    public override bool ShouldPlayVfx => false;
}
