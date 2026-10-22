using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI WORDING PASS (2026-10-14; [USER]: "Yep, please proceed"). No
/// number moves: Pincer's Plan line names the turn it is carried out, Battle
/// Formation says once a turn, Juuga's Plan line says its three turns, and
/// Crystal Collapse is unplayable until a Companion has been played this
/// combat and names the Companion it caught on the strip. Sim twin:
/// <c>tier0/tests/test_kokomi_wording_pass_2026_10_14.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiWordingPassTests
{
    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static string PowerFace(PowerModel power) =>
        ((ILocalizationProvider)power).Localization!
            .First(r => r.Item1 == "description").Item2;

    // ---- 1. PINCER --------------------------------------------------------

    [Fact]
    public void Pincer_names_the_turn_it_is_carried_out()
    {
        var face = Face(new ProtoKkPincer());
        Assert.Contains("Your first Attack that turn is played twice.", face);
        Assert.DoesNotContain("Next turn", face);
        // The switch the carry-out applies says "this turn": it is spent on
        // the morning the Plan lands, never a turn later.
        Assert.Equal("This turn, your first Attack is played twice.",
                     PowerFace(new FirstAttackTwicePower()));
    }

    // ---- 2. BATTLE FORMATION ---------------------------------------------

    [Fact]
    public void Battle_formation_says_when_on_card_and_power()
    {
        // The Kokomi finish pass (2026-10-19): the base start-of-turn
        // template replaced "The first time each turn".
        Assert.StartsWith(
            "At the start of your turn, if 2 or more of your "
          + "[gold]Plans[/gold] were carried out, gain ",
            Face(new ProtoKkBattleFormation()));
        Assert.StartsWith(
            "At the start of your turn, if 2 or more of your "
          + "[gold]Plans[/gold] were carried out, gain ",
            PowerFace(new BattleFormationPower()));
    }

    // ---- 3. JUUGA ----------------------------------------------------------

    [Fact]
    public void Juuga_plan_line_says_its_three_turns()
    {
        var face = Face(new ProtoMiGorouJuuga());
        Assert.EndsWith(
            "[gold]plan[/gold]: Gain 6 [gold]Block[/gold] instead.", face);
        // Wording pass 2026-10-15: the 3 turns lead the face and cover both lines.
        Assert.StartsWith("For {PowerAmount:diff()} turns,", face);
        var clause = Assert.Single(new ProtoMiGorouJuuga().PlanClauses);
        Assert.Equal((KokomiPlan.Kind.JuugaGuard, 3),
                     (clause.Kind, clause.Amount));
        Assert.Equal(6, CompanionOverhaulLaw.JuugaGuardBlock);
    }

    // ---- 4. CRYSTAL COLLAPSE ----------------------------------------------

    // The wording pass's gate (unplayable until a Companion was played) is
    // gone: since the Kokomi upgrade pass (2026-10-19) the face plays a
    // random Common one with none, and the gate refused it anyway (Kokomi
    // Balance suite 4, 2026-10-21, lanes 1, 1b and 5).

    [Fact]
    public void Crystal_collapse_remembers_the_last_other_companion()
    {
        var ledger = new KokomiOverhaulLedger();
        ledger.RollTo(1);
        Assert.Null(ledger.LastCompanionPlayed);
        // Crystal Collapse never counts as its own last Companion.
        ledger.NoteCompanionCard(new ProtoMiGorouCrystalCollapse());
        Assert.Null(ledger.LastCompanionPlayed);
        ledger.NoteCompanionCard(new ProtoMiGorouJuuga());
        Assert.IsType<ProtoMiGorouJuuga>(ledger.LastCompanionPlayed);
        ledger.RollTo(2);
        Assert.IsType<ProtoMiGorouJuuga>(ledger.LastCompanionPlayed);
    }

    [Fact]
    public void Crystal_collapse_is_playable_with_no_companion_played()
    {
        var card = new ProtoMiGorouCrystalCollapse();
        Assert.False(card is IUnplayableReasonCard);
        Assert.Null(typeof(ProtoMiGorouCrystalCollapse).GetProperty(
            "IsPlayable", HeadlessGame.All | System.Reflection.BindingFlags.DeclaredOnly));
        // The fallback its face prints is the carry-out's own.
        Assert.Equal("Random Companion", KokomiPlan.CopiesCaption(null));
    }

    [Fact]
    public void The_strip_caption_names_the_caught_companion()
    {
        Assert.Equal("Copies Juuga", KokomiPlan.CopiesCaption(
            "Gorou — Juuga: Forward Unto Victory"));
        Assert.Equal("Copies Crystal Collapse",
                     KokomiPlan.CopiesCaption("Gorou — Crystal Collapse"));
        Assert.Equal("Copies Strike", KokomiPlan.CopiesCaption("Strike"));
        // The Kokomi upgrade pass (2026-10-19): nothing caught plays a
        // random Common Companion.
        Assert.Equal("Random Companion", KokomiPlan.CopiesCaption(null));
        Assert.Equal("Random Companion", KokomiPlan.CopiesCaption(""));
        // The caption is the strip's live line and the seat page's `live`.
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "LiveLine")),
                        c => c.Contains("CopiesCaption"));
    }

    [Fact]
    public void The_hover_previews_the_companion_it_copies()
    {
        // No combat, nothing to preview: the hover is the card's own tips.
        var card = new ProtoMiGorouCrystalCollapse();
        Assert.Null(KokomiRefounding.CompanionToCopy(card));
        var tips = KokomiCards.WithCopiedCompanionPreview(
            System.Array.Empty<MegaCrit.Sts2.Core.HoverTips.IHoverTip>(),
            card).ToList();
        Assert.Empty(tips);
        Assert.Contains(Il.Calls(Il.Method("KokomiRefounding",
                                           "CompanionToCopy")),
                        c => c.Contains("KokomiPlan.Showing"));
    }
}
