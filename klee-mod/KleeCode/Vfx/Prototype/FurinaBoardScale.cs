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
///     kind of thing only: the folded number on a chip ("5" beside the Hydro
///     word, "3 Block"). It is the number every Companion play and every
///     deploy is priced against, so it is the largest thing on the panel.
///   * TIER 2 -- <see cref="Tier2FontSize"/>. WHO, AND HOW MUCH IS IN THE
///     BANK. Member names and the resource line (Encore, Fanfare, the member
///     bonus). Read second, and read as a group.
///   * TIER 3 -- <see cref="Tier3FontSize"/>. EVERYTHING THAT QUALIFIES
///     SOMETHING ELSE. The FRONT marker's word, the front chip's Evoke line,
///     the reduced-performance note, the pip overflow.
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
/// GEOMETRY LIVES HERE TOO, for the reason the tiers do: the panel's box, its
/// chips and its pips are one layout, and a chip that grew without its row
/// growing is the drift this file exists to make impossible. What is NOT here
/// is anything that is a RULE -- the chip count is `SalonMemberPower.SlotsFor`,
/// the act is `TickValue`, the pip count is Encore over `TickEncoreCost` -- and
/// `tools/lint_constant_parity.py` carries every name below as presentation
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

    /// <summary>Tier 2: who is on stage, and what is in the bank.</summary>
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

    // -------------------------------------------------------- the panel --

    /// <summary>The panel's box. 240 is the creature's own bounds width
    /// (`SalonVisualsBridge`'s header), so the panel cannot overhang into the
    /// enemy intent and targeting lanes on either side.</summary>
    public const float PanelWidth = 240f;

    /// <summary>The panel's height, the sum of the rows below plus their
    /// margins. Written down rather than computed so the backing rectangle and
    /// the anchor agree without either reading the other.</summary>
    public const float PanelHeight = 130f;

    /// <summary>Inset of every row from the panel's edge.</summary>
    public const float PanelPad = 6f;

    /// <summary>The resource line's row: Encore, the pips, Fanfare and the
    /// member bonus, at the TOP of the panel because it is the state the chips
    /// below are read against.</summary>
    public const float ResourceRowY = 5f;

    /// <summary>The resource row's height.</summary>
    public const float ResourceRowHeight = 18f;

    // --------------------------------------------------------- the chips --

    public const float ChipsRowY = 26f;
    public const float ChipWidth = 70f;
    public const float ChipHeight = 84f;

    /// <summary>How much of a chip the member's face crop occupies.</summary>
    public const float FaceHeight = 30f;

    /// <summary>The widest gap between chip centres: three chips inside the
    /// panel with its pad on either side. A cap raised past three tightens
    /// instead of overhanging.</summary>
    public const float ChipPitchMax = 76f;

    // ---------------------------------------------------------- the pips --

    public const float PipWidth = 7f;
    public const float PipHeight = 12f;
    public const float PipGap = 3f;

    /// <summary>Where the pip strip starts inside the resource row: after the
    /// Encore name and its number, which is what "beside the Encore number"
    /// means in pixels.</summary>
    public const float PipStripX = 82f;

    /// <summary>How wide the pip strip may be before the Fanfare half of the
    /// line starts.</summary>
    public const float PipStripWidth = 62f;

    // ------------------------------------------------- the bottom notice --

    /// <summary>The reduced-performance note's row, under the chips.</summary>
    public const float NoticeRowY = 112f;

    /// <summary>The notice row's height.</summary>
    public const float NoticeRowHeight = 13f;
}
