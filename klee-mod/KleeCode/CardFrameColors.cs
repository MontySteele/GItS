using BaseLib.Abstracts;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// EVERY KIT'S CARD COLOUR, IN ONE PLACE (card frames stage 1, 2026-10-19).
///
/// [USER], 2026-10-19: "we need a quick way of distinguishing the character
/// cards". Furina, Kokomi and Varka all wore the Silent's green frame, Klee
/// the Ironclad's red and Yae the Defect's blue, so a kit card looked like a
/// base character's card and like each other's.
///
/// HOW THE TINT IS DRAWN. The base game draws every character card from one
/// frame texture per card type (crimson, `card_frame_attack_s` and siblings)
/// and recolours it with a per-pool material: `res://shaders/hsv.gdshader`,
/// whose `h` rotates hue in YIQ space by (1 - h) of a turn, `s` scales the
/// chroma and `v` scales brightness. The base materials, read out of
/// SlayTheSpire2.pck 2026-10-19, are Ironclad 0.025/0.85/1.0, Regent
/// 0.12/1.5/1.2, Silent 0.32/0.45/1.2, Defect 0.55/0.9/1.0, Necrobinder
/// 0.965/0.55/1.2, Colorless 1.0/0.0/1.2. BaseLib builds the same material
/// from a <see cref="CustomCardPoolModel"/>'s H, S and V when the pool keeps
/// the path `card_frame_red` (<see cref="KitCardPool"/>); the numbers below
/// were chosen against a render of that shader on the shipped frame so that
/// no kit sits on a base character's hue.
///
/// <see cref="Tint.DeckEntry"/> is the deck-entry chip colour (the base pools
/// use a saturated version of their frame hue, Ironclad D62000);
/// <see cref="Tint.EnergyOutline"/> outlines the cost number on the orb. The
/// ORB ITSELF is not here: it is a base texture chosen by name
/// (`EnergyColorName`), not a hue, so every kit keeps the orb it borrowed
/// until stage 2 gives it its own art.
/// </summary>
public static class CardFrameColors
{
    /// <summary>One kit's frame tint: the hsv shader's three parameters plus
    /// the two flat colours the pool also controls.</summary>
    public readonly record struct Tint(
        string Kit, float H, float S, float V, Color DeckEntry, Color EnergyOutline);

    /// <summary>Warm red-orange (renders about #C44A00), between the
    /// Ironclad's red and the Regent's amber.</summary>
    public static readonly Tint Klee =
        new("klee", 0.065f, 1.3f, 1.15f, new Color("F0600F"), new Color("7A3010"));

    /// <summary>Deep blue (about #2348B7), darker and more violet than the
    /// Defect's cyan-blue.</summary>
    public static readonly Tint Furina =
        new("furina", 0.63f, 1.1f, 0.85f, new Color("2F5BE0"), new Color("1A2A70"));

    /// <summary>Pearl coral (about #B27768): pale and low-saturation, so it
    /// reads apart from both the Ironclad's red and the Necrobinder's pink.</summary>
    public static readonly Tint Kokomi =
        new("kokomi", 0.03f, 0.38f, 1.55f, new Color("E89A86"), new Color("7A3E34"));

    /// <summary>Anemo teal-green (about #12805B), bluer than the Silent's
    /// leaf green.</summary>
    public static readonly Tint Varka =
        new("varka", 0.47f, 0.9f, 1.05f, new Color("1FB585"), new Color("0F5A40"));

    /// <summary>Magenta-pink (about #AD33A0), more saturated and more violet
    /// than the Necrobinder's dusty pink.</summary>
    public static readonly Tint Yae =
        new("yae", 0.9f, 0.9f, 1.15f, new Color("D63CC8"), new Color("6B1F63"));

    public static readonly Tint[] All = { Klee, Furina, Kokomi, Varka, Yae };
}

/// <summary>
/// A kit's card pool, tinted by BaseLib's HSV frame material
/// (<see cref="CardFrameColors"/>).
///
/// WHY A <see cref="CustomCardPoolModel"/> NOW. BaseLib's material patch
/// replaces <c>CardPoolModel.FrameMaterial</c> only for its own pool type,
/// and only while the path stays <c>card_frame_red</c>, which is therefore
/// sealed here. Everything else about the five pools is unchanged:
/// <list type="bullet">
/// <item>ID. A <c>CustomCardPoolModel</c> is an <c>ICustomModel</c>, and
/// BaseLib's <c>PrefixIdPatch</c> prefixes such a type's ModelId entry with
/// its namespace. Each subclass pins its old entry with <c>[CustomID]</c>
/// (the game's own <c>StringHelper.Slugify</c> of the type name), so
/// <c>KLEE_CARD_POOL</c> stays <c>KLEE_CARD_POOL</c>.</item>
/// <item>Membership and offer: the subclasses' own GenerateAllCards and
/// FilterThroughEpochs, untouched.</item>
/// <item>IsShared false, so nothing registers it as a shared pool;
/// SeenByDefault false, so the library's mark-as-seen patch skips it;
/// CustomFrame returns null, so the per-type frame texture stays the base
/// one (stage 2 is where that changes).</item>
/// <item>The energy orb: each subclass keeps its borrowed EnergyColorName,
/// which overrides BaseLib's custom-icon name.</item>
/// </list>
/// </summary>
public abstract class KitCardPool : CustomCardPoolModel
{
    /// <summary>This kit's row in <see cref="CardFrameColors"/>.</summary>
    public abstract CardFrameColors.Tint Tint { get; }

    public sealed override string CardFrameMaterialPath => "card_frame_red";

    public sealed override float H => Tint.H;

    public sealed override float S => Tint.S;

    public sealed override float V => Tint.V;

    /// <summary>Not read by BaseLib once H, S and V are given (they are what it
    /// derives from this colour, and S and V above 1 cannot be written as a
    /// colour); kept as the chip swatch so the two cannot disagree.</summary>
    public sealed override Color ShaderColor => Tint.DeckEntry;

    public sealed override Color DeckEntryCardColor => Tint.DeckEntry;

    public sealed override Color EnergyOutlineColor => Tint.EnergyOutline;

    public sealed override bool IsShared => false;

    public sealed override bool IsColorless => false;
}

/// <summary>
/// BORROWED BASICS WEAR THE KIT'S FRAME (2026-10-20).
///
/// [USER], 2026-10-20: "All of the Strikes and Defends in Kokomi's deck still
/// have the Silent's green border. Can we make those mirror the color of the
/// cards in her deck, and do the same for other characters?"
///
/// Every kit starts on the BASE game's Strike and Defend (StrikeSilent for
/// Furina, Kokomi and Varka, StrikeIronclad for Klee, StrikeDefect for Yae),
/// and those stay the exact base cards. Their <c>Pool</c> is the base
/// character's, and the frame, the tiny-card back and the orb all read
/// <c>CardModel.VisualCardPool</c> (base body: <c>=&gt; Pool</c>). This postfix
/// answers the owner's kit pool instead, for a Basic card whose own pool is
/// not a kit pool and whose owner plays a kit. Nothing else moves:
/// <list type="bullet">
/// <item>A canonical card (library, compendium) has no owner, so it keeps the
/// base colour. Ownership is read the way the base game's own
/// <c>EnergyIconHelper.GetPool</c> reads it: <c>IsMutable</c> first, since
/// <c>Owner</c> asserts mutability.</item>
/// <item>A kit's own Basic cards already sit in their kit pool and are
/// skipped; a card whose class overrides VisualCardPool (Clash, Caltrops, ...)
/// never runs this body.</item>
/// <item>Gameplay: the only game read that is not paint is Heirloom Hammer's
/// <c>VisualCardPool.IsColorless</c>, false on a kit pool as on a base
/// character pool. The orb is <c>EnergyColorName</c>, which each kit pool
/// borrows from the same base character as its starter pair, so it is the
/// same texture.</item>
/// <item>Co-op: the tint follows the card's owner, so each player's basics
/// wear that player's kit.</item>
/// </list>
/// </summary>
[HarmonyPatch(typeof(CardModel), "get_VisualCardPool")]
internal static class CardModel_VisualCardPool_KitBasics_Patch
{
    private static void Postfix(CardModel __instance, ref CardPoolModel __result)
    {
        try
        {
            var ownerPool = __instance.IsMutable
                ? __instance.Owner?.Character?.CardPool
                : null;
            __result = BorrowedBasicFrame.PoolFor(__instance.Rarity, __result, ownerPool);
        }
        catch
        {
            // A mid-teardown owner or a card with no pool: the base answer stands.
        }
    }
}

/// <summary>The decision <see cref="CardModel_VisualCardPool_KitBasics_Patch"/>
/// makes, apart from the card so it can be tested without a run.</summary>
public static class BorrowedBasicFrame
{
    /// <summary>The pool a card is drawn with: the owner's kit pool for a
    /// borrowed Basic, otherwise <paramref name="visual"/> unchanged.</summary>
    public static CardPoolModel PoolFor(
        CardRarity rarity, CardPoolModel visual, CardPoolModel? ownerPool) =>
        rarity == CardRarity.Basic
        && visual is not KitCardPool
        && ownerPool is KitCardPool kit
            ? kit
            : visual;
}
