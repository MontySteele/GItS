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

    // ==================================================================
    // `EB-597` -- Shrink's gloss names Attacks and Shrink bites a Skill
    // ==================================================================
    //
    // THE FIND (Kokomi r22 lane 1, fight 2). Wearing `Shrink -1 -- While
    // Shrinker Beetle is alive, your Attacks deal 30% less damage`, the seat
    // watched `Kurage's Oath` -- printed `cost 1, skill` -- fall from 3 to 2.
    // "Weak's glossary on the same screen goes out of its way to say 'a
    // Skill's damage too'; Shrink's does not, and Shrink hits Skills anyway.
    // That is a contradiction between a debuff's text and its behaviour."
    //
    // THE ENGINE IS RIGHT AND ONLY THE WORDS ARE WRONG, which is `EB-469`'s,
    // `EB-481`'s and `EB-521`'s finding a fourth time -- so the fix is the
    // `powers` loc merge and the page row, and this reads the assembly to say
    // which of the two the row's question ("Attack-only or all player
    // damage") actually has as its answer.

    [Fact]
    public void Shrink_gates_on_the_hit_exactly_as_weak_does()
    {
        var shrink = typeof(MegaCrit.Sts2.Core.Models.Powers.ShrinkPower)
            .GetMethod("ModifyDamageMultiplicative", All)!;
        var weak = typeof(MegaCrit.Sts2.Core.Models.Powers.WeakPower)
            .GetMethod("ModifyDamageMultiplicative", All)!;

        // ONE GATE AND IT IS THE PROP'S, not the card's type -- so a Skill
        // that deals damage is Shrunk exactly as an Attack is, because every
        // damage clause the generator emits carries `ValueProp.Move`.
        Assert.Contains("ValuePropExtensions.IsPoweredAttack",
                        Il.Calls(shrink));
        Assert.Contains("ValuePropExtensions.IsPoweredAttack",
                        Il.Calls(weak));
        // And no card is in the question at all: nothing in that body reads a
        // `CardModel`, which is the structural half of the same claim.
        Assert.DoesNotContain(Il.Calls(shrink),
                              c => c.StartsWith("CardModel.",
                                                StringComparison.Ordinal));
    }

    [Fact]
    public void The_shrink_rows_say_a_skills_damage_too_at_the_measured_rate()
    {
        // THE RATE IS THE POWER'S OWN, measured rather than typed: the
        // canonical var `DamageDecrease` is already a percentage, and the
        // blind page's `SHRINK_DEALT_PCT` quotes it.
        var power = new MegaCrit.Sts2.Core.Models.Powers.ShrinkPower();
        var vars = (System.Collections.IEnumerable)power.GetType()
            .GetProperty("CanonicalVars", All)!.GetValue(power)!;
        var rate = vars.Cast<object>()
            .Select(v => (
                name: (string)v.GetType().GetProperty("Name")!.GetValue(v)!,
                value: (decimal)v.GetType().GetProperty("BaseValue")!
                                 .GetValue(v)!))
            .Single(v => v.name == "DamageDecrease").value;
        Assert.Equal(30m, rate);

        var mod = Read(System.IO.Path.Combine("klee-mod", "KleeCode",
                                              "KleeMod.cs"));
        Assert.Contains("[\"SHRINK_POWER.description\"]", mod);
        Assert.Contains("[\"SHRINK_POWER.smartDescription\"]", mod);
        // The clause the row is about, and the two holes the power fills.
        Assert.Contains("[blue]30%[/blue] less damage with every hit it ",
                        mod);
        Assert.Contains("{ApplierName}", mod);
        Assert.Contains("[blue]{DamageDecrease}%[/blue]", mod);
    }

    // ==================================================================
    // `EB-602` -- the reaction preview folds the number the FACE prints
    // ==================================================================
    //
    // THE FIND (Furina r16 lane 1 (c) 3). A lit Chevreuse's face read 10 off a
    // printed 7; the reaction preview beside it named Vaporize off the 7; and
    // 15 landed. `EB-589` put the folded total on this tip and then read the
    // wrong number to fold: `IntValue` is the var's stored BASE, and the
    // Spotlight, her Weak and Passion Overload all live between it and the
    // face. The tip's own claim is that it folds the same number the face
    // does, so it reads `PreviewValue` -- the figure `{Var:diff()}` renders.

    [Fact]
    public void The_previews_base_is_the_number_the_face_renders()
    {
        // MEASURED, because this is the whole of the row: a var built at 7
        // whose preview says 10 answers 7 to `IntValue`. That gap is what the
        // seat read off two surfaces of one card.
        var v = new MegaCrit.Sts2.Core.Localization.DynamicVars.DynamicVar(
            "Damage", 7m);
        Assert.Equal(7, v.IntValue);
        v.PreviewValue = 10m;
        Assert.Equal(7, v.IntValue);
        Assert.Equal(10m, v.PreviewValue);

        var source = Source("Cards/KleeCardTooltips.cs").Replace("\r\n", "\n");
        Assert.Contains("var preview = (int)dynamicVar.PreviewValue;", source);
        Assert.Contains("return preview > 0 ? preview : dynamicVar.IntValue;",
                        source);
    }

    [Fact]
    public void And_a_face_that_already_folded_the_target_is_not_folded_twice()
    {
        // `EB-598` put the target's terms into `FrontFoldedDamageVar`'s own
        // `PreviewValue`, so the branch that reads that preview must not ask
        // `ResolveOnTarget` for them again. Asked BY NAME, because the class
        // is Compile-Removed from a release build.
        var source = Source("Cards/KleeCardTooltips.cs").Replace("\r\n", "\n");
        Assert.Contains(
            "calculated.GetType().Name == \"FrontFoldedDamageVar\"", source);

        var amplified = typeof(KleeCardTooltips)
            .GetMethod("AmplifiedBody", All)!;
        var calls = Il.Calls(amplified);
        Assert.Contains(calls, c => c == "KleeCardTooltips.TargetAlreadyFolded");
        // Both branches end at the target's own cap, which is
        // `ResolveOnTarget`'s last step and not a second arithmetic.
        Assert.Contains(calls, c => c == "SimDamagePipeline.ResolveOnTarget");
        Assert.Contains(calls, c => c == "KleeCardTooltips.Capped");
    }

    // ==================================================================
    // `EB-603` -- Gorou's Block on a killing blow
    // ==================================================================
    //
    // THE FIND (Furina r16 lane 1). `Gorou - Inuzaka All-Round Defense` took
    // a 12-HP body off the board and gave 0 Block, twice, both on killing
    // blows: "I cannot separate 'the clause is broken' from 'the clause does
    // not fire on a kill'."
    //
    // TWO THINGS THE READ FOUND. The number was the SWING and not the loss --
    // `UnblockedDamage` carries the overkill, and `DamageResult` carries the
    // overkill as its own field, so subtracting it is a read rather than a
    // second definition. And a creature with NO combat could wipe the whole
    // ledger table: `For` drops it whenever the combat differs from the last
    // one, and a card whose owner is off the board answers null -- which two
    // speculative call sites can be handed (a face's multiplier lambda, and a
    // smart description that runs "on every tooltip read"). A wipe between
    // the hit and the Block is a 0 on a beat that dealt damage.
    //
    // The arithmetic is pinned for real in tier0
    // (`test_eb603_gorou_blocks_on_a_kill.py`); the ledger is a real object
    // and its guard is exercised here.

    [Fact]
    public void The_play_total_counts_hp_lost_and_not_the_overkill()
    {
        var source = Source("Powers/Prototype/CompanionOverhaulHooks.cs")
            .Replace("\r\n", "\n");

        Assert.Contains(
            ".NoteDamage(result.UnblockedDamage - result.OverkillDamage);",
            source);
    }

    [Fact]
    public void A_creature_with_no_combat_does_not_drop_the_ledger_table()
    {
        // A REAL LEDGER AND A REAL WIPE. The seat's ledger banks a play's
        // damage; a read for a creature that is off the board must leave it
        // standing, because that read is a face refreshing itself and not a
        // new fight starting.
        CompanionOverhaulLedger.ResetAll();
        var seat = Seat.Klee().WithCombatState();
        var ledger = CompanionOverhaulLedger.For(seat.Creature);
        ledger.BeginPlay();
        ledger.NoteDamage(12);

        var offBoard = Seat.Klee().Creature;          // no combat state
        Assert.Null(offBoard.CombatState);
        CompanionOverhaulLedger.For(offBoard);

        Assert.Equal(12, CompanionOverhaulLedger.For(seat.Creature)
                                                .DamageDealtThisPlay);
        Assert.Same(ledger, CompanionOverhaulLedger.For(seat.Creature));
        CompanionOverhaulLedger.ResetAll();
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
