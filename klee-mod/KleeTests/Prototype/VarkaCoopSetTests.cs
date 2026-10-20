#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// VARKA'S CO-OP FIVE ([USER], ruled 2026-10-13): Escort Duty, Marching
/// Orders, Windward Flank, Comrades of the Expedition and West Wind's
/// Blessing. Multiplayer only, outside his pool count, on
/// <see cref="CoopSetTwoTests"/>' terms: every pure read runs for real on a
/// headless board, and anything that awaits a command in a live combat (a
/// Swirl, an Oath gain, a Block grant) has its DOORS and ORDER pinned off the
/// compiled methods. The sim's half is <c>tier0/tests/test_coop_set.py</c>.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaCoopSetTests : IDisposable
{
    public VarkaCoopSetTests()
    {
        HeadlessGame.Arm();
        VarkaOathLedger.ResetAll();
    }

    public void Dispose()
    {
        VarkaOathLedger.ResetAll();
    }

    private static ValueProp Attack => ValueProp.Move;

    // ---- the five cards, as ruled -------------------------------------------

    public static IEnumerable<object[]> Five => new[]
    {
        Row<ProtoVkEscortDuty>(1, CardType.Skill, CardRarity.Uncommon, TargetType.Self),
        Row<ProtoVkMarchingOrders>(1, CardType.Skill, CardRarity.Uncommon, TargetType.AnyAlly),
        Row<ProtoVkWindwardFlank>(1, CardType.Skill, CardRarity.Uncommon, TargetType.AnyEnemy),
        Row<ProtoVkComradesOfTheExpedition>(2, CardType.Power, CardRarity.Rare, TargetType.Self),
        Row<ProtoVkWestWindsBlessing>(2, CardType.Power, CardRarity.Rare, TargetType.Self),
    };

    private static object[] Row<T>(int cost, CardType type, CardRarity rarity,
                                   TargetType target)
        where T : CardModel, new() =>
        new object[] { typeof(T), cost, type, rarity, target };

    [Theory]
    [MemberData(nameof(Five))]
    public void Every_card_is_multiplayer_only_at_the_ruled_cost_type_rarity_and_target(
        Type cardType, int cost, CardType type, CardRarity rarity,
        TargetType target)
    {
        var card = (CardModel)Activator.CreateInstance(cardType)!;
        Assert.Equal(CardMultiplayerConstraint.MultiplayerOnly,
                     card.MultiplayerConstraint);
        Assert.Equal(cost, card.EnergyCost.Canonical);
        Assert.Equal(type, card.Type);
        Assert.Equal(rarity, card.Rarity);
        Assert.Equal(target, card.TargetType);
    }

    [Fact]
    public void The_faces_are_the_rulings_words()
    {
        Assert.Equal(
            "Each player gains {Block:diff()} [gold]Block[/gold]. "
            + "[gold]Swirl[/gold] a random enemy with an aura.",
            Face(new ProtoVkEscortDuty()));
        Assert.Equal(
            "Choose another player. Their Attacks this turn deal additional "
            + "damage equal to your [gold]Oath[/gold] of your "
            + "[gold]current element[/gold].{InCombat:\n(+{VkOath} damage)|}",
            Face(new ProtoVkMarchingOrders()));
        Assert.Equal(
            "[gold]Swirl[/gold] the enemy. This turn, other players' Attacks "
            + "deal 50% more damage to it."
            // Varka round 5 (2026-10-13): a Swirl card's "(no aura: no Swirl)".
            + "{InCombat:{VarkaSwirl}|}",
            Face(new ProtoVkWindwardFlank()));
        Assert.Equal(
            // The power upgrade pass (2026-10-19): 1 [2] Oath.
            "Whenever another player plays an Attack, gain {PowerAmount:diff()} "
            + "[gold]Oath[/gold] of your [gold]current element[/gold].",
            Face(new ProtoVkComradesOfTheExpedition()));
        Assert.Equal(
            "The first time each turn you [gold]Swirl[/gold], each other "
            + "player gains {energyPrefix:energyIcons(1)}"
            + "{IfUpgraded:show: and draws 1 card|}.",
            Face(new ProtoVkWestWindsBlessing()));
    }

    [Fact]
    public void The_upgrades_are_the_ruled_ones()
    {
        // Escort Duty: 6 [9] ("a little low": the paper's 5 [7] went up).
        var escort = new ProtoVkEscortDuty();
        Assert.Equal(6m, escort.DynamicVars.Block.BaseValue);
        Upgrade(escort);
        Assert.Equal(9m, escort.DynamicVars.Block.BaseValue);

        // Marching Orders and Windward Flank: 1 [0]. Comrades (the power
        // upgrade pass, 2026-10-19): 2 [2], and 1 [2] Oath; was 2 [1].
        Assert.Equal(0, Upgraded<ProtoVkMarchingOrders>().EnergyCost
            .GetWithModifiers(CostModifiers.None));
        Assert.Equal(0, Upgraded<ProtoVkWindwardFlank>().EnergyCost
            .GetWithModifiers(CostModifiers.None));
        var comrades = Upgraded<ProtoVkComradesOfTheExpedition>();
        Assert.Equal(2, comrades.EnergyCost.GetWithModifiers(CostModifiers.None));
        Assert.Equal(2m, comrades.DynamicVars["PowerAmount"].BaseValue);

        // West Wind's Blessing: the cost stays 2; upgraded it also draws each
        // other player 1 card (the power upgrade pass, 2026-10-19: was
        // Innate), through WestWindsBlessingPlusPower.
        var blessing = new ProtoVkWestWindsBlessing();
        Assert.DoesNotContain(CardKeyword.Innate, blessing.Keywords);
        Upgrade(blessing);
        Assert.DoesNotContain(CardKeyword.Innate, blessing.Keywords);
        Assert.Equal(2, blessing.EnergyCost.GetWithModifiers(CostModifiers.None));
    }

    // ---- the single-player guard, and the offer -------------------------------

    [Fact]
    public void A_single_player_run_is_never_offered_one()
    {
        // REAL, through the base game's own `GetUnlockedCards`.
        var pool = (ProbePool)RuntimeHelpers.GetUninitializedObject(
            typeof(ProbePool));
        var solo = pool.GetUnlockedCards(
            null!, CardMultiplayerConstraint.SingleplayerOnly).ToList();
        Assert.Single(solo);
        Assert.IsType<ProtoVkGaleSweep>(solo[0]);
        var coop = pool.GetUnlockedCards(
            null!, CardMultiplayerConstraint.MultiplayerOnly).ToList();
        Assert.Equal(6, coop.Count);
    }

    private sealed class ProbePool : CardPoolModel
    {
        public override string Title => "probe";
        public override string EnergyColorName => "probe";
        public override string CardFrameMaterialPath => "probe";
        public override Godot.Color DeckEntryCardColor => default;
        public override bool IsColorless => true;

        protected override CardModel[] GenerateAllCards() => new CardModel[]
        {
            new ProtoVkGaleSweep(),
            new ProtoVkEscortDuty(), new ProtoVkMarchingOrders(),
            new ProtoVkWindwardFlank(), new ProtoVkComradesOfTheExpedition(),
            new ProtoVkWestWindsBlessing(),
        };
    }

    [Fact]
    public void His_roster_offers_them_in_a_multiplayer_tier_outside_the_pool()
    {
        // STRUCTURAL (the offer seams need ModelDb).
        var tier = Il.CallSequence(
            Il.Method("VarkaRoster", "MultiplayerSlice")).ToList();
        foreach (var name in new[] { "ProtoVkEscortDuty", "ProtoVkMarchingOrders",
                                     "ProtoVkWindwardFlank",
                                     "ProtoVkComradesOfTheExpedition",
                                     "ProtoVkWestWindsBlessing" })
        {
            Assert.Contains(tier, c => c.Contains(name));
            Assert.DoesNotContain(
                Il.CallSequence(Il.Method("VarkaRoster", "Pool")),
                c => c.Contains(name));
        }
        Assert.Contains("VarkaRoster.MultiplayerSlice",
            Il.Calls(Il.Method("VarkaRoster", "OfferablePool")));
    }

    // ---- Escort Duty -----------------------------------------------------------

    [Fact]
    public void Escort_duty_gives_every_other_player_the_cards_block_then_swirls_one_aura()
    {
        // His own Block is the row's `block` op, first; the kind gives the
        // others the same var through Joint Orders' call, then Swirls.
        var play = Il.CallSequence(Il.Method("ProtoVkEscortDuty", "OnPlay")).ToList();
        Assert.True(play.IndexOf("CreatureCmd.GainBlock")
                    < play.IndexOf("VarkaCards.EscortDuty"));
        var kind = Il.CallSequence(Il.Method("VarkaCards", "EscortDuty")).ToList();
        var others = kind.IndexOf("CoopSet.OtherPlayers");
        var block = kind.IndexOf("CreatureCmd.GainBlock");
        var bodies = kind.IndexOf("VarkaCards.EscortDutyBodies");
        var swirl = kind.IndexOf("ElementalHit.ApplyOnly");
        Assert.True(others >= 0 && others < block && block < bodies
                    && bodies < swirl);
    }

    [Fact]
    public void Escort_duty_swirls_only_an_enemy_with_an_aura()
    {
        var varka = Seat.Varka();
        var dry = Enemy();
        var wet = Seat.Klee(40).WithPower<HydroAuraPower>(2).Creature;
        Seat.Force(wet, "Side", CombatSide.Enemy);
        ProtoBombs.Board(varka.Creature, dry);
        Assert.Empty(VarkaCards.EscortDutyBodies(varka.Creature));
        ProtoBombs.Board(varka.Creature, dry, wet);
        Assert.Equal(new[] { wet }, VarkaCards.EscortDutyBodies(varka.Creature));
        Assert.Empty(VarkaCards.EscortDutyBodies(null));
    }

    // ---- Marching Orders --------------------------------------------------------

    [Fact]
    public void Marching_orders_reads_his_current_elements_oath()
    {
        var varka = Seat.Varka().Creature;
        Assert.Equal(0, VarkaCards.MarchingOrdersBonus(varka));    // no element
        var ledger = VarkaOathLedger.For(varka);
        ledger.Add(Element.Pyro, 4);
        ledger.Add(Element.Hydro, 2);
        Assert.Equal(0, VarkaCards.MarchingOrdersBonus(varka));    // still none
        ledger.SetCurrent(Element.Hydro);
        Assert.Equal(2, VarkaCards.MarchingOrdersBonus(varka));
        ledger.SetCurrent(Element.Pyro);
        Assert.Equal(4, VarkaCards.MarchingOrdersBonus(varka));
        Assert.Equal(0, VarkaCards.MarchingOrdersBonus(Seat.Klee().Creature));
        Assert.Equal(0, VarkaCards.MarchingOrdersBonus(null));
    }

    [Fact]
    public void Marching_orders_places_a_snapshot_on_the_chosen_player()
    {
        // The number is read once, at the play, and placed as Battle Plan's
        // power on the target, which adds it to THEIR Attacks this turn.
        var kind = Il.CallSequence(Il.Method("VarkaCards", "MarchingOrders")).ToList();
        var read = kind.IndexOf("VarkaCards.MarchingOrdersBonus");
        var apply = kind.FindIndex(c => c.StartsWith("PowerCmd.Apply"));
        Assert.True(read >= 0 && read < apply);
        Assert.Contains("VarkaCards.MarchingOrders",
            Il.Calls(Il.Method("ProtoVkMarchingOrders", "OnPlay")));

        var ally = Seat.Kokomi();
        var up = Power<AttackUpThisTurnPower>(ally.Creature, Seat.Varka().Creature, 5);
        var strike = Owned(new ProtoKkCoordinatedStrike(), ally);
        Assert.Equal(5m, up.ModifyDamageAdditive(
            Enemy(), 6m, Attack, ally.Creature, strike, null));
        // Someone else's hit: nothing.
        Assert.Equal(0m, up.ModifyDamageAdditive(
            Enemy(), 6m, Attack, Seat.Klee().Creature, strike, null));
        Assert.Contains("PowerCmd.Remove",
            Il.Calls(Il.Method("AttackUpThisTurnPower", "AfterSideTurnEnd")));
    }

    [Fact]
    public void Marching_orders_previews_the_live_number()
    {
        var card = new ProtoVkMarchingOrders();
        Assert.IsType<VarkaCurrentOathVar>(card.DynamicVars[VarkaCurrentOathVar.Token]);
        Assert.Contains("VarkaCards.MarchingOrdersBonus",
            Il.Calls(Il.Method("VarkaCurrentOathVar", "UpdateCardPreview")));
    }

    // ---- Windward Flank ----------------------------------------------------------

    [Fact]
    public void Windward_flank_is_flankings_dealer_check_at_one_and_a_half()
    {
        var varka = Seat.Varka();
        var ally = Seat.Kokomi();
        var enemy = Enemy();
        var flank = Power<WindwardFlankPower>(enemy, varka.Creature, 1);

        Assert.Equal(1.5m, flank.ModifyDamageMultiplicative(
            enemy, 10m, Attack, ally.Creature, null, null));
        // His own hit: nothing.
        Assert.Equal(1m, flank.ModifyDamageMultiplicative(
            enemy, 10m, Attack, varka.Creature, null, null));
        // Not a powered attack: nothing.
        Assert.Equal(1m, flank.ModifyDamageMultiplicative(
            enemy, 10m, ValueProp.Unpowered, ally.Creature, null, null));
        // Another enemy: nothing.
        Assert.Equal(1m, flank.ModifyDamageMultiplicative(
            Enemy(), 10m, Attack, ally.Creature, null, null));
    }

    [Fact]
    public void Windward_flank_is_one_per_varka_for_this_turn_swirled_or_not()
    {
        var flank = (WindwardFlankPower)RuntimeHelpers.GetUninitializedObject(
            typeof(WindwardFlankPower));
        Assert.Equal(PowerType.Debuff, flank.Type);
        Assert.Equal(PowerStackType.Single, flank.StackType);
        Assert.Equal(PowerInstanceType.InstancedPerApplier, flank.InstanceType);
        Assert.Equal(1.5m, WindwardFlankPower.Shred);
        Assert.Contains("PowerCmd.Remove",
            Il.Calls(Il.Method("WindwardFlankPower", "AfterSideTurnEnd")));

        // The Swirl, then the shred, unconditionally.
        var play = Il.CallSequence(Il.Method("ProtoVkWindwardFlank", "OnPlay")).ToList();
        var swirl = play.IndexOf("ElementalHit.ApplyOnly");
        var apply = play.FindIndex(c => c.StartsWith("PowerCmd.Apply"));
        Assert.True(swirl >= 0 && swirl < apply);
    }

    // ---- Comrades of the Expedition ----------------------------------------------

    [Fact]
    public void Comrades_hears_another_players_attack_and_gains_his_current_element()
    {
        var calls = Il.CallSequence(
            Il.Method("ComradesOfTheExpeditionPower", "AfterCardPlayed")).ToList();
        var who = calls.IndexOf("CoopSet.IsAnotherPlayersAttack");
        var current = calls.IndexOf("VarkaOath.Current");
        var gain = calls.IndexOf("VarkaOath.Gain");
        Assert.True(who >= 0 && who < current && current < gain);

        // The trigger, for real: an ally's Attack, not his own, not a Skill.
        var varka = Seat.Varka();
        var ally = Seat.Kokomi();
        var strike = Owned(new ProtoKkCoordinatedStrike(), ally);
        Assert.True(CoopSet.IsAnotherPlayersAttack(Play(strike, ally), varka.Creature));
        var his = Owned(new ProtoVkChargedLunge(), varka);
        Assert.False(CoopSet.IsAnotherPlayersAttack(Play(his, varka), varka.Creature));
        var skill = Owned(new ProtoKkJointOrders(), ally);
        Assert.False(CoopSet.IsAnotherPlayersAttack(Play(skill, ally), varka.Creature));
    }

    [Fact]
    public async System.Threading.Tasks.Task Comrades_with_no_current_element_gains_nothing()
    {
        var varka = Seat.Varka();
        var ally = Seat.Kokomi();
        var comrades = Power<ComradesOfTheExpeditionPower>(
            varka.Creature, varka.Creature, 1);
        var strike = Owned(new ProtoKkCoordinatedStrike(), ally);
        await comrades.AfterCardPlayed(null!, Play(strike, ally));
        Assert.Equal(0, VarkaOathLedger.For(varka.Creature).Total);
    }

    // ---- West Wind's Blessing ------------------------------------------------------

    [Fact]
    public void West_winds_blessing_rides_every_swirl_he_makes()
    {
        var swirl = Il.CallSequence(Il.Method("VarkaOath", "OnSwirl")).ToList();
        Assert.Contains("WestWindsBlessingPower.OnSwirl", swirl);
        var pay = Il.CallSequence(
            Il.Method("WestWindsBlessingPower", "OnSwirl")).ToList();
        var others = pay.IndexOf("CoopSet.OtherPlayers");
        var latch = pay.IndexOf("WestWindsBlessingPower.Take");
        var energy = pay.IndexOf("PlayerCmd.GainEnergy");
        Assert.True(others >= 0 && others < latch && latch < energy);
    }

    [Fact]
    public void West_winds_blessing_latches_once_a_round()
    {
        var blessing = Power<WestWindsBlessingPower>(
            Seat.Varka().Creature, Seat.Varka().Creature, 1);
        Assert.True(blessing.Take(1));
        Assert.False(blessing.Take(1));
        Assert.True(blessing.Take(2));
        Assert.False(blessing.Take(2));
    }

    [Fact]
    public async System.Threading.Tasks.Task West_winds_blessing_gives_energy_on_the_players_turn_only()
    {
        // Sparks for Everyone's ruling: a Swirl while the enemies act gives
        // nothing and leaves the turn's trigger; the first on the players'
        // turn pays and the second does not. REAL energy, through the base
        // game's non-interactive seam (CoopSetTwoTests' trick).
        var quiet = MegaCrit.Sts2.Core.Helpers.NonInteractiveMode.AutoSlayerCheck;
        MegaCrit.Sts2.Core.Helpers.NonInteractiveMode.AutoSlayerCheck = () => true;
        try
        {
            var varka = Seat.Varka().WithCombatState();
            var ally = Seat.Kokomi().WithCombatState();
            var enemy = Enemy();
            var combat = Table(new[] { varka.Creature, ally.Creature }, enemy);
            var blessing = Power<WestWindsBlessingPower>(
                varka.Creature, varka.Creature, 1);
            AddPower(varka.Creature, blessing);
            var energy = ally.Player.PlayerCombatState!.Energy;

            combat.CurrentSide = CombatSide.Enemy;
            Assert.False(WestWindsBlessingPower.Counts(varka.Creature));
            await WestWindsBlessingPower.OnSwirl(
                new MegaCrit.Sts2.Core.GameActions.Multiplayer.ThrowingPlayerChoiceContext(),
                varka.Creature);
            Assert.Equal(energy, ally.Player.PlayerCombatState!.Energy);

            combat.CurrentSide = CombatSide.Player;
            await WestWindsBlessingPower.OnSwirl(
                new MegaCrit.Sts2.Core.GameActions.Multiplayer.ThrowingPlayerChoiceContext(),
                varka.Creature);
            Assert.Equal(energy + 1, ally.Player.PlayerCombatState!.Energy);
            await WestWindsBlessingPower.OnSwirl(
                new MegaCrit.Sts2.Core.GameActions.Multiplayer.ThrowingPlayerChoiceContext(),
                varka.Creature);
            Assert.Equal(energy + 1, ally.Player.PlayerCombatState!.Energy);
        }
        finally
        {
            MegaCrit.Sts2.Core.Helpers.NonInteractiveMode.AutoSlayerCheck = quiet;
        }
    }

    // ---- helpers ---------------------------------------------------------------------

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Upgrade(card);
        return card;
    }

    private static void Upgrade(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
    }

    private static T Power<T>(Creature owner, Creature applier, int amount)
        where T : PowerModel
    {
        var power = (T)RuntimeHelpers.GetUninitializedObject(typeof(T));
        SetField(power, "_owner", owner);
        SetField(power, "_applier", applier);
        SetField(power, "_amount", amount);
        Seat.Set(power, "IsMutable", true);
        var init = typeof(T).GetMethod("InitInternalData", HeadlessGame.All);
        if (init?.Invoke(power, Array.Empty<object?>()) is { } data)
        {
            SetField(power, "_internalData", data);
        }
        return power;
    }

    private static void AddPower(Creature owner, PowerModel power)
    {
        for (var t = owner.GetType(); t != null; t = t.BaseType)
        {
            var f = t.GetField("_powers", HeadlessGame.All);
            if (f?.GetValue(owner) is System.Collections.IList list)
            {
                list.Add(power);
                return;
            }
        }
        throw new InvalidOperationException("_powers is gone");
    }

    private static Creature Enemy()
    {
        var body = Seat.Klee(40).Creature;
        Seat.Force(body, "Side", CombatSide.Enemy);
        return body;
    }

    private static CombatState Table(Creature[] players, params Creature[] enemies)
    {
        var combat = ProtoBombs.Board(players[0], enemies);
        var allies = (List<Creature>)typeof(CombatState)
            .GetField("_allies", HeadlessGame.All)!.GetValue(combat)!;
        allies.AddRange(players);
        foreach (var p in players) p.CombatState = combat;
        return combat;
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

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;
}
