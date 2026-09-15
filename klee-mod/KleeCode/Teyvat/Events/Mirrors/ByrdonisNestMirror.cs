using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// BYRDONIS NEST, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/ByrdonisNest.cs` and cross-checked
/// against the harvest (2 options: Eat, Take).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `MaxHpVar(7)`, the same
/// `StringVar("Card", ...)` naming the egg, the same no-pet gate, and the
/// same two branches -- max HP on the first, the egg card previewed into the
/// deck at the base event's own 2-second preview on the second.
///
/// THE EGG IS THE BASE GAME'S CARD. `ByrdonisEgg` is a quest card with global
/// loc rows, exactly like the Chosen Cheese in the cheese cellar: the C#
/// grants the real card and the dressing renames nothing. The Mondstadt face
/// says so at its own heading, and flags besides that `tier05` ships the
/// Eat branch only because the sim does not model an event pet -- a SIM gap,
/// not a C# one, and this mirror is the C# side entire.
/// </summary>
public abstract class ByrdonisNestMirror : TeyvatEventMirror
{
    /// <summary>`ByrdonisNest.cs:21-25`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new MaxHpVar(7m),
            new StringVar("Card", ModelDb.Card<ByrdonisEgg>().Title),
        };

    /// <summary>Two options, in the base event's order, under its names, with
    /// the egg's card hover tip on the second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Eat, InitialOptionKey("EAT")),
            new EventOption(this, Take, InitialOptionKey("TAKE"),
                HoverTipFactory.FromCardWithCardHoverTips<ByrdonisEgg>()),
        };

    /// <summary>
    /// The base event's gate: no player may already hold an event pet. One
    /// egg per run is the rule, and it is asked of the SUBSTITUTE too so the
    /// dressing cannot offer a room the base game would have skipped.
    /// </summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) => !p.HasEventPet());

    /// <summary>`Eat`: the max HP, and nothing else.</summary>
    private async Task Eat()
    {
        await CreatureCmd.GainMaxHp(Owner.Creature, DynamicVars.MaxHp.BaseValue);
        SetEventFinished(L10NLookup(PageKey("EAT.description")));
    }

    /// <summary>`Take`: the egg into the deck, previewed for the base event's
    /// own two seconds.</summary>
    private async Task Take()
    {
        CardModel card = Owner.RunState.CreateCard<ByrdonisEgg>(Owner);
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck), 2f);
        SetEventFinished(L10NLookup(PageKey("TAKE.description")));
    }
}
