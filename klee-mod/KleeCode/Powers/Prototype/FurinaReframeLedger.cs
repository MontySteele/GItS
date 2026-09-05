using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;

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

    /// <summary>`EB-493`. Aimed PERFORMANCES whose named member was not on the
    /// stage, mirroring the sim's <c>salon_perform_target_absent</c>. Kept
    /// apart from the Evoke's count above for that count's own reason: the two
    /// verbs miss for different reasons and a display that wants to say which
    /// one happened must be able to tell them apart. The performance still
    /// happens, on the front.</summary>
    public int PerformTargetAbsences { get; private set; }

    /// <summary>Who the last missed PERFORMANCE aim named.</summary>
    public SalonMember? LastAbsentPerformAim { get; private set; }

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

    public void NotePerformTargetAbsent(SalonMember named)
    {
        PerformTargetAbsences++;
        LastAbsentPerformAim = named;
    }

    public void NoteDrain(int drained)
    {
        Drains++;
        LastDrained = drained;
        TotalDrained += drained;
    }

    public void NoteDesignationUnpaid() => DesignationsUnpaid++;

    public void NoteDesignationRedundant() => DesignationsRedundant++;

    // ---- `EB-405`: WHO PERFORMED, ON WHOM, AND WHAT IT LEFT -----------
    //
    // WHAT THE SEAT SAW (Furina round 4, run 1, (c) 4). A member's line on
    // the page named no target: "Crabaletta chose its own enemy and left a
    // Hydro aura on a body the seat had not picked", in a kit whose readable
    // decision is which element lands on which aura. There was nothing for
    // the page to print -- no Salon block reached the wire at all, and the
    // only Salon row a seat ever saw was the counter power's static rulebook
    // sentence, which by construction can never name a body.
    //
    // THE TARGET IS PICKED HERE AND NOWHERE ELSE. `PerformMember` and `Bow`
    // draw it from `Rng.CombatTargets` over `HittableEnemies` and then throw
    // the reference away: `ElementalHit.Deal` returns the damage and not the
    // creature, so the fact left no trace in any state a poll could read.
    //
    // A LIST AND NOT A COUNTER, which is the one exception to this class's
    // "NO TURN ROLL" note above and is why it is stated here: every field
    // above answers "how many times this combat", and this answers "what
    // happened on the turn I am looking at", which is a different question
    // with a different boundary. It is cleared at the start of each player
    // turn, in `SalonMemberPower.AfterPlayerTurnStart`, which is the one
    // place that boundary exists. Still not a source of truth: nothing
    // branches on it and no rule reads it back.
    //
    // THE SHAPE IS `KokomiPlan.CarriedOutPlan`'s, deliberately -- the page
    // already knows how to name a body from a `combat_id` and fall back to
    // the title for one that died (`blindplay_board.name_moved_rows`), so a
    // second shape would be a second naming rule.

    /// <summary>One member's act: who, on whom, with what, and what the body
    /// is wearing afterwards.</summary>
    public readonly record struct Performed(
        string Member, string? Target, string? CombatId, string? Element,
        string? Aura, int Amount, bool Paid, bool Evoked);

    private readonly List<Performed> _performances = new();

    /// <summary>This turn's performances, in the order they happened.</summary>
    public IReadOnlyList<Performed> Performances => _performances;

    public void NotePerformance(Performed performed) =>
        _performances.Add(performed);

    // ---- `EB-420`: THE REPLAY WITH NOTHING NAMING IT ------------------
    //
    // The same kind of fact as the whiff above, found the same way. Duet plays
    // the next Companion card an extra time and nothing on any screen said so:
    // "I ended the turn unable to say whether Duet had fired at all" is what a
    // rule with no surface reads like. So the replay is recorded under its own
    // name, beside the performances, and the page prints it in that block.
    //
    // `EB-464` CHANGED WHAT IT MEANS AND NOT WHETHER IT IS KEPT. The extra
    // play used to perform nobody, because `AfterCardPlayed` gated the
    // Companion trigger on `IsFirstInSeries`; the r8 ruling took that gate off
    // (see `FurinaResources.AfterCardPlayed`), so the extra play now performs
    // like any other. What the seat could not see is unchanged -- a
    // performance list cannot say which of its acts came from a replay -- so
    // the record stays and the sentence it feeds says the extra play
    // performed. Mirrors the sim's `salon_replay`, emitted from
    // `combat._finish_play` inside the same loop.
    //
    // BY PRINTED TITLE, because that is what the reader is looking at, and per
    // TURN, cleared with the performances: it answers "what happened on the
    // turn I am looking at", which is the performance list's own question.

    private readonly List<string> _replays = new();

    /// <summary>This turn's Companion replays, in the order they happened, by
    /// printed title.</summary>
    public IReadOnlyList<string> Replays => _replays;

    public void NoteReplay(string card) => _replays.Add(card);

    /// <summary>The turn boundary, and the only one this class has.</summary>
    public void ClearPerformances()
    {
        _performances.Clear();
        _replays.Clear();
    }

    /// <summary>
    /// `EB-405`. THE WIRE'S VIEW of this turn's performances.
    ///
    /// A PLAIN DICTIONARY OF PRIMITIVES, and the shape is
    /// <c>KokomiPlan.Snapshot</c>'s for the reason that one is: the bridge
    /// (<c>vendor/STS2_MCP/gits/GitsFurinaSalon.cs</c>) reaches it by
    /// REFLECTION, because this whole file is Compile Remove'd from a release
    /// build and a compile-time reference would make the bridge refuse to load
    /// without it. The field names here ARE the contract, and
    /// <c>understudy/blindplay_board.furina_salon</c> reads them.
    ///
    /// THREE STATES, NOT TWO, the same split every other GItS block on this
    /// wire makes: an ABSENT key is "no reframe in this build", an EMPTY map
    /// is "the rule is here and this seat is not playing it", and a populated
    /// map is her stage. So this returns an empty map rather than null for a
    /// Klee, and the reader is entitled to tell those apart.
    /// </summary>
    public static Dictionary<string, object?> Snapshot(Player? player)
    {
        var snapshot = new Dictionary<string, object?>();
        var creature = player?.Creature;
        if (creature == null || !FurinaReframe.ManualLiveFor(creature))
        {
            return snapshot;
        }
        snapshot["performed"] = For(creature).Performances
            .Select(row => (object?)new Dictionary<string, object?>
            {
                ["member"] = row.Member,
                ["target"] = row.Target,
                ["combat_id"] = row.CombatId,
                ["element"] = row.Element,
                ["aura"] = row.Aura,
                ["amount"] = row.Amount,
                ["paid"] = row.Paid,
                ["evoked"] = row.Evoked,
            })
            .ToList();
        // `EB-420`. BESIDE the performances and never inside them: the
        // replay's own act is already one of the rows above (`EB-464`), and
        // this list is the only thing that says a second PLAY happened at all.
        snapshot["replayed"] = For(creature).Replays
            .Select(card => (object?)card)
            .ToList();
        // `EB-496`'s sibling, `EB-506`: WHO IS AT THE FRONT, and in what order
        // the rest will follow.
        //
        // "I could never tell who the front member was. The stage buff always
        // names one -- *A Companion card you play performs the Usher* -- but
        // the Companion glossary says a play *performs the front member, then
        // sends it to the back*, and after doing exactly that in fight 3 the
        // line still named the Usher. With two members up I was guessing which
        // one my next Companion card would fire" (Furina r11 lane 1, (c) 4).
        //
        // THE BUFF'S FACE IS NOT A LIVE READ AND CANNOT BE. It is a smart
        // description keyed on the front member (<c>ManualKey</c>), so it is
        // one of four registered rows and it refreshes when the game decides
        // to redraw it -- which after a rotation it had not. The COMPANY is a
        // live list, in slot order, front first: <c>PerformLeftmost</c> takes
        // <c>company[0]</c> and <c>RotateLeftmost</c> moves it to the back, so
        // the head of this list is the answer to the seat's question by
        // construction rather than by a second copy of the rule.
        //
        // THE STAGE NAMES, not the card titles, because those are the words
        // every Salon face and the buff itself already print
        // (<c>SalonMemberPower.ManualFrontName</c>).
        snapshot["company"] = SalonMemberPower.CompanyOf(creature)
            .Select(member => (object?)SalonMemberPower.ManualFrontName(member))
            .ToList();
        return snapshot;
    }
}
