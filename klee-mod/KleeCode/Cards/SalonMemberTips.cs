using System.Collections.Generic;
using System.Linq;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
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

        // `EB-384`: asked ONCE, and through the same accessor `SalonRulesBody`
        // uses -- `card.Owner` throws on a canonical model (`EB-94`), and the
        // two tips on one card must agree about whose stage they describe.
        var owner = TipOwner.CreatureOf(card);
        foreach (var member in shown)
        {
            yield return new HoverTip(
                new LocString(Table, KeyFor(member) + ".title"),
                BodyFor(member, owner));
        }

        if (shown.Length > 0)
        {
            yield return new HoverTip(
                new LocString(Table, SalonRulesKey + ".title"),
                SalonRulesBody(card));
        }
    }

    /// <summary>
    /// `EB-488`. THE SALON RULES ON A FACE THAT NAMES A MEMBER AND DEPLOYS
    /// NONE.
    ///
    /// THE FIND (Furina r10 (c) 5). <i>Grand Salon</i> -- "Salon Member
    /// numbers are 1 higher" -- was the run's FIRST reward, offered on a
    /// screen with no glossary for the words it is written in, and the seat
    /// passed on it partly because it could not price it. The Salon tip had
    /// appeared exactly once all run, on <i>Salon Debut</i> in fight 1.
    ///
    /// WHY IT WAS MISSING. <see cref="ForCard"/> attaches from the EFFECT --
    /// which member does this card deploy -- and that is right for the member
    /// paragraphs: a card that fields nobody must not print three of them.
    /// But the RULES paragraph is about the word, and a face that prints
    /// "Salon Member" and deploys none is exactly the face whose reader has
    /// never met the word. So this attaches from the PRINTED WORD, which is
    /// `ArmKeywordTips`' own bargain (`gen_klee_cards.emit` derives it from
    /// the row's built description) and the way the Companion tip already
    /// reaches a reward screen.
    ///
    /// NOT ON A DEPLOY CARD, which already carries this same paragraph
    /// through <see cref="ForCard"/>; the generator excludes them, because two
    /// copies of one definition on one face is what the game's own tip
    /// de-duplication would then be picking between.
    /// </summary>
    public static IEnumerable<IHoverTip> ForSalonRules(
        IEnumerable<IHoverTip> inherited, CardModel card)
    {
        foreach (var tip in inherited) yield return tip;
        yield return new HoverTip(
            new LocString(Table, SalonRulesKey + ".title"),
            SalonRulesBody(card));
    }

    /// <summary>Public because the salon STAGE shares this tooltip source
    /// verbatim (D1 §4): the per-slot hover on the stage and the keyword tip
    /// on a deploy card must be the same copy, not two that agree today.
    /// </summary>
    public static string KeyFor(SalonMember member) => member switch
    {
        SalonMember.Crabaletta => CrabalettaKey,
        SalonMember.Usher => UsherKey,
        _ => ChevalmarinKey,
    };

    // EB-155. Named constants rather than three literals inside the switch
    // above, for the same reason the rule that reads them exists: R20 sweeps
    // this assembly's `KLEEMOD-` keyword CONSTANTS for a `.title` row, and a
    // key that is only ever a literal in a method body is a key that sweep
    // cannot see. Raw keys have reached live builds twice from that blind spot.
    public const string CrabalettaKey = "KLEEMOD-SALON_CRABALETTA";
    public const string UsherKey = "KLEEMOD-SALON_USHER";
    public const string ChevalmarinKey = "KLEEMOD-SALON_CHEVALMARIN";

    /// <summary>What this member does on stage and on the way out. Numbers
    /// come from SalonConstants, so a repricing cannot leave the tooltip
    /// telling the player a retired number.</summary>
    /// <param name="owner">Whose stage this tip is about. `EB-384`: the arm's
    /// branch below is character-scoped like every other reframe seam, so the
    /// owner is asked rather than the bare flag -- in co-op the other seat may
    /// be Klee, and a Furina tip is not the place to invent a roster-wide
    /// branch. `null` (no owner reachable, which is what a canonical
    /// compendium copy gives) is the SHIPPED wording, the same way
    /// <see cref="SalonRulesBody(Creature?)"/> falls back to the printed cap.
    /// </param>
    public static string BodyFor(SalonMember member, Creature? owner = null)
    {
        return ShippedBodyFor(member);
    }

    /// <summary>
    /// THE CLAUSES `EB-629` MOVED OFF THE RULES PARAGRAPH, split by `EB-632`
    /// so that each member's tip carries only its own.
    ///
    /// WHAT `EB-632` FOUND (GPT review, 2026-09-07). `EB-629` shrank the Salon
    /// rules paragraph by moving three clauses onto the member tips, and wrote
    /// them as ONE shared string appended to all three members. Two of the
    /// three are facts about DEALING DAMAGE -- which enemy the roll takes, and
    /// which damage class the hit belongs to -- and the Usher deals none: he
    /// gains <see cref="SalonConstants.UsherTick"/> Block. So his tip was
    /// carrying an enemy-selection rule that never runs for him and a Shatter
    /// exception he can never be on either side of. The wall had moved rather
    /// than shrunk, one member over.
    ///
    /// SO THERE ARE TWO STRINGS AND NOT THREE COPIES.
    /// <see cref="DamagePerformanceRules"/> is the pair that belongs to a
    /// member whose performance is a hit; <see cref="DryCut"/> is the one that
    /// belongs to every member, because every member can be dry. The
    /// per-member switch below picks between them and no sentence is typed
    /// twice -- which is `SalonConstants`' own argument one level up: a rule
    /// restated per member is a rule that goes stale one member at a time.
    ///
    /// EACH SENTENCE IS A RULED FINDING AND CARRIES ITS OWN ID, so a reader
    /// asking why a clause is worded this way has the run to go to:
    ///
    ///   * THE AIM. `EB-425` put it in words after the r5 seat's play was
    ///     refused ("a card that deals damage but takes no target is not
    ///     something the face warns you about"); `EB-451` limited it after the
    ///     r7 seat's one PAID performance rolled a 6-HP Eye with Teeth that
    ///     revives at full. The implementation is `SalonMemberPower.AimPool`,
    ///     R250's shape one roller over -- and it is reached only from the
    ///     damage branch, which is the code half of this split.
    ///   * THE CLASS. `EB-476` and `EB-548`, one rule (`EB-343`): a
    ///     performance reaches `CreatureCmd.Damage` as `ValueProp.Unpowered`,
    ///     so every `IsPoweredAttack()` gate -- the Shatter mark, an enemy's
    ///     on-Attack trigger -- refuses it while `TargetMods` still reads
    ///     Vulnerable. "Not an Attack" alone is ambiguous, which is why the
    ///     sentence says which half is which; "no when-hit power fires" is
    ///     `ArmKeywordTips.ForSetOff`'s own wording.
    /// </summary>
    private const string DamagePerformanceRules =
        "It picks its own enemy, never a [gold]Minion[/gold] while another "
      + "enemy stands. "
      + "A performance is not an [gold]Attack[/gold] and not a hit: "
      + "[gold]Vulnerable[/gold] moves it, but no [gold]Shatter[/gold] and no "
      + "when-hit power fires.";

    /// <summary>
    /// THE DRY CUT, and it is on ALL THREE MEMBERS because all three can be
    /// asked to perform with an empty buffer. R220 A and `EB-587`:
    /// three-quarters, from <see cref="SalonConstants.DryDamageMultiplier"/>
    /// in words, because a player pricing a performance needs the reduced
    /// number's REASON and the strip already prints its size.
    ///
    /// `EB-633` is the other half of the same sentence, one surface over: the
    /// pip row counts FULL-STRENGTH performances, so a row at zero does not
    /// mean the stage is idle, and this is where the tip says so.
    /// </summary>
    private const string DryCut =
        "With no [gold]Encore[/gold] it performs at three-quarters.";

    /// <summary>The shipped upkeep's wording, unmoved and unreachable from the
    /// arm's branch, so a release build's tip is the same expression it has
    /// always been.</summary>
    private static string ShippedBodyFor(SalonMember member) => member switch
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
    ///
    /// EB-94: the owner goes through <see cref="TipOwner"/>. Reading
    /// `card.Owner` directly threw on a canonical model -- which is what the
    /// compendium hands this property -- and took the card's whole tip set
    /// with it.
    /// </summary>
    private static string SalonRulesBody(CardModel card) =>
        SalonRulesBody(TipOwner.CreatureOf(card));

    /// <summary>Creature overload: the stage hover (D1 §4) has no card to
    /// ask, and the copy must not fork.</summary>
    public static string SalonRulesBody(Creature? owner)
    {
        var slots = owner == null
            ? SalonConstants.MemberSlots
            : SalonMemberPower.SlotsFor(owner);

        var body =
            $"Your Salon holds {slots} members. Deploying into a full stage "
          + "bows the OLDEST member out for its payoff. The leftmost member "
          + "bows first. Member numbers gain +1 per "
          + $"{SalonConstants.FocusPerFanfare} Fanfare you hold; a member "
          + "with no Encore to spend acts at three-quarters.";


        if (owner == null) return body;

        var onStage = SalonMemberPower.Count(owner);
        if (onStage < slots) return $"{body} You have {onStage} on stage.";
        var full = "Your stage is FULL: the next deploy bows someone out.";
        return $"{body} {full}";
    }
}
