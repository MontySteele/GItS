using System;
using System.IO;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;
using static KleeMod.Tests.Prototype.StageKit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE DIVERSITY PASS (<c>review/active/furina-diversity-pass-2026-10-11.md</c>
/// sec.2 and sec.3, ruled 2026-10-11, all defaults): the two guest styles'
/// cards and the floors. Headless over the director and the recording board
/// (<see cref="StageKit"/>) where the rule is the director's; the generated
/// card where it is the sheet's. Sim twin:
/// <c>tier0/tests/test_furina_diversity_pass.py</c>.
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class FurinaDiversityPassTests : IDisposable
{
    public FurinaDiversityPassTests() => FurinaStageLedger.ResetAll();

    public void Dispose() => FurinaStageLedger.ResetAll();

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

    // ---- the pool ---------------------------------------------------------

    [Fact]
    public void The_four_new_cards_are_in_the_pool_and_the_four_cut_are_gone()
    {
        var pool = ArmPools.Named("KleeMod.Powers.FurinaStageRoster", "Pool");
        var names = pool.Select(c => c.GetType().Name).ToHashSet();
        foreach (var added in new[] { "ProtoFsHeadliner", "ProtoFsTheLeadingLady",
                                      "ProtoFsTheFullHouse", "ProtoFsPackedHouse" })
        {
            Assert.Contains(added, names);
        }
        foreach (var cut in new[] { "ProtoFsGentleCurrent", "ProtoFsSurgingWaters",
                                    "ProtoFsPayTheTab", "ProtoFsSoldOut" })
        {
            Assert.DoesNotContain(cut, names);
            Assert.Null(typeof(ProtoFsHeadliner).Assembly.GetType(
                "KleeMod.Cards.Prototype.Generated." + cut));
        }
        Assert.Equal(CardRarity.Common, new ProtoFsTutti().Rarity);
        Assert.Equal(CardRarity.Common, new ProtoFsGuestStarWriothesley().Rarity);
        Assert.Equal(CardRarity.Common, new ProtoFsHeadliner().Rarity);
        Assert.Equal(CardRarity.Common, new ProtoFsPackedHouse().Rarity);
        Assert.Equal(CardRarity.Uncommon, new ProtoFsTheLeadingLady().Rarity);
        Assert.Equal(CardRarity.Uncommon, new ProtoFsTheFullHouse().Rarity);
    }

    // ---- Headliner and Packed House ----------------------------------------

    [Fact]
    public void Headliner_is_6_plus_2_a_guest_and_9_upgraded()
    {
        var card = new ProtoFsHeadliner();
        Assert.Equal(6m, card.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(2m, card.DynamicVars.ExtraDamage.BaseValue);
        Assert.Equal(9m, Upgraded(new ProtoFsHeadliner())
            .DynamicVars.CalculationBase.BaseValue);
        Assert.Contains("FurinaStage.Of(card.Owner?.Creature).Count",
                        Generated("ProtoFsHeadliner"));
    }

    [Fact]
    public void Packed_house_is_4_plus_1_every_5_fanfare_and_7_upgraded()
    {
        var card = new ProtoFsPackedHouse();
        Assert.Equal(4m, card.DynamicVars.CalculationBase.BaseValue);
        Assert.Equal(1m, card.DynamicVars.ExtraDamage.BaseValue);
        Assert.Equal(7m, Upgraded(new ProtoFsPackedHouse())
            .DynamicVars.CalculationBase.BaseValue);
        Assert.Contains("FurinaStage.FanfareFives(card.Owner?.Creature)",
                        Generated("ProtoFsPackedHouse"));
        Assert.Equal(5, FurinaStageLaw.PackedHouseFanfarePer);
        Assert.Equal(0, FurinaStage.FanfareFives(null));
    }

    // ---- Leading Lady ------------------------------------------------------

    [Fact]
    public void Leading_lady_gives_strength_and_1_a_guest_to_her_attacks()
    {
        Assert.Contains("PowerCmd.Apply<StrengthPower>",
                        Generated("ProtoFsTheLeadingLady"));
        Assert.Contains("PowerCmd.Apply<LeadingLadyPower>",
                        Generated("ProtoFsTheLeadingLady"));
        Assert.Equal(1, new ProtoFsTheLeadingLady()
            .DynamicVars["PowerAmount"].IntValue);
        Assert.Equal(2, Upgraded(new ProtoFsTheLeadingLady())
            .DynamicVars["PowerAmount"].IntValue);

        var furina = Seat.Furina(80).WithPower<LeadingLadyPower>(1);
        var enemy = Seat.Klee().Creature;
        var lady = furina.Creature.Powers.OfType<LeadingLadyPower>().Single();
        var attack = new ProtoFsHeadliner();
        decimal Hit(ValueProp props, CardModel? card) =>
            lady.ModifyDamageAdditive(enemy, 6m, props, furina.Creature,
                                      card, null);
        Assert.Equal(0m, Hit(ValueProp.Move, attack));      // no guests
        var ledger = FurinaStageLedger.For(furina.Creature);
        ledger.Seat(StagePerformer.Charlotte);
        ledger.Seat(StagePerformer.Clorinde);
        Assert.Equal(2m, Hit(ValueProp.Move, attack));      // 1 x 2 guests
        // Not a Skill's hit, not an unpowered one (a guest's act).
        Assert.Equal(0m, Hit(ValueProp.Move, new ProtoFsTutti()));
        Assert.Equal(0m, Hit(ValueProp.Unpowered, attack));
    }

    // ---- Full House --------------------------------------------------------

    [Fact]
    public void Full_house_spends_up_to_its_cap_into_each_damage_act()
    {
        var kit = StageKit.With(new StageMods { FullHouse = 4 }, 10,
                                StagePerformer.Wriothesley,
                                StagePerformer.Escoffier);
        Run(kit.Director.ActAll());
        Assert.Contains($"damage Wriothesley Random "
                        + $"{FurinaStageLaw.WriothesleyActDamage + 4} Cryo",
                        kit.Board.Log);
        // The second act gets what is left: 10 - 4 = 6, so 4 more.
        Assert.Contains($"damage Escoffier All "
                        + $"{FurinaStageLaw.EscoffierActDamage + 4} Cryo",
                        kit.Board.Log);
        Assert.Equal(2, kit.Stage.Fanfare);
    }

    [Fact]
    public void Full_house_takes_what_is_left_and_skips_an_act_with_no_damage()
    {
        var kit = StageKit.With(new StageMods { FullHouse = 6 }, 3,
                                StagePerformer.Charlotte,
                                StagePerformer.Clorinde);
        Run(kit.Director.ActAll());
        // Charlotte's act Repays and deals nothing: no Spend for her.
        Assert.Contains($"damage Clorinde Random "
                        + $"{FurinaStageLaw.ClorindeActDamage + 3} Electro",
                        kit.Board.Log);
        Assert.Equal(0, kit.Stage.Fanfare);
        // With no Full House the act is unchanged.
        var plain = StageKit.With(10, StagePerformer.Wriothesley);
        Run(plain.Director.ActAll());
        Assert.Contains($"damage Wriothesley Random "
                        + $"{FurinaStageLaw.WriothesleyActDamage} Cryo",
                        plain.Board.Log);
        Assert.Equal(10, plain.Stage.Fanfare);
    }

    [Fact]
    public void Full_house_is_4_and_6_upgraded()
    {
        Assert.Equal(4, new ProtoFsTheFullHouse()
            .DynamicVars["PowerAmount"].IntValue);
        Assert.Equal(6, Upgraded(new ProtoFsTheFullHouse())
            .DynamicVars["PowerAmount"].IntValue);
        Assert.Contains("PowerCmd.Apply<FullHousePower>",
                        Generated("ProtoFsTheFullHouse"));
    }

    // ---- the floors --------------------------------------------------------

    [Fact]
    public void Lynette_aims_at_an_aura_and_falls_back_to_any_enemy()
    {
        var kit = StageKit.Of(StagePerformer.Lynette);
        Run(kit.Director.ActAll());
        Assert.Contains($"damage Lynette Aura "
                        + $"{FurinaStageLaw.LynetteActDamage} Anemo",
                        kit.Board.Log);
        Assert.Contains("one with an aura if able",
                        Face(new ProtoFsGuestStarLynette()));
        Assert.Contains("one with an aura if able",
                        StagePerformerBadge.ActText(StagePerformer.Lynette));
    }

    [Fact]
    public void The_floors_print_and_call_what_the_paper_says()
    {
        Assert.Equal("Each guest acts. Draw 1 card.", Face(new ProtoFsTutti()));
        Assert.Contains("CardPileCmd.Draw", Generated("ProtoFsTutti"));
        // The paper's upgrade, kept under [USER]'s loop ruling (2026-10-11):
        // cost 0, the same draw of 1.
        Assert.Contains("EnergyCost.UpgradeBy(-1)", Generated("ProtoFsTutti"));
        Assert.Equal(1, Upgraded(new ProtoFsTutti()).DynamicVars.Cards.IntValue);
        Assert.StartsWith("Draw 1 card. Choose a guest.", Face(new ProtoFsFinalBow()));
        var bow = Generated("ProtoFsFinalBow");
        Assert.True(bow.IndexOf("CardPileCmd.Draw", StringComparison.Ordinal)
                    < bow.IndexOf("FurinaCards.FinalBow", StringComparison.Ordinal));
        Assert.Contains("If you can't, draw {FsAmount:diff()} cards.",
                        Face(new ProtoFsCastingCall()));
        Assert.Equal(2, new ProtoFsCastingCall().DynamicVars["FsAmount"].IntValue);
        Assert.Contains("CardPileCmd.Draw",
            Il.Calls(typeof(FurinaCards).GetMethod("TutorGuest")!));
        Assert.Equal("You have 4 guest seats. [gold]Summon[/gold] a random guest.",
                     Face(new ProtoFsEnsembleCast()));
        var cast = Generated("ProtoFsEnsembleCast");
        Assert.True(cast.IndexOf("PowerCmd.Apply<EnsembleCastPower>", StringComparison.Ordinal)
                    < cast.IndexOf("FurinaCards.SummonRandom", StringComparison.Ordinal));
        Assert.Contains("StageDirector.SummonGuest",
            Il.Calls(Il.Method("FurinaStage", "SummonRandom")));
    }
}
