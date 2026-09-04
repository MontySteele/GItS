using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND 13, the legibility rows -- what a face has to say before it is read
/// for the first time.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class Round13Tests
{
    /// <summary>A generated card's printed face, off an instance allocated
    /// uninitialised: these `Localization` getters are pure string builders
    /// (`Round12Tests`' idiom, and the headless boundary's reason).</summary>
    private static string Face<T>() where T : notnull
    {
        var model = RuntimeHelpers.GetUninitializedObject(typeof(T));
        var rows = (List<(string, string)>)model.GetType()
            .GetProperty("Localization")!.GetValue(model)!;
        return rows.Single(r => r.Item1 == "description").Item2;
    }

    // ==================================================================
    // `EB-446` -- a name one card is written against and another grants
    // ==================================================================
    //
    // THE FIND (Furina r7 (c) 5). <i>Fischl -- Nightrider</i> prints "If Oz is
    // out, he deals 5 Electro damage to a random enemy" and nothing on the
    // screen says what puts Oz out. The seat played it five times and never
    // learned: the thing the word names is a DIFFERENT companion card, the
    // Power <i>Fischl -- Oz, at Your Side</i>, which that run never held.
    //
    // `ForGrounded`'s SHAPE, and its argument: the attach travels with the
    // printed WORD (`gen_klee_cards.arm_keyword_tip_calls`), so the face that
    // names him carries the definition whether or not the deck can grant him
    // -- which is the state the seat was in for all five plays.

    [Fact]
    public void Nightrider_golds_the_name_it_cannot_grant()
    {
        var face = Face<ProtoMcFischlNightrider>();

        Assert.Contains("If [gold]Oz[/gold] is out", face);
    }

    [Fact]
    public void The_face_that_names_him_carries_the_definition()
    {
        // The whole of the fix: the tip is attached FROM THE FACE, so a reader
        // who has never seen the Power still gets told which card it is.
        Assert.Contains("ArmKeywordTips.ForOz",
                        Il.Calls(Il.Method("ProtoMcFischlNightrider",
                                           "get_ExtraHoverTips")));
        Assert.Contains("ArmKeywordTips.ForOz",
                        Il.Calls(Il.Method("ProtoMcFischlOz",
                                           "get_ExtraHoverTips")));
    }

    [Fact]
    public void The_tip_names_the_power_that_puts_him_out()
    {
        var body = string.Concat(Il.Strings(
            Il.Method("ArmKeywordTips", "ForOz")));

        Assert.Contains("Oz, at Your Side", body);
        // The title is quoted WITHOUT its `Fischl --` prefix: the text
        // conventions ban a dash of any kind in player-facing text, and the
        // lint bites on one.
        Assert.DoesNotContain("--", body);
    }
}
