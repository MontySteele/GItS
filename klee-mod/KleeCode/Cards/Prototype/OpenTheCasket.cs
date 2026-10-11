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
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Cards.Prototype;

/// <summary>
/// OPEN THE CASKET -- the Tamakushi Casket's token (the Casket pass,
/// 2026-09-28). [USER]: the relic "adds one 0-cost Retain / Exhaust card that
/// converts that energy into Strength"; "1 strength per point seems fine; we
/// can adjust down if we need to."
///
/// "Gain Strength equal to the Casket's count, then empty it." The count is
/// <see cref="KokomiOverhaulLedger.CasketCount"/>; emptying it does not stop
/// the relic -- "the casket keeps counting" from 0.
///
/// IT PAYS MORE THAN ONCE (2026-10-01, the four-kit review, Kokomi pick 1).
/// [USER]: "On your new picks agree all around - I think that if it's
/// repeatable, it should probably cost energy, though, to make this a real
/// choice and not just button mashing when it comes up?" So it costs 1 Energy
/// and has no Exhaust: played, it goes to the discard pile and comes back
/// with the deck, and the count it finds is whatever the Casket gathered
/// since the last opening. It keeps Retain.
///
/// A TOKEN, HAND-WRITTEN, IN NO POOL. The relic deals it into her opening hand
/// (<see cref="Relics.TamakushiCasket.BeforeHandDraw"/>) and What the Tokoyo
/// Returns fetches it from the draw pile or the discard pile; nothing offers
/// it. It is not a sheet row because the prototype surface has no token
/// rarity and a `proto_kk_` row that is not in the pool is a finding for
/// <c>tools/lint_arm_pool_parity.py</c> -- Furina's Ethereal Spotlight is the
/// same shape (a relic-dealt token, hand-written, off-pool). It is in
/// <c>KokomiOffPoolCards</c> so <c>CardModel.Pool</c> resolves. Sim twin:
/// <c>kokomi_plan.open_the_casket_card</c> and <c>kokomi_plan.open_casket</c>.
///
/// THE UPGRADE DRAWS 1 (the Kokomi kit review, 2026-10-05): it changed
/// nothing before. Upgraded it also draws 1 card, after the Strength; cost
/// and Retain stay. Sim twin: <c>kokomi_plan.open_the_casket_card(upgraded)</c>.
///
/// IT STARTS AT 0 AND RAMPS (2026-10-10, after [USER]'s Kokomi playtest).
/// [USER]: "I think that the casket should start at 0 and then have a ramping
/// cost (goes up by 1 each time) That means the casket is free the first
/// play, costs 1 the second, and then at 2+ becomes difficult. That way it
/// has obvious use in a short hallway fight". Printed cost 0; every play ends
/// with <c>EnergyCost.AddThisCombat(1)</c>, the base game's Modded (a 0-cost
/// Rare whose face ends "Increase this card's cost by 1."), whose words the
/// face borrows. The ramp lives on the CARD INSTANCE, as Modded's does: the
/// relic deals a fresh copy each combat (so it resets), and What the Tokoyo
/// Returns and Grand Design MOVE that copy to the hand, so a fetched Open
/// keeps its ramped cost. The face's cost is the engine's own resolved cost,
/// so it is always the true price. Sim twin: the
/// <c>cost_mod self_this_combat</c> op on
/// <c>kokomi_plan.open_the_casket_card</c>.
/// </summary>
public sealed class OpenTheCasket : CustomCardModel, ICharacterCard
{
    public string CharacterId => "kokomi";

    /// <summary>The art key. No painting yet: the Casket pass's one art debt.</summary>
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("kk_open_the_casket");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Open the Casket"),
        ("description",
            "Gain [gold]Strength[/gold] equal to the [gold]Casket[/gold]'s "
          + "count, then empty it.{IfUpgraded:show: Draw 1 card.|} "
          + "Increase this card's cost by 1."
          + "{InCombat:{CasketStrength}|}"),
    };

    /// <summary>
    /// THE COUNT ON THE FACE (Kokomi whole-run round 2, 2026-10-10): in
    /// combat the card prints the Strength it would grant, the way Driftglass
    /// prints its damage -- "(Gains N Strength)". Under Grand Design the
    /// number is still the whole count (<see cref="KokomiOverhaulKit.OpenCasket"/>).
    /// </summary>
    protected override void AddExtraArgsToDescription(
        MegaCrit.Sts2.Core.Localization.LocString description)
    {
        base.AddExtraArgsToDescription(description);
        description.Add("CasketStrength", StrengthLine(this));
    }

    /// <summary>The in-combat line, or empty out of combat.</summary>
    public static string StrengthLine(CardModel card) =>
        TipOwner.CreatureOf(card) is { } owner
        && owner.CombatState != null && KokomiOverhaul.LiveFor(owner)
            ? Line(KokomiOverhaulLedger.For(owner).CasketCount
                   * KokomiOverhaulLaw.CasketStrengthPerPoint)
            : "";

    /// <summary>The line's words, for the pins.</summary>
    public static string Line(int strength) =>
        $"\n(Gains {strength} [gold]Strength[/gold])";

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Retain };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForCasket(base.ExtraHoverTips, this);

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new CardsVar(1) };

    public OpenTheCasket()
        : base(0, CardType.Skill, CardRarity.Token, TargetType.Self,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await KokomiOverhaulKit.OpenCasket(choiceContext, Owner.Creature, this);
        if (IsUpgraded)
        {
            await CardPileCmd.Draw(choiceContext, DynamicVars.Cards.BaseValue, Owner);
        }
        // "Increase this card's cost by 1." Modded's line, last, as Modded's.
        EnergyCost.AddThisCombat(1);
    }

    protected override void OnUpgrade()
    {
        // The draw is an IsUpgraded read in OnPlay; nothing to bump here.
    }
}
