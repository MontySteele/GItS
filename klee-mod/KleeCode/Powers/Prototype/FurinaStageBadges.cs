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
// THE POOL TO 75 (review/ruled/furina-pool-growth-2026-10-09.md sec.3): an
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
    /// <paramref name="upgraded"/>. ENGLISH, whatever the language: it is the
    /// badge's model row (written once, at boot) and the blind seat's tip. A
    /// player's guest tip reads the keyed rows (<see cref="LineText"/>,
    /// <see cref="ActOnlyText"/>, <see cref="GuestText"/>).
    /// </summary>
    public static string ActText(StagePerformer who, bool upgraded = false)
    {
        if (LineTemplate(who, upgraded) == null || ActTemplate(who) == null) return "";
        var vars = GuestVars(who, upgraded);
        return CodeText.English(LineRow(who, upgraded), vars) + " "
             + CodeText.English(ActRow(who), vars);
    }

    // ---- the keyed rows (the localization census, 2026-10-23) ------------
    //
    // A guest's tip shows its line, its act, or both, by what its card's face
    // already prints (`Cards.PlayerTips.Guest`), so the two sentences are two
    // rows, and "both" is a third row that joins them. Keys:
    // `KLEEMOD-ARM_STAGE_<GUEST>.description_line` (and `_line_upgraded`
    // where the upgraded line is another sentence) and `.description_act`.

    private const string Table = "card_keywords";

    /// <summary>The guest's tip key, `KLEEMOD-ARM_STAGE_CHARLOTTE`
    /// (<c>ArmKeywordTips.CharlotteKey</c>).</summary>
    private static string KeyOf(StagePerformer who) =>
        "KLEEMOD-ARM_STAGE_" + who.ToString().ToUpperInvariant();

    /// <summary>The line's English, with its numbers as vars.</summary>
    internal static string? LineTemplate(StagePerformer who, bool upgraded) => who switch
    {
        StagePerformer.Charlotte =>
            "The first time each turn one of your cards [gold]Repays[/gold], draw "
          + "{LineDraw} card{LineDraw:plural:|s}.",
        StagePerformer.Wriothesley =>
            "Whenever you [gold]Drain[/gold], deal that much [gold]Cryo[/gold] "
          + "damage to a random enemy.",
        StagePerformer.Lynette =>
            "The first time each turn you lose HP to an enemy, gain that much "
          + "[gold]Fanfare[/gold] again.",
        StagePerformer.Clorinde =>
            "Whenever you [gold]Repay[/gold], deal twice that much "
          + "[gold]Electro[/gold] damage to a random enemy.",
        StagePerformer.Lyney =>
            // Furina round 5 (2026-10-11): in buffer words, the model since
            // 2026-10-11 (`FurinaStageLaw.BufferOf` adds 10).
            "Your [gold]Drain[/gold] buffer is {LineDrop} HP larger.",
        StagePerformer.Sigewinne =>
            "Whenever you [gold]Repay[/gold], gain that much [gold]Block[/gold].",
        StagePerformer.Chevreuse => upgraded
            ? "Whenever you [gold]Spend[/gold], apply {LineVulnerable} "
              + "[gold]Vulnerable[/gold] and {LineWeak} [gold]Weak[/gold] to a "
              + "random enemy."
            : "Whenever you [gold]Spend[/gold], apply {LineVulnerable} "
              + "[gold]Vulnerable[/gold] to a random enemy.",
        StagePerformer.Freminet =>
            "Whenever you [gold]Drain[/gold], gain that much [gold]Block[/gold].",
        StagePerformer.Navia =>
            "Your first [gold]Spend[/gold] each turn costs {LineDiscount} less.",
        StagePerformer.Neuvillette =>
            "Your [gold]Hydro[/gold] damage deals {LineBonus} additional damage.",
        StagePerformer.Escoffier =>
            "Your guests' acts deal {LineBonus} additional damage.",
        _ => null,
    };

    /// <summary>The act's English, "Act: ...", with its numbers as vars.</summary>
    internal static string? ActTemplate(StagePerformer who) => who switch
    {
        // furina-next paper 3 (2026-10-16): the Block floor is the Repay
        // rule, so the act drops the clause.
        StagePerformer.Charlotte => "Act: [gold]Repay[/gold] {Act}.",
        StagePerformer.Wriothesley =>
            "Act: deal {Act} [gold]Cryo[/gold] damage to a random enemy.",
        StagePerformer.Lynette =>
            "Act: deal {Act} [gold]Anemo[/gold] damage to an enemy, aura first.",
        StagePerformer.Clorinde =>
            "Act: deal {Act} [gold]Electro[/gold] damage to a random enemy.",
        StagePerformer.Lyney =>
            "Act: [gold]Drain[/gold] {ActDrain} and deal {Act} [gold]Pyro[/gold] "
          + "damage to ALL enemies. It never [gold]Drains[/gold] past your line.",
        StagePerformer.Sigewinne => "Act: [gold]Repay[/gold] {Act}.",
        StagePerformer.Chevreuse => "Act: deal {Act} damage to a random enemy.",
        StagePerformer.Freminet =>
            "Act: gain {Act} [gold]Block[/gold], and more for "
          + "[gold]Fanfare[/gold]: [gold]Spend[/gold] a quarter of it, rounded "
          + "down, for that much.",
        StagePerformer.Navia =>
            "Act: [gold]Spend[/gold] a third of your [gold]Fanfare[/gold] to "
          + "deal twice that much [gold]Geo[/gold] damage to a random enemy.",
        StagePerformer.Neuvillette =>
            "Act: deal [gold]Hydro[/gold] damage to ALL enemies equal to HP "
          + "lost or [gold]Drained[/gold] since your last turn.",
        StagePerformer.Escoffier =>
            "Act: deal {Act} [gold]Cryo[/gold] damage to ALL enemies.",
        _ => null,
    };

    /// <summary>The guest's numbers, read off <see cref="FurinaStageLaw"/> by
    /// name (`EB-89`), base and upgraded -- the same pairs
    /// `StageDirector.ActAmount` reads.</summary>
    internal static IReadOnlyDictionary<string, object> GuestVars(StagePerformer who, bool upgraded)
    {
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
            StagePerformer.Freminet => Pick(FurinaStageLaw.FreminetActBlock,
                FurinaStageLaw.FreminetActBlockUpgraded),
            StagePerformer.Escoffier => Pick(FurinaStageLaw.EscoffierActDamage,
                FurinaStageLaw.EscoffierActDamageUpgraded),
            _ => 0,
        };
        var lineBonus = who == StagePerformer.Escoffier
            ? Pick(FurinaStageLaw.EscoffierLineBonus, FurinaStageLaw.EscoffierLineBonusUpgraded)
            : Pick(FurinaStageLaw.NeuvilletteHydroBonus, FurinaStageLaw.NeuvilletteHydroBonusUpgraded);
        return CodeText.Vars(
            ("Act", act),
            ("LineDraw", FurinaStageLaw.CharlotteLineDraw),
            ("LineDrop", FurinaStageLaw.LyneyLineDrop),
            ("ActDrain", FurinaStageLaw.LyneyActDrain),
            ("LineVulnerable", FurinaStageLaw.ChevreuseLineVulnerable),
            ("LineWeak", FurinaStageLaw.ChevreuseLineWeakUpgraded),
            ("LineDiscount", NaviaDiscount(upgraded)),
            ("LineBonus", lineBonus));
    }

    /// <summary>The upgraded line is its own row only where it is another
    /// sentence (Chevreuse); elsewhere only its number moves.</summary>
    private static bool UpgradedLineIsItsOwn(StagePerformer who) =>
        LineTemplate(who, true) != LineTemplate(who, false);

    internal static CodeRow LineRow(StagePerformer who, bool upgraded) =>
        upgraded && UpgradedLineIsItsOwn(who)
            ? new(Table, KeyOf(who) + ".description_line_upgraded", LineTemplate(who, true)!)
            : new(Table, KeyOf(who) + ".description_line", LineTemplate(who, false)!);

    internal static CodeRow ActRow(StagePerformer who) =>
        new(Table, KeyOf(who) + ".description_act", ActTemplate(who)!);

    /// <summary>"Both", for a face that prints neither: the line, then the
    /// act.</summary>
    internal static readonly CodeRow LineAndActRow =
        new(Table, "KLEEMOD-ARM_STAGE_GUEST_STAR.description_line_and_act", "{Line} {Act}");

    /// <summary>The guest's line, as the player reads it.</summary>
    internal static string LineText(StagePerformer who, bool upgraded) =>
        CodeText.Format(LineRow(who, upgraded), GuestVars(who, upgraded));

    /// <summary>The guest's act, as the player reads it.</summary>
    internal static string ActOnlyText(StagePerformer who, bool upgraded) =>
        CodeText.Format(ActRow(who), GuestVars(who, upgraded));

    /// <summary>The line and the act, as the player reads them.</summary>
    internal static string GuestText(StagePerformer who, bool upgraded) =>
        CodeText.Format(LineAndActRow, CodeText.Vars(
            ("Line", LineText(who, upgraded)), ("Act", ActOnlyText(who, upgraded))));

    /// <summary>Every guest row (<see cref="CodeText.Sources"/>).</summary>
    public static IEnumerable<CodeRow> TipRows()
    {
        foreach (var who in System.Enum.GetValues<StagePerformer>())
        {
            if (LineTemplate(who, false) == null || ActTemplate(who) == null) continue;
            yield return LineRow(who, false);
            if (UpgradedLineIsItsOwn(who)) yield return LineRow(who, true);
            yield return ActRow(who);
        }
        yield return LineAndActRow;
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
