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
    // 1. NIGHT WATCH -- the multi-body Weak at Dusk
    // ======================================================================

    [Fact]
    public void Night_watch_is_one_weak_on_every_body_and_no_block()
    {
        var card = new ProtoKkNightWatch();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Common, card.Rarity);

        // ONE CLAUSE. The Block came off because the old face asked nothing:
        // it paid a little of everything for one energy and never made the
        // player choose. Slack Water wins at one body; this wins at three.
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.ApplyWeak, clause.Kind);
        Assert.Equal(KokomiPlan.Aim.AllEnemies, clause.Aim);
        Assert.Equal(1, clause.Amount);
        Assert.DoesNotContain("CreatureCmd.GainBlock",
                              Source("ProtoKkNightWatch"));
    }

    [Fact]
    public void Night_watchs_smith_moves_the_weak_and_nothing_else()
    {
        // 1 -> 2 Weak, on the plan line's own var: the row prints one number
        // and the upgrade moves it.
        var source = Source("ProtoKkNightWatch");
        Assert.Contains("PlanPowerAmount\"].UpgradeValueBy(1m)", source);
        Assert.Contains("{PlanPowerAmount:diff()}", Face(new ProtoKkNightWatch()));
    }

    // ======================================================================
    // 2. BREAKWATER -- the wall behind the engine
    // ======================================================================

    [Fact]
    public void Breakwater_pays_a_base_and_a_rate_off_the_morning()
    {
        var card = new ProtoKkBreakwater();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Common, card.Rarity);

        Assert.Equal(2, card.PlanClauses.Count);
        Assert.Equal(KokomiPlan.Kind.Block, card.PlanClauses[0].Kind);
        Assert.Equal(5, card.PlanClauses[0].Amount);
        // THE SAME COUNT TIDE WALL READS, deliberately: "carried out this
        // turn" on a Dusk Plan IS the morning's depth, because
        // <c>ResolveDusk</c> leaves <c>PlansThisMorning</c> alone -- so the
        // Dusk entry is never one of the Plans it pays for.
        Assert.Equal(KokomiPlan.Kind.BlockPerPlanThisMorning,
                     card.PlanClauses[1].Kind);
        Assert.Equal(3, card.PlanClauses[1].Amount);
    }

    [Fact]
    public void Breakwaters_smith_moves_the_base_and_not_the_rate()
    {
        // `upgrades.PLAN_DELTA_OPS` binds `plan_block` to the FLAT clause
        // first, so the wall gets taller and the morning it reads stays
        // priced the same. A rate that smithed would scale with a deck the
        // offer screen cannot see.
        var source = Source("ProtoKkBreakwater");
        Assert.Contains("PlanBlock\"].UpgradeValueBy(2m)", source);
        Assert.Contains("new KokomiPlan.Planned("
                        + "KokomiPlan.Kind.BlockPerPlanThisMorning, 3,",
                        source);
    }

    // ======================================================================
    // 3. SCOUT AHEAD -- the count that stopped depending on position
    // ======================================================================

    [Fact]
    public void Scout_ahead_counts_the_whole_drain_itself_included()
    {
        var card = new ProtoKkScoutAhead();
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.DrawPerPlanThisTurn, clause.Kind);
        Assert.Equal(1, clause.Amount);
        Assert.EndsWith(
            "Draw 1 card for each [gold]Plan[/gold] carried out this turn.",
            Face(card));
    }

    [Fact]
    public void The_drains_count_is_read_once_before_the_loop()
    {
        // STRUCTURAL, for this file's stated split. ORDER-INDEPENDENCE IS THE
        // POINT: a reader whose number depends on where in the queue it sits
        // is a card whose value is its position, which is what round 26's lane
        // would not spend a slot on. So the count is computed once, before the
        // loop, and every entry of the drain is handed the same number. Twin:
        // `test_scout_ahead_counts_the_whole_drain_wherever_it_sits`.
        var source = Source("KokomiPlan", power: true);
        Assert.Contains("var drainPlans = due.Count", source);
        Assert.DoesNotContain("var after = due.Count - index - 1;", source);

        // STILL CARRY-OUTS AND NOT ENTRIES (`EB-501`): Nereid's Ascension
        // carries the first entry of a drain out twice, so a drain under the
        // Rare counts one more.
        Assert.Contains("CarryOutTimes(kokomi) > 1", source);
        var resolve = typeof(KokomiPlan).GetMethod("ResolveOne", All)!;
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
