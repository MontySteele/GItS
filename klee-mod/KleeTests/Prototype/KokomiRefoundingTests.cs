using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI RE-FOUNDING (2026-10-12): the direction in
/// <c>review/ruled/kokomi-design-pass-2026-10-11.md</c>, the cards in
/// <c>review/ruled/kokomi-card-paper-2026-10-12.md</c>. The Casket's count,
/// Open the Casket and Dusk are retired; the relic is Block while a Plan
/// waits; Stings and Wards are her jellyfish; any Companion card can be
/// written as a Plan.
///
/// Headless: pure functions run for real, anything that awaits a command is
/// pinned off the compiled method's call order. The behaviours are the sim's,
/// <c>tier0/tests/test_kokomi_refounding.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiRefoundingTests
{
    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    // ---- the relic ---------------------------------------------------------

    [Fact]
    public void The_casket_is_1_block_a_play_and_the_upgrade_2()
    {
        // Ward and Casket (2026-10-18, [USER]: "if we allow for Sting and
        // Ward to count, is that a real problem? ... (possibly bringing it
        // down to 1 per card played)").
        Assert.Equal(1, KokomiOverhaulLaw.CasketBlock);
        Assert.Equal(1, new TamakushiCasket().Block);
        Assert.Equal(2, new WatatsumiCasket().Block);
        Assert.Equal(2, WatatsumiCasket.WatatsumiBlock);
        // 2026-10-20: it pays for planning, not for any Plan card.
        Assert.Equal(
            "Whenever you [gold]Plan[/gold] a card or play a Companion, gain "
            + "[blue]1[/blue] [gold]Block[/gold].",
            new TamakushiCasket().Localization!
                .First(r => r.Item1 == "description").Item2);
        Assert.Equal(
            "Whenever you [gold]Plan[/gold] a card or play a Companion, gain "
            + "[blue]2[/blue] [gold]Block[/gold].",
            new WatatsumiCasket().Localization!
                .First(r => r.Item1 == "description").Item2);
    }

    [Fact]
    public void The_casket_pays_for_a_planned_card_or_a_companion()
    {
        // 2026-10-20, [USER]: "2 was definitely the intent, and we should
        // figure out a different Block solution if needed." Option 2: "Pay
        // only when a card is Planned or a Companion is played."
        var kokomi = Seat.Kokomi();
        var pet = Kurage();
        // Planned onto the Bake-Kurage: a Plan card, a Plan-line Companion
        // (one bool, so it pays once), a Sting and a Ward.
        foreach (var card in new CardModel[] {
                     new ProtoKkSteadyTide(), new ProtoMiGorouInuzaka(),
                     new ProtoKkSting(), new ProtoKkWard() })
        {
            Assert.True(TamakushiCasket.Counts(
                            Play(Owned(card, kokomi), kokomi, pet),
                            kokomi.Creature),
                        card.GetType().Name);
        }
        // Face-up: a Companion pays, with or without a Plan line.
        foreach (var card in new CardModel[] {
                     new ProtoMiShinobuThundergrust(), new ProtoMiGorouInuzaka() })
        {
            Assert.True(TamakushiCasket.Counts(Play(Owned(card, kokomi), kokomi),
                                               kokomi.Creature),
                        card.GetType().Name);
        }
        // Face-up: a Plan card, a Sting and a Ward pay nothing.
        foreach (var card in new CardModel[] {
                     new ProtoKkSteadyTide(), new ProtoKkSting(),
                     new ProtoKkWard() })
        {
            Assert.False(TamakushiCasket.Counts(Play(Owned(card, kokomi), kokomi),
                                                kokomi.Creature),
                         card.GetType().Name);
        }
        // Not her Strike or Defend, and not on anyone else.
        Assert.False(TamakushiCasket.Counts(Play(Owned(
            new MegaCrit.Sts2.Core.Models.Cards.StrikeSilent(), kokomi), kokomi),
            kokomi.Creature));
        Assert.False(TamakushiCasket.Counts(Play(Owned(
            new MegaCrit.Sts2.Core.Models.Cards.DefendSilent(), kokomi), kokomi),
            kokomi.Creature));
        var klee = Seat.Klee();
        Assert.False(TamakushiCasket.Counts(Play(Owned(
            new ProtoKkSteadyTide(), klee), klee, pet), klee.Creature));
    }

    [Fact]
    public void The_casket_pays_nothing_for_a_plan_carried_out()
    {
        var kokomi = Seat.Kokomi();
        var carrying = (HashSet<MegaCrit.Sts2.Core.Entities.Players.Player>)
            typeof(KokomiPlan).GetField("_carrying", HeadlessGame.All)!
                .GetValue(null)!;
        var play = Play(Owned(new ProtoKkSteadyTide(), kokomi), kokomi, Kurage());
        Assert.True(TamakushiCasket.Counts(play, kokomi.Creature));
        carrying.Add(kokomi.Player);
        try
        {
            Assert.False(TamakushiCasket.Counts(play, kokomi.Creature));
        }
        finally
        {
            carrying.Remove(kokomi.Player);
        }
    }

    [Fact]
    public void The_casket_pays_raw_block_when_the_play_counts()
    {
        // 2026-10-20: the test asks whether the play went onto the
        // Bake-Kurage, and whether it is a carry-out.
        var hook = Seq(nameof(TamakushiCasket), "AfterCardPlayed");
        var counts = hook.IndexOf("TamakushiCasket.Counts");
        var block = hook.IndexOf("CreatureCmd.GainBlock");
        Assert.True(counts >= 0 && block > counts, string.Join(" ", hook));
        var test = Seq(nameof(TamakushiCasket), "Counts");
        Assert.Contains("KokomiPlan.IsCarryingOut", test);
        Assert.Contains("KokomiPlan.PlayedOnPet", test);
        // The start-of-turn Block is gone.
        Assert.Null(typeof(TamakushiCasket).GetMethod("AfterBlockCleared",
            System.Reflection.BindingFlags.Public
            | System.Reflection.BindingFlags.Instance
            | System.Reflection.BindingFlags.DeclaredOnly));
    }

    private static T Owned<T>(T card, Seat owner) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", owner.Player);
        return card;
    }

    /// <summary>A bare Bake-Kurage, enough for <c>BakeKuragePet.Is</c>.</summary>
    private static MegaCrit.Sts2.Core.Entities.Creatures.Creature Kurage()
    {
        var ctor = typeof(MegaCrit.Sts2.Core.Entities.Creatures.Creature)
            .GetConstructors(HeadlessGame.All)
            .First(c => c.GetParameters().Length == 3
                        && c.GetParameters()[0].ParameterType
                           == typeof(MegaCrit.Sts2.Core.Entities.Players.Player));
        var pet = (MegaCrit.Sts2.Core.Entities.Creatures.Creature)
            ctor.Invoke(new object?[] { null, 10, 10 });
        Seat.Force(pet, "Monster",
            System.Runtime.CompilerServices.RuntimeHelpers
                .GetUninitializedObject(typeof(BakeKurageMonster)));
        return pet;
    }

    private static MegaCrit.Sts2.Core.Entities.Cards.CardPlay Play(
        CardModel card, Seat by,
        MegaCrit.Sts2.Core.Entities.Creatures.Creature? target = null) => new()
    {
        Card = card,
        Player = by.Player,
        Target = target,
        ResultPile = PileType.Discard,
        Resources = default,
        IsAutoPlay = false,
        PlayIndex = 0,
        PlayCount = 1,
    };

    // ---- the jellyfish -----------------------------------------------------

    [Fact]
    public void Sting_and_ward_are_ethereal_exhausting_zero_cost_tokens()
    {
        // Cost 0 since the jellyfish build (2026-10-12), with their Plan
        // lines (`KokomiJellyfishBuildTests`).
        foreach (var card in new CardModel[] { new ProtoKkSting(),
                                               new ProtoKkWard() })
        {
            Assert.Equal(0, card.EnergyCost.Canonical);
            Assert.Equal(CardRarity.Token, card.Rarity);
            Assert.Contains(CardKeyword.Ethereal, card.CanonicalKeywords);
            Assert.Contains(CardKeyword.Exhaust, card.CanonicalKeywords);
        }
    }

    // ---- Companions as Plans -----------------------------------------------
    //
    // Kokomi review r9 pick 1 (a), 2026-10-15; [USER]: "let's get rid of
    // Companions as Plans unless we make a card that specifically has a Plan
    // line." The re-founding's general rule (any Companion card can be
    // written) is gone: a Companion is planned only through a Plan line it
    // prints, on the Plan path every Plan card takes.

    [Fact]
    public void A_companion_with_no_plan_line_cannot_be_planned()
    {
        foreach (var card in new CardModel[]
                 { new ProtoMiShinobuThundergrust(), new ProtoMiShinobuGrassRing(),
                   new ProtoMiChioriHasode() })
        {
            // (Kirara left this list in the Inazuma pool rework, 2026-10-18:
            // she prints a Plan line now.)
            var name = card.GetType().Name;
            Assert.IsAssignableFrom<global::KleeMod.Cards.ICompanionCard>(card);
            Assert.False(card is IPlannedCard, name);
            Assert.False(KokomiRefounding.CanBeWritten(card), name);
            // No target override, so the Bake-Kurage refuses it as it
            // refuses any card with no Plan line, and its play never asks
            // whether it was dropped on the jellyfish.
            Assert.NotEqual(card.GetType(),
                            card.GetType().GetProperty("TargetType")!.DeclaringType);
            Assert.DoesNotContain(Il.Calls(Il.Method(name, "OnPlay")),
                                  c => c.Contains("PlayedOnPet")
                                       || c.Contains("KokomiCompanionPlan"));
        }
        // The rule's machinery left with it.
        var asm = typeof(KokomiCompanionPlan).Assembly;
        Assert.Null(asm.GetType("KleeMod.Powers.IWritableCompanion"));
        foreach (var gone in new[] { "Write", "CarryOut", "TargetFor",
                                     "OnKokomi", "AimsAtAnEnemy" })
        {
            Assert.Null(typeof(KokomiCompanionPlan).GetMethod(gone));
        }
        Assert.DoesNotContain("PlayCompanion",
                              System.Enum.GetNames(typeof(KokomiPlan.Kind)));
    }

    [Fact]
    public void A_companion_that_prints_a_plan_line_is_still_planned_by_it()
    {
        // Gorou's Inuzaka: "Plan: Gain 11 Block" (the sim twin carries it out:
        // test_gorou_inuzaka_written_carries_out_its_own_plan_line).
        var gorou = new ProtoMiGorouInuzaka();
        Assert.IsAssignableFrom<global::KleeMod.Cards.ICompanionCard>(gorou);
        Assert.True(KokomiRefounding.CanBeWritten(gorou));
        var plan = Assert.Single(((IPlannedCard)gorou).PlanClauses);
        Assert.Equal(KokomiPlan.Kind.Block, plan.Kind);
        Assert.Equal(KokomiPlan.Aim.Self, plan.Aim);
        // Its play writes its own Plan line on the jellyfish.
        var seq = Seq(nameof(ProtoMiGorouInuzaka), "OnPlay");
        var onPet = seq.FindIndex(c => c.Contains("KokomiPlan.PlayedOnPet"));
        var schedule = seq.FindIndex(c => c.Contains("KokomiPlan.Schedule"));
        Assert.True(onPet >= 0 && schedule > onPet, string.Join(" ", seq));
        Assert.False(KokomiRefounding.CanBeWritten(new ProtoKkEveningWatch()));
    }

    [Fact]
    public void A_generated_companion_is_ethereal_and_exhausts()
    {
        var seq = Seq(nameof(KokomiCompanionPlan), "Generate");
        Assert.Equal(2, seq.Count(c => c == "CardModel.AddKeyword"));
    }

    [Fact]
    public void Grand_designs_free_write_is_the_one_auto_play_that_writes()
    {
        Assert.Contains("KokomiRefounding.IsFreeWrite",
                        Seq(nameof(KokomiPlan), "PlayedOnPet"));
        Assert.Contains("CardCmd.AutoPlay",
                        Seq(nameof(KokomiRefounding), "WriteFree"));
    }

    [Fact]
    public void Call_the_generals_offers_three_on_a_skippable_screen()
    {
        Assert.Equal(3, KokomiCompanionPlan.GeneralsOffered);
        var seq = Seq(nameof(KokomiCards), "CallTheGenerals");
        Assert.Contains("KokomiCompanionPlan.Generated", seq);
        Assert.Contains("CardSelectCmd.FromChooseACardScreen", seq);
    }

    // ---- turn order --------------------------------------------------------

    [Fact]
    public void Dawn_tide_lays_its_hydro_after_the_morning_plans()
    {
        var seq = Seq(nameof(ProtoBakeKuragePower), "AfterPlayerTurnStart");
        var resolve = seq.IndexOf("KokomiPlan.ResolveAll");
        var dawn = seq.IndexOf("DawnTidePower.Signal");
        Assert.True(resolve >= 0 && dawn > resolve, string.Join(" ", seq));
    }

    [Fact]
    public void Dusk_and_the_casket_count_are_gone()
    {
        var types = typeof(TamakushiCasket).Assembly.GetTypes()
            .Select(t => t.Name).ToHashSet();
        Assert.DoesNotContain("OpenTheCasket", types);
        Assert.DoesNotContain("FirstCardFreePower", types);
        Assert.DoesNotContain("ProtoKkFloodTide", types);
        Assert.Null(typeof(ProtoBakeKuragePower).GetMethod(
            "BeforeSideTurnEnd",
            System.Reflection.BindingFlags.DeclaredOnly
            | System.Reflection.BindingFlags.Public
            | System.Reflection.BindingFlags.Instance));
    }
}
