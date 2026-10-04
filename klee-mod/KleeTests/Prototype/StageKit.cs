using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;
using KleeMod.Powers;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE STAGE'S HEADLESS KIT (v2, the re-founding). The rules are
/// <see cref="StageDirector"/>'s over a <see cref="FurinaStageLedger"/>, and
/// the game half is an <see cref="IStageBoard"/>; this board RECORDS what the
/// rules asked of the game, so every rule edge the sim pins
/// (<c>tier0/tests/test_furina_v2_slice.py</c>) can be pinned here without a
/// combat. Every call completes synchronously.
/// </summary>
internal sealed class RecordingBoard : IStageBoard
{
    internal readonly List<string> Log = new();

    internal int BlockGained;

    internal int Dealt;

    internal int Drawn;

    internal int Tricks;

    internal int Energy;

    public bool Over { get; set; }

    public Task Block(StagePerformer who, int amount)
    {
        Log.Add($"block {who} {amount}");
        BlockGained += amount;
        return Task.CompletedTask;
    }

    public Task Damage(StagePerformer who, StageTarget target, int amount,
                       Element element)
    {
        Log.Add($"damage {who} {target} {amount} {element}");
        Dealt += amount;
        return Task.CompletedTask;
    }

    public Task AddTrick()
    {
        Log.Add("trick");
        Tricks++;
        return Task.CompletedTask;
    }

    public Task EnergyNextTurn(int amount)
    {
        Log.Add($"energy {amount}");
        Energy += amount;
        return Task.CompletedTask;
    }

    public Task Draw(int amount)
    {
        Log.Add($"draw {amount}");
        Drawn += amount;
        return Task.CompletedTask;
    }

    public Task ClorindeLine(int amount)
    {
        Log.Add($"clorinde {amount}");
        Dealt += amount;
        return Task.CompletedTask;
    }

    public Task CriticsHit(int amount)
    {
        Log.Add($"critics {amount}");
        return Task.CompletedTask;
    }

    public Task GlovesBlock(int amount)
    {
        Log.Add($"gloves {amount}");
        BlockGained += amount;
        return Task.CompletedTask;
    }

    public Task Lunge(StageSeat? seat) => Task.CompletedTask;

    public Task Sync() => Task.CompletedTask;

    /// <summary>The damage events, in order.</summary>
    internal IEnumerable<string> Hits =>
        Log.Where(l => l.StartsWith("damage ") || l.StartsWith("clorinde "));
}

/// <summary>A free-standing stage and the director over it.</summary>
internal sealed class StageKit
{
    internal FurinaStageLedger Stage { get; }

    internal RecordingBoard Board { get; } = new();

    internal StageDirector Director { get; }

    internal StageKit(StageMods? mods, int fanfare,
                      params StagePerformer[] seats)
    {
        Stage = FurinaStageLedger.Detached();
        Stage.ModsOverride = mods ?? StageMods.None;
        foreach (var who in seats) Stage.Seat(who);
        if (fanfare > 0) Stage.Gain(fanfare);
        Stage.OpenTurn();
        Stage.TakeChanges();
        Stage.ClearBeats();
        Director = new StageDirector(Stage, Board);
    }

    internal static StageKit Of(params StagePerformer[] seats) =>
        new(null, 0, seats);

    internal static StageKit With(int fanfare, params StagePerformer[] seats) =>
        new(null, fanfare, seats);

    internal static StageKit With(StageMods mods, int fanfare,
                                  params StagePerformer[] seats) =>
        new(mods, fanfare, seats);

    internal StagePerformer[] Company => Stage.Seats.Select(s => s.Who).ToArray();

    /// <summary>Run one of the director's verbs to completion.</summary>
    internal static T Run<T>(Task<T> task) => task.GetAwaiter().GetResult();

    internal static void Run(Task task) => task.GetAwaiter().GetResult();

    internal int Beats(string evt) => Stage.Beats.Count(b => b.Event == evt);

    internal int Beats(string evt, StagePerformer who) =>
        Stage.Beats.Count(b => b.Event == evt && b.Who == who);
}
