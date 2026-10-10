using System.IO;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE SPEND PAPER, BUILT AT ITS DEFAULTS (2026-10-10,
/// <c>review/active/furina-spend-paper-2026-10-10.md</c> picks 1 and 2; the
/// picks are open on #1014). "Spend up to X" spends X, or all she holds if
/// that is less, never fails, and is a Spend only when at least 1 counts; it
/// is not a spend-all. Navia's act Spends half the bank and Freminet's a
/// quarter (ruled 2026-10-10), rounded down, oldest first. Pinned headlessly over the director and the
/// recording board (<see cref="StageKit"/>). Sim twin:
/// <c>tier0/tests/test_furina_spend_up_to.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaSpendUpToTests
{
    private static T Run<T>(System.Threading.Tasks.Task<T> task) =>
        StageKit.Run(task);

    private static void Run(System.Threading.Tasks.Task task) =>
        StageKit.Run(task);

    private static CardModel Upgraded(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, null);
        return card;
    }

    private static string Generated(string type) => File.ReadAllText(
        Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode", "Cards",
                     "Prototype", "Generated", type + ".cs"));

    private static string Face(CardModel card) =>
        ((BaseLib.Abstracts.CustomCardModel)card).Localization!
            .Single(r => r.Item1 == "description").Item2;

    private static int Count(StageKit kit, string prefix) =>
        kit.Board.Log.Count(l => l.StartsWith(prefix));

    // ---- the rule ------------------------------------------------------------

    [Theory]
    [InlineData(0, 0, 0)]       // nothing held: nothing spent, no Spend
    [InlineData(3, 3, 0)]       // partial: all 3
    [InlineData(10, 10, 0)]     // exactly X
    [InlineData(25, 10, 15)]    // over X: X
    public void Spend_up_to_spends_x_or_all_you_have(int bank, int spent,
                                                     int left)
    {
        var kit = StageKit.With(bank);
        Assert.Equal(spent, Run(kit.Director.SpendUpTo(10)));
        Assert.Equal(left, kit.Stage.Fanfare);
        Assert.Equal(spent, kit.Stage.SpentThisPlay);
        Assert.Equal(spent > 0 ? 1 : 0, kit.Stage.SpendsThisTurn);
    }

    [Fact]
    public void It_is_a_spend_only_when_at_least_one_is_spent()
    {
        var mods = new StageMods { Thunderous = 3, Crescendo = 1 };
        var none = StageKit.With(mods, 0, StagePerformer.Chevreuse);
        Assert.Equal(0, Run(none.Director.SpendUpTo(10)));
        Assert.Equal(0, none.Stage.SpendsThisTurn);
        Assert.Equal(0, Count(none, "power "));
        Assert.Equal(0, Count(none, "vulnerable "));
        Assert.Equal(0, Count(none, "draw "));

        var one = StageKit.With(mods, 1, StagePerformer.Chevreuse);
        Assert.Equal(1, Run(one.Director.SpendUpTo(10)));
        Assert.Equal(1, one.Stage.SpendsThisTurn);
        Assert.Equal(1, Count(one, "power "));            // Thunderous Applause
        Assert.Contains("vulnerable Random 1", one.Board.Log);   // Chevreuse
        Assert.Contains("draw 1", one.Board.Log);               // Crescendo
    }

    [Fact]
    public void Bis_and_standing_room_only_ignore_an_up_to_spend()
    {
        var mods = new StageMods { Bis = 1, StandingRoomOnly = 2 };
        var kit = StageKit.With(mods, 20);
        Assert.Equal(12, Run(kit.Director.SpendUpTo(12)));
        Assert.Equal(8, kit.Stage.Fanfare);                 // no half back
        Assert.Equal(0, Count(kit, "strength "));
        // The same bank through a spend-all: Bis! keeps half, SRO answers.
        var all = StageKit.With(mods, 20);
        Assert.Equal(20, Run(all.Director.SpendAll()));
        Assert.Equal(10, all.Stage.Fanfare);
        Assert.Contains("strength 2", all.Board.Log);
    }

    [Fact]
    public void Navias_first_two_points_are_free_on_an_up_to_spend()
    {
        // 5 held, up to 10: 2 free plus all 5 count, none left.
        var kit = StageKit.With(5, StagePerformer.Navia);
        Assert.Equal(7, Run(kit.Director.SpendUpTo(10)));
        Assert.Equal(0, kit.Stage.Fanfare);
        Assert.Equal(1, kit.Beats(FurinaStageLedger.LineEvent,
                                  StagePerformer.Navia));
        // The second Spend that turn pays full.
        kit.Stage.Gain(5);
        Assert.Equal(5, Run(kit.Director.SpendUpTo(10)));
        Assert.Equal(0, kit.Stage.Fanfare);

        // Nothing held: the 2 free points still count, and it is a Spend.
        var empty = StageKit.With(0, StagePerformer.Navia);
        Assert.Equal(2, Run(empty.Director.SpendUpTo(10)));
        Assert.Equal(1, empty.Stage.SpendsThisTurn);

        // Over X: X counts, X less 2 is taken.
        var rich = StageKit.With(20, StagePerformer.Navia);
        Assert.Equal(10, Run(rich.Director.SpendUpTo(10)));
        Assert.Equal(12, rich.Stage.Fanfare);

        // Upgraded Navia: 3 free.
        var up = StageKit.Of();
        Run(up.Director.SummonGuest(StagePerformer.Navia, true));
        up.Stage.Gain(10);
        Assert.Equal(8, Run(up.Director.SpendUpTo(8)));
        Assert.Equal(5, up.Stage.Fanfare);
    }

    [Fact]
    public void Center_of_attention_counts_the_full_x_and_takes_nothing()
    {
        var kit = StageKit.With(3);
        Assert.Equal(10, kit.Stage.SpendUpToFree(10));
        Assert.Equal(10, kit.Stage.SpentThisPlay);
        Assert.Equal(3, kit.Stage.Fanfare);
        Assert.Equal(0, kit.Stage.SpendsThisTurn);          // no Spend
    }

    // ---- the guests' share-Spend (Navia half, Freminet a quarter) -------------

    [Fact]
    public void Navias_act_spends_half_the_bank_and_deals_it_as_geo()
    {
        // A Spend first, so her line's discount is used up.
        var kit = StageKit.With(new StageMods { Thunderous = 3 }, 23,
                                StagePerformer.Navia, StagePerformer.Chevreuse);
        Run(kit.Director.Spend(3));                 // 3, 2 free: 22 left
        Assert.Equal(22, kit.Stage.Fanfare);
        kit.Board.Log.Clear();
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.Contains("damage Navia Random 11 Geo", kit.Board.Log);
        Assert.Equal(11, kit.Stage.Fanfare);
        // A guest's half-Spend is a Spend: Chevreuse and Thunderous fire.
        Assert.Contains("vulnerable Random 1", kit.Board.Log);
        Assert.Equal(1, Count(kit, "power "));
        // 1 held: half is 0, no Spend, no damage.
        var poor = StageKit.With(1, StagePerformer.Navia);
        Run(poor.Director.Act(poor.Stage.Seats[0]));
        Assert.Equal(0, Count(poor, "damage "));
        Assert.Equal(1, poor.Stage.Fanfare);
        Assert.Equal(0, poor.Stage.SpendsThisTurn);
    }

    [Fact]
    public void Freminets_act_gains_three_block_then_a_quarter_of_the_bank_as_block()
    {
        var kit = StageKit.With(9, StagePerformer.Freminet);
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.Equal(new[] { "block 3", "block 2" },        // a quarter of 9
                     kit.Board.Log.Where(l => l.StartsWith("block ")));
        Assert.Equal(7, kit.Stage.Fanfare);
        Assert.Equal(0, Count(kit, "damage "));             // no Cryo hit
        var up = StageKit.Of();
        Run(up.Director.SummonGuest(StagePerformer.Freminet, true));
        Run(up.Director.Act(up.Stage.Seats[0]));
        Assert.Equal(new[] { "block 6" },
                     up.Board.Log.Where(l => l.StartsWith("block ")));
        Assert.Equal(3, StageDirector.ActAmount(StagePerformer.Freminet, false));
        Assert.Equal(6, StageDirector.ActAmount(StagePerformer.Freminet, true));
    }

    [Fact]
    public void Two_guests_split_the_bank_oldest_first()
    {
        // Freminet first: a quarter of 40 is 10 (Navia's line makes 2 of it
        // free, the turn's first Spend), 32 left; Navia takes half, 16.
        var kit = StageKit.With(new StageMods { Thunderous = 3 }, 40,
                                StagePerformer.Freminet, StagePerformer.Navia);
        Assert.Equal(2, Run(kit.Director.ActAll()));
        Assert.Contains("block 10", kit.Board.Log);
        Assert.Contains("damage Navia Random 16 Geo", kit.Board.Log);
        Assert.Equal(16, kit.Stage.Fanfare);
        Assert.Equal(2, kit.Stage.SpendsThisTurn);
        Assert.Equal(2, Count(kit, "power "));              // two Spends
    }

    [Fact]
    public void Freminet_then_navia_on_40_with_no_discount()
    {
        // A Spend first uses up Navia's discount (41, 3 spent, 2 free: 40).
        // Freminet takes a quarter of 40, 10 (30 left); Navia half of 30, 15.
        var kit = StageKit.With(41, StagePerformer.Freminet,
                                StagePerformer.Navia);
        Run(kit.Director.Spend(3));
        Assert.Equal(40, kit.Stage.Fanfare);
        kit.Board.Log.Clear();
        Run(kit.Director.ActAll());
        Assert.Equal(new[] { "block 3", "block 10" },
                     kit.Board.Log.Where(l => l.StartsWith("block ")));
        Assert.Contains("damage Navia Random 15 Geo", kit.Board.Log);
        Assert.Equal(15, kit.Stage.Fanfare);
    }

    [Fact]
    public void Showstopper_makes_each_take_their_share_again()
    {
        var kit = StageKit.With(new StageMods { Showstopper = 1 }, 40,
                                StagePerformer.Navia, StagePerformer.Freminet);
        Run(kit.Director.EndOfTurn(0));
        // Round one: Navia 20 (2 free, 22 left), Freminet 5 (17 left).
        // Showstopper Spends 5 (12 left). Round two: Navia 6, Freminet 1.
        Assert.Equal(new[] { "damage Navia Random 20 Geo",
                             "damage Navia Random 6 Geo" },
                     kit.Board.Log.Where(l => l.StartsWith("damage ")));
        Assert.Equal(new[] { "block 3", "block 5", "block 3", "block 1" },
                     kit.Board.Log.Where(l => l.StartsWith("block ")));
        Assert.Equal(5, kit.Stage.Fanfare);
    }

    [Fact]
    public void The_forecast_walks_the_bank_in_seat_order()
    {
        var kit = StageKit.With(40, StagePerformer.Freminet,
                                StagePerformer.Navia);
        var cues = FurinaStage.Forecast(kit.Stage).Cues;
        Assert.Equal(StageCueKind.Block, cues[0].Kind);
        Assert.Equal(13, cues[0].Amount);                   // 3 + 10
        Assert.Equal(StageCueKind.Damage, cues[1].Kind);
        Assert.Equal(16, cues[1].Amount);
    }

    [Fact]
    public void The_two_guests_badges_print_their_share_spend()
    {
        Assert.EndsWith(
            "Act: gain 3 [gold]Block[/gold]. [gold]Spend[/gold] a quarter of your "
            + "[gold]Fanfare[/gold] (rounded down): gain that much more "
            + "[gold]Block[/gold].",
            StagePerformerBadge.ActText(StagePerformer.Freminet));
        Assert.Contains("Act: gain 6 [gold]Block[/gold].",
            StagePerformerBadge.ActText(StagePerformer.Freminet, true));
        Assert.EndsWith(
            "Act: [gold]Spend[/gold] half your [gold]Fanfare[/gold] (rounded "
            + "down). Deal that much [gold]Geo[/gold] damage to a random "
            + "enemy.",
            StagePerformerBadge.ActText(StagePerformer.Navia));
    }

    // ---- the four cards -------------------------------------------------------

    [Fact]
    public void The_four_cards_print_spend_up_to_and_upgrade_their_base()
    {
        Assert.StartsWith(
            "Deal {CalculationBase:diff()} [gold]Hydro[/gold] damage to ALL "
            + "enemies. [gold]Spend[/gold] up to 10: deal 1 more for each.",
            Face(new ProtoFsTidalFlourish()));
        Assert.StartsWith(
            "Deal {CalculationBase:diff()} damage. [gold]Spend[/gold] up to 8: "
            + "deal 1 more for each. Draw 1 for every 4 spent.",
            Face(new ProtoFsSpiritedAria()));
        Assert.Equal(
            "Deal {Damage:diff()} [gold]Hydro[/gold] damage twice. "
            + "[gold]Spend[/gold] up to 12: hit once more for every 4.",
            Face(new ProtoFsCrashingWaves()));
        Assert.StartsWith(
            "Gain {CalculationBase:diff()} [gold]Block[/gold]. "
            + "[gold]Spend[/gold] up to 12: gain 1 more for each.",
            Face(new ProtoFsHoldTheStage()));

        Assert.Equal(5m, new ProtoFsTidalFlourish().DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(8m, Upgraded(new ProtoFsTidalFlourish()).DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(8m, new ProtoFsSpiritedAria().DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(11m, Upgraded(new ProtoFsSpiritedAria()).DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(4m, new ProtoFsCrashingWaves().DynamicVars.Damage.BaseValue);
        Assert.Equal(5m, Upgraded(new ProtoFsCrashingWaves()).DynamicVars.Damage.BaseValue);
        Assert.Equal(6m, new ProtoFsHoldTheStage().DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(8m, Upgraded(new ProtoFsHoldTheStage()).DynamicVars.CalculationBase.BaseValue);
    }

    [Theory]
    [InlineData("ProtoFsTidalFlourish", 10)]
    [InlineData("ProtoFsSpiritedAria", 8)]
    [InlineData("ProtoFsCrashingWaves", 12)]
    [InlineData("ProtoFsHoldTheStage", 12)]
    public void Each_card_spends_up_to_its_x_on_play_with_no_chooser(
        string type, int cap)
    {
        var src = Generated(type);
        Assert.Contains(
            $"await FurinaStage.SpendUpTo(choiceContext, Owner.Creature, {cap});",
            src);
        Assert.DoesNotContain("ModalChoice", src);
        Assert.Null(typeof(ProtoFsTidalFlourish).Assembly.GetType(
            "KleeMod.Cards.Prototype.Generated." + type + "ModeA"));
    }

    [Fact]
    public void The_for_every_four_reads_this_plays_spend()
    {
        Assert.Contains(".WithHitCount(2 + 1 * FurinaStage.SpentFours(this))",
                        Generated("ProtoFsCrashingWaves"));
        Assert.Contains(
            "CardPileCmd.Draw(choiceContext, 0 + 1 * FurinaStage.SpentFours(this), Owner)",
            Generated("ProtoFsSpiritedAria"));
        Assert.Contains("FurinaStage.SpentOrUpTo(card, 8)",
                        Generated("ProtoFsSpiritedAria"));
        Assert.Equal(4, FurinaStageLaw.SpendUpToEvery);
        Assert.Equal(2, FurinaStageLaw.NaviaSpendDivisor);
        Assert.Equal(4, FurinaStageLaw.FreminetSpendDivisor);
    }
}
