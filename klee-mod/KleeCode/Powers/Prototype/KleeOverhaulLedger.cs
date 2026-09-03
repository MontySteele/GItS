using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Powers;

/// <summary>
/// RULE 7's TWO COUNTERS, and the two memories the cards that read them need.
///
/// The slice's build list asks for exactly this: "Two counters, both per turn:
/// Bombs that went off; Bombs that reacted. Grounded reads last turn's first
/// counter." Three cards read the first (Run Away!, Ammo Scavenging, and
/// Grounded shifted by a turn) and three read the second (Sizzle, Perfect
/// Timing, Catalytic Converter).
///
/// A THIRD COUNTER JOINED THEM AT R244 and it is the same kind of fact one
/// family over: <see cref="HexereiPlayedThisTurn"/>, which Coven Errand reads.
/// It is here rather than on the card so that it and <c>WitchesCirclePower</c>
/// cannot disagree about what a Hexerei card is.
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

    /// <summary>Counter one: Bombs that went off this turn.</summary>
    public int SetOffThisTurn { get; private set; }

    /// <summary>Counter two: Bombs whose explosion caused a reaction this turn.</summary>
    public int ReactedThisTurn { get; private set; }

    /// <summary>Counter one, as it stood at the end of last turn. Grounded's
    /// whole read: "if none of your Bombs went off LAST turn".</summary>
    public int SetOffLastTurn { get; private set; }

    /// <summary>
    /// Counter three (R244): Hexerei cards played this turn. Coven Errand's
    /// whole read -- "if you played a Hexerei card this turn, place it on ALL
    /// enemies instead".
    ///
    /// IT LIVES HERE rather than on the card, for rule 7's two counters'
    /// reason: it is written at the ONE site a Hexerei play is noticed
    /// (<see cref="NoteHexereiPlayed"/>, called from the arm's standing
    /// card-play listener), so the card and <c>WitchesCirclePower</c> beside
    /// it cannot disagree about what a Hexerei card is. What COUNTS as one is
    /// <c>CompanionHexerei.IsHexerei</c>'s answer and nobody else's, which is
    /// what lets Alice's Introduction Magic widen the family for a turn without
    /// either reader learning about her.
    /// </summary>
    public int HexereiPlayedThisTurn { get; private set; }

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

    /// <summary>A Hexerei card was played (R244). The ONE write site, for
    /// <see cref="NoteExplosion"/>'s reason.</summary>
    public void NoteHexereiPlayed() => HexereiPlayedThisTurn++;

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

    /// <summary>Roll the per-turn counters to <paramref name="round"/>. Public
    /// to the pins so a turn boundary can be exercised without a combat.</summary>
    public void RollTo(int round)
    {
        if (round == _round) return;
        SetOffLastTurn = round == _round + 1 ? SetOffThisTurn : 0;
        SetOffThisTurn = 0;
        ReactedThisTurn = 0;
        HexereiPlayedThisTurn = 0;
        DamageSetOffThisPlay = 0;
        _setOffMultiplier = 1;
        _round = round;
    }
}
