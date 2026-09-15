using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// TRASH HEAP, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/TrashHeap.cs` and cross-checked against
/// the harvest (2 options: Dive In, Grab).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `HpLossVar(8)` and
/// `GoldVar(100)`, the same above-5-HP gate, the same damage annotation on
/// the first option, and the same two FIXED tables -- five relics and ten
/// cards, each drawn from with `Rng.NextItem`, which is a uniform pick, which
/// is what the face's "equal probability" means.
///
/// THE TABLES ARE THE BASE EVENT'S, ITEM FOR ITEM AND IN ITS ORDER. The order
/// matters because `NextItem` indexes: a table written in a different order
/// would hand a different relic on the same seed. The face lists the cards in
/// the wiki's order (Caltrops, Distraction, Outmaneuver, Clash, ...) and the
/// base event declares them alphabetically; the C# keeps the C#'s.
///
/// EVERY ENTRY IS A BASE-GAME MODEL with base-game loc rows. A dressing
/// renames none of them, exactly as it renames neither the Chosen Cheese nor
/// the Sword of Stone.
/// </summary>
public abstract class TrashHeapMirror : TeyvatEventMirror
{
    /// <summary>The base event's five relics, in its order.</summary>
    private static RelicModel[] Relics => new RelicModel[5]
    {
        ModelDb.Relic<DarkstonePeriapt>(),
        ModelDb.Relic<DreamCatcher>(),
        ModelDb.Relic<HandDrill>(),
        ModelDb.Relic<MawBank>(),
        ModelDb.Relic<TheBoot>(),
    };

    /// <summary>The base event's ten cards, in its order.</summary>
    private static CardModel[] Cards => new CardModel[10]
    {
        ModelDb.Card<Caltrops>(),
        ModelDb.Card<Clash>(),
        ModelDb.Card<Distraction>(),
        ModelDb.Card<DualWield>(),
        ModelDb.Card<Entrench>(),
        ModelDb.Card<HelloWorld>(),
        ModelDb.Card<Outmaneuver>(),
        ModelDb.Card<Rebound>(),
        ModelDb.Card<RipAndTear>(),
        ModelDb.Card<Stack>(),
    };

    /// <summary>`TrashHeap.cs:41-45`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new HpLossVar(8m),
            new GoldVar(100),
        };

    /// <summary>The base event's gate: every player above 5 HP, so the Dive
    /// In branch is never the only thing on offer to someone it would
    /// kill.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player player) => player.Creature.CurrentHp > 5);

    /// <summary>Two options, in the base event's order, under its names, with
    /// the damage annotation on the first.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, DiveIn, InitialOptionKey("DIVE_IN"))
                .ThatDoesDamage(DynamicVars.HpLoss.IntValue),
            new EventOption(this, Grab, InitialOptionKey("GRAB")),
        };

    /// <summary>`DiveIn`: the damage, then one of the five relics.</summary>
    private async Task DiveIn()
    {
        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature, DynamicVars.HpLoss.IntValue,
            ValueProp.Unblockable | ValueProp.Unpowered, null, null, null);
        RelicModel relic = Rng.NextItem(Relics);
        await RelicCmd.Obtain(relic.ToMutable(), Owner);
        SetEventFinished(L10NLookup(PageKey("DIVE_IN.description")));
    }

    /// <summary>`Grab`: the gold, then one of the ten cards previewed into
    /// the deck at the base event's own two seconds.</summary>
    private async Task Grab()
    {
        await PlayerCmd.GainGold(DynamicVars.Gold.BaseValue, Owner);
        CardModel card = Owner.RunState.CreateCard(Rng.NextItem(Cards), Owner);
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck), 2f);
        SetEventFinished(L10NLookup(PageKey("GRAB.description")));
    }
}
