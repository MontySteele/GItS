using System;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using KleeMod.Diagnostics;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA WHOLE-RUN ROUND 3 (2026-10-11), proposed changes 2 and 5: a
/// Repay act's beat carries its floor's Block, so the seat page can print
/// "you Repay 0, +2 Block" as the face does; and the telemetry adds the
/// Drain buffer left at the close, Block gained per card play, and the Guest
/// Star evictions and repeat acts. Python twin:
/// <c>tier0/tests/test_furina_round_3_page.py</c>.
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class FurinaRound3TelemetryTests : IDisposable
{
    private static readonly Type Telemetry = typeof(PlayTelemetryHooks).Assembly
        .GetTypes().First(t => t.Name == "PlayTelemetry");

    public FurinaRound3TelemetryTests()
    {
        Environment.SetEnvironmentVariable("GITS_TELEMETRY_INTENT", "");
        Invoke("ResetForTest");
        FurinaStageLedger.ResetAll();
    }

    public void Dispose()
    {
        Invoke("ResetForTest");
        FurinaStageLedger.ResetAll();
    }

    private static object? Invoke(string name, params object?[] args) =>
        Telemetry.GetMethod(name, HeadlessGame.All)!.Invoke(null, args);

    private static T Run<T>(System.Threading.Tasks.Task<T> task) =>
        StageKit.Run(task);

    private static void Run(System.Threading.Tasks.Task task) =>
        StageKit.Run(task);

    // ---- 2. the Repay floor rides the act's beat ------------------------------

    [Fact]
    public void A_repay_act_with_nothing_drained_logs_its_floor()
    {
        var kit = StageKit.Of(StagePerformer.Charlotte);
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        var act = kit.Stage.Beats.Single(b => b.Event == FurinaStageLedger.ActEvent);
        Assert.Equal(0, act.Moved);
        Assert.Equal(3, act.Floor);
    }

    [Fact]
    public void A_repay_act_that_returns_part_logs_the_rest_as_floor()
    {
        var kit = StageKit.Of();
        Run(kit.Director.SummonGuest(StagePerformer.Sigewinne, true));
        Run(kit.Director.Drain(1));
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        var act = kit.Stage.Beats.Single(b => b.Event == FurinaStageLedger.ActEvent);
        Assert.Equal(1, act.Moved);          // Repay 5 returns 1
        Assert.Equal(4, act.Floor);          // +4 Block
    }

    [Fact]
    public void A_damage_act_has_no_floor()
    {
        var kit = StageKit.Of(StagePerformer.Clorinde);
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.Equal(0, kit.Stage.Beats
            .Single(b => b.Event == FurinaStageLedger.ActEvent).Floor);
    }

    // ---- 5. guest evictions and repeat acts -----------------------------------

    [Fact]
    public void Evictions_and_repeat_acts_are_counted()
    {
        var kit = StageKit.Of(StagePerformer.Clorinde, StagePerformer.Lynette,
                              StagePerformer.Charlotte);
        Assert.Equal(0, kit.Stage.GuestEvictions);
        Run(kit.Director.SummonGuest(StagePerformer.Wriothesley));
        Assert.Equal(1, kit.Stage.GuestEvictions);
        Assert.Equal(0, kit.Stage.GuestRepeatActs);
        Run(kit.Director.SummonGuest(StagePerformer.Lynette));
        Assert.Equal(1, kit.Stage.GuestRepeatActs);
        Assert.Equal(1, kit.Stage.GuestEvictions);
        kit.Stage.Clear();
        Assert.Equal(0, kit.Stage.GuestEvictions);
        Assert.Equal(0, kit.Stage.GuestRepeatActs);
    }

    // ---- 5. the buffer at the close, and the fight record's keys --------------

    [Fact]
    public void The_buffer_left_is_read_before_the_curtain_call_empties_it()
    {
        var ledger = FurinaStageLedger.Detached();
        ledger.Open(80, 80);                          // buffer 20
        ledger.NoteDrain(6, 80);
        Assert.Equal(20, ledger.BufferAtClose);
        Assert.Equal(14, ledger.BufferLeftAtClose);   // a death: read live
        ledger.CurtainCallOf(74, 80);
        Assert.Equal(20, ledger.BufferLeft);          // the call emptied it
        Assert.Equal(14, ledger.BufferLeftAtClose);   // ...the close kept it
        ledger.Clear();
        Assert.Equal(-1, ledger.BufferLeftAtCall);
    }

    [Fact]
    public void A_furina_fight_writes_the_buffer_and_the_guest_counts()
    {
        var furina = Seat.Furina(80).WithCombatState();
        var combat = DispatchProxy.Create<ICombatState,
            FurinaSpendAllPreviewWeakTests.ListenerProxy>();
        furina.Creature.CombatState = combat;
        Invoke("OpenSeatForTest", furina.Player, 1, 0);
        var ledger = FurinaStageLedger.For(furina.Creature);  // buffer 20
        ledger.NoteDrain(5, 80);
        ledger.GuestEvictions = 2;
        ledger.GuestRepeatActs = 1;
        Invoke("RecordTurnEnd", 1);
        var r = JsonDocument.Parse((string)Invoke("JsonForTest", furina.Player)!)
            .RootElement;
        Assert.Equal(20, r.GetProperty("drain_buffer").GetInt32());
        Assert.Equal(15, r.GetProperty("drain_buffer_left").GetInt32());
        Assert.Equal(2, r.GetProperty("guest_evictions").GetInt32());
        Assert.Equal(1, r.GetProperty("guest_repeat_acts").GetInt32());

        var klee = Seat.Klee();
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        var kr = JsonDocument.Parse((string)Invoke("JsonForTest", klee.Player)!)
            .RootElement;
        Assert.False(kr.TryGetProperty("drain_buffer_left", out _));
        Assert.False(kr.TryGetProperty("guest_evictions", out _));
        Assert.Equal(0, kr.GetProperty("card_play_block").GetArrayLength());
    }

    [Fact]
    public void Block_gained_per_card_play_is_one_entry_per_row()
    {
        var seat = Seat.Furina(80);
        Invoke("OpenSeatForTest", seat.Player, 1, 0);
        object hymn = new object(), defend = new object(), auto = new object();
        // Block outside any play (a relic, a guest act) is no play's.
        Invoke("RecordBlock", seat.Creature, 4, null, 1);
        // Hymn: 6 Block, then its floor's 3.
        Invoke("OpenPlayBlockForTest", seat.Player, hymn);
        Invoke("RecordBlock", seat.Creature, 6, null, 1);
        Invoke("RecordBlock", seat.Creature, 3, null, 1);
        Invoke("ClosePlayBlockForTest", seat.Player, hymn, "Hymn", 1, true, true);
        // A play inside a play: the inner keeps its 5, the outer its 2 + 1.
        Invoke("OpenPlayBlockForTest", seat.Player, defend);
        Invoke("RecordBlock", seat.Creature, 2, null, 1);
        Invoke("OpenPlayBlockForTest", seat.Player, auto);
        Invoke("RecordBlock", seat.Creature, 5, null, 1);
        Invoke("ClosePlayBlockForTest", seat.Player, auto, "Auto", 1, true, true);
        Invoke("RecordBlock", seat.Creature, 1, null, 1);
        Invoke("ClosePlayBlockForTest", seat.Player, defend, "Defend", 1, true,
               true);
        // A replayed card: one row, the replays' Block added to it.
        object twice = new object();
        Invoke("OpenPlayBlockForTest", seat.Player, twice);
        Invoke("RecordBlock", seat.Creature, 7, null, 2);
        Invoke("ClosePlayBlockForTest", seat.Player, twice, "Twice", 2, true,
               false);
        Invoke("RecordBlock", seat.Creature, 7, null, 2);
        Invoke("ClosePlayBlockForTest", seat.Player, twice, "Twice", 2, false,
               true);
        var r = JsonDocument.Parse((string)Invoke("JsonForTest", seat.Player)!)
            .RootElement;
        Assert.Equal(new[] { "Hymn", "Auto", "Defend", "Twice" },
            r.GetProperty("cards_played").EnumerateArray()
                .Select(row => row[1].GetString()).ToArray());
        Assert.Equal(new[] { 9, 5, 3, 14 },
            r.GetProperty("card_play_block").EnumerateArray()
                .Select(v => v.GetInt32()).ToArray());
        Assert.Equal(35, r.GetProperty("block_gained").GetInt32());
    }
}
