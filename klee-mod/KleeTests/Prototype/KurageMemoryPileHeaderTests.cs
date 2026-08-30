using System;
using System.Linq;
using System.Reflection;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-214` / R224 item 7 (`M55` re-scoped): the pile view says where Charge
/// comes from.
///
/// `M55`'s printed option put the sentence in the persistent Charge display's
/// LIST. That surface does not exist: `M61` option 3 cut the display to one
/// card, one ring, one number. R224 re-scoped the line to the head of the
/// click-through pile view -- the only text-bearing memory surface left -- and
/// ruled that "Stir" is not built.
///
/// WHAT IS REACHABLE HERE. The header is a Godot `Label` parented to a live
/// `NCardPileScreen`, and no test may touch a Godot object at all (README, the
/// headless boundary). So the pins are the two things that can be wrong
/// without a frame: THE SENTENCE, read off the constant the screen draws, and
/// THE SCOPE -- that the patch reaches a character test and the guarded seat
/// accessor, which is the `EB-225` rule and the shape that ended two blind
/// sessions when it was missing.
/// </summary>
public class KurageMemoryPileHeaderTests
{
    private static readonly Assembly Mod = typeof(KurageMemory).Assembly;

    /// <summary>The sentence, read off `KurageMemoryText` -- NOT off
    /// `KurageMemoryPileRing`, whose static constructor builds a Godot
    /// `StringName` and takes the whole test host down mid-run (README, the
    /// headless boundary). That is why the string has a type of its
    /// own.</summary>
    private static string Line()
        => (string)(Mod.GetType("KleeMod.Vfx.KurageMemoryText")
                    ?? throw new InvalidOperationException("no KurageMemoryText"))
            .GetField("ChargeSource",
                      BindingFlags.NonPublic | BindingFlags.Public
                      | BindingFlags.Static)!
            .GetValue(null)!;

    [Fact]
    public void The_head_of_the_pile_view_carries_R224s_sentence_verbatim()
    {
        // Verbatim, review/active/sitting-2026-08-30.md item 7. No trailing
        // stop, no "Stir", nothing about the queue: R224 ruled ONE sentence
        // and this is it.
        Assert.Equal("Gain 1 Charge when a card of yours Exhausts", Line());
    }

    [Fact]
    public void The_rate_in_the_sentence_is_the_funnels_own_constant()
    {
        // `lint_prose_constants` made this the shape rather than a typed "1",
        // and the pin is what makes the interpolation load-bearing: retune
        // ChargePerExhaust and the sentence follows, or this fails.
        Assert.StartsWith($"Gain {KokomiConstants.ChargePerExhaust} Charge",
                          Line(), StringComparison.Ordinal);
    }

    [Fact]
    public void The_drawn_text_is_the_field_and_not_a_second_copy()
    {
        var strings = Il.Strings(Il.Method("KurageMemoryPileRing", "Header"));

        // The sentence is assembled once, in the static initializer. The draw
        // site must therefore hold no copy of it at all -- if someone re-types
        // it here the two can drift, which is the whole failure R78 named for
        // the Muster keyword and the reason that keyword exists.
        Assert.DoesNotContain(strings, s => s.Contains("Charge when a card"));
    }

    [Fact]
    public void The_header_is_character_scoped_and_seat_guarded()
    {
        // `EB-225`'s two rules, asserted on the effective body the way the
        // lint reads it: the patch delegates to `Header`, `Header` asks
        // whether the seat is Kokomi's and resolves that seat through
        // `KurageMemoryCard.TryGetMe` -- never `LocalContext.GetMe`, which
        // THROWS on a combat that holds no local seat (d217b4f).
        var calls = Il.Calls(Il.Method("KurageMemoryPileRing", "Header"));

        Assert.Contains(calls, c => c.Contains("KokomiResources.IsKokomi"));
        Assert.Contains(calls, c => c.Contains("TryGetMe"));
        Assert.DoesNotContain(calls, c => c.Contains("LocalContext.GetMe"));
    }

    [Fact]
    public void The_patched_hook_is_a_method_the_screen_itself_declares()
    {
        // Harmony resolves `_Ready` by NAME at patch time, and a name that
        // lives only on a base class is a startup throw rather than a missing
        // label. The mod already patches `_ExitTree` on this type; this says
        // the new hook is declared in the same place, and it is what fires if
        // a game update moves it. Reflection over the type only: nothing here
        // constructs one (README, the headless boundary).
        var screen = Mod.GetReferencedAssemblies();
        var sts2 = System.Reflection.Assembly.Load(
            System.Array.Find(screen, a => a.Name == "sts2"));
        var type = sts2.GetType(
            "MegaCrit.Sts2.Core.Nodes.Screens.NCardPileScreen");
        Assert.NotNull(type);

        var ready = type!.GetMethod(
            "_Ready",
            BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic
            | BindingFlags.DeclaredOnly,
            binder: null, types: Type.EmptyTypes, modifiers: null);

        Assert.NotNull(ready);
    }
}
