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
/// patch needed. The spend side is AfterCardPlayed on the same power.
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
    /// The consume. Printed cost is read off EnergyCost.Canonical -- the
    /// sim's rule is "printed cost != 0", NOT "paid cost was 0", so an attack
    /// zeroed by some other effect still eats the charge at threshold, and a
    /// printed-0 attack never does.
    /// </summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var card = cardPlay.Card;
        if (!AppliesTo(card) || card.EnergyCost.Canonical == 0)
        {
            return;
        }

        // applier: null -- the spend is bookkeeping, not a power "given" by
        // anyone; keeping it out of the ModifyPowerAmountGiven hook chain
        // means nothing can inflate or shrink the exact -3.
        await PowerCmd.ModifyAmount(
            choiceContext, this, -CurrentThreshold, applier: null, cardSource: card);
    }
}
