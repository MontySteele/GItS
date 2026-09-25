using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The afternoon seat round of 2026-09-25 (two blind seats, Codex and Opus, on
/// 0.2.3766): Sparks 'n' Splash re-timed to the start of the turn, Bottomless
/// Bag at 1 Spark, the Companion keyword tip, and the "Bomb 0" badge on a
/// revived Illusion.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on
/// <see cref="KleePlaytest20260924Tests"/>' terms. The picks (which Bomb, the
/// pile after growth, what the sweep claims) are pure and run against real
/// piles. A hit needs a live combat, so the order of the calls around it is
/// pinned off the compiled methods and says so. The end-to-end arithmetic is
/// the sim twin's: <c>tier0/tests/test_klee_overhaul_rules.py</c>
/// (<c>test_sparks_n_splash_*</c>).
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeSeatFixes20260925Tests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, new object?[] { });
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    // ---- Sparks 'n' Splash -------------------------------------------------

    [Fact]
    public void Sparks_n_splash_prints_the_start_of_turn_rule_and_costs_one_upgraded()
    {
        const string rule =
            "At the start of your turn, your largest [gold]Bomb[/gold] deals "
          + "its size in [gold]Pyro[/gold] damage without going off.";
        var card = new ProtoKoSparksNSplash();
        Assert.Equal(CardRarity.Rare, card.Rarity);
        Assert.Equal(CardType.Power, card.Type);
        Assert.Equal(2, card.EnergyCost.Canonical);
        Assert.Equal(rule, Face(card));
        // The badge says the same thing in the same words.
        Assert.Equal(rule, new BombEchoPower().Localization!
            .First(r => r.Item1 == "description").Item2);
        // Upgrade: cost 1.
        Assert.Equal(1, Upgraded<ProtoKoSparksNSplash>().EnergyCost
            .GetWithModifiers(CostModifiers.None));
    }

    [Fact]
    public void The_echo_left_the_end_of_the_turn_for_the_start()
    {
        // STRUCTURAL. The seats' finding was that at the end of the turn it
        // fired after the Bombs were already spent. It no longer overrides the
        // turn-end broadcast at all, and at the start of the turn it rides
        // `AfterPlayerTurnStart` -- strictly after rule 1's growth at
        // `BeforeSideTurnStart` (the resolved order is
        // `test_reaction_phase_parity.TURN_START_BROADCAST_ORDER`).
        var declared = BindingFlags.Public | BindingFlags.Instance
                     | BindingFlags.DeclaredOnly;
        Assert.Null(typeof(BombEchoPower).GetMethod("BeforeSideTurnEnd", declared));
        Assert.NotNull(typeof(BombEchoPower).GetMethod("AfterPlayerTurnStart", declared));
        Assert.Contains("ProtoBombPower.GrowBy",
                        Il.Calls(Il.Method("ProtoBombPower", "BeforeSideTurnStart")));
        Assert.Contains("KleeExpansion.RunTurnStartPlacements",
                        Il.Calls(Il.Method("BombEchoPower", "AfterPlayerTurnStart")));
    }

    [Fact]
    public void The_echo_runs_first_in_the_turn_start_sequencer()
    {
        // STRUCTURAL. One fixed order however the broadcast visits the three
        // Powers: the latch, then the echo reading the board as the growth
        // left it, then Secret Base and Dodoco placing.
        var seq = Il.CallSequence(Il.Method("KleeExpansion", "RunTurnStartPlacements"))
            .ToList();
        var latch = seq.IndexOf("KleeOverhaulLedger.TakeTurnStartPlacements");
        var echo = seq.IndexOf("BombEchoPower.Fire");
        var place = seq.IndexOf("ProtoBombPower.PlaceOnRandom");
        Assert.True(latch >= 0 && echo > latch && place > echo,
                    string.Join(", ", seq));
    }

    [Fact]
    public void A_bomb_4_placed_last_turn_is_read_as_8_and_stays()
    {
        // REAL: the pick. A Bomb 4 placed last turn grows by rule 1's 4 at the
        // start of the turn, and the echo reads the grown 8 -- reading takes
        // nothing off the pile.
        Assert.Equal(4, KleeOverhaulLaw.BombGrowth);
        var klee = Seat.Klee();
        var enemy = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, enemy);
        var pile = ProtoBombs.Place(enemy, klee.Creature, new ProtoBombs.Charge(4));

        pile.GrowBy(ProtoBombPower.GrowthFor(klee.Creature));
        var (target, size) = ProtoBombPower.LargestBombFor(klee.Creature);

        Assert.Same(enemy, target);
        Assert.Equal(8, size);
        Assert.Equal(new[] { 8 }, pile.Charges.Select(c => c.Size));
    }

    [Fact]
    public void The_echo_picks_her_largest_bomb_on_the_board_first_on_a_tie()
    {
        // REAL. The largest single charge of hers across ALL enemies, on the
        // enemy it is on; on a tie the first found. Another Klee's pile is
        // not hers to read. No Bomb: nothing.
        var klee = Seat.Klee();
        var other = Seat.Klee().Creature;
        var a = Seat.Klee(200).Creature;
        var b = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, a, b);

        var none = ProtoBombPower.LargestBombFor(klee.Creature);
        Assert.Null(none.Enemy);
        Assert.Equal(0, none.Size);

        ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(6));
        ProtoBombs.Place(b, klee.Creature, new ProtoBombs.Charge(3),
                         new ProtoBombs.Charge(9));
        ProtoBombs.Place(a, other, new ProtoBombs.Charge(40));
        var (target, size) = ProtoBombPower.LargestBombFor(klee.Creature);
        Assert.Same(b, target);
        Assert.Equal(9, size);

        var klee2 = Seat.Klee();
        var c = Seat.Klee(200).Creature;
        var d = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee2.Creature, c, d);
        ProtoBombs.Place(c, klee2.Creature, new ProtoBombs.Charge(6));
        ProtoBombs.Place(d, klee2.Creature, new ProtoBombs.Charge(6));
        Assert.Same(c, ProtoBombPower.LargestBombFor(klee2.Creature).Enemy);
    }

    [Fact]
    public void The_echo_pays_on_a_bombs_terms_and_sets_nothing_off()
    {
        // STRUCTURAL (a hit needs a live combat). The explosion's own door,
        // so the target's Vulnerable and the aura apply and Klee's Strength
        // does not; no Spark, no explosion, no ledger. The death sweep after
        // each hit is what lets a second copy read a board whose killed
        // enemy's Bombs have already jumped.
        var calls = Il.Calls(Il.Method("BombEchoPower", "Fire"));
        Assert.Contains("ElementalHit.DealWithoutDealerMods", calls);
        Assert.Contains("ProtoBombPower.SweepJumps", calls);
        Assert.DoesNotContain("ElementalHit.Deal", calls);
        Assert.DoesNotContain("ProtoBombPower.Explode", calls);
        Assert.DoesNotContain("SparkPower.Gain", calls);
    }

    // ---- Bottomless Bag ----------------------------------------------------

    [Fact]
    public void Bottomless_bag_costs_one_spark()
    {
        Assert.Equal(1, new ProtoKoBottomlessBag().PrintedSparkPrice);
    }

    // ---- Companion ---------------------------------------------------------

    [Fact]
    public void Companion_has_a_tip_and_the_readers_carry_it()
    {
        // The Opus seat: "Companion is never defined on screen, yet three
        // offered cards trigger on it."
        foreach (var name in new[] { "ProtoKoWitchesCircle",
                     "ProtoKoFriendshipBracelet", "ProtoKoComeBackAndPlay" })
        {
            var getter = Il.Method(name, "get_ExtraHoverTips");
            Assert.Contains("ArmKeywordTips.ForCompanion", Il.Calls(getter));
        }
        Assert.Equal("KLEEMOD-ARM_COMPANION", ArmKeywordTips.CompanionKey);
    }

    // ---- the Bomb 0 badge ----------------------------------------------------

    [Fact]
    public void An_emptied_pile_on_a_kept_corpse_is_claimed_and_leaves_the_body()
    {
        // THE CAUSE. The revived Eye with Teeth is an Illusion, and the game
        // keeps an Illusion's Buffs through its death (`IllusionPower
        // .ShouldPowerBeRemovedOnDeath`) and keeps its body in the combat to
        // revive. The death sweep took the pile's charges and jumped them --
        // and left the EMPTY pile on the body, which printed "Bomb 0" when the
        // Eye came back.
        //
        // REAL: the claim. A dead owner's pile is claimed whether or not it
        // still holds charges, and the claim knows the pile is still on the
        // body. STRUCTURAL: the sweep removes it.
        ProtoBombPower.Register.Rebase(null);
        var klee = Seat.Klee();
        var eye = Seat.Klee(6).Creature;
        var survivor = Seat.Klee(74).Creature;
        var combat = ProtoBombs.Board(klee.Creature, eye, survivor);

        var charged = ProtoBombs.Place(eye, klee.Creature, new ProtoBombs.Charge(3));
        ProtoBombPower.Register.Note(charged);
        Seat.Set(eye, "CurrentHp", 0);             // it died, and kept its Buffs

        var claimed = Assert.Single(ProtoBombPower.Register.Claim(combat));
        Assert.Same(charged, claimed.Pile);
        Assert.Equal(new[] { 3 }, claimed.Charges.Select(c => c.Size));
        Assert.Equal(0, charged.TotalSize);
        Assert.True(claimed.StillOnBody, "the kept corpse still wears the pile");

        // An already-empty pile on a dead body is claimed too, with nothing
        // to jump, so the sweep takes it off rather than leaving a Bomb 0.
        var empty = ProtoBombs.Place(eye, klee.Creature);
        ProtoBombPower.Register.Note(empty);
        var bare = Assert.Single(ProtoBombPower.Register.Claim(combat));
        Assert.Same(empty, bare.Pile);
        Assert.Empty(bare.Charges);
        Assert.True(bare.StillOnBody);
        Assert.Empty(ProtoBombPower.Register.Claim(combat));

        var sweep = Il.Calls(Il.Method("ProtoBombPower", "SweepJumps"));
        Assert.Contains("PowerCmd.Remove", sweep);
        Assert.Contains("ProtoBombPower.JumpCharges", sweep);
        ProtoBombPower.Register.Rebase(null);
    }
}
