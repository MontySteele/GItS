using System;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Nodes.Combat;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-621`: the Spark bank as a RESOURCE BADGE IN THE ENERGY AREA, drawn the
/// way the base game draws the Regent's Stars, under the Klee overhaul arm and
/// on the local seat only.
///
/// WHAT IS REAL HERE. Every DECISION the change takes runs for real: who gets
/// the badge, what number it draws, and that with the arm off nothing at all
/// happens.
///
/// WHAT IS STRUCTURAL, and labelled. The element itself is a Godot node tree,
/// and Godot nodes are process death in this host (KleeTests README, the
/// headless boundary) -- so the DRAWING is pinned as source text and as call
/// sets: that the geometry is read off the live `%StarCounter` rather than
/// guessed, that the energy orb takes the base game's own displacement, that
/// the badge rides the funnel that already exists, and that the teardown never
/// has to name a seat. Whether the badge LANDS where the star counter lands is
/// a frame on the next `+proto` deploy and nothing here claims it.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class SparkCounterPinTests
{
    private const BindingFlags All = HeadlessGame.All;

    /// <summary>Run <paramref name="body"/> with the arm forced one way, and
    /// put it back -- <see cref="SparkGaugePinTests"/>' helper, and the reason
    /// this file shares its collection.</summary>
    private static void WithArm(bool enabled, Action body)
    {
        var was = KleeOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = enabled;
            body();
        }
        finally
        {
            KleeOverhaul.Enabled = was;
        }
    }

    // --- the class exists, and only under the arm -------------------------

    [Fact]
    public void The_badge_is_compiled_only_under_the_prototype_arm()
    {
        // THE QUARANTINE IS THE FILE'S LOCATION, not an `#if` inside it:
        // `KleeCode.csproj` `Compile Remove`s `Vfx/Prototype/**/*.cs` without
        // `-p:PrototypeCards=true`. So the acceptance condition for "a release
        // build gains nothing" is that the type lives there, and that is what
        // this asserts -- this test file is itself removed off the arm, so its
        // mere compilation is the other half.
        var csproj = Source("KleeCode.csproj");
        Assert.Contains("<Compile Remove=\"Vfx/Prototype/**/*.cs\" />", csproj);

        Assert.NotNull(Source("Vfx/Prototype/SparkCounter.cs"));
        Assert.Equal("KleeMod.Vfx", typeof(SparkCounter).Namespace);
    }

    // --- who gets it ------------------------------------------------------

    [Fact]
    public void Klee_gets_the_badge_under_the_arm_and_nobody_else_ever_does()
    {
        var klee = Seat.Klee();
        var furina = Seat.Furina();
        var kokomi = Seat.Kokomi();

        WithArm(true, () =>
        {
            Assert.True(SparkCounter.AppliesTo(klee.Creature));
            // Both are at the same table in co-op and neither has a Spark bank.
            Assert.False(SparkCounter.AppliesTo(furina.Creature));
            Assert.False(SparkCounter.AppliesTo(kokomi.Creature));
        });

        // THE ACCEPTANCE CONDITION. Off the arm there is no badge at all, so
        // the shipped energy area is exactly the shipped energy area.
        WithArm(false, () =>
        {
            Assert.False(SparkCounter.AppliesTo(klee.Creature));
            Assert.False(SparkCounter.AppliesTo(furina.Creature));
            Assert.False(SparkCounter.AppliesTo(kokomi.Creature));
        });

        // And a creature it is never asked about answers false rather than
        // throwing: `Refresh` is called from a power's mutation funnel.
        Assert.False(SparkCounter.AppliesTo(null));
    }

    [Fact]
    public void The_scope_is_the_gauge_s_own_predicate_and_not_a_second_copy()
    {
        // `EB-281` settled who owns a Spark display and spelled the co-op
        // reason at length. Two predicates would be two things to keep true.
        var calls = Il.Calls(typeof(SparkCounter)
            .GetMethod(nameof(SparkCounter.AppliesTo), All)!);
        Assert.Contains(calls,
            c => c.EndsWith("SparkGauge.AppliesTo", StringComparison.Ordinal));
    }

    // --- what it draws ----------------------------------------------------

    [Fact]
    public void The_badge_draws_the_bank_and_zero_before_the_first_spark()
    {
        // ZERO IS DRAWN, NOT HIDDEN -- `ShouldAlwaysShowStarCounter`'s posture,
        // and the reason it exists: a resource the kit is priced against has to
        // be on screen from turn one.
        var empty = Seat.Klee();
        Assert.Equal(0, SparkCounter.Read(empty.Creature));

        var banked = Seat.Klee().WithPower<SparkPower>(4);
        Assert.Equal(4, SparkCounter.Read(banked.Creature));

        banked.SetPowerAmount<SparkPower>(1);
        Assert.Equal(1, SparkCounter.Read(banked.Creature));

        // THE ACCEPTANCE CONDITION FROM THE ROW: "the count matches the power's
        // stack." It is the same read the rules take, not a display copy.
        Assert.Equal(SparkPower.SparksAtPlay(banked.Creature),
                     SparkCounter.Read(banked.Creature));
        Assert.Equal(SparkGauge.Read(banked.Creature),
                     SparkCounter.Read(banked.Creature));
    }

    // --- the feed ---------------------------------------------------------

    [Fact]
    public void The_badge_rides_the_funnel_the_bank_already_has()
    {
        // `SparkPower`'s three mutation funnels call `SparkGauge.Refresh`; that
        // is where this display hangs, so the badge and the `spark` meter
        // ledger cannot come from different reads. (The overhead gauge it used
        // to redraw beside this one is gone: playtest 2026-09-24.)
        var calls = Il.Calls(typeof(SparkGauge)
            .GetMethod(nameof(SparkGauge.Refresh), All)!);
        Assert.Contains(calls,
            c => c.EndsWith("SparkCounter.Refresh", StringComparison.Ordinal));
        Assert.DoesNotContain(calls,
            c => c.EndsWith("GaugeBridge.Refresh", StringComparison.Ordinal));

        // And `SparkPower` still calls that one funnel rather than reaching the
        // badge directly, which is what keeps "one funnel" true.
        var sync = Il.Calls(typeof(SparkPower).GetMethod("SyncGauge", All)!);
        Assert.Contains(sync,
            c => c.EndsWith("SparkGauge.Refresh", StringComparison.Ordinal));

        // NO POLLING ANYWHERE. A per-frame `_Process` would be a second
        // cadence, and two cadences is how a display and a bank drift.
        Assert.DoesNotContain("void _Process",
                              Source("Vfx/Prototype/SparkCounter.cs"));
    }

    [Fact]
    public void It_is_built_at_the_one_combat_lifecycle_entry_point()
    {
        // The same `NCombatUi.Activate` postfix the gauges, the Kurage card and
        // the Plan strip use -- one door, so nothing can disagree about when a
        // room is live.
        var postfix = typeof(GaugeBridge).Assembly
            .GetType("KleeMod.Vfx.NCombatUi_Activate_GaugeSetup")!
            .GetMethod("Postfix", All)!;
        Assert.Contains(Il.Calls(postfix),
            c => c.EndsWith("SparkCounter.Setup", StringComparison.Ordinal));
    }

    // --- the geometry, as geometry ----------------------------------------
    //
    // `EB-815`. THESE TWO TESTS REPLACE TWO SOURCE-TEXT PINS, and the swap is
    // the lesson rather than a tidy-up. The old pair asserted that the file
    // CONTAINED the four `root.Anchor{edge} = star.Anchor{edge};` lines and the
    // `EnergyCounterContainer?.SetPosition(...)` call. Both lines were the
    // defect -- `NCombatUi.Activate` reparents `%StarCounter` INTO the energy
    // orb before this mod's postfix runs, so copying its box put the badge on
    // the orb, and the displacement then moved badge and orb together because
    // the badge was inside the orb's own subtree. The suite was green the whole
    // time [USER] was looking at the overlap, because a test that asserts a
    // line of code EXISTS can never fail on where a box LANDS.
    //
    // So the placement is now a pure function over rects and the pins are
    // arithmetic. `Place` takes no nodes, which is what lets the headless host
    // hold it at all (KleeTests README, the headless boundary).

    /// <summary>The badge's own square, as `SideOf` resolves it when the star
    /// counter has not been laid out. Any side would do; this is the shipped
    /// one.</summary>
    private const float Side = 72f;

    /// <summary>The game's design resolution -- the space the panel's offsets
    /// are already in (`KurageMemoryCard`, the same constant).</summary>
    private static readonly Godot.Vector2 Design = new(1920f, 1080f);

    private static Godot.Rect2 Place(
        Godot.Rect2 energy, float side, Godot.Vector2 viewport) =>
        (Godot.Rect2)typeof(SparkCounter)
            .GetMethod(nameof(Place), All)!
            .Invoke(null, new object[] { energy, side, viewport })!;

    [Fact]
    public void The_badge_never_lands_on_the_energy_panel()
    {
        // The two rects the energy panel actually takes: its shipped corner,
        // and the displaced corner the base game gives it for a character that
        // always shows a star counter (`NCombatUi.Activate`, v0.111.0,
        // `new Vector2(100f, 806f)`). The badge must clear BOTH -- the second
        // because the base game may still displace the panel around us.
        var offset = (Godot.Vector2)typeof(SparkCounter)
            .GetField("EnergyCounterOffset", All)!
            .GetValue(null)!;
        Assert.Equal(100f, offset.X);
        Assert.Equal(806f, offset.Y);

        var panels = new[]
        {
            new Godot.Rect2(new Godot.Vector2(60f, 860f), new(140f, 140f)),
            new Godot.Rect2(offset, new Godot.Vector2(140f, 140f)),
        };

        foreach (var panel in panels)
        {
            var badge = Place(panel, Side, Design);

            // THE WHOLE ACCEPTANCE CONDITION, and the thing [USER] saw fail:
            // the flower must not sit on the hexagon.
            Assert.False(badge.Intersects(panel),
                         $"badge {badge} intersects the energy panel {panel}");

            // And it must be on screen to be read at all.
            Assert.True(new Godot.Rect2(Godot.Vector2.Zero, Design)
                            .Encloses(badge),
                        $"badge {badge} is off a {Design} viewport");

            // ABOVE, left edges aligned, and exactly the declared margin clear
            // -- not merely "somewhere that happens not to touch".
            var margin = (float)typeof(SparkCounter)
                .GetField("PanelMargin", All)!.GetValue(null)!;
            Assert.Equal(12f, margin);
            Assert.Equal(panel.Position.X, badge.Position.X);
            Assert.Equal(panel.Position.Y - margin, badge.End.Y);
        }
    }

    [Fact]
    public void The_placement_holds_at_every_viewport_and_panel_position()
    {
        // THE POINT OF THE ROW. The old overlap was scale-INDEPENDENT -- a
        // fixed delta inside one shared subtree -- so a single-viewport pin
        // would have proved nothing about it. This sweeps the panel around the
        // frame and the frame around its own sizes, and asserts the same two
        // properties every time: clear of the panel, inside the viewport.
        var viewports = new[]
        {
            Design,
            new Godot.Vector2(1280f, 720f),      // the small window
            new Godot.Vector2(2560f, 1440f),     // a large one
            new Godot.Vector2(1920f, 800f),      // ultrawide-ish, short
        };

        var corners = new[]
        {
            new Godot.Vector2(0f, 0f),           // flush top-left: no room ABOVE
            new Godot.Vector2(100f, 806f),       // the game's own corner
            new Godot.Vector2(60f, 300f),
            new Godot.Vector2(600f, 40f),        // near the top edge
        };

        foreach (var viewport in viewports)
        {
            foreach (var corner in corners)
            {
                var panel = new Godot.Rect2(corner, new Godot.Vector2(140f, 140f));
                var badge = Place(panel, Side, viewport);

                Assert.False(badge.Intersects(panel),
                             $"badge {badge} intersects panel {panel} "
                             + $"at viewport {viewport}");
                Assert.True(new Godot.Rect2(Godot.Vector2.Zero, viewport)
                                .Encloses(badge),
                            $"badge {badge} escapes viewport {viewport} "
                            + $"with panel {panel}");
            }
        }
    }

    [Fact]
    public void The_badge_is_a_sibling_of_the_energy_panel_and_not_its_child()
    {
        var source = Source("Vfx/Prototype/SparkCounter.cs").Replace("\r\n", "\n");

        // THE ROOT CAUSE, pinned as the one thing about the tree that source
        // text CAN hold: the parent is the energy panel's parent. Parenting
        // into `star.GetParent()` is what put the badge inside the orb, because
        // `Activate` has already reparented the star counter into it.
        Assert.Contains("var panel = ui.EnergyCounterContainer;", source);
        Assert.Contains("var parent = panel?.GetParent() ?? (Node)ui;", source);
        Assert.DoesNotContain("star?.GetParent()", source);

        // The displacement is GONE rather than repaired: with the badge out of
        // the orb's subtree it would be a real eviction of the shipped orb that
        // nothing asked for. The CALL is what must be absent -- the docstring
        // still quotes the base game's own line, and should, because that line
        // is the fact the rest of the file is reasoning about.
        Assert.DoesNotContain("ui.EnergyCounterContainer?.SetPosition", source);
        Assert.DoesNotContain("SetPosition(EnergyCounterOffset", source);

        // `%StarCounter` is still read -- for its SIZE, which the reparent does
        // not make a lie -- and its anchors are never copied again.
        Assert.Contains("GetNodeOrNull<Control>(\"%StarCounter\")", source);
        foreach (var edge in new[] { "Left", "Top", "Right", "Bottom" })
        {
            Assert.DoesNotContain($"root.Anchor{edge} = star.Anchor{edge};",
                                  source);
            Assert.DoesNotContain($"root.Offset{edge} = star.Offset{edge};",
                                  source);
        }

        // And the badge carries the PANEL's anchor pair, which is what makes a
        // resize move the two by one vector with no `_Process`.
        Assert.Contains("root.AnchorLeft = panel.AnchorLeft;", source);
        Assert.Contains("root.AnchorTop = panel.AnchorTop;", source);
    }

    [Fact]
    public void The_glyph_is_the_one_the_resource_wears_everywhere_else()
    {
        var source = Source("Vfx/Prototype/SparkCounter.cs").Replace("\r\n", "\n");

        // Klee's own Spark icon -- the one the status-strip badge wore and the
        // one the meter cost badge paints on a priced card. Same resource, same glyph, wherever it appears.
        Assert.Contains("KleePck.Path(SparkGauge.GlyphPath)", source);
        Assert.Equal("klee/powers/spark.png", SparkGauge.GlyphPath);

        // `EB-222`: no texture is held across a scene. The engine frees a
        // room's assets with the room, and a cached `Texture2D` handed to a
        // `TextureRect` the next combat is what stuck a room and ended a run.
        Assert.Contains("ResourceLoader.Load<Texture2D>(path)", source);
        Assert.DoesNotContain("static Texture2D", source);
    }

    // --- the teardown -----------------------------------------------------

    [Fact]
    public void The_teardown_is_on_the_game_s_hook_and_names_no_seat()
    {
        var patch = typeof(GaugeBridge).Assembly
            .GetType("KleeMod.Vfx.NCombatUi_Deactivate_KleeSparkCounter_Patch")!;

        var attribute = patch.GetCustomAttribute<HarmonyPatch>()!;
        Assert.Equal(typeof(NCombatUi), attribute.info.declaringType);
        Assert.Equal(nameof(NCombatUi.Deactivate), attribute.info.methodName);

        // BY NODE, NOT BY SEAT, and that is the point rather than a shortcut.
        // `NCombatUi.Deactivate` runs while the NEXT room is being built and
        // the combat still held may have no seats in it -- `EB-225`, the shape
        // that ended two blind sessions when a teardown asked for one. So the
        // postfix reaches `Hide(NCombatUi)`, which frees a child THIS mod
        // named and touches no run state at all.
        var postfix = patch.GetMethod("Postfix", All)!;
        Assert.Contains(Il.Calls(postfix),
            c => c.EndsWith("SparkCounter.Hide", StringComparison.Ordinal));

        var hide = typeof(SparkCounter).GetMethod("Hide", All)!;
        Assert.Equal(typeof(NCombatUi),
                     hide.GetParameters().Single().ParameterType);
        Assert.Contains(Il.Calls(hide),
            c => c.EndsWith("Node.FindChild", StringComparison.Ordinal));

        // And the exemption is DECLARED rather than inferred:
        // `tools/lint_prototype_patch_scope.py` prints every marker on every
        // run, and a marker with no reason is itself a finding.
        var source = Source("Vfx/Prototype/SparkCounter.cs").Replace("\r\n", "\n");
        var marker = source.Split('\n')
            .First(line => line.Contains("lint: no-seat:"));
        Assert.True(marker.Trim().Length > "// lint: no-seat:".Length + 10,
                    "the no-seat exemption must carry a reason");
    }

    // --- source access ----------------------------------------------------

    /// <summary>A source file under `klee-mod/KleeCode`.
    /// <see cref="Round21Tests"/>' helper, verbatim.</summary>
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
