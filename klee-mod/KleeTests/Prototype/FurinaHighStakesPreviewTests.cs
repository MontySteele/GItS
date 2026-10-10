using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;
using static KleeMod.Tests.Prototype.FurinaSpendAllPreviewWeakTests;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The Spend rounds review (<c>review/records/furina-spend-rounds-review-2026-10-10.md</c>,
/// "What changes" 2): "High Stakes shows in the card preview. Its damage gate
/// drops the bonus when the preview runs: Hydro Lance printed 15 and dealt
/// 18."
///
/// THE GATE THAT FAILED was <c>target == null</c>. On a Stage board a card
/// in her hand previews with no body (<see cref="FoldedPreview.Body"/>), so
/// the hook was asked with a null target and answered 0. The hit names its
/// target and got the bonus. Strength asks for no target; High Stakes now
/// asks for none either. These pins run the game's own preview on a real
/// card in her real Hand pile (the harness of
/// <see cref="FurinaSpendAllPreviewWeakTests"/>).
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class FurinaHighStakesPreviewTests
{
    /// <summary>12 HP drained this combat, over every 4: +3 a hit.</summary>
    private const int DrainedHp = 12;
    private const int Bonus = DrainedHp / FurinaStageLaw.HighStakesEvery;

    private static Board StakesBoard(CardModel card, bool inHand = true)
    {
        var b = Build(card,
                      f => f.WithPower<HighStakesPower>(
                          FurinaStageLaw.HighStakesEvery),
                      inHand: inHand);
        FurinaStageLedger.For(b.Furina.Creature).NoteDrain(DrainedHp, 66);
        return b;
    }

    [Fact]
    public void Hydro_lance_in_hand_previews_the_high_stakes_bonus()
    {
        InCombat(() =>
        {
            var b = StakesBoard(new ProtoFsHydroLance());
            var formula = b.Card.DynamicVars.CalculatedDamage.Calculate(null);

            var preview = Preview(b.Card, null, inHand: true);

            Assert.Equal(3, Bonus);
            Assert.Equal(formula + Bonus, preview);
            Assert.Equal(HitOrder.Compose(b.Furina.Creature, null, formula,
                                          ValueProp.Move, b.Card),
                         preview);
        });
    }

    [Fact]
    public void Bravura_in_hand_and_aimed_previews_the_same_bonus()
    {
        InCombat(() =>
        {
            var b = StakesBoard(new ProtoFsBravura());
            var formula = b.Card.DynamicVars.CalculatedDamage.Calculate(null);

            Assert.Equal(formula + Bonus, Preview(b.Card, null, inHand: true));
            Assert.Equal(formula + Bonus,
                         Preview(b.Card, b.Enemy, inHand: true));
        });
    }

    [Fact]
    public void The_hook_still_refuses_a_skill_an_unpowered_hit_and_her_own_body()
    {
        InCombat(() =>
        {
            var b = StakesBoard(new ProtoFsBravura());
            var stakes = Assert.Single(
                b.Furina.Creature.Powers.OfType<HighStakesPower>());
            var me = b.Furina.Creature;

            // The preview's call: no target, her Attack, a powered hit.
            Assert.Equal(Bonus, stakes.ModifyDamageAdditive(
                null, 6m, ValueProp.Move, me, b.Card, null));
            // Not a Skill's hit, not an unpowered one, not with no card.
            Assert.Equal(0m, stakes.ModifyDamageAdditive(
                null, 6m, ValueProp.Move, me, new ProtoFsOverdraft(), null));
            Assert.Equal(0m, stakes.ModifyDamageAdditive(
                null, 6m, ValueProp.Unpowered, me, b.Card, null));
            Assert.Equal(0m, stakes.ModifyDamageAdditive(
                b.Enemy, 6m, ValueProp.Move, me, null, null));
            // Not her own body, not someone else's hit.
            Assert.Equal(0m, stakes.ModifyDamageAdditive(
                me, 6m, ValueProp.Move, me, b.Card, null));
            Assert.Equal(0m, stakes.ModifyDamageAdditive(
                me, 6m, ValueProp.Move, b.Enemy, b.Card, null));
        });
    }

    [Fact]
    public void Off_her_hand_the_face_prints_the_formula()
    {
        InCombat(() =>
        {
            var b = StakesBoard(new ProtoFsBravura(), inHand: false);
            var formula = b.Card.DynamicVars.CalculatedDamage.Calculate(null);
            Assert.Equal(formula, Preview(b.Card, null, inHand: false));
        });
    }
}
