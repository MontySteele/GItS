using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Yae;

/// <summary>
/// Yae's Dusty Tome Ancient (the Yae pass, 2026-10-16,
/// <c>review/active/yae-ancients-relics-2026-10-16.md</c> sec.2): a Power, 2
/// Energy, 1 upgraded (Divine Strategy's cost). "Your Edits write their
/// Annotation twice." It bends the Edit rule, the half of her kit no Rare
/// bends yet. Layers already add up, so Red Ink gives 6 and Fox Fire 8,
/// Footnote draws 2, Royalties gives 2 Energy, and Reprint plays the card
/// three times (still once a combat). Deadline Extension twice is the same as
/// once. The rule is <see cref="YaePublishingHousePower"/>'s, read by
/// <see cref="YaeEditing.WriteTimes"/>.
///
/// Game-side only. The Tome skips her Archaic Tooth card, so it draws this
/// one and grants it UPGRADED (read it at 1 Energy). Membership is
/// <c>RosterAncientCards.Yae</c>. Numbers witnessed by
/// <c>tools/lint_handwritten_parity.ANCIENT_WITNESS</c>.
/// </summary>
public sealed class YaePublishingHouse : CustomCardModel, ICharacterCard
{
    public string CharacterId => YaePrototype.CharacterId;

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("yae_publishing_house");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Yae Publishing House"),
        ("description",
            "Your [gold]Edits[/gold] write their Annotation twice."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForEdit(base.ExtraHoverTips, this);

    // autoAdd: false -- RosterAncientCards.Yae owns membership.
    public YaePublishingHouse()
        : base(2, CardType.Power, CardRarity.Ancient, TargetType.Self,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<YaePublishingHousePower>(
            choiceContext, Owner.Creature, 1, applier: Owner.Creature,
            cardSource: this);
    }

    protected override void OnUpgrade()
    {
        EnergyCost.UpgradeBy(-1);
    }
}
