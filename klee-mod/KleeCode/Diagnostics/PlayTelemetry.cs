using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;
using MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;
using KleeMod.Powers;

namespace KleeMod.Diagnostics;

/// <summary>
/// THE HUMAN FEED (Track B). One JSONL fight record per player per fight,
/// written from normal play — including co-op — in the SAME schema
/// `understudy/soak.py` writes for the bot feed. Documented in
/// `understudy/README.md`, "Telemetry schema".
///
/// WHY THIS EXISTS. The bot feed is dense and cheap and dies in Act 1
/// (Understudy debt #3), so every Act 2 and Act 3 cell of Track B's demand
/// curve is empty and stays empty until a HUMAN plays those acts. This is the
/// hook that lets that play count without anyone writing anything down: no UI,
/// no toggle, no export step, on by default, off the shipped path only in the
/// sense that it produces a file nobody has to read.
///
/// WHAT IT IS NOT. It is not balance evidence by itself and not a scorecard;
/// it is a measurement surface that Track B's generator reads
/// (`tools/track_b_curves.py`). Feed labelling is mandatory downstream
/// (Guardrail 7), which is why every record carries `feed` and `source`.
///
/// THE THREE RULES THIS FILE OBEYS, in order of how expensive breaking them is:
///
/// 1. **It never touches game state and never consumes game RNG.** Co-op is
///    deterministic lockstep; a mutation here is a desync at the table, and a
///    desync caused by a *measurement* would be the worst bug this repo has
///    ever shipped. Every method reads and appends to its own dictionaries.
/// 2. **Every entry point is wrapped in try/catch.** An exception thrown from
///    a combat hook lands inside an async continuation and takes the run with
///    it (finding 21's failure mode). Telemetry that can lose a run is worse
///    than no telemetry, so this file fails silent-but-logged, always.
/// 3. **It writes outside the mod directory.** `deploy.ps1` deletes and
///    re-copies `&lt;GameDir&gt;/mods/klee`, so a log written next to the dll — the
///    KleeArt idiom — would be destroyed by the next deploy, which is exactly
///    when the newest data exists. `user://` is the game's own profile root
///    (`%APPDATA%/SlayTheSpire2/`) and survives every redeploy.
/// </summary>
internal static class PlayTelemetry
{
    /// <summary>Schema version of the emitted records. Bump on any BREAKING
    /// change; adding a key is free (understudy/README.md).</summary>
    private const string SchemaVersion = "1";

    /// <summary>`bot` when a harness drives this process (the soak sets the
    /// environment variable for the child it launches), `human` otherwise.
    /// The mod cannot tell a bot from a person by looking, so it is TOLD, and
    /// the default is the one that is true when nobody said anything.</summary>
    private const string FeedEnvVar = "GITS_TELEMETRY_FEED";

    /// <summary>R99/4a — THE ONE-LINE-PER-SESSION DECK INTENT.
    ///
    /// Track B's Fanfare early-half prediction could not be graded because B2
    /// measures cards and every recorded deck was a mixed deck: an archetype
    /// total from a deck that drafted little of that archetype cannot separate
    /// "this archetype produces too little" from "this deck has little of it".
    /// The cheapest fix that exists is to ask the person who knows.
    ///
    /// HOW IT IS DECLARED: one word in
    /// `%APPDATA%/SlayTheSpire2/gits_telemetry/intent.txt` — the directory the
    /// logs already land in, so there is nothing to find and nothing to
    /// create. `GITS_TELEMETRY_INTENT` overrides it, which is how the soak
    /// stamps its committed-draft arm without touching a file the human owns.
    /// The override is by PRESENCE, not by content: a variable that is set but
    /// EMPTY declares nothing and the file is NOT consulted, because a harness
    /// that says "no intent" must not inherit a person's standing declaration.
    ///
    /// READ ONCE PER SESSION, deliberately. A declaration is a statement about
    /// the run you are about to play; re-reading it mid-session would let one
    /// run's records disagree with each other about what they were. Absent
    /// file, empty file, unreadable file: the intent is `""`, which is exactly
    /// what "nobody declared anything" should look like in a column.</summary>
    private const string IntentEnvVar = "GITS_TELEMETRY_INTENT";

    private const string IntentFile = "intent.txt";

    private static readonly Regex IntentLabel =
        new(@"^(\d+)(?:\s*[x×]\s*(\d+))?$", RegexOptions.Compiled);

    private static readonly Regex BbCode = new(@"\[/?[^\]]*\]", RegexOptions.Compiled);

    private static string? _path;
    private static string? _session;
    private static string? _intent;
    private static bool _writeFailed;
    private static readonly Dictionary<Player, FightRecord> Open = new();

    /// <summary>EB-18 — RUN LINKAGE. The run's own string seed, which is the
    /// same token `RunHistoryUtilities.CreateRunHistoryEntry` writes as `seed`
    /// in the `.run` history file `tier1/analyze.py` already reads. That is the
    /// join to the run history, and per-fight granularity stops being a
    /// separate island.
    ///
    /// A SEED IS NOT A RUN, which is what the first cut of this got wrong. It
    /// restarted `fight_index` when the run ID CHANGED, on the reasoning that
    /// two runs in a session have different seeds. Replaying a seed is a
    /// first-class arm (P1.5 / R104), so that reasoning is false in ordinary
    /// use: playing seed X twice in one session produced one `run_id` with
    /// fights numbered 0,1,2,6,7,8 and no gap a reader could see, and the
    /// tier1 join folded the two runs into one.
    ///
    /// THE NEW-RUN SIGNAL IS THE RUN OBJECT ITSELF. `RunManager.State` is
    /// assigned exactly once per run — `SetUpNew*`/`SetUpSaved*` throw
    /// `InvalidOperationException` if it is already set — and nulled in
    /// `CleanUp`, so a second embark is necessarily a DIFFERENT `RunState`
    /// instance. Reference identity against the state we last saw is therefore
    /// the game's own answer to "is this the same run", not a heuristic built
    /// out of floors or characters, and it costs no subscription: the
    /// alternative signal, `RunManager.RunStarted`, is an event, and an
    /// exception from a handler on it lands inside `Launch()` and takes the run
    /// with it (rule 2). Held weakly so a finished run is not kept alive by its
    /// own telemetry.
    ///
    /// `run_instance` is what a READER gets: `&lt;session stamp&gt;#&lt;ordinal&gt;`,
    /// minted once per run seen, sharing the stamp with this session's log file
    /// name. `run_id` + `run_instance` is unique where `run_id` alone is not.
    ///
    /// `fight_index` counts fights WITHIN a run instance, from 0, in the order
    /// this process saw them. A run RESUMED in a later session is a fresh
    /// `RunState` and so numbers from zero again under a new instance token —
    /// a gap a reader can see (floor jumps) beats a number that silently
    /// continues across a boundary it cannot see.</summary>
    private static WeakReference<RunState>? _run;

    private static string _runInstance = string.Empty;

    private static int _runOrdinal;

    private static int _fightIndex;

    /// <summary>Notes which run we are in, and starts a new instance — new
    /// token, fight numbering back to zero — the first time a given
    /// <see cref="RunState"/> is seen.</summary>
    private static void NoteRun(RunState run)
    {
        if (_run != null && _run.TryGetTarget(out var seen) && ReferenceEquals(seen, run))
        {
            return;
        }

        _run = new WeakReference<RunState>(run);
        _runInstance = $"{Session()}#{_runOrdinal++}";
        _fightIndex = 0;
    }

    // -------------------------------------------------------------- open ---

    /// <summary>Opens one record per seat. Any record still open from a
    /// previous fight is flushed as `interrupted` rather than dropped: an
    /// abandoned run and a crash both look like this, and a half fight is
    /// still a demand-curve sample for the turns it did record.</summary>
    internal static void OpenFight()
    {
        try
        {
            // A won fight still waiting for its HP after the end-of-combat
            // effects is written now, unread: the combat-won signal never
            // came (`FinishReturns`).
            FinishReturns(read: false);
            EnsureReturnWatch();
            FlushAll("interrupted");
            Pending.Clear();
            var run = RunManager.Instance?.DebugOnlyGetState();
            var combat = CombatManager.Instance?.DebugOnlyGetState();
            if (run == null || combat == null) return;

            // AN EVENT IS NOT A FIGHT. Punch Off builds an NCombatRoom in
            // VisualOnly mode to animate two creatures hitting each other; it
            // has no intents, no reward and no demand. A record from one would
            // be a floor-N "fight" with zero incoming, which is exactly the
            // shape that quietly drags a median down.
            if (run.CurrentRoom is not CombatRoom room) return;
            var kind = room.RoomType.ToString().ToLowerInvariant();

            var runId = RunId(run);
            NoteRun(run);
            var runInstance = _runInstance;
            var fightIndex = _fightIndex++;
            var encounter = EncounterId(room, combat);
            var enemies = combat.Enemies
                .Where(e => e.IsAlive)
                .Select(e => (Name: NameOf(e), MaxHp: (int)e.MaxHp))
                .ToList();

            var players = run.Players;
            for (var slot = 0; slot < players.Count; slot++)
            {
                var player = players[slot];
                var creature = player.Creature;
                if (creature == null) continue;
                Open[player] = new FightRecord
                {
                    RunId = runId,
                    RunInstance = runInstance,
                    FightIndex = fightIndex,
                    Encounter = encounter,
                    Act = run.CurrentActIndex + 1,
                    Floor = run.TotalFloor,
                    Kind = kind,
                    Seats = players.Count,
                    SeatIndex = slot,
                    Character = SafeTitle(player),
                    Enemies = enemies,
                    HpStart = (int)creature.CurrentHp,
                    MaxHp = (int)creature.MaxHp,
                };
                SeedOpeningBlock(player, (int)creature.Block, combat.RoundNumber);
            }
        }
        catch (Exception e)
        {
            Warn("OpenFight", e);
        }
    }

    // -------------------------------------------------------------- turn ---

    /// <summary>
    /// THE BLOCK GAP (the Furina Spend round 2, 2026-10-10: "In 16 of 67
    /// fights her first turn faced incoming damage and she gained no Block.
    /// The control: 2 of 22."). After her draw, for every seat: did a turn
    /// open with a Block-gaining card in hand (<c>CardModel.GainsBlock</c>)
    /// while the enemies telegraphed attack damage? The round is kept; the
    /// writer counts those turns (`block_card_turns`) and the ones that
    /// gained no Block (`block_card_turns_no_block`). Every character, so
    /// the control reads the same number. A read (rule 1).
    /// </summary>
    internal static void BlockCardTurn(Player player)
    {
        try
        {
            var combat = CombatManager.Instance?.DebugOnlyGetState();
            if (combat == null || !Open.ContainsKey(player)) return;
            var hand = CardPile.Get(PileType.Hand, player)?.Cards;
            var blockCard = hand != null && hand.Any(c => c.GainsBlock);
            var (telegraphed, _) = Telegraphed(combat);
            RecordBlockCardTurn(player, combat.RoundNumber, blockCard,
                                telegraphed);
        }
        catch (Exception e)
        {
            Warn("BlockCardTurn", e);
        }
    }

    /// <summary>The hook-free half of <see cref="BlockCardTurn"/>, and the
    /// test seam.</summary>
    internal static void RecordBlockCardTurn(Player player, int round,
                                             bool blockCardInHand,
                                             int incoming)
    {
        if (!blockCardInHand || incoming <= 0) return;
        if (!Open.TryGetValue(player, out var record)) return;
        record.BlockCardRounds.Add(round);
    }

    /// <summary>The turn-opening sample: HP, block, the telegraph BEFORE
    /// block and the enemy HP pool. The pool is what makes an
    /// output curve possible without trusting attribution — per-turn damage is
    /// the pool's own drop, which cannot under-count the way crediting a card
    /// can.</summary>
    internal static void OpenTurn()
    {
        try
        {
            var combat = CombatManager.Instance?.DebugOnlyGetState();
            if (combat == null || Open.Count == 0) return;
            var round = combat.RoundNumber;
            var pool = EnemyPool(combat);
            var hp = EnemyHp(combat);
            var (telegraphed, attackers) = Telegraphed(combat);

            foreach (var (player, record) in Open)
            {
                var creature = player.Creature;
                if (creature == null) continue;
                record.Turns = Math.Max(record.Turns, round);
                record.HpLastSeen = (int)creature.CurrentHp;
                record.HpTrajectory.Add(new[]
                    { round, (int)creature.CurrentHp, (int)creature.Block });
                record.IncomingByTurn.Add(new[] { round, telegraphed, attackers });
                record.EnemyPoolByTurn.Add(new[] { round, pool });
                record.EnemyHpByTurn.Add(new[] { round, hp });
                NoteFanfareTurnStart(record, creature, round);
                // REACTIONS RIDE ALONG, because the counter already exists and
                // sampling it costs one read (the hand-back's "cheap now"
                // condition). Measurement only: no reaction constant is
                // touched by this file.
                //
                // EB-156: this used to sample `ReactionEffects.TotalResolved`,
                // which is GLOBAL -- deliberately so, and sealed as a RULING
                // (red-pen 2026-07-26 R1: in co-op your partner's Overload
                // satisfies your Chevreuse). Sampling it into a PER-SEAT row
                // was the error, not the counter: both seats' reactions landed
                // in every seat's row, and a reader dividing by that seat's
                // turns or cards used the wrong denominator.
                // `ResolvedThisCombat` is the per-seat counter, keyed the way
                // BombPower's detonation totals next door are. A dealer-less
                // reaction belongs to no seat, so the seats' own numbers sum
                // to at most the team-wide one, never more.
                var mine = ReactionEffects.ResolvedThisCombat(combat, player);
                if (record.ReactionsAtStart < 0)
                {
                    record.ReactionsAtStart = mine;
                }

                // A RUNNING TOTAL since combat start, not this turn's count:
                // a reader takes the last entry (or `reactions_by_type`),
                // never a sum of entries.
                record.ReactionsByTurn.Add(new[]
                    { round, mine - record.ReactionsAtStart });
            }

            SampleDetonations(combat);
        }
        catch (Exception e)
        {
            Warn("OpenTurn", e);
        }
    }

    /// <summary>
    /// EB-18 — the bomb counters, sampled rather than hooked.
    ///
    /// <see cref="BombPower"/> already keeps a per-combat, PER-PLAYER
    /// detonation total (the co-op ownership fix, EPOCH 2 / D2) and now a
    /// corpse-detonation total beside it. Both are monotonic within a combat,
    /// so reading them at each turn boundary and at combat end — taking the
    /// MAX, never the last value — costs two dictionary lookups per seat and
    /// cannot go backwards if a stale-flush reads a record after the next
    /// combat has already reset the counters.
    ///
    /// Sampling, not a hook, on purpose: a listener on the detonation bus
    /// would put telemetry inside the damage path of a lockstep co-op game for
    /// a number that is fully recoverable from outside it.
    /// </summary>
    private static void SampleDetonations(ICombatState combat)
    {
        foreach (var (player, record) in Open)
        {
            // 2026-10-02: the Klee arm's Bombs and Mines are `ProtoBombPower`,
            // which never touched `BombPower`'s counter, so a whole Klee run
            // read 0. Both powers count now; a seat only ever holds one.
            record.Detonations = Math.Max(
                record.Detonations,
                BombPower.DetonationsThisCombat(combat, player)
                + ProtoBombPower.ExplosionsThisCombat(combat, player));
            record.MineDetonations = Math.Max(
                record.MineDetonations,
                ProtoBombPower.MineExplosionsThisCombat(combat, player));
            // 2026-10-08. What the charges did and what set the Mines off.
            record.BombReactions = Math.Max(
                record.BombReactions,
                ProtoBombPower.ReactingExplosionsThisCombat(combat, player));
            record.MineDetonationsByAttack = Math.Max(
                record.MineDetonationsByAttack,
                ProtoBombPower.AttackMineExplosionsThisCombat(combat, player));
            record.CorpseDetonations = Math.Max(
                record.CorpseDetonations,
                BombPower.CorpseDetonationsThisCombat(combat, player));
            // 2026-10-06. The reaction tallies, sampled on the same rule: per
            // key, the MAX of what was held and what the counter reads, so a
            // stale-flush that reads after the next combat reset them (they
            // read empty then) cannot take a number back.
            MaxInto(record.ReactionsByType,
                    ReactionTally.TypesFor(combat, player));
            MaxInto(record.DebuffsFromReactions,
                    ReactionTally.DebuffsFor(combat, player));
            foreach (var (key, value) in ReactionTally.AmpBonusFor(combat, player))
            {
                record.AmpBonusDamage[key] = record.AmpBonusDamage.TryGetValue(
                    key, out var held) ? Math.Max(held, value) : value;
            }
        }
    }

    private static void MaxInto(Dictionary<string, int> into,
                                IReadOnlyDictionary<string, int> from)
    {
        foreach (var (key, value) in from)
        {
            into[key] = into.TryGetValue(key, out var held)
                ? Math.Max(held, value) : value;
        }
    }

    /// <summary>Block standing at the END of the player's turn — the number an
    /// output curve wants. Block read at the turn OPENING is whatever survived
    /// the enemy turn, which is a different quantity wearing the same word.
    /// </summary>
    internal static void CloseTurn()
    {
        try
        {
            var combat = CombatManager.Instance?.DebugOnlyGetState();
            if (combat == null) return;
            RecordTurnEnd(combat.RoundNumber);
            SampleDetonations(combat);
            MaybeClose(combat);
        }
        catch (Exception e)
        {
            Warn("CloseTurn", e);
        }
    }

    /// <summary>The hook-free half of <see cref="CloseTurn"/>, and the test
    /// seam: one turn-end row per open seat.
    ///
    /// 2026-10-05 — STRENGTH BY TURN. The seat's Strength standing at the end
    /// of its turn, 0 with none, read off the base game's own
    /// <c>StrengthPower</c> so it means the same thing for the base five and
    /// every kit character. Negative when Strength is down. A read, never a
    /// write (rule 1).</summary>
    internal static void RecordTurnEnd(int round)
    {
        foreach (var (player, record) in Open)
        {
            var creature = player.Creature;
            if (creature == null) continue;
            record.BlockAtTurnEnd.Add(new[] { round, (int)creature.Block });
            record.StrengthByTurn.Add(new[]
            {
                round,
                creature.GetPowerAmount<MegaCrit.Sts2.Core.Models.Powers.StrengthPower>(),
            });
            record.HpLastSeen = (int)creature.CurrentHp;
            NoteStage(record, creature);
        }
    }

    /// <summary>
    /// The Furina full-run round (2026-10-10): her Fanfare as each of her
    /// turns opens, so a banking claim (Prima Donna, saving for a Spend) can
    /// be checked turn by turn. Furina only: a seat with no stage ledger
    /// writes no row. A read; <c>Peek</c> creates no ledger (rule 1).
    /// </summary>
    private static void NoteFanfareTurnStart(FightRecord record,
                                             Creature creature, int round)
    {
        try
        {
            var ledger = FurinaStageLedger.Peek(creature);
            if (ledger == null) return;
            record.Stage = ledger;
            record.FanfareTurnStart.Add(new[] { round, ledger.Fanfare });
        }
        catch (Exception e)
        {
            Warn("NoteFanfareTurnStart", e);
        }
    }

    /// <summary>
    /// THE SPEND ROUND (2026-10-10, "Next round: telemetry first"): Furina's
    /// Fanfare record for this fight, read off her stage ledger -- the peak,
    /// the bank at the close (the fight's end, or her death), and every Spend
    /// with the bank before it (<see cref="FurinaStageLedger.Spends"/>). The
    /// ledger is held from the first reading on, so a fight closed after its
    /// combat is gone (the stale-flush) still writes it. A read; `Peek`
    /// creates no ledger (rule 1).
    /// </summary>
    private static void NoteStage(FightRecord record, Creature? creature)
    {
        try
        {
            if (creature == null) return;
            var ledger = FurinaStageLedger.Peek(creature);
            if (ledger != null) record.Stage = ledger;
            if (record.Stage != null) record.FanfareEnd = record.Stage.Fanfare;
        }
        catch (Exception e)
        {
            Warn("NoteStage", e);
        }
    }

    // ------------------------------------------------------------ events ---

    /// <summary>Varka's current element as a word for a `cards_played` row,
    /// or null for anyone else (whose rows keep their two columns).</summary>
    internal static string? VarkaElementWord(Creature? creature)
    {
        try
        {
            return creature != null && VarkaOath.Live(creature)
                ? VarkaOath.Current(creature).ToString() : null;
        }
        catch (Exception)
        {
            return null;
        }
    }

    internal static void CardPlayed(CardPlay cardPlay)
    {
        try
        {
            var owner = cardPlay?.Card?.Owner;
            if (owner == null || !Open.TryGetValue(owner, out var record)) return;
            if (!cardPlay!.IsFirstInSeries) return;      // one row per PLAY
            var round = CombatManager.Instance?.DebugOnlyGetState()?.RoundNumber ?? 0;
            record.CardsPlayed.Add((round, CardName(cardPlay.Card),
                                    VarkaElementWord(owner.Creature)));
        }
        catch (Exception e)
        {
            Warn("CardPlayed", e);
        }
    }

    /// <summary>
    /// EB-14 — ONE SELECTOR ANSWER, WITH THE LIST IT WAS CHOSEN FROM.
    ///
    /// Called by <see cref="SelectionTelemetry"/>, which owns the Harmony
    /// patches on the selection screens; this file stays patch-free (pinned by
    /// `test_track_b_curves.py`, which will not let a Harmony patch appear on
    /// the combat lifecycle here without arguing for itself).
    ///
    /// THE ROW IS THE BOT FEED'S ROW, COLUMN FOR COLUMN:
    /// `[round, screen, index, chosen, [offered…]]` (`understudy/soak.py`
    /// `_selector_row`). Three of those columns are decided here, and each was
    /// a way to get it wrong:
    ///
    ///   * ROUND is the fight's own turn counter, not `combat.RoundNumber`.
    ///     A selector is an overlay standing on the round that opened it, and
    ///     the soak reads `fight.turns` for exactly the same reason.
    ///   * INDEX is found by REFERENCE against the offered list, never by
    ///     name. Two Strikes in a pile are two different cards, and matching
    ///     on the printed title would point the row at whichever came first.
    ///   * SEAT is the offered cards' `Owner`, which is the game's own idiom
    ///     here (`CardSelectCmd` itself does `cards[0].Owner`). A row lands
    ///     only if that player has a fight record open — the same scoping the
    ///     bot feed uses, because a selector outside a fight belongs to no
    ///     fight.
    /// </summary>
    internal static void SelectorAnswered(string screen,
                                          IReadOnlyList<CardModel> offered,
                                          IReadOnlyList<CardModel> chosen)
    {
        try
        {
            if (offered.Count == 0 || chosen.Count == 0) return;
            var owner = offered[0].Owner;
            if (owner == null || !Open.TryGetValue(owner, out var record)) return;

            var offeredNames = offered.Select(CardName).ToList();
            foreach (var card in chosen)
            {
                var index = -1;
                for (var i = 0; i < offered.Count; i++)
                {
                    if (!ReferenceEquals(offered[i], card)) continue;
                    index = i;
                    break;
                }

                // `-1` already MEANS "resolved without naming an option" (a
                // confirm, a skip) on this column. Reaching it HERE means
                // something else: the chosen card was not reference-equal to
                // anything in the recorded offer, i.e. the instrument's own
                // identity assumption failed. Same value, different fact, so
                // say so in the log rather than letting it read as a skip.
                if (index < 0)
                {
                    Log.Warn($"[{KleeMod.ModId}] play telemetry selector on "
                           + $"'{screen}': chosen card '{CardName(card)}' is "
                           + "not in the recorded offer; row written with "
                           + "index -1, which on this column also means "
                           + "'no option named'.");
                }

                record.Selectors.Add(
                    (record.Turns, screen, index, CardName(card), offeredNames));
            }
        }
        catch (Exception e)
        {
            Warn("SelectorAnswered", e);
        }
    }

    /// <summary>
    /// EB-118 — ONE RESOLVED EXHAUST SELECTION, in the sim's row shape.
    ///
    /// The row itself is rendered by <see cref="Powers.ExhaustSelection"/>,
    /// which owns the column names; this file only decides WHICH FIGHT it
    /// belongs to. That split is the point: the sim's twin row
    /// (`tier0/engine/effects.py` `exhaust_selection_row`) is compared against
    /// the C# column literals by a parity test, and a serializer that also
    /// held a copy of the names would give it two places to disagree.
    ///
    /// A selection resolved outside a fight record — a seat with no open
    /// fight — is DROPPED rather than filed under a fight it did not happen
    /// in, the same scoping <see cref="SelectorAnswered"/> uses.
    ///
    /// Additive at this schema version (understudy/README.md): a reader that
    /// does not know `exhaust_selections` sees a key it can ignore.
    /// </summary>
    internal static void ExhaustSelectionResolved(Player? seat, string row)
    {
        try
        {
            if (seat == null || !Open.TryGetValue(seat, out var record)) return;
            record.ExhaustSelections.Add(row);
        }
        catch (Exception e)
        {
            Warn("ExhaustSelectionResolved", e);
        }
    }

    /// <summary>
    /// Damage, from the hook rather than from a state diff — which makes this
    /// feed's attribution STRICTLY better than the bot feed's, and the
    /// difference is labelled rather than averaged away. The wire-driven soak
    /// credits a card with the enemy HP drop it happens to see next; here the
    /// game hands us the dealer, the card and the unblocked amount.
    /// </summary>
    internal static void Damage(Creature target, DamageResult result,
                                Creature? dealer, CardModel? cardSource)
    {
        try
        {
            if (!RecordDamage(target, (int)result.UnblockedDamage,
                              (int)result.BlockedDamage, dealer, cardSource))
            {
                return;
            }

            // A KILLING BLOW ENDS THE FIGHT, and it has to end the record with
            // it. The first run-verification recorded every won fight as
            // `interrupted`, closed by the NEXT fight's stale-flush -- so the
            // HP ledger swallowed whatever happened in between (a campfire, an
            // event, a potion) and reported it as damage taken in a fight that
            // was already over. The combat-end hook (R100/5) is the backstop.
            var combat = CombatManager.Instance?.DebugOnlyGetState();
            if (combat != null) MaybeClose(combat);
        }
        catch (Exception e)
        {
            Warn("Damage", e);
        }
    }

    /// <summary>
    /// 2026-10-02 — WHO A HIT BELONGS TO, and what kind of hit it was.
    ///
    /// The co-op fact-check found the credited damage covered 36% of the
    /// enemies' HP plus Block (29% in bosses), because a hit counted only
    /// when the engine named the seat's own creature as the dealer. In order:
    ///
    ///   1. a PET dealer (<c>PetOwner</c> set) is its owner's `pet` damage;
    ///   2. the seat's own creature as dealer is `direct`, as it always was;
    ///   3. otherwise the innermost <see cref="DamageCredit"/> scope names the
    ///      seat and the kind: `element`, `reaction`, `bomb`, `pet`, `power`.
    ///
    /// The source key is the card when the game hands one over, else the
    /// scope's label in parentheses ("(Bomb)", "(Overload)", "(Bake-Kurage)"),
    /// else `(uncredited)` as before. Measurement only: nothing here is read
    /// back by the game.
    /// </summary>
    internal static (Player? Owner, string Kind, string Source) Credit(
        Creature? dealer, CardModel? cardSource)
    {
        var card = cardSource != null ? CardName(cardSource) : null;
        if (dealer?.PetOwner is { } master)
        {
            var frame = DamageCredit.Current;
            var label = frame?.Kind == DamageCredit.Pet ? frame.Label ?? "pet" : "pet";
            return (master, DamageCredit.Pet, card ?? "(" + label + ")");
        }

        if (dealer?.Player is { } own)
        {
            return (own, DamageCredit.Direct, card ?? "(uncredited)");
        }

        if (DamageCredit.Current is { Owner: { } owner } scope)
        {
            return (owner, scope.Kind, card ?? "(" + (scope.Label ?? scope.Kind) + ")");
        }

        return (null, string.Empty, string.Empty);
    }

    /// <summary>The hook-free half of <see cref="Damage"/>, and the test
    /// seam: files one hit and answers whether it could have ended the fight.
    /// </summary>
    internal static bool RecordDamage(Creature? target, int unblocked, int blocked,
                                      Creature? dealer, CardModel? cardSource)
    {
        // This hit reached its `AfterDamageReceived`, so the snapshot its
        // `BeforeDamageReceived` took is spent (see `NoteBeforeDamage`).
        if (target != null) PopPending(target);
        if (unblocked <= 0 && blocked <= 0) return false;

        if (target?.Player is { } victim)
        {
            if (unblocked <= 0 || !Open.TryGetValue(victim, out var taken)) return false;
            taken.DamageTaken += unblocked;
            return target.IsDead;
        }

        var (owner, kind, source) = Credit(dealer, cardSource);
        if (owner == null || !Open.TryGetValue(owner, out var dealt)) return false;
        FileHit(dealt, kind, source, unblocked, blocked);
        return unblocked > 0;
    }

    private static void FileHit(FightRecord record, string kind, string source,
                             int unblocked, int blocked)
    {
        if (unblocked > 0)
        {
            record.DamageBySource.TryGetValue(source, out var running);
            record.DamageBySource[source] = running + unblocked;
            record.DamageByKind.TryGetValue(kind, out var byKind);
            record.DamageByKind[kind] = byKind + unblocked;
        }

        record.DamageBlocked += Math.Max(0, blocked);
    }

    // ---------------------------------------------------- killing blows ---

    /// <summary>One hit in flight: who it credits, and what stood in front of
    /// it when it started.</summary>
    private readonly record struct PendingHit(
        Player? Owner, string Kind, string Source, Player? Victim, int Hp, int Block);

    private static readonly Dictionary<Creature, List<PendingHit>> Pending = new();

    /// <summary>
    /// THE KILLING HIT, which <see cref="Damage"/> never sees:
    /// <c>CreatureCmd.Damage</c> skips <c>AfterDamageReceived</c> for a
    /// creature the hit killed (<c>PlayTelemetryHooks.AfterDeath</c> and
    /// <c>ResolutionLedger.NoteKill</c> say the same). So the last hit on every
    /// enemy was credited to nobody. The snapshot is taken here, before the
    /// hit, under the same credit rules; <see cref="RecordDamage"/> drops it
    /// when the hit lands on a survivor, and <see cref="RecordDeath"/> files it
    /// when the target died instead: the HP it had is the HP the hit took, and
    /// the Block it had is what the hit broke. A STACK per target, because a
    /// hit's own broadcast can start a nested hit on the same body.
    /// </summary>
    internal static void NoteBeforeDamage(Creature target, Creature? dealer,
                                          CardModel? cardSource)
    {
        try
        {
            if (Open.Count == 0 || target == null) return;
            var hp = Math.Max(0, (int)target.CurrentHp);
            var block = Math.Max(0, (int)target.Block);
            PendingHit hit;
            if (target.Player is { } victim)
            {
                if (!Open.ContainsKey(victim)) return;
                hit = new PendingHit(null, string.Empty, string.Empty, victim, hp, block);
            }
            else
            {
                var (owner, kind, source) = Credit(dealer, cardSource);
                if (owner == null || !Open.ContainsKey(owner)) return;
                hit = new PendingHit(owner, kind, source, null, hp, block);
            }

            if (!Pending.TryGetValue(target, out var stack))
            {
                stack = new List<PendingHit>();
                Pending[target] = stack;
            }

            stack.Add(hit);
        }
        catch (Exception e)
        {
            Warn("NoteBeforeDamage", e);
        }
    }

    /// <summary>A death the game prevented: the hit did not kill.</summary>
    internal static void DropPending(Creature creature)
    {
        try
        {
            if (creature != null) Pending.Remove(creature);
        }
        catch (Exception e)
        {
            Warn("DropPending", e);
        }
    }

    private static PendingHit? PopPending(Creature target)
    {
        if (!Pending.TryGetValue(target, out var stack) || stack.Count == 0) return null;
        var top = stack[stack.Count - 1];
        stack.RemoveAt(stack.Count - 1);
        if (stack.Count == 0) Pending.Remove(target);
        return top;
    }

    /// <summary>A creature died. If a hit was in flight on it, that hit
    /// killed it: file the HP it took and the Block it broke.</summary>
    internal static void RecordDeath(Creature creature)
    {
        try
        {
            if (creature == null || PopPending(creature) is not { } hit) return;
            Pending.Remove(creature);
            if (hit.Victim != null)
            {
                if (Open.TryGetValue(hit.Victim, out var taken)) taken.DamageTaken += hit.Hp;
                return;
            }

            if (hit.Owner == null || !Open.TryGetValue(hit.Owner, out var dealt)) return;
            FileHit(dealt, hit.Kind, hit.Source, hit.Hp, hit.Block);
            dealt.KillingBlows++;
        }
        catch (Exception e)
        {
            Warn("RecordDeath", e);
        }
    }

    // ------------------------------------------------------------- block ---

    /// <summary>
    /// 2026-10-02 — BLOCK GAINED, per seat per round. `block_at_turn_end` is
    /// what was STANDING, which hides every point the enemy already broke and
    /// every point gained on the enemy's turn. Credited to the seat whose
    /// creature received it; Block a card put on someone else's creature is
    /// also counted against the card's owner as `block_given`.
    /// </summary>
    internal static void BlockGained(Creature creature, decimal amount,
                                     CardModel? cardSource)
    {
        try
        {
            if (Open.Count == 0) return;
            var round = CombatManager.Instance?.DebugOnlyGetState()?.RoundNumber ?? 0;
            RecordBlock(creature, (int)amount, cardSource?.Owner, round);
        }
        catch (Exception e)
        {
            Warn("BlockGained", e);
        }
    }

    /// <summary>The hook-free half of <see cref="BlockGained"/>, and the
    /// test seam.</summary>
    internal static void RecordBlock(Creature? creature, int amount, Player? giver,
                                     int round)
    {
        if (amount <= 0 || creature?.Player is not { } receiver) return;
        if (Open.TryGetValue(receiver, out var record))
        {
            record.BlockGained.TryGetValue(round, out var running);
            record.BlockGained[round] = running + amount;
        }

        if (giver != null && !ReferenceEquals(giver, receiver)
            && Open.TryGetValue(giver, out var given))
        {
            given.BlockGiven += amount;
        }
    }

    /// <summary>
    /// 2026-10-05 — BLOCK GAINED BEFORE THE RECORD OPENED. The run's own
    /// listeners (relics) walk <c>BeforeCombatStart</c> ahead of this mod's
    /// combat-state listeners, so Anchor's 10 Block (any character's) arrived
    /// at <see cref="BlockGained"/> with no record open and was dropped: base
    /// seats' fights read `block_gained: 0` under a turn-1 `hp_trajectory`
    /// showing 10 Block standing. Block cannot carry between combats
    /// (<c>Player.AfterCombatEnd</c> empties it, and turn 1 does not clear),
    /// so whatever stands when the record opens was gained this fight, and is
    /// filed to round 1. A read, never a write (rule 1).
    /// </summary>
    internal static void SeedOpeningBlock(Player player, int block, int round)
    {
        if (block <= 0 || !Open.TryGetValue(player, out var record)) return;
        var at = Math.Max(1, round);
        record.BlockGained.TryGetValue(at, out var running);
        record.BlockGained[at] = running + block;
    }

    // ------------------------------------------------------ test seams ---

    /// <summary>Test seam: open a bare record for one seat, with no run and no
    /// combat. The mod never calls it.</summary>
    internal static void OpenSeatForTest(Player player, int seats, int seatIndex)
    {
        Open[player] = new FightRecord { Seats = seats, SeatIndex = seatIndex };
    }

    /// <summary>Test seam: the turn-opening Fanfare row for every open seat,
    /// with no combat. The mod never calls it.</summary>
    internal static void RecordTurnStartForTest(int round)
    {
        foreach (var (player, record) in Open)
        {
            if (player.Creature is { } creature)
            {
                NoteFanfareTurnStart(record, creature, round);
            }
        }
    }

    /// <summary>Test seam: the JSON a seat's open record would write.</summary>
    internal static string? JsonForTest(Player player) =>
        Open.TryGetValue(player, out var record) ? record.ToJson() : null;

    /// <summary>Test seam: forget every open record. The mod never calls it.</summary>
    internal static void ResetForTest()
    {
        Open.Clear();
        Pending.Clear();
        AwaitingReturn.Clear();
        _returnWatch = false;
    }

    /// <summary>Test seam: hold won fights for the combat-won signal, as the
    /// game does once <see cref="EnsureReturnWatch"/> has subscribed.
    /// </summary>
    internal static void ArmReturnWatchForTest(bool armed) =>
        _returnWatch = armed;

    /// <summary>Test seam: the won fights waiting for their HP.</summary>
    internal static int AwaitingReturnForTest() => AwaitingReturn.Count;

    // ------------------------------------------------- after the return ---

    /// <summary>
    /// THE SPEND ROUND (2026-10-10): "Telemetry stamps HP before the curtain
    /// call returns drained HP (`PlayTelemetry.cs:1005`). Lane 4's act-1
    /// normals: telemetry 23 lost, records 4." `hp_end` is the last in-fight
    /// reading, and stays so (comparability, and the campfire reason in
    /// <see cref="FlushAll"/>). `hp_after_return` is the HP once every
    /// end-of-combat effect has run -- Furina's curtain call
    /// (<c>AfterCombatEnd</c>), Burning Blood and its kin
    /// (<c>AfterCombatVictory</c>) -- for every character.
    ///
    /// WHERE IT IS READ. Those effects run inside
    /// <c>CombatManager.EndCombatInternal</c>, in hook order this listener does
    /// not control, and the game raises <c>CombatManager.CombatWon</c> after
    /// all of them. So a won fight is HELD here when it closes and written
    /// when that event comes, with the HP then. A held fight that never
    /// hears it (the next fight opened first) is written with
    /// `hp_after_return` -1: not read. A death, an interrupted fight and a
    /// fight closed before the watch is armed are written at once, the
    /// field equal to `hp_end` (no end-of-combat effect ran).
    /// </summary>
    private static readonly List<(Player Player, FightRecord Record)>
        AwaitingReturn = new();

    private static bool _returnWatch;

    private static CombatManager? _watched;

    /// <summary>Subscribe once to the combat-won signal (again if the
    /// manager is ever replaced). An event handler cannot throw into the
    /// game: <see cref="OnCombatWon"/> catches everything (rule 2).</summary>
    private static void EnsureReturnWatch()
    {
        var manager = CombatManager.Instance;
        if (manager == null || ReferenceEquals(_watched, manager)) return;
        if (_watched != null) _watched.CombatWon -= OnCombatWon;
        manager.CombatWon += OnCombatWon;
        _watched = manager;
        _returnWatch = true;
    }

    private static void OnCombatWon(CombatRoom room)
    {
        try
        {
            FinishReturns(read: true);
        }
        catch (Exception e)
        {
            Warn("CombatWon", e);
        }
    }

    /// <summary>Write every held fight: with the seat's HP now when
    /// <paramref name="read"/>, else -1. The test seam too.</summary>
    internal static void FinishReturns(bool read)
    {
        if (AwaitingReturn.Count == 0) return;
        var waiting = AwaitingReturn.ToList();
        AwaitingReturn.Clear();
        foreach (var (player, record) in waiting)
        {
            var creature = player.Creature;
            record.HpAfterReturn = read && creature != null
                ? Math.Max(0, (int)creature.CurrentHp)
                : -1;
            Write(record);
        }
    }

    // ------------------------------------------------------------- close ---

    /// <summary>
    /// R100/5 — THE COMBAT-END SEAM, and it is a first-party hook.
    ///
    /// The previous record said "the game exposes no first-party combat-END
    /// hook". That was wrong about the game (the consequence it described —
    /// won fights reading `interrupted` — was real). Verified against a local
    /// decompile of the shipped `sts2.dll` rather than assumed:
    ///
    ///   CombatManager.EndCombatInternal()
    ///     -> await Hook.AfterCombatEnd(runState, combatState, room)
    ///     -> ... -> await Hook.AfterCombatVictory(runState, combatState, room)
    ///
    /// and both walk `runState.IterateHookListeners(combatState)` — the same
    /// iteration that already delivers `BeforeCombatStart` to this listener.
    /// So the outcome label costs two `AbstractModel` overrides and NO Harmony
    /// patch: no new patch surface on the combat lifecycle of a deterministic
    /// lockstep game, which is a trade worth taking for a label.
    ///
    /// ONE ASYMMETRY, DECLARED. The LOSS path never reaches
    /// `EndCombatInternal` at all — `CheckWinCondition` sees the pending loss,
    /// calls `ProcessPendingLoss` and returns — so there is no combat-end hook
    /// on a death. `died` was already exact from the player's own death and
    /// stays the observation that labels it; <see cref="SeatDied"/> is where
    /// the record closes on a death.
    /// </summary>
    internal static void CombatEnded(bool victory)
    {
        try
        {
            if (Open.Count == 0) return;
            var combat = CombatManager.Instance?.DebugOnlyGetState();
            foreach (var (player, record) in Open)
            {
                var creature = player.Creature;
                if (creature == null) continue;
                // THE FINAL READING, CAPPED BY THE LAST IN-FIGHT ONE.
                // `ReviveBeforeCombatEnd` runs immediately before this hook, so
                // current HP can be HIGHER than anything this fight ever saw —
                // and an HP ledger that credits a fight for the revive that
                // followed it is the same class of lie as one that charges it
                // for the campfire.
                var now = (int)creature.CurrentHp;
                record.HpLastSeen = record.HpLastSeen >= 0
                    ? Math.Min(record.HpLastSeen, now)
                    : now;
            }

            // PRIMARY enemies, mirroring `CombatManager.IsEnding` exactly: a
            // surviving non-primary minion does not stop a combat from ending,
            // so counting it here would relabel won fights as `ended` for the
            // encounters that summon.
            var primariesLeft = combat?.Enemies
                .Any(e => e != null && e.IsAlive && e.IsPrimaryEnemy) ?? false;
            FlushAll(victory || !primariesLeft ? "won" : "ended");
        }
        catch (Exception e)
        {
            Warn("CombatEnded", e);
        }
    }

    /// <summary>A fight is over when every enemy is down or every seat is.
    /// Asked at each turn boundary and on a killing blow, ahead of the
    /// combat-end hook, so the record closes at the moment the fight did; the
    /// stale-flush in <see cref="OpenFight"/> remains the backstop for every
    /// ending neither sees (fled, abandoned, crashed).</summary>
    internal static void MaybeClose(ICombatState combat)
    {
        if (Open.Count == 0) return;
        CloseIfOver(FightGoesOn(combat));
    }

    /// <summary>
    /// 2026-10-05 — A BOSS THAT COMES BACK IN A NEW FORM. Test Subject has
    /// three forms; when the first two drop to 0 HP every enemy is down for a
    /// moment, and a fight line closed on "no enemy alive" was written `won`
    /// after form 1 -- forms 2 and 3, their turns and damage, and a death in
    /// them were never written (lane 3, 2026-10-05: won in 2 turns, the
    /// player died to form 3).
    ///
    /// The game asks the same question before it ends a combat
    /// (<c>CombatManager.IsCombatEnding</c>): its last clause is
    /// <c>Hook.ShouldStopCombatFromEnding</c>, which Test Subject's
    /// <c>AdaptablePower</c> answers true until its third form, and which
    /// Phrog Parasite-style spawners use the same way. So the fight goes on
    /// while any enemy is alive (any, not only primaries: a living summon
    /// keeps the record open as it always did, and the combat-end hook still
    /// closes it) OR while something in the combat holds it open.
    /// </summary>
    internal static bool FightGoesOn(ICombatState? combat)
    {
        if (combat == null) return true;
        return combat.Enemies.Any(e => e != null && e.IsAlive)
               || MegaCrit.Sts2.Core.Hooks.Hook.ShouldStopCombatFromEnding(combat);
    }

    /// <summary>The combat-free half of <see cref="MaybeClose"/>, and the test
    /// seam.</summary>
    internal static void CloseIfOver(bool enemiesLeft)
    {
        if (Open.Count == 0) return;
        var seatsLeft = Open.Keys.Any(p => p.Creature is { IsDead: false });
        if (enemiesLeft && seatsLeft) return;
        FlushAll(enemiesLeft ? "died" : "won");
    }

    /// <summary>
    /// 2026-10-05 — THE FATAL FIGHT. A fight the player died in wrote no line
    /// (Klee suite 1, the two act-1 boss deaths on lanes 3 and 4), so a kit's
    /// boss and elite rows counted only fights it won. Neither close seam
    /// hears a death: <c>CreatureCmd.Damage</c> skips
    /// <c>AfterDamageReceived</c> for a creature the hit killed, and the loss
    /// path never reaches <c>EndCombatInternal</c> (see
    /// <see cref="CombatEnded"/>). The game goes from the last seat's death
    /// straight to <c>LoseCombat</c> and the game-over screen, so the
    /// stale-flush in the next <see cref="OpenFight"/> never comes either.
    ///
    /// <c>AfterDeath</c> does fire for a player (in
    /// <c>KillWithoutCheckingWinCondition</c>, before the player's hooks are
    /// deactivated and before <c>Kill</c> checks for the loss), so the record
    /// closes there: HP is the corpse's 0, and the fight is written once, as
    /// `died`, when the last seat is down. In co-op a seat that dies while
    /// another stands keeps its record open; it is labelled `died` at the
    /// fight's close by <see cref="FlushAll"/>, as it always was.
    /// </summary>
    internal static void SeatDied(Creature creature)
    {
        try
        {
            if (Open.Count == 0 || creature?.Player == null) return;
            var combat = CombatManager.Instance?.DebugOnlyGetState();
            CloseOnSeatDeath(creature, FightGoesOn(combat));
        }
        catch (Exception e)
        {
            Warn("SeatDied", e);
        }
    }

    /// <summary>The combat-free half of <see cref="SeatDied"/>, and the test
    /// seam. A seat with no open record (already flushed) writes nothing, so
    /// the fight is filed once.</summary>
    internal static void CloseOnSeatDeath(Creature creature, bool enemiesLeft)
    {
        if (creature?.Player is not { } player
            || !Open.TryGetValue(player, out var record)) return;
        record.HpLastSeen = Math.Max(0, (int)creature.CurrentHp);
        CloseIfOver(enemiesLeft);
    }

    internal static void FlushAll(string outcome)
    {
        if (Open.Count == 0) return;

        // LAST SAMPLE BEFORE THE WRITE. Cheap, and it is what makes a fight
        // that ended between two turn boundaries carry its bomb counters.
        //
        // ONE RACE STAYS, DECLARED. A killing blow on the LAST living enemy
        // closes the record from inside `Damage`, and the corpse detonation
        // that same blow may trigger is another `AfterDamageReceived` listener
        // in the same iteration -- so if the bomb runs after this listener, the
        // final enemy's corpse detonation lands after its record is written and
        // is not counted. Every earlier enemy is unaffected (no flush happens),
        // which is why the counter is a per-fight COUNT and not an existence
        // claim: `corpse_detonations > 0` is a fact, `== 0` on a fight that
        // ended on a bombed enemy is not proof of absence. The live smoke is
        // what settles the listener order.
        var open = CombatManager.Instance?.DebugOnlyGetState();
        if (open != null) SampleDetonations(open);

        var records = Open.ToList();
        Open.Clear();
        foreach (var (player, record) in records)
        {
            var creature = player.Creature;
            // THE LAST IN-FIGHT READING, NOT THE CURRENT ONE. There is no
            // first-party combat-END hook, so a won fight is closed by the
            // NEXT fight's stale-flush -- and reading HP then would charge this
            // fight for the campfire, the event and the potion in between. The
            // first run-verification recorded a 6-damage fight as costing 59
            // HP for exactly that reason.
            record.HpEnd = record.HpLastSeen >= 0
                ? record.HpLastSeen
                : creature != null ? (int)creature.CurrentHp : record.HpStart;
            record.Outcome = creature is { IsDead: true } ? "died" : outcome;
            record.HomeworkBombSize = HomeworkBombSizes(DeckOf(player));
            NoteStage(record, creature);
            record.HpAfterReturn = record.HpEnd;
            if (_returnWatch && record.Outcome is "won" or "ended")
            {
                AwaitingReturn.Add((player, record));
                continue;
            }
            Write(record);
        }
    }

    /// <summary>
    /// The Klee scaling pass (klee-next, 2026-10-05): the run-long Bomb size of
    /// each Witch's Homework II in <paramref name="player"/>'s deck at fight
    /// end -- base 6 plus its saved <c>HomeworkGrowth</c>, deck order. Empty
    /// with none. Never throws: a deck that cannot be read is an empty list.
    /// </summary>
    internal static List<int> HomeworkBombSizes(IEnumerable<CardModel>? deck)
    {
        var sizes = new List<int>();
        if (deck == null) return sizes;
        foreach (var card in deck)
        {
            if (card is IHomeworkCard homework)
                sizes.Add(KleeScalingPass.RunBombSize(homework));
        }

        return sizes;
    }

    /// <summary>The seat's deck, or null when there is none to read.</summary>
    private static IEnumerable<CardModel>? DeckOf(Player player)
    {
        try
        {
            return player.Deck?.Cards.ToList();
        }
        catch (Exception e) when (e is InvalidOperationException
                                    or NullReferenceException)
        {
            return null;
        }
    }

    // ------------------------------------------------------------- write ---

    private static void Write(FightRecord record)
    {
        if (_writeFailed) return;
        try
        {
            var path = LogPath();
            if (path == null) return;
            File.AppendAllText(path, record.ToJson() + "\n", new UTF8Encoding(false));
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException
                                    or NotSupportedException)
        {
            // ONCE, then never again: a per-fight warning for a disk that is
            // not going to become writable mid-run is noise in the one log a
            // crash report is read from.
            _writeFailed = true;
            Log.Warn($"[{KleeMod.ModId}] play telemetry disabled for this "
                   + $"session ({e.GetType().Name}: {e.Message})");
        }
    }

    private static string Root() =>
        Path.Combine(ProjectSettings.GlobalizePath("user://"), "gits_telemetry");

    /// <summary>This session's stamp, fixed at first use. It names the log file
    /// AND prefixes every `run_instance` written into it, so a token found in a
    /// row says which session minted it without a lookup.</summary>
    private static string Session() =>
        _session ??= DateTime.Now.ToString("yyyyMMdd-HHmmss",
                                           CultureInfo.InvariantCulture);

    private static string? LogPath()
    {
        if (_path != null) return _path;
        var root = Root();
        Directory.CreateDirectory(root);
        _path = Path.Combine(root, $"play-{Session()}.jsonl");
        var intent = Intent();
        Log.Info($"[{KleeMod.ModId}] play telemetry ({Feed()} feed"
               + (intent.Length > 0 ? $", intent '{intent}'" : ", no declared intent")
               + $") -> {_path}");
        return _path;
    }

    private static string Feed()
    {
        var declared = System.Environment.GetEnvironmentVariable(FeedEnvVar);
        return string.IsNullOrWhiteSpace(declared) ? "human" : declared!.Trim();
    }

    /// <summary>The session's declared deck intent, cached after the first
    /// read. Environment first (the harness), then `intent.txt` (the person).
    /// Every failure path returns `""`: an intent nobody could read is an
    /// intent nobody declared, and a telemetry file is not worth one line of
    /// noise in the log a crash report gets read from.</summary>
    private static string Intent()
    {
        if (_intent != null) return _intent;
        var declared = System.Environment.GetEnvironmentVariable(IntentEnvVar);
        if (declared != null)
        {
            // SET-BUT-EMPTY IS A DECLARATION OF NOTHING, NOT AN ABSENCE, and
            // only an ABSENT variable may consult the human's file. The soak
            // exports `GITS_TELEMETRY_INTENT=""` on every launch that had no
            // `--commit` (understudy/soak.py), precisely so an operator's
            // inherited shell variable cannot leak in. Under the old
            // IsNullOrWhiteSpace test that empty string fell THROUGH to
            // `intent.txt` -- the human feed's persistent, cross-session
            // declaration -- so the mod half of a bot soak carried an
            // archetype nobody declared for it while the soak half carried
            // "", splitting one soak across `--intent none` and a declared arm
            // and breaking this class's own "read once so a run's records
            // cannot disagree with each other" invariant. Same bug shape
            // f5784f9 fixed for GITS_TELEMETRY_FEED, whose non-empty "bot"
            // hid it. `Clean("")` is `""`, which is what a column should show.
            return _intent = Clean(declared);
        }

        try
        {
            var file = Path.Combine(Root(), IntentFile);
            if (!File.Exists(file)) return _intent = string.Empty;
            // FIRST LINE ONLY, and the rest is free comment space. Somebody
            // will eventually write down why they declared what they declared,
            // and the reader that punished them for it would be this one.
            var first = File.ReadLines(file, new UTF8Encoding(false))
                            .FirstOrDefault() ?? string.Empty;
            return _intent = Clean(first);
        }
        catch (Exception)
        {
            return _intent = string.Empty;
        }
    }

    /// <summary>One lowercase word, no punctuation to argue about. `Fanfare`,
    /// `fanfare `, and `FANFARE` are the same declaration.</summary>
    private static string Clean(string raw)
    {
        var trimmed = raw.Trim().ToLowerInvariant();
        var cut = trimmed.IndexOfAny(new[] { ' ', '\t', '#' });
        if (cut >= 0) trimmed = trimmed.Substring(0, cut);
        return trimmed.Length > 32 ? trimmed.Substring(0, 32) : trimmed;
    }

    // ------------------------------------------------------------ readers --

    internal static int EnemyPool(ICombatState combat) =>
        combat.Enemies.Where(e => e.IsAlive)
              .Sum(e => Math.Max(0, (int)e.CurrentHp) + Math.Max(0, (int)e.Block));

    /// <summary>The living enemies' HP alone (no Block): the pool's sibling.</summary>
    internal static int EnemyHp(ICombatState combat) =>
        combat.Enemies.Where(e => e.IsAlive).Sum(e => Math.Max(0, (int)e.CurrentHp));

    /// <summary>
    /// (total telegraphed attack damage, attacking bodies) for the turn about
    /// to be played, read BEFORE block. Same limit the wire adapter declares:
    /// this is this-turn-accurate and future-turn-blind, and it reads the
    /// rendered intent LABEL because no numeric intent-damage property is
    /// exposed anywhere in the game's public surface.
    /// </summary>
    private static (int Damage, int Attackers) Telegraphed(ICombatState combat)
    {
        var total = 0;
        var attackers = 0;
        foreach (var creature in combat.Enemies.Where(e => e.IsAlive))
        {
            if (creature.Monster?.NextMove is not MoveState move) continue;
            foreach (var intent in move.Intents)
            {
                if (!string.Equals(intent.IntentType.ToString(), "Attack",
                                   StringComparison.OrdinalIgnoreCase)) continue;
                var targets = creature.CombatState?.PlayerCreatures;
                string label;
                try
                {
                    label = BbCode.Replace(
                        intent.GetIntentLabel(targets, creature).GetFormattedText(),
                        string.Empty).Trim();
                }
                catch (Exception)
                {
                    continue;                    // some intents cannot render
                }

                var m = IntentLabel.Match(label);
                if (!m.Success) continue;
                var hit = int.Parse(m.Groups[1].Value, CultureInfo.InvariantCulture);
                var hits = m.Groups[2].Success
                    ? int.Parse(m.Groups[2].Value, CultureInfo.InvariantCulture)
                    : 1;
                total += hit * hits;
                attackers++;
            }
        }

        return (total, attackers);
    }

    /// <summary>The run's string seed — the token the game's own run history
    /// writes as `seed`, which is what makes this the join key rather than an
    /// invented id. `""` when there is no run to ask (and a reader must treat
    /// an empty run id as unjoinable rather than as one big run).</summary>
    private static string RunId(RunState run)
    {
        try
        {
            return run.Rng?.StringSeed ?? string.Empty;
        }
        catch (Exception)
        {
            return string.Empty;
        }
    }

    /// <summary>The encounter's model id (`ENCOUNTER.…`), which names WHICH
    /// fight this was — the enemy list alone does not, because two encounters
    /// can spawn the same bodies. Room first, combat second: they are the same
    /// object in the ordinary case, and the fallback costs nothing.</summary>
    private static string EncounterId(CombatRoom room, ICombatState combat)
    {
        try
        {
            var encounter = room.Encounter ?? combat.Encounter;
            return encounter?.Id.Entry ?? string.Empty;
        }
        catch (Exception)
        {
            return string.Empty;
        }
    }

    private static string NameOf(Creature creature)
    {
        try
        {
            return creature.Monster?.Id.Entry ?? "unknown";
        }
        catch (Exception)
        {
            return "unknown";
        }
    }

    /// <summary>A card's name as the records write it ("Strike+"); "" for
    /// none. The Furina ledger files her Spends under it.</summary>
    internal static string CardNameOf(CardModel? card) =>
        card == null ? "" : CardName(card);

    private static string CardName(CardModel card)
    {
        try
        {
            var title = card.Title ?? card.Id.Entry;
            return card.IsUpgraded ? title + "+" : title;
        }
        catch (Exception)
        {
            return "unknown";
        }
    }

    private static string SafeTitle(Player player)
    {
        try
        {
            return player.Character?.Title?.GetFormattedText() ?? "unknown";
        }
        catch (Exception)
        {
            return "unknown";
        }
    }

    private static void Warn(string where, Exception e) =>
        Log.Warn($"[{KleeMod.ModId}] play telemetry {where} skipped "
               + $"({e.GetType().Name}: {e.Message})");

    // ------------------------------------------------------------ record ---

    private sealed class FightRecord
    {
        public string RunId = string.Empty;
        public string RunInstance = string.Empty;
        public int FightIndex;
        public string Encounter = string.Empty;
        public int Detonations;
        public int MineDetonations;
        public int CorpseDetonations;
        /// <summary>2026-10-08. Klee-arm charges whose explosion set off an
        /// Elemental Reaction (`bomb_reactions`); the seat's other reactions
        /// came from its Attacks and element cards.</summary>
        public int BombReactions;
        /// <summary>2026-10-08. The Mines among `mine_detonations` that an
        /// enemy's attack set off; the rest were Set off.</summary>
        public int MineDetonationsByAttack;
        public int Act;
        public int Floor;
        public string Kind = "unknown";
        public int Seats;
        public int SeatIndex;
        public string Character = "unknown";
        public List<(string Name, int MaxHp)> Enemies = new();
        public int HpStart;
        public int HpEnd;
        /// <summary>2026-10-10. The HP after the end-of-combat effects (see
        /// <see cref="FinishReturns"/>); -1 when it could not be read.</summary>
        public int HpAfterReturn = -1;
        /// <summary>2026-10-10. Furina's stage ledger for this fight, null
        /// for anyone else (<see cref="NoteStage"/>).</summary>
        public FurinaStageLedger? Stage;
        /// <summary>2026-10-10. Her Fanfare at the close.</summary>
        public int FanfareEnd = -1;
        /// <summary>2026-10-10 (the full-run round). [round, Fanfare] as each
        /// of her turns opens (<see cref="NoteFanfareTurnStart"/>).</summary>
        public readonly List<int[]> FanfareTurnStart = new();
        /// <summary>2026-10-10 (round 2). The rounds that opened with a
        /// Block-gaining card in hand and attack damage telegraphed
        /// (<see cref="BlockCardTurn"/>).</summary>
        public readonly SortedSet<int> BlockCardRounds = new();
        public int MaxHp;
        public int Turns;
        public string Outcome = "unknown";
        public readonly List<int[]> HpTrajectory = new();
        public readonly List<int[]> IncomingByTurn = new();
        public readonly List<int[]> EnemyPoolByTurn = new();
        public readonly List<int[]> EnemyHpByTurn = new();
        public readonly List<int[]> BlockAtTurnEnd = new();
        public readonly List<int[]> StrengthByTurn = new();
        public readonly List<int[]> ReactionsByTurn = new();
        /// <summary>-1 until the first turn sample; the counter is monotonic
        /// across combats, so a fight's own count is a difference.</summary>
        public int ReactionsAtStart = -1;
        /// <summary>The last HP read while this fight was still live; -1 until
        /// the first turn sample. See the flush for why the current value will
        /// not do.</summary>
        public int HpLastSeen = -1;
        /// <summary>`[round, name]`, and for Varka `[round, name, element]`:
        /// his current element once the card resolved (the Varka payoff
        /// round, 2026-10-10: "log the current element on every
        /// `cards_played` row"); "None" before any is set.</summary>
        public readonly List<(int Round, string Name, string? Element)> CardsPlayed = new();
        /// <summary>EB-14. One row per card taken from a selection screen,
        /// in the bot feed's column order. `Offered` is SHARED between the
        /// rows of one screen on purpose: it is written once and never
        /// mutated, and copying it per row would say the two answers came
        /// from two different offers.</summary>
        public readonly List<(int Round, string Screen, int Index, string Chosen,
                              IReadOnlyList<string> Offered)> Selectors = new();
        /// <summary>EB-118. One pre-rendered JSON object per resolved
        /// Exhaust selection, in the sim's column order. Rendered by
        /// `Powers.ExhaustSelection.ParityRow`, which owns the names.</summary>
        public readonly List<string> ExhaustSelections = new();
        public readonly Dictionary<string, int> DamageBySource = new();
        /// <summary>2026-10-02. The same damage split by kind
        /// (<see cref="DamageCredit"/>'s constants), so a reader can tell a
        /// card's hit from an element hit, a reaction, a pet or a Bomb.</summary>
        public readonly Dictionary<string, int> DamageByKind = new();
        /// <summary>2026-10-06. Reactions this seat resolved, by name
        /// (<see cref="ReactionTally"/>; sums to at least the FINAL entry of
        /// `reactions_by_turn`, which is a running total sampled at turn
        /// open and so misses the last turn).</summary>
        public readonly Dictionary<string, int> ReactionsByType = new();
        /// <summary>2026-10-06. The amplifiers' share of the hits they
        /// multiplied, by reaction; written rounded to whole damage.</summary>
        public readonly Dictionary<string, decimal> AmpBonusDamage = new();
        /// <summary>2026-10-06. Debuff stacks this seat's reactions put on
        /// enemies, by power.</summary>
        public readonly Dictionary<string, int> DebuffsFromReactions = new();
        /// <summary>Block this seat's credited hits broke.</summary>
        public int DamageBlocked;
        /// <summary>Hits of this seat's that killed (filed through
        /// <see cref="RecordDeath"/>).</summary>
        public int KillingBlows;
        /// <summary>Block gained by this seat's creature, by round.</summary>
        public readonly SortedDictionary<int, int> BlockGained = new();
        /// <summary>Block this seat's cards put on another seat.</summary>
        public int BlockGiven;
        public int DamageTaken;
        /// <summary>The Klee scaling pass: each Witch's Homework II's
        /// run-long Bomb size at fight end (<see cref="HomeworkBombSizes"/>).
        /// </summary>
        public List<int> HomeworkBombSize = new();

        /// <summary>
        /// Hand-rolled rather than serialized by reflection, deliberately: the
        /// key names ARE the shared schema (understudy/README.md), and a
        /// serializer that derives them from field names turns a C# rename
        /// into a silent cross-session schema break. Written out, a rename
        /// here is a diff someone reads.
        /// </summary>
        public string ToJson()
        {
            var sb = new StringBuilder();
            sb.Append('{');
            Str(sb, "record", "fight");
            sb.Append(',');
            Str(sb, "schema", SchemaVersion);
            sb.Append(',');
            Str(sb, "feed", Feed());
            sb.Append(',');
            Str(sb, "source", "mod");
            sb.Append(',');
            // R99/4a. Empty when nobody declared anything -- which is a
            // reading, not a gap, so the key is always present.
            Str(sb, "intent", Intent());
            // EB-18. The join key and the position of this fight inside the
            // run it belongs to; all three always present, empty run id and
            // all. `run_instance` is the ADDITION that makes the pair unique
            // under a replayed seed -- adding a key is free at this schema
            // version (understudy/README.md), and a reader that does not know
            // it drops back to the old, seed-only grouping.
            sb.Append(',');
            Str(sb, "run_id", RunId);
            sb.Append(',');
            Str(sb, "run_instance", RunInstance);
            sb.Append(",\"fight_index\":").Append(FightIndex);
            sb.Append(',');
            Str(sb, "encounter", Encounter);
            sb.Append(",\"seats\":").Append(Seats);
            sb.Append(",\"seat_index\":").Append(SeatIndex);
            sb.Append(',');
            Str(sb, "character", Character);
            sb.Append(",\"act\":").Append(Act);
            sb.Append(",\"floor\":").Append(Floor);
            sb.Append(',');
            Str(sb, "kind", Kind);
            sb.Append(",\"enemies\":[");
            for (var i = 0; i < Enemies.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append("{\"name\":");
                Quote(sb, Enemies[i].Name);
                sb.Append(",\"max_hp\":").Append(Enemies[i].MaxHp).Append('}');
            }

            sb.Append(']');
            sb.Append(",\"hp_start\":").Append(HpStart);
            sb.Append(",\"hp_end\":").Append(HpEnd);
            sb.Append(",\"max_hp\":").Append(MaxHp);
            sb.Append(",\"hp_lost\":").Append(HpStart - HpEnd);
            // 2026-10-10. Additive: the HP once the end-of-combat effects
            // ran (Furina's curtain call, Burning Blood); -1 not read.
            sb.Append(",\"hp_after_return\":").Append(HpAfterReturn);
            if (Stage != null)
            {
                // 2026-10-10, the Spend round. Furina only: her peak Fanfare,
                // her Fanfare at the close, and every Spend.
                sb.Append(",\"fanfare_peak\":").Append(Stage.PeakFanfare);
                sb.Append(",\"fanfare_end\":").Append(FanfareEnd);
                sb.Append(",\"fanfare_spends\":[");
                var spends = Stage.Spends;
                for (var i = 0; i < spends.Count; i++)
                {
                    if (i > 0) sb.Append(',');
                    sb.Append('{');
                    Str(sb, "card", spends[i].Source);
                    sb.Append(",\"spent\":").Append(spends[i].Spent);
                    sb.Append(",\"before\":").Append(spends[i].Before);
                    sb.Append(",\"cap\":").Append(spends[i].Cap);
                    sb.Append('}');
                }
                sb.Append(']');
                // 2026-10-10, the Spend round 2. HP drained past the line
                // and not returned (the curtain call's lost part; at a
                // death, the past-line HP still owed), and the damage High
                // Stakes added to her Attack hits.
                sb.Append(",\"past_lost\":").Append(Stage.PastLostAtClose);
                sb.Append(",\"high_stakes_bonus\":")
                  .Append(Stage.HighStakesDealt);
                // 2026-10-10, the full-run round: her Fanfare as each turn
                // opened, [round, fanfare].
                Pairs(sb, "fanfare_turn_start", FanfareTurnStart);
            }
            sb.Append(",\"turns\":").Append(Turns);
            sb.Append(',');
            Str(sb, "outcome", Outcome);
            Pairs(sb, "hp_trajectory", HpTrajectory);
            Pairs(sb, "incoming_by_turn", IncomingByTurn);
            Pairs(sb, "enemy_pool_by_turn", EnemyPoolByTurn);
            Pairs(sb, "enemy_hp_by_turn", EnemyHpByTurn);
            Pairs(sb, "block_at_turn_end", BlockAtTurnEnd);
            Pairs(sb, "strength_by_turn", StrengthByTurn);
            Pairs(sb, "reactions_by_turn", ReactionsByTurn);
            sb.Append(",\"cards_played\":[");
            for (var i = 0; i < CardsPlayed.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append('[').Append(CardsPlayed[i].Round).Append(',');
                Quote(sb, CardsPlayed[i].Name);
                if (CardsPlayed[i].Element is { } element)
                {
                    sb.Append(',');
                    Quote(sb, element);
                }
                sb.Append(']');
            }

            sb.Append(']');
            sb.Append(",\"n_cards_played\":").Append(CardsPlayed.Count);
            // EB-14. `[round, screen, index, chosen, [offered…]]`, the bot
            // feed's row shape column for column -- the whole point of the
            // channel is that the two feeds can be read by one reader, and
            // `understudy/replay.py` matches on the OFFERED list, not just the
            // answer.
            sb.Append(",\"selectors\":[");
            for (var i = 0; i < Selectors.Count; i++)
            {
                if (i > 0) sb.Append(',');
                var row = Selectors[i];
                sb.Append('[').Append(row.Round).Append(',');
                Quote(sb, row.Screen);
                sb.Append(',').Append(row.Index).Append(',');
                Quote(sb, row.Chosen);
                sb.Append(",[");
                for (var j = 0; j < row.Offered.Count; j++)
                {
                    if (j > 0) sb.Append(',');
                    Quote(sb, row.Offered[j]);
                }

                sb.Append("]]");
            }

            sb.Append(']');
            // EB-118. Written verbatim: each entry is already a JSON object
            // whose keys are ExhaustSelection.RowKeys.
            sb.Append(",\"exhaust_selections\":[");
            for (var i = 0; i < ExhaustSelections.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append(ExhaustSelections[i]);
            }

            sb.Append(']');
            sb.Append(",\"damage_by_source\":{");
            var first = true;
            foreach (var pair in DamageBySource.OrderBy(p => p.Key, StringComparer.Ordinal))
            {
                if (!first) sb.Append(',');
                first = false;
                Quote(sb, pair.Key);
                sb.Append(':').Append(pair.Value);
            }

            sb.Append('}');
            sb.Append(",\"damage_dealt\":").Append(DamageBySource.Values.Sum());
            // 2026-10-02. Additive keys (understudy/README.md): the kind
            // split, the Block the credited hits broke, the killing hits
            // (which `damage_dealt` now includes), and Block gained.
            sb.Append(",\"damage_by_kind\":{");
            first = true;
            foreach (var pair in DamageByKind.OrderBy(p => p.Key, StringComparer.Ordinal))
            {
                if (!first) sb.Append(',');
                first = false;
                Quote(sb, pair.Key);
                sb.Append(':').Append(pair.Value);
            }

            sb.Append('}');
            // 2026-10-06. What reactions are worth, per seat. Additive keys,
            // human feed only (`understudy/README.md`).
            sb.Append(",\"reactions_by_type\":");
            IntMap(sb, ReactionsByType);
            sb.Append(",\"amp_bonus_damage\":");
            IntMap(sb, AmpBonusDamage.ToDictionary(
                p => p.Key,
                p => (int)Math.Round(p.Value, MidpointRounding.AwayFromZero)));
            sb.Append(",\"debuffs_from_reactions\":");
            IntMap(sb, DebuffsFromReactions);
            sb.Append(",\"damage_blocked\":").Append(DamageBlocked);
            sb.Append(",\"killing_blows\":").Append(KillingBlows);
            sb.Append(",\"block_gained_by_turn\":[");
            first = true;
            foreach (var pair in BlockGained)
            {
                if (!first) sb.Append(',');
                first = false;
                sb.Append('[').Append(pair.Key).Append(',').Append(pair.Value).Append(']');
            }

            sb.Append(']');
            sb.Append(",\"block_gained\":").Append(BlockGained.Values.Sum());
            sb.Append(",\"block_given\":").Append(BlockGiven);
            // 2026-10-10 (the Furina Spend round 2). Every character.
            sb.Append(",\"block_card_turns\":").Append(BlockCardRounds.Count);
            sb.Append(",\"block_card_turns_no_block\":")
              .Append(BlockCardRounds.Count(r =>
                  !BlockGained.TryGetValue(r, out var b) || b <= 0));
            sb.Append(",\"damage_taken\":").Append(DamageTaken);
            // EB-18. This seat's bombs, and how many of them went off on a
            // body that was already dead (probe (e) / Q11's question, asked of
            // every fight instead of one scripted pair).
            sb.Append(",\"detonations\":").Append(Detonations);
            sb.Append(",\"mine_detonations\":").Append(MineDetonations);
            sb.Append(",\"corpse_detonations\":").Append(CorpseDetonations);
            // The Klee scaling pass (klee-next, 2026-10-05). Additive: one
            // int per Witch's Homework II in the deck, `[]` with none.
            sb.Append(",\"homework_bomb_size\":[")
              .Append(string.Join(",", HomeworkBombSize.Select(
                  n => n.ToString(CultureInfo.InvariantCulture))))
              .Append(']');
            sb.Append(",\"bomb_reactions\":").Append(BombReactions);
            sb.Append(",\"mine_detonations_by_attack\":")
              .Append(MineDetonationsByAttack);
            sb.Append(",\"ts\":").Append(
                (DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0)
                    .ToString("F3", CultureInfo.InvariantCulture));
            sb.Append('}');
            return sb.ToString();
        }

        private static void IntMap(StringBuilder sb, IReadOnlyDictionary<string, int> map)
        {
            sb.Append('{');
            var first = true;
            foreach (var pair in map.OrderBy(p => p.Key, StringComparer.Ordinal))
            {
                if (!first) sb.Append(',');
                first = false;
                Quote(sb, pair.Key);
                sb.Append(':').Append(pair.Value);
            }

            sb.Append('}');
        }

        private static void Pairs(StringBuilder sb, string key, List<int[]> rows)
        {
            sb.Append(",\"").Append(key).Append("\":[");
            for (var i = 0; i < rows.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append('[');
                for (var j = 0; j < rows[i].Length; j++)
                {
                    if (j > 0) sb.Append(',');
                    sb.Append(rows[i][j]);
                }

                sb.Append(']');
            }

            sb.Append(']');
        }

        private static void Str(StringBuilder sb, string key, string value)
        {
            sb.Append('"').Append(key).Append("\":");
            Quote(sb, value);
        }

        private static void Quote(StringBuilder sb, string value)
        {
            sb.Append('"');
            foreach (var c in value)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 0x20)
                        {
                            sb.Append("\\u").Append(((int)c).ToString("x4",
                                CultureInfo.InvariantCulture));
                        }
                        else
                        {
                            sb.Append(c);
                        }

                        break;
                }
            }

            sb.Append('"');
        }
    }
}

/// <summary>
/// The subscription face. Registered through the same single
/// <c>SubscribeForCombatStateHooks</c> chain every other listener rides
/// (validate.ps1 S6c allows exactly one call), and resolved through
/// <c>ModelDb</c> rather than <c>new()</c> — a manual construction throws
/// <c>DuplicateModelException</c> at the first combat, which is a lost run.
/// </summary>
public sealed class PlayTelemetryHooks : AbstractModel
{
    private static PlayTelemetryHooks? _instance;

    public override bool ShouldReceiveCombatHooks => true;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        // THE ONE PLACE A MEASUREMENT COULD STILL COST A RUN. This runs inside
        // the roster's single subscription delegate, so an exception here does
        // not disable telemetry -- it disables the aura, resource and garment
        // hooks concatenated beside it. A missing ModelDb registration is a
        // deployment accident; losing Furina's Encore to one would not be.
        PlayTelemetryHooks? instance;
        try
        {
            instance = _instance ??= ModelDb.GetById<PlayTelemetryHooks>(
                ModelDb.GetId<PlayTelemetryHooks>());
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] play telemetry not subscribed "
                   + $"({e.GetType().Name}: {e.Message}); the rest of the "
                   + "combat hooks are unaffected");
            yield break;
        }

        if (instance != null) yield return instance;
    }

    public override Task BeforeCombatStart()
    {
        PlayTelemetry.OpenFight();
        // `EB-216`. A ledger carrying one fight's rows into the next would let
        // a grader attribute a spend to the wrong fight.
        MeterLedger.ResetFight();
        // `EB-349` / `EB-611`. The same rule for the resolution ledger, one
        // reader over: a row from the last fight printed on this fight's first
        // page is the `EB-447` deck defect wearing a different hat.
        ResolutionLedger.ResetFight();
        WatchedPowers.Clear();
        return Task.CompletedTask;
    }

    /// <summary>
    /// 2026-10-05, THE SEAT PAGE'S "SINCE LAST PAGE" LINE: the enemy powers
    /// whose firing is watched. A base-game power marks the moment it acts
    /// with <c>Flash()</c>, which raises its <c>Flashed</c> event -- Crab Rage
    /// when an arm dies, Hard To Kill on a capped hit -- and the page's
    /// after-state shows the result with nothing naming the cause. Watched by
    /// subscribing to the event rather than patching <c>Flash</c>, a one-line
    /// method the JIT may inline past a Harmony patch.
    ///
    /// BASE-GAME POWERS ON ENEMIES ONLY: the mod's own badges (auras, Bombs)
    /// have their own receipts, and the player's own powers are on the
    /// player's block. Cleared per fight.
    /// </summary>
    private static readonly HashSet<PowerModel> WatchedPowers =
        new(ReferenceEqualityComparer.Instance);

    private static void Watch(PowerModel? power)
    {
        try
        {
            if (power == null || WatchedPowers.Contains(power)) return;
            if (power.Owner is not { IsEnemy: true }) return;
            var ns = power.GetType().Namespace ?? "";
            if (!ns.StartsWith("MegaCrit.", StringComparison.Ordinal)) return;
            WatchedPowers.Add(power);
            power.Flashed += OnEnemyPowerFlashed;
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] page events watch: "
                   + $"{e.GetType().Name}: {e.Message}");
        }
    }

    private static void WatchEnemies(ICombatState? combatState)
    {
        if (combatState == null) return;
        try
        {
            foreach (var enemy in combatState.Enemies)
            {
                foreach (var power in enemy.Powers.ToList()) Watch(power);
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] page events enemies: "
                   + $"{e.GetType().Name}: {e.Message}");
        }
    }

    private static void OnEnemyPowerFlashed(PowerModel power)
    {
        try
        {
            if (power.Owner is not { IsEnemy: true }) return;
            ResolutionLedger.NoteEvent(ResolutionLedger.Triggered,
                                       string.Empty, power.Owner,
                                       power.Title.GetFormattedText() ?? "");
        }
        catch (Exception)
        {
            // read-only log; nothing to undo
        }
    }

    /// <summary>2026-10-05: a card drawn by an effect rather than the turn's
    /// own draw, named on the page's "Since last page" line under the card
    /// that drew it (<see cref="ResolutionLedger.NoteEvent"/>).</summary>
    public override Task AfterCardDrawn(PlayerChoiceContext choiceContext,
                                        CardModel card, bool fromHandDraw)
    {
        if (fromHandDraw || card == null) return Task.CompletedTask;
        try
        {
            ResolutionLedger.NoteEvent(ResolutionLedger.Drawn,
                                       card.Title?.ToString() ?? "",
                                       string.Empty, string.Empty);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] page events draw: "
                   + $"{e.GetType().Name}: {e.Message}");
        }
        return Task.CompletedTask;
    }

    /// <summary>The block-card sample (2026-10-10), after the draw: the
    /// hand is the one the turn opens with.</summary>
    public override Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        PlayTelemetry.BlockCardTurn(player);
        return Task.CompletedTask;
    }

    public override Task AfterSideTurnStart(CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        WatchEnemies(combatState);
        if (side == CombatSide.Player)
        {
            PlayTelemetry.OpenTurn();
            MeterLedger.OpenTurn(
                CombatManager.Instance?.DebugOnlyGetState()?.RoundNumber ?? 0);
        }
        return Task.CompletedTask;
    }

    /// <summary>
    /// `EB-216`. THE PLAY BOUNDARY the meter ledger's rows hang off. It runs
    /// here rather than inside <c>SparkPower</c> for two reasons: the ledger is
    /// meter-agnostic by design and must not be opened by whichever meter
    /// happens to move first, and a card that spends Sparks while the counter
    /// is not yet on the creature has no <c>SparkPower</c> to run a hook at
    /// all — the row still has to exist, reading `before: 0`.
    ///
    /// PRE-RESOLUTION, so `before` is the bank the player was looking at when
    /// they chose the card. <c>IsFirstInSeries</c> keeps it to one row per
    /// play across replays, the same gate <c>SparkPower.BeforeCardPlayed</c>
    /// and the fight record already use.
    ///
    /// KOKOMI'S TWO METERS OPEN A ROW HERE TOO (`EB-273`), and they are gated
    /// on her identity where Spark's row is not. That asymmetry is deliberate
    /// rather than inherited: the Spark row predates the second meter and its
    /// `before` is a plain 0 for anyone who has no bank, which cost nothing
    /// while it was the only meter. A THIRD unconditional row would spend the
    /// 400-row cap three times over on plays that can never move the meter, and
    /// the rows a grader has not read yet are the ones the cap drops. Her
    /// Charge asks the shipped identity; her Plan queue asks the ARM, because
    /// off the arm there is no queue to have a depth at all.
    /// </summary>
    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        try
        {
            if (cardPlay?.Card == null || !cardPlay.IsFirstInSeries)
            {
                return Task.CompletedTask;
            }
            // `EB-349` / `EB-611`. THE ROW THIS CARD'S HITS WILL BE FILED
            // AGAINST, opened on the same boundary the meter rows open on and
            // under the same `IsFirstInSeries` gate. It is opened BEFORE the
            // owner check below, deliberately: that check is about a meter
            // living on a creature, and a card resolving is a fact whether or
            // not anybody has a bank. `ResolutionLedger.OpenPlay` applies the
            // gate itself so the two cannot drift apart.
            ResolutionLedger.OpenPlay(cardPlay);

            var creature = cardPlay.Card.Owner?.Creature;
            if (creature == null) return Task.CompletedTask;
            string id = cardPlay.Card.Id.Entry;
            string title = cardPlay.Card.Title ?? id;
            int turn = CombatManager.Instance?.DebugOnlyGetState()?.RoundNumber ?? 0;
            MeterLedger.OpenPlay(
                MeterLedger.Spark, id, title, turn,
                SparkPower.SparksAtPlay(creature));

            if (KokomiOverhaul.LiveFor(creature))
            {
                MeterLedger.OpenPlay(
                    MeterLedger.Plan, id, title, turn,
                    KokomiPlan.Pending(creature.Player!).Count);
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] meter ledger play boundary: "
                   + $"{e.GetType().Name}: {e.Message}");
        }
        return Task.CompletedTask;
    }

    public override Task AfterSideTurnEnd(PlayerChoiceContext choiceContext,
        CombatSide side, IEnumerable<Creature> participants)
    {
        if (side == CombatSide.Player) PlayTelemetry.CloseTurn();
        return Task.CompletedTask;
    }

    /// <summary>The combat-end seam (R100/5). Runs inside
    /// <c>EndCombatInternal</c>, which the loss path never reaches — so
    /// anything still open here survived to the end of a combat that ended,
    /// and <see cref="PlayTelemetry.CombatEnded"/> confirms against the live
    /// enemy list rather than trusting the name of the hook.</summary>
    public override Task AfterCombatEnd(CombatRoom room)
    {
        PlayTelemetry.CombatEnded(victory: false);
        return Task.CompletedTask;
    }

    /// <summary>The unambiguous one, kept as the backstop. It runs later in the
    /// same method, so in the ordinary case it finds nothing open — which is
    /// the point: if anything ever DOES reach it still open, that fight was a
    /// victory and gets labelled as one.</summary>
    public override Task AfterCombatVictory(CombatRoom room)
    {
        PlayTelemetry.CombatEnded(victory: true);
        return Task.CompletedTask;
    }

    public override Task AfterCardPlayed(PlayerChoiceContext choiceContext,
                                         CardPlay cardPlay)
    {
        PlayTelemetry.CardPlayed(cardPlay);
        // `EB-349` / `EB-611`. The row closes on the LAST play of the series
        // and not the first: a replayed card is ONE row to a reader (the
        // `IsFirstInSeries` gate on the open), and closing on play one would
        // file the replays' hits against nothing at all.
        if (cardPlay?.IsLastInSeries ?? true) ResolutionLedger.ClosePlay();
        return Task.CompletedTask;
    }

    /// <summary>2026-10-02. The killing-hit snapshot
    /// (<see cref="PlayTelemetry.NoteBeforeDamage"/>): read-only.</summary>
    public override Task BeforeDamageReceived(PlayerChoiceContext choiceContext,
        Creature target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        PlayTelemetry.NoteBeforeDamage(target, dealer, cardSource);
        return Task.CompletedTask;
    }

    /// <summary>2026-10-02. Block gained, per seat per round.</summary>
    public override Task AfterBlockGained(Creature creature, decimal amount,
        ValueProp props, CardModel? cardSource)
    {
        PlayTelemetry.BlockGained(creature, amount, cardSource);
        return Task.CompletedTask;
    }

    public override Task AfterDamageReceived(PlayerChoiceContext choiceContext,
        Creature target, DamageResult result, ValueProp props,
        Creature? dealer, CardModel? cardSource)
    {
        PlayTelemetry.Damage(target, result, dealer, cardSource);
        // `EB-611`. THE HIT, IN HIT ORDER, under whichever card is resolving.
        // This hook is the one place every number the game delivers arrives
        // at, and the ledger files only the ones that land inside an open play
        // -- so an enemy's attack, a bomb on nobody's turn and a relic's
        // answer pass straight through, each of which has its own receipt.
        ResolutionLedger.NoteHit(target, (int)result.UnblockedDamage,
                                 (int)result.BlockedDamage, dealer);
        return Task.CompletedTask;
    }

    /// <summary>
    /// 2026-09-26 (the Silent control seat): "Poison applied is never shown
    /// in 'what it did'." A power the resolving card put on an enemy -- Poison,
    /// Weak, Vulnerable -- filed under that card. Enemies only; the ledger
    /// drops it where no play is open.
    /// </summary>
    public override Task AfterPowerAmountChanged(PlayerChoiceContext choiceContext,
        PowerModel power, decimal amount, Creature? applier, CardModel? cardSource)
    {
        try
        {
            var owner = power?.Owner;
            if (owner is { IsEnemy: true })
            {
                Watch(power);
                ResolutionLedger.NotePower(owner,
                    power!.Title.GetFormattedText() ?? "", (int)amount);
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] resolution ledger power: "
                   + $"{e.GetType().Name}: {e.Message}");
        }
        return Task.CompletedTask;
    }

    /// <summary>
    /// THE KILLING HIT, which the hook above never hears: `CreatureCmd.Damage`
    /// skips `AfterDamageReceived` for a creature the hit killed. A Strike
    /// that killed its target therefore filed nothing, and the blind page said
    /// "Nothing this page can count landed off it" under it (three seats,
    /// 2026-09-24). `AfterDeath` fires before the corpse is removed; a death
    /// the game PREVENTED is not a kill, and a pet or a player dying is not a
    /// card killing its target, so both are declined.
    /// </summary>
    public override Task AfterDeath(PlayerChoiceContext choiceContext,
        Creature creature, bool wasRemovalPrevented, float deathAnimLength)
    {
        if (!wasRemovalPrevented && creature is { IsEnemy: true })
        {
            ResolutionLedger.NoteKill(creature);
        }
        // 2026-10-02: the killing hit's damage, credited to its seat. A
        // prevented death drops the snapshot without filing it.
        if (!wasRemovalPrevented) PlayTelemetry.RecordDeath(creature);
        else PlayTelemetry.DropPending(creature);
        // 2026-10-05: a seat's death closes the fight when it was the last
        // seat standing -- the only hook the loss path delivers. After
        // RecordDeath, so the killing hit is in the record it writes.
        if (!wasRemovalPrevented && creature is { IsPlayer: true })
        {
            PlayTelemetry.SeatDied(creature);
        }
        return Task.CompletedTask;
    }
}
