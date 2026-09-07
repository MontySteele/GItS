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
/// THE SALON PANEL: ONE ELEMENT FOR THE WHOLE BOARD (`EB-627`, `EB-628`,
/// `EB-633`, `EB-634`, `EB-635`).
///
/// THE FIND. [USER]'s own Furina act-1 run under the reframe, 2026-09-07: "the
/// Encore 'how many ticks of the stage do you have available' idea is not bad,
/// but it's too hard to tell who the stage members are or what they will do",
/// and then, on the rebuilt board's frame, "I don't see Encore anywhere". On
/// screen were three freestanding blue silhouettes at her feet, a small badge
/// under each carrying one bare number, a ribbon underneath carrying another,
/// and -- after the first rebuild -- a chip strip whose pip row sat under the
/// HP bar, a Fanfare badge in the energy corner the size of the energy orb,
/// and three duplicate numbers in the status row.
///
/// WHY ONE PANEL AND NOT FOUR WIDGETS. The first rebuild fixed each complaint
/// where it was made: chips for the silhouettes, pips for the ribbon, a badge
/// beside the orb for the meter. That is four elements in three parts of the
/// screen describing ONE board, and the frame shows what it costs -- the state
/// a player needs in order to price a Companion play (who is in front, what it
/// pays, whether the stage can pay for it) was split across the creature's
/// feet, the bottom-left corner and the status strip, and the piece that
/// answered "can she pay" was the one that had gone invisible. So the board
/// becomes one group with a backing rectangle: everything about the Salon is
/// in one rectangle, and nothing about the Salon is anywhere else.
///
/// WHY THE SILHOUETTES WENT, and why it was the SECOND time art failed that
/// question. Sprint 1 framed three card-art portraits and they read as "three
/// identical blue smudges"; the D4 rework (2026-07-24,
/// <see cref="SalonVisualsBridge"/>'s header) replaced them with freestanding
/// silhouettes on the theory that outline carries identity where a crop does
/// not, and at combat scale the silhouettes read the same way. What is being
/// asked of the picture -- who is this, and what will it do next -- is not a
/// thing a 30-pixel outline of a crab can answer. So the picture stops
/// carrying the message: each member gets its face AND its short name AND its
/// next act in words, and the picture makes the row scannable instead.
///
/// SLOT-INDEX-KEYED, Funnel Contract sec.1, unchanged and for its original
/// reason: deploy is by card and duplicates are legal, so chip i renders
/// whatever <see cref="SalonMemberPower.CompanyOf"/> reports at index i and
/// three Ushers render as three visibly separate Ushers. Nothing here may
/// assume distinct members or a fixed member-to-slot mapping.
///
/// THE FRONT IS NAMED, not just framed. Under the reframe a Companion card
/// performs the FRONT member and a deploy onto a full stage Evokes it -- two
/// rules a player can only act on if they can see which one it is -- and the
/// first rebuild marked it with a gold border alone. A border says "this one
/// is special" and does not say WHAT is special about it, so chip 0 now
/// carries the word <see cref="FrontWord"/> as well as the frame, and
/// `EB-629` keeps the sentence off the rules paragraph on that strength.
///
/// THE NEXT ACT IS THE PERFORMANCE, folded and not printed, and it is TIER 1
/// (<see cref="FurinaBoardScale"/>) because it is the number every play is
/// priced against. It comes from <see cref="SalonMemberPower.TickValue"/> --
/// the same expression the performance resolves through and the same one the
/// member tips fold the Fanfare bonus into -- so a chip cannot disagree with
/// what the member does, and at Encore 0 it is already the dry three-quarters
/// number rather than the wet one.
///
/// THE RESOURCE LINE IS A NAME AND A NUMBER FIRST (`EB-635`). "I don't see
/// Encore anywhere" was true twice over: Encore was 0, so every pip was drawn
/// in the empty colour, and the row itself sat in the band
/// `NCreatureStateDisplay` owns and was covered by the HP bar. A row of dim
/// pips at zero is indistinguishable from no row, so the line leads with the
/// WORD and the NUMBER -- "Encore 2 - Fanfare 13 - Member bonus +1" -- and the
/// pips are a secondary reading beside that number rather than the only one.
///
/// AND AT ZERO IT SAYS THE STAGE HAS NOT STOPPED (`EB-633`). The pips count
/// FULL-STRENGTH performances, which is what one <c>TickEncoreCost</c> buys; a
/// member with nothing to spend still performs, at three-quarters. An empty
/// meter therefore must not read as an idle stage, so the panel prints
/// <see cref="ReducedNotice"/> exactly when the buffer cannot pay -- the same
/// condition <see cref="Paid"/> hands the chips, so the note and the numbers
/// cannot disagree.
///
/// FANFARE'S THRESHOLD IS A TOOLTIP, not a line. "+1 at 20" is a footnote to
/// the Fanfare number and was drawn as a second number under a badge the size
/// of the energy orb; on the panel it hangs off the resource line's hover
/// (<see cref="StepText"/>) so the line stays one sentence.
///
/// ABOVE HER, AND CLEAR OF THE BAND THAT IS NOT OURS. The old anchor put the
/// stage at the creature's feet, which is where `NCreatureStateDisplay` draws
/// the HP bar and the block badge, and both rebuilds lost a row to it. The
/// overhead region is the one measured clear space on this rig -- Furina's
/// combat box tops out at -280 (`GaugeBridge`'s own reading) and the Burst
/// slot at -300 is RETIRED under the arm (`EB-365`) -- so the panel sits above
/// that: its bottom edge is the Burst slot and its top is
/// <see cref="AnchorOffset"/>. It is <see cref="FurinaBoardScale.PanelWidth"/>
/// wide, which is the creature's own bounds width, so it cannot overhang into
/// the enemy intent or targeting lanes on either side, and it is nowhere near
/// the hand's expansion at the bottom of the screen.
///
/// BUILT IN CODE, NOT IN A SCENE, the one deliberate break from the stage it
/// replaces. `salon_stage.tscn` is a pck asset built on a machine with the art
/// tree, and an arm-only element that cannot be drawn without a pck rebuild is
/// an element the next `+proto` deploy might silently not have.
/// <see cref="KokomiPlanStrip"/> and <see cref="SparkCounter"/> build their
/// trees the same way for the same reason. The member ART is the pck's, reused
/// verbatim from <see cref="SalonVisualsBridge"/>'s own table -- a missing
/// texture degrades to name-and-number, never to nothing.
///
/// WHAT NOTHING HEADLESS CAN ANSWER. Whether the panel reads at combat scale,
/// whether the anchor clears the hand's expansion and the targeting arrows,
/// and whether the tiers land as a hierarchy. Godot nodes cannot be built in
/// the test host (KleeTests README, the headless boundary), so the pins are the
/// DECISIONS: the scope, the order, the words, the folded number, the counts
/// and the tier every element declares. The look is owed a frame on the next
/// `+proto` deploy.
///
/// QUARANTINED. `Vfx/Prototype/**` is `Compile Remove`d without
/// `-p:PrototypeCards=true`. Revert is the flag.
/// </summary>
public static class SalonPanel
{
    /// <summary>The node this file owns.</summary>
    internal const string RootName = "KleeModSalonPanel";

    /// <summary>
    /// The panel's top-left, relative to Furina's creature origin.
    ///
    /// ABOVE THE RIG AND ABOVE THE RETIRED BURST SLOT. `GaugeBridge` measured
    /// Furina's combat box as topping out at -280 and put the cross-character
    /// Burst slot at -300; under this arm that slot draws nothing (`EB-365`),
    /// so the panel's BOTTOM edge is -300 and its top is that less
    /// <see cref="FurinaBoardScale.PanelHeight"/>. Centred on her, so the
    /// 240-wide box is the creature's own bounds and overhangs neither lane.
    /// </summary>
    internal static readonly Vector2 AnchorOffset =
        new(-FurinaBoardScale.PanelWidth / 2f,
            -300f - FurinaBoardScale.PanelHeight);

    /// <summary>Chips the panel will ever draw. Three is the cap and five is
    /// what Box Seats upgraded can reach; a sixth has nowhere to go inside the
    /// box and is logged rather than silently invisible.</summary>
    public const int MaxChips = 5;

    /// <summary>Pips drawn beside the Encore number. The NUMBER is the reading
    /// (`EB-635`) and the pips are the secondary one, so the strip is sized to
    /// the decisions a player is actually making rather than to any runway
    /// they could reach.</summary>
    public const int MaxPips = 6;

    /// <summary>The word on chip 0. A gold border says "this one is special"
    /// and not WHAT is special about it; this says it.</summary>
    public const string FrontWord = "FRONT";

    /// <summary>What the panel prints when the buffer cannot pay for a
    /// full-strength performance. `EB-633`: an empty meter must not read as an
    /// idle stage.</summary>
    public const string ReducedNotice = "Reduced performance";

    /// <summary>Accent per member, <see cref="SalonVisualsBridge"/>'s table by
    /// value: the panel and the stage are the same three characters and a
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

    /// <summary>The panel's own ground. Restrained and dark so the tiers read
    /// against a lit background as well as a black one, and translucent so it
    /// is a panel rather than a hole in the scene.</summary>
    private static readonly Color PanelBack = new(0.04f, 0.07f, 0.12f, 0.78f);
    private static readonly Color ChipBack = new(0.06f, 0.11f, 0.18f, 0.82f);
    private static readonly Color EmptyBack = new(0.06f, 0.11f, 0.18f, 0.30f);
    private static readonly Color FrontFrame = new(1f, 0.94f, 0.72f, 0.95f);
    private static readonly Color DryText = new(0.36f, 0.44f, 0.57f);
    private static readonly Color NoticeText = new(1f, 0.78f, 0.42f, 0.95f);
    private static readonly Color PipFull = new(0.42f, 0.83f, 1f, 0.95f);
    private static readonly Color PipEmpty = new(0.28f, 0.34f, 0.44f, 0.55f);

    private static readonly TrackedDisplayBridge.Registry<Player> Displays = new();

    private static bool _warnedFace;

    // ---------------------------------------------------------- the scope --

    /// <summary>
    /// Is the panel this seat's board? The MANUAL leg and nothing else --
    /// <see cref="SalonMemberTips.BodyFor"/>'s own gate, because the panel
    /// draws exactly what that leg's rules make true (members do not act on
    /// their own, a play performs the front, a deploy performs what it fields).
    /// Off the leg the shipped stage is the honest picture and this draws
    /// nothing.
    /// </summary>
    public static bool AppliesTo(Creature? creature) =>
        FurinaReframe.ManualLiveFor(creature);

    // ---------------------------------------------------------- the reads --

    /// <summary>The company in SLOT ORDER, straight from the power. The panel
    /// keeps no copy of the queue: duplicates and out-of-order deploys are the
    /// state's business, and a display that cached them would be the sprint-1
    /// desync one layer up.</summary>
    public static IReadOnlyList<SalonMember> Company(Creature owner) =>
        SalonMemberPower.CompanyOf(owner);

    /// <summary>How many chips this player's panel has.</summary>
    public static int Slots(Creature owner) =>
        Math.Min(MaxChips, SalonMemberPower.SlotsFor(owner));

    /// <summary>The member's name on the chip. SHORT: the card face prints
    /// "Mademoiselle Crabaletta" and a 70-pixel chip cannot, so the panel
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
    ///
    /// `EB-630`. CHEVALMARIN'S LINE CARRIES HER REFUND. It read "Hydro to ALL"
    /// and stopped, which is half her Evoke: she also grants
    /// <see cref="SalonConstants.ChevalmarinBowEncore"/> Encore, and that is
    /// the number which makes replacing her a resource decision rather than a
    /// loss. Interpolated and never typed, on `EB-89`'s rule.
    /// </summary>
    public static string EvokeAct(SalonMember member) => member switch
    {
        SalonMember.Crabaletta =>
            $"Evoke {SalonConstants.CrabalettaBow} Hydro",
        SalonMember.Usher => $"Evoke {SalonConstants.UsherBow} Block",
        _ => "Evoke Hydro to ALL, "
           + $"+{SalonConstants.ChevalmarinBowEncore} Encore",
    };

    /// <summary>
    /// Can the stage pay for a FULL-STRENGTH performance right now? The one
    /// expression the chips, the pips and the reduced-performance notice all
    /// read, so the number, the row and the note cannot disagree about whether
    /// the buffer is dry.
    /// </summary>
    public static bool Paid(Creature owner) =>
        FurinaResources.Encore(owner) >= SalonConstants.TickEncoreCost;

    /// <summary>
    /// PERFORMANCES THE PLAYER CAN STILL PAY FOR IN FULL: Encore divided by
    /// what one performance costs. One pip is one FULL-STRENGTH performance,
    /// which is the whole reading -- the ribbon's old segment was one TURN of
    /// upkeep, a shipped-engine unit the manual leg deleted, and `EB-633`'s
    /// correction is that "remaining" was never the right word either, since a
    /// member with nothing to spend still performs at three-quarters.
    /// </summary>
    public static int Pips(Creature owner) =>
        SalonConstants.TickEncoreCost > 0
            ? FurinaResources.Encore(owner) / SalonConstants.TickEncoreCost
            : 0;

    /// <summary>The Fanfare the panel prints, through the accessor every
    /// reader in the kit uses -- the same one
    /// <see cref="SalonMemberPower.TickValue"/> divides for the member bonus,
    /// so the line and the chips cannot disagree.</summary>
    public static int Fanfare(Creature owner) =>
        FurinaResources.ReadableFanfare(owner);

    /// <summary>How much Fanfare is adding to every member number right now:
    /// the third segment of the resource line, and the one that says what the
    /// second segment is FOR.</summary>
    public static int MemberBonus(Creature owner) =>
        SalonConstants.FocusPerFanfare > 0
            ? Fanfare(owner) / SalonConstants.FocusPerFanfare
            : 0;

    /// <summary>
    /// The Fanfare at which member numbers go up by one more: the NEXT
    /// multiple of <see cref="SalonConstants.FocusPerFanfare"/> strictly above
    /// what is held, so a reading sitting exactly on a threshold points at the
    /// next one rather than at itself.
    /// </summary>
    public static int NextThreshold(Creature owner)
    {
        var step = SalonConstants.FocusPerFanfare;
        if (step <= 0) return 0;
        return (Fanfare(owner) / step + 1) * step;
    }

    /// <summary>
    /// The head of the resource line. Encore leads with its NAME and its
    /// NUMBER (`EB-635`), before any pips.
    /// </summary>
    public static string EncoreText(Creature owner) =>
        $"Encore {FurinaResources.Encore(owner)}";

    /// <summary>The tail of the same line: the meter and what it buys. Read as
    /// one sentence with <see cref="EncoreText"/>, the pips between them.
    /// "Member bonus" and not "Focus" because that bonus is the ONE thing
    /// Fanfare does under the arm, and the chips above are where it lands.
    /// </summary>
    public static string MeterText(Creature owner) =>
        $"- Fanfare {Fanfare(owner)} - Member bonus +{MemberBonus(owner)}";

    /// <summary>The threshold, which is a FOOTNOTE to the Fanfare number and
    /// hangs off the line's hover rather than sitting on it.</summary>
    public static string StepText(Creature owner) =>
        $"+1 at {NextThreshold(owner)}";

    // ------------------------------------------------------- the lifecycle --

    /// <summary>Build the panel for this seat. Called from
    /// <see cref="SalonVisualsBridge.Setup"/>, which is the one door the stage
    /// has ever had -- the `NCombatUi.Activate` postfix -- so the panel and the
    /// stage cannot disagree about when a room is live.</summary>
    public static void Setup(NCombatRoom combatRoom, Player player)
    {
        var creature = player.Creature;
        if (creature == null || !AppliesTo(creature)) return;
        if (combatRoom?.CombatVfxContainer is not { } container) return;

        Displays.Discard(player);

        var root = Build(FurinaBoardScale.EnergyOrbFontSize(combatRoom.Ui));
        container.AddChildSafely(root);
        TrackedDisplayBridge.Track(combatRoom, creature, root, AnchorOffset);
        Displays.Set(player, root);
        Paint(root, creature);
    }

    /// <summary>Re-read the queue, the Fanfare bonus and the Encore, then
    /// redraw. Driven by <see cref="SalonVisualsBridge.Refresh"/>, i.e. by the
    /// Funnel Contract's own funnels -- the deploy funnel, the Encore
    /// gain/spend/absorb trio and `FurinaResources.SyncMeters` for the Fanfare
    /// half. No `_Process` anywhere in this file.</summary>
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

    private static Node2D Build(int? energyOrbFontSize)
    {
        var root = new Node2D { Name = RootName };

        // THE BACKING RECTANGLE, and it is why this is a panel rather than
        // four widgets: everything about the Salon is inside it, and it gives
        // the tiers a constant ground to read against on any background.
        root.AddChildSafely(new ColorRect
        {
            Name = "Back",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Position = Vector2.Zero,
            Size = new Vector2(FurinaBoardScale.PanelWidth,
                               FurinaBoardScale.PanelHeight),
            Color = PanelBack,
            ZIndex = -2,
        });

        root.AddChildSafely(BuildResourceRow(energyOrbFontSize));

        for (var i = 0; i < MaxChips; i++)
        {
            root.AddChildSafely(BuildChip(i));
        }

        // `EB-633`: the note that an empty meter is not an idle stage.
        var notice = Text("Notice", FurinaBoardScale.Tier3FontSize,
            new Vector2(FurinaBoardScale.PanelPad,
                        FurinaBoardScale.NoticeRowY),
            FurinaBoardScale.PanelWidth - 2f * FurinaBoardScale.PanelPad,
            FurinaBoardScale.NoticeRowHeight);
        notice.Visible = false;
        root.AddChildSafely(notice);

        return root;
    }

    private static Control BuildResourceRow(int? energyOrbFontSize)
    {
        // TIER 2, AND UNDER THE ENERGY ORB'S NUMBER (`EB-634`). The clamp is
        // live rather than asserted: the orb's own size is read off the scene
        // where the scene will give it up, and the documented fallback stands
        // where it will not.
        var size = FurinaBoardScale.ResourceFontSize(energyOrbFontSize);
        var row = new Control
        {
            Name = "Resources",
            // PASS and not Ignore: the Fanfare threshold is a hover tooltip on
            // this row (`TooltipText`, painted below), and Godot will not show
            // one on a control that ignores the mouse. `Pass` still hands the
            // event on, so nothing under the panel loses a click.
            MouseFilter = Control.MouseFilterEnum.Pass,
            FocusMode = Control.FocusModeEnum.None,
            Position = new Vector2(0f, FurinaBoardScale.ResourceRowY),
            Size = new Vector2(FurinaBoardScale.PanelWidth,
                               FurinaBoardScale.ResourceRowHeight),
        };

        var encore = Text("Encore", size,
            new Vector2(FurinaBoardScale.PanelPad, 0f),
            FurinaBoardScale.PipStripX - FurinaBoardScale.PanelPad,
            FurinaBoardScale.ResourceRowHeight);
        encore.HorizontalAlignment = HorizontalAlignment.Left;
        row.AddChildSafely(encore);

        var pips = new Control
        {
            Name = "Pips",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            Position = new Vector2(FurinaBoardScale.PipStripX, 3f),
            Size = new Vector2(FurinaBoardScale.PipStripWidth,
                               FurinaBoardScale.PipHeight),
        };
        for (var i = 0; i < MaxPips; i++)
        {
            pips.AddChildSafely(new ColorRect
            {
                Name = $"Pip{i}",
                MouseFilter = Control.MouseFilterEnum.Ignore,
                Position = new Vector2(
                    i * (FurinaBoardScale.PipWidth + FurinaBoardScale.PipGap),
                    0f),
                Size = new Vector2(FurinaBoardScale.PipWidth,
                                   FurinaBoardScale.PipHeight),
                Visible = false,
            });
        }
        row.AddChildSafely(pips);

        var meters = Text("Meters", size,
            new Vector2(FurinaBoardScale.PipStripX
                        + FurinaBoardScale.PipStripWidth, 0f),
            FurinaBoardScale.PanelWidth - FurinaBoardScale.PipStripX
                - FurinaBoardScale.PipStripWidth - FurinaBoardScale.PanelPad,
            FurinaBoardScale.ResourceRowHeight);
        meters.HorizontalAlignment = HorizontalAlignment.Left;
        row.AddChildSafely(meters);

        return row;
    }

    private static Control BuildChip(int index)
    {
        var chip = new Control
        {
            Name = $"Chip{index}",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            // `EB-300`: display only, never in the controller's focus graph.
            // A player walking the HUD must not land on a picture of a crab
            // with no way back to the hand.
            FocusMode = Control.FocusModeEnum.None,
            Size = new Vector2(FurinaBoardScale.ChipWidth,
                               FurinaBoardScale.ChipHeight),
            Visible = false,
        };

        chip.AddChildSafely(new ColorRect
        {
            Name = "Back",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Position = Vector2.Zero,
            Size = new Vector2(FurinaBoardScale.ChipWidth,
                               FurinaBoardScale.ChipHeight),
        });

        // The front marker's FRAME. A frame rather than a tint, so it survives
        // the dry grey: "which one is the front" and "can the stage pay" are
        // two different questions and neither may eat the other's channel. The
        // WORD beside it is `FrontWord`, below.
        chip.AddChildSafely(new ColorRect
        {
            Name = "Frame",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Position = new Vector2(-2f, -2f),
            Size = new Vector2(FurinaBoardScale.ChipWidth + 4f,
                               FurinaBoardScale.ChipHeight + 4f),
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
            Size = new Vector2(FurinaBoardScale.ChipWidth,
                               FurinaBoardScale.FaceHeight),
        });

        // TIER 2: who this is.
        chip.AddChildSafely(Text("Name", FurinaBoardScale.Tier2FontSize,
            new Vector2(0f, FurinaBoardScale.FaceHeight + 1f),
            FurinaBoardScale.ChipWidth, 14f));
        // TIER 1: what it pays. The largest thing on the panel.
        chip.AddChildSafely(Text("Act", FurinaBoardScale.Tier1FontSize,
            new Vector2(0f, FurinaBoardScale.FaceHeight + 15f),
            FurinaBoardScale.ChipWidth, 22f));
        // TIER 3: the two qualifiers.
        chip.AddChildSafely(Text("Front", FurinaBoardScale.Tier3FontSize,
            new Vector2(0f, FurinaBoardScale.FaceHeight + 37f),
            FurinaBoardScale.ChipWidth, 12f));
        chip.AddChildSafely(Text("Evoke", FurinaBoardScale.Tier3FontSize,
            new Vector2(0f, FurinaBoardScale.FaceHeight + 49f),
            FurinaBoardScale.ChipWidth, 12f));

        return chip;
    }

    private static Label Text(string name, int size, Vector2 at,
                              float width, float height) =>
        Sized(new Label
        {
            Name = name,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
            Position = at,
            Size = new Vector2(width, height),
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
        var paid = Paid(owner);
        var full = company.Count >= slots;

        var span = FurinaBoardScale.PanelWidth - 2f * FurinaBoardScale.PanelPad;
        var pitch = slots > 1
            ? Mathf.Min(FurinaBoardScale.ChipPitchMax, span / slots)
            : FurinaBoardScale.ChipPitchMax;
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
                FurinaBoardScale.PanelWidth / 2f + (i - centre) * pitch
                    - FurinaBoardScale.ChipWidth / 2f,
                FurinaBoardScale.ChipsRowY);
            PaintChip(chip, owner, i < company.Count ? company[i] : null,
                      paid, front: i == 0, full: full);
        }

        PaintResources(root, owner, paid);
    }

    private static void PaintChip(
        Control chip, Creature owner, SalonMember? member,
        bool paid, bool front, bool full)
    {
        var occupied = member is { } _;

        if (chip.GetNodeOrNull<ColorRect>("Back") is { } back)
        {
            back.Color = occupied ? ChipBack : EmptyBack;
        }

        // An EMPTY chip is drawn dim rather than hidden: the panel's width is
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
        var frontLabel = chip.GetNodeOrNull<Label>("Front");
        var evoke = chip.GetNodeOrNull<Label>("Evoke");

        if (member is not { } who)
        {
            if (face != null) face.Visible = false;
            if (name != null) { name.Visible = true; name.Text = "—"; }
            if (act != null) act.Visible = false;
            if (frontLabel != null) frontLabel.Visible = false;
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

        // THE FRONT IS NAMED. The frame says "this one is special"; the word
        // says what is special about it, which is the rule a Companion play
        // acts on.
        if (frontLabel != null)
        {
            frontLabel.Visible = front;
            frontLabel.Text = FrontWord;
            frontLabel.AddThemeColorOverride(
                ThemeConstants.Label.FontColor, FrontFrame);
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

    private static void PaintResources(Node2D root, Creature owner, bool paid)
    {
        if (root.GetNodeOrNull<Control>("Resources") is { } row)
        {
            if (row.GetNodeOrNull<Label>("Encore") is { } encore)
            {
                encore.Text = EncoreText(owner);
                encore.AddThemeColorOverride(
                    ThemeConstants.Label.FontColor,
                    paid ? StsColors.cream : DryText);
            }

            if (row.GetNodeOrNull<Label>("Meters") is { } meters)
            {
                meters.Text = MeterText(owner);
                meters.AddThemeColorOverride(
                    ThemeConstants.Label.FontColor, StsColors.cream);
            }

            // The threshold is a FOOTNOTE and hangs off the hover, so the line
            // stays one sentence.
            row.TooltipText = StepText(owner);

            PaintPips(row, owner);
        }

        if (root.GetNodeOrNull<Label>("Notice") is { } notice)
        {
            notice.Visible = !paid;
            notice.Text = ReducedNotice;
            notice.AddThemeColorOverride(
                ThemeConstants.Label.FontColor, NoticeText);
        }
    }

    private static void PaintPips(Control row, Creature owner)
    {
        if (row.GetNodeOrNull<Control>("Pips") is not { } strip) return;

        var drawn = Math.Min(Pips(owner), MaxPips);

        for (var i = 0; i < MaxPips; i++)
        {
            if (strip.GetNodeOrNull<ColorRect>($"Pip{i}") is not { } pip)
            {
                continue;
            }

            // EVERY SLOT IS DRAWN, dim past what the buffer holds: the strip
            // is a secondary reading of the number beside it, and a strip that
            // shrank at zero would make an empty meter look like a missing row
            // -- which is exactly what `EB-635` filed.
            pip.Visible = true;
            pip.Color = i < drawn ? PipFull : PipEmpty;
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
        Log.Warn($"[{KleeMod.ModId}] salon panel: no live face art for "
               + $"{what ?? "a member"}; drawing the name and the number "
               + "alone.");
    }
}
