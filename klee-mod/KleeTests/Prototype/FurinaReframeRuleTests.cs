using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE FURINA REFRAME, SLICE ONE -- the four ruled sentences, both sides of
/// every flag. The C# half of what
/// <c>tier0/tests/test_furina_reframe_slice1.py</c> pins in the sim, and it is
/// deliberately the same file in the same order, section for section, so the
/// two can be read side by side.
///
/// The design is <c>review/ruled/furina-reframe-2026-08-29.md</c> (R220 A;
/// <c>F</c>-picks answered by R224) plus
/// <c>review/ruled/furina-spotlight-options-2026-08-30.md</c> §5 (R228 option
/// 1) and the slot-6 ruling of 2026-08-30. The switch is
/// <c>Powers/Prototype/FurinaReframe.cs</c>, and every flag in it ships OFF.
///
/// THE SHAPE OF THIS FILE, AND WHY IT IS THIS SHAPE. Every behavioural pin
/// comes in a pair: the same board, once with the leg's flag on and once with
/// it off. The OFF half is not padding -- it is the only assertion that can
/// catch a leg leaking into the shipped engine, which is the single failure a
/// quarantined slice can inflict on a game that is being played tonight.
/// <see cref="The_arm_ships_off"/> is first for the same reason, and it is the
/// test that fails if somebody flips a default instead of a fixture.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, the same split
/// <c>SalonVerbTests</c> and <c>KokomiOverhaulRuleTests</c> make and for the
/// same reason (README, "The headless boundary"). REAL, on live objects: the
/// flags and their scoping, the Focus arithmetic, both mints, the four retired
/// mint legs, the aim resolution, the suppression, the empty-stage whiff and
/// the two unpayable/redundant designations -- everything that decides before
/// the first await. STRUCTURAL, read off the compiled method: anything that
/// RESOLVES -- a bow, a deploy, a member performing, an applied power -- needs
/// a combat this harness cannot build, so what is pinned there is the wiring
/// the rule is made of: which flag each seam reads, and that the trigger
/// performs through the ONE shared act rather than a copy of it.
///
/// WHAT IS NOT PINNED HERE, because it is not built: the <c>F1</c> (2) fourth
/// member, the <c>F9</c> cap carriers, the <c>F11</c>/<c>F12</c> drain cards,
/// the <c>F16</c> starter delta, the <c>F13</c>/<c>F14</c>/<c>F15</c> display
/// work, the Burst-meter retirement (R220 B's own branch owns it) and the
/// named-Companion half of R228's selector. §11 of the packet carries each
/// with its reason, and the sim's slice stops at the same line.
/// </summary>
public class FurinaReframeRuleTests
{
    // ==================================================================
    // Fixtures
    // ==================================================================

    /// <summary>
    /// Turn legs on for the length of one test and put every flag back after
    /// it, whatever it does. The five flags are static -- they have to be,
    /// because the seams that read them are static -- so a test that moved one
    /// and did not restore it would silently arm the next one.
    /// </summary>
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;
        private readonly bool _evoke = FurinaReframe.EvokeEnabled;
        private readonly bool _meter = FurinaReframe.MeterEnabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;
        // R251's leg (`EB-365`). Saved and restored like the other five even
        // though no test in THIS file sets it: a fixture that restores five of
        // six flags is a fixture that arms the next file.
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

    /// <summary>
    /// A Furina seat with a company on stage and a full Encore buffer, WITHOUT
    /// running Deploy (which needs a live combat). The two seeded pieces are
    /// the two the shipped code reads -- the private per-Creature company list,
    /// which carries identity, and the counter power, which carries the count
    /// and which CompanyFor uses to detect a stale list from a previous combat.
    /// Lifted verbatim from <c>SalonVerbTests.Stage</c>; the reasoning for
    /// every reflective step is written out there.
    /// </summary>
    private static Seat Stage(params SalonMember[] members)
    {
        FurinaReframeLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();

        var power = (SalonMemberPower)RuntimeHelpers
            .GetUninitializedObject(typeof(SalonMemberPower));
        Seat.Force(power, "Amount", members.Length);
        ((System.Collections.IList)seat.Creature.Powers).Add(power);
        Seat.Force(power, "IsMutable", true);
        Seat.Force(power, "Owner", seat.Creature);

        Company()[seat.Creature] = members.ToList();
        FurinaResources.GainEncore(seat.Creature, 9);
        return seat;
    }

    private static IDictionary<Creature, List<SalonMember>> Company() =>
        (IDictionary<Creature, List<SalonMember>>)typeof(SalonMemberPower)
            .GetField("Company", HeadlessGame.All)!
            .GetValue(null)!;

    private static SalonMemberPower PowerOf(Seat seat) =>
        seat.Creature.Powers.OfType<SalonMemberPower>().First();

    /// <summary>The private numeric-amount helper, called for real. This is
    /// the one piece of the bow's arithmetic that needs no combat, and it is
    /// the piece the Evoke's Focus multiplier lands on.</summary>
    private static int Scaled(Creature owner, int printed, int focusMult) =>
        (int)Il.Method("SalonMemberPower", "Scaled")
            .Invoke(null, new object[] { owner, printed, focusMult })!;

    private static bool CenterStageActive(Creature owner) =>
        (bool)Il.Method("SpotlightSystem", "CenterStageActive")
            .Invoke(null, new object[] { owner })!;

    private static void SetSpotlightMode(Seat seat, SpotlightMode mode) =>
        CustomResources<SpotlightModeResource>
            .Get(seat.Player.PlayerCombatState).Amount = (int)mode;

    private static FurinaResourceHooks Hooks() =>
        (FurinaResourceHooks)RuntimeHelpers
            .GetUninitializedObject(typeof(FurinaResourceHooks));

    /// <summary>A real Companion card, allocated UNINITIALISED: the trigger's
    /// only question of it is `is ICompanionCard`, so identity is the whole
    /// payload, and a CustomCardModel's constructor registers with BaseLib's
    /// model tables -- state a test has no business mutating (the reasoning is
    /// <c>Seat.WithRelic</c>'s, applied to a card).</summary>
    private static CardModel Companion() =>
        (CardModel)RuntimeHelpers.GetUninitializedObject(
            typeof(global::KleeMod.Cards.Generated.BarbaraMelody));

    /// <summary>A card that is NOT a Companion, on the same terms. Furina's
    /// own cards Evoke; they do not also trigger the stage for free.</summary>
    private static CardModel NotACompanion() =>
        (CardModel)RuntimeHelpers.GetUninitializedObject(
            typeof(global::KleeMod.Cards.Furina.EtherealSpotlight));

    // ==================================================================
    // 0. THE QUARANTINE. Read this section before any other.
    // ==================================================================

    // THE ONE PIN AN ARM PROPERTY MAKES DISHONEST (2026-09-02).
    //
    // `dotnet test -p:FurinaReframe=true` defines `FURINA_REFRAME`, which is what MOVES
    // `DefaultEnabled` -- the exact value this pin asserts. So under that
    // property the pin cannot say anything true: green would mean the property
    // did nothing, and red is the property working. It is skipped there rather
    // than left to fail, because a red that means "the switch works" trains
    // everyone to ignore reds.
    //
    // ARM PROPERTIES ARE DEPLOY-LINE ONLY. The supported test configurations
    // are `dotnet test` and `dotnet test -p:PrototypeCards=true`, and this pin
    // runs in both -- which is where the acceptance condition has to hold.
    // docs/current/operations/prototype.md carries the rule.
#if FURINA_REFRAME
    [Fact(Skip = "-p:FurinaReframe=true moves FurinaReframe.DefaultEnabled, which is the value this pin asserts. Arm properties are deploy-line only: see docs/current/operations/prototype.md.")]
#else
    [Fact]
#endif
    public void The_arm_ships_off()
    {
        // The whole slice is dark on a shipped tree, and one test says so.
        // The five properties are settable so a pin can assert both sides of a
        // leg in one build; nothing in the mod ever writes one.
        Assert.False(FurinaReframe.DefaultEnabled);
        Assert.Equal(FurinaReframe.DefaultEnabled, FurinaReframe.Enabled);
        Assert.Equal(FurinaReframe.DefaultEnabled, FurinaReframe.ManualEnabled);
        Assert.Equal(FurinaReframe.DefaultEnabled, FurinaReframe.EvokeEnabled);
        Assert.Equal(FurinaReframe.DefaultEnabled, FurinaReframe.MeterEnabled);
        Assert.Equal(FurinaReframe.DefaultEnabled, FurinaReframe.SpotlightEnabled);
        // R251's leg (`EB-365`) joins the roll call rather than taking a
        // quarantine test of its own.
        Assert.Equal(FurinaReframe.DefaultEnabled, FurinaReframe.BurstEnabled);
    }

    [Fact]
    public void The_master_flag_gates_every_leg()
    {
        // A leg flag alone does nothing: the master is AND-ed into all four, so
        // one flip returns the shipped engine no matter what else is set. The
        // sim's `test_the_master_flag_gates_every_leg`, verbatim.
        using var _ = new Arm(manual: true, evoke: true, meter: true,
                              spotlight: true, burst: true, master: false);
        var furina = Seat.Furina().Creature;

        Assert.False(FurinaReframe.ManualLiveFor(furina));
        Assert.False(FurinaReframe.EvokeLiveFor(furina));
        Assert.False(FurinaReframe.MeterLiveFor(furina));
        Assert.False(FurinaReframe.SpotlightLiveFor(furina));
        Assert.False(FurinaReframe.BurstRetiredFor(furina));
    }

    [Fact]
    public void The_reframe_is_scoped_to_furina()
    {
        // One character's redesign. A roster-wide branch would be a different
        // and much larger change than the one that was countersigned -- and in
        // co-op the other seat may be Klee, whose turn-start this must not
        // suppress.
        using var _ = new Arm(manual: true, evoke: true, meter: true,
                              spotlight: true, burst: true);
        var furina = Seat.Furina().Creature;
        var klee = Seat.Klee().Creature;
        var kokomi = Seat.Kokomi().Creature;

        Assert.True(FurinaReframe.ManualLiveFor(furina));
        Assert.True(FurinaReframe.EvokeLiveFor(furina));
        Assert.True(FurinaReframe.MeterLiveFor(furina));
        Assert.True(FurinaReframe.SpotlightLiveFor(furina));
        Assert.True(FurinaReframe.BurstRetiredFor(furina));

        foreach (var other in new[] { klee, kokomi })
        {
            Assert.False(FurinaReframe.ManualLiveFor(other));
            Assert.False(FurinaReframe.EvokeLiveFor(other));
            Assert.False(FurinaReframe.MeterLiveFor(other));
            Assert.False(FurinaReframe.SpotlightLiveFor(other));
            // Klee and Kokomi each own a Burst meter, and neither is this
            // arm's to retire -- in co-op the other seat may be one of them.
            Assert.False(FurinaReframe.BurstRetiredFor(other));
        }

        // A null creature is a real state on the ownerless-play paths these
        // readers sit behind, and it is nobody's character.
        Assert.False(FurinaReframe.ManualLiveFor(null));
    }

    // ==================================================================
    // 1. MANUAL -- members do not auto-play (the single biggest change)
    // ==================================================================

    [Fact]
    public void The_turn_start_upkeep_resolves_through_PerformMember_with_the_flag_off()
    {
        // STRUCTURAL. The upkeep still runs and still delegates: the flag adds
        // an early return above the loop and changes nothing inside it.
        var upkeep = Il.Method("SalonMemberPower", "AfterPlayerTurnStart");
        var calls = Il.Calls(upkeep);

        Assert.Contains("SalonMemberPower.PerformMember", calls);
        Assert.Contains("FurinaReframe.ManualLiveFor", calls);
    }

    [Fact]
    public void Manual_suppresses_the_turn_start_upkeep()
    {
        // There is no end-of-turn Salon path, so suppressing this one
        // broadcast removes the automatic engine entirely (§2.2). REAL: the
        // suppressed branch returns before anything a combat is needed for.
        using var _ = new Arm(manual: true);
        var seat = Stage(SalonMember.Crabaletta, SalonMember.Usher);
        var encore = FurinaResources.Encore(seat.Creature);

        PowerOf(seat).AfterPlayerTurnStart(default, seat.Player)
            .GetAwaiter().GetResult();

        // No upkeep to pay, and the usher did not act.
        Assert.Equal(encore, FurinaResources.Encore(seat.Creature));
        Assert.Equal(0m, seat.Creature.Block);
    }

    [Fact]
    public void The_suppression_is_loud_rather_than_silent()
    {
        // An instrument that counted upkeeps has to be able to tell an empty
        // stage from a stage whose upkeep no longer exists (D4, and R177's
        // fuel finding was measured on the act this replaces).
        using var _ = new Arm(manual: true);
        var seat = Stage(SalonMember.Crabaletta);

        PowerOf(seat).AfterPlayerTurnStart(default, seat.Player)
            .GetAwaiter().GetResult();

        var ledger = FurinaReframeLedger.For(seat.Creature);
        Assert.Equal(1, ledger.UpkeepsSuppressed);
        Assert.Equal(1, ledger.LastUpkeepSuppressedMembers);
    }

    [Fact]
    public void An_empty_stage_says_nothing_at_turn_start()
    {
        using var _ = new Arm(manual: true);
        var seat = Stage();

        PowerOf(seat).AfterPlayerTurnStart(default, seat.Player)
            .GetAwaiter().GetResult();

        Assert.Equal(0, FurinaReframeLedger.For(seat.Creature).UpkeepsSuppressed);
    }

    // ==================================================================
    // 2. The Companion trigger -- §4.3, F3 (1) and F4 (1)
    // ==================================================================

    [Fact]
    public void The_trigger_performs_through_the_one_shared_act()
    {
        // STRUCTURAL, and it is the packet's hard requirement rather than a
        // style point: no second Salon-resolution implementation. If the hook
        // grew its own copy of the act, the Encore upkeep, the dry cut and the
        // Focus term would drift from the upkeep that performs the same
        // member. The sim pins this with a spy; here it is read off the IL.
        var calls = Il.Calls(
            Il.Method("SalonMemberPower", "CompanionPlayTrigger"));

        Assert.Contains("SalonMemberPower.PerformMember", calls);
        Assert.Contains("SalonMemberPower.RotateLeftmost", calls);
        Assert.Contains("FurinaReframe.ManualLiveFor", calls);
        // NO MINT HERE, deliberately: PerformMember carries the one mint, and
        // a second at this seam would pay the trigger twice -- breaking
        // LAW:145's per-Companion-play bound while appearing to honour it.
        Assert.DoesNotContain("FurinaReframe.MintForPerformance", calls);
        // And no copy of the act's own body.
        Assert.DoesNotContain("FurinaResources.SpendEncore", calls);
        Assert.DoesNotContain("ElementalHit.Deal", calls);
        Assert.DoesNotContain("CreatureCmd.GainBlock", calls);
    }

    [Fact]
    public void The_companion_seam_fires_once_per_play()
    {
        // STRUCTURAL, on the seam rather than the rule. `IsFirstInSeries` is
        // the phase that means "once per play_card call"; a replay is one card
        // resolved twice, and a per-play trigger a replay can double is not a
        // per-play trigger. Klee's mint is gated identically one line away, and
        // the sim gates the same call on `replay_index == 0`. The COMPANION
        // half of the sim's gate is inside the trigger itself rather than here
        // -- see the behavioural pin below -- so that the next caller cannot
        // forget it.
        var calls = Il.Calls(
            Il.Method("FurinaResourceHooks", "AfterCardPlayed"));

        Assert.Contains("SalonMemberPower.CompanionPlayTrigger", calls);
        Assert.Contains("CardPlay.get_IsFirstInSeries", calls);
    }

    [Fact]
    public void A_companion_play_with_an_empty_salon_does_nothing_extra()
    {
        // RULED (§1.1a item 2), and visible under D4 -- under its OWN name,
        // because a display must be able to tell "your Companion found an
        // empty stage" from a card the player chose to play into one.
        using var _ = new Arm(manual: true);
        var seat = Stage();
        var encore = FurinaResources.Encore(seat.Creature);

        SalonMemberPower.CompanionPlayTrigger(default, seat.Creature, Companion())
            .GetAwaiter().GetResult();

        var ledger = FurinaReframeLedger.For(seat.Creature);
        Assert.Equal(1, ledger.TriggerWhiffs);
        Assert.Equal(0, ledger.CompanionTriggers);
        Assert.Equal(encore, FurinaResources.Encore(seat.Creature));
    }

    [Fact]
    public void A_non_companion_play_never_triggers_the_stage()
    {
        // The trigger is the Companion half of the kit. Furina's own cards
        // Evoke; they do not also trigger for free. On an EMPTY stage, which
        // is the board the Companion half is loud on, so "nothing at all" is
        // distinguishable from "a whiff".
        using var _ = new Arm(manual: true);
        var seat = Stage();

        SalonMemberPower.CompanionPlayTrigger(
            default, seat.Creature, NotACompanion()).GetAwaiter().GetResult();

        var ledger = FurinaReframeLedger.For(seat.Creature);
        Assert.Equal(0, ledger.TriggerWhiffs);
        Assert.Equal(0, ledger.CompanionTriggers);
    }

    [Fact]
    public void A_companion_play_does_not_touch_the_stage_with_the_flag_off()
    {
        // The OFF half: an empty stage is exactly the board on which the ON
        // half is loud, so the same board saying nothing is the whole
        // assertion.
        using var _ = new Arm(master: false);
        var seat = Stage();

        SalonMemberPower.CompanionPlayTrigger(default, seat.Creature, Companion())
            .GetAwaiter().GetResult();

        var ledger = FurinaReframeLedger.For(seat.Creature);
        Assert.Equal(0, ledger.TriggerWhiffs);
        Assert.Equal(0, ledger.CompanionTriggers);
    }

    // ==================================================================
    // 3. Deploy tempo -- §4.2, both halves RULED
    // ==================================================================

    [Fact]
    public void A_deploy_performs_the_member_it_deploys_and_overflows_into_an_Evoke()
    {
        // STRUCTURAL: a deploy resolves a bow and a performance, both of which
        // need a combat. What is pinned is that BOTH clauses read the MANUAL
        // leg and that the performance goes through the one shared act -- the
        // member that performs being the one that ENTERED is the loop's own
        // local, which the sim pins arithmetically on its side.
        var calls = Il.Calls(Il.Method("SalonMemberPower", "Deploy"));

        Assert.Contains("FurinaReframe.ManualLiveFor", calls);
        Assert.Contains("SalonMemberPower.PerformMember", calls);
        Assert.Contains("SalonMemberPower.Bow", calls);
    }

    [Fact]
    public void The_full_stage_deploy_evokes_the_front_and_cannot_be_aimed()
    {
        // THE LOCK on the other half of the slot-6 ruling, structural because
        // the sim's version is a booby trap and this is the same trap set at
        // compile time: overflow deployment keeps evoking the FRONT
        // automatically -- that is the reward for filling the stage -- and the
        // aim is what Encore buys on the dedicated card instead. A future edit
        // that routed the overflow bow through the chooser fails HERE rather
        // than quietly erasing an asymmetry that was created on purpose.
        var calls = Il.Calls(Il.Method("SalonMemberPower", "Deploy"));

        Assert.DoesNotContain("FurinaReframe.EvokeTargetIndex", calls);
        // ... and it does not read the EVOKE leg either: §4.2's overflow Evoke
        // is the MANUAL leg's, and asking EVOKE here would make filling the
        // stage wait on a card the player may not own.
        Assert.DoesNotContain("FurinaReframe.EvokeLiveFor", calls);
    }

    // ==================================================================
    // 4. EVOKE -- §4.4, F5 (the card's choice, front by default), F6 (1), F7 (1)
    // ==================================================================

    [Fact]
    public void The_bow_is_the_shipped_bow_with_the_flag_off()
    {
        // `F6`'s multiplier is the only thing the flag adds to the verb, so
        // with it off the number is the printed base plus ONE Focus term.
        //
        // THE OFF HALF SETS THE FLAGS OFF rather than trusting the default,
        // here and in every other "with the flag off" pin below. The default
        // is what `The_arm_ships_off` is for; what this asserts is the RULE --
        // that the shipped number comes back when the leg does not apply --
        // and a rule is asserted by stating its condition, not by inheriting
        // it from the build line.
        using var _ = new Arm(master: false);
        var seat = Stage(SalonMember.Usher);
        FurinaResources.GainFanfare(
            seat.Creature, 3 * SalonConstants.FocusPerFanfare);

        Assert.Equal(1, FurinaReframe.EvokeFocusMult(seat.Creature));
        Assert.Equal(SalonConstants.UsherBow + 3,
            Scaled(seat.Creature, SalonConstants.UsherBow,
                   FurinaReframe.EvokeFocusMult(seat.Creature)));
    }

    [Fact]
    public void An_evoke_applies_the_focus_term_n_times()
    {
        // `F6` (1): a multiplier on the SAME Focus term -- one divisor, one
        // number on screen, "x N" on the face. It lands on the Focus term
        // alone and never on the printed base.
        using var _ = new Arm(evoke: true);
        var seat = Stage(SalonMember.Usher);
        FurinaResources.GainFanfare(
            seat.Creature, 3 * SalonConstants.FocusPerFanfare);

        Assert.Equal(FurinaReframeLaw.EvokeFocusMult,
            FurinaReframe.EvokeFocusMult(seat.Creature));
        Assert.Equal(
            SalonConstants.UsherBow + 3 * FurinaReframeLaw.EvokeFocusMult,
            Scaled(seat.Creature, SalonConstants.UsherBow,
                   FurinaReframe.EvokeFocusMult(seat.Creature)));
    }

    [Fact]
    public void An_empty_meter_makes_the_multiplier_worth_nothing()
    {
        // The multiplier multiplies the Focus term, and the Focus term is zero
        // below one FocusPerFanfare held. An Evoke on a cold meter is the
        // printed number -- which is what makes the meter worth holding.
        using var _ = new Arm(evoke: true);
        var seat = Stage(SalonMember.Usher);

        Assert.Equal(0, FurinaResources.ReadableFanfare(seat.Creature));
        Assert.Equal(SalonConstants.UsherBow,
            Scaled(seat.Creature, SalonConstants.UsherBow,
                   FurinaReframeLaw.EvokeFocusMult));
    }

    [Fact]
    public void The_focus_term_never_reaches_the_encore_refund_or_the_aura()
    {
        // §3.1 amendment 4, countersigned PROSPECTIVE by R224: the Focus term
        // scales performance NUMERICS only -- damage and Block -- and never
        // Energy, Encore, Charge, Fanfare itself, card generation or aura
        // stacks. The sim satisfies it structurally, by putting the multiplier
        // inside `_salon_amount` and nowhere else, and says so; this is the
        // same fact read off the same place. Chevalmarin's Encore refund is
        // the one live row the invariant touches, and `Scaled` has no path to
        // it.
        var calls = Il.Calls(Il.Method("SalonMemberPower", "Scaled"));

        Assert.Contains("FurinaResources.ReadableFanfare", calls);
        Assert.Contains("SalonDamageUpPower.AmountFor", calls);
        Assert.DoesNotContain("FurinaResources.GainEncore", calls);
        Assert.DoesNotContain("FurinaResources.GainFanfare", calls);
        Assert.DoesNotContain("FurinaResources.GainBurst", calls);
        Assert.DoesNotContain("ElementalHit.ApplyOnly", calls);
    }

    [Fact]
    public void An_unaimed_evoke_expends_the_front_member()
    {
        // `F5` as the slot-6 ruling revised it: the card may aim, and the
        // FRONT is what it takes when it names nobody. No aim and the written
        // sentinel are ONE rule, not two -- in C# the sentinel is `null`,
        // which is what `EvokeTargetFront` names.
        using var _ = new Arm(evoke: true);
        var seat = Stage(SalonMember.Usher, SalonMember.Crabaletta);
        var company = SalonMemberPower.CompanyOf(seat.Creature);

        Assert.Equal(0,
            FurinaReframe.EvokeTargetIndex(seat.Creature, company, null));
        Assert.Equal(0, FurinaReframe.EvokeTargetIndex(
            seat.Creature, company, FurinaReframe.EvokeTargetFront));
    }

    [Fact]
    public void An_aimed_evoke_takes_the_member_the_card_names()
    {
        // THE RULING: a dedicated Evoke chooses which member it removes. Each
        // of the three is named in turn off the same board, so what is pinned
        // is the aim itself and not one member's luck of the queue order.
        using var _ = new Arm(evoke: true);
        var stage = new[] { SalonMember.Usher, SalonMember.Crabaletta,
                            SalonMember.Chevalmarin };
        var seat = Stage(stage);
        var company = SalonMemberPower.CompanyOf(seat.Creature);

        for (var i = 0; i < stage.Length; i++)
        {
            Assert.Equal(i,
                FurinaReframe.EvokeTargetIndex(seat.Creature, company, stage[i]));
        }
    }

    [Fact]
    public void The_aim_is_ignored_with_the_evoke_leg_off()
    {
        // The byte-identical guard, in this file's standing shape. A row
        // carrying an aim on a release build is the shipped bow: the front
        // member. The choice is a thing the leg GIVES.
        using var _ = new Arm(master: false);
        var seat = Stage(SalonMember.Usher, SalonMember.Crabaletta,
                         SalonMember.Chevalmarin);
        var company = SalonMemberPower.CompanyOf(seat.Creature);

        Assert.Equal(0, FurinaReframe.EvokeTargetIndex(
            seat.Creature, company, SalonMember.Chevalmarin));
    }

    [Fact]
    public void An_aim_at_an_absent_member_is_reported_rather_than_wasted()
    {
        // An aimed card that cannot find its member is an UNAIMED Evoke, never
        // a wasted one -- and under D4 the miss is recorded, because the aim
        // leaves no trace in the state afterwards for a display to read. The
        // sentinel is the caller's instruction to take the front.
        using var _ = new Arm(evoke: true);
        var seat = Stage(SalonMember.Usher, SalonMember.Crabaletta);
        var company = SalonMemberPower.CompanyOf(seat.Creature);

        Assert.Equal(FurinaReframe.EvokeTargetAbsent,
            FurinaReframe.EvokeTargetIndex(
                seat.Creature, company, SalonMember.Chevalmarin));

        // The verb is what records it, and it takes the front when it does.
        var calls = Il.Calls(Il.Method("SalonMemberPower", "BowLeftmost"));
        Assert.Contains("FurinaReframe.EvokeTargetIndex", calls);
        Assert.Contains(
            "FurinaReframeLedger.NoteEvokeTargetAbsent", calls);
        Assert.Contains("FurinaReframe.EvokeLiveFor", calls);
    }

    [Fact]
    public void The_evoke_price_is_the_cards_shipped_encore_cost()
    {
        // `F7` (1) NEEDED NO PORT, and this pin is what says so rather than an
        // absence. The price is the card's printed Encore cost: a playability
        // GATE and then a spend, both before the op resolves, so an Evoke that
        // cannot be paid for is never half-resolved. That machinery is
        // SHIPPED in both engines -- `FurinaResourceHooks.BeforeCardPlayed`
        // reads the card's Encore cost and spends it, on every card, arm or no
        // arm -- so the reframe adds nothing here and must not.
        var calls = Il.Calls(
            Il.Method("FurinaResourceHooks", "BeforeCardPlayed"));

        Assert.Contains("FurinaResources.SpendEncore", calls);
        Assert.DoesNotContain("FurinaReframe.EvokeLiveFor", calls);
    }

    // ==================================================================
    // 5. METER -- §4.1, performance mints and nothing else does
    // ==================================================================

    [Fact]
    public void A_performance_mints_the_trigger_amount()
    {
        using var _ = new Arm(meter: true);
        var seat = Stage(SalonMember.Usher);

        FurinaReframe.MintForPerformance(seat.Creature);

        Assert.Equal(FurinaReframeLaw.FanfarePerTrigger,
            FurinaResources.Fanfare(seat.Creature));
    }

    [Fact]
    public void An_evoke_mints_the_larger_amount()
    {
        // The ordering is the RULED half of the pair: trigger < Evoke, because
        // an Evoke costs a member. The two figures are prototype seeds.
        using var _ = new Arm(meter: true);
        var seat = Stage(SalonMember.Usher);

        FurinaReframe.MintForEvoke(seat.Creature);

        Assert.Equal(FurinaReframeLaw.FanfarePerEvoke,
            FurinaResources.Fanfare(seat.Creature));
        Assert.True(FurinaReframeLaw.FanfarePerEvoke
                    > FurinaReframeLaw.FanfarePerTrigger);
    }

    [Fact]
    public void Neither_mint_pays_with_the_meter_leg_off()
    {
        using var _ = new Arm(master: false);
        var seat = Stage(SalonMember.Usher);

        FurinaReframe.MintForPerformance(seat.Creature);
        FurinaReframe.MintForEvoke(seat.Creature);

        Assert.Equal(0, FurinaResources.Fanfare(seat.Creature));
    }

    [Fact]
    public void The_mint_is_bounded_per_companion_play()
    {
        // LAW:145 (countersigned R224) permits a character engine to answer a
        // Companion play and mint its resource only where the kit "bounds the
        // amount generated per Companion play". One play, one performance, one
        // bounded mint -- Klee's `KleeCompanionSpark.MaxPerPlay` is the same
        // declaration, and the bound is APPLIED here rather than asserted.
        using var _ = new Arm(meter: true);
        var seat = Stage(SalonMember.Usher, SalonMember.Crabaletta);

        FurinaReframe.MintForPerformance(seat.Creature);

        Assert.True(FurinaResources.Fanfare(seat.Creature)
                    <= FurinaReframeLaw.FanfarePerCompanionTriggerMax);
        Assert.Contains("FurinaReframe.MintForPerformance",
            Il.Calls(Il.Method("SalonMemberPower", "PerformMember")));
        Assert.Contains("FurinaReframe.MintForEvoke",
            Il.Calls(Il.Method("SalonMemberPower", "Bow")));
    }

    [Theory]
    [InlineData("hp_lost")]
    [InlineData("encore_spent")]
    [InlineData("encore_absorbed")]
    public void The_shipped_generation_legs_mint_nothing(string leg)
    {
        // §4.1 retires all four legs, and with them the shipped invariant
        // "every point of damage past Block prints exactly 1 Fanfare".
        using var _ = new Arm(meter: true);
        var seat = Stage(SalonMember.Usher);

        RunLeg(seat, leg);

        Assert.Equal(0, FurinaResources.Fanfare(seat.Creature));
    }

    [Theory]
    [InlineData("hp_lost")]
    [InlineData("encore_spent")]
    [InlineData("encore_absorbed")]
    public void The_shipped_generation_legs_still_mint_with_the_flag_off(string leg)
    {
        using var _ = new Arm(master: false);
        var seat = Stage(SalonMember.Usher);

        RunLeg(seat, leg);

        Assert.True(FurinaResources.Fanfare(seat.Creature) > 0);
    }

    private static void RunLeg(Seat seat, string leg)
    {
        switch (leg)
        {
            case "hp_lost":
                Hooks().AfterCurrentHpChanged(seat.Creature, -7m)
                    .GetAwaiter().GetResult();
                break;
            case "encore_spent":
                FurinaResources.SpendEncore(seat.Creature, 3);
                break;
            default:
                FurinaResources.AbsorbDamage(seat.Creature, 4m);
                break;
        }
    }

    [Fact]
    public void The_retired_legs_stop_the_fanfare_and_nothing_else()
    {
        // The reframe retires the FANFARE legs. It says nothing about Burst,
        // and it says nothing about the ABSORPTION itself -- the buffer still
        // eats the hit, which is what the buffer is for. Both halves pinned,
        // because "the leg is off" is easy to over-apply by one line.
        using var _ = new Arm(meter: true);
        var seat = Stage(SalonMember.Usher);
        var encore = FurinaResources.Encore(seat.Creature);

        FurinaResources.SpendEncore(seat.Creature, 3);

        Assert.Equal(encore - 3, FurinaResources.Encore(seat.Creature));
        Assert.Equal(3 * FurinaResourceConstants.BurstPerEncoreSpent,
            FurinaResources.Burst(seat.Creature));

        var remaining = FurinaResources.AbsorbDamage(seat.Creature, 4m);
        Assert.Equal(0m, remaining);
    }

    [Fact]
    public void The_meter_still_decays()
    {
        // KEPT by §3, and it is the load-bearing half of the whole design: a
        // number that only rises is what D2 calls not-a-decision, and the
        // brake is what makes holding the meter a demand on the stage. So the
        // port leaves `DecayFanfare` alone, and this pin is what makes that an
        // assertion rather than an omission -- with the METER leg ON, which is
        // the leg that could plausibly have been read as retiring it.
        using var _ = new Arm(meter: true, manual: true);
        var seat = Stage(SalonMember.Usher);
        FurinaResources.GainFanfare(seat.Creature, 20);

        var fell = FurinaResources.DecayFanfare(seat.Creature);

        Assert.True(fell > 0);
        Assert.Equal(20 - fell, FurinaResources.Fanfare(seat.Creature));
        Assert.DoesNotContain("FurinaReframe.MeterLiveFor",
            Il.Calls(Il.Method("FurinaResources", "DecayFanfare")));
    }

    [Fact]
    public void The_center_stage_leg_asks_the_same_question_as_the_other_three()
    {
        // STRUCTURAL, because the fourth leg is inside a card-play broadcast.
        // Two flags empty it for two different reasons and either alone is
        // enough: the METER leg retires "a Spotlighted card played" as a
        // Fanfare source, and R228's SPOTLIGHT leg retires Center Stage
        // outright. The sim's `combat._finish_play` carries both tests too.
        var calls = Il.Calls(Il.Method("SpotlightSystem", "NotePlay"));

        Assert.Contains(
            "FurinaResources.ReframeRetiresTheShippedMintLegs", calls);
        Assert.Contains("SpotlightSystem.CenterStageActive", calls);
    }

    [Fact]
    public void The_four_retired_legs_ask_one_question_in_one_place()
    {
        // A rule stated once should be asked once. All four legs route through
        // the same reader, so a fifth leg cannot be retired by accident and
        // none of the four can be missed.
        foreach (var (type, method) in new[]
                 {
                     ("FurinaResources", "SpendEncore"),
                     ("FurinaResources", "AbsorbDamage"),
                     ("FurinaResourceHooks", "AfterCurrentHpChanged"),
                     ("SpotlightSystem", "NotePlay"),
                 })
        {
            Assert.Contains(
                "FurinaResources.ReframeRetiresTheShippedMintLegs",
                Il.Calls(Il.Method(type, method)));
        }
    }

    // ==================================================================
    // 6. SPOTLIGHT -- R228 option (1), ONE MODE, PRICED
    // ==================================================================

    [Fact]
    public void Center_stage_is_live_with_the_flag_off()
    {
        using var _ = new Arm(master: false);
        var seat = Stage();
        SetSpotlightMode(seat, SpotlightMode.CenterStage);

        Assert.True(CenterStageActive(seat.Creature));
    }

    [Fact]
    public void Center_stage_retires_under_the_one_mode_flag()
    {
        using var _ = new Arm(spotlight: true);
        var seat = Stage();
        SetSpotlightMode(seat, SpotlightMode.CenterStage);

        Assert.False(CenterStageActive(seat.Creature));
    }

    [Fact]
    public void An_unaffordable_designation_is_a_no_op_and_not_a_discount()
    {
        // "Free when under-priced" is the failure R228 names as its own
        // biggest risk. An unpaid aim leaves the Spotlight where it was and
        // says so.
        using var _ = new Arm(spotlight: true);
        var seat = Seat.Furina().WithCombatState();
        FurinaReframeLedger.ResetAll();
        FurinaResources.GainEncore(
            seat.Creature, FurinaReframeLaw.SpotlightDesignateEncoreCost - 1);

        SpotlightSystem.DesignateOneMode(default, seat.Creature, null)
            .GetAwaiter().GetResult();

        Assert.Equal(SpotlightMode.None, SpotlightSystem.Mode(seat.Creature));
        Assert.Equal(FurinaReframeLaw.SpotlightDesignateEncoreCost - 1,
            FurinaResources.Encore(seat.Creature));
        Assert.Equal(1,
            FurinaReframeLedger.For(seat.Creature).DesignationsUnpaid);
    }

    [Fact]
    public void Re_aiming_at_the_same_target_bills_nothing()
    {
        using var _ = new Arm(spotlight: true);
        var seat = Stage();
        SetSpotlightMode(seat, SpotlightMode.GuestCast);
        var encore = FurinaResources.Encore(seat.Creature);

        SpotlightSystem.DesignateOneMode(default, seat.Creature, null)
            .GetAwaiter().GetResult();

        Assert.Equal(encore, FurinaResources.Encore(seat.Creature));
        Assert.Equal(1,
            FurinaReframeLedger.For(seat.Creature).DesignationsRedundant);
    }

    [Fact]
    public void The_selector_pays_then_aims_guest_cast()
    {
        // STRUCTURAL for the paid path, which applies a Power and therefore
        // needs a combat. The order is the assertion: the spend happens, and
        // then the shipped `Designate` does the aiming -- so the one-mode
        // selector adds a price and reuses everything else, which is what
        // "Guest Cast and the base multiplier STAY" means in code.
        var sequence = Il.CallSequence(
            Il.Method("SpotlightSystem", "DesignateOneMode")).ToList();

        Assert.Contains("FurinaReframe.SpotlightLiveFor", sequence);
        Assert.Contains("FurinaResources.SpendEncore", sequence);
        Assert.Contains("SpotlightSystem.Designate", sequence);
        Assert.True(
            sequence.IndexOf("FurinaResources.SpendEncore")
            < sequence.LastIndexOf("SpotlightSystem.Designate"),
            "the price is paid before the aim lands");
    }

    [Fact]
    public void The_selector_card_skips_its_choice_screen_under_the_arm()
    {
        // The card's own seam. With one mode there is nothing to choose, so
        // the choose-a-card screen is not shown at all rather than shown with
        // a single option on it.
        var calls = Il.Calls(Il.Method("EtherealSpotlight", "OnPlay"));

        Assert.Contains("FurinaReframe.SpotlightLiveFor", calls);
        Assert.Contains("SpotlightSystem.DesignateOneMode", calls);
        // The shipped path is still there, for the release build and for the
        // arm-off dev build.
        Assert.Contains("CardSelectCmd.FromChooseACardScreen", calls);
    }

    [Fact]
    public void Guest_cast_still_multiplies_by_the_shipped_number()
    {
        // KEPT by R228: Guest Cast and its 1.5x are exactly what they ship.
        // The pick moved what the selector IS, not what it pays.
        Assert.Equal(1.5m, SpotlightSystem.GuestCastBaseMultiplier);
    }

    // ==================================================================
    // 7. THE NUMBERS, and where they came from
    // ==================================================================

    [Fact]
    public void Every_rule_number_is_the_sims()
    {
        // The values themselves are compared against
        // tier0/engine/furina_reframe.py BY VALUE, every CI run, by
        // tools/lint_constant_parity.py -- which is the only place that
        // comparison can honestly be made. What this pin adds is the RELATION
        // the parity gate cannot express: the trigger/Evoke ordering, which is
        // the ruled half of the pair, and the LAW:145 bound being the trigger
        // amount rather than a fifth number.
        Assert.True(FurinaReframeLaw.FanfarePerEvoke
                    > FurinaReframeLaw.FanfarePerTrigger);
        Assert.Equal(FurinaReframeLaw.FanfarePerTrigger,
            FurinaReframeLaw.FanfarePerCompanionTriggerMax);
        Assert.True(FurinaReframeLaw.EvokeFocusMult > 1);
        Assert.True(FurinaReframeLaw.SpotlightDesignateEncoreCost > 0);
        // `EB-479` (R258): the opening buys exactly ONE of the two turn-one
        // doors and never two, which is the relation the value alone cannot
        // state. The selector's price is the arm's own number and is the one
        // this is sized against.
        Assert.Equal(FurinaReframeLaw.SpotlightDesignateEncoreCost,
                     FurinaReframeLaw.OpeningEncore);
    }

    // ==================================================================
    // 8. `EB-479` (R258) -- the opening Encore
    // ==================================================================
    //
    // Rounds 5 to 8 each read her first turn as no decision at 0 Encore, and
    // round 9 called the opening "by construction its own weakest version":
    // both turn-one doors the arm opens -- a Spotlight designation, a member
    // performing wet rather than at 3/4 -- cost Encore, and she had none.
    //
    // REAL, not structural: `FurinaResources.GainEncore` needs a
    // `PlayerCombatState` and nothing else, which `WithCombatState` builds, so
    // the amount that lands is checkable here. What is structural is the SITE,
    // read off the compiled turn-start hook.

    private static Seat Opening(Seat seat, int turn)
    {
        var state = seat.WithCombatState().Player.PlayerCombatState!;
        Seat.Force(state, "TurnNumber", turn);
        return seat;
    }

    [Fact]
    public void EB479_the_arm_opens_each_combat_with_two_encore()
    {
        using var _ = new Arm();
        var seat = Opening(Seat.Furina(), turn: 1);

        FurinaReframeOpening.GrantEncore(seat.Player);

        Assert.Equal(FurinaReframeLaw.OpeningEncore,
                     FurinaResources.Encore(seat.Creature));
    }

    [Fact]
    public void EB479_the_shipped_kit_opens_on_nothing()
    {
        // FLAG OFF IS THE SHIPPED OPENING, which is zero and always has been.
        using var _ = new Arm(master: false);
        var seat = Opening(Seat.Furina(), turn: 1);

        FurinaReframeOpening.GrantEncore(seat.Player);

        Assert.Equal(0, FurinaResources.Encore(seat.Creature));
    }

    [Fact]
    public void EB479_only_turn_one_is_paid()
    {
        // `== 1` rather than `<= 1`, the opening Spark's own guard: an extra
        // first turn cannot pay twice and a second turn pays nothing.
        using var _ = new Arm();
        var seat = Opening(Seat.Furina(), turn: 2);

        FurinaReframeOpening.GrantEncore(seat.Player);

        Assert.Equal(0, FurinaResources.Encore(seat.Creature));
    }

    [Fact]
    public void EB479_no_other_seat_is_paid()
    {
        // In co-op the other seat may be Klee, and a bare flag read would hand
        // him a buffer he has no rule for. Identity is `IsFurina`, which is
        // what `lint_prototype_patch_scope` requires of anything running on
        // every seat at the table under the one prototype switch.
        using var _ = new Arm();
        var seat = Opening(Seat.Klee(), turn: 1);

        FurinaReframeOpening.GrantEncore(seat.Player);

        Assert.Equal(0, FurinaResources.Encore(seat.Creature));
    }

    [Fact]
    public void EB479_the_site_is_the_turn_start_hook()
    {
        // STRUCTURAL PIN (Il). `BeforeCombatStart` sounds right and is wrong:
        // the sim fires its combat-start effects on TURN 1 after the block
        // clear, the energy reset and the draw, and turn 1 of this hook is
        // that same moment. Sim twin: `combat._player_turn` calls
        // `furina_reframe.grant_opening_encore` one line after the opening
        // Spark's own call.
        Assert.Contains("FurinaReframeOpening.GrantEncore", Il.Calls(
            Il.Method("KleeElementalHooks", "AfterPlayerTurnStart")));

        var grant = Il.Calls(Il.Method("FurinaReframeOpening", "GrantEncore"));
        Assert.Contains("FurinaReframe.LiveFor", grant);
        Assert.Contains("FurinaResources.GainEncore", grant);
    }

    // ==================================================================
    // 9. `EB-553` (R260) -- the stage starts with a member
    // ==================================================================
    //
    // Round 11 read both lanes' turn one as empty BY CONSTRUCTION: the stage
    // starts unlit, so on turn one every Companion card prints "performs
    // nobody". [USER] took the relic option -- the starting relic fields
    // Mademoiselle Crabaletta at combat start, the way the Necrobinder's Osty
    // and the Defect's first orb are already out -- over an Innate starter.
    //
    // REAL, not structural: `OpeningMemberFor` decides before the first await,
    // so both sides of the flag, the turn guard and the identity scope are
    // checkable here. What is structural is the DEPLOY, which resolves through
    // `PowerCmd` and `ElementalHit` and needs a combat this harness cannot
    // build.

    [Fact]
    public void EB553_the_arm_opens_every_combat_with_crabaletta_on_stage()
    {
        using var _ = new Arm();
        var seat = Opening(Seat.Furina(), turn: 1);

        Assert.Equal(SalonMember.Crabaletta,
                     FurinaReframeOpening.OpeningMemberFor(seat.Player));
    }

    [Fact]
    public void EB553_the_shipped_kit_opens_on_an_empty_stage()
    {
        // FLAG OFF NOTHING IS FIELDED, which is the shipped opening and always
        // has been: the stage is empty until a card deploys onto it.
        using var _ = new Arm(master: false);
        var seat = Opening(Seat.Furina(), turn: 1);

        Assert.Null(FurinaReframeOpening.OpeningMemberFor(seat.Player));
    }

    [Fact]
    public void EB553_only_turn_one_fields_a_member()
    {
        // `== 1` rather than `<= 1`, the opening Encore's own guard one rule
        // over: an extra first turn cannot field twice, and turn two fields
        // nobody -- a stage that refilled itself every turn would delete the
        // Deploy cards' whole job.
        using var _ = new Arm();
        var seat = Opening(Seat.Furina(), turn: 2);

        Assert.Null(FurinaReframeOpening.OpeningMemberFor(seat.Player));
    }

    [Fact]
    public void EB553_no_other_seat_gets_a_stage()
    {
        // In co-op the other seat may be Klee, who has no Salon at all.
        using var _ = new Arm();
        var seat = Opening(Seat.Klee(), turn: 1);

        Assert.Null(FurinaReframeOpening.OpeningMemberFor(seat.Player));
    }

    [Fact]
    public void EB553_the_member_is_named_and_never_rolled()
    {
        // `EB-416`'s finding one rule over: under the manual stage the FRONT
        // member is the one a Companion play makes perform, so a rolled
        // opening would decide for the player which member their first trigger
        // fires. It is the starter deploy's own member.
        Assert.Equal(SalonMember.Crabaletta, FurinaReframeOpening.OpeningMember);
    }

    [Fact]
    public void EB553_the_site_is_the_turn_start_hook_after_the_grant()
    {
        // STRUCTURAL PIN (Il), and the ORDER is the point: the arrival
        // performance spends Encore, so the fielding has to run AFTER the
        // opening grant or she acts dry at three-quarters on the one turn the
        // player could not have paid for her. Il cannot see a reordering
        // inside one method, so the order is stated in the source comment and
        // what is pinned here is that both calls are in the same hook.
        var hook = Il.Calls(Il.Method("KleeElementalHooks", "AfterPlayerTurnStart"));
        Assert.Contains("FurinaReframeOpening.GrantEncore", hook);
        Assert.Contains("FurinaReframeOpening.FieldOpeningMember", hook);

        // A DEPLOY AND NOT A SECOND WAY ONTO THE STAGE: it goes through
        // `SalonMemberPower.Deploy`, the one implementation, which is what
        // makes "she performs on arrival" inherited from the arm's
        // deploy-performs clause rather than restated here.
        var field = Il.Calls(
            Il.Method("FurinaReframeOpening", "FieldOpeningMember"));
        Assert.Contains("FurinaReframeOpening.OpeningMemberFor", field);
        Assert.Contains("SalonMemberPower.Deploy", field);

        var decide = Il.Calls(
            Il.Method("FurinaReframeOpening", "OpeningMemberFor"));
        Assert.Contains("FurinaReframe.LiveFor", decide);
    }

    [Fact]
    public void EB553_the_relic_carries_the_rule_and_asks_the_live_flag()
    {
        // STRUCTURAL PIN (Il). Enumerating a hover tip end to end formats a
        // `LocString` through `LocManager.Instance`, which is null until the
        // game boots (README, the headless boundary; `ArmKeywordTipTests`
        // records the same). What is reachable is the DECISION and the wiring.
        //
        // THE RULE BELONGS TO THE RELIC, which is true on turn one of every
        // fight whatever the opening hand holds -- and it rides as a tip
        // because the arm's relic face is at 117 of the 120-character relic
        // ceiling with two ruled sentences already on it.
        //
        // AND IT ASKS THE FLAG AT READ TIME, not the compile constant its own
        // face uses: a `Localization` is read once at registration while
        // `ExtraHoverTips` is read on every hover, so a dev build running the
        // reframe off prints nothing here.
        var tips = Il.Calls(
            Il.Method("EtherealSpotlightRelic", "get_ExtraHoverTips"));
        Assert.Contains("ArmKeywordTips.ForOpeningStage", tips);
        Assert.Contains("FurinaReframe.get_Enabled", tips);

        // The sentence itself is `ArmKeywordTips`', measured against the
        // 135-character tip ceiling by `tools/lint_text_conventions.py` and
        // pinned in `ArmKeywordTipTests`.
        Assert.Contains(
            "Mademoiselle Crabaletta",
            string.Concat(Il.Strings(
                Il.Method("ArmKeywordTips", "ForOpeningStage"))));
    }
}
