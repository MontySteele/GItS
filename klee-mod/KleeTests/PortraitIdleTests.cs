using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-38`: the rest-site and merchant gentle idle for the spine-less
/// characters (Klee, Furina, Kokomi).
///
/// WHAT IS REACHABLE. The idle ENDS in Godot -- `Node.GetClass`, `AddChild`,
/// `Reparent`, `CreateTween` -- and none of that can be made in this host
/// (README, "The headless boundary"): a test that touches a scene node takes
/// the whole run with it. So the animation was written with its DATA and its
/// DECISION separated from its native calls. `StaticPortraitIdle.Plan()` is
/// the whole breath as a list and `Attach` plays exactly that list;
/// `WantsIdle` takes the two answers rather than the node. The pins below are
/// those two plus a structural read of the wiring, and each says which it is.
///
/// LIVE ACCEPTANCE, stated so it is not mistaken for covered: that the pivot
/// actually appears in the running tree, that the sprite still draws in its
/// old place under it, and that the motion reads as breathing rather than as
/// a wobble, are all eyes-on at the next deploy. Nothing here can see a frame.
/// </summary>
public class PortraitIdleTests
{
    private static Type Type(string name) =>
        typeof(global::KleeMod.Powers.FurinaResources).Assembly
            .GetTypes().FirstOrDefault(t => t.Name == name)
        ?? throw new InvalidOperationException($"no type named {name}");

    private static T Const<T>(string field) =>
        (T)Type("StaticPortraitIdle").GetField(field, HeadlessGame.All)!
            .GetRawConstantValue()!;

    // ---- the animation, as data ------------------------------------------

    /// <summary>
    /// The plan the shipped `Attach` iterates, read back step by step. This is
    /// the ONE pin that says what the idle actually does, and it is a real
    /// read of the shipped list rather than a restatement of the numbers.
    /// </summary>
    private static List<(string Property, float To, float Seconds, bool Parallel)> Plan()
    {
        var rows = new List<(string, float, float, bool)>();
        var plan = (IEnumerable)Il.Method("StaticPortraitIdle", "Plan")
            .Invoke(null, null)!;
        foreach (var step in plan)
        {
            var t = step.GetType();
            rows.Add((
                (string)t.GetProperty("Property", HeadlessGame.All)!.GetValue(step)!,
                (float)t.GetProperty("To", HeadlessGame.All)!.GetValue(step)!,
                (float)t.GetProperty("Seconds", HeadlessGame.All)!.GetValue(step)!,
                (bool)t.GetProperty("Parallel", HeadlessGame.All)!.GetValue(step)!));
        }

        return rows;
    }

    [Fact]
    public void The_breath_is_one_swell_and_one_settle()
    {
        // Two steps of half a breath each, scale and position moving together
        // inside each step. `Parallel` is Godot's `Tween.Parallel()`, which
        // affects the NEXT tweener only -- so a true row joins the row above
        // it and a false row opens a new step, which is why the flags
        // alternate.
        Assert.Equal(
            new List<(string, float, float, bool)>
            {
                ("scale:y",    1.015f, 1.2f, false),
                ("position:y", -2f,    1.2f, true),
                ("scale:y",    1f,     1.2f, false),
                ("position:y", 0f,     1.2f, true),
            },
            Plan());
    }

    [Fact]
    public void The_two_steps_are_the_two_halves_of_the_period()
    {
        // The period is the number the row and the eyes-on are stated in
        // ("~2.4s"), and the steps are what ships; a drift between them would
        // make the written intent and the animation two different things.
        Assert.Equal(2.4f, Const<float>("PeriodSeconds"));
        Assert.Equal(1.2f, Const<float>("HalfPeriodSeconds"));
        Assert.Equal(
            Const<float>("PeriodSeconds"),
            Const<float>("HalfPeriodSeconds") * 2f);
        Assert.All(Plan(), step =>
            Assert.Equal(Const<float>("HalfPeriodSeconds"), step.Seconds));
    }

    [Fact]
    public void The_move_is_small_and_vertical_only()
    {
        // 1.5% of scale and 2px of lift. The horizontal axis is untouched on
        // purpose: a matched x/y pulse reads as a zoom, not as a breath, and
        // it would also fight the rest site's FlipX convention for a
        // right-hand seat.
        Assert.Equal(1.015f, Const<float>("ScaleYPeak"));
        Assert.Equal(2f, Const<float>("RiseYPixels"));
        Assert.All(Plan(), step =>
            Assert.True(step.Property is "scale:y" or "position:y",
                $"{step.Property} is not one of the two vertical channels"));
    }

    // ---- who gets one ----------------------------------------------------

    [Theory]
    // A real Spine rig: the game starts `relaxed_loop` / the act loop on it
    // itself, so the whole base cast answers here and gets nothing from us.
    [InlineData(true, true, false)]
    [InlineData(true, false, false)]
    // Spine-less with a texture to move: Klee, Furina and Kokomi.
    [InlineData(false, true, true)]
    // Spine-less with no Sprite2D at all: a tree shape we did not build,
    // left alone rather than guessed at.
    [InlineData(false, false, false)]
    public void Only_a_spine_less_portrait_with_a_texture_gets_an_idle(
        bool hasSpineNode, bool hasSprite, bool expected)
    {
        var wants = (bool)Il.Method("StaticPortraitIdle", "WantsIdle")
            .Invoke(null, new object?[] { hasSpineNode, hasSprite })!;
        Assert.Equal(expected, wants);
    }

    [Fact]
    public void The_spine_test_is_the_same_string_the_game_validates_against()
    {
        // `MerchantSpineBinding.SpineClass` is `MegaSprite.SpineClassName`,
        // which is what `MegaSpineBinding` throws on and what
        // `NRestSiteCharacter.GetChildSpineNodes` filters on. The idle asks
        // the same question of the same tree, and the constant is shared in
        // source -- a `const string` inlines, so what this reads back is the
        // literal the shipped `Attach` compares.
        var shared = (string)Type("MerchantSpineBinding")
            .GetField("SpineClass", HeadlessGame.All)!.GetRawConstantValue()!;
        Assert.Equal("SpineSprite", shared);
        Assert.Contains(shared,
            Il.Strings(Il.Method("StaticPortraitIdle", "Attach")));
    }

    // ---- the wiring ------------------------------------------------------

    [Theory]
    [InlineData("NRestSiteCharacter_Ready_GentleIdle_Patch",
                "MegaCrit.Sts2.Core.Nodes.RestSite.NRestSiteCharacter")]
    [InlineData("NMerchantCharacter_Ready_GentleIdle_Patch",
                "MegaCrit.Sts2.Core.Nodes.Screens.Shops.NMerchantCharacter")]
    public void Both_out_of_combat_surfaces_are_hooked(
        string patchType, string target)
    {
        // BOTH, not one: the row's acceptance names the rest site and the
        // merchant, and they are different classes reached by different
        // factories with no shared base but Node2D.
        var patch = Type(patchType);
        var attr = patch.GetCustomAttributes(typeof(HarmonyPatch), false)
                        .Cast<HarmonyPatch>().ToList();
        Assert.NotEmpty(attr);
        Assert.Equal(target, attr[0].info.declaringType!.FullName);
        Assert.Equal("_Ready", attr[0].info.methodName);

        // Harmony's own resolution, so a rename in the game assembly is a red
        // test here rather than a patch that silently arms nothing (F2, the
        // per-type bootstrap's whole argument).
        Assert.NotNull(AccessTools.Method(attr[0].info.declaringType, "_Ready"));

        // A POSTFIX. `_Ready` is where the base cast's own idle is started and
        // the first moment the whole factory-built tree exists; and on the
        // merchant it has to be a postfix for a second reason -- `EB-274`'s
        // PREFIX on this same method returns false for our portraits, and
        // Harmony skips the original, never the postfixes.
        var postfix = patch.GetMethod("Postfix", HeadlessGame.All)!;
        Assert.Equal(typeof(void), postfix.ReturnType);
        Assert.NotEmpty(postfix.GetCustomAttributes(
            typeof(HarmonyPostfix), false));

        // The class-level attribute is what `KleePatchBootstrap.PatchClasses`
        // collects; patch methods without one are applied by nobody, silently.
        Assert.Contains(patch.GetCustomAttributes(inherit: true),
                        a => a is HarmonyPatch);
    }

    [Fact]
    public void The_idle_is_played_from_the_pinned_plan_on_a_tween()
    {
        // STRUCTURAL. `Attach` cannot be run here, but its call set can be
        // read, and two facts about it are the design:
        //
        //  (1) it calls `Plan` -- so the list pinned above is the list that
        //      ships, not a second copy of the numbers that can drift;
        //  (2) it drives that list through a Tween. A `_Process` loop is
        //      banned for a two-node cosmetic: the engine already owns the
        //      clock and a bound Tween dies with the node it animates.
        var calls = Il.Calls(Il.Method("StaticPortraitIdle", "Attach"));
        Assert.Contains("StaticPortraitIdle.Plan", calls);
        Assert.Contains("Node.CreateTween", calls);
        Assert.Contains("Tween.TweenProperty", calls);
        Assert.Contains("Tween.SetLoops", calls);
        Assert.Contains("Tween.SetTrans", calls);
        Assert.Contains("Tween.SetEase", calls);
        Assert.Contains("Tween.Parallel", calls);

        // And nothing anywhere in the file is a per-frame driver.
        foreach (var name in new[]
                 {
                     "StaticPortraitIdle",
                     "NRestSiteCharacter_Ready_GentleIdle_Patch",
                     "NMerchantCharacter_Ready_GentleIdle_Patch",
                 })
        {
            Assert.DoesNotContain(
                Type(name).GetMethods(HeadlessGame.All),
                m => m.DeclaringType == Type(name)
                     && (m.Name == "_Process" || m.Name == "_PhysicsProcess"));
        }
    }

    [Fact]
    public void The_animated_node_is_one_we_add_above_the_texture()
    {
        // STRUCTURAL, and the structure IS the rule. The Sprite2D is the
        // GAME's node: BaseLib's factory made it, `NMerchantCharacter` indexes
        // it as `GetChild(0)` and the rest site's `FlipX` walks its own
        // children for one. So the idle inserts a pivot and reparents the
        // sprite under it...
        var calls = Il.Calls(Il.Method("StaticPortraitIdle", "Attach"));
        Assert.Contains("Node.AddChild", calls);
        Assert.Contains("Node.Reparent", calls);
        // ...at the index it drew at, or the portrait changes z-order.
        Assert.Contains("Node.GetIndex", calls);
        Assert.Contains("Node.MoveChild", calls);

        // ...and writes NO transform itself. Every position and scale in the
        // shipped animation is the Tween's, on the pivot. A `set_Position` or
        // `set_Scale` here would mean the mod is moving a node the game owns
        // and reads back.
        Assert.DoesNotContain(calls, c => c.EndsWith(".set_Position",
            StringComparison.Ordinal));
        Assert.DoesNotContain(calls, c => c.EndsWith(".set_Scale",
            StringComparison.Ordinal));

        // The combat layer is a different system and stays untouched: this
        // file names no creature node at all.
        Assert.DoesNotContain(calls, c => c.Contains("NCreature"));
    }

    [Fact]
    public void The_idle_reads_no_arm_flag()
    {
        // SHIPPED, not quarantined, on `MerchantSpineBindingPatch.cs`'s
        // precedent: the gap belongs to every spine-less portrait and all
        // three of ours are, so an arm-scoped idle would close a third of the
        // row and leave two characters a photograph.
        foreach (var name in new[]
                 {
                     "StaticPortraitIdle",
                     "NRestSiteCharacter_Ready_GentleIdle_Patch",
                     "NMerchantCharacter_Ready_GentleIdle_Patch",
                 })
        {
            foreach (var method in Type(name)
                         .GetMethods(HeadlessGame.All)
                         .Where(m => m.DeclaringType == Type(name)))
            {
                Assert.DoesNotContain(Il.Calls(method),
                                      c => c.Contains("Overhaul"));
            }
        }
    }

    [Fact]
    public void The_arming_line_is_said_once_per_process()
    {
        // One line per rest site and one per shop would be log volume for no
        // information -- `EB-274`'s complaint about its own predecessor. The
        // only thing worth saying is that the idle armed at all, and it is
        // worth saying because the live acceptance is eyes-on and this is the
        // one thing a log can confirm.
        var type = Type("StaticPortraitIdle");
        var reset = type.GetMethod("ResetAll", HeadlessGame.All)!;
        var note = type.GetMethod("NoteOnce", HeadlessGame.All)!;
        var said = (HashSet<string>)
            type.GetField("Said", HeadlessGame.All)!.GetValue(null)!;

        reset.Invoke(null, null);
        Assert.Empty(said);
        note.Invoke(null, new object[] { "rest site" });
        note.Invoke(null, new object[] { "rest site" });
        Assert.Single(said);
        note.Invoke(null, new object[] { "merchant" });
        Assert.Equal(2, said.Count);
        reset.Invoke(null, null);
    }
}
