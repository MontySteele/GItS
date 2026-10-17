using System.Collections.Generic;
using System.Threading.Tasks;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;

namespace KleeMod.Potions;

// ---- Furina's card pass (2026-10-15) ---------------------------------------
//
// `review/active/furina-card-pass-2026-10-15.md` sec.3: her Uncommon and Rare
// beside Bottled Applause (`ArmPotions.cs`), so her pool holds the base
// game's shape of three. In a file of their own so the shared ArmPotions.cs
// changes only in her list and her pool.

/// <summary>Uncommon: "Each guest acts twice." Front to back, each guest's
/// two acts together (<see cref="StageDirector.ActEachTwice"/>).</summary>
public sealed class BottledEncore : ArmPotion
{
    public override PotionRarity Rarity => PotionRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Bottled Encore"),
        ("description", "Each guest acts twice."),
    };

    protected override string ArtPath =>
        ArmPotions.Image("furina", "bottled_encore");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        if (!FurinaStage.LiveFor(target)) return;
        using (FurinaStageLedger.For(target!).CausedBy("Bottled Encore"))
        {
            await FurinaStage.ActEachTwice(choiceContext, target);
        }
    }
}

/// <summary>Rare: "Repay all your drained HP." Singer of Many Waters' Repay
/// (<see cref="FurinaStage.RepayAll"/>), so it pays Fanfare and its readers
/// as any Repay does.</summary>
public sealed class WaterOfLucine : ArmPotion
{
    public override PotionRarity Rarity => PotionRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Water of Lucine"),
        ("description", "[gold]Repay[/gold] all your drained HP."),
    };

    protected override string ArtPath =>
        ArmPotions.Image("furina", "water_of_lucine");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        if (!FurinaStage.LiveFor(target)) return;
        using (FurinaStageLedger.For(target!).CausedBy("Water of Lucine"))
        {
            await FurinaStage.RepayAll(choiceContext, target);
        }
    }
}
