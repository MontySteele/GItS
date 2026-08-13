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
            FlushAll("interrupted");
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
            }
        }
        catch (Exception e)
        {
            Warn("OpenFight", e);
        }
    }

    // -------------------------------------------------------------- turn ---

    /// <summary>The turn-opening sample: HP, block, the telegraph BEFORE
    /// block, the meters, and the enemy HP pool. The pool is what makes an
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
                // REACTIONS RIDE ALONG, because the counter already exists and
                // sampling it costs one read (the hand-back's "cheap now"
                // condition). Measurement only: no reaction constant is
                // touched by this file. `TotalResolved` is GLOBAL rather than
                // per-player -- in co-op both seats' reactions land in every
                // seat's row, and a reader who does not know that would divide
                // by the wrong denominator.
                if (record.ReactionsAtStart < 0)
                {
                    record.ReactionsAtStart = ReactionEffects.TotalResolved;
                }

                record.ReactionsByTurn.Add(new[]
                    { round, ReactionEffects.TotalResolved - record.ReactionsAtStart });
                record.MetersByTurn.Add(new[]
                {
                    round,
                    FurinaResources.IsFurina(creature) ? FurinaResources.Fanfare(creature) : 0,
                    SalonMemberPower.Count(creature),
                    SalonMemberPower.SlotsFor(creature),
                    FurinaResources.IsFurina(creature) ? FurinaResources.Encore(creature) : 0,
                });
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
            record.Detonations = Math.Max(
                record.Detonations, BombPower.DetonationsThisCombat(combat, player));
            record.CorpseDetonations = Math.Max(
                record.CorpseDetonations,
                BombPower.CorpseDetonationsThisCombat(combat, player));
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
            var round = combat.RoundNumber;
            foreach (var (player, record) in Open)
            {
                var creature = player.Creature;
                if (creature == null) continue;
                record.BlockAtTurnEnd.Add(new[] { round, (int)creature.Block });
                record.HpLastSeen = (int)creature.CurrentHp;
            }

            SampleDetonations(combat);
            MaybeClose(combat);
        }
        catch (Exception e)
        {
            Warn("CloseTurn", e);
        }
    }

    // ------------------------------------------------------------ events ---

    internal static void CardPlayed(CardPlay cardPlay)
    {
        try
        {
            var owner = cardPlay?.Card?.Owner;
            if (owner == null || !Open.TryGetValue(owner, out var record)) return;
            if (!cardPlay!.IsFirstInSeries) return;      // one row per PLAY
            var round = CombatManager.Instance?.DebugOnlyGetState()?.RoundNumber ?? 0;
            record.CardsPlayed.Add((round, CardName(cardPlay.Card)));
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
            var amount = (int)result.UnblockedDamage;
            if (amount <= 0) return;

            if (target?.Player is { } victim && Open.TryGetValue(victim, out var taken))
            {
                taken.DamageTaken += amount;
                if (target.IsDead)
                {
                    var over = CombatManager.Instance?.DebugOnlyGetState();
                    if (over != null) MaybeClose(over);
                }

                return;
            }

            var dealerPlayer = dealer?.Player;
            if (dealerPlayer == null || !Open.TryGetValue(dealerPlayer, out var dealt)) return;
            var source = cardSource != null ? CardName(cardSource) : "(uncredited)";
            dealt.DamageBySource.TryGetValue(source, out var running);
            dealt.DamageBySource[source] = running + amount;

            // A KILLING BLOW ENDS THE FIGHT, and it has to end the record with
            // it. The first run-verification recorded every won fight as
            // `interrupted`, closed by the NEXT fight's stale-flush -- so the
            // HP ledger swallowed whatever happened in between (a campfire, an
            // event, a potion) and reported it as damage taken in a fight that
            // was already over. There is no first-party combat-end hook; the
            // last enemy dying is the closest thing the game offers.
            var combat = CombatManager.Instance?.DebugOnlyGetState();
            if (combat != null) MaybeClose(combat);
        }
        catch (Exception e)
        {
            Warn("Damage", e);
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
    /// stays the observation that labels it.
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
    private static void MaybeClose(ICombatState combat)
    {
        if (Open.Count == 0) return;
        var enemiesLeft = combat.Enemies.Any(e => e.IsAlive);
        var seatsLeft = Open.Keys.Any(p => p.Creature is { IsDead: false });
        if (enemiesLeft && seatsLeft) return;
        FlushAll(enemiesLeft ? "died" : "won");
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
            Write(record);
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

    private static int EnemyPool(ICombatState combat) =>
        combat.Enemies.Where(e => e.IsAlive)
              .Sum(e => Math.Max(0, (int)e.CurrentHp) + Math.Max(0, (int)e.Block));

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
        public int CorpseDetonations;
        public int Act;
        public int Floor;
        public string Kind = "unknown";
        public int Seats;
        public int SeatIndex;
        public string Character = "unknown";
        public List<(string Name, int MaxHp)> Enemies = new();
        public int HpStart;
        public int HpEnd;
        public int MaxHp;
        public int Turns;
        public string Outcome = "unknown";
        public readonly List<int[]> HpTrajectory = new();
        public readonly List<int[]> IncomingByTurn = new();
        public readonly List<int[]> EnemyPoolByTurn = new();
        public readonly List<int[]> MetersByTurn = new();
        public readonly List<int[]> BlockAtTurnEnd = new();
        public readonly List<int[]> ReactionsByTurn = new();
        /// <summary>-1 until the first turn sample; the counter is monotonic
        /// across combats, so a fight's own count is a difference.</summary>
        public int ReactionsAtStart = -1;
        /// <summary>The last HP read while this fight was still live; -1 until
        /// the first turn sample. See the flush for why the current value will
        /// not do.</summary>
        public int HpLastSeen = -1;
        public readonly List<(int Round, string Name)> CardsPlayed = new();
        /// <summary>EB-14. One row per card taken from a selection screen,
        /// in the bot feed's column order. `Offered` is SHARED between the
        /// rows of one screen on purpose: it is written once and never
        /// mutated, and copying it per row would say the two answers came
        /// from two different offers.</summary>
        public readonly List<(int Round, string Screen, int Index, string Chosen,
                              IReadOnlyList<string> Offered)> Selectors = new();
        public readonly Dictionary<string, int> DamageBySource = new();
        public int DamageTaken;

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
            sb.Append(",\"turns\":").Append(Turns);
            sb.Append(',');
            Str(sb, "outcome", Outcome);
            Pairs(sb, "hp_trajectory", HpTrajectory);
            Pairs(sb, "incoming_by_turn", IncomingByTurn);
            Pairs(sb, "enemy_pool_by_turn", EnemyPoolByTurn);
            Pairs(sb, "meters_by_turn", MetersByTurn);
            Pairs(sb, "block_at_turn_end", BlockAtTurnEnd);
            Pairs(sb, "reactions_by_turn", ReactionsByTurn);
            sb.Append(",\"cards_played\":[");
            for (var i = 0; i < CardsPlayed.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append('[').Append(CardsPlayed[i].Round).Append(',');
                Quote(sb, CardsPlayed[i].Name);
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
            sb.Append(",\"damage_taken\":").Append(DamageTaken);
            // EB-18. This seat's bombs, and how many of them went off on a
            // body that was already dead (probe (e) / Q11's question, asked of
            // every fight instead of one scripted pair).
            sb.Append(",\"detonations\":").Append(Detonations);
            sb.Append(",\"corpse_detonations\":").Append(CorpseDetonations);
            sb.Append(",\"ts\":").Append(
                (DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0)
                    .ToString("F3", CultureInfo.InvariantCulture));
            sb.Append('}');
            return sb.ToString();
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
        return Task.CompletedTask;
    }

    public override Task AfterSideTurnStart(CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side == CombatSide.Player) PlayTelemetry.OpenTurn();
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
        return Task.CompletedTask;
    }

    public override Task AfterDamageReceived(PlayerChoiceContext choiceContext,
        Creature target, DamageResult result, ValueProp props,
        Creature? dealer, CardModel? cardSource)
    {
        PlayTelemetry.Damage(target, result, dealer, cardSource);
        return Task.CompletedTask;
    }
}
