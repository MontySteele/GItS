using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Enchantments;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Vfx;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// SAPPHIRE SEED, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/SapphireSeed.cs` and cross-checked
/// against the harvest (2 options: Eat, Plant).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same two vars (Sown's title, and
/// a `HealVar(9)`), no act gate, the same heal-then-upgrade on the first
/// option, and the same PRE-FILTERED enchant list on the second.
///
/// THE PLANT BRANCH FILTERS THE DECK ITSELF rather than handing the selector
/// a predicate, which is the base event's own shape and not a tidy-up: it
/// builds the list of cards `Sown` can take and passes that list, where the
/// Self-Help Book hands over a predicate instead. Both reach
/// `CardSelectCmd.FromDeckForEnchantment`; the difference is which overload,
/// and a mirror that picked the other one would have changed which cards the
/// grid shows when a card is enchantable but not in the deck.
/// </summary>
public abstract class SapphireSeedMirror : TeyvatEventMirror
{
    /// <summary>`SapphireSeed.cs:21-25`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new StringVar("Enchantment", ModelDb.Enchantment<Sown>().Title.GetFormattedText()),
            new HealVar(9m),
        };

    /// <summary>Two options, in the base event's order, under its names, with
    /// Sown's enchantment tip on the second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Eat, InitialOptionKey("EAT")),
            new EventOption(this, Plant, InitialOptionKey("PLANT"),
                HoverTipFactory.FromEnchantment<Sown>()),
        };

    /// <summary>`Eat`: the heal, then one chosen card upgraded.</summary>
    private async Task Eat()
    {
        await CreatureCmd.Heal(Owner.Creature, DynamicVars.Heal.IntValue);
        CardModel card = (await CardSelectCmd.FromDeckForUpgrade(
            Owner, new CardSelectorPrefs(CardSelectorPrefs.UpgradeSelectionPrompt, 1)))
            .FirstOrDefault();
        if (card != null)
        {
            CardCmd.Upgrade(card);
        }

        SetEventFinished(L10NLookup(PageKey("EAT.description")));
    }

    /// <summary>`Plant`: one Sown onto a card the enchantment can take, with
    /// the base event's enchant VFX.</summary>
    private async Task Plant()
    {
        EnchantmentModel sown = ModelDb.Enchantment<Sown>();
        List<CardModel> cards = PileType.Deck.GetPile(Owner).Cards
            .Where((CardModel c) => sown.CanEnchant(c)).ToList();
        CardModel card = (await CardSelectCmd.FromDeckForEnchantment(
            cards: cards, enchantment: sown, amount: 1,
            prefs: new CardSelectorPrefs(CardSelectorPrefs.EnchantSelectionPrompt, 1)))
            .FirstOrDefault();
        if (card != null)
        {
            CardCmd.Enchant<Sown>(card, 1m);
            NCardEnchantVfx vfx = NCardEnchantVfx.Create(card);
            if (vfx != null)
            {
                NRun.Instance?.GlobalUi.CardPreviewContainer.AddChildSafely(vfx);
            }
        }

        SetEventFinished(L10NLookup(PageKey("PLANT.description")));
    }
}
