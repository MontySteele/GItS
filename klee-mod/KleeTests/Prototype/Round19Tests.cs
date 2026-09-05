using System;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND NINETEEN -- the three kits' act-one runs of 2026-09-05, and the rows
/// they left behind (`review/active/klee-overhaul-round-19-2026-09-05.md`,
/// `kokomi-overhaul-round-19-2026-09-05.md`,
/// `furina-reframe-round-13-2026-09-05.md`).
///
/// WHAT THIS FILE HOLDS. The round's rows are mostly WORDS -- a rule the
/// engines have had all along and no surface stated -- so most pins here are a
/// sentence on a tip, read off the compiled method the way
/// <see cref="Round16Tests"/> reads one, plus the structural read that says the
/// sentence is true of the code rather than agreed with by it.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class Round19Tests
{
    private const BindingFlags All = HeadlessGame.All;

    /// <summary>A tip's printed body, keys dropped.
    /// <see cref="Round16Tests"/>' helper, verbatim.</summary>
    private static string Printed(Type owner, string method) =>
        string.Concat(Il.Strings(owner.GetMethod(method, All)!)
            .Where(s => !s.StartsWith("KLEEMOD-", StringComparison.Ordinal)));

    // ==================================================================
    // `EB-538` -- a carry-out is not a hit
    // ==================================================================
    //
    // THE FIND (Kokomi r19 lane 2). Skittish gave NO Block to a body hit by
    // Kurage's Oath's and Ambush's carry-outs, and then 6 Block to a plain
    // Strike on the same enemy in the same fight. The seat: "either a defect
    // or a large undocumented advantage of planning into blockers".
    //
    // IT IS THE SECOND, and it is the rule `EB-490` already printed on Klee's
    // Set off one kit over: a planned clause is not a card being played, so it
    // goes out through `ElementalHit.Deal` rather than `DamageCmd.Attack` and
    // reaches `CreatureCmd.Damage` as `ValueProp.Unpowered` with `dealer:
    // null` -- neither an attacker nor a powered hit for a when-hit power to
    // answer. Klee's tip says so; Kokomi's did not.

    private static string PlanTip() => Printed(typeof(ArmKeywordTips), "ForPlan");

    [Fact]
    public void The_plan_tip_says_a_carry_out_is_not_a_hit()
    {
        // SET OFF'S OWN SENTENCE, word for word, because it is the same rule
        // at the same call: "when-hit power" is what a player calls the thing
        // on the enemy's status bar, which is `EB-490`'s finding and the
        // wording it bought.
        Assert.Contains("A carry-out is not a hit: no when-hit power fires.",
                        PlanTip());
        Assert.Contains("no when-hit power fires",
                        Printed(typeof(ArmKeywordTips), "ForSetOff"));
    }

    [Fact]
    public void The_clause_cost_the_tip_its_ceiling_and_the_lint_carries_it()
    {
        // Stated rather than left implicit: the tip was at 135 of 135 before
        // this clause and every clause on it is a seat's finding, so the
        // overage is deliberate and `tools/lint_text_conventions.py` carries
        // `PlanKey` by name with that reason -- the bargain `SetOffKey` makes.
        var rendered = PlanTip()
            .Replace("[gold]", string.Empty).Replace("[/gold]", string.Empty);
        Assert.Equal(186, rendered.Length);
        Assert.EndsWith("A carry-out is not a hit: no when-hit power fires.",
                        rendered);
    }

    [Fact]
    public void A_carry_out_hands_the_hit_no_attacker_so_skittish_cannot_fire()
    {
        // THE BEHAVIOURAL HALF, and it is STRUCTURAL for the reason every
        // damage pin in this suite is: a carry-out needs a live `CombatState`
        // (the README's headless boundary), so what a test reads is which
        // method the call site calls and what that method's one damage call
        // passes.
        //
        // The carry-out asks the elemental funnel...
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "Hit")),
                        c => c == "ElementalHit.Deal");

        // ...and `Deal` reaches `CreatureCmd.Damage` as an UNPOWERED hit with
        // NO DEALER and NO CARD SOURCE, whatever it was asked to deal. Read
        // off the source because an argument's VALUE is invisible to `Il`;
        // `Round16Tests` reads the same lines the same way for Set off.
        var source = Source("Powers/ElementalHit.cs").Replace("\r\n", "\n");
        Assert.Contains(
            "await CreatureCmd.Damage(\n"
          + "            choiceContext, target, landed,\n"
          + "            ignoreBlock ? ValueProp.Unpowered | "
          + "ValueProp.Unblockable\n"
          + "                        : ValueProp.Unpowered,\n"
          + "            dealer: null, cardSource: null, cardPlay: null);",
            source);

        // And the carry-out is never routed through the Attack door, which is
        // the other half of "not a card being played".
        Assert.DoesNotContain(Il.Calls(Il.Method("KokomiPlan", "Hit")),
                              c => c.StartsWith("DamageCmd.",
                                                StringComparison.Ordinal));
    }

    // ---- helpers ---------------------------------------------------------

    /// <summary>A source file under `klee-mod/KleeCode`.
    /// <see cref="Round16Tests"/>' helper, verbatim.</summary>
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
