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
        Assert.Null(typeof(WildfireOathPower).Assembly.GetType(
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
            // Varka payoff fix (2026-10-08): Stoke costs 0, was 1.
            Assert.Equal(card is ProtoVkStokeTheFlames ? 0 : 1,
                         card.EnergyCost.Canonical);
        }
    }

    [Fact]
    public void The_payoff_fix_rares_cost_1()
    {
        // Varka payoff fix (2026-10-08): both rares cost 1, were 2.
        Assert.Equal(1, new ProtoVkWildfireOath().EnergyCost.Canonical);
        Assert.Equal(1, new ProtoVkAbsoluteZero().EnergyCost.Canonical);
    }

    // ---- sec.3: Pyro burns -------------------------------------------------------

    [Fact]
    public void Stoke_the_flames_gains_pyro_then_powers_the_next_pyro_attack()
    {
        // Pyro paper 2 (2026-10-12): "Gain 2 [3] Pyro Oath. Your next Pyro
        // Attack this turn deals 5 [7] additional damage." The rider is gone.
        Assert.Equal(2m, Var(new ProtoVkStokeTheFlames(), "VkAmount"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkStokeTheFlames>(), "VkAmount"));
        Assert.Equal(5m, Var(new ProtoVkStokeTheFlames(), "VkBase"));
        Assert.Equal(7m, Var(Upgraded<ProtoVkStokeTheFlames>(), "VkBase"));
        var play = Calls("ProtoVkStokeTheFlames", "OnPlay");
        Assert.DoesNotContain("CardSelectCmd.FromHand", play);
        Assert.DoesNotContain(play, c => c.Contains("NextAttackUpPower"));
        var gain = play.IndexOf("VarkaCards.GainPyroOath");
        var buff = play.IndexOf("VarkaCards.NextPyroAttack");
        Assert.True(gain >= 0 && gain < buff);
        Assert.Contains(Il.CallSequence(Il.Method("VarkaCards", "NextPyroAttack")),
                        c => c.Contains("PowerCmd.Apply<StokeTheFlamesPower>"));
        Assert.Null(typeof(VarkaCards).GetMethod("ExhaustForPyroOath"));
        // The Varka payoff round (2026-10-10): "Pyro becomes your current
        // element" FIRST, through the non-Knight path Unwavering Banner
        // holds, then the gain, so Dawn Wind's March sees a current-element
        // gain.
        var stoke = Calls("VarkaCards", "GainPyroOath");
        Assert.True(stoke.IndexOf("VarkaOath.CardMakesCurrent")
                    < stoke.IndexOf("VarkaOath.Gain"));
        var makes = Calls("VarkaOath", "CardMakesCurrent");
        Assert.Contains("VarkaOath.BannerHolds", makes);
        Assert.Contains("VarkaOath.SetCurrent", makes);
        // The switch prints as the switch tip, and since the Varka review
        // (2026-10-12) on the face too.
        Assert.Contains("ArmKeywordTips.ForElementSwitch",
                        Il.Calls(Il.Method("ProtoVkStokeTheFlames", "get_ExtraHoverTips")));
        Assert.Equal("[gold]Pyro[/gold] becomes your [gold]current element[/gold]. "
                     + "Gain {VkAmount:diff()} [gold]Pyro[/gold] [gold]Oath[/gold]. "
                     + "Your next [gold]Pyro[/gold] Attack this turn deals "
                     + "{VkBase:diff()} additional damage.",
                     Face(new ProtoVkStokeTheFlames()));
    }

    [Fact]
    public void Stokes_power_pays_pyro_attack_hits_and_ends_with_the_turn()
    {
        // Only a powered Pyro hit of an Attack card takes the bonus.
        Assert.True(StokeTheFlamesPower.Applies(true, true, Element.Pyro));
        Assert.False(StokeTheFlamesPower.Applies(true, true, Element.Anemo));
        Assert.False(StokeTheFlamesPower.Applies(true, true, Element.Cryo));
        Assert.False(StokeTheFlamesPower.Applies(true, false, Element.Pyro));
        Assert.False(StokeTheFlamesPower.Applies(false, true, Element.Pyro));
        // Spent only by a play a Pyro hit paid; gone at the turn's end.
        Assert.Contains("PowerCmd.Remove",
                        Calls("StokeTheFlamesPower", "AfterSideTurnEnd"));
        Assert.Contains("PowerCmd.Remove",
                        Calls("StokeTheFlamesPower", "AfterCardPlayed"));
        Assert.Equal("Your next [gold]Pyro[/gold] Attack this turn deals "
                     + "[blue]{Amount}[/blue] additional damage.",
                     Face(new StokeTheFlamesPower()));
    }

    [Fact]
    public void Ember_cleave_is_setup_strike_in_pyro()
    {
        // Pyro paper 2 (2026-10-12): "Deal 7 [9] Pyro damage. Gain 2 [3]
        // Strength this turn." No Oath gain, no Exhaust rider. The Varka
        // review (2026-10-12, pick 1 (a)): 9 [11].
        Assert.Equal(9m, Var(new ProtoVkEmberCleave(), "VkBase"));
        Assert.Equal(11m, Var(Upgraded<ProtoVkEmberCleave>(), "VkBase"));
        Assert.Equal(2m, Var(new ProtoVkEmberCleave(), "VkAmount"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkEmberCleave>(), "VkAmount"));
        var play = Calls("ProtoVkEmberCleave", "OnPlay");
        Assert.Contains("VarkaCards.ElementHit", Calls("VarkaCards", "PyroStrike"));
        Assert.DoesNotContain("CardSelectCmd.FromHand", play);
        Assert.DoesNotContain("VarkaCards.GainPyroOath", play);
        Assert.True(play.IndexOf("VarkaCards.PyroStrike") >= 0
                    && play.IndexOf("VarkaCards.PyroStrike")
                       < play.IndexOf("VarkaCards.TemporaryStrength"));
        Assert.Contains(Il.CallSequence(Il.Method("VarkaCards", "TemporaryStrength")),
                        c => c.Contains("PowerCmd.Apply<EmberCleavePower>"));
        Assert.True(typeof(MegaCrit.Sts2.Core.Models.Powers.TemporaryStrengthPower)
            .IsAssignableFrom(typeof(EmberCleavePower)));
        Assert.Equal("Deal {VkBase:diff()} [gold]Pyro[/gold] damage. Gain "
                     + "{VkAmount:diff()} [gold]Strength[/gold] this turn.{InCombat:{VarkaSwitch}|}{InCombat:{VarkaWildfire}|}",
                     Face(new ProtoVkEmberCleave()));
    }

    [Fact]
    public void Ashen_oath_gains_strength_and_pyro_oath()
    {
        // The Pyro pass (2026-10-11): "Gain 2 [3] Strength. Gain 2 Pyro
        // Oath." Its Exhaust-trigger power left with it; the gain switches
        // nothing.
        string Title(BaseLib.Abstracts.ILocalizationProvider m) =>
            m.Localization!.Single(r => r.Item1 == "title").Item2;
        Assert.Equal("For Crepus", Title(new ProtoVkPyreOath()));
        Assert.Null(typeof(WildfireOathPower).Assembly.GetType(
            "KleeMod.Powers.PyreOathPower"));
        Assert.DoesNotContain(CardKeyword.Innate, Upgraded<ProtoVkPyreOath>().Keywords);
        Assert.Equal(2m, Var(new ProtoVkPyreOath(), "PowerAmount"));
        Assert.Equal(3m, Var(Upgraded<ProtoVkPyreOath>(), "PowerAmount"));
        Assert.Equal(2m, Var(new ProtoVkPyreOath(), "VkAmount"));
        var play = Calls("ProtoVkPyreOath", "OnPlay");
        Assert.Contains("VarkaCards.PyroOath", play);
        Assert.DoesNotContain("CardSelectCmd.FromHand", play);
        Assert.DoesNotContain("VarkaOath.CardMakesCurrent",
                              Calls("VarkaCards", "PyroOath"));
        Assert.Equal("Gain {PowerAmount:diff()} [gold]Strength[/gold]. Gain "
                     + "{VkAmount:diff()} [gold]Pyro[/gold] [gold]Oath[/gold].",
                     Face(new ProtoVkPyreOath()));
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
    public void Deep_freeze_doubles_weak_and_vulnerable_without_retain()
    {
        var card = new ProtoVkDeepFreeze();
        // Retain dropped 2026-10-13 ([USER]: "I think we should drop Retain").
        Assert.DoesNotContain(CardKeyword.Retain, card.CanonicalKeywords);
        Assert.Equal(0, UpgradedCost<ProtoVkDeepFreeze>());
        var play = Calls("ProtoVkDeepFreeze", "OnPlay");
        Assert.True(play.IndexOf("ElementalHit.ApplyOnly")
                    < play.IndexOf("VarkaCards.DeepFreeze"));
        // Varka payoff fix (2026-10-08): 1 Vulnerable lands before the
        // doubling; Varka last pass (2026-10-12): 1 Weak too.
        Assert.True(play.FindLastIndex(c => c.StartsWith("PowerCmd.Apply", StringComparison.Ordinal))
                    < play.IndexOf("VarkaCards.DeepFreeze"));
        Assert.Equal(2, Il.CallSequence(Il.Method("ProtoVkDeepFreeze", "OnPlay"))
                        .Count(c => c.StartsWith("PowerCmd.Apply", StringComparison.Ordinal)));
        Assert.Contains("PowerCmd.Apply", Calls("VarkaCards", "DeepFreeze"));
    }

    // ---- sec.4: Unwavering Banner, reworded ---------------------------------------

    [Fact]
    public void The_banner_holds_and_pays_once_per_play()
    {
        Assert.Equal("Only [gold]Knights[/gold] change your [gold]current "
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
    public void Charge_of_the_knights_costs_1_and_pays_8_plus_5_then_7()
    {
        var card = new ProtoVkChargeOfTheKnights();
        Assert.Equal(1, card.EnergyCost.Canonical);
        // Varka last pass (2026-10-12): a floor of 8.
        Assert.Equal(8m, Var(card, "CalculationBase"));
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
        // Varka round 3, pick 1 (2026-10-10): re-aimed at 6 [8].
        Assert.Equal("Your [gold]Swirls[/gold] deal {PowerAmount:diff()} "
                     + "additional damage to ALL enemies.",
                     Face(new ProtoVkConvergingWinds()));
        Assert.Equal("Your [gold]Swirls[/gold] deal [blue]{Amount}[/blue] "
                     + "additional damage to ALL enemies.",
                     Face(new ConvergingWindsPower()));
    }

    // ---- text pass 2026-10-13: the second hit's in-combat total ---------------

    [Fact]
    public void Ascension_and_avatar_print_the_second_hits_live_total()
    {
        // [USER]: "the second line doesn't actually say how much it's going
        // to hit for". The face prints {VkHit}; the hit itself is unchanged.
        var ascension = new ProtoVkFourWindsAscension();
        var avatar = new ProtoVkNorthwindAvatar();
        foreach (var card in new CardModel[] { ascension, avatar })
        {
            Assert.Contains(card.DynamicVars.Values,
                            v => v is VarkaCurrentElementHitVar);
            Assert.Contains("as that element.{InCombat:\n(Deals "
                            + "{VkHit:diff()} damage)|}", Face(card));
            Assert.DoesNotContain("in one hit", Face(card));
        }
        Assert.Equal("VkHit", VarkaCurrentElementHitVar.Token);

        // Ascension: 3 per Oath of the current element, nothing without one.
        Assert.Equal(0, VarkaCurrentElementHitVar.Raw(0m, 3m, Element.Pyro, 0));
        Assert.Equal(12, VarkaCurrentElementHitVar.Raw(0m, 3m, Element.Pyro, 4));
        Assert.Equal(0, VarkaCurrentElementHitVar.Raw(0m, 3m, Element.None, 4));
        // Avatar: 8 [12], plus 2 per Oath.
        Assert.Equal(8, VarkaCurrentElementHitVar.Raw(
            Var(avatar, "VkBase"), Var(avatar, "VkPer"), Element.Cryo, 0));
        Assert.Equal(14, VarkaCurrentElementHitVar.Raw(
            Var(avatar, "VkBase"), Var(avatar, "VkPer"), Element.Cryo, 3));
        var upgraded = Upgraded<ProtoVkNorthwindAvatar>();
        Assert.Equal(18, VarkaCurrentElementHitVar.Raw(
            Var(upgraded, "VkBase"), Var(upgraded, "VkPer"), Element.Hydro, 3));
        Assert.Equal(0, VarkaCurrentElementHitVar.Raw(
            Var(avatar, "VkBase"), Var(avatar, "VkPer"), Element.None, 3));

        // BACKLOG 2026-10-19: the one-target cards' Anemo hit Swirls the
        // body's aura first, so the second hit's preview folds no reaction;
        // Dandelion Gale (ALL enemies) keeps the fold.
        Assert.True(VarkaCurrentElementHitVar.FollowsOwnAnemoHit(ascension));
        Assert.True(VarkaCurrentElementHitVar.FollowsOwnAnemoHit(avatar));
        Assert.False(VarkaCurrentElementHitVar.FollowsOwnAnemoHit(
            new global::KleeMod.Cards.Varka.DandelionGale()));

        // Still one hit each: both go through the one shared hit.
        Assert.Contains("VarkaCards.CurrentElementHit",
                        Calls("VarkaCards", "AscensionHit"));
        Assert.Contains("VarkaCards.CurrentElementHit",
                        Calls("VarkaCards", "AvatarHit"));
    }
}
