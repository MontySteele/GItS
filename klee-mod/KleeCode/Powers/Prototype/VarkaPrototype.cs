using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Powers;

/// <summary>
/// Marker for Varka's CharacterModel, the identity gate every Varka rule and
/// patch asks (Kokomi and Furina have one each for the same reason).
/// </summary>
public interface IVarkaCharacter
{
}

/// <summary>
/// VARKA, THE FOURTH CHARACTER: the switch.
///
/// The Oath rework, <c>review/active/varka-paper-kit-2026-09-28.md</c>, every
/// pick ruled 2026-09-29. The rules as built (sec.3, sec.4):
///
///   * SWIRL is the shared rule (<c>TriggerRules.SwirlPays</c>), unchanged.
///   * OATH, one count per element, counted per card
///     (<see cref="VarkaOathLedger"/>); his CURRENT ELEMENT is the last
///     Knight's, and his cards read only its Oath (<see cref="VarkaOath"/>).
///   * A Swirl he makes pays his current element: Pyro 3 damage to the enemy
///     Swirled, Hydro 3 Block, Cryo 1 Vulnerable, Electro 3 damage to ALL
///     (<see cref="VarkaLaw"/>).
///   * BOREAS'S FANG adds Four Winds' Ascension to his hand the first time
///     each combat he gains Oath (<c>Relics.BoreasFang</c>), and at the start
///     of a run rolls his starter Knight.
///   * CONVERGING WINDS, card-scoped: his Swirls react where they land
///     (<see cref="ConvergingWindsPower"/>, <c>ReactionEffects.SwirlPays</c>).
///
/// NO SWITCH OF HIS OWN (collapsed 2026-10-01, legacy cleanup stage 2): he
/// ships nowhere else, so there is no shipped kit to switch back to. He
/// compiles in every build.
///
/// BUILT IN BOTH ENGINES: the sim twin is <c>tier0/engine/varka_oath.py</c>,
/// live whenever the seat is Varka.
/// </summary>
public static class VarkaPrototype
{
    /// <summary>The character id his cards, his Knights' personal pool and
    /// the companion system name him by.</summary>
    public const string CharacterId = "varka";

    /// <summary>Is this creature Varka?</summary>
    public static bool IsVarka(Creature? creature) =>
        creature?.Player?.Character is IVarkaCharacter;
}

/// <summary>
/// The rule numbers the paper prints (sec.3, pick 1): the Swirl payout of
/// each current element and Stormward Stance's threshold. The badge, the
/// current-element tip and the rules all quote them; a card's own numbers
/// live on its row. Mirrored by value against <c>tier0/engine/varka_oath.py</c>
/// (<c>tools/lint_constant_parity.py</c>).
/// </summary>
public static class VarkaLaw
{
    /// <summary>Pyro current: damage to the enemy he Swirled.</summary>
    public const int SwirlPyroDamage = 3;

    /// <summary>Hydro current: Block per Swirl.</summary>
    public const int SwirlHydroBlock = 3;

    /// <summary>Cryo current: Vulnerable on the enemy he Swirled.</summary>
    public const int SwirlCryoVulnerable = 1;

    /// <summary>Electro current (pick 1, E-AoE): damage to ALL enemies.
    /// </summary>
    public const int SwirlElectroDamageAll = 3;

    /// <summary>Stormward Stance: the current element's Oath it needs.
    /// </summary>
    public const int StormwardOathNeeded = 4;

    /// <summary>Eye of Stormterror (the expansion): the Swirls each turn that
    /// draw.</summary>
    public const int EyeOfStormterrorSwirls = 3;

    /// <summary>Absolute Zero (the expansion): the Weak its Cryo payout adds
    /// beside the Vulnerable.</summary>
    public const int AbsoluteZeroWeak = 1;
}
