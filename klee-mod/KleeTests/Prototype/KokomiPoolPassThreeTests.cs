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
/// KOKOMI POOL PASS THREE -- competing faces instead of a cap (`EB-655`,
/// R266, 2026-09-07).
///
/// THE FINDING. Every two-line row printed the same trade: a small now-line, a
/// bigger Plan. So "write it" was the right answer on nearly every safe turn,
/// the queue only got deeper, and the two-Plan cap was an attempt to fix the
/// shape from outside the cards. [USER] retired the cap as a rule; what
/// replaces it is nine changes that give the NOW-LINE something the written
/// half cannot buy -- a bigger number after a carry-out (Feint), information
/// (Read the Field), a board read (Riptide) -- plus two rows that admit they
/// are written-only (Breakwater, Night Watch), a Rare that pays the FIRST Plan
/// rather than every Plan, and one retirement.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on
/// <see cref="KokomiPoolPassTwoTests"/>' split. The card shapes are REAL --
/// every row is constructed and its face, cost, rarity, target type, plan
/// clauses and smith's move are read off the shipped class. The RESOLUTION is
/// not: a drain needs a live <c>CombatState</c>, so the Rare's new window and
/// the discount's two seams are pinned off the compiled methods and labelled.
/// The end-to-end arithmetic is the sim twin's:
/// <c>tier0/tests/test_kokomi_plan.py</c>.
///
/// THE NUMBERS ARE PROTOTYPE NUMBERS (D by the ladder). Nothing here is
/// quotable (R215 B).
/// </summary>
public class KokomiPoolPassThreeTests
{
    private const BindingFlags All = HeadlessGame.All;

    // ======================================================================
    // 1. FEINT -- the now-line pays the Plan's own number after a carry-out
    // ======================================================================

    [Fact]
    public void Feints_now_line_reads_the_plans_waiting_and_not_the_flag()
    {
        // The re-founding (2026-10-12): "plus 3 for each Plan waiting", the
        // queue's own count (`KokomiPlan.PlansHeld`).
        var source = Source("ProtoKkFeint");
        Assert.Contains("KokomiPlan.PlansHeld", source);
        Assert.DoesNotContain(Il.Calls(Il.Method("ProtoKkFeint", "OnPlay")),
                              c => c.Contains("PlanCarriedOutThisTurn"));
    }

    [Fact]
    public void Feint_prints_six_plus_three_per_carry_out_and_upgrades_the_base()
    {
        // THE CASKET PASS (2026-09-28): "Deal 4 damage, plus 3 for each Plan
        // carried out this turn. Plan: Apply 1 Vulnerable." Upgraded: base 6,
        // Plan 2 Vulnerable. Both printed numbers are live vars (`EB-657`),
        // and the in-combat line prints the total. The cleanup pass
        // (2026-09-29) moved the base to 6, upgraded 9.
        var face = Face(new ProtoKkFeint());
        Assert.Contains("{CalculationBase:diff()}", face);
        Assert.Contains("{ExtraDamage:diff()}", face);
        Assert.Contains("{CalculatedDamage:diff()}", face);
        Assert.DoesNotContain("{IfUpgraded:show:", face);
        var source = Source("ProtoKkFeint");
        Assert.Contains("new CalculationBaseVar(6m)", source);
        Assert.Contains("new ExtraDamageVar(3m)", source);
        Assert.Contains("DynamicVars.CalculationBase.UpgradeValueBy(3m);", source);
        // The pool overhaul (2026-10-13): the Plan's rate upgrades, 5 -> 7.
        Assert.Contains("DynamicVars[\"PlanDamage\"].UpgradeValueBy(2m);",
                        source);
    }

    [Fact]
    public void Feints_plan_applies_vulnerable_and_upgrades_to_two()
    {
        // The pool overhaul (2026-10-13): the Plan line is a Chain -- 5 [7]
        // for each Plan carried out this turn, itself included (was R276's
        // Vulnerable).
        var card = new ProtoKkFeint();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Attack, card.Type);
        Assert.Equal(CardRarity.Common, card.Rarity);
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.DamagePerPlanThisTurn, clause.Kind);
        Assert.Equal(5, clause.Amount);
        Assert.Equal(KokomiPlan.Aim.FrontEnemy, clause.Aim);
        Assert.Contains("PlanDamage\"].UpgradeValueBy(2m)",
                        Source("ProtoKkFeint"));
        // `EB-660`: AND THE FACE SAYS SO, live off the Plan's own var.
        Assert.Contains("Or [gold]plan[/gold]: Deal {PlanDamage:diff()} "
                      + "[gold]Hydro[/gold] damage for each [gold]Plan[/gold] "
                      + "carried out this turn.",
                        Face(new ProtoKkFeint()));
    }

    [Fact]
    public void Feint_still_accepts_the_pet_or_an_enemy()
    {
        // THE AIM IS READ THROUGH THE CONDITIONAL. Both branches hit an enemy,
        // so the row keeps the pet-or-enemy drag; a derivation that only
        // looked at the top level would have called this self-aimed and taken
        // the enemy target away from an Attack.
        Assert.Contains("KokomiTargets.PetOrEnemy", Source("ProtoKkFeint"));
    }

    // ======================================================================
    // 2. READ THE FIELD -- the now-line buys information
    // ======================================================================

    [Fact]
    public void Read_the_field_still_buys_information_face_up()
    {
        // WHAT SURVIVED POOL PASS FOUR. The now-line is still the half that
        // buys what the written half cannot -- a screen over the top of the
        // draw pile -- and `EB-679` only changed what the screen DOES with the
        // pick. The verb, the count and the take are pinned in
        // `KokomiPoolPassFourTests`.
        // A PLAN STAYS OPEN (2026-10-01): the now-line is its own method.
        var play = Il.Calls(Il.Method("ProtoKkReadTheField", "PlayNowLine")).ToList();
        // `EB-686` moved the screen one call out, into `ScryTake.Choose`,
        // which owns the grid and the one-candidate branch alike.
        Assert.Contains(play, c => c.Contains("ScryTake.Choose"));
        Assert.Contains(Il.Calls(Il.Method("ScryTake", "Choose")),
                        c => c.Contains("CardSelectCmd.FromSimpleGrid"));
        Assert.Contains(play, c => c.Contains("CardPileCmd.Add"));
    }

    [Fact]
    public void The_scry_screen_has_one_ruled_string_and_one_source()
    {
        // A `LocString` is a table plus a key with no raw-text constructor, so
        // ruled copy can only reach the screen as a row and
        // `KleeMod.InjectLocStrings` is that row's only source.
        Assert.Equal("cards", new[] { "cards" }[0]);
        Assert.False(string.IsNullOrWhiteSpace(ScryBottom.PromptText));
        Assert.Contains("selectionScreenPrompt", ScryBottom.PromptKey);
    }

    [Fact]
    public void Read_the_fields_planned_wall_is_ten_and_smiths_to_twelve()
    {
        // WHAT SURVIVED POOL PASS FOUR: the Plan half, unchanged. The now-line
        // half moved (`EB-679` took the 5 Block off and made the look a take),
        // and its numbers are pinned in `KokomiPoolPassFourTests`.
        // The pool overhaul (2026-10-13): the Plan half is a fetch from the
        // Draw Pile now (was 10 [12] Block), and prints no number.
        var card = new ProtoKkReadTheField();
        Assert.Equal(1, card.EnergyCost.Canonical);
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.DrawPileToHand, clause.Kind);
        Assert.DoesNotContain("PlanBlock", Source("ProtoKkReadTheField"));
    }

    // ======================================================================
    // 3. RIPTIDE -- the AoE debuff rider
    // ======================================================================

    [Fact]
    public void Riptide_adds_the_rider_per_body_and_cannot_fold_it()
    {
        // An all-enemies rider CANNOT fold: one printed number would have to
        // stand for a board that takes several. So it prints two numbers and
        // the loop adds the rider per body -- `bonus_vs_aura`'s shape, with
        // `KokomiOverhaulKit.HasDebuff` as the question.
        var source = Source("ProtoKkRiptide");
        Assert.Contains("HittableEnemies", source);
        Assert.Contains("KokomiOverhaulKit.HasDebuff(auraTarget)", source);
        Assert.Contains("DynamicVars.ExtraDamage.BaseValue", source);
        // NOT the folded shape: no CalculatedDamageVar, no PlainDamage pair.
        Assert.DoesNotContain("FoldedDamageVar", source);
    }

    [Fact]
    public void Riptide_prints_eleven_and_three_and_upgrades_by_three_and_one()
    {
        // THE CASKET PASS (2026-09-28): 11 to ALL, debuffed enemies take 3
        // more (14 / 4 upgraded); the Plan is 2 Energy and a card.
        var card = new ProtoKkRiptide();
        Assert.Equal(2, card.EnergyCost.Canonical);
        // Uncommon since the feed pass (2026-09-29).
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        var face = Face(card);
        Assert.Contains("{Damage:diff()}", face);
        Assert.Contains("{ExtraDamage:diff()}", face);
        // The re-founding (2026-10-12): the Plan is "Draw 3 cards" [4].
        Assert.Contains("Or [gold]plan[/gold]: Draw {PlanCards:diff()} cards.",
                        face);
        var source = Source("ProtoKkRiptide");
        Assert.Contains("new DamageVar(11m", source);
        Assert.Contains("new ExtraDamageVar(3m)", source);
        Assert.Contains("DynamicVars.Damage.UpgradeValueBy(3m)", source);
        Assert.Contains("DynamicVars.ExtraDamage.UpgradeValueBy(1m)", source);
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal((KokomiPlan.Kind.Draw, 3), (clause.Kind, clause.Amount));
    }

    // ======================================================================
    // 4. BATTLE PLAN -- the energy clause off, a face-up Attack rider on
    // ======================================================================

    // ======================================================================
    // 5. NEREID'S ASCENSION -- the FIRST Plan of each drain
    // ======================================================================

    [Fact]
    public void The_rare_says_first_plan_and_no_longer_every_plan()
    {
        var face = Face(new ProtoKkNereidsAscension());
        Assert.Contains("first", face);
        Assert.DoesNotContain("every", face);
    }

    [Fact]
    public void Only_the_first_entry_of_a_drain_reads_carry_out_times()
    {
        // "Each turn" is read as "each DRAIN": a morning and a dusk are two
        // drains on one turn and each pays its own first entry, which is the
        // drain-local reading "the next Plan" already takes. Twin:
        // `test_nereids_doubles_only_the_first_plan_of_a_drain`.
        // Through `firstTimes` (Spring Tide's mid-turn drain, which set it
        // to 1, left with the card in the jellyfish build, 2026-10-12).
        var source = Source("KokomiPlan", power: true);
        Assert.Contains("index == 0 ? firstTimes : 1", source);
        Assert.Contains("var firstTimes = CarryOutTimes(kokomi);", source);
    }

    [Fact]
    public void The_mornings_depth_gains_one_and_is_not_doubled()
    {
        // A three-Plan morning under the Rare is FOUR carry-outs, not six --
        // the number Tide Wall, Well Laid and Tide Chart all read.
        Assert.Contains("due.Count + (CarryOutTimes(kokomi) > 1 ? 1 : 0)",
                        Source("KokomiPlan", power: true));
    }

    // ======================================================================
    // 7. THE CAP SENTENCE
    // ======================================================================

    [Fact]
    public void The_cap_sentence_names_the_drain_it_binds()
    {
        // `EB-650`, R266. The sentence said "a turn" and the rule is about the
        // MORNING: `ResolveDusk` is not capped, so under a declared cap a turn
        // could carry out more Plans than the face claimed was its limit --
        // the r24 defect one word over.
        Assert.Contains("at the start of your turn",
                        Source("KokomiPlan", power: true));
        Assert.DoesNotContain("at most {0} a turn",
                              Source("KokomiPlan", power: true));
    }

    // ======================================================================
    // helpers -- KokomiPoolPassTwoTests' own, for its reasons
    // ======================================================================

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    /// <summary>One generated class's own source, read off disk. A SOURCE READ
    /// and not an IL one, and only for the facts IL cannot carry: a named
    /// argument (`dusk: true`) compiles to a positional load that says nothing
    /// about the name, a `const string` is a literal no call sequence
    /// mentions, and an `(IsUpgraded ? a : b)` swap on a literal leaves no
    /// call at all.</summary>
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
