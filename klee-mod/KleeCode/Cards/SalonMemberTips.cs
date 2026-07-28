using System.Collections.Generic;
using System.Linq;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// B5 (playtest-2 defect, 2026-07-28). Eight salon-deploy cards rendered the
/// same boilerplate -- "Add 1 typed Salon Member(s). Maximum 3; a full stage
/// bows its OLDEST member out..." -- which named no member and reprinted the
/// cap rules on every copy. A player holding Gentilhomme Usher could not tell
/// from the card what the Usher actually did.
///
/// Ruled grammar: the FACE names who takes the stage, the member's abilities
/// move to a tooltip, and the cap paragraph leaves the face entirely.
///
/// The bodies are BUILT HERE rather than shipped as static loc text, for two
/// reasons that are really the same reason:
///
///   * the member numbers live in SalonConstants, and a hand-written string
///     restating them is a copy that goes stale the first time a tick is
///     repriced -- exactly the drift the constant-parity gate exists to catch
///     between the engines, reintroduced inside one of them;
///   * the CAP is a per-player stat since A12, so "Maximum 3" is not a fact
///     about the game any more. It is a fact about this player right now, and
///     only live code can say it.
///
/// Only the titles need loc rows; those ship beside the rider-tip titles in
/// KleeMod.InjectLocStrings under the same KLEEMOD- prefix.
/// </summary>
public static class SalonMemberTips
{
    private const string Table = "card_keywords";

    public const string SalonRulesKey = "KLEEMOD-SALON_RULES";

    /// <summary>The member's stage name, as the card face prints it.</summary>
    public static string DisplayName(SalonMember member) => member switch
    {
        SalonMember.Crabaletta => "Mademoiselle Crabaletta",
        SalonMember.Usher => "Gentilhomme Usher",
        SalonMember.Chevalmarin => "Surintendante Chevalmarin",
        _ => "Salon Member",
    };

    public static IEnumerable<IHoverTip> ForCard(
        IEnumerable<IHoverTip> inherited,
        CardModel card,
        SalonMember[]? members = null,
        bool randomMember = false)
    {
        foreach (var tip in inherited) yield return tip;

        // A random deploy can field ANY member, so it earns all three tips --
        // the player is choosing to roll, and needs to know what they might
        // get. Distinct() so a card that deploys two of the same member does
        // not print the same paragraph twice.
        var shown = randomMember
            ? new[]
            {
                SalonMember.Crabaletta, SalonMember.Usher,
                SalonMember.Chevalmarin,
            }
            : (members ?? System.Array.Empty<SalonMember>()).Distinct().ToArray();

        foreach (var member in shown)
        {
            yield return new HoverTip(
                new LocString(Table, KeyFor(member) + ".title"),
                BodyFor(member));
        }

        if (shown.Length > 0)
        {
            yield return new HoverTip(
                new LocString(Table, SalonRulesKey + ".title"),
                SalonRulesBody(card));
        }
    }

    private static string KeyFor(SalonMember member) => member switch
    {
        SalonMember.Crabaletta => "KLEEMOD-SALON_CRABALETTA",
        SalonMember.Usher => "KLEEMOD-SALON_USHER",
        _ => "KLEEMOD-SALON_CHEVALMARIN",
    };

    /// <summary>What this member does on stage and on the way out. Numbers
    /// come from SalonConstants, so a repricing cannot leave the tooltip
    /// telling the player a retired number.</summary>
    private static string BodyFor(SalonMember member) => member switch
    {
        SalonMember.Crabaletta =>
            $"Each turn, spends {SalonConstants.TickEncoreCost} Encore to deal "
          + $"{SalonConstants.CrabalettaTick} Hydro damage. Bows out for "
          + $"{SalonConstants.CrabalettaBow} Hydro damage.",
        SalonMember.Usher =>
            $"Each turn, spends {SalonConstants.TickEncoreCost} Encore to gain "
          + $"{SalonConstants.UsherTick} "
          + $"Block. Bows out for {SalonConstants.UsherBow} Block.",
        _ =>
            $"Each turn, spends {SalonConstants.TickEncoreCost} Encore to deal "
          + $"{SalonConstants.ChevalmarinTick} Hydro damage. Bows out by "
          + "applying Hydro to ALL enemies and granting "
          + $"{SalonConstants.ChevalmarinBowEncore} Encore.",
    };

    /// <summary>The cap rules the faces no longer carry. The slot count is
    /// read LIVE off the owner (A12 made it a stat), and the bow-order line
    /// is the D1 ruling: with summon order guaranteed, position IS the
    /// signal, so the keyword teaches it instead of a marker on the stage.
    /// </summary>
    private static string SalonRulesBody(CardModel card)
    {
        var owner = card.Owner?.Creature;
        var slots = owner == null
            ? SalonConstants.MemberSlots
            : SalonMemberPower.SlotsFor(owner);

        var body =
            $"Your Salon holds {slots} members. Deploying into a full stage "
          + "bows the OLDEST member out for its payoff -- the leftmost member "
          + "is always the next to bow. Member numbers gain +1 per "
          + $"{SalonConstants.FocusPerFanfare} Fanfare you hold; a member "
          + "with no Encore to spend acts at three-quarters.";

        if (owner == null) return body;

        var onStage = SalonMemberPower.Count(owner);
        return onStage >= slots
            ? $"{body} Your stage is FULL: the next deploy bows someone out."
            : $"{body} You have {onStage} on stage.";
    }
}
