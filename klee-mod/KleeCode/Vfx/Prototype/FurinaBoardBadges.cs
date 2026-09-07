using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;

namespace KleeMod.Vfx;

/// <summary>
/// THE THREE METERS LEAVE THE POWER ROW (`EB-636`).
///
/// THE FIND. [USER] on the `0.2.2917+proto` frame: Encore, Fanfare and the
/// Salon member count should not sit in the power row once the board carries
/// them. The frame shows exactly that -- a status strip under Furina's HP bar
/// holding a "3" and a "13" beside her actual statuses, while
/// <see cref="SalonPanel"/> above her already names three members and prints
/// the Encore, the Fanfare and the member bonus on one line. Two of the three
/// numbers on that frame were printed twice, and the third (Encore) is a
/// resource rather than a status in the first place.
///
/// WHY IT IS THE ROW THAT MOVES AND NOT THE POWER. Because the POWER is how
/// the understudy sees the meter: the bridge serialises a creature's
/// <c>Powers</c> into the wire's <c>status</c> map, which is where a scenario's
/// `expect: power:` reads and where every blind seat's state comes from. Take
/// the model away and a headless run goes blind to the whole Salon. This is
/// <c>SparkPower</c>'s constraint one character over, stated in its own header
/// and solved the same way: the MODEL stays applied and visible, and the one
/// container that turns a model into a status-strip node declines to make one.
///
/// THE PATH IS THE GAME'S OWN CHOKE POINT, and it is the path
/// <see cref="SparkGauge"/> already proved. <c>NPowerContainer.Add</c> is the
/// only place a power becomes a strip node (<c>NPower.Create</c> is called
/// nowhere else in v0.111.0) and it already gates on <c>power.IsVisible</c>;
/// the prefix below adds the arm's exceptions beside that gate rather than
/// moving the model's own visibility, which is the field the wire reads. There
/// is NO hidden-power property on <c>PowerModel</c> to use instead -- the base
/// game's own bookkeeping powers are hidden by never being added to a
/// container, not by a flag -- so a prefix that skips the original is the
/// mod-side equivalent, and it costs nothing: the container rebuilds its
/// <c>_powerNodes</c> layout on every add, so a node never created leaves no
/// gap.
///
/// ONE LEG PER METER, and each is the leg that DRAWS ITS REPLACEMENT. A meter
/// whose replacement is not compiled into this build must keep its badge or
/// the number leaves the screen altogether:
///
///   * <c>SalonMemberPower</c> and <c>EncoreMeterPower</c> hide under the
///     MANUAL leg, which is <see cref="SalonPanel.AppliesTo"/>'s own gate --
///     the panel's chips ARE the company, named and drawn per member, and its
///     resource line leads with the Encore.
///   * <c>FanfareMeterPower</c> hides under the METER leg, the leg that makes
///     a performance the only thing that mints: the panel's resource line
///     prints the Fanfare and the member bonus it is buying, with the next
///     threshold on its hover.
///
/// NOTHING ELSE FURINA CARRIES IS TOUCHED. Her auras, her Spotlight power and
/// every status she can be given keep their badges: they are STATUSES, and the
/// finding is about RESOURCES sitting among them. Same line
/// <see cref="SparkGauge.HidesBadge"/> draws.
///
/// WHAT NOTHING HEADLESS CAN ANSWER: whether the row reads better without
/// them. Godot nodes cannot be built in the test host (KleeTests README), so
/// the pins are the DECISION -- which powers, under which leg, and that the
/// models stay applied and visible. The look is owed a frame on the next
/// `+proto` deploy.
///
/// QUARANTINED. `Vfx/Prototype/**` is `Compile Remove`d without
/// `-p:PrototypeCards=true`. Revert is the flag.
/// </summary>
public static class FurinaBoardBadges
{
    /// <summary>
    /// Is this the badge of a meter the arm's own board already draws?
    ///
    /// THE CHARACTER SCOPE IS STATED HERE (`EB-225`), in the patch's own file,
    /// rather than left inside the <c>*LiveFor</c> readers: this prefix runs on
    /// every power added on every seat at the table, including a co-op Klee's,
    /// and a prototype patch that cannot say whose creature it is about is the
    /// shape that took two blind sessions down.
    ///
    /// And it is asked of the POWER'S OWN OWNER rather than of the local seat,
    /// for <see cref="SparkGauge.HidesBadge"/>'s reason: the replacement is
    /// Furina's own panel, drawn on her creature, and a co-op partner watching
    /// it should not also see the row it replaced.
    /// </summary>
    public static bool HidesBadge(PowerModel power)
    {
        Creature? owner = OwnerOf(power);
        if (owner == null || !FurinaResources.IsFurina(owner))
        {
            return false;
        }

        return power switch
        {
            // The panel's chips are the company, named and per member.
            SalonMemberPower => FurinaReframe.ManualLiveFor(owner),
            // The panel's resource line leads with the Encore.
            EncoreMeterPower => FurinaReframe.ManualLiveFor(owner),
            // And carries the Fanfare and the bonus it is buying.
            FanfareMeterPower => FurinaReframe.MeterLiveFor(owner),
            _ => false,
        };
    }

    /// <summary>
    /// The power's creature, or null when it has none to read.
    /// <c>PowerModel.Owner</c>'s getter calls <c>AssertMutable</c> and THROWS
    /// on a canonical model -- <c>EB-94</c>'s root cause -- and this is asked
    /// inside a Harmony prefix where a throw would take the badge container
    /// with it. <see cref="SparkGauge"/>'s own guard, verbatim.
    /// </summary>
    private static Creature? OwnerOf(PowerModel power)
    {
        try
        {
            return power.IsMutable ? power.Owner : null;
        }
        catch (System.Exception)
        {
            return null;
        }
    }
}

/// <summary>
/// The row half: a prefix beside <c>NPowerContainer.Add</c>'s own
/// <c>IsVisible</c> gate, skipping the original for the three meters the arm's
/// board already draws. See <see cref="FurinaBoardBadges"/> for why the models
/// must stay applied and visible -- they are what the understudy wire reads.
///
/// A SECOND PREFIX ON THIS METHOD, beside
/// <c>NPowerContainer_Add_KleeSparkGauge_Patch</c>, and deliberately not folded
/// into it: the two arms are two characters, two flags and two reverts, and one
/// predicate that answered for both would make either arm's retirement the
/// other's to argue with. Harmony runs both; either returning false skips the
/// original, which is the semantics both want.
///
/// <c>Add</c> is private, which is why the target is named as a string -- the
/// same shape the Spark patch uses. If the name ever stops resolving,
/// <c>KleePatchBootstrap</c> reports THIS class by name at boot and every other
/// patch stays armed; the visible consequence is the three badges coming back
/// beside the board that replaced them, which is noise rather than a lost run.
/// </summary>
[HarmonyPatch(typeof(NPowerContainer), "Add")]
internal static class NPowerContainer_Add_FurinaBoardBadges_Patch
{
    [HarmonyPrefix]
    public static bool Prefix(PowerModel power) =>
        !FurinaBoardBadges.HidesBadge(power);
}
