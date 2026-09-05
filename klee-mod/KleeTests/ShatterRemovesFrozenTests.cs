using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-423` -- "and removes Frozen", made true of the board.
///
/// THE SEAT'S READING (Furina round 5, run 1, fight 4): "the shatter's own
/// text says 'The first Attack to hit it Shatters for 6 unblockable damage and
/// removes Frozen' -- the shatter demonstrably happened (the 6 is in the HP
/// total) and the board still read Frozen 1 afterwards."
///
/// BOTH HALVES OF THAT ARE TRUE, and the sentence was not the wrong half. One
/// Cryo Attack landed on a body that was Frozen AND wearing a Hydro aura, and
/// the two rules live in two powers inside ONE `AfterDamageReceived`
/// broadcast: <c>FrozenPower</c> Shattered and removed itself, then
/// <c>AuraPower</c> consumed the Hydro and resolved a Frozen reaction that put
/// a fresh stack back on.
///
/// THE SIM IS THE REFERENCE AND CANNOT REACH THAT BOARD: `effects.resolve_hit`
/// snapshots `was_frozen`, `reactions._react` does `enemy.frozen += 1`, and
/// the Shatter block then does `enemy.frozen = 0`. Reaction first, Shatter
/// after. So this is a parity fix, not a wording call, and the sim's half of
/// the pin is `tier0/tests/test_reactions.py`.
///
/// WHAT CAN BE PINNED HERE. A Shatter needs a live combat -- `CreatureCmd`,
/// `PowerCmd` and a `CombatState` -- which is outside the headless boundary
/// this project draws. What a headless test CAN read is the mark's own state
/// machine and the call graph that drives it, which is the same posture
/// `FurinaReframeRuleTests`' structural section takes for the Salon seam.
/// </summary>
public class ShatterRemovesFrozenTests
{
    /// <summary>`ReactionEffects` is `internal`, so the three seams below are
    /// reached by reflection -- the same posture `Il` itself takes toward the
    /// mod assembly, and the reason the type is resolved off a public one.
    /// </summary>
    private static readonly Type Reactions = typeof(FrozenPower).Assembly
        .GetType("KleeMod.Powers.ReactionEffects")!;

    private static void Call(string name, params object?[] args) =>
        Reactions.GetMethod(name, HeadlessGame.All)!.Invoke(null, args);

    private static bool Marked(Creature? target) =>
        (bool)Reactions.GetMethod("ShatteredThisHit", HeadlessGame.All)!
            .Invoke(null, new object?[] { target })!;

    private static int IndexOfCall(IReadOnlyList<string> sequence, string call)
    {
        for (var i = 0; i < sequence.Count; i++)
        {
            if (sequence[i] == call) return i;
        }
        return -1;
    }

    private static Creature Body() => Seat.Furina().Creature;

    [Fact]
    public void The_mark_names_one_creature_and_not_another()
    {
        // It suppresses the freeze on the body that Shattered, never a freeze
        // landing on a different body in the same broadcast (a Swirl spreads
        // an aura across the board, and the next hit into it must still
        // freeze).
        var shattered = Body();
        var other = Body();

        Call("MarkShattered", shattered);

        Assert.True(Marked(shattered));
        Assert.False(Marked(other));

        Call("ClearShatterMark");
    }

    [Fact]
    public void The_boundary_clears_the_mark()
    {
        // The lifetime is one damage event. A mark that outlived its broadcast
        // would swallow a real freeze later in the fight, which is a worse bug
        // than the one being fixed.
        var body = Body();
        Call("MarkShattered", body);

        Call("ClearShatterMark");

        Assert.False(Marked(body));
    }

    [Fact]
    public void The_shatter_marks_the_body_it_unfroze()
    {
        var calls = Il.Calls(Il.Method("FrozenPower", "AfterDamageReceived"));

        Assert.Contains("ReactionEffects.MarkShattered", calls);
        // The removal itself is unchanged: the Shatter still takes the whole
        // timer, which is NC-7 (R116) and the sim's `enemy.frozen = 0`.
        Assert.Contains("PowerCmd.Remove", calls);
    }

    [Fact]
    public void The_mark_is_set_after_the_shatter_damage_lands()
    {
        // ORDER MATTERS AND IS THE WHOLE TRICK. The Shatter deals its own
        // unblockable hit, and that hit opens its own `BeforeDamageReceived`
        // broadcast -- which CLEARS the mark. Marking before the damage would
        // therefore mark nothing at all.
        var sequence = Il.CallSequence(
            Il.Method("FrozenPower", "AfterDamageReceived"));

        var damage = IndexOfCall(sequence, "CreatureCmd.Damage");
        var mark = IndexOfCall(sequence, "ReactionEffects.MarkShattered");

        Assert.True(damage >= 0, string.Join(", ", sequence));
        Assert.True(mark > damage, string.Join(", ", sequence));
    }

    [Fact]
    public void Every_damage_event_clears_the_mark_first()
    {
        // `KleeElementalHooks.BeforeDamageReceived` is the one hook that runs
        // for every hit in the broadcast before any power's
        // `AfterDamageReceived`, which is exactly the lifetime the mark needs.
        var sequence = Il.CallSequence(
            Il.Method("KleeElementalHooks", "BeforeDamageReceived"));

        Assert.Contains("ReactionEffects.ClearShatterMark", sequence);
        // AND ABOVE EVERY GUARD, which is the half that matters: the first
        // thing this hook does after the clear is refuse an Unpowered hit, and
        // the Shatter's own nested damage IS one -- so a clear below that
        // return would never run on the hit whose mark it has to bound. Read
        // as an ordering rather than as index 0, because this is an `async`
        // method and the sequence opens with the state machine's own calls.
        var clear = IndexOfCall(sequence, "ReactionEffects.ClearShatterMark");
        var guard = IndexOfCall(sequence, "ValuePropExtensions.IsPoweredAttack");

        Assert.True(guard >= 0, string.Join(", ", sequence));
        Assert.True(clear < guard, string.Join(", ", sequence));
    }

    [Fact]
    public void The_badge_says_when_the_shatter_window_closes()
    {
        // `EB-517`. THE ONE PLACE A SEAT ACTED ON THE PRINTED TEXT AND THE
        // PRINTED TEXT WAS WRONG.
        //
        // Kokomi r18 lane 1, fight 5: "Its next action deals 50% less damage.
        // The first Attack to hit it Shatters for 6 unblockable damage and
        // removes Frozen" read as TWO INDEPENDENT RIDERS -- a halved action,
        // and a standing promise about the next Attack -- so the seat played a
        // 2-damage Attack into a 7-HP Brute expecting 2 + 6 and a free kill.
        // It dealt 2: the Brute had taken its halved action the turn before
        // and the freeze had gone with nothing having Shattered it.
        //
        // THE RULE WAS ALWAYS ONE ACTION LONG. `AfterSideTurnEnd` ticks the
        // counter down at the end of the enemy side's turn, which is LAW's
        // per-turn-decrementing Frozen. The face says so now, and the two
        // halves are pinned in one test so neither can move without the other.
        var face = string.Join(" ", Il.Strings(
            Il.Method("FrozenPower", "get_Localization")));
        Assert.Contains("Until it acts", face);

        Assert.Contains("PowerCmd.TickDownDuration",
            Il.Calls(Il.Method("FrozenPower", "AfterSideTurnEnd")));
    }

    [Fact]
    public void The_frozen_reaction_reads_the_mark()
    {
        // And only the Frozen branch does: the aura is still consumed, the
        // reaction still counts, and every other reaction is untouched.
        var calls = Il.Calls(Il.Method("ReactionEffects", "Resolve"));

        Assert.Contains("ReactionEffects.ShatteredThisHit", calls);
    }
}
