using System.Collections.Generic;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// Legibility sprint, Track L-C (text re-homing). Once a rider renders inside
/// the card's own number (CalculatedDamageVar), restating the arithmetic in
/// the rules text is duplicate bookkeeping -- the face already shows the
/// answer, live and greened. The face keeps a SHORT marker naming the
/// mechanism, so a card read on a reward screen still declares that it
/// scales, and the arithmetic moves here, where it can additionally say what
/// the rider is worth right now.
///
/// `ExtraHoverTips` is evaluated when the card is inspected, so these numbers
/// are live -- the same property KleeCardTooltips uses for its board-aware
/// reaction previews.
///
/// On the API: `HoverTipFactory`'s entry points are all typed (FromKeyword,
/// FromPower, FromPotion, FromOrb, FromEnchantment, FromAffliction), which is
/// why a shared keyword tip cannot carry a per-card rate. `HoverTip` itself,
/// however, has a `(LocString title, string description)` constructor -- free
/// text for the body, so no custom IHoverTip implementation is needed. Only
/// the title needs a loc row; those ship beside the custom-keyword fallbacks
/// in KleeMod.InjectLocStrings under the same KLEEMOD- prefix.
/// </summary>
public static class FurinaRiderTips
{
    private const string Table = "card_keywords";

    public const string FanfareKey = "KLEEMOD-FANFARE_RIDER";
    public const string AuraKey = "KLEEMOD-AURA_RIDER";
    public const string SalonKey = "KLEEMOD-SALON_RIDER";
    public const string CompanionKey = "KLEEMOD-COMPANION_RIDER";

    // `EB-475`. THREE WORDS THAT GATED DECISIONS AND WERE DEFINED NOWHERE.
    //
    // THE FIND (Furina r9 (c) 2). "'If you moved the Spotlight this turn'
    // gates Director's Cut and Take It From the Top, and nothing ever defines
    // what moving the Spotlight is. Ethereal Spotlight's own buff says 'Lasts
    // until the Spotlight moves,' which restates the phrase instead of
    // explaining it. I passed on both cards purely because I could not tell
    // whether I could turn the condition on." Then "'Guest Stars' ... appears
    // inside Blocking Notes' scaling clause", undefined; and "'Take Your Bow
    // -- The leftmost member of your Salon takes their bow' was offered as a
    // card reward with no keyword, no number, and no glossary line. I could
    // guess it means Evoke, but I declined a 0-cost card because I could not
    // read it."
    //
    // ATTACHED FROM THE FACE THAT PRINTS THE WORD, `EB-272`'s rule one sheet
    // over: the first and third are DERIVED by `gen_klee_cards` from the built
    // description, so a row that prints either phrase tomorrow carries the
    // definition because it printed the phrase. The Guest Star row is the
    // exception and says why at its own attach point.
    public const string SpotlightMoveKey = "KLEEMOD-SPOTLIGHT_MOVE";
    public const string GuestStarKey = "KLEEMOD-GUEST_STAR";
    public const string BowKey = "KLEEMOD-TAKES_BOW";

    /// <summary>
    /// `EB-475`, the first word. What MOVES the Spotlight, and whether it has
    /// moved right now -- the house shape of this file (the rule, then what it
    /// is worth at this moment), because the question the seat could not
    /// answer was "can I turn the condition on".
    ///
    /// <see cref="SpotlightSystem.Designate"/> is the ONLY writer of the mark
    /// and <c>Ethereal Spotlight</c> is its only caller, and
    /// <see cref="SpotlightSystem.ResetTurn"/> clears it from Furina's
    /// <c>AfterPlayerTurnStart</c> -- so the mark is this turn's, and the
    /// sequencing the tip is really about is "play the selector first".
    /// </summary>
    public static IEnumerable<IHoverTip> ForSpotlightMove(
        IEnumerable<IHoverTip> inherited, CardModel card)
    {
        foreach (var tip in inherited) yield return tip;
        yield return new HoverTip(
            new LocString(Table, SpotlightMoveKey + ".title"),
            SpotlightMoveBody(card));
    }

    /// <summary>
    /// `EB-475`, the third word, and the one the seat declined a free card
    /// over. A bow is the payoff: the member LEAVES the stage and fires its
    /// own line (<see cref="SalonMemberPower.BowLeftmost"/>). The three
    /// payoffs are interpolated from the constants that pay them, so a retune
    /// cannot leave this sentence quoting a retired number (`EB-89`).
    /// </summary>
    public static IEnumerable<IHoverTip> ForBow(
        IEnumerable<IHoverTip> inherited, CardModel card)
    {
        foreach (var tip in inherited) yield return tip;
        yield return new HoverTip(
            new LocString(Table, BowKey + ".title"), BowBody(card));
    }

    public static IEnumerable<IHoverTip> ForCard(
        IEnumerable<IHoverTip> inherited,
        CardModel card,
        int fanfarePer = 0,
        int fanfareStep = 0,
        bool grantsBlock = false,
        int auraBonus = 0,
        int salonPer = 0,
        bool salonGrantsBlock = false,
        int companionPer = 0)
    {
        foreach (var tip in inherited) yield return tip;

        if (fanfareStep > 0)
        {
            yield return new HoverTip(
                new LocString(Table, FanfareKey + ".title"),
                FanfareBody(card, fanfarePer, fanfareStep, grantsBlock));
        }

        if (auraBonus > 0)
        {
            yield return new HoverTip(
                new LocString(Table, AuraKey + ".title"),
                $"+{auraBonus} damage against an enemy that carries an "
              + "elemental aura. Hover an enemy to see this card's number "
              + "for that target.");
        }

        if (salonPer > 0)
        {
            yield return new HoverTip(
                new LocString(Table, SalonKey + ".title"),
                SalonBody(card, salonPer, salonGrantsBlock));
        }

        if (companionPer > 0)
        {
            yield return new HoverTip(
                new LocString(Table, CompanionKey + ".title"),
                CompanionBody(card, companionPer));
            // `EB-475`, the second word, and the ONE of the three whose attach
            // is not derived from the card's own description -- because no
            // card face prints it. `Guest Star` reaches the player inside
            // `CompanionBody`'s clause ("including Guest Stars"), which is
            // exactly where the r9 seat met it: "it appears inside Blocking
            // Notes' scaling clause". The attach is therefore the tip that
            // prints the word, which is the same rule stated about the same
            // surface.
            yield return new HoverTip(
                new LocString(Table, GuestStarKey + ".title"),
                "A [gold]Companion[/gold] card created into your hand during "
              + "a fight rather than drafted into your deck. It counts as a "
              + "Companion card played, and it is gone when the fight ends.");
        }
    }

    /// <summary>`EB-475`. The rule, then whether it is on right now.</summary>
    private static string SpotlightMoveBody(CardModel card)
    {
        var rule = "Playing [gold]Ethereal Spotlight[/gold] moves it, and "
                 + "nothing else does. The mark clears at the start of your "
                 + "turn, so a card asking this wants the Spotlight played "
                 + "first, this turn.";
        var owner = TipOwner.CreatureOf(card);
        if (owner == null || card.CombatState == null) return rule;
        return SpotlightSystem.MovedThisTurn(owner)
            ? $"{rule} You HAVE moved it this turn."
            : $"{rule} You have NOT moved it this turn.";
    }

    /// <summary>`EB-475`. What a bow is, and whether there is anyone to take
    /// one. The stage read is <see cref="SalonBody"/>'s, one verb over.
    /// </summary>
    private static string BowBody(CardModel card)
    {
        var rule = "The member leaves the stage and fires its payoff: "
                 + $"Crabaletta deals {SalonConstants.CrabalettaBow} Hydro "
                 + $"damage, the Usher gains {SalonConstants.UsherBow} Block, "
                 + "Chevalmarin applies Hydro to ALL enemies and grants "
                 + $"{SalonConstants.ChevalmarinBowEncore} Encore.";
        var owner = TipOwner.CreatureOf(card);
        if (owner == null || card.CombatState == null) return rule;
        var member = SalonMemberPower.LeftmostMember(owner);
        return member is { } who
            ? $"{rule} {SalonMemberTips.DisplayName(who)} is leftmost and "
            + "would take it."
            : $"{rule} Your stage is empty, so this bows nobody.";
    }

    /// <summary>The rate, plus what it is worth at this moment. Out of combat
    /// (deck view, reward screen) there is no meter to read, so the rate
    /// stands alone rather than printing a misleading zero.</summary>
    private static string FanfareBody(
        CardModel card, int per, int step, bool grantsBlock)
    {
        var noun = grantsBlock ? "Block" : "damage";
        var rate = $"+{per} {noun} per {step} Fanfare you hold.";
        var owner = TipOwner.CreatureOf(card);
        if (owner == null || card.CombatState == null) return rate;

        var fanfare = FurinaResources.ReadableFanfare(owner);
        return $"{rate} You hold {fanfare} Fanfare: +{fanfare / step * per} "
             + $"{noun}, already counted in the number above.";
    }

    /// <summary>A13/A14: the per-member slope, plus what the stage is paying
    /// right now. Says "on stage" rather than naming the meter, because the
    /// thing being counted is visible -- the members are standing there --
    /// and the whole point of the rework is that the pilot can watch each
    /// deploy move this number.</summary>
    private static string SalonBody(CardModel card, int per, bool grantsBlock)
    {
        var noun = grantsBlock ? "Block" : "damage";
        var rate = $"+{per} {noun} per Salon member on stage.";
        var owner = TipOwner.CreatureOf(card);
        if (owner == null || card.CombatState == null) return rate;

        var members = SalonMemberPower.Count(owner);
        if (members == 0)
        {
            return $"{rate} Your stage is empty, so this card is paying "
                 + "nothing extra right now.";
        }
        return $"{rate} You have {members} on stage: +{members * per} {noun}, "
             + "already counted in the number above.";
    }

    /// <summary>Fanfare rework Track C.3 (2026-07-28): Blocking Notes'
    /// Companion tempo. Same shape as SalonBody -- the rate, then what it is
    /// worth right now -- because the thing being counted is a fact about
    /// THIS TURN and the player needs to know whether playing the Companion
    /// first is worth the sequencing.
    ///
    /// The count INCLUDES Guest Star token plays. That is the ruling and it
    /// is worth the tip saying so, because a generated Companion does not
    /// look like a drafted one and a player who assumed otherwise would
    /// mis-sequence the whole turn.</summary>
    private static string CompanionBody(CardModel card, int per)
    {
        var rate = $"+{per} Block per Companion card you have played this "
                 + "turn, including Guest Stars.";
        var owner = TipOwner.CreatureOf(card);
        if (owner == null || card.CombatState == null) return rate;

        var plays = CurtainCallHooks.CompanionPlaysThisTurn(owner);
        if (plays == 0)
        {
            return $"{rate} You have played none this turn, so this card is "
                 + "paying nothing extra right now.";
        }
        return $"{rate} You have played {plays}: +{plays * per} Block, "
             + "already counted in the number above.";
    }
}
