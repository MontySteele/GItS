// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// `EB-735`, and it is `GitsFurinaSalon.cs` one arm over, for the reason that
// one exists: a fact the rule decides and the board does not keep.
//
// WHAT THE SEATS SAW (Furina, the Stage, round one, sec.2). "Nothing on the
// blind-play page names a performer, a seat or a bar ... in some 550 actions
// no seat ever knew who was on stage or what a bar held. Each learned the
// roster from one glossary line and inferred bars by firing readers and
// reading the result backwards." All three seats read the cast as "one
// anonymous pool with three names", and every finding in that round is read
// through the hole.
//
// AND `pets` WAS NOT ENOUGH. The three performers ARE pets, so their bodies
// and their HP already reach this wire through `BuildPetsState` -- but a pet
// row carries no SEAT, and the seat is the whole kit: rule 6 sends every
// attack at the front one, rule 8 spends from the front one, rule 5 raises the
// back one. The engine's pet list is in the order the bodies were fielded,
// which a rotation and a departure both break. So the seat order is asked of
// the ledger, which is where it lives, and the pet rows are annotated from the
// same answer (`BuildPetsState`) so the two surfaces cannot disagree.
//
// AND THE LOG, which no snapshot of the bars can carry: what happened to them
// between two screens. A performer arriving, acting, bowing, leaving or
// rotating is a beat a seat either watched or did not, and the two it can
// never watch -- the end-of-turn sweep and what the enemies' attacks took off
// the lead -- are exactly the two the bars change most on.
//
// WHAT THIS READS, AND WHY IT IS REFLECTION -- the same posture and the same
// reasons as `GitsFurinaSalon.cs`: the rule is QUARANTINED inside the klee mod
// (`Powers/Prototype/FurinaStageLedger.cs`, compiled only under
// `-p:PrototypeCards=true`), so a compile-time reference would make this
// bridge refuse to load without the klee mod and would not compile at all
// against a RELEASE klee.dll, which does not contain the type. Reflection
// makes "no klee mod, or a release klee.dll" mean "no Stage", which is the
// truth. Every lookup is cached after the first attempt and every failure is
// swallowed into a null, because a state read must never throw.
//
// THE CONTRACT. `KleeMod.Powers.FurinaStageLedger.Snapshot(Player)` returns a
// plain Dictionary<string, object?> of primitives; this file invokes it and
// hands the result straight to the wire under `player.furina_stage`. The field
// names are the mod's, are documented on that method, and are read by
// `understudy/blindplay_board.furina_stage`. An ABSENT key means "no Stage in
// this build"; an EMPTY map means "the rule is here and this player is not
// playing it". Those are different facts and a reader is entitled to tell them
// apart -- and a POPULATED map with an empty seat list is a third, "the stage
// is empty", which is the one a seat about to spend a rider most needs.
//
// READ-ONLY. Nothing here mutates a ledger or a stage. It is a serialiser.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Godot;

namespace STS2_MCP;

public static partial class McpMod
{
    private const string GitsFurinaStageType =
        "KleeMod.Powers.FurinaStageLedger";
    private const string GitsFurinaStageMethod = "Snapshot";

    private static bool _gitsStageProbed;
    private static MethodInfo? _gitsStageSnapshot;

    /// <summary>
    /// Locate the mod's snapshot method once. A null result is cached too: a
    /// release klee.dll does not contain the type and never will mid-session,
    /// and a state read should not pay for a full assembly walk on every poll.
    /// </summary>
    private static MethodInfo? GitsFurinaStageSnapshot()
    {
        if (_gitsStageProbed) return _gitsStageSnapshot;
        _gitsStageProbed = true;
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a =>
                {
                    try { return a.GetType(GitsFurinaStageType, false); }
                    catch { return null; }
                })
                .FirstOrDefault(t => t != null);
            _gitsStageSnapshot = type?.GetMethod(
                GitsFurinaStageMethod,
                BindingFlags.Static | BindingFlags.Public);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] furina stage probe failed: {ex.Message}");
            _gitsStageSnapshot = null;
        }
        return _gitsStageSnapshot;
    }

    /// <summary>
    /// The stage for one player, or NULL when this build has no Stage in it.
    /// Null is what keeps the wire key ABSENT rather than present-and-empty,
    /// which is the distinction the header names.
    /// </summary>
    internal static Dictionary<string, object?>? GitsFurinaStageState(
        object? player)
    {
        if (player == null) return null;
        var snapshot = GitsFurinaStageSnapshot();
        if (snapshot == null) return null;
        try
        {
            return snapshot.Invoke(null, new[] { player })
                   as Dictionary<string, object?>;
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] furina stage snapshot failed: "
                        + $"{ex.Message}");
            return null;
        }
    }

    /// <summary>
    /// `{combat id -> (member, seat index)}` for this player's performers, or
    /// an empty map on any board that has no stage.
    ///
    /// TAKEN OFF THE SAME SNAPSHOT the block above is built from, so the seat a
    /// `pets` row claims and the seat the stage block prints are one answer
    /// read twice rather than two answers that happen to agree today.
    /// </summary>
    internal static Dictionary<string, (string Member, int Seat)>
        GitsFurinaStageSeats(object? player)
    {
        var seats = new Dictionary<string, (string, int)>();
        if (GitsFurinaStageState(player) is not { } stage) return seats;
        if (stage.TryGetValue("seats", out var rowsObj)
            && rowsObj is IEnumerable<object?> rows)
        {
            foreach (var row in rows)
            {
                if (row is not Dictionary<string, object?> seat) continue;
                var id = seat.TryGetValue("entity_id", out var idObj)
                    ? idObj as string : null;
                if (string.IsNullOrEmpty(id)) continue;
                var member = seat.TryGetValue("member", out var m)
                    ? m as string ?? "" : "";
                var index = seat.TryGetValue("seat", out var i) && i is int n
                    ? n : -1;
                seats[id!] = (member, index);
            }
        }
        return seats;
    }
}
