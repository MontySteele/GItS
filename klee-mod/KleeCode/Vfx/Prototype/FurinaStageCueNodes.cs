using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.HoverTips;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// THE CUES AND CHIPS, DRAWN. The picture half of
/// <see cref="FurinaStageCues"/>: it reads a <see cref="StageCueBoard"/> and
/// computes no number.
///
/// THE CUE sits where an enemy's intent sits over an enemy -- above the
/// body's hitbox, bobbing as <c>NIntent</c> bobs -- and carries the base
/// game's own intent icons (<c>intent_defend</c>, <c>intent_attack_1..5</c>,
/// the colourless energy icon) or the Salon's support glyph for a gift. The
/// number is drawn in the intent label's own font and outline, read off the
/// game's intent scene (<c>res://scenes/combat/intent.tscn</c>'s
/// <c>%Value</c>) when the card is built. The icon sits on a small
/// gold-edged card, one style for every performer; a damage icon is tinted
/// in its element's colour; an act that will do nothing is greyed.
///
/// THE CHIPS are coloured segments laid over a bar's own fill
/// (<c>NHealthBar</c>'s <c>%HpForegroundContainer</c>), at the bar's right
/// end, the way the base game previews poison: payments and taxes (gold),
/// then the fade (grey, with its "−N"), then the enemy's hits (dark red). A
/// bar that will empty wears the base game's death-blow glyph at its left end.
///
/// NOTHING HERE MAY THROW AT ITS CALLER. A cue that cannot be drawn is
/// skipped with one warning; the rules have already run.
///
/// QUARANTINED. <c>Vfx/Prototype/**</c> is Compile Remove'd without
/// <c>-p:PrototypeCards=true</c>, and nothing here runs in `dotnet test`
/// (no combat room exists there: <see cref="HasRoom"/> is false).
/// </summary>
public static class FurinaStageCueNodes
{
    private const string CueName = "KleeStageCue";
    private const string ChipsName = "KleeStageChips";
    private const string HoverShownMeta = "kleemod_cue_hover_shown";
    private const string HoverWiredMeta = "kleemod_cue_hover_wired";
    private const string HoverKeyMeta = "kleemod_cue_key";

    /// <summary>The card: 44 x 50, the icon inside, centred over the head.
    /// </summary>
    private static readonly Vector2 CardSize = new(44f, 50f);

    /// <summary>Clearance between the top of the hitbox and the card's
    /// bottom, and the bob, both <c>NIntent</c>'s (8 px up, 10 px swing).
    /// </summary>
    private const float HeadGap = 18f;

    private static readonly Color CardFill = new(0.09f, 0.11f, 0.19f, 0.92f);
    private static readonly Color CardEdge = new(0.86f, 0.70f, 0.36f, 1f);
    private static readonly Color Greyed = new(0.45f, 0.45f, 0.48f, 0.85f);
    private static readonly Color PriceGold = new(0.94f, 0.78f, 0.32f, 1f);
    private static readonly Color PaidChip = new(0.91f, 0.72f, 0.29f, 0.95f);
    private static readonly Color FadeChip = new(0.55f, 0.57f, 0.62f, 0.95f);
    private static readonly Color HitChip = new(0.45f, 0.03f, 0.07f, 0.95f);
    private static readonly Color FadeText = new(0.80f, 0.82f, 0.86f, 1f);

    private static bool _warned;

    /// <summary>Is there a combat room to draw into? False in every
    /// `dotnet test`.</summary>
    public static bool HasRoom => NCombatRoom.Instance != null;

    /// <summary>
    /// The colour of an element's damage, Genshin's own: the mod prints the
    /// element words in the game's gold, so there is no colour of the mod's
    /// to reuse and the cue takes the element's in-game one.
    /// </summary>
    internal static Color ElementColour(string element) => element switch
    {
        "Hydro" => new Color(0.30f, 0.76f, 0.95f),
        "Electro" => new Color(0.75f, 0.53f, 0.95f),
        "Geo" => new Color(0.96f, 0.72f, 0.20f),
        "Cryo" => new Color(0.62f, 0.87f, 0.93f),
        "Anemo" => new Color(0.45f, 0.86f, 0.70f),
        "Pyro" => new Color(0.94f, 0.47f, 0.22f),
        _ => new Color(1f, 1f, 1f),
    };

    /// <summary>Draw <paramref name="board"/> for this Furina, or take every
    /// cue and chip down where it is null.</summary>
    public static void Draw(Creature furina, StageCueBoard? board)
    {
        if (NCombatRoom.Instance is not { } room) return;
        try
        {
            Paint(room, furina, board);
        }
        catch (Exception e)
        {
            if (_warned) return;
            _warned = true;
            Log.Warn($"[{KleeMod.ModId}] stage: cues skipped: {e}");
        }
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    private static void Paint(NCombatRoom room, Creature furina,
                              StageCueBoard? board)
    {
        var seats = FurinaStageLedger.For(furina).Seats;
        var drawn = new HashSet<NCreature>();
        foreach (var seat in seats)
        {
            if (seat.Pet is not { IsDead: false } pet) continue;
            if (room.GetCreatureNode(pet) is not { } node) continue;
            drawn.Add(node);
            var cue = board?.Cues.FirstOrDefault(c => c.Key == seat.Key);
            var chips = board?.Bars.FirstOrDefault(c => c.Key == seat.Key);
            PaintCue(node, pet, cue);
            PaintChips(node, chips, pet.CurrentHp, pet.MaxHp);
        }
        // A body that left keeps no cue: its node is gone or going, but a
        // body the ledger no longer seats may still stand for a frame.
        foreach (var body in FurinaStagePets.BodiesOf(furina))
        {
            if (room.GetCreatureNode(body) is not { } node) continue;
            if (drawn.Contains(node)) continue;
            PaintCue(node, body, null);
            PaintChips(node, null, 0, 0);
        }
        if (room.GetCreatureNode(furina) is { } her)
        {
            PaintChips(her, board?.Furina, furina.CurrentHp, furina.MaxHp);
        }
    }

    // ------------------------------------------------------------------
    // THE CUE CARD
    // ------------------------------------------------------------------

    private static void PaintCue(NCreature node, Creature pet,
                                 StageCueView? cue)
    {
        var card = node.GetNodeOrNull<Control>(CueName);
        if (cue == null)
        {
            if (card != null)
            {
                ClearHover(card);
                card.Visible = false;
            }
            return;
        }
        card ??= BuildCard(node);
        card.Visible = true;
        card.SetMeta(HoverKeyMeta, cue.Key);
        Place(node, card);

        var greyed = cue.Greyed;
        if (card.GetNodeOrNull<TextureRect>("Holder/Icon") is { } icon)
        {
            icon.Texture = IconTexture(cue);
            icon.SelfModulate = greyed
                ? Greyed
                : cue.Icon == StageCueIcon.Attack
                    ? ElementColour(cue.Element)
                    : new Color(1f, 1f, 1f);
        }
        if (card.GetNodeOrNull<Label>("Holder/Number") is { } number)
        {
            number.Text = cue.Number < 0 ? "" : cue.Number.ToString();
            number.Modulate = greyed ? Greyed : new Color(1f, 1f, 1f);
        }
        if (card.GetNodeOrNull<Label>("Holder/All") is { } all)
        {
            all.Visible = cue.All;
            all.Modulate = greyed ? Greyed : new Color(1f, 1f, 1f);
        }
        if (card.GetNodeOrNull<Label>("Holder/Price") is { } price)
        {
            price.Visible = cue.Price > 0;
            price.Text = $"−{cue.Price}";
            price.Modulate = greyed ? Greyed : new Color(1f, 1f, 1f);
        }
        if (card.GetNodeOrNull<Label>("Holder/Times") is { } times)
        {
            times.Visible = cue.Times > 1;
            times.Text = $"×{cue.Times}";
        }
        if (card.GetNodeOrNull<Panel>("Holder/Card") is { } panel)
        {
            panel.Modulate = greyed ? new Color(1f, 1f, 1f, 0.7f)
                                    : new Color(1f, 1f, 1f, 1f);
        }
        WireHover(card, node, pet, cue);
    }

    /// <summary>Over the head, where <c>NIntent</c> sits over an enemy:
    /// the hitbox's top centre, a gap above it.</summary>
    private static void Place(NCreature node, Control card)
    {
        var box = node.Hitbox;
        var top = box.GlobalPosition + new Vector2(box.Size.X * 0.5f, 0f);
        var local = node.GetGlobalTransform().AffineInverse() * top;
        card.Position = new Vector2(local.X - CardSize.X * 0.5f,
                                    local.Y - HeadGap - CardSize.Y);
    }

    private static Control BuildCard(NCreature node)
    {
        // The root is placed over the head at every refresh; the HOLDER
        // inside it bobs, as NIntent's %IntentHolder does, so a refresh
        // never fights the bob.
        var card = new Control
        {
            Name = CueName,
            Size = CardSize,
            MouseFilter = Control.MouseFilterEnum.Stop,
            ZIndex = 1,
        };
        var holder = new Control
        {
            Name = "Holder",
            Size = CardSize,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        card.AddChild(holder);

        var face = new StyleBoxFlat
        {
            BgColor = CardFill,
            BorderColor = CardEdge,
        };
        face.SetBorderWidthAll(2);
        face.SetCornerRadiusAll(5);
        var panel = new Panel
        {
            Name = "Card",
            Size = CardSize,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        panel.AddThemeStyleboxOverride("panel", face);
        holder.AddChild(panel);

        holder.AddChild(new TextureRect
        {
            Name = "Icon",
            Position = new Vector2(4f, 3f),
            Size = new Vector2(CardSize.X - 8f, CardSize.X - 8f),
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        });

        var (font, size, outline, outlineColour) = IntentFont();
        size = Math.Clamp(size, 14, 24);
        holder.AddChild(Text("Number", font, size, outline, outlineColour,
                             new Color(1f, 1f, 1f),
                             new Vector2(0f, CardSize.Y - size - 4f),
                             new Vector2(CardSize.X, size + 4f),
                             HorizontalAlignment.Center));
        var all = Text("All", font, 12, 4, outlineColour, new Color(1f, 1f, 1f),
                       new Vector2(0f, -2f), new Vector2(CardSize.X - 3f, 14f),
                       HorizontalAlignment.Right);
        all.Text = "ALL";
        holder.AddChild(all);
        holder.AddChild(Text("Price", font, 16, 5, new Color(0.2f, 0.12f, 0f),
                             PriceGold, new Vector2(0f, CardSize.Y + 1f),
                             new Vector2(CardSize.X, 18f),
                             HorizontalAlignment.Center));
        holder.AddChild(Text("Times", font, 18, 6, outlineColour,
                             new Color(1f, 1f, 1f),
                             new Vector2(CardSize.X + 2f,
                                         CardSize.Y * 0.5f - 11f),
                             new Vector2(30f, 22f), HorizontalAlignment.Left));

        node.AddChildSafely(card);
        Bob(holder);
        return card;
    }

    private static Label Text(string name, Font? font, int size, int outline,
                              Color outlineColour, Color colour,
                              Vector2 position, Vector2 box,
                              HorizontalAlignment align)
    {
        var label = new Label
        {
            Name = name,
            Position = position,
            Size = box,
            HorizontalAlignment = align,
            VerticalAlignment = VerticalAlignment.Center,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        if (font != null) label.AddThemeFontOverride("font", font);
        label.AddThemeFontSizeOverride("font_size", size);
        label.AddThemeConstantOverride("outline_size", outline);
        label.AddThemeColorOverride("font_outline_color", outlineColour);
        label.AddThemeColorOverride("font_color", colour);
        return label;
    }

    /// <summary>
    /// The intent number's own font, size and outline, read off the game's
    /// intent scene's <c>%Value</c> label (a rich-text label) and never
    /// held: a room's resources die with the room (`EB-222`). A scene that
    /// cannot be read leaves the theme's font, and a plain outline.
    /// </summary>
    private static (Font? Font, int Size, int Outline, Color OutlineColour)
        IntentFont()
    {
        var fallback = ((Font?)null, 22, 8, new Color(0.1f, 0.1f, 0.1f));
        Node? scene = null;
        try
        {
            if (ResourceLoader.Load<PackedScene>("res://scenes/combat/intent.tscn")
                is not { } packed)
            {
                return fallback;
            }
            scene = packed.Instantiate(PackedScene.GenEditState.Disabled);
            if (scene.GetNodeOrNull<Control>("%Value") is not { } value)
            {
                return fallback;
            }
            return (value.GetThemeFont("normal_font"),
                    value.GetThemeFontSize("normal_font_size"),
                    value.GetThemeConstant("outline_size"),
                    value.GetThemeColor("font_outline_color"));
        }
        catch (Exception)
        {
            return fallback;
        }
        finally
        {
            scene?.Free();
        }
    }

    /// <summary><c>NIntent._Process</c>'s bob -- between 8 px up and 18 px
    /// up, one swing a second -- as a looping tween on the holder, so no
    /// per-frame script is added.</summary>
    private static void Bob(Control holder)
    {
        var tween = holder.CreateTween().SetLoops();
        tween.TweenProperty(holder, "position:y", -10f, 1.0)
            .From(0f)
            .SetTrans(Tween.TransitionType.Sine)
            .SetEase(Tween.EaseType.InOut);
        tween.TweenProperty(holder, "position:y", 0f, 1.0)
            .SetTrans(Tween.TransitionType.Sine)
            .SetEase(Tween.EaseType.InOut);
    }

    private static Texture2D? IconTexture(StageCueView cue)
    {
        string? path = cue.Icon switch
        {
            StageCueIcon.Block => ImageHelper.GetImagePath(
                "atlases/intent_atlas.sprites/intent_defend.tres"),
            StageCueIcon.Attack => ImageHelper.GetImagePath(
                "atlases/intent_atlas.sprites/attack/intent_attack_"
                + AttackTier(cue.Number * Math.Max(1, cue.Times)) + ".tres"),
            StageCueIcon.Energy => EnergyIconHelper.GetPath("colorless"),
            _ => KleePck.Path("furina/salon/glyph_support.png"),
        };
        if (path == null) return null;
        var texture = ResourceLoader.Load<Texture2D>(path);
        return texture != null && GodotObject.IsInstanceValid(texture)
            ? texture
            : null;
    }

    /// <summary><c>AttackIntent.GetTexture</c>'s five sizes, by the damage
    /// the cue shows in all.</summary>
    private static int AttackTier(int total) => total switch
    {
        < 5 => 1,
        < 10 => 2,
        < 20 => 3,
        < 40 => 4,
        _ => 5,
    };

    // ------------------------------------------------------------------
    // THE HOVER: the performer's own badge (its act, in its tip's words)
    // and the forecast line.
    // ------------------------------------------------------------------

    private static readonly Dictionary<ulong, (NCreature Node, Creature Pet, StageCueView Cue)>
        Hovers = new();

    private static void WireHover(Control card, NCreature node, Creature pet,
                                  StageCueView cue)
    {
        Hovers[card.GetInstanceId()] = (node, pet, cue);
        if (card.HasMeta(HoverWiredMeta)) return;
        card.SetMeta(HoverWiredMeta, true);
        card.MouseEntered += () => ShowHover(card);
        card.MouseExited += () => ClearHover(card);
        card.TreeExiting += () =>
        {
            Hovers.Remove(card.GetInstanceId());
        };
    }

    private static void ShowHover(Control card)
    {
        try
        {
            if (!Hovers.TryGetValue(card.GetInstanceId(), out var hover)) return;
            ClearHover(card);
            var tips = new List<IHoverTip>();
            if (hover.Pet.Powers.OfType<StagePerformerBadge>().FirstOrDefault()
                is { } badge)
            {
                tips.AddRange(badge.HoverTips);
            }
            tips.Add(new HoverTip(
                new LocString("card_keywords", "KLEEMOD-TURN_END_DOCKET.header"),
                hover.Cue.Forecast));
            NHoverTipSet.CreateAndShow(card, tips);
            card.SetMeta(HoverShownMeta, true);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] stage: cue hover skipped: {e}");
        }
    }

    private static void ClearHover(Control card)
    {
        if (!card.HasMeta(HoverShownMeta)) return;
        card.RemoveMeta(HoverShownMeta);
        NHoverTipSet.Remove(card);
    }

    // ------------------------------------------------------------------
    // THE CHIPS
    // ------------------------------------------------------------------

    private static void PaintChips(NCreature node, StageBarChips? chips,
                                   int current, int max)
    {
        var fill = FillOf(node);
        if (fill == null) return;
        var layer = fill.GetNodeOrNull<Control>(ChipsName);
        if (chips == null || !chips.Any || max <= 0 || current <= 0)
        {
            if (layer != null) layer.Visible = false;
            return;
        }
        layer ??= BuildLayer(fill);
        layer.Visible = true;
        foreach (var child in layer.GetChildren()) child.QueueFree();

        // From the bar's right end, in the order they happen. Each segment
        // is the forecast's number laid on the bar; one that would run past
        // the empty end stops there.
        var right = current;
        right = Segment(layer, fill, right, chips.Paid, max, PaidChip, null);
        right = Segment(layer, fill, right, chips.Faded, max, FadeChip,
                        chips.Faded > 0 ? $"−{chips.Faded}" : null);
        Segment(layer, fill, right, chips.Hits, max, HitChip, null);
        if (chips.Empties) Curtain(layer);
    }

    /// <summary>The bar's fill container, where the base game lays its
    /// poison and doom previews.</summary>
    private static Control? FillOf(NCreature node)
    {
        var display = node.GetNodeOrNull<Control>("%HealthBar");
        var bar = display?.GetNodeOrNull<NHealthBar>("%HealthBar");
        return bar?.GetNodeOrNull<Control>("%HpForegroundContainer");
    }

    private static Control BuildLayer(Control fill)
    {
        var layer = new Control
        {
            Name = ChipsName,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            AnchorLeft = 0f,
            AnchorTop = 0f,
            AnchorRight = 1f,
            AnchorBottom = 1f,
        };
        fill.AddChildSafely(layer);
        return layer;
    }

    /// <summary>One chip from <paramref name="right"/> leftward, as a share
    /// of the bar's maximum; returns its left end.</summary>
    private static int Segment(Control layer, Control fill, int right,
                               int amount, int max, Color colour,
                               string? label)
    {
        if (amount <= 0 || right <= 0) return right;
        var left = Math.Max(0, right - amount);
        var template = fill.GetNodeOrNull<Control>("%HpForeground");
        var chip = new ColorRect
        {
            Color = colour,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            AnchorLeft = (float)left / max,
            AnchorRight = (float)right / max,
            AnchorTop = template?.AnchorTop ?? 0f,
            AnchorBottom = template?.AnchorBottom ?? 1f,
            OffsetTop = template?.OffsetTop ?? 0f,
            OffsetBottom = template?.OffsetBottom ?? 0f,
        };
        layer.AddChild(chip);
        if (label != null)
        {
            var text = new Label
            {
                Text = label,
                MouseFilter = Control.MouseFilterEnum.Ignore,
                AnchorLeft = (float)left / max,
                AnchorRight = (float)right / max,
                AnchorTop = 0f,
                AnchorBottom = 0f,
                OffsetTop = -18f,
                OffsetBottom = 0f,
                HorizontalAlignment = HorizontalAlignment.Center,
                GrowHorizontal = Control.GrowDirection.Both,
            };
            text.AddThemeFontSizeOverride("font_size", 14);
            text.AddThemeConstantOverride("outline_size", 5);
            text.AddThemeColorOverride("font_outline_color",
                                       new Color(0.1f, 0.1f, 0.12f));
            text.AddThemeColorOverride("font_color", FadeText);
            layer.AddChild(text);
        }
        return left;
    }

    /// <summary>The bar will empty: the base game's death-blow glyph at its
    /// left end.</summary>
    private static void Curtain(Control layer)
    {
        var path = ImageHelper.GetImagePath(
            "atlases/intent_atlas.sprites/intent_death_blow.tres");
        var texture = ResourceLoader.Load<Texture2D>(path);
        if (texture == null || !GodotObject.IsInstanceValid(texture)) return;
        layer.AddChild(new TextureRect
        {
            Texture = texture,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
            AnchorLeft = 0f,
            AnchorRight = 0f,
            AnchorTop = 0.5f,
            AnchorBottom = 0.5f,
            OffsetLeft = -22f,
            OffsetRight = 0f,
            OffsetTop = -11f,
            OffsetBottom = 11f,
        });
    }
}
