using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Audio.Debug;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Vfx.Utilities;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// AMALGAMATOR, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/Amalgamator.cs` and cross-checked against
/// the harvest (2 options: Combine Strikes, Combine Defends).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same two `StringVar`s naming
/// Ultimate Strike and Ultimate Defend, the same gate -- every player holding
/// two valid Strikes AND two valid Defends -- the two cards' hover tips on
/// their own options, the same filtered two-card removal grid, the same
/// TWO forge beats (sound, shake, a 300 ms delay, sound, shake) and the same
/// two-second preview of the card that comes out.
///
/// `IsValid` IS THREE TESTS, NOT ONE. A card counts only if it carries the
/// tag, is `Basic` rarity AND is removable -- so an upgraded Strike still
/// counts (rarity and tag survive an upgrade) while a Strike some relic has
/// made unremovable does not. Restating that as "a basic Strike" would change
/// which decks the event is offered in, since the same predicate is the gate.
///
/// THE DELAY IS `Task.Delay(300)`, NOT `Cmd.Wait`. It is real time and is not
/// scaled by the game's speed setting -- the base event's choice, kept,
/// because the two forge beats are meant to land a fixed distance apart.
///
/// THE OPTION KEYS ARE ALREADY DERIVED IN THE BASE EVENT. Amalgamator is one
/// of the few base events that calls `InitialOptionKey` rather than writing
/// its literals out, so the index's scrape reports NO option keys for it and
/// the mirror's spec declares them -- exactly as Hungry for Mushrooms'
/// relic-keyed pair are declared, though these two ARE spelled here and so the
/// key-literal pin can still see them.
/// </summary>
public abstract class AmalgamatorMirror : TeyvatEventMirror
{
    /// <summary>`Amalgamator.cs:20-24`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new StringVar("Card1", ModelDb.Card<UltimateStrike>().Title),
            new StringVar("Card2", ModelDb.Card<UltimateDefend>().Title),
        };

    /// <summary>The base event's gate: two valid Strikes and two valid
    /// Defends, on every player.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) =>
            p.Deck.Cards.Count((CardModel c) => IsValid(CardTag.Strike, c)) >= 2
         && p.Deck.Cards.Count((CardModel c) => IsValid(CardTag.Defend, c)) >= 2);

    /// <summary>Two options, in the base event's order, each carrying its own
    /// card's hover tip.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, CombineStrikes, InitialOptionKey("COMBINE_STRIKES"),
                HoverTipFactory.FromCardWithCardHoverTips<UltimateStrike>()),
            new EventOption(this, CombineDefends, InitialOptionKey("COMBINE_DEFENDS"),
                HoverTipFactory.FromCardWithCardHoverTips<UltimateDefend>()),
        };

    /// <summary>`CombineStrikes`: two valid Strikes out, two forge beats, one
    /// Ultimate Strike in.</summary>
    private async Task CombineStrikes()
    {
        List<CardModel> cards = (await CardSelectCmd.FromDeckForRemoval(
            player: Owner,
            prefs: new CardSelectorPrefs(CardSelectorPrefs.RemoveSelectionPrompt, 2),
            filter: (CardModel c) => IsValid(CardTag.Strike, c))).ToList();
        await CardPileCmd.RemoveFromDeck(cards);
        await Forge();
        CardModel card = Owner.RunState.CreateCard<UltimateStrike>(Owner);
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck), 2f);
        SetEventFinished(L10NLookup(PageKey("COMBINE_STRIKES.description")));
    }

    /// <summary>`CombineDefends`: the same, with Defends.</summary>
    private async Task CombineDefends()
    {
        List<CardModel> cards = (await CardSelectCmd.FromDeckForRemoval(
            player: Owner,
            prefs: new CardSelectorPrefs(CardSelectorPrefs.RemoveSelectionPrompt, 2),
            filter: (CardModel c) => IsValid(CardTag.Defend, c))).ToList();
        await CardPileCmd.RemoveFromDeck(cards);
        await Forge();
        CardModel card = Owner.RunState.CreateCard<UltimateDefend>(Owner);
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck), 2f);
        SetEventFinished(L10NLookup(PageKey("COMBINE_DEFENDS.description")));
    }

    /// <summary>
    /// The base event's two forge beats, value for value. Written once here
    /// where the base event writes them twice -- the ONE place this mirror
    /// differs in shape from its base, and it differs in shape only: the call
    /// sequence either option reaches is identical, which is what
    /// `A_mirror_reaches_the_same_commands_as_its_base` compares.
    /// </summary>
    private static async Task Forge()
    {
        NDebugAudioManager.Instance?.Play("card_smith.mp3", 1f, PitchVariance.Small);
        NGame.Instance.ScreenShakeTrauma(ShakeStrength.Strong);
        await Task.Delay(300);
        NDebugAudioManager.Instance?.Play("card_smith.mp3", 1f, PitchVariance.Small);
        NGame.Instance.ScreenShakeTrauma(ShakeStrength.Strong);
    }

    /// <summary>The base event's own predicate: the tag, `Basic` rarity, and
    /// removable -- all three.</summary>
    private static bool IsValid(CardTag tag, CardModel card)
    {
        if (card.Tags.Contains(tag))
        {
            if (card != null && card.Rarity == CardRarity.Basic)
            {
                return card.IsRemovable;
            }

            return false;
        }

        return false;
    }
}
