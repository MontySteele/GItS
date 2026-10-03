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
/// REPORTS, NEVER GRADES. Nothing but `PlayTelemetry` reads it; the cards
/// that count explosions read <see cref="KleeOverhaulLedger"/>, unchanged.
/// </summary>
public sealed partial class ProtoBombPower
{
    private static object? _explosionCombat;
    private static readonly Dictionary<Player, int> _explosionsByPlayer = new();
    private static readonly Dictionary<Player, int> _mineExplosionsByPlayer = new();

    /// <summary>Charges (Bombs and Mines) this seat set off this combat.</summary>
    public static int ExplosionsThisCombat(ICombatState? combat, Player? player) =>
        Read(_explosionsByPlayer, combat, player);

    /// <summary>The Mines among <see cref="ExplosionsThisCombat"/>.</summary>
    public static int MineExplosionsThisCombat(ICombatState? combat, Player? player) =>
        Read(_mineExplosionsByPlayer, combat, player);

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
    public static void RecordExplosion(Creature? applier, bool isMine) =>
        RecordExplosion(applier?.CombatState, applier?.Player, isMine);

    public static void RecordExplosion(object? combat, Player? player, bool isMine)
    {
        if (combat == null) return;
        if (!ReferenceEquals(combat, _explosionCombat))
        {
            _explosionCombat = combat;
            _explosionsByPlayer.Clear();
            _mineExplosionsByPlayer.Clear();
        }
        if (player == null) return;
        _explosionsByPlayer[player] =
            (_explosionsByPlayer.TryGetValue(player, out var n) ? n : 0) + 1;
        if (!isMine) return;
        _mineExplosionsByPlayer[player] =
            (_mineExplosionsByPlayer.TryGetValue(player, out var m) ? m : 0) + 1;
    }
}
