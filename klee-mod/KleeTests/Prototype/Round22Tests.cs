using System;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND TWENTY-TWO -- the Kokomi round-22 and Furina round-16 act-one runs of
/// 2026-09-06 (`review/active/kokomi-overhaul-round-22-2026-09-06.md`,
/// `review/active/furina-reframe-round-16-2026-09-06.md`) and the rows they
/// left behind on the C# side.
///
/// WHAT THIS FILE HOLDS, and it is <see cref="Round21Tests"/>' arrangement for
/// its reasons: every row here is about a NUMBER a face prints, and a number
/// in this mod needs a live `CombatState` (the README's headless boundary), so
/// what a pin reads is which call a site makes and what it passes. The
/// behavioural claim is pinned in tier0 wherever the same rule is one
/// function there.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class Round22Tests
{
    private const BindingFlags All = HeadlessGame.All;

    // ==================================================================
    // `EB-598` -- the face folds the AIMED body's Vulnerable as well
    // ==================================================================
    //
    // THE FIND (Kokomi r22 lane 1 (c)). `Undertow`'s face read "Deal 10
    // damage, already including 3 if the enemy has a debuff" against a
    // Vulnerable body -- so a target WAS handed to the preview, its Vulnerable
    // satisfied the debuff rider and the extra 3 was folded in -- and the card
    // then delivered 15. The debuff that bought the rider was not in the
    // number the rider was added to.
    //
    // THE EARLY RETURN WAS THE DEFECT. `EB-522` returned on a non-null target,
    // on the reading that the base var had already answered for that creature.
    // It has not: `CalculatedVar.UpdateCardPreview` runs the DEALER's hooks
    // and no target-side term at all, which is exactly `EB-589`'s finding one
    // surface over ("the face is right about four modifiers and silent about
    // the biggest one"). So the aimed body is a FALLBACK ORDER now, not an
    // exclusion.

    [Fact]
    public void The_folded_face_reads_the_aimed_body_then_the_front_enemy()
    {
        var source = Source("Powers/Prototype/FrontFoldedDamageVar.cs")
            .Replace("\r\n", "\n");

        Assert.Contains(
            "var body = target ?? KokomiPlan.FrontEnemy(card.Owner?.Creature);",
            source);
        // The exclusion is gone, and its absence is the row.
        Assert.DoesNotContain("|| target != null", source);
    }

    [Fact]
    public void And_it_is_still_one_fold_through_the_shared_call()
    {
        // `EB-265`'s rule: the fold is the call `ElementalHit.Deal` makes on
        // the same creature a beat later, so a face that disagrees with the
        // board is a red test rather than a number a seat stops trusting.
        var folded = typeof(FrontFoldedDamageVar)
            .GetMethod("UpdateCardPreview", All)!;
        var calls = Il.Calls(folded);

        Assert.Single(calls.Where(c => c == "SimDamagePipeline.TargetMods"));
        Assert.Contains(calls,
            c => c.EndsWith("CalculatedDamageVar.UpdateCardPreview",
                            StringComparison.Ordinal));
    }

    // ------------------------------------------------------------ helpers --

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
