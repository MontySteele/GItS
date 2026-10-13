using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Kokomi;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// R276, Kokomi's two non-card changes.
///
/// PICK 2 IS RETIRED AS A RULE (2026-10-05). It made every damaging card in
/// Kokomi's hand apply Hydro, Skills included; [USER] ruled that a legacy
/// design -- the element "just lives in the card pool as a symbol on relevant
/// elemental cards". Her two damaging Skills that print Hydro (Opening Gambit,
/// Second Wave) now declare it on the sheet, and a card that declares nothing
/// applies nothing in her hand. Sim twin: <c>tier0/tests/test_kokomi_plan.py</c>.
///
/// (Her Ancient, Princess of Watatsumi, is the Archaic Tooth's Plan card since
/// the Ancient audit, 2026-10-12: <c>AncientAuditTests</c>.)
///
/// THE COLLECTION IS LOAD-BEARING: both arm switches are one static apiece.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiR276Tests
{
    // ---- pick 2, now on the card ---------------------------------------------

    [Fact]
    public void Her_damaging_skills_declare_hydro()
    {
        // Each prints "Deal 7 [gold]Hydro[/gold] damage" and declares it on
        // the sheet (`applies_element: true`), so the codegen puts
        // IElementalCard and the gem on the card itself.
        foreach (var card in new CardModel[]
                 {
                     new ProtoKkOpeningGambit(),
                     new ProtoKkSecondWave(),
                 })
        {
            Assert.Equal(MegaCrit.Sts2.Core.Entities.Cards.CardType.Skill,
                         card.Type);
            var elemental = Assert.IsAssignableFrom<IElementalCard>(card);
            Assert.Equal(Element.Hydro, elemental.Element);
        }
    }

    [Fact]
    public void A_no_element_mod_damage_card_played_by_kokomi_applies_nothing()
    {
        // [USER], 2026-10-05: "I think that that Kokomi effect is a legacy
        // design." Furina's Headliner is a mod-authored Attack that
        // deals damage and names no element -- no IElementalCard, no carried
        // hit, no gem. In Kokomi's hand it used to apply her Hydro; it applies
        // nothing, in hers or anyone's. Before this change the funnel's
        // character fallback answered Hydro here.
        try
        {
            var cheered = new ProtoFsHeadliner();
            Assert.Equal(CardType.Attack, cheered.Type);
            Assert.IsNotAssignableFrom<IElementalCard>(cheered);
            Assert.Equal(Element.None,
                AuraCmd.ElementOfPlay(cheered, Seat.Kokomi().Creature));
            Assert.Equal(Element.None,
                AuraCmd.ElementOfPlay(cheered, Seat.Klee().Creature));

            // Her own Skill that declares nothing (War Council's face-up half
            // is a debuff) applies nothing in her hand either.
            var council = new ProtoKkWarCouncil();
            Assert.IsNotAssignableFrom<IElementalCard>(council);
            Assert.Equal(Element.None,
                AuraCmd.ElementOfPlay(council, Seat.Kokomi().Creature));
        }
        finally
        {
        }
    }

    // ---- pick 1: the halves rewrite's five new Plan clauses -----------------

    [Fact]
    public void The_new_clauses_resolve_through_their_own_seams()
    {
        var resolve = Il.CallSequence(Il.Method("KokomiPlan", "ResolveOne"));
        Assert.Contains(resolve, c => c.Contains("KokomiOverhaulKit.FirstAttackTwice"));
        // Kokomi round-3 changes (2026-10-12): the largest intent, which
        // asks each enemy's `IntendedDamage`.
        Assert.Contains(resolve, c => c.Contains("KokomiOverhaulKit.MostIntendedDamage"));
        Assert.Contains(Il.Calls(Il.Method("KokomiOverhaulKit", "MostIntendedDamage")),
                        c => c.Contains("KokomiOverhaulKit.IntendedDamage"));
    }

    [Fact]
    public void Pincers_switch_skips_a_write_and_ends_with_the_turn()
    {
        Assert.Contains(
            Il.Calls(Il.Method("FirstAttackTwicePower", "ModifyCardPlayCount")),
            c => c.Contains("BakeKuragePet.Is"));
        var spent = Il.Calls(Il.Method("FirstAttackTwicePower",
                                       "AfterCardPlayed"));
        Assert.Contains(spent, c => c.Contains("KokomiPlan.PlayedOnPet"));
        Assert.Contains(spent, c => c.Contains("PowerCmd.Remove"));
        Assert.Contains(Il.Calls(Il.Method("FirstAttackTwicePower",
                                           "AfterSideTurnEnd")),
                        c => c.Contains("PowerCmd.Remove"));
    }

    [Fact]
    public void Tide_walls_intent_read_is_null_safe()
    {
        Assert.Equal(0, KokomiOverhaulKit.IntendedDamage(null, null));
        Assert.Contains(
            Il.Calls(Il.Method("KokomiOverhaulKit", "IntendedDamage")),
            c => c.Contains("AttackIntent.GetTotalDamage"));
    }
}
