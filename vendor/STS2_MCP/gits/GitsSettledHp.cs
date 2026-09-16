// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// EB-676: IS THE HP ON THIS SCREEN THE HP THE RUN IS ACTUALLY ON?
//
// THE DEFECT. Kokomi round 26, lane 1, fight 4: the victory screen printed
// HP 25/80 and the next screen 16/80, and the seat chose its map off the wrong
// number. PR #546 established WHICH READ IS STALE and it is neither a second
// field nor a save -- `BuildPlayerState` writes `creature.CurrentHp` on every
// screen, so the two numbers are ONE FIELD AT TWO MOMENTS. The earlier moment
// was before the fight's own end-of-turn queue (Constrict's 9) had drained
// into it. The python half could only say so in a note on every such move;
// this file is what lets that note come off when there is nothing in flight.
//
// WHY `!CombatManager.Instance.IsInProgress` IS NOT THE PREDICATE, and it is
// the obvious wrong answer. The game's own summary of that property says it is
// "False when ... the combat is ending (the last monster has been killed)".
// The kill screen is exactly that window: `IsInProgress` is ALREADY false
// while `EndCombatInternal` is still running hooks and the action queue is
// still draining. A flag built on it would have read `settled` on the very
// frame the defect was filed against.
//
// THE PREDICATE, IN TWO CLAUSES, AND WHY EACH IS NEEDED.
//
//   (1) NOTHING IS EXECUTING. `RunManager.Instance.ActionExecutor` is the one
//       thing that pulls actions off the queue set and runs them, and HP moves
//       are actions. `IsRunning` is false exactly when its queue task has
//       completed -- i.e. `GetReadyAction()` handed back null and the drain
//       finished -- and `CurrentlyRunningAction` is the belt: a non-null
//       action is work in flight whatever the task says. Both read, because
//       an HP write sitting one action away is the whole of this defect.
//
//   (2) NO COMBAT IS STANDING IN ITS OWN TEARDOWN. `CurrentCombatId` is
//       `_turnState?.Id`, and `CombatManager.Reset` drops `_turnState`
//       wholesale -- so a non-null id means a combat object still exists.
//       Paired with `IsEnding` -- the game's own "combat is in progress but
//       all the enemies are dead and nothing is stopping it from ending, or
//       a pending loss is waiting to be processed" -- that pair is precisely
//       the window between the last monster dying and the room being torn
//       down: the kill screen.
//
// CLAUSE (2) WAS `IsOverOrEnding` AND THAT WAS TOO WIDE (proofs-8a, PR #573).
// Its finding: `hp_settled` was FALSE on 26 of 26 post-combat map, rewards
// and card-reward reads, and true only on the event, treasure and card-select
// screens that never follow a fight. The reason is written into this file's
// own first draft -- "off the map the first half is false" -- and it is not
// true: `Reset` runs when the run leaves the ROOM, not when the fight ends,
// so `CurrentCombatId` is still non-null all the way across the rewards
// screen and onto the map. And `IsOverOrEnding` is `IsEnding || !IsInProgress`
// (decompiled), so the moment `IsInProgress` goes false it is true and STAYS
// true for every screen until the next `SetUpCombat`. Two facts that both
// linger are not a window; they are a latch, and the flag the page was given
// to stop hedging hedged everything instead.
//
// `IsEnding` IS THE HALF THAT DOES NOT LINGER: it is false unless a
// turn state is IN PROGRESS with its enemies dead (or a loss pending), which
// is the kill screen and is over the moment the combat stops being in
// progress. The window `EB-676` was filed on is inside it, and the
// post-combat screens are outside it. The boundary-point warning the game
// attaches to `IsEnding` is about using it ALONE to decide "should I skip
// this effect"; here it is paired with a live id and read only as "is this
// fight in the act of ending", which is the question it answers exactly.
//
// So the unsettled states are "an action is running" and "a live combat is in
// the act of ending", and everything else -- the map, the rewards screen, a
// shop, a rest, an event, and a live fight sitting in the play phase with an
// empty queue -- is settled. A live fight IS settled by this test,
// deliberately: mid-turn with nothing executing, `CurrentHp` is the number
// the player is on, and a flag that cried "provisional" through every combat
// would be a flag nobody reads.
//
// FAIL CLOSED. Every caller-supplied fact this file cannot read for itself
// arrives as a bool; `McpMod.StateBuilder.cs` reads them inside a try/catch
// and, on any throw, publishes `settled: false` with the reason naming the
// throw. An unsettled claim costs a note on a page. A settled claim that is
// wrong is the r26 defect again, wearing a badge that says it is fine.
//
// NO GAME TYPE IN THIS FILE, on `GitsPort.cs`'s and `GitsSkipAct.cs`'s terms
// and for the same reason: the decision has exactly one way to look right and
// be wrong (clause 2 above), the wrong version passes every smoke test that
// does not happen to end a fight on a damage-over-time power, and
// `klee-mod/KleeTests/GitsSettledHpTests.cs` compiles THIS file to pin both
// states rather than a fork of it.

namespace STS2_MCP;

/// <summary>EB-676. Whether the HP figure this state payload carries is the
/// figure the run has settled on, or one read with work still in flight.</summary>
public static class GitsSettledHp
{
    /// <summary>The wire key the answer is published under. Spelled once so
    /// the bridge and the blind page cannot drift apart.</summary>
    public const string SettledKey = "hp_settled";

    /// <summary>The wire key the reason is published under, written only when
    /// the answer is false.</summary>
    public const string ReasonKey = "hp_unsettled_reason";

    /// <summary>What the flag says when a read of the live game threw. Never
    /// a claim that the figure is fine.</summary>
    public const string UnreadableReason =
        "the bridge could not read the combat and action-queue state, so it "
        + "will not claim this figure has settled";

    /// <summary>Why clause (1) refused.</summary>
    public const string ActionRunningReason =
        "an action is still executing, and an HP change one action away has "
        + "not landed in this figure yet";

    /// <summary>Why clause (2) refused -- the r26 kill screen, by name.</summary>
    public const string CombatTearingDownReason =
        "the fight is over but its combat state has not been dropped yet, so "
        + "end-of-turn effects belonging to it may still land in this figure";

    /// <summary>The answer and, when it is false, the sentence saying why.</summary>
    public readonly struct Verdict
    {
        public Verdict(bool settled, string reason)
        {
            Settled = settled;
            Reason = reason;
        }

        /// <summary>True only when nothing in flight can still move the HP on
        /// this payload.</summary>
        public bool Settled { get; }

        /// <summary>Why not, in the reader's words, or the empty string.</summary>
        public string Reason { get; }
    }

    /// <summary>Decide, from the four facts the state builder reads off the
    /// live game.
    ///
    /// `actionQueueRunning` is `RunManager.Instance.ActionExecutor.IsRunning`,
    /// `actionInFlight` is its `CurrentlyRunningAction != null`,
    /// `combatStateStands` is `CombatManager.Instance.CurrentCombatId != null`
    /// (the combat's turn state has not been dropped by `Reset`), and
    /// `combatEnding` is `CombatManager.Instance.IsEnding` -- NOT
    /// `IsOverOrEnding`, which latches true for every screen after a fight
    /// (proofs-8a; the block at the top of this file has the whole
    /// argument).</summary>
    public static Verdict Decide(bool actionQueueRunning, bool actionInFlight,
                                 bool combatStateStands, bool combatEnding)
    {
        // THE QUEUE FIRST, because it is the clause that holds on every screen
        // in the game and the one a reader can check against the page: an
        // action running is work whose result is not on this payload.
        if (actionQueueRunning || actionInFlight)
            return new Verdict(false, ActionRunningReason);

        // THE KILL SCREEN. A combat object that still exists AND is in the
        // act of ending is the r26 window and nothing else: during a live
        // fight with enemies alive the second half is false, and once the
        // fight is over -- rewards, map, everything after -- it is false
        // again. Both halves have to be live at once, which is what the
        // first draft's `IsOverOrEnding` could not say.
        if (combatStateStands && combatEnding)
            return new Verdict(false, CombatTearingDownReason);

        return new Verdict(true, "");
    }

    /// <summary>The verdict for a read that threw. Always unsettled.</summary>
    public static Verdict Unreadable() => new Verdict(false, UnreadableReason);
}
