using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-328`, THE FACE SHAPES: one folding rule per screen, on every shape the
/// mod prints.
///
/// The PAIRS are pinned one file up (`HitOrderPinTests`), against the game's
/// own hook methods in the engine's own phase order. This file pins that each
/// SHAPE reaches that order rather than a second arithmetic of its own:
///
///   | shape          | who computes the face                     |
///   |----------------|-------------------------------------------|
///   | plain          | the game's `DamageVar`                     |
///   | multi-hit      | the game's `DamageVar`, once per hit       |
///   | conditional    | two `FoldedDamageVar`s, one body between   |
///   | Plan-half      | `KokomiPlan.Hers` at writing,              |
///   |                | `KokomiPlan.PlannedDamage` at the morning  |
///   | companion-hit  | `SimDamagePipeline` (the Unpowered mirror) |
///   | Set-off        | `SimDamagePipeline.ResolveOnTarget`        |
///
/// STRUCTURAL WHERE IT HAS TO BE AND SAYS SO. `UpdateCardPreview` reaches
/// `CardModel.CombatState` and `card.Owner.RunState`, which need a live combat
/// this harness cannot build (README, "The headless boundary"), so what the
/// two folding vars DO is read off the compiled method; the Plan half and the
/// mirror are real values.
/// </summary>
public class Eb328FaceOrderTests
{
    private static System.Collections.Generic.IReadOnlyCollection<string> CallsOf(
        System.Type var) =>
        Il.Calls(var.GetMethod("UpdateCardPreview", HeadlessGame.All)!);

    // ---- SHAPE: plain, and the conditional pair on one card ---------------

    [Fact]
    public void Both_folding_vars_hand_the_body_to_the_game_and_add_nothing()
    {
        foreach (var var in new[]
                 { typeof(FrontFoldedDamageVar), typeof(FoldedDamageVar) })
        {
            var calls = CallsOf(var);
            // The body is named once (the guest seat round: through
            // `FoldedPreview.Body`, which is `HitOrder.BodyForPreview` off a
            // Furina Stage board and the game's own target on one) ...
            Assert.Contains("FoldedPreview.Body", calls);
            Assert.Contains("FurinaStage.LiveFor", calls);
            Assert.Contains("KokomiPlan.FrontEnemy", calls);
            // ... and handed to the game's own var, which runs phases 1-4 in
            // the engine's order over it.
            Assert.Contains(calls, c => c.EndsWith(".UpdateCardPreview"));
            // `EB-328`: nothing is multiplied over the engine's answer any
            // more. That expression folded the target's Vulnerable a second
            // time on every aimed face, and folded it AFTER the cap phase.
            Assert.DoesNotContain("SimDamagePipeline.TargetMods", calls);
            Assert.DoesNotContain("SimDamagePipeline.Resolve", calls);
        }
    }

    [Fact]
    public void A_conditional_face_folds_its_two_halves_under_one_rule()
    {
        // `EB-624`'s shape: "Deal 7 damage. If the enemy has a debuff, deal 10
        // instead" -- two live numbers on one card. Both are `FoldedDamageVar`s
        // and both now take their body from `HitOrder.BodyForPreview`, so the
        // two halves cannot fold under two conventions again.
        var vars = new ProtoKkUndertow().DynamicVars;
        Assert.IsType<FoldedDamageVar>((object)vars["PlainDamage"]);
        Assert.IsType<FoldedDamageVar>((object)vars["DebuffDamage"]);
        Assert.IsType<FrontFoldedDamageVar>((object)vars.CalculatedDamage);

        // One implementation between them: `FoldedDamageVar` is one type and
        // both tokens are instances of it, which is what makes "one rule per
        // screen" a fact about the class rather than about this card.
        Assert.Same(
            vars["PlainDamage"].GetType(), vars["DebuffDamage"].GetType());
    }

    [Fact]
    public void The_game_s_own_var_is_still_underneath_both_of_them()
    {
        // The repair must not have turned either face into a mod-side
        // arithmetic: `DamageVar` and `CalculatedDamageVar` are what run the
        // phases, and `EB-624`'s reason for two classes (one token each) is
        // untouched.
        Assert.True(typeof(DamageVar).IsAssignableFrom(typeof(FoldedDamageVar)));
        Assert.True(typeof(CalculatedDamageVar)
            .IsAssignableFrom(typeof(FrontFoldedDamageVar)));
        Assert.Equal("CalculatedDamage", FrontFoldedDamageVar.Token);
    }

    // ---- SHAPE: the Plan half ---------------------------------------------

    [Fact]
    public void The_plan_half_folds_hers_in_the_engine_s_own_order()
    {
        // R246 pick 1 / `EB-599`: a Plan line folds HER Strength and HER
        // enchantment at writing time and nothing of the target's, because the
        // line lands next morning against whatever the body wears then. What
        // `EB-328` has to say about it is only the ORDER, and the order is the
        // engine's: the enchantment is applied BEFORE the additive phase
        // (`Hook.ModifyDamage` folds `cardSource.Enchantment` ahead of every
        // `ModifyDamageAdditive`), so a multiplicative enchantment scales the
        // printed number and NOT the Strength added after it.
        var kokomi = Seat.Kokomi().WithPower<StrengthPower>(3);
        Assert.Equal(7, KokomiPlan.Hers(kokomi.Creature, null, 4));

        // Weak is deliberately absent -- round four-c's finding, and the one
        // judgement `Hers` makes against `SimDamagePipeline.DealerMods`.
        var weakened = Seat.Kokomi()
            .WithPower<StrengthPower>(3).WithPower<WeakPower>(1);
        Assert.Equal(7, KokomiPlan.Hers(weakened.Creature, null, 4));
    }

    [Fact]
    public void The_plan_half_takes_the_target_s_terms_only_at_the_morning()
    {
        // And takes them ONCE, which is the same rule the two folding vars now
        // keep: the morning's hit is an Unpowered mirror hit, so the native
        // Vulnerable declines it and `SimDamagePipeline.TargetMods` is the one
        // place it is applied.
        var vulnerable = Seat.Kokomi(30).WithPower<VulnerablePower>(1).Creature;
        Assert.Equal(6, KokomiPlan.PlannedDamage(vulnerable, 4));
        Assert.Equal(4, KokomiPlan.PlannedDamage(null, 4));
        Assert.Equal(
            4m,
            HitOrder.Compose(null, vulnerable, 4m, ValueProp.Unpowered));
    }

    // ---- SHAPE: the companion hit and the Set-off -------------------------

    [Fact]
    public void A_companion_hit_and_a_set_off_read_the_mirror_and_not_the_hooks()
    {
        var applier = Seat.Kokomi().WithPower<StrengthPower>(5).WithPower<WeakPower>(1);
        var enemy = Seat.Kokomi(30).WithPower<VulnerablePower>(1).Creature;

        // The companion's pulse carries the dealer's side and the target's:
        // (4 + 5) x 0.75 x 1.5.
        var pulse = SimDamagePipeline.TargetMods(
            enemy, SimDamagePipeline.DealerMods(applier.Creature, 4m));
        Assert.Equal(
            HitOrder.Compose(applier.Creature, enemy, 4m, ValueProp.Move),
            pulse);

        // A Bomb carries the target's only (R248) -- 4 x 1.5 -- so the two
        // shapes are two pipelines on purpose and the pin says which is which.
        Assert.Equal(6, SimDamagePipeline.ResolveOnTarget(enemy, 4m, 1m));
    }
}
