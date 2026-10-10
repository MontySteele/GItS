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
//
// THE POOL TO 75 (review/active/furina-pool-growth-2026-10-09.md sec.3): an
// upgraded Guest Star raises its guest's line or act, so each guest has a
// second badge class carrying the upgraded sentence. A power's text is its
// class's, which is why the upgrade is a class and not a field.
// ======================================================================

/// <summary>A guest's badge: its name and what it does.</summary>
public abstract class StagePerformerBadge : PowerModel
{
    public abstract StagePerformer Performer { get; }

    /// <summary>The upgraded guest's badge (the pool to 75).</summary>
    public virtual bool Upgraded => false;

    public override PowerType Type => PowerType.Buff;

    /// <summary>No number: a description, not a counter.</summary>
    public override PowerStackType StackType => PowerStackType.Single;

    public override bool ShouldPlayVfx => false;

    protected List<(string, string)> Face => new()
    {
        ("title", FurinaStageLedger.DisplayName(Performer)),
        ("description", ActText(Performer, Upgraded)),
    };

    /// <summary>The line's cue (the pool to 75, sec.3): the badge flashes on
    /// the guest's body when its line fires.</summary>
    internal void Pulse() => Flash();

    /// <summary>
    /// What a guest does, in two short sentences: its line (while on stage)
    /// and its act (at the end of your turn). The texts are the papers'; the
    /// numbers <see cref="FurinaStageLaw"/>'s (`EB-89`), upgraded where
    /// <paramref name="upgraded"/>.
    /// </summary>
    public static string ActText(StagePerformer who, bool upgraded = false)
    {
        // Each guest's numbers read off `FurinaStageLaw` here, by name
        // (`EB-89`), base and upgraded -- the same pairs
        // `StageDirector.ActAmount` reads.
        int Pick(int baseAmount, int upgradedAmount) =>
            upgraded ? upgradedAmount : baseAmount;
        var act = who switch
        {
            StagePerformer.Charlotte => Pick(FurinaStageLaw.CharlotteActRepay,
                FurinaStageLaw.CharlotteActRepayUpgraded),
            StagePerformer.Sigewinne => Pick(FurinaStageLaw.SigewinneActRepay,
                FurinaStageLaw.SigewinneActRepayUpgraded),
            StagePerformer.Wriothesley => Pick(
                FurinaStageLaw.WriothesleyActDamage,
                FurinaStageLaw.WriothesleyActDamageUpgraded),
            StagePerformer.Lynette => Pick(FurinaStageLaw.LynetteActDamage,
                FurinaStageLaw.LynetteActDamageUpgraded),
            StagePerformer.Clorinde => Pick(FurinaStageLaw.ClorindeActDamage,
                FurinaStageLaw.ClorindeActDamageUpgraded),
            StagePerformer.Lyney => Pick(FurinaStageLaw.LyneyActDamage,
                FurinaStageLaw.LyneyActDamageUpgraded),
            StagePerformer.Chevreuse => FurinaStageLaw.ChevreuseActDamage,
            StagePerformer.Freminet => Pick(FurinaStageLaw.FreminetActDamage,
                FurinaStageLaw.FreminetActDamageUpgraded),
            StagePerformer.Escoffier => Pick(FurinaStageLaw.EscoffierActDamage,
                FurinaStageLaw.EscoffierActDamageUpgraded),
            _ => 0,
        };
        return who switch
        {
            StagePerformer.Charlotte =>
                "The first time one of your cards [gold]Repays[/gold]"
              + " each turn, draw "
              + FurinaStageLaw.CharlotteLineDraw + " card. Act: "
              + "[gold]Repay[/gold] " + act + ". Gain 1 [gold]Block[/gold] "
              + "for any HP it could not [gold]Repay[/gold].",
            StagePerformer.Wriothesley =>
                "Whenever you [gold]Drain[/gold], deal that much "
              + "[gold]Cryo[/gold] damage to a random enemy. Act: deal " + act
              + " [gold]Cryo[/gold] damage to a random enemy.",
            StagePerformer.Lynette =>
                "The first time each turn an enemy makes you lose HP, gain that "
              + "much [gold]Fanfare[/gold] again. Act: deal " + act
              + " [gold]Anemo[/gold] damage to an enemy with an aura.",
            StagePerformer.Clorinde =>
                "Whenever you [gold]Repay[/gold], deal twice that much "
              + "[gold]Electro[/gold] damage to a random enemy. Act: deal "
              + act + " [gold]Electro[/gold] damage to a random enemy.",
            StagePerformer.Lyney =>
                "Your [gold]Drain[/gold] line is "
              + FurinaStageLaw.LyneyLineDrop + " HP lower. Act: "
              + "[gold]Drain[/gold] " + FurinaStageLaw.LyneyActDrain
              + ", never past your line (none at or below it). Deal " + act
              + " [gold]Pyro[/gold] damage to ALL enemies.",
            StagePerformer.Sigewinne =>
                "Whenever you [gold]Repay[/gold], gain that much "
              + "[gold]Block[/gold]. Act: [gold]Repay[/gold] " + act + ". "
              + "Gain 1 [gold]Block[/gold] for any HP it could not "
              + "[gold]Repay[/gold].",
            StagePerformer.Chevreuse =>
                "Whenever you [gold]Spend[/gold], apply "
              + FurinaStageLaw.ChevreuseLineVulnerable
              + " [gold]Vulnerable[/gold]"
              + (upgraded
                    ? " and " + FurinaStageLaw.ChevreuseLineWeakUpgraded
                      + " [gold]Weak[/gold]"
                    : "")
              + " to a random enemy. Act: deal " + act
              + " damage to a random enemy.",
            StagePerformer.Freminet =>
                "Whenever you [gold]Drain[/gold], gain that much "
              + "[gold]Block[/gold]. Act: deal " + act
              + " [gold]Cryo[/gold] damage to a random enemy. Gain "
              + StageDirector.FreminetActBlock(upgraded)
              + " [gold]Block[/gold].",
            StagePerformer.Navia =>
                "Your first [gold]Spend[/gold] each turn costs "
              + NaviaDiscount(upgraded) + " less (a spend-all keeps "
              + NaviaDiscount(upgraded) + "). Act: deal [gold]Geo[/gold] "
              + "damage to a random enemy equal to the "
              + "[gold]Fanfare[/gold] you spent this turn.",
            StagePerformer.Neuvillette =>
                "Your [gold]Hydro[/gold] damage deals "
              + (upgraded ? FurinaStageLaw.NeuvilletteHydroBonusUpgraded
                          : FurinaStageLaw.NeuvilletteHydroBonus)
              + " more. Act: deal [gold]Hydro[/gold] damage to ALL enemies "
              + "equal to the HP you lost since your last turn.",
            StagePerformer.Escoffier =>
                "Whenever a guest acts, [gold]Repay[/gold] "
              + FurinaStageLaw.EscoffierLineRepay + ". Act: deal " + act
              + " [gold]Cryo[/gold] damage to ALL enemies.",
            _ => "",
        };
    }

    private static int NaviaDiscount(bool upgraded) =>
        upgraded ? FurinaStageLaw.NaviaLineDiscountUpgraded
                 : FurinaStageLaw.NaviaLineDiscount;

    /// <summary>Pin this guest's badge on its body, silently, the moment it
    /// is fielded (<c>FurinaStagePets.Field</c>).</summary>
    public static async Task Pin(Creature pet, StagePerformer who,
                                 bool upgraded = false)
    {
        if (pet.Powers.OfType<StagePerformerBadge>().Any()) return;
        var context = new ThrowingPlayerChoiceContext();
        switch (who, upgraded)
        {
            case (StagePerformer.Wriothesley, false):
                await Apply<WriothesleyBadgePower>(context, pet);
                break;
            case (StagePerformer.Wriothesley, true):
                await Apply<WriothesleyUpgradedBadgePower>(context, pet);
                break;
            case (StagePerformer.Lynette, false):
                await Apply<LynetteBadgePower>(context, pet);
                break;
            case (StagePerformer.Lynette, true):
                await Apply<LynetteUpgradedBadgePower>(context, pet);
                break;
            case (StagePerformer.Clorinde, false):
                await Apply<ClorindeBadgePower>(context, pet);
                break;
            case (StagePerformer.Clorinde, true):
                await Apply<ClorindeUpgradedBadgePower>(context, pet);
                break;
            case (StagePerformer.Lyney, false):
                await Apply<LyneyBadgePower>(context, pet);
                break;
            case (StagePerformer.Lyney, true):
                await Apply<LyneyUpgradedBadgePower>(context, pet);
                break;
            case (StagePerformer.Sigewinne, false):
                await Apply<SigewinneBadgePower>(context, pet);
                break;
            case (StagePerformer.Sigewinne, true):
                await Apply<SigewinneUpgradedBadgePower>(context, pet);
                break;
            case (StagePerformer.Chevreuse, false):
                await Apply<ChevreuseBadgePower>(context, pet);
                break;
            case (StagePerformer.Chevreuse, true):
                await Apply<ChevreuseUpgradedBadgePower>(context, pet);
                break;
            case (StagePerformer.Freminet, false):
                await Apply<FreminetBadgePower>(context, pet);
                break;
            case (StagePerformer.Freminet, true):
                await Apply<FreminetUpgradedBadgePower>(context, pet);
                break;
            case (StagePerformer.Navia, false):
                await Apply<NaviaBadgePower>(context, pet);
                break;
            case (StagePerformer.Navia, true):
                await Apply<NaviaUpgradedBadgePower>(context, pet);
                break;
            case (StagePerformer.Neuvillette, false):
                await Apply<NeuvilletteBadgePower>(context, pet);
                break;
            case (StagePerformer.Neuvillette, true):
                await Apply<NeuvilletteUpgradedBadgePower>(context, pet);
                break;
            case (StagePerformer.Escoffier, false):
                await Apply<EscoffierBadgePower>(context, pet);
                break;
            case (StagePerformer.Escoffier, true):
                await Apply<EscoffierUpgradedBadgePower>(context, pet);
                break;
            case (_, true):
                await Apply<CharlotteUpgradedBadgePower>(context, pet);
                break;
            default:
                await Apply<CharlotteBadgePower>(context, pet);
                break;
        }
    }

    /// <summary>Swap a standing guest's badge for its upgraded one (a
    /// duplicate upgraded Guest Star moved it). Idempotent.</summary>
    public static async Task Repin(Creature pet, StagePerformer who,
                                   bool upgraded)
    {
        var badge = pet.Powers.OfType<StagePerformerBadge>().FirstOrDefault();
        if (badge != null && badge.Upgraded == upgraded) return;
        if (badge != null) await PowerCmd.Remove(badge);
        await Pin(pet, who, upgraded);
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

// ---- THE POOL TO 75's four guests (2026-10-09). No face art yet: the badge
// wears the game's default icon until an art pass gives it one.

public sealed class FreminetBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Freminet;
    public List<(string, string)>? Localization => Face;
}

public sealed class NaviaBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Navia;
    public List<(string, string)>? Localization => Face;
}

public sealed class NeuvilletteBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Neuvillette;
    public List<(string, string)>? Localization => Face;
}

public sealed class EscoffierBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Escoffier;
    public List<(string, string)>? Localization => Face;
}

// ---- THE UPGRADED BADGES (the pool to 75, sec.3): the same guest, its line
// or act raised.

public sealed class CharlotteUpgradedBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Charlotte;
    public override bool Upgraded => true;
    public List<(string, string)>? Localization => Face;
}

public sealed class WriothesleyUpgradedBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Wriothesley;
    public override bool Upgraded => true;
    public List<(string, string)>? Localization => Face;
}

public sealed class LynetteUpgradedBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Lynette;
    public override bool Upgraded => true;
    public List<(string, string)>? Localization => Face;
}

public sealed class ClorindeUpgradedBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Clorinde;
    public override bool Upgraded => true;
    public List<(string, string)>? Localization => Face;
}

public sealed class LyneyUpgradedBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Lyney;
    public override bool Upgraded => true;
    public List<(string, string)>? Localization => Face;
}

public sealed class SigewinneUpgradedBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Sigewinne;
    public override bool Upgraded => true;
    public List<(string, string)>? Localization => Face;
}

public sealed class ChevreuseUpgradedBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Chevreuse;
    public override bool Upgraded => true;
    public List<(string, string)>? Localization => Face;
}

public sealed class FreminetUpgradedBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Freminet;
    public override bool Upgraded => true;
    public List<(string, string)>? Localization => Face;
}

public sealed class NaviaUpgradedBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Navia;
    public override bool Upgraded => true;
    public List<(string, string)>? Localization => Face;
}

public sealed class NeuvilletteUpgradedBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Neuvillette;
    public override bool Upgraded => true;
    public List<(string, string)>? Localization => Face;
}

public sealed class EscoffierUpgradedBadgePower : StagePerformerBadge, ILocalizationProvider
{
    public override StagePerformer Performer => StagePerformer.Escoffier;
    public override bool Upgraded => true;
    public List<(string, string)>? Localization => Face;
}
