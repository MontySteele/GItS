using System;
using System.Collections.Generic;
using Godot;
using KleeMod.Cards;
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
/// The Salon stage (animation sprint 2, Track D — the D4 redesign).
///
/// WHAT FAILED, and why this is a re-layout rather than a restyle: sprint 1
/// put three card-art portraits in framed squares beside Furina. The portraits
/// are 500x380 gameplay screenshots, and at combat scale the three read as
/// three identical blue smudges — member identity did not survive. The
/// [USER] verdict (2026-07-24) failed the styling and kept the concept. So the
/// members are now freestanding SILHOUETTE mini-sprites standing on a shallow
/// stage arc: no frame, no square crop, identity carried by outline.
/// Ghost-outline-for-empty is the one sprint-1 idea that did read, restyled
/// here to the stage language.
///
/// SLOT-INDEX-KEYED, per Funnel Contract §1. Deploy is by card and duplicates
/// are legal — three of the same member is a valid stage — so nothing here may
/// assume a fixed member-to-slot mapping or distinct members. Slot i renders
/// whatever <see cref="SalonMemberPower.CompanyOf"/> reports at index i, and a
/// company of three Ushers renders as three Ushers. This retires sprint-1
/// D1's fixed member-to-slot portrait assignment, which silently assumed both.
///
/// The Encore gauge lives here now (D3). It was evicted from the overhead slot
/// by the C4 verdict — overhead means Burst for every character — and re-homes
/// as the ribbon beneath the arc, so the members visibly stand ON their fuel
/// and draining to zero visibly dims the stage they stand on. That causality
/// is the thing the old layout could not show.
///
/// Bridge skeleton is unchanged from sprint 1 (Displays dict + IsInstanceValid
/// staleness + lazy re-Setup + CombatVfxContainer + RemoteTransform2D tracking
/// + the NCombatUi.Activate postfix), which is what survived the playtest and
/// what the G1 extraction covers.
/// </summary>
public static class SalonVisualsBridge
{
    private const string ScenePathRelative = "furina/ui/salon_stage.tscn";

    /// <summary>
    /// Anchor relative to Furina's creature node origin. The stage sits low
    /// and to her left; it is wider than the old flank line (three sprites
    /// plus a ribbon), so the span is deliberately kept inside the creature's
    /// own 240-wide bounds box to stay clear of enemy intent positions and
    /// targeting arrows.
    ///
    /// Y was -30 until the 2026-07-25 playtest read the Encore ribbon as
    /// having no number at all. The ribbon's value label hung BELOW the ribbon,
    /// which put it at creature-relative y -4..+14 — i.e. under the feet, in
    /// the band NCreatureStateDisplay owns. That band is not ours: the HP bar
    /// spans the full bounds width, and NHealthBar.UpdateLayoutForCreatureBounds
    /// pins the block badge to `bounds.GlobalPosition.X - halfWidth`, the LEFT
    /// edge of the 240-wide box — which is exactly where this stage sits. The
    /// number was drawn and then covered. The label moved up onto the ribbon
    /// (see salon_stage.tscn) and the whole stage lifted clear of the band.
    /// Both are layout, so both are [USER] D5's to judge.
    /// </summary>
    private static readonly Vector2 AnchorOffset = new(-104f, -52f);

    /// <summary>Sprite art per member identity, pck-relative.</summary>
    private static readonly Dictionary<SalonMember, string> MemberSprites = new()
    {
        [SalonMember.Usher] = "furina/salon/member_usher.png",
        [SalonMember.Chevalmarin] = "furina/salon/member_chevalmarin.png",
        [SalonMember.Crabaletta] = "furina/salon/member_crabaletta.png",
    };

    /// <summary>
    /// D1 §1: accent hue per member, carried by the underglow pool and the
    /// chip edge -- the SPRITES stay untouched. The sprint-1 failure was
    /// that three blue silhouettes at combat scale read as three identical
    /// smudges; colour is the channel that survives peripheral vision, and
    /// it costs nothing at the sprite level to change.
    ///
    /// Values are the mockup's, converted from #f0708c / #e8bb52 / #5fe0d2.
    /// Duplicates render as duplicate hues, per the Funnel Contract §1
    /// slot-index rule -- three Ushers are three gold pools.
    /// </summary>
    private static readonly Dictionary<SalonMember, Color> MemberAccent = new()
    {
        [SalonMember.Crabaletta] = new Color(0.941f, 0.439f, 0.549f),
        [SalonMember.Usher] = new Color(0.910f, 0.733f, 0.322f),
        [SalonMember.Chevalmarin] = new Color(0.373f, 0.878f, 0.824f),
    };

    /// <summary>
    /// D1 §2: the role glyph. WHITE masters, tinted per member through
    /// Modulate, so one file per ROLE serves every hue and the dry state
    /// greys the glyph by the same path that greys the sprite.
    /// Produced by tools/gen_salon_glyphs.py (art_lint L11 GENERATOR_OWNED).
    /// </summary>
    private static readonly Dictionary<SalonMember, string> RoleGlyphs = new()
    {
        [SalonMember.Crabaletta] = "furina/salon/glyph_damage.png",
        [SalonMember.Usher] = "furina/salon/glyph_block.png",
        [SalonMember.Chevalmarin] = "furina/salon/glyph_support.png",
    };

    /// <summary>The game's own modified-value colour, for a tick the player
    /// has BUFFED above its printed number (Grand Salon, or Fanfare Focus).
    /// The mockup's #b7f79b.</summary>
    private static readonly Color BuffedNumber = new(0.718f, 0.969f, 0.608f);
    private static readonly Color PlainNumber = new(1f, 1f, 1f);
    private static readonly Color DryNumber = new(0.36f, 0.44f, 0.57f);
    private static readonly Color DryEdge = new(0.12f, 0.18f, 0.28f, 0.85f);

    /// <summary>Runway segments the ribbon can draw before it overflows
    /// (D7). Five is the scene's node count, and the "5+" cue exists
    /// because Encore is uncapped and the sixth turn of runway has nowhere
    /// to go.</summary>
    private const int RunwaySegments = 5;

    /// <summary>
    /// Horizontal half-span available to the slot row. The creature bounds
    /// box is 240 wide and the stage arc spans +-96; a slot is 34 wide, so
    /// its CENTRE may not exceed 96 - 17.
    /// </summary>
    private const float SlotHalfSpan = 79f;

    /// <summary>The shipped three-slot spacing. Kept as the cap on gap
    /// width so a stage of three looks exactly as it did before A12 made
    /// the cap growable -- the tightening is something a cap RAISE causes,
    /// not something every Furina sees.</summary>
    private const float SlotSpacingMax = 62f;

    /// <summary>Slot nodes the SCENE ships. The live cap can exceed this
    /// only if a future card raises it past Casting Call upgraded; the loop
    /// clamps and the excess is logged rather than silently invisible.
    /// </summary>
    private const int SceneSlots = 5;

    /// <summary>Largest scale the member art is ever drawn at: exactly half
    /// the 144px master, which is exactly the 72px beam.</summary>
    private const float SpriteScaleMax = 0.5f;

    private const string KeywordTable = "card_keywords";

    private const string HoverTitleMeta = "kleemod_hover_title";
    private const string HoverBodyMeta = "kleemod_hover_body";
    private const string HoverRulesMeta = "kleemod_hover_rules";
    private const string HoverWiredMeta = "kleemod_hover_wired";
    /// <summary>Whether THIS control currently owns a live tip set. Kept on
    /// the node rather than in a static set so it dies with the node --
    /// a static registry of Controls outlives the combat that made them.
    /// NHoverTipSet.CreateAndShow keys its own registry by owner and ADDS,
    /// so showing twice without a Remove in between throws.</summary>
    private const string HoverShownMeta = "kleemod_hover_shown";
    private const string SegmentWidthMeta = "kleemod_seg_width";

    private static readonly Color ActiveTint = new(1f, 1f, 1f, 1f);
    private static readonly Color DryTint = new(0.55f, 0.6f, 0.68f, 0.92f);
    private static readonly Color PoolActive = new(0.62f, 0.85f, 1f, 0.3f);
    private static readonly Color PoolDry = new(0.5f, 0.55f, 0.62f, 0.14f);
    private static readonly Color BeamActive = new(0.7f, 0.88f, 1f, 0.12f);
    private static readonly Color BeamDry = new(0.7f, 0.88f, 1f, 0.03f);

    private const string PreviousCountMeta = "kleemod_salon_count";
    private const string PreviousEncoreMeta = "kleemod_salon_encore";

    private static readonly TrackedDisplayBridge.Registry<Player> Displays = new();

    private static bool _warnedMissingScene;

    public static void Setup(NCombatRoom combatRoom, Player player)
    {
        var creature = player.Creature;
        // Non-Furina players never spawn the stage (mirrors the reference
        // bridge's is-not-Hexaghost check).
        if (creature == null || player.Character is not IFurinaCharacter)
        {
            return;
        }

        DiscardDisplay(player);

        var display = TrackedDisplayBridge.Spawn(
            combatRoom, ScenePathRelative, ref _warnedMissingScene,
            "Salon stage disabled");
        if (display == null)
        {
            return;
        }

        TrackedDisplayBridge.Track(combatRoom, creature, display, AnchorOffset);
        Displays.Set(player, display);
        RefreshDisplay(display, creature, animate: false);
    }

    /// <summary>
    /// Re-read company, dry state and Encore, then redraw. Call sites are the
    /// Funnel Contract's own funnels: SalonMemberPower.Deploy (the single
    /// composition funnel) and the Encore gain/spend/absorb trio, plus
    /// FurinaResources.SyncMeters for the every-sync dry check.
    /// </summary>
    public static void Refresh(Creature? creature)
    {
        var player = creature?.Player;
        if (creature == null || player == null
            || player.Character is not IFurinaCharacter)
        {
            return;
        }

        var display = GetDisplay(player);
        if (display == null)
        {
            if (NCombatRoom.Instance is not { } room)
            {
                return;
            }
            Setup(room, player);
            display = GetDisplay(player);
            if (display == null)
            {
                return;
            }
        }

        RefreshDisplay(display, creature, animate: true);
    }

    public static void DiscardDisplay(Player player) => Displays.Discard(player);

    private static Node2D? GetDisplay(Player player) => Displays.Get(player);

    private static Texture2D? GlyphFor(SalonMember member) =>
        RoleGlyphs.TryGetValue(member, out var relative)
        && KleePck.Path(relative) is { } path
            ? ResourceLoader.Load<Texture2D>(path)
            : null;

    private static Texture2D? SpriteFor(SalonMember member) =>
        MemberSprites.TryGetValue(member, out var relative)
        && KleePck.Path(relative) is { } path
            ? ResourceLoader.Load<Texture2D>(path)
            : null;

    private static void RefreshDisplay(
        Node2D display, Creature creature, bool animate)
    {
        var company = SalonMemberPower.CompanyOf(creature);
        int encore = FurinaResources.Encore(creature);
        bool dry = encore < SalonConstants.TickEncoreCost;

        int previousCount = display.HasMeta(PreviousCountMeta)
            ? (int)display.GetMeta(PreviousCountMeta)
            : 0;
        display.SetMeta(PreviousCountMeta, company.Count);

        var anim = display.GetNodeOrNull<AnimationPlayer>("%AnimationPlayer");
        var popped = false;

        // A12: the cap is a per-player stat now, so the loop asks the player
        // rather than the constant. D1 added %Slot4/%Slot5, so a raised cap
        // now RENDERS -- the sprint-2 gap where a fourth member ticked, bowed
        // and counted for every rider while being invisible is closed.
        //
        // Five is the scene's ceiling. A cap above it would go invisible
        // again, so the loop is clamped and the excess is a KNOWN GAP rather
        // than a silent one: today nothing can raise the cap past 3 + Box
        // Seats upgraded (+2) = 5, which is exactly what the scene ships.
        var slots = Math.Min(SalonMemberPower.SlotsFor(creature), SceneSlots);
        var spacing = SlotSpacing(slots);
        LayOutSlots(display, slots);
        for (var i = 0; i < slots; i++)
        {
            bool occupied = i < company.Count;
            var sprite = display.GetNodeOrNull<Sprite2D>($"%Sprite{i + 1}");
            if (sprite != null)
            {
                // Identity is read per SLOT from state, every refresh —
                // duplicates render as duplicates, and an out-of-order deploy
                // cannot desync the stage from the company.
                sprite.Texture = occupied ? SpriteFor(company[i]) : null;
                sprite.Visible = occupied && sprite.Texture != null;
                sprite.Modulate = dry ? DryTint : ActiveTint;
                if (sprite.Texture is { } art)
                {
                    sprite.Scale = Vector2.One * SpriteScale(art, spacing);
                }
            }

            // Empty slot = ghost outline on the stage floor (the surviving
            // sprint-1 idea, restyled to the stage language).
            if (display.GetNodeOrNull<ColorRect>($"%Ghost{i + 1}") is { } ghost)
            {
                ghost.Visible = !occupied;
                FitDecoration(ghost, spacing);
            }

            // D1 §1: the pool carries the member's accent hue at the pool's
            // own alpha, so identity survives at combat scale without
            // touching the sprite. Dry keeps the existing grey -- "these
            // numbers are not happening" outranks "this is a Crabaletta".
            if (display.GetNodeOrNull<ColorRect>($"%Pool{i + 1}") is { } pool)
            {
                pool.Visible = occupied;
                pool.Color = !occupied || dry
                    ? PoolDry
                    : Accent(company[i], PoolActive.A);
                FitDecoration(pool, spacing);
            }

            if (display.GetNodeOrNull<ColorRect>($"%Beam{i + 1}") is { } beam)
            {
                beam.Visible = occupied;
                beam.Color = !occupied || dry
                    ? BeamDry
                    : Accent(company[i], BeamActive.A);
                FitDecoration(beam, spacing);
            }

            RefreshChip(display, creature, i, occupied ? company[i] : null, dry);
            RefreshSlotHover(display, creature, i, occupied ? company[i] : null);

            if (animate && occupied && i >= previousCount && anim != null)
            {
                // One AnimationPlayer: a multi-member deploy queues its pops
                // into a short cascade instead of cutting the first one off
                // (the sprint-1 behaviour, kept).
                if (popped)
                {
                    anim.Queue($"slot{i + 1}_pop");
                }
                else
                {
                    anim.Play($"slot{i + 1}_pop");
                    popped = true;
                }
            }
        }

        RefreshRibbon(display, encore, company.Count, anim, animate);
    }

    private static Color Accent(SalonMember member, float alpha)
    {
        var hue = MemberAccent.TryGetValue(member, out var c)
            ? c
            : PoolActive;
        return new Color(hue.R, hue.G, hue.B, alpha);
    }

    /// <summary>
    /// D1 §5: the slot row is laid out from the LIVE cap, not from the
    /// scene's authored positions. A cap raise has to appear as a new ghost
    /// slot on a row that still fits inside Furina's 240-wide bounds, and
    /// three fixed positions cannot do both -- so the gap tightens as the
    /// count grows, capped at the shipped three-slot spacing so a normal
    /// Furina's stage is pixel-identical to the one that shipped.
    ///
    /// The arc height is a shallow curve: the middle of the row stands
    /// highest. Computed rather than authored for the same reason as X --
    /// with a variable slot count there is no fixed middle.
    /// </summary>
    private static float SlotSpacing(int slots) =>
        slots > 1
            ? Mathf.Min(SlotSpacingMax, 2f * SlotHalfSpan / (slots - 1))
            : SlotSpacingMax;

    /// <summary>
    /// How far down the member art is scaled to fit its slot.
    ///
    /// PLAYTEST 3 DEFECT (2026-07-28): "the salon pictures stacked over each
    /// other and became unreadable" at cap 4-5. The cause is older than the
    /// cap: the sprites are cut at 144px tall and ~121-129 wide and were
    /// drawn at 1:1 on a 62px pitch, so they have ALWAYS overlapped by about
    /// half. That is missed-requirements sec.4.3, which shipped as a
    /// recorded gap. A12 turned it from ugly into illegible, because the
    /// pitch is now as tight as 39.5px.
    ///
    /// The house rule was pre-scaled art with NO runtime minification. That
    /// rule cannot survive A12 and is explicitly amended here: the slot
    /// pitch is a function of a per-player stat, so there is no single size
    /// the art could be cut at. It is cut once at 144 and fitted at runtime.
    ///
    /// The cap is 0.5 -- exactly half of the 144px master and exactly the
    /// 72px beam -- so the common three-member stage lands on a clean 2x
    /// downscale with no resampling artefacts, and only a RAISED cap goes
    /// below it. Width is measured per texture because the three members
    /// differ by a few pixels, and the one that overflows is the one that
    /// stacks.
    /// </summary>
    private static float SpriteScale(Texture2D art, float spacing)
    {
        var width = art.GetWidth();
        return width > 0
            ? Mathf.Min(SpriteScaleMax, spacing / width)
            : SpriteScaleMax;
    }

    /// <summary>
    /// Squash a slot decoration horizontally when the pitch is tighter than
    /// the decoration is wide. The pool is the accent-hue carrier (D1 §1),
    /// so overlapping pools blur exactly the identity signal the hue exists
    /// to provide -- and the pool is authored at 52px against a cap-5 pitch
    /// of 39.5. Horizontal only: these are glows and outlines, and squashing
    /// one reads as a narrower stage rather than as a smaller member.
    /// </summary>
    private static void FitDecoration(Control? rect, float spacing)
    {
        if (rect == null || rect.Size.X <= 0f) return;
        rect.PivotOffset = rect.Size / 2f;
        rect.Scale = new Vector2(Mathf.Min(1f, spacing / rect.Size.X), 1f);
    }

    private static void LayOutSlots(Node2D display, int slots)
    {
        var spacing = slots > 1 ? SlotSpacing(slots) : 0f;
        var centre = (slots - 1) / 2f;
        for (var i = 0; i < SceneSlots; i++)
        {
            if (display.GetNodeOrNull<Node2D>($"%Slot{i + 1}") is not { } slot)
            {
                continue;
            }
            slot.Visible = i < slots;
            if (i >= slots)
            {
                continue;
            }
            var offset = i - centre;
            var lift = centre > 0f ? Mathf.Abs(offset) / centre : 0f;
            slot.Position = new Vector2(offset * spacing, -20f + 6f * lift);
        }
    }

    /// <summary>
    /// D1 §2: the role chip. Glyph answers "what does this one do", the
    /// number answers "how much, right now" -- and the number comes from
    /// SalonMemberPower.TickValue, the same expression the upkeep resolves
    /// through, so the chip cannot disagree with the tick. A buffed value
    /// renders in the game's modified-number colour; that is the whole
    /// point of showing a live number rather than the printed constant.
    /// </summary>
    private static void RefreshChip(
        Node2D display, Creature creature, int index,
        SalonMember? member, bool dry)
    {
        var i = index + 1;
        var edge = display.GetNodeOrNull<ColorRect>($"%ChipEdge{i}");
        var back = display.GetNodeOrNull<ColorRect>($"%Chip{i}");
        var glyph = display.GetNodeOrNull<Sprite2D>($"%ChipGlyph{i}");
        var label = display.GetNodeOrNull<Label>($"%ChipLabel{i}");

        var show = member.HasValue;
        if (edge != null) edge.Visible = show;
        if (back != null) back.Visible = show;
        if (glyph != null) glyph.Visible = show;
        if (label != null) label.Visible = show;
        if (!show || member is not { } who) return;

        if (edge != null)
        {
            edge.Color = dry ? DryEdge : Accent(who, 0.55f);
        }
        if (glyph != null)
        {
            glyph.Texture = GlyphFor(who);
            glyph.Visible = glyph.Texture != null;
            glyph.Modulate = dry ? DryNumber : Accent(who, 1f);
        }
        if (label != null)
        {
            // paid: !dry is the honest read for a chip drawn between turns.
            // Mid-upkeep the earlier members have already spent, so a later
            // member may go dry after this was drawn -- the tick that
            // follows is the authority, and the dry tint is what tells the
            // player the stage is short.
            var value = SalonMemberPower.TickValue(creature, who, !dry);
            label.Text = value.ToString();
            var buffed = value > SalonMemberPower.BaseTick(who);
            label.AddThemeColorOverride(
                "font_color",
                dry ? DryNumber : buffed ? BuffedNumber : PlainNumber);
        }
    }

    /// <summary>
    /// D1 §4: per-slot hover tips, sharing B5's copy source VERBATIM --
    /// SalonMemberTips is the one place the member's tick line, bow line and
    /// the cap rules are written, and the stage asks it the same questions a
    /// deploy card does.
    ///
    /// The tip content is stashed on the Control as metadata and read at
    /// hover time rather than captured in the callback, so the signal is
    /// connected ONCE per node and the copy is never a snapshot of an older
    /// stage. Connecting per refresh would stack a new handler on every
    /// deploy and every Encore tick.
    ///
    /// UNVERIFIED UNTIL PLAYTEST, and the sprint brief says so: no Godot run
    /// is available here, so whether this hover target fights targeting
    /// arrows or enemy intents is an in-game question. The Control sits
    /// inside the creature's own bounds, which is where the arrows live.
    /// </summary>
    private static void RefreshSlotHover(
        Node2D display, Creature creature, int index, SalonMember? member)
    {
        if (display.GetNodeOrNull<Control>($"%Hover{index + 1}")
            is not { } target)
        {
            return;
        }

        if (member is not { } who)
        {
            target.MouseFilter = Control.MouseFilterEnum.Ignore;
            ClearHover(target);
            return;
        }

        target.MouseFilter = Control.MouseFilterEnum.Stop;
        target.SetMeta(HoverTitleMeta, SalonMemberTips.KeyFor(who) + ".title");
        // `EB-384`: the owner goes with the member, so the stage hover and the
        // deploy card's tip read the same branch of the same copy.
        target.SetMeta(HoverBodyMeta, SalonMemberTips.BodyFor(who, creature));
        target.SetMeta(HoverRulesMeta, SalonMemberTips.SalonRulesBody(creature));

        if (target.HasMeta(HoverWiredMeta))
        {
            return;
        }
        target.SetMeta(HoverWiredMeta, true);
        target.MouseEntered += () => ShowHover(target);
        target.MouseExited += () => ClearHover(target);
    }

    private static void ShowHover(Control target)
    {
        if (!target.HasMeta(HoverTitleMeta))
        {
            return;
        }
        // Remove first: NHoverTipSet keys its live set by owner and ADDS,
        // so a second show without a teardown throws on the duplicate key.
        ClearHover(target);

        var tips = new List<IHoverTip>
        {
            new HoverTip(
                new LocString(KeywordTable,
                              (string)target.GetMeta(HoverTitleMeta)),
                (string)target.GetMeta(HoverBodyMeta)),
            new HoverTip(
                new LocString(KeywordTable,
                              SalonMemberTips.SalonRulesKey + ".title"),
                (string)target.GetMeta(HoverRulesMeta)),
        };
        NHoverTipSet.CreateAndShow(target, tips);
        target.SetMeta(HoverShownMeta, true);
    }

    private static void ClearHover(Control target)
    {
        if (!target.HasMeta(HoverShownMeta))
        {
            return;
        }
        target.RemoveMeta(HoverShownMeta);
        NHoverTipSet.Remove(target);
    }

    /// <summary>
    /// D7: the Encore ribbon is a RUNWAY, not a fill bar. The old
    /// denominator was a display-only 20 -- a lie twice over, because Encore
    /// is uncapped and because 20 meant nothing to the player. A segment is
    /// one TURN of upkeep at the current stage, so the bar answers the
    /// question the player actually has: how many more turns can the salon
    /// run itself?
    ///
    /// Deploying a member visibly SHORTENS the runway with Encore unchanged.
    /// That is correct and it is the point: the fifth member costs a turn of
    /// everyone's fuel.
    ///
    /// Draining to zero still plays the flash and dims the whole stage — the
    /// overdraw moment, shown as a consequence rather than as a number
    /// changing somewhere else.
    /// </summary>
    private static void RefreshRibbon(
        Node2D display, int encore, int members,
        AnimationPlayer? anim, bool animate)
    {
        // Zero members: a runway measures turns of upkeep, and an empty
        // stage has no upkeep, so segmenting would be dividing by a stage
        // that is not there. JUDGMENT CALL (the brief asks for the least
        // weird rendering and a note): the ribbon renders as one plain,
        // muted, FULL-WIDTH bar carrying the number. Full width because a
        // partial plain bar would imply a fraction of something, and there
        // is nothing to be a fraction of; muted because the bar is not
        // measuring anything right now.
        var segmentCost = members * SalonConstants.TickEncoreCost;
        var plain = display.GetNodeOrNull<ColorRect>("%RibbonPlain");
        if (plain != null)
        {
            plain.Visible = segmentCost <= 0;
        }

        var turns = segmentCost > 0 ? encore / (float)segmentCost : 0f;
        for (var i = 0; i < RunwaySegments; i++)
        {
            if (display.GetNodeOrNull<ColorRect>($"%Seg{i + 1}")
                is not { } seg)
            {
                continue;
            }
            // Partial LAST segment: a turn half-paid for is drawn half-wide,
            // so the bar drains continuously instead of snapping a whole
            // turn at a time. The scene's authored width is the full one.
            var fill = Mathf.Clamp(turns - i, 0f, 1f);
            seg.Visible = segmentCost > 0 && fill > 0f;
            if (!seg.HasMeta(SegmentWidthMeta))
            {
                seg.SetMeta(SegmentWidthMeta, seg.Size.X);
            }
            var full = (float)seg.GetMeta(SegmentWidthMeta);
            seg.Size = new Vector2(full * fill, seg.Size.Y);
        }

        if (display.GetNodeOrNull<Label>("%RunwayOverflow") is { } overflow)
        {
            overflow.Visible = segmentCost > 0 && turns > RunwaySegments;
        }

        if (display.GetNodeOrNull<Label>("%RibbonLabel") is { } label)
        {
            label.Text = encore.ToString();
        }

        int previous = display.HasMeta(PreviousEncoreMeta)
            ? (int)display.GetMeta(PreviousEncoreMeta)
            : encore;
        display.SetMeta(PreviousEncoreMeta, encore);

        if (animate && previous > 0 && encore <= 0 && anim != null)
        {
            anim.Stop();
            anim.Play("overdraw");
        }
    }
}
