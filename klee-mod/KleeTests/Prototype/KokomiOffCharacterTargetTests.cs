#nullable enable
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Characters;
using MegaCrit.Sts2.Core.Models.Monsters;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE OFF-CHARACTER AUDIT (2026-10-04): Kokomi's cards in another
/// character's hand (Splash, Kaleidoscope, Prismatic Gem, Orobas's Sea Glass).
///
/// Three defects, three guards: a pet-or-enemy card could be aimed at (or
/// auto-played onto) Osty or a performer; an auto-play with no legal target
/// reached a now-line's <c>ThrowIfNull</c>; and a Plan-only card with no
/// Kurage looked playable. What is REAL here: the four target predicates on
/// real creatures and real seats, BaseLib's auto-play filter run over them,
/// the no-Kurage test on a real <c>PlayerCombatState</c>, and both patches'
/// decisions on real generated cards. What is STRUCTURAL: the Harmony
/// ordering, since <c>CardCmd.AutoPlay</c> needs a live combat.
///
/// THE ENUM VALUES. BaseLib assigns <c>[CustomEnum]</c> fields in its
/// <c>ModelDb.Init</c> prefix, which the headless host never runs, so here
/// they all read <c>TargetType.None</c>. The tests that need the spellings
/// told apart assign distinct values for their own duration
/// (<see cref="WithDistinctSpellings"/>) and put them back; test
/// parallelisation is off for the whole assembly (HeadlessGame.cs).
/// </summary>
public class KokomiOffCharacterTargetTests
{
    // ---- creatures --------------------------------------------------------

    private static Creature Bare(int hp = 10)
    {
        var ctor = typeof(Creature).GetConstructors(HeadlessGame.All)
            .First(c => c.GetParameters().Length == 3
                        && c.GetParameters()[0].ParameterType == typeof(Player));
        return (Creature)ctor.Invoke(new object?[] { null, hp, hp });
    }

    private static Creature Enemy()
    {
        var enemy = Bare(40);
        Seat.Force(enemy, "Side", CombatSide.Enemy);
        return enemy;
    }

    /// <summary>A pet of <paramref name="owner"/>'s, wearing a monster of
    /// type <paramref name="monster"/> (null: a pet with no monster model,
    /// standing in for a performer), registered in the seat's own pet list
    /// the way <c>PlayerCmd.AddPet</c> leaves it.</summary>
    private static Creature PetOf(Seat owner, Type? monster)
    {
        var pet = Bare();
        if (monster != null)
        {
            Seat.Force(pet, "Monster",
                RuntimeHelpers.GetUninitializedObject(monster));
        }
        pet.PetOwner = owner.Player;
        if (owner.Player.PlayerCombatState is { } state)
        {
            ((List<Creature>)typeof(PlayerCombatState)
                .GetField("_pets", HeadlessGame.All)!
                .GetValue(state)!).Add(pet);
        }
        return pet;
    }

    private static Creature Osty(Seat owner) => PetOf(owner, typeof(Osty));
    private static Creature Performer(Seat owner) => PetOf(owner, null);
    private static Creature Kurage(Seat owner) =>
        PetOf(owner, typeof(BakeKurageMonster));

    /// <summary>BaseLib's <c>AutoPlayCustomTargetPatch</c> bag, verbatim:
    /// every live creature the type's predicate accepts.</summary>
    private static List<Creature> Bag(IEnumerable<Creature> creatures,
                                      Func<Creature, Player, bool> predicate,
                                      Player player) =>
        creatures.Where(c => c.IsAlive && predicate(c, player)).ToList();

    // ---- defect 1: the pet half is the Bake-Kurage alone -------------------

    [Fact]
    public void Off_Kokomi_no_spelling_can_aim_at_Osty_or_a_performer()
    {
        var necro = Seat.Of(new Necrobinder()).WithCombatState();
        var osty = Osty(necro);
        var furina = Seat.Furina().WithCombatState();
        var performer = Performer(furina);

        foreach (var (seat, pet) in new[] { (necro, osty), (furina, performer) })
        {
            Assert.False(CanTargetPetOrEnemy(pet, seat.Player));
            Assert.False(CanTargetPetOrAlly(pet, seat.Player));
            Assert.False(CanTargetKurageOnly(pet, seat.Player));
            Assert.False(CanTargetKurageOrSelf(pet, seat.Player));
        }

        // The other halves are untouched: an enemy, the player herself.
        var enemy = Enemy();
        Assert.True(CanTargetPetOrEnemy(enemy, necro.Player));
        Assert.True(CanTargetKurageOrSelf(necro.Creature, necro.Player));
        Assert.True(CanTargetPetOrAlly(furina.Creature, necro.Player));
    }

    [Fact]
    public void An_auto_play_off_Kokomi_rolls_the_enemy_and_never_the_pet()
    {
        // Vanguard auto-played by a Necrobinder: BaseLib's bag over the whole
        // board holds the enemy and NOT Osty, so the Vulnerable cannot land
        // on him (the audit's `ProtoKkVanguard.cs:97` case).
        var necro = Seat.Of(new Necrobinder()).WithCombatState();
        var osty = Osty(necro);
        var enemy = Enemy();
        var board = new[] { necro.Creature, osty, enemy };

        Assert.Equal(new[] { enemy },
            Bag(board, CanTargetPetOrEnemy, necro.Player));
        // Kelp Wall's spelling rolls the player, never the pet.
        Assert.Equal(new[] { necro.Creature },
            Bag(board, CanTargetKurageOrSelf, necro.Player));
        // A Plan-only card's bag is empty: nobody to aim at.
        Assert.Empty(Bag(board, CanTargetKurageOnly, necro.Player));
    }

    [Fact]
    public void On_Kokomi_her_jellyfish_is_still_a_target_of_every_spelling()
    {
        var kokomi = Seat.Kokomi().WithCombatState();
        var kurage = Kurage(kokomi);

        Assert.True(CanTargetPetOrEnemy(kurage, kokomi.Player));
        Assert.True(CanTargetPetOrAlly(kurage, kokomi.Player));
        Assert.True(CanTargetKurageOnly(kurage, kokomi.Player));
        Assert.True(CanTargetKurageOrSelf(kurage, kokomi.Player));

        // ... and only HER jellyfish: a co-op partner's cards cannot reach it.
        var partner = Seat.Klee().WithCombatState();
        Assert.False(CanTargetPetOrEnemy(kurage, partner.Player));
        Assert.False(CanTargetKurageOnly(kurage, partner.Player));
    }

    // ---- defect 2: an auto-play with no legal target does not play --------

    [Fact]
    public void An_auto_play_with_no_target_is_refused_for_the_three_spellings_that_need_one()
    {
        WithDistinctSpellings(() =>
        {
            var vanguard = new ProtoKkVanguard();        // PetOrEnemy
            var jointOrders = new ProtoKkJointOrders();  // PetOrAlly
            var breakwater = new ProtoKkBreakwater();    // PetOnly
            var kelpWall = new ProtoKkKelpWall();        // PetOrSelf

            Assert.True(NoLegalTarget(vanguard, null));
            Assert.True(NoLegalTarget(jointOrders, null));
            Assert.True(NoLegalTarget(breakwater, null));
            // Its self half is always there; BaseLib's roll finds the player.
            Assert.False(NoLegalTarget(kelpWall, null));

            // A filled target is never refused.
            Assert.False(NoLegalTarget(vanguard, Enemy()));
        });
    }

    [Fact]
    public void An_unassigned_spelling_never_refuses_a_Power()
    {
        // The headless host is exactly the boot that skipped BaseLib's
        // assignment: every spelling reads `None`, which is every Power's
        // target type. The guards must stand down rather than refuse them.
        Assert.False(NeedsACreature(TargetType.None));
        Assert.False(IsPlanOnly(TargetType.None));
    }

    [Fact]
    public void The_refusal_runs_after_both_target_fills()
    {
        var patch = typeof(KokomiPlan).Assembly
            .GetType("KleeMod.Powers.AutoPlayWithNoKokomiTargetPatch")!;
        var attrs = patch.GetCustomAttributesData();
        Assert.Contains("BaseLib", patch.GetCustomAttributes(false)
            .OfType<HarmonyLib.HarmonyAfter>().Single().info.after);
        Assert.Contains(attrs.First(a => a.AttributeType.Name == "HarmonyPatch")
                .ConstructorArguments,
            a => a.Value is Type t && t.Name == "CardCmd");
        var prefix = patch.GetMethod("Prefix", HeadlessGame.All)!;
        var priority = prefix.GetCustomAttributesData()
            .First(a => a.AttributeType.Name == "HarmonyPriority");
        Assert.Equal(HarmonyLib.Priority.Last,
            (int)priority.ConstructorArguments[0].Value!);
    }

    // ---- defect 3: a Plan-only card with no Kurage is unplayable ----------

    [Fact]
    public void A_Plan_only_card_off_Kokomi_is_greyed_with_or_without_another_pet()
    {
        WithDistinctSpellings(() =>
        {
            var necro = Seat.Of(new Necrobinder()).WithCombatState();
            var card = Owned(new ProtoKkBreakwater(), necro);
            Assert.True(PlanOnlyUnplayable(card));      // no pet at all

            Osty(necro);
            Assert.True(PlanOnlyUnplayable(card));      // Osty is not the Kurage

            // A pet-or-enemy card is not greyed: it still has the enemy.
            Assert.False(PlanOnlyUnplayable(Owned(new ProtoKkVanguard(), necro)));
        });
    }

    [Fact]
    public void A_Plan_only_card_on_Kokomi_is_playable()
    {
        WithDistinctSpellings(() =>
        {
            var kokomi = Seat.Kokomi().WithCombatState();
            Kurage(kokomi);
            Assert.False(PlanOnlyUnplayable(Owned(new ProtoKkBreakwater(), kokomi)));
            Assert.False(LacksTheKurage(kokomi.Player));
        });
    }

    // ---- helpers ----------------------------------------------------------

    // The predicates are `internal`; reached by reflection rather than made
    // public, on `PetTargetReachTests`' precedent.
    private static readonly Func<Creature, Player, bool> CanTargetPetOrEnemy =
        Pred("CanTargetPetOrEnemy");
    private static readonly Func<Creature, Player, bool> CanTargetPetOrAlly =
        Pred("CanTargetPetOrAlly");
    private static readonly Func<Creature, Player, bool> CanTargetKurageOnly =
        Pred("CanTargetKurageOnly");
    private static readonly Func<Creature, Player, bool> CanTargetKurageOrSelf =
        Pred("CanTargetKurageOrSelf");

    private static Func<Creature, Player, bool> Pred(string name)
    {
        var method = Il.Method("KokomiTargets", name);
        return (c, p) => (bool)method.Invoke(null, new object[] { c, p })!;
    }

    private static bool NeedsACreature(TargetType type) =>
        (bool)Il.Method("KokomiTargets", "NeedsACreature")
            .Invoke(null, new object[] { type })!;

    private static bool IsPlanOnly(TargetType type) =>
        (bool)Il.Method("KokomiTargets", "IsPlanOnly")
            .Invoke(null, new object[] { type })!;

    private static bool LacksTheKurage(Player player) =>
        (bool)Il.Method("KokomiTargets", "LacksTheKurage")
            .Invoke(null, new object[] { player })!;

    private static bool NoLegalTarget(CardModel card, Creature? target) =>
        (bool)Il.Method("AutoPlayWithNoKokomiTargetPatch", "HasNoLegalTarget")
            .Invoke(null, new object?[] { card, target })!;

    private static bool PlanOnlyUnplayable(CardModel card) =>
        (bool)Il.Method("PlanOnlyNeedsTheKuragePatch", "Unplayable")
            .Invoke(null, new object?[] { card })!;

    private static CardModel Owned(CardModel card, Seat seat)
    {
        // The game's ToMutable runs through ModelDb, outside the headless
        // boundary; set the flag it would have set, then the owner.
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", seat.Player);
        return card;
    }

    /// <summary>Give the four spellings distinct values for one test (cards
    /// read the value at construction, so build them inside), then put the
    /// headless host's values back.</summary>
    private static void WithDistinctSpellings(Action body)
    {
        var saved = (KokomiTargets.PetOrEnemy, KokomiTargets.PetOrAlly,
                     KokomiTargets.KurageOnly, KokomiTargets.KurageOrSelf);
        try
        {
            KokomiTargets.PetOrEnemy = (TargetType)9001;
            KokomiTargets.PetOrAlly = (TargetType)9002;
            KokomiTargets.KurageOnly = (TargetType)9003;
            KokomiTargets.KurageOrSelf = (TargetType)9004;
            body();
        }
        finally
        {
            (KokomiTargets.PetOrEnemy, KokomiTargets.PetOrAlly,
             KokomiTargets.KurageOnly, KokomiTargets.KurageOrSelf) = saved;
        }
    }
}
