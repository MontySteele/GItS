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

    private static readonly Regex IntentLabel =
        new(@"^(\d+)(?:\s*[x×]\s*(\d+))?$", RegexOptions.Compiled);

    private static readonly Regex BbCode = new(@"\[/?[^\]]*\]", RegexOptions.Compiled);

    private static string? _path;
    private static bool _writeFailed;
    private static readonly Dictionary<Player, FightRecord> Open = new();

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
        }
        catch (Exception e)
        {
            Warn("OpenTurn", e);
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
            }

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

    /// <summary>A fight is over when every enemy is down or every seat is.
    /// There is no first-party combat-END hook, so this is asked at each turn
    /// boundary; the stale-flush in <see cref="OpenFight"/> is the backstop for
    /// every ending this misses (fled, abandoned, crashed).</summary>
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
        var records = Open.ToList();
        Open.Clear();
        foreach (var (player, record) in records)
        {
            var creature = player.Creature;
            record.HpEnd = creature != null ? (int)creature.CurrentHp : record.HpStart;
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

    private static string? LogPath()
    {
        if (_path != null) return _path;
        var root = Path.Combine(ProjectSettings.GlobalizePath("user://"),
                                "gits_telemetry");
        Directory.CreateDirectory(root);
        var stamp = DateTime.Now.ToString("yyyyMMdd-HHmmss", CultureInfo.InvariantCulture);
        _path = Path.Combine(root, $"play-{stamp}.jsonl");
        Log.Info($"[{KleeMod.ModId}] play telemetry ({Feed()} feed) -> {_path}");
        return _path;
    }

    private static string Feed()
    {
        var declared = System.Environment.GetEnvironmentVariable(FeedEnvVar);
        return string.IsNullOrWhiteSpace(declared) ? "human" : declared!.Trim();
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
        public readonly List<(int Round, string Name)> CardsPlayed = new();
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
