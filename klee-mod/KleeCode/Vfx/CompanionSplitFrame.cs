using System;
using System.Collections.Generic;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Cards;

namespace KleeMod.Vfx;

/// <summary>
/// THE COMPANION SPLIT FRAME (card frames stage 2, 2026-10-20).
///
/// [USER], 2026-10-20: "Agreed on all of the card / orb / energy mockup
/// picks". A shared companion's frame is pure Colorless on its left 40%, a
/// smoothstep blend over the next 20%, and its nation's tint
/// (<see cref="CardFrameColors.NationTint"/>) on the right 40%, so a
/// Mondstadt, an Inazuma and a Fontaine companion read apart before the nation
/// pip (<see cref="NationEmblem"/>, kept) is read.
///
/// WHICH CARDS. A card whose <c>VisualCardPool</c> is
/// <see cref="CompanionCardPool"/> and whose <see cref="Cards.ICompanionCard"/>
/// nation has a tint. Kit-own companions sit in their kit's pool and keep the
/// kit frame; a nation with no tint (Liyue, none yet) keeps plain Colorless.
/// The pool itself does not move: rules read <c>VisualCardPool.IsColorless</c>
/// (Heirloom Hammer), and this is paint only.
///
/// HOW. <c>CardModel.FrameMaterial</c> is a non-virtual getter
/// (<c>=&gt; VisualCardPool.FrameMaterial</c>), read by <c>NCard</c> for the
/// frame (and by <c>NTinyCard</c>, which is put back to plain Colorless below);
/// a postfix returns the split material for the cards above. The shader is the mod's own
/// (<c>res://shared/companion_split_frame.gdshader</c>, from
/// <c>klee-mod/pck-src</c>): the base <c>hsv.gdshader</c>'s arithmetic, run
/// with both sets of numbers and mixed across x.
///
/// THE ATLAS. The frame <c>NCard</c> draws (<c>card_frame_attack_s.tres</c> and
/// siblings) is an <see cref="AtlasTexture"/> region of <c>ui_atlas_0.png</c>
/// (attack <c>Rect2(1320, 83, 598, 844)</c>, read from the game pck), so the
/// shader's UV runs across that region of the whole atlas, not 0..1. Each
/// material carries the region as <c>uv_rect</c>, computed here from the very
/// texture it will draw (<see cref="UvRectOf"/>), and is cached per (nation,
/// region): one per nation per card type. A plain texture's rect is
/// (0, 0, 1, 1).
///
/// SAFE TO MISS. A pck without the shader leaves every companion on the plain
/// Colorless frame (one warning from <see cref="KleePck.Path"/>).
/// </summary>
public static class CompanionSplitFrame
{
    /// <summary>The shader, relative to <c>res://</c>.</summary>
    public const string ShaderPath = "shared/companion_split_frame.gdshader";

    /// <summary>The tint a card's frame splits into, or null for no split.</summary>
    public static CardFrameColors.NationTint? TintFor(CardModel? card, CardPoolModel? visualPool) =>
        card != null && visualPool is CompanionCardPool
            ? CardFrameColors.NationFor(NationEmblem.NationOf(card))
            : null;

    /// <summary>An atlas region as the shader's <c>uv_rect</c>: (x, y, width,
    /// height) as fractions of the atlas.</summary>
    public static Vector4 UvRect(Rect2 region, Vector2 atlasSize) =>
        atlasSize.X > 0f && atlasSize.Y > 0f
            ? new Vector4(region.Position.X / atlasSize.X, region.Position.Y / atlasSize.Y,
                          region.Size.X / atlasSize.X, region.Size.Y / atlasSize.Y)
            : Whole;

    /// <summary>The rect of a plain (non-atlas) texture.</summary>
    public static readonly Vector4 Whole = new(0f, 0f, 1f, 1f);

    /// <summary>The <c>uv_rect</c> a material drawing <paramref name="texture"/> needs.</summary>
    public static Vector4 UvRectOf(Texture2D? texture) =>
        texture is AtlasTexture { Atlas: { } atlas } region
            ? UvRect(region.Region, atlas.GetSize())
            : Whole;

    private static readonly Dictionary<(string Nation, Vector4 Uv), ShaderMaterial> Materials = new();

    private static Shader? _shader;

    private static bool _shaderLoaded;

    private static Shader? LoadShader()
    {
        if (!_shaderLoaded)
        {
            _shaderLoaded = true;
            var path = KleePck.Path(ShaderPath);
            _shader = path == null ? null : ResourceLoader.Load<Shader>(path);
        }

        return _shader;
    }

    /// <summary>The split material for <paramref name="tint"/> drawn on
    /// <paramref name="texture"/>, or null when the shader is not in the pck.</summary>
    public static ShaderMaterial? MaterialFor(CardFrameColors.NationTint tint, Texture2D? texture)
    {
        var uv = UvRectOf(texture);
        if (Materials.TryGetValue((tint.Nation, uv), out var cached))
        {
            return cached;
        }

        var shader = LoadShader();
        if (shader == null)
        {
            return null;
        }

        var material = new ShaderMaterial { Shader = shader };
        material.SetShaderParameter("left_h", CardFrameColors.ColorlessH);
        material.SetShaderParameter("left_s", CardFrameColors.ColorlessS);
        material.SetShaderParameter("left_v", CardFrameColors.ColorlessV);
        material.SetShaderParameter("right_h", tint.H);
        material.SetShaderParameter("right_s", tint.S);
        material.SetShaderParameter("right_v", tint.V);
        material.SetShaderParameter("blend_start", CardFrameColors.SplitStart);
        material.SetShaderParameter("blend_width", CardFrameColors.SplitWidth);
        material.SetShaderParameter("uv_rect", uv);
        Materials[(tint.Nation, uv)] = material;
        return material;
    }

    private static bool _warned;

    /// <summary>Paint never throws into the caller (the frame getter runs
    /// inside card redraws); the first failure is logged once.</summary>
    internal static void Warn(Exception e)
    {
        if (_warned)
        {
            return;
        }

        _warned = true;
        Log.Warn($"[{KleeMod.ModId}] companion split frame: {e.Message}; "
               + "the card keeps the plain Colorless frame.");
    }
}

/// <summary>The card face: the frame <c>NCard</c> draws is <c>Model.Frame</c>
/// with <c>Model.FrameMaterial</c>, so the material is built for that texture.</summary>
[HarmonyPatch(typeof(CardModel), "get_FrameMaterial")]
internal static class CardModel_FrameMaterial_CompanionSplit_Patch
{
    private static void Postfix(CardModel __instance, ref Material __result)
    {
        try
        {
            var tint = CompanionSplitFrame.TintFor(__instance, __instance.VisualCardPool);
            if (tint == null)
            {
                return;
            }

            var split = CompanionSplitFrame.MaterialFor(tint.Value, __instance.Frame);
            if (split != null)
            {
                __result = split;
            }
        }
        catch (Exception e)
        {
            CompanionSplitFrame.Warn(e);
        }
    }
}

/// <summary>
/// THE DECK-LIST CHIP IS LEFT ON PLAIN COLORLESS, deliberately.
/// <c>NTinyCard</c> puts <c>card.FrameMaterial</c> on its <c>%CardBack</c>, a
/// plain neutral-grey texture (<c>run_history/card_back.png</c>) tinted by the
/// pool's <c>DeckEntryCardColor</c> modulate. The hsv arithmetic scales chroma,
/// and a grey has none, so a split material draws the chip exactly as plain
/// Colorless does (checked on the numpy render, 2026-10-20) while carrying the
/// card face's atlas <c>uv_rect</c>. Both entry points therefore put the pool's
/// own material back for a companion: <c>SetCard</c>, and <c>Set(pool, type,
/// rarity)</c>, which takes its material from the pool's first card. Kit chips
/// read apart by their modulate colour, as they always have.
/// </summary>
[HarmonyPatch]
internal static class NTinyCard_CompanionSplit_Patch
{
    private static readonly AccessTools.FieldRef<NTinyCard, TextureRect> CardBack =
        AccessTools.FieldRefAccess<NTinyCard, TextureRect>("_cardBack");

    [HarmonyPostfix]
    [HarmonyPatch(typeof(NTinyCard), nameof(NTinyCard.SetCard))]
    private static void SetCard(NTinyCard __instance, CardModel card)
    {
        try
        {
            var pool = card.VisualCardPool;
            if (CompanionSplitFrame.TintFor(card, pool) != null)
            {
                CardBack(__instance).Material = pool.FrameMaterial;
            }
        }
        catch (Exception e)
        {
            CompanionSplitFrame.Warn(e);
        }
    }

    [HarmonyPostfix]
    // Typed: Godot's GodotObject.Set(StringName, Variant) shares the name.
    [HarmonyPatch(typeof(NTinyCard), nameof(NTinyCard.Set),
                  new[] { typeof(CardPoolModel), typeof(CardType), typeof(CardRarity) })]
    private static void Set(NTinyCard __instance, CardPoolModel cardPool)
    {
        try
        {
            if (cardPool is CompanionCardPool)
            {
                CardBack(__instance).Material = cardPool.FrameMaterial;
            }
        }
        catch (Exception e)
        {
            CompanionSplitFrame.Warn(e);
        }
    }
}
