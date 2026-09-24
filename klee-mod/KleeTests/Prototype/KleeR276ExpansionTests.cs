using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using System.Runtime.CompilerServices;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE R276 POOL EXPANSION -- thirty rows toward the 78-card pool R276 ruled
/// (the main session's spec; 2 Common, 18 Uncommon, 10 Rare), one pin or more
/// per rules note.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on <see cref="KleeR276BatchTests"/>'
/// terms. Every rule with a pure half -- the largest-Bomb reads and writes, the
/// Mine and Bomb selections, the discard filters, the latches, Boom Badge's
/// play count, Playdate's discount, the half of a Mine -- is run against real
/// piles, real ledgers and owned cards. What needs a live combat (a hit, a
/// placement, a draw, a pile move) is pinned off the compiled method, and says
/// so. The end-to-end arithmetic is the sim twin's:
/// <c>tier0/tests/test_klee_r276_expansion.py</c>, case for case.
///
/// NO NUMBER HERE IS QUOTABLE (R215 B): every one is a starting value.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeR276ExpansionTests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, new object?[] { });
        return card;
    }

    private static T Owned<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static IReadOnlyCollection<string> Play(string type) =>
        Il.Calls(Il.Method(type, "OnPlay"));

    private static (Seat Klee, Creature A, Creature B) Board()
    {
        var klee = Seat.Klee();
        var a = Seat.Klee(200).Creature;
        var b = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, a, b);
        return (klee, a, b);
    }

    // ---- the pool ---------------------------------------------------------

    public static IEnumerable<object[]> Rows() => new[]
    {
        // class, rarity, type, energy
        new object[] { typeof(ProtoKoHidingSpot), CardRarity.Common, CardType.Skill, 1 },
        new object[] { typeof(ProtoKoPlaydate), CardRarity.Common, CardType.Skill, 0 },
        new object[] { typeof(ProtoKoJumpyDumptyMkIii), CardRarity.Uncommon, CardType.Attack, 1 },
        new object[] { typeof(ProtoKoSpinningSparkler), CardRarity.Uncommon, CardType.Attack, 1 },
        new object[] { typeof(ProtoKoMineAllMine), CardRarity.Uncommon, CardType.Attack, 1 },
        new object[] { typeof(ProtoKoTeamEffort), CardRarity.Uncommon, CardType.Attack, 1 },
        new object[] { typeof(ProtoKoFishFry), CardRarity.Uncommon, CardType.Attack, 2 },
        new object[] { typeof(ProtoKoOneMoreCharge), CardRarity.Uncommon, CardType.Skill, 1 },
        new object[] { typeof(ProtoKoSitTight), CardRarity.Uncommon, CardType.Skill, 0 },
        new object[] { typeof(ProtoKoTreasureMap), CardRarity.Uncommon, CardType.Skill, 1 },
        new object[] { typeof(ProtoKoTagAlong), CardRarity.Uncommon, CardType.Skill, 1 },
        new object[] { typeof(ProtoKoComeBackAndPlay), CardRarity.Uncommon, CardType.Skill, 0 },
        new object[] { typeof(ProtoKoBoomBadge), CardRarity.Uncommon, CardType.Skill, 0 },
        new object[] { typeof(ProtoKoWaitForIt), CardRarity.Uncommon, CardType.Skill, 1 },
        new object[] { typeof(ProtoKoDuckAndRun), CardRarity.Uncommon, CardType.Skill, 1 },
        new object[] { typeof(ProtoKoPartyPoppers), CardRarity.Uncommon, CardType.Power, 1 },
        new object[] { typeof(ProtoKoLookOut), CardRarity.Uncommon, CardType.Power, 1 },
        new object[] { typeof(ProtoKoPatienceKlee), CardRarity.Uncommon, CardType.Power, 1 },
        new object[] { typeof(ProtoKoFriendshipBracelet), CardRarity.Uncommon, CardType.Power, 1 },
        new object[] { typeof(ProtoKoSecretBase), CardRarity.Uncommon, CardType.Power, 1 },
        new object[] { typeof(ProtoKoHalfAMountain), CardRarity.Rare, CardType.Skill, 1 },
        new object[] { typeof(ProtoKoFavoniusEscort), CardRarity.Rare, CardType.Skill, 1 },
        new object[] { typeof(ProtoKoAdventureClub), CardRarity.Rare, CardType.Skill, 1 },
        new object[] { typeof(ProtoKoWindblumeFireworks), CardRarity.Rare, CardType.Attack, 2 },
        new object[] { typeof(ProtoKoFireworksFinale), CardRarity.Rare, CardType.Attack, 0 },
        new object[] { typeof(ProtoKoDodoco), CardRarity.Rare, CardType.Power, 2 },
        new object[] { typeof(ProtoKoAftershock), CardRarity.Rare, CardType.Power, 2 },
        new object[] { typeof(ProtoKoSparkKnight), CardRarity.Rare, CardType.Power, 2 },
        new object[] { typeof(ProtoKoAlicesDetonator), CardRarity.Rare, CardType.Power, 1 },
        new object[] { typeof(ProtoKoSecondSurprise), CardRarity.Rare, CardType.Power, 1 },
    };

    [Theory]
    [MemberData(nameof(Rows))]
    public void Each_row_is_printed_at_the_specs_rarity_type_and_cost(
        System.Type type, CardRarity rarity, CardType kind, int energy)
    {
        var card = (CardModel)System.Activator.CreateInstance(type)!;
        Assert.Equal(rarity, card.Rarity);
        Assert.Equal(kind, card.Type);
        Assert.Equal(energy, card.EnergyCost.Canonical);
    }

    [Fact]
    public void The_thirty_are_offered_in_their_own_block_at_the_end_of_the_slice()
    {
        var slice = Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice"))
            .Where(c => c.Contains("ProtoKo")).ToList();
        var names = Rows().Select(r => ((System.Type)r[0]).Name).ToList();
        Assert.Equal(30, names.Count);
        Assert.Equal(30, names.Distinct().Count());
        var tail = slice.Skip(slice.Count - 30).ToList();
        for (var i = 0; i < names.Count; i++)
        {
            Assert.Contains(names[i], tail[i]);
        }
    }

    // ---- "your largest Bomb" ---------------------------------------------

    [Fact]
    public void The_largest_bomb_is_the_largest_charge_and_the_first_on_a_tie()
    {
        // REAL. One reading of "your largest Bomb" for One More Charge, Half a
        // Mountain, Treasure Map, Patience and Friendship Bracelet: the
        // largest single charge of hers on the living board; on a tie the
        // first found, which inside one pile is the OLDER charge.
        var (klee, a, b) = Board();
        var other = Seat.Klee().Creature;
        var pa = ProtoBombs.Place(a, klee.Creature,
                                  new ProtoBombs.Charge(7), new ProtoBombs.Charge(7));
        var pb = ProtoBombs.Place(b, klee.Creature, new ProtoBombs.Charge(5));
        ProtoBombs.Place(b, other, new ProtoBombs.Charge(40));    // not hers

        Assert.Equal(7, ProtoBombPower.LargestSizeFor(klee.Creature));
        Assert.Equal(12, ProtoBombPower.GrowLargest(klee.Creature, 5));
        Assert.Equal(new[] { 12, 7 }, pa.Charges.Select(c => c.Size));
        Assert.Equal(new[] { 5 }, pb.Charges.Select(c => c.Size));
    }

    [Fact]
    public void With_no_bomb_the_growth_does_nothing_and_draws_nothing()
    {
        var (klee, _, _) = Board();
        Assert.Equal(0, ProtoBombPower.GrowLargest(klee.Creature, 5));
        Assert.Equal(0, ProtoBombPower.MultiplyLargest(klee.Creature, 2));
        Assert.Equal(0, ProtoBombPower.DrawsAfterGrowth(0, 20, 1));
    }

    [Fact]
    public void One_more_charge_draws_only_when_the_grown_bomb_reaches_twenty()
    {
        // REAL, the bar ("if it is NOW 20 or more"), read off the size the
        // growth left. STRUCTURAL, the draw: `GrowLargestBy` asks the bar and
        // then `CardPileCmd.Draw`.
        Assert.Equal(1, ProtoBombPower.DrawsAfterGrowth(20, 20, 1));
        Assert.Equal(1, ProtoBombPower.DrawsAfterGrowth(23, 20, 1));
        Assert.Equal(0, ProtoBombPower.DrawsAfterGrowth(19, 20, 1));
        Assert.Equal(0, ProtoBombPower.DrawsAfterGrowth(30, 0, 0));
        var grow = Il.CallSequence(Il.Method("ProtoBombPower", "GrowLargestBy"))
            .ToList();
        Assert.True(grow.IndexOf("ProtoBombPower.GrowLargest")
                    < grow.IndexOf("ProtoBombPower.DrawsAfterGrowth"));
        Assert.Contains("CardPileCmd.Draw", grow);

        var card = new ProtoKoOneMoreCharge();
        Assert.Equal(5m, card.DynamicVars["Grow"].BaseValue);
        Assert.Equal(8m, Upgraded<ProtoKoOneMoreCharge>().DynamicVars["Grow"].BaseValue);
        Assert.Contains("If it is now 20 or more, draw 1 card.", Face(card));
    }

    [Fact]
    public void Half_a_mountain_doubles_the_largest_bomb_and_is_repeatable()
    {
        var (klee, a, _) = Board();
        var pile = ProtoBombs.Place(a, klee.Creature,
                                    new ProtoBombs.Charge(5), new ProtoBombs.Charge(9));
        Assert.Equal(18, ProtoBombPower.MultiplyLargest(klee.Creature, 2));
        Assert.Equal(36, ProtoBombPower.MultiplyLargest(klee.Creature, 2));
        Assert.Equal(new[] { 5, 36 }, pile.Charges.Select(c => c.Size));

        // No Exhaust; the upgrade buys Retain.
        var card = new ProtoKoHalfAMountain();
        Assert.DoesNotContain(CardKeyword.Exhaust, card.CanonicalKeywords);
        Assert.Contains(Il.Calls(Il.Method("ProtoKoHalfAMountain", "OnUpgrade")),
                        c => c.Contains("AddKeyword"));
        Assert.Contains("ProtoBombPower.MultiplyLargest", Play("ProtoKoHalfAMountain"));
    }

    [Fact]
    public void Favonius_escort_pays_twice_the_removed_size()
    {
        Assert.Equal(14, ProtoBombPower.BlockForRemoved(7, 2));
        Assert.Equal(7, ProtoBombPower.BlockForRemoved(7, 1));
        Assert.Equal(0, ProtoBombPower.BlockForRemoved(0, 2));
        Assert.Contains("ProtoBombPower.BlockForRemoved",
                        Il.Calls(Il.Method("ProtoBombPower",
                                           "RemoveLargestForBlockAndGain")));
        Assert.Contains("ProtoBombPower.RemoveLargestForBlockAndGain",
                        Play("ProtoKoFavoniusEscort"));
        Assert.Contains(Il.Calls(Il.Method("ProtoKoFavoniusEscort", "OnUpgrade")),
                        c => c.Contains("AddKeyword"));
    }

    // ---- the hits ---------------------------------------------------------

    [Fact]
    public void Mk_iii_hits_a_fresh_random_enemy_each_time_and_plants_on_it()
    {
        // STRUCTURAL: each hit rolls a living enemy, lands as her own Attack
        // hit, and places a Bomb on that body (joining any pile there), or on
        // a survivor if the hit killed it.
        Assert.Contains("ProtoBombPower.HitRandomAndPlant", Play("ProtoKoJumpyDumptyMkIii"));
        var hit = Il.CallSequence(Il.Method("ProtoBombPower", "HitRandomAndPlant"))
            .ToList();
        Assert.True(hit.IndexOf("ProtoBombPower.DealCardDamage")
                    < hit.IndexOf("ProtoBombPower.PlaceOrJump"));
        Assert.Contains(Il.Calls(Il.Method("ProtoBombPower", "PlaceOrJump")),
                        c => c == "ProtoBombPower.Place");

        var card = new ProtoKoJumpyDumptyMkIii();
        Assert.Equal(3m, card.DynamicVars.Damage.BaseValue);
        Assert.Equal(2m, card.DynamicVars["BombSize"].BaseValue);
        var up = Upgraded<ProtoKoJumpyDumptyMkIii>();
        Assert.Equal(4m, up.DynamicVars.Damage.BaseValue);
        Assert.Equal(3m, up.DynamicVars["BombSize"].BaseValue);
        Assert.Equal(TargetType.AllEnemies, card.TargetType);
    }

    [Fact]
    public void Spinning_sparkler_grows_the_bomb_on_the_enemy_it_hit_by_the_printed_number()
    {
        // REAL: "grows that Bomb by 2" -- the enemy's own largest charge of
        // hers takes it, so the pile's total rises by exactly 2; another
        // Klee's pile and a Bomb-less enemy are untouched.
        var (klee, a, b) = Board();
        var other = Seat.Klee().Creature;
        var mine = ProtoBombs.Place(a, klee.Creature,
                                    new ProtoBombs.Charge(3), new ProtoBombs.Charge(7));
        var theirs = ProtoBombs.Place(a, other, new ProtoBombs.Charge(9));
        Assert.True(ProtoBombPower.GrowLargestOn(a, klee.Creature, 2));
        Assert.Equal(new[] { 3, 9 }, mine.Charges.Select(c => c.Size));
        Assert.Equal(new[] { 9 }, theirs.Charges.Select(c => c.Size));
        Assert.False(ProtoBombPower.GrowLargestOn(b, klee.Creature, 2));

        // STRUCTURAL: a plain Attack, twice, never a Set off.
        var hits = Il.Calls(Il.Method("ProtoBombPower", "HitAndGrow"));
        Assert.Contains("ProtoBombPower.GrowLargestOn", hits);
        Assert.DoesNotContain(hits, c => c.StartsWith("ProtoBombPower.SetOff"));
        var card = new ProtoKoSpinningSparkler();
        Assert.Equal(5m, card.DynamicVars.Damage.BaseValue);
        Assert.Equal(2m, card.DynamicVars["Grow"].BaseValue);
        var up = Upgraded<ProtoKoSpinningSparkler>();
        Assert.Equal(6m, up.DynamicVars.Damage.BaseValue);
        Assert.Equal(3m, up.DynamicVars["Grow"].BaseValue);
    }

    [Fact]
    public void Mine_all_mine_hits_only_the_enemies_holding_one_of_her_mines()
    {
        var (klee, a, b) = Board();
        var c = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, a, b, c);
        ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(4, IsMine: true));
        ProtoBombs.Place(b, klee.Creature, new ProtoBombs.Charge(9));        // a Bomb, not a Mine
        ProtoBombs.Place(c, Seat.Klee().Creature,
                         new ProtoBombs.Charge(4, IsMine: true));             // someone else's
        Assert.Equal(new[] { a },
                     ProtoBombPower.MinedEnemies(new[] { a, b, c }, klee.Creature));
        Assert.Contains("ProtoBombPower.MinedEnemies",
                        Il.Calls(Il.Method("ProtoBombPower", "HitMined")));
        Assert.Equal(11m, Upgraded<ProtoKoMineAllMine>().DynamicVars.Damage.BaseValue);
    }

    [Fact]
    public void Fish_fry_reads_the_bombed_enemies_once_and_adds_the_bonus_to_their_hit()
    {
        var (klee, a, b) = Board();
        ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(2));
        var bombed = ProtoBombPower.BombedEnemies(new[] { a, b }, klee.Creature);
        Assert.Contains(a, bombed);
        Assert.DoesNotContain(b, bombed);

        var card = new ProtoKoFishFry();
        Assert.Equal(7m, card.DynamicVars.Damage.BaseValue);
        Assert.Equal(5m, card.DynamicVars.ExtraDamage.BaseValue);
        var up = Upgraded<ProtoKoFishFry>();
        Assert.Equal(10m, up.DynamicVars.Damage.BaseValue);
        Assert.Equal(7m, up.DynamicVars.ExtraDamage.BaseValue);
        var fry = Il.CallSequence(Il.Method("ProtoBombPower", "HitAllBombedBonus"))
            .ToList();
        Assert.True(fry.IndexOf("ProtoBombPower.BombedEnemies")
                    < fry.IndexOf("ProtoBombPower.DealCardDamage"));
    }

    [Fact]
    public void Team_effort_widens_on_a_companion_play_and_hits_the_target_only()
    {
        // STRUCTURAL: the card reads the ledger's Companion count; the wide
        // arm Sets off every enemy (one at a time) and THEN deals the card's
        // own hit to the aimed body.
        var play = Play("ProtoKoTeamEffort");
        Assert.Contains("KleeOverhaulLedger.get_CompanionPlayedThisTurn", play);
        Assert.Contains("ProtoBombPower.SetOffAllThenHit", play);
        Assert.Contains("ProtoBombPower.SetOffAimed", play);
        var wide = Il.CallSequence(Il.Method("ProtoBombPower", "SetOffAllThenHit"))
            .ToList();
        Assert.True(wide.IndexOf("KleeOverhaulLedger.NoteSetOffCardPlayed")
                    < wide.IndexOf("ProtoBombPower.SetOff"));
        Assert.True(wide.IndexOf("ProtoBombPower.SetOff")
                    < wide.IndexOf("ProtoBombPower.DealCardDamage"));
        Assert.IsAssignableFrom<ISetOffCard>(new ProtoKoTeamEffort());
        Assert.Equal(9m, Upgraded<ProtoKoTeamEffort>().DynamicVars.Damage.BaseValue);
    }

    [Fact]
    public void Windblume_fireworks_sets_off_then_hits_then_plants()
    {
        var play = Il.CallSequence(Il.Method("ProtoKoWindblumeFireworks", "OnPlay"))
            .ToList();
        var setOff = play.IndexOf("ProtoBombPower.SetOffAll");
        var place = play.IndexOf("ProtoBombPower.PlaceOnAll");
        var hit = play.FindIndex(c => c.StartsWith("DamageCmd.Attack"));
        Assert.True(setOff >= 0 && hit > setOff && place > hit);
        var up = Upgraded<ProtoKoWindblumeFireworks>();
        Assert.Equal(14m, up.DynamicVars.Damage.BaseValue);
        Assert.Equal(8m, up.DynamicVars["BombSize"].BaseValue);
    }

    [Fact]
    public void Fireworks_finale_spends_the_whole_bank_and_hits_once_per_spark()
    {
        var card = new ProtoKoFireworksFinale();
        Assert.IsAssignableFrom<ISparkXPricedCard>(card);
        Assert.Equal(1, SparkCost.PriceOf(card));      // unplayable at 0 Sparks
        var play = Play("ProtoKoFireworksFinale");
        Assert.Contains("SparkPower.SparksAtPlay", play);
        Assert.Contains("SparkPower.Spend", play);
        Assert.Contains(play, c => c.Contains("WithHitCount"));
        Assert.Equal(7m, Upgraded<ProtoKoFireworksFinale>().DynamicVars.Damage.BaseValue);
    }

    [Fact]
    public void Duck_and_run_blocks_then_sets_off_its_target()
    {
        var play = Il.CallSequence(Il.Method("ProtoKoDuckAndRun", "OnPlay")).ToList();
        Assert.True(play.FindIndex(c => c.StartsWith("CreatureCmd.GainBlock"))
                    < play.IndexOf("ProtoBombPower.SetOffAimed"));
        Assert.IsAssignableFrom<ISetOffCard>(new ProtoKoDuckAndRun());
        Assert.Equal(TargetType.AnyEnemy, new ProtoKoDuckAndRun().TargetType);
        Assert.Equal(10m, Upgraded<ProtoKoDuckAndRun>().DynamicVars.Block.BaseValue);
    }

    [Fact]
    public void Hiding_spot_blocks_and_places_a_mine_on_a_random_enemy()
    {
        var card = new ProtoKoHidingSpot();
        Assert.Equal(6m, card.DynamicVars.Block.BaseValue);
        Assert.Equal(3m, card.DynamicVars["BombSize"].BaseValue);
        var up = Upgraded<ProtoKoHidingSpot>();
        Assert.Equal(8m, up.DynamicVars.Block.BaseValue);
        Assert.Equal(5m, up.DynamicVars["BombSize"].BaseValue);
        Assert.Contains("ProtoBombPower.PlaceOnRandom", Play("ProtoKoHidingSpot"));
        Assert.Contains("[gold]Mine[/gold]", Face(card));
    }

    // ---- the Companion route ---------------------------------------------

    [Fact]
    public void Playdate_takes_one_off_the_next_companion_card_and_nothing_else()
    {
        var seat = Seat.Klee().WithPower<PlaydatePower>(1);
        var power = seat.Creature.Powers.OfType<PlaydatePower>().Single();

        var friend = Owned<ProtoMcDionaIcyPaws>(seat);           // a Companion card
        Assert.True(power.TryModifyEnergyCostInCombat(friend, 2m, out var cost));
        Assert.Equal(1m, cost);
        // Klee's own card is not a Companion card.
        var own = Owned<ProtoKoPop>(seat);
        Assert.False(power.TryModifyEnergyCostInCombat(own, 1m, out _));
        // A free card has nothing to take off.
        Assert.False(power.TryModifyEnergyCostInCombat(friend, 0m, out _));
        // Two Playdates are two sentences about the same next card.
        Assert.Equal(0m, PlaydatePower.Discounted(1m, 2));

        var card = new ProtoKoPlaydate();
        Assert.Equal(3m, card.DynamicVars["BombSize"].BaseValue);
        Assert.Equal(5m, Upgraded<ProtoKoPlaydate>().DynamicVars["BombSize"].BaseValue);
    }

    [Fact]
    public void Playdate_and_the_badge_expire_at_the_end_of_the_turn_they_were_played()
    {
        foreach (var type in new[] { "PlaydatePower", "BoomBadgePower", "WaitForItPower" })
        {
            Assert.Contains("PowerCmd.Remove",
                            Il.Calls(Il.Method(type, "AfterSideTurnEnd")));
        }
    }

    [Fact]
    public void The_discard_picks_filter_by_kind()
    {
        // REAL: Treasure Map offers the Set off cards, Come Back and Play! the
        // Companion cards, in pile order; none of the kind is an empty offer
        // and the card plays on (Treasure Map's growth is its second op).
        var seat = Seat.Klee();
        var kapow = Owned<ProtoKoKapow>(seat);
        var pop = Owned<ProtoKoPop>(seat);
        var countdown = Owned<ProtoKoCountdown>(seat);
        var friend = Owned<ProtoMcDionaIcyPaws>(seat);
        var discard = new CardModel[] { kapow, pop, countdown, friend };

        Assert.Equal(new CardModel[] { kapow, countdown },
                     KleeExpansion.Eligible(discard, KleeExpansion.FetchKind.SetOff));
        Assert.Equal(new CardModel[] { friend },
                     KleeExpansion.Eligible(discard, KleeExpansion.FetchKind.Companion));
        Assert.Empty(KleeExpansion.Eligible(new CardModel[] { pop },
                                            KleeExpansion.FetchKind.SetOff));

        var map = Il.CallSequence(Il.Method("ProtoKoTreasureMap", "OnPlay")).ToList();
        Assert.True(map.IndexOf("KleeExpansion.FetchFromDiscard")
                    < map.IndexOf("ProtoBombPower.GrowLargestBy"));
        var fetch = Il.Calls(Il.Method("KleeExpansion", "FetchFromDiscard"));
        Assert.Contains("CardSelectCmd.FromSimpleGrid", fetch);
        Assert.Contains("CardPileCmd.Add", fetch);
        Assert.Contains(Il.Calls(Il.Method("ProtoKoTreasureMap", "OnUpgrade")),
                        c => c.Contains("EnergyCost.UpgradeBy"));
        Assert.Contains("{IfUpgraded:show:Draw 1 card.|}",
                        Face(new ProtoKoComeBackAndPlay()));
    }

    [Fact]
    public void Tag_along_and_adventure_club_add_random_companions_free_this_turn()
    {
        // STRUCTURAL: a combat-scope copy, the stand-in hand-off, cost 0 this
        // turn, into the hand.
        var add = Il.Calls(Il.Method("KleeExpansion", "AddRandomCompanions"));
        Assert.Contains("CompanionStandIns.HandOff", add);
        Assert.Contains(add, c => c.Contains("SetThisTurn"));
        Assert.Contains("CardPileCmd.AddGeneratedCardToCombat", add);

        Assert.Contains(CardKeyword.Exhaust, new ProtoKoTagAlong().CanonicalKeywords);
        Assert.Contains(Il.Calls(Il.Method("ProtoKoTagAlong", "OnUpgrade")),
                        c => c.Contains("RemoveKeyword"));
        Assert.Contains(CardKeyword.Exhaust, new ProtoKoAdventureClub().CanonicalKeywords);
        Assert.Contains(Il.Calls(Il.Method("ProtoKoAdventureClub", "OnUpgrade")),
                        c => c.Contains("EnergyCost.UpgradeBy"));
    }

    [Fact]
    public void Friendship_bracelet_grows_the_largest_bomb_on_a_companion_play()
    {
        var play = Il.Calls(Il.Method("FriendshipBraceletPower", "AfterCardPlayed"));
        Assert.Contains("KleeExpansion.IsCompanionCard", play);
        Assert.Contains("ProtoBombPower.GrowLargest", play);
        Assert.Equal(4m, Upgraded<ProtoKoFriendshipBracelet>()
                             .DynamicVars["PowerAmount"].BaseValue);
    }

    // ---- the Spark-supported Cook -----------------------------------------

    [Fact]
    public void Boom_badge_doubles_the_next_set_off_card_only()
    {
        var seat = Seat.Klee().WithPower<BoomBadgePower>(1);
        var badge = seat.Creature.Powers.OfType<BoomBadgePower>().Single();
        Assert.Equal(2, badge.ModifyCardPlayCount(Owned<ProtoKoKapow>(seat), null, 1));
        Assert.Equal(1, badge.ModifyCardPlayCount(Owned<ProtoKoPop>(seat), null, 1));
        // Another player's Set off card is not hers to double.
        Assert.Equal(1, badge.ModifyCardPlayCount(Owned<ProtoKoKapow>(Seat.Klee()), null, 1));
        // The doubled card spends one badge.
        Assert.Contains(Il.Calls(Il.Method("BoomBadgePower", "AfterCardPlayed")),
                        c => c.Contains("PowerCmd"));

        var card = new ProtoKoBoomBadge();
        Assert.Equal(3, card.PrintedSparkPrice);
        Assert.Equal(2, Upgraded<ProtoKoBoomBadge>().PrintedSparkPrice);
    }

    [Fact]
    public void Sit_tight_leaves_its_bonus_to_the_end_of_the_turn()
    {
        var card = new ProtoKoSitTight();
        Assert.Contains(CardKeyword.Retain, card.CanonicalKeywords);
        Assert.Equal(1, card.PrintedSparkPrice);
        Assert.Equal(5m, card.DynamicVars.Block.BaseValue);
        Assert.Equal(4m, card.DynamicVars["PowerAmount"].BaseValue);
        var up = Upgraded<ProtoKoSitTight>();
        Assert.Equal(7m, up.DynamicVars.Block.BaseValue);
        Assert.Equal(5m, up.DynamicVars["PowerAmount"].BaseValue);
        // The play reads no ledger: it gains its 5 and installs the power.
        var play = Play("ProtoKoSitTight");
        Assert.DoesNotContain("KleeOverhaulLedger.get_SetOffThisTurn", play);
        Assert.Contains("PowerCmd.Apply", play);
        Assert.Equal(
            "Gain {Block:diff()} [gold]Block[/gold]. At the end of this turn, "
          + "if no [gold]Bomb[/gold] of yours went off this turn, gain "
          + "{PowerAmount:diff()} [gold]Block[/gold].",
            Face(card));
    }

    [Fact]
    public void Sit_tight_pays_only_on_a_turn_where_nothing_went_off()
    {
        // REAL: the ledger read is the whole condition, and it is rule 7's
        // first counter -- ANY explosion this turn, before or after the card.
        var klee = Seat.Klee().Creature;
        KleeOverhaulLedger.ResetAll();
        var ledger = KleeOverhaulLedger.For(klee);
        Assert.True(SitTightPower.Pays(ledger));
        // A Mine answering an attack passes no card but still went off.
        ledger.NoteExplosion(reacted: false, damageDealt: 3);
        Assert.False(SitTightPower.Pays(ledger));
        KleeOverhaulLedger.ResetAll();

        // STRUCTURAL: before the discard flush, it asks the ledger, pays
        // Block and removes itself.
        var turnEnd = Il.CallSequence(Il.Method("SitTightPower", "BeforeSideTurnEnd"))
            .ToList();
        Assert.Contains("SitTightPower.Pays", turnEnd);
        Assert.Contains("CreatureCmd.GainBlock", turnEnd);
        Assert.Contains("PowerCmd.Remove", turnEnd);
    }

    [Fact]
    public void Wait_for_it_is_a_one_shot_on_her_next_reacting_bomb()
    {
        // STRUCTURAL: the power removes itself before it pays.
        var pay = Il.CallSequence(Il.Method("WaitForItPower", "AfterChargeExploded"))
            .ToList();
        var remove = pay.IndexOf("PowerCmd.Remove");
        Assert.True(remove >= 0);
        Assert.True(pay.IndexOf("PlayerCmd.GainEnergy") > remove);
        Assert.True(pay.IndexOf("CardPileCmd.Draw") > remove);
        Assert.Contains(CardKeyword.Retain, new ProtoKoWaitForIt().CanonicalKeywords);
    }

    [Fact]
    public async Task Wait_for_it_ignores_an_explosion_that_did_not_react()
    {
        // REAL: the early return is the whole of "the next time a Bomb
        // triggers a Reaction" -- a plain explosion leaves the power up.
        var seat = Seat.Klee().WithPower<WaitForItPower>(1);
        var power = seat.Creature.Powers.OfType<WaitForItPower>().Single();
        await power.AfterChargeExploded(null!, seat.Creature, Seat.Klee().Creature,
                                        new ProtoBombPower.ProtoCharge(5, false, 0),
                                        reacted: false);
        Assert.Contains(power, seat.Creature.Powers);
    }

    [Fact]
    public void Patience_pays_only_on_a_turn_with_no_set_off_card()
    {
        var klee = Seat.Klee().Creature;
        KleeOverhaulLedger.ResetAll();
        var ledger = KleeOverhaulLedger.For(klee);
        Assert.True(PatienceKleePower.Pays(ledger));
        ledger.NoteSetOffCardPlayed(new ProtoKoKapow());
        Assert.False(PatienceKleePower.Pays(ledger));
        // After the echo, on the strictly later broadcast.
        Assert.Contains("ProtoBombPower.GrowLargest",
                        Il.Calls(Il.Method("PatienceKleePower", "AfterSideTurnEnd")));
        Assert.Equal(6m, Upgraded<ProtoKoPatienceKlee>()
                             .DynamicVars["PowerAmount"].BaseValue);
        KleeOverhaulLedger.ResetAll();
    }

    [Fact]
    public void Party_poppers_reads_the_cost_badge()
    {
        Assert.True(KleeExpansion.CostsSparks(new ProtoKoPocketMatch()));
        Assert.True(KleeExpansion.CostsSparks(new ProtoKoFireworksFinale()));
        Assert.False(KleeExpansion.CostsSparks(new ProtoKoPop()));
        Assert.Contains("KleeExpansion.CostsSparks",
                        Il.Calls(Il.Method("PartyPoppersPower", "AfterCardPlayed")));
        Assert.Equal(3m, Upgraded<ProtoKoPartyPoppers>()
                             .DynamicVars["PowerAmount"].BaseValue);
    }

    // ---- start of turn -----------------------------------------------------

    [Fact]
    public void Secret_base_reads_the_board_before_dodocos_mine_lands()
    {
        // REAL: the latch, once per turn per Klee.
        var klee = Seat.Klee().Creature;
        KleeOverhaulLedger.ResetAll();
        var ledger = KleeOverhaulLedger.For(klee);
        Assert.True(ledger.TakeTurnStartPlacements());
        Assert.False(ledger.TakeTurnStartPlacements());
        ledger.RollTo(1);
        Assert.True(ledger.TakeTurnStartPlacements());
        KleeOverhaulLedger.ResetAll();

        // STRUCTURAL: both Powers call the one sequencer, which asks Secret
        // Base's question before Dodoco's Mine is placed.
        foreach (var type in new[] { "SecretBasePower", "DodocoPower" })
        {
            Assert.Contains("KleeExpansion.RunTurnStartPlacements",
                            Il.Calls(Il.Method(type, "AfterPlayerTurnStart")));
        }
        var run = Il.CallSequence(Il.Method("KleeExpansion", "RunTurnStartPlacements"))
            .ToList();
        Assert.True(run.IndexOf("KleeOverhaulLedger.TakeTurnStartPlacements")
                    < run.IndexOf("ProtoBombPower.AnyPlacedBy"));
        Assert.True(run.IndexOf("ProtoBombPower.AnyPlacedBy")
                    < run.LastIndexOf("ProtoBombPower.PlaceOnRandom"));
        Assert.Equal(7m, Upgraded<ProtoKoSecretBase>()
                             .DynamicVars["PowerAmount"].BaseValue);
        Assert.Contains(Il.Calls(Il.Method("ProtoKoDodoco", "OnUpgrade")),
                        c => c.Contains("EnergyCost.UpgradeBy"));
    }

    [Fact]
    public void Alices_detonator_adds_a_kapow_after_the_draw_upgraded_on_the_plus_card()
    {
        Assert.False(((AlicesDetonatorBasePower)RuntimeHelpers
            .GetUninitializedObject(typeof(AlicesDetonatorPower))).Upgraded);
        Assert.True(((AlicesDetonatorBasePower)RuntimeHelpers
            .GetUninitializedObject(typeof(AlicesDetonatorPlusPower))).Upgraded);
        Assert.Contains("AlicesDetonatorBasePower.Install", Play("ProtoKoAlicesDetonator"));
        var turn = Il.Calls(Il.Method("AlicesDetonatorBasePower", "AfterPlayerTurnStart"));
        Assert.Contains("CardModel.UpgradeInternal", turn);
        Assert.Contains("CardPileCmd.AddGeneratedCardToCombat", turn);
        Assert.Contains(turn, c => c.Contains("CreateCard"));
        Assert.Contains("{IfUpgraded:show:an upgraded|a} Ka-pow!",
                        Face(new ProtoKoAlicesDetonator()));
        // No prompt of any kind.
        Assert.DoesNotContain(turn, c => c.StartsWith("CardSelectCmd"));
    }

    [Fact]
    public void Alices_detonator_previews_the_kapow_it_adds_upgraded_on_the_plus()
    {
        // STRUCTURAL: `HoverTipFactory.FromCard` resolves through `ModelDb`,
        // which is outside the headless boundary. The card's tips end in the
        // one preview helper, and the helper previews Ka-pow! upgraded exactly
        // when the card is (Blade Dance's Shiv, the base game's shape).
        var tips = typeof(ProtoKoAlicesDetonator)
            .GetProperty("ExtraHoverTips", HeadlessGame.All)!.GetGetMethod(true)!;
        Assert.Contains("KleeExpansion.WithKapowPreview", Il.Calls(tips));
        var preview = Il.Calls(Il.Method("KleeExpansion", "WithKapowPreview"));
        Assert.Contains("HoverTipFactory.FromCard", preview);
        Assert.Contains("CardModel.get_IsUpgraded", preview);

        // And the Power's badge previews the same card, upgraded on the Plus
        // twin -- the Ka-pow! it actually adds.
        var badge = typeof(AlicesDetonatorBasePower)
            .GetProperty("ExtraHoverTips", HeadlessGame.All)!.GetGetMethod(true)!;
        var calls = Il.Calls(badge);
        Assert.Contains("HoverTipFactory.FromCard", calls);
        Assert.Contains("AlicesDetonatorBasePower.get_Upgraded", calls);

        // The face stays plain: the preview carries the card, not a gold word.
        Assert.DoesNotContain("[gold]Ka-pow![/gold]", Face(new ProtoKoAlicesDetonator()));
    }

    // ---- the explosion's charge-aware door ----------------------------------

    [Fact]
    public void The_charge_door_runs_after_the_explosion_bus()
    {
        var explode = Il.CallSequence(Il.Method("ProtoBombPower", "Explode")).ToList();
        var bus = explode.IndexOf("ProtoBombPower.NotifyExplosionListeners");
        var door = explode.IndexOf("KleeExpansion.AfterChargeExploded");
        Assert.True(bus >= 0 && door > bus);
    }

    [Fact]
    public async Task Look_out_and_second_surprise_ignore_a_plain_bomb()
    {
        var seat = Seat.Klee().WithPower<LookOutPower>(3).WithPower<SecondSurprisePower>(1);
        var enemy = Seat.Klee(200).Creature;
        var plain = new ProtoBombPower.ProtoCharge(8, false, 0);
        foreach (var power in seat.Creature.Powers.OfType<IProtoChargeListener>())
        {
            // Returns before any command: a plain Bomb is not a Mine.
            await power.AfterChargeExploded(null!, seat.Creature, enemy, plain, false);
        }
        Assert.Contains("CreatureCmd.GainBlock",
                        Il.Calls(Il.Method("LookOutPower", "AfterChargeExploded")));
        var surprise = Il.Calls(Il.Method("SecondSurprisePower", "AfterChargeExploded"));
        Assert.Contains("ProtoBombPower.HalfOf", surprise);
        Assert.Contains("ProtoBombPower.PlaceOrJump", surprise);
        Assert.Equal(5m, Upgraded<ProtoKoLookOut>().DynamicVars["PowerAmount"].BaseValue);
    }

    [Fact]
    public void Second_surprise_places_half_rounded_down_and_nothing_at_zero()
    {
        Assert.Equal(3, ProtoBombPower.HalfOf(7));
        Assert.Equal(4, ProtoBombPower.HalfOf(8));
        Assert.Equal(0, ProtoBombPower.HalfOf(1));
        Assert.Equal(0, ProtoBombPower.HalfOf(0));
        Assert.Contains(Il.Calls(Il.Method("ProtoKoSecondSurprise", "OnUpgrade")),
                        c => c.Contains("EnergyCost.UpgradeBy"));
    }

    [Fact]
    public void Aftershock_fires_once_per_turn_on_a_reacting_bomb()
    {
        var klee = Seat.Klee().Creature;
        KleeOverhaulLedger.ResetAll();
        var ledger = KleeOverhaulLedger.For(klee);
        Assert.True(ledger.TakeAftershock());
        Assert.False(ledger.TakeAftershock());
        ledger.RollTo(1);
        Assert.True(ledger.TakeAftershock());
        KleeOverhaulLedger.ResetAll();

        var shock = Il.CallSequence(Il.Method("AftershockPower", "AfterChargeExploded"))
            .ToList();
        Assert.True(shock.IndexOf("KleeOverhaulLedger.TakeAftershock")
                    < shock.IndexOf("ProtoBombPower.PlaceOnRandom"));
    }

    [Fact]
    public void Spark_knight_hits_once_per_spark_that_landed()
    {
        Assert.Equal(3, SparkKnightPower.HitsFor(3));
        Assert.Equal(0, SparkKnightPower.HitsFor(0));
        Assert.Equal(0, SparkKnightPower.HitsFor(-2));
        Assert.Contains("SparkKnightPower.AfterSparksGained",
                        Il.Calls(Il.Method("SparkPower", "Gain")));
        Assert.Equal(3m, Upgraded<ProtoKoSparkKnight>().DynamicVars["PowerAmount"].BaseValue);
    }

    [Fact]
    public void Spark_knight_hit_carries_no_element()
    {
        // STRUCTURAL (a hit needs a live combat): the hit goes out through the
        // element-less door, never the aura-resolving one, so a companion's
        // Hydro survives it and nothing reacts. The real board is the sim
        // twin's `test_spark_knight_hit_leaves_hydro_standing`.
        var hit = Il.Calls(Il.Method("SparkKnightPower", "AfterSparksGained"));
        Assert.Contains("ElementalHit.DealUnelemented", hit);
        Assert.DoesNotContain("ElementalHit.Deal", hit);
        var door = Il.Calls(Il.Method("ElementalHit", "DealUnelemented"));
        Assert.DoesNotContain(door, c => c.StartsWith("AuraCmd."));
        Assert.DoesNotContain(door, c => c.StartsWith("ReactionEffects."));
        Assert.DoesNotContain(door, c => c.StartsWith("ReactionTable."));
        Assert.Contains("CreatureCmd.Damage", door);
        Assert.DoesNotContain("[gold]Pyro[/gold]", Face(new ProtoKoSparkKnight()));
    }
}
