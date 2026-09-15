using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.PotionPools;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// THE LEGENDS WERE TRUE, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/TheLegendsWereTrue.cs` and cross-checked
/// against the harvest (2 options: Nab the Map, Slowly Find an Exit).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `DamageVar(8m, Unblockable |
/// Unpowered)`, the same three-clause `IsAllowed` (act 1, every player holding
/// a card, every player at 10+ HP), the same `SpoilsMap` into the deck behind
/// the same `CustomScaledWait(0.5f, 1.2f)`, and the same damage-then-potion
/// branch drawn off `PlayerRng.Rewards` over the character pool concatenated
/// with `SharedPotionPool`. Only the loc keys are derived instead of written
/// out, and only the option NAMES are the base game's -- what the player reads
/// is the dressing's `.title` row.
///
/// THE `IsAllowed` GATE IS ASKED OF THE SUBSTITUTE TOO. `RoomSet.
/// EnsureNextEventIsValid` consults the event at the head of the pre-shuffled
/// list -- the BASE one -- and `PullNextEvent`'s postfix swaps afterwards, so
/// the two gates must agree or a dressing would offer an event the base game
/// would have skipped. Identical is how they agree.
/// </summary>
public abstract class TheLegendsWereTrueMirror : TeyvatEventMirror
{
    /// <summary>`TheLegendsWereTrue.cs:21`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new DamageVar(8m, ValueProp.Unblockable | ValueProp.Unpowered) };

    /// <summary>
    /// The base event's gate, all three clauses in its order
    /// (`TheLegendsWereTrue.cs:23-30`): act 1 only, every player holding at
    /// least one card, and every player at 10 HP or more -- the last because
    /// the second option costs 8 unblockable and the base game declines to
    /// offer a room that can only kill.
    /// </summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.CurrentActIndex == 0
        && runState.Players.All((Player p) => p.Deck.Cards.Count > 0)
        && runState.Players.All((Player p) => p.Creature.CurrentHp >= 10);

    /// <summary>
    /// Two options, in the base event's order, under its names, with its
    /// `SpoilsMap` hover tip on the first and its damage annotation on the
    /// second.
    /// </summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, NabTheMap, InitialOptionKey("NAB_THE_MAP"),
                HoverTipFactory.FromCardWithCardHoverTips<SpoilsMap>()),
            new EventOption(this, SlowlyFindAnExit, InitialOptionKey("SLOWLY_FIND_AN_EXIT"))
                .ThatDoesDamage(DynamicVars.Damage.BaseValue),
        };

    /// <summary>
    /// `NabTheMap`. The card is created through `RunState.CreateCard` and
    /// previewed through `CardCmd.PreviewCardPileAdd`, which is what puts it
    /// on screen; the wait is the base event's own and is what the preview
    /// animation is given time by.
    /// </summary>
    private async Task NabTheMap()
    {
        CardModel card = Owner.RunState.CreateCard<SpoilsMap>(Owner);
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck));
        await Cmd.CustomScaledWait(0.5f, 1.2f);
        SetEventFinished(L10NLookup(PageKey("NAB_THE_MAP.description")));
    }

    /// <summary>
    /// `SlowlyFindAnExit`. Damage first, then ONE potion drawn off
    /// `PlayerRng.Rewards` from the character's unlocked pool concatenated
    /// with the shared one, offered as a custom reward. The null guard is the
    /// base event's: `NextItem` over an empty sequence answers null, and a
    /// character with nothing unlocked would otherwise throw after the damage
    /// had already landed.
    /// </summary>
    private async Task SlowlyFindAnExit()
    {
        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature, DynamicVars.Damage, null, null, null);

        IEnumerable<PotionModel> items = Owner.Character.PotionPool
            .GetUnlockedPotions(Owner.UnlockState)
            .Concat(ModelDb.PotionPool<SharedPotionPool>().GetUnlockedPotions(Owner.UnlockState));

        PotionModel potion = Owner.PlayerRng.Rewards.NextItem(items);
        if (potion != null)
        {
            await RewardsCmd.OfferCustom(Owner, new List<Reward>(1)
            {
                new PotionReward(potion.ToMutable(), Owner),
            });
        }

        SetEventFinished(L10NLookup(PageKey("SLOWLY_FIND_AN_EXIT.description")));
    }
}
