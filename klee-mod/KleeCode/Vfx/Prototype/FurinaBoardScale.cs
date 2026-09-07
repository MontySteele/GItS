using System;
using Godot;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.addons.mega_text;

namespace KleeMod.Vfx;

/// <summary>
/// ONE SCALE TABLE FOR FURINA'S BOARD (`EB-634`), AND IT IS A HIERARCHY.
///
/// THE FIND. [USER] on the `0.2.2917+proto` frame: the board's font and icon
/// sizes need controlling, and the Fanfare badge is too large. Four elements
/// were sizing themselves -- the chips, the chip text, the pips, and the badge
/// in the energy corner -- each with its own literals, so nothing on screen
/// agreed about what mattered most. The Fanfare count was drawn at 40, the same
/// order as the energy orb's own number, for a figure the player consults once
/// a turn; the performance numbers, which are what a play is priced against,
/// were drawn at 14.
///
/// SO THE TABLE IS TIERS AND NOT A LIST OF PIXELS. A flat table of sizes would
/// have fixed the drift and not the reading: it would still be possible to
/// give the Evoke footnote the same size as the number it qualifies, and no
/// rule would have been broken. Three tiers, and every text element on the
/// board declares which one it is:
///
///   * TIER 1 -- <see cref="Tier1FontSize"/>. WHAT A PERFORMANCE PAYS. One
///     kind of thing only: the NUMBER on a chip. It is the number every
///     Companion play and every deploy is priced against, so it is the largest
///     thing on the panel.
///   * TIER 2 -- <see cref="Tier2FontSize"/>. WHO, WHAT THE NUMBER IS IN, AND
///     HOW MUCH IS IN THE BANK. Member names, the unit beside the number
///     ("damage", "Block"), the two resource lines and the front chip's
///     Replace footer. Read second, and read as a group.
///   * TIER 3 -- <see cref="Tier3FontSize"/>. EVERYTHING THAT QUALIFIES
///     SOMETHING ELSE. The FRONT marker's word, the reduced-performance note,
///     the pip overflow.
///
/// THE FANFARE NUMBER IS TIER 2 AND SMALLER THAN THE ENERGY ORB'S NUMBER,
/// which is the row's own acceptance condition and is enforced rather than
/// asserted: <see cref="ResourceFontSize"/> takes the orb's size when the live
/// scene will give it and clamps the resource line under it, and falls back to
/// <see cref="EnergyOrbFontSizeFallback"/> -- the size the mod's own badge
/// mirrors the orb's number at (`SparkCounter.CountFontSize`, itself copied
/// from `NStarCounter`) -- when it will not. A constant alone would have been
/// a guess about a scene we do not ship; the node is the fact where the node
/// can be found.
///
/// AND THE BOX IS MEASURED FROM THE WORDS, NOT ASSUMED (`EB-639`, `EB-641`).
/// The first frame of the panel drew "5 Hydro3 Block5 Hydro" -- three chips
/// whose text was wider than the chip it was centred in, so the numbers ran
/// together across the gaps, and an Evoke line that landed on top of the
/// reduced-performance note. The tiers were right and the FIT was never
/// computed. So this file now measures: <see cref="TextWidth"/> is a
/// conservative, documented character table (there is no live font in the test
/// host, and a table that OVER-estimates can only make a box too wide, never
/// too narrow), <see cref="FitFontSize"/> steps a string down until it fits the
/// box it is drawn in, and every row below has its own Y and its own height so
/// two texts cannot share a line.
///
/// GEOMETRY LIVES HERE TOO, for the reason the tiers do: the panel's rows, its
/// chip padding and its pips are one layout, and a chip that grew without its
/// row growing is the drift this file exists to make impossible. What is NOT
/// here is anything that is a RULE -- the chip count is
/// `SalonMemberPower.SlotsFor`, the act is `TickValue`, the pip count is Encore
/// over `TickEncoreCost` -- nor anything that depends on the panel's own WORDS,
/// which is why the panel's WIDTH is measured in <see cref="SalonPanel"/> from
/// the strings it prints and handed back through <see cref="PanelWidthFor"/>.
/// `tools/lint_constant_parity.py` carries every constant below as presentation
/// with that boundary written down.
///
/// QUARANTINED. `Vfx/Prototype/**` is `Compile Remove`d without
/// `-p:PrototypeCards=true`. Revert is the flag.
/// </summary>
public static class FurinaBoardScale
{
    // ------------------------------------------------------------ tiers --

    /// <summary>Tier 1: what a performance pays. The largest thing on the
    /// panel, because it is the number every play is priced against.</summary>
    public const int Tier1FontSize = 20;

    /// <summary>Tier 2: who is on stage, what the number is in, and what is in
    /// the bank.</summary>
    public const int Tier2FontSize = 13;

    /// <summary>Tier 3: anything that qualifies something else.</summary>
    public const int Tier3FontSize = 10;

    /// <summary>
    /// The energy orb's own number size, for when the live label cannot be
    /// read. `SparkCounter.CountFontSize` by value -- the size Klee's badge
    /// mirrors `NStarCounter`'s number at, which is the game's own reading of
    /// "as large as the orb" -- so the fallback is a measured figure rather
    /// than a guess, and every tier above is below it.
    /// </summary>
    public const int EnergyOrbFontSizeFallback = 40;

    /// <summary>
    /// The resource line's size: tier 2, and strictly under the orb's number
    /// whatever the orb turns out to be. `EB-634`'s acceptance condition,
    /// enforced rather than asserted.
    /// </summary>
    public static int ResourceFontSize(int? energyOrbFontSize)
    {
        var orb = energyOrbFontSize is { } n && n > 0
            ? n
            : EnergyOrbFontSizeFallback;
        return Math.Max(1, Math.Min(Tier2FontSize, orb - 1));
    }

    /// <summary>
    /// The energy label's font size off the LIVE scene, or null when this
    /// build's combat UI will not give one up.
    ///
    /// BY SEARCH AND NOT BY PATH. `%EnergyCounterContainer` is a node the game
    /// owns and re-lays out; naming a child of it by path would be a claim
    /// about a scene we do not ship and that `EB-621` already declined to make
    /// for the star counter's rect. The first descendant `Label` in that
    /// container is the number, and if the shape ever changes the answer is
    /// null and the fallback stands -- which is a slightly large line, not a
    /// missing one.
    /// </summary>
    public static int? EnergyOrbFontSize(NCombatUi? ui)
    {
        try
        {
            if (ui?.EnergyCounterContainer is not { } container) return null;
            if (FirstLabel(container) is not { } label) return null;
            var size = label.GetThemeFontSize(ThemeConstants.Label.FontSize);
            return size > 0 ? size : null;
        }
        catch (Exception)
        {
            // Read on a live scene from a display path: a missing theme entry
            // or a freed node must cost the panel a font size, never a run.
            return null;
        }
    }

    private static Label? FirstLabel(Node node)
    {
        foreach (var child in node.GetChildren())
        {
            if (child is Label label) return label;
            if (child is Node inner && FirstLabel(inner) is { } found)
            {
                return found;
            }
        }

        return null;
    }

    // ----------------------------------------------------- measuring text --

    /// <summary>
    /// HOW WIDE A STRING IS, CONSERVATIVELY, in pixels at a font size.
    ///
    /// WHY A TABLE AND NOT THE FONT. The fit has to be computed where the
    /// panel is BUILT and pinned where there is no engine at all: Godot's
    /// `Font.GetStringSize` needs a live `Font` resource, and the test host has
    /// no Godot (KleeTests README, the headless boundary). A measurement that
    /// only exists in the game is exactly the measurement `EB-639` shows
    /// nobody takes.
    ///
    /// SO IT IS A CHARACTER TABLE THAT OVER-ESTIMATES. The advances below are
    /// fractions of the font size, read off the base game's own UI face at the
    /// widest glyph in each class -- digits and capitals at
    /// <see cref="WideCharEm"/>, ordinary lowercase at
    /// <see cref="NarrowCharEm"/>, the space at <see cref="SpaceEm"/> and
    /// punctuation at <see cref="PunctEm"/>. Every unknown character is charged
    /// the WIDE rate. An over-estimate can only make a box too wide or a font
    /// one point too small; an under-estimate is the collision this exists to
    /// prevent, so the error is one-way on purpose.
    /// </summary>
    public static float TextWidth(string? text, int fontSize)
    {
        if (string.IsNullOrEmpty(text) || fontSize <= 0) return 0f;

        var em = 0f;
        foreach (var c in text!)
        {
            em += c switch
            {
                ' ' => SpaceEm,
                '.' or ',' or ':' or ';' or '!' or '\'' or 'i' or 'j' or 'l'
                    => PunctEm,
                >= 'a' and <= 'z' when c is not ('m' or 'w')
                    => NarrowCharEm,
                _ => WideCharEm,
            };
        }

        return em * fontSize;
    }

    /// <summary>A digit, a capital, an 'm' or a 'w', and every character this
    /// table does not know: the widest class, charged to anything unfamiliar so
    /// the error runs towards a box that is too wide.</summary>
    public const float WideCharEm = 0.62f;

    /// <summary>Ordinary lowercase.</summary>
    public const float NarrowCharEm = 0.55f;

    /// <summary>The space.</summary>
    public const float SpaceEm = 0.30f;

    /// <summary>Punctuation and the three thin lowercase letters.</summary>
    public const float PunctEm = 0.35f;

    /// <summary>
    /// The largest size at or under <paramref name="fontSize"/> at which this
    /// string fits <paramref name="width"/>.
    ///
    /// THE LAST LINE OF THE FIT, and it is what makes the pin total rather
    /// than a sample: the panel's boxes are measured for the numbers a stage
    /// actually reaches, and a Fanfare-fed three-digit performance -- or a
    /// five-seat stage under an upgraded Box Seats, where every chip is
    /// narrower -- steps its own text down a point instead of running into its
    /// neighbour. A string can always be made to fit at size 1, so this
    /// terminates.
    /// </summary>
    public static int FitFontSize(string? text, int fontSize, float width)
    {
        var size = fontSize;
        while (size > 1 && TextWidth(text, size) > width)
        {
            size--;
        }

        return size;
    }

    // -------------------------------------------------------- the panel --

    /// <summary>Inset of every row from the panel's edge.</summary>
    public const float PanelPad = 6f;

    /// <summary>
    /// The panel's box width for a stage of <paramref name="slots"/> chips: the
    /// chips and their gaps, or the front chip's Replace footer, whichever
    /// needs more room, plus the pad on either side.
    ///
    /// THE CONTENT DECIDES (`EB-641`). The first box was Furina's own 240-wide
    /// creature bounds, chosen so the panel could not overhang the lanes on
    /// either side -- and the text did not fit in it, which is the defect. A
    /// box measured from the words is wider than that and still nowhere near
    /// the enemy: it is centred on a creature standing in the left third of the
    /// screen, and the whole group moved to ONE dark backing precisely so the
    /// player reads it as one thing wherever it sits.
    /// </summary>
    public static float PanelWidthFor(
        int slots, float chipContentWidth, float footerWidth)
    {
        var chips = Math.Max(1, slots);
        var group = chips * (chipContentWidth + 2f * ChipPad)
                  + (chips - 1) * ChipGap;
        return 2f * PanelPad + Math.Max(group, footerWidth);
    }

    /// <summary>
    /// One chip's width inside a panel of <paramref name="panelWidth"/> drawing
    /// <paramref name="slots"/> chips, never wider than the content asked for.
    ///
    /// A stage of one or two draws chips at their measured width and leaves the
    /// rest of the box empty; a stage of four or five (Box Seats upgraded)
    /// tiles narrower chips into the same box rather than overhanging, and
    /// <see cref="FitFontSize"/> takes the text down with them. What never
    /// happens is chips that overlap.
    /// </summary>
    public static float ChipWidthFor(
        float panelWidth, int slots, float chipContentWidth)
    {
        var chips = Math.Max(1, slots);
        var span = panelWidth - 2f * PanelPad - (chips - 1) * ChipGap;
        return Math.Min(chipContentWidth + 2f * ChipPad, span / chips);
    }

    /// <summary>The padding inside a chip, left and right of its widest
    /// text.</summary>
    public const float ChipPad = 7f;

    /// <summary>The gap between two chips. Consistent, and wide enough that
    /// the row reads as three things rather than one smear -- which is what
    /// `EB-639`'s frame showed when the text was wider than the chip.</summary>
    public const float ChipGap = 8f;

    /// <summary>The gap between the number and the element glyph beside
    /// it.</summary>
    public const float IconGap = 4f;

    // ---------------------------------------------------------- the rows --
    //
    // EVERY ROW HAS ITS OWN Y AND ITS OWN HEIGHT, top to bottom, and the next
    // row starts at or after the previous one's bottom edge. That is the whole
    // of `EB-639`'s no-overlap rule in the vertical direction, and the pins
    // read these numbers rather than a frame.

    /// <summary>Line 1 of the resource header: "Encore N" and the FILLED
    /// pips.</summary>
    public const float ResourceRowY = 5f;
    public const float ResourceRowHeight = 19f;

    /// <summary>Line 2 of the resource header: the Fanfare and what it is
    /// buying. Its own line, because one line carrying both meters was a
    /// sentence-long smear at combat scale.</summary>
    public const float MeterRowY = ResourceRowY + ResourceRowHeight;
    public const float MeterRowHeight = 17f;

    /// <summary>The chip row.</summary>
    public const float ChipsRowY = MeterRowY + MeterRowHeight + 3f;

    /// <summary>How much of a chip the member's face crop occupies. Enlarged
    /// with the chip (`EB-641`): "seahorse, crab, seahorse" has to read at a
    /// glance, and a 30-pixel band could not carry it.</summary>
    public const float FaceHeight = 52f;

    /// <summary>The member's name, under the face.</summary>
    public const float NameRowHeight = 15f;

    /// <summary>The number, its glyph and its unit.</summary>
    public const float ActRowHeight = 24f;

    /// <summary>The FRONT marker's own row, so the word never lands on the
    /// number above it.</summary>
    public const float FrontRowHeight = 13f;

    public const float ChipHeight =
        FaceHeight + 2f + NameRowHeight + ActRowHeight + FrontRowHeight;

    /// <summary>The front chip's Replace footer, touching the chip's bottom
    /// edge so it reads as part of it.</summary>
    public const float FooterRowY = ChipsRowY + ChipHeight;
    public const float FooterRowHeight = 17f;

    /// <summary>The reduced-performance note's row, under everything.</summary>
    public const float NoticeRowY = FooterRowY + FooterRowHeight + 2f;
    public const float NoticeRowHeight = 15f;

    /// <summary>The panel's height: the last row's bottom edge and the
    /// pad.</summary>
    public const float PanelHeight = NoticeRowY + NoticeRowHeight + PanelPad;

    // ---------------------------------------------------------- the pips --

    public const float PipWidth = 7f;
    public const float PipHeight = 12f;
    public const float PipGap = 3f;

    /// <summary>The gap between the Encore number and the first pip: what
    /// "beside the number" is in pixels, now that where the number ENDS is
    /// measured rather than guessed at.</summary>
    public const float PipStripGap = 8f;
}
