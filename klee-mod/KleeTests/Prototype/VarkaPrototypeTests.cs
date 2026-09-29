using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>The one collection every pin that flips
/// <see cref="VarkaPrototype.Enabled"/> runs in.</summary>
[CollectionDefinition(Name, DisableParallelization = true)]
public sealed class VarkaArm
{
    public const string Name = "VarkaArm";
}

/// <summary>
/// VARKA, PROTOTYPE BATCH ONE (<c>review/active/varka-paper-kit-2026-09-28.md</c>
/// sec.10). The rules are pinned the way the element port's are
/// (<c>ElementPortTests</c>): a hit landing needs a live combat, outside the
/// headless boundary, so each rule is ONE pure decision read value by value,
/// on real cards and real seats, and the call graph is pinned to prove the
/// live sites take that decision rather than their own. What only play can
/// show -- the Wind payouts landing, the grid choosing -- is in the PR's
/// in-game checklist.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaPrototypeTests : IDisposable
{
    private readonly bool _enabled = VarkaPrototype.Enabled;
    private readonly bool _swirl = TriggerRules.SwirlPays;

    public VarkaPrototypeTests()
    {
        HeadlessGame.Arm();
        VarkaPrototype.Enabled = true;
    }

    public void Dispose()
    {
        VarkaPrototype.Enabled = _enabled;
        TriggerRules.SwirlPays = _swirl;
    }

    private static T Aura<T>(bool spent) where T : AuraPower
    {
        var aura = (T)RuntimeHelpers.GetUninitializedObject(typeof(T));
        aura.Spent = spent;
        return aura;
    }

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static decimal Var(CardModel card, string name) =>
        card.DynamicVars[name].BaseValue;

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static List<string> Cards(string type, string method) =>
        Il.CallSequence(Il.Method(type, method))
            .Where(c => c.StartsWith("ModelDb.Card<", StringComparison.Ordinal))
            .ToList();

    private static BoreasFang Fang(Seat seat) =>
        seat.Player.Relics.OfType<BoreasFang>().Single();

    // ---- the arm -----------------------------------------------------------

    // ON in every build that names no property (Directory.Build.props).
    // SKIPPED, NOT LEFT TO FAIL, where the build opts him out
    // (-p:ShippedKits=true or -p:VarkaPrototype=false): there the property
    // moved the value this pin asserts (operations/prototype.md).
#if VARKA_PROTOTYPE
    [Fact]
#else
    [Fact(Skip = "This build opts Varka out (-p:ShippedKits=true or -p:VarkaPrototype=false), which moves the default this pin asserts.")]
#endif
    public void The_arm_ships_on()
    {
        Assert.True(VarkaPrototype.DefaultEnabled);
    }

    // ---- Absorb: the rule, on primitives -----------------------------------

    [Theory]
    // A fresh aura and an Absorb card: the aura comes off, the Wind is his.
    [InlineData(Element.Pyro, false, true, false, false, AbsorbOutcome.Absorb)]
    // He already holds that Wind: the hit Swirls instead.
    [InlineData(Element.Pyro, false, true, false, true, AbsorbOutcome.SwirlInstead)]
    // A spent aura is not fresh: only the card's damage.
    [InlineData(Element.Pyro, true, true, false, false, AbsorbOutcome.None)]
    // No aura at all: only the card's damage.
    [InlineData(Element.None, false, true, false, false, AbsorbOutcome.None)]
    // The Fang reads the same rule on a card that prints no Absorb.
    [InlineData(Element.Hydro, false, false, true, false, AbsorbOutcome.Absorb)]
    [InlineData(Element.Cryo, false, false, true, true, AbsorbOutcome.SwirlInstead)]
    [InlineData(Element.Electro, true, false, true, false, AbsorbOutcome.None)]
    // Neither an Absorb card nor a ready Fang: the ordinary lifecycle.
    [InlineData(Element.Hydro, false, false, false, false, AbsorbOutcome.None)]
    // Anemo and Geo leave no aura, so there is no Wind of theirs.
    [InlineData(Element.Anemo, false, true, false, false, AbsorbOutcome.None)]
    [InlineData(Element.Geo, false, true, false, false, AbsorbOutcome.None)]
    public void Absorb_on_fresh_held_spent_and_bare_auras(
        Element aura, bool spent, bool absorbCard, bool fangReady,
        bool holdsWind, AbsorbOutcome expected)
    {
        Assert.Equal(expected,
            VarkaAbsorb.Decide(aura, spent, absorbCard, fangReady, holdsWind));
    }

    [Fact]
    public void With_the_arm_off_nothing_absorbs()
    {
        VarkaPrototype.Enabled = false;
        Assert.Equal(AbsorbOutcome.None,
            VarkaAbsorb.Decide(Element.Pyro, false, true, true, false));
        var seat = Seat.Klee();
        Assert.Equal(AbsorbOutcome.None, VarkaAbsorb.Decide(
            Aura<PyroAuraPower>(false), seat.Creature,
            new ProtoVkWindboundExecution()));
    }

    // ---- Absorb: real cards, a real seat -------------------------------------

    [Fact]
    public void Windbound_absorbs_a_fresh_aura_and_swirls_a_held_wind()
    {
        var seat = Seat.Klee();
        var card = new ProtoVkWindboundExecution();
        Assert.IsAssignableFrom<IAbsorbCard>(card);
        Assert.Equal(AbsorbOutcome.Absorb, VarkaAbsorb.Decide(
            Aura<PyroAuraPower>(false), seat.Creature, card));
        Assert.Equal(AbsorbOutcome.None, VarkaAbsorb.Decide(
            Aura<PyroAuraPower>(true), seat.Creature, card));

        seat.WithPower<PyroWindPower>(1);
        Assert.Equal(AbsorbOutcome.SwirlInstead, VarkaAbsorb.Decide(
            Aura<PyroAuraPower>(false), seat.Creature, card));
        // Another element's Wind does not stop a Hydro Absorb.
        Assert.Equal(AbsorbOutcome.Absorb, VarkaAbsorb.Decide(
            Aura<HydroAuraPower>(false), seat.Creature, card));
    }

    [Fact]
    public void Favonius_cut_absorbs_and_the_plain_anemo_attacks_do_not()
    {
        var seat = Seat.Klee();
        Assert.IsAssignableFrom<IAbsorbCard>(new ProtoVkFavoniusCut());
        foreach (var card in new CardModel[]
                 {
                     new ProtoVkUpdraft(), new ProtoVkSquall(),
                     new ProtoVkTempestCharge(), new ProtoVkGaleSweep(),
                     new ProtoVkFourWindsAscension(),
                 })
        {
            Assert.IsNotAssignableFrom<IAbsorbCard>(card);
            Assert.Equal(AbsorbOutcome.None, VarkaAbsorb.Decide(
                Aura<CryoAuraPower>(false), seat.Creature, card));
        }
    }

    [Fact]
    public void The_lifecycle_and_the_multiplier_take_the_one_decision()
    {
        // STRUCTURAL. The aura's two sites, the forecast and the hit, ask the
        // same pure question, and only the hit carries it out.
        var lifecycle = Il.Calls(Il.Method("AuraPower", "ResolveLifecycle"));
        Assert.Contains("VarkaAbsorb.Decide", lifecycle);
        Assert.Contains("VarkaAbsorb.Take", lifecycle);
        Assert.Contains("VarkaAbsorb.NoteFang", lifecycle);
        var forecast = Il.Calls(Il.Method("AuraPower", "ModifyDamageMultiplicative"));
        Assert.Contains("VarkaAbsorb.Decide", forecast);
        Assert.DoesNotContain("VarkaAbsorb.Take", forecast);
        // An Absorb takes the aura off, gives the Wind and pays Boreas
        // Unbound; nothing in it reacts.
        var take = Il.Calls(Il.Method("VarkaAbsorb", "Take"));
        Assert.Contains("PowerCmd.Remove", take);
        Assert.Contains("VarkaWinds.Gain", take);
        Assert.Contains("BoreasUnboundPower.OnAbsorb", take);
        Assert.DoesNotContain("ReactionEffects.Resolve", take);
    }

    // ---- Boreas's Fang -------------------------------------------------------

    [Fact]
    public void The_fang_takes_the_first_non_anemo_attack_once_a_turn()
    {
        var seat = Seat.Klee().WithRelic<BoreasFang>();
        var strike = new StrikeSilent();

        Assert.True(VarkaAbsorb.FangTakes(seat.Creature, strike));
        Assert.Equal(AbsorbOutcome.Absorb, VarkaAbsorb.Decide(
            Aura<PyroAuraPower>(false), seat.Creature, strike));
        Assert.Equal(1, Fang(seat).DisplayAmount);

        // Used this turn: the next Attack is only an Attack.
        Seat.Force(Fang(seat), "UsedThisTurn", true);
        Assert.False(VarkaAbsorb.FangTakes(seat.Creature, strike));
        Assert.Equal(AbsorbOutcome.None, VarkaAbsorb.Decide(
            Aura<PyroAuraPower>(false), seat.Creature, strike));
        Assert.Equal(0, Fang(seat).DisplayAmount);
    }

    [Fact]
    public void The_fang_reads_absorbs_rule_so_a_held_wind_swirls()
    {
        var seat = Seat.Klee().WithRelic<BoreasFang>()
            .WithPower<HydroWindPower>(1);
        Assert.Equal(AbsorbOutcome.SwirlInstead, VarkaAbsorb.Decide(
            Aura<HydroAuraPower>(false), seat.Creature, new StrikeSilent()));
    }

    [Fact]
    public void The_fang_passes_by_anemo_attacks_skills_and_a_seat_without_it()
    {
        var seat = Seat.Klee().WithRelic<BoreasFang>();
        // "the first NON-ANEMO Attack": an Anemo Attack Swirls instead.
        Assert.False(VarkaAbsorb.FangTakes(seat.Creature, new ProtoVkUpdraft()));
        // Knights are Skills (sec.9.6): a Knight never Absorbs its own paint.
        Assert.False(VarkaAbsorb.FangTakes(seat.Creature,
                                           new ProtoVkAmberBaronBunny()));
        Assert.False(VarkaAbsorb.FangTakes(seat.Creature, new DefendSilent()));
        // No Fang, no Fang.
        Assert.False(VarkaAbsorb.FangTakes(Seat.Klee().Creature,
                                           new StrikeSilent()));
        Assert.True(VarkaAbsorb.IsFangAttackElement(Element.None));
        Assert.True(VarkaAbsorb.IsFangAttackElement(Element.Pyro));
        Assert.False(VarkaAbsorb.IsFangAttackElement(Element.Anemo));
    }

    [Fact]
    public void The_fang_clears_each_turn_and_names_absorb_and_wind()
    {
        Assert.Contains("BoreasFang.set_UsedThisTurn",
                        Il.Calls(Il.Method("BoreasFang", "AfterPlayerTurnStart")));
        Assert.Contains("BoreasFang.set_UsedThisTurn",
                        Il.Calls(Il.Method("BoreasFang", "BeforeCombatStart")));
        var tips = Il.Calls(Il.Method("BoreasFang", "get_ExtraHoverTips"));
        Assert.Contains("ArmKeywordTips.ForAbsorb", tips);
        Assert.Contains("ArmKeywordTips.ForWind", tips);
        // His fourth, Companion, reward choice, every starter's.
        Assert.Contains("CompanionSlot.Roll",
                        Il.Calls(Il.Method("BoreasFang", "TryModifyCardRewardOptions")));
    }

    // ---- the Winds -------------------------------------------------------------

    [Fact]
    public void The_winds_he_holds_are_read_off_his_badges()
    {
        var seat = Seat.Klee();
        Assert.Equal(0, VarkaWinds.HeldCount(seat.Creature));
        seat.WithPower<ElectroWindPower>(1).WithPower<PyroWindPower>(1);
        Assert.Equal(2, VarkaWinds.HeldCount(seat.Creature));
        Assert.True(VarkaWinds.Holds(seat.Creature, Element.Pyro));
        Assert.False(VarkaWinds.Holds(seat.Creature, Element.Cryo));
        // In the payout order, not the order they were gained.
        Assert.Equal(new[] { Element.Pyro, Element.Electro },
                     VarkaWinds.Held(seat.Creature));
        Assert.Equal(0, VarkaWinds.HeldCount(null));
    }

    [Theory]
    [InlineData(typeof(PyroWindPower), Element.Pyro, "ElementalHit.DealUnelemented")]
    [InlineData(typeof(HydroWindPower), Element.Hydro, "CreatureCmd.GainBlock")]
    [InlineData(typeof(CryoWindPower), Element.Cryo, "PowerCmd.Apply")]
    [InlineData(typeof(ElectroWindPower), Element.Electro, "PlayerCmd.GainEnergy")]
    public void Each_wind_pays_its_own_kind_on_a_swirl(
        Type wind, Element element, string pays)
    {
        var power = (WindPower)RuntimeHelpers.GetUninitializedObject(wind);
        Assert.Equal(element, power.Element);
        Assert.Contains(pays, Il.Calls(Il.Method(wind.Name, "PayOnSwirl")));
    }

    [Fact]
    public void The_wind_numbers_are_sec_ten_and_the_badges_print_them()
    {
        Assert.Equal(3, VarkaLaw.PyroWindDamage);
        Assert.Equal(3, VarkaLaw.HydroWindBlock);
        Assert.Equal(1, VarkaLaw.CryoWindWeak);
        Assert.Equal(1, VarkaLaw.ElectroWindEnergy);
        string Badge(Type t) =>
            ((WindPower)RuntimeHelpers.GetUninitializedObject(t)).Localization!
                .First(r => r.Item1 == "description").Item2;
        Assert.Contains("deal [blue]3[/blue] damage to the enemy you hit",
                        Badge(typeof(PyroWindPower)));
        Assert.Contains("gain [blue]3[/blue] [gold]Block[/gold]",
                        Badge(typeof(HydroWindPower)));
        Assert.Contains("apply [blue]1[/blue] [gold]Weak[/gold]",
                        Badge(typeof(CryoWindPower)));
        Assert.Contains("The first time you [gold]Swirl[/gold] each turn",
                        Badge(typeof(ElectroWindPower)));
    }

    [Fact]
    public void Every_swirl_pays_the_winds_from_the_one_reaction_site()
    {
        // STRUCTURAL: `ReactionEffects.Resolve` is the single site every
        // reaction in the mod passes, and the Winds are paid there once.
        Assert.Contains("VarkaWinds.OnSwirl",
                        Il.Calls(Il.Method("ReactionEffects", "Resolve")));
        var onSwirl = Il.Calls(Il.Method("VarkaWinds", "OnSwirl"));
        Assert.Contains("WindPower.PayOnSwirl", onSwirl);
        Assert.Contains("VarkaPrototype.get_Enabled", onSwirl);
        // Electro's once-a-turn latch clears at the end of HIS turn.
        Assert.Contains("ElectroWindPower.set_PaidThisTurn",
                        Il.Calls(Il.Method("ElectroWindPower", "AfterSideTurnEnd")));
    }

    // ---- Four Winds' Ascension ---------------------------------------------

    [Fact]
    public void Ascension_is_six_plus_six_per_wind_and_exhausts()
    {
        var card = new ProtoVkFourWindsAscension();
        Assert.Equal(2, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Attack, card.Type);
        Assert.Equal(CardRarity.Basic, card.Rarity);
        Assert.Contains(CardKeyword.Exhaust, card.Keywords);
        Assert.Equal(6m, Var(card, "CalculationBase"));
        Assert.Equal(6m, Var(card, "ExtraDamage"));
        // sec.10.2: "Deal 6 [9] Anemo, plus 6 for each Wind you hold."
        var up = Upgraded<ProtoVkFourWindsAscension>();
        Assert.Equal(9m, Var(up, "CalculationBase"));
        Assert.Equal(6m, Var(up, "ExtraDamage"));
        // The count it multiplies is the Winds he holds.
        Assert.Contains("VarkaWinds.HeldCount",
                        Il.Calls(Il.Method("ProtoVkFourWindsAscension",
                                           "get_CanonicalVars")));
        Assert.Equal(Element.Anemo, ((IElementalCard)card).Element);
        // No Ancient card yet: the Tome hands him this one.
        Assert.IsAssignableFrom<ITomeCard>(card);
    }

    [Fact]
    public void Eye_of_the_storm_is_four_block_per_wind_and_five_upgraded()
    {
        var card = new ProtoVkEyeOfTheStorm();
        Assert.Equal(0m, Var(card, "CalculationBase"));
        Assert.Equal(4m, Var(card, "CalculationExtra"));
        Assert.Equal(5m, Var(Upgraded<ProtoVkEyeOfTheStorm>(), "CalculationExtra"));
    }

    // ---- Converging Winds --------------------------------------------------

    [Theory]
    // Without the power a spread never reacts: the copy replaces, spent.
    [InlineData(false, Element.Pyro, Element.Hydro, Reaction.None)]
    // With it, the spread's flat 2 carries the element into the aura.
    [InlineData(true, Element.Pyro, Element.Hydro, Reaction.Vaporize)]
    [InlineData(true, Element.Electro, Element.Pyro, Reaction.Overload)]
    [InlineData(true, Element.Cryo, Element.Electro, Reaction.Superconduct)]
    // A bare enemy takes the spent copy, and one already wearing the element
    // keeps its own, exactly as without the power.
    [InlineData(true, Element.Pyro, Element.None, Reaction.None)]
    [InlineData(true, Element.Pyro, Element.Pyro, Reaction.None)]
    public void Converging_winds_reacts_where_a_spread_lands(
        bool converges, Element spread, Element existing, Reaction expected)
    {
        Assert.Equal(expected,
            ConvergingWindsPower.SpreadReaction(converges, spread, existing));
    }

    [Fact]
    public void A_spread_reaction_lands_on_that_enemy_only_and_never_swirls()
    {
        // STRUCTURAL: the Swirl asks the one decision, resolves the reaction
        // through the one site with the spread flag, and the flag keeps an
        // Overload off every other enemy and stops a second Swirl.
        var swirl = Il.Calls(Il.Method("ReactionEffects", "SwirlPays"));
        Assert.Contains("ConvergingWindsPower.SpreadReaction", swirl);
        Assert.Contains("ConvergingWindsPower.Converges", swirl);
        Assert.Contains("ReactionEffects.Resolve", swirl);
        Assert.Contains("VarkaRules.SpreadShielded", swirl);
        Assert.NotNull(Il.Method("ReactionEffects", "Resolve")
            .GetParameters().SingleOrDefault(p => p.Name == "spreadReaction"));
        // With the arm off no dealer converges.
        VarkaPrototype.Enabled = false;
        Assert.False(ConvergingWindsPower.Converges(
            Seat.Klee().WithPower<ConvergingWindsPower>(1).Creature));
        VarkaPrototype.Enabled = true;
        Assert.True(ConvergingWindsPower.Converges(
            Seat.Klee().WithPower<ConvergingWindsPower>(1).Creature));
        Assert.False(ConvergingWindsPower.Converges(Seat.Klee().Creature));
    }

    // ---- the other cards' rules ------------------------------------------

    [Theory]
    [InlineData(true, true, Element.Anemo, 2, true)]
    [InlineData(true, true, Element.Anemo, 4, true)]
    [InlineData(true, true, Element.Anemo, 1, false)]
    [InlineData(true, true, Element.Pyro, 3, false)]
    [InlineData(true, false, Element.Anemo, 3, false)]
    [InlineData(false, true, Element.Anemo, 3, false)]
    public void Stormward_stance_needs_two_winds_and_an_anemo_attack(
        bool powered, bool attack, Element hit, int winds, bool expected)
    {
        Assert.Equal(expected,
            StormwardStancePower.Applies(powered, attack, hit, winds));
    }

    [Fact]
    public void Gale_sweep_takes_the_fresh_auras_when_it_is_played()
    {
        var fresh = Seat.Klee(30).WithPower<PyroAuraPower>(2);
        var spent = Seat.Klee(30).WithPower<HydroAuraPower>(2);
        spent.Creature.Powers.OfType<AuraPower>().Single().Spent = true;
        var bare = Seat.Klee(30);
        Assert.Equal(new[] { fresh.Creature },
                     VarkaRules.FreshAuraBodies(new[]
                     {
                         fresh.Creature, spent.Creature, bare.Creature,
                     }));
        Assert.False(VarkaRules.SpreadShielded(fresh.Creature));
        Assert.Contains("VarkaRules.HitFreshAuras",
                        Il.Calls(Il.Method("ProtoVkGaleSweep", "OnPlay")));
    }

    [Fact]
    public void Tempest_charge_asks_whether_this_play_swirled()
    {
        var calls = Il.CallSequence(Il.Method("ProtoVkTempestCharge", "OnPlay"));
        Assert.Equal(2, calls.Count(c => c == "VarkaWinds.SwirlsMadeBy"));
        Assert.Equal(0, VarkaWinds.SwirlsMadeBy(Seat.Klee().Creature));
    }

    // ---- the Knights -------------------------------------------------------

    [Fact]
    public void The_knights_are_his_personal_companion_skills()
    {
        var knights = new (CardModel Card, Element Element)[]
        {
            (new ProtoVkAmberBaronBunny(), Element.Pyro),
            (new ProtoVkBarbaraShowBegin(), Element.Hydro),
            (new ProtoVkLisaVioletArc(), Element.Electro),
            (new ProtoVkKaeyaFrostgnaw(), Element.Cryo),
        };
        foreach (var (card, element) in knights)
        {
            Assert.True(VarkaRules.IsKnight(card), card.GetType().Name);
            Assert.Equal(CardType.Skill, card.Type);
            Assert.Equal(CardRarity.Common, card.Rarity);
            Assert.Equal(element, ((ICompanionCard)card).CompanionElement);
            Assert.Equal(VarkaPrototype.CharacterId,
                         ((ICompanionCard)card).PersonalPool);
        }
        Assert.Equal(knights.Select(k => k.Element), VarkaRules.KnightElements);
        // Knights' Muster is a Knight card too; his own Attacks are not.
        Assert.True(VarkaRules.IsKnight(new ProtoVkKnightsMuster()));
        Assert.False(VarkaRules.IsKnight(new ProtoVkWindboundExecution()));
        Assert.False(VarkaRules.IsKnight(new ProtoVkFavoniusDrill()));
    }

    [Fact]
    public void Knights_muster_chooses_a_knight_and_hits_with_their_element()
    {
        var card = new ProtoVkKnightsMuster();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(CardRarity.Basic, card.Rarity);
        Assert.Equal(TargetType.AnyEnemy, card.TargetType);
        Assert.Equal(4m, Var(card, "Damage"));
        Assert.Equal(6m, Var(Upgraded<ProtoVkKnightsMuster>(), "Damage"));
        Assert.Equal("Choose a [gold]Knight[/gold]: deal {Damage:diff()} damage "
                   + "of their element.", Face(card));
        var play = Il.CallSequence(Il.Method("ProtoVkKnightsMuster", "OnPlay"))
            .ToList();
        var choose = play.IndexOf("VarkaRules.ChooseKnight");
        var carry = play.IndexOf("HitElement.Carry");
        var hit = play.IndexOf("DamageCmd.Attack");
        Assert.True(choose >= 0 && carry > choose && hit > carry,
                    string.Join(", ", play));
    }

    [Fact]
    public void The_knight_grid_maps_each_face_to_its_element()
    {
        var faces = new CardModel[]
        {
            new KnightOptionAmber(), new KnightOptionBarbara(),
            new KnightOptionLisa(), new KnightOptionKaeya(),
        };
        for (var i = 0; i < faces.Length; i++)
        {
            Assert.Equal(VarkaRules.KnightElements[i],
                         VarkaRules.ElementOfOption(faces, faces[i]));
        }
        Assert.Equal(Element.None, VarkaRules.ElementOfOption(faces, null));
        // A GRID, because the choose-a-card screen throws on four cards.
        Assert.Contains("CardSelectCmd.FromSimpleGrid",
                        Il.Calls(Il.Method("VarkaRules", "ChooseKnight")));
        Assert.Contains("VarkaRules.ChooseKnight",
                        Il.Calls(Il.Method("VarkaRules", "KnightAura")));
        Assert.Contains("VarkaRules.KnightAura",
                        Il.Calls(Il.Method("ProtoVkFavoniusDrill", "OnPlay")));
    }

    [Fact]
    public void Grand_masters_order_repeats_the_next_knight_this_turn()
    {
        Assert.Contains("VarkaRules.IsKnight",
                        Il.Calls(Il.Method("GrandMastersOrderPower",
                                           "ModifyCardPlayCount")));
        Assert.Contains("PowerCmd.Remove",
                        Il.Calls(Il.Method("GrandMastersOrderPower",
                                           "AfterSideTurnEnd")));
        var card = new ProtoVkGrandMastersOrder();
        Assert.Equal(0, card.EnergyCost.Canonical);
        Assert.Contains(CardKeyword.Exhaust, card.Keywords);
        Assert.DoesNotContain(CardKeyword.Retain, card.Keywords);
        Assert.Contains(CardKeyword.Retain,
                        Upgraded<ProtoVkGrandMastersOrder>().Keywords);
    }

    [Fact]
    public void Roll_call_adds_a_knight_and_chooses_it_upgraded()
    {
        var calls = Il.Calls(Il.Method("ProtoVkKnightsRollCall", "OnPlay"));
        Assert.Contains("VarkaRules.AddKnight", calls);
        Assert.Contains("CardModel.get_IsUpgraded", calls);
        var add = Il.Calls(Il.Method("VarkaRules", "AddKnight"));
        Assert.Contains("CardSelectCmd.FromSimpleGrid", add);
        Assert.Contains("CardEnergyCost.SetThisTurn", add);
    }

    // ---- the starter and the pool ------------------------------------------

    [Fact]
    public void The_starter_is_the_base_pair_the_muster_and_the_ascension()
    {
        var deck = Cards("VarkaRoster", "StartingDeck");
        Assert.Equal(10, deck.Count);
        Assert.Equal(4, deck.Count(c => c == "ModelDb.Card<StrikeSilent>"));
        Assert.Equal(4, deck.Count(c => c == "ModelDb.Card<DefendSilent>"));
        Assert.Single(deck, c => c == "ModelDb.Card<ProtoVkKnightsMuster>");
        Assert.Single(deck, c => c == "ModelDb.Card<ProtoVkFourWindsAscension>");
        Assert.Equal(new[] { "ModelDb.Card<StrikeSilent>" },
                     Cards("VarkaRoster", "StarterStrike"));
        Assert.Equal(new[] { "ModelDb.Card<DefendSilent>" },
                     Cards("VarkaRoster", "StarterDefend"));
        Assert.Contains("ModelDb.Relic",
                        Il.Calls(Il.Method("VarkaRoster", "StartingRelics")));
    }

    [Fact]
    public void The_pool_is_nineteen_cards_ten_seven_and_two()
    {
        var pool = Cards("VarkaRoster", "Pool")
            .Select(c => c.Substring("ModelDb.Card<".Length).TrimEnd('>'))
            .ToList();
        Assert.Equal(19, pool.Count);
        Assert.Equal(19, pool.Distinct().Count());
        var types = typeof(VarkaRules).Assembly.GetTypes()
            .Where(t => pool.Contains(t.Name))
            .Select(t => (CardModel)Activator.CreateInstance(t)!)
            .ToList();
        Assert.Equal(19, types.Count);
        Assert.Equal(10, types.Count(c => c.Rarity == CardRarity.Common));
        Assert.Equal(7, types.Count(c => c.Rarity == CardRarity.Uncommon));
        Assert.Equal(2, types.Count(c => c.Rarity == CardRarity.Rare));
        Assert.Equal(4, types.Count(VarkaRules.IsKnight));
        // The starter's two are not offered.
        Assert.DoesNotContain("ProtoVkKnightsMuster", pool);
        Assert.DoesNotContain("ProtoVkFourWindsAscension", pool);
    }

    [Fact]
    public void Large_capsule_asks_varka_for_his_pair()
    {
        var strike = Il.Calls(Il.Method("ArmStarterBasics", "StrikeFor"));
        Assert.Contains("VarkaRoster.StarterStrike", strike);
        Assert.Contains("VarkaPrototype.get_Enabled", strike);
        Assert.Contains("VarkaRoster.StarterDefend",
                        Il.Calls(Il.Method("ArmStarterBasics", "DefendFor")));
    }

#if VARKA_PROTOTYPE
    // ---- the character (compiled only with -p:VarkaPrototype=true) ----------

    [Fact]
    public void Varka_is_eighty_hp_ninety_nine_gold_and_he()
    {
        var varka = new Varka();
        Assert.Equal(80, varka.StartingHp);
        Assert.Equal(99, varka.StartingGold);
        Assert.Equal(MegaCrit.Sts2.Core.Entities.Characters.CharacterGender.Masculine,
                     varka.Gender);
        var loc = varka.Localization!.ToDictionary(r => r.Item1, r => r.Item2);
        Assert.Equal("Varka", loc["title"]);
        Assert.Equal("he", loc["pronounSubject"]);
        Assert.Equal("him", loc["pronounObject"]);
        Assert.Equal("his", loc["possessiveAdjective"]);
        Assert.IsAssignableFrom<IVarkaCharacter>(varka);
        Assert.Contains("VarkaRoster.StartingDeck",
                        Il.Calls(Il.Method("Varka", "get_StartingDeck")));
        Assert.Contains("VarkaRoster.StartingRelics",
                        Il.Calls(Il.Method("Varka", "get_StartingRelics")));
    }

    [Fact]
    public void He_is_a_roster_character_from_mondstadt()
    {
        var seat = Seat.Varka();
        Assert.Equal("varka", CompanionPool.CharacterId(seat.Player));
        Assert.Equal("mondstadt", CompanionPool.HomeNation(seat.Player));
        Assert.True(VarkaPrototype.IsVarka(seat.Creature));
        Assert.False(VarkaPrototype.IsVarka(Seat.Klee().Creature));
    }

    [Fact]
    public void His_pool_offers_the_nineteen_and_holds_the_rest()
    {
        Assert.Contains("VarkaRoster.Pool",
                        Il.Calls(Il.Method("VarkaCardPool", "FilterThroughEpochs")));
        var members = Il.Calls(Il.Method("VarkaCardPool", "GenerateAllCards"));
        Assert.Contains("VarkaRoster.Members", members);
        Assert.Contains("VarkaModalOptions.get_All", members);
        Assert.Contains("ModelDb.Relic",
                        Il.Calls(Il.Method("VarkaRelicPool", "GenerateAllRelics")));
    }
#endif
}
