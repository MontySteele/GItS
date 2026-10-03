using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Vfx;

/// <summary>
/// FURINA'S PERFORMERS ACT AND FLINCH ON SCREEN (motion pass, 2026-10-02).
///
/// Every performer scene (<c>furina/model/usher.tscn</c>, <c>chevalmarin</c>,
/// <c>crabaletta</c> and the twelve <c>guest_*.tscn</c>) ships the four-state
/// contract with an attack and a hurt clip, and nothing ever played either:
/// an act's damage goes out through <c>ElementalHit.DealUnelemented</c> with
/// Furina as the dealer, and a hit on a performer is written to its bar with
/// <c>CreatureCmd.SetMaxAndCurrentHp</c>, which sends no "Hit".
///
/// THE BAKE-KURAGE'S PATTERN, one pet over (<see cref="KurageBeat"/>): the
/// game's own animation door, <c>CreatureCmd.TriggerAnim</c>, which for a
/// spine-less body lands in <see cref="CreatureAnimationRouter"/>. No new
/// art and no new node.
///
/// HEADLESS-SAFE BY THE ENGINE'S OWN GUARD: <c>TriggerAnim</c> returns early
/// when the creature has no node, which is always in KleeTests and the sim.
///
/// QUARANTINED with the stage. `Vfx/Prototype/**` is Compile Remove'd without
/// `-p:PrototypeCards=true`.
/// </summary>
internal static class StagePerformerBeat
{
    /// <summary>
    /// How long a performer's lunge holds before its act resolves. Shorter
    /// than the Bake-Kurage's 0.35 s because a full stage acts three or four
    /// times in one end-of-turn sweep, and Full House repeats each act.
    /// <c>TriggerAnim</c> halves it in fast mode on its own.
    /// </summary>
    private const float ActSeconds = 0.25f;

    /// <summary>The performer acts: its scene's attack state, then the beat.
    /// Awaited by the act, so the act's number lands after the lunge.</summary>
    public static async Task Act(Creature? performer)
    {
        if (!Animates(performer)) return;
        await CreatureCmd.TriggerAnim(performer!, "Attack", ActSeconds);
    }

    /// <summary>
    /// The performer flinches: its scene's hurt state, with no wait, which is
    /// what <c>CreatureCmd.Damage</c> itself does for a hit body
    /// (<c>TriggerAnim(receiver, "Hit", 0f)</c>). Fire-and-forget because the
    /// caller is the synchronous damage-order seam; the zero wait means the
    /// task has nothing to hold.
    /// </summary>
    public static void Flinch(Creature? performer, int loss)
    {
        if (!Flinches(performer is { IsDead: false }, loss)) return;
        _ = CreatureCmd.TriggerAnim(performer!, "Hit", 0f);
    }

    internal static bool Animates(Creature? performer) =>
        performer is { IsDead: false };

    /// <summary>A flinch needs a standing body and a bar that actually lost
    /// something: a hit the lead's Bow Block caught whole draws nothing, as a
    /// fully blocked hit draws nothing in the base.</summary>
    internal static bool Flinches(bool standing, int loss) => standing && loss > 0;
}
