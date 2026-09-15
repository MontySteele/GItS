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
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Enchantments;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.Vfx;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// WOOD CARVINGS, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/WoodCarvings.cs` and cross-checked
/// against the harvest (3 options: Bird, Snake, Torus).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same three vars naming Peck,
/// Slither and Toric Toughness, the same gate (every player holding a
/// removable BASIC card), the same three hover tips, the same
/// Basic-and-transformable filter on both transform branches, and the same
/// enchant VFX on the Snake one.
///
/// THIS IS WHY THE MIRROR LEDGER'S `options` LIST IS ORDERED BY THE LIST AND
/// NOT BY THE SOURCE. The base event builds the Snake option FIRST -- it is a
/// local, computed before the array literal, and the locked twin is the
/// ternary's first branch -- and then puts it SECOND, between Bird and Torus.
/// The index's literal scrape reads source order and reports
/// `SNAKE_LOCKED, SNAKE, BIRD, TORUS`; what the player sees, and what the
/// face's three lines are written against, is `BIRD, SNAKE, TORUS`. The spec
/// carries the second.
///
/// THE TRANSFORMS TARGET STARTER CARDS ONLY. Both Bird and Torus filter to
/// `CardRarity.Basic`, which is what the harvest's "1 starter card" means,
/// and the transform is to a NAMED card rather than a random one --
/// `CardCmd.TransformTo&lt;T&gt;`, not `TransformToRandom`.
/// </summary>
public abstract class WoodCarvingsMirror : TeyvatEventMirror
{
    /// <summary>`WoodCarvings.cs:27-32`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new StringVar("BirdCard", ModelDb.Card<Peck>().Title),
            new StringVar("SnakeEnchantment", ModelDb.Enchantment<Slither>().Title.GetFormattedText()),
            new StringVar("ToricCard", ModelDb.Card<ToricToughness>().Title),
        };

    /// <summary>The base event's gate: every player holding a Basic card that
    /// can actually be removed -- two of the three options transform one, and
    /// a deck with none would leave the room offering nothing.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) => CardPile.Get(PileType.Deck, p).Cards
            .Any((CardModel c) => c != null && c.Rarity == CardRarity.Basic && c.IsRemovable));

    /// <summary>
    /// Three options, in the order the base event PUTS them in -- Bird,
    /// Snake, Torus -- with the Snake one built first and locked when nothing
    /// in the deck can take Slither.
    /// </summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        IReadOnlyList<CardModel> cards = PileType.Deck.GetPile(Owner).Cards;
        EventOption snake = !cards.Any((CardModel c) => ModelDb.Enchantment<Slither>().CanEnchant(c))
            ? new EventOption(this, null, InitialOptionKey("SNAKE_LOCKED"))
            : new EventOption(this, Snake, InitialOptionKey("SNAKE"),
                HoverTipFactory.FromEnchantment<Slither>());

        return new List<EventOption>
        {
            new EventOption(this, Bird, InitialOptionKey("BIRD"),
                HoverTipFactory.FromCardWithCardHoverTips<Peck>()),
            snake,
            new EventOption(this, Torus, InitialOptionKey("TORUS"),
                HoverTipFactory.FromCardWithCardHoverTips<ToricToughness>()),
        };
    }

    /// <summary>`Bird`: one Basic, transformable card becomes Peck.</summary>
    private async Task Bird()
    {
        CardModel card = (await CardSelectCmd.FromDeckGeneric(
            Owner, new CardSelectorPrefs(CardSelectorPrefs.TransformSelectionPrompt, 1),
            (CardModel c) => c.IsTransformable && c.Rarity == CardRarity.Basic))
            .FirstOrDefault();
        if (card != null)
        {
            await CardCmd.TransformTo<Peck>(card, CardPreviewStyle.EventLayout);
        }

        SetEventFinished(L10NLookup(PageKey("BIRD.description")));
    }

    /// <summary>`Snake`: one Slither, with the base event's enchant
    /// VFX.</summary>
    private async Task Snake()
    {
        CardModel card = (await CardSelectCmd.FromDeckForEnchantment(
            Owner, ModelDb.Enchantment<Slither>(), 1,
            new CardSelectorPrefs(CardSelectorPrefs.EnchantSelectionPrompt, 1)))
            .FirstOrDefault();
        if (card != null)
        {
            CardCmd.Enchant<Slither>(card, 1m);
            NCardEnchantVfx vfx = NCardEnchantVfx.Create(card);
            if (vfx != null)
            {
                NRun.Instance?.GlobalUi.CardPreviewContainer.AddChildSafely(vfx);
            }
        }

        SetEventFinished(L10NLookup(PageKey("SNAKE.description")));
    }

    /// <summary>`Torus`: one Basic, transformable card becomes Toric
    /// Toughness. The null check in the predicate is the base event's own and
    /// the Bird branch does not carry it -- kept as written rather than made
    /// consistent, because consistency here would be an edit.</summary>
    private async Task Torus()
    {
        CardModel card = (await CardSelectCmd.FromDeckGeneric(
            Owner, new CardSelectorPrefs(CardSelectorPrefs.TransformSelectionPrompt, 1),
            (CardModel c) => c != null && c.IsTransformable && c.Rarity == CardRarity.Basic))
            .FirstOrDefault();
        if (card != null)
        {
            await CardCmd.TransformTo<ToricToughness>(card, CardPreviewStyle.EventLayout);
        }

        SetEventFinished(L10NLookup(PageKey("TORUS.description")));
    }
}
