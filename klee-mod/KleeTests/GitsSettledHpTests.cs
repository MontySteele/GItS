#nullable enable

using STS2_MCP;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-676. THE TWO STATES THE HP FIGURE CAN BE IN, PINNED HEADLESSLY.
///
/// The defect, from Kokomi round 26 lane 1 fight 4: the victory screen printed
/// HP 25/80 and the next screen 16/80. PR #546 settled that there is ONE HP
/// field on this wire -- `BuildPlayerState` writes `creature.CurrentHp` on
/// every screen -- so the two numbers are that field at two moments, the first
/// taken before the fight's own end-of-turn queue (Constrict's 9) had drained
/// into it, and "the seat chose its map off the wrong number".
///
/// WHY A PIN AND NOT A LOOK. The obvious predicate is
/// `!CombatManager.Instance.IsInProgress`, and it is wrong in the one way that
/// cannot be seen: the game's own summary of that property says it is "False
/// when ... the combat is ending (the last monster has been killed)", which is
/// the kill screen itself. A flag built on it would have answered `settled` on
/// the exact frame the defect was filed against, and every smoke test that did
/// not happen to end a fight on a damage-over-time power would have passed.
/// So both states are pinned here, on the same facts the state builder reads
/// off the live game, rather than being discovered by another seat.
///
/// The predicate lives in `vendor/STS2_MCP/gits/GitsSettledHp.cs`, which is
/// deliberately free of Godot, Harmony and game types so this file compiles
/// THAT source and not a fork of it -- `GitsSkipActTests` and
/// `GitsForceEventTests`' arrangement, for their reason.
/// </summary>
public class GitsSettledHpTests
{
    /// <summary>THE KILL SCREEN, as the r26 seat met it: the last monster is
    /// dead while the turn state is still in progress, so `IsEnding` is true,
    /// and `CombatManager.Reset` has not dropped it, so `CurrentCombatId` is
    /// still non-null.
    /// The queue happens to be between actions at the instant of the read,
    /// which is why clause (1) alone would not have caught this.</summary>
    [Fact]
    public void A_fight_that_has_ended_but_not_been_torn_down_is_not_settled()
    {
        var verdict = GitsSettledHp.Decide(
            actionQueueRunning: false, actionInFlight: false,
            combatStateStands: true, combatEnding: true);

        Assert.False(verdict.Settled);
        Assert.Equal(GitsSettledHp.CombatTearingDownReason, verdict.Reason);
    }

    /// <summary>THE NEXT SCREEN. The run has left the room, `Reset` dropped
    /// the turn state, and nothing is executing. This is the figure the page
    /// may print plainly.</summary>
    [Fact]
    public void The_screen_after_the_teardown_is_settled()
    {
        var verdict = GitsSettledHp.Decide(
            actionQueueRunning: false, actionInFlight: false,
            combatStateStands: false, combatEnding: false);

        Assert.True(verdict.Settled);
        Assert.Equal("", verdict.Reason);
    }

    /// <summary>
    /// PROOFS-8a (PR #573). THE POST-COMBAT SCREENS, WHICH THE FIRST DRAFT
    /// GOT WRONG ON ALL OF THEM.
    ///
    /// THE FIND: `hp_settled` was FALSE on 26 of 26 post-combat map, rewards
    /// and card-reward reads, and true only on the event, treasure and
    /// card-select screens that never follow a fight. Clause (2) was
    /// `IsOverOrEnding`, which is `IsEnding || !IsInProgress` -- true from the
    /// moment a fight stops being in progress and true for every screen after
    /// it -- while `CurrentCombatId` stays non-null until the run leaves the
    /// ROOM. Two facts that both linger are not a window; they are a latch,
    /// and the flag that was meant to let the page stop hedging hedged
    /// everything instead.
    ///
    /// `IsEnding` IS THE HALF THAT DOES NOT LINGER: it needs a turn state
    /// that is IN PROGRESS with its enemies dead (or a pending loss), which
    /// is the kill screen and is over the instant the combat is.
    /// </summary>
    [Fact]
    public void The_rewards_screen_and_the_map_after_a_fight_are_settled()
    {
        // The combat object has not been dropped -- `Reset` runs when the run
        // leaves the room -- but the fight is over and nothing is executing.
        var verdict = GitsSettledHp.Decide(
            actionQueueRunning: false, actionInFlight: false,
            combatStateStands: true, combatEnding: false);

        Assert.True(verdict.Settled);
        Assert.Equal("", verdict.Reason);
    }

    /// <summary>And the queue clause still holds on those screens: an
    /// end-of-combat effect still draining is an HP change that has not
    /// landed, whatever room the page is drawing.</summary>
    [Fact]
    public void A_rewards_screen_with_work_in_flight_is_still_not_settled()
    {
        var verdict = GitsSettledHp.Decide(
            actionQueueRunning: false, actionInFlight: true,
            combatStateStands: true, combatEnding: false);

        Assert.False(verdict.Settled);
        Assert.Equal(GitsSettledHp.ActionRunningReason, verdict.Reason);
    }

    /// <summary>A LIVE FIGHT SITTING IN THE PLAY PHASE IS SETTLED, and that is
    /// a decision rather than an oversight: with nothing executing,
    /// `CurrentHp` is the number the player is on, and a flag that cried
    /// "provisional" through every combat page would be a flag nobody
    /// reads.</summary>
    [Fact]
    public void A_live_fight_with_an_idle_queue_is_settled()
    {
        var verdict = GitsSettledHp.Decide(
            actionQueueRunning: false, actionInFlight: false,
            combatStateStands: true, combatEnding: false);

        Assert.True(verdict.Settled);
    }

    /// <summary>Clause (1), the one that holds on every screen: an action
    /// still executing is an HP change that has not landed.</summary>
    [Fact]
    public void A_running_action_queue_is_never_settled()
    {
        var verdict = GitsSettledHp.Decide(
            actionQueueRunning: true, actionInFlight: false,
            combatStateStands: false, combatEnding: false);

        Assert.False(verdict.Settled);
        Assert.Equal(GitsSettledHp.ActionRunningReason, verdict.Reason);
    }

    /// <summary>The belt on clause (1). `CurrentlyRunningAction` is read as
    /// well as `IsRunning` because a non-null action is work in flight
    /// whatever the queue task says about itself.</summary>
    [Fact]
    public void An_action_in_flight_is_never_settled()
    {
        var verdict = GitsSettledHp.Decide(
            actionQueueRunning: false, actionInFlight: true,
            combatStateStands: false, combatEnding: false);

        Assert.False(verdict.Settled);
        Assert.Equal(GitsSettledHp.ActionRunningReason, verdict.Reason);
    }

    /// <summary>The queue is reported FIRST, because it is the clause a reader
    /// can check against the page in front of them.</summary>
    [Fact]
    public void The_queue_is_the_reason_given_when_both_clauses_refuse()
    {
        var verdict = GitsSettledHp.Decide(
            actionQueueRunning: true, actionInFlight: true,
            combatStateStands: true, combatEnding: true);

        Assert.False(verdict.Settled);
        Assert.Equal(GitsSettledHp.ActionRunningReason, verdict.Reason);
    }

    /// <summary>FAIL CLOSED. A read of the live game that threw publishes
    /// unsettled with a reason naming the throw -- never a settled claim, and
    /// never a silent one.</summary>
    [Fact]
    public void An_unreadable_game_is_never_claimed_to_be_settled()
    {
        var verdict = GitsSettledHp.Unreadable();

        Assert.False(verdict.Settled);
        Assert.Equal(GitsSettledHp.UnreadableReason, verdict.Reason);
    }

    /// <summary>The two wire keys are spelled ONCE, here and in
    /// `understudy/blindplay_faces.py`, and the blind page reads them by these
    /// names. A rename that moved one without the other would take the note
    /// off nothing and put it on everything.</summary>
    [Fact]
    public void The_wire_keys_are_the_ones_the_blind_page_reads()
    {
        Assert.Equal("hp_settled", GitsSettledHp.SettledKey);
        Assert.Equal("hp_unsettled_reason", GitsSettledHp.ReasonKey);
    }
}
