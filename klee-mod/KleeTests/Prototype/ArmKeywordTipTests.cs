using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
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

    // ---- the SECOND runtime branch (`EB-479`, R258) -----------------------

    private static string EncoreBody()
    {
        var body = Tips.GetMethod("EncoreBody", HeadlessGame.All)
            ?? throw new System.InvalidOperationException(
                "ArmKeywordTips.EncoreBody is gone -- the Encore tip's arm "
              + "branch moved, and with it the only surface that states the "
              + "reframe's opening bank.");
        return (string)body.Invoke(null, System.Array.Empty<object>())!;
    }

    [Fact]
    public void Under_the_reframe_the_encore_tip_states_the_opening()
    {
        var was = FurinaReframe.Enabled;
        try
        {
            FurinaReframe.Enabled = true;

            var body = EncoreBody();

            // R258's whole content, with the amount READ from the law rather
            // than typed, so a repricing moves the expectation and the
            // sentence together (`EB-89`, the Spark tip's rule above).
            Assert.Contains(
                "Start each combat with " + FurinaReframeLaw.OpeningEncore
                + ".", body);
            // And the three things that spend it are still named, which is
            // what `EB-407` put on this tip in the first place.
            Assert.Contains("After [gold]Block[/gold] it absorbs damage "
                            + "before HP.", body);
            Assert.Contains("a card pays", body);
            Assert.Contains("a member spends 1 or acts at 3/4.", body);
        }
        finally
        {
            FurinaReframe.Enabled = was;
        }
    }

    [Fact]
    public void With_the_arm_off_the_encore_tip_claims_no_opening()
    {
        // The shipped kit grants none, so the release sentence stands exactly
        // as `EB-407` wrote it -- a tip that promised an opening bank the kit
        // does not hand out is the same class of defect as explaining one
        // arm's word with the other arm's rules.
        var was = FurinaReframe.Enabled;
        try
        {
            FurinaReframe.Enabled = false;

            var body = EncoreBody();

            Assert.DoesNotContain("Start each combat", body);
            Assert.Contains("One pool, as each lands: a card pays to resolve, "
                            + "a member spends 1 to perform or acts at 3/4.",
                            body);
        }
        finally
        {
            FurinaReframe.Enabled = was;
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

        // `EB-432` traded "one at a time" for the order it leaves out: an
        // order that names a first and a rest IS one at a time, and the pile
        // resolves in placement order with the aura going to the oldest.
        Assert.Contains("oldest first", printed);
        Assert.Contains("go off first", printed);
        Assert.Contains("the first takes the aura", printed);
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
        // read back: rule 1's rate, rule 7 ("only when"), R248's burden and,
        // since `EB-361`, rule 3's jump -- a Bomb whose enemy dies moves to a
        // survivor, which three round-10 seats met with no wording anywhere.
        // Rule 2's "all at once" is what those 33 characters cost, and the
        // `Set off` tip two tests up states it in full.
        //
        // `EB-536` ADDED THE MINE TO RULE 7's CLAUSE. "Goes off only when Set
        // off" was printed directly ABOVE the Mine tip, which says a Mine also
        // goes off before its enemy's hit, so two surfaces of one screen
        // contradicted each other and the r19 lane-2 seat read them that way.
        // The tip goes over its ceiling for it and `BombKey` is carried in
        // `tools/lint_text_conventions.py` by name with that reason.
        Assert.Contains("A charge on an enemy: grows ", printed);
        Assert.Contains(" a turn, goes off only when [gold]Set off[/gold], "
                      + "or as a [gold]Mine[/gold]. ", printed);
        // `EB-373` REWROTE THE FOURTH RULE'S CLAUSE. The fold is `FoldedMods`
        // and it reads two things off the target -- Vulnerable, and whichever
        // power sets the lowest damage cap -- so "takes the enemy's debuffs"
        // promised a Slow or a Flutter would move a Bomb, and the r9 seat
        // priced two fights on it. The reason those miss is what the clause
        // leads with now: a Bomb's hit is not an Attack. `EB-361`'s jump rule
        // shares the 135 characters with it: "their" and "to a survivor" paid.
        Assert.Contains("Not an Attack: only [gold]Vulnerable[/gold] and a cap "
                      + "move it.", printed);
        Assert.Contains("Kills move it on.", printed);

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

        // One key per attach, the rider included (`EB-378`).
        Assert.Equal(Attaches().Count(), keys.Count);
        Assert.Equal(keys.Count, keys.Distinct().Count());
        Assert.All(keys, k => Assert.StartsWith("KLEEMOD-ARM_", k));
        Assert.DoesNotContain("KLEEMOD-BOMB", keys);
        Assert.DoesNotContain("KLEEMOD-SWIRL_PREVIEW", keys);
    }

    [Fact]
    public void The_plan_word_states_both_aims_and_all_three_modifiers()
    {
        // `EB-380`. "Never a Minion" was flat and the rule is not:
        // `KokomiPlan.FrontTarget` skips a Minion for a SINGLE-TARGET Plan,
        // and `Aim.AllEnemies` walks every living body, decoys included -- the
        // r9 act-1 seat watched an `Exposed Flank+` Plan land on `Eye With
        // Teeth` while this sentence said it could not. And the modifier
        // clause named two of three: the carry-out is an UNPOWERED
        // `ElementalHit`, so her Strength does not ride it either, and the
        // same seat priced `Kurage's Oath+` at Plan 10 under Vajra expecting
        // it would.
        var body = Printed("ForPlan");
        Assert.Contains("front non-", body);
        Assert.Contains("Minion", body);
        Assert.Contains("or ALL", body);
        Assert.Contains("Enemy ", body);
        Assert.Contains("Vulnerable", body);
        Assert.Contains("Weak", body);
        Assert.Contains("Strength", body);
        Assert.DoesNotContain("never a Minion", body);

        // The ceiling is the base game's own longest mechanic tip (CHANNELING,
        // 134), and this word is read on every battle screen of every run.
        // `Printed` concatenates every literal in the method, so the loc KEY
        // comes off before the markup does.
        // `EB-538` TOOK IT OVER, deliberately: the tip sat at exactly 135 and
        // gained the class a carry-out belongs to, which is `SetOffKey`'s own
        // sentence at the same call one kit over. Every clause here is a
        // seat's finding and none was droppable, so `PlanKey` is carried in
        // `tools/lint_text_conventions.py` by name. The length is pinned so
        // the overage cannot grow quietly.
        var rendered = System.Text.RegularExpressions.Regex.Replace(
            body.Replace(Tips.GetField("PlanKey")!.GetRawConstantValue()
                             as string ?? string.Empty, string.Empty),
            @"\[/?[a-z]+\]", string.Empty);
        Assert.Equal(186, rendered.Length);
        Assert.Contains("A carry-out is not a hit: no when-hit power fires.",
                        body);
    }

    [Fact]
    public void The_plan_element_rider_says_whose_hit_leaves_the_aura()
    {
        // `EB-378`. `KokomiPlan.ResolveAll` deals every damaging Plan clause as
        // `ElementalHit.Deal(..., Element.Hydro, ...)` whatever the card's
        // type, so a SKILL's Plan leaves a Hydro aura -- and the r9 act-1 seat
        // watched one appear from "a card whose face says nothing about an
        // element". The card now declares the element; this says WHEN, which
        // is the half a gem cannot carry.
        var body = Printed("ForPlanElement");
        Assert.Contains("Its own hit applies no aura", body);
        Assert.Contains("Bake-Kurage", body);
        Assert.Contains("Hydro", body);
    }

    [Fact]
    public void The_coven_rider_names_all_three_limbs_of_the_kits_spark()
    {
        // `EB-418`. The r11 seat's one unreadable number: Spark 1 to 2 with no
        // Bomb going off, because `KleeCompanionSpark` mints on any play of one
        // of Klee's own Personal Companions and LAW:145 keeps that grant off
        // the Companion's own face. All three limbs print -- a sentence saying
        // only "makes a Spark" would leave a reacted upgraded play as
        // unreadable as the plain one was.
        var body = Printed("ForCovenSpark");
        Assert.Contains("Klee's own", body);
        Assert.Contains("Companions", body);
        Assert.Contains("Spark", body);
        Assert.Contains("more if it triggered", body);
        Assert.Contains("Elemental Reaction", body);
        Assert.Contains("more if it is upgraded", body);

        // THE NUMERALS ARE THE POWER'S AND ARE NOT TYPED HERE (`EB-89`): each
        // limb is an `int` folded into the concat at runtime, so the literals
        // above carry no digit at all and a repricing moves the sentence with
        // the grant.
        Assert.Equal(1, KleeCompanionSpark.Base);
        Assert.Equal(1, KleeCompanionSpark.ReactionBonus);
        Assert.Equal(1, KleeCompanionSpark.UpgradedBonus);
        // The cap is the sum of the three limbs, so no reachable play can meet
        // a fourth clause and none is printed.
        Assert.Equal(KleeCompanionSpark.Base + KleeCompanionSpark.ReactionBonus
                     + KleeCompanionSpark.UpgradedBonus,
                     KleeCompanionSpark.MaxPerPlay);
    }

    [Fact]
    public void The_kits_spark_is_minted_where_the_rider_says_it_is()
    {
        // `EB-418`, the other half: the sentence is only true while the grant
        // is where it says. `Settle` is the mint and `Arm` decides whether it
        // fires, both keyed on `IsOwnPersonalCompanion` -- the row's own
        // `PersonalPool` against the player's character, which is the same pair
        // `gen_klee_cards` reads to decide which faces carry the sentence.
        var settle = typeof(KleeCompanionSpark)
            .GetMethod("Settle", HeadlessGame.All)!;
        Assert.Contains(Il.Calls(settle),
                        c => c.EndsWith("SparkPower.Gain",
                                        System.StringComparison.Ordinal));
        Assert.Contains("companion:personal/play", Il.Strings(settle));

        var arm = typeof(KleeCompanionSpark).GetMethod("Arm", HeadlessGame.All)!;
        Assert.Contains(
            Il.Calls(arm),
            c => c.EndsWith("KleeCompanionSpark.IsOwnPersonalCompanion",
                            System.StringComparison.Ordinal));
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

        // SIXTEEN: FOURTEEN KEYWORDS AND TWO RIDERS. Draft 6 cut Tide, Surge, Exert and the Garment as
        // keywords and their four `For*` methods left with the rules they
        // defined, taking the table from eleven to seven; the Furina reframe's
        // slice two put Deploy, Evoke and Drain on it (2026-09-02), and R244
        // put `Hexerei` on it -- the coven's family mark, which eighteen faces
        // printed while nothing defined it. `EB-372` put `Grounded` on it --
        // a Power of Klee's that Kaeya's Cold-Blooded Strike is written
        // against by name, met by a seat that had never drafted it. The number
        // is the TABLE's length (`gen_klee_cards.ARM_KEYWORDS`), which is what
        // the python half of this pin walks, so `ForGrounded` takes an
        // OPTIONAL card rather than adding a second entry point for the power
        // that raises it.
        //
        // THE THIRTEENTH IS `EB-378`'s `ForPlanElement`, which titles no keyword:
        // it is a sentence about a CARD whose Hydro arrives with the
        // jellyfish's carry-out rather than with the play. It goes through the
        // same `With`, which is what this pin is actually for.
        //
        // THE FOURTEENTH IS `EB-407`'s `ForEncore`, and it is the one word on
        // this table the arm did not invent. Encore is shipped machinery whose
        // only statement of itself is `EncoreMeterPower`'s badge, which renders
        // once the meter is on the board -- and the word is printed on the Neow
        // screen and on opening-hand faces before that.
        //
        // THE FIFTEENTH IS `EB-418`'s `ForCovenSpark`, the second entry here
        // that titles no keyword: the Spark Klee's KIT mints on a play of one
        // of her own Personal Companions, which LAW:145 keeps off the
        // Companion's face and which therefore had no surface at all until the
        // r11 seat reported it as the one number it could not read.
        //
        // THE SIXTEENTH IS `EB-446`'s `ForOz`, `ForGrounded`'s shape: a name
        // one companion card is written against and a DIFFERENT one grants, so
        // the face that prints it carries the definition. The r7 seat played
        // Fischl -- Nightrider five times without learning what puts Oz out.
        Assert.Equal(16, attaches.Count);
        Assert.Contains(attaches, m => m.Name == "ForPlanElement");
        Assert.Contains(attaches, m => m.Name == "ForCovenSpark");
        Assert.All(attaches, m => Assert.Contains(
            Il.Calls(m), c => c.EndsWith("ArmKeywordTips.With",
                                         System.StringComparison.Ordinal)));
    }

    // --- `EB-504`: KLEE'S RULE ON A RUN THAT HAS NO KLEE IN IT --------------

    private static CardModel Owned<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    [Theory]
    [InlineData("klee", true)]
    [InlineData("kokomi", false)]
    [InlineData("furina", false)]
    public void EB504_klees_two_words_are_klees_runs_alone(
        string character, bool printed)
    {
        // `EB-504`, REOPENED 2026-09-05. The row was closed on the page
        // glossary off the r17 finding, and the r18 lane-2 seat then met the
        // same sentence on a CARD: "two Companion cards in a Kokomi run
        // printed 'Hexerei -- A Companion card that prints the word, and Klee
        // herself ... Cards of hers pay when you play one.' I could not tell
        // what is paid, by whom, or whether it applies to me at all, so I
        // refused both cards partly on that."
        //
        // THE WORD IS EVERYONE'S AND THE RULE IS KLEE'S. `Hexerei` rides
        // eighteen companion faces the whole roster can draft and its rule is
        // her Spark rider; `Oz` is named by Fischl's face, which every
        // character meets, and the Power that fields him is hers. So the tag
        // reaches every run and the rule reaches one -- which is what
        // `blindplay_notes._ARM_KEYWORD_CHARACTER` gates on the page side, and
        // this is the second source that gate could not see.
        //
        // ONE CARD, THREE OWNERS, because that is the whole variable: Albedo
        // is a Mondstadt Universal every character drafts, so nothing about
        // the card changes between the three rows.
        //
        // THE PREDICATE AND NOT THE MATERIALISED TIP: building a `HoverTip`
        // resolves a `LocString`, which needs the game's loc tables and is
        // outside the headless boundary (README). What a test CAN do is ask
        // the gate, and watch the gated call hand its inherited stack straight
        // back -- which is the observable half either way.
        var seat = character switch
        {
            "klee" => Seat.Klee(),
            "kokomi" => Seat.Kokomi(),
            _ => Seat.Furina(),
        };
        var card = Owned<ProtoMcAlbedoSolarIsotoma>(seat);

        Assert.Equal(printed, ArmKeywordTips.KleesRuleBelongsHere(card));

        var inherited = System.Array.Empty<IHoverTip>();
        Assert.Equal(!printed,
            ReferenceEquals(inherited, ArmKeywordTips.ForHexerei(inherited, card)));
        Assert.Equal(!printed,
            ReferenceEquals(inherited, ArmKeywordTips.ForOz(inherited, card)));
    }

    [Fact]
    public void EB504_silence_about_the_character_still_prints_the_rule()
    {
        // The page's own direction (`absent is not zero`): where NOTHING says
        // who is playing -- a canonical compendium copy, which ASSERTS on
        // `Owner` rather than answering, with no run to read either -- the rule
        // prints. A missing tooltip on a Klee run is the worse of the two
        // failures, and it is the one this default avoids.
        Assert.True(ArmKeywordTips.KleesRuleBelongsHere(
            new ProtoMcAlbedoSolarIsotoma()));
    }

    [Fact]
    public void EB504_both_words_ask_the_one_gate()
    {
        // Structural, `Every_keyword_goes_through_the_one_attach_point`'s
        // shape: two words, one predicate, so a third word whose rule belongs
        // to one character cannot arrive with its own copy of the question.
        foreach (var word in new[] { "ForHexerei", "ForOz" })
        {
            Assert.Contains("ArmKeywordTips.KleesRuleBelongsHere",
                            Il.Calls(Il.Method("ArmKeywordTips", word)));
        }
    }
}
