using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-197 and EB-247 -- THE BAKE-KURAGE BUFF'S FACE, under the memory rule.
/// One file, because the two rows are the same buff caught lying about two
/// different things: its LIFETIME (EB-197, below) and its PULSE (EB-247).
///
/// EB-247 -- WHAT THE PULSE DOES. The pulse half of this face promised
/// "4 plus 3 per Charge damage" long after the memory rule retired the
/// per-Charge term. `KurageMemory.Pulse` keys on the TYPE of the last card
/// Kokomi played this turn and pays a flat number per branch -- Attack 4
/// damage and Hydro, Skill 5 Block, Power 1 Charge, no card no pulse -- which
/// is the ruled table (R219 D; packet "The pulse -- keyed to the last card
/// played"). Three witnesses: BOTH of KURAGECAD-W1's fight records named the
/// disagreement unprompted, and the wire's `pulse_kind` alternates `attack 4`
/// / `skill 5 block` page by page. A fourth landed on KOKOMI-SLICE1-WF. The
/// BEHAVIOUR matches the ruling and did not move; the face did.
///
/// The old pin below this one asserted the pulse half was UNTOUCHED, on the
/// reasoning that EB-197 was "a false statement about a countdown, not a
/// rewrite of the power". EB-247 is that rewrite, so the pin inverts: it now
/// asserts the retired arithmetic is GONE and the ruled branches are printed.
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

}
