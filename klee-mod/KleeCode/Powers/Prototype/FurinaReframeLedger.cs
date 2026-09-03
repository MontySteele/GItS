using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Powers;

/// <summary>
/// THE ARM'S MEMORY: the six things the sim SAYS OUT LOUD and the C# had no
/// way to say at all.
///
/// WHY IT EXISTS, and it is not telemetry for its own sake. The sim slice
/// answers D4 with events -- <c>salon_upkeep_suppressed</c>,
/// <c>salon_trigger</c>, <c>salon_trigger_whiffed</c>, <c>salon_evoke</c>,
/// <c>salon_evoke_target_absent</c>, <c>spotlight_designate_unpaid</c> and
/// <c>spotlight_designate_redundant</c> -- and each one exists because the
/// fact it carries leaves NO trace in the state afterwards. "Your Companion
/// found an empty stage" and "you played a card into an empty stage" are the
/// same board a moment later; so are "she called for Crabaletta and
/// Crabaletta was not there" and "she called for nobody". The sim's own
/// comments give that reason at every one of the seven sites. C# has no event
/// log, so a port that dropped them would drop the rule's readability, not
/// just its instrumentation -- and it would leave five of the sim's pins with
/// no C# counterpart to mirror.
///
/// WHAT IT IS NOT. It is not a second source of truth: no rule branches on a
/// counter here, and nothing in the arm reads one back. Every field is
/// written once at the site the sim emits its event and read only by a pin or
/// a display.
///
/// PER PLAYER, keyed the way <c>KleeOverhaulLedger</c> and
/// <c>KokomiOverhaulLedger</c> are keyed and for the same reason (R205): in
/// co-op the other seat's stage is not hers, and a shared integer would credit
/// this Furina with the other seat's suppressions.
///
/// NO TURN ROLL, unlike the other two. Every counter here is a COMBAT total --
/// the questions are "did the upkeep stop", "did a trigger whiff", "did an aim
/// miss", not "how many times this turn" -- so there is no boundary to roll on
/// and adding one would invent a per-turn semantics no rule asked for.
///
/// NOT A LEAK: the whole table is dropped when the combat instance changes, so
/// it holds at most the current combat's seats.
///
/// PUBLIC, for the reason <c>Diagnostics.MeterLedger</c> gives: KleeTests is a
/// separate assembly and these counters are what five of the arm's pins read.
/// </summary>
public sealed class FurinaReframeLedger
{
    private static object? _combat;

    private static readonly Dictionary<Creature, FurinaReframeLedger> _byFurina =
        new();

    /// <summary>This Furina's ledger for this combat, created on first ask.
    /// </summary>
    public static FurinaReframeLedger For(Creature furina)
    {
        var combat = (object?)furina.CombatState;
        if (!ReferenceEquals(_combat, combat))
        {
            _combat = combat;
            _byFurina.Clear();
        }
        if (!_byFurina.TryGetValue(furina, out var ledger))
        {
            ledger = new FurinaReframeLedger();
            _byFurina[furina] = ledger;
        }
        return ledger;
    }

    /// <summary>Test seam: forget everything. The mod never calls it.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _byFurina.Clear();
    }

    // ---- MANUAL ------------------------------------------------------

    /// <summary>Turn-starts whose Salon upkeep did not run, mirroring
    /// <c>salon_upkeep_suppressed</c>. LOUD RATHER THAN SILENT because an
    /// instrument that counted upkeeps has to be able to tell "no members"
    /// from "no upkeep exists any more" -- and R177's fuel finding was
    /// measured on the row this replaces. Counted only when the stage is
    /// NON-EMPTY, exactly as the sim emits it.</summary>
    public int UpkeepsSuppressed { get; private set; }

    /// <summary>The company size the last suppression skipped.</summary>
    public int LastUpkeepSuppressedMembers { get; private set; }

    /// <summary>Companion plays that made the front member perform, mirroring
    /// <c>salon_trigger</c>.</summary>
    public int CompanionTriggers { get; private set; }

    /// <summary>Who performed on the last trigger.</summary>
    public SalonMember? LastTriggerMember { get; private set; }

    /// <summary>Companion plays that found an EMPTY stage, mirroring
    /// <c>salon_trigger_whiffed</c> -- which is a different event from the
    /// card verbs' own whiff on purpose: a display must be able to tell "your
    /// Companion found an empty stage" from a card the player CHOSE to play
    /// into one.</summary>
    public int TriggerWhiffs { get; private set; }

    // ---- EVOKE -------------------------------------------------------

    /// <summary>Bows that were Evokes, mirroring <c>salon_evoke</c> -- a
    /// SECOND event in the sim rather than a field on the shipped
    /// <c>salon_final_bow</c>, because that row is read by instruments and by
    /// tests that compare whole rows.</summary>
    public int Evokes { get; private set; }

    /// <summary>Who took the last Evoke.</summary>
    public SalonMember? LastEvokeMember { get; private set; }

    /// <summary>The Focus multiplier the last Evoke applied.</summary>
    public int LastEvokeFocusMult { get; private set; }

    /// <summary>Aimed Evokes whose named member was not on the stage,
    /// mirroring <c>salon_evoke_target_absent</c>. The Evoke still happens, on
    /// the front: an aimed card that cannot find its member is an UNAIMED
    /// Evoke, never a wasted one.</summary>
    public int EvokeTargetAbsences { get; private set; }

    /// <summary>Who the last missed aim named.</summary>
    public SalonMember? LastAbsentAim { get; private set; }

    // ---- THE DRAIN (slice two) ---------------------------------------

    /// <summary>Drains, mirroring the sim's <c>fanfare_drained</c> event, and
    /// it is here for this ledger's stated reason: the fact leaves NO trace in
    /// the state afterwards. A meter at 0 because nothing was earned and a
    /// meter at 0 because twelve were just spent are the same board a moment
    /// later, and the whole question the two drain rows ask is which of those
    /// a turn produced.</summary>
    public int Drains { get; private set; }

    /// <summary>What the last drain took. Zero is a real answer and the
    /// interesting one: a drain of nothing is the wasted play both rows are
    /// deliberately allowed to be (no <c>requires</c> gate, packet 4.6).
    /// </summary>
    public int LastDrained { get; private set; }

    /// <summary>Every point taken this combat, which is the drain arm's own
    /// throughput and the number a grading round reads.</summary>
    public int TotalDrained { get; private set; }

    // ---- SPOTLIGHT ---------------------------------------------------

    /// <summary>Designations that could not be paid for, mirroring
    /// <c>spotlight_designate_unpaid</c>. UNPAID IS A NO-OP, NOT A DISCOUNT --
    /// "free when under-priced" is the failure R228 names as its own biggest
    /// risk.</summary>
    public int DesignationsUnpaid { get; private set; }

    /// <summary>Designations that re-aimed at the target already in force,
    /// mirroring <c>spotlight_designate_redundant</c>: re-aiming buys nothing,
    /// so it cannot be allowed to bill for nothing either.</summary>
    public int DesignationsRedundant { get; private set; }

    // ---- the writers -------------------------------------------------

    public void NoteUpkeepSuppressed(int members)
    {
        UpkeepsSuppressed++;
        LastUpkeepSuppressedMembers = members;
    }

    public void NoteCompanionTrigger(SalonMember member)
    {
        CompanionTriggers++;
        LastTriggerMember = member;
    }

    public void NoteTriggerWhiffed() => TriggerWhiffs++;

    public void NoteEvoke(SalonMember member, int focusMult)
    {
        Evokes++;
        LastEvokeMember = member;
        LastEvokeFocusMult = focusMult;
    }

    public void NoteEvokeTargetAbsent(SalonMember named)
    {
        EvokeTargetAbsences++;
        LastAbsentAim = named;
    }

    public void NoteDrain(int drained)
    {
        Drains++;
        LastDrained = drained;
        TotalDrained += drained;
    }

    public void NoteDesignationUnpaid() => DesignationsUnpaid++;

    public void NoteDesignationRedundant() => DesignationsRedundant++;
}
