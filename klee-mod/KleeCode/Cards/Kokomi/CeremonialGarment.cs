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
/// state and nothing else -- and everything that makes it a Burst happens
/// afterwards, in <see cref="CeremonialGarmentPower"/>: for
/// <see cref="KokomiConstants.GarmentTurns"/> turns her attacks read the
/// Charge bank (+1 per <see cref="KokomiConstants.GarmentChargeDivisor"/>) and
/// grant Block. That is why the card prints so little next to a 20-point
/// meter: the meter buys the WINDOW, and now buys ONLY the window.
///
/// R74 (Neap Tide v2.1): THE ENTRY SPLASH IS GONE -- 7 to all enemies, hydro,
/// deleted from the sheet. The splash was a second, unrelated payment stapled
/// to the front of a state card, and it let the Burst read as a damage button.
///
/// SHIPPED PARITY DEFECT, FIXED BY THE ADDENDUM A8 AUDIT (2026-07-26), and
/// recorded here because it is the argument for that audit existing. R74
/// edited the SHEET, and every other Kokomi card follows the sheet through
/// codegen -- so the whole batch landed in C# for free. This card does not:
/// it is hand-written (see above), the generator never touches it, and it kept
/// dealing the deleted 7 AoE for the rest of the sprint. tier0 dropped the
/// damage the moment the yaml changed, so E2/E2b measured a Burst that enters
/// a state, while the mod shipped a Burst that enters a state AND nukes the
/// board. Nothing failed: `lint_constant_parity` compares constants, not
/// effect lists, and there is no C# test project.
/// THE GENERAL RULE, since three hand-written cards exist across the roster:
/// a hand-written card is OUTSIDE the sheet-to-C# pipeline, so a sheet ruling
/// that touches one is a two-file edit. Grep the hand-written set on every
/// effects-list ruling.
/// Cost 0 energy plus the full meter as a BaseLib custom-resource cost:
/// SetCanonicalCost wires CanAfford into the playability check, matching the
/// sim's `requires: burst_energy_full`, and
/// <see cref="KokomiBurstResource.DrainOnPlay"/> empties the WHOLE meter on
/// the play hook -- overflow is lost at cast, never at gain.
/// </summary>
public sealed class CeremonialGarment
    : CustomCardModel, ICharacterCard
{
    // NOT IElementalCard any more. The sheet's `applies_element: true` rode on
    // the splash, and R74 deleted the splash -- a Skill with no damage has
    // nothing to apply hydro to. Her CATALYST cadence is unaffected: it is a
    // rule about ATTACKS, and this card is not one.

    public string CharacterId => "kokomi";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("ceremonial_garment");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Ceremonial Garment"),
        ("description",
            "Costs your full [gold]Burst Energy[/gold] meter. "
          + "For {PowerAmount} turns, your Attacks deal 1 more damage per "
          + $"{KokomiConstants.GarmentChargeDivisor} [gold]Charge[/gold] and "
          + $"grant {KokomiConstants.GarmentAttackBlock} Block."),
    };

    /// <summary>Retain: an unplayed Burst stays in hand (sim: the turn-end
    /// filter retains burst-tagged cards). AppliesHydro left with the splash
    /// at R74 -- a keyword promising an application this card cannot make is
    /// the preview-truth defect, not a cosmetic leftover.</summary>
    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Retain };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[]
        {
            new DynamicVar("PowerAmount", KokomiConstants.GarmentTurns),
        };

    // autoAdd: false, and NOT in KokomiCardRoster either -- kit is never
    // draftable. The custom-resource cost is per-instance state, so it is set
    // in the ctor to cover the canonical model and every CreateCard copy.
    // TargetType.Self since R74: the only effect targets the caster. It read
    // AllEnemies for the splash, and a state card that asks you to pick the
    // board is a targeting prompt with no consequence.
    public CeremonialGarment()
        : base(0, CardType.Skill, CardRarity.Rare,
            TargetType.Self, autoAdd: false)
    {
        CustomResources<KokomiBurstResource>.SetCanonicalCost(
            this, KokomiConstants.BurstMax);
    }

    /// <summary>
    /// Sheet order: the STATE lands, then the Tamakushi Casket refresh, on the
    /// same beat as the state it belongs to. There is no third step since R74.
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
