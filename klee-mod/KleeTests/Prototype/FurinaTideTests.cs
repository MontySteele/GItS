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
    public void The_line_is_entry_hp_minus_a_quarter_of_max_hp_rounded_down()
    {
        // The Drain line rule (ruled 2026-10-09): the HP she entered with,
        // minus 1/4 of her Max HP, the quarter rounded down.
        Assert.Equal(30, FurinaStageLaw.LineOf(50, 80));   // 20 HP of room
        Assert.Equal(60, FurinaStageLaw.LineOf(80, 80));
        Assert.Equal(21, 85 - FurinaStageLaw.LineOf(85, 85)); // 21.25 down
        Assert.Equal(21, 60 - FurinaStageLaw.LineOf(60, 85));
        Assert.Equal(59, FurinaStageLaw.LineOf(78, 78));   // 19.5 down
        Assert.Equal(0, FurinaStageLaw.LineOf(10, 80));    // never below 0
        Assert.Equal(0, FurinaStageLaw.LineOf(0, 0));
        Assert.Equal(4, FurinaStageLaw.LineMaxHpDivisor);
        // Lyney lowers it by 10: 50/80 -> 20.
        Assert.Equal(20, FurinaStageLaw.LineOf(50, 80, lyney: true));
        Assert.Equal(59, StageKit.Of().Stage.Line);
        Assert.Equal(30, StageKit.AtMax(50, 50, 80).Stage.Line);
        Assert.Equal(60, StageKit.AtMax(80, 80, 80).Stage.Line);
        Assert.Equal(20,
            StageKit.AtMax(50, 50, 80, StagePerformer.Lyney).Stage.Line);
    }

    [Fact]
    public void The_line_snapshots_max_hp_when_the_combat_opens()
    {
        // Max HP is read once, beside the entry HP: a later Open (or a Max
        // HP change mid-fight) does not move the line.
        var stage = FurinaStageLedger.Detached();
        Assert.True(stage.Open(50, 80));
        Assert.Equal((50, 80), (stage.EntryHp, stage.EntryMaxHp));
        Assert.False(stage.Open(50, 100));
        Assert.Equal(80, stage.EntryMaxHp);
        Assert.Equal(30, stage.Line);
        // The game's opening hands the ledger her Max HP.
        Assert.Contains(Il.Calls(typeof(FurinaStage)
                            .GetMethod(nameof(FurinaStage.OpenCombat))!),
                        c => c.EndsWith("get_MaxHp", StringComparison.Ordinal));
    }

    [Fact]
    public void A_drain_is_never_refused_for_the_line_only_at_zero_hp()
    {
        // Entered at 78, now at 42 (past the line of 59): every Drain short
        // of 0 HP goes ahead; Drain 42 would take her to 0 and does nothing.
        var kit = StageKit.At(42, 78);
        Assert.True(kit.Director.CanDrain(41));
        Assert.False(kit.Director.CanDrain(42));
        Assert.False(Run(kit.Director.Drain(42)));
        Assert.Equal(42, kit.Board.Hp);
        Assert.Equal(0, kit.Stage.Drained);
        Assert.Equal(0, kit.Stage.Fanfare);
        Assert.True(Run(kit.Director.Drain(4)));
        Assert.Equal(38, kit.Board.Hp);
        Assert.Equal(4, kit.Stage.DrainedPast);
        Assert.Equal(1, FurinaStageLaw.DrainFloor);
    }

    [Fact]
    public void The_line_reads_the_entry_hp_not_max_hp()
    {
        // K4: a fight started hurt still has her kit. Entered at 50 of 78:
        // the line is 31 (50 - 19).
        var kit = StageKit.At(30, 50);
        Assert.Equal(31, kit.Stage.Line);
        Assert.True(kit.Director.CanDrain(29));
    }

    [Fact]
    public void A_drain_splits_into_the_part_above_the_line_and_the_part_past_it()
    {
        var kit = StageKit.Of();                       // line 59
        Run(kit.Director.Drain(15));                   // 78 -> 63
        Assert.Equal((15, 0), (kit.Stage.DrainedAbove, kit.Stage.DrainedPast));
        Run(kit.Director.Drain(10));                   // 63 -> 53: 4 + 6
        Assert.Equal((19, 6), (kit.Stage.DrainedAbove, kit.Stage.DrainedPast));
        Run(kit.Director.Drain(3));                    // all past
        Assert.Equal((19, 9), (kit.Stage.DrainedAbove, kit.Stage.DrainedPast));
        Assert.Equal(28, kit.Stage.Drained);
        Assert.True(kit.Stage.PastLine(1, 59 + 0));
        Assert.False(kit.Stage.PastLine(1, 60));
    }

    [Fact]
    public void A_repay_returns_the_past_line_part_first()
    {
        var kit = StageKit.Of();
        Run(kit.Director.Drain(25));                   // 19 above, 6 past
        Assert.Equal(4, Run(kit.Director.Repay(4)));
        Assert.Equal((19, 2), (kit.Stage.DrainedAbove, kit.Stage.DrainedPast));
        Assert.Equal(5, Run(kit.Director.Repay(5)));
        Assert.Equal((16, 0), (kit.Stage.DrainedAbove, kit.Stage.DrainedPast));
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
    public void The_curtain_call_returns_only_the_part_above_the_line()
    {
        var kit = StageKit.Of();
        Run(kit.Director.Drain(25));                   // 53: 19 above, 6 past
        Assert.Equal(19, Run(kit.Director.CurtainCall()));
        Assert.Equal(72, kit.Board.Hp);                // 6 HP stay lost
        Assert.Equal(0, kit.Stage.Drained);
    }

    [Fact]
    public void A_five_century_act_returns_the_past_line_part_too()
    {
        var kit = StageKit.With(new StageMods { FiveCenturyAct = 1 }, 0);
        Assert.Equal(59, kit.Stage.Line);              // it no longer moves it
        Run(kit.Director.Drain(25));
        Assert.Equal(25, Run(kit.Director.CurtainCall()));
        Assert.Equal(78, kit.Board.Hp);
        Assert.Contains("past your line also returns",
            new FiveCenturyActPower().Localization!
                .Single(r => r.Item1 == "description").Item2);
        Assert.Contains("past your line also returns",
            new ProtoFsAFiveCenturyAct().Localization!
                .Single(r => r.Item1 == "description").Item2);
    }

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
    public void Lyneys_line_lowers_the_line_by_ten_and_his_act_drains_two_for_eight_to_all()
    {
        var kit = StageKit.Of(StagePerformer.Lyney);
        Assert.Equal(49, kit.Stage.Line);                    // 59 - 10
        Assert.Equal(59, StageKit.Of().Stage.Line);
        Assert.Equal(1, FurinaStageLaw.LineOf(8, 78, lyney: true));
        Assert.True(StageKit.Run(kit.Director.Act(kit.Stage.Seats[0])));
        Assert.Equal(76, kit.Board.Hp);
        Assert.Equal(2, kit.Stage.Drained);
        Assert.Contains("damage Lyney All 8 Pyro", kit.Board.Log);
        // Below the line (the drain-line round, 2026-10-09) a guest's
        // Drain stops at the line: it drains 0 and still deals its damage.
        var low = StageKit.At(30, 78, StagePerformer.Lyney);
        StageKit.Run(low.Director.Act(low.Stage.Seats[0]));
        Assert.Equal(30, low.Board.Hp);
        Assert.Equal(0, low.Stage.Drained);
        Assert.Contains("damage Lyney All 8 Pyro", low.Board.Log);
        // At 2 HP: no Drain, the damage unchanged.
        var last = StageKit.At(2, 78, StagePerformer.Lyney);
        StageKit.Run(last.Director.Act(last.Stage.Seats[0]));
        Assert.Equal(2, last.Board.Hp);
        Assert.Contains("damage Lyney All 8 Pyro", last.Board.Log);
    }

    [Fact]
    public void Sigewinne_blocks_each_repay_and_her_act_repays_two()
    {
        var kit = StageKit.Of(StagePerformer.Sigewinne);
        Run(kit.Director.Drain(6));
        Run(kit.Director.Repay(3));
        Assert.Contains("block 3", kit.Board.Log);
        kit.Board.Log.Clear();
        StageKit.Run(kit.Director.Act(kit.Stage.Seats[0]));
        // The pool to 75: her line gets a cue of its own before its Block.
        Assert.Equal(new[] { "heal 2", "cue Sigewinne", "block 2" },
                     kit.Board.Log);
    }

    [Fact]
    public void Chevreuse_applies_vulnerable_on_every_spend_and_her_act_deals_four()
    {
        var kit = StageKit.With(9, StagePerformer.Chevreuse);
        Run(kit.Director.Spend(3));
        Run(kit.Director.SpendAll());
        Assert.Equal(2, kit.Board.Log.Count(l => l == "vulnerable Random 1"));
        StageKit.Run(kit.Director.Act(kit.Stage.Seats[0]));
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
    public void The_eleven_guests_parse_and_print_their_line_and_act()
    {
        foreach (var name in FurinaStage.Guests)
        {
            var who = FurinaStage.Parse(name);
            Assert.Equal(name, FurinaStage.Name(who));
            Assert.Contains("Act:", StagePerformerBadge.ActText(who));
        }
        Assert.Equal(11, FurinaStage.Guests.Length);
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
    public void Salons_encore_hits_all_on_a_drain()
    {
        var kit = StageKit.With(new StageMods { SalonsEncore = 3 }, 0);
        Run(kit.Director.Drain(4));
        Assert.Contains("power Salon's Encore All 3", kit.Board.Log);
        // Endless Waltz was cut from the pool (2026-10-09): no Repay hits.
        Run(kit.Director.Repay(4));
        Assert.Single(kit.Board.Hits);
    }

    // ---- the guests (rule 5) -------------------------------------------------

    [Fact]
    public void A_fourth_guest_makes_the_oldest_leave_with_no_act()
    {
        // The pool to 75 (sec.3): no effect on summon, so the evicted guest
        // leaves without acting, and its cards go back (the pins in
        // `FurinaGuestRuleTests` hold the cards' way back).
        var kit = StageKit.Of(StagePerformer.Wriothesley,
                              StagePerformer.Lynette, StagePerformer.Clorinde);
        Assert.Equal(StageSummonResult.Evict,
            StageKit.Run(kit.Director.SummonGuest(StagePerformer.Charlotte)));
        Assert.Equal(new[] { StagePerformer.Lynette, StagePerformer.Clorinde,
                             StagePerformer.Charlotte }, kit.Company);
        Assert.Empty(kit.Board.Hits);
        Assert.Contains("return Wriothesley 0", kit.Board.Log);
    }

    [Fact]
    public void A_second_copy_moves_the_guest_to_the_newest_seat_with_no_act()
    {
        var kit = StageKit.Of(StagePerformer.Clorinde, StagePerformer.Lynette);
        Assert.Equal(StageSummonResult.Repeat,
                     StageKit.Run(kit.Director.SummonGuest(StagePerformer.Clorinde)));
        Assert.Equal(new[] { StagePerformer.Lynette, StagePerformer.Clorinde },
                     kit.Company);
        Assert.Empty(kit.Board.Hits);
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
        // The pool to 75: Charlotte's line gets its own cue before its draw.
        Assert.Equal(new[] { "damage Lynette Aura 3 Anemo", "heal 2",
                             "cue Charlotte", "draw 1", "heal 1" },
                     kit.Board.Log);
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
        Assert.Equal("\n(Wriothesley will leave)",
            FurinaStageBowPreview.Line(full.Stage, StagePerformer.Charlotte));
        Assert.Equal("\n(Lynette moves to the newest seat)",
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
        stage.NoteDrain(4, 78);
        Assert.Equal(4, DrainedCounter.Read(seat.Creature));
        Assert.Equal(FurinaStage.DrainedOf(seat.Creature),
                     DrainedCounter.Read(seat.Creature));

        // 2026-10-05: the line says where it comes from; 2026-10-09: it
        // is entry HP minus 1/4 of Max HP, and HP drained past it is lost
        // unless Repaid.
        Assert.Equal("Drain line [blue]59[/blue] HP (the HP you started "
                     + "this fight with, minus 1/4 of your Max HP): HP you "
                     + "[gold]Drain[/gold] past it is lost unless you "
                     + "[gold]Repay[/gold] it.",
                     DrainedCounter.LineSentence(
                         59, "the HP you started this fight with, minus 1/4 "
                             + "of your Max HP"));
        Assert.Equal("the HP you started this fight with, minus 1/4 of your "
                     + "Max HP",
                     stage.LineWhy);
        Assert.Contains("10 lower with Lyney",
                        FurinaStageLaw.LineWhy(lyney: true));
        var body = DrainedCounter.HoverBody(seat.Creature);
        Assert.StartsWith(DrainedCounter.LineSentence(59, stage.LineWhy), body);
        Assert.Contains("Drained: [blue]4[/blue] HP.", body);
        Assert.Contains("Drained: [blue]9[/blue] HP, [blue]3[/blue] past "
                        + "your line.",
                        DrainedCounter.HoverBody(9, 59, "", past: 3));
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
            "Lose N HP. Drained HP above your line returns after combat. HP "
            + "drained past your line is lost unless you [gold]Repay[/gold] "
            + "it. Your line is the HP you started this fight with, minus 1/4 "
            + "of your Max HP.",
            Body("DrainBody"));
        Assert.Contains("drained HP", Body("RepayBody"));
        Assert.Contains("[gold]Repay[/gold]", Body("FanfareBody"));
        // The pool-75 round (2026-10-09): Fanfare lives one combat (her
        // ledger is per combat), and the tip says so.
        Assert.EndsWith("It resets to 0 after each combat.",
                        Body("FanfareBody"));
    }

    [Fact]
    public void Drain_and_repay_faces_say_the_line_and_the_return()
    {
        // The pool-75 round (2026-10-09). The Drain tip names the line now,
        // and the refusal carries its number.
        Assert.Equal(
            "\nYour Drain line is 30: the HP you started this fight with, "
            + "minus 1/4 of your Max HP.",
            FurinaStageFacePreview.LineNowWords(
                30, FurinaStageLaw.LineWhy(lyney: false)));
        // The Drain line rule (2026-10-09): past the line is a warning, and
        // the one refusal left is a Drain to 0 HP.
        Assert.Equal("\n(Past your Drain line of 59 HP)",
                     FurinaStageFacePreview.PastLine(59));
        Assert.Equal("\n(Not enough HP)", FurinaStageFacePreview.NotEnoughHp);
        // Off a combat the tip adds nothing.
        Assert.Equal("", FurinaStageFacePreview.LineNow(new ProtoFsOusiaPledge()));

        // Every card that Repays prints "(Repays N)", the later and the
        // conditional Repays included.
        foreach (var card in new CardModel[]
                 {
                     new ProtoFsGentleCurrent(), new ProtoFsPneumaTides(),
                     new ProtoFsFountainOfLucine(), new ProtoFsGrandEntrance(),
                     new ProtoFsRiptideLunge(), new ProtoFsSoothingWaters(),
                     new ProtoFsHymnOfManyWaters(),
                 })
        {
            var face = ((BaseLib.Abstracts.CustomCardModel)card).Localization!
                .Single(r => r.Item1 == "description").Item2;
            Assert.EndsWith("{InCombat:{StageRepay}|}", face);
        }
        Assert.EndsWith("Copies stack.",
            new ProtoFsSalonsEncore().Localization!
                .Single(r => r.Item1 == "description").Item2);

        // Riptide Lunge's Repay reads the board after its own Drain 3: at
        // full HP with nothing drained, it would return 3, not 0.
        var seat = Seat.Furina(78).WithCombatState();
        FurinaStageLedger.For(seat.Creature);
        Assert.Equal(0, FurinaStageFacePreview.Room(seat.Creature, 6));
        Assert.Equal(3, FurinaStageFacePreview.Room(seat.Creature, 6, 3));
        FurinaStageLedger.ResetAll();
    }
}
