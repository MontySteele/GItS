using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-197 -- THE BAKE-KURAGE BUFF'S DURATION SENTENCE, under the memory rule.
///
/// Found eyes-on at Gate B (sec.13.6): the buff read "Lasts 1 more turn" in the
/// same frame as the strip's "The Bake-Kurage is on the field for the whole
/// fight. Nothing summons it and nothing removes it." Two surfaces, one
/// creature, opposite claims -- and the strip was the one telling the truth.
///
/// It is not a duration BUG: nothing under the flag ticks the power down
/// (sec.12.6 items 1, 2 and 8 -- the stacks are clamped to 1 at
/// KurageSummon.Field, FirePulse returns before TickDownDuration, and v4
/// installs the jellyfish at combat start). It is the FACE, which kept the
/// shipped sentence. A power with no countdown prints no countdown.
///
/// The power models are allocated uninitialised -- their real constructors
/// register with the game's model tables -- and Localization is a pure string
/// builder that reads nothing off the instance (InterpolationPinTests' idiom).
/// </summary>
public class KurageBuffFaceTests
{
    private static string Description<T>() where T : notnull
    {
        var model = RuntimeHelpers.GetUninitializedObject(typeof(T));
        var rows = (List<(string, string)>)model.GetType()
            .GetProperty("Localization", Harness.HeadlessGame.All)!
            .GetValue(model)!;
        return rows.First(r => r.Item1 == "description").Item2;
    }

    [Fact]
    public void The_jellyfish_buff_prints_no_duration_under_the_memory_rule()
    {
        var body = Description<KurageSummonPower>();

        // The exact string the capture caught, in its unformatted form.
        Assert.DoesNotContain("Lasts", body);
        Assert.DoesNotContain("{Amount}", body);
    }

    [Fact]
    public void The_jellyfish_buff_says_the_lifetime_it_actually_has()
    {
        // In the strip's own words, so the two surfaces cannot drift again.
        Assert.Contains("whole fight", Description<KurageSummonPower>());
    }

    [Fact]
    public void The_pulse_half_of_the_face_is_untouched()
    {
        // Only the duration sentence moved. What the pulse DOES under the
        // memory rule is a different question and a [USER] one -- this row is
        // a false statement about a countdown, not a rewrite of the power.
        var body = Description<KurageSummonPower>();

        Assert.Contains("At the end of your turn", body);
        Assert.Contains("[gold]Charge[/gold]", body);
        Assert.Contains("[gold]Hydro[/gold]", body);
    }
}
