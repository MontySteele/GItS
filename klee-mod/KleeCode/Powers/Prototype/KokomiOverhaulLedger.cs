using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Powers;

/// <summary>
/// THE ARM'S MEMORY: the facts a rule asks about that no game object holds.
///
/// DRAFT 6 LEFT IT WITH THREE. Draft 2's ledger carried the pulse's per-combat
/// budget, the did-she-Surge latch, the Surge total for the current play and
/// the enemy count at play start; the ruled brief's sec.6 cuts every rule that
/// read them, so they are gone rather than kept "in case".
///
/// PER COMBAT
///   * <see cref="EntryHp"/> -- the Mend rule: "never above the HP you entered
///     the fight with". Captured once, at combat start, and never moved by
///     anything inside the fight.
///
/// PER TURN
///   * <see cref="CompanionsPlayedThisTurn"/> -- written by The General's
///     Banner's play hook, and it exists for what it becomes at the boundary:
///   * <see cref="CompanionsPlayedLastTurn"/> -- Chain of Command's "Deal 4
///     damage for each Companion card you played LAST turn". A Plan written on
///     turn N is carried out at the top of N+1, so what the clause needs is the
///     count for the turn the player was looking at when they wrote it. The
///     roll below is the only place that number moves, which is what keeps the
///     card and the counter from disagreeing about which turn "last" was.
///
/// PER PLAYER, keyed the way <c>KleeOverhaulLedger</c> is keyed and for the
/// same reason (R205): in co-op the other seat's turn is not hers.
///
/// THE TURN ROLLS ON READ, not on a hook -- the same arrangement
/// <c>KleeOverhaulLedger</c> makes, and here it is belt rather than braces: the
/// marker power IS guaranteed to be on her (rule 1), so a hook would work too.
/// It is done this way anyway so that a rule read from a card body, a power and
/// a relic can never see three different turns.
///
/// NOT A LEAK: the whole table is dropped when the combat instance changes, so
/// it holds at most the current combat's seats.
///
/// PUBLIC, for the reason <c>Diagnostics.MeterLedger</c> gives: KleeTests is a
/// separate assembly and these numbers are what the Mend cap and the Commander
/// loop read.
/// </summary>
public sealed class KokomiOverhaulLedger
{
    private static object? _combat;
    private static readonly Dictionary<Creature, KokomiOverhaulLedger> _byKokomi = new();

    /// <summary>This Kokomi's ledger for this combat, rolled to this round and
    /// created on first ask. Creation CAPTURES HER ENTRY HP, so a ledger that
    /// was never explicitly opened still caps her Mends at something honest
    /// rather than at zero.</summary>
    public static KokomiOverhaulLedger For(Creature kokomi)
    {
        var combat = (object?)kokomi.CombatState;
        if (!ReferenceEquals(_combat, combat))
        {
            _combat = combat;
            _byKokomi.Clear();
        }
        if (!_byKokomi.TryGetValue(kokomi, out var ledger))
        {
            ledger = new KokomiOverhaulLedger { EntryHp = (int)kokomi.CurrentHp };
            _byKokomi[kokomi] = ledger;
        }
        ledger.RollTo(kokomi.CombatState?.RoundNumber ?? 0);
        return ledger;
    }

    /// <summary>Test seam: forget everything. The mod never calls it.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _byKokomi.Clear();
    }

    /// <summary>
    /// The combat opens: capture her entry HP FROM HERE rather than from the
    /// lazy creation above, so the number is the one she walked in with even
    /// when the first read happens after she has taken a hit.
    /// </summary>
    public static void OpenCombat(Creature kokomi)
    {
        For(kokomi).EntryHp = (int)kokomi.CurrentHp;
    }

    /// <summary>The HP she walked in with. Every Mend's ceiling.</summary>
    public int EntryHp { get; private set; }

    /// <summary>Companion cards played this turn.</summary>
    public int CompanionsPlayedThisTurn { get; private set; }

    /// <summary>Companion cards played on the turn before this one -- what
    /// Chain of Command's Plan reads when it is carried out.</summary>
    public int CompanionsPlayedLastTurn { get; private set; }

    private int _round = -1;

    /// <summary>One Companion play finished.</summary>
    public void NoteCompanionPlayed() => CompanionsPlayedThisTurn++;

    /// <summary>
    /// Roll the per-turn state to <paramref name="round"/>. Public to the pins
    /// so a turn boundary can be exercised without a combat.
    ///
    /// THE HANDOVER IS THE WHOLE POINT: this turn's count becomes last turn's,
    /// in the one place that can be true, so a Plan carried out at the top of a
    /// turn reads the turn that just ended.
    /// </summary>
    public void RollTo(int round)
    {
        if (round == _round) return;
        // A ledger created mid-combat has never seen the previous turn, so
        // there is nothing to hand over on its FIRST roll -- and handing over a
        // zero it never counted is exactly right.
        CompanionsPlayedLastTurn = CompanionsPlayedThisTurn;
        CompanionsPlayedThisTurn = 0;
        _round = round;
    }
}
