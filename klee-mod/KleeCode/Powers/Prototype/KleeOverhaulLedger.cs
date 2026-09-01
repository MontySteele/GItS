using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Powers.Prototype;

/// <summary>
/// RULE 7's TWO COUNTERS, and the two memories the cards that read them need.
///
/// The slice's build list asks for exactly this: "Two counters, both per turn:
/// Bombs that went off; Bombs that reacted. Grounded reads last turn's first
/// counter." Three cards read the first (Run Away!, Ammo Scavenging, and
/// Grounded shifted by a turn) and three read the second (Sizzle, Perfect
/// Timing, Catalytic Converter).
///
/// TWO MORE LIVE HERE BECAUSE THEY ARE THE SAME KIND OF FACT, scoped to a PLAY
/// rather than a turn:
///   * <see cref="SizeSetOffThisPlay"/> -- Big Badda Boom's "damage equal to
///     the total size of the Bombs set off". It has to be remembered, because
///     the pile is gone by the time the card's second clause asks.
///   * <see cref="TakeDoubling"/> -- The Big One's "Bombs set off this way deal
///     double". Armed by the card and spent BY the Set off, so "this way" means
///     this card rather than the rest of the turn.
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
/// </summary>
internal sealed class KleeOverhaulLedger
{
    private static object? _combat;
    private static readonly Dictionary<Creature, KleeOverhaulLedger> _byKlee = new();

    /// <summary>This Klee's ledger for this combat, rolled to this round and
    /// created on first ask.</summary>
    internal static KleeOverhaulLedger For(Creature klee)
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
    internal static void ResetAll()
    {
        _combat = null;
        _byKlee.Clear();
    }

    /// <summary>Counter one: Bombs that went off this turn.</summary>
    internal int SetOffThisTurn { get; private set; }

    /// <summary>Counter two: Bombs whose explosion caused a reaction this turn.</summary>
    internal int ReactedThisTurn { get; private set; }

    /// <summary>Counter one, as it stood at the end of last turn. Grounded's
    /// whole read: "if none of your Bombs went off LAST turn".</summary>
    internal int SetOffLastTurn { get; private set; }

    /// <summary>Total SIZE set off since the current card play began.</summary>
    internal int SizeSetOffThisPlay { get; private set; }

    private bool _doubleNextSetOff;
    private int _round = -1;

    /// <summary>One explosion landed, for <paramref name="size"/>. THE ONE
    /// write site for both counters and the play memory, so the three can never
    /// disagree about what an explosion is.</summary>
    internal void NoteExplosion(bool reacted, int size)
    {
        SetOffThisTurn++;
        SizeSetOffThisPlay += size;
        if (reacted) ReactedThisTurn++;
    }

    /// <summary>A card play begins: the play-scoped size memory starts empty.
    /// Emitted at the top of the body of any card that reads it.</summary>
    internal void BeginPlay() => SizeSetOffThisPlay = 0;

    /// <summary>The Big One arms this; the next Set off spends it.</summary>
    internal void ArmDoubling() => _doubleNextSetOff = true;

    /// <summary>Read and clear. The Set off that consumes it is "this way".</summary>
    internal bool TakeDoubling()
    {
        var armed = _doubleNextSetOff;
        _doubleNextSetOff = false;
        return armed;
    }

    /// <summary>Read without clearing: a Mine answering an enemy attack must
    /// not eat the doubling a card armed for its own Set off.</summary>
    internal bool PeekDoubling() => _doubleNextSetOff;

    /// <summary>Roll the per-turn counters to <paramref name="round"/>. Public
    /// to the pins so a turn boundary can be exercised without a combat.</summary>
    internal void RollTo(int round)
    {
        if (round == _round) return;
        SetOffLastTurn = round == _round + 1 ? SetOffThisTurn : 0;
        SetOffThisTurn = 0;
        ReactedThisTurn = 0;
        SizeSetOffThisPlay = 0;
        _doubleNextSetOff = false;
        _round = round;
    }
}
