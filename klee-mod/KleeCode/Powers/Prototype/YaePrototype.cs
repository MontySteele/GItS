using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;

namespace KleeMod.Powers;

/// <summary>
/// Marker for Yae Miko's CharacterModel, the identity gate every Yae rule
/// asks (Varka's <see cref="IVarkaCharacter"/>, one character over). On the
/// CHARACTER, not the cards, so a Yae card another seat holds in co-op does
/// not hand that seat her shrine.
/// </summary>
public interface IYaeCharacter
{
}

/// <summary>
/// YAE MIKO, THE FIFTH CHARACTER (<c>review/active/yae-card-paper-2026-10-13.md</c>,
/// ruled 2026-10-13). The shrine and the publishing house:
///
///   * SAKURA (<see cref="YaeShrineLedger"/>, <see cref="YaeShrine"/>): up to
///     3 beside her, each with a Level and a 3-strike timer. At the end of
///     her turn each strikes, oldest first, for 2 + its Level Electro as a
///     pet's hit, then the timers tick; a Sakura that withers strikes once
///     more (Last Bloom). A plant creates one at the card's Level; with
///     three standing the oldest refreshes and gains a Level instead (shrine
///     r2). Tenko strikes now (typed: as Block, at ALL, or as draw) and
///     resets every timer.
///   * EDIT (<see cref="YaeEditing"/>): a card in hand gains one of five
///     Annotations (her Enchantments, <see cref="YaeAnnotationModel"/>) for
///     the combat. PUBLISH keeps one for the run: The Seven Glamours in
///     combat, and Meditations of a Yako's reward-screen Publish after an
///     elite or boss fight (<c>Relics.MeditationsOfAYako</c>).
///
/// NO SWITCH, as Varka: she ships nowhere else. BUILT IN BOTH ENGINES: the
/// sim twin is <c>tier0/engine/yae_shrine.py</c>, whose numbers
/// <see cref="YaeLaw"/> mirrors (<c>tools/lint_constant_parity.py</c>).
/// </summary>
public static class YaePrototype
{
    /// <summary>The id her cards, her pool and the companion system name her
    /// by.</summary>
    public const string CharacterId = "yae";

    /// <summary>Is this creature Yae?</summary>
    public static bool IsYae(Creature? creature) =>
        creature?.Player?.Character is IYaeCharacter;

    /// <summary>Is this player Yae?</summary>
    public static bool IsYae(Player? player) => player?.Character is IYaeCharacter;
}

/// <summary>
/// The rule numbers the paper prints (sec.2), mirrored by value against
/// <c>tier0/engine/yae_shrine.py</c>. A card's own numbers live on its row.
/// </summary>
public static class YaeLaw
{
    /// <summary>"Up to 3 Sakura stand beside her."</summary>
    public const int SakuraCap = 3;

    /// <summary>A Sakura's timer when planted or refreshed: 3 strikes
    /// (pick 4 (a)).</summary>
    public const int SakuraTurns = 3;

    /// <summary>A strike deals this plus the Sakura's Level.</summary>
    public const int SakuraBase = 2;

    /// <summary>A Sakura is planted at Level 1, plus 1 for each Fox's
    /// Mooncall. Levels have no cap (Yae review r1, pick 2, ruled
    /// 2026-10-14): they stack without limit and leave with the Sakura.
    /// </summary>
    public const int PlantLevel = 1;

    /// <summary>Red Ink: this much more damage per hit and Block per gain.
    /// </summary>
    public const int RedInkAmount = 3;

    /// <summary>Fox Fire: this much Electro to a random enemy.</summary>
    public const int FoxFireDamage = 4;

    /// <summary>Offering: each strike, this many more cards at the start of
    /// her next turn (design axes, ruled 2026-10-14).</summary>
    public const int OfferingPerStrike = 1;

    /// <summary>Royalties: this much Energy when the card is played.
    /// </summary>
    public const int RoyaltiesPayout = 1;
}
