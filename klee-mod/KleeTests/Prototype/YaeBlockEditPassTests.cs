#nullable enable

using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE YAE BLOCK AND EDIT PASS (2026-10-19,
/// <c>review/active/yae-block-edit-pass-2026-10-19.md</c> sec.2): Kitsune
/// Sakura at Defect's Frost access. Twin Sakura plants a Sakura and a Kitsune
/// Sakura, Cliffhanger is Kitsune Lantern (7 [10] and a Kitsune), Sakura
/// Canopy costs 2 for 6 [9] Block and 2 Kitsune. Faces, call graphs and the
/// display's preview pinned; the plants themselves walk the ledger's one
/// full-shrine rule (<see cref="YaeShrine.Plant"/>). The sim half is
/// <c>tier0/tests/test_yae_review_r3.py</c> and <c>test_yae_shrine.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeBlockEditPassTests : IDisposable
{
    public YaeBlockEditPassTests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose() => YaeShrineLedger.ResetAll();

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    private static string Title(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "title").Item2;

    private static int Plants(Type card) =>
        Il.CallSequence(card.GetMethod("OnPlay", HeadlessGame.All)!)
            .Count(c => c == "YaeCards.Plant");

    [Fact]
    public void Twin_sakura_plants_one_sakura_then_one_kitsune()
    {
        var twin = new ProtoYmTwinSakura();
        Assert.Equal("Plant a [gold]Sakura[/gold] and a [gold]Kitsune Sakura[/gold]."
                     + "{IfUpgraded:show: Gain 4 [gold]Block[/gold].|}", Face(twin));
        Assert.Equal(2, Plants(typeof(ProtoYmTwinSakura)));
        Assert.Equal(new[] { YaeSakuraKind.Thunder, YaeSakuraKind.Kitsune },
                     ((ISakuraPlantMixCard)twin).SakuraPlantKinds);
        Assert.Equal(1, twin.EnergyCost.Canonical);
    }

    [Fact]
    public void Twin_sakuras_preview_walks_both_plants_into_a_full_shrine()
    {
        var yae = Seat.Yae().Creature;
        var ledger = YaeShrineLedger.For(yae);
        for (var i = 0; i < 3; i++)
        {
            ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.None, YaeLaw.SakuraCap,
                         YaeSakuraKind.Thunder);
        }
        var preview = YaeSakuraSlots.PreviewFor(new ProtoYmTwinSakura(), yae);
        Assert.NotNull(preview);
        Assert.Equal(YaeSakuraSlots.Preview(ledger.Standing, YaeLaw.SakuraCap, YaePlantShape.Plant,
                         new[] { YaeSakuraKind.Thunder, YaeSakuraKind.Kitsune }),
                     preview);
    }

    [Fact]
    public void A_full_shrine_takes_twin_sakuras_kitsune_by_the_replace_rule()
    {
        // The ledger's rule both plants walk: the Sakura refreshes its kind,
        // then the Kitsune replaces a strike Sakura (not its kind).
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        for (var i = 0; i < 3; i++)
        {
            ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.None, YaeLaw.SakuraCap,
                         YaeSakuraKind.Thunder);
        }
        ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.None, YaeLaw.SakuraCap,
                     YaeSakuraKind.Thunder);
        ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.None, YaeLaw.SakuraCap,
                     YaeSakuraKind.Kitsune);
        Assert.Equal(3, ledger.Count);
        Assert.Equal(1, ledger.Standing.Count(s => s.Kind == YaeSakuraKind.Kitsune));
    }

    [Fact]
    public void Kitsune_lantern_deals_7_and_plants_a_kitsune()
    {
        var lantern = new ProtoYmCliffhanger();
        Assert.Equal("Kitsune Lantern", Title(lantern));
        Assert.Equal("Deal {Damage:diff()} [gold]Electro[/gold] damage. Plant a "
                     + "[gold]Kitsune Sakura[/gold].", Face(lantern));
        Assert.Equal(7m, lantern.DynamicVars.Damage.BaseValue);
        Assert.Equal(YaeSakuraKind.Kitsune, lantern.SakuraPlantKind);
        Assert.True(lantern is ISakuraPlanterCard);
        Assert.Equal(1, Plants(typeof(ProtoYmCliffhanger)));
        Assert.DoesNotContain(Il.CallSequence(typeof(ProtoYmCliffhanger).GetMethod(
            "OnPlay", HeadlessGame.All)!), c => c.Contains("YaeCards.Edit"));
    }

    [Fact]
    public void Sakura_canopy_costs_2_for_6_block_and_2_kitsune()
    {
        var canopy = new ProtoYmSakuraCanopy();
        Assert.Equal("Gain {Block:diff()} [gold]Block[/gold]. Plant {YmAmount:diff()} "
                     + "[gold]Kitsune Sakura[/gold].", Face(canopy));
        Assert.Equal(2, canopy.EnergyCost.Canonical);
        Assert.Equal(6m, canopy.DynamicVars.Block.BaseValue);
        Assert.Equal(2m, canopy.DynamicVars["YmAmount"].BaseValue);
        Assert.Equal(YaeSakuraKind.Kitsune, canopy.SakuraPlantKind);
        Assert.Equal(1, Plants(typeof(ProtoYmSakuraCanopy)));
    }
}
