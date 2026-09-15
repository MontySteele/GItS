using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// SPIRIT GRAFTER, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/SpiritGrafter.cs` and cross-checked
/// against the harvest (2 options: Let It In, Rejection).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same two NAMED canonical vars
/// (`HpLossVar("RejectionHpLoss", 10)` and `HealVar("LetItInHealAmount", 25)`
/// -- named rather than canonical because the description prints both and a
/// canonical pair would collide on the lookup), Metamorphosis's card hover tip
/// on the first option and the damage annotation on the second, the same
/// heal-then-add on Let It In, and the same
/// upgrade-one-card-then-take-10-unblockable on Rejection, in that order.
///
/// THE ORDER ON REJECTION IS LOAD-BEARING. The upgrade grid comes FIRST and
/// the HP comes after it, so a player who is killed by the 10 has already
/// banked the upgrade; a mirror that swapped them would change what a dying
/// run keeps. `ThatDoesDamage` on the option is the annotation the option row
/// prints, and the real hit is the `CreatureCmd.Damage` in the handler --
/// both, as the base event has both.
///
/// THE CARD IS THE BASE GAME'S METAMORPHOSIS with its global row, and the
/// upgrade selection uses the engine's own `UpgradeSelectionPrompt`, not a
/// dressed one: a dressing writes the event's pages, and the card-grid header
/// is the engine's furniture.
/// </summary>
public abstract class SpiritGrafterMirror : TeyvatEventMirror
{
    /// <summary>The base event's own key names for its two named vars.</summary>
    private const string RejectionHpLossKey = "RejectionHpLoss";

    private const string LetItInHealAmountKey = "LetItInHealAmount";

    /// <summary>`SpiritGrafter.cs:22-26`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new HpLossVar(RejectionHpLossKey, 10m),
            new HealVar(LetItInHealAmountKey, 25m),
        };

    /// <summary>Two options, in the base event's order, with Metamorphosis's
    /// hover tip on the first and the HP annotation on the second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, LetItIn, InitialOptionKey("LET_IT_IN"),
                HoverTipFactory.FromCardWithCardHoverTips<Metamorphosis>()),
            new EventOption(this, Rejection, InitialOptionKey("REJECTION"))
                .ThatDoesDamage(DynamicVars[RejectionHpLossKey].BaseValue),
        };

    /// <summary>`LetItIn`: the heal, then Metamorphosis into the deck.</summary>
    private async Task LetItIn()
    {
        await CreatureCmd.Heal(Owner.Creature, DynamicVars[LetItInHealAmountKey].BaseValue);
        CardModel card = Owner.RunState.CreateCard<Metamorphosis>(Owner);
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck));
        SetEventFinished(L10NLookup(PageKey("LET_IT_IN.description")));
    }

    /// <summary>`Rejection`: the upgrade grid FIRST, then the unblockable,
    /// unpowered 10.</summary>
    private async Task Rejection()
    {
        CardModel card = (await CardSelectCmd.FromDeckForUpgrade(
            Owner, new CardSelectorPrefs(CardSelectorPrefs.UpgradeSelectionPrompt, 1)))
            .FirstOrDefault();
        if (card != null)
        {
            CardCmd.Upgrade(card);
        }

        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature,
            DynamicVars[RejectionHpLossKey].BaseValue,
            ValueProp.Unblockable | ValueProp.Unpowered, null, null);
        SetEventFinished(L10NLookup(PageKey("REJECTION.description")));
    }
}
