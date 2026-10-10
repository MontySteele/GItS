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
/// The null-target preview sweep (2026-10-10, after #1037's High Stakes fix).
/// A card in the hand previews its damage with no target, so a damage hook
/// that answers 0 on <c>target == null</c> drops its bonus from the face
/// while the hit, which names a target, still gets it. Strength asks for no
/// target. A bonus that is the dealer's own now asks for none either:
/// Neuvillette's Hydro line on Furina's badge and Varka's Stormward Stance.
///
/// A bonus that reads the TARGET (an aura, a debuff count) keeps its gate,
/// since a hand card has no enemy to read: Night Vigil (the target's aura)
/// and Ceremonial Garment (the target's debuffs). Pinned below so the
/// difference is deliberate.
///
/// These pins run the game's own preview on a real card in the owner's real
/// Hand pile (the harness of <see cref="FurinaSpendAllPreviewWeakTests"/>).
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class NullTargetPreviewGateTests
{
    private static decimal PreviewDamage(CardModel card, Creature? target)
    {
        var var = card.DynamicVars.Damage;
        var.UpdateCardPreview(card, CardPreviewMode.Normal, target,
                              runGlobalHooks: true);
        return var.PreviewValue;
    }

    [Fact]
    public void Hydro_lance_in_hand_previews_neuvillettes_hydro_line()
    {
        InCombat(() =>
        {
            var b = Build(new ProtoFsHydroLance(),
                          f => f.WithPower<FanfarePower>(1));
            var formula = b.Card.DynamicVars.CalculatedDamage.Calculate(null);
            Assert.Equal(formula, Preview(b.Card, null, inHand: true));

            FurinaStageLedger.For(b.Furina.Creature)
                .Seat(StagePerformer.Neuvillette);
            var line = FurinaStageLaw.NeuvilletteHydroBonus;

            Assert.Equal(formula + line, Preview(b.Card, null, inHand: true));
            Assert.Equal(formula + line,
                         Preview(b.Card, b.Enemy, inHand: true));
            Assert.Equal(HitOrder.Compose(b.Furina.Creature, null, formula,
                                          ValueProp.Move, b.Card),
                         formula + line);
        });
    }

    [Fact]
    public void Crosswind_in_hand_previews_stormward_stance()
    {
        InCombat(() =>
        {
            var b = Build(new ProtoVkCrosswind(),
                          v => v.WithPower<StormwardStancePower>(3),
                          owner: () => Seat.Varka());
            var printed = b.Card.DynamicVars.Damage.BaseValue;

            Assert.Equal(printed + 3, PreviewDamage(b.Card, null));
            Assert.Equal(printed + 3, PreviewDamage(b.Card, b.Enemy));
            Assert.Equal(HitOrder.Compose(b.Furina.Creature, null, printed,
                                          ValueProp.Move, b.Card),
                         printed + 3);
        });
    }

    [Fact]
    public void Stormward_stance_still_refuses_a_skill_an_unpowered_hit_and_his_own_body()
    {
        var varka = Seat.Varka().WithPower<StormwardStancePower>(3);
        var enemy = Seat.Klee().Creature;
        var stance = varka.Creature.Powers.OfType<StormwardStancePower>().Single();
        var me = varka.Creature;
        var attack = new ProtoVkCrosswind();

        Assert.Equal(3m, stance.ModifyDamageAdditive(
            null, 8m, ValueProp.Move, me, attack, null));
        Assert.Equal(0m, stance.ModifyDamageAdditive(
            null, 8m, ValueProp.Unpowered, me, attack, null));
        Assert.Equal(0m, stance.ModifyDamageAdditive(
            enemy, 8m, ValueProp.Move, me, null, null));
        Assert.Equal(0m, stance.ModifyDamageAdditive(
            me, 8m, ValueProp.Move, me, attack, null));
        Assert.Equal(0m, stance.ModifyDamageAdditive(
            null, 8m, ValueProp.Move, enemy, attack, null));
    }

    [Fact]
    public void Target_reading_bonuses_keep_their_null_target_gate()
    {
        var klee = Seat.Klee()
            .WithPower<NightVigilPower>(4)
            .WithPower<ProtoCeremonialGarmentPower>(2);
        var me = klee.Creature;
        var attack = new ProtoVkCrosswind();

        var vigil = me.Powers.OfType<NightVigilPower>().Single();
        var garment = me.Powers.OfType<ProtoCeremonialGarmentPower>().Single();
        Assert.Equal(0m, vigil.ModifyDamageAdditive(
            null, 8m, ValueProp.Move, me, attack, null));
        Assert.Equal(0m, garment.ModifyDamageAdditive(
            null, 8m, ValueProp.Move, me, attack, null));
    }
}
