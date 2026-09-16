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
/// `EB-328`: AND IT WAS FOLDING TWICE, which the note here used to deny. The
/// claim was that <c>CalculatedVar.UpdateCardPreview</c> runs "the DEALER's
/// hooks" and therefore could not reach the target's side. It is not the
/// dealer's hooks: <c>Hook.ModifyDamage</c> walks
/// <c>CombatState.IterateHookListeners</c>, which is EVERY ally's and every
/// enemy's powers (plus relics, potions, orbs and every card in every pile),
/// and it hands each of them the <c>target</c> it was given --
/// <c>VulnerablePower.ModifyDamageMultiplicative</c> fires on
/// <c>target == Owner</c>. So whenever the game named a body, the base call
/// had ALREADY folded that body's Vulnerable and that body's
/// <c>ModifyDamageCap</c>, and the extra <c>SimDamagePipeline.TargetMods</c>
/// multiplied the Vulnerable in a second time -- after the cap phase, so the
/// number escaped a clamp the wire applies as well. Under Weak 1 and
/// Vulnerable 1 a base 4 printed 4 x 0.75 x 1.5 x 1.5 = 6 while the board
/// moved 4.
///
/// THE REPAIR IS TO NAME THE BODY ONCE AND LET THE ENGINE FOLD IT.
/// <see cref="HitOrder.BodyForPreview"/> answers the aimed creature where the
/// game named one, the front enemy where it did not, and null on the
/// all-enemies branch the game folds for itself; the game's own var then runs
/// phases 1-4 over that body in the engine's own order, which is written out
/// in <see cref="HitOrder"/> with the type names it was decompiled from.
/// Nothing is multiplied on top afterwards, which is why the pairs agree now:
/// Weak and Vulnerable are BOTH phase-2 terms and belong in one product.
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
        // OFF A CARD THAT IS NOT IN PLAY the game runs no hooks at all, and
        // neither does this: a compendium or deck-view read prints its base.
        // A canonical (compendium) copy has no owner and the getter ASSERTS
        // rather than returning null -- `PlanDamageVar`'s guard, verbatim.
        if (!runGlobalHooks || !card.IsMutable)
        {
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        // `EB-598`: THE AIMED BODY WHERE THE GAME NAMED ONE, the front enemy
        // where it did not. `EB-328`: and handed to the game's own var as the
        // target, ONCE, rather than folded on top of its answer -- see the
        // note above and `HitOrder`.
        base.UpdateCardPreview(
            card, previewMode,
            HitOrder.BodyForPreview(
                card, previewMode, target,
                KokomiPlan.FrontEnemy(card.Owner?.Creature)),
            runGlobalHooks);
    }
}

/// <summary>
/// `EB-624`: the OTHER branch of a conditional hit, folded the same way, under
/// a name of its own.
///
/// THE SHAPE THE BASE GAME USES. <c>FLATTEN</c> and its family print "Deal 8
/// damage. If X, deal 12 instead." -- two numbers, both live, and the reader
/// picks. <i>Undertow</i> printed `EB-598`'s one-number form instead ("Deal 10
/// damage, already including 3 if the enemy has a debuff"), which [USER]'s
/// act-1 run of 2026-09-07 read as a sentence arguing with itself: 10 cannot
/// already include a 3 that the enemy it is aimed at has not earned.
///
/// WHY A SECOND VAR AND NOT A SECOND <see cref="FrontFoldedDamageVar"/>. The
/// game's <c>CalculatedDamageVar</c> hardcodes the token `CalculatedDamage` in
/// its constructor and <c>DynamicVar.Name</c> is get-only, so two of them on
/// one card is one var: a face needs two tokens. <c>DamageVar</c> is the one
/// damage var the game gives a <c>(string name, ...)</c> overload, and its
/// preview is the same <c>Hook.ModifyDamage(..., ModifyDamageHookType.All)</c>
/// call the calculated var makes -- Strike's own fold. So both sides are the
/// game's, by the game's own call, over the body
/// <see cref="HitOrder.BodyForPreview"/> names (`EB-328`).
///
/// THE HIT IS UNTOUCHED. <c>CalculatedDamage</c> stays on the card and stays
/// what <c>DamageCmd.Attack</c> is handed; these two are printed and nothing
/// else, which is why they may be plain <c>DamageVar</c>s carrying the two
/// sheet numbers rather than the base/extra pair the multiplier reads.
///
/// QUARANTINED, for <see cref="FrontFoldedDamageVar"/>'s reason and by the
/// same csproj rule.
/// </summary>
public sealed class FoldedDamageVar : DamageVar
{
    public FoldedDamageVar(string name, decimal damage, ValueProp props)
        : base(name, damage, props)
    {
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        // Off a card that is not in play the game runs no hooks, and neither
        // does this: a shop shelf and a deck view print the sheet's numbers,
        // which is the screen `EB-484` was filed from and the screen this
        // shape finally answers.
        if (!runGlobalHooks || !card.IsMutable)
        {
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        // `EB-328`: the body named once and handed to the game's own var, the
        // same repair `FrontFoldedDamageVar` takes and for the same reason --
        // this branch prints the OTHER half of one conditional face, so the
        // two halves have to fold under one rule or the sentence argues with
        // itself again.
        var body = HitOrder.BodyForPreview(
            card, previewMode, target,
            KokomiPlan.FrontEnemy(card.Owner?.Creature));
        base.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
        if (card.Owner?.Creature == null) return;
        // `EB-388` / `EB-498`: AND THE SPOTLIGHT, WHICH IS NOT A HOOK. The
        // emitted play wraps every branch leg of a Companion row in
        // <c>SpotlightSystem.PrintedDamage</c> -- so under Guest Cast the leg
        // already PAYS the multiplied number, and only the face was behind
        // (Furina r2 run 2; r3's Freminet printing 6 and paying 9).
        // `PrintedDamageDelta`'s own note says why it cannot ride
        // `Hook.ModifyDamage`: Spotlight multiplies the PRINTED number and
        // adds its flat bonus ahead of Strength and Vulnerable, and routing it
        // through the hook would fold Strength into the multiplier and change
        // the resolved hit.
        //
        // IDENTITY EVERYWHERE ELSE, which is why it is unconditional here:
        // <c>PrintedDamage</c> takes <c>OutwardMultiplier</c> 1 and returns
        // its argument for any card that is not a spotlighted
        // <c>ICompanionCard</c> -- every Kokomi and Klee row that prints a
        // branch pair reads exactly what it read before.
        //
        // FOLDED FIRST AND HOOKED SECOND, `SpotlitBlockVar`'s order and for
        // its reason: the play hands <c>DamageCmd.Attack</c> the printed
        // number and the game's terms apply to THAT, so a percentage must not
        // compound against the wrong base.
        var folded = new DamageVar(
            Name, SpotlightSystem.PrintedDamage(card, BaseValue), Props);
        folded.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
        PreviewValue = folded.PreviewValue;
    }
}

/// <summary>
/// `EB-498` / `EB-388`: <see cref="FoldedDamageVar"/>'s BLOCK twin -- a named
/// <c>BlockVar</c> whose preview runs the game's block hooks over the number
/// the play will actually gain.
///
/// WHY IT EXISTS. A conditional face's Block arm is a second Block number on
/// one card, so it cannot be <c>CalculatedBlockVar</c> (one
/// <c>CalculationBase</c> per card) and it cannot be
/// <see cref="SpotlightSystem.SpotlitBlockVar"/> either, whose token is the
/// card's own <c>Block</c> slot. It is the game's own <c>BlockVar</c> under a
/// token of its own -- `EB-737`'s shape -- plus the Spotlight fold the
/// emitted play already applies (<c>PrintedBlock</c>), so "gain 4 additional
/// Block" prints 6 under Guest Cast where the card gains 6.
///
/// IDENTITY OFF A COMPANION ROW, for <see cref="FoldedDamageVar"/>'s reason:
/// <c>PrintedBlock</c> returns its argument for anything that is not a
/// spotlighted <c>ICompanionCard</c>.
///
/// IT SUBCLASSES <c>BlockVar</c> AND THAT IS LOAD-BEARING
/// (<c>SpotlitBlockVar</c>'s own note): <c>DynamicVarSet</c> casts, and a
/// plain <c>DynamicVar</c> under a Block token throws the first time the card
/// is played.
///
/// QUARANTINED, in this file and by this file's csproj rule.
/// </summary>
public sealed class FoldedBlockVar : BlockVar
{
    public FoldedBlockVar(string name, decimal amount, ValueProp props)
        : base(name, amount, props)
    {
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
        if (!runGlobalHooks || !card.IsMutable) return;
        if (card.Owner?.Creature == null) return;
        var folded = new BlockVar(
            Name, SpotlightSystem.PrintedBlock(card, BaseValue), Props);
        folded.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
        PreviewValue = folded.PreviewValue;
    }
}
