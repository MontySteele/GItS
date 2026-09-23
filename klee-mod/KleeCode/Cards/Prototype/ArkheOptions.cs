using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;

namespace KleeMod.Cards.Prototype;

// ======================================================================
// ARKHE ALIGNMENT'S TWO FACES (R276 batch two), for the choose-a-card screen
// the power opens at the start of her turn.
//
// THE ETHEREAL SPOTLIGHT'S SHAPE: a card only because the screen takes cards,
// never played, never in a pile, never offered -- but a POOL MEMBER
// (`FurinaOffPoolCards`), because a card in no pool throws inside the screen
// (`EB-150`). QUARANTINED with the power that opens them.
// ======================================================================

/// <summary>Ousia: this turn your performers' acts deal double damage.
/// </summary>
public sealed class ArkheOusiaOption : CustomCardModel
{
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("proto_fs_arkhe_alignment");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Ousia"),
        ("description",
            "This turn, your performers' acts deal double damage."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        System.Array.Empty<DynamicVar>();

    public ArkheOusiaOption()
        : base(0, CardType.Skill, CardRarity.Token, TargetType.Self, autoAdd: false)
    {
    }

    protected override Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay) =>
        Task.CompletedTask;

    protected override void OnUpgrade()
    {
    }
}

/// <summary>Pneuma: this turn your performers' acts give double Block, and
/// the lead performer regains 2 Fanfare.</summary>
public sealed class ArkhePneumaOption : CustomCardModel
{
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("proto_fs_arkhe_alignment");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Pneuma"),
        ("description",
            "This turn, your performers' acts give double [gold]Block[/gold], "
          + "and the lead performer regains "
          + ArkheAlignmentPower.PneumaLeadRegain + " [gold]Fanfare[/gold]."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        System.Array.Empty<DynamicVar>();

    public ArkhePneumaOption()
        : base(0, CardType.Skill, CardRarity.Token, TargetType.Self, autoAdd: false)
    {
    }

    protected override Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay) =>
        Task.CompletedTask;

    protected override void OnUpgrade()
    {
    }
}
