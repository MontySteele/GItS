using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// WAR HISTORIAN, REPY, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/WarHistorianRepy.cs` and cross-checked
/// against the harvest (2 options: Unlock Cage, Unlock Chest).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `IsShared`, the same
/// `IsAllowed => false`, the same Lantern Key removals, the same
/// cage-gives-History-Course-and-sets-`FreedRepy` and
/// chest-gives-two-potions-and-two-relics, and the same second page offering
/// the OTHER door when the player still holds a Lantern Key in a solo run.
///
/// `IsAllowed` RETURNS FALSE, AND THAT IS THE BASE EVENT'S. This event is
/// never rolled into the pool: it is reached by holding the Lantern Key, which
/// is what The Lantern Key's own Keep-the-Key branch hands out. The mirror
/// carries the same `false`, so the dressed event is reachable exactly where
/// the base one is and nowhere else -- a mirror that "fixed" the gate would put
/// it in the act's event rotation, which is a behaviour change and not a
/// dressing. Both Glory faces flag the Lantern Key pairing on this event for
/// the same reason.
///
/// THE SECOND PAGE REUSES THE **INITIAL** OPTION KEYS. `SecondUnlockChest` is
/// offered under `pages.INITIAL.options.UNLOCK_CHEST`, not under a key of the
/// second page's own -- so there are no extra option rows to write and the
/// player sees the same words the first page showed. The base event's choice,
/// kept, and the reason this mirror needs no `extra_options` at all.
///
/// THE ORDER IN THE **SECOND** HANDLERS IS INVERTED ON PURPOSE.
/// `SecondUnlockCage` calls `SetEventFinished` BEFORE it removes the keys and
/// grants the relic, where the first-choice handlers finish last. That is the
/// base event's code and it is kept: the page has to be set before an await
/// that can pop a reward screen over it.
///
/// `ExtraFields.FreedRepy` IS A RUN FLAG THE BASE GAME OWNS, and other content
/// reads it. A dressing writes the same flag.
/// </summary>
public abstract class WarHistorianRepyMirror : TeyvatEventMirror
{
    /// <summary>The base event's own.</summary>
    public override bool IsShared => true;

    /// <summary>The base event's own: a second door only in a solo run, and
    /// only while a Lantern Key is still in the deck.</summary>
    private bool ShouldGetSecondReward
    {
        get
        {
            if (Owner.Deck.Cards.Any((CardModel c) => c is LanternKey))
            {
                return Owner.RunState.Players.Count <= 1;
            }

            return false;
        }
    }

    /// <summary>The base event's own: never rolled into the pool -- see the
    /// class comment.</summary>
    public override bool IsAllowed(IRunState runState) => false;

    /// <summary>Two options, in the base event's order, with History Course's
    /// relic tip concatenated onto the Lantern Key's card tip on the
    /// first.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, InitialUnlockCage, InitialOptionKey("UNLOCK_CAGE"),
                HoverTipFactory.FromRelic<HistoryCourse>()
                    .Concat(HoverTipFactory.FromCardWithCardHoverTips<LanternKey>())),
            new EventOption(this, InitialUnlockChest, InitialOptionKey("UNLOCK_CHEST"),
                HoverTipFactory.FromCardWithCardHoverTips<LanternKey>()),
        };

    private async Task InitialUnlockCage()
    {
        await RemoveLanternKeysForInitialChoice();
        await UnlockCage();
        if (ShouldGetSecondReward)
        {
            SetEventState(L10NLookup(PageKey("UNLOCK_CAGE.description")), new List<EventOption>
            {
                new EventOption(this, SecondUnlockChest, InitialOptionKey("UNLOCK_CHEST"),
                    HoverTipFactory.FromCardWithCardHoverTips<LanternKey>()),
            });
        }
        else
        {
            SetEventFinished(L10NLookup(PageKey("UNLOCK_CAGE.description")));
        }
    }

    private async Task InitialUnlockChest()
    {
        await RemoveLanternKeysForInitialChoice();
        await UnlockChest();
        if (ShouldGetSecondReward)
        {
            SetEventState(L10NLookup(PageKey("UNLOCK_CHEST.description")), new List<EventOption>
            {
                new EventOption(this, SecondUnlockCage, InitialOptionKey("UNLOCK_CAGE"),
                    HoverTipFactory.FromRelic<HistoryCourse>()
                        .Concat(HoverTipFactory.FromCardWithCardHoverTips<LanternKey>())),
            });
        }
        else
        {
            SetEventFinished(L10NLookup(PageKey("UNLOCK_CHEST.description")));
        }
    }

    /// <summary>The page FIRST, then the work -- the base event's order on the
    /// second choice, and the opposite of the first.</summary>
    private async Task SecondUnlockCage()
    {
        SetEventFinished(L10NLookup(PageKey("EXTRA_UNLOCK_CAGE.description")));
        await RemoveLanternKeysForSecondChoice();
        await UnlockCage();
    }

    private async Task SecondUnlockChest()
    {
        SetEventFinished(L10NLookup(PageKey("EXTRA_UNLOCK_CHEST.description")));
        await RemoveLanternKeysForSecondChoice();
        await UnlockChest();
    }

    /// <summary>Two potions and two relics, as one offer.</summary>
    private async Task UnlockChest()
    {
        List<Reward> rewards = new List<Reward>
        {
            new PotionReward(Owner),
            new PotionReward(Owner),
            new RelicReward(Owner),
            new RelicReward(Owner),
        };
        await RewardsCmd.OfferCustom(Owner, rewards);
    }

    /// <summary>The run flag the base game owns, then the relic.</summary>
    private async Task UnlockCage()
    {
        Owner.RunState.ExtraFields.FreedRepy = true;
        await RelicCmd.Obtain<HistoryCourse>(Owner);
    }

    /// <summary>In multiplayer the first choice already spends EVERY key,
    /// because there is no second door to save one for.</summary>
    private async Task RemoveLanternKeysForInitialChoice()
    {
        if (Owner.RunState.Players.Count > 1)
        {
            await RemoveLanternKeysForSecondChoice();
        }
        else
        {
            await RemoveFirstLanternKey();
        }
    }

    private async Task RemoveFirstLanternKey()
    {
        CardModel key = Owner.Deck.Cards.FirstOrDefault((CardModel c) => c is LanternKey);
        if (key != null)
        {
            PlayerCmd.CompleteQuest(key);
            await CardPileCmd.RemoveFromDeck(key);
        }
    }

    private async Task RemoveLanternKeysForSecondChoice()
    {
        List<CardModel> keys = Owner.Deck.Cards.Where((CardModel c) => c is LanternKey).ToList();
        foreach (CardModel key in keys)
        {
            PlayerCmd.CompleteQuest(key);
            await CardPileCmd.RemoveFromDeck(key);
        }
    }
}
