using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;
using static KleeMod.Powers.StagePerformer;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE (v2, the re-founding): the rules, one pin per rule edge.
///
/// The design is <c>review/active/furina-refounding-2026-10-03.md</c> -- sec.1's
/// rules as sec.8 amends them, sec.2's cast, sec.10's sheet. The sim's
/// reference is <c>tier0/engine/furina_v2.py</c> and its pins
/// <c>tier0/tests/test_furina_v2_slice.py</c>: every test here that mirrors one
/// says which. NOTHING MEASURED HERE IS QUOTABLE: a prototype arm's arithmetic.
/// </summary>
public class FurinaStageV2Tests
{
    private static StageMods Mods(int rehearsal = 0, int bowDraw = 0,
                                  int bowActs = 1, int bowBlock = 0,
                                  bool fiveCentury = false, int critics = 0,
                                  int starBilling = 0, int starTurn = 0,
                                  int fullHouse = 0, int capacity = 3) =>
        new()
        {
            Rehearsal = rehearsal, BowDraw = bowDraw, BowActs = bowActs,
            BowBlock = bowBlock, FiveCentury = fiveCentury,
            CriticsDarling = critics, StarBilling = starBilling,
            StarTurn = starTurn, FullHouse = fullHouse, Capacity = capacity,
        };

    // ---- rule 1: three seats, Usher opens, acts front to back ----------------

    [Fact]
    public void Salon_solitaire_opens_with_usher_once()
    {
        // test_salon_solitaire_opens_with_usher_once
        var kit = StageKit.Of();
        Assert.True(kit.Stage.Open());
        Assert.Equal(new[] { Usher }, kit.Company);
        Assert.False(kit.Stage.Open());
        Assert.Equal(new[] { Usher }, kit.Company);
        // A stage something else filled first is left as it is.
        var other = StageKit.Of(Crabaletta);
        Assert.True(other.Stage.Open());
        Assert.Equal(new[] { Crabaletta }, other.Company);
    }

    [Fact]
    public void Acts_run_front_to_back_so_seat_order_funds_a_star()
    {
        // test_acts_run_front_to_back_so_seat_order_funds_a_star
        var funded = StageKit.With(1, Charlotte, Neuvillette);
        StageKit.Run(funded.Director.EndOfTurn());
        Assert.Equal(1, funded.Beats(FurinaStageLedger.ActEvent, Neuvillette));
        Assert.Equal(0, funded.Stage.Fanfare);

        var starved = StageKit.With(1, Neuvillette, Charlotte);
        StageKit.Run(starved.Director.EndOfTurn());
        Assert.Equal(1, starved.Beats(FurinaStageLedger.SkipEvent, Neuvillette));
        Assert.Equal(2, starved.Stage.Fanfare);
    }

    [Fact]
    public void The_trio_acts()
    {
        // test_the_trio_acts
        var kit = StageKit.Of(Usher, Chevalmarin, Crabaletta);
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal(new[]
        {
            "block Usher 4",
            "damage Chevalmarin All 2 None",
            "damage Crabaletta Random 5 None",
        }, kit.Board.Log);
    }

    [Fact]
    public void Performers_have_no_bars_and_no_body_shows_one()
    {
        // Rule 1: performers take no hits and cannot be emptied. The body is
        // a pet with no visible bar, and nothing hooks her damage any more.
        Assert.Null(typeof(FurinaStageLedger).GetMethod("Absorb"));
        Assert.Null(typeof(StageSeat).GetProperty("Fanfare"));
        Assert.DoesNotContain("FurinaStage.AbsorbHit",
            Il.Calls(Il.Method("FurinaResourceHooks", "ModifyHpLostBeforeOsty")));
    }

    // ---- rule 5: one number; a star pays, and a payment is not a Spend ------

    [Fact]
    public void A_star_payment_is_not_a_spend()
    {
        // test_a_star_payment_is_not_a_spend
        var kit = StageKit.With(3, Clorinde, Navia);
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal(1, kit.Stage.PaidThisTurn);
        Assert.Equal(0, kit.Stage.SpentThisTurn);
        Assert.DoesNotContain(kit.Board.Log, l => l.StartsWith("clorinde"));
        Assert.Equal(1, kit.Beats(FurinaStageLedger.ActEvent, Navia));
        // Navia read 0 spent: only Clorinde's act hit.
        Assert.Equal(new[] { "damage Clorinde Random 6 Electro" }, kit.Board.Hits);
    }

    [Fact]
    public void A_short_star_skips_stays_and_spends_nothing()
    {
        // test_a_short_star_skips_stays_and_spends_nothing
        var kit = StageKit.With(1, Neuvillette);
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal(1, kit.Stage.Fanfare);
        Assert.Equal(new[] { Neuvillette }, kit.Company);
        Assert.Equal(1, kit.Beats(FurinaStageLedger.SkipEvent, Neuvillette));
        Assert.Equal(0, kit.Stage.PaidThisTurn);
        Assert.Empty(kit.Board.Hits);
    }

    [Fact]
    public void Fanfare_has_no_fade_and_no_cap()
    {
        // test_fanfare_has_no_fade_and_no_cap
        var kit = StageKit.With(40, Usher);
        StageKit.Run(kit.Director.EndOfTurn());
        kit.Stage.OpenTurn();
        Assert.Equal(40, kit.Stage.Fanfare);
    }

    // ---- rule 3: the Bow, a free act, then 1 Fanfare -------------------------

    [Fact]
    public void A_bow_is_a_free_act_then_one_fanfare()
    {
        // test_a_bow_is_a_free_act_then_one_fanfare
        var kit = StageKit.Of(Neuvillette, Clorinde, Charlotte);
        Assert.Equal(StageSummonResult.Evict,
                     StageKit.Run(kit.Director.SummonGuest(Sigewinne, 0)));
        Assert.Equal(new[] { Clorinde, Charlotte, Sigewinne }, kit.Company);
        // Unpaid (the Bow is free), and no line bonus: he left before it.
        Assert.Equal(new[] { "damage Neuvillette All 7 Hydro" }, kit.Board.Hits);
        Assert.Equal(0, kit.Stage.PaidThisTurn);
        Assert.Equal(FurinaStageLaw.BowFanfare, kit.Stage.Fanfare);
        var order = kit.Stage.Beats
            .Where(b => b.Event is FurinaStageLedger.ActEvent
                        or FurinaStageLedger.GainEvent)
            .Select(b => b.Event).ToList();
        Assert.Equal(new[] { FurinaStageLedger.ActEvent, FurinaStageLedger.GainEvent },
                     order);
    }

    [Fact]
    public void A_second_copy_of_a_guest_bows_it_and_it_keeps_its_seat()
    {
        // test_a_second_copy_of_a_guest_bows_it_and_returns_it
        var kit = StageKit.Of(Clorinde, Usher);
        Assert.Equal(StageSummonResult.Repeat,
                     StageKit.Run(kit.Director.SummonGuest(Clorinde, 0)));
        Assert.Equal(new[] { Clorinde, Usher }, kit.Company);
        Assert.Equal(1, kit.Beats(FurinaStageLedger.BowEvent, Clorinde));
        Assert.Equal(1, kit.Stage.Fanfare);
        Assert.Equal(new[] { "damage Clorinde Random 6 Electro" }, kit.Board.Hits);
    }

    // ---- rule 4: overflow -- Salon summons never evict guests ----------------

    [Fact]
    public void A_full_stage_bows_the_front_most_salon_member()
    {
        // test_a_full_stage_bows_the_front_most_salon_member
        var kit = StageKit.Of(Neuvillette, Usher, Chevalmarin);
        Assert.Equal(StageSummonResult.Evict,
                     StageKit.Run(kit.Director.SummonSalon(Crabaletta)));
        Assert.Equal(new[] { Neuvillette, Chevalmarin, Crabaletta }, kit.Company);
        Assert.Equal(1, kit.Beats(FurinaStageLedger.BowEvent));
        Assert.Equal(1, kit.Beats(FurinaStageLedger.BowEvent, Usher));
    }

    [Fact]
    public void A_guest_summon_onto_a_mixed_stage_also_bows_a_salon_member()
    {
        // test_a_guest_summon_onto_a_mixed_stage_also_bows_a_salon_member
        var kit = StageKit.Of(Navia, Usher, Clorinde);
        StageKit.Run(kit.Director.SummonGuest(Charlotte, 0));
        Assert.Equal(new[] { Navia, Clorinde, Charlotte }, kit.Company);
    }

    public static TheoryData<StagePerformer[], StagePerformer> Overflow()
    {
        var data = new TheoryData<StagePerformer[], StagePerformer>();
        var stages = new[]
        {
            new[] { Usher, Neuvillette, Clorinde },
            new[] { Neuvillette, Usher, Clorinde },
            new[] { Neuvillette, Clorinde, Usher },
            new[] { Navia, Charlotte, Sigewinne },
            new[] { Chevalmarin, Usher, Navia },
        };
        foreach (var stage in stages)
        {
            foreach (var member in new[] { Usher, Chevalmarin, Crabaletta })
            {
                data.Add(stage, member);
            }
        }
        return data;
    }

    [Theory]
    [MemberData(nameof(Overflow))]
    public void Overflow_never_evicts_a_guest_for_a_salon_summon(
        StagePerformer[] stage, StagePerformer member)
    {
        // test_overflow_never_evicts_a_guest_for_a_salon_summon
        var kit = StageKit.Of(stage);
        var guests = stage.Where(FurinaStage.IsGuest).ToList();
        StageKit.Run(kit.Director.SummonSalon(member));
        Assert.All(guests, g => Assert.Contains(g, kit.Company));
        Assert.All(guests, g => Assert.Equal(0, kit.Beats(FurinaStageLedger.BowEvent, g)));
    }

    [Fact]
    public void The_walk_on_is_one_act_and_one_fanfare_without_a_seat()
    {
        // test_the_walk_on_is_one_act_and_one_fanfare_without_a_seat
        var kit = StageKit.Of(Neuvillette, Clorinde, Charlotte);
        Assert.Equal(StageSummonResult.WalkOn,
                     StageKit.Run(kit.Director.SummonSalon(Usher)));
        Assert.Equal(new[] { Neuvillette, Clorinde, Charlotte }, kit.Company);
        Assert.Equal(1, kit.Beats(FurinaStageLedger.ActEvent, Usher));
        Assert.Equal(new[] { "block Usher 4" }, kit.Board.Log);
        Assert.Equal(1, kit.Stage.Fanfare);
        Assert.Equal(1, kit.Beats(FurinaStageLedger.WalkOnEvent));
    }

    [Fact]
    public void A_guest_summon_onto_three_guests_bows_the_front_guest()
    {
        // test_a_guest_summon_onto_three_guests_bows_the_front_guest
        var kit = StageKit.Of(Navia, Clorinde, Charlotte);
        StageKit.Run(kit.Director.SummonGuest(Neuvillette, 0));
        Assert.Equal(new[] { Clorinde, Charlotte, Neuvillette }, kit.Company);
        Assert.Equal(1, kit.Beats(FurinaStageLedger.BowEvent));
        Assert.Equal(1, kit.Beats(FurinaStageLedger.BowEvent, Navia));
    }

    [Fact]
    public void A_summon_takes_the_back_most_free_seat()
    {
        var kit = StageKit.Of(Usher);
        StageKit.Run(kit.Director.SummonSalon(Crabaletta));
        StageKit.Run(kit.Director.SummonGuest(Clorinde, 0));
        Assert.Equal(new[] { Usher, Crabaletta, Clorinde }, kit.Company);
        Assert.Equal(0, kit.Beats(FurinaStageLedger.BowEvent));
    }

    // ---- the flow counts (sec.8) -------------------------------------------------

    [Fact]
    public void Flow_counts_persist_through_end_of_turn_acts_and_reset_at_turn_start()
    {
        // test_flow_counts_persist_through_end_of_turn_acts_and_reset_at_turn_start
        var kit = StageKit.With(5, Navia);
        Assert.Equal(3, StageKit.Run(kit.Director.Spend(3)));
        Assert.Equal(3, kit.Stage.SpentThisTurn);
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal(new[] { "damage Navia Random 6 Geo" }, kit.Board.Hits);
        Assert.Equal(3, kit.Stage.SpentThisTurn);
        kit.Stage.OpenTurn();
        Assert.Equal(0, kit.Stage.SpentThisTurn);
        Assert.Equal(0, kit.Stage.GainedThisTurn);
    }

    [Fact]
    public void Gained_this_turn_counts_bows_and_charlotte_until_turn_start()
    {
        // test_gained_this_turn_counts_bows_and_charlotte_until_turn_start
        var kit = StageKit.Of(Charlotte);
        StageKit.Run(kit.Director.Gain(3));
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal(3 + FurinaStageLaw.ActCharlotteGain, kit.Stage.GainedThisTurn);
        kit.Stage.OpenTurn();
        Assert.Equal(0, kit.Stage.GainedThisTurn);
    }

    [Fact]
    public void Ousia_reads_gained_and_pneuma_reads_spent_not_paid()
    {
        // test_ousia_reads_gained_and_pneuma_reads_spent_not_paid: the two
        // counts the readers multiply, read off the ledger.
        var kit = StageKit.With(4, Clorinde);
        StageKit.Run(kit.Director.Cue(0));                // pays 1: not spent
        Assert.Equal(0, kit.Stage.SpentThisTurn);
        Assert.Equal(1, kit.Stage.PaidThisTurn);
        StageKit.Run(kit.Director.Gain(3));
        Assert.Equal(3, kit.Stage.GainedThisTurn);
    }

    // ---- Spend on cards, and Clorinde's line ----------------------------------------

    [Fact]
    public void A_spend_of_three_and_clorinde_answers_with_a_flat_four()
    {
        // test_curtain_rise_spends_three_for_seventeen_and_clorinde_answers
        var kit = StageKit.With(3, Clorinde);
        Assert.Equal(3, StageKit.Run(kit.Director.Spend(3)));
        Assert.Equal(0, kit.Stage.Fanfare);
        Assert.Equal(3, kit.Stage.SpentThisTurn);
        Assert.Equal(new[] { "clorinde 4" }, kit.Board.Hits);
    }

    [Fact]
    public void A_short_spend_is_refused_and_moves_nothing()
    {
        // test_curtain_rise_short_deals_seven: the mode is not offered, and
        // a payment asked for anyway takes nothing.
        var kit = StageKit.With(2, Clorinde);
        Assert.False(kit.Stage.CanSpend(3));
        Assert.Equal(0, StageKit.Run(kit.Director.Spend(3)));
        Assert.Equal(2, kit.Stage.Fanfare);
        Assert.Empty(kit.Board.Hits);
    }

    [Fact]
    public void Spend_all_takes_everything_and_zero_is_no_spend()
    {
        // test_bravura_spends_all_and_zero_is_no_spend
        var empty = StageKit.Of(Clorinde);
        Assert.Equal(0, StageKit.Run(empty.Director.SpendAll()));
        Assert.Empty(empty.Board.Hits);
        Assert.Equal(0, empty.Stage.SpentThisPlay);

        var kit = StageKit.With(5);
        Assert.Equal(5, StageKit.Run(kit.Director.SpendAll()));
        Assert.Equal(0, kit.Stage.Fanfare);
        Assert.Equal(5, kit.Stage.SpentThisPlay);
        Assert.Equal(5, kit.Stage.SpentThisTurn);
    }

    // ---- rule 6: Rehearsal -------------------------------------------------------

    [Fact]
    public void Rehearsal_scales_damage_and_block_acts_only()
    {
        // test_rehearsal_scales_damage_and_block_acts_only
        var kit = StageKit.With(Mods(rehearsal: 1), 0, Usher, Crabaletta, Charlotte);
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal(FurinaStageLaw.ActUsherBlock + 1, kit.Board.BlockGained);
        Assert.Equal(FurinaStageLaw.ActCrabalettaDamage + 1, kit.Board.Dealt);
        Assert.Equal(FurinaStageLaw.ActCharlotteGain, kit.Stage.Fanfare);
    }

    [Fact]
    public void Rehearsal_does_not_scale_clorindes_line()
    {
        // test_rehearsal_does_not_scale_clorindes_line
        var kit = StageKit.With(Mods(rehearsal: 2), 3, Clorinde);
        StageKit.Run(kit.Director.Spend(3));
        Assert.Equal(new[] { "clorinde 4" }, kit.Board.Hits);
    }

    [Fact]
    public void Rehearsal_is_a_power_with_stacks_read_into_the_mods()
    {
        FurinaStageLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState().WithPower<RehearsalPower>(2);
        Assert.Equal(2, FurinaStage.ModsOf(seat.Creature).Rehearsal);
        Assert.Equal(2, FurinaStageLedger.For(seat.Creature).Rehearsal);
        FurinaStageLedger.ResetAll();
    }

    // ---- rule 7: Cue --------------------------------------------------------------

    [Fact]
    public void A_cue_acts_the_chosen_performer_and_a_star_pays()
    {
        // test_a_cue_acts_the_chosen_performer_and_a_star_pays
        var kit = StageKit.With(1, Usher, Clorinde);
        StageKit.Run(kit.Director.Cue(1));
        Assert.Equal(1, kit.Beats(FurinaStageLedger.CueEvent, Clorinde));
        Assert.Equal(1, kit.Stage.PaidThisTurn);
        Assert.Equal(new[] { "damage Clorinde Random 6 Electro" }, kit.Board.Hits);
    }

    [Fact]
    public void A_short_star_cued_skips_and_nothing_else_moves()
    {
        // test_a_short_star_cued_skips_and_the_card_still_blocks
        var kit = StageKit.Of(Neuvillette);
        StageKit.Run(kit.Director.Cue(0));
        Assert.Equal(1, kit.Beats(FurinaStageLedger.SkipEvent, Neuvillette));
        Assert.Empty(kit.Board.Hits);
    }

    [Fact]
    public void A_cue_on_an_empty_stage_does_nothing()
    {
        var kit = StageKit.Of();
        StageKit.Run(kit.Director.Cue(null));
        StageKit.Run(kit.Director.Cue(0));
        Assert.Empty(kit.Board.Log);
    }

    [Fact]
    public void Bis_cues_the_one_chosen_performer_twice()
    {
        var kit = StageKit.With(2, Usher, Clorinde);
        StageKit.Run(kit.Director.Cue(1, times: 2));
        Assert.Equal(2, kit.Stage.PaidThisTurn);
        Assert.Equal(2, kit.Board.Hits.Count());
        Assert.DoesNotContain(kit.Board.Log, l => l.StartsWith("block"));
    }

    [Fact]
    public void Step_forward_moves_the_chosen_performer()
    {
        // test_step_forward_moves_the_chosen_performer
        var kit = StageKit.Of(Neuvillette, Charlotte);
        StageKit.Run(kit.Director.StepForward(1));
        Assert.Equal(new[] { Charlotte, Neuvillette }, kit.Company);
    }

    [Fact]
    public void The_picker_asks_only_with_two_or_more_and_scripts_headless()
    {
        FurinaStageLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        Assert.Null(StageKit.Run(FurinaStage.ChooseSeat(
            null!, seat.Player, FurinaStage.SeatPick.Cue)));
        stage.Seat(Usher);
        Assert.Equal(0, StageKit.Run(FurinaStage.ChooseSeat(
            null!, seat.Player, FurinaStage.SeatPick.Cue)));
        stage.Seat(Clorinde);
        FurinaStage.PickOverride = (_, _) => 1;
        try
        {
            Assert.Equal(1, StageKit.Run(FurinaStage.ChooseSeat(
                null!, seat.Player, FurinaStage.SeatPick.Bow)));
        }
        finally
        {
            FurinaStage.PickOverride = null;
            FurinaStageLedger.ResetAll();
        }
        // The panel is the grid screen, with its own prompt per verb.
        Assert.Contains("CardSelectCmd.FromSimpleGrid",
            Il.Calls(Il.Method("FurinaStage", "ChooseSeat")));
        foreach (var name in new[] { "Cue", "StepForward", "FinalBow" })
        {
            Assert.Contains("FurinaStage.ChooseSeat",
                Il.Calls(Il.Method("FurinaStage", name)));
        }
    }

    // ---- the guests' lines and acts (sec.2, sec.8, sec.10) -------------------

    [Fact]
    public void Escoffier_makes_only_the_first_salon_summon_card_free()
    {
        // test_escoffier_makes_only_the_first_salon_summon_card_free
        FurinaStageLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        var takeTheStage = new ProtoFsSalonDebut();
        var encore = new ProtoFsPlotTwist();
        Assert.False(FurinaStage.PlaysFree(seat.Creature, takeTheStage));
        stage.Seat(Escoffier);
        Assert.True(FurinaStage.PlaysFree(seat.Creature, takeTheStage));
        Assert.False(FurinaStage.PlaysFree(seat.Creature, encore));
        FurinaStage.NoteCardPlayed(seat.Creature, takeTheStage);
        Assert.False(FurinaStage.PlaysFree(seat.Creature, new ProtoFsLeadingLady()));
        stage.OpenTurn();
        Assert.True(FurinaStage.PlaysFree(seat.Creature, new ProtoFsLeadingLady()));
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void The_salon_summon_and_cue_cards_are_marked_off_their_rows()
    {
        var salon = new System.Type[]
        {
            typeof(ProtoFsSalonDebut), typeof(ProtoFsLeadingLady),
            typeof(ProtoFsSurintendanteChevalmarin),
            typeof(ProtoFsMademoiselleCrabaletta), typeof(ProtoFsGalaPremiere),
        };
        var cues = new System.Type[]
        {
            typeof(ProtoFsPlotTwist), typeof(ProtoFsInterposition),
            typeof(ProtoFsStageWhisper), typeof(ProtoFsBis),
            typeof(ProtoFsGuestOfHonor),
        };
        var all = typeof(ProtoFsSalonDebut).Assembly.GetTypes()
            .Where(t => t.Name.StartsWith("ProtoFs")).ToList();
        Assert.Equal(salon.OrderBy(t => t.Name),
            all.Where(t => typeof(IStageSalonSummonCard).IsAssignableFrom(t))
               .OrderBy(t => t.Name));
        Assert.Equal(cues.OrderBy(t => t.Name),
            all.Where(t => typeof(IStageCueCard).IsAssignableFrom(t))
               .OrderBy(t => t.Name));
        // Improvised Number's summon is conditional: not a Salon summon card.
        Assert.False(typeof(IStageSalonSummonCard)
            .IsAssignableFrom(typeof(ProtoFsImprovisedNumber)));
    }

    [Fact]
    public void Lyney_makes_the_first_cue_card_free_and_his_act_adds_a_trick()
    {
        FurinaStageLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Seat(Lyney);
        Assert.True(FurinaStage.PlaysFree(seat.Creature, new ProtoFsPlotTwist()));
        Assert.False(FurinaStage.PlaysFree(seat.Creature, new ProtoFsSalonDebut()));
        FurinaStage.NoteCardPlayed(seat.Creature, new ProtoFsStageWhisper());
        Assert.False(FurinaStage.PlaysFree(seat.Creature, new ProtoFsPlotTwist()));
        FurinaStageLedger.ResetAll();

        var kit = StageKit.With(1, Lyney);
        StageKit.Run(kit.Director.Cue(0));
        Assert.Equal(1, kit.Board.Tricks);
        Assert.Equal(FurinaStageLaw.ActLyneyPrice, kit.Stage.PaidThisTurn);
    }

    [Fact]
    public void The_trick_is_a_zero_cost_pyro_four_that_retains_and_exhausts()
    {
        var trick = new global::KleeMod.Cards.Prototype.StageTrick();
        Assert.Equal(0, trick.EnergyCost.GetWithModifiers(
            MegaCrit.Sts2.Core.Entities.Cards.CostModifiers.None));
        Assert.Equal(Element.Pyro, trick.Element);
        Assert.Equal(FurinaStageLaw.TrickDamage,
                     (int)trick.DynamicVars.Damage.BaseValue);
        Assert.Contains(MegaCrit.Sts2.Core.Entities.Cards.CardKeyword.Retain,
                        trick.CanonicalKeywords);
        Assert.Contains(MegaCrit.Sts2.Core.Entities.Cards.CardKeyword.Exhaust,
                        trick.CanonicalKeywords);
    }

    [Fact]
    public void Escoffiers_act_pays_two_and_the_salon_acts()
    {
        // test_escoffiers_act_pays_two_and_the_salon_acts
        var kit = StageKit.With(2, Usher, Escoffier, Crabaletta);
        StageKit.Run(kit.Director.Cue(1));
        Assert.Equal(2, kit.Stage.PaidThisTurn);
        Assert.Equal(new[] { "block Usher 4", "damage Crabaletta Random 5 None" },
                     kit.Board.Log);
    }

    [Fact]
    public void Neuvillettes_line_adds_two_to_his_hydro_act_on_stage()
    {
        // test_new_neuvillette_line_adds_two_to_hydro_cards_and_hydro_acts
        var kit = StageKit.With(2, Neuvillette);
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal(new[] { "damage Neuvillette All 9 Hydro" }, kit.Board.Hits);
    }

    [Fact]
    public void Neuvillettes_line_adds_two_to_her_hydro_cards_only()
    {
        // test_new_neuvillette_line_adds_two_to_hydro_cards_and_hydro_acts /
        // test_new_neuvillette_line_leaves_non_hydro_damage_alone
        FurinaStageLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();
        var crab = new ProtoFsMademoiselleCrabaletta();   // a Hydro Skill
        var encore = new ProtoFsPlotTwist();              // a plain Attack
        Assert.Equal(0, FurinaStage.HydroBonus(seat.Creature, crab));
        FurinaStageLedger.For(seat.Creature).Seat(Neuvillette);
        Assert.Equal(FurinaStageLaw.NeuvilletteHydroBonus,
                     FurinaStage.HydroBonus(seat.Creature, crab));
        Assert.Equal(0, FurinaStage.HydroBonus(seat.Creature, encore));
        Assert.Equal(0, FurinaStage.HydroBonus(seat.Creature, null));
        FurinaStageLedger.ResetAll();
        // The trio's acts carry no element, so the line never reaches them.
        var kit = StageKit.Of(Neuvillette, Chevalmarin, Crabaletta);
        StageKit.Run(kit.Director.Cue(1));
        StageKit.Run(kit.Director.Cue(2));
        Assert.Equal(new[] { "damage Chevalmarin All 2 None",
                             "damage Crabaletta Random 5 None" }, kit.Board.Hits);
    }

    [Fact]
    public void A_repeat_bow_of_neuvillette_takes_his_line_and_an_eviction_does_not()
    {
        var repeat = StageKit.Of(Neuvillette);
        StageKit.Run(repeat.Director.SummonGuest(Neuvillette, 0));
        Assert.Equal(new[] { "damage Neuvillette All 9 Hydro" }, repeat.Board.Hits);
    }

    [Fact]
    public void Clorindes_act_is_six_and_her_line_a_flat_four()
    {
        // test_clorinde_act_is_six_and_the_old_eight_is_a_variant
        Assert.Equal(6, FurinaStageLaw.ActClorindeDamage);
        Assert.Equal(4, FurinaStageLaw.ClorindeSpendDamage);
        Assert.Equal(1, FurinaStageLaw.ActClorindePrice);
    }

    [Fact]
    public void Navia_deals_twice_the_fanfare_spent_this_turn_and_nothing_at_zero()
    {
        var none = StageKit.Of(Navia);
        StageKit.Run(none.Director.EndOfTurn());
        Assert.Empty(none.Board.Hits);
        Assert.Equal(1, none.Beats(FurinaStageLedger.ActEvent, Navia));

        var kit = StageKit.With(Mods(rehearsal: 1), 3, Navia);
        StageKit.Run(kit.Director.Spend(3));
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal(new[] { "damage Navia Random 7 Geo" }, kit.Board.Hits);
        Assert.Equal(0, kit.Stage.PaidThisTurn);           // she is free
    }

    [Fact]
    public void Charlotte_draws_one_more_at_the_start_of_the_turn()
    {
        // test_charlotte_draws_one_more_at_the_start_of_the_turn (the draw is
        // a game command; the turn start asks for it while she is on stage).
        var calls = Il.Calls(Il.Method("FurinaStage", "TurnStart"));
        Assert.Contains("CardPileCmd.Draw", calls);
        Assert.Equal(1, FurinaStageLaw.CharlotteExtra);
        var kit = StageKit.Of(Charlotte);
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal(FurinaStageLaw.ActCharlotteGain, kit.Stage.Fanfare);
    }

    [Fact]
    public void Sigewinne_blocks_three_plus_two_per_hp_loss_since_her_last_act()
    {
        // test_sigewinne_blocks_three_plus_two_per_hp_loss
        var kit = StageKit.Of(Sigewinne);
        kit.Stage.NoteHpLoss();
        kit.Stage.NoteHpLoss();
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal(new[] { "block Sigewinne 7" }, kit.Board.Log);
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal("block Sigewinne 3", kit.Board.Log.Last());
        // Losses before she sat do not count.
        var late = StageKit.Of();
        late.Stage.NoteHpLoss();
        late.Stage.Seat(Sigewinne);
        StageKit.Run(late.Director.EndOfTurn());
        Assert.Equal(new[] { "block Sigewinne 3" }, late.Board.Log);
    }

    [Fact]
    public void Wriothesley_hits_four_plus_what_her_block_stopped_since_his_last_act()
    {
        var kit = StageKit.With(Mods(rehearsal: 1), 0, Wriothesley);
        kit.Stage.NoteBlocked(5);
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal(new[] { "damage Wriothesley Random 10 Cryo" }, kit.Board.Hits);
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal("damage Wriothesley Random 5 Cryo", kit.Board.Hits.Last());
    }

    [Fact]
    public void Lynette_moves_the_first_cued_performer_each_turn_to_the_front()
    {
        var kit = StageKit.Of(Usher, Lynette, Crabaletta);
        StageKit.Run(kit.Director.Cue(2));
        Assert.Equal(new[] { Crabaletta, Usher, Lynette }, kit.Company);
        Assert.Equal(new[] { "damage Crabaletta Random 5 None" }, kit.Board.Log);
        StageKit.Run(kit.Director.Cue(2));                  // the second Cue
        Assert.Equal(new[] { Crabaletta, Usher, Lynette }, kit.Company);
        kit.Stage.OpenTurn();
        StageKit.Run(kit.Director.Cue(1));
        Assert.Equal(new[] { Usher, Crabaletta, Lynette }, kit.Company);
        // Her act: Anemo, preferring an enemy with an aura.
        StageKit.Run(kit.Director.Cue(2));
        Assert.Contains("damage Lynette Aura 3 Anemo", kit.Board.Log);
    }

    [Fact]
    public void Chevreuse_acts_once_a_turn_every_act_counted()
    {
        var kit = StageKit.With(4, Chevreuse);
        StageKit.Run(kit.Director.Cue(0));
        Assert.Equal(1, kit.Board.Energy);
        Assert.Equal(2, kit.Stage.PaidThisTurn);
        StageKit.Run(kit.Director.EndOfTurn());              // her second act
        Assert.Equal(1, kit.Board.Energy);
        Assert.Equal(2, kit.Stage.Fanfare);
        // Her free Bow is an act too: a new turn's Bow gives Energy unpaid.
        kit.Stage.OpenTurn();
        StageKit.Run(kit.Director.SummonGuest(Chevreuse, 0));
        Assert.Equal(2, kit.Board.Energy);
        Assert.Equal(0, kit.Stage.PaidThisTurn);
    }

    [Fact]
    public void A_chevreuse_that_cannot_pay_keeps_her_act_for_later()
    {
        var kit = StageKit.With(1, Chevreuse);
        StageKit.Run(kit.Director.Cue(0));
        Assert.Equal(0, kit.Board.Energy);
        StageKit.Run(kit.Director.Gain(1));
        StageKit.Run(kit.Director.Cue(0));
        Assert.Equal(1, kit.Board.Energy);
    }

    [Fact]
    public void Guest_cards_give_their_fanfare_after_the_summon()
    {
        // test_guest_cards_give_the_papers_fanfare
        var kit = StageKit.Of();
        StageKit.Run(kit.Director.SummonGuest(Neuvillette, 4));
        Assert.Equal(4, kit.Stage.Fanfare);
        var support = StageKit.Of();
        StageKit.Run(support.Director.SummonGuest(Charlotte, 0));
        Assert.Equal(0, support.Stage.Fanfare);
    }

    // ---- the powers' and relics' rules ------------------------------------------

    [Fact]
    public void Thunderous_applause_draws_on_every_bow_and_walk_on()
    {
        // test_thunderous_applause_draws_on_every_bow_and_walk_on
        var kit = StageKit.With(Mods(bowDraw: 1), 0, Neuvillette, Clorinde, Charlotte);
        StageKit.Run(kit.Director.SummonSalon(Usher));       // a walk-on
        Assert.Equal(1, kit.Board.Drawn);
        StageKit.Run(kit.Director.SummonGuest(Navia, 0));    // an eviction
        Assert.Equal(2, kit.Board.Drawn);
    }

    [Fact]
    public void Critics_darling_deals_every_change_to_her_fanfare()
    {
        var kit = StageKit.With(Mods(critics: 1), 0, Neuvillette);
        StageKit.Run(kit.Director.Gain(3));
        StageKit.Run(kit.Director.EndOfTurn());              // he pays 2
        StageKit.Run(kit.Director.Spend(1));
        Assert.Equal(new[] { "critics 3", "critics 2", "critics 1" },
                     kit.Board.Log.Where(l => l.StartsWith("critics")));
    }

    [Fact]
    public void A_five_century_act_returns_the_first_performer_that_bows_and_leaves()
    {
        var kit = StageKit.With(Mods(fiveCentury: true), 0, Usher, Crabaletta);
        StageKit.Run(kit.Director.FinalBow(0));
        Assert.Equal(new[] { Crabaletta, Usher }, kit.Company);
        StageKit.Run(kit.Director.FinalBow(0));               // once a turn
        Assert.Equal(new[] { Usher }, kit.Company);
        // An evicted performer does not come back: the summon takes its seat.
        var full = StageKit.With(Mods(fiveCentury: true), 0, Usher, Crabaletta,
                                 Chevalmarin);
        StageKit.Run(full.Director.SummonSalon(Crabaletta));
        Assert.Equal(new[] { Crabaletta, Chevalmarin, Crabaletta }, full.Company);
    }

    [Fact]
    public void Final_bow_on_an_empty_stage_does_nothing()
    {
        var kit = StageKit.Of();
        StageKit.Run(kit.Director.FinalBow(null));
        StageKit.Run(kit.Director.FinalBow(0));
        Assert.Empty(kit.Board.Log);
        Assert.Equal(0, kit.Stage.Fanfare);
    }

    [Fact]
    public void The_bouquet_makes_a_bow_act_twice_and_the_gloves_block_after_it()
    {
        var kit = StageKit.With(Mods(bowActs: 2, bowBlock: 3), 0, Usher);
        StageKit.Run(kit.Director.FinalBow(0));
        Assert.Equal(new[] { "block Usher 4", "block Usher 4", "gloves 3" },
                     kit.Board.Log);
        Assert.Equal(1, kit.Stage.Fanfare);
    }

    [Fact]
    public void Full_house_repeats_each_act_on_a_full_stage_only()
    {
        var full = StageKit.With(Mods(fullHouse: 1), 0, Usher, Usher, Usher);
        StageKit.Run(full.Director.EndOfTurn());
        Assert.Equal(6, full.Board.Log.Count);
        var two = StageKit.With(Mods(fullHouse: 1), 0, Usher, Usher);
        StageKit.Run(two.Director.EndOfTurn());
        Assert.Equal(2, two.Board.Log.Count);
    }

    [Fact]
    public void Star_billing_draws_and_star_turn_acts_after_a_guest_joins()
    {
        var kit = StageKit.With(Mods(starBilling: 2, starTurn: 1), 0);
        StageKit.Run(kit.Director.SummonGuest(Clorinde, 2));
        Assert.Equal(2, kit.Board.Drawn);
        Assert.Equal(1, kit.Stage.PaidThisTurn);             // she paid to act
        Assert.Equal(new[] { "damage Clorinde Random 6 Electro" }, kit.Board.Hits);
    }

    [Fact]
    public void Guest_book_gives_three_on_the_first_guest_star_of_the_combat_only()
    {
        var kit = StageKit.Of();
        StageKit.Run(kit.Director.SummonGuest(Charlotte, 0, guestBook: 3));
        Assert.Equal(3, kit.Stage.Fanfare);
        StageKit.Run(kit.Director.SummonGuest(Lynette, 0, guestBook: 3));
        Assert.Equal(3, kit.Stage.Fanfare);
    }

    [Fact]
    public void Grand_finale_bows_every_performer_and_nobody_leaves()
    {
        var kit = StageKit.Of(Usher, Crabaletta);
        StageKit.Run(kit.Director.BowAll());
        Assert.Equal(new[] { Usher, Crabaletta }, kit.Company);
        Assert.Equal(2, kit.Stage.Fanfare);
        Assert.Equal(2, kit.Stage.BowsThisCombat);
    }

    [Fact]
    public void Endless_waltz_acts_the_guests_only_and_a_star_pays()
    {
        var kit = StageKit.With(1, Usher, Clorinde, Charlotte);
        StageKit.Run(kit.Director.PerformAll(guestsOnly: true));
        Assert.DoesNotContain(kit.Board.Log, l => l.StartsWith("block"));
        Assert.Equal(1, kit.Stage.PaidThisTurn);
        Assert.Equal(1, kit.Stage.Fanfare);                  // 1 - 1 + Charlotte's 1
    }

    [Fact]
    public void Ousia_multiplies_the_act_damage_rehearsal_included()
    {
        var kit = StageKit.With(Mods(rehearsal: 1), 0, Crabaletta, Usher);
        kit.Stage.ActDamageMultiplier = 2;
        StageKit.Run(kit.Director.EndOfTurn());
        Assert.Equal(new[] { "damage Crabaletta Random 12 None", "block Usher 5" },
                     kit.Board.Log);
        kit.Stage.CloseTurn();
        Assert.Equal(1, kit.Stage.ActDamageMultiplier);
    }

    [Fact]
    public void Arkhe_alignments_pneuma_gains_fanfare_and_its_ousia_doubles()
    {
        Assert.Equal(2, ArkheAlignmentPower.PneumaFanfare);
        Assert.Contains("FurinaStage.Gain",
            Il.Calls(Il.Method("ArkheAlignmentPower", "Choose")));
    }

    // ---- the forecast and the Spend warning ----------------------------------------

    [Fact]
    public void The_forecast_reads_the_sweep_front_to_back()
    {
        var funded = StageKit.With(1, Charlotte, Neuvillette);
        var forecast = FurinaStage.Forecast(funded.Stage);
        Assert.Equal(StageCueKind.Fanfare, forecast.Cues[0].Kind);
        Assert.False(forecast.Cues[1].Skips);
        Assert.Equal(9, forecast.Cues[1].Amount);
        Assert.Equal(0, forecast.FanfareAfter);

        var starved = StageKit.With(1, Neuvillette, Charlotte);
        var short_ = FurinaStage.Forecast(starved.Stage);
        Assert.True(short_.Cues[0].Skips);
        Assert.Equal(2, short_.FanfareAfter);
        // Pure: nothing moved.
        Assert.Equal(1, starved.Stage.Fanfare);
        Assert.Empty(starved.Board.Log);
    }

    [Fact]
    public void The_forecast_counts_usher_and_full_house()
    {
        var kit = StageKit.With(Mods(fullHouse: 1, rehearsal: 1), 0,
                                Usher, Usher, Crabaletta);
        var forecast = FurinaStage.Forecast(kit.Stage);
        Assert.Equal(4 * (FurinaStageLaw.ActUsherBlock + 1), forecast.Block);
        Assert.Equal(2, forecast.Cues[2].Times);
    }

    // ---- the faces, the badges and the wire ------------------------------------

    [Fact]
    public void Every_performer_tip_badge_and_picker_face_says_the_same_sentence()
    {
        foreach (var who in System.Enum.GetValues<StagePerformer>())
        {
            var text = StagePerformerBadge.ActText(who);
            Assert.False(string.IsNullOrEmpty(text));
            Assert.DoesNotContain(";", text);
        }
        Assert.Contains("Act: gain 4 [gold]Block[/gold].",
                        StagePerformerBadge.ActText(Usher));
    }

    [Fact]
    public void Every_performer_has_a_picker_face_and_the_trick_is_a_pool_member()
    {
        // One face per performer, each naming its own.
        var faces = typeof(global::KleeMod.Cards.Prototype.StageSeatOption)
            .Assembly.GetTypes()
            .Where(t => !t.IsAbstract && typeof(
                global::KleeMod.Cards.Prototype.StageSeatOption).IsAssignableFrom(t))
            .Select(t => ((global::KleeMod.Cards.Prototype.StageSeatOption)
                System.Activator.CreateInstance(t)!).Performer)
            .OrderBy(w => w).ToList();
        Assert.Equal(System.Enum.GetValues<StagePerformer>().OrderBy(w => w), faces);
        Assert.Contains(Il.Calls(Il.Method("FurinaStage", "OptionFor")),
                        c => c.Contains("ModelDb.Card"));
        Assert.Contains(Il.Calls(Il.Method("FurinaOffPoolCards", "BuildAll")),
                        c => c.Contains("AllOptions"));
    }

    [Fact]
    public void The_fanfare_badge_reads_the_ledger()
    {
        FurinaStageLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState().WithPower<FanfarePower>(1);
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Gain(7);
        var badge = seat.Creature.Powers.OfType<FanfarePower>().Single();
        Assert.Equal(7, badge.DisplayAmount);
        var smart = ((BaseLib.Abstracts.ILocalizationProvider)badge).Localization!
            .Single(r => r.Item1 == "smartDescription").Item2;
        Assert.Contains("{Gained}", smart);
        Assert.Contains("{Spent}", smart);
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void The_wire_carries_her_fanfare_the_flow_counts_and_the_seats()
    {
        FurinaStageLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Seat(Usher);
        stage.Seat(Clorinde);
        stage.Gain(5);
        stage.Spend(2);
        var wire = FurinaStageLedger.Snapshot(seat.Player);
        Assert.Equal(true, wire["live"]);
        Assert.Equal(3, wire["fanfare"]);
        Assert.Equal(5, wire["gained_this_turn"]);
        Assert.Equal(2, wire["spent_this_turn"]);
        var seats = (System.Collections.Generic.List<object?>)wire["seats"]!;
        Assert.Equal(2, seats.Count);
        var second = (System.Collections.Generic.Dictionary<string, object?>)seats[1]!;
        Assert.Equal("clorinde", second["member"]);
        Assert.Equal(true, second["guest"]);
        Assert.Equal(1, second["price"]);
        FurinaStageLedger.ResetAll();
    }
}
