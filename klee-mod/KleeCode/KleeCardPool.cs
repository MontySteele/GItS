using Godot;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;

namespace KleeMod;

/// <summary>
/// Klee's card pool. C1 contains only the four starter stubs; the slice list
/// (31 cards + companions, spec C2) lands via codegen from the YAML sheet.
///
/// C1 STUB: EnergyColorName / CardFrameMaterialPath borrow Ironclad's red
/// assets because we ship no .pck yet (has_pck: false). Custom frame + energy
/// art is an art-pass item, not a boot blocker.
/// </summary>
public sealed class KleeCardPool : CardPoolModel
{
    public override string Title => "klee";

    public override string EnergyColorName => "ironclad";

    public override string CardFrameMaterialPath => "card_frame_red";

    // Klee red, per spec C1.4 (artist's final call later).
    public override Color DeckEntryCardColor => new Color("E85A4F");

    public override Color EnergyOutlineColor => new Color("7A2418");

    public override bool IsColorless => false;

    protected override CardModel[] GenerateAllCards()
    {
        return new CardModel[]
        {
            // Starters (hand-written).
            ModelDb.Card<Kaboom>(),
            ModelDb.Card<DuckAndCover>(),
            ModelDb.Card<Pop>(),

            // Aura-application batch (R23, hand-written): conditional and
            // per-target aura/bomb bonuses are not codegen ops.
            ModelDb.Card<Sizzle>(),
            ModelDb.Card<FlameDance>(),
            ModelDb.Card<KaboomBeetleSwarm>(),
            ModelDb.Card<ElementalEcstasy>(),

            // Generated from docs/klee-cards.yaml by tools/gen_klee_cards.py.
            // Mechanical subset: damage/block/draw/place_bomb/gain_spark.
            // Cards needing powers, burst energy, auras or conditionals are
            // blocked in Generated/manifest.json until those systems land.
            //
            // These carry the pool's rarity coverage: reward and transform
            // generation draws Common/Uncommon/Rare, and a pool with none of
            // those soft locks the reward screen after every combat (finding 17).
            ModelDb.Card<AlchemicalCuriosity>(),
            ModelDb.Card<AllMyTreasures>(),
            ModelDb.Card<AmmoScavenging>(),
            ModelDb.Card<BigBaddaBoom>(),
            ModelDb.Card<BlastRadius>(),
            // Power-card pass: unblocked by the apply_power op.
            ModelDb.Card<BlazingDelight>(),
            ModelDb.Card<BombVoyage>(),
            ModelDb.Card<BombsAway>(),
            ModelDb.Card<CantCatchMe>(),
            ModelDb.Card<CatalyticConversion>(),
            // Burst spike: unblocked by the burst_energy op.
            ModelDb.Card<ClockworkToy>(),
            ModelDb.Card<ClusterCharge>(),
            ModelDb.Card<CombustionStudy>(),
            ModelDb.Card<Crackle>(),
            ModelDb.Card<DaDaDa>(),
            ModelDb.Card<DoublePop>(),
            ModelDb.Card<EndlessFireworks>(),
            ModelDb.Card<ExplosiveFrags>(),
            ModelDb.Card<ExplosivesWorkshop>(),
            ModelDb.Card<FishFlavoredBait>(),
            ModelDb.Card<FlameOnTheWick>(),
            ModelDb.Card<HideAndSeek>(),
            ModelDb.Card<HotHands>(),
            ModelDb.Card<JumpyDumpty>(),
            ModelDb.Card<JumpyDumptyMk2>(),
            ModelDb.Card<MineToss>(),
            ModelDb.Card<NoHoldingBack>(),
            ModelDb.Card<PlaytimeForever>(),
            ModelDb.Card<PocketFireworks>(),
            ModelDb.Card<RapidFire>(),
            ModelDb.Card<RunAway>(),
            ModelDb.Card<SkipAndHop>(),
            ModelDb.Card<Snap>(),
            ModelDb.Card<SorryJean>(),
            ModelDb.Card<SparkCollection>(),
            ModelDb.Card<SparkKnightStyle>(),
            ModelDb.Card<SparklyTreasure>(),
            ModelDb.Card<SpiritedAway>(),
            ModelDb.Card<TrueSparkKnight>(),
            ModelDb.Card<VermillionPact>(),
            ModelDb.Card<WarmGlow>(),
        };
    }
}
