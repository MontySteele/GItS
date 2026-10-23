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

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA-NEXT PAPER 2 (<c>review/active/furina-next-2-2026-10-16.md</c>
/// sec.2, ruled 2026-10-16, picks 1 (a) and 2 (a)): Bravura spends up to 18,
/// Bring the House Down up to 10 for each guest on stage, and Extended Run
/// takes Bis!'s slot: "Attacks and Skills that Spend up to a number can Spend
/// 8 [12] more." Its scope, pinned as the paper asks: it adds once, flat, to
/// a played card's whole cap, copies add, and it does not touch Full House,
/// a guest's share-Spend or a fixed Spend. Headless over the ledger, the
/// director and the recording board (<see cref="StageKit"/>); the card verb
/// is pinned off the generated card and the IL. Sim twin:
/// <c>tier0/tests/test_furina_extended_run.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaExtendedRunTests : IDisposable
{
    public FurinaExtendedRunTests() => FurinaStageLedger.ResetAll();

    public void Dispose() => FurinaStageLedger.ResetAll();

    private static T Run<T>(System.Threading.Tasks.Task<T> task) =>
        StageKit.Run(task);

    private static void Run(System.Threading.Tasks.Task task) =>
        StageKit.Run(task);

    private static string Generated(string type) => File.ReadAllText(
        Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode", "Cards",
                     "Prototype", "Generated", type + ".cs"));

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .Single(r => r.Item1 == "description").Item2;

    private static string Title(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .Single(r => r.Item1 == "title").Item2;

    private static CardModel Upgraded(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    /// <summary>A played card's "Spend up to <paramref name="printed"/>",
    /// as <c>FurinaStage.SpendUpTo</c> pays it: the ledger's card cap, then
    /// the director's one Spend.</summary>
    private static int CardSpend(StageKit kit, int printed) =>
        Run(kit.Director.SpendUpTo(kit.Stage.CardUpToCap(printed)));

    // ---- the card ------------------------------------------------------------

    [Fact]
    public void Extended_run_is_a_rare_power_for_1_on_bis_old_id()
    {
        var card = new ProtoFsBis();
        Assert.Equal("Extended Run", Title(card));
        Assert.Equal(
            "Attacks and Skills that [gold]Spend[/gold] up to a number can "
            + "[gold]Spend[/gold] {PowerAmount:diff()} more.", Face(card));
        Assert.Equal(CardType.Power, card.Type);
        Assert.Equal(CardRarity.Rare, card.Rarity);
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(8, card.DynamicVars["PowerAmount"].IntValue);
        var plus = Upgraded(new ProtoFsBis());
        Assert.Equal(12, plus.DynamicVars["PowerAmount"].IntValue);
        Assert.DoesNotContain(CardKeyword.Innate, plus.Keywords);
        Assert.Contains("PowerCmd.Apply<ExtendedRunPower>",
                        Generated("ProtoFsBis"));
        Assert.Null(typeof(ProtoFsBis).Assembly.GetType(
            "KleeMod.Powers.BisPower"));
    }

    // ---- the scope -------------------------------------------------------------

    [Fact]
    public void Bring_the_house_down_is_a_fixed_spend_it_leaves_alone()
    {
        // The upgrade census (2026-10-23): "Spend 5 for each guest on stage"
        // is a Spend N, not a "Spend up to", so no cap for Extended Run to
        // raise (it added 8 to the old 10-a-guest cap).
        Assert.DoesNotContain("SpendUpTo", Generated("ProtoFsBringTheHouseDown"));
        Assert.Equal(
            "Deal {Damage:diff()} damage. [gold]Spend[/gold] 5 for each "
            + "guest on stage: each guest acts twice.",
            Face(new ProtoFsBringTheHouseDown()));
    }

    [Theory]
    [InlineData(24, 42, 14)]    // two upgraded copies: 18 + 24
    [InlineData(16, 34, 11)]    // two copies: 18 + 16
    [InlineData(0, 18, 6)]      // none: Bravura's own 18
    public void Copies_add_on_bravura(int extended, int spent, int hits)
    {
        var kit = StageKit.With(new StageMods { ExtendedRun = extended },
                                200);
        Assert.Equal(spent, CardSpend(kit, 18));
        Assert.Equal(hits, spent / FurinaStageLaw.BravuraSpentPer);
        Assert.Equal(200 - spent, kit.Stage.Fanfare);
    }

    [Fact]
    public void Bravura_spends_up_to_18_and_hits_7_for_every_3()
    {
        var src = Generated("ProtoFsBravura");
        Assert.Contains(
            "await FurinaStage.SpendUpTo(choiceContext, Owner.Creature, 18);",
            src);
        Assert.DoesNotContain("SpendAll", src);
        Assert.Contains(".WithHitCount(0 + 1 * FurinaStage.SpentThrees(this))",
                        src);
        Assert.Contains("FurinaStage.SpentOrUpTo(card, 18)", src);
        Assert.Equal(3, FurinaStageLaw.BravuraSpentPer);
        Assert.Equal(7m, new ProtoFsBravura().DynamicVars.Damage.BaseValue);
        Assert.Equal(9m, Upgraded(new ProtoFsBravura())
            .DynamicVars.Damage.BaseValue);
        Assert.StartsWith(
            "[gold]Spend[/gold] up to 18. Deal {Damage:diff()} "
            + "[gold]Hydro[/gold] damage for every 3 spent.",
            Face(new ProtoFsBravura()));
    }

    [Fact]
    public void Full_house_cap_is_unchanged()
    {
        var kit = StageKit.With(new StageMods { FullHouse = 4, ExtendedRun = 12 },
                                20);
        Assert.Equal(4, Run(kit.Director.FullHouse()));
        Assert.Equal(16, kit.Stage.Fanfare);
    }

    [Fact]
    public void Quick_flourishs_fixed_cost_is_unchanged()
    {
        var kit = StageKit.With(new StageMods { ExtendedRun = 12 }, 20);
        Assert.Equal(4, Run(kit.Director.Spend(4)));
        Assert.Equal(16, kit.Stage.Fanfare);
        Assert.Contains("await FurinaStage.Spend(choiceContext, Owner.Creature, 4);",
                        Generated("ProtoFsQuickCue"));
    }

    [Fact]
    public void A_guests_share_spend_is_unchanged()
    {
        // Navia's and Freminet's fractional Spends go through the director's
        // share, which never reads Extended Run.
        var kit = StageKit.With(new StageMods { ExtendedRun = 12 }, 20);
        Assert.Equal(5, Run(kit.Director.SpendShare(4)));
        Assert.Equal(15, kit.Stage.Fanfare);
    }

    [Fact]
    public void Only_the_card_verb_reads_it()
    {
        // The verb an Attack's or Skill's "Spend up to" calls adds the cap;
        // Spend half, the director's Spend and Full House do not.
        Assert.Contains("FurinaStageLedger.CardUpToCap",
                        Il.Calls(Il.Method("FurinaStage", "SpendUpTo")));
        Assert.Contains("FurinaStageLedger.CardUpToCap",
                        Il.Calls(Il.Method("FurinaStage", "SpentOrUpTo")));
        Assert.DoesNotContain("FurinaStageLedger.CardUpToCap",
                              Il.Calls(Il.Method("FurinaStage", "SpendHalf")));
        Assert.DoesNotContain("FurinaStageLedger.CardUpToCap",
                              Il.Calls(Il.Method("StageDirector", "FullHouse")));
        Assert.DoesNotContain("FurinaStageLedger.CardUpToCap",
                              Il.Calls(Il.Method("StageDirector", "SpendUpTo")));
    }

    [Fact]
    public void A_spend_all_keeps_nothing_back()
    {
        // Bis! is gone: Rising Applause and Let the People Rejoice take the
        // whole bank whatever Extended Run says.
        var kit = StageKit.With(new StageMods { ExtendedRun = 8 }, 20);
        Assert.Equal(20, Run(kit.Director.SpendAll()));
        Assert.Equal(0, kit.Stage.Fanfare);
    }
}
