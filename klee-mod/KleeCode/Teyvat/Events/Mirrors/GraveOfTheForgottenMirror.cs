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
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Vfx;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// GRAVE OF THE FORGOTTEN, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/GraveOfTheForgotten.cs` and cross-checked
/// against the harvest (2 options: Confront, Accept).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same three `StringVar`s, the same
/// gate -- every player holding a card Soul's Power can enchant -- the same
/// `_LOCKED` substitution on Confront, the same CONCATENATED hover tips on the
/// live Confront (Soul's Power's, then Decay's) and Forgotten Soul's relic tip
/// on Accept, the same curse-THEN-enchant on Confront, and the same relic on
/// Accept.
///
/// THE CURSE COMES BEFORE THE ENCHANT GRID, which is the clause worth naming:
/// Decay is added to the deck FIRST, so the card the player then picks to
/// enchant may be the Decay they were just handed. Reordering the two lines
/// reads as tidying and removes a real option.
///
/// `HasEnchantableCards` IS ASKED TWICE, in the gate and in the option build,
/// and both are the base event's -- `IsAllowed` is not re-consulted once the
/// room is entered, so the locked twin still has to exist. It is an INSTANCE
/// method here as it is there, because the gate hands it to `All` as a method
/// group over players while the option build calls it on `Owner`.
/// </summary>
public abstract class GraveOfTheForgottenMirror : TeyvatEventMirror
{
    /// <summary>The base event's own key names.</summary>
    private const string EnchantmentKey = "Enchantment";

    private const string RelicKey = "Relic";

    private const string CurseKey = "Curse";

    /// <summary>`GraveOfTheForgotten.cs:29-34`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new StringVar(RelicKey, ModelDb.Relic<ForgottenSoul>().Title.GetFormattedText()),
            new StringVar(EnchantmentKey,
                ModelDb.Enchantment<SoulsPower>().Title.GetFormattedText()),
            new StringVar(CurseKey, ModelDb.Card<Decay>().Title),
        };

    /// <summary>The base event's gate: every player holds a card Soul's Power
    /// can enchant.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All(HasEnchantableCards);

    /// <summary>Two options, in the base event's order. The first is the
    /// locked twin when nothing in the deck can take Soul's Power.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        EventOption confront = !HasEnchantableCards(Owner)
            ? new EventOption(this, null, InitialOptionKey("CONFRONT_LOCKED"))
            : new EventOption(this, Confront, InitialOptionKey("CONFRONT"),
                HoverTipFactory.FromEnchantment<SoulsPower>()
                    .Concat(HoverTipFactory.FromCardWithCardHoverTips<Decay>()));

        return new List<EventOption>
        {
            confront,
            new EventOption(this, Accept, InitialOptionKey("ACCEPT"),
                HoverTipFactory.FromRelic<ForgottenSoul>()),
        };
    }

    /// <summary>`Confront`: the Decay FIRST -- so it is itself enchantable --
    /// then one card enchanted with Soul's Power, with the base event's
    /// two-guard VFX.</summary>
    private async Task Confront()
    {
        await CardPileCmd.AddCurseToDeck<Decay>(Owner);
        CardModel card = (await CardSelectCmd.FromDeckForEnchantment(
            Owner, ModelDb.Enchantment<SoulsPower>(), 1,
            new CardSelectorPrefs(CardSelectorPrefs.EnchantSelectionPrompt, 1)))
            .FirstOrDefault();
        if (card != null)
        {
            CardCmd.Enchant<SoulsPower>(card, 1m);
            NCardEnchantVfx vfx = NCardEnchantVfx.Create(card);
            if (vfx != null)
            {
                NRun.Instance?.GlobalUi.CardPreviewContainer.AddChildSafely(vfx);
            }
        }

        SetEventFinished(L10NLookup(PageKey("CONFRONT.description")));
    }

    /// <summary>`Accept`: the relic.</summary>
    private async Task Accept()
    {
        await RelicCmd.Obtain<ForgottenSoul>(Owner);
        SetEventFinished(L10NLookup(PageKey("ACCEPT.description")));
    }

    /// <summary>The base event's own, and an INSTANCE method as it is
    /// there.</summary>
    private bool HasEnchantableCards(Player player)
    {
        IReadOnlyList<CardModel> cards = PileType.Deck.GetPile(player).Cards;
        return cards.Any((CardModel c) => ModelDb.Enchantment<SoulsPower>().CanEnchant(c));
    }
}
