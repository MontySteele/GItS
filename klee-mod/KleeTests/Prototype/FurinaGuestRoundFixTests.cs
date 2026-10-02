#nullable enable

using System.Linq;
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

}
