using System.Linq;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// `EB-328`. THE ORDER A HIT IS COMPOSED IN, WRITTEN DOWN ONCE, and the one
/// question a printed face has to answer before it folds anything: has the
/// game already folded the target's side?
///
/// ============================================================
/// THE GAME'S ORDER, DECOMPILED (sts2.dll 0.111.0, `41cef1ea`)
/// ============================================================
/// Read with `ilspycmd -t MegaCrit.Sts2.Core.Hooks.Hook`. Every number a card
/// deals -- a play, a summon's pulse, a bomb, an intent -- arrives at
/// <c>CreatureCmd.Damage</c>, and the FIRST thing that method does is
///
///     Hook.ModifyDamage(runState, combatState, target, dealer, amount, props,
///                       cardSource, cardPlay, ModifyDamageHookType.All,
///                       CardPreviewMode.None, out modifiers)
///
/// which composes in exactly these phases, in this order:
///
///   0. <c>EnchantmentModel.EnchantDamageAdditive</c>, then
///      <c>EnchantmentModel.EnchantDamageMultiplicative</c> -- the CARD's own
///      rider, off <c>cardSource.Enchantment</c>, BEFORE any hook phase. So an
///      enchantment's multiplier does NOT scale the Strength added below it;
///      it scales the printed number only. (`KokomiPlan.Enchanted` and the
///      sim's `kokomi_plan._enchanted` are that pair, in that order.)
///   1. ADDITIVE, over every listener of
///      <c>IRunState.IterateHookListeners(combatState)</c>, each asked
///      <c>AbstractModel.ModifyDamageAdditive</c> and its answer SUMMED:
///      <c>StrengthPower</c> and the mod's own flat riders
///      (<c>AttackUpThisTurnPower</c>, <c>NextAttackUpPower</c>, ...).
///   2. MULTIPLICATIVE, over the same listeners, each asked
///      <c>AbstractModel.ModifyDamageMultiplicative</c> and its answer
///      MULTIPLIED IN: <c>WeakPower</c> (x0.75, gated on
///      <c>dealer == Owner</c>) and <c>VulnerablePower</c> (x1.5, gated on
///      <c>target == Owner</c>) -- so BOTH of those live in the same phase,
///      after the whole additive sum.
///   3. CAP, the MINIMUM <c>AbstractModel.ModifyDamageCap</c> over the same
///      listeners: <c>HardToKillPower</c> and <c>IntangiblePower</c> are the
///      only two overrides in the shipped assembly, and both answer
///      <c>decimal.MaxValue</c> unless <c>target == Owner</c>. The cap is LAST
///      and clamps everything above it.
///   4. <c>Math.Max(0m, num)</c>.
///
/// Then, and only then, <c>CreatureCmd.Damage</c> runs
/// <c>Hook.BeforeDamageReceived</c>, <c>Creature.DamageBlockInternal</c> and
/// the two <c>Hook.ModifyHpLost</c> phases. Nothing in those phases is part of
/// a damage number and NO face can honestly print them -- see
/// <see cref="RelicsOnTheHpLossPhase"/>.
///
/// WHAT THE LISTENER SET IS, because "the dealer's hooks" is not what it is
/// (<c>CombatState.IterateHookListeners</c>): every ally's and every enemy's
/// powers, each monster, each live player's relics and potions and orbs, EVERY
/// CARD in every pile with its affliction and enchantment, then the combat's
/// modifiers, badges and multiplayer scaling. The TARGET's powers are in that
/// list. This is the fact `EB-328` turned on.
///
/// ============================================================
/// THE ONE QUESTION A FACE HAS TO ANSWER
/// ============================================================
/// <c>DamageVar.UpdateCardPreview</c> and
/// <c>CalculatedDamageVar.UpdateCardPreview</c> both run that same
/// <c>Hook.ModifyDamage(..., ModifyDamageHookType.All, ...)</c>, handing it
/// the creature the card is being AIMED at. So:
///
///   * aimed at a body -- the game folded phases 1-4 INCLUDING that body's
///     Vulnerable and that body's cap;
///   * sitting in a hand with no body -- <c>target</c> is null, so
///     <c>VulnerablePower</c> and the cap powers all see <c>target != Owner</c>
///     and answer neutral: the target's side is NOT folded;
///   * an all-enemies or random-enemy face in hand at
///     <c>CardPreviewMode.MultiCreatureTargeting</c> -- <c>Hook.ModifyDamage</c>
///     runs its own loop over <c>combatState.HittableEnemies</c> and takes the
///     per-enemy number only when every enemy agrees on it, otherwise it falls
///     back to the null-target pass. That branch is the game's own judgement
///     and this file leaves it alone.
///
/// The mod's folding vars used to call the base var and THEN multiply
/// <c>SimDamagePipeline.TargetMods</c> over its answer. On a hand face that was
/// right and is what `EB-598` built. On an AIMED face it was the target's
/// Vulnerable a second time -- and applied after phase 3, so it also escaped
/// the cap the hit will clamp to. <see cref="BodyForPreview"/> is the repair:
/// name the body ONCE, hand it to the game's own var, and let phases 1-4 run
/// over it in the engine's own order.
/// </summary>
public static class HitOrder
{
    /// <summary>
    /// THE BODY THIS FACE IS ABOUT, or null to leave the game's own answer
    /// standing.
    ///
    /// Non-null <paramref name="target"/> is returned unchanged: the game
    /// named a body and its hook will fold that body's terms itself.
    ///
    /// Null target at <see cref="CardPreviewMode.MultiCreatureTargeting"/> on
    /// an all-enemies / random-enemy face that is in Hand or Play is returned
    /// as null, because that is the exact predicate
    /// <c>Hook.ModifyDamage</c> uses to run its own all-enemies loop
    /// (<c>target == null &amp;&amp; previewMode == MultiCreatureTargeting</c>,
    /// <c>(uint)(cardSource.TargetType - 3) &lt;= 1u</c>,
    /// <c>cardSource.Pile.Type is Hand or Play</c>). Substituting the front
    /// enemy there would print the front enemy's Vulnerable on a face the game
    /// deliberately prints unfolded when the enemies disagree.
    ///
    /// Otherwise <paramref name="frontEnemy"/>, which is `EB-598`'s rule and
    /// <c>KokomiPlan.FrontEnemy</c>'s definition: a hand face is about the
    /// body it is going to hit, and a blind page reads the face exactly there.
    /// It is a PARAMETER rather than a call because that reader lives under
    /// <c>Powers/Prototype/</c>, which <c>KleeCode.csproj</c> Compile-Removes
    /// from a release build, and the order recorded in this file is the
    /// shipped game's whether an arm is compiled or not.
    /// </summary>
    public static Creature? BodyForPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        Creature? frontEnemy)
    {
        if (target != null) return target;
        if (GameFoldsEveryEnemyItself(card, previewMode)) return null;
        return frontEnemy;
    }

    /// <summary>
    /// <c>Hook.ModifyDamage</c>'s own multi-creature predicate, spelled out so
    /// a pin can read it. Named rather than inlined for the reason the base
    /// library's own predicates are named: it is the one branch this file
    /// declines to touch, and declining has to be visible.
    /// </summary>
    public static bool GameFoldsEveryEnemyItself(
        CardModel card, CardPreviewMode previewMode)
    {
        if (previewMode != CardPreviewMode.MultiCreatureTargeting) return false;
        if (card.TargetType is not (TargetType.AllEnemies or TargetType.RandomEnemy))
        {
            return false;
        }
        var pile = card.Pile;
        return pile != null
            && (pile.Type == PileType.Hand || pile.Type == PileType.Play);
    }

    /// <summary>
    /// `EB-752`, ANSWERED AND CLOSED AS NOT-A-CALCULATOR-BUG.
    ///
    /// The row asks for The Boot's number to be folded into a card's printed
    /// damage the way Weak is. It cannot be, and the decompile says why:
    /// <c>TheBoot.ModifyHpLostAfterOstyLate</c> is an HP-LOSS hook, not a
    /// <c>ModifyDamage</c> one. It runs at step 3 of
    /// <c>CreatureCmd.Damage</c>, AFTER <c>DamageBlockInternal</c> has taken
    /// the target's Block out -- so its answer depends on how much Block the
    /// body is wearing when the hit lands, which a face cannot know and which
    /// a 4 into 12 Block does not change at all. The same is true of every
    /// other <c>ModifyHpLost*</c> listener.
    ///
    /// A face that printed 5 for a Boot-raised 4 would be right on a naked
    /// enemy and wrong on a blocking one; the row's own acceptance ("a face's
    /// number equals the number the wire delivers") is therefore unreachable
    /// for this relic through arithmetic, and what it wants is the row's other
    /// option -- print the modifier BESIDE the number. That is a text surface,
    /// not this calculator.
    /// </summary>
    public static bool RelicsOnTheHpLossPhase => true;

    /// <summary>
    /// Every <c>ModifyDamageCap</c> the ENGINE would find for this body,
    /// applied the way phase 3 applies it -- the minimum, and last.
    ///
    /// <see cref="SimDamagePipeline.TargetCap"/> is the reader; this exists so
    /// the phase has a name at the place the order is recorded, and so a pin
    /// can assert that a mod-side prediction clamps AFTER its multipliers
    /// rather than before them. Clamping first and multiplying afterwards is
    /// the `EB-328` shape on the other end of the chain: a Hard To Kill 3 with
    /// a Vulnerable on the same body printed 4.5 where the wire delivers 3.
    /// </summary>
    public static decimal ApplyCapLast(Creature target, decimal amount)
    {
        var cap = SimDamagePipeline.TargetCap(target);
        return amount > cap ? cap : amount;
    }

    /// <summary>
    /// THE DEALER'S ADDITIVE PHASE AND THE DEALER'S MULTIPLICATIVE PHASE, over
    /// a body's real powers, asked of the GAME'S OWN hook methods.
    ///
    /// Not used by any shipped path -- <see cref="SimDamagePipeline"/> is what
    /// the Unpowered mirror hits run, deliberately, because those hits fail
    /// <c>ValueProp.IsPoweredAttack</c> and the native powers decline them
    /// (that file's own note). This is the pins' instrument: it lets a headless
    /// test compose a pair the way the engine composes it -- every additive
    /// answer summed, THEN every multiplicative answer multiplied in, THEN the
    /// cap -- without the test re-deriving 0.75 and 1.5 for itself.
    /// </summary>
    public static decimal Compose(
        Creature? dealer, Creature? target, decimal amount,
        MegaCrit.Sts2.Core.ValueProps.ValueProp props,
        CardModel? cardSource = null)
    {
        var listeners = (dealer?.Powers ?? Enumerable.Empty<PowerModel>())
            .Concat(target?.Powers ?? Enumerable.Empty<PowerModel>())
            .Cast<AbstractModel>()
            .ToList();

        var num = amount;
        foreach (var one in listeners)
        {
            num += one.ModifyDamageAdditive(
                target, num, props, dealer, cardSource, cardPlay: null);
        }
        foreach (var one in listeners)
        {
            num *= one.ModifyDamageMultiplicative(
                target, num, props, dealer, cardSource, cardPlay: null);
        }
        var cap = decimal.MaxValue;
        foreach (var one in listeners)
        {
            var mine = one.ModifyDamageCap(
                target, props, dealer, cardSource, cardPlay: null);
            if (mine < cap) cap = mine;
        }
        if (num > cap) num = cap;
        return num < 0m ? 0m : num;
    }
}
