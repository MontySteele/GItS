using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using Godot;
using HarmonyLib;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Cards.Holders;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.HoverTips;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// VARKA'S OATH DIAL BY THE ENERGY ORB (2026-10-14).
///
/// THE RULING. [USER] chose option 2 of three: "An Oath dial by the Energy
/// orb. This is where Regent shows his Stars, a spot players already read for
/// a character's resource. It would be four small element pips with numbers,
/// the current one large and lit. A pip would pulse when a Swirl adds Oath,
/// and hovering a card that switches elements would preview the switch on the
/// dial." -- "Agreed on 2! It's definitely the cleanest option!"
///
/// WHERE IT GOES is Klee's Spark counter's answer, reused rather than
/// re-derived (<see cref="SparkCounter"/>): the base game's
/// <c>%StarCounter</c> sits by <c>%EnergyCounterContainer</c>, so the dial is
/// a SIBLING of that panel (never a child, `EB-815`), carries the panel's
/// anchor pair, and sits <see cref="SparkCounter.PanelMargin"/> above its top
/// edge, left edges aligned (<see cref="PlaceDial"/>). Its unit is the star
/// counter's own size (<see cref="SparkCounter.SideOf"/>).
///
/// A COLUMN, NOT A ROW, and that is the 2026-10-11 finding, not a taste: the
/// space to the right of the orb's top is where the base game centres the
/// Block badge on the creature's left edge, which is why Furina's counters
/// stack in a column. Every pip shares the star counter's X span, so none can
/// reach the Block badge. The order is fixed, Pyro, Hydro, Electro, Cryo from
/// the top (the order every surface lists them), so the eye learns where each
/// lives; the current one is drawn at the star counter's size and lit, the
/// others small and dimmed. Before any current element, all four are small
/// and dim. On a turn his cards read all four (the Elixir, All Four Winds)
/// all four are lit, the current still the large one.
///
/// THE LEDGER IS THE TRUTH (<see cref="VarkaOathLedger"/>); the dial is a view
/// of it, as the badge is. Its feed is <see cref="OathBadge.Sync"/>, the funnel
/// every Oath move already takes to redraw the badge, plus the turn start. No
/// <c>_Process</c>. A pip PULSES when its count rose since the last paint
/// (<see cref="Risen"/>) -- a Swirl, an application, any gain.
///
/// THE PREVIEW. While the player hovers or holds a card of his whose play
/// would change his current element (the "(Makes X current)" question,
/// <see cref="VarkaOath.WouldSwitchTo"/>, on the element the card is emitted
/// with, <see cref="IVarkaSwitchCard"/>), the pip that would become current
/// is ghost-lit with a gold ring (<see cref="PreviewTarget"/>).
///
/// THE HOVER is the badge's own tooltip: the live Oath badge's
/// <c>HoverTips</c>, so the two cannot say different things. Mouse only, like
/// Regent's <c>NStarCounter</c> (it connects <c>MouseEntered</c> and takes no
/// focus); the dial is display-only and never in the controller's focus graph.
///
/// THE OLD BADGE stays on his creature as a model -- the seat page reads its
/// title and sentence off the bridge (<c>tier0/tests/test_varka_seat_page.py</c>)
/// -- and is suppressed on his OWN status strip only
/// (<see cref="HidesBadge"/>), the way Furina's Fanfare badge is. A co-op
/// partner still sees it on his creature; only the local Varka's dial is drawn,
/// so two Varkas each see their own.
///
/// WHAT NOTHING HEADLESS CAN ANSWER: where it lands and how it reads. The pins
/// are the decisions (<c>VarkaOathDialTests</c>); the look is a frame on the
/// next deploy.
/// </summary>
public static class VarkaOathDial
{
    /// <summary>The node this file owns, and the handle its teardown uses.</summary>
    internal const string RootName = "KleeModVarkaOathDial";

    /// <summary>A small pip's size, as a fraction of the current one's.</summary>
    public const float SmallScale = 0.6f;

    /// <summary>The gap kept from the energy panel: the Spark counter's.</summary>
    public const float Margin = SparkCounter.PanelMargin;

    /// <summary>The gap between pips, in the panel's own units.</summary>
    internal const float PipGap = 6f;

    /// <summary>A dimmed pip's modulate: the art greyed, the number readable.
    /// </summary>
    internal static readonly Color DimModulate = new(0.55f, 0.55f, 0.55f, 0.85f);

    /// <summary>A lit pip's modulate.</summary>
    internal static readonly Color LitModulate = new(1f, 1f, 1f, 1f);

    /// <summary>The previewed pip's modulate: ghost-lit, brighter than dim.
    /// </summary>
    internal static readonly Color PreviewModulate = new(1f, 1f, 1f, 0.9f);

    /// <summary>The previewed pip's ring: the base game's gold.</summary>
    internal static Color PreviewRing => StsColors.gold;

    private const string HoverShownMeta = "kleemod_oath_dial_hover_shown";

    private const string SideMeta = "kleemod_oath_dial_side";

    /// <summary>The seat whose dial this screen draws.</summary>
    private static Player? _dialSeat;

    private static readonly
        TrackedDisplayBridge.Registry<Player, Control> Displays = new();

    /// <summary>The counts at the last paint, per seat, for the pulse.</summary>
    private static readonly Dictionary<Player, Dictionary<Element, int>> Seen = new();

    /// <summary>The card the local player is hovering, and the one held.</summary>
    private static CardModel? _hovered;
    private static CardModel? _held;

    private static readonly HashSet<string> WarnedGlyphs = new();

    // ------------------------------------------------------- pure parts --

    /// <summary>One pip as the dial draws it. PURE.</summary>
    public readonly record struct OathPip(
        Element Element, int Oath, bool IsCurrent, bool Lit, bool Preview);

    /// <summary>
    /// The four pips, in the ledger's order. The current element's is large
    /// and lit; on a read-all-four turn every pip is lit; before any current
    /// element none is. The preview marks the pip a card would make current.
    /// PURE.
    /// </summary>
    public static IReadOnlyList<OathPip> Pips(
        Element current, Func<Element, int> oath, bool readsAllFour,
        Element preview)
    {
        var now = CurrentPip(current);
        return VarkaOathLedger.Elements
            .Select(e => new OathPip(
                e, Math.Max(0, oath(e)), e == now,
                e == now || readsAllFour,
                e == preview && e != now))
            .ToList();
    }

    /// <summary>The pip drawn large: the current element, or None before
    /// the first (and for any element that keeps no Oath). PURE.</summary>
    public static Element CurrentPip(Element current) =>
        VarkaOath.IsOathElement(current) ? current : Element.None;

    /// <summary>
    /// The pip a card previews: the element it makes current, when its play
    /// would switch to it now (<paramref name="wouldSwitch"/>, the switch
    /// line's question) and it is not already current. PURE.
    /// </summary>
    public static Element PreviewTarget(
        Element current, Element switchesTo, bool wouldSwitch) =>
        wouldSwitch && VarkaOath.IsOathElement(switchesTo)
            && switchesTo != CurrentPip(current)
            ? switchesTo : Element.None;

    /// <summary>The element a card makes current: its emitted one, or a
    /// Knight's own. None for any other card. PURE.</summary>
    public static Element SwitchElementOf(CardModel? card) =>
        card is IVarkaSwitchCard switching
            ? switching.VarkaSwitchElement
            : VarkaOath.KnightElement(card);

    /// <summary>The pip this card previews on its owner's dial, now.</summary>
    public static Element PreviewFor(CardModel? card)
    {
        var element = SwitchElementOf(card);
        if (element == Element.None) return Element.None;
        Creature? owner;
        try
        {
            owner = card?.Owner?.Creature;
        }
        catch (Exception)
        {
            return Element.None;
        }
        return PreviewTarget(VarkaOath.Current(owner), element,
                             VarkaOath.WouldSwitchTo(card, element));
    }

    /// <summary>The elements whose Oath rose between two paints, in the
    /// ledger's order. A first paint (no <paramref name="before"/>) pulses
    /// nothing. PURE.</summary>
    public static IReadOnlyList<Element> Risen(
        IReadOnlyDictionary<Element, int>? before,
        IReadOnlyDictionary<Element, int> after)
    {
        if (before == null) return Array.Empty<Element>();
        return VarkaOathLedger.Elements
            .Where(e => after.GetValueOrDefault(e) > before.GetValueOrDefault(e))
            .ToList();
    }

    /// <summary>The dial's height for a given pip side: one large pip, three
    /// small, three gaps. Constant whichever pip is current, so the column
    /// never jumps. PURE.</summary>
    public static float Height(float side) =>
        side + 3f * side * SmallScale + 3f * PipGap;

    /// <summary>
    /// Each pip's visual box inside the dial, top to bottom in the ledger's
    /// order, laid from the BOTTOM up so the column sits on the orb's margin
    /// whichever pip is large. Small pips are centred on the column. PURE.
    /// </summary>
    public static IReadOnlyList<Rect2> PipRects(float side, Element current)
    {
        var now = CurrentPip(current);
        var sizes = VarkaOathLedger.Elements
            .Select(e => e == now ? side : side * SmallScale).ToList();
        var used = sizes.Sum() + PipGap * (sizes.Count - 1);
        var y = Height(side) - used;
        var rects = new List<Rect2>();
        foreach (var s in sizes)
        {
            rects.Add(new Rect2(new Vector2((side - s) / 2f, y),
                                new Vector2(s, s)));
            y += s + PipGap;
        }
        return rects;
    }

    /// <summary>
    /// WHERE THE DIAL GOES: <see cref="SparkCounter.Place"/>'s rule for a box
    /// that is taller than it is wide. Above the energy panel, left edges
    /// aligned, <see cref="SparkCounter.PanelMargin"/> clear; with no room
    /// above, to its right, bottom-aligned with it; held inside the viewport
    /// on each axis the viewport can hold. PURE.
    /// </summary>
    public static Rect2 PlaceDial(Rect2 energy, Vector2 size, Vector2 viewport)
    {
        var margin = SparkCounter.PanelMargin;
        var above = new Vector2(energy.Position.X,
                                energy.Position.Y - margin - size.Y);
        var at = above.Y >= 0f
            ? above
            : new Vector2(energy.End.X + margin, energy.End.Y - size.Y);
        return new Rect2(Hold(at, size, viewport), size);
    }

    private static Vector2 Hold(Vector2 at, Vector2 size, Vector2 viewport) =>
        new(viewport.X > size.X ? Mathf.Clamp(at.X, 0f, viewport.X - size.X) : at.X,
            viewport.Y > size.Y ? Mathf.Clamp(at.Y, 0f, viewport.Y - size.Y) : at.Y);

    /// <summary>
    /// How many Spark-counter slots the dial takes in the column above the
    /// orb, so a Varka holding Sparks draws them above it. PURE.
    /// </summary>
    public static int SlotsTall(float side) =>
        Math.Max(1, (int)Math.Ceiling(
            (Height(side) + SparkCounter.PanelMargin)
            / (side + SparkCounter.PanelMargin)));

    /// <summary>The glyph a pip wears: the Vision his Oath badge wears for
    /// that element (<c>KleePowerIcons</c>). PURE.</summary>
    public static string GlyphPathFor(Element element) => element switch
    {
        Element.Pyro => "varka/powers/pyro_wind.png",
        Element.Hydro => "varka/powers/hydro_wind.png",
        Element.Electro => "varka/powers/electro_wind.png",
        Element.Cryo => "varka/powers/cryo_wind.png",
        _ => "",
    };

    // ------------------------------------------------------------ scope --

    /// <summary>Does this creature get the dial? Varka, from turn one.</summary>
    public static bool AppliesTo(Creature? creature) =>
        creature != null && VarkaPrototype.IsVarka(creature);

    /// <summary>
    /// Is this his Oath badge on his OWN screen, where the dial draws it? A
    /// co-op partner still sees it on his creature. Never throws: a
    /// canonical power has no owner to ask.
    /// </summary>
    public static bool HidesBadge(PowerModel power)
    {
        if (power is not OathBadgePower) return false;
        Creature? owner;
        try
        {
            owner = power.IsMutable ? power.Owner : null;
        }
        catch (Exception)
        {
            return false;
        }
        return owner != null && AppliesTo(owner) && LocalContext.IsMe(owner);
    }

    // --------------------------------------------------------- lifecycle --

    /// <summary>Build the dial for the LOCAL seat, from the
    /// <c>NCombatUi.Activate</c> postfix <c>GaugeBridge</c> installs.</summary>
    public static void Setup(CombatState? state)
    {
        var me = TryGetMe(state);
        if (me == null || !AppliesTo(me.Creature)) return;
        if (NCombatRoom.Instance?.Ui is not { } ui) return;

        var star = ui.GetNodeOrNull<Control>("%StarCounter");
        var panel = ui.EnergyCounterContainer;
        var parent = panel?.GetParent() ?? (Node)ui;

        Displays.Discard(me);
        Seen.Remove(me);
        var side = SparkCounter.SideOf(star);
        var root = Build(side);
        var creature = me.Creature;
        root.MouseEntered += () => ShowHover(root, creature);
        root.MouseExited += () => ClearHover(root);
        root.TreeExiting += () => ClearHover(root);

        parent.AddChildSafely(root);
        Displays.Set(me, root);
        _dialSeat = me;

        Apply(root, panel, side, ui.GetViewportRect().Size);
        Paint(root, me, creature);
    }

    /// <summary>Re-read the ledger and redraw. Headless-safe: it returns
    /// before any node work when there is no combat room.</summary>
    public static void Refresh(Creature? creature)
    {
        if (!AppliesTo(creature) || NCombatRoom.Instance == null) return;
        var player = creature!.Player;
        if (player == null || !LocalContext.IsMe(player)) return;

        var root = Displays.Get(player);
        if (root == null)
        {
            Setup(creature.CombatState as CombatState);
            root = Displays.Get(player);
            if (root == null) return;
        }

        Paint(root, player, creature);
    }

    /// <summary>The local player hovered (or stopped hovering) a card in
    /// hand. Only his own Varka's cards move the preview.</summary>
    internal static void NoteHover(CardModel? card, bool hovered)
    {
        if (hovered)
        {
            if (!OwnedByLocalVarka(card)) return;
            _hovered = card;
        }
        else if (ReferenceEquals(_hovered, card))
        {
            _hovered = null;
        }
        RefreshPreview();
    }

    /// <summary>The local player picked a card up (or put it down).</summary>
    internal static void NoteHeld(CardModel? card)
    {
        if (card != null && !OwnedByLocalVarka(card)) return;
        if (card == null && _held != null && ReferenceEquals(_hovered, _held))
        {
            // Played or put back: its holder may never send the unhover.
            _hovered = null;
        }
        _held = card;
        RefreshPreview();
    }

    private static bool OwnedByLocalVarka(CardModel? card)
    {
        try
        {
            var owner = card?.Owner?.Creature;
            return AppliesTo(owner) && LocalContext.IsMe(owner!);
        }
        catch (Exception)
        {
            return false;
        }
    }

    /// <summary>Redraw this screen's dial, whose seat <see cref="Setup"/>
    /// recorded: a hover that ends names no card to find it by.</summary>
    private static void RefreshPreview() => Refresh(_dialSeat?.Creature);

    /// <summary>The preview for this seat's dial: the hovered or held card's,
    /// when that card is this seat's own.</summary>
    private static Element PreviewOn(Player player)
    {
        var card = _held ?? _hovered;
        try
        {
            return card != null && ReferenceEquals(card.Owner, player)
                ? PreviewFor(card) : Element.None;
        }
        catch (Exception)
        {
            // A canonical copy asserts on Owner: nothing to preview.
            return Element.None;
        }
    }

    /// <summary>The local seat, or null. <c>LocalContext.GetMe</c> throws for
    /// "not in this combat" (`EB-225`), so it is caught here.</summary>
    private static Player? TryGetMe(CombatState? state)
    {
        if (state == null) return null;
        try
        {
            return LocalContext.GetMe(state);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] oath dial: no local seat in this "
                   + $"combat ({e.GetType().Name}: {e.Message}); drawing "
                   + "nothing.");
            return null;
        }
    }

    // ----------------------------------------------------------- drawing --

    /// <summary>The node tree: a column box holding four pips, each the
    /// Spark counter's glyph-and-number node at the star counter's size,
    /// dressed with the counter face and scaled down when small.</summary>
    internal static Control Build(float side)
    {
        var root = new Control
        {
            Name = RootName,
            // The one way in is the mouse, as on Regent's star counter.
            MouseFilter = Control.MouseFilterEnum.Stop,
            FocusMode = Control.FocusModeEnum.None,
            Size = new Vector2(side, Height(side)),
        };
        root.SetMeta(SideMeta, side);

        foreach (var element in VarkaOathLedger.Elements)
        {
            var pip = SparkCounter.Build(side);
            pip.Name = element.ToString();
            pip.MouseFilter = Control.MouseFilterEnum.Ignore;
            pip.PivotOffset = new Vector2(side / 2f, side / 2f);
            FurinaCounterFace.Dress(pip, side, ElementRing(element));
            root.AddChildSafely(pip);
        }

        root.SetFocusBehaviorRecursive(
            Control.FocusBehaviorRecursiveEnum.Disabled);
        return root;
    }

    /// <summary>A pip's ring: the element's own colour, the one the stage
    /// cues use (<see cref="FurinaStageCueNodes.ElementColour"/>).</summary>
    internal static Color ElementRing(Element element) =>
        FurinaStageCueNodes.ElementColour(element.ToString());

    /// <summary>
    /// Put <see cref="PlaceDial"/>'s answer on the node in the panel's own
    /// anchor space, exactly as <see cref="SparkCounter.Apply"/> does, so a
    /// resize moves panel and dial by one vector.
    /// </summary>
    internal static void Apply(Control root, Control? panel, float side,
                               Vector2 viewport)
    {
        var size = new Vector2(side, Height(side));
        if (panel == null)
        {
            var guess = PlaceDial(
                new Rect2(SparkCounter.EnergyCounterOffset,
                          new Vector2(side, side)),
                size, viewport);
            root.AnchorLeft = 0f;
            root.AnchorTop = 0f;
            root.AnchorRight = 0f;
            root.AnchorBottom = 0f;
            root.OffsetLeft = guess.Position.X;
            root.OffsetTop = guess.Position.Y;
            root.OffsetRight = guess.End.X;
            root.OffsetBottom = guess.End.Y;
            return;
        }

        var rect = new Rect2(panel.Position, panel.Size);
        var delta = PlaceDial(rect, size, viewport).Position - rect.Position;
        root.AnchorLeft = panel.AnchorLeft;
        root.AnchorRight = panel.AnchorLeft;
        root.AnchorTop = panel.AnchorTop;
        root.AnchorBottom = panel.AnchorTop;
        root.OffsetLeft = panel.OffsetLeft + delta.X;
        root.OffsetTop = panel.OffsetTop + delta.Y;
        root.OffsetRight = root.OffsetLeft + size.X;
        root.OffsetBottom = root.OffsetTop + size.Y;
    }

    private static void Paint(Control root, Player player, Creature? creature)
    {
        if (creature == null || !GodotObject.IsInstanceValid(root)) return;

        var ledger = VarkaOathLedger.For(creature);
        var counts = VarkaOathLedger.Elements
            .ToDictionary(e => e, e => ledger.Oath(e));
        var pips = Pips(ledger.Current, e => counts[e], ledger.ReadsAllFour,
                        PreviewOn(player));
        var side = root.HasMeta(SideMeta)
            ? (float)root.GetMeta(SideMeta).AsDouble()
            : SparkCounter.SideOf(null);
        var rects = PipRects(side, ledger.Current);

        Seen.TryGetValue(player, out var before);
        var risen = Risen(before, counts);
        Seen[player] = counts;

        for (var i = 0; i < pips.Count; i++)
        {
            var pip = pips[i];
            if (root.GetNodeOrNull<Control>(pip.Element.ToString())
                is not { } node)
            {
                continue;
            }
            var scale = pip.IsCurrent ? 1f : SmallScale;
            var centre = new Vector2(side / 2f, side / 2f);
            // The pivot is the pip's centre, so its visual top-left is
            // Position + centre * (1 - scale).
            node.Position = rects[i].Position - centre * (1f - scale);
            node.Scale = new Vector2(scale, scale);
            node.Modulate = pip.Lit ? LitModulate
                : pip.Preview ? PreviewModulate : DimModulate;
            if (node.GetNodeOrNull<Label>("Count") is { } count)
            {
                count.Text = pip.Oath.ToString(CultureInfo.InvariantCulture);
            }
            FurinaCounterFace.SetFill(node, pip.Oath == 0
                ? FurinaCounterFace.EmptyFill : FurinaCounterFace.Fill);
            SetPreview(node, pip.Preview);
            if (node.GetNodeOrNull<TextureRect>("Icon") is { } icon)
            {
                SetGlyph(icon, pip.Element);
            }
            if (risen.Contains(pip.Element))
            {
                Pulse(node, scale);
            }
        }
    }

    /// <summary>Gold ring on the pip a held card would make current, the
    /// element's own otherwise.</summary>
    private static void SetPreview(Control pip, bool preview)
    {
        if (pip.GetNodeOrNull<Panel>("Ring") is not { } ring) return;
        if (ring.GetThemeStylebox("panel") is not StyleBoxFlat box) return;
        var element = Enum.TryParse<Element>(pip.Name.ToString(), out var e)
            ? e : Element.None;
        box.BorderColor = preview ? PreviewRing : ElementRing(element);
    }

    /// <summary>The pulse: a quick swell and back, on the pip alone.</summary>
    private static void Pulse(Control pip, float scale)
    {
        try
        {
            var tween = pip.CreateTween();
            tween.TweenProperty(pip, "scale",
                    new Vector2(scale * 1.3f, scale * 1.3f), 0.12)
                .SetTrans(Tween.TransitionType.Quad)
                .SetEase(Tween.EaseType.Out);
            tween.TweenProperty(pip, "scale",
                    new Vector2(scale, scale), 0.2)
                .SetTrans(Tween.TransitionType.Quad)
                .SetEase(Tween.EaseType.In);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] oath dial: pulse skipped: {e.Message}");
        }
    }

    /// <summary>Resolved fresh on every paint, never cached across a scene
    /// (`EB-222`), and never throws at its caller.</summary>
    private static void SetGlyph(TextureRect icon, Element element)
    {
        var glyph = GlyphPathFor(element);
        try
        {
            var path = KleePck.Path(glyph);
            var texture = path == null
                ? null
                : ResourceLoader.Load<Texture2D>(path);
            if (texture == null || !GodotObject.IsInstanceValid(texture))
            {
                if (WarnedGlyphs.Add(glyph))
                {
                    Log.Warn($"[{KleeMod.ModId}] oath dial: no live {glyph}; "
                           + "drawing the number with no glyph.");
                }
                icon.Visible = false;
                return;
            }
            icon.Texture = texture;
            icon.Visible = true;
        }
        catch (Exception e)
        {
            if (WarnedGlyphs.Add(glyph))
            {
                Log.Warn($"[{KleeMod.ModId}] oath dial: the glyph could not be "
                       + $"drawn ({e.GetType().Name}: {e.Message}); drawing the "
                       + "number alone.");
            }
        }
    }

    /// <summary>The badge's own tooltip: the live Oath badge's hover tips, or
    /// the plain Oath badge's before he holds any Oath.</summary>
    private static void ShowHover(Control root, Creature creature)
    {
        try
        {
            if (!GodotObject.IsInstanceValid(root)) return;
            ClearHover(root);
            var badge = creature.Powers.OfType<OathBadgePower>().FirstOrDefault();
            var tips = badge != null
                ? badge.HoverTips.ToList()
                : new List<IHoverTip>
                  {
                      ModelDb.Power<UnswornOathPower>().DumbHoverTip,
                  };
            NHoverTipSet.CreateAndShow(
                root, tips, HoverTip.GetHoverTipAlignment(root));
            root.SetMeta(HoverShownMeta, true);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] oath dial: hover skipped: {e}");
        }
    }

    private static void ClearHover(Control root)
    {
        if (!GodotObject.IsInstanceValid(root) || !root.HasMeta(HoverShownMeta))
        {
            return;
        }
        root.RemoveMeta(HoverShownMeta);
        NHoverTipSet.Remove(root);
    }

    /// <summary>Free the dial when the combat UI stands down, by node name,
    /// never by seat (`EB-225`), and forget the hover and the pulse marks.
    /// </summary>
    internal static void Hide(NCombatUi? ui)
    {
        _hovered = null;
        _held = null;
        _dialSeat = null;
        Seen.Clear();
        if (ui == null || !GodotObject.IsInstanceValid(ui)) return;
        if (ui.FindChild(RootName, recursive: true, owned: false)
            is { } node && GodotObject.IsInstanceValid(node))
        {
            node.QueueFree();
        }
    }
}

/// <summary>The dial dies with the combat, on the game's own hook.</summary>
// lint: no-seat: pure static teardown. It frees, by name, the one child node
// this file added to the combat UI and clears this file's own statics; it
// touches no run state, player or creature. The scope lives at the only door
// that BUILDS the node (`Setup`, through `VarkaOathDial.AppliesTo`).
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Deactivate))]
internal static class NCombatUi_Deactivate_VarkaOathDial_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCombatUi __instance) =>
        VarkaOathDial.Hide(__instance);
}

/// <summary>His Oath badge stays off his own status strip, where the dial
/// draws it; a co-op partner still sees it.</summary>
[HarmonyPatch(typeof(NPowerContainer), "Add")]
internal static class NPowerContainer_Add_VarkaOathDial_Patch
{
    [HarmonyPrefix]
    public static bool Prefix(PowerModel power) =>
        !VarkaOathDial.HidesBadge(power);
}

/// <summary>A card in hand hovered or focused (mouse or controller): the
/// dial previews the switch it would make.</summary>
[HarmonyPatch(typeof(NHandCardHolder), "DoCardHoverEffects")]
internal static class NHandCardHolder_Hover_VarkaOathDial_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NHandCardHolder __instance, bool isHovered)
    {
        try
        {
            var card = __instance.CardNode?.Model;
            if (card?.Owner?.Creature is not { } owner
                || !VarkaPrototype.IsVarka(owner)
                || !LocalContext.IsMe(owner))
            {
                if (!isHovered) VarkaOathDial.NoteHover(card, false);
                return;
            }
            VarkaOathDial.NoteHover(card, isHovered);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] oath dial: hover preview skipped: "
                   + e.Message);
        }
    }
}

/// <summary>A card picked up with the mouse: the dial keeps the preview
/// while it is held.</summary>
[HarmonyPatch(typeof(NMouseCardPlay), nameof(NMouseCardPlay.Start))]
internal static class NMouseCardPlay_Start_VarkaOathDial_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NMouseCardPlay __instance) =>
        VarkaOathDialHold.Pick(__instance);
}

/// <summary>A card picked up with the controller.</summary>
[HarmonyPatch(typeof(NControllerCardPlay), nameof(NControllerCardPlay.Start))]
internal static class NControllerCardPlay_Start_VarkaOathDial_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NControllerCardPlay __instance) =>
        VarkaOathDialHold.Pick(__instance);
}

/// <summary>The held card is played or put back: the game's own
/// <c>Cleanup</c> runs on both.</summary>
[HarmonyPatch(typeof(NCardPlay), "Cleanup")]
internal static class NCardPlay_Cleanup_VarkaOathDial_Patch
{
    [HarmonyPrefix]
    public static void Prefix(NCardPlay __instance) =>
        VarkaOathDialHold.Drop(__instance);
}

/// <summary>The held-card doors, scoped to the local Varka.</summary>
internal static class VarkaOathDialHold
{
    internal static void Pick(NCardPlay play)
    {
        try
        {
            var card = play.Holder?.CardNode?.Model;
            if (card?.Owner?.Creature is not { } owner
                || !VarkaPrototype.IsVarka(owner)
                || !LocalContext.IsMe(owner))
            {
                return;
            }
            VarkaOathDial.NoteHeld(card);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] oath dial: held preview skipped: "
                   + e.Message);
        }
    }

    internal static void Drop(NCardPlay play)
    {
        try
        {
            var card = play.Holder?.CardNode?.Model;
            if (card?.Owner?.Creature is not { } owner
                || !VarkaPrototype.IsVarka(owner)
                || !LocalContext.IsMe(owner))
            {
                return;
            }
            VarkaOathDial.NoteHeld(null);
        }
        catch (Exception)
        {
            // Display only: never throw into the game's card play.
        }
    }
}
