using System;
using System.Collections.Generic;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Nodes.HoverTips;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// The end-of-turn docket (EB-53/N1 — the attribution pass).
///
/// WHAT IT IS. One creature-tracked display per PLAYER SEAT, carrying a slot
/// per end-of-turn source standing on that creature, in the order
/// <see cref="TurnEndAttribution.Order"/> fires them. Each slot shows the
/// source's entity or badge, the number it is about to produce, and how many
/// turns it has left; each slot hovers to the copy that already explains it.
///
/// WHAT IT FIXES, both halves of the ask in one widget because the ask says so
/// ("whatever the pass does for summons should carry burst attribution too"):
///
///   * KOKOMI'S BAKE-KURAGE. The jellyfish had no body on the field and its
///     pulse number lived only inside a hover tip on cards that field it. Its
///     slot renders the summon art as a standing entity and prints
///     <see cref="KurageSummonPower.PulseDamage"/> before the turn ends —
///     which is what QUEUE `S4-G14` needs before Q1/Q4 can be asked at all.
///   * BURSTS, ALL SEATS. The docket is anchored to the creature that owns the
///     source, so a partner's Sparks 'n' Splash volley is announced over the
///     partner, counts down over the partner, and flashes over the partner as
///     it fires. Position IS the attribution — the same answer the Salon stage
///     gives for salon members, and the same reason the overhead Burst gauge
///     is per-creature rather than on the HUD.
///
/// IDIOMS FOLLOWED, not invented:
///   * <see cref="TrackedDisplayBridge"/> skeleton verbatim — keyed registry
///     with IsInstanceValid staleness, spawn-into-CombatVfxContainer with one
///     loud warning, RemoteTransform2D tracking, no _Process polling.
///   * <see cref="SalonVisualsBridge"/>'s slot row: identity read per SLOT
///     from state on every refresh, live number on a chip from the SAME
///     expression the resolution uses, buffed values in the game's
///     modified-value colour, per-slot hover sharing its copy source verbatim,
///     layout computed from the live count rather than authored.
///   * <see cref="GaugeBridge"/>'s spec array and its overhead-row convention.
///
/// PRESENTATION ONLY. Every read is an accessor the resolution already calls;
/// nothing here mutates state, latches a window, or draws from
/// <c>Rng.CombatTargets</c>. That is the <see cref="PreventExhaustWardPower"/>
/// ruling — previews run a different number of times on each co-op peer, so a
/// preview that writes anything desyncs the table. It is also why this layer
/// needs no sim twin: the sim is a one-seat combat model and this draws
/// nothing it does not already compute.
/// </summary>
public static class TurnEndPreviewBridge
{
    private const string ScenePathRelative = "shared/turn_end_docket.tscn";

    /// <summary>
    /// A THIRD overhead row, above Kokomi's Charge counter.
    ///
    /// The row choice is the C1 convention argument one row further up: the
    /// slot at -300 means "Burst" for every character and may not be shifted,
    /// the row at -340 is Kokomi's Charge, so the next clear band is -380. It
    /// is the SAME height for every seat on purpose — "what is about to happen
    /// at end of turn" has to be findable in one place across a co-op table,
    /// and a per-character height would make the partner's docket something
    /// you hunt for.
    ///
    /// Overhead rather than below the feet, and that is not taste: the band
    /// below a creature belongs to NCreatureStateDisplay (the HP bar spans the
    /// full bounds width and NHealthBar.UpdateLayoutForCreatureBounds pins the
    /// block badge to the left edge of the 240-wide box). The Salon stage's
    /// Encore label was drawn there once and simply covered.
    /// </summary>
    private static readonly Vector2 AnchorOffset = new(0f, -380f);

    /// <summary>Slot nodes the SCENE ships — one per entry in
    /// <see cref="TurnEndAttribution.Order"/>. The loop clamps and logs the
    /// excess rather than rendering a fifth source invisibly, the
    /// SalonVisualsBridge known-gap rule.</summary>
    private const int SceneSlots = 4;

    /// <summary>Slot pitch, and the half-span the row may occupy. 240 is the
    /// creature bounds width; the row is kept inside it so it cannot drift over
    /// a neighbouring seat at a two-player table.</summary>
    private const float SlotSpacing = 46f;

    /// <summary>Largest scale a slot's art is drawn at. The Bake-Kurage sprite
    /// is cut at 128px tall (tools/cut_kurage_summon.py) against a ~36px slot,
    /// so it is fitted at runtime — the amendment SalonVisualsBridge already
    /// made to the pre-scaled-art house rule, for the same reason: the pitch is
    /// computed, so there is no single size the art could be cut at.</summary>
    private const float SpriteScaleMax = 0.32f;

    /// <summary>The game's own modified-value colour (mockup #b7f79b), for a
    /// number raised above the rate the source's printed text quotes — today
    /// that is a Bake-Kurage pulse with Before Sun and Moon behind it.</summary>
    private static readonly Color BuffedNumber = new(0.718f, 0.969f, 0.608f);
    private static readonly Color PlainNumber = new(1f, 1f, 1f);
    private static readonly Color TurnsColour = new(0.72f, 0.85f, 0.95f, 1f);

    private const string KeywordTable = "card_keywords";

    private const string HoverTitleMeta = "kleemod_hover_title";
    private const string HoverBodyMeta = "kleemod_hover_body";
    private const string HoverWiredMeta = "kleemod_hover_wired";
    private const string HoverShownMeta = "kleemod_hover_shown";

    private static readonly TrackedDisplayBridge.Registry<Player> Displays = new();

    private static bool _warnedMissingScene;
    private static bool _warnedExcessSources;

    /// <summary>
    /// Which slot index a source currently occupies, per player. Needed only by
    /// <see cref="NoteFiring"/>, which is handed a source and has to find the
    /// slot the last refresh gave it — the row is COMPACTED (only standing
    /// sources get a slot), so slot index is not a function of the source
    /// alone.
    ///
    /// Bounded like SpotlightSystem's PendingDraws and for the same reason: the
    /// key is a Player, and a Player reaches the whole run graph. Cleared on
    /// every Setup and on Discard, and only ever holding one small list per
    /// live display.
    /// </summary>
    private static readonly Dictionary<Player, List<string>> SlotOrder = new();

    public static void Setup(NCombatRoom combatRoom, Player player)
    {
        var creature = player.Creature;
        if (creature == null) return;

        DiscardDisplay(player);

        var display = TrackedDisplayBridge.Spawn(
            combatRoom, ScenePathRelative, ref _warnedMissingScene,
            "end-of-turn docket disabled");
        if (display == null) return;

        TrackedDisplayBridge.Track(combatRoom, creature, display, AnchorOffset);
        Displays.Set(player, display);
        RefreshDisplay(display, player, creature);
    }

    /// <summary>
    /// Re-read the standing sources and redraw. Call sites are the funnels on
    /// <see cref="TurnEndSequencer"/> (card played, turn start, turn end) plus
    /// <c>KokomiResources.GainCharge</c>, which is the one mutation that moves
    /// a docket number without a card play necessarily being in flight.
    /// </summary>
    public static void Refresh(Creature? creature)
    {
        var player = creature?.Player;
        if (creature == null || player == null) return;

        var display = Displays.Get(player);
        if (display == null)
        {
            // Stale or never built (mid-combat reload): rebuild in place, the
            // reference-bridge idiom both sibling bridges use.
            if (NCombatRoom.Instance is not { } room) return;
            Setup(room, player);
            return;
        }

        RefreshDisplay(display, player, creature);
    }

    public static void DiscardDisplay(Player player)
    {
        SlotOrder.Remove(player);
        Displays.Discard(player);
    }

    /// <summary>
    /// Flash the slot a source is firing from, called by
    /// <see cref="TurnEndSequencer"/> immediately before it resolves.
    ///
    /// This is the attribution AT THE MOMENT OF THE HIT, which is the half a
    /// standing preview cannot do: four numbers arrive in one burst and the
    /// docket says which slot each came out of. It is deliberately a flash on
    /// an existing slot rather than a new floating callout — the slot is
    /// already the thing the player learned to read, and a second surface would
    /// have to be re-learned.
    ///
    /// Pure and failure-tolerant by construction: no display, no room, no
    /// matching slot, or a freed node all return quietly. It runs inside the
    /// turn-end resolution, so it may never be able to throw.
    /// </summary>
    public static void NoteFiring(Creature? creature, TurnEndSource source)
    {
        var player = creature?.Player;
        if (player == null) return;
        if (Displays.Get(player) is not { } display) return;
        if (!SlotOrder.TryGetValue(player, out var keys)) return;

        var index = keys.IndexOf(source.Key);
        if (index < 0 || index >= SceneSlots) return;
        if (display.GetNodeOrNull<AnimationPlayer>("%AnimationPlayer")
            is not { } anim)
        {
            return;
        }
        anim.Stop();
        anim.Play($"fire{index + 1}");
    }

    private static void RefreshDisplay(
        Node2D display, Player player, Creature creature)
    {
        var standing = TurnEndAttribution.Standing(creature);

        // The whole docket disappears when the creature's end of turn does
        // nothing. An empty plate reading "END OF TURN" over every creature in
        // every fight is exactly the noise a legibility layer must not add --
        // the KokomiRiderTips rule that a tip which advertises a window it is
        // not in trains players to stop reading it.
        display.Visible = standing.Count > 0;

        var shown = Math.Min(standing.Count, SceneSlots);
        if (standing.Count > SceneSlots && !_warnedExcessSources)
        {
            _warnedExcessSources = true;
            MegaCrit.Sts2.Core.Logging.Log.Warn(
                $"[{KleeMod.ModId}] end-of-turn docket has {SceneSlots} slots "
                + $"but {standing.Count} sources are standing; the excess is "
                + "not rendered (add slots to shared/turn_end_docket.tscn).");
        }

        var keys = new List<string>(shown);
        for (var i = 0; i < shown; i++) keys.Add(standing[i].Key);
        SlotOrder[player] = keys;

        LayOutSlots(display, shown);

        for (var i = 0; i < SceneSlots; i++)
        {
            var source = i < shown ? standing[i] : null;
            RefreshSlot(display, creature, i, source);
        }
    }

    /// <summary>
    /// Centre the row on the live count, SalonVisualsBridge D1 §5: a docket of
    /// one must not sit where the leftmost of four sits, or the row would
    /// appear to slide sideways as sources come and go.
    /// </summary>
    private static void LayOutSlots(Node2D display, int slots)
    {
        var centre = (slots - 1) / 2f;
        for (var i = 0; i < SceneSlots; i++)
        {
            if (display.GetNodeOrNull<Node2D>($"%Slot{i + 1}") is not { } slot)
            {
                continue;
            }
            slot.Visible = i < slots;
            if (i >= slots) continue;
            slot.Position = new Vector2((i - centre) * SlotSpacing, 0f);
        }
    }

    private static void RefreshSlot(
        Node2D display, Creature creature, int index, TurnEndSource? source)
    {
        var i = index + 1;
        var sprite = display.GetNodeOrNull<Sprite2D>($"%Icon{i}");
        var chip = display.GetNodeOrNull<ColorRect>($"%Chip{i}");
        var edge = display.GetNodeOrNull<ColorRect>($"%ChipEdge{i}");
        var label = display.GetNodeOrNull<Label>($"%ChipLabel{i}");
        var turns = display.GetNodeOrNull<Label>($"%Turns{i}");

        var show = source != null;
        if (chip != null) chip.Visible = show;
        if (edge != null) edge.Visible = show;
        if (label != null) label.Visible = show;
        if (turns != null) turns.Visible = show;
        if (sprite != null) sprite.Visible = false;

        RefreshSlotHover(display, creature, index, source);
        if (source == null) return;

        // The ENTITY if the source has one, else the power's own badge. The
        // sprite is hidden rather than substituted when neither resolves --
        // KleePck.Path returns null while a file is absent, and a slot with a
        // number and no picture is a working slot. (EB-65 is what a
        // substitution costs: a null path that falls through to a base getter
        // renders the red NOPE placeholder.)
        if (sprite != null && TextureFor(creature, source) is { } art)
        {
            sprite.Texture = art;
            sprite.Visible = true;
            var width = art.GetWidth();
            var height = art.GetHeight();
            var longest = Math.Max(width, height);
            sprite.Scale = Vector2.One * (longest > 0
                ? Mathf.Min(SpriteScaleMax, SlotSpacing * 0.8f / longest)
                : SpriteScaleMax);
        }

        if (label != null)
        {
            label.Text = source.Preview(creature);
            label.AddThemeColorOverride(
                "font_color",
                source.Buffed(creature) ? BuffedNumber : PlainNumber);
        }

        if (turns != null)
        {
            var left = source.TurnsLeft?.Invoke(creature) ?? 0;
            // A one-turn source prints nothing: "1" over a thing that is about
            // to fire and leave is a fact the player cannot act on, and every
            // Bake-Kurage at KurageDuration 1 would carry it permanently.
            turns.Text = left > 1 ? $"{left}" : string.Empty;
            turns.AddThemeColorOverride("font_color", TurnsColour);
        }
    }

    private static Texture2D? TextureFor(Creature creature, TurnEndSource source)
    {
        var path = source.SpritePath is { } relative
            ? KleePck.Path(relative)
            : null;
        if (path == null && source.Find(creature) is { } power)
        {
            path = KleePowerIcons.PathFor(power);
        }
        return path == null ? null : ResourceLoader.Load<Texture2D>(path);
    }

    /// <summary>
    /// Per-slot hover, sharing its copy source with the cards (the D1 §4 rule:
    /// the stage asks the same question a card does and must not fork the
    /// prose). The Bake-Kurage slot's body IS
    /// <c>KokomiRiderTips.PulseBody</c>, the paragraph the fielding cards
    /// already print.
    ///
    /// Content is stashed as node metadata and read at hover time rather than
    /// captured in the closure, so the signal is connected ONCE per node and
    /// the copy is never a snapshot of an older board.
    /// </summary>
    private static void RefreshSlotHover(
        Node2D display, Creature creature, int index, TurnEndSource? source)
    {
        if (display.GetNodeOrNull<Control>($"%Hover{index + 1}")
            is not { } target)
        {
            return;
        }

        if (source == null)
        {
            target.MouseFilter = Control.MouseFilterEnum.Ignore;
            ClearHover(target);
            return;
        }

        target.MouseFilter = Control.MouseFilterEnum.Stop;
        target.SetMeta(HoverTitleMeta, source.TitleKey + ".title");
        target.SetMeta(HoverBodyMeta, source.Body(creature));

        if (target.HasMeta(HoverWiredMeta)) return;
        target.SetMeta(HoverWiredMeta, true);
        target.MouseEntered += () => ShowHover(target);
        target.MouseExited += () => ClearHover(target);
    }

    private static void ShowHover(Control target)
    {
        if (!target.HasMeta(HoverTitleMeta)) return;
        // Remove first: NHoverTipSet keys its live set by owner and ADDS, so a
        // second show without a teardown throws on the duplicate key.
        ClearHover(target);
        NHoverTipSet.CreateAndShow(target, new List<IHoverTip>
        {
            new HoverTip(
                new LocString(KeywordTable, (string)target.GetMeta(HoverTitleMeta)),
                (string)target.GetMeta(HoverBodyMeta)),
        });
        target.SetMeta(HoverShownMeta, true);
    }

    private static void ClearHover(Control target)
    {
        if (!target.HasMeta(HoverShownMeta)) return;
        target.RemoveMeta(HoverShownMeta);
        NHoverTipSet.Remove(target);
    }
}
