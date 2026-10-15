using System;
using System.Linq;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// SUCROSE'S "NO AURA" CLAUSE (Kokomi review r8, 2026-10-14, item 7). Two
/// seat plays were wasted on a Sucrose Swirl with no element on the board:
/// the card did nothing and the face had not said it would. Like Tenko's
/// "(no Sakura)", a Sucrose Swirl face carries <c>{InCombat:{SwirlAura}|}</c>
/// right after the words it qualifies ("Swirl the enemy", "Swirl ALL
/// enemies"; <c>gen_klee_cards.swirl_aura_face_lines</c> places it), and in
/// combat it reads " (no aura: no Swirl)" while the enemy the card is aimed
/// at has no aura, or, not aimed, while no enemy has one. Empty otherwise,
/// off a combat and on a canonical card. Display only. Varka's own Swirl
/// cards keep <c>VarkaOath.SwirlLine</c>. Sim twin:
/// <c>gen_klee_cards.SWIRL_AURA_WORDS</c>.
/// </summary>
public static class SwirlAuraFace
{
    /// <summary>The description token the clause rides on.</summary>
    public const string Token = "SwirlAura";

    /// <summary>The clause with nothing to Swirl.</summary>
    public const string NoAura = " (no aura: no Swirl)";

    /// <summary>The words for a board: <see cref="NoAura"/> when there is no
    /// aura to Swirl, else empty. PURE.</summary>
    public static string Words(bool aura) => aura ? "" : NoAura;

    /// <summary>The card's live clause.</summary>
    public static string Line(CardModel? card)
    {
        Creature? owner;
        try
        {
            owner = TipOwner.CreatureOf(card);
        }
        catch (Exception)
        {
            return "";
        }
        if (owner?.CombatState == null) return "";
        var target = DescribedTarget.For(card);
        if (target != null) return Words(AuraCmd.Find(target) != null);
        return Words(owner.CombatState.HittableEnemies
            .Any(e => AuraCmd.Find(e) != null));
    }
}
