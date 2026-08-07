using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Kokomi;

/// <summary>
/// Kokomi's Ancient-rarity card: a Charge engine.
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
/// SHAPE. Furina's Ancient drips Encore because Encore is her whole economy
/// at once. Kokomi's equivalent is Charge, and the parallel is deliberate
/// down to one asymmetry: 3 is small next to Furina's 5 because Encore is
/// SPENT and Charge is not. Her bank only grows, and the Kurage pulse reads
/// it at KuragePulsePerCharge -- a drip here compounds against a multiplier
/// instead of adding to a total, so the honest scaling comparison is not
/// 3-vs-5 but 3-times-4-per-turn against 5-once.
///
/// It is also the only Charge in the game that does not cost her a card,
/// which is the point of an Ancient: the one door out of her central bargain.
///
/// Hand-written and outside the ratified sheets, like every Ancient: these
/// are game-side-only content. (tier05 now models events and relics; the
/// no-passive-accrual law that barred this card's per-turn Charge shape
/// gained its Ancient carve-out -- R127, 2026-08-07 -- and the sim twin is
/// filed as EB-30m.) PROPOSED, and flagged as
/// such in R58 -- this one wants red-pen more than most, because no
/// instrument can tell us it is wrong until EB-30m lands.
///
/// NAME: "Princess of Watatsumi" is her canon innate passive (wiki-verified
/// in the sheet header) and was unused by the pool. Still subject to the
/// [USER]-only naming audit like the rest of the v0.5 block.
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
            "At the start of your turn, gain {PowerAmount:diff()} "
          + "[gold]Charge[/gold]."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar("PowerAmount", 3m)
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
        await PowerCmd.Apply<ChargePerTurnPower>(
            choiceContext, Owner.Creature, DynamicVars["PowerAmount"].IntValue,
            applier: Owner.Creature, cardSource: this);
    }

    protected override void OnUpgrade()
    {
        DynamicVars["PowerAmount"].UpgradeValueBy(1m);
    }
}
