// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// `EB-216`, the Kokomi draft-6 half, and it is `GitsKurageMemory.cs` one rule
// over: the bridge serialises `creature.Powers`, so the arm's pending-Plans
// badge reaches the wire as an ID and an AMOUNT -- a COUNT and nothing else.
// Under draft 6 that is not enough to play her:
//
//   * WHICH Plans are waiting, and in what ORDER, is the whole of what the
//     next morning will be. A count says three things will happen and not
//     what they are;
//   * the Bake-Kurage is a PET, and a Plan is played ON it -- so a seat needs
//     an entity id to aim at, or it cannot write a Plan at all;
//   * Nereid's Ascension makes the queue's LENGTH stop being the number of
//     things that will happen, and The Moon Overlooks the Waters makes a Plan
//     happen twice over two turns. Neither is visible from a badge.
//
// WHAT THIS READS, AND WHY IT IS REFLECTION -- the same posture and the same
// reasons as `GitsKurageMemory.cs`: the rule is QUARANTINED inside the klee mod
// (`Powers/Prototype/KokomiPlan.cs`, compiled only under
// `-p:PrototypeCards=true`), so a compile-time reference would make this bridge
// refuse to load without the klee mod and would not compile at all against a
// RELEASE klee.dll, which does not contain the type. Reflection makes "no klee
// mod, or a release klee.dll" mean "no Plan rule", which is the truth. Every
// lookup is cached after the first attempt and every failure is swallowed into
// a null, because a state read must never throw.
//
// THE CONTRACT. `KleeMod.Powers.KokomiPlan.Snapshot(Player)` returns a plain
// Dictionary<string, object?> of primitives; this file invokes it and hands the
// result straight to the wire under `player.kokomi_plans`. The field names are
// the mod's, are documented on that method, and are read by
// `understudy/blindplay.py`. An ABSENT key means "no Plan rule in this build";
// an EMPTY map means "the rule is here and this player is not playing it".
// Those are different facts and a reader is entitled to tell them apart.
//
// READ-ONLY. Nothing here mutates a queue or a card. It is a serialiser.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Godot;
using MegaCrit.Sts2.Core.Models;

namespace STS2_MCP;

public static partial class McpMod
{
    private const string GitsKokomiPlanType = "KleeMod.Powers.KokomiPlan";
    private const string GitsKokomiPlanMethod = "Snapshot";

    private static bool _gitsPlanProbed;
    private static MethodInfo? _gitsPlanSnapshot;

    /// <summary>
    /// Locate the mod's snapshot method once. A null result is cached too: a
    /// release klee.dll does not contain the type and never will mid-session,
    /// and a state read should not pay for a full assembly walk on every poll.
    /// </summary>
    private static MethodInfo? GitsKokomiPlanSnapshot()
    {
        if (_gitsPlanProbed) return _gitsPlanSnapshot;
        _gitsPlanProbed = true;
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a =>
                {
                    try { return a.GetType(GitsKokomiPlanType, false); }
                    catch { return null; }
                })
                .FirstOrDefault(t => t != null);
            _gitsPlanSnapshot = type?.GetMethod(
                GitsKokomiPlanMethod,
                BindingFlags.Static | BindingFlags.Public);
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] kokomi plan probe failed: {ex.Message}");
            _gitsPlanSnapshot = null;
        }
        return _gitsPlanSnapshot;
    }

    /// <summary>
    /// The pending Plans for one player, or NULL when this build has no Plan
    /// rule in it. Null is what keeps the wire key ABSENT rather than
    /// present-and-empty, which is the distinction the header names.
    /// </summary>
    internal static Dictionary<string, object?>? GitsKokomiPlanState(
        object? player)
    {
        if (player == null) return null;
        var snapshot = GitsKokomiPlanSnapshot();
        if (snapshot == null) return null;
        try
        {
            return snapshot.Invoke(null, new[] { player })
                   as Dictionary<string, object?>;
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] kokomi plan snapshot failed: "
                        + $"{ex.Message}");
            return null;
        }
    }

    /// <summary>
    /// GItS LOCAL ADDITION (`EB-216`, the Kokomi draft-6 half). Can this card
    /// be aimed at the LOCAL player's pet?
    ///
    /// THE CARD IS ASKED, not a table. `CardModel.IsValidTarget` is the game's
    /// own gate and the base library prefixes it for every custom target type,
    /// so this answers for `Pet`, `PetOrSelf` and the Kokomi arm's own
    /// `PetOrEnemy` without the bridge knowing any of their values -- which it
    /// could not, since they are minted at `ModelDb.Init` and have no enum
    /// name to render.
    ///
    /// FALSE IS THE ANSWER FOR EVERY BOARD WITHOUT A PET, which is almost all
    /// of them, so the field is a cheap constant on a normal run.
    /// </summary>
    private static bool GitsCanTargetPet(CardModel card)
    {
        try
        {
            var owner = card.Owner;
            var pets = owner?.PlayerCombatState?.Pets;
            if (pets == null || pets.Count == 0) return false;
            foreach (var pet in pets)
            {
                if (pet.IsAlive && card.IsValidTarget(pet)) return true;
            }
            return false;
        }
        catch
        {
            // A state read must never throw. A card with no owner, or a
            // combat mid-teardown, is simply "no".
            return false;
        }
    }
}
