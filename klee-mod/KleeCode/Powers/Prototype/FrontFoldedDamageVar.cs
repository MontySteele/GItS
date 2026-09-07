using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// `EB-522`: a calculated damage face that prints what it will deal, on the
/// screen where the game hands it nobody to deal it to.
///
/// THE FIND (Kokomi r18 lane 2, fight 5). "Well Laid printed 'Deal 8 damage'
/// and removed 12 HP (36 to 24). Riptide on the same screen printed 'Deal 9
/// damage to ALL' for its immediate line and 'Plan: Deal 19' for its Plan
/// line -- 19 is 13 x 1.5, so the Plan line IS multiplied by the enemy's
/// Vulnerable on the printed face while the immediate line is not. Two numbers
/// on one card computed to two different conventions."
///
/// WHY THE TWO DISAGREED, and neither half is a bug in the pipeline.
/// <c>UpdateCardPreview</c> is handed the creature the card is being aimed at,
/// and the target-side multiplier is a fact about THAT creature. A sighted
/// player dragging a card has one; a card sitting in a hand has none, and a
/// blind page reads the face exactly there -- so an aimed row's number is its
/// base. <see cref="KokomiPlan.PlanDamageVar"/> is the row that already
/// answered this, because a Plan card is dragged onto the PET and its preview
/// target is therefore NEVER the enemy that will be hit: it reads
/// <see cref="KokomiPlan.FrontEnemy"/> itself. That is the convention the
/// packet took, and this is it on the other kind of face.
///
/// `EB-598`: AND WITH A TARGET TOO, because the base var never folded the
/// target's side either. This used to return early on a non-null target, on
/// the reading that "the game's answer stands wherever the game had one to
/// give"; the r22 lane-1 seat measured otherwise. <i>Undertow</i>'s face read
/// "Deal 10 damage, already including 3 if the enemy has a debuff" -- so a
/// target WAS handed in, its Vulnerable satisfied the debuff rider, and the
/// extra 3 was folded -- and the card then delivered 15. The Vulnerable that
/// bought the rider was not in the number the rider was added to. So the fold
/// is about the BODY, whichever way the preview learned of it: the aimed
/// creature when the game names one, the front enemy when it does not.
///
/// STILL INCAPABLE OF FOLDING TWICE, and by the same argument as before,
/// checked rather than assumed: <c>CalculatedVar.UpdateCardPreview</c> runs
/// the DEALER's hooks (her Strength, her Weak, the Spotlight, this row's own
/// multiplier), which is why the face folds four modifiers and was silent
/// about the fifth (`EB-589`'s finding, one surface over). The target's terms
/// are added here, once.
///
/// <see cref="SimDamagePipeline.TargetMods"/> AND NOT A SECOND EXPRESSION,
/// `EB-265`'s rule: it is the call <c>ElementalHit.Deal</c> makes on the same
/// creature a beat later, so a face that disagrees with the board is a red
/// test rather than a number a seat stops trusting.
///
/// QUARANTINED. The file sits under <c>Powers/Prototype/</c>, which
/// <c>KleeCode.csproj</c> Compile-Removes from a release build, and
/// <c>gen_klee_cards.build_vars</c> emits it for `proto_` rows only: the
/// shipped sheets keep the game's own var, because what a card prints at rest
/// is a surface R249 ruled is not repainted outside the arm. It sits beside
/// the arms' other vars rather than beside the cards for one further reason:
/// <c>lint_generated_structure.var_token_aliases</c> reads this directory for
/// the <c>Token</c> declaration below.
///
/// WHAT NO HEADLESS PIN CAN SAY. <c>CalculatedDamageVar.UpdateCardPreview</c>
/// reaches <c>CardModel.CombatState</c>, which needs a live combat this
/// harness cannot build (KleeTests/README.md, "The headless boundary"), so the
/// number itself is owed a live read. What IS pinned is the wiring: which type
/// the generator emits, that it is the game's own var underneath, that the
/// fold is the shared call, and that the body it folds is the aimed one where
/// there is one and the front enemy where there is not.
/// </summary>
public sealed class FrontFoldedDamageVar : CalculatedDamageVar
{
    /// <summary>The token this var DECLARES, which is the game's own and not
    /// the type name above: the base constructor names it, so a face still
    /// prints `{CalculatedDamage:diff()}` and a body still looks it up under
    /// that word. Stated as a const because
    /// `tools/lint_generated_structure.var_token_aliases` reads exactly this
    /// declaration, the way `DeferredBlockVar` and `SpotlitBlockVar` do.
    /// </summary>
    public const string Token = "CalculatedDamage";

    public FrontFoldedDamageVar(ValueProp props) : base(props)
    {
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
        // OFF A CARD THAT IS NOT IN PLAY the game runs no hooks at all, and
        // neither does this: a compendium or deck-view read prints its base.
        if (!runGlobalHooks) return;
        // A canonical (compendium) copy has no owner and the getter ASSERTS
        // rather than returning null -- `PlanDamageVar`'s guard, verbatim.
        if (!card.IsMutable) return;
        // `EB-598`: THE AIMED BODY WHERE THE GAME NAMED ONE, the front enemy
        // where it did not. Both are the same question -- which creature is
        // this number about -- and the base var answers neither.
        var body = target ?? KokomiPlan.FrontEnemy(card.Owner?.Creature);
        if (body == null) return;
        PreviewValue = (int)SimDamagePipeline.TargetMods(body, PreviewValue);
    }
}
