#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Potions;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using SilentRelics = MegaCrit.Sts2.Core.Models.Relics;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// VARKA'S OWN RELICS AND POTIONS (<c>review/active/varka-expansion-2026-10-01.md</c>
/// sec.4, built at the paper's defaults). On <c>ArmRelicsPotionsTests</c>'
/// terms: every decision (a count, a gate, a move, a read) runs on a headless
/// board or the pure Oath ledger; what awaits a command that needs a live
/// combat (Block, a hit, a pile move, a grid) is pinned by its doors.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaRelicsPotionsTests : IDisposable
{
    public VarkaRelicsPotionsTests()
    {
        HeadlessGame.Arm();
        VarkaOathLedger.ResetAll();
    }

    public void Dispose()
    {
        VarkaOathLedger.ResetAll();
    }

    // ==== the shape ==========================================================

    [Fact]
    public void Seven_relics_in_the_base_games_shape_and_three_potions()
    {
        var rarities = VarkaArmRelics.Types
            .Select(t => Canon<RelicModel>(t).Rarity).ToList();
        Assert.Equal(7, rarities.Count);
        Assert.Equal(1, rarities.Count(r => r == RelicRarity.Common));
        Assert.Equal(2, rarities.Count(r => r == RelicRarity.Uncommon));
        Assert.Equal(3, rarities.Count(r => r == RelicRarity.Rare));
        Assert.Equal(1, rarities.Count(r => r == RelicRarity.Shop));
        Assert.Equal(RelicRarity.Common, Canon<RelicModel>(typeof(KnightsCommission)).Rarity);
        Assert.Equal(RelicRarity.Shop, Canon<RelicModel>(typeof(FavoniusDutyRoster)).Rarity);

        var potions = VarkaPotions.Types.Select(t => Canon<PotionModel>(t)).ToList();
        Assert.Equal(
            new[] { PotionRarity.Common, PotionRarity.Uncommon, PotionRarity.Rare },
            potions.Select(p => p.Rarity).ToArray());
        Assert.All(potions, p => Assert.Equal(PotionUsage.CombatOnly, p.Usage));
        Assert.All(potions, p => Assert.Equal(TargetType.AnyPlayer, p.TargetType));
    }

    [Fact]
    public void Every_relic_and_potion_has_a_title_and_a_plain_face()
    {
        var titles = new List<string>();
        foreach (var type in VarkaArmRelics.Types.Concat(VarkaPotions.Types))
        {
            var loc = ((ILocalizationProvider)Canon<AbstractModel>(type)).Localization!;
            Assert.Equal(new[] { "title", "description" },
                         loc.Select(r => r.Item1).ToArray());
            var face = loc[1].Item2;
            Assert.DoesNotContain("{", face);
            // Measured as read, without the colour tags.
            var plain = System.Text.RegularExpressions.Regex.Replace(face, @"\[/?\w+\]", "");
            Assert.True(plain.Length < 140, $"{loc[0].Item2}: {plain}");
            titles.Add(loc[0].Item2);
        }
        Assert.Equal(new[]
        {
            "Knight's Commission", "Windblume Garland", "Dandelion Seeds",
            "Banner of the West Wind", "Stormterror's Scale", "Andrius's Howl",
            "Favonius Duty Roster", "Bottled Resolve", "Bottled Gale",
            "Elixir of the Four Winds",
        }, titles);
    }

    [Fact]
    public void Pick_one_ships_at_its_default_the_borrow_goes()
    {
        Assert.False(VarkaArmRelics.KeepSilentBorrow);
        Assert.Equal(
            new[] { typeof(BoreasFang) }.Concat(VarkaArmRelics.Types)
                .Append(typeof(WolfsGravestone)),
            ArmRelicPools.VarkaArmPool);
    }

    [Fact]
    public void The_potion_pool_is_his_three()
    {
        var pool = Il.CallSequence(Il.Method("VarkaPotionPool", "GenerateAllPotions"));
        Assert.Equal(VarkaPotions.Types.Select(t => $"ModelDb.Potion<{t.Name}>").ToArray(),
                     pool.Where(c => c.StartsWith("ModelDb.Potion<")).ToArray());
        var potions = (VarkaPotionPool)RuntimeHelpers.GetUninitializedObject(typeof(VarkaPotionPool));
        SetField(potions, "_allPotions", VarkaPotions.Types.Select(t => Canon<PotionModel>(t)).ToList());
        Assert.Equal(VarkaPotions.Types, potions.GetUnlockedPotions(null!).Select(p => p.GetType()));
    }

    // ==== the relics =========================================================

    [Fact]
    public void Knights_commission_reads_the_element_the_run_rolled_all_run()
    {
        // Main session, 2026-10-01: the element the Fang rolled, even after
        // the card is removed or transformed.
        Assert.Equal(Element.Electro, KnightsCommission.StartingElement(
            Element.Electro, new CardModel[] { new StrikeSilent() }));
        Assert.Equal(Element.Electro, KnightsCommission.StartingElement(
            Element.Electro, Array.Empty<CardModel>()));
        Assert.Equal(Element.Hydro, KnightsCommission.StartingElement(
            Element.Hydro, new CardModel[] { new ProtoVkAmberFieryRain() }));
        // A run begun before the record existed: the starter Knight in the
        // deck, never a pool Knight.
        Assert.Equal(Element.Electro, KnightsCommission.StartingElement(Element.None,
            new CardModel[] { new StrikeSilent(), new ProtoVkLisaLightningRose() }));
        Assert.Equal(Element.None, KnightsCommission.StartingElement(Element.None,
            new CardModel[] { new ProtoVkKaeyaFrostgnaw(), new StrikeSilent() }));

        // The record: written on the Fang at the roll, read back, carried to
        // Wolf's Gravestone at Touch of Orobas.
        var fang = (BoreasFang)RuntimeHelpers.GetUninitializedObject(typeof(BoreasFang));
        Assert.Equal(Element.None, VarkaStarterKnight.Of(fang));
        VarkaStarterKnight.Record(fang, Element.Cryo);
        Assert.Equal(Element.Cryo, VarkaStarterKnight.Of(fang));
        Assert.Contains("VarkaStarterKnight.Record",
                        Il.Calls(Il.Method("BoreasFang", "AfterObtained")));
        var upgrade = Il.CallSequence(Il.Method("BoreasFang", "GetUpgradeReplacement"));
        Assert.Contains("VarkaStarterKnight.Of", upgrade);
        Assert.Contains("VarkaStarterKnight.Record", upgrade);
        Assert.Contains("VarkaStarterKnight.Of",
                        Il.Calls(Il.Method("KnightsCommission", "AfterPlayerTurnStart")));
        // Re-aimed (main session, 2026-10-01): the Fang sets the element, so
        // the Commission sets none; it gains 2 Oath through the one door (so
        // the Fang answers it on turn one).
        var calls = Il.CallSequence(Il.Method("KnightsCommission", "AfterPlayerTurnStart")).ToList();
        Assert.DoesNotContain("VarkaOath.SetCurrent", calls);
        Assert.Contains("VarkaOath.Gain", calls);
        Assert.Equal(2, KnightsCommission.Oath);
    }

    [Fact]
    public void A_change_carries_the_banner_first_then_the_garland_then_boreas_unbound()
    {
        var set = Il.CallSequence(Il.Method("VarkaOath", "SetCurrent")).ToList();
        Assert.True(set.IndexOf("VarkaOathLedger.SetCurrent")
                    < set.IndexOf("VarkaArmRelics.OnElementChanged"));
        Assert.True(set.IndexOf("VarkaArmRelics.OnElementChanged")
                    < set.IndexOf("BoreasUnboundPower.OnElementChanged"));
        var changed = Il.CallSequence(Il.Method("VarkaArmRelics", "OnElementChanged")).ToList();
        Assert.True(changed.IndexOf("BannerOfTheWestWind.Carry")
                    < changed.IndexOf("WindblumeGarland.BlockFor"));
        Assert.Contains("CreatureCmd.GainBlock", changed);
    }

    [Fact]
    public void His_pool_lists_his_seven_and_offers_them_without_the_borrow()
    {
        var members = Il.CallSequence(Il.Method("VarkaRelicPool", "GenerateAllRelics"));
        foreach (var t in VarkaArmRelics.Types.Append(typeof(BoreasFang))
                     .Append(typeof(WolfsGravestone)))
        {
            Assert.Contains($"ModelDb.Relic<{t.Name}>", members);
        }

        var pool = (VarkaRelicPool)RuntimeHelpers.GetUninitializedObject(typeof(VarkaRelicPool));
        SetField(pool, "_relics", Silent().Append(typeof(BoreasFang))
            .Append(typeof(WolfsGravestone)).Concat(VarkaArmRelics.Types)
            .Select(t => (RelicModel)RuntimeHelpers.GetUninitializedObject(t)).ToList());
        var offer = pool.GetUnlockedRelics(null!).Select(r => r.GetType()).ToList();
        Assert.Equal(ArmRelicPools.VarkaArmPool.OrderBy(t => t.Name),
                     offer.OrderBy(t => t.Name));
        Assert.DoesNotContain(offer, t => t.Assembly != typeof(VarkaRelicPool).Assembly);
    }

    [Fact]
    public void His_potion_pool_is_his_own()
    {
        var calls = Il.CallSequence(typeof(Varka).GetProperty("PotionPool")!.GetGetMethod()!);
        Assert.Contains("ModelDb.PotionPool<VarkaPotionPool>", calls);
        Assert.DoesNotContain("ModelDb.PotionPool<SilentPotionPool>", calls);
    }

    [Fact]
    public void Windblume_garland_pays_four_block_a_copy_and_nothing_for_anyone_else()
    {
        var varka = Seat.Varka();
        Assert.Equal(0, WindblumeGarland.BlockFor(varka.Creature));
        Give<WindblumeGarland>(varka);
        Assert.Equal(4, WindblumeGarland.BlockFor(varka.Creature));
        Give<WindblumeGarland>(varka);
        Assert.Equal(8, WindblumeGarland.BlockFor(varka.Creature));
        // Held by anyone else it does nothing.
        var klee = Seat.Klee();
        Give<WindblumeGarland>(klee);
        Assert.Equal(0, WindblumeGarland.BlockFor(klee.Creature));
    }

    [Fact]
    public void Banner_of_the_west_wind_moves_the_old_elements_oath_to_the_new()
    {
        var varka = Seat.Varka();
        var ledger = VarkaOathLedger.For(varka.Creature);
        ledger.Add(Element.Pyro, 4);
        ledger.Add(Element.Hydro, 1);
        Assert.Equal(0, BannerOfTheWestWind.Carry(varka.Creature, Element.Pyro, Element.Hydro));
        Assert.Equal(4, ledger.Oath(Element.Pyro));

        Give<BannerOfTheWestWind>(varka);
        Assert.Equal(4, BannerOfTheWestWind.Carry(varka.Creature, Element.Pyro, Element.Hydro));
        Assert.Equal(0, ledger.Oath(Element.Pyro));
        Assert.Equal(5, ledger.Oath(Element.Hydro));
        Assert.Equal(5, ledger.Total);
        // The first element of a fight has no old one to carry.
        Assert.Equal(0, BannerOfTheWestWind.Carry(varka.Creature, Element.None, Element.Cryo));
        Assert.Equal(5, ledger.Oath(Element.Hydro));
    }

    [Fact]
    public void Stormterrors_scale_makes_a_swirl_pay_twice()
    {
        var varka = Seat.Varka();
        Assert.Equal(1, StormterrorsScale.PayoutsFor(varka.Creature));
        Give<StormterrorsScale>(varka);
        Assert.Equal(2, StormterrorsScale.PayoutsFor(varka.Creature));
        // The payout loop reads it after the credit; the credit runs once.
        var swirl = Il.CallSequence(Il.Method("VarkaOath", "OnSwirl")).ToList();
        Assert.True(swirl.IndexOf("VarkaOathLedger.TryCredit")
                    < swirl.IndexOf("StormterrorsScale.TakePayouts"));
        Assert.Single(swirl, c => c == "VarkaOathLedger.TryCredit");
    }

    [Fact]
    public void A_relic_or_potion_credits_no_oath_and_switches_nothing()
    {
        var varka = Seat.Varka().Creature;
        var ledger = VarkaOathLedger.For(varka);
        using (VarkaOath.NoCredit(varka))
        {
            Assert.False(ledger.TryCredit(swirl: false, Element.Pyro));
            Assert.False(ledger.TryCredit(swirl: true, Element.Pyro));
            ledger.OpenScope(open: true);
            Assert.False(ledger.OpenOathSwitches(Element.Pyro));
            ledger.CloseScope();
        }
        Assert.True(ledger.TryCredit(swirl: false, Element.Pyro));
        Assert.True(ledger.TryCredit(swirl: true, Element.Pyro));

        // Dandelion Seeds and Bottled Gale run inside it.
        foreach (var (type, method) in new[] { ("DandelionSeeds", "AfterPlayerTurnStartLate"),
                                               ("BottledGale", "OnUse") })
        {
            var calls = Il.CallSequence(Il.Method(type, method)).ToList();
            Assert.Contains("VarkaOath.NoCredit", calls);
        }
        Assert.Contains("ElementalHit.ApplyOnly",
                        Il.Calls(Il.Method("DandelionSeeds", "AfterPlayerTurnStartLate")));
        Assert.Contains("VarkaRules.SwirlFreshAuras",
                        Il.Calls(Il.Method("BottledGale", "OnUse")));
    }

    [Fact]
    public void Dandelion_seeds_fires_only_when_no_enemy_wears_an_aura()
    {
        var bare = Enemy();
        var other = Enemy();
        Assert.True(DandelionSeeds.Fires(Element.Hydro, new[] { bare, other }));
        Assert.False(DandelionSeeds.Fires(Element.None, new[] { bare, other }));
        var aura = Seat.Klee(40).WithPower<PyroAuraPower>(2).Creature;
        Seat.Force(aura, "Side", CombatSide.Enemy);
        Assert.False(DandelionSeeds.Fires(Element.Hydro, new[] { bare, aura }));
    }

    [Fact]
    public async Task Andriuss_howl_notes_each_ascension_he_plays()
    {
        var varka = Seat.Varka();
        var howl = Give<AndriussHowl>(varka);
        var ascension = Owned(new ProtoVkFourWindsAscension(), varka);
        var strike = Owned(new StrikeSilent(), varka);
        await howl.AfterCardPlayed(null!, Play(strike, varka));
        Assert.Empty(howl.Waiting);
        await howl.AfterCardPlayed(null!, Play(ascension, varka));
        await howl.AfterCardPlayed(null!, Play(ascension, varka));
        Assert.Single(howl.Waiting);                 // once per copy
        // Another player's Ascension is not his.
        var other = Seat.Varka();
        await howl.AfterCardPlayed(null!, Play(Owned(new ProtoVkFourWindsAscension(), other), other));
        Assert.Single(howl.Waiting);
        // The turn start puts the noted copies back in hand, then forgets them.
        var start = Il.CallSequence(Il.Method("AndriussHowl", "AfterPlayerTurnStart")).ToList();
        Assert.Contains("CardPileCmd.Add", start);
    }

    [Fact]
    public void Favonius_duty_roster_is_roll_calls_unchosen_add_on_turn_one()
    {
        var calls = Il.CallSequence(Il.Method("FavoniusDutyRoster", "AfterPlayerTurnStart"));
        Assert.Contains("VarkaArmRelics.FirstTurnOf", calls);
        Assert.Contains("VarkaRules.AddKnight", calls);
        // Roll Call's pool (never a starter-only Knight), free this turn.
        Assert.Contains("VarkaRules.PoolKnights",
                        Il.Calls(Il.Method("VarkaRules", "AddKnight")));
        Assert.Contains("CardEnergyCost.SetThisTurn",
                        Il.Calls(Il.Method("VarkaRules", "AddKnight")));

        var varka = Seat.Varka().WithCombatState();
        var roster = Give<FavoniusDutyRoster>(varka);
        Assert.True(VarkaArmRelics.FirstTurnOf(roster, varka.Player));
        varka.Player.PlayerCombatState!.IncrementTurnNumber();
        Assert.False(VarkaArmRelics.FirstTurnOf(roster, varka.Player));
    }

    // ==== the potions ========================================================

    [Fact]
    public void Bottled_resolve_chooses_any_of_the_four_sets_it_and_gains_three()
    {
        Assert.Equal(3, BottledResolve.Oath);
        var use = Il.CallSequence(Il.Method("BottledResolve", "Use")).ToList();
        Assert.True(use.IndexOf("VarkaOath.SetCurrent") < use.IndexOf("VarkaOath.Gain"));
        var onUse = Il.Calls(Il.Method("BottledResolve", "OnUse"));
        Assert.Contains("VarkaRules.ChooseElement", onUse);
    }

    [Fact]
    public void Elixir_of_the_four_winds_reads_all_four_this_turn_only()
    {
        var varka = Seat.Varka().Creature;
        var ledger = VarkaOathLedger.For(varka);
        ledger.Add(Element.Hydro, 3);
        ledger.Add(Element.Pyro, 2);
        ledger.Add(Element.Cryo, 1);
        ledger.SetCurrent(Element.Hydro);
        Assert.Equal(3, VarkaOath.CurrentOath(varka));

        Assert.True(ElixirOfTheFourWinds.Use(varka));
        Assert.Equal(6, VarkaOath.CurrentOath(varka));
        Assert.True(ledger.AllFourThisTurn);
        // Nothing moved: the four counts stand.
        Assert.Equal(3, ledger.Oath(Element.Hydro));

        // The next round ends it.
        ledger.RollTo(RoundOf(ledger) + 1);
        Assert.False(ledger.AllFourThisTurn);
        Assert.Equal(3, ledger.CurrentOath);

        // Anyone else: nothing.
        Assert.False(ElixirOfTheFourWinds.Use(Seat.Klee().Creature));
    }

    // ==== the ledger =========================================================

    [Fact]
    public void Move_oath_moves_every_point_and_gains_nothing()
    {
        var ledger = VarkaOathLedger.For(Seat.Klee().Creature);
        ledger.Add(Element.Electro, 3);
        Assert.Equal(3, ledger.MoveOath(Element.Electro, Element.Cryo));
        Assert.Equal(0, ledger.Oath(Element.Electro));
        Assert.Equal(3, ledger.Oath(Element.Cryo));
        Assert.Equal(0, ledger.MoveOath(Element.Cryo, Element.Cryo));
        Assert.Equal(0, ledger.MoveOath(Element.None, Element.Cryo));
        Assert.Equal(0, ledger.MoveOath(Element.Anemo, Element.Cryo));
        Assert.Equal(3, ledger.Total);
    }

    // ==== helpers ============================================================

    private static int RoundOf(VarkaOathLedger ledger) =>
        (int)typeof(VarkaOathLedger).GetField("_round", HeadlessGame.All)!.GetValue(ledger)!;

    private static T Canon<T>(Type type) where T : class =>
        (T)RuntimeHelpers.GetUninitializedObject(type);

    private static IEnumerable<Type> Silent() => new[]
    {
        typeof(SilentRelics.NinjaScroll), typeof(SilentRelics.PaperKrane),
        typeof(SilentRelics.RingOfTheSnake), typeof(SilentRelics.Tingsha),
        typeof(SilentRelics.ToughBandages), typeof(SilentRelics.TwistedFunnel),
    };

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

    private static Creature Enemy()
    {
        var body = Seat.Klee(40).Creature;
        Seat.Force(body, "Side", CombatSide.Enemy);
        return body;
    }

    private static T Owned<T>(T card, Seat owner) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", owner.Player);
        return card;
    }

    private static CardPlay Play(CardModel card, Seat by) => new()
    {
        Card = card,
        Player = by.Player,
        Target = null,
        ResultPile = PileType.Discard,
        Resources = default,
        IsAutoPlay = false,
        PlayIndex = 0,
        PlayCount = 1,
    };

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
