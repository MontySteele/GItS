using System.Collections.Generic;
using BaseLib.Abstracts;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// THE TOOLTIP TRIM (2026-10-14, review/active/tooltip-trim-2026-10-14.md
/// sec.3, all three picks at (a)). The PLAYER's words for the arm tips whose
/// seat wording is longer than a hover should be.
///
/// [USER], during the 2026-10-14 Furina run: "her cards still make a million
/// words of tooltips come up ... I think it's worth trying to figure out how
/// to make this cleaner / simpler so the tooltips aren't half the screen."
///
/// THE HOUSE RULE: at most 3 boxes on a card's static hover, about 90
/// characters a box, in base-game style (what the word does, in one
/// sentence). `tools/lint_hover_tips.py` holds every generated card to it.
///
/// THE SEAT KEEPS EVERY WORD. Each body here replaces the seat wording only
/// while <see cref="TipAudience.Seat"/> is false; the bridge reads as a seat,
/// so a blind seat's page carries the long sentence it always did (the
/// riders the seats asked for). Which boxes a card raises for each reader is
/// codegen's (`gen_klee_cards.player_tip_layers`).
///
/// The numerals are read from the laws they quote (`EB-89`).
/// </summary>
internal static class PlayerTips
{
    /// <summary>The merged Guest Star box, the paper's sentence. Declared
    /// before <see cref="Bodies"/>, which reads it at type init.</summary>
    internal static readonly string GuestStarBody =
        "Joins at the back and acts at the end of your turn. A fourth guest "
      + "pushes out the oldest.";

    /// <summary>Player bodies by tip key. A key with no row prints its seat
    /// wording to both readers.</summary>
    internal static readonly Dictionary<string, string> Bodies = new()
    {
        // Klee. Bomb and Set off kept, one sentence each; the jump and the
        // other enemies' Bombs are the seat's.
        [ArmKeywordTips.BombKey] =
            "Deals its size in [gold]Pyro[/gold] damage when "
          + "[gold]Set off[/gold], and grows " + KleeOverhaulLaw.BombGrowth
          + " each turn.",
        [ArmKeywordTips.SetOffKey] =
            "Every [gold]Bomb[/gold] on the enemy goes off, oldest first.",
        [ArmKeywordTips.MineKey] =
            "A [gold]Bomb[/gold] that also goes off when its enemy attacks you.",
        [ArmKeywordTips.OzKey] =
            "Fischl's raven. While you hold Oz, at Your Side, he hits with "
          + "[gold]Electro[/gold] each turn.",

        // Kokomi. The Plan on a Companion is the paper's own sentence.
        [ArmKeywordTips.PlanKey] =
            "Instead of the line above, play it on the "
          + "[gold]Bake-Kurage[/gold]. It happens next turn.",
        [ArmKeywordTips.PlanOnlyKey] =
            "Play the card on the [gold]Bake-Kurage[/gold]. It happens next "
          + "turn.",
        [ArmKeywordTips.PlanNoLineKey] =
            "This card has no Plan line, so it cannot be played on the "
          + "[gold]Bake-Kurage[/gold].",
        [ArmKeywordTips.CompanionPlanKey] =
            "Play it on the [gold]Bake-Kurage[/gold] to carry it out next "
          + "turn.",

        // Shared element words.
        [ArmKeywordTips.SwirlKey] =
            "[gold]Anemo[/gold] meets an aura: deal "
          + Elements.ReactionConstants.SwirlDamage
          + " unblockable damage to ALL enemies and spread that element.",
        [ArmKeywordTips.ElementalReactionKey] =
            "An element meets another element's aura on an enemy, and the "
          + "two react.",

        // Varka. Oath and Current element kept, one sentence each.
        [ArmKeywordTips.OathKey] =
            "1 Oath per element a card applies, plus 1 per element it "
          + "[gold]Swirls[/gold]. Kept all fight.",
        [ArmKeywordTips.CurrentElementKey] =
            "The last [gold]Pyro[/gold], [gold]Hydro[/gold], [gold]Cryo[/gold] "
          + "or [gold]Electro[/gold] you applied. Your [gold]Swirls[/gold] "
          + "pay out in it.",
        [ArmKeywordTips.KnightKey] =
            "One of Varka's Companions. Playing one makes its element your "
          + "current element.",

        // Furina. One merged Guest Star box (pick 3 (a)): a Guest Star card
        // drops Summon and keeps this.
        [ArmKeywordTips.SpendKey] =
            "Pay that much [gold]Fanfare[/gold]. Offered only if you have "
          + "enough.",
        [ArmKeywordTips.DrainKey] =
            "Lose N HP. After combat, up to 1/4 of your Max HP drained comes "
          + "back; [gold]Repay[/gold] the rest.",
        [ArmKeywordTips.RepayKey] =
            "Regain that much drained HP, never more than you drained.",
        [ArmKeywordTips.SummonKey] = GuestStarBody,
        [ArmKeywordTips.GuestStarKey] = GuestStarBody,
    };

    /// <summary><paramref name="seatBody"/>, or the player's words for
    /// <paramref name="key"/> when a player is reading.</summary>
    internal static string For(string key, string seatBody) =>
        !TipAudience.Seat && Bodies.TryGetValue(key, out var player)
            ? player
            : seatBody;

    /// <summary>The Spark tip, the player's way: the price and the opening
    /// bank; "no cap" and "gone after combat" are the seat's.</summary>
    internal static string SparkBody(bool openingBank) =>
        openingBank
            ? "Some cards cost [gold]Sparks[/gold] instead of Energy. Start "
              + "each combat with " + KleeOverhaulLaw.OpeningSpark + "."
            : "Some cards cost [gold]Sparks[/gold] instead of Energy.";

    /// <summary>
    /// A guest's own tip (pick 3 (a)): "the guest's sentence only where the
    /// face does not already say it". The sentence is
    /// <c>StagePerformerBadge.ActText</c>'s, a standing line then
    /// "Act: ...". A face that prints the act shows the line; a face that
    /// prints the line shows the act; a face that prints neither shows both.
    /// The seat reads the whole sentence.
    /// </summary>
    internal static string Guest(CardModel card, string full)
    {
        if (TipAudience.Seat) return full;
        var split = full.IndexOf(" Act: ", System.StringComparison.Ordinal);
        if (split < 0) return full;
        var line = full.Substring(0, split);
        var act = full.Substring(split + 1);
        var face = Face(card);
        if (face == null) return full;
        if (face.Contains("Act:", System.StringComparison.Ordinal)) return line;
        if (face.Contains(LineOpening(line), System.StringComparison.Ordinal))
            return act;
        return full;
    }

    /// <summary>A line's words up to its first number, which is what a face
    /// prints before its own <c>{GuestLine}</c> variable.</summary>
    internal static string LineOpening(string line)
    {
        for (var i = 0; i < line.Length; i++)
        {
            if (char.IsDigit(line[i])) return line.Substring(0, i);
        }
        return line;
    }

    /// <summary>The card's English face, the row the emitter wrote.</summary>
    private static string? Face(CardModel card)
    {
        if (card is not CustomCardModel custom) return null;
        var rows = custom.Localization;
        if (rows == null) return null;
        foreach (var row in rows)
        {
            if (row.Item1 == "description") return row.Item2;
        }
        return null;
    }
}
