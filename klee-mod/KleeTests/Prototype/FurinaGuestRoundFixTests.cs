#nullable enable

using System.Linq;
using KleeMod.Cards.Furina.Generated;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- the first guest seat round (0.2.3794), the preview
/// half. Two seats read Soloist's Solicitation and Curtain Rise folding the
/// board two ways on one turn: Soloist 6 beside Curtain Rise 10 / 19 after a
/// Vulnerable, and Soloist 4 beside Curtain Rise 7 / 13 under Shrink.
///
/// THE CAUSE. Soloist is a shipped card on the game's own <c>DamageVar</c>,
/// which in a hand is handed no target and folds the DEALER's side only.
/// Curtain Rise is a <c>proto_</c> row on <see cref="FoldedDamageVar"/>, which
/// substituted the front enemy (`EB-598`) and so folded that body's
/// Vulnerable as well -- under Shrink the two cancelled (7 x 0.7 x 1.5) and
/// the face looked unadjusted.
///
/// THE RULE PINNED. On a Furina Stage board a folded face previews against
/// the body the base game names: none in a hand, the aimed one while dragged.
/// The numbers themselves need a live combat (README, "the headless
/// boundary"), so the body is pinned through the one helper both folding vars
/// call, and the arithmetic through <see cref="HitOrder.Compose"/>, the
/// engine's own phases.
/// </summary>
public class FurinaGuestRoundFixTests
{
    private const decimal Plain = 7m;   // Curtain Rise, "Deal 7"
    private const decimal Branch = 13m; // "Spend 3: deal 13 instead"
    private const decimal Soloist = 6m; // Soloist's Solicitation

    private static decimal Folded(Seat furina, MegaCrit.Sts2.Core.Entities
                                  .Creatures.Creature? body, decimal amount,
                                  MegaCrit.Sts2.Core.Models.CardModel card) =>
        HitOrder.Compose(furina.Creature, body, amount, ValueProp.Move, card);

    [Fact]
    public void Both_folding_vars_ask_the_stage_which_convention_holds()
    {
        foreach (var var in new[]
                 { typeof(FrontFoldedDamageVar), typeof(FoldedDamageVar) })
        {
            var calls = Il.Calls(var.GetMethod("UpdateCardPreview",
                                               HeadlessGame.All)!);
            Assert.Contains("FoldedPreview.Body", calls);
            Assert.Contains("FurinaStage.LiveFor", calls);
        }
        Assert.Contains("HitOrder.BodyForPreview",
                        Il.Calls(typeof(FoldedPreview).GetMethod("Body")!));
    }

    [Fact]
    public void Curtain_rise_folds_the_same_body_as_soloist_on_the_stage()
    {
        var curtain = new ProtoFsCurtainRise();
        var soloist = new SoloistsSolicitation();
        var enemy = Seat.Furina(30).WithPower<VulnerablePower>(1).Creature;

        // In a hand the base game names no body, and neither does the Stage
        // face now; aimed, both take the aimed one.
        Assert.Null(FoldedPreview.Body(true, curtain, CardPreviewMode.Normal,
                                       null, enemy));
        Assert.Same(enemy, FoldedPreview.Body(
            true, curtain, CardPreviewMode.Normal, enemy, enemy));
        // Off the Stage, `EB-598`'s front enemy stands for the other arms.
        Assert.Same(enemy, FoldedPreview.Body(
            false, curtain, CardPreviewMode.Normal, null, enemy));
        Assert.NotNull(soloist);
    }

    [Fact]
    public void Under_weak_both_faces_fold_her_weak_in_hand_and_aimed()
    {
        var furina = Seat.Furina().WithPower<WeakPower>(1);
        var enemy = Seat.Furina(30).Creature;
        var curtain = new ProtoFsCurtainRise();
        var soloist = new SoloistsSolicitation();

        var hand = FoldedPreview.Body(true, curtain, CardPreviewMode.Normal,
                                      null, enemy);
        // Weak is hers, so it folds whether or not a body is named.
        Assert.Equal(Plain * 0.75m, Folded(furina, hand, Plain, curtain));
        Assert.Equal(Branch * 0.75m, Folded(furina, hand, Branch, curtain));
        Assert.Equal(Soloist * 0.75m, Folded(furina, null, Soloist, soloist));
    }

    [Fact]
    public void Under_vulnerable_neither_face_folds_it_in_hand_and_both_do_aimed()
    {
        var furina = Seat.Furina();
        var enemy = Seat.Furina(30).WithPower<VulnerablePower>(1).Creature;
        var curtain = new ProtoFsCurtainRise();
        var soloist = new SoloistsSolicitation();

        // In hand: the seat saw Curtain Rise 10 / 19 beside Soloist 6. Now
        // both print the written number.
        var hand = FoldedPreview.Body(true, curtain, CardPreviewMode.Normal,
                                      null, enemy);
        Assert.Equal(Plain, Folded(furina, hand, Plain, curtain));
        Assert.Equal(Branch, Folded(furina, hand, Branch, curtain));
        Assert.Equal(Soloist, Folded(furina, null, Soloist, soloist));

        // Aimed at the Vulnerable body: both fold it, the base game's way.
        var aimed = FoldedPreview.Body(true, curtain, CardPreviewMode.Normal,
                                       enemy, enemy);
        Assert.Equal(Plain * 1.5m, Folded(furina, aimed, Plain, curtain));
        Assert.Equal(Branch * 1.5m, Folded(furina, aimed, Branch, curtain));
        Assert.Equal(Soloist * 1.5m, Folded(furina, enemy, Soloist, soloist));
    }
}
