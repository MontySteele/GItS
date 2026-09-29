#if PROTOTYPE_CARDS
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Relics;

/// <summary>
/// FURINA'S OWN RELICS, the Stage arm's pool
/// (<c>review/active/relics-potions-klee-furina-2026-09-27.md</c>, ruled
/// 2026-09-27 at the defaults): one Common, two Uncommons, three Rares and one
/// Shop relic beside Salon Solitaire. Under the Stage they, the starter and The
/// Curtain Never Falls are her whole relic pool; the Silent borrow and the
/// Ethereal Spotlight leave it (<see cref="FurinaRelicPool"/>).
///
/// Each relic is a READ: the Stage's own verbs ask whether the relic is held
/// (<see cref="Holds{T}"/>) at the one site the rule it bends lives --
/// the opening, the Bow, the Guest Star, the fade, the Spend -- so a rule is
/// bent in one place and the forecast sees what play sees. With the Stage off
/// every read answers "not held".
/// </summary>
public static class FurinaStageRelics
{
    /// <summary>The seven, in the paper's table order.</summary>
    public static readonly IReadOnlyList<Type> Types = new[]
    {
        typeof(OperaGlasses), typeof(StagehandsGloves), typeof(GuestBook),
        typeof(GrandTheaterProgram), typeof(CurtainCallBouquet),
        typeof(PalaisLedger), typeof(OpeningNight),
    };

    /// <summary>Does this Furina, on a live Stage, hold <typeparamref name="T"/>?
    /// </summary>
    public static bool Holds<T>(Creature? furina) where T : RelicModel =>
        Count<T>(furina) > 0;

    internal static int Count<T>(Creature? furina) where T : RelicModel =>
        FurinaStage.LiveFor(furina) && furina!.Player is { } player
            ? player.Relics.OfType<T>().Count()
            : 0;

    internal static void Flash<T>(Creature furina) where T : RelicModel
    {
        foreach (var relic in furina.Player!.Relics.OfType<T>()) relic.Flash();
    }

    internal static string Icon(string slug) => "furina/relics/" + slug + ".png";
}

/// <summary>Common. "Your Usher starts each combat at 5 Fanfare instead of
/// 3." Read by <see cref="FurinaStage.OpenCombat"/>.</summary>
public sealed class OperaGlasses : CustomRelicModel
{
    public const int OpeningFanfare = 5;

    public OperaGlasses() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Common;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Opera Glasses"),
        ("description",
            "Your [gold]Usher[/gold] starts each combat at [blue]"
          + OpeningFanfare + "[/blue] [gold]Fanfare[/gold] instead of "
          + FurinaStageLaw.OpeningFanfare + "."),
    };

    /// <summary>The Fanfare the opening Usher takes the front seat with.
    /// </summary>
    public static int OpeningFor(Creature? furina) =>
        FurinaStageRelics.Holds<OperaGlasses>(furina)
            ? OpeningFanfare
            : FurinaStageLaw.OpeningFanfare;

    protected override string IconBaseName => "snake_ring";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("opera_glasses")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("opera_glasses")) ?? base.BigIconPath;
}

/// <summary>Uncommon. "Whenever a performer Bows, gain 3 Block." Paid after
/// the Bow's own act, from <see cref="FurinaStage.Bow"/>.</summary>
public sealed class StagehandsGloves : CustomRelicModel
{
    public const int Block = 3;

    public StagehandsGloves() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Stagehand's Gloves"),
        ("description",
            "Whenever a performer [gold]Bows[/gold], gain [blue]" + Block
          + "[/blue] [gold]Block[/gold]."),
    };

    /// <summary>The Block one Bow pays: 3 a copy.</summary>
    public static int BlockFor(Creature? furina) =>
        Block * FurinaStageRelics.Count<StagehandsGloves>(furina);

    public static async Task AfterBow(Creature furina)
    {
        var block = BlockFor(furina);
        if (block <= 0 || furina.IsDead) return;
        FurinaStageRelics.Flash<StagehandsGloves>(furina);
        await CreatureCmd.GainBlock(furina, block, ValueProp.Unpowered, null,
                                    fast: true);
        // Relics smoke seat 2026-09-27: its Block was named nowhere.
        Powers.RelicAnswerLog.NoteGain("Stagehand's Gloves", block, "Block");
    }

    protected override string IconBaseName => "snake_ring";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("stagehands_gloves")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("stagehands_gloves")) ?? base.BigIconPath;
}

/// <summary>Uncommon. "The first Guest Star you summon each combat arrives
/// with 3 more Fanfare." The latch is the combat's stage ledger's.</summary>
public sealed class GuestBook : CustomRelicModel
{
    public const int Bonus = 3;

    public GuestBook() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Guest Book"),
        ("description",
            "The first [gold]Guest Star[/gold] you summon each combat arrives "
          + "with [blue]" + Bonus + "[/blue] more [gold]Fanfare[/gold]."),
    };

    /// <summary>The extra Fanfare this Guest Star arrives with: 3 for the
    /// first of the combat, 0 after. Spends the combat's latch.</summary>
    public static int TakeBonus(Creature furina)
    {
        if (!FurinaStageRelics.Holds<GuestBook>(furina)) return 0;
        var ledger = FurinaStageLedger.For(furina);
        if (ledger.GuestBookSpent) return 0;
        ledger.GuestBookSpent = true;
        FurinaStageRelics.Flash<GuestBook>(furina);
        return Bonus;
    }

    protected override string IconBaseName => "snake_ring";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("guest_book")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("guest_book")) ?? base.BigIconPath;
}

/// <summary>Rare. "The applause no longer fades." Rule 12 off, at
/// <see cref="FurinaStage.Fades"/>, which the end-of-turn fade and the
/// forecast both read.</summary>
public sealed class GrandTheaterProgram : CustomRelicModel
{
    public GrandTheaterProgram() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Grand Theater Program"),
        ("description",
            "Your performers no longer fade."),
    };

    protected override string IconBaseName => "snake_ring";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("grand_theater_program")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("grand_theater_program")) ?? base.BigIconPath;
}

/// <summary>Rare. "A performer that Bows acts twice as it leaves." Read at
/// <see cref="FurinaStage.Bow"/>, and by the ledger's Bow Block, so the Block
/// an emptied Usher's Bow catches from the rest of a hit is both acts'.
/// </summary>
public sealed class CurtainCallBouquet : CustomRelicModel
{
    public const int BowActs = 2;

    public CurtainCallBouquet() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Curtain Call Bouquet"),
        ("description",
            "A performer that [gold]Bows[/gold] acts twice as it leaves."),
    };

    /// <summary>How many times a Bow's act resolves: 2 with the Bouquet
    /// (copies do not stack), 1 without.</summary>
    public static int ActsFor(Creature? furina) =>
        FurinaStageRelics.Holds<CurtainCallBouquet>(furina) ? BowActs : 1;

    protected override string IconBaseName => "snake_ring";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("curtain_call_bouquet")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("curtain_call_bouquet")) ?? base.BigIconPath;
}

/// <summary>Rare. "A Spend your back performer can't cover is paid by the
/// performers in front of it, back to front." Read by the ledger's
/// <see cref="FurinaStageLedger.CanSpend"/> and
/// <see cref="FurinaStageLedger.Spend"/>: the Spend is offered only when the
/// whole stage covers it, and every performer the payment empties Bows.
/// </summary>
public sealed class PalaisLedger : CustomRelicModel
{
    public PalaisLedger() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Palais Ledger"),
        ("description",
            "A [gold]Spend[/gold] your [gold]back performer[/gold] can't cover "
          + "is paid by the performers in front of it, back to front."),
    };

    protected override string IconBaseName => "snake_ring";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("palais_ledger")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("palais_ledger")) ?? base.BigIconPath;
}

/// <summary>Shop. "At the start of each combat, summon a random performer
/// behind your Usher." LATE in the combat start, so the starter has already
/// put Usher in front (Salon Solitaire and The Curtain Never Falls both open
/// in <c>BeforeCombatStart</c>); the opening is idempotent, so it is asked
/// again here and a stage opened by neither still reads "behind your Usher".
/// </summary>
public sealed class OpeningNight : CustomRelicModel
{
    public OpeningNight() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Shop;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Opening Night"),
        ("description",
            "At the start of each combat, summon a random performer behind "
          + "your [gold]Usher[/gold]."),
    };

    public override async Task BeforeCombatStartLate()
    {
        var furina = Owner?.Creature;
        if (!FurinaStage.LiveFor(furina)) return;
        await FurinaStage.OpenCombat(furina);
        Flash();
        using (FurinaStageLedger.For(furina!).CausedBy("Opening Night"))
        {
            await FurinaStage.Summon(new ThrowingPlayerChoiceContext(), furina,
                                     "random");
        }
    }

    protected override string IconBaseName => "snake_ring";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("opening_night")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("opening_night")) ?? base.BigIconPath;
}
#endif
