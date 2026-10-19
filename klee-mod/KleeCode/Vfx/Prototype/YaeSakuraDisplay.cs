using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using Godot;
using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Cards.Holders;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.HoverTips;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.addons.mega_text;

namespace KleeMod.Vfx;

/// <summary>What hovering a planting card says on one shrine slot.</summary>
public enum YaeSlotPreview
{
    None = 0,

    /// <summary>A new Sakura goes into this empty slot.</summary>
    Plants = 1,

    /// <summary>A same-kind plant into a full shrine refreshes this one and
    /// gives it a Level.</summary>
    Refreshes = 2,

    /// <summary>This one withers and the new Sakura takes its place (a
    /// full-shrine plant of another kind, or Replanting's oldest).</summary>
    Replaces = 3,
}

/// <summary>One shrine slot as the display draws it. PURE.</summary>
/// <param name="Slot">0 for the oldest, as the badges count.</param>
/// <param name="Empty">No Sakura stands here.</param>
/// <param name="Pips">Turns left drawn as pips (0 to 3); 0 when
/// <paramref name="TurnsText"/> is drawn instead.</param>
/// <param name="TurnsText">The number past three, or the infinity mark when
/// it never withers; null while pips say it.</param>
/// <param name="Marks">Its Annotations, in the order written.</param>
/// <param name="Oldest">Outlined: the oldest acts first.</param>
public readonly record struct YaeSakuraSlotView(
    int Slot, bool Empty, YaeSakuraKind Kind, int Level, int Pips,
    string? TurnsText, bool Infinite, IReadOnlyList<YaeAnnotation> Marks,
    bool Oldest, YaeSlotPreview Preview);

/// <summary>
/// THE SAKURA DISPLAY'S VIEW MODEL (pick 3 (a) of
/// <c>review/active/yae-pool-to-78-2026-10-15.md</c>, ruled 2026-10-15).
/// Every decision the row draws, PURE, so the headless suite pins it: how
/// many slots, which are empty, each Sakura's kind, Level, turns (pips, a
/// number past three, an infinity mark when it never withers), its
/// Annotation marks, the oldest, and what a planting card would do to each
/// slot. <see cref="YaeSakuraDisplay"/> is the Godot half and computes
/// nothing.
/// </summary>
public static class YaeSakuraSlots
{
    /// <summary>Turns drawn as pips up to this many; past it, a number.</summary>
    public const int MaxPips = 3;

    /// <summary>The mark for a Sakura that never withers.</summary>
    public const string InfinityMark = "∞";

    public const string PlantsText = "Plants here";
    public const string RefreshesText = "Refreshes this Sakura";
    public const string ReplacesText = "Replaces this Sakura";

    /// <summary>The hover title on a slot (<c>KleeMod</c>'s keyword table).</summary>
    public const string SlotTitleKey = "KLEEMOD-YAE_SHRINE_SLOT";

    /// <summary>The one-line rules on a standing Sakura's slot.</summary>
    public const string RulesLine =
        "Each Sakura acts at the end of your turn, oldest first, then loses "
      + "a turn. At 0 it acts again and withers.";

    /// <summary>The one-line rules on an empty slot.</summary>
    public const string EmptyLine =
        "An empty slot in your shrine. Planting a Sakura fills it.";

    /// <summary>One slot per Sakura the shrine may hold (3, more with Sakura
    /// Channeling or Fox Ofuda), and never fewer than stand. PURE.</summary>
    public static int SlotCount(int standing, int cap) =>
        Math.Max(Math.Max(0, cap), Math.Max(0, standing));

    /// <summary>How a timer reads: pips up to three, the number past it,
    /// the infinity mark when it never withers (Eternity, or Deadline
    /// Extension, whose timer does not tick). PURE.</summary>
    public static (int Pips, string? Text, bool Infinite) Turns(
        int turnsLeft, bool neverWithers)
    {
        if (neverWithers) return (0, InfinityMark, true);
        var turns = Math.Max(0, turnsLeft);
        return turns <= MaxPips
            ? (turns, null, false)
            : (0, turns.ToString(CultureInfo.InvariantCulture), false);
    }

    /// <summary>
    /// The row: the standing Sakura oldest first, then the empty slots.
    /// <paramref name="eternal"/>: Eternity is on her. <paramref name="preview"/>:
    /// a planting card's per-slot preview (<see cref="Preview"/>), or null.
    /// PURE.
    /// </summary>
    public static IReadOnlyList<YaeSakuraSlotView> Slots(
        IReadOnlyList<YaeSakura> standing, int cap, bool eternal,
        IReadOnlyList<YaeSlotPreview>? preview = null)
    {
        var n = SlotCount(standing.Count, cap);
        var slots = new List<YaeSakuraSlotView>(n);
        for (var i = 0; i < n; i++)
        {
            var shown = preview != null && i < preview.Count
                ? preview[i] : YaeSlotPreview.None;
            if (i >= standing.Count)
            {
                slots.Add(new YaeSakuraSlotView(
                    i, true, YaeSakuraKind.Thunder, 0, 0, null, false,
                    Array.Empty<YaeAnnotation>(), false, shown));
                continue;
            }
            var s = standing[i];
            var (pips, text, infinite) = Turns(
                s.TurnsLeft, eternal || s.Has(YaeAnnotation.DeadlineExtension));
            slots.Add(new YaeSakuraSlotView(
                i, false, s.Kind, s.Level, pips, text, infinite,
                s.Annotations.ToList(), i == 0, shown));
        }
        return slots;
    }

    /// <summary>
    /// The Sakura a planting card plants, in order, read off the shrine as
    /// its play would: "Plant N" (<paramref name="amount"/>), one at a Level,
    /// Replanting's one of the oldest's kind, Genre Shift's missing kinds,
    /// Narukami Bloom's until full. PURE.
    /// </summary>
    public static IReadOnlyList<YaeSakuraKind> PlantsOf(
        YaePlantShape shape, YaeSakuraKind kind, int amount,
        IReadOnlyList<YaeSakura> standing, int cap) => shape switch
    {
        YaePlantShape.Plant => Enumerable.Repeat(kind, Math.Max(0, amount)).ToList(),
        YaePlantShape.PlantLevel => new[] { kind },
        YaePlantShape.Replant => standing.Count == 0
            ? Array.Empty<YaeSakuraKind>() : new[] { standing[0].Kind },
        YaePlantShape.PlantMissing =>
            new[] { YaeSakuraKind.Thunder, YaeSakuraKind.Foxfire, YaeSakuraKind.Kitsune }
                .Where(k => standing.All(s => s.Kind != k)).ToList(),
        YaePlantShape.PlantUntilFull => Enumerable.Repeat(
            YaeSakuraKind.Thunder, Math.Max(0, cap - standing.Count)).ToList(),
        _ => Array.Empty<YaeSakuraKind>(),
    };

    /// <summary>
    /// WHAT A PLANTING CARD DOES TO EACH SLOT, walked one plant at a time by
    /// the ledger's own rule (<see cref="YaeShrineLedger.Plant(int, int?, YaeAnnotation, int, YaeSakuraKind, int)"/>):
    /// into room, a new Sakura (the next empty slot says "Plants here"); into
    /// a full shrine, the Sakura closest to withering
    /// (<see cref="YaeShrineLedger.WithersSooner"/>) is refreshed by its own
    /// kind or replaced by another. Replanting replaces the oldest first.
    /// One entry per slot (<see cref="SlotCount"/>). PURE.
    /// </summary>
    public static IReadOnlyList<YaeSlotPreview> Preview(
        IReadOnlyList<YaeSakura> standing, int cap, YaePlantShape shape,
        IReadOnlyList<YaeSakuraKind> plants)
    {
        var result = Enumerable.Repeat(YaeSlotPreview.None,
                                       SlotCount(standing.Count, cap)).ToArray();
        var live = standing
            .Select((s, i) => new Walk(i, s.Kind, s.TurnsLeft,
                                       s.Has(YaeAnnotation.DeadlineExtension)))
            .ToList();
        if (shape == YaePlantShape.Replant)
        {
            if (live.Count == 0) return result;
            result[0] = YaeSlotPreview.Replaces;
            live.RemoveAt(0);
        }
        foreach (var kind in plants)
        {
            if (live.Count >= cap && live.Count > 0)
            {
                var at = 0;
                for (var i = 1; i < live.Count; i++)
                {
                    if (YaeShrineLedger.WithersSooner(
                            live[i].Deadline, live[i].Turns,
                            live[at].Deadline, live[at].Turns))
                        at = i;
                }
                var target = live[at];
                if (target.Kind == kind)
                {
                    target.Turns = Math.Max(target.Turns, YaeLaw.SakuraTurns);
                    if (target.Orig >= 0 && result[target.Orig] == YaeSlotPreview.None)
                        result[target.Orig] = YaeSlotPreview.Refreshes;
                    continue;
                }
                live.RemoveAt(at);
                if (target.Orig >= 0) result[target.Orig] = YaeSlotPreview.Replaces;
            }
            live.Add(new Walk(-1, kind, YaeLaw.SakuraTurns, false));
        }
        // The net Sakura added fill the empty slots, left to right.
        for (var i = standing.Count; i < Math.Min(live.Count, result.Length); i++)
        {
            result[i] = YaeSlotPreview.Plants;
        }
        return result;
    }

    private sealed class Walk
    {
        public Walk(int orig, YaeSakuraKind kind, int turns, bool deadline)
        {
            Orig = orig;
            Kind = kind;
            Turns = turns;
            Deadline = deadline;
        }

        public int Orig { get; }
        public YaeSakuraKind Kind { get; }
        public int Turns { get; set; }
        public bool Deadline { get; }
    }

    /// <summary>The words under a previewed slot, or null. PURE.</summary>
    public static string? PreviewText(YaeSlotPreview preview) => preview switch
    {
        YaeSlotPreview.Plants => PlantsText,
        YaeSlotPreview.Refreshes => RefreshesText,
        YaeSlotPreview.Replaces => ReplacesText,
        _ => null,
    };

    /// <summary>
    /// The preview a card in hand gives <paramref name="yae"/>'s row now:
    /// null for a card that plants nothing (no <see cref="ISakuraPlantShapeCard"/>)
    /// or anyone not Yae. Reads the card's own YmAmount, as its play does.
    /// </summary>
    public static IReadOnlyList<YaeSlotPreview>? PreviewFor(CardModel? card, Creature? yae)
    {
        if (card is not ISakuraPlantShapeCard shape || yae == null || !YaeShrine.Live(yae))
            return null;
        var standing = YaeShrineLedger.For(yae).Standing;
        var cap = YaeShrine.MaxSakura(yae);
        var plants = card is ISakuraPlantMixCard mix
            ? mix.SakuraPlantKinds
            : PlantsOf(shape.SakuraPlantShape, shape.SakuraPlantKind,
                       YaeCards.Var(card, "YmAmount"), standing, cap);
        return Preview(standing, cap, shape.SakuraPlantShape, plants);
    }

    /// <summary>The glyph a kind wears: the strike Sakura her Sesshou Sakura
    /// badge, the Foxfire Sakura the Spiritfox icon Foxfire Lure wears, the
    /// Kitsune Sakura the red kitsune doll Kitsune Mask wears. PURE.</summary>
    public static string GlyphPathFor(YaeSakuraKind kind) => kind switch
    {
        YaeSakuraKind.Foxfire => "yae/powers/foxfire_lure.png",
        YaeSakuraKind.Kitsune => "yae/relics/kitsune_mask.png",
        _ => "yae/powers/sakura.png",
    };

    /// <summary>The letter on an Annotation's mark. PURE.</summary>
    public static string MarkLetter(YaeAnnotation annotation) => annotation switch
    {
        YaeAnnotation.RedInk => "R",
        YaeAnnotation.FoxFire => "F",
        YaeAnnotation.DeadlineExtension => "D",
        _ => "",
    };
}

/// <summary>
/// YAE'S SAKURA DISPLAY (pick 3 (a) of
/// <c>review/active/yae-pool-to-78-2026-10-15.md</c>, ruled 2026-10-15):
/// "a row of slots beside Yae, one per shrine slot (3, or 5 with Sakura
/// Channeling); empty slots shown, so a full shrine is plain. Each Sakura:
/// its kind by colour and icon (strike, Kitsune, Foxfire), its Level as the
/// big number, its turns left as pips (a number past three, an infinity mark
/// under Eternity), a small mark per Annotation. The oldest is outlined.
/// Hovering a planting card previews it: 'refreshes this Sakura' or
/// 'replaces this Sakura'. Hover on a slot gives the one-line rules."
///
/// WHERE: over her head, a child of her <c>NCreature</c>, placed off the
/// hitbox at every paint -- the spot Furina's stage cues take over a body
/// (<see cref="FurinaStageCueNodes"/>), and where the base game's Defect
/// keeps his orbs. Whether it collides with anything is a live question.
///
/// THE LEDGER IS THE TRUTH and the badges stay. Each Sakura's badge
/// (<see cref="SakuraBadgePower"/>) is still on her status strip, its
/// tooltip unchanged (the seat page reads it), and a slot's hover shows the
/// one-line rules and then that badge's own tips. The feed is
/// <see cref="SakuraBadge.Sync"/>, the funnel every shrine move ends in, plus
/// a power landing on her (Sakura Channeling, Eternity) and a card in hand
/// hovered, focused or held (Varka's dial's doors, <see cref="VarkaOathDial"/>).
///
/// NO CONTROLLER FOCUS (`EB-300`): display only, out of the focus walk. The
/// preview does follow a controller's focused card.
///
/// The <see cref="YaeSakuraSlots"/> pins are the decisions; the look is a
/// frame on the next deploy.
/// </summary>
public static class YaeSakuraDisplay
{
    internal const string RootName = "KleeModYaeSakuraRow";

    internal const float SlotSide = 56f;
    internal const float SlotGap = 6f;
    internal const float HeadGap = 16f;
    internal const float PreviewHeight = 30f;
    private const int LevelFontSize = 26;
    private const int SmallFontSize = 13;
    private const float PipSide = 8f;

    private const string SlotMeta = "kleemod_yae_slot";
    private const string HoverShownMeta = "kleemod_yae_slot_hover_shown";

    private static readonly Color SlotFill = new(0.09f, 0.08f, 0.14f, 0.88f);
    private static readonly Color EmptyEdge = new(0.55f, 0.55f, 0.6f, 0.55f);
    private static readonly Color PipOn = new(0.98f, 0.93f, 0.80f, 1f);
    private static readonly Color PipOff = new(0.98f, 0.93f, 0.80f, 0.18f);

    /// <summary>The local Yae, set when the row is painted.</summary>
    private static Creature? _seat;

    private static CardModel? _hovered;
    private static CardModel? _held;

    private static readonly HashSet<string> WarnedGlyphs = new();
    private static bool _warned;

    /// <summary>A kind's colour: the strike Sakura Electro's, the Foxfire
    /// Sakura Pyro's, the Kitsune Sakura (Block) Hydro's.</summary>
    internal static Color KindColour(YaeSakuraKind kind) => kind switch
    {
        YaeSakuraKind.Foxfire => FurinaStageCueNodes.ElementColour("Pyro"),
        YaeSakuraKind.Kitsune => FurinaStageCueNodes.ElementColour("Hydro"),
        _ => FurinaStageCueNodes.ElementColour("Electro"),
    };

    internal static Color MarkColour(YaeAnnotation annotation) => annotation switch
    {
        YaeAnnotation.RedInk => new Color(0.93f, 0.25f, 0.25f),
        YaeAnnotation.FoxFire => new Color(0.98f, 0.62f, 0.25f),
        YaeAnnotation.DeadlineExtension => new Color(0.45f, 0.86f, 0.70f),
        _ => new Color(1f, 1f, 1f),
    };

    // --------------------------------------------------------- lifecycle --

    /// <summary>The row for the LOCAL Yae, from the <c>NCombatUi.Activate</c>
    /// postfix <c>GaugeBridge</c> installs.</summary>
    public static void Setup(CombatState? state)
    {
        if (state == null || LocalContext.NetId is not { } netId) return;
        Player? me;
        try
        {
            me = state.GetPlayer(netId);
        }
        catch (InvalidOperationException)
        {
            return;
        }
        Refresh(me?.Creature);
    }

    /// <summary>Re-read the shrine and redraw. Headless-safe: nothing runs
    /// without a combat room, and nothing here throws at its caller.</summary>
    public static void Refresh(Creature? yae)
    {
        if (yae == null || NCombatRoom.Instance is not { } room) return;
        try
        {
            if (!YaeShrine.Live(yae) || yae.CombatState == null) return;
            if (yae.Player is not { } player || !LocalContext.IsMe(player)) return;
            _seat = yae;
            Paint(room, yae, player);
        }
        catch (Exception e)
        {
            if (_warned) return;
            _warned = true;
            Log.Warn($"[{KleeMod.ModId}] sakura row: skipped: {e}");
        }
    }

    /// <summary>A card in hand hovered or focused, or no longer.</summary>
    internal static void NoteHover(CardModel? card, bool hovered)
    {
        if (hovered)
        {
            if (!OwnedByLocalYae(card)) return;
            _hovered = card;
        }
        else if (ReferenceEquals(_hovered, card))
        {
            _hovered = null;
        }
        else
        {
            return;
        }
        Refresh(_seat);
    }

    /// <summary>A card picked up, or put down (null).</summary>
    internal static void NoteHeld(CardModel? card)
    {
        if (card != null && !OwnedByLocalYae(card)) return;
        if (card == null && _held == null) return;
        if (card == null && ReferenceEquals(_hovered, _held)) _hovered = null;
        _held = card;
        Refresh(_seat);
    }

    internal static bool OwnedByLocalYae(CardModel? card)
    {
        try
        {
            var owner = card?.Owner?.Creature;
            return owner != null && YaeShrine.Live(owner) && owner.Player is { } p
                   && LocalContext.IsMe(p);
        }
        catch (Exception)
        {
            return false;
        }
    }

    /// <summary>Forget the seat and the hover when the combat UI stands
    /// down; the row itself dies with her creature node.</summary>
    internal static void Forget()
    {
        _seat = null;
        _hovered = null;
        _held = null;
    }

    // ----------------------------------------------------------- drawing --

    private static IReadOnlyList<YaeSlotPreview>? PreviewOn(Player player, Creature yae)
    {
        var card = _held ?? _hovered;
        try
        {
            return card != null && ReferenceEquals(card.Owner, player)
                ? YaeSakuraSlots.PreviewFor(card, yae) : null;
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static void Paint(NCombatRoom room, Creature yae, Player player)
    {
        if (room.GetCreatureNode(yae) is not { } node) return;
        var row = node.GetNodeOrNull<Control>(RootName);
        if (row == null)
        {
            row = new Control
            {
                Name = RootName,
                MouseFilter = Control.MouseFilterEnum.Ignore,
                FocusMode = Control.FocusModeEnum.None,
                ZIndex = 1,
            };
            node.AddChildSafely(row);
        }

        var ledger = YaeShrineLedger.For(yae);
        var slots = YaeSakuraSlots.Slots(
            ledger.Standing, YaeShrine.MaxSakura(yae),
            yae.GetPowerAmount<EternityPower>() > 0, PreviewOn(player, yae));

        for (var i = 0; i < slots.Count; i++)
        {
            var slot = row.GetNodeOrNull<Control>("Slot" + i) ?? BuildSlot(row, i);
            slot.Visible = true;
            slot.Position = new Vector2(i * (SlotSide + SlotGap), 0f);
            PaintSlot(slot, slots[i]);
        }
        // A cap that fell (never in practice) hides the extra slots.
        for (var i = slots.Count; row.GetNodeOrNull<Control>("Slot" + i) is { } extra; i++)
        {
            ClearHover(extra);
            extra.Visible = false;
        }
        row.SetFocusBehaviorRecursive(Control.FocusBehaviorRecursiveEnum.Disabled);
        Place(node, row, slots.Count);
    }

    /// <summary>Centred over her head, a gap above the hitbox.</summary>
    private static void Place(NCreature node, Control row, int count)
    {
        var width = count * SlotSide + Math.Max(0, count - 1) * SlotGap;
        var height = SlotSide + PreviewHeight;
        row.Size = new Vector2(width, height);
        var box = node.Hitbox;
        var top = box.GlobalPosition + new Vector2(box.Size.X * 0.5f, 0f);
        var local = node.GetGlobalTransform().AffineInverse() * top;
        row.Position = new Vector2(local.X - width * 0.5f,
                                   local.Y - HeadGap - height);
    }

    private static Control BuildSlot(Control row, int index)
    {
        var slot = new Control
        {
            Name = "Slot" + index,
            // The mouse is the way in (the one-line rules); no focus.
            MouseFilter = Control.MouseFilterEnum.Stop,
            FocusMode = Control.FocusModeEnum.None,
            Size = new Vector2(SlotSide, SlotSide),
        };
        slot.SetMeta(SlotMeta, index);

        var outline = RingPanel("Oldest", StsColors.gold, 3, -4f, SlotSide + 8f, false);
        slot.AddChildSafely(outline);

        var frame = RingPanel("Frame", EmptyEdge, 2, 0f, SlotSide, true);
        slot.AddChildSafely(frame);

        slot.AddChildSafely(new TextureRect
        {
            Name = "Icon",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
            Position = new Vector2(6f, 6f),
            Size = new Vector2(SlotSide - 12f, SlotSide - 12f),
            SelfModulate = new Color(1f, 1f, 1f, 0.6f),
        });

        var level = TextLabel("Level", LevelFontSize);
        level.Position = new Vector2(0f, 4f);
        level.Size = new Vector2(SlotSide, SlotSide - 18f);
        slot.AddChildSafely(level);

        for (var p = 0; p < YaeSakuraSlots.MaxPips; p++)
        {
            var pip = RingPanel("Pip" + p, PipOn, 0, 0f, PipSide, true);
            var span = YaeSakuraSlots.MaxPips * PipSide + (YaeSakuraSlots.MaxPips - 1) * 4f;
            pip.Position = new Vector2((SlotSide - span) / 2f + p * (PipSide + 4f),
                                       SlotSide - PipSide - 5f);
            slot.AddChildSafely(pip);
        }

        var turns = TextLabel("Turns", SmallFontSize);
        turns.Position = new Vector2(0f, SlotSide - SmallFontSize - 8f);
        turns.Size = new Vector2(SlotSide, SmallFontSize + 4f);
        slot.AddChildSafely(turns);

        for (var m = 0; m < 3; m++)
        {
            var mark = TextLabel("Mark" + m, SmallFontSize - 1);
            mark.HorizontalAlignment = HorizontalAlignment.Center;
            mark.Position = new Vector2(SlotSide - 14f - m * 12f, 1f);
            mark.Size = new Vector2(12f, SmallFontSize + 2f);
            slot.AddChildSafely(mark);
        }

        var preview = TextLabel("Preview", SmallFontSize - 1);
        preview.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        preview.Position = new Vector2(-SlotGap / 2f, SlotSide + 2f);
        preview.Size = new Vector2(SlotSide + SlotGap, PreviewHeight);
        preview.VerticalAlignment = VerticalAlignment.Top;
        preview.AddThemeColorOverride(ThemeConstants.Label.FontColor, StsColors.gold);
        slot.AddChildSafely(preview);

        slot.MouseEntered += () => ShowHover(slot);
        slot.MouseExited += () => ClearHover(slot);
        slot.TreeExiting += () => ClearHover(slot);
        row.AddChildSafely(slot);
        return slot;
    }

    private static Panel RingPanel(string name, Color edge, int width, float at,
                                   float side, bool fill)
    {
        var box = new StyleBoxFlat
        {
            DrawCenter = fill,
            BgColor = width == 0 ? edge : SlotFill,
            BorderColor = edge,
            AntiAliasing = true,
        };
        box.SetBorderWidthAll(width);
        box.SetCornerRadiusAll(Mathf.CeilToInt(side / (width == 0 ? 2f : 5f)));
        var panel = new Panel
        {
            Name = name,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            Position = new Vector2(at, at),
            Size = new Vector2(side, side),
        };
        panel.AddThemeStyleboxOverride("panel", box);
        return panel;
    }

    private static Label TextLabel(string name, int size)
    {
        var label = new Label
        {
            Name = name,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
        };
        label.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize, size);
        label.AddThemeConstantOverride(ThemeConstants.Label.OutlineSize,
                                       Math.Max(3, size / 4));
        label.AddThemeColorOverride(ThemeConstants.Label.FontOutlineColor,
                                    FurinaCounterFace.OutlineColour);
        label.AddThemeColorOverride(ThemeConstants.Label.FontColor, StsColors.cream);
        return label;
    }

    private static void PaintSlot(Control slot, YaeSakuraSlotView view)
    {
        var previewed = view.Preview != YaeSlotPreview.None;
        if (slot.GetNodeOrNull<Panel>("Frame") is { } frame
            && frame.GetThemeStylebox("panel") is StyleBoxFlat box)
        {
            box.BorderColor = previewed ? StsColors.gold
                : view.Empty ? EmptyEdge : KindColour(view.Kind);
            box.BgColor = view.Empty ? new Color(SlotFill, 0.45f) : SlotFill;
        }
        if (slot.GetNodeOrNull<Panel>("Oldest") is { } oldest) oldest.Visible = view.Oldest;
        if (slot.GetNodeOrNull<TextureRect>("Icon") is { } icon)
        {
            if (view.Empty) icon.Visible = false;
            else SetGlyph(icon, view.Kind);
        }
        if (slot.GetNodeOrNull<Label>("Level") is { } level)
        {
            level.Visible = !view.Empty;
            level.Text = view.Level.ToString(CultureInfo.InvariantCulture);
        }
        for (var p = 0; p < YaeSakuraSlots.MaxPips; p++)
        {
            if (slot.GetNodeOrNull<Panel>("Pip" + p) is not { } pip) continue;
            pip.Visible = !view.Empty && view.TurnsText == null;
            pip.Modulate = p < view.Pips ? PipOn : PipOff;
        }
        if (slot.GetNodeOrNull<Label>("Turns") is { } turns)
        {
            turns.Visible = !view.Empty && view.TurnsText != null;
            turns.Text = view.TurnsText ?? string.Empty;
        }
        for (var m = 0; m < 3; m++)
        {
            if (slot.GetNodeOrNull<Label>("Mark" + m) is not { } mark) continue;
            var has = !view.Empty && m < view.Marks.Count;
            mark.Visible = has;
            if (!has) continue;
            mark.Text = YaeSakuraSlots.MarkLetter(view.Marks[m]);
            mark.AddThemeColorOverride(ThemeConstants.Label.FontColor,
                                       MarkColour(view.Marks[m]));
        }
        if (slot.GetNodeOrNull<Label>("Preview") is { } preview)
        {
            var text = YaeSakuraSlots.PreviewText(view.Preview);
            preview.Visible = text != null;
            preview.Text = text ?? string.Empty;
        }
    }

    /// <summary>Resolved fresh on every paint, never cached across a scene
    /// (`EB-222`), and never throws at its caller.</summary>
    private static void SetGlyph(TextureRect icon, YaeSakuraKind kind)
    {
        var glyph = YaeSakuraSlots.GlyphPathFor(kind);
        try
        {
            var path = KleePck.Path(glyph);
            var texture = path == null ? null : ResourceLoader.Load<Texture2D>(path);
            if (texture == null || !GodotObject.IsInstanceValid(texture))
            {
                if (WarnedGlyphs.Add(glyph))
                    Log.Warn($"[{KleeMod.ModId}] sakura row: no live {glyph}; "
                           + "drawing the slot with no glyph.");
                icon.Visible = false;
                return;
            }
            icon.Texture = texture;
            icon.Visible = true;
        }
        catch (Exception e)
        {
            icon.Visible = false;
            if (WarnedGlyphs.Add(glyph))
                Log.Warn($"[{KleeMod.ModId}] sakura row: glyph skipped: {e.Message}");
        }
    }

    // ------------------------------------------------------------- hover --

    /// <summary>The one-line rules, then the slot's own badge's tooltip (the
    /// sentence the seat page reads), and the full-shrine rule when full.
    /// </summary>
    private static void ShowHover(Control slot)
    {
        try
        {
            if (_seat is not { } yae || !slot.HasMeta(SlotMeta)) return;
            ClearHover(slot);
            var index = slot.GetMeta(SlotMeta).AsInt32();
            var standing = YaeShrineLedger.For(yae).Count;
            var title = new LocString(Cards.ArmKeywordTips.KeywordTable,
                                      YaeSakuraSlots.SlotTitleKey + ".title");
            var tips = new List<IHoverTip>
            {
                new HoverTip(title, index < standing
                    ? YaeSakuraSlots.RulesLine : YaeSakuraSlots.EmptyLine),
            };
            if (index < standing
                && yae.Powers.OfType<SakuraBadgePower>()
                    .FirstOrDefault(b => b.Slot == index) is { } badge)
            {
                tips.AddRange(badge.HoverTips);
            }
            if (YaeShrine.Full(yae))
            {
                tips.Add(new HoverTip(
                    new LocString(Cards.ArmKeywordTips.KeywordTable,
                                  Cards.ArmKeywordTips.FullShrineKey + ".title"),
                    Cards.ArmKeywordTips.YaeFullShrineTip));
            }
            NHoverTipSet.CreateAndShow(slot, tips, HoverTip.GetHoverTipAlignment(slot));
            slot.SetMeta(HoverShownMeta, true);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] sakura row: hover skipped: {e.Message}");
        }
    }

    private static void ClearHover(Control slot)
    {
        if (!GodotObject.IsInstanceValid(slot) || !slot.HasMeta(HoverShownMeta)) return;
        slot.RemoveMeta(HoverShownMeta);
        NHoverTipSet.Remove(slot);
    }
}

/// <summary>The row's statics end with the combat; the node dies with her
/// creature node.</summary>
// lint: no-seat: pure static teardown of this file's own fields; it touches
// no run state, player or creature. The scope lives at the one door that
// draws (`YaeSakuraDisplay.Refresh`, through `YaeShrine.Live` and
// `LocalContext.IsMe`).
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Deactivate))]
internal static class NCombatUi_Deactivate_YaeSakuraDisplay_Patch
{
    [HarmonyPostfix]
    public static void Postfix() => YaeSakuraDisplay.Forget();
}

/// <summary>A power landing on her (Sakura Channeling's slots, Eternity's
/// infinity mark): redraw.</summary>
[HarmonyPatch(typeof(NPowerContainer), "Add")]
internal static class NPowerContainer_Add_YaeSakuraDisplay_Patch
{
    [HarmonyPostfix]
    public static void Postfix(PowerModel power)
    {
        try
        {
            if (power is not (SakuraChannelingPower or EternityPower)) return;
            var owner = power.IsMutable ? power.Owner : null;
            if (owner == null || !YaePrototype.IsYae(owner)) return;
            YaeSakuraDisplay.Refresh(owner);
        }
        catch (Exception)
        {
            // Display only.
        }
    }
}

/// <summary>A card in hand hovered or focused (mouse or controller): the
/// row previews what its plant would do.</summary>
[HarmonyPatch(typeof(NHandCardHolder), "DoCardHoverEffects")]
internal static class NHandCardHolder_Hover_YaeSakuraDisplay_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NHandCardHolder __instance, bool isHovered)
    {
        try
        {
            var card = __instance.CardNode?.Model;
            if (!YaePrototype.IsYae(card?.Owner?.Creature))
            {
                // Another seat's card: only its unhover can matter.
                if (!isHovered) YaeSakuraDisplay.NoteHover(card, false);
                return;
            }
            YaeSakuraDisplay.NoteHover(card, isHovered);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] sakura row: hover preview skipped: {e.Message}");
        }
    }
}

/// <summary>A card picked up with the mouse keeps the preview while held.</summary>
[HarmonyPatch(typeof(NMouseCardPlay), nameof(NMouseCardPlay.Start))]
internal static class NMouseCardPlay_Start_YaeSakuraDisplay_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NMouseCardPlay __instance) =>
        YaeSakuraDisplayHold.Pick(__instance);
}

/// <summary>A card picked up with the controller.</summary>
[HarmonyPatch(typeof(NControllerCardPlay), nameof(NControllerCardPlay.Start))]
internal static class NControllerCardPlay_Start_YaeSakuraDisplay_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NControllerCardPlay __instance) =>
        YaeSakuraDisplayHold.Pick(__instance);
}

/// <summary>The held card is played or put back.</summary>
[HarmonyPatch(typeof(NCardPlay), "Cleanup")]
internal static class NCardPlay_Cleanup_YaeSakuraDisplay_Patch
{
    [HarmonyPrefix]
    public static void Prefix(NCardPlay __instance) =>
        YaeSakuraDisplayHold.Drop(__instance);
}

internal static class YaeSakuraDisplayHold
{
    internal static void Pick(NCardPlay play)
    {
        try
        {
            var card = play.Holder?.CardNode?.Model;
            if (!YaePrototype.IsYae(card?.Owner?.Creature)) return;
            if (YaeSakuraDisplay.OwnedByLocalYae(card)) YaeSakuraDisplay.NoteHeld(card);
        }
        catch (Exception)
        {
            // Display only: never throw into the game's card play.
        }
    }

    internal static void Drop(NCardPlay play)
    {
        try
        {
            var card = play.Holder?.CardNode?.Model;
            if (!YaePrototype.IsYae(card?.Owner?.Creature)) return;
            if (YaeSakuraDisplay.OwnedByLocalYae(card)) YaeSakuraDisplay.NoteHeld(null);
        }
        catch (Exception)
        {
            // Display only.
        }
    }
}
