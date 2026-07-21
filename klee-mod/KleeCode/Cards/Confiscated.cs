using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// Fish Blasting's downside token (tier0 tokens.yaml): a Status that costs 1
/// and does nothing -- the tax is the energy and the draw it wastes, and
/// Dodge Roll can exhaust it. Deliberately NOT in KleeCardPool, so it is never
/// rolled as a reward; generated add_card bodies create instances via
/// CombatState.CreateCard. It IS in KleeExtraCardPool -- a card that belongs
/// to no pool at all throws "You monster!" out of CardModel.Pool the moment it
/// is drawn (see that file).
/// </summary>
public sealed class Confiscated : CustomCardModel
{
    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("confiscated");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Confiscated"),
        ("description", "Does nothing."),
    };

    public Confiscated()
        : base(1, CardType.Skill, CardRarity.Status, TargetType.Self, autoAdd: false)
    {
    }

    protected override Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
        => Task.CompletedTask;
}
