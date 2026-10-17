using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Potions;

/// <summary>
/// KOKOMI'S OWN POTIONS (<c>review/active/kokomi-relics-potions-2026-10-15.md</c>,
/// kit census pick 1 (a)): a refill, a burst and one rule-bending turn,
/// Klee's, Varka's and Furina's shape (<see cref="ArmPotion"/>: combat only,
/// aimed at a player). Her <c>PotionPool</c> answers
/// <see cref="KokomiPotionPool"/>, her three and nothing borrowed. Each asks
/// <see cref="KokomiOverhaul.LiveFor"/>: handed to anyone else, it does
/// nothing. No sim twin until Balance.
/// </summary>
public static class KokomiPotions
{
    public static readonly IReadOnlyList<Type> Types = new[]
    {
        typeof(BottledShoal), typeof(BottledTide), typeof(AStunningStratagem),
    };
}

/// <summary>Common. "Add 3 Stings to your Hand." Shoal Call's door
/// (<see cref="KokomiCards.AddJellyfish"/>), so Kurage Lantern reads them
/// and a full hand sends the rest to the Discard Pile.</summary>
public sealed class BottledShoal : ArmPotion
{
    public const int Stings = 3;

    public override PotionRarity Rarity => PotionRarity.Common;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Bottled Shoal"),
        ("description",
            "Add [blue]" + Stings + "[/blue] [gold]Stings[/gold] to your "
          + "[gold]Hand[/gold]."),
    };

    public override IEnumerable<IHoverTip> ExtraHoverTips =>
        KokomiCards.WithStingPreview(Array.Empty<IHoverTip>());

    protected override string ArtPath =>
        ArmPotions.Image("kokomi", "bottled_shoal");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        if (!KokomiOverhaul.LiveFor(target)) return;
        await KokomiCards.AddJellyfish(target!.Player,
            KokomiCards.Jellyfish.Sting, Stings, upgraded: false);
    }
}

/// <summary>Uncommon. "The Bake-Kurage carries out every waiting Plan now."
/// Change of Plans' door once per waiting Plan
/// (<see cref="KokomiPlan.ResolveEveryNow"/>), front first.</summary>
public sealed class BottledTide : ArmPotion
{
    public override PotionRarity Rarity => PotionRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Bottled Tide"),
        ("description",
            "The [gold]Bake-Kurage[/gold] carries out every waiting "
          + "[gold]Plan[/gold] now."),
    };

    protected override string ArtPath =>
        ArmPotions.Image("kokomi", "bottled_tide");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        await KokomiPlan.ResolveEveryNow(choiceContext, target);
    }
}

/// <summary>Rare. "Next turn, every Plan is carried out twice." Kokomi's
/// special dish. Puts <see cref="StunningStratagemPower"/> on her, armed for
/// the round after this one.</summary>
public sealed class AStunningStratagem : ArmPotion
{
    public override PotionRarity Rarity => PotionRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "A Stunning Stratagem"),
        ("description",
            "Next turn, every [gold]Plan[/gold] is carried out twice."),
    };

    protected override string ArtPath =>
        ArmPotions.Image("kokomi", "a_stunning_stratagem");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        if (!KokomiOverhaul.LiveFor(target)) return;
        await PowerCmd.Apply<StunningStratagemPower>(
            choiceContext, target!, 1, target, null);
        Arm(target!);
    }

    /// <summary>Arm the power she now wears for the next round.</summary>
    public static void Arm(Creature kokomi)
    {
        var power = kokomi.Powers.OfType<StunningStratagemPower>()
            .FirstOrDefault();
        power?.Arm(kokomi.CombatState?.RoundNumber ?? 0);
    }
}

/// <summary>Kokomi's potion pool: her three, and nothing borrowed (census
/// pick 2: the Silent borrow goes once she has her own set).</summary>
public sealed class KokomiPotionPool : MegaCrit.Sts2.Core.Models.PotionPoolModel
{
    public override string EnergyColorName => "silent";

    public override Color LabOutlineColor => new("6FC8D6");

    protected override IEnumerable<PotionModel> GenerateAllPotions() => new PotionModel[]
    {
        ModelDb.Potion<BottledShoal>(),
        ModelDb.Potion<BottledTide>(),
        ModelDb.Potion<AStunningStratagem>(),
    };
}
