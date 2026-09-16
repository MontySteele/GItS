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
            // TRIMMED 2026-09-08 ([USER]'s run 2, an E default): the
            // relic pointer left the word. The relic's own face is where the
            // per-explosion rate has always been stated, so nothing about the
            // income stopped being printed -- the tip stopped pointing at it.
            Assert.Contains(
                "Start each combat with " + KleeOverhaulLaw.OpeningSpark
                + ". Gone after combat.", body);
            Assert.DoesNotContain("Pounding Surprise", body);
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

    [Fact]
    public void The_encore_tip_names_what_spends_the_pool()
    {
        // `EB-407`'s sentence, and no opening bank in it: the shipped kit
        // grants none, and the arm that did is retired (`EB-726`).
        var body = (string)(Tips.GetMethod("EncoreBody", HeadlessGame.All)
            ?? throw new System.InvalidOperationException(
                "ArmKeywordTips.EncoreBody is gone."))
            .Invoke(null, System.Array.Empty<object>())!;

        Assert.DoesNotContain("Start each combat", body);
        Assert.Contains("After [gold]Block[/gold] it absorbs damage "
                        + "before HP.", body);
        Assert.Contains("One pool, as each lands: a card pays to resolve, "
                        + "a member spends 1 to perform or acts at 3/4.",
                        body);
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
        //
        // TRIMMED 2026-09-08 ([USER]'s run 2, an E default: "a lot of
        // unnecessary tooltip text that could be trimmed"). Every rule read
        // back here is still on the word; what left is the prose around them.
        Assert.Contains(" a turn, and goes off when [gold]Set off[/gold] "
                      + "or as a [gold]Mine[/gold]. ", printed);
        // `EB-373` REWROTE THE FOURTH RULE'S CLAUSE. The fold is `FoldedMods`
        // and it reads two things off the target -- Vulnerable, and whichever
        // power sets the lowest damage cap -- so "takes the enemy's debuffs"
        // promised a Slow or a Flutter would move a Bomb, and the r9 seat
        // priced two fights on it. The reason those miss is what the clause
        // leads with now: a Bomb's hit is not an Attack. `EB-361`'s jump rule
        // shares the 135 characters with it: "their" and "to a survivor" paid.
        // `EB-555` DEFINED THE CAP inside that clause, because the word was
        // printed on two tips of one screen and defined on neither.
        // `EB-400` NAMED BLOCK in the same clause: the list read as the only
        // two things that touch the hit, and Block was outside it.
        // The 2026-09-08 trim dropped the "Not an Attack" negative, which
        // two seats misread anyway, and says "the HP cap" where the clause
        // used to spend a phrase on whose HP it is.
        Assert.Contains("[gold]Block[/gold] stops it. Only "
                      + "[gold]Vulnerable[/gold] and the HP cap move it.",
                        printed);
        Assert.DoesNotContain("Not an Attack", printed);
        // `EB-574` SPELT RULE 3 OUT. "Kills move it on" read as a promise
        // about the charge doing the killing: the r21 lane-1 seat set off
        // Mine 11, killed Toadpole B and saw nothing arrive on A. Same words
        // here, on the Mine tip and on the badge, so no two can be read
        // against each other.
        Assert.Contains("If the enemy dies with it on, it moves to a "
                      + "survivor.", printed);

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
        Assert.Contains("Vulnerable", body);
        // `EB-599` REVERSED THE MODIFIER CLAUSE, because the rule moved: the
        // line folds HER Strength when the Plan is written and nothing of the
        // target's, since a Plan resolves next morning against whatever the
        // body wears then. The r22 lane-2 seat paid for a "Plan: Deal 10"
        // that arrived as 7 once that Vulnerable had expired. `Weak` stays
        // off the sentence -- `powered: false` at the carry-out answers for
        // every other term of hers at once.
        Assert.Contains("folds as you write it", body);
        // `EB-623`: "morning" is retired from every printed surface.
        Assert.Contains("counts next turn", body);
        Assert.DoesNotContain("morning", body);
        Assert.DoesNotContain("Weak", body);
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
        // `EB-599` PUT 31 BACK for a rule a class name cannot state: the line
        // folds her Strength at writing time and nothing of the target's, so
        // the clause is about WHEN each side is read.
        // `EB-623` TOOK FIVE OFF for free: "counts at the morning" became
        // "counts next turn", the same fact in the base game's timing words.
        // `EB-330` / `EB-563` / `EB-411` TOOK 81 MORE in one rewrite: how
        // many Plans wait and what the badge's number is, and where a
        // carry-out lands. All three were on the blind-play panel and nowhere
        // in the game.
        Assert.Equal(292, rendered.Length);
        Assert.Contains("A carry-out is not a hit: no when-hit power fires.",
                        body);
    }

    [Fact]
    public void The_plan_word_says_any_number_wait_and_the_badge_is_their_count()
    {
        // `EB-563` and `EB-330`, one sentence filed as two. Three r4c seats
        // read the `Plan` badge's number as a CAPACITY, and the r20 lane-2
        // seat wrote ONE Plan at a time for four fights before trying two.
        // `KokomiPlan` caps nothing on an unconfigured build. The panel has
        // said so since `EB-648` (`blindplay_notes.PLAN_COUNT_NOTE`); a seat
        // reading a card in hand never reaches the panel, which is the gap.
        var body = Printed("ForPlan");
        Assert.Contains("any number wait, in ", body);
        Assert.Contains("order, and the badge is their count", body);
    }

    [Fact]
    public void The_plan_word_says_a_carry_out_lands_in_standing_block()
    {
        // `EB-411`. A Plating 8 Sewer Clam ate a whole Plan and no screen in
        // the game said it would (Kokomi r10 run 2 (c) 4). The morning
        // resolves before the player has played a card and an enemy's Block
        // falls at ITS turn start, so whatever it raised on its own turn is
        // still standing and no move strips it first. Panel twin:
        // `blindplay_notes.PLAN_BLOCK_NOTE`.
        var body = Printed("ForPlan");
        Assert.Contains("still standing", body);
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
        // Bomb going off, because `KleeCompanionSpark` mints on any play of a
        // Hexerei Companion and LAW:145 keeps that grant off
        // the Companion's own face. All three limbs print -- a sentence saying
        // only "makes a Spark" would leave a reacted upgraded play as
        // unreadable as the plain one was.
        var body = Printed("ForCovenSpark");
        // `EB-642`: the rider names the MARK, not the pool -- R265 pick 1 made
        // the printed word the whole rule, so the sentence points at the same
        // word the face above it prints.
        Assert.Contains("Hexerei", body);
        Assert.DoesNotContain("Klee's own", body);
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
        // fires, both keyed on `PaysKleesSpark` -- the row's family mark
        // against the player's character (`EB-642`, `EB-434`), which is the
        // same read `gen_klee_cards` makes to decide which faces carry the
        // sentence.
        var settle = typeof(KleeCompanionSpark)
            .GetMethod("Settle", HeadlessGame.All)!;
        Assert.Contains(Il.Calls(settle),
                        c => c.EndsWith("SparkPower.Gain",
                                        System.StringComparison.Ordinal));
        Assert.Contains("companion:personal/play", Il.Strings(settle));

        var arm = typeof(KleeCompanionSpark).GetMethod("Arm", HeadlessGame.All)!;
        Assert.Contains(
            Il.Calls(arm),
            c => c.EndsWith("KleeCompanionSpark.PaysKleesSpark",
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

        // SEVENTEEN KEYWORDS AND FOUR RIDERS (`EB-625` made the words
        // fifteen; `EB-726` took `ForOpeningStage` with the retired reframe). Originally: SIXTEEN, FOURTEEN KEYWORDS AND TWO RIDERS. Draft 6 cut Tide, Surge, Exert and the Garment as
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
        //
        // THE SEVENTEENTH IS `EB-575`'s `ForEmptyField`, the fourth entry that
        // titles no keyword and the FIRST whose sentence comes and goes with
        // the board. A `Set off` row or the merge played with no Bomb anywhere
        // is accepted, charges its Energy and its Spark, and resolves its own
        // line or nothing at all -- while a Spark-priced card the bank is
        // short for prints CANNOT BE PLAYED on the same screen (Klee r21 lane
        // 1). It goes through the same `With`, twice: which of its two
        // sentences a row gets is derived from the row's effects.
        //
        // THE NINETEENTH IS `EB-573`'s `ForMergeRiders`, the fifth entry that
        // titles no keyword: what a merge keeps besides the Mine. Careful
        // Arrangement's face promises "a Mine if any of them was" and says
        // nothing about riders, while the merge sums `PayloadMineAll` across
        // every charge it takes -- so Jumpy Dumpty's Mine-on-ALL survives it
        // and grows in bulk (Klee r21 lane 1, "completely undiscoverable
        // except by accident").
        //
        // THE TWENTIETH IS `EB-625`'s `ForCasket`, and it IS a keyword: the
        // relic Shell Guard's payout hangs off. "Whenever the Tamakushi
        // Casket strikes" named a thing nothing on screen defined, and
        // [USER]'s act-1 run read the card and asked how the Casket could
        // strike at all. `Grounded`'s shape and `Oz`'s, one kit over.
        //
        // THE TWENTY-FIRST IS `EB-643`'s `ForDusk`, the pool pass's one new
        // word and a rule about WHEN alone: the Bake-Kurage carries a Dusk
        // Plan out at the end of the turn it was written on, before the
        // enemies act. A word of its own rather than a sixth clause on the
        // Plan tip, which is at its ceiling and carries five seats' findings.
        //
        // THE TWENTY-SECOND TO THE TWENTY-EIGHTH ARE `EB-723`'s, and they
        // arrive as a set because the Stage brief's sec.12 names them as one:
        // "Tips the faces need: Spend, Fanfare (the bar), Raise, Bow, the
        // lead, the back performer, Rotate". Each is a rule the SHIPPED engine
        // does not have -- a shipped Fanfare is a METER and this one is a
        // performer's own bar -- so all seven belong on this quarantined
        // surface and none is a shipped keyword. Two of them are two words on
        // purpose: what `lead performer` and `back performer` carry is a rule
        // about WHICH SEAT, and a tip on the bare word "lead" would fire on
        // prose that meant something else.
        //
        // TWENTY-FIVE SINCE `EB-723`, and it was twenty-one. THREE LEFT and
        // SEVEN ARRIVED. `ForDeploy`, `ForEvoke` and `ForDrain` went with the
        // reframe's eleven `proto_fr_` rows under R213 B's deletion rule -- a
        // tooltip for a rule no row prints is a definition of a mechanic that
        // is not there. The seven are the Stage brief's own list (sec.12):
        // `Spend`, `Fanfare`, `Raise`, `Bow`, `lead performer`, `back
        // performer` and `Rotate`, each naming a rule the shipped engine does
        // not have. `ForEncore` survived the cut and became the SIXTH attach
        // here that titles no keyword: no prototype face prints the word any
        // more, and every Furina row the Stage does not swap still does.
        //
        // THE TWENTY-SIXTH IS `EB-709`'s `ForPlanTwice`, and it is a RIDER
        // rather than a keyword -- `ForPlanElement`'s shape. Tide Wall paid 6
        // and then 9 under Second Wave and no face said whether the doubled
        // entry counted as one Plan or two for a per-Plan clause (Kokomi r31
        // lane 2). It counts as two, and the card that bends the count is
        // where the count is explained.
        //
        // THE TWENTY-SEVENTH IS THE STAGE READERS' `ForStageReader`, a RIDER
        // and the SECOND whose sentence comes and goes with the screen
        // (`ForEmptyField` is the first). The four readers multiply a LIVE
        // bar, so off a board their faces print a literal 0 -- "Deal 0 damage
        // to ALL enemies" on the Rare at Neow, "Deal 0 damage" on `Ousia
        // Surge` at a reward -- and two round-three seats turned the Rare down
        // on it. The face cannot say otherwise: a description is a loc string
        // injected once at boot. It goes through the same `With`, four times
        // over: which of its four rules a row gets is derived from the
        // multiplier `EB-747` picked for that row's payoff.
        Assert.Equal(26, attaches.Count);
        Assert.Contains(attaches, m => m.Name == "ForStageReader");
        Assert.Contains(attaches, m => m.Name == "ForPlanTwice");
        Assert.Contains(attaches, m => m.Name == "ForSpend");
        Assert.Contains(attaches, m => m.Name == "ForFanfare");
        Assert.Contains(attaches, m => m.Name == "ForRaise");
        Assert.Contains(attaches, m => m.Name == "ForBow");
        Assert.Contains(attaches, m => m.Name == "ForLeadPerformer");
        Assert.Contains(attaches, m => m.Name == "ForBackPerformer");
        Assert.Contains(attaches, m => m.Name == "ForRotate");
        Assert.Contains(attaches, m => m.Name == "ForDusk");
        Assert.Contains(attaches, m => m.Name == "ForCasket");
        Assert.Contains(attaches, m => m.Name == "ForPlanElement");
        Assert.Contains(attaches, m => m.Name == "ForCovenSpark");
        Assert.Contains(attaches, m => m.Name == "ForEmptyField");
        Assert.Contains(attaches, m => m.Name == "ForMergeRiders");
        Assert.All(attaches, m => Assert.Contains(
            Il.Calls(m), c => c.EndsWith("ArmKeywordTips.With",
                                         System.StringComparison.Ordinal)));
    }

    // --- `EB-573`: WHAT THE MERGE KEEPS BESIDES THE MINE --------------------

    [Fact]
    public void EB573_the_merge_row_says_riders_survive_it()
    {
        Assert.Contains(
            Il.Calls(Il.Method("ProtoKoCarefulArrangement",
                               "get_ExtraHoverTips")),
            c => c.Contains("ForMergeRiders"));
        var body = Printed("ForMergeRiders");
        Assert.Contains("The merged [gold]Bomb[/gold] keeps every rider its "
                      + "charges carried, and their riders add up.", body);
    }

    [Fact]
    public void EB573_the_badge_counts_the_rider_it_is_carrying()
    {
        // The RULE is on the card and the NUMBER is on the pile: a Bomb 21
        // that was Jumpy's Bomb 8 two merges ago still drops Mine 3 on ALL,
        // and the badge is where a player meets that pile.
        ProtoBombPower.Register.Rebase(null);
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        ProtoBombs.Board(klee.Creature, enemy);

        var plain = ProtoBombs.Place(enemy, klee.Creature,
                                     new ProtoBombs.Charge(8));
        Assert.Equal(0, plain.PayloadTotal);
        Assert.DoesNotContain("Rider", LocKeyOf(plain));

        var rider = ProtoBombs.Place(enemy, klee.Creature,
                                     new ProtoBombs.Charge(8, PayloadMineAll: 3),
                                     new ProtoBombs.Charge(5, PayloadMineAll: 2));
        // THE SUM, which is what `MergeAllTo` builds and `Explode` pays out.
        Assert.Equal(5, rider.PayloadTotal);
        Assert.Contains("Rider", LocKeyOf(rider));
        ProtoBombPower.Register.Rebase(null);
    }

    private static string LocKeyOf(ProtoBombPower pile) =>
        (string)typeof(ProtoBombPower)
            .GetProperty("SmartDescriptionLocKey", HeadlessGame.All)!
            .GetValue(pile)!;

    // --- `EB-575`: THE BOARD A SET OFF NEEDS, AND WHAT IT DOES WITHOUT IT --
    //
    // THE FIND (Klee r21 lane 1, (c) 2 and (c) 3). Careful Arrangement on a
    // bare board and Fwoosh! on another were both ACCEPTED: the Energy went,
    // the Spark went, and nothing resolved. "A blank that the game charges you
    // for" -- while a Spark-priced card the bank is short for prints CANNOT BE
    // PLAYED on the same screen and names the price and the bank.

    [Fact]
    public void EB575_a_set_off_and_a_merge_carry_the_empty_field_rider()
    {
        // THE ATTACH IS THE GENERATOR'S and it is derived from the row's
        // effects, so the pin is that the two faces the seat played carry it.
        // `EB-749` cut Fwoosh! and Fireworks Show; Pocket Match is the same
        // Spark-priced Set off shape, and Tinder Toss carries Fireworks Show's
        // board-wide line.
        foreach (var card in new[] { "ProtoKoCarefulArrangement", "ProtoKoPocketMatch",
                                     "ProtoKoTheBigOne", "ProtoKoTinderToss" })
        {
            Assert.Contains(Il.Calls(Il.Method(card, "get_ExtraHoverTips")),
                            c => c.Contains("ForEmptyField"));
        }
    }

    [Fact]
    public void EB575_the_rider_prints_on_a_bare_board_and_not_on_a_cooked_one()
    {
        // A REAL BOARD, and the whole question this rider asks:
        // `ProtoBombPower.AnyPlacedBy`, which is the same read Set off's
        // playability gate makes (it was Grounded's too until `EB-749`).
        ProtoBombPower.Register.Rebase(null);
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        ProtoBombs.Board(klee.Creature, enemy);

        var merge = Owned<ProtoKoCarefulArrangement>(klee);
        var setOff = Owned<ProtoKoPocketMatch>(klee);
        var none = System.Linq.Enumerable.Empty<IHoverTip>();

        // THE PREDICATE AND NOT THE MATERIALISED TIP, `EB-504`'s rule one test
        // down: building a `HoverTip` formats a `LocString` through a
        // `LocManager` that is null until the game boots. What a test CAN do
        // is ask the gate, and watch the gated call hand its inherited stack
        // straight back -- which is the observable half either way.
        Assert.True(ArmKeywordTips.FieldIsEmptyFor(merge));
        Assert.True(ArmKeywordTips.FieldIsEmptyFor(setOff));
        Assert.NotSame(none, ArmKeywordTips.ForEmptyField(none, merge, false));
        Assert.NotSame(none, ArmKeywordTips.ForEmptyField(none, setOff, true));

        // COOKED: silent. The sentence is about THIS board, so it goes when
        // the board it names goes, and the call hands the stack straight back.
        ProtoBombs.Place(enemy, klee.Creature, new ProtoBombs.Charge(6));
        Assert.False(ArmKeywordTips.FieldIsEmptyFor(merge));
        Assert.False(ArmKeywordTips.FieldIsEmptyFor(setOff));
        Assert.Same(none, ArmKeywordTips.ForEmptyField(none, merge, false));
        Assert.Same(none, ArmKeywordTips.ForEmptyField(none, setOff, true));

        // AND OFF A BOARD ENTIRELY -- a reward, a shop, a deck view -- there is
        // no field to be empty and the rider says nothing.
        Assert.False(ArmKeywordTips.FieldIsEmptyFor(new ProtoKoPocketMatch()));
        ProtoBombPower.Register.Rebase(null);
    }

    [Fact]
    public void EB575_the_two_sentences_are_the_ruled_ones()
    {
        var body = Printed("ForEmptyField");
        // A ROW WITH A LINE OF ITS OWN still does that line (Pocket Match's
        // 5, Countdown's draw), and a row that is nothing but the Bomb work
        // does nothing whatever (Careful Arrangement, The Big One, Quick
        // Fuse). Saying either sentence on the other row would be
        // false, so both are printed and the generator picks.
        Assert.Contains("No [gold]Bomb[/gold] on the field: this card is only "
                      + "its own line.", body);
        Assert.Contains("No [gold]Bomb[/gold] on the field: this card does "
                      + "nothing.", body);
        // And the gate is the BOARD, asked once.
        Assert.Contains(
            Il.Calls(Il.Method("ArmKeywordTips", "FieldIsEmptyFor")),
            c => c.EndsWith("ProtoBombPower.AnyPlacedBy",
                            System.StringComparison.Ordinal));
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

    // --- a Stage round-three defect: the readers' 0 off the board ----------

    [Fact]
    public void The_stage_readers_tip_states_each_rule_and_the_absent_stage()
    {
        // THE FIND (round three). The four readers multiply a LIVE bar, so
        // off a board their faces print a literal 0 -- "Deal 0 damage to ALL
        // enemies" on the Rare at Neow, "Deal 0 damage" on `Ousia Surge` at a
        // reward -- and two seats turned the Rare down on it. The number is
        // right in combat and right at resolution (`EB-747`); what is wrong
        // is the screen with no stage behind it, and a description cannot fix
        // itself because it is a loc string injected once at boot.
        //
        // THE SENTENCES OFF THE COMPILED METHOD, this file's own rule: a
        // materialised `HoverTip` resolves a `LocString` through a
        // `LocManager` that is null until the game boots, so what is
        // reachable here is the text each branch would print.
        var body = Printed("ForStageReader");

        // One rule per reader, each read off that reader's own code.
        Assert.Contains(
            "The number is the [gold]lead performer[/gold]'s "
          + "[gold]Fanfare[/gold].", body);
        Assert.Contains(
            "The number is the [gold]back performer[/gold]'s "
          + "[gold]Fanfare[/gold].", body);
        Assert.Contains(
            "The number is the [gold]lead performer[/gold]'s "
          + "[gold]Fanfare[/gold], which this [gold]Bow[/gold] spends.", body);
        Assert.Contains(
            "The number is every performer's [gold]Fanfare[/gold] added up "
          + "and spent.", body);

        // And the clause that IS the defect, which the rule carries only
        // where there is no combat behind the card: in a fight the face is
        // already right and this sentence would be false.
        Assert.Contains(
            " There is no stage outside combat, so the number above reads 0.",
            body);
    }

    [Fact]
    public void The_readers_rider_yields_on_and_off_a_board_alike()
    {
        // UNLIKE `ForEmptyField`, WHICH GOES SILENT. That rider is a sentence
        // about a board in a particular state; this one is about what the
        // card's number IS, which is true on every screen -- and the screen
        // it was filed on is the one with no board at all.
        var none = System.Linq.Enumerable.Empty<IHoverTip>();
        var offTheBoard = new ProtoFsOusiaSurge();
        Assert.NotSame(none, ArmKeywordTips.ForStageReader(
            none, offTheBoard, ArmKeywordTips.StageReader.Lead));

        var furina = Seat.Furina();
        var inPlay = Owned<ProtoFsOusiaSurge>(furina);
        Assert.NotSame(none, ArmKeywordTips.ForStageReader(
            none, inPlay, ArmKeywordTips.StageReader.Lead));
    }
}
