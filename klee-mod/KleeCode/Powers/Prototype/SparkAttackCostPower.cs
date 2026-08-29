using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Powers;

/// <summary>
/// TRUE SPARK KNIGHT, re-authored -- the STRICT conversion (PICK 5 wording (1),
/// sub-pick (a); the independent seat FOLLOWS on both, review/active/
/// klee-sparks-2026-08-29.md sec.9). The C# half of the rule tier0 carries in
/// <c>combat.spark_power_price</c>; every clause below is that function's, and
/// no rule is re-derived on this side.
///
///     "Your Attacks that do not already cost [Spark] cost 3 [Spark] instead of
///      their Energy cost."
///
/// THE QUARANTINE. This directory is <c>Compile Remove</c>d unless
/// <c>-p:PrototypeCards=true</c> (KleeCode.csproj) -- the same switch that
/// compiles <c>Cards/Prototype/**</c>, defines <c>PROTOTYPE_CARDS</c> and stamps
/// a dev deploy <c>+proto</c>. A release build contains no type from this file,
/// the one seam that names it (<c>SparkCost.PowerPriceOf</c>) is itself inside
/// <c>#if PROTOTYPE_CARDS</c>, and the targeted revert is the flag. Its sim twin
/// is <c>C.SPARK_ALT_COST_ENABLED</c>.
///
/// WHY IT IS A POWER AND NOT A COST HOOK. The base game ships
/// <c>AbstractModel.TryModifyStarCost</c> for exactly this shape and nothing in
/// the base game overrides it -- but Sparks are not Stars, and making them Stars
/// was declined as a one-way door (PICK 8 option 1). So the three clauses ride
/// three extension points the game already fans out to every power in combat:
///
///   * the PRICE is <see cref="TryModifyEnergyCostInCombat"/> zeroing the Energy
///     line, which <c>CardEnergyCost.GetWithModifiers</c> consults for BOTH
///     display and payment -- so a converted Attack visibly reads 0 in hand;
///   * the GATE is <see cref="ShouldPlay"/>, fanned by <c>Hook.ShouldPlay</c> and
///     read by <c>CardModel.CanPlay</c> before any energy is committed, so a
///     short bank shows as an unplayable card rather than a play that does
///     nothing. It is the same posture <c>SparkPower.CanSpend</c> gives a card
///     that prints its own price, one layer up;
///   * the PAYMENT is the <see cref="BeforeCardPlayed"/> /
///     <see cref="AfterCardPlayed"/> split, inherited unchanged from the rule
///     this one replaces -- see <c>SparkPower.BeforeCardPlayed</c> for the Snap
///     finding that forced the split, which applies here identically.
///
/// EVERY HOOK ABOVE IS FANNED TO EVERY MODEL IN THE COMBAT, the other seat's
/// powers included (<c>Hook.IterateCombatHookListeners</c>). <see cref="Converts"/>
/// therefore checks the card's owner against this power's owner, and it is the
/// single predicate all four sites share so they cannot be retired by halves.
/// </summary>
public sealed class SparkAttackCostPower : PowerModel, ILocalizationProvider
{
    /// <summary>
    /// Mirrors tier0 <c>C.SPARK_ATTACK_POWER_PRICE = 3</c>. Lifted, not picked:
    /// [USER]'s own phrase for the card ("converts all attacks into
    /// 3-spark-cost attacks") and the retired threshold's own number.
    /// </summary>
    public const int Price = 3;

    public List<(string, string)>? Localization => new()
    {
        ("title", "True Spark Knight"),
        ("description",
            "Your Attacks that do not already cost [gold]Spark[/gold] cost "
          + Price + " [gold]Spark[/gold] instead of their Energy cost."),
    };

    public override PowerType Type => PowerType.Buff;

    /// <summary>
    /// Counter, matching <see cref="SparkPower"/>: the amount is a stack count
    /// and nothing ticks it down by time. Only one copy exists, so the count is
    /// 1 for the whole combat -- the PRICE is <see cref="Price"/> and is a
    /// constant of the rule, never the stack.
    /// </summary>
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// The Spark price this power puts on <paramref name="card"/> right now, or
    /// 0. The static entry point <c>SparkCost.PowerPriceOf</c> calls, and the
    /// mirror of tier0 <c>combat.spark_power_price</c>: it finds the power on
    /// the CARD's own owner, so a second seat's Knight can never price this
    /// seat's Attacks.
    /// </summary>
    public static int PriceFor(CardModel card)
    {
        Creature? creature = SparkCost.OwnerCreatureOf(card);
        if (creature == null)
        {
            return 0;
        }

        var power = creature.Powers.OfType<SparkAttackCostPower>().FirstOrDefault();
        return power != null && power.Converts(card) ? Price : 0;
    }

    /// <summary>
    /// The rule's three clauses, and each one is a line -- tier0
    /// <c>spark_power_price</c>, same order, same reasons:
    ///
    ///   * ATTACKS ONLY. Skills and Powers keep their Energy cost untouched;
    ///     Energy becomes very nearly pure Skill currency, which is the payoff
    ///     loop the card is a bet on.
    ///   * "THAT DO NOT ALREADY COST [Spark]" -- sub-pick (a). A card printing
    ///     its own <c>spend_spark</c> keeps its printed price and this power
    ///     neither raises it nor adds to it. Sub-pick (b) would have re-priced
    ///     Fwoosh! from 1 to 3, punishing the very cards the archetype drafts.
    ///   * X-COST ATTACKS ARE EXEMPT, AND THE PACKET DOES NOT SAY SO. sec.5 is
    ///     silent on X; this is the reading taken and it goes back to [USER] in
    ///     sec.10.11 item 3. An X card's cost IS the energy it spends, so a flat
    ///     3-Spark conversion resolves it at X = 0 and it deals nothing --
    ///     exactly the reasoning R34 gave for the base rule's own X exemption,
    ///     reached again from the other side.
    ///
    /// Plus the ownership clause every fanned hook needs.
    /// </summary>
    private bool Converts(CardModel card) =>
        card.Type == CardType.Attack
        && !card.EnergyCost.CostsX
        && SparkCost.PrintedPriceOf(card) == 0
        && SparkCost.OwnerCreatureOf(card) == Owner;

    /// <summary>
    /// "…instead of their Energy cost." The Energy line goes to 0 for a
    /// converted Attack, whether or not the bank can pay the Sparks -- a brick
    /// under this power reads as "0 energy, 3 Sparks, and you have 1", not as a
    /// card whose printed cost lies until you can afford it.
    /// </summary>
    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (originalCost <= 0m || !Converts(card))
        {
            return false;
        }

        modifiedCost = 0m;
        return true;
    }

    /// <summary>
    /// The GATE. <c>Hook.ShouldPlay</c> walks every model in the combat and the
    /// first refusal wins, naming this power as the preventer; <c>CanPlay</c>
    /// then reports <c>UnplayableReason.BlockedByHook</c>. Mirrors tier0
    /// <c>card_playable</c>, which gates on <c>spark_price</c> and not on the
    /// printed half alone.
    /// </summary>
    public override bool ShouldPlay(CardModel card, AutoPlayType autoPlayType) =>
        !Converts(card) || SparkPower.CanSpend(Owner, Price);

    /// <summary>
    /// Transient decision state, set between a BeforeCardPlayed and its
    /// AfterCardPlayed. Same shape and same caveat as
    /// <c>SparkPower._pendingSpendPlay</c>: a stale reference on a clone can
    /// never equal a live CardPlay, so the worst case is a no-op.
    /// </summary>
    private CardPlay? _pendingSpendPlay;

    /// <summary>
    /// The spend DECISION, snapshotted at play start. tier0's <c>play_card</c>
    /// pays before the card's effects resolve, so a card whose own rider pushes
    /// the bank over mid-resolution must not change what it was charged --
    /// the Snap finding, recorded on <c>SparkPower.BeforeCardPlayed</c> and
    /// binding here for the same reason. <c>IsFirstInSeries</c> reproduces
    /// "once per play_card call" across replays.
    /// </summary>
    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        if (cardPlay.IsFirstInSeries && Converts(cardPlay.Card))
        {
            _pendingSpendPlay = cardPlay;
        }

        return Task.CompletedTask;
    }

    /// <summary>
    /// The payment, executing the play-time decision. Through
    /// <c>SparkPower.Spend</c> -- the same all-or-nothing payment a card that
    /// prints its own price uses, refusing through the same predicate
    /// <see cref="ShouldPlay"/> gates on, so the price shown, the price gated
    /// and the price paid are one number.
    ///
    /// AFTER resolution rather than before, for the ordering reason
    /// <c>SparkPower.AfterCardPlayed</c> records: mutating the bank first could
    /// drop it under a rule that is still being read.
    /// </summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay != _pendingSpendPlay)
        {
            return;
        }

        _pendingSpendPlay = null;
        await SparkPower.Spend(choiceContext, Owner, Price, cardPlay.Card);
    }
}
