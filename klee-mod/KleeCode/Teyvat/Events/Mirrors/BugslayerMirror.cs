using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// BUGSLAYER, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/Bugslayer.cs` and cross-checked against
/// the harvest (2 options: Extermination, Squash).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same two `StringVar`s putting
/// Exterminate's and Squash's own titles into the description, the same two
/// card hover tips, and the same shared `AddAndPreview&lt;T&gt;` -- create off
/// `RunState`, add to the DECK, preview for two seconds, finish.
///
/// THE TWO CARDS ARE THE BASE GAME'S AND KEEP THEIR GLOBAL ROWS. A dressing
/// renames the EVENT, never a card: the `StringVar`s read
/// `ModelDb.Card&lt;T&gt;().Title`, so the face's sentence names whatever the
/// shipped game calls them, in whatever language is loaded.
/// </summary>
public abstract class BugslayerMirror : TeyvatEventMirror
{
    /// <summary>`Bugslayer.cs:16-20`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new StringVar("Card1", ModelDb.Card<Exterminate>().Title),
            new StringVar("Card2", ModelDb.Card<Squash>().Title),
        };

    /// <summary>Two options, in the base event's order, each carrying its own
    /// card's hover tip.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Extermination, InitialOptionKey("EXTERMINATION"),
                HoverTipFactory.FromCardWithCardHoverTips<Exterminate>()),
            new EventOption(this, Squash, InitialOptionKey("SQUASH"),
                HoverTipFactory.FromCardWithCardHoverTips<Squash>()),
        };

    private async Task Extermination() =>
        await AddAndPreview<Exterminate>(L10NLookup(PageKey("EXTERMINATION.description")));

    private async Task Squash() =>
        await AddAndPreview<Squash>(L10NLookup(PageKey("SQUASH.description")));

    /// <summary>The base event's own helper: the card is created through the
    /// RUN's `CreateCard` (there is no combat state in an event room), added
    /// to the deck, and previewed for the base event's 2 seconds.</summary>
    private async Task AddAndPreview<T>(LocString loc) where T : CardModel
    {
        CardModel card = Owner.RunState.CreateCard<T>(Owner);
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck), 2f);
        SetEventFinished(loc);
    }
}
