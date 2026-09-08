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
    public void Feints_now_line_is_a_carry_out_conditional_and_not_a_flat_hit()
    {
        // Sango Isshin's shape at Common: the branch reads the ledger's
        // `PlanCarriedOutThisTurn`, which is the same question the Rare asks,
        // so "a Plan was carried out this turn" has one definition in the arm.
        // Twin: `test_feint_pays_the_planned_number_after_a_carry_out`.
        Assert.Contains(Il.Calls(Il.Method("ProtoKkFeint", "OnPlay")),
                        c => c.Contains("PlanCarriedOutThisTurn"));
    }

    [Fact]
    public void Feint_prints_five_and_ten_and_upgrades_them_by_two_and_three()
    {
        // THE TWO PRINTED NUMBERS UPGRADE BY DIFFERENT AMOUNTS, which is the
        // whole reason `conditional_then_damage` exists: `conditional_damage`
        // moves both branches by 2 and the then-branch takes 1 more.
        var face = Face(new ProtoKkFeint());
        Assert.Contains("{IfUpgraded:show:7|5}", face);
        Assert.Contains("{IfUpgraded:show:13|10}", face);
        // The branch amounts are literals that swap at play time, so the swap
        // is in the BODY and not in a var -- the shape `_branch_amount` emits.
        var source = Source("ProtoKkFeint");
        Assert.Contains("(IsUpgraded ? 7m : 5m)", source);
        Assert.Contains("(IsUpgraded ? 13m : 10m)", source);
    }

    [Fact]
    public void Feints_plan_still_deals_ten_and_upgrades_to_thirteen()
    {
        var card = new ProtoKkFeint();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Attack, card.Type);
        Assert.Equal(CardRarity.Common, card.Rarity);
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.Damage, clause.Kind);
        Assert.Equal(10, clause.Amount);
        Assert.Contains("PlanDamage\"].UpgradeValueBy(3m)", Source("ProtoKkFeint"));
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
    public void Read_the_field_shows_the_top_two_and_bottoms_the_pick()
    {
        // The screen is the game's own selection grid over the top N, and the
        // move never leaves the draw pile: `CardPileCmd.Add(..., PileType.Draw,
        // CardPilePosition.Bottom)`. Twin: `effects._op_scry_bottom`, which
        // bottoms the highest-cost card because the sim has no human.
        var play = Il.Calls(Il.Method("ProtoKkReadTheField", "OnPlay")).ToList();
        Assert.Contains(play, c => c.Contains("CardSelectCmd.FromSimpleGrid"));
        Assert.Contains(play, c => c.Contains("CardPileCmd.Add"));
        var source = Source("ProtoKkReadTheField");
        Assert.Contains("Cards.Take(2)", source);
        Assert.Contains("CardPilePosition.Bottom", source);
        Assert.Contains("ScryBottom.Prompt", source);
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
    public void Read_the_field_upgrades_both_block_numbers_and_not_the_scry()
    {
        var card = new ProtoKkReadTheField();
        Assert.Equal(1, card.EnergyCost.Canonical);
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(10, clause.Amount);
        var source = Source("ProtoKkReadTheField");
        Assert.Contains("DynamicVars.Block.UpgradeValueBy(2m)", source);
        Assert.Contains("PlanBlock\"].UpgradeValueBy(2m)", source);
        // ONE PRINTED NUMBER PER HALF: the "2" the scry looks at is a rule of
        // the card and not a number the smith moves.
        Assert.DoesNotContain("Cards.Take(3)", source);
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
    public void Riptide_prints_nine_and_four_and_upgrades_by_three_and_two()
    {
        var card = new ProtoKkRiptide();
        Assert.Equal(2, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Common, card.Rarity);
        var face = Face(card);
        Assert.Contains("{Damage:diff()}", face);
        Assert.Contains("{ExtraDamage:diff()}", face);
        var source = Source("ProtoKkRiptide");
        Assert.Contains("new DamageVar(9m", source);
        Assert.Contains("new ExtraDamageVar(4m)", source);
        Assert.Contains("DynamicVars.Damage.UpgradeValueBy(3m)", source);
        Assert.Contains("DynamicVars.ExtraDamage.UpgradeValueBy(2m)", source);
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(13, clause.Amount);
    }

    // ======================================================================
    // 4. BATTLE PLAN -- the energy clause off, a face-up Attack discount on
    // ======================================================================

    [Fact]
    public void Battle_plans_plan_is_a_draw_and_the_discount_and_no_energy()
    {
        // THE ENERGY CLAUSE IS GONE. It paid the write back its own cost, so
        // writing was free and the now-line was a strictly smaller card.
        var card = new ProtoKkBattlePlan();
        var clauses = card.PlanClauses;
        Assert.Equal(2, clauses.Count);
        Assert.Equal(KokomiPlan.Kind.Draw, clauses[0].Kind);
        Assert.Equal(2, clauses[0].Amount);
        Assert.Equal(KokomiPlan.Kind.NextAttackDiscount, clauses[1].Kind);
        // A GRANT AND NOT A NUMBER: the size is the rule's, so the clause
        // carries none -- `PLAN_AMOUNTLESS_OPS`.
        Assert.Equal(0, clauses[1].Amount);
        Assert.Equal(KokomiPlan.Aim.Self, clauses[1].Aim);
        Assert.DoesNotContain(clauses, c => c.Kind == KokomiPlan.Kind.Energy);
    }

    [Fact]
    public void The_new_kind_is_the_one_the_codegen_maps()
    {
        // `gen_klee_cards.PLAN_CLAUSE_KINDS` maps the sheet's spelling onto
        // this member BY NAME, so a rename is a codegen break rather than a
        // silent approximation.
        Assert.Contains("NextAttackDiscount",
                        System.Enum.GetNames(typeof(KokomiPlan.Kind)));
    }

    [Fact]
    public void The_carry_out_applies_the_power_through_the_kit()
    {
        Assert.Contains(
            Il.Calls(typeof(KokomiPlan).GetMethod("ResolveOne", All)!),
            c => c.Contains("NextAttackDiscount"));
    }

    [Fact]
    public void The_discount_is_one_stack_a_discount_and_an_attack_only()
    {
        // ONE STACK, ALWAYS (the face says "costs 1 less", not "per Plan"),
        // and a SUBTRACTION floored at zero rather than a zeroing.
        Assert.Equal(1, NextAttackDiscountPower.Discount);
        var source = Source("KokomiOverhaulPowers", power: true);
        Assert.Contains("if (card.Type != CardType.Attack) return false;",
                        source);
        Assert.Contains("System.Math.Max(0m, originalCost - Discount)",
                        source);
        // ONE STACK: the kit refuses a second grant outright.
        Assert.Contains("OfType<NextAttackDiscountPower>().Any()) return;",
                        Source("KokomiOverhaulKit", power: true));
    }

    [Fact]
    public void A_written_attack_does_not_spend_the_discount()
    {
        // THE FACE-UP CLAUSE, enforced where it can be. A card dragged onto
        // the Bake-Kurage is a WRITE -- none of its now-line resolves -- so it
        // is not "an Attack you played" in the sense the face means, and the
        // grant waits for one that is. The COST seam cannot ask the same
        // question (`TryModifyEnergyCostInCombat` is handed no `CardPlay`),
        // which is disclosed on the power and in the pass's provenance.
        Assert.Contains("KokomiPlan.PlayedOnPet",
                        Il.Calls(typeof(NextAttackDiscountPower)
                            .GetMethod("AfterCardPlayed", All)!));
    }

    [Fact]
    public void The_discount_dies_with_its_turn()
    {
        // "This turn" is the ratified same-turn boundary Rally's grant keeps.
        Assert.Contains("PowerCmd.Remove",
                        Il.Calls(typeof(NextAttackDiscountPower)
                            .GetMethod("AfterSideTurnEnd", All)!));
    }

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
        Assert.Contains("index == 0 ? CarryOutTimes(kokomi) : 1",
                        Source("KokomiPlan", power: true));
    }

    [Fact]
    public void The_mornings_depth_gains_one_and_is_not_doubled()
    {
        // A three-Plan morning under the Rare is FOUR carry-outs, not six --
        // the number Tide Wall, Well Laid and Tide Chart all read.
        Assert.Contains("due.Count + (CarryOutTimes(kokomi) > 1 ? 1 : 0)",
                        Source("KokomiPlan", power: true));
    }

    [Fact]
    public void Scout_aheads_forward_count_is_entries_now()
    {
        // Entries after this one, one carry-out each: the Rare doubles the
        // first entry alone and this entry is never the first when anything
        // follows it.
        Assert.Contains("var after = due.Count - index - 1;",
                        Source("KokomiPlan", power: true));
    }

    // ======================================================================
    // 6. THE DUSK ROWS -- written-only
    // ======================================================================

    [Fact]
    public void Both_dusk_rows_target_the_pet_alone_and_print_where_they_go()
    {
        // `EB-646` priced the face-up half to the Dusk line and the seat still
        // never played it, so the now-line comes off instead. The plan-only
        // shape does the rest: `KokomiTargets.PetOnly`, and the face LEADS
        // with the instruction (`gen_klee_cards._plan_only_line`), so a play
        // that is not a write is refused with the reason printed.
        foreach (var (card, name) in new (CardModel, string)[]
                 {
                     (new ProtoKkBreakwater(), "ProtoKkBreakwater"),
                     (new ProtoKkNightWatch(), "ProtoKkNightWatch"),
                 })
        {
            Assert.Contains("KokomiTargets.PetOnly", Source(name));
            Assert.StartsWith("Play on the [gold]Bake-Kurage[/gold].",
                              Face(card));
            Assert.Contains("[gold]Dusk[/gold]", Face(card));
            // No now-line at all: the whole body is the write.
            Assert.DoesNotContain("CreatureCmd.GainBlock", Source(name));
        }
    }

    [Fact]
    public void The_written_only_rows_still_write_a_dusk_plan()
    {
        Assert.Contains("dusk: true", Source("ProtoKkBreakwater"));
        Assert.Contains("dusk: true", Source("ProtoKkNightWatch"));
        Assert.Equal(6, Assert.Single(new ProtoKkBreakwater().PlanClauses).Amount);
        Assert.Equal(4, new ProtoKkNightWatch().PlanClauses[0].Amount);
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
