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
// FURINA, THE STAGE (v2) -- THE BADGES THAT SAY WHAT EACH PERFORMER DOES.
//
// Hovering a creature shows its powers' tips, and the base game gives Osty a
// quiet badge for exactly this (`DieForYouPower`). A performer's badge is
// that shape: titled with its name, carrying its act (and a guest's "while
// on stage" line), changing no number. The same sentence is its keyword tip
// on every card that names it (`ArmKeywordTips`) and its face on the
// performer picker (`StageSeatOption`), all three off <see cref="ActText"/>.
// ======================================================================

/// <summary>A performer's badge: its name and what it does.</summary>
public abstract class StagePerformerBadge : PowerModel
{
    public abstract StagePerformer Performer { get; }

    public override PowerType Type => PowerType.Buff;

    /// <summary>No number: a description, not a counter.</summary>
    public override PowerStackType StackType => PowerStackType.Single;

    public override bool ShouldPlayVfx => false;

    protected List<(string, string)> Face => new()
    {
        ("title", FurinaStageLedger.DisplayName(Performer)),
        ("description", ActText(Performer)),
    };

    /// <summary>
    /// What a performer does, in one or two short sentences: its act (with
    /// its price, for a star) and, for a guest, its line. Numbers from
    /// <see cref="FurinaStageLaw"/> (`EB-89`). Rehearsal's +N is on the
    /// Rehearsal badge, not here.
    /// </summary>
    public static string ActText(StagePerformer who) => who switch
    {
        StagePerformer.Usher =>
            "Act: gain " + FurinaStageLaw.ActUsherBlock + " [gold]Block[/gold].",
        StagePerformer.Chevalmarin =>
            "Act: deal " + FurinaStageLaw.ActChevalmarinDamage
          + " damage to ALL enemies.",
        StagePerformer.Crabaletta =>
            "Act: deal " + FurinaStageLaw.ActCrabalettaDamage
          + " damage to a random enemy.",
        StagePerformer.Neuvillette =>
            "Your [gold]Hydro[/gold] damage deals "
          + FurinaStageLaw.NeuvilletteHydroBonus + " more. Act: pay "
          + FurinaStageLaw.ActNeuvillettePrice + " [gold]Fanfare[/gold] to deal "
          + FurinaStageLaw.ActNeuvilletteDamage
          + " [gold]Hydro[/gold] damage to ALL enemies.",
        StagePerformer.Clorinde =>
            "Whenever you [gold]Spend[/gold], deal "
          + FurinaStageLaw.ClorindeSpendDamage
          + " [gold]Electro[/gold] damage to a random enemy. Act: pay "
          + FurinaStageLaw.ActClorindePrice + " to deal "
          + FurinaStageLaw.ActClorindeDamage
          + " [gold]Electro[/gold] damage to a random enemy.",
        StagePerformer.Lyney =>
            "The first [gold]Cue[/gold] card you play each turn costs 0. Act: "
          + "pay " + FurinaStageLaw.ActLyneyPrice
          + " [gold]Fanfare[/gold] to add a Trick to your hand.",
        StagePerformer.Escoffier =>
            "The first Salon summon card you play each turn costs 0. Act: "
          + "pay " + FurinaStageLaw.ActEscoffierPrice
          + " [gold]Fanfare[/gold] to make your Salon members act.",
        StagePerformer.Navia =>
            "Act: deal [gold]Geo[/gold] damage to a random enemy, twice the "
          + "[gold]Fanfare[/gold] you spent this turn.",
        StagePerformer.Charlotte =>
            "At the start of your turn, draw " + FurinaStageLaw.CharlotteExtra
          + " more card. Act: gain " + FurinaStageLaw.ActCharlotteGain
          + " [gold]Fanfare[/gold].",
        StagePerformer.Lynette =>
            "The first performer you [gold]Cue[/gold] each turn moves to the "
          + "front. Act: deal " + FurinaStageLaw.ActLynetteDamage
          + " [gold]Anemo[/gold] damage to an enemy with an aura, if any.",
        StagePerformer.Chevreuse =>
            "Act, once a turn: pay " + FurinaStageLaw.ActChevreusePrice
          + " [gold]Fanfare[/gold] to gain " + FurinaStageLaw.ActChevreuseEnergy
          + " [gold]Energy[/gold] next turn.",
        StagePerformer.Sigewinne =>
            "Act: gain " + FurinaStageLaw.ActSigewinneBlock
          + " [gold]Block[/gold], plus " + FurinaStageLaw.SigewinnePerHpLoss
          + " for each time you lost HP since her last act.",
        StagePerformer.Wriothesley =>
            "Act: deal " + FurinaStageLaw.ActWriothesleyDamage
          + " [gold]Cryo[/gold] damage to a random enemy, plus "
          + FurinaStageLaw.WriothesleyPerBlocked
          + " per damage your [gold]Block[/gold] stopped since his last act.",
        _ => "",
    };

    /// <summary>Pin this performer's badge on its body, silently, the moment
    /// it is fielded (<c>FurinaStagePets.Field</c>).</summary>
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
            case StagePerformer.Lyney:
                await Apply<LyneyBadgePower>(context, pet);
                break;
            case StagePerformer.Escoffier:
                await Apply<EscoffierBadgePower>(context, pet);
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

public sealed class UsherBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Usher;
    public List<(string, string)>? Localization => Face;
}

public sealed class ChevalmarinBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Chevalmarin;
    public List<(string, string)>? Localization => Face;
}

public sealed class CrabalettaBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Crabaletta;
    public List<(string, string)>? Localization => Face;
}

public sealed class NeuvilletteBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Neuvillette;
    public List<(string, string)>? Localization => Face;
}

public sealed class ClorindeBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Clorinde;
    public List<(string, string)>? Localization => Face;
}

public sealed class NaviaBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Navia;
    public List<(string, string)>? Localization => Face;
}

public sealed class ChevreuseBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Chevreuse;
    public List<(string, string)>? Localization => Face;
}

public sealed class WriothesleyBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Wriothesley;
    public List<(string, string)>? Localization => Face;
}

public sealed class SigewinneBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Sigewinne;
    public List<(string, string)>? Localization => Face;
}

public sealed class CharlotteBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Charlotte;
    public List<(string, string)>? Localization => Face;
}

public sealed class LynetteBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Lynette;
    public List<(string, string)>? Localization => Face;
}

public sealed class LyneyBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Lyney;
    public List<(string, string)>? Localization => Face;
}

public sealed class EscoffierBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Escoffier;
    public List<(string, string)>? Localization => Face;
}
