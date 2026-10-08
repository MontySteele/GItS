using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// VARKA, THE COMBO PASS (<c>review/active/varka-combo-pass-2026-10-04.md</c>,
/// RULED 2026-10-04, all four picks): five generic Block cards out, Pyro's
/// Exhaust engine and Cryo's status payoffs in, Unwavering Banner reworded,
/// and section 1's card fixes. Arithmetic by value, live sites by their call
/// graph. The sim twin is <c>tier0/tests/test_varka_combo.py</c>.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaComboTests : IDisposable
{
    public VarkaComboTests()
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

    private static decimal Var(CardModel card, string name) =>
        card.DynamicVars[name].BaseValue;

    private static List<string> Calls(string type, string method) =>
        Il.Calls(Il.Method(type, method)).ToList();

    private static string Face(object model) =>
        ((ILocalizationProvider)model).Localization!
            .Single(l => l.Item1 == "description").Item2;

    // ---- the pool --------------------------------------------------------------

    [Fact]
    public void The_pool_stays_78_five_out_five_in()
    {
        var pool = Il.CallSequence(Il.Method("VarkaRoster", "Pool"))
            .Where(c => c.StartsWith("ModelDb.Card<", StringComparison.Ordinal))
            .ToList();
        Assert.Equal(78, pool.Count);
        foreach (var name in new[] { "ProtoVkStokeTheFlames", "ProtoVkEmberCleave",
                                     "ProtoVkShatter", "ProtoVkPyreOath",
                                     "ProtoVkDeepFreeze" })
        {
            Assert.Contains($"ModelDb.Card<{name}>", pool);
        }
        foreach (var gone in new[] { "ProtoVkGaleMantle", "ProtoVkWestWindShield",
                                     "ProtoVkKnightlyGuard", "ProtoVkTailwindGuard",
                                     "ProtoVkOathOfTheKnights" })
        {
            Assert.Null(typeof(ProtoVkShatter).Assembly.GetType(
                "KleeMod.Cards.Prototype.Generated." + gone));
        }
        Assert.Null(typeof(PyreOathPower).Assembly.GetType(
            "KleeMod.Powers.OathOfTheKnightsPower"));
        Assert.DoesNotContain(Calls("VarkaOath", "TurnStart"),
                              c => c.Contains("OathOfTheKnights"));
    }

    [Fact]
    public void The_new_cards_rarity_and_cost()
    {
        var rows = new (CardModel Card, CardType Type, CardRarity Rarity)[]
        {
            (new ProtoVkStokeTheFlames(), CardType.Skill, CardRarity.Common),
            (new ProtoVkEmberCleave(), CardType.Attack, CardRarity.Common),
            (new ProtoVkShatter(), CardType.Attack, CardRarity.Common),
            (new ProtoVkPyreOath(), CardType.Power, CardRarity.Uncommon),
            (new ProtoVkDeepFreeze(), CardType.Skill, CardRarity.Uncommon),
        };
        foreach (var (card, type, rarity) in rows)
        {
            Assert.Equal(type, card.Type);
            Assert.Equal(rarity, card.Rarity);
            Assert.Equal(1, card.EnergyCost.Canonical);
        }
    }

    // ---- sec.3: Pyro burns -------------------------------------------------------

    [Fact]
    public void Stoke_the_flames_exhausts_a_chosen_card_then_gains_pyro()
    {
        Assert.Equal(2m, Var(new ProtoVkStokeTheFlames(), "VkAmount"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkStokeTheFlames>(), "VkAmount"));
        var play = Calls("ProtoVkStokeTheFlames", "OnPlay");
        Assert.Contains("CardSelectCmd.FromHand", play);
        Assert.Contains("CardCmd.Exhaust", play);
        Assert.Contains("VarkaCards.GainPyroOath", play);
        // The 2026-10-05 seat round: gain, then "Pyro becomes your current
        // element", through the non-Knight path Unwavering Banner holds.
        var stoke = Calls("VarkaCards", "GainPyroOath");
        Assert.True(stoke.IndexOf("VarkaOath.Gain")
                    < stoke.IndexOf("VarkaOath.CardMakesCurrent"));
        var makes = Calls("VarkaOath", "CardMakesCurrent");
        Assert.Contains("VarkaOath.BannerHolds", makes);
        Assert.Contains("VarkaOath.SetCurrent", makes);
        // The text pass of 2026-10-08: rule 6 golds the element.
        Assert.Equal("[gold]Exhaust[/gold] a card. Gain {VkAmount:diff()} "
                     + "[gold]Pyro[/gold] [gold]Oath[/gold]. [gold]Pyro[/gold] "
                     + "becomes your [gold]current element[/gold].",
                     Face(new ProtoVkStokeTheFlames()));
    }

    [Fact]
    public void Ember_cleave_hits_9_pyro_then_exhausts()
    {
        Assert.Equal(9m, Var(new ProtoVkEmberCleave(), "VkBase"));
        Assert.Equal(12m, Var(Upgraded<ProtoVkEmberCleave>(), "VkBase"));
        var play = Calls("ProtoVkEmberCleave", "OnPlay");
        Assert.True(play.IndexOf("VarkaCards.PyroStrike")
                    < play.IndexOf("CardCmd.Exhaust"));
        Assert.Contains("VarkaCards.ElementHit", Calls("VarkaCards", "PyroStrike"));
    }

    [Fact]
    public void Pyre_oath_gains_pyro_on_every_exhaust()
    {
        Assert.Equal(PowerStackType.Counter, new PyreOathPower().StackType);
        Assert.Contains("VarkaOath.Gain",
                        Calls("PyreOathPower", "AfterCardExhausted"));
        Assert.DoesNotContain(CardKeyword.Innate,
                              new ProtoVkPyreOath().CanonicalKeywords);
        Assert.Contains(CardKeyword.Innate, Upgraded<ProtoVkPyreOath>().Keywords);
    }

    // ---- sec.4: Cryo shatters ----------------------------------------------------

    [Fact]
    public void Shatter_is_5_plus_2_per_stack_and_previews_it()
    {
        var card = new ProtoVkShatter();
        Assert.Equal(5m, Var(card, "VkBase"));
        Assert.Equal(2m, Var(card, "VkPer"));
        Assert.Equal(7m, Var(Upgraded<ProtoVkShatter>(), "VkBase"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkShatter>(), "VkPer"));
        Assert.Equal(5, VarkaCards.ShatterDamage(5m, 2m, 0));
        Assert.Equal(11, VarkaCards.ShatterDamage(5m, 2m, 3));
        Assert.Equal(16, VarkaCards.ShatterDamage(7m, 3m, 3));
        Assert.Equal(0, VarkaCards.WeakAndVulnerable(null));
        Assert.Contains(card.DynamicVars.Values, v => v is VarkaShatterDamageVar);
        Assert.Contains("(Deals {VkHit:diff()} damage)", Face(card));
        var hit = Calls("VarkaCards", "Shatter");
        Assert.Contains("VarkaCards.WeakAndVulnerable", hit);
        Assert.Contains("VarkaCards.ElementHit", hit);
    }

    [Fact]
    public void Deep_freeze_retains_and_doubles_weak_and_vulnerable()
    {
        var card = new ProtoVkDeepFreeze();
        Assert.Contains(CardKeyword.Retain, card.CanonicalKeywords);
        Assert.Equal(0, UpgradedCost<ProtoVkDeepFreeze>());
        var play = Calls("ProtoVkDeepFreeze", "OnPlay");
        Assert.True(play.IndexOf("ElementalHit.ApplyOnly")
                    < play.IndexOf("VarkaCards.DeepFreeze"));
        Assert.Contains("PowerCmd.Apply", Calls("VarkaCards", "DeepFreeze"));
    }

    // ---- sec.4: Unwavering Banner, reworded ---------------------------------------

    [Fact]
    public void The_banner_holds_and_pays_once_per_play()
    {
        Assert.Equal("Only [gold]Knights[/gold] can change your [gold]current "
                     + "element[/gold]. Whenever another card would, gain 1 "
                     + "[gold]Oath[/gold] of your [gold]current element[/gold] "
                     + "instead.", Face(new UnwaveringBannerPower()));
        Assert.Contains("VarkaOath.BannerHolds",
                        Calls("VarkaOath", "NoteApplication"));
        Assert.Contains("VarkaOath.BannerHolds",
                        Calls("VarkaCards", "ChangeOfGuard"));
        var holds = Calls("VarkaOath", "BannerHolds");
        Assert.Contains("VarkaOathLedger.TakeBannerPay", holds);
        Assert.Contains("VarkaOath.Gain", holds);
        // The latch is one per play: open a play, take it twice.
        var ledger = new VarkaOathLedger();
        ledger.OpenScope(open: true, card: null);
        Assert.True(ledger.TakeBannerPay());
        Assert.False(ledger.TakeBannerPay());
        ledger.CloseScope();
        ledger.OpenScope(open: true, card: null);
        Assert.True(ledger.TakeBannerPay());
    }

    // ---- sec.1 and sec.2's fixes ---------------------------------------------------

    [Fact]
    public void Baron_bunny_hits_one_random_enemy()
    {
        var fire = Calls("VarkaBaronBunnyPower", "Fire");
        Assert.Contains("Rng.NextItem", fire);
        Assert.Single(fire, c => c == "ElementalHit.DealWithoutDealerMods");
        Assert.Contains("a random enemy", Face(new ProtoVkAmberBaronBunny()));
        Assert.Contains("a random enemy", Face(new VarkaBaronBunnyPower()));
        Assert.Equal(6m, Var(new ProtoVkAmberBaronBunny(), "PowerAmount"));
        Assert.Equal(8m, Var(Upgraded<ProtoVkAmberBaronBunny>(), "PowerAmount"));
    }

    [Fact]
    public void Charge_of_the_knights_costs_1_and_pays_5_then_7()
    {
        var card = new ProtoVkChargeOfTheKnights();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(5m, Var(card, "ExtraDamage"));
        Assert.Equal(7m, Var(Upgraded<ProtoVkChargeOfTheKnights>(), "ExtraDamage"));
    }

    [Fact]
    public void Lions_fang_and_four_winds_ascension_upgrade_their_cost()
    {
        Assert.Equal(2, new ProtoMcJeanLionsFang().EnergyCost.Canonical);
        Assert.Equal(1, UpgradedCost<ProtoMcJeanLionsFang>());
        Assert.Equal(1, UpgradedCost<ProtoVkFourWindsAscension>());
        Assert.Equal(10m, Var(Upgraded<ProtoVkFourWindsAscension>(), "Damage"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkFourWindsAscension>(), "VkPer"));
    }

    [Fact]
    public void Kaeya_and_razor_are_attacks()
    {
        Assert.Equal(CardType.Attack, new ProtoVkKaeyaFrostgnaw().Type);
        Assert.Equal(CardType.Attack, new ProtoVkRazorClawAndThunder().Type);
    }

    [Fact]
    public void Thundering_verdict_and_converging_winds_say_it_plainly()
    {
        Assert.StartsWith("Deal {VkBase:diff()} [gold]Electro[/gold] damage, plus "
                          + "{VkPer:diff()} for each [gold]Electro[/gold] [gold]Oath[/gold], to "
                          + "ALL enemies X times.",
                          Face(new ProtoVkThunderingVerdict()));
        Assert.Contains("(Deals {VkHit:diff()} damage each time)",
                        Face(new ProtoVkThunderingVerdict()));
        const string winds = "The elements your [gold]Swirls[/gold] spread set "
                           + "off [gold]Elemental Reactions[/gold].";
        Assert.Equal(winds, Face(new ProtoVkConvergingWinds()));
        Assert.Equal(winds, Face(new ConvergingWindsPower()));
    }
}
