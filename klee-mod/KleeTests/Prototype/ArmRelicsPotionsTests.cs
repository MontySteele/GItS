#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
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
using SilentRelics = MegaCrit.Sts2.Core.Models.Relics;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KLEE'S AND FURINA'S OWN RELICS AND POTIONS
/// (<c>review/active/relics-potions-klee-furina-2026-09-27.md</c>, ruled
/// 2026-09-27: all four picks at their defaults, the two Rare potions raised).
///
/// WHAT IS REAL AND WHAT IS STRUCTURAL, on the suite's usual terms. The pool
/// OFFER runs for real over a pool whose member list is seeded (a pool cannot
/// be BUILT headless -- <c>ModelDb</c> is empty), and the member list itself
/// is pinned off <c>GenerateAllRelics</c>'s call sites. Every relic's and
/// potion's decision -- a bonus, a latch, a threshold, a doubling, a pooled
/// Spend, a fade that takes nothing -- runs on a headless board. What awaits
/// a command that needs a live combat (a placement, a hit, Block, a summon) is
/// pinned by its doors and their order, and says so.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class ArmRelicsPotionsTests
{
    // ==== the pools ==========================================================

    [Fact]
    public void Each_arm_adds_the_base_games_shape_one_common_two_uncommon_three_rare_one_shop()
    {
        foreach (var set in new[] { KleeArmRelics.Types, FurinaStageRelics.Types })
        {
            var rarities = set.Select(t => Canon<RelicModel>(t).Rarity).ToList();
            Assert.Equal(7, rarities.Count);
            Assert.Equal(1, rarities.Count(r => r == RelicRarity.Common));
            Assert.Equal(2, rarities.Count(r => r == RelicRarity.Uncommon));
            Assert.Equal(3, rarities.Count(r => r == RelicRarity.Rare));
            Assert.Equal(1, rarities.Count(r => r == RelicRarity.Shop));
        }
        foreach (var set in new[] { ArmPotions.Klee, ArmPotions.Furina })
        {
            var potions = set.Select(t => Canon<PotionModel>(t)).ToList();
            Assert.Equal(
                new[] { PotionRarity.Common, PotionRarity.Uncommon, PotionRarity.Rare },
                potions.Select(p => p.Rarity).ToArray());
            Assert.All(potions, p => Assert.Equal(PotionUsage.CombatOnly, p.Usage));
            Assert.All(potions, p => Assert.Equal(TargetType.AnyPlayer, p.TargetType));
        }
    }

    [Fact]
    public void Every_relic_and_potion_has_a_title_and_a_plain_face()
    {
        var models = KleeArmRelics.Types.Concat(FurinaStageRelics.Types)
            .Select(t => (ILocalizationProvider)Canon<AbstractModel>(t))
            .Concat(ArmPotions.Klee.Concat(ArmPotions.Furina)
                .Select(t => (ILocalizationProvider)Canon<AbstractModel>(t)));
        foreach (var model in models)
        {
            var loc = model.Localization!;
            Assert.Equal(new[] { "title", "description" },
                         loc.Select(r => r.Item1).ToArray());
            var face = loc[1].Item2;
            Assert.DoesNotContain("{", face);
            Assert.True(face.Length < 140, $"{loc[0].Item2}: {face}");
        }
    }

    [Fact]
    public void Each_pool_lists_its_seven_as_members()
    {
        // STRUCTURAL: membership is what `RelicModel.Pool` resolves through,
        // and `GenerateAllRelics` needs `ModelDb`. Every one of the seven is a
        // `ModelDb.Relic<T>` call site in its own pool.
        var klee = Il.CallSequence(Il.Method("KleeRelicPool", "GenerateAllRelics"));
        foreach (var t in KleeArmRelics.Types)
        {
            Assert.Contains($"ModelDb.Relic<{t.Name}>", klee);
        }
        var furina = Il.CallSequence(Il.Method("FurinaRelicPool", "GenerateAllRelics"));
        foreach (var t in FurinaStageRelics.Types)
        {
            Assert.Contains($"ModelDb.Relic<{t.Name}>", furina);
        }
    }

    [Fact]
    public void Klee_arm_on_offers_her_eight_and_the_ancient_and_no_silent_borrow()
    {
        var pool = Pool<KleeRelicPool>(KleeMembers());
        try
        {
            var offer = Types(pool.GetUnlockedRelics(null!));
            Assert.Equal(
                new[] { typeof(PoundingSurprise), typeof(ExplosiveFrags) }
                    .Concat(KleeArmRelics.Types).OrderBy(t => t.Name),
                offer.OrderBy(t => t.Name));
            Assert.DoesNotContain(offer, t => t.Assembly != typeof(Klee).Assembly);
        }
        finally
        {
        }
    }

    [Fact]
    public void Kokomi_keeps_the_silent_borrow_for_relics_and_potions()
    {
        // No offer override: `RelicPoolModel`'s own, which is every member.
        Assert.Equal(typeof(RelicPoolModel),
            typeof(KokomiRelicPool).GetMethod("GetUnlockedRelics")!.DeclaringType);
        var potions = Il.CallSequence(
            typeof(Kokomi).GetProperty("PotionPool")!.GetGetMethod()!);
        Assert.Equal(new[] { "ModelDb.PotionPool<SilentPotionPool>" },
                     potions.Where(c => c.StartsWith("ModelDb.")).ToArray());
    }

    [Theory]
    [InlineData(typeof(Klee), "KleeOverhaul", "KleePotionPool")]
    [InlineData(typeof(Furina), "FurinaStage", "FurinaPotionPool")]
    public void The_potion_pool_is_the_arms_three_on_and_the_silent_borrow_off(
        Type character, string arm, string own)
    {
        // STRUCTURAL (`ModelDb.PotionPool<T>` needs a booted game): the getter
        // asks its arm, then answers its own pool or the borrow.
        var getter = character.GetProperty("PotionPool")!.GetGetMethod()!;
        var calls = Il.CallSequence(getter);
        Assert.Contains($"ModelDb.PotionPool<{own}>", calls);

        var pool = Il.CallSequence(Il.Method(own, "GenerateAllPotions"));
        var three = own == "KleePotionPool" ? ArmPotions.Klee : ArmPotions.Furina;
        Assert.Equal(three.Select(t => $"ModelDb.Potion<{t.Name}>").ToArray(),
                     pool.Where(c => c.StartsWith("ModelDb.Potion<")).ToArray());
    }

    [Fact]
    public void The_potion_pools_offer_their_three_and_nothing_else()
    {
        var klee = (KleePotionPool)RuntimeHelpers.GetUninitializedObject(typeof(KleePotionPool));
        SetField(klee, "_allPotions", ArmPotions.Klee.Select(t => Canon<PotionModel>(t)).ToList());
        Assert.Equal(ArmPotions.Klee, klee.GetUnlockedPotions(null!).Select(p => p.GetType()));
        var furina = (FurinaPotionPool)RuntimeHelpers.GetUninitializedObject(typeof(FurinaPotionPool));
        SetField(furina, "_allPotions", ArmPotions.Furina.Select(t => Canon<PotionModel>(t)).ToList());
        Assert.Equal(ArmPotions.Furina, furina.GetUnlockedPotions(null!).Select(p => p.GetType()));
    }

    // ==== Klee ===============================================================

    [Fact]
    public void Dodoco_charm_adds_one_per_copy_to_a_placement_and_nothing_arm_off()
    {
        using var arm = new KleeArm();
        var klee = Seat.Klee();
        Assert.Equal(0, DodocoCharm.BonusFor(klee.Creature));
        Give<DodocoCharm>(klee);
        Assert.Equal(1, DodocoCharm.BonusFor(klee.Creature));
        Give<DodocoCharm>(klee);
        Assert.Equal(2, DodocoCharm.BonusFor(klee.Creature));
    }

    [Fact]
    public void Dodoco_charm_is_paid_at_the_placer_and_never_on_a_move()
    {
        // STRUCTURAL (a placement is a `PowerCmd.Apply`): `Place` reads the
        // bonus, and every caller passes `relocated` -- true for the two
        // moves (a jump, a merge), false for every placement.
        Assert.Contains("DodocoCharm.BonusFor",
                        Il.Calls(Il.Method("ProtoBombPower", "Place")));
        foreach (var move in new[] { "JumpCharges", "MergeAllTo" })
        {
            Assert.All(PlaceFlags(move), f => Assert.True(f, move));
        }
        foreach (var place in new[] { "PlaceOnAll", "PlaceOnRandom", "PlaceCopyOfLargest", "Explode" })
        {
            Assert.All(PlaceFlags(place), f => Assert.False(f, place));
        }
    }

    [Fact]
    public void Clover_charm_pays_three_block_a_copy_on_a_mine_whatever_set_it_off()
    {
        using var arm = new KleeArm();
        var klee = Seat.Klee();
        Assert.Equal(0, CloverCharm.BlockFor(klee.Creature));
        Give<CloverCharm>(klee);
        Assert.Equal(3, CloverCharm.BlockFor(klee.Creature));
        // The Mine branch of the one explosion, then the Block.
        var explode = Il.CallSequence(Il.Method("ProtoBombPower", "Explode")).ToList();
        Assert.Contains("CloverCharm.AfterMineWentOff", explode);
        Assert.True(explode.IndexOf("MineFragsPower.OnMineWentOff")
                    < explode.IndexOf("CloverCharm.AfterMineWentOff"));
        Assert.Contains("CreatureCmd.GainBlock",
                        Il.Calls(Il.Method("CloverCharm", "AfterMineWentOff")));
    }

    [Fact]
    public void Fresh_catch_and_dodoco_army_fire_on_her_first_turn_only()
    {
        using var arm = new KleeArm();
        var klee = Seat.Klee().WithCombatState();
        var catchRelic = Give<FreshCatch>(klee);
        var army = Give<DodocoArmy>(klee);
        Assert.True(FreshCatch.FirstTurnOf(catchRelic, klee.Player));
        Assert.True(FreshCatch.FirstTurnOf(army, klee.Player));
        Assert.False(FreshCatch.FirstTurnOf(catchRelic, Seat.Klee().WithCombatState().Player));
        klee.Player.PlayerCombatState!.IncrementTurnNumber();
        Assert.False(FreshCatch.FirstTurnOf(catchRelic, klee.Player));

        // The doors: Hydro through the shared element funnel, a Mine 2 on
        // ALL enemies through the arm's own placer.
        Assert.Contains("ElementalHit.ApplyOnly",
                        Il.Calls(Il.Method("FreshCatch", "AfterPlayerTurnStart")));
        Assert.Contains("ProtoBombPower.PlaceOnAll",
                        Il.Calls(Il.Method("DodocoArmy", "AfterPlayerTurnStart")));
        Assert.Equal(2, DodocoArmy.MineSize);
    }

    [Fact]
    public async Task Alices_guidebook_grows_her_largest_bomb_three_from_turn_two()
    {
        using var arm = new KleeArm();
        var klee = Seat.Klee().WithCombatState();
        var a = Enemy();
        var b = Enemy();
        ProtoBombs.Board(klee.Creature, a, b);
        var small = ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(4));
        var big = ProtoBombs.Place(b, klee.Creature, new ProtoBombs.Charge(5),
                                   new ProtoBombs.Charge(9));
        var book = Give<AlicesGuidebook>(klee);

        await book.AfterPlayerTurnStartLate(null!, klee.Player);   // turn 1
        Assert.Equal(new[] { 5, 9 }, big.Charges.Select(c => c.Size));

        klee.Player.PlayerCombatState!.IncrementTurnNumber();
        await book.AfterPlayerTurnStartLate(null!, klee.Player);   // turn 2
        Assert.Equal(new[] { 5, 12 }, big.Charges.Select(c => c.Size));
        Assert.Equal(new[] { 4 }, small.Charges.Select(c => c.Size));
    }

    [Fact]
    public async Task Fireworks_stand_pays_one_energy_when_one_card_sets_off_three()
    {
        using var arm = new KleeArm();
        var quiet = MegaCrit.Sts2.Core.Helpers.NonInteractiveMode.AutoSlayerCheck;
        MegaCrit.Sts2.Core.Helpers.NonInteractiveMode.AutoSlayerCheck = () => true;
        try
        {
            var klee = Seat.Klee().WithCombatState();
            var enemy = Enemy();
            ProtoBombs.Board(klee.Creature, enemy);
            var stand = Give<FireworksStand>(klee);
            var energy = klee.Player.PlayerCombatState!.Energy;
            var play = Play(Owned(new ProtoKoShrapnel(), klee), klee);

            // Two go off: nothing.
            await stand.BeforeCardPlayed(play);
            for (var i = 0; i < 2; i++)
            {
                await stand.OnBombExploded(null!, klee.Creature, enemy, 4, false);
            }
            await stand.AfterCardPlayed(null!, play);
            Assert.Equal(energy, klee.Player.PlayerCombatState!.Energy);

            // Three go off, one of another Klee's among four: one energy.
            var other = Seat.Klee();
            await stand.BeforeCardPlayed(play);
            await stand.OnBombExploded(null!, other.Creature, enemy, 4, false);
            for (var i = 0; i < 3; i++)
            {
                await stand.OnBombExploded(null!, klee.Creature, enemy, 4, false);
            }
            Assert.Equal(3, stand.SetOffThisPlay);
            await stand.AfterCardPlayed(null!, play);
            Assert.Equal(energy + 1, klee.Player.PlayerCombatState!.Energy);

            // A Mine going off outside a card counts toward nothing.
            await stand.OnBombExploded(null!, klee.Creature, enemy, 4, false);
            Assert.Equal(0, stand.SetOffThisPlay);
        }
        finally
        {
            MegaCrit.Sts2.Core.Helpers.NonInteractiveMode.AutoSlayerCheck = quiet;
        }
    }

    [Fact]
    public void Alices_teapot_takes_the_first_bomb_that_goes_off_each_round()
    {
        using var arm = new KleeArm();
        var klee = Seat.Klee();
        var enemy = Enemy();
        var combat = ProtoBombs.Board(klee.Creature, enemy);
        combat.RoundNumber = 1;

        // No Teapot: nothing.
        combat.CurrentSide = CombatSide.Player;
        Assert.False(AlicesTeapot.TakeFor(klee.Creature, Element.Pyro));
        Give<AlicesTeapot>(klee);

        // Her turn: the first Bomb, and not the second.
        Assert.True(AlicesTeapot.Pending(klee.Creature));
        Assert.True(AlicesTeapot.TakeFor(klee.Creature, Element.Pyro));
        Assert.False(AlicesTeapot.TakeFor(klee.Creature, Element.Pyro));

        // The enemy turn after it is the same round (designer ruling
        // 2026-09-27, as Dodoco Tales reads "each turn"): already spent.
        combat.CurrentSide = CombatSide.Enemy;
        Assert.False(AlicesTeapot.Pending(klee.Creature));
        Assert.False(AlicesTeapot.TakeFor(klee.Creature, Element.Pyro));

        // A round where her turn set nothing off: a Mine going off on the
        // enemies' turn takes it, so the Mine badge's "with Vaporize" is true.
        combat.RoundNumber = 2;
        combat.CurrentSide = CombatSide.Enemy;
        Assert.True(AlicesTeapot.Pending(klee.Creature));
        Assert.True(AlicesTeapot.TakeFor(klee.Creature, Element.Pyro));
        Assert.False(AlicesTeapot.TakeFor(klee.Creature, Element.Pyro));

        // Hydro on Hydro is no reaction: not taken.
        combat.RoundNumber = 3;
        combat.CurrentSide = CombatSide.Player;
        Assert.False(AlicesTeapot.TakeFor(klee.Creature, Element.Hydro));
    }

    [Fact]
    public void Alices_teapot_reacts_through_the_one_funnel_and_consumes_nothing_real()
    {
        // STRUCTURAL (the hit is a `CreatureCmd.Damage`): the explosion asks
        // the Teapot BEFORE its hit and hands the Hydro to `DealAsIfAura`,
        // which resolves the reaction at the one site every reaction passes
        // and never finds, refreshes, applies or removes a real aura.
        var explode = Il.CallSequence(Il.Method("ProtoBombPower", "Explode")).ToList();
        Assert.True(explode.IndexOf("AlicesTeapot.TakeFor")
                    < explode.IndexOf("ElementalHit.DealAsIfAura"));
        var hit = Il.Calls(Il.Method("ElementalHit", "DealAsIfAura"));
        Assert.Contains("ReactionEffects.Resolve", hit);
        Assert.Contains("ReactionTable.AmplifierMultiplier", hit);
        Assert.DoesNotContain("AuraCmd.Find", hit);
        Assert.DoesNotContain("AuraCmd.Apply", hit);
        Assert.DoesNotContain("AuraCmd.Refresh", hit);
        Assert.DoesNotContain("PowerCmd.Remove", hit);
        Assert.Equal(Reaction.Vaporize, ReactionTable.Lookup(Element.Hydro, Element.Pyro));
    }

    [Fact]
    public void Alices_teapot_folds_its_vaporize_into_the_bomb_badge_until_spent()
    {
        using var arm = new KleeArm();
        var klee = Seat.Klee();
        var enemy = Enemy();
        var combat = ProtoBombs.Board(klee.Creature, enemy);
        combat.RoundNumber = 1;
        combat.CurrentSide = CombatSide.Player;
        var pile = ProtoBombs.Place(enemy, klee.Creature, new ProtoBombs.Charge(10),
                                    new ProtoBombs.Charge(4));
        Assert.Equal(14, pile.PredictedSetOffDamage());
        Assert.Equal("None", LiveReaction(pile));

        Give<AlicesTeapot>(klee);
        Assert.True(AlicesTeapot.Pending(klee.Creature));
        // The first charge meets the Hydro that is not there; the one behind
        // it lands on a bare body, as with a real aura (`EB-559`).
        var vaporized = (int)(10m * ReactionConstants.VaporizeMult) + 4;
        Assert.Equal(vaporized, pile.PredictedSetOffDamage());
        Assert.Equal("Vaporize", LiveReaction(pile));

        // And on the enemies' turn while this round's is unspent (designer
        // ruling 2026-09-27): a Mine going off there takes it, so its badge's
        // "with Vaporize" is true.
        combat.CurrentSide = CombatSide.Enemy;
        Assert.Equal(vaporized, pile.PredictedSetOffDamage());

        // Spent this turn: back to the plain number; the next turn, again.
        combat.CurrentSide = CombatSide.Player;
        Assert.True(AlicesTeapot.TakeFor(klee.Creature, Element.Pyro));
        Assert.Equal(14, pile.PredictedSetOffDamage());
        combat.RoundNumber = 2;
        Assert.Equal(vaporized, pile.PredictedSetOffDamage());
    }

    [Fact]
    public void Alices_teapot_leaves_the_real_aura_for_the_next_bomb()
    {
        // The Teapot's pretend Hydro consumes nothing real (`Explode`), so the
        // charge behind it meets the enemy's real Hydro and Vaporizes too;
        // with the Vermillion Pact held, that aura is then kept for the rest.
        using var arm = new KleeArm();
        var klee = Seat.Klee();
        var hydro = Seat.Klee(40).WithPower<HydroAuraPower>(2);
        Seat.Force(hydro.Creature, "Side", CombatSide.Enemy);
        var combat = ProtoBombs.Board(klee.Creature, hydro.Creature);
        combat.RoundNumber = 1;
        combat.CurrentSide = CombatSide.Player;
        var pile = ProtoBombs.Place(hydro.Creature, klee.Creature,
            new ProtoBombs.Charge(10), new ProtoBombs.Charge(4),
            new ProtoBombs.Charge(4));
        Give<AlicesTeapot>(klee);
        Assert.True(AlicesTeapot.Pending(klee.Creature));

        int Vap(int size) => (int)(size * ReactionConstants.VaporizeMult);
        Assert.Equal(Vap(10) + Vap(4) + 4, pile.PredictedSetOffDamage());

        klee.WithPower<VermillionPactPower>(1);
        Assert.Equal(Vap(10) + Vap(4) + Vap(4), pile.PredictedSetOffDamage());
    }

    private static string LiveReaction(ProtoBombPower pile) =>
        typeof(ProtoBombPower).GetProperty("LiveReaction", HeadlessGame.All)!
            .GetValue(pile)!.ToString()!;

    [Fact]
    public void Dodoco_tales_pays_two_for_the_first_explosion_each_turn_and_one_after()
    {
        using var arm = new KleeArm();
        var klee = Seat.Klee();
        var enemy = Enemy();
        var combat = ProtoBombs.Board(klee.Creature, enemy);
        combat.RoundNumber = 1;
        Assert.Equal(2, ExplosiveFrags.SparksFor(klee.Creature));
        Assert.Equal(1, ExplosiveFrags.SparksFor(klee.Creature));
        Assert.Equal(1, ExplosiveFrags.SparksFor(klee.Creature));
        combat.RoundNumber = 2;
        Assert.Equal(2, ExplosiveFrags.SparksFor(klee.Creature));
        Assert.Contains("ExplosiveFrags.SparksFor",
                        Il.Calls(Il.Method("ExplosiveFrags", "OnBombExploded")));
    }

    [Fact]
    public void Dodoco_tales_keeps_its_shipped_body_with_the_arm_off()
    {
        // The detonation bus pays the shipped 1; only the arm's own explosion
        // bus reads the repair.
        var detonated = Il.Calls(Il.Method("ExplosiveFrags", "OnBombDetonated"));
        Assert.Contains("SparkPower.Gain", detonated);
        Assert.DoesNotContain("ExplosiveFrags.SparksFor", detonated);
        Assert.Equal(1, ExplosiveFrags.SparksPerDetonation);
    }

    [Fact]
    public void Blasting_powder_grows_every_one_of_her_bombs_six()
    {
        using var arm = new KleeArm();
        var klee = Seat.Klee();
        var other = Seat.Klee();
        var a = Enemy();
        var b = Enemy();
        ProtoBombs.Board(klee.Creature, a, b);
        var mine = ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(4),
                                    new ProtoBombs.Charge(2, IsMine: true));
        var there = ProtoBombs.Place(b, klee.Creature, new ProtoBombs.Charge(10));
        var theirs = ProtoBombs.Place(b, other.Creature, new ProtoBombs.Charge(7));

        BlastingPowder.Use(klee.Creature);
        Assert.Equal(new[] { 10, 8 }, mine.Charges.Select(c => c.Size));
        Assert.Equal(new[] { 16 }, there.Charges.Select(c => c.Size));
        Assert.Equal(new[] { 7 }, theirs.Charges.Select(c => c.Size));
    }

    [Fact]
    public void Jumpy_juice_doubles_every_one_of_her_bombs_and_sets_nothing_off()
    {
        using var arm = new KleeArm();
        var klee = Seat.Klee();
        var a = Enemy();
        ProtoBombs.Board(klee.Creature, a);
        var pile = ProtoBombs.Place(a, klee.Creature, new ProtoBombs.Charge(6),
                                    new ProtoBombs.Charge(3, IsMine: true));
        JumpyJuice.Use(klee.Creature);
        Assert.Equal(new[] { 12, 6 }, pile.Charges.Select(c => c.Size));
        Assert.Equal(new[] { false, true }, pile.Charges.Select(c => c.IsMine));

    }

    [Fact]
    public void Bottled_sparks_gains_three_sparks()
    {
        Assert.Equal(3, BottledSparks.Sparks);
        Assert.Contains("SparkPower.Gain", Il.Calls(Il.Method("BottledSparks", "OnUse")));
    }

    // ==== Furina (the re-founding, 2026-10-04, sec.10) =======================

    [Fact]
    public void Opera_glasses_start_each_combat_with_three_fanfare()
    {
        Assert.Equal(3, OperaGlasses.Fanfare);
        Assert.Contains("FurinaStage.Gain",
                        Il.Calls(Il.Method("OperaGlasses", "BeforeCombatStart")));
        Assert.Equal("Start each combat with [blue]3[/blue] [gold]Fanfare[/gold].",
                     Face(Canon<RelicModel>(typeof(OperaGlasses))));
    }

    [Fact]
    public void Stagehands_gloves_and_the_bouquet_reach_the_bow_through_the_mods()
    {
        using var _ = new StageArm();
        var seat = Seat.Furina().WithCombatState();
        Assert.Equal(0, FurinaStage.ModsOf(seat.Creature).BowBlock);
        Assert.Equal(1, FurinaStage.ModsOf(seat.Creature).BowActs);
        Give<StagehandsGloves>(seat);
        Give<CurtainCallBouquet>(seat);
        var mods = FurinaStage.ModsOf(seat.Creature);
        Assert.Equal(3, mods.BowBlock);
        Assert.Equal(2, mods.BowActs);
        // The Bow: its act (twice), its Fanfare, then the Gloves' Block.
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Seat(StagePerformer.Usher);
        var board = new RecordingBoard();
        StageKit.Run(new StageDirector(stage, board).FinalBow(0));
        Assert.Equal(new[] { "block Usher 4", "block Usher 4", "gloves 3" },
                     board.Log);
        Assert.Equal(1, stage.Fanfare);
    }

    [Fact]
    public void Guest_book_gives_three_on_the_first_guest_star_of_the_combat_only()
    {
        using var _ = new StageArm();
        var seat = Seat.Furina().WithCombatState();
        Assert.Equal(0, GuestBook.BonusFor(seat.Creature));
        Give<GuestBook>(seat);
        Assert.Equal(3, GuestBook.BonusFor(seat.Creature));
        var stage = FurinaStageLedger.For(seat.Creature);
        StageKit.Run(new StageDirector(stage, new RecordingBoard())
            .SummonGuest(StagePerformer.Charlotte, 0, GuestBook.BonusFor(seat.Creature)));
        Assert.Equal(3, stage.Fanfare);
        Assert.Equal(0, GuestBook.BonusFor(seat.Creature));
        FurinaStageLedger.ResetAll();                       // the next combat
        Assert.Equal(3, GuestBook.BonusFor(seat.Creature));
        Assert.Contains("GuestBook.BonusFor",
                        Il.Calls(Il.Method("FurinaStage", "GuestStar")));
    }

    [Fact]
    public void Grand_theater_program_gains_one_fanfare_each_turn()
    {
        Assert.Equal(1, GrandTheaterProgram.Fanfare);
        Assert.Equal("At the start of your turn, gain [blue]1[/blue] "
                     + "[gold]Fanfare[/gold].",
                     Face(Canon<RelicModel>(typeof(GrandTheaterProgram))));
        var start = Il.CallSequence(Il.Method("FurinaStage", "TurnStart")).ToList();
        Assert.Contains("FurinaStageRelics.Count<GrandTheaterProgram>", start);
        Assert.Contains("FurinaStage.Gain", start);
    }

    [Fact]
    public void Palais_ledger_takes_one_off_a_spend_n()
    {
        using var _ = new StageArm();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Gain(2);
        Assert.Equal(3, FurinaStage.PriceOf(seat.Creature, 3));
        Assert.False(FurinaStage.CanSpend(seat.Creature, 3));
        Give<PalaisLedger>(seat);
        Assert.Equal(2, FurinaStage.PriceOf(seat.Creature, 3));
        Assert.Equal(0, FurinaStage.PriceOf(seat.Creature, 1));
        Assert.True(FurinaStage.CanSpend(seat.Creature, 3));
        Assert.Contains("FurinaStage.PriceOf",
                        Il.Calls(Il.Method("FurinaStage", "CanSpend")));
        Assert.Contains("FurinaStage.PriceOf",
                        Il.Calls(Il.Method("FurinaStage", "Spend")));
    }

    [Fact]
    public void Opening_night_summons_a_random_performer_behind_usher_after_the_opening()
    {
        Assert.Equal(RelicRarity.Shop, Canon<RelicModel>(typeof(OpeningNight)).Rarity);
        var late = Il.CallSequence(Il.Method("OpeningNight", "BeforeCombatStartLate")).ToList();
        Assert.True(late.IndexOf("FurinaStage.OpenCombat") >= 0);
        Assert.True(late.IndexOf("FurinaStage.OpenCombat") < late.IndexOf("FurinaStage.Summon"));
        Assert.Contains("random", Il.Strings(Il.Method("OpeningNight", "BeforeCombatStartLate")));
        Assert.Equal(typeof(SalonSolitaire),
            typeof(SalonSolitaire).GetMethod("BeforeCombatStart")!.DeclaringType);

        using var _ = new StageArm();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Open();
        stage.Seat(StagePerformer.Crabaletta);
        Assert.Equal(new[] { StagePerformer.Usher, StagePerformer.Crabaletta },
                     stage.Seats.Select(s => s.Who));
    }

    [Fact]
    public void The_curtain_never_falls_opens_usher_and_gives_one_rehearsal()
    {
        Assert.Equal(1, CurtainNeverFalls.Rehearsal);
        var open = Il.CallSequence(Il.Method("CurtainNeverFalls", "BeforeCombatStart")).ToList();
        Assert.Contains("FurinaStage.OpenCombat", open);
        Assert.Contains(open, c => c.StartsWith("PowerCmd.Apply<RehearsalPower>"));
        Assert.Equal("Start each combat with [gold]Usher[/gold] on stage and "
                     + "[blue]1[/blue] [gold]Rehearsal[/gold].",
                     Face(Canon<RelicModel>(typeof(CurtainNeverFalls))));
        Assert.Equal("Start each combat with [gold]Usher[/gold] on stage.",
                     Face(Canon<RelicModel>(typeof(SalonSolitaire))));
        // Touch of Orobas upgrades the Stage's starter into it.
        Assert.Contains("ModelDb.Relic<CurtainNeverFalls>",
                        Il.CallSequence(Il.Method("SalonSolitaire", "GetUpgradeReplacement")));
    }

    [Fact]
    public void Both_stage_starters_carry_the_companion_slot()
    {
        // 2026-09-27, [USER]'s co-op run: a Stage Furina never saw the fourth
        // reward choice. Salon Solitaire and its upgrade both roll the slot.
        foreach (var type in new[] { "SalonSolitaire", "CurtainNeverFalls" })
        {
            var calls = Il.Calls(Il.Method(type, "TryModifyCardRewardOptions"));
            Assert.Contains("CompanionSlot.Roll", calls);
        }
    }

    [Fact]
    public void The_furina_potions_gain_fanfare_gain_rehearsal_and_act_twice_now()
    {
        // The re-founding (sec.10): "Gain 6 Fanfare.", "Gain 1 Rehearsal.",
        // Encore Elixir unchanged.
        Assert.Contains("FurinaStage.Gain",
                        Il.Calls(Il.Method("BottledApplause", "OnUse")));
        Assert.Contains(Il.CallSequence(Il.Method("CurtainWater", "OnUse")),
                        c => c.StartsWith("PowerCmd.Apply<RehearsalPower>"));
        Assert.Contains("FurinaStage.PerformAll",
                        Il.Calls(Il.Method("EncoreElixir", "OnUse")));
        Assert.Equal((6, 1, 2), (BottledApplause.Fanfare, CurtainWater.Rehearsal,
                                 EncoreElixir.Acts));
    }

    // ==== helpers ============================================================

    private sealed class KleeArm : IDisposable
    {

        internal KleeArm()
        {
            KleeOverhaulLedger.ResetAll();
        }

        public void Dispose()
        {
            KleeOverhaulLedger.ResetAll();
        }
    }

    private sealed class StageArm : IDisposable
    {

        internal StageArm()
        {
            FurinaStageLedger.ResetAll();
        }

        public void Dispose()
        {
            FurinaStageLedger.ResetAll();
        }
    }

    /// <summary>A relic or a potion to READ (its rarity, its face): the
    /// constructor is never run, because it runs the model's type initializer
    /// and `RelicModel`'s holds a Godot `StringName` -- process death
    /// headless (README, the headless boundary).</summary>
    private static T Canon<T>(Type type) where T : class =>
        (T)RuntimeHelpers.GetUninitializedObject(type);

    private static IEnumerable<Type> Silent() => new[]
    {
        typeof(SilentRelics.NinjaScroll), typeof(SilentRelics.PaperKrane),
        typeof(SilentRelics.RingOfTheSnake), typeof(SilentRelics.Tingsha),
        typeof(SilentRelics.ToughBandages), typeof(SilentRelics.TwistedFunnel),
    };

    private static List<RelicModel> KleeMembers() =>
        Silent().Append(typeof(PoundingSurprise)).Append(typeof(ExplosiveFrags))
            .Concat(KleeArmRelics.Types).Select(Uninit).ToList();

    private static RelicModel Uninit(Type type) =>
        (RelicModel)RuntimeHelpers.GetUninitializedObject(type);

    private static T Pool<T>(List<RelicModel> members) where T : RelicPoolModel
    {
        var pool = (T)RuntimeHelpers.GetUninitializedObject(typeof(T));
        SetField(pool, "_relics", members);
        return pool;
    }

    private static List<Type> Types(IEnumerable<RelicModel> relics) =>
        relics.Select(r => r.GetType()).ToList();

    private static T Give<T>(Seat seat) where T : RelicModel
    {
        var relic = (T)RuntimeHelpers.GetUninitializedObject(typeof(T));
        Seat.Set(relic, "IsMutable", true);
        // Through the property's own setter: a reflective FIELD write runs
        // `RelicModel`'s type initializer (a Godot `StringName`), which kills
        // the test host.
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

    /// <summary>A relic's or potion's printed face.</summary>
    private static string Face(AbstractModel model) =>
        ((ILocalizationProvider)model).Localization!
            .Single(r => r.Item1 == "description").Item2;

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

    /// <summary>
    /// The `relocated` argument each call to <c>ProtoBombPower.Place</c> in
    /// <paramref name="method"/> passes, read off the IL: the last argument is
    /// loaded by the instruction just before the call, <c>ldc.i4.1</c> (0x17)
    /// for true and <c>ldc.i4.0</c> (0x16) for false.
    /// </summary>
    private static List<bool> PlaceFlags(string method)
    {
        var bodies = (IEnumerable<MethodBase>)typeof(Il)
            .GetMethod("Bodies", HeadlessGame.All)!
            .Invoke(null, new object[] { Il.Method("ProtoBombPower", method) })!;
        var flags = new List<bool>();
        foreach (var body in bodies)
        {
            var il = body.GetMethodBody()?.GetILAsByteArray();
            if (il == null) continue;
            for (var i = 1; i + 5 <= il.Length; i++)
            {
                if (il[i] != 0x28) continue;
                MethodBase? target;
                try
                {
                    target = body.Module.ResolveMethod(BitConverter.ToInt32(il, i + 1));
                }
                catch
                {
                    continue;
                }
                if (target?.Name != "Place" || target.DeclaringType != typeof(ProtoBombPower))
                {
                    continue;
                }
                Assert.True(il[i - 1] == 0x16 || il[i - 1] == 0x17,
                            $"{method}: the argument before Place is 0x{il[i - 1]:X2}");
                flags.Add(il[i - 1] == 0x17);
            }
        }
        Assert.NotEmpty(flags);
        return flags;
    }
}
