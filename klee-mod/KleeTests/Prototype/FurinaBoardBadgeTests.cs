using System;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-636`: THE THREE METERS LEAVE THE POWER ROW, AND STAY ON THE WIRE.
///
/// THE FIND. [USER] on the `0.2.2917+proto` frame: Encore, Fanfare and the
/// Salon member count should not sit in the power row once the board carries
/// them. The frame shows a "3" and a "13" among Furina's statuses while the
/// member strip at her feet already names three members and the badge beside
/// the energy orb already prints the Fanfare with its next threshold.
///
/// WHAT IS REAL HERE. Both halves of the decision: which powers are suppressed
/// under which leg, whose creature it is judged on, and -- the half that
/// constrains the whole design -- that the MODELS stay applied and visible, so
/// the understudy wire still carries them.
///
/// WHAT NOTHING HERE CAN VERIFY: whether the row reads better without them.
/// That is a frame on the next `+proto` deploy.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class FurinaBoardBadgeTests
{
    private const BindingFlags All = HeadlessGame.All;

    /// <summary>Every reframe flag moved together and every one restored --
    /// <see cref="SalonMemberStripPinTests"/>' fixture, and for its reason.
    /// The `manual` and `meter` legs are settable on their own because the two
    /// meters hide under different legs and the pins say which.</summary>
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;
        private readonly bool _evoke = FurinaReframe.EvokeEnabled;
        private readonly bool _meter = FurinaReframe.MeterEnabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;
        private readonly bool _burst = FurinaReframe.BurstEnabled;

        internal Arm(bool master = true, bool? manual = null,
                     bool? meter = null)
        {
            FurinaReframe.Enabled = master;
            FurinaReframe.ManualEnabled = manual ?? master;
            FurinaReframe.EvokeEnabled = master;
            FurinaReframe.MeterEnabled = meter ?? master;
            FurinaReframe.SpotlightEnabled = master;
            FurinaReframe.BurstEnabled = master;
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

    private static PowerModel PowerOn<T>(Seat seat) where T : PowerModel =>
        seat.Creature.Powers.OfType<T>().Single();

    // === 1. which badges go, and under which leg =========================

    [Fact]
    public void The_three_meters_lose_their_badges_under_their_own_legs()
    {
        var furina = Seat.Furina()
                         .WithPower<SalonMemberPower>(3)
                         .WithPower<EncoreMeterPower>(2)
                         .WithPower<FanfareMeterPower>(13);

        using (new Arm())
        {
            Assert.True(FurinaBoardBadges.HidesBadge(
                PowerOn<SalonMemberPower>(furina)));
            Assert.True(FurinaBoardBadges.HidesBadge(
                PowerOn<EncoreMeterPower>(furina)));
            Assert.True(FurinaBoardBadges.HidesBadge(
                PowerOn<FanfareMeterPower>(furina)));
        }

        // THE ACCEPTANCE CONDITION. Off the arm the very same powers on the
        // very same seat keep their badges: this is a display retirement
        // inside one arm, not a roster change.
        using (new Arm(master: false))
        {
            foreach (var power in furina.Creature.Powers)
            {
                Assert.False(FurinaBoardBadges.HidesBadge(power));
            }
        }
    }

    [Fact]
    public void Each_meter_hides_under_the_leg_that_draws_its_replacement()
    {
        // A meter whose replacement is not compiled into this build must KEEP
        // its badge, or the number leaves the screen altogether. The company
        // and the pips are the member strip, which is the MANUAL leg
        // (`SalonMemberStrip.AppliesTo`); the Fanfare badge beside the energy
        // orb is the METER leg (`FanfareCounter.AppliesTo`).
        var furina = Seat.Furina()
                         .WithPower<SalonMemberPower>(3)
                         .WithPower<EncoreMeterPower>(2)
                         .WithPower<FanfareMeterPower>(13);

        using (new Arm(master: true, manual: false))
        {
            Assert.False(FurinaBoardBadges.HidesBadge(
                PowerOn<SalonMemberPower>(furina)));
            Assert.False(FurinaBoardBadges.HidesBadge(
                PowerOn<EncoreMeterPower>(furina)));
            Assert.True(FurinaBoardBadges.HidesBadge(
                PowerOn<FanfareMeterPower>(furina)));
        }

        using (new Arm(master: true, meter: false))
        {
            Assert.True(FurinaBoardBadges.HidesBadge(
                PowerOn<SalonMemberPower>(furina)));
            Assert.False(FurinaBoardBadges.HidesBadge(
                PowerOn<FanfareMeterPower>(furina)));
        }

        // And the two predicates ARE the two elements' own scopes rather than
        // second copies of them.
        using var _ = new Arm();
        Assert.True(SalonMemberStrip.AppliesTo(furina.Creature));
        Assert.True(FanfareCounter.AppliesTo(furina.Creature));
    }

    [Fact]
    public void Furinas_statuses_keep_their_badges()
    {
        // The finding is about RESOURCES sitting among the statuses, not about
        // the strip. Same line `SparkGauge.HidesBadge` draws one character
        // over.
        var furina = Seat.Furina()
                         .WithPower<SalonMemberPower>(3)
                         .WithPower<SalonCapUpPower>(1)
                         .WithPower<GuestCastPower>(1);

        using var _ = new Arm();
        Assert.False(FurinaBoardBadges.HidesBadge(
            PowerOn<SalonCapUpPower>(furina)));
        Assert.False(FurinaBoardBadges.HidesBadge(
            PowerOn<GuestCastPower>(furina)));
    }

    [Fact]
    public void A_second_seats_meter_is_judged_by_its_own_owner()
    {
        // Co-op, and `EB-225`'s rule: this prefix runs on every power added on
        // every seat at the table. A Fanfare meter that is somehow on a Klee
        // is not this arm's business, and the character scope is stated in the
        // patch's own file rather than left inside the leg readers.
        var klee = Seat.Klee().WithPower<FanfareMeterPower>(4);
        using var _ = new Arm();

        Assert.False(FurinaBoardBadges.HidesBadge(
            PowerOn<FanfareMeterPower>(klee)));

        var source = Source("Vfx/Prototype/FurinaBoardBadges.cs");
        Assert.Contains("FurinaResources.IsFurina(owner)", source);
    }

    [Fact]
    public void A_canonical_meter_is_asked_without_throwing()
    {
        // `EB-94`. The prefix runs inside the game's badge container, and
        // `PowerModel.Owner`'s getter asserts mutability and THROWS on a
        // canonical model -- a throw there takes the whole status strip with
        // it. An ownerless power simply has no badge to suppress.
        using var _ = new Arm();
        Assert.False(FurinaBoardBadges.HidesBadge(new FanfareMeterPower()));
        Assert.False(FurinaBoardBadges.HidesBadge(new EncoreMeterPower()));
    }

    // === 2. the wire's own precondition ==================================

    [Fact]
    public void The_meters_stay_VISIBLE_to_the_model_so_the_wire_keeps_them()
    {
        // THE REASON THE BADGE IS SUPPRESSED AT THE CONTAINER, and the answer
        // to the row's "find how the game hides a power's icon". The game DOES
        // ship a designed way -- `PowerModel.IsVisibleInternal`, which
        // `AmbergrisPower` overrides to false -- and it cannot be used here:
        // the understudy bridge's `BuildPowersState` opens with
        // `if (!power.IsVisible) continue;`, so an invisible power leaves the
        // observed board entirely and every `expect: power:` reading Encore,
        // Fanfare or the member count would go silently blind.
        //
        // So none of the three overrides it, and the suppression happens at
        // the one container that turns a model into a node.
        foreach (var type in new[]
                 {
                     typeof(SalonMemberPower), typeof(EncoreMeterPower),
                     typeof(FanfareMeterPower),
                 })
        {
            var declared = type.GetProperty("IsVisibleInternal", All)
                ?.GetGetMethod(nonPublic: true)
                ?.DeclaringType;
            Assert.Equal(typeof(PowerModel), declared);
        }
    }

    [Fact]
    public void The_models_are_still_applied_when_their_badges_are_gone()
    {
        // The other half of the same condition: hiding the ROW must not remove
        // the POWER. The wire reads a creature's `Powers`, so this is what a
        // scenario's `expect: power: {name: "Salon Member"}` is asserting
        // against -- `understudy/scenarios/furina-full-stage-frame.yaml` reads
        // all three off the live lane for exactly this reason.
        var furina = Seat.Furina()
                         .WithPower<SalonMemberPower>(3)
                         .WithPower<FanfareMeterPower>(13);

        using var _ = new Arm();
        Assert.True(FurinaBoardBadges.HidesBadge(
            PowerOn<SalonMemberPower>(furina)));

        Assert.Contains(furina.Creature.Powers,
                        p => p is SalonMemberPower { Amount: 3 });
        Assert.Contains(furina.Creature.Powers,
                        p => p is FanfareMeterPower { Amount: 13 });
    }

    // === 3. the patch ====================================================

    [Fact]
    public void The_suppression_is_a_prefix_at_the_games_own_choke_point()
    {
        // `NPowerContainer.Add` is the ONE place a power becomes a strip node
        // and it already gates on `power.IsVisible`; the prefix adds the arm's
        // exceptions beside that gate. A PREFIX THAT SKIPS THE ORIGINAL rather
        // than a postfix that removes a node: the container re-lays its own
        // `_powerNodes` on every add, so a node never created leaves no gap.
        var patch = typeof(FurinaBoardBadges).Assembly
            .GetType("KleeMod.Vfx.NPowerContainer_Add_FurinaBoardBadges_Patch")!;

        var attribute = patch.GetCustomAttribute<HarmonyPatch>()!;
        Assert.Equal(typeof(NPowerContainer), attribute.info.declaringType);
        Assert.Equal("Add", attribute.info.methodName);

        var prefix = patch.GetMethod("Prefix", All)!;
        Assert.NotNull(prefix.GetCustomAttribute<HarmonyPrefix>());
        // Returning bool is what makes it a skip rather than an observer.
        Assert.Equal(typeof(bool), prefix.ReturnType);
        Assert.Contains(Il.Calls(prefix),
            c => c.EndsWith("FurinaBoardBadges.HidesBadge",
                            StringComparison.Ordinal));
    }

    [Fact]
    public void It_is_a_second_prefix_beside_the_sparks_and_not_folded_in()
    {
        // Two arms, two characters, two flags, two reverts. One predicate that
        // answered for both would make either arm's retirement the other's to
        // argue with; Harmony runs both prefixes and either returning false
        // skips the original, which is the semantics both want.
        var spark = typeof(SparkGauge).Assembly
            .GetType("KleeMod.Vfx.NPowerContainer_Add_KleeSparkGauge_Patch")!;
        var furina = typeof(FurinaBoardBadges).Assembly
            .GetType("KleeMod.Vfx.NPowerContainer_Add_FurinaBoardBadges_Patch")!;

        Assert.NotEqual(spark, furina);
        Assert.Equal(
            spark.GetCustomAttribute<HarmonyPatch>()!.info.methodName,
            furina.GetCustomAttribute<HarmonyPatch>()!.info.methodName);
    }

    [Fact]
    public void The_file_is_compiled_only_under_the_prototype_arm()
    {
        Assert.Contains("<Compile Remove=\"Vfx/Prototype/**/*.cs\" />",
                        Source("KleeCode.csproj"));
        Assert.NotNull(Source("Vfx/Prototype/FurinaBoardBadges.cs"));
        Assert.Equal("KleeMod.Vfx", typeof(FurinaBoardBadges).Namespace);
    }

    // --- source access ----------------------------------------------------

    private static string Source(string relativePath) =>
        Read(System.IO.Path.Combine("klee-mod", "KleeCode",
            relativePath.Replace('/', System.IO.Path.DirectorySeparatorChar)));

    private static string Read(string relative)
    {
        var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = System.IO.Path.Combine(dir.FullName, relative);
            if (System.IO.File.Exists(candidate))
            {
                return System.IO.File.ReadAllText(candidate);
            }

            dir = dir.Parent;
        }

        throw new System.IO.FileNotFoundException(relative);
    }
}
