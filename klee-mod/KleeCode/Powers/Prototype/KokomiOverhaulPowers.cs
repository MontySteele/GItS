using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Treatise: "Once per turn, when the Bake-Kurage carries out a Plan, draw 1
/// card." The card that turns the Tactician's delay into cards.
///
/// ONCE PER TURN SINCE 2026-09-02, and it is [USER]'s ruling off live play:
/// "Treatise looks too good (one draw per turn if a Plan fired might be ok;
/// one draw per Plan is too abuseable)." It used to pay on EVERY Plan carried
/// out, which a morning holding three Plans turned into three cards, and
/// Nereid's Ascension doubled again.
///
/// STILL ON THE PLAN BUS AND NOT ON THE TURN: the draw is owed only if a Plan
/// was actually carried out, so a turn she wrote nothing on still pays
/// nothing. The turn is the CAP, not the trigger.
///
/// THE LATCH IS THE LEDGER'S SHARED ONE
/// (<see cref="KokomiOverhaulLedger.ClaimOncePerTurn"/>), for the reason its
/// own header gives: the bus fires from <c>AfterPlayerTurnStart</c> for the
/// queue and from inside a card play for The Moon Overlooks the Waters' extra
/// resolution, and both are the same turn's one draw.
///
/// ONE PAYMENT PER PLAN, NOT PER CLAUSE, is unchanged underneath the cap, and
/// <see cref="KokomiPlan"/>'s resolution loop is what makes that true rather
/// than a comment here: War Council prints two clauses and is one Plan.
/// </summary>
public sealed class TreatisePower
    : PowerModel, ILocalizationProvider, IKokomiPlanListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Treatise"),
        ("description",
            "Once per turn, when the [gold]Bake-Kurage[/gold] carries out a "
          + "[gold]Plan[/gold], draw [blue]{Amount}[/blue] card{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task OnPlanResolved(
        PlayerChoiceContext choiceContext, Creature kokomi)
    {
        if (kokomi != Owner) return;                 // co-op: your plans only
        var player = Owner?.Player;
        if (player == null) return;
        if (!KokomiOverhaulLedger.ClaimOncePerTurn(Owner, nameof(TreatisePower)))
        {
            return;
        }
        await CardPileCmd.Draw(choiceContext, Amount, player);
    }
}

/// <summary>
/// Song of Pearls: "Once per turn, when the Bake-Kurage carries out a Plan,
/// gain 3 Block." Treatise's defensive twin, on the same bus, priced in the
/// same unit and capped the same way.
///
/// ONCE PER TURN SINCE 2026-09-02, and [USER] ruled it in one word --
/// "Likewise" -- of Treatise's own verdict: the two cards are the same shape,
/// so a fix that left one of them paying per Plan would just move the
/// abusable line onto the other.
///
/// THE BLOCK IS POWERED (<c>ValueProp.Move</c>) for the reason a planned Block
/// is: rule 3 says "your Strength and Dexterity count, since the plans are
/// hers", and this Block is paid out BY a Plan. The alternative --
/// <c>Unpowered</c>, the NC-11 power-sourced line -- would make the same
/// morning's Block from Read the Field and from this card scale differently,
/// which nothing printed says.
/// </summary>
public sealed class SongOfPearlsPower
    : PowerModel, ILocalizationProvider, IKokomiPlanListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Song of Pearls"),
        ("description",
            "Once per turn, when the [gold]Bake-Kurage[/gold] carries out a "
          + "[gold]Plan[/gold], gain [blue]{Amount}[/blue] [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task OnPlanResolved(
        PlayerChoiceContext choiceContext, Creature kokomi)
    {
        if (kokomi != Owner) return;                 // co-op: your plans only
        if (Owner == null || Amount <= 0) return;
        if (!KokomiOverhaulLedger.ClaimOncePerTurn(
                Owner, nameof(SongOfPearlsPower)))
        {
            return;
        }
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Move, null);
    }
}

/// <summary>
/// The Moon Overlooks the Waters (Rare): "Plans also happen now." Rule 2's
/// delay is gone.
///
/// It stores nothing and hooks nothing. <see cref="KokomiPlan.Schedule"/> asks
/// for it at the one moment the question can be asked -- as a Plan is written
/// -- because the extra resolution is a property of the WRITING, and a hook
/// would have to reconstruct which Plans were new.
/// </summary>
public sealed class PlansAlsoNowPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "The Moon Overlooks the Waters"),
        ("description", "[gold]Plans[/gold] also happen when played."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// The Clouds Like Waves Rippling (Rare): "Whenever you apply a debuff to an
/// enemy, gain 2 Block."
///
/// THE SAME EVENT THE CASKET READS, through the same one predicate
/// (<see cref="KokomiOverhaulKit.IsHerDebuffOnEnemy"/>), so the relic and this
/// card can never disagree about what applying a debuff was. That matters here
/// more than anywhere: the pool's status lines feed the relic ON PURPOSE
/// (slice sec.4), so a player holding both is meant to see two things happen
/// off one clause.
///
/// PER APPLICATION, NOT PER STACK. `War Council`'s "apply 1 Weak to each" over
/// three enemies is three applications and three payouts; one card applying 2
/// Weak to one enemy is one.
/// </summary>
public sealed class CloudsLikeWavesPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "The Clouds Like Waves Rippling"),
        ("description",
            "Whenever you apply a debuff to an enemy, gain [blue]{Amount}[/blue] "
          + "[gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPowerAmountChanged(
        PlayerChoiceContext choiceContext, PowerModel power, decimal amount,
        Creature? applier, CardModel? cardSource)
    {
        if (Owner == null || Amount <= 0) return;
        if (!KokomiOverhaulKit.IsHerDebuffOnEnemy(power, amount, applier, Owner))
        {
            return;
        }
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Move, null);
    }
}

/// <summary>
/// The General's Banner: "Once per turn, when you play a Companion card, apply
/// 1 Weak to the front enemy."
///
/// ONCE PER TURN SINCE 2026-09-02 ([USER], live: "The General's Banner applies
/// a LOT of Weak. Probably too strong."). It used to pay per PLAY, which a
/// Commander hand full of Companions turned into a stack of Weak nothing else
/// in the arm can match, and a replayed Companion paid twice on top.
///
/// THE COMPANION COUNTER IS NOT CAPPED WITH IT, and the two lines below are
/// deliberately in this order: <see cref="KokomiOverhaulLedger"/> counts EVERY
/// Companion play because that count is Chain of Command's ("for each
/// Companion card you played last turn"), and this hook is its only writer.
/// Capping the count with the Weak would have silently re-priced a different
/// card.
///
/// THE FRONT ENEMY IS <see cref="KokomiPlan.FrontEnemy"/>'s, which is the same
/// reader a planned hit uses -- so "the front enemy" means one thing in this
/// arm and is defined once.
/// </summary>
public sealed class GeneralsBannerPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "The General's Banner"),
        ("description",
            "Once per turn, when you play a [gold]Companion[/gold] card, apply "
          + "[blue]{Amount}[/blue] [gold]Weak[/gold] to the front enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card is not ICompanionCard) return;
        if (cardPlay.Card.Owner?.Creature != Owner) return;
        if (Owner == null || Amount <= 0) return;
        KokomiOverhaulLedger.For(Owner).NoteCompanionPlayed();
        var front = KokomiPlan.FrontEnemy(Owner);
        // The claim is taken AFTER the board question, so a Companion played
        // on an empty board does not spend the turn's Weak on nothing.
        if (front == null) return;
        if (!KokomiOverhaulLedger.ClaimOncePerTurn(
                Owner, nameof(GeneralsBannerPower)))
        {
            return;
        }
        await PowerCmd.Apply<WeakPower>(
            choiceContext, front, Amount, applier: Owner, cardSource: null);
    }
}

/// <summary>
/// Rally's grant: "The next Companion card you play this turn costs 1 less."
///
/// A DISCOUNT, NOT A ZEROING, and that is draft 6's change from draft 2's
/// Vanguard: the card prints "costs 1 less", so this SUBTRACTS and floors at
/// zero. Setting the cost would be a different card on an expensive Companion.
///
/// THE SHAPE IS <c>CompanionCostThisTurnPower</c>'s and
/// <c>ReplayNextCompanionPower</c>'s, taken together and for their own reasons:
/// the cost move rides <c>TryModifyEnergyCostInCombat</c> (the same surface the
/// Spark zeroing uses) and the grant is consumed by the next Companion play and
/// expires at the END of the turn it was written on -- the ratified same-turn
/// boundary (FLAG-1 / R114, family X11), which is what "this turn" says.
/// </summary>
public sealed class NextCompanionDiscountPower : PowerModel, ILocalizationProvider
{
    /// <summary>How much the next Companion is discounted by. A rule's number
    /// and not a card's: Rally prints it, but the power carries it, so it is
    /// mirrored by value from tier0 the way every other rule number is.</summary>
    public const int Discount = 1;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Rally"),
        ("description",
            "The next [gold]Companion[/gold] card you play this turn costs "
          + "[blue]" + Discount + "[/blue] less."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (card is not ICompanionCard) return false;
        if (card.Owner?.Creature != Owner) return false;
        if (originalCost <= 0m) return false;
        modifiedCost = System.Math.Max(0m, originalCost - Discount);
        return true;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card is not ICompanionCard) return;
        if (cardPlay.Card.Owner?.Creature != Owner) return;
        if (!cardPlay.IsLastInSeries) return;
        await PowerCmd.Remove(this);
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}
