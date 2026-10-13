using System;
using System.Collections.Generic;
using Godot;

namespace KleeMod.Story;

/// <summary>
/// THE SHAPE OF ONE CHARACTER'S STORY IN THE RUN (Klee story batches 1 and 2,
/// <c>review/ruled/klee-story-batch-1-2026-10-12.md</c> and
/// <c>klee-story-batch-2-2026-10-12.md</c>).
///
/// ONE DATA TABLE PER CHARACTER. Every line a player reads, every event page
/// and every option's effect is a value in a <see cref="CharacterStory"/>;
/// the machinery (<see cref="StoryAncients"/>, <see cref="StoryEventModel"/>,
/// <see cref="StoryLines"/>, <see cref="StoryLoc"/>) reads the table and names
/// no character. Kokomi, Furina and Varka get their lines by adding a table
/// to <see cref="StoryRegistry.All"/> and, for an event, a one-line
/// <see cref="StoryEventModel"/> subclass (the game's ModelDb needs one type
/// per event).
///
/// THE WORDS ARE THE PAPER'S. Markdown emphasis in the paper is carried as
/// the game's own markup: <c>*word*</c> as <c>[i]word[/i]</c> and
/// <c>**Name**</c> as <c>[gold]Name[/gold]</c>; the outer quotation marks of a
/// spoken line are the speech bubble's, not the line's.
/// <c>KleeStoryTests</c> reads every string back against the paper.
/// </summary>
public sealed class CharacterStory
{
    /// <summary>The character this table speaks for.</summary>
    public required Type Character { get; init; }

    /// <summary>The name the result pages label her lines with.</summary>
    public required string Name { get; init; }

    /// <summary>Character select: the intro's first line (the paper's bold).</summary>
    public required string IntroTitle { get; init; }

    /// <summary>Character select: the intro's second line.</summary>
    public required string IntroLine { get; init; }

    /// <summary>The two-line intro as the select screen prints it.</summary>
    public string Intro => IntroTitle + "\n" + IntroLine;

    /// <summary>One exchange per Ancient, on her first visit to it.</summary>
    public required IReadOnlyList<AncientExchange> Ancients { get; init; }

    /// <summary>Speech bubbles in combat, and the run's last word.</summary>
    public required CombatLines Lines { get; init; }

    /// <summary>A two-character exchange at each boss, partner first.</summary>
    public required IReadOnlyList<PairExchange> Pairs { get; init; }

    /// <summary>Her own events, at most one per act.</summary>
    public required IReadOnlyList<StoryEvent> Events { get; init; }

    /// <summary>The sheet ids (<c>docs/prototype-surface.yaml</c>) of her
    /// cards that place a Bomb -- what "Upgrade 2 random cards that place a
    /// Bomb" draws from. Mine-only cards are not in it.</summary>
    public IReadOnlyCollection<string> BombPlacers { get; init; } = Array.Empty<string>();
}

/// <summary>An Ancient's line and her answer. <see cref="Ancient"/> is the
/// paper's name for it, <see cref="AncientEntry"/> the base game's
/// <c>Id.Entry</c>.</summary>
public sealed record AncientExchange(
    string Ancient, string AncientEntry, string AncientLine, string CharacterLine);

/// <summary>The six moments the paper gives a combat line to.</summary>
public sealed record CombatLines(
    string BossEntry, string LowHp, string BigBomb, string BossKill,
    string RunLoss, string RunWin);

/// <summary>Who the partner is, what they say, and her answer.</summary>
public sealed record PairExchange(
    Type Partner, string PartnerName, string PartnerLine, string OwnLine);

/// <summary>What an option does. Every effect a story event can have is one
/// of these, so a new event is data and not code.</summary>
public enum StoryEffectKind
{
    /// <summary>Gain <c>Amount</c> Gold, then add <c>Card</c> to the deck.</summary>
    GainGoldAddCard,

    /// <summary>Add <c>Card</c> to the deck.</summary>
    AddCard,

    /// <summary>Add an upgraded <c>Card</c> to the deck.</summary>
    AddUpgradedCard,

    /// <summary>Remove a card of the player's choice from the deck.</summary>
    RemoveCard,

    /// <summary>Heal <c>Amount</c> HP.</summary>
    Heal,

    /// <summary>Remove a Curse of the player's choice; with none, gain
    /// <c>Amount</c> Gold.</summary>
    RemoveCurseElseGold,

    /// <summary>Upgrade <c>Amount</c> random cards that place a Bomb (all of
    /// them if there are fewer).</summary>
    UpgradeRandomBombCards,
}

/// <summary>One option's effect.</summary>
public sealed record StoryEffect(StoryEffectKind Kind, int Amount = 0, Type? Card = null);

/// <summary>One option: its button, its effect line, what it does, and the
/// page it leaves on screen (<c>null</c>: the event's own page stays).</summary>
public sealed record StoryOption(
    string Key, string Title, string Description, StoryEffect Effect,
    string? Result = null);

/// <summary>One event: the act it belongs to (0 is act 1), the model type
/// the game knows it by, its page, its options and its picture.</summary>
public sealed record StoryEvent(
    int ActIndex, Type EventType, string Title, string Body,
    IReadOnlyList<StoryOption> Options,
    Func<Texture2D?> Portrait, string FallbackPortraitPath);
