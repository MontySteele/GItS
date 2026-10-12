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
/// Dodge Roll can exhaust it. <c>CardType.Status</c> since the Klee
/// finish-line batch (2026-10-03; [USER]: "Confiscated should be a Status,
/// not a Skill?"): it was a Skill at Status rarity. Still playable, the base
/// game's <c>Slimed</c> shape (a Status with no Unplayable keyword plays at
/// its cost); it no longer counts as a Skill for any Skill reader. Deliberately NOT in KleeCardPool, so it is never
/// rolled as a reward; generated add_card bodies create instances via
/// CombatState.CreateCard. It IS in KleeExtraCardPool -- a card that belongs
/// to no pool at all throws "You monster!" out of CardModel.Pool the moment it
/// is drawn (see that file). Exhaust since 2026-10-11 ([USER]: "Actually,
/// should we tag Confiscated with Exhaust? Currently we're using it as a
/// drawback mechanism to load the deck but it builds over time."), the
/// keyword Slimed carries; the face still reads "Does nothing." and the game
/// appends "Exhaust." from the keyword.
/// </summary>
public sealed class Confiscated : CustomCardModel
{
    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("confiscated");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Confiscated"),
        ("description", "Does nothing."),
    };

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Exhaust };

    public Confiscated()
        : base(1, CardType.Status, CardRarity.Status, TargetType.Self, autoAdd: false)
    {
    }

    protected override Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
        => Task.CompletedTask;
}
