using System;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
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
    private static readonly MegaCrit.Sts2.Core.Models.ModelId GuestCastId =
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
