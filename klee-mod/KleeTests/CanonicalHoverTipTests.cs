using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Furina.Generated;
using KleeMod.Cards.Kokomi.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Exceptions;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-94 -- the hover tips a CANONICAL card could not be asked for.
///
/// <c>CardModel.Owner</c>'s GETTER calls <c>AssertMutable()</c>, so on a
/// canonical model it throws <c>CanonicalModelException</c>, and the `?.` the
/// tip builders wrote around it never helped: the throw is inside the
/// property, not in the dereference. The throw escaped the whole
/// <c>HoverTips</c> getter, so the affected cards did not lose only the salon
/// paragraph -- they lost every keyword tip they had, which is what the wire
/// read as `keywords: 0` for Endless Waltz, Dress Rehearsal and Dinner
/// Service while their neighbours returned 1.
///
/// A canonical model is exactly what the hover surfaces are handed:
/// <c>NCardLibraryGrid._Ready</c> fills the compendium out of
/// <c>ModelDb.AllCards</c>, <c>NCard.Create</c> stores that model verbatim,
/// and <c>NCardHolder.CreateHoverTips</c> reads
/// <c>CardNode.Model.HoverTips</c> off it on every hover.
///
/// WHY THIS TEST WAS PREVIOUSLY IMPOSSIBLE. README's headless boundary lists
/// "a canonical CardModel's Owner getter throws" as EB-94 met from the test
/// side: any test that reached the owner read from a freshly constructed card
/// hit the defect itself. The fix is what makes the test writable.
///
/// WHAT IS STILL WIRE-ONLY. Enumerating <c>ExtraHoverTips</c> end to end is
/// NOT reachable here and is not faked past: every yielded <c>HoverTip</c>
/// formats a <c>LocString</c> title through <c>LocManager.Instance</c>, which
/// is null until the game boots (<c>LocManager.Initialize</c> reaches
/// <c>SaveManager.Instance</c>). So the acceptance "the three named cards
/// return their keyword on the wire" needs the next deploy. What IS reachable
/// -- and is what actually threw -- is the OWNER READ and the body builders
/// hanging off it, invoked on the real canonical models, plus a class-wide
/// gate that no tip body reaches the asserting getter again.
/// </summary>
public class CanonicalHoverTipTests
{
    // The three cards the wire measured at `keywords: 0`. Two route through
    // SalonMemberTips, one through FurinaRiderTips -- the SAME defect in two
    // files, which is why the row's "FurinaRiderTips is not affected on the
    // evidence available" did not survive its own evidence.
    private static DressRehearsal Rehearsal() => new();

    private static EndlessWaltz Waltz() => new();

    private static DinnerService Dinner() => new();

    private static string Invoke(
        System.Type owner, string method, params object[] args)
    {
        var m = owner
            .GetMethods(HeadlessGame.All)
            .Single(candidate =>
                candidate.Name == method
                && candidate.GetParameters().Length == args.Length
                && candidate.GetParameters()[0].ParameterType == typeof(CardModel));
        return (string)m.Invoke(null, args)!;
    }

    // --- the models really are the ones the compendium hands over ----------

    [Fact]
    public void A_freshly_constructed_card_is_the_canonical_prototype()
    {
        // The guard on every assertion below: if construction ever started
        // producing MUTABLE models, these tests would keep passing while
        // testing nothing. `ModelDb.ToMutable` is outside the boundary, so a
        // fresh instance is the only canonical card a test can hold, and it is
        // the same flag state `ModelDb.AllCards` hands the card library.
        Assert.True(Rehearsal().IsCanonical);
        Assert.True(Waltz().IsCanonical);
        Assert.True(Dinner().IsCanonical);
        Assert.False(Dinner().IsMutable);
    }

    [Fact]
    public void The_owner_getter_still_throws_on_a_canonical_model()
    {
        // The defect's MECHANISM, pinned on the game's own type rather than
        // argued from the decompile. If a game update ever makes the getter
        // non-asserting, this fails and the workaround below can be retired
        // deliberately instead of rotting in place.
        var card = Rehearsal();

        Assert.Throws<CanonicalModelException>(() => _ = card.Owner);
    }

    // --- the fix -----------------------------------------------------------

    [Fact]
    public void The_tip_owner_read_answers_null_instead_of_throwing()
    {
        Assert.Null(TipOwner.CreatureOf(Rehearsal()));
        Assert.Null(TipOwner.CreatureOf(Waltz()));
        Assert.Null(TipOwner.CreatureOf(Dinner()));
        Assert.Null(TipOwner.CreatureOf(null));
    }

    [Fact]
    public void The_tip_owner_read_still_answers_the_seat_on_an_owned_card()
    {
        // The mutation guard on the fix. Returning null unconditionally would
        // pass every test above and silently delete the LIVE half of every
        // rider tip -- the "you hold N Fanfare" / "you have N on stage" clause
        // that is the whole reason these bodies ask for an owner at all.
        var seat = Seat.Furina().WithCombatState();
        var card = Rehearsal();
        Seat.Set(card, "IsMutable", true);
        card.Owner = seat.Player;

        Assert.Same(seat.Creature, TipOwner.CreatureOf(card));
    }

    // --- the bodies that threw --------------------------------------------

    [Fact]
    public void Endless_waltz_builds_its_salon_rules_paragraph_when_canonical()
    {
        var body = Invoke(typeof(SalonMemberTips), "SalonRulesBody", Waltz());

        Assert.Contains("Salon holds", body);
        Assert.Contains("bows the OLDEST member out", body);
        // No owner means no live stage clause, which is the correct copy for a
        // compendium entry: there is no board to report on.
        Assert.DoesNotContain("on stage.", body);
    }

    [Fact]
    public void Dress_rehearsal_builds_its_salon_rules_paragraph_when_canonical()
    {
        var body = Invoke(typeof(SalonMemberTips), "SalonRulesBody", Rehearsal());

        Assert.Contains("Salon holds", body);
        Assert.Contains("leftmost member", body);
    }

    [Fact]
    public void Dinner_service_builds_its_salon_rider_paragraph_when_canonical()
    {
        // The third card on the wire, and the one that proves the defect was
        // never confined to SalonMemberTips: Dinner Service carries no salon
        // member, it carries a FurinaRiderTips salon SCALER (+2 Block per
        // member), and that body read the same asserting getter.
        var body = Invoke(
            typeof(FurinaRiderTips), "SalonBody", Dinner(), 2, true);

        Assert.Equal("+2 Block per Salon member on stage.", body);
    }

    [Fact]
    public void Bake_kurage_builds_its_pulse_paragraph_when_canonical()
    {
        // KokomiRiderTips is the same defect one character over; it was fixed
        // in the same pass rather than left as a second row.
        var body = Invoke(typeof(KokomiRiderTips), "PulseBody", new BakeKurage());

        Assert.False(string.IsNullOrWhiteSpace(body));
    }

    // --- the class-wide gate ----------------------------------------------

    [Fact]
    public void No_hover_tip_body_reads_the_asserting_owner_getter()
    {
        // STRUCTURAL, and labelled: this reads call sets, not behaviour. It is
        // the part that keeps the fix from being undone one tip at a time --
        // `card.Owner?.Creature` reads as safe and is not, so the ban has to
        // be mechanical rather than a comment.
        var types = new[]
        {
            typeof(SalonMemberTips), typeof(FurinaRiderTips),
            typeof(KokomiRiderTips), typeof(KleeCardTooltips),
        };

        foreach (var type in types)
        {
            foreach (var method in type.GetMethods(HeadlessGame.All))
            {
                Assert.DoesNotContain(
                    "CardModel.get_Owner",
                    Il.Calls(method));
            }
        }
    }
}
