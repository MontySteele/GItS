using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// "BELOW HALF", WITH ITS NUMBER (release fixes, 2026-10-14). Understudy's
/// Debut and Crowd Favorite said "below half" and left the player to work out
/// the HP. In combat a face reads "below half (39 HP)" through the base
/// game's <c>{InCombat:...|}</c> seam (<c>gen_klee_cards.half_hp_face_lines</c>
/// places the token on every face that prints the words).
///
/// Below half is <c>hp * 2 &lt; max</c> (the sheet's <c>hp_pct_below_50</c>,
/// Crowd Favorite's check), so the number printed is the first HP that is NOT
/// below half: half of Max HP, rounded up. At 78 Max HP, below 39.
/// </summary>
public static class HalfHpFace
{
    /// <summary>The HP "below half" is below: half of Max HP, rounded
    /// up.</summary>
    public static int Threshold(int maxHp) => (maxHp + 1) / 2;

    /// <summary>The words' row (the localization census, 2026-10-23, step
    /// 2); the leading space is the row's.</summary>
    internal static readonly CodeRow Row =
        new("card_keywords", "KLEEMOD-FACE_HALF_HP.description", " ({Hp} HP)");

    /// <summary>The in-combat words, " (39 HP)", for the pins.</summary>
    public static string Words(int maxHp) =>
        CodeText.Format(Row, CodeText.Vars(("Hp", Threshold(maxHp))));

    /// <summary>The card's owner's line, or nothing with no owner to
    /// read.</summary>
    public static string Line(CardModel card) =>
        TipOwner.CreatureOf(card) is { CombatState: not null } owner
            ? Words(owner.MaxHp)
            : "";

    /// <summary>A creature's line (Crowd Favorite's power).</summary>
    public static string Line(Creature? creature) =>
        creature == null ? "" : Words(creature.MaxHp);
}
