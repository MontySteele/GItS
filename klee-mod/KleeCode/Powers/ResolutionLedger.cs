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
    ///
    /// `Killed` marks the entry <see cref="NoteKill(Creature?)"/> files for a
    /// body that DIED inside the play. The game never hands the killing hit to
    /// `AfterDamageReceived` (`CreatureCmd.Damage` skips that broadcast for a
    /// creature the hit killed), so a kill arrives with no numbers at all, and
    /// the flag is what keeps the page from printing it as a zero.
    /// </summary>
    /// `OnPlayer` (2026-10-01, a Varka seat) marks a hit that landed on a
    /// PLAYER while the card resolved -- an enemy's Thorns answering the
    /// attack, say. The seat read one under Diluc's row as "Overload hit
    /// Varka"; a reaction's splash only ever reaches enemies
    /// (`CombatState.HittableEnemies`), so the page says whose HP it was.
    /// `Source` (2026-10-04, the Klee w20 round) is who dealt a hit that
    /// landed on a player -- the enemy whose Thorns answered the attack --
    /// so the page names it instead of guessing; empty where the game named
    /// no dealer.
    /// `Self` (the Furina pool-75 round, 2026-10-09) marks a hit on a player
    /// the game filed with no dealer but the player: her own HP cost, such
    /// as a Drain. With no dealer on the wire the page guessed the one
    /// Thorns holder, and Ousia Pledge's Drain 3 read as "from Toadpole's
    /// Thorns" (Thorns 2) on a Skill.
    public readonly record struct Hit(string Target, int Amount, int Blocked,
                                      string CombatId, bool Killed = false,
                                      bool OnPlayer = false,
                                      string Source = "",
                                      bool Self = false);

    /// <summary>A power the card put on an enemy, and by how much
    /// (2026-09-26, the Silent control seat: "Poison applied is never shown
    /// in 'what it did'"). `Amount` is the change the game reports to
    /// `AfterPowerAmountChanged`, signed, so a strip reads as one.</summary>
    public readonly record struct PowerApplied(string Target, string Power,
                                               int Amount, string CombatId);

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

        /// <summary>What happened inside this card that no other line of the
        /// page shows, in order (<see cref="NoteEvent"/>). On a
        /// <see cref="Between"/> row, what happened outside any play.</summary>
        public List<PageEvent> Events { get; } = new();

        /// <summary>A row that is not a card: it holds only the events filed
        /// while no play was open (an enemy's turn, the start of yours). Its
        /// card and id are empty, so a reader that predates it skips it.
        /// </summary>
        public bool Between { get; init; }

        /// <summary>The powers this card put on enemies, in order
        /// (<see cref="NotePower(string, string, int, string)"/>).</summary>
        public List<PowerApplied> Applied { get; } = new();

        /// <summary>Who a random summon inside this card rolled, in order:
        /// the member id and its printed name (<see cref="NoteSummon"/>).
        /// </summary>
        public List<(string Member, string Name)> Summoned { get; } = new();

        /// <summary>Varka's Oath gains inside this card, in order: the
        /// element, the amount, and "applied", "Swirl" or "" for its source
        /// (<see cref="NoteOath"/>). `FangAscension` marks the card whose
        /// gain made Boreas's Fang add Four Winds' Ascension.</summary>
        public List<(string Element, int Amount, string Source)> Oath { get; } = new();
        public bool FangAscension { get; set; }

        public bool Carried { get; set; }
        public bool Overflowed { get; set; }
    }

    /// <summary>
    /// 2026-10-05, THE SEAT PAGE'S "SINCE LAST PAGE" LINE. One thing that
    /// happened which the page's after-state does not show: a card drawn by
    /// an effect (`drawn`), a debuff an Artifact negated (`negated`), a
    /// base-game enemy power that fired (`triggered`), a stolen card given
    /// back (`returned`); and (seat page 3) an attack that Shattered Frozen
    /// (`shattered`), and the drained HP the curtain call gave back at the
    /// combat's end (`curtain`, its figure in `Amount`). `Seq` rises across
    /// the game process and is seeded off the clock, so a page that
    /// remembers the last one it printed prints only what is new -- across
    /// a restart too.
    /// </summary>
    public readonly record struct PageEvent(string Kind, string Card,
                                            string Target, string Power,
                                            string CombatId, bool OnPlayer,
                                            long Seq, int Amount = 0);

    /// <summary>The event kinds, spelled once (the page reads these words).
    /// </summary>
    public const string Drawn = "drawn";
    public const string Negated = "negated";
    public const string Triggered = "triggered";
    public const string Returned = "returned";
    public const string Shattered = "shattered";
    public const string HpReturned = "curtain";

    private static long _seq =
        System.DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() * 1000;

    /// <summary>The row out-of-play events are filed on, while it is still
    /// the last row; null once a play has opened after it.</summary>
    private static Resolved? _between;

    private static readonly List<Resolved> Rows = new();

    /// <summary>The row hits are being filed against, or null between plays.
    /// The game loop is single threaded and a card resolves whole before the
    /// next one starts, so one open row is the whole of the bookkeeping --
    /// the posture `KokomiPlan`'s Plan receipt takes.</summary>
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
        _between = null;
    }

    /// <summary>Drop everything. Called when a combat opens, so one fight's
    /// resolutions cannot be read as the next one's -- `MeterLedger`'s
    /// `ResetFight` and its reason (`EB-216`).</summary>
    public static void ResetFight()
    {
        Rows.Clear();
        _open = null;
        _between = null;
        _playerTurnEnd = -1;
    }

    /// <summary>
    /// "This happened, and the page's after-state will not show it"
    /// (2026-10-05). Filed on the card that is resolving, or -- outside any
    /// play -- on a <see cref="Resolved.Between"/> row, so the turn's order
    /// is kept. Capped per row like the hits; the cap says so.
    /// </summary>
    public static void NoteEvent(string kind, string card, string target,
                                 string power, string combatId = "",
                                 bool onPlayer = false, int amount = 0)
    {
        if (string.IsNullOrEmpty(kind)) return;
        var row = _open;
        if (row == null)
        {
            if (_between == null || Rows.Count == 0
                || !ReferenceEquals(Rows[^1], _between))
            {
                if (Rows.Count >= MaxRows) return;
                _between = new Resolved(string.Empty, string.Empty, false)
                {
                    Between = true,
                };
                Rows.Add(_between);
            }
            row = _between;
        }
        if (row.Events.Count >= MaxHits)
        {
            row.Overflowed = true;
            return;
        }
        row.Events.Add(new PageEvent(kind, card ?? string.Empty,
                                     target ?? string.Empty,
                                     power ?? string.Empty,
                                     combatId ?? string.Empty, onPlayer,
                                     ++_seq, amount));
    }

    /// <summary>The same note for a body: its printed name, its combat id
    /// and whether it is a player, read without a throw.</summary>
    public static void NoteEvent(string kind, string card, Creature? body,
                                 string power, int amount = 0)
    {
        bool onPlayer;
        try { onPlayer = body?.IsPlayer ?? false; }
        catch (System.Exception) { onPlayer = false; }
        NoteEvent(kind, card, Named(body), power,
                  Safe(() => body?.CombatId.ToString()), onPlayer, amount);
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
        _between = null;
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
    public static void NoteHit(Creature? target, int amount, int blocked,
                               Creature? dealer = null)
    {
        if (_open == null || (amount <= 0 && blocked <= 0)) return;
        if (_open.Hits.Count >= MaxHits)
        {
            _open.Overflowed = true;
            return;
        }
        bool onPlayer;
        try { onPlayer = target?.IsPlayer ?? false; }
        catch (System.Exception) { onPlayer = false; }
        var self = onPlayer
                   && (dealer == null || ReferenceEquals(dealer, target));
        _open.Hits.Add(new Hit(Named(target), amount, blocked,
                               Safe(() => target?.CombatId.ToString()),
                               OnPlayer: onPlayer,
                               Source: onPlayer && !self
                                   ? Named(dealer) : string.Empty,
                               Self: self));
    }

    /// <summary>
    /// "This body died inside the card that is resolving."
    ///
    /// THE KILLING HIT NEVER REACHES <see cref="NoteHit"/>: the base game
    /// skips `AfterDamageReceived` for a creature the hit killed (the kill
    /// gate in `CreatureCmd.Damage`; `docs/current/atlas/
    /// kit-verbs-vs-base-triggers.md`, D5). So a Strike that killed its target
    /// filed no hit, and the page printed "Nothing this page can count landed
    /// off it" under the card that emptied the board. `Hook.AfterDeath` is the
    /// broadcast that does fire, before the corpse is removed, and this is its
    /// mouth: one entry in HIT ORDER, where the killing hit would have been,
    /// carrying the body and no number.
    ///
    /// ENEMIES ONLY, and the caller checks it: a pet or a player dying inside
    /// a play is not a card killing its target. Dropped where no play is open,
    /// <see cref="NoteHit"/>'s rule and its reason.
    /// </summary>
    public static void NoteKill(Creature? target)
    {
        if (target == null) return;
        NoteKill(Named(target), Safe(() => target.CombatId.ToString()));
    }

    /// <summary>The same kill, taking the two facts rather than the game
    /// object -- <see cref="OpenPlay(string, string, bool)"/>'s bargain and
    /// its reason: a dead <c>Creature</c> cannot be built in <c>KleeTests</c>,
    /// and the behaviour worth pinning (the order, the cap, one entry per
    /// body) is this file's. The overload above is the only shipped caller.
    /// </summary>
    public static void NoteKill(string target, string combatId)
    {
        if (_open == null) return;
        if (_open.Hits.Exists(h => h.Killed && h.CombatId == combatId)) return;
        if (_open.Hits.Count >= MaxHits)
        {
            _open.Overflowed = true;
            return;
        }
        _open.Hits.Add(new Hit(target, 0, 0, combatId, Killed: true));
    }

    /// <summary>
    /// "A random summon inside the card that is resolving brought THIS
    /// performer on" (2026-09-25 evening). The section listed Take the Stage,
    /// Understudy and Double Casting with no performer at all, and the seat
    /// had to find the arrival on the stage log. <paramref name="member"/> is
    /// the id (the page translates it; it never reaches a seat) and
    /// <paramref name="name"/> the printed name. Dropped where no play is
    /// open, <see cref="NoteHit"/>'s rule and its reason: a Bow's summon at
    /// the start of her turn is not a card resolving.
    /// </summary>
    public static void NoteSummon(string member, string name)
    {
        if (_open == null || string.IsNullOrEmpty(member)) return;
        if (_open.Summoned.Count >= MaxHits)
        {
            _open.Overflowed = true;
            return;
        }
        _open.Summoned.Add((member, name ?? string.Empty));
    }

    /// <summary>
    /// "This power changed on this enemy, inside the card that is resolving."
    /// ENEMIES ONLY, and the caller checks it: what a card puts on the player
    /// is on the player's own status block. Dropped where no play is open,
    /// <see cref="NoteHit"/>'s rule and its reason: an enemy buffing itself
    /// on its own turn is not a card resolving.
    /// </summary>
    public static void NotePower(Creature? target, string power, int amount)
    {
        if (target == null) return;
        NotePower(Named(target), power, amount,
                  Safe(() => target.CombatId.ToString()));
    }

    /// <summary>The same note, taking the facts rather than the game object,
    /// <see cref="OpenPlay(string, string, bool)"/>'s bargain and its
    /// reason.</summary>
    public static void NotePower(string target, string power, int amount,
                                 string combatId)
    {
        if (_open == null || amount == 0 || string.IsNullOrEmpty(power)) return;
        if (_open.Applied.Count >= MaxHits)
        {
            _open.Overflowed = true;
            return;
        }
        _open.Applied.Add(new PowerApplied(target, power, amount, combatId));
    }

    /// <summary>Where the open row's power list stands, so a placement can
    /// find the entry its own <c>PowerCmd.Apply</c> filed
    /// (<see cref="SizeAppliedSince"/>).</summary>
    public readonly record struct AppliedMark(object? Row, int Count);

    public static AppliedMark MarkApplied() =>
        new(_open, _open?.Applied.Count ?? 0);

    /// <summary>
    /// "What was placed was a Bomb 11, not one Bomb" (2026-10-04; the Opus
    /// seat, 2026-10-02, and the co-op round, 2026-09-27: the play log read
    /// "Put Bomb 1" / "Mine 1" where the card placed Bomb 11 / Mine 3). A Bomb
    /// pile's power Amount is its COUNT, so the hook files a 1 for every
    /// placement, and the charge's size is added only after the apply
    /// returns. The placement calls this once the charge is on the pile: the
    /// last entry filed on <paramref name="target"/> since
    /// <paramref name="mark"/> takes the placed size and the placed kind's
    /// name. Nothing filed since the mark, or another row open, changes
    /// nothing.
    /// </summary>
    public static void SizeAppliedSince(AppliedMark mark, Creature? target,
                                        string power, int size)
    {
        if (target == null) return;
        SizeAppliedSince(mark, Safe(() => target.CombatId.ToString()),
                         power, size);
    }

    /// <summary>The same, taking the combat id rather than the game object,
    /// <see cref="NotePower(string, string, int, string)"/>'s bargain.</summary>
    public static void SizeAppliedSince(AppliedMark mark, string combatId,
                                        string power, int size)
    {
        if (_open == null || !ReferenceEquals(mark.Row, _open)) return;
        for (int i = _open.Applied.Count - 1; i >= mark.Count && i >= 0; i--)
        {
            if (_open.Applied[i].CombatId != combatId) continue;
            _open.Applied[i] = _open.Applied[i] with
            {
                Power = string.IsNullOrEmpty(power) ? _open.Applied[i].Power
                                                    : power,
                Amount = size,
            };
            return;
        }
    }

    /// <summary>
    /// "Varka gained this Oath inside the card that is resolving" (the
    /// rebalance round, 2026-10-03: two seats could not tell where Oath came
    /// from). <paramref name="source"/> is "applied", "Swirl" or "". Dropped
    /// where no play is open, <see cref="NoteHit"/>'s rule and its reason.
    /// </summary>
    public static void NoteOath(string element, int amount, string source)
    {
        if (_open == null || amount <= 0 || string.IsNullOrEmpty(element)) return;
        if (_open.Oath.Count >= MaxHits)
        {
            _open.Overflowed = true;
            return;
        }
        _open.Oath.Add((element, amount, source ?? string.Empty));
    }

    /// <summary>"This card's Oath gain made Boreas's Fang add Four Winds'
    /// Ascension." Dropped where no play is open.</summary>
    public static void NoteFangAscension()
    {
        if (_open != null) _open.FangAscension = true;
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
                    ["killed"] = hit.Killed,
                    ["on_player"] = hit.OnPlayer,
                    ["source"] = hit.Source,
                    ["self"] = hit.Self,
                }),
            ["applied"] = row.Applied.ConvertAll(a =>
                new Dictionary<string, object?>
                {
                    ["target"] = a.Target,
                    ["power"] = a.Power,
                    ["amount"] = a.Amount,
                    ["combat_id"] = a.CombatId,
                }),
            ["summoned"] = row.Summoned.ConvertAll(s =>
                new Dictionary<string, object?>
                {
                    ["member"] = s.Member,
                    ["name"] = s.Name,
                }),
            ["oath"] = row.Oath.ConvertAll(o =>
                new Dictionary<string, object?>
                {
                    ["element"] = o.Element,
                    ["amount"] = o.Amount,
                    ["source"] = o.Source,
                }),
            ["fang_ascension"] = row.FangAscension,
            ["between"] = row.Between,
            ["events"] = row.Events.ConvertAll(e =>
                new Dictionary<string, object?>
                {
                    ["kind"] = e.Kind,
                    ["card"] = e.Card,
                    ["target"] = e.Target,
                    ["power"] = e.Power,
                    ["combat_id"] = e.CombatId,
                    ["on_player"] = e.OnPlayer,
                    ["seq"] = e.Seq,
                    ["amount"] = e.Amount,
                }),
        });
}
