using System.Runtime.CompilerServices;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Enchantments;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// Seat 2026-10-19, Yae lane 2: "Sakura Seal+ on a Strike changed it from
/// 'Deal 9' to 'Deal 6' -- it seems to have overwritten the Soup's Ember
/// bonus." A card has one Enchantment slot, and the Edit cleared whatever
/// sat in it. Now a card wearing any Enchantment that is not a Masterpiece
/// is never Edited, and the Edit never clears it.
/// </summary>
public class YaeEditKeepsEnchantmentTests
{
    private static T Mutable<T>(T card) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        return card;
    }

    private static T Wear<T>(CardModel card, T enchantment) where T : EnchantmentModel
    {
        Seat.Set(enchantment, "IsMutable", true);
        Seat.Set(enchantment, "Card", card);
        Seat.Set(card, "Enchantment", enchantment);
        return enchantment;
    }

    private static Sharp BaseEnchantment(CardModel card)
    {
        var sharp = (Sharp)RuntimeHelpers.GetUninitializedObject(typeof(Sharp));
        typeof(EnchantmentModel).GetField("_amount", HeadlessGame.All)!
            .SetValue(sharp, 3);
        return Wear(card, sharp);
    }

    [Fact]
    public void A_card_wearing_a_base_enchantment_is_never_edited()
    {
        var editor = Mutable(new ProtoYmFoxfireLure());
        var souped = Mutable(new StrikeIronclad());
        var sharp = BaseEnchantment(souped);

        Assert.True(YaeEditing.WearsOtherEnchantment(souped));
        Assert.False(YaeEditing.CanWear(souped));
        Assert.False(YaeEditing.Editable(souped, editor));
        foreach (var a in YaeAnnotationText.All)
        {
            Assert.False(YaeEditing.EditReaches(souped, editor, a), a.ToString());
        }
        Assert.False(YaeEditing.PublishReaches(souped, editor));

        // An Edit attempt (and a Publish, and a bare Clear) leaves it on.
        Assert.False(YaeEditing.Annotate(souped, YaeAnnotation.SakuraSeal, recordDraft: false));
        Assert.False(YaeEditing.PublishToDeck(souped, YaeAnnotation.RedInk));
        YaeEditing.Clear(souped);
        Assert.Same(sharp, souped.Enchantment);
        Assert.Equal(3, souped.Enchantment!.Amount);
    }

    [Fact]
    public void A_plain_card_or_a_masterpiece_still_edits()
    {
        var editor = Mutable(new ProtoYmFoxfireLure());
        var plain = Mutable(new StrikeIronclad());
        Assert.False(YaeEditing.WearsOtherEnchantment(plain));
        Assert.True(YaeEditing.CanWear(plain));
        Assert.True(YaeEditing.EditReaches(plain, editor, YaeAnnotation.RedInk));

        var annotated = Mutable(new StrikeIronclad());
        Wear(annotated, new YaeMasterpiece());
        Assert.False(YaeEditing.WearsOtherEnchantment(annotated));
        Assert.True(YaeEditing.CanWear(annotated));
        Assert.True(YaeEditing.EditReaches(annotated, editor, YaeAnnotation.RedInk));
    }
}
