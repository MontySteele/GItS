using System;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
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
