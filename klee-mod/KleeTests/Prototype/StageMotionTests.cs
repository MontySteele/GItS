using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE MOTION PASS ON THE STAGE AND ON KLEE'S DODOCO (2026-10-02): the
/// performers act and flinch, the Spotlight shine falls on a new lead, and
/// Dodoco pops as its Mine goes out. Drawing needs Godot nodes, which is
/// process death in this host (README, the headless boundary), so the rules
/// that decide WHEN are pinned as pure functions and the call sites
/// structurally.
/// </summary>
public class StageMotionTests
{
    private static bool LeadChanged(int? last, int? now) =>
        (bool)typeof(FurinaStagePlacement).GetMethod("LeadChanged", HeadlessGame.All)!
            .Invoke(null, new object?[] { last, now })!;

    private static bool Flinches(bool standing, int loss) =>
        (bool)Il.Method("StagePerformerBeat", "Flinches")
            .Invoke(null, new object[] { standing, loss })!;

    [Fact]
    public void The_spotlight_shines_on_a_change_of_lead_and_only_then()
    {
        // The first performer of a fight takes the spotlight.
        Assert.True(LeadChanged(null, 7));
        // A Step Forward, or the next performer moving up after a Bow.
        Assert.True(LeadChanged(7, 9));
        // Every other reflow (a bar moved, a back seat filled) is not a new
        // lead and draws nothing.
        Assert.False(LeadChanged(7, 7));
        // An empty stage has no one to light.
        Assert.False(LeadChanged(7, null));
        Assert.False(LeadChanged(null, null));
    }

    [Fact]
    public void A_performer_flinches_only_when_its_bar_lost_something()
    {
        Assert.True(Flinches(standing: true, loss: 3));
        // A hit the Bow Block caught whole, like a fully blocked hit in the
        // base, draws nothing.
        Assert.False(Flinches(standing: true, loss: 0));
        Assert.False(Flinches(standing: false, loss: 3));
    }

    [Fact]
    public void The_act_lunges_and_the_hit_flinches_through_the_games_own_door()
    {
        // STRUCTURAL PIN: both beats are CreatureCmd.TriggerAnim, the door
        // the router serves, and the stage's two seams call them.
        Assert.Contains(Il.Calls(Il.Method("StagePerformerBeat", "Act")),
                        c => c.Contains("TriggerAnim"));
        Assert.Contains(Il.Calls(Il.Method("StagePerformerBeat", "Flinch")),
                        c => c.Contains("TriggerAnim"));
        // The re-founding (2026-10-04): the act lunges through the board;
        // performers take no hits, so nothing on the stage flinches.
        Assert.Contains(Il.Calls(Il.Method("GameStageBoard", "Lunge")),
                        c => c.Contains("StagePerformerBeat.Act"));
        Assert.Contains(Il.Calls(Il.Method("StageDirector", "Act")),
                        c => c.Contains("IStageBoard.Lunge"));
    }

    [Fact]
    public void The_two_orphaned_effects_have_callers_again()
    {
        Assert.Contains(Il.Calls(Il.Method("KleeExpansion", "RunTurnStartPlacements")),
                        c => c.Contains("KleeCombatVfx.SpawnDodocoPop"));
        Assert.Contains(Il.Calls(Il.Method("FurinaStagePlacement", "ShineOnNewLead")),
                        c => c.Contains("KleeCombatVfx.SpawnSpotlightShine"));
        Assert.Contains(Il.Calls(Il.Method("FurinaStagePlacement", "Reflow")),
                        c => c.Contains("FurinaStagePlacement.ShineOnNewLead"));
    }
}
