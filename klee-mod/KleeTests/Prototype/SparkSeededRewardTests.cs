using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-577`: the Klee arm's first card rewards each carry a Spark-priced row.
///
/// THE READING SIX ROUNDS MADE. Sparks are inert until a sink is drafted (r17
/// through r21); the r21 lane-2 seat ended fights holding 3, 4 and 5 with Dig
/// In the deck's one reader, so the resource this kit mints on every explosion
/// did nothing at all for two acts.
///
/// WHAT IS REACHABLE HERE. Running the patch end to end is NOT: it wants a
/// `Player` with a `RunState`, a `CardCreationOptions` and the game's own
/// `CardFactory` roll, all of which are past the headless boundary (KleeTests
/// README). What IS reachable is every DECISION the rule makes -- the target it
/// patches, the gates it asks before it touches anything, the constant it
/// bounds itself by, and the pick that spends no rng -- so that is what this
/// pins, on the real shipped assembly. The BEHAVIOUR is pinned in the sim
/// (`tier05/tests/test_eb577_spark_seed.py`), which owns the same rule.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class SparkSeededRewardTests
{
    private static System.Type Patch => typeof(KleeOverhaulLaw)
        .Assembly
        .GetType("KleeMod.Powers.CardFactory_CreateForReward_SparkSeed_Patch",
                 throwOnError: true)!;

    private static MethodInfo Postfix =>
        Patch.GetMethod("Postfix", HeadlessGame.All)!;

    [Fact]
    public void It_patches_the_one_roll_a_reward_screen_makes()
    {
        // The base game rolls a reward screen's cards in exactly one place,
        // and its three-argument overload is the multi-card one a screen uses.
        var attr = Patch.GetCustomAttributes(inherit: true)
            .OfType<HarmonyPatch>()
            .First(a => a.info.declaringType != null);
        Assert.Equal(typeof(CardFactory), attr.info.declaringType);
        Assert.Equal(nameof(CardFactory.CreateForReward), attr.info.methodName);
        Assert.Equal(
            new[] { typeof(Player), typeof(int), typeof(CardCreationOptions) },
            attr.info.argumentTypes);

        // A POSTFIX, because the rule reads what the roll produced: a screen
        // that already offered a Spark row is left exactly as it was.
        Assert.NotNull(Postfix.GetCustomAttribute<HarmonyPostfix>());
        Assert.Contains(Postfix.GetParameters(), p => p.Name == "__result");
    }

    [Fact]
    public void Every_gate_the_rule_asks_is_in_the_body()
    {
        var calls = Il.Calls(Postfix);
        // QUARANTINED: the arm's switch and the arm's identity gate, the same
        // pair every other rule in this arm asks.
        Assert.Contains(calls,
            c => c.EndsWith("KleeOverhaul.get_Enabled",
                            System.StringComparison.Ordinal));
        Assert.Contains(calls, c => c.Contains("get_Character"));
        // THE FLOOR, off the run rather than counted here.
        Assert.Contains(calls, c => c.Contains("get_TotalFloor"));
        // AND THE POOL THE SWAP DRAWS FROM is the screen's own, so the rule
        // can never offer a card that screen could not have rolled.
        Assert.Contains(calls, c => c.Contains("GetPossibleCards"));
    }

    [Fact]
    public void The_bound_is_the_mirrored_constant_and_not_a_literal()
    {
        // `EB-89`'s rule: the number is a named constant compared by value
        // against tier0 (`tools/lint_constant_parity.py`), so a re-tune moves
        // both engines or neither.
        Assert.Equal(3, KleeOverhaulLaw.SparkSeedFloors);
        Assert.DoesNotContain(
            Il.Strings(Postfix),
            s => s.Contains(KleeOverhaulLaw.SparkSeedFloors.ToString()));
    }

    [Fact]
    public void The_pick_spends_no_run_rng()
    {
        // `RunState.Rng` has no card-reward stream of its own -- the roll this
        // postfix runs after has already been made -- so drawing here would
        // spend one of the base game's streams and a seeded run would diverge
        // from the same seed played with the arm off. The pick is DERIVED: the
        // eligible rows in a stable order, indexed by the floor.
        var pick = Patch.GetMethod("Pick", HeadlessGame.All)!;
        var calls = Il.Calls(pick);
        Assert.DoesNotContain(calls, c => c.Contains("Rng"));
        Assert.Contains(calls, c => c.Contains("OrderBy"));
        // And it takes the FLOOR, not the player: nothing about the run's
        // state can reach the choice except the number that bounds the rule.
        Assert.Equal(new[] { typeof(int).Name },
                     pick.GetParameters().Take(1)
                         .Select(x => x.ParameterType.Name).ToArray());
    }

    /// <summary>
    /// `EB-594`. THE SWAPPED ROW IS NEVER THE CANONICAL MODEL.
    ///
    /// The rule draws its replacement from
    /// <c>CardCreationOptions.GetPossibleCards</c>, which is the game's
    /// REGISTRY: those rows are canonical models, and a canonical model handed
    /// to a screen survives until something asserts on it. On
    /// `0.2.2817+proto` lane 1 the assert came from
    /// <c>CardChoiceHistoryEntry..ctor</c> serialising the pick
    /// (<c>AbstractModel.AssertMutable</c> -> <c>CanonicalModelException: ...
    /// ProtoKoSugarRush used in incorrect place</c>), thrown inside
    /// <c>HeftyTablet.AfterObtained</c>, which left the Neow screen with an
    /// empty option list and no legal verb: a hard blocker.
    ///
    /// A STRUCTURAL PIN (see <see cref="Il"/>), because constructing a real
    /// reward result wants a live <c>RunState</c>, past the headless boundary.
    /// The postfix constructs no <c>CardCreationResult</c> of its own at all,
    /// so the ONLY door a row reaches a screen through is <c>Instantiate</c>,
    /// and that one creates an instance first.
    /// </summary>
    [Fact]
    public void The_swapped_row_is_an_instance_and_not_the_canonical_model()
    {
        var instantiate = Patch.GetMethod("Instantiate", HeadlessGame.All)!;
        var calls = Il.Calls(instantiate);
        // The call the base game's own reward path ends in, at RUN scope
        // because a reward goes into the deck (CompanionSlot.Roll mirrors it).
        Assert.Contains(calls, c => c.Contains("CreateCard"));
        Assert.Contains(calls, c => c == "CardCreationResult..ctor");

        // And the postfix hands nothing to a screen except through it.
        var postfix = Il.Calls(Postfix);
        Assert.DoesNotContain(postfix, c => c == "CardCreationResult..ctor");
        Assert.Contains(postfix, c => c.Contains("Instantiate"));
    }

    /// <summary>
    /// `EB-594`. POST-FIGHT REWARD SCREENS ONLY. <c>CreateForReward</c> also
    /// rolls Neow's options, a relic's "choose one of three" (Hefty Tablet) and
    /// a shop's stock; a floor number cannot tell those apart from the reward
    /// after a fight, which is the only screen this rule was written about. The
    /// gate is the same <c>CardCreationSource.Encounter</c> test the mod's four
    /// <c>TryModifyCardRewardOptions</c> hooks already ask.
    /// </summary>
    [Fact]
    public void The_rule_fires_on_the_post_fight_reward_screen_only()
    {
        Assert.Contains(Il.Calls(Postfix), c => c.Contains("get_Source"));
    }

    [Fact]
    public void The_spark_test_is_the_arms_own_declaration()
    {
        // `ISparkPricedCard` is what `SparkCost` and the playability gate
        // read, so this rule and the refusal a player meets cannot disagree
        // about which cards are Spark-priced.
        var priced = Patch.GetMethod("IsSparkPriced", HeadlessGame.All)!;
        Assert.Contains(Il.Calls(priced),
                        c => c.Contains("get_PrintedSparkPrice"));
        // And the arm really has rows to seed with: an offer rule whose pool
        // is empty is a rule that never fires.
        Assert.Contains(
            typeof(KleeOverhaulLaw).Assembly.GetTypes(),
            t => typeof(ISparkPricedCard).IsAssignableFrom(t) && !t.IsInterface);
    }
}
