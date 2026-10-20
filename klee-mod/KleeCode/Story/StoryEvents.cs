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
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Hooks;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.PotionPools;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Runs.History;
using MegaCrit.Sts2.Core.ValueProps;
using KleeMod.Diagnostics;

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
/// cards or her curse. Since the co-op story rooms (ruled 2026-10-16) a
/// co-op table never draws a character's event type: it draws
/// <see cref="StoryCoopRoomEvent"/>, whose copy for each player is that
/// player's own event. The Proceed path stays for a room saved before.
/// </summary>
public abstract class StoryEventModel : EventModel
{
    /// <summary>This event's row in its character's table, found by type.</summary>
    protected virtual StoryEvent Data =>
        StoryRegistry.All.SelectMany(s => s.Events).First(e => e.EventType == GetType());

    internal StoryEvent StoryData => Data;

    /// <summary>The table this event belongs to (null: the co-op room's
    /// placeholder, which belongs to none).</summary>
    internal virtual CharacterStory? Story =>
        StoryRegistry.All.FirstOrDefault(s => s.Events.Contains(Data));

    /// <summary>The entry this page's loc rows are filed under: the event's
    /// own, or (the co-op room) the routed event's.</summary>
    protected virtual string LocEntry => Id.Entry;

    /// <summary>The base picture under the drawn art. One path for the
    /// canonical model and every copy: the room preloads the canonical's.</summary>
    internal virtual string FallbackPortraitPath => Data.FallbackPortraitPath;

    /// <summary>The title row, when it is not the model's own (the co-op
    /// room's copy showing a player's routed event); null otherwise.</summary>
    internal string? TitleKeyOverride =>
        LocEntry == Id.Entry ? null : LocEntry + ".title";

    internal const string Table = "events";

    /// <summary>The owner's saved story, read as the event begins.</summary>
    private IReadOnlyList<StoryRecord> _records = Array.Empty<StoryRecord>();

    /// <summary>The line this page opens with for its owner, or null.</summary>
    private StoryOpening? _opening;

    /// <summary>The <c>events</c> rows for one event, keyed off the entry the
    /// game files it under (<see cref="StoryRegistry.EntryOf"/>).</summary>
    public static Dictionary<string, string> Rows(StoryEvent e, string entry)
    {
        var rows = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            [entry + ".title"] = e.Title,
            [entry + ".pages.INITIAL.description"] = e.Body,
        };
        foreach (var o in e.Openings)
        {
            rows[OpeningKey(entry, o)] = OpeningPage(e, o);
        }
        foreach (var o in e.Options)
        {
            rows[OptionTitleKey(entry, o)] = o.Title;
            rows[OptionDescriptionKey(entry, o)] = o.Description;
            rows[ResultKey(entry, o)] = o.Result ?? e.Body;
        }
        return rows;
    }

    /// <summary>The page with its opening line: the line, then the body.</summary>
    public static string OpeningPage(StoryEvent e, StoryOpening o) => o.Line + "\n\n" + e.Body;

    public static string OpeningKey(string entry, StoryOpening o) =>
        $"{entry}.pages.INITIAL_{o.Key}.description";

    public static string OptionTitleKey(string entry, StoryOption o) =>
        $"{entry}.pages.INITIAL.options.{o.Key}.title";

    public static string OptionDescriptionKey(string entry, StoryOption o) =>
        $"{entry}.pages.INITIAL.options.{o.Key}.description";

    /// <summary>The page an option leaves up: its result, or the event's own
    /// page where the paper gives none.</summary>
    public static string ResultKey(string entry, StoryOption o) =>
        $"{entry}.pages.{o.Key}.description";

    protected virtual bool IsOwners => StoryRules.IsOwnersEvent(Owner?.Character?.GetType(), GetType());

    /// <summary>Decide what this copy shows, before the page is read (the
    /// co-op room picks its owner's event). Nothing for a character's own
    /// event type.</summary>
    protected virtual void ResolveFor(Player owner)
    {
    }

    /// <summary>The page opens with the line that matches what the owner did
    /// earlier in the run.</summary>
    public override LocString InitialDescription =>
        _opening != null
            ? new LocString(Table, OpeningKey(LocEntry, _opening))
            : LocEntry == Id.Entry
                ? base.InitialDescription
                : new LocString(Table, LocEntry + ".pages.INITIAL.description");

    /// <summary>
    /// Read the owner's saved story, choose the opening line, and take what
    /// the opening removes ("Doubt is removed as the event opens"). Only the
    /// owner's copy: everyone else gets the plain page and Proceed.
    /// </summary>
    protected override async Task BeforeEventStarted(bool isPreFinished)
    {
        await base.BeforeEventStarted(isPreFinished);
        if (Owner == null) return;
        try
        {
            ResolveFor(Owner);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] story: could not route the co-op room, the placeholder stands: {e}");
        }
        if (!IsOwners) return;
        try
        {
            _records = StoryHistory.RecordsFor(Owner.RunState, Owner);
            _opening = StoryRules.OpeningFor(Data, _records);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] story: could not read the saved story, the page opens plain: {e}");
            _records = Array.Empty<StoryRecord>();
            _opening = null;
        }
        if (_opening?.RemovesOnOpen is Type removes) await RemoveEvery(Owner, removes);
    }

    protected override void SetInitialEventState(bool isPreFinished)
    {
        if (!IsOwners)
        {
            SetEventFinished(InitialDescription);
            return;
        }
        base.SetInitialEventState(isPreFinished);
    }

    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        var entry = LocEntry;
        var deck = Owner != null ? DeckView(Owner, Story) : null;
        return StoryRules.OptionsFor(Data, _records).Select(o =>
            {
                // A price the owner cannot pay is locked, the base game's way
                // (Luminous Choir): the row is shown with no action, under
                // the option's own line.
                var locked = deck != null && StoryRules.IsLocked(o, deck);
                var option = new EventOption(
                    this,
                    locked ? null : () => Choose(o),
                    new LocString(Table, OptionTitleKey(entry, o)),
                    new LocString(Table, OptionDescriptionKey(entry, o)),
                    InitialOptionKey(locked ? o.Key + "_LOCKED" : o.Key),
                    TipsFor(o));
                // The game's own lethal warnings: an HP cost (Brain Leech's
                // ThatDoesDamage) and a Max HP cost (Vakuu's
                // ThatDecreasesMaxHp). One option carrying both flashes if
                // either would kill.
                var hp = o.HpCost;
                var maxHp = o.MaxHpCost;
                if (hp > 0 && maxHp > 0)
                    return option.ThatWillKillPlayerIf(p =>
                        p.Creature.CurrentHp <= hp || p.Creature.MaxHp <= maxHp);
                if (hp > 0) return option.ThatDoesDamage(hp);
                if (maxHp > 0) return option.ThatDecreasesMaxHp(maxHp);
                return option;
            })
            .ToList();
    }

    /// <summary>What the locks read off the owner.</summary>
    internal static StoryDeckView DeckView(Player owner, CharacterStory? story)
    {
        var cards = owner.Deck.Cards;
        return new StoryDeckView(
            Gold: owner.Gold,
            Removable: cards.Count(c => c.IsRemovable),
            Transformable: cards.Count(c => c.Type != CardType.Quest && c.IsTransformable),
            RemovableCurses: cards.Count(IsRemovableCurse),
            UpgradableBombPlacers: story == null
                ? 0
                : cards.Count(c => c.IsUpgradable && StoryRules.PlacesBomb(story, c.Id.Entry)),
            OfferSize: e => OfferSize(owner, story, e));
    }

    /// <summary>How many cards a card offer has to show (an option with none
    /// is locked). A count that cannot be read is not a lock.</summary>
    private static int OfferSize(Player owner, CharacterStory? story, StoryEffect effect)
    {
        try
        {
            return effect.Kind switch
            {
                StoryEffectKind.ChooseOfferToDeck when effect.Offer != null => OfferPool(owner, effect.Offer).Count,
                StoryEffectKind.ChooseFromPoolToDeck => story?.ChoicePool?.Invoke().Count ?? 0,
                _ => 1,
            };
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: could not count a card offer, it stays open: {e.Message}");
            return 1;
        }
    }

    /// <summary>A hover tip for each card an option adds.</summary>
    private static IEnumerable<IHoverTip> TipsFor(StoryOption option)
    {
        var tips = new List<IHoverTip>();
        foreach (var effect in option.Effects)
        {
            if (effect.Card == null) continue;
            if (effect.Kind is not (StoryEffectKind.AddCard or StoryEffectKind.AddUpgradedCard
                or StoryEffectKind.GainGoldAddCard)) continue;
            try
            {
                var card = ModelDb.GetById<CardModel>(ModelDb.GetId(effect.Card));
                tips.Add(HoverTipFactory.FromCard(card, effect.Kind == StoryEffectKind.AddUpgradedCard));
            }
            catch (Exception e)
            {
                Log.Warn($"[{KleeMod.ModId}] story: no hover tip for {effect.Card.Name}: {e.Message}");
            }
        }
        return tips;
    }

    /// <summary>The choice being taken, for the play telemetry; null when
    /// it could not be read.</summary>
    private StoryChoiceRecord? _choice;

    private async Task Choose(StoryOption option)
    {
        _choice = BeginChoice(option);
        foreach (var effect in option.Effects)
        {
            await Apply(option, effect);
        }
        if (_choice != null) PlayTelemetry.StoryChoice(_choice);
        _choice = null;
        SetEventFinished(L10NLookup(ResultKey(LocEntry, option)));
    }

    /// <summary>
    /// THE STORY CHOICE TELEMETRY (ruled 2026-10-19): the owner's state as
    /// the option is taken, before its effects. A read only; null, and the
    /// option still runs, if anything cannot be read.
    /// </summary>
    private StoryChoiceRecord? BeginChoice(StoryOption option)
    {
        try
        {
            var owner = Owner!;
            var run = owner.RunState;
            var players = run.Players;
            var seat = 0;
            for (var i = 0; i < players.Count; i++)
            {
                if (ReferenceEquals(players[i], owner)) seat = i;
            }
            return new StoryChoiceRecord
            {
                Event = LocEntry,
                Option = option.Key,
                Character = owner.Character.Title.GetFormattedText(),
                CharacterId = owner.Character.Id.Entry,
                Act = run.CurrentActIndex + 1,
                Floor = run.TotalFloor,
                Seats = players.Count,
                SeatIndex = seat,
                HpBefore = (int)owner.Creature.CurrentHp,
                MaxHpBefore = (int)owner.Creature.MaxHp,
                GoldBefore = owner.Gold,
                DeckBefore = owner.Deck.Cards.Count,
                // Inside the room the map history holds it: its own number.
                EventRoom = StoryHistory.EventRoomsThisAct(run),
            };
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: choice telemetry skipped ({e.GetType().Name}: {e.Message})");
            return null;
        }
    }

    private static (string Id, bool Upgraded) CardRow(CardModel card) =>
        (card.Id.ToString(), card.IsUpgraded);

    private async Task Apply(StoryOption option, StoryEffect effect)
    {
        var owner = Owner!;
        switch (effect.Kind)
        {
            case StoryEffectKind.GainGoldAddCard:
                await PlayerCmd.GainGold(effect.Amount, owner);
                NoteAdded(await AddToDeck(owner, effect.Card!, upgraded: false));
                break;
            case StoryEffectKind.AddCard:
                NoteAdded(await AddToDeck(owner, effect.Card!, upgraded: false));
                break;
            case StoryEffectKind.AddUpgradedCard:
                NoteAdded(await AddToDeck(owner, effect.Card!, upgraded: true));
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
                UpgradeRandom(owner, effect.Amount, c => story != null && StoryRules.PlacesBomb(story, c.Id.Entry));
                break;
            case StoryEffectKind.UpgradeRandomCards:
                UpgradeRandom(owner, effect.Amount, _ => true);
                break;
            case StoryEffectKind.LoseHpUpgradeRandomCards:
                await LoseHp(owner, effect.HpLoss);
                UpgradeRandom(owner, effect.Amount, _ => true);
                break;
            case StoryEffectKind.ChooseFromPoolToDeck:
                await ChooseFromPool(owner, option, effect,
                    Story?.ChoicePool?.Invoke() ?? Array.Empty<CardModel>());
                break;
            case StoryEffectKind.ChooseOfferToDeck:
                await ChooseFromPool(owner, option, effect, OfferPool(owner, effect.Offer!),
                    effect.Offer!.Upgraded);
                break;
            case StoryEffectKind.LoseMaxHp:
                await CreatureCmd.LoseMaxHp(new ThrowingPlayerChoiceContext(), owner.Creature,
                    effect.Amount, isFromCard: false);
                break;
            case StoryEffectKind.Nothing:
                break;
            case StoryEffectKind.LoseHp:
                await LoseHp(owner, effect.Amount);
                break;
            case StoryEffectKind.GainGold:
                await PlayerCmd.GainGold(effect.Amount, owner);
                break;
            case StoryEffectKind.LoseGold:
                await PlayerCmd.LoseGold(effect.Amount, owner);
                break;
            case StoryEffectKind.GainRandomRelic:
                var relic = RelicFactory.PullNextRelicFromFront(owner).ToMutable();
                _choice?.RelicsGained.Add(relic.Id.ToString());
                await RelicCmd.Obtain(relic, owner);
                break;
            case StoryEffectKind.GainRandomRareRelic:
                var rare = RelicFactory.PullNextRelicFromFront(owner, RelicRarity.Rare).ToMutable();
                _choice?.RelicsGained.Add(rare.Id.ToString());
                await RelicCmd.Obtain(rare, owner);
                break;
            case StoryEffectKind.GainRandomPotions:
                var potions = await OfferRandomPotions(owner, effect.Amount);
                _choice?.PotionsOffered.AddRange(potions);
                break;
            case StoryEffectKind.TransformCards:
                await TransformChosen(owner, effect.Amount);
                break;
            case StoryEffectKind.RemoveEvery:
                await RemoveEvery(owner, effect.Card!);
                break;
            case StoryEffectKind.RemoveEveryCurseLoseGoldEach:
                var curses = owner.Deck.Cards.Where(IsRemovableCurse).ToList();
                if (curses.Count == 0) break;
                await PlayerCmd.LoseGold(effect.Amount * curses.Count, owner);
                await CardPileCmd.RemoveFromDeck(curses);
                break;
            case StoryEffectKind.UpgradeChosenCard:
                var chosen = (await CardSelectCmd.FromDeckForUpgrade(
                        owner, new CardSelectorPrefs(CardSelectorPrefs.UpgradeSelectionPrompt, 1)))
                    .FirstOrDefault();
                if (chosen != null) CardCmd.Upgrade(chosen, CardPreviewStyle.EventLayout);
                break;
        }
    }

    /// <summary>Dense Vegetation's HP cost: unblockable, unpowered.</summary>
    private static async Task LoseHp(Player owner, int amount)
    {
        await CreatureCmd.Damage(new ThrowingPlayerChoiceContext(), owner.Creature,
            amount, ValueProp.Unblockable | ValueProp.Unpowered, null, null);
    }

    /// <summary>"Gain N random potions": N potions from the character's and
    /// the shared pools, offered as rewards (Suspicious Condiment's draw).
    /// The ids of the potions offered, for the telemetry.</summary>
    private static async Task<List<string>> OfferRandomPotions(Player owner, int count)
    {
        var rewards = new List<Reward>();
        var ids = new List<string>();
        for (var i = 0; i < count; i++)
        {
            var pool = owner.Character.PotionPool.GetUnlockedPotions(owner.UnlockState)
                .Concat(ModelDb.PotionPool<SharedPotionPool>().GetUnlockedPotions(owner.UnlockState));
            var potion = owner.PlayerRng.Rewards.NextItem(pool);
            if (potion == null) continue;
            rewards.Add(new PotionReward(potion.ToMutable(), owner));
            ids.Add(potion.Id.ToString());
        }
        if (rewards.Count > 0) await RewardsCmd.OfferCustom(owner, rewards);
        return ids;
    }

    /// <summary>"Transform N cards": the player picks (Morphic Grove); with
    /// fewer than N, the game takes those there are.</summary>
    private async Task TransformChosen(Player owner, int count)
    {
        var chosen = (await CardSelectCmd.FromDeckForTransformation(
                owner, new CardSelectorPrefs(CardSelectorPrefs.TransformSelectionPrompt, count)))
            .ToList();
        foreach (var card in chosen)
        {
            await CardCmd.TransformToRandom(card, Rng, CardPreviewStyle.EventLayout);
        }
    }

    /// <summary>"Remove every X": every copy in the deck; with none, nothing.</summary>
    private static async Task RemoveEvery(Player owner, Type cardType)
    {
        var copies = owner.Deck.Cards.Where(c => c.GetType() == cardType).ToList();
        if (copies.Count > 0) await CardPileCmd.RemoveFromDeck(copies);
    }

    /// <summary>"Upgrade N random cards": up to N distinct upgradable deck
    /// cards that pass <paramref name="filter"/>, drawn on the event's Rng.</summary>
    private void UpgradeRandom(Player owner, int count, Func<CardModel, bool> filter)
    {
        var candidates = owner.Deck.Cards.Where(c => c.IsUpgradable && filter(c)).ToList();
        var picks = StoryRules.PickRandom(candidates, count, n => Rng.NextInt(n));
        if (picks.Count > 0) CardCmd.Upgrade(picks, CardPreviewStyle.EventLayout);
    }

    /// <summary>
    /// "Choose 1 of 3 random Guest Stars to add to your deck": <c>Amount</c>
    /// distinct cards from <paramref name="pool"/> (the table's
    /// <see cref="CharacterStory.ChoicePool"/>, or a card offer,
    /// <see cref="OfferPool"/>) by Knights' Roll Call's draw
    /// (<c>VarkaRules.DrawDistinct</c>'s shape, on the event's Rng, so no
    /// reward rng moves), upgraded when <paramref name="upgraded"/>, picked on
    /// the game's add-to-deck grid (Brain Leech's Share Knowledge). Fewer
    /// than <c>Amount</c>: those there are. The screen's prompt is the
    /// option's own line.
    /// </summary>
    private async Task ChooseFromPool(
        Player owner, StoryOption option, StoryEffect effect, IReadOnlyList<CardModel> pool,
        bool upgraded = false)
    {
        var offered = StoryRules.PickRandom(pool, effect.Amount, n => Rng.NextInt(n))
            .Select(c =>
            {
                var card = owner.RunState.CreateCard(c, owner);
                if (upgraded && card.IsUpgradable) CardCmd.Upgrade(card);
                return new CardCreationResult(card);
            })
            .ToList();
        if (offered.Count == 0) return;
        _choice?.CardsOffered.AddRange(offered.Select(c => CardRow(c.Card)));
        var prefs = new CardSelectorPrefs(
            new LocString(Table, OptionDescriptionKey(LocEntry, option)), 1)
        {
            Cancelable = false,
        };
        await SelectCardsToAddToDeckFromGrid(offered, prefs);
        // The grid adds the picked card to the deck: the offered card that
        // is in it now.
        _choice?.CardsPicked.AddRange(offered
            .Where(c => owner.Deck.Cards.Contains(c.Card))
            .Select(c => CardRow(c.Card)));
    }

    private void NoteAdded(CardModel card) => _choice?.CardsAdded.Add(CardRow(card));

    /// <summary>"Choose 1 of 3 random Uncommon Attacks": the cards of her
    /// offer the <paramref name="offer"/> admits (<see cref="StoryOffer.Admits"/>),
    /// from the set her card rewards roll from
    /// (<c>CardPoolModel.GetUnlockedCards</c>, in its own fixed order) or,
    /// for Companions, the ones she can be offered
    /// (<c>CompanionPool.Eligible</c>, the reward slot's and the shop's
    /// rule).</summary>
    private static IReadOnlyList<CardModel> OfferPool(Player owner, StoryOffer offer)
    {
        IEnumerable<CardModel> source = offer.Companions
            ? CompanionPool.Eligible(owner, offer.Rarity, null)
            : owner.Character.CardPool
                .GetUnlockedCards(owner.UnlockState, owner.RunState.CardMultiplayerConstraint);
        return source.Where(c => offer.Admits(c.Rarity, c.Type)).ToList();
    }

    public static bool IsRemovableCurse(CardModel card) =>
        card.Type == CardType.Curse && card.IsRemovable;

    private static async Task<CardModel> AddToDeck(Player owner, Type cardType, bool upgraded)
    {
        var canonical = ModelDb.GetById<CardModel>(ModelDb.GetId(cardType));
        var card = owner.RunState.CreateCard(canonical, owner);
        if (upgraded) CardCmd.Upgrade(card);
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck), 2f);
        return card;
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
/// THE SAVED STORY IN A LIVE RUN. Nothing new is saved: the game already
/// keeps the visited events and, per player, every event choice in the run
/// history (both in the run's save file), and
/// <see cref="StoryRules.Records"/> reads the story back out of them.
/// </summary>
public static class StoryHistory
{
    public static IReadOnlyList<StoryRecord> RecordsFor(IRunState run, Player player)
    {
        var story = StoryRegistry.For(player.Character);
        if (story == null || run is not RunState state) return Array.Empty<StoryRecord>();
        return StoryRules.Records(
            story, t => state.VisitedEventIds.Contains(ModelDb.GetId(t)),
            ChoiceKeys(run.MapPointHistory, player.NetId), StoryRegistry.EntryOf);
    }

    /// <summary>The act's event rooms in the run's map history
    /// (<see cref="StoryRules.EventRoomsIn"/>). The map history is shared, so
    /// every client at a co-op table counts the same.</summary>
    public static int EventRoomsThisAct(IRunState run)
    {
        var act = run.CurrentActIndex;
        var history = run.MapPointHistory;
        return act < 0 || act >= history.Count ? 0 : EventRooms(history[act]);
    }

    /// <summary>One act's map history, counted.</summary>
    public static int EventRooms(IEnumerable<MapPointHistoryEntry> act) =>
        StoryRules.EventRoomsIn(act.Select(point => (
            point.MapPointType == MapPointType.Ancient,
            point.Rooms is { Count: > 0 } rooms && rooms[0].RoomType == RoomType.Event)));

    /// <summary>The loc keys of every event option this player chose, in run
    /// order, from the run history.</summary>
    public static IEnumerable<string?> ChoiceKeys(
        IEnumerable<IEnumerable<MapPointHistoryEntry>> history, ulong playerId) =>
        history
            .SelectMany(act => act)
            .SelectMany(point => point.PlayerStats)
            .Where(stats => stats.PlayerId == playerId)
            .SelectMany(stats => stats.EventChoices)
            .Select(choice => choice.Title?.LocEntryKey);
}

/// <summary>
/// THE STORY EVENT REACHES THE MAP HERE: the game's own substitution seam,
/// <c>Hook.ModifyNextEvent</c>, called by <c>ActModel.PullNextEvent</c> once
/// per event room and BEFORE the pulled event is recorded as visited -- so
/// the run's visited list holds the story event and it is offered once.
///
/// WHICH EVENT ROOM (ruled 2026-10-19): the act's 1st, 2nd or 3rd, each
/// with chance 1/3, from one roll on the run's seed and the act
/// (<see cref="StoryRules.StoryRoomDue"/>) against the act's event rooms
/// already in the map history (<see cref="StoryHistory.EventRoomsThisAct"/>;
/// the room being pulled is not in it yet). A reload at the same room counts
/// the same rooms and reads the same roll.
///
/// A GAME SUBSTITUTION WINS. If something in the run already swapped the
/// event (Lantern Key's act-3 quest), the room still counts as an event room
/// and the story event waits for the act's next one.
///
/// SOLO draws her event type; CO-OP draws the one story room
/// (<see cref="StoryRules.RoomEventFor"/>). Both clients run this on the same
/// shared state (the seed, the act, every player's run history), so both
/// substitute the same model.
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
            var room = StoryRules.StoryRoomEventFor(
                run.Players.Select(p => (p.Character.GetType(), StoryHistory.RecordsFor(run, p))).ToList(),
                run.CurrentActIndex,
                (ulong)run.Rng.Seed,
                StoryHistory.EventRoomsThisAct(run));
            if (room == null) return;
            __result = ModelDb.GetById<EventModel>(ModelDb.GetId(room));
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
        if (!ResourceLoader.Exists(__result)) __result = story.FallbackPortraitPath;
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

/// <summary>
/// THE CO-OP ROOM'S TITLE. <c>EventModel.Title</c> reads the model's own
/// row; a co-op room copy showing a player's routed event reads that event's.
/// </summary>
[HarmonyPatch(typeof(EventModel), nameof(EventModel.Title), MethodType.Getter)]
internal static class EventModel_Title_Story_Patch
{
    [HarmonyPostfix]
    private static void Postfix(EventModel __instance, ref LocString __result)
    {
        if (__instance is not StoryEventModel story || story.TitleKeyOverride is not string key) return;
        __result = new LocString(StoryEventModel.Table, key);
    }
}

/// <summary>
/// THE CO-OP STORY ROOM (ruled 2026-10-16,
/// <c>review/active/klee-varka-story-chains-2026-10-14.md</c>, "Co-op").
/// [USER]: "Is it possible to instead give them separate events, appropriate
/// to their character? And for characters who have no events, they get a
/// placeholder like "heal 10 or gain 50 gold"".
///
/// ONE ROOM EVENT, A PAGE PER PLAYER. The game gives every player in an event
/// room a copy of ONE canonical event (<c>EventSynchronizer.BeginEvent</c>:
/// <c>canonicalEvent.ToMutable()</c> per player), and the room saves, titles
/// and preloads that one. So a co-op story room is this model, and each copy
/// shows its owner's own routed event (<see cref="StoryRules.CoopEventFor"/>,
/// from that player's saved story) or, with none, the placeholder
/// (<see cref="StoryCoop.QuietLanding"/>). Its options carry the routed
/// event's loc keys, so the choice the game writes to that player's run
/// history is the routed event's, and <see cref="StoryRules.Records"/> reads
/// it back as that player's alone.
///
/// IN SYNC. Each client builds every player's copy, and each copy routes
/// from shared state only (the run seed, the act, that player's character and
/// run history), so both clients show each player the same options in the
/// same order, and the option index the game sends means the same on both.
/// </summary>
public sealed class StoryCoopRoomEvent : StoryEventModel
{
    private StoryEvent? _routed;

    /// <summary>This copy's event: its owner's, or the placeholder.</summary>
    protected override StoryEvent Data => _routed ?? StoryCoop.QuietLanding;

    internal override CharacterStory? Story =>
        _routed == null ? null : StoryRegistry.All.FirstOrDefault(s => s.Events.Contains(_routed));

    protected override string LocEntry =>
        _routed == null ? Id.Entry : StoryRegistry.EntryOf(_routed.EventType);

    internal override string FallbackPortraitPath => StoryCoop.QuietLanding.FallbackPortraitPath;

    /// <summary>Every player takes the options on their own page.</summary>
    protected override bool IsOwners => true;

    protected override void ResolveFor(Player owner)
    {
        _routed = StoryRules.CoopEventFor(
            owner.Character.GetType(), StoryHistory.RecordsFor(owner.RunState, owner),
            owner.RunState.CurrentActIndex, (ulong)owner.RunState.Rng.Seed);
    }
}
