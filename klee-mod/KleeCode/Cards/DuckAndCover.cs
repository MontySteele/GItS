using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards;

/// <summary>
/// Klee's basic block. Sheet: cost 1, block 5.
/// Mechanically identical to DefendSilent — the intended reskin.
/// </summary>
public sealed class DuckAndCover : CustomCardModel
{
    // Deliberately NOT overriding GainsBlock: CustomCardModel already overrides
    // it to auto-detect a BlockVar in DynamicVars, which we have.

    /// <summary>Loose-PNG art, no .pck. File is images/cards/duck_and_cover.png.</summary>
    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("duck_and_cover");

    /// <summary>See Kaboom.Localization for why this lives on the model.</summary>
    public override List<(string, string)>? Localization => new()
    {
        ("title", "Duck and Cover"),
        ("description", "Gain {Block:diff()} [gold]Block[/gold]."),
    };

    protected override HashSet<CardTag> CanonicalTags => new() { CardTag.Defend };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new BlockVar(5m, ValueProp.Move) };

    // autoAdd: false -- see Kaboom for why. KleeCardPool owns membership.
    public DuckAndCover()
        : base(1, CardType.Skill, CardRarity.Basic, TargetType.Self, autoAdd: false)
    {
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block, cardPlay);
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Block.UpgradeValueBy(3m);
    }
}
