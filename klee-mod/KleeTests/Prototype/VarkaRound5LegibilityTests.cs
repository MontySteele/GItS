using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// Varka round 5 (<c>review/records/varka-round-5-2026-10-13.md</c>, "What to
/// change" 1 and 2), display and log only: the switch line says the Oath the
/// new element holds, a Swirl card says "(No aura to Swirl)" in hand, and
/// Chain Lightning and Short Circuit name what they discarded. The suite is
/// headless, so the pure words and the ledger are pinned by value and the
/// wiring off the compiled methods; the page half is
/// <c>tier0/tests/test_varka_round5_legibility.py</c>.
/// </summary>
public class VarkaRound5LegibilityTests
{
    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    // ==== the switch line ===================================================

    [Fact]
    public void The_switch_line_names_the_oath_the_new_element_holds()
    {
        Assert.Equal("\n(Makes Cryo current: 2 Oath)",
                     VarkaOath.SwitchWords(Element.Cryo, 2));
        Assert.Equal("\n(Makes Hydro current: 0 Oath)",
                     VarkaOath.SwitchWords(Element.Hydro, 0));
        // Banner of the West Wind carries the old element's Oath over.
        Assert.Equal(2, VarkaOath.SwitchOath(2, 0));
        Assert.Equal(7, VarkaOath.SwitchOath(2, 5));
        Assert.Equal(0, VarkaOath.SwitchOath(-1, 0));
        // Off a fight there is no Varka to read.
        Assert.Equal(0, VarkaOath.OathOnSwitch(null, Element.Cryo));
        Assert.Equal("", VarkaOath.SwitchLine(new ProtoVkKaeyaFrostgnaw(), Element.Cryo));
    }

    [Fact]
    public void The_switch_line_reads_the_ledger_and_the_banner()
    {
        Assert.Contains(Il.Calls(Il.Method("VarkaOath", "SwitchLine")),
                        c => c.Contains("VarkaOath.OathOnSwitch"));
        var reads = Il.Calls(Il.Method("VarkaOath", "OathOnSwitch"));
        Assert.Contains(reads, c => c.Contains("VarkaOath.Count"));
        Assert.Contains(reads, c => c.Contains("VarkaArmRelics.Held"));
    }

    // ==== the Swirl line ====================================================

    [Fact]
    public void No_aura_reads_no_aura_to_swirl()
    {
        Assert.Equal("\n(No aura to Swirl)", VarkaOath.SwirlWords(aura: false));
        Assert.Equal("", VarkaOath.SwirlWords(aura: true));
        // Off a fight the face adds nothing.
        Assert.Equal("", VarkaOath.SwirlLine(null));
        Assert.Equal("", VarkaOath.SwirlLine(new ProtoVkFourWindsAscension()));
    }

    [Fact]
    public void The_swirl_line_reads_the_aimed_enemy_first()
    {
        var calls = Il.Calls(Il.Method("VarkaOath", "SwirlLine"));
        Assert.Contains(calls, c => c.Contains("DescribedTarget.For"));
        Assert.Contains(calls, c => c.Contains("AuraCmd.Find"));
    }

    [Fact]
    public void The_aimed_enemy_is_held_only_for_its_own_card()
    {
        var card = new ProtoVkCrosscurrent();
        Assert.Null(DescribedTarget.For(card));
        using (DescribedTarget.Aim(card, null))
        {
            Assert.Null(DescribedTarget.For(card));
            Assert.Null(DescribedTarget.For(new ProtoVkCrosswind()));
        }
        Assert.Null(DescribedTarget.For(null));
    }

    [Fact]
    public void Every_varka_swirl_card_ends_its_face_in_the_line()
    {
        foreach (var card in new CardModel[]
                 {
                     new ProtoVkFourWindsAscension(), new ProtoVkCrosscurrent(),
                     new ProtoVkWallOfGales(), new ProtoVkGaleSweep(),
                     new ProtoVkDownburst(), new ProtoVkJeanDandelionBreeze(),
                 })
        {
            Assert.EndsWith("{InCombat:{VarkaSwirl}|}", Face(card));
        }
        // A card that does not Swirl carries none.
        Assert.DoesNotContain("VarkaSwirl", Face(new ProtoVkKaeyaFrostgnaw()));
        Assert.DoesNotContain("VarkaSwirl", Face(new ProtoVkChainLightning()));
    }

    // ==== Chain Lightning's discard =========================================

    [Fact]
    public void The_game_picks_the_discard_only_from_a_short_hand()
    {
        Assert.True(ResolutionLedger.DiscardPickedForYou(2, 2));
        Assert.True(ResolutionLedger.DiscardPickedForYou(1, 2));
        Assert.True(ResolutionLedger.DiscardPickedForYou(0, 2));
        Assert.False(ResolutionLedger.DiscardPickedForYou(3, 2));
    }

    [Fact]
    public void The_discards_are_filed_on_the_play_line()
    {
        ResolutionLedger.ResetFight();
        try
        {
            ResolutionLedger.OpenPlay("X", "Chain Lightning", false);
            ResolutionLedger.NoteDiscards("Chain Lightning",
                                          new List<string?> { "Strike", "Defend" },
                                          pickedForYou: true);
            ResolutionLedger.ClosePlay();
            var row = Assert.Single(ResolutionLedger.Snapshot());
            var events = Assert.IsType<List<Dictionary<string, object?>>>(row["events"]);
            Assert.Equal(new[] { "Strike", "Defend" },
                         events.Select(e => (string?)e["card"]));
            Assert.All(events, e =>
            {
                Assert.Equal("play_discard", e["kind"]);
                Assert.Equal("only cards in hand", e["power"]);
            });
        }
        finally
        {
            ResolutionLedger.ResetFight();
        }
    }

    [Fact]
    public void Chain_lightning_and_short_circuit_note_their_discards()
    {
        foreach (var type in new[] { "ProtoVkChainLightning", "ProtoVkShortCircuit" })
        {
            var calls = Il.Calls(Il.Method(type, "OnPlay"));
            Assert.Contains(calls, c => c.Contains("ResolutionLedger.NoteDiscards"));
            Assert.Contains(calls, c => c.Contains("ResolutionLedger.DiscardPickedForYou"));
        }
    }
}
