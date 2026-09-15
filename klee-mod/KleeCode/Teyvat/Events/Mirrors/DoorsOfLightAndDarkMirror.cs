using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Extensions;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// DOORS OF LIGHT AND DARK, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/DoorsOfLightAndDark.cs` and cross-checked
/// against the harvest (2 options: Light, Dark).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `CardsVar(2)`, no act gate,
/// the same `StableShuffle` off the EVENT's rng taking `Cards` upgradable
/// cards on the first option, and the same one-card removal on the second.
///
/// THE LIGHT BRANCH SHUFFLES AND TAKES rather than sampling twice, which is
/// the base event's own shape and is what makes "2 random cards" never the
/// same card twice. The shuffle is `StableShuffle`, so in co-op every client
/// resolves the same two.
///
/// NEITHER BRANCH IS ASYNC BECAUSE IT NEEDS TO BE. `Light` returns
/// `Task.CompletedTask` in the base event -- the upgrades are synchronous --
/// and the mirror keeps that rather than making it uniform with `Dark`.
/// </summary>
public abstract class DoorsOfLightAndDarkMirror : TeyvatEventMirror
{
    /// <summary>`DoorsOfLightAndDark.cs:15`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new CardsVar(2) };

    /// <summary>Two options, in the base event's order, under its
    /// names.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Light, InitialOptionKey("LIGHT")),
            new EventOption(this, Dark, InitialOptionKey("DARK")),
        };

    /// <summary>`Light`: `Cards` upgradable cards, shuffled and taken.</summary>
    private Task Light()
    {
        IEnumerable<CardModel> chosen = PileType.Deck.GetPile(Owner).Cards
            .Where((CardModel c) => c?.IsUpgradable ?? false)
            .ToList()
            .StableShuffle(Rng)
            .Take(DynamicVars.Cards.IntValue);
        foreach (CardModel card in chosen)
        {
            CardCmd.Upgrade(card);
        }

        SetEventFinished(L10NLookup(PageKey("LIGHT.description")));
        return Task.CompletedTask;
    }

    /// <summary>`Dark`: one chosen card out of the deck.</summary>
    private async Task Dark()
    {
        List<CardModel> cards = (await CardSelectCmd.FromDeckForRemoval(
            player: Owner, prefs: new CardSelectorPrefs(CardSelectorPrefs.RemoveSelectionPrompt, 1)))
            .ToList();
        await CardPileCmd.RemoveFromDeck(cards);
        SetEventFinished(L10NLookup(PageKey("DARK.description")));
    }
}
