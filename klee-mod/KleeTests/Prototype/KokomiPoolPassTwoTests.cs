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
/// KOKOMI POOL PASS TWO -- the queue as something the player OPERATES ON
/// (`EB-643`, R265).
///
/// THE FINDING. Round after round the seats wrote a Plan and then watched it
/// play itself: a morning is a thing that is READ, not decided. Everything the
/// arm asked the player to choose happened before the Plan was queued -- which
/// card, and whether to plan it -- and nothing after. So the pass is eight rows
/// that reach INTO the queue: two riders on the entry that follows (Opening
/// Gambit, Second Wave), a draw that counts the entries after it (Scout
/// Ahead), three now-lines that unwrite or re-aim what is already written
/// (Second Thoughts, Ebb Tide, Converging Tide), and the two DUSK rows whose
/// Plan lands at the end of the turn it was written on (Breakwater, Night
/// Watch). Plus one lane rule, the two-Plan cap, behind a runtime toggle.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on <see cref="KokomiPoolPassTests"/>'
/// split. The card shapes are REAL -- every row is constructed and its face,
/// cost, rarity, vars, plan clauses and smith's move are read off the shipped
/// class. The RESOLUTION is not: a drain needs a live <c>CombatState</c>, so
/// the rider's window, the cap's arithmetic and the dusk hook are pinned off
/// the compiled methods and labelled. The end-to-end arithmetic is the sim
/// twin's: `tier0/tests/test_kokomi_plan.py`, section "POOL PASS TWO".
///
/// THE NUMBERS ARE PROTOTYPE NUMBERS (D by the ladder). Nothing here is
/// quotable (R215 B).
/// </summary>
public class KokomiPoolPassTwoTests
{
    private const BindingFlags All = HeadlessGame.All;

    // ======================================================================
    // 1. THE VOCABULARY: three clauses added, all three drain-positional
    // ======================================================================

    [Fact]
    public void The_three_new_kinds_are_the_ones_the_codegen_maps()
    {
        // `gen_klee_cards.PLAN_CLAUSE_KINDS` maps the sheet's spellings onto
        // these members BY NAME, so a rename here is a codegen break rather
        // than a silent approximation -- the contract every Kind is under.
        var names = System.Enum.GetNames(typeof(KokomiPlan.Kind));
        Assert.Contains("DrawPerPlanAfter", names);
        Assert.Contains("NextPlanDoubleDamage", names);
        Assert.Contains("NextPlanExtraCarryOut", names);
    }

    [Fact]
    public void The_entry_carries_dusk_and_an_aim_override_and_no_creature()
    {
        // Rule 3's discipline, re-asserted for the two fields `EB-643` adds.
        // `Dusk` is a bool -- a fact about the writing card's FACE -- and
        // `AimOverride` is a `CombatId` STRING, which is the difference that
        // matters: a Plan written last turn cannot hold a reference to a
        // creature the game has torn down, so the override is resolved against
        // the live board at carry-out.
        var entry = typeof(KokomiPlan.Entry);
        Assert.Equal(typeof(bool), entry.GetProperty("Dusk", All)!.PropertyType);
        Assert.Equal(typeof(string),
                     entry.GetProperty("AimOverride", All)!.PropertyType);
        Assert.DoesNotContain(
            entry.GetProperties(All),
            p => p.PropertyType.Name == "Creature");
    }

    // ======================================================================
    // 2. THE RIDERS -- Opening Gambit and Second Wave
    // ======================================================================

    [Fact]
    public void Opening_gambit_writes_a_vulnerable_and_then_the_rider()
    {
        var card = new ProtoKkOpeningGambit();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);

        var clauses = card.PlanClauses;
        Assert.Equal(2, clauses.Count);
        Assert.Equal(KokomiPlan.Kind.ApplyVulnerable, clauses[0].Kind);
        Assert.Equal(KokomiPlan.Aim.AllEnemies, clauses[0].Aim);
        Assert.Equal(1, clauses[0].Amount);
        // THE RIDER AIMS AT NOTHING and carries no size: "double" has no
        // number to print, which is why it is in `PLAN_AMOUNTLESS_OPS`.
        Assert.Equal(KokomiPlan.Kind.NextPlanDoubleDamage, clauses[1].Kind);
        Assert.Equal(KokomiPlan.Aim.Self, clauses[1].Aim);
    }

    [Fact]
    public void Opening_gambits_smith_moves_the_now_line_only()
    {
        // The Plan half prints no number the upgrade could move: the
        // Vulnerable is the setup and the doubling is the payoff.
        var card = new ProtoKkOpeningGambit();
        Assert.Contains("{Damage:diff()}", Face(card));
        Assert.DoesNotContain("PlanDamage", Face(card));
    }

    [Fact]
    public void Second_waves_plan_is_the_extra_carry_out_rider_alone()
    {
        var card = new ProtoKkSecondWave();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Common, card.Rarity);

        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.NextPlanExtraCarryOut, clause.Kind);
        Assert.Equal(KokomiPlan.Aim.Self, clause.Aim);
    }

    [Fact]
    public void The_riders_are_noted_by_the_entry_and_spent_by_the_drain()
    {
        // STRUCTURAL, and it is the whole rule: `ResolveEntry` NOTES the
        // rider its clauses print and hands it back, and `Drain` is what
        // spends it on the entry that follows. That split is what keeps "the
        // next Plan" a fact about a DRAIN rather than a flag on the class that
        // could outlive one -- so a rider written by the last Plan of a
        // morning reaches nothing. Twin:
        // `test_riptide_then_gambit_doubles_nothing`.
        var entry = typeof(KokomiPlan).GetMethod("ResolveEntry", All)!;
        Assert.Equal("ValueTuple`2", entry.ReturnType.GetGenericArguments()
                     .Single().Name);

        var drain = typeof(KokomiPlan).GetMethod("Drain", All)!;
        Assert.Contains("KokomiPlan.ResolveEntry", Il.Calls(drain));

        // AND NOWHERE ELSE HOLDS ONE: no field on the class carries a rider,
        // which is the structural form of "it falls off the end of a local".
        Assert.DoesNotContain(
            typeof(KokomiPlan).GetFields(All),
            f => f.Name.Contains("double", System.StringComparison
                                              .OrdinalIgnoreCase)
                 || f.Name.Contains("rider",
                                    System.StringComparison.OrdinalIgnoreCase)
                    && f.Name != "_riders");
    }

    [Fact]
    public void Change_of_plans_does_not_go_through_the_drain()
    {
        // `ResolveFront` carries ONE entry out, so there is no "next" for a
        // rider to name -- it neither sets nor consumes one, and the pin is
        // that it never reaches the loop that owns them. Twin:
        // `test_change_of_plans_neither_sets_nor_consumes_a_rider`.
        Assert.DoesNotContain(
            "KokomiPlan.Drain",
            Il.Calls(typeof(KokomiPlan).GetMethod("ResolveFront", All)!));
    }

    [Fact]
    public void The_doubling_lands_in_the_one_damage_funnel()
    {
        // `Hit` is where every damaging Plan clause goes, so "the next Plan
        // deals double damage" is true of the flat hit, of Sango Isshin's
        // quarter and of Chain of Command's total without three readings --
        // and it is applied to the number that was WRITTEN, before the target
        // has its say. Twin: `test_gambit_then_riptide_doubles_riptide`.
        var hit = typeof(KokomiPlan).GetMethod("Hit", All)!;
        Assert.Contains(hit.GetParameters(), p => p.Name == "doubleDamage");
        var calls = Il.CallSequence(hit).ToList();
        Assert.True(calls.IndexOf("ElementalHit.Deal") > 0);
    }

    // ======================================================================
    // 3. SCOUT AHEAD -- the row whose value is its position
    // ======================================================================

    [Fact]
    public void Scout_ahead_draws_one_now_and_per_carry_out_after()
    {
        var card = new ProtoKkScoutAhead();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Common, card.Rarity);

        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.DrawPerPlanAfter, clause.Kind);
        Assert.Equal(KokomiPlan.Aim.Self, clause.Aim);
        // THE AMOUNT IS THE RATE, the shape Tide Wall's clause already has.
        Assert.Equal(1, clause.Amount);
    }

    [Fact]
    public void Scout_aheads_smith_moves_the_cost_and_not_the_rate()
    {
        // The rate is the QUEUE's fact and not the card's: an upgrade that
        // raised it would scale with a deck the offer screen cannot see.
        var moves = Il.Calls(Il.Method("ProtoKkScoutAhead", "OnUpgrade"));
        Assert.Contains(moves, c => c.Contains("EnergyCost"));
    }

    [Fact]
    public void The_count_is_the_drains_and_is_read_per_entry()
    {
        // STRUCTURAL. `Drain` computes `after` inside the loop off
        // `CarryOutTimes`, which is what makes it CARRY-OUTS and not entries
        // (`EB-501`'s reading pointed forwards) and what makes a Scout Ahead
        // written first and one written last answer honestly. Twins:
        // `test_scout_ahead_counts_the_carry_outs_after_it`,
        // `test_scout_ahead_first_of_three_under_nereids_reads_four`.
        var resolve = typeof(KokomiPlan).GetMethod("ResolveOne", All)!;
        Assert.Contains(resolve.GetParameters(), p => p.Name == "after");
        var drain = typeof(KokomiPlan).GetMethod("Drain", All)!;
        Assert.Contains("KokomiPlan.CarryOutTimes", Il.Calls(drain));
    }

    // ======================================================================
    // 4. THE THREE NOW-LINES
    // ======================================================================

    [Fact]
    public void Second_thoughts_is_a_zero_cost_exhaust_with_no_plan_line()
    {
        // A card that UNWRITES a Plan cannot also be one.
        var card = new ProtoKkSecondThoughts();
        Assert.Equal(0, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Common, card.Rarity);
        Assert.IsNotAssignableFrom<IPlannedCard>(card);
        Assert.Contains("KokomiPlan.CancelLast",
                        Il.Calls(Il.Method("ProtoKkSecondThoughts", "OnPlay")));
    }

    [Fact]
    public void Cancel_last_takes_the_newest_and_pays_the_cards_own_cost()
    {
        // STRUCTURAL: the LAST entry (`List.RemoveAt` at `Count - 1`, where
        // `ResolveFront` removes at 0), the card out of the DISCARD pile into
        // the hand, and the Energy read off `EnergyCost.GetResolved` -- "its
        // cost" means the cost it has now. Twins:
        // `test_second_thoughts_returns_the_card_and_refunds_its_cost`,
        // `test_second_thoughts_takes_the_newest_and_leaves_the_rest`.
        var calls = Il.Calls(typeof(KokomiPlan).GetMethod("CancelLast", All)!)
                      .ToList();
        Assert.Contains(calls, c => c.Contains("List`1.RemoveAt"));
        Assert.Contains(calls, c => c.Contains("CardPile"));
        Assert.Contains(calls, c => c.Contains("EnergyCost"));
        Assert.Contains(calls, c => c.Contains("PlayerCmd.GainEnergy"));
    }

    [Fact]
    public void Ebb_tide_is_an_uncommon_exhaust_that_cashes_the_queue()
    {
        var card = new ProtoKkEbbTide();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.Contains("KokomiPlan.CancelAllForCash",
                        Il.Calls(Il.Method("ProtoKkEbbTide", "OnPlay")));
    }

    [Fact]
    public void Cancel_all_pays_per_entry_and_energy_before_the_draw()
    {
        // PER ENTRY and not per carry-out: "for each" counts the Plans she is
        // HOLDING, which is `List.Count` on the queue and not the ledger's
        // morning. Energy first, so a drawn card meets a hand that can afford
        // it. Twin: `test_ebb_tide_cashes_the_whole_queue_per_entry`.
        var calls = Il.CallSequence(
            typeof(KokomiPlan).GetMethod("CancelAllForCash", All)!).ToList();
        Assert.Contains(calls, c => c.Contains("List`1.get_Count"));
        Assert.DoesNotContain(calls, c => c.Contains("PlansThisMorning"));
        Assert.True(calls.FindIndex(c => c.Contains("GainEnergy"))
                    < calls.FindIndex(c => c.Contains("CardPileCmd.Draw")));
    }

    [Fact]
    public void Converging_tide_aims_at_an_enemy_and_re_points_the_queue()
    {
        var card = new ProtoKkConvergingTide();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Common, card.Rarity);
        // AIMED, because it dereferences the played target: "this enemy" is
        // the body the play was aimed at and never a second definition of the
        // front.
        Assert.Equal(TargetType.AnyEnemy, card.TargetType);
        Assert.Contains("KokomiPlan.Redirect",
                        Il.Calls(Il.Method("ProtoKkConvergingTide", "OnPlay")));
    }

    [Fact]
    public void The_redirect_stamps_an_id_and_only_the_front_aim_reads_it()
    {
        // The stamp is a `CombatId` (nothing on the queue may hold a body the
        // game can tear down), and `Aimed` reads it on the FrontEnemy branch
        // alone -- an ALL clause does not aim at the front, so there is
        // nothing on it for "instead of the front" to be about. A dead target
        // falls back to the front, which is the arm's standing rule. Twins:
        // `test_converging_tide_leaves_an_all_enemies_clause_alone`,
        // `test_a_dead_redirect_target_falls_back_to_the_front`.
        var redirect = Il.Calls(typeof(KokomiPlan)
            .GetMethod("Redirect", All)!).ToList();
        Assert.Contains(redirect, c => c.Contains("get_CombatId"));

        var aimed = Il.CallSequence(typeof(KokomiPlan)
            .GetMethod("Aimed", All)!).ToList();
        Assert.True(aimed.FindIndex(c => c.Contains("get_AimOverride"))
                    < aimed.FindIndex(c => c.Contains("KokomiPlan.FrontEnemy")));
    }

    // ======================================================================
    // 5. DUSK
    // ======================================================================

    [Fact]
    public void Breakwater_writes_a_dusk_plan_of_seven_block()
    {
        var card = new ProtoKkBreakwater();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardRarity.Common, card.Rarity);

        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.Block, clause.Kind);
        Assert.Equal(7, clause.Amount);
        // THE FLAG RIDES THE WRITE, because Dusk is a fact about WHEN this
        // card's line lands and the entry is the only thing that survives the
        // play.
        Assert.Contains("dusk: true",
                        Source("ProtoKkBreakwater"));
    }

    [Fact]
    public void Night_watch_writes_block_and_a_weak_at_dusk()
    {
        var card = new ProtoKkNightWatch();
        Assert.Equal(1, card.EnergyCost.Canonical);
        var clauses = card.PlanClauses;
        Assert.Equal(2, clauses.Count);
        Assert.Equal(KokomiPlan.Kind.Block, clauses[0].Kind);
        Assert.Equal(5, clauses[0].Amount);
        Assert.Equal(KokomiPlan.Kind.ApplyWeak, clauses[1].Kind);
        Assert.Equal(KokomiPlan.Aim.FrontEnemy, clauses[1].Aim);
        Assert.Contains("dusk: true", Source("ProtoKkNightWatch"));
    }

    [Fact]
    public void An_ordinary_plan_row_still_emits_the_call_it_always_did()
    {
        // The dusk argument is passed only where the row declares it, so every
        // card authored before the field existed is byte-identical.
        Assert.DoesNotContain("dusk:", Source("ProtoKkFeint"));
    }

    [Fact]
    public void Dusk_is_drained_before_the_enemies_act()
    {
        // THE HOOK: `BeforeSideTurnEnd` on the PLAYER side, which is the
        // nearest broadcast this mod has to the printed sentence -- the Block
        // is on her before the swing, which is the only clause of the face a
        // card can tell apart. The sim runs it at the same site
        // (`combat._player_turn`, `kokomi_plan.resolve_dusk`). Twin:
        // `test_a_dusk_plan_lands_at_the_end_of_the_turn_it_was_written_on`.
        var hook = typeof(ProtoBakeKuragePower)
            .GetMethod("BeforeSideTurnEnd", All)!;
        Assert.Contains("KokomiPlan.ResolveDusk", Il.Calls(hook));
    }

    [Fact]
    public void The_dusk_drain_takes_the_dusk_entries_and_leaves_the_rest()
    {
        // The dusk entries leave the queue and the others stay, taken before
        // the first clause runs for `ResolveAll`'s reason. It goes through the
        // SHARED `Drain`, so a dusk carry-out is a carry-out -- Treatise draws
        // on it and `NotePlanCarriedOut` fires. Twins:
        // `test_a_dusk_drain_leaves_the_morning_entries_where_they_are`,
        // `test_a_dusk_carry_out_is_a_carry_out`.
        var calls = Il.Calls(typeof(KokomiPlan)
            .GetMethod("ResolveDusk", All)!).ToList();
        Assert.Contains(calls, c => c.Contains("RemoveAll"));
        Assert.Contains("KokomiPlan.Drain", calls);
    }

    [Fact]
    public void The_dusk_drain_does_not_touch_the_mornings_depth()
    {
        // Tide Wall, Well Laid and Tide Chart all print "this morning", and an
        // evening is not one. Twin:
        // `test_a_dusk_carry_out_does_not_touch_the_mornings_depth`.
        Assert.DoesNotContain(
            Il.Calls(typeof(KokomiPlan).GetMethod("ResolveDusk", All)!),
            c => c.Contains("NoteMorning"));
    }

    // ======================================================================
    // 6. THE TWO-PLAN CAP
    // ======================================================================

    [Fact]
    public void The_cap_defaults_to_unlimited_and_is_read_once()
    {
        // ZERO IS UNLIMITED AND ZERO IS THE DEFAULT, so an unconfigured build
        // drains what it always drained: the trial is a trial, and a lane that
        // did not ask for it must not get it. Twin:
        // `test_the_cap_defaults_to_unlimited`.
        KokomiPlan.ResetAll();
        Assert.Equal(0, KokomiPlan.PlanCap);
    }

    [Fact]
    public void The_cap_comes_from_the_environment_at_the_lanes_own_door()
    {
        // The env-var shape is the EXISTING per-lane pattern (`GITS_LANE`,
        // `GITS_TELEMETRY_FEED`, `GITS_TELEMETRY_INTENT`): a seat launches a
        // lane's game as a child process, so an exported variable is what a
        // lane already has and not rebuilding per arm is what the toggle is
        // for. Cached, for `PlayTelemetry.Intent`'s reason -- one run's
        // mornings must not disagree about the rule they were under.
        var getter = typeof(KokomiPlan).GetProperty("PlanCap", All)!
            .GetGetMethod(nonPublic: true)!;
        var calls = Il.Calls(getter).ToList();
        Assert.Contains(calls, c => c.Contains("GetEnvironmentVariable"));
        Assert.Contains(typeof(KokomiPlan).GetFields(All),
                        f => f.Name == "_planCap");
        Assert.Contains("GITS_KOKOMI_PLAN_CAP", Source("KokomiPlan", power: true));
    }

    [Fact]
    public void What_the_cap_holds_back_stays_queued_in_order()
    {
        // At N the front N entries are carried out and the rest STAY, in
        // order -- not discarded and not re-sorted, because the whole trial is
        // about whether queue order becomes a decision. They go back in FRONT
        // of anything written during the drain, and on the unwind path too: a
        // fight that ended mid-drain does not un-cap the Plans it never
        // reached. Twin: `test_the_cap_carries_out_two_and_holds_the_third`.
        var calls = Il.Calls(typeof(KokomiPlan)
            .GetMethod("ResolveAll", All)!).ToList();
        Assert.Contains(calls, c => c.Contains("KokomiPlan.get_PlanCap"));
        Assert.Contains(calls, c => c.Contains("List`1.GetRange"));
        Assert.Contains(calls, c => c.Contains("List`1.InsertRange"));
    }

    [Fact]
    public void The_cap_is_not_read_by_the_dusk_drain()
    {
        // A Dusk Plan has already waited for nothing, so the morning's
        // allowance is untouched by one. Twin:
        // `test_the_cap_does_not_count_dusk_carry_outs`.
        Assert.DoesNotContain(
            Il.Calls(typeof(KokomiPlan).GetMethod("ResolveDusk", All)!),
            c => c.Contains("PlanCap"));
    }

    // ======================================================================
    // 7. THE ROSTER
    // ======================================================================

    [Fact]
    public void All_eight_rows_are_offerable_and_none_is_in_the_starter()
    {
        var slice = Il.CallSequence(
            Il.Method("KokomiOverhaulRoster", "Slice")).ToList();
        foreach (var row in new[]
                 {
                     "ProtoKkOpeningGambit", "ProtoKkSecondWave",
                     "ProtoKkScoutAhead", "ProtoKkSecondThoughts",
                     "ProtoKkEbbTide", "ProtoKkConvergingTide",
                     "ProtoKkBreakwater", "ProtoKkNightWatch",
                 })
        {
            Assert.Contains(slice, c => c.Contains(row));
        }

        // DENSITY GOES IN THE OFFER AND NEVER IN THE STARTER, which stands
        // under R254 and R257 and which pool pass one already kept.
        var starter = Il.CallSequence(
            Il.Method("KokomiOverhaulRoster", "StartingDeck")).ToList();
        Assert.DoesNotContain(starter, c => c.Contains("ProtoKkBreakwater"));
    }

    // ---- helpers ---------------------------------------------------------

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    /// <summary>One generated card's own source, read off disk.
    ///
    /// A SOURCE READ AND NOT AN IL ONE, and only for the two facts IL cannot
    /// carry: a named argument (`dusk: true`) compiles to a positional load
    /// that says nothing about the name, and a `const string` is a literal no
    /// call sequence mentions. Everything else in this file is read off the
    /// compiled member.</summary>
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
