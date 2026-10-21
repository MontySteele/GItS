using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI REVIEW, ROUND 6 (2026-10-14,
/// <c>review/active/kokomi-review-r6-2026-10-14.md</c>, section 3 and picks
/// 1 (a), 2 (b), 3 (a); [USER]: "2,3,4) Good with the defaults, other than
/// the first question." Then, on pick 1: "Let's go with (a)."). The mod's
/// halves: the numbers, Sea Glass Harvest's Discard Pile, Mend's cap on the
/// face, the two Hydro sources in the cut Powers' slots, Read the Field's
/// free card, the wire's two new queue fields and the strip's warning, and
/// the Kelp Wall check (only an Attack's blocked damage counts). Sim and
/// page twin: <c>tier0/tests/test_kokomi_review_r6_2026_10_14.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiReviewR6Tests
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

    private static List<string> Slice() =>
        Il.CallSequence(Il.Method("KokomiOverhaulRoster", "Slice"))
            .Where(c => c.StartsWith("ModelDb.Card", StringComparison.Ordinal))
            .Select(c => c.Substring(c.IndexOf('<') + 1).TrimEnd('>'))
            .ToList();

    // ---- items 1-5 -------------------------------------------------------------

    [Fact]
    public void The_numbers_pass()
    {
        Assert.Equal((8, 11), Vars<ProtoKkWatatsumiDrill>("Damage"));   // the pool sweep, 2026-10-18
        Assert.Equal((5, 6), Vars<ProtoKkKuragesWake>("Damage"));
        Assert.Equal((5, 7), Vars<ProtoKkWatchfulShoal>("PowerAmount"));
        Assert.Equal((6, 8), Vars<ProtoKkGrandStrategist>("PowerAmount"));
        Assert.Equal((8, 11), Vars<ProtoKkTidalRiposte>("PowerAmount"));
    }

    // ---- item 6 ------------------------------------------------------------------

    [Fact]
    public void Sea_glass_harvest_reads_the_hand_only()
    {
        // Item 6 had it read the hand, draw pile and discard pile; the Kokomi
        // balance audit (ruled 2026-10-21) cut it back to the hand: one read.
        var reads = Il.CallSequence(
                Il.Method("KokomiStatusBatch", "TransformStatuses"))
            .Count(c => c.Contains("KokomiStatusBatch.PileStatuses"));
        Assert.Equal(1, reads);
        Assert.Contains(
            "Transform every Status and Curse in your [gold]Hand[/gold]",
            Face(new ProtoKkSeaGlassHarvest()));
    }

    // ---- pick 1 (a) ----------------------------------------------------------------

    [Fact]
    public void Mend_prints_what_will_land_on_all_three_cards()
    {
        foreach (var card in new CardModel[] { new ProtoKkTheMoonAShip(),
                                               new ProtoKkKuragesMercy(),
                                               new ProtoMiMizukiAnraku() })
        {
            Assert.IsType<MendLandsVar>(card.DynamicVars[MendLandsVar.Token]);
            Assert.Contains("{MendLands} will land", Face(card));
        }
        // One cap: Mend heals what the preview reads.
        Assert.Contains(Calls("KokomiRules", "Mend"),
                        c => c.Contains("KokomiRules.MendWouldLand"));
        Assert.Contains(Calls("MendLandsVar", "UpdateCardPreview"),
                        c => c.Contains("KokomiRules.MendWouldLand"));
    }

    // ---- pick 2 (b) ----------------------------------------------------------------

    [Fact]
    public void Two_hydro_sources_take_the_cut_powers_slots()
    {
        var slice = Slice();
        Assert.Equal(79, slice.Count); // Kokomi v3 (2026-10-18): Unbroken Tide
        Assert.DoesNotContain("ProtoKkJellyfishCurrent", slice);
        Assert.DoesNotContain("ProtoKkCoordinatedTide", slice);
        Assert.Contains("ProtoKkKurageVanguard", slice);
        Assert.Contains("ProtoKkFollowingCurrent", slice);
        foreach (var card in new CardModel[] { new ProtoKkKurageVanguard(),
                                               new ProtoKkFollowingCurrent() })
        {
            Assert.Equal((CardType.Power, CardRarity.Uncommon, 1),
                         (card.Type, card.Rarity, card.EnergyCost.Canonical));
        }
        Assert.Equal((4, 6), Vars<ProtoKkKurageVanguard>("PowerAmount"));
        Assert.Equal((4, 5), Vars<ProtoKkFollowingCurrent>("PowerAmount"));
    }

    /// <summary>The Kokomi boss ramp (2026-10-21, [USER]: "Got it, let's
    /// try that"): "It deals 2 more each turn." The power's Amount is the
    /// next hit and grows by 2 after each trigger.</summary>
    [Fact]
    public void Kurage_vanguard_ramps_2_a_turn()
    {
        Assert.Equal(2, KurageVanguardPower.Growth);
        Assert.Equal(new[] { 4, 6, 8 },
            Enumerable.Range(0, 3).Select(t => KurageVanguardPower.HitAfter(4, t)));
        Assert.Equal(new[] { 6, 8, 10 },
            Enumerable.Range(0, 3).Select(t => KurageVanguardPower.HitAfter(6, t)));
        Assert.Equal((4, 6), Vars<ProtoKkKurageVanguard>("PowerAmount"));
        Assert.EndsWith("It deals 2 more each turn.",
                        Face(new ProtoKkKurageVanguard()));
        var power = new KurageVanguardPower().Localization!
            .First(r => r.Item1 == "description").Item2;
        Assert.Equal(
            "At the start of your turn, the [gold]Bake-Kurage[/gold] deals "
          + "[blue]{Amount}[/blue] [gold]Hydro[/gold] damage. It deals 2 "
          + "more each turn.", power);
        var signal = Il.CallSequence(
            Il.Method("KurageVanguardPower", "Signal")).ToList();
        var hit = signal.FindIndex(c => c.Contains("KurageHydroSources.Hit"));
        var grow = signal.FindIndex(c => c.Contains("PowerCmd.ModifyAmount"));
        Assert.True(hit >= 0 && hit < grow);
    }

    [Fact]
    public void The_sources_hit_the_front_enemy_for_hydro_at_their_moments()
    {
        var hit = Calls("KurageHydroSources", "Hit");
        Assert.Contains(hit, c => c.Contains("KokomiPlan.FrontEnemy"));
        Assert.Contains(hit, c => c.Contains("ElementalHit.Deal"));
        var morning = Il.CallSequence(
            Il.Method("ProtoBakeKuragePower", "AfterPlayerTurnStart")).ToList();
        var vanguard = morning.FindIndex(
            c => c.Contains("KurageVanguardPower.Signal"));
        var dawn = morning.FindIndex(c => c.Contains("DawnTidePower.Signal"));
        var plans = morning.FindIndex(c => c.Contains("KokomiPlan.ResolveAll"));
        Assert.True(plans >= 0 && plans < vanguard && vanguard < dawn);
        Assert.Contains(Calls("KokomiRefounding", "OnCarriedOut"),
                        c => c.Contains("FollowingCurrentPower.OnCarriedOut"));
    }

    // ---- pick 3 (a) ----------------------------------------------------------------

    [Fact]
    public void Read_the_fields_card_costs_0_this_turn()
    {
        Assert.Contains(Calls("KokomiPlan", "DrawPileToHand"),
                        c => c.Contains("SetThisTurn"));
        // The Kokomi upgrade pass (2026-10-19): 0 on both faces; the
        // upgrade adds a draw.
        Assert.EndsWith("It costs 0 this turn.{IfUpgraded:show: Draw 1 card.|}",
                        Face(new ProtoKkReadTheField()));
    }

    // ---- items 7 and 11: the wire --------------------------------------------------

    [Fact]
    public void The_queue_row_carries_the_attack_reading_and_the_card_type()
    {
        var keys = Il.Strings(Il.Method("KokomiPlan", "QueueRow"));
        Assert.Contains("needs_attack", keys);
        Assert.Contains("attack", keys);
        Assert.Equal("No enemy intends to attack", KokomiPlan.NoAttackIntended);
        Assert.Contains(Calls("KokomiPlan", "LiveLine"),
                        c => c.Contains("KokomiPlan.AnyEnemyIntendsAttack"));
    }

    // ---- item 12: Kelp Wall ----------------------------------------------------------

    [Fact]
    public void Only_an_attacks_blocked_damage_moves_kelp_walls_count()
    {
        var ledger = new KokomiOverhaulLedger();
        ledger.NoteEnemyHit("1", blocked: 5, unblocked: 0, attack: false);
        Assert.Equal((0, 5), (ledger.DamageBlockedTotal,
                              ledger.DamageTakenTotal));
        ledger.NoteEnemyHit("1", blocked: 4, unblocked: 0, attack: true);
        Assert.Equal(4, ledger.DamageBlockedTotal);
        Assert.Contains("the Attack damage you blocked",
                        Face(new ProtoKkKelpWall()));
    }
}
