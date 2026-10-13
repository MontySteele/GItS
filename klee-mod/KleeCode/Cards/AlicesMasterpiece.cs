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

namespace KleeMod.Cards;

/// <summary>
/// Klee's second Ancient-rarity card (pool completion, 2026-10-01;
/// review/active/pool-completion-2026-10-01.md sec.3, ruled at the default):
/// "When one of your Bombs or Mines goes off, it stays on the enemy at half its size,
/// rounded down." Bends the Klee arm's rule 2, under which a set-off Bomb is
/// gone; the rule and its readings are <see cref="AlicesMasterpiecePower"/>'s.
///
/// Game-side only. Her Dusty Tome card: the Tome skips her Archaic Tooth card,
/// Mk.Omega (the Ancient audit, 2026-10-12), so it draws this one and grants
/// it UPGRADED (read it at 2 Energy). Membership is <c>RosterAncientCards.Klee</c>;
/// reward, transform and shop generation filter Ancient upstream. Compiled
/// with the prototype surface only, because the rule it bends is the arm's.
/// Numbers witnessed by <c>tools/lint_handwritten_parity.ANCIENT_WITNESS</c>.
/// Art: the placeholder until the art pass.
/// </summary>
public sealed class AlicesMasterpiece : CustomCardModel, ICharacterCard
{
    public string CharacterId => "klee";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("alices_masterpiece");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Alice's Masterpiece"),
        ("description",
            "When one of your [gold]Bombs[/gold] or [gold]Mines[/gold] goes off, it "
          + "stays on the enemy at half its size, rounded down."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForMine(ArmKeywordTips.ForBomb(base.ExtraHoverTips, this), this);

    // autoAdd: false -- RosterAncientCards.Klee owns membership.
    public AlicesMasterpiece()
        : base(3, CardType.Power, CardRarity.Ancient, TargetType.Self,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<AlicesMasterpiecePower>(
            choiceContext, Owner.Creature, 1, applier: Owner.Creature,
            cardSource: this);
    }

    protected override void OnUpgrade()
    {
        EnergyCost.UpgradeBy(-1);
    }
}
