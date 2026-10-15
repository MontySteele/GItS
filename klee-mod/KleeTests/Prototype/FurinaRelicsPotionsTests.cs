#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Potions;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA'S CARD PASS (2026-10-15,
/// <c>review/active/furina-card-pass-2026-10-15.md</c>): Ousia / Pneuma's two
/// halves, her six new relics and two new potions. On
/// <c>ArmRelicsPotionsTests</c>' terms: every decision runs on the headless
/// Stage kit (<see cref="StageKit"/>, whose board records Block, Energy and
/// the relic flashes); what awaits a live combat (a summon, a potion's use)
/// is pinned by its doors.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaRelicsPotionsTests : IDisposable
{
    public FurinaRelicsPotionsTests()
    {
        FurinaStageLedger.ResetAll();
    }

    public void Dispose()
    {
        FurinaStageLedger.ResetAll();
    }

    // ==== the shape and the pools ============================================

    [Fact]
    public void Her_seven_relics_in_the_base_shape_and_three_potions()
    {
        Assert.Equal(
            new[]
            {
                RelicRarity.Common, RelicRarity.Uncommon, RelicRarity.Uncommon,
                RelicRarity.Rare, RelicRarity.Rare, RelicRarity.Rare,
                RelicRarity.Shop,
            },
            FurinaStageRelics.Types.Select(t => Canon<RelicModel>(t).Rarity).ToArray());
        Assert.Equal(
            new[] { typeof(BottledApplause), typeof(BottledEncore), typeof(WaterOfLucine) },
            ArmPotions.Furina);
        Assert.Equal(
            new[] { PotionRarity.Common, PotionRarity.Uncommon, PotionRarity.Rare },
            ArmPotions.Furina.Select(t => Canon<PotionModel>(t).Rarity).ToArray());
    }

    [Fact]
    public void Her_pool_lists_and_offers_all_seven_with_her_starter_and_ancient()
    {
        var members = Il.CallSequence(Il.Method("FurinaRelicPool", "GenerateAllRelics"));
        foreach (var t in FurinaStageRelics.Types)
        {
            Assert.Contains($"ModelDb.Relic<{t.Name}>", members);
        }
        var pool = (FurinaRelicPool)RuntimeHelpers.GetUninitializedObject(typeof(FurinaRelicPool));
        SetField(pool, "_relics", FurinaStageRelics.Types
            .Append(typeof(SalonSolitaire)).Append(typeof(CurtainNeverFalls))
            .Append(typeof(MegaCrit.Sts2.Core.Models.Relics.NinjaScroll))
            .Select(t => (RelicModel)RuntimeHelpers.GetUninitializedObject(t)).ToList());
        var offer = pool.GetUnlockedRelics(null!).Select(r => r.GetType()).ToList();
        Assert.Equal(
            FurinaStageRelics.Types.Append(typeof(SalonSolitaire))
                .Append(typeof(CurtainNeverFalls)).OrderBy(t => t.Name),
            offer.OrderBy(t => t.Name));
        var potions = Il.CallSequence(Il.Method("FurinaPotionPool", "GenerateAllPotions"));
        Assert.Equal(ArmPotions.Furina.Select(t => $"ModelDb.Potion<{t.Name}>").ToArray(),
                     potions.Where(c => c.StartsWith("ModelDb.Potion<")).ToArray());
    }

    [Fact]
    public void The_faces_are_the_papers_words()
    {
        Assert.Equal("At the start of each combat, [gold]Summon[/gold] a random guest.",
                     Face(typeof(OperaTicketStub)));
        Assert.Equal("Whenever you [gold]Repay[/gold] more than you have drained, gain "
                     + "the rest as [gold]Block[/gold].", Face(typeof(FontaineTeardrop)));
        Assert.Equal("Whenever a guest acts, gain [blue]1[/blue] [gold]Fanfare[/gold].",
                     Face(typeof(ClaquesLedger)));
        Assert.Equal("Whenever you [gold]Spend[/gold] 10 or more at once, gain "
                     + "{energyPrefix:energyIcons(1)}.", Face(typeof(BouquetOfRoses)));
        Assert.Equal("You have [blue]1[/blue] more guest seat.",
                     Face(typeof(EpicleseSeasonPass)));
        Assert.Equal("Each guest acts twice.", Face(typeof(BottledEncore)));
        Assert.Equal("[gold]Repay[/gold] all your drained HP.", Face(typeof(WaterOfLucine)));
    }

    // ==== Ousia / Pneuma ====================================================

    [Fact]
    public void Ousia_drains_and_pneuma_repays_each_on_its_own_face()
    {
        var face = Face(typeof(ProtoFsOusiaPneuma));
        Assert.Contains("Ousia: [gold]Drain[/gold] 2. Deal {BranchDamage:diff()} damage.", face);
        Assert.Contains("Pneuma: [gold]Repay[/gold] 2. Gain {BranchBlock:diff()} [gold]Block[/gold].", face);
        var card = new ProtoFsOusiaPneuma();
        Assert.Equal(10m, card.DynamicVars["BranchDamage"].BaseValue);
        Assert.Equal(8m, card.DynamicVars["BranchBlock"].BaseValue);
        var play = Il.Calls(Il.Method("ProtoFsOusiaPneuma", "OnPlay"));
        Assert.Contains("FurinaStage.Drain", play);
        Assert.Contains("FurinaStage.Repay", play);
        Assert.Contains("FurinaCards.Flip", play);
        // Each face's in-combat line rides only that face.
        var args = Il.Calls(Il.Method("ProtoFsOusiaPneuma", "AddExtraArgsToDescription"));
        Assert.Contains("FurinaStageFacePreview.DrainLine", args);
        Assert.Contains("FurinaStageFacePreview.Repay", args);
    }

    // ==== the relics ========================================================

    [Fact]
    public void Opera_ticket_stub_summons_ensemble_casts_random_guest_on_turn_one()
    {
        Assert.Contains("FurinaStage.SummonRandom",
                        Il.Calls(Il.Method("OperaTicketStub", "AfterPlayerTurnStart")));
        Assert.Contains("FurinaStage.SummonRandom",
                        Il.Calls(Il.Method("FurinaCards", "SummonRandom")));
        var kit = StageKit.Of();
        StageKit.Run(kit.Director.SummonGuest(StagePerformer.Navia));
        Assert.Single(kit.Stage.Seats);
    }

    [Fact]
    public void Fontaine_teardrop_pays_the_repay_past_the_drained_hp_as_block()
    {
        var mods = new StageMods { FontaineTeardrop = 1 };
        // Nothing drained: all 3 is the rest.
        var kit = new StageKit(mods, 0, 78, 78);
        Assert.Equal(0, StageKit.Run(kit.Director.Repay(3)));
        Assert.Contains("block 3", kit.Board.Log);
        Assert.Equal(new[] { "FontaineTeardrop" }, kit.Board.Flashed);
        // 2 drained, Repay 3: 2 back and 1 Block.
        kit = new StageKit(mods, 0, 78, 78);
        StageKit.Run(kit.Director.Drain(2));
        Assert.Equal(2, StageKit.Run(kit.Director.Repay(3)));
        Assert.Contains("block 1", kit.Board.Log);
        // A Repay of no more than she drained pays nothing.
        kit = new StageKit(mods, 0, 78, 78);
        StageKit.Run(kit.Director.Drain(4));
        StageKit.Run(kit.Director.Repay(3));
        Assert.DoesNotContain(kit.Board.Log, l => l.StartsWith("block"));
        // A printed floor pays beside it: the two stack.
        kit = new StageKit(mods, 0, 78, 78);
        StageKit.Run(kit.Director.RepayFloor(3, StageFloor.Block));
        Assert.Equal(2, kit.Board.Log.Count(l => l == "block 3"));
        // Without it, nothing.
        kit = new StageKit(null, 0, 78, 78);
        StageKit.Run(kit.Director.Repay(3));
        Assert.DoesNotContain(kit.Board.Log, l => l.StartsWith("block"));
    }

    [Fact]
    public void Claques_ledger_gains_one_fanfare_a_guest_act()
    {
        var mods = new StageMods { ClaquesLedger = 1 };
        var kit = StageKit.With(mods, 0, StagePerformer.Wriothesley,
                                StagePerformer.Clorinde);
        Assert.Equal(2, StageKit.Run(kit.Director.ActAll()));
        Assert.Equal(2, kit.Stage.Fanfare);
        // A guest that acts twice gains 2.
        kit = StageKit.With(mods, 0, StagePerformer.Wriothesley);
        StageKit.Run(kit.Director.FinalBow(0, 2));
        Assert.Equal(2, kit.Stage.Fanfare);
        Assert.All(kit.Board.Flashed, f => Assert.Equal("ClaquesLedger", f));
        // Without it, an act gains none.
        kit = StageKit.With(0, StagePerformer.Wriothesley);
        StageKit.Run(kit.Director.ActAll());
        Assert.Equal(0, kit.Stage.Fanfare);
    }

    [Fact]
    public void Bouquet_of_roses_gains_energy_on_a_spend_of_ten_or_more()
    {
        var mods = new StageMods { BouquetOfRoses = 1 };
        var kit = StageKit.With(mods, 20);
        StageKit.Run(kit.Director.Spend(9));
        Assert.Equal(0, kit.Board.Energy);
        StageKit.Run(kit.Director.Spend(10));
        Assert.Equal(1, kit.Board.Energy);
        Assert.Equal(new[] { "BouquetOfRoses" }, kit.Board.Flashed);
        // A spend-all of 10 or more counts, once.
        kit = StageKit.With(mods, 15);
        StageKit.Run(kit.Director.SpendAll());
        Assert.Equal(1, kit.Board.Energy);
        // Below 10, none; without it, none.
        kit = StageKit.With(mods, 9);
        StageKit.Run(kit.Director.SpendAll());
        Assert.Equal(0, kit.Board.Energy);
        kit = StageKit.With(20);
        StageKit.Run(kit.Director.Spend(10));
        Assert.Equal(0, kit.Board.Energy);
    }

    [Fact]
    public void Epiclese_season_pass_adds_a_seat_and_the_relics_are_read_off_her()
    {
        var furina = Seat.Furina();
        Give<EpicleseSeasonPass>(furina);
        Give<FontaineTeardrop>(furina);
        Give<ClaquesLedger>(furina);
        Give<BouquetOfRoses>(furina);
        var mods = FurinaStage.ModsOf(furina.Creature);
        Assert.Equal(FurinaStageLaw.Seats + 1, mods.Capacity);
        Assert.Equal(1, mods.FontaineTeardrop);
        Assert.Equal(1, mods.ClaquesLedger);
        Assert.Equal(1, mods.BouquetOfRoses);
        Assert.Equal(FurinaStageLaw.Seats, FurinaStage.ModsOf(Seat.Furina().Creature).Capacity);
        // Four seats hold four guests; with Ensemble Cast, five.
        var kit = StageKit.With(new StageMods { Capacity = 4 }, 0,
                                StagePerformer.Wriothesley, StagePerformer.Clorinde,
                                StagePerformer.Lynette, StagePerformer.Navia);
        Assert.Equal(4, kit.Stage.Seats.Count);
        Assert.Equal(5, FurinaStageLaw.EnsembleSeats + FurinaStageLaw.SeasonPassSeats);
    }

    // ==== the potions =======================================================

    [Fact]
    public void Bottled_encore_has_each_guest_act_twice()
    {
        Assert.Contains("FurinaStage.ActEachTwice",
                        Il.Calls(Il.Method("BottledEncore", "OnUse")));
        var kit = StageKit.Of(StagePerformer.Wriothesley, StagePerformer.Clorinde);
        Assert.Equal(4, StageKit.Run(kit.Director.ActEachTwice()));
        Assert.Equal(2, kit.Beats(FurinaStageLedger.ActEvent, StagePerformer.Wriothesley));
        Assert.Equal(2, kit.Beats(FurinaStageLedger.ActEvent, StagePerformer.Clorinde));
        Assert.Equal(0, StageKit.Run(StageKit.Of().Director.ActEachTwice()));
    }

    [Fact]
    public void Water_of_lucine_repays_all_her_drained_hp()
    {
        Assert.Contains("FurinaStage.RepayAll",
                        Il.Calls(Il.Method("WaterOfLucine", "OnUse")));
        var kit = StageKit.Of();
        StageKit.Run(kit.Director.Drain(7));
        Assert.Equal(7, StageKit.Run(kit.Director.RepayAll()));
        Assert.Equal(0, kit.Stage.Drained);
    }

    // ==== helpers ============================================================

    private static T Canon<T>(Type type) where T : class =>
        (T)RuntimeHelpers.GetUninitializedObject(type);

    private static string Face(Type type) =>
        ((ILocalizationProvider)RuntimeHelpers.GetUninitializedObject(type))
            .Localization!.Single(r => r.Item1 == "description").Item2;

    private static T Give<T>(Seat seat) where T : RelicModel
    {
        var relic = (T)RuntimeHelpers.GetUninitializedObject(typeof(T));
        Seat.Set(relic, "IsMutable", true);
        Seat.Set(relic, "Owner", seat.Player);
        var relics = (List<RelicModel>)typeof(MegaCrit.Sts2.Core.Entities.Players.Player)
            .GetField("_relics", HeadlessGame.All)!.GetValue(seat.Player)!;
        relics.Add(relic);
        return relic;
    }

    private static void SetField(object target, string field, object value)
    {
        for (var t = target.GetType(); t != null; t = t.BaseType)
        {
            var f = t.GetField(field, HeadlessGame.All);
            if (f == null) continue;
            f.SetValue(target, value);
            return;
        }
        throw new InvalidOperationException($"{field} is gone");
    }
}
