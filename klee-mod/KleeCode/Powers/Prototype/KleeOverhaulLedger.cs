using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Logging;
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

    private int _setOffMultiplier = 1;
    private int _round = -1;

    /// <summary>One explosion landed, for <paramref name="damageDealt"/> --
    /// the number <c>ElementalHit.Deal</c> returned, never the charge's size.
    /// THE ONE write site for both counters and the play memory, so the three
    /// can never disagree about what an explosion is.</summary>
    public void NoteExplosion(bool reacted, int damageDealt)
    {
        SetOffThisTurn++;
        DamageSetOffThisPlay += damageDealt;
        if (reacted) ReactedThisTurn++;
    }

    /// <summary>A card that counts as a Companion was played (R244, R276).
    /// The ONE write site, for <see cref="NoteExplosion"/>'s reason.</summary>
    public void NoteCompanionPlayed() => CompanionPlayedThisTurn++;

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
    public void BeginPlay() => DamageSetOffThisPlay = 0;

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
    /// ONCE MORE!'s WHOLE READ (`EB-732`): the last card this combat whose
    /// <i>Set off</i> resolved.
    ///
    /// PER COMBAT AND DELIBERATELY NOT ROLLED by <see cref="RollTo"/>, unlike
    /// every counter above it: the face says "this combat". It is dropped with
    /// the rest of the table when the combat instance changes, which is where
    /// its lifetime ends.
    ///
    /// THE CARD AND NOT ITS MODEL ID, because the card the player takes back
    /// has to be the one that went to the discard pile -- two copies of Ka-pow!
    /// are two cards and only one of them was played.
    ///
    /// WRITTEN AT THE OP SITE, above the early returns of the three
    /// card-facing entry points (<c>ProtoBombPower.SetOffAimed</c>,
    /// <c>SetOffAll</c>, <c>SetOffRandom</c>) rather than where a charge goes
    /// off: a Set off played into an empty board is still the last Set off card
    /// you played. A Mine passes no card and is declined. Sim twin:
    /// <c>state.ko_last_set_off_card</c>, written by
    /// <c>klee_overhaul.note_set_off_card</c> from <c>effects._op_set_off</c>.
    /// </summary>
    public CardModel? LastSetOffCard { get; private set; }

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
        LastSetOffCard = card;
        SetOffCardsThisTurn++;
    }

    /// <summary>
    /// ONCE MORE! resolved: the last Set off card comes back out of the
    /// DISCARD pile, or nothing happens.
    ///
    /// DETERMINISTIC AND SILENT, with no selection screen: there is one answer
    /// and the player already knows it. NOTHING HAPPENS AND THE SPARKS ARE
    /// STILL SPENT when the card is not in the discard pile -- exhausted, still
    /// in hand, or none played yet -- because a Spark price is a cost line and
    /// a cost line is paid before the body runs.
    ///
    /// THE PILE TEST IS EXPLICIT, and <c>CardPileCmd.Add</c> would not make it:
    /// that command takes a card out of wherever it is, so calling it on a card
    /// still in hand would silently be a no-op and on an exhausted card would
    /// be a resurrection the face does not promise.
    ///
    /// TOP of the hand, <c>KokomiPlan.Replay</c>'s position and for its reason:
    /// the card handed back is the one the player is looking at.
    /// </summary>
    public static async Task ReturnLastSetOff(Player? player)
    {
        var klee = player?.Creature;
        if (klee == null) return;
        var card = For(klee).LastSetOffCard;
        if (card == null) return;
        var pile = CardPile.Get(PileType.Discard, player);
        if (pile == null || !pile.Cards.Contains(card)) return;
        await CardPileCmd.Add(card, PileType.Hand, CardPilePosition.Top);
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
        _turnStartPlacementsDone = false;
        DamageSetOffThisPlay = 0;
        _setOffMultiplier = 1;
        _round = round;
    }
}
