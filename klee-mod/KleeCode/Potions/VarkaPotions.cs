using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Relics;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.PotionPools;

namespace KleeMod.Potions;

/// <summary>
/// VARKA'S OWN POTIONS (<c>review/active/varka-expansion-2026-10-01.md</c>
/// sec.4, built at the paper's defaults while its picks are open): a refill,
/// a burst and one rule-bending turn, Klee's and Furina's shape
/// (<see cref="ArmPotion"/>: combat only, aimed at a player). His
/// <c>PotionPool</c> answers <see cref="VarkaPotionPool"/>.
///
/// RELIC AND POTION APPLICATIONS GAIN NO OATH (sec.4): Bottled Gale's Swirls
/// run inside <see cref="VarkaOath.NoCredit"/>, so they pay his current
/// element and credit nothing. Bottled Resolve sets his element and gains its
/// 3 Oath because its face says so.
/// </summary>
public static class VarkaPotions
{
    public static readonly IReadOnlyList<Type> Types = new[]
    {
        typeof(BottledResolve), typeof(BottledGale), typeof(ElixirOfTheFourWinds),
    };
}

/// <summary>Common. "Choose an element. It becomes your current element;
/// gain 3 Oath of it." Change of Guard's grid, over all four.</summary>
public sealed class BottledResolve : ArmPotion
{
    public const int Oath = 3;

    public override PotionRarity Rarity => PotionRarity.Common;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Bottled Resolve"),
        ("description",
            "Choose an element. It becomes your [gold]current element[/gold]; "
          + "gain [blue]" + Oath + "[/blue] [gold]Oath[/gold] of it."),
    };

    protected override string ArtPath =>
        ArmPotions.Image("varka", "bottled_resolve");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        if (!VarkaPrototype.IsVarka(target)) return;
        var element = await VarkaRules.ChooseElement(
            choiceContext, target!.Player, VarkaOathLedger.Elements);
        await Use(choiceContext, target, element);
    }

    /// <summary>The effect once the element is chosen.</summary>
    public static async Task Use(
        PlayerChoiceContext choiceContext, Creature varka, Element element)
    {
        if (element == Element.None || !VarkaPrototype.IsVarka(varka)) return;
        await VarkaOath.SetCurrent(choiceContext, varka, element, knight: false);
        await VarkaOath.Gain(choiceContext, varka, element, Oath);
    }
}

/// <summary>Uncommon. "Swirl every aura." Wall of Gales' sweep
/// (<see cref="VarkaRules.SwirlFreshAuras"/>), its Swirls paying his current
/// element and crediting no Oath.</summary>
public sealed class BottledGale : ArmPotion
{
    public override PotionRarity Rarity => PotionRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Bottled Gale"),
        ("description", "[gold]Swirl[/gold] every aura."),
    };

    protected override string ArtPath =>
        ArmPotions.Image("varka", "bottled_gale");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        using (VarkaOath.NoCredit(target!))
        {
            await VarkaRules.SwirlFreshAuras(choiceContext, target);
        }
    }
}

/// <summary>Rare. "This turn, your cards read your total Oath across all
/// four elements." Every read of his current element's Oath
/// (<see cref="VarkaOathLedger.CurrentOath"/>) answers the total until the
/// round ends; his badge shows it.</summary>
public sealed class ElixirOfTheFourWinds : ArmPotion
{
    public override PotionRarity Rarity => PotionRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Elixir of the Four Winds"),
        ("description",
            "This turn, your cards read your total [gold]Oath[/gold] across "
          + "all four elements."),
    };

    protected override string ArtPath =>
        ArmPotions.Image("varka", "elixir_of_the_four_winds");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        if (!Use(target)) return;
        await OathBadge.Sync(choiceContext, target!);
    }

    /// <summary>The effect: PURE on the ledger, so the tests run it.
    /// </summary>
    public static bool Use(Creature? varka)
    {
        if (!VarkaPrototype.IsVarka(varka)) return false;
        VarkaOathLedger.For(varka!).ReadAllFourThisTurn();
        return true;
    }
}

/// <summary>Varka's potion pool: his three, and nothing
/// borrowed unless the expansion paper's pick 1 rules (b)
/// (<see cref="VarkaArmRelics.KeepSilentBorrow"/>).</summary>
public sealed class VarkaPotionPool : PotionPoolModel
{
    public override string EnergyColorName => "silent";

    public override Color LabOutlineColor => new("4CC2A8");

    protected override IEnumerable<PotionModel> GenerateAllPotions()
    {
        IEnumerable<PotionModel> own = new PotionModel[]
        {
            ModelDb.Potion<BottledResolve>(),
            ModelDb.Potion<BottledGale>(),
            ModelDb.Potion<ElixirOfTheFourWinds>(),
        };
#pragma warning disable CS0162 // pick 1(b) is one constant away
        if (VarkaArmRelics.KeepSilentBorrow)
        {
            own = own.Concat(ModelDb.PotionPool<SilentPotionPool>().AllPotions);
        }
#pragma warning restore CS0162
        return own;
    }
}
