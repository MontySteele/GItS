using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;
using static KleeMod.Tests.Prototype.FurinaSpendAllPreviewWeakTests;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The null-target preview sweep (2026-10-10, after #1037's High Stakes fix),
/// the companion half: Durin's Principle of Purity, Dark ("Your Pyro damage
/// deals 4 [6] more"). A card in the hand previews with no target, and the
/// hook answered 0 on <c>target == null</c>, so the bonus was missing from
/// the face while the hit got it. The bonus is the owner's, so it asks for no
/// target, as Strength does. Runs the game's own preview on a real card in
/// the owner's real Hand pile (the harness of
/// <see cref="FurinaSpendAllPreviewWeakTests"/>).
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class PurityDarkPreviewTests
{
    private static decimal PreviewDamage(CardModel card, Creature? target)
    {
        var var = card.DynamicVars.Damage;
        var.UpdateCardPreview(card, CardPreviewMode.Normal, target,
                              runGlobalHooks: true);
        return var.PreviewValue;
    }

    [Fact]
    public void Explosive_spark_in_hand_previews_purity_dark()
    {
        InCombat(() =>
        {
            var b = Build(new ProtoKoExplosiveSpark(),
                          k => k.WithPower<PurityDarkPower>(4),
                          owner: () => Seat.Klee());
            var printed = b.Card.DynamicVars.Damage.BaseValue;

            Assert.Equal(printed + 4, PreviewDamage(b.Card, null));
            Assert.Equal(printed + 4, PreviewDamage(b.Card, b.Enemy));
            Assert.Equal(HitOrder.Compose(b.Furina.Creature, null, printed,
                                          ValueProp.Move, b.Card),
                         printed + 4);
        });
    }

    [Fact]
    public void Purity_dark_still_refuses_other_elements_unpowered_hits_and_its_owner()
    {
        var klee = Seat.Klee().WithPower<PurityDarkPower>(4);
        var enemy = Seat.Varka().Creature;
        var dark = klee.Creature.Powers.OfType<PurityDarkPower>().Single();
        var me = klee.Creature;
        var pyro = new ProtoKoExplosiveSpark();

        Assert.Equal(4m, dark.ModifyDamageAdditive(
            null, 12m, ValueProp.Move, me, pyro, null));
        Assert.Equal(0m, dark.ModifyDamageAdditive(
            null, 8m, ValueProp.Move, me, new ProtoVkCrosswind(), null));
        Assert.Equal(0m, dark.ModifyDamageAdditive(
            null, 12m, ValueProp.Unpowered, me, pyro, null));
        Assert.Equal(0m, dark.ModifyDamageAdditive(
            enemy, 12m, ValueProp.Move, me, null, null));
        Assert.Equal(0m, dark.ModifyDamageAdditive(
            me, 12m, ValueProp.Move, me, pyro, null));
        Assert.Equal(0m, dark.ModifyDamageAdditive(
            null, 12m, ValueProp.Move, enemy, pyro, null));
    }
}
