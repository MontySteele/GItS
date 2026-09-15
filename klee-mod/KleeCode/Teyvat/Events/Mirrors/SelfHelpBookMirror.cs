using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Enchantments;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Vfx;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// SELF-HELP BOOK, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/SelfHelpBook.cs` and cross-checked
/// against the frozen harvest (4 options: Read the Back, Read a Random
/// Passage, Read the Entire Book, Move On).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same three enchantments at the
/// same amount (`Sharp` 2 on an Attack, `Nimble` 2 on a Skill, `Swift` 2 on a
/// Power), the same six canonical vars naming them, the same one-card
/// selector under `CardSelectorPrefs.EnchantSelectionPrompt`, and the same
/// enchant VFX. Only the loc keys are derived instead of written out.
///
/// THIS IS THE FIRST MIRROR WITH LOCKED OPTIONS, and they are the reason the
/// generator's mirror ledger grew an `options` list. The base event offers a
/// reading only when the player HOLDS a card of that type to enchant and
/// substitutes an unclickable `_LOCKED` twin otherwise -- so seven option
/// keys exist and only FOUR are ever a player's choice. The face writes four
/// lines; the twins take their text from the readings they stand in for,
/// which is what an unaffordable option is: the same option, greyed.
///
/// AND `NO_OPTIONS` IS A REAL OPTION, not a fallback: when the player holds
/// nothing enchantable the base event offers exactly one clickable line that
/// finishes the event. The face's "Move On" is that line.
/// </summary>
public abstract class SelfHelpBookMirror : TeyvatEventMirror
{
    /// <summary>`SelfHelpBook.cs:32-40`, value for value: the three
    /// enchantment titles read off `ModelDb` so the dressing's prose can
    /// print them, and the three amounts, all 2.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new StringVar("Enchantment1", ModelDb.Enchantment<Sharp>().Title.GetFormattedText()),
            new StringVar("Enchantment2", ModelDb.Enchantment<Nimble>().Title.GetFormattedText()),
            new StringVar("Enchantment3", ModelDb.Enchantment<Swift>().Title.GetFormattedText()),
            new IntVar("Enchantment1Amount", 2m),
            new IntVar("Enchantment2Amount", 2m),
            new IntVar("Enchantment3Amount", 2m),
        };

    /// <summary>
    /// The base event's option construction, branch for branch
    /// (`SelfHelpBook.cs:42-79`): three availability checks first, then
    /// either the three readings -- each locked independently -- or the one
    /// `NO_OPTIONS` line when none of them is available.
    ///
    /// A LOCKED OPTION IS A NULL HANDLER, which is the base game's own idiom:
    /// `EventModel.ReplaceNullOptions` turns it into an unclickable row.
    /// </summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        List<EventOption> options = new List<EventOption>();
        bool hasAttack = PlayerHasCardsAvailable<Sharp>(Owner, CardType.Attack);
        bool hasSkill = PlayerHasCardsAvailable<Nimble>(Owner, CardType.Skill);
        bool hasPower = PlayerHasCardsAvailable<Swift>(Owner, CardType.Power);

        if (hasAttack || hasSkill || hasPower)
        {
            if (hasAttack)
            {
                options.Add(new EventOption(this, ReadTheBack, InitialOptionKey("READ_THE_BACK"),
                    HoverTipFactory.FromEnchantment<Sharp>(2)));
            }
            else
            {
                options.Add(new EventOption(this, null, InitialOptionKey("READ_THE_BACK_LOCKED")));
            }

            if (hasSkill)
            {
                options.Add(new EventOption(this, ReadPassage, InitialOptionKey("READ_PASSAGE"),
                    HoverTipFactory.FromEnchantment<Nimble>(2)));
            }
            else
            {
                options.Add(new EventOption(this, null, InitialOptionKey("READ_PASSAGE_LOCKED")));
            }

            if (hasPower)
            {
                options.Add(new EventOption(this, ReadEntireBook, InitialOptionKey("READ_ENTIRE_BOOK"),
                    HoverTipFactory.FromEnchantment<Swift>(2)));
            }
            else
            {
                options.Add(new EventOption(this, null, InitialOptionKey("READ_ENTIRE_BOOK_LOCKED")));
            }
        }
        else
        {
            options.Add(new EventOption(this, SkipBook, InitialOptionKey("NO_OPTIONS")));
        }

        return options;
    }

    /// <summary>`ReadTheBack`: Sharp 2 onto an Attack.</summary>
    private async Task ReadTheBack()
    {
        await SelectAndEnchant<Sharp>(2, CardType.Attack, L10NLookup(PageKey("READ_THE_BACK.description")));
    }

    /// <summary>`ReadPassage`: Nimble 2 onto a Skill.</summary>
    private async Task ReadPassage()
    {
        await SelectAndEnchant<Nimble>(2, CardType.Skill, L10NLookup(PageKey("READ_PASSAGE.description")));
    }

    /// <summary>`ReadEntireBook`: Swift 2 onto a Power.</summary>
    private async Task ReadEntireBook()
    {
        await SelectAndEnchant<Swift>(2, CardType.Power, L10NLookup(PageKey("READ_ENTIRE_BOOK.description")));
    }

    /// <summary>
    /// The base event's availability test: a card in the DECK, of the right
    /// type, that the enchantment can actually take.
    /// </summary>
    private bool PlayerHasCardsAvailable<T>(Player player, CardType typeRestriction)
        where T : EnchantmentModel
    {
        EnchantmentModel enchantment = ModelDb.Enchantment<T>();
        return PileType.Deck.GetPile(player).Cards
            .FirstOrDefault((CardModel c) => DeckFilter(c, enchantment, typeRestriction)) != null;
    }

    /// <summary>The base event's shared reading body: one card, enchanted,
    /// then the page the caller named.</summary>
    private async Task SelectAndEnchant<T>(int amount, CardType typeRestriction, LocString finalDescription)
        where T : EnchantmentModel
    {
        CardSelectorPrefs prefs = new CardSelectorPrefs(CardSelectorPrefs.EnchantSelectionPrompt, 1);
        EnchantmentModel enchantment = ModelDb.Enchantment<T>();
        CardModel card = (await CardSelectCmd.FromDeckForEnchantment(
            Owner, enchantment, amount, (CardModel c) => c.Type == typeRestriction, prefs)).FirstOrDefault();
        if (card != null)
        {
            await ApplyEnchantment<T>(card, amount);
        }

        SetEventFinished(finalDescription);
    }

    /// <summary>The base event's deck filter, clause for clause.</summary>
    private bool DeckFilter(CardModel card, EnchantmentModel enchantment, CardType type)
    {
        if (card.Pile.Type == PileType.Deck && card.Type == type)
        {
            return enchantment.CanEnchant(card);
        }

        return false;
    }

    /// <summary>The base event's enchant-and-show, including the VFX the
    /// player reads the result off.</summary>
    private Task ApplyEnchantment<T>(CardModel card, int amount) where T : EnchantmentModel
    {
        CardCmd.Enchant<T>(card, amount);
        NCardEnchantVfx vfx = NCardEnchantVfx.Create(card);
        if (vfx != null)
        {
            NRun.Instance?.GlobalUi.CardPreviewContainer.AddChildSafely(vfx);
        }

        return Task.CompletedTask;
    }

    /// <summary>`SkipBook`: the one line offered when nothing can be
    /// enchanted, which finishes the event and does nothing else.</summary>
    private Task SkipBook()
    {
        SetEventFinished(L10NLookup(PageKey("NO_OPTIONS.description")));
        return Task.CompletedTask;
    }
}
