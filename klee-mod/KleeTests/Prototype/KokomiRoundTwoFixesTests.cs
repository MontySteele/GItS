using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI ROUND 2 (build 0.2.5212, 2026-10-13), the C# side: Grand Design's
/// gate counts exactly the cards the Bake-Kurage takes, and one card whose
/// read throws can no longer make a good hand read "no card in your hand can
/// be planned" (lane 3). Sim twin:
/// <c>tier0/tests/test_kokomi_round_2_fixes_2026_10_13.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiRoundTwoFixesTests
{
    private sealed class ThrowingPlanCard : CustomCardModel, IPlannedCard
    {
        public ThrowingPlanCard()
            : base(1, CardType.Skill, CardRarity.Common, TargetType.Self,
                   autoAdd: false)
        {
        }

        public IReadOnlyList<KokomiPlan.Planned> PlanClauses =>
            throw new InvalidOperationException("probe");

        protected override Task OnPlay(
            PlayerChoiceContext choiceContext, CardPlay cardPlay)
            => Task.CompletedTask;
    }

    private static List<CardModel> Hand(Seat seat) =>
        (List<CardModel>)typeof(CardPile)
            .GetField("_cards", HeadlessGame.All)!
            .GetValue(PileType.Hand.GetPile(seat.Player)!)!;

    private static T Owned<T>(Seat seat, T card) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", seat.Player);
        return card;
    }

    private static bool IsPetSpelling(TargetType type) =>
        type == KokomiTargets.PetOrEnemy || type == KokomiTargets.PetOrAlly
        || type == KokomiTargets.PetOnly || type == KokomiTargets.PetOrSelf;

    /// <summary>Every card class in the mod, as printed and upgraded, in a
    /// Kokomi hand beside Grand Design: the gate answers yes exactly when
    /// the card's target on her includes the Bake-Kurage.</summary>
    [Fact]
    public void Grand_design_counts_exactly_what_the_bake_kurage_takes()
    {
        var types = typeof(KokomiRefounding).Assembly.GetTypes()
            .Where(t => typeof(CardModel).IsAssignableFrom(t) && !t.IsAbstract
                        && t.GetConstructor(Type.EmptyTypes) != null)
            .OrderBy(t => t.Name).ToList();
        var wrong = new List<string>();
        int checkedCards = 0, plannable = 0;
        foreach (var type in types)
        {
            foreach (var upgrade in new[] { false, true })
            {
                CardModel card;
                try { card = (CardModel)Activator.CreateInstance(type)!; }
                catch { continue; }
                var seat = Seat.Kokomi().WithCombatState();
                var gd = Owned(seat, new ProtoKkGrandDesign());
                Owned(seat, card);
                if (upgrade)
                {
                    try
                    {
                        typeof(CardModel)
                            .GetMethod("UpgradeInternal", HeadlessGame.All)!
                            .Invoke(card, null);
                    }
                    catch { continue; }
                }
                Hand(seat).Add(gd);
                Hand(seat).Add(card);
                // 2026-10-18 (ruled): and a Basic Attack or Skill with no
                // Plan line, which Grand Design plans as itself.
                bool takes = card is not ProtoKkGrandDesign
                             && (IsPetSpelling(card.TargetType)
                                 || (card.Rarity == CardRarity.Basic
                                     && card.Type is CardType.Attack
                                                  or CardType.Skill));
                if (KokomiRefounding.AnyToPlan(gd) != takes)
                    wrong.Add($"{type.Name}{(upgrade ? "+" : "")}");
                checkedCards++;
                if (takes) plannable++;
            }
        }
        Assert.Empty(wrong);
        Assert.True(checkedCards > 800, $"checked {checkedCards}");
        // 78 (both faces) since Kokomi review r9 pick 1 (a), 2026-10-15:
        // Companions with no Plan line left the Bake-Kurage's reach.
        Assert.True(plannable > 60, $"plannable {plannable}");
    }

    [Fact]
    public void A_throwing_card_does_not_empty_the_hand()
    {
        var seat = Seat.Kokomi().WithCombatState();
        var gd = Owned(seat, new ProtoKkGrandDesign());
        Hand(seat).Add(gd);
        Hand(seat).Add(Owned(seat, new ThrowingPlanCard()));
        Assert.False(KokomiRefounding.AnyToPlan(gd));
        Hand(seat).Add(Owned(seat, new ProtoKkSting()));
        Assert.True(KokomiRefounding.AnyToPlan(gd));
        Assert.Null(((IUnplayableReasonCard)gd).UnplayableReason);
    }
}
