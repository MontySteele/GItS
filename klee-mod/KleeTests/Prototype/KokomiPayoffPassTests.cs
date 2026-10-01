using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI PAYOFF PASS (2026-10-01). The main session recommended cutting
/// Second Thoughts ("an undo button, and an undo is a dead draw") alongside a
/// Plan-volume payoff that is not damage; [USER]: "Sounds good! Please
/// proceed!" Kurage Canopy (Block per carry-out) and Coral Tithe (the Casket
/// into Energy and cards) join the pool, which is 70. What awaits a command is
/// pinned off the compiled methods. Sim twin:
/// <c>tier0/tests/test_kokomi_payoff_pass.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiPayoffPassTests : IDisposable
{
    private readonly bool _kokomi = KokomiOverhaul.Enabled;

    public KokomiPayoffPassTests() => KokomiOverhaul.Enabled = true;

    public void Dispose() => KokomiOverhaul.Enabled = _kokomi;

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    // ---- the offer -------------------------------------------------------

    [Fact]
    public void The_offer_is_seventy_ending_with_the_two_and_without_second_thoughts()
    {
        var slice = Seq("KokomiOverhaulRoster", "Slice")
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
            .ToList();
        Assert.Equal(70, slice.Count);
        Assert.Equal(new[] { "ProtoKkKurageCanopy", "ProtoKkCoralTithe" },
                     slice.Skip(68).ToArray());
        Assert.DoesNotContain(slice, c => c.Contains("SecondThoughts"));
        Assert.Null(typeof(ProtoKkNip).Assembly.GetType(
            "KleeMod.Cards.Prototype.Generated.ProtoKkSecondThoughts"));
        // All Streams' give-back is the door the cut card shared; it stays.
        Assert.Contains(Seq("KokomiPlan", "CancelAllForNext"),
                        c => c.Contains("KokomiPlan.GiveBack"));
    }

    // ---- Kurage Canopy -------------------------------------------------------

    [Fact]
    public void Kurage_canopy_is_a_one_cost_uncommon_power_of_two_block_three_upgraded()
    {
        var card = new ProtoKkKurageCanopy();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Power, card.Type);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.Equal(2, card.DynamicVars["PowerAmount"].IntValue);
        var up = Upgraded<ProtoKkKurageCanopy>();
        Assert.Equal(3, up.DynamicVars["PowerAmount"].IntValue);
        Assert.Equal(1, up.EnergyCost.Canonical);
        Assert.Contains("carries out a [gold]Plan[/gold]", Face(card));
        Assert.Contains(Seq("ProtoKkKurageCanopy", "OnPlay"),
                        c => c.Contains("KurageCanopyPower"));
    }

    [Fact]
    public void Kurage_canopy_rides_the_plan_bus_once_per_carry_out()
    {
        // The bus rings from ResolveEntry, which is ONE carry-out; the drain
        // calls it `times` times (Second Wave, Nereid's Ascension, All
        // Streams' gift), so a doubled carry-out pays twice.
        Assert.True(typeof(IKokomiPlanListener)
            .IsAssignableFrom(typeof(KurageCanopyPower)));
        var hook = Seq("KurageCanopyPower", "OnPlanResolved");
        Assert.Contains("CreatureCmd.GainBlock", hook);
        Assert.DoesNotContain(hook,
            c => c.Contains("KokomiOverhaulLedger.ClaimOncePerTurn"));
        Assert.Contains("IKokomiPlanListener.OnPlanResolved",
                        Seq("KokomiPlan", "ResolveEntry"));
        var drain = Seq("KokomiPlan", "Drain");
        var times = drain.FindIndex(c => c.Contains("KokomiPlan.CarryOutTimes"));
        var resolve = drain.FindIndex(c => c.Contains("KokomiPlan.ResolveEntry"));
        Assert.True(times >= 0 && resolve > times,
                    "the drain must carry an entry out `times` times");
        Assert.Contains(drain, c => c.Contains("Entry.get_Extra"));
    }

    // ---- Coral Tithe ---------------------------------------------------------

    [Fact]
    public void Coral_tithe_is_a_zero_cost_uncommon_skill_every_three_then_two()
    {
        var card = new ProtoKkCoralTithe();
        Assert.Equal(0, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.Equal(3, card.DynamicVars["KkAmount"].IntValue);
        Assert.Equal(2, Upgraded<ProtoKkCoralTithe>().DynamicVars["KkAmount"].IntValue);
        Assert.Contains(Seq("ProtoKkCoralTithe", "OnPlay"),
                        c => c.Contains("KokomiCards.CoralTithe"));
    }

    [Theory]
    [InlineData(0, 3, 0)]
    [InlineData(3, 3, 1)]
    [InlineData(7, 3, 2)]
    [InlineData(0, 2, 0)]
    [InlineData(3, 2, 1)]
    [InlineData(7, 2, 3)]
    public void Coral_tithe_pays_one_for_every_n_rounded_down(int points, int per, int paid)
    {
        Assert.Equal(paid, KokomiCards.CoralTithePaid(points, per));
    }

    [Fact]
    public void Coral_tithe_reads_the_casket_the_relics_way_then_empties_and_pays()
    {
        var calls = Seq("KokomiCards", "CoralTithe");
        var relic = calls.FindIndex(c => c.Contains("GetRelic"));
        var empty = calls.FindIndex(c => c.Contains("KokomiOverhaulLedger.EmptyCasket"));
        var paid = calls.FindIndex(c => c.Contains("KokomiCards.CoralTithePaid"));
        var energy = calls.FindIndex(c => c.Contains("PlayerCmd.GainEnergy"));
        var draw = calls.FindIndex(c => c.Contains("CardPileCmd.Draw"));
        Assert.True(relic >= 0 && empty > relic && paid > empty
                    && energy > paid && draw > energy);
    }

    [Fact]
    public void Coral_tithe_does_nothing_without_a_casket_and_empties_one_below_three()
    {
        // No Casket: the count is not touched.
        KokomiOverhaulLedger.ResetAll();
        var bare = Seat.Kokomi();
        KokomiOverhaulLedger.For(bare.Creature).AddToCasket(7);
        var card = new ProtoKkCoralTithe();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", bare.Player);
        Assert.True(KokomiCards.CoralTithe(null!, card, null!).IsCompleted);
        Assert.Equal(7, KokomiOverhaulLedger.For(bare.Creature).CasketCount);

        // The Watatsumi Casket (the Orobas upgrade) is a Tamakushi Casket: an
        // empty count runs to the end and pays nothing.
        KokomiOverhaulLedger.ResetAll();
        var seat = Seat.Kokomi().WithRelic<WatatsumiCasket>();
        var held = new ProtoKkCoralTithe();
        Seat.Set(held, "IsMutable", true);
        Seat.Set(held, "Owner", seat.Player);
        Assert.True(KokomiCards.CoralTithe(null!, held, null!).IsCompleted);
        Assert.Equal(0, KokomiOverhaulLedger.For(seat.Creature).CasketCount);
    }
}
