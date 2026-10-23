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
    public void The_tenko_clause_names_each_kinds_sum()
    {
        // Review r3: one plain Tenko; each kind's sum in its own words.
        Assert.Equal(" (Sakura: 12 damage)", YaeShrineFace.TenkoWords(12));
        Assert.Equal(" (Sakura: 5 damage, 2 to each enemy, 5 Block)", YaeShrineFace.TenkoWords(5, 2, 5));
        Assert.Equal(" (Sakura: 5 Block)", YaeShrineFace.TenkoWords(0, 0, 5));
        Assert.Equal(" (no Sakura)", YaeShrineFace.TenkoWords(0));
    }
    [Fact]
    public void The_sum_is_each_sakuras_action_of_that_kind()
    {
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        for (var i = 0; i < 3; i++) ledger.Plant(YaeLaw.PlantLevel);
        Assert.Equal(9, YaeShrineFace.Total(ledger.Standing, YaeSakuraKind.Thunder));
        Assert.Equal(0, YaeShrineFace.Total(ledger.Standing, YaeSakuraKind.Kitsune));
        ledger.LevelUp(3);                    // 4, 4, 4: no cap
        // The Sakura Levels paper (2026-10-17): each Level adds 2.
        Assert.Equal(9 + 3 * 6, YaeShrineFace.Total(ledger.Standing, YaeSakuraKind.Thunder));
        ledger.EditSakura(YaeSakuraEnd.Every, 1, YaeAnnotation.RedInk);
        Assert.Equal(27 + 3 * 3, YaeShrineFace.Total(ledger.Standing, YaeSakuraKind.Thunder));
    }
    [Fact]
    public void Off_a_fight_the_clause_is_empty()
    {
        Assert.Equal("", YaeShrineFace.TenkoLine(new ProtoYmKitsuneGuile()));
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
    public void No_card_prints_a_typed_tenko()
    {
        foreach (var card in new CardModel[]
                 {
                     new ProtoYmShrineMaidensGuard(), new ProtoYmFoxfireSweep(),
                     new ProtoYmKitsuneGuile(), new ProtoYmManuscriptPile(),
                 })
        {
            foreach (var kind in new[] { "Warding", "Wildfire", "Offering" })
            {
                Assert.DoesNotContain($"({kind}", Face(card));
            }
            Assert.DoesNotContain("Rite", Face(card));
        }
        Assert.Contains($"[gold]Tenko[/gold]{{InCombat:{{{YaeShrineFace.TenkoToken}}}|}}",
                        Face(new ProtoYmKitsuneGuile()));
    }
    [Fact]
    public void The_full_shrine_rule_is_a_tip_on_every_planting_card()
    {
        // Review r3: with kinds the rule has two branches, so it left the
        // plant faces for its own tip.
        Assert.DoesNotContain("oldest", ArmKeywordTips.YaeSakuraTip);
        // Yae draft pass, 2026-10-17: "It strikes now." (round 9, pick 1 (a)).
        Assert.Equal("Plant a [gold]Sakura[/gold]. It strikes now.", Face(new ProtoYmYakanEvocation()));
        Assert.DoesNotContain("Warding", ArmKeywordTips.YaeTenkoTip);
        Assert.DoesNotContain("Rite", ArmKeywordTips.YaeSakuraTip);
        // Yae review r5, item 5: the long form (170) replaced the 97-character
        // one, which four of five seats could not read until it bit them.
        Assert.True(ArmKeywordTips.YaeFullShrineTip.Length <= 170);
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
        // Yae review r4, pick 1 (a): up to 2 [3] cards (was 1 [2]).
        Assert.Equal(2, (int)seal.DynamicVars["YmAmount"].BaseValue);
        var upgrade = Il.Calls(Il.Method("ProtoYmSakuraSeal", "OnUpgrade"));
        Assert.Contains(upgrade, c => c.Contains("UpgradeValueBy"));
        Assert.DoesNotContain(upgrade, c => c.Contains("EnergyCost"));
        Assert.Contains("up to {YmAmount:diff()} cards", Face(seal));
    }

    // ==== 4. Kitsune Rite, Tenko and a card =================================

    [Fact]
    public void Kitsune_rite_tenkos_then_draws_one_and_keeps_its_upgrade()
    {
        var rite = new ProtoYmKitsuneRite();
        Assert.Equal(1, rite.EnergyCost.Canonical);
        Assert.EndsWith("|}. Draw {Cards:diff()} card{Cards:plural:|s}.", Face(rite));
        var calls = Il.CallSequence(Il.Method("ProtoYmKitsuneRite", "OnPlay")).ToList();
        var tenko = calls.FindIndex(c => c.Contains("YaeCards.Tenko"));
        var draw = calls.FindIndex(c => c.Contains("CardPileCmd.Draw"));
        Assert.True(tenko >= 0 && draw > tenko, string.Join(" | ", calls));
        // Upgrade census (2026-10-23, [USER]): draw 1 [2] (was cost -1).
        Assert.DoesNotContain(Il.Calls(Il.Method("ProtoYmKitsuneRite", "OnUpgrade")),
                              c => c.Contains("EnergyCost"));
        Assert.Equal(1m, rite.DynamicVars.Cards.BaseValue);
    }
}
