using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Relics;

/// <summary>
/// FURINA'S OWN RELICS (the Salon's Tab, 2026-10-05, proposal sec.16): her
/// pool keeps Opera Glasses and Grand Theater Program beside Salon Solitaire
/// and The Curtain Never Falls. Stagehand's Gloves, Guest Book, Curtain Call
/// Bouquet, Palais Ledger and Opening Night left with the v2 Stage: each
/// named the trio, the Bow or the guests' Fanfare.
///
/// FURINA'S CARD PASS (2026-10-15,
/// <c>review/active/furina-card-pass-2026-10-15.md</c> sec.2; kit census
/// pick 1 (a), [USER]: "Agreed on all of the above!") adds five: two
/// Uncommons, two Rares and a Shop relic.
/// </summary>
public static class FurinaStageRelics
{
    /// <summary>Her seven, by rarity, in the papers' table order.</summary>
    public static readonly IReadOnlyList<Type> Types = new[]
    {
        typeof(OperaGlasses),
        typeof(OperaTicketStub), typeof(FontaineTeardrop),
        typeof(GrandTheaterProgram), typeof(ClaquesLedger),
        typeof(BouquetOfRoses),
        typeof(EpicleseSeasonPass),
    };

    /// <summary>Does this Furina, on a live Stage, hold <typeparamref name="T"/>?
    /// </summary>
    public static bool Holds<T>(Creature? furina) where T : RelicModel =>
        Count<T>(furina) > 0;

    internal static int Count<T>(Creature? furina) where T : RelicModel =>
        FurinaResources.IsFurina(furina) && furina!.Player is { } player
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
        if (!FurinaResources.IsFurina(furina)) return;
        Flash();
        await FurinaStage.Gain(new ThrowingPlayerChoiceContext(), furina,
                               Fanfare, "Opera Glasses");
    }

    protected override string IconBaseName => "ring_of_the_snake";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("opera_glasses")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("opera_glasses")) ?? base.BigIconPath;
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

    protected override string IconBaseName => "ring_of_the_snake";
    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("grand_theater_program")) ?? base.PackedIconPath;
    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon("grand_theater_program")) ?? base.BigIconPath;
}


// ---- Furina's card pass (2026-10-15) ---------------------------------------

/// <summary>One of the card pass's five: <c>furina/relics/&lt;slug&gt;.png</c>,
/// the base game's placeholder until its art lands.</summary>
public abstract class FurinaStageRelic : CustomRelicModel
{
    protected FurinaStageRelic() : base(autoAdd: false) { }

    protected abstract string Slug { get; }

    protected override string IconBaseName => "ring_of_the_snake";

    public override string PackedIconPath =>
        KleePck.Path(FurinaStageRelics.Icon(Slug)) ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path(FurinaStageRelics.Icon(Slug)) ?? base.BigIconPath;
}

/// <summary>Uncommon: "At the start of each combat, Summon a random guest."
/// The guest Ensemble Cast summons (<see cref="FurinaStage.SummonRandom"/>),
/// on her first turn after the opening draw (Fresh Catch's hook). Copies
/// summon one each.</summary>
public sealed class OperaTicketStub : FurinaStageRelic
{
    protected override string Slug => "opera_ticket_stub";

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Opera Ticket Stub"),
        ("description",
            "At the start of each combat, [gold]Summon[/gold] a random guest."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForSummon(Array.Empty<IHoverTip>(), null!);

    /// <summary>Her own first turn, alive, on a live Stage.</summary>
    public static bool Fires(RelicModel relic, Player player) =>
        player == relic.Owner
        && player.PlayerCombatState?.TurnNumber == 1
        && player.Creature is { IsDead: false } furina
        && FurinaResources.IsFurina(furina);

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!Fires(this, player)) return;
        Flash();
        await FurinaStage.SummonRandom(choiceContext, player.Creature);
    }
}

/// <summary>Uncommon: "An unreturned Repay gains 2 Block for each HP instead
/// of 1." (furina-next paper 3, 2026-10-16, pick 1: the rule made its old
/// text, "Whenever you Repay more than you have drained, gain the rest as
/// Block", every Repay's.) Paid in <see cref="StageDirector.FloorBlock"/>.
/// </summary>
public sealed class FontaineTeardrop : FurinaStageRelic
{
    protected override string Slug => "fontaine_teardrop";

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Fontaine Teardrop"),
        ("description",
            "An unreturned [gold]Repay[/gold] gains 2 [gold]Block[/gold] for "
          + "each HP instead of 1."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForRepay(Array.Empty<IHoverTip>(), null!);
}

/// <summary>Rare: "Whenever a guest acts, gain 1 Fanfare." Paid in
/// <see cref="StageDirector.Act"/>.</summary>
public sealed class ClaquesLedger : FurinaStageRelic
{
    public const int Fanfare = 1;

    protected override string Slug => "claques_ledger";

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Claque's Ledger"),
        ("description",
            "Whenever a guest acts, gain [blue]" + Fanfare
          + "[/blue] [gold]Fanfare[/gold]."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForFanfare(Array.Empty<IHoverTip>(), null!);
}

/// <summary>Rare: "Whenever you Spend 10 or more at once, gain [E]." Paid in
/// the director's Spend (<c>StageDirector.AfterSpend</c>).</summary>
public sealed class BouquetOfRoses : FurinaStageRelic
{
    public const int Energy = 1;

    protected override string Slug => "bouquet_of_roses";

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Bouquet of Roses"),
        ("description",
            "Whenever you [gold]Spend[/gold] " + FurinaStageLaw.BouquetSpend
          + " or more at once, gain {energyPrefix:energyIcons(" + Energy
          + ")}."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForSpend(Array.Empty<IHoverTip>(), null!);
}

/// <summary>Shop: "You have 1 more guest seat." Read in
/// <see cref="FurinaStage.ModsOf"/>: 3 seats become 4, and 5 with Ensemble
/// Cast.</summary>
public sealed class EpicleseSeasonPass : FurinaStageRelic
{
    protected override string Slug => "epiclese_season_pass";

    public override RelicRarity Rarity => RelicRarity.Shop;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Epiclese Season Pass"),
        ("description",
            "You have [blue]" + FurinaStageLaw.SeasonPassSeats
          + "[/blue] more guest seat."),
    };
}
