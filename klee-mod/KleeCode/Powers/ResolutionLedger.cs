using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Powers;

/// <summary>
/// `EB-349` and `EB-611`. WHAT RESOLVED, WHO IT HIT, AND IN WHAT ORDER.
///
/// THE STANDING FACT this closes is printed on the blind page itself, in
/// `understudy/blindplay_notes.AUTO_TURN_NOTE`: "What it played, what it aimed
/// at and what each card did are not on this page's data feed -- THERE IS NO
/// RECORD OF A CARD RESOLVING ON THE WIRE AT ALL." Every screen the bridge
/// sends is an after-state. A reader gets the board a turn left behind and
/// never the turn.
///
/// THE TWO FINDS THAT SHARE THIS ONE LEDGER.
///
///   `EB-349` (Kokomi r4d act 3, 1). A relic that plays a turn FOR the player
///   -- Vakuu -- took six openings, five of them from an empty hand, and
///   nothing on any screen said a turn had happened. The page names the relic
///   off its own printed sentence and states the gap, which is the whole of
///   what a page with no feed can do.
///
///   `EB-611` (Klee r23 lane 2 (c) 3). A multi-hit random `Set off` prints
///   only the after-state, so a seat could confirm WHICH bodies were hit and
///   never the ORDER -- and a random-target multi-hit is precisely the card
///   whose order decides whether the beat made sense. "Rapid Fire on a hallway
///   prints four ordered lines" is the row's acceptance.
///
/// SO A ROW IS ONE RESOLVED CARD and the hits sit under it in hit order. No
/// number is derived and none is predicted: the hit's amount is the DELIVERED
/// one, handed over by `Hook.AfterDamageReceived`, which is the same figure
/// `PlayTelemetry.Damage` has always taken from that hook.
///
/// AUTO-PLAY IS THE GAME'S OWN FLAG AND NOT A GUESS ABOUT A RELIC.
/// `CardPlay.IsAutoPlay` is a required init property on every play the engine
/// makes (decompiled, sts2.dll 0.111.0 `41cef1ea`), so "the game played this
/// one" is read rather than inferred from which relic happens to be held. The
/// page's existing note matches on the relic's printed SENTENCE and will keep
/// doing so; what this adds is the turn itself.
///
/// `MeterLedger` IS A DIFFERENT ROUTE AND WAS ALREADY CHECKED (`EB-611`'s read
/// of 2026-09-07): it files a row per METER MOVEMENT with no bodies on it, so
/// it can say a Spark was spent and never what was hit.
///
/// THE SINGLE FUNNEL IS `PlayTelemetryHooks`, the mod's own board-wide hook
/// listener, which already sits on all three broadcasts this needs --
/// `BeforeCardPlayed`, `AfterDamageReceived`, `AfterCardPlayed`. A card cannot
/// resolve off that list, which is the row's acceptance in the same sense
/// <see cref="ReactionEffects.Resolve"/> is `ReactionLog`'s.
///
/// IT IS <see cref="ReactionLog"/>'S SHAPE AND ITS WINDOW, deliberately, down
/// to the carry: the wire keys ARE the contract; `Snapshot` hands primitives
/// to `vendor/STS2_MCP/gits/GitsResolutionLedger.cs` by reflection because
/// that assembly cannot reference this one; and a card that resolved after the
/// player ended their turn carries exactly one turn rather than being dropped
/// before a page could print it (`EB-710`).
///
/// SHIPPED CODE AND NOT ARM-GATED, `ReactionLog`'s reason one rule over: every
/// arm plays cards, and a Klee lane's ordered Rapid Fire is as unprinted as a
/// Kokomi lane's auto-played turn was. Empty is a fact; absent is a build with
/// no klee mod.
///
/// A CAP, AND WHY. `MeterLedger`'s 400-row cap exists because a grader reads
/// rows after the fact; this ledger is read by a PAGE, one turn at a time, so
/// the only growth risk is a single pathological turn. The cap is on rows per
/// turn and on hits per row, and when it bites the row says so rather than
/// silently truncating -- a reader adding up four lines that should be six is
/// the `EB-518` error all over again.
/// </summary>
public static class ResolutionLedger
{
    /// <summary>The most resolutions one turn will file. A turn past this is
    /// a turn no page can print anyway, and the overflow flag on the last row
    /// is what the reader is told.</summary>
    public const int MaxRows = 120;

    /// <summary>The most hits one resolution will file.</summary>
    public const int MaxHits = 40;

    /// <summary>One landed hit, as the page prints it: the body, the HP that
    /// came off it, what its Block ate, and the id the page names bodies by.
    ///
    /// TWO NUMBERS AND NOT ONE, because a reader reconciling a beat is doing
    /// two different sums. `Amount` is `DamageResult.UnblockedDamage` -- the
    /// HP that moved, which is what a seat watching the bar is subtracting --
    /// and `Blocked` is `DamageResult.BlockedDamage`, without which a hit that
    /// landed entirely on Block would read as a hit that did not happen. The
    /// game's own doc comments on those two properties are the definitions.
    /// </summary>
    public readonly record struct Hit(string Target, int Amount, int Blocked,
                                      string CombatId);

    /// <summary>One resolved card.
    ///
    /// `AutoPlayed` is `CardPlay.IsAutoPlay`. `Carried` is
    /// <see cref="ReactionLog.Reacted"/>'s and means the same thing: the card
    /// resolved after the player ended their turn and no page has printed it.
    /// `Overflowed` is true on a row whose hits hit <see cref="MaxHits"/>.
    /// </summary>
    public sealed record Resolved(string CardId, string Card, bool AutoPlayed)
    {
        public List<Hit> Hits { get; } = new();
        public bool Carried { get; set; }
        public bool Overflowed { get; set; }
    }

    private static readonly List<Resolved> Rows = new();

    /// <summary>The row hits are being filed against, or null between plays.
    /// The game loop is single threaded and a card resolves whole before the
    /// next one starts, so one open row is the whole of the bookkeeping --
    /// `KokomiPlan.NoteRider`'s own posture one file over.</summary>
    private static Resolved? _open;

    /// <summary>Where the player stopped watching, or negative for "no mark
    /// was taken this turn". <see cref="ReactionLog.MarkPlayerTurnEnd"/>'s
    /// twin, taken from the same broadcast.</summary>
    private static int _playerTurnEnd = -1;

    /// <summary>"The player's turn is ending here." `EB-710`'s mark, and the
    /// argument for it is written out on
    /// <see cref="ReactionLog.MarkPlayerTurnEnd"/>.</summary>
    public static void MarkPlayerTurnEnd() => _playerTurnEnd = Rows.Count;

    /// <summary>
    /// Open the turn's window, carrying the rows the player has not been
    /// shown. <see cref="ReactionLog.MarkTurnStart"/>'s argument, whole: this
    /// fires at the end of the ENEMY turn, so a straight clear would drop
    /// every row filed since the player last had control -- and an auto-played
    /// turn is exactly such a row. Rows past the mark survive one turn,
    /// flagged; rows before it have been printed and go. NO MARK, NO CARRY.
    /// </summary>
    public static void MarkTurnStart()
    {
        var carried = new List<Resolved>();
        for (var i = _playerTurnEnd; i >= 0 && i < Rows.Count; i++)
        {
            Rows[i].Carried = true;
            carried.Add(Rows[i]);
        }
        Rows.Clear();
        Rows.AddRange(carried);
        _playerTurnEnd = -1;
        _open = null;
    }

    /// <summary>Drop everything. Called when a combat opens, so one fight's
    /// resolutions cannot be read as the next one's -- `MeterLedger`'s
    /// `ResetFight` and its reason (`EB-216`).</summary>
    public static void ResetFight()
    {
        Rows.Clear();
        _open = null;
        _playerTurnEnd = -1;
    }

    /// <summary>
    /// "A card is resolving." Opens the row its hits will be filed against.
    ///
    /// FIRST IN SERIES ONLY, the gate `PlayTelemetryHooks.BeforeCardPlayed`
    /// and `SparkPower.BeforeCardPlayed` already use: a replayed card is one
    /// play to a reader and several to the engine, and four rows reading
    /// `Rapid Fire` would be `EB-518`'s division problem in a new place.
    /// </summary>
    public static void OpenPlay(CardPlay? cardPlay)
    {
        if (cardPlay?.Card == null || !cardPlay.IsFirstInSeries) return;
        OpenPlay(Safe(() => cardPlay.Card.Id.Entry),
                 Safe(() => cardPlay.Card.Title?.ToString()),
                 cardPlay.IsAutoPlay);
    }

    /// <summary>
    /// The same open, taking the three facts rather than the game object.
    ///
    /// IT EXISTS SO THE LEDGER CAN BE PINNED HEADLESSLY. `CardPlay` has six
    /// required init properties, two of which are a live `CardModel` and a
    /// live `Player`, so a test that had to build one could not run in
    /// `KleeTests` at all -- and the behaviour worth pinning is this file's
    /// (the order, the caps, the window, the shape), not the game's. The
    /// overload above is the only caller in shipped code and this is the only
    /// place a row is minted, so the two cannot drift.
    /// </summary>
    public static void OpenPlay(string cardId, string card, bool autoPlayed)
    {
        if (Rows.Count >= MaxRows)
        {
            _open = null;
            return;
        }
        var row = new Resolved(cardId, card, autoPlayed);
        Rows.Add(row);
        _open = row;
    }

    /// <summary>
    /// "This much reached this body, inside the card that is resolving."
    ///
    /// ONE ROW PER HIT AND NOT PER BODY, which is `EB-611`'s whole point: four
    /// entries reading `Rapid Fire 6` divide among a hallway more than one
    /// way, and the beat that does not add up is the one that struck the same
    /// body twice. The ORDER is the list's order, which is the order the hook
    /// fired in, which is hit order.
    ///
    /// A HIT THAT MOVED NOTHING AT ALL IS NOT A HIT -- neither HP nor Block --
    /// and `RelicAnswerLog.Note`'s rule is deliberately NOT copied whole here.
    /// That log reports a subtraction a reader is trying to account for, so a
    /// zero there is noise; this one reports an ORDER, and a hit that landed
    /// entirely on Block is a place in that order. Dropping it would print
    /// three lines for a four-hit card, which is the `EB-611` defect wearing
    /// a different hat.
    ///
    /// DROPPED WHERE NO PLAY IS OPEN, deliberately: an enemy's attack, a
    /// bomb going off on nobody's turn and a relic's answer all reach this
    /// hook, and none of them is a card resolving. The relic's answer has its
    /// own receipt (`RelicAnswerLog`) and the reaction has `ReactionLog`.
    /// </summary>
    public static void NoteHit(Creature? target, int amount, int blocked)
    {
        if (_open == null || (amount <= 0 && blocked <= 0)) return;
        if (_open.Hits.Count >= MaxHits)
        {
            _open.Overflowed = true;
            return;
        }
        _open.Hits.Add(new Hit(Named(target), amount, blocked,
                               Safe(() => target?.CombatId.ToString())));
    }

    /// <summary>"That card has finished." Closes the row.</summary>
    public static void ClosePlay() => _open = null;

    /// <summary>A printed title, or `""`, and never a throw --
    /// <see cref="ReactionLog"/>'s bargain and its reason: a display read is a
    /// read of live game objects that a torn-down combat can leave half
    /// standing, and a LOG must never be the thing that ends a beat.</summary>
    private static string Named(Creature? creature) =>
        Safe(() => creature?.Monster?.Title.GetFormattedText()
                   ?? creature?.Name);

    private static string Safe(System.Func<string?> read)
    {
        try
        {
            return read() ?? string.Empty;
        }
        catch (System.Exception)
        {
            return string.Empty;
        }
    }

    /// <summary>
    /// THE WIRE'S VIEW. `ReactionLog.Snapshot`'s shape and contract: plain
    /// dictionaries of primitives, oldest first, read by reflection from the
    /// bridge. The key names here ARE the contract and
    /// `understudy/blindplay_board.resolutions` reads them.
    ///
    /// PRESENT AND EMPTY ON A TURN NOTHING RESOLVED, which is a fact and not a
    /// hole -- and on an auto-played turn it is THE fact, because a turn the
    /// game took with an empty hand files no rows and the page may then say so
    /// instead of hedging. An ABSENT key is a build with no ledger at all.
    /// </summary>
    public static List<Dictionary<string, object?>> Snapshot() =>
        Rows.ConvertAll(row => new Dictionary<string, object?>
        {
            ["card_id"] = row.CardId,
            ["card"] = row.Card,
            ["auto_played"] = row.AutoPlayed,
            ["carried"] = row.Carried,
            ["overflowed"] = row.Overflowed,
            ["hits"] = row.Hits.ConvertAll(hit =>
                new Dictionary<string, object?>
                {
                    ["target"] = hit.Target,
                    ["amount"] = hit.Amount,
                    ["blocked"] = hit.Blocked,
                    ["combat_id"] = hit.CombatId,
                }),
        });
}
