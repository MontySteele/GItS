using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Hooks;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// KELP WALL'S LIVE PLAN BLOCK (Kokomi round 3 review, change 4): the face
/// prints "Gain 7 Block, plus 3 for each status or curse in your hand" and,
/// in combat, the total that sentence comes to against the hand as it stands
/// -- the <c>{InCombat:...}</c> line Driftglass already prints for its Casket.
///
/// THE TWO CLAUSES ARE FOLDED SEPARATELY, because they are paid separately:
/// <c>KokomiPlan.Kind.Block</c> pays the flat Block and
/// <see cref="KokomiStatusBatch.BlockPerStatus"/> pays the per-status Block,
/// each through its own <c>GainBlock(..., ValueProp.Move, null)</c>. So
/// Dexterity and Frail bite each clause once, and a hand with no statuses
/// pays (and previews) only the flat clause. The null card source is
/// <see cref="UnsourcedBlockVar"/>'s reason: the payout consults no
/// enchantment, so the preview does not either.
///
/// The flat term is read off the row's own <c>PlanBlock</c> var, so an
/// upgraded copy previews its upgraded number. The hand is the hand at
/// preview time; the Plan counts the hand it lands in, which is the same
/// "live, not promised" reading Driftglass's preview takes of the Casket.
///
/// PREVIEW ONLY: nothing queues or pays off this var.
/// </summary>
public sealed class PlanStatusBlockVar : DynamicVar
{
    public const string VarName = "PlanStatusBlock";

    private readonly int _rate;

    public PlanStatusBlockVar(decimal flat, int rate)
        : base(VarName, flat)
    {
        _rate = rate;
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        var flat = card.DynamicVars.TryGetValue("PlanBlock", out var planBlock)
            ? planBlock.BaseValue
            : BaseValue;
        EnchantedValue = flat;
        PreviewValue = flat;
        if (!runGlobalHooks || !card.IsMutable) return;
        var kokomi = card.Owner?.Creature;
        if (card.CombatState == null || kokomi == null) return;
        var total = Hook.ModifyBlock(
            card.CombatState, kokomi, flat, ValueProp.Move,
            null, null, out IEnumerable<AbstractModel> _);
        var statuses = KokomiStatusBatch.StatusesInHand(kokomi.Player);
        if (statuses > 0 && _rate > 0)
        {
            total += Hook.ModifyBlock(
                card.CombatState, kokomi, (decimal)(_rate * statuses),
                ValueProp.Move, null, null, out IEnumerable<AbstractModel> _);
        }
        PreviewValue = total;
    }
}
