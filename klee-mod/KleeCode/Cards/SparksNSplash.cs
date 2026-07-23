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

namespace KleeMod.Cards;

/// <summary>
/// Sparks 'n' Splash -- the kit Burst card (sheet: rare power, cost 0,
/// kit_card, requires burst_energy_full; v1.9: the Burst is kit, not loot).
///
/// Hand-written: its lifecycle is machinery, not ops. NEVER in
/// KleeCardPool.GenerateAllCards -- the card is granted to hand by
/// <see cref="KitGrant"/> when the Burst meter fills and is otherwise
/// unobtainable (not draftable, not transformable; the sim's loader excludes
/// kit cards from every pool).
///
/// Cost model: 0 energy (normal EnergyCost) PLUS a BaseLib custom-resource
/// cost of the full meter -- SetCanonicalCost(40) wires CanAfford (>= 40)
/// into the game's playability check, matching the sim's
/// requires: burst_energy_full gate, and the play pipeline calls
/// KleeBurstResource.Spend, whose override drains the WHOLE meter (sim law:
/// overflow is lost at cast, never at gain).
///
/// Retain (CanonicalKeywords): the sim's turn-end filter keeps burst-tagged
/// cards in hand; the game's flush honors the Retain keyword the same way.
/// A played Power leaves combat entirely, which is the game-side reading of
/// "returns to the kit, no pile" -- the next full meter grants a fresh copy.
/// </summary>
public sealed class SparksNSplash : CustomCardModel
{
    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("sparks_n_splash");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Sparks 'n' Splash"),
        ("description",
            "Costs your full [gold]Burst Energy[/gold] meter. "
          + "For {PowerAmount} turns: at the end of your turn, deal 5 damage "
          + "to a random enemy 4 times, applying [gold]Pyro[/gold]."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar("PowerAmount", 3m)
        };

    /// <summary>Retain: an unplayed Burst stays in hand (sim: the turn-end
    /// filter retains burst-tagged cards).</summary>
    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Retain };

    // autoAdd: false -- and deliberately NOT in KleeCardPool either (kit is
    // never draftable). The custom-resource cost is per-instance state;
    // setting it in the ctor covers the canonical and every CreateCard copy.
    public SparksNSplash()
        : base(0, CardType.Power, CardRarity.Rare, TargetType.Self, autoAdd: false)
    {
        CustomResources<KleeBurstResource>.SetCanonicalCost(this, BurstConstants.KleeMax);
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<SparksNSplashPower>(
            choiceContext, Owner.Creature, DynamicVars["PowerAmount"].IntValue,
            applier: Owner.Creature, cardSource: this);
    }

    protected override void OnUpgrade()
    {
        // klee-upgrades.yaml: NO UPGRADE (kit card, v1.9; Talent Training =
        // v2 design space). Unreachable in practice -- the kit card is never
        // in the deck, so the smith never offers it.
    }
}
