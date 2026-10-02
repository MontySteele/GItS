#nullable enable

using System.Linq;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Cards;

/// <summary>
/// 2026-10-01 (seat round): VIGOR ON A PER-TARGET ALL-ENEMIES ATTACK.
/// Crashing Waves with Vigor 8 previewed "Deal 16 damage to ALL enemies" and
/// landed 16/8/8/8. The base game's <c>VigorPower</c> pays every target of
/// the ONE attack command it first sees (a base AoE is one command), then
/// removes itself; a generated card whose ALL-enemies attack carries a
/// per-target bonus (an aura, a debuff) issues one command per enemy, so
/// Vigor paid the first and was gone for the rest.
///
/// The carry follows the base game: read Vigor before the sweep, let the
/// first command take it the base game's way, and add the same amount to
/// every later command of the sweep. The preview (the card's own DamageVar,
/// which Vigor already modifies) is then the truth for every enemy.
/// </summary>
public sealed class AoeVigor
{
    private readonly int _amount;
    private bool _first = true;

    private AoeVigor(int amount) => _amount = amount;

    /// <summary>Read the attacker's Vigor before the sweep's first hit.</summary>
    public static AoeVigor Begin(Creature? attacker) =>
        new(attacker == null
            ? 0
            : (int)attacker.Powers.OfType<VigorPower>().Sum(p => p.Amount));

    /// <summary>What this hit adds: 0 for the first (Vigor pays it), the
    /// Vigor read at the start for each one after.</summary>
    public int Next()
    {
        if (_first)
        {
            _first = false;
            return 0;
        }
        return _amount;
    }
}
