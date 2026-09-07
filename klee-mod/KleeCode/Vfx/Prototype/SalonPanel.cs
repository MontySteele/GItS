using System;
using System.Collections.Generic;
using Godot;
using HarmonyLib;
using KleeMod.Cards;
using KleeMod.Cards.Furina;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Multiplayer.Game.PeerInput;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.addons.mega_text;

namespace KleeMod.Vfx;

/// <summary>
/// THE SALON PANEL: ONE ELEMENT FOR THE WHOLE BOARD (`EB-627`, `EB-628`,
/// `EB-633`, `EB-634`, `EB-635`, `EB-639`, `EB-640`, `EB-641`, `EB-637`,
/// `EB-644`).
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
/// AND THEN THE WORDS HAD TO FIT IT (`EB-639`, `EB-641`). The first live frame
/// of the panel read "5 Hydro3 Block5 Hydro": the tiers were right, the chips
/// were 70 pixels wide, and nothing had ever measured the strings against the
/// box they were centred in. So the box is measured
/// (<see cref="ChipContentWidth"/> through <see cref="FurinaBoardScale.TextWidth"/>),
/// the unit is a word and a glyph ("5 damage" with the card faces' Hydro
/// glyph, never "5 Hydro"), the header is two short lines with FILLED pips
/// only, and the front chip's footer says what replacing it pays in the
/// player's own verb.
///
/// AND THEN IT HAD TO BE ONE THING (`EB-644`, the fourth pass). GPT's review
/// of the third pass's frames: "readable enough to understand, but still
/// looks like several widgets assembled together. The header floats above the
/// member backgrounds, the replacement text sits on a separate strip, and
/// 'Reduced performance' hangs underneath." Every complaint there is a row
/// with its own ground, its own inset or its own width. So:
///
///   * ONE GROUND, ONE INSET, ONE GAP. The header, the chips and the footer
///     all start at <see cref="FurinaBoardScale.PanelPad"/>, are separated by
///     the same <see cref="FurinaBoardScale.RowGap"/> with a hairline in it,
///     and stand on the panel's own backing: the footer has no strip of its
///     own any more, and nothing hangs under anything.
///   * THE SLOT ROW IS THE BOX. <see cref="PanelWidth"/> is the chips and
///     their gaps and nothing else, so it cannot move when a message changes;
///     every header and footer string is measured against that width at its
///     own tier and would be SHORTENED at design time rather than widen the
///     panel (<see cref="InnerWidth"/>, pinned string by string).
///   * THE CONDITION SITS BESIDE ITS CAUSE. "Encore 0 · Reduced" on the
///     Encore line (<see cref="EncoreText"/>), in the reduced tint, instead of
///     a note on a row of its own.
///   * ONE CONTEXTUAL FOOTER, always a row: the front member's replacement
///     price when the stage is full, dim until a Deploy card is under the
///     cursor and bright while one is (<see cref="FooterText"/>).
///   * THE CARD UNDER THE CURSOR MOVES THE PANEL (`EB-637`). A Companion in
///     hand turns the front chip's word from FRONT to PERFORMS; a Deploy on a
///     full stage turns it to LEAVES and lights the footer; a Deploy on a stage
///     with room writes ENTERS on the seat it will fill; the Spotlight tints
///     the pips it would spend. FRONT named a position and not a trigger, so
///     the trigger is now shown by the card that pulls it, and the front chip's
///     own hover says it in words (<see cref="FrontTip"/>). The signal is the
///     game's own: <c>HoveredModelTracker</c> is told every hand hover, every
///     drag and every release by <c>NPlayerHand</c>, and the four postfixes at
///     the foot of this file read it.
///   * THE FANFARE FOOTNOTE SAYS WHAT IT PROMISES. "+1 at 10" beside a
///     Fanfare of 13 read either as the bonus already held or as the next
///     one; <see cref="StepText"/> now names the bonus the NEXT threshold
///     buys ("Bonus +2 at 20"), and the line itself says the one held.
///
/// Every string on the panel is as short as it can be and still be
/// unambiguous. There are no sentences on it.
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
/// <see cref="FurinaBoardScale.FaceHeight"/> inside the wider chip.
///
/// SLOT-INDEX-KEYED, Funnel Contract sec.1, unchanged and for its original
/// reason: deploy is by card and duplicates are legal, so chip i renders
/// whatever <see cref="SalonMemberPower.CompanyOf"/> reports at index i and
/// three Ushers render as three visibly separate Ushers. Nothing here may
/// assume distinct members or a fixed member-to-slot mapping.
///
/// THE NEXT ACT IS THE PERFORMANCE, folded and not printed, and its NUMBER is
/// TIER 1 (<see cref="FurinaBoardScale"/>) because it is the number every play
/// is priced against. It comes from <see cref="SalonMemberPower.TickValue"/> --
/// the same expression the performance resolves through and the same one the
/// member tips fold the Fanfare bonus into -- so a chip cannot disagree with
/// what the member does, and at Encore 0 it is already the dry three-quarters
/// number rather than the wet one (`EB-633`: an empty meter is a reduced
/// stage, never a stopped one, and the Encore line says so).
///
/// ABOVE HER, AND CLEAR OF THE BAND THAT IS NOT OURS. The old anchor put the
/// stage at the creature's feet, which is where `NCreatureStateDisplay` draws
/// the HP bar and the block badge, and both rebuilds lost a row to it. The
/// overhead region is the one measured clear space on this rig -- Furina's
/// combat box tops out at -280 (`GaugeBridge`'s own reading) and the Burst
/// slot at -300 is RETIRED under the arm (`EB-365`) -- so the panel sits above
/// that: its bottom edge is the Burst slot and its top is
/// <see cref="AnchorOffset"/>. Centred on her; she stands in the left third of
/// the screen and the group is one backing rectangle, so the width is nowhere
/// near the enemy intent or the targeting lanes.
///
/// AND IT DIES WITH THE FIGHT (`EB-640`). The room's VFX container survives
/// into the reward screen by design, so the panel takes itself down:
/// <see cref="Hide"/> frees it by node name at `NCombatUi.Deactivate` and at
/// Furina's own combat-end hooks, which run inside `EndCombatInternal` before
/// the reward screen opens.
///
/// BUILT IN CODE, NOT IN A SCENE: an arm-only element that cannot be drawn
/// without a pck rebuild is an element the next `+proto` deploy might silently
/// not have. The member ART is the pck's, reused verbatim from
/// <see cref="SalonVisualsBridge"/>'s own table -- a missing texture degrades
/// to name-and-number, never to nothing.
///
/// WHAT NOTHING HEADLESS CAN ANSWER. Whether the panel reads at combat scale
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

    /// <summary>The word on chip 0 when no card is under the cursor. A gold
    /// border says "this one is special" and not WHAT is special about it;
    /// this says where it stands, and the hover words below say what happens
    /// to it.</summary>
    public const string FrontWord = "FRONT";

    /// <summary>Chip 0's word while a Companion card is hovered: the trigger
    /// FRONT only named the position of (`EB-637`).</summary>
    public const string PerformsWord = "PERFORMS";

    /// <summary>A chip's word while a Deploy is hovered and the stage is
    /// full: this member is replaced.</summary>
    public const string LeavesWord = "LEAVES";

    /// <summary>An empty chip's word while a Deploy is hovered and the stage
    /// has room: the member the card fields sits here.</summary>
    public const string EntersWord = "ENTERS";

    /// <summary>The front chip's own hover line, the rule in words for a
    /// player who has not yet picked up a Companion card.</summary>
    public const string FrontTip = "Performs when you play a Companion";

    /// <summary>The word beside the Encore number when the buffer cannot pay
    /// for a full-strength performance. `EB-633`: an empty meter must not read
    /// as an idle stage; `EB-644`: the condition sits beside its cause.</summary>
    public const string ReducedWord = "Reduced";

    /// <summary>
    /// The widest NUMBER the box is built for: two digits.
    ///
    /// Not a claim that three are unreachable -- Fanfare feeds the performance
    /// and nothing here caps it -- but the design case the box is measured
    /// against. Past it <see cref="FurinaBoardScale.FitFontSize"/> takes the
    /// text down a point rather than the chip taking the panel wider.
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
    /// than re-cut.</summary>
    private static readonly Dictionary<SalonMember, string> Faces = new()
    {
        [SalonMember.Usher] = "furina/salon/member_usher.png",
        [SalonMember.Chevalmarin] = "furina/salon/member_chevalmarin.png",
        [SalonMember.Crabaletta] = "furina/salon/member_crabaletta.png",
    };

    /// <summary>The panel's own ground, and the ONLY ground (`EB-644`): the
    /// header and the footer stand on it directly. Dark and nearly opaque
    /// (`EB-641`: the tiers have to read against a lit forest as well as a
    /// black room), and still translucent so it is a panel rather than a hole
    /// in the scene.</summary>
    private static readonly Color PanelBack = new(0.03f, 0.05f, 0.09f, 0.88f);
    private static readonly Color ChipBack = new(0.09f, 0.15f, 0.24f, 0.92f);
    private static readonly Color EmptyBack = new(0.06f, 0.11f, 0.18f, 0.35f);
    private static readonly Color HoverBack = new(0.16f, 0.27f, 0.42f, 0.95f);
    private static readonly Color Rule = new(0.42f, 0.52f, 0.66f, 0.45f);
    private static readonly Color FrontFrame = new(1f, 0.94f, 0.72f, 0.95f);
    private static readonly Color HoverFrame = new(1f, 1f, 1f, 1f);
    private static readonly Color DryText = new(0.62f, 0.68f, 0.78f);
    private static readonly Color ReducedText = new(1f, 0.78f, 0.42f, 0.98f);
    private static readonly Color PipFull = new(0.42f, 0.83f, 1f, 0.95f);
    private static readonly Color PipSpend = new(1f, 0.78f, 0.42f, 0.98f);
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
    /// half that is the member's own name and the tip keeps the full one.</summary>
    public static string ShortName(SalonMember member) => member switch
    {
        SalonMember.Crabaletta => "Crabaletta",
        SalonMember.Usher => "Usher",
        _ => "Chevalmarin",
    };

    /// <summary>
    /// WHAT THE MEMBER'S NUMBER IS IN (`EB-641`). "5 Hydro" is not a quantity
    /// a player can price a play against; a performance deals damage or it
    /// gains Block, so the unit is one of those two words and the ELEMENT
    /// rides beside it as the glyph (<see cref="ElementOf"/>), never as a
    /// noun.
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
    /// WHAT THIS MEMBER DOES WHEN IT NEXT PERFORMS, as a number. It is
    /// <see cref="SalonMemberPower.TickValue"/>, where the Fanfare bonus, Grand
    /// Salon and the dry three-quarters all already live -- so the chip folds
    /// the bonus the way the member tips do because it is the same call.
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
    /// WHAT REPLACING THIS MEMBER PAYS -- the footer while the stage is full,
    /// because that is the one board state in which the next deploy reaches
    /// it. The verb the player is choosing is REPLACE; the price is in the
    /// same units the chip above uses. `EB-630`: Chevalmarin's line carries
    /// her refund, the number that makes replacing her a resource decision
    /// rather than a loss; interpolated and never typed, on `EB-89`'s rule.
    /// </summary>
    public static string ReplaceText(SalonMember member) => member switch
    {
        SalonMember.Crabaletta =>
            $"Replace: {SalonConstants.CrabalettaBow} damage",
        SalonMember.Usher => $"Replace: {SalonConstants.UsherBow} Block",
        _ => "Replace: Hydro to ALL · "
           + $"+{SalonConstants.ChevalmarinBowEncore} Encore",
    };

    /// <summary>The footer's text for a company on a stage of
    /// <paramref name="slots"/>: the front member's replacement price when
    /// the stage is full, nothing otherwise. Nothing, and not a hidden row:
    /// the row keeps its height so the panel never moves.</summary>
    public static string FooterText(
        IReadOnlyList<SalonMember> company, int slots) =>
        company.Count > 0 && company.Count >= slots
            ? ReplaceText(company[0])
            : string.Empty;

    /// <summary>
    /// Can the stage pay for a FULL-STRENGTH performance right now? The one
    /// expression the chips, the pips and the Encore line's "Reduced" all
    /// read, so the number, the row and the word cannot disagree about whether
    /// the buffer is dry.
    /// </summary>
    public static bool Paid(Creature owner) =>
        FurinaResources.Encore(owner) >= SalonConstants.TickEncoreCost;

    /// <summary>
    /// PERFORMANCES THE PLAYER CAN STILL PAY FOR IN FULL: Encore divided by
    /// what one performance costs. One pip is one FULL-STRENGTH performance,
    /// which is the whole reading; a member with nothing to spend still
    /// performs, at three-quarters (`EB-633`).
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
    /// because Encore has no maximum and an empty track would draw a capacity
    /// that does not exist (`EB-641`). When the buffer cannot pay, the word
    /// <see cref="ReducedWord"/> sits beside the number (`EB-644`): the
    /// condition and its cause on one line, in one tint.
    /// </summary>
    public static string EncoreText(Creature owner) =>
        Paid(owner)
            ? $"Encore {FurinaResources.Encore(owner)}"
            : $"Encore {FurinaResources.Encore(owner)} · {ReducedWord}";

    /// <summary>
    /// LINE 2: the meter and what it buys, on its own line and as short as it
    /// can be. "Bonus" and not "Member bonus" because the chips it lands on are
    /// six pixels below it. Two short lines beat one long one at combat scale.
    /// </summary>
    public static string MeterText(Creature owner) =>
        $"Fanfare {Fanfare(owner)} · Bonus +{MemberBonus(owner)}";

    /// <summary>
    /// The threshold, which is a FOOTNOTE to the Fanfare number and hangs off
    /// the header's hover rather than sitting on it. IT NAMES THE BONUS THE
    /// NEXT THRESHOLD BUYS (`EB-644`): "+1 at 10" beside a Fanfare of 13 read
    /// as either the bonus already held or the next one, so the footnote says
    /// "Bonus +2 at 20" -- the line above it says what is held, this says what
    /// is next, and the two cannot be confused for each other.
    /// </summary>
    public static string StepText(Creature owner) =>
        $"Bonus +{MemberBonus(owner) + 1} at {NextThreshold(owner)}";

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

    // ------------------------------------------------------- the hover --

    /// <summary>What the card under the cursor will do to the stage.</summary>
    public enum HoverKind
    {
        /// <summary>No card, or a card the stage does not answer to.</summary>
        None,
        /// <summary>A Companion card: the FRONT member performs.</summary>
        Companion,
        /// <summary>A Deploy: a member enters, and on a full stage the front
        /// member is replaced.</summary>
        Deploy,
        /// <summary>The Ethereal Spotlight: it spends Encore.</summary>
        Spotlight,
    }

    private static CardModel? _hoveredCard;
    private static CardModel? _selectedCard;
    private static Creature? _lastHoverOwner;

    /// <summary>
    /// WHAT KIND OF CARD THIS IS, TO THE STAGE. By marker interface and never
    /// by name or text: <see cref="ICompanionCard"/> is the mark the Companion
    /// rule itself reads (<c>SalonMemberPower.CompanionPlayTrigger</c>),
    /// <see cref="ISalonDeployCard"/> is written by the generator on every
    /// row that applies the member power, and the Spotlight is its own class.
    /// A card that is none of these does nothing to the stage and the panel
    /// says nothing about it.
    /// </summary>
    public static HoverKind KindOf(CardModel? card) => card switch
    {
        null => HoverKind.None,
        ICompanionCard => HoverKind.Companion,
        ISalonDeployCard => HoverKind.Deploy,
        EtherealSpotlight => HoverKind.Spotlight,
        _ => HoverKind.None,
    };

    /// <summary>How many members a hovered Deploy fields, off its own
    /// mark; zero for anything else.</summary>
    public static int DeployCountOf(CardModel? card) =>
        card is ISalonDeployCard deploy
            ? Math.Max(1, deploy.SalonDeployCount)
            : 0;

    /// <summary>Whose card this is, or null. A card in a hand is a mutable
    /// instance and answers; a canonical model REFUSES the read
    /// (<c>AssertMutable</c>), and a display path must not throw for asking,
    /// so the refusal is null here.</summary>
    private static Creature? OwnerOf(CardModel card)
    {
        try
        {
            return card.Owner?.Creature;
        }
        catch (Exception)
        {
            return null;
        }
    }

    /// <summary>The card the local player is holding over the hand: the one
    /// being PLAYED (picked up, dragged, aimed) wins over the one merely
    /// hovered, because picking a card up unfocuses the hand under it and the
    /// preview must not vanish at the moment it matters most.</summary>
    public static CardModel? ActiveCard => _selectedCard ?? _hoveredCard;

    /// <summary>The hover this owner's panel should show: the active card's
    /// kind if the card is this owner's, else nothing. A co-op partner's hover
    /// is not on this screen and is not tracked here.</summary>
    public static HoverKind HoverFor(Creature owner)
    {
        var card = ActiveCard;
        return card != null && OwnerOf(card) == owner
            ? KindOf(card)
            : HoverKind.None;
    }

    /// <summary>The active Deploy's count for this owner, zero when the
    /// active card is not this owner's Deploy.</summary>
    public static int DeploysFor(Creature owner)
    {
        var card = ActiveCard;
        return card != null && OwnerOf(card) == owner
            ? DeployCountOf(card)
            : 0;
    }

    /// <summary>
    /// THE WORD ON A CHIP, from the seat, the stage and the card under the
    /// cursor. One function for every chip so the four words cannot disagree
    /// about which seat a Deploy reaches:
    ///
    ///   * no card: chip 0 says FRONT when someone is in it;
    ///   * a Companion: chip 0 says PERFORMS -- the trigger FRONT only named
    ///     the position of;
    ///   * a Deploy: the seats it REPLACES say LEAVES (the front ones, as many
    ///     as the deploys exceed the room by -- `SalonMemberPower.Deploy`'s
    ///     loop, closed the way <c>WillReplace</c> closes it) and the empty
    ///     seats it fills say ENTERS; chip 0 says FRONT if it is neither;
    ///   * the Spotlight: no seat changes, so the words are the no-card ones.
    /// </summary>
    public static string SlotWord(
        int index, int companyCount, int slots, HoverKind hover, int deploys)
    {
        var occupied = index < companyCount;

        switch (hover)
        {
            case HoverKind.Companion:
                return index == 0 && occupied ? PerformsWord : string.Empty;

            case HoverKind.Deploy:
            {
                var room = Math.Max(0, slots - companyCount);
                var replaced = Math.Min(companyCount,
                                        Math.Max(0, deploys - room));
                if (occupied && index < replaced) return LeavesWord;
                if (!occupied && index < companyCount + Math.Min(room, deploys))
                {
                    return EntersWord;
                }

                return index == 0 && occupied ? FrontWord : string.Empty;
            }

            default:
                return index == 0 && occupied ? FrontWord : string.Empty;
        }
    }

    /// <summary>Is this chip lit by the hover? Exactly when its word is one
    /// of the hover words -- one rule for the frame, the ground and the word,
    /// so a chip cannot be lit without saying why.</summary>
    public static bool Highlighted(string word) =>
        word == PerformsWord || word == LeavesWord || word == EntersWord;

    /// <summary>How many pips the hovered Spotlight would spend: its price,
    /// clamped to what the strip draws. Zero for any other hover.</summary>
    public static int SpendPips(Creature owner)
    {
        if (HoverFor(owner) != HoverKind.Spotlight) return 0;
        if (SalonConstants.TickEncoreCost <= 0) return 0;
        var pips = FurinaReframeLaw.SpotlightDesignateEncoreCost
                 / SalonConstants.TickEncoreCost;
        return Math.Min(Math.Min(pips, Pips(owner)), MaxPips);
    }

    /// <summary>The hand's hover, from the game's own tracker. The four
    /// postfixes at the foot of this file are the only callers.</summary>
    internal static void NoteHovered(CardModel? card)
    {
        _hoveredCard = card;
        RepaintForHover(ActiveCard);
    }

    internal static void NoteUnhovered()
    {
        _hoveredCard = null;
        RepaintForHover(ActiveCard);
    }

    internal static void NoteSelected(CardModel? card)
    {
        _selectedCard = card;
        RepaintForHover(ActiveCard);
    }

    internal static void NoteDeselected()
    {
        _selectedCard = null;
        RepaintForHover(ActiveCard);
    }

    /// <summary>
    /// Repaint the panel the hover has left and the one it has reached. FURINA
    /// ONLY and by the identity predicate the mod already owns: the tracker
    /// reports every seat's hand, and a hover on Klee's hand must not so much
    /// as look for a Salon. A hover is a display path, so a failure here costs
    /// one preview and never a run.
    /// </summary>
    private static void RepaintForHover(CardModel? card)
    {
        try
        {
            var owner = card == null ? null : OwnerOf(card);
            if (owner != null && !FurinaResources.IsFurina(owner))
            {
                owner = null;
            }

            var previous = _lastHoverOwner;
            _lastHoverOwner = owner;

            if (previous != null && previous != owner) Refresh(previous);
            if (owner != null) Refresh(owner);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] salon panel: a hover could not be "
                   + $"drawn ({e.GetType().Name}: {e.Message}).");
        }
    }

    // ------------------------------------------------------- the measured box --

    /// <summary>Every word the slot row can print, for the measurement and
    /// the pins. DECLARED BEFORE THE MEASUREMENT: static fields initialise in
    /// textual order, and the measurement below reads this one.</summary>
    public static readonly string[] SlotWords =
    {
        FrontWord, PerformsWord, LeavesWord, EntersWord,
    };

    /// <summary>
    /// The widest thing a chip can ever print, at its own tier.
    ///
    /// EVERY REACHABLE STRING, not a sample of them: each member's name at tier
    /// 2, each member's effect row at tier 1 plus glyph plus tier 2 for the
    /// two-digit design case, and every slot word at tier 3. This is the whole
    /// of `EB-639`'s "the fit is computed, not assumed" in the horizontal
    /// direction; the vertical half is that every row in
    /// <see cref="FurinaBoardScale"/> has its own Y.
    /// </summary>
    public static readonly float ChipContentWidth = WidestChipContent();

    /// <summary>
    /// The panel's box, measured from the chips for the stage a Furina
    /// actually stands on (<see cref="SalonConstants.MemberSlots"/>) AND FROM
    /// NOTHING ELSE (`EB-644`). Fixed for the run, so the anchor below is
    /// fixed too: a raised cap tiles narrower chips into the same box, and no
    /// header or footer string can move the panel out from under the player
    /// mid-combat -- each is measured against <see cref="InnerWidth"/> and
    /// shortened at design time if it does not fit.
    /// </summary>
    public static readonly float PanelWidth = FurinaBoardScale.PanelWidthFor(
        SalonConstants.MemberSlots, ChipContentWidth);

    /// <summary>The width every row has for its text: the panel less the one
    /// inset on each side.</summary>
    public static readonly float InnerWidth =
        PanelWidth - 2f * FurinaBoardScale.PanelPad;

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
        var widest = 0f;
        foreach (var word in SlotWords)
        {
            widest = Math.Max(widest, FurinaBoardScale.TextWidth(
                word, FurinaBoardScale.Tier3FontSize));
        }

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
    /// stepped down TOGETHER where they do not, because the tiers are a
    /// hierarchy and shrinking one half alone would end with a unit as large
    /// as the number it qualifies.
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

    /// <summary>Re-read the queue, the Fanfare bonus, the Encore and the
    /// hover, then redraw. Driven by <see cref="SalonVisualsBridge.Refresh"/>,
    /// i.e. by the Funnel Contract's own funnels, and by the hover postfixes
    /// below. No `_Process` anywhere in this file.</summary>
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
    /// over at the next combat. The hover is forgotten with it.
    /// </summary>
    internal static void Hide()
    {
        _hoveredCard = null;
        _selectedCard = null;
        _lastHoverOwner = null;

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
        // four widgets: everything about the Salon is inside it, and it is the
        // ONLY ground -- the header and the footer stand on it directly
        // (`EB-644`). Sized to the slot row, which is what the measurement
        // above is for.
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

        // THE HAIRLINES, one in each row gap, so the three bands read as
        // sections of one object rather than as three objects.
        root.AddChildSafely(Hairline("RuleTop",
            FurinaBoardScale.ChipsRowY
                - (FurinaBoardScale.RowGap + FurinaBoardScale.RuleHeight) / 2f));
        root.AddChildSafely(Hairline("RuleBottom",
            FurinaBoardScale.FooterRowY
                - (FurinaBoardScale.RowGap + FurinaBoardScale.RuleHeight) / 2f));

        for (var i = 0; i < MaxChips; i++)
        {
            root.AddChildSafely(BuildChip(i));
        }

        root.AddChildSafely(BuildFooter());

        return root;
    }

    private static ColorRect Hairline(string name, float y) => new()
    {
        Name = name,
        MouseFilter = Control.MouseFilterEnum.Ignore,
        Position = new Vector2(FurinaBoardScale.PanelPad, y),
        Size = new Vector2(InnerWidth, FurinaBoardScale.RuleHeight),
        Color = Rule,
        ZIndex = -1,
    };

    private static Control BuildResourceRows(int? energyOrbFontSize)
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
            Size = new Vector2(
                PanelWidth,
                FurinaBoardScale.MeterRowY + FurinaBoardScale.MeterRowHeight
                    - FurinaBoardScale.ResourceRowY),
        };

        // LINE 1: the word, the number, then the lit pips beside them. LEFT
        // at the one inset, like every row.
        var encore = Text("Encore", size,
            new Vector2(FurinaBoardScale.PanelPad, 0f),
            InnerWidth, FurinaBoardScale.ResourceRowHeight);
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
            InnerWidth, FurinaBoardScale.PipHeight);
        overflow.HorizontalAlignment = HorizontalAlignment.Left;
        overflow.Visible = false;
        row.AddChildSafely(overflow);

        // LINE 2: the meter and what it buys.
        var meters = Text("Meters", size,
            new Vector2(FurinaBoardScale.PanelPad,
                        FurinaBoardScale.MeterRowY
                            - FurinaBoardScale.ResourceRowY),
            InnerWidth, FurinaBoardScale.MeterRowHeight);
        meters.HorizontalAlignment = HorizontalAlignment.Left;
        row.AddChildSafely(meters);

        return row;
    }

    private static Control BuildChip(int index)
    {
        var chip = new Control
        {
            Name = $"Chip{index}",
            // Ignore by default; the FRONT chip is switched to Pass at paint
            // so its own hover line (`FrontTip`) can show. `EB-300`: display
            // only, never in the controller's focus graph -- a player walking
            // the HUD must not land on a picture of a crab with no way back to
            // the hand.
            MouseFilter = Control.MouseFilterEnum.Ignore,
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

        // The front marker's FRAME, and the hover's. A frame rather than a
        // tint, so it survives the dry grey: "which one is the front" and
        // "can the stage pay" are two different questions and neither may eat
        // the other's channel. The WORD under it says what the frame means.
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
        // TIER 3: the slot word, on its own row.
        chip.AddChildSafely(Text("Word", FurinaBoardScale.Tier3FontSize,
            Vector2.Zero, 0f, FurinaBoardScale.FrontRowHeight));

        return chip;
    }

    private static Label BuildFooter()
    {
        // ONE LABEL ON THE PANEL'S OWN GROUND (`EB-644`), at the one inset,
        // as wide as every other row. It had a strip of its own and read as a
        // separate object; now it is the panel's last row, and it is ALWAYS
        // a row so the box never changes height with the message.
        var footer = Text("Footer", FurinaBoardScale.Tier2FontSize,
            new Vector2(FurinaBoardScale.PanelPad, FurinaBoardScale.FooterRowY),
            InnerWidth, FurinaBoardScale.FooterRowHeight);
        footer.HorizontalAlignment = HorizontalAlignment.Left;
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
        var hover = HoverFor(owner);
        var deploys = DeploysFor(owner);

        // THE FIT, EVERY PAINT. The chip is as wide as the box allows for the
        // stage actually on screen, and every string inside it is stepped down
        // to that width -- so a raised cap or a three-digit performance costs a
        // font point, never a collision. The group starts at the one inset.
        var chipWidth = FurinaBoardScale.ChipWidthFor(
            PanelWidth, slots, ChipContentWidth);
        var left = FurinaBoardScale.PanelPad;

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
                      chipWidth, paid,
                      word: SlotWord(i, company.Count, slots, hover, deploys),
                      front: i == 0);
        }

        PaintFooter(root, company, slots, hover);
        PaintResources(root, owner, paid);
    }

    private static void PaintChip(
        Control chip, Creature owner, SalonMember? member, float width,
        bool paid, string word, bool front)
    {
        var occupied = member is { } _;
        var lit = Highlighted(word);

        if (chip.GetNodeOrNull<ColorRect>("Back") is { } back)
        {
            back.Size = new Vector2(width, FurinaBoardScale.ChipHeight);
            back.Color = lit ? HoverBack : occupied ? ChipBack : EmptyBack;
        }

        // An EMPTY chip is drawn dim rather than hidden: the panel's width is
        // the cap, and a stage of one that renders as one chip tells the
        // player nothing about the two seats they still have. It is FRAMED
        // only while a hovered Deploy will fill it.
        if (chip.GetNodeOrNull<ColorRect>("Frame") is { } frame)
        {
            frame.Size = new Vector2(width + 4f,
                                     FurinaBoardScale.ChipHeight + 4f);
            frame.Visible = lit || (occupied && front);
            frame.Color = lit ? HoverFrame : FrontFrame;
        }

        // THE FRONT CHIP'S OWN HOVER LINE: the rule in words, for a player
        // who has not picked up a Companion yet. `Pass` so the tooltip can
        // show; the click still goes through.
        chip.TooltipText = occupied && front ? FrontTip : string.Empty;
        chip.MouseFilter = occupied && front
            ? Control.MouseFilterEnum.Pass
            : Control.MouseFilterEnum.Ignore;

        var inner = width - 2f * FurinaBoardScale.ChipPad;
        var face = chip.GetNodeOrNull<TextureRect>("Face");
        var name = chip.GetNodeOrNull<Label>("Name");
        var number = chip.GetNodeOrNull<Label>("ActNumber");
        var icon = chip.GetNodeOrNull<TextureRect>("ActIcon");
        var unit = chip.GetNodeOrNull<Label>("ActUnit");
        var wordLabel = chip.GetNodeOrNull<Label>("Word");

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

        if (wordLabel != null)
        {
            wordLabel.Position = new Vector2(
                FurinaBoardScale.ChipPad,
                FurinaBoardScale.FaceHeight + 2f
                    + FurinaBoardScale.NameRowHeight
                    + FurinaBoardScale.ActRowHeight);
            wordLabel.Size = new Vector2(
                inner, FurinaBoardScale.FrontRowHeight);
            // THE WORD IS THE STATE (`EB-637`): FRONT, or what the card under
            // the cursor does to this seat. Lit words in the hover tint, FRONT
            // in the frame's.
            wordLabel.Visible = word.Length > 0;
            wordLabel.Text = word;
            wordLabel.AddThemeColorOverride(
                ThemeConstants.Label.FontColor, lit ? HoverFrame : FrontFrame);
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
        Node2D root, IReadOnlyList<SalonMember> company, int slots,
        HoverKind hover)
    {
        if (root.GetNodeOrNull<Label>("Footer") is not { } footer) return;

        // ONE CONTEXTUAL FOOTER (`EB-644`): the price of the next deploy on a
        // full stage, DIM until a Deploy is under the cursor and BRIGHT while
        // one is. The text is never stepped down -- it was measured against
        // the row at its own tier when it was written, and the pin holds it
        // there -- and the row is always present, so nothing below it moves.
        footer.Text = FooterText(company, slots);
        footer.Visible = footer.Text.Length > 0;
        footer.AddThemeColorOverride(
            ThemeConstants.Label.FontColor,
            hover == HoverKind.Deploy ? StsColors.cream : DryText);
    }

    private static void PaintResources(Node2D root, Creature owner, bool paid)
    {
        if (root.GetNodeOrNull<Control>("Resources") is not { } row) return;

        var size = FurinaBoardScale.Tier2FontSize;

        if (row.GetNodeOrNull<Label>("Encore") is { } encore)
        {
            encore.Text = EncoreText(owner);
            size = encore.GetThemeFontSize(ThemeConstants.Label.FontSize);
            // THE REDUCED TINT IS THE LINE'S (`EB-644`): the word and the
            // number it qualifies wear one colour, and it is the colour the
            // chips' dry numbers do not, so "Reduced" is read before it is
            // read.
            encore.AddThemeColorOverride(
                ThemeConstants.Label.FontColor,
                paid ? StsColors.cream : ReducedText);
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

    private static void PaintPips(Control row, Creature owner, float x)
    {
        if (row.GetNodeOrNull<Control>("Pips") is not { } strip) return;

        var drawn = Math.Min(Pips(owner), MaxPips);
        var spend = SpendPips(owner);
        strip.Position = new Vector2(x, 3f);

        for (var i = 0; i < MaxPips; i++)
        {
            if (strip.GetNodeOrNull<ColorRect>($"Pip{i}") is not { } pip)
            {
                continue;
            }

            // FILLED ONLY (`EB-641`). Nothing is drawn where there is nothing,
            // and the number beside it is the reading either way. While the
            // Spotlight is under the cursor, the pips it would spend wear the
            // spend tint (`EB-637`) -- a hover, not the standing claim `EB-641`
            // took off the strip.
            pip.Visible = i < drawn;
            pip.Color = i < spend ? PipSpend : PipFull;
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

/// <summary>
/// THE HAND'S HOVER, from the game's own tracker (`EB-637`).
///
/// <c>NPlayerHand</c> tells <c>RunManager.Instance.HoveredModelTracker</c>
/// about every hand hover (<c>OnHolderFocused</c> / <c>OnHolderUnfocused</c>)
/// and every pick-up and release (<c>StartCardPlay</c> and its <c>Finished</c>
/// callback), and it does so for the co-op wire's sake: the tracker exists to
/// tell the other seat what this one is looking at. That makes it the one
/// place both signals already pass through with the card MODEL in hand, which
/// is what the panel needs -- the marker interface is on the model. Four
/// postfixes, one each, all delegating to the panel; the character scope is
/// the panel's (<c>FurinaResources.IsFurina</c> on the card's owner), because
/// the tracker is every seat's and a hover on Klee's hand must not look for a
/// Salon.
/// </summary>
[HarmonyPatch(typeof(HoveredModelTracker),
              nameof(HoveredModelTracker.OnLocalCardHovered))]
internal static class HoveredModelTracker_OnLocalCardHovered_SalonPanel_Patch
{
    [HarmonyPostfix]
    public static void Postfix(CardModel cardModel) =>
        SalonPanel.NoteHovered(cardModel);
}

[HarmonyPatch(typeof(HoveredModelTracker),
              nameof(HoveredModelTracker.OnLocalCardUnhovered))]
internal static class HoveredModelTracker_OnLocalCardUnhovered_SalonPanel_Patch
{
    [HarmonyPostfix]
    public static void Postfix() => SalonPanel.NoteUnhovered();
}

[HarmonyPatch(typeof(HoveredModelTracker),
              nameof(HoveredModelTracker.OnLocalCardSelected))]
internal static class HoveredModelTracker_OnLocalCardSelected_SalonPanel_Patch
{
    [HarmonyPostfix]
    public static void Postfix(CardModel cardModel) =>
        SalonPanel.NoteSelected(cardModel);
}

[HarmonyPatch(typeof(HoveredModelTracker),
              nameof(HoveredModelTracker.OnLocalCardDeselected))]
internal static class HoveredModelTracker_OnLocalCardDeselected_SalonPanel_Patch
{
    [HarmonyPostfix]
    public static void Postfix() => SalonPanel.NoteDeselected();
}
