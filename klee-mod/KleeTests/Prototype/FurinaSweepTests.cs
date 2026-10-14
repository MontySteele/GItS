using System;
using System.IO;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE SWEEP (<c>review/active/furina-sweep-2026-10-14.md</c> sec.2
/// and sec.3): fifteen cut, fifteen new, the pool still 78 at 23 / 35 / 20.
/// Structural pins over the generated cards and <see cref="FurinaCards"/>'
/// seven verbs, each the base card's command calls; the behaviour is the sim
/// twin's, <c>tier0/tests/test_furina_sweep_2026_10_14.py</c>.
/// </summary>
public class FurinaSweepTests
{
    private static string Generated(string type) => File.ReadAllText(
        Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode", "Cards",
                     "Prototype", "Generated", type + ".cs"));

    private static string Face(CardModel card) =>
        ((BaseLib.Abstracts.CustomCardModel)card).Localization!
            .Single(r => r.Item1 == "description").Item2;

    private static CardModel Upgraded(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        card.UpgradeInternal();
        return card;
    }

    private static readonly string[] Cut =
    {
        "ProtoFsSoloistsSolicitation", "ProtoFsSpiritedAria",
        "ProtoFsStandingOvationAll", "ProtoFsHydroLance", "ProtoFsOverdraft",
        "ProtoFsPackedHouse", "ProtoFsIntervalBell", "ProtoFsSoothingWaters",
        "ProtoFsBalanceTheBooks", "ProtoFsSalonsEncore", "ProtoFsOusiaSurge",
        "ProtoFsHighStakes", "ProtoFsPneumaTides", "ProtoFsTheDeluge",
        "ProtoFsHymnOfRenewal",
    };

    private static readonly (Type Type, CardRarity Rarity)[] New =
    {
        (typeof(ProtoFsRainOfTears), CardRarity.Common),
        (typeof(ProtoFsRehearsal), CardRarity.Common),
        (typeof(ProtoFsSilenceInTheCourt), CardRarity.Common),
        (typeof(ProtoFsPirouette), CardRarity.Common),
        (typeof(ProtoFsSpotlightGrab), CardRarity.Common),
        (typeof(ProtoFsCostumeFitting), CardRarity.Common),
        (typeof(ProtoFsQuickChange), CardRarity.Uncommon),
        (typeof(ProtoFsReadTheScript), CardRarity.Uncommon),
        (typeof(ProtoFsPracticedGrace), CardRarity.Uncommon),
        (typeof(ProtoFsMiseEnScene), CardRarity.Uncommon),
        (typeof(ProtoFsIntermission), CardRarity.Uncommon),
        (typeof(ProtoFsSecondAct), CardRarity.Uncommon),
        (typeof(ProtoFsSoloRecital), CardRarity.Uncommon),
        (typeof(ProtoFsPneumaAndOusia), CardRarity.Rare),
        (typeof(ProtoFsStandIn), CardRarity.Rare),
    };

    [Fact]
    public void The_fifteen_new_are_in_the_pool_at_their_rarities_and_the_fifteen_cut_are_gone()
    {
        var pool = ArmPools.Named("KleeMod.Powers.FurinaStageRoster", "Pool");
        var names = pool.Select(c => c.GetType().Name).ToHashSet();
        foreach (var (type, rarity) in New)
        {
            Assert.Contains(type.Name, names);
            Assert.Equal(rarity, ((CardModel)Activator.CreateInstance(type)!).Rarity);
        }
        foreach (var cut in Cut)
        {
            Assert.DoesNotContain(cut, names);
            Assert.Null(typeof(ProtoFsRainOfTears).Assembly.GetType(
                "KleeMod.Cards.Prototype.Generated." + cut));
        }
        Assert.Equal(17, pool.Count(c => c.Type == CardType.Power));
    }

    [Fact]
    public void Each_new_card_calls_its_verb()
    {
        Assert.Contains("FurinaCards.UpgradeInHand", Generated("ProtoFsCostumeFitting"));
        Assert.Contains("FurinaCards.DiscardHandRedraw", Generated("ProtoFsQuickChange"));
        Assert.Contains("FurinaCards.LookTakeDiscard", Generated("ProtoFsReadTheScript"));
        Assert.Contains("FurinaCards.FreeInHand", Generated("ProtoFsMiseEnScene"));
        Assert.Contains("FurinaCards.RetainHand", Generated("ProtoFsIntermission"));
        Assert.Contains("FurinaCards.DiscardToHand", Generated("ProtoFsSecondAct"));
        Assert.Contains("FurinaCards.CopyInHand", Generated("ProtoFsStandIn"));
        Assert.Contains("RecallFromDiscard.Recall", Generated("ProtoFsSpotlightGrab"));
        Assert.Contains("PowerCmd.Apply<ProtoFsSilenceInTheCourtPower>",
                        Generated("ProtoFsSilenceInTheCourt"));
        Assert.Contains("PowerCmd.Apply<DexterityPower>", Generated("ProtoFsPracticedGrace"));
        Assert.Contains("PowerCmd.Apply<PneumaAndOusiaPower>",
                        Generated("ProtoFsPneumaAndOusia"));
        Assert.Contains("HasEnergyCostX => true", Generated("ProtoFsSoloRecital"));
        Assert.Contains(".WithHitCount(x)", Generated("ProtoFsSoloRecital"));
        Assert.Contains(".WithHitCount(3)", Generated("ProtoFsPirouette"));
    }

    [Fact]
    public void The_verbs_are_the_base_cards_command_calls()
    {
        var upgrade = Il.Calls(Il.Method("FurinaCards", "UpgradeInHand"));
        Assert.Contains("CardSelectCmd.FromHandForUpgrade", upgrade);   // Armaments
        Assert.Contains("CardCmd.Upgrade", upgrade);
        Assert.Contains("CardCmd.DiscardAndDraw",                       // Calculated Gamble
            Il.Calls(Il.Method("FurinaCards", "DiscardHandRedraw")));
        var look = Il.Calls(Il.Method("FurinaCards", "LookTakeDiscard"));
        Assert.Contains("CardSelectCmd.FromSimpleGrid", look);
        Assert.Contains("CardCmd.Discard", look);
        var free = Il.Calls(Il.Method("FurinaCards", "FreeInHand"));
        Assert.Contains("CardEnergyCost.SetThisTurn", free);             // Enlightenment's calls
        Assert.Contains("CardEnergyCost.SetUntilPlayed", free);
        Assert.Contains("PowerCmd.Apply",                                // Equilibrium
            Il.Calls(Il.Method("FurinaCards", "RetainHand")));
        Assert.Contains("CardSelectCmd.FromCombatPile",                  // Hologram
            Il.Calls(Il.Method("FurinaCards", "DiscardToHand")));
        var copy = Il.Calls(Il.Method("FurinaCards", "CopyInHand"));
        Assert.Contains("CardModel.CreateClone", copy);                  // Dual Wield
        Assert.Contains("CardModel.AddKeyword", copy);
        Assert.Contains("CardPileCmd.AddGeneratedCardToCombat", copy);
    }

    [Fact]
    public void The_three_flag_upgrades_read_is_upgraded_and_the_numbers_move()
    {
        foreach (var type in new[] { "ProtoFsCostumeFitting", "ProtoFsQuickChange",
                                     "ProtoFsMiseEnScene" })
        {
            Assert.Contains("// furina_upgraded:", Generated(type));
        }
        foreach (var verb in new[] { "UpgradeInHand", "DiscardHandRedraw", "FreeInHand" })
        {
            Assert.Contains(Il.Calls(Il.Method("FurinaCards", verb)),
                            c => c.Contains("get_IsUpgraded"));
        }
        Assert.Equal(8m, Upgraded(new ProtoFsRainOfTears()).DynamicVars.Block.BaseValue);
        Assert.Equal(10m, Upgraded(new ProtoFsRehearsal()).DynamicVars.Block.BaseValue);
        Assert.Equal(14m, Upgraded(new ProtoFsIntermission()).DynamicVars.Block.BaseValue);
        Assert.Equal(7m, Upgraded(new ProtoFsSecondAct()).DynamicVars.Block.BaseValue);
        Assert.Equal(5m, Upgraded(new ProtoFsPirouette()).DynamicVars.Damage.BaseValue);
        Assert.Equal(12m, Upgraded(new ProtoFsSpotlightGrab()).DynamicVars.Damage.BaseValue);
        Assert.Equal(9m, Upgraded(new ProtoFsSoloRecital()).DynamicVars.Damage.BaseValue);
        Assert.Equal(8m, Upgraded(new ProtoFsSilenceInTheCourt())
            .DynamicVars["StrengthLoss"].BaseValue);
        Assert.Equal(3m, Upgraded(new ProtoFsPracticedGrace())
            .DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal(3m, Upgraded(new ProtoFsPneumaAndOusia())
            .DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal(0, Upgraded(new ProtoFsReadTheScript())
            .EnergyCost.GetWithModifiers(CostModifiers.None));
        Assert.Equal(0, Upgraded(new ProtoFsStandIn())
            .EnergyCost.GetWithModifiers(CostModifiers.None));
    }

    [Fact]
    public void The_faces_read_as_the_paper()
    {
        Assert.Equal("Discard your [gold]Hand[/gold], then draw that many "
                     + "cards{IfUpgraded:show: plus 1|}.", Face(new ProtoFsQuickChange()));
        Assert.Equal("Choose a card in your [gold]Hand[/gold]. Add a copy of it "
                     + "to your [gold]Hand[/gold]. The copy [gold]Exhausts[/gold].",
                     Face(new ProtoFsStandIn()));
        Assert.Contains("X times", Face(new ProtoFsSoloRecital()));
        Assert.Contains(CardKeyword.Retain, new ProtoFsRehearsal().Keywords);
        Assert.Contains(CardKeyword.Exhaust, new ProtoFsSilenceInTheCourt().Keywords);
        Assert.Contains(CardKeyword.Exhaust, new ProtoFsQuickChange().Keywords);
        Assert.Contains(CardKeyword.Exhaust, new ProtoFsSecondAct().Keywords);
    }

    [Fact]
    public void Pneuma_and_ousia_reads_the_play_and_silence_is_piercing_wails_power()
    {
        var calls = Il.Calls(typeof(PneumaAndOusiaPower)
            .GetMethod("AfterCardPlayed", HeadlessGame.All)!);
        Assert.Contains("CreatureCmd.GainBlock", calls);
        Assert.Contains("ElementalHit.DealUnelemented", calls);
        Assert.True(typeof(MegaCrit.Sts2.Core.Models.Powers.TemporaryStrengthPower)
            .IsAssignableFrom(typeof(ProtoFsSilenceInTheCourtPower)));
    }
}
