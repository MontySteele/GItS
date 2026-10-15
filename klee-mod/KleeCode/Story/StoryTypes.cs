using System;
using System.Collections.Generic;
using Godot;
using MegaCrit.Sts2.Core.Models;

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
/// no character. Kokomi and Furina get their lines (Varka has his, VarkaStory.cs) by adding a table
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

    /// <summary>The cards whose play speaks the signature line, once a
    /// combat (Varka: Four Winds' Ascension and Dandelion Gale, the Ancient
    /// that replaces it). Empty: the line has its own trigger (Klee: her
    /// biggest Bomb, called from the Bomb's explosion).</summary>
    public IReadOnlyCollection<Type> SignatureCards { get; init; } = Array.Empty<Type>();

    /// <summary>What "Choose 1 of 3 random ..." draws from (Varka: his pool
    /// Knights, the pool Knights' Roll Call offers). Null: none.</summary>
    public Func<IReadOnlyList<CardModel>>? ChoicePool { get; init; }
}

/// <summary>An Ancient's line and her answer. <see cref="Ancient"/> is the
/// paper's name for it, <see cref="AncientEntry"/> the base game's
/// <c>Id.Entry</c>.</summary>
public sealed record AncientExchange(
    string Ancient, string AncientEntry, string AncientLine, string CharacterLine);

/// <summary>The six moments the paper gives a combat line to. The third is
/// the character's signature moment: Klee's biggest Bomb (30 or more at
/// once), Varka's Four Winds' Ascension.</summary>
public sealed record CombatLines(
    string BossEntry, string LowHp, string Signature, string BossKill,
    string RunLoss, string RunWin);

/// <summary>Who the partner is, what they say, and her answer. The partner
/// speaks first unless <see cref="OwnFirst"/> (the paper's order: Varka
/// opens his exchange with Kokomi).</summary>
public sealed record PairExchange(
    Type Partner, string PartnerName, string PartnerLine, string OwnLine,
    bool OwnFirst = false);

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

    /// <summary>Upgrade <c>Amount</c> random upgradable cards (all of them
    /// if there are fewer).</summary>
    UpgradeRandomCards,

    /// <summary>Lose <c>HpLoss</c> HP, then upgrade <c>Amount</c> random
    /// upgradable cards.</summary>
    LoseHpUpgradeRandomCards,

    /// <summary>Choose 1 of <c>Amount</c> distinct random cards from the
    /// table's <see cref="CharacterStory.ChoicePool"/> and add it to the
    /// deck.</summary>
    ChooseFromPoolToDeck,

    /// <summary>Nothing (the skip).</summary>
    Nothing,

    // ---- The story chains (review/active/klee-varka-story-chains-2026-10-14.md)

    /// <summary>Lose <c>Amount</c> HP (Dense Vegetation's cost: unblockable).</summary>
    LoseHp,

    /// <summary>Gain <c>Amount</c> Gold.</summary>
    GainGold,

    /// <summary>Lose <c>Amount</c> Gold. A price: locked when the player has
    /// less.</summary>
    LoseGold,

    /// <summary>Gain a random relic (Luminous Choir's pull).</summary>
    GainRandomRelic,

    /// <summary>Gain a random Rare relic.</summary>
    GainRandomRareRelic,

    /// <summary>Gain <c>Amount</c> random potions, offered as rewards
    /// (Endless Conveyor's Suspicious Condiment).</summary>
    GainRandomPotions,

    /// <summary>Transform <c>Amount</c> cards of the player's choice
    /// (Morphic Grove). Locked with no card that can be transformed.</summary>
    TransformCards,

    /// <summary>Remove every copy of <c>Card</c> from the deck. With none,
    /// nothing.</summary>
    RemoveEvery,

    /// <summary>Remove every Curse; lose <c>Amount</c> Gold for each.
    /// Locked with no Curse, or with less Gold than the price.</summary>
    RemoveEveryCurseLoseGoldEach,

    /// <summary>Upgrade a card of the player's choice.</summary>
    UpgradeChosenCard,
}

/// <summary>One option's effect.</summary>
public sealed record StoryEffect(
    StoryEffectKind Kind, int Amount = 0, Type? Card = null, int HpLoss = 0);

/// <summary>One option: its button, its effect line, what it does, and the
/// page it leaves on screen (<c>null</c>: the event's own page stays).
/// <see cref="Then"/> are further steps, run in order after
/// <see cref="Effect"/> ("Lose 10 HP. Gain a random relic."). An option with
/// <see cref="ShownIf"/> is offered only when the condition holds on the
/// run's saved story (Mom's Last Note's "Saved the cache" slot).</summary>
public sealed record StoryOption(
    string Key, string Title, string Description, StoryEffect Effect,
    string? Result = null)
{
    public IReadOnlyList<StoryEffect> Then { get; init; } = Array.Empty<StoryEffect>();

    public StoryCondition? ShownIf { get; init; }

    /// <summary>Every step, in order.</summary>
    public IReadOnlyList<StoryEffect> Effects
    {
        get
        {
            var all = new List<StoryEffect>(1 + Then.Count) { Effect };
            all.AddRange(Then);
            return all;
        }
    }

    /// <summary>All the HP the option costs (for the game's lethal warning).</summary>
    public int HpCost
    {
        get
        {
            var total = 0;
            foreach (var e in Effects)
            {
                total += e.HpLoss;
                if (e.Kind == StoryEffectKind.LoseHp) total += e.Amount;
            }
            return total;
        }
    }
}

/// <summary>One event: the act it belongs to (0 is act 1), the model type
/// the game knows it by, its page, its options and its picture.
///
/// THE CHAIN. <see cref="Follows"/> names the events of the act before that
/// lead here; <see cref="Home"/> marks the act's home event, offered when the
/// act before brought none. Act 1's events are drawn at random.
/// <see cref="Openings"/> are the lines the page opens with, matched in order
/// against the run's saved story; the first that holds is used.</summary>
public sealed record StoryEvent(
    int ActIndex, Type EventType, string Title, string Body,
    IReadOnlyList<StoryOption> Options,
    Func<Texture2D?> Portrait, string FallbackPortraitPath)
{
    public IReadOnlyList<Type> Follows { get; init; } = Array.Empty<Type>();

    public bool Home { get; init; }

    public IReadOnlyList<StoryOpening> Openings { get; init; } = Array.Empty<StoryOpening>();
}

/// <summary>What the run saved for one story event: the act it fired in, the
/// event, and the option chosen (null while it is still open).</summary>
public sealed record StoryRecord(int ActIndex, Type EventType, string? OptionKey);

/// <summary>
/// A test against the run's saved story. <see cref="Fired"/>: that event fired
/// (and, with <see cref="Option"/>, that option was chosen).
/// <see cref="NoEventInAct"/>: no story event fired in that act.
/// <see cref="Not"/> inverts the whole test. All empty: always true.
/// </summary>
public sealed record StoryCondition(
    Type? Fired = null, string? Option = null, int? NoEventInAct = null, bool Not = false)
{
    public bool Holds(IReadOnlyList<StoryRecord> records)
    {
        var holds = true;
        if (Fired != null)
        {
            holds = false;
            foreach (var r in records)
            {
                if (r.EventType == Fired && (Option == null || r.OptionKey == Option)) holds = true;
            }
        }
        if (holds && NoEventInAct is int act)
        {
            foreach (var r in records)
            {
                if (r.ActIndex == act) holds = false;
            }
        }
        return Not ? !holds : holds;
    }
}

/// <summary>A line the page opens with when <see cref="When"/> holds, and a
/// card removed from the owner's deck as the page opens (Doubt, when Dodoco
/// comes home).</summary>
public sealed record StoryOpening(
    string Key, StoryCondition When, string Line, Type? RemovesOnOpen = null);
