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
/// Each relic is a READ or a one-line hook: the Stage asks whether a relic is
/// held (<see cref="Holds{T}"/>, <see cref="FurinaStage.ModsOf"/>) at the one
/// site the rule it bends lives -- the opening, the Bow, the Guest Star, the
/// turn start, the Spend. With the Stage off every read answers "not held".
/// The re-founding's sheet (sec.10) rewrote Opera Glasses, Grand Theater
/// Program and Guest Book on the one Fanfare number.
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

/// <summary>Common (sec.10): "Start each combat with 3 Fanfare."</summary>
public sealed class OperaGlasses : CustomRelicModel
{
    public const int Fanfare = 3;

    public OperaGlasses() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Common;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Opera Glasses"),
        ("description",
            "Start each combat with [blue]" + Fanfare
          + "[/blue] [gold]Fanfare[/gold]."),
    };

    public override async Task BeforeCombatStart()
    {
        var furina = Owner?.Creature;
        if (!FurinaStage.LiveFor(furina)) return;
        Flash();
        await FurinaStage.Gain(new ThrowingPlayerChoiceContext(), furina,
                               Fanfare, "Opera Glasses");
    }

    protected override string IconBaseName => "snake_ring";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("opera_glasses")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("opera_glasses")) ?? base.BigIconPath;
}

/// <summary>Uncommon. "Whenever a performer Bows, gain 3 Block." Paid after
/// the Bow's act and its Fanfare (<see cref="StageDirector.Bow"/>).</summary>
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

    protected override string IconBaseName => "snake_ring";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("stagehands_gloves")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("stagehands_gloves")) ?? base.BigIconPath;
}

/// <summary>Uncommon (sec.10): "The first time you summon a Guest Star each
/// combat, gain 3 Fanfare." The latch is the combat's stage ledger's, spent
/// by <see cref="StageDirector.SummonGuest"/>.</summary>
public sealed class GuestBook : CustomRelicModel
{
    public const int Bonus = 3;

    public GuestBook() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Guest Book"),
        ("description",
            "The first time you summon a [gold]Guest Star[/gold] each combat, "
          + "gain [blue]" + Bonus + "[/blue] [gold]Fanfare[/gold]."),
    };

    /// <summary>The Fanfare this Guest Star summon is owed: 3 while the
    /// combat's latch is open, 0 after or without the relic.</summary>
    public static int BonusFor(Creature furina)
    {
        if (!FurinaStageRelics.Holds<GuestBook>(furina)) return 0;
        if (FurinaStageLedger.For(furina).GuestBookSpent) return 0;
        FurinaStageRelics.Flash<GuestBook>(furina);
        return Bonus;
    }

    protected override string IconBaseName => "snake_ring";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("guest_book")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("guest_book")) ?? base.BigIconPath;
}

/// <summary>Rare (sec.10, overriding sec.8): "At the start of your turn, gain
/// 1 Fanfare." Paid in <see cref="FurinaStage.TurnStart"/>.</summary>
public sealed class GrandTheaterProgram : CustomRelicModel
{
    public const int Fanfare = 1;

    public GrandTheaterProgram() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Grand Theater Program"),
        ("description",
            "At the start of your turn, gain [blue]" + Fanfare
          + "[/blue] [gold]Fanfare[/gold]."),
    };

    protected override string IconBaseName => "snake_ring";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("grand_theater_program")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("grand_theater_program")) ?? base.BigIconPath;
}

/// <summary>Rare. "A performer that Bows acts twice as it leaves." Read by
/// <see cref="StageDirector.Bow"/> through <see cref="FurinaStage.ModsOf"/>.
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

/// <summary>Rare. "Your Spends cost 1 less Fanfare." Read by
/// <c>FurinaStage.PriceOf</c>, at the Spend gate and the payment alike. A
/// spend-all has no price to lower. Game-side only, like every relic.
/// </summary>
public sealed class PalaisLedger : CustomRelicModel
{
    /// <summary>What it takes off a Spend's price, per copy.</summary>
    public const int Discount = 1;

    public PalaisLedger() : base(autoAdd: false) { }

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Palais Ledger"),
        ("description",
            "Your [gold]Spend[/gold]s cost [blue]" + Discount + "[/blue] less "
          + "[gold]Fanfare[/gold]."),
    };

    protected override string IconBaseName => "snake_ring";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("palais_ledger")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("palais_ledger")) ?? base.BigIconPath;
}

/// <summary>Shop. "At the start of each combat, summon a random performer
/// behind your Usher": a random Salon member, LATE in the combat start, so
/// the starter has already put Usher on stage (the opening is idempotent, so
/// it is asked again here).</summary>
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
