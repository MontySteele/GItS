using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// SWIRL LEGIBILITY (2026-10-19): wording and previews only, no rule moved.
/// Varka's Swirl faces name what his Fang pays, the Swirl reaction preview
/// says what this Swirl does, and Prune's Hexhunter Chime says "no aura" and
/// shows its element on the Bomb it hands it to. The page half is
/// <c>tier0/tests/test_newcomer_seat_2026_10_19.py</c>.
/// </summary>
[Collection(VarkaArm.Name)]
public class SwirlLegibilityTests : IDisposable
{
    public SwirlLegibilityTests()
    {
        HeadlessGame.Arm();
        VarkaOathLedger.ResetAll();
        CompanionOverhaulLedger.ResetAll();
    }

    public void Dispose()
    {
        VarkaOathLedger.ResetAll();
        CompanionOverhaulLedger.ResetAll();
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    // ==== 1. Varka's Swirl line ============================================

    [Fact]
    public void The_payout_words_name_each_element_with_the_law_numbers()
    {
        Assert.Equal($"Swirl pays Pyro: {VarkaLaw.SwirlPyroDamage} damage",
                     VarkaOath.SwirlPays(Element.Pyro, 1));
        Assert.Equal($"Swirl pays Hydro: {VarkaLaw.SwirlHydroBlock} Block",
                     VarkaOath.SwirlPays(Element.Hydro, 1));
        Assert.Equal($"Swirl pays Cryo: {VarkaLaw.SwirlCryoVulnerable} Vulnerable",
                     VarkaOath.SwirlPays(Element.Cryo, 1));
        Assert.Equal($"Swirl pays Electro: {VarkaLaw.SwirlElectroDamageAll} "
                     + "damage to ALL", VarkaOath.SwirlPays(Element.Electro, 1));
        Assert.Equal("Swirl pays Hydro: 3 Block, twice",
                     VarkaOath.SwirlPays(Element.Hydro, 2));
        Assert.Equal("Swirl pays Hydro: 3 Block, 4 times",
                     VarkaOath.SwirlPays(Element.Hydro, 4));
        Assert.Equal("", VarkaOath.SwirlPays(Element.None, 1));
        Assert.Equal("", VarkaOath.SwirlPays(Element.Geo, 1));
        // The older words keep their shape.
        Assert.Equal("Hydro (3 Block)", VarkaOath.PayoutWords(Element.Hydro));
        Assert.Equal("", VarkaOath.PayoutWords(Element.None));
    }

    [Fact]
    public void The_face_line_is_no_aura_or_the_payout()
    {
        Assert.Equal("\n(no aura: no Swirl)",
                     VarkaOath.SwirlWords(false, "Swirl pays Hydro: 3 Block"));
        Assert.Equal("\n(no aura: no Swirl)", VarkaOath.SwirlWords(false, ""));
        Assert.Equal("\n(Swirl pays Hydro: 3 Block)",
                     VarkaOath.SwirlWords(true, "Swirl pays Hydro: 3 Block"));
        Assert.Equal("", VarkaOath.SwirlWords(true, ""));
        Assert.Contains(Il.Calls(Il.Method("VarkaOath", "SwirlLine")),
                        c => c.Contains("VarkaOath.SwirlPaysNow"));
    }

    [Fact]
    public void The_payout_follows_the_current_element_and_needs_the_fang()
    {
        var bare = Seat.Varka().Creature;
        VarkaOathLedger.For(bare).SetCurrent(Element.Hydro);
        Assert.Equal("", VarkaOath.SwirlPaysNow(bare, null));

        var varka = Seat.Varka().WithRelic<BoreasFang>().Creature;
        Assert.Equal("", VarkaOath.SwirlPaysNow(varka, null));
        foreach (var element in VarkaOathLedger.Elements)
        {
            VarkaOathLedger.For(varka).SetCurrent(element);
            Assert.Equal(VarkaOath.SwirlPays(element, 1),
                         VarkaOath.SwirlPaysNow(varka, null));
        }
        // Crosscurrent's own Swirl pays twice.
        VarkaOathLedger.For(varka).SetCurrent(Element.Hydro);
        Assert.Equal("Swirl pays Hydro: 3 Block, twice",
                     VarkaOath.SwirlPaysNow(varka, new ProtoVkCrosscurrent()));
        // Not a Varka: nothing.
        Assert.Equal("", VarkaOath.SwirlPaysNow(Seat.Klee().Creature, null));
        Assert.Equal("", VarkaOath.SwirlPaysNow(null, null));
    }

    [Fact]
    public void Stormterrors_scale_multiplies_the_line()
    {
        var varka = Seat.Varka().WithRelic<BoreasFang>()
            .WithRelic<StormterrorsScale>().Creature;
        VarkaOathLedger.For(varka).SetCurrent(Element.Cryo);
        Assert.Equal("Swirl pays Cryo: 1 Vulnerable, twice",
                     VarkaOath.SwirlPaysNow(varka, null));
    }

    // ==== 2. the Swirl reaction preview =====================================

    [Fact]
    public void The_swirl_preview_names_the_spread_and_the_damage()
    {
        Assert.Equal(
            "Spreads [gold]Cryo[/gold] to the other enemies and deals "
          + "[blue]2[/blue] damage to ALL enemies.",
            KleeCardTooltips.SwirlPreviewBody(Element.Cryo, true, 2,
                                              Element.None, ""));
        Assert.Equal(
            "Removes the [gold]Pyro[/gold] aura and deals [blue]2[/blue] "
          + "damage to ALL enemies.",
            KleeCardTooltips.SwirlPreviewBody(Element.Pyro, false, 2,
                                              Element.None, ""));
    }

    [Fact]
    public void Varkas_swirl_preview_adds_his_oath_and_payout()
    {
        Assert.Equal(
            "Spreads [gold]Cryo[/gold] to the other enemies and deals "
          + "[blue]2[/blue] damage to ALL enemies. +1 [gold]Cryo[/gold] Oath; "
          + "Swirl pays Hydro: 3 Block.",
            KleeCardTooltips.SwirlPreviewBody(Element.Cryo, true, 2,
                Element.Cryo, VarkaOath.SwirlPays(Element.Hydro, 1)));
        Assert.Equal(
            "Spreads [gold]Cryo[/gold] to the other enemies and deals "
          + "[blue]2[/blue] damage to ALL enemies. +1 [gold]Cryo[/gold] Oath.",
            KleeCardTooltips.SwirlPreviewBody(Element.Cryo, true, 2,
                                              Element.Cryo, ""));
        var calls = Il.Calls(Il.Method("KleeCardTooltips", "SwirlBody"));
        Assert.Contains(calls, c => c.Contains("VarkaOath.SwirlPaysNow"));
        Assert.Contains(calls, c => c.Contains("CompanionOverhaulReactions.DamageMultiplier"));
    }

    // ==== 3. Prune's Hexhunter Chime ========================================

    [Fact]
    public void The_chime_says_when_there_is_no_aura_to_swirl()
    {
        Assert.Contains("[gold]Swirl[/gold] the enemy{InCombat:{SwirlAura}|}.",
                        Face(new ProtoMcPruneHexhunterChime()));
        Assert.Contains(Il.Calls(Il.Method("ProtoMcPruneHexhunterChime",
                                           "AddExtraArgsToDescription")),
                        c => c.Contains("SwirlAuraFace.Line"));
    }

    [Fact]
    public void The_chimes_swirl_tip_is_the_players_too()
    {
        var calls = Il.Calls(Il.Method("ProtoMcPruneHexhunterChime",
                                       "get_ExtraHoverTips"));
        Assert.Contains(calls, c => c.Contains("ArmKeywordTips.ForSwirl"));
        Assert.DoesNotContain(calls, c => c.Contains("TipAudience.get_Seat"));
    }

    [Fact]
    public void A_bomb_under_an_armed_chime_names_the_swirled_element()
    {
        var klee = Seat.Klee().WithPower<HexhunterChimePower>(1);
        var lone = ProtoBombs.Place(Seat.Klee(60).Creature, klee.Creature,
                                    new ProtoBombs.Charge(5));
        // Armed, nothing Swirled yet: Pyro.
        Assert.Equal(Element.None, lone.ChimeElementNow());
        Assert.Equal("[gold]Pyro[/gold]",
                     lone.DynamicVars["BombElement"].ToString());

        CompanionOverhaulLedger.For(klee.Creature).NoteSwirl(Element.Hydro);
        Assert.Equal(Element.Hydro, lone.ChimeElementNow());
        Assert.Equal("[gold]Hydro[/gold]",
                     lone.DynamicVars["BombElement"].ToString());
        Assert.Equal(5, lone.PredictedSetOffDamage());

        var pile = ProtoBombs.Place(Seat.Klee(60).Creature, klee.Creature,
                                    new ProtoBombs.Charge(5),
                                    new ProtoBombs.Charge(4));
        Assert.Equal("[gold]Hydro[/gold] and [gold]Pyro[/gold]",
                     pile.DynamicVars["BombElement"].ToString());
    }

    [Fact]
    public void A_bomb_with_no_chime_reads_pyro()
    {
        var klee = Seat.Klee();
        CompanionOverhaulLedger.For(klee.Creature).NoteSwirl(Element.Cryo);
        var pile = ProtoBombs.Place(Seat.Klee(60).Creature, klee.Creature,
                                    new ProtoBombs.Charge(5));
        Assert.Equal(Element.None, pile.ChimeElementNow());
        Assert.Equal("[gold]Pyro[/gold]",
                     pile.DynamicVars["BombElement"].ToString());
        Assert.Equal("[gold]Pyro[/gold]",
                     ProtoBombPower.ElementWords(Element.None, 3));
        Assert.Equal("[gold]Pyro[/gold]",
                     ProtoBombPower.ElementWords(Element.Pyro, 1));
        Assert.Equal("[gold]Electro[/gold]",
                     ProtoBombPower.ElementWords(Element.Electro, 1));
    }

    [Fact]
    public void The_explosion_still_asks_the_chime_command()
    {
        // Preview only: the hit's element is still the command's.
        Assert.Contains(Il.Calls(Il.Method("ProtoBombPower", "Explode")),
                        c => c.Contains("CompanionCovenBombs.ElementFor"));
    }
}
