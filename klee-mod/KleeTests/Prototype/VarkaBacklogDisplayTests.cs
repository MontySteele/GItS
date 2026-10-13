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
}
