using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI REVIEW, ROUND 8 (2026-10-14,
/// <c>review/active/kokomi-review-r8-2026-10-14.md</c>, items 1 to 12;
/// Claude's, Kokomi at Prototype). The mod's halves: five cards that pay
/// Block now, Mend's "(N will land)" read at format time, Sucrose's "(no
/// aura: no Swirl)", and a carry-out's receipt carrying the reactions its
/// hits set off. Sim and page twin:
/// <c>tier0/tests/test_kokomi_review_r8_2026_10_14.py</c>; the bridge's
/// row is <c>GitsPowerRowTests</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiReviewR8Tests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    private static (int, int) Vars<T>(string name)
        where T : CardModel, new() =>
        (new T().DynamicVars[name].IntValue,
         Upgraded<T>().DynamicVars[name].IntValue);

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static List<string> Calls(string type, string method) =>
        Il.Calls(Il.Method(type, method)).ToList();

    // ---- items 1-5 -------------------------------------------------------------

    [Fact]
    public void Shell_of_sanctuarys_slot_is_draft_the_orders()
    {
        // Shell of Sanctuary was cut by the Kokomi card paper v2 (2026-10-18,
        // sec.2 change 1); Draft the Orders is its Common slot, 5 [8] Block.
        Assert.Equal((5, 8), Vars<ProtoKkDraftTheOrders>("Block"));
        Assert.DoesNotContain(CardKeyword.Retain,
                              new ProtoKkDraftTheOrders().CanonicalKeywords);
        Assert.Contains(Calls("ProtoKkDraftTheOrders", "OnPlay"),
                        c => c.Contains("CreatureCmd.GainBlock"));
        Assert.DoesNotContain(Calls("ProtoKkDraftTheOrders", "OnPlay"),
                              c => c.Contains("CardPileCmd.Draw"));
    }

    [Fact]
    public void The_four_other_numbers()
    {
        Assert.Equal((6, 8), Vars<ProtoKkEveningWatch>("KkAmount"));
        Assert.Equal((8, 11), Vars<ProtoKkUndercurrentSnare>("Block"));
        Assert.Equal(4, new ProtoKkUndercurrentSnare().PlanClauses.Single().Amount);
        Assert.Equal((10, 13), Vars<ProtoKkSurgingShoal>("Damage"));
        Assert.Equal((10, 13), Vars<ProtoKkSurgingShoal>("Block"));
        Assert.Equal((8, 10), Vars<ProtoKkFeint>("Damage"));
        Assert.Equal(6, new ProtoKkFeint().PlanClauses.Single().Amount);
    }

    [Fact]
    public void Surging_shoal_attacks_all_and_blocks_with_no_plan()
    {
        var shoal = new ProtoKkSurgingShoal();
        Assert.IsNotAssignableFrom<IPlannedCard>(shoal);
        Assert.Equal("Deal {Damage:diff()} [gold]Hydro[/gold] damage to ALL "
                     + "enemies. Gain {Block:diff()} [gold]Block[/gold].",
                     Face(shoal));
        var play = Calls("ProtoKkSurgingShoal", "OnPlay");
        Assert.Contains(play, c => c.Contains("TargetingAllOpponents"));
        Assert.Contains(play, c => c.Contains("CreatureCmd.GainBlock"));
    }

    // ---- item 6 ------------------------------------------------------------------

    [Fact]
    public void Mend_lands_is_read_through_the_cap_at_format_time()
    {
        // A bare `{MendLands}` is formatted through ToString / IConvertible,
        // which read the printed number until this; both answer Live now.
        Assert.Contains(Calls("MendLandsVar", "GetBaseValueForIConvertible"),
                        c => c.Contains("MendLandsVar.get_Live"));
        var toString = typeof(MendLandsVar).GetMethod(
            nameof(ToString), Type.EmptyTypes)!;
        Assert.Equal(typeof(MendLandsVar), toString.DeclaringType);
        Assert.Contains(Il.Calls(toString),
                        c => c.Contains("MendLandsVar.get_Live"));
        Assert.Contains(Calls("MendLandsVar", "get_Live"),
                        c => c.Contains("KokomiRules.MendWouldLand"));
        // With no owner in a combat (a canonical card) the printed number.
        Assert.Equal("6", new ProtoKkTheMoonAShip()
            .DynamicVars[MendLandsVar.Token].ToString());
    }

    // ---- item 7 ------------------------------------------------------------------

    [Fact]
    public void Sucrose_says_when_there_is_no_aura_to_swirl()
    {
        Assert.Equal(" (no aura: no Swirl)", SwirlAuraFace.Words(false));
        Assert.Equal("", SwirlAuraFace.Words(true));
        Assert.Equal("", SwirlAuraFace.Line(new ProtoMcSucroseGust()));
        Assert.Contains("[gold]Swirl[/gold] the enemy{InCombat:{SwirlAura}|}.",
                        Face(new ProtoMcSucroseMollisFavonius()));
        foreach (var card in new CardModel[] { new ProtoMcSucroseGust(),
                                               new ProtoMcSucroseAstable() })
        {
            Assert.Contains("[gold]Swirl[/gold] ALL enemies{InCombat:{SwirlAura}|}.",
                            Face(card));
        }
        foreach (var type in new[] { "ProtoMcSucroseGust",
                                     "ProtoMcSucroseAstable",
                                     "ProtoMcSucroseMollisFavonius" })
        {
            Assert.Contains(Calls(type, "AddExtraArgsToDescription"),
                            c => c.Contains("SwirlAuraFace.Line"));
        }
    }

    // ---- item 9 ------------------------------------------------------------------

    [Fact]
    public void A_carry_outs_row_carries_the_reactions_its_hits_set_off()
    {
        Assert.Contains("reactions",
                        Il.Strings(Il.Method("KokomiPlan", "CarriedOutRow")));
        Assert.Contains(Calls("CompanionOverhaulReactions", "Note"),
                        c => c.Contains("KokomiPlan.NoteReaction"));
        Assert.Equal("Vaporize", KokomiPlan.ReactionName(Reaction.Vaporize));
        Assert.Equal("Electro-Charged",
                     KokomiPlan.ReactionName(Reaction.ElectroCharged));
        Assert.Equal("Overloaded", KokomiPlan.ReactionName(Reaction.Overload));
        // Outside a carry-out (no seat) it notes nothing and does not throw.
        KokomiPlan.NoteReaction(null, Reaction.Vaporize);
    }
}
