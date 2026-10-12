using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Hooks;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Story;

/// <summary>
/// A STORY EVENT: one page and its options, read from a character's table.
///
/// THE SUBCLASS IS ONE LINE (<see cref="Data"/>). The game's ModelDb registers
/// events by type, so each event needs a class; everything it shows and does
/// is the table's (<see cref="StoryEvent"/>, <see cref="StoryEffectKind"/>).
///
/// IN NO ACT'S POOL. It reaches the map by substitution at pull time
/// (<see cref="Hook_ModifyNextEvent_Story_Patch"/>), the game's own seam for
/// exactly this (Lantern Key's), which consumes no rng and so leaves every
/// later roll of the run where it was.
///
/// ONLY ITS OWNER PLAYS IT. In co-op every player in an event room gets a
/// copy of the same event; a copy whose owner is not this event's character
/// shows the page and finishes at once (Proceed), so no one else takes her
/// cards or her curse.
/// </summary>
public abstract class StoryEventModel : EventModel
{
    /// <summary>This event's row in its character's table.</summary>
    protected abstract StoryEvent Data { get; }

    internal StoryEvent StoryData => Data;

    /// <summary>The table this event belongs to.</summary>
    internal CharacterStory Story =>
        StoryRegistry.All.First(s => s.Events.Contains(Data));

    internal const string Table = "events";

    /// <summary>The <c>events</c> rows for one event, keyed off the entry the
    /// game files it under (<see cref="StoryRegistry.EntryOf"/>).</summary>
    public static Dictionary<string, string> Rows(StoryEvent e, string entry)
    {
        var rows = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            [entry + ".title"] = e.Title,
            [entry + ".pages.INITIAL.description"] = e.Body,
        };
        foreach (var o in e.Options)
        {
            rows[OptionTitleKey(entry, o)] = o.Title;
            rows[OptionDescriptionKey(entry, o)] = o.Description;
            rows[ResultKey(entry, o)] = o.Result ?? e.Body;
        }
        return rows;
    }

    public static string OptionTitleKey(string entry, StoryOption o) =>
        $"{entry}.pages.INITIAL.options.{o.Key}.title";

    public static string OptionDescriptionKey(string entry, StoryOption o) =>
        $"{entry}.pages.INITIAL.options.{o.Key}.description";

    /// <summary>The page an option leaves up: its result, or the event's own
    /// page where the paper gives none.</summary>
    public static string ResultKey(string entry, StoryOption o) =>
        $"{entry}.pages.{o.Key}.description";

    protected override void SetInitialEventState(bool isPreFinished)
    {
        if (!StoryRules.IsOwnersEvent(Owner?.Character?.GetType(), GetType()))
        {
            SetEventFinished(InitialDescription);
            return;
        }
        base.SetInitialEventState(isPreFinished);
    }

    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        var entry = Id.Entry;
        return Data.Options.Select(o => new EventOption(
                this,
                () => Choose(o),
                new LocString(Table, OptionTitleKey(entry, o)),
                new LocString(Table, OptionDescriptionKey(entry, o)),
                InitialOptionKey(o.Key),
                TipsFor(o.Effect)))
            .ToList();
    }

    private static IEnumerable<IHoverTip> TipsFor(StoryEffect effect)
    {
        if (effect.Card == null) return Array.Empty<IHoverTip>();
        try
        {
            var card = ModelDb.GetById<CardModel>(ModelDb.GetId(effect.Card));
            return new[] { HoverTipFactory.FromCard(card, effect.Kind == StoryEffectKind.AddUpgradedCard) };
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: no hover tip for {effect.Card.Name}: {e.Message}");
            return Array.Empty<IHoverTip>();
        }
    }

    private async Task Choose(StoryOption option)
    {
        await Apply(option.Effect);
        SetEventFinished(L10NLookup(ResultKey(Id.Entry, option)));
    }

    private async Task Apply(StoryEffect effect)
    {
        var owner = Owner!;
        switch (effect.Kind)
        {
            case StoryEffectKind.GainGoldAddCard:
                await PlayerCmd.GainGold(effect.Amount, owner);
                await AddToDeck(owner, effect.Card!, upgraded: false);
                break;
            case StoryEffectKind.AddCard:
                await AddToDeck(owner, effect.Card!, upgraded: false);
                break;
            case StoryEffectKind.AddUpgradedCard:
                await AddToDeck(owner, effect.Card!, upgraded: true);
                break;
            case StoryEffectKind.RemoveCard:
                await RemoveChosen(owner, null);
                break;
            case StoryEffectKind.Heal:
                await CreatureCmd.Heal(owner.Creature, effect.Amount);
                break;
            case StoryEffectKind.RemoveCurseElseGold:
                if (owner.Deck.Cards.Any(IsRemovableCurse))
                {
                    await RemoveChosen(owner, IsRemovableCurse);
                }
                else
                {
                    await PlayerCmd.GainGold(effect.Amount, owner);
                }
                break;
            case StoryEffectKind.UpgradeRandomBombCards:
                var story = Story;
                var candidates = owner.Deck.Cards
                    .Where(c => c.IsUpgradable && StoryRules.PlacesBomb(story, c.Id.Entry))
                    .ToList();
                var picks = StoryRules.PickRandom(candidates, effect.Amount, n => Rng.NextInt(n));
                if (picks.Count > 0) CardCmd.Upgrade(picks, CardPreviewStyle.EventLayout);
                break;
        }
    }

    public static bool IsRemovableCurse(CardModel card) =>
        card.Type == CardType.Curse && card.IsRemovable;

    private static async Task AddToDeck(Player owner, Type cardType, bool upgraded)
    {
        var canonical = ModelDb.GetById<CardModel>(ModelDb.GetId(cardType));
        var card = owner.RunState.CreateCard(canonical, owner);
        if (upgraded) CardCmd.Upgrade(card);
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck), 2f);
    }

    private static async Task RemoveChosen(Player owner, Func<CardModel, bool>? filter)
    {
        var chosen = (await CardSelectCmd.FromDeckForRemoval(
                owner, new CardSelectorPrefs(CardSelectorPrefs.RemoveSelectionPrompt, 1), filter))
            .ToList();
        if (chosen.Count > 0) await CardPileCmd.RemoveFromDeck(chosen);
    }
}

/// <summary>
/// THE STORY EVENT REACHES THE MAP HERE: the game's own substitution seam,
/// <c>Hook.ModifyNextEvent</c>, called by <c>ActModel.PullNextEvent</c> once
/// per event room and BEFORE the pulled event is recorded as visited -- so
/// the run's visited list holds the story event and it is offered once.
///
/// A GAME SUBSTITUTION WINS. If something in the run already swapped the
/// event (Lantern Key's act-3 quest), the story event waits for the act's
/// next event room.
/// </summary>
[HarmonyPatch(typeof(Hook), nameof(Hook.ModifyNextEvent))]
internal static class Hook_ModifyNextEvent_Story_Patch
{
    [HarmonyPostfix]
    private static void Postfix(IRunState runState, EventModel currentEvent, ref EventModel __result)
    {
        try
        {
            if (runState is not RunState run || !ReferenceEquals(__result, currentEvent)) return;
            var story = StoryRules.EventFor(
                run.Players.Select(p => p.Character.GetType()),
                run.CurrentActIndex,
                t => run.VisitedEventIds.Contains(ModelDb.GetId(t)));
            if (story == null) return;
            __result = ModelDb.GetById<EventModel>(ModelDb.GetId(story.EventType));
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] story: event substitution failed, the drawn event stands: {e}");
        }
    }
}

/// <summary>
/// THE PICTURE. An event's portrait path is derived from its id
/// (<c>res://images/events/&lt;entry&gt;.png</c>) and is preloaded on room
/// entry, where a missing file is a cached load failure. So the PATH falls
/// back to a base event's picture, which always loads, and the DRAWN portrait
/// is the table's official Klee art when it is on disk (the card-art folder
/// the deploy stages next to the dll).
/// </summary>
[HarmonyPatch(typeof(EventModel), "get_InitialPortraitPath")]
internal static class EventModel_InitialPortraitPath_Story_Patch
{
    [HarmonyPostfix]
    private static void Postfix(EventModel __instance, ref string __result)
    {
        if (__instance is not StoryEventModel story) return;
        if (!ResourceLoader.Exists(__result)) __result = story.StoryData.FallbackPortraitPath;
    }
}

[HarmonyPatch(typeof(EventModel), nameof(EventModel.CreateInitialPortrait))]
internal static class EventModel_CreateInitialPortrait_Story_Patch
{
    [HarmonyPostfix]
    private static void Postfix(EventModel __instance, ref Texture2D __result)
    {
        if (__instance is not StoryEventModel story) return;
        try
        {
            var art = story.StoryData.Portrait();
            if (art != null && RosterArt.LastResolved) __result = art;
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: event art fell back to the base picture: {e.Message}");
        }
    }
}
