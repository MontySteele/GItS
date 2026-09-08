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
/// KOKOMI POOL PASS FOUR -- the round-26 dead faces, rebuilt (`EB-679`,
/// 2026-09-08).
///
/// THE FINDING. Four rows of the pool were read by round 26's lanes and none
/// of them was worth a slot. Night Watch asked nothing (4 Block, a Weak and
/// the casket's ping for one energy). Breakwater was Night Watch's worse twin.
/// Scout Ahead's whole value was its POSITION in the queue, so it competed for
/// a slot with Plans that always paid. Read the Field's look-and-bury never
/// produced a decision, and its 5 Block was a dead slot beside a Dusk Plan.
///
/// WHAT REPLACES THEM, one sentence each: Night Watch is the multi-body Weak
/// at Dusk and Slack Water's pair; Breakwater is the wall behind the engine,
/// reading the morning it followed; Scout Ahead counts the whole drain,
/// itself included, so its answer no longer moves with the card; Read the
/// Field TAKES a card instead of burying one, and the count it shows is a
/// number the smith moves.
///
/// TWO OF THE FOUR MOVED AGAIN AT POOL PASS FIVE (`EB-685`, 2026-09-08) and
/// their pins moved with them, to <see cref="KokomiPoolPassFiveTests"/>: round
/// 27 read both Dusk rows out of PHASE with the moment they land on. Night
/// Watch is retired -- Slack Water's Plan half became the Dusk Weak and a pool
/// does not need the card twice -- and Breakwater counts the queue at dusk
/// rather than the morning it followed, which a Plan written today can never
/// be part of. What is still pass four's, and pinned below, is Scout Ahead's
/// recount and Read the Field's take.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on
/// <see cref="KokomiPoolPassThreeTests"/>' split. The card shapes are REAL --
/// every row is constructed and its face, cost, rarity, plan clauses and
/// smith's move are read off the shipped class. The RESOLUTION is not: a drain
/// needs a live <c>CombatState</c>, so the recounted drain is pinned off the
/// compiled method and labelled. The end-to-end arithmetic is the sim twin's:
/// <c>tier0/tests/test_kokomi_plan.py</c>.
///
/// THE NUMBERS ARE PROTOTYPE NUMBERS (D by the ladder). Nothing here is
/// quotable (R215 B).
/// </summary>
public class KokomiPoolPassFourTests
{
    private const BindingFlags All = HeadlessGame.All;

    // ======================================================================
    // 1 and 2. NIGHT WATCH and BREAKWATER moved to pool pass five (`EB-685`);
    // their pins are in KokomiPoolPassFiveTests, and the class doc says why.
    // ======================================================================

    // ======================================================================
    // 3. SCOUT AHEAD -- the count pass four took off its position, and R267
    //    pick 3 put back on it
    // ======================================================================

    [Fact]
    public void Scout_ahead_counts_the_plans_that_follow_it()
    {
        // R267 PICK 3 REVERSED THIS PASS'S RECOUNT. Pass four removed an
        // ordering decision because one seat avoided the 0-payout slot; the
        // clause is back, and the face says "later" so a seat can read the
        // rule off it.
        var card = new ProtoKkScoutAhead();
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.DrawPerPlanAfter, clause.Kind);
        Assert.Equal(1, clause.Amount);
        Assert.EndsWith(
            "Draw 1 card for each later [gold]Plan[/gold] carried out with "
            + "this one.",
            Face(card));
    }

    [Fact]
    public void The_drains_count_is_read_per_entry_again()
    {
        // STRUCTURAL, for this file's stated split. R267 pick 3: the count is
        // read INSIDE the entry loop, which is what lets a Scout Ahead written
        // first and one written last answer differently -- the decision the
        // card poses. Pass four's whole-drain term stays computed once above
        // the loop for `DrawPerPlanThisTurn`, which no row spells. Twin:
        // `test_scout_ahead_counts_the_plans_that_follow_it`.
        var source = Source("KokomiPlan", power: true);
        Assert.Contains("var after = due.Count - index - 1;", source);
        Assert.Contains("var drainPlans = due.Count", source);

        // CARRY-OUTS AND NOT ENTRIES (`EB-501`), and for the positional count
        // that means Nereid's adds NOTHING: `EB-655` narrowed the Rare to the
        // FIRST entry of a drain, and an entry is never the first when
        // something follows it, so every later entry is one carry-out.
        Assert.Contains("CarryOutTimes(kokomi) > 1", source);
        var resolve = typeof(KokomiPlan).GetMethod("ResolveOne", All)!;
        Assert.Contains(resolve.GetParameters(), p => p.Name == "after");
        Assert.Contains(resolve.GetParameters(), p => p.Name == "drainPlans");
    }

    // ======================================================================
    // 4. READ THE FIELD -- a take, not a bury
    // ======================================================================

    [Fact]
    public void Read_the_field_takes_one_of_three_and_bottoms_the_rest()
    {
        // The screen is the game's own selection grid over the top N; the pick
        // is added to the HAND and everything else the player was shown goes
        // to the bottom of the pile it came from, so nothing leaves the deck.
        // Twin: `effects._op_scry_take`, which takes the lowest-cost card
        // because the sim has no human.
        var source = Source("ProtoKkReadTheField");
        Assert.Contains("Cards.Take(DynamicVars[\"Scry\"].IntValue)", source);
        Assert.Contains("ScryTake.Prompt", source);
        Assert.Contains("CardPileCmd.Add(taken, PileType.Hand)", source);
        Assert.Contains("CardPilePosition.Bottom", source);
        // THE 5 BLOCK IS GONE: a dead slot beside a Dusk Plan, and the whole
        // now-line is the selection now.
        Assert.DoesNotContain("CreatureCmd.GainBlock", source);
    }

    [Fact]
    public void Read_the_fields_look_count_is_a_number_the_smith_moves()
    {
        // "Look at 2, bury 1" got no better for showing 3; "look at 3, TAKE 1"
        // does, which is what made the count upgradable at all (`EB-679`).
        var source = Source("ProtoKkReadTheField");
        Assert.Contains("new DynamicVar(\"Scry\", 3m)", source);
        Assert.Contains("Scry\"].UpgradeValueBy(1m)", source);
        Assert.Contains("{Scry:diff()}", Face(new ProtoKkReadTheField()));
    }

    [Fact]
    public void The_take_screen_has_one_ruled_string_and_one_source()
    {
        // A `LocString` is a table plus a key with no raw-text constructor, so
        // ruled copy can only reach the screen as a row and
        // `KleeMod.InjectLocStrings` is that row's only source. A SECOND CLASS
        // beside `ScryBottom` because a screen is keyed on the VERB, and
        // taking and burying are two verbs.
        Assert.False(string.IsNullOrWhiteSpace(ScryTake.PromptText));
        Assert.Contains("selectionScreenPrompt", ScryTake.PromptKey);
        Assert.NotEqual(ScryBottom.PromptKey, ScryTake.PromptKey);
    }

    // ======================================================================
    // helpers -- KokomiPoolPassThreeTests' own, for its reasons
    // ======================================================================

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    /// <summary>One generated class's own source, read off disk. A SOURCE READ
    /// and not an IL one, and only for the facts IL cannot carry: a named
    /// argument compiles to a positional load that says nothing about the
    /// name, a `const string` is a literal no call sequence mentions, and a
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
