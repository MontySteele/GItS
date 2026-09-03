using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE FURINA REFRAME, ROUND TWO -- the blind act-1 seat's run, pinned
/// (`review/qa/furina-reframe-round-2-2026-09-04/opus-act1.md`).
///
/// `EB-382`, and the whole of this file's first section, is a row whose
/// SUSPECT was wrong and whose OBSERVATION was right. The seat watched banked
/// Encore vanish across three turn boundaries and, seeing a Salon member on
/// stage each time, read the correlation as causation: "a member on stage
/// appears to eat all remaining Encore at turn start". The row filed the
/// turn-start hooks accordingly.
///
/// THE TURN START SPENDS NOTHING, which is what section 1 says twice over --
/// behaviourally, on the row's own board at each of the three amounts it
/// reports, and structurally, over every hook that runs in the two turn-start
/// broadcasts. THE SPEND IS THE SHIPPED ABSORPTION (section 2): Encore eats
/// damage that gets past Block, which is what the buffer is for, and the arm's
/// METER leg retires the Fanfare that used to mark it -- so under the arm the
/// buffer empties with no mark on any surface at all.
///
/// The seat's own numbers reconcile against absorption exactly. Fight 1, turn
/// 2 into turn 3: the intent read `2x4` after the Shatter un-froze it, so 8
/// damage arrived, HP went 57 -> 53 and Encore went 4 -> 0. Four absorbed,
/// four to HP, eight in total. The "control case" the seat read as "no member,
/// so nothing ate it" is the turn its own record calls "Took 0 damage".
///
/// The sim's half is `tier0/tests/test_furina_reframe_round2.py`, the same
/// sections in the same order. The legibility half -- the page saying what
/// spends Encore, which is the gap that made an ordinary buffer read as a
/// confiscation -- is `understudy.blindplay_notes.METER_RULES`.
/// </summary>
public class FurinaReframeRoundTwoTests
{
    // ==================================================================
    // Fixtures. Lifted from FurinaReframeRuleTests, whose reasoning for
    // every reflective step is written out there.
    // ==================================================================

    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;
        private readonly bool _evoke = FurinaReframe.EvokeEnabled;
        private readonly bool _meter = FurinaReframe.MeterEnabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;
        private readonly bool _burst = FurinaReframe.BurstEnabled;

        internal Arm(bool manual = false, bool evoke = false, bool meter = false,
                     bool spotlight = false, bool burst = false,
                     bool master = true)
        {
            FurinaReframe.Enabled = master;
            FurinaReframe.ManualEnabled = manual;
            FurinaReframe.EvokeEnabled = evoke;
            FurinaReframe.MeterEnabled = meter;
            FurinaReframe.SpotlightEnabled = spotlight;
            FurinaReframe.BurstEnabled = burst;
        }

        public void Dispose()
        {
            FurinaReframe.Enabled = _enabled;
            FurinaReframe.ManualEnabled = _manual;
            FurinaReframe.EvokeEnabled = _evoke;
            FurinaReframe.MeterEnabled = _meter;
            FurinaReframe.SpotlightEnabled = _spotlight;
            FurinaReframe.BurstEnabled = _burst;
        }
    }

    /// <summary>The seat's board: a Furina with a company on stage and a
    /// KNOWN buffer, because the amount is what the row is about.</summary>
    private static Seat Stage(int encore, params SalonMember[] members)
    {
        FurinaReframeLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();

        var power = (SalonMemberPower)RuntimeHelpers
            .GetUninitializedObject(typeof(SalonMemberPower));
        // The registered id, seeded the way `Bombs.Place` seeds it and for
        // the same reason: BaseLib assigns it at registration, which is
        // model-table state a test has no business mutating, and
        // `SmartDescriptionLocKey` is `Id.Entry` plus a suffix.
        Seat.Force(power, "Id", BadgeId);
        Seat.Force(power, "Amount", members.Length);
        ((System.Collections.IList)seat.Creature.Powers).Add(power);
        Seat.Force(power, "IsMutable", true);
        Seat.Force(power, "Owner", seat.Creature);

        Company()[seat.Creature] = members.ToList();
        FurinaResources.GainEncore(seat.Creature, encore);
        return seat;
    }

    /// <summary>Stand-in for the badge's registered id. See `Stage`.</summary>
    private static readonly MegaCrit.Sts2.Core.Models.ModelId BadgeId =
        new("POWER", "KLEE_SALON_MEMBER_TEST");

    private static IDictionary<Creature, List<SalonMember>> Company() =>
        (IDictionary<Creature, List<SalonMember>>)typeof(SalonMemberPower)
            .GetField("Company", HeadlessGame.All)!
            .GetValue(null)!;

    private static SalonMemberPower PowerOf(Seat seat) =>
        seat.Creature.Powers.OfType<SalonMemberPower>().First();

    // ==================================================================
    // 1. `EB-382` -- the turn start spends nothing
    // ==================================================================

    [Theory]
    [InlineData(4)]
    [InlineData(3)]
    [InlineData(1)]
    public void A_staged_turn_start_spends_no_encore_under_the_arm(int banked)
    {
        // The row's own scenario, at each of the three amounts it reports.
        // REAL: the suppressed branch returns before anything a combat is
        // needed for.
        using var _ = new Arm(manual: true);
        var seat = Stage(banked, SalonMember.Chevalmarin);

        PowerOf(seat).AfterPlayerTurnStart(default, seat.Player)
            .GetAwaiter().GetResult();

        Assert.Equal(banked, FurinaResources.Encore(seat.Creature));
    }

    [Fact]
    public void The_empty_stage_is_not_what_carried_the_control_turn()
    {
        // The seat read its control case as "no member, so nothing ate it".
        // An empty stage and a staged one carry the same buffer across the
        // same boundary, so the member was never the variable.
        using var _ = new Arm(manual: true);
        var staged = Stage(1, SalonMember.Chevalmarin);
        var empty = Stage(1);

        PowerOf(staged).AfterPlayerTurnStart(default, staged.Player)
            .GetAwaiter().GetResult();
        PowerOf(empty).AfterPlayerTurnStart(default, empty.Player)
            .GetAwaiter().GetResult();

        Assert.Equal(1, FurinaResources.Encore(staged.Creature));
        Assert.Equal(1, FurinaResources.Encore(empty.Creature));
    }

    [Theory]
    [InlineData("SalonMemberPower", "AfterPlayerTurnStart")]
    [InlineData("FurinaResourceHooks", "BeforeSideTurnStart")]
    [InlineData("FurinaResourceHooks", "AfterPlayerTurnStart")]
    public void No_turn_start_hook_takes_encore_itself(string type, string method)
    {
        // STRUCTURAL, and it is the half that covers the hooks a headless
        // harness cannot run: the two broadcasts a player turn opens with hold
        // the decay, the block flush, the Spotlight reset, the deferred draws
        // and the kit grant, and NONE of them reduces the buffer. The Salon
        // hook's own delegation to `PerformMember` is what pays the shipped
        // upkeep, and `SalonVerbTests` pins that it stays there.
        var calls = Il.Calls(Il.Method(type, method));

        Assert.DoesNotContain("FurinaResources.SpendEncore", calls);
        Assert.DoesNotContain("FurinaResources.AbsorbDamage", calls);
        Assert.DoesNotContain("FurinaResources.SpendEncoreOrHp", calls);
    }

    // ==================================================================
    // 2. `EB-382` -- where it actually goes
    // ==================================================================

    [Fact]
    public void Absorption_is_the_spend_the_seat_saw()
    {
        // Fight 1's arithmetic, reproduced: 8 damage past Block against 4
        // banked Encore leaves 4 to reach HP and empties the buffer.
        using var _ = new Arm(manual: true, meter: true);
        var seat = Stage(4, SalonMember.Chevalmarin);

        var reachedHp = FurinaResources.AbsorbDamage(seat.Creature, 8m);

        Assert.Equal(4m, reachedHp);
        Assert.Equal(0, FurinaResources.Encore(seat.Creature));
    }

    [Fact]
    public void The_arm_leaves_that_spend_no_receipt()
    {
        // WHY IT READ AS A DISAPPEARANCE. The shipped engine printed one
        // Fanfare per point absorbed, so an emptying buffer had a mark on the
        // meter beside it. The reframe's §4.1 retires that leg, and nothing
        // replaced the mark -- which is the whole of the finding, and why the
        // repair is a sentence on the page rather than a change to the rule.
        using var _ = new Arm(manual: true, meter: true);
        var seat = Stage(4, SalonMember.Chevalmarin);

        FurinaResources.AbsorbDamage(seat.Creature, 4m);

        Assert.Equal(0, FurinaResources.Encore(seat.Creature));
        Assert.Equal(0, FurinaResources.Fanfare(seat.Creature));
    }

    [Fact]
    public void The_shipped_engine_still_prints_that_receipt()
    {
        // The flag-off half: absorption is a Fanfare source in a release
        // build, which is what made the same spend visible before the arm.
        using var _ = new Arm(master: false);
        var seat = Stage(4, SalonMember.Chevalmarin);

        FurinaResources.AbsorbDamage(seat.Creature, 4m);

        Assert.Equal(0, FurinaResources.Encore(seat.Creature));
        Assert.True(FurinaResources.Fanfare(seat.Creature) > 0);
    }

    // ==================================================================
    // 3. `EB-384` -- the deploy that lost its member
    // ==================================================================

    [Fact]
    public void A_stage_the_counter_has_not_caught_up_to_survives_a_read()
    {
        // THE DEPLOY WINDOW, reproduced without a deploy, which is what makes
        // this a REAL pin rather than a structural one: `Deploy` adds the
        // entering member to the company list and applies the mirror counter
        // AFTER the loop, so for that window the stage legitimately holds a
        // member the counter has never heard of. The old staleness test read
        // "nonempty list, zero counter" as garbage from a previous combat and
        // wiped it.
        //
        // MUTATION CHECK: put `if (Count(owner) == 0 && list.Count > 0)
        // list.Clear();` back in `CompanyFor` and this fails.
        var seat = Stage(0);
        Company()[seat.Creature] = new List<SalonMember>
        {
            SalonMember.Chevalmarin,
        };

        Assert.Equal(0, SalonMemberPower.Count(seat.Creature));
        Assert.Single(SalonMemberPower.CompanyOf(seat.Creature));
    }

    [Fact]
    public void A_company_built_in_an_earlier_combat_is_still_dropped()
    {
        // The other half of the same edit, and the job the old test was
        // actually there for. The Creature key can outlive a combat, so the
        // list has to go when the combat it was built in does -- now asked of
        // the combat itself, which is the question, rather than of a counter
        // that happens to answer it most of the time.
        var seat = Stage(0, SalonMember.Crabaletta);
        SalonMemberPower.CompanyOf(seat.Creature);          // stamps this combat
        CompanyCombat()[seat.Creature] = new object();      // ... a different one

        Assert.Empty(SalonMemberPower.CompanyOf(seat.Creature));
    }

    [Fact]
    public void The_staleness_test_no_longer_asks_the_counter()
    {
        // STRUCTURAL, and it is the regression itself rather than a
        // consequence of it: the mirror counter is not the question, so
        // `CompanyFor` must not read it.
        var calls = Il.Calls(Il.Method("SalonMemberPower", "CompanyFor"));

        Assert.DoesNotContain("SalonMemberPower.Count", calls);
    }

    [Theory]
    [InlineData("SalonMemberPower", "Deploy", "SalonMemberPower.PerformMember")]
    [InlineData("SalonMemberPower", "PerformMember", "FurinaResources.SpendEncore")]
    [InlineData("FurinaResources", "SpendEncore", "SalonVisualsBridge.Refresh")]
    [InlineData("SalonVisualsBridge", "RefreshDisplay", "SalonMemberPower.CompanyOf")]
    public void The_path_that_wiped_the_stage_is_four_calls_long(
        string type, string method, string call)
    {
        // STRUCTURAL, and it is the CAUSE written down: the arm's
        // deploy-performs clause put a performance inside the window, a
        // performance that can PAY reaches the Encore spend, the spend
        // refreshes the stage art, and the art reads the company. Each link
        // is shipped and correct on its own. Kept as a pin because the fix is
        // one line in `CompanyFor` and nothing else on this path changed, so
        // a reader asking "why was that line load-bearing" gets the chain.
        Assert.Contains(call, Il.Calls(Il.Method(type, method)));
    }

    [Fact]
    public void The_members_own_tip_stops_promising_a_turn_start_act()
    {
        // `EB-384`'s display half. The seat read 1 damage in one fight and 2
        // in another off a card that prints neither, while the member tip
        // beside it described the shipped upkeep the arm deletes.
        using var _ = new Arm(manual: true);
        var seat = Stage(0);

        var tip = global::KleeMod.Cards.SalonMemberTips.BodyFor(
            SalonMember.Chevalmarin, seat.Creature);

        Assert.DoesNotContain("Each turn", tip);
        Assert.Contains("Performs for " + SalonConstants.ChevalmarinTick, tip);
        Assert.Contains("Evokes", tip);
    }

    [Fact]
    public void The_members_own_tip_is_the_shipped_one_with_the_arm_off()
    {
        using var _ = new Arm(master: false);
        var seat = Stage(0);

        var tip = global::KleeMod.Cards.SalonMemberTips.BodyFor(
            SalonMember.Chevalmarin, seat.Creature);

        Assert.StartsWith("Each turn", tip);
        Assert.Contains("Bows out", tip);
    }

    [Fact]
    public void The_arms_salon_rules_keep_the_dry_clause()
    {
        // The three-quarters cut is what makes 1 and 2 the same member on two
        // turns, and the arm's own rules paragraph had dropped it.
        using var _ = new Arm(manual: true);
        var seat = Stage(0, SalonMember.Chevalmarin);

        var rules = global::KleeMod.Cards.SalonMemberTips.SalonRulesBody(seat.Creature);

        Assert.Contains("three-quarters", rules);
        Assert.DoesNotContain("bows the OLDEST member out", rules);
    }

    // ==================================================================
    // 4. `EB-383` -- one rulebook on the screen, and a name on the buff
    // ==================================================================

    private static string LocKey(SalonMemberPower power) =>
        (string)typeof(SalonMemberPower)
            .GetProperty("SmartDescriptionLocKey", HeadlessGame.All)!
            .GetValue(power)!;

    private static string Row(SalonMemberPower power, string suffix) =>
        power.Localization!.First(r => r.Item1.EndsWith(suffix)).Item2;

    [Theory]
    [InlineData(SalonMember.Crabaletta, "Crabaletta")]
    [InlineData(SalonMember.Usher, "the Usher")]
    [InlineData(SalonMember.Chevalmarin, "Chevalmarin")]
    public void The_buff_names_the_member_it_is_about(
        SalonMember front, string printed)
    {
        // The seat "worked out mine was Chevalmarin by subtracting
        // Neuvillette's 7 from a 9-point HP drop", because the badge said
        // `Salon Member 1` and then recited all three members' abilities.
        using var _ = new Arm(manual: true);
        var seat = Stage(0, front, SalonMember.Usher);

        var key = LocKey(PowerOf(seat));
        var face = Row(PowerOf(seat), key.Split('.').Last());

        Assert.EndsWith("Manual" + front, key);
        Assert.EndsWith(printed + ".", face);
    }

    [Fact]
    public void The_buff_stops_printing_the_upkeep_the_arm_deleted()
    {
        // THE TWO RULEBOOKS, which is the row: this badge said "At the start
        // of your turn, each Salon Member spends 1 Encore for its act" three
        // lines above the Salon tip saying "Members do NOT act on their own",
        // and behaviour matched the tip in all five fights.
        using var _ = new Arm(manual: true);
        var seat = Stage(0, SalonMember.Crabaletta);

        var face = Row(PowerOf(seat), LocKey(PowerOf(seat)).Split('.').Last());

        Assert.DoesNotContain("At the start of your turn", face);
        Assert.Contains("performs at once", face);
        Assert.Contains("Evokes", face);
        Assert.Contains("Companion", face);
    }

    [Fact]
    public void An_empty_stage_still_has_a_row_to_print()
    {
        // A key with no row behind it falls back to the shipped face, which
        // would put the retired upkeep back on the screen -- so the row set
        // and the selector are built off one list and this is the pin on the
        // one member of it that is not a member.
        using var _ = new Arm(manual: true);
        var seat = Stage(0);

        var key = LocKey(PowerOf(seat));

        Assert.EndsWith("ManualEmpty", key);
        Assert.Contains(PowerOf(seat).Localization!,
            row => key.EndsWith(row.Item1));
    }

    [Fact]
    public void Every_key_the_selector_can_compose_has_a_row()
    {
        // The whole join, not one arm of it: four fronts, four rows, and the
        // rows come off the same list the selector reads.
        using var _ = new Arm(manual: true);
        var keys = new List<string>();
        foreach (var front in new SalonMember?[]
                 {
                     null, SalonMember.Crabaletta, SalonMember.Usher,
                     SalonMember.Chevalmarin,
                 })
        {
            var seat = front is { } who ? Stage(0, who) : Stage(0);
            keys.Add(LocKey(PowerOf(seat)).Split('.').Last());
        }

        var rows = PowerOf(Stage(0)).Localization!
            .Select(r => r.Item1).ToList();
        Assert.Equal(4, keys.Distinct().Count());
        foreach (var key in keys) Assert.Contains(key, rows);
    }

    [Fact]
    public void The_shipped_badge_is_untouched_with_the_arm_off()
    {
        // The acceptance condition for a release build: the same key and the
        // same paragraph the badge has printed since the v2 rework.
        using var _ = new Arm(master: false);
        var seat = Stage(0, SalonMember.Crabaletta);

        Assert.EndsWith(".smartDescription", LocKey(PowerOf(seat)));
        Assert.Contains("At the start of your turn",
            Row(PowerOf(seat), "smartDescription"));
    }

    [Fact]
    public void A_canonical_badge_answers_the_selector_without_throwing()
    {
        // `HasSmartDescription` probes this key on the compendium's own copy,
        // whose `Owner` getter asserts mutability (`EB-94`). It has no stage,
        // so the shipped key is also the honest answer.
        using var _ = new Arm(manual: true);
        var canonical = (SalonMemberPower)RuntimeHelpers
            .GetUninitializedObject(typeof(SalonMemberPower));
        Seat.Force(canonical, "Id", BadgeId);

        Assert.EndsWith(".smartDescription", LocKey(canonical));
    }

    // ==================================================================
    // 5. `EB-385` -- the Fanfare badge's generators
    // ==================================================================

    private static FanfareMeterPower Badge(Seat seat)
    {
        var badge = (FanfareMeterPower)RuntimeHelpers
            .GetUninitializedObject(typeof(FanfareMeterPower));
        Seat.Force(badge, "Id",
            new MegaCrit.Sts2.Core.Models.ModelId("POWER", "KLEE_FANFARE_TEST"));
        Seat.Force(badge, "Amount", 6);
        Seat.Force(badge, "IsMutable", true);
        Seat.Force(badge, "Owner", seat.Creature);
        return badge;
    }

    private static string BadgeKey(FanfareMeterPower badge) =>
        (string)typeof(FanfareMeterPower)
            .GetProperty("SmartDescriptionLocKey", HeadlessGame.All)!
            .GetValue(badge)!;

    [Fact]
    public void The_fanfare_badge_names_the_arms_mint_sites_and_no_others()
    {
        // The seat lost 1 HP and spent 2 Encore in one turn for 0 Fanfare,
        // then watched Salon Debut pay 2. The badge was naming three
        // generators the METER leg retires and missing the only one that mints.
        using var _ = new Arm(meter: true);
        var seat = Stage(0);
        var badge = Badge(seat);

        var key = BadgeKey(badge);
        var face = badge.Localization!
            .First(r => key.EndsWith(r.Item1)).Item2;

        Assert.EndsWith(".smartDescriptionReframe", key);
        Assert.DoesNotContain("losing HP", face);
        Assert.DoesNotContain("absorbing", face);
        Assert.DoesNotContain("Center Stage", face);
        Assert.Contains("member performing", face);
        Assert.Contains("Evoke", face);
    }

    [Fact]
    public void The_two_amounts_on_the_badge_are_the_arms_own_law()
    {
        // `EB-89`'s rule one meter over: a retune of either mint must not be
        // able to leave the badge quoting a retired number. These are the two
        // constants the mint sites read and `lint_constant_parity` mirrors.
        using var _ = new Arm(meter: true);
        var seat = Stage(0);
        var badge = Badge(seat);

        var face = badge.Localization!
            .First(r => r.Item1 == "smartDescriptionReframe").Item2;

        Assert.Contains("[blue]" + FurinaReframeLaw.FanfarePerTrigger
                        + "[/blue] when it stays", face);
        Assert.Contains("[blue]" + FurinaReframeLaw.FanfarePerEvoke
                        + "[/blue] on an", face);
    }

    [Fact]
    public void The_shipped_fanfare_badge_is_untouched_with_the_leg_off()
    {
        using var _ = new Arm(master: false);
        var seat = Stage(0);

        Assert.EndsWith(".smartDescription", BadgeKey(Badge(seat)));
    }

    [Fact]
    public void A_canonical_fanfare_badge_answers_without_throwing()
    {
        using var _ = new Arm(meter: true);
        var canonical = (FanfareMeterPower)RuntimeHelpers
            .GetUninitializedObject(typeof(FanfareMeterPower));
        Seat.Force(canonical, "Id",
            new MegaCrit.Sts2.Core.Models.ModelId("POWER", "KLEE_FANFARE_TEST"));

        Assert.EndsWith(".smartDescription", BadgeKey(canonical));
    }

    // ==================================================================
    // 6. `EB-386` -- Guest Cast's duration, and its badge telling the truth
    // ==================================================================

    [Fact]
    public void Guest_cast_prints_when_it_ends()
    {
        // The feed carries no duration field at all -- a status row is id,
        // name, amount, type and text -- so a power that does not say when it
        // ends reaches a reader as a buff with no end. The seat spent a run
        // that way: "`Guest Cast` has no printed duration."
        var power = (GuestCastPower)RuntimeHelpers
            .GetUninitializedObject(typeof(GuestCastPower));
        var face = power.Localization!
            .First(r => r.Item1 == "description").Item2;

        Assert.Contains("Lasts until the [gold]Spotlight[/gold] moves", face);
    }

    [Fact]
    public void Center_stage_prints_when_it_ends_too()
    {
        // The same sentence on the mode beside it, because a duration printed
        // on one of a pair reads as a difference between them.
        var power = (CenterStagePower)RuntimeHelpers
            .GetUninitializedObject(typeof(CenterStagePower));
        var face = power.Localization!
            .First(r => r.Item1 == "description").Item2;

        Assert.Contains("Lasts until the [gold]Spotlight[/gold] moves", face);
    }

    [Fact]
    public void The_guest_cast_badge_comes_back_when_the_mode_still_holds()
    {
        // The seat watched this badge leave the status list "while
        // `Spotlight Mode: 2` stayed and Companion cards kept showing boosted
        // numbers". The MODE is the rule and the badge is the display, so a
        // badge missing under a live mode is a display that has stopped
        // describing it. STRUCTURAL for the apply itself, which needs a
        // combat; REAL for the decision, which is the whole of the defect.
        var calls = Il.Calls(Il.Method("SpotlightSystem", "SyncModeDisplay"));

        Assert.Contains("SpotlightSystem.Mode", calls);
        Assert.Contains("PowerCmd.Apply", calls);
        Assert.DoesNotContain("PowerCmd.Remove", calls);
        Assert.Contains("SpotlightSystem.SyncModeDisplay",
            Il.Calls(Il.Method("FurinaResources", "SyncMeters")));
    }

    [Fact]
    public void The_badge_sync_grants_no_rule_and_claims_no_other_seat()
    {
        // It cannot grant an effect, because nothing reads these powers: every
        // Spotlight predicate reads the mode RESOURCE. What it can do wrong is
        // fire for the Klee at the other side of a co-op table, so the
        // identity gate is asked first, the way every Furina hook asks it.
        var calls = Il.Calls(Il.Method("SpotlightSystem", "SyncModeDisplay"));

        Assert.Contains("FurinaResources.IsFurina", calls);
    }

    private static IDictionary<Creature, object?> CompanyCombat() =>
        (IDictionary<Creature, object?>)typeof(SalonMemberPower)
            .GetField("CompanyCombat", HeadlessGame.All)!
            .GetValue(null)!;
}
