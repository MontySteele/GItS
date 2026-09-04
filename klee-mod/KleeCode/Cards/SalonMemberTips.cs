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
#if PROTOTYPE_CARDS
        // `EB-384`. THE MEMBER'S OWN TIP SAYS WHAT A PERFORMANCE PAYS, because
        // under the arm a deploy card's damage is the entering member's and
        // the card face prints none of it. The round-two seat watched
        // Overflowing Hospitality -- a card whose face is one deploy line --
        // take an enemy for 1 in one fight and 2 in another and called both
        // unexplained. Both were this member: the printed 2, and the
        // three-quarters cut of it on the turn the stage could not pay.
        //
        // "EACH TURN" IS THE CLAUSE THAT HAD TO GO. It is the shipped upkeep,
        // which the MANUAL leg deletes, so every member tip on the screen was
        // contradicting the Salon rules tip printed directly under it
        // (`SalonRulesBody`, whose own arm branch is `EB-368`'s). Same defect
        // as `EB-383`'s buff, one surface over.
        if (FurinaReframe.ManualLiveFor(owner))
        {
            return member switch
            {
                SalonMember.Crabaletta =>
                    $"Performs for {SalonConstants.CrabalettaTick} Hydro "
                  + $"damage, paying {SalonConstants.TickEncoreCost} Encore. "
                  + $"Evokes for {SalonConstants.CrabalettaBow} Hydro damage "
                  + "and leaves the stage.",
                SalonMember.Usher =>
                    $"Performs for {SalonConstants.UsherTick} Block, paying "
                  + $"{SalonConstants.TickEncoreCost} Encore. Evokes for "
                  + $"{SalonConstants.UsherBow} Block and leaves the stage.",
                _ =>
                    $"Performs for {SalonConstants.ChevalmarinTick} Hydro "
                  + $"damage, paying {SalonConstants.TickEncoreCost} Encore. "
                  + "Evokes by applying Hydro to ALL enemies and granting "
                  + $"{SalonConstants.ChevalmarinBowEncore} Encore.",
            };
        }
#endif
        return ShippedBodyFor(member);
    }

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

#if PROTOTYPE_CARDS
        // `EB-368`. THE ARM'S THREE SALON RULES ARE PRINTED NOWHERE, and the
        // act-2 seat played no Salon card across three fights because of it.
        // Every sentence above is a SHIPPED rule the reframe replaces: members
        // do not act on their own turn, a deploy performs on the spot, a
        // deploy onto a full stage EVOKES the front rather than bowing the
        // oldest out for its payoff, and a Companion play performs the front
        // member -- the arm's whole engine, and none of it on any face.
        //
        // The branch is here rather than on the two deploy faces because this
        // is the tip both the deploy card and the stage hover read (D1 §4), so
        // the rules are stated once and cannot fork. The faces carry their own
        // clause too; this is the paragraph behind the word.
        //
        // `EB-425` ADDED THE AIM. A deploy card DEALS DAMAGE and TAKES NO
        // TARGET, and the first place the r5 seat learned that was a refusal:
        // "the first thing I tried was `play "Salon Debut" on "Corpse Slug
        // (1)"` and it was refused... the card's own reminder text says the
        // member `Performs for 6 Hydro damage`, and a card that deals damage
        // but takes no target is not something the face warns you about. The
        // Salon picked slug 2 on its own. I never got to choose a member's
        // target all round." The rule is `SalonPowers.PerformMember`'s, which
        // draws the body from `Rng.CombatTargets` over `HittableEnemies` and
        // is the only implementation of a member acting -- so the sentence is
        // about every performance and not about one card, which is why it is
        // here and not on Salon Debut's face. In the `Deploy` tip's words: a
        // member performs, and the enemy it performs on is its own choice.
        //
        // THE `Deploy` KEYWORD TIP COULD NOT TAKE IT. That word is 132 of its
        // 135-character ceiling carrying `EB-368`'s three rules, and this
        // clause is 39; the paragraph behind the word has the room, is printed
        // on the same card, and is where the other four rules already live.
        //
        // `EB-451` PUT THE LIMIT ON THE AIM. "Its own choice" was true and
        // still cost the r7 seat the run's one PAID performance: the roll took
        // the 6-HP Eye with Teeth, which revives at full, while the body that
        // mattered stood beside it. The roll now skips a Minion while a
        // non-Minion stands (`SalonMemberPower.AimPool`, R250's shape one roller
        // over), and the sentence that describes the aim is the sentence that
        // says so.
        if (FurinaReframe.ManualLiveFor(owner))
        {
            body =
                $"Your Salon holds {slots} members. Members do NOT act on "
              + "their own. A [gold]Companion[/gold] card you play performs "
              + "the front member; a [gold]Deploy[/gold] performs the member "
              + "it fields at once; deploying onto a full stage "
              + "[gold]Evokes[/gold] the front member first. The leftmost "
              + "member is the front. A performing member picks its own "
              + "enemy, never a [gold]Minion[/gold] while another enemy "
              + "stands. Member numbers gain +1 per "
              + $"{SalonConstants.FocusPerFanfare} Fanfare you hold, and a "
              + "member with no Encore to spend performs at three-quarters.";
        }
#endif

        if (owner == null) return body;

        var onStage = SalonMemberPower.Count(owner);
        if (onStage < slots) return $"{body} You have {onStage} on stage.";
        var full = "Your stage is FULL: the next deploy bows someone out.";
#if PROTOTYPE_CARDS
        // `EB-368`. The live half of the same sentence: under the arm a full
        // stage is a REWARD (the free Evoke), not a cost, and telling a seat
        // it is about to lose a member for a payoff it does not get is how the
        // round-two seat learned to stop deploying.
        if (FurinaReframe.ManualLiveFor(owner))
        {
            full = "Your stage is FULL: the next deploy [gold]Evokes[/gold] "
                 + "the front member first.";
        }
#endif
        return $"{body} {full}";
    }
}
