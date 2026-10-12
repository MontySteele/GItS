using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Logging;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// RULE 7's TWO COUNTERS, and the two memories the cards that read them need.
///
/// The slice's build list asks for exactly this: "Two counters, both per turn:
/// Bombs that went off; Bombs that reacted. Grounded reads last turn's first
/// counter." Three cards read the first (Run Away!, Ammo Scavenging, and
/// Grounded shifted by a turn) and two read the second (Sizzle and Perfect
/// Timing).
///
/// A THIRD COUNTER JOINED THEM AT R244 and it is the same kind of fact:
/// <see cref="CompanionPlayedThisTurn"/>, which Coven Errand reads (a Hexerei
/// count until R276). It is here rather than on the card so that it and
/// <c>WitchesCirclePower</c> cannot disagree about what counts.
///
/// TWO MORE LIVE HERE BECAUSE THEY ARE THE SAME KIND OF FACT, scoped to a PLAY
/// rather than a turn:
///   * <see cref="DamageSetOffThisPlay"/> -- Big Badda Boom's "hit again for
///     the damage the Bombs dealt". It has to be remembered, because the pile
///     is gone by the time the card's second clause asks. `EB-270` renamed it
///     from `SizeSetOffThisPlay` and moved what is added to it: it used to bank
///     the charge SIZES, while the card's face (`EB-291`) says DAMAGE, and the
///     two part company the moment a modifier applies -- under Weak a pair of
///     8+9 Bombs deals 12 and banked 17. It now banks what
///     <c>ElementalHit.Deal</c> returned, so the bonus line, the badge and the
///     tooltip are three readings of one number.
///   * <see cref="TakeMultiplier"/> -- The Big One's "Set off for quadruple
///     damage" (R243, [USER]: "move The Big One to 4x with no flat number";
///     the row carries the number). Armed by the card and spent BY the Set
///     off, so "this way" means this card rather than the rest of the turn.
///
/// PER PLAYER, keyed the way <c>BombPower</c>'s detonation counters are keyed
/// and for the same reason (D2, and R205 behind it): in co-op the other Klee's
/// explosions are hers, and a shared integer would pay this Klee's Run Away!
/// for a turn she spent doing nothing. Keyed per Creature because that is what
/// every call site already holds.
///
/// THE TURN ROLLS ON READ, not on a hook, and that is deliberate. Rule 7 says
/// nothing fires by itself, so under this arm there is no power guaranteed to
/// be on Klee and no hook guaranteed to fire -- a turn-boundary callback would
/// have to be hung off something that might not exist. The combat's round
/// number is already the boundary, so <see cref="For"/> compares it to the
/// stamp it last saw and rolls when it has moved. Self-correcting: a jump of
/// more than one round means Klee had no turn in between, and last turn's
/// counter is then honestly zero.
///
/// NOT A LEAK: the whole table is dropped when the combat instance changes, so
/// it holds at most the current combat's seats.
///
/// PUBLIC, for the reason <c>Diagnostics.MeterLedger</c> gives: KleeTests is a
/// separate assembly and these counters are what three defence cards and two
/// payoffs read, so an IL-shape assertion standing in for the arithmetic would
/// be checking the wrong thing.
/// </summary>
public sealed class KleeOverhaulLedger
{
    private static object? _combat;
    private static readonly Dictionary<Creature, KleeOverhaulLedger> _byKlee = new();

    /// <summary>This Klee's ledger for this combat, rolled to this round and
    /// created on first ask.</summary>
    public static KleeOverhaulLedger For(Creature klee)
    {
        var combat = (object?)klee.CombatState;
        if (!ReferenceEquals(_combat, combat))
        {
            _combat = combat;
            _byKlee.Clear();
        }
        if (!_byKlee.TryGetValue(klee, out var ledger))
        {
            ledger = new KleeOverhaulLedger();
            _byKlee[klee] = ledger;
        }
        ledger.RollTo(klee.CombatState?.RoundNumber ?? 0);
        return ledger;
    }

    /// <summary>Test seam: forget everything. The mod never calls it.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _byKlee.Clear();
    }

    /// <summary>
    /// `EB-318` / `EB-450`: THE ARM'S LINE LOG, and this arm had none.
    ///
    /// THE TWO FINDS ARE ONE GAP. A detonation of `Jumpy Dumpty` places a Mine
    /// on ALL enemies and the round-7 seat could only confirm ONE had happened
    /// by watching a Spark tick over; a Mine firing into a Cryo aura on the
    /// enemy's turn moved an enemy 12 where the badge printed 7, with the
    /// reaction named nowhere (r13 f6). Both are the same thing missing: the
    /// board says what IS, never what just happened, and the two moments that
    /// matter here happen while no card is in front of the player.
    ///
    /// LINES AND NOT COUNTERS. A counter nothing reads is dead weight (rule 7's
    /// two exist because six cards read them); what these two rows ask for is a
    /// SENTENCE, in the player's own vocabulary, that a run record carries. So
    /// each is written once, at the site that knows it, and mirrored to
    /// `godot.log` -- the channel this repo already reads a live run's truth
    /// out of -- so a round's record can quote it.
    ///
    /// PER COMBAT AND NOT PER TURN: <see cref="RollTo"/> deliberately does not
    /// clear this. A log that forgot the last turn could not answer the
    /// question either seat was asking, which was about a beat that had already
    /// passed. Capped at <see cref="LineCap"/> so a long fight cannot grow it
    /// without bound, oldest dropped first, and dropped whole with the rest of
    /// the table when the combat changes.
    ///
    /// WHAT IT IS NOT: a wire route. The bridge answers a play BEFORE the card
    /// resolves (`McpMod.Actions.ExecutePlayCard` enqueues and returns), so
    /// there is no post-resolution channel to the blind page today, and
    /// `GitsMeterLedger`'s own header records why a developer-vocabulary
    /// ledger is kept off a grading surface. The page half of both rows is the
    /// board it already reads.
    /// </summary>
    public IReadOnlyList<string> Lines => _lines;

    private const int LineCap = 200;

    private readonly List<string> _lines = new();

    /// <summary>Write one line. The ONE door, so every line reaches the log in
    /// the same shape and a pin can read them back without a game.</summary>
    public void NoteLine(string line)
    {
        if (string.IsNullOrEmpty(line)) return;
        _lines.Add(line);
        if (_lines.Count > LineCap) _lines.RemoveAt(0);
        Log.Info($"[{KleeMod.ModId}] {line}");
    }

    /// <summary>Counter one: Bombs that went off this turn.</summary>
    public int SetOffThisTurn { get; private set; }

    /// <summary>Counter two: Bombs whose explosion caused a reaction this turn.</summary>
    public int ReactedThisTurn { get; private set; }

    /// <summary>Counter one, as it stood at the end of last turn. Grounded's
    /// whole read: "if none of your Bombs went off LAST turn".</summary>
    public int SetOffLastTurn { get; private set; }

    /// <summary>
    /// Counter three (R244, R276): Companion cards played this turn. Coven
    /// Errand's whole read -- "if you played a Companion card this turn, place
    /// it on ALL enemies instead".
    ///
    /// IT LIVES HERE rather than on the card, for rule 7's two counters'
    /// reason: it is written at the ONE site such a play is noticed
    /// (<see cref="NoteCompanionPlayed"/>, called from the arm's standing
    /// card-play listener), so the card and <c>WitchesCirclePower</c> beside
    /// it cannot disagree about what counts. What COUNTS is
    /// <c>CompanionHexerei.CountsAsCompanion</c>'s answer and nobody else's,
    /// which is what lets Alice's Introduction Magic widen it for a turn
    /// without either reader learning about her.
    /// </summary>
    public int CompanionPlayedThisTurn { get; private set; }

    /// <summary>Total DAMAGE the explosions since the current card play began
    /// actually dealt -- post-Strength, post-Weak, post-reaction,
    /// post-Vulnerable (`EB-270`), which is what Big Badda Boom's face
    /// promises.</summary>
    public int DamageSetOffThisPlay { get; private set; }

    /// <summary>
    /// What Big Badda Boom's second clause HITS FOR before the target's own
    /// terms: <see cref="DamageSetOffThisPlay"/> with each explosion's
    /// Vulnerable taken back out (the Klee later-act seats, 2026-09-26, the
    /// lane-2 full run). The clause is a card Attack, so the game's pipeline
    /// applies the target's Vulnerable to it -- and it was being handed a
    /// number that had already paid it, so a Vulnerable enemy paid it twice
    /// (the Terror Eel's "12, 7, 18, 28": the Bombs landed 19 and the echo 28).
    /// Now the Vulnerable is paid ONCE, by the echo, and the number the echo
    /// lands equals what the Bombs dealt. Block the Bombs removed still counts,
    /// as it always did.
    ///
    /// ROUNDED UP at the sixth place: <c>dealt / 1.5</c> repeats, and the
    /// game truncates the product, so a sum that fell a hair short of an
    /// integer would lose a point the Bombs really dealt.
    /// </summary>
    public decimal SetOffEchoBaseThisPlay { get; private set; }

    private int _setOffMultiplier = 1;
    private int _round = -1;

    /// <summary>One explosion landed, for <paramref name="damageDealt"/> --
    /// the number <c>ElementalHit.Deal</c> returned, never the charge's size.
    /// THE ONE write site for both counters and the play memory, so the three
    /// can never disagree about what an explosion is.</summary>
    public void NoteExplosion(bool reacted, int damageDealt,
                              bool vulnerablePaid = false)
    {
        SetOffThisTurn++;
        DamageSetOffThisPlay += damageDealt;
        SetOffEchoBaseThisPlay += EchoBase(damageDealt, vulnerablePaid);
        if (reacted) ReactedThisTurn++;
    }

    /// <summary>One explosion's share of <see cref="SetOffEchoBaseThisPlay"/>:
    /// what it dealt, with the target's Vulnerable taken back out where it
    /// paid one. PURE, and the arithmetic the pins read.</summary>
    public static decimal EchoBase(int damageDealt, bool vulnerablePaid)
    {
        if (!vulnerablePaid) return damageDealt;
        var raw = damageDealt / ReactionConstants.VulnerableTakenMult;
        return decimal.Ceiling(raw * 1_000_000m) / 1_000_000m;
    }

    /// <summary>A card that counts as a Companion was played (R244, R276).
    /// The ONE write site, for <see cref="NoteExplosion"/>'s reason.</summary>
    public void NoteCompanionPlayed() => CompanionPlayedThisTurn++;

    /// <summary>
    /// THE SCALING PASS (klee-next, 2026-10-05), Witch's Homework's ruling:
    /// "It grows at most once a combat, whatever replays it." Keyed by the
    /// DECK card the play came from (<c>DeckVersion</c>, or the card itself
    /// when it has none), so a replay of the same card, a second Bomb from it
    /// and a merged mark all find the latch spent. Per combat, because the
    /// ledger is (<see cref="For"/>).
    /// </summary>
    private readonly HashSet<CardModel> _homeworkGrown =
        new(ReferenceEqualityComparer.Instance);

    /// <summary>True the FIRST time <paramref name="deckCard"/> is asked in
    /// this combat, false after.</summary>
    public bool TakeHomework(CardModel deckCard) => _homeworkGrown.Add(deckCard);

    private bool _aftershockSpent;

    /// <summary>
    /// R276, Aftershock's once-per-turn latch: true the FIRST time it is asked
    /// in a turn, false after, reset with the turn. On the ledger rather than
    /// on the Power so "each turn" is the same boundary every counter here
    /// rolls on.
    /// </summary>
    public bool TakeAftershock()
    {
        if (_aftershockSpent) return false;
        _aftershockSpent = true;
        return true;
    }

    private bool _sparksForEveryoneSpent;

    /// <summary>
    /// THE CO-OP SET, SECOND BATCH, <i>Sparks for Everyone</i>'s
    /// once-per-turn latch ("The first time each turn one of your Bombs goes
    /// off"): true the FIRST time it is asked in a turn, false after, reset
    /// with the turn. Aftershock's latch, and on the ledger for its reason --
    /// "each turn" is the one boundary every counter here rolls on.
    /// </summary>
    public bool TakeSparksForEveryone()
    {
        if (_sparksForEveryoneSpent) return false;
        _sparksForEveryoneSpent = true;
        return true;
    }

    // ---- the arm's own relics (review/active/relics-potions-klee-furina-2026-09-27.md) ----

    private bool _dodocoTalesSpent;

    /// <summary>Dodoco Tales, repaired for the arm: "The first time each
    /// turn, gain 2 instead." True the FIRST time it is asked in a turn (a
    /// round, the ledger's own clock), whatever set the Bomb off.</summary>
    public bool TakeDodocoTales()
    {
        if (_dodocoTalesSpent) return false;
        _dodocoTalesSpent = true;
        return true;
    }

    private bool _teapotSpent;

    /// <summary>Alice's Teapot: "The first Bomb that goes off each turn".
    /// True the FIRST time it is asked in a round (her turn plus the enemy
    /// turn after it), so a Mine going off on the enemies' turn takes it
    /// when her turn left it unspent.
    /// </summary>
    public bool TakeTeapot()
    {
        if (_teapotSpent) return false;
        _teapotSpent = true;
        return true;
    }

    /// <summary>Has the Teapot fired this turn? A read that spends nothing,
    /// for the badge.</summary>
    public bool TeapotSpent => _teapotSpent;

    private bool _turnStartPlacementsDone;

    /// <summary>
    /// R276, the start-of-turn placements' latch: true the FIRST time it is
    /// asked in a turn. Sparks 'n' Splash, Klee's Secret Base and Dodoco share
    /// one <c>AfterPlayerTurnStart</c> broadcast with no guaranteed relative
    /// order, and each reads or writes the board the others touch -- so
    /// whichever is called first runs ALL of them, in one fixed order
    /// (<c>KleeExpansion.RunTurnStartPlacements</c>), and the others find the
    /// latch taken.
    /// </summary>
    public bool TakeTurnStartPlacements()
    {
        if (_turnStartPlacementsDone) return false;
        _turnStartPlacementsDone = true;
        return true;
    }

    /// <summary>A card play begins: the play-scoped size memory starts empty.
    /// Emitted at the top of the body of any card that reads it.</summary>
    public void BeginPlay()
    {
        DamageSetOffThisPlay = 0;
        SetOffEchoBaseThisPlay = 0m;
    }

    /// <summary>The Big One arms this with the row's own number; the next Set
    /// off spends it. An int rather than the flag it replaced: R243's card
    /// audit ruling made the multiplier the card's ("4x with no flat
    /// number"), so the engine multiplies by whatever the row says.</summary>
    public void ArmMultiplier(int multiplier) => _setOffMultiplier = multiplier;

    /// <summary>Read and clear (to 1). The Set off that consumes it is "this way".</summary>
    public int TakeMultiplier()
    {
        var armed = _setOffMultiplier;
        _setOffMultiplier = 1;
        return armed;
    }

    /// <summary>Read without clearing: a Mine answering an enemy attack must
    /// not eat the multiplier a card armed for its own Set off.</summary>
    public int PeekMultiplier() => _setOffMultiplier;

    /// <summary>
    /// `EB-749` (R271 sec.5.1). GROUNDED'S WHOLE READ: did a <i>Set off</i>
    /// CARD resolve this turn.
    ///
    /// A COUNT OF CARDS AND NOT OF EXPLOSIONS, which is the whole of why it is
    /// not <see cref="SetOffThisTurn"/>. The ruled condition excepts two things
    /// by name and both fall out of this site rather than out of a special
    /// case: a MINE answering an enemy attack passes no card (the same
    /// <c>null</c> Once More! declines), and SPARKS 'N' SPLASH is a Power's
    /// end-of-turn hit that never reaches a Set off entry point at all. Neither
    /// switches Grounded off.
    /// </summary>
    public int SetOffCardsThisTurn { get; private set; }

    /// <summary><see cref="SetOffCardsThisTurn"/> as it stood at the end of
    /// last turn -- the number Grounded's condition actually asks for. Rolled
    /// on the same round stamp as every counter above, so a SKIPPED round
    /// reports an honest zero rather than a stale count.</summary>
    public int SetOffCardsLastTurn { get; private set; }

    /// <summary>The ONE write site, for <see cref="NoteExplosion"/>'s
    /// reason.</summary>
    public void NoteSetOffCardPlayed(CardModel? card)
    {
        if (card == null) return;
        SetOffCardsThisTurn++;
    }

    /// <summary>Roll the per-turn counters to <paramref name="round"/>. Public
    /// to the pins so a turn boundary can be exercised without a combat.</summary>
    public void RollTo(int round)
    {
        if (round == _round) return;
        SetOffLastTurn = round == _round + 1 ? SetOffThisTurn : 0;
        SetOffCardsLastTurn =
            round == _round + 1 ? SetOffCardsThisTurn : 0;
        SetOffCardsThisTurn = 0;
        SetOffThisTurn = 0;
        ReactedThisTurn = 0;
        CompanionPlayedThisTurn = 0;
        _aftershockSpent = false;
        _sparksForEveryoneSpent = false;
        _dodocoTalesSpent = false;
        _teapotSpent = false;
        _turnStartPlacementsDone = false;
        DamageSetOffThisPlay = 0;
        SetOffEchoBaseThisPlay = 0m;
        _setOffMultiplier = 1;
        _round = round;
    }
}
