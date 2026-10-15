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
/// (shrine r2 replaced the "Rite: X" clause with a Tenko clause: "Tenko
/// (12 damage)", "Tenko (Warding: 5 Block)"); every
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

    // ==== 1. the Tenko clause (shrine r2 replaced the Rite clause) ========

    [Fact]
    public void The_tenko_clause_names_the_sum_in_each_kinds_words()
    {
        Assert.Equal(" (12 damage)", YaeShrineFace.TenkoWords(YaeTenkoKind.Thunder, 12));
        // A typed Tenko strikes AND adds its kind (2026-10-14).
        Assert.Equal(": 5 damage, 5 Block", YaeShrineFace.TenkoWords(YaeTenkoKind.Warding, 5, 5));
        Assert.Equal(": 5 damage, 2 to each enemy", YaeShrineFace.TenkoWords(YaeTenkoKind.Wildfire, 5, 2));
        Assert.Equal(": 9 damage, draw 3", YaeShrineFace.TenkoWords(YaeTenkoKind.Offering, 9, 3));
        // No Sakura standing.
        Assert.Equal(" (no Sakura)", YaeShrineFace.TenkoWords(YaeTenkoKind.Thunder, 0));
        Assert.Equal(", no Sakura", YaeShrineFace.TenkoWords(YaeTenkoKind.Warding, 0));
    }

    [Fact]
    public void The_sum_is_each_sakuras_strike_as_that_kind()
    {
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        for (var i = 0; i < 3; i++) ledger.Plant(YaeLaw.PlantLevel);
        // Levels 1, 1, 1 (shrine r2: a plant levels nothing).
        Assert.Equal(9, YaeShrineFace.Total(ledger.Standing, YaeTenkoKind.Thunder));
        Assert.Equal(9, YaeShrineFace.Total(ledger.Standing, YaeTenkoKind.Warding));
        Assert.Equal(3, YaeShrineFace.Total(ledger.Standing, YaeTenkoKind.Wildfire));
        Assert.Equal(3, YaeShrineFace.Total(ledger.Standing, YaeTenkoKind.Offering));
        ledger.LevelUp(3);                    // 4, 4, 4: no cap
        Assert.Equal(9 + 3 * 3, YaeShrineFace.Total(ledger.Standing, YaeTenkoKind.Thunder));
        ledger.EditSakura(YaeSakuraEnd.Every, 1, YaeAnnotation.RedInk);
        Assert.Equal(18 + 3 * 3, YaeShrineFace.Total(ledger.Standing, YaeTenkoKind.Warding));
        Assert.Equal(3, YaeShrineFace.Total(ledger.Standing, YaeTenkoKind.Offering));
    }

    [Fact]
    public void Off_a_fight_the_clause_is_empty()
    {
        Assert.Equal("", YaeShrineFace.TenkoLine(new ProtoYmShrineMaidensGuard(), YaeTenkoKind.Warding));
        Assert.Equal("", YaeShrineFace.TenkoLine(new ProtoYmThunderRite()));
        Assert.Equal("", YaeShrineFace.TenkoLine(null));
    }

    [Fact]
    public void The_clause_reads_the_strike_size()
    {
        Assert.Contains(Il.Calls(Il.Method("YaeShrineFace", "TenkoLine")),
                        c => c.Contains("YaeShrineFace.Total"));
        Assert.Equal(" (no Sakura)", YaeShrineFace.NoSakura);
    }

    [Fact]
    public void Every_typed_tenko_card_carries_the_clause_inside_its_brackets()
    {
        foreach (var (card, kind) in new (CardModel, string)[]
                 {
                     (new ProtoYmShrineMaidensGuard(), "Warding"),
                     (new ProtoYmFoxfireSweep(), "Wildfire"),
                     (new ProtoYmKitsuneGuile(), "Wildfire"),
                     (new ProtoYmManuscriptPile(), "Offering"),
                 })
        {
            Assert.Contains($"[gold]Tenko[/gold] ({kind}{{InCombat:{{{YaeShrineFace.TenkoToken}}}|}})",
                            Face(card));
            Assert.DoesNotContain("Rite", Face(card));
            Assert.Contains(Il.Calls(Il.Method(card.GetType().Name, "AddExtraArgsToDescription")),
                            c => c.Contains("YaeShrineFace.TenkoLine"));
        }
    }

    [Fact]
    public void The_tenko_tip_names_the_kinds_and_the_plant_faces_the_full_shrine()
    {
        Assert.Contains("Warding", ArmKeywordTips.YaeTenkoTip);
        Assert.Contains("Wildfire", ArmKeywordTips.YaeTenkoTip);
        Assert.Contains("Offering", ArmKeywordTips.YaeTenkoTip);
        Assert.Contains("refresh to 3 turns", ArmKeywordTips.YaeTenkoTip);
        // 2026-10-14: the full-shrine rule left the tip for the plant faces.
        Assert.DoesNotContain("oldest", ArmKeywordTips.YaeSakuraTip);
        Assert.Contains("your oldest strikes, refreshes", Face(new ProtoYmYakanEvocation()));
        Assert.DoesNotContain("Rite", ArmKeywordTips.YaeSakuraTip);
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
