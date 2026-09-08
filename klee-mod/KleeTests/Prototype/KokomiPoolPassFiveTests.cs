using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI POOL PASS FIVE -- the phase of the Dusk lines (`EB-685`,
/// 2026-09-08).
///
/// THE FINDING. Round 27 read pool pass four's own Dusk rows and found two of
/// them out of PHASE with the moment they land on. Breakwater counted the
/// morning that had already been drained, which a Plan written today can never
/// be part of: both seats counted 0 and were paid 5 on four plays out of four.
/// Slack Water's Weak was still a MORNING Plan, so it arrived after the swing
/// it was written against -- the complaint every seat has made since round 25.
/// Both are timing defects rather than numbers, and the pass moves WHEN each
/// clause looks, not how much it pays.
///
/// WHAT CHANGES, one sentence each: Breakwater counts the queue AT DUSK, on a
/// new op of its own; Slack Water's Plan half becomes a Dusk line beside its
/// unchanged now-line, the surface's first row with both; Night Watch is
/// retired, because Slack Water's Dusk half is its job and it lost every draft
/// comparison; Scout Ahead prints the count pass four already gave it.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on
/// <see cref="KokomiPoolPassFourTests"/>' split. The card shapes are REAL --
/// every row is constructed and its face, cost, rarity, plan clauses and
/// smith's move are read off the shipped class. The RESOLUTION is not: a drain
/// needs a live <c>CombatState</c>, so the count's source and the order the
/// dusk queue is emptied in are pinned off the compiled method and labelled.
/// The end-to-end arithmetic is the sim twin's:
/// <c>tier0/tests/test_kokomi_plan.py</c>.
///
/// THE NUMBERS ARE PROTOTYPE NUMBERS (D by the ladder). Nothing here is
/// quotable (R215 B).
/// </summary>
public class KokomiPoolPassFiveTests
{
    private const BindingFlags All = HeadlessGame.All;

    // ======================================================================
    // 1. BREAKWATER -- the wall behind the engine, counting the queue
    // ======================================================================

    [Fact]
    public void Breakwater_pays_a_base_and_a_rate_off_the_plans_it_holds()
    {
        var card = new ProtoKkBreakwater();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Common, card.Rarity);

        Assert.Equal(2, card.PlanClauses.Count);
        Assert.Equal(KokomiPlan.Kind.Block, card.PlanClauses[0].Kind);
        Assert.Equal(5, card.PlanClauses[0].Amount);
        // NOT TIDE WALL'S COUNT ANY MORE. `BlockPerPlanThisMorning` is the
        // depth of a drain that has FINISHED, and a Dusk Plan lands on the
        // evening of the turn it was written on -- so the old spelling read 0
        // every time the morning had been empty, which is what r27's seats
        // saw. This one reads the queue as it stands.
        Assert.Equal(KokomiPlan.Kind.BlockPerPlanHeld,
                     card.PlanClauses[1].Kind);
        Assert.Equal(3, card.PlanClauses[1].Amount);
        Assert.EndsWith(
            "plus 3 for each [gold]Plan[/gold] the [gold]Bake-Kurage[/gold] "
            + "is holding.",
            Face(card));
    }

    [Fact]
    public void The_held_count_is_the_pending_queue_and_not_the_ledger()
    {
        // STRUCTURAL, for this file's stated split. The clause reads
        // <see cref="KokomiPlan.PlansHeld"/> -- the pending queue, LIVE at the
        // moment the entry resolves -- and never
        // `KokomiOverhaulLedger.PlansThisMorning`, which is the number Tide
        // Wall reads and the one pass four wrongly gave this card. Twin:
        // `test_breakwater_pays_for_the_plans_the_jellyfish_is_holding`.
        var resolve = typeof(KokomiPlan).GetMethod("ResolveOne", All)!;
        Assert.Contains("KokomiPlan.PlansHeld", Il.Calls(resolve));

        var source = Source("KokomiPlan", power: true);
        Assert.Contains("case Kind.BlockPerPlanHeld:", source);
        Assert.Contains("plan.Amount * PlansHeld(kokomi)", source);
    }

    [Fact]
    public void The_dusk_entries_leave_the_queue_before_the_first_clause_runs()
    {
        // THE TWO EXCLUSIONS THE FACE NEEDS ARE BY CONSTRUCTION AND NOT BY A
        // FILTER: `ResolveDusk` removes every dusk entry from the queue and
        // only then drains them, so the Breakwater is never one of the Plans
        // it pays for and neither is a second Dusk Plan written the same turn
        // -- a Dusk sibling is not waiting for the next morning either. Twin:
        // `test_breakwater_never_counts_itself_or_a_second_dusk_plan`.
        var calls = Il.Calls(typeof(KokomiPlan).GetMethod("ResolveDusk", All)!)
            .ToList();
        var removed = calls.FindIndex(c => c.Contains("RemoveAll"));
        var drained = calls.FindIndex(c => c.Contains("Drain"));
        Assert.True(removed >= 0 && drained > removed,
                    "the dusk entries must leave the queue before the drain");
    }

    [Fact]
    public void Breakwaters_smith_moves_the_base_and_not_the_rate()
    {
        // `upgrades.PLAN_DELTA_OPS` binds `plan_block` to the FLAT clause
        // first, so the wall gets taller and the rate stays where it is. A
        // rate that smithed would scale with a deck the offer screen cannot
        // see -- pass four's argument, and the pass did not move it.
        var source = Source("ProtoKkBreakwater");
        Assert.Contains("PlanBlock\"].UpgradeValueBy(2m)", source);
        Assert.Contains("new KokomiPlan.Planned("
                        + "KokomiPlan.Kind.BlockPerPlanHeld, 3,",
                        source);
    }

    // ======================================================================
    // 2. SLACK WATER -- R267 pick 1 reversed this pass's phase move
    // ======================================================================

    [Fact]
    public void Slack_water_keeps_its_now_line_and_writes_for_the_morning()
    {
        var card = new ProtoKkSlackWater();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Basic, card.Rarity);

        // R267 PICK 1. Pass five moved the written half to Dusk; the brief
        // names the next-morning Weak as the kit's turn-one decision and a
        // starter card is [USER]'s, so the row is back to its pre-pass form.
        // The face-up half was never touched by either move: 4 damage and a
        // single Weak.
        var source = Source("ProtoKkSlackWater");
        Assert.Contains("DamageCmd.Attack(DynamicVars.Damage.BaseValue)",
                        source);
        Assert.Contains("PowerCmd.Apply<WeakPower>", source);

        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.ApplyWeak, clause.Kind);
        Assert.Equal(KokomiPlan.Aim.AllEnemies, clause.Aim);
        Assert.DoesNotContain("[gold]Dusk[/gold]", Face(card));
        Assert.Contains("[gold]Plan[/gold]", Face(card));
    }

    [Fact]
    public void The_two_half_row_carries_no_dusk_argument_or_tip()
    {
        // R267 pick 1, the other half of the reversal: `plan_dusk:` is a fact
        // about the row's PLAN LINE, so taking it off the row takes `dusk:`
        // off the one `Schedule` call the codegen emits and the Dusk tip off
        // the card. THE MACHINERY IS UNTOUCHED -- pass five widened nothing to
        // add it and nothing narrows to remove it. The card is still playable
        // on an enemy (`KokomiTargets.PetOrEnemy`), which is a two-half row's
        // own shape and not the phase's.
        var source = Source("ProtoKkSlackWater");
        Assert.Contains("if (KokomiPlan.PlayedOnPet(cardPlay))", source);
        Assert.DoesNotContain("dusk:", source);
        Assert.DoesNotContain("ArmKeywordTips.ForDusk", source);
        Assert.Contains("KokomiTargets.PetOrEnemy", source);
        // The Dusk row that IS written-only still is, tip and all.
        Assert.Contains("KokomiTargets.PetOnly", Source("ProtoKkBreakwater"));
        Assert.Contains("this, PlanClauses, dusk: true);",
                        Source("ProtoKkBreakwater"));
    }

    // ======================================================================
    // 3. NIGHT WATCH -- retired
    // ======================================================================

    [Fact]
    public void Night_watch_is_off_the_surface_and_out_of_the_slice()
    {
        // R213 B's deletion rule: the row leaves the sheet, the generated
        // class and `KokomiOverhaulRoster.Slice()` in one commit. It lost
        // every draft comparison in r27 and Slack Water's Dusk half is its
        // job. It spelled NO rule of its own -- its clause was the shared
        // `ApplyWeak` -- so nothing stays behind it the way
        // `KokomiPlan.RedirectQueued` and `CancelAllForCash` do.
        Assert.DoesNotContain(
            "ProtoKkNightWatch",
            Il.CallSequence(Il.Method("KokomiOverhaulRoster", "Slice"))
                .Aggregate(string.Empty, (a, c) => a + c));
        Assert.Null(typeof(ProtoKkBreakwater).Assembly
            .GetType("KleeMod.Cards.Prototype.Generated.ProtoKkNightWatch"));
    }

    // ======================================================================
    // helpers -- KokomiPoolPassFourTests' own, for its reasons
    // ======================================================================

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    /// <summary>One class's own source, read off disk. A SOURCE READ and not
    /// an IL one, and only for the facts IL cannot carry: a named argument
    /// compiles to a positional load that says nothing about the name, and a
    /// literal argument leaves no call at all.</summary>
    private static string Source(string type, bool power = false)
    {
        var root = System.AppContext.BaseDirectory;
        var repo = new System.IO.DirectoryInfo(root);
        while (repo != null && !System.IO.Directory.Exists(
                   System.IO.Path.Combine(repo.FullName, "klee-mod")))
        {
            repo = repo.Parent;
        }
        Assert.NotNull(repo);
        var dir = power
            ? System.IO.Path.Combine(repo!.FullName, "klee-mod", "KleeCode",
                                     "Powers", "Prototype")
            : System.IO.Path.Combine(repo!.FullName, "klee-mod", "KleeCode",
                                     "Cards", "Prototype", "Generated");
        return System.IO.File.ReadAllText(
            System.IO.Path.Combine(dir, type + ".cs"));
    }
}
