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
/// The paper kit <c>review/active/varka-paper-kit-2026-09-28.md</c> sec.10,
/// "Prototype, batch one"; [USER], 2026-09-29: "You're good to go on building
/// the Varka prototype!". The rules as built (sec.10.1):
///
///   * SWIRL is the shared rule (<c>TriggerRules.SwirlPays</c>), unchanged.
///   * ABSORB is his cards' keyword (<c>IAbsorbCard</c>): on a fresh aura it
///     takes the aura off that enemy and gives its Wind; no spread and no
///     flat 2. Holding that Wind already, the hit Swirls instead. No fresh
///     aura, only the card's damage (<see cref="VarkaAbsorb"/>).
///   * WINDS, one per element, for the rest of the fight, each paid on every
///     Swirl he makes (<see cref="VarkaWinds"/>).
///   * BOREAS'S FANG, the starting relic: once each turn, the first non-Anemo
///     Attack that hits a fresh aura Absorbs it (<c>Relics.BoreasFang</c>).
///   * CONVERGING WINDS, card-scoped: his Swirls react where they land
///     (<see cref="ConvergingWindsPower"/>, <c>ReactionEffects.SwirlPays</c>).
///
/// TWO SWITCHES, the arms' arrangement. <c>-p:PrototypeCards=true</c> is the
/// quarantine and compiles this file. <c>-p:VarkaPrototype=true</c> moves
/// <see cref="Enabled"/>'s default AND compiles the character class and his
/// two pools, because a character that ships nowhere else has nothing to
/// switch back to: off, he is simply not on the select screen. The rules
/// compile either way so one build can pin both sides.
///
/// C# FIRST, SIM AT BALANCE (<c>docs/current/operations/prototype.md</c>):
/// there is no tier0 twin of any of this yet.
/// </summary>
public static class VarkaPrototype
{
    /// <summary>The character id his cards, his Knights' personal pool and
    /// the companion system name him by.</summary>
    public const string CharacterId = "varka";

    /// <summary>The arm's default, from <c>-p:VarkaPrototype</c> (on in every
    /// build that names no property, <c>klee-mod/Directory.Build.props</c>).
    /// </summary>
    public const bool DefaultEnabled =
#if VARKA_PROTOTYPE
        true;
#else
        false;
#endif

    /// <summary>Is the arm live? Settable so a headless pin can assert both
    /// sides of the switch in one build; nothing in the mod writes it.
    /// </summary>
    public static bool Enabled { get; set; } = DefaultEnabled;

    /// <summary>Is this creature Varka?</summary>
    public static bool IsVarka(Creature? creature) =>
        creature?.Player?.Character is IVarkaCharacter;

    /// <summary>Is the arm live for this creature?</summary>
    public static bool LiveFor(Creature? creature) =>
        Enabled && IsVarka(creature);
}

/// <summary>
/// The numbers sec.10 prints, each a first-guess placeholder for play.
/// The Winds' four payouts live here because the Wind powers and their tips
/// both quote them; a card's own number lives on its row.
/// </summary>
public static class VarkaLaw
{
    /// <summary>Pyro Wind: damage to the enemy you Swirled.</summary>
    public const int PyroWindDamage = 3;

    /// <summary>Hydro Wind: Block per Swirl.</summary>
    public const int HydroWindBlock = 3;

    /// <summary>Cryo Wind: Weak on the enemy you Swirled.</summary>
    public const int CryoWindWeak = 1;

    /// <summary>Electro Wind: Energy on the first Swirl each turn.</summary>
    public const int ElectroWindEnergy = 1;
}
