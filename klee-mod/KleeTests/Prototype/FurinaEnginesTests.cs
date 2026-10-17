using System;
using System.IO;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;
using Xunit.Abstractions;
using static KleeMod.Tests.Prototype.StageKit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA'S ENGINES (<c>review/active/furina-next-2026-10-15.md</c>, ruled
/// 2026-10-16, pick 1 (a), as revised): Crescendo, Standing Room Only and
/// Prima Donna each lose the condition that kept them from firing. Headless
/// over the director and the recording board (<see cref="StageKit"/>) where
/// the rule is the director's; the generated card where it is the sheet's.
/// Sim twin: <c>tier0/tests/test_furina_pool75.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaEnginesTests : IDisposable
{
    private readonly ITestOutputHelper _out;

    public FurinaEnginesTests(ITestOutputHelper output)
    {
        _out = output;
        FurinaStageLedger.ResetAll();
    }

    public void Dispose() => FurinaStageLedger.ResetAll();

    private static string Generated(string type) => File.ReadAllText(
        Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode", "Cards",
                     "Prototype", "Generated", type + ".cs"));

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .Single(r => r.Item1 == "description").Item2;

    private static CardModel Upgraded(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    /// <summary>Her turn closes and the next opens: the end-of-turn latch
    /// (<see cref="FurinaStageLedger.CloseTurn"/>), then the turn-open reset.
    /// </summary>
    private static void NextTurn(StageKit kit)
    {
        kit.Stage.CloseTurn();
        kit.Stage.OpenTurn();
    }

    // ---- Crescendo ----------------------------------------------------------

    [Fact]
    public void Crescendo_counts_from_the_turn_it_is_played()
    {
        // Played this turn: its first payment is at the next turn start.
        var kit = StageKit.With(new StageMods { Crescendo = 2 }, 0);
        var paid = Enumerable.Range(0, 4)
            .Select(_ => kit.Director.Crescendo()).ToArray();
        Assert.Equal(new[] { 2, 4, 6, 8 }, paid);
        Assert.Equal(20, kit.Stage.Fanfare);            // the paper's 20
    }

    [Fact]
    public void A_later_copy_starts_small_and_the_upgrade_steps_by_three()
    {
        var kit = StageKit.With(new StageMods { Crescendo = 2 }, 0);
        Assert.Equal(2, kit.Director.Crescendo());
        Assert.Equal(4, kit.Director.Crescendo());
        // An upgraded copy joins (2 + 3 applied): it pays 3, the first 6.
        kit.Stage.ModsOverride = new StageMods { Crescendo = 5 };
        Assert.Equal(6 + 3, kit.Director.Crescendo());
        Assert.Equal(8 + 6, kit.Director.Crescendo());
        var none = StageKit.With(0);
        Assert.Equal(0, none.Director.Crescendo());
    }

    [Fact]
    public void Crescendo_is_2_and_3_upgraded_with_no_innate()
    {
        var card = new ProtoFsCrescendo();
        Assert.Equal(2, card.DynamicVars["PowerAmount"].IntValue);
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal("At the start of your turn, gain {PowerAmount:diff()} "
                     + "[gold]Fanfare[/gold], then {PowerAmount:diff()} more "
                     + "each turn after.", Face(card));
        var plus = Upgraded(new ProtoFsCrescendo());
        Assert.Equal(3, plus.DynamicVars["PowerAmount"].IntValue);
        Assert.DoesNotContain(CardKeyword.Innate, plus.Keywords);
        Assert.Contains("FurinaStage.CrescendoGains",
                        Il.Calls(Il.Method("FurinaStage", "TurnStart")));
    }

    // ---- Standing Room Only -------------------------------------------------

    [Fact]
    public void Standing_room_only_answers_every_spend_of_at_least_one()
    {
        var kit = StageKit.With(new StageMods { StandingRoomOnly = 1 }, 6);
        Run(kit.Director.Spend(2));                     // a fixed Spend
        Run(kit.Director.SpendUpTo(2));                 // a Spend up to
        Run(kit.Director.SpendAll());                   // a spend-all
        Assert.Equal(3, kit.Board.Gained);
        // A Spend of 0 is no Spend.
        Assert.Equal(0, Run(kit.Director.SpendAll()));
        Assert.Equal(0, Run(kit.Director.SpendUpTo(4)));
        Assert.Equal(0, Run(kit.Director.Spend(0)));
        Assert.Equal(3, kit.Board.Gained);
    }

    [Fact]
    public void Guest_spends_count_navia_freminet_and_showstopper()
    {
        var mods = new StageMods { StandingRoomOnly = 1, Showstopper = 1 };
        var kit = StageKit.With(mods, 40, StagePerformer.Freminet,
                                StagePerformer.Navia);
        Run(kit.Director.EndOfTurn(0));
        // Freminet's and Navia's share-Spends, Showstopper's Spend 5, then
        // their shares again: one Strength a Spend.
        Assert.Equal(5, kit.Stage.SpendsThisTurn);
        Assert.Equal(5, kit.Board.Gained);
    }

    [Fact]
    public void Standing_room_only_costs_1_and_upgrades_to_innate()
    {
        var card = new ProtoFsStandingRoomOnly();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal("Whenever you [gold]Spend[/gold], gain 1 "
                     + "[gold]Strength[/gold].", Face(card));
        var plus = Upgraded(new ProtoFsStandingRoomOnly());
        Assert.Equal(1, plus.EnergyCost.Canonical);
        Assert.Contains(CardKeyword.Innate, plus.Keywords);
    }

    /// <summary>The paper's runaway check (sec.3): Standing Room Only with
    /// Full House, Showstopper and three damaging guests on a large bank.
    /// One end of turn: three Full House Spends, Showstopper's Spend 5, and
    /// three more Full House Spends -- 7 Strength.</summary>
    [Fact]
    public void Full_house_showstopper_and_three_damaging_guests_give_seven_strength_a_turn()
    {
        var mods = new StageMods
        {
            StandingRoomOnly = 1, FullHouse = 4, Showstopper = 1,
        };
        var kit = StageKit.With(mods, 200, StagePerformer.Wriothesley,
                                StagePerformer.Clorinde,
                                StagePerformer.Lynette);
        Run(kit.Director.EndOfTurn(0));
        _out.WriteLine($"Strength in one turn: {kit.Board.Gained} "
                       + $"({kit.Stage.SpendsThisTurn} Spends, "
                       + $"{200 - kit.Stage.Fanfare} Fanfare spent)");
        Assert.Equal(7, kit.Stage.SpendsThisTurn);
        Assert.Equal(7, kit.Board.Gained);
        Assert.Equal(200 - 6 * 4 - 5, kit.Stage.Fanfare);
    }

    // ---- Prima Donna --------------------------------------------------------

    [Fact]
    public void Prima_donna_pays_only_for_a_spend_last_turn()
    {
        var kit = StageKit.With(new StageMods { PrimaDonna = 1 }, 4);
        Assert.Equal(0, Run(kit.Director.PrimaDonna()));   // no turn closed
        // A Spend this turn does not pay this turn (Quick Flourish's
        // refund): only once the turn has closed.
        Run(kit.Director.Spend(2));
        Assert.Equal(0, Run(kit.Director.PrimaDonna()));
        NextTurn(kit);
        Assert.Equal(1, Run(kit.Director.PrimaDonna()));
        Assert.Equal(1, kit.Board.Energy);
        // A turn with no Spend: nothing the turn after.
        NextTurn(kit);
        Assert.Equal(0, Run(kit.Director.PrimaDonna()));
        Assert.Equal(1, kit.Board.Energy);
        Assert.Equal(0, kit.Board.Drawn);
    }

    [Fact]
    public void A_spend_of_zero_does_not_count_for_prima_donna()
    {
        var kit = StageKit.With(new StageMods { PrimaDonna = 1 }, 0);
        Run(kit.Director.SpendUpTo(10));
        Run(kit.Director.SpendAll());
        Run(kit.Director.Spend(0));
        NextTurn(kit);
        Assert.Equal(0, Run(kit.Director.PrimaDonna()));
    }

    [Fact]
    public void An_end_of_turn_spend_counts_as_last_turn()
    {
        // Showstopper's Spend 5 at the end of her turn; EndOfTurn closes it.
        var kit = StageKit.With(new StageMods { PrimaDonna = 1, Showstopper = 1 },
                                5, StagePerformer.Wriothesley);
        Run(kit.Director.EndOfTurn(0));
        kit.Stage.OpenTurn();
        Assert.Equal(1, Run(kit.Director.PrimaDonna()));
    }

    [Fact]
    public void The_upgraded_prima_donna_also_draws_a_card()
    {
        var kit = StageKit.With(
            new StageMods { PrimaDonna = 1, PrimaDonnaDraw = 1 }, 3);
        Run(kit.Director.Spend(3));
        NextTurn(kit);
        Assert.Equal(1, Run(kit.Director.PrimaDonna()));
        Assert.Equal(1, kit.Board.Energy);
        Assert.Equal(1, kit.Board.Drawn);
    }

    [Fact]
    public void Prima_donna_costs_2_and_its_upgrade_installs_the_plus_power()
    {
        var card = new ProtoFsPrimaDonna();
        Assert.Equal(2, card.EnergyCost.Canonical);
        Assert.Equal("At the start of your turn, if you [gold]Spent[/gold] "
                     + "last turn, gain {energyPrefix:energyIcons(1)}"
                     + "{IfUpgraded:show: and draw 1 card|}.", Face(card));
        var plus = Upgraded(new ProtoFsPrimaDonna());
        Assert.Equal(2, plus.EnergyCost.Canonical);
        var source = Generated("ProtoFsPrimaDonna");
        Assert.Contains("PowerCmd.Apply<PrimaDonnaPlusPower>", source);
        Assert.Contains("PowerCmd.Apply<PrimaDonnaPower>", source);
        Assert.DoesNotContain("EnergyCost.UpgradeBy", source);
    }
}
