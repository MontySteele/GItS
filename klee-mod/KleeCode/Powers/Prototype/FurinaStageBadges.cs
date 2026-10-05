using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

// ======================================================================
// FURINA, THE SALON'S TAB -- THE BADGES THAT SAY WHAT EACH GUEST DOES.
//
// Hovering a creature shows its powers' tips, and the base game gives Osty a
// quiet badge for exactly this (`DieForYouPower`). A guest's badge is that
// shape: titled with its name, carrying its line and its act, changing no
// number. The same sentence is its keyword tip on its Guest Star card
// (`ArmKeywordTips`), both off <see cref="ActText"/>.
// ======================================================================

/// <summary>A guest's badge: its name and what it does.</summary>
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
    /// What a guest does, in two short sentences: its line (while on stage)
    /// and its act (at the end of your turn). The texts are sec.16's; the
    /// numbers <see cref="FurinaStageLaw"/>'s (`EB-89`).
    /// </summary>
    public static string ActText(StagePerformer who) => who switch
    {
        StagePerformer.Charlotte =>
            "The first time you [gold]Repay[/gold] each turn, draw "
          + FurinaStageLaw.CharlotteLineDraw + " card. Act: [gold]Repay[/gold] "
          + FurinaStageLaw.CharlotteActRepay + ".",
        StagePerformer.Wriothesley =>
            "Whenever you [gold]Drain[/gold], deal that much [gold]Cryo[/gold] "
          + "damage to a random enemy. Act: deal "
          + FurinaStageLaw.WriothesleyActDamage
          + " [gold]Cryo[/gold] damage to a random enemy.",
        StagePerformer.Lynette =>
            "The first time each turn an enemy makes you lose HP, gain that "
          + "much [gold]Fanfare[/gold] again. Act: deal "
          + FurinaStageLaw.LynetteActDamage
          + " [gold]Anemo[/gold] damage to an enemy with an aura.",
        StagePerformer.Clorinde =>
            "Whenever you [gold]Repay[/gold], deal twice that much "
          + "[gold]Electro[/gold] damage to a random enemy. Act: deal "
          + FurinaStageLaw.ClorindeActDamage
          + " [gold]Electro[/gold] damage to a random enemy.",
        StagePerformer.Lyney =>
            "Your [gold]Drain[/gold] line is "
          + FurinaStageLaw.LyneyLineDrop + " HP lower. Act: [gold]Drain[/gold] "
          + FurinaStageLaw.LyneyActDrain + ": deal "
          + FurinaStageLaw.LyneyActDamage
          + " [gold]Pyro[/gold] damage to ALL enemies.",
        StagePerformer.Sigewinne =>
            "Whenever you [gold]Repay[/gold], gain that much "
          + "[gold]Block[/gold]. Act: [gold]Repay[/gold] "
          + FurinaStageLaw.SigewinneActRepay + ".",
        StagePerformer.Chevreuse =>
            "Whenever you [gold]Spend[/gold], apply "
          + FurinaStageLaw.ChevreuseLineVulnerable
          + " [gold]Vulnerable[/gold] to a random enemy. Act: deal "
          + FurinaStageLaw.ChevreuseActDamage
          + " damage to a random enemy.",
        _ => "",
    };

    /// <summary>Pin this guest's badge on its body, silently, the moment it
    /// is fielded (<c>FurinaStagePets.Field</c>).</summary>
    public static async Task Pin(Creature pet, StagePerformer who)
    {
        if (pet.Powers.OfType<StagePerformerBadge>().Any()) return;
        var context = new ThrowingPlayerChoiceContext();
        switch (who)
        {
            case StagePerformer.Wriothesley:
                await Apply<WriothesleyBadgePower>(context, pet);
                break;
            case StagePerformer.Lynette:
                await Apply<LynetteBadgePower>(context, pet);
                break;
            case StagePerformer.Clorinde:
                await Apply<ClorindeBadgePower>(context, pet);
                break;
            case StagePerformer.Lyney:
                await Apply<LyneyBadgePower>(context, pet);
                break;
            case StagePerformer.Sigewinne:
                await Apply<SigewinneBadgePower>(context, pet);
                break;
            case StagePerformer.Chevreuse:
                await Apply<ChevreuseBadgePower>(context, pet);
                break;
            default:
                await Apply<CharlotteBadgePower>(context, pet);
                break;
        }
    }

    private static Task Apply<T>(PlayerChoiceContext context, Creature pet)
        where T : PowerModel =>
        PowerCmd.Apply<T>(context, pet, 1, applier: null, cardSource: null,
                          silent: true);
}

public sealed class CharlotteBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Charlotte;
    public List<(string, string)>? Localization => Face;
}

public sealed class WriothesleyBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Wriothesley;
    public List<(string, string)>? Localization => Face;
}

public sealed class LynetteBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Lynette;
    public List<(string, string)>? Localization => Face;
}

public sealed class ClorindeBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Clorinde;
    public List<(string, string)>? Localization => Face;
}

public sealed class LyneyBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Lyney;
    public List<(string, string)>? Localization => Face;
}

public sealed class SigewinneBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Sigewinne;
    public List<(string, string)>? Localization => Face;
}

public sealed class ChevreuseBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Chevreuse;
    public List<(string, string)>? Localization => Face;
}
