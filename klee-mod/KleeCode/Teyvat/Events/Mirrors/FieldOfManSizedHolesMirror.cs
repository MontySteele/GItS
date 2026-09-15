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
using MegaCrit.Sts2.Core.Nodes.Vfx;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// FIELD OF MAN-SIZED HOLES, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/FieldOfManSizedHoles.cs` and
/// cross-checked against the harvest (2 options: Resist, Enter Your Hole).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same four canonical vars, the same
/// gate -- every player must hold at least one card Perfect Fit CAN enchant --
/// Normality's card hover tip on the first option and Perfect Fit's
/// enchantment tip on the second, the same remove-two-then-take-Normality on
/// Resist, and the same enchant-one-with-Perfect-Fit plus its VFX on Enter
/// Your Hole.
///
/// THE GATE ASKS THE ENCHANTMENT, NOT THE EVENT. `ModelDb.Enchantment&lt;PerfectFit&gt;().CanEnchant`
/// is handed to `Any` as a predicate, so what the event is allowed to do is
/// whatever Perfect Fit says it can do -- a mirror that re-stated the rule in
/// its own terms would drift the first time the enchantment changed.
///
/// THE REMOVAL COUNT IS THE `CardsVar`, not a literal 2: the grid is opened
/// for `DynamicVars.Cards.IntValue` cards and the description prints the same
/// var, which is what keeps the page and the grid agreeing.
///
/// THE VFX IS GUARDED TWICE, and both guards are the base event's: `Create`
/// may answer null, and the container is reached through `NRun.Instance?`
/// because the run's global UI can be gone by the time the grid closes.
/// </summary>
public abstract class FieldOfManSizedHolesMirror : TeyvatEventMirror
{
    /// <summary>`FieldOfManSizedHoles.cs:21-27`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new GoldVar(75),
            new CardsVar(2),
            new StringVar("ResistCurse", ModelDb.Card<Normality>().Title),
            new StringVar("Enchantment",
                ModelDb.Enchantment<PerfectFit>().Title.GetFormattedText()),
        };

    /// <summary>The base event's gate: every player holds a card Perfect Fit
    /// can enchant.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) =>
            CardPile.Get(PileType.Deck, p).Cards.Any(ModelDb.Enchantment<PerfectFit>().CanEnchant));

    /// <summary>Two options, in the base event's order, with Normality's card
    /// tip on the first and Perfect Fit's enchantment tip on the
    /// second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Resist, InitialOptionKey("RESIST"),
                HoverTipFactory.FromCardWithCardHoverTips<Normality>()),
            new EventOption(this, EnterYourHole, InitialOptionKey("ENTER_YOUR_HOLE"),
                HoverTipFactory.FromEnchantment<PerfectFit>()),
        };

    /// <summary>`Resist`: the removal grid for `Cards` cards, the removal,
    /// then one Normality.</summary>
    private async Task Resist()
    {
        List<CardModel> cards = (await CardSelectCmd.FromDeckForRemoval(
            player: Owner,
            prefs: new CardSelectorPrefs(
                CardSelectorPrefs.RemoveSelectionPrompt, DynamicVars.Cards.IntValue))).ToList();
        await CardPileCmd.RemoveFromDeck(cards);
        await CardPileCmd.AddCursesToDeck(
            new List<CardModel> { ModelDb.Card<Normality>() }, Owner);
        SetEventFinished(L10NLookup(PageKey("RESIST.description")));
    }

    /// <summary>`EnterYourHole`: one card enchanted with Perfect Fit, and the
    /// base event's two-guard VFX.</summary>
    private async Task EnterYourHole()
    {
        CardModel card = (await CardSelectCmd.FromDeckForEnchantment(
            Owner, ModelDb.Enchantment<PerfectFit>(), 1,
            new CardSelectorPrefs(CardSelectorPrefs.EnchantSelectionPrompt, 1)))
            .FirstOrDefault();
        if (card != null)
        {
            CardCmd.Enchant<PerfectFit>(card, 1m);
            NCardEnchantVfx vfx = NCardEnchantVfx.Create(card);
            if (vfx != null)
            {
                NRun.Instance?.GlobalUi.CardPreviewContainer.AddChildSafely(vfx);
            }
        }

        SetEventFinished(L10NLookup(PageKey("ENTER_YOUR_HOLE.description")));
    }
}
