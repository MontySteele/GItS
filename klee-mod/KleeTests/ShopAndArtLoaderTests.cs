using System;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Nodes.Screens.Shops;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-274` and `EB-275`: two per-visit log faults, one in the shop and one on
/// every card draw. Both are SHIPPED-side (neither is behind an arm flag) and
/// both are pinned here rather than beside a prototype arm for that reason.
///
/// WHAT IS REACHABLE. Both fixes end in a Godot native call -- `Node.GetClass`
/// on one side, `Image`/`ImageTexture` on the other -- and neither can be made
/// in this host (README, "The headless boundary"). So each fix was written with
/// its DECISION separated from its native call:
/// `MerchantSpineBinding.BindsSpineClass` takes a class NAME, and `RosterArt` decides between a file and a blank in a
/// method whose call graph is readable. The pins below are those decisions plus
/// a structural read of the wiring, and they say which is which.
/// </summary>
public class ShopAndArtLoaderTests
{
    private static Type Type(string name) =>
        typeof(global::KleeMod.Powers.FurinaResources).Assembly
            .GetTypes().FirstOrDefault(t => t.Name == name)
        ?? throw new InvalidOperationException($"no type named {name}");

    // ---- EB-274: entering a shop throws on a non-Spine portrait ----------

    private static bool BindsSpine(string? childClass) =>
        (bool)Il.Method("MerchantSpineBinding", "BindsSpineClass")
                .Invoke(null, new object?[] { childClass })!;

    [Fact]
    public void Only_a_real_spine_child_may_be_bound()
    {
        // The game's own comparison, which is `MegaSpineBinding`'s validator:
        // `BoundObject.GetClass() != SpineClassName` throws. Our merchant
        // portraits are `Sprite2D` -- BaseLib's scene conversion builds the
        // NMerchantCharacter tree around a bare texture node -- which is the
        // exact string the exception carried:
        //   "Expected BoundObject to be a SpineSprite, but it is a Sprite2D!"
        Assert.True(BindsSpine("SpineSprite"));
        Assert.False(BindsSpine("Sprite2D"));
        Assert.False(BindsSpine("Node2D"));
        // A merchant with no children at all: `GetChild(0)` is itself an error
        // and the game's two methods index it unchecked, so "nothing there" is
        // refused for the same reason a Sprite2D is.
        Assert.False(BindsSpine(null));
    }

    [Fact]
    public void The_spine_class_name_is_the_one_the_game_validates_against()
    {
        var field = Type("MerchantSpineBinding")
            .GetField("SpineClass", HeadlessGame.All)!;
        Assert.Equal("SpineSprite", (string)field.GetRawConstantValue()!);
    }

    [Theory]
    [InlineData("NMerchantCharacter_Ready_SpineGuard_Patch", "_Ready")]
    [InlineData("NMerchantCharacter_PlayAnimation_SpineGuard_Patch",
                "PlayAnimation")]
    public void Both_doors_into_the_binding_are_guarded(
        string patchType, string method)
    {
        // TWO methods build the binding, not one: `_Ready` starts the idle and
        // the public `PlayAnimation` sets it. Guarding only `_Ready` would move
        // the throw from shop entry to whenever anything asks the merchant to
        // emote, which is the same defect later in the session.
        var patch = Type(patchType);
        var attr = patch.GetCustomAttributes(typeof(HarmonyPatch), false)
                        .Cast<HarmonyPatch>().ToList();
        Assert.NotEmpty(attr);
        Assert.Equal(typeof(NMerchantCharacter), attr[0].info.declaringType);
        Assert.Equal(method, attr[0].info.methodName);

        // Harmony's own resolution, so a rename in the game assembly is a red
        // test here rather than a patch that silently arms nothing (F2, the
        // per-type bootstrap's whole argument).
        Assert.NotNull(AccessTools.Method(typeof(NMerchantCharacter), method));

        // A PREFIX that can refuse: only a `bool`-returning prefix skips the
        // original, and skipping is the fix.
        var prefix = patch.GetMethod("Prefix", HeadlessGame.All)!;
        Assert.Equal(typeof(bool), prefix.ReturnType);
        Assert.NotEmpty(prefix.GetCustomAttributes(
            typeof(HarmonyPrefix), false));
    }

    [Fact]
    public void The_guard_reads_no_arm_flag()
    {
        // The row's acceptance is "a shop entered as Kokomi AND as Klee logs no
        // exception", and the log carried the line for both -- so a fix scoped
        // to one arm would close half the row. Nothing in the file may consult
        // `KokomiOverhaul` / `KleeOverhaul` / `CompanionOverhaul`.
        foreach (var name in new[]
                 {
                     "MerchantSpineBinding",
                     "NMerchantCharacter_Ready_SpineGuard_Patch",
                     "NMerchantCharacter_PlayAnimation_SpineGuard_Patch",
                 })
        {
            foreach (var method in Type(name)
                         .GetMethods(HeadlessGame.All)
                         .Where(m => m.DeclaringType == Type(name)))
            {
                var calls = Il.Calls(method);
                Assert.DoesNotContain(calls, c => c.Contains("Overhaul"));
            }
        }
    }

    [Fact]
    public void The_skip_is_said_once_per_process_and_not_once_per_shop()
    {
        // The complaint was VOLUME -- a stack trace per shop that "reads like a
        // fault in the console". One warning per shop would be the same defect
        // in a quieter font.
        var type = Type("MerchantSpineBinding");
        var reset = type.GetMethod("ResetAll", HeadlessGame.All)!;
        var note = type.GetMethod("NoteOnce", HeadlessGame.All)!;
        var said = (System.Collections.Generic.HashSet<string>)
            type.GetField("Said", HeadlessGame.All)!.GetValue(null)!;

        reset.Invoke(null, null);
        Assert.Empty(said);
        note.Invoke(null, new object[] { "the merchant's idle animation" });
        note.Invoke(null, new object[] { "the merchant's idle animation" });
        Assert.Single(said);
        note.Invoke(null, new object[] { "a merchant animation request" });
        Assert.Equal(2, said.Count);
        reset.Invoke(null, null);
    }

    // ---- EB-275: a missing card image logs on every frame ----------------

    [Fact]
    public void A_row_with_no_staged_image_resolves_to_the_blank()
    {
        // STRUCTURAL, and the structure IS the fix. BaseLib's portrait patch is
        // `if (CustomPortrait != null) __result = CustomPortrait;` -- so a null
        // sent the game to its OWN atlas for a modded id it cannot hold, and
        // `AtlasResourceLoader` said "Missing sprite '<char>/kleemod-proto_..'"
        // on EVERY DRAW. Returning a texture is the only thing that stops that,
        // so `CardPortrait` must reach `Blank`.
        var portrait = Il.Method("RosterArt", "CardPortrait");
        Assert.Contains(Il.Calls(portrait), c => c.Contains("RosterArt.Blank"));
    }

    [Fact]
    public void The_blank_is_built_once_and_held()
    {
        // A portrait getter is hit repeatedly by the UI; rebuilding the blank
        // per access would trade a per-frame log line for a per-frame
        // allocation, which is the same defect wearing the other hat.
        var blank = Il.Method("RosterArt", "Blank");
        var calls = Il.Calls(blank);
        Assert.Contains(calls, c => c.Contains("Image.CreateEmpty"));
        Assert.Contains(calls, c => c.Contains("ImageTexture.CreateFromImage"));
        Assert.NotNull(Type("RosterArt").GetField("_blank", HeadlessGame.All));
    }

    [Fact]
    public void The_blank_stands_in_at_the_authored_portrait_size()
    {
        // `tools/art_lint.py` bills every portrait against 500x380 and
        // `tools/art_coverage.py` reads the same shape off disk, so the blank
        // occupies the space a real portrait would and the card frame cannot
        // move under it.
        var type = Type("RosterArt");
        Assert.Equal(500, (int)type.GetField("PortraitWidth", HeadlessGame.All)!
                                   .GetRawConstantValue()!);
        Assert.Equal(380, (int)type.GetField("PortraitHeight", HeadlessGame.All)!
                                   .GetRawConstantValue()!);
    }

    [Fact]
    public void A_failure_to_build_the_blank_degrades_rather_than_throws()
    {
        // A portrait getter runs inside card construction. With no engine
        // behind the native calls the honest answer is the pre-EB-275 one --
        // null, and the atlas miss back -- because a card that throws while
        // being built is a lost run rather than a lost picture.
        var blank = Il.Method("RosterArt", "Blank");
        var handlers = blank.GetMethodBody()!.ExceptionHandlingClauses;
        Assert.NotEmpty(handlers);
    }
}
