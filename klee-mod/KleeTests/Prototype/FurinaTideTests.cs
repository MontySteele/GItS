using System;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE SALON'S TAB (2026-10-05,
/// <c>review/active/furina-research-proposal-2026-10-05.md</c> sec.2, sec.16
/// and sec.17): every rule, pinned headlessly over the director and a board
/// that keeps her HP (<see cref="StageKit"/>). The sim twin is
/// <c>tier0/tests/test_furina_tide_arm.py</c>, rule for rule.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaTideTests
{
    private static int Run(System.Threading.Tasks.Task<int> task) =>
        StageKit.Run(task);

    private static bool Run(System.Threading.Tasks.Task<bool> task) =>
        StageKit.Run(task);

    // ---- rule 1: the line ---------------------------------------------------

    [Fact]
    public void The_line_is_half_her_entry_hp_rounded_up()
    {
        Assert.Equal(39, FurinaStageLaw.LineOf(78));
        Assert.Equal(39, FurinaStageLaw.LineOf(77));
        Assert.Equal(20, FurinaStageLaw.LineOf(40));
        Assert.Equal(0, FurinaStageLaw.LineOf(0));
    }

    [Fact]
    public void A_drain_cannot_take_her_below_the_line()
    {
        // Entered at 78, now at 42: Drain 3 reaches 39 exactly; Drain 4 would
        // cross it and does nothing.
        var kit = StageKit.At(42, 78);
        Assert.True(kit.Director.CanDrain(3));
        Assert.False(kit.Director.CanDrain(4));
        Assert.False(Run(kit.Director.Drain(4)));
        Assert.Equal(42, kit.Board.Hp);
        Assert.Equal(0, kit.Stage.Drained);
        Assert.Equal(0, kit.Stage.Fanfare);
        Assert.True(Run(kit.Director.Drain(3)));
        Assert.Equal(39, kit.Board.Hp);
        Assert.Equal(3, kit.Stage.Drained);
    }

    [Fact]
    public void The_line_reads_the_entry_hp_not_max_hp()
    {
        // K4: a fight started hurt still has her kit. Entered at 50 of 78:
        // the line is 25, so Drain 5 from 30 is legal.
        var kit = StageKit.At(30, 50);
        Assert.Equal(25, kit.Stage.Line);
        Assert.True(kit.Director.CanDrain(5));
        Assert.False(kit.Director.CanDrain(6));
    }

    // ---- rule 2: the drained ledger caps Repay -----------------------------

    [Fact]
    public void Repay_returns_at_most_what_was_drained()
    {
        var kit = StageKit.Of();
        Run(kit.Director.Drain(5));
        Assert.Equal(73, kit.Board.Hp);
        Assert.Equal(5, Run(kit.Director.Repay(9)));
        Assert.Equal(78, kit.Board.Hp);
        Assert.Equal(0, kit.Stage.Drained);
        // Nothing drained: nothing returns, and no Fanfare.
        var before = kit.Stage.Fanfare;
        Assert.Equal(0, Run(kit.Director.Repay(3)));
        Assert.Equal(before, kit.Stage.Fanfare);
    }

    [Fact]
    public void Repay_never_returns_hp_an_enemy_took()
    {
        var kit = StageKit.Of();
        Run(kit.Director.Drain(3));             // 75, 3 drained
        kit.Board.Hp -= 10;                      // a hit: 65
        kit.Director.OnHpLost(10);
        Assert.Equal(3, Run(kit.Director.Repay(10)));
        Assert.Equal(68, kit.Board.Hp);
        Assert.Equal(0, kit.Stage.Drained);
    }

    [Fact]
    public void The_ledger_never_returns_past_max_hp()
    {
        var kit = StageKit.Of();
        Run(kit.Director.Drain(6));             // 72, 6 drained
        kit.Board.Hp = 76;                       // healed 4 by something else
        Assert.Equal(2, Run(kit.Director.Repay(6)));
        Assert.Equal(78, kit.Board.Hp);
        Assert.Equal(0, kit.Stage.Drained);
    }

    [Fact]
    public void Singer_of_many_waters_repays_every_drained_hp()
    {
        var kit = StageKit.Of();
        Run(kit.Director.Drain(4));
        Run(kit.Director.Drain(5));
        Assert.Equal(9, Run(kit.Director.RepayAll()));
        Assert.Equal(78, kit.Board.Hp);
    }

    // ---- the curtain call ---------------------------------------------------

    [Fact]
    public void The_curtain_call_returns_every_drained_hp_and_prints_nothing()
    {
        var kit = StageKit.Of();
        Run(kit.Director.Drain(6));
        Run(kit.Director.Drain(3));
        var fanfare = kit.Stage.Fanfare;
        Assert.Equal(9, Run(kit.Director.CurtainCall()));
        Assert.Equal(78, kit.Board.Hp);
        Assert.Equal(0, kit.Stage.Drained);
        Assert.Equal(fanfare, kit.Stage.Fanfare);
        Assert.Empty(kit.Board.Hits);
        // Wired to the combat's end, on every Furina with a ledger.
        Assert.Contains("FurinaStage.CurtainCall",
                        Il.Calls(Il.Method("FurinaStageHooks", "AfterCombatEnd")));
    }

    // ---- rule 3: Fanfare from HP --------------------------------------------

    [Fact]
    public void A_hit_past_block_prints_one_fanfare_a_point()
    {
        var kit = StageKit.Of();
        Assert.Equal(7, kit.Director.OnHpLost(7));
        Assert.Equal(7, kit.Stage.Fanfare);
        // The game half reads the HP change, so Block is already out of it.
        Assert.Contains("FurinaStage.NoteHpLost",
                        Il.Calls(Il.Method("FurinaStageHooks", "AfterCurrentHpChanged")));
    }

    [Fact]
    public void A_drain_prints_its_fanfare_once()
    {
        var kit = StageKit.Of();
        Run(kit.Director.Drain(3));
        Assert.Equal(3, kit.Stage.Fanfare);
        // The HP-loss hook stands aside while a Drain resolves.
        kit.Stage.Draining = true;
        Assert.Equal(0, kit.Director.OnHpLost(3));
        kit.Stage.Draining = false;
        Assert.Equal(3, kit.Stage.Fanfare);
    }

    [Fact]
    public void A_repay_prints_one_fanfare_a_point()
    {
        var kit = StageKit.Of();
        Run(kit.Director.Drain(4));
        Run(kit.Director.Repay(4));
        Assert.Equal(8, kit.Stage.Fanfare);
    }

    // ---- Universal Revelry (the pool-40 paper, sec.2) ----------------------

    [Fact]
    public void Revelry_adds_to_drains_and_repays_never_to_hits_and_copies_add()
    {
        // "Whenever you Drain or Repay, gain that much additional Fanfare."
        var one = StageKit.With(new StageMods { Revelry = 1 }, 0);
        Assert.Equal(5, one.Director.OnHpLost(5));        // a hit: no bonus
        Run(one.Director.Drain(3));                       // 3 + 3
        Assert.Equal(11, one.Stage.Fanfare);
        Run(one.Director.Repay(2));                       // 2 + 2
        Assert.Equal(15, one.Stage.Fanfare);
        // Two copies: +2x, never multiplicative.
        var two = StageKit.With(new StageMods { Revelry = 2 }, 0);
        Assert.Equal(5, two.Director.OnHpLost(5));
        Run(two.Director.Drain(3));                       // 3 + 6
        Assert.Equal(14, two.Stage.Fanfare);
        Assert.Equal(
            "Whenever you [gold]Drain[/gold] or [gold]Repay[/gold], gain that "
            + "much additional [gold]Fanfare[/gold].",
            new UniversalRevelryPower().Localization!
                .Single(r => r.Item1 == "description").Item2);
    }

    // ---- the pool to 39 (review/active/furina-pool-40-2026-10-05.md) ------

    [Fact]
    public void Critics_darling_hits_for_each_drain_and_repay_but_not_a_hit()
    {
        var kit = StageKit.With(new StageMods { CriticsDarling = 1 }, 0);
        kit.Director.OnHpLost(6);
        Assert.Empty(kit.Board.Hits);
        Run(kit.Director.Drain(4));
        Assert.Contains("power Critics' Darling Random 4", kit.Board.Log);
        Run(kit.Director.Repay(3));
        Assert.Contains("power Critics' Darling Random 3", kit.Board.Log);
        var two = StageKit.With(new StageMods { CriticsDarling = 2 }, 0);
        Run(two.Director.Drain(4));
        Assert.Contains("power Critics' Darling Random 8", two.Board.Log);
    }

    [Fact]
    public void Ousia_surge_draws_on_the_first_drain_each_turn_only()
    {
        var kit = StageKit.With(new StageMods { OusiaSurge = 1 }, 0);
        Run(kit.Director.Drain(2));
        Run(kit.Director.Drain(2));
        Assert.Equal(1, kit.Board.Drawn);
        kit.Stage.OpenTurn();
        Run(kit.Director.Drain(2));
        Assert.Equal(2, kit.Board.Drawn);
    }

    [Fact]
    public void A_five_century_act_puts_the_line_at_one_hp()
    {
        var kit = StageKit.With(new StageMods { FiveCenturyAct = 1 }, 0);
        Assert.Equal(1, kit.Stage.Line);
        kit.Board.Hp = 11;
        Assert.True(kit.Director.CanDrain(10));
        Assert.False(kit.Director.CanDrain(11));
        Assert.Equal(1, FurinaStageLaw.LineOf(78, lyney: true, fiveCentury: true));
    }

    [Fact]
    public void Lyneys_line_lowers_the_line_by_ten_and_his_act_drains_two_for_eight_to_all()
    {
        var kit = StageKit.Of(StagePerformer.Lyney);
        Assert.Equal(29, kit.Stage.Line);                    // 39 - 10
        Assert.Equal(39, StageKit.Of().Stage.Line);
        Assert.Equal(1, FurinaStageLaw.LineOf(8, lyney: true, fiveCentury: false));
        Assert.True(StageKit.Run(kit.Director.Act(StagePerformer.Lyney,
                                                  kit.Stage.Seats[0])));
        Assert.Equal(76, kit.Board.Hp);
        Assert.Equal(2, kit.Stage.Drained);
        Assert.Contains("damage Lyney All 8 Pyro", kit.Board.Log);
        // Below the line, the act skips: no Drain and no damage.
        var low = StageKit.At(30, 78, StagePerformer.Lyney);
        StageKit.Run(low.Director.Act(StagePerformer.Lyney, low.Stage.Seats[0]));
        Assert.Equal(30, low.Board.Hp);
        Assert.Empty(low.Board.Hits);
    }

    [Fact]
    public void Sigewinne_blocks_each_repay_and_her_act_repays_two()
    {
        var kit = StageKit.Of(StagePerformer.Sigewinne);
        Run(kit.Director.Drain(6));
        Run(kit.Director.Repay(3));
        Assert.Contains("block 3", kit.Board.Log);
        kit.Board.Log.Clear();
        StageKit.Run(kit.Director.Act(StagePerformer.Sigewinne,
                                      kit.Stage.Seats[0]));
        Assert.Equal(new[] { "heal 2", "block 2" }, kit.Board.Log);
    }

    [Fact]
    public void Chevreuse_applies_vulnerable_on_every_spend_and_her_act_deals_four()
    {
        var kit = StageKit.With(9, StagePerformer.Chevreuse);
        Run(kit.Director.Spend(3));
        Run(kit.Director.SpendAll());
        Assert.Equal(2, kit.Board.Log.Count(l => l == "vulnerable Random 1"));
        StageKit.Run(kit.Director.Act(StagePerformer.Chevreuse,
                                      kit.Stage.Seats[0]));
        Assert.Contains("damage Chevreuse Random 4 None", kit.Board.Log);
    }

    [Fact]
    public void Bis_keeps_half_of_a_spend_all_rounded_down()
    {
        var kit = StageKit.With(new StageMods { Bis = 1 }, 9);
        Assert.Equal(9, Run(kit.Director.SpendAll()));
        Assert.Equal(9, kit.Stage.SpentThisPlay);
        Assert.Equal(4, kit.Stage.Fanfare);
        // A Spend N is not a spend-all.
        Assert.Equal(4, Run(kit.Director.Spend(4)));
        Assert.Equal(0, kit.Stage.Fanfare);
        var none = StageKit.With(9);
        Run(none.Director.SpendAll());
        Assert.Equal(0, none.Stage.Fanfare);
    }

    [Fact]
    public void Fountain_of_lucine_repays_at_each_of_the_next_three_turn_starts()
    {
        var kit = StageKit.Of();
        Run(kit.Director.Drain(30));
        kit.Stage.ScheduleRepay(3, FurinaStageLaw.FountainTurns);
        kit.Stage.ScheduleRepay(4, FurinaStageLaw.FountainTurns);
        Assert.Equal(7, kit.Stage.RepayDueNext);
        for (var turn = 0; turn < 3; turn++)
        {
            Assert.Equal(7, Run(kit.Director.TurnStartRepays()));
        }
        Assert.False(kit.Stage.OwesRepays);
        Assert.Equal(0, Run(kit.Director.TurnStartRepays()));
        Assert.Equal(78 - 30 + 21, kit.Board.Hp);
        // One Repay per play: two plays are two Repays a turn.
        Assert.Equal(6, kit.Board.Log.Count(l => l.StartsWith("heal ")));
        // Wired to her turn start.
        Assert.Contains("FurinaStage.FountainRepays",
            Il.Calls(Il.Method("FurinaStage", "TurnStart")));
    }

    [Fact]
    public void The_seven_guests_parse_and_print_their_line_and_act()
    {
        foreach (var name in FurinaStage.Guests)
        {
            var who = FurinaStage.Parse(name);
            Assert.Equal(name, FurinaStage.Name(who));
            Assert.Contains("Act:", StagePerformerBadge.ActText(who));
        }
        Assert.Equal(7, FurinaStage.Guests.Length);
    }

    // ---- Spend and the three Powers ----------------------------------------

    [Fact]
    public void A_spend_is_paid_in_full_and_thunderous_applause_answers_it()
    {
        var kit = StageKit.With(new StageMods { Thunderous = 3 }, 5);
        Assert.Equal(0, Run(kit.Director.Spend(6)));
        Assert.Equal(5, kit.Stage.Fanfare);
        Assert.Equal(4, Run(kit.Director.Spend(4)));
        Assert.Equal(1, Run(kit.Director.SpendAll()));
        Assert.Equal(0, kit.Stage.Fanfare);
        Assert.Equal(2, kit.Board.Log.Count(l => l.StartsWith("power Thunderous")));
        // Nothing held is no Spend.
        Assert.Equal(0, Run(kit.Director.SpendAll()));
        Assert.Equal(2, kit.Board.Log.Count(l => l.StartsWith("power Thunderous")));
    }

    [Fact]
    public void Salons_encore_hits_all_on_a_drain_and_endless_waltz_on_a_repay()
    {
        var kit = StageKit.With(new StageMods { SalonsEncore = 3, EndlessWaltz = 1 }, 0);
        Run(kit.Director.Drain(4));
        Assert.Contains("power Salon's Encore All 3", kit.Board.Log);
        Run(kit.Director.Repay(4));
        Assert.Contains("power Endless Waltz Random 4", kit.Board.Log);
    }

    // ---- the guests (rule 5) -------------------------------------------------

    [Fact]
    public void A_fourth_guest_makes_the_oldest_leave_acting_once_more()
    {
        var kit = StageKit.Of(StagePerformer.Wriothesley,
                              StagePerformer.Lynette, StagePerformer.Clorinde);
        StageKit.Run(kit.Director.SummonGuest(StagePerformer.Charlotte));
        Assert.Equal(new[] { StagePerformer.Lynette, StagePerformer.Clorinde,
                             StagePerformer.Charlotte }, kit.Company);
        Assert.Equal("damage Wriothesley Random 4 Cryo", kit.Board.Hits.Single());
    }

    [Fact]
    public void A_second_copy_makes_the_guest_act_and_stay()
    {
        var kit = StageKit.Of(StagePerformer.Clorinde);
        Assert.Equal(StageSummonResult.Repeat,
                     StageKit.Run(kit.Director.SummonGuest(StagePerformer.Clorinde)));
        Assert.Equal(new[] { StagePerformer.Clorinde }, kit.Company);
        Assert.Equal("damage Clorinde Random 6 Electro", kit.Board.Hits.Single());
        // No Fanfare for it: the Bow's Fanfare is gone.
        Assert.Equal(0, kit.Stage.Fanfare);
    }

    [Fact]
    public void The_guests_lines_read_drains_repays_and_hits()
    {
        var kit = StageKit.Of(StagePerformer.Wriothesley,
                              StagePerformer.Clorinde, StagePerformer.Charlotte);
        Run(kit.Director.Drain(5));
        Assert.Contains("damage Wriothesley Random 5 Cryo", kit.Board.Log);
        Run(kit.Director.Repay(2));
        Assert.Contains("damage Clorinde Random 4 Electro", kit.Board.Log);
        Assert.Equal(1, kit.Board.Drawn);
        Run(kit.Director.Repay(2));                 // Charlotte: once a turn
        Assert.Equal(1, kit.Board.Drawn);

        var lynette = StageKit.Of(StagePerformer.Lynette);
        Assert.Equal(6, lynette.Director.OnEnemyHit(6));
        Assert.Equal(0, lynette.Director.OnEnemyHit(6));   // once a turn
        lynette.Stage.OpenTurn();
        Assert.Equal(2, lynette.Director.OnEnemyHit(2));
    }

    [Fact]
    public void At_the_end_of_her_turn_the_guests_act_then_the_singer_repays()
    {
        var kit = StageKit.Of(StagePerformer.Lynette, StagePerformer.Charlotte);
        Run(kit.Director.Drain(6));
        kit.Board.Log.Clear();
        StageKit.Run(kit.Director.EndOfTurn(FurinaStageLaw.SingerRepay));
        // Lynette finds no aura-wearer here (the board decides), then
        // Charlotte Repays 2 and draws, then the Singer Repays 1 (the
        // 2026-10-09 playtest trim; was 2).
        Assert.Equal(new[] { "damage Lynette Aura 3 Anemo", "heal 2",
                             "draw 1", "heal 1" }, kit.Board.Log);
        Assert.Equal(3, kit.Stage.Drained);
    }

    [Fact]
    public void Salon_solitaire_is_one_and_its_upgrade_two()
    {
        // The 2026-10-09 playtest trim: 1 [2], was 2 [3].
        FurinaStageLedger.ResetAll();
        Assert.Equal(1, FurinaStage.SingerOf(
            Seat.Furina().WithRelic<SalonSolitaire>().Creature));
        Assert.Equal(2, FurinaStage.SingerOf(
            Seat.Furina().WithRelic<CurtainNeverFalls>().Creature));
        Assert.Equal(0, FurinaStage.SingerOf(Seat.Furina().Creature));
        Assert.Equal(0, FurinaStage.SingerOf(
            Seat.Klee().WithRelic<SalonSolitaire>().Creature));
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void The_summon_preview_names_who_will_move()
    {
        var full = StageKit.Of(StagePerformer.Wriothesley,
                               StagePerformer.Lynette, StagePerformer.Clorinde);
        Assert.Equal("\n(Wriothesley will act and leave)",
            FurinaStageBowPreview.Line(full.Stage, StagePerformer.Charlotte));
        Assert.Equal("\n(Lynette will act again)",
            FurinaStageBowPreview.Line(full.Stage, StagePerformer.Lynette));
        Assert.Equal("",
            FurinaStageBowPreview.Line(StageKit.Of().Stage,
                                       StagePerformer.Charlotte));
    }

    [Fact]
    public void A_spend_all_record_closes_with_its_play_and_its_turn()
    {
        // The Salon's Tab seat round (2026-10-05): a spend-all face read the
        // LAST play's spend at 0 Fanfare ("Deals 113") until the next play.
        var kit = StageKit.With(7);
        kit.Stage.BeginPlay();
        Assert.Equal(7, kit.Stage.SpendAll());
        Assert.Equal(7, kit.Stage.SpentThisPlay);
        kit.Stage.EndPlay();
        Assert.Equal(0, kit.Stage.SpentThisPlay);
        kit.Stage.Gain(4);
        Assert.Equal(4, kit.Stage.SpendAll());
        kit.Stage.OpenTurn();
        Assert.Equal(0, kit.Stage.SpentThisPlay);
        // And the hook that closes it at the end of every play is there.
        Assert.Contains("FurinaStage.EndPlay",
            Il.Calls(typeof(FurinaStageHooks).GetMethod("AfterCardPlayed")!));
    }

    [Fact]
    public void Drain_and_repay_cards_carry_their_in_combat_lines()
    {
        Assert.Equal("\n(Repays 0)", FurinaStageFacePreview.Line(0));
        foreach (var (card, token) in new (CardModel, string)[]
                 {
                     (new ProtoFsCurtainRise(), "StageDrainLine"),
                     (new ProtoFsSalonsTab(), "StageDrainLine"),
                     (new ProtoFsMademoiselleCrabaletta(), "StageDrainLine"),
                     (new ProtoFsSurgingWaters(), "StageRepay"),
                     (new ProtoFsSingerOfManyWaters(), "StageRepay"),
                 })
        {
            var face = ((BaseLib.Abstracts.CustomCardModel)card).Localization!
                .Single(r => r.Item1 == "description").Item2;
            Assert.EndsWith("{InCombat:{" + token + "}|}", face);
        }
        // Salon's Tab's Drain option says it draws too.
        Assert.StartsWith("[gold]Drain[/gold] 4: draw ",
            new ProtoFsSalonsTabModeB().Localization!
                .Single(r => r.Item1 == "description").Item2);
    }

    // ---- the fixed price and the mode gate ---------------------------------

    [Fact]
    public void A_fixed_drain_or_spend_card_is_unplayable_when_it_cannot_pay()
    {
        foreach (var (type, gate) in new[]
                 {
                     ("ProtoFsMademoiselleCrabaletta", "FurinaStage.CanDrain"),
                     ("ProtoFsSoloistsSolicitation", "FurinaStage.CanDrain"),
                     ("ProtoFsQuickCue", "FurinaStage.CanSpend"),
                 })
        {
            var t = typeof(ProtoFsCurtainRise).Assembly
                .GetType("KleeMod.Cards.Prototype.Generated." + type)!;
            Assert.Contains(gate, Il.Calls(Il.Method(type, "get_IsPlayable")));
            Assert.True(typeof(IUnplayableReasonCard).IsAssignableFrom(t));
        }
        // Off Furina, or with no owner, the gate answers no and never throws.
        FurinaStageLedger.ResetAll();
        Assert.False(FurinaStage.CanDrain(null, 2));
        Assert.False(FurinaStage.CanDrain(Seat.Klee().Creature, 2));
        Assert.False(FurinaStage.CanSpend(Seat.Klee().Creature, 4));
        Assert.True(FurinaStage.CanDrain(Seat.Furina(78).Creature, 5));
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void A_drain_mode_is_offered_only_above_the_line()
    {
        foreach (var type in new[] { "ProtoFsCurtainRise", "ProtoFsLeadingLady",
                                     "ProtoFsSurintendanteChevalmarin",
                                     "ProtoFsSalonsTab" })
        {
            Assert.Contains("FurinaStage.CanDrain",
                            Il.Calls(Il.Method(type, "OnPlay")));
            Assert.Contains("FurinaStage.Drain",
                            Il.Calls(Il.Method(type, "OnPlay")));
        }
    }

    [Fact]
    public void Her_verbs_do_nothing_on_anyone_else_and_never_throw()
    {
        FurinaStageLedger.ResetAll();
        var klee = Seat.Klee().WithCombatState().Creature;
        var context = new MegaCrit.Sts2.Core.GameActions.Multiplayer
            .ThrowingPlayerChoiceContext();
        Assert.False(StageKit.Run(FurinaStage.Drain(context, klee, 3)));
        Assert.Equal(0, StageKit.Run(FurinaStage.Repay(context, klee, 3)));
        Assert.Equal(0, StageKit.Run(FurinaStage.RepayAll(context, klee)));
        Assert.Equal(0, StageKit.Run(FurinaStage.SpendAll(context, klee)));
        StageKit.Run(FurinaStage.GuestStar(context, klee, "clorinde"));
        Assert.Equal(0, FurinaStage.DrainedOf(klee));
        Assert.Equal(80, (int)klee.CurrentHp);
        FurinaStageLedger.ResetAll();
    }

    // ---- the "Drained N" counter --------------------------------------------

    [Fact]
    public void The_drained_counter_reads_the_ledger_and_its_hover_names_the_line()
    {
        FurinaStageLedger.ResetAll();
        Assert.True(DrainedCounter.AppliesTo(Seat.Furina().Creature));
        Assert.False(DrainedCounter.AppliesTo(Seat.Klee().Creature));
        Assert.False(DrainedCounter.AppliesTo(null));

        var seat = Seat.Furina(78).WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        Assert.Equal(0, DrainedCounter.Read(seat.Creature));
        stage.NoteDrain(4);
        Assert.Equal(4, DrainedCounter.Read(seat.Creature));
        Assert.Equal(FurinaStage.DrainedOf(seat.Creature),
                     DrainedCounter.Read(seat.Creature));

        // 2026-10-05: the line says where it comes from.
        Assert.Equal("Drain line [blue]39[/blue] HP (half the HP you started "
                     + "this fight with): you can [gold]Drain[/gold] down to it.",
                     DrainedCounter.LineSentence(
                         39, "half the HP you started this fight with"));
        Assert.Equal("half the HP you started this fight with", stage.LineWhy);
        Assert.Equal("A Five-Century Act",
                     FurinaStageLaw.LineWhy(lyney: true, fiveCentury: true));
        Assert.Contains("10 lower with Lyney",
                        FurinaStageLaw.LineWhy(lyney: true, fiveCentury: false));
        var body = DrainedCounter.HoverBody(seat.Creature);
        Assert.StartsWith(DrainedCounter.LineSentence(39, stage.LineWhy), body);
        Assert.Contains("Drained: [blue]4[/blue] HP.", body);
        Assert.Equal(DrainedCounter.HoverBody(0, 0, ""),
                     DrainedCounter.HoverBody(null));

        // Headless-safe, and on the funnel the Fanfare gauge rides.
        DrainedCounter.Refresh(seat.Creature);
        DrainedCounter.Refresh(Seat.Klee().Creature);
        DrainedCounter.Refresh(null);
        Assert.Contains(Il.Calls(typeof(FurinaStage)
                            .GetMethod(nameof(FurinaStage.RefreshBadges))!),
                        c => c.EndsWith("DrainedCounter.Refresh",
                                        StringComparison.Ordinal));
        var activate = Il.Calls(typeof(DrainedCounter).Assembly
            .GetType("KleeMod.Vfx.NCombatUi_Activate_GaugeSetup")!
            .GetMethod("Postfix", HeadlessGame.All)!);
        Assert.Contains(activate,
            c => c.EndsWith("DrainedCounter.Setup", StringComparison.Ordinal));
        // One slot along from the Fanfare gauge; the Spark counter after it.
        Assert.Equal(1, DrainedCounter.Slot);
        Assert.Equal(2, SparkCounter.SlotFor(Seat.Furina().Creature));
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void The_drain_and_repay_tips_say_the_rule()
    {
        string Body(string name) => (string)typeof(ArmKeywordTips)
            .GetField(name, HeadlessGame.All)!.GetRawConstantValue()!;
        Assert.Equal(
            "Lose N HP, never below half your HP at combat start. Lyney and "
            + "A Five-Century Act lower that line. Drained HP returns after "
            + "combat.",
            Body("DrainBody"));
        Assert.Contains("drained HP", Body("RepayBody"));
        Assert.Contains("[gold]Repay[/gold]", Body("FanfareBody"));
    }
}
