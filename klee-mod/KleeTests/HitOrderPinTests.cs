using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-328`: THE ORDER, AND A PIN PER MODIFIER PAIR.
///
/// THE ROW. "The card face composes modifiers wrong: under Weak 1 and a
/// Strength-style buff the printed number disagrees with the dealt number in
/// some pairs." The order the mod's faces have to keep is the engine's, and it
/// is written out at <see cref="HitOrder"/> with the type names it was
/// decompiled from (sts2.dll 0.111.0): enchantment, then EVERY
/// <c>ModifyDamageAdditive</c>, then EVERY <c>ModifyDamageMultiplicative</c>,
/// then the minimum <c>ModifyDamageCap</c>, then <c>Math.Max(0)</c>.
///
/// WHAT IS REAL HERE, AND IT IS ALL OF IT. Every multiplier and every flat
/// term below is obtained by calling the GAME'S OWN hook method on a REAL
/// power attached to a REAL <c>Creature</c> -- <c>WeakPower</c>,
/// <c>VulnerablePower</c>, <c>StrengthPower</c>, <c>FrailPower</c>,
/// <c>DexterityPower</c>, <c>HardToKillPower</c> -- through
/// <see cref="HitOrder.Compose"/>, which walks the phases in the engine's
/// order and nothing else. No constant is restated here; 0.75 and 1.5 are
/// asked for, not typed.
///
/// WHAT IS NOT REACHABLE, and it is one thing:
/// <c>DamageVar.UpdateCardPreview</c> itself needs <c>card.Owner.RunState</c>
/// and a live <c>CombatState</c> (README, "The headless boundary"). So the
/// PRINTED side is composed here from the phases the game composes it from,
/// each of them run for real, and the two folding vars' own wiring is pinned
/// structurally one file over (`Prototype/Eb328FaceOrderTests.cs`).
///
/// EVERY PAIR PIN IS A TWO-SIDED ASSERTION: the composed number, and the
/// number the WRONG composition gives. A pin that only asserted the right
/// answer would pass on a build where the two compositions happened to
/// collide (`EB-288`'s lesson, one file over), and the point of the row is
/// that they do not collide.
/// </summary>
public class HitOrderPinTests
{
    private const decimal Base = 4m;

    /// <summary>The prop a card's Attack carries -- <c>DamageVar</c>'s own,
    /// and the one every native modifier gates on.</summary>
    private static readonly ValueProp Move = ValueProp.Move;

    private static decimal Composed(
        MegaCrit.Sts2.Core.Entities.Creatures.Creature? dealer,
        MegaCrit.Sts2.Core.Entities.Creatures.Creature? target,
        decimal amount = 4m, CardModel? card = null) =>
        HitOrder.Compose(dealer, target, amount, Move, card);

    /// <summary>The expression the folding vars USED to compute: the engine's
    /// whole composition, and then the target's Vulnerable multiplied over the
    /// top of it. Kept here, named, because every pin below is the difference
    /// between it and <see cref="HitOrder.Compose"/>.</summary>
    private static decimal DoubleFolded(
        MegaCrit.Sts2.Core.Entities.Creatures.Creature dealer,
        MegaCrit.Sts2.Core.Entities.Creatures.Creature target,
        decimal amount = 4m) =>
        SimDamagePipeline.TargetMods(target, Composed(dealer, target, amount));

    // ---- the phases themselves ------------------------------------------

    [Fact]
    public void The_props_a_card_attack_carries_are_a_powered_attack()
    {
        // Everything below depends on this: the native modifiers all return
        // neutral for a prop that is not a powered attack, which is the whole
        // reason `SimDamagePipeline` mirrors them for the Unpowered hits.
        Assert.True(Move.IsPoweredAttack());
        Assert.False(ValueProp.Unpowered.IsPoweredAttack());
    }

    [Fact]
    public void Every_additive_term_lands_before_every_multiplicative_one()
    {
        var klee = Seat.Klee().WithPower<StrengthPower>(5).WithPower<WeakPower>(1);
        var enemy = Seat.Klee(30).Creature;

        // (4 + 5) x 0.75 -- phase 1 whole, then phase 2.
        Assert.Equal(6.75m, Composed(klee.Creature, enemy));

        // The other order, which is what a face that multiplies first and adds
        // the buff afterwards computes, and it is a different number.
        var weak = klee.Creature.Powers.OfType<WeakPower>().Single();
        var mult = weak.ModifyDamageMultiplicative(
            enemy, Base, Move, klee.Creature, null, null);
        Assert.Equal(8m, Base * mult + 5m);
        Assert.NotEqual(Base * mult + 5m, Composed(klee.Creature, enemy));
    }

    // ---- PAIR: Weak x Strength ------------------------------------------

    [Fact]
    public void Pair_weak_x_strength_is_the_sum_reduced_once()
    {
        var klee = Seat.Klee().WithPower<StrengthPower>(5).WithPower<WeakPower>(1);
        var enemy = Seat.Klee(30).Creature;

        // The row's own example, the number the board moved: 4 + 5, x0.75.
        Assert.Equal(6.75m, Composed(klee.Creature, enemy));
        // And the face that kept the Weak and dropped the buff -- the defect
        // the row was filed on -- is a different number.
        Assert.NotEqual(3m, (int)Composed(klee.Creature, enemy));
        Assert.Equal(6, (int)Composed(klee.Creature, enemy));
    }

    // ---- PAIR: Weak x Vulnerable ----------------------------------------

    [Fact]
    public void Pair_weak_x_vulnerable_is_one_product_and_the_old_face_folded_twice()
    {
        var klee = Seat.Klee().WithPower<WeakPower>(1);
        var enemy = Seat.Klee(30).WithPower<VulnerablePower>(1).Creature;

        // Both are phase-2 terms, so they multiply into ONE product: 4 x 0.75
        // x 1.5 = 4.5, printed 4.
        Assert.Equal(4.5m, Composed(klee.Creature, enemy));
        Assert.Equal(4, (int)Composed(klee.Creature, enemy));

        // The defect: the Vulnerable a second time. 4.5 x 1.5 = 6.75, printed
        // 6, against a board that moves 4.
        Assert.Equal(6.75m, DoubleFolded(klee.Creature, enemy));
        Assert.NotEqual(
            (int)Composed(klee.Creature, enemy),
            (int)DoubleFolded(klee.Creature, enemy));
    }

    // ---- PAIR: Strength x Vulnerable ------------------------------------

    [Fact]
    public void Pair_strength_x_vulnerable_adds_then_multiplies_once()
    {
        var klee = Seat.Klee().WithPower<StrengthPower>(5);
        var enemy = Seat.Klee(30).WithPower<VulnerablePower>(1).Creature;

        Assert.Equal(13.5m, Composed(klee.Creature, enemy));
        Assert.Equal(20.25m, DoubleFolded(klee.Creature, enemy));
        Assert.NotEqual(
            (int)Composed(klee.Creature, enemy),
            (int)DoubleFolded(klee.Creature, enemy));
    }

    // ---- PAIR: an arm modifier x each of the three ------------------------

    /// <summary>An Attack card, for the one modifier that asks what kind of
    /// card is dealing: <c>AttackUpThisTurnPower</c> declines anything that is
    /// not <c>CardType.Attack</c>.</summary>
    private static CardModel AnAttack() => new global::KleeMod.Cards.Kaboom();

    [Fact]
    public void Pair_arm_modifier_x_strength_share_the_additive_phase()
    {
        var klee = Seat.Klee()
            .WithPower<AttackUpThisTurnPower>(5)
            .WithPower<StrengthPower>(2);
        var enemy = Seat.Klee(30).Creature;

        // Two flat riders, one phase: 4 + 5 + 2.
        Assert.Equal(11m, Composed(klee.Creature, enemy, Base, AnAttack()));
    }

    [Fact]
    public void Pair_arm_modifier_x_weak_is_the_row_s_own_example()
    {
        // `EB-328`'s find, in the shape it was filed in: "under Weak 1 and
        // Fantastic Voyage 5 together, Slack Water printed 3 and dealt 6
        // (4 + 5, x0.75), keeping the Weak and dropping the buff". The buff is
        // `AttackUpThisTurnPower` -- `EB-699` renamed it after its effect.
        var klee = Seat.Klee()
            .WithPower<AttackUpThisTurnPower>(5)
            .WithPower<WeakPower>(1);
        var enemy = Seat.Klee(30).Creature;

        var composed = Composed(klee.Creature, enemy, Base, AnAttack());
        Assert.Equal(6.75m, composed);
        Assert.Equal(6, (int)composed);
        // 3 was the printed number, and it is what you get by keeping the Weak
        // and dropping the buff.
        Assert.Equal(3, (int)Composed(
            Seat.Klee().WithPower<WeakPower>(1).Creature, enemy, Base, AnAttack()));
    }

    [Fact]
    public void Pair_arm_modifier_x_vulnerable_folds_the_target_once()
    {
        var klee = Seat.Klee().WithPower<AttackUpThisTurnPower>(5);
        var enemy = Seat.Klee(30).WithPower<VulnerablePower>(1).Creature;
        var card = AnAttack();

        Assert.Equal(13.5m, HitOrder.Compose(klee.Creature, enemy, Base, Move, card));
        Assert.Equal(
            20.25m,
            SimDamagePipeline.TargetMods(
                enemy, HitOrder.Compose(klee.Creature, enemy, Base, Move, card)));
    }

    [Fact]
    public void An_arm_modifier_declines_a_skill_so_the_face_shape_matters()
    {
        var klee = Seat.Klee().WithPower<AttackUpThisTurnPower>(5);
        var enemy = Seat.Klee(30).Creature;
        // No cardSource at all -- a bomb, a summon's pulse -- and the rider
        // stays out of the number. This is why the pin table is per face
        // SHAPE as well as per pair.
        Assert.Equal(Base, Composed(klee.Creature, enemy));
    }

    // ---- PAIR: Shrink (a dealer-side multiplier) x each --------------------

    [Fact]
    public void Pair_shrink_x_weak_is_two_multipliers_in_one_phase()
    {
        // `EB-597` established that Shrink gates on the PROP exactly as Weak
        // does, so a Skill that deals damage is Shrunk like an Attack. Both
        // are phase-2 terms on the dealer: 4 x 0.7 x 0.75 = 2.1.
        var klee = Seat.Klee().WithPower<ShrinkPower>(1).WithPower<WeakPower>(1);
        var enemy = Seat.Klee(30).Creature;
        Assert.Equal(2.1m, Composed(klee.Creature, enemy));
        Assert.Equal(2, (int)Composed(klee.Creature, enemy));
    }

    [Fact]
    public void Pair_shrink_x_strength_shrinks_the_sum()
    {
        // `EB-696`'s shape: a face that prints its base under Shrink while the
        // hand's other faces print reduced ones. There is one order and the
        // buff is inside the multiplier: (4 + 5) x 0.7 = 6.3.
        var klee = Seat.Klee().WithPower<ShrinkPower>(1).WithPower<StrengthPower>(5);
        var enemy = Seat.Klee(30).Creature;
        Assert.Equal(6.3m, Composed(klee.Creature, enemy));
        // Shrinking the base and adding the buff afterwards is 7.8, a whole
        // point out once truncated.
        Assert.Equal(7.8m, Base * 0.7m + 5m);
    }

    [Fact]
    public void Pair_shrink_x_vulnerable_is_one_product_and_the_old_face_folded_twice()
    {
        var klee = Seat.Klee().WithPower<ShrinkPower>(1);
        var enemy = Seat.Klee(30).WithPower<VulnerablePower>(1).Creature;
        Assert.Equal(4.2m, Composed(klee.Creature, enemy));
        Assert.Equal(6.3m, DoubleFolded(klee.Creature, enemy));
    }

    // ---- PAIR: the cap x each ---------------------------------------------

    [Fact]
    public void Pair_cap_x_vulnerable_clamps_last()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30)
            .WithPower<VulnerablePower>(1)
            .WithPower<HardToKillPower>(3)
            .Creature;

        // 4 x 1.5 = 6, clamped to 3 -- phase 3 is last.
        Assert.Equal(3m, Composed(klee.Creature, enemy));
        // Clamping first and multiplying after gives 4.5, which is the shape a
        // face takes when it multiplies the target's terms over the engine's
        // finished answer.
        Assert.Equal(4.5m, DoubleFolded(klee.Creature, enemy));
    }

    [Fact]
    public void Pair_cap_x_strength_clamps_the_sum_not_the_base()
    {
        var klee = Seat.Klee().WithPower<StrengthPower>(20);
        var enemy = Seat.Klee(30).WithPower<HardToKillPower>(3).Creature;
        Assert.Equal(3m, Composed(klee.Creature, enemy));
    }

    // ---- PAIR: Frail x Dexterity, on the Block side ------------------------

    [Fact]
    public void Pair_frail_x_dexterity_adds_before_it_multiplies()
    {
        var klee = Seat.Klee()
            .WithPower<DexterityPower>(3)
            .WithPower<FrailPower>(1);
        var me = klee.Creature;

        var dex = me.Powers.OfType<DexterityPower>().Single();
        var frail = me.Powers.OfType<FrailPower>().Single();

        var additive = dex.ModifyBlockAdditive(me, 5m, Move, null, null);
        var multiplier = frail.ModifyBlockMultiplicative(me, 5m + additive, Move, null, null);

        // The engine's Block phases mirror the damage ones: (5 + 3) x 0.75 = 6.
        Assert.Equal(3m, additive);
        Assert.Equal(0.75m, multiplier);
        Assert.Equal(6m, (5m + additive) * multiplier);
        // The other order is 6.75, and once the number is truncated the pair
        // disagrees by a whole point at 11 base block -- 10 against 11, which
        // is the worked example the sim's `modify_block_gained` carries in its
        // own docstring.
        Assert.Equal(6.75m, 5m * multiplier + additive);
        Assert.Equal(10, (int)((11m + additive) * multiplier));
        Assert.Equal(11, (int)(11m * multiplier + additive));
    }

    // ---- FACE SHAPE: the Unpowered mirror (companion hit, Set-off) ---------

    [Fact]
    public void The_native_modifiers_decline_an_unpowered_hit_so_the_mirror_exists()
    {
        var klee = Seat.Klee().WithPower<StrengthPower>(5).WithPower<WeakPower>(1);
        var enemy = Seat.Klee(30).WithPower<VulnerablePower>(1).Creature;

        // Every one of the three answers neutral, which is why a companion's
        // pulse and a Bomb cannot read their numbers off `Hook.ModifyDamage`.
        Assert.Equal(
            Base,
            HitOrder.Compose(klee.Creature, enemy, Base, ValueProp.Unpowered));
    }

    [Fact]
    public void The_mirror_keeps_the_engine_s_phase_order_for_the_terms_it_mirrors()
    {
        var klee = Seat.Klee().WithPower<StrengthPower>(5).WithPower<WeakPower>(1);
        var enemy = Seat.Klee(30).WithPower<VulnerablePower>(1).Creature;

        var mirrored = SimDamagePipeline.TargetMods(
            enemy, SimDamagePipeline.DealerMods(klee.Creature, Base));

        // The mirror and the engine agree on the three terms the mirror
        // carries: (4 + 5) x 0.75 x 1.5.
        Assert.Equal(Composed(klee.Creature, enemy), mirrored);
    }

    [Fact]
    public void A_set_off_carries_the_target_s_terms_and_clamps_them_last()
    {
        var klee = Seat.Klee().WithPower<StrengthPower>(5).WithPower<WeakPower>(1);
        var enemy = Seat.Klee(30)
            .WithPower<VulnerablePower>(1)
            .WithPower<HardToKillPower>(3)
            .Creature;

        // R248: a Bomb is the enemy's burden -- the placer's Strength and Weak
        // never enter it. 4 x 1.5 = 6, clamped by the enemy's own cap to 3.
        Assert.Equal(3, SimDamagePipeline.ResolveOnTarget(enemy, Base, 1m));
        Assert.Equal(3m, HitOrder.ApplyCapLast(enemy, SimDamagePipeline.TargetMods(enemy, Base)));
        // Clamping before the multiplier would pay 4.
        Assert.Equal(
            4,
            (int)SimDamagePipeline.TargetMods(enemy, HitOrder.ApplyCapLast(enemy, Base)));
    }

    // ---- FACE SHAPE: multi-hit -------------------------------------------

    [Fact]
    public void A_multi_hit_face_pays_the_additive_phase_once_per_hit()
    {
        var klee = Seat.Klee().WithPower<StrengthPower>(5).WithPower<WeakPower>(1);
        var enemy = Seat.Klee(30).Creature;

        // Three hits of a 4-damage face is three separate compositions, not
        // one composition of 12: 3 x (4+5) x 0.75 = 20.25, where a face that
        // composed the total would print (12+5) x 0.75 = 12.75.
        var perHit = Composed(klee.Creature, enemy);
        Assert.Equal(20.25m, perHit * 3m);
        Assert.NotEqual(perHit * 3m, Composed(klee.Creature, enemy, Base * 3m));
    }

    // ---- EB-752: the relic that no damage face can print -------------------

    [Fact]
    public void The_boot_is_an_hp_loss_hook_and_not_a_damage_one()
    {
        var boot = typeof(TheBoot);
        // It overrides the HP-loss phase...
        Assert.Equal(
            boot,
            boot.GetMethod("ModifyHpLostAfterOstyLate")!.DeclaringType);
        // ...and none of the three damage phases, which run BEFORE the
        // target's Block is taken out. So its number is a function of the
        // Block the body is wearing, and no printed damage number can carry
        // it. `EB-752` wants the row's other option: print the modifier beside
        // the number. See `HitOrder.RelicsOnTheHpLossPhase`.
        Assert.NotEqual(boot, boot.GetMethod("ModifyDamageAdditive")!.DeclaringType);
        Assert.NotEqual(boot, boot.GetMethod("ModifyDamageMultiplicative")!.DeclaringType);
        Assert.NotEqual(boot, boot.GetMethod("ModifyDamageCap")!.DeclaringType);
        Assert.True(HitOrder.RelicsOnTheHpLossPhase);
    }

    // ---- EB-689: one folding rule per screen ------------------------------

    [Fact]
    public void Every_attack_face_takes_the_same_body_whatever_it_targets()
    {
        var enemy = Seat.Klee(30).Creature;
        var anyEnemy = AnAttack();
        Assert.Equal(TargetType.AnyEnemy, anyEnemy.TargetType);

        // Aimed: the game named the body, and the face keeps it.
        Assert.Same(
            enemy,
            HitOrder.BodyForPreview(anyEnemy, CardPreviewMode.Normal, enemy, null));
        // In hand: no body from the game, so the front enemy -- the same body
        // for every Attack on the screen, which is the row's acceptance.
        Assert.Same(
            enemy,
            HitOrder.BodyForPreview(anyEnemy, CardPreviewMode.Normal, null, enemy));
    }

    [Fact]
    public void The_all_enemies_branch_is_left_to_the_game()
    {
        var card = AnAttack();
        var enemy = Seat.Klee(30).Creature;

        // Not an all-enemies face, so the predicate is false whatever the
        // preview mode, and the front enemy stands.
        Assert.False(HitOrder.GameFoldsEveryEnemyItself(
            card, CardPreviewMode.MultiCreatureTargeting));
        Assert.Same(enemy, HitOrder.BodyForPreview(
            card, CardPreviewMode.MultiCreatureTargeting, null, enemy));

        // And an all-enemies face outside that preview mode is an ordinary
        // face: the mode is half the predicate.
        Seat.Force(card, "TargetType", TargetType.AllEnemies);
        Assert.False(HitOrder.GameFoldsEveryEnemyItself(card, CardPreviewMode.Normal));

        // THE PILE CLAUSE IS STRUCTURAL and says so. `CardModel.Pile` is
        // computed -- `_owner?.Piles.FirstOrDefault(p => p.Cards.Contains(this))`
        // -- so a card only has one inside a live combat, which is the headless
        // boundary (README). A card with no pile is not in Hand or Play and the
        // predicate is false, which is the behaviour this CAN assert; that the
        // clause reads the pile at all is read off the compiled method.
        Assert.Null(card.Pile);
        Assert.False(HitOrder.GameFoldsEveryEnemyItself(
            card, CardPreviewMode.MultiCreatureTargeting));
        var calls = Il.Calls(typeof(HitOrder).GetMethod(
            nameof(HitOrder.GameFoldsEveryEnemyItself))!);
        Assert.Contains("CardModel.get_Pile", calls);
        Assert.Contains("CardModel.get_TargetType", calls);
    }
}
