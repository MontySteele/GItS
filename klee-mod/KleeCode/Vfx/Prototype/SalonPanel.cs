using System;
using System.Collections.Generic;
using Godot;
using HarmonyLib;
using KleeMod.Cards;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.addons.mega_text;

namespace KleeMod.Vfx;

/// <summary>
/// THE SALON PANEL: ONE ELEMENT FOR THE WHOLE BOARD (`EB-627`, `EB-628`,
/// `EB-633`, `EB-634`, `EB-635`, `EB-639`, `EB-640`, `EB-641`).
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
/// AND THEN THE WORDS HAD TO FIT IT (`EB-639`, `EB-641`; the placement itself
/// is kept -- "keep this placement and refine the panel"). The first live frame
/// of the panel read "5 Hydro3 Block5 Hydro": the tiers were right, the chips
/// were 70 pixels wide, and nothing had ever measured the strings against the
/// box they were centred in, so neighbouring numbers ran together and the front
/// chip's Evoke line landed on top of the reduced-performance note. Four things
/// change together, and none of them is a new element:
///
///   * THE BOX IS MEASURED. <see cref="ChipContentWidth"/> is the widest thing
///     a chip can ever print, at its own tier, through
///     <see cref="FurinaBoardScale.TextWidth"/>; the chip is that plus padding,
///     the panel is the chips plus their gaps, and at paint time every string
///     is stepped down by <see cref="FurinaBoardScale.FitFontSize"/> until it
///     fits the box it is actually in. A number no arithmetic here bounds --
///     Fanfare feeds the performance without limit -- can therefore never
///     collide with its neighbour.
///   * THE UNIT IS A WORD AND A GLYPH, NEVER "HYDRO" ALONE. "5 Hydro" is not a
///     quantity of anything a player can act on: it reads as five of a
///     substance. A performance deals DAMAGE, so the chip says
///     <see cref="EffectText"/> -- "5 damage" -- and carries the element as the
///     same Hydro glyph every card face wears
///     (<see cref="ElementBadge.IconPathFor"/>, reused rather than re-drawn).
///     The Usher's is "3 Block", which needs no glyph and gets none.
///   * THE HEADER IS TWO SHORT LINES, and the pips are FILLED ONLY. "Encore 1"
///     with one lit pip, then "Fanfare 15 · Bonus +1". An empty pip TRACK
///     behind the lit ones drew a capacity that does not exist -- Encore has no
///     maximum -- so nothing is drawn where there is nothing.
///   * THE FRONT CHIP'S FOOTER SAYS WHAT REPLACING IT PAYS, in the player's own
///     verb: <see cref="ReplaceText"/>, tier 2, on its own row touching the
///     chip. "Evoke" is the rules word and it is on the card that does it; the
///     panel is answering "what happens if I deploy onto a full stage", and the
///     answer is that the front one is replaced.
///
/// Every string on the panel is as short as it can be and still be unambiguous.
/// There are no sentences on it.
///
/// WHY THE SILHOUETTES WENT, and why it was the SECOND time art failed that
/// question. Sprint 1 framed three card-art portraits and they read as "three
/// identical blue smudges"; the D4 rework (2026-07-24,
/// <see cref="SalonVisualsBridge"/>'s header) replaced them with freestanding
/// silhouettes on the theory that outline carries identity where a crop does
/// not, and at combat scale the silhouettes read the same way. What is being
/// asked of the picture -- who is this, and what will it do next -- is not a
/// thing a 30-pixel outline of a crab can answer. So the picture stops
/// carrying the message alone: each member gets its face AND its short name AND
/// its next act in words, and the face is drawn at
/// <see cref="FurinaBoardScale.FaceHeight"/> inside the wider chip so that
/// "seahorse, crab, seahorse" is readable at a glance rather than inferred from
/// the name under it.
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
/// THE NEXT ACT IS THE PERFORMANCE, folded and not printed, and its NUMBER is
/// TIER 1 (<see cref="FurinaBoardScale"/>) because it is the number every play
/// is priced against. It comes from <see cref="SalonMemberPower.TickValue"/> --
/// the same expression the performance resolves through and the same one the
/// member tips fold the Fanfare bonus into -- so a chip cannot disagree with
/// what the member does, and at Encore 0 it is already the dry three-quarters
/// number rather than the wet one.
///
/// AND AT ZERO IT SAYS THE STAGE HAS NOT STOPPED (`EB-633`). The pips count
/// FULL-STRENGTH performances, which is what one <c>TickEncoreCost</c> buys; a
/// member with nothing to spend still performs, at three-quarters. An empty
/// meter therefore must not read as an idle stage, so the panel prints
/// <see cref="ReducedNotice"/> exactly when the buffer cannot pay -- the same
/// condition <see cref="Paid"/> hands the chips, so the note and the numbers
/// cannot disagree -- on a row of its own under everything else.
///
/// FANFARE'S THRESHOLD IS A TOOLTIP, not a line. "+1 at 20" is a footnote to
/// the Fanfare number and was drawn as a second number under a badge the size
/// of the energy orb; on the panel it hangs off the resource header's hover
/// (<see cref="StepText"/>) so the header stays two short lines.
///
/// ABOVE HER, AND CLEAR OF THE BAND THAT IS NOT OURS. The old anchor put the
/// stage at the creature's feet, which is where `NCreatureStateDisplay` draws
/// the HP bar and the block badge, and both rebuilds lost a row to it. The
/// overhead region is the one measured clear space on this rig -- Furina's
/// combat box tops out at -280 (`GaugeBridge`'s own reading) and the Burst
/// slot at -300 is RETIRED under the arm (`EB-365`) -- so the panel sits above
/// that: its bottom edge is the Burst slot and its top is
/// <see cref="AnchorOffset"/>. It is <see cref="PanelWidth"/> wide, centred on
/// her, and that width is now the CONTENT's rather than the creature bounds'
/// 240: a box that cannot hold its own words is not a narrower panel, it is a
/// broken one. She stands in the left third of the screen and the group is one
/// backing rectangle, so the extra width is nowhere near the enemy intent or
/// the targeting lanes and reads as one object wherever it sits.
///
/// AND IT DIES WITH THE FIGHT (`EB-640`). The Evoke that killed the last enemy
/// left the panel drawn, dimmed, behind the Loot dialog -- a stage described
/// for a combat that no longer exists. The room's VFX container survives into
/// the reward screen by design (the creature and her HP bar are still drawn
/// there), so the panel has to take itself down: <see cref="Hide"/> frees it by
/// node name at `NCombatUi.Deactivate`, the hook every other HUD element in
/// this tree uses, and at Furina's own combat-end hooks, which run inside
/// `EndCombatInternal` before the reward screen opens.
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
/// DECISIONS: the scope, the order, the words, the folded number, the counts,
/// the measured fit and the tier every element declares. The look is owed a
/// frame on the next `+proto` deploy.
///
/// QUARANTINED. `Vfx/Prototype/**` is `Compile Remove`d without
/// `-p:PrototypeCards=true`. Revert is the flag.
/// </summary>
public static class SalonPanel
{
    /// <summary>The node this file owns.</summary>
    internal const string RootName = "KleeModSalonPanel";

    /// <summary>Chips the panel will ever draw. Three is the cap and five is
    /// what Box Seats upgraded can reach; a sixth has nowhere to go inside the
    /// box and is logged rather than silently invisible.</summary>
    public const int MaxChips = 5;

    /// <summary>Pips drawn beside the Encore number. The NUMBER is the reading
    /// (`EB-635`) and the pips are the secondary one, so the strip is sized to
    /// the decisions a player is actually making rather than to any runway
    /// they could reach; past it the count carries on in a "+n".</summary>
    public const int MaxPips = 6;

    /// <summary>The word on chip 0. A gold border says "this one is special"
    /// and not WHAT is special about it; this says it.</summary>
    public const string FrontWord = "FRONT";

    /// <summary>What the panel prints when the buffer cannot pay for a
    /// full-strength performance. `EB-633`: an empty meter must not read as an
    /// idle stage.</summary>
    public const string ReducedNotice = "Reduced performance";

    /// <summary>
    /// The widest NUMBER the box is built for: two digits.
    ///
    /// Not a claim that three are unreachable -- Fanfare feeds the performance
    /// and nothing here caps it -- but the design case the box is measured
    /// against. Past it <see cref="FurinaBoardScale.FitFontSize"/> takes the
    /// text down a point rather than the chip taking the panel wider, which is
    /// the trade a player would choose: a slightly smaller 128 beats a panel
    /// that grew a third for one number.
    /// </summary>
    internal const string WidestNumber = "88";

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

    /// <summary>The panel's own ground. Darker and less transparent than the
    /// first draw (`EB-641`: the tiers have to read against a lit forest as
    /// well as a black room), and still translucent so it is a panel rather
    /// than a hole in the scene.</summary>
    private static readonly Color PanelBack = new(0.03f, 0.05f, 0.09f, 0.88f);
    private static readonly Color ChipBack = new(0.09f, 0.15f, 0.24f, 0.92f);
    private static readonly Color EmptyBack = new(0.06f, 0.11f, 0.18f, 0.35f);
    private static readonly Color FootBack = new(0.13f, 0.20f, 0.30f, 0.92f);
    private static readonly Color FrontFrame = new(1f, 0.94f, 0.72f, 0.95f);
    private static readonly Color DryText = new(0.62f, 0.68f, 0.78f);
    private static readonly Color NoticeText = new(1f, 0.78f, 0.42f, 0.98f);
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
    /// "Mademoiselle Crabaletta" and a chip cannot, so the panel prints the
    /// half that is the member's own name and the tip keeps the full one.
    /// Recognition is the job -- the face above it and this word are the two
    /// halves of "who is that".</summary>
    public static string ShortName(SalonMember member) => member switch
    {
        SalonMember.Crabaletta => "Crabaletta",
        SalonMember.Usher => "Usher",
        _ => "Chevalmarin",
    };

    /// <summary>
    /// WHAT THE MEMBER'S NUMBER IS IN.
    ///
    /// `EB-641`. It was the element's name -- "5 Hydro" -- which is not a
    /// quantity a player can price a play against: it reads as five of a
    /// substance rather than as damage that happens to be Hydro. A performance
    /// deals damage or it gains Block, so the unit is one of those two words
    /// and the ELEMENT rides beside it as the glyph
    /// (<see cref="ElementOf"/>), never as a noun.
    /// </summary>
    public static string EffectUnit(SalonMember member) =>
        member == SalonMember.Usher ? "Block" : "damage";

    /// <summary>The element a member's performance carries, or
    /// <c>Element.None</c> for the Usher, whose Block is elementless. The glyph
    /// itself is <see cref="ElementBadge.IconPathFor"/>'s -- the same aura art
    /// every card face wears, so the panel teaches nothing new.</summary>
    public static Element ElementOf(SalonMember member) =>
        member == SalonMember.Usher ? Element.None : Element.Hydro;

    /// <summary>
    /// WHAT THIS MEMBER DOES WHEN IT NEXT PERFORMS, as number and unit.
    ///
    /// The number is <see cref="SalonMemberPower.TickValue"/>, which is where
    /// the Fanfare bonus, Grand Salon and the dry three-quarters all already
    /// live -- so the chip folds the bonus the way the member tips do because
    /// it is the same call, not because it repeats the arithmetic.
    /// </summary>
    public static string EffectNumber(
        Creature owner, SalonMember member, bool paid) =>
        SalonMemberPower.TickValue(owner, member, paid)
            .ToString(System.Globalization.CultureInfo.InvariantCulture);

    /// <summary>The chip's effect line as one string -- the number and its
    /// unit, which is what a player reads off it and what the fit is measured
    /// against. The glyph sits between them on screen.</summary>
    public static string EffectText(
        Creature owner, SalonMember member, bool paid) =>
        $"{EffectNumber(owner, member, paid)} {EffectUnit(member)}";

    /// <summary>
    /// WHAT REPLACING THIS MEMBER PAYS -- the front chip's footer, drawn while
    /// the stage is full, because that is the one board state in which the next
    /// deploy reaches it.
    ///
    /// `EB-641`. It read "Evoke 14 Hydro" in tier 3 under a 70-pixel chip: the
    /// rules verb, at footnote size, in the element-as-noun spelling. The verb
    /// the player is choosing here is REPLACE -- they are deploying onto a full
    /// stage -- so the footer names the price of that in the same units the
    /// chip above uses, at tier 2, on its own row.
    ///
    /// `EB-630`. CHEVALMARIN'S LINE CARRIES HER REFUND: she also grants
    /// <see cref="SalonConstants.ChevalmarinBowEncore"/> Encore, which is the
    /// number that makes replacing her a resource decision rather than a loss.
    /// Interpolated and never typed, on `EB-89`'s rule.
    /// </summary>
    public static string ReplaceText(SalonMember member) => member switch
    {
        SalonMember.Crabaletta =>
            $"Replace: {SalonConstants.CrabalettaBow} damage",
        SalonMember.Usher => $"Replace: {SalonConstants.UsherBow} Block",
        _ => "Replace: Hydro to ALL · "
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
    /// the second half of the header's second line, and the one that says what
    /// the first half is FOR.</summary>
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
    /// LINE 1 of the resource header. Encore leads with its NAME and its
    /// NUMBER (`EB-635`); the lit pips follow it and nothing follows them,
    /// because Encore has no maximum and an empty track behind the lit pips
    /// would draw a capacity that does not exist (`EB-641`).
    /// </summary>
    public static string EncoreText(Creature owner) =>
        $"Encore {FurinaResources.Encore(owner)}";

    /// <summary>
    /// LINE 2: the meter and what it buys, on its own line and as short as it
    /// can be. "Bonus" and not "Member bonus" because the chips it lands on are
    /// six pixels below it; "Fanfare" and not "Fanfare meter" for the same
    /// reason. Two short lines beat one long one at combat scale, which is the
    /// whole of `EB-641`'s point 3.
    /// </summary>
    public static string MeterText(Creature owner) =>
        $"Fanfare {Fanfare(owner)} · Bonus +{MemberBonus(owner)}";

    /// <summary>The threshold, which is a FOOTNOTE to the Fanfare number and
    /// hangs off the header's hover rather than sitting on it.</summary>
    public static string StepText(Creature owner) =>
        $"+1 at {NextThreshold(owner)}";

    /// <summary>Pips the strip cannot draw, as a "+n" beside it. The number on
    /// line 1 is the truth; this keeps the STRIP from quietly claiming to be
    /// it.</summary>
    public static string OverflowText(Creature owner)
    {
        var over = Pips(owner) - MaxPips;
        return over > 0
            ? $"+{over.ToString(System.Globalization.CultureInfo.InvariantCulture)}"
            : string.Empty;
    }

    // ------------------------------------------------------- the measured box --

    /// <summary>
    /// The widest thing a chip can ever print, at its own tier.
    ///
    /// EVERY REACHABLE STRING, not a sample of them: each member's name at tier
    /// 2, each member's effect row at tier 1 plus glyph plus tier 2 for the
    /// two-digit design case, and the FRONT word at tier 3. This is the whole
    /// of `EB-639`'s "the fit is computed, not assumed" in the horizontal
    /// direction; the vertical half is that every row in
    /// <see cref="FurinaBoardScale"/> has its own Y.
    /// </summary>
    public static readonly float ChipContentWidth = WidestChipContent();

    /// <summary>The widest Replace footer, measured the same way.</summary>
    public static readonly float FooterContentWidth = WidestFooter();

    /// <summary>
    /// The panel's box, measured from the two above for the stage a Furina
    /// actually stands on (<see cref="SalonConstants.MemberSlots"/>). Fixed for
    /// the run, so the anchor below is fixed too: a raised cap tiles narrower
    /// chips into the same box rather than moving the panel out from under the
    /// player mid-combat.
    /// </summary>
    public static readonly float PanelWidth = FurinaBoardScale.PanelWidthFor(
        SalonConstants.MemberSlots, ChipContentWidth, FooterContentWidth);

    /// <summary>
    /// The panel's top-left, relative to Furina's creature origin.
    ///
    /// ABOVE THE RIG AND ABOVE THE RETIRED BURST SLOT. `GaugeBridge` measured
    /// Furina's combat box as topping out at -280 and put the cross-character
    /// Burst slot at -300; under this arm that slot draws nothing (`EB-365`),
    /// so the panel's BOTTOM edge is -300 and its top is that less
    /// <see cref="FurinaBoardScale.PanelHeight"/>. Centred on her.
    /// </summary>
    internal static readonly Vector2 AnchorOffset =
        new(-PanelWidth / 2f, -300f - FurinaBoardScale.PanelHeight);

    private static float WidestChipContent()
    {
        var widest = FurinaBoardScale.TextWidth(
            FrontWord, FurinaBoardScale.Tier3FontSize);

        foreach (SalonMember member in Enum.GetValues(typeof(SalonMember)))
        {
            widest = Math.Max(widest, FurinaBoardScale.TextWidth(
                ShortName(member), FurinaBoardScale.Tier2FontSize));
            widest = Math.Max(widest, EffectRowWidth(
                WidestNumber, member,
                FurinaBoardScale.Tier1FontSize,
                FurinaBoardScale.Tier2FontSize));
        }

        return widest;
    }

    private static float WidestFooter()
    {
        var widest = 0f;
        foreach (SalonMember member in Enum.GetValues(typeof(SalonMember)))
        {
            widest = Math.Max(widest, FurinaBoardScale.TextWidth(
                ReplaceText(member), FurinaBoardScale.Tier2FontSize));
        }

        return widest;
    }

    /// <summary>
    /// The effect row's width: the number, the glyph the element gets, and the
    /// unit -- at the two sizes they are drawn at. One expression, used by the
    /// measurement above and by the paint below, so the box and the drawing
    /// cannot disagree about how wide the row is.
    /// </summary>
    public static float EffectRowWidth(
        string number, SalonMember member, int numberSize, int unitSize)
    {
        var width = FurinaBoardScale.TextWidth(number, numberSize)
                  + FurinaBoardScale.IconGap
                  + FurinaBoardScale.TextWidth(EffectUnit(member), unitSize);

        if (ElementOf(member) != Element.None)
        {
            width += unitSize + FurinaBoardScale.IconGap;
        }

        return width;
    }

    /// <summary>
    /// The two sizes the effect row is actually drawn at inside a chip
    /// <paramref name="inner"/> pixels wide: tier 1 and tier 2 where they fit,
    /// stepped down TOGETHER where they do not.
    ///
    /// Together, because the tiers are a hierarchy and shrinking one half alone
    /// would end with a unit as large as the number it qualifies. This is the
    /// expression the paint uses and the one the fit pin measures, so what is
    /// drawn and what is pinned cannot be two different answers.
    /// </summary>
    public static (int Number, int Unit) EffectSizes(
        string number, SalonMember member, float inner)
    {
        var numberSize = FurinaBoardScale.Tier1FontSize;
        var unitSize = FurinaBoardScale.Tier2FontSize;

        while (numberSize > 1 && unitSize > 1
               && EffectRowWidth(number, member, numberSize, unitSize) > inner)
        {
            numberSize--;
            unitSize = Math.Max(1, unitSize - 1);
        }

        return (numberSize, unitSize);
    }

    /// <summary>The inner width one chip offers its text on a stage of
    /// <paramref name="slots"/>: the measured chip width, or the share of the
    /// box a raised cap leaves it, less the padding on both sides.</summary>
    public static float ChipInnerWidth(int slots) =>
        FurinaBoardScale.ChipWidthFor(PanelWidth, slots, ChipContentWidth)
        - 2f * FurinaBoardScale.ChipPad;

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

    /// <summary>
    /// FREE THE PANEL WHEN THE FIGHT IS OVER (`EB-640`).
    ///
    /// BY NODE, NOT BY SEAT, <see cref="SparkCounter.Hide"/>'s idiom and for
    /// its reason: the teardown hooks run while the NEXT room is being built
    /// and the combat we still hold may have no seats in it (`EB-225`), so a
    /// teardown that has to resolve a seat is a teardown that can throw out of
    /// `_Ready`. This one asks the live room's VFX container for a child THIS
    /// file named and frees it; the registry's <c>IsInstanceValid</c> staleness
    /// then answers null for it, and <see cref="Setup"/> discards anything left
    /// over at the next combat.
    /// </summary>
    internal static void Hide()
    {
        try
        {
            if (NCombatRoom.Instance is not { } room) return;
            if (room.CombatVfxContainer is not { } container) return;
            if (!GodotObject.IsInstanceValid(container)) return;

            if (container.FindChild(RootName, recursive: true, owned: false)
                is { } node && GodotObject.IsInstanceValid(node))
            {
                node.QueueFree();
            }
        }
        catch (Exception e)
        {
            // A teardown runs on the way out of a combat, and the room it is
            // asking about may be half-built or half-gone. Losing the free
            // costs a stale panel until the next `Setup` discards it; throwing
            // here costs the run.
            Log.Warn($"[{KleeMod.ModId}] salon panel: the teardown could not "
                   + $"reach the room ({e.GetType().Name}: {e.Message}).");
        }
    }

    // ---------------------------------------------------------- the tree --

    private static Node2D Build(int? energyOrbFontSize)
    {
        var root = new Node2D { Name = RootName };

        // THE BACKING RECTANGLE, and it is why this is a panel rather than
        // four widgets: everything about the Salon is inside it, and it gives
        // the tiers a constant ground to read against on any background. Sized
        // to the content (`EB-641`), which is what the two measurements above
        // are for.
        root.AddChildSafely(new ColorRect
        {
            Name = "Back",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Position = Vector2.Zero,
            Size = new Vector2(PanelWidth, FurinaBoardScale.PanelHeight),
            Color = PanelBack,
            ZIndex = -2,
        });

        root.AddChildSafely(BuildResourceRows(energyOrbFontSize));

        for (var i = 0; i < MaxChips; i++)
        {
            root.AddChildSafely(BuildChip(i));
        }

        root.AddChildSafely(BuildFooter());

        // `EB-633`: the note that an empty meter is not an idle stage, on its
        // own row under everything else so it cannot land on the footer the way
        // `EB-639`'s frame showed it landing on the Evoke line.
        var notice = Text("Notice", FurinaBoardScale.Tier3FontSize,
            new Vector2(FurinaBoardScale.PanelPad,
                        FurinaBoardScale.NoticeRowY),
            PanelWidth - 2f * FurinaBoardScale.PanelPad,
            FurinaBoardScale.NoticeRowHeight);
        notice.Visible = false;
        root.AddChildSafely(notice);

        return root;
    }

    private static Control BuildResourceRows(int? energyOrbFontSize)
    {
        // TIER 2, AND UNDER THE ENERGY ORB'S NUMBER (`EB-634`). The clamp is
        // live rather than asserted: the orb's own size is read off the scene
        // where the scene will give it up, and the documented fallback stands
        // where it will not.
        var size = FurinaBoardScale.ResourceFontSize(energyOrbFontSize);
        var inner = PanelWidth - 2f * FurinaBoardScale.PanelPad;

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
            Size = new Vector2(
                PanelWidth,
                FurinaBoardScale.MeterRowY + FurinaBoardScale.MeterRowHeight
                    - FurinaBoardScale.ResourceRowY),
        };

        // LINE 1: the word, the number, then the lit pips beside them.
        var encore = Text("Encore", size,
            new Vector2(FurinaBoardScale.PanelPad, 0f),
            inner, FurinaBoardScale.ResourceRowHeight);
        encore.HorizontalAlignment = HorizontalAlignment.Left;
        row.AddChildSafely(encore);

        var pips = new Control
        {
            Name = "Pips",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            Position = new Vector2(FurinaBoardScale.PanelPad, 3f),
            Size = new Vector2(
                MaxPips * (FurinaBoardScale.PipWidth + FurinaBoardScale.PipGap),
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
                Color = PipFull,
            });
        }
        row.AddChildSafely(pips);

        var overflow = Text("Overflow", FurinaBoardScale.Tier3FontSize,
            new Vector2(FurinaBoardScale.PanelPad, 2f),
            inner, FurinaBoardScale.PipHeight);
        overflow.HorizontalAlignment = HorizontalAlignment.Left;
        overflow.Visible = false;
        row.AddChildSafely(overflow);

        // LINE 2: the meter and what it buys.
        var meters = Text("Meters", size,
            new Vector2(FurinaBoardScale.PanelPad,
                        FurinaBoardScale.MeterRowY
                            - FurinaBoardScale.ResourceRowY),
            inner, FurinaBoardScale.MeterRowHeight);
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
            Size = new Vector2(ChipContentWidth + 2f * FurinaBoardScale.ChipPad,
                               FurinaBoardScale.ChipHeight),
            Visible = false,
        };

        chip.AddChildSafely(new ColorRect
        {
            Name = "Back",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Position = Vector2.Zero,
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
        });

        // TIER 2: who this is.
        chip.AddChildSafely(Text("Name", FurinaBoardScale.Tier2FontSize,
            Vector2.Zero, 0f, FurinaBoardScale.NameRowHeight));
        // TIER 1: the number a play is priced against, with TIER 2 for the
        // unit it is in and the element's own glyph between them.
        chip.AddChildSafely(Text("ActNumber", FurinaBoardScale.Tier1FontSize,
            Vector2.Zero, 0f, FurinaBoardScale.ActRowHeight));
        chip.AddChildSafely(new TextureRect
        {
            Name = "ActIcon",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
            Visible = false,
        });
        chip.AddChildSafely(Text("ActUnit", FurinaBoardScale.Tier2FontSize,
            Vector2.Zero, 0f, FurinaBoardScale.ActRowHeight));
        // TIER 3: the qualifier, on its own row.
        chip.AddChildSafely(Text("Front", FurinaBoardScale.Tier3FontSize,
            Vector2.Zero, 0f, FurinaBoardScale.FrontRowHeight));

        return chip;
    }

    private static Control BuildFooter()
    {
        var footer = new Control
        {
            Name = "Footer",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            FocusMode = Control.FocusModeEnum.None,
            Position = new Vector2(FurinaBoardScale.PanelPad,
                                   FurinaBoardScale.FooterRowY),
            Size = new Vector2(PanelWidth - 2f * FurinaBoardScale.PanelPad,
                               FurinaBoardScale.FooterRowHeight),
            Visible = false,
        };

        // Its own ground, touching the front chip's bottom edge: that is what
        // "visually attached to the front chip" is in pixels.
        footer.AddChildSafely(new ColorRect
        {
            Name = "Back",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Position = Vector2.Zero,
            Color = FootBack,
        });

        var text = Text("Text", FurinaBoardScale.Tier2FontSize,
            new Vector2(FurinaBoardScale.ChipPad, 0f),
            0f, FurinaBoardScale.FooterRowHeight);
        text.HorizontalAlignment = HorizontalAlignment.Left;
        footer.AddChildSafely(text);

        return footer;
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

        // THE FIT, EVERY PAINT. The chip is as wide as the box allows for the
        // stage actually on screen, and every string inside it is stepped down
        // to that width -- so a raised cap or a three-digit performance costs a
        // font point, never a collision.
        var chipWidth = FurinaBoardScale.ChipWidthFor(
            PanelWidth, slots, ChipContentWidth);
        var group = slots * chipWidth + (slots - 1) * FurinaBoardScale.ChipGap;
        var left = (PanelWidth - group) / 2f;

        for (var i = 0; i < MaxChips; i++)
        {
            if (root.GetNodeOrNull<Control>($"Chip{i}") is not { } chip)
            {
                continue;
            }

            chip.Visible = i < slots;
            if (i >= slots) continue;

            chip.Position = new Vector2(
                left + i * (chipWidth + FurinaBoardScale.ChipGap),
                FurinaBoardScale.ChipsRowY);
            chip.Size = new Vector2(chipWidth, FurinaBoardScale.ChipHeight);
            PaintChip(chip, owner, i < company.Count ? company[i] : null,
                      chipWidth, paid, front: i == 0, full: full);
        }

        PaintFooter(root, company.Count > 0 ? company[0] : null,
                    left, chipWidth, full);
        PaintResources(root, owner, paid);
    }

    private static void PaintChip(
        Control chip, Creature owner, SalonMember? member, float width,
        bool paid, bool front, bool full)
    {
        var occupied = member is { } _;

        if (chip.GetNodeOrNull<ColorRect>("Back") is { } back)
        {
            back.Size = new Vector2(width, FurinaBoardScale.ChipHeight);
            back.Color = occupied ? ChipBack : EmptyBack;
        }

        // An EMPTY chip is drawn dim rather than hidden: the panel's width is
        // the cap, and a stage of one that renders as one chip tells the
        // player nothing about the two seats they still have.
        if (chip.GetNodeOrNull<ColorRect>("Frame") is { } frame)
        {
            frame.Size = new Vector2(width + 4f,
                                     FurinaBoardScale.ChipHeight + 4f);
            frame.Visible = occupied && front;
            frame.Color = FrontFrame;
        }

        var inner = width - 2f * FurinaBoardScale.ChipPad;
        var face = chip.GetNodeOrNull<TextureRect>("Face");
        var name = chip.GetNodeOrNull<Label>("Name");
        var number = chip.GetNodeOrNull<Label>("ActNumber");
        var icon = chip.GetNodeOrNull<TextureRect>("ActIcon");
        var unit = chip.GetNodeOrNull<Label>("ActUnit");
        var frontLabel = chip.GetNodeOrNull<Label>("Front");

        if (face != null)
        {
            face.Position = new Vector2(0f, 1f);
            face.Size = new Vector2(width, FurinaBoardScale.FaceHeight);
        }

        if (name != null)
        {
            name.Position = new Vector2(
                FurinaBoardScale.ChipPad, FurinaBoardScale.FaceHeight + 2f);
            name.Size = new Vector2(inner, FurinaBoardScale.NameRowHeight);
        }

        if (frontLabel != null)
        {
            frontLabel.Position = new Vector2(
                FurinaBoardScale.ChipPad,
                FurinaBoardScale.FaceHeight + 2f
                    + FurinaBoardScale.NameRowHeight
                    + FurinaBoardScale.ActRowHeight);
            frontLabel.Size = new Vector2(
                inner, FurinaBoardScale.FrontRowHeight);
        }

        if (member is not { } who)
        {
            if (face != null) face.Visible = false;
            if (name != null)
            {
                name.Visible = true;
                name.Text = "—";
                name.AddThemeColorOverride(
                    ThemeConstants.Label.FontColor, PipEmpty);
            }
            if (number != null) number.Visible = false;
            if (icon != null) icon.Visible = false;
            if (unit != null) unit.Visible = false;
            if (frontLabel != null) frontLabel.Visible = false;
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
            Sized(name, FurinaBoardScale.FitFontSize(
                name.Text, FurinaBoardScale.Tier2FontSize, inner));
            name.AddThemeColorOverride(
                ThemeConstants.Label.FontColor, paid ? accent : DryText);
        }

        PaintEffect(chip, owner, who, inner, paid, number, icon, unit);

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
    }

    /// <summary>
    /// The number, the glyph and the unit, laid out as ONE centred row from
    /// their own measured widths -- the same expression
    /// <see cref="EffectRowWidth"/> sized the box with, so what is drawn and
    /// what was measured cannot drift apart.
    /// </summary>
    private static void PaintEffect(
        Control chip, Creature owner, SalonMember who, float inner, bool paid,
        Label? number, TextureRect? icon, Label? unit)
    {
        var digits = EffectNumber(owner, who, paid);
        var word = EffectUnit(who);
        var element = ElementOf(who);

        // The fit, in the one expression the pin measures.
        var (numberSize, unitSize) = EffectSizes(digits, who, inner);

        var numberWidth = FurinaBoardScale.TextWidth(digits, numberSize);
        var unitWidth = FurinaBoardScale.TextWidth(word, unitSize);
        var iconSide = element == Element.None ? 0f : unitSize;
        var rowWidth = EffectRowWidth(digits, who, numberSize, unitSize);
        var x = FurinaBoardScale.ChipPad + Math.Max(0f, (inner - rowWidth) / 2f);
        var y = FurinaBoardScale.FaceHeight + 2f
              + FurinaBoardScale.NameRowHeight;

        if (number != null)
        {
            number.Visible = true;
            number.Text = digits;
            Sized(number, numberSize);
            number.Position = new Vector2(x, y);
            number.Size = new Vector2(
                numberWidth, FurinaBoardScale.ActRowHeight);
            number.AddThemeColorOverride(
                ThemeConstants.Label.FontColor,
                paid ? StsColors.cream : DryText);
        }

        x += numberWidth + FurinaBoardScale.IconGap;

        if (icon != null)
        {
            icon.Visible = false;
            if (element != Element.None)
            {
                SetIcon(icon, element);
                icon.Position = new Vector2(
                    x,
                    y + (FurinaBoardScale.ActRowHeight - iconSide) / 2f);
                icon.Size = new Vector2(iconSide, iconSide);
            }
        }

        if (element != Element.None)
        {
            x += iconSide + FurinaBoardScale.IconGap;
        }

        if (unit != null)
        {
            unit.Visible = true;
            unit.Text = word;
            Sized(unit, unitSize);
            unit.Position = new Vector2(x, y);
            unit.Size = new Vector2(unitWidth, FurinaBoardScale.ActRowHeight);
            unit.AddThemeColorOverride(
                ThemeConstants.Label.FontColor,
                paid ? StsColors.cream : DryText);
        }
    }

    private static void PaintFooter(
        Node2D root, SalonMember? front, float left, float chipWidth, bool full)
    {
        if (root.GetNodeOrNull<Control>("Footer") is not { } footer) return;

        // Only the front, and only on a full stage: that is the one board state
        // in which a deploy replaces this member.
        footer.Visible = full && front is { };
        if (front is not { } who || !full) return;

        var text = ReplaceText(who);
        var available = PanelWidth - FurinaBoardScale.PanelPad - left
                      - 2f * FurinaBoardScale.ChipPad;
        var size = FurinaBoardScale.FitFontSize(
            text, FurinaBoardScale.Tier2FontSize, available);
        var width = Math.Max(
            chipWidth,
            FurinaBoardScale.TextWidth(text, size)
                + 2f * FurinaBoardScale.ChipPad);

        footer.Position = new Vector2(left, FurinaBoardScale.FooterRowY);
        footer.Size = new Vector2(width, FurinaBoardScale.FooterRowHeight);

        if (footer.GetNodeOrNull<ColorRect>("Back") is { } back)
        {
            back.Size = new Vector2(width, FurinaBoardScale.FooterRowHeight);
        }

        if (footer.GetNodeOrNull<Label>("Text") is { } label)
        {
            label.Text = text;
            Sized(label, size);
            label.Position = new Vector2(FurinaBoardScale.ChipPad, 0f);
            label.Size = new Vector2(width - 2f * FurinaBoardScale.ChipPad,
                                     FurinaBoardScale.FooterRowHeight);
            label.AddThemeColorOverride(
                ThemeConstants.Label.FontColor, StsColors.cream);
        }
    }

    private static void PaintResources(Node2D root, Creature owner, bool paid)
    {
        if (root.GetNodeOrNull<Control>("Resources") is { } row)
        {
            var size = FurinaBoardScale.Tier2FontSize;

            if (row.GetNodeOrNull<Label>("Encore") is { } encore)
            {
                encore.Text = EncoreText(owner);
                size = encore.GetThemeFontSize(ThemeConstants.Label.FontSize);
                encore.AddThemeColorOverride(
                    ThemeConstants.Label.FontColor,
                    paid ? StsColors.cream : DryText);
                PaintPips(row, owner,
                          FurinaBoardScale.PanelPad
                          + FurinaBoardScale.TextWidth(encore.Text, size)
                          + FurinaBoardScale.PipStripGap);
            }

            if (row.GetNodeOrNull<Label>("Meters") is { } meters)
            {
                meters.Text = MeterText(owner);
                meters.AddThemeColorOverride(
                    ThemeConstants.Label.FontColor, StsColors.cream);
            }

            // The threshold is a FOOTNOTE and hangs off the hover, so the
            // header stays two short lines.
            row.TooltipText = StepText(owner);
        }

        if (root.GetNodeOrNull<Label>("Notice") is { } notice)
        {
            notice.Visible = !paid;
            notice.Text = ReducedNotice;
            notice.AddThemeColorOverride(
                ThemeConstants.Label.FontColor, NoticeText);
        }
    }

    private static void PaintPips(Control row, Creature owner, float x)
    {
        if (row.GetNodeOrNull<Control>("Pips") is not { } strip) return;

        var drawn = Math.Min(Pips(owner), MaxPips);
        strip.Position = new Vector2(x, 3f);

        for (var i = 0; i < MaxPips; i++)
        {
            if (strip.GetNodeOrNull<ColorRect>($"Pip{i}") is not { } pip)
            {
                continue;
            }

            // FILLED ONLY (`EB-641`). The old strip drew all six slots and dimmed
            // the ones the buffer could not pay for, which draws a MAXIMUM:
            // Encore has none, and a track that is mostly empty at 1 says the
            // player is nearly out of something they are not. Nothing is drawn
            // where there is nothing, and the number beside it is the reading
            // either way.
            pip.Visible = i < drawn;
            pip.Color = PipFull;
        }

        if (row.GetNodeOrNull<Label>("Overflow") is { } overflow)
        {
            overflow.Text = OverflowText(owner);
            overflow.Visible = overflow.Text.Length > 0;
            overflow.Position = new Vector2(
                x + drawn * (FurinaBoardScale.PipWidth
                             + FurinaBoardScale.PipGap)
                  + FurinaBoardScale.PipGap,
                2f);
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
        var relative = Faces.TryGetValue(member, out var r) ? r : null;
        face.Visible = Load(face, relative, member.ToString());
    }

    /// <summary>The element's glyph, the SAME art a card face wears
    /// (<see cref="ElementBadge.IconPathFor"/>) -- so "damage" and the element
    /// it is in are one reading the player has already learned. Resolved fresh
    /// for `EB-222`'s reason, like the face above it.</summary>
    private static void SetIcon(TextureRect icon, Element element)
    {
        icon.Visible = Load(
            icon, ElementBadge.IconPathFor(element), element.ToString());
    }

    private static bool Load(TextureRect into, string? relative, string what)
    {
        try
        {
            var path = relative == null ? null : KleePck.Path(relative);
            var texture = path == null
                ? null
                : ResourceLoader.Load<Texture2D>(path);

            if (texture == null || !GodotObject.IsInstanceValid(texture))
            {
                Warn(relative ?? what);
                return false;
            }

            into.Texture = texture;
            return true;
        }
        catch (Exception e)
        {
            Warn($"{what} ({e.GetType().Name}: {e.Message})");
            return false;
        }
    }

    private static void Warn(string? what)
    {
        if (_warnedFace) return;
        _warnedFace = true;
        Log.Warn($"[{KleeMod.ModId}] salon panel: no live art for "
               + $"{what ?? "a member"}; drawing the name and the number "
               + "alone.");
    }
}

/// <summary>The panel dies with the combat, on the game's own hook -- one
/// teardown per HUD element, the shape every other element in this tree takes
/// (`EB-640`). The Salon stage's door BUILDS it and never closed it, so a
/// lethal Evoke left it drawn behind the Loot dialog.</summary>
// lint: no-seat: pure static teardown. It frees, by name, the one node this
// file added to the room's vfx container, and touches no run state, no player
// and no creature -- so there is no seat to resolve and no character to scope
// to. The scope lives at the only door that BUILDS the node
// (`SalonVisualsBridge.Setup` through `SalonPanel.AppliesTo`); naming a seat
// here is exactly what `EB-225` shows a teardown must not have to do, since
// `NCombatUi.Deactivate` runs while the next room is still being built.
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Deactivate))]
internal static class NCombatUi_Deactivate_SalonPanel_Patch
{
    [HarmonyPostfix]
    public static void Postfix() => SalonPanel.Hide();
}
