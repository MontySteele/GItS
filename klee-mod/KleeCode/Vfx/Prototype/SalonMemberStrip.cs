using System;
using System.Collections.Generic;
using Godot;
using KleeMod.Cards;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.addons.mega_text;

namespace KleeMod.Vfx;

/// <summary>
/// THE SALON AS A MEMBER STRIP (`EB-627`, and `EB-628`'s pips).
///
/// THE FIND. [USER]'s own Furina act-1 run under the reframe, 2026-09-07:
/// "the Encore 'how many ticks of the stage do you have available' idea is not
/// bad, but it's too hard to tell who the stage members are or what they will
/// do." On screen were three freestanding blue silhouettes at her feet, a small
/// badge under each carrying one bare number, and a ribbon underneath carrying
/// another.
///
/// WHY THE SILHOUETTES GO, and why this is the SECOND time that art has failed
/// the same question. Sprint 1 framed three card-art portraits and they read as
/// "three identical blue smudges"; the D4 rework (2026-07-24,
/// <see cref="SalonVisualsBridge"/>'s header) replaced them with freestanding
/// silhouettes on the theory that outline carries identity where a crop does
/// not. At combat scale the silhouettes read the same way. The thing being
/// asked of the picture -- who is this, and what will it do next -- is not a
/// thing a 30-pixel outline of a crab can answer, and two attempts is enough
/// evidence that it never will be. So the picture stops carrying the whole
/// message: each member gets its face AND its short name AND its next act in
/// words, and the picture becomes the thing that makes the row scannable rather
/// than the thing that has to be decoded.
///
/// SLOT-INDEX-KEYED, Funnel Contract sec.1, unchanged and for its original
/// reason: deploy is by card and duplicates are legal, so chip i renders
/// whatever <see cref="SalonMemberPower.CompanyOf"/> reports at index i and
/// three Ushers render as three Ushers. Nothing here may assume distinct
/// members or a fixed member-to-slot mapping.
///
/// THE FRONT IS MARKED, and that is the half of the arm's rules the old stage
/// could not show at all. Under the reframe a Companion card performs the
/// FRONT member and a deploy onto a full stage Evokes it -- two rules that a
/// player can only act on if they can see which one it is. The rules paragraph
/// used to say "the leftmost member is the front" in words; a highlighted frame
/// says it where the decision is made, which is why `EB-629` can drop the
/// sentence.
///
/// THE NEXT ACT IS THE PERFORMANCE, and it is folded, not printed. The number
/// comes from <see cref="SalonMemberPower.TickValue"/> -- the same expression
/// the performance itself resolves through and the same one the member tips
/// fold the Fanfare bonus into -- so a chip cannot disagree with what the
/// member does. Chevalmarin's "Hydro to ALL" is her EVOKE and not her
/// performance (she performs for <see cref="SalonConstants.ChevalmarinTick"/>
/// Hydro at one body), so it appears on the FRONT chip only, and only while
/// the stage is FULL, which is exactly the state in which the next deploy
/// Evokes her. Printing it on every chip would be printing a number the player
/// cannot reach.
///
/// ENCORE IS A ROW OF PIPS (`EB-628`). The ribbon's runway drew turns of upkeep
/// -- a shipped-engine reading, because under the arm there is no upkeep and
/// members do not act on their own. A performance costs
/// <see cref="SalonConstants.TickEncoreCost"/>, so ONE PIP IS ONE PERFORMANCE,
/// which is the "ticks of stage available" reading [USER] liked, drawn as
/// ticks. The first <see cref="FurinaReframeLaw.SpotlightDesignateEncoreCost"/>
/// pips wear the Spotlight's colour, so the price of a designation is a thing
/// the player counts rather than remembers.
///
/// INSIDE THE CREATURE'S BOUNDS, on <see cref="SalonVisualsBridge"/>'s own
/// anchor and for its reason: the box is 240 wide, the band under her feet
/// belongs to `NCreatureStateDisplay` (the HP bar and the block badge), and a
/// strip that overhangs either edge lands in the enemy intent and targeting
/// lanes. The row is laid out from the LIVE cap, tightening as the cap grows,
/// capped at the shipped three-slot pitch so a normal Furina's strip does not
/// move when a card could have raised her cap.
///
/// BUILT IN CODE, NOT IN A SCENE, which is the one deliberate break from the
/// stage it replaces. `salon_stage.tscn` is a pck asset; the pck is built from
/// `pck-src` on a machine with the art tree, and an arm-only element that
/// cannot be drawn without a pck rebuild is an element the next `+proto` deploy
/// might silently not have. <see cref="Prototype.KokomiPlanStrip"/> and
/// <see cref="SparkCounter"/> build their trees the same way for the same
/// reason. The member ART is the pck's, reused verbatim from
/// <see cref="SalonVisualsBridge"/>'s own table -- a missing texture degrades
/// to name-and-number, never to nothing.
///
/// WHAT NOTHING HEADLESS CAN ANSWER. Whether the strip reads at combat scale,
/// whether the chips clear the HP bar, and whether the pips read as ticks.
/// Godot nodes cannot be built in the test host (KleeTests README, the headless
/// boundary), so the pins are the DECISIONS: the scope, the order, the words,
/// the folded number and the pip count. The look is owed a frame on the next
/// `+proto` deploy.
///
/// QUARANTINED. `Vfx/Prototype/**` is `Compile Remove`d without
/// `-p:PrototypeCards=true`. Revert is the flag.
/// </summary>
public static class SalonMemberStrip
{
    /// <summary>The node this file owns.</summary>
    internal const string RootName = "KleeModSalonMemberStrip";

    /// <summary>The stage's anchor, <see cref="SalonVisualsBridge"/>'s own
    /// value: the strip stands where the stage stood, so a player who has seen
    /// one build finds the other in the same place.</summary>
    internal static readonly Vector2 AnchorOffset = new(-104f, -52f);

    /// <summary>Chips the strip will ever draw. Three is the cap and five is
    /// what Box Seats upgraded can reach; a sixth has nowhere to go inside the
    /// bounds box and is logged rather than silently invisible.</summary>
    public const int MaxChips = 5;

    private const float ChipWidth = 58f;
    private const float ChipHeight = 62f;
    private const float FaceHeight = 32f;
    private const float ChipPitchMax = 62f;
    private const float HalfSpan = 79f;

    private const int NameFontSize = 11;
    private const int ActFontSize = 14;
    private const int EvokeFontSize = 10;
    private const int PipFontSize = 12;

    /// <summary>Pips drawn before the row overflows into "+N". Ten
    /// performances of runway is far past any decision the player is making,
    /// and an unbounded row would run off the bounds box.</summary>
    public const int MaxPips = 10;

    private const float PipWidth = 9f;
    private const float PipHeight = 12f;
    private const float PipGap = 4f;
    private const float PipRowY = ChipHeight + 6f;

    /// <summary>Accent per member, <see cref="SalonVisualsBridge"/>'s table by
    /// value: the strip and the stage are the same three characters and a
    /// second palette would be a second thing to keep true.</summary>
    private static readonly Dictionary<SalonMember, Color> Accent = new()
    {
        [SalonMember.Crabaletta] = new Color(0.941f, 0.439f, 0.549f),
        [SalonMember.Usher] = new Color(0.910f, 0.733f, 0.322f),
        [SalonMember.Chevalmarin] = new Color(0.373f, 0.878f, 0.824f),
    };

    /// <summary>Member art, pck-relative -- the same three files the stage's
    /// silhouettes are cut from (`tools/cut_salon_members.py`), reused rather
    /// than re-cut. A face crop of art we already ship costs no new asset and
    /// no new generator.</summary>
    private static readonly Dictionary<SalonMember, string> Faces = new()
    {
        [SalonMember.Usher] = "furina/salon/member_usher.png",
        [SalonMember.Chevalmarin] = "furina/salon/member_chevalmarin.png",
        [SalonMember.Crabaletta] = "furina/salon/member_crabaletta.png",
    };

    private static readonly Color ChipBack = new(0.06f, 0.11f, 0.18f, 0.82f);
    private static readonly Color EmptyBack = new(0.06f, 0.11f, 0.18f, 0.30f);
    private static readonly Color FrontFrame = new(1f, 0.94f, 0.72f, 0.95f);
    private static readonly Color DryText = new(0.36f, 0.44f, 0.57f);
    private static readonly Color PipFull = new(0.42f, 0.83f, 1f, 0.95f);
    private static readonly Color PipSpotlight = new(1f, 0.86f, 0.42f, 0.95f);
    private static readonly Color PipEmpty = new(0.28f, 0.34f, 0.44f, 0.35f);

    private static readonly TrackedDisplayBridge.Registry<Player> Displays = new();

    private static bool _warnedFace;

    // ---------------------------------------------------------- the scope --

    /// <summary>
    /// Is the strip this seat's stage? The MANUAL leg and nothing else --
    /// <see cref="SalonMemberTips.BodyFor"/>'s own gate, because the strip
    /// draws exactly what that leg's rules make true (members do not act on
    /// their own, a play performs the front, a deploy performs what it fields).
    /// Off the leg the shipped stage is the honest picture and this draws
    /// nothing.
    /// </summary>
    public static bool AppliesTo(Creature? creature) =>
        FurinaReframe.ManualLiveFor(creature);

    // ---------------------------------------------------------- the reads --

    /// <summary>The company in SLOT ORDER, straight from the power. The strip
    /// keeps no copy of the queue: duplicates and out-of-order deploys are the
    /// state's business, and a display that cached them would be the sprint-1
    /// desync one layer up.</summary>
    public static IReadOnlyList<SalonMember> Company(Creature owner) =>
        SalonMemberPower.CompanyOf(owner);

    /// <summary>How many chips this player's strip has.</summary>
    public static int Slots(Creature owner) =>
        Math.Min(MaxChips, SalonMemberPower.SlotsFor(owner));

    /// <summary>The member's name on the chip. SHORT: the card face prints
    /// "Mademoiselle Crabaletta" and a 58-pixel chip cannot, so the strip
    /// prints the half that is the member's own name and the tip keeps the
    /// full one.</summary>
    public static string ShortName(SalonMember member) => member switch
    {
        SalonMember.Crabaletta => "Crabaletta",
        SalonMember.Usher => "Usher",
        _ => "Chevalmarin",
    };

    /// <summary>The word the member's act is measured in.</summary>
    public static string ActWord(SalonMember member) =>
        member == SalonMember.Usher ? "Block" : "Hydro";

    /// <summary>
    /// WHAT THIS MEMBER DOES WHEN IT NEXT PERFORMS, as number and word.
    ///
    /// The number is <see cref="SalonMemberPower.TickValue"/>, which is where
    /// the Fanfare bonus, Grand Salon and the dry three-quarters all already
    /// live -- so the chip folds the bonus the way the member tips do because
    /// it is the same call, not because it repeats the arithmetic.
    /// </summary>
    public static string NextAct(Creature owner, SalonMember member, bool paid)
        => $"{SalonMemberPower.TickValue(owner, member, paid)} "
         + ActWord(member);

    /// <summary>
    /// What an Evoke of this member does, in the member tips' own words
    /// (<see cref="SalonMemberTips.BodyFor"/> under the arm). Drawn on the
    /// FRONT chip while the stage is full, because that is the one state in
    /// which the next deploy reaches it.
    /// </summary>
    public static string EvokeAct(SalonMember member) => member switch
    {
        SalonMember.Crabaletta =>
            $"Evoke {SalonConstants.CrabalettaBow} Hydro",
        SalonMember.Usher => $"Evoke {SalonConstants.UsherBow} Block",
        _ => "Evoke Hydro to ALL",
    };

    /// <summary>
    /// PERFORMANCES THE PLAYER CAN STILL PAY FOR: Encore divided by what one
    /// performance costs. One pip is one performance, which is the whole
    /// reading -- the ribbon's old segment was one TURN of upkeep, a shipped
    /// -engine unit that the manual leg deleted.
    /// </summary>
    public static int Pips(Creature owner) =>
        SalonConstants.TickEncoreCost > 0
            ? FurinaResources.Encore(owner) / SalonConstants.TickEncoreCost
            : 0;

    /// <summary>How many leading pips wear the Spotlight's colour: the price
    /// of a designation, read off the law rather than restated.</summary>
    public static int SpotlightPips =>
        FurinaReframeLaw.SpotlightDesignateEncoreCost;

    // ------------------------------------------------------- the lifecycle --

    /// <summary>Build the strip for this seat. Called from
    /// <see cref="SalonVisualsBridge.Setup"/>, which is the one door the stage
    /// has ever had -- the `NCombatUi.Activate` postfix -- so the strip and the
    /// stage cannot disagree about when a room is live.</summary>
    public static void Setup(NCombatRoom combatRoom, Player player)
    {
        var creature = player.Creature;
        if (creature == null || !AppliesTo(creature)) return;
        if (combatRoom?.CombatVfxContainer is not { } container) return;

        Displays.Discard(player);

        var root = Build();
        container.AddChildSafely(root);
        TrackedDisplayBridge.Track(combatRoom, creature, root, AnchorOffset);
        Displays.Set(player, root);
        Paint(root, creature);
    }

    /// <summary>Re-read the queue, the Fanfare bonus and the Encore, then
    /// redraw. Driven by <see cref="SalonVisualsBridge.Refresh"/>, i.e. by the
    /// Funnel Contract's own funnels -- the deploy funnel and the Encore
    /// gain/spend/absorb trio. No `_Process` anywhere in this file.</summary>
    public static void Refresh(Creature? creature)
    {
        var player = creature?.Player;
        if (creature == null || player == null || !AppliesTo(creature)) return;

        var root = Displays.Get(player);
        if (root == null)
        {
            // Stale or never built (a mid-combat reload): rebuild in place,
            // the reference-bridge idiom `GaugeBridge.Refresh` uses.
            if (NCombatRoom.Instance is not { } room) return;
            Setup(room, player);
            root = Displays.Get(player);
            if (root == null) return;
        }

        Paint(root, creature);
    }

    public static void Discard(Player player) => Displays.Discard(player);

    // ---------------------------------------------------------- the tree --

    private static Node2D Build()
    {
        var root = new Node2D { Name = RootName };

        for (var i = 0; i < MaxChips; i++)
        {
            var chip = new Control
            {
                Name = $"Chip{i}",
                MouseFilter = Control.MouseFilterEnum.Ignore,
                // `EB-300`: display only, never in the controller's focus
                // graph. A player walking the HUD must not land on a picture
                // of a crab with no way back to the hand.
                FocusMode = Control.FocusModeEnum.None,
                Size = new Vector2(ChipWidth, ChipHeight),
                Visible = false,
            };

            chip.AddChildSafely(new ColorRect
            {
                Name = "Back",
                MouseFilter = Control.MouseFilterEnum.Ignore,
                Position = Vector2.Zero,
                Size = new Vector2(ChipWidth, ChipHeight),
            });

            // The front marker. A FRAME rather than a tint, so it survives the
            // dry grey: "which one is the front" and "can the stage pay" are
            // two different questions and neither may eat the other's channel.
            chip.AddChildSafely(new ColorRect
            {
                Name = "Frame",
                MouseFilter = Control.MouseFilterEnum.Ignore,
                Position = new Vector2(-2f, -2f),
                Size = new Vector2(ChipWidth + 4f, ChipHeight + 4f),
                Visible = false,
                ZIndex = -1,
            });

            chip.AddChildSafely(new TextureRect
            {
                Name = "Face",
                MouseFilter = Control.MouseFilterEnum.Ignore,
                FocusMode = Control.FocusModeEnum.None,
                ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
                StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
                Position = new Vector2(0f, 1f),
                Size = new Vector2(ChipWidth, FaceHeight),
            });

            chip.AddChildSafely(Text("Name", NameFontSize,
                new Vector2(0f, FaceHeight + 1f)));
            chip.AddChildSafely(Text("Act", ActFontSize,
                new Vector2(0f, FaceHeight + 14f)));
            chip.AddChildSafely(Text("Evoke", EvokeFontSize,
                new Vector2(0f, FaceHeight + 30f)));

            root.AddChildSafely(chip);
        }

        var pips = new Control
        {
            Name = "Pips",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            Position = new Vector2(0f, PipRowY),
            Size = new Vector2(2f * HalfSpan, PipHeight),
        };
        for (var i = 0; i < MaxPips; i++)
        {
            pips.AddChildSafely(new ColorRect
            {
                Name = $"Pip{i}",
                MouseFilter = Control.MouseFilterEnum.Ignore,
                Position = new Vector2(i * (PipWidth + PipGap), 0f),
                Size = new Vector2(PipWidth, PipHeight),
                Visible = false,
            });
        }
        pips.AddChildSafely(Text("Overflow", PipFontSize,
            new Vector2(MaxPips * (PipWidth + PipGap) + 2f, -2f)));
        root.AddChildSafely(pips);

        return root;
    }

    private static Label Text(string name, int size, Vector2 at) =>
        Sized(new Label
        {
            Name = name,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
            Position = at,
            Size = new Vector2(ChipWidth, 14f),
        }, size);

    private static Label Sized(Label label, int size)
    {
        label.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize, size);
        return label;
    }

    // --------------------------------------------------------- the drawing --

    private static void Paint(Node2D root, Creature owner)
    {
        if (!GodotObject.IsInstanceValid(root)) return;

        var company = Company(owner);
        var slots = Slots(owner);
        var encore = FurinaResources.Encore(owner);
        var paid = encore >= SalonConstants.TickEncoreCost;
        var full = company.Count >= slots;

        var pitch = slots > 1
            ? Mathf.Min(ChipPitchMax, 2f * HalfSpan / (slots - 1))
            : ChipPitchMax;
        var centre = (slots - 1) / 2f;

        for (var i = 0; i < MaxChips; i++)
        {
            if (root.GetNodeOrNull<Control>($"Chip{i}") is not { } chip)
            {
                continue;
            }

            chip.Visible = i < slots;
            if (i >= slots) continue;

            chip.Position = new Vector2(
                (i - centre) * pitch - ChipWidth / 2f, 0f);
            PaintChip(chip, owner, i, i < company.Count ? company[i] : null,
                      paid, front: i == 0, full: full);
        }

        PaintPips(root, owner);
    }

    private static void PaintChip(
        Control chip, Creature owner, int index, SalonMember? member,
        bool paid, bool front, bool full)
    {
        var occupied = member is { } _;

        if (chip.GetNodeOrNull<ColorRect>("Back") is { } back)
        {
            back.Color = occupied ? ChipBack : EmptyBack;
        }

        // An EMPTY chip is drawn dim rather than hidden: the strip's width is
        // the cap, and a stage of one that renders as one chip tells the
        // player nothing about the two seats they still have.
        if (chip.GetNodeOrNull<ColorRect>("Frame") is { } frame)
        {
            frame.Visible = occupied && front;
            frame.Color = FrontFrame;
        }

        var face = chip.GetNodeOrNull<TextureRect>("Face");
        var name = chip.GetNodeOrNull<Label>("Name");
        var act = chip.GetNodeOrNull<Label>("Act");
        var evoke = chip.GetNodeOrNull<Label>("Evoke");

        if (member is not { } who)
        {
            if (face != null) face.Visible = false;
            if (name != null) { name.Visible = true; name.Text = "—"; }
            if (act != null) { act.Visible = false; }
            if (evoke != null) evoke.Visible = false;
            if (name != null)
            {
                name.AddThemeColorOverride(
                    ThemeConstants.Label.FontColor, PipEmpty);
            }
            return;
        }

        var accent = Accent.TryGetValue(who, out var hue) ? hue : FrontFrame;

        if (face != null)
        {
            SetFace(face, who);
        }

        if (name != null)
        {
            name.Visible = true;
            name.Text = ShortName(who);
            name.AddThemeColorOverride(
                ThemeConstants.Label.FontColor, paid ? accent : DryText);
        }

        if (act != null)
        {
            act.Visible = true;
            act.Text = NextAct(owner, who, paid);
            act.AddThemeColorOverride(
                ThemeConstants.Label.FontColor,
                paid ? StsColors.cream : DryText);
        }

        if (evoke != null)
        {
            // Only the front, and only on a full stage: that is the one board
            // state in which a deploy reaches this member's Evoke.
            evoke.Visible = front && full;
            evoke.Text = EvokeAct(who);
            evoke.AddThemeColorOverride(
                ThemeConstants.Label.FontColor, DryText);
        }
    }

    private static void PaintPips(Node2D root, Creature owner)
    {
        if (root.GetNodeOrNull<Control>("Pips") is not { } row) return;

        var pips = Pips(owner);
        var drawn = Math.Min(pips, MaxPips);

        for (var i = 0; i < MaxPips; i++)
        {
            if (row.GetNodeOrNull<ColorRect>($"Pip{i}") is not { } pip)
            {
                continue;
            }
            pip.Visible = true;
            pip.Color = i >= drawn
                ? PipEmpty
                : i < SpotlightPips ? PipSpotlight : PipFull;
        }

        if (row.GetNodeOrNull<Label>("Overflow") is { } overflow)
        {
            overflow.Visible = pips > MaxPips;
            overflow.Text = $"+{pips - MaxPips}";
            overflow.AddThemeColorOverride(
                ThemeConstants.Label.FontColor, PipFull);
        }
    }

    /// <summary>
    /// The member's art, RESOLVED FRESH ON EVERY PAINT and never held across a
    /// scene. `EB-222`: the engine preloads a room's assets and frees them with
    /// the room, so a cached <c>Texture2D</c> becomes a corpse the next combat
    /// hands to <c>TextureRect.SetTexture</c> -- which stuck a room and ended a
    /// run once already. Losing the picture leaves the name and the number,
    /// which is the half the chip exists for; throwing here would be a run.
    /// </summary>
    private static void SetFace(TextureRect face, SalonMember member)
    {
        try
        {
            var relative = Faces.TryGetValue(member, out var r) ? r : null;
            var path = relative == null ? null : KleePck.Path(relative);
            var texture = path == null
                ? null
                : ResourceLoader.Load<Texture2D>(path);

            if (texture == null || !GodotObject.IsInstanceValid(texture))
            {
                Warn(relative);
                face.Visible = false;
                return;
            }

            face.Texture = texture;
            face.Visible = true;
        }
        catch (Exception e)
        {
            Warn($"{member} ({e.GetType().Name}: {e.Message})");
            face.Visible = false;
        }
    }

    private static void Warn(string? what)
    {
        if (_warnedFace) return;
        _warnedFace = true;
        Log.Warn($"[{KleeMod.ModId}] salon strip: no live face art for "
               + $"{what ?? "a member"}; drawing the name and the number "
               + "alone.");
    }
}
