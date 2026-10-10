using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE VARKA PAYOFF ROUND'S "CLAUDE SHIPS" LIST
/// (<c>review/records/varka-payoff-round-2026-10-10.md</c>): the card texts,
/// Wolfpack's exhausting copy shuffled into the draw pile, the seat page's
/// new lines, the held relic named, the telemetry element and the lane's
/// Knight override. Strings by value, live sites by their call graph. The
/// sim twin is <c>tier0/tests/test_varka_payoff_round.py</c>.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaPayoffRoundTests : IDisposable
{
    public VarkaPayoffRoundTests()
    {
        HeadlessGame.Arm();
        VarkaOathLedger.ResetAll();
        ResolutionLedger.ResetFight();
    }

    public void Dispose()
    {
        VarkaOathLedger.ResetAll();
        ResolutionLedger.ResetFight();
    }

    private static List<string> Calls(string type, string method) =>
        Il.Calls(Il.Method(type, method)).ToList();

    private static string Face(object model) =>
        ((ILocalizationProvider)model).Localization!
            .Single(l => l.Item1 == "description").Item2;

    [Fact]
    public void Ember_cleave_switches_before_it_gains_too()
    {
        // Ember Cleave's gain is the `gain_pyro_oath` kind, Stoke's.
        Assert.Contains("VarkaCards.GainPyroOath",
                        Calls("ProtoVkEmberCleave", "OnPlay"));
        var gain = Calls("VarkaCards", "GainPyroOath");
        Assert.True(gain.IndexOf("VarkaOath.CardMakesCurrent")
                    < gain.IndexOf("VarkaOath.Gain"), string.Join(", ", gain));
    }

    [Fact]
    public void Wolfpack_says_shuffle_and_exhaust_on_card_and_power()
    {
        const string face = "Whenever you play Four Winds' Ascension, shuffle "
                          + "a copy of it into your [gold]Draw Pile[/gold]. The "
                          + "copy [gold]Exhausts[/gold].";
        Assert.Equal(face, Face(new ProtoVkWolfpack()));
        Assert.Equal(face, Face(new WolfpackPower()));
        Assert.Equal("wolfpack", ResolutionLedger.Wolfpack);
    }

    [Fact]
    public void The_banner_card_says_the_current_element()
    {
        Assert.Equal("Only [gold]Knights[/gold] change your [gold]current "
                     + "element[/gold]. Whenever another card would, gain 1 "
                     + "[gold]Oath[/gold] of your [gold]current element[/gold] "
                     + "instead.", Face(new ProtoVkUnwaveringBanner()));
    }

    [Fact]
    public void Twin_gales_says_what_each_swirl_paid()
    {
        Assert.Equal("Pyro (" + VarkaLaw.SwirlPyroDamage + " damage) and Cryo ("
                     + VarkaLaw.SwirlCryoVulnerable + " Vulnerable)",
                     VarkaOath.TwinGalesPaid(Element.Pyro, Element.Cryo, 1));
        // The Swirled element is the current one: it pays once.
        Assert.Equal("Hydro (" + VarkaLaw.SwirlHydroBlock + " Block)",
                     VarkaOath.TwinGalesPaid(Element.Hydro, Element.Hydro, 1));
        // No current element: only the Swirled one pays.
        Assert.Equal("Electro (" + VarkaLaw.SwirlElectroDamageAll
                     + " damage to ALL), x2",
                     VarkaOath.TwinGalesPaid(Element.None, Element.Electro, 2));
        Assert.Equal(string.Empty,
                     VarkaOath.TwinGalesPaid(Element.None, Element.None, 1));
        Assert.Equal("paid", ResolutionLedger.SwirlPaid);
        var swirl = Calls("VarkaOath", "OnSwirl");
        Assert.Contains("VarkaOath.TwinGalesPaid", swirl);
        Assert.Contains("ResolutionLedger.NoteEvent", swirl);
    }

    [Fact]
    public void An_anemo_application_with_no_aura_is_filed_on_the_row()
    {
        Assert.Contains("ResolutionLedger.NoteAnemoApplication",
                        Calls("ElementalHit", "ApplyOnly"));
        ResolutionLedger.OpenPlay("sucrose", "Sucrose — Wind Spirit Creation",
                                  false);
        ResolutionLedger.NoteAnemoApplication(onAura: false);
        ResolutionLedger.NoteAnemoApplication(onAura: false);
        ResolutionLedger.ClosePlay();
        var row = ResolutionLedger.Snapshot().Single();
        Assert.Equal(2, row["swirl_no_aura"]);
        Assert.Equal(0, row["swirl_on_aura"]);
        // Outside a play nothing is filed.
        ResolutionLedger.NoteAnemoApplication(onAura: true);
        Assert.Single(ResolutionLedger.Snapshot());
    }

    [Fact]
    public void The_knight_override_parses_and_keeps_the_roll()
    {
        Assert.Equal("GITS_VARKA_KNIGHT", VarkaStarterKnight.OverrideEnvVar);
        Assert.Equal(Element.Pyro, VarkaStarterKnight.ParseOverride("pyro"));
        Assert.Equal(Element.Hydro, VarkaStarterKnight.ParseOverride(" Hydro "));
        Assert.Equal(Element.Cryo, VarkaStarterKnight.ParseOverride("CRYO"));
        Assert.Equal(Element.Electro, VarkaStarterKnight.ParseOverride("electro"));
        Assert.Equal(Element.None, VarkaStarterKnight.ParseOverride(""));
        Assert.Equal(Element.None, VarkaStarterKnight.ParseOverride(null));
        Assert.Equal(Element.None, VarkaStarterKnight.ParseOverride("anemo"));

        var knights = new[] { "amber", "barbara", "lisa", "kaeya" };
        Element Of(string k) => k switch
        {
            "amber" => Element.Pyro, "barbara" => Element.Hydro,
            "lisa" => Element.Electro, _ => Element.Cryo,
        };
        Assert.Equal("amber", VarkaStarterKnight.Choose("kaeya", Element.Pyro,
                                                        knights, Of));
        Assert.Equal("kaeya", VarkaStarterKnight.Choose("kaeya", Element.None,
                                                        knights, Of));

        // The seed's roll is still drawn, then the override picks.
        var obtained = Calls("BoreasFang", "AfterObtained");
        var roll = obtained.IndexOf("PlayerRngSet.get_Transformations");
        var forced = obtained.IndexOf("VarkaStarterKnight.Override");
        Assert.True(roll >= 0 && forced > roll, string.Join(", ", obtained));
        Assert.Contains("VarkaStarterKnight.Choose", string.Join(",", obtained));
    }

    [Fact]
    public void A_cards_played_row_carries_varka_element_only()
    {
        Assert.Contains("PlayTelemetry.VarkaElementWord",
                        Calls("PlayTelemetry", "CardPlayed"));
    }
}
