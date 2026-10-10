using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Diagnostics;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE SPEND ROUND 2'S "CLAUDE SHIPS" CHANGES
/// (<c>review/records/furina-spend-round-2-2026-10-10.md</c>): High Stakes
/// reads the HP drained this combat, gross; Gentle Current Repays on play
/// with its Block floor; Charlotte's line reads a card's Repay only; a Drain
/// line of 0 explains itself; the Salon Solitaire comment; and the telemetry
/// the next round reads (past-line HP lost, High Stakes' damage, Thunderous
/// Applause by name, the block-card turns). Sim twin:
/// <c>tier0/tests/test_furina_spend_round_2.py</c>.
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class FurinaSpendRound2Tests : IDisposable
{
    private static readonly Type Telemetry = typeof(PlayTelemetryHooks).Assembly
        .GetTypes().First(t => t.Name == "PlayTelemetry");

    public FurinaSpendRound2Tests()
    {
        Environment.SetEnvironmentVariable("GITS_TELEMETRY_INTENT", "");
        Invoke("ResetForTest");
        FurinaStageLedger.ResetAll();
    }

    public void Dispose()
    {
        Invoke("ResetForTest");
        FurinaStageLedger.ResetAll();
    }

    private static object? Invoke(string name, params object?[] args) =>
        Telemetry.GetMethod(name, HeadlessGame.All)!.Invoke(null, args);

    private static string Generated(string type) => File.ReadAllText(
        Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode", "Cards",
                     "Prototype", "Generated", type + ".cs"));

    private static string Face(CardModel card) =>
        ((BaseLib.Abstracts.CustomCardModel)card).Localization!
            .Single(r => r.Item1 == "description").Item2;

    private static CardModel Upgraded(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, null);
        return card;
    }

    // ---- 1. High Stakes reads a running total ---------------------------------

    [Fact]
    public void High_stakes_says_drained_this_combat_and_keeps_the_live_hover()
    {
        Assert.Equal(
            "Your Attacks deal 1 additional damage for every "
            + "{PowerAmount:diff()} HP you have [gold]Drained[/gold] this "
            + "combat.",
            Face(new ProtoFsHighStakes()));
        var rows = new HighStakesPower().Localization!;
        Assert.Equal(
            "Your Attacks deal 1 additional damage for every "
            + "[blue]{Amount}[/blue] HP you have [gold]Drained[/gold] this "
            + "combat.",
            rows.Single(r => r.Item1 == "description").Item2);
        Assert.EndsWith(
            "this combat. Now: [blue]{Bonus}[/blue] additional damage.",
            rows.Single(r => r.Item1 == "smartDescription").Item2);
        Assert.DoesNotContain("Repaid", Face(new ProtoFsHighStakes()));
    }

    [Fact]
    public void The_ledger_counts_every_drain_gross_and_repay_never_lowers_it()
    {
        var kit = StageKit.AtMax(62, 80, 80);            // line 60
        StageKit.Run(kit.Director.Drain(8));              // 2 above, 6 past
        Assert.Equal(8, kit.Stage.DrainedThisCombat);
        StageKit.Run(kit.Director.Repay(5));
        Assert.Equal(3, kit.Stage.Drained);
        Assert.Equal(8, kit.Stage.DrainedThisCombat);
        StageKit.Run(kit.Director.Drain(3));
        Assert.Equal(11, kit.Stage.DrainedThisCombat);
        // The curtain call empties the loan, not the count.
        StageKit.Run(kit.Director.CurtainCallParts());
        Assert.Equal(11, kit.Stage.DrainedThisCombat);
        kit.Stage.Clear();
        Assert.Equal(0, kit.Stage.DrainedThisCombat);
    }

    [Fact]
    public void High_stakes_bonus_reads_the_gross_count_and_copies_add()
    {
        var furina = Seat.Furina(80).WithPower<HighStakesPower>(5);
        var enemy = Seat.Klee().Creature;
        var stakes = furina.Creature.Powers.OfType<HighStakesPower>().Single();
        var attack = new ProtoFsBravura();
        decimal Hit(HighStakesPower p) =>
            p.ModifyDamageAdditive(enemy, 6m, ValueProp.Move, furina.Creature,
                                   attack, null);
        var ledger = FurinaStageLedger.For(furina.Creature);
        ledger.NoteDrain(7, 80);
        ledger.NoteDrain(4, 50);
        ledger.NoteRepay(11);                             // all of it back
        Assert.Equal(0, ledger.Drained);
        Assert.Equal(2m, Hit(stakes));                    // 11 / 5
        Assert.Equal(2, stakes.DisplayAmount);
        furina.WithPower<HighStakesPower>(4);
        Assert.Equal(2m + 2m, furina.Creature.Powers.OfType<HighStakesPower>()
            .Sum(p => Hit(p)));                           // 11/5 + 11/4
        Assert.Contains("FurinaStage.DrainedThisCombatOf",
            Il.Calls(typeof(HighStakesPower).GetProperty("Bonus")!.GetMethod!));
    }

    [Theory]
    [InlineData(3, 10, 3)]
    [InlineData(3, 2, 2)]
    [InlineData(0, 9, 0)]
    [InlineData(4, 0, 0)]
    public void High_stakes_credit_is_the_bonus_capped_at_the_hit(
        int bonus, int dealt, int credit)
    {
        Assert.Equal(credit, FurinaStageLaw.HighStakesCredit(bonus, dealt));
    }

    [Fact]
    public void High_stakes_files_what_it_added_for_the_telemetry()
    {
        var calls = Il.Calls(Il.Method("HighStakesPower", "AfterDamageGiven"));
        Assert.Contains("FurinaStageLedger.NoteHighStakes", calls);
        Assert.Contains("FurinaStageLaw.HighStakesCredit", calls);
        var ledger = FurinaStageLedger.Detached();
        ledger.NoteHighStakes(3);
        ledger.NoteHighStakes(0);
        ledger.NoteHighStakes(2);
        Assert.Equal(5, ledger.HighStakesDealt);
    }

    // ---- 2. Gentle Current Repays now -----------------------------------------

    [Fact]
    public void Gentle_current_repays_on_play_with_its_block_floor()
    {
        var card = new ProtoFsGentleCurrent();
        Assert.Equal(
            "Gain {Block:diff()} [gold]Block[/gold]. [gold]Repay[/gold] "
            + "{RepayAmount:diff()}. Gain 1 [gold]Block[/gold] for any HP it "
            + "could not [gold]Repay[/gold].{InCombat:{StageRepay}|}",
            Face(card));
        Assert.Equal(5, card.DynamicVars.Block.IntValue);
        Assert.Equal(3, card.DynamicVars["RepayAmount"].IntValue);
        var up = Upgraded(new ProtoFsGentleCurrent());
        Assert.Equal(7, up.DynamicVars.Block.IntValue);
        Assert.Equal(4, up.DynamicVars["RepayAmount"].IntValue);
        var code = Generated("ProtoFsGentleCurrent");
        Assert.Contains("FurinaStage.Repay(choiceContext, Owner.Creature, "
                        + "DynamicVars[\"RepayAmount\"].IntValue, "
                        + "StageFloor.Block)", code);
        // The house preview: "(Repays N, +M Block)".
        Assert.Contains("FurinaStageFacePreview.Repay(this, "
                        + "DynamicVars[\"RepayAmount\"].IntValue, "
                        + "FurinaStageFacePreview.PayBlock)", code);
        Assert.Equal("\n(Repays 1, +2 Block)",
                     FurinaStageFacePreview.Line(1, 3, "Block"));
    }

    [Fact]
    public void The_next_turn_repay_power_is_gone()
    {
        Assert.DoesNotContain(typeof(HighStakesPower).Assembly.GetTypes(),
                              t => t.Name == "RepayNextTurnPower");
        Assert.DoesNotContain("RepayNextTurn",
            string.Join(" ", Il.Calls(Il.Method("FurinaStage", "TurnStart"))));
        Assert.Null(typeof(FurinaCards).GetMethod("RepayNextTurn",
                                                  HeadlessGame.All));
    }

    // ---- 3. Charlotte's line reads a card's Repay ------------------------------

    [Fact]
    public void Charlottes_line_draws_on_a_cards_repay()
    {
        var kit = StageKit.Of(StagePerformer.Charlotte);
        StageKit.Run(kit.Director.Drain(6));
        kit.Stage.BeginPlay("Soothing Waters");
        Assert.True(kit.Stage.CardRepaying);
        StageKit.Run(kit.Director.Repay(2));
        kit.Stage.EndPlay();
        Assert.Equal(1, kit.Board.Drawn);
        Assert.Contains("cue Charlotte", kit.Board.Log);
    }

    [Fact]
    public void Charlottes_line_ignores_her_act_and_salon_solitaire()
    {
        var kit = StageKit.Of(StagePerformer.Charlotte);
        StageKit.Run(kit.Director.Drain(6));
        // The end of her turn under Salon Solitaire's cause: her act Repays
        // 2, the Singer Repays 1, and nothing is drawn.
        using (kit.Stage.CausedBy(FurinaStage.SalonSolitaireTitle))
        {
            StageKit.Run(kit.Director.EndOfTurn(FurinaStageLaw.SingerRepay));
        }
        Assert.Equal(3, kit.Stage.Drained);
        Assert.Equal(0, kit.Board.Drawn);
        Assert.False(kit.Stage.CharlotteDrewThisTurn);
        // A bare Repay outside any play (a turn-start Power) draws nothing.
        StageKit.Run(kit.Director.Repay(1));
        Assert.Equal(0, kit.Board.Drawn);
    }

    [Fact]
    public void Inside_a_card_play_a_guest_act_or_a_power_repay_still_does_not_count()
    {
        var kit = StageKit.Of(StagePerformer.Charlotte);
        StageKit.Run(kit.Director.Drain(10));
        kit.Stage.BeginPlay("Encore!");
        // Encore! makes Charlotte act: her act's Repay is the act's.
        StageKit.Run(kit.Director.ActOldest());
        Assert.Equal(0, kit.Board.Drawn);
        Assert.Equal(0, kit.Stage.Acting);
        // Grand Entrance's Repay in a Guest Star play is the Power's.
        using (kit.Stage.CausedBy(StageDirector.GrandEntranceTitle))
        {
            Assert.False(kit.Stage.CardRepaying);
            StageKit.Run(kit.Director.RepayFloor(2, StageFloor.Block));
        }
        Assert.Equal(0, kit.Board.Drawn);
        // The card's own Repay does.
        StageKit.Run(kit.Director.Repay(1));
        Assert.Equal(1, kit.Board.Drawn);
        kit.Stage.EndPlay();
        Assert.False(kit.Stage.CardRepaying);
    }

    [Fact]
    public void Charlottes_line_text_says_one_of_your_cards()
    {
        Assert.StartsWith(
            "The first time one of your cards [gold]Repays[/gold] each turn, "
            + "draw 1 card. Act: [gold]Repay[/gold] 2.",
            StagePerformerBadge.ActText(StagePerformer.Charlotte));
        Assert.Contains("FurinaStageLedger.get_CardRepaying",
                        Il.Calls(Il.Method("StageDirector", "Repay")));
    }

    // ---- 4. A Drain line of 0 explains itself --------------------------------

    [Fact]
    public void A_line_of_zero_says_all_your_drain_returns()
    {
        var why = FurinaStageLaw.LineWhyBase;
        Assert.Equal(
            "Drain line [blue]0[/blue] HP (" + why + "): all your "
            + "[gold]Drain[/gold] returns after combat.",
            global::KleeMod.Vfx.DrainedCounter.LineSentence(0, why));
        Assert.Equal(
            "\nYour Drain line is 0: " + why + ". All your Drain returns "
            + "after combat.",
            FurinaStageFacePreview.LineNowWords(0, why));
        // Any other line reads as before.
        Assert.Contains("past it is lost unless",
            global::KleeMod.Vfx.DrainedCounter.LineSentence(30, why));
        Assert.Equal("\nYour Drain line is 30: " + why + ".",
                     FurinaStageFacePreview.LineNowWords(30, why));
        Assert.Equal("all your Drain returns after combat",
                     FurinaStageLaw.LineZeroReturns);
    }

    // ---- 5. Hygiene ------------------------------------------------------------

    [Fact]
    public void The_salon_solitaire_comment_says_one_and_two()
    {
        var source = File.ReadAllText(Path.Combine(Round17Tests.Repo(),
            "klee-mod", "KleeCode", "Powers", "Prototype", "FurinaStage.cs"));
        Assert.Contains("At the end of your turn, Repay\n///      1.\" "
                        + "(Upgraded: 2.", source.Replace("\r\n", "\n"));
        Assert.Equal(1, FurinaStageLaw.SingerRepay);
    }

    // ---- 6. Telemetry ----------------------------------------------------------

    [Fact]
    public void A_furina_fight_writes_past_lost_and_high_stakes_bonus()
    {
        var furina = Seat.Furina(80).WithCombatState();
        var combat = DispatchProxy.Create<ICombatState,
            FurinaSpendAllPreviewWeakTests.ListenerProxy>();
        furina.Creature.CombatState = combat;
        Invoke("OpenSeatForTest", furina.Player, 1, 0);
        var ledger = FurinaStageLedger.For(furina.Creature);  // line 60
        ledger.NoteDrain(8, 62);                               // 2 above, 6 past
        ledger.NoteHighStakes(5);
        Assert.Equal(6, ledger.PastLostAtClose);               // owed: a death
        Invoke("RecordTurnEnd", 1);
        var r = JsonDocument.Parse((string)Invoke("JsonForTest", furina.Player)!)
            .RootElement;
        Assert.Equal(6, r.GetProperty("past_lost").GetInt32());
        Assert.Equal(5, r.GetProperty("high_stakes_bonus").GetInt32());
        // After the curtain call the lost part is the call's own.
        var parts = ledger.CurtainCallOf(70, 80);
        Assert.Equal(6, parts.Lost);
        Assert.Equal(0, ledger.DrainedPast);
        Assert.Equal(6, ledger.PastLostAtClose);
        // Under A Five-Century Act nothing past the line is lost.
        var five = FurinaStageLedger.Detached();
        five.ModsOverride = new StageMods { FiveCenturyAct = 1 };
        five.Open(80, 80);
        five.NoteDrain(8, 62);
        five.CurtainCallOf(54, 80);
        Assert.Equal(0, five.PastLostAtClose);

        var klee = Seat.Klee();
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        var kr = JsonDocument.Parse((string)Invoke("JsonForTest", klee.Player)!)
            .RootElement;
        Assert.False(kr.TryGetProperty("past_lost", out _));
        Assert.False(kr.TryGetProperty("high_stakes_bonus", out _));
    }

    [Fact]
    public void Thunderous_applause_is_credited_by_name()
    {
        Assert.Contains("DamageCredit.Open",
            Il.Calls(Il.Method("GameStageBoard", "PowerHit")));
        var furina = Seat.Furina(80);
        Invoke("OpenSeatForTest", furina.Player, 1, 0);
        using (DamageCredit.Open(furina.Creature, DamageCredit.Power,
                                 StageDirector.ThunderousTitle))
        {
            var credit = ((Player? Owner, string Kind, string Source))
                Invoke("Credit", null, null)!;
            Assert.Same(furina.Player, credit.Owner);
            Assert.Equal(DamageCredit.Power, credit.Kind);
            Assert.Equal("(Thunderous Applause)", credit.Source);
        }
    }

    [Fact]
    public void Every_seat_writes_its_block_card_turns()
    {
        var klee = Seat.Klee(80);
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        Invoke("RecordBlockCardTurn", klee.Player, 1, true, 10);
        Invoke("RecordBlockCardTurn", klee.Player, 2, true, 6);
        Invoke("RecordBlockCardTurn", klee.Player, 3, false, 12); // no card
        Invoke("RecordBlockCardTurn", klee.Player, 4, true, 0);   // no attack
        Invoke("RecordBlock", klee.Creature, 5, null, 1);         // round 1
        var r = JsonDocument.Parse((string)Invoke("JsonForTest", klee.Player)!)
            .RootElement;
        Assert.Equal(2, r.GetProperty("block_card_turns").GetInt32());
        Assert.Equal(1, r.GetProperty("block_card_turns_no_block").GetInt32());
        Assert.Contains("PlayTelemetry.BlockCardTurn",
            Il.Calls(Il.Method("PlayTelemetryHooks", "AfterPlayerTurnStart")));
    }
}
