#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Cards.Varka;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE VARKA REVIEW (review/ruled/varka-review-2026-10-12.md, ruled
/// 2026-10-12: "Both sound workable to me - Dandelion Gale could be the
/// Replace version"). His two Ancients and their doors, the switch preview,
/// and the card numbers the review moved. What awaits a live combat (the hit,
/// the Swirl) is pinned by its doors, on <c>VarkaRelicsPotionsTests</c>' terms.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaAncientsTests : IDisposable
{
    public VarkaAncientsTests()
    {
        HeadlessGame.Arm();
        VarkaOathLedger.ResetAll();
    }

    public void Dispose()
    {
        VarkaOathLedger.ResetAll();
    }

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static int UpgradedCost<T>() where T : CardModel, new() =>
        Upgraded<T>().EnergyCost.GetWithModifiers(CostModifiers.None);

    /// <summary>The type argument of every <c>ModelDb.Card&lt;T&gt;()</c> call
    /// in the body, read off its IL (<c>ArmPools</c>' scan).</summary>
    private static List<Type> CardTypesCalled(System.Reflection.MethodBase method)
    {
        var found = new List<Type>();
        var il = method.GetMethodBody()?.GetILAsByteArray() ?? Array.Empty<byte>();
        for (var i = 0; i < il.Length - 4; i++)
        {
            if (il[i] != 0x28) continue; // call
            try
            {
                var target = method.Module.ResolveMethod(BitConverter.ToInt32(il, i + 1));
                if (target is { IsGenericMethod: true, Name: "Card" })
                {
                    found.AddRange(target.GetGenericArguments());
                }
            }
            catch
            {
                // Not a method token.
            }
        }
        return found;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    // ==== All Four Winds =====================================================

    [Fact]
    public void All_four_winds_is_a_3_cost_ancient_power_costing_2_upgraded()
    {
        var card = new AllFourWinds();
        Assert.Equal(CardRarity.Ancient, card.Rarity);
        Assert.Equal(CardType.Power, card.Type);
        Assert.Equal(3, card.EnergyCost.Canonical);
        Assert.Equal(2, (int)Upgraded<AllFourWinds>().EnergyCost
            .GetWithModifiers(MegaCrit.Sts2.Core.Entities.Cards.CostModifiers.None));
        Assert.Equal("Your cards read your [gold]Oath[/gold] of every element "
                   + "together.", Face(card));
        var play = Il.Calls(Il.Method("AllFourWinds", "OnPlay"));
        Assert.Contains("VarkaOathLedger.ReadAllFourThisCombat", play);
        Assert.Contains(Il.CallSequence(Il.Method("AllFourWinds", "OnPlay")),
                        c => c.Contains("AllFourWindsPower"));
    }

    [Fact]
    public void All_four_winds_reads_all_four_for_the_whole_combat()
    {
        var varka = Seat.Varka().Creature;
        var ledger = VarkaOathLedger.For(varka);
        ledger.Add(Element.Hydro, 3);
        ledger.Add(Element.Pyro, 2);
        ledger.Add(Element.Cryo, 1);
        ledger.SetCurrent(Element.Hydro);
        Assert.Equal(3, VarkaOath.CurrentOath(varka));

        ledger.ReadAllFourThisCombat();
        Assert.True(ledger.ReadsAllFour);
        Assert.Equal(6, VarkaOath.CurrentOath(varka));
        // Unlike the Elixir, the next round keeps it.
        var round = (int)typeof(VarkaOathLedger)
            .GetField("_round", HeadlessGame.All)!.GetValue(ledger)!;
        ledger.RollTo(round + 1);
        Assert.False(ledger.AllFourThisTurn);
        Assert.True(ledger.AllFourThisCombat);
        Assert.Equal(6, ledger.CurrentOath);
        // Nothing moved: the four counts stand.
        Assert.Equal(3, ledger.Oath(Element.Hydro));
    }

    // ==== Dandelion Gale =====================================================

    [Fact]
    public void Dandelion_gale_is_the_ascension_on_all_enemies_2_cost_1_upgraded()
    {
        // The Archaic Tooth redesign (2026-10-13): "the ancient starts at 2,
        // and upgrading it at a campfire (or replacing an already-upgraded
        // Ascension) takes it to 1."
        var card = new DandelionGale();
        Assert.Equal(CardRarity.Ancient, card.Rarity);
        Assert.Equal(CardType.Attack, card.Type);
        Assert.Equal(2, card.EnergyCost.Canonical);
        Assert.Equal(1, UpgradedCost<DandelionGale>());
        Assert.Equal(TargetType.AllEnemies, card.TargetType);
        Assert.Contains(CardKeyword.Retain, card.CanonicalKeywords);
        Assert.Equal(Element.Anemo, ((IElementalCard)card).Element);
        Assert.Equal(10m, card.DynamicVars.Damage.BaseValue);
        Assert.Equal(3m, card.DynamicVars["VkPer"].BaseValue);
        // The upgrade is the cost only.
        Assert.Equal(10m, Upgraded<DandelionGale>().DynamicVars.Damage.BaseValue);
        Assert.Equal(3m, Upgraded<DandelionGale>().DynamicVars["VkPer"].BaseValue);
        Assert.Contains(card.DynamicVars.Values, v => v is VarkaCurrentElementHitVar);
        Assert.Equal(
            "Deal {Damage:diff()} [gold]Anemo[/gold] damage to ALL enemies. "
          + "Then deal {VkPer:diff()} damage per [gold]Oath[/gold] of your "
          + "[gold]current element[/gold] to each, as that element."
          + "{InCombat:\n(Deals {VkHit:diff()} damage)|}",
            Face(card));
        // The Anemo hit on ALL, then the current-element hit on ALL.
        var play = Il.CallSequence(Il.Method("DandelionGale", "OnPlay")).ToList();
        var hit = play.FindIndex(c => c.Contains("Execute"));
        Assert.True(hit >= 0 && play.IndexOf("VarkaCards.GaleHit") > hit);
        var gale = Il.CallSequence(Il.Method("VarkaCards", "GaleHit")).ToList();
        Assert.Contains("VarkaOath.NoApplyCredit", gale);
        Assert.Contains(gale, c => c.Contains("TargetingAllOpponents"));
    }

    [Fact]
    public void The_archaic_tooth_turns_four_winds_ascension_into_dandelion_gale()
    {
        Assert.IsAssignableFrom<ITranscendenceCard>(new ProtoVkFourWindsAscension());
        var made = Il.Method("ProtoVkFourWindsAscension",
                             "GetTranscendenceTransformedCard");
        Assert.Equal(typeof(CardModel), ((System.Reflection.MethodInfo)made).ReturnType);
        Assert.Contains(typeof(DandelionGale), CardTypesCalled(made));
    }

    // ==== the doors ==========================================================

    [Fact]
    public void His_ancients_are_in_the_ledger_the_offer_and_the_pool()
    {
        var ledger = Il.CallSequence(
                typeof(RosterAncientCards).GetProperty("Varka")!.GetGetMethod()!)
            .Where(c => c.StartsWith("ModelDb.Card<", StringComparison.Ordinal))
            .ToList();
        Assert.Equal(new[] { "ModelDb.Card<AllFourWinds>",
                             "ModelDb.Card<DandelionGale>" }, ledger);
        Assert.Contains("RosterAncientCards.get_Varka",
                        Il.Calls(Il.Method("VarkaRoster", "OfferablePool")));
        Assert.Contains("VarkaRoster.OfferablePool",
                        Il.Calls(Il.Method("VarkaCardPool", "FilterThroughEpochs")));
        Assert.Contains("RosterAncientCards.get_Varka",
                        Il.Calls(Il.Method("VarkaCardPool", "GenerateAllCards")));
        // Four Winds' Ascension is no longer the Tome's stand-in.
        Assert.False(new ProtoVkFourWindsAscension() is ITomeCard);
    }

    // ==== the switch preview ================================================

    [Fact]
    public void The_switch_line_names_the_element_and_is_empty_off_a_fight()
    {
        Assert.Equal("\n(Makes Pyro current)", VarkaOath.SwitchWords(Element.Pyro));
        Assert.Equal("", VarkaOath.SwitchLine(null, Element.Pyro));
        Assert.Equal("", VarkaOath.SwitchLine(new ProtoVkKindledEdge(), Element.Pyro));
        Assert.Contains("VarkaOath.WouldSwitchTo",
                        Il.Calls(Il.Method("VarkaOath", "SwitchLine")));
    }

    [Fact]
    public void A_card_that_switches_ends_its_face_in_the_line()
    {
        // A non-Knight (Kindled Edge) and a Knight (Amber) both carry it.
        foreach (var card in new CardModel[]
                 { new ProtoVkKindledEdge(), new ProtoVkAmberFieryRain() })
        {
            // BACKLOG: a Pyro card's Wildfire Oath line follows it.
            Assert.EndsWith("{InCombat:{VarkaSwitch}|}{InCombat:{VarkaWildfire}|}",
                            Face(card));
        }
        // A face that prints the switch (Stoke the Flames) carries none.
        var stoke = Face(new ProtoVkStokeTheFlames());
        Assert.StartsWith("[gold]Pyro[/gold] becomes your [gold]current element[/gold].",
                          stoke);
        Assert.DoesNotContain("VarkaSwitch", stoke);
        // An Anemo card switches nothing.
        Assert.DoesNotContain("VarkaSwitch", Face(new ProtoVkWindboundExecution()));
    }

    // ==== the numbers the review moved =======================================

    [Fact]
    public void Ember_cleave_deals_9_and_11_upgraded()
    {
        Assert.Equal(9m, new ProtoVkEmberCleave().DynamicVars["VkBase"].BaseValue);
        Assert.Equal(11m, Upgraded<ProtoVkEmberCleave>().DynamicVars["VkBase"].BaseValue);
    }
}
