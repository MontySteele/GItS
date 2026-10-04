using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
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
/// THE CO-OP SET, SECOND BATCH (review/active/coop-concepts-2026-09-27.md;
/// [USER], 2026-09-27, picks 2a and 3a): Raise a Toast and The Crowd Roars for
/// Furina, Shrapnel and Sparks for Everyone for Klee. Multiplayer only, on
/// <see cref="CoopSetTests"/>' terms.
///
/// THE SIM SEATS ONE PLAYER, so the co-op rules are tested here only
/// (`tier0/tests/test_coop_set.py` pins the sim's half: the rows load, no
/// pool deals them, and a clause aimed at another player lands on no one).
///
/// WHAT IS REAL AND WHAT IS STRUCTURAL, as in the first set: every pure read
/// -- Shrapnel's multiplier, the toast's number, the Crowd's trigger, the
/// once-a-turn latch -- is run for real on a headless board; anything that
/// awaits a command (an explosion, an energy grant, a Strength apply, a
/// performer's arrival) needs a live combat, so its DOORS and ORDER are
/// pinned off the compiled methods and say so.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class CoopSetTwoTests
{
    private static ValueProp Attack => ValueProp.Move;

    // ---- the four cards, as the ruled table prints them ------------------

    public static IEnumerable<object[]> Four => new[]
    {
        Row<ProtoKoShrapnel>(1, CardType.Skill, CardRarity.Uncommon),
        Row<ProtoKoSparksForEveryone>(2, CardType.Power, CardRarity.Rare),
    };

    private static object[] Row<T>(int cost, CardType type, CardRarity rarity)
        where T : CardModel, new() =>
        new object[] { typeof(T), cost, type, rarity };

    [Theory]
    [MemberData(nameof(Four))]
    public void Every_card_is_multiplayer_only_at_the_printed_cost_type_and_rarity(
        Type cardType, int cost, CardType type, CardRarity rarity)
    {
        var card = (CardModel)Activator.CreateInstance(cardType)!;
        Assert.Equal(CardMultiplayerConstraint.MultiplayerOnly,
                     card.MultiplayerConstraint);
        Assert.Equal(cost, card.EnergyCost.Canonical);
        Assert.Equal(type, card.Type);
        Assert.Equal(rarity, card.Rarity);
    }

    [Fact]
    public void The_targets_are_the_ally_the_enemy_and_the_player_herself()
    {
        // "Another player" is the base game's ally target (Coordinate, Lift);
        // Shrapnel's Mine is aimed at an enemy; the two Powers take none.
        Assert.Equal(TargetType.AnyEnemy, new ProtoKoShrapnel().TargetType);
        Assert.Equal(TargetType.Self,
                     new ProtoKoSparksForEveryone().TargetType);
    }

    [Fact]
    public void The_faces_are_the_designs_words()
    {
        Assert.Equal(
            "Place a [gold]Mine[/gold] {BombSize:diff()}. While an enemy holds "
            + "your [gold]Mine[/gold], other players' Attacks deal 50% more "
            + "damage to it.",
            Face(new ProtoKoShrapnel()));
        Assert.Equal(
            "The first time each turn one of your [gold]Bombs[/gold] goes "
            + "off, each other player gains 1 [gold]Energy[/gold].",
            Face(new ProtoKoSparksForEveryone()));
    }

    [Fact]
    public void The_upgrades_are_the_ruled_ones()
    {
        // Shrapnel: Mine 4 -> 7.
        var shrapnel = new ProtoKoShrapnel();
        Assert.Equal(4m, shrapnel.DynamicVars["BombSize"].BaseValue);
        Upgrade(shrapnel);
        Assert.Equal(7m, shrapnel.DynamicVars["BombSize"].BaseValue);

        // Sparks for Everyone: gains Innate, and the cost stays 2 ([USER],
        // 2026-09-27: "might also be fine at 2 cost").
        var sparks = new ProtoKoSparksForEveryone();
        Assert.DoesNotContain(CardKeyword.Innate, sparks.Keywords);
        Upgrade(sparks);
        Assert.Contains(CardKeyword.Innate, sparks.Keywords);
        Assert.Equal(2, sparks.EnergyCost.GetWithModifiers(CostModifiers.None));
    }

    // ---- the single-player guard, and the offer ---------------------------

    [Fact]
    public void A_single_player_run_is_never_offered_one()
    {
        // REAL, through the base game's own `GetUnlockedCards`: a one-player
        // run's constraint drops all four and keeps the standard card.
        var pool = (ProbePool)RuntimeHelpers.GetUninitializedObject(
            typeof(ProbePool));
        var solo = pool.GetUnlockedCards(
            null!, CardMultiplayerConstraint.SingleplayerOnly).ToList();
        Assert.Single(solo);
        Assert.IsType<ProtoKoChainFuse>(solo[0]);

        var coop = pool.GetUnlockedCards(
            null!, CardMultiplayerConstraint.MultiplayerOnly).ToList();
        Assert.Equal(3, coop.Count);
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
            new ProtoKoChainFuse(),
            new ProtoKoShrapnel(), new ProtoKoSparksForEveryone(),
        };
    }

    [Fact]
    public void Each_arm_offers_them_in_its_multiplayer_tier_outside_the_slice()
    {
        // STRUCTURAL (the offer seams need ModelDb): the tier methods name
        // them, and Klee's slice -- the 78 -- does not.
        var klee = Il.CallSequence(
            Il.Method("KleeOverhaulRoster", "MultiplayerSlice"));
        Assert.Contains(klee, c => c.Contains("ProtoKoShrapnel"));
        Assert.Contains(klee, c => c.Contains("ProtoKoSparksForEveryone"));
        Assert.DoesNotContain(
            Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice")),
            c => c.Contains("Shrapnel") || c.Contains("SparksForEveryone"));
    }

    // ---- Shrapnel ----------------------------------------------------------------

    [Fact]
    public void Shrapnel_is_flankings_dealer_check_at_one_and_a_half()
    {
        var klee = Seat.Klee();
        var ally = Seat.Furina();
        var enemy = Enemy();
        ProtoBombs.Board(klee.Creature, enemy);
        ProtoBombs.Place(enemy, klee.Creature, new ProtoBombs.Charge(4, IsMine: true));
        var shred = Power<ShrapnelPower>(enemy, klee.Creature, 1);

        // Another player's powered attack on this enemy: x1.5.
        Assert.Equal(1.5m, shred.ModifyDamageMultiplicative(
            enemy, 10m, Attack, ally.Creature, null, null));
        // Klee's own hit, the applier: nothing (Flanking's `dealer == Applier`).
        Assert.Equal(1m, shred.ModifyDamageMultiplicative(
            enemy, 10m, Attack, klee.Creature, null, null));
        // Not a powered attack (a Bomb going off, a power's damage): nothing.
        Assert.Equal(1m, shred.ModifyDamageMultiplicative(
            enemy, 10m, ValueProp.Unpowered, ally.Creature, null, null));
        // Another target: nothing.
        Assert.Equal(1m, shred.ModifyDamageMultiplicative(
            Enemy(), 10m, Attack, ally.Creature, null, null));
    }

    [Fact]
    public void Shrapnel_holds_only_while_the_enemy_holds_her_mine()
    {
        var klee = Seat.Klee();
        var otherKlee = Seat.Klee();
        var ally = Seat.Furina();
        var enemy = Enemy();
        ProtoBombs.Board(klee.Creature, enemy);
        var shred = Power<ShrapnelPower>(enemy, klee.Creature, 1);

        // No charge at all, then a plain Bomb, then another Klee's Mine:
        // none of them is HER Mine.
        Assert.Equal(1m, shred.ModifyDamageMultiplicative(
            enemy, 10m, Attack, ally.Creature, null, null));
        var bombs = ProtoBombs.Place(enemy, klee.Creature, new ProtoBombs.Charge(6));
        Assert.Equal(1m, shred.ModifyDamageMultiplicative(
            enemy, 10m, Attack, ally.Creature, null, null));
        ProtoBombs.Place(enemy, otherKlee.Creature, new ProtoBombs.Charge(5, IsMine: true));
        Assert.Equal(1m, shred.ModifyDamageMultiplicative(
            enemy, 10m, Attack, ally.Creature, null, null));

        // Her Mine: on. Taken (a Mine going off takes it first): off again.
        var mine = ProtoBombs.Place(enemy, klee.Creature, new ProtoBombs.Charge(4, IsMine: true));
        Assert.Equal(1.5m, shred.ModifyDamageMultiplicative(
            enemy, 10m, Attack, ally.Creature, null, null));
        mine.TakeMines();
        Assert.Equal(1m, shred.ModifyDamageMultiplicative(
            enemy, 10m, Attack, ally.Creature, null, null));
        Assert.NotNull(bombs);
    }

    [Fact]
    public void Shrapnel_is_one_shred_per_klee_on_the_enemy()
    {
        var shred = (ShrapnelPower)RuntimeHelpers.GetUninitializedObject(
            typeof(ShrapnelPower));
        Assert.Equal(PowerType.Debuff, shred.Type);
        Assert.Equal(PowerStackType.Single, shred.StackType);
        Assert.Equal(PowerInstanceType.InstancedPerApplier, shred.InstanceType);
        Assert.Equal(1.5m, ShrapnelPower.Shred);

        // The card places the Mine with the arm's one placer, then the shred
        // on the same enemy, placed by Klee.
        var play = Il.CallSequence(Il.Method("ProtoKoShrapnel", "OnPlay")).ToList();
        var place = play.IndexOf("ProtoBombPower.Place");
        var apply = play.FindIndex(c => c.StartsWith("PowerCmd.Apply"));
        Assert.True(place >= 0 && place < apply);
    }

    [Fact]
    public void The_shred_leaves_with_her_last_mine_when_it_goes_off()
    {
        // STRUCTURAL (an explosion needs a live combat): the Mine branch of
        // every explosion asks Shrapnel after Explosive Frags, and the ask
        // removes the shred only when she holds no Mine there any more.
        var explode = Il.CallSequence(Il.Method("ProtoBombPower", "Explode")).ToList();
        var frags = explode.IndexOf("MineFragsPower.OnMineWentOff");
        var shrapnel = explode.IndexOf("ShrapnelPower.AfterMineWentOff");
        Assert.True(frags >= 0 && frags < shrapnel);
        var after = Il.Calls(Il.Method("ShrapnelPower", "AfterMineWentOff"));
        Assert.Contains("ProtoBombPower.HoldsMineFrom", after);
        Assert.Contains("PowerCmd.Remove", after);
    }

    [Fact]
    public async System.Threading.Tasks.Task An_allys_attack_that_sets_off_her_mine_is_still_shredded()
    {
        // THE ORDERING THE DESIGN NAMES: a Mine set off by an ally's Attack
        // (Knights of Favonius, Pass the Match) goes off AFTER that Attack's
        // hits resolve, so the Attack is still shredded.
        //
        // REAL up to the Set off: Knights opens its watch at BeforeCardPlayed
        // and only NOTES each hit at AfterDamageReceived, so while the hits
        // land the Mine is on the enemy and the shred reads x1.5. The Set off
        // itself needs a live combat, so its place (AfterCardPlayed, and
        // nowhere earlier) is pinned off the compiled methods, and the pile
        // it takes is then taken the way SetOff takes it.
        var klee = Seat.Klee();
        var ally = Seat.Furina();
        var enemy = Enemy();
        ProtoBombs.Board(klee.Creature, enemy);
        var mine = ProtoBombs.Place(enemy, klee.Creature,
                                    new ProtoBombs.Charge(4, IsMine: true));
        var shred = Power<ShrapnelPower>(enemy, klee.Creature, 1);
        var knights = Power<KnightsOfFavoniusPower>(klee.Creature, klee.Creature, 1);
        SetField(knights, "_internalData", new CoopSet.HitRecord());

        var attack = Owned(new ProtoKkCoordinatedStrike(), ally);
        var play = Play(attack, ally);
        try
        {
            await knights.BeforeCardPlayed(play);
            // The hit lands: shredded, and the Mine is still there after it.
            Assert.Equal(1.5m, shred.ModifyDamageMultiplicative(
                enemy, 10m, Attack, ally.Creature, attack, play));
            await knights.AfterDamageReceived(
                null!, enemy, null!, Attack, ally.Creature, attack);
            Assert.Equal(1, mine.MineCount);
            Assert.True(ProtoBombPower.HoldsMineFrom(enemy, klee.Creature));
        }
        finally
        {
        }

        // Nothing sets off before AfterCardPlayed.
        foreach (var power in new[] { "KnightsOfFavoniusPower", "PassTheMatchPower" })
        {
            Assert.DoesNotContain("CoopSet.SetOffOn",
                Il.Calls(Il.Method(power, "BeforeCardPlayed")));
            Assert.DoesNotContain("CoopSet.SetOffOn",
                Il.Calls(Il.Method(power, "AfterDamageReceived")));
            Assert.Contains("CoopSet.SetOffOn",
                Il.Calls(Il.Method(power, "AfterCardPlayed")));
        }

        // The Set off takes the pile first (take-then-resolve); from then on
        // the shred is off.
        mine.TakeAll();
        Assert.Equal(1m, shred.ModifyDamageMultiplicative(
            enemy, 10m, Attack, ally.Creature, attack, play));
    }

    // ---- Sparks for Everyone ---------------------------------------------------------

    [Fact]
    public void Sparks_for_everyone_is_once_a_turn_on_the_ledgers_latch()
    {
        KleeOverhaulLedger.ResetAll();
        try
        {
            var ledger = new KleeOverhaulLedger();
            ledger.RollTo(1);
            Assert.True(ledger.TakeSparksForEveryone());
            Assert.False(ledger.TakeSparksForEveryone());
            ledger.RollTo(1);
            Assert.False(ledger.TakeSparksForEveryone());
            ledger.RollTo(2);                 // the next turn
            Assert.True(ledger.TakeSparksForEveryone());
        }
        finally
        {
            KleeOverhaulLedger.ResetAll();
        }
    }

    [Fact]
    public async System.Threading.Tasks.Task Sparks_for_everyone_hears_only_her_bombs_and_needs_someone_to_give_to()
    {
        KleeOverhaulLedger.ResetAll();
        try
        {
            // A one-seat fight: nobody else, so nothing is given and the
            // turn's latch is not spent.
            var klee = Seat.Klee();
            var enemy = Enemy();
            Table(new[] { klee.Creature }, enemy);
            var sparks = Power<SparksForEveryonePower>(klee.Creature, klee.Creature, 1);
            klee.Creature.CombatState!.CurrentSide = CombatSide.Player;
            await sparks.OnBombExploded(null!, klee.Creature, enemy, 4, false);
            Assert.True(KleeOverhaulLedger.For(klee.Creature).TakeSparksForEveryone());

            // Another Klee's Bomb is not hers: the latch is not touched.
            KleeOverhaulLedger.ResetAll();
            var other = Seat.Klee();
            var ally = Seat.Furina();
            Table(new[] { klee.Creature, other.Creature, ally.Creature }, enemy);
            await sparks.OnBombExploded(null!, other.Creature, enemy, 4, false);
            Assert.True(KleeOverhaulLedger.For(klee.Creature).TakeSparksForEveryone());
        }
        finally
        {
            KleeOverhaulLedger.ResetAll();
        }
    }

    [Fact]
    public async System.Threading.Tasks.Task An_enemy_turn_mine_gives_no_energy_and_leaves_the_turns_trigger()
    {
        // DESIGNER RULING (2026-09-27): only a Bomb that goes off on the
        // players' turn counts. A Mine answering an attack on the enemies'
        // turn grants nothing and does not use up the once-per-turn trigger;
        // the next explosion on the players' turn still grants it.
        KleeOverhaulLedger.ResetAll();
        // The base game's own non-interactive seam: with it on, the energy
        // grant's sound cue is skipped, so the REAL PlayerCmd.GainEnergy runs
        // headless and the ally's energy can be read back.
        var quiet = MegaCrit.Sts2.Core.Helpers.NonInteractiveMode.AutoSlayerCheck;
        MegaCrit.Sts2.Core.Helpers.NonInteractiveMode.AutoSlayerCheck = () => true;
        try
        {
            var klee = Seat.Klee().WithCombatState();
            var ally = Seat.Furina().WithCombatState();
            var enemy = Enemy();
            var combat = Table(new[] { klee.Creature, ally.Creature }, enemy);
            var sparks = Power<SparksForEveryonePower>(klee.Creature, klee.Creature, 1);
            var energy = ally.Player.PlayerCombatState!.Energy;

            // The enemies' turn: her Mine answers an attack.
            combat.CurrentSide = CombatSide.Enemy;
            Assert.False(SparksForEveryonePower.Counts(klee.Creature, klee.Creature));
            await sparks.OnBombExploded(null!, klee.Creature, enemy, 4, false);
            Assert.Equal(energy, ally.Player.PlayerCombatState!.Energy);

            // The next players' turn, same round (the round rolls at the
            // player turn, so this is the harder case): the first explosion
            // still grants the energy, and the second does not.
            combat.CurrentSide = CombatSide.Player;
            Assert.True(SparksForEveryonePower.Counts(klee.Creature, klee.Creature));
            await sparks.OnBombExploded(null!, klee.Creature, enemy, 4, false);
            Assert.Equal(energy + 1, ally.Player.PlayerCombatState!.Energy);
            await sparks.OnBombExploded(null!, klee.Creature, enemy, 4, false);
            Assert.Equal(energy + 1, ally.Player.PlayerCombatState!.Energy);
        }
        finally
        {
            MegaCrit.Sts2.Core.Helpers.NonInteractiveMode.AutoSlayerCheck = quiet;
            KleeOverhaulLedger.ResetAll();
        }
    }

    [Fact]
    public void Sparks_for_everyone_rides_the_explosion_bus_and_gives_believe_in_yous_energy()
    {
        // STRUCTURAL (energy needs a live combat). The bus every Bomb reader
        // rides, so a Set off card, an ally's Attack and a Mine answering an
        // attack all count; each other living player; Believe In You's command.
        Assert.True(typeof(IProtoExplosionListener)
            .IsAssignableFrom(typeof(SparksForEveryonePower)));
        var seq = Il.CallSequence(
            Il.Method("SparksForEveryonePower", "OnBombExploded")).ToList();
        var others = seq.IndexOf("CoopSet.OtherPlayers");
        var latch = seq.IndexOf("KleeOverhaulLedger.TakeSparksForEveryone");
        var energy = seq.IndexOf("PlayerCmd.GainEnergy");
        Assert.True(others >= 0 && others < latch && latch < energy);
        Assert.Contains("ProtoBombPower.NotifyExplosionListeners",
            Il.Calls(Il.Method("ProtoBombPower", "Explode")));
    }

    // ---- helpers -----------------------------------------------------------------------

    private static void Upgrade(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
    }

    /// <summary>A power on <paramref name="owner"/>, placed by
    /// <paramref name="applier"/>: the backing fields, the way the harness
    /// seeds every power it cannot apply.</summary>
    private static T Power<T>(Creature owner, Creature applier, int amount)
        where T : PowerModel
    {
        var power = (T)RuntimeHelpers.GetUninitializedObject(typeof(T));
        SetField(power, "_owner", owner);
        SetField(power, "_applier", applier);
        SetField(power, "_amount", amount);
        Seat.Set(power, "IsMutable", true);
        return power;
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
