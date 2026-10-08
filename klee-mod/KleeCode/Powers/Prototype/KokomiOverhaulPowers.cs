using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Elements;
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
/// Treatise (Kokomi core pass, 2026-09-27): "Once per turn, when you play a
/// card with a Plan line normally, draw 1 card." It pays for the other side of
/// the Plan choice -- playing the now-line -- where it used to pay for a
/// carry-out. "Normally" is <see cref="KokomiPlan.PlayedOnPet"/> answering no:
/// a card written on the Bake-Kurage draws nothing.
///
/// ONCE PER TURN on the ledger's shared latch
/// (<see cref="KokomiOverhaulLedger.ClaimOncePerTurn"/>), claimed before the
/// draw. Copies stack the amount: two copies draw 2, still once a turn.
/// Sim twin: <c>kokomi_plan.note_face_up_plan_card</c>.
/// </summary>
public sealed class TreatisePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Treatise"),
        ("description",
            "The first time each turn you play a card with a [gold]Plan[/gold] "
          + "line normally, draw [blue]{Amount}[/blue] card{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (Owner == null || Amount <= 0) return;
        if (cardPlay.Card.Owner?.Creature != Owner) return;
        if (cardPlay.Card is not IPlannedCard { PlanClauses.Count: > 0 }) return;
        if (KokomiPlan.PlayedOnPet(cardPlay)) return;
        var player = Owner.Player;
        if (player == null) return;
        if (!KokomiOverhaulLedger.ClaimOncePerTurn(Owner, nameof(TreatisePower)))
        {
            return;
        }
        await CardPileCmd.Draw(choiceContext, Amount, player);
    }
}

/// <summary>
/// Princess of Watatsumi, her Ancient, UNDER THE ARM (R276 hygiene):
/// "Whenever the Bake-Kurage carries out a Plan, gain 2 Block and draw 1
/// card." The shipped card grants Charge every turn, a resource this arm turns
/// off, so a Dusty Tome handed an arm run a dead pick.
/// <see cref="KleeMod.Cards.Kokomi.PrincessOfWatatsumi"/> applies this instead
/// of <see cref="ChargePerTurnPower"/> while the arm is live for her, and the
/// shipped behaviour is untouched off the arm.
///
/// EVERY PLAN, NOT ONCE A TURN: this is the one Ancient, the Tome's single
/// grant, and its printed text says "Whenever". The Block is POWERED (rule 3:
/// her Dexterity counts on what a Plan pays).
///
/// <see cref="PowerModel.Amount"/> is the Block; the draw is always 1.
/// Sim twin: <c>kokomi_plan.PRINCESS_OF_WATATSUMI</c>.
/// </summary>
public sealed class PrincessOfWatatsumiPlanPower
    : PowerModel, ILocalizationProvider, IKokomiPlanListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Princess of Watatsumi"),
        ("description",
            "Whenever the [gold]Bake-Kurage[/gold] carries out a "
          + "[gold]Plan[/gold], gain [blue]{Amount}[/blue] [gold]Block[/gold] "
          + "and draw 1 card."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task OnPlanResolved(
        PlayerChoiceContext choiceContext, Creature kokomi)
    {
        if (kokomi != Owner) return;                 // co-op: your plans only
        var player = Owner?.Player;
        if (Owner == null || player == null || Amount <= 0) return;
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Move, null);
        await CardPileCmd.Draw(choiceContext, 1, player);
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
/// THE COMPANION COUNTER MOVED OFF THIS HOOK (`EB-362`). It used to be
/// written here and ONLY here, which meant Chain of Command's "for each
/// Companion card you played last/this turn" read a permanent zero on any
/// board without The General's Banner in play -- the seat that found it had
/// declined the card outright (round-5 run 3, act 3, finding 7). The counter
/// is now <see cref="ProtoBakeKuragePower.AfterCardPlayed"/>'s, beside
/// <see cref="KokomiOverhaulLedger.NoteCompanionCard"/>, because rule 1
/// guarantees that marker is on her every turn of every combat and this Power
/// is a card she may never draw.
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
            "The first time each turn you play a [gold]Companion[/gold] card, apply "
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
/// PINCER's carry-out (R276 pick 1): "This turn, your first Attack is played
/// twice." The base game's replay surface (<c>ModifyCardPlayCount</c>), the
/// shape <see cref="ReplayNextCompanionPower"/> takes one card type over.
///
/// A WRITE NEITHER TAKES NOR SPENDS IT, Battle Plan's old rider's rule: a card
/// dragged onto the Bake-Kurage resolves none of its face, so it is not "an
/// Attack played" in the sense the face means -- and doubling a write would
/// queue the same Plan twice. Removed by the face-up Attack that spends it,
/// and at the end of her turn either way ("this turn"). Sim twin:
/// <c>kokomi_plan.FIRST_ATTACK_TWICE</c>.
/// </summary>
public sealed class FirstAttackTwicePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Pincer"),
        ("description",
            "This turn, your first Attack is played twice."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override int ModifyCardPlayCount(
        CardModel card, Creature? target, int playCount)
    {
        if (card.Type != CardType.Attack) return playCount;
        if (card.Owner?.Creature != Owner) return playCount;
        if (BakeKuragePet.Is(target)) return playCount;
        return playCount + 1;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card.Type != CardType.Attack) return;
        if (cardPlay.Card.Owner?.Creature != Owner) return;
        if (KokomiPlan.PlayedOnPet(cardPlay)) return;
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

/// <summary>
/// STOLEN CHAPTER's carry-out (R276 pick 1): "This turn, the first card you
/// play costs 0." The cost seam, which is handed no
/// <c>CardPlay</c> -- and needs none here: a card written on the Bake-Kurage IS
/// played and paid for, so the first card is the first card either way. An
/// auto-play pays nothing and does not spend it. Removed at the end of her
/// turn either way. Sim twin: <c>kokomi_plan.FIRST_CARD_FREE</c>.
/// </summary>
public sealed class FirstCardFreePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Stolen Chapter"),
        ("description",
            "This turn, the first card you play costs 0."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (card.Owner?.Creature != Owner) return false;
        if (originalCost <= 0m) return false;
        modifiedCost = 0m;
        return true;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card.Owner?.Creature != Owner) return;
        if (cardPlay.IsAutoPlay) return;
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

/// <summary>
/// NEREID'S ASCENSION (Rare Power, 2): "The Bake-Kurage carries out your
/// first Plan twice." `EB-492`, narrowed by `EB-655`.
///
/// A POWER, AND THAT IS THE WHOLE REDESIGN. The row it replaces was a Plan --
/// "Exhaust. Plan: for 2 turns, the Bake-Kurage carries out every Plan twice"
/// -- so the card that was meant to be the kit's payoff spent the morning it
/// was meant to pay: two energy, an Exhaust and a Plan slot, in a deck the r14
/// seat measured at two Plan cards to double
/// (`review/active/kokomi-pool-pass-2026-09-05.md` sec.1). As a Power it never
/// takes a morning, it lasts the fight instead of two turns, and its price is
/// two energy on a turn that writes no Plan.
///
/// IT STORES NOTHING AND HOOKS NOTHING:
/// <c>KokomiPlan.CarryOutTimes</c> asks for it at the one moment the question
/// can be asked -- inside the drain loop, before each entry -- and a hook would
/// have to reconstruct which Plans were still owed. The stack is a marker, so a
/// second copy doubles nothing further; "your first Plan twice" is what the
/// face says, and twice is twice.
///
/// THE BADGE SHOWS NO COUNT (2026-09-29). It was <c>Counter</c>, so a second
/// copy wore a "2" that promised a stack the rule never pays. It is
/// <see cref="PowerStackType.Single"/> now, the repo's shape for a power that
/// does not stack; the rule reads only whether it is worn, so nothing moves.
///
/// THE BRIEF'S RULE 3 IS THE ONE THIS BREAKS. "Every Plan is carried out once,
/// in order" is the arm's law and this Rare is the card the brief allows to
/// break it (brief sec.5); it breaks the ONCE and leaves the ORDER alone --
/// each Plan is carried out twice before the next one starts.
/// </summary>
public sealed class NereidsAscensionPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Nereid's Ascension"),
        ("description",
            "At the start of your turn, the [gold]Bake-Kurage[/gold] "
          + "carries out your first [gold]Plan[/gold] twice."
          + " Your first [gold]Dusk[/gold] [gold]Plan[/gold] is doubled too."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;
}
