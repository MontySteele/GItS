using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Powers;

/// <summary>
/// Klee's Spark counter (spec C2.3; reference implementation
/// tier0/engine/combat.py card_cost/play_card, constants.py
/// SPARKS_FOR_FREE_ATTACK).
///
/// Canonical rules:
///   - Sparks accumulate on the player, unbounded, for the rest of the combat.
///   - While at THRESHOLD or more, the player's Attacks cost 0.
///   - Playing an Attack whose PRINTED cost is nonzero while at threshold
///     consumes THRESHOLD Sparks. Printed-0 attacks never consume (the sim's
///     `card.cost != 0` guard) -- a free attack should not eat the charge.
///
/// The cost side rides Hook.ModifyEnergyCostInCombat, which CardEnergyCost
/// consults for BOTH display and payment (GetWithModifiers -> the hook), so
/// the card visibly reads 0 in hand the moment the third Spark lands -- no UI
/// patch needed. The spend DECISION is snapshotted in BeforeCardPlayed
/// (pre-resolution, the sim's timing); the consume executes in
/// AfterCardPlayed. See the method comments for the Snap finding that
/// forced the split.
///
/// X-cost attacks are EXEMPT from both sides, deliberately: zeroing an X-card
/// sets X = 0 and makes the card do nothing, which converts the buff into a
/// trap. The sim does apply sparks to X-attacks; divergence recorded in
/// DECISIONS finding 26 rather than silently shipped. Klee's two X-cost cards
/// are C3-blocked, so nothing observable differs yet.
/// </summary>
public sealed class SparkPower : PowerModel, ILocalizationProvider
{
    /// <summary>Mirrors tier0 constants.py SPARKS_FOR_FREE_ATTACK = 3.</summary>
    public const int Threshold = 3;

    /// <summary>
    /// The live threshold: True Spark Knight lowers it, floored at 1 (sim:
    /// combat.py spark_threshold, `max(1, 3 - spark_threshold_down)`). Used
    /// for BOTH the cost gate and the spend, so they can never disagree --
    /// the sim reads spark_threshold(state) at both sites too.
    /// </summary>
    private int CurrentThreshold => System.Math.Max(
        1, Threshold
           - (Owner?.Powers.OfType<SparkThresholdDownPower>()
                  .FirstOrDefault()?.Amount ?? 0));

    public List<(string, string)>? Localization => new()
    {
        ("title", "Spark"),
        ("description",
            "At 3 [gold]Sparks[/gold], your Attacks cost 0. "
          + "Playing one consumes 3 [gold]Sparks[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    /// <summary>Counter: sparks are spent, not ticked down by time.</summary>
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// Grants sparks to <paramref name="player"/>. The single entry point for
    /// every future source (gain_spark codegen op, Pounding Surprise, Crackle
    /// per M8 ruling R10) so the gain path stays one line to instrument.
    /// </summary>
    public static async Task Gain(
        PlayerChoiceContext choiceContext, Creature player, int amount,
        CardModel? cardSource)
    {
        await PowerCmd.Apply<SparkPower>(
            choiceContext, player, amount, applier: player, cardSource: cardSource);
    }

    private bool AppliesTo(CardModel card) =>
        Amount >= CurrentThreshold
        && card.Type == CardType.Attack
        && !card.EnergyCost.CostsX
        && card.Owner?.Creature == Owner;

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (originalCost <= 0m || !AppliesTo(card))
        {
            return false;
        }

        modifiedCost = 0m;
        return true;
    }

    /// <summary>
    /// The spend DECISION, snapshotted at play start (playtest finding
    /// 2026-07-20, the Snap bug): the sim's play_card evaluates
    /// `sparks >= threshold` BEFORE the card's effects resolve, so a card
    /// whose own rider pushes the bank to threshold mid-resolution must NOT
    /// eat the charge -- the player paid energy for that play. Deciding in
    /// AfterCardPlayed (the old shape) read the post-rider bank: Snap at 2
    /// Sparks cost 1 energy, granted the 3rd Spark, then wrongly consumed
    /// all 3. Printed cost is read off EnergyCost.Canonical -- the sim's
    /// guard is `card.cost != 0` (a printed-0 attack never consumes).
    ///
    /// IsFirstInSeries reproduces "once per play_card call" across replays,
    /// same as the burst grant in KleeElementalHooks. The threshold is
    /// snapshotted with the decision (sim: `p.sparks -= spark_threshold(state)`
    /// reads the state at play time).
    /// </summary>
    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        if (cardPlay.IsFirstInSeries
            && AppliesTo(cardPlay.Card)
            && cardPlay.Card.EnergyCost.Canonical != 0)
        {
            _pendingSpendPlay = cardPlay;
            _pendingSpendAmount = CurrentThreshold;
        }
        return Task.CompletedTask;
    }

    /// <summary>
    /// Transient decision state; only ever set between a BeforeCardPlayed and
    /// its AfterCardPlayed (one card resolves at a time). Not cloned
    /// meaningfully by MutableClone -- a stale reference on a clone can never
    /// equal a live CardPlay, so the worst case is a no-op.
    /// </summary>
    private CardPlay? _pendingSpendPlay;
    private int _pendingSpendAmount;

    /// <summary>
    /// The consume, executing the play-time decision. Kept AFTER resolution:
    /// mutating the bank in BeforeCardPlayed could drop Amount below
    /// threshold before the payment machinery reads the (zeroed) cost --
    /// that ordering has no decompile evidence, so the safe side wins. The
    /// sim spends pre-resolution, which only differs observably for cards
    /// that READ the bank mid-play (formula cards; none are shipped --
    /// revisit with evidence when formula codegen lands).
    /// </summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay != _pendingSpendPlay)
        {
            return;
        }
        _pendingSpendPlay = null;

        // applier: null -- the spend is bookkeeping, not a power "given" by
        // anyone; keeping it out of the ModifyPowerAmountGiven hook chain
        // means nothing can inflate or shrink the exact spend.
        await PowerCmd.ModifyAmount(
            choiceContext, this, -_pendingSpendAmount, applier: null,
            cardSource: cardPlay.Card);
    }
}
