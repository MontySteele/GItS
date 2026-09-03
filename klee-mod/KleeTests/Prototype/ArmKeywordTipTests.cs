using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.HoverTips;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-272`: the quarantined arms' keyword tips.
///
/// WHAT IS REACHABLE HERE. Enumerating a tip end to end is NOT: every yielded
/// <c>HoverTip</c> formats a <c>LocString</c> title through
/// <c>LocManager.Instance</c>, which is null until the game boots (README, the
/// headless boundary; <c>CanonicalHoverTipTests</c> records the same). What IS
/// reachable is every DECISION the tips make -- the one runtime branch, the
/// sentences read off the compiled methods, the keys, and the single attach
/// point -- so that is what this file pins, on the real shipped assembly.
///
/// THE TITLE ROWS ARE NOT PINNED HERE. <c>KeywordTitleRowTests</c> finds every
/// `KLEEMOD-` key in the assembly BY REFLECTION and demands a registered
/// `.title` row for it, so these eleven are already covered by the rule that
/// exists for exactly this failure -- a keyword shipping as its own raw loc key
/// (0.2-589, 0.2-634). A second list here would be a second list to forget.
///
/// THE ATTACH RULE IS PINNED IN PYTHON (`tier0/tests/test_arm_keyword_tips.py`),
/// because it is the generator's: which faces owe which tip is decided by
/// `gen_klee_cards.arm_keyword_tip_calls` reading the row's own description.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class ArmKeywordTipTests
{
    private static readonly System.Type Tips = typeof(ArmKeywordTips);

    /// <summary>Every public `For&lt;Word&gt;` entry point.</summary>
    private static IEnumerable<MethodInfo> Attaches() => Tips
        .GetMethods(BindingFlags.Public | BindingFlags.Static)
        .Where(m => m.Name.StartsWith("For", System.StringComparison.Ordinal)
                 && m.ReturnType == typeof(IEnumerable<IHoverTip>));

    /// <summary>The literal text one attach method prints. Adjacent string
    /// constants are folded by the compiler, so each sentence below is a
    /// single `ldstr` and reading them needs no ordering.</summary>
    private static string Printed(string method) => string.Concat(
        Il.Strings(Tips.GetMethod(method, HeadlessGame.All)!));

    private static string SparkBody()
    {
        var body = Tips.GetMethod("SparkBody", HeadlessGame.All)
            ?? throw new System.InvalidOperationException(
                "ArmKeywordTips.SparkBody is gone -- the Spark rule moved.");
        return (string)body.Invoke(null, System.Array.Empty<object>())!;
    }

    // ---- the one runtime branch -------------------------------------------

    [Fact]
    public void Under_the_overhaul_the_spark_tip_states_the_kit_rule()
    {
        var was = KleeOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = true;

            var body = SparkBody();

            // Rule 4, with the opening bank READ from the law rather than
            // typed, so a repricing moves the expectation and the sentence
            // together (`EB-89`). The per-explosion RATE is stated once, on
            // Pounding Surprise, and the tip names the relic instead of
            // restating it: two statements of one income is what the r4 seat
            // double-counted (`EB-291`).
            Assert.Contains(
                "Start each combat with " + KleeOverhaulLaw.OpeningSpark
                + ". Pounding Surprise grants more.", body);
            Assert.DoesNotContain("whenever a [gold]Bomb[/gold] goes off",
                                  body);
            Assert.Contains("Gone after combat.", body);
        }
        finally
        {
            KleeOverhaul.Enabled = was;
        }
    }

    [Fact]
    public void With_the_arm_off_the_spark_tip_claims_no_kit_gain()
    {
        // The Sparks arm prints `Spark` on twelve faces of its own, and under
        // THAT arm the gain is Pounding Surprise's -- a relic's body, not a kit
        // rule. A flat sentence would have explained one arm's word with the
        // other arm's rules, which is the class of defect this row is about.
        var was = KleeOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = false;

            var body = SparkBody();

            Assert.DoesNotContain("whenever a [gold]Bomb[/gold] goes off",
                                  body);
            // R242 pick 1's opening bank is the overhaul's rule too, so the
            // Sparks arm must not claim it either.
            Assert.DoesNotContain("Start each combat", body);
            Assert.DoesNotContain("Pounding Surprise", body);
            // And the half that is true on BOTH arms is still said: the
            // alternative cost is live in every prototype build.
            Assert.False(SparkPower.BaseRuleActive);
            Assert.Contains(
                "Some cards cost [gold]Sparks[/gold] instead of Energy, with no "
                + "cap.", body);
            Assert.Contains("Gone after combat.", body);
        }
        finally
        {
            KleeOverhaul.Enabled = was;
        }
    }

    // ---- the two sentences the row names ----------------------------------

    [Fact]
    public void The_mend_tip_carries_the_entry_hp_bound()
    {
        // THE ROW'S SECOND HALF. The Casket read as broken at full HP because
        // a Mend at the ceiling does nothing and nothing on screen said there
        // was a ceiling. The sentence is `KokomiRules.Mend`'s own.
        Assert.Contains("never above the HP you entered the fight with",
                        Printed("ForMend"));
    }

    [Fact]
    public void The_set_off_tip_states_the_order_the_explosions_land_in()
    {
        // [USER], on the dev build: "Set Off has no tooltip text." The ORDER
        // clause is the half a player cannot infer from watching -- the
        // explosions resolve BEFORE the rest of the card.
        var printed = Printed("ForSetOff");

        Assert.Contains("one at a time", printed);
        Assert.Contains("goes off first", printed);
    }

    [Fact]
    public void The_bomb_tip_says_the_arm_s_rule_and_not_the_shipped_one()
    {
        // The shipped `BombPower` detonates at the start of your turn and
        // early on unblocked damage; the arm's never goes off by itself. Two
        // words, one spelling -- and this is the tip that would be read as the
        // other one if the two were ever merged.
        var printed = Printed("ForBomb");

        // `EB-343` rewrote the word rather than adding to it. It gained a
        // fourth rule and the four sentences it had would have put it 60
        // characters over a ceiling that is the base game's own longest
        // mechanic tip, on the one word a seat reads every turn ([USER], PR
        // #340). All four rules survive the compression, which is what these
        // read back: rule 1's rate, rule 7 ("only when"), rule 2's "all at
        // once", and R248's burden.
        Assert.Contains("A charge on an enemy: grows ", printed);
        Assert.Contains(" a turn, goes off only when [gold]Set off[/gold], "
                      + "all at once.", printed);
        Assert.Contains("Its hit takes the enemy's debuffs, not yours.",
                        printed);

        // `EB-89`, read the only way it can be read: the growth rate is NOT a
        // literal anywhere in this method -- the two halves of the sentence are
        // separate `ldstr`s with a `string.Concat` between them, which is what
        // an interpolated constant compiles to and what a hand-typed numeral
        // would not. A repricing therefore cannot leave the tip lying.
        Assert.DoesNotContain(KleeOverhaulLaw.BombGrowth.ToString(), printed);
        Assert.Contains(Il.Calls(Tips.GetMethod("ForBomb", HeadlessGame.All)!),
                        c => c.Contains("Concat"));
    }

    // ---- the shape --------------------------------------------------------

    [Fact]
    public void Every_arm_key_is_its_own_and_none_shadows_a_shipped_keyword()
    {
        // `Bomb` and `Swirl` are the same WORD under two different rules
        // (`KLEEMOD-BOMB` detonates by itself; `KLEEMOD-SWIRL_PREVIEW` is a
        // board-aware preview). A shared key would have let one definition
        // overwrite the other at the loc merge, silently.
        var keys = Tips
            .GetFields(BindingFlags.Public | BindingFlags.Static)
            .Where(f => f.IsLiteral && f.FieldType == typeof(string))
            .Select(f => (string)f.GetRawConstantValue()!)
            .ToList();

        Assert.Equal(Attaches().Count(), keys.Count);
        Assert.Equal(keys.Count, keys.Distinct().Count());
        Assert.All(keys, k => Assert.StartsWith("KLEEMOD-ARM_", k));
        Assert.DoesNotContain("KLEEMOD-BOMB", keys);
        Assert.DoesNotContain("KLEEMOD-SWIRL_PREVIEW", keys);
    }

    [Fact]
    public void Every_keyword_goes_through_the_one_attach_point()
    {
        // Structural pin. `With` yields the INHERITED list first and its own
        // tip last, so a card's live arithmetic (a reaction preview, the Charge
        // rate, the Garment window) stays at the top of the stack and the
        // definition of a word is read second. One builder means a new keyword
        // cannot arrive with a different shape by accident.
        var attaches = Attaches().ToList();

        // TEN. Draft 6 cut Tide, Surge, Exert and the Garment as keywords and
        // their four `For*` methods left with the rules they defined, taking
        // the table from eleven to seven; the Furina reframe's slice two put
        // Deploy, Evoke and Drain on it (2026-09-02). The number is the
        // TABLE's length (`gen_klee_cards.ARM_KEYWORDS`), which is what the
        // python half of this pin walks.
        Assert.Equal(10, attaches.Count);
        Assert.All(attaches, m => Assert.Contains(
            Il.Calls(m), c => c.EndsWith("ArmKeywordTips.With",
                                         System.StringComparison.Ordinal)));
    }
}
