using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Entities.Cards;
#if PROTOTYPE_CARDS
using KleeMod.Powers;
#endif

namespace KleeMod.Cards;

/// <summary>
/// `EB-449`. THE PRINTED HALF OF A RETIRED METER.
///
/// THE DEFECT, three rounds running. Under the Furina reframe the Burst meter
/// is retired -- <c>FurinaReframe.BurstRetiredFor</c> is the one question the
/// display guard, the income funnel and the kit grant all ask -- and `EB-449`
/// took the explanatory TIP off her faces in r8. It did not touch the two
/// things the seat actually reads: the printed line "<c>Burst +5.</c>" at the
/// end of the body, and the gold "<c>Elemental Skill</c>" keyword the game
/// appends under it. The r11 lane-1 seat met both on <i>Gentilhomme Usher</i>
/// at two separate rewards and SKIPPED THE CARD FOR IT -- a Common enabler
/// passed over because its face promised a resource that does not exist.
///
/// BY RULE AND NOT BY NAME, which is the whole of the reopen. The set is
/// "every Furina face carrying <c>tags: [skill_tag]</c>", thirteen rows today,
/// and it is derived at codegen from the same field that emits
/// <c>ISkillTagCard</c> -- so a fourteenth row inherits the blank instead of
/// having to be remembered. <c>tools/gen_klee_cards.py</c> emits both members
/// through this class for exactly those rows and character-for-character the
/// old text for every other row on every other sheet (Klee's fifteen and
/// Kokomi's one keep their meters and keep their line).
///
/// A RUNTIME READ AND NOT A <c>#if</c>, deliberately. The generated files are
/// committed and must be one text whatever the build; a compile switch inside
/// them would make the codegen check answer differently under two property
/// sets, and no headless test could then read the OTHER side. The flag's
/// default IS the compile switch (<c>FurinaReframe.DefaultEnabled</c>), a
/// <c>Localization</c> property builds its list per call, and BaseLib reads it
/// at registration -- so a real build answers exactly what a `#if` would, and
/// a test can flip the flag and read both faces.
///
/// NO OWNER, and that is a fact about the surface rather than a shortcut:
/// these are card FACES, read at boot and in the compendium where no creature
/// exists. <c>BurstRetiredFor</c>'s <c>IsFurina</c> half is carried by the
/// call site instead -- only Furina's own sheet emits these members.
///
/// THE GAMEPLAY IS UNTOUCHED. <c>ISkillTagCard</c> still rides the row and
/// <c>FurinaResources</c> still refuses to pay it under the arm; this class
/// only decides what is PRINTED. The two are separate on purpose: the day the
/// arm is withdrawn, the meter and its words come back together.
/// </summary>
public static class FurinaBurstRider
{
    /// <summary>Whether the shipped Burst meter is retired for this BUILD --
    /// the creature-less half of <c>FurinaReframe.BurstRetiredFor</c>, for the
    /// surfaces that have no creature to ask about.</summary>
    public static bool Retired =>
#if PROTOTYPE_CARDS
        FurinaReframe.Enabled && FurinaReframe.BurstEnabled;
#else
        false;
#endif

    /// <summary>The face to print: the arm's, with no promise of a meter that
    /// does not exist, or the shipped one.</summary>
    public static string Face(string arm, string shipped) =>
        Retired ? arm : shipped;

    /// <summary>The card's keywords, minus <c>Elemental Skill</c> under the
    /// arm. The keyword cannot be re-worded instead: its loc row is registered
    /// once at boot for every card that carries it
    /// (<c>KleeCardTooltips</c> says so beside the tip it does gate), so the
    /// only per-arm answer available is whether the card carries it at
    /// all.</summary>
    public static IEnumerable<CardKeyword> Keywords(
        IEnumerable<CardKeyword> declared) =>
        Retired
            ? declared.Where(word => word != KleeKeywords.ElementalSkill)
            : declared;
}
