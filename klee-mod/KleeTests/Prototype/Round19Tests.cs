using System;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Elements;
using BaseGame = MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Entities.Cards;
using BaseLib.Abstracts;
using System.Collections.Generic;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
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

    // ==================================================================
    // `EB-548` -- a performance is not a hit, `EB-538`'s twin
    // ==================================================================
    //
    // THE FIND (Furina r13 lane 2). Member performances bypass Skittish while
    // the enemy's own buff says "hit": "Chevalmarin hit C for 2 and C's HP
    // moved by 2 with no Block gained... the correct line against Skittish is
    // to spend the free perform first". The seat called it "the most useful
    // thing I learned and effectively invisible".
    //
    // THE SENTENCE WAS ALREADY THERE AND NAMED THE WRONG SIDE OF THE BOARD.
    // `EB-476` put "a performance is not an Attack: Vulnerable moves it,
    // Shatter and on-Attack triggers do not" on the Salon paragraph, which is
    // exactly `EB-490`'s finding one kit over: "on-Attack trigger" reads as
    // something on the PLAYER's side, and a player looking for the rule about
    // the thing on the ENEMY's status bar does not find it. Same call, same
    // rule, same words as Set off and the Plan.

    [Fact]
    public void The_salon_paragraph_says_a_performance_is_not_a_hit()
    {
        using var _ = new ReframeArm();
        var seat = Seat.Furina().WithCombatState();

        var rules = SalonMemberTips.SalonRulesBody(seat.Creature);

        Assert.Contains("not a hit", rules);
        Assert.Contains("no when-hit power fires", rules);
        // The Vulnerable half is untouched: the pair is the sentence, and
        // dropping either puts `EB-476`'s finding back.
        Assert.Contains("[gold]Vulnerable[/gold] moves it", rules);
        Assert.DoesNotContain("on-Attack triggers", rules);
    }

    [Fact]
    public void The_three_surfaces_say_it_in_the_same_words()
    {
        // ONE RULE AT ONE CALL, on the three words a player can meet it
        // through. A surface that said it differently would be a fourth rule
        // to learn, which is the whole of what `EB-490` was about.
        using var _ = new ReframeArm();
        var seat = Seat.Furina().WithCombatState();

        foreach (var surface in new[]
                 {
                     Printed(typeof(ArmKeywordTips), "ForSetOff"),
                     PlanTip(),
                     SalonMemberTips.SalonRulesBody(seat.Creature),
                 })
        {
            Assert.Contains("when-hit power", surface);
        }
    }

    [Fact]
    public void A_performance_hands_the_hit_no_attacker_either()
    {
        // The behavioural half, structural for the reason `EB-538`'s is:
        // `PerformMember` is the ONE implementation of a member acting and it
        // asks the same unpowered funnel a carry-out does, so neither can fire
        // a power keyed on being hit.
        Assert.Contains(Il.Calls(Il.Method("SalonMemberPower", "PerformMember")),
                        c => c == "ElementalHit.Deal");
        Assert.DoesNotContain(
            Il.Calls(Il.Method("SalonMemberPower", "PerformMember")),
            c => c.StartsWith("DamageCmd.", StringComparison.Ordinal));
    }


    // ==================================================================
    // `EB-533` -- Grounded says its answer either way
    // ==================================================================
    //
    // THE FIND (Klee r19 lane 1). The card was logged every turn: paid three
    // times, failed twice, and both failures were the turn after the seat had
    // detonated everything, which is the card's price rather than its trap.
    // What was missing was a line: "the two failures printed no near-miss
    // line, I caught it only by diffing my own Block".
    //
    // A LATCH, NOT A LIVE BOARD READ. The badge is read at RENDER time and the
    // condition is answered at TURN START, and the seat's failing turn is the
    // one they disagree on: detonate everything, Grounded pays nothing, then
    // place a fresh Bomb. A face that re-read the board would print "a Bomb is
    // on the field" over a turn that paid nothing -- a second silent failure
    // rather than a fix.

    [Fact]
    public void Grounded_carries_a_face_for_each_answer_and_neither_is_the_rule()
    {
        var rows = new GroundedPower().Localization!
            .ToDictionary(r => r.Item1, r => r.Item2);

        Assert.Contains("nothing was paid", rows["smartDescriptionUnpaid"]);
        Assert.Contains("[gold]Bomb[/gold]", rows["smartDescriptionUnpaid"]);
        Assert.Contains("paid", rows["smartDescriptionPaid"]);
        Assert.Contains("[gold]Spark[/gold]", rows["smartDescriptionPaid"]);

        // The static rule stays what it was: it is what the card promises, and
        // the two faces above are what it did.
        Assert.StartsWith("At the start of your turn,", rows["description"]);
    }

    [Fact]
    public void The_selector_picks_the_answer_the_power_last_gave()
    {
        // The key is the live choice for `ProtoBombPower`'s reason: loc is
        // registered once at boot and the board changes every turn. UNASKED is
        // its own key with no row, so a power played this turn and never yet
        // asked falls back to the static rule -- a badge claiming a failure the
        // power never had is the same defect pointing the other way.
        var power = new GroundedPower();
        var key = typeof(GroundedPower)
            .GetProperty("SmartDescriptionLocKey", All)!;
        // The latch is a FIELD and `Seat.Set` reaches properties, so it is set
        // by reflection here -- the value under test is the one the turn start
        // writes, and no public door onto it exists or should.
        var latch = typeof(GroundedPower).GetField("_paid", All)!;

        Assert.EndsWith(".smartDescriptionUnasked", (string)key.GetValue(power)!);

        latch.SetValue(power, false);
        Assert.EndsWith(".smartDescriptionUnpaid", (string)key.GetValue(power)!);

        latch.SetValue(power, true);
        Assert.EndsWith(".smartDescriptionPaid", (string)key.GetValue(power)!);
    }

    [Fact]
    public void Both_branches_of_the_turn_start_record_their_answer()
    {
        // STRUCTURAL, and read off the SOURCE because a field store is
        // invisible to `Il` -- `Round16Tests` reads a source file the same way
        // for the same reason. The claim is that the refusing branch records
        // BEFORE it returns, which is the one line of this method the row
        // moves: a `_paid = false` written after the return would compile and
        // print nothing.
        var body = Source("Powers/Prototype/KleeOverhaulPowers.cs")
            .Replace("\r\n", "\n");
        body = body[body.IndexOf("public sealed class GroundedPower",
                                 StringComparison.Ordinal)..];
        var refusal = body.IndexOf("&& !CompanionStandIns.GroundedBlind(Owner))",
                                   StringComparison.Ordinal);
        var returned = body.IndexOf("return;", refusal, StringComparison.Ordinal);
        var unpaid = body.IndexOf("_paid = false;", StringComparison.Ordinal);
        var paid = body.IndexOf("_paid = true;", StringComparison.Ordinal);

        Assert.True(unpaid > refusal && unpaid < returned,
                    "the refusing branch records its answer before returning");
        Assert.True(paid > returned, "the paying branch records its own");
    }

    // ==================================================================
    // `EB-534` -- what the merge does to a Mine, said on the face
    // ==================================================================
    //
    // TWO SEATS, OPPOSITE READS, AND THE FACE SAID NEITHER. Klee r18 lane 1
    // read Careful Arrangement as PRESERVING Mine status ("the body line said
    // so"); r19 lane 1 read it as converting Mines to plain Bombs and never
    // played the card ("worse than a blank card"). The face said only "as one
    // Bomb".
    //
    // THE ENGINES BOTH PRESERVE IT, and they always did: `MergeAllTo` folds
    // `isMine |= charge.IsMine` and `merge_all_to` does the same, because a
    // merge is a MOVE and a move must not silently delete the defence the
    // player set up (`EB-395`, pinned in `KleeOverhaulRuleTests` and
    // `test_klee_overhaul_rules`). So r18 was right, r19 was wrong, and the
    // fix is one clause on the card rather than anything in the fold.
    //
    // THE GROWTH-TICK PRICE STAYS ON THE KEYWORD. "Merging N Bombs into one
    // destroys N minus one growth ticks a turn" is the r19 seat's own
    // arithmetic and it is true, but it is a consequence of the Bomb tip's
    // "each grows N a turn" read over one pile instead of N -- a card says
    // what it does and nothing about why (text conventions, rule 15), and the
    // rule it would be restating is already on the word it prints.

    [Fact]
    public void Careful_arrangements_face_says_the_merged_pile_is_a_mine()
    {
        var face = string.Join(" ", Il.Strings(
            Il.Method("ProtoKoCarefulArrangement", "get_Localization")));

        Assert.Contains("as one [gold]Bomb[/gold]", face);
        Assert.Contains("[gold]Mine[/gold] if any of them was", face);
    }

    [Fact]
    public void And_the_fold_it_describes_is_the_one_the_arm_runs()
    {
        // The face is a claim about `MergeAllTo`, so it is checked against
        // `MergeAllTo`: the fold READS `IsMine` off every charge it moves, and
        // hands the result to the one placer. Structural for the reason every
        // Bomb pin is -- a merge needs a live `CombatState`.
        var il = Il.Calls(Il.Method("ProtoBombPower", "MergeAllTo"));

        Assert.Contains(il, c => c.Contains("get_IsMine"));
        Assert.Contains("ProtoBombPower.Place", il);
    }

    // ==================================================================
    // `EB-545` -- Feigned Retreat's planned Block is paid and printed
    // ==================================================================
    //
    // THE FIND (Kokomi r19 lane 1). "Its two halves point in opposite
    // directions": the seat read the Plan as adding damage but not Block,
    // against a face that says "Plan: Gain 4 Block and deal 6 damage". So
    // either the clause was not carried out or the morning block did not print
    // it.
    //
    // IT IS NEITHER. The Plan carries both clauses, in the order the face
    // prints them, and `ResolveOne`'s Block case RETURNS the Block it gained
    // -- which is what makes it the number on the carry-out line, labelled by
    // `NumberKind`, with the hit's own HP row under it. The seat's sentence is
    // about the FACE: the now-line and the Plan line print the same 4, so
    // waiting buys the damage and nothing more. That is the card's shape and a
    // design reading, and no payment moves for it.

    [Fact]
    public void Feigned_retreats_plan_carries_both_clauses_in_printed_order()
    {
        var card = new ProtoKkFeignedRetreat();
        var clauses = card.PlanClauses;

        Assert.Equal(2, clauses.Count);
        Assert.Equal(KokomiPlan.Kind.Block, clauses[0].Kind);
        Assert.Equal(4, clauses[0].Amount);
        Assert.Equal(KokomiPlan.Kind.Damage, clauses[1].Kind);
        Assert.Equal(6, clauses[1].Amount);

        // AND THE FACE PRINTS WHAT THE CLAUSES DO, which is the half the seat
        // was reading: the same 4 now and planned, plus the damage.
        var face = string.Join(" ", Il.Strings(
            Il.Method("ProtoKkFeignedRetreat", "get_Localization")));
        Assert.Contains("[gold]Plan[/gold]: Gain", face);
        Assert.Contains("[gold]Block[/gold] and deal", face);
    }

    [Fact]
    public void A_planned_block_is_paid_powered_and_is_the_number_on_the_line()
    {
        // The Block clause goes out through `CreatureCmd.GainBlock` and RETURNS
        // what it gained, so it is `number` on the carry-out line -- the first
        // clause that produces one wins, and this card's first clause is the
        // Block. `NumberKind` labels it, which is what puts "the 4 is Block" on
        // the page beside the hit's own HP row.
        var resolve = Il.Calls(Il.Method("KokomiPlan", "ResolveOne"));
        Assert.Contains("CreatureCmd.GainBlock", resolve);

        var announce = Il.Calls(Il.Method("KokomiPlan", "ResolveEntry"));
        Assert.Contains("KokomiPlan.NumberKind", announce);
        Assert.Contains("KokomiPlan.Announce", announce);
    }

    // ==================================================================
    // `EB-536` -- the hit clause is a fact about a stack, and the two
    //             Bomb tips stopped contradicting each other
    // ==================================================================
    //
    // TWO FINDINGS, ONE ROW (Klee r19 lane 2). `EB-514`'s new headline clause
    // "in 1 hit for as many Sparks" printed on EVERY Bomb block and "was never
    // comprehensible" -- and on a pile of one it is saying nothing, because
    // the total IS the hit and "as many" points back at a number the sentence
    // has already spent. And the Bomb tip's "goes off only when Set off" was
    // printed directly above the Mine tip, which says a Mine also goes off
    // before its enemy's hit: two surfaces of one screen contradicting each
    // other.

    [Fact]
    public void A_single_charge_headline_says_nothing_about_hits()
    {
        var pile = ProtoBombs.Place(Seat.Klee(60).Creature,
                                    Seat.Klee().Creature,
                                    new ProtoBombs.Charge(7));
        var face = pile.Localization!
            .First(r => r.Item1 == "smartDescriptionOne").Item2;

        Assert.DoesNotContain("{Count}", face);
        Assert.DoesNotContain("hit", face);
        // The rest of the face is untouched: the total, the queue and rule 3.
        Assert.Contains("[gold]Set off[/gold] here deals [blue]{Size}[/blue] "
                      + "Pyro damage.", face);
        Assert.Contains("Bombs here: [blue]{Charges}[/blue]", face);
    }

    [Fact]
    public void A_stack_still_names_its_hits_and_names_its_sparks()
    {
        var pile = ProtoBombs.Place(Seat.Klee(60).Creature,
                                    Seat.Klee().Creature,
                                    new ProtoBombs.Charge(4),
                                    new ProtoBombs.Charge(3));
        var face = pile.Localization!
            .First(r => r.Item1 == "smartDescription").Item2;

        // THE SPARK COUNT IS A NUMBER AGAIN. "For as many Sparks" asked the
        // reader to carry the hit count across a clause; the number carries
        // itself, and the plural is fixed because this face is only ever
        // chosen for two charges or more.
        Assert.Contains("in [blue]{Count}[/blue] hits for [blue]{Count}[/blue] "
                      + "[gold]Sparks[/gold].", face);
        Assert.DoesNotContain("as many", face);
        Assert.DoesNotContain("plural", face);
    }

    [Fact]
    public void The_live_face_follows_the_charge_count_off_the_board()
    {
        // The axis is READ, not assumed: the selector asks the live charge
        // list, so a stack that loses a charge becomes a single and a single
        // that gains one becomes a stack. `EB-289`'s var is what it asks --
        // the stack amount cannot be lowered by the pure takes.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(60).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
                                    new ProtoBombs.Charge(4),
                                    new ProtoBombs.Charge(6, IsMine: true));

        Assert.EndsWith(".smartDescriptionMines", LocKey(pile));
        pile.TakeMines();
        Assert.EndsWith(".smartDescriptionOne", LocKey(pile));
    }

    [Fact]
    public void The_bomb_tip_and_the_mine_tip_no_longer_disagree()
    {
        var bomb = Printed(typeof(ArmKeywordTips), "ForBomb");
        var mine = Printed(typeof(ArmKeywordTips), "ForMine");

        // The Bomb tip names the second door, so the Mine tip is not a
        // correction to it any more.
        Assert.Contains("goes off only when [gold]Set off[/gold], or as a "
                      + "[gold]Mine[/gold].", bomb);
        Assert.Contains("also goes off before its enemy's hit", mine);
    }

    /// <summary>The reframe's MANUAL leg on for one test, every flag back
    /// after it -- <c>FurinaRoundNineTests.Arm</c> verbatim, and for its
    /// reason: the six flags are process-global statics.</summary>
    private sealed class ReframeArm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;
        private readonly bool _evoke = FurinaReframe.EvokeEnabled;
        private readonly bool _meter = FurinaReframe.MeterEnabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;
        private readonly bool _burst = FurinaReframe.BurstEnabled;

        internal ReframeArm(bool master = true)
        {
            FurinaReframe.Enabled = master;
            FurinaReframe.ManualEnabled = master;
            FurinaReframe.EvokeEnabled = false;
            FurinaReframe.MeterEnabled = false;
            FurinaReframe.SpotlightEnabled = false;
            FurinaReframe.BurstEnabled = false;
        }

        public void Dispose()
        {
            FurinaReframe.Enabled = _enabled;
            FurinaReframe.ManualEnabled = _manual;
            FurinaReframe.EvokeEnabled = _evoke;
            FurinaReframe.MeterEnabled = _meter;
            FurinaReframe.SpotlightEnabled = _spotlight;
            FurinaReframe.BurstEnabled = _burst;
        }
    }

    // ---- helpers ---------------------------------------------------------

    // ==================================================================
    // `EB-535` -- the Hexerei word says what the payment is
    // ==================================================================
    //
    // THE FIND (Klee r19 lane 2). "I read this a dozen times across five
    // fights and I still do not know what it does. 'Cards of hers pay' -- pay
    // what, to whom, and when? I played Razor four times and never saw
    // anything I could attribute to Hexerei." The rule was on a DIFFERENT
    // screen the whole time -- the Companion Spark rider, which rides Klee's
    // own Personals and not the family tag -- and the seat found it late and
    // still could not tell whether Razor was one of Klee's own.

    [Fact]
    public void The_hexerei_word_names_the_spark_and_its_bound()
    {
        var hexerei = Printed(typeof(ArmKeywordTips), "ForHexerei");

        // THE NUMERALS ARE THE POWER'S AND ARE NOT TYPED HERE (`EB-89`), so
        // `Printed` -- which concatenates the LITERALS -- sees the sentence
        // with two holes in it. That is the pin: a typed digit would show up.
        Assert.Contains("Playing one of hers makes [blue][/blue] "
                      + "[gold]Spark[/gold], up to [blue][/blue].", hexerei);
        Assert.DoesNotContain("Cards of hers pay", hexerei);
        // The clauses that answer the seat's OTHER question -- whether Razor is
        // one of Klee's own -- are what paid for the room, and they stay.
        Assert.Contains("Some are Klee's own, some are not.", hexerei);
    }

    [Fact]
    public void The_numbers_are_the_kits_own_declaration_and_not_typed()
    {
        // `EB-89`'s rule: a retune of the rider must not leave this sentence
        // quoting a retired figure, so both numerals come off
        // `KleeCompanionSpark` -- which is the declaration LAW:145 obliges
        // Klee's KIT to make, and the same source `ForCovenSpark` reads.
        var hexerei = Printed(typeof(ArmKeywordTips), "ForHexerei");
        var coven = Printed(typeof(ArmKeywordTips), "ForCovenSpark");

        Assert.DoesNotContain(KleeCompanionSpark.Base.ToString(), hexerei);
        Assert.DoesNotContain(KleeCompanionSpark.MaxPerPlay.ToString(), hexerei);
        Assert.DoesNotContain(KleeCompanionSpark.Base.ToString(), coven);
        // AND THE VALUES THEMSELVES, so the sentence and the grant move
        // together: the cap is the sum of the three limbs, which is why the
        // rider prints no bound and this word does.
        Assert.Equal(1, KleeCompanionSpark.Base);
        Assert.Equal(KleeCompanionSpark.Base + KleeCompanionSpark.ReactionBonus
                     + KleeCompanionSpark.UpgradedBonus,
                     KleeCompanionSpark.MaxPerPlay);
        // THE BOUND IS ON THIS WORD AND NOT ON THE RIDER, deliberately: on the
        // rider it would state a ceiling no single clause reaches, and here it
        // is the whole of what a player asking "how much" needs.
        Assert.Contains("up to", hexerei);
        Assert.DoesNotContain("up to", coven);
    }

    [Fact]
    public void And_the_word_still_says_nothing_on_a_run_that_is_not_klees()
    {
        // `EB-504`'s gate is untouched: the tag rides eighteen faces the whole
        // roster can draft and the RULE is Klee's, so a Kokomi run meets the
        // word and not the sentence. A payment named on a run that cannot make
        // it would be the same defect `EB-504` closed, one clause louder.
        var body = Il.Method("ArmKeywordTips", "ForHexerei");
        Assert.Contains("ArmKeywordTips.KleesRuleBelongsHere", Il.Calls(body));
    }

    // ==================================================================
    // `EB-540` -- a Skill's damage spends no next-Attack buff
    // ==================================================================
    //
    // THE FIND (Kokomi r19 lane 2). "Ambush is a `skill` whose entire text is
    // 'Deal 5 damage.' Bennett buffs 'your next Attack', so Bennett's buff sat
    // unspent on my bar while Ambush hit. The card types are internally
    // consistent, but the faces give a blind reader no warning that a damage
    // card can fail to be an Attack." The seat played the buff and the Skill in
    // the same turn and read the result off its own status bar.
    //
    // THE SENTENCE IS ON THE BUFF, which is the surface the seat was reading
    // and the one whose class owns the rule: `NextAttackRiderPower` refuses on
    // the card TYPE in `BeforeCardPlayed`, and every subclass asks the same of
    // `cardSource`. A kit's keyword would have carried a rule that is not
    // about that kit -- the riders are Companion powers and reach every
    // character -- and would have said it on Kokomi's Plan cards only.
    //
    // AND IT SAYS THE NARROW TRUE THING. "A Skill's damage is not an Attack"
    // is one surface too wide: `EB-469`/`EB-481` measured the other half --
    // a Skill's damage clause is emitted as `ValueProp.Move`, so Weak cuts it
    // and Vulnerable raises it. What is true is the card TYPE.

    [Theory]
    [InlineData(typeof(PassionOverloadPower))]
    [InlineData(typeof(SwirlChargePower))]
    [InlineData(typeof(StarfrostDiscountPower))]
    [InlineData(typeof(CrowfeatherCoverPower))]
    public void Every_next_attack_rider_prints_the_card_type_rule(Type rider)
    {
        var power = (ILocalizationProvider)Activator.CreateInstance(rider)!;
        var face = power.Localization!
            .First(r => r.Item1 == "description").Item2;

        Assert.Contains("Only an Attack card spends it, never a Skill.", face);
        Assert.Contains("next Attack", face);
    }

    [Fact]
    public void The_clause_is_declared_once_on_the_class_that_owns_the_rule()
    {
        // FOUR FACES, ONE SENTENCE. A second copy is a second sentence to keep
        // in step, and the rule they are all describing is one method's.
        var clause = typeof(NextAttackRiderPower)
            .GetField("CardTypeClause", All)!.GetRawConstantValue() as string;
        Assert.Equal(" Only an Attack card spends it, never a Skill.", clause);

        Assert.Contains("CardModel.get_Type", Il.Calls(
            Il.Method("NextAttackRiderPower", "BeforeCardPlayed")));
    }

    [Fact]
    public void A_skills_damage_still_takes_weak_and_vulnerable()
    {
        // THE HALF THE CLAUSE DOES NOT CLAIM, pinned so a later rewording
        // cannot widen it into `EB-469`'s defect: a Skill's damage clause is
        // emitted as `ValueProp.Move`, which IS a powered attack, so the
        // target's and the dealer's terms read it. Only the card TYPE gate
        // refuses.
        Assert.True(ValueProp.Move.IsPoweredAttack());

        var vars = ((IEnumerable<DynamicVar>)typeof(ProtoKkKuragesOath)
            .GetProperty("CanonicalVars", All)!
            .GetValue(new ProtoKkKuragesOath())!).ToList();
        var damage = vars.OfType<DamageVar>().Single();

        Assert.Equal(CardType.Skill, new ProtoKkKuragesOath().Type);
        Assert.Equal(ValueProp.Move, damage.Props);
    }

    // ==================================================================
    // `EB-539` -- Well Laid's bare face, and the rider-tip split
    // ==================================================================
    //
    // THE FIND (Kokomi r19 lane 2). On a bare morning `Well Laid` printed
    // "Deal 2 damage, already including 3 for each Plan carried out this
    // morning", and the seat read it as self-contradictory: 2 cannot already
    // include a 3 that nothing paid.
    //
    // IT IS `EB-441`'s CLAUSE WORKING EXACTLY AS WRITTEN, on the one board
    // where the fold is zero -- the face's number IS live and the count IS
    // folded into it. What the row asked for is a face that says one thing at
    // count 0 and another above it, and the engine does not have one
    // (`Round16Tests.A_card_cannot_print_one_face_in_a_shop_and_another_in_a_fight`
    // checks that against the shipped `sts2.dll`).
    //
    // THE REMEDY IS THE CODEBASE'S OWN FOR THIS SHAPE: Undertow's
    // `ForDebuffRider` (`EB-484`), one count over. The FACE prints the live
    // total and nothing else; the RULE and the live count go on the rider tip.

    [Fact]
    public void EB539_well_laids_face_is_the_live_total_and_nothing_else()
    {
        var card = Source(
            "Cards/Prototype/Generated/ProtoKkWellLaid.cs");

        Assert.Contains(
            "(\"description\", \"Deal {CalculatedDamage:diff()} damage.\")",
            card);
        Assert.DoesNotContain("already including", card);
        // The var triple is untouched: the number is still the live fold, and
        // 2 on a bare morning is still what a bare morning pays.
        Assert.Contains("new CalculationBaseVar(2m)", card);
        Assert.Contains("new ExtraDamageVar(3m)", card);
        Assert.Contains("PlansThisMorning", card);
    }

    [Fact]
    public void EB539_the_rule_and_the_live_count_are_on_the_rider_tip()
    {
        var card = Source(
            "Cards/Prototype/Generated/ProtoKkWellLaid.cs");
        // Handed the SAME base and per the rider emits the vars from, so the
        // sentence cannot quote a number the hit does not use.
        Assert.Contains(
            "KokomiRiderTips.ForMorningDamageRider(", card);
        Assert.Contains(", this, 2, 3)", card);

        var body = Printed(typeof(KokomiRiderTips), "MorningDamageBody");
        Assert.Contains(", plus ", body);
        Assert.Contains("for each [gold]Plan[/gold] the "
                      + "[gold]Bake-Kurage[/gold] carried out this morning",
                        body);
        Assert.Contains("; this morning: ", body);

        Assert.Equal("KLEEMOD-MORNING_DAMAGE_RIDER",
                     KokomiRiderTips.MorningDamageKey);
        Assert.Contains(
            "[Cards.KokomiRiderTips.MorningDamageKey + \".title\"]",
            Source("KleeMod.cs"));
    }

    [Fact]
    public void EB539_off_the_board_the_rule_stands_without_a_count()
    {
        // The `FurinaRiderTips` rule every tip in that file keeps: a shop
        // shelf and a deck view have no morning, and "this morning: 0" printed
        // there would be the same false certainty the row was filed on. So the
        // body asks for an owner and a combat before it counts.
        var calls = Il.Calls(typeof(KokomiRiderTips)
            .GetMethod("MorningDamageBody", All)!);
        Assert.Contains(calls, c => c.Contains("CreatureOf"));
        Assert.Contains(calls, c => c.Contains("get_CombatState"));
        Assert.Contains(calls, c => c.Contains("get_PlansThisMorning"));
    }

    [Fact]
    public void EB539_the_word_moved_with_the_rule_and_kept_its_definition()
    {
        // The arm-keyword attach is derived from the words the card PRINTS,
        // and this split took `Plan` off the face. Without the generator
        // carrying the rider's own word into that scan the row would have gone
        // on saying `Plan` with nothing on screen defining it -- the silence
        // the attach rule exists to make impossible.
        Assert.Contains(
            "ArmKeywordTips.ForPlan(",
            Source("Cards/Prototype/Generated/ProtoKkWellLaid.cs"));
    }

    // ==================================================================
    // `EB-542` -- raw LocString keys in the carry-out log
    // ==================================================================
    //
    // THE FIND (Kokomi r19 lane 1). `Bake-Kurage: Flank: LocString table
    // monsters entry CORPSE_SLUG.name, LocString table monsters entry
    // CORPSE_SLUG.name, 8 -- the 8 is damage.` It recurred on floor 5 with
    // `CALCIFIED_CULTIST` and `DAMP_CULTIST`, and the seat noted the scope
    // exactly: "Only Flank's 'each enemy that intends to attack' line does
    // this -- Kurage's Oath, Pincer and Feigned Retreat all printed clean."
    //
    // THAT SCOPE IS THE DIAGNOSIS. A `LocString`'s `ToString` is its DEBUG
    // form; every other row this class emits carries a `CombatId` and the page
    // renames it out of its own fight memory, so an unresolved title never
    // survived to the screen. `AimedLabel` bakes its names into a string with
    // no id on it, which is the one place it could.

    [Fact]
    public void The_carry_out_line_names_enemies_through_the_bridges_own_lookup()
    {
        // STRUCTURAL, and it is the whole fix: `GetFormattedText` is what
        // `McpMod.SafeGetText` calls to name every body in the enemy list, so
        // the log and the list resolve one way. Read off the compiled method
        // because a live `Monster` needs a combat this harness cannot build.
        var calls = Il.Calls(Il.Method("KokomiPlan", "EnemyName"));

        Assert.Contains(calls, c => c.Contains("GetFormattedText"));
        Assert.DoesNotContain(calls, c => c.EndsWith("LocString.ToString",
                                                     StringComparison.Ordinal));
    }

    [Fact]
    public void The_label_that_bakes_names_in_is_the_only_one_without_an_id()
    {
        // WHY THE DEFECT WAS FLANK-SHAPED, pinned so a new row that bakes a
        // name into a line inherits the reason rather than the bug: the two
        // row types that carry names also carry the handle the page renames
        // them by, and `AimedLabel` carries neither.
        Assert.Contains("KokomiPlan.EnemyName",
                        Il.Calls(Il.Method("KokomiPlan", "AimedLabel")));

        var moved = typeof(KokomiPlan).GetNestedType("MovedOn", All)!;
        var rider = typeof(KokomiPlan).GetNestedType("Rider", All)!;
        Assert.NotNull(moved.GetProperty("CombatId"));
        Assert.NotNull(rider.GetProperty("CombatId"));
    }

    // ==================================================================
    // `EB-543` -- Neow's Talisman's Strike half, and who was wearing the tag
    // ==================================================================
    //
    // THE FIND (Kokomi r19 lane 1). "The relic printed 'Upgrade 1 of your
    // Strikes' and no Strike in my deck was ever upgraded ... the deck census
    // showed `Defend+` and `Slack Water+` -- and four unmodified Strikes, in
    // every hand, all run. This also cost me Miniature Cannon value later."
    //
    // THE ANSWER TO THE ROW'S QUESTION IS YES AND THE DEFECT IS THE OTHER WAY
    // ROUND. The kit's Strike IS the base game's -- `ArmStarterBasics` hands
    // `StrikeSilent` to every sweep site and the arm's starting deck deals four
    // of them -- so it has carried the tag all along. What it did not have was
    // exclusivity: the codegen tagged EVERY basic attack, so `Slack Water`
    // wore `CardTag.Strike` too and won the deck scan. That is `EB-409`'s
    // family exactly (Strike Dummy paying on Slack Water), and the fix is the
    // one that row named: a prototype basic takes neither tag.

    [Theory]
    [InlineData(typeof(ProtoKkSlackWater))]
    [InlineData(typeof(ProtoKaboomSink))]
    public void No_prototype_basic_wears_the_strike_or_defend_tag(Type row)
    {
        var card = (CardModel)Activator.CreateInstance(row)!;

        Assert.Equal(CardRarity.Basic, card.Rarity);
        Assert.DoesNotContain(CardTag.Strike, card.Tags);
        Assert.DoesNotContain(CardTag.Defend, card.Tags);
    }

    [Fact]
    public void And_the_card_the_relic_should_find_is_the_one_the_arm_deals()
    {
        // THE OTHER HALF, and it is what makes the removal safe rather than
        // just narrower: both arms deal the BASE pair, which carries the tag
        // by construction, so "one of your Strikes" has exactly one answer in
        // an arm deck instead of two.
        var seams = Il.Calls(Il.Method("ArmStarterBasics", "StrikeFor"));
        Assert.Contains("KleeOverhaulRoster.StarterStrike", seams);
        Assert.Contains("KokomiOverhaulRoster.StarterStrike", seams);

        Assert.Contains(CardTag.Strike, new BaseGame.StrikeSilent().Tags);
        Assert.Contains(CardTag.Strike, new BaseGame.StrikeIronclad().Tags);
    }

    // ==================================================================
    // `EB-544` -- where an element comes from, and where it does not
    // ==================================================================
    //
    // THE FIND (Kokomi r19 lane 1). "A Fire Potion used to set up Vaporize
    // left no Pyro aura at all, and nothing on any screen says which sources
    // apply an element and which do not." The seat spent a potion on a
    // reaction it could not have.
    //
    // THE RULE IS ONE EXPRESSION'S. `AuraCmd.ElementOfPlay`
    // answers off the CARD being played -- and, under the companion arm, off a
    // rider on the dealer -- so a play with no card behind it answers
    // `Element.None` and applies nothing. A potion is exactly that play.

    [Fact]
    public void A_play_with_no_card_behind_it_applies_no_element()
    {
        var seat = Seat.Klee();

        Assert.Equal(Element.None,
                     AuraCmd.ElementOfPlay(null, seat.Creature));
        // And with no dealer either, which is the shape a relic's own hit and
        // an enemy's take.
        Assert.Equal(Element.None,
                     AuraCmd.ElementOfPlay(null, null));
    }

    [Fact]
    public void A_card_that_prints_one_is_the_only_source_the_funnel_reads()
    {
        // The other half, so the gloss's "from a CARD that prints one" is a
        // claim about this method and not about a card: the funnel asks the
        // card for its element, and a card that declares none -- a Defend --
        // answers none.
        var seat = Seat.Klee();

        Assert.Equal(Element.Pyro, AuraCmd.ElementOfPlay(
            new Kaboom(), seat.Creature));
        Assert.Equal(Element.None, AuraCmd.ElementOfPlay(
            new DuckAndCover(), seat.Creature));
    }

    // ==================================================================
    // `EB-546` -- the Vaporize that did not multiply
    // ==================================================================
    //
    // THE FIND (Furina r13 lane 1). "The salon log read: `Crabaletta hit
    // Sludge Spinner for 6 Hydro, and left no aura on it.` The enemy was
    // wearing Pyro Aura 2, and Crabaletta was at full strength (Encore paid)
    // ... so 9. The HP bar moved 24 to 18. Six." And in fight 2 the same card
    // into the same aura while DRY hit for 6 off a 4.5 base, which IS 1.5x.
    //
    // WHAT IS PINNED HERE is every term of that arithmetic that a headless
    // test can reach, plus the wiring that composes them -- the row's
    // reproduction half is `tier0/tests/test_eb546_a_performance_amplifies.py`,
    // where a paid performance into Pyro lands 9 and a dry one lands 6. The
    // live 6 is NOT reproduced by either engine's code and the row stays open
    // on it.

    [Fact]
    public void The_amplifier_is_one_and_a_half_and_does_not_ask_who_paid()
    {
        // THE TERM ITSELF. It is a property of the REACTION, so nothing about
        // the Encore buffer can reach it -- which is why "paid" and "dry"
        // cannot differ in whether they multiply, only in what they multiply.
        Assert.Equal(ReactionConstants.VaporizeMult,
                     ReactionTable.AmplifierMultiplier(Reaction.Vaporize));
        Assert.Equal(ReactionConstants.VaporizeMult,
                     ReactionTable.AmplifierMultiplier(Reaction.Vaporize, null));
        Assert.Equal(1.5m, ReactionConstants.VaporizeMult);
    }

    [Fact]
    public void The_dry_cut_is_a_size_and_the_amplifier_is_a_separate_term()
    {
        // The two numbers the seat's readings turn on, off the one expression
        // the badge and the hit share: a paid Crabaletta is her printed tick
        // and a dry one is three-quarters of it, TRUNCATED -- 6 and 4, which
        // is what makes 9 and 6 the two amplified answers.
        var seat = Seat.Furina().WithCombatState();

        var paid = SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Crabaletta, paid: true);
        var dry = SalonMemberPower.TickValue(
            seat.Creature, SalonMember.Crabaletta, paid: false);

        Assert.Equal(SalonConstants.CrabalettaTick, paid);
        Assert.Equal((int)(paid * SalonConstants.DryDamageMultiplier), dry);
        Assert.Equal(6, paid);
        Assert.Equal(4, dry);
    }

    [Fact]
    public void A_performance_goes_through_the_funnel_that_multiplies()
    {
        // STRUCTURAL, and it is the whole of what a headless test can say
        // about the live reading: there is ONE implementation of a member
        // acting, it asks `ElementalHit.Deal`, and `Deal` multiplies by the
        // amplifier and then reads the target's terms -- in that order, with
        // no branch between them that the Encore buffer can reach.
        Assert.Contains("ElementalHit.Deal",
                        Il.Calls(Il.Method("SalonMemberPower", "PerformMember")));

        var deal = Il.CallSequence(Il.Method("ElementalHit", "Deal")).ToList();
        var amp = deal.FindIndex(c => c.Contains("AmplifierMultiplier"));
        var mods = deal.FindIndex(c => c.Contains("TargetMods"));
        var hit = deal.FindIndex(c => c.Contains("CreatureCmd.Damage"));

        Assert.True(amp >= 0 && mods > amp && hit > mods,
                    "amplifier, then the target's terms, then the hit");
    }

    // ==================================================================
    // `EB-549` -- two cards, one name, and the door that let both in
    // ==================================================================
    //
    // THE FIND (Furina r13 lane 1). "Two cards in this run share a name with a
    // completely different card": the card-reward copy of `Kaeya --
    // Frostgnaw` read "Deal 8 damage. Gain 3 Block", and the copy An
    // Invitation fetched into hand was a 6-damage no-Block card under the same
    // title. "From the seat they are simply two different cards with one
    // name."
    //
    // THEY ARE THE ARM'S ROW AND THE SHIPPED ROW IT REWRITES. A prototype row
    // that shadows a shipped one keeps its printed name, and the premise of
    // that (`EB-322`, and `lint_unique_names`' shadow rule) is that the arm
    // substitutes the shipped row out. `CompanionPool.All` makes that true at
    // the offer door; this generator read `CompanionRoster.All` and went
    // around it -- `EB-491`'s lesson one door over.

    [Fact]
    public void The_guest_star_generator_reads_the_arm_aware_door()
    {
        var calls = Il.Calls(Il.Method("GuestStarGenerator", "Generate"));

        Assert.Contains("CompanionPool.get_All", calls);
        Assert.DoesNotContain("CompanionRoster.get_All", calls);
    }

    [Fact]
    public void And_that_door_is_the_one_the_offer_surfaces_read()
    {
        // The claim the fix rests on, read where it lives: `CompanionPool.All`
        // answers the ARM's roster while the arm is on and the shipped one
        // otherwise, so every consumer of it sees one row per printed name.
        var door = Il.Calls(Il.Method("CompanionPool", "get_All"));

        Assert.Contains("CompanionOverhaul.get_Enabled", door);
        Assert.Contains("CompanionOverhaulRoster.Roster", door);
        Assert.Contains("CompanionRoster.get_All", door);
    }

    /// <summary>The loc key a pile's badge is resolving right now.
    /// <c>KleeOverhaulRoundOneFixTests.LocKey</c>, verbatim.</summary>
    private static string LocKey(ProtoBombPower pile) =>
        (string)typeof(ProtoBombPower)
            .GetProperty("SmartDescriptionLocKey", All)!
            .GetValue(pile)!;

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
