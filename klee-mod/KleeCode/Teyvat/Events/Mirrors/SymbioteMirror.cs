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
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Enchantments;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.Vfx;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// SYMBIOTE, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/Symbiote.cs` and cross-checked against
/// the harvest (2 options: Approach, Kill With Fire).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same two vars, the same act-2-or-
/// later gate, the same `_LOCKED` substitution on the first option when the
/// deck holds nothing Corrupted can enchant, Corrupted's enchantment tip on
/// the live one and the static Transform tip on the second, the same
/// enchant-one-card-plus-VFX on Approach, and the same transform-`Cards`-cards
/// on Kill With Fire.
///
/// THE LOCKED TWIN IS A SEPARATE KEY AND A NULL HANDLER.
/// `SYMBIOTE.pages.INITIAL.options.APPROACH_LOCKED` is the same option greyed
/// out -- no `onChosen`, no hover tip -- so the generator writes it as an
/// `extra_options` row taking Approach's own face line. Both its `.title` and
/// `.description` are emitted, because an option key is a PREFIX wherever it
/// sits (EB-765).
///
/// THE GATE AND THE SUBSTITUTION ASK THE SAME QUESTION TWICE, and both are the
/// base event's: `IsAllowed` is not consulted again once the room is entered,
/// so an event that became unenchantable between the roll and the page still
/// needs the locked twin at build time.
///
/// THE TRANSFORM ROLLS OFF THE EVENT'S OWN `Rng`, which a dressed entry seeds
/// differently -- the same local, per-event divergence `ThisOrThatMirror`
/// documents, and not the tracked reward stream Potion Courier rolls on.
/// </summary>
public abstract class SymbioteMirror : TeyvatEventMirror
{
    /// <summary>The base event's own key name.</summary>
    private const string EnchantmentKey = "Enchantment";

    /// <summary>`Symbiote.cs:24-28`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new StringVar(EnchantmentKey,
                ModelDb.Enchantment<Corrupted>().Title.GetFormattedText()),
            new CardsVar(1),
        };

    /// <summary>The base event's gate: act 2 or later.</summary>
    public override bool IsAllowed(IRunState runState) => runState.CurrentActIndex > 0;

    /// <summary>Two options, in the base event's order. The first is the
    /// locked twin when nothing in the deck can take Corrupted.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        CardPile pile = PileType.Deck.GetPile(Owner);
        EventOption approach = !pile.Cards.Any(CanEnchant)
            ? new EventOption(this, null, InitialOptionKey("APPROACH_LOCKED"))
            : new EventOption(this, Approach, InitialOptionKey("APPROACH"),
                HoverTipFactory.FromEnchantment<Corrupted>());

        return new List<EventOption>
        {
            approach,
            new EventOption(this, KillWithFire, InitialOptionKey("KILL_WITH_FIRE"),
                HoverTipFactory.Static(StaticHoverTip.Transform)),
        };
    }

    /// <summary>`Approach`: one card enchanted with Corrupted, and the base
    /// event's two-guard VFX.</summary>
    private async Task Approach()
    {
        CardModel card = (await CardSelectCmd.FromDeckForEnchantment(
            player: Owner, enchantment: ModelDb.Enchantment<Corrupted>(), amount: 1,
            prefs: new CardSelectorPrefs(CardSelectorPrefs.EnchantSelectionPrompt, 1)))
            .FirstOrDefault();
        if (card != null)
        {
            CardCmd.Enchant<Corrupted>(card, 1m);
            NCardEnchantVfx vfx = NCardEnchantVfx.Create(card);
            if (vfx != null)
            {
                NRun.Instance?.GlobalUi.CardPreviewContainer.AddChildSafely(vfx);
            }
        }

        SetEventFinished(L10NLookup(PageKey("APPROACH.description")));
    }

    /// <summary>`KillWithFire`: `Cards` cards transformed, one at a time, off
    /// the event's own `Rng`.</summary>
    private async Task KillWithFire()
    {
        List<CardModel> cards = (await CardSelectCmd.FromDeckForTransformation(
            player: Owner,
            prefs: new CardSelectorPrefs(
                CardSelectorPrefs.TransformSelectionPrompt, DynamicVars.Cards.IntValue)))
            .ToList();
        foreach (CardModel card in cards)
        {
            await CardCmd.TransformToRandom(card, Rng, CardPreviewStyle.EventLayout);
        }

        SetEventFinished(L10NLookup(PageKey("KILL_WITH_FIRE.description")));
    }

    /// <summary>The base event's own predicate, static for the same reason:
    /// `Any` takes it as a method group.</summary>
    private static bool CanEnchant(CardModel card) =>
        ModelDb.Enchantment<Corrupted>().CanEnchant(card);
}
