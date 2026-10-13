using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The Varka display and rule lines of the backlog batch of 2026-10-13:
/// Wildfire Oath's preview on the cards that apply Pyro, and the Varka
/// screen's three parts (Sayu's Swirl on no aura, Sharpshooter's condition,
/// Cycle of Seasons' own line). The suite is headless, so the wiring is
/// pinned off the compiled methods; the sim halves are
/// <c>tier0/tests/test_varka_wildfire_preview.py</c> and
/// <c>tier0/tests/test_varka_screen_backlog.py</c>.
/// </summary>
public class VarkaBacklogDisplayTests
{
    [Fact]
    public void Wildfire_oath_prints_what_each_pyro_application_deals()
    {
        Assert.Equal("", VarkaOath.WildfireWords(0));
        Assert.Equal("\n(Wildfire Oath deals 5)", VarkaOath.WildfireWords(5));
        // Off a combat the face adds nothing.
        Assert.Equal("", VarkaOath.WildfireLine(new ProtoVkEmberCleave()));
        Assert.Equal("", VarkaOath.WildfireLine(null));
        // The number is the power's own arithmetic over the Pyro Oath.
        Assert.Contains(Il.Calls(Il.Method("VarkaOath", "WildfireLine")),
                        c => c.Contains("WildfireOathPower.DamageFor"));
    }

    [Fact]
    public void An_anemo_hit_is_a_swirl_attempt_the_page_can_count()
    {
        // (a) Sayu's random Swirl: the hit's Anemo is noted before the hit's
        // reaction resolves, so a bare enemy reads "the Swirl did nothing".
        Assert.Contains(Il.Calls(Il.Method("KleeElementalHooks",
                                           "BeforeDamageReceived")),
                        c => c.Contains("ResolutionLedger.NoteAnemoApplication"));
    }

    [Fact]
    public void Sharpshooter_reads_pyro_before_its_first_hit()
    {
        // (b) The snapshot is taken before the first hit is dealt, so a
        // reaction that eats the Pyro mid-card cannot cancel the second.
        var calls = Il.CallSequence(Il.Method("ProtoVkAmberSharpshooter",
                                              "OnPlay")).ToList();
        var snapshot = calls.FindIndex(c => c.Contains("AuraCmd.Find"));
        var firstHit = calls.FindIndex(c => c.Contains("Execute"));
        Assert.True(snapshot >= 0 && firstHit > snapshot,
                    string.Join(", ", calls));
    }

    [Fact]
    public void Cycle_of_seasons_files_its_hit_under_its_own_name()
    {
        // (c) The hit is filed with `by`, and the page labels it.
        Assert.Contains("ResolutionLedger.HitsBy",
            Il.CallSequence(Il.Method("CycleOfSeasonsPower",
                                      "OnElementChanged")));
        Assert.Equal("Cycle of Seasons",
            new ResolutionLedger.Hit("Slime", 7, 0, "1",
                                     By: "Cycle of Seasons").By);
    }
}
