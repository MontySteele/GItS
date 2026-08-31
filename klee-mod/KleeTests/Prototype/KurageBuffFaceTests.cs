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
    public void The_face_still_opens_on_when_the_pulse_resolves()
    {
        // Unchanged by EB-247 and load-bearing: the pulse is an END-of-turn
        // event while the memory fires at turn START, and the two are only
        // told apart by this clause.
        var body = Description<KurageSummonPower>();

        Assert.Contains("At the end of your turn", body);
        Assert.Contains("[gold]Hydro[/gold]", body);
    }

    [Fact]
    public void The_retired_per_charge_promise_is_gone()
    {
        // EB-247's red half. `KURAGE_PULSE_PER_CHARGE` retired with the
        // memory rule; the face went on printing it, and that is the sentence
        // both fight records quoted back.
        var body = Description<KurageSummonPower>();

        Assert.DoesNotContain("per [gold]Charge[/gold]", body);
        Assert.DoesNotContain(
            KokomiConstants.KuragePulsePerCharge + " per", body);
    }

    [Fact]
    public void The_face_prints_all_three_ruled_branches_and_the_null_one()
    {
        // Each number FROM ITS LAW, so a swept constant cannot leave the face
        // behind -- the same discipline the Muster keyword keeps on its
        // discount. The Attack branch is asserted flat: it is the branch the
        // stale text hid, and it is EB-256's only escape.
        var body = Description<KurageSummonPower>();

        Assert.Contains("last card you played", body);
        Assert.Contains(
            $"After an Attack: it deals {KokomiConstants.KuragePulseBase} "
            + "damage", body);
        Assert.Contains(
            "After a Skill: it grants "
            + KurageMemory.KurageMemoryLaw.PulseBlock + " Block", body);
        Assert.Contains("After a Power:", body);
        Assert.Contains("If you played no card at all, it does nothing.",
                        body);
    }

    [Fact]
    public void The_fielding_tip_quotes_the_same_ruled_table_as_the_buff()
    {
        // ONE PULSE, THREE SURFACES. The buff above, this paragraph (which the
        // fielding cards hover AND the end-of-turn docket asks for by design,
        // TurnEndAttribution's `kurage` slot), and the wire. All three said
        // different things, which is what the row is. Out of combat, so the
        // RULE is asserted with no live bank to read.
        var rule = Cards.KokomiRiderTips.PulseBody(null, inCombat: false);

        Assert.Contains("LAST card you played", rule);
        Assert.Contains(
            $"Attack -> {KokomiConstants.KuragePulseBase} damage", rule);
        Assert.Contains(
            "Skill -> " + KurageMemory.KurageMemoryLaw.PulseBlock + " Block",
            rule);
        Assert.Contains("No card played, no pulse.", rule);
        Assert.DoesNotContain("per [gold]Charge[/gold] you hold", rule);
    }

    [Fact]
    public void The_power_branch_prints_the_mode_it_is_actually_in()
    {
        // PowerPulse is a MODE selector with a live alternative ("hydro",
        // v2's PICK C1, still implemented so the arm can be swept). A face
        // that hard-coded the Charge sentence would be wrong the moment the
        // arm moved -- which is the defect class this row is, one sweep later.
        var body = Description<KurageSummonPower>();

        if (KurageMemory.KurageMemoryLaw.PowerPulse == "charge")
        {
            Assert.Contains(
                $"it banks {KokomiConstants.ChargePerExhaust} "
                + "[gold]Charge[/gold]", body);
        }
        else
        {
            Assert.Contains(
                "After a Power: it applies [gold]Hydro[/gold]", body);
        }
    }
}
