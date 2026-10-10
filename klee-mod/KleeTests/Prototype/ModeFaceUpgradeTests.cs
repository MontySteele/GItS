using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text.RegularExpressions;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Enchantments;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-805` (2026-10-04): A MODE FACE PRINTS THE PARENT'S NUMBERS, UPGRADED
/// AND NOT. Durin's Binary Form and Principle of Purity printed the sheet's
/// label on their chooser faces, so an upgraded card read 8 in the hand and 6
/// in the chooser, and every numbered mode title carried a literal the body
/// under it could disagree with.
///
/// The faces are rendered here the two ways the game renders them that a
/// headless suite can reach: an <c>{IfUpgraded:show:a|b}</c> swap read off
/// <c>IsUpgraded</c>, and a <c>{Var}</c> / <c>{Var:diff()}</c> token read off
/// the card's own <c>DynamicVars</c>. The board fold needs a live combat and
/// is <c>ModalChoice.CreateMatchingOption</c>'s to pin; the upgrade is applied
/// here the way that method applies it, <c>UpgradeInternal</c> on the option
/// when the parent is upgraded.
/// </summary>
public class ModeFaceUpgradeTests
{
    private static readonly Regex UpgradeSwap =
        new(@"\{IfUpgraded:show:([^{}|]*)\|([^{}|]*)\}");

    private static readonly Regex VarToken = new(@"\{(\w+)(?::diff\(\))?\}");

    private static T Upgraded<T>(T card) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    private static string Raw(CardModel card, string key) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == key).Item2;

    /// <summary>The face with its upgrade swaps and var tokens resolved.</summary>
    private static string Render(CardModel card)
    {
        var text = UpgradeSwap.Replace(Raw(card, "description"),
            m => card.IsUpgraded ? m.Groups[1].Value : m.Groups[2].Value);
        return VarToken.Replace(text, m =>
            card.DynamicVars.TryGetValue(m.Groups[1].Value, out var v)
                ? ((int)v.BaseValue).ToString(CultureInfo.InvariantCulture)
                : m.Value);
    }

    /// <summary>Every generated mode face, paired with its parent card.</summary>
    public static IEnumerable<object[]> GeneratedModes()
    {
        var types = typeof(ModalOptionCard).Assembly.GetTypes();
        foreach (var option in types.Where(t =>
                     typeof(ModalOptionCard).IsAssignableFrom(t) && !t.IsAbstract
                     && t.Namespace == typeof(ProtoFsCurtainRise).Namespace))
        {
            var cut = option.Name.LastIndexOf("Mode", StringComparison.Ordinal);
            var parent = types.Single(t => t.Namespace == option.Namespace
                                           && t.Name == option.Name[..cut]);
            yield return new object[] { parent, option };
        }
    }

    [Theory]
    [MemberData(nameof(GeneratedModes))]
    public void A_mode_face_prints_its_parents_number_upgraded_or_not(
        Type parentType, Type optionType)
    {
        foreach (var upgraded in new[] { false, true })
        {
            var parent = (CardModel)Activator.CreateInstance(parentType)!;
            var option = (CardModel)Activator.CreateInstance(optionType)!;
            if (upgraded)
            {
                Upgraded(parent);
                Upgraded(option);
            }
            var face = Render(option);
            Assert.DoesNotContain("{", face);
            var parentFace = Render(parent);
            if (!parentFace.Contains(face) && parentFace.Contains(": also "))
            {
                // The Salon's Tab seat round (2026-10-05): an "also" mode
                // prints its whole label, so it says it draws too. Its
                // numbers are still the parent's.
                foreach (Match n in Regex.Matches(face, @"\d+"))
                {
                    Assert.Contains(n.Value, parentFace);
                }
                continue;
            }
            Assert.Contains(face, parentFace);
        }
    }

    [Fact]
    public void Curtain_rise_modes_read_the_upgraded_numbers()
    {
        Assert.Equal("Deal 7 damage", Render(new ProtoFsCurtainRiseModeA()));
        Assert.Equal("Deal 10 damage",
                     Render(Upgraded(new ProtoFsCurtainRiseModeA())));
        Assert.Equal("[gold]Drain[/gold] 3: deal 12 instead",
                     Render(new ProtoFsCurtainRiseModeB()));
        Assert.Equal("[gold]Drain[/gold] 3: deal 16 instead",
                     Render(Upgraded(new ProtoFsCurtainRiseModeB())));
    }

    /// <summary>Hang a real enchantment on a card, uninitialised, the way
    /// <c>EnchantedRiderTests.Enchant</c> does (its constructor registers with
    /// the game's model tables), and mutable, as one on a deck card is.</summary>
    private static T Enchant<T>(CardModel card, int amount)
        where T : EnchantmentModel
    {
        var enchantment = (T)RuntimeHelpers.GetUninitializedObject(typeof(T));
        typeof(EnchantmentModel)
            .GetField("_amount", HeadlessGame.All)!
            .SetValue(enchantment, amount);
        Seat.Set(enchantment, "IsMutable", true);
        Seat.Set(enchantment, "Card", card);
        Seat.Set(card, "Enchantment", enchantment);
        return enchantment;
    }

    private static decimal Face(CardModel card, string var)
    {
        var v = card.DynamicVars[var];
        v.UpdateCardPreview(card, CardPreviewMode.Normal, null,
                            runGlobalHooks: false);
        return v.PreviewValue;
    }

    [Fact]
    public void A_mode_face_carries_the_parents_enchantment()
    {
        // The Furina full-run seat round (2026-10-10): a Sharp Curtain Rise
        // read 16 in the chooser and hit for 18; an Instinct one read 11 and
        // hit for 22. The face now folds what the hit folds.
        var parent = new ProtoFsCurtainRise();
        Seat.Set(parent, "IsMutable", true);
        var sharp = Enchant<Sharp>(parent, 2);
        var option = new ProtoFsCurtainRiseModeB();
        Seat.Set(option, "IsMutable", true);

        ModalChoice.CarryEnchantment(option, parent);

        Assert.IsType<Sharp>(option.Enchantment);
        // A copy, not the parent's own: the parent's stays on the parent.
        Assert.NotSame(sharp, option.Enchantment);
        Assert.Same(parent, sharp.Card);
        Assert.Same(option, option.Enchantment!.Card);
        Assert.Equal(2, option.Enchantment.Amount);
        Assert.Equal(14m, Face(option, "BranchDamage"));

        var instinctParent = new ProtoFsCurtainRise();
        Seat.Set(instinctParent, "IsMutable", true);
        Enchant<Instinct>(instinctParent, 1);
        var instinctOption = new ProtoFsCurtainRiseModeA();
        Seat.Set(instinctOption, "IsMutable", true);
        ModalChoice.CarryEnchantment(instinctOption, instinctParent);
        Assert.Equal(14m, Face(instinctOption, "PlainDamage"));
    }

    [Fact]
    public void An_unenchanted_parent_leaves_the_face_bare()
    {
        var parent = new ProtoFsCurtainRise();
        var option = new ProtoFsCurtainRiseModeB();
        Seat.Set(option, "IsMutable", true);
        ModalChoice.CarryEnchantment(option, parent);
        ModalChoice.CarryEnchantment(option, null);
        Assert.Null(option.Enchantment);
    }

    [Fact]
    public void Binary_form_modes_read_the_upgraded_numbers_under_a_numberless_title()
    {
        Assert.Equal("[gold]White[/gold]: Deal 6 [gold]Pyro[/gold] damage to ALL enemies",
                     Render(new ProtoMcDurinBinaryFormModeA()));
        Assert.Equal("[gold]White[/gold]: Deal 8 [gold]Pyro[/gold] damage to ALL enemies",
                     Render(Upgraded(new ProtoMcDurinBinaryFormModeA())));
        Assert.Equal("[gold]Dark[/gold]: Deal 5 [gold]Pyro[/gold] damage to an enemy 3 times",
                     Render(Upgraded(new ProtoMcDurinBinaryFormModeB())));
        Assert.Equal("White", Raw(new ProtoMcDurinBinaryFormModeA(), "title"));
        Assert.Equal("Dark", Raw(new ProtoMcDurinBinaryFormModeB(), "title"));
    }

    [Fact]
    public void Principle_of_purity_modes_read_the_upgraded_numbers()
    {
        Assert.Contains("75% more",
                        Render(Upgraded(new ProtoMcDurinPrincipleOfPurityModeA())));
        // The text pass of 2026-10-08: rule 8's "N additional damage".
        Assert.Contains("deal 6 additional damage",
                        Render(Upgraded(new ProtoMcDurinPrincipleOfPurityModeB())));
    }
}
