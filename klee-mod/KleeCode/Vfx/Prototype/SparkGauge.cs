using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;

namespace KleeMod.Vfx;

/// <summary>
/// THE SPARK BANK AS A RESOURCE DISPLAY, under the Klee overhaul arm only
/// (<c>EB-281</c>).
///
/// THE DEFECT. Under <c>KleeOverhaul.Enabled</c> Sparks are Klee's ONE meter --
/// every explosion mints one (<c>KleeOverhaulLaw.SparkPerExplosion</c>) and the
/// slice's sinks are priced in them -- and the bank rendered as a status-strip
/// Power, a badge among the buffs and debuffs. [USER] asked for the shape the
/// base game already uses for a character resource: the Regent's star counter,
/// which is a glyph and a number in a place of its own and is never mixed in
/// with the statuses. A resource a whole kit is priced against should not have
/// to be told apart from Vulnerable.
///
/// TWO HALVES, AND THE BANK ITSELF DOES NOT MOVE.
///
///   1. <b>The gauge.</b> A <c>GaugeBridge</c> spec (<c>klee_spark</c>) at the
///      overhead slot, carrying Klee's own <c>klee/powers/spark.png</c> glyph
///      as its cap icon. BAR-LESS, like Kokomi's Charge and for the same
///      reason: Sparks have no ceiling, so there is no honest span to draw and
///      a bar would invent one. It renders as a glyph and a climbing number,
///      which is the Regent's star counter's own shape.
///   2. <b>The badge.</b> <see cref="HidesBadge"/> plus the Harmony prefix at
///      the bottom of this file keep <c>SparkPower</c> out of the status strip
///      while the arm is live.
///
/// WHY THE BADGE IS SUPPRESSED AT THE CONTAINER AND NOT AT THE MODEL. The game
/// has a designed way to hide a power: <c>PowerModel.IsVisibleInternal</c>
/// (<c>AmbergrisPower</c> is the base game's own user of it), and
/// <c>NPowerContainer.Add</c> gates the badge on exactly that. It cannot be used
/// here, and the reason is the WIRE: the understudy bridge's
/// <c>BuildPowersState</c> opens with <c>if (!power.IsVisible) continue;</c>, so
/// an invisible power is not merely un-badged, it is off the observed board
/// altogether. The blind page finds the bank by the printed name "Spark" in
/// that list (<c>understudy/qa_packet.spark_note</c>) and
/// <c>understudy/adapter.STATUS_FIELDS</c> maps the same row onto
/// <c>Player.sparks</c>. Hiding the model would have silently blinded both, and
/// repairing them would have meant a SECOND deployable (the bridge is its own
/// mod) moving in lockstep with this one.
///
/// So the model stays visible and exactly one CONSUMER is told to skip it. The
/// wire keeps carrying the bank under the name "Spark" with its rule text, the
/// blind page's output is unchanged byte for byte, and no bridge rebuild is
/// owed. What the prefix costs is that the badge's hover tip goes with the
/// badge: the sentence <c>SparkPower.Localization</c> prints ("A resource.
/// Cards that print a Spark price spend it.") has no on-screen home under the
/// arm. The price itself is still on every card that charges one -- the meter
/// cost badge (<see cref="MeterCostBadge"/>) paints it beside the energy orb in
/// the same Spark glyph -- and a refusal still says "you have no Spark, and
/// this costs N" (<c>KleeUnplayableReason</c>).
///
/// EVERYTHING ELSE IS UNTOUCHED, deliberately. <c>SparkPower</c> is still the
/// bank: the alt-cost gate, the payment, the cost badge, the refusal sentence
/// and the <c>spark</c> meter ledger all read and move the same power they read
/// and moved before. This file adds a DISPLAY and takes one away; it is not a
/// re-homing of the resource.
///
/// PUBLIC rather than internal, for the reason <c>ProtoBombPower.Charges</c>
/// gives: KleeTests is a separate assembly, the four decisions below are the
/// whole of the change, and the alternative was an <c>InternalsVisibleTo</c>
/// nothing else in this mod needs or an IL-shape assertion standing in for the
/// decisions themselves.
/// </summary>
public static class SparkGauge
{
    /// <summary>
    /// Klee's own Spark counter icon -- the one the status-strip badge wore
    /// (<c>KleePowerIcons</c>) and the one the meter cost badge already paints
    /// on a priced card. The glyph is the same everywhere the resource is,
    /// which is the whole argument for a dedicated display.
    /// </summary>
    public const string GlyphPath = "klee/powers/spark.png";

    /// <summary>
    /// Does this creature get the Spark gauge? Klee, and only while the arm is
    /// live. OFF THE ARM THIS IS FALSE AND NOTHING ELSE IN THE FILE RUNS: the
    /// gauge is not built, the badge is not suppressed, and the shipped display
    /// is what it was.
    ///
    /// The arm is the same runtime read <c>Klee.StartingDeck</c> and
    /// <c>KleeCardPool.FilterThroughEpochs</c> take, for the reason
    /// <c>KleeOverhaul</c> records: a dev build compiles this arm beside the
    /// Sparks arm, so the switch cannot be a bare <c>#if</c>.
    ///
    /// THE IDENTITY HALF IS <c>IKleeCharacter</c> rather than <c>is Klee</c>:
    /// the shape <c>tools/lint_prototype_patch_scope.py</c> requires of every
    /// patch under the quarantine, and the shape Furina's and Kokomi's own gates
    /// already take. The reason is co-op -- everything compiled under the one
    /// prototype switch is fanned to every seat at the table, and a change that
    /// cannot name whose creature it is about is the shape of `EB-194` and
    /// `EB-221`. This method is the WHOLE scope of the change: the gauge and the
    /// badge suppression both come through it.
    /// </summary>
    public static bool AppliesTo(Creature creature) =>
        KleeOverhaul.Enabled && creature.Player?.Character is IKleeCharacter;

    /// <summary>
    /// The number the gauge draws: the bank, right now.
    ///
    /// <see cref="SparkPower.SparksAtPlay"/> rather than
    /// <see cref="SparkPower.SparksAsResolved"/> because it is the PLAIN read
    /// and a display wants the plain read. The two can only disagree while the
    /// base free-Attack rule has a pending threshold spend, and that rule is
    /// retired wherever this file compiles at all
    /// (<c>SparkPower.BaseRuleActive</c> is <c>false</c> under
    /// <c>PROTOTYPE_CARDS</c>, which is the switch that compiles
    /// <c>Vfx/Prototype/**</c>). The alt-cost power keeps its own pending
    /// decision and pays through <c>SparkPower.Spend</c>, so it never arms the
    /// accessor's subtraction either.
    /// </summary>
    public static int Read(Creature creature) =>
        SparkPower.SparksAtPlay(creature);

    /// <summary>
    /// Redraw Klee's gauges. Called from <c>SparkPower</c>'s mutation funnels
    /// -- the same chokepoints the <c>spark</c> meter ledger rides -- so the
    /// number on screen and the number in the ledger can never come from
    /// different reads.
    ///
    /// Arm-gated HERE rather than at each call site: with the arm off there is
    /// no Spark gauge to redraw, and a release build must not gain a gauge
    /// refresh on a code path that never had one.
    /// </summary>
    public static void Refresh(Creature? creature)
    {
        if (creature == null || !AppliesTo(creature))
        {
            return;
        }

        GaugeBridge.Refresh(creature);
    }

    /// <summary>
    /// Is this the power whose badge the arm suppresses? Exactly
    /// <c>SparkPower</c>, exactly while the arm is live, and asked of the
    /// power's own owner rather than of the local seat -- in co-op a Klee
    /// under the arm hides her bank badge on either screen, because the gauge
    /// that replaces it is drawn on her creature and is visible to both.
    ///
    /// Nothing else Klee carries is touched. Bombs, the reaction badges and
    /// True Spark Knight keep their status-strip badges: they are STATUSES, and
    /// the finding was about a RESOURCE sitting among them.
    /// </summary>
    public static bool HidesBadge(PowerModel power)
    {
        if (power is not SparkPower)
        {
            return false;
        }

        Creature? owner = OwnerOf(power);
        return owner != null && AppliesTo(owner);
    }

    /// <summary>
    /// The power's creature, or null when it has none to read.
    /// <c>PowerModel.Owner</c>'s getter calls <c>AssertMutable</c> and THROWS
    /// on a canonical model -- <c>EB-94</c>'s root cause, and this is asked
    /// inside a Harmony prefix where a throw would take the badge container
    /// with it.
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
/// The badge half: <c>NPowerContainer.Add</c> is the ONE place a power becomes a
/// status-strip node (<c>NPower.Create</c> is called nowhere else in the game),
/// and it already gates on <c>power.IsVisible</c>. This prefix adds the arm's
/// one exception beside that gate rather than moving the model's own visibility
/// -- see <see cref="SparkGauge"/> for why the model must stay visible.
///
/// A PREFIX THAT SKIPS THE ORIGINAL, not a postfix that removes a node: the
/// container keeps its own <c>_powerNodes</c> list and re-lays it out on every
/// add, so a node that was never created costs nothing and leaves no gap.
///
/// <c>Add</c> is private, which is why the target is named as a string -- the
/// same shape <c>NCard_UpdateStarCostVisuals_KleeMeterBadge_Patch</c> already
/// uses. If the name ever stops resolving, <c>KleePatchBootstrap</c> reports
/// THIS class by name at boot and every other patch stays armed; the visible
/// consequence would be the Spark badge coming back beside the gauge, which is
/// noise rather than a lost run.
/// </summary>
[HarmonyPatch(typeof(NPowerContainer), "Add")]
internal static class NPowerContainer_Add_KleeSparkGauge_Patch
{
    [HarmonyPrefix]
    public static bool Prefix(PowerModel power) => !SparkGauge.HidesBadge(power);
}
