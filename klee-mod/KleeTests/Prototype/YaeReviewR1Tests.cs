using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// YAE REVIEW R1 (Claude, 2026-10-14, no pick;
/// <c>review/active/yae-design-axes-2026-10-14.md</c>, the dated note):
/// a "Rite: X" card says what the shrine would do under X, summed over the
/// Sakura standing, and the Rite badge says it for the current Rite; every
/// Tenko card says "(no Sakura)" while none stands; Sakura Seal costs 0 (upgrade: Edit 2 cards); Kitsune Rite
/// is "Tenko. Draw 1 card." The suite is headless, so the words and sums
/// are pinned by value and the wiring off the compiled members. The sim half
/// is <c>tier0/tests/test_yae_review_r1.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeReviewR1Tests : IDisposable
{
    public YaeReviewR1Tests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose()
    {
        YaeShrineLedger.ResetAll();
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    // ==== 1. the Rite clause ================================================

    [Fact]
    public void The_rite_clause_names_the_sum_in_each_rites_words()
    {
        Assert.Equal(" (your Sakura: 12 damage)", YaeShrineFace.RiteWords(YaeRite.Thunder, 12));
        Assert.Equal(" (your Sakura: 5 Block)", YaeShrineFace.RiteWords(YaeRite.Warding, 5));
        Assert.Equal(" (your Sakura: 2 to ALL)", YaeShrineFace.RiteWords(YaeRite.Wildfire, 2));
        Assert.Equal(" (your Sakura: draw 3)", YaeShrineFace.RiteWords(YaeRite.Offering, 3));
        // No Sakura standing: no clause.
        Assert.Equal("", YaeShrineFace.RiteWords(YaeRite.Warding, 0));
    }

    [Fact]
    public void The_sum_is_each_sakuras_strike_under_that_rite()
    {
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        for (var i = 0; i < 3; i++) ledger.Plant(YaeLaw.PlantLevel, YaeLaw.LevelCap);
        // Levels 3, 2, 1.
        Assert.Equal(12, YaeShrineFace.Total(ledger.Standing, YaeRite.Thunder, 0, 0));
        Assert.Equal(12, YaeShrineFace.Total(ledger.Standing, YaeRite.Warding, 0, 0));
        Assert.Equal(6, YaeShrineFace.Total(ledger.Standing, YaeRite.Wildfire, 0, 0));
        Assert.Equal(3, YaeShrineFace.Total(ledger.Standing, YaeRite.Offering, 0, 0));
        // Grove sizes three Rites and not Offering, as the strike does.
        Assert.Equal(12 + 3 * 2, YaeShrineFace.Total(ledger.Standing, YaeRite.Thunder, 2, 0));
        Assert.Equal(3, YaeShrineFace.Total(ledger.Standing, YaeRite.Offering, 2, 1));
    }

    [Fact]
    public void Off_a_fight_the_clauses_are_empty()
    {
        Assert.Equal("", YaeShrineFace.RiteLine(new ProtoYmShrineMaidensGuard(), YaeRite.Warding));
        Assert.Equal("", YaeShrineFace.RiteLine(null, YaeRite.Thunder));
        Assert.Equal("", YaeShrineFace.TenkoLine(new ProtoYmThunderRite()));
        Assert.Equal("", YaeShrineFace.TenkoLine(null));
    }

    [Fact]
    public void The_clauses_read_the_strike_size_and_the_shrine()
    {
        Assert.Contains(Il.Calls(Il.Method("YaeShrineFace", "RiteLine")),
                        c => c.Contains("YaeShrineFace.Total"));
        Assert.Contains(Il.Calls(Il.Method("YaeShrineFace", "TenkoLine")),
                        c => c.Contains("YaeShrine.Count"));
        Assert.Equal(" (no Sakura)", YaeShrineFace.NoSakura);
    }

    [Fact]
    public void Every_rite_card_carries_the_clause_after_the_rites_name()
    {
        foreach (var (card, rite) in new (CardModel, string)[]
                 {
                     (new ProtoYmThunderRite(), "Thunder"),
                     (new ProtoYmShrineMaidensGuard(), "Warding"),
                     (new ProtoYmFoxfireSweep(), "Wildfire"),
                     (new ProtoYmKitsuneGuile(), "Wildfire"),
                     (new ProtoYmManuscriptPile(), "Offering"),
                 })
        {
            Assert.Contains($"[gold]Rite[/gold]: {rite}{{InCombat:{{{YaeShrineFace.RiteToken}}}|}}",
                            Face(card));
            Assert.Contains(Il.Calls(Il.Method(card.GetType().Name, "AddExtraArgsToDescription")),
                            c => c.Contains("YaeShrineFace.RiteLine"));
        }
    }

    [Fact]
    public void The_rite_badge_says_the_same_for_the_current_rite()
    {
        Assert.Equal(" Your Sakura now: {Total} Block.", YaeRiteText.Now(YaeRite.Warding));
        Assert.Equal(" Your Sakura now: {Total} damage.", YaeRiteText.Now(YaeRite.Thunder));
        Assert.Equal(" Your Sakura now: {Total} to ALL.", YaeRiteText.Now(YaeRite.Wildfire));
        Assert.Equal(" Your Sakura now: draw {Total}.", YaeRiteText.Now(YaeRite.Offering));
        var loc = ((WardingRitePower)System.Runtime.CompilerServices.RuntimeHelpers
            .GetUninitializedObject(typeof(WardingRitePower))).Localization!;
        Assert.Contains(loc, r => r.Item1 == YaeRiteBadgePower.LiveKey
                                  && r.Item2.EndsWith("Your Sakura now: {Total} Block.",
                                                      StringComparison.Ordinal));
        Assert.Contains(loc, r => r.Item1 == "smartDescription"
                                  && !r.Item2.Contains("{Total}"));
        Assert.Contains(Il.Calls(Il.Method("SakuraBadge", "Sync")),
                        c => c.Contains("YaeRiteBadgePower.Refresh"));
    }

    // ==== 2. Tenko with no Sakura ===========================================

    [Fact]
    public void Every_tenko_card_says_no_sakura_and_none_is_gated()
    {
        // The coordinator dropped Kitsune Rite's gate (2026-10-14): it is
        // playable with no Sakura and says "Tenko (no Sakura)" like the rest.
        foreach (var card in new CardModel[]
                 {
                     new ProtoYmKitsuneRite(), new ProtoYmThunderRite(),
                     new ProtoYmMikageThunder(), new ProtoYmTenkoKenshin(),
                 })
        {
            Assert.Contains($"[gold]Tenko[/gold]{{InCombat:{{{YaeShrineFace.TenkoToken}}}|}}",
                            Face(card));
            Assert.Contains(Il.Calls(Il.Method(card.GetType().Name, "AddExtraArgsToDescription")),
                            c => c.Contains("YaeShrineFace.TenkoLine"));
            Assert.False(typeof(IUnplayableReasonCard).IsAssignableFrom(card.GetType()));
        }
    }

    // ==== 3. Sakura Seal, 0 Energy ==========================================

    [Fact]
    public void Sakura_seal_costs_0_and_its_upgrade_edits_two_cards()
    {
        var seal = new ProtoYmSakuraSeal();
        Assert.Equal(0, seal.EnergyCost.Canonical);
        Assert.Equal(1, (int)seal.DynamicVars["YmAmount"].BaseValue);
        var upgrade = Il.Calls(Il.Method("ProtoYmSakuraSeal", "OnUpgrade"));
        Assert.Contains(upgrade, c => c.Contains("UpgradeValueBy"));
        Assert.DoesNotContain(upgrade, c => c.Contains("EnergyCost"));
        Assert.Contains("{IfUpgraded:show:2 cards|a card}", Face(seal));
    }

    // ==== 4. Kitsune Rite, Tenko and a card =================================

    [Fact]
    public void Kitsune_rite_tenkos_then_draws_one_and_keeps_its_upgrade()
    {
        var rite = new ProtoYmKitsuneRite();
        Assert.Equal(1, rite.EnergyCost.Canonical);
        Assert.EndsWith("|}. Draw 1 card.", Face(rite));
        var calls = Il.CallSequence(Il.Method("ProtoYmKitsuneRite", "OnPlay")).ToList();
        var tenko = calls.FindIndex(c => c.Contains("YaeCards.Tenko"));
        var draw = calls.FindIndex(c => c.Contains("CardPileCmd.Draw"));
        Assert.True(tenko >= 0 && draw > tenko, string.Join(" | ", calls));
        Assert.Contains(Il.Calls(Il.Method("ProtoYmKitsuneRite", "OnUpgrade")),
                        c => c.Contains("EnergyCost"));
    }
}
