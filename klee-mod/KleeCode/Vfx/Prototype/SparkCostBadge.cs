using Godot;
using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.addons.mega_text;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.UI;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Cards;

namespace KleeMod.Vfx;

/// <summary>
/// THE KLEE SPARK COST BADGE -- PICK 8 option 2
/// (review/active/klee-sparks-2026-08-29.md sec.6.4; the independent seat
/// FOLLOWS, citing D4: "at the decision point the player can perceive and
/// forecast the consequences that matter, through the card, a keyword, a
/// persistent UI element or a character rule").
///
/// THE DEFECT IT REPAIRS. Klee's Spark price is a sentence in the card's RULES
/// BOX ("Spend 1 [Spark]. Deal 8 damage."). The base game never does that: all
/// 23 of Regent's Star cards say NOTHING about their price in rules text and
/// carry it entirely on a dedicated cost badge beside the energy orb. A price
/// in the rules box is a price you read after deciding, and PREDICTION P2 in
/// sec.10.9 bets a grader cannot state the price off the FACE without it.
///
/// WHY A PATCH ON THE STAR BADGE AND NOT THE STAR BADGE ITSELF. Option 1 was to
/// store Sparks in `PlayerCombatState.Stars` and get all of this free. It was
/// DECLINED as a one-way door: Sparks would BE Stars, every reader re-points,
/// and in co-op a Regent star relic would top up Klee's bank. So the badge is
/// ours -- but its GRAMMAR is the game's, because that is the whole point of a
/// badge. This is a postfix on `NCard.UpdateStarCostVisuals`, which means:
///
///   * SAME POSITION AND SAME SHAPE. It writes `%StarIcon` / `%StarLabel`, the
///     very node pair Regent's price uses -- so the Spark price sits exactly
///     where a player already looks for a second cost, at the same size, in the
///     same font, on every surface that renders a card.
///   * DIFFERENT ICONOGRAPHY. The texture is Klee's own `klee/powers/spark.png`
///     -- the icon her Spark counter already wears -- so the badge says SPARK
///     and never STAR. No new art: the asset ships today.
///   * SAME COLOUR RULES. `StsColors.cream` when the bank can pay,
///     `StsColors.red` with `unplayableEnergyCostOutline` when it cannot, which
///     is `CardCostHelper.GetStarCostColor`'s own InsufficientResources arm.
///
/// ONE NUMBER, WHICH IS THE POINT. The badge renders `SparkCost.PriceOf`, the
/// exact expression the generated `IsPlayable` gate and `SparkAttackCostPower`'s
/// `ShouldPlay` read. There is no second table and no second literal, so the
/// price shown cannot drift from the price charged. Under the strict Rare Power
/// an Attack that prints no price still gets a badge -- reading 3 -- because
/// PriceOf is state-aware, and its Energy badge reads 0 because the power zeroes
/// the Energy line for the same card.
///
/// A POSTFIX, NOT A PREFIX, deliberately: the base method runs first and does
/// its own work (including hiding the icon for a card with no Star cost, which
/// every Klee card is), and this writes over the result only for a card that
/// charges Sparks. A card that charges none is left exactly as the base game
/// drew it -- so a Regent at the same table still sees his own star badge, and
/// so does a Klee card in the compendium with no bank behind it.
///
/// QUARANTINED. `Vfx/Prototype/**` is Compile Remove'd without
/// `-p:PrototypeCards=true`, so a release build carries no patch class and
/// `KleePatchBootstrap` has nothing to arm. Revert is the flag.
/// </summary>
internal static class SparkCostBadge
{
    /// <summary>The Spark counter's own icon, reused. Null while the pck is
    /// absent or stale, which is the same fallback every KleePck path takes:
    /// no texture means the base game's drawing stands.</summary>
    private const string IconPath = "klee/powers/spark.png";

    private static Texture2D? _icon;
    private static bool _iconProbed;

    private static Texture2D? Icon()
    {
        if (_iconProbed)
        {
            return _icon;
        }

        _iconProbed = true;
        string? path = KleePck.Path(IconPath);
        _icon = path == null ? null : ResourceLoader.Load<Texture2D>(path);
        return _icon;
    }

    /// <summary>
    /// Paint the badge for <paramref name="card"/>, or leave the base game's
    /// drawing alone.
    ///
    /// EVERY EARLY RETURN IS A REAL CASE. A null model or an unready node is the
    /// pooled-NCard lifecycle; a non-Visible card is the face-down/locked
    /// compendium state the base method has already handled its own way; and a
    /// price of 0 is every card in the game that does not charge Sparks --
    /// including all of Klee's with the flag's rule inactive.
    /// </summary>
    internal static void Paint(NCard nCard, PileType pileType)
    {
        CardModel? card = nCard.Model;
        if (card == null || !nCard.IsNodeReady()
            || nCard.Visibility != ModelVisibility.Visible)
        {
            return;
        }

        int price = SparkCost.PriceOf(card);
        if (price <= 0)
        {
            return;
        }

        var label = nCard.GetNodeOrNull<MegaLabel>("%StarLabel");
        var icon = nCard.GetNodeOrNull<TextureRect>("%StarIcon");
        if (label == null || icon == null)
        {
            return;
        }

        Texture2D? texture = Icon();
        if (texture == null)
        {
            return;                 // no Spark glyph: do not draw a STAR
        }

        icon.Texture = texture;
        icon.Visible = true;
        label.SetTextAutoSize(price.ToString());

        // Affordability, in the base game's own two colours. Only in HAND: a
        // card in the draw pile, the compendium or a reward screen has no bank
        // to be short against, and the base game reddens a cost in hand only for
        // exactly that reason (UpdateStarCostColor's `pileType == PileType.Hand`
        // arm).
        Color text = StsColors.cream;
        Color outline = StsColors.defaultStarCostOutline;
        if (pileType == PileType.Hand && !SparkCost.Affordable(card))
        {
            text = StsColors.red;
            outline = StsColors.unplayableEnergyCostOutline;
        }

        label.AddThemeColorOverride(ThemeConstants.Label.FontColor, text);
        label.AddThemeColorOverride(ThemeConstants.Label.FontOutlineColor, outline);
    }
}

/// <summary>
/// The one arming point. `UpdateStarCostVisuals` is private and is called from
/// `UpdateVisuals` and `SetPretendCardCanBePlayed` -- i.e. from every redraw the
/// game already performs -- so the badge refreshes on exactly the cadence the
/// star badge does and needs no polling of its own.
/// </summary>
[HarmonyPatch(typeof(NCard), "UpdateStarCostVisuals")]
internal static class NCard_UpdateStarCostVisuals_KleeSparkBadge_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCard __instance, PileType pileType)
        => SparkCostBadge.Paint(__instance, pileType);
}

/// <summary>
/// The badge's one side effect on the rest of the face, repaired.
///
/// `NCard.UpdateEnchantmentVisuals` shifts the enchantment tab UP 45px when the
/// card has no Star cost -- the base game reclaiming the empty badge slot. Every
/// Klee card has no Star cost, so an ENCHANTED Spark-priced card would draw its
/// enchantment tab straight through the badge we just painted. This puts the tab
/// back down for exactly the cards that now occupy that slot, and touches
/// nothing else: it runs after the base method (which sets the position from its
/// own private default), so the correction is a plain +45 down, and it fires
/// only when there is a price to have displaced it.
/// </summary>
[HarmonyPatch(typeof(NCard), "UpdateEnchantmentVisuals")]
internal static class NCard_UpdateEnchantmentVisuals_KleeSparkBadge_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCard __instance)
    {
        CardModel? card = __instance.Model;
        if (card == null || SparkCost.PriceOf(card) <= 0
            || card.HasStarCostX || card.CurrentStarCost >= 0)
        {
            return;                 // no badge of ours, or the game kept the slot
        }

        var tab = __instance.GetNodeOrNull<Control>("%Enchantment");
        if (tab != null)
        {
            tab.Position += Vector2.Down * 45f;
        }
    }
}
