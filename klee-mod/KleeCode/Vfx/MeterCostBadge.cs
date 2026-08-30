using System;
using Godot;
using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.addons.mega_text;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Entities.UI;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Cards;

namespace KleeMod.Vfx;

/// <summary>
/// THE METER COST BADGE -- one badge, three meters (EB-220).
///
/// It began as the Klee Spark cost badge (PICK 8 option 2,
/// review/active/klee-sparks-2026-08-29.md sec.6.4; the independent seat
/// FOLLOWS, citing D4: "at the decision point the player can perceive and
/// forecast the consequences that matter, through the card, a keyword, a
/// persistent UI element or a character rule"). [USER], 2026-08-30: "Yes, I
/// think Encore and Charge need badges." So the look is not re-invented per
/// meter -- it is PARAMETERISED by meter, and the number it renders still comes
/// from the same expression the playability gate charges.
///
/// THE DEFECT IT REPAIRS. A meter price used to be a sentence in the card's
/// RULES BOX ("Spend 1 [Spark]. Deal 8 damage.", "Spend 3 Encore: draw 3") or,
/// for an <c>encore_cost</c> row, nowhere on the face at all -- BaseLib's
/// <c>CustomResourceCost.UpdateCostVisuals</c> is an empty method, so a card
/// costing 2 Encore drew exactly like a card costing none. The base game never
/// does that: all 23 of Regent's Star cards say NOTHING about their price in
/// rules text and carry it entirely on a dedicated cost badge beside the energy
/// orb. A price in the rules box is a price you read after deciding.
///
/// WHY A PATCH ON THE STAR BADGE AND NOT THE STAR BADGE ITSELF. Option 1 was to
/// store Sparks in `PlayerCombatState.Stars` and get all of this free. It was
/// DECLINED as a one-way door: Sparks would BE Stars, every reader re-points,
/// and in co-op a Regent star relic would top up Klee's bank. So the badge is
/// ours -- but its GRAMMAR is the game's, because that is the whole point of a
/// badge. This is a postfix on `NCard.UpdateStarCostVisuals`, which means:
///
///   * SAME POSITION AND SAME SHAPE. It writes `%StarIcon` / `%StarLabel`, the
///     very node pair Regent's price uses -- so the price sits exactly where a
///     player already looks for a second cost, at the same size, in the same
///     font, on every surface that renders a card.
///   * DIFFERENT ICONOGRAPHY, PER METER. Sparks wear Klee's own
///     `klee/powers/spark.png` -- the icon her Spark counter already wears --
///     so the badge says SPARK and never STAR.
///   * SAME COLOUR RULES. <c>StsColors.red</c> with
///     <c>unplayableEnergyCostOutline</c> when the bank cannot pay, which is
///     <c>CardCostHelper.GetStarCostColor</c>'s own InsufficientResources arm.
///
/// ENCORE AND CHARGE HAVE NO ICON, and no art was authored to give them one.
/// Neither meter owns a glyph anywhere in the mod: Encore's ambient display is
/// the Salon stage RIBBON (a coloured bar and a number, D3) and Charge's is the
/// second-row GAUGE (a bare climbing number, no cap icon). So the badge borrows
/// what those two displays actually use to say which meter they are -- their
/// COLOUR, read off the same values the ribbon and the gauge are drawn with --
/// and HIDES the icon rather than showing a star. The result is a number in the
/// card's second cost slot, in the colour of the meter it spends, on a card
/// whose text names that meter. If [USER] wants a glyph instead, that is an art
/// pick with a contact sheet, not something to improvise here.
///
/// A POSTFIX, NOT A PREFIX, deliberately: the base method runs first and does
/// its own work (including hiding the icon for a card with no Star cost, which
/// every card of ours is), and this writes over the result only for a card that
/// charges a meter. A card that charges none is left exactly as the base game
/// drew it -- so a Regent at the same table still sees his own star badge.
///
/// SHIPPED, NOT QUARANTINED (EB-220). The badge used to live under
/// `Vfx/Prototype/**`, which is Compile Remove'd without
/// `-p:PrototypeCards=true`, because when it was built every priced face it had
/// to draw was a prototype row. Encore is not a prototype: `deep_breath`,
/// `ebb_and_flow` and `dress_rehearsal` are shipped Furina cards, so the badge
/// ships with them. What stays behind the flag is the state-aware half of the
/// Spark price -- the strict Rare Power's contribution, which
/// <see cref="SparkCost.PowerPriceOf"/> compiles to a literal 0 in a release
/// build.
/// </summary>
internal static class MeterCostBadge
{
    /// <summary>
    /// The pck-relative glyph for a meter, or null when the meter owns none.
    ///
    /// Sparks reuse the Spark counter's own icon. Encore and Charge return null
    /// because no such asset exists -- see the class note. Null here means "draw
    /// the number, hide the icon", which is a deliberate rendering; it is NOT
    /// the pck-missing case, which is a null from <c>KleePck.Path</c> for a path
    /// that IS declared and which falls back to drawing nothing at all.
    /// </summary>
    private static string? IconPathFor(Meter meter) => meter switch
    {
        Meter.Sparks => "klee/powers/spark.png",
        _ => null,
    };

    /// <summary>
    /// The colour a meter is already drawn in elsewhere on the screen, so the
    /// badge reads as that meter rather than as a second energy orb.
    ///
    /// Sparks keep <c>StsColors.cream</c> -- the base game's own cost colour --
    /// because the spark GLYPH already carries the identity there, and recolour-
    /// ing a look [USER] has not yet had eyes on would be two changes in one.
    /// Encore's value is the Salon stage ribbon's fill
    /// (`furina/ui/salon_stage.tscn`, %Seg1) and Charge's is the second-row
    /// gauge's fill (<see cref="GaugeBridge"/>, the `kokomi_charge` spec).
    /// </summary>
    private static Color ColorFor(Meter meter) => meter switch
    {
        Meter.Encore => new Color(0.35f, 0.75f, 1f),
        Meter.Charge => new Color(0.44f, 0.78f, 0.84f),
        _ => StsColors.cream,
    };

    private static bool _warnedFreedGlyph;

    /// <summary>
    /// The glyph for a meter, RESOLVED FRESH ON EVERY PAINT (EB-222).
    ///
    /// THE DEFECT THIS IS. EB-220 shipped a `Dictionary&lt;Meter, Texture2D?&gt;`
    /// static cache in front of this load -- one `ResourceLoader.Load` for the
    /// life of the process, its result held in a static field forever. The game
    /// does not let a texture live that long: it PRELOADS a room's asset set and
    /// TEARS IT DOWN with the room ("Preloading 'Combat Room' assets... count=9"
    /// on the way in, `Asset not cached: res://klee/powers/bomb.png` once it is
    /// gone). So the `CompressedTexture2D` combat #1 loaded was freed with combat
    /// #1's assets, our static field kept pointing at the corpse, and the FIRST
    /// card drawn in combat #2 handed it to `TextureRect.SetTexture` --
    /// `ObjectDisposedException` out of `NCard.UpdateStarCostVisuals`, up through
    /// `CardPileCmd.Draw` and into the turn loop, which died with the combat in
    /// progress and stuck the room (`understudy.soak`, every run).
    ///
    /// SO THE MOD HOLDS NO TEXTURE ACROSS SCENES, and this method is the whole
    /// rule: ask `ResourceLoader` each time. That is not the expensive read it
    /// looks like -- the engine keeps its own resource cache and answers a
    /// second load of a live path from it -- and it is the only source that can
    /// tell us the truth about a resource whose lifetime the engine owns.
    /// `KleePck.Path` still caches, but it caches a STRING and a bool.
    ///
    /// AND THE ANSWER IS STILL CHECKED, because a cache we do not own can hand
    /// back a wrapper for an object that is already gone. A freed texture is
    /// reported through <paramref name="freed"/> rather than as a plain null:
    /// null means "this meter owns no glyph" (Encore, Charge -- draw the number,
    /// hide the icon) or "the glyph is declared and the pck lacks it" (draw
    /// nothing), and neither of those is what a disposed resource means.
    /// </summary>
    private static Texture2D? Glyph(Meter meter, out bool freed)
    {
        freed = false;

        string? declared = IconPathFor(meter);
        string? path = declared == null ? null : KleePck.Path(declared);
        if (path == null)
        {
            return null;
        }

        Texture2D? texture = ResourceLoader.Load<Texture2D>(path);
        if (texture == null)
        {
            return null;
        }

        if (!GodotObject.IsInstanceValid(texture))
        {
            freed = true;
            return null;
        }

        return texture;
    }

    /// <summary>
    /// Put the glyph on the badge, or take the badge's glyph off -- and never,
    /// under any circumstance, throw at the caller.
    ///
    /// `Paint` runs inside `CardPileCmd.Draw`, i.e. INSIDE THE TURN LOOP, and
    /// EB-222 is what an exception from here costs: the loop dies, the combat is
    /// stuck, and the run is over. `IsInstanceValid` above is the guard; this
    /// `catch` is the promise, for the resource the engine frees between the
    /// check and the write and for the icon node torn down under us. Either way
    /// the card draws without a glyph and the badge still shows its NUMBER,
    /// which is the half of the display the price actually lives in. Warned
    /// once, like every other degrade in this layer.
    /// </summary>
    private static void SetGlyph(TextureRect icon, Texture2D? texture)
    {
        try
        {
            if (texture == null || !GodotObject.IsInstanceValid(icon))
            {
                icon.Visible = false;
                return;
            }

            icon.Texture = texture;
            icon.Visible = true;
        }
        catch (ObjectDisposedException e)
        {
            WarnFreedGlyph(e.Message);
            try
            {
                icon.Visible = false;
            }
            catch (ObjectDisposedException)
            {
                // The icon node itself is gone. Nothing to draw on, and
                // nothing further to do: the caller paints the number next.
            }
        }
    }

    private static void WarnFreedGlyph(string detail)
    {
        if (_warnedFreedGlyph)
        {
            return;
        }

        _warnedFreedGlyph = true;
        Log.Warn($"[{KleeMod.ModId}] meter cost badge: the meter glyph was freed "
               + $"by the engine ({detail}); drawing the price with no glyph.");
    }

    /// <summary>
    /// Paint the badge for <paramref name="card"/>, or leave the base game's
    /// drawing alone.
    ///
    /// EVERY EARLY RETURN IS A REAL CASE. A null model or an unready node is the
    /// pooled-NCard lifecycle; a non-Visible card is the face-down/locked
    /// compendium state the base method has already handled its own way; and no
    /// price at all is every card in the game that charges no meter of ours.
    /// </summary>
    internal static void Paint(NCard nCard, PileType pileType)
    {
        CardModel? card = nCard.Model;
        if (card == null || !nCard.IsNodeReady()
            || nCard.Visibility != ModelVisibility.Visible)
        {
            return;
        }

        if (MeterCost.Priced(card) is not { } price || price.Amount <= 0)
        {
            return;
        }

        var label = nCard.GetNodeOrNull<MegaLabel>("%StarLabel");
        var icon = nCard.GetNodeOrNull<TextureRect>("%StarIcon");
        if (label == null || icon == null)
        {
            return;
        }

        Texture2D? texture = Glyph(price.Meter, out bool freed);
        if (texture == null && !freed && IconPathFor(price.Meter) != null)
        {
            return;                 // a glyph is declared and absent: no STAR
        }

        if (freed)
        {
            WarnFreedGlyph("IsInstanceValid was false for the loaded texture");
        }

        // null here is one of two: this meter owns no glyph (Encore, Charge --
        // number only, by design), or the engine freed the one it had (EB-222 --
        // number only, warned once). Both draw the badge; neither throws.
        SetGlyph(icon, texture);

        label.SetTextAutoSize(price.Amount.ToString());

        // Affordability, in the base game's own two colours. Only in HAND: a
        // card in the draw pile, the compendium or a reward screen has no bank
        // to be short against, and the base game reddens a cost in hand only for
        // exactly that reason (UpdateStarCostColor's `pileType == PileType.Hand`
        // arm).
        Color text = ColorFor(price.Meter);
        Color outline = StsColors.defaultStarCostOutline;
        if (pileType == PileType.Hand && !MeterCost.Affordable(card, price))
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
internal static class NCard_UpdateStarCostVisuals_KleeMeterBadge_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCard __instance, PileType pileType)
        => MeterCostBadge.Paint(__instance, pileType);
}

/// <summary>
/// The badge's one side effect on the rest of the face, repaired.
///
/// `NCard.UpdateEnchantmentVisuals` shifts the enchantment tab UP 45px when the
/// card has no Star cost -- the base game reclaiming the empty badge slot. Every
/// card of ours has no Star cost, so an ENCHANTED priced card would draw its
/// enchantment tab straight through the badge we just painted. This puts the tab
/// back down for exactly the cards that now occupy that slot, and touches
/// nothing else: it runs after the base method (which sets the position from its
/// own private default), so the correction is a plain +45 down, and it fires
/// only when there is a price to have displaced it.
/// </summary>
[HarmonyPatch(typeof(NCard), "UpdateEnchantmentVisuals")]
internal static class NCard_UpdateEnchantmentVisuals_KleeMeterBadge_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCard __instance)
    {
        CardModel? card = __instance.Model;
        if (card == null || MeterCost.Priced(card) is not { Amount: > 0 }
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
