using System;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Vfx;

namespace KleeMod.Vfx;

/// <summary>
/// A PERFORMER'S FANFARE LOSS, SHOWN AS THE BASE GAME SHOWS HP LOSS.
///
/// THE FIND ([USER], a full Furina run on 0.2.3820+proto): "I didn't notice
/// any Fanfare decaying." Rule 12 ran (<c>FurinaStageLedger.Fade</c>), and so
/// did every hit on the lead (<c>FurinaStageLedger.Absorb</c>), but a
/// performer's bar is written with <c>CreatureCmd.SetMaxAndCurrentHp</c>,
/// which draws no number: the only trace of either loss was the bar being
/// shorter than it was.
///
/// SO THE LOSS POPS THE ENGINE'S OWN DAMAGE NUMBER over the performer that
/// lost it: <c>NDamageNumVfx</c>, parented where <c>CreatureCmd.Damage</c>
/// parents it (the creature's vfx container, or the run's global UI). No new
/// art, no new wording; the number is the Fanfare the performer lost.
///
/// TWO CALLERS: a hit on the lead (<c>FurinaStage.AbsorbHit</c>, at the hit)
/// and rule 12 (<c>FurinaStage.FadeAndShow</c>, after the acts, one per
/// performer that faded).
///
/// HEADLESS-SAFE. <see cref="Requested"/> is raised first and touches no Godot
/// object, so a test can count the pops; the drawing is a separate method that
/// runs only once a combat room exists, which it never does in `dotnet test`
/// (KleeTests/README.md: anything touching a Godot object is process death).
///
/// QUARANTINED. <c>Vfx/Prototype/**</c> is Compile Remove'd without
/// <c>-p:PrototypeCards=true</c>.
/// </summary>
public static class FurinaStageLossPop
{
    /// <summary>Raised for every pop asked for, with the performer and the
    /// Fanfare it lost, before anything is drawn. The test seam, and the only
    /// part of this class `dotnet test` can reach.</summary>
    public static event Action<StagePerformer, int>? Requested;

    /// <summary>Pop <paramref name="loss"/> over <paramref name="seat"/>'s
    /// body. A no-op for a loss of 0 or less.</summary>
    public static void Show(StageSeat? seat, int loss)
    {
        if (seat == null || loss <= 0) return;
        Requested?.Invoke(seat.Who, loss);
        if (seat.Pet is not { IsDead: false } pet) return;
        if (NCombatRoom.Instance is not { } room) return;
        try
        {
            Draw(room, pet, loss);
        }
        catch (Exception e)
        {
            // A number that cannot be drawn must not take the hit or the end
            // of turn down with it: the bar is already right.
            Log.Warn($"[{KleeMod.ModId}] stage: loss number skipped: {e}");
        }
    }

    /// <summary>
    /// The engine's own pop, placed as the engine places it. Asked with
    /// <c>requireInteractable: false</c> because a pet's node need not be
    /// interactable, and ONLY once the body has a node: without one the
    /// engine's overload spawns the number at the screen origin.
    /// </summary>
    [MethodImpl(MethodImplOptions.NoInlining)]
    private static void Draw(NCombatRoom room, Creature pet, int loss)
    {
        if (room.GetCreatureNode(pet) == null) return;
        var number = NDamageNumVfx.Create(pet, loss, requireInteractable: false);
        if (number == null) return;
        if (pet.GetVfxContainer() is { } container)
        {
            container.AddChildSafely(number);
        }
        else
        {
            NRun.Instance?.GlobalUi.AddChildSafely(number);
        }
    }
}
