using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Kokomi;

/// <summary>
/// Kokomi's Ancient-rarity card.
///
/// WHY IT EXISTS AT ALL is a crash, not a design want. The act-2 Darv event
/// rolls Dusty Tome ~50% of the time, and DustyTome.SetupForPlayer draws a
/// random CardRarity.Ancient card from the character's pool. A character with
/// no Ancient card gets an empty draw, NextItem(...).Id NREs inside
/// Darv.GenerateInitialOptions, and the run softlocks on room entry. That was
/// a live playtest defect on 2026-07-23; the invariant (>= 1 visible Ancient
/// per roster character) and its lint came out of it.
///
/// Membership in RosterAncientCards.Kokomi does NOT make it rollable --
/// reward, transform and shop generation all filter Ancient upstream, so
/// Dusty Tome is the single door. The Tome upgrades what it grants, so read
/// the card at its upgraded numbers.
///
/// The card reads "Whenever the Bake-Kurage carries out a Plan, gain 2 Block
/// and draw 1 card." (upgrade: 3 Block) and applies
/// <c>PrincessOfWatatsumiPlanPower</c> (R276 hygiene). Its shipped face, a
/// per-turn Charge drip, went with the shipped kits (legacy cleanup stage 5);
/// <c>PowerAmount</c> stays declared because both engines' witness
/// (<c>tools/lint_handwritten_parity.ANCIENT_WITNESS</c>) reads one var list.
/// Sim twin: the <c>princess_of_watatsumi</c> row in
/// <c>tier0/content/cards/ancients.yaml</c>.
///
/// NAME: "Princess of Watatsumi" is her canon innate passive.
/// </summary>
public sealed class PrincessOfWatatsumi : CustomCardModel, ICharacterCard
{
    public string CharacterId => "kokomi";

    // Art: reuses her rare Charge accelerant's portrait until the art pass
    // gives the Ancient its own crop. A look-pass item, not a blocker.
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("prayer_to_the_moon");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Princess of Watatsumi"),
        ("description",
            "Whenever the [gold]Bake-Kurage[/gold] carries out a "
          + "[gold]Plan[/gold], gain {PlanBlock:diff()} [gold]Block[/gold] "
          + "and draw 1 card."),
    };

    // The face prints Plan, and carries that word's definition.
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForPlan(base.ExtraHoverTips, this);

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar("PowerAmount", 3m),
            new DynamicVar("PlanBlock", 2m)
        };

    // autoAdd: false -- RosterAncientCards.Kokomi owns membership, concatted
    // into KokomiCardPool.GenerateAllCards.
    public PrincessOfWatatsumi()
        : base(1, CardType.Power, CardRarity.Ancient, TargetType.Self,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!KokomiOverhaul.LiveFor(Owner.Creature)) return;
        await PowerCmd.Apply<PrincessOfWatatsumiPlanPower>(
            choiceContext, Owner.Creature,
            DynamicVars["PlanBlock"].IntValue,
            applier: Owner.Creature, cardSource: this);
    }

    protected override void OnUpgrade()
    {
        DynamicVars["PowerAmount"].UpgradeValueBy(1m);
        DynamicVars["PlanBlock"].UpgradeValueBy(1m);
    }
}
