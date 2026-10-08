using System.Collections.Generic;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;

namespace KleeMod.Powers;

/// <summary>
/// THE PROTOTYPE BOMB'S DETONATION COUNT, for the play telemetry.
///
/// The fight record's `detonations` read <see cref="BombPower"/>'s counter,
/// and the Klee arm's Bombs and Mines are this power, which never touched it:
/// the 2026-10-02 co-op fact-check read 0 detonations across a whole Klee run.
/// So this keeps the same shape <see cref="BombPower.DetonationsThisCombat"/>
/// keeps -- per combat, per placer, cleared when the combat instance changes
/// -- with Mines counted beside the total.
///
/// 2026-10-08, two more counts beside them, so a reader can tell the cause:
/// the charges whose explosion set off an Elemental Reaction (a Bomb's
/// reaction apart from an Attack's, which `reactions_by_type` cannot split),
/// and the Mines that went off answering an enemy's attack (rule 6) rather
/// than a Set off.
///
/// REPORTS, NEVER GRADES. Nothing but `PlayTelemetry` reads it; the cards
/// that count explosions read <see cref="KleeOverhaulLedger"/>, unchanged.
/// </summary>
public sealed partial class ProtoBombPower
{
    private static object? _explosionCombat;
    private static readonly Dictionary<Player, int> _explosionsByPlayer = new();
    private static readonly Dictionary<Player, int> _mineExplosionsByPlayer = new();
    private static readonly Dictionary<Player, int> _reactingExplosionsByPlayer = new();
    private static readonly Dictionary<Player, int> _attackMineExplosionsByPlayer = new();

    /// <summary>Charges (Bombs and Mines) this seat set off this combat.</summary>
    public static int ExplosionsThisCombat(ICombatState? combat, Player? player) =>
        Read(_explosionsByPlayer, combat, player);

    /// <summary>The Mines among <see cref="ExplosionsThisCombat"/>.</summary>
    public static int MineExplosionsThisCombat(ICombatState? combat, Player? player) =>
        Read(_mineExplosionsByPlayer, combat, player);

    /// <summary>The charges among <see cref="ExplosionsThisCombat"/> whose
    /// hit set off an Elemental Reaction.</summary>
    public static int ReactingExplosionsThisCombat(ICombatState? combat, Player? player) =>
        Read(_reactingExplosionsByPlayer, combat, player);

    /// <summary>The Mines among <see cref="MineExplosionsThisCombat"/> that
    /// went off answering an enemy's attack; the rest were Set off.</summary>
    public static int AttackMineExplosionsThisCombat(ICombatState? combat, Player? player) =>
        Read(_attackMineExplosionsByPlayer, combat, player);

    private static int Read(Dictionary<Player, int> table, ICombatState? combat,
                            Player? player)
    {
        if (combat == null || player == null
            || !ReferenceEquals(combat, _explosionCombat)) return 0;
        return table.TryGetValue(player, out var n) ? n : 0;
    }

    /// <summary>One charge went off. The ONE write site; public as the test
    /// seam (an explosion needs a live combat the headless suite cannot
    /// build).</summary>
    public static void RecordExplosion(Creature? applier, bool isMine,
                                       bool reacted = false, bool byAttack = false) =>
        RecordExplosion(applier?.CombatState, applier?.Player, isMine, reacted,
                        byAttack);

    public static void RecordExplosion(object? combat, Player? player, bool isMine,
                                       bool reacted = false, bool byAttack = false)
    {
        if (combat == null) return;
        if (!ReferenceEquals(combat, _explosionCombat))
        {
            _explosionCombat = combat;
            _explosionsByPlayer.Clear();
            _mineExplosionsByPlayer.Clear();
            _reactingExplosionsByPlayer.Clear();
            _attackMineExplosionsByPlayer.Clear();
        }
        if (player == null) return;
        Bump(_explosionsByPlayer, player);
        if (reacted) Bump(_reactingExplosionsByPlayer, player);
        if (!isMine) return;
        Bump(_mineExplosionsByPlayer, player);
        if (byAttack) Bump(_attackMineExplosionsByPlayer, player);
    }

    private static void Bump(Dictionary<Player, int> table, Player player) =>
        table[player] = (table.TryGetValue(player, out var n) ? n : 0) + 1;
}
