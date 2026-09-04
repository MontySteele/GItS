// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// `EB-405`, and it is `GitsKokomiPlan.cs` one arm over, for the same reason
// that one exists: a fact the rule decides and the board does not keep.
//
// WHAT THE SEAT SAW (Furina round 4, run 1, (c) 4). A Salon member's
// performance named no target on the page -- "Crabaletta chose its own enemy
// and left a Hydro aura on a body the seat had not picked" -- in a kit whose
// readable decision is which element lands on which aura. The page was not
// dropping the fact: no Salon block reached this wire at all. The only Salon
// row a seat ever saw was the counter power's static rulebook sentence, which
// carries the company COUNT and by construction cannot carry a body.
//
// AND THE FACT IS GONE A MOMENT LATER. `SalonPowers.PerformMember` draws its
// target from `Rng.CombatTargets` over `HittableEnemies` and hands it to
// `ElementalHit.Deal`, which returns the DAMAGE and not the creature. Which
// body was picked, and what it is wearing afterwards, are decided inside that
// switch and thrown away by it.
//
// WHAT THIS READS, AND WHY IT IS REFLECTION -- the same posture and the same
// reasons as `GitsKokomiPlan.cs`: the rule is QUARANTINED inside the klee mod
// (`Powers/Prototype/FurinaReframeLedger.cs`, compiled only under
// `-p:PrototypeCards=true`), so a compile-time reference would make this
// bridge refuse to load without the klee mod and would not compile at all
// against a RELEASE klee.dll, which does not contain the type. Reflection
// makes "no klee mod, or a release klee.dll" mean "no reframe", which is the
// truth. Every lookup is cached after the first attempt and every failure is
// swallowed into a null, because a state read must never throw.
//
// THE CONTRACT. `KleeMod.Powers.FurinaReframeLedger.Snapshot(Player)` returns
// a plain Dictionary<string, object?> of primitives; this file invokes it and
// hands the result straight to the wire under `player.furina_salon`. The field
// names are the mod's, are documented on that method, and are read by
// `understudy/blindplay_board.furina_salon`. An ABSENT key means "no reframe
// in this build"; an EMPTY map means "the rule is here and this player is not
// playing it". Those are different facts and a reader is entitled to tell them
// apart.
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
    private const string GitsFurinaSalonType =
        "KleeMod.Powers.FurinaReframeLedger";
    private const string GitsFurinaSalonMethod = "Snapshot";

    private static bool _gitsSalonProbed;
    private static MethodInfo? _gitsSalonSnapshot;

    /// <summary>
    /// Locate the mod's snapshot method once. A null result is cached too: a
    /// release klee.dll does not contain the type and never will mid-session,
    /// and a state read should not pay for a full assembly walk on every poll.
    /// </summary>
    private static MethodInfo? GitsFurinaSalonSnapshot()
    {
        if (_gitsSalonProbed) return _gitsSalonSnapshot;
        _gitsSalonProbed = true;
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a =>
                {
                    try { return a.GetType(GitsFurinaSalonType, false); }
                    catch { return null; }
                })
                .FirstOrDefault(t => t != null);
            _gitsSalonSnapshot = type?.GetMethod(
                GitsFurinaSalonMethod,
                BindingFlags.Static | BindingFlags.Public);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] furina salon probe failed: {ex.Message}");
            _gitsSalonSnapshot = null;
        }
        return _gitsSalonSnapshot;
    }

    /// <summary>
    /// This turn's Salon performances for one player, or NULL when this build
    /// has no reframe in it. Null is what keeps the wire key ABSENT rather
    /// than present-and-empty, which is the distinction the header names.
    /// </summary>
    internal static Dictionary<string, object?>? GitsFurinaSalonState(
        object? player)
    {
        if (player == null) return null;
        var snapshot = GitsFurinaSalonSnapshot();
        if (snapshot == null) return null;
        try
        {
            return snapshot.Invoke(null, new[] { player })
                   as Dictionary<string, object?>;
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] furina salon snapshot failed: "
                        + $"{ex.Message}");
            return null;
        }
    }
}
