using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.PotionPools;
using MegaCrit.Sts2.Core.Rewards;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// WELLSPRING, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/Wellspring.cs` and cross-checked against
/// the harvest (2 options: Bottle, Bathe).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `BatheCurses` var at 1, no
/// act gate, the same Guilty card hover tip on the second option, the same
/// one-potion draw off `PlayerRng.Rewards` over the character's unlocked pool
/// concatenated with the shared one, and the same remove-one-then-add-Guilty
/// on the other branch.
///
/// THE POTION COMES OFF `PlayerRng.Rewards` AND NOT THE EVENT'S OWN `Rng`,
/// which is the same seam The Legends Were True's second option uses and is
/// the reason a dressed entry's different hash does not move it: the draw is
/// on the PLAYER's reward stream, not on the per-event stream seeded from
/// `Id.Entry`. The null guard is the base event's: `NextItem` over an empty
/// sequence answers null.
///
/// THE CURSE COUNT IS A VAR AND IS READ AS ONE. `AddGuilty` repeats the model
/// `BatheCurses` times, so the printed number and the number added cannot
/// drift.
/// </summary>
public abstract class WellspringMirror : TeyvatEventMirror
{
    /// <summary>`Wellspring.cs:18`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new DynamicVar("BatheCurses", 1m) };

    /// <summary>Two options, in the base event's order, under its names, with
    /// Guilty's card hover tip on the second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Bottle, InitialOptionKey("BOTTLE")),
            new EventOption(this, Bathe, InitialOptionKey("BATHE"),
                HoverTipFactory.FromCardWithCardHoverTips<Guilty>()),
        };

    /// <summary>`Bottle`: one potion, offered as a custom reward.</summary>
    private async Task Bottle()
    {
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

        SetEventFinished(L10NLookup(PageKey("BOTTLE.description")));
    }

    /// <summary>`Bathe`: one card out, then `BatheCurses` Guilty in.</summary>
    private async Task Bathe()
    {
        List<CardModel> cards = (await CardSelectCmd.FromDeckForRemoval(
            player: Owner, prefs: new CardSelectorPrefs(CardSelectorPrefs.RemoveSelectionPrompt, 1)))
            .ToList();
        await CardPileCmd.RemoveFromDeck(cards);
        await AddGuilty(DynamicVars["BatheCurses"].IntValue);
        SetEventFinished(L10NLookup(PageKey("BATHE.description")));
    }

    /// <summary>The base event's own helper, kept separate for the same
    /// reason it is separate there: the count is a var.</summary>
    private async Task AddGuilty(int amount)
    {
        await CardPileCmd.AddCursesToDeck(Enumerable.Repeat(ModelDb.Card<Guilty>(), amount), Owner);
    }
}
