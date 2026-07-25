using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards.Kokomi;

/// <summary>
/// Ceremonial Garment -- Kokomi's kit Burst (sheet: rare skill, cost 0,
/// kit_card, requires burst_energy_full; v1.9: the Burst is kit, not loot).
///
/// Hand-written, like Klee's and Furina's, because its lifecycle is machinery
/// rather than ops: it is granted to hand by
/// <see cref="KokomiKitGrant"/> at a full meter, Retained until cast, and is
/// in no rollable pool (KokomiOffPoolCards keeps it Pool-legal but filtered
/// out of reward generation).
///
/// SHAPE B, the kickoff §2.2 recommendation. The card itself is small -- a
/// splash and a state -- and everything that makes it a Burst happens
/// afterwards, in <see cref="CeremonialGarmentPower"/>: for
/// <see cref="KokomiConstants.GarmentTurns"/> turns her attacks read the
/// Charge bank (+1 per <see cref="KokomiConstants.GarmentChargeDivisor"/>) and
/// grant Block. That is why the printed 7 looks modest next to a 20-point
/// meter: the meter buys the WINDOW, not the splash.
///
/// A SKILL that deals damage, deliberately. The card type is what keeps the
/// entry splash out of its own Charge read -- the rider gates on
/// CardType.Attack on both sides of the bridge (tier0 flat_attack_bonus's
/// `if card.type == "attack"`), so a Burst printed as an Attack would silently
/// pay itself the bank on cast and every measured number would be wrong.
///
/// Cost 0 energy plus the full meter as a BaseLib custom-resource cost:
/// SetCanonicalCost wires CanAfford into the playability check, matching the
/// sim's `requires: burst_energy_full`, and
/// <see cref="KokomiBurstResource.DrainOnPlay"/> empties the WHOLE meter on
/// the play hook -- overflow is lost at cast, never at gain.
/// </summary>
public sealed class CeremonialGarment
    : CustomCardModel, IElementalCard, ICharacterCard
{
    /// <summary>tier0 sheet: `applies_element: true` on the splash.</summary>
    public Element Element => Element.Hydro;

    public string CharacterId => "kokomi";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("ceremonial_garment");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Ceremonial Garment"),
        ("description",
            "Costs your full [gold]Burst Energy[/gold] meter. "
          + "Deal {Damage} damage to ALL enemies. For {PowerAmount} turns, "
          + "your Attacks deal 1 more damage per "
          + $"{KokomiConstants.GarmentChargeDivisor} [gold]Charge[/gold] and "
          + $"grant {KokomiConstants.GarmentAttackBlock} Block."),
    };

    /// <summary>Retain: an unplayed Burst stays in hand (sim: the turn-end
    /// filter retains burst-tagged cards).</summary>
    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Retain, KleeKeywords.AppliesHydro };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[]
        {
            new DamageVar(7m, ValueProp.Move),
            new DynamicVar("PowerAmount", KokomiConstants.GarmentTurns),
        };

    // autoAdd: false, and NOT in KokomiCardRoster either -- kit is never
    // draftable. The custom-resource cost is per-instance state, so it is set
    // in the ctor to cover the canonical model and every CreateCard copy.
    public CeremonialGarment()
        : base(0, CardType.Skill, CardRarity.Rare,
            TargetType.AllEnemies, autoAdd: false)
    {
        CustomResources<KokomiBurstResource>.SetCanonicalCost(
            this, KokomiConstants.BurstMax);
    }

    /// <summary>
    /// Sheet order, and it matters: the STATE lands before the splash. The
    /// splash is a Skill's damage so it takes no Charge read either way, but
    /// applying first is what makes the Tamakushi Casket refresh below happen
    /// on the same beat as the state it belongs to.
    /// </summary>
    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<CeremonialGarmentPower>(
            choiceContext, Owner.Creature,
            DynamicVars["PowerAmount"].IntValue,
            applier: Owner.Creature, cardSource: this);

        // Tamakushi Casket (v0.4 §1.3, her canon A1): casting the Garment
        // while the Kurage is fielded REFRESHES the jellyfish's duration --
        // the E-into-Q loop, verbatim. Guarded on the summon already being
        // out: the Burst does not conjure one from nothing.
        //
        // NEAR-DEAD BY CONSTRUCTION, and shipped anyway. At KurageDuration 1
        // a fielded jellyfish is always at exactly 1, so refresh-to-full only
        // does anything if the Burst goes off the same turn the Kurage was
        // played. The sim carries the identical dead link ([USER] confirmed
        // shipping the parity rather than holding the build), so removing it
        // here would be the first divergence rather than a cleanup.
        if (Owner.Creature.Powers.Any(p => p is KurageSummonPower))
        {
            await KurageSummon.Field(
                choiceContext, Owner.Creature,
                KokomiConstants.KurageDuration, this);
        }

        await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
            .FromCard(this)
            .TargetingAllOpponents(CombatState!)
            .WithHitFx("vfx/vfx_attack_slash")
            .SpawningHitVfxOnEachCreature()
            .Execute(choiceContext);
    }

    /// <summary>
    /// "Returns to the kit, no pile" (tier0 combat.py play_card's kit_card
    /// branch, which is unconditional on card TYPE). This card is a Skill, so
    /// its default result pile is Discard -- exactly the divergence that made
    /// Furina's Attack-shaped Burst recirculate into the draw pile and
    /// permanently add a Burst to the deck on every cast. Klee's never showed
    /// it because a played Power already leaves combat.
    /// </summary>
    protected override PileType GetResultPileTypeForCardPlay() => PileType.None;

    protected override void OnUpgrade()
    {
        // kokomi-upgrades.yaml: NO UPGRADE (kit card, v1.9; the sparks_n_splash
        // precedent -- Talent Training is v2 design space). Unreachable in
        // practice: the kit card is never in the deck, so the smith never
        // offers it.
    }
}
