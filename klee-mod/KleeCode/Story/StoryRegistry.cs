using System;
using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Story;

/// <summary>
/// Every character that has a story table, and the pure decisions the story
/// machinery takes. Each decision is a function of plain values so the
/// headless suite (<c>KleeStoryTests</c>) runs the same code the game does.
/// </summary>
public static class StoryRegistry
{
    /// <summary>The tables. Yae adds hers here.</summary>
    public static readonly IReadOnlyList<CharacterStory> All = new[]
    {
        KleeStory.Table,
        VarkaStory.Table,
        FurinaStory.Table,
        KokomiStory.Table,
    };

    /// <summary>The table for this character, or null.</summary>
    public static CharacterStory? For(Type? character) =>
        character == null ? null : All.FirstOrDefault(s => s.Character == character);

    /// <summary>The table for this character model, or null.</summary>
    public static CharacterStory? For(CharacterModel? character) => For(character?.GetType());

    /// <summary>The <c>Id.Entry</c> the game files this character under
    /// (<c>KLEEMOD-KLEE</c> in a live game): <c>ModelDb.GetEntry</c>, the
    /// same function a model's own <c>Id</c> is built from.</summary>
    public static string EntryOf(Type type) => ModelDb.GetEntry(type);
}

/// <summary>The decisions, as pure functions.</summary>
public static class StoryRules
{
    /// <summary>
    /// The story event an event room in this act becomes IF IT IS THE ACT'S
    /// STORY ROOM, or null. Which event room that is, is
    /// <see cref="StoryRoomDue"/>'s call (<see cref="StoryRoomEventFor"/>
    /// asks both); at most one of hers fires an act (<see cref="Route"/>).
    /// The solo rule; a co-op table goes through <see cref="RoomEventFor"/>,
    /// where every player's event shares the act's story room.
    /// </summary>
    /// <param name="seats">Each player's character and that player's saved
    /// story (<see cref="Records"/>), in seat order.</param>
    /// <param name="actIndex">The act, 0 for act 1.</param>
    /// <param name="seed">The run's seed: act 1's draw.</param>
    public static StoryEvent? EventFor(
        IEnumerable<(Type Character, IReadOnlyList<StoryRecord> Records)> seats,
        int actIndex, ulong seed)
    {
        foreach (var (character, records) in seats)
        {
            var story = StoryRegistry.For(character);
            if (story == null) continue;
            var e = Route(story, actIndex, records, seed);
            if (e != null) return e;
        }
        return null;
    }

    /// <summary>
    /// WHEN THE STORY ROOM COMES (ruled 2026-10-19, the story rewards paper,
    /// pick 2: "1/3 at the act's first event room, 2/3 at the second, certain
    /// at the third"). Cumulative: the act's story room is its 1st, 2nd or
    /// 3rd event room with equal chance. Retune here, in one place.
    /// </summary>
    public static readonly IReadOnlyList<double> StoryRoomThresholds = new[] { 1.0 / 3.0, 2.0 / 3.0, 1.0 };

    /// <summary>
    /// The act's ONE story-room roll, in [0, 1): from the run seed and the
    /// act alone, never one of the run's own rngs (so no other roll in the
    /// run moves), and never re-rolled room by room. A reload, and every
    /// client at a co-op table, reads the same number.
    /// </summary>
    public static double StoryRoomRoll(ulong seed, int actIndex) =>
        (Mix(seed, "story.room.act" + actIndex) >> 11) * (1.0 / (1UL << 53));

    /// <summary>
    /// Whether the event room being pulled is the act's story room, given the
    /// act's event rooms already visited (<paramref name="eventRoomsBefore"/>:
    /// 0 at the act's first). Past the schedule's end it stays due, so a room
    /// another substitution took (Lantern Key's) passes the story on to the
    /// next one. An act with fewer event rooms than its roll needs never
    /// fires: the chain takes its skip branch (<see cref="Route"/>).
    /// </summary>
    public static bool StoryRoomDue(ulong seed, int actIndex, int eventRoomsBefore)
    {
        if (eventRoomsBefore < 0) return false;
        var i = Math.Min(eventRoomsBefore, StoryRoomThresholds.Count - 1);
        return StoryRoomRoll(seed, actIndex) < StoryRoomThresholds[i];
    }

    /// <summary>The act's story room as a 1-based event-room number (1, 2 or
    /// 3 under the ruled schedule): the first room <see cref="StoryRoomDue"/>
    /// holds for.</summary>
    public static int StoryRoomNumber(ulong seed, int actIndex)
    {
        var roll = StoryRoomRoll(seed, actIndex);
        for (var i = 0; i < StoryRoomThresholds.Count; i++)
        {
            if (roll < StoryRoomThresholds[i]) return i + 1;
        }
        return StoryRoomThresholds.Count;
    }

    /// <summary>
    /// THE ACT'S EVENT ROOMS SO FAR, from the run's map history for this act:
    /// each map point whose first room was an event room, story room or not,
    /// and whatever substitution (Lantern Key's) chose its event. An Ancient
    /// is not one. Read as the next room is pulled, the history does not yet
    /// hold that room (<c>RunManager</c> appends a point after it creates
    /// its room); read inside a room, it holds that room too, so it is the
    /// room's own 1-based number.
    /// </summary>
    public static int EventRoomsIn(IEnumerable<(bool IsAncient, bool FirstRoomIsEvent)> actHistory) =>
        actHistory.Count(p => !p.IsAncient && p.FirstRoomIsEvent);

    /// <summary>
    /// THE MODEL THE EVENT ROOM BEING PULLED BECOMES, or null for the drawn
    /// event: <see cref="RoomEventFor"/> when this is the act's story room
    /// (<see cref="StoryRoomDue"/>), else nothing. What the game's seam asks.
    /// </summary>
    public static Type? StoryRoomEventFor(
        IReadOnlyList<(Type Character, IReadOnlyList<StoryRecord> Records)> seats,
        int actIndex, ulong seed, int eventRoomsBefore) =>
        StoryRoomDue(seed, actIndex, eventRoomsBefore) ? RoomEventFor(seats, actIndex, seed) : null;

    /// <summary>
    /// THE MODEL AN EVENT ROOM BECOMES, or null for the drawn event.
    ///
    /// SOLO: her own event type (<see cref="EventFor"/>), unchanged.
    ///
    /// CO-OP (ruled 2026-10-16, the chains paper's "Co-op"): the act's story
    /// room is a story room for every player at once. Where any seat's story
    /// would claim this room (<see cref="CoopRoom"/>), the room becomes
    /// <see cref="StoryCoopRoomEvent"/>, whose copy for each player shows
    /// that player's own event or the placeholder.
    /// </summary>
    public static Type? RoomEventFor(
        IReadOnlyList<(Type Character, IReadOnlyList<StoryRecord> Records)> seats,
        int actIndex, ulong seed)
    {
        if (seats.Count <= 1) return EventFor(seats, actIndex, seed)?.EventType;
        return CoopRoom(seats, actIndex, seed) == null ? null : typeof(StoryCoopRoomEvent);
    }

    /// <summary>
    /// THE CO-OP STORY ROOM, seat by seat, or null when no seat's story has
    /// an event this act (the room stays the drawn event). Each seat gets its
    /// own routed event (<see cref="CoopEventFor"/>), or null: the
    /// placeholder, for a character with no story table, a story with no
    /// event this act, or a story that already fired this act.
    /// </summary>
    public static IReadOnlyList<StoryEvent?>? CoopRoom(
        IReadOnlyList<(Type Character, IReadOnlyList<StoryRecord> Records)> seats,
        int actIndex, ulong seed)
    {
        var room = seats.Select(s => CoopEventFor(s.Character, s.Records, actIndex, seed)).ToList();
        return room.Any(e => e != null) ? room : null;
    }

    /// <summary>One player's page in the co-op story room: her own routed
    /// event, by the solo rules (<see cref="Route"/>) on her own saved story,
    /// or null for the placeholder.</summary>
    public static StoryEvent? CoopEventFor(
        Type? character, IReadOnlyList<StoryRecord> records, int actIndex, ulong seed)
    {
        var story = StoryRegistry.For(character);
        return story == null ? null : Route(story, actIndex, records, seed);
    }

    /// <summary>
    /// THE CHAIN (review/active/klee-varka-story-chains-2026-10-14.md, "The
    /// shape"). Act 1 offers one of its events at random (drawn from the
    /// seed, so a reload draws the same one). Act 2 follows the thread act 1
    /// started; with no act-1 event it offers the home thread. Act 3 closes
    /// the thread act 2 followed; with no act-2 event it offers the home
    /// finale. Null once one of hers fired this act.
    /// </summary>
    public static StoryEvent? Route(
        CharacterStory story, int actIndex, IReadOnlyList<StoryRecord> records, ulong seed)
    {
        if (records.Any(r => r.ActIndex == actIndex)) return null;
        var inAct = story.Events.Where(e => e.ActIndex == actIndex).ToList();
        if (inAct.Count == 0) return null;
        if (actIndex == 0)
        {
            return inAct[Draw(seed, story.Name + ".act1", inAct.Count)];
        }
        var before = records.FirstOrDefault(r => r.ActIndex == actIndex - 1);
        if (before != null)
        {
            var next = inAct.FirstOrDefault(e => e.Follows.Contains(before.EventType));
            if (next != null) return next;
        }
        return inAct.FirstOrDefault(e => e.Home);
    }

    /// <summary>A draw in [0, n) from the seed and a salt, without touching
    /// any of the run's own rngs (so every later roll stays where it was).</summary>
    public static int Draw(ulong seed, string salt, int n) => (int)(Mix(seed, salt) % (ulong)n);

    /// <summary>The seed and a salt, hashed (FNV-1a, then splitmix64).</summary>
    private static ulong Mix(ulong seed, string salt)
    {
        ulong h = 14695981039346656037UL; // FNV-1a
        foreach (var ch in salt)
        {
            h ^= ch;
            h *= 1099511628211UL;
        }
        var z = seed ^ h;
        z += 0x9E3779B97F4A7C15UL; // splitmix64
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBUL;
        z ^= z >> 31;
        return z;
    }

    /// <summary>
    /// THE SAVED STORY, read from what the game already saves: the run's
    /// visited events (each story event belongs to one act) and the player's
    /// event choices in the run history, whose titles are the options' loc
    /// keys (<c>ENTRY.pages.INITIAL.options.KEY.title</c>).
    ///
    /// A CHOICE IS ALSO A VISIT. In a co-op story room
    /// (<see cref="StoryCoopRoomEvent"/>) the run visits the room's model,
    /// not a player's event; her choice under that event's keys, in HER run
    /// history, is what says it fired, and fired for her alone.
    /// </summary>
    public static List<StoryRecord> Records(
        CharacterStory story, Func<Type, bool> visited, IEnumerable<string?> choiceKeys,
        Func<Type, string> entryOf)
    {
        var keys = choiceKeys.Where(k => k != null).Select(k => k!).ToList();
        var records = new List<StoryRecord>();
        foreach (var e in story.Events)
        {
            var prefix = entryOf(e.EventType) + ".pages.INITIAL.options.";
            string? option = null;
            foreach (var k in keys)
            {
                if (k.StartsWith(prefix, StringComparison.Ordinal) && k.EndsWith(".title", StringComparison.Ordinal))
                {
                    option = k[prefix.Length..^".title".Length];
                }
            }
            if (option == null && !visited(e.EventType)) continue;
            records.Add(new StoryRecord(e.ActIndex, e.EventType, option));
        }
        return records;
    }

    /// <summary>The line the page opens with, or null: the first of the
    /// event's openings that holds.</summary>
    public static StoryOpening? OpeningFor(StoryEvent e, IReadOnlyList<StoryRecord> records) =>
        e.Openings.FirstOrDefault(o => o.When.Holds(records));

    /// <summary>The options offered: those whose condition holds.</summary>
    public static List<StoryOption> OptionsFor(StoryEvent e, IReadOnlyList<StoryRecord> records) =>
        e.Options.Where(o => o.ShownIf == null || o.ShownIf.Holds(records)).ToList();

    /// <summary>
    /// "Empty and unaffordable cases follow the base game, which locks an
    /// option it cannot pay (Luminous Choir)": a Gold price above the
    /// player's Gold; "Remove every Curse" with no Curse; Remove or Transform
    /// with no eligible card; "Upgrade N random cards that place a Bomb" with
    /// none; "Choose 1 of 3 random ..." with no card to offer (fewer than three
    /// is not a lock: those there are are offered). "Remove every X" with none
    /// is not a lock: that part does nothing.
    /// </summary>
    public static bool IsLocked(StoryOption option, StoryDeckView deck)
    {
        foreach (var e in option.Effects)
        {
            switch (e.Kind)
            {
                case StoryEffectKind.LoseGold when deck.Gold < e.Amount:
                case StoryEffectKind.RemoveCard when deck.Removable == 0:
                case StoryEffectKind.TransformCards when deck.Transformable == 0:
                case StoryEffectKind.UpgradeRandomBombCards when deck.UpgradableBombPlacers == 0:
                case StoryEffectKind.RemoveEveryCurseLoseGoldEach
                    when deck.RemovableCurses == 0 || deck.Gold < e.Amount * deck.RemovableCurses:
                case StoryEffectKind.ChooseOfferToDeck or StoryEffectKind.ChooseFromPoolToDeck
                    when deck.OfferSize != null && deck.OfferSize(e) == 0:
                    return true;
            }
        }
        return false;
    }

    /// <summary>Whether this player may take the event's options: it is
    /// HER event. Everyone else at the table gets the page and Proceed (a
    /// co-op room saved before the co-op story rooms; since then a co-op
    /// table draws <see cref="StoryCoopRoomEvent"/>, where everyone plays).</summary>
    public static bool IsOwnersEvent(Type? ownerCharacter, Type eventType) =>
        StoryRegistry.For(ownerCharacter)?.Events.Any(e => e.EventType == eventType) ?? false;

    /// <summary>
    /// "Drops below a third of max HP": this change took her from at least a
    /// third to under it, and she is still standing. A fight she STARTS below
    /// a third never "drops" there, so it says nothing until she heals above
    /// and falls again -- and even then only once a combat.
    /// </summary>
    public static bool CrossedBelowThird(int hpBefore, int hpAfter, int maxHp) =>
        maxHp > 0 && hpAfter > 0 && hpAfter * 3 < maxHp && hpBefore * 3 >= maxHp;

    /// <summary>"Her biggest Bomb (30 or more damage at once)": one Bomb's
    /// explosion that landed 30 or more. A Mine is not a Bomb here.</summary>
    public const int BigBombDamage = 30;

    public static bool IsBigBomb(bool isMine, int dealt) => !isMine && dealt >= BigBombDamage;

    /// <summary>
    /// The pair exchange at a boss for this speaker, or null: the first
    /// partner in her table who is also at the table. One exchange per boss,
    /// and it stands in for her solo boss line, so a fight opens on two
    /// bubbles rather than three.
    /// </summary>
    public static PairExchange? PairFor(CharacterStory story, IEnumerable<Type> others)
    {
        var present = others.ToHashSet();
        return story.Pairs.FirstOrDefault(p => present.Contains(p.Partner));
    }

    /// <summary>A story Curse (Klee's Confinement, Varka's Overdue Reports):
    /// "After 3 combats, remove this from your deck."</summary>
    public const int StoryCurseCombats = 3;

    /// <summary>One more combat served; true when it is the last.</summary>
    public static bool StoryCurseServedOut(int combatsServed) =>
        combatsServed >= StoryCurseCombats;

    /// <summary>Whether this card's play is the character's signature
    /// moment (Varka: Four Winds' Ascension or Dandelion Gale), by her
    /// table.</summary>
    public static bool IsSignaturePlay(CharacterStory story, Type? card) =>
        card != null && story.SignatureCards.Contains(card);

    /// <summary>
    /// WHO SPEAKS AT A BOSS'S ENTRY, by seat. Each story character speaks
    /// once: in a pair exchange if one is written for her and someone at the
    /// table, held in EITHER character's table (Klee's table holds the Varka
    /// and Klee pair), else her own boss line. A pair stands in for both its
    /// speakers' solo lines, so a fight opens on two bubbles, not three.
    /// Seats are walked in order; a seat's own table is asked first.
    /// </summary>
    public static List<BossEntrySpeech> BossEntryPlan(IReadOnlyList<Type> seats)
    {
        var plan = new List<BossEntrySpeech>();
        var spoken = new HashSet<int>();
        for (var i = 0; i < seats.Count; i++)
        {
            if (spoken.Contains(i)) continue;
            var own = StoryRegistry.For(seats[i]);
            BossEntrySpeech? pair = null;
            if (own != null)
            {
                foreach (var p in own.Pairs)
                {
                    var j = FreeSeat(seats, spoken, i, p.Partner);
                    if (j >= 0) { pair = new BossEntrySpeech(own, i, p, j); break; }
                }
            }
            if (pair == null)
            {
                for (var j = 0; j < seats.Count && pair == null; j++)
                {
                    if (j == i || spoken.Contains(j)) continue;
                    var other = StoryRegistry.For(seats[j]);
                    var p = other?.Pairs.FirstOrDefault(x => x.Partner == seats[i]);
                    if (p != null) pair = new BossEntrySpeech(other!, j, p, i);
                }
            }
            if (pair != null)
            {
                plan.Add(pair);
                spoken.Add(pair.OwnerSeat);
                spoken.Add(pair.PartnerSeat);
            }
            else if (own?.Lines != null)
            {
                // A table with no combat lines (Kokomi's, while her lines
                // are an open pick) has no solo line to speak.
                plan.Add(new BossEntrySpeech(own, i, null, -1));
                spoken.Add(i);
            }
        }
        return plan;
    }

    private static int FreeSeat(IReadOnlyList<Type> seats, HashSet<int> spoken, int self, Type character)
    {
        for (var j = 0; j < seats.Count; j++)
        {
            if (j != self && !spoken.Contains(j) && seats[j] == character) return j;
        }
        return -1;
    }

    /// <summary>The sheet id of a card from its <c>Id.Entry</c>:
    /// <c>KLEEMOD-PROTO_KO_POP</c> -> <c>proto_ko_pop</c>.</summary>
    public static string SheetIdOf(string entry)
    {
        var dash = entry.IndexOf('-');
        return (dash >= 0 ? entry[(dash + 1)..] : entry).ToLowerInvariant();
    }

    /// <summary>Whether a card places a Bomb, by her table.</summary>
    public static bool PlacesBomb(CharacterStory story, string cardEntry) =>
        story.BombPlacers.Contains(SheetIdOf(cardEntry));

    /// <summary>
    /// "Upgrade N random cards that place a Bomb (if fewer exist, upgrade
    /// those there are)": up to <paramref name="count"/> distinct picks from
    /// <paramref name="candidates"/>, each drawn by <paramref name="pickIndex"/>
    /// (the event's own Rng in the game) from what is left.
    /// </summary>
    public static List<T> PickRandom<T>(IReadOnlyList<T> candidates, int count, Func<int, int> pickIndex)
    {
        var left = candidates.ToList();
        var picked = new List<T>();
        while (picked.Count < count && left.Count > 0)
        {
            var i = pickIndex(left.Count);
            picked.Add(left[i]);
            left.RemoveAt(i);
        }
        return picked;
    }
}

/// <summary>What a lock reads off the owner: Gold, and how many deck cards
/// can be removed, transformed, are removable Curses, and are upgradable
/// cards that place a Bomb; and how many cards a card offer has to show
/// (<see cref="OfferSize"/>; null: not asked, never a lock).</summary>
public sealed record StoryDeckView(
    int Gold, int Removable, int Transformable, int RemovableCurses, int UpgradableBombPlacers,
    Func<StoryEffect, int>? OfferSize = null);

/// <summary>One speech at a boss's entry: the table <see cref="Story"/> whose
/// rows are spoken, the seat that owns it, and either a pair exchange with
/// the partner's seat or (<see cref="Pair"/> null) the owner's solo line.</summary>
public sealed record BossEntrySpeech(
    CharacterStory Story, int OwnerSeat, PairExchange? Pair, int PartnerSeat);

/// <summary>
/// Once-a-combat latches. Keyed by the combat (a fresh combat is a fresh
/// latch set) and by whatever the line is about -- the speaker and the line.
/// </summary>
public sealed class CombatLatch
{
    private readonly HashSet<(object, string)> _taken = new();

    /// <summary>True the first time this (who, what) is asked; false after.</summary>
    public bool TryTake(object who, string what) => _taken.Add((who, what));
}
