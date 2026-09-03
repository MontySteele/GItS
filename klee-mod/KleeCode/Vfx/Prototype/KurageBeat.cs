using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes.Vfx;

namespace KleeMod.Vfx;

/// <summary>
/// THE BAKE-KURAGE'S BEAT: the two seconds of screen time that say the
/// jellyfish just did something (`EB-316`, `EB-317`).
///
/// WHAT WAS WRONG IS NOT THAT THE RULES WERE WRONG. Both rows are legibility
/// defects on rules that already resolve correctly. The Tamakushi Casket's
/// 2-Hydro strike landed in the same frame as the card that caused it, so its
/// damage number arrived on top of the card's and read as one bigger hit --
/// [USER] "had to remind myself why" and the round-3 seat saw "no line, no
/// announcement". The morning drain carried out every Plan with no pause and
/// no picture, so the strip went from four thumbnails to none between frames
/// and two seats asked for a carry-out moment. Neither is fixed by changing a
/// number; both are fixed by spending TIME and NAMING THE SOURCE.
///
/// THREE ENGINE COMMANDS AND NO NEW ART, which is the whole of this file:
///
///   * <see cref="Act"/> is <c>CreatureCmd.TriggerAnim(pet, "Attack", w)</c>.
///     That is the game's own animation door, and for a spine-less modded
///     creature it lands in <c>CreatureAnimationRouter</c>, which
///     travels the pet scene's AnimationTree to its <c>attack</c> state --
///     the four-state contract <c>bake_kurage.tscn</c> already ships. The
///     command's own <c>waitTime</c> is the beat: it is what stops the
///     jellyfish's hit from arriving in the same frame as the card's.
///   * <see cref="Say"/> is <c>NSpeechBubbleVfx.Create(text, speaker, secs,
///     colour)</c> parented to <c>Creature.GetVfxContainer()</c> -- exactly
///     what <c>TalkCmd.Play</c> does, minus the <c>LocString</c>. TalkCmd is
///     not reused because a LocString is a table plus a key with no raw-text
///     constructor (the note <c>KleeMod.InjectLocStrings</c> carries), and
///     this line is BUILT PER PLAN out of a card title and a number that
///     landed -- a loc row could only hold the template, and the template is
///     one format string. The node is the game's, so the bubble looks like
///     every other creature's.
///   * the damage number is <c>CreatureCmd.Damage</c>'s own
///     <c>NDamageNumVfx</c>, which every hit through <c>ElementalHit</c>
///     already spawns. Nothing here draws one. What was missing was never the
///     number; it was the gap in front of it.
///
/// HEADLESS-SAFE BY THE ENGINE'S OWN GUARDS, not by ours.
/// <c>NSpeechBubbleVfx.Create</c> returns null under <c>TestMode.IsOn</c> and
/// <c>Creature.GetVfxContainer</c> returns null there too, so
/// <see cref="Say"/> is a no-op in KleeTests; <c>TriggerAnim</c> returns early
/// when the creature has no node. The mod adds no test seam of its own.
///
/// ONE GRAMMAR FOR BOTH ROWS. <see cref="Line"/> is the ruled format --
/// "Bake-Kurage: Ambush, 12" -- and the casket's announcement takes the same
/// shape with the relic's name in the card's place. It is also the exact
/// string that rides the wire to the blind page (`KokomiPlan.Snapshot`), so
/// what a seat reads and what a player sees are one string built once.
///
/// QUARANTINED. `Vfx/Prototype/**` is Compile Remove'd without
/// `-p:PrototypeCards=true`. Revert is the flag.
/// </summary>
internal static class KurageBeat
{
    /// <summary>The pet's name, spelled once for every surface that says it.
    /// `text-conventions.md`: always "Bake-Kurage", never "the jellyfish".</summary>
    internal const string PetName = "Bake-Kurage";

    /// <summary>
    /// How long the lunge holds before the hit lands.
    ///
    /// THE NUMBER IS THE POINT OF THE ROW, so it is named rather than inlined:
    /// a strike with no gap in front of it is the defect `EB-316` reports.
    /// <c>TriggerAnim</c> halves it for fast mode on its own
    /// (<c>Cmd.CustomScaledWait(min(w/2, 0.25), w)</c>), so this is the
    /// standard-speed figure and fast mode still gets a visible beat.
    /// </summary>
    private const float ActSeconds = 0.35f;

    /// <summary>How long the line stays up. Short enough that four Plans in a
    /// morning do not stack their bubbles, long enough to read six words.</summary>
    private const double LineSeconds = 1.4;

    /// <summary>
    /// The jellyfish acts: the attack state of its own scene, then the beat.
    ///
    /// AWAITED, and that is the whole mechanism -- the caller's next line is
    /// the hit, so awaiting this is what puts the damage number on its own
    /// frame instead of inside the card's.
    /// </summary>
    public static async Task Act(Creature? pet)
    {
        if (pet == null || pet.IsDead) return;
        await CreatureCmd.TriggerAnim(pet, "Attack", ActSeconds);
    }

    /// <summary>
    /// The line, over the speaker's head. Silent for a dead or absent speaker,
    /// and silent headless.
    /// </summary>
    public static void Say(Creature? speaker, string text)
    {
        if (speaker == null || speaker.IsDead || string.IsNullOrEmpty(text))
        {
            return;
        }
        // Cyan for a Hydro jellyfish, off the game's own `VfxColor` palette
        // -- the bubble's art, shape and animation are all the base game's.
        var bubble = NSpeechBubbleVfx.Create(
            text, speaker, LineSeconds, VfxColor.Cyan);
        if (bubble == null) return;
        speaker.GetVfxContainer()?.AddChildSafely(bubble);
    }

    /// <summary>
    /// The ruled format, built in ONE place: "Bake-Kurage: Ambush, 12", or
    /// "Bake-Kurage: Stolen Chapter" when the clause produced no number.
    ///
    /// THE BLIND PAGE PRINTS THIS SAME STRING. It rides `kokomi_plans` as
    /// `carried_out[].line` and `understudy/blindplay.render` prints it
    /// verbatim, so a seat's page and a player's screen cannot come to
    /// disagree about the words -- which is the whole reason the format is not
    /// re-spelled in Python.
    /// </summary>
    public static string Line(string what, int? number) =>
        number is { } n ? $"{PetName}: {what}, {n}" : $"{PetName}: {what}";
}
