using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// INFESTED AUTOMATON, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/InfestedAutomaton.cs` and cross-checked
/// against the harvest (2 options: Study, Touch Core).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: no canonical vars, the same two
/// `CardCreationOptions.ForNonCombatWithDefaultOdds` over the character's OWN
/// card pool, the same two predicates -- a Power on the first, a canonical
/// zero-cost that is not X on the second -- the same
/// `WithFlags(NoCardPoolModifications)` on the second and none on the first,
/// the same `FirstOrDefault()?.Card` null guard, and the same 1.2-second
/// `EventLayout` preview.
///
/// THE TWO PREDICATES DIFFER IN MORE THAN THEIR TEST, and the difference is
/// the point of the second option: `NoCardPoolModifications` is what keeps a
/// zero-cost pull from moving the run's pool state, so the mirror carries the
/// flag on exactly the option the base event carries it on.
///
/// THE CARD COMES FROM THE PLAYER'S CHARACTER POOL, so a dressed Infested
/// Automaton offers whatever the roster character in the seat can be offered.
/// A dressing changes the nation on the page, not the pool.
/// </summary>
public abstract class InfestedAutomatonMirror : TeyvatEventMirror
{
    /// <summary>The base event's own: none.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars => Array.Empty<DynamicVar>();

    /// <summary>Two options, in the base event's order, under its names.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Study, InitialOptionKey("STUDY")),
            new EventOption(this, TouchCore, InitialOptionKey("TOUCH_CORE")),
        };

    /// <summary>`Study`: one Power out of the character's pool, into the
    /// deck.</summary>
    private async Task Study()
    {
        CardCreationOptions options = CardCreationOptions.ForNonCombatWithDefaultOdds(
            new List<CardPoolModel> { Owner.Character.CardPool },
            (CardModel c) => c.Type == CardType.Power);
        CardModel card = CardFactory.CreateForReward(Owner, 1, options).FirstOrDefault()?.Card;
        if (card != null)
        {
            CardCmd.PreviewCardPileAdd(
                await CardPileCmd.Add(card, PileType.Deck), 1.2f, CardPreviewStyle.EventLayout);
        }

        SetEventFinished(L10NLookup(PageKey("STUDY.description")));
    }

    /// <summary>`TouchCore`: one canonical-zero-cost, non-X card out of the
    /// same pool, with the base event's `NoCardPoolModifications` flag.</summary>
    private async Task TouchCore()
    {
        CardCreationOptions options = CardCreationOptions.ForNonCombatWithDefaultOdds(
            new List<CardPoolModel> { Owner.Character.CardPool },
            delegate(CardModel c)
            {
                CardEnergyCost energyCost = c.EnergyCost;
                return energyCost != null && energyCost.Canonical == 0 && !energyCost.CostsX;
            }).WithFlags(CardCreationFlags.NoCardPoolModifications);
        CardModel card = CardFactory.CreateForReward(Owner, 1, options).FirstOrDefault()?.Card;
        if (card != null)
        {
            CardCmd.PreviewCardPileAdd(
                await CardPileCmd.Add(card, PileType.Deck), 1.2f, CardPreviewStyle.EventLayout);
        }

        SetEventFinished(L10NLookup(PageKey("TOUCH_CORE.description")));
    }
}
