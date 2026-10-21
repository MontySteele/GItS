using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Potions;

/// <summary>
/// YAE'S OWN POTIONS (the Yae pass, 2026-10-16,
/// <c>review/active/yae-ancients-relics-2026-10-16.md</c> sec.4): a refill, a
/// burst and one rule-bending turn, Kokomi's shape (<see cref="ArmPotion"/>:
/// combat only, aimed at a player). Her <c>PotionPool</c> answers
/// <see cref="YaePotionPool"/>, her three and nothing borrowed. Each asks
/// <see cref="YaeShrine.Live"/>: handed to anyone else, it does nothing. No
/// sim twin until Balance.
/// </summary>
public static class YaePotions
{
    public static readonly IReadOnlyList<Type> Types = new[]
    {
        typeof(BottledSakura), typeof(FoxsInkwell), typeof(NarukamiSake),
    };

    /// <summary>Her Sakura tip, read off her starter.</summary>
    internal static IEnumerable<IHoverTip> SakuraTip(IEnumerable<IHoverTip> inherited) =>
        ArmKeywordTips.ForSakura(inherited, ModelDb.Card<ProtoYmYakanEvocation>());
}

/// <summary>Common. "Plant 2 Sakura." Twin Sakura's plant, one at a time
/// (each into a full shrine makes the Sakura closest to withering act first).</summary>
public sealed class BottledSakura : ArmPotion
{
    public const int Sakura = 2;

    public override PotionRarity Rarity => PotionRarity.Common;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Bottled Sakura"),
        ("description",
            "Plant [blue]" + Sakura + "[/blue] [gold]Sakura[/gold]."),
    };

    public override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForFullShrine(YaePotions.SakuraTip(Array.Empty<IHoverTip>()), null);

    protected override string ArtPath => ArmPotions.Image("yae", "bottled_sakura");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        if (!YaeShrine.Live(target)) return;
        await YaeShrine.Plant(choiceContext, target, Sakura);
    }
}

/// <summary>Uncommon. "Edit a card in your hand with an Annotation of your
/// choice." "Choose an Annotation" is Reborn as Guuji Yae's existing modal
/// (<see cref="Cards.Prototype.YaeModalOptions.Choose"/>), then one Edit of
/// one card in hand, every card a candidate (no card is doing the Edit).
/// An Edit like any other: Serialization, Proofreader's Glasses and Yae
/// Publishing House read it.</summary>
public sealed class FoxsInkwell : ArmPotion
{
    public override PotionRarity Rarity => PotionRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Fox's Inkwell"),
        ("description",
            "[gold]Edit[/gold] a card in your [gold]Hand[/gold] with an "
          + "Annotation of your choice."),
    };

    public override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForEdit(Array.Empty<IHoverTip>(), null);

    protected override string ArtPath => ArmPotions.Image("yae", "foxs_inkwell");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        if (!YaeShrine.Live(target) || target!.Player is not { } owner) return;
        var chosen = await Cards.Prototype.YaeModalOptions.Choose(choiceContext, owner);
        if (chosen == YaeAnnotation.None) return;
        await YaeEditing.EditOneFor(choiceContext, owner, this, chosen);
    }
}

/// <summary>Rare. "Each Sakura gains 2 Levels. Tenko." The Levels first, so
/// the Tenko's strikes are the bigger ones; then Tenko (Kagura Bell Levels
/// after its strikes). With no Sakura standing it does nothing.</summary>
public sealed class NarukamiSake : ArmPotion
{
    public const int Levels = 2;

    public override PotionRarity Rarity => PotionRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Narukami Sake"),
        ("description",
            "Each [gold]Sakura[/gold] gains [blue]" + Levels + "[/blue] Levels. "
          + "[gold]Tenko[/gold]."),
    };

    public override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForTenko(YaePotions.SakuraTip(Array.Empty<IHoverTip>()), null);

    protected override string ArtPath => ArmPotions.Image("yae", "narukami_sake");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        if (!YaeShrine.Live(target)) return;
        YaeShrineLedger.For(target!).LevelUp(Levels);
        await SakuraBadge.Sync(choiceContext, target!);
        await YaeShrine.Tenko(choiceContext, target);
    }
}

/// <summary>Yae's potion pool: her three, and nothing borrowed (the Defect's
/// borrow went with her own set, as Kokomi's Silent borrow did).</summary>
public sealed class YaePotionPool : PotionPoolModel
{
    // Her own orb (card frames stage 2): the kit card pool's energy name, so
    // BaseLib's icon hook draws the same orb on this pool's tooltips.
    public override string EnergyColorName => KitEnergyIcon.NameOf<YaeCardPool>();

    public override Color LabOutlineColor => new("B07FE0");

    protected override IEnumerable<PotionModel> GenerateAllPotions() => new PotionModel[]
    {
        ModelDb.Potion<BottledSakura>(),
        ModelDb.Potion<FoxsInkwell>(),
        ModelDb.Potion<NarukamiSake>(),
    };
}
