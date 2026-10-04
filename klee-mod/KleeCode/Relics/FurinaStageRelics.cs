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
/// FURINA'S OWN RELICS (the Salon's Tab, 2026-10-05, proposal sec.16): her
/// pool keeps Opera Glasses and Grand Theater Program beside Salon Solitaire
/// and The Curtain Never Falls. Stagehand's Gloves, Guest Book, Curtain Call
/// Bouquet, Palais Ledger and Opening Night left with the v2 Stage: each
/// named the trio, the Bow or the guests' Fanfare.
/// </summary>
public static class FurinaStageRelics
{
    /// <summary>The two, in the paper's table order.</summary>
    public static readonly IReadOnlyList<Type> Types = new[]
    {
        typeof(OperaGlasses), typeof(GrandTheaterProgram),
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

