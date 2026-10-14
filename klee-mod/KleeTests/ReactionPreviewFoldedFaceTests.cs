using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Elements;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE KOKOMI SEATS (2026-10-14): a Chevreuse card's tip read "Reaction
/// preview: Vaporize ... lands 31" and the hit into a Hydro Ovicopter dealt 21.
///
/// The face is a <c>FrontFoldedDamageVar</c>: it folds the FRONT enemy's
/// target terms -- that body's Vaporize amplifier included -- into the number
/// it prints, so 14 printed 21. The tip's last branch then took that 21 and
/// multiplied the 1.5x in again for the first Hydro body in board order, which
/// was not the front enemy: 21 x 1.5 = 31.
///
/// The damage pipeline is the authority: a Pyro hit of 14 into any Hydro body
/// with no other terms lands 21. The arithmetic is pinned by value; the wiring
/// (the face body visited first, its terms divided back out) structurally,
/// because the tip needs a live combat (README, "The headless boundary").
/// </summary>
public class ReactionPreviewFoldedFaceTests
{
    private const decimal NoCap = decimal.MaxValue;

    private static List<string> Calls(string method) =>
        Il.Calls(Il.Method("KleeCardTooltips", method)).ToList();

    [Fact]
    public void A_face_folded_off_one_hydro_body_lands_its_own_number_on_another()
    {
        var vaporize = ReactionTable.AmplifierMultiplier(Reaction.Vaporize);
        // The pipeline's answer for the hit itself: 14 x 1.5.
        var real = (int)(14m * vaporize);
        Assert.Equal(21, real);
        Assert.Equal(real,
            KleeCardTooltips.LandedOffFoldedFace(real, vaporize, vaporize, NoCap));
        // What the tip used to print.
        Assert.NotEqual(31,
            KleeCardTooltips.LandedOffFoldedFace(real, vaporize, vaporize, NoCap));
    }

    [Fact]
    public void A_bare_face_body_still_takes_this_bodys_amplifier_and_vulnerable()
    {
        var vaporize = ReactionTable.AmplifierMultiplier(Reaction.Vaporize);
        Assert.Equal(21,
            KleeCardTooltips.LandedOffFoldedFace(14, 1m, vaporize, NoCap));
        // This body's Vulnerable too, which the old branch dropped: 14 x 1.5 x 1.5.
        Assert.Equal(31,
            KleeCardTooltips.LandedOffFoldedFace(14, 1m, vaporize * 1.5m, NoCap));
    }

    [Fact]
    public void Dividing_out_a_truncated_face_never_lands_a_point_short()
    {
        // 9 x 1.5 printed 13; back out and in again is still 13.
        Assert.Equal(13,
            KleeCardTooltips.LandedOffFoldedFace(13, 1.5m, 1.5m, NoCap));
        Assert.Equal(3,
            KleeCardTooltips.LandedOffFoldedFace(21, 1.5m, 1.5m, 3m));
    }

    [Fact]
    public void The_tip_visits_the_face_body_first_and_divides_its_terms_out()
    {
        var amplified = Calls("AmplifiedBody");
        Assert.Contains("KleeCardTooltips.LandedOffFoldedFace", amplified);
        Assert.Contains("KleeCardTooltips.BodyTerms", amplified);
        Assert.Contains("KleeCardTooltips.PreviewOrder", Calls("ForCard"));
        Assert.Contains("KleeCardTooltips.FaceBody", Calls("PreviewOrder"));
    }
}
