using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;
using KleeMod.Powers;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE SALON'S TAB'S HEADLESS KIT (2026-10-05). The rules are
/// <see cref="StageDirector"/>'s over a <see cref="FurinaStageLedger"/>, and
/// the game half is an <see cref="IStageBoard"/>; this board RECORDS what the
/// rules asked of the game and keeps Furina's HP, so every rule edge the sim
/// pins (<c>tier0/tests/test_furina_tide_arm.py</c>) can be pinned here
/// without a combat. Every call completes synchronously.
/// </summary>
internal sealed class RecordingBoard : IStageBoard
{
    internal readonly List<string> Log = new();

    internal int Dealt;

    internal int Drawn;

    public bool Over { get; set; }

    public int Hp { get; set; } = 78;

    public int MaxHp { get; set; } = 78;

    public Task<int> LoseHp(int amount)
    {
        var lost = Math.Min(amount, Hp);
        Hp -= lost;
        Log.Add($"lose {lost}");
        return Task.FromResult(lost);
    }

    public Task<int> Heal(int amount)
    {
        var back = Math.Min(amount, MaxHp - Hp);
        Hp += back;
        Log.Add($"heal {back}");
        return Task.FromResult(back);
    }

    public Task Damage(StagePerformer who, StageTarget target, int amount,
                       Element element)
    {
        Log.Add($"damage {who} {target} {amount} {element}");
        Dealt += amount;
        return Task.CompletedTask;
    }

    public Task PowerHit(string source, StageTarget target, int amount)
    {
        Log.Add($"power {source} {target} {amount}");
        Dealt += amount;
        return Task.CompletedTask;
    }

    public Task Block(int amount)
    {
        Log.Add($"block {amount}");
        return Task.CompletedTask;
    }

    public Task Vulnerable(StageTarget target, int amount)
    {
        Log.Add($"vulnerable {target} {amount}");
        return Task.CompletedTask;
    }

    public Task Weak(StageTarget target, int amount)
    {
        Log.Add($"weak {target} {amount}");
        return Task.CompletedTask;
    }

    internal int Gained;

    public Task Strength(int amount)
    {
        Log.Add($"strength {amount}");
        Gained += amount;
        return Task.CompletedTask;
    }

    public Task Draw(int amount)
    {
        Log.Add($"draw {amount}");
        Drawn += amount;
        return Task.CompletedTask;
    }

    public Task Lunge(StageSeat? seat) => Task.CompletedTask;

    /// <summary>The pool to 75: a line's cue, recorded by who fired.</summary>
    public Task LineCue(StageSeat? seat)
    {
        Log.Add($"cue {seat?.Who}");
        return Task.CompletedTask;
    }

    /// <summary>The pool to 75: the cards a leaving guest sends to the
    /// discard pile, recorded (headless there is no pile).</summary>
    internal readonly List<object> Returned = new();

    public Task ReturnCards(StageSeat seat)
    {
        Log.Add($"return {seat.Who} {seat.Cards.Count}");
        Returned.AddRange(seat.Cards);
        seat.Cards.Clear();
        return Task.CompletedTask;
    }

    public Task Sync() => Task.CompletedTask;

    /// <summary>The damage events, in order.</summary>
    internal IEnumerable<string> Hits =>
        Log.Where(l => l.StartsWith("damage ") || l.StartsWith("power "));
}

/// <summary>A free-standing ledger and the director over it, Furina at
/// <c>hp</c> of 78 having entered the combat at <c>entry</c>.</summary>
internal sealed class StageKit
{
    internal FurinaStageLedger Stage { get; }

    internal RecordingBoard Board { get; } = new();

    internal StageDirector Director { get; }

    internal StageKit(StageMods? mods, int fanfare, int hp, int entry,
                      params StagePerformer[] seats)
    {
        Stage = FurinaStageLedger.Detached();
        Stage.ModsOverride = mods ?? StageMods.None;
        Stage.Open(entry);
        Board.Hp = hp;
        foreach (var who in seats) Stage.Seat(who);
        if (fanfare > 0) Stage.Gain(fanfare);
        Stage.OpenTurn();
        Stage.ClearBeats();
        Director = new StageDirector(Stage, Board);
    }

    internal static StageKit Of(params StagePerformer[] seats) =>
        new(null, 0, 78, 78, seats);

    internal static StageKit With(int fanfare, params StagePerformer[] seats) =>
        new(null, fanfare, 78, 78, seats);

    internal static StageKit With(StageMods mods, int fanfare,
                                  params StagePerformer[] seats) =>
        new(mods, fanfare, 78, 78, seats);

    internal static StageKit At(int hp, int entry,
                                params StagePerformer[] seats) =>
        new(null, 0, hp, entry, seats);

    internal StagePerformer[] Company => Stage.Seats.Select(s => s.Who).ToArray();

    /// <summary>Run one of the director's verbs to completion.</summary>
    internal static T Run<T>(Task<T> task) => task.GetAwaiter().GetResult();

    internal static void Run(Task task) => task.GetAwaiter().GetResult();

    internal int Beats(string evt) => Stage.Beats.Count(b => b.Event == evt);

    internal int Beats(string evt, StagePerformer who) =>
        Stage.Beats.Count(b => b.Event == evt && b.Who == who);
}
