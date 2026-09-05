using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI POOL PASS -- five new rows and one redesign (`EB-492`,
/// <c>review/active/kokomi-pool-pass-2026-09-05.md</c>).
///
/// THE FINDING. The seats drafted Attacks and the pool's Attacks mostly
/// carried no Plan line: exactly one Common (Feint) had one, so a seat that
/// took the damage it was offered planned on five turns in sixteen (round 14)
/// and read "Nothing is planned" sixteen times (round 10). Density in the
/// OFFER, not in the starter, which stands under R254 and R257.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on the README's terms and
/// <see cref="KokomiOverhaulRuleTests"/>' split. The card shapes are REAL --
/// every row is constructed and its face, cost, rarity, vars, plan clauses and
/// smith's move are read off the shipped class. The RESOLUTION is not: a
/// planned hit needs <c>ElementalHit.Deal</c> and a live <c>CombatState</c>,
/// both outside the headless boundary, so the loop, the capture and the aim
/// are pinned off the compiled methods and labelled. The end-to-end arithmetic
/// is the sim twin's: <c>tier0/tests/test_kokomi_plan.py</c>, section "THE POOL
/// PASS".
///
/// THE NUMBERS ARE PROTOTYPE NUMBERS (D by the ladder). Nothing here is
/// quotable (R215 B).
/// </summary>
public class KokomiPoolPassTests
{
    private const BindingFlags All = HeadlessGame.All;

    // ======================================================================
    // 1. THE VOCABULARY: one aim added, one clause retired
    // ======================================================================

    [Fact]
    public void The_aim_enum_carries_the_intent_keyed_set()
    {
        // `gen_klee_cards.PLAN_AIM_CS` maps the sheet's
        // `enemies_intending_attack` onto this member BY NAME, so a rename
        // here is a codegen break rather than a silent approximation -- the
        // same contract `Kind` is under.
        Assert.Equal(new[] { "Self", "FrontEnemy", "AllEnemies",
                             "EnemiesIntendingAttack" },
                     System.Enum.GetNames(typeof(KokomiPlan.Aim)));
    }

    [Fact]
    public void The_retired_doubling_clause_is_gone_with_its_power()
    {
        // `EB-492` RETIRED `PlanTwice` rather than leaving it standing with no
        // row to spell it: Nereid's Ascension is a Power now, and a clause no
        // card can write is a rule nothing enforces. The enum is the whitelist
        // the codegen validates a row's `plan:` list against, so its ABSENCE
        // here is what makes the retirement true on both sides.
        Assert.DoesNotContain("PlanTwice",
                              System.Enum.GetNames(typeof(KokomiPlan.Kind)));
        Assert.DoesNotContain(
            typeof(KokomiPlan).Assembly.GetTypes(),
            t => t.Name == "PlanTwicePower");
    }

    [Fact]
    public void The_planned_clause_still_stores_no_creature()
    {
        // Rule 3's own discipline, re-asserted because `EB-492` is the first
        // clause to remember anything about a body at all. `Targets` is a list
        // of `CombatId` STRINGS, which is the difference that matters: a Plan
        // written last turn cannot hold a reference to a creature the game has
        // torn down, so the set is resolved against the live board at
        // carry-out and a body that died is simply not there.
        var planned = typeof(KokomiPlan.Planned);
        Assert.DoesNotContain(
            planned.GetProperties(All),
            p => p.PropertyType.Name == "Creature");
        Assert.DoesNotContain(
            planned.GetProperties(All),
            p => p.PropertyType.IsGenericType
                 && p.PropertyType.GetGenericArguments()
                     .Any(a => a.Name == "Creature"));
        Assert.NotNull(planned.GetProperty("Targets", All));
        Assert.NotNull(planned.GetProperty("Times", All));
    }

    // ======================================================================
    // 2. RIPTIDE -- the heavy AoE, at 2
    // ======================================================================

    [Fact]
    public void Riptide_hits_all_enemies_on_both_halves()
    {
        var card = new ProtoKkRiptide();
        Assert.Equal(2, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Attack, card.Type);
        Assert.Equal(CardRarity.Common, card.Rarity);

        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.Damage, clause.Kind);
        Assert.Equal(KokomiPlan.Aim.AllEnemies, clause.Aim);
        Assert.Equal(13, clause.Amount);
        Assert.Equal(1, clause.Times);      // the default, said out loud
    }

    [Fact]
    public void Riptide_prints_both_numbers_and_the_smith_moves_both()
    {
        // The row's two printed numbers are its two halves, so the face prints
        // each as a var and `OnUpgrade` moves those same vars (`EB-283`).
        var card = new ProtoKkRiptide();
        Assert.Contains("{Damage:diff()}", Face(card));
        Assert.Contains("{PlanDamage:diff()}", Face(card));

        var moves = Il.Calls(Il.Method("ProtoKkRiptide", "OnUpgrade"));
        Assert.Contains(moves, c => c.Contains("UpgradeValueBy"));
    }

    // ======================================================================
    // 3. PINCER -- the multi-hit Plan clause
    // ======================================================================

    [Fact]
    public void Pincers_plan_is_three_separate_hits()
    {
        // `Times` on the clause, not a bigger `Amount`: three hits of 3 and
        // one hit of 9 are different against an aura, against anything hung
        // off a strike, and against a body that dies partway.
        var card = new ProtoKkPincer();
        Assert.Equal(1, card.EnergyCost.Canonical);

        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.Damage, clause.Kind);
        Assert.Equal(KokomiPlan.Aim.FrontEnemy, clause.Aim);
        Assert.Equal(3, clause.Amount);
        Assert.Equal(3, clause.Times);
    }

    [Fact]
    public void Pincers_now_line_is_two_hits_through_the_games_own_counter()
    {
        // The now-line takes `WithHitCount`, the base game's own multi-hit
        // door, so the played half is two strikes for everything that reads a
        // strike -- the same statement the Plan half makes with `Times`.
        var play = Il.Calls(Il.Method("ProtoKkPincer", "OnPlay"));
        Assert.Contains(play, c => c.Contains("WithHitCount"));
    }

    [Fact]
    public void The_carry_out_loops_the_clauses_times_and_re_reads_its_aim()
    {
        // STRUCTURAL (the hit itself is `ElementalHit.Deal`, outside the
        // headless boundary). What is pinned is that `Hit` reads `Times` at
        // all and that `Aimed` is called INSIDE that loop -- which is what
        // makes a front enemy killed by the first pass hand the next one to
        // the enemy behind it. Twin:
        // `test_a_times_clause_re_reads_its_aim_between_hits`.
        var hit = typeof(KokomiPlan).GetMethod("Hit", All)!;
        var calls = Il.Calls(hit).ToList();
        Assert.Contains(calls, c => c.Contains("Planned.get_Times"));
        Assert.Contains(calls, c => c.Contains("KokomiPlan.Aimed"));
    }

    // ======================================================================
    // 4. FLANK -- the intent-keyed set, fixed when the Plan is written
    // ======================================================================

    [Fact]
    public void Flank_plans_at_the_enemies_that_intend_to_attack()
    {
        var card = new ProtoKkFlank();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);

        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.Damage, clause.Kind);
        Assert.Equal(KokomiPlan.Aim.EnemiesIntendingAttack, clause.Aim);
        // EMPTY UNTIL THE PLAN IS WRITTEN, which is the whole shape of the
        // card: the printed clause is a rule and the set is this board's.
        Assert.Null(clause.Targets);
    }

    [Fact]
    public void The_set_is_captured_when_the_plan_is_written()
    {
        // R250's rule for an aimed Plan, applied to a SET: what the player is
        // reading when they decide to write it is the intents on screen NOW,
        // so the capture is in `Schedule` and not in the carry-out. A read at
        // resolution would answer about the next turn's intents instead.
        // Twin: `test_the_intent_set_is_fixed_when_the_plan_is_written`.
        var schedule = typeof(KokomiPlan).GetMethod("Schedule", All)!;
        Assert.Contains(Il.Calls(schedule),
                        c => c.Contains("KokomiPlan.IntendingAttack"));

        // And nothing in the carry-out asks the board what it intends.
        var aimed = typeof(KokomiPlan).GetMethod("Aimed", All)!;
        Assert.DoesNotContain(Il.Calls(aimed),
                              c => c.Contains("IntendsAttack"));
        Assert.Contains(Il.Calls(aimed),
                        c => c.Contains("Planned.get_Targets"));
    }

    [Fact]
    public void The_intent_test_is_the_arms_one_definition()
    {
        // ONE definition, so a planned Flank and the Furina arm's reader can
        // never disagree about what an attack intent was:
        // `CurtainCallHooks.EnemyIntendsAttack` is now the board-wide half of
        // the per-creature `IntendsAttack` this aim reads.
        Assert.Contains(
            Il.Calls(typeof(KokomiPlan).GetMethod("IntendingAttack", All)!),
            c => c.Contains("CurtainCallHooks.IntendsAttack"));
        Assert.Contains(
            Il.Calls(Il.Method("CurtainCallHooks", "EnemyIntendsAttack")),
            c => c.Contains("IntendsAttack"));
    }

    [Fact]
    public void An_empty_set_still_writes_a_plan_and_says_so()
    {
        // "The Plan is written and carries out nothing." A Plan that silently
        // declined to queue would make the badge and the strip lie about the
        // queue's depth, so the entry is real and the LABEL is what tells the
        // player -- the same channel Crystal Collapse's "nothing" uses.
        // Twin: `test_an_empty_intent_set_is_a_plan_that_carries_out_nothing`.
        var label = typeof(KokomiPlan).GetMethod("AimedLabel", All)!;
        Assert.Contains(Il.Strings(label), s => s.Contains("nothing"));
        Assert.Contains(Il.Calls(typeof(KokomiPlan).GetMethod("Schedule", All)!),
                        c => c.Contains("KokomiPlan.AimedLabel"));
    }

    // ======================================================================
    // 5. WELL LAID -- the morning, read from the damage side
    // ======================================================================

    [Fact]
    public void Well_laid_is_a_free_attack_with_a_floor_and_a_scaler()
    {
        var card = new ProtoKkWellLaid();
        Assert.Equal(0, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Attack, card.Type);
        Assert.Equal(CardRarity.Common, card.Rarity);

        // The `CalculatedDamageVar` TRIPLE: the base is the floor a morning
        // with no Plan pays, the extra is the per-Plan term.
        var vars = Vars(card);
        Assert.Equal(2m, vars.Single(v => v.Name == "CalculationBase").BaseValue);
        Assert.Equal(3m, vars.Single(v => v.Name == "ExtraDamage").BaseValue);
        Assert.Contains(vars, v => v.Name == "CalculatedDamage");
    }

    [Fact]
    public void Well_laid_prints_no_plan_line()
    {
        // It reads the morning; it is not part of one. A Plan line here would
        // make the card pay for a morning it had just postponed.
        Assert.False(typeof(IPlannedCard)
                         .IsAssignableFrom(typeof(ProtoKkWellLaid)));
        // `EB-539`: the morning clause left the FACE for the rider tip -- a
        // card has one face, and "already including 3" is a contradiction on a
        // bare morning -- so the face is the live total alone and the rule is
        // read one surface over (`Round19Tests`, `EB-539`).
        Assert.Equal("Deal {CalculatedDamage:diff()} damage.",
                     Face(new ProtoKkWellLaid()));
    }

    [Fact]
    public void Well_laid_reads_the_same_morning_tide_wall_reads()
    {
        // ONE FACT AND NOT TWO COUNTS. `PlansThisMorning` is written once, at
        // the drain, before the first clause runs, and cleared on the turn
        // boundary -- so the morning a now-line sees and the morning Tide
        // Wall's planned Block multiplies are the same number.
        var mine = Il.Calls(Il.Method("ProtoKkWellLaid", "get_CanonicalVars"))
            .Concat(NestedCalls(typeof(ProtoKkWellLaid)))
            .ToList();
        Assert.Contains(mine, c => c.Contains("PlansThisMorning"));

        var one = typeof(KokomiPlan).GetMethod("ResolveOne", All)!;
        Assert.Contains(Il.Calls(one), c => c.Contains("PlansThisMorning"));
    }

    // ======================================================================
    // 6. FEIGNED RETREAT -- both halves, only when planned
    // ======================================================================

    [Fact]
    public void Feigned_retreat_plans_block_and_then_damage()
    {
        // TWO CLAUSES AND THE ORDER IS THE FACE. "Gain 4 Block and deal 6
        // damage" is read top to bottom, and the Block is what guards the turn
        // the hit is taken on.
        var card = new ProtoKkFeignedRetreat();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Skill, card.Type);

        var clauses = card.PlanClauses;
        Assert.Equal(2, clauses.Count);
        Assert.Equal(KokomiPlan.Kind.Block, clauses[0].Kind);
        Assert.Equal(KokomiPlan.Aim.Self, clauses[0].Aim);
        Assert.Equal(KokomiPlan.Kind.Damage, clauses[1].Kind);
        Assert.Equal(KokomiPlan.Aim.FrontEnemy, clauses[1].Aim);
    }

    // ======================================================================
    // 7. NEREID'S ASCENSION -- the Rare, redesigned in place
    // ======================================================================

    [Fact]
    public void The_ascension_is_a_power_and_no_longer_a_plan()
    {
        // THE WHOLE REDESIGN. Written as a Plan it spent the morning it was
        // meant to pay for -- two energy, an Exhaust and a Plan slot, in a
        // deck the r14 seat measured at two Plan cards to double.
        var card = new ProtoKkNereidsAscension();
        Assert.Equal(CardType.Power, card.Type);
        Assert.Equal(CardRarity.Rare, card.Rarity);
        Assert.Equal(2, card.EnergyCost.Canonical);
        Assert.False(typeof(IPlannedCard)
                         .IsAssignableFrom(typeof(ProtoKkNereidsAscension)));
        Assert.DoesNotContain(CardKeyword.Exhaust, card.CanonicalKeywords);

        Assert.Contains(Il.Calls(Il.Method("ProtoKkNereidsAscension", "OnPlay")),
                        c => c.Contains("PowerCmd.Apply"));
    }

    [Fact]
    public void The_ascension_buys_its_turn_back_at_the_smith()
    {
        // The row prints no number the rule may move -- "every Plan twice" is
        // a rule, not an amount -- so the upgrade takes the COST clause: its
        // price is two energy on a turn that writes no Plan, and the `+` card
        // buys that turn back.
        Assert.Contains(
            Il.Calls(Il.Method("ProtoKkNereidsAscension", "OnUpgrade")),
            c => c.Contains("UpgradeBy"));
    }

    [Fact]
    public void The_doubling_is_read_per_plan_off_the_power()
    {
        // The reading, pinned where it is taken: `CarryOutTimes` is asked
        // INSIDE the drain loop, before each entry, and it asks for the POWER.
        // That still matters with the clause gone -- a Plan can play a card
        // (Moon's Reflection reaches one), so a morning can install the
        // Ascension partway through, and the Plans after it are doubled while
        // the ones already carried out are not.
        // REAL, off a real seat: the power is worn and the read moves. (A
        // structural pin could not say this -- `Enumerable.OfType`'s type
        // argument is not in the IL call name.)
        var times = typeof(KokomiPlan).GetMethod("CarryOutTimes", All)!;
        var bare = Seat.Kokomi();
        Assert.Equal(1, times.Invoke(null, new object[] { bare.Creature }));

        var risen = Seat.Kokomi().WithPower<NereidsAscensionPower>(1);
        Assert.Equal(2, times.Invoke(null, new object[] { risen.Creature }));

        var all = typeof(KokomiPlan).GetMethod("ResolveAll", All)!;
        var drain = Il.CallSequence(all).ToList();
        Assert.True(drain.IndexOf("KokomiPlan.CarryOutTimes")
                    < drain.IndexOf("KokomiPlan.ResolveEntry"));
    }

    [Fact]
    public void The_power_is_a_marker_with_nothing_to_tick()
    {
        // `CarryOutTimes` reads whether it is worn and never its amount, so a
        // second copy of the Rare doubles nothing further; and it lasts the
        // fight, so there is no `AfterSideTurnEnd` tick to get the window's
        // length wrong.
        var power = typeof(NereidsAscensionPower);
        Assert.Null(power.GetMethod("AfterSideTurnEnd",
                                    BindingFlags.Public | BindingFlags.Instance
                                    | BindingFlags.DeclaredOnly));
        Assert.Null(power.GetMethod("Wear", All));

        var times = typeof(KokomiPlan).GetMethod("CarryOutTimes", All)!;
        var twice = Seat.Kokomi().WithPower<NereidsAscensionPower>(2);
        Assert.Equal(2, times.Invoke(null, new object[] { twice.Creature }));
    }

    // ======================================================================
    // 8. THE OFFER SEAM
    // ======================================================================

    [Fact]
    public void All_five_new_rows_are_offered_by_the_arm()
    {
        // `lint_arm_pool_parity` holds this list to the sheet and to
        // `C.KOKOMI_OVERHAUL_POOL_IDS`; what a pin adds is that the rows the
        // finding asked for are actually on the OFFER seam -- the seam R252
        // forgot one arm over, which is why the gate exists.
        var slice = Il.CallSequence(
            Il.Method("KokomiOverhaulRoster", "Slice")).ToList();
        foreach (var row in new[] { "ProtoKkRiptide", "ProtoKkPincer",
                                    "ProtoKkFlank", "ProtoKkWellLaid",
                                    "ProtoKkFeignedRetreat" })
        {
            Assert.Contains(slice, c => c.Contains(row));
        }

        var starter = Il.CallSequence(
            Il.Method("KokomiOverhaulRoster", "StartingDeck")).ToList();
        Assert.DoesNotContain(starter, c => c.Contains("ProtoKkRiptide"));
    }

    // ---- helpers ---------------------------------------------------------

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    /// <summary><c>CanonicalVars</c> is protected, so it is read the way every
    /// other internal seam in this project is read.</summary>
    private static IReadOnlyList<DynamicVar> Vars(CardModel card) =>
        ((IEnumerable<DynamicVar>)typeof(CardModel)
            .GetProperty("CanonicalVars", All)!.GetValue(card)!).ToList();

    /// <summary>
    /// Every call in a type's COMPILER-GENERATED members.
    ///
    /// A `static (card, _) => ...` multiplier compiles into a method on a
    /// nested display class, so the ledger read a generated row makes is not
    /// on any method a name can ask for. This walks the nested types instead,
    /// which is the one place that lambda's body can be read back.
    /// </summary>
    private static IEnumerable<string> NestedCalls(System.Type owner) =>
        owner.GetNestedTypes(All)
            .SelectMany(t => t.GetMethods(All))
            .SelectMany(m => Il.Calls(m));
}
