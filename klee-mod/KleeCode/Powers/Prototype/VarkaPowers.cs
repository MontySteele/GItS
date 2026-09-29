using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Grand Master's Order (sec.10.3; sec.9.6: "repeats the next Knight card;
/// Knights' Muster counts, and the repeat may choose a different Knight").
/// The next Knight card played this turn is played Amount extra times, the
/// base game's replay surface (<c>ModifyCardPlayCount</c>), so a repeated
/// Muster asks its question again. <see cref="ReplayNextCompanionPower"/>'s
/// shape, one card kind narrower, and scoped to the turn it was played on the
/// same way.
/// </summary>
public sealed class GrandMastersOrderPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Grand Master's Order"),
        ("description",
            "The next [gold]Knight[/gold] you play this turn is played "
          + "{Amount} extra time{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override int ModifyCardPlayCount(
        CardModel card, Creature? target, int playCount)
    {
        if (!VarkaRules.IsKnight(card)) return playCount;
        if (card.Owner?.Creature != Owner) return playCount;
        return playCount + Amount;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!VarkaRules.IsKnight(cardPlay.Card)) return;
        if (cardPlay.Card?.Owner?.Creature != Owner) return;
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
/// Stormward Stance (sec.10.3): "While you hold 2 or more Winds, your Anemo
/// Attacks deal 3 more." An additive term on his own powered Attacks whose
/// hit is Anemo, read live, so a third Wind absorbed mid-turn turns it on for
/// the next Attack.
/// </summary>
public sealed class StormwardStancePower : PowerModel, ILocalizationProvider
{
    /// <summary>The Winds the Stance needs, printed on the card.</summary>
    public const int WindsNeeded = 2;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Stormward Stance"),
        ("description",
            "While you hold " + WindsNeeded + " or more [gold]Winds[/gold], "
          + "your [gold]Anemo[/gold] Attacks deal [blue]{Amount}[/blue] "
          + "additional damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The Stance's condition on primitives. PURE.</summary>
    public static bool Applies(bool poweredAttack, bool isAttackCard,
                               Element hit, int windsHeld) =>
        poweredAttack && isAttackCard && hit == Element.Anemo
        && windsHeld >= WindsNeeded;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == null || target == Owner) return 0m;
        return Applies(props.IsPoweredAttack(),
                       cardSource is { Type: CardType.Attack },
                       AuraCmd.ElementOfPlay(cardSource, dealer),
                       VarkaWinds.HeldCount(Owner))
            ? Amount : 0m;
    }
}

/// <summary>
/// Converging Winds (sec.10.3, the Gale archetype's Rare): "Your Swirls react
/// where they land", with sec.5's bounds: the spread hit is the flat 2
/// carrying the swirled element; a reaction it sets off lands on that enemy
/// only; a reaction from a spread never Swirls again; the struck enemy's own
/// flat 2 carries no element. A marker: the rule is carried out inside the
/// Swirl itself (<c>ReactionEffects.SwirlPays</c>), which asks
/// <see cref="Converges"/>.
/// </summary>
public sealed class ConvergingWindsPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Converging Winds"),
        ("description",
            "Your [gold]Swirls[/gold] react where they land. An "
          + "[gold]Elemental Reaction[/gold] a spread sets off hits only that "
          + "enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;

    /// <summary>Do this dealer's Swirls react where they land? PURE.</summary>
    public static bool Converges(Creature? dealer) =>
        VarkaPrototype.Enabled && dealer != null
        && dealer.HasPower<ConvergingWindsPower>();

    /// <summary>
    /// THE SPREAD'S ONE DECISION, on primitives: a copy of
    /// <paramref name="spread"/> arriving on an enemy wearing
    /// <paramref name="existing"/> reacts there, instead of replacing it,
    /// only under this power and only where the two elements react. A
    /// same-element body keeps its own aura (<c>TriggerRules.SpreadLands</c>)
    /// and a bare one takes the spent copy, both as without the power. PURE.
    /// </summary>
    public static Reaction SpreadReaction(bool converges, Element spread,
                                          Element existing)
    {
        if (!converges || existing == Element.None || existing == spread)
        {
            return Reaction.None;
        }
        var reaction = ReactionTable.Lookup(existing, spread);
        // "A reaction a spread sets off never Swirls again": the spread is an
        // aura element, so the table cannot answer Swirl -- stated anyway.
        return reaction == Reaction.Swirl ? Reaction.None : reaction;
    }
}

/// <summary>
/// Boreas Unbound (sec.10.3): "Whenever you Absorb, gain 1 Energy." Paid by
/// <see cref="VarkaAbsorb.Take"/>, the one place an Absorb happens; a hit that
/// Swirls because the Wind is already held is not an Absorb and pays nothing.
/// </summary>
public sealed class BoreasUnboundPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Boreas Unbound"),
        ("description",
            "Whenever you [gold]Absorb[/gold], gain [blue]{Amount}[/blue] "
          + "[gold]Energy[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task OnAbsorb(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        Flash();
        await PlayerCmd.GainEnergy(Amount, Owner.Player);
    }
}
