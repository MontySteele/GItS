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
    /// <summary>The tables. Kokomi and Furina add theirs here.</summary>
    public static readonly IReadOnlyList<CharacterStory> All = new[]
    {
        KleeStory.Table,
        VarkaStory.Table,
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
    /// The story event an event room in this act becomes, or null.
    ///
    /// THE FIRST EVENT ROOM OF THE ACT. The paper calls each one "Act N's
    /// story event", so it is guaranteed rather than one more draw in a pool
    /// of thirty: the first event a story character's run pulls in the act is
    /// her event, once (an event already seen is never offered again). With
    /// two story characters at one table the first player's event comes
    /// first, and the next player's at the act's next event room.
    /// </summary>
    /// <param name="characters">The run's players' characters, in seat order.</param>
    /// <param name="actIndex">The act, 0 for act 1.</param>
    /// <param name="alreadySeen">Whether an event type has been visited this run.</param>
    public static StoryEvent? EventFor(
        IEnumerable<Type> characters, int actIndex, Func<Type, bool> alreadySeen)
    {
        foreach (var character in characters)
        {
            var story = StoryRegistry.For(character);
            if (story == null) continue;
            foreach (var e in story.Events)
            {
                if (e.ActIndex == actIndex && !alreadySeen(e.EventType)) return e;
            }
        }
        return null;
    }

    /// <summary>Whether this player may take the event's options: it is
    /// HER event. Everyone else at the table gets the page and Proceed.</summary>
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
            else if (own != null)
            {
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
