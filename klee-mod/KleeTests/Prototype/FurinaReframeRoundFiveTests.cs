using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE FURINA REFRAME, ROUND FIVE -- the blind act-1 seat's run, pinned
/// (`review/qa/furina-reframe-round-5-2026-09-04/opus-act1.md`).
///
/// Two rows, and both are SENTENCES rather than rules: the arm changed what
/// happens and left a shipped clause standing that says otherwise.
///
///   * `EB-421`. Guest Cast prints "no Fanfare". The seat watched the meter go
///     3 to 5 on the beat the clause forbade, because the arm mints by
///     PERFORMANCE and a Companion play is what makes the front member
///     perform. The arm's face drops the clause and adds nothing.
///   * `EB-420`. Duet's extra play does not make the Salon perform a second
///     time, and that is DELIBERATE -- LAW:145's per-Companion-play bound,
///     which `KleeCompanionSpark` states in as many words ("a per-play bound a
///     replay can double is not a bound"). The seat could not see it: two
///     Crabaletta performs where it counted three due, and no line on any
///     screen naming Duet at all. So the arm's face says it and the ledger
///     names the play that did not perform.
/// </summary>
public class FurinaReframeRoundFiveTests
{
    // ==================================================================
    // Fixtures. The Arm flag-holder is lifted from
    // FurinaReframeRoundTwoTests, whose reasoning is written out there.
    // ==================================================================

    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;
        private readonly bool _meter = FurinaReframe.MeterEnabled;

        internal Arm(bool manual = false, bool meter = false,
                     bool master = true)
        {
            FurinaReframe.Enabled = master;
            FurinaReframe.ManualEnabled = manual;
            FurinaReframe.MeterEnabled = meter;
        }

        public void Dispose()
        {
            FurinaReframe.Enabled = _enabled;
            FurinaReframe.ManualEnabled = _manual;
            FurinaReframe.MeterEnabled = _meter;
        }
    }

    /// <summary>Stand-in for the badge's registered id: BaseLib assigns the
    /// real one at registration, and `SmartDescriptionLocKey` is `Id.Entry`
    /// plus a suffix. Same seeding as `FurinaReframeRoundTwoTests.Stage`.
    /// </summary>
    private static readonly ModelId GuestCastId =
        new("POWER", "KLEE_GUEST_CAST_TEST");

    private static GuestCastPower Badge(Seat seat)
    {
        var badge = (GuestCastPower)RuntimeHelpers
            .GetUninitializedObject(typeof(GuestCastPower));
        Seat.Force(badge, "Id", GuestCastId);
        Seat.Force(badge, "IsMutable", true);
        Seat.Force(badge, "Owner", seat.Creature);
        return badge;
    }

    private static string BadgeKey(GuestCastPower badge) =>
        (string)typeof(GuestCastPower)
            .GetProperty("SmartDescriptionLocKey", HeadlessGame.All)!
            .GetValue(badge)!;

    /// <summary>The sentence this badge would print, resolved the way the
    /// game resolves it: the row whose key `SmartDescriptionLocKey` names, and
    /// `description` when it names the base key -- a power with no
    /// `smartDescription` row of its own falls back to its description, which
    /// is what the shipped Guest Cast has always done.</summary>
    private static string FaceFor(GuestCastPower badge)
    {
        var key = BadgeKey(badge);
        var rows = badge.Localization!;
        return rows.FirstOrDefault(r => r.Item1 != "description"
                                        && key.EndsWith(r.Item1)).Item2
               ?? rows.First(r => r.Item1 == "description").Item2;
    }

    // ==================================================================
    // 1. `EB-421` -- Guest Cast does not forbid Fanfare under the arm
    // ==================================================================

    [Fact]
    public void The_arms_guest_cast_face_does_not_forbid_fanfare()
    {
        using var _ = new Arm(meter: true);
        var badge = Badge(Seat.Furina());

        Assert.EndsWith(".smartDescriptionReframe", BadgeKey(badge));
        Assert.DoesNotContain("Fanfare", FaceFor(badge));
    }

    [Fact]
    public void The_arms_guest_cast_face_is_the_shipped_one_minus_the_clause()
    {
        // Nothing was ADDED: the mode buff still says what it multiplies and
        // when it ends, and the rate the meter mints at belongs to the meter's
        // own badge (`EB-385`), not to a second surface here.
        using var _ = new Arm(meter: true);
        var badge = Badge(Seat.Furina());

        var face = FaceFor(badge);
        Assert.Contains("50% stronger printed damage", face);
        Assert.Contains("Lasts until the [gold]Spotlight[/gold] moves", face);
    }

    [Fact]
    public void The_shipped_guest_cast_face_is_untouched_with_the_leg_off()
    {
        // "no Fanfare" is TRUE of the shipped kit -- the Spotlight's Fanfare is
        // Center Stage's, her own cards only -- so the release sentence stands.
        using var _ = new Arm(master: false);
        var badge = Badge(Seat.Furina());

        Assert.EndsWith(".smartDescription", BadgeKey(badge));
        Assert.Contains("no Fanfare", FaceFor(badge));
    }

    // ==================================================================
    // 2. `EB-420` -- Duet's extra play, printed and logged
    // ==================================================================

    private static readonly ModelId ReplayId =
        new("POWER", "KLEE_REPLAY_NEXT_TEST");

    private static ReplayNextCompanionPower Replay(Seat seat)
    {
        var badge = (ReplayNextCompanionPower)RuntimeHelpers
            .GetUninitializedObject(typeof(ReplayNextCompanionPower));
        Seat.Force(badge, "Id", ReplayId);
        Seat.Force(badge, "IsMutable", true);
        Seat.Force(badge, "Owner", seat.Creature);
        return badge;
    }

    private static string ReplayKey(ReplayNextCompanionPower badge) =>
        (string)typeof(ReplayNextCompanionPower)
            .GetProperty("SmartDescriptionLocKey", HeadlessGame.All)!
            .GetValue(badge)!;

    private static string ReplayFace(ReplayNextCompanionPower badge)
    {
        var key = ReplayKey(badge);
        var rows = badge.Localization!;
        return rows.FirstOrDefault(r => r.Item1 != "description"
                                        && key.EndsWith(r.Item1)).Item2
               ?? rows.First(r => r.Item1 == "description").Item2;
    }

    /// <summary>A Companion card, uninitialised with a forced id -- the same
    /// shape `FurinaReframeRuleTests.Companion` uses, plus the id, because the
    /// ledger records the printed title and falls back to the entry.</summary>
    private static CardModel Companion()
    {
        var card = (CardModel)
            RuntimeHelpers.GetUninitializedObject(
                typeof(global::KleeMod.Cards.Generated.BarbaraMelody));
        Seat.Force(card, "Id",
            new ModelId("CARD", "BARBARA_TEST"));
        return card;
    }

    private static CardModel NotACompanion()
    {
        var card = (CardModel)
            RuntimeHelpers.GetUninitializedObject(
                typeof(global::KleeMod.Cards.Furina.EtherealSpotlight));
        Seat.Force(card, "Id",
            new ModelId("CARD", "SPOTLIGHT_TEST"));
        return card;
    }

    [Fact]
    public void The_arms_replay_face_says_the_salon_still_performs_once()
    {
        // The rule was already this and was printed nowhere: the trigger is
        // gated on `IsFirstInSeries` (LAW:145's per-Companion-play bound), and
        // the seat "ended the turn unable to say whether Duet had fired".
        using var _ = new Arm(manual: true);
        var badge = Replay(Seat.Furina());

        Assert.EndsWith(".smartDescriptionReframe", ReplayKey(badge));
        Assert.Contains("performs on the first play only", ReplayFace(badge));
    }

    [Fact]
    public void The_shipped_replay_face_is_untouched_off_the_arm()
    {
        // Off the arm nothing performs off a Companion play at all, so the
        // clause would name a trigger that does not exist. Klee holds this
        // same power (Study Buddy) and reads the shipped sentence for the same
        // reason -- `ManualLiveFor` is Furina's.
        using var _ = new Arm(master: false);
        var badge = Replay(Seat.Furina());

        Assert.EndsWith(".smartDescription", ReplayKey(badge));
        Assert.DoesNotContain("first play only", ReplayFace(badge));
    }

    [Fact]
    public void Klee_holding_study_buddy_reads_the_shipped_face_under_the_arm()
    {
        using var _ = new Arm(manual: true);
        var badge = Replay(Seat.Klee());

        Assert.EndsWith(".smartDescription", ReplayKey(badge));
    }

    [Fact]
    public void A_companion_replay_is_recorded_under_the_arm()
    {
        // The log half. `NoteCompanionReplay` is what the seam calls on the
        // side of the gate that does NOT trigger, so the page can name the
        // play that performed nobody.
        using var _ = new Arm(manual: true);
        FurinaReframeLedger.ResetAll();
        var seat = Seat.Furina();

        SalonMemberPower.NoteCompanionReplay(seat.Creature, Companion());

        Assert.Single(FurinaReframeLedger.For(seat.Creature)
                          .ReplaysWithoutTrigger);
    }

    [Fact]
    public void A_replay_of_a_non_companion_is_not_recorded()
    {
        // The trigger is the Companion half of the kit; her own cards Evoke.
        using var _ = new Arm(manual: true);
        FurinaReframeLedger.ResetAll();
        var seat = Seat.Furina();

        SalonMemberPower.NoteCompanionReplay(seat.Creature, NotACompanion());

        Assert.Empty(FurinaReframeLedger.For(seat.Creature)
                         .ReplaysWithoutTrigger);
    }

    [Fact]
    public void Nothing_is_recorded_with_the_manual_leg_off()
    {
        using var _ = new Arm(master: false);
        FurinaReframeLedger.ResetAll();
        var seat = Seat.Furina();

        SalonMemberPower.NoteCompanionReplay(seat.Creature, Companion());

        Assert.Empty(FurinaReframeLedger.For(seat.Creature)
                         .ReplaysWithoutTrigger);
    }

    [Fact]
    public void The_turn_boundary_clears_the_replays_with_the_performances()
    {
        // One list's question, so one boundary: "what happened on the turn I
        // am looking at".
        using var _ = new Arm(manual: true);
        FurinaReframeLedger.ResetAll();
        var seat = Seat.Furina();
        var ledger = FurinaReframeLedger.For(seat.Creature);

        SalonMemberPower.NoteCompanionReplay(seat.Creature, Companion());
        ledger.ClearPerformances();

        Assert.Empty(ledger.ReplaysWithoutTrigger);
    }

    [Fact]
    public void The_wire_carries_the_replays_beside_the_performances()
    {
        // Beside and never inside: a replay that performed nobody is not a
        // performance, and the reader has to be able to tell the two apart.
        using var _ = new Arm(manual: true);
        FurinaReframeLedger.ResetAll();
        var seat = Seat.Furina();

        SalonMemberPower.NoteCompanionReplay(seat.Creature, Companion());
        var snapshot = FurinaReframeLedger.Snapshot(seat.Player);

        Assert.True(snapshot.ContainsKey("performed"));
        var replayed = Assert.IsType<List<object?>>(
            snapshot["replayed"]);
        Assert.Single(replayed);
    }

    [Fact]
    public void A_canonical_guest_cast_badge_answers_without_throwing()
    {
        // `HasSmartDescription` probes the key on the compendium's own copy,
        // whose `Owner` getter asserts mutability (`EB-94`). It has no owner,
        // so the shipped key is the honest answer.
        using var _ = new Arm(meter: true);
        var canonical = (GuestCastPower)RuntimeHelpers
            .GetUninitializedObject(typeof(GuestCastPower));
        Seat.Force(canonical, "Id", GuestCastId);

        Assert.EndsWith(".smartDescription", BadgeKey(canonical));
    }
}
