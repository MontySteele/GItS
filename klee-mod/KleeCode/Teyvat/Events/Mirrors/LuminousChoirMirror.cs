using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Gold;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// LUMINOUS CHOIR, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/LuminousChoir.cs` and cross-checked
/// against the harvest (2 options: Reach into the Flesh, Offer Tribute).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `GoldVar(149)` marked down
/// by `Rng.NextInt(0, 50)` in `CalculateVars` -- which is what makes the
/// harvest's 99-149 band -- the same gate (every player able to pay AND with
/// relics left in the grab bag), the same two-card removal plus Spore Mind on
/// the first option, and the same pay-then-pull-from-the-front on the second.
///
/// THE GATE READS THE VAR AFTER THE MARKDOWN, which is the base event's own
/// ordering and is why the mirror does not inline 149: `IsAllowed` compares
/// against `DynamicVars.Gold.BaseValue`, and that value has already been
/// rolled down by the time a room is validated.
///
/// THE TRIBUTE OPTION LOCKS RATHER THAN DISAPPEARS. A player short of the
/// price is offered `OFFER_TRIBUTE_LOCKED` with a null handler -- the base
/// game's idiom for a greyed row -- so the page always shows two lines. It
/// has no face line of its own and takes the Offer Tribute line's, which is
/// what an unaffordable option is.
///
/// THE RELIC COMES OFF THE FRONT OF THE RUN'S QUEUE, not from a fresh roll,
/// so it is the same relic the base event would have granted on the same
/// seed.
/// </summary>
public abstract class LuminousChoirMirror : TeyvatEventMirror
{
    /// <summary>`LuminousChoir.cs:20`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new GoldVar(149) };

    /// <summary>
    /// The base event's gate, both clauses: every player can pay the rolled
    /// price, and every player still has relics available to be granted --
    /// the second because the Offer Tribute branch pulls one and an empty bag
    /// would have taken the gold for nothing.
    /// </summary>
    public override bool IsAllowed(IRunState runState)
    {
        IRunState state = runState;
        return state.Players.All((Player p) =>
            (decimal)p.Gold >= DynamicVars.Gold.BaseValue && p.RelicGrabBag.HasAvailableRelics(state));
    }

    /// <summary>The base event's markdown: 0-49 off the 149
    /// (`NextInt` is exclusive at the top).</summary>
    public override void CalculateVars()
    {
        DynamicVars.Gold.BaseValue -= (decimal)Rng.NextInt(0, 50);
    }

    /// <summary>
    /// Two options, in the base event's order, under its names: the flesh,
    /// with Spore Mind's card hover tip, and then the tribute -- offered or
    /// locked on the owner's own purse.
    /// </summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        List<EventOption> options = new List<EventOption>
        {
            new EventOption(this, ReachIntoTheFlesh, InitialOptionKey("REACH_INTO_THE_FLESH"),
                HoverTipFactory.FromCardWithCardHoverTips<SporeMind>()),
        };

        if (Owner.Gold >= DynamicVars.Gold.IntValue)
        {
            options.Add(new EventOption(this, OfferTribute, InitialOptionKey("OFFER_TRIBUTE")));
        }
        else
        {
            options.Add(new EventOption(this, null, InitialOptionKey("OFFER_TRIBUTE_LOCKED")));
        }

        return options;
    }

    /// <summary>`ReachIntoTheFlesh`: two cards out of the deck, then the
    /// curse in.</summary>
    private async Task ReachIntoTheFlesh()
    {
        List<CardModel> cards = (await CardSelectCmd.FromDeckForRemoval(
            player: Owner, prefs: new CardSelectorPrefs(CardSelectorPrefs.RemoveSelectionPrompt, 2)))
            .ToList();
        await CardPileCmd.RemoveFromDeck(cards);
        await CardPileCmd.AddCurseToDeck<SporeMind>(Owner);
        SetEventFinished(L10NLookup(PageKey("REACH_INTO_THE_FLESH.description")));
    }

    /// <summary>`OfferTribute`: the gold spent, then the relic off the front
    /// of the queue.</summary>
    private async Task OfferTribute()
    {
        await PlayerCmd.LoseGold(DynamicVars.Gold.IntValue, Owner, GoldLossType.Spent);
        RelicModel relic = RelicFactory.PullNextRelicFromFront(Owner).ToMutable();
        await RelicCmd.Obtain(relic, Owner);
        SetEventFinished(L10NLookup(PageKey("OFFER_TRIBUTE.description")));
    }
}
