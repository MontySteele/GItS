using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text.Json;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Diagnostics;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE SPEND ROUND'S "CLAUDE SHIPS" CHANGES
/// (<c>review/records/furina-spend-round-2026-10-10.md</c>): High Stakes
/// reworked, A Five-Century Act made visible, the curtain call's lost HP, the
/// fixed-Drain refusal reason, Bubble Aria's chooser label, the calculated
/// Block preview under Frail and Dexterity, and the telemetry the next round
/// reads (her Fanfare per fight, HP after the end-of-combat effects). Sim
/// twin: <c>tier0/tests/test_furina_spend_round_fixes.py</c>.
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class FurinaSpendRoundFixesTests : IDisposable
{
    private static readonly Type Telemetry = typeof(PlayTelemetryHooks).Assembly
        .GetTypes().First(t => t.Name == "PlayTelemetry");

    public FurinaSpendRoundFixesTests()
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

    // ---- 1. High Stakes ------------------------------------------------------

    [Fact]
    public void High_stakes_prints_the_divisor_five_and_four_upgraded()
    {
        var card = new ProtoFsHighStakes();
        Assert.Equal(
            "Your Attacks deal 1 additional damage for every "
            + "{PowerAmount:diff()} HP you have [gold]Drained[/gold] this "
            + "combat.",
            Face(card));
        Assert.Equal(FurinaStageLaw.HighStakesEvery,
                     card.DynamicVars["PowerAmount"].IntValue);
        Assert.Equal(FurinaStageLaw.HighStakesEveryUpgraded,
                     Upgraded(new ProtoFsHighStakes())
                         .DynamicVars["PowerAmount"].IntValue);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.Contains(": base(1, CardType.Power, CardRarity.Uncommon",
                        Generated("ProtoFsHighStakes"));
    }

    [Theory]
    [InlineData(0, 5, 0)]
    [InlineData(4, 5, 0)]
    [InlineData(5, 5, 1)]
    [InlineData(14, 5, 2)]
    [InlineData(14, 4, 3)]
    [InlineData(30, 5, 6)]
    public void High_stakes_bonus_is_the_drained_over_the_divisor_rounded_down(
        int drained, int every, int bonus)
    {
        Assert.Equal(bonus, FurinaStageLaw.HighStakesBonus(drained, every));
    }

    [Fact]
    public void High_stakes_adds_per_attack_hit_off_the_gross_drained_and_copies_add()
    {
        var furina = Seat.Furina(80).WithPower<HighStakesPower>(5);
        var enemy = Seat.Klee().Creature;
        var stakes = furina.Creature.Powers.OfType<HighStakesPower>().Single();
        Assert.Equal(PowerInstanceType.Instanced, stakes.InstanceType);
        var attack = new ProtoFsBravura();
        decimal Hit(HighStakesPower p, CardModel? source,
                    ValueProp props = ValueProp.Move) =>
            p.ModifyDamageAdditive(enemy, 6m, props, furina.Creature, source,
                                   null);

        Assert.Equal(0m, Hit(stakes, attack));       // nothing drained
        var ledger = FurinaStageLedger.For(furina.Creature);
        ledger.NoteDrain(8, 80);                      // above the line
        ledger.NoteDrain(6, 45);                      // past the line (60)
        Assert.Equal(14, ledger.Drained);
        Assert.Equal(2m, Hit(stakes, attack));        // 14 / 5
        Assert.Equal(2, stakes.Bonus);
        Assert.Equal(2, stakes.DisplayAmount);        // the badge: the bonus
        // The Spend round 2 (2026-10-10): Repay no longer lowers it.
        ledger.NoteRepay(5);
        Assert.Equal(9, ledger.Drained);
        Assert.Equal(2m, Hit(stakes, attack));        // still 14 / 5
        ledger.NoteDrain(1, 80);
        Assert.Equal(3m, Hit(stakes, attack));        // 15 / 5
        // Not a Skill's hit, not an unpowered hit, not someone else's.
        Assert.Equal(0m, Hit(stakes, new ProtoFsOverdraft()));
        Assert.Equal(0m, Hit(stakes, attack, ValueProp.Unpowered));
        Assert.Equal(0m, stakes.ModifyDamageAdditive(
            enemy, 6m, ValueProp.Move, enemy, attack, null));
        // A second copy (upgraded, every 4) is its own instance and adds.
        furina.WithPower<HighStakesPower>(4);
        var both = furina.Creature.Powers.OfType<HighStakesPower>().ToList();
        Assert.Equal(2, both.Count);
        Assert.Equal(3m + 3m, both.Sum(p => Hit(p, attack)));   // 15/5 + 15/4
    }

    [Fact]
    public void High_stakes_no_longer_reads_the_line_and_against_the_tide_still_does()
    {
        Assert.DoesNotContain("FurinaStage.NearLine",
            Il.Calls(Il.Method("HighStakesPower", "ModifyDamageAdditive")));
        Assert.Contains("FurinaStage.NearLine(Owner.Creature)",
                        Generated("ProtoFsAgainstTheTide"));
        Assert.Contains("HighStakesPower.Refresh",
            Il.Calls(Il.Method("FurinaStage", "RefreshBadges")));
    }

    // ---- 2. A Five-Century Act becomes visible ------------------------------

    [Fact]
    public void Under_a_five_century_act_the_counter_drops_lost_unless_you_repay()
    {
        Assert.Equal(
            "Drained [blue]12[/blue] HP ([blue]4[/blue] past your line: lost "
            + "unless you [gold]Repay[/gold])",
            global::KleeMod.Vfx.DrainedCounter.DrainedPhrase(12, 4));
        Assert.Equal("Drained [blue]12[/blue] HP ([blue]4[/blue] past your line)",
                     global::KleeMod.Vfx.DrainedCounter.DrainedPhrase(12, 4, true));
        var hover = global::KleeMod.Vfx.DrainedCounter.HoverBody(12, 30, "", 4, true);
        // The hover's own two lines drop it; the Drain tip under them still
        // states the rule as it stands without the power.
        Assert.StartsWith(
            "Drain line [blue]30[/blue] HP.\nDrained [blue]12[/blue] HP "
            + "([blue]4[/blue] past your line).\n", hover);
        Assert.Contains("past it is lost unless",
                        global::KleeMod.Vfx.DrainedCounter.HoverBody(12, 30, "", 4));
        Assert.Equal("\n(Past your Drain line: returns after combat)",
                     FurinaStageFacePreview.PastLineReturns);
    }

    [Fact]
    public void A_fixed_drain_face_past_the_line_says_it_returns_under_a_five_century_act()
    {
        InCombat(() =>
        {
            var b = Build(new ProtoFsOverdraft());            // Drain 4
            var ledger = FurinaStageLedger.For(b.Furina.Creature);
            Seat.Force(b.Furina.Creature, "CurrentHp", ledger.Line + 2);
            Assert.Equal(FurinaStageFacePreview.PastLine(ledger.Line),
                         FurinaStageFacePreview.DrainLine(b.Card, 4));
            ledger.ModsOverride = new StageMods { FiveCenturyAct = 1 };
            Assert.Equal("\n(Past your Drain line: returns after combat)",
                         FurinaStageFacePreview.DrainLine(b.Card, 4));
            // Above the line nothing is printed either way.
            Seat.Force(b.Furina.Creature, "CurrentHp", ledger.Line + 10);
            Assert.Equal("", FurinaStageFacePreview.DrainLine(b.Card, 4));
        });
    }

    // ---- 3. The curtain call names what did not come back -------------------

    [Fact]
    public void The_curtain_call_carries_the_lost_past_line_hp()
    {
        // Entered at 60 of 80: the line is 40. At 42, Drain 8: 2 above, 6
        // past.
        var kit = StageKit.AtMax(42, 60, 80);
        Assert.True(StageKit.Run(kit.Director.Drain(8)));
        Assert.Equal(2, kit.Stage.DrainedAbove);
        Assert.Equal(6, kit.Stage.DrainedPast);
        var parts = StageKit.Run(kit.Director.CurtainCallParts());
        Assert.Equal(new CurtainCallParts(2, 0, 6), parts);
        Assert.Equal(36, kit.Board.Hp);
        Assert.Equal(0, kit.Stage.Drained);
    }

    [Fact]
    public void Under_a_five_century_act_the_curtain_call_names_the_past_part_returned()
    {
        var kit = new StageKit(new StageMods { FiveCenturyAct = 1 }, 0, 42, 60,
                               80);
        StageKit.Run(kit.Director.Drain(8));
        var parts = StageKit.Run(kit.Director.CurtainCallParts());
        Assert.Equal(new CurtainCallParts(8, 6, 0), parts);
        Assert.Equal(42, kit.Board.Hp);
    }

    [Fact]
    public void The_curtain_event_carries_lost_and_past_onto_the_wire()
    {
        ResolutionLedger.ResetFight();
        ResolutionLedger.NoteEvent(ResolutionLedger.HpReturned, "", "Furina",
                                   "", "", onPlayer: true, amount: 2,
                                   lost: 6, past: 0);
        var events = (List<Dictionary<string, object?>>)
            ResolutionLedger.Snapshot()[0]["events"]!;
        Assert.Equal(2, events[0]["amount"]);
        Assert.Equal(6, events[0]["lost"]);
        Assert.Equal(0, events[0]["past"]);
        ResolutionLedger.ResetFight();
        Assert.Contains("StageDirector.CurtainCallParts",
            Il.Calls(Il.Method("FurinaStage", "CurtainCall")));
    }

    // ---- 4. The refusal says 0 HP --------------------------------------------

    [Fact]
    public void Every_fixed_drain_refusal_says_it_would_take_you_to_zero_hp()
    {
        var dir = Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode",
                               "Cards", "Prototype", "Generated");
        var files = Directory.GetFiles(dir, "ProtoFs*.cs");
        Assert.DoesNotContain(files, f => File.ReadAllText(f)
            .Contains("below your Drain line"));
        var refusing = files.Count(f => File.ReadAllText(f)
            .Contains(": \"it would take you to 0 HP\";"));
        Assert.True(refusing >= 11, $"{refusing} fixed-Drain refusals");
        Assert.Contains(": \"it would take you to 0 HP\";",
                        Generated("ProtoFsOverdraft"));
    }

    // ---- 5. Bubble Aria's chooser label --------------------------------------

    [Fact]
    public void Bubble_arias_spend_mode_says_the_block_it_also_gains()
    {
        var card = new ProtoFsBubbleAria();
        Assert.Equal(
            "Gain 6 [gold]Block[/gold]. [gold]Spend[/gold] 3: draw 2 cards.",
            card.ModeLabels[1]);
        Assert.Equal(
            "Gain 8 [gold]Block[/gold]. [gold]Spend[/gold] 3: draw 2 cards.",
            ((ProtoFsBubbleAria)Upgraded(new ProtoFsBubbleAria())).ModeLabels[1]);
    }

    // ---- 6. A calculated Block preview folds Frail and Dexterity -------------

    private sealed class Board
    {
        public required Seat Furina;
        public required CardModel Card;
    }

    private const int SeatFanfare = 20;

    private static Board Build(CardModel card, Action<Seat>? furinaPowers = null,
                               bool inHand = true)
    {
        FurinaStageLedger.ResetAll();
        var furina = Seat.Furina(66).WithCombatState();
        furinaPowers?.Invoke(furina);
        var listeners = furina.Creature.Powers.Cast<AbstractModel>().ToList();
        var run = DispatchProxy.Create<IRunState,
            FurinaSpendAllPreviewWeakTests.ListenerProxy>();
        ((FurinaSpendAllPreviewWeakTests.ListenerProxy)(object)run).Listeners =
            listeners;
        var combat = DispatchProxy.Create<ICombatState,
            FurinaSpendAllPreviewWeakTests.ListenerProxy>();
        ((FurinaSpendAllPreviewWeakTests.ListenerProxy)(object)combat).Listeners =
            listeners;
        Seat.Force(furina.Player, "RunState", run);
        furina.Creature.CombatState = combat;

        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", furina.Player);
        Seat.Force(furina.Player, "RunPiles", Array.Empty<CardPile>());
        var state = furina.Player.PlayerCombatState!;
        var pile = inHand ? state.Hand : state.DrawPile;
        ((List<CardModel>)typeof(CardPile)
            .GetField("_cards", HeadlessGame.All)!.GetValue(pile)!).Add(card);

        FurinaStageLedger.For(furina.Creature).Gain(SeatFanfare);
        return new Board { Furina = furina, Card = card };
    }

    private static void InCombat(Action body)
    {
        var field = typeof(CombatManager).GetField("_turnState", HeadlessGame.All)!;
        var saved = field.GetValue(CombatManager.Instance);
        var turn = RuntimeHelpers.GetUninitializedObject(field.FieldType);
        Seat.Set(turn, "IsInProgress", true);
        field.SetValue(CombatManager.Instance, turn);
        try
        {
            body();
        }
        finally
        {
            field.SetValue(CombatManager.Instance, saved);
            FurinaStageLedger.ResetAll();
        }
    }

    private static decimal BlockPreview(CardModel card, bool inHand = true)
    {
        var var = card.DynamicVars.CalculatedBlock;
        var.UpdateCardPreview(card, CardPreviewMode.Normal, null,
                              runGlobalHooks: inHand);
        return var.PreviewValue;
    }

    [Fact]
    public void The_show_must_go_on_is_declared_with_the_folding_var()
    {
        Assert.IsType<FoldedCalculatedBlockVar>(
            new ProtoFsTheShowMustGoOn().DynamicVars.CalculatedBlock);
        Assert.Contains("new FoldedCalculatedBlockVar(ValueProp.Move)",
                        Generated("ProtoFsTheShowMustGoOn"));
        Assert.DoesNotContain("new CalculatedBlockVar(",
                              Generated("ProtoFsTheShowMustGoOn"));
    }

    [Fact]
    public void In_hand_under_frail_the_show_must_go_on_previews_the_frailed_block()
    {
        InCombat(() =>
        {
            var b = Build(new ProtoFsTheShowMustGoOn(),
                          f => f.WithPower<FrailPower>(2));
            Assert.Equal(SeatFanfare,
                b.Card.DynamicVars.CalculatedBlock.Calculate(null));
            // 20 x 0.75 = 15: the Block the play gains.
            Assert.Equal(15m, BlockPreview(b.Card));
        });
    }

    [Fact]
    public void In_hand_with_dexterity_the_show_must_go_on_previews_the_added_block()
    {
        InCombat(() =>
        {
            var b = Build(new ProtoFsTheShowMustGoOn(),
                          f => f.WithPower<DexterityPower>(3));
            Assert.Equal(23m, BlockPreview(b.Card));
        });
    }

    [Fact]
    public void Off_her_hand_the_calculated_block_prints_its_formula()
    {
        InCombat(() =>
        {
            var b = Build(new ProtoFsTheShowMustGoOn(),
                          f => f.WithPower<FrailPower>(2), inHand: false);
            Assert.Equal(SeatFanfare, BlockPreview(b.Card, inHand: false));
        });
    }

    // ---- 7. Telemetry ---------------------------------------------------------

    [Fact]
    public void Her_ledger_keeps_the_peak_and_every_spend_with_the_bank_before()
    {
        var kit = StageKit.With(10);
        kit.Stage.BeginPlay("Hydro Lance+");
        Assert.True(kit.Stage.Spend(4));
        kit.Stage.EndPlay();
        kit.Stage.Gain(9);
        kit.Stage.MarkUpTo(12);
        Assert.True(kit.Stage.Spend(12));
        kit.Stage.SpendAll();
        Assert.Equal(15, kit.Stage.PeakFanfare);
        Assert.Equal(new[]
            {
                new StageSpendRecord("Hydro Lance+", 4, 10, -1),
                new StageSpendRecord("", 12, 15, 12),
                new StageSpendRecord("", 3, 3, -1),
            },
            kit.Stage.Spends.ToArray());
        // Peek creates nothing.
        Assert.Null(FurinaStageLedger.Peek(Seat.Furina().Creature));
    }

    private static string[] WrittenLines(Action act)
    {
        var field = Telemetry.GetField("_path", HeadlessGame.All)!;
        var saved = field.GetValue(null);
        var path = Path.Combine(Path.GetTempPath(),
            $"gits-telemetry-test-{Guid.NewGuid():N}.jsonl");
        field.SetValue(null, path);
        try
        {
            act();
            return File.Exists(path) ? File.ReadAllLines(path) : Array.Empty<string>();
        }
        finally
        {
            field.SetValue(null, saved);
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void A_furina_fight_writes_her_fanfare_record()
    {
        var furina = Seat.Furina(80).WithCombatState();
        var combat = DispatchProxy.Create<ICombatState,
            FurinaSpendAllPreviewWeakTests.ListenerProxy>();
        furina.Creature.CombatState = combat;
        Invoke("OpenSeatForTest", furina.Player, 1, 0);
        var ledger = FurinaStageLedger.For(furina.Creature);
        ledger.Gain(14);
        ledger.BeginPlay("Hydro Lance");
        ledger.Spend(4);
        ledger.EndPlay();

        Invoke("RecordTurnEnd", 1);
        var json = (string?)Invoke("JsonForTest", furina.Player);
        var r = JsonDocument.Parse(json!).RootElement;
        Assert.Equal(14, r.GetProperty("fanfare_peak").GetInt32());
        Assert.Equal(10, r.GetProperty("fanfare_end").GetInt32());
        var spend = Assert.Single(r.GetProperty("fanfare_spends").EnumerateArray());
        Assert.Equal("Hydro Lance", spend.GetProperty("card").GetString());
        Assert.Equal(4, spend.GetProperty("spent").GetInt32());
        Assert.Equal(14, spend.GetProperty("before").GetInt32());
        Assert.Equal(-1, spend.GetProperty("cap").GetInt32());

        // Anyone else writes none of the three.
        var klee = Seat.Klee();
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        var kr = JsonDocument.Parse((string)Invoke("JsonForTest", klee.Player)!)
            .RootElement;
        Assert.False(kr.TryGetProperty("fanfare_peak", out _));
        Assert.True(kr.TryGetProperty("hp_after_return", out _));
    }

    [Fact]
    public void A_won_fight_waits_for_the_end_of_combat_effects_and_writes_the_hp_after()
    {
        var klee = Seat.Klee(80);
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        Invoke("ArmReturnWatchForTest", true);
        var lines = WrittenLines(() =>
        {
            Seat.Force(klee.Creature, "CurrentHp", 50);
            Invoke("RecordTurnEnd", 1);
            Invoke("CloseIfOver", false);                 // the last enemy fell
            Assert.Equal(1, (int)Invoke("AwaitingReturnForTest")!);
            Seat.Force(klee.Creature, "CurrentHp", 56);   // the curtain call
            Invoke("FinishReturns", true);                // CombatWon
            Invoke("FinishReturns", true);                // writes nothing more
        });
        var r = JsonDocument.Parse(Assert.Single(lines)).RootElement;
        Assert.Equal("won", r.GetProperty("outcome").GetString());
        Assert.Equal(50, r.GetProperty("hp_end").GetInt32());
        Assert.Equal(56, r.GetProperty("hp_after_return").GetInt32());
    }

    [Fact]
    public void A_death_is_written_at_once_and_an_unheard_return_reads_minus_one()
    {
        var klee = Seat.Klee(80);
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        Invoke("ArmReturnWatchForTest", true);
        var died = WrittenLines(() =>
        {
            Seat.Force(klee.Creature, "CurrentHp", 0);
            Invoke("CloseOnSeatDeath", klee.Creature, true);
        });
        var d = JsonDocument.Parse(Assert.Single(died)).RootElement;
        Assert.Equal("died", d.GetProperty("outcome").GetString());
        Assert.Equal(0, d.GetProperty("hp_after_return").GetInt32());

        var again = Seat.Klee(80);
        Invoke("OpenSeatForTest", again.Player, 1, 0);
        var unheard = WrittenLines(() =>
        {
            Invoke("CloseIfOver", false);
            Invoke("FinishReturns", false);               // the next fight opened
        });
        Assert.Equal(-1, JsonDocument.Parse(Assert.Single(unheard)).RootElement
            .GetProperty("hp_after_return").GetInt32());
    }

    [Fact]
    public void Unarmed_a_won_fight_is_written_at_once_with_hp_after_equal_to_hp_end()
    {
        var klee = Seat.Klee(80);
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        var lines = WrittenLines(() =>
        {
            Seat.Force(klee.Creature, "CurrentHp", 61);
            Invoke("RecordTurnEnd", 1);
            Invoke("CloseIfOver", false);
        });
        var r = JsonDocument.Parse(Assert.Single(lines)).RootElement;
        Assert.Equal(61, r.GetProperty("hp_end").GetInt32());
        Assert.Equal(61, r.GetProperty("hp_after_return").GetInt32());
    }

    [Fact]
    public void The_fight_opens_by_writing_any_unheard_return_and_watching_for_the_next()
    {
        var calls = Il.Calls(Il.Method("PlayTelemetry", "OpenFight"));
        Assert.Contains("PlayTelemetry.FinishReturns", calls);
        Assert.Contains("PlayTelemetry.EnsureReturnWatch", calls);
        Assert.Contains("PlayTelemetry.NoteStage",
            Il.Calls(Il.Method("PlayTelemetry", "FlushAll")));
    }
}
