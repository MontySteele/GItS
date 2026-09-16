// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// EB-761: THE ARITHMETIC BEHIND `force_next_event`, WITH NO GAME TYPE IN IT.
//
// WHY THIS FILE IS SEPARATE FROM `GitsDebugState.cs`. The decision the op
// makes is one index calculation -- "which slot does the act read next, and
// where does the named event sit today" -- and `klee-mod/KleeTests` can
// compile THIS file and exercise that calculation headlessly, exactly as it
// already compiles `GitsPort.cs` and `GitsModalTargeting.cs`. The half that
// needs `ActModel` (reaching the act's `RoomSet` and swapping two entries)
// stays in `GitsDebugState.cs`, where it is three statements over the answer
// this file computes. One file, no fork.
//
// THE SEAM, AND WHY IT IS THE CHEAPEST ONE.
//
//   MegaCrit.Sts2.Core.Models.ActModel.PullNextEvent(RunState)
//     -> _rooms.EnsureNextEventIsValid(runState)
//     -> Hook.ModifyNextEvent(runState, _rooms.NextEvent)
//
//   MegaCrit.Sts2.Core.Rooms.RoomSet
//     public readonly List<EventModel> events;      // shuffled ONCE, at
//     public int eventsVisited;                     // run start
//     public EventModel NextEvent => events[eventsVisited % events.Count];
//
// `RunManager.GenerateRooms` builds that list as
// `AllEvents.Concat(ModelDb.AllSharedEvents).UnstableShuffle(rng)` at run
// start and never touches the rng again for events: every later `?` room is a
// READ off the same list at a moving cursor. So the whole of "force this
// event" is "put the named model at the cursor", which
//
//   * CONSUMES NO RNG, so the run's every other roll is where it would have
//     been. (A route that re-shuffled, or that generated a fresh event, would
//     move the stream and make every subsequent room a different room.)
//   * MINTS NOTHING. The event was already in this act's pending list, in
//     this run, and would have come up on its own eventually. The op changes
//     WHEN, and nothing else -- the same posture `GitsSeed` (select the run)
//     and `GitsGiveCard` (select a card the pools already hold) are held to.
//
// THE CURSOR IS NOT INDEX 0, AND THAT IS THE ONE THING EASY TO GET WRONG.
// `NextEvent` reads `events[eventsVisited % events.Count]`, and
// `eventsVisited` has already been incremented by every `?` room this act
// visited (`RoomSet.MarkVisited`) and by every skip `EnsureNextEventIsValid`
// made. "The head of the pending list" therefore means index
// `eventsVisited % events.Count`, which this file calls the SLOT. Writing to
// index 0 would be writing to a slot the act walked past on floor 3.
//
// WHAT THE SWAP COSTS, STATED RATHER THAN HIDDEN. Putting the target at the
// slot displaces whatever sat there to the target's old index. If the target
// sat AFTER the slot, that displaced event simply comes up later than it
// would have. If it sat BEFORE the slot -- an index this act has already
// walked past -- the displaced event lands behind the cursor and will not be
// offered again until the list wraps. Nothing is lost (the list is never
// shortened) and no rng moves either way; a scenario that forces an event has
// already given up comparability, which is what the route's guardrail says.
//
// ONE MORE THING THE SLOT DOES NOT PROMISE. `EnsureNextEventIsValid` runs
// BEFORE the read and walks the cursor forward past any event that fails
// `IsAllowed(runState)` or is already in `runState.VisitedEventIds`. So a
// forced event that is not allowed here, or that this run has already seen,
// would be silently stepped over -- the write would land and the `?` room
// would open on something else. `GitsDebugState` checks both against the live
// run and REFUSES rather than writing a no-op wearing an ok; this file is the
// arithmetic only and knows nothing about a run.

// `#nullable enable` because this file is compiled TWICE: into the bridge,
// whose project turns annotations on, and into `klee-mod/KleeTests`, whose
// project does not. Without the directive the `object?` below is a warning in
// the second build only, which is a difference between two compilations of one
// file and exactly the kind of thing that gets waved through.
#nullable enable

using System;
using System.Collections.Generic;

namespace STS2_MCP;

/// <summary>EB-761. Where the act's event cursor points, and where the named
/// event sits -- the whole decision `force_next_event` makes.</summary>
public static class GitsForceEvent
{
    /// <summary>The answer. `Found` false means the id is not in this act's
    /// pending list at all, which is a refusal and not a write.</summary>
    public readonly struct Placement
    {
        public Placement(bool found, int index, int slot, int count,
                         string resolved)
        {
            Found = found;
            Index = index;
            Slot = slot;
            Count = count;
            Resolved = resolved;
        }

        /// <summary>Whether the named event is in the list.</summary>
        public bool Found { get; }

        /// <summary>Where it sits today, or -1.</summary>
        public int Index { get; }

        /// <summary>The index `PullNextEvent` will read, or -1 for an empty
        /// list. This is `eventsVisited % events.Count`, NOT zero.</summary>
        public int Slot { get; }

        /// <summary>How long the pending list is.</summary>
        public int Count { get; }

        /// <summary>The id as the list spells it -- so a caller that matched
        /// case-insensitively can see what it actually reached.</summary>
        public string Resolved { get; }

        /// <summary>Whether a write is needed at all. A target already
        /// standing at the slot is the state the caller asked for, and the
        /// op answers ok without touching the list.</summary>
        public bool AlreadyNext => Found && Index == Slot;
    }

    /// <summary>Resolve `targetId` against `eventIds` and report where the
    /// cursor points.
    ///
    /// EXACT ORDINAL MATCH FIRST, CASE-INSENSITIVE SECOND, and the spelling
    /// that was found is reported back -- `GitsDebugState`'s standing rule
    /// for every id it resolves, for the reason `set_power` states: a caller
    /// that spelled it loosely is entitled to see which entry it reached.
    /// </summary>
    public static Placement Locate(IReadOnlyList<string> eventIds,
                                   int eventsVisited, string targetId)
    {
        var ids = eventIds ?? Array.Empty<string>();
        var count = ids.Count;
        if (count == 0) return new Placement(false, -1, -1, 0, "");

        // A NEGATIVE OR HUGE `eventsVisited` IS NOT THIS FILE'S TO JUDGE, but
        // it is this file's to survive: C#'s `%` keeps the sign of the left
        // operand, so a negative counter would index out of the list. The
        // game never produces one; the arithmetic is written so that a save
        // that did could not crash the route.
        var slot = ((eventsVisited % count) + count) % count;

        var target = (targetId ?? "").Trim();
        if (target.Length == 0) return new Placement(false, -1, slot, count, "");

        for (var i = 0; i < count; i++)
            if (string.Equals(ids[i], target, StringComparison.Ordinal))
                return new Placement(true, i, slot, count, ids[i]);
        for (var i = 0; i < count; i++)
            if (string.Equals(ids[i], target, StringComparison.OrdinalIgnoreCase))
                return new Placement(true, i, slot, count, ids[i]);
        return new Placement(false, -1, slot, count, "");
    }

    // ------------------------------------------- EB-770: run facts -------
    //
    // WHY A REFUSAL CARRIES NUMBERS AND NOT AN EXPLANATION.
    // `EventModel.IsAllowed(IRunState)` is a compiled method. When it answers
    // false the bridge knows only that; there is no source expression to quote
    // and no decompiler in the process to make one. What the bridge CAN do,
    // cheaply and read-only, is print the handful of run values every base
    // gate in 0.111.0 asks about -- the act index, the floor, gold, potions,
    // relics, the deck's removable and transformable counts, HP -- and let the
    // caller compare them against the gate, which `understudy/force_event.py`
    // prints from `tools/data/sts2_base_events.json` beside them.
    //
    // THE SPELLING IS THE TABLE'S. A fact is named after the member the gate
    // reads (`CurrentActIndex`, `TotalFloor`, `Gold`) so the two halves line
    // up word for word on the page a caller is reading. Where they could not
    // -- there is no member called `Deck.Cards.Any(IsRemovable)` -- the count
    // is spelled `RemovableCards` and the gate's own clause stands next to it.
    //
    // ONE PLAYER, SAID OUT LOUD. Every base gate is `Players.All(...)`, so a
    // co-op run's answer is the WORST player's and not the first one's. The
    // caller passes whichever player it read plus `playerCount`, and that
    // count is written into the facts so a two-player refusal cannot be read
    // as if it described the whole party.

    /// <summary>What the live run holds, for a caller comparing it against a
    /// gate. Every value is a plain number read off the run; nothing here is a
    /// judgement about whether the gate passes.</summary>
    public static Dictionary<string, object?> Facts(
        int currentActIndex, int totalFloor, int gold, int potions,
        int relics, int tradableRelics, int deckCards, int removableCards,
        int transformableCards, int currentHp, int maxHp, int playerCount)
    {
        return new Dictionary<string, object?>
        {
            ["CurrentActIndex"] = currentActIndex,
            ["TotalFloor"] = totalFloor,
            ["Gold"] = gold,
            ["Potions"] = potions,
            ["Relics"] = relics,
            ["TradableRelics"] = tradableRelics,
            ["DeckCards"] = deckCards,
            ["RemovableCards"] = removableCards,
            ["TransformableCards"] = transformableCards,
            ["CurrentHp"] = currentHp,
            ["MaxHp"] = maxHp,
            ["Players"] = playerCount
        };
    }

    /// <summary>The facts as one sentence, in the dictionary's own order.
    ///
    /// A SENTENCE AS WELL AS A DICTIONARY, because the refusal is read two
    /// ways: `understudy/force_event.py` prints the structured `run_facts`,
    /// while a caller holding only the error string -- an MCP client, a log
    /// line -- would otherwise see the same bare "IsAllowed is false" the
    /// round complained about.</summary>
    public static string DescribeFacts(Dictionary<string, object?>? facts)
    {
        if (facts == null || facts.Count == 0) return "";
        var parts = new List<string>(facts.Count);
        foreach (var pair in facts)
            parts.Add($"{pair.Key}={pair.Value}");
        return "This run holds: " + string.Join(", ", parts) + ".";
    }

    /// <summary>Swap the entries at `from` and `to`. A SWAP AND NOT AN INSERT:
    /// the list's length is what `NextEvent`'s modulo divides by, so a route
    /// that inserted would renumber every slot behind the cursor and change
    /// which event every LATER `?` room in the act opens. A swap moves exactly
    /// two entries and leaves the cycle the run was already on intact.
    ///
    /// Returns false, and writes nothing, for an index this list does not
    /// have or for a no-op swap.</summary>
    public static bool Swap<T>(IList<T> list, int from, int to)
    {
        if (list == null) return false;
        if (from < 0 || to < 0 || from >= list.Count || to >= list.Count)
            return false;
        if (from == to) return false;
        (list[from], list[to]) = (list[to], list[from]);
        return true;
    }
}
