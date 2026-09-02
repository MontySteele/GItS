using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Powers;

/// <summary>
/// THE ARM'S MEMORY: the four facts a rule asks about that no game object
/// holds, plus her entry HP, which is the cap on every Mend in the combat.
///
/// PER COMBAT
///   * <see cref="EntryHp"/> -- rule 4 and the Mend rule: "never above the HP
///     she entered the combat with" (brief sec.14: the default is walked in
///     with, "because it makes rest sites hers"). Captured once, at combat
///     start, and never moved by anything inside the fight.
///   * <see cref="PulseSpent"/> -- rule 4's per-combat budget, held here and
///     SHOWN on the relic. It counts HP the pulse actually restored, which is
///     the brief's own arithmetic: script A's turn 1 pulse "would Mend 2, but
///     she is at 80, so nothing", and after three effective pulses "the pulse
///     paid 6 of its 8". An ineffective pulse spends nothing.
///
/// PER TURN
///   * <see cref="SurgedThisTurn"/> -- rule 4's condition, and the whole of the
///     hold-or-surge decision: the pulse pays only on a turn she did NOT Surge.
///   * <see cref="CompanionsPlayedThisTurn"/> -- The General's Banner's "the
///     FIRST Companion you play each turn".
///
/// PER PLAY
///   * <see cref="SurgeDamageThisPlay"/> -- Undertow's "Block equal to half the
///     damage dealt". It has to be remembered, because the Tide is gone by the
///     time the card's second clause asks.
///   * <see cref="EnemiesAtPlayStart"/> -- Deep Current's "Tide +1 per enemy
///     hit". Snapshotted at the TOP of the body, before the AoE resolves, so an
///     enemy the AoE killed still counts as hit. See
///     <see cref="BeginPlay"/>.
///
/// PER PLAYER, keyed the way <c>KleeOverhaulLedger</c> is keyed and for the
/// same reason (R205): in co-op the other seat's turn is not hers, and a shared
/// integer would let one Kokomi's Surge cancel the other's pulse.
///
/// THE TURN ROLLS ON READ, not on a hook -- the same arrangement
/// <c>KleeOverhaulLedger</c> makes, and here it is belt rather than braces: the
/// jellyfish IS guaranteed to be on her (rule 1), so a hook would work too. It
/// is done this way anyway so that a rule read from a card body, a power and a
/// relic can never see three different turns.
///
/// NOT A LEAK: the whole table is dropped when the combat instance changes, so
/// it holds at most the current combat's seats.
///
/// PUBLIC, for the reason <c>Diagnostics.MeterLedger</c> gives: KleeTests is a
/// separate assembly and these six numbers are what the pulse, the Rare, two
/// payoffs and the Commander's Rare all read.
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

    /// <summary>HP the pulse has restored this combat. Rule 4's budget is
    /// measured against this.</summary>
    public int PulseSpent { get; private set; }

    /// <summary>Rule 4's condition: has she Surged this turn?</summary>
    public bool SurgedThisTurn { get; private set; }

    /// <summary>Companion cards played this turn -- The General's Banner reads
    /// zero to mean "this is the first".</summary>
    public int CompanionsPlayedThisTurn { get; private set; }

    /// <summary>Damage the Surges in the current card play dealt.</summary>
    public int SurgeDamageThisPlay { get; private set; }

    /// <summary>Living enemies when the current card play began.</summary>
    public int EnemiesAtPlayStart { get; private set; }

    private int _round = -1;

    /// <summary>One Surge landed, for <paramref name="damage"/>. THE ONE write
    /// site for the turn latch and the play total, so the pulse and Undertow
    /// cannot disagree about what a Surge was.</summary>
    public void NoteSurge(int damage)
    {
        SurgedThisTurn = true;
        SurgeDamageThisPlay += damage;
    }

    /// <summary>The pulse restored <paramref name="hp"/>. Only what LANDED, so
    /// a pulse at full HP spends nothing.</summary>
    public void NotePulse(int hp) => PulseSpent += hp;

    /// <summary>One Companion play finished.</summary>
    public void NoteCompanionPlayed() => CompanionsPlayedThisTurn++;

    /// <summary>
    /// A card play begins: the play-scoped memories start clean and the enemy
    /// count is snapshotted. Emitted at the top of the body of any card that
    /// reads one of them.
    /// </summary>
    public void BeginPlay(int livingEnemies)
    {
        SurgeDamageThisPlay = 0;
        EnemiesAtPlayStart = livingEnemies;
    }

    /// <summary>Roll the per-turn state to <paramref name="round"/>. Public to
    /// the pins so a turn boundary can be exercised without a combat.</summary>
    public void RollTo(int round)
    {
        if (round == _round) return;
        SurgedThisTurn = false;
        CompanionsPlayedThisTurn = 0;
        SurgeDamageThisPlay = 0;
        EnemiesAtPlayStart = 0;
        _round = round;
    }
}
