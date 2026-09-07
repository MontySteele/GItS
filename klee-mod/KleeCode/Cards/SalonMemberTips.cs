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
        //
        // `EB-629` MOVED THREE CLAUSES DOWN HERE FROM THE RULES PARAGRAPH,
        // which had grown to about 700 characters carrying seven rules and
        // which [USER] read, in his own act-1 run, as "still a gigantic wall of
        // text". All three are facts about A MEMBER ABOUT TO PERFORM -- the
        // enemy its roll may take (`EB-425`, `EB-451`), the damage class the
        // performance belongs to (`EB-476`, `EB-548`, one rule: `EB-343`'s
        // `ValueProp.Unpowered`) and the dry cut (R220 A, `EB-587`) -- so this
        // is the tip they are read on at the moment they matter, which is what
        // the rules paragraph never was. They are one shared string
        // (<see cref="PerformanceRules"/>) rather than three copies, on
        // `SalonConstants`' own argument: a rule restated per member is a rule
        // that goes stale one member at a time.
        if (FurinaReframe.ManualLiveFor(owner))
        {
            return member switch
            {
                SalonMember.Crabaletta =>
                    $"Performs for {SalonConstants.CrabalettaTick} Hydro "
                  + $"damage, paying {SalonConstants.TickEncoreCost} Encore. "
                  + $"Evokes for {SalonConstants.CrabalettaBow} Hydro damage "
                  + "and leaves the stage. " + PerformanceRules,
                SalonMember.Usher =>
                    $"Performs for {SalonConstants.UsherTick} Block, paying "
                  + $"{SalonConstants.TickEncoreCost} Encore. Evokes for "
                  + $"{SalonConstants.UsherBow} Block and leaves the stage. "
                  + PerformanceRules,
                _ =>
                    $"Performs for {SalonConstants.ChevalmarinTick} Hydro "
                  + $"damage, paying {SalonConstants.TickEncoreCost} Encore. "
                  + "Evokes by applying Hydro to ALL enemies and granting "
                  + $"{SalonConstants.ChevalmarinBowEncore} Encore. "
                  + PerformanceRules,
            };
        }
#endif
        return ShippedBodyFor(member);
    }

    /// <summary>
    /// THE THREE CLAUSES `EB-629` MOVED OFF THE RULES PARAGRAPH, written once
    /// and appended to every member's arm tip.
    ///
    /// ONE STRING, THREE MEMBERS. The alternative was the same three sentences
    /// typed into three switch arms, which is the drift `SalonConstants` exists
    /// to prevent one level up: a rule restated per member is a rule that goes
    /// stale one member at a time.
    ///
    /// EACH SENTENCE IS A RULED FINDING AND CARRIES ITS OWN ID, so a reader
    /// asking why a clause is worded this way has the run to go to:
    ///
    ///   * THE AIM. `EB-425` put it in words after the r5 seat's play was
    ///     refused ("a card that deals damage but takes no target is not
    ///     something the face warns you about"); `EB-451` limited it after the
    ///     r7 seat's one PAID performance rolled a 6-HP Eye with Teeth that
    ///     revives at full. The implementation is `SalonMemberPower.AimPool`,
    ///     R250's shape one roller over.
    ///   * THE CLASS. `EB-476` and `EB-548`, one rule (`EB-343`): a
    ///     performance reaches `CreatureCmd.Damage` as `ValueProp.Unpowered`,
    ///     so every `IsPoweredAttack()` gate -- the Shatter mark, an enemy's
    ///     on-Attack trigger -- refuses it while `TargetMods` still reads
    ///     Vulnerable. "Not an Attack" alone is ambiguous, which is why the
    ///     sentence says which half is which; "no when-hit power fires" is
    ///     `ArmKeywordTips.ForSetOff`'s own wording.
    ///   * THE DRY CUT. R220 A and `EB-587`: three-quarters, from
    ///     <see cref="SalonConstants.DryDamageMultiplier"/> in words, because a
    ///     player pricing a performance needs the reduced number's REASON and
    ///     the strip already prints its size.
    /// </summary>
    private const string PerformanceRules =
        "It picks its own enemy, never a [gold]Minion[/gold] while another "
      + "enemy stands, and performs at three-quarters with no "
      + "[gold]Encore[/gold]. "
      + "A performance is not an [gold]Attack[/gold] and not a hit: "
      + "[gold]Vulnerable[/gold] moves it, but no [gold]Shatter[/gold] and no "
      + "when-hit power fires.";

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
        // `EB-368`. THE ARM'S SALON RULES ARE PRINTED NOWHERE ELSE, and the
        // act-2 seat played no Salon card across three fights because of it.
        // Every sentence in the shipped paragraph above is a rule the reframe
        // replaces -- members do not act on their own turn, a deploy performs
        // on the spot, a deploy onto a full stage EVOKES the front rather than
        // bowing the oldest out for its payoff, and a Companion play performs
        // the front member -- so the arm's whole engine is here, on the tip
        // both the deploy card and the stage read (D1 sec.4), stated once and
        // unable to fork.
        //
        // `EB-629` CUT IT TO THREE SENTENCES, and the reason is the shape it
        // had grown into rather than any one clause in it. [USER]'s own act-1
        // run, 2026-09-07: "still a gigantic wall of text" -- about 700
        // characters carrying seven rules, at the moment a player is deciding
        // whether to play one card. Seven rules on one tip is not seven rules
        // read; it is one tip skipped. What stays is the three a player cannot
        // act without: THE CAP, WHAT PERFORMS, and THE BONUS.
        //
        // NOTHING WAS DELETED FROM THE MOD'S TEXT. Each dropped clause moved
        // to the surface read AT THE MOMENT IT MATTERS, which for all of them
        // is a member about to perform -- i.e. the member's own tip,
        // <see cref="BodyFor"/>:
        //
        //   * THE AIM (`EB-425`, limited by `EB-451`). "A deploy card deals
        //     damage and takes no target" cost the r5 seat a refused play, and
        //     "its own choice" then cost the r7 seat the run's one PAID
        //     performance to a 6-HP Eye with Teeth that revives at full. The
        //     rule is `SalonMemberPower.PerformMember`'s roll over
        //     `AimPool`, so it belongs to a MEMBER performing and now reads on
        //     the member.
        //   * NOT AN ATTACK AND NOT A HIT (`EB-476`, `EB-548`). One rule,
        //     `EB-343`'s: a performance goes out through `ElementalHit.Deal`
        //     as `ValueProp.Unpowered`, so the Shatter mark and every on-Attack
        //     trigger refuse it while `TargetMods` still reads Vulnerable. The
        //     r13 seat called it "the most useful thing I learned and
        //     effectively invisible"; it is now on the tip of the thing that
        //     does it.
        //   * THE DRY CUT (R220 A, `EB-587`). A member with no Encore performs
        //     at three-quarters -- a fact about ONE member's next act, which is
        //     what its own tip is for.
        //
        // AND THE FRONT. "The leftmost member is the front" left with no new
        // home in text, because `EB-627` gave it a better one: chip 0 on the
        // member strip wears a highlight frame. A rule the player can SEE does
        // not need a sentence.
        if (FurinaReframe.ManualLiveFor(owner))
        {
            body =
                $"Your Salon holds {slots} members. A [gold]Companion[/gold] "
              + "card you play performs the front member; a "
              + "[gold]Deploy[/gold] performs the member it adds, and onto a "
              + "full stage it first [gold]Evokes[/gold] the front one. "
              + "Member numbers gain +1 per "
              + $"{SalonConstants.FocusPerFanfare} [gold]Fanfare[/gold] you "
              + "hold.";
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
